#!/usr/bin/env python3
"""Run for CRYSTAL-UP-20261108-001A-E002: periodic parent tilings from the labelled parent collars surviving LAST-BIT-20261108-001B,
with candidate periods filtered by the seed collar itself.

    /home/jscul/p-vs-np-contact-first/.venv/bin/python -B run.py
Writes artifacts/CRYSTAL-UP-20261108-001A/CRYSTAL-UP-20261108-001A-E002_compatible_periods/run/{rows.jsonl, result.json}.

E001 (stopped after 12 seeds) tried the 120 smallest lattices its candidate periods span, and the seed collar fitted on none. Two
necessary conditions, each exact, now filter them:
  - tiles of one orbit share shape and label, so a crystal containing the seed collar C has at least n(C) tiles per period, the
    number of distinct (shape, label) classes among C's tiles;
  - a period v maps tiles to tiles, so every tile of C + v and of C - v either is a tile of C with the same label or overlaps none;
    this must hold for every vector of the lattice, which matters only up to the collar's diameter.
For each of the 203 off-law collars of S1* as seed: E001's two patches (exhaustive extension to tile distance 2, move orders
shuffled by seeds 0 and 1, 3,000 steps each) and candidate periods (translation vectors between two patch tiles with the same shape
and label, Euclidean length at most 9, and between complete tiles with the same labelled collar); the periods compatible with C; the
lattices two compatible periods span with n(C) to 48 tiles per period whose every vector up to the collar's diameter is compatible
with C, smallest first, at most 200; growth on each torus from the
seed (E001's torus_lib.torus_grow, 1,000 steps). Every completed torus gets E001's independent check (a decor_lib plane whose cut
admits a periodic labelling obeying L(s)). Control: E001's, the constant decoration's rhombus seed, through these same steps."""
from __future__ import annotations

import json
import multiprocessing as mp
import random
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
E001 = HERE.parent / "CRYSTAL-UP-20261108-001A-E001_crystals_from_survivors"
sys.path.insert(0, str(E001))
import torus_lib as T  # noqa: E402

F, D, GE = T.F, T.D, T.GE
OUT = ROOT / "artifacts/CRYSTAL-UP-20261108-001A/CRYSTAL-UP-20261108-001A-E002_compatible_periods/run"
SURVIVORS = ROOT / "proofs/LAST-BIT-20261108-001B/LAST-BIT-20261108-001B-P001_geometry_alone/survivors.json"
CONST = ((0, 0, 0, 0, 0), (1, 1, 1, 1, 1))
PARAMS = {"patches": 2, "patch depth": 2, "patch budget": 3000, "max length": 9, "max tiles per period": 48, "lattices per seed": 200,
          "torus budget": 1000, "workers": 8}
W = {}


def shift(t, v):
    return tuple((p[0] + v[0], p[1] + v[1]) for p in t)


def classes(C):
    return len({(T.shape(t), l) for t, l in C})


def compatible(C, v):
    lab = dict(C)
    for t, l in C:
        for s in (1, -1):
            u = shift(t, (s * v[0], s * v[1]))
            if u in lab:
                if lab[u] != l:
                    return False
            elif any(GE.interiors_meet(u, t2) for t2 in lab):
                return False
    return True


def reach2(C):
    """squared Euclidean diameter of the collar: a translate by a longer vector meets none of its tiles"""
    pts = [q for t, _ in C for q in t]
    return max(T.norm2((a[0] - b[0], a[1] - b[1])) for a in pts for b in pts)


def lattice_ok(C, basis, r2):
    """every lattice vector no longer than the collar's diameter is compatible with C (the basis is Lagrange-Gauss reduced)"""
    b1, b2 = basis
    K = int(1.6 * (float(r2) / float(T.norm2(b1))) ** 0.5) + 2   # |a|, |b| <= 1.58 r / |b1| for a reduced basis
    for a in range(-K, K + 1):
        for b in range(-K, K + 1):
            if (a, b) <= (0, 0):
                continue
            v = (a * b1[0] + b * b2[0], a * b1[1] + b * b2[1])
            if T.norm2(v) <= r2 and not compatible(C, v):
                return False
    return True


def search(key):
    t0 = time.time()
    C = sorted(key[1])
    nmin = classes(C)
    r2 = reach2(C)
    cands, patches = set(), []
    for r in range(PARAMS["patches"]):
        P = T.grow_patch(W["kbh"], key, PARAMS["patch depth"], PARAMS["patch budget"], random.Random(r))
        patches.append(None if P is None else len(P.tiles))
        if P is not None:
            cands |= T.vectors(P) | T.vectors(P, same_collar=False, max_len2=PARAMS["max length"] ** 2)
    good = {v for v in cands if compatible(C, v)}
    spanned = [x for x in T.lattices(good, PARAMS["max tiles per period"]) if x[0] >= nmin]
    lats = [x for x in spanned if lattice_ok(C, x[1], r2)][:PARAMS["lattices per seed"]]
    out = {"n(C)": nmin, "patches": patches, "candidate periods": len(cands), "compatible periods": len(good),
           "lattices spanned": len(spanned), "lattices": len(lats), "tiles per period of the lattices": sorted({n for n, _ in lats}), "outcomes": {}, "tori": []}
    for n, basis in lats:
        res, _ = T.torus_grow(W["kbh"], key, basis, PARAMS["torus budget"], n)
        out["outcomes"][res[0]] = out["outcomes"].get(res[0], 0) + 1
        if res[0] == "torus":
            out["tori"].append({"tiles per period": n, "lattice": basis, "cell": res[1]})
    out["seconds"] = round(time.time() - t0, 1)
    return out


