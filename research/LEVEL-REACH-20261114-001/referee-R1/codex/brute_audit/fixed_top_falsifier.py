"""Bounded fixed-top falsifier, prioritizing the two known counterexamples."""
from __future__ import annotations

import json
import random
import resource
import time
from pathlib import Path

import brute_supports as brute
from compare_and_extend import bounds
from counterexample_deep import enumerate_models, quotient_bonds

HERE = Path(__file__).resolve().parent


def exact_table(record, k0, s, Ns):
    out = {"case": record["case"], "key": record["key"], "k0": k0, "s": s, "levels": []}
    key = brute.freeze_key(record["key"])
    for N in Ns:
        knots = brute.placement_pattern(key, N)
        models, complete = enumerate_models(knots, (1 << (N + 1)) - 1, limit=8192)
        A, B = bounds(k0, s)
        quotient = quotient_bonds(models, A, B) if complete and models else None
        out["levels"].append({"N": N, "knots": knots, "model_count": len(models),
                              "models_complete": complete,
                              "models": list(map(list, models)) if complete else None,
                              "quotient": quotient})
    return out


def main():
    started = time.perf_counter()
    first = json.loads((HERE / "actual_monotonicity_violation.json").read_text())
    second = json.loads((HERE / "actual_k2_monotonicity_violation.json").read_text())
    records = brute.population_records()
    random.Random("fixed-top-falsifier-20261114").shuffle(records)
    priority = [first, second]
    seen = {r["case"] for r in priority}
    selected = priority + [r for r in records if r["case"] not in seen][:400]
    results = []
    violations = []
    with (HERE / "monotonicity_k3_results.jsonl").open("w") as f:
        for record in selected:
            key = brute.freeze_key(record["key"])
            knots4 = brute.placement_pattern(key, 4)
            A, B = bounds(3, 1)
            before = brute.least_bond(knots4, 31, A, B, cap=3)
            if isinstance(before["L"], int):
                knots5 = brute.placement_pattern(key, 5)
                A, B = bounds(3, 1)
                after = brute.least_bond(knots5, 63, A, B, cap=before["L"])
                violation = after["L"] != "dead" and (not isinstance(after["L"], int) or after["L"] > before["L"])
                row = {"case": record["case"], "key": record["key"], "N_before": 4, "N_after": 5,
                       "k0": 3, "s": 1, "before": before, "after": after, "violation": violation}
                results.append(row)
                f.write(json.dumps(row) + "\n")
                f.flush()
                if record["case"] in seen or violation:
                    print(json.dumps({"case": record["case"], "fixed_top3_before": before["L"],
                                      "after": after["L"], "violation": violation}), flush=True)
                if violation:
                    violations.append(row)
                    (HERE / "actual_k3_monotonicity_violation.json").write_text(json.dumps(row, indent=2) + "\n")
                    detail = exact_table(row, 3, 1, (4, 5))
                    (HERE / "actual_k3_monotonicity_models.json").write_text(json.dumps(detail, indent=2) + "\n")
                    print(json.dumps({"k3_exact_models": [{"N": v["N"], "models": v["model_count"],
                                                           "complete": v["models_complete"],
                                                           "L": v["quotient"].get("L") if v["quotient"] else None}
                                                          for v in detail["levels"]]}), flush=True)
                    break
            elif record["case"] in seen:
                print(json.dumps({"case": record["case"], "fixed_top3_before": before["L"], "skip": True}), flush=True)
    (HERE / "monotonicity_k3_summary.json").write_text(json.dumps({
        "frozen_descriptions_max": len(selected), "finite_before_comparisons": len(results),
        "violations": violations, "seconds": time.perf_counter() - started,
        "max_rss_KiB": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
    }, indent=2) + "\n")
    # Independently strengthen the k0=2 witness as well.
    detail = exact_table(second, 2, 1, (3, 4))
    (HERE / "actual_k2_monotonicity_models.json").write_text(json.dumps(detail, indent=2) + "\n")
    print(json.dumps({"k2_exact_models": [{"N": v["N"], "models": v["model_count"],
                                          "complete": v["models_complete"],
                                          "L": v["quotient"].get("L") if v["quotient"] else None}
                                         for v in detail["levels"]]}), flush=True)


if __name__ == "__main__":
    main()
