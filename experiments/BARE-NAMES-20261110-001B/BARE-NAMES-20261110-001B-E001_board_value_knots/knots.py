"""The frozen census of BARE-NAMES-20261110-001B: which one-bit count laws knot the board with the values.

Names are a countable set with no letters. A state gives each name a value s(u) in {0, 1} and each pair of names a neighbour
distinction n(u, v). A count law S, one of the 1,024 Life-like laws (key L<m>, m = sum of 2^(5c + k) over S), allows a state when
every place has exactly four neighbours and its pair (c, k), c its value and k its number of neighbours with value 1, is in S.

For each law:
  types     the pairs (c, k) that occur in some allowed state: the greatest subset T of S in which every pair has, for each
            neighbour value it needs, a pair of that value in T that accepts a neighbour of value c. A tree built greedily realizes
            every pair of T, and the universal cover of any allowed board is allowed (ticket A, target 3);
  V, E      the values that occur, and the unordered value pairs that occur on an edge;
  relation  the joint states of (n(u, v), s(u), s(v)) over all allowed states: (0, a, b) for a, b in V (disjoint unions of
            allowed boards are allowed), (1, a, b) for {a, b} in E;
  knot      K1-K3 on that relation, with the two values as the loops' distinctions and the neighbour distinction as the contact,
            decided by knotlab's checker;
  native    for the first law of each knot shape with a board in the frozen list, target 5's switch (flips n(u, v)) and swap
            (flips s(u) and s(v)) carried out on two disjoint copies of the board and checked place by place against the law.

Usage: knots.py [--out FILE] [--controls-only]
"""
import argparse
import itertools
import json
import os
import subprocess
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
SLUG = 'BARE-NAMES-20261110-001B-E001_board_value_knots'
DEFAULT_OUT = os.path.join(ROOT, 'artifacts', 'BARE-NAMES-20261110-001B', SLUG, 'knots.json')

PAIRS = [(c, k) for c in (0, 1) for k in range(5)]


def law(m):
    return {(c, k) for (c, k) in PAIRS if (m >> (5 * c + k)) & 1}


def accepts(t, c):
    """A place of pair t can have a neighbour of value c."""
    return t[1] >= 1 if c == 1 else t[1] <= 3


def needs(t):
    """The neighbour values a place of pair t has."""
    return [b for b in (0, 1) if (t[1] >= 1 if b == 1 else t[1] <= 3)]


def types(S):
    T = set(S)
    changed = True
    while changed:
        changed = False
        for t in list(T):
            if any(not any(u[0] == b and accepts(u, t[0]) for u in T) for b in needs(t)):
                T.discard(t)
                changed = True
    return T


def values_and_edges(T):
    V = sorted({t[0] for t in T})
    E = sorted({tuple(sorted((t[0], b))) for t in T for b in needs(t)})
    return V, E


def relation(V, E):
    R = {(0, a, b) for a in V for b in V}
    R |= {(1, a, b) for a in V for b in V if tuple(sorted((a, b))) in E}
    return sorted(R)


def cnf_of(R):
    """Clauses excluding every triple (N, A, B) outside R."""
    clauses = []
    for (n, a, b) in itertools.product((0, 1), repeat=3):
        if (n, a, b) not in R:
            lits = [('~' if v else '') + name for v, name in ((n, 'N'), (a, 'A'), (b, 'B'))]
            clauses.append(' '.join(lits))
    return '; '.join(clauses)


def knotlab(cnf):
    if not cnf:
        return {'is_knot': False, 'note': 'unconstrained'}
    out = subprocess.run([sys.executable, '-B', '-m', 'knotlab', 'check', '--cnf', cnf, '--loops', 'A', 'B', '--contact', 'N',
                          '--json'], capture_output=True, text=True, cwd=ROOT, env={**os.environ, 'PYTHONPATH': 'tools'})
    return json.loads(out.stdout)


# --- the frozen list of explicit finite boards (simple 4-regular graphs) ---------------------------------------------------

def torus(m, n):
    idx = lambda i, j: (i % m) * n + (j % n)
    return [sorted({idx(i + 1, j), idx(i - 1, j), idx(i, j + 1), idx(i, j - 1)}) for i in range(m) for j in range(n)]


def circulant(n, a):
    return [sorted({(i + 1) % n, (i - 1) % n, (i + a) % n, (i - a) % n}) for i in range(n)]


