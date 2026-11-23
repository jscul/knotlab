"""The best reference table found, written as a pair of side tables with a cut of two (rank-4 factorisation), with exact re-verification:
hiding, score, largest change of a complete record, control value, best over all two-valued functions, and the linear-programming
residual of the four complete-record tables from the local polytope (positive: no common local explanation)."""
import json
import numpy as np
from fractions import Fraction
import common as c

M4 = np.zeros((8, 8), dtype=np.int64)
for x1 in (0, 1):
    for x2 in (0, 1):
        for x3 in (0, 1):
            for y1 in (0, 1):
                for y2 in (0, 1):
                    for y3 in (0, 1):
                        if x2 != x3 and y2 != y3 and (x1 ^ y1) == ((x1 ^ x3) & (y1 ^ y2)):
                            M4[x1 * 4 + x2 * 2 + x3, y1 * 4 + y2 * 2 + y3] += 1
cols = [1, 2, 5, 6]
TA = np.zeros((8, 4), dtype=np.int64); TB = np.zeros((8, 4), dtype=np.int64)
for k, y in enumerate(cols):
    TA[:, k] = M4[:, y]; TB[y, k] = 1
assert np.array_equal(TA @ TB.T, M4)
hA, hB = c.hidden_batch(M4[None])
v, combo, pat = c.exact_best(M4)
vc = c.exact_best(M4, control=True)[0]
gen, _ = c.best_general(M4)
lp, st = c.lp_local_residual(M4)
out = dict(M=M4.tolist(), TA=TA.tolist(), TB=TB.tolist(), hidden=bool(hA[0] and hB[0]), exact_score=str(v), score=float(v), combo_masks=[x for x in combo], pattern=pat,
           tv=str(c.exact_tv(M4)), control_exact=str(vc), best_general_functions=gen, lp_residual=lp, lp_status=int(st))
print(json.dumps(out))
print('TA (rows x = x1x2x3, columns = cut values 00,01,10,11):'); print(TA)
print('TB:'); print(TB)
# selector form of Alice's side: x2 != x3 forced; if x1 != x3 the cut bit s2 equals x2, else s1 equals x1
ok = True
for x in range(8):
    x1, x2, x3 = (x >> 2) & 1, (x >> 1) & 1, x & 1
    for cc in range(4):
        s1, s2 = cc >> 1, cc & 1
        want = (x2 != x3) and ((s2 == x2) if (x1 != x3) else (s1 == x1))
        ok &= (bool(TA[x, cc]) == bool(want))
print('selector form of TA confirmed:', ok)
json.dump(out, open(f'{c.ART}/reference_final.json', 'w'), indent=1)

tvk, pol = c.keyed_policy_change(M4)
print('keyed-setting policy on the reference table: largest change of the other observer complete record', tvk, float(tvk), pol)
out['keyed_policy_change'] = dict(tv=str(tvk), policy=pol)
json.dump(out, open(f'{c.ART}/reference_final.json', 'w'), indent=1)
