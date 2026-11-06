"""Check for SL23-BOUNDED-20261025-001A-P001: SL(2,3) counting is polynomial with bounded homology.

Standard library only; imports nothing from other proofs. Parts:
  1. structure: SL(2,3) has centre A = {I, -I}, N = Q8 normal with N/A elementary abelian and G/N = Z3; its normal subgroups are
     1, A, Q8, G, so no abelian normal subgroup has a nilpotent quotient (not abelian-by-nilpotent); Fitting height 2. Q8, D8 and
     Z2 x SL(2,3) also satisfy the hypotheses (the last with m = 2); S4 does not (control);
  2. Gauss sums of quadratic polynomials over F2 by pairwise elimination agree with brute force;
  3. the algorithm (maps to G/N, affine twisted lifts through N/A, quadratic obstruction through A, Gauss sums) agrees with brute
     force on integral surgeries S3_p(K) (balanced presentations) for four groups, seven slopes and five knots, and on random
     presentations; at random points every relator sign is checked to be a polynomial of degree at most 2;
  4. scale: SL(2,3) on S3_6 of connected sums of figure-eight knots, with the lift-space dimensions, brute force where feasible;
  5. controls: dropping the obstruction overcounts on closed manifolds with H^2(M; F2) != 0.
Writes result.json next to this file with --write."""
import itertools
import json
import random
import sys
import time
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent


# ------------------------------------------------------------------------------------------------------------------ groups
class Group:
    def __init__(self, elems, mul):
        self.E = list(elems)
        idx = {e: i for i, e in enumerate(self.E)}
        self.M = [[idx[mul(a, b)] for b in self.E] for a in self.E]
        self.n = len(self.E)
        self.I = next(i for i in range(self.n) if all(self.M[i][j] == j for j in range(self.n)))
        self.INV = [next(b for b in range(self.n) if self.M[a][b] == self.I) for a in range(self.n)]

    def pw(self, a, e):
        r = self.I
        if e < 0:
            a, e = self.INV[a], -e
        for _ in range(e):
            r = self.M[r][a]
        return r

    def word(self, w, vals):
        g = self.I
        for x, e in w:
            g = self.M[g][self.pw(vals[x], e)]
        return g

    def gen(self, gens):
        S, fr = {self.I}, [self.I]
        while fr:
            a = fr.pop()
            for g in gens:
                b = self.M[a][g]
                if b not in S:
                    S.add(b)
                    fr.append(b)
        return frozenset(S)

    def order(self, a):
        k, x = 1, a
        while x != self.I:
            x = self.M[x][a]
            k += 1
        return k

    def center(self):
        return [z for z in range(self.n) if all(self.M[z][g] == self.M[g][z] for g in range(self.n))]

    def is_normal(self, H):
        return all(self.M[self.M[g][h]][self.INV[g]] in H for g in range(self.n) for h in H)

    def normal_subgroups(self):
        classes = []
        seen = set()
        for a in range(self.n):
            if a not in seen:
                c = frozenset(self.M[self.M[g][a]][self.INV[g]] for g in range(self.n))
                seen |= c
                classes.append(c)
        subs = {frozenset([self.I])}
        frontier = list(subs)
        while frontier:
            H = frontier.pop()
            for c in classes:
                K = self.gen(list(H | c))
                if K not in subs:
                    subs.add(K)
                    frontier.append(K)
        return subs

    def quotient_is_nilpotent(self, H):
        """G/H nilpotent iff every Sylow subgroup of G/H is normal (unique): count elements of p-power order in G/H"""
        cosets = {}
        for g in range(self.n):
            cosets.setdefault(frozenset(self.M[g][h] for h in H), g)
        reps = list(cosets.values())
        order = len(reps)
        coset_of = {}
        for key, g in cosets.items():
            for x in key:
                coset_of[x] = g

        def qorder(g):
            k, x = 1, coset_of[g]
            while coset_of[x] != coset_of[self.I]:
                x = coset_of[self.M[x][g]]
                k += 1
            return k
        for p in {p for p in range(2, order + 1) if order % p == 0 and all(p % d for d in range(2, p))}:
            pp = 1
            while order % (pp * p) == 0:
                pp *= p
            n_p = sum(1 for g in reps if all(q == p for q in prime_factors(qorder(g))))
            if n_p != pp:
                return False
        return True

    def is_abelian(self, H):
        return all(self.M[a][b] == self.M[b][a] for a in H for b in H)


