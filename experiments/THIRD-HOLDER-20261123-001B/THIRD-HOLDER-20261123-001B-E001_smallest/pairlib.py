"""Side-table preparation and the exact reduction used by pairs.py and pairs_c.py (THIRD-HOLDER-20261123-001B-E001).

The reduction (deviations.md, item 4).  For a side table T (8 old values x K values of the shared distinctions) write
p_b(T) = T^T W_b.  M = T_A T_B^T.  Alice's complete record hides Bob's setting iff T_A p_0(T_B) || T_A p_1(T_B); Bob's iff
T_B p_0(T_A) || T_B p_1(T_A).
 (1) p_0 || p_1 for both tables ("both parallel"): hidden, with one common local explanation (hidden value = the shared
     distinctions, weight p_0(T_A) p_0(T_B) entrywise up to scale): score at most 2.
 (2) a table of rank 1: M has rank 1, the old words are a product: hidden, score at most 2.
 (3) otherwise a hidden pair has a non-parallel side; put it as Bob.  Alice's hiding then holds iff the kernel of T_A meets
     the plane span(p_0(T_B), p_1(T_B)) (for a pair with an allowed old word).  It depends on T_A only through its kernel and
     on T_B only through that plane.  With K = 2 the plane is everything, so T_A would have rank 1: no excess with one
     shared distinction.
 (4) if M has rank at most 2, its columns span a pointed cone in a plane with two extreme columns, so M = A' B'^T with
     non-negative A', B' of two columns, and (1)-(3) with K = 2 give a score at most 2.  So an excess needs both tables of
     rank at least 3, and (K = 4) the hiding side T_A of rank exactly 3, its kernel a line k in span(p_0(T_B), p_1(T_B)).
"""
import itertools
import numpy as np
import common as c

def load(tag):
    """Exact tables of a sides_*.npz -> projective tables (divided by the gcd), with the smallest structure per table."""
    d = np.load(f'{c.ART}/sides_{tag}.npz')
    T = d['T'].astype(np.int64); ne = d['nonempty']
    kn = d['knots'].astype(np.int64); ex = d['extra'].astype(np.int64)
    idx0 = np.nonzero(ne)[0]
    T = T[ne]; kn = kn[ne]; ex = ex[ne]
    g = np.gcd.reduce(T.reshape(len(T), -1), axis=1)
    Tp = T // g[:, None, None]
    flat = Tp.reshape(len(Tp), -1)
    U, inv = np.unique(flat, axis=0, return_inverse=True)
    inv = inv.reshape(-1)
    order = np.lexsort((ex, kn, inv))
    first = np.ones(len(order), dtype=bool); first[1:] = inv[order][1:] != inv[order][:-1]
    rep = np.empty(len(U), dtype=np.int64); rep[inv[order][first]] = order[first]
    return dict(T=U.reshape(len(U), 8, -1), rep=idx0[rep], knots=kn[rep], extra=ex[rep], n_exact=int(len(d['T'])),
                n_nonempty=int(ne.sum()), mult=np.bincount(inv, minlength=len(U)), tag=tag)

def orbit_reps(S):
    """Reduce a projective table list to one table per orbit under the four row maps of a side (swap x2<->x3, flip the three
    old values); the representative is the member with the smallest structure.  Pairs of representatives stand for every
    ordered pair of the list: the old table of an image pair is an image of the old table under the evaluation's symmetries."""
    T = S['T']; n = len(T)
    imgs = np.stack([T[:, p, :].reshape(n, -1) for p in c.ROW_PERMS], 1)        # (n,4,8K)
    # canonical = lexicographically smallest image
    can = imgs[:, 0].copy()
    for g in range(1, 4):
        cand = imgs[:, g]
        diff = cand != can
        firstd = diff.argmax(1)
        less = diff.any(1) & (cand[np.arange(n), firstd] < can[np.arange(n), firstd])
        can[less] = cand[less]
    u, inv = np.unique(can, axis=0, return_inverse=True); inv = inv.reshape(-1)
    order = np.lexsort((S['extra'], S['knots'], inv))
    first = np.ones(n, dtype=bool); first[1:] = inv[order][1:] != inv[order][:-1]
    reps = order[first]
    size = np.bincount(inv, minlength=len(u))[inv[reps]]
    out = {k: (v[reps] if isinstance(v, np.ndarray) and len(v) == n else v) for k, v in S.items()}
    out['orbit_size'] = size; out['n_projective'] = n
    return out

