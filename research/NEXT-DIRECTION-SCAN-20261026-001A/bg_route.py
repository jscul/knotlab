#!/usr/bin/env python3
"""NEXT-DIRECTION-SCAN-20261026-001A (lane A): the Bulatov-Grohe route for coprime class-2-by-cyclic groups.

Abstract (algebraic) layer only: given a trilinear graded-alternating form T on V = sum_s V_s (the twisted triple product
of a manifold, as steered by Borromean moves) and a group G = N x| C_r of class (K) (p odd, r | p - 1), compare

  N_direct = #{c in H^1(B_psi) : o(c) = 0},   <o(c), w (x) z_b*> = sum_{a,a'} T(c_a, c_a', w) beta_b(a, a')

(enumerated over all c) with the Bulatov-Grohe form

  N_BG = p^(-#tests) * sum_{X : V(Gamma) -> U_s} prod_{edges uv} g(X_u - X_v),
  g(delta) = sum over one edge's private variables of e_p(F_edge(delta, ., .)) = |U_3| p^(dim U_2 - rank K(delta)),

where U_s = B_s (+) A*_{-s} collects, for the V-character s, the cocycle coordinates and the test coordinates.
The weight matrix W[x, y] = g(x - y) is rank one iff g is constant iff K = 0.

Run:  /home/jscul/p-vs-np-contact-first/.venv/bin/python -B bg_route.py   (numpy; about 1-3 minutes)
Writes bg_route_result.json next to this file.
"""
import itertools
import json
import math
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent


# ---------------------------------------------------------------- groups of class (K), p odd, characters zeta^s
class Group:
    """B basis e_a with character exponents cB[a]; A basis z_b with exponents cA[b]; kappa[(a, a')] (a < a') in A.
    beta = strictly upper-triangular part of kappa (for p odd the class of beta is determined by kappa)."""

    def __init__(self, name, p, r, cB, cA, kappa):
        self.name, self.p, self.r = name, p, r
        self.cB = [x % r for x in cB]
        self.cA = [x % r for x in cA]
        self.kappa = {}
        for (a, a2), vec in kappa.items():
            assert a < a2 and len(vec) == len(cA)
            for b, v in enumerate(vec):
                if v % p:
                    assert self.cA[b] == (self.cB[a] + self.cB[a2]) % r, f"{name}: kappa not equivariant"
            self.kappa[(a, a2)] = [v % p for v in vec]

    def beta(self, a, a2, b):
        if a < a2 and (a, a2) in self.kappa:
            return self.kappa[(a, a2)][b]
        return 0

    def hard_pairs(self):
        """(s, t) with s, t, s + t nonzero mod r and kappa_{s,t} != 0"""
        out = set()
        for (a, a2), vec in self.kappa.items():
            s, t = self.cB[a], self.cB[a2]
            if any(vec) and s and t and (s + t) % self.r:
                out.add(tuple(sorted((s, t))))
        return sorted(out)


def perm_sign(seq):
    seq = list(seq)
    s = 1
    for i in range(len(seq)):
        for j in range(i + 1, len(seq)):
            if seq[i] > seq[j]:
                s = -s
    return s


def Tval(T, i, j, k):
    if i == j or j == k or i == k:
        return 0
    key = tuple(sorted((i, j, k)))
    v = T.get(key, 0)
    return perm_sign((i, j, k)) * v if v else 0


def add_alt(T, i, j, k, c):
    """T += c * (e_i* wedge e_j* wedge e_k*) restricted to the slot order (i, j, k)"""
    key = tuple(sorted((i, j, k)))
    T[key] = T.get(key, 0) + perm_sign((i, j, k)) * c


# ---------------------------------------------------------------- the direct count
def variables(G, vchar, k):
    r = G.r
    cvars = [(a, i) for a in range(len(G.cB)) for i in range(len(vchar)) if vchar[i] == (k * G.cB[a]) % r]
    tests = [(b, j) for b in range(len(G.cA)) for j in range(len(vchar)) if vchar[j] == (-k * G.cA[b]) % r]
    return cvars, tests


