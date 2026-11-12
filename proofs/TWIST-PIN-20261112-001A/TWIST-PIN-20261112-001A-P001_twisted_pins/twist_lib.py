"""Twisted pins (research/TWIST-PIN-20261112-001/preregistration.md, ticket A).

Distinction substitution as in SUBST-NEST-20261112-001 (block B, the block's knots in every order between copies), now with a twist:
member v of knot e of P carries a symmetry g_(e,v) of B (a permutation of B's distinctions keeping its knots), and the knot binds
NAE((x, g_(e,x)(p')), (y, g_(e,y)(q')), (z, g_(e,z)(r'))) for every ordering (p', q', r') of a knot of B. All g the identity: the
untwisted substitution."""
import itertools
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "proofs/SUBST-NEST-20261112-001A/SUBST-NEST-20261112-001A-P001_block_substitution"))
import subst_lib as S  # noqa: E402


def automorphisms(B):
    m, E = B
    Es = {frozenset(e) for e in E}
    return [p for p in itertools.permutations(range(m)) if {frozenset(p[x] for x in e) for e in E} == Es]


def compose(a, b):
    """(a o b)(x) = a(b(x))"""
    return tuple(a[b[x]] for x in range(len(b)))


def inverse(a):
    out = [0] * len(a)
    for i, x in enumerate(a):
        out[x] = i
    return tuple(out)


def conjugacy_classes(G):
    seen, reps = set(), []
    for g in sorted(G):
        if g in seen:
            continue
        cls = {compose(compose(h, g), inverse(h)) for h in G}
        seen |= cls
        reps.append(g)
    return reps


def orbits(h, items):
    items = set(items)
    out = []
    while items:
        x = min(items)
        orb = {x}
        y = h[x]
        while y != x:
            orb.add(y)
            y = h[y]
        out.append(sorted(orb & set(range(len(h)))))
        items -= orb
    return out


def twisted(P, B, twist):
    """sigma(P) with twists: twist maps (knot index, slot 0/1/2) to a symmetry (default identity)"""
    n, Pk = P
    m, Bk = B
    idx = {(v, p): v * m + p for v in range(n) for p in range(m)}
    ident = tuple(range(m))
    T = sorted({perm for e in Bk for perm in itertools.permutations(e)})
    knots = [(idx[(v, a)], idx[(v, b)], idx[(v, c)]) for v in range(n) for (a, b, c) in Bk]
    for ei, (x, y, z) in enumerate(Pk):
        gx, gy, gz = (twist.get((ei, s), ident) for s in range(3))
        knots += [(idx[(x, gx[p])], idx[(y, gy[q])], idx[(z, gz[r])]) for (p, q, r) in T]
    return (n * m, knots), idx


def two_sharing_two():
    return (4, [(0, 1, 2), (0, 1, 3)])


def closed_chain(k):
    n = 2 * k
    return (n, [(2 * i, 2 * i + 1, (2 * i + 2) % n) for i in range(k)])


def two_cycles():
    """two closed chains of 3 knots sharing distinction 0"""
    a = [(0, 1, 2), (2, 3, 4), (4, 5, 0)]
    b = [(0, 6, 7), (7, 8, 9), (9, 10, 0)]
    return (11, a + b)


def ties_in_copy(Q, idx, v, p, m):
    tied = S.tie_class(Q, idx[(v, p)])
    if tied is None:
        return None
    inv = {i: a for a, i in idx.items()}
    return sorted(inv[t][1] for t in tied if inv[t][0] == v), sum(1 for t in tied if inv[t][0] != v)


def lives(Q):
    from pysat.solvers import Solver
    with Solver(name="cadical153", bootstrap_with=S.nae_clauses(Q[1])) as s:
        return s.solve()


def ring(n):
    """the one-shift base on a ring of n distinctions: knots (i, i+1, i+2) mod n"""
    return (n, [(i, (i + 1) % n, (i + 2) % n) for i in range(n)])


