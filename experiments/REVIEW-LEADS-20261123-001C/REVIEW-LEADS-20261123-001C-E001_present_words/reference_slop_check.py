"""Check that the largest feasible random-start score (2.0000000863, violation 1e-9) is feasibility slop: project it exactly onto the hiding equations."""
import sys, json, glob
sys.path.insert(0, 'experiments/REVIEW-LEADS-20261123-001C/REVIEW-LEADS-20261123-001C-E001_present_words')
import numpy as np, reference as R, common as c
from scipy.optimize import minimize
best = None
for f in glob.glob('artifacts/REVIEW-LEADS-20261123-001C/REVIEW-LEADS-20261123-001C-E001_present_words/reference_slsqp_?.json'):
    for o in json.load(open(f)):
        if o.get('viol', 1) < 1e-7 and (best is None or o['score'] > best['score']): best = o
print(best['seed'], best['score'], best['viol'], best['combo'])
x = np.array(best['x'])
T, V, lam, mu = R.split(x)
M = T @ V.T
print('support rows', (M.sum(1) > 1e-6).sum(), 'cols', (M.sum(0) > 1e-6).sum(), 'lam', lam, 'mu', mu)
# project exactly onto the hiding constraints (keep T, V >= 0, sums 1)
def cons16(z): return R.cons(z)[:16]
res = minimize(lambda z: ((z - x) ** 2).sum(), x, jac=lambda z: 2 * (z - x), method='SLSQP', bounds=[(0, 1)] * 64 + [(0.05, 20)] * 2,
               constraints=[dict(type='eq', fun=R.cons, jac=R.cons_jac)], options=dict(maxiter=500, ftol=1e-18))
z = res.x; Tz, Vz, lz, mz = R.split(z)
print('after projection: violation', np.abs(R.cons(z)).max(), 'score', R.best_combo(Tz @ Vz.T)[0], 'moved', np.abs(z - x).max())
