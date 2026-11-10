"""The frozen census of RIGID-WORLDS-20261110-001A: does a one-bit law with identity at radius 2 force a two-dimensional world?

Identity of indiscernibles at radius 2: two names whose radius-2 views (the values at the 17 names ug, g a reduced word of length
at most 2) agree are one place. The allowed boards are the finite boards with a colouring obeying the law at every place and giving
distinct places distinct radius-2 views (BOARD-DIST-20261110-001A, Theorem 7 and its remark).

A board is a two-dimensional torus when it is abelian, so Z^2/Lambda, and Lambda has no nonzero vector of L1 norm at most 4: then
every radius-2 ball of the board is the plane's (13 distinct places). A law forces a two-dimensional world when some board is
allowed and every allowed board is a two-dimensional torus.

Steps per law (frozen):
 1. Refutation by boards, in order, stopping at the first board allowed: the one-place board; every abelian board with at most 8
    places (all thick); every non-abelian board with at most 6 places; the 16 plane-like non-abelian boards with 7 places; 150
    random non-abelian boards of 8 to 32 places (seed 92); every thick torus Z^2/Lambda of index 9 to 64 with a nonzero vector of
    L1 norm 3 or 4. Parity laws are decided by linear algebra over GF(2), the others by SAT with a budget of 10^6 conflicts.
 2. For each law not refuted, the exact view-board search: is any board allowed, is a non-abelian board allowed, is a thick board
    allowed (a loop, or a word x^a y^b with 0 < |a| + |b| <= 4 closing at a place), each by SAT over the law's allowed views.
    A law with more than 3,000 allowed views is reported undecided.
 3. Reading: the two-dimensional tori of index at most 32 that each law allows.

Usage: rigid.py [--out FILE] [--controls-only]
"""
import argparse
import itertools
import json
import os
import random
import sys
import time

import numpy as np
from pysat.solvers import Minisat22
from pysat.card import CardEnc, EncType

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
BD = os.path.join(ROOT, 'experiments', 'BOARD-DIST-20261110-001B', 'BOARD-DIST-20261110-001B-E001_which_boards_one_bit_laws_allow')
sys.path.insert(0, BD)
import board_lib as bl  # noqa: E402
import ioi2_stress as s2  # noqa: E402

SLUG = 'RIGID-WORLDS-20261110-001A-E001_rigid_worlds_at_radius_two'
DEFAULT_OUT = os.path.join(ROOT, 'artifacts', 'RIGID-WORLDS-20261110-001A', SLUG, 'census.json')
W2 = s2.WORDS2                       # the 17 offsets
IDX = {w: i for i, w in enumerate(W2)}
BUDGET = 1000000


def reduce_letters(w):
    out = []
    for g in w:
        if out and out[-1] == bl.INV[g]:
            out.pop()
        else:
            out.append(g)
    return tuple(out)


# ---- the views ------------------------------------------------------------------------------------------------------------

def inner_stars():
    """For the 5 inner names (offsets () and (g,)), the cell indices of their stars (centre, x, X, y, Y)."""
    stars = []
    for o in [()] + [(g,) for g in range(4)]:
        cells = [IDX[o]] + [IDX[reduce_letters(o + (h,))] for h in range(4)]
        stars.append(cells)
    return stars


STARS = inner_stars()


def allowed_views(L):
    v = np.arange(1 << 17, dtype=np.int64)
    ok = np.ones(1 << 17, dtype=bool)
    for cells in STARS:
        p = np.zeros(1 << 17, dtype=np.int64)
        for t, c in enumerate(cells):
            p |= ((v >> c) & 1) << t
        ok &= ((np.int64(L) >> p) & 1).astype(bool)
    return np.nonzero(ok)[0]


def overlap(g):
    """Pairs (i, j): cell i of a view at u equals cell j of the view at ug (the 8 names within 2 of both)."""
    pairs = []
    for w in W2:
        rel = reduce_letters((bl.INV[g],) + w)          # the same name seen from ug
        if rel in IDX:
            pairs.append((IDX[w], IDX[rel]))
    assert len(pairs) == 8
    return pairs


