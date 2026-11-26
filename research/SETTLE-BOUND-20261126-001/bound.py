"""bound.py: the settling bound from the start alone.  SETTLE-BOUND-20261126-001 (a check by the thread, not
registered); README.md has the frozen bound and the expectations.

    bound.py grow N KNOT_LAW OUT [SAMPLE SEED]   grow census starts of N knots (all, or SAMPLE of them chosen by
                                                 random.Random(SEED).sample over the census list) to round 24 under
                                                 KNOT_LAW (nae or parity); one JSON line each, with M and the kind
    bound.py test GROWN.jsonl OUT.json           settling against the bound, and the pair rule with the bound as cut

M is the larger of the largest set of live start knots sharing a distinction with one knot, and the largest fresh
count of a round-1 birth.  Growth, readings, kinds and settling are the look-alike study's (alike.py, phase2.py),
imported unchanged."""
import sys, os, json, random, collections, itertools
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'LOOK-ALIKE-20261126-001'))
import alike, phase2 as P

ROUNDS = 24
SLACK = {'sig0': 5, 'sig1': 7}


def start_block(stars):
    cnt = collections.Counter(d for k in stars for d in k); n = len(stars)
    loose = [sum(1 for d in k if cnt[d] == 1) for k in stars]
    live = {i for i in range(n) if loose[i] > 0}
    nb = [set(j for j in range(n) if j != i and set(stars[i]) & set(stars[j])) for i in range(n)]
    return max((len(nb[w] & live) for w in range(n)), default=0)


def M_of(stars, knot_law):
    g = alike.grow(stars, rounds=1, knot_law=knot_law)
    f1 = max((k[0][2] for k in g['rows'][0]['sig0']), default=0) if g['rows'] else 0
    return max(start_block(stars), f1)


def grow_many(N, knot_law, out, sample=None, seed=None):
    C = alike.census(N)
    if sample: C = random.Random(seed).sample(C, sample)
    with open(out, 'w') as f:
        for i, gi, loose, stars in C:
            g = alike.grow(stars, rounds=ROUNDS, knot_law=knot_law)
            g.update({'n knots': N, 'index': i, 'graph': gi, 'loose': loose, 'stars': stars, 'knot law': knot_law,
                      'kind': alike.kind([r['n'] for r in g['rows']], g['end']), 'M': M_of(stars, knot_law)})
            f.write(json.dumps(g) + '\n'); f.flush()


def test(path, out):
    xs = []
    for l in open(path):
        x = json.loads(l)
        if not x['kind'].startswith('dim'): continue
        D = int(x['kind'].split()[1]); V = P.views(x); n = len(x['rows'])
        rec = {'i': x['index'], 'kind': x['kind'], 'D': D, 'M': x['M'], 'n': n, 'V': V, 'K': {}, 'cut': {}, 'P': {}}
        for R in ('sig0', 'sig1'):
            rec['K'][R] = P.settles(V[R], D)
            c = x['M'] + SLACK[R]; rec['cut'][R] = c
            rec['P'][R] = P.fitted(V[R], D, c, n) if n > c + 1 else None
        xs.append(rec)
    res = {'starts of a dimension': len(xs), 'kinds': dict(collections.Counter(x['kind'] for x in xs))}
    bound = collections.Counter(); misses = []
    for x in xs:
        for R in ('sig0', 'sig1'):
            K, c = x['K'][R], x['cut'][R]
            if K is None: what = 'not settled in the rounds read'
            elif K <= c: what = 'within the bound'
            else: what = 'past the bound'
            bound[(R, what)] += 1
            if what != 'within the bound': misses.append([x['i'], x['kind'], R, x['M'], K, x['n']])
    res['bound'] = {' / '.join(k): v for k, v in sorted(bound.items())}
    res['bound misses'] = misses
    res['M'] = dict(sorted(collections.Counter(x['M'] for x in xs).items()))
    pairs = collections.Counter(); pmiss = []
    for a, b in itertools.combinations(xs, 2):
        if a['kind'] != b['kind']: continue
        n = min(a['n'], b['n'])
        for R in ('sig0', 'sig1'):
            if a['P'][R] is None or b['P'][R] is None or n <= max(a['cut'][R], b['cut'][R]) + 1:
                pairs[(R, 'not testable: too few rounds past the cut')] += 1; continue
            obs = P.first_nested(a['V'][R], b['V'][R], n); pre = P.first_nested(a['P'][R], b['P'][R], n)
            pairs[(R, 'predicted' if obs == pre else 'missed')] += 1
            if obs != pre and len(pmiss) < 200: pmiss.append([a['i'], b['i'], R, obs, pre])
    res['pairs'] = {' / '.join(k): v for k, v in sorted(pairs.items())}
    res['pair misses (first 200)'] = pmiss
    json.dump(res, open(out, 'w'), indent=1)
    print(json.dumps({k: res[k] for k in ('starts of a dimension', 'kinds', 'bound', 'pairs')}, indent=1))
    print('bound misses:', misses[:20])


if __name__ == '__main__':
    if sys.argv[1] == 'grow':
        N, law, out = int(sys.argv[2]), sys.argv[3], sys.argv[4]
        sample, seed = (int(sys.argv[5]), int(sys.argv[6])) if len(sys.argv) > 6 else (None, None)
        grow_many(N, law, out, sample, seed)
    elif sys.argv[1] == 'test':
        test(sys.argv[2], sys.argv[3])
