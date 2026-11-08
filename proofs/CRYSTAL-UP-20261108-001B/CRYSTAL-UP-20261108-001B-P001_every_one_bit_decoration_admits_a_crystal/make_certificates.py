#!/usr/bin/env python3
"""How the certificates of CRYSTAL-UP-20261108-001B-P001 were made (provenance only; check.py does not run this).

    /home/jscul/p-vs-np-contact-first/.venv/bin/python -B make_certificates.py

- crystal.json: every completed torus of CRYSTAL-UP-20261108-001A-E002 (its rows.jsonl), smallest first, each one period of a
  labelled parent tiling, moved from its seed tile's affine frame to Euclidean coordinates, (x, y) -> (x, 2y).
- escapes.json: for each of the eight decorations ROUND-PRICE-20261108-001B left open (one per class) that ONE-BIT-20261108-001B
  saw escape, its first recorded escape (a domino-torus plane, a number of cuts and a sublattice), rebuilt with that run's code and labelled by ROUND-PRICE-20261108-001A's decor_lib.periodic
  (with its model): the k-fold cut of the plane over one period of the sublattice, each tile with its label.
Both are only inputs to the independent check, which accepts or rejects them on its own."""
import glob
import importlib.util
import itertools
import json
import sys
from fractions import Fraction as Fr
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    sys.modules[name] = m
    spec.loader.exec_module(m)
    return m


def crystal():
    rows = [json.loads(x) for x in (ROOT / "artifacts/CRYSTAL-UP-20261108-001A/CRYSTAL-UP-20261108-001A-E002_compatible_periods/run/"
                                         "rows.jsonl").read_text().splitlines()]
    e = lambda p: (Fr(p[0]), 2 * Fr(p[1]))
    out = []
    for r in rows:
        for t in r["tori"]:
            out.append({"seed": r["seed"], "tiles per period": t["tiles per period"],
                        "tiles": [[[str(x) for x in e(p)] for p in tile] + [lab] for tile, lab in t["cell"]],
                        "lattice": [[str(x) for x in e(v)] for v in t["lattice"]]})
    out.sort(key=lambda c: (c["tiles per period"], c["seed"][0], json.dumps(c["seed"][1])))
    (HERE / "crystal.json").write_text(json.dumps({
        "about": "Every completed torus of CRYSTAL-UP-20261108-001A-E002, smallest first: one period of a labelled parent tiling, each "
                 "tile (O, P, Q) (right angle, end of the long leg, end of the short leg) in Euclidean coordinates (legs 1 and 2) "
                 "with its label, the lattice basis, and the seed collar it grew from.", "crystals": out}, indent=1))


def escapes():
    OB = load("one_bit_b_run", glob.glob(str(ROOT / "experiments/ONE-BIT-20261108-001B/*/run.py"))[0])
    D, A = OB.D, OB.A
    res = json.loads(Path(glob.glob(str(ROOT / "artifacts/ONE-BIT-20261108-001B/*/run/result.json"))[0]).read_text())
    sk = D.Skeleton()
    rp = json.loads((ROOT / "proofs/ROUND-PRICE-20261108-001B/ROUND-PRICE-20261108-001B-P001_labelled_composition_for_the_survivors/"
                            "result.json").read_text())
    open_sigs = [r["sig"] for r in rp["census"]["survivors"] if r["period-4 brick crystals: first admitted (plane, k, torus)"] is None]
    out = []
    for sig in open_sigs:
        escs = res["escapes by decoration"].get(json.dumps(sig), [])
        if not escs:
            continue
        sig = tuple(tuple(x) for x in sig)
        (m, n, doms, diags), (k, L) = escs[0]
        doms = [tuple(d) for d in doms]
        cell, _ = OB.collars(doms, diags, m, n)
        plane = D.Plane(sk, cell, ((m, 0), (0, n)))
        ok, model = D.periodic(plane, D.law(sk, sig), k, tuple(L), want_model=True)
        assert ok, (sig, esc)
        a, c, d = L
        tiles = []
        for s, t in enumerate(plane.cell):
            for i in range(a):
                for j in range(d):
                    base = tuple((p[0] + i * m, p[1] + j * n) for p in t)
                    for path in itertools.product(range(5), repeat=k):
                        u = base
                        for step in path:
                            u = A.cut(u)[step]
                        tiles.append([[str(x) for x in p] for p in u] + [int(model[(s, i, j, path)])])
        out.append({"decoration": [list(sig[0]), list(sig[1])], "plane": [m, n, [list(x) for x in doms], list(diags)], "cuts": k,
                    "sublattice": list(L), "tiles": tiles, "lattice": [[str(a * m), "0"], [str(c * m), str(d * n)]]})
    (HERE / "escapes.json").write_text(json.dumps({
        "about": "One escape crystal per escaping class of ONE-BIT-20261108-001B (the seven classes other than 10101 / 00110), "
                 "exported from its recorded escapes: the k-fold cut of the domino plane, one period of the sublattice, each tile "
                 "(O, P, Q) in Euclidean coordinates with the label of the periodic labelling decor_lib found.", "crystals": out}))


if __name__ == "__main__":
    crystal()
    if "--crystals-only" not in sys.argv:
        escapes()
