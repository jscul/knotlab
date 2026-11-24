"""Colour refinement and an exact isomorphism test for vertex-coloured simple graphs.

Ticket RING-IN-BALANCE-20261123-001C, written independently from the frozen text.

A graph is a list of integer colours and a list of adjacency lists, optionally with a level for
each vertex (the round, own time at birth or generation of a knot; None for a distinction). The
hash is the multiset of stable colours after colour refinement (1-dimensional Weisfeiler-Leman);
equal graphs always get equal hashes, so different hashes prove the graphs are not the same.

The exact test refines the disjoint union of the two graphs and then looks for a colour-
preserving bijection in two ways, and every bijection it returns is verified edge by edge, so a
returned mapping is a proof of isomorphism:
  1. graded (when levels are given): map the knots of the least level by a small search, then
     every other knot, level by level, to an unused knot of the same level and stable colour whose
     knots of lower level that it meets are the images of its own; then map the distinctions by
     their holders. (In a grown structure the knots of lower level a knot meets are its parents.)
  2. general: collapse twin vertices (same colour, same neighbours) and backtrack along a
     breadth-first order; if a step budget is exhausted, networkx's VF2 decides.
"""

import hashlib
from collections import Counter, defaultdict, deque


def stable_int(obj):
    """A process-independent 64-bit integer for a repr-able object (Python's str hash is salted)."""
    return int.from_bytes(hashlib.blake2b(repr(obj).encode(), digest_size=8).digest(), "big")


class Graph:
    __slots__ = ("col", "adj", "lev")

    def __init__(self, col, adj, lev=None):
        self.col = col
        self.adj = adj
        self.lev = lev

    @property
    def n(self):
        return len(self.col)


STATS = Counter()


def refine(col, adj):
    """Iterate colour refinement until the partition stops splitting.
    Colours are Python hashes of tuples of integers (deterministic across processes).
    Returns (stable colouring, number of iterations)."""
    cur = list(col)
    k = len(set(cur))
    it = 0
    n = len(cur)
    while True:
        nxt = [hash((cur[v], tuple(sorted([cur[u] for u in adj[v]])))) for v in range(n)]
        it += 1
        k2 = len(set(nxt))
        if k2 == k:
            return cur, it
        cur, k = nxt, k2


def graph_hash(g):
    cur, it = refine(g.col, g.adj)
    return stable_int((it, g.n, tuple(sorted(Counter(cur).items()))))


def _verify(g1, g2, m):
    n = g1.n
    if m is None or len(m) != n or sorted(m) != list(range(n)):
        return False
    set2 = [set(a) for a in g2.adj]
    for v in range(n):
        if g1.col[v] != g2.col[m[v]]:
            return False
        if len(g1.adj[v]) != len(g2.adj[m[v]]):
            return False
        for u in g1.adj[v]:
            if m[u] not in set2[m[v]]:
                return False
    return True


