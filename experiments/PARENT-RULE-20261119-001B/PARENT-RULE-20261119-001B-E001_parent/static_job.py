"""Shared-runner job for PARENT-RULE-20261119-001B-E001, part S (every small arrangement).  Every legal arrangement in which
junctions meet at most once, with 2 to 7 junctions and at most 3 loose distinctions per junction (at most 2 at 7 junctions):
a connected simple graph from the networkx graph atlas (the junctions and the distinctions they share) and a loose count per
junction, one per orbit of the graph's automorphisms.  Legal: every junction holds at least 3 distinctions; no cut vertex but the
outside one.  For each: its exact table (by bonds), a hash of its sorted rows (a table-isomorphism invariant), and the properties:
backed pairs (P1), backed by a closed junction (P1+), live junctions never meet (P2), the stratum (closed, pendant-only: every live
junction meets at most one junction, backed: some live junction meets two or more), the peel depth, and the control property Q
(backed pairs required of the closed junctions instead of the live ones).  Cases: one per chunk of atlas graphs."""
import hashlib
import itertools
import sys
from pathlib import Path

import networkx as nx
from networkx.algorithms import isomorphism

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import plib as L  # noqa: E402
NMAX = 7
_ATLAS = None


def atlas():
    global _ATLAS
    if _ATLAS is None:
        _ATLAS = [(i, g) for i, g in enumerate(nx.graph_atlas_g()) if 2 <= g.number_of_nodes() <= NMAX and nx.is_connected(g)]
    return _ATLAS


def lmax(n):
    return 3 if n <= 6 else 2


def setup(params):
    atlas()


def cases():
    by_n = {}
    for i, g in atlas():
        by_n.setdefault(g.number_of_nodes(), []).append(i)
    for n, idx in sorted(by_n.items()):
        step = 10 if n == 7 else (5 if n == 6 else len(idx))
        for k in range(0, len(idx), step):
            yield f'n{n}-{k // step:03d}', {'n': n, 'graphs': idx[k:k + step]}


def arrangement(g, ell):
    """Stars: shared distinctions are the graph's edges, then each junction's loose ones."""
    stars = [set() for _ in range(g.number_of_nodes())]
    b = 0
    for u, v in sorted(g.edges()):
        stars[u].add(b)
        stars[v].add(b)
        b += 1
    for j, k in enumerate(ell):
        for _ in range(k):
            stars[j].add(b)
            b += 1
    return [frozenset(s) for s in stars]


def legal(g, ell):
    n = g.number_of_nodes()
    if any(g.degree(j) + ell[j] < 3 for j in range(n)):
        return False
    h = g.copy()
    for j in range(n):
        if ell[j]:
            h.add_edge(j, 'o')
    return not (set(nx.articulation_points(h)) - {'o'})


def q_control(stars):
    own = L.owners(stars)
    nb = L.neighbours(stars, own)
    live = set(L.live_set(stars, own))
    bad = 0
    for j in range(len(stars)):
        if j in live:
            continue
        for u, v in itertools.combinations(sorted(nb[j]), 2):
            if not ((nb[u] & nb[v]) - {j}):
                bad += 1
    return bad


def run(case_id, p):
    G = dict(atlas())
    out = []
    for gi in p['graphs']:
        g = nx.convert_node_labels_to_integers(G[gi])
        n = g.number_of_nodes()
        auts = [tuple(m[i] for i in range(n)) for m in isomorphism.GraphMatcher(g, g).isomorphisms_iter()]
        for ell in itertools.product(range(lmax(n) + 1), repeat=n):
            if any(tuple(ell[s[i]] for i in range(n)) < ell for s in auts):
                continue
            if not legal(g, ell):
                continue
            stars = arrangement(g, ell)
            tab, labels = L.table(stars)
            key = hashlib.sha1(repr(L.row_key(tab, labels)).encode()).hexdigest()[:20]
            pr = L.props(stars)
            out.append([n, gi, ''.join(map(str, ell)), key, len(labels), pr['P1'], pr['P1+'], pr['P2'], pr['stratum'][0],
                        L.depth(stars), q_control(stars)])
    return {'rows': out, 'fields': ['n', 'atlas', 'loose', 'key', 'distinctions', 'P1', 'P1+', 'P2', 'stratum', 'depth', 'Q']}
