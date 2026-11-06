"""Check for CLASSK-DICHOTOMY-20261026-001A-P001: class-(K) counts on gadget surgeries are positive sums of sector
partition functions. numpy + ck_lib.py (this directory); imports cp_lib.py read-only from COPRIME-CLASS2-20261026-001B-P001.
Run: .venv/bin/python check.py [--write] [--quick]

1. The count formula against independent lifting counts on small surgeries, for class-(K) groups that are not Heisenberg
   (cocycles to G/A enumerated, then the affine lifting system solved with the group law; trivial characters and p-torsion
   included; beta not alternating, and its alternating version kappa / 2).
2. Gadget models: for random class-(K) groups, all three slot patterns, every sector k and small multigraphs (parallel edges
   included), the direct obstruction count (no regrouping), the template count and |A23|^-n Z_W agree.
3. The weights: W_k symmetric and positive; constant exactly when its three pairings vanish; the matrix [W(x - y)] has rank one
   exactly then; every hard pair gives a nonconstant W_1 for its slot triple; groups without a hard pair give constant weights
   for every slot triple and sector (negative control).
4. Disjoint unions: every sector count is multiplicative; the assembled count equals sum_k c_k lambda_k^n mu_k^m Z_{W_k}.
"""
import itertools
import json
import random
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
sys.path.insert(1, str(next((ROOT / "proofs/COPRIME-CLASS2-20261026-001B").glob("COPRIME-CLASS2-20261026-001B-P001_*"))))
import ck_lib as K  # noqa: E402
import cp_lib as C  # noqa: E402  (read-only: braid presentations, Heisenberg evaluation of cup products)

QUICK = "--quick" in sys.argv
T31, F41, K52, S61 = ([1, 1, 1], 2), ([1, -2, 1, -2], 3), ([1, 1, 1, 2, -1, 2], 3), ([1, 1, 2, -1, -3, 2, -3], 4)
KNOTS = {"3_1": T31, "4_1": F41, "5_2": K52, "6_1": S61}


# ------------------------------------------------------------------------------------------------ part 1: count formula

def fox(U, rels, mult, p):
    """rows of c(relator) in terms of c(generator) for a cocycle twisted by mult on every (meridian) generator"""
    inv = pow(mult, p - 2, p)
    rows = []
    for rel in rels:
        row, pref = [0] * U, 1
        for g, s in rel:
            for _ in range(abs(s)):
                if s > 0:
                    row[g] = (row[g] + pref) % p
                    pref = pref * mult % p
                else:
                    pref = pref * inv % p
                    row[g] = (row[g] - pref) % p
        rows.append(row)
    return rows


def z1_b1_h1(U, rels, mult, p):
    Z = K.nullspace(fox(U, rels, mult, p), U, p)
    B = [[(mult - 1) % p] * U] if mult != 1 else []
    H, basis = [], list(B)
    for z in Z:
        if K.rank(basis + [z], p) > len(basis):
            basis.append(z)
            H.append(z)
    return Z, len(B), H


def span(vectors, p):
    """all elements of the span of a nonempty list of vectors"""
    out = []
    for coefs in itertools.product(range(p), repeat=len(vectors)):
        out.append(tuple(sum(c * v[g] for c, v in zip(coefs, vectors)) % p for g in range(len(vectors[0]))))
    return out


def count_direct(G, U, rels, k):
    """sum over cocycles c in Z^1(pi; B_psik) of the number of lifts, by the group law (no cup products)"""
    p = G.p
    Zs = []
    for i in range(G.dB):
        Z, _, _ = z1_b1_h1(U, rels, pow(G.bmul[i], k, p), p)
        Zs.append(span(Z, p) if Z else [tuple([0] * U)])
    lin = []
    for j in range(G.dA):
        Fj = fox(U, rels, pow(G.amul[j], k, p), p)
        cols = [[Fj[t][g] for t in range(len(rels))] for g in range(U)]
        lin.append((K.rref(cols, p), U - K.rank(Fj, p)))
    n_lifts = p ** sum(nl for _, nl in lin)
    good = 0
    for c in itertools.product(*Zs):
        imgs = [(tuple([0] * G.dA), tuple(c[i][g] for i in range(G.dB)), k % G.r) for g in range(U)]
        consts = [[] for _ in range(G.dA)]
        for rel in rels:
            a, b, e = G.word(rel, imgs)
            assert not any(b) and e == 0, "not a cocycle"
            for j in range(G.dA):
                consts[j].append(a[j])
        ok = True
        for j, ((R, piv), _) in enumerate(lin):
            v = list(consts[j])
            for row, cc in zip(R, piv):
                f = v[cc]
                if f:
                    v = [(x - f * y) % p for x, y in zip(v, row)]
            if any(v):
                ok = False
                break
        good += ok
    return good * n_lifts


