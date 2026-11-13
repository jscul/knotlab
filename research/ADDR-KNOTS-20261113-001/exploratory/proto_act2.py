"""Exploratory (not registered): dense addressed knots, binary, s = 3, all four triples of {identity, q0, q1, q2};
fates at levels 1..N with numpy actions and Minisat; activity class from the automaton (count of words reaching nontrivial states)."""
import itertools, sys, collections, numpy as np
from multiprocessing import Pool
from pysat.solvers import Minisat22
N = int(sys.argv[1]); s = 3


def act_all(aut, q, n):
    sw, d0, d1 = (np.array(v) for v in aut)
    x = np.arange(1 << n, dtype=np.int64); y = np.zeros_like(x); st = np.full(x.shape, q)
    for i in range(n - 1, -1, -1):
        b = (x >> i) & 1; y = (y << 1) | (b ^ sw[st]); st = np.where(b == 0, d0[st], d1[st])
    return y


def trivial(aut):
    sw, d0, d1 = aut; out = []
    for q in range(s):
        seen, stck = set(), [q]
        while stck:
            u = stck.pop()
            if u not in seen:
                seen.add(u); stck += [d0[u], d1[u]]
        out.append(all(sw[u] == 0 for u in seen))
    return out


def activity(aut, n=16):
    sw, d0, d1 = aut; tv = trivial(aut); m = [0] * n
    for q0 in range(s):
        c = [0] * s; c[q0] = 1
        for i in range(n):
            c2 = [0] * s
            for u in range(s):
                c2[d0[u]] += c[u]; c2[d1[u]] += c[u]
            c = c2; m[i] = max(m[i], sum(c[u] for u in range(s) if not tv[u]))
    if m[-1] == 0: return "finitary"
    if m[-1] == m[-4]: return "bounded"
    if m[-1] >= 1.5 * m[-2]: return "exponential"
    return "polynomial"


def alive(K):
    if len(K) == 0: return True
    S = Minisat22()
    for a, b, c in K.tolist():
        S.add_clause([a + 1, b + 1, c + 1]); S.add_clause([-a - 1, -b - 1, -c - 1])
    r = S.solve(); S.delete(); return r


def one(aut):
    life, nk, dens = [], 0, 0.0
    for n in range(1, N + 1):
        im = [np.arange(1 << n)] + [act_all(aut, q, n) for q in range(s)]
        ks = []
        for a, b, c in itertools.combinations(range(4), 3):
            T = np.stack([im[a], im[b], im[c]], 1)
            ok = (T[:, 0] != T[:, 1]) & (T[:, 1] != T[:, 2]) & (T[:, 0] != T[:, 2])
            ks.append(np.sort(T[ok], 1))
        K = np.unique(np.concatenate(ks), axis=0)
        nk += len(K); dens = len(K) / (1 << n); life.append(alive(K))
        if not life[-1]: break
    a = activity(aut)
    if nk == 0: return a, "no knots", aut, 0.0
    if all(life): return a, "alive to %d" % N, aut, dens
    return a, "first death %d" % len(life), aut, dens


if __name__ == "__main__":
    auts = [(sw, d0, d1) for sw in itertools.product((0, 1), repeat=s)
            for d0 in itertools.product(range(s), repeat=s) for d1 in itertools.product(range(s), repeat=s)]
    with Pool(8) as P:
        res = P.map(one, auts, chunksize=20)
    tab = collections.Counter((a, f) for a, f, _, _ in res)
    for k in sorted(tab): print(k, tab[k])
    print("density at last level by (activity, alive/dead):")
    dd = collections.defaultdict(list)
    for a, f, _, de in res:
        if f != "no knots": dd[(a, f.startswith("alive"))].append(de)
    for k in sorted(dd): print(k, len(dd[k]), "mean %.2f" % np.mean(dd[k]))
    late = sorted([(int(f.split()[-1]), a, aut) for a, f, aut, _ in res if f.startswith("first") and int(f.split()[-1]) >= 7], reverse=True)
    print("latest first deaths:", late[:10])
