"""Nesting by substitution (research/SUBST-NEST-20261112-001/preregistration.md, ticket A).

Law: not-all-equal (NAE) on three distinctions. A pattern is (n, knots), knots triples of distinctions 0..n-1.
Block substitution: a block B (a pattern on m distinctions) and a binding set T of ordered triples over 0..m-1. sigma(P): each
distinction v of P becomes a copy of B, distinctions (v, p); B's knots inside every copy; each knot (x, y, z) of P becomes the knots
((x, p), (y, q), (z, r)) for (p, q, r) in T. The canonical binding sets (closed under reordering and the block's symmetries): the
diagonal {(p, p, p)}; the block's own knots in every order; every ordered triple of distinct places.
Knot substitution: a motif M with three corners; level k+1 replaces every knot of level k by a copy of M glued at its corners."""
import itertools

from pysat.solvers import Solver


def nae_clauses(knots, base=1):
    cl = []
    for (a, b, c) in knots:
        cl.append([a + base, b + base, c + base])
        cl.append([-(a + base), -(b + base), -(c + base)])
    return cl


def solutions(n, knots):
    return [s for s in itertools.product((0, 1), repeat=n) if all(not (s[a] == s[b] == s[c]) for (a, b, c) in knots)]


def canonical(n, knots):
    return min(tuple(sorted(tuple(sorted(p[x] for x in e)) for e in knots)) for p in itertools.permutations(range(n)))


def connected(n, knots):
    if n == 1:
        return True
    comp = {0}
    grow = True
    while grow:
        grow = False
        for e in knots:
            if comp & set(e) and not set(e) <= comp:
                comp |= set(e)
                grow = True
    return comp == set(range(n))


def blocks(max_m=5, extra_m=6, extra_knots=5):
    """living connected blocks: every pattern on 3..max_m distinctions, and on extra_m distinctions with up to extra_knots knots, one per
    isomorphism class, that allows a state"""
    found = {}
    for m in range(3, extra_m + 1):
        triples = list(itertools.combinations(range(m), 3))
        kmax = len(triples) if m <= max_m else extra_knots
        perms = list(itertools.permutations(range(m)))
        for k in range(1, kmax + 1):
            for E in itertools.combinations(triples, k):
                if set(itertools.chain(*E)) != set(range(m)) or not connected(m, E):
                    continue
                key = min(tuple(sorted(tuple(sorted(p[x] for x in e)) for e in E)) for p in perms)
                if (m, key) in found:
                    continue
                if not solutions(m, key):
                    continue
                found[(m, key)] = True
    return [(m, [tuple(e) for e in key]) for (m, key) in sorted(found)]


def binding_sets(m, knots):
    return {
        "diagonal": [(p, p, p) for p in range(m)],
        "the block's knots": sorted({perm for e in knots for perm in itertools.permutations(e)}),
        "all distinct triples": list(itertools.permutations(range(m), 3)),
    }


def substitute(P, B, T):
    """sigma(P) as a pattern, with the address (v, p) of each distinction"""
    n, Pk = P
    m, Bk = B
    idx = {(v, p): v * m + p for v in range(n) for p in range(m)}
    knots = [(idx[(v, a)], idx[(v, b)], idx[(v, c)]) for v in range(n) for (a, b, c) in Bk]
    knots += [(idx[(x, p)], idx[(y, q)], idx[(z, r)]) for (x, y, z) in Pk for (p, q, r) in T]
    return (n * m, knots), idx


def template(B, T):
    """the template: points are the block's solutions; a knot (t1, t2, t3) when NAE(t1[p], t2[q], t3[r]) for every (p, q, r) in T"""
    m, Bk = B
    S = solutions(m, Bk)
    K = [(i, j, k) for i, a in enumerate(S) for j, b in enumerate(S) for k, c in enumerate(S)
         if all(not (a[p] == b[q] == c[r]) for (p, q, r) in T)]
    return S, K


def star_colouring(B):
    """a place p and values 0/1 elsewhere such that every knot of B holds both a 0 and a 1 (the twisted mirror lift)"""
    m, Bk = B
    out = []
    for p in range(m):
        others = [q for q in range(m) if q != p]
        for vals in itertools.product((0, 1), repeat=m - 1):
            col = dict(zip(others, vals))
            if all({col[x] for x in e if x != p} == {0, 1} for e in Bk):
                out.append(p)
                break
    return out


