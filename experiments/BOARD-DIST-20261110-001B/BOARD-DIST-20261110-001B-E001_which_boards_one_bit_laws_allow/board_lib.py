"""Boards made of identity distinctions (BOARD-DIST-20261110-001B).

Names are the reduced words in x, y and their inverses X, Y. A board is a right congruence on the
names (u ~ v gives ug ~ vg for every letter g), equivalently a subgroup H of the free group F2: its
places are the cosets Hu and its x- and y-steps make the Schreier graph of H. A finite board is a
transitive pair (sx, sy) of permutations of range(n).

A one-bit value law reads a place and its four neighbours as a pattern
    p = c + 2*x + 4*X + 8*y + 16*Y,
bit 0 the place's value and bits 1 to 4 the values of its x-, X-, y- and Y-neighbours. A law is the
set of patterns it allows, held as a 32-bit mask.
"""
import itertools

X_, XI, Y_, YI = 0, 1, 2, 3          # letter indices: x, X = x^-1, y, Y = y^-1
LETTERS = 'xXyY'
INV = (1, 0, 3, 2)


def centre(p):
    return p & 1


def nb(p, g):
    """The value a pattern gives to the g-neighbour."""
    return (p >> (g + 1)) & 1


def pattern(c, vx, vX, vy, vY):
    return c | (vx << 1) | (vX << 2) | (vy << 3) | (vY << 4)


def patterns_of(L):
    return [p for p in range(32) if (L >> p) & 1]


# ----------------------------------------------------------------------------------------------
# The law family
# ----------------------------------------------------------------------------------------------

def lifelike_mask(m10):
    """Life-like law m10: bit 5*c + k set when a place of value c with k neighbours of value 1 is allowed."""
    L = 0
    for p in range(32):
        c, k = p & 1, bin(p >> 1).count('1')
        if (m10 >> (5 * c + k)) & 1:
            L |= 1 << p
    return L


PARITY0 = sum(1 << (5 * c + k) for c in (0, 1) for k in range(5) if (c + k) % 2 == 0)
PARITY1 = sum(1 << (5 * c + k) for c in (0, 1) for k in range(5) if (c + k) % 2 == 1)


def atom_mask():
    """The atom x, y -> c: a place's value is 1 whenever its x- and y-neighbours' values are both 1."""
    L = 0
    for p in range(32):
        if not (nb(p, X_) and nb(p, Y_)) or centre(p):
            L |= 1 << p
    return L


def law_family():
    """The frozen family: the 1,024 Life-like laws (key 'L<m10>') and the atom (key 'atom')."""
    fam = [('L%d' % m, lifelike_mask(m)) for m in range(1024)]
    fam.append(('atom', atom_mask()))
    return fam


# ----------------------------------------------------------------------------------------------
# Finite boards
# ----------------------------------------------------------------------------------------------

def _inverse(s):
    inv = [0] * len(s)
    for i, j in enumerate(s):
        inv[j] = i
    return inv


def canon(sx, sy):
    """Canonical relabelling of a transitive pair, or None if it is not transitive.

    For each start place, label places in breadth-first order over the letters x, X, y, Y; keep the
    lexicographically least code. Returns (code, sx', sy') with sx', sy' the relabelled pair.
    """
    n = len(sx)
    gens = (sx, _inverse(sx), sy, _inverse(sy))
    best = None
    for s0 in range(n):
        lab = {s0: 0}
        order = [s0]
        k = 0
        while k < len(order):
            v = order[k]
            k += 1
            for g in gens:
                w = g[v]
                if w not in lab:
                    lab[w] = len(order)
                    order.append(w)
        if len(order) < n:
            return None
        nx = tuple(lab[sx[v]] for v in order)
        ny = tuple(lab[sy[v]] for v in order)
        code = nx + ny
        if best is None or code < best[0]:
            best = (code, nx, ny)
    return best


def _partitions(n, maxpart=None):
    if maxpart is None:
        maxpart = n
    if n == 0:
        yield ()
        return
    for k in range(min(n, maxpart), 0, -1):
        for rest in _partitions(n - k, k):
            yield (k,) + rest


