"""Shared, standard-library machinery for TRIPLE-PRODUCT-20261026-001 (written fresh for this epic).

G = UT3(F4) x| <h>, h: (x, y, z) -> (w^2 x, w^2 y, w z). F4 = {0, 1, 2, 3} with 2 = w, 3 = w^2 = w + 1 (addition is XOR).
A knot is the closure of a braid word (generator i > 0: strand at position i-1 crosses over position i; i < 0: under).
M = S^3_3(K) is given by the Wirtinger relators but one and mu^3 lambda (preferred longitude).
For psi with psi(meridian) = 1:
  V   = H^1(M; F4 twisted by w^2), as an F2 basis H of cocycle vectors (2 bits per generator) modulo coboundaries;
  B   = the obstruction bimap V x V -> coker(delta_1) on A-cochains, B(a, b) = [c_a u c_b];
  N   = #{(a, b) : B(a, b) = 0}, so |Hom(pi1 M, G)| = 1 + 128 4^d N when H1(M) = Z/3 (proof.md).
"""
import itertools

# ---------------------------------------------------------------- F4
def fmul(p, q):
    if p == 0 or q == 0:
        return 0
    lg = {1: 0, 2: 1, 3: 2}
    return (1, 2, 3)[(lg[p] + lg[q]) % 3]

W, W2 = 2, 3
FINV = {1: 1, 2: 3, 3: 2}
TR = {0: 0, 1: 0, 2: 1, 3: 1}          # absolute trace F4 -> F2
FROB = {0: 0, 1: 1, 2: 3, 3: 2}        # x -> x^2


def det3(u, v, x):
    """determinant of the 3x3 matrix with rows u, v, x over F4 (characteristic 2: the permanent)"""
    t = 0
    for i, j, k in itertools.permutations(range(3)):
        t ^= fmul(fmul(u[i], v[j]), x[k])
    return t


# ---------------------------------------------------------------- the group
POW = {0: (1, 1, 1), 1: (W2, W2, W), 2: (W, W, W2)}   # alpha^e acting on (x, y, z)


def alpha(e, n):
    a, b, c = POW[e % 3]
    return (fmul(a, n[0]), fmul(b, n[1]), fmul(c, n[2]))


def gmul(g1, g2):
    (x, y, z, e), (u, v, w, f) = g1, g2
    u2, v2, w2 = alpha(e, (u, v, w))
    return (x ^ u2, y ^ v2, z ^ w2 ^ fmul(x, v2), (e + f) % 3)


ELEMS = [(x, y, z, e) for x in range(4) for y in range(4) for z in range(4) for e in range(3)]
ONE = (0, 0, 0, 0)


def ginv(g):
    for k in ELEMS:
        if gmul(g, k) == ONE:
            return k
    raise AssertionError


INV = {g: ginv(g) for g in ELEMS}


def word_value(word, images):
    """word: list of (generator, exponent); images: list of group elements"""
    out = ONE
    for g, s in word:
        x = images[g] if s > 0 else INV[images[g]]
        for _ in range(abs(s)):
            out = gmul(out, x)
    return out


def frobenius_aut(g):
    """(n, h^e) -> (Frobenius(n), h^(2e)); an automorphism of G (checked in check.py)"""
    x, y, z, e = g
    return (FROB[x], FROB[y], FROB[z], (2 * e) % 3)


