"""The frozen census of PLACE-FLIP-20261110-001B: which board-value knots of abstract names flip in place.

The family is the 90 one-bit count laws of degree four whose board knots with the values (BARE-NAMES-20261110-001B): one neighbour
distinction n(u, v) and its two endpoint values s(u), s(v) form a knot.

Flips in place (frozen in the pre-registration):
  - a value s(u) is flipped in place at a state x when some finite change of values alone (every neighbour distinction kept) flips
    it, is not a renaming (not x composed with a permutation of finitely many names), and is minimal (no allowed change of a proper
    subset of its values flips s(u));
  - a neighbour distinction is flipped in place by a change of neighbour distinctions alone with the same three conditions; the
    switch of an edge with its copy does this when the edge lies on a cycle (ticket A);
  - the knot of law L is native in place at x when, for some edge {u, v}, all three of n(u, v), s(u), s(v) are flipped in place.

Worlds:
  dust   infinitely many disjoint copies of an allowed coloured board (B, c), B from the frozen list and c using both values; for the
         laws whose boards never put a 0 beside a 1, copies of (B0, all 0) and (B1, all 1), B1 the first frozen board not isomorphic
         to B0. A change of values on one copy is a renaming exactly when its new colouring is an automorphic image of c (ticket A).
  tree   the universal cover of such a coloured board (for those laws, the covers of (B0, all 0) and (B1, all 1)). A tree has no
         renaming that moves finitely many places, so a change of values there is never a renaming (ticket A). The search changes
         values within distance 2 of u only.

Usage: flips.py [--out FILE] [--controls-only]
"""
import argparse
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
SLUG = 'PLACE-FLIP-20261110-001B-E001_flips_in_place'
DEFAULT_OUT = os.path.join(ROOT, 'artifacts', 'PLACE-FLIP-20261110-001B', SLUG, 'flips.json')
BN = 'BARE-NAMES-20261110-001B-E001_board_value_knots'
KNOTS_PY = os.path.join(ROOT, 'experiments', 'BARE-NAMES-20261110-001B', BN, 'knots.py')
KNOTS_JSON = os.path.join(ROOT, 'artifacts', 'BARE-NAMES-20261110-001B', BN, 'knots.json')

_spec = importlib.util.spec_from_file_location('knots', KNOTS_PY)
kn = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(kn)

NO_MIXED = 'knot: no edge 01'


# --- the frozen boards ----------------------------------------------------------------------------------------------------------

def random_bipartite(m, seed):
    rng = random.Random(seed)
    while True:
        edges = set()
        ok = True
        for _ in range(4):
            perm = list(range(m))
            rng.shuffle(perm)
            for i, j in enumerate(perm):
                e = (i, m + j)
                if e in edges:
                    ok = False
                    break
                edges.add(e)
            if not ok:
                break
        if ok:
            G = nx.Graph(list(edges))
            if nx.is_connected(G):
                return G


def frozen_boards():
    boards = list(kn.board_list())
    for n in (8, 10, 12, 14, 16):
        for seed in range(4):
            G = nx.random_regular_graph(4, n, seed=seed)
            if nx.is_connected(G):
                boards.append(('random 4-regular n=%d seed=%d' % (n, seed), [sorted(G[v]) for v in range(n)]))
    for m in (4, 5, 6, 7, 8):
        for seed in range(4):
            G = random_bipartite(m, seed)
            boards.append(('random bipartite 4-regular n=%d seed=%d' % (2 * m, seed), [sorted(G[v]) for v in range(2 * m)]))
    for name, adj in boards:
        assert all(len(nb) == 4 and v not in nb for v, nb in enumerate(adj)), name
        assert all(v in adj[w] for v, nb in enumerate(adj) for w in nb), name
    return boards


def automorphisms(adj):
    G = nx.Graph([(v, w) for v, nb in enumerate(adj) for w in nb])
    return [tuple(m[v] for v in range(len(adj))) for m in nx.algorithms.isomorphism.GraphMatcher(G, G).isomorphisms_iter()]


def allowed_colourings(adj, S):
    n = len(adj)
    A = np.zeros((n, n), dtype=np.int64)
    for v, nb in enumerate(adj):
        A[v, nb] = 1
    cols = ((np.arange(1 << n)[:, None] >> np.arange(n)[None, :]) & 1).astype(np.int64)
    code = 5 * cols + cols @ A.T
    ok = np.zeros(10, dtype=bool)
    for (c, k) in S:
        ok[5 * c + k] = True
    return [int(x) for x in np.nonzero(ok[code].all(axis=1))[0]]


def orbit(c, auts, n):
    return {sum(((c >> s[v]) & 1) << v for v in range(n)) for s in auts}