OV = {g: overlap(g) for g in range(4)}


def classes(views, g):
    """Source and target class keys of each view for letter g."""
    src = np.zeros(len(views), dtype=np.int64)
    tgt = np.zeros(len(views), dtype=np.int64)
    for k, (i, j) in enumerate(OV[g]):
        src |= ((views >> i) & 1) << k
        tgt |= ((views >> j) & 1) << k
    return src, tgt


# ---- step 1: refutation by boards ---------------------------------------------------------------------------------------

def is_parity(m10):
    return m10 in (bl.PARITY0, bl.PARITY1)


def board_allows(L, m10, board):
    """An injective-radius-2-view colouring obeying the law on the board: True, False, or None (budget)."""
    if m10 is not None and is_parity(m10):
        r = s2.parity_colouring(0 if m10 == bl.PARITY0 else 1, board)
        if r == 'undecided':
            return None
        return r is not None
    G = s2.gens(board)
    n = len(board[0])
    at = s2.radius2_cells(board)
    s = Minisat22()
    forb = [p for p in range(32) if not (L >> p) & 1]
    for p in range(n):
        cells = [p, G[0][p], G[1][p], G[2][p], G[3][p]]
        for pat in forb:
            lits, taut = set(), False
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
    s.conf_budget(BUDGET)
    r = s.solve_limited()
    s.delete()
    return r


def l1_min(abd):
    """The least L1 norm of a nonzero vector of Lambda = <(a, 0), (b, d)>."""
    a, b, d = abd
    best = None
    for m in range(-8, 9):
        for k in range(-8, 9):
            if m == 0 and k == 0:
                continue
            v = (m * a + k * b, k * d)
            nrm = abs(v[0]) + abs(v[1])
            if best is None or nrm < best:
                best = nrm
    return best


def frozen_boards():
    one = [((0,), (0,))]
    abelian = [bd for (abd, bd) in bl.tori(8) if len(bd[0]) > 1]      # every finite abelian board is a torus Z^2/Lambda
    nonab6 = [b for n in range(1, 7) for b in bl.finite_boards(n) if not bl.is_abelian(*b)]
    tori_rnd = s2.frozen_boards()
    nonab7, rand = tori_rnd[1], tori_rnd[2]
    thick = [bd for (abd, bd) in bl.tori(64) if 9 <= len(bd[0]) and l1_min(abd) in (3, 4)]
    two_d = [(abd, bd) for (abd, bd) in bl.tori(32) if l1_min(abd) >= 5]
    lists = [('one place', one), ('abelian to 8 places', abelian), ('non-abelian to 6 places', nonab6),
             ('plane-like non-abelian, 7 places', nonab7), ('random non-abelian, 8 to 32 places', rand),
             ('thick tori, index 9 to 64', thick)]
    return lists, two_d


# ---- step 2: the exact view-board search -----------------------------------------------------------------------------

