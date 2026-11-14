"""Exploratory (route A, step 2): on #2's reduced pattern at even levels, does fixing f(A) = f(A xor e2) = c get refuted by unit
propagation, or by failed-literal probing of depth 1 or 2? (Rigidity needs f(A) != f(A xor e2) for every A.)"""
import sys, random
import numpy as np
sys.path.insert(0, 'experiments/LEVEL-RETURN-20261113-001A/LEVEL-RETURN-20261113-001A-E001_certified_levels')
from certify import pattern
TWO = [3, [1, 0, 1], [0, 2, 2], [2, 1, 1], [[0, 8, 10], [1, 8, 12], [1, 9, 10]]]
def build(n):
    K = pattern(TWO, n); X = np.arange(1 << n); par = np.array([bin(int(t)).count('1') & 1 for t in X])
    V = par[K]; K = K[V.min(1) != V.max(1)] if n % 2 == 0 else K
    occ = [[] for _ in range(1 << n)]
    for i, (a, b, c) in enumerate(K.tolist()):
        for v in (a, b, c): occ[v].append(i)
    return K.tolist(), occ
def up(K, occ, assign):
    val = dict(assign); queue = list(assign)
    while queue:
        v = queue.pop()
        for i in occ[v]:
            k = K[i]; vals = [val.get(u) for u in k]
            un = [u for u, x in zip(k, vals) if x is None]; set_ = [x for x in vals if x is not None]
            if not un and len(set(set_)) == 1: return None  # all equal: conflict
            if len(un) == 1 and len(set_) == 2 and set_[0] == set_[1]:
                u = un[0]; val[u] = 1 - set_[0]; queue.append(u)
    return val
def refuted(K, occ, assign, depth):
    v = up(K, occ, assign)
    if v is None: return True
    if depth == 0: return False
    free = [u for u in range(len(occ)) if u not in v and occ[u]]
    for u in free:
        if all(refuted(K, occ, {**v, u: c}, depth - 1) for c in (0, 1)): return True
    return False
rng = random.Random(1)
for n in (6, 8, 10):
    K, occ = build(n); N = 1 << n
    for depth in (0, 1):
        tested = 0; ref = 0
        for A in rng.sample(range(N), min(12, N)):
            B = A ^ (1 << (n - 2))  # flip letter 2 (first letter is the most significant bit)
            if not occ[A] or not occ[B]: continue
            tested += 1
            ref += all(refuted(K, occ, {A: c, B: c}, depth) for c in (0, 1))
        print(n, 'depth', depth, 'refuted', ref, 'of', tested, flush=True)

if __name__ == '__main__' and len(sys.argv) > 1:
    pass