# ---------------------------------------------------------------- braid closures and surgery presentations
def presentation(word, n, p=3):
    """Closure of the braid `word` on n strands, which must be a knot. Returns (U, rels, arc_at) where arc_at[(L, q)] is the
    generator of the arc at position q just above crossing L. Relators: x_o^-s x_i x_o^s x_j^-1 (all crossings but the last),
    and mu^p lambda with lambda = prod of x_o^s along the traversal from the start of arc 0, times mu^-writhe."""
    m = len(word)
    arc_at, q, cur, visits = {}, 0, 0, []
    for _ in range(n):
        for L, g in enumerate(word):
            arc_at[(L, q)] = cur
            i = abs(g) - 1
            if q in (i, i + 1):
                left = q == i
                over = (left and g > 0) or (not left and g < 0)
                visits.append((L, over, 1 if g > 0 else -1, cur))
                if not over:
                    cur += 1
                q = i + 1 if left else i
        if q == 0 and len(arc_at) == n * m:
            break
    assert len(arc_at) == n * m and q == 0 and cur == m, "closure is not a knot"
    U = m
    arc_at = {k: v % U for k, v in arc_at.items()}
    over_arc = {L: a % U for L, ov, s, a in visits if ov}
    cr = [(over_arc[L], a % U, (a + 1) % U, s) for L, ov, s, a in visits if not ov]
    rels = [[(o, -s), (i, 1), (o, s), (j, -1)] for o, i, j, s in cr[:-1]]
    w = sum(s for *_, s in cr)
    lam = [(o, s) for o, i, j, s in cr] + ([(0, -1)] * w if w >= 0 else [(0, 1)] * (-w))
    rels.append(([(0, 1)] * p if p >= 0 else [(0, -1)] * (-p)) + lam)
    return U, rels, arc_at


def smith_invariants(U, rels):
    """invariant factors of H1 (abelianized relator matrix over Z), as a sorted list (0 = free summand)"""
    M = [[sum(s for g, s in r if g == j) for j in range(U)] for r in rels]
    inv = []
    while M and M[0]:
        nz = [(abs(M[i][j]), i, j) for i in range(len(M)) for j in range(len(M[0])) if M[i][j]]
        if not nz:
            break
        _, i, j = min(nz)
        M[0], M[i] = M[i], M[0]
        for row in M:
            row[0], row[j] = row[j], row[0]
        done = False
        while not done:
            done = True
            p = M[0][0]
            for i in range(1, len(M)):
                if M[i][0]:
                    f = M[i][0] // p
                    M[i] = [a - f * b for a, b in zip(M[i], M[0])]
                    if M[i][0]:
                        done = False
            for j in range(1, len(M[0])):
                if M[0][j]:
                    f = M[0][j] // p
                    for row in M:
                        row[j] -= f * row[0]
                    if M[0][j]:
                        done = False
            if not done:
                nz = [(abs(M[i][j]), i, j) for i in range(len(M)) for j in range(len(M[0])) if (i == 0 or j == 0) and M[i][j]]
                _, i, j = min(nz)
                M[0], M[i] = M[i], M[0]
                for row in M:
                    row[0], row[j] = row[j], row[0]
            elif any(M[i][j] % p for i in range(1, len(M)) for j in range(1, len(M[0]))):
                i, j = next((i, j) for i in range(1, len(M)) for j in range(1, len(M[0])) if M[i][j] % p)
                M[0] = [a + b for a, b in zip(M[0], M[i])]
                done = False
        inv.append(abs(M[0][0]))
        M = [row[1:] for row in M[1:]]
    zeros = (U - len(inv))
    return sorted([d for d in inv if d != 1] + [0] * zeros)


# ---------------------------------------------------------------- F2 linear algebra on int bitmasks
def reduce_into(basis, x):
    """basis: dict pivot -> vector (pivot = highest bit). Fully reduces x (no pivot bit left set): the canonical remainder."""
    for p in sorted(basis, reverse=True):
        if x >> p & 1:
            x ^= basis[p]
    return x


def span_add(basis, x):
    r = reduce_into(basis, x)
    if r:
        basis[r.bit_length() - 1] = r
        return True
    return False


