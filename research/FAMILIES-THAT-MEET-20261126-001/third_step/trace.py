"""trace.py SPEC: where the first family's side first differs between two starts of reach.py, and why.
SPEC is JSON: d, ration, treatment, rounds, ma, mb (the two values of m), optional bound.

Every knot is named by how it was made (its kind, its parents' names, and for an offshoot its number among its
parent's offshoots that round), so that a knot on the first family's side has the same name in both starts.  The
first-side births of the first differing round that one start has and the other lacks are listed, each with its
parent's record that round: how many joins the parent owed, how many loose distinctions it held, and, for each of
its joins that was cancelled, which member was short, what that member is made from, and what it was owed and
given at its birth."""
import sys, os, json, collections, hashlib
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); import reach
price, eng, eng_cap = reach.price, reach.eng, reach.eng_cap

def grow(d, m, ration, treatment, rounds, bound):
    live, deg, stars = price.source(reach.tail(d, m))
    E = eng_cap if (ration.startswith('CAP-') and ration != 'CAP-3') else eng
    run = E.Run(E.Law(ration, treatment, None, 'nae'), stars=stars, rounds=rounds, knot_bound=bound, mult=price.MULT)
    S = run.S
    other = {'b2'} | {x for x in live if x[0] in 'qz'}
    name = {i: x for i, x in enumerate(live)}; anc = {i: collections.Counter([x]) for i, x in enumerate(live)}
    for i in range(len(live), len(stars)): name[i] = 'w%d' % i; anc[i] = collections.Counter()
    born = {}; first = []
    for t in range(1, run.rounds_read + 1):
        row = collections.Counter(); seen = collections.Counter()
        for b in run.recs[t - 1]['births']:
            ps = tuple(sorted(name[p] for p in b['parents']))
            key = (b['kind'], ps); k = seen[key]; seen[key] += 1
            n = hashlib.sha1(repr((b['kind'], ps, k)).encode()).hexdigest()[:12]
            name[b['id']] = n; born[b['id']] = (t, b)
            a = collections.Counter()
            for p in b['parents']: a |= anc[p]
            anc[b['id']] = a
            if 'b1' in a and not (set(a) & other): row[n] += 1
        first.append(row)
    return {'run': run, 'S': S, 'name': name, 'anc': anc, 'born': born, 'first': first, 'other': other, 'deg': deg}

def made_from(g, u):
    a = g['anc'][u]; return ' '.join(sorted(a)) if a else '(spent witness)'

def describe(g, u):
    if u not in g['born']: return 'original %s' % g['name'][u]
    t, b = g['born'][u]
    return '%s of round %d from [%s]; owed %d joins at birth, given %d fresh' % (b['kind'], t, made_from(g, u), b['D'], b['f'])

def report(spec):
    d, ration, treatment, rounds = spec['d'], spec['ration'], spec['treatment'], spec['rounds']
    A = grow(d, spec['ma'], ration, treatment, rounds, spec.get('bound', 10 ** 6))
    B = grow(d, spec['mb'], ration, treatment, rounds, spec.get('bound', 10 ** 6))
    Rr = min(len(A['first']), len(B['first']))
    t = next((i + 1 for i in range(Rr) if A['first'][i] != B['first'][i]), None)
    out = {'spec': spec, 'rounds compared': Rr, 'first differing round': t, 'degrees': {spec['ma']: {x: A['deg'][x] for x in ('s', 't', 'b1', 'b2', 'q%d' % d)},
                                                                                       spec['mb']: {x: B['deg'][x] for x in ('s', 't', 'b1', 'b2', 'q%d' % d)}}}
    if t is None: return out
    for tag, X, Y, m in (('only in m = %d' % spec['ma'], A, B, spec['ma']), ('only in m = %d' % spec['mb'], B, A, spec['mb'])):
        only = X['first'][t - 1] - Y['first'][t - 1]
        rec = X['run'].recs[t - 1]; byname = {X['name'][b['id']]: b for b in rec['births']}
        kinds = collections.Counter(); cause = collections.Counter(); examples = []
        for n in sorted(only):
            b = byname[n]; kinds[b['kind']] += 1
            if b['kind'] != 'offshoot': cause['(a join)'] += 1; continue
            p = b['parents'][0]
            # the parent's joins this round that were cancelled, and who was short in each
            why = []
            for g in rec['cancelled']:
                if p in g:
                    for u in g:
                        if u != p and u in set(rec['short']):
                            why.append((made_from(X, u), describe(X, u), rec['owe'][u], rec['h'][u]))
            # is the same parent present in the other start, and what did it do there?
            cause[tuple(sorted(set(w[0] for w in why)))] += 1
            if len(examples) < 4:
                examples.append({'birth': n, 'parent': describe(X, p), 'parent owed': rec['owe'][p], 'parent held': rec['h'][p],
                                 'short partners': [{'made from': w[0], 'what': w[1], 'owed now': w[2], 'held now': w[3]} for w in why]})
        out[tag] = {'births': sum(only.values()), 'by kind': dict(kinds),
                    'offshoots by the short partners that cancelled a join of their parent': {' | '.join(k) if isinstance(k, tuple) else k: v for k, v in cause.most_common(8)},
                    'examples': examples}
    return out

if __name__ == '__main__':
    print(json.dumps(report(json.loads(sys.argv[1])), indent=1))
