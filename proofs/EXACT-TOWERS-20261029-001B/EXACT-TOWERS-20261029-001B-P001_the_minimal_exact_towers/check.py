"""Checks for EXACT-TOWERS-20261029-001B-P001 (the minimal exact towers: Sierpinski gasket, tetrahedral, Fano).

  0 dependency artifacts bound by the hashes recorded in manifest.json
  1 the three gadgets: relation a placement of the knot, uniform counts (factor c), legs on three distinct copies, pairwise at one
    distance s; (m, h, s, c) = (3, 3, 2, 2), (4, 3, 2, 2), (7, 6, 3, 5); every variable within s of each leg and every copy holding
    a variable within s - 1 of each leg (the conditions of Theorem 1(iii))
  2 the towers up to level 6, 5 and 4: m^k copies, 3 + h(m^k - 1)/(m - 1) variables, corners pairwise at distance s^k, every
    variable within s^k of each corner, and the ball of radius s^j around a corner holding exactly 3 + h(m^j - 1)/(m - 1) variables
  3 the law at every level, by variable elimination on the whole tower up to level 4, 3 and 3: c^((m^k - 1)/(m - 1)) completions on
    every allowed corner tuple and none on the others, so the corner law is uniform on the knot at every level; its information
    values
  4 finite ramification: the bags of the substitution hierarchy form a tree decomposition of width h + 2, and deleting the three
    corners of any node cuts off everything it introduced
  5 softening: allowed tuples weight 1, excluded tuples weight r; the gadget's weights stay two-valued, r' = N(r)/D(r) with the stated
    integer polynomials and factorizations (so 0 < r < r' < 1 for 0 < r < 1), and the linear coefficient is m c (at least 3c by the
    leg-copy lemma of ticket A)
  6 controls: a rebuilding gadget that is not exact (x or (y != z), four copies) changes its corner law from level to level, the
    share of the two tuples far from both excluded tuples increasing over levels 1, 2, 3; in the triangular grid of side 4 (shared
    midpoints) deleting the corners of a corner sub-triangle does not cut it off; a Fano gadget with one line moved is not exact
Run: python3 -B check.py [--write]   (standard library; about a minute)"""
import hashlib, itertools, json, math, os, sys, time
from collections import Counter, defaultdict
from fractions import Fraction

T0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
import tower_lib as TL  # noqa: E402
out, ok_all = {}, True


def report(key, ok, detail):
    global ok_all
    out[key] = {"ok": bool(ok), "detail": detail}
    ok_all &= bool(ok)
    print(("PASS " if ok else "FAIL ") + key + ": " + json.dumps(detail, default=str)[:1500], flush=True)


GADGETS = [(TL.TRIANGLE, (3, 3, 2, 2), 6, 4), (TL.TETRA, (4, 3, 2, 2), 5, 3), (TL.FANO, (7, 6, 3, 5), 4, 3)]


def H(ps):
    return -sum(p * math.log2(p) for p in ps if p > 0)


def info(R):
    """mutual information of two corners and total correlation of the three, uniform law on R"""
    n = len(R)
    pab = Counter((t[0], t[1]) for t in R)
    pa = Counter(t[0] for t in R)
    pb = Counter(t[1] for t in R)
    mi = H([v / n for v in pa.values()]) + H([v / n for v in pb.values()]) - H([v / n for v in pab.values()])
    tc = sum(H([v / n for v in Counter(t[i] for t in R).values()]) for i in range(3)) - math.log2(n)
    return round(mi, 6), round(tc, 6)


