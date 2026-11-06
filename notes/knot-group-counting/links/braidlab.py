"""Braid-closure tools for counting homomorphisms from link groups to S3.

Conventions
-----------
A braid on n strands is a list of nonzero ints: +i is sigma_i, -i is sigma_i^{-1}
(1-indexed, sigma_i acts on 0-indexed positions i-1, i).
Right Hurwitz action on labels (Wirtinger colourings of the closure):
    sigma_i     : (a, b) -> (a b a^-1, a)      left strand passes OVER, moves right
    sigma_i^-1  : (a, b) -> (b, b^-1 a b)      right strand passes OVER, moves left
Hom(pi_1(S^3 - closure), G) is in bijection with the fixed points of beta on G^n.
Crossing sign convention: sign(sigma_i) = +1, sign(sigma_i^-1) = -1 (used consistently
for writhe, linking numbers and framing corrections).

S3 = F3 x| F2: the element (x, s) is the affine map z -> (-1)^s z + x of F3.
Transpositions are (x, 1); 3-cycles are (x, 0) with x != 0.
"""
import itertools
import numpy as np

# ---------------------------------------------------------------- S3 as (x, s)
ELTS = [(x, s) for s in (0, 1) for x in range(3)]
IDX = {g: i for i, g in enumerate(ELTS)}
E = (0, 0)


def mul(g, h):
    x1, s1 = g
    x2, s2 = h
    return ((x1 + (x2 if s1 == 0 else -x2)) % 3, (s1 + s2) % 2)


def inv(g):
    x, s = g
    return ((-x if s == 0 else x) % 3, s)


def conj(o, t):
    return mul(mul(o, t), inv(o))


def cent_size(g):
    return sum(1 for h in ELTS if mul(g, h) == mul(h, g))


CENT = {g: cent_size(g) for g in ELTS}
MUL = np.array([[IDX[mul(a, b)] for b in ELTS] for a in ELTS], dtype=np.int64)
INV = np.array([IDX[inv(a)] for a in ELTS], dtype=np.int64)


def power(g, k):
    r = E
    if k < 0:
        g, k = inv(g), -k
    for _ in range(k):
        r = mul(r, g)
    return r

# ---------------------------------------------------------------- braid basics


def perm_of(word, n):
    """pos[p] = bottom position of the strand that starts at top position p."""
    order = list(range(n))  # order[q] = strand id currently at position q
    for g in word:
        i = abs(g) - 1
        order[i], order[i + 1] = order[i + 1], order[i]
    bottom = [None] * n
    for q, sid in enumerate(order):
        bottom[sid] = q
    return bottom


def components(word, n):
    """List of components, each a list of strand ids (= top positions) in traversal order."""
    bottom = perm_of(word, n)
    seen, comps = set(), []
    for p in range(n):
        if p in seen:
            continue
        c, q = [], p
        while q not in seen:
            seen.add(q)
            c.append(q)
            q = bottom[q]  # closure: bottom position q -> top position q (strand q)
        comps.append(c)
    return comps


def comp_index(word, n):
    comps = components(word, n)
    ci = [None] * n
    for k, c in enumerate(comps):
        for p in c:
            ci[p] = k
    return comps, ci


def crossings(word, n):
    """Yield (step, gen, left_id, right_id, over_id, under_id, sign)."""
    order = list(range(n))
    out = []
    for t, g in enumerate(word):
        i = abs(g) - 1
        a, b = order[i], order[i + 1]
        if g > 0:
            over, under, sgn = a, b, +1
        else:
            over, under, sgn = b, a, -1
        out.append((t, g, a, b, over, under, sgn))
        order[i], order[i + 1] = b, a
    return out


def linking_and_writhe(word, n):
    comps, ci = comp_index(word, n)
    c = len(comps)
    tot = np.zeros((c, c), dtype=np.int64)
    for (_, _, a, b, _, _, sgn) in crossings(word, n):
        tot[ci[a], ci[b]] += sgn
        if ci[a] != ci[b]:
            tot[ci[b], ci[a]] += sgn
    lk = np.zeros((c, c), dtype=np.int64)
    w = [0] * c
    for i in range(c):
        w[i] = int(tot[i, i])
        for j in range(c):
            if i != j:
                assert tot[i, j] % 2 == 0
                lk[i, j] = tot[i, j] // 2
    return comps, lk, w

# ---------------------------------------------------------------- brute force


def fixed_points(word, n):
    """All fixed points of the Hurwitz action on S3^n (as an int array of shape (F, n))."""
    tup = np.array(list(itertools.product(range(6), repeat=n)), dtype=np.int64)
    cur = tup.copy()
    for g in word:
        i = abs(g) - 1
        a, b = cur[:, i].copy(), cur[:, i + 1].copy()
        if g > 0:
            cur[:, i] = MUL[MUL[a, b], INV[a]]
            cur[:, i + 1] = a
        else:
            cur[:, i] = b
            cur[:, i + 1] = MUL[MUL[INV[b], a], b]
    ok = np.all(cur == tup, axis=1)
    return tup[ok]