def _perm_of_type(parts):
    perm, start = [], 0
    for k in parts:
        perm.extend(range(start + 1, start + k))
        perm.append(start)
        start += k
    return tuple(perm)


def finite_boards(n):
    """All connected boards with n places up to isomorphism: list of (sx, sy) in canonical labelling."""
    seen = {}
    for parts in _partitions(n):
        sx = _perm_of_type(parts)
        for sy in itertools.permutations(range(n)):
            c = canon(sx, sy)
            if c is not None and c[0] not in seen:
                seen[c[0]] = (c[1], c[2])
    return [seen[k] for k in sorted(seen)]


def is_abelian(sx, sy):
    return all(sx[sy[v]] == sy[sx[v]] for v in range(len(sx)))


def covers(big, small):
    """Whether the finite board `big` covers `small`: a letter-preserving map of places exists."""
    bx, by = big
    sx, sy = small
    n, m = len(bx), len(sx)
    if n % m:
        return False
    bgen = (bx, _inverse(bx), by, _inverse(by))
    sgen = (sx, _inverse(sx), sy, _inverse(sy))
    for f0 in range(m):
        f = {0: f0}
        stack = [0]
        ok = True
        while stack and ok:
            v = stack.pop()
            for g in range(4):
                w, fw = bgen[g][v], sgen[g][f[v]]
                if w in f:
                    if f[w] != fw:
                        ok = False
                        break
                else:
                    f[w] = fw
                    stack.append(w)
        if ok:
            return True
    return False


def torus(a, b, d):
    """The torus Z^2 / <(a, 0), (b, d)> (Hermite normal form, 0 <= b < a) as a finite board."""
    def red(i, j):
        k = j // d
        return ((i - k * b) % a, j - k * d)
    places = [(i, j) for j in range(d) for i in range(a)]
    idx = {p: t for t, p in enumerate(places)}
    sx = tuple(idx[red(i + 1, j)] for (i, j) in places)
    sy = tuple(idx[red(i, j + 1)] for (i, j) in places)
    return sx, sy


def tori(nmax):
    """Every torus Z^2 / Lambda of index at most nmax, one per lattice in Hermite normal form."""
    out = []
    for N in range(1, nmax + 1):
        for a in range(1, N + 1):
            if N % a == 0:
                d = N // a
                for b in range(a):
                    out.append(((a, b, d), torus(a, b, d)))
    return out


def line_quotient_of(board, a, b):
    """Whether an abelian finite board is a quotient of the line Sch(ker phi), phi(x) = a, phi(y) = b:
    x^(-b) y^a acts trivially."""
    sx, sy = board
    if not is_abelian(sx, sy):
        return False
    n = len(sx)
    six, siy = _inverse(sx), _inverse(sy)

    def power(s, si, e, v):
        for _ in range(abs(e)):
            v = s[v] if e > 0 else si[v]
        return v
    return all(power(sy, siy, a, power(sx, six, -b, v)) == v for v in range(n))


def board_patterns(board):
    """For a finite board: the bit matrix of all 2^n colourings and each colouring's set of patterns as
    a 32-bit mask (numpy arrays)."""
    import numpy as np
    sx, sy = board
    n = len(sx)
    six, siy = _inverse(sx), _inverse(sy)
    cols = np.arange(1 << n, dtype=np.int64)
    bits = ((cols[:, None] >> np.arange(n)[None, :]) & 1).astype(np.int64)
    masks = np.zeros(1 << n, dtype=np.int64)
    for v in range(n):
        p = bits[:, v] | (bits[:, sx[v]] << 1) | (bits[:, six[v]] << 2) | (bits[:, sy[v]] << 3) | (bits[:, siy[v]] << 4)
        masks |= (np.int64(1) << p)
    return bits, masks


