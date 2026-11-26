"""Under a cap, does more than one count cross?  Second step of FAMILIES-THAT-MEET-20261126-001 (a check by the
thread, not registered).

The first step changed one number on the generator study's 21-knot start, the degree of the second family's own
original b2 (2 or 4), and under a cap of 4 to 8 the first family's side then made something else.  That is "how
much the other side asks".  Here the number is held and what lies beyond it is changed.  Three starts give b2 the
same degree 4, so that the knots b2 shares with the first family's originals are asked for the same number of
joins in each, and differ one step further out:
  ring    b2 is on one ring of four with three new originals of degree 2 (the first step's change);
  two     b2 has two new partners, each on a ring of four of its own: the partners have degree 3;
  four    b2 has two new partners, each on two rings of four: the partners have degree 5.
The first family's side is read as before: the knots that have b1 among their original ancestors and neither b2
nor any new original, each birth as (kind, parents, places, fresh), round by round.

Written BEFORE its first run.  Expected: under the ordinary count the three starts give the same side (argued in
the first step: a knot's making depends on its own originals only).  Under a cap of 4 to 8: the sides differ
between the three starts for at least one cap and treatment, and where they do, a round or more after the round in
which the start as given and `ring` part.  The reason I expect it: a knot holding b2 is asked for a join by each
of its sibling knots that exists, and whether the siblings further out exist depends, under a cap, on whether
knots holding the new originals were paid.  I hold this weakly."""
import sys, os, json, time, collections
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'first_step'))
import price                                  # the first step's program: the start, and the shared growth engine
eng = price.eng
import eng_cap                                # written into ../first_step by its make_engine_cap.py

def ring(a, names):
    """a ring of four through `a` with three new originals"""
    x, y, z = names
    return [(a, x), (x, y), (y, z), (z, a)]

VARIANTS = collections.OrderedDict([
    ('as given', []),
    ('ring', ring('b2', ('q1', 'q2', 'q3'))),
    ('two', [('b2', 'q1'), ('b2', 'p1')] + ring('q1', ('q2', 'q3', 'q4')) + ring('p1', ('p2', 'p3', 'p4'))),
    ('four', [('b2', 'q1'), ('b2', 'p1')] + ring('q1', ('q2', 'q3', 'q4')) + ring('q1', ('q5', 'q6', 'q7'))
             + ring('p1', ('p2', 'p3', 'p4')) + ring('p1', ('p5', 'p6', 'p7'))),
])

def side(variant, ration, treatment, knot_law, rounds, bound):
    live, deg, stars = price.source(VARIANTS[variant])
    E = eng_cap if (ration.startswith('CAP-') and ration != 'CAP-3') else eng
    run = E.Run(E.Law(ration, treatment, None, knot_law), stars=stars, rounds=rounds, knot_bound=bound, mult=price.MULT)
    S = run.S
    other = {'b2'} | {x for x in live if x[0] in 'qp'}
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
    return {'degree of b2': deg['b2'], 'degrees of its new partners': sorted(deg[x if a == 'b2' else a] for a, x in VARIANTS[variant] if 'b2' in (a, x)),
            'rounds': run.rounds_read, 'stop': run.stop, 'knots': S.n_knots, 'side': out}

def study(ration, treatment, knot_law, rounds, bound):
    s = {v: side(v, ration, treatment, knot_law, rounds, bound) for v in VARIANTS}
    R = min(x['rounds'] for x in s.values())
    first = lambda a, b: next((t + 1 for t in range(R) if s[a]['side'][t] != s[b]['side'][t]), None)
    return {'ration': ration, 'treatment': treatment, 'knot law': knot_law, 'rounds compared': R,
            'stops': {v: s[v]['stop'] for v in VARIANTS}, 'knots': {v: s[v]['knots'] for v in VARIANTS},
            'degree of b2': {v: s[v]['degree of b2'] for v in VARIANTS},
            'degrees of the new partners of b2': {v: s[v]['degrees of its new partners'] for v in VARIANTS},
            'births on the first side': {v: sum(len(x) for x in s[v]['side'][:R]) for v in VARIANTS},
            'first round the side differs': {'as given / ring': first('as given', 'ring'), 'ring / two': first('ring', 'two'),
                                             'ring / four': first('ring', 'four'), 'two / four': first('two', 'four')}}

if __name__ == '__main__':
    rounds = int(sys.argv[1]); bound = int(sys.argv[2])
    rows = []
    for ration in ['ORD'] + ['CAP-%d' % c for c in (2, 3, 4, 5, 6, 7, 8)]:
        for treatment in ('CANCEL-RETIRE', 'CANCEL-OFFSHOOT', 'CANCEL-WAIT'):
            for knot_law in ('nae', 'parity'):
                t = time.time(); r = study(ration, treatment, knot_law, rounds, bound); r['seconds'] = round(time.time() - t, 1)
                rows.append(r); print(json.dumps(r), flush=True)
