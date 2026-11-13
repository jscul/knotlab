"""Exploratory (before any registered run): structure of the 7 parity-alternating patterns at levels <= 12 (already read by the
census). Dead levels: a minimal dead core by deletion; alive levels: the model's form."""
import json, gzip, sys, itertools
import numpy as np
from pysat.solvers import Cadical195
sys.path.insert(0, 'proofs/ADDR-KNOTS-20261113-001B/ADDR-KNOTS-20261113-001B-P001_growing_interfaces')
from check import act
A = 'artifacts/ADDR-KNOTS-20261113-001A/ADDR-KNOTS-20261113-001A-E001_addressed_census/keys.jsonl.gz'
recs = [json.loads(l) for l in gzip.open(A, 'rt')]
prof = lambda r: ''.join({1: '1', 0: '0', None: '?'}[v] for v in r['verdict_n'])
alt = [r for r in recs if r['return'] and prof(r)[4:] in ('10101010', '01010101')]
def pattern(key, n):
    s, sw, d0, d1, pls = key
    W = [()] + [(q,) for q in range(s)] + [(q, t) for q in range(s) for t in range(s)]
    ks = []
    for pl in pls:
        T = np.stack([act((sw, d0, d1), W[i], n) for i in pl], 1)
        ok = (T[:, 0] != T[:, 1]) & (T[:, 1] != T[:, 2]) & (T[:, 0] != T[:, 2])
        ks.append(np.sort(T[ok], 1))
    return np.unique(np.concatenate(ks), axis=0)
def core(K):
    S = Cadical195(); sel = list(range(1, len(K) + 1)); off = 1 << 20
    for i, (a, b, c) in enumerate(K.tolist()):
        g = off + i
        S.add_clause([-g, a + 1, b + 1, c + 1]); S.add_clause([-g, -a - 1, -b - 1, -c - 1])
    assum = [off + i for i in range(len(K))]
    assert not S.solve(assumptions=assum)
    cur = sorted(x - off for x in S.get_core())
    while True:  # refine by repeated cores
        assert not S.solve(assumptions=[off + j for j in cur])
        nxt = sorted(x - off for x in S.get_core())
        if len(nxt) >= len(cur): break
        cur = nxt
    i = 0
    while len(cur) <= 400 and i < len(cur):  # deletion-based minimisation on small cores only
        trial = cur[:i] + cur[i + 1:]
        if S.solve(assumptions=[off + j for j in trial]): i += 1
        else: cur = sorted(x - off for x in S.get_core())
    S.delete(); return K[cur]
for r in alt:
    s, sw, d0, d1, pls = r['key']
    print(flush=True); print('==', prof(r), 's', s, 'sw', sw, 'd0', d0, 'd1', d1, 'placements', pls, 'rel', r['rel_class'])
    for n in range(3, 10):
        K = pattern(r['key'], n)
        if r['verdict_n'][n - 1] == 0:
            C = core(K); V = sorted(set(C.ravel().tolist()))
            print('  level', n, 'dead; minimal core', len(C), 'knots on', len(V), 'addresses', [format(v, f'0{n}b') for v in V][:14])
