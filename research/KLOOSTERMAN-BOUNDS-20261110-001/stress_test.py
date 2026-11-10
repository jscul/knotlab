#!/usr/bin/env python3
"""Stress test for KLOOSTERMAN-BOUNDS-20261110-001, one and two sizes past ticket A's checks 3 and 5: at sides 256 and 512, for every b,
the kernel of X_b is G_b r(Y) of degree below h (its top degrees deg G_b + 2j, each G_b Y^j in the kernel) with deg G_b = h - k_b,
k_b = (|K(b) - 1| - 1)/2, and valuations 0, ..., dim - 1 (ticket A: sides 8 to 128). Writes stress_test.json and
stress_test_log.txt beside this file."""
import json
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
LIB = ROOT / "proofs/KLOOSTERMAN-BOUNDS-20261110-001A/KLOOSTERMAN-BOUNDS-20261110-001A-P001_one_polynomial_per_eigenvalue"
sys.path.insert(0, str(LIB))
import bounds_lib as BL  # noqa: E402

RL = BL.RL
T0 = time.time()
LOG = HERE / "stress_test_log.txt"
RES = {}


def log(*a):
    s = " ".join(str(x) for x in a)
    print(s, flush=True)
    with open(LOG, "a") as f:
        f.write("[%6.0fs] %s\n" % (time.time() - T0, s))


def save(final=False):
    RES["seconds"] = round(time.time() - T0)
    if final:
        RES["pass"] = all(v.get("pass") for v in RES.values() if isinstance(v, dict))
    (HERE / "stress_test.json").write_text(json.dumps(RES, indent=1, default=str) + "\n")


def main():
    open(LOG, "w").close()
    for m in (8, 9):
        run(m)
    save(final=True)
    log("done, pass", RES["pass"])


def run(m):
    n, h = 1 << m, 1 << (m - 1)
    F = RL.GF(m + 1)
    bad_cyclic, bad_deg, bad_val, done = 0, 0, 0, 0
    counts = {}
    for b in F.exp:
        X = RL.star_matrix(F, b, m, h)
        ker = BL.nullspace(F, X)
        K = F.kloosterman(b)
        k = BL.k_index(K)
        if not ker:
            bad_deg += k != 0
        else:
            degs, ech = BL.top_degrees(F, ker)
            G = ech[-1][:degs[0] + 1]
            fam, v = [], G.copy()
            while len(v) - 1 < h:
                fam.append(np.concatenate([v, np.zeros(h - len(v), dtype=np.int64)]))
                v = BL.times_Y(v)
            ok = degs == [degs[0] + 2 * j for j in range(len(degs))] and len(fam) == len(ker)
            ok = ok and all(not BL.matmul(F, X, f[:, None]).any() for f in fam)
            bad_cyclic += not ok
            bad_deg += degs[0] != h - k
            bad_val += BL.low_degrees(F, ker) != list(range(len(ker)))
        key = "k %d" % k
        counts[key] = counts.get(key, 0) + 1
        done += 1
        if done % 128 == 0:
            log("side %d: %d of %d values of b done" % (n, done, F.q1))
    RES["one polynomial per eigenvalue at side %d" % n] = {
        "values of b": F.q1, "kernels not G_b r(Y)": bad_cyclic, "deg G_b != h - k_b": bad_deg,
        "valuations not 0..dim-1": bad_val, "counts by k": counts,
        "pass": bad_cyclic == 0 and bad_deg == 0 and bad_val == 0}
    log("side %d:" % n, RES["one polynomial per eigenvalue at side %d" % n])
    save()


if __name__ == "__main__":
    main()
