"""EARN-BUDGET-R1, the referee's own recomputation (fresh code, results.jsonl only): per cell and arm, the median over instances
of each instance's five-run geometric mean of `work` and of `cpu`; R against the better of NOV and PS re-chosen in each of 10,000
paired resamples (99%); E/GbO, E/GO, E/Gb, E/ST; and, for the charge check, each arm's CPU per charged incidence split by loop."""
import json, collections
import numpy as np
A = '/home/jscul/p-vs-np-contact-first/artifacts/EARN-BUDGET-20261117-001A/EARN-BUDGET-20261117-001A-E001_earn_budget/'
W = collections.defaultdict(lambda: collections.defaultdict(dict)); C = collections.defaultdict(lambda: collections.defaultdict(dict))
per = collections.defaultdict(list); diag = collections.defaultdict(list); bad = collections.Counter()
for f in ('test/results.jsonl', 'stress/results.jsonl'):
    for l in open(A + f):
        x = json.loads(l)['result']
        if x['arm'] == 'CDCL': continue
        rs = x['runs']
        for q in rs:
            if not q.get('solved') or q.get('verified') is False or q.get('contradiction'): bad[(x['cell'], x['arm'])] += 1
            if q.get('work_rebuild', 0) > 0 and q.get('cpu_rebuild', 0) > 0:
                per[(x['cell'], x['arm'])].append((q['cpu_fast'] / max(1, q['work_fast']) * 1e9, q['cpu_rebuild'] / q['work_rebuild'] * 1e9,
                                                    q['cpu_slow'] / max(1, q['work_slow']) * 1e9))
            if x['arm'] == 'E': diag[x['cell']].append((q.get('rho_top'), q.get('doublings'), q.get('rebuilds')))
        W[x['cell']][x['arm']][x['seed']] = np.exp(np.mean([np.log(q['work']) for q in rs]))
        C[x['cell']][x['arm']][x['seed']] = np.exp(np.mean([np.log(q['cpu']) for q in rs]))
rng = np.random.default_rng(20261117)
out = {'bad_runs': {f'{k[0]}|{k[1]}': v for k, v in bad.items()}, 'cells': {}}
for cell in sorted(W):
    arms = W[cell]; seeds = sorted(set.intersection(*[set(v) for v in arms.values()]))
    X = {a: np.array([arms[a][s] for s in seeds]) for a in arms}; Y = {a: np.array([C[cell][a][s] for s in seeds]) for a in arms}
    B = 10000; idx = rng.integers(0, len(seeds), (B, len(seeds)))
    best = min(('NOV', 'PS'), key=lambda a: np.median(X[a])); bestb = np.minimum(np.median(X['NOV'][idx], 1), np.median(X['PS'][idx], 1))
    bestc = min(('NOV', 'PS'), key=lambda a: np.median(Y[a]))
    res = dict(instances=len(seeds), best=best, arms={}, pairs={})
    for a in arms:
        if a in ('NOV', 'PS'): continue
        rb = np.median(X[a][idx], 1) / bestb
        res['arms'][a] = dict(R=float(np.median(X[a]) / np.median(X[best])), ci99=[float(np.quantile(rb, .005)), float(np.quantile(rb, .995))],
                              R_cpu=float(np.median(Y[a]) / np.median(Y[bestc])))
        if (cell, a) in per:
            p = np.array(per[(cell, a)]); res['arms'][a]['ns_per_incidence_fast_rebuild_slow'] = [float(np.median(p[:, i])) for i in range(3)]
    for a, b in (('E', 'GbO'), ('E', 'GO'), ('E', 'Gb'), ('E', 'ST'), ('Erb', 'E'), ('ErbL', 'E')):
        if a in X and b in X:
            q = np.median(X[a][idx], 1) / np.median(X[b][idx], 1)
            res['pairs'][f'{a}/{b}'] = [float(np.median(X[a]) / np.median(X[b])), float(np.quantile(q, .005)), float(np.quantile(q, .995))]
    if cell in diag:
        d = np.array([[v if v is not None else np.nan for v in t] for t in diag[cell]], float)
        res['E_diag'] = dict(rho_top_median=float(np.nanmedian(d[:, 0])), doublings_median=float(np.nanmedian(d[:, 1])),
                             rebuilds_median=float(np.nanmedian(d[:, 2])), runs=len(d))
    out['cells'][cell] = res
print(json.dumps(out, indent=1))
