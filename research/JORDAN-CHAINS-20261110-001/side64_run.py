#!/usr/bin/env python3
"""The registered post-registration check of JORDAN-CHAINS-20261110-001A: the chain lemma at every a in GF(128)*, side 64 (ticket A's
check 5 runs sides 8 to 32 in process). Writes side64.json and side64_log.txt beside this file. About eleven minutes."""
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "proofs/JORDAN-CHAINS-20261110-001A/JORDAN-CHAINS-20261110-001A-P001_the_chains_one_polynomial_heads"))
import chains_lib as CH  # noqa: E402

T0 = time.time()


def main():
    m = 6
    F = CH.RL.GF(m + 1)
    bad, by_k, fails = 0, {}, []
    log = open(HERE / "side64_log.txt", "w")
    for i, a in enumerate(F.exp):
        r = CH.chain_lemma_at(F, a, m)
        if not r["ok"]:
            bad += 1
            fails.append({"a = alpha^": F.log[a], "result": r})
        by_k[r["k"]] = by_k.get(r["k"], 0) + 1
        if (i + 1) % 16 == 0:
            log.write("[%5.0fs] %d of %d\n" % (time.time() - T0, i + 1, F.q1))
            log.flush()
    res = {"side": 64, "values of a": F.q1, "failures": bad, "failing cases": fails, "counts by k": by_k,
           "seconds": round(time.time() - T0), "pass": bad == 0}
    (HERE / "side64.json").write_text(json.dumps(res, indent=1, default=str) + "\n")
    log.write("done, pass %s\n" % res["pass"])


if __name__ == "__main__":
    main()
