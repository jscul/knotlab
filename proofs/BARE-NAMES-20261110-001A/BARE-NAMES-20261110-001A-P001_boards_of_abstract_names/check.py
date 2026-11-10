"""Checks for BARE-NAMES-20261110-001A: boards of abstract names.

1. T2, the labelling. On random simple 2k-regular graphs (k = 2, 3), an Euler orientation and k perfect matchings of the oriented
   double cover give k fixed-point-free permutations whose edges are exactly the graph's, each edge once.
2. T3, lifts. For every one-bit count law with a two-valued board in ticket B's frozen list, random double covers of that board,
   with the lifted values, are simple 4-regular boards the law allows.
3. T5, the moves. For every such law, the switch of an edge with its copy on two disjoint copies flips the neighbour distinction,
   and exchanging names with a place of the other value flips each endpoint's value; every resulting state is allowed.
4. T4, the named square. On the tori C_m x C_n, 3 <= m, n <= 9, the square law (coordinates mod 3, one neighbour at each unit
   offset, squares closing) has a state iff 3 divides m and n, as every component must be Z^2/L with L inside 3Z^2.
5. Ticket B's table, cross-checked. Every pair (value, number of 1-neighbours) and every edge value pair seen in an allowed colouring
   of a frozen board lies in the census's pairs and edges for that law.

Usage: check.py
"""
import importlib.util
import itertools
import json
import os
import random
import time

import networkx as nx
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
SLUG_B = 'BARE-NAMES-20261110-001B-E001_board_value_knots'
KNOTS_PY = os.path.join(ROOT, 'experiments', 'BARE-NAMES-20261110-001B', SLUG_B, 'knots.py')
KNOTS_JSON = os.path.join(ROOT, 'artifacts', 'BARE-NAMES-20261110-001B', SLUG_B, 'knots.json')
OUT = os.path.join(HERE, 'result.json')

_spec = importlib.util.spec_from_file_location('knots', KNOTS_PY)
kn = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(kn)


# --- 1. the labelling ---------------------------------------------------------------------------------------------------------

def labelling(G, k):
    orient = []
    for comp in nx.connected_components(G):
        H = G.subgraph(comp)
        orient += list(nx.eulerian_circuit(H))
    D = nx.Graph()
    left = [('+', v) for v in G]
    D.add_nodes_from(left, bipartite=0)
    D.add_nodes_from([('-', v) for v in G], bipartite=1)
    D.add_edges_from((('+', a), ('-', b)) for a, b in orient)
    sigmas = []
    for _ in range(k):
        M = nx.bipartite.hopcroft_karp_matching(D, top_nodes=left)
        sigma = {v: M[('+', v)][1] for v in G if ('+', v) in M}
        if len(sigma) != G.number_of_nodes() or len(set(sigma.values())) != G.number_of_nodes():
            return None
        sigmas.append(sigma)
        D.remove_edges_from((('+', v), ('-', w)) for v, w in sigma.items())
    return sigmas


def check_labelling():
    rows = []
    ok = True
    for k in (2, 3):
        for n in (10, 20, 40):
            for seed in range(5):
                G = nx.random_regular_graph(2 * k, n, seed=seed)
                sig = labelling(G, k)
                if sig is None:
                    rows.append([k, n, seed, False])
                    ok = False
                    continue
                edges = [frozenset((v, s[v])) for s in sig for v in G]
                good = (all(s[v] != v for s in sig for v in G) and len(edges) == len(set(edges)) == G.number_of_edges()
                        and set(edges) == {frozenset(e) for e in G.edges()})
                rows.append([k, n, seed, good])
                ok = ok and good
    return {'graphs': len(rows), 'all_decomposed': ok, 'pass': ok}


# --- 2 and 3. lifts and moves -------------------------------------------------------------------------------------------------

def double_cover(adj, rng):
    n = len(adj)
    volt = {}
    for v in range(n):
        for w in adj[v]:
            if v < w:
                volt[(v, w)] = rng.randrange(2)
    lift = [[] for _ in range(2 * n)]
    for (v, w), t in volt.items():
        for s in (0, 1):
            a, b = v + n * s, w + n * ((s + t) % 2)
            lift[a].append(b)
            lift[b].append(a)
    return [sorted(nb) for nb in lift]


def boards_with_codes():
    """For each frozen board, every colouring's set of pairs (value, number of 1-neighbours) and of edge value pairs, as bit
    masks (pairs: bit 5c + k; edges: bit 0 for 00, 1 for 01, 2 for 11)."""
    out = []
    for name, adj in kn.board_list():
        n = len(adj)
        A = np.zeros((n, n), dtype=np.int64)
        for v, nb in enumerate(adj):
            A[v, nb] = 1
        cols = ((np.arange(1 << n)[:, None] >> np.arange(n)[None, :]) & 1).astype(np.int64)
        code = 5 * cols + cols @ A.T
        pair_mask = np.bitwise_or.reduce(np.left_shift(1, code), axis=1)
        edge_mask = np.zeros(len(cols), dtype=np.int64)
        for v, nb in enumerate(adj):
            for w in nb:
                if v < w:
                    edge_mask |= np.left_shift(1, cols[:, v] + cols[:, w])
        out.append((name, adj, cols, pair_mask, edge_mask, cols.sum(axis=1)))
    return out


