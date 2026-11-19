"""Pilot: the eddy rule on random arrangements of 6 to 12 knots; every start with a cycle of blocks is grown, plus a control."""
import json, sys, time
from collections import Counter
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import eddy as E, sampler as S  # noqa: E402
N = int(sys.argv[1]); M = int(sys.argv[2]); seed0 = int(sys.argv[3])
rows, tab = [], Counter()
t0 = time.time()
for s in range(seed0, seed0 + M):
    sz, e = S.sample(N, s)
    v = E.eddy(sz, e)
    vh = E.eddy(sz, e, skip_hyper=False)
    L = E.loops(sz, e)
    kr = S.knot_cycle_rank(N, e)
    rec = {'seed': s, 'rule': str(v), 'rule_with_h': str(vh), 'knot_rank': kr,
           'rank_h': L['rank_with_hyperedges'] if L else None, 'rank': L['rank_without'] if L else None}
    if L and (L['rank_with_hyperedges'] > 0 or s % 50 == 0):
        cls, c = E.growth_class(sz, e, rounds=36, maxj=200000, tmax=60)
        rec['growth'] = cls; rec['counts'] = c[:20]
        tab[(rec['rule'], rec['rule_with_h'], cls)] += 1
    rows.append(rec)
print(N, M, round(time.time() - t0, 1), dict(tab))
json.dump(rows, open(HERE / f'random_{N}_{seed0}.json', 'w'))
