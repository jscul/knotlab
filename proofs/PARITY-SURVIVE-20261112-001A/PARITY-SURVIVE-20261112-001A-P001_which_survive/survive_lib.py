"""Which parity placements survive (research/PARITY-SURVIVE-20261112-001/preregistration.md, ticket A).

As in PARITY-MIX-20261112-001: copies of a harmony at (r, c) on the n x n repeat; at each cell the mixed knot is the not-all-equal
one-order stitch or a flip-blind parity knot. Classes: a state with its complement. Tiers of fixing by count 0 (up to flips):
F, the full system; P, parity knots and every copy a state of the harmony, no not-all-equal stitch; L, the parity equations alone on
classes over F_2 (each class a vector of F_2^P modulo all-ones); GAC, arc consistency on class domains with both relations' class
projections, started from count 0's classes."""
import math
import random
import sys
from pathlib import Path

from pysat.solvers import Solver

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "proofs/PARITY-MIX-20261112-001A/PARITY-MIX-20261112-001A-P001_parity_among_copies"))
import parity_lib as PL  # noqa: E402

S = PL.S
E = PL.E


def setup(h):
    st = PL.setup(h)
    W, P = st["W"], st["P"]
    mask = (1 << P) - 1
    reps = sorted({st["cls"][i] for i in range(len(W))})
    st["classes"] = reps
    st["cidx"] = {c: j for j, c in enumerate(reps)}
    st["ccls"] = [st["cidx"][st["cls"][i]] for i in range(len(W))]  # state index -> class number
    canon = lambda x: min(x, x ^ mask)
    st["cvec"] = [canon(W[c]) for c in reps]  # class number -> canonical word (a vector modulo all-ones)
    Ws = set(W)
    nc = len(reps)
    fb = set()
    for a in range(nc):
        for b in range(nc):
            s = st["cvec"][a] ^ st["cvec"][b]
            for t in (s, s ^ mask):
                if t in Ws:
                    fb.add((a, b, st["ccls"][W.index(t)]))
    st["FBcls"] = fb
    st["Rcls"] = {(st["ccls"][x], st["ccls"][y], st["ccls"][z]) for (x, y, z) in st["R"]}
    return st


def fb_in_R(st):
    """flip-blind triples (u, v, w) of states that the not-all-equal stitch allows"""
    W, P = st["W"], st["P"]
    mask = (1 << P) - 1
    return sum(1 for (u, v, w) in st["R"] if (W[u] ^ W[v] ^ W[w]) in (0, mask))


def class_level_state(st, n, K):
    """a class colouring with flip-blind class triples at parity cells and the stitch's class triples elsewhere (no lifting)"""
    nc = len(st["classes"])
    var = lambda x, a: x * nc + a + 1
    cl = []
    for x in range(n * n):
        cl.append([var(x, a) for a in range(nc)])
        for a in range(nc):
            for b in range(a + 1, nc):
                cl.append([-var(x, a), -var(x, b)])
    ks = PL.knots(n, n)
    for c, (x, y, z) in enumerate(ks):
        allowed = st["FBcls"] if c in K else st["Rcls"]
        for a in range(nc):
            for b in range(nc):
                for d in range(nc):
                    if (a, b, d) not in allowed:
                        cl.append([-var(x, a), -var(y, b), -var(z, d)])
    with Solver(name="cadical153", bootstrap_with=cl) as s:
        return s.solve()


def full_state(st, n, K):
    cl, nxt, var = PL.build(st, n, n, K, 0)
    with Solver(name="cadical153", bootstrap_with=cl) as s:
        return s.solve()


def cell_neighbours(n):
    """cells whose knots share a copy with a cell's knot"""
    ks = PL.knots(n, n)
    out = {}
    for c, k in enumerate(ks):
        out[c] = {d for d, k2 in enumerate(ks) if d != c and set(k) & set(k2)}
    return out


def has_isolated_parity_cell(n, K, nb):
    return any(not (nb[c] & K) for c in K)