def prime_factors(n):
    out, d = [], 2
    while n > 1:
        while n % d == 0:
            out.append(d)
            n //= d
        d += 1
    return out


def m3(a, b):
    return ((a[0] * b[0] + a[1] * b[2]) % 3, (a[0] * b[1] + a[1] * b[3]) % 3,
            (a[2] * b[0] + a[3] * b[2]) % 3, (a[2] * b[1] + a[3] * b[3]) % 3)


def perm_mul(a, b):
    return tuple(a[b[i]] for i in range(4))


class Structure:
    """A central elementary abelian 2-group, N normal containing A with N/A elementary abelian, G/N cyclic generated by top_gen"""

    def __init__(self, G, A, N, top_gen, top_order):
        self.G, self.A, self.N = G, sorted(A), sorted(N)
        assert set(A) <= set(G.center()) and G.is_normal(frozenset(N)) and set(A) <= set(N)
        assert all(G.M[a][a] == G.I for a in A) and all(G.M[x][x] in set(A) for x in N)
        assert all(G.M[G.M[x][y]][G.INV[G.M[y][x]]] in set(A) for x in N for y in N)
        self.Abasis = self._basis(A, [G.I])
        self.Nbasis = self._basis(N, A)
        self.m, self.k = len(self.Abasis), len(self.Nbasis)
        self.a_bits = {}
        for bits in itertools.product((0, 1), repeat=self.m):
            g = G.I
            for b, e in zip(bits, self.Abasis):
                if b:
                    g = G.M[g][e]
            self.a_bits[g] = bits
        self.ntil = {}
        for bits in itertools.product((0, 1), repeat=self.k):
            g = G.I
            for b, e in zip(bits, self.Nbasis):
                if b:
                    g = G.M[g][e]
            self.ntil[bits] = g
        self.q = top_order
        self.top = [G.pw(top_gen, j) for j in range(top_order)]
        self.nf = {}
        for j, t in enumerate(self.top):
            for v, nv in self.ntil.items():
                for a, bits in self.a_bits.items():
                    self.nf[G.M[G.M[t][nv]][a]] = (j, v, bits)
        assert len(self.nf) == G.n

    def _basis(self, H, base):
        basis, span = [], self.G.gen(list(base))
        for x in H:
            if x not in span:
                basis.append(x)
                span = self.G.gen(list(base) + basis)
        return basis


# ------------------------------------------------------------------------------------------------------------ linear algebra
def nullspace_mod(rows, n, p):
    A = [r[:] for r in rows]
    piv, rk = [], 0
    for c in range(n):
        pr = next((i for i in range(rk, len(A)) if A[i][c] % p), None)
        if pr is None:
            continue
        A[rk], A[pr] = A[pr], A[rk]
        inv = pow(A[rk][c], p - 2, p)
        A[rk] = [(x * inv) % p for x in A[rk]]
        for i in range(len(A)):
            if i != rk and A[i][c] % p:
                f = A[i][c]
                A[i] = [(x - f * y) % p for x, y in zip(A[i], A[rk])]
        piv.append(c)
        rk += 1
    basis = []
    for fc in (c for c in range(n) if c not in piv):
        v = [0] * n
        v[fc] = 1
        for i, pc in enumerate(piv):
            v[pc] = (-A[i][fc]) % p
        basis.append(v)
    return basis


def affine_solve_f2(rows, rhs, n):
    A = [r[:] + [b] for r, b in zip(rows, rhs)]
    piv, rk = [], 0
    for c in range(n):
        pr = next((i for i in range(rk, len(A)) if A[i][c]), None)
        if pr is None:
            continue
        A[rk], A[pr] = A[pr], A[rk]
        for i in range(len(A)):
            if i != rk and A[i][c]:
                A[i] = [x ^ y for x, y in zip(A[i], A[rk])]
        piv.append(c)
        rk += 1
    if any(row[n] and not any(row[:n]) for row in A):
        return None
    part = [0] * n
    for i, pc in enumerate(piv):
        part[pc] = A[i][n]
    basis = []
    for fc in (c for c in range(n) if c not in piv):
        v = [0] * n
        v[fc] = 1
        for i, pc in enumerate(piv):
            v[pc] = A[i][fc]
        basis.append(v)
    return part, basis


