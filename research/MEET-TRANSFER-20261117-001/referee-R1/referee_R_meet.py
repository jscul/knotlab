"""MEET-TRANSFER-R1, the referee's own recomputation (fresh code, test/results.jsonl only): per cell, per-instance five-run
geometric means of flips; each seed's median; arm figure = geometric mean of its seeds' medians; R against the best of the five
tuned rules (three Novelty+ settings, probSAT, WalkSAT) re-chosen in each of 10,000 paired resamples (99%); per-seed R; the
95th-percentile ratio and solved fractions for the inner-loop bar; CPU ratio."""
import json, collections, glob
import numpy as np
A = glob.glob('/home/jscul/p-vs-np-contact-first/artifacts/MEET-TRANSFER-20261117-001A/*/')[0]
F = collections.defaultdict(lambda: collections.defaultdict(dict)); C = collections.defaultdict(lambda: collections.defaultdict(dict))
S = collections.defaultdict(lambda: collections.defaultdict(dict))
for l in open(A + 'test/results.jsonl'):
    x = json.loads(l)['result']; cell = '|'.join(map(str, x['cell'])); rs = x['runs']
    F[cell][x['arm']][x['seed']] = np.exp(np.mean([np.log(q['flips']) for q in rs]))
    C[cell][x['arm']][x['seed']] = np.exp(np.mean([np.log(q['cpu']) for q in rs]))
    S[cell][x['arm']][x['seed']] = np.mean([q['solved'] for q in rs])
RULES = ['novelty_plus#1', 'novelty_plus#2', 'novelty_plus#3', 'probsat', 'walksat']
ARMS = {'D': 4, 'Dr': 2, 'Dl': 4, 'Dn': 2, 'L3sm': 2}
rng = np.random.default_rng(20261117); out = {}
for cell in sorted(F):
    arms = F[cell]; seeds = sorted(arms['D_s0'])
    X = {a: np.array([arms[a][s] for s in seeds]) for a in arms}; Y = {a: np.array([C[cell][a][s] for s in seeds]) for a in arms}
    B = 10000; idx = rng.integers(0, len(seeds), (B, len(seeds)))
    best = min(RULES, key=lambda r: np.median(X[r])); bestb = np.min(np.stack([np.median(X[r][idx], 1) for r in RULES]), 0)
    bestc = min(RULES, key=lambda r: np.median(Y[r]))
    res = dict(instances=len(seeds), best=best, best_median=float(np.median(X[best])), arms={})
    for a, k in ARMS.items():
        ss = [f'{a}_s{i}' for i in range(k)]
        g = np.exp(np.mean([np.log(np.median(X[s])) for s in ss])); gb = np.exp(np.mean([np.log(np.median(X[s][idx], 1)) for s in ss], 0))
        p95 = float(np.exp(np.mean([np.log(np.quantile(X[s], .95)) for s in ss])) / np.quantile(X[best], .95))
        res['arms'][a] = dict(R=float(g / np.median(X[best])), ci99=[float(np.quantile(gb / bestb, .005)), float(np.quantile(gb / bestb, .995))],
                              seeds=[float(np.median(X[s]) / np.median(X[best])) for s in ss], p95_ratio=p95,
                              solved=float(np.mean([S[cell][s][q] for s in ss for q in seeds])), best_solved=float(np.mean([S[cell][best][q] for q in seeds])),
                              cpu_ratio=float(np.exp(np.mean([np.log(np.median(Y[s])) for s in ss])) / np.median(Y[bestc])))
    out[cell] = res
print(json.dumps(out, indent=1))
