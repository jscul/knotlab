#!/usr/bin/env python3
"""PLAIN-TIME-20261108-001 stress test: the computed pattern of the covers' first late distance, one type past the checked ones, as
predictions written before the run: l(3,13) = (3 - 1)(13 - 1) + 1 = 25 and l(13,3) = 26 (coprime types; plus 1 when the faces are
triangles and the rings larger). Two primes each.

    .venv/bin/python3 -B research/PLAIN-TIME-20261108-001/stress_test.py   writes stress_test.json beside this file"""
import json
import sys
from multiprocessing import Pool
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "proofs/PLAIN-TIME-20261108-001B/PLAIN-TIME-20261108-001B-P001_only_the_sphere_reads_distance_plainly"))
import cover_lib as C  # noqa: E402

PRED = {(3, 13): (25, 27), (13, 3): (26, 28)}


def task(args):
    (m, f), R, start = args
    p = C.prime_for(m, f, start)
    layers, by, late = C.cover_ball(m, f, p, R)
    return m, f, p, sum(layers), min(late) if late else None


if __name__ == "__main__":
    with Pool(4) as pool:
        res = pool.map(task, [(mf, R, s) for mf, (pred, R) in PRED.items() for s in (10 ** 7, 3 * 10 ** 7)])
    out = {}
    for (m, f), (pred, R) in PRED.items():
        rows = [r for r in res if (r[0], r[1]) == (m, f)]
        out["(%d,%d)" % (m, f)] = {"predicted": pred, "radius": R, "first late (two primes)": [r[4] for r in rows],
                                   "ball contacts": rows[0][3], "pass": all(r[4] == pred for r in rows)}
    (HERE / "stress_test.json").write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps(out, indent=1))
