"""Shared definitions for REVIEW-LEADS-20261123-001C-E001 (uniform present words, births as settings).

Definitions follow research/REVIEW-LEADS-20261123-001C/preregistration.md.  The evaluation of a table M of old allowed-word
counts reuses the abstract check docs/prompts/missed_leads_checks/finished_weighting_chsh.py (loaded by `load_starter`
without running its search).
"""
import os, itertools, json, math
import numpy as np
from fractions import Fraction

REPO = '/home/jscul/p-vs-np-contact-first'
EXP = os.path.join(REPO, 'experiments/REVIEW-LEADS-20261123-001C/REVIEW-LEADS-20261123-001C-E001_present_words')
ART = os.path.join(REPO, 'artifacts/REVIEW-LEADS-20261123-001C/REVIEW-LEADS-20261123-001C-E001_present_words')
STARTER = os.path.join(REPO, 'docs/prompts/missed_leads_checks/finished_weighting_chsh.py')
os.makedirs(ART, exist_ok=True)

TOL = 1e-9

# ---- records and weights (same as the starter) ----------------------------------------------------------------------
REC = [(x1, x2, x3, z) for x1 in (0, 1) for x2 in (0, 1) for x3 in (0, 1) for z in (0, 1)]   # index = xval*2 + z
SGN = np.array([[(-1) ** sum(b for b, m in zip(r, [(k >> 3) & 1, (k >> 2) & 1, (k >> 1) & 1, k & 1]) if m) for r in REC]
                for k in range(1, 16)], dtype=np.int64)                                       # 15 x 16 parity outcomes

def side_factor(a):
    f = np.zeros((8, 16), dtype=np.int64)
    for xa in range(8):
        x = [(xa >> 2) & 1, (xa >> 1) & 1, xa & 1]
        for z in (0, 1):
            if not (x[0] == x[1 + a] == z):
                f[xa, xa * 2 + z] = 1
    return f
F = [side_factor(0), side_factor(1)]                 # F[a][x, record]: 1 when the fresh value is lawful for setting a
W = np.array([F[0].sum(1), F[1].sum(1)], dtype=np.int64)   # W[a][x] = number of lawful fresh values (1 or 2)
C = [SGN @ F[a].T for a in (0, 1)]                   # C[a][k, x] = sum over lawful records of the parity sign: 15 x 8
Cf = [c.astype(np.float64) for c in C]
Wf = W.astype(np.float64)
INVW = 1.0 / Wf

def load_starter():
    """Exec only the definitions of the starter (up to its section 1) and return its namespace."""
    src = open(STARTER).read()
    cut = src.index('# ---- 1. a four-type preparation')
    ns = {'__name__': 'starter'}
    exec(compile(src[:cut], STARTER, 'exec'), ns)
    return ns

# ---- batched hiding test, exact in integers ---------------------------------------------------------------------------
def parallel_rows(u0, u1):
    """rows of nonnegative integer vectors: u0 and u1 proportional (both nonzero)."""
    s0 = u0.sum(-1, keepdims=True); s1 = u1.sum(-1, keepdims=True)
    return (u0 * s1 == u1 * s0).all(-1)

def hidden_batch(M):
    """M: (n,8,8) int64, nonzero.  Hidden iff M W0 || M W1 (Alice) and M^T W0 || M^T W1 (Bob) (see notes)."""
    M = np.asarray(M, dtype=np.int64)
    uA0 = M @ W[0]; uA1 = M @ W[1]                    # Bob's weights on the columns: Alice's old-record vectors
    vB0 = np.einsum('nxy,x->ny', M, W[0]); vB1 = np.einsum('nxy,x->ny', M, W[1])
    return parallel_rows(uA0, uA1), parallel_rows(vB0, vB1)

