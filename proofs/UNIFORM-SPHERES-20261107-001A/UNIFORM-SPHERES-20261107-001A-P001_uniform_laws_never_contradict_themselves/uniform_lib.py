"""Uniform knot laws and the surfaces they build, for UNIFORM-SPHERES-20261107-001A.

A law of lines and co-lines: points, lines (triples) and co-lines (cyclic sequences of points), such that each pair of consecutive
points of a line (a corner) lies, as a consecutive pair, in exactly one co-line, and each point's link alternates lines and co-lines in one
cycle. Points, corners, lines and co-lines are then the vertices, edges and faces of a closed surface: nothing is drawn. The knot is the
signed not-all-equal constraint on the lines; the co-lines are the faces whose agreements COUNT-SURFACES-20261107-001A counts.

The Cayley law C(G; x, y) of a finite group G and elements x, y (w = (xy)^-1): points G; lines {g, gx, gxy}; co-lines the cosets
g<x>, g<y>, g<w> in their cyclic order. Around a point the link is: line {g, gx, gxy}, coset g<x>, line {gx^-1, g, gy}, coset g<y>,
line {gy^-1x^-1, gy^-1, g}, coset g<w>. In the triangulation T of COUNT-SURFACES-20261107-001A, point g is an up triangle whose side k
meets the line l_k(g) = L(g), L(gx^-1), L(gy^-1x^-1); line L(h) = (h, hx, hxy) is a down triangle whose side k meets its k-th point; and
side k of L(h) is glued to side k of its k-th point with the identity map on corners. Corner c of a triangle lies in the co-line of its
type: corners 0, 1, 2 of every triangle are of types y, w, x. Every point has co-line sizes (|x|, |y|, |w|)."""
import itertools
import math
import random
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "proofs/COUNT-SURFACES-20261107-001A/COUNT-SURFACES-20261107-001A-P001_the_count_reads_the_euler_characteristic"))
import surface_lib as L  # noqa: E402


# ------------------------------------------------------------------------------------------------ permutation groups
def compose(p, q):
    """(p q)(i) = p(q(i)): apply q first; we write group products left to right as in the law, so g*h := compose(h, g)"""
    return tuple(p[i] for i in q)


def mul(g, h):
    """the product gh, acting as g then h on the right: (gh)(i) = h(g(i))"""
    return tuple(h[i] for i in g)


def inv(p):
    r = [0] * len(p)
    for i, j in enumerate(p):
        r[j] = i
    return tuple(r)


def order(p):
    e = tuple(range(len(p)))
    q, k = p, 1
    while q != e:
        q, k = mul(q, p), k + 1
    return k


def closure(gens):
    e = tuple(range(len(gens[0])))
    seen, frontier = {e}, [e]
    while frontier:
        nxt = []
        for g in frontier:
            for s in gens:
                h = mul(g, s)
                if h not in seen:
                    seen.add(h)
                    nxt.append(h)
        frontier = nxt
    return sorted(seen)


def perm(cycles, n):
    p = list(range(n))
    for cyc in cycles:
        for a, b in zip(cyc, cyc[1:] + cyc[:1]):
            p[a] = b
    return tuple(p)


# ------------------------------------------------------------------------------------------------ the Cayley law
def cayley_law(x, y, name=""):
    """the Surface of C(G; x, y), G = <x, y>"""
    G = closure([x, y])
    idx = {g: i for i, g in enumerate(G)}
    n = len(G)
    xi, yi = inv(x), inv(y)
    # triangle ids: point g -> idx[g]; line L(h) -> n + idx[h]
    colour = [0] * n + [1] * n
    side, cmap = [None] * (2 * n), [None] * (2 * n)
    ident = [{c: c for c in range(3) if c != k} for k in range(3)]
    for g in G:
        lk = [g, mul(g, xi), mul(mul(g, yi), xi)]           # l_0, l_1, l_2 (lines named by their first point)
        side[idx[g]] = [(n + idx[h], k) for k, h in enumerate(lk)]
        cmap[idx[g]] = [dict(ident[k]) for k in range(3)]
        pts = [g, mul(g, x), mul(mul(g, x), y)]             # L(g) = (g, gx, gxy)
        side[n + idx[g]] = [(idx[p], k) for k, p in enumerate(pts)]
        cmap[n + idx[g]] = [dict(ident[k]) for k in range(3)]
    S = L.Surface(name or f"C(G; x, y), |G| = {n}", colour, side, cmap)
    S.group, S.idx, S.x, S.y = G, idx, x, y
    S.type = (order(x), order(y), order(inv(mul(x, y))))
    return S


