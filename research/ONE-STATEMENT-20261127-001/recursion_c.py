"""recursion_c.py OUT.json: part (c), the advisor's recursion test.  ONE-STATEMENT-20261127-001.
The tree presentation of the nine facts read as a first-layer start: four knots, the root (R1 R2 R3) and T_i
(R_i p_i q_i), so the R_i are shared and the p_i, q_i loose (places 3, 3, 3, 3; loose 0, 2, 2, 2).  Grown by ordinary
parity growth for three rounds: the places of every birth.  Against it, what growth does to the nine facts on the
witness: each round each family's fact moves to a new carrier (the fresh distinctions of its newest births), one
two-place relation (old carrier = new carrier, modulo the laws) per family per round (THIRD-LAYER referee R1, Lemma 3;
SELECTED-KNOTS-20261127-001's advisor, S1).  The prediction: they differ, since ordinary growth never makes a two-place
birth."""
import sys, json, collections
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
for d in ('BUILT-BINDING-20261126-001', 'THIRD-LAYER-20261126-001'): sys.path.insert(0, str(ROOT / 'research' / d))
import repro as RP
R1, R2, R3, p1, q1, p2, q2, p3, q3 = range(9)
S = ((R1, R2, R3), (R1, p1, q1), (R2, p2, q2), (R3, p3, q3))
st = S; out = {'start': [list(k) for k in S], 'rounds': []}
for t in range(1, 4):
    nxt, status, births = RP.forbid.grown(st, 'parity', 'ordinary')
    if status != 'funded': out['rounds'].append({'round': t, 'end': status}); break
    out['rounds'].append({'round': t, 'births': len(births), 'places of births': dict(collections.Counter(len(b['inputs']) + b['f'] for b in births)),
                          'two-place births': sum(1 for b in births if len(b['inputs']) + b['f'] == 2)})
    st = nxt
out['second layer, per round'] = 'six two-place relations (each family fact equals its next carrier), no birth of three or more places'
json.dump(out, open(sys.argv[1], 'w'), indent=1); print(json.dumps(out, indent=1))
