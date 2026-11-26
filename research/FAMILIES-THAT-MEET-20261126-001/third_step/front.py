"""front.py SPEC: how far a difference between two starts of reach.py has travelled, round by round.
SPEC is JSON: d, ration, treatment, rounds, bound, ma, mb.

Every knot is named by how it was made (kind, parents' names, and its number among equal births of the round), so
a knot made the same way has the same name in both starts.  Knots are sorted by the furthest part of the second
family they are made from:
    end     made from the tail's last original q_d or from a ring on it (where the two starts differ)
    q_i     made from q_i (i < d) and from nothing further out
    b2      made from b2 and from nothing of the tail
    first   made from b1 and from nothing of b2 or the tail (the first family's side, as reach.py reads it)
    rest    made from neither b1 nor b2 nor the tail
For each round and each sort: knots made in one start only, and knots made in both that were owed a different
number of joins at birth (the engine's demand D), knots given a different number of fresh distinctions, and knots
owed more than the cap in one start and not in the other (short in one start only: the one way a knot made in both
starts can act differently in the next round).  One structure in memory at a time (the engine's round called
directly)."""
import sys, os, json, collections, hashlib
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); import reach
price, eng, eng_cap = reach.price, reach.eng, reach.eng_cap

def sort_of(a, d):
    if any(x[0] == 'z' for x in a) or ('q%d' % d) in a: return 'end'
    for i in range(d - 1, 0, -1):
        if ('q%d' % i) in a: return 'q%d' % i
    if 'b2' in a: return 'b2'
    return 'first' if 'b1' in a else 'rest'

def grow(d, m, ration, treatment, rounds, bound):
    live, deg, stars = price.source(reach.tail(d, m))
    E = eng_cap if (ration.startswith('CAP-') and ration != 'CAP-3') else eng
    law = E.Law(ration, treatment, None, 'nae'); G = E.Guard(price.MULT)
    S = E.from_stars(stars); stop = None
    name = {i: x for i, x in enumerate(live)}; anc = {i: frozenset([x]) for i, x in enumerate(live)}
    for i in range(len(live), len(stars)): name[i] = 'w%d' % i; anc[i] = frozenset()
    rows = []
    while stop is None and S.round < rounds:
        T = S.copy()
        try: rec = E.play_round(T, law, G)
        except E.GuardStop: stop = 'guard'; break
        S = T; row = {}; seen = collections.Counter(); short = set(rec['short'])
        for b in rec['births']:
            ps = tuple(sorted(name[p] for p in b['parents']))
            key = (b['kind'], ps); k = seen[key]; seen[key] += 1
            n = hashlib.sha1(repr((b['kind'], ps, k)).encode()).hexdigest()[:14]
            name[b['id']] = n
            a = frozenset().union(*[anc[p] for p in b['parents']]); anc[b['id']] = a
            row[n] = (sort_of(a, d), b['D'], b['f'])
        acts = collections.Counter((sort_of(anc[u], d), rec['act'][u]) for u in rec['members'])
        rows.append((row, acts)); del rec
        if S.n_knots > bound: stop = 'knots'
    return rows, stop

def compare(spec):
    d = spec['d']
    A, sa = grow(d, spec['ma'], spec['ration'], spec['treatment'], spec['rounds'], spec['bound'])
    B, sb = grow(d, spec['mb'], spec['ration'], spec['treatment'], spec['rounds'], spec['bound'])
    sorts = ['end'] + ['q%d' % i for i in range(d - 1, 0, -1)] + ['b2', 'first', 'rest']
    cap = int(spec['ration'][4:]) if spec['ration'].startswith('CAP-') else 10 ** 9
    out = {'spec': spec, 'stops': [sa, sb], 'rounds compared': min(len(A), len(B)), 'sorts': sorts, 'rounds': []}
    for t in range(min(len(A), len(B))):
        (ra, aa), (rb, ab) = A[t], B[t]
        line = {'round': t + 1}
        for s in sorts:
            na = {n for n, v in ra.items() if v[0] == s}; nb = {n for n, v in rb.items() if v[0] == s}
            both = na & nb
            line[s] = {'made in both': len(both), 'only in m=%d' % spec['ma']: len(na - nb), 'only in m=%d' % spec['mb']: len(nb - na),
                       'in both, owed differently': sum(1 for n in both if ra[n][1] != rb[n][1]),
                       'in both, given differently': sum(1 for n in both if ra[n][2] != rb[n][2]),
                       'in both, over the cap in one only': sum(1 for n in both if (ra[n][1] > cap) != (rb[n][1] > cap)),
                       'short members m=%d' % spec['ma']: sum(v for (ss, a), v in aa.items() if ss == s and a != 'none'),
                       'short members m=%d' % spec['mb']: sum(v for (ss, a), v in ab.items() if ss == s and a != 'none')}
        out['rounds'].append(line)
    return out

if __name__ == '__main__':
    r = compare(json.loads(sys.argv[1]))
    if '--table' in sys.argv:
        s = r['spec']; a, b = 'only in m=%d' % s['ma'], 'only in m=%d' % s['mb']
        print('d = %d, %s, %s, m = %d against %d; stops %s' % (s['d'], s['ration'], s['treatment'], s['ma'], s['mb'], r['stops']))
        print('round  ' + '  '.join('%-22s' % x for x in r['sorts']))
        for line in r['rounds']:
            print('%5d  ' % line['round'] + '  '.join('%-22s' % ('%d =, %d|%d, D%d X%d' % (line[x]['made in both'], line[x][a], line[x][b], line[x]['in both, owed differently'], line[x]['in both, over the cap in one only'])) for x in r['sorts']))
    else:
        print(json.dumps(r))