def count_cohomological(G, U, rels, k):
    """sum over x in H^1(pi; B_psik) of [o(x) = 0] times |Z^1(A)| |B^1(B)|, o(x) = sum beta (x_i u x_i2) from Heisenberg
    evaluation of cup products, classes reduced modulo coboundaries"""
    p, r = G.p, G.r
    Hs, b1 = [], 0
    for i in range(G.dB):
        _, bb, H = z1_b1_h1(U, rels, pow(G.bmul[i], k, p), p)
        Hs.append(H)
        b1 += bb
    z1a = 0
    for j in range(G.dA):
        Z, _, _ = z1_b1_h1(U, rels, pow(G.amul[j], k, p), p)
        z1a += len(Z)
    cup = {}
    reducers = {}
    for (i, i2, j), v in G.beta.items():
        if (i, i2) in cup:
            continue
        mult = pow(G.bmul[i] * G.bmul[i2], k, p)
        if mult not in reducers:
            Dz = fox(U, rels, mult, p)
            cols = [[Dz[t][g] for t in range(len(rels))] for g in range(U)]
            reducers[mult] = C.Reducer(cols, p, len(rels))
        Hg = C.Group(p, r, G.bmul[i], G.bmul[i2])
        tab = {}
        for s, hx in enumerate(Hs[i]):
            for t, hy in enumerate(Hs[i2]):
                imgs = [(hx[g], hy[g], 0, k % r) for g in range(U)]
                vec = []
                for rel in rels:
                    X, Y, Zc, e = Hg.word(rel, imgs)
                    assert X == 0 and Y == 0 and e == 0
                    vec.append(Zc)
                tab[(s, t)] = reducers[mult].reduce(vec)
        cup[(i, i2)] = tab
    dims = [len(H) for H in Hs]
    N = 0
    nrel = len(rels)
    for x in itertools.product(*[list(itertools.product(range(p), repeat=d)) for d in dims]):
        ok = True
        for j in range(G.dA):
            v = [0] * nrel
            for (i, i2, jj), b in G.beta.items():
                if jj != j:
                    continue
                for (s, t), cl in cup[(i, i2)].items():
                    f = b * x[i][s] * x[i2][t] % p
                    if f:
                        v = [(a + f * c) % p for a, c in zip(v, cl)]
            if any(v):
                ok = False
                break
        N += ok
    return p ** z1a * p ** b1 * N


def part1():
    rows, ok = {}, True
    groups = {
        # p = 5, r = 4 (Z = 2): free class-2 pieces graded (1, 1, 2) with a symmetric diagonal term in the trivial character
        "G1 p=5 r=4 B(1,1,2)": K.KGroup(5, 4, [1, 1, 2], [2, 3, 3, 0],
                                         {(0, 1, 0): 1, (0, 2, 1): 2, (1, 2, 2): 3, (2, 2, 3): 1, (1, 0, 0): 3}),
        # trivial character in B, commutators with it (no hard pair): exercises H^1(M; F_p) on p-torsion surgeries
        "G2 p=5 r=4 B(0,1,3)": K.KGroup(5, 4, [0, 1, 3], [1, 0, 3], {(0, 1, 0): 1, (1, 2, 1): 2, (0, 2, 2): 4}),
        # p = 7, r = 6 (Z = 3): characters 3, 2, 6, 6
        "G3 p=7 r=6 B(1,2,3,3)": K.KGroup(7, 6, [1, 2, 3, 3], [3, 4, 5, 0],
                                           {(0, 1, 0): 1, (0, 2, 1): 2, (1, 3, 2): 1, (2, 3, 3): 3}),
        # p = 7, r = 3: three coordinates of one character of order 3 (pattern {s, s, s}), free class 2
        "G4 p=7 r=3 B(1,1,1)": K.KGroup(7, 3, [1, 1, 1], [2, 2, 2], {(0, 1, 0): 1, (0, 2, 1): 1, (1, 2, 2): 1}),
    }
    cases = [("G1 p=5 r=4 B(1,1,2)", "3_1", [4, 20]), ("G1 p=5 r=4 B(1,1,2)", "6_1", [4]),
             ("G2 p=5 r=4 B(0,1,3)", "3_1", [4, 20]), ("G2 p=5 r=4 B(0,1,3)", "4_1", [20]),
             ("G3 p=7 r=6 B(1,2,3,3)", "3_1", [6]), ("G3 p=7 r=6 B(1,2,3,3)", "6_1", [6]),
             ("G4 p=7 r=3 B(1,1,1)", "4_1", [3]), ("G4 p=7 r=3 B(1,1,1)", "3_1", [3, 21])]
    if QUICK:
        cases = cases[:3]
    for gname, kn, surgs in cases:
        G = groups[gname]
        Galt = G.alternating_version()
        word, nstr = KNOTS[kn]
        for s in surgs:
            U, rels, _ = C.presentation(word, nstr, s)
            per = {}
            tot_d = tot_c = tot_a = 0
            for k in range(G.r):
                d = count_direct(G, U, rels, k)
                c = count_cohomological(G, U, rels, k)
                a = count_cohomological(Galt, U, rels, k)
                per[k] = [d, c, a]
                tot_d, tot_c, tot_a = tot_d + d, tot_c + c, tot_a + a
            good = all(v[0] == v[1] == v[2] for v in per.values())
            rows[f"{gname} on S^3_{s}({kn})"] = {"per_sector [direct lifts, cohomological, cohomological with kappa/2]": per,
                                                 "total": tot_d, "ok": good}
            ok &= good
    return {"rows": rows, "ok": ok}


