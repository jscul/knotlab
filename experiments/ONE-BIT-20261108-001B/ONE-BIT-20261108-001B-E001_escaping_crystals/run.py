"""ONE-BIT-20261108-001B-E001: crystals that escape the one-bit decorations left open (exploratory; see contract.json).

    /home/jscul/p-vs-np-contact-first/.venv/bin/python -B run.py
Writes artifacts/ONE-BIT-20261108-001B/ONE-BIT-20261108-001B-E001_escaping_crystals/run/{filter.json, rows.jsonl, result.json}."""
from __future__ import annotations

import importlib.util
import itertools
import json
import math
import multiprocessing as mp
import sys
import time
from collections import defaultdict
from fractions import Fraction as Fr
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUT = ROOT / "artifacts/ONE-BIT-20261108-001B/ONE-BIT-20261108-001B-E001_escaping_crystals/run"


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


AB = _load("atlas_b_run", ROOT / "experiments/PINWHEEL-ATLAS-20261107-001B/PINWHEEL-ATLAS-20261107-001B-E001_periodic_planes_against_the_law/run.py")
sys.path.insert(0, str(ROOT / "proofs/ROUND-PRICE-20261108-001A/ROUND-PRICE-20261108-001A-P001_one_hidden_bit_against_the_crystal"))
import decor_lib as D  # noqa: E402

A = D.A
L1_JSON = ROOT / "proofs/COLLAR-PLANE-20261108-001B/COLLAR-PLANE-20261108-001B-P001_the_collar_law_forces_one_level/level_one_law.json"
OPEN = [((0, 0, 0, 0, 1), (1, 0, 0, 1, 0)), ((0, 0, 0, 1, 0), (1, 0, 1, 1, 1)), ((0, 0, 1, 1, 1), (1, 0, 0, 1, 0)),
        ((0, 1, 1, 0, 0), (1, 0, 0, 0, 1)), ((1, 0, 0, 0, 0), (0, 0, 1, 0, 1)), ((1, 0, 1, 0, 1), (0, 0, 0, 0, 0)),
        ((1, 0, 1, 0, 1), (0, 0, 1, 1, 0)), ((1, 0, 1, 1, 0), (0, 0, 1, 0, 1))]
CONTROL = ((1, 0, 0, 0, 1), (0, 1, 1, 0, 0))
TORI = ((2, 2), (2, 4), (4, 2), (2, 6), (6, 2), (4, 4))
W = {}


def l1_sets():
    d = json.loads(L1_JSON.read_text())
    return {frozenset(((Fr(t[0]), Fr(t[1])), (Fr(t[2]), Fr(t[3])), (Fr(t[4]), Fr(t[5]))) for t in c["tiles"]) for c in d["collars"]}


def block(doms, diags, m, n):
    tiles = []
    for a in range(3):
        for b in range(3):
            for (kind, i, j), d in zip(doms, diags):
                x, y = i + a * m, j + b * n
                tiles += AB.rect_h(x, y, d) if kind == "h" else AB.rect_v(x, y, d)
    return [tuple((Fr(p[0]), Fr(p[1])) for p in t) for t in tiles]


def collars(doms, diags, m, n):
    tiles = block(doms, diags, m, n)
    cells = defaultdict(list)
    for t in tiles:
        for c in {(math.floor(p[0]), math.floor(p[1])) for p in t}:
            cells[c].append(t)
    cen = lambda t: (sum(p[0] for p in t) / 3, sum(p[1] for p in t) / 3)
    cell = [t for t in tiles if m <= cen(t)[0] < 2 * m and n <= cen(t)[1] < 2 * n]
    out = []
    for t in cell:
        near = set()
        for p in t:
            for dx in (-2, -1, 0, 1, 2):
                for dy in (-2, -1, 0, 1, 2):
                    near.update(cells.get((math.floor(p[0]) + dx, math.floor(p[1]) + dy), ()))
        col = [u for u in near if u == t or A.touch(t, u)]
        out.append((A.orient(t), tuple(D.canon([tuple(A.to_frame(t, p) for p in u) for u in col]))))
    return cell, out


def classify(typ):
    """1 if the collar is in L1; 2 if its five children's collars are all in L1; 0 otherwise"""
    h, tiles = typ
    if frozenset(tiles) in W["L1"]:
        return 1
    try:
        kids = D.images(h, list(tiles))
    except Exception:
        return 0
    return 2 if all(frozenset(t[1]) in W["L1"] for t, _ in kids) else 0


def init():
    W["L1"] = l1_sets()


