"""Checks for WEAK-APER-20261110-001A: free solutions without finite boards.

1. Mirror invariance. The reflection k -> -k maps a level law S to S' = {(c, b, a) : (a, b, c) in S} and its solutions to the
   solutions of S', commuting with the action. So the census classes E, D, A, P and WA of S and S' must agree for all 32,768 laws,
   and so must the presence of an L1 certificate.
2. The undecided laws. Each contains (3, 0, 1), and its mirror is classed -L2. The mirrored horofunction -b_xi mod 3 has the triple
   (3, 0, 1) at every place of a ball; for xi = x^oo its stabilizer up to length 6 is {x^3j}, and for a generic-looking end no
   element up to length 6 fixes it.
3. Exact balance verdicts. Every law the census put through the balance program is re-decided in rational arithmetic, on tree
   patterns pruned by code independent of the census:
     WA  by a potential y (a Farkas certificate) under which every tree pattern gains at least 1:
         gain(p) = sum over g in {x, y} of y_g(p_0, p_g) - y_g(p_{g^-1}, p_0). Over a finite board the gains telescope to 0;
     A   by an explicit finite board built from a rational balanced solution with positive weight on branching patterns
         (target 1's construction), checked place by place against the law;
     P   by an explicit finite board, and a potential with every gain >= 0 and every branching pattern's gain >= 1, so that no
         finite board uses a branching pattern.
4. Small boards. Every board with at most 4 places that carries a solution of a law agrees with its class (never E or WA).
5. Drift (target 6, found after the census). A law is in class WA exactly when every tree pattern has more neighbours one level
   up than one level down, or every one more down than up.

Usage: check.py [--limit N]   (N laws only, for timing)
"""
import argparse
import importlib.util
import itertools
import json
import math
import os
import random
import time
from collections import defaultdict
from fractions import Fraction

import numpy as np
from scipy.optimize import linprog

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
SLUG_B = 'WEAK-APER-20261110-001B-E001_level_laws_on_three_values'
CENSUS_PY = os.path.join(ROOT, 'experiments', 'WEAK-APER-20261110-001B', SLUG_B, 'census.py')
CENSUS_JSON = os.path.join(ROOT, 'artifacts', 'WEAK-APER-20261110-001B', SLUG_B, 'census.json')
OUT = os.path.join(HERE, 'result.json')

_spec = importlib.util.spec_from_file_location('census', CENSUS_PY)
census = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(census)

Q = 3
INV = (1, 0, 3, 2)                       # letters x, X, y, Y
TRIPLES = census.TRIPLES                 # the census's bit order
TIDX = {t: i for i, t in enumerate(TRIPLES)}
MIRROR = [TIDX[(c, b, a)] for (a, b, c) in TRIPLES]
PATTERNS = list(itertools.product(range(Q), repeat=5))


def triple(p):
    c = p[0]
    a = sum(1 for v in p[1:] if v == (c - 1) % Q)
    b = sum(1 for v in p[1:] if v == c)
    return (a, b, 4 - a - b)


PAT_T = [TIDX[triple(p)] for p in PATTERNS]


def law(m):
    return {TRIPLES[i] for i in range(15) if (m >> i) & 1}


def mirror(m):
    return sum(1 << MIRROR[i] for i in range(15) if (m >> i) & 1)


def coarse(c):
    return c.split('-')[0]


# --- tree patterns, pruned independently of census.py ---------------------------------------------------------------------

def need_keys(p):
    """The g-neighbour of p must be a pattern q with (q_0, q_{g^-1}) = (p_g, p_0)."""
    return [(g, p[1 + g], p[0]) for g in range(4)]


def offer_keys(q):
    return [(g, q[0], q[1 + INV[g]]) for g in range(4)]


def tree_patterns(m):
    pats = [p for p, t in zip(PATTERNS, PAT_T) if (m >> t) & 1]
    offers = defaultdict(int)
    needers = defaultdict(list)
    for p in pats:
        for k in offer_keys(p):
            offers[k] += 1
        for k in need_keys(p):
            needers[k].append(p)
    dead = set()
    stack = [p for p in pats if any(offers[k] == 0 for k in need_keys(p))]
    while stack:
        p = stack.pop()
        if p in dead:
            continue
        dead.add(p)
        for k in offer_keys(p):
            offers[k] -= 1
            if offers[k] == 0:
                stack.extend(r for r in needers[k] if r not in dead)
    return [p for p in pats if p not in dead]