def nullspace(rows, n):
    """basis (bitmasks over n variables) of {x : popcount(row & x) even for every row}"""
    piv = {}
    for r in rows:
        x = r
        for p in sorted(piv, reverse=True):
            if x >> p & 1:
                x ^= piv[p]
        if x:
            p = x.bit_length() - 1
            for q in list(piv):
                if piv[q] >> p & 1:
                    piv[q] ^= x
            piv[p] = x
    free = [j for j in range(n) if j not in piv]
    out = []
    for f in free:
        v = 1 << f
        for p, r in piv.items():
            if r >> f & 1:
                v |= 1 << p
        out.append(v)
    return out


def kernel_dim(rows):
    """dimension of {beta : xor of rows[b] over beta = 0}, i.e. len(rows) - rank"""
    basis = {}
    return len(rows) - sum(span_add(basis, r) for r in rows)


def kernel_space(rows):
    """canonical (fully reduced) basis, as a frozenset, of {beta : xor of rows[b] over beta = 0}"""
    piv, kern = {}, []
    for b, r in enumerate(rows):
        x, tag = r, 1 << b
        while x:
            hb = x.bit_length() - 1
            if hb in piv:
                px, pt = piv[hb]
                x ^= px
                tag ^= pt
            else:
                piv[hb] = (x, tag)
                break
        if not x:
            kern.append(tag)
    basis = {}
    for v in kern:
        span_add(basis, v)
    keys = sorted(basis)
    for k in keys:
        for k2 in keys:
            if k2 != k and basis[k2] >> k & 1:
                basis[k2] ^= basis[k]
    return frozenset(basis.values())


# ---------------------------------------------------------------- twisted cocycles and the obstruction bimap
def _vals(bits, U):
    return [(bits >> (2 * g) & 1) | ((bits >> (2 * g + 1) & 1) << 1) for g in range(U)]


def _relator_parts(U, rels, psi, cx, cy, az=None):
    imgs = [(cx[g], cy[g], az[g] if az else 0, psi[g] % 3) for g in range(U)]
    out = []
    for r in rels:
        X, Y, Z, e = word_value(r, imgs)
        assert e == 0
        out.append((X, Y, Z))
    return out


def _pack(values):
    """list of F4 values -> bitmask with 2 bits per entry"""
    v = 0
    for t, x in enumerate(values):
        v |= x << (2 * t)
    return v


def obstruction_data(U, rels, psi=None):
    """F2 basis H of V (cocycle bitmasks, 2 bits per generator, complementing the coboundaries), the bimap B[(i, j)] as
    bitmasks in coker(delta_1) coordinates (reduced against the A-coboundary image), and the image basis."""
    psi = psi or [1] * U
    zero = [0] * U
    R = len(rels)
    # cocycle conditions: X-parts of relators with cy = 0 (linear in cx), as rows over the 2U bits of cx
    cols = []
    for b in range(2 * U):
        cx = _vals(1 << b, U)
        cols.append(_pack([X for X, Y, Z in _relator_parts(U, rels, psi, cx, zero)]))
    rows = []
    for t in range(2 * R):
        rows.append(sum(((cols[b] >> t) & 1) << b for b in range(2 * U)))
    Z1 = nullspace(rows, 2 * U)
    # the same conditions hold for y-cocycles (same module); check on the basis
    for z in Z1:
        assert all(Y == 0 for X, Y, Z in _relator_parts(U, rels, psi, zero, _vals(z, U)))
    # coboundaries: g -> (psi(g) - 1) v = w v for psi(g) = 1, constant over generators
    cob = []
    for v in (1, 2):
        cob.append(_pack([fmul(W, v) if psi[g] % 3 == 1 else (fmul(W2, v) if psi[g] % 3 == 2 else 0) for g in range(U)]))
    zb = {}
    for z in Z1:
        span_add(zb, z)
    for c in cob:
        assert reduce_into(zb, c) == 0, "coboundary is not a cocycle"
    cb = {}
    for c in cob:
        span_add(cb, c)
    H = []
    for z in Z1:
        if span_add(cb, z):
            H.append(z)
    # A-coboundary image in the relator Z-space
    img = {}
    for g in range(U):
        for t in (1, 2):
            az = [0] * U
            az[g] = t
            span_add(img, _pack([Z for X, Y, Z in _relator_parts(U, rels, psi, zero, zero, az)]))
    def obs(a, b):
        return reduce_into(img, _pack([Z for X, Y, Z in _relator_parts(U, rels, psi, _vals(a, U), _vals(b, U))]))
    Bm = {(i, j): obs(H[i], H[j]) for i in range(len(H)) for j in range(len(H))}
    # bilinearity spot check
    if len(H) >= 2:
        assert obs(H[0] ^ H[1], H[0]) == Bm[(0, 0)] ^ Bm[(1, 0)]
    return H, Bm, img


