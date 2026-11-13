"""Exploratory: Class B on a d-letter alphabet. Knots {x, a x, b x} (a, b states or identity), degenerate dropped.
Words as tuples; first letter first. Fates at levels 1..N; interface = knots meeting two first-letter parts."""
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
def level(aut, st, n):
    words = list(itertools.product(range(d), repeat=n)); idx = {w: i for i, w in enumerate(words)}
    K = set()
    for x in words:
        t = [idx[act(aut, q, x)] for q in st]
        if len(set(t)) == 3: K.add(tuple(sorted(t)))
    return K, words
def alive(K):
    if not K: return True
    S = Minisat22()
    for a, b, c in K: S.add_clause([a+1, b+1, c+1]); S.add_clause([-a-1, -b-1, -c-1])
    r = S.solve(); S.delete(); return r
def all_auts():
    for pm in itertools.product(range(len(perms)), repeat=s):
        for dn in itertools.product(itertools.product(range(s), repeat=d), repeat=s):
            yield (tuple(perms[i] for i in pm), dn)
auts = list(all_auts()) if not SAMPLE else None
rng = random.Random(1)
if SAMPLE:
    auts = [(tuple(perms[rng.randrange(len(perms))] for _ in range(s)), tuple(tuple(rng.randrange(s) for _ in range(d)) for _ in range(s))) for _ in range(SAMPLE)]
choices = [(None, a, b) for a in range(s) for b in range(a+1, s)] + [(None, None, a) for a in []]
choices = [(None, a, b) for a, b in itertools.combinations([None] + list(range(s)), 2) if True]
choices = [(None,) + c if None not in c else c for c in []]  # placeholder
choices = []
opts = [None] + list(range(s))
for a, b in itertools.combinations(range(s), 2): choices.append((None, a, b))
if s >= 3:
    for t in itertools.combinations(range(s), 3): choices.append(t)
fates = collections.Counter(); prof = collections.Counter(); ex = {}
for aut in auts:
    for st in choices:
        life, nk = [], []
        for n in range(1, N+1):
            K, _ = level(aut, st, n); nk.append(len(K)); life.append(alive(K))
        if sum(nk) == 0: fates["no knots"] += 1; continue
        p = "".join("1" if v else "0" for v in life); prof[p] += 1
        if "0" in p and p not in ex: ex[p] = (aut, st)
        f = "alive" if "0" not in p else ("dies at once" if p.lstrip("1") == p and "1" not in p.split("0",1)[1:] and p[0]=="0" and set(p)=={"0"} else ("lives then dies" if p[-1]=="0" else "dies then lives"))
        fates[f] += 1
print("d,s,N =", d, s, N, dict(fates))
print("profiles:", prof.most_common(12))
for p, (aut, st) in list(ex.items())[:6]: print("example", p, aut, st)