def span_mod(basis, p, n):
    for co in itertools.product(range(p), repeat=len(basis)):
        yield [sum(c * b[i] for c, b in zip(co, basis)) % p for i in range(n)]


def gauss_sum(nvar, quad, lin, const):
    """sum_{u in F2^nvar} (-1)^(sum_{(i,j) in quad} u_i u_j + sum_{i in lin} u_i + const), by eliminating pairs:
    sum_{u_i, u_j} (-1)^(u_i (u_j + A) + u_j B) = 2 (-1)^(A B)"""
    quad = {tuple(sorted(e)) for e in quad}
    lin = set(lin)
    adj = {i: set() for i in range(nvar)}
    for i, j in quad:
        adj[i].add(j)
        adj[j].add(i)
    alive, scale, c = set(range(nvar)), 1, const % 2
    while True:
        pair = next(((i, j) for i in alive for j in adj[i]), None)
        if pair is None:
            break
        i, j = pair
        A_l, A_c = set(adj[i]) - {j}, int(i in lin)
        B_l, B_c = set(adj[j]) - {i}, int(j in lin)
        for x in list(adj[i]):
            adj[x].discard(i)
        for x in list(adj[j]):
            adj[x].discard(j)
        adj[i], adj[j] = set(), set()
        lin.discard(i)
        lin.discard(j)
        alive.discard(i)
        alive.discard(j)
        c ^= A_c & B_c
        if B_c:
            lin ^= A_l
        if A_c:
            lin ^= B_l
        for a in A_l:
            for b in B_l:
                if a == b:
                    lin ^= {a}
                elif b in adj[a]:
                    adj[a].discard(b)
                    adj[b].discard(a)
                else:
                    adj[a].add(b)
                    adj[b].add(a)
        scale *= 2
    if lin & alive:
        return 0
    return scale * (2 ** len(alive)) * (-1) ** c


# ----------------------------------------------------------------------------------------------------------- the algorithm
def count(S, ngen, rels, rng=None, drop_obstruction=False, stats=None):
    G, q, k, m = S.G, S.q, S.k, S.m
    E2 = [[sum(e for x, e in r if x == g) % 2 for g in range(ngen)] for r in rels]
    tops = [[0] * ngen]
    if q > 1:
        Eq = [[sum(e for x, e in r if x == g) % q for g in range(ngen)] for r in rels]
        tops = list(span_mod(nullspace_mod(Eq, ngen, q), q, ngen))
    hom_A = 2 ** (m * len(nullspace_mod(E2, ngen, 2)))
    E2T = [[E2[r][g] for r in range(len(rels))] for g in range(ngen)]
    W = list(span_mod(nullspace_mod(E2T, len(rels), 2), 2, len(rels)))
    total = 0
    for psi in tops:
        def values(bits):
            return [G.M[S.top[psi[x]]][S.ntil[tuple(bits[k * x:k * x + k])]] for x in range(ngen)]

        def normal_forms(bits):
            out = []
            for r in rels:
                j, v, a = S.nf[G.word(r, values(bits))]
                assert j == 0
                out.append((v, a))
            return out
        nv = k * ngen
        f0 = normal_forms([0] * nv)
        cols = [normal_forms([int(t == i) for t in range(nv)]) for i in range(nv)]
        rows, rhs = [], []
        for ri in range(len(rels)):
            for comp in range(k):
                rows.append([cols[i][ri][0][comp] ^ f0[ri][0][comp] for i in range(nv)])
                rhs.append(f0[ri][0][comp])
        sol = affine_solve_f2(rows, rhs, nv)
        if sol is None:
            continue
        part, Kb = sol
        D = len(Kb)
        if stats is not None:
            stats.append(D)

        def point(u):
            return [(part[t] + sum(u[i] * Kb[i][t] for i in range(D))) % 2 for t in range(nv)]

        def signs(u):
            out = normal_forms(point(u))
            assert all(v == tuple([0] * k) for v, a in out), "a point of the lift space is not a lift"
            return [a for v, a in out]
        if drop_obstruction:
            total += 2 ** D
            continue
        g0 = signs([0] * D)
        g1 = [signs([int(t == i) for t in range(D)]) for i in range(D)]
        g2 = {(i, j): signs([int(t in (i, j)) for t in range(D)]) for i in range(D) for j in range(i + 1, D)}
        if rng is not None and D:
            for _ in range(6):
                u = [rng.randint(0, 1) for _ in range(D)]
                direct = signs(u)
                ones = [i for i in range(D) if u[i]]
                for ri in range(len(rels)):
                    for c in range(m):
                        pred = g0[ri][c]
                        for i in ones:
                            pred ^= g1[i][ri][c] ^ g0[ri][c]
                        for x_, y_ in itertools.combinations(ones, 2):
                            pred ^= g2[(x_, y_)][ri][c] ^ g1[x_][ri][c] ^ g1[y_][ri][c] ^ g0[ri][c]
                        assert pred == direct[ri][c], "relator sign is not quadratic"
        acc = 0
        for ws in itertools.product(W, repeat=m):
            def dot(vec):
                return sum(ws[c][ri] * vec[ri][c] for ri in range(len(rels)) for c in range(m)) % 2
            c0 = dot(g0)
            lin = {i for i in range(D) if dot(g1[i]) ^ c0}
            quad = {(i, j) for (i, j), val in g2.items() if dot(val) ^ dot(g1[i]) ^ dot(g1[j]) ^ c0}
            acc += gauss_sum(D, quad, lin, c0)
        assert acc % (len(W) ** m) == 0
        total += acc // (len(W) ** m)
    return hom_A * total


