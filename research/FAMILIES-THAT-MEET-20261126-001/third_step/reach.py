"""How far does a cap let one side feel the other?  Third step of FAMILIES-THAT-MEET-20261126-001 (a check by the
thread, not registered), at the owner's word.

The second step held the degree of the second family's own original b2 and changed what lies one step beyond it;
under caps of 6 to 8 the first family's side then differed.  Here the change is moved out.  From b2 a tail of d new
originals is hung, b2 - q1 - ... - qd, the first d - 1 of degree 2, and the last one carries m rings of four
(degree 1 + 2m).  For one d the three starts m = 1, 2, 3 are the same out to d - 1 steps beyond b2 and differ only
at step d.  The knot made from s, b2 and the whole tail would receive 6, 8 or 10 fresh distinctions under the
ordinary count for m = 1, 2, 3, whatever d is, since an original of degree 2 adds nothing to a price.

The first family's side is read as before: the knots that have b1 among their original ancestors and neither b2
nor any new original, each birth as (kind, parents, places, fresh), round by round.

Written BEFORE its first run.  Expected:
 (1) under the ordinary count the first side is the same for the three values of m at every d (argued in the first
     step);
 (2) for d = 1 the first side differs between values of m at caps of 6 to 9 at least, and not at 4 or 5 (the second
     step's finding in another form);
 (3) for d = 2 and d = 3 it differs at some cap from 6 to 12, if the rounds read are enough, and is first seen
     later than for d = 1, by a round or more for each further step.  If nothing shows for d = 3 within the rounds
     read, that is "not seen within those rounds" and no more.  I hold (3) weakly."""
import sys, os, json, time, collections
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'first_step'))
import price                                  # the first step's program: the start, and the shared growth engine
eng = price.eng
import eng_cap                                # written into ../first_step by its make_engine_cap.py

def tail(d, m):
    """b2 - q1 - ... - qd, and m rings of four at qd"""
    pairs = [('b2', 'q1')] + [('q%d' % i, 'q%d' % (i + 1)) for i in range(1, d)]
    end = 'q%d' % d
    for j in range(m):
        x, y, z = ('z%d%d' % (j, k) for k in (1, 2, 3))
        pairs += [(end, x), (x, y), (y, z), (z, end)]
    return pairs

def side(d, m, ration, treatment, knot_law, rounds, bound):
    live, deg, stars = price.source(tail(d, m))
    E = eng_cap if (ration.startswith('CAP-') and ration != 'CAP-3') else eng
    run = E.Run(E.Law(ration, treatment, None, knot_law), stars=stars, rounds=rounds, knot_bound=bound, mult=price.MULT)
    S = run.S
    other = {'b2'} | {x for x in live if x[0] in 'qz'}
    anc = {i: frozenset([x]) for i, x in enumerate(live)}
    for i in range(len(live), len(stars)): anc[i] = frozenset()
    out = []
    for t in range(1, run.rounds_read + 1):
        row = []
        for b in run.recs[t - 1]['births']:
            a = frozenset().union(*[anc[p] for p in b['parents']]); anc[b['id']] = a
            if 'b1' in a and not (a & other):
                row.append((b['kind'], len(b['parents']), len(S.places[b['id']]), b['f']))
        out.append(tuple(sorted(row)))
    return {'degrees': {x: deg[x] for x in ['b2'] + ['q%d' % i for i in range(1, d + 1)]}, 'rounds': run.rounds_read,
            'stop': run.stop, 'knots': S.n_knots, 'side': out}

def side_lean(d, m, ration, treatment, knot_law, rounds, bound):
    """The same reading with one structure in memory: the engine's own round, called directly, and each round's
    record dropped once its births are read.  (The engine's `Run` keeps every round's structure and record; the
    studies at caps of 10 and 12 passed the memory cap that way and were stopped.)"""
    live, deg, stars = price.source(tail(d, m))
    E = eng_cap if (ration.startswith('CAP-') and ration != 'CAP-3') else eng
    law = E.Law(ration, treatment, None, knot_law); G = E.Guard(price.MULT)
    S = E.from_stars(stars); stop = None
    other = {'b2'} | {x for x in live if x[0] in 'qz'}
    anc = {i: frozenset([x]) for i, x in enumerate(live)}
    for i in range(len(live), len(stars)): anc[i] = frozenset()
    out = []
    while stop is None and S.round < rounds:
        T = S.copy()
        try:
            rec = E.play_round(T, law, G)
        except E.GuardStop:
            stop = 'guard'; break
        S = T; row = []
        for b in rec['births']:
            a = frozenset().union(*[anc[p] for p in b['parents']]); anc[b['id']] = a
            if 'b1' in a and not (a & other):
                row.append((b['kind'], len(b['parents']), len(S.places[b['id']]), b['f']))
        out.append(tuple(sorted(row))); del rec
        if S.n_knots > bound: stop = 'knots'
    return {'degrees': {x: deg[x] for x in ['b2'] + ['q%d' % i for i in range(1, d + 1)]}, 'rounds': S.round,
            'stop': stop, 'knots': S.n_knots, 'side': out}

def study(d, ration, treatment, knot_law, rounds, bound, lean=False):
    f = side_lean if lean else side
    s = {m: f(d, m, ration, treatment, knot_law, rounds, bound) for m in (1, 2, 3)}
    R = min(x['rounds'] for x in s.values())
    first = lambda a, b: next((t + 1 for t in range(R) if s[a]['side'][t] != s[b]['side'][t]), None)
    return {'d': d, 'ration': ration, 'treatment': treatment, 'knot law': knot_law, 'rounds compared': R,
            'rounds read': {m: s[m]['rounds'] for m in s}, 'stops': {m: s[m]['stop'] for m in s}, 'knots': {m: s[m]['knots'] for m in s},
            'degrees': {m: s[m]['degrees'] for m in s},
            'births on the first side': {m: sum(len(x) for x in s[m]['side'][:R]) for m in s},
            'first round the side differs': {'1 / 2': first(1, 2), '1 / 3': first(1, 3), '2 / 3': first(2, 3)}}

if __name__ == '__main__':
    spec = json.loads(sys.argv[1])
    t = time.time(); r = study(spec['d'], spec['ration'], spec['treatment'], spec.get('knot_law', 'nae'), spec['rounds'], spec['bound'], spec.get('lean', False))
    r['lean'] = bool(spec.get('lean', False))
    r['seconds'] = round(time.time() - t, 1); print(json.dumps(r))
