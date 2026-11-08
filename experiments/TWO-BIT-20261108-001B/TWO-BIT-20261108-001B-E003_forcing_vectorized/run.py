#!/usr/bin/env python3
"""Run for TWO-BIT-20261108-001B-E003: the stop rule's bounded forcing test on 12 surviving products of one-bit decorations, with
arc consistency vectorized (E001, six products at once, and E002, one at a time under a 16 GB cap, were both stopped by memory
before writing a sampled row; E002's control reproduced E001's probe exactly).

    /home/jscul/p-vs-np-contact-first/.venv/bin/python -B run.py
Writes artifacts/TWO-BIT-20261108-001B/TWO-BIT-20261108-001B-E001_forcing_on_a_sample/run/{rows.jsonl, result.json}.

With forcing4.py beside it (multi-label versions of LAST-BIT-20261108-001B's forcing_lib pieces). For 12 of the 3,241 surviving
product classes, drawn by random.sample with seed 1 from the sorted list:
  1. parents: in how many core collars of the level-one law can the central tile's five children carry a label vector that is no
     s(a) (SAT, labels as two-bit words)? Zero means every parent's label is forced;
  2. arc consistency on each factor's labelled level-one collars first, then the product's level-one collars from pairs of the two
     factors' survivors, kept when every child collar's labels lie in the product's law. This loses nothing: the projections of the
     product's arc-consistent collars are arc-consistent for each factor (a supporting neighbour projects to a supporting one);
  3. arc consistency on those (support counts; the first stage of ONE-BIT-20261108-001A's joint test): what is left, split into
     labelled keys of the product's law, pinwheel collars with other labels, and non-pinwheel collars.
Products run one at a time, so a single product's collars are in memory at once.
  4. For the first three sampled products, in sample order, with off-law collars left: a torus search from up to 20 of them each
     (non-pinwheel collars first, then the others, in a seeded random order), by CRYSTAL-UP-20261108-001A-E002's search with the
     arc-consistent collars as the law and at most 100 lattices per seed; a completed torus counts as a crystal when its cut admits a
     periodic two-bit labelling obeying the product's law on the torus's own lattice.
The line pauses after this test, whatever it shows (the epic's frozen stop rule)."""
from __future__ import annotations

import importlib.util
import json
import multiprocessing as mp
import random
import sys
import time
from fractions import Fraction as Fr
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
OUT = ROOT / "artifacts/TWO-BIT-20261108-001B/TWO-BIT-20261108-001B-E003_forcing_vectorized/run"
A_RUN = ROOT / "artifacts/TWO-BIT-20261108-001A/TWO-BIT-20261108-001A-E001_products_against_crystals/run"


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


TA = _load("two_bit_a_run", ROOT / "experiments/TWO-BIT-20261108-001A/TWO-BIT-20261108-001A-E001_products_against_crystals/run.py")
E2 = _load("crystal_up_e002_run", ROOT / "experiments/CRYSTAL-UP-20261108-001A/CRYSTAL-UP-20261108-001A-E002_compatible_periods/run.py")
E2.PARAMS["lattices per seed"] = 100
# forcing4 loads its own copy of the forcing library after the torus search's, so the functions its setup sends to worker
# processes are the ones registered under their module names
import forcing4 as F4  # noqa: E402

F, D = F4.F, F4.D
SAMPLE, TORUS_PRODUCTS, SEEDS = 12, 3, 20
W = {}


def dec(s):
    return tuple(tuple(int(c) for c in part) for part in s.split("/"))


def product_job(pair):
    s1, s2 = dec(pair[0]), dec(pair[1])
    t0 = time.time()
    sig = TA.product(s1, s2)
    L = F.law_as_sets(sig)
    free = F4.parents_free(L, sig)
    L1, L2 = F.law_as_sets(s1), F.law_as_sets(s2)
    Q1, Q2 = F.Q_of(L1, s1), F.Q_of(L2, s2)
    A1, A2 = F4.arc_consistency_np(Q1), F4.arc_consistency_np(Q2)
    S1 = {yi: [p for p in ps if A1[(yi, p)]] for yi, ps in Q1.items()}
    S2 = {yi: [p for p in ps if A2[(yi, p)]] for yi, ps in Q2.items()}
    Q = F4.Q_product_from(S1, S2, L, s1, s2)
    alive = F4.arc_consistency_np(Q)
    core, sk = F.G["core"], F.G["sk"]
    inL, keyout, nonkey = [], [], []
    for (yi, p), ok in alive.items():
        if not ok:
            continue
        Y, iskey = core[yi]
        (nonkey if not iskey else (inL if p in L.get(sk.index[(1, Y)], set()) else keyout)).append((yi, p))
    return {"product": list(pair), "law (labelled collars)": sum(len(v) for v in L.values()),
            "core collars whose centre's children can avoid every s(a)": free,
            "factors' level-one collars, and after arc consistency": [sum(len(v) for v in Q1.values()), sum(len(v) for v in S1.values()),
                                                                       sum(len(v) for v in Q2.values()), sum(len(v) for v in S2.values())],
            "Q": sum(len(v) for v in Q.values()),
            "after arc consistency: in the law, keys with other labels, non-keys": [len(inL), len(keyout), len(nonkey)],
            "seconds": round(time.time() - t0, 1)}, (inL, keyout, nonkey)


