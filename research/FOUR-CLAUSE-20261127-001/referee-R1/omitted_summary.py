"""Recount the omitted-stage results, keeping stage and start weightings distinct."""

from collections import Counter
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def read(path):
    return [json.loads(line) for line in path.read_text().splitlines()]


def summary(rows):
    patterns = [p for s in rows for p in s["patterns"]]
    roles = [u for p in patterns for u in p["qualifying_roles"]]
    return {
        "stages": len(rows), "distinct_starts": len({s["start"] for s in rows}),
        "stages_with_a_qualifying_role": sum(s["first_step"] is not None for s in rows),
        "stages_with_a_birth_essential_role": sum(s["first_step_needing_a_birth"] is not None for s in rows),
        "signed_absent_word_candidates": sum(s["peel_counts"][0] for s in rows),
        "signed_candidates_after_disjointness": sum(s["peel_counts"][-1] for s in rows),
        "structural_patterns": len(patterns),
        "patterns_with_four_genuine_bonds": sum(p["four_genuine_lower_bonds"] for p in patterns),
        "qualifying_roles": len(roles),
        "qualifying_roles_by_upper_word_count": Counter(len(u["upper_words"]) for u in roles),
        "qualifying_roles_by_number_of_individually_needed_births": Counter(len(u["birth_law_deletions"]) for u in roles),
        "qualifying_roles_by_number_of_individually_needed_initial_laws": Counter(len(u["initial_law_deletions"]) for u in roles),
    }


def main():
    rows = read(HERE / "omitted_stages.jsonl")
    archive = [r for f in sorted((HERE.parent / "out").glob("four_*.jsonl")) for r in read(f)]
    source = {int(r["start"].split()[1]): r["rounds"] for r in archive}
    omitted = {(i, row["round"]) for i, r in source.items() for row in r if row.get("not read")}
    assert len(rows) == len(omitted) == 211
    assert {(r["start"], r["round"]) for r in rows} == omitted
    assert all(r["completed_all_or_found_birth_step"] and len(r["patterns"]) == r["structural_patterns_tested"] for r in rows)
    hits = {r["start"] for r in rows if r["first_step_needing_a_birth"]}
    archived_hits = {i for i, r in source.items() if any(row.get("a birth needed, proper, free, not read at one lower bond", 0)
                                                          for row in r)}
    studied = {i for i, r in source.items() if any(row["round"] and not row.get("not read") for row in r)}
    grown = {i for i, r in source.items() if any(row["round"] for row in r)}
    union = hits | archived_hits
    controls = json.loads((HERE / "omitted_controls.json").read_text())
    global_checks = json.loads((HERE / "omitted_global.json").read_text())
    screened = {(r["start"], r["round"]):r for r in read(HERE / "omitted_screen.jsonl")}
    assert all(screened[s["start"], s["round"]]["peel_counts"] == s["peel_counts"] for s in rows)
    assert all(bool(screened[s["start"], s["round"]]["structural_patterns_tested"]) == bool(s["patterns"]) for s in rows)
    data = {
        "weighting": "Each omitted stage counted once; separate counts count each listed census start once.",
        "omitted": summary(rows),
        "omitted_by_round": {t: summary([r for r in rows if r["round"] == t]) for t in (1, 2)},
        "omitted_by_distinctions": {
            n: {"stages": len(rn), "positive": sum(r["first_step"] is not None for r in rn)}
            for n in sorted({r["distinctions"] for r in rows})
            for rn in [[r for r in rows if r["distinctions"] == n]]
        },
        "positive_omitted_stages": [
            {"census_entry": r["start"], "round": r["round"],
             "initial_knot_sizes": [len(k) for k in r["source_supports"][:r["source_knots"]]],
             "knots": r["knots"], "distinctions": r["distinctions"], "patterns": len(r["patterns"]),
             "qualifying_roles": sum(len(p["qualifying_roles"]) for p in r["patterns"])}
            for r in rows if r["first_step"]
        ],
        "start_denominators": {
            "frozen_positive_read_starts_and_starts_with_a_grown_stage_read": [len(archived_hits), len(studied)],
            "after_reading_all_stages_for_the_same_start_denominator": [len(union & studied), len(studied)],
            "all_starts_reaching_one_or_more_grown_stages": [len(union), len(grown)],
            "all_600_sampled_starts": [len(union), len(source)],
            "positive_starts_among_starts_with_at_least_one_omitted_stage":
                [len({i for i, _ in omitted} & union), len({i for i, _ in omitted})],
            "archived_positive_census_entries": sorted(archived_hits),
            "new_positive_census_entries": sorted(hits),
        },
        "structural_validation": {
            "directly_tested_controls": len(controls["direct_projection_cases"]),
            "omitted_genuine_signed_bond_words_in_all_controls": sum(
                r["genuine_words_omitted"] for r in controls["direct_projection_cases"].values()),
            "positives_with_stronger_all_stage_bond_check": {
                r["start"]: {"upper_functions": r["functions_tested"],
                             "determined_upper_functions": r["functions_determined_at_a_stage_bond"],
                             "planted_determining_bonds": len(r["positive_control"]["determining_stage_bonds"])}
                for r in global_checks},
        },
        "full_run_stage_seconds_summed": round(sum(s["elapsed_seconds"] for s in rows), 3),
        "full_run_process_peak_KiB": max(s["process_peak_KiB"] for s in rows),
    }
    (HERE / "omitted_summary.json").write_text(json.dumps(data, indent=2) + "\n")


if __name__ == "__main__":
    main()
