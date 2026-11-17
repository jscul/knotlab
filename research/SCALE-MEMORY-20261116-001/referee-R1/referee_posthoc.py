"""SCALE-MEMORY-R1: the referee's own recomputation of the post hoc five-run check (fresh code, posthoc/results.jsonl only).
Per arm, the pooled median over every run of every instance; per scale-free arm the geometric mean of its two seeds; R against the
best of the three Novelty+ settings (re-chosen per resample); paired bootstrap over instances (each carries its five runs), 99%."""
import json, collections
import numpy as np
P = '/home/jscul/p-vs-np-contact-first/artifacts/SCALE-MEMORY-20261116-001A/SCALE-MEMORY-20261116-001A-E001_scale_memory/posthoc/results.jsonl'
D = collections.defaultdict(lambda: collections.defaultdict(dict)); unsolved = collections.Counter()
for l in open(P):
    r = json.loads(l); r = r.get('result', r)
    D[r['n']][r['arm']][r['seed']] = [x['flips'] for x in r['runs']]
    unsolved[(r['n'], r['arm'])] += sum(not x['solved'] for x in r['runs'])
rng = np.random.default_rng(7)
out = {'unsolved': {f'{k[0]}|{k[1]}': v for k, v in unsolved.items() if v}}
for n, A in sorted(D.items()):
    seeds = sorted(A['L3s_s0']); X = {a: np.array([A[a][s] for s in seeds], float) for a in A}   # instances x 5
    B = 10000; idx = rng.integers(0, len(seeds), (B, len(seeds)))
    pm = lambda a: np.median(X[a]); pmb = lambda a: np.median(X[a][idx].reshape(B, -1), axis=1)
    nov = [a for a in A if a.startswith('novelty')]
    best = min(nov, key=pm); bestb = np.min(np.stack([pmb(a) for a in nov]), 0)
    res = dict(novelty={a: pm(a) for a in nov}, best=best)
    for arm in ('L3s', 'L3sm'):
        g = np.sqrt(pm(f'{arm}_s0') * pm(f'{arm}_s1')); gb = np.sqrt(pmb(f'{arm}_s0') * pmb(f'{arm}_s1'))
        res[arm] = dict(R=g / pm(best), ci99=[float(np.quantile(gb / bestb, .005)), float(np.quantile(gb / bestb, .995))],
                        s0=pm(f'{arm}_s0') / pm(best), s1=pm(f'{arm}_s1') / pm(best))
    res['L3_s1'] = dict(R=pm('L3_s1') / pm(best))
    out[str(n)] = res
print(json.dumps(out, indent=1, default=float))
