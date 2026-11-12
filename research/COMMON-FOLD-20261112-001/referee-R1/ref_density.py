#!/usr/bin/env python3
"""Referee COMMON-FOLD-R1: how close the tied bases are to having no state. For every base (outcome "base") at r = 3 to 8, the
number of states on the 6 x 6 torus and on the 8 x 8 torus (capped at 20,000; 0 when that torus carries none), by class.
Writes result_density.json."""
import json
import random
import statistics as st
import sys
from pathlib import Path

from pysat.solvers import Glucose4

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import ref_fold as R  # noqa: E402


def torus_count(K, P, Q, cap=20000):
    cells = [(x, y) for x in range(P) for y in range(Q)]
    idx = {c: i + 1 for i, c in enumerate(cells)}
    cl = []
    for (x, y) in cells:
        for k in K:
            v = [idx[((x + a) % P, (y + b) % Q)] for a, b in k]
            cl += [v, [-u for u in v]]
    n = 0
    with Glucose4(bootstrap_with=cl) as s:
        while s.solve():
            m = s.get_model()
            n += 1
            if n >= cap:
                return n
            s.add_clause([-x for x in m[:P * Q]])
    return n


if __name__ == "__main__":
    mine = {json.loads(l)["sample"]: json.loads(l) for l in open(HERE / "result_fold.jsonl")}
    out = {}
    for r in range(3, 9):
        by = {}
        for i in range(200):
            rec = mine[i]["by r"][str(r)]
            if rec["outcome"] != "base":
                continue
            K = random.Random(50000 + i).sample(R.KINDS, 8)[:r]
            c6, c8 = torus_count(K, 6, 6), torus_count(K, 8, 8)
            by.setdefault(rec["class"], []).append([c6, c8])
        out[str(r)] = {c: {"bases": len(v), "median states on 6x6": st.median(x[0] for x in v),
                           "median states on 8x8": st.median(x[1] for x in v), "share with no state on 8x8": sum(x[1] == 0 for x in v) / len(v)}
                       for c, v in by.items()}
        print(r, json.dumps(out[str(r)]), flush=True)
    (HERE / "result_density.json").write_text(json.dumps(out, indent=1) + "\n")
