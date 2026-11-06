"""Bimap B: H^1(M;F4_{w^2})_x x H^1(M;F4_{w^2})_y -> W (span of obstruction classes) for G = UT3(F4) x| C3 (hard action), its radicals,
centroid and fully refined direct decomposition (idempotents of the centroid = fixed space of Frobenius)."""
import itertools, random, sys
sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[1] / "UT3-TWIST-PROBE-20261025-001"))
import probe as PR
SLA, CHC = PR.SLA, PR.CHC
fmul = PR.fmul

def solve_aff(rows, rhs, n): return SLA.affine_solve_f2(rows, rhs, n)

def rank_basis(vectors):
    return PR.echelon(vectors)

def in_span_coords(v, basis_vecs):
    """coordinates of v in the span of basis_vecs (list of F2 vectors), or None"""
    n = len(basis_vecs)
    if n == 0:
        return [] if not any(v) else None
    rows = [[basis_vecs[j][t] for j in range(n)] for t in range(len(v))]
    sol = solve_aff(rows, v, n)
    return None if sol is None else sol[0]

def extract(G, ngen, rels, psi, section=lambda x, y: 0, rng=None, shift_reps=False):
    def rel_vals(xbits, ybits, avec=None):
        vals = []
        for g in range(ngen):
            x = xbits[2 * g] | (xbits[2 * g + 1] << 1); y = ybits[2 * g] | (ybits[2 * g + 1] << 1)
            z = section(x, y) ^ (avec[g] if avec else 0)
            vals.append(G.E.index((x, y, z, psi[g] % 3)))
        out = []
        for r in rels:
            X, Y, Z, e = G.E[G.word(r, vals)]
            assert e == 0
            out.append((X, Y, Z))
        return out
    n2 = 2 * ngen
    b2 = lambda v: [v & 1, v >> 1]
    Z0 = [0] * n2
    # x-cocycles (y = 0) and y-cocycles (x = 0): linear equations
    def cocycles(which):
        f0 = rel_vals(Z0, Z0)
        cols = []
        for i in range(n2):
            e = [int(t == i) for t in range(n2)]
            cols.append(rel_vals(e, Z0) if which == "x" else rel_vals(Z0, e))
        rows = []
        for ri in range(len(rels)):
            for comp in range(4):
                sel = (lambda tr: b2(tr[0])[comp]) if comp < 2 else (lambda tr: b2(tr[1])[comp - 2])
                rows.append([sel(cols[i][ri]) ^ sel(f0[ri]) for i in range(n2)])
        return SLA.nullspace_mod(rows, n2, 2)
    Zx, Zy = cocycles("x"), cocycles("y")
    # coboundaries: conjugate the section representation by (x0,0,0) or (0,y0,0): cocycle value x0 + w^{2 psi} x0 per generator
    def cob(x0):
        v = []
        for g in range(ngen):
            val = x0 ^ fmul(PR.W2 if psi[g] % 3 == 1 else (PR.W if psi[g] % 3 == 2 else 1), x0)
            v += b2(val)
        return v
    Bx = [cob(1), cob(2)]
    # A-coboundary image in the relator z-space
    zb = lambda rv: [b for (X, Y, Z) in rv for b in b2(Z)]
    z0 = zb(rel_vals(Z0, Z0))
    dcols = []
    for g in range(ngen):
        for bit in (1, 2):
            av = [0] * ngen; av[g] = bit
            dcols.append([a ^ b for a, b in zip(zb(rel_vals(Z0, Z0, av)), z0)])
    im = PR.echelon(dcols)
    red = lambda v: PR.reduce(v, im)
    # H^1 basis: complement of coboundaries inside cocycles
    def h1_basis(Zb, Bb):
        basis = PR.echelon([b[:] for b in Bb])
        out = []
        for v in Zb:
            w = PR.reduce(v, basis)
            if any(w):
                basis = PR.echelon([b for _, b in basis] + [v])
                out.append(v)
        return out
    Hx, Hy = h1_basis(Zx, Bx), h1_basis(Zy, Bx)
    # coboundaries must be cocycles (checked against the computed cocycle spaces)
    for bvec in Bx:
        assert SLA.affine_solve_f2([[Zx[j][t] for j in range(len(Zx))] for t in range(n2)], bvec, len(Zx)) is not None, "x-coboundary not a cocycle"
        assert SLA.affine_solve_f2([[Zy[j][t] for j in range(len(Zy))] for t in range(n2)], bvec, len(Zy)) is not None, "y-coboundary not a cocycle"
    if shift_reps and rng:
        def shift(v):
            c1, c2 = rng.randint(0, 1), rng.randint(0, 1)
            return [a ^ (c1 & b1) ^ (c2 & b2_) for a, b1, b2_ in zip(v, Bx[0], Bx[1])]
        Hx = [shift(v) for v in Hx]
        Hy = [shift(v) for v in Hy]
    o = lambda xb, yb: red(zb(rel_vals(xb, yb)))
    o00 = o(Z0, Z0)
    assert not any(o00)
    # sanity: pure x or pure y cocycles have zero obstruction; coboundaries pair to zero
    for v in Zx[:3]: assert not any(o(v, Z0))
    for v in Zy[:3]: assert not any(o(Z0, v))
    for bvec in Bx:
        for v in Zy: assert not any(o(bvec, v)), "coboundary pairs nontrivially"
    Bvals = {}
    for i, a in enumerate(Hx):
        for j, b in enumerate(Hy):
            Bvals[(i, j)] = o(a, b)
    # bilinearity sanity on a few sums
    if len(Hx) >= 2 and len(Hy) >= 1:
        s = [p ^ q for p, q in zip(Hx[0], Hx[1])]
        assert o(s, Hy[0]) == [p ^ q for p, q in zip(Bvals[(0, 0)], Bvals[(1, 0)])]
    return Hx, Hy, Bvals, len(im)

