"""Gates for RIM-EXCESS-20261118-001B-E001.   .venv/bin/python -B checks.py   (writes checks_output.json)"""
import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import job  # noqa: E402

P, W, M, N = job.P, job.W, job.M, job.N
out = {}


def gate(name, ok, detail=""):
    out[name] = {"pass": bool(ok), "detail": detail}
    print("PASS" if ok else "FAIL", name, detail)


T = frozenset({("u", 0, 0)})
DD = W.height_distances(T)
gate("one-knot", P.min_cycle_weight([(0, 0), (1, 0), (0, 1)], DD) == 3 and P.pair_b_polygons(T, (0, 0), (1, 0))[0] == 2,
     "a knot is a polygon of weight 3 = 3(3 - 2); its pairs are at bond distance 2")
T2 = frozenset({("u", 0, 0), ("d", 0, 0)})
gate("two-knot", P.pair_b_polygons(T2, (0, 0), (1, 1), emax=4)[0] is None and P.pair_b_polygons(T2, (0, 0), (1, 0))[0] == 2,
     "the lone double meeting's facing pair has no bond; a shared distinction is two from a lone one")
V, ix, D, S, lone, _ = W.read(job.START)
b, s, to = P.pair_b_polygons(job.START, (0, 3), (4, 0), emax=6, time_limit=120)
gate("referee-disc", b == D[ix[(0, 3)]][ix[(4, 0)]] == 7 and s == 4, "the polygon search finds b = 7 at steps 4 on the referee's twelve-knot disc")
gate("tight-subsets", P.tight_subset_exists([(0, 0), (1, 0), (0, 1), (1, 1)], W.height_distances(T2), exclude_full=True),
     "the four distinctions of two knots sharing two hold a tight proper sub-collection (a knot), checked over all orders")
json.dump(out, open(HERE / "checks_output.json", "w"), indent=1)
print("ALL PASS" if all(v["pass"] for v in out.values()) else "SOME FAIL")
