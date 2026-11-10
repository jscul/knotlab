"""Stress test S2 of BOARD-DIST-20261110-001B: identity of indiscernibles at radius 2 for parity 0,
parity 1 and the atom, one size past the radius-1 census.

A finite board is an IoI2 board of a law when some colouring satisfies the law at every place and gives
distinct places distinct radius-2 views (the values at the 17 names u g, g a reduced word of length at
most 2). For each law: which tori Z_m x Z_n (3 <= m <= n <= 9) are IoI2 boards (plane-like and abelian),
and how many boards of a frozen non-abelian list are.

Usage: ioi2_stress.py [--out FILE]
"""
import argparse
import json
import os
import random
import sys
import time

from pysat.solvers import Minisat22

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import board_lib as bl  # noqa: E402

WORDS2 = [()]
for g in range(4):
    WORDS2.append((g,))
for g in range(4):
    for h in range(4):
        if h != bl.INV[g]:
            WORDS2.append((g, h))
assert len(WORDS2) == 17


def gens(board):
    sx, sy = board
    return (sx, bl._inverse(sx), sy, bl._inverse(sy))


def ioi2_colouring(L, board):
    """A colouring with the law at every place and distinct radius-2 views, or None."""
    G = gens(board)
    n = len(board[0])
    at = [[None] * 17 for _ in range(n)]
    for p in range(n):
        for i, w in enumerate(WORDS2):
            q = p
            for g in w:
                q = G[g][q]
            at[p][i] = q
    s = Minisat22()
    forb = [p for p in range(32) if not (L >> p) & 1]
    for p in range(n):
        cells = [p, G[0][p], G[1][p], G[2][p], G[3][p]]
        for pat in forb:
            lits = set()
            taut = False
            for t, c in enumerate(cells):
                lit = -(c + 1) if (pat >> t) & 1 else (c + 1)
                if -lit in lits:
                    taut = True
                    break
                lits.add(lit)
            if not taut:
                s.add_clause(sorted(lits))
    top = n
    for p in range(n):
        for q in range(p + 1, n):
            ds = []
            for i in range(17):
                a, b = at[p][i], at[q][i]
                if a == b:
                    continue
                top += 1
                s.add_clause([-top, a + 1, b + 1])
                s.add_clause([-top, -(a + 1), -(b + 1)])
                ds.append(top)
            s.add_clause(ds)
    if not s.solve():
        s.delete()
        return None
    model = s.get_model()
    s.delete()
    return [1 if model[p] > 0 else 0 for p in range(n)]


def check_colouring(L, board, col):
    G = gens(board)
    n = len(col)
    views = set()
    for p in range(n):
        if not (L >> bl.pattern(col[p], col[G[0][p]], col[G[1][p]], col[G[2][p]], col[G[3][p]])) & 1:
            return False
        v = []
        for w in WORDS2:
            q = p
            for g in w:
                q = G[g][q]
            v.append(col[q])
        views.add(tuple(v))
    return len(views) == n


def plane_like(board):
    sx, sy = board
    six, siy = bl._inverse(sx), bl._inverse(sy)
    return all(len({p, sx[p], six[p], sy[p], siy[p]}) == 5 for p in range(len(sx)))


def frozen_boards(seed=92):
    tori = [((m, n), bl.torus(m, 0, n)) for m in range(3, 10) for n in range(m, 10)]
    nonab = [b for b in bl.finite_boards(7) if plane_like(b) and not bl.is_abelian(*b)]
    rng = random.Random(seed)
    rand = []
    for size in (8, 12, 16, 24, 32):
        got = 0
        while got < 30:
            sx = list(range(size))
            sy = list(range(size))
            rng.shuffle(sx)
            rng.shuffle(sy)
            c = bl.canon(tuple(sx), tuple(sy))
            if c is None or bl.is_abelian(c[1], c[2]):
                continue
            rand.append((c[1], c[2]))
            got += 1
    return tori, nonab, rand


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default=None)
    args = ap.parse_args()
    t0 = time.time()
    tori, nonab, rand = frozen_boards()
    laws = {'parity0': bl.lifelike_mask(bl.PARITY0), 'parity1': bl.lifelike_mask(bl.PARITY1), 'atom': bl.atom_mask()}
    res = {'boards': {'tori': len(tori), 'nonabelian_7': len(nonab), 'random_nonabelian': len(rand)}, 'laws': {}}
    for name, L in laws.items():
        r = {'tori_with_ioi2': [], 'nonabelian_with_ioi2': 0, 'bad': 0}
        for (mn, b) in tori:
            col = ioi2_colouring(L, b)
            if col is not None:
                r['tori_with_ioi2'].append(list(mn))
                r['bad'] += not check_colouring(L, b, col)
        for b in nonab + rand:
            col = ioi2_colouring(L, b)
            if col is not None:
                r['nonabelian_with_ioi2'] += 1
                r['bad'] += not check_colouring(L, b, col)
        r['prediction_holds'] = bool(r['tori_with_ioi2']) and r['nonabelian_with_ioi2'] > 0
        res['laws'][name] = r
        print(name, json.dumps(r), '%.1fs' % (time.time() - t0), flush=True)
    res['seconds'] = round(time.time() - t0, 1)
    if args.out:
        with open(args.out, 'w') as fh:
            json.dump(res, fh, indent=1, sort_keys=True)


if __name__ == '__main__':
    main()
