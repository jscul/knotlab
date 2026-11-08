#!/usr/bin/env python3
"""Run for TWO-BIT-20261108-001A-E001: products of two one-bit decorations of the pinwheel against the crystals in hand.

    /home/jscul/p-vs-np-contact-first/.venv/bin/python -B run.py [--limit N]
Writes artifacts/TWO-BIT-20261108-001A/TWO-BIT-20261108-001A-E001_products_against_crystals/run/{table.json, rows.jsonl, result.json}.

A product s1 x s2 labels a tile with a pair of bits (label 2a + b) and gives child m the label 2 s1(a)_m + s2(b)_m. Its law is the
labelled closure of ROUND-PRICE-20261108-001A's decor_lib with four labels.
  1. The crystals: the 11 domino-torus planes legal within two cuts (ONE-BIT-20261108-001B), at their first legal cut j and j + 1,
     and the 26 mixed-orientation crystals of CRYSTAL-UP-20261108-001A (its certificate crystal.json) at one and two cuts; tori of
     index 1 or 2 over each plane's lattice. A test is (plane, cuts, torus).
  2. One bit: for each of the 1,024 one-bit decorations, the tests its law admits (decor_lib.periodic; on each plane and torus the
     levels are tried in order, and admission at one level gives the next, by ROUND-PRICE-20261108-001A's Lemma 2).
  3. Products, up to exchanging the factors and relabelling either (s~(b) = 1 - s(1 - b)): the tests both factors admit, cheapest
     first, each a periodic two-bit labelling obeying the product's law (a SAT model with two variables per tile); the first
     admitted test is the product's escape. A product's escape projects to an escape of each factor, so no other test can admit it.
     A product with no escape is a survivor.
Controls: every one-bit decoration admits some test (the one-bit census, every decoration escaping); the product of the constant
decoration 00000 / 11111 with any one-bit decoration escapes; the rhombus lattice's four tests are in the list."""
from __future__ import annotations

import glob
import importlib.util
import itertools
import json
import multiprocessing as mp
import sys
import time
from fractions import Fraction as Fr
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUT = ROOT / "artifacts/TWO-BIT-20261108-001A/TWO-BIT-20261108-001A-E001_products_against_crystals/run"


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


OB = _load("one_bit_b_run", glob.glob(str(ROOT / "experiments/ONE-BIT-20261108-001B/*/run.py"))[0])
D, AB = OB.D, OB.AB
CONST = ((0, 0, 0, 0, 0), (1, 1, 1, 1, 1))
W = {}


def relabel(s):
    return tuple(tuple(1 - x for x in s[1 - b]) for b in (0, 1))


def product(s1, s2):
    return tuple(tuple(2 * s1[a][m] + s2[b][m] for m in range(5)) for a in (0, 1) for b in (0, 1))


def canonical(s1, s2):
    best = None
    for x, y in ((s1, s2), (s2, s1)):
        for xx in (x, relabel(x)):
            for yy in (y, relabel(y)):
                best = (xx, yy) if best is None or (xx, yy) < best else best
    return best


def all_one_bit():
    return [(tuple(a), tuple(b)) for a in itertools.product((0, 1), repeat=5) for b in itertools.product((0, 1), repeat=5)]


def build_planes(sk):
    """[(name, Plane, levels)]"""
    rows = [json.loads(x) for x in Path(glob.glob(str(ROOT / "artifacts/ONE-BIT-20261108-001B/*/run/rows.jsonl"))[0]).read_text().splitlines()]
    seen, out = {}, []
    for r in rows:
        key = json.dumps(r["plane"])
        if key in seen:
            continue
        seen[key] = 1
        m, n, doms, diags = r["plane"]
        cell = []
        for (kind, i, jj), d in zip(doms, diags):
            cell += AB.rect_h(i, jj, d) if kind == "h" else AB.rect_v(i, jj, d)
        j = r["first legal cut"]
        out.append(("domino " + key, D.Plane(sk, cell, ((m, 0), (0, n))), (j, j + 1)))
    crys = json.loads(Path(glob.glob(str(ROOT / "proofs/CRYSTAL-UP-20261108-001B/*/crystal.json"))[0]).read_text())["crystals"]
    for c in crys:
        cell = [tuple((Fr(x), Fr(y)) for x, y in t[:3]) for t in c["tiles"]]
        lat = tuple(tuple(Fr(x) for x in v) for v in c["lattice"])
        out.append((f"mixed seed {c['seed'][0]} {c['tiles per period']} tiles", D.Plane(sk, cell, lat, radius=6), (1, 2)))
    return out


def tests_of(planes):
    tori = [L for m in (1, 2) for L in D.sublattices(m)]
    out = []
    for pi, (name, P, levels) in enumerate(planes):
        for k in levels:
            for L in tori:
                cost = len(P.cell) * 5 ** k * L[0] * L[2]
                out.append((cost, pi, k, L))
    out.sort()
    return [(pi, k, L) for _, pi, k, L in out]


