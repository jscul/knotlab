"""Referee R1, task 4: narrow layered circuits (fresh code only).

Claim (Q3b, proof's "Layered circuits"): a layered monotone circuit of width
W, as an atom pattern (true inputs and one helper t held; AND gate
(x, y -> g); OR gate (x, t -> g), (y, t -> g)), is forced in one phase of
the keep law with 2W carried distinctions, at any depth.

Instances: the study's (rebuilt from the protocol read in job.py/atoms.py:
seed sha256("CS:narrow:<W>:<d>:<s>"), inputs rng.random(W) < 1/2, per layer
two distinct uniform readers and AND with chance 1/2) and fresh ones with
the referee's own generator (referee_core.layered_circuit) at more depths.
Per sample: P of the keep law at w = 2W, the least w giving one phase, the
forced set against circuit evaluation, and the number of true gates.
"""

import hashlib
import json
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import referee_carry as R  # noqa: E402

RC = R.RC


def study_circuit(W, d, s):
    seed = int.from_bytes(hashlib.sha256(f"CS:narrow:{W}:{d}:{s}".encode()).digest()[:8], "little")
    rng = np.random.default_rng(seed)
    inputs = rng.random(W) < 0.5
    layers = []
    for _ in range(d):
        x = rng.integers(0, W, W)
        y = rng.integers(0, W - 1, W)
        y = y + (y >= x)
        is_and = rng.random(W) < 0.5
        layers.append((is_and, x, y))
    return inputs, layers


def fresh_circuit(W, d, s):
    seed = int.from_bytes(hashlib.sha256(f"REFEREE-R1:CARRY:narrow:{W}:{d}:{s}".encode()).digest()[:8], "big")
    return RC.layered_circuit(W, d, np.random.default_rng(seed))


def measure(kind, W, d, s):
    inputs, layers = (study_circuit if kind == "study" else fresh_circuit)(W, d, s)
    n, A, held = RC.layered_to_atoms(inputs, layers)
    atoms = [tuple(int(x) for x in row) for row in A]
    H = set(np.flatnonzero(held).tolist())
    vals = RC.layered_eval(inputs, layers)
    true_ids = {0} | {1 + L * W + i for L, v in enumerate(vals) for i in range(W) if v[i]}
    clo = R.closure(n, atoms, H)
    rec = {"kind": kind, "W": W, "d": d, "s": s, "n": n, "true_gates": len(true_ids) - 1 - int(inputs.sum()),
           "closure_ok": clo == true_ids}
    rec["sigma_max"] = max(x for x in R.sigma(n, atoms, H) if x < R.INF)
    try:
        r = R.run_law(n, atoms, H, 2 * W, "keep", cap=1_500_000)
    except R.Capped as e:
        rec.update({"capped": int(e.args[0]), "P_keep_2W": None, "forced_ok": None, "least_w_one_phase": None})
        return rec
    rec["P_keep_2W"] = r["P"]
    rec["states_2W"] = r["states"]
    rec["forced_ok"] = r["forced"] == clo
    least = None
    for w in range(1, 2 * W + 1):
        if R.run_law(n, atoms, H, w, "keep")["P"] <= 1:
            least = w
            break
    rec["least_w_one_phase"] = least
    return rec


def main():
    t0 = time.time()
    out = []
    for W, depths in ((2, (4, 8, 16)), (3, (4, 6, 8))):
        for d in depths:
            for s in range(5):
                out.append(measure("study", W, d, s))
    for W, depths in ((2, (4, 8, 16, 32, 64)), (3, (4, 8, 12, 16))):
        for d in depths:
            for s in range(10):
                out.append(measure("fresh", W, d, s))
    bad = [r for r in out if "capped" not in r and not (r["closure_ok"] and r["forced_ok"] and r["P_keep_2W"] <= 1)]
    summ = {"cases": len(out), "fail": bad, "seconds": round(time.time() - t0, 1),
            "least_w_hist": {}, "with_true_gates": sum(1 for r in out if r["true_gates"] > 0),
            "sigma_max_hist": {}, "capped": [(r["kind"], r["W"], r["d"], r["s"]) for r in out if "capped" in r]}
    for r in out:
        k = f"W{r['W']}:{r['least_w_one_phase']}"
        summ["least_w_hist"][k] = summ["least_w_hist"].get(k, 0) + 1
        k = f"W{r['W']}:{r['sigma_max']}"
        summ["sigma_max_hist"][k] = summ["sigma_max_hist"].get(k, 0) + 1
    print(json.dumps(summ, indent=1))
    with open(os.path.join(HERE, "referee_task4_narrow.json"), "w") as fh:
        json.dump({"summary": summ, "samples": out}, fh, indent=1)


if __name__ == "__main__":
    main()
