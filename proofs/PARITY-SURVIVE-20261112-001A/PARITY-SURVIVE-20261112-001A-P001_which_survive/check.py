#!/usr/bin/env python3
"""Checks for PARITY-SURVIVE-20261112-001A (research/PARITY-SURVIVE-20261112-001/preregistration.md).

    .venv/bin/python3 -B check.py --part lemma|small|scale|summary [--write]
lemma: for the 45 harmonies (period <= 16), the flip-blind triples the not-all-equal stitch allows (lemma A), and class counts.
small: for the 8 harmonies with a flip-blind triple, every placement on 3 x 3 and 4 x 4 (one per translation class for survival, weighted by
class size; fixing from every base count, which covers every placement): full survival, class-level survival (B1), an isolated parity
cell (B2), and on survivors the tiers F, P, L, GAC. scale: placements with each cell parity independently with probability rho, for rho
in RHOS, n = 3..9, N per cell: survival, class-level survival, isolated parity cells, tiers on survivors; the first-moment rate.
summary: the frozen items. Referee: the background referee thread (pending)."""
import hashlib
import json
import os
import sys
import time
from multiprocessing import Pool
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
T0 = time.time()
DEPS = [str((HERE / f).relative_to(ROOT)) for f in ("survive_lib.py", "check.py")] + \
       ["proofs/PARITY-MIX-20261112-001A/PARITY-MIX-20261112-001A-P001_parity_among_copies/parity_lib.py",
        "proofs/SHIFT-LOCK-20261112-001A/SHIFT-LOCK-20261112-001A-P001_two_shift_locks/shift_lib.py",
        "research/PARITY-SURVIVE-20261112-001/preregistration.md"]
RHOS = (0.125, 0.25, 0.5, 0.75, 0.875)
NS = range(3, 10)
N = 100


def sha(p):
    return hashlib.sha256((ROOT / p).read_bytes()).hexdigest()


def lemma_job(i):
    import survive_lib as L
    h = L.PL.harmonies()[i]
    st = L.setup(h)
    return {"i": i, "harmony": L.PL.name(h), "states": len(st["W"]), "classes": len(st["classes"]),
            "flip-blind triples": L.PL.flip_blind_triples(st), "flip-blind triples the stitch allows": L.fb_in_R(st)}


def small_job(arg):
    import survive_lib as L
    i, n = arg
    h = L.PL.harmonies()[i]
    st = L.setup(h)
    nb = L.cell_neighbours(n)
    rows = []
    t = time.time()
    for K, w in L.PL.translation_classes(n, n):
        full = L.full_state(st, n, K)
        row = {"cells": sorted(K), "k": len(K), "weight": w, "state": full, "class-level state": L.class_level_state(st, n, K),
               "isolated parity cell": L.has_isolated_parity_cell(n, K, nb)}
        if full and 0 < len(K) < n * n:
            row["tiers"] = L.tiers(st, n, K)
        rows.append(row)
    return {"i": i, "n": n, "harmony": L.PL.name(h), "rows": rows, "seconds": round(time.time() - t, 1)}


def scale_job(arg):
    import survive_lib as L
    i, n = arg
    h = L.PL.harmonies()[i]
    st = L.setup(h)
    nb = L.cell_neighbours(n)
    rows = []
    t = time.time()
    for rho in RHOS:
        for s in range(N):
            K = L.bernoulli_placement(n, rho, "PARITY-SURVIVE|%d|%d|%s|%d" % (i, n, rho, s))
            full = L.full_state(st, n, K)
            row = {"rho": rho, "sample": s, "k": len(K), "state": full, "class-level state": L.class_level_state(st, n, K),
                   "isolated parity cell": L.has_isolated_parity_cell(n, K, nb)}
            if full and 0 < len(K) < n * n:
                row["cells"] = sorted(K)
                row["tiers"] = L.tiers(st, n, K)
            rows.append(row)
    return {"i": i, "n": n, "harmony": L.PL.name(h), "rows": rows, "seconds": round(time.time() - t, 1),
            "first-moment rates": {str(rho): L.first_moment_rate(st, rho) for rho in RHOS}}


def picks():
    lem = json.loads((HERE / "result_lemma.json").read_text())["checks"]["result"]["rows"]
    return [r["i"] for r in lem if r["flip-blind triples"] > 0]


def run_part(part):
    import survive_lib as L
    if part == "lemma":
        with Pool(8) as pool:
            return {"rows": pool.map(lemma_job, range(len(L.PL.harmonies())), chunksize=1)}
    part_dir = HERE / "partial"
    part_dir.mkdir(exist_ok=True)
    job = small_job if part == "small" else scale_job
    sizes = (3, 4) if part == "small" else list(reversed(NS))
    args = [(i, n) for n in sizes for i in picks()]
    rows = []
    with Pool(8) as pool:
        for row in pool.imap_unordered(job, args, chunksize=1):
            (part_dir / ("%s_%02d_%d.json" % (part, row["i"], row["n"]))).write_text(json.dumps(row) + "\n")
            rows.append(row)
    return {"rows": sorted(rows, key=lambda r: (r["i"], r["n"]))}


