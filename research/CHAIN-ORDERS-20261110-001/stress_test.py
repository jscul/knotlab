#!/usr/bin/env python3
"""Stress test for CHAIN-ORDERS-20261110-001, one size past ticket A's checks of the leading form (every a for sides 8 to 128): at side
256, for every a in GF(512)*, whether the symmetric reduction M of the family Z(a + d) onto the eigenvectors G Y^j (G monic, complement
the monomials off the kernel's top degrees) has v(M_ij) >= e = 2k - 1 - 2(i + j) and [d^e] M_ij = a^-e [k - i - j is a power of two].
Writes stress_test.json and stress_test_log.txt beside this file every 32 values of a."""
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "proofs/CHAIN-ORDERS-20261110-001A/CHAIN-ORDERS-20261110-001A-P001_the_reduced_form_at_every_order"))
import orders_lib as OL  # noqa: E402

T0 = time.time()
RES = {"side": 256, "values of a": "every a in GF(512)*", "failures": [], "k counts": {}}


def save(done, final=False):
    RES["checked"] = done
    RES["seconds"] = round(time.time() - T0)
    if final:
        RES["pass"] = not RES["failures"]
    (HERE / "stress_test.json").write_text(json.dumps(RES, indent=1, default=str) + "\n")


def main():
    log = open(HERE / "stress_test_log.txt", "w")
    F = OL.RL.GF(9)
    for t, a in enumerate(F.exp):
        r = OL.leading_form_at(F, a, 8)
        RES["k counts"][str(r["k"])] = RES["k counts"].get(str(r["k"]), 0) + 1
        if not r["ok"]:
            RES["failures"].append({"a": "alpha^%d" % F.log[a], "k": r["k"], "bad": r.get("bad")})
        if (t + 1) % 32 == 0:
            log.write("[%6.0fs] %d of %d, failures %d\n" % (time.time() - T0, t + 1, len(F.exp), len(RES["failures"])))
            log.flush()
            save(t + 1)
    save(len(F.exp), final=True)
    log.write("done, pass %s\n" % RES["pass"])
    log.close()


if __name__ == "__main__":
    main()
