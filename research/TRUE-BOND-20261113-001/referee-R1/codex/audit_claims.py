"""Blind row arithmetic for TRUE-BOND referee points 2--6.

Reads only the two expressly admitted JSONL inputs and the supplied summary.
It does not import or inspect the implementation under review.
"""

from collections import Counter
from copy import deepcopy
from fractions import Fraction
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
TRUE = "artifacts/TRUE-BOND-20261113-001A/TRUE-BOND-20261113-001A-E001_side_branches/true_rates_all.jsonl"
PRIOR = "artifacts/PROVED-RATE-20261113-001A/PROVED-RATE-20261113-001A-E001_cycle_mean/rates_all.jsonl"
SUMMARY = "artifacts/TRUE-BOND-20261113-001A/TRUE-BOND-20261113-001A-E001_side_branches/summary.json"
OUTPUT = Path(__file__).resolve().with_name("audit_claims.json")


def load_rows(relative):
    rows = []
    with (ROOT / relative).open() as handle:
        for line_number, line in enumerate(handle, 1):
            if line.strip():
                rows.append((line_number, json.loads(line)))
    return rows


def duplicate_ids(rows):
    return {str(idx): count for idx, count in Counter(r["idx"] for _, r in rows).items() if count != 1}


def ratio(numerator, denominator):
    return {"numerator": numerator, "denominator": denominator,
            "percent": 100 * numerator / denominator if denominator else None}