def branching(P):
    keys = defaultdict(int)
    for q in P:
        for k in offer_keys(q):
            keys[k] += 1
    return {p for p in P if any(keys[k] >= 2 for k in need_keys(p))}


# --- the balance program, decided exactly ---------------------------------------------------------------------------------

ROWS = [(g, a, b) for g in (0, 2) for a in range(Q) for b in range(Q)]
RIDX = {r: i for i, r in enumerate(ROWS)}


def balance_matrix(P):
    """Rows (g, a, b), one column per pattern: +1 where its g-edge leaves with values (a, b), -1 where its g^-1-edge arrives
    with them. A balanced n (M n = 0) is the pattern count of a finite board (target 1)."""
    M = [[0] * len(P) for _ in ROWS]
    for j, p in enumerate(P):
        for g in (0, 2):
            M[RIDX[(g, p[0], p[1 + g])]][j] += 1
            M[RIDX[(g, p[1 + INV[g]], p[0])]][j] -= 1
    return M


def gains(M, y):
    return [sum(M[i][j] * y[i] for i in range(len(M)) if M[i][j]) for j in range(len(M[0]))]


def potential(M, strict):
    """A rational y with gain_j >= 1 where strict[j] and >= 0 elsewhere, or None. HiGHS maximizes a common margin t <= 1 with
    |y| <= 100; the answer is rounded and then verified exactly."""
    m, n = len(M), len(M[0])
    A_ub = [[-M[i][j] for i in range(m)] + [1.0 if strict[j] else 0.0] for j in range(n)]
    res = linprog([0.0] * m + [-1.0], A_ub=A_ub, b_ub=[0.0] * n, bounds=[(-100, 100)] * m + [(None, 1.0)],
                  method='highs')
    if res.status != 0 or -res.fun < 1e-9:
        return None
    for den in (10 ** 3, 10 ** 6, 10 ** 9):
        y = [Fraction(v).limit_denominator(den) for v in res.x[:m]]
        gs = gains(M, y)
        if all(g >= 0 for g in gs) and all(gs[j] > 0 for j in range(n) if strict[j]):
            k = min(gs[j] for j in range(n) if strict[j])
            return [v / k for v in y]
    return None


def solve_exact(rows, rhs, cols):
    """Gauss-Jordan in rationals on the given columns; free columns set to 0. None if inconsistent."""
    A = [[Fraction(r[c]) for c in cols] + [Fraction(b)] for r, b in zip(rows, rhs)]
    k = len(cols)
    piv = []
    r = 0
    for c in range(k):
        pr = next((i for i in range(r, len(A)) if A[i][c] != 0), None)
        if pr is None:
            continue
        A[r], A[pr] = A[pr], A[r]
        inv = 1 / A[r][c]
        A[r] = [v * inv for v in A[r]]
        for i in range(len(A)):
            if i != r and A[i][c] != 0:
                f = A[i][c]
                A[i] = [vi - f * vr for vi, vr in zip(A[i], A[r])]
        piv.append(c)
        r += 1
        if r == len(A):
            break
    if any(A[i][k] != 0 for i in range(r, len(A))):
        return None
    sol = {cols[c]: Fraction(0) for c in range(k)}
    for i, c in enumerate(piv):
        sol[cols[c]] = A[i][k]
    return sol


def balanced(M, P, weight_on=None):
    """A rational balanced distribution from HiGHS's basic solution, solved exactly on its support (maximizing the weight on
    weight_on if given). Returns {column: Fraction} or None."""
    n = len(P)
    A_eq = np.array(M + [[1] * n], dtype=float)
    b_eq = np.zeros(len(A_eq))
    b_eq[-1] = 1.0
    c = np.zeros(n) if weight_on is None else np.array([-1.0 if p in weight_on else 0.0 for p in P])
    res = linprog(c, A_eq=A_eq, b_eq=b_eq, bounds=[(0, None)] * n, method='highs')
    if res.status != 0:
        return None
    supp = [j for j in range(n) if res.x[j] > 1e-9]
    sol = solve_exact(M + [[1] * n], [0] * len(M) + [1], supp)
    if sol is None or any(v < 0 for v in sol.values()):
        return None
    return {j: v for j, v in sol.items() if v > 0}


