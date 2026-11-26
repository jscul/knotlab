"""One loose distinction fewer: does the side of the first family then make something else when the second family's
mark is changed?  Second part of the first step on sub-goal B337 as restated (a check by the thread, not registered).

The generator study's 21-knot start is funded: every live original has as many loose distinctions as candidate
pairs, and there the knots whose clusters avoid an original are the same whatever is done to that original
(price.py).  Here one live original is given ONE loose distinction fewer, so that it owes more joins than it can pay,
and the law's treatment of a short knot comes into play (it retires, makes offshoots, or waits).  For each such
start, the mark b2 of the second family is changed as in price.py (two more candidate pairs: degree 4 for 2), and
the births on the first family's side are compared round by round: the knots that have b1 among their original
ancestors and neither b2 nor the new originals, each as (kind, number of parents, number of places, fresh).

Written BEFORE its first run.  Expected: with nothing short the two sources agree (known from price.py); with s or
with t short the sides differ under at least one treatment; I do not know for the other originals.

Added AFTER that run, in which the expectation failed (0 of 60 comparisons differ: an original short at the start is
short in round 1 only, and under the ordinary count every made knot receives as many fresh distinctions as it is
asked for joins, so nothing made is ever short).  Third part, written before its own first run: the same funded
start under the two capped rations of the record (the cap of three; just enough for three places), where a made knot
can be asked for more joins than it holds.  Expected: the first family's side differs with the change at b2 under at
least one treatment for each capped ration.

Added AFTER that run, in which the expectation failed again (0 of 12 differ: under a cap of three or less, every
knot that holds b2 is asked for more than three joins in BOTH sources, so it is short in both, and the growth
nearly stops).  Fourth part, written before its own first run, with a reason this time.  A made knot Y whose cluster
holds b2 is asked for about as many joins as its cluster has one-point additions, which is 2 more in the changed
source for each time it holds b2; under a cap c it receives at most c fresh distinctions.  So for a cap between the
two numbers Y is paid in full in one source and short in the other.  A short knot's joins are cancelled, and a knot
X of the first side that shares a parent with Y then keeps a distinction it would have given to their join, and
makes something else with it.  The smallest such pair: X = {v, s, b1} and Y = {s, b1, b2}, asked for 4 joins as
given and 6 changed.  Expected: the first side differs for every cap from 4 to 8, under each treatment, first in
round 3 or 4; it does not differ at cap 2 or 3 (seen for 3) nor under the ordinary count (seen)."""
import sys, os, json, collections
import price
from price import eng
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
try:
    import eng_cap                       # written by make_engine_cap.py
except ImportError:
    eng_cap = None

def start(short=None, extra=()):
    live, deg, stars = price.source(extra)
    if short is not None:
        i = live.index(short); mine = stars[i]
        owners = collections.Counter(d for k in stars for d in k)
        loose = [d for d in mine if owners[d] == 1]
        stars[i] = [d for d in mine if d != loose[-1]]                 # one loose distinction fewer (its name stays unused)
    return live, stars

def side(short, treatment, knot_law, extra, rounds, ration='ORD'):
    live, stars = start(short, extra)
    E = eng_cap if (ration.startswith('CAP-') and ration != 'CAP-3') else eng
    law = E.Law(ration, treatment, None, knot_law)
    run = E.Run(law, stars=stars, rounds=rounds, knot_bound=20000, mult=price.MULT)
    S = run.S
    anc = {i: frozenset([x]) for i, x in enumerate(live)}
    for i in range(len(live), len(stars)): anc[i] = frozenset()
    other = {'b2', 'q1', 'q2', 'q3'}
    out = []; nshort = 0
    for t in range(1, run.rounds_read + 1):
        rec = run.recs[t - 1]; nshort += len(rec['short']); row = []
        for b in rec['births']:
            a = frozenset().union(*[anc[p] for p in b['parents']]); anc[b['id']] = a
            if 'b1' in a and not (a & other):
                row.append((b['kind'], len(b['parents']), len(S.places[b['id']]), b['f']))
        out.append(tuple(sorted(row)))
    return {'rounds': run.rounds_read, 'stop': run.stop, 'knots': S.n_knots, 'short knot rounds': nshort, 'side': out}

def compare(short, treatment, knot_law, rounds, ration='ORD'):
    a = side(short, treatment, knot_law, (), rounds, ration); b = side(short, treatment, knot_law, price.CHANGED, rounds, ration)
    R = min(a['rounds'], b['rounds'])
    first = next((t + 1 for t in range(R) if a['side'][t] != b['side'][t]), None)
    return {'ration': ration, 'short': short, 'treatment': treatment, 'knot law': knot_law, 'rounds compared': R, 'stops': [a['stop'], b['stop']],
            'knots': [a['knots'], b['knots']], 'rounds with a short knot': [a['short knot rounds'], b['short knot rounds']],
            'births on the first side': [sum(len(x) for x in a['side'][:R]), sum(len(x) for x in b['side'][:R])],
            'first round the side differs': first,
            'example': None if first is None else {'as given': collections.Counter(a['side'][first - 1]).most_common(4), 'changed': collections.Counter(b['side'][first - 1]).most_common(4)}}

def capped(rounds):
    return [compare(None, treatment, knot_law, rounds, ration) for ration in ('CAP-3', 'FLOOR1') for knot_law in ('nae', 'parity')
            for treatment in ('CANCEL-RETIRE', 'CANCEL-OFFSHOOT', 'CANCEL-WAIT')]

def caps(rounds):
    return [compare(None, treatment, knot_law, rounds, 'CAP-%d' % c) for c in (2, 3, 4, 5, 6, 7, 8) for knot_law in ('nae', 'parity')
            for treatment in ('CANCEL-RETIRE', 'CANCEL-OFFSHOOT', 'CANCEL-WAIT')]

if __name__ == '__main__':
    rounds = int(sys.argv[1]) if len(sys.argv) > 1 else 6
    if len(sys.argv) > 2 and sys.argv[2] == 'caps':
        print(json.dumps(caps(rounds))); sys.exit()
    if len(sys.argv) > 2 and sys.argv[2] == 'capped':
        print(json.dumps(capped(rounds))); sys.exit()
    rows = []
    for knot_law in ('nae', 'parity'):
        for treatment in ('CANCEL-RETIRE', 'CANCEL-OFFSHOOT', 'CANCEL-WAIT'):
            for short in (None, 'v', 'r1', 'r2', 'r3', 's', 't', 'b0', 'b1', 'b2'):
                rows.append(compare(short, treatment, knot_law, rounds))
    print(json.dumps(rows))
