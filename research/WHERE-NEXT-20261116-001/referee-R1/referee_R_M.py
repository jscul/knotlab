"""WHERE-NEXT-R1: the referee's own recomputation of median flips per cell and arm, R (L3 / best re-tuned rule, the best rule
re-chosen in every paired bootstrap resample) and M (L3 / L2), from the raw test and stress results. Written fresh; reads only the
results.jsonl files. 10,000 resamples, numpy default_rng(20261116)."""
import json, sys, collections
import numpy as np
A = '/home/jscul/p-vs-np-contact-first/artifacts/WHERE-NEXT-20261116-001A/WHERE-NEXT-20261116-001A-E001_where_next/'
rows = [json.loads(l) for f in ('test/results.jsonl', 'stress/results.jsonl') for l in open(A + f)]
recs = [r['result'] if 'result' in r else r for r in rows]
status = collections.Counter(r.get('status', 'ok') for r in rows)
cells = collections.defaultdict(lambda: collections.defaultdict(dict))
for r in recs:
    cells[(r['fam'], r['n'])][r['arm']][r['seed']] = (r['flips'], r['solved'])
RULES = ["walksat", "probsat", "novelty_plus", "greedy_where", "sticky", "fms"]
rng = np.random.default_rng(20261116)
out = {'status': dict(status), 'cells': {}}
for (fam, n), arms in sorted(cells.items()):
    seeds = sorted(arms['L3'])
    assert all(sorted(a) == seeds for a in arms.values()), (fam, n)
    F = {a: np.array([arms[a][s][0] for s in seeds], float) for a in arms}
    S = {a: np.array([arms[a][s][1] for s in seeds]) for a in arms}
    ret = {}
    for rule in RULES:
        if f'{rule}@cell' in arms: ret[rule] = f'{rule}@cell'
        elif f'{rule}@train' in arms: ret[rule] = f'{rule}@train'
    med = {a: float(np.median(F[a])) for a in arms}
    best = min(ret, key=lambda r: med[ret[r]])
    R = med['L3'] / med[ret[best]]; M = med['L3'] / med['L2']
    B = 10000; idx = rng.integers(0, len(seeds), (B, len(seeds)))
    Rb = np.empty(B); Mb = np.empty(B)
    L3m = np.median(F['L3'][idx], axis=1); L2m = np.median(F['L2'][idx], axis=1)
    rm = np.stack([np.median(F[ret[r]][idx], axis=1) for r in ret])
    Rb = L3m / rm.min(axis=0); Mb = L3m / L2m
    primary = (fam, n) == ('rand', 3200)
    conf = 0.95 if primary else 0.983
    lo, hi = (1 - conf) / 2, 1 - (1 - conf) / 2
    out['cells'][f'{fam}|{n}'] = dict(
        instances=len(seeds), medians={a: med[a] for a in sorted(arms)}, solved={a: int(S[a].sum()) for a in sorted(arms)},
        best_rule=ret[best], R=R, R_ci=[float(np.quantile(Rb, lo)), float(np.quantile(Rb, hi))], conf=conf,
        M=M, M_ci=[float(np.quantile(Mb, lo)), float(np.quantile(Mb, hi))],
        R_ci95=[float(np.quantile(Rb, 0.025)), float(np.quantile(Rb, 0.975))],
        frac_resamples_R_lower_than_0_9=float((Rb <= 0.9).mean()))
print(json.dumps(out, indent=1))
