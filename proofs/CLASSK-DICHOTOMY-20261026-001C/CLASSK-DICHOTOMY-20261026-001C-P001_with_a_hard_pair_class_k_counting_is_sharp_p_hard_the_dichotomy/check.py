"""Check for CLASSK-DICHOTOMY-20261026-001C-P001: with a hard pair, class-(K) counting is #P-hard with H1 = Z/r.
numpy; imports read-only: ck_lib.py (CLASSK-DICHOTOMY-20261026-001A-P001), predict.py and ck_specs.py and the frozen artifact
rows.json of CLASSK-DICHOTOMY-20261026-001B-E001. Run: .venv/bin/python check.py [--write]

1. Bulatov-Grohe hypotheses: W_1 positive, even, nonconstant and rank [W_1(x - y)] >= 2 for every hard pair of the experiment
   groups and of random groups; rank one in every sector for groups without a hard pair.
2. Lemma I on concrete groups: anchors among small multigraphs; exact Vandermonde recovery of (sum_I c_k) f_1(Gamma); h(Gamma + F)
   also computed directly on the disjoint union.
3. Knot groups on the extended model: sum over beta of f_{k,beta} = knot count; f_{1,0} = closed count; f_{k,beta}
   multiplicative on K2 + K2.
4. End to end (frozen experiment rows): closed counts on K2 + K2 are squares of those on K2; knot-exterior counts on K2 + K2 equal
   sum over beta of f_{k,beta}(K2)^2.
5. The refinement: hard pairs of G_d for d | r.
6. Size data: crossings of the experiment's surgeries.
"""
import itertools
import json
import random
import sys
import time
from fractions import Fraction
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
EXP = next((ROOT / "experiments/CLASSK-DICHOTOMY-20261026-001B").glob("CLASSK-DICHOTOMY-20261026-001B-E001_*"))
ART = ROOT / "artifacts/CLASSK-DICHOTOMY-20261026-001B" / EXP.name
sys.path.insert(0, str(EXP))
import ck_specs as SP  # noqa: E402  (puts ck_lib on the path)
import predict as PR  # noqa: E402
L = SP.L

GRAPHS = {
    "K2": (2, [(0, 1)]), "P3": (3, [(0, 1), (1, 2)]), "digon": (2, [(0, 1), (0, 1)]), "K3": (3, [(0, 1), (1, 2), (2, 0)]),
    "triple edge": (2, [(0, 1)] * 3), "K2+K2": (4, [(0, 1), (2, 3)]), "P3+K2": (5, [(0, 1), (1, 2), (3, 4)]),
}


def union(g1, g2):
    (n1, e1), (n2, e2) = g1, g2
    return (n1 + n2, list(e1) + [(u + n1, v + n1) for u, v in e2])


# ------------------------------------------------------------------------------------------------ part 1

def u_size(G, S, k):
    gad = L.Gadget(S, 2, [(0, 1)], G.r, G.p)
    sd = L.SectorData(G, gad, k)
    return G.p ** (len(sd.B1) + len(sd.A23)), sd


def rank_of_W(G, S, k, with_rank=True):
    gad = L.Gadget(S, 2, [(0, 1)], G.r, G.p)
    W, U, sd = L.weight_table(G, gad, k)
    if len(U) > 400 or not with_rank:
        return None, len(U), len(set(W.values())) > 1, all(W[u] > 0 for u in U), sd.nonzero()
    M = np.array(L.weight_matrix(W, U, G.p), dtype=float)
    even = all(W[u] == W[tuple((-x) % G.p for x in u)] for u in U)
    return int(np.linalg.matrix_rank(M)), len(U), len(set(W.values())) > 1, all(W[u] > 0 for u in U) and even, sd.nonzero()


