"""Machinery controls for CLASSK-DICHOTOMY-20261026-001B-E001 (run first; any failure makes the run invalid).

V1  braid knots: twisted cohomology dimensions of the diagram machinery equal cp_lib's (3_1, 4_1, 5_2, 6_1; every nontrivial
    character; (p, r) = (7, 6) and (5, 4))
V3  Borromean rings: 138 maps to S3 from the link group and 48 from its 0-surgery T^3
V7  the counting path (cohomology_data + measured_count) against cp_lib's independent Heisenberg count, per sector, on
    r-surgeries of 3_1 and 6_1 (Heisenberg groups (3, 2) at p = 7 and (2, 2) at p = 5)
V8  the counting path against independent lifting counts (cocycles to G/A, then the affine lifting system; ticket A's check,
    read-only) for two class-(K) groups that are not Heisenberg (one with a non-alternating beta), on 3_1 and 6_1 surgeries
V6  the u-pairing on single twist-knot exteriors equals the pre-registered CALIBRATION
T2  winding calibration at (p, r) = (5, 4): a copy whose band winds j times in direction -1 has functional chi^j times the
    unwound copy (j = 1, 2)
"""
import itertools
import json
import math
import sys
import time

import ck_core as PC  # noqa: E402  (puts cp_lib on the path)
import cp_lib as C  # noqa: E402
from ck_core import Comp, BraidLayout, Diagram, cohomology, projector_leaf
from ck_build import ellipse
from ck_fixtures import Spec, Base, choose_arcs, leaf_functionals, cohomology_data, measured_count, KNOTS
from ck_specs import CALIBRATION, FIELDS, L, LIBA


def perm_group(gens, deg):
    els = {tuple(range(deg))}
    fr = list(els)
    while fr:
        new = []
        for a in fr:
            for g in gens:
                b = tuple(a[g[i]] for i in range(deg))
                if b not in els:
                    els.add(b)
                    new.append(b)
        fr = new
    els = sorted(els)
    ix = {e: i for i, e in enumerate(els)}
    mul = [[ix[tuple(a[b[i]] for i in range(deg))] for b in els] for a in els]
    inv = [ix[tuple(sorted(range(deg), key=lambda i: a[i]))] for a in els]
    return mul, inv


def brute(ngen, rels, mul, inv):
    e = next(i for i in range(len(mul)) if all(mul[i][j] == j for j in range(len(mul))))
    cnt = 0
    for tup in itertools.product(range(len(mul)), repeat=ngen):
        ok = True
        for rel in rels:
            x = e
            for g, s in rel:
                y = tup[g] if s > 0 else inv[tup[g]]
                for _ in range(abs(s)):
                    x = mul[x][y]
            if x != e:
                ok = False
                break
        cnt += ok
    return cnt


