"""The frozen stage-2 census of RANDOM-FATES-20261112-001C-E001 (contract.json beside this file): the law's distance along
newest-four growth, which never ends (RANDOM-FATES-20261112-001B, T4(b)).

Bases: newest-four growth (fates.proc_band with w = 4) at q in {0, 0.1, 0.3, 0.5, 0.7, 0.9}, ten bases each, grown until the move
that would bring the 801st distinction (so 800 distinctions, 0 to 799). Per base, eight nested sequences: i uniform in [40, 200],
and for each g in {4, 8, 16, 32, 64, 128, 256, 512}, j = i + g + r with r uniform in {0, 1, 2, 3}. For each pair: steps apart
d, the least bond L (bonddp.least_bond, margin 8, no size cap, blow-up at 20,000 states), its members, and the number of
incompletely closed windows between them (positions m in [i + 3, j] whose four distinctions m - 3 .. m do not carry all four knots).
Rechecks: every undefined pair at g >= 64 (up to 40 per q) and 40 defined pairs per q again with margin 32; each defined pair
with a bond of at most 10 members verified independently by a SAT solver. Controls: the complete pattern (L = 2 when g = 0 mod 4,
else 3), the chain {2k, 2k+1, 2k+2} (L = steps + 2), and the programme against brute force on 300 random small newest-four patterns.

Run from the repository root:
    .venv/bin/python -B experiments/RANDOM-FATES-20261112-001C/RANDOM-FATES-20261112-001C-E001_newest_four_count/census.py [--workers 6]
    .venv/bin/python -B experiments/RANDOM-FATES-20261112-001C/RANDOM-FATES-20261112-001C-E001_newest_four_count/census.py --summary
Output: artifacts/RANDOM-FATES-20261112-001C/RANDOM-FATES-20261112-001C-E001_newest_four_count/{bases.jsonl, controls.json,
summary.json}.
"""

from __future__ import annotations

import hashlib
import itertools
import json
import os
import random
import sys
import time
from multiprocessing import Pool

import numpy as np
from pysat.solvers import Solver

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "experiments", "RANDOM-FATES-20261112-001A", "RANDOM-FATES-20261112-001A-E001_fates_census"))
import bonddp as B  # noqa: E402
import fates as F  # noqa: E402

OUT = os.path.join(ROOT, "artifacts", "RANDOM-FATES-20261112-001C", "RANDOM-FATES-20261112-001C-E001_newest_four_count")
QS = (0.0, 0.1, 0.3, 0.5, 0.7, 0.9)
BASES = 10
NMAX = 800
SEQS = 8
GAPS = (4, 8, 16, 32, 64, 128, 256, 512)
MARGIN, MARGIN2 = 8, 32
RECHECK = 40
VERIFY_MAX = 10


def seed_of(*parts):
    return int(hashlib.sha256(":".join(map(str, parts)).encode()).hexdigest()[:12], 16)


def grow_to(q, nmax, rng):
    gen = F.proc_band(4, q, rng)
    knots = []
    while True:
        t = next(gen)
        if t is None:
            continue
        if max(t) >= nmax:
            return knots
        knots.append(t)


def open_windows(kset, i, j):
    c = 0
    for m in range(i + 3, j + 1):
        if not all(t in kset for t in itertools.combinations(range(m - 3, m + 1), 3)):
            c += 1
    return c


def verify_bond(knots, S):
    """Independent check by SAT: S constrained and every S minus one member free."""
    with Solver(name="minisat22", bootstrap_with=[c for t in knots for c in F.cls(t)]) as s:
        def ext(vs, bits):
            return s.solve(assumptions=[v + 1 if b else -(v + 1) for v, b in zip(vs, bits)])
        def free(vs):
            return all(ext(vs, (0,) + r) for r in itertools.product((0, 1), repeat=len(vs) - 1))
        return (not free(S)) and all(free([x for x in S if x != y]) for y in S)


