"""commute.py: the commuting test and the advisor's check 1f (README.md). On rings of n knots with two loose distinctions
each, loose values pinned: the exchanged pattern of the bare ring; of the ring after one round; one round of growth of
the bare ring's exchanged pattern; and whether the grown ring's exchanged pattern is the bare ring itself up to renaming
(compared as labelled multigraphs: knots with their loose counts, shared distinctions as edges)."""
import sys, json
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE.parent / 'FOLD-SIGN-20261126-001'))
sys.argv = sys.argv[:1]
import dual, fold
from networkx.algorithms import isomorphism
classes, classes2, forbid = dual.classes, dual.classes2, dual.forbid


def exchanged(supports, pin):
    names, idx, n, held, loose, rows = classes2.setup(supports, pin)
    M, missing = classes2.short_moves(n, rows, True)
    return tuple(tuple(names[i] for i in range(n) if (t >> i) & 1) for t in sorted(M))


def same(a, b):
    A, B = fold.multigraph(a), fold.multigraph(b)
    return isomorphism.GraphMatcher(A, B, node_match=lambda x, y: x['loose'] == y['loose'], edge_match=lambda x, y: x['m'] == y['m']).is_isomorphic()


for n in range(5, 11):
    R = classes.ring(n, 2)
    ex_bare = exchanged(R, True)
    st, status, b = forbid.grown(R, 'parity', 'ordinary')
    ex_grown = exchanged(st, True)
    if all(len(k) >= 3 for k in ex_bare):
        g2, s2, b2 = forbid.grown(ex_bare, 'parity', 'ordinary')
    else:
        g2, s2 = None, 'not lawful'
    print(json.dumps({'ring': n, 'exchanged bare ring (places)': [len(k) for k in ex_bare], 'exchanged grown ring (places)': sorted(len(k) for k in ex_grown),
                      'growth of the exchanged bare ring': s2, 'its knots (places)': sorted(len(k) for k in g2) if g2 else None,
                      'growth commutes with the exchange': bool(g2) and same(g2, ex_grown),
                      'exchanged grown ring is the bare ring up to renaming': same(ex_grown, R)}))
