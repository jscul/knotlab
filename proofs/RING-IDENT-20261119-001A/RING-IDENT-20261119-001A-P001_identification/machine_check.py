"""Machine checks for RING-IDENT-20261119-001A-P001 (a separate algorithm, same task).

1. Girth (Lemma 1): over every connected simple knot graph on 3 to 7 knots (networkx's atlas) at bare sizes, and with one surplus
   distinction at each knot in turn, every start in RING-PAIR's scope (covermodel.in_scope) has a candidate complex whose
   vertex-block incidence graph has girth >= 8 (no cycle of two or three blocks).  Out-of-scope starts are counted by girth.
2. Invariants (the theorem's parent and loose-bit clauses): for every in-scope start on 3 to 7 knots whose knot graph has a cycle
   (S5), and, as the control that S5 is needed, for the in-scope trees, the multiset over junctions of round t of
   (parents, fresh distinctions) from the growth equals the multiset over deck orbits of clusters of size t + 1 containing a knot of
   (|R*(C)|, |boundary(C)|), for t = 0..T.  Clusters are enumerated in a ball of the universal cover around each vertex's base lift;
   an orbit of size-m clusters is met once at each of its m points, so each rooted cluster counts 1/m.
python3 -B machine_check.py <out.json>"""
import itertools
import json
import sys
from collections import Counter, defaultdict
from fractions import Fraction
from pathlib import Path

import networkx as nx

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'experiments/RING-PAIR-20261119-001B/RING-PAIR-20261119-001B-E001_cover'))
import covermodel as CM  # noqa: E402
J = CM.J


def incidence_girth(nv, blocks):
    G = nx.Graph()
    for i, B in enumerate(blocks):
        for v in B:
            G.add_edge(('v', v), ('b', i))
    try:
        return nx.girth(G)
    except Exception:
        cyc = nx.minimum_cycle_basis(G)
        return min((len(c) for c in cyc), default=float('inf'))


def cover_ball(nv, blocks, root, radius):
    """Unroll the incidence graph from vertex `root` to `radius` vertex steps.  Returns (proj, adj, blocks_of): cover vertices are
    ints, proj maps them to X's vertices, and adjacency is through cover blocks."""
    at = defaultdict(list)
    for i, B in enumerate(blocks):
        for v in B:
            at[v].append(i)
    proj = {0: root}
    depth = {0: 0}
    came = {0: None}            # the block index the vertex was entered through
    cblocks = []                # (block index, [cover vertices])
    frontier = [0]
    nxt_id = 1
    while frontier:
        new = []
        for u in frontier:
            if depth[u] >= radius:
                continue
            for bi in at[proj[u]]:
                if bi == came[u]:
                    continue
                members = [u]
                for w in blocks[bi]:
                    if w == proj[u]:
                        continue
                    c = nxt_id
                    nxt_id += 1
                    proj[c] = w
                    depth[c] = depth[u] + 1
                    came[c] = bi
                    members.append(c)
                    new.append(c)
                cblocks.append(members)
        frontier = new
    adj = defaultdict(set)
    for members in cblocks:
        for a, b in itertools.combinations(members, 2):
            adj[a].add(b)
            adj[b].add(a)
    return proj, adj, depth


def clusters_with(root, adj, m):
    """All connected vertex sets of size <= m containing `root` (each once)."""
    out = []
    seen = set()
    stack = [frozenset([root])]
    while stack:
        S = stack.pop()
        if S in seen:
            continue
        seen.add(S)
        out.append(S)
        if len(S) == m:
            continue
        bd = set().union(*(adj[v] for v in S)) - S
        for x in bd:
            stack.append(S | {x})
    return out


def removable(S, adj, is_knot):
    out = 0
    for v in S:
        R = S - {v}
        if not R or not any(is_knot(x) for x in R):
            continue
        start = next(iter(R))
        seen, st = {start}, [start]
        while st:
            a = st.pop()
            for b in adj[a] & R:
                if b not in seen:
                    seen.add(b)
                    st.append(b)
        if len(seen) == len(R):
            out += 1
    return out


def model_invariants(n, edges, surplus, T):
    nv, blocks = CM.blocks_of(n, edges, surplus)
    inv = defaultdict(Counter)
    for x in range(nv):
        proj, adj, depth = cover_ball(nv, blocks, x, T + 3)
        is_knot = lambda c: proj[c] < n  # noqa: E731
        for S in clusters_with(0, adj, T + 1):
            if not any(is_knot(c) for c in S):
                continue
            if max(depth[c] for c in S) > T + 1:
                continue
            bd = len(set().union(*(adj[v] for v in S)) - S)
            inv[len(S) - 1][(removable(S, adj, is_knot), bd)] += Fraction(1, len(S))
    return {t: {k: v for k, v in c.items()} for t, c in inv.items()}


def growth_invariants(n, edges, surplus, T):
    P = J.S.from_junctions(J.stars_from(J.bare_sizes(n, edges, surplus), edges))
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
    return {t: dict(c) for t, c in inv.items()}


def main():
    dest = Path(sys.argv[1])
    out = {'girth': Counter(), 'in_scope': 0, 'in_scope_girth_below_8': [], 'invariants': {}}
    starts = []
    for G in nx.graph_atlas_g():
        if not (3 <= G.number_of_nodes() <= 7) or not nx.is_connected(G):
            continue
        n = G.number_of_nodes()
        edges = sorted(tuple(sorted(e)) for e in G.edges())
        for surplus in [{}] + [{str(k): 1} for k in range(n)]:
            ok, why = CM.in_scope(n, edges, surplus)
            nv, blocks = CM.blocks_of(n, edges, surplus)
            g = incidence_girth(nv, blocks)
            out['girth'][f"{'in' if ok else 'out'}:{g}"] += 1
            if ok:
                out['in_scope'] += 1
                if g < 8:
                    out['in_scope_girth_below_8'].append([n, edges, surplus, g])
                starts.append((n, edges, surplus, not nx.is_tree(G)))
    out['girth'] = dict(out['girth'])
    T = 6
    tally = Counter()
    for n, edges, surplus, cyc in starts:
        a = growth_invariants(n, edges, surplus, T)
        b = model_invariants(n, edges, surplus, T)
        b = {t: {k: v for k, v in c.items() if v} for t, c in b.items()}
        same = all({k: Fraction(v) for k, v in a.get(t, {}).items()} == b.get(t, {}) for t in range(0, T + 1) if t in a or t in b)
        tally[('S5' if cyc else 'tree', same)] += 1
        if not same and cyc:
            out['invariants'][str((n, edges, surplus))] = {'growth': {t: {str(k): v for k, v in c.items()} for t, c in a.items()},
                                                          'model': {t: {str(k): str(v) for k, v in c.items()} for t, c in b.items()}}
    out['invariants'] = {'disagreements_with_S5': out['invariants'],
                         'tally': {f'{k[0]}:{"agree" if k[1] else "differ"}': v for k, v in sorted(tally.items())}}
    dest.write_text(json.dumps(out, indent=1, default=str))
    print(json.dumps({k: v for k, v in out.items() if k != 'invariants'}), json.dumps(out['invariants']['tally']),
          len(out['invariants']['disagreements_with_S5']))


if __name__ == '__main__':
    main()
