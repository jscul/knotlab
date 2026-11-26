"""handtest.py OUT.json: the advisor's hand test before the freeze.  Starts where the reach of a reader is cut through a
group of three or more: a path of knots ending in a triple of knots that touch pairwise, in two triples sharing a knot,
or in four knots touching pairwise, with and without extra loose distinctions, at the smallest sizes that do not stall
(WEIGHTINGS' bare sizes) plus SURPLUS; every live knot is a reader; the least number of holder steps whose knots give
the reader's view through round t, for t = 1..T, under not-all-equal (and parity, reported)."""
import sys, os, json, itertools, collections
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ondemand as O, run as RUN
WL = RUN.WL; stars_of = RUN.stars_of
T = 8


def family():
    for L in (2, 4, 6, 8):
        path = [(i, i + 1) for i in range(L)]
        a = L
        ends = {'a triple': [(a, a + 1), (a, a + 2), (a + 1, a + 2)],
                'two triples sharing a knot': [(a, a + 1), (a, a + 2), (a + 1, a + 2), (a + 2, a + 3), (a + 2, a + 4), (a + 3, a + 4)],
                'four touching pairwise': [(x, y) for x, y in itertools.combinations(range(a, a + 4), 2)],
                'a triple at both ends': [(a, a + 1), (a, a + 2), (a + 1, a + 2), (0, a + 3), (0, a + 4), (a + 3, a + 4)]}
        for name, e in ends.items():
            edges = path + e; n = 1 + max(max(p) for p in edges)
            for surplus in (0, 1):
                sizes = WL.bare(n, edges)
                if surplus: sizes = [s + 1 for s in sizes]
                yield '%s, path of %d, surplus %d' % (name, L, surplus), stars_of(sizes, edges)


if __name__ == '__main__':
    res = collections.Counter(); bad = []; over = []
    for name, stars in family():
        opn, places, B = O.roster(stars)
        for law in ('nae', 'parity'):
            full = O.grow(opn, places, B, T, law, cap=RUN.CAP); n = RUN.readable(full, T)
            if full['end'] == 'stall': res[(law, 'stalls')] += 1; continue
            for k in sorted(opn):
                D = O.dist_from(k, set(opn), B); Vf = RUN.views(full, k, n)
                E = max(D.values())
                for t in range(1, n + 1):
                    r = next((q for q in range(0, E + 1) if RUN.views(O.grow(opn, places, B, t, law,
                              region={v for v in D if D[v] <= q}), k, t) == Vf[:t]), None)
                    ext = 'never (all of the reader piece needed and more)' if r is None else (
                        'the knots within t steps suffice' if r <= t else 'the knots within t + %d steps needed' % (r - t))
                    res[(law, ext)] += 1
                    if (r is None or r > t) and len(bad) < 30: bad.append([name, law, k, t, r, E])
    r = {'tally': {' / '.join(k): v for k, v in sorted(res.items())}, 'differ (first 30)': bad}
    json.dump(r, open(sys.argv[1], 'w'), indent=1); print(json.dumps(r, indent=1)[:2500])
