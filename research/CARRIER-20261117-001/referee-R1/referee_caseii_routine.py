"""Referee R1 for CARRIER-20261117-001, the owner's point (a): the study's stem descent restricted to case (ii) (O_v not below O_u),
against the referee's SAT values for case (ii) pairs (referee_carrier_caseii.json).  This file runs the study's own head_bond.py
(only to read what its case (ii) states give); the values it is compared with are the referee's.

  ../../../.venv/bin/python -B referee_caseii_routine.py > referee_caseii_routine.json      (from this directory)
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(ROOT / "research/DIRECT-REACH-20261115-001/exploratory"))
import head_bond as H  # noqa: E402  (the study's routine, read only)
from window_tree import WindowTree, level_states  # noqa: E402

THIRD = json.load(open(ROOT / "research/KEEP-REACH-20261117-001/third_class.json"))["third"]


def direct_head_split(tree, N, k, s, d):
    F = tree.feasible(N)
    st = level_states(tree, N, F)
    allstates = H.level_k_states(tree, k, lambda lvl: F[N - lvl - 1], F[N - k], st)
    case_i = {(tree.m[t], tree.m[t], t, frozenset((x, x) for x in up if x in F[N - k][t])) for t, up in st[k]}
    out = {}
    for name, init in (("i", allstates & case_i), ("ii", allstates - case_i)):
        S = frozenset(init)
        for lvl in range(k, k + s):
            S = H.advance(tree, S, F[N - lvl - 1], record=lvl < k + d)
        r = N - k - s
        out[name] = H.best_capped((H.rows_of(tree, x, F[r], None, False) for x in S), cap=8)
    return out


def main():
    mine = {(r["pattern"], r["s"]): r for r in json.load(open(HERE / "referee_carrier_caseii.json"))["rows"]}
    res = []
    for (idx, s), r in sorted(mine.items()):
        tree = WindowTree(THIRD[idx]["key"])
        v = direct_head_split(tree, 8, 3, s, 2)
        row = {"pattern": idx, "N": 8, "s": s, "routine_case_i": v["i"], "routine_case_ii": v["ii"],
               "sat_case_i": r["case_i_least_stem_bond"], "sat_case_ii": r["case_ii_least_stem_bond"],
               "agree": v["i"] == r["case_i_least_stem_bond"] and v["ii"] == r["case_ii_least_stem_bond"]}
        res.append(row)
        print(json.dumps(row), file=sys.stderr, flush=True)
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
