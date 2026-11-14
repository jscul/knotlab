"""Substantive larger-case comparison and bounded monotonicity falsifier."""
from __future__ import annotations

import argparse
import hashlib
import json
import random
import resource
import sys
import time
from pathlib import Path

import brute_supports as brute

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import fresh_pattern
import fresh_search


def bounds(k0, s):
    return (range((1 << k0) - 1, (1 << (k0 + 1)) - 1),
            range((1 << (k0 + s)) - 1, (1 << (k0 + s + 1)) - 1))


def compare_existing():
    rows = [json.loads(line) for line in (HERE / "brute_N4_cap7.jsonl").read_text().splitlines()]
    out = []
    for row in rows:
        pattern = brute.placement_pattern(brute.freeze_key(row["key"]), row["N"])
        assert pattern == fresh_pattern.build(row["key"], row["N"])
        for original in row["levels"]:
            A, B = bounds(row["k0"], original["s"])
            result = fresh_search.search(pattern, row["nvars"], A, B, cap=7, seconds=30, width_limit=12)
            item = {"case": row["case"], "s": original["s"], "brute_L": original["L"],
                    "fresh": result, "agree": result["L"] == original["L"] if result.get("exact") else None}
            out.append(item)
            print(json.dumps({"comparison": row["case"], "s": original["s"], "brute": original["L"],
                              "fresh": result["L"], "agree": item["agree"]}), flush=True)
    (HERE / "comparison_N4.json").write_text(json.dumps(out, indent=2) + "\n")


def enriched_cases():
    records = brute.population_records()
    selected = []
    rng = random.Random("support-enrichment-20261114")
    for label, predicate, count in (
        ("actual_profile_3344", lambda r: [v["L_N"] for v in r.get("levels", [])] == [3, 3, 4, 4], 4),
        ("actual_undecided_dense", lambda r: brute.label(r) == "undecided" and r["knot_count"] > 1000, 4),
        ("actual_direct_rigid", lambda r: [v["L_N"] for v in r.get("levels", [])] == [2, 2, 2, 2], 4),
        ("actual_none_connected", lambda r: any(v["components"] and v["L_N"] == "none" for v in r.get("levels", [])), 2),
    ):
        eligible = [r for r in records if predicate(r)]
        for row in rng.sample(eligible, min(count, len(eligible))):
            selected.append({"source": label, "case": row["case"], "key": row["key"],
                             "study_N9_L": [r["L_N"] for r in row.get("levels", [])],
                             "eligible_count": len(eligible)})
    return selected


def extend():
    rows = []
    with (HERE / "enriched_results.jsonl").open("w") as f:
        for case in enriched_cases():
            for N, cap in ((4, 7), (5, 4)):
                key = brute.freeze_key(case["key"])
                triples = brute.placement_pattern(key, N)
                assert triples == brute.direct_pattern(key, N) == fresh_pattern.build(key, N)
                nvars = (1 << (N + 1)) - 1
                for s in (1, 2):
                    A, B = bounds(2, s)
                    result = brute.least_bond(triples, nvars, A, B, cap)
                    other = fresh_search.search(triples, nvars, A, B, cap=cap, seconds=30, width_limit=12)
                    row = {**case, "N": N, "k0": 2, "s": s, "cap": cap,
                           "knots": len(triples), "brute": result, "fresh": other,
                           "agree": result["L"] == other["L"] if other.get("exact") else None}
                    f.write(json.dumps(row, sort_keys=True) + "\n")
                    f.flush()
                    rows.append(row)
                    print(json.dumps({"extended": case["case"], "source": case["source"], "N": N, "s": s,
                                      "brute": result["L"], "fresh": other["L"], "agree": row["agree"]}), flush=True)
    return rows


