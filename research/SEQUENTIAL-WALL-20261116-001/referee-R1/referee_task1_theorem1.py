"""Task 1: Theorem 1 (phase(v) = sigma(v)) by brute force on small patterns.

(i) exhaustive: every set of atoms on n = 4 distinctions (12 possible atoms,
    demander pair unordered) with every held set (2^12 x 2^4 = 65,536 cases);
(ii) random: patterns with n = 5..12, m from n/2 to 4n atoms, held sets of
    size 1..n-1.
For each case: phase by the forcing law (pure Python), sigma by the set-valued
enumeration of derivation-tree values by height (exact, argued in
referee_core.strahler_sets), sigma by Knuth's generalized Dijkstra, sigma by
relaxation from INF, the vectorized phase law, and the forced set by
exhaustive states for n <= 8.
"""

import itertools
import json
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import referee_core as C  # noqa: E402


def brute_forced(n, atoms, held):
    held = set(held)
    free = [v for v in range(n) if v not in held]
    always = [True] * n
    for bits in itertools.product((0, 1), repeat=len(free)):
        x = [1] * n
        for v, bt in zip(free, bits):
            x[v] = bt
        if all((not (x[a] and x[b])) or x[c] for (a, b, c) in atoms):
            always = [al and bool(xv) for al, xv in zip(always, x)]
    return always


def one_case(n, atoms, held, stats, do_brute=False, do_np=False):
    P, phase, Pcount = C.phases_py(n, atoms, held)
    s_set = C.strahler_sets(n, atoms, held)
    s_knuth = C.strahler_knuth(n, atoms, held)
    s_relax = C.strahler_relax_from_inf(n, atoms, held)
    forced = C.closure_worklist(n, atoms, held)
    S, R = C.rounds_py(n, atoms, held)
    ok = True
    ok &= phase == s_set
    ok &= s_set == s_knuth
    ok &= s_set == s_relax
    ok &= all((v in P) == forced[v] == (v in S) for v in range(n))
    fin = [x for x in s_set if x != C.INF]
    ok &= Pcount == (max(fin) if fin else 0)
    if do_np and atoms:
        A = np.array(atoms, dtype=np.int64)
        hm = np.zeros(n, dtype=bool)
        hm[list(held)] = True
        Pn, phn, tn, _ = C.phases_np(n, A, hm)
        phn = [C.INF if x < 0 else int(x) for x in phn.tolist()]
        ok &= phn == phase and tn == Pcount
        stats["np_checked"] += 1
    if do_brute:
        ok &= brute_forced(n, atoms, held) == forced
        stats["brute_checked"] += 1
    stats["cases"] += 1
    stats["distinctions"] += n
    stats["max_sigma"] = max(stats["max_sigma"], max(fin) if fin else 0)
    for x in fin:
        stats["sigma_hist"][str(x)] = stats["sigma_hist"].get(str(x), 0) + 1
    if not ok:
        stats["failures"].append({"n": n, "atoms": atoms, "held": list(held),
                                  "phase": [str(x) for x in phase], "sigma": [str(x) for x in s_set]})
    return ok


def new_stats():
    return {"cases": 0, "distinctions": 0, "failures": [], "max_sigma": 0, "sigma_hist": {},
            "brute_checked": 0, "np_checked": 0}


def main():
    out = {}
    t0 = time.time()
    # counterexample from the proof: numerically least solution is wrong
    n, atoms, held = 3, [(0, 1, 2), (0, 2, 1)], [0]   # h=0, c=1, d=2
    s = C.strahler_sets(n, atoms, held)
    eq_ok = all(combine_ok for combine_ok in [C.combine(0, 1) == 1])
    out["unsupported_cycle_example"] = {"sigma_c_d": [str(s[1]), str(s[2])],
                                        "phases": [str(x) for x in C.phases_py(n, atoms, held)[1]],
                                        "numerically_least_solution_1_1_satisfies_equations": eq_ok}

    # (i) exhaustive n = 4
    n = 4
    all_atoms = [(a, b, c) for a, b in itertools.combinations(range(n), 2) for c in range(n) if c not in (a, b)]
    st = new_stats()
    for mask in range(1 << len(all_atoms)):
        atoms = [all_atoms[i] for i in range(len(all_atoms)) if mask >> i & 1]
        for hmask in range(1 << n):
            held = [v for v in range(n) if hmask >> v & 1]
            one_case(n, atoms, held, st, do_brute=(mask % 97 == 0), do_np=(mask % 131 == 0))
    st["seconds"] = round(time.time() - t0, 1)
    out["exhaustive_n4"] = st

    # (ii) random n = 5..12
    rng = np.random.default_rng(20261116)
    t1 = time.time()
    st = new_stats()
    for it in range(30000):
        n = int(rng.integers(5, 13))
        m = int(rng.integers(max(1, n // 2), 4 * n + 1))
        A = C.random_atoms(n, m, rng)
        atoms = [tuple(x) for x in A.tolist()]
        k = int(rng.integers(1, n))
        held = rng.permutation(n)[:k].tolist()
        one_case(n, atoms, held, st, do_brute=(n <= 8 and it % 10 == 0), do_np=(it % 5 == 0))
    st["seconds"] = round(time.time() - t1, 1)
    out["random_n5_12"] = st

    # (ii-b) stress: few held, many atoms (deeper sigma); also sets with H = 2n
    t2 = time.time()
    st = new_stats()
    st["height_2n_agrees"] = 0
    for it in range(20000):
        n = int(rng.integers(8, 13))
        m = int(rng.integers(2 * n, 6 * n + 1))
        A = C.random_atoms(n, m, rng)
        atoms = [tuple(x) for x in A.tolist()]
        k = int(rng.integers(2, 4))
        held = rng.permutation(n)[:k].tolist()
        one_case(n, atoms, held, st, do_np=(it % 5 == 0))
        if it % 20 == 0:
            st["height_2n_agrees"] += int(C.strahler_sets(n, atoms, held, H=2 * n) == C.strahler_sets(n, atoms, held))
    st["seconds"] = round(time.time() - t2, 1)
    out["stress_few_held_n8_12"] = st

    # (iii) structured (larger n, sigma by Knuth and sets): pyramids, ladders
    st = new_stats()
    for h in range(1, 7):
        idx = {}
        for i in range(h + 1):
            for j in range(h + 1 - i):
                idx[i, j] = len(idx)
        atoms = [(idx[i - 1, j], idx[i - 1, j + 1], idx[i, j]) for i in range(1, h + 1) for j in range(h + 1 - i)]
        held = [idx[0, j] for j in range(h + 1)]
        one_case(len(idx), atoms, held, st, do_np=True)
    out["pyramids_h1_6"] = st
    out["all_ok"] = (not out["exhaustive_n4"]["failures"] and not out["random_n5_12"]["failures"]
                     and not out["pyramids_h1_6"]["failures"] and not out["stress_few_held_n8_12"]["failures"])
    out["seconds_total"] = round(time.time() - t0, 1)
    with open(os.path.join(HERE, "referee_task1_theorem1.json"), "w") as fh:
        json.dump(out, fh, indent=1)
    print(json.dumps({k: (v if not isinstance(v, dict) else {x: y for x, y in v.items() if x != "failures"})
                      for k, v in out.items()}, indent=1))
    for k in ("exhaustive_n4", "random_n5_12", "stress_few_held_n8_12", "pyramids_h1_6"):
        print(k, "failures:", len(out[k]["failures"]))


if __name__ == "__main__":
    main()
