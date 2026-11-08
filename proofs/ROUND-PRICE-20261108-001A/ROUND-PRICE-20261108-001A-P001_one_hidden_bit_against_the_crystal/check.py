#!/usr/bin/env python3
"""Check for ROUND-PRICE-20261108-001A-P001: one hidden bit per tile against the rhombus crystal.

    /home/jscul/p-vs-np-contact-first/.venv/bin/python -B check.py      (writes result.json and census.json)

Uses decor_lib.py beside it (PINWHEEL-ATLAS-20261107-001A's atlas_lib for the cut and collars; PySAT's CaDiCaL for the labellings).
- The 1,024 decorated substitutions on two labels; for each, its labelled collar law.
- The crystal R_k, the k-fold cut of the rhombus lattice (COLLAR-PLANE-20261108-001A), for k = 1, 2, 3: admitted when some periodic
  labelling (a torus of index 1, 2 or 4 over the rhombus lattice) obeys the law, excluded when a finite box (cells |i|, |j| <= 1, every
  descendant's collar inside |i|, |j| <= 2) has no obeying labelling, otherwise undecided. Admitted at k implies admitted at every
  larger k, so the search for a decoration stops at its first admitted k.
- Survivors (excluded at k = 1, 2 and 3): the rhombus crystal at k = 4, and the brick crystal (brick rows of 1 x 2 rectangles with
  alternating diagonals, collar-legal after two cuts, COLLAR-PLANE-20261108-001C) at k = 2, 3 and 4.
- Controls: every periodic labelling found is checked tile by tile; relabelling 0 <-> 1 gives the same verdict; the two constant
  decorations admit R_1; an empty law is unsatisfiable and a law allowing everything is satisfiable on a box; for three decorations
  the labelled law contains every labelled collar of a genuine labelled level-4 pinwheel patch, computed from coordinates."""
from __future__ import annotations

import itertools
import json
import multiprocessing as mp
import sys
import time
from collections import Counter
from fractions import Fraction as Fr
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import decor_lib as D  # noqa: E402

A = D.A
SIGS = [s for s in itertools.product(itertools.product((0, 1), repeat=5), repeat=2)]
TORI = [L for m in (1, 2, 4) for L in D.sublattices(m)]
G = {}


def brick_plane(sk):
    """brick rows of 1 x 2 rectangles, diagonals alternating along each row (PINWHEEL-ATLAS-20261107-001B's rows_plane([[1], [0]],
    brick)), as a cell and a lattice found by search"""
    def rect_h(x, y, d):
        a, b, c, e = (x, y), (x + 2, y), (x + 2, y + 1), (x, y + 1)
        return [(a, b, e), (c, e, b)] if d == 0 else [(b, a, c), (e, c, a)]
    pat = [[1], [0]]
    tiles = []
    for j in range(-8, 9):
        for i in range(-8, 9):
            tiles += rect_h(2 * i + (1 if j % 2 else 0), j, pat[i % 2][j % 1])
    tset = set(tiles)
    near = [t for t in tiles if all(abs(p[0]) <= 6 and abs(p[1]) <= 3 for p in t)]
    vecs = [(a, b) for a in range(-8, 9) for b in range(0, 5) if (a, b) != (0, 0) and (b > 0 or a > 0)
            and all(tuple((p[0] + a, p[1] + b) for p in t) in tset for t in near)]
    v1 = min((v for v in vecs if v[1] == 0), key=lambda v: abs(v[0]))
    v2 = min((v for v in vecs if v[1] > 0), key=lambda v: (v[1], abs(v[0])))
    det = v1[0] * v2[1] - v1[1] * v2[0]

    def coords(t):
        cx = Fr(sum(p[0] for p in t), 3)
        cy = Fr(sum(p[1] for p in t), 3)
        return ((cx * v2[1] - cy * v2[0]) / det, (cy * v1[0] - cx * v1[1]) / det)
    cell = [t for t in tiles if 0 <= coords(t)[0] < 1 and 0 <= coords(t)[1] < 1]
    return D.Plane(sk, cell, (v1, v2)), (v1, v2), len(cell)


def setup():
    t0 = time.time()
    sk = D.Skeleton()
    rh = D.Plane(sk, D.RHOMBUS, D.RHOMBUS_LATTICE)
    br, blat, bcell = brick_plane(sk)
    for P, K in ((rh, 4), (br, 4)):
        for k in range(K + 1):
            for s, p in P.descendants(k):
                P.tile(s, p)
    G.update(sk=sk, rh=rh, br=br, blat=blat, bcell=bcell, setup_seconds=round(time.time() - t0, 1))


def verify_model(plane, allowed, k, L, model):
    a, c, d = L
    for s in range(len(plane.cell)):
        for i in range(a):
            for j in range(d):
                for (s1, path) in plane.descendants(k):
                    if s1 != s:
                        continue
                    n, coll = plane.tile(s, path)
                    tup = tuple(int(model[(s2,) + D.reduce(i + di, j + dj, L) + (p,)]) for s2, di, dj, p in coll)
                    if tup not in set(allowed.get(n, [])):
                        return False
    return True


def crystal(plane, allowed, ks, B=2):
    """verdicts per k: ('admitted', torus) at the first admitted k, ('excluded',) or ('undecided',) before it"""
    out = []
    for k in ks:
        hit = None
        for L in TORI:
            ok, model = D.periodic(plane, allowed, k, L, want_model=True)
            if ok:
                hit = (L, verify_model(plane, allowed, k, L, model))
                break
        if hit:
            out.append({"k": k, "verdict": "admitted", "torus": list(hit[0]), "labelling verified": hit[1]})
            break
        out.append({"k": k, "verdict": "undecided" if D.boxed(plane, allowed, k, B) else "excluded"})
    return out