def part1(rng):
    rows, ok = {}, True
    groups = []
    for (p, r), gs in SP.GROUPS.items():
        for name, (bexp, pairs) in gs.items():
            groups.append((f"experiment: {name}", SP.group(p, r, bexp, pairs)))
    for (p, r, S) in [(7, 6, (1, 2, 3)), (7, 6, (1, 1, 4)), (7, 6, (2, 2, 2)), (13, 12, (1, 4, 7)), (5, 4, (1, 1, 2)),
                      (13, 3, (1, 1, 1))]:
        for t in range(3):
            bexp = list(K for K in S) + [rng.randrange(r) for _ in range(rng.randrange(0, 2))]
            groups.append((f"random p={p} r={r}", L.random_kgroup(rng, p, r, bexp, density=0.7, reuse=0.7)))
    nh = nrank = skipped = 0
    for gname, G in groups:
        for (e, e2) in sorted(G.hard_pairs()):
            S = (e, e2, (-(e + e2)) % G.r)
            nU, sd0 = u_size(G, S, 1)
            if nU > 10 ** 5:
                # too large to tabulate W: the pairing criterion of Theorem A (b) still applies
                ok &= sd0.nonzero()
                skipped += 1
                continue
            rk, nU, nc, pos, nz = rank_of_W(G, S, 1)
            good = nc and pos and nz and (rk is None or rk >= 2)
            rows[f"{gname} p={G.p} r={G.r} B={G.bexp} hard pair {(e, e2)}"] = {"|U|": nU, "rank": rk, "nonconstant": nc,
                                                                              "positive and even": pos, "ok": good}
            ok &= good
            nh += 1
            nrank += rk is not None
    # groups without a hard pair: every sector, every slot triple of (p, r): rank one
    neg = 0
    for (p, r) in [(7, 6), (5, 4)]:
        for t in range(4):
            bexp = [rng.randrange(r) for _ in range(4)]
            G = L.random_kgroup(rng, p, r, bexp, density=0.9)
            beta = {key: v for key, v in G.beta.items()
                    if not (G.bexp[key[0]] and G.bexp[key[1]] and (G.bexp[key[0]] + G.bexp[key[1]]) % r)}
            G = L.KGroup(p, r, G.bexp, G.aexp, beta)
            assert not G.hard_pairs()
            for S in {(a, b, (-(a + b)) % r) for a in range(1, r) for b in range(1, r) if (a + b) % r}:
                for k in range(r):
                    nU, sd0 = u_size(G, S, k)
                    if nU > 10 ** 5:
                        ok &= not sd0.nonzero()
                        neg += 1
                        continue
                    rk, nU, nc, pos, nz = rank_of_W(G, S, k, with_rank=False)
                    good = (not nc) and (not nz)          # a constant weight has rank one (Theorem A (b))
                    ok &= good
                    neg += 1
    return {"rows": rows, "hard pairs": nh, "ranks computed": nrank, "hard pairs too large to tabulate (pairing checked)": skipped,
            "negative cases": neg, "ok": ok}


# ------------------------------------------------------------------------------------------------ part 2

def f_values(G, S, graph):
    """f_k(Gamma) = sector-k contribution / c_k = |H^1(A_psik)| * free factor * template count"""
    n, E = graph
    gad = L.Gadget(S, n, E, G.r, G.p)
    d = L.base_dims(gad.summand_counts(), G.r)
    out = []
    for k in range(G.r):
        h1a = G.p ** sum(d.get(k * e % G.r, 0) for e in G.aexp if k * e % G.r)
        free = G.p ** sum(d.get(k * e % G.r, 0) for e in G.bexp if k * e % G.r and (k * e % G.r) not in set(gad.S))
        out.append(h1a * free * L.template_count(G, gad, k))
    return out


def c_values(G):
    return [G.p ** (sum(1 for e in G.bexp if k * e % G.r) + sum(1 for e in G.aexp if k * e % G.r)) for k in range(G.r)]


def solve_vandermonde(zs, hs):
    """solve sum_i g_i z_i^j = h_j (j = 0..R-1) exactly"""
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


