"""Thread's independent recheck of the 48 returning descriptions with Glucose4 (not Codex's code; action from the proof note's check.py)."""
import json, glob, itertools, sys
import numpy as np
from pysat.solvers import Glucose4
sys.path.insert(0, 'proofs/ADDR-KNOTS-20261113-001B/ADDR-KNOTS-20261113-001B-P001_growing_interfaces')
from check import act
C = 'experiments/ADDR-KNOTS-20261113-001A/ADDR-KNOTS-20261113-001A-E001_addressed_census/codex/full'
recs = [json.loads(l) for f in glob.glob(C + '/keys/*.jsonl') for l in open(f)]
ret = [r for r in recs if r['return']]
out = []
for r in ret:
    s, sw, d0, d1, pls = r['key']
    W = [()] + [(q,) for q in range(s)] + [(q, t) for q in range(s) for t in range(s)]
    aut = (sw, d0, d1); mine = []
    for n in range(1, 13):
        ks = []
        for pl in pls:
            T = np.stack([act(aut, W[i], n) for i in pl], 1)
            ok = (T[:, 0] != T[:, 1]) & (T[:, 1] != T[:, 2]) & (T[:, 0] != T[:, 2])
            ks.append(np.sort(T[ok], 1))
        K = np.unique(np.concatenate(ks), axis=0)
        assert len(K) == r['knots_n'][n - 1], (r['key_id'], n, len(K), r['knots_n'][n - 1])
        if len(K) == 0: mine.append(1); continue
        S = Glucose4()
        for a, b, c in K.tolist(): S.add_clause([a + 1, b + 1, c + 1]); S.add_clause([-a - 1, -b - 1, -c - 1])
        S.add_clause([int(K.min()) + 1]); S.conf_budget(1_000_000); v = S.solve_limited(); S.delete()
        mine.append(None if v is None else int(v))
    agree = all(a is None or b is None or a == b for a, b in zip(mine, r['verdict_n']))
    out.append(dict(key_id=r["key_id"], codex=r["verdict_n"], glucose=mine, agree=agree)); print(len(out), agree, flush=True)
print(sum(o['agree'] for o in out), 'of', len(out), 'agree;', sum(None in o['glucose'] for o in out), 'with a Glucose null')
json.dump(out, open('research/ADDR-KNOTS-20261113-001/returns_recheck.json', 'w'), indent=0)
