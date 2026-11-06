"""Check for BEYOND-CLASS2-20261027-001A-P001: a cross-layer hard pair makes counting #P-hard although the class-2 quotient
is easy. numpy; bc_lib.py (this directory); imports read-only cp_lib.py (COPRIME-CLASS2-20261026-001B-P001) and ck_lib.py
(CLASSK-DICHOTOMY-20261026-001A-P001). Run: .venv/bin/python check.py [--write]

1. The BCH groups: graded, equivariant, Jacobi (in the constructor); associativity, inverses, exponent p and equivariance of the
   group law on random samples, for the cross-layer and four-way algebras.
2. Class dependence: on small knot surgeries the layered direct count equals |B1(L1)| times the sum, over representatives of
   H1(L1), of the number of completions; completions agree on coboundary-shifted representatives.
3. The reduction: on many knot surgeries with H1 = Z/r, in every sector, the cross-layer count equals |B1(L1)| |B1(L2)|
   |Z1(L3)| times the Heisenberg (alpha, alpha) kernel count (cp_lib); the control alpha^2 = 1 gives constants times |V_alpha|^2.
4. Hard-pair structure: the cross-layer algebra has a graded hard pair across layers; its class-2 quotient has none; the
   Heisenberg (alpha, alpha) sector-1 weight on its gadget model is nonconstant.
5. Hardness bookkeeping on the gadget model: h(Gamma) = sum_k c_k f_k(Gamma) with the extra factor p^(d_alpha^k) linear in
   (n, m); an anchor and a Vandermonde solve recover the sector-1 term.
"""
import itertools
import json
import random
import sys
import time
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
sys.path.insert(1, str(next((ROOT / "proofs/COPRIME-CLASS2-20261026-001B").glob("COPRIME-CLASS2-20261026-001B-P001_*"))))
sys.path.insert(2, str(next((ROOT / "proofs/CLASSK-DICHOTOMY-20261026-001A").glob("CLASSK-DICHOTOMY-20261026-001A-P001_*"))))
import bc_lib as B  # noqa: E402
import cp_lib as C  # noqa: E402  (read-only: braid presentations, Heisenberg obstruction and kernel counts)
import ck_lib as K  # noqa: E402  (read-only: gadget models, template counts, weight tables)

T31, F41, K52, S61 = ([1, 1, 1], 2), ([1, -2, 1, -2], 3), ([1, 1, 1, 2, -1, 2], 3), ([1, 1, 2, -1, -3, 2, -3], 4)
KNOTS = {"3_1": T31, "4_1": F41, "5_2": K52, "6_1": S61}


def knot_list():
    out = dict(KNOTS)
    w, n = C.connected_sum([T31, T31])
    out["3_1 # 3_1"] = (w, n)
    w, n = C.connected_sum([T31, S61])
    out["3_1 # 6_1"] = (w, n)
    w, n = C.connected_sum([S61, F41])
    out["6_1 # 4_1"] = (w, n)
    return out


# ------------------------------------------------------------------------------------------------ part 1

def part1(rng):
    rows, ok = {}, True
    algs = [("cross-layer p=5 r=4 alpha=Z", B.cross_layer_algebra(5, 4, 1)),
            ("cross-layer p=7 r=6 alpha=Z", B.cross_layer_algebra(7, 6, 1)),
            ("cross-layer p=7 r=3 alpha=Z", B.cross_layer_algebra(7, 3, 1)),
            ("four-way p=5 r=4 alpha=Z", B.four_way_algebra(5, 4, 1)),
            ("four-way p=7 r=6 alpha=Z", B.four_way_algebra(7, 6, 1))]
    for name, L in algs:
        p, r = L.p, L.r
        good = True
        rand = lambda: (tuple(rng.randrange(p) for _ in range(L.n)), rng.randrange(r))
        for _ in range(200):
            a, b, c = rand(), rand(), rand()
            good &= L.mul(L.mul(a, b), c) == L.mul(a, L.mul(b, c))
            good &= L.mul(a, L.inv(a)) == L.ident()
            X, Y = a[0], b[0]
            e = rng.randrange(r)
            good &= L.act(e, L.bch(X, Y)) == L.bch(L.act(e, X), L.act(e, Y))
            g = (X, 0)
            acc = L.ident()
            for _ in range(p):
                acc = L.mul(acc, g)
            good &= acc == L.ident()
        rows[name] = {"order": p ** L.n * r, "graded hard pairs": B.graded_hard_pairs(L), "ok": bool(good)}
        ok &= bool(good)
    return {"rows": rows, "ok": ok}


