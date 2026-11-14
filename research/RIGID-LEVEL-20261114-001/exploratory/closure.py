"""Exploratory: for #2 (reduced at even levels, full at odd), with g = f XOR parity each knot becomes 'its same-parity pair equal
implies its apex equal to them'. Rigidity follows if (i) the apex-closure of every knot's pair is everything and (ii) the pair graph is
not bipartite. Check both at small levels."""
import sys, collections
import numpy as np
sys.path.insert(0, 'experiments/LEVEL-RETURN-20261113-001A/LEVEL-RETURN-20261113-001A-E001_certified_levels')
from certify import pattern
TWO = [3, [1, 0, 1], [0, 2, 2], [2, 1, 1], [[0, 8, 10], [1, 8, 12], [1, 9, 10]]]
for n in range(5, 13):
    K = pattern(TWO, n); X = np.arange(1 << n); par = np.array([bin(int(t)).count('1') & 1 for t in X])
    V = par[K]; K = K[V.min(1) != V.max(1)]
    trip = []
    for a, b, c in K.tolist():
        pa, pb, pc = par[a], par[b], par[c]
        if pa == pb: trip.append((a, b, c))
        elif pa == pc: trip.append((a, c, b))
        else: trip.append((b, c, a))
    byp = collections.defaultdict(list)
    for u, v, w in trip: byp[u].append((v, w)); byp[v].append((u, w))
    def closure(u, v):
        C = {u, v}; st = [u, v]
        while st:
            x = st.pop()
            for y, w in byp[x]:
                if y in C and w not in C: C.add(w); st.append(w)
        return len(C)
    sizes = [closure(u, v) for u, v, w in trip]
    # pair graph bipartite?
    adj = collections.defaultdict(list)
    for u, v, w in trip: adj[u].append(v); adj[v].append(u)
    col = {}; bip = True
    for s0 in adj:
        if s0 in col: continue
        col[s0] = 0; st = [s0]
        while st and bip:
            x = st.pop()
            for y in adj[x]:
                if y not in col: col[y] = 1 - col[x]; st.append(y)
                elif col[y] == col[x]: bip = False; break
    used = len(set(K.ravel().tolist()))
    print(n, 'knots', len(trip), 'addresses', used, 'closure of a pair: min', min(sizes), 'max', max(sizes),
          'share full %.2f' % (sum(s == used for s in sizes) / len(sizes)), 'pair graph bipartite', bip, flush=True)
