#!/usr/bin/env python3
"""Check for CRYSTAL-UP-20261108-001B-P001: the last one-bit decoration of the pinwheel, s(0) = 1 0 1 0 1, s(1) = 0 0 1 1 0,
admits a crystal.

    python3 -B check.py            (writes result.json beside this file)

Written apart from the search that found the crystal (CRYSTAL-UP-20261108-001A-E002) and from the main pipeline (atlas_lib,
decor_lib, the growth engine): standard library only, exact rational arithmetic. The cut, collars, closure and angle-count
completeness test are those of the knotlab note's independent replay (publication/knotlab/notes/pinwheel-local-rules/replay.py),
imported unchanged; this file adds labels. The certificate is crystal.json: one period of a parent tiling (20 tiles with labels)
and its lattice.
  1. The tiles tile the plane: no two tiles of a window overlap (separating axes), and the tiles of a period fill the cell's area.
  2. The labelled law of the decoration: the closure of the four one-tile labelled collars (either hand, either label) under the
     labelled cut, kept when complete by the angle count.
  3. The parent tiling is a new kind of crystal: some of its collars are not pinwheel collars.
  4. Cut once, with each child labelled s(parent's label)[child index], every one of the 100 labelled collars of a period lies in
     the law; cut twice, all 500 do.
  5. The fourteen earlier escapes (escapes.json: one certificate per class of ONE-BIT-20261108-001B, exported by
     make_certificates.py from its recorded results): each is a tiling, all its labelled collars lie in its decoration's law, and
     with every label exchanged in the relabelled decoration's law; and the eight classes covered are exactly those
     ROUND-PRICE-20261108-001's exact census left open.
Controls: the undecorated closure has 193 collars, 108 complete (the replay's own counts); the law reached from one labelled tile
is the same from all four, and every collar in it is a pinwheel collar; the uncut labelled crystal does not obey the law;
flipping any one label of the cell breaks the cut.
By the radius lemma (ROUND-PRICE-20261108-001A, Lemma 2), a periodic plane obeying a decorated substitution's collar law gives,
after further cuts, a periodic plane obeying its law at every radius, so the decoration does not force the pinwheel."""
from __future__ import annotations

import importlib.util
import json
import sys
from collections import deque
from fractions import Fraction as F
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
REPLAY = ROOT / "publication/knotlab/notes/pinwheel-local-rules/replay.py"
spec = importlib.util.spec_from_file_location("pinwheel_replay", REPLAY)
R = importlib.util.module_from_spec(spec)
spec.loader.exec_module(R)
SIG = ((1, 0, 1, 0, 1), (0, 0, 1, 1, 0))


def relabel(sig):
    """the decoration obeyed by a decorated tiling once every label is exchanged"""
    return tuple(tuple(1 - x for x in sig[1 - b]) for b in (0, 1))


def lkey(h, c, items):
    return (h, frozenset((tuple(R.frame(c, x) for x in t), lab) for t, lab in items))


def limages(k, sig):
    h, items = k
    kids = [(c, sig[lab][m]) for t, lab in items for m, c in enumerate(R.cut(t))]
    return [lkey(h * R.hand(c), c, [(d, l) for d, l in kids if d == c or R.touch(c, d)]) for c in R.cut(R.BASE)]


def labelled_law(sig, seeds):
    seen, q = set(seeds), deque(seeds)
    while q:
        for k2 in limages(q.popleft(), sig):
            if k2 not in seen:
                seen.add(k2)
                q.append(k2)
    return {k for k in seen if R.complete((k[0], frozenset(t for t, _ in k[1])))}


def interiors_meet(S, T):
    for X, Y in ((S, T), (T, S)):
        for i in range(3):
            a, b, c = X[i], X[(i + 1) % 3], X[(i + 2) % 3]
            side = R.cross(a, b, c)
            if all(R.cross(a, b, p) * side <= 0 for p in Y):
                return False
    return True


def area(t):
    return abs(R.cross(*t)) / 2


def window(cell, basis, r):
    (a, b), (c, d) = basis
    return [(tuple((p[0] + i * a + j * c, p[1] + i * b + j * d) for p in t), lab)
            for i in range(-r, r + 1) for j in range(-r, r + 1) for t, lab in cell]


