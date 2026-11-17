"""SLOW-LOOP-R1, the referee's own recomputation (fresh code, results.jsonl only): per cell and arm, the median over instances
of each instance's geometric mean of `work` over its runs (and of `cpu`), R against the better of NOV and PS re-chosen in each
of 10,000 paired resamples, 99% intervals; also the share of unverified or unsolved runs."""
import json, collections
import numpy as np
A = '/home/jscul/p-vs-np-contact-first/artifacts/SLOW-LOOP-20261117-001A/SLOW-LOOP-20261117-001A-E001_slow_loop/'
W = collections.defaultdict(lambda: collections.defaultdict(dict)); C = collections.defaultdict(lambda: collections.defaultdict(dict))
bad = collections.Counter(); share = collections.defaultdict(list)
for f in ('test/results.jsonl', 'stress/results.jsonl'):
    for l in open(A + f):
        r = json.loads(l); x = r['result']
        if x['arm'] == 'CDCL': continue
        runs = x['runs']
        for q in runs:
            if not q.get('solved') or q.get('verified') is False: bad[(x['cell'], x['arm'])] += 1
        W[x['cell']][x['arm']][x['seed']] = np.exp(np.mean([np.log(q['work']) for q in runs]))
        C[x['cell']][x['arm']][x['seed']] = np.exp(np.mean([np.log(q['cpu']) for q in runs]))
        if x['arm'] in ('G', 'GO', 'RND', 'ST', 'Gx'):
            share[(x['cell'], x['arm'])].append(np.mean([(q.get('work_slow', 0) + q.get('work_rebuild', 0)) / q['work'] for q in runs]))
rng = np.random.default_rng(20261117)
out = {'unsolved_or_unverified': {f'{k[0]}|{k[1]}': v for k, v in bad.items()}, 'cells': {}}
for cell in sorted(W):
    arms = W[cell]; seeds = sorted(set.intersection(*[set(v) for v in arms.values()]))
    X = {a: np.array([arms[a][s] for s in seeds]) for a in arms}; Y = {a: np.array([C[cell][a][s] for s in seeds]) for a in arms}
    B = 10000; idx = rng.integers(0, len(seeds), (B, len(seeds)))
    best = min(('NOV', 'PS'), key=lambda a: np.median(X[a])); bestb = np.minimum(np.median(X['NOV'][idx], 1), np.median(X['PS'][idx], 1))
    bestc = min(('NOV', 'PS'), key=lambda a: np.median(Y[a]))
    res = dict(instances=len(seeds), best=best, best_median_work=float(np.median(X[best])), arms={})
    for a in arms:
        if a in ('NOV', 'PS'): continue
        rb = np.median(X[a][idx], 1) / bestb
        res['arms'][a] = dict(R_work=float(np.median(X[a]) / np.median(X[best])),
                              ci99=[float(np.quantile(rb, .005)), float(np.quantile(rb, .995))],
                              R_cpu=float(np.median(Y[a]) / np.median(Y[bestc])),
                              slow_share=float(np.median(share[(cell, a)])) if (cell, a) in share else None)
    out['cells'][cell] = res
print(json.dumps(out, indent=1))
