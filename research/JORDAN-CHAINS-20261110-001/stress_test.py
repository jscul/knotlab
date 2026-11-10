#!/usr/bin/env python3
"""Stress test for JORDAN-CHAINS-20261110-001, one size past ticket A's chain lemma (sides 8 to 64): at side 128, for a sample of a in
GF(256)* covering k = 1, 2, 3, 4, 6, 7, 8, 11 and 15 (a = alpha^s for s = 15, 21, 7, 3, 39, 27, 1, 37 and 0, alpha the root of the least
primitive polynomial; s = 0 is the eigenvalue 1), whether each G Y^j heads a chain of exactly 2k - 1 - 4j and these are the Jordan
blocks. Writes stress_test.json and stress_test_log.txt beside this file after each a."""
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "proofs/JORDAN-CHAINS-20261110-001A/JORDAN-CHAINS-20261110-001A-P001_the_chains_one_polynomial_heads"))
import chains_lib as CH  # noqa: E402

T0 = time.time()
SAMPLE = [15, 21, 7, 3, 39, 27, 1, 37, 0]
RES = {"side": 128, "sample (s with a = alpha^s)": SAMPLE, "cases": {}}


def save(final=False):
    RES["seconds"] = round(time.time() - T0)
    if final:
        RES["pass"] = all(v["ok"] for v in RES["cases"].values())
    (HERE / "stress_test.json").write_text(json.dumps(RES, indent=1, default=str) + "\n")


def main():
    log = open(HERE / "stress_test_log.txt", "w")
    F = CH.RL.GF(8)
    for s in SAMPLE:
        r = CH.chain_lemma_at(F, F.exp[s], 7)
        RES["cases"]["alpha^%d" % s] = r
        log.write("[%6.0fs] a = alpha^%d: k = %d, ok %s, blocks %s\n" % (time.time() - T0, s, r["k"], r["ok"], r.get("blocks")))
        log.flush()
        save()
    save(final=True)
    log.write("done, pass %s\n" % RES["pass"])


if __name__ == "__main__":
    main()