def allowed_on_finite(board, laws):
    """For each law (32-bit masks): whether the board admits a colouring of allowed patterns, and
    whether no place is frozen (both values occur at every place among the allowed colourings)."""
    import numpy as np
    bits, masks = board_patterns(board)
    Ls = np.array(laws, dtype=np.int64)
    forb = (~Ls) & 0xFFFFFFFF
    valid = (masks[:, None] & forb[None, :]) == 0                 # (colourings, laws)
    allowed = valid.any(axis=0)
    b = bits.astype(bool)
    ones = (valid[:, :, None] & b[:, None, :]).any(axis=0)       # (laws, places)
    zeros = (valid[:, :, None] & ~b[:, None, :]).any(axis=0)
    unfrozen = allowed & (ones & zeros).all(axis=1)
    return allowed, unfrozen


# ----------------------------------------------------------------------------------------------
# The tree, the lines and the plane
# ----------------------------------------------------------------------------------------------

def compat(p, g, q):
    """q can be the pattern of p's g-neighbour."""
    return centre(q) == nb(p, g) and nb(q, INV[g]) == centre(p)


def half_tree_sets(L):
    """H[g]: the allowed patterns that can root an infinite half-tree entered by the letter g (its
    parent in direction INV[g]); the greatest fixpoint."""
    allowed = patterns_of(L)
    H = [set(allowed) for _ in range(4)]
    changed = True
    while changed:
        changed = False
        for g in range(4):
            for r in list(H[g]):
                for h in range(4):
                    if h == INV[g]:
                        continue
                    if not any(compat(r, h, r2) for r2 in H[h]):
                        H[g].discard(r)
                        changed = True
                        break
    return H


def tree_patterns(L, H=None):
    """The patterns of places in law solutions on the tree."""
    if H is None:
        H = half_tree_sets(L)
    return {p for p in patterns_of(L) if all(any(compat(p, h, r) for r in H[h]) for h in range(4))}


def line_solutions(L, a, b):
    """The line Sch(ker phi), phi(x) = a, phi(y) = b: places Z, x adds a, y adds b. Returns (allowed,
    centre values occurring), exactly, from the windows on bi-infinite paths of the window graph."""
    w = max(abs(a), abs(b))
    width = 2 * w + 1

    def pat(W):
        return pattern(W[w], W[w + a], W[w - a], W[w + b], W[w - b])
    edges = []
    for W in itertools.product((0, 1), repeat=width):
        if (L >> pat(W)) & 1:
            edges.append((W[:-1], W[1:], W[w]))
    states = {s for e in edges for s in e[:2]}
    while True:
        outs = {e[0] for e in edges}
        ins = {e[1] for e in edges}
        keep = outs & ins
        new = [e for e in edges if e[0] in keep and e[1] in keep]
        if len(new) == len(edges):
            break
        edges = new
    vals = {e[2] for e in edges}
    return bool(edges), vals


LINES = ((1, 0), (0, 1), (1, 1), (1, -1), (1, 2), (2, 1))


