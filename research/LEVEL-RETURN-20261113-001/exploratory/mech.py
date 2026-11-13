"""Exploratory: for the 7 alternating patterns, (L) which linear states <a,x>+c are states at the alive levels; (D) which
embeddings x -> v.x (v of length 1 or 2 prefixed) send the level-n pattern into the level-(n+|v|) pattern."""
import json, gzip, sys
import numpy as np
sys.path.insert(0, 'proofs/ADDR-KNOTS-20261113-001B/ADDR-KNOTS-20261113-001B-P001_growing_interfaces')
sys.path.insert(0, 'research/LEVEL-RETURN-20261113-001/exploratory')
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
def popc(v): return np.array([bin(int(t)).count('1') & 1 for t in v])
for r in alt:
    p = prof(r); print('==', p, r['key'][1:4])
    for n in range(3, 11):
        K = pattern(r['key'], n)
        if p[n - 1] == '1' and n <= 10:
            X = np.arange(1 << n)
            good = []
            for a in range(1, 1 << n):
                val = popc(X & a)
                v = val[K]
                if np.all(v.min(1) != v.max(1)): good.append(format(a, f'0{n}b'))
            print('  level', n, 'alive; linear states <a,x>:', len(good), good[:6])
    # embeddings x -> v.x
    for n in range(3, 9):
        K = set(map(tuple, pattern(r['key'], n).tolist()))
        for L in (1, 2):
            K2 = set(map(tuple, pattern(r['key'], n + L).tolist()))
            for v in range(1 << L):
                img = {tuple(sorted(v * (1 << n) + t for t in k)) for k in K}
                if img <= K2: print('  embed level', n, '->', n + L, 'by prefix', format(v, f'0{L}b'))
