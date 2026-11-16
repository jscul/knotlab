"""Task 4: circuits as atom patterns.

(a) encoding check: on every input of small random layered and unlayered
    circuits, the atom pattern's forced set (worklist closure) equals the
    circuit's value at every gate; on the tiniest, the forced set also equals
    the set of distinctions that are 1 in every allowed state (brute force).
(b) layered, widths 256 and 1024, d = 8, 16, 32, 64: median over samples with
    a true output of the largest sigma among true outputs (last layer).
(c) unlayered, 256 inputs, G = 1,024, 4,096, 16,384: median largest sigma
    over true gates.
sigma by Knuth's algorithm, checked against the phase law everywhere.
Seeds: SeedSequence([7732, ...]) (referee's own).
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


def encoding_check(rng):
    res = {"layered_circuits": 0, "layered_inputs": 0, "unlayered_circuits": 0, "unlayered_inputs": 0,
           "brute_force_cases": 0, "mismatches": 0}
    for _ in range(120):
        w = int(rng.integers(2, 6))
        d = int(rng.integers(1, 5))
        _, layers = C.layered_circuit(w, d, rng)
        for bits in itertools.product((False, True), repeat=w):
            inp = np.array(bits, dtype=bool)
            vals = C.layered_eval(inp, layers)
            n, A, hm = C.layered_to_atoms(inp, layers)
            atoms = [tuple(x) for x in A.tolist()]
            held = np.flatnonzero(hm).tolist()
            f = C.closure_worklist(n, atoms, held)
            got = [np.array(f[1 + L * w: 1 + (L + 1) * w]) for L in range(d + 1)]
            if not all(np.array_equal(g, v) for g, v in zip(got, vals)):
                res["mismatches"] += 1
            if n - len(held) <= 14:
                res["brute_force_cases"] += 1
                if brute_forced(n, atoms, held) != f:
                    res["mismatches"] += 1
            res["layered_inputs"] += 1
        res["layered_circuits"] += 1
    for _ in range(120):
        ni = int(rng.integers(2, 7))
        g = int(rng.integers(1, 11))
        _, gates = C.unlayered_circuit(ni, g, rng)
        for bits in itertools.product((False, True), repeat=ni):
            inp = np.array(bits, dtype=bool)
            vals = C.unlayered_eval(inp, gates)
            n, A, hm = C.unlayered_to_atoms(inp, gates)
            atoms = [tuple(x) for x in A.tolist()]
            held = np.flatnonzero(hm).tolist()
            f = C.closure_worklist(n, atoms, held)
            if not np.array_equal(np.array(f[1:]), vals):
                res["mismatches"] += 1
            if n - len(held) <= 14:
                res["brute_force_cases"] += 1
                if brute_forced(n, atoms, held) != f:
                    res["mismatches"] += 1
            res["unlayered_inputs"] += 1
        res["unlayered_circuits"] += 1
    return res


def measure(n, A, hm, out_ids):
    S, R = C.rounds_np(n, A, hm)
    P, phase, Pc, _ = C.phases_np(n, A, hm)
    sig = C.strahler_knuth_np(n, A, hm)
    sig = np.array([-1 if x == C.INF else x for x in sig], dtype=np.int64)
    so = sig[out_ids]
    so = so[so >= 0]
    return {"R": int(R), "P": int(Pc), "sigma_equals_phase": bool(np.array_equal(sig, phase)),
            "out_true": int(len(so)), "out_max_sigma": int(so.max()) if len(so) else -1}


def main():
    t0 = time.time()
    out = {}
    rng = np.random.default_rng(np.random.SeedSequence([7732, 0]))
    out["encoding"] = encoding_check(rng)
    out["encoding"]["seconds"] = round(time.time() - t0, 1)
    print("encoding", out["encoding"], flush=True)

    lay = {}
    for w in (256, 1024):
        for d in (8, 16, 32, 64):
            recs = []
            t1 = time.time()
            for s in range(10):
                rng = np.random.default_rng(np.random.SeedSequence([7732, 1, w, d, s]))
                inputs, layers = C.layered_circuit(w, d, rng)
                vals = C.layered_eval(inputs, layers)
                n, A, hm = C.layered_to_atoms(inputs, layers)
                r = measure(n, A, hm, 1 + d * w + np.arange(w))
                S, _ = C.rounds_np(n, A, hm)
                r["evaluation_matches"] = all(np.array_equal(S[1 + L * w: 1 + (L + 1) * w], vals[L])
                                              for L in range(d + 1))
                recs.append(r)
            alive = [r for r in recs if r["out_true"] > 0]
            lay[f"w{w}-d{d}"] = {
                "alive": len(alive), "of": len(recs),
                "out_max_sigma_median": float(np.median([r["out_max_sigma"] for r in alive])) if alive else None,
                "out_max_sigma_all": [r["out_max_sigma"] for r in recs],
                "P_median": float(np.median([r["P"] for r in recs])),
                "R_median": float(np.median([r["R"] for r in recs])),
                "sigma_equals_phase_all": all(r["sigma_equals_phase"] for r in recs),
                "evaluation_matches_all": all(r["evaluation_matches"] for r in recs),
                "seconds": round(time.time() - t1, 1)}
            print(f"w{w}-d{d}", lay[f"w{w}-d{d}"], flush=True)
    out["layered"] = lay

    unl = {}
    for g in (1024, 4096, 16384):
        recs = []
        t1 = time.time()
        for s in range(10):
            rng = np.random.default_rng(np.random.SeedSequence([7732, 2, g, s]))
            inputs, gates = C.unlayered_circuit(256, g, rng)
            vals = C.unlayered_eval(inputs, gates)
            n, A, hm = C.unlayered_to_atoms(inputs, gates)
            r = measure(n, A, hm, 1 + 256 + np.arange(g))
            S, _ = C.rounds_np(n, A, hm)
            r["evaluation_matches"] = bool(np.array_equal(S[1:], vals))
            recs.append(r)
        unl[str(g)] = {
            "out_max_sigma_median": float(np.median([r["out_max_sigma"] for r in recs])),
            "out_max_sigma_all": [r["out_max_sigma"] for r in recs],
            "P_median": float(np.median([r["P"] for r in recs])),
            "R_median": float(np.median([r["R"] for r in recs])),
            "sigma_equals_phase_all": all(r["sigma_equals_phase"] for r in recs),
            "evaluation_matches_all": all(r["evaluation_matches"] for r in recs),
            "seconds": round(time.time() - t1, 1)}
        print(g, unl[str(g)], flush=True)
    out["unlayered"] = unl
    out["study"] = {"layered_w1024_out_max_strahler": {"8": 4, "16": 5, "32": 7, "64": 9},
                    "layered_w256_out_max_strahler": {"8": 4, "16": 5, "32": 6, "64": 9},
                    "unlayered_out_max_strahler": {"1024": 2, "4096": 3, "16384": 4}}
    out["seconds_total"] = round(time.time() - t0, 1)
    with open(os.path.join(HERE, "referee_task4_circuits.json"), "w") as fh:
        json.dump(out, fh, indent=1)


if __name__ == "__main__":
    main()
