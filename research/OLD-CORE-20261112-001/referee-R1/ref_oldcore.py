#!/usr/bin/env python3
"""Referee OLD-CORE-R1, with the referee's own code (RANDOM-FATES-R1's ref_fates.py generators, which draw in the frozen order; no
import of census.py or fates.py):
  regen    every growth regenerated from the census's seeds (sha256 of "OC:label:run"); for every ending, k*, m*, the floor, the
           peeled core (n2, m2) and k*_deg recomputed and compared with the record; and P_d with a fair degree-matched sampler: the
           switch chain on 3-uniform patterns with the core's degree sequence (pick two knots and one member of each, swap them when
           both new knots have three distinct members and are not already knots; the proposal is symmetric, so the chain's stationary
           law is uniform on the simple patterns it reaches), from two starts: the core itself, and the census's kind of start
           (stubs shuffled into triples and repaired by stub swaps, reimplemented); burn-in 20 m steps, then 20 samples 5 m steps
           apart; the share of samples that allow no state;
  missing  the two O global growths the census stopped (runs 54 and 99): the same measures, P_u and P_u2 with 20 uniform resamples
           each, every solver call capped by a conflict budget (unknown past it).

    python3 -B ref_oldcore.py regen|missing [workers]      (writes result_regen.jsonl / result_missing.json)"""
import itertools
import json
import random
import sys
import time
from collections import Counter
from multiprocessing import Pool
from pathlib import Path

from pysat.solvers import Glucose4, Solver

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "research" / "RANDOM-FATES-20261112-001" / "referee-R1"))
import ref_fates as RF  # noqa: E402

ART = ROOT / "artifacts" / "OLD-CORE-20261112-001A" / "OLD-CORE-20261112-001A-E001_old_core"
H = {"X0.25": 6000, "X0.3": 6000, "X0.35": 2000, "Og0.3": 2000, "Ol0.3": 2000}


def grow(label, run):
    rng = random.Random(RF.seed_of("OC", label, run))
    g = RF.make(label, rng)
    knots = []
    with Glucose4() as s:
        for _ in range(H[label]):
            t = next(g)
            if t is None:
                continue
            knots.append(tuple(sorted(t)))
            for c in RF.nae_clauses(t):
                s.add_clause(c)
            if not s.solve():
                return knots, True
    return knots, False


def sat(knots, budget=None):
    if not knots:
        return True
    with Solver(name="cadical153", bootstrap_with=[c for t in knots for c in RF.nae_clauses(t)]) as s:
        if budget is None:
            return s.solve()
        s.conf_budget(budget)
        r = s.solve_limited()
        return r                        # None when the budget ran out


def least_dead(knots, order):
    rank = {v: i for i, v in enumerate(order)}
    key = [max(rank[v] for v in t) for t in knots]
    lo, hi = 3, len(order)
    while lo < hi:
        mid = (lo + hi) // 2
        if sat([t for t, k in zip(knots, key) if k < mid]):
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


def switch_chain(knots, rng, burn, gap, samples):
    T = [list(t) for t in knots]
    present = Counter(tuple(sorted(t)) for t in T)
    m = len(T)
    out = []
    total = burn + gap * samples
    for step in range(1, total + 1):
        i, j = rng.randrange(m), rng.randrange(m)
        if i != j:
            a, b = rng.randrange(3), rng.randrange(3)
            x, y = T[i][a], T[j][b]
            if x != y:
                ti = T[i][:a] + [y] + T[i][a + 1:]
                tj = T[j][:b] + [x] + T[j][b + 1:]
                if len(set(ti)) == 3 and len(set(tj)) == 3:
                    ki, kj = tuple(sorted(ti)), tuple(sorted(tj))
                    oi, oj = tuple(sorted(T[i])), tuple(sorted(T[j]))
                    if ki != kj and present[ki] == 0 and present[kj] == 0:
                        present[oi] -= 1
                        present[oj] -= 1
                        present[ki] += 1
                        present[kj] += 1
                        T[i], T[j] = ti, tj
        if step > burn and (step - burn) % gap == 0:
            out.append([tuple(sorted(t)) for t in T])
    return out