# ---- batched scores -------------------------------------------------------------------------------------------------
def E_tables(M, control=False):
    """M: (n,8,8) float.  Returns list of four (n,15,15) correlation tables [E00,E01,E10,E11]."""
    out = []
    tot = M.sum((1, 2))
    for a in (0, 1):
        for b in (0, 1):
            if control:
                Mab = M * INVW[a][None, :, None] * INVW[b][None, None, :]
                num = np.einsum('kx,nxy,ly->nkl', Cf[a], Mab, Cf[b], optimize=True)
                out.append(num / tot[:, None, None])
            else:
                num = np.einsum('kx,nxy,ly->nkl', Cf[a], M, Cf[b], optimize=True)
                den = np.einsum('x,nxy,y->n', Wf[a], M, Wf[b])
                out.append(num / den[:, None, None])
    return out

def chsh_best_from_E(E):
    """Best |CHSH| over the 15^4 parity choices and the four one-minus sign patterns; E list of four (n,15,15)."""
    E00, E01, E10, E11 = E
    n = E00.shape[0]
    best = np.zeros(n)
    for p in range(4):
        s = [1.0] * 4; s[p] = -1.0
        u = s[0] * E00[:, :, None, :] + s[2] * E10[:, None, :, :]        # (n, kA0, kA1, kB0)
        v = s[1] * E01[:, :, None, :] + s[3] * E11[:, None, :, :]        # (n, kA0, kA1, kB1)
        hi = u.max(-1) + v.max(-1); lo = -(u.min(-1) + v.min(-1))
        best = np.maximum(best, np.maximum(hi, lo).max((1, 2)))
    return best

def score_batch(M, control=False, chunk=1500):
    M = np.asarray(M, dtype=np.float64)
    out = np.empty(M.shape[0])
    for i in range(0, M.shape[0], chunk):
        out[i:i + chunk] = chsh_best_from_E(E_tables(M[i:i + chunk], control))
    return out

def tv_batch(M):
    """largest change of a complete record (floats): max over (own setting, far setting pair) of the total variation."""
    M = np.asarray(M, dtype=np.float64)
    tv = np.zeros(M.shape[0])
    for a in (0, 1):
        g = [Wf[a][None, :] * np.einsum('nxy,y->nx', M, Wf[b]) for b in (0, 1)]
        p = [x / x.sum(1, keepdims=True) for x in g]
        tv = np.maximum(tv, 0.5 * np.abs(p[0] - p[1]).sum(1))
        g = [Wf[a][None, :] * np.einsum('nxy,x->ny', M, Wf[b]) for b in (0, 1)]
        p = [x / x.sum(1, keepdims=True) for x in g]
        tv = np.maximum(tv, 0.5 * np.abs(p[0] - p[1]).sum(1))
    return tv

# ---- exact (Fraction) evaluation for single tables ------------------------------------------------------------------
def exact_E(M, control=False):
    """dict (a,b) -> 15x15 object arrays of Fractions."""
    M = np.asarray(M, dtype=np.int64)
    res = {}
    for a in (0, 1):
        for b in (0, 1):
            if control:
                # M/(W_a W_b) with common denominator 4
                scale = 4
                Mab = np.array([[Fraction(int(M[x, y]), int(W[a][x] * W[b][y])) for y in range(8)] for x in range(8)], dtype=object)
                num = np.array([[sum(int(C[a][k, x]) * Mab[x, y] * int(C[b][l, y]) for x in range(8) for y in range(8))
                                 for l in range(15)] for k in range(15)], dtype=object)
                den = sum(Mab[x, y] * int(W[a][x] * W[b][y]) for x in range(8) for y in range(8))
                res[a, b] = num / den
            else:
                num = (C[a] @ M @ C[b].T)                    # exact ints
                den = int(W[a] @ M @ W[b])
                res[a, b] = np.array([[Fraction(int(num[k, l]), den) for l in range(15)] for k in range(15)], dtype=object)
    return res

