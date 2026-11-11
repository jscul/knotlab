"""The frozen census of NAE-SURFACE-20261111-001A-E001 (contract.json beside this file).

Does the not-all-equal law read any d-regular world of knots alone faithfully when the world is not a surface?

Run from the repository root:
    .venv/bin/python -B experiments/NAE-SURFACE-20261111-001A/NAE-SURFACE-20261111-001A-E001_faithful_non_surface/census.py
Output: artifacts/NAE-SURFACE-20261111-001A/NAE-SURFACE-20261111-001A-E001_faithful_non_surface/census.json and census_log.txt.
The readings come from KNOTS-ALONE-20261111-001A-E001's frozen library, checked against its recorded hash before use.
"""

from __future__ import annotations

import hashlib
import itertools
import json
import os
import random
import sys
import time
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
LIB = os.path.join(ROOT, "experiments", "KNOTS-ALONE-20261111-001A", "KNOTS-ALONE-20261111-001A-E001_knots_alone_census")
sys.path.insert(0, LIB)
import knots_alone as ka  # noqa: E402

CONTROL = "--control" in sys.argv
OUT = os.path.join(ROOT, "artifacts", "NAE-SURFACE-20261111-001A", "NAE-SURFACE-20261111-001A-E001_faithful_non_surface")
if CONTROL:
    OUT = sys.argv[sys.argv.index("--control") + 1]
os.makedirs(OUT, exist_ok=True)
LOG = open(os.path.join(OUT, "census_log.txt"), "w")

# Frozen families (contract.json, "definitions")
D_RANGE = (4, 5, 6, 7)
F0_V = 6                                    # every world on six distinctions
F1_V = range(13, 31)                        # random sample, 3 | dV
F1_N, F1_SEED = 40, 20261112                # per cell; seed F1_SEED + 100 d + V
F2_V = range(24, 49)                        # faithful flat lattice tori of edge-width >= 5
F2_K, F2_REPS, F2_SEED = (1, 2, 4), 2, 20261113
REGISTERED_F1 = [(d, V) for d in D_RANGE for V in F1_V if (d * V) % 3 == 0]
REGISTERED_F0 = [(d, F0_V) for d in D_RANGE if (d * F0_V) % 3 == 0]


def log(*a):
    msg = " ".join(str(x) for x in a)
    print(msg, flush=True)
    LOG.write(msg + "\n")
    LOG.flush()


def check_library():
    contract = json.load(open(os.path.join(LIB, "contract.json")))
    code = contract["public_inputs"]["code"]
    want = code.split("knots_alone.py (sha256 ")[1].split(")")[0]
    have = hashlib.sha256(open(os.path.join(LIB, "knots_alone.py"), "rb").read()).hexdigest()
    return want == have, have


def defects(V, T):
    """The ways a regular world fails the surface condition."""
    mult = ka.edges_of(T)
    out = {"pairs in one knot": sum(1 for c in mult.values() if c == 1),
           "pairs in three or more": sum(1 for c in mult.values() if c >= 3)}
    pinched = 0
    if not out["pairs in one knot"] and not out["pairs in three or more"]:
        for v in range(V):
            lc = ka.link_cycles(V, T, v)
            if lc is not None and len(lc) > 1:
                pinched += 1
    out["pinched links"] = pinched
    return out


def canon_small(V, T):
    """Canonical form of a triple system by trying every relabelling (small V only)."""
    best = None
    for perm in itertools.permutations(range(V)):
        code = tuple(sorted(tuple(sorted(perm[v] for v in t)) for t in T))
        if best is None or code < best:
            best = code
    return best


def every_world(V, d):
    """Every connected simple d-regular triple system on V distinctions, up to isomorphism (V = 6)."""
    trip = list(itertools.combinations(range(V), 3))
    m = d * V // 3
    classes = {}
    for chosen in itertools.combinations(range(len(trip)), m):
        deg = [0] * V
        for i in chosen:
            for v in trip[i]:
                deg[v] += 1
        if any(x != d for x in deg):
            continue
        T = [trip[i] for i in chosen]
        if not ka.connected(V, T):
            continue
        key = canon_small(V, T)
        classes.setdefault(key, [list(t) for t in key])
    return list(classes.values())


def hexn(x, y):
    return max(abs(x), abs(y)) if x * y >= 0 else abs(x) + abs(y)


def faithful_tori(Vs):
    """Faithful flat lattice tori of edge-width >= 5, one per isomorphism class."""
    seen, out = set(), []
    for V in Vs:
        for a in range(1, V + 1):
            if V % a:
                continue
            c = V // a
            for b in range(c):
                r = ka.lattice_torus_with_coords(a, b, c)
                if r is None:
                    continue
                _, T = r
                code = min(ka.canon_codes_surface(T))
                if code in seen:
                    continue
                seen.add(code)
                L = [(i * a, i * b + j * c) for i in range(-8, 9) for j in range(-8, 9) if (i, j) != (0, 0)]
                ew = min(hexn(*u) for u in L)
                if ew < 5:
                    continue
                if ka.read_law_sat(V, T, ka.LAWS["NAE"]).get("faithful"):
                    out.append({"V": V, "lattice": [a, b, c], "edge_width": ew, "T": [list(t) for t in T]})
    return out