def uniform_signing(KS, sigma):
    """the same sign pattern sigma = (s0, s1, s2) on the three sides of every line"""
    return [sigma[k] for i in range(KS.n) for k in range(3)]


def point_types(KS):
    """for each point, the sorted sizes of the three co-lines (faces) at its corners"""
    S = KS.S
    out = Counter()
    for t in KS.points:
        out[tuple(sorted(KS.d[S.vert[t][c]] for c in range(3)))] += 1
    return out


def spherical_types(dmax=60):
    """all (d1 <= d2 <= d3), d >= 2, with 1/d1 + 1/d2 + 1/d3 > 1, and n = 2 / (sum - 1)"""
    from fractions import Fraction
    out = []
    for d1 in range(2, dmax + 1):
        for d2 in range(d1, dmax + 1):
            for d3 in range(d2, dmax + 1):
                s = Fraction(1, d1) + Fraction(1, d2) + Fraction(1, d3)
                if s > 1:
                    out.append(((d1, d2, d3), 2 / (s - 1)))
    return out


# ------------------------------------------------------------------------------------------------ groups used
def dihedral(d):
    """D_d on d points: x = reflection i -> -i, y = reflection i -> 1 - i, xy a rotation of order d"""
    x = tuple((-i) % d for i in range(d))
    y = tuple((1 - i) % d for i in range(d))
    return x, y


def find_pair(G, a, b, c, rng=None, tries=200000):
    """x of order a, y of order b in the group G (a list of permutations) with xy of order c generating G"""
    by_order = {}
    for g in G:
        by_order.setdefault(order(g), []).append(g)
    X, Y = by_order.get(a, []), by_order.get(b, [])
    pairs = itertools.product(X, Y) if len(X) * len(Y) <= tries else (
        (rng.choice(X), rng.choice(Y)) for _ in range(tries))
    for x, y in pairs:
        if order(mul(x, y)) == c and len(closure([x, y])) == len(G):
            return x, y
    return None


def symmetric(m):
    return closure([perm([[0, 1]], m), perm([list(range(m))], m)])


def alternating(m):
    return [g for g in symmetric(m) if parity(g) == 0]


def parity(p):
    seen, par = set(), 0
    for i in range(len(p)):
        if i in seen:
            continue
        j, ln = i, 0
        while j not in seen:
            seen.add(j)
            j, ln = p[j], ln + 1
        par ^= (ln - 1) & 1
    return par


def gl32():
    """GL(3, 2) = PSL(2, 7) as permutations of the 7 nonzero vectors of F2^3"""
    vecs = [v for v in itertools.product((0, 1), repeat=3) if any(v)]
    vid = {v: i for i, v in enumerate(vecs)}
    out = []
    for rows in itertools.product(vecs, repeat=3):
        M = [list(r) for r in rows]
        det = (M[0][0] * (M[1][1] * M[2][2] + M[1][2] * M[2][1]) + M[0][1] * (M[1][0] * M[2][2] + M[1][2] * M[2][0])
               + M[0][2] * (M[1][0] * M[2][1] + M[1][1] * M[2][0])) % 2
        if det:
            out.append(tuple(vid[tuple(sum(M[r][c] * v[c] for c in range(3)) % 2 for r in range(3))] for v in vecs))
    return sorted(set(out))


def affine(k, linear, shift):
    """the permutation v -> linear v + shift of Z_k^2 (points indexed a*k + b)"""
    out = []
    for a in range(k):
        for b in range(k):
            u = ((linear[0][0] * a + linear[0][1] * b + shift[0]) % k, (linear[1][0] * a + linear[1][1] * b + shift[1]) % k)
            out.append(u[0] * k + u[1])
    return tuple(out)


