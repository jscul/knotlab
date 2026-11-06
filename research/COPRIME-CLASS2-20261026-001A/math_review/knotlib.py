"""Independent re-implementation (no repo code) of: braid closure -> Wirtinger presentation of S^3_3(K);
twisted cocycles for G = UT3(F4) x| C3; the obstruction bimap V x V -> H^2(F4_w); kernel counts; leaf functionals.
Conventions (input format only matches the repo): generator i > 0 = strand at position i-1 crosses OVER position i."""
import itertools

# ---------------- F4: 0,1,2=w,3=w^2=w+1 ; addition = xor
LOG = {1: 0, 2: 1, 3: 2}; EXP = [1, 2, 3]
def m4(a, b):
    return 0 if a == 0 or b == 0 else EXP[(LOG[a] + LOG[b]) % 3]
def inv4(a):
    return EXP[(-LOG[a]) % 3]
def wpow(k):
    return EXP[k % 3]
W, W2 = 2, 3

# ---------------- groups
def gmul(g, h):
    """G = N x| C3 ; (x,y,z,e)(u,v,w,f); h acts by (w^2 x, w^2 y, w z)"""
    x, y, z, e = g; u, v, w, f = h
    u2, v2, w2 = m4(wpow(2 * e), u), m4(wpow(2 * e), v), m4(wpow(e), w)
    return (x ^ u2, y ^ v2, z ^ w2 ^ m4(x, v2), (e + f) % 3)
def ginv(g):
    x, y, z, e = g
    s = wpow(-2 * e)
    return (m4(s, x), m4(s, y), m4(wpow(-e), z ^ m4(x, y)), (-e) % 3)
ONE = (0, 0, 0, 0)
def word_eval(word, img):
    out = ONE
    for a, s in word:
        g = img[a] if s > 0 else ginv(img[a])
        for _ in range(abs(s)):
            out = gmul(out, g)
    return out

# ---------------- braid closure
def closure(word, n):
    """returns dict with arcs, crossings, arc_at[(level, pos)], traversal longitude data"""
    # union-find over provisional arc ids
    par = []
    def new():
        par.append(len(par)); return len(par) - 1
    def fd(a):
        while par[a] != a:
            par[a] = par[par[a]]; a = par[a]
        return a
    cur = [new() for _ in range(n)]
    top = list(cur)
    arc_at = {}
    cross = []  # (level, over_id, in_id, out_id, s, under_pos_before, under_pos_after)
    for L, g in enumerate(word):
        for q in range(n):
            arc_at[(L, q)] = cur[q]
        i = abs(g) - 1   # positions i, i+1
        s = 1 if g > 0 else -1
        left, right = cur[i], cur[i + 1]
        if s > 0:   # left over right: right strand is under, moves to position i
            o, ui = left, right
            uo = new()
            cur[i], cur[i + 1] = uo, o
            cross.append((L, o, ui, uo, s, i + 1, i))
        else:       # left under right: left strand is under, moves to position i+1
            o, ui = right, left
            uo = new()
            cur[i], cur[i + 1] = o, uo
            cross.append((L, o, ui, uo, s, i, i + 1))
    for q in range(len(word), len(word)):
        pass
    for q in range(n):
        arc_at[(len(word), q)] = cur[q]
    # closure: bottom position q == top position q
    for q in range(n):
        a, b = fd(cur[q]), fd(top[q])
        if a != b:
            par[a] = b
    roots = sorted({fd(a) for a in range(len(par))})
    idx = {r: k for k, r in enumerate(roots)}
    A = lambda a: idx[fd(a)]
    arc_at = {k: A(v) for k, v in arc_at.items()}
    cr = [(L, A(o), A(ui), A(uo), s, pb, pa) for (L, o, ui, uo, s, pb, pa) in cross]
    # traversal: follow the strand starting at top position 0
    perm_pos = 0
    visits = []
    q = 0
    steps = 0
    while True:
        for L, g in enumerate(word):
            i = abs(g) - 1
            if q in (i, i + 1):
                c = cr[L]
                # is our strand the under strand here?
                if c[5] == q:
                    visits.append(c)
                    q = c[6]
                else:
                    q = i + 1 if q == i else i
        steps += 1
        if q == 0:
            break
        assert steps <= n
    return {"n_arcs": len(roots), "cross": cr, "arc_at": arc_at, "visits": visits, "steps": steps, "start_arc": arc_at[(0, 0)]}

