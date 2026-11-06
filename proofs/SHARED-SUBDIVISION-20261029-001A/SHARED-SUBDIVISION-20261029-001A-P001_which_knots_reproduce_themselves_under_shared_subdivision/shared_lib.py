"""Library for SHARED-SUBDIVISION-20261029-001A-P001: the 34 three-bit knots in 16 classes; the triangular-lattice torus with copies
of a knot on up triangles (S2) or on all triangles (S1); the shared subdivision by a factor k (fine side L = k m, coarse sites
(k i, k j)); exact counts of fine extensions of every coarse assignment (floats for the support, residues modulo four primes below
2^18 for equality, every float product and sum staying below 2^53); an independent exact counter in Python integers; solution
counts by transfer-matrix traces; enumeration of solutions and an affineness test."""
import itertools
import numpy as np
cube = list(itertools.product((0, 1), repeat=3))
def knots():
    res = []
    def grow(start, E):
        if E: res.append(frozenset(s for s in cube if s not in E))
        for i in range(start, 8):
            s = cube[i]
            if all(sum(a != b for a, b in zip(s, e)) >= 2 for e in E): grow(i + 1, E + [s])
    grow(0, []); return res
def permute(K, p): return frozenset(tuple(s[p[i]] for i in range(3)) for s in K)
def placements(K): return sorted({permute(K, p) for p in itertools.permutations(range(3))}, key=sorted)
def excl(K): return tuple(sorted(set(cube) - K))
K34 = knots()
classes = {}
for K in K34: classes.setdefault(min(tuple(sorted(P)) for P in placements(K)), K)
reps = list(classes.values())
def rules():
    """S2: every knot on up triangles; S1: every pair of placements of one class on up and down triangles"""
    out = [("S2", K, None) for K in K34]
    for K in reps:
        for P1 in placements(K):
            for P2 in placements(K): out.append(("S1", P1, P2))
    return out
PRIMES = (262139, 262133, 262127, 262121)
def transfer(L, Rup, Rdown):
    n = 1 << L
    up = np.zeros(8, bool); dn = np.zeros(8, bool)
    for s in Rup: up[s[0] * 4 + s[1] * 2 + s[2]] = True
    if Rdown is not None:
        for s in Rdown: dn[s[0] * 4 + s[1] * 2 + s[2]] = True
    r = np.arange(n)
    bits = (r[:, None] >> np.arange(L)[None, :]) & 1
    ok = np.ones((n, n), bool)
    for i in range(L):
        a = bits[:, i][:, None]; b = bits[:, (i + 1) % L][:, None]; c = bits[:, i][None, :]
        ok &= up[a * 4 + b * 2 + c]
        if Rdown is not None:
            d = bits[:, (i + 1) % L][:, None]; e = bits[:, i][None, :]; f = bits[:, (i + 1) % L][None, :]
            ok &= dn[d * 4 + e * 2 + f]
    return ok.astype(np.float64), bits
def _modmat(A, B, p):
    return np.mod(A @ B, p)
def coarse_counts(L, k, Rup, Rdown):
    """dict coarse rows (x_0..x_{m-1}) -> (float count, residues); coarse sites are fine sites (k i, k j)"""
    m = L // k
    T, bits = transfer(L, Rup, Rdown)
    key = (bits[:, ::k] * (1 << np.arange(m))[None, :]).sum(1)
    masks = [(key == x).astype(np.float64)[:, None] for x in range(1 << m)]
    Mf = np.linalg.matrix_power(T, k)
    Mp = []
    for p in PRIMES:
        A = np.eye(T.shape[0])
        for _ in range(k): A = _modmat(A, T, p)
        Mp.append(A)
    out = {}
    if m == 3:
        Bf = [Mf * mk for mk in masks]
        Bp = [[A * mk for mk in masks] for A in Mp]
        for x0, x1 in itertools.product(range(8), repeat=2):
            Cf = Bf[x0] @ Bf[x1]
            Cp = [_modmat(Bp[i][x0], Bp[i][x1], p) for i, p in enumerate(PRIMES)]
            for x2 in range(8):
                f = float(np.sum(Cf * Bf[x2].T))
                res = tuple(int(np.sum(Cp[i].astype(np.int64) * Bp[i][x2].T.astype(np.int64)) % p) for i, p in enumerate(PRIMES))
                out[(x0, x1, x2)] = (f, res)
    elif m == 4:
        Bf = np.stack([Mf * mk for mk in masks])
        Cf = np.einsum("pab,qbc->pqac", Bf, Bf).reshape(256, -1)
        CfT = np.einsum("pab,qbc->pqca", Bf, Bf).reshape(256, -1)
        Nf = Cf @ CfT.T
        Np = []
        for i, p in enumerate(PRIMES):
            Bp = np.stack([Mp[i] * mk for mk in masks])
            Cp = np.mod(np.einsum("pab,qbc->pqac", Bp, Bp), p).reshape(256, -1)
            CpT = np.mod(np.einsum("pab,qbc->pqca", Bp, Bp), p).reshape(256, -1)
            Np.append(np.mod(Cp @ CpT.T, p))
        for a in range(256):
            x0, x1 = divmod(a, 16)
            for b in range(256):
                x2, x3 = divmod(b, 16)
                out[(x0, x1, x2, x3)] = (float(Nf[a, b]), tuple(int(Np[i][a, b]) for i in range(len(PRIMES))))
    else:
        raise ValueError("coarse side 3 or 4 only")
    return out