def bernoulli_placement(n, rho, tag):
    rng = random.Random(tag)
    return frozenset(c for c in range(n * n) if rng.random() < rho)


def first_moment_rate(st, rho):
    """lambda(rho) per cell: ln|W| + rho ln(|FB| / |W|^3) + (1 - rho) ln(|R| / |W|^3), with FB the ordered flip-blind triples of states"""
    W, P = st["W"], st["P"]
    mask = (1 << P) - 1
    Ws = set(W)
    nW = len(W)
    fb = sum((((W[u] ^ W[v]) in Ws) + (((W[u] ^ W[v]) ^ mask) in Ws)) for u in range(nW) for v in range(nW))
    return math.log(nW) + rho * math.log(fb / nW ** 3) + (1 - rho) * math.log(len(st["R"]) / nW ** 3)


# ---------------------------------------------------------------- tiers of fixing

def tier_F_P(st, n, K, drop_nae, r0=0):
    """for the counts r != r0, in order r0 + 1, ..., r0 + n - 1: (flip-frozen, fixed by count r0) in the full system (drop_nae False)
    or the parity-and-states system P"""
    if drop_nae:
        # P: parity knots only, every copy a state: build with every non-parity cell absent
        cl1, nxt, var1 = build_parity_only(st, n, K, 0)
        cl2, nxt2, var2 = build_parity_only(st, n, K, nxt)
    else:
        cl1, nxt, var1 = PL.build(st, n, n, K, 0)
        cl2, nxt2, var2 = PL.build(st, n, n, K, nxt)
    nxt = nxt2
    v = S.cell(n, n)
    with Solver(name="cadical153", bootstrap_with=cl1) as s:
        if not s.solve():
            return None
    cl = cl1 + cl2
    A0 = nxt
    nxt += 1
    for c in range(n):
        c2, nxt = PL.eqmod_clauses(st, var1, var2, v(r0, c), A0, nxt)
        cl += c2
    D = {}
    for j in range(1, n):
        D[j] = nxt
        nxt += 1
        c2, nxt = PL.differ_mod_clauses(st, var1, var2, [v(r0 + j, c) for c in range(n)], D[j], nxt)
        cl += c2
    out = []
    with Solver(name="cadical153", bootstrap_with=cl) as s:
        for j in range(1, n):
            frozen = not s.solve(assumptions=[D[j]])
            fixed = frozen or not s.solve(assumptions=[A0, D[j]])
            out.append((frozen, fixed))
    return out


def build_parity_only(st, n, K, offset):
    """copies with their own kinds and the parity knots at K, nothing else"""
    import itertools
    h, P = st["h"], st["P"]
    cl, nv, var0 = E.build((n * n, []), h, "one order")
    var = lambda x, i: var0(x, i) + offset
    cl = [[l + offset if l > 0 else l - offset for l in c] for c in cl]
    nxt = nv + offset + 1
    for c, (x, y, z) in enumerate(PL.knots(n, n)):
        if c not in K:
            continue
        r = nxt
        nxt += 1
        for i in range(P):
            lits = [var(x, i), var(y, i), var(z, i), r]
            for signs in itertools.product((1, -1), repeat=4):
                if sum(1 for s in signs if s < 0) % 2 == 1:
                    cl.append([s * l for s, l in zip(signs, lits)])
    return cl, nxt, var


def tier_L(n, K, r0=0):
    """counts r0 + j, j = 1..n-1, whose every copy is an F_2-linear function of count 0 under the parity equations alone (one F_2 coordinate;
    every coordinate of a class obeys the same equations)"""
    N = n * n
    v = S.cell(n, n)
    rows = []
    for c, (x, y, z) in enumerate(PL.knots(n, n)):
        if c in K:
            rows.append((1 << x) ^ (1 << y) ^ (1 << z))
    # the solution space: its basis; x_c is fixed by count 0 iff every solution vanishing on count 0 vanishes at c
    # solutions vanishing on count 0: add equations x_{(0, c)} = 0
    eqs = rows + [1 << v(r0, c) for c in range(n)]
    basis = nullspace(eqs, N)
    fixed_cells = {c for c in range(N) if all(not ((b >> c) & 1) for b in basis)}
    return [all(v(r0 + j, c) in fixed_cells for c in range(n)) for j in range(1, n)]


