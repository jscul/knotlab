"""The frozen census of OLD-CORE-20261112-001A-E001 (contract.json beside this file): does a growth that adds distinctions end when
its oldest distinctions, read as a pattern by themselves, reach the end of uniform knots?

Processes: RANDOM-FATES-20261112-001A-E001's frozen fates.py (sha256 pinned in the contract), imported by path. Settings: X(0.25)
and X(0.3) to 6,000 moves; X(0.35), O global (0.3) and O local (0.3) to 2,000 moves; 100 growths each; seeds sha256 of
"OC:label:run" (fresh). For every growth that ends, with n distinctions and knots K (the killing knot last):
  core C_k = the knots of K whose three distinctions are all among the oldest k (indices < k); k* = the least k with C_k allowing
  no state (bisection; satisfiability is monotone in k, and C_n allows none); m* = |C_k*|; D* = m*/k*; the floor = the killing
  knot's largest index + 1 (k* is at least the floor, since the killing knot is in every contradiction of K);
  peeled core: C_k* with distinctions in at most one knot removed repeatedly (n2 distinctions, m2 knots);
  P_u = the share of 20 uniform patterns (k* distinctions, m* distinct uniform knots) that allow no state;
  P_u2 = the same with (n2, m2);
  P_d = the share of 20 degree-matched patterns (the core's degree sequence: stubs shuffled into triples, then degree-preserving
        swaps of one stub between two triples until no triple repeats a distinction or another triple) that allow no state;
  k*_deg = the least k with the knots among the k distinctions of highest final degree (ties by age) allowing no state.
For every growth: outcome, knots, distinctions, moves at the end.

Run from the repository root:
    .venv/bin/python -B experiments/OLD-CORE-20261112-001A/OLD-CORE-20261112-001A-E001_old_core/census.py [--workers 8]
    .venv/bin/python -B experiments/OLD-CORE-20261112-001A/OLD-CORE-20261112-001A-E001_old_core/census.py --summary
Output: artifacts/OLD-CORE-20261112-001A/OLD-CORE-20261112-001A-E001_old_core/{runs.jsonl, summary.json}.
"""

from __future__ import annotations

import hashlib
import json
import os
import random
import sys
import time
from collections import Counter
from multiprocessing import Pool

import numpy as np
from pysat.solvers import Solver

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "experiments", "RANDOM-FATES-20261112-001A", "RANDOM-FATES-20261112-001A-E001_fates_census"))
import fates as F  # noqa: E402

OUT = os.path.join(ROOT, "artifacts", "OLD-CORE-20261112-001A", "OLD-CORE-20261112-001A-E001_old_core")
SETTINGS = [("X0.25", 6000), ("X0.3", 6000), ("X0.35", 2000), ("Og0.3", 2000), ("Ol0.3", 2000)]
RUNS = 100
R = 20


def seed_of(*parts):
    return int(hashlib.sha256(":".join(map(str, parts)).encode()).hexdigest()[:12], 16)


def make_gen(label, rng):
    if label.startswith("X"):
        return F.proc_expand(float(label[1:]), rng)
    return F.proc_overlap(float(label[2:]), rng, local=label.startswith("Ol"))


def sat(knots):
    if not knots:
        return True
    with Solver(name=F.SOLVER, bootstrap_with=[c for t in knots for c in F.cls(t)]) as s:
        return s.solve()


def least_dead_prefix(knots, order):
    """The least k such that the knots among the first k distinctions of `order` allow no state."""
    rank = {v: i for i, v in enumerate(order)}
    key = [max(rank[v] for v in t) for t in knots]
    lo, hi = 3, len(order)
    while lo < hi:
        mid = (lo + hi) // 2
        if sat([t for t, kk in zip(knots, key) if kk < mid]):
            lo = mid + 1
        else:
            hi = mid
    return lo


def peel(knots):
    K = list(knots)
    while True:
        deg = Counter(v for t in K for v in t)
        K2 = [t for t in K if all(deg[v] >= 2 for v in t)]
        if len(K2) == len(K):
            return K
        K = K2


def uniform_pattern(n, m, rng):
    seen = set()
    total = n * (n - 1) * (n - 2) // 6
    m = min(m, total)
    while len(seen) < m:
        seen.add(tuple(sorted(rng.sample(range(n), 3))))
    return list(seen)


def degree_pattern(knots, rng, max_swaps=200000):
    stubs = [v for t in knots for v in t]
    rng.shuffle(stubs)
    T = [stubs[i:i + 3] for i in range(0, len(stubs), 3)]

    def bad(i, counts):
        t = T[i]
        return len(set(t)) < 3 or counts[tuple(sorted(t))] > 1

    for _ in range(max_swaps):
        counts = Counter(tuple(sorted(t)) for t in T if len(set(t)) == 3)
        badl = [i for i in range(len(T)) if bad(i, counts)]
        if not badl:
            return [tuple(sorted(t)) for t in T]
        i = rng.choice(badl)
        j = rng.randrange(len(T))
        a, b = rng.randrange(3), rng.randrange(3)
        T[i][a], T[j][b] = T[j][b], T[i][a]
    return None