def base_task(spec):
    q, b = spec
    t0 = time.time()
    rng = random.Random(seed_of("C", q, b, "grow"))
    knots = grow_to(q, NMAX, rng)
    kset = set(knots)
    nbr = F.adjacency(NMAX, knots)
    step = B.make_step(NMAX, knots)
    prng = random.Random(seed_of("C", q, b, "pairs"))
    pairs = []
    for sidx in range(SEQS):
        i = prng.randrange(40, 201)
        dist = F.steps_from(nbr, i)
        for g in GAPS:
            j = i + g + prng.randrange(4)
            L, S, status = B.least_bond(NMAX, knots, i, j, margin=MARGIN, step=step)
            rec = {"seq": sidx, "i": i, "j": j, "g": g, "gap": j - i, "d": dist.get(j), "L": L, "status": status,
                   "members": S, "open": open_windows(kset, i, j)}
            if status == "ok" and L <= VERIFY_MAX:
                rec["verified"] = verify_bond(knots, S)
            pairs.append(rec)
    # rechecks with a wider margin
    und = [p for p in pairs if p["status"] == "none" and p["g"] >= 64][:RECHECK // BASES + 1]
    dfn = [p for p in pairs if p["status"] == "ok"]
    prng.shuffle(dfn)
    for p in und + dfn[:RECHECK // BASES]:
        L2, S2, st2 = B.least_bond(NMAX, knots, p["i"], p["j"], margin=MARGIN2, step=step)
        p["recheck32"] = {"L": L2, "status": st2}
    return {"q": q, "base": b, "knots": len(knots), "pairs": pairs, "seconds": round(time.time() - t0, 1)}


def controls():
    out = {}
    N = 80
    comp = [t for t in itertools.combinations(range(N), 3) if t[2] - t[0] <= 3]
    out["complete"] = [B.least_bond(N, comp, 30, 30 + g, margin=MARGIN)[0] for g in range(1, 17)]
    out["complete_ok"] = out["complete"] == [2 if g % 4 == 0 else 3 for g in range(1, 17)]
    chain = [(2 * k, 2 * k + 1, 2 * k + 2) for k in range(39)]
    nb = F.adjacency(N, chain)
    res = [(B.least_bond(N, chain, 10, 10 + g, margin=MARGIN)[0], F.steps_from(nb, 10).get(10 + g)) for g in range(1, 31)]
    out["chain"] = res
    out["chain_ok"] = all(L == d + 2 for L, d in res)
    # brute force on small random newest-four patterns
    rng = random.Random(seed_of("C", "brute"))
    checked = bad = 0
    examples = []
    while checked < 300:
        q = rng.choice((0.0, 0.2, 0.4, 0.6, 0.8))
        knots, _ = F.grow(F.proc_band(4, q, random.Random(rng.randrange(10 ** 9))), rng.randrange(6, 22))
        n = max(v for t in knots for v in t) + 1
        if not 5 <= n <= 13:
            continue
        st = np.arange(1 << n, dtype=np.int64)
        ok = np.ones(len(st), bool)
        for t in knots:
            tot = sum((st >> v) & 1 for v in t)
            ok &= (tot != 0) & (tot != 3)
        st = st[ok]

        def nc(S):
            code = np.zeros(len(st), dtype=np.int64)
            for k, v in enumerate(S):
                code |= ((st >> v) & 1) << k
            return len(np.unique(code))

        def bond(S):
            return nc(S) < (1 << len(S)) and all(nc([x for x in S if x != y]) == 1 << (len(S) - 1) for y in S)

        i, j = sorted(rng.sample(range(n), 2))
        rest = [w for w in range(n) if w not in (i, j)]
        brute = None
        for size in range(2, n + 1):
            if any(bond([i, j, *ex]) for ex in itertools.combinations(rest, size - 2)):
                brute = size
                break
        dp = B.least_bond(n, knots, i, j, margin=n)[0]
        checked += 1
        if dp != brute:
            bad += 1
            examples.append([n, knots, i, j, dp, brute])
    out["brute"] = {"checked": checked, "mismatches": bad, "examples": examples[:5]}
    return out


def run(workers):
    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, "bases.jsonl")
    done = set()
    if os.path.exists(path):
        for line in open(path):
            r = json.loads(line)
            done.add((r["q"], r["base"]))
    specs = [(q, b) for q in QS for b in range(BASES) if (q, b) not in done]
    t0 = time.time()
    with Pool(workers) as pool, open(path, "a") as f:
        for rec in pool.imap_unordered(base_task, specs):
            f.write(json.dumps(rec) + "\n")
            f.flush()
            print(f"q={rec['q']} base={rec['base']} {rec['seconds']} s", flush=True)
    with open(os.path.join(OUT, "controls.json"), "w") as f:
        json.dump(controls(), f, indent=1)
    print(f"done in {time.time() - t0:.0f} s", flush=True)


def spearman(x, y):
    if len(x) < 3:
        return None
    rx = np.argsort(np.argsort(x)).astype(float)
    ry = np.argsort(np.argsort(y)).astype(float)
    if rx.std() == 0 or ry.std() == 0:
        return 0.0
    return float(np.corrcoef(rx, ry)[0, 1])


def summarize():
    bases = [json.loads(l) for l in open(os.path.join(OUT, "bases.jsonl"))]
    ctrl = json.load(open(os.path.join(OUT, "controls.json")))
    S = {"cells": {}, "controls": {k: ctrl[k] for k in ("complete_ok", "chain_ok", "brute")}}
    for q in QS:
        bs = [b for b in bases if b["q"] == q]
        for g in GAPS:
            ps = [p for b in bs for p in b["pairs"] if p["g"] == g]
            dfn = [p for p in ps if p["status"] == "ok"]
            S["cells"][f"q{q} g{g}"] = {
                "pairs": len(ps), "defined_share": len(dfn) / len(ps) if ps else None,
                "blowups": sum(p["status"] == "blowup" for p in ps),
                "L_median": float(np.median([p["L"] for p in dfn])) if dfn else None,
                "d_median": float(np.median([p["d"] for p in ps if p["d"] is not None])),
                "excess_median": float(np.median([p["L"] - (p["d"] + 2) for p in dfn])) if dfn else None,
                "ties": sum(1 for p in dfn if p["L"] == 2),
                "verified": [sum(1 for p in dfn if p.get("verified") is True), sum(1 for p in dfn if "verified" in p)]}
    rech = [p for b in bases for p in b["pairs"] if "recheck32" in p]
    S["recheck32"] = {"undefined_rechecked": sum(1 for p in rech if p["status"] == "none"),
                      "undefined_now_defined": sum(1 for p in rech if p["status"] == "none" and p["recheck32"]["status"] == "ok"),
                      "defined_rechecked": sum(1 for p in rech if p["status"] == "ok"),
                      "defined_changed": sum(1 for p in rech if p["status"] == "ok" and p["recheck32"]["L"] != p["L"])}
    S["verified_all"] = all(p.get("verified", True) for b in bases for p in b["pairs"])

    def base_med(b, g):
        ls = [p["L"] for p in b["pairs"] if p["g"] == g and p["status"] == "ok"]
        return float(np.median(ls)) if ls else None

    def g_half(b):
        for g in GAPS:
            ps = [p for p in b["pairs"] if p["g"] == g]
            if sum(p["status"] == "ok" for p in ps) < len(ps) / 2:
                return g
        return float("inf")

    P = {}
    gh = {q: float(np.median([g_half(b) for b in bases if b["q"] == q])) for q in QS}
    P["Q1"] = {"g_half_median": gh, "holds": gh[0.1] < gh[0.3] < gh[0.5] and gh[0.1] <= 128}
    ratios = []
    for b in bases:
        if b["q"] != 0.5:
            continue
        ok = all(sum(p["status"] == "ok" for p in b["pairs"] if p["g"] == g) >= 6 for g in (32, 64, 128))
        if ok:
            m32, m64, m128 = base_med(b, 32), base_med(b, 64), base_med(b, 128)
            ratios.append((m128 - m64) / (m64 - m32) if m64 != m32 else float("inf"))
    P["Q2"] = {"ratios": ratios, "eligible_bases": len(ratios),
               "holds": len(ratios) >= 7 and sum(1.5 <= r <= 2.7 for r in ratios) >= 7}
    meds = {}
    for q in (0.3, 0.5, 0.7, 0.9):
        bm = [base_med(b, 64) for b in bases if b["q"] == q
              and sum(p["status"] == "ok" for p in b["pairs"] if p["g"] == 64) >= 4]
        meds[q] = float(np.median(bm)) if bm else None
    P["Q3"] = {"median_of_base_medians_g64": meds,
               "holds": all(meds[q] is not None for q in meds) and meds[0.3] > meds[0.5] > meds[0.7] > meds[0.9]}
    rho = {}
    for q in (0.7, 0.9):
        ps = [p for b in bases if b["q"] == q for p in b["pairs"] if p["g"] == 256 and p["status"] == "ok"]
        rho[q] = spearman([p["L"] for p in ps], [p["open"] for p in ps]) if len(ps) >= 20 else None
    P["Q4a"] = {"spearman_L_open_g256": rho, "holds": all(r is not None and r > 0.5 for r in rho.values())}
    grow = []
    for b in bases:
        if b["q"] == 0.9:
            a, c = base_med(b, 128), base_med(b, 512)
            grow.append(None if a is None or c is None else c - a)
    P["Q4b"] = {"L512_minus_L128": grow, "holds": sum(1 for x in grow if x is not None and x >= 3) >= 8}
    P["Q5_ties_g32plus"] = {f"q{q}": sum(1 for b in bases if b["q"] == q for p in b["pairs"]
                                         if p["g"] >= 32 and p["status"] == "ok" and p["L"] == 2) for q in QS}
    S["predictions"] = P
    with open(os.path.join(OUT, "summary.json"), "w") as f:
        json.dump(S, f, indent=1, sort_keys=True, default=str)
    print(json.dumps(P, indent=1, sort_keys=True, default=str))


if __name__ == "__main__":
    if "--summary" in sys.argv:
        summarize()
    else:
        run(int(sys.argv[sys.argv.index("--workers") + 1]) if "--workers" in sys.argv else 6)
