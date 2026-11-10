"""The frozen census of LEIBNIZ-BOARDS-20261110-001B: which one-bit laws leave the tree under Leibniz's rule.

Under Leibniz's rule (names that agree at every radius are one place) the boards of a value law are the Schreier graphs of the
stabilizers of its solutions on the tree of names (ticket A). This census classifies the 1,024 Life-like one-bit laws and the atom
by their solutions on the tree:
  E  no solution;
  D  deterministic: every tree pattern has exactly one compatible neighbour pattern in each direction, so the law has finitely
     many solutions and every board is finite;
  A  some periodic solution (a colouring of a finite board) uses a branching pattern (a pattern with two compatible neighbour
     patterns in one direction), so by ticket A's Lemma A the tree is a board, and so is the Schreier graph of an infinite cyclic
     subgroup (an infinite board other than the tree);
  U  branching, but no periodic solution with a branching pattern on the finite boards searched (to 8 places): not decided here.
For class A, a reading: whether the plane is a board (an aperiodic solution on Z^2), certified when some torus solution has a cell,
or a 2 x 2 block, that can be refilled differently with every pattern still allowed.

Usage: census.py [--nmax 6] [--nmax-rest 8] [--out FILE]
"""
import argparse
import itertools
import json
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
LIB = os.path.join(ROOT, 'experiments', 'BOARD-DIST-20261110-001B', 'BOARD-DIST-20261110-001B-E001_which_boards_one_bit_laws_allow')
sys.path.insert(0, LIB)
import board_lib as bl  # noqa: E402

SLUG = 'LEIBNIZ-BOARDS-20261110-001B-E001_which_laws_leave_the_tree'
DEFAULT_OUT = os.path.join(ROOT, 'artifacts', 'LEIBNIZ-BOARDS-20261110-001B', SLUG, 'census.json')


def branching_patterns(L):
    """Tree patterns with at least two compatible neighbour patterns (in the half-tree sets) in some direction."""
    H = bl.half_tree_sets(L)
    P = bl.tree_patterns(L, H)
    branch = set()
    for p in P:
        for h in range(4):
            if sum(1 for q in H[h] if bl.compat(p, h, q)) >= 2:
                branch.add(p)
                break
    return P, branch


def mask_of(pats):
    m = 0
    for p in pats:
        m |= 1 << p
    return m


def periodic_branching(boards, laws_masks, branch_masks):
    """For each law: the first finite board (index) with a colouring of allowed patterns that uses a branching pattern."""
    found = [None] * len(laws_masks)
    Ls = np.array(laws_masks, dtype=np.int64)
    forb = (~Ls) & 0xFFFFFFFF
    Bs = np.array(branch_masks, dtype=np.int64)
    todo = np.array([b != 0 for b in branch_masks])
    for i, bd in enumerate(boards):
        if not todo.any():
            break
        bits, masks = bl.board_patterns(bd)
        valid = (masks[:, None] & forb[None, :]) == 0
        uses = (masks[:, None] & Bs[None, :]) != 0
        hit = (valid & uses).any(axis=0) & todo
        for j in np.nonzero(hit)[0]:
            found[j] = i
        todo &= ~hit
    return found