def monotonicity(limit=1288):
    """A single genuine increase suffices; cap at the old finite L is exact."""
    records = brute.population_records()
    random.Random("monotonicity-falsifier-20261114").shuffle(records)
    checked = []
    violations = []
    started = time.perf_counter()
    with (HERE / "monotonicity_results.jsonl").open("w") as f:
        for record in records[:limit]:
            key = brute.freeze_key(record["key"])
            for N, k0, s in ((2, 1, 1), (3, 1, 2), (3, 2, 1), (4, 2, 2)):
                first = brute.placement_pattern(key, N)
                A, B = bounds(k0, s)
                before = brute.least_bond(first, (1 << (N + 1)) - 1, A, B, 4)
                if not isinstance(before["L"], int):
                    continue
                second = brute.placement_pattern(key, N + 1)
                A, B = bounds(k0, s)
                after = brute.least_bond(second, (1 << (N + 2)) - 1, A, B, before["L"])
                raised = after["L"] != "dead" and (not isinstance(after["L"], int) or after["L"] > before["L"])
                row = {"case": record["case"], "key": record["key"], "N_before": N, "N_after": N + 1,
                       "k0": k0, "s": s, "before": before, "after": after, "violation": raised}
                checked.append(row)
                f.write(json.dumps(row, sort_keys=True) + "\n")
                f.flush()
                if raised:
                    violations.append(row)
                    print(json.dumps({"MONOTONICITY_VIOLATION": record["case"], "N": N,
                                      "k0": k0, "s": s, "before": before["L"], "after": after["L"]}), flush=True)
                    # Preserve and independently cross-check the first exact witness.
                    A, B = bounds(k0, s)
                    row["fresh_before"] = fresh_search.search(first, (1 << (N + 1)) - 1, A, B, cap=before["L"], seconds=60, width_limit=14)
                    A, B = bounds(k0, s)
                    row["fresh_after"] = fresh_search.search(second, (1 << (N + 2)) - 1, A, B, cap=before["L"], seconds=60, width_limit=14)
                    (HERE / "actual_monotonicity_violation.json").write_text(json.dumps(row, indent=2) + "\n")
                    return {"checked": len(checked), "descriptions_attempted": records.index(record) + 1,
                            "violations": violations, "seconds": time.perf_counter() - started}
            if len(checked) % 100 == 0:
                print(json.dumps({"monotonicity_checks": len(checked), "seconds": time.perf_counter() - started}), flush=True)
    return {"checked": len(checked), "descriptions_attempted": min(limit, len(records)),
            "violations": violations, "seconds": time.perf_counter() - started}


def source_controls():
    outputs = {}
    identity = brute.freeze_key([1, [0], [0], [0], [[0, 1, 2]]])
    flip = brute.freeze_key([1, [1], [0], [0], [[0, 1, 2]]])
    expected = sorted((x, 2 * x + 1, 2 * x + 2) for x in range(15))
    outputs["tree_identity_N4"] = brute.placement_pattern(identity, 4) == expected
    outputs["tree_arbitrary_action_N4"] = brute.placement_pattern(flip, 4) == expected
    outputs["no_append_at_boundary"] = brute.placement_pattern(identity, 0) == []
    outputs["word_order_none_0_1"] = [(w, a) for w in brute.old.words(1) for a in (None, 0, 1)][:3] == [((), None), ((), 0), ((), 1)]
    outputs["two_flips_cancel"] = all(brute.old.direct_state(flip, 0, brute.old.direct_state(flip, 0, x, n), n) == x
                                          for n in range(6) for x in range(1 << n))
    outputs["distinctness_negative"] = brute.placement_pattern(brute.freeze_key([1, [0], [0], [0], [[0, 3, 6]]]), 5) == []
    outputs["corrupted_tree_rejected"] = brute.placement_pattern(identity, 4) != expected[:-1]
    outputs["all_passed"] = all(outputs.values())
    (HERE / "source_controls.json").write_text(json.dumps(outputs, indent=2) + "\n")
    return outputs


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("compare", "extend", "mono", "controls"))
    parser.add_argument("--limit", type=int, default=1288)
    args = parser.parse_args()
    started = time.perf_counter()
    if args.mode == "compare":
        compare_existing()
    elif args.mode == "extend":
        extend()
    elif args.mode == "mono":
        result = monotonicity(args.limit)
        (HERE / "monotonicity_summary.json").write_text(json.dumps(result, indent=2) + "\n")
    else:
        source_controls()
    (HERE / f"resources_{args.mode}.json").write_text(json.dumps({
        "seconds": time.perf_counter() - started,
        "max_rss_KiB": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        "invocation": sys.argv,
    }, indent=2) + "\n")


if __name__ == "__main__":
    main()