def main():
    t0 = time.time()
    res = {}
    # V1
    rows = {}
    for (p, r), z in FIELDS.items():
        PC.configure(p, r, z)
        for name, (word, n) in KNOTS.items():
            Lay = BraidLayout(word, n)
            D = Diagram([Comp("K", Lay.pts, 1, r, "knot")])
            rels = D.crossing_rels + D.framing_rels()
            Uc, relc, _ = C.presentation(word, n, r)
            chars = [pow(z, e, p) for e in range(1, r)]
            mine = [len(cohomology(len(D.gens), rels, D.psi, chi)[0]) for chi in chars]
            theirs = [len(C.cohomology(Uc, relc, chi, 1, p)[0]) for chi in chars]
            rows[f"p={p} r={r} {name}"] = {"dims by character exponent 1..r-1": mine, "cp_lib": theirs, "ok": mine == theirs}
    res["V1_braid_knots"] = {"rows": rows, "ok": all(x["ok"] for x in rows.values())}
    # V3
    PC.configure(7, 6, 3)
    S3 = perm_group([(1, 0, 2), (1, 2, 0)], 3)
    comps = [Comp(f"E{k}", [ellipse(k, 2 * math.pi * s / 48) for s in range(48)], 0, 0, "b") for k in range(3)]
    D = Diagram(comps)
    link = brute(len(D.gens), D.crossing_rels, *S3)
    t3 = brute(len(D.gens), D.crossing_rels + D.framing_rels(), *S3)
    res["V3_borromean"] = {"link group S3 maps": link, "T3 S3 maps": t3, "ok": link == 138 and t3 == 48}
    # V7
    rows = {}
    for (p, r, a, b, ea, eb, kn) in [(7, 6, 3, 2, 1, 2, "3_1"), (7, 6, 3, 2, 1, 2, "6_1"), (5, 4, 2, 2, 1, 1, "6_1"),
                                     (5, 4, 2, 2, 1, 1, "3_1")]:
        z = FIELDS[(p, r)]
        spec = Spec(p, r, z, (1, 1, 1), {"x": kn, "y": kn, "t": kn})
        PC.configure(p, r, z)
        word, n = KNOTS[kn]
        Lay = BraidLayout(word, n)
        data = cohomology_data([Comp("K", Lay.pts, 1, r, "knot")], spec)
        G = L.KGroup(p, r, [ea, eb], [(ea + eb) % r], {(0, 1, 0): 1})
        Gc = C.Group(p, r, a, b)
        tot, parts = C.hom_count(Gc, word, n)
        mine = {k: measured_count(G, data, k, L.count_bilinear_zeros) for k in range(r)}
        theirs = {k: parts[k][2] for k in range(r)}
        rows[f"p={p} r={r} Heisenberg ({a}, {b}) on S^3_{r}({kn})"] = {"measured path": mine, "cp_lib": theirs,
                                                                        "ok": mine == theirs}
    res["V7_counting_path"] = {"rows": rows, "ok": all(x["ok"] for x in rows.values())}
    # V8
    sys.path.insert(0, str(LIBA))
    import check as CA  # ticket A's check (read-only): count_direct, z1_b1_h1
    rows = {}
    cases = [(5, 4, [1, 1, 2], [2, 3, 3, 0], {(0, 1, 0): 1, (0, 2, 1): 2, (1, 2, 2): 3, (2, 2, 3): 1, (1, 0, 0): 3}, "3_1"),
             (5, 4, [1, 1, 2], [2, 3, 3, 0], {(0, 1, 0): 1, (0, 2, 1): 2, (1, 2, 2): 3, (2, 2, 3): 1, (1, 0, 0): 3}, "6_1"),
             (7, 6, [1, 2, 3, 3], [3, 4, 5, 0], {(0, 1, 0): 1, (0, 2, 1): 2, (1, 3, 2): 1, (2, 3, 3): 3}, "6_1")]
    for (p, r, bexp, aexp, beta, kn) in cases:
        z = FIELDS[(p, r)]
        G = L.KGroup(p, r, bexp, aexp, beta)
        spec = Spec(p, r, z, (1, 1, 1), {"x": kn, "y": kn, "t": kn})
        PC.configure(p, r, z)
        word, n = KNOTS[kn]
        Lay = BraidLayout(word, n)
        data = cohomology_data([Comp("K", Lay.pts, 1, r, "knot")], spec)
        U, rels, _ = C.presentation(word, n, r)
        mine, theirs = {}, {}
        for k in range(r):
            fac = 1
            for j in range(G.dA):
                Zj, _, _ = CA.z1_b1_h1(U, rels, pow(G.amul[j], k, p), p)
                fac *= p ** len(Zj)
            fac *= p ** sum(1 for i in range(G.dB) if pow(G.bmul[i], k, p) != 1)
            mine[k] = fac * measured_count(G, data, k, L.count_bilinear_zeros)
            theirs[k] = CA.count_direct(G, U, rels, k)
        rows[f"p={p} r={r} B={bexp} on S^3_{r}({kn})"] = {"measured path x |Z1(A)| |B1(B)|": mine, "direct lifting": theirs,
                                                          "ok": mine == theirs}
    res["V8_counting_path_vs_lifting"] = {"rows": rows, "ok": all(x["ok"] for x in rows.values())}
    # V6
    rows = {}
    for (p, kn, e), want in CALIBRATION.items():
        r = 6 if p == 7 else 4
        z = FIELDS[(p, r)]
        PC.configure(p, r, z)
        word, n = KNOTS[kn]
        Lay = BraidLayout(word, n)
        D = Diagram([Comp("K", Lay.pts, 1, None, "knot")])
        rels = D.crossing_rels
        U = len(D.gens)
        Hu = cohomology(U, rels, D.psi, 1)[0]
        Ht = cohomology(U, rels, D.psi, pow(z, e, p))[0]
        Bm = PC.obstruction_bimap(U, rels, D.psi, 1, pow(z, e, p), Hu, Ht)
        got = any(any(v) for v in Bm.values())
        rows[f"p={p} {kn} tau = Z^{e}"] = {"dim H1(X; F_p)": len(Hu), "dim V_tau": len(Ht), "u u v nonzero": got,
                                           "pre-registered": want, "ok": got == want and len(Hu) == 1 and len(Ht) == 1}
    res["V6_u_pairing_calibration"] = {"rows": rows, "ok": all(x["ok"] for x in rows.values())}
    # T2 at (5, 4)
    p, r, z = 5, 4, 2
    spec = Spec(p, r, z, (1, 1, 2), {"x": "6_1", "y": "6_1", "t": "4_1"})
    spec.configure()
    base = Base(spec, ["x", "x", "y", "t"], {0: 3, 1: 1, 2: 1, 3: 1})       # a gap tall enough for the four test copies
    base.gap_choice = choose_arcs(base)
    Lay = base.layout()
    k, q = base.gap_choice[0]
    lo, hi = Lay.gap(k)
    leaves = []
    for idx, (j, d) in enumerate([(0, -1), (1, -1), (2, -1), (1, 1)]):
        m = [0] * r
        m[j] = 1
        pts, _, _ = projector_leaf(float(q), hi - 1.0 - 4.0 * idx, m, d)
        leaves.append(Comp(f"j{j}d{d}", pts, 0, 0, "leaf"))
    chi_s, chi_inv = pow(z, 1, p), pow(z, 3, p)
    F, _ = leaf_functionals(Comp("K", Lay.pts, 1, r, "knot"), leaves, chis=(chi_s, chi_inv))
    rows, ok = {}, True
    for chi in (chi_s, chi_inv):
        f0 = F[chi]["j0d-1"]
        for nm, e in (("j1d-1", 1), ("j2d-1", 2), ("j1d1", -1)):
            good = all((pow(chi, e % r, p) * a - b) % p == 0 for a, b in zip(f0, F[chi][nm]))
            rows[f"chi {chi}, {nm}: chi^{e} x unwound"] = good
            ok &= good and any(f0)
    res["T2_winding_calibration_p5"] = {"rows": rows, "ok": ok}
    res["ok"] = all(v["ok"] for v in res.values() if isinstance(v, dict))
    res["seconds"] = round(time.time() - t0, 1)
    return res


if __name__ == "__main__":
    out = main()
    print(json.dumps(out, indent=1, default=str))
    sys.exit(0 if out["ok"] else 1)