def view_board_sat(views, mode):
    """mode 'any', 'nonab' (a place where sigma_x sigma_y != sigma_y sigma_x) or 'thick' (a loop, or a closing word x^a y^b,
    0 < |a| + |b| <= 4). Returns True/False/None."""
    V = [int(t) for t in views]
    n = len(V)
    nid = [0]

    def new():
        nid[0] += 1
        return nid[0]
    inv = [new() for _ in range(n)]
    m = {}
    cl = []
    for g in (bl.X_, bl.Y_):
        src, tgt = classes(views, g)
        byt = {}
        for j in range(n):
            byt.setdefault(int(tgt[j]), []).append(j)
        mg = {}
        for i in range(n):
            for j in byt.get(int(src[i]), []):
                mg[(i, j)] = new()
        m[g] = mg
        outs = {i: [] for i in range(n)}
        ins = {j: [] for j in range(n)}
        for (i, j), v in mg.items():
            cl.append([-v, inv[i]])
            cl.append([-v, inv[j]])
            outs[i].append(v)
            ins[j].append(v)
        for i in range(n):
            for lst in (outs[i], ins[i]):
                cl.append([-inv[i]] + lst)
                for a, b in itertools.combinations(lst, 2):
                    cl.append([-a, -b])
    mx, my = m[bl.X_], m[bl.Y_]
    succ = {g: {} for g in (bl.X_, bl.Y_)}
    for g in (bl.X_, bl.Y_):
        for (i, j), v in m[g].items():
            succ[g].setdefault(i, []).append((j, v))
    pred = {g: {} for g in (bl.X_, bl.Y_)}
    for g in (bl.X_, bl.Y_):
        for (i, j), v in m[g].items():
            pred[g].setdefault(j, []).append((i, v))
    if mode == 'any':
        cl.append(list(inv))
    elif mode == 'nonab':
        ds = []
        for t in range(n):
            # A: t -x-> a -y-> w ; B: t -y-> b -x-> w ; non-commuting: some w with A and not B
            qs = []
            ws = {}
            for (a, va) in succ[bl.X_].get(t, []):
                for (w, vw) in succ[bl.Y_].get(a, []):
                    ws.setdefault(w, []).append((va, vw))
            for w, chains in ws.items():
                A = new()
                cs = []
                for (va, vw) in chains:
                    c = new()
                    cl.append([-c, va])
                    cl.append([-c, vw])
                    cs.append(c)
                cl.append([-A] + cs)
                B = new()
                for (b, vb) in succ[bl.Y_].get(t, []):
                    for (w2, vw2) in succ[bl.X_].get(b, []):
                        if w2 == w:
                            cl.append([-vb, -vw2, B])
                q = new()
                cl.append([-q, A])
                cl.append([-q, -B])
                qs.append(q)
            if qs:
                d = new()
                cl.append([-d, inv[t]])
                cl.append([-d] + qs)
                ds.append(d)
        if not ds:
            return False
        cl.append(ds)
    elif mode == 'thick':
        # reach variables along each word x^a y^b; R[k][q] true when the k-step image of the start is q
        words = []
        for a in range(-4, 5):
            for b in range(-4, 5):
                if 0 < abs(a) + abs(b) <= 4:
                    w = [bl.X_ if a > 0 else bl.XI] * abs(a) + [bl.Y_ if b > 0 else bl.YI] * abs(b)
                    words.append(w)
        hits = []
        for t in range(n):
            for w in words:
                cur = {t: inv[t]}
                ok = True
                for g in w:
                    nxt = {}
                    base = bl.X_ if g in (bl.X_, bl.XI) else bl.Y_
                    forward = g in (bl.X_, bl.Y_)
                    for q, vq in cur.items():
                        moves = succ[base].get(q, []) if forward else pred[base].get(q, [])
                        for (q2, vm) in moves:
                            r = new()
                            cl.append([-r, vq])
                            cl.append([-r, vm])
                            nxt.setdefault(q2, []).append(r)
                    if not nxt:
                        ok = False
                        break
                    cur2 = {}
                    for q2, rs in nxt.items():
                        z = new()
                        cl.append([-z] + rs)
                        cur2[q2] = z
                    cur = cur2
                    if sum(len(v) for v in nxt.values()) > 200000:
                        return None
                if ok and t in cur:
                    hits.append(cur[t])
        if not hits:
            return False
        cl.append(hits)
    s = Minisat22()
    for c in cl:
        s.add_clause(c)
    s.conf_budget(BUDGET)
    r = s.solve_limited()
    s.delete()
    return r


# ---- the census -------------------------------------------------------------------------------------------------------