def main():
    raw = load_rows(TRUE)
    prior = load_rows(PRIOR)
    supplied_summary = json.loads((ROOT / SUMMARY).read_text())
    rows = []
    issues = []
    for line, row in raw:
        values, ray = row["L"], row["L_ray"]
        if len(values) != 12 or len(ray) != 12:
            issues.append({"idx": row["idx"], "issue": "array_length"})
        flags = [v is not None for v in values]
        if flags != sorted(flags, reverse=True):
            issues.append({"idx": row["idx"], "issue": "nonprefix_values"})
        if any(v is not None and type(v) is not int for v in values + ray):
            issues.append({"idx": row["idx"], "issue": "nonnumeric_value"})
        pairs = [(s, a, b, b - a) for s, (a, b) in enumerate(zip(values, ray), 1)
                 if a is not None and b is not None]
        if any(a is not None and b is None for a, b in zip(values, ray)):
            issues.append({"idx": row["idx"], "issue": "true_without_ray"})
        depth = max((s for s, v in enumerate(values, 1) if v is not None), default=0)
        rows.append({"source_line": line, "idx": row["idx"], "status": row["status"],
                     "depth": depth, "L": values, "L_ray": ray,
                     "deficits": [d for s, a, b, d in pairs],
                     "shortened": any(d > 0 for s, a, b, d in pairs),
                     "raw": row})

    study = [(line, r) for line, r in prior if r.get("complete") is True
             and (r.get("lambda_float") or 0) > 0]
    expected_ids = {r["idx"] for _, r in study}
    actual_ids = {r["idx"] for r in rows}
    positivity_disagreements = [r["idx"] for _, r in prior
                               if ((r.get("lambda_float") or 0) > 0)
                               != (Fraction(r["lambda"]) > 0 if r.get("lambda") is not None else False)]
    short = [r for r in rows if r["shortened"]]
    depth12 = [r for r in rows if r["depth"] == 12]
    ge8 = [r for r in rows if r["depth"] >= 8]
    p2 = [r for r in short if r["L"][5] is not None and r["L"][11] is not None]
    p3 = [r for r in rows if r["L"][5] is not None and r["L"][11] is not None]

    def group(selected):
        shortened = [r for r in selected if r["shortened"]]
        result = {"families": len(selected), "ids": [r["idx"] for r in selected],
                  "shorteners": ratio(len(shortened), len(selected)),
                  "shortener_ids": [r["idx"] for r in shortened]}
        if all(r["depth"] >= 8 for r in selected):
            result["endpoint_growth_from_4"] = ratio(sum(r["L"][r["depth"] - 1] > r["L"][3]
                                                         for r in selected), len(selected))
            result["shortener_endpoint_growth_from_4"] = ratio(
                sum(r["L"][r["depth"] - 1] > r["L"][3] for r in shortened), len(shortened))
        if all(r["depth"] == 12 for r in selected):
            result["growth_6_to_12"] = ratio(sum(r["L"][11] > r["L"][5] for r in selected), len(selected))
            result["shortener_growth_6_to_12"] = ratio(
                sum(r["L"][11] > r["L"][5] for r in shortened), len(shortened))
        return result

    computed_summary = {
        "families": len(rows),
        "status": dict(Counter(r["status"] for r in rows)),
        "depth_reached": {str(k): v for k, v in sorted(Counter(r["depth"] for r in rows).items())},
        "P1_shortened_within_reached": [len(short), len(rows)],
        "negative_deficit": sum(d < 0 for r in rows for d in r["deficits"]),
        "P2_deficit_growth_6_to_12": dict(Counter(str(r["deficits"][11] - r["deficits"][5]) for r in p2)),
        "P3_L12_gt_L6": [sum(r["L"][11] > r["L"][5] for r in p3), len(p3)],
        "grows_within_reached_ge8": [sum(r["L"][r["depth"] - 1] > r["L"][3] for r in ge8), len(ge8)],
        "max_deficit": dict(Counter(str(max(r["deficits"], default=0)) for r in rows)),
        "deficit_profiles_shortened": {str(r["idx"]): r["deficits"] for r in short},
    }

    known_nonshort = [r for r in depth12 if not r["shortened"]]
    unknown_p1 = [r for r in rows if not r["shortened"] and r["depth"] < 12]
    shortened_evidence = [{"idx": r["idx"], "source_line": r["source_line"], "depth": r["depth"],
                           "L_observed": r["L"][:r["depth"]],
                           "L_ray_observed": r["L_ray"][:r["depth"]], "deficits": r["deficits"]}
                          for r in short]
    errors = [{"idx": r["idx"], "source_line": r["source_line"], "depth": r["depth"],
               "active_s": r["raw"].get("active_s"), "stage": r["raw"].get("stage"),
               "error": r["raw"].get("error"), "seconds": r["raw"].get("seconds")}
              for r in rows if r["status"] == "error"]
    no_values = [{"idx": r["idx"], "source_line": r["source_line"], "status": r["status"]}
                 for r in rows if not r["deficits"]]
    wrong_count = deepcopy(computed_summary)
    wrong_count["families"] += 1
    wrong_profile = deepcopy(computed_summary)
    wrong_profile["deficit_profiles_shortened"][str(short[0]["idx"])][0] += 1
    controls = {
        "total_is_226": len(rows) == 226,
        "study_set_exact": actual_ids == expected_ids and len(study) == 226,
        "no_true_duplicates": not duplicate_ids(raw),
        "no_prior_duplicates": not duplicate_ids(prior),
        "no_row_schema_or_prefix_issues": not issues,
        "summary_matches_all_fields": computed_summary == supplied_summary,
        "status_partition": sum(computed_summary["status"].values()) == len(rows),
        "depth_partition": sum(computed_summary["depth_reached"].values()) == len(rows),
        "depth12_group_partition": len(depth12) + sum(r["depth"] < 12 for r in rows) == 226,
        "ge8_group_partition": len(ge8) + sum(r["depth"] < 8 for r in rows) == 226,
        "shortener_depth12_partition": sum(r["depth"] == 12 for r in short) + sum(r["depth"] < 12 for r in short) == len(short),
        "shortener_ge8_partition": sum(r["depth"] >= 8 for r in short) + sum(r["depth"] < 8 for r in short) == len(short),
        "p1_three_way_partition": len(short) + len(known_nonshort) + len(unknown_p1) == 226,
        "done_equals_depth12": {r["idx"] for r in rows if r["status"] == "done"} == {r["idx"] for r in depth12},
        "exactly_two_error_rows": len(errors) == 2,
        "eleven_rows_explicitly_unobserved": len(no_values) == 11,
        "negative_control_wrong_count_detected": wrong_count != supplied_summary,
        "negative_control_wrong_profile_detected": wrong_profile != supplied_summary,
        "negative_control_duplicate_detected": bool(duplicate_ids(raw + [raw[0]])),
        "negative_control_missing_id_detected": (actual_ids - {rows[0]["idx"]}) != expected_ids,
    }
    evidence = {
        "scope_id": "TRUE-BOND-20261113-001", "lane": "referee-R1 points 2--6",
        "sources": {"true_rows": TRUE, "prior_rows": PRIOR, "supplied_summary": SUMMARY},
        "implementation_access": "None: no implementation source or implementation output directory was opened or imported.",
        "study_selection": {"prior_rows": len(prior), "prior_complete_positive_lambda_rows": len(study),
                            "true_rows": len(rows), "true_unique_ids": len(actual_ids),
                            "missing_ids": sorted(expected_ids - actual_ids),
                            "extra_ids": sorted(actual_ids - expected_ids),
                            "true_duplicate_ids": duplicate_ids(raw), "prior_duplicate_ids": duplicate_ids(prior),
                            "float_vs_exact_lambda_sign_disagreements": positivity_disagreements,
                            "study_ids": sorted(expected_ids)},
        "computed_summary": computed_summary,
        "summary_fields_equal": {key: computed_summary.get(key) == supplied_summary.get(key)
                                 for key in sorted(set(computed_summary) | set(supplied_summary))},
        "groups": {"depth12": group(depth12), "not_depth12": group([r for r in rows if r["depth"] < 12]),
                   "at_least8": group(ge8), "below8": group([r for r in rows if r["depth"] < 8])},
        "prediction_denominators": {
            "P1": {"registered": 226, "known_shortened": len(short),
                   "known_not_shortened_through12": len(known_nonshort), "unresolved": len(unknown_p1),
                   "failure_already_decided": len(short) > 0.2 * 226},
            "P2": {"known_shortened": len(short), "known_shortened_observed_at6_and12": len(p2),
                   "known_shortened_missing_endpoint": len(short) - len(p2),
                   "observed": [{"idx": r["idx"], "source_line": r["source_line"],
                                 "D6": r["deficits"][5], "D12": r["deficits"][11],
                                 "difference": r["deficits"][11] - r["deficits"][5]} for r in p2],
                   "verdict": "undecided; 2/2 complete cases do not decide the conditional 80% prediction"},
            "P3": {"registered": 226, "successes": sum(r["L"][11] > r["L"][5] for r in p3),
                   "observed": len(p3), "unknown": len(rows) - len(p3),
                   "required_successes": 204, "verdict": "undecided for registered denominator"}},
        "errors": errors, "no_observed_true_values": no_values,
        "incomplete_ray_reference_ids": [r["idx"] for r in rows if r["status"] == "incomplete_ray_reference"],
        "depth_at_most5": sum(r["depth"] <= 5 for r in rows),
        "shortened_evidence": shortened_evidence,
        "four_misdescribed_profiles": [r for r in shortened_evidence if r["idx"] in (269, 302, 642, 908)],
        "row_issues": issues, "controls": controls,
    }
    assert all(controls.values()), {k: v for k, v in controls.items() if not v}
    OUTPUT.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"output": str(OUTPUT.relative_to(ROOT)), "controls": len(controls),
                      "all_controls_pass": True, "statuses": computed_summary["status"],
                      "shortened": len(short), "depth12_shortened": len([r for r in depth12 if r["shortened"]]),
                      "ge8_shortened": len([r for r in ge8 if r["shortened"]])}, sort_keys=True))


if __name__ == "__main__":
    main()