def kernel_count(H, Bm):
    """N = #{(a, b) in V x V : B(a, b) = 0} by a Gray-code sweep over a"""
    d2 = len(H)
    R = [[Bm[(i, b)] for b in range(d2)] for i in range(d2)]
    cur, N, prev = [0] * d2, 0, 0
    for step in range(1 << d2):
        g = step ^ (step >> 1)
        if step:
            i = (g ^ prev).bit_length() - 1
            cur = [x ^ y for x, y in zip(cur, R[i])]
        prev = g
        N += 1 << kernel_dim(cur)
    return N


def count_formula(word, n):
    """(d, N, 1 + 128 4^d N, H1 invariants) for M = S^3_3(closure of word)"""
    U, rels, _ = presentation(word, n, 3)
    H, Bm, _ = obstruction_data(U, rels)
    N = kernel_count(H, Bm)
    d = len(H) // 2
    return d, N, 1 + 128 * 4 ** d * N, smith_invariants(U, rels)


# ---------------------------------------------------------------- brute force (braids on at most 3 strands)
def conj_class(g):
    return sorted({gmul(gmul(k, g), INV[k]) for k in ELEMS})


def brute_count(word, n, p=3):
    """|Hom(pi1 S^3_p(K), G)| by enumerating images of the top arcs (all meridians are conjugate) and propagating them
    through the braid; checks closure and every relator."""
    U, rels, arc = presentation(word, n, p)
    total = 0
    for g0 in ELEMS:
        cls = conj_class(g0)
        for rest in itertools.product(cls, repeat=n - 1):
            top = [g0, *rest]
            cur = list(top)
            img = [None] * U
            ok = True
            for L, g in enumerate(word):
                for q in range(n):
                    a = arc[(L, q)]
                    if img[a] is None:
                        img[a] = cur[q]
                    elif img[a] != cur[q]:
                        ok = False
                        break
                if not ok:
                    break
                i = abs(g) - 1
                a, b = cur[i], cur[i + 1]
                if g > 0:
                    cur[i], cur[i + 1] = gmul(gmul(INV[a], b), a), a
                else:
                    cur[i], cur[i + 1] = b, gmul(gmul(b, a), INV[b])
            if not ok or cur != top:
                continue
            if all(word_value(r, img) == ONE for r in rels):
                total += 1
    return total


# ---------------------------------------------------------------- recovering T from B (Poincare duality makes B a contraction of T)
def _coords_solver(vectors):
    """returns f(x) -> bitmask of coefficients expressing x in span(vectors) (None if not in the span)"""
    piv = {}
    for idx, v in enumerate(vectors):
        x, tag = v, 1 << idx
        while x:
            hb = x.bit_length() - 1
            if hb in piv:
                px, pt = piv[hb]
                x ^= px
                tag ^= pt
            else:
                piv[hb] = (x, tag)
                break
    def solve(x):
        tag = 0
        while x:
            hb = x.bit_length() - 1
            if hb not in piv:
                return None
            px, pt = piv[hb]
            x ^= px
            tag ^= pt
        return tag
    return solve


