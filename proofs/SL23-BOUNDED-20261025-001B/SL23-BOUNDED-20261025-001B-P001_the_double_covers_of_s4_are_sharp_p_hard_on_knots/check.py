"""Check for SL23-BOUNDED-20261025-001B-P001: the double covers of S4 are #P-hard on knots.

Standard library only; imports nothing from other proofs. Parts:
  1. groups: GL(2,3) and the binary octahedral group 2O (generated inside SL(2,9) by (1+i)/sqrt2 and (1+i+j+k)/2, with sqrt2 = i
     in F9) have order 48 and centre {I, -I}; conjugation on their four Sylow 3-subgroups maps them onto S4 with kernel the
     centre; the lifts of transpositions are involutions in GL(2,3) and elements of order 4 in 2O;
  2. knots: by brute force over Wirtinger presentations, for each knot of a zoo, |Hom(pi, G~)| = 2 |Hom(pi, S4)|, the maps sending
     meridians to lifts of transpositions number 2T(K), and |Hom(pi, S4)| = 4 + R(K) + 2T(K) with R the 3-cycle colourings;
  3. controls and the open closed case: on the closed manifold S3_2(trefoil) the lift count is not twice the S4 count; the naive
     identity |Hom(pi1 S3_4(K), G~)| = 8 + 2T(K) holds on some knots and fails on others.
Writes result.json next to this file with --write."""
import itertools
import json
import sys
import time
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent


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

    def order(self, a):
        k, x = 1, a
        while x != self.I:
            x = self.M[x][a]
            k += 1
        return k

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

    def center(self):
        return [z for z in range(self.n) if all(self.M[z][g] == self.M[g][z] for g in range(self.n))]


def m3(a, b):
    return ((a[0] * b[0] + a[1] * b[2]) % 3, (a[0] * b[1] + a[1] * b[3]) % 3,
            (a[2] * b[0] + a[3] * b[2]) % 3, (a[2] * b[1] + a[3] * b[3]) % 3)


def f9m(a, b):
    return ((a[0] * b[0] - a[1] * b[1]) % 3, (a[0] * b[1] + a[1] * b[0]) % 3)


def f9a(a, b):
    return ((a[0] + b[0]) % 3, (a[1] + b[1]) % 3)


def m9(A, B):
    return tuple(f9a(f9m(A[2 * r], B[c]), f9m(A[2 * r + 1], B[2 + c])) for r in range(2) for c in range(2))


def binary_octahedral():
    O, i_, one, mone, mi = (0, 0), (0, 1), (1, 0), (2, 0), (0, 2)
    ident = (one, O, O, one)
    qi = (i_, O, O, mi)
    qj = (O, one, mone, O)
    qk = m9(qi, qj)

    def scal(s, A):
        return tuple(f9m(s, x) for x in A)

    def add(A, B):
        return tuple(f9a(x, y) for x, y in zip(A, B))
    g1 = scal(mi, add(ident, qi))                          # (1 + i)/sqrt2 with 1/sqrt2 = 1/i = -i
    g2 = scal((2, 0), add(add(ident, qi), add(qj, qk)))   # (1 + i + j + k)/2 with 1/2 = 2 mod 3
    S, fr = {ident}, [ident]
    while fr:
        a = fr.pop()
        for g in (g1, g2):
            b = m9(a, g)
            if b not in S:
                S.add(b)
                fr.append(b)
    return Group(sorted(S), m9)


def perm_mul(a, b):
    return tuple(a[b[i]] for i in range(4))


S4 = Group(list(itertools.permutations(range(4))), perm_mul)


def projection_to_s4(G):
    """conjugation action on the four Sylow 3-subgroups: a homomorphism G -> S4"""
    sylows = sorted({G.gen([a]) for a in range(G.n) if G.order(a) == 3}, key=lambda H: min(H))
    assert len(sylows) == 4

    def perm(g):
        return tuple(sylows.index(frozenset(G.M[G.M[g][h]][G.INV[g]] for h in H)) for H in sylows)
    return [S4.E.index(perm(g)) for g in range(G.n)]


def cycle_type(G, a):
    p = G.E[a]
    seen, t = set(), []
    for i in range(4):
        if i not in seen:
            L, j = 0, i
            while j not in seen:
                seen.add(j)
                j = p[j]
                L += 1
            t.append(L)
    return tuple(sorted(t, reverse=True))


# --------------------------------------------------------------------------------------------------------- knots, brute force
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


def peripheral(G, code):
    """all homomorphisms pi -> G as (meridian image, preferred longitude image)"""
    U, cr = wirtinger(code)
    w = sum(s for *_, s in cr)
    out = []
    for m in range(G.n):
        cls = sorted({G.M[G.M[g][m]][G.INV[g]] for g in range(G.n)})
        val = [None] * U
        val[0] = m

        def rec(k_):
            if k_ == len(cr):
                P = G.I
                for o, i, j, s in cr:
                    P = G.M[P][G.pw(val[o], s)]
                out.append((m, G.M[P][G.pw(val[0], -w)]))
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
    return out