def seed_job(args):
    key = args
    return E2.search(key)


def main():
    t0 = time.time()
    OUT.mkdir(parents=True, exist_ok=True)
    surv = json.loads((A_RUN / "result.json").read_text())["survivors"]
    random.seed(1)
    sample = random.sample(sorted(tuple(x) for x in surv), SAMPLE)
    F.setup(4)
    res = {"experiment": "TWO-BIT-20261108-001B-E003", "sample": [list(x) for x in sample], "rows": []}
    # control: the pre-freeze probe's survivor must give E001's arc-consistent counts
    ctrl, _ = product_job(("00001/00010", "00111/10100"))
    res["control"] = {"product": ctrl["product"], "after arc consistency": ctrl["after arc consistency: in the law, keys with other labels, non-keys"],
                      "matches E001's probe (964, 1620, 60)": ctrl["after arc consistency: in the law, keys with other labels, non-keys"] == [964, 1620, 60]}
    print("control", json.dumps(res["control"]), round(time.time() - t0, 1), flush=True)
    outs = []
    with open(OUT / "rows.jsonl", "w") as fh:
        for pair in sample:
            row, parts = product_job(pair)
            outs.append((row, parts))
            fh.write(json.dumps(row) + "\n")
            fh.flush()
            print(json.dumps(row), round(time.time() - t0, 1), flush=True)
    res["rows"] = [row for row, _ in outs]
    print(json.dumps(res["rows"], indent=1), round(time.time() - t0, 1), flush=True)
    # torus searches
    E2.T.light_setup()
    tor = []
    for (row, (inL, keyout, nonkey)) in outs:
        if len(tor) >= TORUS_PRODUCTS or not (keyout or nonkey):
            continue
        s1, s2 = dec(row["product"][0]), dec(row["product"][1])
        sig = TA.product(s1, s2)
        E2.W["kbh"] = E2.T.keys_by_h(inL + keyout + nonkey)
        rng = random.Random(1)
        nk = list(nonkey)
        ko = list(keyout)
        rng.shuffle(nk)
        rng.shuffle(ko)
        seeds = (nk + ko)[:SEEDS]
        keys = [(1, frozenset(zip(F.G["sets"][yi], p))) for yi, p in seeds]
        with mp.Pool(6) as pool:
            found = pool.map(seed_job, keys, chunksize=1)
        allowed = D.law(F.G["sk"], sig)
        crystals = []
        for (yi, p), out in zip(seeds, found):
            for t in out["tori"]:
                cell = [tt for tt, _ in t["cell"]]
                plane = D.Plane(F.G["sk"], cell, t["lattice"], radius=6)
                if TA.periodic4(plane, allowed, 1, (1, 0, 1)):
                    crystals.append({"seed": [yi, list(p)], "tiles per period": t["tiles per period"]})
        tor.append({"product": row["product"], "seeds": len(seeds), "lattices tried": sum(o["lattices"] for o in found),
                    "torus outcomes": {k: sum(o["outcomes"].get(k, 0) for o in found) for k in ("torus", "none", "budget", "invalid")},
                    "crystals": crystals})
        print(json.dumps(tor[-1]), round(time.time() - t0, 1), flush=True)
    res["torus searches"] = tor
    res["sampled survivors whose parents are all forced"] = sum(1 for r in res["rows"] if r["core collars whose centre's children can avoid every s(a)"] == 0)
    res["sampled survivors with off-law collars after arc consistency"] = sum(
        1 for r in res["rows"] if sum(r["after arc consistency: in the law, keys with other labels, non-keys"][1:]) > 0)
    res["crystals found"] = sum(len(t["crystals"]) for t in tor)
    res["seconds"] = round(time.time() - t0, 1)
    (OUT / "result.json").write_text(json.dumps(res, indent=1, default=str) + "\n")
    print(json.dumps({k: v for k, v in res.items() if k not in ("rows",)}, indent=1, default=str))


if __name__ == "__main__":
    main()
