"""Gate checks for JOIN-GROWTH-20261118-001B.  python3 -B checks.py > checks_output.json

G1  fastlib's groups equal freelib's: 300 random census arrangements of up to four knots (seed 1) and four joined starts, grown 9
    rounds both ways, give identical presentations (bits of every junction, fresh counts, outcome).
G2  a mutant of fastlib that keeps cliques with a common neighbour disagrees with freelib on some start of G1.
G3  the bare ring of five four-place knots grows 5 junctions every round to round 30; the ring of four four-place knots and one
    five-place knot reproduces RING-GROWTH's c(t) = c(t - 5) + c(t - 6) from round 6 to round 35."""
import itertools
import json
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import joinlib as J  # noqa: E402
import fastlib  # noqa: E402

ROOT = HERE.parents[2]
sys.path.append(str(ROOT / 'experiments/TOUCH-CENSUS-20261118-001B/TOUCH-CENSUS-20261118-001B-E001_arrangements'))
import arrlib  # noqa: E402

F, S = J.F, J.S


def grow_stars(st, rounds=9, maxj=5000):
    P = S.from_junctions(st)
    out = 'alive'
    for _ in range(rounds):
        r = P.step(S.gf2(F.fewest), None)
        if r is None:
            out = 'stall'
            break
        if r['new'] == 0:
            out = 'closed'
            break
        if len(P.bits_of) > maxj:
            break
    return out, P.bits_of, P.fresh


def mutant(self, live, cap=None):
    lv = set(live)
    cand = fastlib.candidates(self, lv)
    big = [frozenset(C) for C in fastlib.maximal_cliques(cand, [u for u in lv if cand[u]]) if len(C) >= 3]
    covered = {p for S_ in big for p in itertools.combinations(sorted(S_), 2)}
    pairs = [frozenset((u, v)) for u in sorted(lv) for v in sorted(cand[u]) if u < v and (u, v) not in covered]
    return sorted(big, key=sorted) + sorted(pairs, key=sorted)


def main():
    out = {}
    random.seed(1)
    keys = sorted(arrlib.arrangements(4))
    starts = [arrlib.stars_of(k) for k in random.sample(keys, 300)]
    R = J.ring_edges(5)
    for n, edges, sp in [(6, R + [(0, 5)], {}), (7, R + [(0, 5), (5, 6)], {}), (7, R + [(0, 5), (2, 6)], {'5': 2}),
                         (10, R + J.ring_edges(5, 5) + [(0, 5)], {})]:
        starts.append(J.stars_from(J.bare_sizes(n, edges, sp), edges))
    fast, orig = F.Presentation.groups_among, fastlib._orig
    res = {}
    for name, impl in [('orig', orig), ('fast', fast), ('mutant', mutant)]:
        F.Presentation.groups_among = impl
        res[name] = [grow_stars(st) for st in starts]
    F.Presentation.groups_among = fast
    out['G1'] = {'starts': len(starts), 'mismatches': sum(a != b for a, b in zip(res['orig'], res['fast']))}
    out['G2'] = {'mutant_disagreements': sum(a != b for a, b in zip(res['orig'], res['mutant']))}
    c0 = J.grow([4] * 5, R, rounds=30)['counts']
    c1 = J.grow([4, 4, 4, 4, 5], R, rounds=35)['counts']
    out['G3'] = {'bare_ring_five_every_round': all(x == 5 for x in c0[1:]) and len(c0) == 31,
                 'ring_recurrence': all(c1[t] == c1[t - 5] + c1[t - 6] for t in range(6, len(c1))), 'rounds': len(c1) - 1}
    out['pass'] = (out['G1']['mismatches'] == 0 and out['G2']['mutant_disagreements'] > 0 and
                   out['G3']['bare_ring_five_every_round'] and out['G3']['ring_recurrence'])
    print(json.dumps(out, indent=1))


if __name__ == '__main__':
    main()