def presentation(word, n, p=3, longitude_sign=+1):
    K = closure(word, n)
    assert len(K["visits"]) == len(word), "closure not a knot (traversal did not visit every crossing as under)"
    U = K["n_arcs"]
    rels = []
    for (L, o, ui, uo, s, pb, pa) in K["cross"][:-1]:
        rels.append([(o, -s), (ui, 1), (o, s), (uo, -1)])     # x_uo = x_o^-s x_ui x_o^s
    w = sum(c[4] for c in K["cross"])
    mu = K["start_arc"]
    lam = [(c[1], longitude_sign * c[4]) for c in K["visits"]] + [(mu, -longitude_sign * w)]
    rels.append([(mu, p)] + lam)
    return U, rels, K, mu, lam

# ---------------- F4 linear algebra (lists)
def rref(rows, ncol):
    rows = [r[:] for r in rows]
    piv = []
    rk = 0
    for c in range(ncol):
        p = next((i for i in range(rk, len(rows)) if rows[i][c]), None)
        if p is None:
            continue
        rows[rk], rows[p] = rows[p], rows[rk]
        s = inv4(rows[rk][c]); rows[rk] = [m4(s, x) for x in rows[rk]]
        for i in range(len(rows)):
            if i != rk and rows[i][c]:
                g = rows[i][c]; rows[i] = [x ^ m4(g, y) for x, y in zip(rows[i], rows[rk])]
        piv.append(c); rk += 1
    return rows[:rk], piv

def nullspace(rows, ncol):
    R, piv = rref(rows, ncol) if rows else ([], [])
    free = [c for c in range(ncol) if c not in piv]
    basis = []
    for f in free:
        v = [0] * ncol; v[f] = 1
        for r, pc in zip(R, piv):
            v[pc] = r[f]      # char 2: -r[f] = r[f]
        basis.append(v)
    return basis

def reduce_vec(R, piv, v):
    v = v[:]
    for r, pc in zip(R, piv):
        if v[pc]:
            g = v[pc]; v = [x ^ m4(g, y) for x, y in zip(v, r)]
    return v

def rank(rows, ncol):
    return len(rref(rows, ncol)[0]) if rows else 0

# ---------------- cocycles and obstruction
def affine_eval(word, c):
    """value of the twisted cocycle c (w^2-action, psi = 1 on every generator) on a word"""
    t, e = 0, 0
    for a, s in word:
        for _ in range(abs(s)):
            if s > 0:
                t ^= m4(wpow(2 * e), c[a]); e = (e + 1) % 3
            else:
                # g^-1 = (w^{-2} * (-c), -1) -> value w^{-2} c ... combine: (t,e)(t',e') = (t + w^{2e} t', e+e')
                tinv = m4(wpow(-2), c[a])
                t ^= m4(wpow(2 * e), tinv); e = (e - 1) % 3
    return t, e

def cocycle_space(U, rels):
    rows = []
    for r in rels:
        col = []
        for a in range(U):
            c = [0] * U; c[a] = 1
            t, e = affine_eval(r, c)
            assert e == 0
            col.append(t)
        rows.append(col)
    Z1 = nullspace(rows, U)
    const = [W] * U          # coboundary of v=1: w * 1 on every meridian
    # verify constant is a cocycle
    for r in rels:
        assert affine_eval(r, const)[0] == 0
    # basis of Z1 modulo constants
    R, piv = rref([const], U)
    H = []
    for z in Z1:
        rr, pp = rref([const] + H + [z], U)
        if len(rr) == len(H) + 2:
            H.append(z)
    return Z1, H

def obstruction(U, rels, H):
    R = len(rels)
    zero = [0] * U
    # L: z-cochain -> relator z-values
    Lrows = []
    for a in range(U):
        img = [(0, 0, 1 if b == a else 0, 1) for b in range(U)]
        Lrows.append([word_eval(r, img)[2] for r in rels])
    imL, pivL = rref(Lrows, R)
    qcols = [c for c in range(R) if c not in pivL]
    def Bval(cx, cy):
        img = [(cx[b], cy[b], 0, 1) for b in range(U)]
        vals = []
        for r in rels:
            X, Y, Z, e = word_eval(r, img)
            assert X == 0 and Y == 0 and e == 0
            vals.append(Z)
        red = reduce_vec(imL, pivL, vals)
        return [red[c] for c in qcols]
    d = len(H)
    B = [[Bval(H[i], H[j]) for j in range(d)] for i in range(d)]
    return B, len(qcols)

