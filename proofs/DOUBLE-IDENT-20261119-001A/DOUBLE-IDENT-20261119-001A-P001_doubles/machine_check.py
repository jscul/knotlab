"""Machine check for DOUBLE-IDENT-20261119-001A-P001 (a separate algorithm, same task).

Every arrangement of TOUCH-CENSUS-20261118-001 (26,441, 1 to 5 knots, 3 to 5 places, any number of shared distinctions between two
knots; `runs/touch-census`) is classified on the data the growth reads: the live knots (open = places - shared >= 1, shared counted
with multiplicity), each knot's live neighbours, and the round-1 groups among live knots.
- stall: some live knot has demand above its open count;
- out: a round-1 group of three or more (S3), or two live knots with two common neighbours, live or not (S4);
- one loose: the start holds a single loose distinction (S6');
- in: the rest.
For every arrangement in the class and every one-loose arrangement, the growth's per-round multiset of (parents, fresh) to T = 6 is
compared with the relayed extended cover's (RELAY-IDENT): X+ over the live knots with blocks N(w) ∩ live for every knot w, s = open
- d pendant points per live knot with R(open) rays, a relay point with two rays on each finite piece when there are two or more
pieces, and closure at round 1 for a one-loose start.  python3 -B machine_check.py <out.json>"""
import importlib.util
import itertools
import json
import sys
from collections import Counter, defaultdict
from fractions import Fraction
from multiprocessing import Pool
from pathlib import Path

import networkx as nx

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
_s = importlib.util.spec_from_file_location('ri_check', ROOT / 'proofs/RING-IDENT-20261119-001A/RING-IDENT-20261119-001A-P001_identification/machine_check.py')
RI = importlib.util.module_from_spec(_s)
_s.loader.exec_module(RI)
J = RI.J
sys.path.insert(0, str(ROOT / 'scripts'))
from longrun import load_results  # noqa: E402
T = 6


def edges_of(key):
    sizes, flat = key
    e = []
    for (i, j), m in zip(itertools.combinations(range(len(sizes)), 2), flat):
        e += [(i, j)] * m
    return list(sizes), e


def data(sizes, edges):
    n = len(sizes)
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
    return n, nb, opn, live, groups, d


def classify(sizes, edges):
    n, nb, opn, live, groups, d = data(sizes, edges)
    if any(d[k] > opn[k] for k in live):
        return 'stall'
    if any(len(g) > 2 for g in groups):
        return 'out'
    if any(len(nb[a] & nb[b]) >= 2 for a, b in itertools.combinations(live, 2)):
        return 'out'
    loose = sum(opn[k] for k in live)
    if loose == 0:
        return 'none'
    if loose == 1:
        return 'one loose'
    return 'in'


def complex_of(sizes, edges):
    n, nb, opn, live, groups, d = data(sizes, edges)
    ls = set(live)
    blocks = [tuple(sorted(nb[w] & ls)) for w in range(n) if len(nb[w] & ls) >= 2]
    nv = n
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
    return n, live, nv, blocks


def model(sizes, edges):
    n, live, nv, blocks = complex_of(sizes, edges)
    inv = defaultdict(Counter)
    ls = set(live)
    for k in range(n):
        if k not in ls:
            inv[0][(0, 0)] += 1
    G = nx.Graph()
    G.add_nodes_from(('v', v) for v in range(nv) if v >= n or v in ls)
    for i, B in enumerate(blocks):
        for v in B:
            G.add_edge(('v', v), ('b', i))
    pieces = []
    for comp in nx.connected_components(G):
        pts = {x[1] for x in comp if x[0] == 'v'}
        if not (pts & ls):
            continue
        H = G.subgraph(comp)
        infinite = H.number_of_edges() >= H.number_of_nodes() or any(p >= n and H.degree(('v', p)) >= 2 for p in pts)
        pieces.append((pts, infinite))
    for x in range(nv):
        if x < n and x not in ls:
            continue
        proj, adj, depth = RI.cover_ball(nv, blocks, x, T + 3)
        is_knot = lambda c: proj[c] < n  # noqa: E731
        for S in RI.clusters_with(0, adj, T + 1):
            if not any(is_knot(c) for c in S) or max(depth[c] for c in S) > T + 1:
                continue
            bd = len(set().union(*(adj[v] for v in S)) - S)
            inv[len(S) - 1][(RI.removable(S, adj, is_knot), bd)] += Fraction(1, len(S))
    many = len(pieces) >= 2
    for pts, infinite in pieces:
        if infinite:
            continue
        m = len(pts)
        adj = defaultdict(set)
        for B in blocks:
            if set(B) <= pts:
                for a, b in itertools.combinations(B, 2):
                    adj[a].add(b)
                    adj[b].add(a)
        rstar = RI.removable(frozenset(pts), adj, lambda c: c < n)
        t0 = m - 1
        if t0 <= T and many:
            inv[t0][(rstar, 0)] -= 1
            inv[t0][(rstar, 1)] += 1
            for k in range(1, T - t0 + 1):
                inv[t0 + k][(1, 2)] += 1 if k == 1 else 2
                if k > 2:
                    inv[t0 + k][(2, 2)] += k - 2
    return {t: {k: Fraction(v) for k, v in c.items() if v} for t, c in inv.items()}


def growth(sizes, edges):
    P = J.S.from_junctions(J.stars_from(sizes, edges))
    P.linalg = False
    inv = defaultdict(Counter)
    for j in range(len(sizes)):
        inv[0][(0, len(P.loose(j)))] += 1
    for t in range(1, T + 1):
        r = P.step(J.F.fewest, None)
        if r is None or r['new'] == 0:
            break
        for j, rr in enumerate(P.round_of):
            if rr == t:
                inv[t][(P.parents[j], P.fresh[j])] += 1
    return {t: {k: Fraction(v) for k, v in c.items()} for t, c in inv.items()}


def one(key):
    sizes, edges = edges_of(key)
    c = classify(sizes, edges)
    multi = 'double touches' if any(m >= 2 for m in key[1]) else 'simple'
    if c not in ('in', 'one loose'):
        return key, c, multi, None
    a = growth(sizes, edges)
    if c == 'one loose':
        same = all(a.get(t, {}) == {} for t in range(2, T + 1)) and a.get(1, {}) == {(1, 0): 1}
    else:
        b = model(sizes, edges)
        same = all(a.get(t, {}) == b.get(t, {}) for t in range(T + 1) if t in a or t in b)
    return key, c, multi, same


def main():
    dest = Path(sys.argv[1])
    R = load_results(str(ROOT / 'runs/touch-census'))
    keys = [(tuple(a['key'][0]), tuple(a['key'][1])) for r in R.values() if r.get('status') == 'ok' for a in r['result']['arrangements']]
    with Pool(6) as p:
        res = p.map(one, keys, chunksize=20)
    out = {'arrangements': len(res), 'classes': Counter(), 'compare': Counter(), 'disagreements': []}
    for key, c, multi, same in res:
        out['classes'][f'{c}, {multi}'] += 1
        if same is not None:
            out['compare'][f'{c}, {multi}: {"agree" if same else "differ"}'] += 1
            if not same and len(out['disagreements']) < 12:
                out['disagreements'].append([list(map(list, key)), c])
    out['classes'] = dict(sorted(out['classes'].items()))
    out['compare'] = dict(sorted(out['compare'].items()))
    dest.write_text(json.dumps(out, indent=1, default=str))
    print(json.dumps({k: v for k, v in out.items() if k != 'disagreements'}, indent=1), len(out['disagreements']))


if __name__ == '__main__':
    main()