def wallpaper_pair(kind, k):
    """generators of rotation-group quotients acting on Z_k^2: (3,3,3) two 120-degree rotations; (2,4,4) a half turn and a quarter turn;
    (2,3,6) a half turn and a 120-degree rotation (hexagonal coordinates)"""
    R3 = [[0, -1], [1, -1]]          # 120 degrees on the hexagonal lattice
    R4 = [[0, -1], [1, 0]]           # 90 degrees on the square lattice
    R2 = [[-1, 0], [0, -1]]
    if kind == (3, 3, 3):
        return affine(k, R3, (0, 0)), affine(k, R3, (1, 0))
    if kind == (2, 4, 4):
        return affine(k, R2, (1, 0)), affine(k, R4, (0, 0))
    if kind == (2, 3, 6):
        return affine(k, R2, (1, 0)), affine(k, R3, (0, 0))
    raise ValueError(kind)


# ------------------------------------------------------------------------------------------------ cyclic chains (the antiprism laws)
def dihedral_blocks(S, d):
    """for C(D_d; x, y): the points g grouped into blocks by the rotation part g(0) (the image of 0), a cyclic order of size d"""
    return {S.idx[g]: g[0] for g in S.group}


def chain_width(KS, block):
    """the largest cyclic span (in blocks) of a line's points; block maps point index -> block index"""
    nb = len(set(block.values()))
    w = 0
    for i in range(KS.n):
        bs = {block[KS.pt[i][k]] for k in range(3)}
        w = max(w, min(max((b - s0) % nb for b in bs) for s0 in bs))
    return w


def antiprism_blocks(S):
    """for C(D_d; x, y): the rotation i -> i + j goes to block j and the reflection i -> j - i to block -j; every line then holds two
    consecutive blocks (a cyclic chain of width 1)"""
    d = len(S.group[0])
    out = {}
    for g in S.group:
        rot = (g[1] - g[0]) % d == 1 % d
        out[S.idx[g]] = g[0] % d if rot else (-g[0]) % d
    return out, d


def find_violated_chain(KS, s, x, block, nb):
    """binary search on a cyclic chain of width 1: returns (a violated line, the queried points). Invariant: an arc of blocks [a, b] whose
    lines (those inside it) cannot all hold given the values on blocks a and b."""
    members = {}
    for p, bl in block.items():
        members.setdefault(bl, []).append(p)
    line_at = {}
    for i in range(KS.n):
        bs = sorted({block[KS.pt[i][k]] for k in range(3)})
        if len(bs) == 1:
            c = bs[0]
        else:
            u, v = bs
            c = u if (v - u) % nb == 1 else v
            assert (bs[0] - c) % nb in (0, 1) and (bs[1] - c) % nb in (0, 1)
        line_at.setdefault(c % nb, []).append(i)
    queried = {}

    def ask(bl):
        for p in members[bl % nb]:
            queried[p] = x[p]

    def holds(i, val):
        lit = [val[KS.pt[i][k]] ^ s[3 * i + k] for k in range(3)]
        return not (lit[0] == lit[1] == lit[2])

    def arc_ok(a, b, fixed):
        """is there an assignment of blocks a..b, with blocks a and b as given, satisfying the lines inside?"""
        def states(bl):
            ps = members[bl % nb]
            if bl in fixed:
                return [fixed[bl]]
            return [dict(zip(ps, v)) for v in itertools.product((0, 1), repeat=len(ps))]
        cur = [st for st in states(a)]
        for bl in range(a, b):
            nxt = []
            for st in states(bl + 1):
                if any(all(holds(i, {**c, **st}) for i in line_at.get(bl % nb, [])) for c in cur):
                    nxt.append(st)
            cur = nxt
            if not cur:
                return False
        return True

    ask(0)
    fixed = {0: {p: x[p] for p in members[0]}, nb: {p: x[p] for p in members[0]}}
    a, b = 0, nb
    assert not arc_ok(a, b, fixed)
    while b - a > 2:
        m = (a + b) // 2
        ask(m)
        fixed[m] = {p: x[p] for p in members[m % nb]}
        if not arc_ok(a, m, fixed):
            b = m
        else:
            assert not arc_ok(m, b, fixed)
            a = m
    for bl in range(a, b + 1):
        ask(bl)
    for bl in range(a, b):
        for i in line_at.get(bl % nb, []):
            if not holds(i, x):
                return i, queried
    return None, queried