# ----------------------------------------------------------------------------- graded matcher
def _graded(g1, g2, c1, c2, max_start_maps=200):
    n = g1.n
    lv1, lv2 = g1.lev, g2.lev
    K1 = [v for v in range(n) if lv1[v] is not None]
    K2 = [v for v in range(n) if lv2[v] is not None]
    if sorted(lv1[v] for v in K1) != sorted(lv2[v] for v in K2):
        return None

    def meets(g, lv, a, same_level):
        out = Counter()
        for d in g.adj[a]:
            for b in g.adj[d]:
                if b != a and lv[b] is not None and ((lv[b] == lv[a]) if same_level else (lv[b] < lv[a])):
                    out[b] += 1
        return out

    low1 = {a: meets(g1, lv1, a, False) for a in K1}
    low2 = {b: meets(g2, lv2, b, False) for b in K2}
    L0 = min((lv1[a] for a in K1), default=None)
    S1 = sorted(a for a in K1 if lv1[a] == L0)
    S2 = sorted(b for b in K2 if lv2[b] == L0)
    sh1 = {a: meets(g1, lv1, a, True) for a in S1}
    sh2 = {b: meets(g2, lv2, b, True) for b in S2}
    rest1 = sorted((a for a in K1 if lv1[a] != L0), key=lambda a: (lv1[a], a))
    idx2 = defaultdict(list)
    for b in sorted(b for b in K2 if lv2[b] != L0):
        idx2[(lv2[b], c2[b], frozenset(low2[b].items()))].append(b)
    D1 = [d for d in range(n) if lv1[d] is None]
    grp2 = defaultdict(list)
    for d in range(n):
        if lv2[d] is None:
            grp2[(c2[d], frozenset(g2.adj[d]))].append(d)

    def extend(phi0):
        phi = dict(phi0)
        ptr = Counter()
        for a in rest1:
            img = frozenset((phi[x], k) for x, k in low1[a].items())
            key = (lv1[a], c1[a], img)
            lst = idx2.get(key)
            if lst is None or ptr[key] >= len(lst):
                return None
            phi[a] = lst[ptr[key]]
            ptr[key] += 1
        m = [-1] * n
        for a, b in phi.items():
            m[a] = b
        grp1 = defaultdict(list)
        for d in D1:
            grp1[(c1[d], frozenset(phi[a] for a in g1.adj[d]))].append(d)
        for key, lst in grp1.items():
            lst2 = grp2.get(key)
            if lst2 is None or len(lst2) != len(lst):
                return None
            for d, e in zip(lst, lst2):
                m[d] = e
        return m

    tried = 0
    phi = {}
    used = set()

    def start_maps(i):
        nonlocal tried
        if tried >= max_start_maps:
            return
        if i == len(S1):
            tried += 1
            yield dict(phi)
            return
        a = S1[i]
        for b in S2:
            if b in used or c2[b] != c1[a]:
                continue
            if any(sh1[a].get(x, 0) != sh2[b].get(phi[x], 0) for x in S1[:i]):
                continue
            phi[a] = b
            used.add(b)
            yield from start_maps(i + 1)
            used.discard(b)
            del phi[a]

    for phi0 in start_maps(0):
        m = extend(phi0)
        if m is not None and _verify(g1, g2, m):
            return m
    return None


# ----------------------------------------------------------------------------- general matcher
def _twin_classes(g, c):
    cls = defaultdict(list)
    for v in range(g.n):
        cls[(c[v], tuple(sorted(g.adj[v])))].append(v)
    classes = sorted(cls.values())
    rep = {}
    for i, vs in enumerate(classes):
        for v in vs:
            rep[v] = i
    adj = [sorted({rep[u] for u in g.adj[vs[0]]}) for vs in classes]
    col = [hash((c[vs[0]], len(vs))) for vs in classes]
    return classes, Graph(col, adj)


