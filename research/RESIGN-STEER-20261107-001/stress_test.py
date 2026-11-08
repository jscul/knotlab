#!/usr/bin/env python3
"""One size past for RESIGN-STEER-20261107-001's computed claims (research-next-steps, "Stress-Test Published Claims").

Ticket B measured the local rules on K_2-K_8 and K_10, the slope on K_12 and K_16, and the ascent on K_3-K_8. This reruns each with
the experiment's own functions one size past: the rules on K_12 (300 trials), the slope on K_20, and four ascents on K_9 and two on
K_10. Writes stress_test.json next to this file.

    python3 -B research/RESIGN-STEER-20261107-001/stress_test.py"""
import json
import random
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
EXP = ROOT / "experiments/RESIGN-STEER-20261107-001B/RESIGN-STEER-20261107-001B-E001_local_rules_and_the_force_between_halves"
sys.path.insert(0, str(EXP))
import run as R  # noqa: E402

T0 = time.time()


def rules_at(m, rng, trials=300):
    K = R.sphere(m)
    budget = 40 * m
    rows = []
    while len(rows) < trials:
        l, match, holes = R.start(K, rng)
        t = rng.randrange(K.V)
        if t not in holes:
            rows.append((l, match, holes, t, rng.randrange(K.V)))
    out = {"sphere": K.name, "budget": budget}
    for rule in ("strict", "sideways", "no_reversal", "random", "decoy"):
        ok = 0
        slow = []
        for (l, match, holes, t, decoy) in rows:
            r, st, _ = R.run_rule(K, match, holes, t, rule, rng, budget, decoy)
            ok += r
            if not r and rule == "no_reversal":
                slow.append(R.run_rule(K, match, holes, t, rule, rng, 10 * budget)[0])
        out[rule] = {"reached": ok, "of": trials}
        if rule == "no_reversal":
            out["no_reversal failures reached with 10x budget"] = slow
    R.log("stress rules", out)
    return out


if __name__ == "__main__":
    rng = random.Random(20261108)
    res = {"rules": rules_at(12, rng)}
    res["exponent"] = R.exponent(20, rng)
    res["ascent"] = [R.ascent(9, 4, rng), R.ascent(10, 2, rng)]
    res["passes"] = {
        "no_reversal reaches >= 95% on K_12": res["rules"]["no_reversal"]["reached"] >= 0.95 * 300,
        "K_20 slope within 0.1 of 1/2": abs(res["exponent"]["slope"] - 0.5) <= 0.1,
        "every ascent on K_9 and K_10 stops on two corners": all(
            set(a["endpoints"]) <= {"two corners, antipodal", "two corners, not antipodal"} for a in res["ascent"]),
    }
    res["seconds"] = round(time.time() - T0, 1)
    (HERE / "stress_test.json").write_text(json.dumps(res, indent=1, default=str) + "\n")
    R.log("wrote stress_test.json", res["passes"])
