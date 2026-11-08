#!/usr/bin/env python3
"""Checks for GROW-COIN-20261107-001A: refinement shares its coin, accretion must carry it.

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
import growth_lib as GL  # noqa: E402
SM, SL = GL.SM, GL.SL

T0 = time.time()
OUT = {}


def check(name, ok, info):
    OUT[name] = {"pass": bool(ok), "info": info}
    print("PASS" if ok else "FAIL", name, json.dumps(info, default=str)[:600], round(time.time() - T0, 1), "s", flush=True)
    if not ok:
        sys.exit(1)


if __name__ == "__main__":
    manifest = json.loads((HERE / "manifest.json").read_text())
    bad = {q: dg for q, dg in manifest["parent_bindings"].items() if hashlib.sha256((ROOT / q).read_bytes()).hexdigest() != dg}
    status = {q: json.loads((ROOT / q).read_text()).get("status") for q in manifest["parent_bindings"]
              if q.endswith(".json") and q.startswith("proofs/")}
    check("0 dependency artifacts bound by hash; upstream proofs Proved", not bad and all(s in ("Proved", "passed") for s in status.values()),
          {"mismatched": bad, "statuses": status})

    # 1 refinement: K_m -> K_jm, all-or-nothing; it scales a tube to a tube, so it keeps whatever shape it is given
    rows, ok = [], True
    for m in range(1, 5):
        for j in (2, 3):
            S = SM.from_triangles("s", GL.subdivide(SM.octahedral(m).vtris, j))
            good = GL.two_kind_sphere(S) and SM.isomorphic(S, SL.octahedral_sphere(m * j))
            rows.append([m, j, S.nt, good])
            ok &= good
    tube_rows = []
    for (m, L, tau) in ((1, 3, 0), (2, 3, 1)):
        S = SM.from_triangles("s", GL.subdivide(SM.tube(m, L, tau).vtris, 2))
        same = SM.isomorphic(S, SM.tube(2 * m, 2 * L, 2 * tau))
        tube_rows.append([[m, L, tau], same, GL.is_K(S)])
        ok &= same and not GL.is_K(S)
    K2 = SM.octahedral(2).vtris
    partial = GL.subdivide(K2[:1], 2) + K2[1:]
    try:
        SM.from_triangles("p", partial)
        partial_ok = True
    except ValueError:
        partial_ok = False
    ok &= not partial_ok
    check("1 refinement: subdividing K_m into j^2 gives K_jm (m <= 4, j = 2, 3); a tube refines to a tube; refining one triangle "
          "alone leaves no closed surface", ok, {"[m, j, triangles, = K_jm]": rows, "[tube, refines to tube(2m, 2L, 2tau), round]": tube_rows,
                                                 "one triangle refined alone is a closed surface": partial_ok})

    # 2 accretion by rings: the four turns of one ring made corners gives K_m
    rows, ok = [], True
    for m in range(1, 7):
        G, why = GL.uniform(m)
        S = SM.from_triangles("g", G.tris)
        good = why == "closed" and GL.two_kind_sphere(S) and SM.isomorphic(S, SL.octahedral_sphere(m))
        rows.append([m, why, S.nt, good])
        ok &= good
    check("2 ring growth with the four turns of ring m made corners closes into K_m (m <= 6)", ok, {"[m, end, triangles, = K_m]": rows})

    # 3 every choice pattern up to 100 triangles: the round outputs come only from the uniform patterns
    closed = GL.enumerate_closed(100)
    valid = all(GL.two_kind_sphere(S) for S, _ in closed)
    reps = GL.distinct([S for S, _ in closed])
    round_reps = [S.nt for S in reps if GL.is_K(S)]
    other_reps = sorted(S.nt for S in reps if not GL.is_K(S))
    pats_round = Counter()
    for S, pat in closed:
        if GL.is_K(S):
            corners_at = [(d, s, c) for d, s, c in pat if s]
            uniform_pat = len(corners_at) == 1 and corners_at[0][1] == corners_at[0][2] == 4
            pats_round[uniform_pat] += 1
    check("3 every choice pattern up to 100 triangles: all closed outputs are two-kind spheres; the round ones arise only when all "
          "four turns of one ring become corners together; the others are not round",
          valid and pats_round.get(False, 0) == 0 and len(other_reps) > 0,
          {"closed runs": len(closed), "distinct spheres": len(reps), "round (triangles)": round_reps,
           "non-round (triangles)": other_reps, "round runs from uniform patterns / others": [pats_round.get(True, 0), pats_round.get(False, 0)]})

    # 4 independent coins: each turn made a corner with probability p, independently
    rng = random.Random(20261107)
    res = Counter()
    sizes = Counter()
    for trial in range(400):
        p = (0.05, 0.1, 0.2, 0.35)[trial % 4]
        G, why = GL.grow(lambda r, G, cv: [v for v in cv if rng.random() < p], maxrings=60)
        if why == "closed":
            S = SM.from_triangles("g", G.tris)
            res["closed round" if GL.is_K(S) else "closed non-round"] += 1
            if not GL.is_K(S):
                sizes[S.nt] += 1
        else:
            res[why] += 1
    check("4 with an independent coin at every turn, ring growth closes into non-round spheres as well as round ones",
          res["closed non-round"] > 0, {"runs": dict(res), "non-round sizes": dict(sorted(sizes.items())[:20])})

    # 5 single-strip accretion: when a turn is decided, its radius-w window is the same in every lap of ring >= w + 1
    rows, ok = [], True
    for w in (2, 3, 4, 5):
        for m in range(w + 2, w + 6):
            dec = GL.turn_decisions(m, w)
            corner = {win for r, d, win in dec if d == "corner"}
            flat = {win for r, d, win in dec if d == "flat" and r >= w + 1}
            n_corner = sum(1 for _, d, _ in dec if d == "corner")
            rows.append([w, m, n_corner, len(corner), corner <= flat])
            ok &= n_corner == 3 and len(corner) == 1 and corner <= flat
    small = GL.turn_decisions(3, 3)
    ctrl = {win for r, d, win in small if d == "corner"} & {win for r, d, win in small if d == "flat"}
    check("5 single-strip ring growth of K_m: at the three equator turns decided in its lap (the fourth starts the lap), the "
          "radius-w window is the window at which earlier rings' turns go flat (w <= 5, m = w + 2 .. w + 5)", ok,
          {"[w, m, corner decisions, distinct corner windows, all among flat windows]": rows,
           "control m = w = 3: corner and flat windows shared": len(ctrl)})

    # 6 the window law of one order, run in random orders: what it closes
    law = GL.window_law(range(1, 11), 5)
    rng = random.Random(7)
    res, sizes = Counter(), Counter()
    for _ in range(200):
        D, why = GL.random_order_run(law, 5, rng)
        res[why] += 1
        if why == "closed":
            S = SM.from_triangles("g", D.tris)
            sizes[(S.nt, GL.is_K(S))] += 1
    check("6 the radius-5 window law of the single-strip order, run in random orders, closes only small round spheres and is "
          "otherwise stuck (no evidence about large sizes)", res["closed"] > 0 and all(r for (_, r) in sizes),
          {"law windows": len(law), "runs": dict(res), "[triangles, round]: runs": {str(k): v for k, v in sorted(sizes.items())}})

    out = {"status": "passed", "checks": OUT}
    res_path = HERE / "result.json"
    if "--write" in sys.argv:
        res_path.write_text(json.dumps(out, indent=1, default=str) + "\n")
        print("wrote", res_path)
    else:
        old = json.loads(res_path.read_text())
        same = json.loads(json.dumps(out, default=str))["checks"] == old["checks"]
        print("result.json reproduced" if same else "result.json DIFFERS")
        sys.exit(0 if same else 1)
