"""Heisenberg groups over F_p with a diagonal coprime C_r action, on knot surgeries S^3_r(K) (standard library only).

G = H(F_p) x| <h>, H(F_p) = {(x, y, z)} with (x, y, z)(u, v, t) = (x + u, y + v, z + t + x v); h acts by (x, y, z) -> (a x, b y, a b z),
where a, b are r-th roots of unity in F_p (r | p - 1, p odd). Knots are braid closures; M = S^3_r(K) has H1 = Z/r.
"""
import itertools


class Field:
    def __init__(self, p):
        self.p = p

    def inv(self, x):
        return pow(x % self.p, self.p - 2, self.p)


def rref(rows, p):
    """reduced row echelon form mod p; returns (rows, pivot columns)"""
    rows = [[x % p for x in r] for r in rows]
    piv, rk = [], 0
    ncol = len(rows[0]) if rows else 0
    for c in range(ncol):
        k = next((i for i in range(rk, len(rows)) if rows[i][c]), None)
        if k is None:
            continue
        rows[rk], rows[k] = rows[k], rows[rk]
        iv = pow(rows[rk][c], p - 2, p)
        rows[rk] = [x * iv % p for x in rows[rk]]
        for i in range(len(rows)):
            if i != rk and rows[i][c]:
                f = rows[i][c]
                rows[i] = [(x - f * y) % p for x, y in zip(rows[i], rows[rk])]
        piv.append(c)
        rk += 1
    return rows[:rk], piv


def rank(rows, p):
    return len(rref(rows, p)[0]) if rows else 0


def nullspace(rows, n, p):
    """basis of {x in F_p^n : row . x = 0 for all rows}"""
    if not rows:
        return [[int(i == j) for j in range(n)] for i in range(n)]
    R, piv = rref(rows, p)
    free = [j for j in range(n) if j not in piv]
    out = []
    for f in free:
        v = [0] * n
        v[f] = 1
        for r, c in zip(R, piv):
            v[c] = (-r[f]) % p
        out.append(v)
    return out


class Reducer:
    """canonical reduction of vectors modulo the span of given vectors (mod p)"""
    def __init__(self, vectors, p, n):
        self.p, self.n = p, n
        self.R, self.piv = rref(vectors, p) if vectors else ([], [])

    def reduce(self, v):
        v = [x % self.p for x in v]
        for r, c in zip(self.R, self.piv):
            if v[c]:
                f = v[c]
                v = [(x - f * y) % self.p for x, y in zip(v, r)]
        return tuple(v)


# ---------------------------------------------------------------- the group
class Group:
    def __init__(self, p, r, a, b):
        assert (p - 1) % r == 0 and pow(a, r, p) == 1 and pow(b, r, p) == 1
        self.p, self.r, self.a, self.b = p, r, a % p, b % p
        self.ap = [pow(a, e, p) for e in range(r)]
        self.bp = [pow(b, e, p) for e in range(r)]
        self.abp = [pow(a * b, e, p) for e in range(r)]

    def mul(self, g1, g2):
        (x, y, z, e), (u, v, t, f) = g1, g2
        p = self.p
        u2, v2, t2 = self.ap[e] * u % p, self.bp[e] * v % p, self.abp[e] * t % p
        return ((x + u2) % p, (y + v2) % p, (z + t2 + x * v2) % p, (e + f) % self.r)

    def inv(self, g):
        x, y, z, e = g
        p, r = self.p, self.r
        n = ((-x) % p, (-y) % p, (-z + x * y) % p)
        e2 = (-e) % r
        return (self.ap[e2] * n[0] % p, self.bp[e2] * n[1] % p, self.abp[e2] * n[2] % p, e2)

    def elements(self):
        p, r = self.p, self.r
        return [(x, y, z, e) for x in range(p) for y in range(p) for z in range(p) for e in range(r)]

    def word(self, w, images):
        out = (0, 0, 0, 0)
        for g, s in w:
            x = images[g] if s > 0 else self.inv(images[g])
            for _ in range(abs(s)):
                out = self.mul(out, x)
        return out


