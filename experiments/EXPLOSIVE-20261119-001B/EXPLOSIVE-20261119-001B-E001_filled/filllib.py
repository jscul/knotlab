"""EXPLOSIVE-20261119-001B: the filled map of joins, and growth with its groups.

The **filled map** of a start is X⁺'s incidence graph (live knots as points, blocks N(w) ∩ live for every knot w, as in
DOUBLE-IDENT), with a two-cell glued on every cycle of three blocks: three live knots pairwise in three different blocks, with no
block holding all three. Those cycles are exactly the round-1 groups of three (DEAD-CAP Lemma 2). Its first Betti number is
computed over GF(2), per piece, with b2 = the number of cells less the rank of their boundaries.

**The filled reading** (H). If every piece's filled map has b1 = 0, the growth is read as a tree start's would be, with each
live knot's rays from its true round-1 demand:
- d_k counts the groups through k, a group of three counting once;
- rays s_k · R(open_k), with s_k = open_k − d_k;
- a piece with no ray counts two when there are two or more pieces;
- "closes" if nothing remains.

If some piece keeps a cycle (b1 ≥ 1), the reading is "cycle left".

**Growth.** The program's engine (joinlib's state, the fewest counts, structural implied test), round by round to round T or a
junction cap. It records each round's count and its largest group (most parents of a junction born that round)."""
import importlib.util
import itertools
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path

import networkx as nx

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
_s = importlib.util.spec_from_file_location('cc_mc_x', ROOT / 'proofs/CAP-CHAINS-20261119-001A/CAP-CHAINS-20261119-001A-P001_caps/machine_check.py')
CC = importlib.util.module_from_spec(_s)
sys.modules['cc_mc_x'] = CC
_s.loader.exec_module(CC)
DC, J = CC.DC, CC.J


def structure(sizes, e):
    n, nb, opn, live, groups, d = DC.data(sizes, e)
    ls = set(live)
    s4 = not any(len(nb[u] & nb[v]) >= 2 for u, v in itertools.combinations(live, 2))
    stall = any(d[k] > opn[k] for k in live)
    blocks = {w: frozenset(nb[w] & ls) for w in range(n) if len(nb[w] & ls) >= 2}
    of = defaultdict(set)
    for w, B in blocks.items():
        for k in B:
            of[k].add(w)
    tri = []
    for x, y, z in itertools.combinations(sorted(of), 3):
        a, b, c = of[x] & of[y], of[y] & of[z], of[z] & of[x]
        if a and b and c and not (of[x] & of[y] & of[z]):
            tri.append(((x, y, z), (min(a), min(b), min(c))))
    G = nx.Graph()
    G.add_nodes_from(('p', k) for k in live)
    for w, B in blocks.items():
        for k in B:
            G.add_edge(('b', w), ('p', k))
    pieces = []
    for comp in nx.connected_components(G):
        H = G.subgraph(comp)
        pts = sorted(x[1] for x in comp if x[0] == 'p')
        cells = [[('p', x), ('b', wa), ('p', y), ('b', wb), ('p', z), ('b', wc)] for (x, y, z), (wa, wb, wc) in tri if x in pts]
        rays = sum((opn[k] - d[k]) * {1: 2, 2: 1}.get(opn[k], 0) for k in pts)
        pieces.append({'points': pts, 'rank': H.number_of_edges() - H.number_of_nodes() + 1, 'cells': len(cells),
                       'b1': b1_filled(H, cells)[0], 'b2': b1_filled(H, cells)[1], 'rays': rays})
    op = any(set(t1[0]) & set(t2[0]) for t1, t2 in itertools.combinations(tri, 2))
    ob = any(set(t1[1]) & set(t2[1]) for t1, t2 in itertools.combinations(tri, 2))
    return {'n': n, 'live': live, 'open': opn, 'd': d, 'groups': groups, 's4': s4, 'stall': stall, 'tri': len(tri),
            'overlap_point': op, 'overlap_block': ob,
            'pieces': pieces, 'max_group1': max((len(g) for g in groups), default=0)}


def b1_filled(H, cells):
    E = list(H.edges())
    idx = {frozenset(x): i for i, x in enumerate(E)}
    rank_graph = H.number_of_edges() - H.number_of_nodes() + 1
    rows = []
    for cyc in cells:
        m = 0
        for u, v in zip(cyc, cyc[1:] + cyc[:1]):
            m ^= 1 << idx[frozenset((u, v))]
        rows.append(m)
    basis = {}
    r = 0
    for x in rows:
        while x:
            h = x.bit_length() - 1
            if h in basis:
                x ^= basis[h]
            else:
                basis[h] = x
                r += 1
                break
    return rank_graph - r, len(rows) - r


def filled_reading(S):
    ps = S['pieces']
    if any(p['b1'] > 0 for p in ps):
        return 'cycle left'
    many = len(ps) >= 2
    D = max((p['rays'] if p['rays'] else (2 if many else 0)) for p in ps) if ps else 0
    return 'closes' if D == 0 else f'dimension {D}'


def grow(sizes, e, T, maxj):
    P = J.S.from_junctions(J.stars_from(sizes, e))
    P.linalg = False
    counts, groups = [len(sizes)], [1]
    outcome = 'alive'
    for t in range(1, T + 1):
        r = P.step(J.F.fewest, None)
        if r is None:
            outcome = 'stall'
            break
        if r['new'] == 0:
            outcome = 'closed'
            counts.append(0)
            groups.append(0)
            break
        born = [j for j, ro in enumerate(P.round_of) if ro == t]
        counts.append(len(born))
        groups.append(max(P.parents[j] for j in born))
        if len(P.bits_of) > maxj:
            outcome = 'cap'
            break
    return {'outcome': outcome, 'counts': counts, 'groups': groups}


def measured(g):
    """Exclusive classes, in this order: closes; polynomial of dimension D with period q (the D-th differences at lag q vanish on
    the last max(4, D + 3) values, q = 1, 2, 3, D = 1..8); explosive (a round-over-round ratio of at least 3 at round 4 or later,
    faster than any rate in the class within five places); exponential-like (the last five ratios within 15% of their mean, mean
    above 1.05); undecided (cut by the junction cap or the horizon before any of these)."""
    c = g['counts']
    if g['outcome'] == 'closed':
        return 'closes'
    if g['outcome'] == 'stall':
        return 'stall'
    body = c[1:]
    for D in range(1, 9):
        for q in (1, 2, 3):
            dd = body
            for _ in range(D):
                dd = [dd[i + q] - dd[i] for i in range(len(dd) - q)]
            need = max(4, D + 3)
            if len(dd) >= need and all(v == 0 for v in dd[-need:]):
                return f'dimension {D}' + ('' if q == 1 else f' (period {q})')
    rat = [c[i + 1] / c[i] for i in range(len(c) - 1) if c[i]]
    if any(r >= 3 for r in rat[3:]):
        return 'explosive'
    last = rat[-5:]
    if len(last) == 5:
        m = sum(last) / 5
        if m > 1.05 and all(abs(r - m) <= 0.15 * m for r in last):
            return 'exponential-like'
    return 'undecided'


def overlap(S):
    """Whether two cycles of three blocks share a point, or share a block."""
    return S.get('overlap_point', False), S.get('overlap_block', False)
