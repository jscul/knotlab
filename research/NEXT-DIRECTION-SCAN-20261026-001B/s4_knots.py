"""Lane B of NEXT-DIRECTION-SCAN-20261026-001: S4 on knots, the identity |Hom(pi, S4)| = 4 + R + 2T, and the size of R.

Parts:
  A. On the quandle of 3-cycles of S4, the 3-crossing twist sigma^3 (and sigma^-3), sigma(x, y) = (x y x^-1, x), fixes every pair in
     the same A4-class. With the smoothing argument of BOUNDED-H1-20261025-001A Lemma 2.1 this gives R = 2 * 4^n for every knot
     diagram D(G^(3)) with n black regions (two A4-classes of 3-cycles, one per knot, 4^n colourings each).
  B. Brute force on braid closures that are D(G^(3)) knots (trefoil = D(K2^(3)), granny 3_1 # 3_1 = D(P3^(3))): the counts by
     meridian class, T against the bicycle law, the 4-cycle count against T (Livingston), R against 2 * 4^n.
  C. The knot family of the S4 hardness proof, K_k = D((H~[Gamma_1^{||k}])^(3)): T(K_k) = 2^-N 68^(k m) Z_{W_k}(H~) with
     W_k = R + (25/17)^k I + (15/17)^k N (proof Section 6), R(K_k) = 2 * 4^N, N = n + 2 k m; the ratio R / T and |Hom|.
Standard library only. Run: python3 -B s4_knots.py   (about 1 minute)
"""
import itertools
import json
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent


def pmul(p, q):          # (p q)(i) = p(q(i))
    return tuple(p[q[i]] for i in range(4))


def pinv(p):
    r = [0] * 4
    for i, x in enumerate(p):
        r[x] = i
    return tuple(r)


S4 = list(itertools.permutations(range(4)))


def cycle_type(p):
    seen, t = set(), []
    for i in range(4):
        if i in seen:
            continue
        j, L = i, 0
        while j not in seen:
            seen.add(j)
            j = p[j]
            L += 1
        t.append(L)
    return tuple(sorted(t, reverse=True))


CLASS = {(1, 1, 1, 1): "identity", (2, 1, 1): "transposition", (2, 2): "double transposition", (3, 1): "3-cycle", (4,): "4-cycle"}
A4 = [p for p in S4 if cycle_type(p) in ((1, 1, 1, 1), (2, 2), (3, 1))]


def a4_class(x):
    """the A4-conjugacy class of a 3-cycle, as a frozenset"""
    return frozenset(pmul(pmul(g, x), pinv(g)) for g in A4)


def part_a():
    three = [p for p in S4 if cycle_type(p) == (3, 1)]
    same = cross = same_ok = cross_ok = 0
    for x in three:
        for y in three:
            fwd = (x, y)
            for _ in range(3):
                a, b = fwd
                fwd = (pmul(pmul(a, b), pinv(a)), a)
            bwd = (x, y)
            for _ in range(3):
                a, b = bwd
                bwd = (b, pmul(pmul(pinv(b), a), b))
            ok = fwd == (x, y) and bwd == (x, y)
            if a4_class(x) == a4_class(y):
                same += 1
                same_ok += ok
            else:
                cross += 1
                cross_ok += ok
    return {"3-cycles": len(three), "A4-classes": len({a4_class(x) for x in three}),
            "same-class pairs": same, "fixed by sigma^3 and sigma^-3": same_ok,
            "cross-class pairs": cross, "cross-class pairs fixed": cross_ok, "ok": same == same_ok == 32}


def braid_counts(word, n):
    """|Hom(knot group of the closure, S4)| split by the class of the meridian; Hurwitz action on the top images"""
    out = {v: 0 for v in CLASS.values()}
    for top in itertools.product(S4, repeat=n):
        cur = list(top)
        for g in word:
            i = abs(g) - 1
            x, y = cur[i], cur[i + 1]
            if g > 0:
                cur[i], cur[i + 1] = pmul(pmul(x, y), pinv(x)), x
            else:
                cur[i], cur[i + 1] = y, pmul(pmul(pinv(y), x), y)
        if cur == list(top):
            out[CLASS[cycle_type(top[0])]] += 1
    return out


def f2_nullity_laplacian(n, E):
    L = [[0] * n for _ in range(n)]
    for u, v in E:
        L[u][u] ^= 1
        L[v][v] ^= 1
        L[u][v] ^= 1
        L[v][u] ^= 1
    r = 0
    for c in range(n):
        p = next((i for i in range(r, n) if L[i][c]), None)
        if p is None:
            continue
        L[r], L[p] = L[p], L[r]
        for i in range(n):
            if i != r and L[i][c]:
                L[i] = [a ^ b for a, b in zip(L[i], L[r])]
        r += 1
    return n - r                      # = c(H) + dim B(H)


