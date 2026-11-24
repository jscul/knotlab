# Thread's check of a hand-built 9-knot structure in which BOTH setting births are births rule Q makes
# (a one-parent birth takes its parent's loose distinction and one distinction the parent shares).
# Fully separate from the recorded scorer: the four finished structures are enumerated word by word, the joint distribution
# of the two complete records is kept in exact fractions, hiding is tested exactly, and the four-correlation score is
# maximised over ALL two-valued outcome functions of each complete record (not only parities).
# Run from the repository root: .venv/bin/python -B research/SETTING-AS-REREAD-20261123-001/thread_checks/nine_knot_both_settings.py
import itertools, collections, sys
from fractions import Fraction
ALICE = [('even', ('x1', 'x2', 'x3', 'c')), ('nae', ('c', 'x2', 's1')), ('nae', ('c', 'x3', 's2')),
         ('even', ('x2', 'h1', 'h2')), ('odd', ('x3', 'h1', 'h2'))]
BOB = [('even', ('y2', 'k1', 'k2')), ('odd', ('y3', 'k1', 'k2')), ('odd', ('s2', 'k1', 'k2')), ('even', ('y1', 'y2', 'y3', 's1'))]
def ok(law, vals):
    return (len(set(vals)) > 1) if law == 'nae' else (sum(vals) % 2 == (0 if law == 'even' else 1))
def words(knots):
    names = sorted({m for _, mem in knots for m in mem})
    for w in itertools.product((0, 1), repeat=len(names)):
        d = dict(zip(names, w))
        if all(ok(l, [d[m] for m in mem]) for l, mem in knots): yield d
def analyse(start, obsA=('x1', 'x2', 'x3'), obsB=('y1', 'y2', 'y3'), verbose=True):
    hold = collections.Counter(m for _, mem in start for m in mem)
    J = {}; nwords = {}
    for a in (0, 1):
        for b in (0, 1):
            fin = start + [('nae', (obsA[0], obsA[1 + a], 'za')), ('nae', (obsB[0], obsB[1 + b], 'zb'))]
            c = collections.Counter()
            for d in words(fin):
                c[(tuple(d[m] for m in obsA) + (d['za'],), tuple(d[m] for m in obsB) + (d['zb'],))] += 1
            n = sum(c.values()); nwords[a, b] = n
            J[a, b] = {k: Fraction(v, n) for k, v in c.items()}
    def marg(j, side):
        m = collections.Counter()
        for (ra, rb), p in j.items(): m[ra if side == 0 else rb] += p
        return dict(m)
    hidden = all(marg(J[a, 0], 0) == marg(J[a, 1], 0) for a in (0, 1)) and all(marg(J[0, b], 1) == marg(J[1, b], 1) for b in (0, 1))
    # best score over all outcome functions: enumerate Alice's two functions on her record values, Bob's follow
    RA = sorted({ra for j in J.values() for ra, _ in j}); RB = sorted({rb for j in J.values() for _, rb in j})
    best = Fraction(0)
    signs = [(1, 1, 1, -1), (1, 1, -1, 1), (1, -1, 1, 1), (-1, 1, 1, 1)]
    for fa0 in itertools.product((1, -1), repeat=len(RA)):
        A0 = dict(zip(RA, fa0))
        for fa1 in itertools.product((1, -1), repeat=len(RA)):
            if fa1[0] != 1: continue                      # global sign of A1 with B's is free
            A1 = dict(zip(RA, fa1)); A = (A0, A1)
            # linear forms for Bob's functions
            L = {(a, b): collections.Counter() for a in (0, 1) for b in (0, 1)}
            for (a, b), j in J.items():
                for (ra, rb), p in j.items(): L[a, b][rb] += A[a][ra] * p
            for s in signs:
                tot = Fraction(0)
                for b in (0, 1):
                    for rb in RB:
                        tot += abs(s[0 * 2 + b] * L[0, b][rb] + s[2 + b] * L[1, b][rb])
                if tot > best: best = tot
    if verbose:
        print('holders above two:', {k: n for k, n in hold.items() if n > 2}, '| loose:', sorted(k for k, n in hold.items() if n == 1))
        print('allowed words of the four finished structures:', [nwords[a, b] for a in (0, 1) for b in (0, 1)])
        print('record values met: Alice', len(RA), 'Bob', len(RB), '| hidden:', hidden, '| largest score over all outcome functions:', best)
    return hidden, best, nwords
if __name__ == '__main__':
    print('start: Alice', ALICE); print('       Bob  ', BOB)
    analyse(ALICE + BOB)
