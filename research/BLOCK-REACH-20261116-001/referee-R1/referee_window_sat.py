"""Referee R1 (BLOCK-REACH-20261116-001), item 2: the block step against SAT.

For random windows of r block steps in P_N (N = 11 by default), along a random explicit path of orbits (my block DP's types, mapped
to explicit addresses), my composed relation (referee_forget.Forget.step, at remaining depth N - level - 1 for each step) is
compared with the projection onto (O_j, O_(j+r)) of the sub-pattern the window describes: every knot of P_N (my builder) placed at
an address under O_j (O_j included) and not under O_(j+r) (O_(j+r) excluded), by SAT on every assignment of the two orbits.
As a control for item (b), the same window with the bottom orbit also restricted by its own subtree (z in F_{N-j-r}) is compared too:
when it differs from SAT, the test shows that the study's step (child unrestricted) is the one the sub-pattern has.
Also: where r >= the study's claimed r_all, the SAT projection must be rectangular.
Usage: referee_window_sat.py OUT.json N n_descriptions windows_per_description"""
import gzip
import json
import random
import sys
import time
from pathlib import Path

import numpy as np
from pysat.solvers import Cadical195

sys.path.insert(0, '/home/jscul/p-vs-np-contact-first/research/DIRECT-REACH-20261115-001/referee-R1')
sys.path.insert(0, '/home/jscul/p-vs-np-contact-first/research/BLOCK-REACH-20261116-001/referee-R1')
from referee_pattern import Aut, hid  # noqa: E402  (my own)
from referee_forget import Forget, compose, is_rect, load_census  # noqa: E402  (my own)

ROOT = Path('/home/jscul/p-vs-np-contact-first')


def placed_knots(A, n, N):
    """(knot rows as heap ids, placed address) of level n in P_N."""
    img = {}
    rows, where = [], []
    X = np.arange(1 << n, dtype=np.int64)
    for p in A.placements:
        mem = []
        for t in p:
            wi, e = divmod(t, 3)
            if e and n == N:
                mem = None
                break
            if wi not in img:
                img[wi] = A.act(A.W[wi], n)
            y = img[wi]
            mem.append(y + (1 << n) - 1 if e == 0 else 2 * y + (e - 1) + (1 << (n + 1)) - 1)
        if mem is None:
            continue
        M = np.sort(np.stack(mem, axis=1), axis=1)
        keep = (M[:, 0] != M[:, 1]) & (M[:, 1] != M[:, 2])
        rows.append(M[keep])
        where.append(X[keep])
    if not rows:
        return np.empty((0, 3), dtype=np.int64), np.empty(0, dtype=np.int64)
    return np.concatenate(rows), np.concatenate(where)


def window_projection(A, N, j, top, r, bottom):
    """SAT projection onto (top orbit at level j, bottom orbit at level j + r), element order, of the window's sub-pattern."""
    top_a, bot_a = np.array(top), np.array(bottom)
    clauses, seen = [], set()
    for n in range(j, N + 1):
        K, V = placed_knots(A, n, N)
        if not len(K):
            continue
        keep = np.isin(V >> (n - j), top_a)
        if n >= j + r:
            keep &= ~np.isin(V >> (n - j - r), bot_a)
        for row in K[keep].tolist():
            tr = tuple(row)
            if tr not in seen:
                seen.add(tr)
    vid = {}
    proj = [hid(a, j) for a in top] + [hid(b, j + r) for b in bottom]
    for h in proj:
        vid.setdefault(h, len(vid) + 1)
    for tr in seen:
        lits = [vid.setdefault(h, len(vid) + 1) for h in tr]
        clauses.append(lits)
        clauses.append([-l for l in lits])
    out = set()
    with Cadical195(bootstrap_with=clauses) as S:
        for pat in range(1 << len(proj)):
            ass = [vid[h] if (pat >> i) & 1 else -vid[h] for i, h in enumerate(proj)]
            if S.solve(assumptions=ass):
                out.add((pat & ((1 << len(top)) - 1), pat >> len(top)))
    return frozenset(out), len(seen)


if __name__ == '__main__':
    out_path, N, nd, per = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
    rng = random.Random(1116)
    rows = json.load(open(ROOT / 'research/BLOCK-REACH-20261116-001/census_forget.json'))['rows']
    recs = load_census()
    r01 = sorted(c for c, v in rows.items() if v['r0'] == 1)
    others = sorted(c for c in rows if c not in r01)
    by = {}
    for c in others:
        by.setdefault((rows[c]['name'], rows[c]['r_all']), []).append(c)
    cand = []
    for k in sorted(by, key=str):
        cand += rng.sample(by[k], min(5, len(by[k])))
    pick = r01 + rng.sample(cand, min(len(cand), max(0, nd - len(r01))))
    res, mism, nonrect, alt_differs = [], [], [], 0
    t0 = time.time()
    for cid in pick:
        key = recs[cid]['key']
        f = Forget(key)
        A = Aut(key)
        B = f.B
        claimed = rows[cid]['r_all']
        for w in range(per):
            choices = [1, 2, 3] + ([claimed] if isinstance(claimed, int) else [])
            r = rng.choice(choices)
            j = rng.randint(1, N - r)
            # a random explicit path from the root down to level j + r
            node = (0, [0])
            path = [node]
            cis = []
            for n in range(j + r):
                t, addrs = node
                ci = rng.randrange(len(B.kids[t]))
                c, pos = B.kids[t][ci]
                node = (c, [2 * addrs[p // 2] + p % 2 for p in pos])
                path.append(node)
                cis.append(ci)
            t, top = path[j]
            R = frozenset((x, x) for x in range(1 << B.m[t]))
            for i in range(r):
                lvl = j + i
                c, S = f.step(path[lvl][0], cis[lvl], N - lvl - 1)
                R = compose(R, S)
            tb, bottom = path[j + r]
            Ralt = frozenset((a, z) for a, z in R if z in f.F[min(N - j - r, f.r0)][tb])
            J, nk = window_projection(A, N, j, top, r, bottom)
            rec = dict(case=cid, N=N, j=j, r=r, claimed_r_all=claimed, sizes=[len(top), len(bottom)], knots=nk,
                       equal=J == R, alt_equal=J == Ralt, rect=is_rect(J), relation_size=len(J))
            if J != R:
                mism.append(rec)
            if Ralt != R:
                alt_differs += 1
            if isinstance(claimed, int) and r >= claimed and not is_rect(J):
                nonrect.append(rec)
            res.append(rec)
        print(cid[:12], rows[cid]['name'], 'claimed', claimed, 'windows so far', len(res), 'mismatches', len(mism),
              'nonrect', len(nonrect), '%.0fs' % (time.time() - t0), flush=True)
        json.dump(dict(N=N, windows=len(res), mismatches=mism, nonrect_where_claimed=nonrect,
                       alt_restricted_child_differs_from_step=alt_differs,
                       alt_equal_SAT_when_differs=sum(1 for x in res if x['alt_equal'] and not x['equal']),
                       records=res, seconds=time.time() - t0), open(out_path, 'w'), indent=0)
    print('done windows', len(res), 'mismatches', len(mism), 'nonrect', len(nonrect), 'alt differs', alt_differs)
