"""css.py: values and changes both readable (README.md, part B). For a parity structure (knots as lists of distinction
names, every law even), the allowed words S are the assignments every knot's law allows; the allowed changes are the
sets whose flip keeps every law, which under even parity are S itself. A value read of a set z of distinctions is the
parity of their values (the literature's Z^z); a change read of a set x asks whether flipping x is allowed, comparing two
words (X^x). The coherent counting state weights every allowed word equally and relates every two of them equally (the
literature's equal superposition over S, the stabiliser state with value reads S-perp and change reads S); its value
reads alone give the counts.

For two readers holding sets A and B of distinctions (the rest is the middle), the number of shared pairs of
anticommuting certainties between them, e (the literature's count of ebits of a stabiliser state, Fattal and others,
2004): the rank over GF(2) of the pairing x|A . z|A between the change reads x and value reads z of the state's
certainties on A + B. With e = 0 the two readers' joint table has a list of values; e >= 1 is needed for any excess, and
e >= 2 admits the literature's two-reader game of certainty (Mermin and Peres's square) with value, change and product
reads. Three ways the middle is treated:
    unread       certainties supported on A + B only
    changes      a middle reader reads every middle distinction's change; the certainties' value parts must avoid the
                 middle, their change parts are cut to A + B (the middle's record sets the signs)
    values       a middle reader reads every middle value; the change parts must avoid the middle"""
import itertools


def index(knots):
    names = sorted({d for k in knots for d in k}, key=str)
    return names, {d: i for i, d in enumerate(names)}


def rowspace(vecs):
    piv = {}
    for v in vecs:
        while v:
            h = v.bit_length() - 1
            if h in piv: v ^= piv[h]
            else: piv[h] = v; break
    return list(piv.values())


def kernel(rows, m):
    """vectors x of m bits with x . r = 0 for every r in rows"""
    R = rowspace(rows)
    # reduced row echelon
    R.sort(key=lambda r: -r.bit_length())
    piv = {}
    for r in R:
        h = r.bit_length() - 1
        for p in list(piv):
            if piv[p] >> h & 1: piv[p] ^= r
        piv[h] = r
    for h in list(piv):
        for p in list(piv):
            if p != h and piv[p] >> h & 1: piv[p] ^= piv[h]
    free = [j for j in range(m) if j not in piv]
    out = []
    for f in free:
        x = 1 << f
        for h, r in piv.items():
            if r >> f & 1: x |= 1 << h
        out.append(x)
    return out


def subspace_within(basis, mask, m):
    """the vectors of span(basis) supported inside mask"""
    out = ~mask & ((1 << m) - 1)
    # solve: combinations whose bits outside mask vanish
    rows = [(b & out, 1 << i) for i, b in enumerate(basis)]
    piv = {}; ker = []
    for x, tag in rows:
        while x:
            h = x.bit_length() - 1
            if h in piv: x ^= piv[h][0]; tag ^= piv[h][1]
            else: piv[h] = (x, tag); break
        if not x: ker.append(tag)
    res = []
    for tag in ker:
        v = 0
        for i, b in enumerate(basis):
            if tag >> i & 1: v ^= b
        res.append(v)
    return rowspace(res)


def rank(vecs):
    return len(rowspace(vecs))


def pairing_rank(X, Z, A):
    """rank of the matrix (x|A . z|A) over GF(2)"""
    rows = []
    for x in X:
        r = 0
        for j, z in enumerate(Z):
            r |= ((x & z & A).bit_count() & 1) << j
        rows.append(r)
    return rank(rows)


def state(knots):
    names, idx = index(knots); m = len(names)
    assert all(len(set(k)) == len(k) for k in knots), 'a knot lists each distinction once'
    stars = [sum(1 << idx[d] for d in k) for k in knots]
    Zs = rowspace(stars)                     # value certainties: the span of the knots' laws
    Xs = kernel(stars, m)                    # change certainties: the allowed changes
    assert len(Zs) + len(Xs) == m
    assert all((x & z).bit_count() % 2 == 0 for x in Xs for z in Zs)
    return names, idx, m, Xs, Zs


