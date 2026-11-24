"""Shared definitions for THIRD-HOLDER-20261123-001B-E001 (the smallest structure with a hidden excess; a third holder).

Definitions follow research/THIRD-HOLDER-20261123-001B/preregistration.md (frozen).  Observers, settings, weighting, records,
hiding and the score are those of ticket REVIEW-LEADS-20261123-001C; the evaluation code below is copied from
experiments/REVIEW-LEADS-20261123-001C/REVIEW-LEADS-20261123-001C-E001_present_words/common.py (sections marked COPIED), with
only the paths changed.  New here: structures written as lists of knots, their side tables by direct enumeration, holder
counts, classes L and S, and extra holders.
"""
import os, itertools, json, math
import numpy as np
from fractions import Fraction

REPO = '/home/jscul/p-vs-np-contact-first'
EXP = os.path.join(REPO, 'experiments/THIRD-HOLDER-20261123-001B/THIRD-HOLDER-20261123-001B-E001_smallest')
ART = os.path.join(REPO, 'artifacts/THIRD-HOLDER-20261123-001B/THIRD-HOLDER-20261123-001B-E001_smallest')
STARTER = os.path.join(REPO, 'docs/prompts/missed_leads_checks/finished_weighting_chsh.py')
os.makedirs(ART, exist_ok=True)

TOL = 1e-9

# ---- COPIED: records and weights --------------------------------------------------------------------------------------
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
C = [SGN @ F[a].T for a in (0, 1)]                   # C[a][k, x]: 15 x 8
Cf = [c.astype(np.float64) for c in C]
Wf = W.astype(np.float64)
INVW = 1.0 / Wf

def load_starter():
    """Exec only the definitions of the starter (up to its section 1) and return its namespace (gives `evaluate`)."""
    src = open(STARTER).read()
    cut = src.index('# ---- 1. a four-type preparation')
    ns = {'__name__': 'starter'}
    exec(compile(src[:cut], STARTER, 'exec'), ns)
    return ns

# ---- COPIED: batched hiding test, exact in integers ---------------------------------------------------------------------
def parallel_rows(u0, u1):
    s0 = u0.sum(-1, keepdims=True); s1 = u1.sum(-1, keepdims=True)
    return (u0 * s1 == u1 * s0).all(-1)

def hidden_batch(M):
    """M: (n,8,8) int64, nonzero.  Hidden iff M W0 || M W1 (Alice) and M^T W0 || M^T W1 (Bob)."""
    M = np.asarray(M, dtype=np.int64)
    uA0 = M @ W[0]; uA1 = M @ W[1]
    vB0 = np.einsum('nxy,x->ny', M, W[0]); vB1 = np.einsum('nxy,x->ny', M, W[1])
    return parallel_rows(uA0, uA1), parallel_rows(vB0, vB1)

# ---- COPIED: batched scores -------------------------------------------------------------------------------------------
def E_tables(M, control=False):
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
    E00, E01, E10, E11 = E
    n = E00.shape[0]
    best = np.zeros(n)
    for p in range(4):
        s = [1.0] * 4; s[p] = -1.0
        u = s[0] * E00[:, :, None, :] + s[2] * E10[:, None, :, :]
        v = s[1] * E01[:, :, None, :] + s[3] * E11[:, None, :, :]
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

# ---- COPIED: exact (Fraction) evaluation for single tables --------------------------------------------------------------
def exact_E(M, control=False):
    M = np.asarray(M, dtype=np.int64)
    res = {}
    for a in (0, 1):
        for b in (0, 1):
            if control:
                Mab = np.array([[Fraction(int(M[x, y]), int(W[a][x] * W[b][y])) for y in range(8)] for x in range(8)], dtype=object)
                num = np.array([[sum(int(C[a][k, x]) * Mab[x, y] * int(C[b][l, y]) for x in range(8) for y in range(8))
                                 for l in range(15)] for k in range(15)], dtype=object)
                den = sum(Mab[x, y] * int(W[a][x] * W[b][y]) for x in range(8) for y in range(8))
                res[a, b] = num / den
            else:
                num = (C[a] @ M @ C[b].T)
                den = int(W[a] @ M @ W[b])
                res[a, b] = np.array([[Fraction(int(num[k, l]), den) for l in range(15)] for k in range(15)], dtype=object)
    return res

