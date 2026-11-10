"""Library for CHAIN-ORDERS-20261110-001A: the reduced form of the cut-open torus's family at every order, at sides 2^m.

The family Z(w) = S + M_(Omega(w)) on F[k]_(<h) of JORDAN-CHAINS-20261110-001A, with u = (w - a)/a. Here: its sparse Taylor form, the
symmetric Lyapunov-Schmidt reduction M onto ker Z(a) = G F[Y]_(<J) (as power series), the moment (Hankel) family psi(w), the leading
matrices Gamma^(k) over GF(2), and the reparametrized family Zhat(l) = (1 + l) Z(a + a l/(1 + l)) = Z_0 + l S + (even in l)."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CHAINS_LIB = ROOT / "proofs/JORDAN-CHAINS-20261110-001A/JORDAN-CHAINS-20261110-001A-P001_the_chains_one_polynomial_heads"
sys.path.insert(0, str(CHAINS_LIB))
import chains_lib as CH  # noqa: E402

BL, RL = CH.BL, CH.RL


def is_pow2(t):
    return t >= 1 and (t & (t - 1)) == 0


def sparse_taylor(F, a, m, L):
    """Theorem 1: Omega(a + d) = (1 + d/a)(Omega_a + sum_(r=1)^(m-1) d^(2^r) k^(h - 2^(r-1))), as coefficient lists for d^0..d^(L-1)"""
    h = 1 << (m - 1)
    b = F.sqrt(a)
    base = [[0] * h for _ in range(L)]
    base[0][0] = b
    for i in range(2, m + 1):
        base[0][h - (1 << (i - 2))] ^= F.pw(b, 1 << i)
    for r in range(1, m):
        if (1 << r) < L:
            base[1 << r][h - (1 << (r - 1))] ^= 1
    ainv = F.inv(a)
    out = [[0] * h for _ in range(L)]
    for i in range(L):
        for d in range(h):
            if base[i][d]:
                out[i][d] ^= base[i][d]
                if i + 1 < L:
                    out[i + 1][d] ^= F.m(ainv, base[i][d])
    return out


def inverse(F, A):
    n = A.shape[0]
    M = np.concatenate([A, np.eye(n, dtype=np.int64)], axis=1)
    for col in range(n):
        p = col + np.nonzero(M[col:, col])[0][0]
        if p != col:
            M[[col, p]] = M[[p, col]]
        M[col] = F.mul_np(np.full(2 * n, F.inv(int(M[col, col])), dtype=np.int64), M[col])
        f = M[:, col].copy()
        f[col] = 0
        idx = np.nonzero(f)[0]
        if len(idx):
            M[idx] ^= F.mul_np(f[idx][:, None], M[col][None, :])
    return M[:, n:]


def series_mul(F, A, B, L):
    out = [np.zeros((A[0].shape[0], B[0].shape[1]), dtype=np.int64) for _ in range(L)]
    for i in range(min(L, len(A))):
        if not A[i].any():
            continue
        for j in range(min(L - i, len(B))):
            if B[j].any():
                out[i + j] ^= BL.matmul(F, A[i], B[j])
    return out


def series_inv(F, A, L):
    A0i = inverse(F, A[0])
    out = [A0i]
    for r in range(1, L):
        acc = np.zeros_like(A0i)
        for s in range(1, r + 1):
            if s < len(A) and A[s].any():
                acc ^= BL.matmul(F, A[s], out[r - s])
        out.append(BL.matmul(F, A0i, acc))
    return out


def monic_least(F, a, m):
    """G (monic least-degree element of ker X_b), k, the kernel basis G Y^j"""
    h = 1 << (m - 1)
    ker, G = CH.least_polynomial(F, RL.star_matrix(F, F.sqrt(a), m, h))
    if G is None:
        return None, 0, []
    G = F.mul_np(np.full(len(G), F.inv(int(G[-1])), dtype=np.int64), G)
    return G, h - (len(G) - 1), CH.cyclic_basis(G, h)


def schur(F, Zs, fam, Wbasis, L):
    """the symmetric reduction M = B_KK - B_KW B_WW^-1 B_WK (B = Z^T Gam), basis [fam | Wbasis], as a list of J x J matrices"""
    h = Zs[0].shape[0]
    J = len(fam)
    P = np.zeros((h, h), dtype=np.int64)
    for j, f in enumerate(fam):
        P[:, j] = f
    for t, w in enumerate(Wbasis):
        P[:, J + t] = w
    Gam = BL.gram(h)
    Bs = [BL.matmul(F, BL.matmul(F, P.T.copy(), BL.matmul(F, Z.T.copy(), Gam)), P) for Z in Zs]
    BKK = [B[:J, :J] for B in Bs]
    BKW = [B[:J, J:] for B in Bs]
    BWK = [B[J:, :J] for B in Bs]
    BWW = [B[J:, J:] for B in Bs]
    if BKK[0].any() or BKW[0].any():
        raise ValueError("not a kernel basis")
    corr = series_mul(F, series_mul(F, BKW, series_inv(F, BWW, L), L), BWK, L)
    return [BKK[r] ^ corr[r] for r in range(L)]


def monomial_complement(G, h, J):
    tops = {len(G) - 1 + 2 * j for j in range(J)}
    out = []
    for d in range(h):
        if d not in tops:
            e = np.zeros(h, dtype=np.int64)
            e[d] = 1
            out.append(e)
    return out


def reduction(F, a, m, L):
    """k, J and the reduction M(d) of Z(a + d) (monomial complement, G monic), coefficients of d^0..d^(L-1)"""
    G, k, fam = monic_least(F, a, m)
    if G is None:
        return 0, 0, []
    h = 1 << (m - 1)
    return k, len(fam), schur(F, CH.coefficients(F, a, m, L), fam, monomial_complement(G, h, len(fam)), L)


def leading_form_at(F, a, m):
    """the target: v(M_ij) >= e = 2k - 1 - 2(i + j) and [d^e] M_ij = a^-e [k - i - j is a power of two]"""
    K = F.kloosterman(a)
    kk = (abs(K - 1) - 1) // 2
    if kk == 0:
        return {"k": 0, "ok": True}
    L = 2 * kk
    k, J, M = reduction(F, a, m, L)
    bad = []
    for i in range(J):
        for j in range(J):
            e = 2 * k - 1 - 2 * (i + j)
            if any(M[r][i, j] for r in range(min(e, L))):
                bad.append([i, j, "low"])
            want = F.pw(a, (-e) % F.q1) if is_pow2(k - i - j) else 0
            if e < L and int(M[e][i, j]) != want:
                bad.append([i, j, "lead"])
    return {"k": k, "J": J, "ok": not bad and k == kk, "bad": bad}


def _pmul(F, x, y, h):
    out = np.zeros(h, dtype=np.int64)
    for i in np.nonzero(x)[0]:
        if i >= h:
            break
        out[i:h] ^= F.mul_np(np.full(h - i, int(x[i]), dtype=np.int64), y[:h - i])
    return out


def _bivariate_inverse(F, A, L, h):
    a0 = A[0]
    inv0 = np.zeros(h, dtype=np.int64)
    c = F.inv(int(a0[0]))
    inv0[0] = c
    for d in range(1, h):
        s = 0
        for e in range(1, d + 1):
            if a0[e] and inv0[d - e]:
                s ^= F.m(int(a0[e]), int(inv0[d - e]))
        inv0[d] = F.m(c, s)
    out = [inv0]
    for r in range(1, L):
        acc = np.zeros(h, dtype=np.int64)
        for s in range(1, r + 1):
            if A[s].any():
                acc ^= _pmul(F, A[s], out[r - s], h)
        out.append(_pmul(F, inv0, acc, h))
    return out


def to_Y(F, f, h):
    """the Y-series (Y = k + k^2) agreeing with the k-series f mod k^h"""
    f = f.copy()
    out = np.zeros(h, dtype=np.int64)
    Ypow = np.zeros(h, dtype=np.int64)
    Ypow[0] = 1
    for j in range(h):
        c = int(f[j])
        out[j] = c
        if c:
            f ^= F.mul_np(np.full(h, c, dtype=np.int64), Ypow)
        nxt = np.zeros(h, dtype=np.int64)
        nxt[1:] ^= Ypow[:-1]
        nxt[2:] ^= Ypow[:-2]
        Ypow = nxt
    return out


def psi_family(F, a, m, L):
    """Theorem 2: psi(a + d) = (Omega + k + 1)/(k Omega + (k + 1)^2) mod k^h, as Y-series for d^0..d^(L-1)"""
    h = 1 << (m - 1)
    oms = [np.array(o, dtype=np.int64) for o in CH.taylor(F, a, m, L)]
    Nser = [o.copy() for o in oms]
    Nser[0][0] ^= 1
    Nser[0][1] ^= 1
    Dser = [np.concatenate([[0], o[:-1]]) for o in oms]
    Dser[0][0] ^= 1
    Dser[0][2] ^= 1
    Dinv = _bivariate_inverse(F, Dser, L, h)
    psi = [np.zeros(h, dtype=np.int64) for _ in range(L)]
    for i in range(L):
        for j in range(L - i):
            psi[i + j] ^= _pmul(F, Nser[i], Dinv[j], h)
    return [to_Y(F, p, h) for p in psi]


def hankel_blocks(F, a, m, L):
    """the partial multiplicities at d = 0 of H(d) = [psi_(i+j+1)(a + d)]_(i, j < h/2)"""
    h = 1 << (m - 1)
    H = h // 2
    Hs = [np.array([[p[i + j + 1] for j in range(H)] for i in range(H)], dtype=np.int64) for p in psi_family(F, a, m, L)]
    return CH.partial_multiplicities(F, Hs, L)


def gamma_invertible(k):
    """Theorem 3: Gamma^(k) = [k - i - j is a power of two]_(i, j < ceil(k/2)) has full rank over GF(2) (rows as bit sets)"""
    J = (k + 1) // 2
    rows = []
    for i in range(J):
        v = 0
        for j in range(J):
            if is_pow2(k - i - j):
                v |= 1 << j
        rows.append(v)
    rank = 0
    for c in range(J):
        piv = next((r for r in range(rank, J) if rows[r] >> c & 1), None)
        if piv is None:
            continue
        rows[rank], rows[piv] = rows[piv], rows[rank]
        for r in range(J):
            if r != rank and rows[r] >> c & 1:
                rows[r] ^= rows[rank]
        rank += 1
    return rank == J


def lam_family(F, a, m, L):
    """Zhat(l) = (1 + l) Z(a + d), d = a l/(1 + l) (so u = d/a = l/(1 + l)): coefficients of l^0..l^(L-1), from the exact Taylor ones"""
    Zs = CH.coefficients(F, a, m, L)
    h = Zs[0].shape[0]
    # d^r = a^r l^r (1 + l)^(-r);  then multiply by (1 + l)
    out = [np.zeros((h, h), dtype=np.int64) for _ in range(L)]
    for r in range(L):
        c = F.pw(a, r)
        for t in range(L - r):
            if CH.binom2(-r + 1, t):          # (1 + l)^(1 - r)
                out[r + t] ^= F.mul_np(np.full((h, h), c, dtype=np.int64), Zs[r])
    return out


def good_complement(G, fam, h, k):
    """a complement of the kernel containing k G Y^j for 2j < k - 1, filled up with monomials"""
    J = len(fam)
    dG = len(G) - 1
    out, used = [], {dG + 2 * j for j in range(J)}
    for j in range(J):
        if 2 * j < k - 1:
            v = np.concatenate([[0], fam[j][:-1]])
            out.append(v)
            used.add(dG + 2 * j + 1)
    for d in range(h):
        if d not in used:
            e = np.zeros(h, dtype=np.int64)
            e[d] = 1
            out.append(e)
    return out


def norm_coeffs(F, G):
    """N(G) = G(k) G(k + 1), tau-invariant, as a polynomial in Y (coefficients of Y^0..Y^(deg G))"""
    G = np.array(G, dtype=np.int64)
    prod = BL.poly_mul(F, G, BL.shift_poly(G))
    return to_Y(F, prod, len(prod))[:len(G)]


def third_order_at(F, a, m):
    """Theorem 5: with a complement W' containing k G Y^j (2j < k - 1), the reduction of Zhat has [l] M_ij = [l^2] M_ij = 0 when
    i + j <= k - 2 and 2i or 2j < k - 1, and [l^3] M_ij = [Y^(h - 2 - i - j)] N(G) when 2i, 2j < k - 1; also checked: with the
    monomial complement of the target, the first two orders vanish whenever i + j <= k - 2"""
    G, k, fam = monic_least(F, a, m)
    if G is None or k < 2:
        return {"k": k, "ok": True}
    h = 1 << (m - 1)
    J = len(fam)
    Zh = lam_family(F, a, m, 4)
    Mg = schur(F, Zh, fam, good_complement(G, fam, h, k), 4)
    Mm = schur(F, Zh, fam, monomial_complement(G, h, J), 4)
    N = norm_coeffs(F, G)
    bad = []
    for i in range(J):
        for j in range(J):
            s = i + j
            if s <= k - 2 and (Mm[1][i, j] or Mm[2][i, j]):
                bad.append([i, j, "order 1 or 2, monomial complement"])
            if s <= k - 2 and (2 * i < k - 1 or 2 * j < k - 1) and (Mg[1][i, j] or Mg[2][i, j]):
                bad.append([i, j, "order 1 or 2"])
            if 2 * i < k - 1 and 2 * j < k - 1:
                c = h - 2 - s
                want = int(N[c]) if 0 <= c < len(N) else 0
                if int(Mg[3][i, j]) != want:
                    bad.append([i, j, "order 3"])
    return {"k": k, "ok": not bad, "bad": bad}


def _gf2_rank(rows, ncols):
    rows = list(rows)
    rank = 0
    for c in range(ncols):
        piv = next((r for r in range(rank, len(rows)) if rows[r] >> c & 1), None)
        if piv is None:
            continue
        rows[rank], rows[piv] = rows[piv], rows[rank]
        for r in range(len(rows)):
            if r != rank and rows[r] >> c & 1:
                rows[r] ^= rows[rank]
        rank += 1
    return rank


def square_blocks(d, kind):
    """Jordan blocks over GF(2) at its eigenvalue of the operator induced on a square of F^d by the single Jordan block e_i -> e_i + e_(i-1)
    ('wedge-group', 'sym-group': u on wedge^2 or Sym^2, minus 1) or by the nilpotent e_i -> e_(i-1) ('wedge-lie': N x 1 + 1 x N on wedge^2)"""
    if kind.startswith("wedge"):
        basis = [(i, j) for i in range(d) for j in range(i + 1, d)]
    else:
        basis = [(i, j) for i in range(d) for j in range(i, d)]
    idx = {p: t for t, p in enumerate(basis)}
    n = len(basis)

    def image(i, j):
        out = 0
        if kind == "wedge-lie":
            terms = [(i - 1, j), (i, j - 1)]
            for x, y in terms:
                if x >= 0 and y >= 0 and x != y:
                    out ^= 1 << idx[(min(x, y), max(x, y))]
            return out
        ui = [i] + ([i - 1] if i else [])
        uj = [j] + ([j - 1] if j else [])
        for x in ui:
            for y in uj:
                if kind == "wedge-group" and x == y:
                    continue
                out ^= 1 << idx[(min(x, y), max(x, y))]
        return out ^ (1 << idx[(i, j)])          # minus the identity
    cols = [image(i, j) for (i, j) in basis]     # column t = image of basis vector t, as a bit set over rows

    def apply(vecs):                             # N applied to bit-set vectors
        out = []
        for v in vecs:
            w, t = 0, 0
            while v:
                if v & 1:
                    w ^= cols[t]
                v >>= 1
                t += 1
            out.append(w)
        return out
    powers, cur, dims = [], [1 << t for t in range(n)], []
    while True:
        cur = apply(cur)
        dims.append(n - _gf2_rank(cur, n))
        if dims[-1] == n:
            break
    ge = [dims[0]] + [dims[i] - dims[i - 1] for i in range(1, len(dims))]
    out = []
    for l in range(len(ge)):
        out += [l + 1] * (ge[l] - (ge[l + 1] if l + 1 < len(ge) else 0))
    return sorted(out, reverse=True)