def swap_worlds(V, T, k, seed):
    """k degree-preserving swaps: two disjoint knots {a,b,c}, {x,y,z} become {a,b,z}, {x,y,c}."""
    rng = random.Random(seed)
    knots = [tuple(sorted(t)) for t in T]
    present = set(knots)
    done, tries = 0, 0
    while done < k and tries < 10000:
        tries += 1
        i, j = rng.sample(range(len(knots)), 2)
        t1, t2 = knots[i], knots[j]
        if set(t1) & set(t2):
            continue
        c, z = rng.choice(t1), rng.choice(t2)
        n1 = tuple(sorted([v for v in t1 if v != c] + [z]))
        n2 = tuple(sorted([v for v in t2 if v != z] + [c]))
        if n1 in present or n2 in present or n1 == n2:
            continue
        present -= {t1, t2}
        present |= {n1, n2}
        knots[i], knots[j] = n1, n2
        done += 1
    if done < k:
        return None
    return sorted(knots)


def reading(V, T):
    r = ka.read_law_sat(V, T, ka.LAWS["NAE"])
    return r


def main():
    t0 = time.time()
    lib_ok, lib_sha = check_library()
    log("library hash matches KNOTS-ALONE's contract:", lib_ok, lib_sha)
    if not lib_ok:
        raise SystemExit("library changed")
    records, faithful = [], []
    cells_run = {"F0": [], "F1": [], "F2": []}

    def add(family, cell, V, T, extra=None):
        T = [tuple(t) for t in T]
        if ka.is_surface(V, T):
            return
        r = reading(V, T)
        rec = {"family": family, "cell": list(cell), "V": V, "d": ka.degrees(V, T)[0], "defects": defects(V, T),
               "NAE": r, **(extra or {})}
        if r.get("faithful"):
            rec["T"] = [list(t) for t in T]
            faithful.append(rec)
        records.append(rec)

    if not CONTROL:
        for d, V in REGISTERED_F0:
            worlds = every_world(V, d)
            for T in worlds:
                add("F0", (d, V), V, T)
            cells_run["F0"].append([d, V, len(worlds)])
            log("F0 d", d, "V", V, "classes", len(worlds), round(time.time() - t0, 1), "s")
        for d, V in REGISTERED_F1:
            worlds = ka.random_regular_worlds_sat(V, d, F1_N, seed=F1_SEED + 100 * d + V)
            for T in worlds:
                add("F1", (d, V), V, T)
            cells_run["F1"].append([d, V, len(worlds)])
        log("F1 done", round(time.time() - t0, 1), "s")
        tori = faithful_tori(F2_V)
        log("F2 faithful tori of edge-width >= 5:", len(tori), round(time.time() - t0, 1), "s")
        for n, tor in enumerate(tori):
            for k in F2_K:
                for rep in range(F2_REPS):
                    W = swap_worlds(tor["V"], [tuple(t) for t in tor["T"]], k, seed=F2_SEED + 1000 * n + 10 * k + rep)
                    if W is not None and ka.connected(tor["V"], W):
                        add("F2", (6, tor["V"]), tor["V"], W, {"torus": tor["lattice"], "swaps": k, "rep": rep})
            cells_run["F2"].append([6, tor["V"], tor["lattice"]])
    else:
        # control mode: worlds outside the family (d = 3, and one swap of a 12-distinction flat torus)
        for T in ka.random_regular_worlds_sat(9, 3, 20, seed=1):
            add("control d=3", (3, 9), 9, T)
        T = ka.lattice_tori(12)[-1]
        for k in (1, 2):
            W = swap_worlds(12, T, k, seed=5)
            if W is not None and ka.connected(12, W):
                add("control swap", (6, 12), 12, W, {"swaps": k})
    # coverage: every registered cell was run (the lesson of KNOTS-ALONE's dropped cells)
    coverage = {"F0": sorted(tuple(c[:2]) for c in cells_run["F0"]) == sorted(REGISTERED_F0),
                "F1": sorted(tuple(c[:2]) for c in cells_run["F1"]) == sorted(REGISTERED_F1)}
    log("every registered cell run:", coverage)
    summary = {"coverage": coverage, "cells": cells_run, "worlds": Counter(r["family"] for r in records),
               "faithful": Counter((r["family"], r["d"]) for r in faithful).most_common(),
               "faithful by defect": Counter(tuple(k for k, v in r["defects"].items() if v) for r in faithful).most_common(),
               "smallest faithful": sorted(faithful, key=lambda r: (r["V"], r["d"]))[:3]}
    per_d = defaultdict(Counter)
    for r in records:
        per_d[(r["family"], r["d"])]["sampled"] += 1
        per_d[(r["family"], r["d"])]["faithful"] += bool(r["NAE"].get("faithful"))
        per_d[(r["family"], r["d"])]["native"] += bool(r["NAE"].get("native"))
    summary["per family and d"] = {f"{k[0]} d={k[1]}": dict(v) for k, v in sorted(per_d.items())}
    summary["P1"] = {"holds": any(r["family"] == "F2" for r in faithful)}
    summary["P2"] = {d: any(r["family"] == "F1" and r["d"] == d for r in faithful) for d in D_RANGE}
    summary["P2"]["holds"] = all(summary["P2"][d] for d in D_RANGE)
    summary["P3"] = {"holds": not any(r["family"] == "F0" for r in faithful)}
    summary["seconds"] = round(time.time() - t0, 1)
    log(json.dumps(summary, indent=1, default=str)[:6000])
    with open(os.path.join(OUT, "census.json"), "w") as f:
        json.dump({"summary": summary, "records": records}, f, default=str)


if __name__ == "__main__":
    main()
