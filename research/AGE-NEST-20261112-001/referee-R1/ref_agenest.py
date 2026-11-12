#!/usr/bin/env python3
"""Referee AGE-NEST-R1, with the referee's own code (OLD-CORE-R1's ref_oldcore.py for the growths and the switch chain; no import of
either census.py or fates.py):
  fairness  the five degree sequences of the census: every simple pattern enumerated (the referee's own enumeration), the exact
            transition matrices of SW and R2 (vertex order as age) rebuilt, checked symmetric, and each chain's components counted
            against the classes it must preserve (R2: the multiset of each knot's youngest member);
  ladder    every non-pilot ending of X(0.25), X(0.3), X(0.35) (the census's twelve pilot endings excluded, as frozen): the core
            regenerated, and the four rungs resampled with the referee's own code, 20 each: SW and R2 as 20 independent chains of
            20 m steps from the core (the census's scheme), R2p (each knot's youngest kept, the other two uniform among older
            distinctions, simple), FULL (the growth's schedule kept: a birth knot keeps its new distinction and redraws its pair
            among older ones; a closing redraws three among the core's distinctions existing at its time); the share that allow no
            state; the largest density of knots among the oldest j distinctions, j >= 20 (is some early part past 2.1?);
  mixing    for 40 cores (the smallest 20 of X(0.3) and of X(0.35) with m >= 150): SW and R2 also with 100 m steps per chain, and as 20
            samples 20 m apart after a burn-in of 200 m (one long chain), against the census's scheme.

    python3 -B ref_agenest.py fairness|ladder|mixing [workers]"""
import itertools
import json
import random
import sys
import time
from collections import Counter
from multiprocessing import Pool
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "research" / "OLD-CORE-20261112-001" / "referee-R1"))
import ref_oldcore as O  # noqa: E402

OC_RUNS = ROOT / "artifacts" / "OLD-CORE-20261112-001A" / "OLD-CORE-20261112-001A-E001_old_core" / "runs.jsonl"
AN_RUNS = ROOT / "artifacts" / "AGE-NEST-20261112-001A" / "AGE-NEST-20261112-001A-E001_resample_ladder" / "runs.jsonl"
PILOT = {("X0.3", r) for r in (0, 1, 4, 10, 11, 12)} | {("X0.35", r) for r in range(6)}
FAIR_SEQS = [[3, 3, 3, 3, 3, 3], [4, 3, 3, 2, 2, 1], [5, 4, 3, 2, 2, 1, 1], [6, 3, 3, 2, 2, 1, 1], [4, 4, 3, 3, 2, 2, 2, 1]]


# ---------------------------------------------------------------- the chains (the referee's)

def step(T, present, rng, keep_youngest):
    m = len(T)
    i, j = rng.randrange(m), rng.randrange(m)
    if i == j:
        return
    a, b = T[i], T[j]                      # sorted triples
    if keep_youngest:
        u, v = a[rng.randrange(2)], b[rng.randrange(2)]
        if not (v < a[2] and u < b[2]):
            return
    else:
        u, v = a[rng.randrange(3)], b[rng.randrange(3)]
    if u in b or v in a:
        return
    na = tuple(sorted([x for x in a if x != u] + [v]))
    nb = tuple(sorted([x for x in b if x != v] + [u]))
    if present.get(na) or present.get(nb):
        return
    present[a] -= 1
    present[b] -= 1
    present[na] = present.get(na, 0) + 1
    present[nb] = present.get(nb, 0) + 1
    T[i], T[j] = na, nb


def run_chain(core, rng, steps, keep_youngest):
    T = [tuple(sorted(t)) for t in core]
    present = Counter(T)
    for _ in range(steps):
        step(T, present, rng, keep_youngest)
    return T


def long_chain(core, rng, burn, gap, samples, keep_youngest):
    T = [tuple(sorted(t)) for t in core]
    present = Counter(T)
    out = []
    for s in range(burn + gap * samples):
        step(T, present, rng, keep_youngest)
        if s >= burn and (s - burn + 1) % gap == 0:
            out.append(list(T))
    return out


