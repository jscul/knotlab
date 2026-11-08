#!/usr/bin/env python3
"""Checks for SPHERE-GROWTH-20261107-001A: round spheres need one hidden bit per incidence.

    python3 -B check.py          verify result.json against a fresh run
    python3 -B check.py --write  write result.json from a fresh run
Run with the repository's .venv (pysat, numpy). Single process; a few minutes."""
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
import seam_lib as SM  # noqa: E402
SL = SM.SL

T0 = time.time()
OUT = {}


def check(name, ok, info):
    OUT[name] = {"pass": bool(ok), "info": info}
    print("PASS" if ok else "FAIL", name, json.dumps(info, default=str)[:600], round(time.time() - T0, 1), "s", flush=True)
    if not ok:
        sys.exit(1)


def two_kind_sphere(S):
    return S.validate() and S.euler() == 2 and set(SM.degrees(S)) <= {4, 6}


def is_K(S):
    return any(SM.isomorphic(SL.octahedral_sphere(m), S) for m in range(1, 12) if 8 * m * m == S.nt)


if __name__ == "__main__":
    manifest = json.loads((HERE / "manifest.json").read_text())
    bad = {q: dg for q, dg in manifest["parent_bindings"].items() if hashlib.sha256((ROOT / q).read_bytes()).hexdigest() != dg}
    status = {q: json.loads((ROOT / q).read_text()).get("status") for q in manifest["parent_bindings"]
              if q.endswith(".json") and q.startswith("proofs/")}
    check("0 dependency artifacts bound by hash; upstream proofs Proved", not bad and all(s in ("Proved", "passed") for s in status.values()),
          {"mismatched": bad, "statuses": status})

    # 1 constructions; six digons on every closed two-kind sphere
    rows, ok = [], True
    for m in range(1, 6):
        K = SM.octahedral(m)
        same = SM.isomorphic(K, SL.octahedral_sphere(m)) and SM.isomorphic(K, SM.tube(m, m, 0))
        rows.append(["K", m, K.nt, same, SM.degrees(K).count(4)])
        ok &= same and two_kind_sphere(K) and SM.degrees(K).count(4) == 6
    tubes = [(m, L, tau) for m in range(1, 5) for L in range(1, m + 4) for tau in range(m)]
    digons = Counter()
    for (m, L, tau) in tubes:
        T = SM.tube(m, L, tau)
        ok &= two_kind_sphere(T)
        digons[SM.degrees(T).count(4)] += 1
    rng = random.Random(20261107)
    grown, tries = [], 0
    while len(grown) < 60 and tries < 20000:
        tries += 1
        S = SM.random_sphere(rng, q=rng.choice((0.1, 0.2, 0.3)), maxv=300)
        if S is not None:
            grown.append(S)
    for S in grown:
        ok &= two_kind_sphere(S)
        digons[SM.degrees(S).count(4)] += 1
    check("1 K_m built two ways agrees with surface_lib and T(m, m, 0); every tube and grown sphere is a two-kind sphere with six digons",
          ok and set(digons) == {6} and len(grown) == 60,
          {"K_m": rows, "tubes": len(tubes), "grown": len(grown), "growth tries": tries, "digon counts": dict(digons)})

    # 2 the local Kasteleyn rule: no even co-line, and the knot contradicts itself (count identity and a solver)
    ok, info = True, []
    for name, S in ([("K_%d" % m, SM.octahedral(m)) for m in range(2, 6)] + [("T%s" % (p,), SM.tube(*p)) for p in ((2, 5, 1), (3, 7, 0), (3, 4, 2))]
                    + [("grown#%d" % i, grown[i]) for i in range(0, 60, 12)]):
        K, s = SM.kasteleyn(S)
        D = K.even_faces(s)
        r2 = random.Random(len(info))
        idents = all(K.count_identity(s, SL.random_assignment(K.n, r2))[0] for _ in range(20))
        sat = K.sat(s)[0]
        info.append([name, K.n, len(D), idents, sat])
        ok &= (not D) and idents and not sat
    check("2 local Kasteleyn signs leave no even co-line; the count identity holds and every sphere's knot is unsatisfiable", ok, info)

    # 3 the tube lemma: balls of radius r of every tube lie among K_m's once m >= 2r (theorem: m >= 2r + 1); the control m = 2r - 1 fails
    ok, info = True, []
    for r in (1, 2, 3):
        for m in range(max(1, 2 * r - 1), 2 * r + 3):
            BK = SM.ball_set(SM.octahedral(m), r)
            cases = [(m, L, 0) for L in range(2 * r + 1, m + 4)] + [(m, m + 1, tau) for tau in range(1, m)]
            inside = [SM.ball_set(SM.tube(*c), r) <= BK for c in cases if c != (m, m, 0)]
            info.append([r, m, len(BK), sum(inside), len(inside)])
            ok &= all(inside) if m >= 2 * r else not any(inside)
    check("3 tube lemma: every radius-r ball of T(m, L, tau) occurs in K_m for m >= 2r (r <= 3); none of the tubes passes at m = 2r - 1",
          ok, {"[r, m, balls in K_m, tubes inside, tubes]": info})

    # 4 tubes keep the contradiction but stay easy; K_m does not
    tube_w, ok = {}, True
    for m in (2, 3, 4):
        ws = []
        for L in (m, 2 * m, 4 * m, 8 * m):
            K, s = SM.kasteleyn(SM.tube(m, L, 0))
            ws.append([L, K.n, SM.elimination_width(K.S, K)])
        tube_w[m] = ws
        ok &= max(w for _, _, w in ws) <= 4 * m + 1
    k_w = []
    for m in range(2, 9):
        K, s = SM.kasteleyn(SM.octahedral(m))
        k_w.append([m, K.n, SM.elimination_width(K.S, K)])
    ok &= all(a[2] < b[2] for a, b in zip(k_w, k_w[1:]))
    check("4 elimination width on T(m, L, 0) stays <= 4m + 1 at every length L; on K_m it rises with m", ok,
          {"tubes [L, n, width]": tube_w, "K_m [m, n, width]": k_w})

    # 5 the seam law: one marking on K_m (its octahedron's edges), none on every other tube or grown sphere
    ok, kinfo = True, []
    for m in range(1, 6):
        S = SM.octahedral(m)
        mk = SM.seam_markings(S)
        _, rays_ok = SM.straight_rays(S)
        kinfo.append([m, len(mk), len(mk[0]) if mk else 0, bool(mk) and mk[0] == SM.octahedron_edges(S), rays_ok])
        ok &= len(mk) == 1 and len(mk[0]) == 12 * m and mk[0] == SM.octahedron_edges(S) and rays_ok
    agree, with_marking = 0, []
    for (m, L, tau) in tubes:
        T = SM.tube(m, L, tau)
        mk = SM.seam_markings(T, limit=1)
        _, rays_ok = SM.straight_rays(T)
        isK = is_K(T)
        agree += (bool(mk) == isK == rays_ok)
        if mk:
            with_marking.append([m, L, tau])
    g_agree, g_K = 0, 0
    for S in grown:
        mk = SM.seam_markings(S, limit=1)
        _, rays_ok = SM.straight_rays(S)
        isK = is_K(S)
        g_K += isK
        g_agree += (bool(mk) == isK == rays_ok)
    ok &= agree == len(tubes) and g_agree == len(grown)
    check("5 seam law: K_m (m <= 5) has exactly one marking, its octahedron's edges; a tube or grown sphere has one iff it is a K_m",
          ok, {"K_m [m, markings, seams, = edges, rays]": kinfo, "tubes agreeing": [agree, len(tubes)],
               "tubes with a marking": with_marking, "grown agreeing": [g_agree, len(grown)], "grown that are K_m": g_K})

    # 6 control: seams that may turn let non-round tubes through
    ctrl = []
    for c in ((2, 3, 0), (3, 4, 1), (3, 5, 0), (4, 6, 2)):
        T = SM.tube(*c)
        ctrl.append([list(c), len(SM.seam_markings(T, straight=False, limit=2)), len(SM.seam_markings(T, limit=1))])
    check("6 control: without 'opposite' in S2 each of these tubes has markings, with it none", all(a > 0 and b == 0 for _, a, b in ctrl),
          {"[tube, turning markings (limit 2), straight markings]": ctrl})

    # 7 the region map: every cubic bipartite plane multigraph on 4 + 4 vertices with six faces of length 4 is the cube
    Q = SM.cubic_quadrangulations()
    jp = all(sorted(tuple(1 - x for x in row).index(1) for row in M) == [0, 1, 2, 3]
             and all(sorted(row) == [0, 1, 1, 1] for row in M) for M in Q)
    check("7 region-map census: 24 biadjacency matrices, each J - P for a permutation matrix P (the cube)", len(Q) == 24 and jp,
          {"matrices": len(Q), "all J - P": jp})

    # 8 growth without hidden states: closed spheres are rarely round
    sizes = sorted(S.nt for S in grown)
    check("8 random local growth closes in some runs, and its closed spheres are round only as the octahedron K_1",
          g_K == sum(1 for S in grown if S.nt == 8) and max(sizes) > 8 * 9,
          {"closed": len(grown), "tries": tries, "sizes (triangles)": sizes, "K_m among them": g_K})

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
