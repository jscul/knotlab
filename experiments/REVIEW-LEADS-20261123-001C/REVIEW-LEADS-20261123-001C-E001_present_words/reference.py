"""Reference: the largest parity-outcome score over arbitrary non-negative side tables TA, TB (8 x 4 each: a cut of two) under exact
hiding.  Local optimisation (SLSQP with analytic gradients) from seeded random starts.

Variables: TA, TB >= 0 (sum of each fixed to 1: the score is unchanged by scaling a side), lam, mu > 0.  M = TA TB^T.
Hiding (exact): M (W0 - lam W1) = 0 for Alice (her old-record vectors M W0 and M W1 are proportional) and
(W0 - mu W1)^T M = 0 for Bob.  Outcome choice (masks and sign pattern) is re-chosen at the current table, then held fixed for
the next SLSQP run; rounds repeat until the choice no longer changes.

usage: reference.py FIRST_START COUNT [tag]
"""
import sys, time, json
import numpy as np
from scipy.optimize import minimize
import common as c

W0, W1 = c.Wf[0], c.Wf[1]
CA, CB = c.Cf[0], c.Cf[1]
NT = 32

def split(x):
    return x[:NT].reshape(8, 4), x[NT:2 * NT].reshape(8, 4), x[64], x[65]

def cons(x):
    T, V, lam, mu = split(x)
    M = T @ V.T
    return np.concatenate([M @ (W0 - lam * W1), M.T @ (W0 - mu * W1), [T.sum() - 1.0, V.sum() - 1.0]])

def cons_jac(x):
    T, V, lam, mu = split(x)
    M = T @ V.T
    v = W0 - lam * W1; w = W0 - mu * W1
    J = np.zeros((18, 66))
    dl = V.T @ v                # (4,)  g1_x = T_x . dl
    for xi in range(8):
        J[xi, 4 * xi:4 * xi + 4] = dl
        J[xi, NT:2 * NT] = np.outer(v, T[xi]).reshape(-1)
        J[xi, 64] = -(M[xi] @ W1)
    dm = T.T @ w                # (4,)  g2_y = V_y . dm
    for yi in range(8):
        J[8 + yi, NT + 4 * yi:NT + 4 * yi + 4] = dm
        J[8 + yi, :NT] = np.outer(w, V[yi]).reshape(-1)
        J[8 + yi, 65] = -(M[:, yi] @ W1)
    J[16, :NT] = 1.0; J[17, NT:2 * NT] = 1.0
    return J

def to_x(y):
    """unconstrained y = (t[32], v[32], l, m) -> x = (T[32], V[32], lam, mu), plus the Jacobian dx/dy."""
    t = y[:NT]; v = y[NT:2 * NT]
    qt = t * t; qv = v * v; St = qt.sum(); Sv = qv.sum()
    T = qt / St; V = qv / Sv
    lam = np.exp(np.clip(y[64], -8, 8)); mu = np.exp(np.clip(y[65], -8, 8))
    x = np.concatenate([T, V, [lam, mu]])
    def chain(jx):
        """jx: (r,66) derivative wrt x -> derivative wrt y."""
        jy = np.zeros_like(jx)
        gT = jx[:, :NT]; gV = jx[:, NT:2 * NT]
        jy[:, :NT] = 2 * t[None, :] * (gT - (gT * T[None, :]).sum(1, keepdims=True)) / St
        jy[:, NT:2 * NT] = 2 * v[None, :] * (gV - (gV * V[None, :]).sum(1, keepdims=True)) / Sv
        jy[:, 64] = jx[:, 64] * lam; jy[:, 65] = jx[:, 65] * mu
        return jy
    return x, chain

def make_obj_y(combo):
    f = make_obj(combo)
    def fy(y):
        x, chain = to_x(y)
        val, g = f(x)
        return val, chain(g[None, :])[0]
    return fy

def cons_y(y):
    x, _ = to_x(y)
    return cons(x)[:16]

def cons_jac_y(y):
    x, chain = to_x(y)
    return chain(cons_jac(x)[:16])

