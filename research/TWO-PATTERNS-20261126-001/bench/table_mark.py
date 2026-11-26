"""table_mark.py [ROUNDS]: the first step of the link's test (README, "A link, checked").  Two two-knot parts whose
first knots share one distinction, under the ordinary count, grown twice: as they are, and with a MARK, one more
loose distinction at a start knot of the first part (its first knot, then its other knot).  Every knot of both is
read at its place (i, j) along the two parts' own lines.  Where in the table does the mark show: at which places
does the number of knots, or what they hold (places and fresh distinctions), differ?"""
import sys, json, collections
import bench
eng = bench.eng
ROUNDS = int(sys.argv[1]) if len(sys.argv) > 1 else 10
two = [[0, 1, 2], [0, 3, 4]]
def grow(mark):
    stars = [list(k) for k in two] + [[5 + d for d in k] for k in two]; role = [0, 0, 1, 1]
    stars[0].append(10); stars[2].append(10)
    if mark is not None: stars[mark].append(11)
    S = eng.from_stars(stars); G = eng.Guard(100); L = eng.Law('ORD', 'CANCEL-WAIT', None, 'nae')
    anc = {i: frozenset([r]) for i, r in enumerate(role)}
    place = {i: tuple(0 if r == k else None for k in (0, 1)) for i, r in enumerate(role)}
    table = collections.defaultdict(list); own = collections.Counter(); short = 0
    for t in range(1, ROUNDS + 1):
        T = S.copy(); rec = eng.play_round(T, L, G); S = T; short += len(rec['short'])
        for b in rec['births']:
            a = frozenset().union(*[anc[p] for p in b['parents']]); anc[b['id']] = a
            pl = [None, None]
            for p in b['parents']:
                for k in (0, 1):
                    if place[p][k] is not None: pl[k] = max(pl[k] or 0, place[p][k])
            if len(a) == 1: pl[next(iter(a))] = t; own[(next(iter(a)), t)] += 1
            place[b['id']] = tuple(pl)
            if len(a) == 2: table[tuple(pl)].append((len(S.places[b['id']]), b['f']))
    return {k: sorted(v) for k, v in table.items()}, own, short, S.n_knots
base, own0, s0, n0 = grow(None)
out = {'rounds': ROUNDS, 'unmarked': {'knots': n0, 'short members, all rounds': s0, 'places of the table': len(base)}}
for mark, what in ((0, "the first part's first knot (its site)"), (1, "the first part's other knot")):
    t, own, s, n = grow(mark)
    dif = sorted(k for k in set(base) | set(t) if base.get(k) != t.get(k))
    more = sorted(k for k in dif if len(t.get(k, [])) != len(base.get(k, [])))
    out['mark at ' + what] = {
        'knots': n, 'short members, all rounds': s,
        "the first part's own births by round": [own[(0, r)] for r in range(1, ROUNDS + 1)], "unmarked": [own0[(0, r)] for r in range(1, ROUNDS + 1)],
        "the second part's own births by round": [own[(1, r)] for r in range(1, ROUNDS + 1)],
        'places of the table that differ': len(dif), 'of them with another number of knots': len(more),
        'places that differ, by place along the first line': dict(sorted(collections.Counter(k[0] for k in dif).items())),
        'places that differ, by place along the second line': dict(sorted(collections.Counter(k[1] for k in dif).items())),
        'places of the table in the marked growth': len(t), 'examples': [(k, base.get(k), t.get(k)) for k in dif[:4]]}
print(json.dumps(out, indent=1))
