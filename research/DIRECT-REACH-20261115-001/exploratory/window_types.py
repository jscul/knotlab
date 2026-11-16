"""Closed windows and their types across levels (DIRECT-REACH-20261115-001, exploratory, the thread's own code).

For a description (automaton, placements) and an address w, the window at w is the orbit O(w) of w under the placement's words,
with every child v0, v1 of the orbit, and every knot placed at an orbit address. Its knots involve only those addresses, so it is a
sub-pattern of the pattern at any depth N > |w|; a relation forced in the window (two addresses always equal, or always unequal) is
forced in the whole pattern, and a dead window kills the pattern. The type of w (the orbit with each word's target and section at
each orbit address, read from w) fixes the window up to renaming, and the type of wa is a function of the type of w and a; when the
orbit stays bounded the types form a finite automaton, so the windows at every level are finitely many, all checked here.

Downward ties (an address forced equal or unequal to an address one level below, inside a window) then compose into chains; a cycle
of downward ties among the types gives a chain from a level to every deeper level, so, where the pattern is alive at every depth,
a bond of two members joining level k to level k + s for every s and every depth (L = 2), without any monotonicity in N.
"""
import gzip
import itertools
import json
import sys
from collections import deque
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
CENSUS = ROOT / 'artifacts/LEVEL-REACH-20261114-001A/LEVEL-REACH-20261114-001A-E001_level_reach/records_slim.jsonl.gz'


def words(s):
    return [()] + [(q,) for q in range(s)] + [(q, r) for q in range(s) for r in range(s)]


def step_word(aut, ws, b):
    """ws: the word's current maps left to right (applied right to left). Returns (output letter, sections)."""
    sw, d0, d1 = aut
    c, new = b, list(ws)
    for i in range(len(ws) - 1, -1, -1):
        q = ws[i]
        new[i] = d0[q] if c == 0 else d1[q]
        c ^= sw[q]
    return c, tuple(new)