def coarse_solutions(m, Rup, Rdown):
    T, _ = transfer(m, Rup, Rdown)
    return {xs for xs in itertools.product(range(1 << m), repeat=m) if all(T[xs[j], xs[(j + 1) % m]] for j in range(m))}
def exactness(L, k, Rup, Rdown):
    N = coarse_counts(L, k, Rup, Rdown)
    S = coarse_solutions(L // k, Rup, Rdown)
    supp = {x for x, (f, r) in N.items() if f > 0}
    res = {N[x][1] for x in S}
    return {"coarse solutions": len(S), "fine solutions (float)": sum(f for f, r in N.values()), "support equal": supp == S,
            "extra": len(supp - S), "missing": len(S - supp), "uniform": len(res) <= 1,
            "count": (min(N[x][0] for x in S) if S else None)}

def exact_counts_python(L, k, Rup, Rdown, xs):
    """independent exact count of the fine extensions of one coarse assignment xs, by row-by-row propagation in Python integers"""
    m = L // k
    T, bits = transfer(L, Rup, Rdown)
    n = T.shape[0]
    nxt = [[int(s) for s in np.nonzero(T[r])[0]] for r in range(n)]
    key = [int(sum(int(bits[r, k * i]) << i for i in range(m))) for r in range(n)]
    total = 0
    for r0 in range(n):
        if key[r0] != xs[0]: continue
        vec = {r0: 1}
        for step in range(1, L + 1):
            new = {}
            for r, c in vec.items():
                for s in nxt[r]:
                    if step % k == 0 and step < L and key[s] != xs[step // k]: continue
                    new[s] = new.get(s, 0) + c
            vec = new
        total += vec.get(r0, 0)
    return total
def solution_count(L, Rup, Rdown):
    T, _ = transfer(L, Rup, Rdown)
    return float(np.trace(np.linalg.matrix_power(T, L)))
def solutions(L, Rup, Rdown, cap=300000):
    T, _ = transfer(L, Rup, Rdown)
    n = T.shape[0]
    nxt = [[int(s) for s in np.nonzero(T[r])[0]] for r in range(n)]
    out = []
    def rec(rows):
        if len(out) > cap: return
        if len(rows) == L:
            if T[rows[-1], rows[0]]: out.append(tuple(rows))
            return
        for s in nxt[rows[-1]]:
            rows.append(s); rec(rows); rows.pop()
    for r0 in range(n): rec([r0])
    return out if len(out) <= cap else None
def affine(L, sols):
    """an affine subspace of GF(2)^(L*L): |S| = 2^rank(S - s0)"""
    if not sols: return True
    ints = [sum(r << (L * j) for j, r in enumerate(s)) for s in sols]
    s0 = ints[0]; basis = []
    for v in ints:
        v ^= s0
        for b in basis: v = min(v, v ^ b)
        if v: basis.append(v)
    return (1 << len(basis)) == len(ints)
def line_constant(L, sol):
    """the directions (1, 0), (0, 1), (1, -1) along which the configuration is constant"""
    x = [[(sol[j] >> i) & 1 for i in range(L)] for j in range(L)]
    dirs = []
    if all(x[j][i] == x[j][(i + 1) % L] for i in range(L) for j in range(L)): dirs.append("(1, 0)")
    if all(x[j][i] == x[(j + 1) % L][i] for i in range(L) for j in range(L)): dirs.append("(0, 1)")
    if all(x[j][i] == x[(j + 1) % L][(i - 1) % L] for i in range(L) for j in range(L)): dirs.append("(1, -1)")
    return dirs