def main(write):
    man = json.load(open(os.path.join(HERE, "manifest.json")))
    bad = {p: h for p, h in man["parent_bindings"].items()
           if hashlib.sha256(open(os.path.join(ROOT, p), "rb").read()).hexdigest() != h}
    report("0 dependency artifacts bound by hash", not bad, {"parents": len(man["parent_bindings"]), "mismatched": bad})

    g1 = {}
    ok1 = True
    for g, (m, h, s, c), kmax, kc in GADGETS:
        cnt = TL.relation_counts(g)
        R = frozenset(t for t in TL.cube if cnt[t])
        excl = sorted(set(TL.cube) - R)
        knot = all(sum(a != b for a, b in zip(u, v)) >= 2 for u in excl for v in excl if u != v) and 0 < len(excl)
        vals = {cnt[t] for t in R}
        legs_copies = [i for i, (vs, Q) in enumerate(g[2]) for x in vs if x in "abc"]
        tw = TL.Tower(g, R)
        tw.substitute()
        adj = tw.adjacency()
        d0, d1 = TL.bfs(adj, 0), TL.bfs(adj, 1)
        dist = (d0[1], d0[2], d1[2])
        within, copies_ok = TL.leg_conditions(g, s)
        okg = (knot and vals == {c} and len(g[2]) == m and len(g[1]) == h and len(set(legs_copies)) == 3 and dist == (s, s, s)
               and within and copies_ok)
        ok1 &= okg
        g1[g[0]] = {"excluded": excl, "factor": sorted(vals), "copies": len(g[2]), "hidden": len(g[1]), "legs on copies": legs_copies,
                    "leg distances": dist, "every variable within s of each leg": within,
                    "every copy has a variable within s - 1 of each leg": copies_ok,
                    "dimension log m / log s": round(math.log(m) / math.log(s), 6)}
    report("1 the three gadgets", ok1, g1)

    g2, ok2 = {}, True
    g3, ok3 = {}, True
    g4, ok4 = {}, True
    for g, (m, h, s, c), kmax, kc in GADGETS:
        cnt = TL.relation_counts(g)
        R = frozenset(t for t in TL.cube if cnt[t])
        tw = TL.Tower(g, R)
        rows = []
        for k in range(1, kmax + 1):
            tw.substitute()
            adj = tw.adjacency()
            ds = [TL.bfs(adj, i) for i in range(3)]
            dist = (ds[0][1], ds[0][2], ds[1][2])
            ecc = [max(d.values()) for d in ds]
            balls = [sum(1 for v in ds[0].values() if v <= s ** j) for j in range(k + 1)]
            pred_balls = [3 + h * (m ** j - 1) // (m - 1) for j in range(k + 1)]
            okk = (len(tw.copies) == m ** k and tw.nvars == 3 + h * (m ** k - 1) // (m - 1) and dist == (s ** k,) * 3
                   and ecc == [s ** k] * 3 and balls == pred_balls and len(ds[0]) == tw.nvars)
            ok2 &= okk
            rows.append({"level": k, "copies": len(tw.copies), "variables": tw.nvars, "corner distances": dist,
                         "eccentricities": ecc, "balls |B(a, s^j)|": balls})
            if k <= kc:
                cc = TL.count_by_elimination(tw.nvars, tw.copies)
                pred = c ** ((m ** k - 1) // (m - 1))
                okc = all(cc[t] == pred for t in R) and all(cc[t] == 0 for t in TL.cube if t not in R)
                ok3 &= okc
                g3.setdefault(g[0], []).append({"level": k, "completions per allowed tuple": sorted({cc[t] for t in R}),
                                                "predicted": pred, "zero off the knot": all(cc[t] == 0 for t in TL.cube if t not in R)})
            if k == min(kmax, 4 if m < 7 else 3):
                cover, conn, width = TL.check_tree_decomposition(tw)
                sep_ok, tested = TL.check_separators(tw)
                ok4 &= cover and conn and width == h + 2 and sep_ok and tested > 0
                g4[g[0]] = {"level": k, "copies covered": cover, "subtrees connected": conn, "width": width, "h + 2": h + 2,
                            "three-corner cuts": sep_ok, "nodes tested": tested}
        g2[g[0]] = rows
        mi, tc = info(R)
        g3.setdefault(g[0], []).append({"corner law": "uniform on the knot at every level",
                                        "mutual information of two corners (bits)": mi, "total correlation (bits)": tc})
    report("2 tower structure (copies, variables, distances, balls)", ok2, g2)
    report("3 the law at every level (variable elimination)", ok3, g3)
    report("4 finite ramification (tree decomposition, three-corner cuts)", ok4, g4)

    # 5 softening
    P = TL.P
    expect = {
        TL.TRIANGLE[0]: (P.pprod([0, 4], P.lin(1, -1), P.lin(1, 1), [-1]), P.pprod([-2], P.lin(1, -1), P.lin(1, -1), P.lin(1, -1))),
        TL.TETRA[0]: (P.pprod([0, 2], P.lin(1, -1), P.lin(1, 3), [-1]), P.pprod([2], P.lin(1, -1), P.lin(1, -1))),
        TL.FANO[0]: (P.pprod([0, 1], P.lin(1, -1), P.lin(1, 3), [10, 5, 0, 1], [-1]),
                     P.pprod([-1], P.lin(1, -1), P.lin(1, -1), P.lin(1, -1), P.lin(1, 1), [5, 1, 1, 1])),
    }
    g5, ok5 = {}, True
    for g, (m, h, s, c), kmax, kc in GADGETS:
        W = TL.soft_polys(g)
        cnt = TL.relation_counts(g)
        R = frozenset(t for t in TL.cube if cnt[t])
        A = {tuple(W[t]) for t in R}
        E = {tuple(W[t]) for t in TL.cube if t not in R}
        two = len(A) == 1 and len(E) == 1
        D, N = list(A.pop()), list(E.pop())
        up = P.padd(N, P.pneg(P.pmul(P.R, D)))
        down = P.padd(D, P.pneg(N))
        e_up, e_down = expect[g[0]]
        # positivity of the cofactors on [0, 1] (the factors other than (1 - r) are positive there): sampled exactly
        pos = all(P.peval(up, Fraction(i, 64)) > 0 and P.peval(down, Fraction(i, 64)) > 0 for i in range(1, 64))
        traj, x = [], 0.001
        for _ in range(12):
            traj.append(x)
            x = P.peval(N, x) / P.peval(D, x)
        okg = two and up == e_up and down == e_down and pos and N[0] == 0 and D[0] == c and N[1] == m * c and N[1] >= 3 * c
        ok5 &= okg
        g5[g[0]] = {"allowed weight D(r)": D, "excluded weight N(r)": N, "two-valued": two,
                    "N - r D factorization": up == e_up, "D - N factorization": down == e_down, "0 < r < r' < 1 sampled": pos,
                    "multiplier N1 / D0": str(Fraction(N[1], D[0])), "copies m": m, "trajectory from 0.001": [round(v, 4) for v in traj]}
    report("5 softening is unstable (exact maps)", ok5, g5)

    # 6 controls
    # (a) a rebuilding gadget that is not exact: x or (y != z) from four copies drifts
    drift = TL.drift_control()
    # (b) shared midpoints: the triangular grid of side 4 has no three-corner cut around a corner sub-triangle
    shared = TL.shared_midpoint_control()
    # (c) a mutated Fano gadget is not exact (one line moved)
    mut = TL.mutated_fano_control()
    report("6 controls", drift["changes"] and drift["share increases"] and shared["not cut off"] and mut["not exact"], {"drift": drift, "shared midpoints": shared,
                                                                                            "mutated Fano": mut})

    status = "Proved" if ok_all else "Failed"
    print("ALL CHECKS PASS" if ok_all else "SOME CHECKS FAIL", f"({time.time() - T0:.0f}s)")
    if write:
        json.dump({"schema_version": 1, "artifact_id": man["artifact_id"], "status": status,
                   "checks": {"ok": ok_all, **out}, "seconds": round(time.time() - T0, 1)},
                  open(os.path.join(HERE, "result.json"), "w"), indent=1, default=str)
    return ok_all


if __name__ == "__main__":
    sys.exit(0 if main("--write" in sys.argv) else 1)
