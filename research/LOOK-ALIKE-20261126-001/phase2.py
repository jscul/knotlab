"""phase2.py GROWN.jsonl OUT.json: the frozen criterion (README, addendum) tested on the five-knot starts.
1. Settling: for each start of a dimension, the least K at which its view settles in each reading, against the bounds
   12 (sig0) and 14 (sig1); the view counts each kind of birth per round.
2. The pair rule: for every pair of one dimension, the first round from which they agree up to the count, observed
   through the last round both read, and as the rule computes it from counts through round 14 and fitted polynomials
   after.  Pairs are split among worker processes by the first start's index."""
import sys, json, collections, itertools
from concurrent.futures import ProcessPoolExecutor

BOUND = {'sig0': 12, 'sig1': 14}
CUT = 14


def views(x):
    return {R: [{json.dumps(k): v for k, v in row[R]} for row in x['rows']] for R in ('sig0', 'sig1')}


def poly_at(ys_by_round, D, K, t):
    xs = list(range(K - D + 1, K + 1)); tot = 0.0
    for i, xi in enumerate(xs):
        term = ys_by_round[xi - 1]
        for j, xj in enumerate(xs):
            if j != i: term *= (t - xj) / (xi - xj)
        tot += term
    return round(tot)


def fitted(V, D, K, n):
    """the view through round K, then each kind's fitted polynomial up to round n"""
    kinds = set().union(*V[:K])
    out = [dict(v) for v in V[:K]]
    for t in range(K + 1, n + 1):
        row = {}
        for k in kinds:
            c = poly_at([v.get(k, 0) for v in V], D, K, t)
            if c: row[k] = c
        out.append(row)
    return out


def settles(V, D):
    """least K (D <= K <= len - 2) at which the fitted view equals the observed one in every later round"""
    n = len(V)
    for K in range(max(D, 3), n - 1):
        if fitted(V, D, K, n) == V: return K
    return None


def nested(a, b):
    return all(b.get(k, 0) >= v for k, v in a.items()) or all(a.get(k, 0) >= v for k, v in b.items())


def first_nested(A, B, n):
    k = n
    while k > 0 and nested(A[k - 1], B[k - 1]): k -= 1
    return k + 1 if k < n else None


STARTS = None


def init(path):
    global STARTS
    STARTS = []
    for l in open(path):
        x = json.loads(l)
        if not x['kind'].startswith('dim'): continue
        D = int(x['kind'].split()[1]); V = views(x)
        P = {R: (fitted(V[R], D, CUT, len(V[R])) if len(V[R]) > CUT else None) for R in V}
        STARTS.append({'i': x['index'], 'kind': x['kind'], 'D': D, 'V': V, 'P': P, 'n': len(x['rows'])})


def work(lo_hi):
    lo, hi = lo_hi; tally = collections.Counter(); misses = []
    for a in range(lo, hi):
        A = STARTS[a]
        for B in STARTS[a + 1:]:
            if B['kind'] != A['kind']: continue
            n = min(A['n'], B['n'])
            for R in ('sig0', 'sig1'):
                obs = first_nested(A['V'][R], B['V'][R], n)
                if A['P'][R] is None or B['P'][R] is None or n <= CUT:
                    tally[(A['kind'], R, 'not predicted: too few rounds')] += 1; continue
                pre = first_nested(A['P'][R], B['P'][R], n)
                ok = obs == pre
                tally[(A['kind'], R, 'predicted' if ok else 'missed')] += 1
                tally[(A['kind'], R, 'observed ' + ('never' if obs is None else ('by round 8' if obs <= 8 else 'later')))] += 1
                if not ok and len(misses) < 50: misses.append([A['i'], B['i'], R, obs, pre])
    return tally, misses


if __name__ == '__main__':
    path, out = sys.argv[1], sys.argv[2]
    init(path)
    res = {'starts of a dimension': len(STARTS), 'by kind': dict(collections.Counter(s['kind'] for s in STARTS))}
    st = collections.Counter(); unsettled = []
    for s in STARTS:
        for R in ('sig0', 'sig1'):
            K = settles(s['V'][R], s['D'])
            st[(s['kind'], R, 'within bound' if K is not None and K <= BOUND[R] else ('later' if K else 'never'))] += 1
            if K is None or K > BOUND[R]: unsettled.append([s['i'], s['kind'], R, K, s['n']])
    res['settling'] = {' / '.join(k): v for k, v in sorted(st.items())}
    res['unsettled or late'] = unsettled
    N = len(STARTS); chunks = [(i, min(N, i + 25)) for i in range(0, N, 25)]
    tally = collections.Counter(); misses = []
    with ProcessPoolExecutor(6, initializer=init, initargs=(path,)) as ex:
        for t, m in ex.map(work, chunks):
            tally.update(t); misses.extend(m)
    res['pairs'] = {' / '.join(k): v for k, v in sorted(tally.items())}
    res['misses (first 50 per chunk)'] = misses
    json.dump(res, open(out, 'w'), indent=1)
    print(json.dumps({k: res[k] for k in ('starts of a dimension', 'by kind', 'settling')}, indent=1))
    print(json.dumps(res['pairs'], indent=1)); print('misses listed:', len(misses))
