"""Referee R1 for STATE-RULES-20261117-001: the knot arm with more runs.  This file runs the STUDY'S OWN rules.py (labelled; the
point is statistical power and a confound, not an independent recomputation, which referee_fresh.py does).

  ../../../.venv/bin/python -B referee_power.py > referee_power.json      (from this directory)

1. Fan against non-fan (the owner's premise): KF3 (fewest states over knot-local moves) from fan6 and from nonfan6, the same 12
   states with different knots, 1,000 runs each to n = 12.  At n = 7, 8, 10 and 12: the distribution of the number of orders (lam),
   the two-order frequency, and the distribution over classes of the grown STATES (knots ignored) at n = 7 and 8.  Tests:
   two-sided Fisher on two orders at n = 8; chi-square on the lam distribution; the overlap of the state-class distributions.
   Also the power the study's 30 + 30 runs had to see the difference observed here.
2. The weighting confound behind "2/3 against 1/2": from the line of three, two orders at n = 6 under KF3 (knot-local, weight per
   knot set), KC3 (closure-local, a function of the states, weight per knot set) and F3 (states-only, weight per extension),
   1,000 runs each for KF3 and KC3, against F3's exact 1/2.
"""
import collections
import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "experiments/STATE-RULES-20261117-001B/STATE-RULES-20261117-001B-E001_rules"))
import rules as R  # noqa: E402  (the study's code)
from scipy.stats import chi2_contingency, fisher_exact  # noqa: E402


def runs(rule, start, nmax, count, tag, local, canon):
    out = []
    for i in range(count):
        states, knots, n, tr = R.knot_grow(rule, 3, start, nmax, f"REF:{tag}:{i}", None, local)
        out.append(tr)
    return out


def class_at(rule, start, n_at, count, tag, local, canon):
    """The class of the grown states (knots ignored) at n_at, per run."""
    cls = []
    for i in range(count):
        states, knots, n, tr = R.knot_grow(rule, 3, start, n_at, f"REF:{tag}:{i}", None, local)
        cls.append(canon.cid(states, n))
    return cls


def power(p1, p2, n, sims=4000, seed=1):
    import random
    rng = random.Random(seed)
    hit = 0
    for _ in range(sims):
        a = sum(rng.random() < p1 for _ in range(n))
        b = sum(rng.random() < p2 for _ in range(n))
        if fisher_exact([[a, n - a], [b, n - b]])[1] < 0.05:
            hit += 1
    return hit / sims


def main():
    out = {}
    canon = R.Canon()
    big = {}
    for start in ("fan6", "nonfan6"):
        big[start] = runs("fewest", start, 12, 1000, f"KF3:{start}", "knot", canon)
    res = {}
    for n in (7, 8, 10, 12):
        lam = {s: collections.Counter(next(r for r in tr if r["n"] == n)["lam"] for tr in big[s]) for s in big}
        two = {s: sum(1 for tr in big[s] if next(r for r in tr if r["n"] == n).get("two_way")) for s in big}
        keys = sorted(set(lam["fan6"]) | set(lam["nonfan6"]))
        table = [[lam["fan6"].get(k, 0) for k in keys], [lam["nonfan6"].get(k, 0) for k in keys]]
        table = [list(col) for col in zip(*[c for c in zip(*table) if sum(c) > 0])]
        chi = chi2_contingency(table)[1] if len(table[0]) > 1 else 1.0
        fish = fisher_exact([[two["fan6"], 1000 - two["fan6"]], [two["nonfan6"], 1000 - two["nonfan6"]]])[1]
        res[n] = {"lam_fan6": dict(lam["fan6"]), "lam_nonfan6": dict(lam["nonfan6"]), "two_orders": two,
                  "fisher_p_two_orders": fish, "chi2_p_lam": chi}
        print("n", n, json.dumps(res[n]), file=sys.stderr, flush=True)
    out["fan_vs_nonfan_KF3_1000_runs"] = res
    p1, p2 = res[8]["two_orders"]["fan6"] / 1000, res[8]["two_orders"]["nonfan6"] / 1000
    out["power_of_30_vs_30_at_these_rates"] = {"rates": [p1, p2], "power": power(p1, p2, 30)}
    canon2 = R.Canon()
    cl = {}
    for n_at in (7, 8):
        c = {s: collections.Counter(class_at("fewest", s, n_at, 400, f"KF3cls:{s}:{n_at}", "knot", canon2)) for s in ("fan6", "nonfan6")}
        shared = set(c["fan6"]) & set(c["nonfan6"])
        tv = 0.5 * sum(abs(c["fan6"].get(k, 0) / 400 - c["nonfan6"].get(k, 0) / 400) for k in set(c["fan6"]) | set(c["nonfan6"]))
        cl[n_at] = {"classes_fan6": len(c["fan6"]), "classes_nonfan6": len(c["nonfan6"]), "shared_classes": len(shared),
                    "total_variation_distance": tv}
        print("classes at", n_at, json.dumps(cl[n_at]), file=sys.stderr, flush=True)
    out["state_classes_fan_vs_nonfan_400_runs"] = cl
    conf = {}
    for name, local in (("KF3", "knot"), ("KC3", "closure")):
        trs = runs("fewest", "line", 6, 1000, f"conf:{name}", local, canon)
        conf[name] = sum(1 for tr in trs if next(r for r in tr if r["n"] == 6).get("two_way")) / 1000
    conf["F3_exact"] = 0.5
    out["two_orders_at_6_from_one_knot"] = conf
    print(json.dumps(out, indent=1, default=str))


if __name__ == "__main__":
    main()
