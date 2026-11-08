#!/usr/bin/env python3
"""Row periods of the native paths of PATH-HYBRID-20261108-001, and which hybrid paths survive one more cell (exact, about a minute).

    .venv/bin/python3 -B research/PATH-HYBRID-20261108-001/periods.py   writes periods.json
- For every native path of tickets A and B: its contacts' row periods (the period of each contact's row sequence of M^T), and
  whether the last contact's row settles on one fixed row (period 1). A fixed row r has rM = r: it is a parity the path conserves.
- For ticket B's 1,120: one more cell on ring A, on ring B (beyond c2, on the long arc) or on ring D, each with its ring's rule,
  positions kept. Survival is tabulated against the last contact's period.
- Among the decided paths of the stress test (stress_test.json), how many have every period at most 12."""
import json
import sys
from collections import Counter, defaultdict
from multiprocessing import Pool
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "experiments/PATH-HYBRID-20261108-001B/PATH-HYBRID-20261108-001B-E001_hybrid_middles"))
import hybrid_lib as H  # noqa: E402

A_PATHS = ROOT / "artifacts/PATH-HYBRID-20261108-001A/PATH-HYBRID-20261108-001A-E001_broad_sweep/run/paths.json"
B_PATHS = ROOT / "artifacts/PATH-HYBRID-20261108-001B/PATH-HYBRID-20261108-001B-E001_hybrid_middles/run/paths.json"


def native(rules, sizes, ks, laws):
    a = H.analyze(rules, sizes, ks, laws)
    return a["all persist"] and a["ends at the last contact"]


def grow(x):
    rules, sizes, ks, laws = x
    rules = (rules[0], rules[1], list(rules[2]) if isinstance(rules[2], list) else rules[2], rules[3])
    laws = tuple(tuple(l) for l in laws)
    out = {}
    for name, i in (("A", 0), ("B", 1), ("D", 3)):
        s = list(sizes)
        s[i] += 1
        out[name] = native(rules, tuple(s), list(ks), laws)
    return out


def main():
    a_rows = [r for r in json.loads(A_PATHS.read_text())["rows"] if r[4]]
    b = json.loads(B_PATHS.read_text())
    b_rows = [r for r in b["rows"] if r[b["columns"].index("native")]]
    pi = b["columns"].index("row periods")
    out = {"ticket A: last contact's period (paths)": dict(Counter(str(r[8][2]) for r in a_rows)),
           "ticket B: last contact's period (paths)": dict(Counter(str(r[pi][2]) for r in b_rows)),
           "ticket B: all three contacts settle on fixed rows (paths)": sum(1 for r in b_rows if r[pi] == [1, 1, 1])}
    with Pool(16) as pool:
        res = pool.map(grow, [(r[0], r[1], r[2], r[3]) for r in b_rows], chunksize=8)
    by = defaultdict(Counter)
    for r, g in zip(b_rows, res):
        p = r[pi][2]
        by[p]["paths"] += 1
        for k, v in g.items():
            by[p][f"native with one more cell on {k}"] += v
    out["ticket B: survival of one more cell, by the last contact's period"] = {str(p): dict(c) for p, c in sorted(by.items())}
    out["ticket B: survival totals"] = {k: sum(g[k] for g in res) for k in ("A", "B", "D")}
    st = json.loads((HERE / "stress_test.json").read_text())["transport of the construction"]
    out["stress test: decided paths with every period at most 12"] = st["share of decided paths with every row period at most 12"]
    (HERE / "periods.json").write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