def job(seed):
    yi, p = seed
    return seed, search((1, frozenset(zip(F.G["sets"][yi], p))))


def verify(torus, allowed, core_sets):
    cell = [t for t, _ in torus["cell"]]
    plane = D.Plane(F.G["sk"], cell, torus["lattice"], radius=6)
    sk = F.G["sk"]
    in_core = all(sk.types[n][1] in core_sets for n, _ in plane.root)
    off_key = sum(1 for n, _ in plane.root if not (n < sk.n_keys and sk.complete[n]))
    return {"cell collars in the core": in_core, "cell collars that are not pinwheel collars": off_key,
            "cut admits a periodic labelling obeying the law": bool(in_core and D.periodic(plane, allowed, 1, (1, 0, 1)))}


def jsonable(x):
    if isinstance(x, dict):
        return {str(k): jsonable(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [jsonable(v) for v in x]
    if hasattr(x, "numerator") and not isinstance(x, int):
        return str(x)
    return x


def main():
    t0 = time.time()
    OUT.mkdir(parents=True, exist_ok=True)
    T.light_setup()
    core_sets = set(F.G["sets"])
    res = {"experiment": "CRYSTAL-UP-20261108-001A-E002", "parameters": PARAMS, "controls": {}}
    Lc = F.law_as_sets(CONST)
    Qc = F.Q_of(Lc, CONST)
    W["kbh"] = T.keys_by_h([(yi, p) for yi, ps in Qc.items() for p in ps])
    plane = D.Plane(F.G["sk"], D.RHOMBUS, D.RHOMBUS_LATTICE)
    rh = F.G["sets"].index(F.G["sk"].types[plane.root[0][0]][1])
    ctrl = search((1, frozenset(zip(F.G["sets"][rh], (0,) * len(F.G["sets"][rh])))))
    allowed_c = D.law(F.G["sk"], CONST)
    checks = [verify(t, allowed_c, core_sets) for t in ctrl["tori"]]
    res["controls"]["the constant decoration's rhombus seed completes a torus that passes the check"] = any(
        c["cut admits a periodic labelling obeying the law"] for c in checks)
    res["control run"] = jsonable({k: v for k, v in ctrl.items() if k != "tori"} | {"tori": [t["tiles per period"] for t in ctrl["tori"]]})
    print("control", res["controls"], res["control run"], round(time.time() - t0, 1), flush=True)
    surv = json.loads(SURVIVORS.read_text())
    L, inL, ko, nk = T.survivor_law(surv)
    W["kbh"] = T.keys_by_h(inL + ko + nk)
    res["law S1*: in L(s), keys outside L(s), non-keys"] = [len(inL), len(ko), len(nk)]
    allowed = D.law(F.G["sk"], T.SIG)
    seeds = nk + ko
    nkset = set(nk)
    found = []
    with open(OUT / "rows.jsonl", "w") as fh, mp.Pool(PARAMS["workers"]) as pool:
        for n, ((yi, p), out) in enumerate(pool.imap_unordered(job, seeds, chunksize=1)):
            row = {"seed": [yi, list(p)], "kind": "non-key" if (yi, p) in nkset else "key outside L(s)"}
            row.update({k: v for k, v in out.items() if k != "tori"})
            row["tori"] = []
            for t in out["tori"]:
                chk = verify(t, allowed, core_sets)
                row["tori"].append(jsonable(t) | {"check": chk})
                if chk["cut admits a periodic labelling obeying the law"]:
                    found.append(row["seed"])
            fh.write(json.dumps(jsonable(row)) + "\n")
            fh.flush()
            if n % 10 == 0:
                print(n, len(seeds), "crystals so far", len(found), round(time.time() - t0, 1), flush=True)
    rows = [json.loads(x) for x in (OUT / "rows.jsonl").read_text().splitlines()]
    tot = {}
    for r in rows:
        for k, v in r["outcomes"].items():
            tot[k] = tot.get(k, 0) + v
    res["seeds"] = len(rows)
    res["seeds with a patch"] = sum(1 for r in rows if any(x is not None for x in r["patches"]))
    res["seeds with a compatible period"] = sum(1 for r in rows if r["compatible periods"])
    res["compatible periods (total)"] = sum(r["compatible periods"] for r in rows)
    res["lattices spanned (before the lattice filter)"] = sum(r["lattices spanned"] for r in rows)
    res["seeds with a lattice"] = sum(1 for r in rows if r["lattices"])
    res["lattices tried"] = sum(r["lattices"] for r in rows)
    res["torus outcomes"] = tot
    res["completed tori"] = sum(len(r["tori"]) for r in rows)
    res["crystals (completed tori passing the check)"] = len(found)
    res["seeds with a crystal"] = found
    res["status"] = "passed" if all(res["controls"].values()) else "failed"
    res["seconds"] = round(time.time() - t0, 1)
    (OUT / "result.json").write_text(json.dumps(jsonable(res), indent=1) + "\n")
    print(json.dumps(jsonable(res), indent=1))
    return 0 if res["status"] == "passed" else 1


if __name__ == "__main__":
    sys.exit(main())