def flips_in_place_dust(c, x, allowed, orb):
    """The smallest minimal change of values on the copy that flips x and is not an automorphic image of c, as a size, or None.
    Changes are taken in order of size, so a change is minimal exactly when it contains no minimal change found before it."""
    ds = sorted((c ^ a for a in allowed if ((c ^ a) >> x) & 1), key=lambda d: bin(d).count('1'))
    mins = []
    for d in ds:
        if any(e & d == e for e in mins):
            continue
        mins.append(d)
        if (c ^ d) not in orb:
            return bin(d).count('1')
    return None


# --- the switch ------------------------------------------------------------------------------------------------------------------

def switch_check(adj, col, S, u, v):
    """The switch of {u, v} with its copy on two disjoint copies: allowed, minimal over the four changed distinctions, and joining the
    copies into one connected component (so not a renaming)."""
    n = len(adj)
    base = [set(nb) for nb in adj] + [set(w + n for w in nb) for nb in adj]
    col2 = list(col) + list(col)
    u2, v2 = u + n, v + n
    changes = [(u, v, 0), (u2, v2, 0), (u, v2, 1), (u2, v, 1)]

    def apply(sub):
        g = [set(nb) for nb in base]
        for (a, b, on) in sub:
            if on:
                g[a].add(b)
                g[b].add(a)
            else:
                g[a].discard(b)
                g[b].discard(a)
        return [sorted(nb) for nb in g]

    full = apply(changes)
    ok = kn.allowed_state(full, col2, S)
    minimal = all(not (kn.allowed_state(apply(sub), col2, S) and v not in apply(sub)[u])
                  for r in range(1, 4) for sub in itertools.combinations(changes, r) if (u, v, 0) in sub)
    G = nx.Graph([(a, b) for a, nb in enumerate(full) for b in nb])
    joined = nx.node_connected_component(G, u) == set(range(2 * n))
    return bool(ok and minimal and joined)


# --- the tree --------------------------------------------------------------------------------------------------------------------

def tree_ball(adj, root, radius=4):
    """The ball of radius `radius` of the universal cover, rooted at a lift of `root`: node images, parents, depths, neighbours."""
    img, par, dep = [root], [-1], [0]
    frontier = [0]
    for d in range(1, radius + 1):
        nxt = []
        for t in frontier:
            for b in adj[img[t]]:
                if par[t] >= 0 and b == img[par[t]]:
                    continue
                img.append(b)
                par.append(t)
                dep.append(d)
                nxt.append(len(img) - 1)
        frontier = nxt
    nbrs = [[] for _ in img]
    for t, p in enumerate(par):
        if p >= 0:
            nbrs[t].append(p)
            nbrs[p].append(t)
    return img, par, dep, nbrs


def flips_in_place_tree(adj, col, S, x, cache):
    """Is some change of values within distance 2 of the root, root flipped, allowed in the cover of (B, col)? (Every such change
    contains a minimal one, and none is a renaming.)"""
    key = (tuple(map(tuple, adj)), tuple(col), x)
    if key in cache:
        return cache[key]
    img, par, dep, nbrs = tree_ball(adj, x)
    free = [t for t in range(len(img)) if 1 <= dep[t] <= 2]
    check = [t for t in range(len(img)) if dep[t] <= 3]
    base = np.array([col[b] for b in img], dtype=np.int8)
    vals = np.tile(base, (1 << len(free), 1))
    vals[:, 0] = 1 - base[0]
    bits = ((np.arange(1 << len(free))[:, None] >> np.arange(len(free))[None, :]) & 1).astype(np.int8)
    vals[:, free] = bits
    ok = np.zeros(10, dtype=bool)
    for (c, k) in S:
        ok[5 * c + k] = True
    good = np.ones(len(vals), dtype=bool)
    for t in check:
        k = vals[:, nbrs[t]].sum(axis=1)
        good &= ok[5 * vals[:, t] + k]
    res = bool(good.any())
    cache[key] = res
    return res


def two_valued(boards, S, cap):
    """The two-valued allowed colourings of the frozen boards, in frozen order, at most `cap` per board."""
    for i, (name, adj) in enumerate(boards):
        n = len(adj)
        allowed = allowed_colourings(adj, S)
        for c in [c for c in allowed if 0 < bin(c).count('1') < n][:cap]:
            yield i, name, adj, allowed, c


