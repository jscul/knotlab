#!/usr/bin/env python3
"""Stress test for LINEAR-ROOTS-20261109-001, one and two sizes past ticket A's check 4: the geometric Kloosterman law,
dim ker(I + C_s(a)) = |K(a)|/4 for every a in GF(2n)*, at sides 256 and 512 (ticket A: 4 to 128), in the normalized form of
Theorem 2 (the kernel of F -> (k + 1) F(k + 1) + Omega_b(k) F(k) mod k^h, b^2 = a). Writes stress_test.json and stress_test_log.txt
beside this file."""
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
LIB = ROOT / "proofs/LINEAR-ROOTS-20261109-001A/LINEAR-ROOTS-20261109-001A-P001_kloosterman_multiplicities"
sys.path.insert(0, str(LIB))
import roots_lib as RL  # noqa: E402

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
        n, h = 1 << m, 1 << (m - 1)
        F = RL.GF(m + 1)
        bad, counts = 0, {}
        for a in F.exp:
            d = h - F.rank(RL.star_matrix(F, F.sqrt(a), m, h))
            K = F.kloosterman(a)
            bad += d != abs(K) // 4
            key = "kernel %d, K %d" % (d, K)
            counts[key] = counts.get(key, 0) + 1
        RES["geometric law at side %d" % n] = {"values of a": F.q1, "mismatches": bad, "counts": counts, "pass": bad == 0}
        log("side", n, "mismatches", bad, "of", F.q1)
        save()
    save(final=True)
    log("done, pass", RES["pass"])


if __name__ == "__main__":
    main()