def make_obj(combo):
    kA0, kA1, kB0, kB1, pat = combo
    cs = [CA[kA0], CA[kA1]]; ds = [CB[kB0], CB[kB1]]
    sg = np.ones((2, 2)); sg[(pat >> 1) & 1, pat & 1] = -1.0
    def f(x):
        T, V, lam, mu = split(x)
        M = T @ V.T
        G = np.zeros((8, 8)); val = 0.0
        for a in (0, 1):
            for b in (0, 1):
                W_a, W_b = c.Wf[a], c.Wf[b]
                num = cs[a] @ M @ ds[b]; den = W_a @ M @ W_b
                val += sg[a, b] * num / den
                G += sg[a, b] * (np.outer(cs[a], ds[b]) / den - num * np.outer(W_a, W_b) / den ** 2)
        g = np.zeros(66)
        g[:NT] = (G @ V).reshape(-1); g[NT:2 * NT] = (G.T @ T).reshape(-1)
        # maximise |val|: minimise -val * sign
        sgn = 1.0 if val >= 0 else -1.0
        return -sgn * val, -sgn * g
    return f

def best_combo(M):
    """(score, combo) of the best parity outcome choice at M (single table), by full enumeration."""
    E = c.E_tables(np.asarray(M, dtype=np.float64)[None])
    E00, E01, E10, E11 = [e[0] for e in E]
    best = (-1.0, None)
    for p in range(4):
        sg = np.ones(4); sg[p] = -1
        V = sg[0] * E00[:, None, :, None] + sg[1] * E01[:, None, None, :] + sg[2] * E10[None, :, :, None] + sg[3] * E11[None, :, None, :]
        q = np.unravel_index(int(np.abs(V).argmax()), V.shape)
        if abs(V[q]) > best[0]:
            best = (float(abs(V[q])), (int(q[0]), int(q[1]), int(q[2]), int(q[3]), p))
    return best

def run_start(seed, rounds=5, maxiter=120, init=None):
    rng = np.random.default_rng(seed)
    if init is None:
        # random start: sparse-ish nonnegative tables (t, v are square roots of the entries)
        T = rng.random((8, 4)) ** 2 * (rng.random((8, 4)) < 0.7); V = rng.random((8, 4)) ** 2 * (rng.random((8, 4)) < 0.7)
        if T.sum() == 0: T += 0.1
        if V.sum() == 0: V += 0.1
        y = np.concatenate([np.sqrt(T / T.sum()).reshape(-1), np.sqrt(V / V.sum()).reshape(-1), [np.log(rng.uniform(0.5, 2)), np.log(rng.uniform(0.5, 2))]])
    else:
        y = init.copy()
    combo = (int(rng.integers(15)), int(rng.integers(15)), int(rng.integers(15)), int(rng.integers(15)), int(rng.integers(4)))
    hist = []
    for r in range(rounds):
        res = minimize(make_obj_y(combo), y, jac=True, method='SLSQP',
                       constraints=[dict(type='eq', fun=cons_y, jac=cons_jac_y)], options=dict(maxiter=maxiter, ftol=1e-12))
        y = res.x
        x, _ = to_x(y)
        T, V, lam, mu = split(x)
        viol = float(np.abs(cons(x)[:16]).max())
        M = T @ V.T
        sc, newc = best_combo(M)
        hist.append((sc, viol))
        if newc == combo and r > 0: break
        combo = newc
    return dict(seed=int(seed), score=sc, viol=viol, combo=combo, x=x.tolist(), rounds=len(hist), success=bool(res.success))

if __name__ == '__main__':
    first = int(sys.argv[1]); count = int(sys.argv[2]); tag = sys.argv[3] if len(sys.argv) > 3 else f'{first}_{count}'
    t0 = time.time(); out = []
    for s in range(first, first + count):
        try:
            r = run_start(20261123 * 10 + s)
        except Exception as e:
            r = dict(seed=s, error=str(e), score=0.0, viol=1.0)
        r['start'] = s
        out.append(r)
        if (s - first) % 20 == 0:
            ok = [o for o in out if o.get('viol', 1) < 1e-7]
            print(f'start {s}: {time.time() - t0:.0f}s, feasible {len(ok)}, best feasible {max([o["score"] for o in ok], default=0):.6f}', flush=True)
        if time.time() - t0 > 540: 
            print('time limit reached', flush=True); break
    json.dump(out, open(f'{c.ART}/reference_{tag}.json', 'w'))
    ok = [o for o in out if o.get('viol', 1) < 1e-7]
    print(f'{len(out)} starts run in {time.time() - t0:.0f}s; feasible (violation < 1e-7): {len(ok)}; best feasible score {max([o["score"] for o in ok], default=0):.9f}')
    sc = sorted([round(o['score'], 5) for o in ok], reverse=True)[:10]
    print('top feasible scores', sc)