# --------------------------------------------------------------------------------------------- knots and surgery presentations
def gauss_from_braid(word, nstrands):
    visits, p = [], 0
    while True:
        for j, g in enumerate(word):
            i = abs(g) - 1
            if p in (i, i + 1):
                left = p == i
                visits.append((j, (left and g > 0) or (not left and g < 0), 1 if g > 0 else -1))
                p = i + 1 if left else i
        if p == 0:
            break
    assert all(c == 2 for c in Counter(v[0] for v in visits).values()) and len(visits) == 2 * len(word)
    return visits


def connected_sum(a, b):
    off = 1 + max(v[0] for v in a)
    return list(a) + [(c + off, ov, s) for c, ov, s in b]


def wirtinger(code):
    k = max(i for i, v in enumerate(code) if not v[1])
    code = code[k + 1:] + code[:k + 1]
    U = sum(1 for v in code if not v[1])
    a, over, sign, order = 0, {}, {}, []
    for c, ov, s in code:
        sign[c] = s
        if ov:
            over[c] = a
        else:
            order.append((c, a, (a + 1) % U))
            a += 1
    return U, [(over[c], i, j, sign[c]) for c, i, j in order]


def surgery_presentation(code, p):
    """balanced: the Wirtinger relators but one, and mu^p lambda with the preferred longitude"""
    U, cr = wirtinger(code)
    rels = [[(o, -s), (i, 1), (o, s), (j, -1)] for o, i, j, s in cr[:-1]]
    w = sum(s for *_, s in cr)
    lam = [(o, s) for o, i, j, s in cr] + ([(0, -1)] * w if w >= 0 else [(0, 1)] * (-w))
    rels.append(([(0, 1)] * p if p >= 0 else [(0, -1)] * (-p)) + lam)
    return U, rels


def brute_surgery(G, code, p):
    U, cr = wirtinger(code)
    w = sum(s for *_, s in cr)
    total = 0
    for m in range(G.n):
        cls = sorted({G.M[G.M[g][m]][G.INV[g]] for g in range(G.n)})
        val = [None] * U
        val[0] = m

        def rec(k_):
            nonlocal total
            if k_ == len(cr):
                P = G.I
                for o, i, j, s in cr:
                    P = G.M[P][G.pw(val[o], s)]
                total += G.M[G.pw(m, p)][G.M[P][G.pw(val[0], -w)]] == G.I
                return
            o, i, j, s = cr[k_]
            for x in ([val[o]] if val[o] is not None else cls):
                new_o = val[o] is None
                if new_o:
                    val[o] = x
                g = G.pw(x, s)
                nv = G.M[G.M[G.INV[g]][val[i]]][g]
                new_j = val[j] is None
                if new_j:
                    val[j] = nv
                if val[j] == nv:
                    rec(k_ + 1)
                if new_j:
                    val[j] = None
                if new_o:
                    val[o] = None
        rec(0)
    return total