def chain(n):
    """n knots in a row, each sharing one distinction with the next: (2n + 1) distinctions"""
    return (2 * n + 1, [(2 * i, 2 * i + 1, 2 * i + 2) for i in range(n)])


def gasket(level):
    knots = [(0, 1, 2)]
    n, A, B, C = 3, 0, 1, 2
    for _ in range(level):
        def relabel(base_knots, base_n, fixed, offset):
            mp, nxt = {}, offset
            for v in range(base_n):
                if v in fixed:
                    mp[v] = fixed[v]
                else:
                    mp[v] = nxt
                    nxt += 1
            return [tuple(mp[x] for x in kn) for kn in base_knots], mp, nxt
        k1, m1, top = relabel(knots, n, {A: B}, n)
        k2, m2, top = relabel(knots, n, {A: C, B: m1[C]}, top)
        knots = knots + k1 + k2
        A, B, C = A, m1[B], m2[C]
        n = top
    return (n, knots)


def tie_class(P, root):
    n, knots = P
    cl = nae_clauses(knots)
    r = root + 1
    with Solver(name="cadical153", bootstrap_with=cl) as s:
        if not s.solve():
            return None
        m0 = s.get_model()
        val = lambda m, v: m[v - 1] > 0
        rel = {v: val(m0, r) ^ val(m0, v) for v in range(1, n + 1)}
        cand = set(rel) - {r}
        tied = {r}
        while cand:
            y = min(cand)
            if s.solve(assumptions=[r if val(m0, r) else -r, -y if val(m0, y) else y]):
                m = s.get_model()
                cand -= {v for v in cand if (val(m, r) ^ val(m, v)) != rel[v]}
            else:
                cand.discard(y)
                tied.add(y)
        return {v - 1 for v in tied}


def distances(P, root):
    n, knots = P
    adj = {v: set() for v in range(n)}
    for t in knots:
        for a in t:
            adj[a] |= set(t) - {a}
    dist, frontier = {root: 0}, [root]
    while frontier:
        nxt = []
        for a in frontier:
            for b in adj[a]:
                if b not in dist:
                    dist[b] = dist[a] + 1
                    nxt.append(b)
        frontier = nxt
    return dist


def count_states(P, cap=100000):
    n, knots = P
    c = 0
    with Solver(name="cadical153", bootstrap_with=nae_clauses(knots)) as s:
        while s.solve():
            m = s.get_model()
            c += 1
            if c > cap:
                return None
            s.add_clause([(-(i + 1) if m[i] > 0 else (i + 1)) for i in range(n)])
    return c


def iterate(P, B, T, k):
    """sigma^k(P) with the full address (v, p_1, ..., p_k) of each distinction"""
    cur, addr = P, {v: (v,) for v in range(P[0])}
    for _ in range(k):
        nxt, idx = substitute(cur, B, T)
        addr = {i: addr[v] + (p,) for (v, p), i in idx.items()}
        cur = nxt
    return cur, addr


def motif_flow(M, corners=(0, 1, 2)):
    """the corner relation after one knot substitution: Phi_M(NAE), the corners' values that extend to a state of M"""
    n, knots = M
    return sorted({tuple(s[c] for c in corners) for s in solutions(n, knots)})


def motif_level(M, level):
    """level k of knot substitution by M (corners 0, 1, 2 of M), as a pattern; level 0 is one knot"""
    n0, Mk = M
    P = (3, [(0, 1, 2)])
    for _ in range(level):
        n, knots = P
        new = []
        nxt = n
        for (a, b, c) in knots:
            mp = {0: a, 1: b, 2: c}
            for v in range(3, n0):
                mp[v] = nxt
                nxt += 1
            new += [tuple(mp[x] for x in kn) for kn in Mk]
        P = (nxt, new)
    return P


FANO = [(0, 1, 2), (0, 3, 4), (0, 5, 6), (1, 3, 5), (1, 4, 6), (2, 3, 6), (2, 4, 5)]
MOTIFS = {
    "three knots sharing corners (gasket)": (6, [(0, 3, 4), (3, 1, 5), (4, 5, 2)]),
    # the Fano plane less the knot on 0, 1, 2: its corners are the removed knot's three distinctions
    "Fano plane less one knot": (7, [e for e in FANO if e != (0, 1, 2)]),
}