def tensor(Bvals, u, v):
    """W = span of values; returns (u, v, w, T) with T[t][i][j] in F2 coordinates of W"""
    vals = [Bvals[(i, j)] for i in range(u) for j in range(v)]
    Wb = [b for _, b in PR.echelon(vals)]
    w = len(Wb)
    T = [[[0] * v for _ in range(u)] for _ in range(w)]
    for i in range(u):
        for j in range(v):
            c = in_span_coords(Bvals[(i, j)], Wb) if w else []
            for t in range(w): T[t][i][j] = c[t]
    return w, T

def strip_radicals(T, u, v, w):
    # left radical: a with sum_i a_i T[t][i][j] = 0 for all t, j
    rowsL = [[T[t][i][j] for i in range(u)] for t in range(w) for j in range(v)]
    radL = SLA.nullspace_mod(rowsL, u, 2) if u else []
    rowsR = [[T[t][i][j] for j in range(v)] for t in range(w) for i in range(u)]
    radR = SLA.nullspace_mod(rowsR, v, 2) if v else []
    # choose complements and project: new basis = complement vectors; tensor on complement (radical directions pair to zero)
    def complement(rad, n):
        basis = PR.echelon([r[:] for r in rad]); out = []
        for i in range(n):
            e = [int(t == i) for t in range(n)]
            if any(PR.reduce(e, basis)):
                basis = PR.echelon([b for _, b in basis] + [e]); out.append(e)
        return out
    CU, CV = complement(radL, u), complement(radR, v)
    T2 = [[[sum(a[i] * T[t][i][j] * b[j] for i in range(u) for j in range(v)) % 2 for b in CV] for a in CU] for t in range(w)]
    return len(radL), len(radR), len(CU), len(CV), T2

def nullspace_bits(rows, n):
    """F2 nullspace with rows as Python ints (bit c = column c)"""
    piv = {}
    for r in rows:
        x = 0
        for c, bit in enumerate(r):
            if bit: x |= 1 << c
        for c in sorted(piv, reverse=False):
            pass
        while x:
            c = x.bit_length() - 1
            if c in piv:
                x ^= piv[c]
            else:
                piv[c] = x
                break
    # back-substitute to reduced form
    cols = sorted(piv)
    for c in cols:
        for d in cols:
            if d != c and (piv[d] >> c) & 1:
                piv[d] ^= piv[c]
    free = [c for c in range(n) if c not in piv]
    basis = []
    for fc in free:
        v = [0] * n
        v[fc] = 1
        for c, row in piv.items():
            if (row >> fc) & 1:
                v[c] = 1
        basis.append(v)
    return basis

def centroid(T, u, v, w):
    """basis of {(f, g, h): B(f a, b) = h B(a, b) = B(a, g b)} over F2; unknowns f (u*u), g (v*v), h (w*w)"""
    nf, ng, nh = u * u, v * v, w * w
    N = nf + ng + nh
    F = lambda k, i: k * u + i            # f[k][i]: (f e_i)_k
    Gi = lambda k, j: nf + k * v + j
    H = lambda t, s: nf + ng + t * w + s   # (h e_s)_t
    rows = []
    for i in range(u):
        for j in range(v):
            for t in range(w):
                r = [0] * N   # sum_k f[k][i] T[t][k][j] + sum_s h[t][s] T[s][i][j] = 0
                for k in range(u):
                    if T[t][k][j]: r[F(k, i)] ^= 1
                for s in range(w):
                    if T[s][i][j]: r[H(t, s)] ^= 1
                rows.append(r)
                r = [0] * N   # sum_k g[k][j] T[t][i][k] + sum_s h[t][s] T[s][i][j] = 0
                for k in range(v):
                    if T[t][i][k]: r[Gi(k, j)] ^= 1
                for s in range(w):
                    if T[s][i][j]: r[H(t, s)] ^= 1
                rows.append(r)
    basis = nullspace_bits(rows, N)
    def unpack(x):
        f = [[x[F(k, i)] for i in range(u)] for k in range(u)]
        g = [[x[Gi(k, j)] for j in range(v)] for k in range(v)]
        h = [[x[H(t, s)] for s in range(w)] for t in range(w)]
        return f, g, h
    def pack(f, g, h):
        x = [0] * N
        for k in range(u):
            for i in range(u): x[F(k, i)] = f[k][i]
        for k in range(v):
            for j in range(v): x[Gi(k, j)] = g[k][j]
        for t in range(w):
            for s in range(w): x[H(t, s)] = h[t][s]
        return x
    return basis, unpack, pack