# ------------------------------------------------------------------------------------------------ part 2: gadget models

GRAPHS = {
    "K2": (2, [(0, 1)]),
    "P3": (3, [(0, 1), (1, 2)]),
    "digon": (2, [(0, 1), (0, 1)]),
    "K3": (3, [(0, 1), (1, 2), (2, 0)]),
    "K2+K2": (4, [(0, 1), (2, 3)]),
}

SLOTS = [  # (p, r, S)
    (5, 4, (1, 1, 2)), (5, 4, (3, 3, 2)),
    (7, 3, (1, 1, 1)), (7, 3, (2, 2, 2)),
    (7, 6, (1, 2, 3)), (7, 6, (3, 4, 5)), (7, 6, (1, 1, 4)), (7, 6, (5, 5, 2)), (7, 6, (2, 2, 2)), (7, 6, (4, 4, 4)),
    (13, 4, (1, 1, 2)), (13, 6, (1, 2, 3)), (13, 12, (1, 4, 7)), (13, 12, (2, 2, 8)), (13, 12, (4, 4, 4)),
    (11, 5, (1, 1, 3)),
]


def size_ok(G, gad, k, budget):
    """enumeration sizes of the template count and of the translation-reduced partition function"""
    sd = K.SectorData(G, gad, k)
    t = G.p ** (gad.n * len(sd.B1) + len(gad.edges) * len(sd.B2))
    comps = len({min(c) for c in components(gad.n, gad.edges)})
    f = (G.p ** (len(sd.B1) + len(sd.A23))) ** (gad.n - comps)
    return t <= budget and f <= budget


def components(n, edges):
    parent = list(range(n))

    def find(a):
        while parent[a] != a:
            a = parent[a]
        return a
    for u, v in edges:
        parent[find(u)] = find(v)
    out = {}
    for a in range(n):
        out.setdefault(find(a), []).append(a)
    return list(out.values())


def free_factor(G, gad, k):
    """prod over B coordinates whose regraded character is nontrivial and outside S of p^(d_theta)"""
    d = K.base_dims(gad.summand_counts(), G.r)
    return G.p ** sum(d.get(k * e % G.r, 0) for e in G.bexp if k * e % G.r and (k * e % G.r) not in set(gad.S))


def structured_group(p, r, S):
    """free class 2 on the slot coordinates (two coordinates for a repeated slot character, three for P3), graded"""
    Sn, pat = K.normalize_slots(S, r)
    bexp = list(Sn) if pat == "distinct" else ([Sn[0], Sn[0], Sn[2]] if pat == "sst" else [Sn[0]] * 3)
    aexp, beta = [], {}
    for i in range(len(bexp)):
        for i2 in range(i + 1, len(bexp)):
            aexp.append((bexp[i] + bexp[i2]) % r)
            beta[(i, i2, len(aexp) - 1)] = 1
    return K.KGroup(p, r, bexp, aexp, beta)