def exact_best(M, control=False, slack=1e-7):
    """Exact best |CHSH| over parity choices: float screen, exact evaluation of every combination within `slack` of the float best.
    Returns (Fraction value, combo, pattern)."""
    Mf = np.asarray(M, dtype=np.float64)[None]
    E = E_tables(Mf, control)
    Ex = exact_E(M, control)
    E00, E01, E10, E11 = [e[0] for e in E]
    cand = []
    gbest = 0.0
    allv = []
    for p in range(4):
        s = np.ones(4); s[p] = -1
        V = (s[0] * E00[:, None, :, None] + s[1] * E01[:, None, None, :] + s[2] * E10[None, :, :, None] + s[3] * E11[None, :, None, :])
        allv.append(V)
        gbest = max(gbest, float(np.abs(V).max()))
    best = (Fraction(-1), None, None)
    for p in range(4):
        s = [1] * 4; s[p] = -1
        idx = np.argwhere(np.abs(allv[p]) >= gbest - slack)
        for kA0, kA1, kB0, kB1 in idx:
            v = s[0] * Ex[0, 0][kA0, kB0] + s[1] * Ex[0, 1][kA0, kB1] + s[2] * Ex[1, 0][kA1, kB0] + s[3] * Ex[1, 1][kA1, kB1]
            if abs(v) > best[0]:
                best = (abs(v), (int(kA0) + 1, int(kA1) + 1, int(kB0) + 1, int(kB1) + 1), p)
    return best

def exact_tv(M):
    M = np.asarray(M, dtype=np.int64)
    tv = Fraction(0)
    for a in (0, 1):
        for b in (0, 1):
            pass
    for a in (0, 1):
        g = [W[a] * (M @ W[b]) for b in (0, 1)]
        tv = max(tv, sum(abs(Fraction(int(p), int(g[0].sum())) - Fraction(int(q), int(g[1].sum()))) for p, q in zip(*g)) / 2)
        g = [W[a] * (M.T @ W[b]) for b in (0, 1)]
        tv = max(tv, sum(abs(Fraction(int(p), int(g[0].sum())) - Fraction(int(q), int(g[1].sum()))) for p, q in zip(*g)) / 2)
    return tv

# ---- joint record tables and general (non-parity) outcome functions --------------------------------------------------
def joint_records(M, control=False):
    """dict (a,b) -> 16x16 float joint distribution of complete records."""
    M = np.asarray(M, dtype=np.float64)
    P = {}
    for a in (0, 1):
        for b in (0, 1):
            Mab = M * (INVW[a][:, None] * INVW[b][None, :]) if control else M
            J = F[a].T.astype(np.float64) @ Mab @ F[b].astype(np.float64)
            P[a, b] = J / J.sum()
    return P

def best_general(M, n_random=200, seed=0, iters=60, control=False):
    """Best CHSH over all two-valued functions of the complete records by alternating optimization, started from every
    parity pair (225) and n_random random functions; each of the four one-minus patterns.  Returns (value, (A,B,pattern))."""
    P = joint_records(M, control)
    rng = np.random.default_rng(seed)
    starts = []
    for kA0 in range(15):
        for kA1 in range(15):
            starts.append(np.stack([SGN[kA0], SGN[kA1]]).astype(np.float64))
    for _ in range(n_random):
        starts.append(rng.choice([-1.0, 1.0], size=(2, 16)))
    A0 = np.stack(starts)                                     # (S,2,16)
    best = (-1.0, None)
    for p in range(4):
        s = np.ones((2, 2)); s[(p >> 1) & 1, p & 1] = -1.0
        A = A0.copy()
        val_prev = -np.inf
        for it in range(iters):
            B = np.empty_like(A)
            for b in (0, 1):
                g = sum(s[a, b] * A[:, a, :] @ P[a, b] for a in (0, 1))      # (S,16)
                B[:, b, :] = np.where(g >= 0, 1.0, -1.0)
            A_new = np.empty_like(A)
            for a in (0, 1):
                g = sum(s[a, b] * B[:, b, :] @ P[a, b].T for b in (0, 1))
                A_new[:, a, :] = np.where(g >= 0, 1.0, -1.0)
            A = A_new
            val = sum(s[a, b] * np.einsum('sr,rt,st->s', A[:, a, :], P[a, b], B[:, b, :]) for a in (0, 1) for b in (0, 1))
            if np.all(val <= val_prev + 1e-13):
                break
            val_prev = val
        i = int(np.argmax(np.abs(val)))
        if abs(val[i]) > best[0]:
            best = (float(abs(val[i])), (A[i].copy(), B[i].copy(), p))
    return best