# ------------------------------------------------------------------------------------------------ part 2

def representatives(U, rels, L, k):
    """for each layer-1 basis index: a basis of a complement of B1 in Z1 (twisted by its character to the k)"""
    p, r = L.p, L.r
    out = {}
    for i in L.layer(1):
        mult = pow(L.Z, (k * L.chi[i]) % r, p)
        Z = B.z1(U, rels, mult, p)
        basis = [[(mult - 1) % p] * U] if mult != 1 else []
        H = []
        for z in Z:
            if B.rank(basis + [z], p) > len(basis):
                basis.append(z)
                H.append(z)
        out[i] = (H, mult)
    return out


def part2(rng):
    rows, ok = {}, True
    cases = [("cross-layer", B.cross_layer_algebra(5, 4, 1), "3_1", 4), ("cross-layer", B.cross_layer_algebra(5, 4, 1), "6_1", 4),
             ("four-way", B.four_way_algebra(5, 4, 1), "6_1", 4), ("four-way", B.four_way_algebra(5, 4, 1), "3_1", 4),
             ("cross-layer", B.cross_layer_algebra(7, 3, 1), "3_1", 3)]
    for (lab, L, kn, surg) in cases:
        p, r = L.p, L.r
        word, n = KNOTS[kn]
        U, rels, _ = C.presentation(word, n, surg)
        per = {}
        good = True
        for k in range(r):
            direct = B.direct_count(L, U, rels, k)
            reps = representatives(U, rels, L, k)
            L1 = L.layer(1)
            b1 = 1
            for i in L1:
                b1 *= p if reps[i][1] != 1 else 1
            spaces = [B.span_all(reps[i][0], p, U) for i in L1]
            s = 0
            shift_ok = True
            for f1 in itertools.product(*spaces):
                fix = {i: list(v) for i, v in zip(L1, f1)}
                c = B.direct_count(L, U, rels, k, fix_f1=fix)
                s += c
                # a coboundary-shifted representative has the same number of completions
                if rng.random() < 0.2:
                    shift = rng.randrange(1, p)
                    fix2 = {i: [(fix[i][g] + shift * (reps[i][1] - 1)) % p for g in range(U)] for i in L1}
                    shift_ok &= B.direct_count(L, U, rels, k, fix_f1=fix2) == c
            per[k] = [direct, b1 * s, shift_ok]
            good &= direct == b1 * s and shift_ok
        rows[f"{lab} p={p} r={r} S^3_{surg}({kn})"] = {"per sector [direct, |B1(L1)| sum over H1 reps, shift invariance]": per,
                                                       "ok": bool(good)}
        ok &= bool(good)
    return {"rows": rows, "ok": ok}


# ------------------------------------------------------------------------------------------------ part 3

def heis_kernel(p, r, a_val, word, n, surg, k):
    """cp_lib's Heisenberg (a, a) kernel count #{(u, v) in V_a^k x V_a^k : u u v = 0} over psi_k"""
    G = C.Group(p, r, a_val, a_val)
    U, rels, _ = C.presentation(word, n, surg)
    Hx, Hy, Bm, _ = C.obstruction(G, U, rels, k)
    N, _ = C.kernel_counts(Hx, Hy, Bm, p)
    return N, len(Hx)