def main():
    t0 = time.time()
    res = {'1_labelling': check_labelling()}
    cen = json.load(open(KNOTS_JSON))
    boards = boards_with_codes()
    rng = random.Random(20261110)
    lifts_ok, moves_ok, tested = True, True, 0
    cross_bad = []
    knotted = {int(m) for m, r in cen['laws'].items() if r.get('is_knot')}
    for m in range(1 << 10):
        S = kn.law(m)
        s_mask = sum(1 << (5 * c + k) for (c, k) in S)
        r = cen['laws'][str(m)]
        t_mask = sum(1 << (5 * c + k) for (c, k) in r['types'])
        e_mask = sum(1 << (a + b) for (a, b) in r['edges'])
        found = None
        for name, adj, cols, pair_mask, edge_mask, sums in boards:
            good = (pair_mask & ~s_mask) == 0
            if not good.any():
                continue
            seen_p = int(np.bitwise_or.reduce(pair_mask[good]))
            seen_e = int(np.bitwise_or.reduce(edge_mask[good]))
            if seen_p & ~t_mask:
                cross_bad.append([m, name, 'pair'])
            if seen_e & ~e_mask:
                cross_bad.append([m, name, 'edge'])
            if found is None and m in knotted:
                idx = np.nonzero(good & (sums > 0) & (sums < len(adj)))[0]
                if len(idx):
                    found = (adj, [int(x) for x in cols[idx[0]]])
        if found is not None:
            adj, col = found
            tested += 1
            for _ in range(3):
                lift = double_cover(adj, rng)
                col2 = col + col
                if not kn.allowed_state(lift, col2, S):
                    lifts_ok = False
            mv = kn.native_moves(adj, col, S)
            if not (mv['switch_flips_n'] and mv['swap_flips_s(u)'] and mv['swap_flips_s(v)']):
                moves_ok = False
    res['2_lifts'] = {'laws': tested, 'all_allowed': lifts_ok, 'pass': lifts_ok}
    res['3_moves'] = {'laws': tested, 'knotted_laws': len(knotted), 'all_succeed': moves_ok, 'pass': moves_ok}
    res['5_cross_check'] = {'disagreements': cross_bad[:20], 'count': len(cross_bad), 'pass': not cross_bad}
    res['4_square_law'] = square_law_tori()
    res['pass'] = all(v['pass'] for v in res.values() if isinstance(v, dict))
    res['status'] = 'passed' if res['pass'] else 'failed'
    res['seconds'] = round(time.time() - t0, 1)
    json.dump(res, open(OUT, 'w'), indent=1, sort_keys=True)
    print(json.dumps({k: (v['pass'] if isinstance(v, dict) else v) for k, v in res.items()}))


# --- 4. the named square on tori ------------------------------------------------------------------------------------------------

OFFS = [(1, 0), (2, 0), (0, 1), (0, 2)]          # +e1, -e1, +e2, -e2 in (Z/3)^2


def square_state(adj):
    """A coordinate map to (Z/3)^2 with one neighbour at each unit offset and squares closing, by backtracking with
    propagation; None if there is none."""
    n = len(adj)
    coord = [None] * n
    coord[0] = (0, 0)

    def consistent():
        for v in range(n):
            if coord[v] is None:
                continue
            seen = {}
            for w in adj[v]:
                if coord[w] is None:
                    continue
                d = ((coord[w][0] - coord[v][0]) % 3, (coord[w][1] - coord[v][1]) % 3)
                if d not in OFFS or d in seen:
                    return False
                seen[d] = w
            # squares: the +e1 neighbour's +e2 neighbour is the +e2 neighbour's +e1 neighbour
            for (a, b) in (((1, 0), (0, 1)), ((1, 0), (0, 2)), ((2, 0), (0, 1)), ((2, 0), (0, 2))):
                if a in seen and b in seen:
                    x, y = seen[a], seen[b]
                    zx = [z for z in adj[x] if coord[z] is not None and ((coord[z][0] - coord[x][0]) % 3,
                                                                         (coord[z][1] - coord[x][1]) % 3) == b]
                    zy = [z for z in adj[y] if coord[z] is not None and ((coord[z][0] - coord[y][0]) % 3,
                                                                         (coord[z][1] - coord[y][1]) % 3) == a]
                    if zx and zy and zx[0] != zy[0]:
                        return False
        return True

    order = list(nx.bfs_tree(nx.Graph([(v, w) for v in range(n) for w in adj[v]]), 0))

    def solve(i):
        if i == len(order):
            return True
        v = order[i]
        if coord[v] is not None:
            return solve(i + 1)
        cands = set()
        for w in adj[v]:
            if coord[w] is not None:
                for d in OFFS:
                    cands.add(((coord[w][0] + d[0]) % 3, (coord[w][1] + d[1]) % 3))
        for c in sorted(cands):
            coord[v] = c
            if consistent() and solve(i + 1):
                return True
            coord[v] = None
        return False

    return list(coord) if solve(1) else None


def square_law_tori():
    rows = []
    ok = True
    for m in range(3, 10):
        for n in range(m, 10):
            st = square_state(kn.torus(m, n))
            has = st is not None
            pred = (m % 3 == 0) and (n % 3 == 0)
            rows.append([m, n, has])
            ok = ok and (has == pred)
    return {'tori': rows, 'prediction_holds': ok, 'pass': ok}


if __name__ == '__main__':
    main()