def filter_job(spec):
    m, n, doms, diags = spec
    cell, cols = collars(doms, diags, m, n)
    return spec, cols


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    init()
    specs = [(m, n, tuple(map(tuple, doms)), tuple(diags)) for m, n in TORI for doms in AB.torus_dominoes(m, n)
             for diags in itertools.product((0, 1), repeat=len(doms))]
    with mp.Pool(16, initializer=init) as pool:
        results = pool.map(filter_job, specs, chunksize=64)
    types = {}
    for _, cols in results:
        for typ in cols:
            types.setdefault(typ, None)
    with mp.Pool(16, initializer=init) as pool:
        cls = dict(zip(types, pool.map(classify, list(types), chunksize=16)))
    kept = {}
    level_count = defaultdict(int)
    for spec, cols in results:
        c = [cls[t] for t in cols]
        if 0 in c:
            continue
        j = 1 if all(x == 1 for x in c) else 2
        level_count[(spec[0], spec[1], j)] += 1
        sig = tuple(sorted((t[0], t[1]) for t in cols))
        if sig not in kept:
            kept[sig] = (spec, j)
    filt = {"planes": len(specs), "collar types": len(types), "type classes": {str(k): sum(1 for v in cls.values() if v == k) for k in (0, 1, 2)},
            "passing by torus and level": {f"{m}x{n} j={j}": v for (m, n, j), v in sorted(level_count.items())},
            "distinct kept planes": len(kept), "seconds": round(time.time() - t0, 1)}
    print(json.dumps(filt), flush=True)
    (OUT / "filter.json").write_text(json.dumps(filt, indent=1) + "\n")
    # controls on the filter
    def lookup(m, n, doms, diags):
        spec = (m, n, tuple(map(tuple, doms)), tuple(diags))
        for s2, cols in results:
            if s2 == spec:
                c = [cls[t] for t in cols]
                return 0 if 0 in c else (1 if all(x == 1 for x in c) else 2)
    ctl = {
        "the rhombus lattice (2 x 4 vertical, diagonals 0 1 1 0) passes at j = 1": lookup(2, 4, [["v", 0, 0], ["v", 1, 0], ["v", 0, 2], ["v", 1, 2]], [0, 1, 1, 0]) == 1,
        "a period-4 brick plane passes at j = 1": lookup(4, 4, [["h", 0, 0], ["h", 2, 0], ["h", 3, 1], ["h", 1, 1], ["h", 0, 2], ["h", 2, 2], ["h", 3, 3], ["h", 1, 3]], [0, 1, 0, 1, 1, 0, 1, 0]) == 1,
        "the plain rectangle lattice (2 x 2, horizontal, one diagonal) is set aside": lookup(2, 2, [["h", 0, 0], ["h", 0, 1]], [0, 0]) == 0,
    }
    main_rows = [json.loads(l) for l in open(ROOT / "artifacts/COLLAR-PLANE-20261108-001C/COLLAR-PLANE-20261108-001C-E001_periodic_planes_after_cutting/run/main_rows.jsonl")]
    small = {}
    for r in main_rows:
        if r["family"] == "F3 dominoes" and r["passes"]:
            m, n, doms, diags = json.loads(r["plane"])
            small.setdefault((m, n, tuple(map(tuple, doms)), tuple(diags)), r["cuts"])
            small[(m, n, tuple(map(tuple, doms)), tuple(diags))] = min(small[(m, n, tuple(map(tuple, doms)), tuple(diags))], r["cuts"])
    agree = all(lookup(m, n, doms, diags) == k for (m, n, doms, diags), k in small.items())
    ctl["every small-torus plane COLLAR-PLANE-20261108-001C passed is kept at its first passing level"] = agree
    print(json.dumps(ctl), flush=True)
    # labelled tests
    sk = D.Skeleton()
    W["sk"] = sk
    planes = []
    for sig, (spec, j) in kept.items():
        m, n, doms, diags = spec
        cell = []
        for (kind, i, jj), d in zip(doms, diags):
            cell += AB.rect_h(i, jj, d) if kind == "h" else AB.rect_v(i, jj, d)
        planes.append((spec, j, D.Plane(sk, cell, ((m, 0), (0, n)))))
    W["planes"] = planes
    for _, j, P in planes:
        for k in range(j + 3):
            for sp in P.descendants(k):
                P.tile(*sp)
    jobs = [(pi, sig) for pi in range(len(planes)) for sig in OPEN + [CONTROL]]
    rows = []
    with open(OUT / "rows.jsonl", "w") as fh, mp.Pool(16) as pool:
        for row in pool.imap_unordered(label_job, jobs):
            rows.append(row)
            fh.write(json.dumps(row) + "\n")
            fh.flush()
    escapes = defaultdict(list)
    for r in rows:
        if r["admitted at"] is not None:
            escapes[str(r["sig"])].append([r["plane"], r["admitted at"]])
    ctl["the control decoration 10001/01100 is admitted by some plane"] = bool(escapes.get(str([list(CONTROL[0]), list(CONTROL[1])])))
    res = {"experiment": "ONE-BIT-20261108-001B-E001", "filter": filt, "controls": ctl,
           "escapes by decoration": {str([list(s[0]), list(s[1])]): escapes.get(str([list(s[0]), list(s[1])]), []) for s in OPEN + [CONTROL]},
           "open decorations admitted by no plane": [[list(s[0]), list(s[1])] for s in OPEN if not escapes.get(str([list(s[0]), list(s[1])]))],
           "seconds": round(time.time() - t0, 1)}
    (OUT / "result.json").write_text(json.dumps(res, indent=1) + "\n")
    print(json.dumps(res, indent=1))


def label_job(job):
    pi, sig = job
    spec, j, P = W["planes"][pi]
    allowed = D.law(W["sk"], sig)
    tori = [L for m in (1, 2) for L in D.sublattices(m)]
    hit = None
    for k in range(j, j + 3):
        for L in tori:
            ok, model = D.periodic(P, allowed, k, L, want_model=True)
            if ok:
                hit = [k, list(L)]
                break
        if hit:
            break
    return {"plane": [spec[0], spec[1], [list(d) for d in spec[2]], list(spec[3])], "first legal cut": j,
            "sig": [list(sig[0]), list(sig[1])], "admitted at": hit}


if __name__ == "__main__":
    main()
