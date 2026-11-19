"""PARENT-RULE-20261119-001B library: the properties, peeling, exact tables of small arrangements, and the states test.

An arrangement is a list of junctions, each a frozenset of distinctions (ints); a distinction is held by one junction (loose) or
two (shared).  A junction is live when it holds a loose distinction.
- backed pairs (P1): every two junctions a live junction meets also both meet a junction other than it;
- backed by a closed junction (P1+): that third junction can be chosen holding no loose distinction;
- live junctions never meet (P2);
- peeling: remove the live junctions, so that the distinctions they took become loose again and their own loose ones vanish; the
  peel depth is the number of successive peels at which P1+ and P2 hold (a closed arrangement has no live junction: depth 0).
Exact tables of arrangements with at most 15 vertices (junctions and the outside vertex) come from every bond: a cut between a
connected vertex set and its connected complement, the outside vertex a plain vertex.  Pairs in no common bond read 'none'.
"""
from collections import defaultdict
from itertools import combinations

import networkx as nx
from networkx.algorithms import isomorphism


def owners(stars):
    own = defaultdict(list)
    for j, s in enumerate(stars):
        for b in s:
            own[b].append(j)
    return own


def neighbours(stars, own=None):
    own = own or owners(stars)
    nb = [set() for _ in stars]
    for b, js in own.items():
        if len(js) == 2:
            nb[js[0]].add(js[1])
            nb[js[1]].add(js[0])
    return nb


def live_set(stars, own=None):
    own = own or owners(stars)
    return sorted({js[0] for js in own.values() if len(js) == 1})


def max_shared(stars):
    c = defaultdict(int)
    for js in owners(stars).values():
        if len(js) == 2:
            c[tuple(sorted(js))] += 1
    return max(c.values(), default=0)


def props(stars):
    """Violation counts: P1 (backed pairs), P1+ (backed by a closed junction), P2 (live junctions never meet); and the stratum."""
    own = owners(stars)
    nb = neighbours(stars, own)
    live = live_set(stars, own)
    lv = set(live)
    p1 = p1p = p2 = 0
    for j in live:
        for u, v in combinations(sorted(nb[j]), 2):
            third = (nb[u] & nb[v]) - {j}
            if not third:
                p1 += 1
            if not (third - lv):
                p1p += 1
    for u, v in combinations(live, 2):
        if v in nb[u]:
            p2 += 1
    if not live:
        stratum = 'closed'
    elif all(len(nb[j]) <= 1 for j in live):
        stratum = 'pendant-only'
    else:
        stratum = 'backed'
    return {'P1': p1, 'P1+': p1p, 'P2': p2, 'stratum': stratum}


def peel(stars):
    """The arrangement with the live junctions removed (their own loose distinctions vanish, the ones they took become loose)."""
    live = set(live_set(stars))
    return [s for j, s in enumerate(stars) if j not in live]


def depth(stars, cap=64):
    d = 0
    cur = stars
    while d < cap:
        if not live_set(cur):
            return d
        p = props(cur)
        if p['P1+'] or p['P2']:
            return d
        d += 1
        cur = peel(cur)
        if not cur:
            return d
    return d


# ---- exact tables by bonds (small arrangements) ----

def graph_of(stars):
    """Vertices 0..n-1 junctions, n the outside vertex when some distinction is loose; edge list (distinction, u, v)."""
    own = owners(stars)
    n = len(stars)
    has_o = any(len(js) == 1 for js in own.values())
    edges = []
    for b in sorted(own):
        js = own[b]
        edges.append((b, js[0], js[1] if len(js) == 2 else n))
    return (n + 1 if has_o else n), edges


def bonds(stars):
    nv, edges = graph_of(stars)
    adj = [0] * nv
    for _, u, v in edges:
        adj[u] |= 1 << v
        adj[v] |= 1 << u
    full = (1 << nv) - 1

    def connected(mask):
        if not mask:
            return False
        start = mask & -mask
        seen, frontier = start, start
        while frontier:
            nxt = 0
            m = frontier
            while m:
                low = m & -m
                nxt |= adj[low.bit_length() - 1]
                m ^= low
            nxt &= mask & ~seen
            seen |= nxt
            frontier = nxt
        return seen == mask

    out = []
    # every cut once: subsets containing vertex 0
    for rest in range(0, 1 << (nv - 1)):
        S = (rest << 1) | 1
        if S == full:
            continue
        if connected(S) and connected(full & ~S):
            cut = [b for b, u, v in edges if ((S >> u) & 1) != ((S >> v) & 1)]
            out.append(cut)
    return out


def table(stars):
    labels = sorted(owners(stars))
    best = {}
    for cut in bonds(stars):
        k = len(cut) - 1
        for p in combinations(sorted(cut), 2):
            if p not in best or best[p] > k:
                best[p] = k
    return {p: best.get(p, 'none') for p in combinations(labels, 2)}, labels