def omega_matrix(H, U, psi=None):
    """Om[i] = coordinates (bitmask over H) of w * H[i], modulo coboundaries"""
    psi = psi or [1] * U
    cob = [_pack([fmul(W, v) if psi[g] % 3 == 1 else fmul(W2, v) for g in range(U)]) for v in (1, 2)]
    solve = _coords_solver(H + cob)
    full = (1 << len(H)) - 1
    out = []
    for h in H:
        tag = solve(_pack([fmul(W, x) for x in _vals(h, U)]))
        assert tag is not None
        out.append(tag & full)
    return out


def recover_trace_form(H, Bm, U):
    """All F2-linear phi: W -> V* with t(a, b, c) = phi(B(a, b))(c) symmetric and F4-balanced (t(wa, b, c) = t(a, b, wc)).
    Returns (solution basis, t_of(sol), w, injective(sol)). The true Poincare pairing is one injective solution."""
    d2 = len(H)
    wb = {}
    for v in Bm.values():
        span_add(wb, v)
    Wb = list(wb.values())
    w = len(Wb)
    solve = _coords_solver(Wb)
    C = {k: solve(v) for k, v in Bm.items()}
    Om = omega_matrix(H, U)
    nv = w * d2
    def lin(i, j, cmask):
        s = 0
        for r in range(w):
            if C[(i, j)] >> r & 1:
                for k in range(d2):
                    if cmask >> k & 1:
                        s ^= 1 << (r * d2 + k)
        return s
    rows = []
    for i in range(d2):
        for j in range(d2):
            for k in range(d2):
                if j < k:
                    rows.append(lin(i, j, 1 << k) ^ lin(i, k, 1 << j))
                if i < j:
                    rows.append(lin(i, j, 1 << k) ^ lin(j, i, 1 << k))
                rhs = 0
                for i2 in range(d2):
                    if Om[i] >> i2 & 1:
                        rhs ^= lin(i2, j, 1 << k)
                rows.append(lin(i, j, Om[k]) ^ rhs)
    sols = nullspace(rows, nv)
    def t_of(sol):
        t = [[[0] * d2 for _ in range(d2)] for _ in range(d2)]
        for i in range(d2):
            for j in range(d2):
                for k in range(d2):
                    s = 0
                    for r in range(w):
                        if C[(i, j)] >> r & 1:
                            s ^= sol >> (r * d2 + k) & 1
                    t[i][j][k] = s
        return t
    def injective(sol):
        basis = {}
        return sum(span_add(basis, sum((sol >> (r * d2 + k) & 1) << k for k in range(d2))) for r in range(w)) == w
    return sols, t_of, w, injective, Om


def injective_solution(sols, injective):
    for co in range(1, 1 << len(sols)):
        s = 0
        for b in range(len(sols)):
            if co >> b & 1:
                s ^= sols[b]
        if injective(s):
            return s
    return None


def trace_form_rows(t):
    """P[i][b] = bitmask over c of t(h_i, h_b, h_c)"""
    d2 = len(t)
    return [[sum(t[i][b][c] << c for c in range(d2)) for b in range(d2)] for i in range(d2)]


def count_from_rows(P):
    """#{(a, b) : t(a, b, .) = 0} by a Gray-code sweep; P as from trace_form_rows"""
    return kernel_count(list(range(len(P))), {(i, b): P[i][b] for i in range(len(P)) for b in range(len(P))})


def cubic_character_sum(t):
    """|V|^-1 sum over a, b, c in V of (-1)^{t(a, b, c)} (explicit triple sum; for small V)"""
    d2 = len(t)
    P = trace_form_rows(t)
    s = 0
    for a in range(1 << d2):
        rows = [0] * d2
        for i in range(d2):
            if a >> i & 1:
                rows = [x ^ y for x, y in zip(rows, P[i])]
        for b in range(1 << d2):
            f = 0
            for j in range(d2):
                if b >> j & 1:
                    f ^= rows[j]
            for c in range(1 << d2):
                s += -1 if bin(f & c).count("1") & 1 else 1
    assert s % (1 << d2) == 0
    return s >> d2


