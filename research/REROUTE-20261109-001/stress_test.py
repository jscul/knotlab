"""Stress test for REROUTE-20261109-001, one size past what was checked: (1) the triangular and honeycomb line networks (computed in
REROUTE-20261109-001B, check 3, to n = 20) on every n x n torus from 21 to 28; (2) H3 of REROUTE-20261109-001C-E001 (to n = 16) on random
re-routings of the three n = 20 tori, four seeds, every ring of at most 12 contacts read for every target.

    .venv/bin/python3 -B stress_test.py    writes stress_test.json beside it
"""
import json
import random
import sys
import time
from multiprocessing import Pool
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "proofs/REROUTE-20261109-001B/REROUTE-20261109-001B-P001_rerouting_keeps_persistence"))
import reroute_lib as RR  # noqa: E402


def lines(args):
    kind, n, cls = args
    sig, rot, edges, B = RR.lattice(kind, n)
    cl = RR.classes(kind, rot)
    s = RR.reroute(sig, set().union(*[cl[k] for k in cls]))
    if not RR.is_network(s):
        return args, None
    rs = RR.rings(s)
    return args, {"rings": len(rs), "late": RR.late_pairs(s), "no single fastest way": RR.late_pairs(s, single=True),
                  "balls 2r + 1": RR.ring_graph_balls(s, n - 1, roots=[0])[0] == [min(2 * r + 1, len(rs)) for r in range(n)]}


def small_rings(args):
    kind, n, seed = args
    rng = random.Random(20261113 + 100 * seed + n)
    sig, rot, edges, B = RR.lattice(kind, n)
    F = RR.face_moves(sig)
    S = set()
    for _ in range(4 * n * n):
        T = S.symmetric_difference(rng.choice(F))
        if RR.is_network(RR.reroute(sig, T)):
            S = T
    s = RR.reroute(sig, S)
    rs = [cs for cs in RR.rings(s) if len(cs) <= 12]
    late = set()
    for t in range(len(s) // 2):
        dist, par, low = RR.routes_to(s, t)
        for i, cs in enumerate(rs):
            if i in late:
                continue
            m = min(dist[e] for e in cs)
            if not any(par[e] for e in cs if dist[e] == m):
                late.add(i)
    return args, {"rings of at most 12 contacts": len(rs), "late for some target": len(late)}


if __name__ == "__main__":
    t0 = time.time()
    jobs = [("triangular", n, (k,)) for n in range(21, 29) for k in range(3)] + [("honeycomb", n, c) for n in range(21, 29) for c in ((0, 1), (0, 2), (1, 2))]
    with Pool(16) as pool:
        a = pool.map(lines, sorted(jobs, key=lambda j: -j[1]), chunksize=1)
        b = pool.map(small_rings, [(k, 20, sd) for k in ("square", "triangular", "honeycomb") for sd in range(4)], chunksize=1)
    ok1 = all(v is not None and v["late"] == 0 and v["no single fastest way"] == 0 and v["balls 2r + 1"] and v["rings"] == 2 * j[1] for j, v in a)
    ok2 = all(v["late for some target"] == v["rings of at most 12 contacts"] for j, v in b)
    out = {"lines on time with single fastest ways, n = 21 to 28": ok1, "networks": len(a),
           "H3 at n = 20": ok2, "small rings late / read": [sum(v["late for some target"] for j, v in b), sum(v["rings of at most 12 contacts"] for j, v in b)],
           "rows": {"%s %d %s" % j: v for j, v in a + b}, "seconds": round(time.time() - t0, 1)}
    (HERE / "stress_test.json").write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=1))
