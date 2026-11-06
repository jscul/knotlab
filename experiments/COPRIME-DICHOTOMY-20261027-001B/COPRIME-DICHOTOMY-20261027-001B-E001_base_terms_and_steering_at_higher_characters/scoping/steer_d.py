"""scoping: the steering rule at sector order d >= 3.  Base: connected sum of summands with vanishing local forms; insert
cable_d(P4, o) at level l; measure Q(xi; s) = <o_relators, J_t^T s> at the obstruction component and compare with
kappa_t * sum_j <W_j^(3)(leaves), l_j(s)>, kappa_t = t^-2 - t^-1, t = obstruction character"""
import sys, glob, os
import numpy as np
sys.path.insert(0, "/tmp/claude-1000/-home-jscul-p-vs-np-contact-first/6694d27d-4771-575f-adbb-a5c8aaccce97/scratchpad/cdA")
ROOT = "/home/jscul/p-vs-np-contact-first"
sys.path.insert(1, glob.glob(os.path.join(ROOT, "experiments/TRIPLE-SYSTEM-20261027-001B/*E001_*"))[0])
sys.path.insert(2, glob.glob(os.path.join(ROOT, "proofs/COPRIME-CLASS2-20261026-001B/*P001_*"))[0])
from cd_lib import GLie, BraidAlg, CyclicBraidModel, root_of_unity, solve_any
import mlib
import cp_lib as C

def bur(n, g, t, p):
    M = np.eye(n, dtype=np.int64)
    i = abs(g) - 1
    ti = pow(t, p - 2, p)
    if g > 0:
        M[i, i], M[i, i + 1], M[i + 1, i], M[i + 1, i + 1] = (1 - ti) % p, ti, 1, 0
    else:
        M[i, i], M[i, i + 1], M[i + 1, i], M[i + 1, i + 1] = 0, 1, t, (1 - t) % p
    return M

def bur_word(word, n, t, p):
    M = np.eye(n, dtype=np.int64)
    for g in word: M = bur(n, g, t, p) @ M % p
    return M

def J_matrix(n, t, p):
    J = np.eye(n, dtype=np.int64)
    for q in range(n):
        for q2 in range(q):
            J[q, q2] = (t - 1) * pow(t, q - q2 - 1, p) % p
    return J

def relator_values(Mo, inputs, upto_layer):
    """solve layers < upto_layer as in Mo.solve (inputs on free components), then return relator values (bs, n+1, D)"""
    A, p, n = Mo.A, Mo.p, Mo.n
    bs = next(iter(inputs.values())).shape[0]
    V = np.zeros((bs, n, A.D), dtype=np.int64)
    ok = np.ones(bs, dtype=bool)
    for lay in range(1, upto_layer):
        R = Mo.run(V)
        for k in [k for k in range(A.D) if A.layer[k] == lay]:
            X, bad = solve_any(Mo.Lin[int(A.chars[k])], (-R[:, :, k]).T % p, p)
            ok &= ~bad
            V[:, :, k] = (X.T + (inputs[k] if k in inputs else 0)) % p
    return Mo.run(V), V, ok

def fourway(p, d, zeta, e):
    L = GLie.from_brackets(p, d, "x y w z u t".split(), [1, 1, 1, 2, 2, 3], [e, -e, -e, 0, 0, -e],
                           {("x", "y"): {"z": 1}, ("w", "x"): {"u": 1}, ("w", "z"): {"t": 1}, ("y", "u"): {"t": -1}})
    return L, BraidAlg(L, zeta)