def knot_relation_ok(B):
    """the advisor's form of the untwisted binding: (a, b, c) are allowed between three copies exactly when every knot of B holds at
    most one place where a, b, c are not unanimous"""
    m, E = B
    T = sorted({perm for e in E for perm in itertools.permutations(e)})
    sts = S.solutions(m, E)
    for a in sts:
        for b in sts:
            for c in sts:
                ok = all(not (a[x] == b[y] == c[z]) for (x, y, z) in T)
                D = {p for p in range(m) if not (a[p] == b[p] == c[p])}
                pred = all(len(D & set(e)) <= 1 for e in E)
                if ok != pred:
                    return False
    return True


def state_graph_distance(B, h):
    """least distance, over states t, from t to t o h in the graph on B's states joining t, t' when the places where they differ meet
    every knot of B at most once (the advisor's exact condition for one twisted cycle of n knots: lives iff this is at most n)"""
    m, E = B
    sts = S.solutions(m, E)
    index = {s: i for i, s in enumerate(sts)}
    adj = {i: [] for i in range(len(sts))}
    for i, a in enumerate(sts):
        for j, b in enumerate(sts):
            D = {p for p in range(m) if a[p] != b[p]}
            if all(len(D & set(e)) <= 1 for e in E):
                adj[i].append(j)
    best = None
    for t in sts:
        th = tuple(t[h[x]] for x in range(m))
        if th not in index:
            continue
        src, dst = index[t], index[th]
        dist = {src: 0}
        frontier = [src]
        while frontier and dst not in dist:
            nxt = []
            for u in frontier:
                for w in adj[u]:
                    if w not in dist:
                        dist[w] = dist[u] + 1
                        nxt.append(w)
            frontier = nxt
        if dst in dist:
            best = dist[dst] if best is None else min(best, dist[dst])
    return best


def generated(gens, m):
    G = {tuple(range(m))}
    frontier = list(G)
    while frontier:
        g = frontier.pop()
        for h in gens:
            k = compose(h, g)
            if k not in G:
                G.add(k)
                frontier.append(k)
    return G


def quotient_prediction(B, H, N):
    """states of B constant on the H-orbits of N (the pinned layer as a state of B/H, restricted to N): whether any exists, and the
    ties they force among B's distinctions (pairs equal or unequal in every such state)"""
    m, E = B
    sts = [s for s in S.solutions(m, E) if all(s[q] == s[g[q]] for g in H for q in N)]
    full = [s for s in S.solutions(m, E) if all(s[q] == s[g[q]] for g in H for q in range(m))]
    ties = {}
    for p in range(m):
        ties[p] = sorted(q for q in range(m) if sts and len({s[p] ^ s[q] for s in sts}) == 1)
    return {"some state constant on the orbits of N": bool(sts), "some state fixed by H": bool(full), "ties": ties}


def classify(B, H, N, own_ties):
    """balanced (H trivial), N-balanced (H fixes N up to B's own ties), N-twisted (some h moves q in N off its own tie class)"""
    m = B[0]
    if all(g == tuple(range(m)) for g in H):
        return "balanced"
    for g in H:
        for q in N:
            if g[q] != q and g[q] not in own_ties[q]:
                return "N-twisted"
    return "N-balanced"


def holonomy_group(P, B, twist, root=0):
    """the group generated at the root copy by the holonomies of all closed walks of copies through shared knots: moving from copy v to
    copy w through knot e carries v's distinction q to w's distinction g_(e,w)(g_(e,v)^-1(q))"""
    n, Pk = P
    m = B[0]
    ident = tuple(range(m))
    steps = []
    for ei, members in enumerate(Pk):
        gs = [twist.get((ei, s), ident) for s in range(3)]
        for i in range(3):
            for j in range(3):
                if i != j:
                    steps.append((members[i], members[j], compose(gs[j], inverse(gs[i]))))
    tau = {root: ident}
    frontier = [root]
    while frontier:
        v = frontier.pop()
        for (a, b, T) in steps:
            if a == v and b not in tau:
                tau[b] = compose(T, tau[v])
                frontier.append(b)
    gens = set()
    for (a, b, T) in steps:
        if a in tau and b in tau:
            h = compose(inverse(tau[b]), compose(T, tau[a]))
            if h != ident:
                gens.add(h)
    return generated(gens, m)
