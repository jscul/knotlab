"""A second computation of every take, written from the rule's words and not from the engine's code.  For each birth of
a run, from the places of the knots at the start of its round alone: the knots within reach of each parent (one holder
step, or two under MET2), the distinctions on offer (held by two or more knots, held by a knot within reach of every
parent, not held by a parent), and the one the rule selects.  Compared with what the engine's birth took."""
import sys, json, collections
import scan2
from scan2 import eng, stars_of
def takes_by_rule(places, parents, take):
    holders = collections.defaultdict(set)
    for u, ps in enumerate(places):
        for d in ps: holders[d].add(u)
    def near(u):
        out = set()
        for d in places[u]: out |= holders[d]
        out.discard(u); return out
    def within(p):
        a = near(p)
        if take.startswith('MET2'):
            b = set(a)
            for w in a: b |= near(w)
            b.discard(p); return b
        return a
    common = None
    for p in parents:
        r = within(p); common = r if common is None else common & r
    common -= set(parents)
    held = set()
    for p in parents: held |= set(places[p])
    offer = sorted({d for w in common for d in places[w] if len(holders[d]) >= 2 and d not in held})
    if not offer: return []
    if take.endswith('-SOLE'): return offer if len(offer) == 1 else []
    if take.endswith('-ALL'): return offer
    n = [len(holders[d]) for d in offer]
    best = max(n) if take.endswith('-MANY') else min(n)
    return [offer[n.index(best)]] if n.count(best) == 1 else []
spec = json.loads(sys.argv[1])
law = eng.Law(spec['ration'], spec['treatment'], spec['take'], spec['knot_law'])
run = eng.Run(law, stars=stars_of(spec['start']), rounds=7)
births = same = took = 0; bad = []
for t in range(1, run.rounds_read + 1):
    S = run.snaps[t - 1]
    for b in run.recs[t - 1]['births']:
        births += 1
        mine = takes_by_rule(S.places, list(b['parents']), spec['take'])
        took += bool(b['takes'])
        if sorted(mine) == sorted(b['takes']): same += 1
        elif len(bad) < 3: bad.append((t, b['kind'], b['parents'], b['takes'], mine))
print(json.dumps({'start': spec['start'], 'law': law.name(), 'rounds': run.rounds_read, 'births': births, 'births that took': took, 'same as the rule': same, 'first disagreements': bad}))
