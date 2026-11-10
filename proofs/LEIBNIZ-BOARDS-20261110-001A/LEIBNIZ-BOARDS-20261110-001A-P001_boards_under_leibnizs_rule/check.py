"""Finite checks of LEIBNIZ-BOARDS-20261110-001A. They calibrate the proofs; they prove nothing.

0. T2: the horofunction law on Z/3 (a place of value k has exactly one neighbour of value k - 1 and three of value k + 1). The
   colouring s(u) = b(u) mod 3, b the Busemann function of the end x^oo (b(u) = |u| - 2j, j the number of leading x's of u), obeys
   the law at every name with its star in the ball B_9, is invariant under left multiplication by x^3 there, and is moved by every
   other element of length at most 6 (so its stabilizer meets B_6 exactly in <x^3>).
1. T3's hypothesis in ticket B's census: every class-A certificate (a finite board with a colouring that uses a branching
   pattern) is re-verified from the law.

Usage: check.py [--out result.json]
"""
import argparse
import json
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'experiments', 'BOARD-DIST-20261110-001B', 'BOARD-DIST-20261110-001B-E001_which_boards_one_bit_laws_allow'))
import board_lib as bl  # noqa: E402

INVERSE = {'x': 'X', 'X': 'x', 'y': 'Y', 'Y': 'y'}


def reduce_word(w):
    out = []
    for g in w:
        if out and out[-1] == INVERSE[g]:
            out.pop()
        else:
            out.append(g)
    return ''.join(out)


def ball(L):
    words, layer = [''], ['']
    for _ in range(L):
        layer = [w + g for w in layer for g in 'xXyY' if not (w and w[-1] == INVERSE[g])]
        words.extend(layer)
    return words


def busemann(u):
    j = 0
    while j < len(u) and u[j] == 'x':
        j += 1
    return len(u) - 2 * j


def s_horo(u):
    return busemann(u) % 3


def check0(L=9, glen=6, ulen=8):
    law_ok = True
    for u in ball(L):
        k = s_horo(u)
        nbr = [s_horo(reduce_word(u + g)) for g in 'xXyY']
        if not (nbr.count((k - 1) % 3) == 1 and nbr.count((k + 1) % 3) == 3):
            law_ok = False
    inv = all(s_horo(reduce_word('xxx' + u)) == s_horo(u) for u in ball(L))
    fixed = []
    test = ball(ulen)
    for g in ball(glen):
        if g and all(s_horo(reduce_word(g + u)) == s_horo(u) for u in test):
            fixed.append(g)
    cube = {'xxx', 'xxxxxx', 'XXX', 'XXXXXX'}
    return {'law_holds_on_B9': law_ok, 'invariant_under_x3': inv, 'fixed_elements_to_length_6': sorted(fixed),
            'passed': law_ok and inv and set(fixed) == cube}


def check1():
    """Re-verify every class-A certificate of ticket B's census: on the recorded finite board, some colouring with every
    pattern allowed uses a branching pattern (computed again from the law)."""
    census = json.load(open(os.path.join(ROOT, 'artifacts', 'LEIBNIZ-BOARDS-20261110-001B',
                                         'LEIBNIZ-BOARDS-20261110-001B-E001_which_laws_leave_the_tree', 'census.json')))
    fam = dict(bl.law_family())
    good = total = 0
    for k, r in census['laws'].items():
        if r.get('class') != 'A' or k not in fam:
            continue
        total += 1
        L = fam[k]
        H = bl.half_tree_sets(L)
        P = bl.tree_patterns(L, H)
        branch = {p for p in P if any(sum(1 for q in H[h] if bl.compat(p, h, q)) >= 2 for h in range(4))}
        sx, sy = r['periodic_branching_board']
        bits, masks = bl.board_patterns((tuple(sx), tuple(sy)))
        forb = (~L) & 0xFFFFFFFF
        bm = 0
        for p in branch:
            bm |= 1 << p
        if any((int(m) & forb) == 0 and (int(m) & bm) for m in masks):
            good += 1
    return {'class_A_certificates': total, 'reverified': good, 'passed': good == total and total > 0}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default=os.path.join(HERE, 'result.json'))
    a = ap.parse_args()
    res = {'check0_horofunction': check0(), 'check1_class_A_certificates': check1()}
    res['passed'] = all(v['passed'] for v in res.values())
    res['status'] = 'passed' if res['passed'] else 'failed'
    json.dump(res, open(a.out, 'w'), indent=1, sort_keys=True)
    print(json.dumps({k: (v['passed'] if isinstance(v, dict) else v) for k, v in res.items()}))
    print(json.dumps(res['check0_horofunction']))


if __name__ == '__main__':
    main()
