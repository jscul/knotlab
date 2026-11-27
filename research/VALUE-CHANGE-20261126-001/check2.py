"""check2.py: the advisor's second check (README.md, part A). On the closures of k-label subsets (k = 3: eight knots,
twelve distinctions; k = 4: sixteen knots, thirty-two), which ordinary growth makes from one knot of k places: is there a
choice of which unheld pairs of values fail to commute (pairs a common knot holds always commute) that makes every two
knots' laws commute and the sum of the knots' signs odd, when the choice must be unchanged by
    (a) permuting the labels (the symmetries that fix the founder: a rule in holders and descent), or
    (b) every symmetry of the holder pattern (permuting labels and complementing any set of them: a rule in holders alone),
or (c) with no restriction (the previous study's R3)? Exact, GF(2): variables are the orbits of unheld pairs."""
import sys, json, itertools
from pathlib import Path


def closure(k):
    V = range(1 << k)
    E = sorted({(a, a ^ (1 << b)) if a < a ^ (1 << b) else (a ^ (1 << b), a) for a in V for b in range(k)})
    return list(V), E


def solve(k, group):
    V, E = closure(k); idx = {e: i for i, e in enumerate(E)}
    unheld = [(i, j) for i, j in itertools.combinations(range(len(E)), 2) if not set(E[i]) & set(E[j])]
    def act(g, e):
        a, b = (g(e[0]), g(e[1])); return (min(a, b), max(a, b))
    orbit = {}; orbits = []
    for p in unheld:
        if p in orbit: continue
        O = set()
        for g in group:
            i, j = idx[act(g, E[p[0]])], idx[act(g, E[p[1]])]
            O.add((min(i, j), max(i, j)))
        for q in O: orbit[q] = len(orbits)
        orbits.append(O)
    star = {u: [i for i, e in enumerate(E) if u in e] for u in V}
    word = [i for u in V for i in star[u]]
    pos = {}
    for t, i in enumerate(word): pos.setdefault(i, []).append(t)
    inter = lambda i, j: (lambda a, b, x, y: a < x < b < y or x < a < y < b)(*pos[i], *pos[j])
    rows = []
    for u, v in itertools.combinations(V, 2):
        r = 0
        for (i, j) in unheld:
            c = (i in star[u] and j in star[v]) ^ (j in star[u] and i in star[v])
            if c: r ^= 1 << orbit[(i, j)]
        rows.append(r)
    cost = 0
    for (i, j) in unheld:
        if inter(i, j): cost ^= 1 << orbit[(i, j)]
    piv = {}
    for r in rows:
        while r:
            h = r.bit_length() - 1
            if h in piv: r ^= piv[h]
            else: piv[h] = r; break
    c = cost
    while c:
        h = c.bit_length() - 1
        if h not in piv: break
        c ^= piv[h]
    n_sol = 2 ** (len(orbits) - len(piv))
    return {'knots': len(V), 'distinctions': len(E), 'unheld pairs': len(unheld), 'orbits': len(orbits),
            'commuting choices': n_sol, 'an odd sign attainable': c != 0}


def perms(k):
    for p in itertools.permutations(range(k)):
        yield lambda a, p=p: sum(((a >> b) & 1) << p[b] for b in range(k))


def autos(k):
    for p in itertools.permutations(range(k)):
        for m in range(1 << k):
            yield lambda a, p=p, m=m: sum(((a >> b) & 1) << p[b] for b in range(k)) ^ m


if __name__ == '__main__':
    for k in (3, 4):
        for name, G in (('(a) label permutations', list(perms(k))), ('(b) every symmetry of the holders', list(autos(k))),
                        ('(c) no restriction', [lambda a: a])):
            print(json.dumps({'labels': k, 'choices unchanged by': name, **solve(k, G)}), flush=True)