# ---------------------------------------------------------------- leaves, Borromean insertions, predictions
BORROMEAN = [1, -2] * 3          # its closure is the Borromean rings; a pure braid


def fat(i, k, sign):
    """k-cabled crossing of fat strands i, i + 1 (1-based), as thin generators"""
    base = (i - 1) * k
    w = [base + k + r - 1 - t for r in range(1, k + 1) for t in range(k)]
    return w if sign > 0 else [-x for x in reversed(w)]


def cable(word3, k, offset=0):
    out = []
    for g in word3:
        out += [(abs(x) + offset) * (1 if x > 0 else -1) for x in fat(abs(g), k, 1 if g > 0 else -1)]
    return out


def fig8_sum(k):
    """connected sum of k figure-eight knots, on 2k + 1 strands"""
    return [x for i in range(k) for x in (2 * i + 1, -(2 * i + 2), 2 * i + 1, -(2 * i + 2))]


def insert_at(base, ins):
    """ins: list of (level, offset). Inserts the 3-cabled Borromean braid on thin positions offset..offset+8 just above
    base[level]; returns the new word and the level, in the new word, of each insertion's top (input order). Insertions at
    the same level are placed in input order (corrected in the reissue: the closed version mislabelled tops in that case)."""
    order = sorted(range(len(ins)), key=lambda i: (ins[i][0], i))
    w, tops, j = [], [None] * len(ins), 0
    for L in range(len(base) + 1):
        while j < len(order) and ins[order[j]][0] == L:
            tops[order[j]] = len(w)
            w += cable(BORROMEAN, 3, offset=ins[order[j]][1])
            j += 1
        if L < len(base):
            w.append(base[L])
    return w, tops


def window(o):
    return tuple((o + 3 * j, o + 3 * j + 1, o + 3 * j + 2) for j in range(3))


def leaf_values(H, U, arc, L, positions):
    """values on the basis H of the functional a -> c_a(x_{p_k} ... x_{p_1}) for the loop around the strands at the given
    positions of level L (the right-to-left product, which the Wirtinger relators preserve across crossings)"""
    out = []
    for h in H:
        v = _vals(h, U)
        s, f = 0, 1
        for q in reversed(positions):      # rightmost first
            s ^= fmul(f, v[arc[(L, q)]])
            f = fmul(f, W2)
        out.append(s)
    return out


def predicted_rows(H, leafsets, extra=None):
    """P[i][b] = bitmask over c of tr( sum_e det(l_e(h_i), l_e(h_b), l_e(h_c)) ) (+ extra[i][b])"""
    d2 = len(H)
    P = []
    for i in range(d2):
        row = []
        for b in range(d2):
            r = 0
            for c in range(d2):
                t = 0
                for lam in leafsets:
                    t ^= det3([x[i] for x in lam], [x[b] for x in lam], [x[c] for x in lam])
                r |= TR[t] << c
            if extra:
                r ^= extra[i][b]
            row.append(r)
        P.append(row)
    return P


def compare_kernels(Bm, P):
    """for every a in V: the kernel of b -> B(a, b) against the kernel of b -> t(a, b, .) from P; returns (N, #mismatching a)"""
    d2 = len(P)
    R = [[Bm[(i, b)] for b in range(d2)] for i in range(d2)]
    ca, cp, N, bad, prev = [0] * d2, [0] * d2, 0, 0, 0
    for step in range(1 << d2):
        g = step ^ (step >> 1)
        if step:
            i = (g ^ prev).bit_length() - 1
            ca = [x ^ y for x, y in zip(ca, R[i])]
            cp = [x ^ y for x, y in zip(cp, P[i])]
        prev = g
        ka = kernel_space(ca)
        N += 1 << len(ka)
        bad += kernel_space(cp) != ka
    return N, bad