def part3():
    rows, ok = {}, True
    configs = [(5, 4, 1), (7, 3, 1), (7, 6, 1), (7, 6, 2), (13, 4, 1)]
    knots = knot_list()
    n_cmp = 0
    for (p, r, e) in configs:
        L = B.cross_layer_algebra(p, r, e)
        a_val = pow(L.Z, e, p)
        for kn, (word, nstr) in knots.items():
            U, rels, _ = C.presentation(word, nstr, r)
            # cost guard: the layer-1 and layer-2 enumerations
            dims = [len(B.z1(U, rels, pow(L.Z, (k * e) % r, p), p)) for k in range(r)]
            if p ** (2 * max(dims)) > 3 * 10 ** 5:
                continue
            per, good = {}, True
            for k in range(r):
                direct = B.direct_count(L, U, rels, k)
                Nk, dV = heis_kernel(p, r, a_val, word, nstr, r, k)
                m = {i: pow(L.Z, (k * L.chi[i]) % r, p) for i in range(L.n)}
                const = 1
                for i in L.layer(1) + L.layer(2):
                    const *= p if m[i] != 1 else 1
                for i in L.layer(3):
                    const *= p ** len(B.z1(U, rels, m[i], p))
                per[k] = [direct, const * Nk]
                good &= direct == const * Nk
                n_cmp += 1
            rows[f"p={p} r={r} alpha=Z^{e} S^3_{r}({kn})"] = {"per sector [direct, constants x Heisenberg kernel]": per,
                                                              "ok": bool(good)}
            ok &= bool(good)
    # control: alpha^2 = 1 (p = 5, r = 4, alpha = Z^2 = -1): no condition, constants x |V|^2
    L = B.cross_layer_algebra(5, 4, 2)
    for kn in ("6_1", "4_1"):
        word, nstr = KNOTS[kn]
        U, rels, _ = C.presentation(word, nstr, 4)
        per, good = {}, True
        for k in range(4):
            direct = B.direct_count(L, U, rels, k)
            m = {i: pow(L.Z, (k * L.chi[i]) % 4, 5) for i in range(L.n)}
            const = 1
            for i in L.layer(1) + L.layer(2):
                const *= 5 if m[i] != 1 else 1
            for i in L.layer(3):
                const *= 5 ** len(B.z1(U, rels, m[i], 5))
            dV = len(representatives(U, rels, L, k)[L.idx["y"]][0])
            free = const * 5 ** (2 * dV)
            Nk, _ = heis_kernel(5, 4, pow(L.Z, 2, 5), word, nstr, 4, k)
            per[k] = [direct, free, "Heisenberg kernel " + str(Nk)]
            good &= direct == free
        rows[f"control alpha^2 = 1 (p=5, r=4) S^3_4({kn})"] = {"per sector [direct, constants x |V|^2, (Heisenberg kernel)]": per,
                                                               "ok": bool(good)}
        ok &= bool(good)
    return {"rows": rows, "comparisons": n_cmp, "ok": ok}


# ------------------------------------------------------------------------------------------------ parts 4 and 5

def part4():
    rows, ok = {}, True
    for (p, r, e) in [(5, 4, 1), (7, 3, 1), (7, 6, 1), (7, 6, 2)]:
        L = B.cross_layer_algebra(p, r, e)
        Q = B.heisenberg_algebra(p, r, 0, e)               # the class-2 quotient: x (trivial), y (alpha), z = [x, y]
        Hh = B.heisenberg_algebra(p, r, e, e)              # Heisenberg (alpha, alpha)
        G = K.KGroup(p, r, [e, e], [2 * e], {(0, 1, 0): 1})
        S = (e, e, (-2 * e) % r)
        gad = K.Gadget(S, 2, [(0, 1)], r, p)
        W, U, sd = K.weight_table(G, gad, 1)
        nc = len(set(W.values())) > 1
        good = (B.graded_hard_pairs(L) == [("y", "z")] and B.graded_hard_pairs(Q) == []
                and B.graded_hard_pairs(Hh) == [("x", "y")] and nc)
        rows[f"p={p} r={r} alpha=Z^{e}"] = {"cross-layer hard pairs": B.graded_hard_pairs(L), "quotient hard pairs": B.graded_hard_pairs(Q),
                                            "Heisenberg (alpha, alpha) hard pairs": B.graded_hard_pairs(Hh),
                                            "slot pattern": gad.pattern, "W_1 nonconstant": nc, "ok": bool(good)}
        ok &= bool(good)
    return {"rows": rows, "ok": ok}