def det2(a, b, c_, d):
    return a * d - b * c_

def det3(A):
    return (A[..., 0, 0] * (A[..., 1, 1] * A[..., 2, 2] - A[..., 1, 2] * A[..., 2, 1])
            - A[..., 0, 1] * (A[..., 1, 0] * A[..., 2, 2] - A[..., 1, 2] * A[..., 2, 0])
            + A[..., 0, 2] * (A[..., 1, 0] * A[..., 2, 1] - A[..., 1, 1] * A[..., 2, 0]))

def det4(A):
    return sum(((-1) ** j) * A[..., 0, j] * det3(np.delete(A[..., 1:, :], j, axis=-1)) for j in range(4))

def primitive(V):
    g = np.gcd.reduce(np.abs(V), axis=1); g[g == 0] = 1
    V = V // g[:, None]
    sgn = np.sign(V[np.arange(len(V)), (V != 0).argmax(1)]); sgn[sgn == 0] = 1
    return V * sgn[:, None]

PAIRS4 = list(itertools.combinations(range(4), 2))

def _exact_one(T):
    """Exact rank, kernel line (rank 3) and row-space Pluecker vector (rank 2) of one integer table, by fraction-free
    elimination in Python integers (used when the entries are too large for the int64 Gram method)."""
    from fractions import Fraction
    rows = [[Fraction(int(v)) for v in r] for r in T]
    K = len(rows[0]); piv = []; R = []
    for col in range(K):
        pr = next((i for i in range(len(rows)) if rows[i][col] != 0), None)
        if pr is None: continue
        r = rows.pop(pr); r = [v / r[col] for v in r]
        rows = [[v - w * rr[col] for v, w in zip(rr, r)] for rr in rows]
        R = [[v - w * rr[col] for v, w in zip(rr, r)] for rr in R]
        R.append(r); piv.append(col)
    rank = len(R)
    key = [0] * 6
    def prim(v):
        import math
        den = 1
        for x in v: den = den * x.denominator // math.gcd(den, x.denominator)
        iv = [int(x * den) for x in v]
        g = 0
        for x in iv: g = math.gcd(g, abs(x))
        iv = [x // g for x in iv] if g else iv
        f = next((x for x in iv if x != 0), 1)
        return [x if f > 0 else -x for x in iv]
    if K == 4 and rank == 3:
        free = [j for j in range(4) if j not in piv][0]
        k = [Fraction(0)] * 4; k[free] = Fraction(1)
        for r, pc in zip(R, piv): k[pc] = -r[free]
        key[:4] = prim(k)
    if K == 4 and rank == 2:
        r1, r2 = R
        key = prim([r1[i] * r2[j] - r1[j] * r2[i] for i, j in PAIRS4])
    return rank, key

def classify(T, chunk=200000):
    """Exact: p vectors, parallel flag, support of the shared values, rank, kernel key (rank 3: primitive kernel line; rank 2:
    primitive Pluecker vector of the row space), primitive Pluecker vector of span(p0, p1).  Ranks from the Gram matrix
    G = T^T T in int64 (positive semidefinite: rank = size of its largest non-singular principal minor; kernel of T = kernel
    of G; exact while every entry of T is at most 55), else by exact elimination table by table."""
    parts = []
    big = int(T.max()) > 55
    for i0 in range(0, len(T), chunk):
        X = T[i0:i0 + chunk]; n = len(X); K = X.shape[2]
        p = np.stack([np.einsum('nxk,x->nk', X, c.W[b]) for b in (0, 1)], 1)
        par = c.parallel_rows(p[:, 0], p[:, 1])
        supp = ((X.sum(1) > 0) * (1 << np.arange(K))).sum(1)
        rank = np.zeros(n, dtype=np.int64)
        key = np.zeros((n, 6), dtype=np.int64); P = np.zeros((n, 6), dtype=np.int64)
        if big:
            for t in range(n):
                rank[t], key[t] = _exact_one(X[t])
        else:
            G = np.einsum('nxk,nxl->nkl', X, X)
            rank[(np.diagonal(G, axis1=1, axis2=2) > 0).any(1)] = 1
            if K == 2:
                d = G[:, 0, 0] * G[:, 1, 1] - G[:, 0, 1] * G[:, 1, 0]
                rank[d != 0] = 2
            else:
                m2 = np.stack([G[:, i, i] * G[:, j, j] - G[:, i, j] * G[:, j, i] for i, j in PAIRS4], 1)
                rank[(m2 != 0).any(1)] = 2
                trip = list(itertools.combinations(range(4), 3))
                m3 = np.stack([det3(G[:, list(t)][:, :, list(t)]) for t in trip], 1)
                rank[(m3 != 0).any(1)] = 3
                rank[det4(G) != 0] = 4
                i3 = np.nonzero(rank == 3)[0]
                if len(i3):
                    Gi = G[i3]
                    adj = np.zeros((len(i3), 4, 4), dtype=np.int64)
                    for r in range(4):
                        for s_ in range(4):
                            minor = np.delete(np.delete(Gi, r, axis=1), s_, axis=2)
                            adj[:, s_, r] = ((-1) ** (r + s_)) * det3(minor)
                    col = (adj != 0).any(1).argmax(1)
                    key[i3, :4] = primitive(adj[np.arange(len(i3)), :, col])
                i2 = np.nonzero(rank == 2)[0]
                if len(i2):
                    Gi = G[i2]
                    R = np.zeros((len(i2), 6), dtype=np.int64); done = np.zeros(len(i2), dtype=bool)
                    for a, b in PAIRS4:
                        Pl = np.stack([Gi[:, i, a] * Gi[:, j, b] - Gi[:, j, a] * Gi[:, i, b] for i, j in PAIRS4], 1)
                        nz = (Pl != 0).any(1) & ~done
                        R[nz] = Pl[nz]; done |= nz
                    assert done.all()
                    key[i2] = primitive(R)
        if K == 4:
            i3 = np.nonzero(rank == 3)[0]
            assert (np.einsum('nxk,nk->nx', X[i3], key[i3, :4]) == 0).all() and (key[i3, :4] != 0).any(1).all()
            P = primitive(np.stack([p[:, 0, a] * p[:, 1, b] - p[:, 0, b] * p[:, 1, a] for a, b in PAIRS4], 1))
        parts.append(dict(p=p, par=par, supp=supp, rank=rank, key=key, P=P))
    return {k: np.concatenate([q[k] for q in parts]) for k in parts[0]}

def classes(keys):
    if len(keys) == 0:
        return np.zeros((0, keys.shape[1]), np.int64), np.zeros(0, np.int64)
    u, inv = np.unique(keys, axis=0, return_inverse=True)
    return u, inv.reshape(-1)

def compat_matrix(uK, uP, K=4):
    """bool (nK, nP): kernel class (first column = rank 2 or 3, then the key) meets plane class.  Exact: int64 products with
    bounds asserted (Python integers otherwise)."""
    out = np.zeros((len(uK), len(uP)), dtype=bool)
    if len(uK) == 0 or len(uP) == 0 or K != 4: return out
    bigP = int(np.abs(uP).max()); bigK = int(np.abs(uK[:, 1:]).max())
    dt = np.int64 if 6 * bigP * bigK < 2 ** 62 else object
    Pz = uP.astype(dt)
    r2 = uK[:, 0] == 2; r3 = uK[:, 0] == 3
    if r2.any():
        R = uK[r2, 1:].astype(dt)
        out[r2] = (R @ Pz.T) == 0                     # Cauchy-Binet: kernel meets plane iff R . P = 0
    if r3.any():
        k = uK[r3, 1:5].astype(dt)
        idx = {pq: q for q, pq in enumerate(PAIRS4)}
        ok = np.ones((int(r3.sum()), len(uP)), dtype=bool)
        for (a, b, cc) in ((0, 1, 2), (0, 1, 3), (0, 2, 3), (1, 2, 3)):     # (P wedge k) = 0
            v = (np.outer(k[:, cc], Pz[:, idx[(a, b)]]) - np.outer(k[:, b], Pz[:, idx[(a, cc)]]) + np.outer(k[:, a], Pz[:, idx[(b, cc)]]))
            ok &= (v == 0)
        out[r3] = ok
    return out
