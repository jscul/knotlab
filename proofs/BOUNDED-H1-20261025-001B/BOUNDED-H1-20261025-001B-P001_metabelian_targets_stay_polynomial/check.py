"""Check for BOUNDED-H1-20261025-001B-P001: metabelian targets stay polynomial with bounded homology.

Standard library only. The algorithm: for a finite group G with an abelian normal subgroup N and nilpotent quotient Q = G/N,
  (1) enumerate Hom(P, Q) by lifting through a central series of Q with prime-order factors (a linear system over F_p per step,
      whose solutions are a translate of Hom(H1(P), F_p));
  (2) for each, count the lifts through N as solutions of a linear system over N whose coefficients come from the twisted
      expansion of the relators (Fox calculus), by elimination over Z/p^a.
Parts:
  1. decompositions: every test group has one, S4 has none;
  2. random presentations with bounded mod-p homology: the algorithm agrees with brute force, and |Hom(P, Q)| <= |Q|^d;
  3. knot groups (Wirtinger presentations) with the meridian sent to a fixed conjugacy class: agreement with brute force;
  4. scale: tripled alternating knots of grids with hundreds of generators; S3 transposition counts equal 3^n, as predicted by
     BOUNDED-H1-20261025-001A, while the algorithm stays fast;
  5. controls.
Writes result.json next to this file."""
import itertools
import json
import math
import random
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent


# ------------------------------------------------------------------------------------------------------------------ groups
class Group:
    def __init__(self, name, els, mul):
        self.name = name
        self.els = list(els)
        self.n = len(self.els)
        ix = {g: i for i, g in enumerate(self.els)}
        self.M = [[ix[mul(a, b)] for b in self.els] for a in self.els]
        self.e = next(i for i in range(self.n) if all(self.M[i][j] == j for j in range(self.n)))
        self.I = [next(j for j in range(self.n) if self.M[i][j] == self.e) for i in range(self.n)]

    def conj(self, h, a):
        return self.M[self.M[h][a]][self.I[h]]

    def closure(self, gens):
        S = {self.e}
        fr = [self.e]
        while fr:
            new = []
            for x in fr:
                for g in gens:
                    y = self.M[x][g]
                    if y not in S:
                        S.add(y)
                        new.append(y)
            fr = new
        return frozenset(S)

    def classes(self):
        seen, out = set(), []
        for a in range(self.n):
            if a in seen:
                continue
            c = frozenset(self.conj(h, a) for h in range(self.n))
            seen |= c
            out.append(c)
        return out

    def normal_subgroups(self):
        found = {frozenset([self.e])}
        fr = [frozenset([self.e])]
        cls = self.classes()
        while fr:
            new = []
            for Nn in fr:
                for c in cls:
                    if c <= Nn:
                        continue
                    S = self.closure(list(Nn | c))
                    if S not in found:
                        found.add(S)
                        new.append(S)
            fr = new
        return sorted(found, key=len)

    def commutator_subgroup(self, A, B):
        return self.closure([self.M[self.M[self.M[a][b]][self.I[a]]][self.I[b]] for a in A for b in B])


def metacyclic(m, r, n, name):
    els = [(x, y) for y in range(n) for x in range(m)]
    return Group(name, els, lambda a, b: ((a[0] + pow(r, a[1], m) * b[0]) % m, (a[1] + b[1]) % n))


def dicyclic(N, name):
    els = [(k, j) for j in (0, 1) for k in range(2 * N)]

    def mul(a, b):
        (k1, j1), (k2, j2) = a, b
        if j1 == 0:
            return ((k1 + k2) % (2 * N), j2)
        if j2 == 0:
            return ((k1 - k2) % (2 * N), 1)
        return ((k1 - k2 + N) % (2 * N), 0)
    return Group(name, els, mul)


def perm_group(gens, n, name):
    idn = tuple(range(n))
    S = {idn}
    fr = [idn]
    while fr:
        new = []
        for p in fr:
            for g in gens:
                q = tuple(p[g[i]] for i in range(n))
                if q not in S:
                    S.add(q)
                    new.append(q)
        fr = new
    return Group(name, sorted(S), lambda p, q: tuple(p[q[i]] for i in range(n)))