def run_case(p, d, e, base_summand, ncopies, level_frac, offset, rng, bs=12):
    zeta = root_of_unity(p, d)
    L, A = fourway(p, d, zeta, e)
    base, n = C.connected_sum([base_summand] * ncopies)
    assert n >= offset + 4 * d
    lev = int(len(base) * level_frac)
    ins = C.cable(mlib.P4, d, offset=offset)
    w2 = base[:lev] + ins + base[lev:]
    out = {}
    tobs = pow(zeta, (-e) % d, p)              # character of the obstruction component t
    J = J_matrix(n, tobs, p)
    Mb = CyclicBraidModel(base, n, A, p)
    Mi = CyclicBraidModel(w2, n, A, p)
    for c in (e % d, (-e) % d):
        assert len(Mb.cocycles[c]) == len(Mi.cocycles[c]), "cocycle spaces differ"
    ix, iy, iw, it = (A.idx[s] for s in "xywt")
    def rc(Mo, c): return (rng.integers(0, p, (bs, len(Mo.cocycles[c]))) @ Mo.cocycles[c]) % p
    inputs = {ix: rc(Mb, e % d), iy: rc(Mb, (-e) % d), iw: rc(Mb, (-e) % d)}
    s = rc(Mb, e % d)                           # dual cocycles at character t^-1 = zeta^e
    y = (s @ J) % p                              # rows: (J^T s)^T = s^T J
    res = {}
    for name, Mo in (("base", Mb), ("inserted", Mi)):
        R, V, ok = relator_values(Mo, inputs, 3)
        o = R[:, :n, it] % p
        res[name] = ((o * y).sum(axis=1) % p, ok, V)
    # prediction from the leaves at level lev
    Vb = res["base"][2]
    T3 = mlib.degree3_tensor(mlib.P4, 4, p)
    inv3 = pow(3, p - 2, p)
    leaves = np.zeros((bs, 4, L.D), dtype=np.int64)
    for k, comp in ((ix, e % d), (iy, (-e) % d), (iw, (-e) % d)):
        tc = pow(zeta, comp, p)
        col = (Vb[:, :, k] @ bur_word(base[:lev], n, tc, p).T) % p      # colours at level lev
        for j in range(4):
            o0 = offset + j * d
            leaves[:, j, k] = sum(pow(tc, d - 1 - i, p) * col[:, o0 + i] for i in range(d)) % p
    sl = (s @ bur_word(base[:lev], n, pow(zeta, e % d, p), p).T) % p
    tinv = pow(tobs, p - 2, p)
    dual_leaf = np.zeros((bs, 4), dtype=np.int64)
    for j in range(4):
        o0 = offset + j * d
        dual_leaf[:, j] = sum(pow(tinv, d - 1 - i, p) * sl[:, o0 + i] for i in range(d)) % p
    pred = np.zeros(bs, dtype=np.int64)
    for j in range(4):
        Lam = np.zeros((bs, L.D), dtype=np.int64)
        for (i1, i2, i3), v in T3[j].items():
            Lam = (Lam + v * L.br(leaves[:, i1], L.br(leaves[:, i2], leaves[:, i3]))) % p
        Lam = Lam * inv3 % p
        pred = (pred + Lam[:, it] * dual_leaf[:, j]) % p
    kappa = (tinv * tinv - tinv) % p
    pred = pred * kappa % p
    dQ = (res["inserted"][0] - res["base"][0]) % p
    return {"base Q zero": bool((res["base"][0] == 0).all()), "lower layers ok": bool(res["base"][1].all() and res["inserted"][1].all()),
            "dQ == pred": bool((dQ == pred).all()), "dQ nonzero samples": int((dQ != 0).sum()),
            "dQ == -pred": bool((dQ == (-pred) % p).all()), "ratio": [int(a) * pow(int(b), p - 2, p) % p for a, b in zip(dQ, pred) if b][:6]}

rng = np.random.default_rng(1)
cases = [(7, 3, 1, ([1, 1, -2, 1, -2, -2], 3), 6), (7, 3, 2, ([1, 1, -2, 1, -2, -2], 3), 6),
         (13, 3, 1, ([1, 1, -2, 1, -2, 1, -2, -2], 3), 6)]
for (p, d, e, summ, nc) in []:
    for (lf, off) in ((0.0, 0), (0.5, 1), (1.0, 0)):
        print(p, d, e, lf, off, run_case(p, d, e, summ, nc, lf, off, rng), flush=True)

def cable_k1(word, n, k):
    """(k,1)-cable of the closure of word (n strands): k-cable with blackboard framing plus delta_k^(1 - k * writhe)"""
    out = C.cable(word, k)
    w = sum(1 if g > 0 else -1 for g in word)
    j = 1 - k * w
    delta = list(range(1, k))
    out += delta * j if j > 0 else [-g for g in reversed(delta)] * (-j)
    return out, n * k

print("--- even orders: cable summands", flush=True)
for (p, d, e, k) in [(13, 4, 1, 2), (13, 4, 3, 2), (5, 4, 1, 2), (7, 6, 1, 3), (13, 6, 1, 3), (7, 6, 5, 3)]:
    summ = cable_k1([1] * p, 2, k)
    nc = 4 * d // (2 * k - 1) + 2
    for (lf, off) in ((0.0, 0), (0.5, 1)):
        print(p, d, e, "cable", k, lf, off, run_case(p, d, e, summ, nc, lf, off, rng, bs=10), flush=True)