def board_from(sol, P, m):
    """Target 1's construction: places labelled by patterns, each letter's edges matched within each pair of values. Returns
    the board's size if every place's star is its label and allowed by the law, else None."""
    den = 1
    for v in sol.values():
        den = den * v.denominator // math.gcd(den, v.denominator)
    places = [j for j, v in sorted(sol.items()) for _ in range(int(v * den))]
    if len(places) > 200000:
        return None
    sigma = {}
    for g in (0, 2):
        outs, ins = defaultdict(list), defaultdict(list)
        for v, j in enumerate(places):
            p = P[j]
            outs[(p[0], p[1 + g])].append(v)
            ins[(p[1 + INV[g]], p[0])].append(v)
        s = [None] * len(places)
        for key, vs in outs.items():
            ws = ins.get(key, [])
            if len(ws) != len(vs):
                return None
            for v, w in zip(vs, ws):
                s[v] = w
        sigma[g] = s
    col = [P[j][0] for j in places]
    inv = {g: [None] * len(places) for g in (0, 2)}
    for g in (0, 2):
        for v, w in enumerate(sigma[g]):
            inv[g][w] = v
    for v, j in enumerate(places):
        star = (col[v], col[sigma[0][v]], col[inv[0][v]], col[sigma[2][v]], col[inv[2][v]])
        if star != P[j] or not (m >> TIDX[triple(star)]) & 1:
            return None
    return len(places)


# --- small boards ---------------------------------------------------------------------------------------------------------

def small_board_masks(max_places):
    """The sets of triples used by solutions on connected boards (pairs of permutations) of at most max_places places."""
    masks = set()
    for n in range(1, max_places + 1):
        perms = list(itertools.permutations(range(n)))
        for sx in perms:
            for sy in perms:
                seen, stack = {0}, [0]
                while stack:
                    v = stack.pop()
                    for w in (sx[v], sy[v], sx.index(v), sy.index(v)):
                        if w not in seen:
                            seen.add(w)
                            stack.append(w)
                if len(seen) < n:
                    continue
                ix = [sx.index(v) for v in range(n)]
                iy = [sy.index(v) for v in range(n)]
                for col in itertools.product(range(Q), repeat=n):
                    mk = 0
                    for v in range(n):
                        mk |= 1 << TIDX[triple((col[v], col[sx[v]], col[ix[v]], col[sy[v]], col[iy[v]]))]
                    masks.add(mk)
    minimal = [a for a in masks if not any(b != a and b & a == b for b in masks)]
    return sorted(minimal)


# --- the mirrored horofunction on a ball ----------------------------------------------------------------------------------

def reduce_word(w):
    out = []
    for g in w:
        if out and out[-1] == INV[g]:
            out.pop()
        else:
            out.append(g)
    return tuple(out)


def inverse(w):
    return tuple(INV[g] for g in reversed(w))


def ball(R):
    words, frontier = [()], [()]
    for _ in range(R):
        nxt = []
        for w in frontier:
            for g in range(4):
                if not w or w[-1] != INV[g]:
                    nxt.append(w + (g,))
        words += nxt
        frontier = nxt
    return words