class Description:
    def __init__(self, key):
        s, sw, d0, d1, placements = key
        self.aut = (tuple(sw), tuple(d0), tuple(d1))
        W = words(s)
        self.placements = sorted({tuple(sorted(p)) for p in placements})
        self.used = sorted({t // 3 for p in self.placements for t in p})
        self.maps = [W[i] for i in self.used]          # map index -> word
        self.slot_map = {i: k for k, i in enumerate(self.used)}

    def root_type(self):
        return self.canon([[(0, m) for m in self.maps]], 0)

    def canon(self, elems, root):
        """elems[i][k] = (target index, section word of map k at element i). BFS relabel from root."""
        order, seen = [root], {root: 0}
        for i in order:
            for tgt, _ in elems[i]:
                if tgt not in seen:
                    seen[tgt] = len(order)
                    order.append(tgt)
        return tuple(tuple((seen[t], sec) for t, sec in elems[i]) for i in order)

    def child(self, T, a):
        """Type of (root of T)·a."""
        idx, elems, dq = {(0, a): 0}, [], deque([(0, a)])
        while dq:
            i, b = dq.popleft()
            row = []
            for k in range(len(self.maps)):
                tgt, sec = T[i][k]
                out, nsec = step_word(self.aut, sec, b)
                node = (tgt, out)
                if node not in idx:
                    idx[node] = len(idx)
                    dq.append(node)
                row.append((node, nsec))
            elems.append(row)
        order = list(idx)
        return self.canon([[(idx[n], sec) for n, sec in row] for row in elems], 0), order

    def reroot(self, T, j):
        return self.canon([list(r) for r in T], j)

    def window(self, T):
        """Variables 0..m-1 the orbit, m + 2i + b the child (i, b). Knot rows of distinct members."""
        m = len(T)
        knots = set()
        for i in range(m):
            for p in self.placements:
                mem = []
                for t in p:
                    wi, slot = divmod(t, 3)
                    j = T[i][self.slot_map[wi]][0]
                    mem.append(j if slot == 0 else m + 2 * j + slot - 1)
                if len(set(mem)) == 3:
                    knots.add(tuple(sorted(mem)))
        return 3 * m, sorted(knots)


def window_states(nv, knots):
    if nv > 24:
        return None
    X = ((np.arange(1 << nv, dtype=np.int64)[:, None] >> np.arange(nv)) & 1).astype(np.int8)
    ok = np.ones(len(X), dtype=bool)
    for a, b, c in knots:
        s = X[:, a] + X[:, b] + X[:, c]
        ok &= (s != 0) & (s != 3)
    return X[ok]


def forced_pairs(S):
    """Pairs (u, v, sign) with u XOR v constant (sign 0 equal, 1 unequal)."""
    if S is None or len(S) == 0:
        return None
    out = []
    nv = S.shape[1]
    for u in range(nv):
        d = S ^ S[:, [u]]
        const = np.all(d == d[0], axis=0)
        for v in range(u + 1, nv):
            if const[v]:
                out.append((u, v, int(d[0, v])))
    return out


def explore(key, max_types=4000, max_orbit=8):
    D = Description(key)
    root = D.root_type()
    types, level_of, dq = {root: 0}, {root: {0}}, deque([root])
    edges = {}
    while dq:
        T = dq.popleft()
        if len(T) > max_orbit:
            return dict(status='orbit>%d' % max_orbit)
        kids = []
        for a in (0, 1):
            C, _ = D.child(T, a)
            kids.append(C)
            if C not in types:
                if len(types) >= max_types:
                    return dict(status='types>%d' % max_types)
                types[C] = len(types)
                dq.append(C)
        edges[T] = kids
    # levels at which each type occurs, as a set of (residue) is not needed: record first level and periodic reach
    info = {}
    downward = {}
    dead_types = []
    for T in types:
        nv, knots = D.window(T)
        S = window_states(nv, knots)
        if S is not None and len(S) == 0:
            dead_types.append(types[T])
            continue
        fp = forced_pairs(S)
        if fp is None:
            info[types[T]] = 'too big'
            continue
        m = len(T)
        down = []
        for u, v, sg in fp:
            if u == 0 and v >= m:            # root to a child (j, b)
                j, b = divmod(v - m, 2)
                C, _ = D.child(D.reroot(T, j), b)
                down.append((types[C], sg))
        downward[types[T]] = down
    # levels: the set of types at level n, from the root, until it repeats (finite automaton)
    lv, seen_sets, n = [frozenset([root])], {}, 0
    while lv[-1] not in seen_sets:
        seen_sets[lv[-1]] = n
        nxt = frozenset(C for T in lv[-1] for C in edges[T])
        lv.append(nxt)
        n += 1
    start, period = seen_sets[lv[-1]], n - seen_sets[lv[-1]]
    # does an infinite downward tie path start from a type at level k? (a cycle of downward ties reachable from it)
    G = {t: [c for c, _ in downward.get(t, [])] for t in range(len(types))}
    on_cycle = set()
    # nodes from which an infinite path exists: iterate removal of sinks
    alive = set(G)
    changed = True
    while changed:
        changed = False
        for t in list(alive):
            if not any(c in alive for c in G[t]):
                alive.discard(t)
                changed = True
    def infinite_from_level(k):
        Lk = lv[k] if k < len(lv) else lv[start + (k - start) % period]
        return any(types[T] in alive for T in Lk)
    return dict(status='finite', n_types=len(types), max_orbit=max(len(T) for T in types), dead_types=dead_types,
                levels_start=start, levels_period=period,
                infinite_tie_chain_from=[k for k in range(0, 8) if infinite_from_level(k)],
                n_types_with_down_ties=sum(1 for t in downward if downward[t]))


def population_D():
    with gzip.open(CENSUS, 'rt') as f:
        rows = sorted((json.loads(l) for l in f), key=lambda r: r['case'])
    out = []
    for r in rows:
        prof = [x['L_N'] for x in r['levels']]
        if r['union'] == 'alive' and prof in ([2] * 4, [3] * 4, [3, 3, 4, 4]):
            out.append((r['case'], r['key'], prof, r['classes']['relative']['class']))
    return out


if __name__ == '__main__':
    pop = population_D()
    lim = int(sys.argv[1]) if len(sys.argv) > 1 else len(pop)
    summary = {}
    for cid, key, prof, cls in pop[:lim]:
        r = explore(key)
        tag = (str(prof), r['status'], bool(r.get('infinite_tie_chain_from')) and 3 in r.get('infinite_tie_chain_from', []),
               bool(r.get('dead_types')))
        summary[tag] = summary.get(tag, 0) + 1
        print(cid[:12], prof, cls, json.dumps(r), flush=True)
    print('SUMMARY (profile, types, infinite tie chain from level 3, a dead window):')
    for k, v in sorted(summary.items()):
        print(' ', k, v)
