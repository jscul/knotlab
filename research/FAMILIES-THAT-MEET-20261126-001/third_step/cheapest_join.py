"""cheapest_join.py SPEC: why the sides come apart in round c - 1.  SPEC is JSON: d, m, rounds, bound.

Written at the epic's close as the check of a link (the note's "round c - 1" was counted, not explained).  Under
the ordinary count a knot is given as many fresh distinctions as joins it is owed: its price, which by the
generator line's formula is 2 plus the sum over its originals of (pairs - 2), the number of pair-ends leaving its
cluster.  A cap of c makes short every knot whose price is above c, and a group with a short member is cancelled.
So a group joining the sides can be kept under a cap of c only if its dearest member's price is at most c.

This program grows the start under the ordinary count and, for each round t, takes over the groups joining the
sides the least value of the dearest member's loose count (its price).  If that least value is t + 3, then under a
cap of c the groups of round t can be kept only while t + 3 <= c, the last kept ones are in round c - 3, their
joins make the last groups joining the sides in round c - 2, all cancelled, and none is left in round c - 1.

Result (cheapest_join.jsonl; five starts, 8 or 9 rounds): the candidate FAILS.  The least value is 4, 5, 5 in the
first three rounds and 7 in every round from the fourth to the ninth, in all five starts.  Under the ordinary
count a group joining the sides with no member dearer than 7 is there in every round, so prices under the
ordinary count do not give round c - 1; a growth under a cap has lost the knots those groups are made from."""
import sys, os, json
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); import reach
price, eng = reach.price, reach.eng

def run(spec):
    d, m = spec['d'], spec['m']
    live, deg, stars = price.source(reach.tail(d, m))
    law = eng.Law('ORD', 'CANCEL-RETIRE', None, 'nae'); G = eng.Guard(price.MULT)
    S = eng.from_stars(stars)
    other = {'b2'} | {x for x in live if x[0] in 'qz'}
    side = {i: ('second' if x in other else 'outside') for i, x in enumerate(live)}
    for i in range(len(live), len(stars)): side[i] = 'witness'
    out = []
    while S.round < spec['rounds'] and S.n_knots <= spec['bound']:
        T = S.copy(); rec = eng.play_round(T, law, G); S = T
        cross = [g for g in rec['groups'] if len({side[u] for u in g}) > 1]
        least = min((max(rec['h'][u] for u in g) for g in cross), default=None)
        out.append({'round': S.round, 'groups joining the sides': len(cross), 'least dearest member': least,
                    'round + 3': S.round + 3, 'short members': len(rec['short'])})
        for b in rec['births']:
            side[b['id']] = 'second' if any(side[p] == 'second' for p in b['parents']) else 'outside'
        del rec
    return {'spec': spec, 'rounds': out, 'least dearest member is round + 3 in every round read': all(x['least dearest member'] == x['round + 3'] for x in out)}

if __name__ == '__main__':
    print(json.dumps(run(json.loads(sys.argv[1]))))
