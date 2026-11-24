"""P1: the full enumeration gives 20/9 with both complete records hidden exactly; the totals of the four finished structures.

Recomputes the four joint tables of complete records by full enumeration (2^28 assignments each, every knot on every
assignment), checks them against the tables saved by item_g.py, and evaluates the score (best over parity outcomes of each
observer's four record bits and the four sign patterns, exact), the hiding of both complete records (exact) and the largest
change of a complete record."""
import json
from fractions import Fraction
import numpy as np
import common as c

S = c.build(1)
J = {}
for sa in (0, 1):
    for sb in (0, 1):
        J[sa, sb], nv, nk = c.full_joint(S, sa, sb)
saved = c.load_joint(f'{c.ART}/joint_k1_full.json')
same = all(np.array_equal(J[ab], saved[ab]) for ab in J)
ev = c.evaluate_tables(J, 1)
held = Fraction(ev['score']) == Fraction(20, 9) and ev['hidden_alice'] and ev['hidden_bob']
print(f'recomputed tables equal the saved ones: {same}')
print(f'totals (allowed words of each finished structure, settings ab): {ev["totals"]}')
print(f'score {ev["score"]} = {ev["score_float"]:.9f}; outcome choice {ev["outcome_choice"]}')
print(f'hidden: Alice {ev["hidden_alice"]}, Bob {ev["hidden_bob"]}; largest change of a complete record {ev["largest_change"]}')
print('P1:', 'HELD' if held else 'FAILED')
ev.update(tables_equal_saved=same, P1='held' if held else 'failed', joint_tables={f'{a}{b}': J[a, b].tolist() for (a, b) in J})
json.dump(ev, open(f'{c.ART}/item_p1.json', 'w'), indent=1)