def box_sat(L, k, centre_value=None):
    """Whether the k x k box has a colouring with allowed patterns at its (k-2)^2 interior cells
    (optionally with the central interior cell's value fixed). pysat, exact."""
    from pysat.solvers import Minisat22
    var = lambda i, j: 1 + i * k + j
    forb = [p for p in range(32) if not (L >> p) & 1]
    s = Minisat22()
    for i in range(1, k - 1):
        for j in range(1, k - 1):
            cells = (var(i, j), var(i + 1, j), var(i - 1, j), var(i, j + 1), var(i, j - 1))
            for p in forb:
                s.add_clause([-c if (p >> t) & 1 else c for t, c in enumerate(cells)])
    assum = []
    if centre_value is not None:
        c0 = var(k // 2, k // 2)
        assum = [c0 if centre_value else -c0]
    r = s.solve(assumptions=assum)
    s.delete()
    return r


# ----------------------------------------------------------------------------------------------
# Identity of indiscernibles at radius 1: boards are balanced view sets
# ----------------------------------------------------------------------------------------------

def ioi1_sat(L, mode, at_least=1):
    """IoI1 boards of law L: a set V of distinct views (allowed patterns) with permutations
    sigma_x, sigma_y of V such that sigma_g(t) is compatible with t. mode:
      'any'       some board with at least `at_least` places;
      'nonab'     some place where sigma_x sigma_y != sigma_y sigma_x;
      'planelike' sigma_x, sigma_y commute everywhere and every star has 5 distinct places.
    Returns None (unsatisfiable) or (V, sx, sy) as dicts on views."""
    from pysat.solvers import Minisat22
    from pysat.card import CardEnc, EncType
    T = patterns_of(L)
    nid = [0]

    def new():
        nid[0] += 1
        return nid[0]
    inv = {t: new() for t in T}
    m = {g: {} for g in (X_, Y_)}
    for g in (X_, Y_):
        for t in T:
            for u in T:
                if compat(t, g, u):
                    m[g][(t, u)] = new()
    cl = []
    for g in (X_, Y_):
        for (t, u), v in m[g].items():
            cl.append([-v, inv[t]])
            cl.append([-v, inv[u]])
        for t in T:
            outs = [v for (a, b), v in m[g].items() if a == t]
            ins = [v for (a, b), v in m[g].items() if b == t]
            cl.append([-inv[t]] + outs)
            cl.append([-inv[t]] + ins)
            for i in range(len(outs)):
                for j in range(i + 1, len(outs)):
                    cl.append([-outs[i], -outs[j]])
            for i in range(len(ins)):
                for j in range(i + 1, len(ins)):
                    cl.append([-ins[i], -ins[j]])
    mx, my = m[X_], m[Y_]
    if mode == 'nonab':
        ds = []
        for t in T:
            qs = []
            for w in T:
                A = new()
                cs = []
                for a in T:
                    if (t, a) in mx and (a, w) in my:
                        c = new()
                        cl.append([-c, mx[(t, a)]])
                        cl.append([-c, my[(a, w)]])
                        cs.append(c)
                cl.append([-A] + cs)
                B = new()
                for b in T:
                    if (t, b) in my and (b, w) in mx:
                        cl.append([-my[(t, b)], -mx[(b, w)], B])
                q = new()
                cl.append([-q, A])
                cl.append([-q, -B])
                qs.append(q)
            d = new()
            cl.append([-d, inv[t]])
            cl.append([-d] + qs)
            ds.append(d)
        cl.append(ds)
    elif mode == 'planelike':
        for t in T:
            for a in T:
                if (t, a) not in mx:
                    continue
                for w in T:
                    if (a, w) not in my:
                        continue
                    for b in T:
                        if (t, b) in my:
                            if (b, w) in mx:
                                cl.append([-mx[(t, a)], -my[(a, w)], -my[(t, b)], mx[(b, w)]])
                            else:
                                cl.append([-mx[(t, a)], -my[(a, w)], -my[(t, b)]])
        for t in T:
            for g, mg in ((X_, mx), (Y_, my)):
                if (t, t) in mg:
                    cl.append([-mg[(t, t)]])
                for a in T:
                    if a != t and (t, a) in mg and (a, t) in mg:
                        cl.append([-mg[(t, a)], -mg[(a, t)]])
            for a in T:
                if (t, a) in mx and (t, a) in my:
                    cl.append([-mx[(t, a)], -my[(t, a)]])
                if (t, a) in mx and (a, t) in my:
                    cl.append([-mx[(t, a)], -my[(a, t)]])
                if (a, t) in mx and (t, a) in my:
                    cl.append([-mx[(a, t)], -my[(t, a)]])
                if (a, t) in mx and (a, t) in my:
                    cl.append([-mx[(a, t)], -my[(a, t)]])
    lits = [inv[t] for t in T]
    if not lits:
        return None
    card = CardEnc.atleast(lits=lits, bound=at_least, top_id=nid[0], encoding=EncType.seqcounter)
    s = Minisat22()
    for c in cl:
        s.add_clause(c)
    for c in card.clauses:
        s.add_clause(c)
    if not s.solve():
        s.delete()
        return None
    model = set(v for v in s.get_model() if v > 0)
    s.delete()
    V = [t for t in T if inv[t] in model]
    sx = {t: u for (t, u), v in mx.items() if v in model}
    sy = {t: u for (t, u), v in my.items() if v in model}
    return V, sx, sy


def verify_ioi1(L, V, sx, sy):
    """Independent check of an IoI1 board: colour each view-place by its centre, recompute every view
    from the permutations, and check law, injectivity and that the recomputed view is the label."""
    Vs = set(V)
    if set(sx) != Vs or set(sy) != Vs or set(sx.values()) != Vs or set(sy.values()) != Vs:
        return False
    ix = {u: t for t, u in sx.items()}
    iy = {u: t for t, u in sy.items()}
    for t in V:
        p = pattern(centre(t), centre(sx[t]), centre(ix[t]), centre(sy[t]), centre(iy[t]))
        if p != t or not (L >> p) & 1:
            return False
    return True


def components(V, sx, sy):
    """The connected components of a board on views."""
    seen, comps = set(), []
    ix = {u: t for t, u in sx.items()}
    iy = {u: t for t, u in sy.items()}
    for t0 in V:
        if t0 in seen:
            continue
        comp, stack = [], [t0]
        seen.add(t0)
        while stack:
            t = stack.pop()
            comp.append(t)
            for nbr in (sx[t], ix[t], sy[t], iy[t]):
                if nbr not in seen:
                    seen.add(nbr)
                    stack.append(nbr)
        comps.append(comp)
    return comps


# ----------------------------------------------------------------------------------------------
# The square closing at a name: the relation on (e(1, c), s(1), s(c)), c = x y X Y
# ----------------------------------------------------------------------------------------------

C_PATH = (X_, Y_, XI, YI)          # 1 -x-> x -y-> xy -X-> xyX -Y-> xyXY = c


def _witnessed(p, letters, H):
    return all(any(compat(p, h, r) for r in H[h]) for h in letters)


def path_tuples(L, H=None):
    """Value tuples (s(1), s(x), s(xy), s(xyX), s(c)) along the path to c = xyXY.

    Returns (tree, cycle): the tuples in law solutions on the tree (every state with e(1, c) = 0
    refines to the tree with the same values), and those on Sch(<c>), the finest board identifying 1
    and c: a 4-cycle w0 -x-> w1 -y-> w2 -X-> w3 -Y-> w0 with half-trees attached (s(c) = s(1))."""
    if H is None:
        H = half_tree_sets(L)
    allowed = patterns_of(L)
    tree = set()
    layer = {}
    for p in allowed:
        if _witnessed(p, [h for h in range(4) if h != C_PATH[0]], H):
            layer.setdefault(p, set()).add((centre(p),))
    for i in range(1, 5):
        back = INV[C_PATH[i - 1]]
        fwd = C_PATH[i] if i < 4 else None
        others = [h for h in range(4) if h != back and h != fwd]
        new = {}
        for p, tups in layer.items():
            for q in allowed:
                if compat(p, C_PATH[i - 1], q) and _witnessed(q, others, H):
                    new.setdefault(q, set()).update(t + (centre(q),) for t in tups)
        layer = new
    for tups in layer.values():
        tree |= tups
    cyc = {0: (X_, Y_), 1: (XI, Y_), 2: (YI, XI), 3: (X_, YI)}   # each place's two cycle letters
    ok = {i: [p for p in allowed if _witnessed(p, [h for h in range(4) if h not in cyc[i]], H)] for i in range(4)}
    cycle = set()
    for q0 in ok[0]:
        for q1 in ok[1]:
            if not compat(q0, X_, q1):
                continue
            for q2 in ok[2]:
                if not compat(q1, Y_, q2):
                    continue
                for q3 in ok[3]:
                    if compat(q2, XI, q3) and compat(q3, YI, q0):
                        cycle.add((centre(q0), centre(q1), centre(q2), centre(q3), centre(q0)))
    return tree, cycle


PATH_NAMES = ('1', 'x', 'xy', 'xyX', 'xyXY')


def square_relations(L, H=None):
    """For each pair (i, j) of path names, the exact projection of the allowed states onto
    (e(1, c), s(path[i]), s(path[j])); the pair (0, 4) is the square's own relation."""
    tree, cycle = path_tuples(L, H)
    rels = {}
    for i in range(5):
        for j in range(i + 1, 5):
            rels[(i, j)] = sorted({(0, t[i], t[j]) for t in tree} | {(1, t[i], t[j]) for t in cycle})
    return rels