def drawn_control():
    """A radius-2 law drawn from one torus: the allowed views are exactly the radius-2 views of a colouring of the 13-place torus
    Z^2/<(2, 3), (3, -2)>... found by search as the first colouring with distinct views and unique overlap classes."""
    for (abd, bd) in bl.tori(32):
        if l1_min(abd) < 5:
            continue
        at = s2.radius2_cells(bd)
        n = len(bd[0])
        for c in range(1 << n):
            col = [(c >> v) & 1 for v in range(n)]
            views = [sum(col[at[p][i]] << i for i in range(17)) for p in range(n)]
            if len(set(views)) < n:
                continue
            arr = np.array(views, dtype=np.int64)
            uniq = True
            for g in (bl.X_, bl.Y_):
                src, tgt = classes(arr, g)
                if len(set(src.tolist())) < n or len(set(tgt.tolist())) < n:
                    uniq = False
            if uniq:
                return list(abd), arr
    return None, None


def run_law(key, L, m10, lists, two_d, views=None):
    r = {}
    if views is None:
        views = allowed_views(L)
    r['views'] = int(len(views))
    for name, bds in lists:
        for i, b in enumerate(bds):
            res = board_allows(L, m10, b)
            if res:
                r['refuted_by'] = [name, i, len(b[0])]
                return r
    if len(views) > 3000:
        r['status'] = 'undecided (more than 3,000 views)'
        return r
    r['any'] = view_board_sat(views, 'any')
    if not r['any']:
        r['status'] = 'no board'
        return r
    r['nonabelian'] = view_board_sat(views, 'nonab')
    r['thick'] = view_board_sat(views, 'thick') if r['nonabelian'] is False else None
    if r['nonabelian'] is False and r['thick'] is False:
        r['status'] = 'forces two-dimensional tori'
        r['tori'] = [list(abd) for (abd, bd) in two_d if board_allows(L, m10, bd)] if m10 is not None else None
    elif r['nonabelian'] or r['thick']:
        r['status'] = 'not forcing (found by the view-board search)'
    else:
        r['status'] = 'undecided (budget)'
    return r


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default=DEFAULT_OUT)
    ap.add_argument('--controls-only', action='store_true')
    args = ap.parse_args()
    t0 = time.time()
    lists, two_d = frozen_boards()
    meta = {'lists': {name: len(b) for name, b in lists}, 'two_d_tori_index_to_32': len(two_d)}
    out = {'meta': meta, 'laws': {}, 'controls': {}}
    abd, cviews = drawn_control()
    ctl = {'torus': abd, 'views': int(len(cviews)) if cviews is not None else 0}
    if cviews is not None:
        ctl['any'] = view_board_sat(cviews, 'any')
        ctl['nonabelian'] = view_board_sat(cviews, 'nonab')
        ctl['thick'] = view_board_sat(cviews, 'thick')
        ctl['forces'] = bool(ctl['any'] and ctl['nonabelian'] is False and ctl['thick'] is False)
    out['controls']['drawn'] = ctl
    full = run_law('full', (1 << 32) - 1, 1023, lists, two_d)
    out['controls']['full'] = full
    print('controls', json.dumps(out['controls']), round(time.time() - t0, 1), flush=True)
    if not args.controls_only:
        for k, L in bl.law_family():
            m10 = int(k[1:]) if k.startswith('L') else None
            if m10 is None:
                r = run_law(k, L, -1, lists, two_d)
            else:
                r = run_law(k, L, m10, lists, two_d)
            if m10 is not None and 'refuted_by' not in r and 'status' not in r:
                r['status'] = 'refuted'
            out['laws'][k] = r
        summary = {}
        for k, r in out['laws'].items():
            st = 'refuted by a board' if 'refuted_by' in r else r.get('status')
            summary[st] = summary.get(st, 0) + 1
        out['summary'] = summary
        out['forcing'] = sorted(k for k, r in out['laws'].items() if r.get('status') == 'forces two-dimensional tori')
        print(json.dumps(summary), out['forcing'], flush=True)
    out['seconds'] = round(time.time() - t0, 1)
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    json.dump(out, open(args.out, 'w'), indent=1, sort_keys=True)


if __name__ == '__main__':
    main()
