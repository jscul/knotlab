"""peel.py: the link the advisor offered for the end of a jam, checked at the smallest sizes.  An intuition, not
evidence (intuition-links skill).

The literature's threshold peeling (bootstrap percolation, or pruning to a core with a threshold for each vertex):
a vertex leaves once as many of its neighbours have left as its threshold.  Here: take the two sources and their line
after round 1, when every member is short and waits (jammed); give one member one more loose distinction; then each
member's SHORTFALL is what it owes less what it holds.  If every shortfall is one and a group is lost as soon as any
of its members acts, the member given the distinction acts in round 2 and every other member acts one round after
the first of its group partners: its round is 2 plus its distance from that member in the graph of groups.

Read: the round each member of the jammed roster first acts (is not short, so spends and leaves) in the real growth,
against that prediction, for the two sources at d = 1 to 8 under JOIN-FEWER and ONE-FEWER with waiting, the extra
distinction at each member of the other source's own knots in turn.

    peel.py                  prints the table"""
import sys, os, collections, json
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ring_line
bench, eng = ring_line.bench, ring_line.eng


def check(d, ration, rounds=16):
    stars, role = bench.build('source', 'source', d, None, 'meeting')
    g = ring_line.Growth(stars, role, ring_line.law_of(ration)); g.run(1, 10 ** 6)
    S1 = g.S
    R = eng.build_roster(S1, eng.live_members(S1), 'peel', eng.Guard(1000))
    owe = collections.Counter(u for q in R.groups for u in q)
    gap = {u: owe[u] - R.h[u] for u in R.members}
    adj = collections.defaultdict(set)
    for q in R.groups:
        for u in q: adj[u].update(v for v in q if v != u)
    out = []
    for m in [u for u in R.members if g.anc[u] == frozenset(['B'])]:
        dist = {m: 0}; fr = [m]
        while fr:
            nx_ = []
            for u in fr:
                for v in adj[u]:
                    if v not in dist: dist[v] = dist[u] + 1; nx_.append(v)
            fr = nx_
        h = ring_line.fork_at(g, 1); ring_line.mark(h, m)
        acted = {}
        while h.stop is None and h.S.round < rounds and len(acted) < len(R.members):
            S = h.S; mem = {u: hh for u, hh, k in eng.live_members(S)}
            T = S.copy(); rec = eng.play_round(T, h.law, h.G); h.S = T
            short = set(rec['short'])
            for u in R.members:
                if u not in acted and u in mem and u not in short: acted[u] = T.round
        pred = {u: 2 + dist[u] for u in R.members if u in dist}
        agree = sum(1 for u in R.members if acted.get(u) == pred.get(u))
        out.append({'d': d, 'law': ration, 'marked': m, 'members': len(R.members), 'shortfalls': dict(collections.Counter(gap.values())),
                    'acted': len(acted), 'as predicted': agree,
                    'late by': dict(collections.Counter(str(acted[u] - pred[u]) if u in acted and u in pred else 'none' for u in R.members if acted.get(u) != pred.get(u))),
                    'misses': sorted([(u, g.anc[u] == frozenset(['A']), pred.get(u), acted.get(u)) for u in R.members if acted.get(u) != pred.get(u)])[:6]})
    return out


if __name__ == '__main__':
    rows = []
    for ration in ('JOIN-FEWER', 'ONE-FEWER'):
        for d in range(1, 9):
            rs = check(d, ration); rows += rs
            print(ration, d, 'members', rs[0]['members'], 'shortfalls', rs[0]['shortfalls'], 'marks', len(rs),
                  'all as predicted', sum(1 for r in rs if r['as predicted'] == r['members']), 'members as predicted',
                  sum(r['as predicted'] for r in rs), 'of', sum(r['members'] for r in rs), flush=True)
    json.dump(rows, open(os.path.join(HERE, 'peel.json'), 'w'), indent=0)