# ---------------------------------------------------------------- braids and presentations
def presentation(word, n, p_surg):
    """closure of `word` on n strands (a knot): (U, rels, arc_at) with relators x_o^-s x_i x_o^s x_j^-1 (all crossings but the
    last) and mu^p lambda (Seifert longitude); arc_at[(L, q)] = generator of the arc at position q just above crossing L"""
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
    rels.append(([(0, 1)] * p_surg if p_surg >= 0 else [(0, -1)] * (-p_surg)) + lam)
    return U, rels, arc_at


def fat(i, k, sign):
    base = (i - 1) * k
    w = [base + k + r - 1 - t for r in range(1, k + 1) for t in range(k)]
    return w if sign > 0 else [-x for x in reversed(w)]


def cable(word3, k, offset=0):
    out = []
    for g in word3:
        out += [(abs(x) + offset) * (1 if x > 0 else -1) for x in fat(abs(g), k, 1 if g > 0 else -1)]
    return out


BORROMEAN = [1, -2] * 3


def connected_sum(words):
    """connected sum of braid closures given as (word, strands); summand i shares its first strand with the previous last"""
    out, off = [], 0
    for w, n in words:
        out += [(abs(x) + off) * (1 if x > 0 else -1) for x in w]
        off += n - 1
    return out, off + 1


def insert_at(base, ins, k):
    """ins: list of (level, offset); inserts the k-cabled Borromean braid before base[level]; returns word, tops"""
    blen = len(cable(BORROMEAN, k))
    order = sorted(range(len(ins)), key=lambda i: ins[i][0])
    tops, shift = [None] * len(ins), 0
    for i in order:
        tops[i] = ins[i][0] + shift
        shift += blen
    w = list(base)
    for i in sorted(order, key=lambda i: -ins[i][0]):
        L, o = ins[i]
        w = w[:L] + cable(BORROMEAN, k, offset=o) + w[L:]
    return w, tops


# ---------------------------------------------------------------- twisted cohomology by Fox calculus
def fox_rows(U, rels, zeta, k, p):
    """row per relator: coefficients of c(g) in c(relator), for the character g -> zeta^(k psi) with psi = 1 on meridians"""
    act = pow(zeta, k, p)
    inv_act = pow(act, p - 2, p)
    rows = []
    for rel in rels:
        row, pref = [0] * U, 1
        for g, s in rel:
            for _ in range(abs(s)):
                if s > 0:
                    row[g] = (row[g] + pref) % p
                    pref = pref * act % p
                else:
                    pref = pref * inv_act % p
                    row[g] = (row[g] - pref) % p
        rows.append(row)
    return rows


def cohomology(U, rels, zeta, k, p):
    """(H1 basis as cocycle vectors complementing coboundaries, dim Z1, dim B1) for F_p twisted by zeta^(k psi)"""
    Z = nullspace(fox_rows(U, rels, zeta, k, p), U, p)
    act = pow(zeta, k, p)
    B = [[(act - 1) % p] * U] if act != 1 else []
    basis = [b for b in B if any(b)]
    H = []
    for z in Z:
        if rank(basis + [z], p) > len(basis):
            basis.append(z)
            H.append(z)
    return H, len(Z), len(B)


def obstruction(G, U, rels, k=1):
    """Heisenberg obstruction over psi_k: bases Hx (char a^k), Hy (char b^k) and canonical classes Bm[(i, j)] of the relator
    z-cochain modulo the coboundary image (char (ab)^k)"""
    p = G.p
    Hx, zx, bx = cohomology(U, rels, G.a, k, p)
    Hy, zy, by = cohomology(U, rels, G.b, k, p)
    Dz = fox_rows(U, rels, G.a * G.b % p, k, p)          # relators x generators
    cols = [[Dz[i][g] for i in range(len(rels))] for g in range(U)]
    red = Reducer(cols, p, len(rels))
    def zvec(av, bv):
        imgs = [(av[g], bv[g], 0, k % G.r) for g in range(U)]
        out = []
        for rel in rels:
            X, Y, Zc, e = G.word(rel, imgs)
            assert X == 0 and Y == 0 and e == 0
            out.append(Zc)
        return red.reduce(out)
    Bm = {(i, j): zvec(Hx[i], Hy[j]) for i in range(len(Hx)) for j in range(len(Hy))}
    return Hx, Hy, Bm, (zx, bx, zy, by)


