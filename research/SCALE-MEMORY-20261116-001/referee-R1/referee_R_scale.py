"""SCALE-MEMORY-R1, the referee's own recomputation (fresh code): per arm and cell, the geometric mean of the two seeds' median
flips over the best re-tuned rule's median (R), with a paired bootstrap over instances that recomputes both seeds' medians and
re-chooses the best rule (99%, 10,000 resamples), each seed's own R, and the ratios S, T, C, I, K. Inputs: SCALE-MEMORY test/ and
WHERE-NEXT test/ and stress/ results.jsonl only."""
import json, collections
import numpy as np
SM = '/home/jscul/p-vs-np-contact-first/artifacts/SCALE-MEMORY-20261116-001A/SCALE-MEMORY-20261116-001A-E001_scale_memory/'
WN = '/home/jscul/p-vs-np-contact-first/artifacts/WHERE-NEXT-20261116-001A/WHERE-NEXT-20261116-001A-E001_where_next/'
F = collections.defaultdict(lambda: collections.defaultdict(dict))   # (fam,n) -> arm -> seed -> flips
def add(path, rename=None):
    for l in open(path):
        r = json.loads(l); r = r.get('result', r)
        arm = r['arm']
        if rename: arm = rename.get(arm, arm)
        F[(r['fam'], r['n'])][arm][r['seed']] = r['flips']
add(WN + 'test/results.jsonl', {'L3': 'L3_s1'}); add(WN + 'stress/results.jsonl', {'L3': 'L3_s1'})
add(SM + 'test/results.jsonl')
RULES = ['walksat', 'probsat', 'novelty_plus', 'greedy_where', 'sticky', 'fms']
ARMS = ['L3', 'L3s', 'L3sm', 'L3m', 'L3c', 'L2m']
rng = np.random.default_rng(20261117)
out = {}
for cell in [('rand', 800), ('rand', 3200), ('rand', 12800), ('local', 3200)]:
    A = F[cell]
    ret = {}
    for rule in RULES:
        for nm in (f'{rule}@cell', f'{rule}@train'):
            if nm in A and len(A[nm]) >= 50: ret[rule] = nm; break
    seeds = sorted(set.intersection(*[set(A[a]) for a in [ret[r] for r in ret] + [f'{x}_s{s}' for x in ARMS for s in (0, 1) if f'{x}_s{s}' in A]]))
    X = {a: np.array([A[a][s] for s in seeds], float) for a in A if all(s in A[a] for s in seeds)}
    B = 10000; idx = rng.integers(0, len(seeds), (B, len(seeds)))
    med = lambda a: np.median(X[a]); medb = lambda a: np.median(X[a][idx], axis=1)
    rules = [ret[r] for r in ret]
    best = min(rules, key=med); bestb = np.min(np.stack([medb(r) for r in rules]), 0)
    res = dict(instances=len(seeds), best_rule=best, best_median=med(best), rule_medians={r: med(r) for r in rules}, arms={})
    armflips = {}; armflipsb = {}
    for x in ARMS:
        if f'{x}_s0' in X and f'{x}_s1' in X:
            g = np.sqrt(med(f'{x}_s0') * med(f'{x}_s1')); gb = np.sqrt(medb(f'{x}_s0') * medb(f'{x}_s1'))
            armflips[x], armflipsb[x] = g, gb
            res['arms'][x] = dict(s0=med(f'{x}_s0'), s1=med(f'{x}_s1'), geo=g, R=g / med(best),
                                  R_ci99=[float(np.quantile(gb / bestb, 0.005)), float(np.quantile(gb / bestb, 0.995))],
                                  R_s0=med(f'{x}_s0') / med(best), R_s1=med(f'{x}_s1') / med(best))
    def ratio(a, b):
        if a in armflips and b in armflips:
            q = armflipsb[a] / armflipsb[b]
            return dict(point=armflips[a] / armflips[b], ci99=[float(np.quantile(q, 0.005)), float(np.quantile(q, 0.995))])
    res['ratios'] = {k: ratio(*v) for k, v in dict(S=('L3s', 'L3'), T=('L3m', 'L3'), C=('L3m', 'L3c'), I_m=('L3sm', 'L3m'),
                                                     I_s=('L3sm', 'L3s'), K=('L3m', 'L2m'), P1_L3s_over_L3=('L3s', 'L3')).items()}
    out[f'{cell[0]}|{cell[1]}'] = res
print(json.dumps(out, indent=1, default=float))