def r2p(core, rng):
    out = set()
    for t in sorted(core, key=lambda t: t[2]):
        y = t[2]
        for _ in range(1000):
            a, b = rng.sample(range(y), 2)
            nt = tuple(sorted((a, b, y)))
            if nt not in out:
                break
        out.add(nt)
    return list(out)


def full(K, ks, rng):
    seen = set()
    sched = []
    for t in K:
        new = [v for v in t if v not in seen]
        if t[2] < ks:
            sched.append(("birth", t[2]) if new else ("closing", max(seen) + 1))
        seen |= set(t)
    out = set()
    for kind, x in sched:
        for _ in range(1000):
            if kind == "birth":
                nt = (0, 1, 2) if x < 2 else tuple(sorted(rng.sample(range(x), 2) + [x]))
            else:
                nt = tuple(sorted(rng.sample(range(min(ks, x)), 3)))
            if nt not in out:
                break
        out.add(nt)
    return list(out)


def prefix_density(core, jmin=20):
    ys = sorted(t[2] for t in core)
    best = 0.0
    c = 0
    for j in range(1, max(ys) + 2):
        while c < len(ys) and ys[c] < j:
            c += 1
        if j >= jmin:
            best = max(best, c / j)
    return best


def unsat_share(samples):
    return sum(not O.sat(s) for s in samples) / len(samples)


def core_of(label, run, ks):
    knots, dead = O.grow(label, run)
    assert dead
    return knots, [t for t in knots if t[2] < ks]


def ladder_job(rec):
    t0 = time.time()
    K, core = core_of(rec["label"], rec["run"], rec["kstar"])
    m = len(core)
    rng = random.Random(rec["run"] * 31 + 17)
    out = {"label": rec["label"], "run": rec["run"], "kstar": rec["kstar"], "m": m, "core unsat": not O.sat(core),
           "largest density among the oldest j (j >= 20)": prefix_density(core)}
    out["P_SW"] = unsat_share([run_chain(core, rng, 20 * m, False) for _ in range(20)])
    out["P_R2"] = unsat_share([run_chain(core, rng, 20 * m, True) for _ in range(20)])
    out["P_R2p"] = unsat_share([r2p(core, rng) for _ in range(20)])
    out["P_FULL"] = unsat_share([full(K, rec["kstar"], rng) for _ in range(20)])
    # R2 keeps every prefix count, by construction: check on one resample
    smp = run_chain(core, rng, 20 * m, True)
    out["R2 keeps the youngest multiset and the degrees"] = (sorted(t[2] for t in smp) == sorted(t[2] for t in core)
                                                              and Counter(v for t in smp for v in t) == Counter(v for t in core for v in t))
    out["seconds"] = round(time.time() - t0, 1)
    return out


def mixing_job(rec):
    K, core = core_of(rec["label"], rec["run"], rec["kstar"])
    m = len(core)
    rng = random.Random(rec["run"] * 37 + 5)
    out = {"label": rec["label"], "run": rec["run"], "m": m}
    for name, keep in (("SW", False), ("R2", True)):
        out[f"{name} 20 m"] = unsat_share([run_chain(core, rng, 20 * m, keep) for _ in range(20)])
        out[f"{name} 100 m"] = unsat_share([run_chain(core, rng, 100 * m, keep) for _ in range(20)])
        out[f"{name} long chain"] = unsat_share(long_chain(core, rng, 200 * m, 20 * m, 20, keep))
    return out


# ---------------------------------------------------------------- fairness (exact)

def enumerate_simple(deg):
    n, m = len(deg), sum(deg) // 3
    triples = list(itertools.combinations(range(n), 3))
    out = []

    def rec(start, chosen, left):
        if len(chosen) == m:
            if not any(left):
                out.append(tuple(chosen))
            return
        for i in range(start, len(triples)):
            t = triples[i]
            if all(left[v] > 0 for v in t):
                for v in t:
                    left[v] -= 1
                rec(i + 1, chosen + [t], left)
                for v in t:
                    left[v] += 1
    rec(0, [], list(deg))
    return out