def _bfs_match(adj1, adj2, c1, c2, budget):
    n = len(adj1)
    set2 = [set(a) for a in adj2]
    freq = Counter(c1)
    by2 = defaultdict(list)
    for w in range(n):
        by2[c2[w]].append(w)
    order, par = [], [-1] * n
    seen = [False] * n
    for s in sorted(range(n), key=lambda v: (freq[c1[v]], v)):
        if seen[s]:
            continue
        seen[s] = True
        q = deque([s])
        while q:
            v = q.popleft()
            order.append(v)
            for u in sorted(adj1[v], key=lambda u: (freq[c1[u]], u)):
                if not seen[u]:
                    seen[u] = True
                    par[u] = v
                    q.append(u)
    m12 = [-1] * n
    m21 = [-1] * n
    cands = [None] * n
    ptr = [0] * n
    i = 0
    steps = 0
    while i < n:
        v = order[i]
        if cands[i] is None:
            p = par[v]
            cv = c1[v]
            if p < 0:
                cands[i] = [w for w in by2[cv] if m21[w] < 0]
            else:
                cands[i] = [w for w in adj2[m12[p]] if c2[w] == cv and m21[w] < 0]
            ptr[i] = 0
        else:
            w = m12[v]
            if w >= 0:
                m21[w] = -1
                m12[v] = -1
        placed = False
        lst = cands[i]
        while ptr[i] < len(lst):
            w = lst[ptr[i]]
            ptr[i] += 1
            steps += 1
            if m21[w] >= 0:
                continue
            ok = True
            k1 = 0
            for u in adj1[v]:
                mu = m12[u]
                if mu >= 0:
                    k1 += 1
                    if mu not in set2[w]:
                        ok = False
                        break
            if not ok:
                continue
            k2 = 0
            for x in adj2[w]:
                if m21[x] >= 0:
                    k2 += 1
            if k1 != k2:
                continue
            m12[v] = w
            m21[w] = v
            placed = True
            break
        if steps > budget:
            return "budget"
        if placed:
            i += 1
            if i < n:
                cands[i] = None
        else:
            cands[i] = None
            i -= 1
            if i < 0:
                return None
    return m12


def _general(g1, g2, c1, c2, budget):
    cl1, r1 = _twin_classes(g1, c1)
    cl2, r2 = _twin_classes(g2, c2)
    if r1.n != r2.n or Counter(r1.col) != Counter(r2.col):
        return None
    k = r1.n
    st, _ = refine(r1.col + r2.col, r1.adj + [[u + k for u in a] for a in r2.adj])
    rc1, rc2 = st[:k], st[k:]
    if Counter(rc1) != Counter(rc2):
        return None
    mr = _bfs_match(r1.adj, r2.adj, rc1, rc2, budget)
    if mr is None or mr == "budget":
        return mr
    m = [-1] * g1.n
    for i, j in enumerate(mr):
        for a, b in zip(cl1[i], cl2[j]):
            m[a] = b
    return m


def _nx_fallback(g1, g2):
    import networkx as nx
    from networkx.algorithms import isomorphism as nxi

    def to_nx(g):
        G = nx.Graph()
        for v in range(g.n):
            G.add_node(v, c=g.col[v])
        for v in range(g.n):
            for u in g.adj[v]:
                if u > v:
                    G.add_edge(v, u)
        return G

    GM = nxi.GraphMatcher(to_nx(g1), to_nx(g2), node_match=lambda a, b: a["c"] == b["c"])
    if not GM.is_isomorphic():
        return None
    return [GM.mapping[v] for v in range(g1.n)]


def isomorphism(g1, g2, budget=2_000_000):
    """Return a verified colour-preserving isomorphism g1 -> g2 as a list, or None."""
    n = g1.n
    if n != g2.n or sorted(g1.col) != sorted(g2.col):
        return None
    if sum(map(len, g1.adj)) != sum(map(len, g2.adj)):
        return None
    st, _ = refine(list(g1.col) + list(g2.col), list(g1.adj) + [[u + n for u in a] for a in g2.adj])
    c1, c2 = st[:n], st[n:]
    if Counter(c1) != Counter(c2):
        STATS["refinement_differs"] += 1
        return None
    if g1.lev is not None and g2.lev is not None:
        m = _graded(g1, g2, c1, c2)
        if m is not None:
            STATS["graded"] += 1
            return m
        STATS["graded_failed"] += 1
    m = _general(g1, g2, c1, c2, budget)
    if m == "budget":
        STATS["networkx"] += 1
        m = _nx_fallback(g1, g2)
    if m is None:
        STATS["general_none"] += 1
        return None
    if not _verify(g1, g2, m):
        raise AssertionError("matcher returned a non-isomorphism")
    STATS["general"] += 1
    return m


def same(g1, g2):
    """Hash first; exact test only when the hashes agree."""
    if graph_hash(g1) != graph_hash(g2):
        return False
    return isomorphism(g1, g2) is not None