def kernels_from_bimap(B, d, h2):
    """for each a in F4^d (as tuple): canonical rref basis of ker(b -> B(a, b))"""
    out = {}
    for a in itertools.product(range(4), repeat=d):
        rows = []
        for j in range(d):
            v = [0] * h2
            for i in range(d):
                if a[i]:
                    v = [x ^ m4(a[i], y) for x, y in zip(v, B[i][j])]
            rows.append(v)
        # kernel of beta -> sum_j beta_j rows[j]: nullspace of the transpose
        T = [[rows[j][k] for j in range(d)] for k in range(h2)]
        ns = nullspace(T, d) if h2 else [[1 if i == j else 0 for i in range(d)] for j in range(d)]
        out[a] = tuple(map(tuple, rref(ns, d)[0])) if ns else ()
    return out

def det3(r1, r2, r3):
    s = 0
    for p in itertools.permutations(range(3)):
        s ^= m4(m4(r1[p[0]], r2[p[1]]), r3[p[2]])
    return s

def kernels_from_leaves(leafsets, d, T0=None):
    """leafsets: list of [l1, l2, l3], each l = list of values on the basis H (length d).
    T(a,b,c) = sum det; for each a: rref basis of {b : T(a,b,.) = 0}"""
    # precompute T on basis triples
    Tb = [[[0] * d for _ in range(d)] for _ in range(d)]
    for i in range(d):
        for j in range(d):
            for k in range(d):
                s = 0
                for (l1, l2, l3) in leafsets:
                    s ^= det3([l1[i], l2[i], l3[i]], [l1[j], l2[j], l3[j]], [l1[k], l2[k], l3[k]])
                if T0:
                    s ^= T0[i][j][k]
                Tb[i][j][k] = s
    out = {}
    for a in itertools.product(range(4), repeat=d):
        M = [[0] * d for _ in range(d)]   # M[j][k] = T(a, h_j, h_k)
        for i in range(d):
            if a[i]:
                for j in range(d):
                    for k in range(d):
                        if Tb[i][j][k]:
                            M[j][k] ^= m4(a[i], Tb[i][j][k])
        T = [[M[j][k] for j in range(d)] for k in range(d)]
        ns = nullspace(T, d)
        out[a] = tuple(map(tuple, rref(ns, d)[0])) if ns else ()
    return out, Tb

def count(kern):
    return sum(4 ** len(v) for v in kern.values())

def leaf_values(H, arc_at, level, positions):
    """values on the basis H of c_h(x_{p_k} ... x_{p_1}) (right-to-left product of the bundle arcs at the level)"""
    word = [(arc_at[(level, q)], 1) for q in reversed(sorted(positions))]
    vals = []
    for h in H:
        t, e = affine_eval(word, h)
        assert e == len(positions) % 3
        vals.append(t)
    return vals

# ---------------- braids
def fig8_sum(k):
    return [x for i in range(k) for x in (2 * i + 1, -(2 * i + 2), 2 * i + 1, -(2 * i + 2))]

def cable_unequal(word3, sizes, offset):
    """cable a braid word on fat strands (generators +-1, +-2, ...) with bundle sizes per fat strand (tracked as they move);
    thin positions start at `offset` (0-based). Returns the thin word (1-based generators, sign = over/under of left strand)."""
    sizes = list(sizes)
    out = []
    for g in word3:
        i = abs(g) - 1
        s = 1 if g > 0 else -1
        p = offset + sum(sizes[:i])
        a, b = sizes[i], sizes[i + 1]
        for t in range(b):
            # right-bundle strand at thin position p + a + t moves left across a strands of the left bundle
            for pos in range(p + a + t, p + t, -1):
                out.append(s * pos)       # generator index pos swaps thin positions pos-1, pos
        sizes[i], sizes[i + 1] = b, a
    return out, sizes

BORR = [1, -2] * 3

def insert(base, ins):
    """ins: list of (level, thin word); inserted just above base[level] (ties kept in input order, earlier = higher);
    returns new word and the level of each insertion top"""
    by_level = {}
    for t, (L, iw) in enumerate(ins):
        by_level.setdefault(L, []).append(t)
    w, tops = [], [None] * len(ins)
    for L in range(len(base) + 1):
        for t in by_level.get(L, []):
            tops[t] = len(w)
            w += ins[t][1]
        if L < len(base):
            w.append(base[L])
    return w, tops
