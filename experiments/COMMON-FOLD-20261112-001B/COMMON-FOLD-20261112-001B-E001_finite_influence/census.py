"""The frozen exploratory census of COMMON-FOLD-20261112-001B-E001 (contract.json beside this file): global influence on random
finite samples.

Samples: uniform growth U(n) (a uniform new knot on n distinctions per move, grown until the first knot after which no state is
allowed) for n = 100, 200, 400, 20 runs each, and the tree control T (300 moves), 20 runs, from RANDOM-FATES-20261112-001A-E001's
frozen library fates.py (sha256 72d3571ed66dddaa6c517b3ce29ce14ae72c008c025669e2ef071b77b73eba35), with seeds 50000 + run (growth)
and 60000 + run (reading), disjoint from that census's. Stages: the base after half and three quarters of the knots of its last
base, and the last base itself (for T, the base at 300 moves and at half).

Readings on each base, for 20 co-knotted pairs and 20 knots drawn uniformly, and every allowed pattern on them up to complement:
  - forced set: every distinction whose value is the same in every allowed state with that pattern (exact, by SAT);
  - beyond ties: the forced distinctions not forced by any single member of the set with its value (a member's own tie class);
  - by propagation: forced by repeating "two equal values of a knot force the third to the other value" (unit propagation of NAE's
    clauses), and the rest, forced only by search;
  - shell profile: the fraction forced among the distinctions at each number of steps from the set.
Per base: means and maxima over the sets of the forced fraction (of all distinctions), the fraction beyond ties, the fraction by
propagation, and the profile.

    .venv/bin/python -B experiments/COMMON-FOLD-20261112-001B/COMMON-FOLD-20261112-001B-E001_finite_influence/census.py [--workers 8]
Output: artifacts/COMMON-FOLD-20261112-001B/COMMON-FOLD-20261112-001B-E001_finite_influence/census.json and log.txt.
"""
from __future__ import annotations

import importlib.util
import itertools
import json
import os
import random
import sys
import time
from collections import deque
from multiprocessing import Pool

from pysat.solvers import Minisat22, Solver

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
OUT = os.path.join(ROOT, "artifacts", "COMMON-FOLD-20261112-001B", "COMMON-FOLD-20261112-001B-E001_finite_influence")
FATES = os.path.join(ROOT, "experiments", "RANDOM-FATES-20261112-001A", "RANDOM-FATES-20261112-001A-E001_fates_census", "fates.py")
FATES_SHA = "72d3571ed66dddaa6c517b3ce29ce14ae72c008c025669e2ef071b77b73eba35"
NS, RUNS, NSETS = (100, 200, 400), 20, 20
spec = importlib.util.spec_from_file_location("fates", FATES)
F = importlib.util.module_from_spec(spec)
spec.loader.exec_module(F)


def lit(v, b):
    return (v + 1) if b else -(v + 1)


def backbone(s, n, assum):
    """Distinctions 0 .. n-1 (not assumed) with one value in every state under the assumptions; None if none allowed."""
    if not s.solve(assumptions=assum):
        return None
    val = {abs(x) - 1: x > 0 for x in s.get_model() if abs(x) <= n}
    cand = set(range(n)) - {abs(a) - 1 for a in assum}
    out = {}
    while cand:
        v = cand.pop()
        if s.solve(assumptions=assum + [lit(v, not val[v])]):
            v2 = {abs(x) - 1: x > 0 for x in s.get_model() if abs(x) <= n}
            cand = {u for u in cand if v2[u] == val[u]}
        else:
            out[v] = val[v]
    return out


def propagated(p, assum):
    ok, lits = p.propagate(assumptions=assum)
    return {abs(x) - 1 for x in lits} if ok else None


def bfs(nbr, src):
    d = {x: 0 for x in src}
    q = deque(src)
    while q:
        x = q.popleft()
        for y in nbr[x]:
            if y not in d:
                d[y] = d[x] + 1
                q.append(y)
    return d


