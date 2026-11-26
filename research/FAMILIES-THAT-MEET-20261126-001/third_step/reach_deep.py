"""reach_deep.py SPEC: one start of reach.py, read round by round as deep as its limits allow, a line a round.
SPEC is JSON: d, m, ration, treatment, rounds, bound, and optionally take and choice (a taking rule of the engine, for the swap
of drive_take.py; without it nothing is taken, as in every other run of this step; added after drive_deep.py ran).

Written after the first two passes (drive_reach.py, drive_reach_second.py), for three reasons found in them.
(a) reach.py compared its three starts on the rounds all three had read, so a pair that had both read a further
    round was not compared on it.  Here each start is its own run and pairs are compared afterwards (tally_deep.py).
(b) A start stopped by the memory cap lost every round it had read.  Here each round is printed as it is read.
(c) The first side's births say whether it differed, not whether it could have.  Here each round also counts the
    groups that hold a knot with nothing of the second family in its descent together with a knot that has some:
    the only joins through which one side can change the other (README, "Why"), and how many of them were kept.

Sides, by original ancestors: `second` has b2 or an original of the tail; `first` has b1 and nothing of the second;
`rest` has neither.  Two readings of what is outside the second side are kept as digests:
    first      the first side's births as the sorted list of (kind, parents, places, fresh), as reach.py reads it;
    outside    every birth outside the second side, by name and fresh count, a knot's name being how it was made
               (kind, parents' names, number among equal births of the round): equal digests through a round mean
               the same knots, made the same way and given the same, in both starts."""
import sys, os, json, time, hashlib, collections
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); import reach
price, eng, eng_cap = reach.price, reach.eng, reach.eng_cap

def run(spec):
    d, m, ration, treatment = spec['d'], spec['m'], spec['ration'], spec['treatment']
    live, deg, stars = price.source(reach.tail(d, m))
    E = eng_cap if (ration.startswith('CAP-') and ration != 'CAP-3') else eng
    law = E.Law(ration, treatment, spec.get('take'), 'nae', spec.get('choice')); G = E.Guard(price.MULT)
    S = E.from_stars(stars)
    other = {'b2'} | {x for x in live if x[0] in 'qz'}
    side = {}; name = {}
    for i, x in enumerate(live):
        side[i] = 'second' if x in other else ('first' if x == 'b1' else 'rest')
        if side[i] != 'second': name[i] = x
    for i in range(len(live), len(stars)): side[i] = 'witness'                # spent: never a member, never a parent
    def of(ps):
        s = {side[p] for p in ps}
        return 'second' if 'second' in s else ('first' if 'first' in s else 'rest')
    t0 = time.time()
    while S.round < spec['rounds']:
        T = S.copy()
        try: rec = E.play_round(T, law, G)
        except E.GuardStop:
            print(json.dumps({'stop': 'guard'}), flush=True); return
        S = T
        short = set(rec['short']); cross = collections.Counter()
        for g in rec['groups']:
            s = {side[u] for u in g}
            if 'second' in s and len(s) > 1:
                kept = not any(u in short for u in g)
                for x in s - {'second'}:
                    cross[x] += 1
                    if kept: cross[x + ' kept'] += 1
                cross['any'] += 1
                if kept: cross['any kept'] += 1
        mem = collections.Counter(side[u] for u in rec['members'])
        sh = collections.Counter(side[u] for u in short)
        first = []; outside = []; seen = collections.Counter()
        for b in rec['births']:
            s = of(b['parents']); side[b['id']] = s
            if s == 'second': continue
            ps = tuple(sorted(name[p] for p in b['parents']))
            key = (b['kind'], ps); k = seen[key]; seen[key] += 1
            n = hashlib.sha1(repr((b['kind'], ps, k)).encode()).hexdigest()[:16]; name[b['id']] = n
            outside.append((n, b['f']))
            if s == 'first': first.append((b['kind'], len(b['parents']), len(S.places[b['id']]), b['f']))
        first.sort(); outside.sort()
        print(json.dumps({'round': S.round, 'knots': S.n_knots, 'groups': len(rec['groups']), 'members': dict(mem), 'short': dict(sh),
                          'groups joining the sides': cross['any'], 'of them kept': cross['any kept'],
                          'with a first-side member': [cross['first'], cross['first kept']], 'with a member of the rest': [cross['rest'], cross['rest kept']],
                          'first': [len(first), hashlib.sha1(repr(first).encode()).hexdigest()[:16]],
                          'outside': [len(outside), hashlib.sha1(repr(outside).encode()).hexdigest()[:16]],
                          'births that took a distinction': sum(1 for b in rec['births'] if b['takes']),
                          'seconds': round(time.time() - t0, 1)}), flush=True)
        del rec
        if S.n_knots > spec['bound']:
            print(json.dumps({'stop': 'knots'}), flush=True); return
    print(json.dumps({'stop': 'rounds'}), flush=True)

if __name__ == '__main__':
    run(json.loads(sys.argv[1]))
