"""Library for EXACT-TOWERS-20261029-001A-P001: the 34 three-bit knots in 16 classes, hub gadgets with three legs (legs in one copy
each, hidden variables in at least two distinct copies, no variable twice in a copy, connected; enumeration as in
HUB-SURVIVORS-20261029-001A-P001), their count tensors, solution sets, leg distances, redundancy, frozen and tied hidden variables,
and structural automorphisms (signed permutations of the variables fixing the leg set and mapping copies to copies)."""
import itertools
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
def excl(K): return tuple(sorted(set(cube) - K))
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
def slots_of(m, legs, hid):
    slots = [[] for _ in range(m)]
    for i, c in enumerate(legs): slots[c].append(i)
    for j, S in enumerate(hid):
        for c in S: slots[c].append(3 + j)
    return [tuple(s) for s in slots]
def copies_of(m, legs, hid, choice, PL):
    return [(s, PL[choice[c]]) for c, s in enumerate(slots_of(m, legs, hid))]
def leg_dist(n, cops):
    adj = [set() for _ in range(n)]
    for vs, Q in cops:
        for u in vs:
            for v in vs:
                if u != v: adj[u].add(v)
    def bfs(src):
        d = {src: 0}; q = [src]
        for u in q:
            for w in adj[u]:
                if w not in d: d[w] = d[u] + 1; q.append(w)
        return d
    d0, d1 = bfs(0), bfs(1)
    return (d0[1], d0[2], d1[2])
def norm(vs, Q):
    order = sorted(range(3), key=lambda i: vs[i])
    return (tuple(vs[i] for i in order), frozenset(tuple(s[i] for i in order) for s in Q))
def redundant(cops):
    """two copies impose the identical constraint on the same variables"""
    c = Counter(norm(vs, Q) for vs, Q in cops)
    return max(c.values()) > 1
def solutions(n, cops):
    X = np.array(list(itertools.product((0, 1), repeat=n)), dtype=np.int8)
    ok = np.ones(len(X), dtype=bool)
    for vs, Q in cops:
        tab = np.zeros(8, dtype=bool)
        for s in Q: tab[s[0] * 4 + s[1] * 2 + s[2]] = True
        ok &= tab[X[:, vs[0]] * 4 + X[:, vs[1]] * 2 + X[:, vs[2]]]
    return X[ok]
def frozen_and_tied(n, S):
    """hidden variables constant on all solutions; pairs of distinct variables (at least one hidden) always equal or always opposite"""
    frozen = [v for v in range(3, n) if len(set(S[:, v].tolist())) == 1]
    tied = []
    for u in range(n):
        for v in range(max(u + 1, 3), n):
            if u in frozen or v in frozen: continue
            d = set((S[:, u] ^ S[:, v]).tolist())
            if len(d) == 1: tied.append((u, v, "equal" if d == {0} else "opposite"))
    return frozen, tied
def struct_aut(n, cops):
    """signed permutations (pi, f) of the variables with pi fixing the leg set {0,1,2}, mapping the multiset of constraints to itself"""
    key = Counter(norm(vs, Q) for vs, Q in cops)
    sets = Counter(tuple(sorted(vs)) for vs, Q in cops)
    deg = Counter(x for vs, Q in cops for x in vs)
    out = []
    for pl in itertools.permutations(range(3)):
        for ph in itertools.permutations(range(3, n)):
            pi = list(pl) + list(ph)
            if any(deg[x] != deg[pi[x]] for x in range(n)): continue
            if Counter(tuple(sorted(pi[x] for x in vs)) for vs, Q in cops) != sets: continue
            # flips: backtrack variable by variable, checking each copy once all its variables are assigned
            f = [None] * n
            def ok_copy(vs, Q):
                img = norm(tuple(pi[x] for x in vs), frozenset(tuple(s[i] ^ f[vs[i]] for i in range(3)) for s in Q))
                return img in key
            by_last = defaultdict(list)
            for vs, Q in cops: by_last[max(vs)].append((vs, Q))
            def rec(v):
                if v == n:
                    img = Counter(norm(tuple(pi[x] for x in vs), frozenset(tuple(s[i] ^ f[vs[i]] for i in range(3)) for s in Q))
                                  for vs, Q in cops)
                    if img == key: out.append((tuple(pi), tuple(f)))
                    return
                for b in (0, 1):
                    f[v] = b
                    if all(ok_copy(vs, Q) for vs, Q in by_last[v]): rec(v + 1)
                f[v] = None
            rec(0)
    return out
def act(t, pi, f):
    u = [0, 0, 0]
    for i in range(3): u[pi[i]] = t[i] ^ f[i]
    return tuple(u)
def autK(K):
    return [(p, f) for p in itertools.permutations(range(3)) for f in itertools.product((0, 1), repeat=3)
            if frozenset(act(s, p, f) for s in K) == K]
def has_pendant(n, cops):
    """some set of at most two variables whose deletion leaves a group of copies (connected through the remaining variables) in
    which no copy holds a leg"""
    for size in (1, 2):
        for S in itertools.combinations(range(n), size):
            S = set(S)
            comp = list(range(len(cops)))
            def find(x):
                while comp[x] != x:
                    comp[x] = comp[comp[x]]; x = comp[x]
                return x
            owner = {}
            for i, (vs, Q) in enumerate(cops):
                for v in vs:
                    if v in S: continue
                    if v in owner: comp[find(i)] = find(owner[v])
                    else: owner[v] = i
            groups = defaultdict(list)
            for i in range(len(cops)): groups[find(i)].append(i)
            for g in groups.values():
                if not any(v < 3 for i in g for v in cops[i][0]): return True
    return False