def load(part):
    return json.loads((HERE / ("result_%s.json" % part)).read_text())["checks"]["result"]


def tier_tally(rows, weight_key="weight"):
    """over survivors with 0 < k < nm: (base, count) pairs weighted; fixed in F not frozen; of them not in P; P not in L; F not GAC"""
    t = {"pairs": 0, "F fixed, not flip-frozen": 0, "F not P (the stitches' share)": 0, "P not L": 0, "L": 0, "F not GAC": 0,
         "GAC not computed": 0}
    for x in rows:
        if not x.get("tiers"):
            continue
        w = x.get(weight_key, 1)
        for p in x["tiers"]:
            t["pairs"] += w
            if p["F"] and not p["flip-frozen"]:
                t["F fixed, not flip-frozen"] += w
                if not p["P"]:
                    t["F not P (the stitches' share)"] += w
                if p["P"] and not p["L"]:
                    t["P not L"] += w
                if p["L"]:
                    t["L"] += w
                if p["GAC"] is None:
                    t["GAC not computed"] += w
                elif not p["GAC"]:
                    t["F not GAC"] += w
    return t


def summary():
    lem = load("lemma")["rows"]
    out = {"lemma A: flip-blind triples the stitch allows, over harmonies with any": [[r["harmony"], r["flip-blind triples"], r["flip-blind triples the stitch allows"]] for r in lem if r["flip-blind triples"]],
           "harmonies with exactly 3 classes among those": [r["harmony"] for r in lem if r["flip-blind triples"] and r["classes"] == 3]}
    try:
        sm = load("small")["rows"]
        cells = [x for r in sm for x in r["rows"]]
        mixed = [x for r in sm for x in r["rows"] if 0 < x["k"] < r["n"] ** 2]
        out["B1 lifting never binds: class-level survival equals survival (weighted placements)"] = [sum(x["weight"] for x in cells if x["state"] == x["class-level state"]), sum(x["weight"] for x in cells)]
        out["B1 counterexamples (class-level only)"] = [[r["harmony"], r["n"], x["cells"]] for r in sm for x in r["rows"] if x["class-level state"] and not x["state"]][:30]
        out["B2 isolated parity cell is fatal: survivors with one"] = sum(x["weight"] for x in mixed if x["state"] and x["isolated parity cell"])
        out["small: survivors with 0 < k < nm (weighted)"] = sum(x["weight"] for x in mixed if x["state"])
        out["small: tiers"] = tier_tally(mixed)
    except FileNotFoundError:
        out["small"] = "not run"
    try:
        sc = load("scale")["rows"]
        surv = {}
        for r in sc:
            for x in r["rows"]:
                key = "%d|%s" % (r["n"], x["rho"])
                b = surv.setdefault(key, [0, 0, 0])
                b[0] += 1
                b[1] += bool(x["state"]) and 0 < x["k"] < r["n"] ** 2
                b[2] += bool(x["class-level state"]) and 0 < x["k"] < r["n"] ** 2
        out["scale: survival share by n and rho (all 8 harmonies)"] = {k: round(v[1] / v[0], 4) for k, v in sorted(surv.items())}
        out["scale: class-level survival share by n and rho"] = {k: round(v[2] / v[0], 4) for k, v in sorted(surv.items())}
        mixed = [x for r in sc for x in r["rows"] if 0 < x["k"] < r["n"] ** 2]
        out["scale: B1 class-level without a state"] = sum(1 for x in mixed if x["class-level state"] and not x["state"])
        out["scale: B2 survivors with an isolated parity cell"] = sum(1 for x in mixed if x["state"] and x["isolated parity cell"])
        out["scale: tiers"] = tier_tally(mixed)
        out["scale: first-moment rates"] = {r["harmony"]: r["first-moment rates"] for r in sc if r["n"] == 3}
    except FileNotFoundError:
        out["scale"] = "not run"
    return out


def main():
    if os.environ.get("PYTHONHASHSEED") != "0":
        os.execve(sys.executable, [sys.executable, "-B"] + sys.argv, {**os.environ, "PYTHONHASHSEED": "0"})
    part = sys.argv[sys.argv.index("--part") + 1]
    res = summary() if part == "summary" else run_part(part)
    res = {"dependencies": {p: sha(p) for p in DEPS}, "result": res, "seconds": round(time.time() - T0, 1)}
    path = HERE / ("result_%s.json" % part if part != "summary" else "result.json")
    if "--write" in sys.argv:
        path.write_text(json.dumps({"status": "passed", "checks": res}, indent=1, default=str) + "\n")
        print("wrote", path, round(time.time() - T0, 1), "s")


if __name__ == "__main__":
    main()
