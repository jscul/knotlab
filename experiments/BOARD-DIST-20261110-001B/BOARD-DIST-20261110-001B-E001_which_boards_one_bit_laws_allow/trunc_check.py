"""Second code for BOARD-DIST-20261110-001B (B4), written without board_lib: the truncated CNF on the
ball of names B_L, read by a SAT solver, as backlog B92 first proposed.

Variables: s(u) for every name u in B_L; e(u, v) for every pair of names (free-board queries only).
Clauses: transitivity of e, letter closure e(u, v) -> e(ug, vg) when ug and vg lie in the ball,
constancy e(u, v) -> (s(u) <-> s(v)), and the law at every name whose four neighbours lie in the ball.

Usage: trunc_check.py [--fixed-L 6] [--free-L 4] [--out FILE]
"""
import argparse
import itertools
import json
import os
import sys
import time

from pysat.solvers import Minisat22

INVERSE = {'x': 'X', 'X': 'x', 'y': 'Y', 'Y': 'y'}
C_WORD = 'xyXY'


def times(u, g):
    return u[:-1] if u and u[-1] == INVERSE[g] else u + g


def ball(L):
    words, layer = [''], ['']
    for _ in range(L):
        layer = [w + g for w in layer for g in 'xXyY' if not (w and w[-1] == INVERSE[g])]
        words.extend(layer)
    return words


def inverse(u):
    return ''.join(INVERSE[g] for g in reversed(u))


def reduce_word(w):
    out = []
    for g in w:
        if out and out[-1] == INVERSE[g]:
            out.pop()
        else:
            out.append(g)
    return ''.join(out)


LAWS = {
    'parity0': lambda c, x, X, y, Y: (c + x + X + y + Y) % 2 == 0,
    'parity1': lambda c, x, X, y, Y: (c + x + X + y + Y) % 2 == 1,
    'atom': lambda c, x, X, y, Y: (not (x and y)) or c == 1,
}
FORBIDDEN = {k: [v for v in itertools.product((0, 1), repeat=5) if not f(*v)] for k, f in LAWS.items()}


def exps(u):
    return (u.count('x') - u.count('X'), u.count('y') - u.count('Y'))


