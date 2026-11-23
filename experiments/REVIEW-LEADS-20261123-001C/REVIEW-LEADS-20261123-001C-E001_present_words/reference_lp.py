"""Reference by linear programming over arbitrary non-negative old tables M (8 x 8), then the cut-of-two (non-negative rank <= 4) check.

Under exact hiding with ratios lam (Alice) and mu (Bob), M (W0 - lam W1) = 0 and (W0 - mu W1)^T M = 0, every denominator is
W_a M W_b = D lam^[b=0] mu^[a=0], so with the outcome choice fixed the score is LINEAR in M on the polytope
P(lam, mu) = {M >= 0 : the two hiding equations, W1^T M W1 = 1}.  The score (best choice) is a maximum of linear functions, so its
maximum over P is at a vertex.  For each (lam, mu) on a grid, repeat from random outcome choices: LP over P with the current
choice, then re-choose the best outcome choice at the new vertex, until nothing improves.
usage: reference_lp.py LAM_MIN LAM_MAX MU_MIN MU_MAX N_GRID N_RESTARTS SEED TAG
"""
import sys, time, json
import numpy as np
from scipy.optimize import linprog
import common as c
from reference import best_combo

W0, W1 = c.Wf[0], c.Wf[1]
CA, CB = c.Cf[0], c.Cf[1]

def polytope_A(lam, mu):
    v = W0 - lam * W1; w = W0 - mu * W1
    A = np.zeros((17, 64))
    for x in range(8):
        A[x, 8 * x:8 * x + 8] = v
    for y in range(8):
        A[8 + y, y::8] = w
    A[16] = np.outer(W1, W1).reshape(-1)
    b = np.zeros(17); b[16] = 1.0
    return A, b

def objective(combo, lam, mu):
    kA0, kA1, kB0, kB1, pat = combo
    cs = [CA[kA0], CA[kA1]]; ds = [CB[kB0], CB[kB1]]
    sg = np.ones((2, 2)); sg[(pat >> 1) & 1, pat & 1] = -1.0
    G = np.zeros((8, 8))
    for a in (0, 1):
        for b in (0, 1):
            fac = (lam if b == 0 else 1.0) * (mu if a == 0 else 1.0)
            G += sg[a, b] * np.outer(cs[a], ds[b]) / fac
    return G

def ascent(lam, mu, combo, A, b, max_iter=12):
    best = (-1, None, None)
    for it in range(max_iter):
        G = objective(combo, lam, mu)
        for sign in (1.0, -1.0):          # the score is |value|: maximise either sign
            pass
        res = linprog(-G.reshape(-1), A_eq=A, b_eq=b, bounds=(0, None), method='highs')
        if res.status != 0: return best
        res2 = linprog(G.reshape(-1), A_eq=A, b_eq=b, bounds=(0, None), method='highs')
        cands = [res.x]
        if res2.status == 0: cands.append(res2.x)
        top = None
        for xv in cands:
            M = xv.reshape(8, 8)
            sc, cb = best_combo(M)
            if top is None or sc > top[0] + 1e-13: top = (sc, cb, M)
        if top[0] <= best[0] + 1e-12:
            return best
        best = top
        combo = top[1]
    return best

if __name__ == '__main__':
    l0, l1, m0, m1 = map(float, sys.argv[1:5]); ng = int(sys.argv[5]); nr = int(sys.argv[6]); seed = int(sys.argv[7]); tag = sys.argv[8]
    rng = np.random.default_rng(seed)
    t0 = time.time()
    lams = np.linspace(l0, l1, ng); mus = np.linspace(m0, m1, ng)
    results = []
    gbest = (0, None)
    for lam in lams:
        for mu in mus:
            A, b = polytope_A(lam, mu)
            pbest = (0, None, None)
            for r in range(nr):
                combo = (int(rng.integers(15)), int(rng.integers(15)), int(rng.integers(15)), int(rng.integers(15)), int(rng.integers(4)))
                res = ascent(lam, mu, combo, A, b)
                if res[0] > pbest[0]: pbest = res
            results.append(dict(lam=float(lam), mu=float(mu), score=float(pbest[0]), combo=pbest[1], M=(pbest[2].tolist() if pbest[2] is not None else None)))
            if pbest[0] > gbest[0]:
                gbest = (pbest[0], dict(lam=float(lam), mu=float(mu), combo=pbest[1], M=pbest[2].tolist()))
        print(f'lam {lam:.4f}: {time.time() - t0:.0f}s best so far {gbest[0]:.9f}', flush=True)
        if time.time() - t0 > 540: print('time limit'); break
    json.dump(dict(results=results, best=gbest), open(f'{c.ART}/reference_lp_{tag}.json', 'w'))
    print('best', gbest[0], gbest[1]['lam'], gbest[1]['mu'], gbest[1]['combo'])
