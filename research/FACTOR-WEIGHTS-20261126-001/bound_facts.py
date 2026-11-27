"""bound_facts.py: restricting the coherent counting state to one value of a bound whole-held fact (README.md, part B;
frozen in preregistration.md). The third-layer referee's construction (THIRD-LAYER-20261126-001/referee-R1: three rings
of four knots, split attachments, double links; its growth.py builds and grows it) at the rounds its certificate records
(1, 4, 5, 6), with its five facts' carriers (R, S, T the whole rings, P, Q the first ring's alternating families; bound
by R + S + T = 0 and P + Q + R = 0, sums of knot laws). Readers: the regions of the three rings' lineages (every place of
the knots descended from one ring alone); the rest unread. Per stage:
    local flips    for each ring region, the allowed changes supported in it: does any flip any of the 31 nonzero sums
                   of the five facts?
    restricted e   the coherent counting state restricted to f = 0 (the carrier appended as one more knot) for each of
                   the five facts and the largest and smallest over the 31 sums, e for each pair of ring readers under
                   the three treatments of the middle (unread, read for values, read for changes)
Controls (the advisor's): three rings joined by nothing, restricted to a + b (one loose distinction of each of two
rings), to a + b + m (m of the third ring), to ring 0's own fact, and readers holding only a and b."""
import sys, json, itertools
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / 'THIRD-LAYER-20261126-001' / 'referee-R1'))
sys.path.insert(0, str(HERE.parent / 'VALUE-CHANGE-20261126-001')); sys.path.insert(0, str(HERE.parent / 'BUILT-BINDING-20261126-001'))
import growth as G            # noqa: E402  (the referee's)
import css                    # noqa: E402
import repro                  # noqa: E402


def restricted(knots, A, B, facts, middle):
    """e between A and B in the coherent counting state restricted to every fact in `facts` reading 0 (each fact's
    carrier appended as one more knot, as the advisor proposed), under a treatment of the middle (css.ebits)"""
    return css.ebits([list(k) for k in knots] + [list(f) for f in facts], A, B, middle)


def local_flips(knots, region, facts):
    names, idx, m, Xs, Zs = css.state(knots)
    L = css.subspace_within(Xs, sum(1 << idx[d] for d in region), m)
    F = [sum(1 << idx[d] for d in f) for f in facts]
    return [any((x & f).bit_count() & 1 for x in L) for f in F], len(L)


TREATMENTS = ('unread', 'values', 'changes')


def run():
    cert = json.load(open(HERE.parent / 'THIRD-LAYER-20261126-001' / 'referee-R1' / 'ring_overlap_counts.json'))
    want = {s['round']: s for s in cert['stages']}
    S, rings, loose = G.ring_start(3, 4, 'split', 'double')
    lineage = {k: frozenset([r]) for r, ring in enumerate(rings) for k in ring}
    for k in range(len(S)): lineage.setdefault(k, frozenset(['middle']))
    st = S
    for t in range(1, max(want) + 1):
        st, status, births = G.grow(st)
        assert status == 'funded'
        for b in births: lineage[b['knot']] = frozenset().union(*(lineage[p] for p in b['parents']))
        if t not in want: continue
        w = want[t]; knots = [list(k) for k in st]
        assert len(knots) == w['knots'] and len({d for k in knots for d in k}) == w['distinctions']
        five = w['supports']
        sums = []
        for pick in itertools.product((0, 1), repeat=5):
            if any(pick):
                f = set()
                for p, s in zip(pick, five):
                    if p: f ^= set(s)
                sums.append((pick, sorted(f)))
        region = {r: sorted({d for u, k in enumerate(knots) if lineage[u] == frozenset([r]) for d in k}) for r in range(3)}
        row = {'round': t, 'knots': len(knots), 'distinctions': w['distinctions']}
        for r in range(3):
            flips, nloc = local_flips(knots, region[r], [f for _, f in sums])
            row['ring %d: local changes (rank)' % r] = nloc
            row['ring %d: sums of the five facts flipped by a local change' % r] = sum(flips)
        es = {}
        names5 = ('R', 'S', 'T', 'P', 'Q')
        for r, s in itertools.combinations(range(3), 2):
            A, B = region[r], region[s]
            assert not set(A) & set(B) and css.separated(knots, A, B)
            for mid in TREATMENTS:
                key = 'rings %d and %d, middle %s' % (r, s, mid)
                es[key] = {'unrestricted': restricted(knots, A, B, [], mid),
                           **{nm + ' fixed': restricted(knots, A, B, [f], mid) for nm, f in zip(names5, five)},
                           'largest over the 31 sums': max(restricted(knots, A, B, [f], mid) for _, f in sums),
                           'smallest over the 31 sums': min(restricted(knots, A, B, [f], mid) for _, f in sums)}
        row['e'] = es
        print(json.dumps(row), flush=True)
    # controls: rings joined by nothing (BUILT-BINDING's builder, link 'apart')
    S3, rings3, loose3 = repro.rings_start(R=3, n=4, link='apart')
    knots = [list(k) for k in S3]
    reg = [sorted({d for k in ring for d in knots[k]}) for ring in rings3]
    A, B = reg[0], reg[1]
    a, b, mm = loose3[0][0], loose3[1][0], loose3[2][0]
    out = {'separated': css.separated(knots, A, B)}
    for mid in TREATMENTS:
        out['middle ' + mid] = {'unrestricted': restricted(knots, A, B, [], mid),
                                'a + b fixed (one loose distinction of each ring)': restricted(knots, A, B, [[a, b]], mid),
                                'a + b + m fixed (m a loose distinction of the third ring)': restricted(knots, A, B, [[a, b, mm]], mid),
                                "ring 0's own fact fixed": restricted(knots, A, B, [list(loose3[0])], mid),
                                'readers holding only a and b, a + b + m fixed': restricted(knots, [a], [b], [[a, b, mm]], mid)}
    print(json.dumps({'controls: three rings joined by nothing': out}), flush=True)

if __name__ == '__main__':
    run()
