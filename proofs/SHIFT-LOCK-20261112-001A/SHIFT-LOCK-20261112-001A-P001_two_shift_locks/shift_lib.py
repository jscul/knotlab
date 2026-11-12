"""Locks across two shifts (research/SHIFT-LOCK-20261112-001/preregistration.md, ticket A).

Harmonies stitched in one order, as in LOOP-LOCK-20261112-001: each copy is a state of a harmony H, and a knot (x, y, z) of copies binds
NAE((x, i), (y, i + a), (z, i + b)) for every kind (0, a, b) of H and every place i; R is the one-knot relation on H's states. Copies sit
at (r, c) in Z_n x Z_m. One-shift knots ((r, c), (r, c+1), (r, c+2)) and ((r, c), (r+1, c), (r+2, c)); the two-shift knot
((r, c), (r, c+1), (r+1, c)). Locked: every copy equal to every other, place by place, in every state."""
import math
import sys
from pathlib import Path

import numpy as np
from pysat.solvers import Solver

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "proofs/LOOP-LOCK-20261112-001A/LOOP-LOCK-20261112-001A-P001_loop_locking"))
import loop_lib as L  # noqa: E402

E = L.E


def harmonies():
    return E.harmonies()


def name(h):
    return " + ".join(h["orbits"])


# ---------------------------------------------------------------- the relation, its symmetries, the pair transfer

def setup(h):
    W, R, T = L.relation(h)
    P = h["P"]
    mask = (1 << P) - 1
    index = {x: i for i, x in enumerate(W)}
    G = []  # the group <shift, complement> acting on W: element (a, e) sends x to (x read from place a), complemented if e
    for e in (0, 1):
        for a in range(P):
            perm = tuple(index[L.rot(x, a, P) ^ (mask if e else 0)] for x in W)
            G.append(((a, e), perm))
    return {"h": h, "W": W, "R": R, "P": P, "G": G, "Rset": set(R)}


