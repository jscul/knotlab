"""Referee R1, task 1b: Theorems 1-3 at larger sigma (fresh code only).

Patterns at the jump (m = 3n, held = the first k* of a uniform order) at
n = 16, 24, 32, 48, 64, and random densities at n = 20, 30 with small held
sets, own seeds.  Same checks as task 1 (task-1 check_pattern), with w = 1, 2, 3.
Also records the smallest random witness (fewest distinctions, then atoms)
where the copying variant reaches less than the pebble game at the same w.
"""

import json
import os
import sys
import time
from multiprocessing import Pool

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import referee_carry as R  # noqa: E402
import referee_task1_theorems as T1  # noqa: E402


def gen(seed=1117):
    rng = np.random.default_rng(seed)
    for n, cnt in ((16, 300), (24, 300), (32, 200), (48, 120), (64, 80)):
        for _ in range(cnt):
            A = R.RC.random_atoms(n, 3 * n, rng)
            atoms = [tuple(int(x) for x in row) for row in A]
            order = rng.permutation(n).tolist()
            k = R.k_star(n, atoms, order)
            yield (n, atoms, order[:k])
    for n in (20, 30):
        for _ in range(200):
            c = float(rng.choice([1.5, 2.0, 2.5, 3.0]))
            A = R.RC.random_atoms(n, int(round(c * n)), rng)
            atoms = [tuple(int(x) for x in row) for row in A]
            held = rng.choice(n, int(rng.integers(2, 5)), replace=False).tolist()
            yield (n, atoms, held)


def copy_witness(seed=5):
    """Smallest random pattern with copy-reach(w) != pebble-reach(w)."""
    rng = np.random.default_rng(seed)
    best = None
    for n in range(5, 9):
        for _ in range(20000):
            m = int(rng.integers(n, 4 * n))
            A = R.RC.random_atoms(n, m, rng)
            atoms = sorted({tuple(int(x) for x in row) for row in A})
            held = set(rng.choice(n, int(rng.integers(2, 4)), replace=False).tolist())
            for w in (2, 3):
                pr = R.pebble_reach(n, atoms, held, w) - held
                cr = R.one_phase_reach(atoms, held, w, "copy")
                if cr != pr:
                    # prune atoms greedily while the difference persists
                    cur = list(atoms)
                    changed = True
                    while changed:
                        changed = False
                        for i in range(len(cur)):
                            trial = cur[:i] + cur[i + 1:]
                            p2 = R.pebble_reach(n, trial, held, w) - held
                            c2 = R.one_phase_reach(trial, held, w, "copy")
                            if c2 != p2:
                                cur = trial
                                changed = True
                                break
                    cand = (n, len(cur), w, cur, sorted(held),
                            sorted(R.pebble_reach(n, cur, held, w) - held),
                            sorted(R.one_phase_reach(cur, held, w, "copy")),
                            sorted(R.one_phase_reach(cur, held, w + 1, "copy")))
                    if best is None or cand[:2] < best[:2]:
                        best = cand
        if best is not None:
            break
    if best is None:
        return None
    n, m, w, at, H, pr, cr, cr1 = best
    return {"n": n, "w": w, "atoms": at, "held": H, "pebble_reach": pr, "copy_reach_w": cr,
            "copy_reach_w_plus_1": cr1}


def main():
    t0 = time.time()
    with Pool(4) as pool:
        res = pool.map(T1.check_pattern, list(gen()), chunksize=2)
    agg = T1.aggregate(res)
    agg["seconds"] = round(time.time() - t0, 1)
    print(json.dumps({k: v for k, v in agg.items() if k != "bad"}), flush=True)
    print("bad:", agg["bad"][:2])
    t0 = time.time()
    wit = copy_witness()
    print("copy witness:", wit, round(time.time() - t0, 1))
    with open(os.path.join(HERE, "referee_task1b_larger.json"), "w") as fh:
        json.dump({"larger": agg, "copy_witness": wit}, fh, indent=1)


if __name__ == "__main__":
    main()