def periodic4(plane, allowed, k, L):
    """a periodic labelling with four labels (two variables per position) obeying allowed, on the sublattice L"""
    from pysat.solvers import Cadical153
    a, c, d = L
    cells = [(s, i, j) for s in range(len(plane.cell)) for i in range(a) for j in range(d)]
    cons = D.constraints(plane, allowed, k, cells)
    var = {}
    S = Cadical153()
    rows = []
    for lits, al in cons:
        if not al:
            S.delete()
            return False
        keys = [(x[0],) + D.reduce(x[1], x[2], L) + (x[3],) for x in lits]
        rows.append(([(var.setdefault((kk, 0), len(var) + 1), var.setdefault((kk, 1), len(var) + 1)) for kk in keys], al))
    top = len(var)
    for vs, al in rows:
        ys = []
        for tup in al:
            top += 1
            ys.append(top)
            for (v0, v1), lab in zip(vs, tup):
                S.add_clause([-top, v0 if lab >> 1 else -v0])
                S.add_clause([-top, v1 if lab & 1 else -v1])
        S.add_clause(ys)
    ok = S.solve()
    S.delete()
    return ok


def warm(sk, planes):
    for _, P, levels in planes:
        for k in range(max(levels) + 1):
            for sp in P.descendants(k):
                P.tile(*sp)


def one_bit_job(s):
    """the tests s admits; a labelling admitted at k cut once more is admitted at k + 1 on the same torus (ROUND-PRICE-20261108-001A,
    Lemma 2), so on each plane and torus the levels are tried in order and the larger ones follow"""
    law = D.law(W["sk"], s)
    ok = set()
    by = {}
    for t, (pi, k, L) in enumerate(W["tests"]):
        by.setdefault((pi, L), []).append((k, t))
    for (pi, L), ks in by.items():
        ks.sort()
        for n, (k, t) in enumerate(ks):
            if D.periodic(W["planes"][pi][1], law, k, L):
                ok.update(tt for _, tt in ks[n:])
                break
    return s, sorted(ok)


def product_job(pair):
    s1, s2 = pair
    cand = sorted(set(W["A"][s1]) & set(W["A"][s2]))
    if not cand:
        return pair, None, 0
    law = D.law(W["sk"], product(s1, s2))
    for n, t in enumerate(cand):
        pi, k, L = W["tests"][t]
        if periodic4(W["planes"][pi][1], law, k, L):
            return pair, t, n + 1
    return pair, None, len(cand)


def main():
    t0 = time.time()
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    OUT.mkdir(parents=True, exist_ok=True)
    sk = D.Skeleton()
    planes = build_planes(sk)
    warm(sk, planes)
    W.update(sk=sk, planes=planes, tests=tests_of(planes))
    res = {"experiment": "TWO-BIT-20261108-001A-E001", "planes": [p[0] for p in planes], "tests": len(W["tests"]), "controls": {}}
    decs = all_one_bit()
    with mp.Pool(12) as pool:
        A = dict(pool.map(one_bit_job, decs, chunksize=8))
    W["A"] = A
    (OUT / "table.json").write_text(json.dumps({"tests": [[planes[pi][0], k, list(L)] for pi, k, L in W["tests"]],
                                                "admitted": {"".join(map(str, s[0])) + "/" + "".join(map(str, s[1])): A[s] for s in decs}}) + "\n")
    res["one-bit decorations admitting some test"] = sum(1 for s in decs if A[s])
    res["controls"]["every one-bit decoration admits some listed test"] = res["one-bit decorations admitting some test"] == 1024
    print("one-bit table", res["one-bit decorations admitting some test"], round(time.time() - t0, 1), flush=True)
    classes = sorted({canonical(s1, s2) for s1 in decs for s2 in decs})
    res["product classes"] = len(classes)
    if limit:
        classes = classes[:limit]
    esc = {}
    with open(OUT / "rows.jsonl", "w") as fh, mp.Pool(12) as pool:
        for n, (pair, t, tried) in enumerate(pool.imap_unordered(product_job, classes, chunksize=16)):
            esc[pair] = t
            fh.write(json.dumps({"product": ["".join(map(str, x[0])) + "/" + "".join(map(str, x[1])) for x in pair],
                                 "escape": None if t is None else [planes[W["tests"][t][0]][0], W["tests"][t][1], list(W["tests"][t][2])],
                                 "tests tried": tried}) + "\n")
            if n % 5000 == 0:
                fh.flush()
                print(n, len(classes), "survivors so far", sum(1 for v in esc.values() if v is None), round(time.time() - t0, 1), flush=True)
    surv = [p for p, t in esc.items() if t is None]
    res["product classes tested"] = len(esc)
    res["escaping"] = len(esc) - len(surv)
    res["survivors"] = [["".join(map(str, x[0])) + "/" + "".join(map(str, x[1])) for x in p] for p in surv]
    by = {}
    for t in esc.values():
        if t is not None:
            name = planes[W["tests"][t][0]][0].split(" [")[0].split(" seed")[0]
            by[name] = by.get(name, 0) + 1
    res["first escape by crystal family"] = by
    const_ok = all(esc.get(canonical(CONST, s)) is not None for s in decs if canonical(CONST, s) in esc)
    res["controls"]["every product with the constant decoration escapes"] = const_ok
    res["controls"]["the rhombus lattice's tests are listed"] = any("[2, 4, [[\"v\", 0, 0]" in planes[pi][0] for pi, _, _ in W["tests"])
    res["status"] = "passed" if all(res["controls"].values()) else "failed"
    res["seconds"] = round(time.time() - t0, 1)
    (OUT / "result.json").write_text(json.dumps(res, indent=1) + "\n")
    print(json.dumps({k: v for k, v in res.items() if k != "survivors"}, indent=1), "survivors:", len(surv))
    return 0 if res["status"] == "passed" else 1


if __name__ == "__main__":
    sys.exit(main())
