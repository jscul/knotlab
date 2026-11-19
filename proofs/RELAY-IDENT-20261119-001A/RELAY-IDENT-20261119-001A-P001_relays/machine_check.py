"""Machine check for RELAY-IDENT-20261119-001A-P001 (a separate algorithm, same task).

For every connected simple knot graph on 2 to 7 knots (networkx's atlas) at bare sizes, and with one surplus distinction at each knot
in turn, every start with (S3) and (S4) is compared, per round t <= T, on the multiset over junctions of (parents, fresh distinctions)
from the growth against the model:
- infinite pieces of X+ (a cycle of the incidence graph or a ray): its clusters of t + 1 points, (|R*(C)|, |boundary(C)|), as in
  CHAIN-IDENT;
- a finite piece Y without chains: its clusters up to its top Y (round |Y| - 1).  If another piece holds a live knot, the top gets
  (|R*(Y)|, 1) and a relay follows: round |Y| - 1 + k holds k junctions, the relay point (1, 2) at k = 1, and for k >= 2 two chain
  ends (1, 2) and k - 2 two-chain junctions (2, 2).  If it is the only piece with a live knot, the top gets (|R*(Y)|, 0) and the
  growth closes.
python3 -B machine_check.py <out.json>"""
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
_s = importlib.util.spec_from_file_location('ci_check', ROOT / 'proofs/CHAIN-IDENT-20261119-001A/CHAIN-IDENT-20261119-001A-P001_chains/machine_check.py')
CI = importlib.util.module_from_spec(_s)
_s.loader.exec_module(CI)
RI = CI.RI
J = CI.J
T = CI.T


def pieces(n, edges, surplus):
    """The pieces of X+ holding a live knot: (points, infinite?)."""
    sizes, opn, live, d, groups, nv, blocks = CI.plus_complex(n, edges, surplus)
    G = nx.Graph()
    G.add_nodes_from(('v', v) for v in range(nv))
    for i, B in enumerate(blocks):
        for v in B:
            G.add_edge(('v', v), ('b', i))
    out = []
    for comp in nx.connected_components(G):
        pts = {x[1] for x in comp if x[0] == 'v'}
        if not (pts & set(live)):
            continue
        H = G.subgraph(comp)
        has_cycle = H.number_of_edges() >= H.number_of_nodes()
        has_ray = len(pts) > len([p for p in pts if p < n]) + sum(1 for p in pts if p >= n and H.degree(('v', p)) == 1) \
            or any(p >= n and H.degree(('v', p)) >= 2 for p in pts)
        out.append((pts, has_cycle or has_ray))
    return out, blocks, nv, live


def model(n, edges, surplus):
    inv = CI.model(n, edges, surplus)
    ps, blocks, nv, live = pieces(n, edges, surplus)
    # CHAIN-IDENT's model counts a knot that is not live twice, once as an isolated point of the cover and once by hand (harmless
    # there: its class has no such knot); count it once here
    dead = n - len(live)
    if dead:
        inv[0][(0, 0)] -= dead
        if inv[0][(0, 0)] == 0:
            del inv[0][(0, 0)]
    many = len(ps) >= 2
    for pts, infinite in ps:
        if infinite:
            continue
        m = len(pts)
        adj = defaultdict(set)
        for B in blocks:
            if set(B) <= pts:
                for a, b in itertools.combinations(B, 2):
                    adj[a].add(b)
                    adj[b].add(a)
        top = frozenset(pts)
        rstar = RI.removable(top, adj, lambda c: c < n)
        t0 = m - 1
        key = (rstar, 0)
        if t0 <= T and inv.get(t0, {}).get(key, 0) >= 1 and many:
            inv[t0][key] -= 1
            if inv[t0][key] == 0:
                del inv[t0][key]
            inv[t0][(rstar, 1)] = inv[t0].get((rstar, 1), 0) + 1
            for k in range(1, T - t0 + 1):
                t = t0 + k
                inv.setdefault(t, {})
                if k == 1:
                    inv[t][(1, 2)] = inv[t].get((1, 2), 0) + 1
                else:
                    inv[t][(1, 2)] = inv[t].get((1, 2), 0) + 2
                    if k > 2:
                        inv[t][(2, 2)] = inv[t].get((2, 2), 0) + (k - 2)
    return {t: {k: Fraction(v) for k, v in c.items() if v} for t, c in inv.items()}


def main():
    dest = Path(sys.argv[1])
    out = {'compare': Counter(), 'disagreements': []}
    for G in nx.graph_atlas_g():
        if not (2 <= G.number_of_nodes() <= 7) or not nx.is_connected(G):
            continue
        n = G.number_of_nodes()
        edges = sorted(tuple(sorted(e)) for e in G.edges())
        for surplus in [{}] + [{str(k): 1} for k in range(n)]:
            c = CI.classify(n, edges, surplus)
            if c not in ('in', 'S5+', 'S6'):
                continue
            ps, *_ = pieces(n, edges, surplus)
            kind = 'chains only' if all(inf for _, inf in ps) else ('relay' if len(ps) >= 2 else 'single finite piece')
            a, b = CI.growth(n, edges, surplus), model(n, edges, surplus)
            same = all(a.get(t, {}) == b.get(t, {}) for t in range(T + 1) if t in a or t in b)
            out['compare'][f'{kind}:{"agree" if same else "differ"}'] += 1
            if not same and len(out['disagreements']) < 10:
                out['disagreements'].append([n, edges, surplus, kind,
                                             {t: {str(k): str(v) for k, v in x.items()} for t, x in a.items()},
                                             {t: {str(k): str(v) for k, v in x.items()} for t, x in b.items()}])
    out['compare'] = dict(out['compare'])
    dest.write_text(json.dumps(out, indent=1, default=str))
    print(json.dumps(out['compare']), len(out['disagreements']))


if __name__ == '__main__':
    main()
