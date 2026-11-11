"""The frozen census of LONG-LOOP-20261111-001A-E001 (contract.json beside this file).

The long-loop regime: is the not-all-equal law (NAE) faithful on every flat world of edge-width at least 5 in range, and on tori of
edge-width at least 6 is bond distance graph distance + 1 out to distance 3?

Run from the repository root:
    .venv/bin/python -B experiments/LONG-LOOP-20261111-001A/LONG-LOOP-20261111-001A-E001_long_loops/census.py
Output: artifacts/LONG-LOOP-20261111-001A/LONG-LOOP-20261111-001A-E001_long_loops/census.json and census_log.txt.
Readings by KNOTS-ALONE-20261111-001A-E001's frozen library, whose hash is checked first.
"""

from __future__ import annotations

import hashlib
import itertools
import json
import os
import random
import sys
import time
from collections import Counter
from multiprocessing import Pool

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
LIB = os.path.join(ROOT, "experiments", "KNOTS-ALONE-20261111-001A", "KNOTS-ALONE-20261111-001A-E001_knots_alone_census")
LIB_SHA = "aee9a2eda0907064b89eae4fe4badddb22b80fecb62bd91d5a5fa448397010de"
sys.path.insert(0, HERE)
sys.path.insert(0, LIB)
import flat_worlds as fw  # noqa: E402
import knots_alone as ka  # noqa: E402
import numpy as np  # noqa: E402
from pysat.solvers import Minisat22  # noqa: E402

CONTROL = "--control" in sys.argv
OUT = os.path.join(ROOT, "artifacts", "LONG-LOOP-20261111-001A", "LONG-LOOP-20261111-001A-E001_long_loops")
if CONTROL:
    OUT = sys.argv[sys.argv.index("--control") + 1]

# Frozen parameters (contract.json, "definitions")
TORUS_V = range(49, 81)
KLEIN_V = range(19, 41)
EW_FAITHFUL = 5        # P1: every world of edge-width >= 5 in range
EW_RULER = 6           # P2: every torus of edge-width >= 6 in range that NAE reads faithfully
SAMPLE, SEED = 4000, 20261114
WORKERS = 12


def log(msg):
    print(msg, flush=True)
    with open(os.path.join(OUT, "census_log.txt"), "a") as f:
        f.write(msg + "\n")


class Oracle:
    """Which value patterns of a set of distinctions extend to an allowed NAE state: a sample first, SAT for the rest."""

    def __init__(self, V, T, seed):
        self.V = V
        self.s = Minisat22(bootstrap_with=ka.law_clauses(T, ka.LAWS["NAE"]))
        rng = random.Random(seed)
        rows = []
        for _ in range(SAMPLE):
            self.s.set_phases([v + 1 if rng.random() < 0.5 else -(v + 1) for v in range(V)])
            self.s.solve()
            m = self.s.get_model()
            rows.append([1 if m[v] > 0 else 0 for v in range(V)])
        self.S = np.array(rows, dtype=np.int64)
        self.cache = {}

    def patterns(self, vars_):
        vars_ = tuple(sorted(vars_))
        if vars_ in self.cache:
            return self.cache[vars_]
        k = len(vars_)
        code = np.zeros(len(self.S), dtype=np.int64)
        for i, v in enumerate(vars_):
            code |= self.S[:, v] << i
        seen = set(np.nonzero(np.bincount(code, minlength=1 << k))[0].tolist())
        for p in range(1 << k):
            if p not in seen:
                bits = [(p >> i) & 1 for i in range(k)]
                if self.s.solve(assumptions=[v + 1 if b else -(v + 1) for v, b in zip(vars_, bits)]):
                    seen.add(p)
        self.cache[vars_] = seen
        return seen

    def free(self, vars_):
        return len(self.patterns(vars_)) == 1 << len(vars_)

    def is_bond(self, S, knots):
        if any(tuple(sorted(t)) in knots for t in itertools.combinations(S, 3)) and len(S) > 3:
            return False
        if self.free(S):
            return False
        return all(self.free([x for x in S if x != y]) for y in S)


def ruler(V, T, seed):
    """Bond distance from distinction 0 to every v at graph distance 2 and 3, as the pre-registration fixes it."""
    knots = set(ka.norm(T))
    delta = ka.graph_distance(V, T, 0)
    o = Oracle(V, T, seed)
    adj = {u: set() for u in range(V)}
    for t in T:
        for a, b in itertools.combinations(t, 2):
            adj[a].add(b)
            adj[b].add(a)
    dist = {u: ka.graph_distance(V, T, u) for u in range(V) if delta[u] <= 3}
    rows = []
    for v in range(1, V):
        if delta[v] not in (2, 3):
            continue
        rec = {"v": v, "delta": delta[v]}
        region = sorted(u for u in range(V) if u not in (0, v) and (delta[u] <= 2 or dist[v][u] <= 2))
        if delta[v] == 2:
            # the lemma: a four-element bond around a hidden distinction (control of the code and the lemma)
            rec["bond4_local"] = any(o.is_bond((0, v) + e, knots) for e in itertools.combinations(region, 2))
        else:
            others = [u for u in range(V) if u not in (0, v)]
            rec["bond4_global"] = any(o.is_bond((0, v) + e, knots) for e in itertools.combinations(others, 2))
            rec["bond5_local"] = any(o.is_bond((0, v) + e, knots) for e in itertools.combinations(region, 3))
        rows.append(rec)
    return rows