def kernel_counts(Hx, Hy, Bm, p):
    """N = #{(a, b) : B(a, b) = 0} and the kernel subspace (canonical rref rows) for every a in span(Hx)"""
    dx, dy = len(Hx), len(Hy)
    N, kers = 0, {}
    for a in itertools.product(range(p), repeat=dx):
        rows = []
        for j in range(dy):
            v = None
            for i in range(dx):
                if a[i]:
                    w = Bm[(i, j)]
                    v = [(x + a[i] * y) % p for x, y in zip(v, w)] if v else [a[i] * y % p for y in w]
            rows.append(v if v else [0] * len(Bm[(0, 0)]) if Bm else [])
        # kernel of b -> sum_j b_j rows[j]
        cols = [[rows[j][t] for j in range(dy)] for t in range(len(rows[0]))] if rows and rows[0] else []
        K = nullspace(cols, dy, p) if cols else [[int(i == j) for j in range(dy)] for i in range(dy)]
        kers[a] = tuple(map(tuple, rref(K, p)[0])) if K else ()
        N += p ** len(K)
    return N, kers


def hom_count(G, word, n, surg=None):
    """|Hom(pi1 S^3_s(K), G)| (s = surg, default r) from the formula: sum over psi_k of |Z1(A)| |B1_x| |B1_y| N_k"""
    U, rels, _ = presentation(word, n, surg or G.r)
    p, total, parts = G.p, 0, {}
    for k in range(G.r):
        Hx, Hy, Bm, (zx, bx, zy, by) = obstruction(G, U, rels, k)
        _, zz, _ = cohomology(U, rels, G.a * G.b % p, k, p)
        N, _ = kernel_counts(Hx, Hy, Bm, p)
        c = p ** zz * p ** bx * p ** by * N
        parts[k] = (len(Hx), len(Hy), N, c)
        total += c
    return total, parts


def brute_count(G, word, n, surg=None, knot_group=False):
    """|Hom| by enumeration (all meridians conjugate; orbit reduction over conjugacy classes of the first top arc);
    knot_group=True drops the surgery relator (counts maps of the knot group)"""
    U, rels, arc = presentation(word, n, surg or G.r)
    if knot_group:
        rels = rels[:-1]
    E = G.elements()
    seen, reps = set(), []
    for g in E:
        if g in seen:
            continue
        cls = {G.mul(G.mul(h, g), G.inv(h)) for h in E}
        seen |= cls
        reps.append((g, sorted(cls)))
    total = 0
    for g0, cls in reps:
        cnt = 0
        for rest in itertools.product(cls, repeat=n - 1):
            top = [g0, *rest]
            cur, img, ok = list(top), [None] * U, True
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
                x, y = cur[i], cur[i + 1]
                if g > 0:
                    cur[i], cur[i + 1] = G.mul(G.mul(G.inv(x), y), x), x
                else:
                    cur[i], cur[i + 1] = y, G.mul(G.mul(y, x), G.inv(y))
            if ok and cur == top and all(G.word(r, img) == (0, 0, 0, 0) for r in rels):
                cnt += 1
        total += cnt * len(cls)
    return total


def leaf(H, arc, L, positions, zeta, p):
    """values on the basis H of a -> c_a(x_{p_last} ... x_{p_first}) (right-to-left product of the bundle's arcs)"""
    out = []
    for h in H:
        s, f = 0, 1
        for q in reversed(positions):
            s = (s + f * h[arc[(L, q)]]) % p
            f = f * zeta % p
        out.append(s)
    return out