# ---- local-explanation test (linear program on the four complete-record tables) ------------------------------------------
def lawful_records(a):
    return [r for r in range(16) if F[a][r // 2, r].sum() > 0 and F[a][r // 2, r] == 1]

def lp_local_residual(M, control=False):
    """Smallest L1 residual of the four complete-record joint tables from the local polytope (deterministic strategies
    over each side's lawful records at both settings).  Zero up to ~1e-9 iff one common local explanation exists."""
    from scipy.optimize import linprog
    from scipy.sparse import coo_matrix
    P = joint_records(M, control)
    L = [lawful_records(0), lawful_records(1)]
    nL = [len(L[0]), len(L[1])]                                 # 12, 12
    S_A = [(r0, r1) for r0 in range(nL[0]) for r1 in range(nL[1])]
    nS = len(S_A)
    nvar = nS * nS
    rows = []; cols = []; rhs = []
    row = 0; rowidx = {}
    for a in (0, 1):
        for b in (0, 1):
            for ra in range(nL[a]):
                for rb in range(nL[b]):
                    rowidx[a, b, ra, rb] = row; rhs.append(P[a, b][L[a][ra], L[b][rb]]); row += 1
    nrow = row
    # variable index lam = sA * nS + sB
    sa = np.repeat(np.arange(nS), nS); sb = np.tile(np.arange(nS), nS)
    lam = np.arange(nvar)
    A_choice = np.array(S_A)                                    # (nS,2)
    R = []; Cc = []
    for a in (0, 1):
        for b in (0, 1):
            ra = A_choice[sa, a]; rb = A_choice[sb, b]
            base = rowidx[a, b, 0, 0]
            rr = base + ra * nL[b] + rb
            R.append(rr); Cc.append(lam)
    R = np.concatenate(R); Cc = np.concatenate(Cc)
    Aeq = coo_matrix((np.ones(len(R)), (R, Cc)), shape=(nrow, nvar)).tocsr()
    # residual variables e+ e-: Aeq p + e+ - e- = rhs, minimize sum(e+ + e-)
    from scipy.sparse import hstack, identity
    A_full = hstack([Aeq, identity(nrow), -identity(nrow)]).tocsr()
    c = np.concatenate([np.zeros(nvar), np.ones(2 * nrow)])
    res = linprog(c, A_eq=A_full, b_eq=np.array(rhs), bounds=(0, None), method='highs')
    return float(res.fun), res.status

def table_key(T):
    return np.asarray(T, dtype=np.int64).tobytes()

# ---- symmetries of the evaluation (score, hiding, largest change and control value are unchanged) ---------------------
# Row maps of a side: swap x2<->x3 (this swaps the two settings a=0,1), and flip every old value (x -> 7-x).  The same maps act on
# Bob's side; exchanging the observers transposes M.  Checked numerically in gates_a.py (symmetry check).
_swap = np.array([((x >> 2) & 1) * 4 + (x & 1) * 2 + ((x >> 1) & 1) for x in range(8)])
_flip = np.array([7 - x for x in range(8)])
ROW_PERMS = [np.arange(8), _swap, _flip, _swap[_flip]]

def sym_images(M):
    """the 32 images of a table M (8x8): 4 row maps x 4 column maps, and the transpose of each."""
    out = []
    for pa in ROW_PERMS:
        for pb in ROW_PERMS:
            Mi = M[np.ix_(pa, pb)]
            out.append(Mi); out.append(Mi.T)
    return out

_rng_sym = np.random.default_rng(777)
HASH_R = _rng_sym.integers(1, 2 ** 40, size=(8, 8), dtype=np.int64)
HASH_R2 = _rng_sym.integers(1, 2 ** 40, size=(8, 8), dtype=np.int64)
def _hash_matrix(R):
    cols = []
    for pa in ROW_PERMS:
        for pb in ROW_PERMS:
            # image Mi = M[ix_(pa,pb)]: hash(Mi) = sum_xy R[x,y] M[pa[x],pb[y]] = sum_{x'y'} Rp[x',y'] M[x',y']
            Rp = np.zeros((8, 8), dtype=np.int64)
            Rp[np.ix_(pa, pb)] = R
            cols.append(Rp.reshape(64))
            # transpose of the image: hash = sum_xy R[x,y] Mi[y,x]
            Rt = np.zeros((8, 8), dtype=np.int64)
            Rt[np.ix_(pa, pb)] = R.T
            cols.append(Rt.reshape(64))
    return np.stack(cols, 1)                       # (64, 32)
HASH_M1 = _hash_matrix(HASH_R)
HASH_M2 = _hash_matrix(HASH_R2)

def canon_keys(flatM):
    """flatM: (n,64) int64.  Returns (key, check) with key the minimum over the 32 images' hashes (equal for equivalent tables)."""
    H1 = flatM @ HASH_M1
    am = H1.argmin(1)
    key = H1[np.arange(len(H1)), am]
    chk = (flatM @ HASH_M2)[np.arange(len(H1)), am]
    return key, chk

# ---- C kernel for the batch score (same arithmetic as score_batch; checked against it in gates_a.py) ------------------------
import ctypes
_lib = None
def _load_kernel():
    global _lib
    if _lib is None:
        _lib = ctypes.CDLL(ART + '/chsh_kernel.so')
        _lib.best_scores.argtypes = [ctypes.c_int, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_int, ctypes.c_void_p]
    return _lib
_Cflat = np.ascontiguousarray(np.stack(Cf)).astype(np.float64)       # (2,15,8)
_Wflat = np.ascontiguousarray(Wf)                                      # (2,8)

def score_batch_c(M, control=False):
    lib = _load_kernel()
    M = np.ascontiguousarray(M, dtype=np.float64).reshape(-1, 64)
    out = np.empty(len(M))
    lib.best_scores(len(M), M.ctypes.data, _Cflat.ctypes.data, _Wflat.ctypes.data, int(control), out.ctypes.data)
    return out

# ---- keyed-setting policy test --------------------------------------------------------------------------------------------
def keyed_policy_change(M):
    """One observer's setting is keyed to one of its own old values: Bob's b = y_j (or 1 - y_j), j = 1,2,3 (and the same with the
    roles exchanged).  Returns the largest total-variation change of the other observer's complete record, relative to its
    distribution under a fixed setting of the keyed observer (equal for both fixed settings when the pair is hidden), as an exact
    Fraction, with the policy that attains it."""
    M = np.asarray(M, dtype=np.int64)
    best = (Fraction(0), None)
    for who in ('Bob keyed', 'Alice keyed'):
        MM = M if who == 'Bob keyed' else M.T
        for j in range(3):
            for flip in (0, 1):
                w = np.array([W[(((y >> (2 - j)) & 1) ^ flip)][y] for y in range(8)], dtype=np.int64)     # weight of the keyed birth
                for a in (0, 1):
                    pol = W[a] * (MM @ w)                                  # other observer's old-record weights under the policy
                    for b in (0, 1):
                        fixed = W[a] * (MM @ W[b])
                        tv = sum(abs(Fraction(int(p), int(pol.sum())) - Fraction(int(q), int(fixed.sum()))) for p, q in zip(pol, fixed)) / 2
                        if tv > best[0]: best = (tv, dict(who=who, key=f'old value {j + 1}', flip=flip, other_setting=a, fixed_setting=b))
    return best