def mirrored_horofunction(z, r_in, max_len):
    """s = -b_xi mod 3 for the end xi through the reduced word z, exact on words of length < |z|: the triples used at the
    places of radius <= r_in, and the elements of length 1..max_len with k.s = s on the ball of radius r_in."""
    N = len(z)
    assert N > r_in + max_len + 1

    def s(w):
        return (-(len(reduce_word(inverse(w) + z)) - N)) % Q

    used = set()
    for w in ball(r_in):
        k = s(w)
        nbs = [s(reduce_word(w + (g,))) for g in range(4)]
        used.add((sum(v == (k - 1) % Q for v in nbs), sum(v == k for v in nbs), sum(v == (k + 1) % Q for v in nbs)))
    inner = ball(r_in)
    values = {g: s(g) for g in inner}
    fixing = []
    for k in ball(max_len)[1:]:
        ki = inverse(k)
        if all(s(reduce_word(ki + g)) == values[g] for g in inner):
            fixing.append(''.join('xXyY'[g] for g in k))
    return sorted(used), sorted(fixing)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--limit', type=int, default=None)
    args = ap.parse_args()
    t0 = time.time()
    cen = json.load(open(CENSUS_JSON))
    cls = {int(k): v['class'] for k, v in cen['laws'].items()}
    masks = sorted(cls) if args.limit is None else sorted(cls)[:args.limit]
    out = {}

    # 1. mirror invariance
    bad = [m for m in masks if coarse(cls[m]) != coarse(cls[mirror(m)])
           or (cls[m].endswith('L1') != cls[mirror(m)].endswith('L1'))]
    out['1_mirror'] = {'laws': len(masks), 'disagreements': bad, 'pass': not bad}

    # 2. the undecided laws and the mirrored horofunction
    und = cen['undecided']
    rows = [{'law': m, 'class': cls[m], 'contains_301': bool((m >> TIDX[(3, 0, 1)]) & 1), 'mirror': mirror(m),
             'mirror_class': cls[mirror(m)]} for m in und]
    used_x, fix_x = mirrored_horofunction((0,) * 24, 10, 6)
    rng = random.Random(20261110)
    z = []
    while len(z) < 24:
        g = rng.randrange(4)
        if not z or z[-1] != INV[g]:
            z.append(g)
    used_g, fix_g = mirrored_horofunction(tuple(z), 10, 6)
    ok2 = (all(r['contains_301'] and r['mirror_class'].endswith('-L2') for r in rows)
           and used_x == [(3, 0, 1)] and used_g == [(3, 0, 1)] and fix_x == ['XXX', 'XXXXXX', 'xxx', 'xxxxxx']
           and fix_g == [])
    out['2_undecided'] = {'laws': rows, 'end_x_triples': used_x, 'end_x_fixing_up_to_6': fix_x,
                          'generic_end': ''.join('xXyY'[g] for g in z), 'generic_triples': used_g,
                          'generic_fixing_up_to_6': fix_g, 'pass': ok2}
    print('mirror', out['1_mirror']['pass'], 'undecided', ok2, round(time.time() - t0, 1), flush=True)

    # 3. exact balance verdicts
    tally = defaultdict(int)
    failures = []
    max_board = 0
    max_den = 1
    drift = defaultdict(int)
    drift_bad = []
    for count, m in enumerate(masks):
        c = cls[m]
        if c in ('E', 'D'):
            P = tree_patterns(m)
            if (c == 'E') != (not P) or (c == 'D' and branching(P)):
                failures.append([m, c, 'pruning disagrees'])
            tally[c + ' recomputed'] += 1
            continue
        P = tree_patterns(m)
        Br = branching(P)
        M = balance_matrix(P)
        tr = {triple(p) for p in P}
        way = 'up' if all(t[2] > t[0] for t in tr) else 'down' if all(t[0] > t[2] for t in tr) else 'none'
        drift[(coarse(c), way)] += 1
        if (way != 'none') != (coarse(c) == 'WA'):
            drift_bad.append(m)
        if coarse(c) == 'WA':
            y = potential(M, [True] * len(P))
            if y is None:
                failures.append([m, c, 'no exact potential'])
            else:
                max_den = max(max_den, max(v.denominator for v in y))
                tally['WA potential'] += 1
        elif c == 'A':
            sol = balanced(M, P, weight_on=Br)
            size = board_from(sol, P, m) if sol else None
            if size is None or not any(P[j] in Br for j in sol):
                failures.append([m, c, 'no exact board with a branching pattern'])
            else:
                max_board = max(max_board, size)
                tally['A board'] += 1
        else:
            sol = balanced(M, P)
            size = board_from(sol, P, m) if sol else None
            y = potential(M, [p in Br for p in P])
            if size is None or y is None:
                failures.append([m, c, 'no exact board or potential'])
            else:
                tally['P board and potential'] += 1
        if count % 4096 == 4095:
            print(count + 1, dict(tally), len(failures), round(time.time() - t0, 1), flush=True)
    out['3_exact'] = {'tally': dict(tally), 'failures': failures, 'largest_board': max_board,
                      'largest_potential_denominator': max_den, 'pass': not failures}
    out['5_drift'] = {'class_and_drift': {'%s %s' % k: v for k, v in sorted(drift.items())}, 'disagreements': drift_bad,
                      'pass': not drift_bad}

    # 4. small boards
    minimal = small_board_masks(4)
    clash = []
    with_board = defaultdict(int)
    for m in masks:
        if any(mk & ~m == 0 for mk in minimal):
            with_board[coarse(cls[m])] += 1
            if coarse(cls[m]) in ('E', 'WA'):
                clash.append(m)
    out['4_small_boards'] = {'max_places': 4, 'minimal_triple_sets': len(minimal), 'laws_with_a_board_by_class': dict(with_board),
                             'clashes': clash, 'pass': not clash}
    out['pass'] = all(v['pass'] for k, v in out.items() if isinstance(v, dict) and 'pass' in v)
    out['status'] = 'passed' if out['pass'] else 'failed'
    out['seconds'] = round(time.time() - t0, 1)
    if args.limit is None:
        json.dump(out, open(OUT, 'w'), indent=1, sort_keys=True, default=list)
    print(json.dumps({k: (v['pass'] if isinstance(v, dict) else v) for k, v in out.items()}), flush=True)


if __name__ == '__main__':
    main()
