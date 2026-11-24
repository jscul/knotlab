# Thread's exploratory check (before any freeze) of an 11-knot structure on which one round of rule Q makes exactly two
# births, the two observers' setting births.  Uses the thread's own rule-Q engine for round 1 and the separate word-by-word
# analysis of nine_knot_both_settings.py.  Also a stronger hiding test: every distinction held by an observer's own knots.
# Run from the repository root: .venv/bin/python -B research/SETTING-AS-REREAD-20261123-001/thread_checks/eleven_knot_both_settings.py
import sys, os, itertools, collections
from fractions import Fraction
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '../../ONE-PARENT-REREAD-20261123-001/thread_checks'))
import rule_q_engine as qe
import nine_knot_both_settings as nk
ALICE = nk.ALICE
BOB = [('even', ('y1', 'y2', 'y3', 't')), ('even', ('t', 'm1', 'm2')), ('even', ('s1', 'm1', 'm2')),
       ('even', ('y2', 'k1', 'k2')), ('odd', ('y3', 'k1', 'k2')), ('odd', ('s2', 'k1', 'k2'))]
START = ALICE + BOB
def whole_side_hidden(start, obsA, obsB):
    """Is the joint distribution of EVERY distinction held by an observer's own knots, with its fresh one, the same for either far choice?"""
    sideA = sorted({m for _, mem in ALICE for m in mem}); sideB = sorted({m for _, mem in BOB for m in mem})
    D = {}
    for a in (0, 1):
        for b in (0, 1):
            fin = start + [('nae', (obsA[0], obsA[1 + a], 'za')), ('nae', (obsB[0], obsB[1 + b], 'zb'))]
            ca = collections.Counter(); cb = collections.Counter(); n = 0
            for d in nk.words(fin):
                n += 1; ca[tuple(d[m] for m in sideA) + (d['za'],)] += 1; cb[tuple(d[m] for m in sideB) + (d['zb'],)] += 1
            D[a, b] = ({k: Fraction(v, n) for k, v in ca.items()}, {k: Fraction(v, n) for k, v in cb.items()})
    return (all(D[a, 0][0] == D[a, 1][0] for a in (0, 1)), all(D[0, b][1] == D[1, b][1] for b in (0, 1)))
if __name__ == '__main__':
    names = {}; stars = [tuple(names.setdefault(m, len(names)) for m in mem) for _, mem in START]; back = {i: n for n, i in names.items()}
    g = qe.Q(stars, 'O'); g.round()
    print('round 1 under rule Q:', [(tuple(back.get(x, 'fresh') for x in b['inputs']), 'parents', b['parents'], 'fresh', b['fresh']) for b in g.births[0]])
    hold = collections.Counter(d for s in stars for d in s)
    opts = {('A' if back[b['inputs'][0]] == 'x1' else 'B'): sorted(back[d] for d in stars[b['parents'][0]] if hold[d] >= 2) for b in g.births[0]}
    print('shared distinctions each birth may take:', opts)
    for pa in itertools.combinations(opts['A'], 2):
        for pb in itertools.combinations(opts['B'], 2):
            h, best, nw = nk.analyse(START, obsA=('x1',) + pa, obsB=('y1',) + pb, verbose=False)
            ws = whole_side_hidden(START, ('x1',) + pa, ('y1',) + pb)
            print(' Alice', pa, '| Bob', pb, '| words', sorted(set(nw.values())), '| hidden', h, '| score', best, '| hidden for every distinction of the side (Alice, Bob):', ws)
    # ordinary growth on the same structure: no re-read, no choice
    g0 = qe.Q(stars, 'O', reread=False); g0.round()
    print('ordinary growth, round 1:', [(tuple(back.get(x, 'fresh') for x in b['inputs']), 'fresh', b['fresh']) for b in g0.births[0]])