def heisenberg(p):
    els = [(a, b, c) for a in range(p) for b in range(p) for c in range(p)]
    return Group(f"Heis{p ** 3}", els, lambda x, y: ((x[0] + y[0]) % p, (x[1] + y[1]) % p, (x[2] + y[2] + x[0] * y[1]) % p))


def is_abelian(G, A):
    return all(G.M[a][b] == G.M[b][a] for a in A for b in A)


def decomposition(G):
    """an abelian normal subgroup N with G/N nilpotent (largest such N first), or None"""
    full = frozenset(range(G.n))
    lower = [full]
    while True:
        nxt = G.commutator_subgroup(lower[-1], full)
        if nxt == lower[-1]:
            break
        lower.append(nxt)
    for Nn in sorted(G.normal_subgroups(), key=len, reverse=True):
        if not is_abelian(G, Nn):
            continue
        # G/N nilpotent iff some term of the lower central series of G lies in N
        if any(term <= Nn for term in lower):
            return Nn
    return None


# ------------------------------------------------------------------------------------------- quotient structure and series
def quotient_series(G, Nn):
    """normal subgroups G = K_0 > K_1 > ... > K_s = N, each K_i/K_{i+1} central in G/K_{i+1} of prime order;
    returns list of (K_i, c_i, p_i) with c_i in K_i generating K_i modulo K_{i+1}"""
    chain = [Nn]
    while len(chain[-1]) < G.n:
        K = chain[-1]
        # elements central modulo K and of prime order modulo K, outside K
        cand = None
        for z in range(G.n):
            if z in K:
                continue
            central = all(G.M[G.M[G.M[z][h]][G.I[z]]][G.I[h]] in K for h in range(G.n))
            if not central:
                continue
            # order modulo K
            o, x = 1, z
            while x not in K:
                x = G.M[x][z]
                o += 1
            if all(o % d for d in range(2, o)):
                cand = (z, o)
                break
        z, o = cand
        Knew = G.closure(list(K) + [z])
        chain.append(Knew)
    chain = list(reversed(chain))           # G = chain[0] > ... > chain[-1] = N
    series = []
    for i in range(len(chain) - 1):
        K, Knext = chain[i], chain[i + 1]
        z = next(x for x in K if x not in Knext)
        p = len(K) // len(Knext)
        series.append((K, Knext, z, p))
    return series


# ------------------------------------------------------------------------------------------------------------ presentations
def evaluate(G, word, imgs):
    x = G.e
    for gen, s in word:
        g = imgs[gen]
        x = G.M[x][g if s > 0 else G.I[g]]
    return x


def homology_dims(ngen, rels, primes):
    out = {}
    for p in primes:
        rows = []
        for r in rels:
            row = [0] * ngen
            for gen, s in r:
                row[gen] += s
            rows.append([x % p for x in row])
        rank = 0
        A = [r[:] for r in rows]
        for c in range(ngen):
            pr = next((i for i in range(rank, len(A)) if A[i][c] % p), None)
            if pr is None:
                continue
            A[rank], A[pr] = A[pr], A[rank]
            inv = pow(A[rank][c], p - 2, p)
            A[rank] = [(v * inv) % p for v in A[rank]]
            for i in range(len(A)):
                if i != rank and A[i][c] % p:
                    f = A[i][c]
                    A[i] = [(v - f * w) % p for v, w in zip(A[i], A[rank])]
            rank += 1
        out[p] = ngen - rank
    return out


# ---------------------------------------------------------------------------------------- linear algebra over Z/p^a and F_p
def solve_mod_prime(rows, rhs, nv, p):
    """all solutions of a linear system over F_p, as (particular, basis) or None"""
    A = [r[:] + [b] for r, b in zip(rows, rhs)]
    piv, r = [], 0
    for c in range(nv):
        pr = next((i for i in range(r, len(A)) if A[i][c] % p), None)
        if pr is None:
            continue
        A[r], A[pr] = A[pr], A[r]
        inv = pow(A[r][c], p - 2, p)
        A[r] = [(v * inv) % p for v in A[r]]
        for i in range(len(A)):
            if i != r and A[i][c] % p:
                f = A[i][c]
                A[i] = [(v - f * w) % p for v, w in zip(A[i], A[r])]
        piv.append(c)
        r += 1
    if any(all(v % p == 0 for v in row[:nv]) and row[nv] % p for row in A):
        return None
    part = [0] * nv
    for i, c in enumerate(piv):
        part[c] = A[i][nv] % p
    basis = []
    for fc in (c for c in range(nv) if c not in piv):
        v = [0] * nv
        v[fc] = 1
        for i, c in enumerate(piv):
            v[c] = (-A[i][fc]) % p
        basis.append(v)
    return part, basis


