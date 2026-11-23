"""Reference, part 2 (exploratory, after the pre-registered random-start run): vertex search over arbitrary non-negative old tables.

For a grid of hiding ratios (lam, mu) the set P(lam, mu) of old tables M >= 0 with M (W0 - lam W1) = 0, (W0 - mu W1)^T M = 0 and
W1^T M W1 = 1 is a polytope, and the score is a convex function of M on it, so its maximum is at a vertex.  Vertices are sampled by
solving linear programs with random objectives (at lam = mu = 1 the face on which the unconstrained value pair is removed is used,
since otherwise only single-entry tables of score 2 appear).  The best vertices are then polished continuously in (M, lam, mu).
usage: reference_vertices.py LAM_INDEX_START LAM_INDEX_END N_LP SEED TAG    (grid of 25 values in (0.5, 2) plus 2/3, 3/4, 1, 4/3, 3/2)
"""
import sys, time, json
import numpy as np
from scipy.optimize import linprog, minimize
import common as c
import reference_lp as L
from reference import best_combo

GRID = sorted(set(np.round(np.linspace(0.5, 2.0, 27)[1:-1], 6).tolist() + [2 / 3, 3 / 4, 1.0, 4 / 3, 3 / 2]))
AC = [0, 3, 4, 7]

def sample_point(lam, mu, nlp, rng):
    A, b = L.polytope_A(lam, mu)
    bounds = [(0, None)] * 64
    if abs(lam - 1) < 1e-12 and abs(mu - 1) < 1e-12:
        for x in AC:
            for y in AC: bounds[8 * x + y] = (0, 0)
    verts = {}
    for r in range(nlp):
        g = rng.normal(size=64)
        if r % 2: g = np.abs(g) * rng.choice([-1, 1], size=64)
        res = linprog(g, A_eq=A, b_eq=b, bounds=bounds, method='highs-ds')
        if res.status != 0: continue
        x = np.round(res.x, 10); verts[x.tobytes()] = x
    if not verts: return None
    return np.array(list(verts.values())).reshape(-1, 8, 8)

def polish(M0, lam0, mu0, rounds=6):
    """Continuous polish in (M, lam, mu) with the outcome choice re-picked each round."""
    W0, W1 = c.Wf[0], c.Wf[1]
    x0 = np.concatenate([M0.reshape(-1), [lam0, mu0]])
    def cons(x):
        M = x[:64].reshape(8, 8); lam, mu = x[64], x[65]
        return np.concatenate([M @ (W0 - lam * W1), (W0 - mu * W1) @ M, [W1 @ M @ W1 - 1.0]])
    def cons_jac(x):
        M = x[:64].reshape(8, 8); lam, mu = x[64], x[65]
        v = W0 - lam * W1; w = W0 - mu * W1
        J = np.zeros((17, 66))
        for xi in range(8): J[xi, 8 * xi:8 * xi + 8] = v
        for yi in range(8): J[8 + yi, yi:64:8] = w
        J[16, :64] = np.outer(W1, W1).reshape(-1)
        J[:8, 64] = -(M @ W1); J[8:16, 65] = -(W1 @ M)
        return J
    best = None
    x = x0.copy()
    combo = best_combo(x[:64].reshape(8, 8))[1]
    for r in range(rounds):
        kA0, kA1, kB0, kB1, pat = combo
        cs = [c.Cf[0][kA0], c.Cf[0][kA1]]; ds = [c.Cf[1][kB0], c.Cf[1][kB1]]
        sg = np.ones((2, 2)); sg[(pat >> 1) & 1, pat & 1] = -1.0
        def f(x):
            M = x[:64].reshape(8, 8); val = 0.0; G = np.zeros((8, 8))
            for a in (0, 1):
                for b in (0, 1):
                    num = cs[a] @ M @ ds[b]; den = c.Wf[a] @ M @ c.Wf[b]
                    val += sg[a, b] * num / den
                    G += sg[a, b] * (np.outer(cs[a], ds[b]) / den - num * np.outer(c.Wf[a], c.Wf[b]) / den ** 2)
            s = 1.0 if val >= 0 else -1.0
            g = np.zeros(66); g[:64] = -s * G.reshape(-1)
            return -s * val, g
        res = minimize(f, x, jac=True, method='SLSQP', bounds=[(0, None)] * 64 + [(0.5, 2.0)] * 2,
                       constraints=[dict(type='eq', fun=cons, jac=cons_jac)], options=dict(maxiter=200, ftol=1e-14))
        xn = res.x; viol = float(np.abs(cons(xn)).max())
        if viol > 1e-8: break
        sc, newc = best_combo(xn[:64].reshape(8, 8))
        if best is None or sc > best[0] + 1e-13:
            best = (sc, xn.copy(), newc, viol)
        if newc == combo: break
        combo = newc; x = xn
    return best

if __name__ == '__main__':
    i0, i1, nlp, seed, tag = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), sys.argv[5]
    rng = np.random.default_rng(seed)
    t0 = time.time(); cands = []; stats = []
    for li in range(i0, min(i1, len(GRID))):
        lam = GRID[li]
        for mu in GRID:
            V = sample_point(lam, mu, nlp, rng)
            if V is None: continue
            sc = c.score_batch_c(V)
            top = np.argsort(-sc)[:3]
            stats.append((lam, mu, len(V), float(sc.max())))
            for q in top:
                if sc[q] > 2 + 1e-9: cands.append((float(sc[q]), lam, mu, V[q]))
        print(f'lam {lam:.4f}: {time.time() - t0:.0f}s; candidates above 2: {len(cands)}; best {max([x[0] for x in cands], default=0):.6f}', flush=True)
        if time.time() - t0 > 400: print('time limit before polishing'); break
    cands.sort(key=lambda t: -t[0])
    polished = []
    for sc0, lam, mu, M in cands[:60]:
        if time.time() - t0 > 560: break
        p = polish(M, lam, mu)
        if p is None: continue
        polished.append(dict(start=sc0, score=p[0], lam=float(p[1][64]), mu=float(p[1][65]), combo=p[2], viol=p[3], M=p[1][:64].reshape(8, 8).tolist()))
    polished.sort(key=lambda d: -d['score'])
    json.dump(dict(grid=GRID, stats=stats, n_candidates=len(cands), polished=polished), open(f'{c.ART}/reference_vertices_{tag}.json', 'w'))
    print(f'{len(cands)} candidates above 2; polished {len(polished)}; best polished', polished[0]['score'] if polished else None,
          polished[0]['lam'] if polished else None, polished[0]['mu'] if polished else None, f'{time.time() - t0:.0f}s')