def cut_labelled(items, sig, k):
    for _ in range(k):
        items = [(c, sig[lab][m]) for t, lab in items for m, c in enumerate(R.cut(t))]
    return items


class Grid:
    """tiles bucketed by the unit cells their bounding boxes meet, to find touching tiles fast"""

    def __init__(self, items, size):
        self.size = size
        self.cells = {}
        for it in items:
            for c in self._cells(it[0]):
                self.cells.setdefault(c, []).append(it)

    def _cells(self, t):
        s = self.size
        xs, ys = [p[0] for p in t], [p[1] for p in t]
        for i in range(int((min(xs) / s).__floor__()), int((max(xs) / s).__floor__()) + 1):
            for j in range(int((min(ys) / s).__floor__()), int((max(ys) / s).__floor__()) + 1):
                yield (i, j)

    def near(self, t):
        out = {}
        for c in self._cells(t):
            for it in self.cells.get(c, ()):
                out[it[0]] = it
        return out.values()


def collars_in(plane, reps, law, size):
    """the labelled collars of the tiles reps, read in the plane, that are not in the law"""
    g = Grid(plane, size)
    bad = 0
    for t, lab in reps:
        bad += lkey(R.hand(t), t, [(u, l) for u, l in g.near(t) if u == t or R.touch(t, u)]) not in law
    return bad