KNOWN = [
    # (label, p, r, bexp, aexp, beta, S, graph, k, expected sector count N_k including free factors, source)
    ("free class 2, pattern 1", 7, 6, [1, 2, 3], [3, 4, 5], {(0, 1, 0): 1, (0, 2, 1): 1, (1, 2, 2): 1}, (1, 2, 3), "K2", 1,
     133, "PATTERN1-CHECKPOINT-20261026-001 (actual surgery)"),
    ("free class 2, pattern 1", 7, 6, [1, 2, 3], [3, 4, 5], {(0, 1, 0): 1, (0, 2, 1): 1, (1, 2, 2): 1}, (1, 2, 3), "K2", 5,
     2401, "PATTERN1-CHECKPOINT-20261026-001 (actual surgery)"),
    ("free class 2, pattern 1", 7, 6, [1, 2, 3], [3, 4, 5], {(0, 1, 0): 1, (0, 2, 1): 1, (1, 2, 2): 1}, (1, 2, 3), "digon", 1,
     2737, "PATTERN1-CHECKPOINT-20261026-001 (actual surgery)"),
    ("free class 2, pattern 1", 7, 6, [1, 2, 3], [3, 4, 5], {(0, 1, 0): 1, (0, 2, 1): 1, (1, 2, 2): 1}, (1, 2, 3), "digon", 5,
     117649, "PATTERN1-CHECKPOINT-20261026-001 (actual surgery)"),
    ("Heisenberg alpha = beta, s^3 = 1 (D pattern 3)", 7, 3, [1, 1], [2], {(0, 1, 0): 1}, (1, 1, 1), "digon", 1,
     46101601, "COPRIME-CLASS2-20261026-001D end-to-end"),
    ("Heisenberg alpha = beta (D pattern 2)", 5, 4, [1, 1], [2], {(0, 1, 0): 1}, (1, 1, 2), "K3", 1,
     3240625, "COPRIME-CLASS2-20261026-001D end-to-end"),
    ("Heisenberg gamma = alpha (D pattern 4)", 5, 4, [1, 2], [3], {(0, 1, 0): 1}, (1, 1, 2), "K3", 1,
     25925, "COPRIME-CLASS2-20261026-001D end-to-end"),
]


def make_group(rng, p, r, S, extra, hard=True, density=0.8, max_dB=5):
    """random class-(K) group: B contains the slot characters (with multiplicity), preimages of slot characters under
    `extra` random powers k (so that sectors other than psi become nonconstant), and kappa is dense"""
    Sn, pat = K.normalize_slots(S, r)
    bexp = []
    for s in sorted(set(Sn)):
        mult = 2 if (pat != "distinct" and s == Sn[0]) else 1
        bexp += [s] * mult
    for _ in range(extra):
        k = rng.randrange(2, r) if r > 2 else 1
        s = rng.choice(Sn)
        pre = [e for e in range(r) if k * e % r == s]
        bexp.append(rng.choice(pre) if pre else rng.randrange(r))
    bexp = bexp[:max_dB]
    rng.shuffle(bexp)
    G = K.random_kgroup(rng, p, r, bexp, density=density)
    if not hard:
        beta = {key: v for key, v in G.beta.items()
                if not (G.bexp[key[0]] and G.bexp[key[1]] and (G.bexp[key[0]] + G.bexp[key[1]]) % r)}
        G = K.KGroup(p, r, G.bexp, G.aexp, beta)
    return G


def u_size(G, gad, k):
    sd = K.SectorData(G, gad, k)
    return G.p ** (len(sd.B1) + len(sd.A23))


def one_case(G, gad, k, budget):
    tc = K.template_count(G, gad, k)
    fc, W, U, sd, _ = K.fourier_count(G, gad, k)
    row = {"template": tc, "fourier": fc}
    good = tc == fc
    dc, nvar, ncov = K.direct_count(G, gad, k, max_enum=budget)
    row["cover dims"] = ncov
    if dc is not None:
        row["direct"] = dc
        good &= dc == tc
    nonconst = len(set(W.values())) > 1
    good &= nonconst == sd.nonzero()
    p = G.p
    good &= all(W[u] == W[tuple((-x) % p for x in u)] and W[u] > 0 for u in U)
    row["W nonconstant"] = nonconst
    row["|U|"] = len(U)
    row["ok"] = bool(good)
    return row, dc is not None, nonconst


