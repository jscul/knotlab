"""merge_test.py GROWN.jsonl OUT.json: the frozen point law and combined bound (README, "Frozen") on a grown sample.
T: the least t with c_s <= c_(s+1) for every s from t to the last round read before it.  A start of dimension D is
checkable when its settling round K <= 24 - D.  Settling is the look-alike study's."""
import sys, os, json, collections
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'LOOK-ALIKE-20261126-001'))
import phase2 as P

SLACK_M = {'sig0': 5, 'sig1': 7}
SLACK_T = {'sig0': 3, 'sig1': 5}


def T_of(c):
    T = len(c)
    while T > 1 and all(c[s - 1] <= c[s] for s in range(T - 1, len(c))): T -= 1
    return T


if __name__ == '__main__':
    path, out = sys.argv[1], sys.argv[2]
    res = collections.Counter(); breaks = []; slack = {R: collections.Counter() for R in SLACK_M}; kinds = collections.Counter()
    for l in open(path):
        x = json.loads(l); kinds[x['kind'] if x['kind'].startswith('dim') else x['kind'].split()[0]] += 1
        if not x['kind'].startswith('dim'): continue
        D = int(x['kind'].split()[1]); V = P.views(x); c = [r['n'] for r in x['rows']]; T = T_of(c)
        for R in ('sig0', 'sig1'):
            K = P.settles(V[R], D)
            if K is None or K > 24 - D or len(c) < 24:
                res[(R, 'censored')] += 1; continue
            m, t = x['M'] + SLACK_M[R], T + SLACK_T[R]
            if K > m:
                ok = K == t; res[(R, 'late: K = T + %d' % SLACK_T[R] if ok else 'late: point law broken')] += 1
                if not ok: breaks.append([x['index'], R, 'point', x['M'], T, K])
            b = max(m, t)
            if K <= b: res[(R, 'within the combined bound')] += 1; slack[R][b - K] += 1
            else: res[(R, 'combined bound broken')] += 1; breaks.append([x['index'], R, 'bound', x['M'], T, K])
    r = {'kinds': dict(kinds), 'tally': {' / '.join(k): v for k, v in sorted(res.items())},
         'slack (bound minus K)': {R: dict(sorted(v.items())) for R, v in slack.items()}, 'breaks': breaks}
    json.dump(r, open(out, 'w'), indent=1); print(json.dumps(r, indent=1)[:3000])
