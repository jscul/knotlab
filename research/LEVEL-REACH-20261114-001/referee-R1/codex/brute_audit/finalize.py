"""Collect completed independent support-audit evidence without new searches."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import brute_supports as brute

HERE = Path(__file__).resolve().parent


def load(name):
    return json.loads((HERE / name).read_text())


def lines(name):
    return [json.loads(line) for line in (HERE / name).read_text().splitlines()]


def main():
    primary = lines("brute_N4_cap7.jsonl")
    compared = load("comparison_N4.json")
    enriched = lines("enriched_results.jsonl")
    checks = ([{"N": 4, "case": r["case"], "s": q["s"], "result": q}
               for r in primary for q in r["levels"]] +
              [{"N": r["N"], "case": r["case"], "s": r["s"], "result": r["brute"]} for r in enriched])
    comparisons = compared + enriched
    full = [r for r in comparisons if r["agree"] is not None]
    mismatches = [r for r in full if not r["agree"]]
    cases = {r["case"] for r in primary + enriched}
    actual_cases = {r["case"] for r in primary if r["source"] == "actual_registered_population"} | {r["case"] for r in enriched}
    records = {r["case"]: r for r in brute.population_records()}
    witness_ids = {load("actual_monotonicity_violation.json")["case"], load("actual_k3_monotonicity_violation.json")["case"]}
    witness_population_context = [{"case": key, "key": records[key]["key"], "N9_union": records[key]["union"],
                                   "N9_L": [v["L_N"] for v in records[key].get("levels", [])],
                                   "memberships": records[key]["memberships"]} for key in sorted(witness_ids)]
    coverage = {
        "N4_queries": sum(r["N"] == 4 for r in checks),
        "N5_queries": sum(r["N"] == 5 for r in checks),
        "queries": len(checks), "unique_descriptions_including_controls": len(cases),
        "unique_actual_population_descriptions": len(actual_cases),
        "support_caps": {"N4": 7, "N5": 4},
        "candidate_supports_total": sum(sum(r["result"]["candidate_supports"].values()) for r in checks),
        "SAT_projection_calls_total": sum(r["result"].get("sat_calls", 0) for r in checks),
        "exact_fresh_comparisons": len(full),
        "exact_fresh_comparisons_numeric_or_bounded": sum(r.get("brute_L", r.get("brute", {}).get("L")) != "none" for r in full),
        "fresh_limit_exclusions": len(comparisons) - len(full),
        "mismatches": mismatches,
        "all_pattern_reconstructions_agree": all(r["pattern_reconstructions_agree"] for r in primary),
        "sampling": "2 per N9 outcome stratum using fixed seed, plus 3 controls; enrichment uses 4 each profile3344,dense-undecided,direct-rigid",
    }
    out = {"scope": "LEVEL-REACH-20261114-001/referee-R1/codex/brute_audit", "coverage": coverage,
           "source_controls": load("source_controls.json"),
           "fixed_top_exact_comparisons": load("fixed_top_exact_comparisons.json"),
           "monotonicity": {"generic_countermodel": "countermodels.json",
                            "actual_first_witness": "actual_monotonicity_model_tables.json",
                            "actual_k2_witness": "actual_k2_monotonicity_models.json",
                            "actual_fixed_k3_witness": "actual_k3_monotonicity_violation.json"},
           "witness_population_context": witness_population_context,
           "limits": ["No claim of N4/N5 equality to study N9 numbers: top level and truncation differ.",
                      "Exact least bond only through declared cap unless complete model-quotient search says unrestricted.",
                      "Separate exact solver's width exclusions are not passes.",
                      "The N5 complete-state attempt for the fixed-top witness stops after8193states and is explicitly incomplete.",
                      "Independent AI subagent implementation within same task; no external replication."]}
    source_paths = [HERE / "brute_supports.py", HERE / "compare_and_extend.py", HERE / "counterexample_deep.py",
                    HERE / "fixed_top_falsifier.py", HERE / "finalize.py", brute.OLD,
                    HERE.parent / "fresh_pattern.py", HERE.parent / "fresh_search.py"]
    out["source_sha256"] = {str(p.relative_to(brute.ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in source_paths}
    raw = brute.ROOT / "artifacts/LEVEL-REACH-20261114-001A/LEVEL-REACH-20261114-001A-E001_level_reach/records_slim.jsonl.gz"
    out["input_sha256"] = {str(raw.relative_to(brute.ROOT)): hashlib.sha256(raw.read_bytes()).hexdigest()}
    (HERE / "summary.json").write_text(json.dumps(out, indent=2) + "\n")
    assert not mismatches
    assert out["source_controls"]["all_passed"]
    for p in HERE.glob("*.json"):
        json.loads(p.read_text())
    for p in HERE.glob("*.jsonl"):
        for line in p.read_text().splitlines():
            json.loads(line)
    print(json.dumps(coverage, indent=2))
    print(json.dumps(witness_population_context, indent=2))


if __name__ == "__main__":
    main()