# ------------------------------------------------------------------------------------------------------------------ main
def main():
    t0 = time.time()
    out, ok_all = {}, True
    rng = random.Random(20261025)

    # part 1: structures
    SL = Group([m for m in itertools.product(range(3), repeat=4) if (m[0] * m[3] - m[1] * m[2]) % 3 == 1], m3)
    A_sl = [a for a in range(SL.n) if SL.order(a) <= 2]
    Q8_sl = [a for a in range(SL.n) if SL.order(a) in (1, 2, 4)]
    tau = next(a for a in range(SL.n) if SL.order(a) == 3)
    S_SL = Structure(SL, A_sl, Q8_sl, tau, 3)
    normals = SL.normal_subgroups()
    p1 = {"|SL(2,3)|": SL.n, "centre": len(SL.center()), "normal subgroup orders": sorted(len(H) for H in normals),
          "abelian normal subgroups with nilpotent quotient": [len(H) for H in normals if SL.is_abelian(H) and SL.quotient_is_nilpotent(H)],
          "Q8 nilpotent and SL(2,3)/Q8 nilpotent (Fitting height 2)": SL.quotient_is_nilpotent(frozenset(Q8_sl))}
    Q8 = Group([SL.E[a] for a in Q8_sl], m3)
    S_Q8 = Structure(Q8, [a for a in range(8) if Q8.order(a) <= 2], list(range(8)), Q8.I, 1)
    S4 = Group(list(itertools.permutations(range(4))), perm_mul)
    D8set = S4.gen([S4.E.index((1, 2, 3, 0)), S4.E.index((2, 1, 0, 3))])
    D8 = Group([S4.E[i] for i in sorted(D8set)], perm_mul)
    S_D8 = Structure(D8, D8.center(), list(range(8)), D8.I, 1)
    Z2SL = Group([(s, g) for s in (0, 1) for g in SL.E], lambda a, b: ((a[0] + b[0]) % 2, m3(a[1], b[1])))
    N2 = [i for i, (s, g) in enumerate(Z2SL.E) if SL.order(SL.E.index(g)) in (1, 2, 4)]
    tau2 = Z2SL.E.index((0, SL.E[tau]))
    S_Z2SL = Structure(Z2SL, Z2SL.center(), N2, tau2, 3)
    # S4: central subgroups are trivial, so N/1 would have to be elementary abelian with nilpotent quotient
    s4_struct = [len(H) for H in S4.normal_subgroups()
                 if all(S4.M[x][x] == S4.I for x in H) and S4.is_abelian(H) and S4.quotient_is_nilpotent(H)]
    p1["S4: normal elementary abelian 2-subgroups with nilpotent quotient (A = 1)"] = s4_struct
    p1["structures (|G|, m, dim N/A, |G/N|)"] = {nm: (S.G.n, S.m, S.k, S.q) for nm, S in
                                                (("SL(2,3)", S_SL), ("Q8", S_Q8), ("D8", S_D8), ("Z2 x SL(2,3)", S_Z2SL))}
    ok1 = (SL.n == 24 and p1["centre"] == 2 and p1["normal subgroup orders"] == [1, 2, 8, 24]
           and p1["abelian normal subgroups with nilpotent quotient"] == [] and p1["Q8 nilpotent and SL(2,3)/Q8 nilpotent (Fitting height 2)"]
           and s4_struct == [] and S_Z2SL.m == 2)
    p1["ok"] = ok1
    out["1_structure"] = p1
    print("part 1:", p1, flush=True)
    ok_all &= ok1

    # part 2: Gauss sums
    ok2 = True
    for _ in range(400):
        n = rng.randint(0, 8)
        quad = {(i, j) for i in range(n) for j in range(i + 1, n) if rng.random() < 0.4}
        lin = {i for i in range(n) if rng.random() < 0.5}
        c = rng.randint(0, 1)
        bf = sum((-1) ** ((sum(u[i] * u[j] for i, j in quad) + sum(u[i] for i in lin) + c) % 2)
                 for u in itertools.product((0, 1), repeat=n))
        ok2 &= gauss_sum(n, quad, lin, c) == bf
    out["2_gauss_sums"] = {"random quadratic polynomials": 400, "ok": ok2}
    print("part 2: Gauss sums", ok2, flush=True)
    ok_all &= ok2

    # part 3: algorithm vs brute force
    f8 = gauss_from_braid([1, -2, 1, -2], 3)
    knots = {"3_1": gauss_from_braid([1, 1, 1], 2), "4_1": f8, "8_18": gauss_from_braid([1, -2] * 4, 3),
             "4_1 # 4_1": connected_sum(f8, f8), "10_124": gauss_from_braid([1, 2] * 5, 3)}
    structs = {"SL(2,3)": S_SL, "Q8": S_Q8, "D8": S_D8, "Z2 x SL(2,3)": S_Z2SL}
    rows3, ok3, n3 = {}, True, 0
    for nm, S in structs.items():
        agree = 0
        for kn, code in knots.items():
            for p in (0, 1, 2, 3, 4, 6, -6):
                U, rels = surgery_presentation(code, p)
                a = count(S, U, rels, rng=rng)
                b = brute_surgery(S.G, code, p)
                agree += a == b
                n3 += 1
                if nm == "SL(2,3)":
                    rows3[f"SL(2,3) {kn} p={p}"] = [a, b]
        rnd = 0
        for _ in range(25):
            ng = rng.randint(1, 2 if S.G.n > 24 else 3)
            rels = [[(rng.randrange(ng), rng.choice((1, -1))) for _ in range(rng.randint(1, 7))]
                    for _ in range(rng.randint(max(1, ng - 1), ng + 1))]
            a = count(S, ng, rels, rng=rng)
            b = sum(1 for vals in itertools.product(range(S.G.n), repeat=ng) if all(S.G.word(r, vals) == S.G.I for r in rels))
            rnd += a == b
        rows3[f"{nm}: surgeries agreeing"] = agree
        rows3[f"{nm}: random presentations agreeing (of 25)"] = rnd
        ok3 &= agree == len(knots) * 7 and rnd == 25
        print(f"part 3 {nm}: surgeries {agree}/{len(knots) * 7}, random {rnd}/25 ({time.time() - t0:.0f} s)", flush=True)
    out["3_algorithm_vs_brute_force"] = {"rows": rows3, "ok": ok3}
    ok_all &= ok3

    # part 4: scale
    rows4, ok4 = {}, True
    codes = {1: f8}
    for kk in range(2, 13):
        codes[kk] = connected_sum(codes[kk - 1], f8)
    for kk in (1, 2, 3, 6, 9, 12):
        code = codes[kk]
        U, rels = surgery_presentation(code, 6)
        dims = []
        t1 = time.time()
        a = count(S_SL, U, rels, stats=dims)
        ta = time.time() - t1
        b = brute_surgery(SL, code, 6) if kk <= 3 else None
        rows4[f"(4_1)^{kk}, p = 6"] = {"generators": U, "lift-space dimensions": dims, "count": a, "brute force": b, "seconds": round(ta, 2)}
        ok4 &= b is None or a == b
        print(f"part 4 (4_1)^{kk}: {U} generators, lift dims {dims}, count {a}, brute {b} ({ta:.1f} s)", flush=True)
    out["4_scale"] = {"rows": rows4, "ok": ok4}
    ok_all &= ok4

    # part 5: controls
    c = {}
    U, rels = surgery_presentation(knots["3_1"], 2)
    c["dropping the obstruction overcounts on S3_2(3_1)"] = count(S_SL, U, rels, drop_obstruction=True) != brute_surgery(SL, knots["3_1"], 2)
    U, rels = surgery_presentation(knots["4_1 # 4_1"], 6)
    c["dropping the obstruction overcounts on S3_6(4_1 # 4_1)"] = count(S_SL, U, rels, drop_obstruction=True) != brute_surgery(SL, knots["4_1 # 4_1"], 6)
    U, rels = surgery_presentation(knots["8_18"], 3)
    c["no obstruction when H^2(M; F2) = 0 (S3_3(8_18)): dropping it changes nothing"] = count(S_SL, U, rels, drop_obstruction=True) == count(S_SL, U, rels)
    ok5 = all(c.values())
    out["5_controls"] = {"rows": c, "ok": ok5}
    print("part 5 controls:", c, flush=True)
    ok_all &= ok5

    out["ok"] = ok_all
    out["seconds"] = round(time.time() - t0, 1)
    result = {"schema_version": 1, "artifact_id": "SL23-BOUNDED-20261025-001A-P001", "status": "Proved" if ok_all else "Partial",
              "checks": out}
    if "--write" in sys.argv:
        (HERE / "result.json").write_text(json.dumps(result, indent=2, default=str) + "\n")
    print("ALL OK" if ok_all else "FAILURES", out["seconds"], "s")
    return 0 if ok_all else 1


if __name__ == "__main__":
    sys.exit(main())
