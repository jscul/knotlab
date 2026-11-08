#!/usr/bin/env python3
"""Checks for UNIFORM-SPHERES-20261107-001A: uniform laws and the spheres they can close into.

    python3 -B check.py          verify result.json against a fresh run
    python3 -B check.py --write  write result.json from a fresh run
Run with the repository's .venv (pysat). Single process; about a minute."""
import hashlib
import itertools
import json
import math
import random
import sys
import time
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
import uniform_lib as U  # noqa: E402
L = U.L

T0 = time.time()
OUT = {}


def check(name, ok, info):
    OUT[name] = {"pass": bool(ok), "info": info}
    print("PASS" if ok else "FAIL", name, json.dumps(info, default=str)[:600], round(time.time() - T0, 1), "s", flush=True)
    if not ok:
        sys.exit(1)


def census(rng):
    """the uniform Cayley laws used throughout"""
    laws = [U.cayley_law(U.perm([[0, 1], [2, 3]], 4), U.perm([[0, 2], [1, 3]], 4), "V4")]
    for d in (3, 4, 5, 6, 8, 12):
        x, y = U.dihedral(d)
        laws.append(U.cayley_law(x, y, f"D{d}"))
    for nm, G, t in [("A4", U.alternating(4), (2, 3, 3)), ("S4", U.symmetric(4), (2, 3, 4)), ("A5", U.alternating(5), (2, 3, 5))]:
        x, y = U.find_pair(G, *t, rng=rng)
        laws.append(U.cayley_law(x, y, nm))
    for kind in [(3, 3, 3), (2, 4, 4), (2, 3, 6)]:
        for k in (3, 4):
            x, y = U.wallpaper_pair(kind, k)
            laws.append(U.cayley_law(x, y, f"{kind}/Z{k}^2"))
    x, y = U.find_pair(U.gl32(), 2, 3, 7)
    laws.append(U.cayley_law(x, y, "PSL(2,7)"))
    laws.append(U.cayley_law(tuple((i + 1) % 7 for i in range(7)), tuple((i + 2) % 7 for i in range(7)), "Z7 (Fano)"))
    return laws