def quad_forms(G, vchar, T, k):
    p = G.p
    cvars, tests = variables(G, vchar, k)
    D = len(cvars)
    Ms = []
    for (b, j) in tests:
        M = np.zeros((D, D), dtype=np.int64)
        for x, (a, i) in enumerate(cvars):
            for y, (a2, i2) in enumerate(cvars):
                be = G.beta(a, a2, b)
                if be:
                    t = Tval(T, i, i2, j)
                    if t:
                        M[x, y] = (M[x, y] + be * t) % p
        if M.any():
            Ms.append(M)
    return cvars, tests, Ms


def direct_count(G, vchar, T, k, limit=12_000_000):
    """#{c : every obstruction coordinate vanishes}, enumerating all c (None if p^D > limit)"""
    p = G.p
    cvars, tests, Ms = quad_forms(G, vchar, T, k)
    D = len(cvars)
    total = p ** D
    if total > limit:
        return None
    if not Ms:
        return total
    good = 0
    CH = 1 << 20
    pw = p ** np.arange(D, dtype=np.int64)
    for start in range(0, total, CH):
        idx = np.arange(start, min(total, start + CH), dtype=np.int64)
        X = (idx[:, None] // pw[None, :]) % p
        ok = np.ones(len(idx), dtype=bool)
        for M in Ms:
            q = ((X @ M) * X).sum(axis=1) % p
            ok &= q == 0
        good += int(ok.sum())
    return good


# ---------------------------------------------------------------- the Bulatov-Grohe side
def single_edge(G, chars3, k):
    """single-edge instance: V basis (l, y, t) with characters chars3 and T(l, y, t) = 1. Returns (U-coordinate lists,
    function K(delta) giving the matrix of the bilinear form (Xi_y, Xi_t) -> F(delta, Xi_y, Xi_t))."""
    p, r = G.p, G.r
    vchar = list(chars3)
    T = {}
    add_alt(T, 0, 1, 2, 1)
    U = []
    for i in range(3):
        U.append([("c", a) for a in range(len(G.cB)) if vchar[i] == (k * G.cB[a]) % r] +
                 [("w", b) for b in range(len(G.cA)) if vchar[i] == (-k * G.cA[b]) % r])
    pos = [{v: n for n, v in enumerate(U[i])} for i in range(3)]
    # monomials c_{a,i} c_{a2,i2} w_{b,j}: coefficient T(i, i2, j) beta_b(a, a2)
    mono = []
    for b in range(len(G.cA)):
        for j in range(3):
            if vchar[j] != (-k * G.cA[b]) % r:
                continue
            for a in range(len(G.cB)):
                for a2 in range(len(G.cB)):
                    be = G.beta(a, a2, b)
                    if not be:
                        continue
                    for i in range(3):
                        for i2 in range(3):
                            if vchar[i] != (k * G.cB[a]) % r or vchar[i2] != (k * G.cB[a2]) % r:
                                continue
                            t = Tval(T, i, i2, j)
                            if t:
                                slots = {i: ("c", a), i2: ("c", a2), j: ("w", b)}
                                assert len(slots) == 3
                                mono.append((be * t % p, pos[0][slots[0]], pos[1][slots[1]], pos[2][slots[2]]))

    def K(delta):
        M = np.zeros((len(U[1]), len(U[2])), dtype=np.int64)
        for c, u0, u1, u2 in mono:
            M[u1, u2] = (M[u1, u2] + c * delta[u0]) % p
        return M
    return U, K


def rank_mod_p(M, p):
    M = [list(map(int, row)) for row in np.asarray(M) % p]
    if not M or not M[0]:
        return 0
    rk, rows, cols = 0, len(M), len(M[0])
    for c in range(cols):
        piv = next((i for i in range(rk, rows) if M[i][c] % p), None)
        if piv is None:
            continue
        M[rk], M[piv] = M[piv], M[rk]
        iv = pow(M[rk][c], p - 2, p)
        M[rk] = [x * iv % p for x in M[rk]]
        for i in range(rows):
            if i != rk and M[i][c]:
                f = M[i][c]
                M[i] = [(x - f * y) % p for x, y in zip(M[i], M[rk])]
        rk += 1
    return rk


def g_table(G, chars3, k, explicit=True):
    """g(delta) for every delta in U_l: the rank formula |U_t| p^(dim U_y - rank K(delta)); if small, also the explicit
    character sum (vectorized), which must agree (equal counts on the nonzero residues)."""
    p = G.p
    U, K = single_edge(G, chars3, k)
    d0, d1, d2 = map(len, U)
    table = {}
    do_explicit = explicit and p ** (d1 + d2) <= 400000 and p ** d0 <= 400
    if do_explicit:
        Xa = np.array(list(itertools.product(range(p), repeat=d1)), dtype=np.int64).reshape(p ** d1, d1)
        Ya = np.array(list(itertools.product(range(p), repeat=d2)), dtype=np.int64).reshape(p ** d2, d2)
    for delta in itertools.product(range(p), repeat=d0):
        Kd = K(delta)
        rk = rank_mod_p(Kd, p) if d1 and d2 else 0
        val = p ** d2 * p ** (d1 - rk)
        if do_explicit:
            vals = ((Xa @ Kd) @ Ya.T) % p if d1 and d2 else np.zeros((len(Xa), len(Ya)), dtype=np.int64)
            cnt = np.bincount(vals.ravel(), minlength=p)
            assert len(set(cnt[1:].tolist())) <= 1, "character sum is not real"
            assert int(cnt[0] - cnt[1]) == val, ("g mismatch", cnt, val)
        table[delta] = (val, rk)
    return U, table


def weight_matrix(G, chars3, k):
    p = G.p
    U, table = g_table(G, chars3, k, explicit=False)
    d0 = len(U[0])
    states = list(itertools.product(range(p), repeat=d0))
    S = len(states)
    st = np.array(states, dtype=np.int64).reshape(S, d0)
    W = np.zeros((S, S), dtype=np.int64)
    pw = p ** np.arange(d0, dtype=np.int64)
    # delta index for every pair
    gv = np.zeros(p ** d0 if d0 else 1, dtype=np.int64)
    for delta, (v, _) in table.items():
        gv[int(np.dot(np.array(delta, dtype=np.int64), pw)) if d0 else 0] = v
    if d0:
        diff = (st[:, None, :] - st[None, :, :]) % p
        W = gv[(diff * pw).sum(axis=2)]
    else:
        W = gv.reshape(1, 1)
    return W


def bg_sum(G, chars3, k, n, edges, ntests):
    """N_BG = p^-ntests * sum_X prod_e g(X_u - X_v) (exact integer)"""
    p = G.p
    U, _ = single_edge(G, chars3, k)
    S = p ** len(U[0])
    if S ** n > 3_000_000:
        # only constant weights are evaluated in closed form at this size
        U, table = g_table(G, chars3, k, explicit=False)
        vals = {v for v, _ in table.values()}
        if len(vals) != 1:
            return None
        total = S ** n * vals.pop() ** len(edges)
        den = p ** ntests
        assert total % den == 0
        return total // den
    W = weight_matrix(G, chars3, k)
    letters = "abcdefgh"[:n]
    ops, subs = [], []
    for (u, v) in edges:
        if u == v:
            ops.append(np.diag(W).astype(object))
            subs.append(letters[u])
        else:
            ops.append(W.astype(object))
            subs.append(letters[u] + letters[v])
    for x in range(n):   # make sure every vertex is summed
        ops.append(np.ones(W.shape[0], dtype=object))
        subs.append(letters[x])
    total = np.einsum(",".join(subs) + "->", *ops, optimize=False)
    total = int(total)
    den = p ** ntests
    assert total % den == 0, ("non-integer", total, den)
    return total // den


# ---------------------------------------------------------------- gadgets
def gadget(pattern, chars3, n, edges):
    """returns (vchar, T, chars of the single-edge instance). pattern 1: T = sum_e (x_u - x_v) (x) y_e (x) t_e on three
    distinct characters; pattern 2: sum_e ((x_u - x_v) ^ p_e) (x) w_e on (s, s, t); pattern 3: sum_e (x_u - x_v) ^ p_e ^ s_e."""
    s1, s2, s3 = chars3
    m = len(edges)
    vchar = [s1] * n + [s2] * m + [s3] * m
    T = {}
    for e, (u, v) in enumerate(edges):
        Y, Z = n + e, n + m + e
        if u != v:
            add_alt(T, u, Y, Z, 1)
            add_alt(T, v, Y, Z, -1)
    T = {key: val for key, val in T.items() if val}
    return vchar, T


GRAPHS = {"K2": (2, [(0, 1)]), "digon": (2, [(0, 1), (0, 1)]), "P3": (3, [(0, 1), (1, 2)]),
          "K3": (3, [(0, 1), (1, 2), (0, 2)]), "loop+edge": (2, [(0, 0), (0, 1)])}


def potts(n, edges, Q, v):
    return sum(math.prod(1 + v * (s[a] == s[b]) for a, b in edges) for s in itertools.product(range(Q), repeat=n))


# ---------------------------------------------------------------- the test groups
def groups():
    G = {}
    # p = 7, r = 6, zeta = 3 (primitive 6th root mod 7): pattern 1 lives on V-characters (1, 2, 3)
    G["H(7) (z,z^2) [Heisenberg, pattern 1]"] = Group("H7_12", 7, 6, [1, 2], [3], {(0, 1): [1]})
    G["free3(7) (z,z^2,z^3) [three components]"] = Group("F7", 7, 6, [1, 2, 3], [3, 4, 5],
                                                         {(0, 1): [1, 0, 0], (0, 2): [0, 1, 0], (1, 2): [0, 0, 1]})
    G["free3(7) minus [e1,e2] [two components]"] = Group("F7b", 7, 6, [1, 2, 3], [4, 5], {(0, 2): [1, 0], (1, 2): [0, 1]})
    G["free3(7) only [e2,e3] [Heisenberg in other roles]"] = Group("F7c", 7, 6, [1, 2, 3], [5], {(1, 2): [1]})
    # p = 5, r = 4, zeta = 2: the V-multiset {1, 1, 2} (two equal characters)
    G["H(5) (z,z) [Heisenberg, pattern 2]"] = Group("H5_11", 5, 4, [1, 1], [2], {(0, 1): [1]})
    G["H(5) (z,z^2) [Heisenberg, pattern 4]"] = Group("H5_12", 5, 4, [1, 2], [3], {(0, 1): [1]})
    G["mix(5): [e1,e2]->A_{z^2}, [e1,f]->A_{z^3}"] = Group("M5", 5, 4, [1, 1, 2], [2, 3], {(0, 1): [1, 0], (0, 2): [0, 1]})
    G["mix(5)': also [e2,f]->A_{z^3}"] = Group("M5b", 5, 4, [1, 1, 2], [2, 3], {(0, 1): [1, 0], (0, 2): [0, 1], (1, 2): [0, 1]})
    # p = 7, r = 3, zeta = 2: pattern 3 (all characters equal, zeta^3 = 1)
    G["H(7) (w,w) [Heisenberg, pattern 3]"] = Group("H7_11", 7, 3, [1, 1], [2], {(0, 1): [1]})
    G["free3(7) (w,w,w) [pattern 3, three components]"] = Group("F7w", 7, 3, [1, 1, 1], [2, 2, 2],
                                                               {(0, 1): [1, 0, 0], (0, 2): [0, 1, 0], (1, 2): [0, 0, 1]})
    # two hard blocks for one gadget (the sum over psi_k): H x H' with H' acting by the inverse characters, so that
    # psi_1 reads H and psi_5 = psi^-1 reads H' on the same V-triple (1, 2, 3); and H x H with one action (same k)
    G["H(7) x H(7)' (z,z^2) x (z^5,z^4) [two k's read one triple]"] = Group("HH7", 7, 6, [1, 2, 5, 4], [3, 3],
                                                                           {(0, 1): [1, 0], (2, 3): [0, 1]})
    G["H(7) x H(7) (z,z^2) twice [tensor-product weight]"] = Group("HH7s", 7, 6, [1, 2, 1, 2], [3, 3],
                                                                  {(0, 1): [1, 0], (2, 3): [0, 1]})
    # negative controls: no hard pair
    G["NEG H(5) (z,z^3) [ab = 1]"] = Group("N5", 5, 4, [1, 3], [0], {(0, 1): [1]})
    G["NEG trivial slot: [e0 (char 1), e1] -> A_{z}"] = Group("N5b", 5, 4, [0, 1], [1], {(0, 1): [1]})
    G["NEG H(7,r=6) (z,z^5) [ab = 1]"] = Group("N7", 7, 6, [1, 5], [0], {(0, 1): [1]})
    return G


def triples(r):
    """multisets {s1, s2, s3} of nonzero exponents with s1 + s2 + s3 = 0 mod r, with the gadget pattern"""
    out = []
    for s in itertools.combinations_with_replacement(range(1, r), 3):
        if sum(s) % r == 0:
            a, b, c = s
            if a != b and b != c and a != c:
                out.append(((a, b, c), 1))
            elif a == b == c:
                out.append(((a, a, a), 3))
            else:
                dbl = a if a == b else c
                single = c if a == b else a
                out.append(((dbl, dbl, single), 2))
    return out


def main():
    t0 = time.time()
    out = {"description": "Bulatov-Grohe route, abstract layer (bg_route.py)", "cases": [], "weights": [], "controls": {}}
    ok_all = True
    Gs = groups()

    # (1) the BG form equals the direct count, on small graphs, for every group and every psi_k
    plan = [
        ("H(7) (z,z^2) [Heisenberg, pattern 1]", (1, 2, 3), 1, ["K2", "digon", "P3", "loop+edge"]),
        ("free3(7) (z,z^2,z^3) [three components]", (1, 2, 3), 1, ["K2", "digon", "P3", "loop+edge"]),
        ("free3(7) minus [e1,e2] [two components]", (1, 2, 3), 1, ["K2", "digon", "P3"]),
        ("free3(7) only [e2,e3] [Heisenberg in other roles]", (1, 2, 3), 1, ["K2", "digon", "P3"]),
        ("free3(7) (z,z^2,z^3) [three components]", (2, 1, 3), 1, ["K2", "digon", "P3"]),
        ("free3(7) (z,z^2,z^3) [three components]", (3, 1, 2), 1, ["K2", "digon", "P3"]),
        ("H(5) (z,z) [Heisenberg, pattern 2]", (1, 1, 2), 2, ["K2", "digon"]),
        ("H(5) (z,z^2) [Heisenberg, pattern 4]", (1, 1, 2), 2, ["K2", "digon", "P3", "K3"]),
        ("mix(5): [e1,e2]->A_{z^2}, [e1,f]->A_{z^3}", (1, 1, 2), 2, ["K2", "digon", "loop+edge"]),
        ("mix(5)': also [e2,f]->A_{z^3}", (1, 1, 2), 2, ["K2", "digon"]),
        ("mix(5): [e1,e2]->A_{z^2}, [e1,f]->A_{z^3}", (2, 1, 1), 1, ["K2", "digon", "P3"]),
        ("H(7) (w,w) [Heisenberg, pattern 3]", (1, 1, 1), 3, ["K2"]),
        ("free3(7) (w,w,w) [pattern 3, three components]", (1, 1, 1), 3, []),
        ("NEG H(5) (z,z^3) [ab = 1]", (1, 1, 2), 2, ["K2", "digon", "P3"]),
        ("NEG trivial slot: [e0 (char 1), e1] -> A_{z}", (1, 1, 2), 2, ["K2", "digon"]),
    ]
    for gname, chars3, pattern, gnames in plan:
        G = Gs[gname]
        for gr in gnames:
            n, E = GRAPHS[gr]
            if pattern == 1:
                vchar, T = gadget(1, chars3, n, E)
            else:
                # (s, s, t): vertex coordinates and p_e in the doubled slot, w_e in the single slot;
                # pattern 3: (s, s, s) with s_e in the third slot (alternating 3-form)
                s, _, t = chars3
                m = len(E)
                vchar = [s] * n + [s] * m + [t] * m
                T = {}
                for e, (u, v) in enumerate(E):
                    P, W_ = n + e, n + m + e
                    if u != v:
                        add_alt(T, u, P, W_, 1)
                        add_alt(T, v, P, W_, -1)
                T = {key: val for key, val in T.items() if val}
            for k in range(G.r):
                cvars, tests = variables(G, vchar, k)
                Nd = direct_count(G, vchar, T, k)
                Nb = bg_sum(G, (vchar[0], vchar[n] if len(E) else chars3[1], vchar[-1] if len(E) else chars3[2]), k, n, E,
                            len(tests))
                row = {"group": gname, "V-triple (gadget slots)": chars3, "pattern": pattern, "graph": gr, "k": k,
                       "dim c": len(cvars), "#tests": len(tests), "N_direct": Nd, "N_BG": Nb,
                       "ok": (Nd is None) or (Nb is None) or Nd == Nb}
                ok_all &= row["ok"]
                out["cases"].append(row)
                if k == 1 or not row["ok"]:
                    print(f"{gname[:44]:44s} {str(chars3):10s} {gr:9s} k={k} dims c={len(cvars):2d} tests={len(tests):2d} "
                          f"direct={Nd} BG={Nb} {'ok' if row['ok'] else 'MISMATCH'}", flush=True)

    # (2) the weight g on every V-triple of nontrivial characters, every psi_k: rank one (constant) or not
    for gname, G in Gs.items():
        for chars3, pattern in triples(G.r):
            for k in range(G.r):
                U, table = g_table(G, chars3, k, explicit=True)
                vals = sorted({v for v, _ in table.values()})
                prof = {}
                for delta, (v, rk) in table.items():
                    prof[rk] = prof.get(rk, 0) + 1
                row = {"group": gname, "triple": chars3, "pattern": pattern, "k": k, "dims U": [len(u) for u in U],
                       "g values": vals, "rank profile {rank: #delta}": prof, "rank one": len(vals) <= 1}
                out["weights"].append(row)
    # summary: which groups have a non-rank-one block, and for which (triple, k)
    summary = {}
    for gname, G in Gs.items():
        hard = [(w["triple"], w["k"]) for w in out["weights"] if w["group"] == gname and not w["rank one"]]
        summary[gname] = {"hard pairs (kappa)": G.hard_pairs(), "non-rank-one blocks (triple, k)": hard,
                          "consistent (hard pair <=> some block not rank one)": bool(G.hard_pairs()) == bool(hard)}
        ok_all &= summary[gname]["consistent (hard pair <=> some block not rank one)"]
        print(f"{gname[:50]:50s} hard pairs {G.hard_pairs()}  non-rank-one blocks {hard}", flush=True)
    out["summary"] = summary

    # (3) positive controls against COPRIME-CLASS2-20261026-001D: Potts values for the Heisenberg gadgets
    ctl = {}
    # pattern 3, p = 7: digon -> 7^(2m-n) Z(7^3, 48) = 46101601
    G = Gs["H(7) (w,w) [Heisenberg, pattern 3]"]
    n, E = GRAPHS["digon"]
    # pattern-3 gadget: V_s = vertices + p_e + s_e, T = sum (x_u - x_v) ^ p_e ^ s_e; single-edge chars (1,1,1)
    vchar = [1] * (n + 2 * len(E))
    ntests = sum(1 for b in range(len(G.cA)) for j in range(len(vchar)) if vchar[j] == (-G.cA[b]) % G.r)
    nb = bg_sum(G, (1, 1, 1), 1, n, E, ntests)
    ctl["pattern 3 p=7 digon (D: 46101601)"] = {"N_BG": nb, "ok": nb == 46101601}
    # pattern 2 (Heisenberg (2,2)) and pattern 4 (Heisenberg (2,4)) at p = 5 on the triangle: 3240625 and 25925
    n, E = GRAPHS["K3"]
    for gname, target in [("H(5) (z,z) [Heisenberg, pattern 2]", 3240625), ("H(5) (z,z^2) [Heisenberg, pattern 4]", 25925)]:
        G = Gs[gname]
        m = len(E)
        vchar = [1] * (n + m) + [2] * m
        ntests = sum(1 for b in range(len(G.cA)) for j in range(len(vchar)) if vchar[j] == (-G.cA[b]) % G.r)
        nb = bg_sum(G, (1, 1, 2), 1, n, E, ntests)
        ctl[f"{gname} triangle (D: {target})"] = {"N_BG": nb, "ok": nb == target}
    # pattern 1 Heisenberg with the diagonal gadget: Potts(7, 6) up to the factor
    G = Gs["H(7) (z,z^2) [Heisenberg, pattern 1]"]
    n, E = GRAPHS["K3"]
    nb = bg_sum(G, (1, 2, 3), 1, n, E, len(E))
    ctl["pattern 1 p=7 triangle, diagonal gadget: N = 7^(-m) * 7^m Z(7, 6)"] = {"N_BG": nb, "Z(7,6)": potts(n, E, 7, 6),
                                                                                "ok": nb == potts(n, E, 7, 6)}
    for k_, v in ctl.items():
        print("control:", k_, v, flush=True)
        ok_all &= v["ok"]
    out["controls"] = ctl
    out["ok"] = ok_all
    out["seconds"] = round(time.time() - t0, 1)
    (HERE / "bg_route_result.json").write_text(json.dumps(out, indent=1, default=str) + "\n")
    print("ALL OK" if ok_all else "FAILURES", out["seconds"], "s")
    return 0 if ok_all else 1


if __name__ == "__main__":
    sys.exit(main())