def part2():
    rows, ok = {}, True
    cases = [
        ("two nonconstant sectors", 7, 6, [1, 2, 3, 4, 5], [(0, 1), (0, 2), (1, 2), (4, 3)], (1, 2, 3)),
        ("two equivalent nonconstant sectors", 7, 6, [1, 2, 3, 5, 4], [(0, 1), (0, 2), (1, 2), (3, 4), (3, 2), (4, 2)],
         (1, 2, 3)),
        ("Heisenberg (3, 2)", 7, 6, [1, 2], [(0, 1)], (1, 2, 3)),
        ("pattern 2, free class 2 on (2, 2, 4) at p = 5", 5, 4, [1, 1, 2], [(0, 1), (0, 2), (1, 2)], (1, 1, 2)),
    ]
    for (lab, p, r, bexp, pairs, S) in cases:
        G = SP.group(p, r, bexp, pairs)
        c = c_values(G)

        def small(g):
            n, E = GRAPHS[g]
            gad = L.Gadget(S, n, E, r, p)
            return all(p ** (n * len(L.SectorData(G, gad, k).B1) + len(E) * len(L.SectorData(G, gad, k).B2)) <= 3 * 10 ** 6
                       for k in range(r))
        family = [g for g in ["K2", "P3", "digon", "K3", "triple edge"] if small(g)]
        F = {g: f_values(G, S, GRAPHS[g]) for g in family}
        # equivalence classes of sectors on the family (I = sectors agreeing with f_1 on every family graph)
        I = [k for k in range(r) if all(F[g][k] == F[g][1] for g in family)]
        # anchor: a family graph, or a disjoint union of two, separating f_1 from every sector outside I
        anchor = None
        cands = [(g,) for g in family] + [(g, h) for g in family for h in family]
        for cand in cands:
            vals = [1] * r
            for g in cand:
                vals = [v * w for v, w in zip(vals, F[g])]
            if all(vals[k] != vals[1] for k in range(r) if k not in I):
                anchor, fF = cand, vals
                break
        row = {"family": family, "I (sectors equal to f_1 on the family)": I, "anchor": anchor}
        good = anchor is not None
        if good:
            zs = sorted(set(fF))
            row["R (distinct anchor values)"] = len(zs)
            for g in [g for g in ("K2", "P3", "digon", "K3") if g in F]:
                fG = F[g]
                hs = [sum(c[k] * fG[k] * fF[k] ** j for k in range(r)) for j in range(len(zs))]
                sol = solve_vandermonde(zs, hs)
                got = sol[zs.index(fF[1])]
                want = sum(c[k] for k in I) * fG[1]
                row[f"recovered on {g}"] = [str(got), want, got == want]
                good &= got == want
            # direct check of multiplicativity on a union small enough to enumerate (an anchor component if possible)
            def union_size(g):
                n_, E_ = union(GRAPHS["K2"], GRAPHS[g])
                gad = L.Gadget(S, n_, E_, r, p)
                return max(p ** (n_ * len(L.SectorData(G, gad, k).B1) + len(E_) * len(L.SectorData(G, gad, k).B2))
                           for k in range(r))
            g0 = next((g for g in list(anchor) + ["K2"] if union_size(g) <= 2 * 10 ** 6), None)
            if g0 is not None:
                fu = f_values(G, S, union(GRAPHS["K2"], GRAPHS[g0]))
                prod = [a * b for a, b in zip(F["K2"], F[g0])]
                row[f"f_k(K2 + {g0}) = f_k(K2) f_k({g0})"] = fu == prod
                good &= fu == prod
        row["ok"] = bool(good)
        ok &= bool(good)
        rows[lab] = row
    return {"rows": rows, "ok": ok}


# ------------------------------------------------------------------------------------------------ part 3