def row_key(tab, labels):
    rows = defaultdict(list)
    for (a, b), d in tab.items():
        rows[a].append(str(d))
        rows[b].append(str(d))
    return (len(labels), tuple(sorted(tuple(sorted(r)) for r in rows.values())))


def coloured(tab, labels):
    g = nx.Graph()
    g.add_nodes_from(labels)
    for (a, b), d in tab.items():
        g.add_edge(a, b, d=str(d))
    hs = nx.weisfeiler_lehman_subgraph_hashes(g, edge_attr='d', iterations=3)
    for v in g.nodes:
        g.nodes[v]['k'] = tuple(hs[v])
    return g


def iso(g1, g2):
    if sorted(d['k'] for _, d in g1.nodes(data=True)) != sorted(d['k'] for _, d in g2.nodes(data=True)):
        return False
    return isomorphism.GraphMatcher(g1, g2, node_match=lambda a, b: a['k'] == b['k'],
                                    edge_match=lambda a, b: a.get('d') == b.get('d')).is_isomorphic()


def incidence(stars):
    own = owners(stars)
    g = nx.Graph()
    for j, s in enumerate(stars):
        g.add_node(('j', j), k='j')
        for b in s:
            g.add_node(('b', b), k='loose' if len(own[b]) == 1 else 'shared')
            g.add_edge(('j', j), ('b', b))
    return g


def arrangement_iso(a, b):
    ga, gb = incidence(a), incidence(b)
    if ga.number_of_nodes() != gb.number_of_nodes() or ga.number_of_edges() != gb.number_of_edges():
        return False
    return isomorphism.GraphMatcher(ga, gb, node_match=lambda x, y: x['k'] == y['k']).is_isomorphic()


# ---- states ----

def rank(words):
    basis = []
    for w in words:
        for bvec in basis:
            w = min(w, w ^ bvec)
        if w:
            basis.append(w)
    return len(basis)


def junction_graph(stars):
    own = owners(stars)
    g = nx.Graph()
    g.add_nodes_from(range(len(stars)))
    for b, js in own.items():
        u, v = (js[0], 'o') if len(js) == 1 else tuple(js)
        if g.has_edge(u, v):
            g[u][v]['m'] += 1
        else:
            g.add_edge(u, v, m=1)
    return g


def quotient(stars, tab):
    own = owners(stars)
    cls = defaultdict(list)
    for b in sorted(own):
        cls[tuple(sorted(own[b]))].append(b)
    keys = sorted(cls)

    def t(x, y):
        return tab[(x, y)] if (x, y) in tab else tab[(y, x)]
    g = nx.Graph()
    for k in keys:
        inner = str(t(cls[k][0], cls[k][1])) if len(cls[k]) > 1 else '-'
        g.add_node(k, s=(len(cls[k]), inner))
    for i, k in enumerate(keys):
        for k2 in keys[i + 1:]:
            g.add_edge(k, k2, d=str(t(cls[k][0], cls[k2][0])))
    hs = nx.weisfeiler_lehman_subgraph_hashes(g, node_attr='s', edge_attr='d', iterations=3)
    for k in keys:
        g.nodes[k]['k'] = (g.nodes[k]['s'], tuple(hs[k]))
    return g, cls


def carriers(a, b, ta, tb, cap=5000):
    """Iterate over (renaming, carries) for the table isomorphisms a -> b taken on twin classes: carries is True when the renaming
    carries a's equation space onto b's.  Stops after cap renamings (yields ('cap', None))."""
    ga, ca = quotient(a, ta)
    gb, cb = quotient(b, tb)
    if sorted(d['k'] for _, d in ga.nodes(data=True)) != sorted(d['k'] for _, d in gb.nodes(data=True)):
        return
    lb = sorted(owners(b))
    idxb = {x: i for i, x in enumerate(lb)}
    wb = [sum(1 << idxb[x] for x in s) for s in b]
    rb = rank(wb)
    m = isomorphism.GraphMatcher(ga, gb, node_match=lambda x, y: x['k'] == y['k'], edge_match=lambda x, y: x['d'] == y['d'])
    count = 0
    for phi in m.isomorphisms_iter():
        count += 1
        if count > cap:
            yield 'cap', None
            return
        lift = {}
        for k, members in ca.items():
            for x, y in zip(members, cb[phi[k]]):
                lift[x] = y
        mapped = [sum(1 << idxb[lift[x]] for x in s) for s in a]
        yield lift, (rank(wb + mapped) == rb and rank(mapped) == rb)


def states(a, b, ta, tb, cap=5000):
    """'same', 'other' or 'undecided'."""
    ga, gb = junction_graph(a), junction_graph(b)
    if ga.number_of_nodes() == gb.number_of_nodes() and ga.number_of_edges() == gb.number_of_edges() and \
            isomorphism.GraphMatcher(ga, gb, edge_match=lambda x, y: x['m'] == y['m']).is_isomorphic():
        return 'same'
    for lift, ok in carriers(a, b, ta, tb, cap):
        if lift == 'cap':
            return 'undecided'
        if ok:
            return 'same'
    return 'other'