def work(item):
    t0 = time.time()
    V, T, ew, kind, idx = item["V"], [tuple(t) for t in item["T"]], item["ew"], item["kind"], item["idx"]
    r = ka.read_law_sat(V, T, ka.LAWS["NAE"])
    out = {"idx": idx, "kind": kind, "V": V, "edge_width": ew, "NAE": r}
    if kind == "torus" and ew >= EW_RULER and r.get("faithful"):
        out["ruler"] = ruler(V, T, SEED + idx)
    elif item.get("force_ruler") and r.get("faithful"):
        out["ruler"] = ruler(V, T, SEED + idx)
    out["seconds"] = round(time.time() - t0, 1)
    return out


def worlds():
    items, seen = [], set()
    for V in TORUS_V:
        for L in fw.sublattices(V):
            r = fw.torus(L)
            if r is None:
                continue
            v_, T, ew = r
            if not ka.is_surface(v_, T):
                continue
            code = min(ka.canon_codes_surface(T))
            if code in seen:
                continue
            seen.add(code)
            items.append({"V": v_, "T": T, "ew": ew, "kind": "torus", "lattice": [L.a, L.b, L.c]})
    for V in KLEIN_V:
        for v_, T, ew in fw.klein_bottles(V):
            if not (ka.is_surface(v_, T) and not ka.orientable(T)):
                continue
            code = min(ka.canon_codes_surface(T))
            if code in seen:
                continue
            seen.add(code)
            items.append({"V": v_, "T": T, "ew": ew, "kind": "Klein"})
    return items


def klein_control():
    """The glide quotients against the exhaustive SAT Klein bottles of KNOTS-ALONE, 7..16 distinctions."""
    ok = {}
    for V in range(7, 17):
        reps, n = ka.surface_worlds_sat(V, 6)
        sat = sorted(min(ka.canon_codes_surface(T)) for T in reps if not ka.orientable(T))
        glide = set()
        for v_, T, ew in fw.klein_bottles(V):
            if ka.is_surface(v_, T) and not ka.orientable(T):
                glide.add(min(ka.canon_codes_surface(T)))
        ok[V] = sorted(glide) == sat
    return ok


def main():
    os.makedirs(OUT, exist_ok=True)
    open(os.path.join(OUT, "census_log.txt"), "w").close()
    t0 = time.time()
    have = hashlib.sha256(open(os.path.join(LIB, "knots_alone.py"), "rb").read()).hexdigest()
    log(f"library hash matches: {have == LIB_SHA}")
    if have != LIB_SHA:
        raise SystemExit("library changed")
    if CONTROL:
        # outside the family: the KNOTS-ALONE tori with 21 distinctions (a known shortcut at distance 3) and 24
        items = []
        for V in (21, 24):
            for i, L in enumerate(fw.sublattices(V)):
                r = fw.torus(L)
                if r and ka.is_surface(r[0], r[1]):
                    items.append({"V": V, "T": r[1], "ew": r[2], "kind": "control torus", "idx": len(items),
                                  "lattice": [L.a, L.b, L.c], "force_ruler": True})
        items = items[:6]
        kc = {}
    else:
        kc = klein_control()
        log(f"glide Klein bottles = SAT Klein bottles at 7..16: {all(kc.values())} {kc}")
        items = worlds()
        for i, it in enumerate(items):
            it["idx"] = i
    log(f"worlds: {Counter((it['kind'], it['ew']) for it in items)} ({round(time.time() - t0, 1)} s)")
    with Pool(WORKERS) as pool:
        results = pool.map(work, items, chunksize=1)
    for it, r in zip(items, results):
        r["lattice"] = it.get("lattice")
        r["T"] = it["T"]
    # P1
    p1_worlds = [r for r in results if r["edge_width"] >= EW_FAITHFUL and r["kind"] in ("torus", "Klein")]
    p1_fail = [{k: r[k] for k in ("kind", "V", "edge_width", "lattice", "NAE")} for r in p1_worlds if not r["NAE"].get("faithful")]
    # P2
    p2_worlds = [r for r in results if "ruler" in r and r["kind"] == "torus"]
    p2_fail = []
    for r in p2_worlds:
        for row in r["ruler"]:
            if row["delta"] == 2 and not row["bond4_local"]:
                p2_fail.append([r["V"], r["lattice"], row])
            if row["delta"] == 3 and (row["bond4_global"] or not row["bond5_local"]):
                p2_fail.append([r["V"], r["lattice"], row])
    p2_ineligible = [[r["V"], r["lattice"]] for r in results if r["kind"] == "torus" and r["edge_width"] >= EW_RULER
                     and not r["NAE"].get("faithful")]
    below = Counter((r["kind"], r["edge_width"], bool(r["NAE"].get("faithful"))) for r in results if r["edge_width"] < EW_FAITHFUL)
    summary = {"klein control": kc, "worlds": len(results),
               "P1": {"worlds": len(p1_worlds), "failures": p1_fail, "holds": bool(p1_worlds) and not p1_fail},
               "P2": {"tori": len(p2_worlds), "not faithful (outside P2)": p2_ineligible, "failures": p2_fail,
                      "holds": bool(p2_worlds) and not p2_fail},
               "below edge-width 5 (no prediction)": sorted([list(k) + [n] for k, n in below.items()]),
               "seconds": round(time.time() - t0, 1)}
    if CONTROL:
        summary["control rulers"] = [[r["V"], r["lattice"], r["edge_width"], r["NAE"].get("faithful"),
                                      [row for row in r.get("ruler", []) if row["delta"] == 3][:4]] for r in results]
    log(json.dumps(summary, indent=1, default=str)[:8000])
    with open(os.path.join(OUT, "census.json"), "w") as f:
        json.dump({"summary": summary, "results": results}, f, default=str)


if __name__ == "__main__":
    main()