def count_affine_bilinear(p, groups, forms):
    """#{x : every form vanishes}; forms are dicts with keys (v1, v2) (bilinear), (v,) (linear) and () (constant)"""
    nvar = sum(len(g) for g in groups)
    gof = {v: gi for gi, g in enumerate(groups) for v in g}
    inter, selfl = set(), set()
    for f in forms:
        for key, cc in f.items():
            if len(key) == 2 and cc % p:
                a, b = gof[key[0]], gof[key[1]]
                if a == b:
                    selfl.add(a)
                else:
                    inter.add((min(a, b), max(a, b)))
    ng = len(groups)
    best = None
    for mask in range(1 << ng):
        cov = {g for g in range(ng) if mask >> g & 1}
        if not selfl <= cov or any(a not in cov and b not in cov for a, b in inter):
            continue
        w = sum(len(groups[g]) for g in cov)
        if best is None or w < best[0]:
            best = (w, cov)
    cov = best[1]
    cv = [v for g in sorted(cov) for v in groups[g]]
    rv = [v for g in range(ng) if g not in cov for v in groups[g]]
    ci, ri = {v: i for i, v in enumerate(cv)}, {v: i for i, v in enumerate(rv)}
    total = 0
    for X in itertools.product(range(p), repeat=len(cv)):
        rows = []
        for f in forms:
            row = [0] * (len(rv) + 1)
            for key, cc in f.items():
                cc %= p
                if not cc:
                    continue
                if len(key) == 0:
                    row[-1] = (row[-1] + cc) % p
                elif len(key) == 1:
                    v = key[0]
                    if v in ci:
                        row[-1] = (row[-1] + cc * X[ci[v]]) % p
                    else:
                        row[ri[v]] = (row[ri[v]] + cc) % p
                else:
                    a, b = key
                    if a in ci and b in ci:
                        row[-1] = (row[-1] + cc * X[ci[a]] * X[ci[b]]) % p
                    elif a in ci:
                        row[ri[b]] = (row[ri[b]] + cc * X[ci[a]]) % p
                    else:
                        row[ri[a]] = (row[ri[a]] + cc * X[ci[b]]) % p
            rows.append(row)
        A = [r_[:-1] for r_ in rows]
        rA = L.rank(A, p) if rows and len(rv) else 0
        rAb = L.rank(rows, p) if rows else 0
        if rA == rAb:
            total += p ** (len(rv) - rA)
    return total


def knot_count_fixed(G, gad, fx, k, beta):
    """the extended-model knot count of sector k with the u-coefficient fixed to beta (a dict over the B coordinates whose
    regraded character is trivial)"""
    p, r = G.p, G.r
    ext, T, coords_of = PR.extended_model(gad, fx, True)
    iu = coords_of[0][0]
    I = [i for i in range(G.dB) if (k * G.bexp[i]) % r in coords_of]
    var, groups = {}, []
    for i in I:
        th = (k * G.bexp[i]) % r
        if th == 0:
            continue
        g = []
        for a in coords_of[th]:
            var[(i, a)] = len(var)
            g.append(var[(i, a)])
        groups.append(g)

    def val(i, a):
        return ("const", beta[i]) if (k * G.bexp[i]) % r == 0 else ("var", var[(i, a)])
    forms = []
    for j in range(G.dA):
        rho = (k * G.aexp[j]) % r
        if rho == 0 or (-rho) % r not in coords_of:
            continue
        for c in coords_of[(-rho) % r]:
            f = {}
            for i in I:
                for i2 in I:
                    if i >= i2:
                        continue
                    v = G.kappa_entry(i, i2, j)
                    if not v:
                        continue
                    for a in coords_of[(k * G.bexp[i]) % r]:
                        for b in coords_of[(k * G.bexp[i2]) % r]:
                            t = int(T[a, b, c])
                            if not t:
                                continue
                            x1, x2 = val(i, a), val(i2, b)
                            coef = v * t
                            if x1[0] == "const" and x2[0] == "const":
                                key = ()
                                coef *= x1[1] * x2[1]
                            elif x1[0] == "const":
                                key = (x2[1],)
                                coef *= x1[1]
                            elif x2[0] == "const":
                                key = (x1[1],)
                                coef *= x2[1]
                            else:
                                key = (x1[1], x2[1])
                            f[key] = (f.get(key, 0) + coef) % p
            f = {key: v for key, v in f.items() if v}
            if f:
                forms.append(f)
    if not groups:
        return 0 if any(() in f and f[()] for f in forms) else 1
    return count_affine_bilinear(p, groups, forms)


