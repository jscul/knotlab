#!/usr/bin/env python3
"""Checks for PARITY-MIX-20261112-001A (research/PARITY-MIX-20261112-001/preregistration.md).

    .venv/bin/python3 -B check.py --part census|p3|p4|p6|p8|summary [--write]
census: the 45 harmonies (period <= 16): flip-blind parity triples, the largest subspace of classes, which slots of the not-all-equal
stitch are functional up to flips, and two harnesses on 3 x 3 (one parity knot; all parity). p3, p4: every placement of parity knots on
3 x 3 and on 4 x 4 (one per class under the repeat's translations, weighted by class size), for every harmony with a flip-blind triple.
p6, p8: N uniform placements of k parity knots for each k in a frozen list. Each placement: a state?, flip-frozen counts, counts fixed by
count 0 up to flips, counts reached by propagation, the fixed but unreached counts, full fixing. Referee: the background referee
thread (pending)."""
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
DEPS = [str((HERE / f).relative_to(ROOT)) for f in ("parity_lib.py", "check.py")] + \
       ["proofs/SHIFT-LOCK-20261112-001A/SHIFT-LOCK-20261112-001A-P001_two_shift_locks/shift_lib.py",
        "proofs/LOOP-LOCK-20261112-001A/LOOP-LOCK-20261112-001A-P001_loop_locking/loop_lib.py",
        "proofs/ENDLESS-BLOCK-20261112-001A/ENDLESS-BLOCK-20261112-001A-P001_endless_blocks/endless_lib.py",
        "research/PARITY-MIX-20261112-001/preregistration.md"]
SAMPLED = {"p6": (6, list(range(0, 37, 3)), 20), "p8": (8, list(range(0, 65, 4)), 10)}


def sha(p):
    return hashlib.sha256((ROOT / p).read_bytes()).hexdigest()


def census_job(i):
    import parity_lib as L
    h = L.harmonies()[i]
    st = L.setup(h)
    T = L.flip_blind_triples(st)
    one = L.reach(st, 3, 3, frozenset([0]))["state"]
    allp = L.reach(st, 3, 3, frozenset(range(9)))["state"]
    return {"i": i, "harmony": L.name(h), "states": len(st["W"]), "flip-blind triples": T,
            "largest subspace": L.largest_subspace(st) if T else 0, "functional slots": L.functional_slots(st),
            "3 x 3, one parity knot: a state": one, "3 x 3, all parity: a state": allp}


def place_job(arg):
    import parity_lib as L
    part, i = arg
    h = L.harmonies()[i]
    st = L.setup(h)
    func = L.functional_slots(st)
    rows = []
    t = time.time()
    if part in ("p3", "p4"):
        n = 3 if part == "p3" else 4
        for K, weight in L.translation_classes(n, n):
            r = L.cell_row(st, n, n, K, func)
            r["weight"] = weight
            rows.append(r)
    else:
        n, ks, N = SAMPLED[part]
        for k, K in L.placements_sampled(n, n, ks, N, "PARITY-MIX"):
            r = L.cell_row(st, n, n, K, func)
            r["weight"] = 1
            rows.append(r)
    return {"i": i, "harmony": L.name(h), "n": n, "rows": rows, "seconds": round(time.time() - t, 1)}


def run_part(part):
    import parity_lib as L
    if part == "census":
        with Pool(8) as pool:
            return {"rows": pool.map(census_job, range(len(L.harmonies())), chunksize=1)}
    census = json.loads((HERE / "result_census.json").read_text())["checks"]["result"]["rows"]
    pick = [r["i"] for r in census if r["flip-blind triples"] > 0]
    part_dir = HERE / "partial"
    part_dir.mkdir(exist_ok=True)
    rows = []
    with Pool(8) as pool:
        for row in pool.imap_unordered(place_job, [(part, i) for i in pick], chunksize=1):
            (part_dir / ("%s_%02d.json" % (part, row["i"]))).write_text(json.dumps(row) + "\n")
            rows.append(row)
    return {"harmonies": pick, "rows": sorted(rows, key=lambda r: r["i"])}


def load(part):
    return json.loads((HERE / ("result_%s.json" % part)).read_text())["checks"]["result"]


def profile(rows):
    """per k: weighted share with a state, with full fixing, with a fixed but unreached count"""
    by = {}
    for r in rows:
        b = by.setdefault(r["k"], [0, 0, 0, 0])
        b[0] += r["weight"]
        if r["state"]:
            b[1] += r["weight"]
            b[2] += r["weight"] * bool(r["full fixing"])
            b[3] += r["weight"] * (r["fixed but unreached counts"] > 0)
    return {k: {"placements": v[0], "with a state": round(v[1] / v[0], 4), "full fixing": round(v[2] / v[0], 4),
                "fixed but unreached": round(v[3] / v[0], 4)} for k, v in sorted(by.items())}


def summary():
    census = load("census")["rows"]
    out = {"harmonies": len(census),
           "with a flip-blind triple": [[r["harmony"], r["flip-blind triples"], r["largest subspace"]] for r in census if r["flip-blind triples"]],
           "without": len([r for r in census if not r["flip-blind triples"]]),
           "harness: one parity knot on 3 x 3 has a state only with a flip-blind triple": all((not r["3 x 3, one parity knot: a state"]) or r["flip-blind triples"] > 0 for r in census),
           "harness: all parity on 3 x 3 has a state exactly with a flip-blind triple": all(r["3 x 3, all parity: a state"] == (r["flip-blind triples"] > 0) for r in census),
           "functional slots of the not-all-equal stitch": [[r["harmony"], r["functional slots"]] for r in census if any(r["functional slots"].values())]}
    for part in ("p3", "p4", "p6", "p8"):
        try:
            res = load(part)
        except FileNotFoundError:
            out[part] = "not run"
            continue
        rows = res["rows"]
        cells = [(r["harmony"], x) for r in rows for x in r["rows"]]
        nm = rows[0]["n"] ** 2 if rows else 0
        out[part] = {
            "placements with a fixed but unreached count, k < nm": sum(x["weight"] for _, x in cells if x["state"] and x["fixed but unreached counts"] > 0 and x["k"] < nm),
            "harmonies with such a placement": sorted({h for h, x in cells if x["state"] and x["fixed but unreached counts"] > 0 and x["k"] < nm}),
            "smallest k with full fixing, per harmony": {r["harmony"]: min([x["k"] for x in r["rows"] if x["state"] and x["full fixing"]], default=None) for r in rows},
            "profile over all harmonies": profile([x for _, x in cells]),
            "profile per harmony": {r["harmony"]: profile(r["rows"]) for r in rows}}
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
