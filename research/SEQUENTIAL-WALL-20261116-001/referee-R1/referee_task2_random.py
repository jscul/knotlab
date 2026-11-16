"""Task 2 (and 3): rounds and phases at the jump on random atom patterns.

usage: referee_task2_random.py LOG2N SAMPLES [--deep]
  n = 2^LOG2N, m = 3n atoms (ordered distinct uniform triples), held = first
  k of a uniform order; k* = least k with closure >= n/2 (binary search, the
  closure being monotone in k).  Readings at k*, k* - 1 and alpha n for
  alpha in {0.03, 0.06, 0.2, 0.4}.  At k* and k* - 1 also sigma by Knuth's
  algorithm (checked = phase) and, with --deep, the exact fewest-leaves fringe.
Seeds: numpy SeedSequence([7731, LOG2N, s]) (referee's own, not the study's).
Writes referee_task2_n<LOG2N>.json.
"""

import json
import math
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import referee_core as C  # noqa: E402

ALPHAS = [0.03, 0.06, 0.2, 0.4]


def closure_size(n, A, order, k):
    hm = np.zeros(n, dtype=bool)
    hm[order[:k]] = True
    S, R = C.rounds_np(n, A, hm)
    return int(S.sum())


def k_star_search(n, A, order):
    lo, hi = 1, n  # closure(n) = n >= n/2
    while lo < hi:
        mid = (lo + hi) // 2
        if 2 * closure_size(n, A, order, mid) >= n:
            hi = mid
        else:
            lo = mid + 1
    return lo


def reading(n, A, atoms_list, order, k, deep=False, fringe=False):
    hm = np.zeros(n, dtype=bool)
    hm[order[:k]] = True
    S, R = C.rounds_np(n, A, hm)
    P, phase, Pc, sizes = C.phases_np(n, A, hm)
    out = {"k": int(k), "closure": int(S.sum()), "R": int(R), "P": int(Pc), "phase_sizes": sizes,
           "phase_law_same_forced_set": bool(np.array_equal(S, P))}
    if deep:
        held = order[:k].tolist()
        wl = C.closure_worklist(n, atoms_list, held)
        out["worklist_closure_agrees"] = bool(np.array_equal(np.array(wl), S))
        sig = C.knuth_superior(n, atoms_list, held, 0, C.combine)
        sig_arr = np.array([-1 if x == C.INF else x for x in sig], dtype=np.int64)
        out["sigma_equals_phase"] = bool(np.array_equal(sig_arr, phase))
        fin = sig_arr >= 0
        out["max_sigma"] = int(sig_arr[fin].max())
        if fringe:
            fr = C.knuth_superior(n, atoms_list, held, 1, lambda x, y: x + y)
            lf = np.array([math.log2(x) if x != C.INF else -1.0 for x in fr])
            out["max_log2_fringe"] = float(lf[fin].max())
            out["sigma_le_log2_fringe_all"] = bool(np.all(sig_arr[fin] <= lf[fin] + 1e-12))
            # fringe at the distinction(s) of largest sigma
            out["log2_fringe_at_max_sigma_min"] = float(lf[sig_arr == out["max_sigma"]].min())
    return out


def run_sample(e, s, deep, fringe):
    n = 2 ** e
    rng = np.random.default_rng(np.random.SeedSequence([7731, e, s]))
    A = C.random_atoms(n, 3 * n, rng)
    order = rng.permutation(n)
    ks = k_star_search(n, A, order)
    atoms_list = [tuple(x) for x in A.tolist()] if deep else None
    res = {"e": e, "s": s, "n": n, "k_star": int(ks), "alpha_star": ks / n}
    res["at_k_star"] = reading(n, A, atoms_list, order, ks, deep, fringe)
    res["at_k_star_minus_1"] = reading(n, A, atoms_list, order, ks - 1, deep, fringe)
    res["k_star_is_least"] = bool(2 * res["at_k_star"]["closure"] >= n and 2 * res["at_k_star_minus_1"]["closure"] < n)
    res["alphas"] = {}
    for al in ALPHAS:
        k = max(1, int(round(al * n)))
        res["alphas"][str(al)] = reading(n, A, atoms_list, order, k)
    return res


def main():
    e = int(sys.argv[1])
    samples = int(sys.argv[2])
    deep = "--deep" in sys.argv or "--fringe" in sys.argv
    fringe = "--fringe" in sys.argv
    t0 = time.time()
    recs = []
    for s in range(samples):
        t1 = time.time()
        r = run_sample(e, s, deep, fringe)
        r["seconds"] = round(time.time() - t1, 2)
        recs.append(r)
        print(e, s, r["k_star"], r["at_k_star"]["R"], r["at_k_star"]["P"], r["at_k_star_minus_1"]["R"],
              r["at_k_star_minus_1"]["P"], r["at_k_star"].get("max_log2_fringe"), r["seconds"], flush=True)
    out = {"e": e, "samples": samples, "deep": deep, "fringe": fringe,
           "seconds": round(time.time() - t0, 1), "records": recs}
    with open(os.path.join(HERE, f"referee_task2_n{e}.json"), "w") as fh:
        json.dump(out, fh)


if __name__ == "__main__":
    main()