def betas(G, k):
    triv = [i for i in range(G.dB) if (k * G.bexp[i]) % G.r == 0]
    for vals in itertools.product(range(G.p), repeat=len(triv)):
        yield dict(zip(triv, vals))


def part3():
    rows, ok = {}, True
    fx_k2 = SP.FIXTURES["P1-K2"]
    fx_u = SP.FIXTURES["P1-K2+K2"]
    tests = [("P1-K2", "trivial-character commutators (1, 3, 2, 6)"), ("P2-K2", "pattern 2 with a trivial character (1, 3, 3, 4)"),
             ("P3-K2", "pattern 3 with a trivial character (1, 2, 2)"), ("P2-K2 at p=5", "with a trivial character (1, 2, 2, 4)"),
             ("P1-K2", "two hard sectors (3, 2, 6, 4, 5)")]
    for fname, gname in tests:
        fx = SP.FIXTURES[fname]
        p, r = fx[0], fx[1]
        G = SP.all_groups(p, r)[gname]
        gad = PR.gadget_of(fx)
        row = {}
        good = True
        for k in range(r):
            fs = {tuple(sorted(b.items())): knot_count_fixed(G, gad, fx, k, b) for b in betas(G, k)}
            total = sum(fs.values())
            knot = PR.model_count(G, gad, fx, k, with_u=True)
            closed = PR.model_count(G, gad, fx, k, with_u=False)
            zero = tuple(sorted({i: 0 for i in range(G.dB) if (k * G.bexp[i]) % r == 0}.items()))
            g1 = total == knot and fs[zero] == closed
            row[f"k={k}"] = {"sum over beta": total, "knot count": knot, "f_(k,0)": fs[zero], "closed count": closed,
                             "number of beta": len(fs), "ok": g1}
            good &= g1
        # multiplicativity of f_{k, beta} on K2 + K2 (pattern 1 only, where the union fixture exists)
        if fname == "P1-K2":
            gadu = PR.gadget_of(fx_u)
            for k in range(r):
                for b in betas(G, k):
                    a = knot_count_fixed(G, gad, fx_k2, k, b)
                    u = knot_count_fixed(G, gadu, fx_u, k, b)
                    good &= u == a * a
            row["f_(k,beta)(K2 + K2) = f_(k,beta)(K2)^2 for every k and beta"] = bool(good)
        row["ok"] = bool(good)
        ok &= bool(good)
        rows[f"{fname} / {gname}"] = row
    return {"rows": rows, "ok": ok}


# ------------------------------------------------------------------------------------------------ part 4

def part4():
    rows, ok = {}, True
    rp = ART / "rows.json"
    if not rp.exists():
        return {"rows": {}, "ok": False, "note": "experiment rows not found"}
    data = json.loads(rp.read_text())
    if data.get("verdict") != "supported":
        return {"rows": {}, "ok": False, "note": f"experiment verdict {data.get('verdict')}"}
    R = data["rows"]
    k2, un = R["P1-K2"]["counts"], R["P1-K2+K2"]["counts"]
    fx = SP.FIXTURES["P1-K2"]
    gad = PR.gadget_of(fx)
    for gname in k2:
        if gname not in un:
            continue
        G = SP.all_groups(7, 6)[gname]
        cl2 = {int(k): v for k, v in k2[gname]["closed measured"].items()}
        clu = {int(k): v for k, v in un[gname]["closed measured"].items()}
        kn2 = {int(k): v for k, v in k2[gname]["knot measured"].items()}
        knu = {int(k): v for k, v in un[gname]["knot measured"].items()}
        sq_closed = all(clu[k] == cl2[k] ** 2 for k in cl2)
        pred_knot = {k: sum(knot_count_fixed(G, gad, fx, k, b) ** 2 for b in betas(G, k)) for k in kn2}
        knot_ok = all(knu[k] == pred_knot[k] for k in kn2)
        not_square = [k for k in kn2 if knu[k] != kn2[k] ** 2]
        rows[gname] = {"closed: N_k(K2+K2) = N_k(K2)^2": sq_closed, "knot: N_k(K2+K2) = sum_beta f_(k,beta)(K2)^2": knot_ok,
                       "sectors where the knot count is not a square": not_square, "ok": sq_closed and knot_ok}
        ok &= sq_closed and knot_ok
    return {"rows": rows, "ok": ok}


