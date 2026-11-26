"""table_check.py K [ROUNDS]: a check of a link (intuition-links), made when the bench's toy showed the knots of both
of two two-knot parts numbering n(n + 1) after n rounds.

K two-knot parts whose first knots all hold one new distinction, grown under the ordinary count (a short knot
waits).  Every knot is given, for each part, the latest round in which an ancestor of it was made that is that
part's own (0 for a start knot): its PLACE along that part's own line.  Read:
  (1) the knots with every part in their descent, round by round, by their K places;
  (2) the parents of such a knot, by their places;
  (3) the balls around one such knot: how many knots lie within r sharings of it, a sharing being one distinction
      held in common, over the whole structure.
If the knots of all K parts are a K-way table of the parts' own lines, (1) gives the same number of knots for every
K places that add up to the round (less what the first rounds lose), (2) gives parents one place back along one
line, and (3) grows as the K-th power of r."""
import sys, json, collections
import bench
eng = bench.eng
K = int(sys.argv[1]); ROUNDS = int(sys.argv[2]) if len(sys.argv) > 2 else 10
two = [[0, 1, 2], [0, 3, 4]]
stars, role, nxt = [], [], 0
for i in range(K):
    stars += [[nxt + d for d in kn] for kn in two]; role += [i] * 2; nxt += 5
for i in range(K): stars[2 * i].append(nxt)
S = eng.from_stars(stars); G = eng.Guard(100); L = eng.Law('ORD', 'CANCEL-WAIT', None, 'nae')
anc = {i: frozenset([r]) for i, r in enumerate(role)}
place = {i: tuple(0 if r == k else None for k in range(K)) for i, r in enumerate(role)}
made = {i: 0 for i in range(len(role))}
out = {'parts': K, 'rounds': [], 'parents of a knot of all parts, by place steps back': None}
steps = collections.Counter()
for t in range(1, ROUNDS + 1):
    T = S.copy(); rec = eng.play_round(T, L, G); S = T
    cells = collections.Counter()
    for b in rec['births']:
        a = frozenset().union(*[anc[p] for p in b['parents']]); anc[b['id']] = a; made[b['id']] = t
        pl = [None] * K
        for p in b['parents']:
            for k in range(K):
                if place[p][k] is not None: pl[k] = max(pl[k] or 0, place[p][k])
        if len(a) == 1: pl[next(iter(a))] = t
        place[b['id']] = tuple(pl)
        if len(a) == K:
            cells[tuple(pl)] += 1
            for p in b['parents']:
                if len(anc[p]) == K: steps[tuple(x - y for x, y in zip(pl, place[p]))] += 1
                else: steps['a parent not of all parts'] += 1
    sums = collections.Counter(sum(c) for c in cells)
    out['rounds'].append({'round': t, 'knots of all parts': sum(cells.values()), 'different places': len(cells),
                          'knots at one place (min, max)': [min(cells.values(), default=0), max(cells.values(), default=0)],
                          'places add up to': dict(sums), 'short': len(rec['short']), 'knots': S.n_knots})
out['parents of a knot of all parts, by place steps back'] = {str(k): v for k, v in steps.most_common()}
# balls: sharings over the whole structure, around a knot of all parts made near the middle round at a middle place
adj = collections.defaultdict(set)
for holders in S.holders:
    for u in holders:
        for v in holders:
            if u != v: adj[u].add(v)
mid = [u for u in range(S.n_knots) if len(anc.get(u, ())) == K and made[u] == (ROUNDS * 2) // 3]
mid.sort(key=lambda u: max(place[u]) - min(place[u]))
if mid:
    c = mid[0]; dist = {c: 0}; frontier = [c]
    while frontier:
        nx = []
        for u in frontier:
            for v in adj[u]:
                if v not in dist: dist[v] = dist[u] + 1; nx.append(v)
        frontier = nx
    balls = collections.Counter(dist.values()); tot = 0; ball = []
    for r in range(0, max(balls) + 1):
        tot += balls[r]; ball.append(tot)
    out['ball around the knot at places %s made in round %d, by sharings' % (place[c], made[c])] = ball[:ROUNDS]
print(json.dumps(out, indent=1))