def exact_best(M, control=False, slack=1e-7):
    """Exact best |CHSH| over parity choices: float screen, exact evaluation of every combination within `slack` of the
    float best.  Returns (Fraction value, combo, pattern)."""
    Mf = np.asarray(M, dtype=np.float64)[None]
    E = E_tables(Mf, control)
    Ex = exact_E(M, control)
    E00, E01, E10, E11 = [e[0] for e in E]
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
        g = [W[a] * (M @ W[b]) for b in (0, 1)]
        tv = max(tv, sum(abs(Fraction(int(p), int(g[0].sum())) - Fraction(int(q), int(g[1].sum()))) for p, q in zip(*g)) / 2)
        g = [W[a] * (M.T @ W[b]) for b in (0, 1)]
        tv = max(tv, sum(abs(Fraction(int(p), int(g[0].sum())) - Fraction(int(q), int(g[1].sum()))) for p, q in zip(*g)) / 2)
    return tv

def exact_hidden(M):
    hA, hB = hidden_batch(np.asarray(M, dtype=np.int64)[None])
    return bool(hA[0]), bool(hB[0])

# ---- COPIED: symmetries of the evaluation ---------------------------------------------------------------------------------
_swap = np.array([((x >> 2) & 1) * 4 + (x & 1) * 2 + ((x >> 1) & 1) for x in range(8)])
_flip = np.array([7 - x for x in range(8)])
ROW_PERMS = [np.arange(8), _swap, _flip, _swap[_flip]]

_rng_sym = np.random.default_rng(777)
HASH_R = _rng_sym.integers(1, 2 ** 40, size=(8, 8), dtype=np.int64)
HASH_R2 = _rng_sym.integers(1, 2 ** 40, size=(8, 8), dtype=np.int64)
def _hash_matrix(R):
    cols = []
    for pa in ROW_PERMS:
        for pb in ROW_PERMS:
            Rp = np.zeros((8, 8), dtype=np.int64)
            Rp[np.ix_(pa, pb)] = R
            cols.append(Rp.reshape(64))
            Rt = np.zeros((8, 8), dtype=np.int64)
            Rt[np.ix_(pa, pb)] = R.T
            cols.append(Rt.reshape(64))
    return np.stack(cols, 1)
HASH_M1 = _hash_matrix(HASH_R)
HASH_M2 = _hash_matrix(HASH_R2)

def canon_keys(flatM):
    """flatM: (n,64) int64 (normalised by gcd).  Key = minimum over the 32 images' hashes (wraps mod 2^64, consistently)."""
    H1 = flatM @ HASH_M1
    am = H1.argmin(1)
    key = H1[np.arange(len(H1)), am]
    chk = (flatM @ HASH_M2)[np.arange(len(H1)), am]
    return key, chk

# ---- COPIED: C kernel for the batch score ------------------------------------------------------------------------------
import ctypes
_lib = None
def _load_kernel():
    global _lib
    if _lib is None:
        _lib = ctypes.CDLL(ART + '/chsh_kernel.so')
        _lib.best_scores.argtypes = [ctypes.c_int, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_int, ctypes.c_void_p]
    return _lib
_Cflat = np.ascontiguousarray(np.stack(Cf)).astype(np.float64)
_Wflat = np.ascontiguousarray(Wf)

def score_batch_c(M, control=False):
    lib = _load_kernel()
    M = np.ascontiguousarray(M, dtype=np.float64).reshape(-1, 64)
    out = np.empty(len(M))
    lib.best_scores(len(M), M.ctypes.data, _Cflat.ctypes.data, _Wflat.ctypes.data, int(control), out.ctypes.data)
    return out

# ---- NEW: structures as lists of knots ---------------------------------------------------------------------------------
# A knot is (law, members) with law in {'even', 'odd', 'nae'} and members a tuple of distinction names.  Alice's observer
# distinctions are x1 x2 x3, Bob's y1 y2 y3; a distinction held on both sides is shared.  The two setting births are
# nae(x1, x_{2+a}, za) and nae(y1, y_{2+b}, zb).
OBS = {'A': ('x1', 'x2', 'x3'), 'B': ('y1', 'y2', 'y3')}

def law_ok(law, s, k):
    if law == 'nae': return (s != 0) & (s != k)
    if law == 'even': return (s % 2) == 0
    return (s % 2) == 1

def holders(knots):
    h = {}
    for law, mem in knots:
        for m in mem: h[m] = h.get(m, 0) + 1
    return h

def split_structure(knots_A, knots_B):
    """Return dict with shared, internal names and holder counts per side."""
    hA = holders(knots_A); hB = holders(knots_B)
    shared = sorted(set(hA) & set(hB))
    return dict(hA=hA, hB=hB, shared=shared)

