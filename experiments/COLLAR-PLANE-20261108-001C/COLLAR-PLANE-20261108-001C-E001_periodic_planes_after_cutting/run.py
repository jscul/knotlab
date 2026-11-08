"""COLLAR-PLANE-20261108-001C-E001: which of PINWHEEL-ATLAS-20261107-001B's periodic planes become collar-legal after cutting?
(exploratory; see contract.json)

    python3 -B run.py main        F1, F2, F4 at 1-3 cuts; F3's 2 x 2, 2 x 4 and 4 x 2 tori at 1 and 2 cuts
    python3 -B run.py big1        the background part: F3's 2 x 6, 6 x 2 and 4 x 4 tori at 1 cut
Writes artifacts/COLLAR-PLANE-20261108-001C/COLLAR-PLANE-20261108-001C-E001_periodic_planes_after_cutting/run/<part>_rows.jsonl and
<part>_result.json."""
from __future__ import annotations

import itertools
import json
import math
import multiprocessing as mp
import sys
import time
from collections import Counter
from fractions import Fraction as Fr
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
import importlib.util  # noqa: E402


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


AB = _load("atlas_b_run", ROOT / "experiments/PINWHEEL-ATLAS-20261107-001B/PINWHEEL-ATLAS-20261107-001B-E001_periodic_planes_against_the_law/run.py")
CA = _load("collar_plane_a_check", ROOT / "proofs/COLLAR-PLANE-20261108-001A/COLLAR-PLANE-20261108-001A-P001_a_periodic_plane_obeys_every_radius/check.py")

A = CA.A
OUT = ROOT / "artifacts/COLLAR-PLANE-20261108-001C/COLLAR-PLANE-20261108-001C-E001_periodic_planes_after_cutting/run"
W = {}
WORKERS = int(__import__("os").environ.get("WORKERS", "22"))


def init():
    keys, complete = CA.law()
    W["complete"] = complete


def frac(t):
    return tuple((Fr(p[0]), Fr(p[1])) for p in t)


def centroid(t):
    return (sum(p[0] for p in t) / 3, sum(p[1] for p in t) / 3)


def test(tiles, k, window, margin):
    """does every tile with centroid in the half-open window have a complete key after k cuts?"""
    x0, y0, x1, y1 = window
    near = [frac(t) for t in tiles if all(x0 - margin <= p[0] <= x1 + margin and y0 - margin <= p[1] <= y1 + margin for p in t)]
    cut = CA.cut_k(near, k)
    reps = [t for t in cut if x0 <= centroid(t)[0] < x1 and y0 <= centroid(t)[1] < y1]
    n, bad, used = CA.collar_test(cut, reps, W["complete"])
    return n, bad, used


def job(spec):
    fam, name, k = spec
    t0 = time.time()
    if fam in ("F1 grid", "F2 brick"):
        pat = json.loads(name)
        tiles = AB.rows_plane(pat, 6, fam == "F2 brick")
        n, bad, used = test(tiles, k, (0, 0, 4, 4), 3)
    elif fam == "F3 dominoes":
        m, nn, doms, diags = json.loads(name)
        doms = [tuple(d) for d in doms]
        tiles = AB.torus_plane(doms, diags, m, nn, size=max(m, nn) + 8)
        # torus_plane starts at the origin; shift the window inside, away from the patch edge
        n, bad, used = test(tiles, k, (m, nn, 2 * m, 2 * nn), 3)
    elif fam == "F4 half-turn shapes":
        poly, pair = AB.two_tile_shapes()[name]
        tiles = AB.halfturn_plane(poly, pair, 40)
        n, bad, used = test(tiles, k, (-15, -15, 15, 15), 15)
    else:
        raise ValueError(fam)
    return {"family": fam, "plane": name, "cuts": k, "tested": n, "not keys": bad, "keys used": used, "passes": n > 0 and bad == 0,
            "seconds": round(time.time() - t0, 2)}


