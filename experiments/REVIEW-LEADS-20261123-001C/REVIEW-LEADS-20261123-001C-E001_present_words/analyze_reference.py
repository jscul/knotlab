"""Analyse the vertex search of the reference: distinct best tables, their form, a test of non-negative rank <= 4 (a cut of two),
and exact rationalisation with re-verification of the best.   usage: analyze_reference.py"""
import glob, json, sys, math
import numpy as np
from fractions import Fraction
import sympy
import common as c
import reference_lp as L
from reference import best_combo

np.set_printoptions(linewidth=200, precision=4, suppress=True)

def nmf_exact(M, k, restarts=60, iters=4000, seed=0):
    """Try to write M (8x8, >= 0) as TA TB^T with TA, TB >= 0 having k columns (multiplicative updates, many starts).
    Returns (relative residual, TA, TB)."""
    rng = np.random.default_rng(seed)
    best = (np.inf, None, None)
    nM = np.linalg.norm(M)
    for r in range(restarts):
        A = rng.random((8, k)) + 0.1; B = rng.random((8, k)) + 0.1
        for it in range(iters):
            B *= (M.T @ A) / np.maximum(B @ (A.T @ A), 1e-12)
            A *= (M @ B) / np.maximum(A @ (B.T @ B), 1e-12)
        res = np.linalg.norm(M - A @ B.T) / nM
        if res < best[0]: best = (res, A.copy(), B.copy())
        if res < 1e-9: break
    return best

def support_rank_info(M, tol=1e-9):
    rows = np.nonzero(M.max(1) > tol)[0]; cols = np.nonzero(M.max(0) > tol)[0]
    return rows.tolist(), cols.tolist()

def rationalize(M, lam, mu, dens=(1, 2, 3, 4, 5, 6, 8, 10, 12, 16, 20, 24, 30, 40, 60, 100, 200, 500, 1000)):
    S = [q for q in range(64) if M.reshape(-1)[q] > 1e-7]
    out = []
    for den in dens:
        lr = Fraction(lam).limit_denominator(den); mr = Fraction(mu).limit_denominator(den)
        v = [Fraction(int(c.W[0][y])) - lr * int(c.W[1][y]) for y in range(8)]
        w = [Fraction(int(c.W[0][x])) - mr * int(c.W[1][x]) for x in range(8)]
        A = sympy.zeros(17, len(S)); b = sympy.zeros(17, 1)
        for j, q in enumerate(S):
            x, y = divmod(q, 8)
            for xi in range(8):
                if xi == x: A[xi, j] = sympy.Rational(v[y].numerator, v[y].denominator)
            for yi in range(8):
                if yi == y: A[8 + yi, j] = sympy.Rational(w[x].numerator, w[x].denominator)
            A[16, j] = int(c.W[1][x] * c.W[1][y])
        b[16] = 1
        try:
            sol, params = A.gauss_jordan_solve(b)
        except Exception:
            continue
        sol = sol.subs({p: 0 for p in params}) if params.shape[0] else sol
        vals = [Fraction(int(s.p), int(s.q)) for s in sol]
        if any(v_ < 0 for v_ in vals): continue
        Mr = [[Fraction(0)] * 8 for _ in range(8)]
        for j, q in enumerate(S):
            x, y = divmod(q, 8); Mr[x][y] = vals[j]
        L_ = 1
        for row in Mr:
            for e in row: L_ = L_ * e.denominator // math.gcd(L_, e.denominator)
        Mi = np.array([[int(e * L_) for e in row] for row in Mr], dtype=np.int64)
        g = np.gcd.reduce(Mi.reshape(-1)); Mi = Mi // g
        hA, hB = c.hidden_batch(Mi[None])
        if not (hA[0] and hB[0]): continue
        v_, combo, pat = c.exact_best(Mi)
        out.append(dict(den=den, lam=str(lr), mu=str(mr), exact=str(v_), value=float(v_), M=Mi.tolist(), combo=combo, pattern=pat))
    return out

if __name__ == '__main__':
    pol = []
    for f in sorted(glob.glob(f'{c.ART}/reference_vertices_v?.json')):
        d = json.load(open(f)); pol += d['polished']
    seen = {}; rows = []
    for p in sorted(pol, key=lambda d: -d['score']):
        M = np.array(p['M']); Mi = np.rint(M / M[M > 1e-9].min() * 1000).astype(np.int64) if False else None
        key = c.canon_keys(np.rint(M * 1e6).astype(np.int64).reshape(1, 64))[0][0]
        if key in seen: continue
        seen[key] = 1; rows.append(p)
    print(len(pol), 'polished,', len(rows), 'distinct up to symmetry and rounding')
    best_by_rank = {}
    for p in rows[:25]:
        M = np.array(p['M']); rr, cc = support_rank_info(M)
        print(f"score {p['score']:.9f} lam {p['lam']:.6f} mu {p['mu']:.6f} support {int((M > 1e-9).sum())} nonzero rows {len(rr)} cols {len(cc)} viol {p['viol']:.1e}")
    json.dump(rows[:60], open(f'{c.ART}/reference_vertices_distinct.json', 'w'))
