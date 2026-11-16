"""Cross-check: the study's atoms.py run AS THE THING UNDER TEST on the
referee's own instances, compared per distinction with the referee's oracle.
(Run with python -B so no bytecode is written into the study's folder.)"""

import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import referee_core as C  # noqa: E402

ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
STUDY = os.path.join(ROOT, "experiments", "SEQUENTIAL-WALL-20261116-001A",
                     "SEQUENTIAL-WALL-20261116-001A-E001_rounds_phases")
sys.dont_write_bytecode = True
sys.path.insert(0, STUDY)
import atoms as S  # noqa: E402  (under test)
from referee_task5_dual import random_acyclic  # noqa: E402


def as_int(lst):
    return np.array([-1 if x == C.INF else x for x in lst], dtype=np.int64)


def compare(n, A, hm, dual=False, fringe=False):
    atoms = [tuple(x) for x in A.tolist()]
    held = np.flatnonzero(hm).tolist()
    p = S.Pattern(n, A, held)
    r = {}
    _, ph_s, P_s = S.untangling_phases(p)
    _, ph_o, P_o, _ = C.phases_np(n, A, hm)
    r["phase"] = bool(np.array_equal(ph_s, ph_o)) and P_s == P_o
    rk = S.rank(p)
    rk = np.where(rk >= S.INF, -1, rk)
    r["rank_vs_sigma"] = bool(np.array_equal(rk, as_int(C.strahler_knuth(n, atoms, held))))
    if fringe:
        lf = S.log2_fringe(p)
        fr = C.fringe_knuth(n, atoms, held)
        lo = np.array([math.log2(x) if x != C.INF else np.inf for x in fr])
        fin = np.isfinite(lo)
        r["log2_fringe"] = bool(np.array_equal(np.isfinite(lf), fin) and np.allclose(lf[fin], lo[fin], atol=1e-9))
    if dual:
        unf_s, dph_s, Pd_s = S.dual_phases(p)
        unf_o, dph_o, Pd_o = C.dual_law_py(n, atoms, held)
        r["dual_phase"] = bool(np.array_equal(dph_s, as_int(dph_o))) and Pd_s == Pd_o
        r["P_dual"] = [int(Pd_s), int(Pd_o)]
    return r


def main():
    out = {"random_acyclic_small": {"cases": 0, "all_agree": True},
           "random_k_star_n2^12": [], "layered_w1024_d32": []}
    rng = np.random.default_rng(np.random.SeedSequence([7736, 0]))
    for _ in range(3000):
        n = int(rng.integers(5, 13))
        m = int(rng.integers(max(1, n // 2), 4 * n + 1))
        atoms, topo = random_acyclic(n, m, rng)
        k = int(rng.integers(0, n // 2 + 1))
        hm = np.zeros(n, dtype=bool)
        hm[rng.permutation(n)[:k]] = True
        r = compare(n, np.array(atoms, dtype=np.int64), hm, dual=True, fringe=True)
        out["random_acyclic_small"]["cases"] += 1
        out["random_acyclic_small"]["all_agree"] &= all(v for kk, v in r.items() if kk != "P_dual")
    from referee_task2_random import k_star_search
    for s in range(5):
        n = 4096
        rng = np.random.default_rng(np.random.SeedSequence([7731, 12, s]))  # same as task 2
        A = C.random_atoms(n, 3 * n, rng)
        order = rng.permutation(n)
        ks = k_star_search(n, A, order)
        hm = np.zeros(n, dtype=bool)
        hm[order[:ks]] = True
        out["random_k_star_n2^12"].append(compare(n, A, hm, fringe=True))
    for s in range(10):
        rng = np.random.default_rng(np.random.SeedSequence([7735, 1024, 32, s]))  # same as pdual_more
        inputs, layers = C.layered_circuit(1024, 32, rng)
        n, A, hm = C.layered_to_atoms(inputs, layers)
        out["layered_w1024_d32"].append(compare(n, A, hm, dual=True))
    print(json.dumps(out, indent=1))
    json.dump(out, open(os.path.join(HERE, "referee_cross_study_code.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