def read(knots, rng):
    n = max(v for t in knots for v in t) + 1
    nbr = F.adjacency(n, knots)
    cl = [c for t in knots for c in F.cls(t)]
    s = Solver(name="cadical153", bootstrap_with=cl)
    p = Minisat22(bootstrap_with=cl)
    tie = {}

    def tie_of(v, b):
        if (v, b) not in tie:
            f = backbone(s, n, [lit(v, b)])
            tie[(v, b)] = set(f) if f is not None else set()
        return tie[(v, b)]
    pairs = sorted({q for t in knots for q in itertools.combinations(t, 2)})
    out = {"n": n, "m": len(knots)}
    for label, sets, pats in (("pair", rng.sample(pairs, min(NSETS, len(pairs))), [(0, 0), (0, 1)]),
                              ("knot", rng.sample(knots, min(NSETS, len(knots))), [(0, 0, 1), (0, 1, 0), (1, 0, 0)])):
        recs = []
        for S in sets:
            S = list(S)
            d = bfs(nbr, S)
            shells = {}
            for u, k in d.items():
                shells.setdefault(k, []).append(u)
            best = None
            for pat in pats:
                assum = [lit(v, b) for v, b in zip(S, pat)]
                f = backbone(s, n, assum)
                if f is None:
                    continue
                fs = set(f)
                ties = set().union(*(tie_of(v, b) for v, b in zip(S, pat))) - set(S)
                beyond = fs - ties
                up = propagated(p, assum)
                up = (up - set(S)) if up is not None else set()
                rec = {"forced": len(fs) / n, "beyond ties": len(beyond) / n, "by propagation": len(fs & up) / n,
                       "reach": max((d.get(u, -1) for u in fs), default=0),
                       "profile": {k: round(sum(u in fs for u in us) / len(us), 4) for k, us in sorted(shells.items()) if k > 0}}
                if best is None or rec["forced"] > best["forced"]:
                    best = rec
            if best is not None:
                recs.append(best)
        prof = {}
        for r_ in recs:
            for k, v in r_["profile"].items():
                prof.setdefault(k, []).append(v)
        out[label] = {"sets": len(recs),
                      **{f"{q} mean": round(sum(r_[q] for r_ in recs) / len(recs), 4) for q in ("forced", "beyond ties", "by propagation", "reach")},
                      **{f"{q} max": round(max(r_[q] for r_ in recs), 4) for q in ("forced", "beyond ties", "by propagation", "reach")},
                      "profile mean": {k: round(sum(v) / len(v), 4) for k, v in sorted(prof.items())}}
    s.delete()
    p.delete()
    return out


def job(item):
    proc, n, run = item
    rng = random.Random(50000 + run)
    if proc == "U":
        knots, dead = F.grow(F.proc_uniform(n, rng), 50 * n)
        last = knots[:-1] if dead else knots
        stages = {"half": last[: len(last) // 2], "three quarters": last[: (3 * len(last)) // 4], "last base": last}
    else:
        knots, dead = F.grow(F.proc_tree(rng), 300)
        last = knots
        stages = {"half": last[: len(last) // 2], "horizon": last}
    res = {"process": proc, "n": n, "run": run, "ended": dead, "knots of the last base": len(last)}
    for st, kn in stages.items():
        res[st] = read(kn, random.Random(60000 + run))
    return res


def log(*a):
    msg = " ".join(str(x) for x in a)
    print(msg, flush=True)
    with open(os.path.join(OUT, "log.txt"), "a") as f:
        f.write(msg + "\n")


def main():
    import hashlib
    assert hashlib.sha256(open(FATES, "rb").read()).hexdigest() == FATES_SHA, "fates.py changed"
    workers = int(sys.argv[sys.argv.index("--workers") + 1]) if "--workers" in sys.argv else 8
    os.makedirs(OUT, exist_ok=True)
    t0 = time.time()
    items = [("T", 0, r) for r in range(RUNS)] + [("U", n, r) for n in NS for r in range(RUNS)]
    rows = []
    with Pool(workers) as pool:
        for row in pool.imap_unordered(job, items, chunksize=1):
            rows.append(row)
            log(row["process"], row["n"], row["run"], round(time.time() - t0, 1), "s")
    summ = {}
    for proc, n in [("T", 0)] + [("U", n) for n in NS]:
        rr = [r for r in rows if r["process"] == proc and r["n"] == n]
        for st in (("half", "horizon") if proc == "T" else ("half", "three quarters", "last base")):
            for lab in ("pair", "knot"):
                vals = [r[st][lab] for r in rr]
                summ[f"{proc}{n or ''} {st} {lab}"] = {q: round(sum(v[q] for v in vals) / len(vals), 4) for q in vals[0] if q.endswith("mean")}
    t_beyond_knot = max(r[st]["knot"]["forced max"] for r in rows if r["process"] == "T" for st in ("half", "horizon"))
    t_pair = max(r[st]["pair"]["reach max"] for r in rows if r["process"] == "T" for st in ("half", "horizon"))
    summ["checks"] = {"T: a knot's pattern forces nothing (largest forced fraction)": t_beyond_knot, "T: largest pair reach": t_pair}
    json.dump({"rows": rows, "summary": summ}, open(os.path.join(OUT, "census.json"), "w"), indent=1)
    log("summary", json.dumps(summ)[:4000])
    log("done", round(time.time() - t0, 1), "s")


if __name__ == "__main__":
    main()