def repaired_start(knots, rng, max_swaps=200000):
    """the census's kind of start: stubs shuffled into triples, repaired by swapping one stub of a bad triple with a random one"""
    stubs = [v for t in knots for v in t]
    rng.shuffle(stubs)
    T = [stubs[i:i + 3] for i in range(0, len(stubs), 3)]
    for _ in range(max_swaps):
        cnt = Counter(tuple(sorted(t)) for t in T if len(set(t)) == 3)
        bad = [i for i, t in enumerate(T) if len(set(t)) < 3 or cnt[tuple(sorted(t))] > 1]
        if not bad:
            return [tuple(sorted(t)) for t in T]
        i = rng.choice(bad)
        j = rng.randrange(len(T))
        a, b = rng.randrange(3), rng.randrange(3)
        T[i][a], T[j][b] = T[j][b], T[i][a]
    return None


def uniform_pattern(n, m, rng):
    seen = set()
    m = min(m, n * (n - 1) * (n - 2) // 6)
    while len(seen) < m:
        seen.add(tuple(sorted(rng.sample(range(n), 3))))
    return list(seen)


def analyse(label, run, rec=None, resample_uniform=False, budget=None):
    t0 = time.time()
    knots, dead = grow(label, run)
    n = max(v for t in knots for v in t) + 1
    out = {"label": label, "run": run, "dead": dead, "knots": len(knots), "n": n}
    if rec is not None:
        out["knots and ending match"] = (len(knots), dead, n) == (rec["knots"], rec["dead"], rec["n"])
    if not dead:
        return out
    ks = least_dead(knots, list(range(n)))
    core = [t for t in knots if t[2] < ks]
    pc = peel(core)
    n2 = len({v for t in pc for v in t})
    deg = Counter(v for t in knots for v in t)
    kd = least_dead(knots, sorted(range(n), key=lambda v: (-deg[v], v)))
    out.update({"kstar": ks, "mstar": len(core), "floor": max(knots[-1]) + 1, "n2": n2, "m2": len(pc), "kstar_deg": kd})
    if rec is not None:
        out["core measures match"] = all(out[k] == rec[k] for k in ("kstar", "mstar", "floor", "n2", "m2", "kstar_deg"))
    m = len(core)
    rng = random.Random(run * 7919 + 1)
    pd = {}
    for start_name in ("core", "repaired"):
        start = core if start_name == "core" else repaired_start(core, rng)
        if start is None:
            pd[start_name] = None
            continue
        smp = switch_chain(start, rng, burn=20 * m, gap=5 * m, samples=20)
        res = [sat(s, budget) for s in smp]
        pd[start_name] = sum(r is False for r in res) / len(res) if all(r is not None for r in res) else None
    out["P_d switch chain (from the core, from a repaired start)"] = [pd["core"], pd["repaired"]]
    if resample_uniform:
        rr = random.Random(run * 104729 + 3)
        res = [sat(uniform_pattern(ks, m, rr), budget) for _ in range(20)]
        out["P_u"] = sum(r is False for r in res) / 20 if all(r is not None for r in res) else ["unknown in", sum(r is None for r in res)]
        res = [sat(uniform_pattern(n2, len(pc), rr), budget) for _ in range(20)]
        out["P_u2"] = sum(r is False for r in res) / 20 if all(r is not None for r in res) else ["unknown in", sum(r is None for r in res), "ended", sum(r is False for r in res)]
    out["seconds"] = round(time.time() - t0, 1)
    return out


def regen_job(rec):
    return analyse(rec["label"], rec["run"], rec)


def main():
    part = sys.argv[1]
    workers = int(sys.argv[2]) if len(sys.argv) > 2 else 3
    recs = [json.loads(l) for l in (ART / "runs.jsonl").read_text().splitlines()]
    if part == "missing":
        out = [analyse("Og0.3", r, None, resample_uniform=True, budget=2_000_000) for r in (54, 99)]
        (HERE / "result_missing.json").write_text(json.dumps(out, indent=1) + "\n")
        print(json.dumps(out, indent=1))
        return
    path = HERE / "result_regen.jsonl"
    done = set()
    if path.exists():
        done = {(json.loads(l)["label"], json.loads(l)["run"]) for l in path.read_text().splitlines()}
    todo = [r for r in recs if r["dead"] and (r["label"], r["run"]) not in done]
    todo.sort(key=lambda r: r.get("mstar", 0))
    t0 = time.time()
    with Pool(workers) as pool:
        for res in pool.imap_unordered(regen_job, todo):
            with open(path, "a") as fh:
                fh.write(json.dumps(res) + "\n")
            print(res["label"], res["run"], res.get("core measures match"), res.get("P_d switch chain (from the core, from a repaired start)"), res.get("seconds"),
                  round(time.time() - t0), "s", flush=True)


if __name__ == "__main__":
    main()