def part2(rng, budget):
    rows, ok = {}, True
    stats = {"cases": 0, "three-way": 0, "nonconstant": 0, "nonconstant three-way": 0, "patterns": {}, "known values": 0}
    # known values
    for (lab, p, r, bexp, aexp, beta, S, gname, k, expect, src) in KNOWN:
        G = K.KGroup(p, r, bexp, aexp, beta)
        n, E = GRAPHS[gname]
        gad = K.Gadget(S, n, E, r, p)
        row, three, nc = one_case(G, gad, k, budget)
        f = free_factor(G, gad, k)
        row["expected N_k"] = expect
        row["source"] = src
        row["N_k = free factor x template"] = f * row["template"]
        good = row["ok"] and f * row["template"] == expect and three
        row["ok"] = bool(good)
        ok &= bool(good)
        stats["known values"] += 1
        rows[f"known: {lab}, p={p} r={r} {gname} k={k}"] = row
    print("  part 2 known values", ok, round(time.time() - T0, 1), flush=True)
    for (p, r, S) in SLOTS:
        groups = [("free class 2 on the slots", structured_group(p, r, S))]
        Sn, pat = K.normalize_slots(S, r)
        if pat == "sst":
            groups.append(("one coordinate per slot character", K.KGroup(p, r, [Sn[0], Sn[2]], [(Sn[0] + Sn[2]) % r],
                                                                         {(0, 1, 0): 1})))
        if pat == "sss":
            groups.append(("two coordinates (Heisenberg)", K.KGroup(p, r, [Sn[0], Sn[0]], [2 * Sn[0] % r], {(0, 1, 0): 1})))
        for gi in range(2 if p <= 7 and not QUICK else 1):
            groups.append((f"random {gi}", make_group(rng, p, r, S, extra=rng.randrange(1, 4))))
        for glab, G in groups:
            for gname, (n, E) in GRAPHS.items():
                gad = K.Gadget(S, n, E, r, p)
                for k in range(r):
                    if not size_ok(G, gad, k, budget):
                        continue
                    row, three, nc = one_case(G, gad, k, budget)
                    stats["cases"] += 1
                    stats["three-way"] += three
                    stats["nonconstant"] += nc
                    stats["nonconstant three-way"] += nc and three
                    stats["patterns"][gad.pattern] = stats["patterns"].get(gad.pattern, 0) + 1
                    ok &= row["ok"]
                    rows[f"p={p} r={r} S={S} {glab} B={G.bexp} {gname} k={k}"] = row
        print("  part 2", (p, r, S), stats["cases"], stats["nonconstant"], round(time.time() - T0, 1), flush=True)
    return {"rows": rows, "stats": stats, "ok": ok}


def part3(rng):
    """weights and ranks; hard pairs force a nonconstant W_1; no hard pair gives constant weights everywhere"""
    rows, ok = {}, True
    hard_tested = neg_tested = rank_tested = 0
    for (p, r, S) in SLOTS:
        for trial in range(3 if not QUICK else 1):
            G = make_group(rng, p, r, S, extra=rng.randrange(1, 4))
            gad = K.Gadget(S, 2, [(0, 1)], r, p)
            # every hard pair of G gives its slot triple a nonconstant W_1
            for (e, e2) in sorted(G.hard_pairs()):
                S2 = (e, e2, (-(e + e2)) % r)
                gad2 = K.Gadget(S2, 2, [(0, 1)], r, p)
                if u_size(G, gad2, 1) > 5000:
                    continue
                W, U, sd = K.weight_table(G, gad2, 1)
                nc = len(set(W.values())) > 1
                rows[f"p={p} r={r} B={G.bexp} hard pair {(e, e2)} -> S={gad2.S} ({gad2.pattern})"] = {
                    "W_1 nonconstant": nc, "pairings nonzero": sd.nonzero()}
                ok &= nc and sd.nonzero()
                hard_tested += 1
            # ranks of [W(x - y)] for every sector (small U only)
            for k in range(r):
                if u_size(G, gad, k) > 400:
                    continue
                W, U, sd = K.weight_table(G, gad, k)
                Mat = np.array(K.weight_matrix(W, U, p), dtype=float)
                rk = int(np.linalg.matrix_rank(Mat))
                nc = len(set(W.values())) > 1
                good = (rk >= 2) == nc and (rk >= 1)
                ok &= good
                rank_tested += 1
                if nc:
                    rows.setdefault(f"rank examples p={p} r={r}", []).append([k, len(U), rk])
            # negative control: no hard pair -> every sector constant, for every slot triple of the same (p, r)
            Gn = make_group(rng, p, r, S, extra=rng.randrange(1, 4), hard=False)
            assert not Gn.hard_pairs()
            for (p2, r2, S2) in SLOTS:
                if (p2, r2) != (p, r):
                    continue
                g2 = K.Gadget(S2, 2, [(0, 1)], r, p)
                for k in range(r):
                    if u_size(Gn, g2, k) > 5000:
                        continue
                    W, U, sd = K.weight_table(Gn, g2, k)
                    good = len(set(W.values())) == 1 and not sd.nonzero()
                    ok &= good
                    neg_tested += 1
    return {"rows": rows, "hard pairs tested": hard_tested, "ranks tested": rank_tested,
            "negative controls tested": neg_tested, "ok": ok}