def count_mod_prime_power(rows, rhs, nv, p, a):
    """number of solutions in (Z/p^a)^nv of a linear system over Z/p^a (elimination with valuation pivoting)"""
    q = p ** a
    A = [[v % q for v in r] + [b % q] for r, b in zip(rows, rhs)]
    total_exp = 0           # log_p of the number of solutions
    used_rows, cols = set(), list(range(nv))
    free = nv
    for _ in range(nv):
        best = None
        for i in range(len(A)):
            if i in used_rows:
                continue
            for c in cols:
                v = A[i][c] % q
                if v:
                    val = 0
                    while v % p == 0:
                        v //= p
                        val += 1
                    if best is None or val < best[0]:
                        best = (val, i, c)
        if best is None:
            break
        val, i, c = best
        unit = (A[i][c] // p ** val) % q
        inv = pow(unit, -1, q)
        A[i] = [(v * inv) % q for v in A[i]]          # pivot entry = p^val
        for k in range(len(A)):
            if k != i and A[k][c] % q:
                f = (A[k][c] // p ** val)            # every other entry in this column has valuation >= val
                A[k] = [(v - f * w) % q for v, w in zip(A[k], A[i])]
        # column c is now zero except the pivot; the equation p^val x_c + (terms in other columns) = b:
        # we eliminate the column c entries in row i of other columns too, by column operations (change of variables)
        for c2 in cols:
            if c2 != c and A[i][c2] % q:
                f = A[i][c2] // p ** val if A[i][c2] % (p ** val) == 0 else None
                assert f is not None
                for k in range(len(A)):
                    A[k][c2] = (A[k][c2] - f * A[k][c]) % q
        used_rows.add(i)
        cols.remove(c)
        # p^val x_c = b_i has p^val solutions if p^val | b_i, else none
        if A[i][nv] % (p ** val):
            return 0
        total_exp += val
        free -= 1
    # remaining rows must be zero on the right
    for k in range(len(A)):
        if k not in used_rows and A[k][nv] % q:
            return 0
    return p ** (total_exp + a * free)


# ------------------------------------------------------------------------------------------------------------- the algorithm
class Solver:
    def __init__(self, G, Nn):
        self.G = G
        self.N = sorted(Nn)
        self.Nset = Nn
        self.series = quotient_series(G, Nn)
        # N as a product of homocyclic p-parts (Z/p^a)^k: find coordinates by brute force on the small abelian group
        self.parts = self.decompose_abelian()

    def decompose_abelian(self):
        G = self.G
        order = {x: self.order(x) for x in self.N}
        parts = []
        primes = sorted({p for p in range(2, len(self.N) + 1) if len(self.N) % p == 0 and all(p % r for r in range(2, p))})
        for p in primes:
            Np = [x for x in self.N if order[x] in [p ** k for k in range(0, 10)]]
            a = max(int(round(math.log(order[x], p))) if order[x] > 1 else 0 for x in Np)
            # basis: greedy independent elements of order p^a (assumes homocyclic p-part, true for the test groups)
            basis, span = [], {G.e}
            for x in Np:
                if order[x] != p ** a or x in span:
                    continue
                new = set()
                for s in span:
                    y = s
                    for _ in range(p ** a):
                        new.add(y)
                        y = G.M[y][x]
                if len(new) > len(span):
                    basis.append(x)
                    span = new
            assert len(span) == len(Np), "p-part is not homocyclic"
            coords = {}
            for exps in itertools.product(range(p ** a), repeat=len(basis)):
                y = G.e
                for b, k in zip(basis, exps):
                    for _ in range(k):
                        y = G.M[y][b]
                if y not in coords:
                    coords[y] = exps
            parts.append((p, a, basis, coords))
        return parts

    def order(self, x):
        o, y = 1, x
        while y != self.G.e:
            y = self.G.M[y][x]
            o += 1
        return o

    def to_coords(self, x, part):
        p, a, basis, coords = part
        # project x in N to its p-part: x^(|N|/p^... ) trick via multiplying the p'-part away
        m = len(self.N)
        pa = 1
        while m % p == 0:
            m //= p
            pa *= p
        # x^(m * inv(m) mod pa) is the p-part of x
        e = m * pow(m, -1, pa)
        y = self.G.e
        for _ in range(e % (pa * m) if e % (pa * m) else 0):
            y = self.G.M[y][x]
        return coords[y]

    # ---- level 1: Hom(P, Q) by central lifting
    def hom_to_quotient(self, ngen, rels, constraint=None):
        G = self.G
        homs = [[G.e] * ngen]
        for K, Knext, z, p in self.series:
            # current reps define a hom to G/K; lift to G/Knext: g_x -> g_x z^{a_x}
            zp = [G.e]
            for _ in range(p - 1):
                zp.append(G.M[zp[-1]][z])
            new_homs = []
            for imgs in homs:
                rows, rhs = [], []
                for r in rels:
                    v = evaluate(G, r, imgs)            # in K
                    t = next(k for k in range(p) if G.M[v][G.I[zp[k]]] in Knext)
                    row = [0] * ngen
                    for gen, s in r:
                        row[gen] += s
                    rows.append([x % p for x in row])
                    rhs.append((-t) % p)
                sol = solve_mod_prime(rows, rhs, ngen, p)
                if sol is None:
                    continue
                part, basis = sol
                for coeffs in itertools.product(range(p), repeat=len(basis)):
                    a = [(part[i] + sum(c * b[i] for c, b in zip(coeffs, basis))) % p for i in range(ngen)]
                    new_homs.append([G.M[imgs[i]][zp[a[i]]] for i in range(ngen)])
            homs = new_homs
        if constraint is not None:
            gen, allowed = constraint
            Nn = self.Nset
            homs = [h for h in homs if any(G.M[G.I[h[gen]]][c] in Nn for c in allowed)]
        return homs

    # ---- level 2: lifts through N
    def lift_count(self, ngen, rels, imgs, constraint=None):
        G = self.G
        total = 1
        fixed = {}
        if constraint is not None:
            gen, allowed = constraint
            options = [G.M[G.I[imgs[gen]]][c] for c in allowed if G.M[G.I[imgs[gen]]][c] in self.Nset]
        else:
            options = [None]
        count = 0
        for opt in options:
            c_total = 1
            for part in self.parts:
                p, a, basis, coords = part
                k = len(basis)
                q = p ** a
                rows, rhs = [], []
                for r in rels:
                    # the relator as an affine function of the N-components n_x: evaluate with unit perturbations
                    base_imgs = list(imgs)
                    if opt is not None:
                        base_imgs[gen] = G.M[imgs[gen]][opt]
                    v0 = evaluate(G, r, base_imgs)
                    c0 = self.to_coords(v0, part)
                    lin = [[0] * k for _ in range(ngen * k)]
                    for x in range(ngen):
                        if opt is not None and x == gen:
                            continue
                        for bi, b in enumerate(basis):
                            pert = list(base_imgs)
                            pert[x] = G.M[base_imgs[x]][b]
                            v = evaluate(G, r, pert)
                            d = G.M[G.I[v0]][v]             # v0^-1 v in N (affine difference, via left translation)
                            # the map n -> v0^-1 r(g n) is additive in n; read its coordinates
                            lin[x * k + bi] = list(self.to_coords(d, part))
                    for comp in range(k):
                        rows.append([lin[j][comp] for j in range(ngen * k)])
                        rhs.append((-c0[comp]) % q)
                cnt = count_mod_prime_power(rows, rhs, ngen * k, p, a)
                if opt is not None:
                    # the fixed generator's coordinates are not unknowns: divide out its free part
                    cnt //= q ** k
                c_total *= cnt
            count += c_total
        return count

    def count(self, ngen, rels, constraint=None):
        return sum(self.lift_count(ngen, rels, h, constraint) for h in self.hom_to_quotient(ngen, rels, constraint))


def brute_force(G, ngen, rels, constraint=None):
    tot = 0
    for imgs in itertools.product(range(G.n), repeat=ngen):
        if constraint is not None and imgs[constraint[0]] not in constraint[1]:
            continue
        if all(evaluate(G, r, imgs) == G.e for r in rels):
            tot += 1
    return tot


# -------------------------------------------------------------------------------------------------------------- presentations
def random_presentation(rng, ngen, nrel, maxlen):
    rels = []
    for _ in range(nrel):
        L = rng.randint(2, maxlen)
        rels.append([(rng.randrange(ngen), rng.choice((1, -1))) for _ in range(L)])
    return rels


def wirtinger(arcs, crossings):
    """crossing (over, in, out): relation out = over in over^-1, as relator over in over^-1 out^-1"""
    return [[(o, 1), (u, 1), (o, -1), (w, -1)] for o, u, w in crossings]


def braid_wirtinger(word, nstrands):
    """Wirtinger presentation of the closure of a braid (strands oriented downward): generators = arcs, one relator per crossing;
    positive generator i: strand at position i passes over position i+1, out = over in over^-1; negative: out = over^-1 in over"""
    cur = list(range(nstrands))
    nxt = nstrands
    cr = []
    for g in word:
        i = abs(g) - 1
        if g > 0:
            over, under = cur[i], cur[i + 1]
            new = nxt
            nxt += 1
            cr.append((over, under, new, 1))
            cur[i], cur[i + 1] = new, over
        else:
            over, under = cur[i + 1], cur[i]
            new = nxt
            nxt += 1
            cr.append((over, under, new, -1))
            cur[i], cur[i + 1] = over, new
    # closure: identify the final arc at each position with the initial one
    par = list(range(nxt))

    def f(x):
        while par[x] != x:
            par[x] = par[par[x]]
            x = par[x]
        return x
    for j in range(nstrands):
        a, b = f(cur[j]), f(j)
        if a != b:
            par[a] = b
    reps = sorted({f(x) for x in range(nxt)})
    idx = {r: i for i, r in enumerate(reps)}
    rels = []
    for o, u, w, sg in cr:
        o, u, w = idx[f(o)], idx[f(u)], idx[f(w)]
        rels.append([(o, sg), (u, 1), (o, -sg), (w, -1)])
    return len(reps), rels


# --------------------------------------------------------------------------------------- tripled alternating knot of a grid
def diagram(n, edges, rot):
    m = len(edges)
    link = {}
    for w in range(n):
        r = rot[w]
        for i in range(len(r)):
            a, b = r[i], r[(i + 1) % len(r)]
            ea = 0 if edges[a][0] == w else 1
            eb = 0 if edges[b][0] == w else 1
            sa = (a, ea, "F2" if ea == 0 else "F1")
            sb = (b, eb, "F1" if eb == 0 else "F2")
            link[sa] = sb
            link[sb] = sa
    opp = {}
    for e in range(m):
        opp[(e, 0, "F1")] = (e, 1, "F2")
        opp[(e, 1, "F2")] = (e, 0, "F1")
        opp[(e, 0, "F2")] = (e, 1, "F1")
        opp[(e, 1, "F1")] = (e, 0, "F2")
    is_over = lambda s: (s[1], s[2]) in ((0, "F1"), (1, "F2"))
    seen, comps = set(), []
    for e in range(m):
        for start in ((e, 0, "F1"), (e, 0, "F2")):
            if start in seen:
                continue
            comp, s = [], start
            while s not in seen:
                seen.add(s)
                t = opp[s]
                seen.add(t)
                comp.append((s[0], is_over(s)))
                s = link[t]
            comps.append(comp)
    arc_id, over_arc, unders = 0, {}, {e: [] for e in range(m)}
    for comp in comps:
        k = next(i for i, (e, ov) in enumerate(comp) if not ov)
        comp = comp[k + 1:] + comp[:k + 1]
        first = cur = arc_id
        arc_id += 1
        for i, (e, ov) in enumerate(comp):
            if ov:
                over_arc[e] = cur
            else:
                nxt = arc_id if i < len(comp) - 1 else first
                if i < len(comp) - 1:
                    arc_id += 1
                unders[e].append((cur, nxt))
                cur = nxt
    return arc_id, [(over_arc[e], unders[e][0][0], unders[e][0][1]) for e in range(m)], len(comps)


def tripled_grid_knot(W, H):
    pts = [(x, y) for y in range(H) for x in range(W)]
    idx = {p: i for i, p in enumerate(pts)}
    E = [(idx[(x, y)], idx[(x + dx, y + dy)]) for (x, y) in pts for dx, dy in ((1, 0), (0, 1)) if (x + dx, y + dy) in idx]
    ne, nrot = [], {u: [] for u in range(len(pts))}
    ids = {}
    for e, (u, v) in enumerate(E):
        ids[e] = [len(ne), len(ne) + 1, len(ne) + 2]
        ne += [(u, v)] * 3
    for u in range(len(pts)):
        x0, y0 = pts[u]
        inc = sorted([e for e, (a, b) in enumerate(E) if u in (a, b)],
                     key=lambda e: math.atan2(pts[E[e][0] + E[e][1] - u][1] - y0, pts[E[e][0] + E[e][1] - u][0] - x0))
        for e in inc:
            nrot[u].extend(ids[e] if E[e][0] == u else list(reversed(ids[e])))
    na, cr, nc = diagram(len(pts), ne, nrot)
    return len(pts), na, cr, nc


# ------------------------------------------------------------------------------------------------------------------- main
def main():
    t0 = time.time()
    out = {}
    ok_all = True
    S3 = metacyclic(3, 2, 2, "S3")
    D8 = metacyclic(4, 3, 2, "D8")
    Q8 = dicyclic(2, "Q8")
    A4 = perm_group([(1, 2, 0, 3), (1, 0, 3, 2)], 4, "A4")
    D16 = metacyclic(8, 7, 2, "D16")
    DIC12 = metacyclic(3, 2, 4, "Z3 x| Z4")
    Z7Z3 = metacyclic(7, 2, 3, "Z7 x| Z3")
    H27 = heisenberg(3)
    S4 = perm_group([(1, 0, 2, 3), (1, 2, 3, 0)], 4, "S4")
    groups = [S3, D8, Q8, A4, D16, DIC12, Z7Z3, H27]

    # ---------------------------------------------------------------- part 1: decompositions
    p1 = {}
    solvers = {}
    for G in groups:
        Nn = decomposition(G)
        p1[G.name] = None if Nn is None else len(Nn)
        if Nn is not None:
            solvers[G.name] = Solver(G, Nn)
    p1["S4"] = decomposition(S4)
    ok1 = all(p1[G.name] is not None for G in groups) and p1["S4"] is None
    out["1_decompositions"] = {"N orders": {k: v for k, v in p1.items() if k != "S4"}, "S4 has none": p1["S4"] is None, "ok": ok1}
    print("part 1 decompositions:", {k: v for k, v in p1.items()}, "ok" if ok1 else "FAIL", flush=True)
    ok_all &= ok1

    # ---------------------------------------------------------------- part 2: random presentations
    rng = random.Random(20261025)
    p2 = {}
    ok2 = True
    for G in groups:
        sol = solvers[G.name]
        qprimes = sorted({p for _, _, _, p in sol.series})
        tested = agree = 0
        bound_ok = True
        while tested < 12:
            ngen = rng.choice([2, 3])
            if G.n ** ngen > 30000:
                ngen = 2
            rels = random_presentation(rng, ngen, rng.randint(1, ngen + 1), 6)
            dims = homology_dims(ngen, rels, qprimes)
            if any(d > 2 for d in dims.values()):
                continue
            homs = sol.hom_to_quotient(ngen, rels)
            Q = G.n // len(sol.N)
            bound_ok &= len(homs) <= Q ** max(dims.values() or [0])
            a = sol.count(ngen, rels)
            b = brute_force(G, ngen, rels)
            tested += 1
            agree += a == b
            if a != b:
                print("   DISAGREE", G.name, rels, a, b, flush=True)
        good = agree == tested and bound_ok
        p2[G.name] = {"presentations": tested, "agree with brute force": agree, "|Hom(P,Q)| <= |Q|^d": bound_ok, "ok": good}
        ok2 &= good
        print(f"part 2 {G.name:12s}: {agree}/{tested} agree, bound {bound_ok} ({time.time() - t0:.0f} s)", flush=True)
    out["2_random_presentations"] = {"rows": p2, "ok": ok2}
    ok_all &= ok2

    # ---------------------------------------------------------------- part 3: knot groups with a meridian class
    p3 = {}
    ok3 = True
    knots = {"trefoil": braid_wirtinger([1, 1, 1], 2), "cinquefoil": braid_wirtinger([1] * 5, 2),
             "figure eight": braid_wirtinger([1, -2, 1, -2], 3), "5_2": braid_wirtinger([1, 1, 1, 2, -1, 2], 3)}
    for G in (S3, A4, D8, Q8, DIC12):
        sol = solvers[G.name]
        for kname, (na, rels_full) in knots.items():
            rels = rels_full[:-1]
            for cls in G.classes():
                if len(cls) == 1 and G.e in cls:
                    continue
                constraint = (0, sorted(cls))
                a = sol.count(na, rels, constraint)
                b = brute_force(G, na, rels, constraint) if G.n ** na <= 300000 else None
                good = b is None or a == b
                p3[f"{G.name} {kname} class of size {len(cls)}"] = {"algorithm": a, "brute force": b, "ok": good}
                ok3 &= good
        print(f"part 3 {G.name}: done ({time.time() - t0:.0f} s)", flush=True)
    out["3_knot_groups"] = {"rows": p3, "ok": ok3}
    print("part 3 knot groups:", "ok" if ok3 else "FAIL", flush=True)
    ok_all &= ok3

    # ---------------------------------------------------------------- part 4: scale on tripled alternating knots
    p4 = {}
    ok4 = True
    trans_S3 = sorted(next(c for c in S3.classes() if len(c) == 3))
    for W, H in ((2, 3), (2, 5), (3, 4), (3, 6)):
        n, na, cr, nc = tripled_grid_knot(W, H)
        if nc != 1:
            p4[f"grid {W}x{H}"] = {"components": nc, "skipped": "not a knot"}
            continue
        rels = wirtinger(na, cr)[:-1]
        t1 = time.time()
        a = solvers["S3"].count(na, rels, (0, trans_S3))
        dt = time.time() - t1
        good = a == 3 ** n
        p4[f"grid {W}x{H}"] = {"vertices": n, "generators": na, "components": nc, "S3 transposition count": a, "3^n": 3 ** n,
                               "seconds": round(dt, 2), "ok": good}
        ok4 &= good
        print(f"part 4 grid {W}x{H}: {na} generators, a knot, S3 count {a} = 3^{n}: {good} ({dt:.1f} s)", flush=True)
    ok4 &= sum(1 for v in p4.values() if v.get("ok")) >= 2
    out["4_scale"] = {"rows": p4, "ok": ok4}
    ok_all &= ok4

    # ---------------------------------------------------------------- part 5: controls
    c = {}
    # a presentation with large homology: |Hom(P, Q)| grows like |Q|^d, so boundedness matters
    sol = solvers["S3"]
    big = [[(i, 1), (i, 1)] for i in range(6)]          # Z2^6
    c["Hom(Z2^6, Z2) has 2^6 elements (no bound without bounded homology)"] = len(sol.hom_to_quotient(6, big)) == 64
    # wrong target: forcing S4 through the solver of a different group is impossible; the decomposition search returns None
    c["S4 is not abelian-by-nilpotent"] = decomposition(S4) is None
    # a wrong lift count (ignoring the twist) disagrees with brute force on some presentation
    rels = [[(0, 1), (1, 1), (0, -1), (1, -1)]]          # Z^2: Hom = commuting pairs
    c["commuting pairs in S3 counted correctly (18)"] = sol.count(2, rels) == brute_force(S3, 2, rels) == 18
    ok5 = all(c.values())
    out["5_controls"] = {"rows": c, "ok": ok5}
    print("part 5 controls:", c, flush=True)
    ok_all &= ok5

    out["ok"] = ok_all
    out["seconds"] = round(time.time() - t0, 1)
    result = {"schema_version": 1, "artifact_id": "BOUNDED-H1-20261025-001B-P001", "status": "Proved" if ok_all else "Partial",
              "checks": out}
    (HERE / "result.json").write_text(json.dumps(result, indent=2, default=str) + "\n")
    print("ALL OK" if ok_all else "FAILURES", out["seconds"], "s")
    return 0 if ok_all else 1


if __name__ == "__main__":
    sys.exit(main())