if __name__ == "__main__":
    manifest = json.loads((HERE / "manifest.json").read_text())
    bad = {q: dg for q, dg in manifest["parent_bindings"].items() if hashlib.sha256((ROOT / q).read_bytes()).hexdigest() != dg}
    status = {q: json.loads((ROOT / q).read_text()).get("status") for q in manifest["parent_bindings"]
              if q.endswith(".json") and q.startswith("proofs/")}
    check("0 dependency artifacts bound by hash; upstream proofs Proved", not bad and all(s in ("Proved", "passed") for s in status.values()),
          {"mismatched": bad, "statuses": status})
    rng = random.Random(20261107)
    LAWS = census(rng)

    # 1. Cayley laws build closed orientable surfaces with the curvature formula
    ok1, rows = True, []
    for S in LAWS:
        K = L.KnotSpace(S)
        d1, d2, d3 = S.type
        formula = K.n * (Fraction(1, d1) + Fraction(1, d2) + Fraction(1, d3) - 1)
        good = S.validate() and S.connected() and S.orientable() and K.simple() and S.euler() == formula
        good &= dict(U.point_types(K)) == {tuple(sorted(S.type)): K.n}
        ok1 &= good
        rows.append((S.name, S.type, K.n, S.euler()))
    check("1 every Cayley law C(G; x, y) is a closed orientable surface built from its own lines and co-lines; every point has co-line "
          "sizes (|x|, |y|, |xy|) and chi = n(1/d1 + 1/d2 + 1/d3 - 1)", ok1, {"(law, type, n, chi)": rows})

    # 2. the spherical types
    sph = U.spherical_types(60)
    expect = {((2, 2, d), 2 * d) for d in range(2, 61)} | {((2, 3, 3), 12), ((2, 3, 4), 24), ((2, 3, 5), 60)}
    got = {(t, int(n)) for t, n in sph if n == int(n)}
    check("2 the types with 1/d1 + 1/d2 + 1/d3 > 1 (d >= 2, up to 60) are exactly (2,2,d) with n = 2d and (2,3,3), (2,3,4), (2,3,5) with "
          "n = 12, 24, 60; all are realized above (V4, dihedral groups, A4, S4, A5)", got == expect and all(n == int(n) for _, n in sph),
          {"spherical types": len(sph), "non-dihedral": sorted(t for t, n in got if t[1] > 2)})

    # 3. uniform signs never force the lines
    ok3, rows3 = True, []
    for S in LAWS:
        K = L.KnotSpace(S)
        sides = []
        for sigma in itertools.product((0, 1), repeat=3):
            s = U.uniform_signing(K, sigma)
            D = K.even_faces(s)
            even = sum(1 for v in range(K.V) if K.d[v] % 2 == 0)
            ok3 &= set(v for v in range(K.V) if K.d[v] % 2 == 0) <= set(D)
            ok3 &= K.chi - len(D) <= 0
            for _ in range(3):
                good, viol, E = K.count_identity(s, L.random_assignment(K.n, rng))
                ok3 &= good
            sides.append("faces" if K.chi < len(D) else "none")
        rows3.append((S.name, sorted(set(sides))))
    check("3 with uniform signs every even co-line is an even face, so chi - |D| <= n(sum of 1/d over odd sizes - 1) <= 0: the count never "
          "forces a line to fail on any uniform law, and on every uniform sphere it forces over-agreement instead", ok3,
          {"(law, forced side over the 8 uniform patterns)": rows3})

    # 4. the knot with uniform signs; the circulant census
    ok4, rows4 = True, []
    for S in LAWS:
        K = L.KnotSpace(S)
        sat = [K.sat(U.uniform_signing(K, sigma))[0] for sigma in itertools.product((0, 1), repeat=3)]
        if S.name.startswith("Z7"):
            ok4 &= sat == [False, True, True, True, True, True, True, False]
        else:
            ok4 &= all(sat)
        rows4.append((S.name, sum(sat)))
    unsat, total = [], 0
    for n in range(3, 49):
        seen = set()
        for a in range(1, n):
            for b in range(1, n):
                if math.gcd(math.gcd(a, b), n) != 1:
                    continue
                ds = {0, a % n, (a + b) % n}
                if len(ds) < 3:
                    continue
                canon = min(tuple(sorted((u * t - u * s0) % n for t in ds)) for u in range(1, n) if math.gcd(u, n) == 1 for s0 in ds)
                if canon in seen:
                    continue
                seen.add(canon)
                S = U.cayley_law(tuple((i + a) % n for i in range(n)), tuple((i + b) % n for i in range(n)))
                K = L.KnotSpace(S)
                if not K.simple():
                    continue
                total += 1
                for sigma in itertools.product((0, 1), repeat=3):
                    if not K.sat(U.uniform_signing(K, sigma))[0]:
                        unsat.append((n, sorted(ds), sigma))
    ok4 &= [(u[0], u[1]) for u in unsat] == [(7, [0, 1, 3])] * 2
    check("4 with uniform signs the knot is satisfiable on every law above except the Fano plane (Z7, lines {g, g+1, g+3}, all signs "
          "equal), and among all circulant laws with n <= 48 the Fano plane is the only unsatisfiable one", ok4,
          {"(law, satisfiable uniform patterns of 8)": rows4, "circulant laws": total, "unsatisfiable": unsat})

    # 5. Kasteleyn signs (not uniform): the knot fails on every uniform sphere, holds on the flat and hyperbolic laws tested
    ok5, rows5 = True, []
    for S in LAWS:
        K = L.KnotSpace(S)
        s0 = K.signing(())
        if s0 is None or S.name.startswith("Z7"):     # the Fano law: its uniform signs are already Kasteleyn and fail (check 4)
            continue
        Z = K.classes()
        picks = list(itertools.product((0, 1), repeat=len(Z))) if len(Z) <= 2 else [tuple(rng.randrange(2) for _ in Z) for _ in range(4)]
        res = []
        for bits in picks:
            s = list(s0)
            for b, z in zip(bits, Z):
                if b:
                    s = [u ^ w for u, w in zip(s, z)]
            res.append(K.sat(s)[0])
        sphere = K.chi == 2
        ok5 &= (not any(res)) if sphere else all(res)
        uniform_kast = any(not K.even_faces(U.uniform_signing(K, sg)) for sg in itertools.product((0, 1), repeat=3))
        ok5 &= not (sphere and uniform_kast)
        rows5.append((S.name, K.chi, f"{sum(res)}/{len(res)}", uniform_kast))
    check("5 with Kasteleyn signs (no even face) the knot is unsatisfiable on every uniform sphere and satisfiable in every tested class of "
          "the flat and hyperbolic laws; on spheres no uniform pattern is Kasteleyn", ok5,
          {"(law, chi, satisfiable classes, a uniform pattern is Kasteleyn)": rows5})

    # 6. the antiprism laws are cyclic chains: binary search
    ok6, rows6 = True, []
    for d in (3, 5, 8, 16, 64, 256):
        x, y = U.dihedral(d)
        S = U.cayley_law(x, y, f"D{d}")
        K = L.KnotSpace(S)
        blk, nb = U.antiprism_blocks(S)
        w = U.chain_width(K, blk)
        s = K.signing(())
        mq = 0
        good = w == 1 and not K.sat(s)[0]
        for _ in range(20):
            xx = L.random_assignment(K.n, rng)
            li, Q = U.find_violated_chain(K, s, xx, blk, nb)
            lit = [xx[K.pt[li][k]] ^ s[3 * li + k] for k in range(3)]
            good &= lit[0] == lit[1] == lit[2]
            mq = max(mq, len(Q))
        good &= mq <= 2 * math.ceil(math.log2(d)) + 8
        ok6 &= good
        rows6.append((d, K.n, w, mq))
    check("6 the antiprism laws C(D_d) are cyclic chains of width 1; with Kasteleyn signs binary search finds a violated line with at most "
          "2 log2 d + 8 queries (FP^dt)", ok6, {"(d, n, width, most queries)": rows6})

    # 7. the knot sphere has two kinds of points
    ok7, rows7 = True, []
    for k in range(2, 7):
        K = L.KnotSpace(L.octahedral_sphere(k))
        pt = dict(U.point_types(K))
        good = pt == {(3, 3, 3): K.n - 12, (2, 3, 3): 12} and sum(1 for v in range(K.V) if K.d[v] == 2) == 6
        ok7 &= good
        rows7.append((k, K.n, {str(t): c for t, c in pt.items()}))
    check("7 the knot sphere K_k has exactly two kinds of points, (3,3,3) and (2,3,3) (the twelve points at its six digons): one kind more "
          "than any uniform law, and its contradiction is PPADS-complete (COUNT-TFNP-20261107-001B)", ok7, {"(k, n, point types)": rows7})

    # 8. controls
    ctrl = {}
    S = LAWS[7]
    broken = L.Surface("broken", S.colour, [list(r) for r in S.side], [list(r) for r in S.cmap])
    t = S.nt // 2
    broken.side[t][0], broken.side[t][1] = broken.side[t][1], broken.side[t][0]
    try:
        broken_ok = broken.validate()
    except (KeyError, AssertionError):
        broken_ok = False
    ctrl["a law whose line meets its points in the wrong slots is not a surface"] = not broken_ok
    K = L.KnotSpace(LAWS[1])
    s1 = U.uniform_signing(K, (0, 0, 0))
    wrong = False
    for _ in range(5):
        viol, agree = K.tallies(s1, L.random_assignment(K.n, rng))
        wrong |= 2 * (viol - sum(a // 2 for a in agree)) != K.chi + 2 - len(K.even_faces(s1))
    ctrl["on a uniform sphere the count with chi replaced by chi + 2 fails"] = wrong
    x, y = U.dihedral(16)
    S16 = U.cayley_law(x, y, "D16")
    K16 = L.KnotSpace(S16)
    ctrl["blocks by the image of 0 alone give width > 1"] = U.chain_width(K16, {S16.idx[g]: g[0] for g in S16.group}) > 1
    check("8 controls: each check can fail", all(ctrl.values()), ctrl)

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
