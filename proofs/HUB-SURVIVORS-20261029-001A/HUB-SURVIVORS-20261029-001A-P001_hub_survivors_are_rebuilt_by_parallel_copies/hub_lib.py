"""Library for HUB-SURVIVORS-20261029-001A-P001: the 34 three-bit knots, their 16 classes up to coordinate order, and hub
gadgets with three legs (legs in one copy each, hidden variables in at least two distinct copies, no variable twice in a copy,
connected), enumerated with the lowest unfilled copy first and deduplicated up to relabelling of copies."""
import itertools, sys, time
from collections import Counter, defaultdict
import numpy as np
cube = list(itertools.product((0, 1), repeat=3))
def knots():
    res = []
    def grow(start, E):
        if E: res.append(frozenset(s for s in cube if s not in E))
        for i in range(start, 8):
            s = cube[i]
            if all(sum(a != b for a, b in zip(s, e)) >= 2 for e in E): grow(i + 1, E + [s])
    grow(0, []); return res
def permute(K, p): return frozenset(tuple(s[p[i]] for i in range(3)) for s in K)
def placements(K): return sorted({permute(K, p) for p in itertools.permutations(range(3))}, key=sorted)
K34 = knots()
classes = {}
for K in K34: classes.setdefault(min(tuple(sorted(P)) for P in placements(K)), K)
reps = list(classes.values())
L = "abcdefghijklmnopqrstuvwxyz"
def T(K):
    t = np.zeros((2, 2, 2), dtype=np.int64)
    for s in K: t[s] = 1
    return t
def gadgets(m, k=3):
    subsets = sorted(c for r in range(2, m + 1) for c in itertools.combinations(range(m), r))
    out = {}
    for legs in itertools.combinations_with_replacement(range(m), k):
        if legs[0] != 0: continue
        deg0 = [0] * m
        for c in legs: deg0[c] += 1
        if max(deg0) > (2 if m > 1 else 3): continue
        def rec(start, chosen, deg):
            if all(d == 3 for d in deg):
                adj = defaultdict(set)
                for S in chosen:
                    for a in S:
                        for b in S: adj[a].add(b)
                seen, st = {0}, [0]
                while st:
                    u = st.pop()
                    for w in adj[u]:
                        if w not in seen: seen.add(w); st.append(w)
                if len(seen) == m:
                    key = min((tuple(sorted(p[c] for c in legs)), tuple(sorted(tuple(sorted(p[c] for c in S)) for S in chosen)))
                              for p in itertools.permutations(range(m)))
                    out.setdefault(key, (legs, tuple(chosen)))
                return
            first = next(c for c in range(m) if deg[c] < 3)
            for j in range(start, len(subsets)):
                S = subsets[j]
                if S[0] != first: continue
                if all(deg[c] < 3 for c in S):
                    for c in S: deg[c] += 1
                    chosen.append(S); rec(j, chosen, deg); chosen.pop()
                    for c in S: deg[c] -= 1
        rec(0, [], deg0[:])
    return list(out.values())
def spec(m, legs, hid):
    slots = [[] for _ in range(m)]
    for i, c in enumerate(legs): slots[c].append(L[i])
    for j, S in enumerate(hid):
        for c in S: slots[c].append(L[3 + j])
    return ",".join("".join(s) for s in slots) + "->abc"