def nullspace(eqs, N):
    """a basis of {x in F_2^N : e.x = 0 for every e}"""
    piv = {}
    for e in eqs:
        for p, row in piv.items():
            if (e >> p) & 1:
                e ^= row
        if e:
            p = e.bit_length() - 1
            for q in list(piv):
                if (piv[q] >> p) & 1:
                    piv[q] ^= e
            piv[p] = e
    free = [c for c in range(N) if c not in piv]
    basis = []
    for f in free:
        x = 1 << f
        for p, row in piv.items():
            if (row >> f) & 1:
                x |= 1 << p
        basis.append(x)
    return basis


def tier_GAC(st, n, K, count0_assignments, r0=0):
    """for the counts r0 + j: every copy's class domain a singleton after arc consistency from each given count-r0 class assignment"""
    nc = len(st["classes"])
    ks = PL.knots(n, n)
    v = S.cell(n, n)
    allowed = [st["FBcls"] if c in K else st["Rcls"] for c in range(len(ks))]
    res = [True] * (n - 1)
    for a0 in count0_assignments:
        dom = [set(range(nc)) for _ in range(n * n)]
        for c in range(n):
            dom[v(r0, c)] = {a0[c]}
        changed = True
        while changed:
            changed = False
            for c, (x, y, z) in enumerate(ks):
                A = allowed[c]
                sup = [(a, b, d) for (a, b, d) in A if a in dom[x] and b in dom[y] and d in dom[z]]
                for pos, var in ((0, x), (1, y), (2, z)):
                    keep = {t[pos] for t in sup}
                    if keep != dom[var]:
                        dom[var] = keep
                        changed = True
        for j in range(1, n):
            if not all(len(dom[v(r0 + j, c)]) == 1 for c in range(n)):
                res[j - 1] = False
    return res


def count0_class_assignments(st, n, K, r0=0, cap=30):
    """distinct count-r0 class assignments of states (up to cap; None past it)"""
    cl, nxt, var = PL.build(st, n, n, K, 0)
    v = S.cell(n, n)
    out = []
    with Solver(name="cadical153", bootstrap_with=cl) as s:
        while len(out) < cap and s.solve():
            X = PL.S.decode(st, s.get_model(), var, n * n)
            a0 = tuple(st["ccls"][X[v(r0, c)]] for c in range(n))
            out.append(a0)
            # block this assignment of count r0's classes: forbid its exact words with every pattern of flips
            words = [st["W"][X[v(r0, c)]] for c in range(n)]
            mask = (1 << st["P"]) - 1
            import itertools
            for flips in itertools.product((0, 1), repeat=n):
                lits = []
                for c in range(n):
                    w = words[c] ^ (mask if flips[c] else 0)
                    for i in range(st["P"]):
                        lits.append(-var(v(r0, c), i) if (w >> i) & 1 else var(v(r0, c), i))
                s.add_clause(lits)
        if len(out) >= cap and s.solve():
            return None
    return sorted(set(out))


def tiers(st, n, K):
    """for every base count r0 and every other count: F, P, L, GAC fixing and flip-freezing; None if K leaves no state"""
    out = []
    for r0 in range(n):
        F = tier_F_P(st, n, K, False, r0)
        if F is None:
            return None
        Pt = tier_F_P(st, n, K, True, r0)
        Lt = tier_L(n, K, r0)
        a0 = count0_class_assignments(st, n, K, r0)
        G = tier_GAC(st, n, K, a0, r0) if a0 is not None else None
        for j in range(n - 1):
            out.append({"base": r0, "count": (r0 + j + 1) % n, "flip-frozen": F[j][0], "F": F[j][1],
                        "P": bool(Pt[j][1]) if Pt else None, "P flip-frozen": bool(Pt[j][0]) if Pt else None,
                        "L": Lt[j], "GAC": None if G is None else G[j]})
    return out