def structure_measures(knots_A, knots_B):
    """Number of knots, extra holders (holders beyond two summed over old distinctions, counting old holders on both sides),
    largest number of holders, the class (L, S or neither), and the observers' old holder counts."""
    hA = holders(knots_A); hB = holders(knots_B)
    tot = dict(hA)
    for k, v in hB.items(): tot[k] = tot.get(k, 0) + v
    extra = sum(max(0, v - 2) for v in tot.values())
    obs = [tot.get(o, 0) for o in OBS['A'] + OBS['B']]
    shared = sorted(set(hA) & set(hB))
    shared_ok = all(hA[s] == 1 and hB[s] == 1 for s in shared)
    obs_on_both = any(o in hB for o in OBS['A']) or any(o in hA for o in OBS['B'])
    if obs_on_both or not shared_ok: cls = 'neither'
    elif all(v == 1 for v in obs): cls = 'L'
    elif all(1 <= v <= 2 for v in obs): cls = 'S'
    else: cls = 'neither'
    internal = [k for k in tot if k not in OBS['A'] + OBS['B'] and k not in shared]
    return dict(knots=len(knots_A) + len(knots_B), knots_A=len(knots_A), knots_B=len(knots_B), extra_holders=extra,
                max_holders=max(tot.values()) if tot else 0, max_holders_internal=max([tot[k] for k in internal], default=0),
                cls=cls, observer_holders=obs, shared=shared, n_internal=len(internal))

def enumerate_ok(names, knots, chunk_bits=22):
    """Yield (offset, bits dict, ok mask) over all words of `names` in chunks (bit i of the word index is names[i])."""
    n = len(names); pos = {nm: i for i, nm in enumerate(names)}
    total = 1 << n; step = 1 << min(n, chunk_bits)
    for off in range(0, total, step):
        idx = np.arange(off, off + step, dtype=np.int64)
        bits = {nm: ((idx >> i) & 1).astype(np.int8) for nm, i in pos.items()}
        ok = np.ones(step, dtype=bool)
        for law, mem in knots:
            s = sum(bits[m] for m in mem)
            ok &= law_ok(law, s, len(mem))
        yield off, bits, ok

def side_table(knots, own, cut):
    """Side table T[x, s]: number of completions of the side's other distinctions for each value x of its three observer
    distinctions `own` and each value s of its shared distinctions `cut` (in the given order), by direct enumeration."""
    names = []
    for law, mem in knots:
        for m in mem:
            if m not in names: names.append(m)
    for m in list(own) + list(cut):
        if m not in names: names.append(m)        # an observer or cut distinction with no holder is free
    K = 1 << len(cut)
    T = np.zeros((8, K), dtype=np.int64)
    for off, bits, ok in enumerate_ok(names, knots):
        xi = bits[own[0]].astype(np.int64) * 4 + bits[own[1]] * 2 + bits[own[2]]
        si = np.zeros_like(xi)
        for c_ in cut: si = si * 2 + bits[c_]
        np.add.at(T, (xi[ok], si[ok]), 1)
    return T

def old_table(knots_A, knots_B):
    """M = T_A T_B^T over the shared distinctions (product of side tables)."""
    sh = sorted(set(holders(knots_A)) & set(holders(knots_B)))
    TA = side_table(knots_A, OBS['A'], sh); TB = side_table(knots_B, OBS['B'], sh)
    return TA @ TB.T, TA, TB, sh

def brute_joint(knots_A, knots_B, a, b):
    """16x16 joint record counts of the finished structure for settings (a, b) by enumerating every word of the whole finished
    structure (old knots of both sides plus the two births), with no side-table shortcut."""
    ks = list(knots_A) + list(knots_B) + [('nae', ('x1', f'x{2 + a}', 'za')), ('nae', ('y1', f'y{2 + b}', 'zb'))]
    names = []
    for law, mem in ks:
        for m in mem:
            if m not in names: names.append(m)
    J = np.zeros((16, 16), dtype=np.int64)
    for off, bits, ok in enumerate_ok(names, ks):
        ra = ((bits['x1'].astype(np.int64) * 4 + bits['x2'] * 2 + bits['x3']) * 2 + bits['za'])[ok]
        rb = ((bits['y1'].astype(np.int64) * 4 + bits['y2'] * 2 + bits['y3']) * 2 + bits['zb'])[ok]
        np.add.at(J, (ra, rb), 1)
    return J, len(names)

