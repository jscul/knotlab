#!/usr/bin/env python3
"""Referee BASES-WITHIN-R1: L9 on every lag assignment of the alternation (lags (0, s, t), s, t in {0, 1}, for every outer pattern),
shifts.c's verdict against signed not-all-equal by brute force over the outer distinctions; and L8 (no outer pattern without a closed
chain ends under any lags) read off result_exhaustive.json. Writes result_signs.json."""
import itertools
import json
from pathlib import Path

import ref_lib as R
import ref_shifts as S

HERE = Path(__file__).resolve().parent
alt = R.harmonies()[0]
assert alt["orbits"] == ["01"]
pats = R.outer_patterns() + [(7, R.FANO[:-1]), (7, R.FANO)]
total = agree = 0
for n, E in pats:
    A = [tuple((0, s, t) for (s, t) in c) for c in itertools.product([(0, 0), (0, 1), (1, 0), (1, 1)], repeat=len(E))]
    fast = S.listed(alt, n, E, A)
    for a, f in zip(A, fast):
        signed = any(all(R.nae(x[p] ^ sp, x[q] ^ sq, x[r] ^ sr) for (p, q, r), (sp, sq, sr) in zip(E, a))
                     for x in itertools.product((0, 1), repeat=n))
        total += 1
        agree += signed == f


def acyclic(n, E):
    parent = {}

    def find(x):
        while parent.setdefault(x, x) != x:
            x = parent[x]
        return x
    for k, e in enumerate(E):
        for x in e:
            a, b = find(("k", k)), find(("d", x))
            if a == b:
                return False
            parent[a] = b
    return True


ex = json.loads((HERE / "result_exhaustive.json").read_text())
l8 = [(r["i"], p["outer"]) for r in ex["rows"] for p in r["patterns"] if acyclic(p["outer"][0], [tuple(e) for e in p["outer"][1]]) and p["dead"]]
res = {"alternation assignments": total, "agree with signed NAE": agree,
       "outer patterns without a closed chain": sum(acyclic(n, E) for n, E in pats[:-1]),
       "L8 violations (an acyclic pattern ended under some lags)": l8}
(HERE / "result_signs.json").write_text(json.dumps(res, indent=1) + "\n")
print(res)