def count_brute(word, n):
    return len(fixed_points(word, n))


def longitudes(word, n, labels):
    """For one fixed point (tuple of S3 elements indexed by top position), return for each
    component (in components() order) the pair (meridian, blackboard longitude P_total),
    where the label of the component's first strand is conjugated by P_total after one
    full traversal: P_total m P_total^-1 = m."""
    order = list(range(n))
    cur = list(labels)
    P = [E] * n  # partial conjugator per strand id
    for g in word:
        i = abs(g) - 1
        a, b = cur[i], cur[i + 1]
        sa, sb = order[i], order[i + 1]
        if g > 0:
            cur[i], cur[i + 1] = conj(a, b), a
            P[sb] = mul(a, P[sb])
        else:
            cur[i], cur[i + 1] = b, conj(inv(b), a)
            P[sa] = mul(inv(b), P[sa])
        order[i], order[i + 1] = sb, sa
    assert tuple(cur) == tuple(labels), "not a fixed point"
    out = []
    for c in components(word, n):
        tot = E
        for p in c:  # traversal order: strand p, then strand bottom[p], ...
            tot = mul(P[p], tot)
        m = labels[c[0]]
        assert conj(tot, m) == m
        out.append((m, tot))
    return out

# ---------------------------------------------------------------- linear algebra mod 3


def rank_mod3(M):
    A = np.array(M, dtype=np.int64) % 3
    if A.size == 0:
        return 0
    r = 0
    rows, cols = A.shape
    for c in range(cols):
        piv = None
        for i in range(r, rows):
            if A[i, c] != 0:
                piv = i
                break
        if piv is None:
            continue
        A[[r, piv]] = A[[piv, r]]
        A[r] = (A[r] * (1 if A[r, c] == 1 else 2)) % 3
        nz = np.nonzero(A[:, c])[0]
        for i in nz:
            if i != r:
                A[i] = (A[i] - A[i, c] * A[r]) % 3
        r += 1
        if r == rows:
            break
    return r


def nullspace_mod3(M):
    """Basis (list of vectors) of {x : M x = 0} over F3."""
    A = np.array(M, dtype=np.int64) % 3
    rows, cols = A.shape
    piv_cols, r = [], 0
    for c in range(cols):
        piv = None
        for i in range(r, rows):
            if A[i, c] != 0:
                piv = i
                break
        if piv is None:
            continue
        A[[r, piv]] = A[[piv, r]]
        A[r] = (A[r] * (1 if A[r, c] == 1 else 2)) % 3
        for i in range(rows):
            if i != r and A[i, c] != 0:
                A[i] = (A[i] - A[i, c] * A[r]) % 3
        piv_cols.append(c)
        r += 1
        if r == rows:
            break
    free = [c for c in range(cols) if c not in piv_cols]
    basis = []
    for f in free:
        v = np.zeros(cols, dtype=np.int64)
        v[f] = 1
        for k, pc in enumerate(piv_cols):
            v[pc] = (-A[k, f]) % 3
        basis.append(v)
    return basis

# ---------------------------------------------------------------- sign-sector (psi) method


def sector_matrix(word, n, signs):
    """signs[p] in {0,1} for each top position (must be constant on components).
    Returns M (n x n over F3) with: final x-vector = M @ initial x-vector."""
    vec = [np.eye(n, dtype=np.int64)[p] for p in range(n)]
    sg = list(signs)
    for g in word:
        i = abs(g) - 1
        va, sa = vec[i], sg[i]
        vb, sb = vec[i + 1], sg[i + 1]
        if g > 0:
            # new_i = a b a^-1 : x = (-1)^{sa} xb + (1-(-1)^{sb}) xa, sign sb
            nx = ((vb if sa == 0 else -vb) + (0 if sb == 0 else 2) * va) % 3
            vec[i], sg[i] = nx, sb
            vec[i + 1], sg[i + 1] = va, sa
        else:
            # new_{i+1} = b^-1 a b : o = b^-1 = (-(-1)^{sb} xb, sb)
            xo = (-vb if sb == 0 else vb) % 3
            nx = ((va if sb == 0 else -va) + (0 if sa == 0 else 2) * xo) % 3
            vec[i], sg[i] = vb, sb
            vec[i + 1], sg[i + 1] = nx, sa
    assert sg == list(signs)
    return np.array(vec, dtype=np.int64) % 3


def sector_count(word, n, signs):
    M = sector_matrix(word, n, signs)
    return 3 ** (n - rank_mod3((M - np.eye(n, dtype=np.int64)) % 3))


def count_psi(word, n, return_sectors=False):
    comps, ci = comp_index(word, n)
    c = len(comps)
    tot, sectors = 0, {}
    for psi in itertools.product((0, 1), repeat=c):
        signs = [psi[ci[p]] for p in range(n)]
        t = sector_count(word, n, signs)
        sectors[psi] = t
        tot += t
    return (tot, sectors) if return_sectors else tot

