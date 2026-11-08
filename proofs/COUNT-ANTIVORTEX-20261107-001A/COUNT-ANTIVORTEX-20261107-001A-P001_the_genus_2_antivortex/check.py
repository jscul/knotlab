#!/usr/bin/env python3
"""Checks for COUNT-ANTIVORTEX-20261107-001A: the genus-2 antivortex.

    python3 -B check.py          verify result.json against a fresh run
    python3 -B check.py --write  write result.json from a fresh run
Run with the repository's .venv. Single process; a few minutes."""
import hashlib
import json
import random
import sys
import time
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
import antivortex_lib as A  # noqa: E402
L, F, SP = A.L, A.F, A.SP

T0 = time.time()
OUT = {}


def check(name, ok, info):
    OUT[name] = {"pass": bool(ok), "info": info}
    print("PASS" if ok else "FAIL", name, json.dumps(info, default=str)[:600], round(time.time() - T0, 1), "s", flush=True)
    if not ok:
        sys.exit(1)


def params(m):
    a = -(-(2 * m + 22) // 3)
    c = 5 + 2 * m + 7
    return a, 3, (c, c), m, 5, 5


def coarse_triangle_of_face(red, v):
    R = red["R"]
    P = red["K"]["fpts"][v]
    if not all(p in R for p in P):
        return None
    vs = set()
    for p in P:
        vs.update(SP.coarse_of(R[p]))
    return tuple(sorted(vs))


def colouring(m, rng, seed_kind):
    """a random interior colouring; seed_kind adds a few fully labelled triangles of one orientation"""
    iv = SP.interior_vertices(m)
    c = {v: rng.randrange(3) for v in iv}
    if seed_kind:
        for _ in range(2):
            a, b = rng.choice(iv)
            tri = [(a, b), (a + 1, b), (a, b + 1)]
            if all(v in c for v in tri):
                for v, col in zip(tri, (0, 1, 2) if seed_kind > 0 else (0, 2, 1)):
                    c[v] = col
    return c


if __name__ == "__main__":
    manifest = json.loads((HERE / "manifest.json").read_text())
    bad = {q: dg for q, dg in manifest["parent_bindings"].items() if hashlib.sha256((ROOT / q).read_bytes()).hexdigest() != dg}
    status = {q: json.loads((ROOT / q).read_text()).get("status") for q in manifest["parent_bindings"]
              if q.endswith(".json") and q.startswith("proofs/")}
    check("0 dependency artifacts bound by hash; upstream proofs Proved", not bad and all(s in ("Proved", "passed") for s in status.values()),
          {"mismatched": bad, "statuses": status})
    rng = random.Random(20261107)

    # 1. the surfaces
    rows, ok1 = [], True
    for (a, h, c) in [(3, 1, (4, 4)), (4, 2, (6, 6)), (6, 3, (9, 9)), (10, 3, (21, 21)), (12, 4, (24, 24))]:
        D = A.holed_double(a, h, c)
        KS = L.KnotSpace(D)
        dd = Counter(KS.d)
        good = (D.validate() and D.connected() and D.euler() == -2 and D.orientable() and dd[4] == 6 and set(dd) == {3, 4}
                and KS.n == 2 * (9 * a * a - 3 * h * h) and KS.simple())
        ok1 &= good
        rows.append(((a, h), KS.n, D.euler(), dict(dd), good))
    check("1 the doubles of the holed tori T(3a) are closed orientable surfaces of genus 2 whose faces have three corners except six "
          "with four (the hexagon's corners, degree 8)", ok1, {"(a, h), n, chi, face sizes": rows})

    # 2. frame holonomy around faces (class independent)
    ok2, hol = True, Counter()
    for (a, h, c) in [(4, 2, (6, 6)), (10, 3, (21, 21))]:
        D = A.holed_double(a, h, c)
        KS = L.KnotSpace(D)
        for bits, s in A.signings(KS):
            K = A.flat_dict(KS, s)
            for v in range(D.nv):
                hv = F.face_holonomy(K, v)
                hol[(KS.d[v], hv)] += 1
                ok2 &= hv == ((0, 0, 0) if KS.d[v] == 3 else (2, 1, 1))
    check("2 in every sign class the frames are flat around three-corner faces and turn by label +1 around each degree-8 face "
          "(sublattice -1, complement), the mirror of the sphere corners' -1", ok2, {"(corners, holonomy): count": {str(k): v for k, v in hol.items()}})

    # 3. the local lemma
    check("3 local lemma: in a common frame a triangle on three sublattices with labels within two consecutive values is never "
          "monochromatic (48 cases)", A.local_lemma(), {})

    # 4. the antivortex flat state: exactly one class develops; no violated line and one over-agreeing face, at z
    ok4, info4 = True, []
    for m in (3, 5):
        a, h, c, mm, x0, y0 = params(m)
        consistent, states = [], []
        for bits, s in A.signings(L.KnotSpace(A.holed_double(a, h, c))):
            red = A.build(a, h, c, mm, x0, y0, classes={bits})
            if red is not None and red.get("bits") is not None:
                consistent.append(bits)
                KS, z = red["KS"], red["z"]
                for zc in (0, 1):
                    x = list(red["x_out"])
                    x[z] = zc
                    vl, ov = A.defects(KS, red["s"], x)
                    at_z = all(z in red["K"]["fpts"][v] for v in ov)
                    states.append((zc, len(vl), len(ov), at_z))
        good = len(consistent) == 1 and all(st[1] == 0 and st[2] == 1 and st[3] for st in states)
        ok4 &= good
        info4.append((m, a, consistent, states))
    check("4 of the 16 Kasteleyn classes exactly one develops consistently over the surface cut along a chart-confined star; its state "
          "violates no line and over-agrees at exactly one face, at z, for either colour of z (so the knot's lines are satisfiable)",
          ok4, {"(m, a, consistent class, (z colour, violated, over-agreeing, at z))": info4})

    # 5. the reduction: boundary and defects
    ok5, info5 = True, []
    for m in range(3, 8):
        red = A.build(*params(m))
        KS, s, R, mm = red["KS"], red["s"], red["R"], red["m"]
        target = A.canonical_boundary(mm, (0, 2, 1))
        good = red["boundary_ok"] and all(red["bcol"][v] == target[v] for v in target)
        reads = max(len(SP.coarse_of(XY)) for XY in R.values())
        tot = Counter()
        for trial in range(16):
            cint = colouring(mm, rng, (trial % 3) - 1)
            x, col = A.image(red, cint)
            vl, ov = A.defects(KS, s, x)
            full = SP.full_triangles(col, mm)
            ccw = {t for t in full if A.orient(col, t) > 0}
            cw = set(full) - ccw
            lt = [SP.coarse_triangle_of_line(red, l) for l in vl]
            ft = [coarse_triangle_of_face(red, v) for v in ov]
            good &= None not in lt and None not in ft
            good &= sorted(lt) == sorted(tuple(sorted(t)) for t in ccw)
            good &= sorted(ft) == sorted(tuple(sorted(t)) for t in cw)
            good &= len(cw) - len(ccw) == 1
            tot["ccw"] += len(ccw)
            tot["cw"] += len(cw)
        good &= reads <= 2
        ok5 &= good
        info5.append((mm, KS.n, dict(tot), good))
    check("5 for m = 3..7 the region's boundary is the canonical Sperner boundary with colours 1 and 2 swapped; on 80 colourings the "
          "violated lines sit exactly one in each counterclockwise fully labelled triangle and the over-agreeing faces exactly one in each "
          "clockwise one, nothing outside the region, and every point reads at most two Sperner colours", ok5,
          {"(m, n, full triangles, ok)": info5})

    # 6. the count on genus 2
    red = A.build(*params(3))
    KS, s = red["KS"], red["s"]
    ok6, nn = True, 0
    for _ in range(40):
        x = L.random_assignment(KS.n, rng)
        good, viol, E = KS.count_identity(s, x)
        ok6 &= good and E - viol == 1
        nn += 1
    check("6 the count: over-agreement minus violated lines is 1 under every tested assignment, so an over-agreeing face always exists "
          "and the face problem is total", ok6, {"assignments": nn})

    # 7. controls
    ctrl = {}
    D2 = A.holed_double(None, 3, (12, 12), L_vectors=(25, 0, 25))
    KS2 = L.KnotSpace(D2)
    any_ok = False
    for bits, s in A.signings(KS2):
        K2 = A.flat_dict(KS2, s)
        G2 = F.gamma(K2)
        z2 = A.point_at(D2, KS2, 0, 2, 2)
        star2 = F.disjoint_paths(G2, F.triangles_at(K2, G2, z2), [("f", v) for v in range(D2.nv) if KS2.d[v] == 4], z2, random.Random(1))
        try:
            F.develop(K2, z2, star2, next(p for p in range(KS2.n) if p != z2))
            any_ok = True
        except AssertionError:
            pass
    ctrl["a torus with L not in L3 (25 x 25): no class develops (the handles turn the sublattice)"] = not any_ok
    red = A.build(*params(4))
    rngc = random.Random(3)
    swapped_fails = False
    for _ in range(10):
        x, col = A.image(red, colouring(4, rngc, 1))
        vl, ov = A.defects(red["KS"], red["s"], x)
        full = SP.full_triangles(col, 4)
        cw = [t for t in full if A.orient(col, t) < 0]
        swapped_fails |= len(vl) != len(cw)
    ctrl["counting violated lines against clockwise triangles fails"] = swapped_fails
    ctrl["the unswapped canonical boundary (0, 1, 2) differs from the region's"] = any(
        red["bcol"][v] != b for v, b in A.canonical_boundary(4).items())
    check("7 controls: each check can fail", all(v for v in ctrl.values()), ctrl)

    out = {"status": "passed", "checks": OUT}
    res = HERE / "result.json"
    if "--write" in sys.argv:
        res.write_text(json.dumps(out, indent=1, default=str) + "\n")
        print("wrote", res)
    else:
        old = json.loads(res.read_text())
        same = json.loads(json.dumps(out, default=str))["checks"] == old["checks"]
        print("result.json reproduced" if same else "result.json DIFFERS")
        sys.exit(0 if same else 1)