def main():
    t0 = time.time()
    out, ok_all = {}, True
    GL = Group([m for m in itertools.product(range(3), repeat=4) if (m[0] * m[3] - m[1] * m[2]) % 3], m3)
    TO = binary_octahedral()
    groups = {"GL(2,3)": GL, "2O": TO}
    p1, ok1, lift_class = {}, True, {}
    for name, G in groups.items():
        pr = projection_to_s4(G)
        hom = all(pr[G.M[a][b]] == S4.M[pr[a]][pr[b]] for a in range(G.n) for b in range(G.n))
        kernel = [g for g in range(G.n) if pr[g] == S4.I]
        lifts = [g for g in range(G.n) if cycle_type(S4, pr[g]) == (2, 1, 1)]
        lift_class[name] = (pr, lifts)
        r = {"order": G.n, "centre": len(G.center()), "homomorphism onto S4": hom and len(set(pr)) == 24,
             "kernel = centre": sorted(kernel) == sorted(G.center()), "orders of transposition lifts": sorted({G.order(g) for g in lifts})}
        p1[name] = r
        ok1 &= G.n == 48 and r["centre"] == 2 and r["homomorphism onto S4"] and r["kernel = centre"]
    ok1 &= p1["GL(2,3)"]["orders of transposition lifts"] == [2] and p1["2O"]["orders of transposition lifts"] == [4]
    p1["ok"] = ok1
    out["1_groups"] = p1
    print("part 1:", p1, flush=True)
    ok_all &= ok1

    f8 = gauss_from_braid([1, -2, 1, -2], 3)
    tre = gauss_from_braid([1, 1, 1], 2)
    zoo = {"3_1": tre, "4_1": f8, "5_2": gauss_from_braid([1, 1, 1, 2, -1, 2], 3), "6_1": gauss_from_braid([1, 1, 2, -1, -3, 2, -3], 4),
           "8_18": gauss_from_braid([1, -2] * 4, 3), "8_19": gauss_from_braid([1, 2] * 4, 3),
           "10_82": gauss_from_braid([-1, -1, -1, -1, 2, -1, 2, -1, 2, 2], 3), "3_1 # 3_1": connected_sum(tre, tre),
           "3_1 # 4_1": connected_sum(tre, f8)}
    rows, ok2 = {}, True
    for kn, code in zoo.items():
        ps4 = peripheral(S4, code)
        T = sum(1 for m, lam in ps4 if cycle_type(S4, m) == (2, 1, 1))
        R = sum(1 for m, lam in ps4 if cycle_type(S4, m) == (3, 1))
        r = {"|Hom(pi,S4)|": len(ps4), "T": T, "R": R, "4 + R + 2T": 4 + R + 2 * T}
        good = len(ps4) == 4 + R + 2 * T
        for name, G in groups.items():
            pr, lifts = lift_class[name]
            pg = peripheral(G, code)
            on_lifts = sum(1 for m, lam in pg if m in set(lifts))
            r[f"|Hom(pi,{name})|"] = len(pg)
            r[f"{name} maps with meridians on transposition lifts"] = on_lifts
            good &= len(pg) == 2 * len(ps4) and on_lifts == 2 * T
        r["ok"] = good
        rows[kn] = r
        ok2 &= good
        print(f"part 2 {kn}: |Hom S4| {len(ps4)} = 4 + {R} + 2*{T}; GL {r['|Hom(pi,GL(2,3))|']} 2O {r['|Hom(pi,2O)|']} "
              f"{'ok' if good else 'FAIL'} ({time.time() - t0:.0f} s)", flush=True)
    out["2_knots"] = {"rows": rows, "ok": ok2}
    ok_all &= ok2

    c = {}
    ps4 = peripheral(S4, tre)
    s4_closed = sum(1 for m, lam in ps4 if S4.M[S4.pw(m, 2)][lam] == S4.I)
    for name, G in groups.items():
        pg = peripheral(G, tre)
        closed = sum(1 for m, lam in pg if G.M[G.pw(m, 2)][lam] == G.I)
        c[f"S3_2(3_1): |Hom(pi1, {name})| vs 2 |Hom(pi1, S4)|"] = [closed, 2 * s4_closed]
    c["closed manifolds obstruct some lifts (counts differ)"] = any(a != b for a, b in c.values() if isinstance(a, int))
    naive = {}
    for kn in ("3_1", "8_19", "3_1 # 3_1", "3_1 # 4_1"):
        T = rows[kn]["T"]
        for name, G in groups.items():
            pg = peripheral(G, zoo[kn])
            c4 = sum(1 for m, lam in pg if G.M[G.pw(m, 4)][lam] == G.I)
            naive[f"{kn} {name}"] = [c4, 8 + 2 * T]
    c["S3_4 counts vs the naive 8 + 2T"] = naive
    c["the naive identity holds on some knots and fails on others"] = (any(a == b for a, b in naive.values())
                                                                      and any(a != b for a, b in naive.values()))
    ok3 = c["closed manifolds obstruct some lifts (counts differ)"] and c["the naive identity holds on some knots and fails on others"]
    out["3_controls_and_open_case"] = {"rows": c, "ok": ok3}
    print("part 3:", c, flush=True)
    ok_all &= ok3

    out["ok"] = ok_all
    out["seconds"] = round(time.time() - t0, 1)
    result = {"schema_version": 1, "artifact_id": "SL23-BOUNDED-20261025-001B-P001", "status": "Proved" if ok_all else "Partial",
              "checks": out}
    if "--write" in sys.argv:
        (HERE / "result.json").write_text(json.dumps(result, indent=2, default=str) + "\n")
    print("ALL OK" if ok_all else "FAILURES", out["seconds"], "s")
    return 0 if ok_all else 1


if __name__ == "__main__":
    sys.exit(main())