# ------------------------------------------------------------------------------------------------ parts 5 and 6

def restricted_hard(G, d):
    """hard pairs of G_d = N x| C_d (C_d the subgroup of order d): characters restricted, exponent e -> e (r/d) mod r"""
    r = G.r
    s = r // d
    out = set()
    for (i, i2, j), v in G.kap.items():
        e, e2 = G.bexp[i] * s % r, G.bexp[i2] * s % r
        if e and e2 and (e + e2) % r:
            out.add((G.bexp[i], G.bexp[i2]))
    return out


def part5():
    rows, ok = {}, True
    tests = [("free class 2 on (3, 2, 6)", 7, 6, [1, 2, 3], [(0, 1), (0, 2), (1, 2)], {1: False, 2: False, 3: False, 6: True}),
             ("free class 2 on (3, 3, 4)", 7, 6, [1, 1, 4], [(0, 1), (0, 2), (1, 2)], {1: False, 2: False, 3: True, 6: True}),
             ("Heisenberg (2, 2), s^3 = 1", 7, 6, [2, 2], [(0, 1)], {1: False, 2: False, 3: True, 6: True}),
             ("Heisenberg (2, 2) at p = 5", 5, 4, [1, 1], [(0, 1)], {1: False, 2: False, 4: True})]
    for (lab, p, r, bexp, pairs, want) in tests:
        G = SP.group(p, r, bexp, pairs)
        got = {d: bool(restricted_hard(G, d)) for d in want}
        rows[lab] = {"G_d has a hard pair, by d": got, "expected": want, "ok": got == want}
        ok &= got == want
    return {"rows": rows, "ok": ok}


def part6():
    rp = ART / "rows.json"
    if not rp.exists():
        return {"ok": False}
    data = json.loads(rp.read_text())
    sizes = {f: {"crossings": r["crossings"], "components": r["components"]} for f, r in data["rows"].items()}
    return {"sizes": sizes, "ok": True}


def main():
    t0 = time.time()
    rng = random.Random(20261027)
    checks = {}
    for name, fn in (("1_bulatov_grohe_hypotheses", lambda: part1(rng)), ("2_anchor_isolation", part2),
                     ("3_knot_groups_extended_model", part3), ("4_end_to_end_disjoint_unions", part4),
                     ("5_refinement_by_subgroups", part5), ("6_size_data", part6)):
        checks[name] = fn()
        print(name, checks[name]["ok"], round(time.time() - t0, 1), flush=True)
    allok = all(v["ok"] for v in checks.values())
    checks["ok"] = allok
    out = {"schema_version": 1, "artifact_id": "CLASSK-DICHOTOMY-20261026-001C-P001", "status": "Proved" if allok else "Failed",
           "checks": checks, "seconds": round(time.time() - t0, 1)}
    if "--write" in sys.argv:
        (HERE / "result.json").write_text(json.dumps(out, indent=1, default=str) + "\n")
    print(json.dumps({"status": out["status"], "seconds": out["seconds"]}))
    return 0 if allok else 1


if __name__ == "__main__":
    sys.exit(main())