def plane_refill(L, tmax=16):
    """A torus solution with a cell or a 2 x 2 block that can be refilled differently, every pattern still allowed: then the
    plane carries aperiodic solutions (independent refills at sparse translates). Returns the torus (a, b, d) or None."""
    for (abd, bd) in bl.tori(tmax):
        sx, sy = bd
        n = len(sx)
        six, siy = bl._inverse(sx), bl._inverse(sy)
        nbrs = [(sx[v], six[v], sy[v], siy[v]) for v in range(n)]

        def pat(col, v):
            a, b, c, d = nbrs[v]
            return bl.pattern(col[v], col[a], col[b], col[c], col[d])
        for cbits in range(1 << n):
            col = [(cbits >> v) & 1 for v in range(n)]
            if not all((L >> pat(col, v)) & 1 for v in range(n)):
                continue
            # single cells and 2 x 2 blocks (v, vx, vy, vxy)
            for v in range(n):
                blocks = [(v,), (v, sx[v], sy[v], sy[sx[v]])]
                for blk in blocks:
                    cells = sorted(set(blk))
                    for alt in itertools.product((0, 1), repeat=len(cells)):
                        if all(col[c] == a for c, a in zip(cells, alt)):
                            continue
                        new = list(col)
                        for c, a in zip(cells, alt):
                            new[c] = a
                        touched = set(cells)
                        for c in cells:
                            touched.update(nbrs[c])
                        if all((L >> pat(new, w)) & 1 for w in touched):
                            return list(abd)
            break  # one solution per torus suffices to look for refills
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--nmax', type=int, default=6)
    ap.add_argument('--nmax-rest', type=int, default=8)
    ap.add_argument('--out', default=DEFAULT_OUT)
    ap.add_argument('--controls-only', action='store_true')
    args = ap.parse_args()
    t0 = time.time()
    fam = [('full', (1 << 32) - 1), ('empty', 0)]
    if not args.controls_only:
        fam += bl.law_family()
    res = {}
    masks, bmasks = [], []
    for k, L in fam:
        P, B = branching_patterns(L)
        res[k] = {'tree_patterns': len(P), 'branching_patterns': len(B)}
        masks.append(L)
        bmasks.append(mask_of(B))
    boards = []
    for n in range(1, args.nmax + 1):
        boards.extend(bl.finite_boards(n))
    found = periodic_branching(boards, masks, bmasks)
    rest = [j for j, (k, L) in enumerate(fam) if bmasks[j] and found[j] is None]
    extra = []
    if rest and args.nmax_rest > args.nmax:
        for n in range(args.nmax + 1, args.nmax_rest + 1):
            extra.extend(bl.finite_boards(n))
        sub = periodic_branching(extra, [masks[j] for j in rest], [bmasks[j] for j in rest])
        for j, f in zip(rest, sub):
            if f is not None:
                found[j] = len(boards) + f
    allb = boards + extra
    for j, (k, L) in enumerate(fam):
        r = res[k]
        if r['tree_patterns'] == 0:
            r['class'] = 'E'
        elif r['branching_patterns'] == 0:
            r['class'] = 'D'
        elif found[j] is not None:
            r['class'] = 'A'
            b = allb[found[j]]
            r['periodic_branching_board'] = [list(b[0]), list(b[1])]
        else:
            r['class'] = 'U'
    for j, (k, L) in enumerate(fam):
        if res[k]['class'] == 'A':
            res[k]['plane_refill_torus'] = plane_refill(L)
    counts = {}
    for k, r in res.items():
        if k.startswith('L'):
            counts[r['class']] = counts.get(r['class'], 0) + 1
    summary = {'life_like_classes': counts, 'atom': res.get('atom', {}).get('class'),
               'controls': {'full': res['full']['class'], 'empty': res['empty']['class']},
               'U_laws': sorted(k for k, r in res.items() if r['class'] == 'U'),
               'D_laws': sorted(k for k, r in res.items() if r['class'] == 'D'),
               'plane_certified': sum(1 for k, r in res.items() if k.startswith('L') and r.get('plane_refill_torus')),
               'class_A_without_plane_certificate': sorted(k for k, r in res.items() if r['class'] == 'A' and not r.get('plane_refill_torus') and k.startswith('L')),
               'finite_boards_searched': len(allb), 'seconds': round(time.time() - t0, 1)}
    out = {'summary': summary, 'laws': res}
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, 'w') as fh:
        json.dump(out, fh, indent=1, sort_keys=True)
    print(json.dumps(summary, indent=1))


if __name__ == '__main__':
    main()
