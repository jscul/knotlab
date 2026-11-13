"""Exploratory search for automatic states (a DFA with k <= 3 states reading the address from its first letter; the value is the
output bit of the state reached) at the alive levels 4..10 of the 7 alternating patterns."""
import json, gzip, sys, itertools
import numpy as np
sys.path.insert(0, 'experiments/LEVEL-RETURN-20261113-001A/LEVEL-RETURN-20261113-001A-E001_certified_levels')
from certify import pattern
A = 'artifacts/ADDR-KNOTS-20261113-001A/ADDR-KNOTS-20261113-001A-E001_addressed_census/keys.jsonl.gz'
recs = [json.loads(l) for l in gzip.open(A, 'rt')]
prof = lambda r: ''.join({1: '1', 0: '0', None: '?'}[v] for v in r['verdict_n'])
alt = [r for r in recs if r['return'] and prof(r)[4:] in ('10101010', '01010101')]
def run_dfa(delta, n):
    X = np.arange(1 << n); st = np.zeros(1 << n, dtype=np.int64)
    for i in range(n - 1, -1, -1):
        b = (X >> i) & 1; st = delta[st, b]
    return st
for idx, r in enumerate(alt):
    p = prof(r); lev = [n for n in range(4, 11) if p[n - 1] == '1']
    Ks = {n: pattern(r['key'], n) for n in lev}
    found = []
    for k in (1, 2, 3):
        for trans in itertools.product(range(k), repeat=2 * k):
            delta = np.array(trans).reshape(k, 2)
            ends = {n: run_dfa(delta, n) for n in lev}
            for outs in itertools.product((0, 1), repeat=k):
                o = np.array(outs)
                if o.min() == o.max(): continue
                if all(np.all((lambda V: V.min(1) != V.max(1))(o[ends[n]][Ks[n]])) for n in lev):
                    found.append((k, trans, outs))
        if found: break
    print(idx + 1, p, 'alive levels', lev, 'automatic states found:', len(found), found[:3], flush=True)
