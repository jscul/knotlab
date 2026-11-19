"""Machine check for CHAIN-IDENT-20261119-001A-P001 (a separate algorithm, same task).

For every connected simple knot graph on 2 to 7 knots (networkx's atlas) at bare sizes, and with one surplus distinction at each knot
in turn, classify the start by (S3) no round-1 group of three, (S4) no two knots with two common neighbours, (S5+) every component of
X+ holding a live knot is infinite (a cycle of the incidence graph, or a ray), (S6) at least two live knots.  For each start in the
class, compare per round t <= T the multiset over junctions of (parents, fresh distinctions) from the growth with the multiset over
deck orbits of clusters of t + 1 points of X+'s cover holding a knot of (|R*(C)|, |boundary(C)|).  X+ has the knot blocks N(w)
(live knots only), s_w = open_w - d_w pendant points per knot, and R(open_w) rays at each pendant point (0 if open >= 3, 1 if 2,
2 if 1), truncated at T + 3 points.  Starts outside the class are tallied by reason, and the relay class (S5+ failing) is compared
too, as the control.  python3 -B machine_check.py <out.json>"""
import importlib.util
import itertools
import json
import sys
from collections import Counter, defaultdict
from fractions import Fraction
from pathlib import Path

import networkx as nx

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
_s = importlib.util.spec_from_file_location('ri_check', ROOT / 'proofs/RING-IDENT-20261119-001A/RING-IDENT-20261119-001A-P001_identification/machine_check.py')
RI = importlib.util.module_from_spec(_s)
_s.loader.exec_module(RI)
J = RI.J
T = 6


def plus_complex(n, edges, surplus):
    sizes = J.bare_sizes(n, edges, surplus)
    sh = Counter()
    nb = defaultdict(set)
    for a, b in edges:
        sh[a] += 1
        sh[b] += 1
        nb[a].add(b)
        nb[b].add(a)
    opn = [sizes[k] - sh[k] for k in range(n)]
    live = [k for k in range(n) if opn[k] >= 1]
    P = J.S.from_junctions(J.stars_from(sizes, edges))
    groups = P.groups_among(live)
    d = Counter()
    for g in groups:
        for j in g:
            d[j] += 1
    ls = set(live)
    blocks = [tuple(sorted(nb[w] & ls)) for w in range(n) if len(nb[w] & ls) >= 2]
    nv = n
    rays = 0
    pend_info = []
    for k in live:
        s = opn[k] - d[k]
        R = 0 if opn[k] >= 3 else (1 if opn[k] == 2 else 2)
        for _ in range(s):
            o = nv
            nv += 1
            blocks.append((k, o))
            for _ in range(R):
                prev = o
                for _ in range(T + 3):
                    blocks.append((prev, nv))
                    prev = nv
                    nv += 1
                rays += 1
            pend_info.append((k, R))
    return sizes, opn, live, d, groups, nv, blocks


def classify(n, edges, surplus):
    sizes, opn, live, d, groups, nv, blocks = plus_complex(n, edges, surplus)
    if any(len(g) > 2 for g in groups):
        return 'S3'
    nb = defaultdict(set)
    for a, b in edges:
        nb[a].add(b)
        nb[b].add(a)
    if any(len(nb[a] & nb[b]) >= 2 for a, b in itertools.combinations(range(n), 2)):
        return 'S4'
    if len(live) < 2:
        return 'S6'
    G = nx.Graph()
    G.add_nodes_from(('v', v) for v in range(nv))
    for i, B in enumerate(blocks):
        for v in B:
            G.add_edge(('v', v), ('b', i))
    for comp in nx.connected_components(G):
        pts = {x[1] for x in comp if x[0] == 'v'}
        if not (pts & set(live)):
            continue
        H = G.subgraph(comp)
        infinite = H.number_of_edges() >= H.number_of_nodes() or any(p >= n and H.degree(('v', p)) >= 2 and any(
            len(blocks[b[1]]) == 2 and p in blocks[b[1]] and min(blocks[b[1]]) >= n for b in H.neighbors(('v', p))) for p in pts)
        if not infinite:
            return 'S5+'
    return 'in'


def model(n, edges, surplus):
    sizes, opn, live, d, groups, nv, blocks = plus_complex(n, edges, surplus)
    inv = defaultdict(Counter)
    for x in range(nv):
        proj, adj, depth = RI.cover_ball(nv, blocks, x, T + 3)
        is_knot = lambda c: proj[c] < n  # noqa: E731
        for S in RI.clusters_with(0, adj, T + 1):
            if not any(is_knot(c) for c in S) or max(depth[c] for c in S) > T + 1:
                continue
            bd = len(set().union(*(adj[v] for v in S)) - S)
            inv[len(S) - 1][(RI.removable(S, adj, is_knot), bd)] += Fraction(1, len(S))
    for k in range(n):                       # a knot that is not live is a round-0 junction with nothing open
        if k not in live:
            inv[0][(0, 0)] += 1
    return {t: {k: v for k, v in c.items() if v} for t, c in inv.items()}


def growth(n, edges, surplus):
    sizes = J.bare_sizes(n, edges, surplus)
    P = J.S.from_junctions(J.stars_from(sizes, edges))
    P.linalg = False
    inv = defaultdict(Counter)
    for j in range(n):
        inv[0][(0, len(P.loose(j)))] += 1
    for t in range(1, T + 1):
        r = P.step(J.F.fewest, None)
        if r is None or r['new'] == 0:
            break
        for j, rr in enumerate(P.round_of):
            if rr == t:
                inv[t][(P.parents[j], P.fresh[j])] += 1
    return {t: {k: Fraction(v) for k, v in c.items()} for t, c in inv.items()}


def main():
    dest = Path(sys.argv[1])
    out = {'classes': Counter(), 'compare': Counter(), 'disagreements_in_class': []}
    for G in nx.graph_atlas_g():
        if not (2 <= G.number_of_nodes() <= 7) or not nx.is_connected(G):
            continue
        n = G.number_of_nodes()
        edges = sorted(tuple(sorted(e)) for e in G.edges())
        for surplus in [{}] + [{str(k): 1} for k in range(n)]:
            c = classify(n, edges, surplus)
            out['classes'][c] += 1
            floor = any(J.bare_sizes(n, edges, surplus)[k] > len([e for e in edges if k in e]) + 0 for k in range(n))
            if c not in ('in', 'S5+'):
                continue
            a, b = growth(n, edges, surplus), model(n, edges, surplus)
            same = all(a.get(t, {}) == b.get(t, {}) for t in range(T + 1) if t in a or t in b)
            out['compare'][f'{c}:{"agree" if same else "differ"}'] += 1
            if c == 'in' and not same and len(out['disagreements_in_class']) < 10:
                out['disagreements_in_class'].append([n, edges, surplus,
                                                      {t: {str(k): str(v) for k, v in x.items()} for t, x in a.items()},
                                                      {t: {str(k): str(v) for k, v in x.items()} for t, x in b.items()}])
    out['classes'] = dict(out['classes'])
    out['compare'] = dict(out['compare'])
    dest.write_text(json.dumps(out, indent=1, default=str))
    print(json.dumps({k: v for k, v in out.items() if k != 'disagreements_in_class'}), len(out['disagreements_in_class']))


if __name__ == '__main__':
    main()