def job(sig):
    allowed = D.law(G["sk"], sig)
    res = {"sig": [list(sig[0]), list(sig[1])], "labelled keys": sum(len(v) for v in allowed.values()),
           "rhombus": crystal(G["rh"], allowed, (1, 2, 3))}
    if all(r["verdict"] == "excluded" for r in res["rhombus"]):
        res["rhombus k=4"] = crystal(G["rh"], allowed, (4,))
        res["brick"] = crystal(G["br"], allowed, (2, 3, 4))
    return res


def swap(sig):
    return (tuple(1 - x for x in sig[1]), tuple(1 - x for x in sig[0]))


def pattern(r):
    return " ".join(f"k{x['k']}:{x['verdict']}" for x in r["rhombus"])


def genuine_check(sig, allowed):
    """label T_4 top-down from label 0 and handedness of its own seed, compute every interior tile's labelled collar from
    coordinates, and look it up in the law"""
    sk = G["sk"]
    tiles = [(((Fr(0), Fr(0)), (Fr(0), Fr(1)), (Fr(1), Fr(0))), 0)]
    for _ in range(4):
        tiles = [(c, sig[l][m]) for t, l in tiles for m, c in enumerate(A.cut(t))]
    lab = dict(tiles)
    ts = list(lab)
    bad = tested = 0
    for t in ts:
        col = [u for u in ts if u == t or A.touch(t, u)]
        framed = {tuple(A.to_frame(t, p) for p in u): u for u in col}
        typ = (A.orient(t), tuple(D.canon(list(framed))))
        n = sk.index.get(typ)
        if n is None or n >= sk.n_keys or not sk.complete[n]:
            continue
        tested += 1
        if tuple(lab[framed[x]] for x in typ[1]) not in set(allowed.get(n, [])):
            bad += 1
    return tested, bad


def main():
    t0 = time.time()
    setup()
    res = {"checks": {}, "controls": {}, "census": {"setup seconds": G["setup_seconds"]}}
    sk = G["sk"]
    res["census"]["collar keys (both seeds), complete"] = [sk.n_keys, sum(sk.complete[:sk.n_keys])]
    res["census"]["rhombus cell tiles, collar types"] = [len(G["rh"].cell), len({n for n, _ in G["rh"].root})]
    res["census"]["brick lattice, cell tiles"] = [G["blat"], G["bcell"]]
    with mp.Pool(16) as pool:
        rows = pool.map(job, SIGS, chunksize=4)
    by = {tuple(map(tuple, r["sig"])): r for r in rows}
    pats = Counter(pattern(r) for r in rows)
    res["census"]["rhombus verdict patterns (k = 1, 2, 3)"] = dict(sorted(pats.items()))
    surv = [r for r in rows if all(x["verdict"] == "excluded" for x in r["rhombus"])]
    res["census"]["survivors (excluded at k = 1, 2, 3)"] = [
        {"sig": r["sig"], "rhombus k=4": r["rhombus k=4"], "brick": r["brick"]} for r in surv]
    res["checks"]["every periodic labelling found obeys the law tile by tile"] = all(
        x.get("labelling verified", True) for r in rows for x in r["rhombus"] + r.get("rhombus k=4", []) + r.get("brick", []))
    res["checks"]["every decoration has a verdict at k = 1"] = all(r["rhombus"] for r in rows)
    res["controls"]["relabelling 0 and 1 gives the same verdicts"] = all(pattern(by[s]) == pattern(by[swap(s)]) for s in by)
    const = [((0,) * 5, (1,) * 5), ((1,) * 5, (0,) * 5)]
    res["controls"]["the constant decorations admit R_1"] = all(by[s]["rhombus"][0]["verdict"] == "admitted" and by[s]["rhombus"][0]["k"] == 1
                                                              for s in const)
    P = G["rh"]
    res["controls"]["an empty law is unsatisfiable on a box"] = not D.boxed(P, {}, 1, 2)
    full = {n: [tup for tup in itertools.product((0, 1), repeat=len(sk.types[n][1]))] for n in {P.tile(s, p)[0] for s, p in P.descendants(1)}}
    res["controls"]["a law allowing every labelling is satisfiable on a box"] = D.boxed(P, full, 1, 2)
    gen = {}
    for sig in (((0, 1, 1, 1, 0), (1, 1, 1, 0, 1)), ((0, 1, 0, 1, 0), (1, 0, 1, 0, 1)), ((1, 0, 0, 0, 0), (0, 1, 1, 1, 1))):
        tested, bad = genuine_check(sig, D.law(sk, sig))
        gen[str(sig)] = [tested, bad]
    res["census"]["genuine labelled T_4: interior collars tested, outside the law"] = gen
    res["controls"]["genuine labelled pinwheel collars lie in the law"] = all(t > 0 and b == 0 for t, b in gen.values())
    (HERE / "census.json").write_text(json.dumps(rows, indent=0) + "\n")
    res["status"] = "passed" if all(res["checks"].values()) and all(res["controls"].values()) else "failed"
    res["failures"] = [k for k, v in {**res["checks"], **res["controls"]}.items() if not v]
    res["runtime_seconds"] = round(time.time() - t0, 1)
    (HERE / "result.json").write_text(json.dumps(res, indent=1, default=str) + "\n")
    print(json.dumps(res, indent=1, default=str))
    return 0 if res["status"] == "passed" else 1


if __name__ == "__main__":
    sys.exit(main())