def run_law(m, shape, boards, auts, tree_cache, dust_cap=60, tree_worlds=12):
    S = kn.law(m)
    out = {'law': m, 'shape': shape}
    dust = tree = None
    if shape == NO_MIXED:
        b0 = next((i for i, (name, adj) in enumerate(boards) if 0 in allowed_colourings(adj, S)), None)
        b1 = None
        if b0 is not None:
            G0 = nx.Graph([(v, w) for v, nb in enumerate(boards[b0][1]) for w in nb])
            for i, (name, adj) in enumerate(boards):
                G = nx.Graph([(v, w) for v, nb in enumerate(adj) for w in nb])
                if (1 << len(adj)) - 1 in allowed_colourings(adj, S) and not nx.is_isomorphic(G, G0):
                    b1 = i
                    break
        if b0 is not None and b1 is not None:
            adj = boards[b0][1]
            n = len(adj)
            allowed = allowed_colourings(adj, S)
            u, v = 0, adj[0][0]
            du = flips_in_place_dust(0, u, allowed, orbit(0, auts[b0], n))
            dv = flips_in_place_dust(0, v, allowed, orbit(0, auts[b0], n))
            sw = switch_check(adj, [0] * n, S, u, v)
            dust = {'boards': [boards[b0][0], boards[b1][0]], 'edge': [u, v], 'flip_sizes': [du, dv], 'switch': sw,
                    'native_in_place': bool(du and dv and sw)}
            tu = flips_in_place_tree(adj, [0] * n, S, u, tree_cache)
            tv = flips_in_place_tree(adj, [0] * n, S, v, tree_cache)
            tree = {'boards': [boards[b0][0], boards[b1][0]], 'edge': [u, v], 'values_flip': [tu, tv],
                    'native_in_place': bool(tu and tv)}
    else:
        for i, name, adj, allowed, c in two_valued(boards, S, dust_cap):
            n = len(adj)
            orb = orbit(c, auts[i], n)
            for u in range(n):
                for v in adj[u]:
                    if v < u:
                        continue
                    du = flips_in_place_dust(c, u, allowed, orb)
                    dv = flips_in_place_dust(c, v, allowed, orb) if du else None
                    if du and dv:
                        col = [(c >> w) & 1 for w in range(n)]
                        sw = switch_check(adj, col, S, u, v)
                        if sw:
                            dust = {'board': name, 'colouring': c, 'edge': [u, v], 'flip_sizes': [du, dv], 'switch': sw,
                                    'native_in_place': True}
                            break
                if dust:
                    break
            if dust:
                break
        worlds = 0
        for i, name, adj, allowed, c in two_valued(boards, S, dust_cap):
            if worlds >= tree_worlds:
                break
            worlds += 1
            n = len(adj)
            col = [(c >> w) & 1 for w in range(n)]
            for u in range(n):
                if not flips_in_place_tree(adj, col, S, u, tree_cache):
                    continue
                for v in adj[u]:
                    if flips_in_place_tree(adj, col, S, v, tree_cache):
                        tree = {'board': name, 'colouring': c, 'edge': [u, v], 'native_in_place': True}
                        break
                if tree:
                    break
            if tree:
                break
        out['tree_worlds_tried'] = worlds
    out['dust'] = dust if dust else {'native_in_place': False, 'note': 'no world of the frozen class found'}
    out['tree'] = tree if tree else {'native_in_place': False, 'note': 'no value flip within distance 2 in the worlds tried'}
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default=DEFAULT_OUT)
    ap.add_argument('--controls-only', action='store_true')
    args = ap.parse_args()
    t0 = time.time()
    boards = frozen_boards()
    auts = [automorphisms(adj) for _, adj in boards]
    cache = {}
    out = {'boards': [[name, len(adj), len(a)] for (name, adj), a in zip(boards, auts)]}
    out['controls'] = {'full law 1023': run_law(1023, 'control', boards, auts, cache)}
    print('controls', json.dumps(out['controls']), round(time.time() - t0, 1), flush=True)
    if not args.controls_only:
        cen = json.load(open(KNOTS_JSON))
        knotted = sorted((int(m), r['shape']) for m, r in cen['laws'].items() if r.get('is_knot'))
        rows = []
        for idx, (m, shape) in enumerate(knotted):
            rows.append(run_law(m, shape, boards, auts, cache))
            if idx % 10 == 9:
                print(idx + 1, round(time.time() - t0, 1), flush=True)
        out['laws'] = rows
        counts = {}
        for r in rows:
            key = (r['shape'], 'dust ' + ('N' if r['dust']['native_in_place'] else 'not'),
                   'tree ' + ('N' if r['tree']['native_in_place'] else 'not'))
            counts[' | '.join(key)] = counts.get(' | '.join(key), 0) + 1
        out['counts'] = dict(sorted(counts.items()))
    out['seconds'] = round(time.time() - t0, 1)
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    json.dump(out, open(args.out, 'w'), indent=1, sort_keys=True, default=list)
    print(json.dumps(out.get('counts', {})), out['seconds'], flush=True)


if __name__ == '__main__':
    main()