def matmul(A, B_):
    n, m, p = len(A), len(B_), len(B_[0]) if B_ else 0
    return [[sum(A[i][k] & B_[k][j] for k in range(m)) & 1 for j in range(p)] for i in range(n)]

def blocks(T, u, v, w):
    """number of blocks of the finest direct decomposition and their F2 sizes (u_i, v_i, w_i)"""
    if u == 0 or v == 0 or w == 0:
        return 0, [], 0
    basis, unpack, pack = centroid(T, u, v, w)
    c = len(basis)
    # Frobenius x -> x^2 on the centroid, in the basis
    Fm = []
    for x in basis:
        f, g, h = unpack(x)
        y = pack(matmul(f, f), matmul(g, g), matmul(h, h))
        co = in_span_coords(y, basis)
        assert co is not None, "centroid not closed under squaring"
        Fm.append(co)
    # idempotents: coefficient vectors a with Frob(a) = a, i.e. (F^T + I) a = 0
    rows = [[Fm[j][i] ^ (i == j) for j in range(c)] for i in range(c)]
    E = SLA.nullspace_mod(rows, c, 2)
    nE = len(E)
    # atoms of the Boolean algebra of idempotents
    elems = []
    for co in itertools.product((0, 1), repeat=nE):
        a = [0] * c
        for cc, e in zip(co, E):
            if cc: a = [p ^ q for p, q in zip(a, e)]
        if any(a):
            x = [0] * len(basis[0])
            for k in range(c):
                if a[k]: x = [p ^ q for p, q in zip(x, basis[k])]
            elems.append(x)
    def le(e1, e2):  # e1 <= e2 iff e1 * e2 = e1
        f1, g1, h1 = unpack(e1); f2, g2, h2 = unpack(e2)
        return pack(matmul(f1, f2), matmul(g1, g2), matmul(h1, h2)) == e1
    atoms = [e for e in elems if not any(e2 != e and le(e2, e) for e2 in elems)]
    def rk(Mx): return len(PR.echelon([r[:] for r in Mx]))
    sizes = sorted((rk(unpack(e)[0]), rk(unpack(e)[1]), rk(unpack(e)[2])) for e in atoms)
    return nE, sizes, c

def random_change(T, u, v, w, rng):
    def inv_matrix(n):
        while True:
            M = [[rng.randint(0, 1) for _ in range(n)] for _ in range(n)]
            if len(PR.echelon([r[:] for r in M])) == n: return M
    P, Q, R = inv_matrix(u), inv_matrix(v), inv_matrix(w)
    T2 = [[[0] * v for _ in range(u)] for _ in range(w)]
    for t in range(w):
        for i in range(u):
            for j in range(v):
                T2[t][i][j] = sum(R[t][s] & P[a][i] & Q[b][j] & T[s][a][b] for s in range(w) for a in range(u) for b in range(v)) & 1
    return T2

def analyze(G, code, p=3, rng=None, checks=True, section=lambda x, y: 0, shift_reps=False):
    U, rels = SLA.surgery_presentation(code, p)
    h1 = CHC.h1_invariants(code, p)
    out = {"generators": U, "H1": h1}
    for psi in PR.characters(U, rels):
        if psi[0] != 1: continue
        Hx, Hy, Bvals, imrank = extract(G, U, rels, psi, section=section, rng=rng, shift_reps=shift_reps)
        u, v = len(Hx), len(Hy)
        w, T = tensor(Bvals, u, v)
        rl, rr, u2, v2, T2 = strip_radicals(T, u, v, w)
        nb, sizes, cdim = blocks(T2, u2, v2, w)
        row = {"dim H1_x (F2)": u, "dim H1_y": v, "image span W": w, "radicals (L,R)": (rl, rr),
               "nondegenerate part (u,v,w)": (u2, v2, w), "centroid dim": cdim, "blocks": nb, "block sizes (F2)": sizes,
               "coker(delta1) on P": 2 * len(rels) - imrank, "H2(M) = coker - 2": 2 * len(rels) - imrank - 2}
        if checks and rng and u2 and v2 and w:
            ok = True
            for _ in range(3):
                T3 = random_change(T2, u2, v2, w, rng)
                nb3, sizes3, _ = blocks(T3, u2, v2, w)
                ok &= (nb3, sizes3) == (nb, sizes)
            row["random basis changes agree"] = ok
        out["psi=1"] = row
    return out