def part4(rng):
    """multiplicativity over disjoint unions and the assembled formula"""
    rows, ok = {}, True
    for (p, r, S) in [(5, 4, (1, 1, 2)), (7, 6, (1, 2, 3)), (7, 6, (1, 1, 4)), (7, 3, (1, 1, 1))]:
        G = make_group(rng, p, r, S, extra=1)
        for k in range(r):
            g1 = K.Gadget(S, 2, [(0, 1)], r, p)
            g2 = K.Gadget(S, 4, [(0, 1), (2, 3)], r, p)
            if not size_ok(G, g2, k, 10 ** 6):
                continue
            a, b = K.template_count(G, g1, k), K.template_count(G, g2, k)
            good = b == a * a
            rows[f"p={p} r={r} S={S} B={G.bexp} k={k}: N(K2+K2) = N(K2)^2"] = [b, a, good]
            ok &= good
        # assembled count: sum_k c_k (|H1(A)| free) N_k = sum_k c_k lambda^n mu^m Z_W
        for gname in ("K2", "P3", "digon"):
            n, E = GRAPHS[gname]
            gad = K.Gadget(S, n, E, r, p)
            if not all(size_ok(G, gad, k, 10 ** 6) for k in range(r)):
                continue
            tot, parts = K.model_hom_count(G, gad)
            pf = 0
            for k in range(r):
                ck, a_, b_ = K.sector_constants(G, S, k)
                W, U, sd = K.weight_table(G, gad, k)
                Z, _ = K.partition_function(W, U, n, E, p)
                num = ck * Z * p ** (b_ * len(E))
                pf_k = num * p ** (a_ * n) if a_ >= 0 else num // p ** (-a_ * n)
                assert a_ >= 0 or num % p ** (-a_ * n) == 0
                pf += pf_k
            good = pf == tot
            rows[f"p={p} r={r} S={S} B={G.bexp} {gname}: assembled"] = [tot, pf, good]
            ok &= good
    return {"rows": rows, "ok": ok}


T0 = time.time()


def main():
    t0 = time.time()
    rng = random.Random(20261026)
    out = {"schema_version": 1, "artifact_id": "CLASSK-DICHOTOMY-20261026-001A-P001"}
    checks = {}
    checks["1_count_formula_vs_lifting"] = part1()
    print("part 1", checks["1_count_formula_vs_lifting"]["ok"], round(time.time() - t0, 1), flush=True)
    checks["2_gadget_counts"] = part2(rng, budget=3 * 10 ** 5 if QUICK else 2 * 10 ** 6)
    print("part 2", checks["2_gadget_counts"]["ok"], checks["2_gadget_counts"]["stats"], round(time.time() - t0, 1), flush=True)
    checks["3_weights_and_ranks"] = part3(rng)
    print("part 3", checks["3_weights_and_ranks"]["ok"], {k: v for k, v in checks["3_weights_and_ranks"].items() if "tested" in k},
          round(time.time() - t0, 1), flush=True)
    checks["4_disjoint_unions_and_assembly"] = part4(rng)
    print("part 4", checks["4_disjoint_unions_and_assembly"]["ok"], round(time.time() - t0, 1), flush=True)
    allok = all(v["ok"] for v in checks.values())
    checks["ok"] = allok
    out["status"] = "Proved" if allok else "Failed"
    out["checks"] = checks
    out["seconds"] = round(time.time() - t0, 1)
    if "--write" in sys.argv:
        (HERE / "result.json").write_text(json.dumps(out, indent=1, default=str) + "\n")
    print(json.dumps({"status": out["status"], "seconds": out["seconds"]}))
    return 0 if allok else 1


if __name__ == "__main__":
    sys.exit(main())