# ---------------------------------------------------------------- steering: predicted trilinear form from Borromean leaves
PERMS = [((0, 1, 2), 1), ((1, 2, 0), 1), ((2, 0, 1), 1), ((0, 2, 1), -1), ((2, 1, 0), -1), ((1, 0, 2), -1)]


def leaf_sets(G, H3, arc, tops, offsets, k):
    """for each insertion: leaf functionals on (Hx, Hy, Hg) for its three bundles of k strands"""
    p = G.p
    gam = pow(G.a * G.b % p, p - 2, p)
    chars = (G.a, G.b, gam)
    out = []
    for L, o in zip(tops, offsets):
        bundles = [list(range(o + k * j, o + k * j + k)) for j in range(3)]
        out.append([[leaf(H3[t], arc, L, bq, chars[t], p) for bq in bundles] for t in range(3)])
    return out


def predicted_kernels(G, H3, leaves, coef=1):
    """for every a: the left kernel (canonical rref) of b -> T(a, b, .) with T = coef * sum over insertions of
    sum_sigma sgn(sigma) l_{sigma1}(a) m_{sigma2}(b) n_{sigma3}(c)"""
    p = G.p
    Hx, Hy, Hg = H3
    dx, dy, dg = len(Hx), len(Hy), len(Hg)
    kers = {}
    for a in itertools.product(range(p), repeat=dx):
        # lam values at a for each insertion and leaf
        la = [[sum(a[i] * ins[0][j][i] for i in range(dx)) % p for j in range(3)] for ins in leaves]
        M = [[0] * dg for _ in range(dy)]
        for ins, lv in zip(leaves, la):
            for (s1, s2, s3), sg in PERMS:
                if lv[s1] == 0:
                    continue
                for b in range(dy):
                    mb = ins[1][s2][b]
                    if mb:
                        f = coef * sg * lv[s1] * mb % p
                        for c in range(dg):
                            nc = ins[2][s3][c]
                            if nc:
                                M[b][c] = (M[b][c] + f * nc) % p
        cols = [[M[b][c] for b in range(dy)] for c in range(dg)]
        K = nullspace(cols, dy, p) if dg else [[int(i == j) for j in range(dy)] for i in range(dy)]
        kers[a] = tuple(map(tuple, rref(K, p)[0])) if K else ()
    return kers


def steer_test(G, word, n, ins, k, coefs=(1,)):
    """insert k-cabled Borromean braids at ins = [(level, offset)]; compare actual obstruction kernels with predictions"""
    p = G.p
    w, tops = insert_at(word, ins, k)
    U, rels, arc = presentation(w, n, G.r)
    Hx, Hy, Bm, _ = obstruction(G, U, rels, 1)
    gam = pow(G.a * G.b % p, p - 2, p)
    Hg, _, _ = cohomology(U, rels, gam, 1, p)
    leaves = leaf_sets(G, (Hx, Hy, Hg), arc, tops, [o for _, o in ins], k)
    N, act = kernel_counts(Hx, Hy, Bm, p)
    res = {}
    for c in coefs:
        pred = predicted_kernels(G, (Hx, Hy, Hg), leaves, c)
        res[c] = sum(1 for a in act if act[a] != pred[a])
    return dict(U=U, dims=(len(Hx), len(Hy), len(Hg)), N=N, mismatches=res)


def knot_group_count(G, word, n):
    """|Hom(pi1(S^3 - K), G)| by the same formula on the knot group (Wirtinger relators but one, no surgery relator)"""
    U, rels, _ = presentation(word, n, G.r)
    rels = rels[:-1]
    p, total = G.p, 0
    for k in range(G.r):
        Hx, Hy, Bm, (zx, bx, zy, by) = obstruction(G, U, rels, k)
        _, zz, _ = cohomology(U, rels, G.a * G.b % p, k, p)
        N, _ = kernel_counts(Hx, Hy, Bm, p)
        total += p ** zz * p ** bx * p ** by * N
    return total