def task(spec):
    label, run, H = spec
    t0 = time.time()
    rng = random.Random(seed_of("OC", label, run))
    knots, dead = F.grow(make_gen(label, rng), H)
    n = max(v for t in knots for v in t) + 1
    rec = {"label": label, "run": run, "dead": dead, "knots": len(knots), "n": n}
    if dead:
        K = [tuple(sorted(t)) for t in knots]
        ks = least_dead_prefix(K, list(range(n)))
        core = [t for t in K if t[2] < ks]
        used = sorted({v for t in core for v in t})
        pc = peel(core)
        n2 = len({v for t in pc for v in t})
        rr = random.Random(seed_of("OC", label, run, "resample"))
        pu = sum(not sat(uniform_pattern(ks, len(core), rr)) for _ in range(R)) / R
        pu2 = sum(not sat(uniform_pattern(n2, len(pc), rr)) for _ in range(R)) / R if n2 >= 3 else None
        dres = [degree_pattern(core, rr) for _ in range(R)]
        dres = [d for d in dres if d is not None]
        pd = sum(not sat(d) for d in dres) / len(dres) if dres else None
        deg = Counter(v for t in K for v in t)
        order = sorted(range(n), key=lambda v: (-deg[v], v))
        kd = least_dead_prefix(K, order)
        rec.update({"kstar": ks, "mstar": len(core), "Dstar": len(core) / ks, "core_used": len(used),
                    "floor": max(K[-1]) + 1, "n2": n2, "m2": len(pc), "D2": (len(pc) / n2) if n2 else None,
                    "P_u": pu, "P_u2": pu2, "P_d": pd, "degree_resamples": len(dres), "kstar_deg": kd})
    rec["seconds"] = round(time.time() - t0, 1)
    return rec


def run(workers):
    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, "runs.jsonl")
    done = set()
    if os.path.exists(path):
        for line in open(path):
            r = json.loads(line)
            done.add((r["label"], r["run"]))
    specs = [(lab, r, H) for lab, H in SETTINGS for r in range(RUNS) if (lab, r) not in done]
    with Pool(workers) as pool, open(path, "a") as f:
        for rec in pool.imap_unordered(task, specs, chunksize=1):
            f.write(json.dumps(rec) + "\n")
            f.flush()


def med(xs):
    xs = [x for x in xs if x is not None]
    return float(np.median(xs)) if xs else None


def summarize():
    recs = [json.loads(l) for l in open(os.path.join(OUT, "runs.jsonl"))]
    S = {"settings": {}}
    for lab, H in SETTINGS:
        rs = [r for r in recs if r["label"] == lab]
        ends = [r for r in rs if r["dead"]]
        e = {"runs": len(rs), "ended": len(ends)}
        if ends:
            e.update({"kstar_over_n": med([r["kstar"] / r["n"] for r in ends]),
                      "kstar_over_floor": med([r["kstar"] / r["floor"] for r in ends]),
                      "floor_over_n": med([r["floor"] / r["n"] for r in ends]),
                      "Dstar": med([r["Dstar"] for r in ends]), "D2": med([r["D2"] for r in ends]),
                      "P_u": med([r["P_u"] for r in ends]), "P_u2": med([r["P_u2"] for r in ends]),
                      "P_d": med([r["P_d"] for r in ends]),
                      "kdeg_le_kage": float(np.mean([r["kstar_deg"] <= r["kstar"] for r in ends])),
                      "knots_at_end": med([r["knots"] for r in ends])})
        S["settings"][lab] = e
    st = S["settings"]
    labs = [lab for lab, _ in SETTINGS if st[lab]["ended"] >= 10]
    P = {"eligible": labs,
         "L1_uniform_end": {"P_u": {l: st[l]["P_u"] for l in labs}, "holds": all(st[l]["P_u"] >= 0.3 for l in labs)},
         "L1p_uniform_end_peeled": {"P_u2": {l: st[l]["P_u2"] for l in labs}, "holds": all(st[l]["P_u2"] is not None and st[l]["P_u2"] >= 0.3 for l in labs)},
         "L2_degree": {"P_d": {l: st[l]["P_d"] for l in labs}, "holds": all(st[l]["P_d"] is not None and st[l]["P_d"] >= 0.3 for l in labs)},
         "L3_degree_order": {"share": {l: st[l]["kdeg_le_kage"] for l in labs}, "holds": all(st[l]["kdeg_le_kage"] >= 0.7 for l in labs)}}
    S["predictions"] = P
    with open(os.path.join(OUT, "summary.json"), "w") as f:
        json.dump(S, f, indent=1, sort_keys=True, default=lambda o: o.item())
    print(json.dumps(S, indent=1, sort_keys=True, default=lambda o: o.item()))


if __name__ == "__main__":
    if "--summary" in sys.argv:
        summarize()
    else:
        run(int(sys.argv[sys.argv.index("--workers") + 1]) if "--workers" in sys.argv else 8)