def evaluate_joint(J):
    """Exact evaluation from the four 16x16 brute-force joint record tables J[(a,b)]: hidden flags (exact, integers), best
    parity score (exact Fraction, from the float screen as in exact_best), largest change of a complete record (Fraction)."""
    # hidden: Alice's complete-record distribution for each a is the same for b = 0, 1; likewise Bob
    hidA = all(np.array_equal(J[a, 0].sum(1) * int(J[a, 1].sum()), J[a, 1].sum(1) * int(J[a, 0].sum())) for a in (0, 1))
    hidB = all(np.array_equal(J[0, b].sum(0) * int(J[1, b].sum()), J[1, b].sum(0) * int(J[0, b].sum())) for b in (0, 1))
    tv = Fraction(0)
    for a in (0, 1):
        p = [J[a, b].sum(1) for b in (0, 1)]
        tv = max(tv, sum(abs(Fraction(int(u), int(p[0].sum())) - Fraction(int(v), int(p[1].sum()))) for u, v in zip(*p)) / 2)
    for b in (0, 1):
        p = [J[a, b].sum(0) for a in (0, 1)]
        tv = max(tv, sum(abs(Fraction(int(u), int(p[0].sum())) - Fraction(int(v), int(p[1].sum()))) for u, v in zip(*p)) / 2)
    Ef = {}; Ex = {}
    for a in (0, 1):
        for b in (0, 1):
            num = SGN @ J[a, b] @ SGN.T; den = int(J[a, b].sum())
            Ef[a, b] = num / den
            Ex[a, b] = (num, den)
    best = Fraction(-1); arg = None
    allv = []; gbest = 0.0
    for p in range(4):
        s = np.ones(4); s[p] = -1
        V = (s[0] * Ef[0, 0][:, None, :, None] + s[1] * Ef[0, 1][:, None, None, :] + s[2] * Ef[1, 0][None, :, :, None] + s[3] * Ef[1, 1][None, :, None, :])
        allv.append(V); gbest = max(gbest, float(np.abs(V).max()))
    for p in range(4):
        s = [1] * 4; s[p] = -1
        for kA0, kA1, kB0, kB1 in np.argwhere(np.abs(allv[p]) >= gbest - 1e-7):
            v = (s[0] * Fraction(int(Ex[0, 0][0][kA0, kB0]), Ex[0, 0][1]) + s[1] * Fraction(int(Ex[0, 1][0][kA0, kB1]), Ex[0, 1][1])
                 + s[2] * Fraction(int(Ex[1, 0][0][kA1, kB0]), Ex[1, 0][1]) + s[3] * Fraction(int(Ex[1, 1][0][kA1, kB1]), Ex[1, 1][1]))
            if abs(v) > best: best = abs(v); arg = (int(kA0) + 1, int(kA1) + 1, int(kB0) + 1, int(kB1) + 1, p)
    return dict(hidden_A=bool(hidA), hidden_B=bool(hidB), hidden=bool(hidA and hidB), score=best, arg=arg, change=tv)

def full_check(knots_A, knots_B):
    """Full enumeration of the four finished structures, and agreement with the side-table product."""
    J = {}; nn = None
    for a in (0, 1):
        for b in (0, 1):
            J[a, b], nn = brute_joint(knots_A, knots_B, a, b)
    ev = evaluate_joint(J)
    M, TA, TB, sh = old_table(knots_A, knots_B)
    agree = all(np.array_equal(J[a, b], F[a].T @ M @ F[b]) for a in (0, 1) for b in (0, 1))
    ev.update(distinctions_finished=nn, words_finished=[int(J[a, b].sum()) for a in (0, 1) for b in (0, 1)],
              agrees_with_side_tables=bool(agree), old_words=int(M.sum()))
    return ev

def fmt_knots(knots):
    return [f'{law}({",".join(mem)})' for law, mem in knots]

def parse_knots(lst):
    out = []
    for s in lst:
        law, rest = s.split('(')
        out.append((law, tuple(rest.rstrip(')').split(','))))
    return out

def fstr(v):
    return None if v is None else (str(v) if not isinstance(v, float) else repr(v))

# ---- NEW: structures stored by sides.py ----------------------------------------------------------------------------------
LAWNAME = ['even', 'odd', 'nae']
def side_struct(row, nk, cut, who, cut_names=None, perm=None):
    """Knot list of one stored side structure (row = structs[t], nk = knots[t]) for side `who` in 'AB'.  The cut
    distinctions are named cut_names (default s1, s2), internal ones Ah1.. or Bh1..  perm: optional reordering of the
    cut names (cut index j is named cut_names[perm[j]])."""
    cut_names = cut_names or [f's{j + 1}' for j in range(cut)]
    perm = perm if perm is not None else list(range(cut))
    own = OBS[who]
    def nm(j):
        if j < 3: return own[j]
        if j < 3 + cut: return cut_names[perm[j - 3]]
        return f'{who}h{j - 2 - cut}'
    out = []
    for k in range(int(nk)):
        ar, law = int(row[k][0]), int(row[k][1])
        out.append((LAWNAME[law], tuple(nm(int(m)) for m in row[k][2:2 + ar])))
    return out
