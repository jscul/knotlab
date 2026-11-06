"""Machinery controls for the pattern-1 checkpoint (run before the fixtures; any failure invalidates the run).

V1  braid knots: twisted cohomology dimensions equal those of cp_lib's presentation (3_1, 4_1, 5_2, 6_1; five characters)
V1b big braid knots with cabled Borromean insertions (lane A's pattern-1 knots): N_free3 = 938791 and 49735
V2  chirality and framing: +1 and -1 surgery on cp_lib's trefoil sigma_1^3 give the same number of A5 maps as cp_lib (121, 1)
V3  Borromean rings: 138 maps to S3 from the link group and 48 from its 0-surgery T^3
V4  a Y-graph realized as its six-component link reproduces the cabled-Borromean braid insertion: N_free3 = 938791, H = 18865
T2  winding calibration: a copy whose band winds j times in direction -1 has functional chi^j times the unwound copy (j = 1, 2)
"""
import itertools
import json
import math
import sys
import time

import pc_core as PC  # noqa: E402  (puts cp_lib on the path)
import cp_lib as C  # noqa: E402
from pc_core import Comp, BraidLayout, Diagram, cohomology, obstruction_bimap, counts_from_bimaps, P, R
from pc_build import ellipse, y_graph, leaf_bundle
from pc_core import projector_leaf
from pc_fixtures import Base, choose_arcs, leaf_functionals


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


def free3(comps):
    D = Diagram(comps)
    rels = D.crossing_rels + D.framing_rels()
    U = len(D.gens)
    H = {chi: cohomology(U, rels, D.psi, chi)[0] for chi in (3, 2, 6)}
    B12 = obstruction_bimap(U, rels, D.psi, 3, 2, H[3], H[2])
    B13 = obstruction_bimap(U, rels, D.psi, 3, 6, H[3], H[6])
    B23 = obstruction_bimap(U, rels, D.psi, 2, 6, H[2], H[6])
    return counts_from_bimaps(B12, B13, B23, len(H[3]), len(H[2]), len(H[6]))


def main():
    t0 = time.time()
    res = {}
    rows = {}
    for name, (word, n) in {"3_1": PC.T31, "4_1": ([1, -2, 1, -2], 3), "5_2": PC.K52, "6_1": PC.S61}.items():
        L = BraidLayout(word, n)
        D = Diagram([Comp("K", L.pts, 1, 6, "knot")])
        rels = D.crossing_rels + D.framing_rels()
        Uc, relc, _ = C.presentation(word, n, 6)
        mine = [len(cohomology(len(D.gens), rels, D.psi, chi)[0]) for chi in (3, 2, 6, 4, 5)]
        theirs = [len(C.cohomology(Uc, relc, chi, 1, P)[0]) for chi in (3, 2, 6, 4, 5)]
        rows[name] = {"dims (chi = 3, 2, 6, 4, 5)": mine, "cp_lib": theirs, "ok": mine == theirs}
    res["V1_braid_knots"] = {"rows": rows, "ok": all(r["ok"] for r in rows.values())}
    word0, n = C.connected_sum([PC.T31, PC.S61, PC.K52] * 3)
    rows = {}
    for ins, expect in (([(1, 1)], 938791), ([(1, 1), (18, 1)], 49735)):
        w, _ = C.insert_at(word0, ins, R)
        L = BraidLayout(w, n)
        cnt = free3([Comp("K", L.pts, 1, 6, "knot")])
        rows[str(ins)] = {"N_free3": cnt["free3"], "expected": expect, "ok": cnt["free3"] == expect}
    res["V1b_insertion_knots"] = {"rows": rows, "ok": all(r["ok"] for r in rows.values())}
    A5 = perm_group([(1, 2, 0, 3, 4), (0, 1, 3, 4, 2)], 5)
    rows = {}
    for f in (1, -1):
        L = BraidLayout(*PC.T31)
        D = Diagram([Comp("K", L.pts, 1, f, "knot")])
        mine = brute(len(D.gens), D.crossing_rels + D.framing_rels(), *A5)
        Uc, relc, _ = C.presentation(*PC.T31, f)
        theirs = brute(Uc, relc, *A5)
        rows[f"framing {f}"] = {"A5 maps": mine, "cp_lib": theirs, "ok": mine == theirs}
    res["V2_chirality"] = {"rows": rows, "ok": all(r["ok"] for r in rows.values()) and rows["framing 1"]["A5 maps"] == 121}
    S3 = perm_group([(1, 0, 2), (1, 2, 0)], 3)
    comps = [Comp(f"E{k}", [ellipse(k, 2 * math.pi * s / 48) for s in range(48)], 0, 0, "b") for k in range(3)]
    D = Diagram(comps)
    link = brute(len(D.gens), D.crossing_rels, *S3)
    t3 = brute(len(D.gens), D.crossing_rels + D.framing_rels(), *S3)
    res["V3_borromean"] = {"link group S3 maps": link, "T3 S3 maps": t3, "ok": link == 138 and t3 == 48}
    L = BraidLayout(word0, n, gaps={0: 6.0})
    lo, hi = L.gap(0)
    leaves, roots = [], []
    for k, (a, b) in enumerate(((1, 6), (7, 12), (13, 18))):
        lf, root = leaf_bundle(f"A{k}", float(a), float(b), lo + 1.5 + 0.8 * k)
        leaves.append(lf)
        roots.append(root)
    cnt = free3([Comp("K", L.pts, 1, 6, "knot")] + leaves + y_graph(0, (-12.0, lo + 2.0, 20.0), roots, 24.0))
    res["V4_y_graph_link"] = {"counts": cnt, "ok": cnt == {"free3": 938791, "H12": 18865, "H13": 18865, "H23": 18865}}
    base = Base(["x", "x", "y", "t"], {0: 1, 1: 1, 2: 1, 3: 1})
    base.gap_choice = choose_arcs(base)
    L = base.layout()
    k, q = base.gap_choice[0]
    lo, hi = L.gap(k)
    leaves = []
    for idx, (j, d) in enumerate([(0, -1), (1, -1), (2, -1), (1, 1)]):
        m = [0] * 6
        m[j] = 1
        pts, _, _ = projector_leaf(float(q), hi - 1.0 - 4.0 * idx, m, d)
        leaves.append(Comp(f"j{j}d{d}", pts, 0, 0, "leaf"))
    F, _ = leaf_functionals(Comp("K", L.pts, 1, 6, "knot"), leaves, chis=(3, 5))
    rows = {}
    ok = True
    for chi in (3, 5):
        f0 = F[chi]["j0d-1"]
        for nm, e in (("j1d-1", 1), ("j2d-1", 2), ("j1d1", -1)):
            good = all((pow(chi, e % R, P) * a - b) % P == 0 for a, b in zip(f0, F[chi][nm]))
            rows[f"chi {chi}, {nm}: chi^{e} x unwound"] = good
            ok &= good and any(f0)
    res["T2_winding_calibration"] = {"rows": rows, "ok": ok}
    res["ok"] = all(v["ok"] for v in res.values() if isinstance(v, dict))
    res["seconds"] = round(time.time() - t0, 1)
    return res


if __name__ == "__main__":
    r = main()
    print(json.dumps(r, indent=1))
    sys.exit(0 if r["ok"] else 1)
