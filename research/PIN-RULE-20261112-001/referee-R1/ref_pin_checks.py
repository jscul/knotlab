#!/usr/bin/env python3
"""Referee PIN-RULE-R1: two small checks with the referee's own code (ref_subst.py of the SUBST-NEST referee folder, the referee's).

1. Section 3's "pins never vary" under every block-triple set closed under reordering, including the diagonal: tested on a pattern
   P that holds an opposite tie of its own (the Fano plane less the knot {2, 4, 5}, which forces 2 = 4 = 5, plus the knot {2, 4, 7},
   which then forces 7 != 2), with the block K4 (all four knots on four distinctions; no spare distinction).
2. N7 / rigid: the number of states of sigma(P) for K4 with its knots on the chain of 4 knots (expected 6, the block's states)."""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "SUBST-NEST-20261112-001" / "referee-R1"))
import ref_subst as S  # noqa: E402
from pysat.solvers import Glucose4  # noqa: E402

K4 = (4, [(0, 1, 2), (0, 1, 3), (0, 2, 3), (1, 2, 3)])
FANO_LESS = [(0, 1, 2), (0, 3, 4), (0, 5, 6), (1, 3, 5), (1, 4, 6), (2, 3, 6)]
P = (8, FANO_LESS + [(2, 4, 7)])
out = {}
relP = S.tie_relation(*P)
out["P's own tie (2, 7)"] = relP.get((2, 7))
for tname in ("diagonal", "the block's knots"):
    T = S.triple_sets(*K4)[tname]
    Q = S.substitute(P, K4, T)
    rel = S.tie_relation(*Q)
    m = K4[0]
    out[tname] = {"lives": rel is not None,
                  "relation of (2, p) and (7, p) for p = 0..3": [rel.get((2 * m + p, 7 * m + p)) for p in range(m)]}


def count(n, knots, cap=1000):
    cl = [c for a, b, c3 in knots for c in ([a + 1, b + 1, c3 + 1], [-(a + 1), -(b + 1), -(c3 + 1)])]
    k = 0
    with Glucose4(bootstrap_with=cl) as s:
        while s.solve() and k <= cap:
            mdl = s.get_model()
            k += 1
            s.add_clause([-l for l in mdl[:n]])
    return k


Q = S.substitute(S.chain(4), K4, S.triple_sets(*K4)["the block's knots"])
out["states of sigma(chain of 4) with K4 and its knots"] = count(*Q)
(HERE / "result_pin_checks.json").write_text(json.dumps(out, indent=1) + "\n")
print(out)