def board_list():
    boards = []
    for (m, n) in ((3, 3), (3, 4), (3, 5), (4, 4)):
        boards.append(('torus %dx%d' % (m, n), torus(m, n)))
    for n in range(5, 15):
        for a in range(2, (n + 1) // 2):
            if 2 * a != n:
                boards.append(('circulant C%d(1,%d)' % (n, a), circulant(n, a)))
    for name, adj in boards:
        assert all(len(nb) == 4 and v not in nb for v, nb in enumerate(adj)), name
        assert all(v in adj[w] for v, nb in enumerate(adj) for w in nb), name
    return boards


def colourings(adj, S):
    """All colourings of a board allowed by S, as rows of a 0/1 array (numpy, every colouring checked)."""
    n = len(adj)
    A = np.zeros((n, n), dtype=np.int64)
    for v, nb in enumerate(adj):
        A[v, nb] = 1
    cols = ((np.arange(1 << n)[:, None] >> np.arange(n)[None, :]) & 1).astype(np.int64)
    k = cols @ A.T
    code = 5 * cols + k
    ok = np.zeros(10, dtype=bool)
    for (c, kk) in S:
        ok[5 * c + kk] = True
    good = ok[code].all(axis=1)
    return cols[good]


def allowed_state(adj, col, S):
    n = len(adj)
    for v in range(n):
        nb = adj[v]
        if len(nb) != 4 or len(set(nb)) != 4 or v in nb:
            return False
        if any(v not in adj[w] for w in nb):
            return False
        if (col[v], sum(col[w] for w in nb)) not in S:
            return False
    return True


def native_moves(adj, col, S):
    """Target 5 on two disjoint copies: a switch of two edges of one value type flips n(u, v), and swapping u (or v) with a far
    place of the other value flips s(u) (or s(v)); every resulting state is checked against the law."""
    n = len(adj)
    adj2 = [list(nb) for nb in adj] + [[w + n for w in nb] for nb in adj]
    col2 = list(col) + list(col)
    assert allowed_state(adj2, col2, S)
    u, v = 0, adj[0][0]
    u2, v2 = u + n, v + n
    sw = [list(nb) for nb in adj2]
    sw[u] = sorted([w for w in sw[u] if w != v] + [v2])
    sw[v] = sorted([w for w in sw[v] if w != u] + [u2])
    sw[u2] = sorted([w for w in sw[u2] if w != v2] + [v])
    sw[v2] = sorted([w for w in sw[v2] if w != u2] + [u])
    switch_ok = allowed_state(sw, col2, S) and v not in sw[u]
    res = {'edge': [u, v], 'edge_type': [int(col[u]), int(col[v])], 'switch_flips_n': bool(switch_ok)}
    for name, x in (('u', u), ('v', v)):
        others = [w for w in range(n, 2 * n) if col2[w] != col2[x] and w not in adj2[x]]
        if not others:
            res['swap_flips_s(%s)' % name] = False
            continue
        w = others[0]
        perm = list(range(2 * n))
        perm[x], perm[w] = w, x
        adj3 = [None] * (2 * n)
        col3 = [None] * (2 * n)
        for p in range(2 * n):
            adj3[perm[p]] = sorted(perm[q] for q in adj2[p])
            col3[perm[p]] = col2[p]
        res['swap_flips_s(%s)' % name] = bool(allowed_state(adj3, col3, S) and col3[x] != col2[x])
    return res


def census(masks):
    rows = {}
    for m in masks:
        S = law(m)
        T = types(S)
        V, E = values_and_edges(T)
        R = relation(V, E) if T else []
        rows[m] = {'types': sorted(T), 'values': V, 'edges': E, 'relation': R}
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default=DEFAULT_OUT)
    ap.add_argument('--controls-only', action='store_true')
    args = ap.parse_args()
    t0 = time.time()
    no_adjacent_ones = sum(1 << (5 * 0 + k) for k in range(5)) + (1 << (5 * 1 + 0))
    controls = {'no adjacent 1s': no_adjacent_ones, 'full': (1 << 10) - 1, 'empty': 0}
    out = {'controls': {}}
    for name, m in controls.items():
        r = census([m])[m]
        r['knotlab'] = knotlab(cnf_of(r['relation'])) if r['relation'] else {'is_knot': False, 'note': 'no state'}
        out['controls'][name] = {'law': m, 'values': r['values'], 'edges': r['edges'],
                                 'is_knot': r['knotlab'].get('is_knot')}
    for name, adj in board_list():
        cols = [c for c in colourings(adj, law(no_adjacent_ones)) if 0 < c.sum() < len(c)]
        if cols:
            out['controls']['no adjacent 1s']['native'] = {'board': name, **native_moves(adj, list(cols[0]),
                                                                                         law(no_adjacent_ones))}
            break
    print('controls', json.dumps(out['controls']), flush=True)
    if not args.controls_only:
        rows = census(range(1 << 10))
        shapes = {}
        verdicts = {}
        for m, r in rows.items():
            if not r['relation']:
                r['shape'] = 'no state'
                continue
            cnf = cnf_of(r['relation'])
            if cnf not in verdicts:
                verdicts[cnf] = knotlab(cnf)
            kv = verdicts[cnf]
            r['cnf'] = cnf
            r['is_knot'] = bool(kv.get('is_knot'))
            r['shape'] = ('knot: no edge ' + ', '.join('%d%d' % e for e in ((0, 0), (0, 1), (1, 1)) if list(e) not in
                                                       [list(x) for x in r['edges']])) if r['is_knot'] else 'no knot'
            shapes.setdefault(r['shape'], []).append(m)
        boards = board_list()
        native = {}
        for shape, ms in sorted(shapes.items()):
            if not shape.startswith('knot'):
                continue
            found = None
            for m in ms:
                S = law(m)
                for name, adj in boards:
                    cols = colourings(adj, S)
                    both = [c for c in cols if 0 < c.sum() < len(c)]
                    if both:
                        found = (m, name, adj, both[0])
                        break
                if found:
                    break
            if found is None:
                native[shape] = {'law': None, 'note': 'no law of this shape has a two-valued board in the frozen list'}
                continue
            m, name, adj, col = found
            native[shape] = {'law': m, 'board': name, 'colouring': [int(x) for x in col], **native_moves(adj, list(col), law(m))}
        counts = {s: len(ms) for s, ms in sorted(shapes.items())}
        counts['no state'] = sum(1 for r in rows.values() if r['shape'] == 'no state')
        out['laws'] = rows
        out['counts'] = counts
        out['knot_verdicts'] = {c: {k: verdicts[c].get(k) for k in ('is_knot', 'allowed', 'minimum_width',
                                                                     'pairwise_definable')} for c in verdicts}
        out['native'] = native
        out['frozen_boards'] = [name for name, _ in boards]
    out['seconds'] = round(time.time() - t0, 1)
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    json.dump(out, open(args.out, 'w'), indent=1, sort_keys=True, default=list)
    print(json.dumps(out.get('counts', {})), json.dumps(out.get('native', {}))[:1500], out['seconds'], flush=True)


if __name__ == '__main__':
    main()