def main():
    crystals = json.loads((HERE / "crystal.json").read_text())["crystals"]
    res = {"checks": {}, "controls": {}, "census": {}}
    keys = R.closure()
    comp = {k for k in keys if R.complete(k)}
    res["controls"]["undecorated closure: 193 collars, 108 complete"] = (len(keys), len(comp)) == (193, 108)
    seeds = [(h, frozenset([(R.BASE, a)])) for h in (1, -1) for a in (0, 1)]
    law = labelled_law(SIG, seeds)
    res["census"]["labelled collars in the law"] = len(law)
    res["controls"]["the law is the same from each one-tile seed"] = all(labelled_law(SIG, [s]) == law for s in seeds)
    res["controls"]["every labelled collar of the law is a pinwheel collar"] = all(
        (k[0], frozenset(t for t, _ in k[1])) in comp for k in law)
    swap = relabel(SIG)
    law_s = labelled_law(swap, seeds)
    rows = []
    for n, c in enumerate(crystals):
        cell = [(tuple((F(x), F(y)) for x, y in t[:3]), t[3]) for t in c["tiles"]]
        basis = tuple(tuple(F(x) for x in v) for v in c["lattice"])
        plane = window(cell, basis, 3)
        det = abs(basis[0][0] * basis[1][1] - basis[0][1] * basis[1][0])
        g0 = Grid(plane, F(2))
        tiled = sum(area(t) for t, _ in cell) == det and not any(
            u != t and interiors_meet(t, u) for t, _ in cell for u, _ in g0.near(t))
        off = sum(1 for t, _ in cell if R.key(R.hand(t), t, [u for u, _ in g0.near(t) if u == t or R.touch(t, u)]) not in comp)
        row = {"seed": c["seed"], "tiles per period": len(cell), "a tiling": tiled, "parent collars that are not pinwheel collars": off}
        depths = (1, 2) if n == 0 or len(cell) == 20 else (1,)
        for k in depths:
            row[f"cut {k} time(s): labelled collars outside the law"] = collars_in(
                cut_labelled(plane, SIG, k), cut_labelled(cell, SIG, k), law, F(1) if k == 1 else F(1, 2))
        cs = [(t, 1 - lab) for t, lab in cell]
        row["labels exchanged, cut once: collars outside the relabelled law"] = collars_in(
            cut_labelled(window(cs, basis, 3), swap, 1), cut_labelled(cs, swap, 1), law_s, F(1))
        rows.append(row)
        if n == 0:
            first = (cell, basis, plane)
    res["census"]["the crystals"] = rows
    res["census"]["crystals checked, tiles per period of the smallest"] = [len(rows), rows[0]["tiles per period"]]
    res["checks"]["every crystal tiles the plane"] = all(r["a tiling"] for r in rows)
    res["checks"]["no crystal's parent tiling is collar-legal"] = all(r["parent collars that are not pinwheel collars"] > 0 for r in rows)
    res["checks"]["every crystal cut once obeys the law of 10101 / 00110"] = all(
        r["cut 1 time(s): labelled collars outside the law"] == 0 for r in rows)
    res["checks"]["the smallest crystal and a 20-tile one cut twice obey it"] = all(
        r.get("cut 2 time(s): labelled collars outside the law", 0) == 0 for r in rows) and sum(
        "cut 2 time(s): labelled collars outside the law" in r for r in rows) >= 2
    res["checks"]["with labels exchanged, every crystal cut once obeys the relabelled decoration 11001 / 01010"] = all(
        r["labels exchanged, cut once: collars outside the relabelled law"] == 0 for r in rows)
    cell, basis, plane = first
    res["controls"]["the smallest crystal uncut does not obey the law"] = collars_in(plane, cell, law, F(2)) > 0
    flips = []
    for i in range(len(cell)):
        c2 = [(t, (1 - lab) if j == i else lab) for j, (t, lab) in enumerate(cell)]
        flips.append(collars_in(cut_labelled(window(c2, basis, 2), SIG, 1), cut_labelled(c2, SIG, 1), law, F(1)) > 0)
    res["controls"]["flipping any one label of the smallest crystal breaks its cut"] = all(flips)
    # the fourteen earlier escapes (ONE-BIT-20261108-001B), one certificate per class, and their relabellings
    esc = json.loads((HERE / "escapes.json").read_text())["crystals"]
    rows = []
    for c in esc:
        sig = tuple(tuple(x) for x in c["decoration"])
        k = c["cuts"]
        tiles = [(tuple((F(x), F(y)) for x, y in t[:3]), t[3]) for t in c["tiles"]]
        b = tuple(tuple(F(x) for x in v) for v in c["lattice"])
        size = F(2, 5 ** ((k + 1) // 2))
        win = window(tiles, b, 1)
        dt = abs(b[0][0] * b[1][1] - b[0][1] * b[1][0])
        g = Grid(win, size)
        tiled = sum(area(t) for t, _ in tiles) == dt and not any(
            u != t and interiors_meet(t, u) for t, _ in tiles for u, _ in g.near(t))
        bad = collars_in(win, tiles, labelled_law(sig, seeds), size)
        rs = relabel(sig)
        flipped = [(t, 1 - lab) for t, lab in tiles]
        bad_r = collars_in(window(flipped, b, 1), flipped, labelled_law(rs, seeds), size)
        rows.append({"decoration": "".join(map(str, sig[0])) + " / " + "".join(map(str, sig[1])),
                     "relabelled": "".join(map(str, rs[0])) + " / " + "".join(map(str, rs[1])),
                     "cuts": k, "tiles per period": len(tiles), "a tiling": tiled, "collars outside the law": bad,
                     "relabelled: collars outside its law": bad_r})
    res["census"]["the fourteen earlier escapes"] = rows
    res["checks"]["each of the seven classes of earlier escapes, and its relabelling, has a periodic plane obeying its law"] = (
        len(rows) == 7 and all(r["a tiling"] and r["collars outside the law"] == 0 and r["relabelled: collars outside its law"] == 0
                               for r in rows))
    cls = {min(tuple(tuple(x) for x in c["decoration"]), relabel(tuple(tuple(x) for x in c["decoration"]))) for c in esc}
    cls.add(min(SIG, relabel(SIG)))
    rp = json.loads((ROOT / "proofs/ROUND-PRICE-20261108-001B/ROUND-PRICE-20261108-001B-P001_labelled_composition_for_the_survivors/result.json").read_text())
    left = [tuple(tuple(x) for x in r["sig"]) for r in rp["census"]["survivors"]
            if r["period-4 brick crystals: first admitted (plane, k, torus)"] is None]
    open_classes = {min(s, relabel(s)) for s in left}
    res["census"]["classes the exact census left open (ROUND-PRICE-20261108-001B)"] = len(open_classes)
    res["checks"]["the certificates cover exactly the eight classes the exact census left open"] = (
        len(open_classes) == 8 and cls == open_classes)
    ok = all(res["checks"].values()) and all(res["controls"].values())
    res["status"] = "passed" if ok else "failed"
    res["failures"] = [k for k, v in {**res["checks"], **res["controls"]}.items() if not v]
    (HERE / "result.json").write_text(json.dumps(res, indent=1) + "\n")
    print(json.dumps(res, indent=1))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