def is_power_of_c(w):
    if w == '':
        return True
    for base in (C_WORD, inverse(C_WORD)):
        if len(w) % 4 == 0 and w == base * (len(w) // 4):
            return True
    return False


BOARDS = {
    'tree': lambda u: u,
    'plane': exps,
    'line(1,0)': lambda u: exps(u)[0],
    'line(1,1)': lambda u: sum(exps(u)),
    'collapse': lambda u: 0,
}


def classes(names, board):
    """Class index of each name under a named board; Sch(<c>) by union-find on u v^-1 in <c>."""
    if board != 'Sch(<c>)':
        key = BOARDS[board]
        ids = {}
        return {u: ids.setdefault(key(u), len(ids)) for u in names}
    parent = {u: u for u in names}

    def find(u):
        while parent[u] != u:
            parent[u] = parent[parent[u]]
            u = parent[u]
        return u
    for u, v in itertools.combinations(names, 2):
        if is_power_of_c(reduce_word(u + inverse(v))):
            parent[find(u)] = find(v)
    ids = {}
    return {u: ids.setdefault(find(u), len(ids)) for u in names}


def fixed_board(law, L, board):
    """With the board fixed: is there an allowed state, and which (s(1), s(c)) pairs occur?"""
    names = ball(L)
    cls = classes(names, board)
    s = Minisat22()
    for u in names:
        if len(u) <= L - 1:
            cells = [cls[u]] + [cls[times(u, g)] for g in 'xXyY']
            for p in FORBIDDEN[law]:
                clause = set()
                taut = False
                for cell, val in zip(cells, p):
                    lit = -(cell + 1) if val else (cell + 1)
                    if -lit in clause:
                        taut = True
                        break
                    clause.add(lit)
                if not taut:
                    s.add_clause(sorted(clause))
    sat = s.solve()
    pairs = []
    if sat and L >= 4:
        a_var, c_var = cls[''] + 1, cls[C_WORD] + 1
        for a in (0, 1):
            for b in (0, 1):
                if a_var == c_var and a != b:
                    continue
                assum = [a_var if a else -a_var] + ([] if a_var == c_var else [c_var if b else -c_var])
                if s.solve(assumptions=assum):
                    pairs.append([a, b])
    s.delete()
    return sat, pairs


def free_board(law, L, ioi1=False):
    """The full truncated CNF with the board free. Returns the projection onto (e(1, c), s(1), s(c)),
    and with IoI1 also whether the tree board and whether any state is allowed."""
    names = ball(L)
    idx = {u: i for i, u in enumerate(names)}
    N = len(names)
    sv = lambda u: idx[u] + 1
    pid = {}
    for i in range(N):
        for j in range(i + 1, N):
            pid[(i, j)] = N + 1 + len(pid)

    def ev(u, v):
        i, j = idx[u], idx[v]
        return pid[(i, j) if i < j else (j, i)]
    s = Minisat22()
    for i, j, k in itertools.combinations(range(N), 3):
        a, b, c = pid[(i, j)], pid[(i, k)], pid[(j, k)]
        s.add_clause([-a, -b, c])
        s.add_clause([-a, -c, b])
        s.add_clause([-b, -c, a])
    ball_set = set(names)
    for i, j in pid:
        u, v = names[i], names[j]
        e = pid[(i, j)]
        s.add_clause([-e, -sv(u), sv(v)])
        s.add_clause([-e, sv(u), -sv(v)])
        for g in 'xXyY':
            ug, vg = times(u, g), times(v, g)
            if ug in ball_set and vg in ball_set:
                s.add_clause([-e, ev(ug, vg)])
    inner = [u for u in names if len(u) <= L - 1]
    for u in inner:
        cells = [sv(u)] + [sv(times(u, g)) for g in 'xXyY']
        for p in FORBIDDEN[law]:
            s.add_clause([-c if val else c for c, val in zip(cells, p)])
    if ioi1:
        allowed_views = [v for v in itertools.product((0, 1), repeat=5) if LAWS[law](*v)]
        for u, v in itertools.combinations(inner, 2):
            cu = [sv(u)] + [sv(times(u, g)) for g in 'xXyY']
            cv = [sv(v)] + [sv(times(v, g)) for g in 'xXyY']
            for t in allowed_views:
                s.add_clause([-c if val else c for c, val in zip(cu, t)] +
                             [-c if val else c for c, val in zip(cv, t)] + [ev(u, v)])
    out = {}
    if ioi1:
        out['any'] = s.solve()
        out['tree'] = s.solve(assumptions=[-e for e in pid.values()])
    else:
        rel = []
        e1c, s1, sc = ev('', C_WORD), sv(''), sv(C_WORD)
        for e in (0, 1):
            for a in (0, 1):
                for b in (0, 1):
                    if s.solve(assumptions=[e1c if e else -e1c, s1 if a else -s1, sc if b else -sc]):
                        rel.append([e, a, b])
        out['relation'] = rel
    s.delete()
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--fixed-L', type=int, default=6)
    ap.add_argument('--free-L', type=int, default=4)
    ap.add_argument('--out', default=None)
    args = ap.parse_args()
    t0 = time.time()
    res = {'fixed_L': args.fixed_L, 'free_L': args.free_L, 'laws': {}}
    for law in LAWS:
        r = {}
        for board in list(BOARDS) + ['Sch(<c>)']:
            sat, pairs = fixed_board(law, args.fixed_L, board)
            r[board] = {'allowed': sat, 'pairs': pairs}
        if args.free_L:
            r['free'] = free_board(law, args.free_L)
            r['free_ioi1'] = free_board(law, args.free_L, ioi1=True)
        res['laws'][law] = r
        print(law, json.dumps(r), '%.1fs' % (time.time() - t0), flush=True)
    res['seconds'] = round(time.time() - t0, 1)
    if args.out:
        with open(args.out, 'w') as fh:
            json.dump(res, fh, indent=1, sort_keys=True)


if __name__ == '__main__':
    main()