def ebits(knots, A, B, middle='unread'):
    names, idx, m, Xs, Zs = state(knots)
    a = sum(1 << idx[d] for d in A); b = sum(1 << idx[d] for d in B); ab = a | b
    if middle == 'unread':
        X = subspace_within(Xs, ab, m); Z = subspace_within(Zs, ab, m)
    elif middle == 'changes':
        X = rowspace([x & ab for x in Xs]); Z = subspace_within(Zs, ab, m)
    elif middle == 'values':
        X = subspace_within(Xs, ab, m); Z = rowspace([z & ab for z in Zs])
    else:                                   # a set of middle distinctions read for changes, the rest unread
        c = sum(1 << idx[d] for d in middle)
        X = rowspace([x & ab for x in subspace_within(Xs, ab | c, m)]); Z = subspace_within(Zs, ab, m)
    return pairing_rank(X, Z, a)


def identities(knots, A, B):
    """the advisor's identities, an independent route: e(changes) = dim of the value laws on A + B less those on A and on
    B (the readers' value correlation in bits); e(values) the same with the allowed changes"""
    names, idx, m, Xs, Zs = state(knots)
    a = sum(1 << idx[d] for d in A); b = sum(1 << idx[d] for d in B)
    d = lambda basis, mask: len(subspace_within(basis, mask, m))
    return {'changes': d(Zs, a | b) - d(Zs, a) - d(Zs, b), 'values': d(Xs, a | b) - d(Xs, a) - d(Xs, b)}


def square(knots, A, B):
    """with the middle read for changes and two shared pairs (e >= 2): the literature's two-reader game of certainty
    (Mermin and Peres's square) built from the readers' own value, change and combined reads. Returns the nine cells'
    A-side reads (as change part, value part), whether each cell's A-read times its B partner is a certainty of the
    sorted state, whether every row's and column's A-reads commute, and the row and column product signs."""
    names, idx, m, Xs, Zs = state(knots)
    a = sum(1 << idx[d] for d in A); b = sum(1 << idx[d] for d in B); ab = a | b
    X = rowspace([x & ab for x in Xs]); Z = subspace_within(Zs, ab, m)
    # two cross pairs with pairing on A the identity
    # symplectic Gram-Schmidt on the pairing x|A . z|A: two pairs with x_i . z_j = delta_ij
    pair = lambda x, z: (x & z & a).bit_count() & 1
    Xl, Zl = list(X), list(Z); xs, zs = [], []
    while len(xs) < 2:
        hit = next(((i, j) for i, x in enumerate(Xl) for j, z in enumerate(Zl) if pair(x, z)), None)
        if hit is None: return None
        x, z = Xl.pop(hit[0]), Zl.pop(hit[1])
        Xl = [y ^ x if pair(y, z) else y for y in Xl]      # clear the rest against the chosen pair
        Zl = [w ^ z if pair(x, w) else w for w in Zl]
        xs.append(x); zs.append(z)
    X1, X2 = xs; Z1, Z2 = zs
    cells = [[(X1, 0), (X2, 0), (X1 ^ X2, 0)],
             [(0, Z2), (0, Z1), (0, Z1 ^ Z2)],
             [(X1, Z2), (X2, Z1), (X1 ^ X2, Z1 ^ Z2)]]
    Xspan = rowspace(X); Zspan = rowspace(Z)
    def inspan(v, basis):
        for bvec in sorted(basis, key=lambda q: -q.bit_length()):
            if v >> (bvec.bit_length() - 1) & 1: v ^= bvec
        return v == 0
    certain = [[inspan(x, Xspan) and inspan(z, Zspan) for (x, z) in row] for row in cells]
    def comm(p, q): return ((p[0] & q[1] & a).bit_count() + (p[1] & q[0] & a).bit_count()) % 2 == 0
    lines = [row for row in cells] + [[cells[r][c] for r in range(3)] for c in range(3)]
    commuting = all(comm(p, q) for L in lines for p, q in itertools.combinations(L, 2))
    return {'cells certain': sum(sum(r) for r in certain), 'rows and columns commute on A': commuting}


def separated(knots, A, B):
    A, B = set(A), set(B)
    return not any(set(k) & A and set(k) & B for k in knots)