def pair_transfer(S):
    W, R = S["W"], S["R"]
    n = len(W)
    M = np.zeros((n * n, n * n), dtype=np.uint8)
    for (u, v, w) in R:
        M[u * n + v, v * n + w] = 1
    diag = np.array([i // n == i % n for i in range(n * n)])
    return M, diag


def bool_powers(M, kmax):
    out = [np.eye(M.shape[0], dtype=np.uint8)]
    Mi = M.astype(np.int64)
    for _ in range(kmax):
        out.append(((out[-1].astype(np.int64) @ Mi) > 0).astype(np.uint8))
    return out


def ring_unlocks(pw, diag, k):
    """a closed walk of length k of the pair transfer through an off-diagonal pair (a non-constant ring state of k knots)"""
    return bool(any(pw[k][i, i] for i in np.nonzero(~diag)[0]))


def ring_states(S, k, cap):
    """all ring states of k knots (closed walks of length k of the pair transfer), as tuples of state indices; None past cap"""
    W, Rs = S["W"], S["Rset"]
    n = len(W)
    nxt = {}
    for (u, v, w) in S["R"]:
        nxt.setdefault((u, v), []).append(w)
    out = []
    if k == 1:
        return [(u,) for u in range(n)]
    for s0 in range(n):
        for s1 in range(n):
            if k == 2:
                if (s0, s1, s0) in Rs and (s1, s0, s1) in Rs:
                    out.append((s0, s1))
                continue
            stack = [[s0, s1]]
            while stack:
                seq = stack.pop()
                if len(seq) == k:
                    if (seq[-2], seq[-1], seq[0]) in Rs and (seq[-1], seq[0], seq[1]) in Rs:
                        out.append(tuple(seq))
                        if len(out) > cap:
                            return None
                    continue
                for w in nxt.get((seq[-2], seq[-1]), []):
                    stack.append(seq + [w])
    return out


# ---------------------------------------------------------------- patterns

def cell(n, m):
    return lambda r, c: (r % n) * m + (c % m)


def one_shift_pattern(n, m):
    v = cell(n, m)
    knots = [(v(r, c), v(r, c + 1), v(r, c + 2)) for r in range(n) for c in range(m)]
    knots += [(v(r, c), v(r + 1, c), v(r + 2, c)) for r in range(n) for c in range(m)]
    return (n * m, knots)


def two_shift_pattern(n, m):
    v = cell(n, m)
    return (n * m, [(v(r, c), v(r, c + 1), v(r + 1, c)) for r in range(n) for c in range(m)])


def is_state(S, n, m, X):
    Rs = S["Rset"]
    v = cell(n, m)
    return all((X[v(r, c)], X[v(r, c + 1)], X[v(r + 1, c)]) in Rs for r in range(n) for c in range(m))


# ---------------------------------------------------------------- stepped states and short steps

def power(perm, k, u):
    for _ in range(k):
        u = perm[u]
    return u


def stepped_states(S, n, m):
    """X(r, c) = g^r h^c u with g, h in <shift, complement>, R(u, hu, gu), g^n u = u, h^m u = u"""
    out = set()
    nW = len(S["W"])
    v = cell(n, m)
    for (_, g) in S["G"]:
        for (_, hh) in S["G"]:
            for u in range(nW):
                if (u, hh[u], g[u]) not in S["Rset"]:
                    continue
                if power(g, n, u) != u or power(hh, m, u) != u:
                    continue
                X = [0] * (n * m)
                for r in range(n):
                    row = power(g, r, u)
                    for c in range(m):
                        X[v(r, c)] = row
                        row = hh[row]
                out.add(tuple(X))
    return out


BUDGET = 20000  # conflicts per solver call in the short and broad searches; past it the cell is "not settled"

SHORT = [(1, 0), (0, 1), (1, 1), (1, -1), (2, 0), (0, 2), (2, 1), (1, 2), (2, -1), (1, -2), (2, 2), (2, -2)]


def short_steps(n, m):
    """the steps of sup-norm at most 2 (up to sign) that are not zero on the n x m repeat, one for each distinct reduction"""
    seen, out = set(), []
    for (a, b) in SHORT:
        red = (a % n, b % m)
        neg = ((-a) % n, (-b) % m)
        if red == (0, 0) or red in seen or neg in seen:
            continue
        seen.add(red)
        out.append((a, b))
    return out


def invariances(S, X, n, m, steps):
    """the (step, symmetry) pairs with X(x + step) = g X(x) at every copy x"""
    v = cell(n, m)
    out = []
    for (a, b) in steps:
        for (gname, g) in S["G"]:
            if all(X[v(r + a, c + b)] == g[X[v(r, c)]] for r in range(n) for c in range(m)):
                out.append(((a, b), gname))
    return out


def shortest_invariance(S, X, n, m):
    """the least sup-norm of a step, not zero on the repeat, along which X is invariant up to a symmetry of the harmony"""
    best = None
    for a in range(-(n // 2), n // 2 + 1):
        for b in range(-(m // 2), m // 2 + 1):
            if (a % n, b % m) == (0, 0):
                continue
            size = max(abs(a), abs(b))
            if best is not None and size >= best:
                continue
            if invariances(S, X, n, m, [(a, b)]):
                best = size
    return best


# ---------------------------------------------------------------- SAT

def bits(S, X, var):
    P = S["P"]
    lits = []
    for c, x in enumerate(X):
        w = S["W"][x]
        for i in range(P):
            lits.append(var(c, i) if (w >> i) & 1 else -var(c, i))
    return lits


def decode(S, model, var, ncopies):
    P = S["P"]
    pos = set(l for l in model if l > 0)
    index = {x: i for i, x in enumerate(S["W"])}
    X = []
    for c in range(ncopies):
        w = sum(1 << i for i in range(P) if var(c, i) in pos)
        X.append(index[w])
    return tuple(X)


def unlocking_state(S, Ppat):
    """a state with some copy unequal to copy 0, or None if locked (or no state)"""
    cl, nv, var = E.build(Ppat, S["h"], "one order")
    P = S["P"]
    aux, extra, nxt = [], [], nv + 1
    for c in range(1, Ppat[0]):
        for i in range(P):
            y = nxt
            nxt += 1
            a, b = var(0, i), var(c, i)
            extra += [[-y, a, b], [-y, -a, -b]]
            aux.append(y)
    with Solver(name="cadical153", bootstrap_with=cl + extra + [aux]) as s:
        if not s.solve():
            return None
        return decode(S, s.get_model(), var, Ppat[0])


def state_outside(S, Ppat, family):
    """a state of the pattern not in the given family of states, or None"""
    cl, nv, var = E.build(Ppat, S["h"], "one order")
    block = [[-l for l in bits(S, X, var)] for X in family]
    with Solver(name="cadical153", bootstrap_with=cl + block) as s:
        if not s.solve():
            return None
        return decode(S, s.get_model(), var, Ppat[0])


def invariance_clauses(S, var, n, m, step, gname, sel, nxt):
    """clauses saying: if sel, X(x + step) = g X(x) at every copy and place (g = shift by a places, complemented if e); returns
    (clauses, next free variable)"""
    a_, e = gname
    P = S["P"]
    v = cell(n, m)
    cl = []
    for r in range(n):
        for c in range(m):
            x, y = v(r, c), v(r + step[0], c + step[1])
            for i in range(P):
                p, q = var(y, i), var(x, (i + a_) % P)
                if e:
                    cl += [[-sel, p, q], [-sel, -p, -q]]
                else:
                    cl += [[-sel, p, -q], [-sel, -p, q]]
    return cl, nxt


def violation_clauses(S, var, n, m, step, gname, nxt):
    """clauses saying X(x + step) differs from g X(x) somewhere; returns (clauses, next free variable)"""
    a_, e = gname
    P = S["P"]
    v = cell(n, m)
    cl, ds = [], []
    for r in range(n):
        for c in range(m):
            x, y = v(r, c), v(r + step[0], c + step[1])
            for i in range(P):
                p, q = var(y, i), var(x, (i + a_) % P)
                d = nxt
                nxt += 1
                ds.append(d)
                if e:
                    cl += [[-d, p, -q], [-d, -p, q]]
                else:
                    cl += [[-d, p, q], [-d, -p, -q]]
    cl.append(ds)
    return cl, nxt


def nonconstant_clauses(S, var, ncopies, nxt):
    P = S["P"]
    cl, ds = [], []
    for c in range(1, ncopies):
        for i in range(P):
            d = nxt
            nxt += 1
            ds.append(d)
            a, b = var(0, i), var(c, i)
            cl += [[-d, a, b], [-d, -a, -b]]
    cl.append(ds)
    return cl, nxt


def short_state(S, n, m, Ppat):
    """a non-constant state invariant, up to a symmetry of the harmony, along some short step; None if there is none. One
    (step, symmetry) pair at a time, each guarded by a selector and refuted before the next is added"""
    cl, nv, var = E.build(Ppat, S["h"], "one order")
    extra, nxt = nonconstant_clauses(S, var, Ppat[0], nv + 1)
    with Solver(name="cadical153", bootstrap_with=cl + extra) as s:
        for step in short_steps(n, m):
            for (gname, _) in S["G"]:
                sel = nxt
                nxt += 1
                c2, nxt = invariance_clauses(S, var, n, m, step, gname, sel, nxt)
                for c in c2:
                    s.add_clause(c)
                s.conf_budget(BUDGET)
                res = s.solve_limited(assumptions=[sel])
                if res is None:
                    return "not settled"
                if res:
                    return decode(S, s.get_model(), var, Ppat[0])
                s.add_clause([-sel])
    return None


def broad_state(S, n, m, Ppat, max_rounds=400):
    """a non-constant state invariant along no short step (up to every symmetry of the harmony): returns (state or None, rounds);
    the solver is refined with every invariance a found state has"""
    cl, nv, var = E.build(Ppat, S["h"], "one order")
    extra, nxt = nonconstant_clauses(S, var, Ppat[0], nv + 1)
    steps = short_steps(n, m)
    with Solver(name="cadical153", bootstrap_with=cl + extra) as s:
        for rounds in range(1, max_rounds + 1):
            s.conf_budget(BUDGET)
            res = s.solve_limited()
            if res is None:
                return "not settled", rounds
            if not res:
                return None, rounds
            X = decode(S, s.get_model(), var, Ppat[0])
            inv = invariances(S, X, n, m, steps)
            if not inv:
                return X, rounds
            for (step, gname) in inv:
                c2, nxt = violation_clauses(S, var, n, m, step, gname, nxt)
                for c in c2:
                    s.add_clause(c)
    return "not settled", max_rounds


def stabiliser(X, n, m):
    """the translations (dr, dc) of Z_n x Z_m that fix the state"""
    v = cell(n, m)
    return [(dr, dc) for dr in range(n) for dc in range(m)
            if all(X[v(r, c)] == X[v(r + dr, c + dc)] for r in range(n) for c in range(m))]


def tied_to_first(S, Ppat):
    """the copies equal to copy 0, place by place, in every state"""
    res = L.locked(Ppat, S["h"], [[0, c] for c in range(1, Ppat[0])])
    if res is None:
        return None
    return [0] + [c for c, r in zip(range(1, Ppat[0]), res) if r]


# ---------------------------------------------------------------- increments on one orbit

def increments(S):
    """for each orbit (by its first state index), A_u = {(a, b) mod the orbit's period : R(u, shift_a u, shift_b u)}, and whether A_u
    holds a subgroup of Z_p^2 other than {(0, 0)} (the linear case)"""
    W, P = S["W"], S["P"]
    index = {x: i for i, x in enumerate(W)}
    seen, out = set(), []
    for iu, x in enumerate(W):
        if iu in seen:
            continue
        orbit = []
        y = x
        while True:
            orbit.append(index[y])
            y = L.rot(y, 1, P)
            if y == x:
                break
        seen.update(orbit)
        p = len(orbit)
        A = sorted((a, b) for a in range(p) for b in range(p) if (iu, orbit[a], orbit[b]) in S["Rset"])
        Aset = set(A)
        subgroups = []
        for (a, b) in A:
            if (a, b) == (0, 0):
                continue
            cyc = {((a * t) % p, (b * t) % p) for t in range(p)}
            if cyc <= Aset:
                subgroups.append((a, b))
        triple = all(e == e1 == e2 for e in A for e1 in A for e2 in A
                     if (e[0] - e1[0]) % p == (e[1] - e2[1]) % p)
        out.append({"orbit start": iu, "period": p, "A": A, "cyclic subgroups inside": subgroups,
                    "graph subgroups inside (lambda not 0 or 1)": [lam for lam in range(2, p)
                                                                   if all(((a, (lam * a) % p) in Aset) for a in range(p))],
                    "passes the triple test": triple})
    return out


# ---------------------------------------------------------------- the linear control (Ledrappier's law over two values)

def ledrappier_kernel_dim(n):
    """dimension over F2 of the states of x(r, c) + x(r, c+1) + x(r+1, c) = 0 on Z_n x Z_n"""
    v = cell(n, n)
    rows = []
    for r in range(n):
        for c in range(n):
            rows.append((1 << v(r, c)) ^ (1 << v(r, c + 1)) ^ (1 << v(r + 1, c)))
    rank, pivots = 0, {}
    for row in rows:
        while row:
            p = row.bit_length() - 1
            if p in pivots:
                row ^= pivots[p]
            else:
                pivots[p] = row
                rank += 1
                break
    return n * n - rank


def gf2_polymod_gcd_nontrivial(n):
    """whether (1 + S)^n + 1 and S^n + 1 share a factor over F2 (the advisor's criterion for a non-zero state)"""
    def mul(a, b):
        r = 0
        while b:
            if b & 1:
                r ^= a
            a <<= 1
            b >>= 1
        return r

    def mod(a, b):
        db = b.bit_length()
        while a and a.bit_length() >= db:
            a ^= b << (a.bit_length() - db)
        return a
    f = 1
    for _ in range(n):
        f = mul(f, 0b11)
    f ^= 1
    g = (1 << n) | 1
    while f:
        g, f = f, mod(g, f)
    return g.bit_length() > 1


def ledrappier_short_dims(n):
    """for each short step v not zero on Z_n x Z_n, the dimension over F2 of the linear law's states invariant along v"""
    v = cell(n, n)
    base = []
    for r in range(n):
        for c in range(n):
            base.append((1 << v(r, c)) ^ (1 << v(r, c + 1)) ^ (1 << v(r + 1, c)))
    out = {}
    for (a, b) in short_steps(n, n):
        rows = list(base)
        for r in range(n):
            for c in range(n):
                x, y = v(r, c), v(r + a, c + b)
                if x != y:
                    rows.append((1 << x) ^ (1 << y))
        rank, pivots = 0, {}
        for row in rows:
            while row:
                p = row.bit_length() - 1
                if p in pivots:
                    row ^= pivots[p]
                else:
                    pivots[p] = row
                    rank += 1
                    break
        out["%d,%d" % (a, b)] = n * n - rank
    return out

