"""Exact independent-engine checks of the already saved forest audit cases."""
from __future__ import annotations

import json
import resource
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import job


def setup(params):
    pass


def cases():
    yield "ambient_detour", {"kind": "ambient"}
    yield "random_exact_engines", {"kind": "random"}


def run(case_id, payload):
    started = time.monotonic()
    search, brute = job.load_old()
    if payload["kind"] == "ambient":
        # The entire universe of binary addresses through N=3 is present.
        addresses = ["", "0", "1", "00", "01", "10", "11", "000", "001",
                     "010", "011", "100", "101", "110", "111"]
        names = [("0", "00", "01"), ("00", "10", "11"), ("10", "000", "001")]
        knots = [tuple(addresses.index(x) for x in row) for row in names]
        A = [i for i, x in enumerate(addresses) if len(x) == 1]
        B = [i for i, x in enumerate(addresses) if len(x) == 3]
        fast = search.search(knots, len(addresses), A, B, cap=15, seconds=20)
        exact = brute.least_bond(knots, len(addresses), A, B, cap=15)
        result = {"addresses": addresses, "knots": knots, "A": A, "B": B,
                  "fresh_search": fast, "brute_supports": exact,
                  "agree_with_compact_truth_L5": fast["L"] == exact["L"] == 5}
        assert result["agree_with_compact_truth_L5"]
    else:
        raw = [json.loads(line) for line in (HERE / "run/results.jsonl").read_text().splitlines()]
        patterns = [p for row in raw if row["case"].startswith("random_")
                    for p in row["result"]["patterns"]]
        checked, truth_crosschecks, failures = [], [], []
        direct_count = 0
        for pattern in patterns:
            n = pattern["n"]
            for query in pattern["level_queries"]:
                k, s = query["k"], query["s"]
                A = [v for v in range(n) if pattern["levels"][v] == k]
                B = [v for v in range(n) if pattern["levels"][v] == k + s]
                exact = search.search(pattern["knots"], n, A, B, cap=n, seconds=10)
                actual = "none" if exact["L"] == f"> {n}" else exact["L"]
                row = {"seed": pattern["seed"], "k": k, "s": s,
                       "truth_L": query["L"], "fresh_L": actual,
                       "exact": exact["exact"], "agree": actual == query["L"]}
                checked.append(row)
                if not row["agree"] or not row["exact"]:
                    failures.append(row)
            if n <= 9 and direct_count < 20:
                # Compare complete bond families, not merely one endpoint minimum.
                direct_count += 1
                direct = brute.enumerated_bonds(pattern["knots"], n, [0], [n-1])
                truth = sorted(map(tuple, pattern["bonds"]))
                reference = sorted(map(tuple, direct["all_bonds"]))
                row = {"seed": pattern["seed"], "n": n, "bonds": len(truth),
                       "all_bonds_agree": truth == reference}
                truth_crosschecks.append(row)
                if not row["all_bonds_agree"]:
                    failures.append(row)
        result = {"patterns": len(patterns), "level_query_crosschecks": checked,
                  "complete_bond_family_crosschecks": truth_crosschecks,
                  "failures": failures}
    result["resources"] = {"seconds": time.monotonic() - started,
                           "max_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                           "compute_workers": 1}
    return result