# ---------------------------------------------------------------- constructions


def A_gen(i, j):
    """Pure braid generator A_{ij} for 0-indexed positions i < j (strand j winds once
    around strand i; linking +1 in our sign convention)."""
    assert i < j
    w = []
    for k in range(j - 1, i, -1):
        w.append(k + 1)          # sigma_{k+1} acts on positions k, k+1
    w += [i + 1, i + 1]
    for k in range(i + 1, j):
        w.append(-(k + 1))
    return w


def sub_braid(word, n, keep):
    """Braid on the strands whose ids are in `keep` (deleting the other components)."""
    keep = set(keep)
    order = list(range(n))
    out = []
    for g in word:
        i = abs(g) - 1
        a, b = order[i], order[i + 1]
        if a in keep and b in keep:
            pos = sum(1 for q in range(i) if order[q] in keep)
            out.append((pos + 1) * (1 if g > 0 else -1))
        order[i], order[i + 1] = b, a
    ids = sorted(keep)
    return out, len(ids)


def bundle_crossing(P, a, b, positive):
    """Expanded braid for a bundle of width a (at expanded positions P..P+a-1) crossing a
    bundle of width b immediately to its right; the left bundle moves right, passing over
    (positive) or under (negative)."""
    w = []
    for r in range(a - 1, -1, -1):
        for t in range(b):
            gen = P + r + t + 1      # acts on positions P+r+t, P+r+t+1
            w.append(gen if positive else -gen)
    return w


def full_twist(Q, k, times):
    """`times` full twists on k strands at expanded positions Q..Q+k-1."""
    base = []
    for _ in range(k):
        base += [Q + r + 1 for r in range(k - 1)]
    if times >= 0:
        return base * times
    return [-g for g in reversed(base)] * (-times)


def cable(word, n, ncopies, framing=None):
    """Replace each strand of component c by ncopies[c] parallel strands (blackboard
    parallel), then add full twists so that the copies of component c have pairwise
    linking number framing[c] (default 0 = Seifert framing).
    Returns (new_word, new_n, copies) where copies[c] = list of new strand ids."""
    comps, ci = comp_index(word, n)
    _, lk, wr = linking_and_writhe(word, n)
    if framing is None:
        framing = [0] * len(comps)
    width = [ncopies[ci[p]] for p in range(n)]
    order = list(range(n))
    out = []
    for g in word:
        i = abs(g) - 1
        a, b = order[i], order[i + 1]
        P = sum(width[order[q]] for q in range(i))
        out += bundle_crossing(P, width[a], width[b], g > 0)
        order[i], order[i + 1] = b, a
    # framing correction at the bottom
    for c, comp in enumerate(comps):
        k = ncopies[c]
        if k <= 1:
            continue
        t = framing[c] - wr[c]
        p = comp[0]
        q = order.index(p)
        Q = sum(width[order[r]] for r in range(q))
        out += full_twist(Q, k, t)
    N = sum(width)
    return out, N


def tie_trefoil(word, n, strand_id, twists=3):
    """Connected sum of the component containing `strand_id` with T(2,twists) (twists odd).
    Returns (new_word, n+1)."""
    order = list(range(n))
    for g in word:
        i = abs(g) - 1
        order[i], order[i + 1] = order[i + 1], order[i]
    q = order.index(strand_id)
    gamma = [k + 1 for k in range(q, n - 1)]  # moves bottom position q to n-1
    new = [-g for g in reversed(gamma)] + list(word) + gamma
    new += [n] * twists                        # sigma_n acts on positions n-1, n
    return new, n + 1


def tie_trefoil_tracked(word, n, strand_id, twists=3):
    """Like tie_trefoil, but also returns idmap: old top id -> new top id (the extra strand
    has id n and lies in the same component as strand_id)."""
    order = list(range(n))
    for g in word:
        i = abs(g) - 1
        order[i], order[i + 1] = order[i + 1], order[i]
    q = order.index(strand_id)
    # the bottom position of strand_id is q; conjugate by gamma = s_{q+1} ... s_{n-1}
    gamma = [k + 1 for k in range(q, n - 1)]
    new = [-g for g in reversed(gamma)] + list(word) + gamma + [n] * twists
    # new top position of old strand s: perm_gamma(s)
    def pg(s):
        if s < q:
            return s
        if s == q:
            return n - 1
        return s - 1
    idmap = {s: pg(s) for s in range(n)}
    return new, n + 1, idmap


def tie_trefoils(word, n, reps, j, twists=3):
    """Tie j trefoils into each component represented by strand ids in reps (list).
    Returns (word, n, new_reps)."""
    reps = list(reps)
    for idx in range(len(reps)):
        for _ in range(j):
            word, n2, idmap = tie_trefoil_tracked(word, n, reps[idx], twists)
            reps = [idmap[r] for r in reps]
            n = n2
    return word, n, reps
