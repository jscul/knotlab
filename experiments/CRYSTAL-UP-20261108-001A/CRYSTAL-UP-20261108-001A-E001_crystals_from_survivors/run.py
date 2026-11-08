#!/usr/bin/env python3
"""Run for CRYSTAL-UP-20261108-001A-E001: periodic parent tilings built from the labelled parent collars that survive
LAST-BIT-20261108-001B, for the last one-bit decoration of the pinwheel, s = 10101 / 00110.

    /home/jscul/p-vs-np-contact-first/.venv/bin/python -B run.py
Writes artifacts/CRYSTAL-UP-20261108-001A/CRYSTAL-UP-20261108-001A-E001_crystals_from_survivors/run/{rows.jsonl, result.json}.

With torus_lib.py beside it. The law one level up is S1*: the 513 labelled parent collars surviving that ticket (310 in L(s), 50
pinwheel collars with labels L(s) does not list, 153 non-pinwheel collars). A periodic parent tiling all of whose labelled collars
lie in S1* and one of which is off-law cuts into a periodic plane obeying L(s) that is not a pinwheel tiling: a crystal escaping the
decoration. For each of the 203 off-law collars as seed:
  1. two patches grown by exhaustive extension to tile distance 2 (move orders shuffled by seeds 0 and 1, 3,000 steps each);
  2. candidate periods: translation vectors between two of their tiles with the same shape and label, Euclidean length at most 9
     (the seed's short leg is 1), and between complete tiles with the same labelled collar;
  3. the lattices two candidates span with at most 32 tiles per period, smallest first, the first 120;
  4. growth on each lattice's torus from the seed (torus_lib.torus_grow, 1,000 steps), exhaustive within the budget.
Every completed torus is checked independently: its cell and lattice as a decor_lib plane, every cell collar a core collar, and the
cut admitting a periodic labelling that obeys L(s) (decor_lib.periodic on the plane's own lattice).
Control: the constant decoration 00000 / 11111 with the law Q(L) of its level-one collars and the rhombus lattice's collar as seed:
the same steps must complete a torus that passes the same check under that decoration's law."""
from __future__ import annotations

import json
import multiprocessing as mp
import random
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import torus_lib as T  # noqa: E402

F, D = T.F, T.D
ROOT = HERE.parents[2]
OUT = ROOT / "artifacts/CRYSTAL-UP-20261108-001A/CRYSTAL-UP-20261108-001A-E001_crystals_from_survivors/run"
SURVIVORS = ROOT / "proofs/LAST-BIT-20261108-001B/LAST-BIT-20261108-001B-P001_geometry_alone/survivors.json"
CONST = ((0, 0, 0, 0, 0), (1, 1, 1, 1, 1))
PARAMS = {"patches": 2, "patch depth": 2, "patch budget": 3000, "max length": 9, "max tiles per period": 32, "lattices per seed": 120,
          "torus budget": 1000, "workers": 8}
W = {}


def search(key):
    """steps 1-4 for one seed under the law in W['kbh']"""
    t0 = time.time()
    strict, relaxed, patches = set(), set(), []
    for r in range(PARAMS["patches"]):
        P = T.grow_patch(W["kbh"], key, PARAMS["patch depth"], PARAMS["patch budget"], random.Random(r))
        patches.append(None if P is None else len(P.tiles))
        if P is not None:
            strict |= T.vectors(P)
            relaxed |= T.vectors(P, same_collar=False, max_len2=PARAMS["max length"] ** 2)
    lats = T.lattices(strict | relaxed, PARAMS["max tiles per period"])[:PARAMS["lattices per seed"]]
    out = {"patches": patches, "vectors": [len(strict), len(relaxed | strict)], "lattices": len(lats), "outcomes": {}, "tori": []}
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
    """independent check of a completed torus: a decor_lib plane whose cut admits a periodic labelling obeying `allowed`"""
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
    res = {"experiment": "CRYSTAL-UP-20261108-001A-E001", "parameters": PARAMS, "controls": {}}
    # control: the constant decoration and the rhombus collar
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
    print("control", res["controls"], round(time.time() - t0, 1), flush=True)
    # the decoration
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
