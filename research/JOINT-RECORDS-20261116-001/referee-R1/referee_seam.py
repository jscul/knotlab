"""JOINT-RECORDS-R1, the referee's own census (fresh code): complement-closed relations on s places, how many are fixed by their
k-place shadows, which three-place ones fail, the knot test on those, and NAE face-colourings of the three Platonic triangulations
by brute force and by perfect matchings of the dual."""
import itertools, json
def tuples(s): return list(itertools.product((0, 1), repeat=s))
def comp_closed(s):
    T = tuples(s); orbits = []
    seen = set()
    for t in T:
        if t in seen: continue
        c = tuple(1 - x for x in t); seen |= {t, c}; orbits.append((t, c))
    for mask in range(1 << len(orbits)):
        yield frozenset(x for i, o in enumerate(orbits) if mask >> i & 1 for x in o)
def shadow_closure(R, s, k):
    T = tuples(s); subs = list(itertools.combinations(range(s), k))
    proj = {S: {tuple(t[i] for i in S) for t in R} for S in subs}
    return frozenset(t for t in T if all(tuple(t[i] for i in S) in proj[S] for S in subs))
def is_knot3(R):  # K1-K3 on three places: nonempty, constrained, every pair free
    full = {(0, 0), (0, 1), (1, 0), (1, 1)}
    return bool(R) and len(R) < 8 and all({(t[i], t[j]) for t in R} == full for i, j in ((0, 1), (0, 2), (1, 2)))
out = {}
for s in (1, 2, 3, 4):
    rels = list(comp_closed(s))
    row = {'complement_closed': len(rels)}
    for k in range(1, s):
        row[f'fixed_by_{k}_place'] = sum(shadow_closure(R, s, k) == R for R in rels)
    if s == 3:
        fails = [R for R in rels if shadow_closure(R, 3, 2) != R]
        row['two_place_failures'] = [sorted(''.join(map(str, t)) for t in set(tuples(3)) - R) for R in fails]
        row['failures_all_knots'] = all(is_knot3(R) for R in fails)
    if s == 4:
        nae4 = frozenset(t for t in tuples(4) if 0 < sum(t) < 4)
        row['nae4_fixed_by_3'] = shadow_closure(nae4, 4, 3) == nae4
        row['nae4_fixed_by_2'] = shadow_closure(nae4, 4, 2) == nae4
    out[f's={s}'] = row
# Platonic triangulations: faces as vertex triples
TET = [(0, 1, 2), (0, 1, 3), (0, 2, 3), (1, 2, 3)]
OCT = [(a, b, c) for a in (0, 1) for b in (2, 3) for c in (4, 5)]
def icosahedron():
    import math
    phi = (1 + 5 ** 0.5) / 2
    V = [(0, s1, s2 * phi) for s1 in (-1, 1) for s2 in (-1, 1)] + [(s1, s2 * phi, 0) for s1 in (-1, 1) for s2 in (-1, 1)] + \
        [(s2 * phi, 0, s1) for s1 in (-1, 1) for s2 in (-1, 1)]
    d = lambda p, q: sum((a - b) ** 2 for a, b in zip(p, q))
    E = {(i, j) for i in range(12) for j in range(i + 1, 12) if abs(d(V[i], V[j]) - 4) < 1e-9}
    F = [t for t in itertools.combinations(range(12), 3) if all(p in E for p in itertools.combinations(t, 2))]
    return F
ICO = icosahedron()
def nae_count(F, n):
    return sum(all(0 < c[a] + c[b] + c[x] < 3 for a, b, x in F) for c in itertools.product((0, 1), repeat=n))
def pm_dual(F):
    # dual: faces adjacent when they share an edge; count perfect matchings by brute recursion
    adj = {i: [j for j in range(len(F)) if j != i and len(set(F[i]) & set(F[j])) == 2] for i in range(len(F))}
    def count(free):
        if not free: return 1
        i = min(free); tot = 0
        for j in adj[i]:
            if j in free: tot += count(free - {i, j})
        return tot
    return count(frozenset(range(len(F))))
out['platonic'] = {name: dict(faces=len(F), nae=nae_count(F, n), twice_pm_dual=2 * pm_dual(F))
                   for name, F, n in (('tetrahedron', TET, 4), ('octahedron', OCT, 6), ('icosahedron', ICO, 12))}
print(json.dumps(out, indent=1))