def bicycle_T(n, E):
    return sum(2 ** f2_nullity_laplacian(n, [e for e in E if phi[e[0]] == phi[e[1]]]) for phi in itertools.product(range(3), repeat=n))


def part_b():
    rows = {}
    for name, word, strands, (n, E) in [("trefoil = D(K2^(3))", [1, 1, 1], 2, (2, [(0, 1)])),
                                        ("granny 3_1 # 3_1 = D(P3^(3))", [1, 1, 1, 2, 2, 2], 3, (3, [(0, 1), (1, 2)]))]:
        c = braid_counts(word, strands)
        T = c["transposition"]
        R = c["3-cycle"]
        tot = sum(c.values())
        rows[name] = {"counts by meridian class": c, "|Hom|": tot, "4 + R + 2T": 4 + R + 2 * T,
                      "T by the bicycle law": bicycle_T(n, E), "2 * 4^n": 2 * 4 ** n,
                      "ok": tot == 4 + R + 2 * T and T == bicycle_T(n, E) and R == 2 * 4 ** n and c["4-cycle"] == T}
    return rows


# ---------------------------------------------------------------- part C: the hardness family
STATES = [(t, p, x) for t in (0, 1) for p in range(3) for x in (0, 1)]
NU = {z: (1 - z[0], z[1], 1 - z[2]) for z in STATES}


def Zw(n, E, a, b):
    """sum over z in Z12^V of prod_e W(z_u, z_v), W = 1 (other), a (equal), b (nu-related)"""
    W = [[a if i == j else (b if NU[STATES[i]] == STATES[j] else 1) for j in range(12)] for i in range(12)]
    adj = {}
    for u, v in E:
        adj.setdefault(v, []).append(u)
    tot = Fraction(0)
    # sum vertex by vertex with partial products (n <= 5)
    def rec(i, z, w):
        nonlocal tot
        if i == n:
            tot += w
            return
        for s in range(12):
            ww = w
            for u, v in E:
                if v == i and u < i:
                    ww *= W[z[u]][s]
                elif u == i and v < i:
                    ww *= W[z[v]][s]
            z.append(s)
            rec(i + 1, z, ww)
            z.pop()
    rec(0, [], Fraction(1))
    return tot


def doubled(n, E, tree):
    """H~: the edges outside the spanning tree doubled (BOUNDED-H1 proof, Section 6 step 1)"""
    out = []
    for e in E:
        out += [e] if e in tree else [e, e]
    return out


def part_c():
    graphs = {"C3 (end-to-end check of the proof)": (3, [(0, 1), (1, 2), (0, 2)], None),
              "K4 doubled": (4, [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)], [(0, 1), (0, 2), (0, 3)]),
              "diamond doubled": (4, [(0, 1), (1, 2), (2, 0), (1, 3), (3, 2)], [(0, 1), (1, 2), (1, 3)]),
              "C5 doubled": (5, [(0, 1), (1, 2), (2, 3), (3, 4), (0, 4)], [(0, 1), (1, 2), (2, 3), (3, 4)])}
    rows = {}
    for name, (n, E, tree) in graphs.items():
        Ht = E if tree is None else doubled(n, E, tree)
        m = len(Ht)
        for k in ((1,) if tree is None else (1, 3, 5)):
            N = n + 2 * k * m
            Z = Zw(n, Ht, Fraction(25, 17) ** k, Fraction(15, 17) ** k)
            T = Fraction(68) ** (k * m) * Z / 2 ** N
            assert T.denominator == 1
            T = int(T)
            R = 2 * 4 ** N
            rows[f"{name}, k={k}"] = {"N (black regions)": N, "T": T, "R = 2*4^N": R, "R / T": f"{R / T:.3g}",
                                      "|Hom| = 4 + R + 2T": 4 + R + 2 * T, "|Hom| / 2T": f"{(4 + R + 2 * T) / (2 * T):.6g}"}
    rows["C3 (end-to-end check of the proof), k=1"]["matches the proof's value 1,158,510"] = \
        rows["C3 (end-to-end check of the proof), k=1"]["T"] == 1158510
    return rows


def main():
    out = {"A_sigma_cubed_on_3_cycles": part_a()}
    print("A:", out["A_sigma_cubed_on_3_cycles"], flush=True)
    out["B_brute_force"] = part_b()
    print("B:", json.dumps(out["B_brute_force"], indent=1), flush=True)
    out["C_hardness_family"] = part_c()
    print("C:", json.dumps(out["C_hardness_family"], indent=1), flush=True)
    (HERE / "s4_knots.json").write_text(json.dumps(out, indent=1, default=str) + "\n")


if __name__ == "__main__":
    main()
