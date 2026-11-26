"""made_mark.py A B D: a mark set at a made knot.  (Added after the reach table, which showed that a mark at a start
knot leaves every knot of the joint descent a join of two owed two, so that no ration can tell one from another.
A mark at a made knot makes one place irregular: its children are owed one more.)

Receiver A and sender B (indices into reach.PATTERNS) are joined at distance D and grown to round R0 = 6.  Then,
for each knot K made in round R0 that is not one of A's own, in turn, K is given one more loose distinction by
hand and the growth goes on to round 16 beside the unmarked one, under the same law.  Read: the first round A's
own births differ, and K's distance at round R0, in sharings (a distinction held in common), from the nearest of
A's own knots.  Laws: the ordinary count, ODD-FEWER and BUSY-FEWER, with each treatment.  A line a law."""
import sys, json, collections
import reach
bench, eng, rations = reach.bench, reach.eng, reach.rations
R0, ROUNDS, BOUND = 6, 16, 3000

def fork(g):
    h = reach.Growth.__new__(reach.Growth); h.law = g.law; h.G = eng.Guard(bench.MULT); h.S = g.S.copy()
    h.anc = dict(g.anc); h.name = dict(g.name); h.rows = list(g.rows); h.stop = g.stop
    return h

def distances(g):
    """sharings from the nearest of A's own knots, for every knot"""
    S = g.S; adj = collections.defaultdict(set)
    for holders in S.holders:
        for u in holders:
            for v in holders:
                if u != v: adj[u].add(v)
    dist = {u: 0 for u in range(S.n_knots) if g.anc.get(u) == frozenset(['A'])}; frontier = list(dist)
    while frontier:
        nx = []
        for u in frontier:
            for v in adj[u]:
                if v not in dist: dist[v] = dist[u] + 1; nx.append(v)
        frontier = nx
    return dist

def study(A, B, d, ration, treatment):
    law = bench.LAWS[ration](treatment, None) if ration in bench.LAWS else eng.Law(ration, treatment, None, 'nae')
    stars, role = bench.build(A, B, d, None, 'meeting')
    g = reach.Growth(stars, role, law); g.run(R0, BOUND)
    if len(g.rows) < R0: return {'law': [ration, treatment], 'not grown to round': R0}
    dist = distances(g); S = g.S
    targets = [u for u in range(S.n_knots) if S.made[u] == R0 and g.anc[u] != frozenset(['A'])]
    whole = fork(g); whole.run(ROUNDS, BOUND)
    out = {'A': A, 'B': B, 'd': d, 'law': [ration, treatment], 'knots at round %d' % R0: S.n_knots, 'rounds': len(whole.rows), 'marks': []}
    for K in targets:
        h = fork(g); x = len(h.S.holders)
        h.S.places[K].append(x); h.S.holders.append([K]); h.S.barred.append(False); h.S.maker.append(K)
        h.run(ROUNDS, BOUND)
        n = min(len(whole.rows), len(h.rows))
        own = next((whole.rows[i]['round'] for i in range(R0, n) if whole.rows[i]['own'] != h.rows[i]['own']), None)
        a = g.anc[K]; cls = 'own B' if a == frozenset(['B']) else 'joint' if ('A' in a and 'B' in a) else 'link side'
        out['marks'].append([cls, dist.get(K), own, n, sum(1 for i in range(R0, n) if h.rows[i]['short'] and not whole.rows[i]['short'])])
    return out

if __name__ == '__main__':
    reach.register()
    A, B, d = reach.PATTERNS[int(sys.argv[1])], reach.PATTERNS[int(sys.argv[2])], int(sys.argv[3])
    for ration in ('ORD', 'ODD-FEWER', 'BUSY-FEWER'):
        for treatment in reach.TREATMENTS:
            print(json.dumps(study(A, B, d, ration, treatment)), flush=True)