def solve_vandermonde(zs, hs):
    R = len(zs)
    M = [[Fraction(z) ** j for z in zs] + [Fraction(hs[j])] for j in range(R)]
    for c in range(R):
        piv = next(i for i in range(c, R) if M[i][c] != 0)
        M[c], M[piv] = M[piv], M[c]
        for i in range(R):
            if i != c and M[i][c] != 0:
                f = M[i][c] / M[c][c]
                M[i] = [a - f * b for a, b in zip(M[i], M[c])]
    return [M[i][R] / M[i][i] for i in range(R)]


def part5():
    """on the gadget model of S = (alpha, alpha, alpha^-2): f_k(Gamma) = (Heisenberg sector function) x p^(d_alpha^k); the
    anchor K2 and a Vandermonde solve recover the sector-1 term"""
    rows, ok = {}, True
    graphs = {"K2": (2, [(0, 1)]), "P3": (3, [(0, 1), (1, 2)]), "digon": (2, [(0, 1), (0, 1)])}
    for (p, r, e) in [(5, 4, 1), (7, 6, 1)]:
        G = K.KGroup(p, r, [e, e], [2 * e], {(0, 1, 0): 1})
        S = (e, e, (-2 * e) % r)

        def f_vals(n, E):
            gad = K.Gadget(S, n, E, r, p)
            d = K.base_dims(gad.summand_counts(), r)
            out = []
            for k in range(r):
                h1a = p ** sum(d.get(k * a % r, 0) for a in G.aexp if k * a % r)
                free = p ** sum(d.get(k * b % r, 0) for b in G.bexp if k * b % r and (k * b % r) not in set(gad.S))
                extra = p ** d.get(k * e % r, 0) if k * e % r else 1      # the |Z1(F_alpha^k)| factor, up to a constant
                # the Fourier form |A23|^-n Z_W, equal to the template count (CLASSK-DICHOTOMY-20261026-001A), avoids enumeration
                out.append(h1a * free * extra * K.fourier_count(G, gad, k)[0])
            return out
        c = [p ** (2 * (1 if k * e % r else 0) + (1 if k * e % r else 0) + (1 if 2 * k * e % r else 0)) for k in range(r)]
        F = {g: f_vals(*graphs[g]) for g in graphs}
        I = [k for k in range(r) if all(F[g][k] == F[g][1] for g in graphs)]
        fF = F["K2"]
        good = all(fF[k] != fF[1] for k in range(r) if k not in I)
        zs = sorted(set(fF))
        rec = {}
        for g in ("P3", "digon"):
            hs = [sum(c[k] * F[g][k] * fF[k] ** j for k in range(r)) for j in range(len(zs))]
            sol = solve_vandermonde(zs, hs)
            got = sol[zs.index(fF[1])]
            want = sum(c[k] for k in I) * F[g][1]
            rec[g] = [str(got), want, got == want]
            good &= got == want
        rows[f"p={p} r={r} alpha=Z^{e}"] = {"I": I, "anchor": "K2", "recovered": rec, "ok": bool(good)}
        ok &= bool(good)
    return {"rows": rows, "ok": ok}


def main():
    t0 = time.time()
    rng = random.Random(20261027)
    checks = {}
    for name, fn in (("1_bch_groups", lambda: part1(rng)), ("2_class_dependence", lambda: part2(rng)),
                     ("3_reduction_to_heisenberg", part3), ("4_hard_pair_structure", part4), ("5_hardness_bookkeeping", part5)):
        checks[name] = fn()
        print(name, checks[name]["ok"], round(time.time() - t0, 1), flush=True)
    allok = all(v["ok"] for v in checks.values())
    checks["ok"] = allok
    out = {"schema_version": 1, "artifact_id": "BEYOND-CLASS2-20261027-001A-P001", "status": "Proved" if allok else "Failed",
           "checks": checks, "seconds": round(time.time() - t0, 1)}
    if "--write" in sys.argv:
        (HERE / "result.json").write_text(json.dumps(out, indent=1, default=str) + "\n")
    print(json.dumps({"status": out["status"], "seconds": out["seconds"]}))
    return 0 if allok else 1


if __name__ == "__main__":
    sys.exit(main())
