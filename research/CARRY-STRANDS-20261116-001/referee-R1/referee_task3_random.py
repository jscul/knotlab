"""Referee R1, task 3: random atom patterns at the jump (fresh code only).

m = 3n atoms, each an ordered triple of distinct distinctions; held = the
first k* of a uniform order, k* the least k with |closure| >= n/2.

Two sample sets:
  study  the study's own instances, rebuilt by this file from the sampling
         protocol read in the study's job.py and atoms.py (seed = first 8
         bytes, little-endian, of sha256("CS:rand:<n>:<s>"); draws a, then
         b among != a, then c among != a, b; then a permutation), so that each
         sample can be compared with the study's results.jsonl one by one;
  fresh  new instances with the referee's own sampler and seeds.
Readings per sample: k*, sigma_max, R, P1/T1, P2/T2 spend, P2/T2 keep, the
keep-gain fractions (all, before and after the narrowest forcing-law phase,
as operationalized in the study's job.py: narrowest = first argmin of the
phase sizes over phases 1..P1-2, only when P1 >= 4), T2spend / T1.  Also
Theorem 1 (spend-only phase = ceil(sigma / 2)), Theorem 2 (T >= sigma_max,
distance >= 2^sigma_F - 1) on every sample, and the spend-only DP against the
BFS (P and L).

usage: referee_task3_random.py N [N ...] [--fresh-only] [--samples=K] [--start=S0]
"""

import hashlib
import json
import math
import os
import sys
import time
from multiprocessing import Pool

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import referee_carry as R  # noqa: E402


def study_instance(n, s):
    seed = int.from_bytes(hashlib.sha256(f"CS:rand:{n}:{s}".encode()).digest()[:8], "little")
    rng = np.random.default_rng(seed)
    m = int(round(3.0 * n))
    a = rng.integers(0, n, m)
    b = rng.integers(0, n - 1, m)
    b = b + (b >= a)
    lo, hi = np.minimum(a, b), np.maximum(a, b)
    c = rng.integers(0, n - 2, m)
    c = c + (c >= lo)
    c = c + (c >= hi)
    order = rng.permutation(n)
    atoms = [(int(x), int(y), int(z)) for x, y, z in zip(a, b, c)]
    assert all(len({x, y, z}) == 3 for x, y, z in atoms)
    return atoms, order.tolist()


def fresh_instance(n, s):
    seed = int.from_bytes(hashlib.sha256(f"REFEREE-R1:CARRY:rand:{n}:{s}".encode()).digest()[:8], "big")
    rng = np.random.default_rng(seed)
    A = R.RC.random_atoms(n, 3 * n, rng)
    order = rng.permutation(n)
    return [tuple(int(x) for x in row) for row in A], order.tolist()


def measure(args):
    kind, n, s = args
    t0 = time.time()
    atoms, order = (study_instance if kind == "study" else fresh_instance)(n, s)
    k = R.k_star(n, atoms, order)
    H = set(order[:k])
    sig = R.sigma(n, atoms, H)
    fin = [v for v in range(n) if sig[v] < R.INF]
    newly = [v for v in fin if v not in H]
    out = {"kind": kind, "n": n, "s": s, "k_star": k, "forced": len(fin),
           "sigma_max": max(sig[v] for v in fin), "R": R.native_R(n, atoms, H), "checks": []}
    runs = {}
    for w, law in ((1, "spend"), (2, "spend"), (2, "keep")):
        r = R.run_law(n, atoms, H, w, law, with_sigma_F=(law == "spend"))
        assert r["forced"] == set(fin)
        runs[(w, law)] = r
        key = f"w{w}{'k' if law == 'keep' else ''}"
        out[key] = {"P": r["P"], "T": r["T"], "L": r["L"], "states": r["states"]}
        if law == "spend":
            # Theorem 1, Theorem 2, DP
            if any(r["phase"][v] != math.ceil(sig[v] / w) for v in fin):
                out["checks"].append(f"T1 fails at w={w}")
            if r["T"] < out["sigma_max"]:
                out["checks"].append(f"T2a fails at w={w}")
            for ph in r["firsts"]:
                if any(dist < 2 ** sF - 1 for dist, sF in ph.values()):
                    out["checks"].append(f"T2b fails at w={w}")
            d = R.run_spend_dp(n, atoms, H, w)
            if d["P"] != r["P"] or d["L"] != r["L"] or d["phase"] != r["phase"]:
                out["checks"].append(f"DP != BFS at w={w}")
    if n <= 64:
        r3 = R.run_law(n, atoms, H, 3, "spend")
        out["w3"] = {"P": r3["P"], "T": r3["T"]}
        if any(r3["phase"][v] != math.ceil(sig[v] / 3) for v in fin):
            out["checks"].append("T1 fails at w=3")
        if r3["T"] < out["sigma_max"]:
            out["checks"].append("T2a fails at w=3")
    kp = runs[(2, "keep")]["phase"]
    p1 = runs[(1, "spend")]["phase"]
    g = {v: kp[v] < math.ceil(sig[v] / 2) for v in newly}
    out["keep_gain_fraction"] = float(np.mean([g[v] for v in newly])) if newly else None
    P1 = runs[(1, "spend")]["P"]
    out["phase_sizes_w1"] = [sum(1 for v in range(n) if p1[v] == t) for t in range(1, P1 + 1)]
    if P1 >= 4:
        sizes = out["phase_sizes_w1"]
        narrow = 1 + int(np.argmin(sizes[:-2]))
        bef = [v for v in newly if p1[v] <= narrow]
        aft = [v for v in newly if p1[v] > narrow]
        out["narrow"] = narrow
        out["keep_gain_before"] = float(np.mean([g[v] for v in bef])) if bef else None
        out["keep_gain_after"] = float(np.mean([g[v] for v in aft])) if aft else None
    out["T2_over_T1"] = out["w2"]["T"] / out["w1"]["T"] if out["w1"]["T"] else None
    out["sec"] = round(time.time() - t0, 2)
    return out


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    ns = [int(a) for a in args]
    fresh_only = "--fresh-only" in sys.argv
    K, S0 = 20, 0
    for a in sys.argv:
        if a.startswith("--samples="):
            K = int(a.split("=")[1])
        if a.startswith("--start="):
            S0 = int(a.split("=")[1])
    jobs = []
    for n in ns:
        if not fresh_only:
            jobs += [("study", n, s) for s in range(S0, S0 + K)]
        jobs += [("fresh", n, s) for s in range(S0, S0 + K)]
    t0 = time.time()
    res = []
    with Pool(4) as pool:
        for r in pool.imap_unordered(measure, jobs):
            res.append(r)
            print(r["kind"], r["n"], r["s"], r["sec"], r["sigma_max"], r["w1"]["T"], r["w2"]["T"], r["w2k"]["T"],
                  r["w2k"]["P"], r["checks"], flush=True)
    res.sort(key=lambda r: (r["n"], r["kind"], r["s"]))
    tag = "_".join(str(n) for n in ns) + ("_fresh" if fresh_only else "") + (f"_from{S0}" if S0 else "")
    with open(os.path.join(HERE, f"referee_task3_random_n{tag}.json"), "w") as fh:
        json.dump({"samples": res, "seconds": round(time.time() - t0, 1)}, fh, indent=1)


if __name__ == "__main__":
    main()
