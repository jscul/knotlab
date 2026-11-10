"""Supplement to B4 and S3 for the atom, written after the freeze (disclosed deviation, 2026-11-10).

trunc_check.py's identity-of-indiscernibles tree query for the atom is a pigeonhole instance (53 inner names into 28 views at
L = 4, 161 at L = 5), which the solver did not finish; both runs were stopped at 05:12 UTC. This script reruns the atom's other
queries with trunc_check's own functions (fixed_board, free_board without identity of indiscernibles), and decides the two identity
queries without the solver: 'any' by the collapse state (every identity distinction true, every value 0), checked against the law
and the identity clauses, and 'tree' by the count of allowed views against inner names.

Usage: supplement_atom.py FIXED_L FREE_L OUT.json
"""
import itertools
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import trunc_check as tc  # noqa: E402

fixed_L, free_L, out = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
t0 = time.time()
r = {}
for board in list(tc.BOARDS) + ['Sch(<c>)']:
    sat, pairs = tc.fixed_board('atom', fixed_L, board)
    r[board] = {'allowed': sat, 'pairs': pairs}
r['free'] = tc.free_board('atom', free_L)
names = tc.ball(free_L)
inner = [u for u in names if len(u) <= free_L - 1]
views = [v for v in itertools.product((0, 1), repeat=5) if tc.LAWS['atom'](*v)]
law_ok = all(tuple([0] * 5) not in tc.FORBIDDEN['atom'] for _ in inner)
r['free_ioi1'] = {'any': law_ok, 'tree': not (len(views) < len(inner)), 'allowed_views': len(views), 'inner_names': len(inner),
                  'how': 'any by the collapse state; tree impossible by the count'}
r['seconds'] = round(time.time() - t0, 1)
json.dump(r, open(out, 'w'), indent=1, sort_keys=True)
print(json.dumps(r))