def moves(state, keep):
    E = list(state)
    m = len(E)
    S = set(E)
    res = Counter()
    for i in range(m):
        for j in range(m):
            if i == j:
                res[state] += 1 / m ** 2
                continue
            a, b = E[i], E[j]
            ua, vb = (a[:2], b[:2]) if keep else (a, b)
            for u in ua:
                for v in vb:
                    p = 1 / (m * m * len(ua) * len(vb))
                    ok = u not in b and v not in a and (not keep or (v < a[2] and u < b[2]))
                    if ok:
                        na = tuple(sorted([x for x in a if x != u] + [v]))
                        nb = tuple(sorted([x for x in b if x != v] + [u]))
                        ok = na not in S and nb not in S
                    if ok:
                        new = list(E)
                        new[i], new[j] = na, nb
                        res[tuple(sorted(new))] += p
                    else:
                        res[state] += p
    return res


def fairness():
    out = []
    for deg in FAIR_SEQS:
        pats = sorted(set(tuple(sorted(p)) for p in enumerate_simple(deg)))
        idx = {p: i for i, p in enumerate(pats)}
        for keep in (False, True):
            T = {}
            for p in pats:
                for q, pr in moves(p, keep).items():
                    T[idx[p], idx[q]] = T.get((idx[p], idx[q]), 0) + pr
            sym = all(abs(T.get((j, i), 0) - v) < 1e-12 for (i, j), v in T.items())
            rows_sum = Counter()
            for (i, j), v in T.items():
                rows_sum[i] += v
            stochastic = all(abs(rows_sum[i] - 1) < 1e-9 for i in range(len(pats)))
            adj = {i: set() for i in range(len(pats))}
            for (i, j), v in T.items():
                if v > 0 and i != j:
                    adj[i].add(j)
            seen, comps = set(), []
            for s in range(len(pats)):
                if s in seen:
                    continue
                stack, comp = [s], set()
                while stack:
                    x = stack.pop()
                    if x in comp:
                        continue
                    comp.add(x)
                    stack.extend(adj[x] - comp)
                seen |= comp
                comps.append(comp)
            if keep:
                sig = lambda p: tuple(sorted(t[2] for t in p))
                ok = all(len({sig(pats[i]) for i in c}) == 1 for c in comps) and len(comps) == len({sig(p) for p in pats})
            else:
                ok = len(comps) == 1
            out.append({"degrees": deg, "chain": "R2" if keep else "SW", "patterns": len(pats), "symmetric": sym, "stochastic": stochastic,
                        "components": len(comps), "each preserved class one component": ok})
    return out


def main():
    part = sys.argv[1]
    workers = int(sys.argv[2]) if len(sys.argv) > 2 else 3
    if part == "fairness":
        out = fairness()
        (HERE / "result_fairness.json").write_text(json.dumps(out, indent=1) + "\n")
        print(json.dumps(out, indent=1))
        return
    oc = [json.loads(l) for l in OC_RUNS.read_text().splitlines()]
    recs = [r for r in oc if r["label"] in ("X0.25", "X0.3", "X0.35") and r["dead"] and (r["label"], r["run"]) not in PILOT]
    if part == "ladder":
        path = HERE / "result_ladder.jsonl"
        done = set()
        if path.exists():
            done = {(json.loads(l)["label"], json.loads(l)["run"]) for l in path.read_text().splitlines()}
        todo = sorted([r for r in recs if (r["label"], r["run"]) not in done], key=lambda r: r["mstar"])
        with Pool(workers) as pool:
            for res in pool.imap_unordered(ladder_job, todo):
                with open(path, "a") as fh:
                    fh.write(json.dumps(res) + "\n")
                print(res["label"], res["run"], res["m"], res["P_SW"], res["P_R2"], res["P_R2p"], res["P_FULL"], res["seconds"], flush=True)
    else:
        sel = []
        for lab in ("X0.3", "X0.35"):
            sel += sorted([r for r in recs if r["label"] == lab and r["mstar"] >= 150], key=lambda r: r["mstar"])[:20]
        with Pool(workers) as pool:
            res = pool.map(mixing_job, sel, chunksize=1)
        (HERE / "result_mixing.json").write_text(json.dumps(res, indent=1) + "\n")
        print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