def specs(part):
    out = []
    if part == "main":
        for fam, brick in (("F1 grid", False), ("F2 brick", True)):
            for p, q in ((1, 1), (1, 2), (2, 1), (2, 2)):
                for bits in itertools.product((0, 1), repeat=p * q):
                    pat = [list(bits[i * q:(i + 1) * q]) for i in range(p)]
                    out += [(fam, json.dumps(pat), k) for k in (1, 2, 3)]
        out += [("F4 half-turn shapes", name, k) for name in AB.two_tile_shapes() for k in (1, 2, 3)]
    tori = {"main": ((2, 2), (2, 4), (4, 2)), "big1": ((2, 6), (6, 2), (4, 4))}[part]
    cuts = {"main": (1, 2), "big1": (1,)}[part]
    for m, n in tori:
        for doms in AB.torus_dominoes(m, n):
            for diags in itertools.product((0, 1), repeat=len(doms)):
                name = json.dumps([m, n, [list(d) for d in doms], list(diags)])
                out += [("F3 dominoes", name, k) for k in cuts]
    return out


def controls():
    init()
    res = {}
    poly, pair = AB.two_tile_shapes()["isosceles triangle (mirror across the short leg)"]
    n, bad, _ = test(AB.halfturn_plane(poly, pair, 40), 1, (-15, -15, 15, 15), 15)
    res["the rhombus lattice passes after one cut"] = n > 0 and bad == 0
    for k in (1, 2):
        n, bad, _ = test(AB.rows_plane([[0]], 6, False), k, (0, 0, 4, 4), 3)
        res[f"the rectangle lattice fails after {k} cut(s)"] = bad > 0
    # a genuine pinwheel patch: tiles within two tile sizes of the centroid of T_5's big triangle (about eight tile sizes from its edge)
    # all have complete keys (no cut needed)
    tiles = [frac(t) for t in AB.A.pinwheel_patch(5)]
    big = ((0, 0), (2 * 10 ** 5, 0), (0, 10 ** 5))
    cx, cy = Fr(sum(p[0] for p in big), 3), Fr(sum(p[1] for p in big), 3)
    size = max(max(abs(t[i][0] - t[(i + 1) % 3][0]) for i in range(3)) for t in tiles)
    win = (cx - 2 * size, cy - 2 * size, cx + 2 * size, cy + 2 * size)
    reps = [t for t in tiles if win[0] <= centroid(t)[0] < win[2] and win[1] <= centroid(t)[1] < win[3]]
    n, bad, _ = CA.collar_test(tiles, reps, W["complete"])
    res["a genuine pinwheel patch passes in its interior"] = n > 0 and bad == 0
    return res


def main(part):
    OUT.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    ctl = controls()
    print(json.dumps(ctl), flush=True)
    if not all(ctl.values()):
        (OUT / f"{part}_result.json").write_text(json.dumps({"controls": ctl, "status": "controls failed"}, indent=1) + "\n")
        return 1
    jobs = specs(part)
    rows = []
    with open(OUT / f"{part}_rows.jsonl", "w") as fh, mp.Pool(WORKERS, initializer=init) as pool:
        for i, row in enumerate(pool.imap_unordered(job, jobs, chunksize=8)):
            rows.append(row)
            if row["passes"] or row["family"] != "F3 dominoes":
                fh.write(json.dumps(row) + "\n")
                fh.flush()
            if i % 2000 == 0:
                print(i, len(jobs), round(time.time() - t0, 1), flush=True)
    summary = {}
    for fam in sorted({r["family"] for r in rows}):
        for k in (1, 2, 3):
            rs = [r for r in rows if r["family"] == fam and r["cuts"] == k]
            if not rs:
                continue
            key = f"{fam}, {k} cut(s)"
            summary[key] = {"planes": len(rs), "pass": sum(r["passes"] for r in rs)}
            if fam == "F3 dominoes":
                by = Counter((json.loads(r["plane"])[0], json.loads(r["plane"])[1]) for r in rs if r["passes"])
                tot = Counter((json.loads(r["plane"])[0], json.loads(r["plane"])[1]) for r in rs)
                summary[key]["by torus (pass / planes)"] = {f"{m}x{n}": f"{by[(m, n)]} / {tot[(m, n)]}" for (m, n) in sorted(tot)}
            else:
                summary[key]["passing planes"] = [r["plane"] for r in rs if r["passes"]]
    res = {"experiment": "COLLAR-PLANE-20261108-001C-E001", "part": part, "controls": ctl, "summary": summary,
           "planes tested": len(rows), "seconds": round(time.time() - t0, 1)}
    (OUT / f"{part}_result.json").write_text(json.dumps(res, indent=1) + "\n")
    print(json.dumps(summary, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "main"))
