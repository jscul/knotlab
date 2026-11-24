"""C3: every order. On D2(4,3) under the birth-by-birth law with DEAD and BY-GENERATION (RATION-3,
waiting), a search over all orders of the moves of generations 0 and 1, by distinct structures up
to renaming. An extra search under ANY (not registered) is reported separately.

Usage: python -B run_c3.py   -> c3_results.json
"""

import json
import os
import time
from collections import Counter

import birth_by_birth as bb
import iso
from selfcheck import ART


def search(rule):
    t0 = time.time()
    nodes = bb.every_order("D2(4,3)", rule)
    term = [n for n in nodes if n["terminal"]]
    outcomes = Counter(json.dumps(n["outcome"], sort_keys=True) for n in term)
    memo = {}     # number of orders from each state to each kind of end

    def count(i):
        if i in memo:
            return memo[i]
        n = nodes[i]
        if n["terminal"]:
            r = Counter({json.dumps(n["outcome"], sort_keys=True): 1})
        else:
            r = Counter()
            for k in n["children"]:
                r.update(count(k))
        memo[i] = r
        return r

    orders_by_outcome = count(0)
    return {"start": "D2(4,3)", "rule": rule, "distinct_states": len(nodes), "terminal_states": len(term),
            "orders_total": nodes[0]["orders"], "terminal_outcomes": {k: v for k, v in outcomes.items()},
            "orders_by_outcome": dict(orders_by_outcome), "time_s": round(time.time() - t0, 2),
            "pass_P1": all(n["outcome"]["jam_at_gen1"] and n["outcome"]["gen1_moves"] == 8 and n["outcome"]["gen1_joins"] == 0
                           for n in term)}


def main():
    out = {"registered": search("DEAD"), "extra_not_registered": search("ANY"), "iso_stats": dict(iso.STATS)}
    path = os.path.join(ART, "c3_results.json")
    with open(path, "w") as f:
        json.dump(out, f, indent=1)
    print("written", path)
    print(json.dumps(out, indent=1)[:3000])


if __name__ == "__main__":
    main()
