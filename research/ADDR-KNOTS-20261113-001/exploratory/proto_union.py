"""Exploratory: all triples of {identity} + states as knots at once (density up to C(s+1,3) per distinction)."""
import itertools, sys, collections, random
from pysat.solvers import Minisat22
d = int(sys.argv[1]); s = int(sys.argv[2]); N = int(sys.argv[3]); SAMPLE = int(sys.argv[4]) if len(sys.argv) > 4 else 0
perms = list(itertools.permutations(range(d)))
def act(aut, q, x):
    if q is None: return x
    pm, dn = aut; y = []
    for b in x:
        y.append(pm[q][b]); q = dn[q][b]
    return tuple(y)
def level(aut, triples, n):
    words = list(itertools.product(range(d), repeat=n)); idx = {w: i for i, w in enumerate(words)}
    K = set()
    for x in words:
        im = {q: idx[act(aut, q, x)] for q in [None] + list(range(s))}
        for st in triples:
            t = [im[q] for q in st]
            if len(set(t)) == 3: K.add(tuple(sorted(t)))
    return K
def alive(K):
    if not K: return True
    S = Minisat22()
    for a, b, c in K: S.add_clause([a+1, b+1, c+1]); S.add_clause([-a-1, -b-1, -c-1])
    r = S.solve(); S.delete(); return r
rng = random.Random(1)
if SAMPLE:
    auts = [(tuple(perms[rng.randrange(len(perms))] for _ in range(s)), tuple(tuple(rng.randrange(s) for _ in range(d)) for _ in range(s))) for _ in range(SAMPLE)]
else:
    auts = [(tuple(perms[i] for i in pm), dn) for pm in itertools.product(range(len(perms)), repeat=s) for dn in itertools.product(itertools.product(range(s), repeat=d), repeat=s)]
triples = list(itertools.combinations([None] + list(range(s)), 3))
prof = collections.Counter(); dens = collections.defaultdict(list); ex = {}
for aut in auts:
    life, nk = [], []
    for n in range(1, N+1):
        K = level(aut, triples, n); nk.append(len(K)); life.append(alive(K))
    p = "".join("1" if v else "0" for v in life) if sum(nk) else "none"
    prof[p] += 1; dens[p].append(nk[-1] / d**N)
    if p not in ex: ex[p] = aut
print("d,s,N =", d, s, N, "triples", len(triples), "automata", len(auts))
for p, c in prof.most_common(15): print(p, c, "mean knots/distinction at N: %.2f" % (sum(dens[p]) / len(dens[p])), ex[p])
