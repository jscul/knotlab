"""Independent read-only reconciliation of BOND-DEPTH's existing JSON records.

Run from the repository root with .venv/bin/python -B.  The producer is not
imported.  Its dlang dependency is reused ONLY to recover the declared cohort
from the antecedent source records, not to calculate or classify any L value.
The only file written is record_audit.json beside this script.
"""

from __future__ import annotations

import copy
import gzip
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import resource
import sys
import time
from collections import Counter, defaultdict


ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
BASE = ROOT / "artifacts/BOND-DEPTH-20261112-001A/BOND-DEPTH-20261112-001A-E001_spine_bonds"
PRODUCER = ROOT / "experiments/BOND-DEPTH-20261112-001A/BOND-DEPTH-20261112-001A-E001_spine_bonds"
SOURCE = ROOT / "artifacts/LIMIT-ONLY-20261112-001A/LIMIT-ONLY-20261112-001A-E001_limit_only"
DLANG = ROOT / "experiments/SHORT-DESC-20261112-001A/SHORT-DESC-20261112-001A-E001_description_census/dlang.py"
INF = 10**9
CAP = 20000


def rel(path):
    return str(path.relative_to(ROOT))


def digest(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return {"path": rel(path), "bytes": path.stat().st_size, "sha256": h.hexdigest()}


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def scientific(record):
    return {k: v for k, v in record.items() if k not in ("seconds", "helper")}


def fields_differ(left, right):
    missing = object()
    return sorted(k for k in left.keys() | right.keys() if left.get(k, missing) != right.get(k, missing))


def record_compare(left, right, ignore_metadata=False):
    if ignore_metadata:
        left, right = scientific(left), scientific(right)
    return {"equal": canonical(left) == canonical(right), "changed_fields": fields_differ(left, right)}


def read_rows(path):
    rows = []
    for line_no, line in enumerate(path.read_text().splitlines(), 1):
        if not line.strip():
            raise ValueError(f"Blank JSONL line at {rel(path)}:{line_no}")
        record = json.loads(line)
        rows.append({"path": rel(path), "line": line_no, "record": record})
    return rows


def recover_cohort(source_paths):
    """Independent source loader; shared dlang evaluates usual-limit liveness."""
    spec = importlib.util.spec_from_file_location("bond_record_audit_dlang", DLANG)
    lib = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(lib)
    antecedents = []
    for path in source_paths:
        with gzip.open(path, "rt") as stream:
            for line in stream:
                record = json.loads(line)
                if record.get("limit_only"):
                    antecedents.append(record["defs"])
    expected = {}
    for idx, defs in enumerate(antecedents):
        if len(defs) != 1:
            continue
        k, own_count, calls = defs[0]
        calls = [(callee, tuple(args)) for callee, args in calls]
        if any(callee == "SELF" and sorted(args) == [0, 1, 2] for callee, args in calls):
            calls = calls + [("K", (0, 1, 2))]
        usual = [(k, own_count, calls)]
        _, _, limit = lib.depth_sequence(usual, lib.TOP)
        if bool(lib.relations(usual, limit)[-1].any()):
            expected[idx] = own_count
    return expected, len(antecedents)


def classify(record):
    if record.get("unfinished") or not record["L"]:
        return "unfinished"
    if all(value >= INF for value in record["L"]):
        return "no_ray_bond_observed"
    if record["rate"] is None:
        return "undetermined_within_30"
    return "bounded_label" if record["rate"]["gain"] == 0 else "growing_label"


def ids(rows):
    return sorted(record["idx"] for record in rows)


def cohort_group(rows):
    return {"count": len(rows), "idx": ids(rows)}


def cycle(record):
    rate = record["rate"]
    return record["L"][rate["from_s"] - 1 : rate["from_s"] - 1 + rate["period"]]


def minimal_period(word):
    for period in range(1, len(word) + 1):
        if len(word) % period == 0 and all(v == word[i % period] for i, v in enumerate(word)):
            return word[:period]
    raise AssertionError("Every finite word has its full length as a period")


def fraction(numerator, denominator):
    return {"numerator": numerator, "denominator": denominator, "share": numerator / denominator}


def main():
    started = time.monotonic()
    cpu_started = time.process_time()
    if not sys.dont_write_bytecode:
        raise RuntimeError("Use Python -B to prevent bytecode writes outside the assigned output")
    raw_paths = sorted((BASE / "raw").glob("*.jsonl"))
    source_paths = sorted(SOURCE.glob("sample_*.jsonl.gz"))
    input_paths = raw_paths + [BASE / name for name in ("runs_merged.jsonl", "validation.json", "summary.json")]
    input_paths += [PRODUCER / name for name in ("census.py", "helper_after_start.py", "contract.json", "identity.json")]
    input_paths += [ROOT / "research/BOND-DEPTH-20261112-001" / name for name in ("preregistration.md", "bond_depth.md")]
    input_paths += [DLANG, ROOT / "experiments/LIMIT-STATE-20261112-001A/LIMIT-STATE-20261112-001A-E001_limit_states/census.py"] + source_paths
    before = [digest(path) for path in input_paths]
    raw = [item for path in raw_paths for item in read_rows(path)]
    merged_items = read_rows(BASE / "runs_merged.jsonl")
    merged = [item["record"] for item in merged_items]
    summary = json.loads((BASE / "summary.json").read_text())
    validation = json.loads((BASE / "validation.json").read_text())
    expected, antecedent_count = recover_cohort(source_paths)
    grouped = defaultdict(list)
    for item in raw:
        grouped[item["record"]["idx"]].append(item)
    finished = [r for r in merged if not r.get("unfinished")]
    unfinished = [r for r in merged if r.get("unfinished")]
    merged_by_id = {r["idx"]: r for r in merged}
    raw_ids, merged_ids, expected_ids = set(grouped), set(merged_by_id), set(expected)
    classes = Counter(map(classify, merged))
    unknown = [r for r in merged if classify(r) == "undetermined_within_30"]
    full = [r for r in unknown if len(r["L"]) == 30]
    capped = [r for r in unknown if r["states"] > CAP]
    rising = [r for r in full if r["L"][-1] > r["L"][0]]
    flat = [r for r in full if r["L"][-1] == r["L"][0]]
    late_rising = [r for r in full if r["L"][-1] > r["L"][19]]
    early_only = [r for r in rising if r["L"][-1] == r["L"][19]]
    bounded = [r for r in merged if classify(r) == "bounded_label"]
    no_bond = [r for r in merged if classify(r) == "no_ray_bond_observed"]

    duplicates = []
    diff_fields = Counter()
    duplicate_provenance = Counter()
    scientific_mismatches = []
    for idx, group in sorted(grouped.items()):
        if len(group) == 1:
            continue
        kinds = {"helper" if "helper" in item["record"] else "original" for item in group}
        duplicate_provenance["original_and_helper" if len(kinds) == 2 else next(iter(kinds)) + "_only"] += 1
        anchor = group[0]["record"]
        compared = []
        for item in group[1:]:
            full_diff = record_compare(anchor, item["record"])
            science_diff = record_compare(anchor, item["record"], True)
            diff_fields.update(full_diff["changed_fields"])
            compared.append({"path": item["path"], "line": item["line"], "full": full_diff, "scientific": science_diff})
            if not science_diff["equal"]:
                scientific_mismatches.append({"idx": idx, **compared[-1]})
        duplicates.append({
            "idx": idx,
            "multiplicity": len(group),
            "records": [{"path": item["path"], "line": item["line"], "seconds": item["record"]["seconds"], "helper": item["record"].get("helper")} for item in group],
            "comparisons_with_first": compared,
        })

    def selected_by(order, first=False):
        selection = {}
        for item in order:
            r = item["record"]
            if first:
                selection.setdefault(r["idx"], r)
            else:
                selection[r["idx"]] = r
        return selection

    def mismatches(selection):
        return [idx for idx, record in sorted(selection.items()) if merged_by_id.get(idx) != record]

    first_sorted = selected_by(raw, first=True)
    last_sorted = selected_by(raw)
    reverse_files = [item for path in reversed(raw_paths) for item in raw if item["path"] == rel(path)]
    last_reverse = selected_by(reverse_files)
    raw_full_multiset = Counter(canonical(item["record"]) for item in raw)
    merged_full_multiset = Counter(canonical(record) for record in finished)
    raw_science_multiset = Counter(canonical(scientific(item["record"])) for item in raw)
    merged_science_multiset = Counter(canonical(scientific(record)) for record in finished)
    selected_sources = []
    dropped = []
    for idx, group in sorted(grouped.items()):
        winners = [item for item in group if item["record"] == merged_by_id.get(idx)]
        selected_sources.append({"idx": idx, "sources": [{"path": item["path"], "line": item["line"]} for item in winners]})
        for item in group:
            if item not in winners:
                dropped.append({"idx": idx, "path": item["path"], "line": item["line"], "record_sha256": hashlib.sha256(canonical(item["record"]).encode()).hexdigest()})

    rate_issues = []
    for r in finished:
        q = r["rate"]
        if q and (q["period"] <= 0 or q["from_s"] < 1 or q["from_s"] + q["period"] != len(r["L"]) or q["gain"] < 0 or r["L"][q["from_s"] - 1] != r["L"][-1] - q["gain"]):
            rate_issues.append(r["idx"])
    tail_groups = defaultdict(list)
    no_finite_tail, variable_tail, constant_tail = [], [], []
    for r in bounded:
        tail = cycle(r)
        tail_groups[canonical(tail)].append(r["idx"])
        if all(value >= INF for value in tail):
            no_finite_tail.append(r)
        elif len(set(tail)) > 1:
            variable_tail.append(r)
        else:
            constant_tail.append(r)
    finite_tail = [r for r in bounded if all(value < INF for value in cycle(r))]
    tail_details = [{"idx": r["idx"], "L": r["L"], "rate": r["rate"], "recurring_word": cycle(r), "minimal_word": minimal_period(cycle(r)), "observed_minimum": min(r["L"]), "tail_minimum": min(cycle(r)), "tail_maximum": max(cycle(r))} for r in bounded + no_bond]

    # The negative control changes an L value in memory; source files are untouched.
    fixture = raw[0]["record"]
    changed_value = copy.deepcopy(fixture)
    changed_value["L"][0] += 1
    changed_timing = copy.deepcopy(fixture)
    changed_timing["seconds"] += 1
    controls = {
        "identity_accepts_full": record_compare(fixture, copy.deepcopy(fixture))["equal"],
        "identity_accepts_scientific": record_compare(fixture, copy.deepcopy(fixture), True)["equal"],
        "changed_L_rejects_full": not record_compare(fixture, changed_value)["equal"],
        "changed_L_rejects_scientific": not record_compare(fixture, changed_value, True)["equal"],
        "changed_L_fields": record_compare(fixture, changed_value, True)["changed_fields"],
        "changed_seconds_rejects_full": not record_compare(fixture, changed_timing)["equal"],
        "changed_seconds_accepts_scientific": record_compare(fixture, changed_timing, True)["equal"],
        "fixture_idx": fixture["idx"],
    }
    summary_recomputed = {
        "families": len(expected),
        "bounded_exact": classes["bounded_label"],
        "growing_exact": classes["growing_label"],
        "undetermined_within_30": len(unknown),
        "undetermined_full_30": len(full),
        "undetermined_growing_within_30": len(rising),
        "no_ray_bond": len(no_bond),
        "unfinished": len(unfinished),
    }
    summary_mismatches = {key: {"stored": summary.get(key), "recomputed": value} for key, value in summary_recomputed.items() if summary.get(key) != value}
    original = [item for item in raw if "helper" not in item["record"]]
    helpers = [item for item in raw if "helper" in item["record"]]
    after = [digest(path) for path in input_paths]
    changed_inputs = [a["path"] for a, b in zip(before, after) if a != b]
    expected_l_mismatches = [{"idx": r["idx"], "expected_l": expected.get(r["idx"]), "stored_l": r.get("l")} for r in finished if r.get("l") != expected.get(r["idx"])]
    assert all(controls[k] for k in controls if k not in ("fixture_idx", "changed_L_fields"))
    assert not changed_inputs
    assert len(merged) == len(expected) == 664
    assert len(raw) == len(finished) + len(dropped) == 831
    assert sum(classes.values()) == len(merged)
    assert len(unknown) == len(full) + len(capped)
    assert len(full) == len(rising) + len(flat)
    assert len(bounded) == len(finite_tail) + len(no_finite_tail)
    assert not scientific_mismatches and not summary_mismatches
    assert expected_ids == merged_ids and expected_ids - raw_ids == set(ids(unfinished))

    result = {
        "schema_version": 1,
        "scope_kind": "epic",
        "scope_id": "BOND-DEPTH-20261112-001",
        "audit": "raw and merged record reconciliation; no DP replay",
        "thread_id": os.environ.get("CODEX_THREAD_ID"),
        "invocation": ".venv/bin/python -B research/BOND-DEPTH-20261112-001/referee-R1/codex/audit_records.py",
        "independence": {"producer_imported": False, "shared_library": rel(DLANG), "shared_library_use": "Cohort reconstruction only: depth_sequence and relations on usual definitions; no recorded L recomputation", "classification_and_comparators": "Independent code in this script; no producer summarize, run_family or extrapolate calls"},
        "input_manifest": before,
        "inputs_unchanged_after_audit": not changed_inputs,
        "changed_input_paths": changed_inputs,
        "cohort": {"antecedent_limit_only_families": antecedent_count, "expected_count": len(expected), "expected_idx": sorted(expected), "finished_count": len(finished), "unfinished_count": len(unfinished), "unfinished_idx": ids(unfinished), "expected_absent_from_raw_idx": sorted(expected_ids - raw_ids), "unexpected_raw_idx": sorted(raw_ids - expected_ids), "expected_absent_from_merged_idx": sorted(expected_ids - merged_ids), "unexpected_merged_idx": sorted(merged_ids - expected_ids), "merged_duplicate_idx": [idx for idx, count in Counter(r["idx"] for r in merged).items() if count > 1], "l_mismatches": expected_l_mismatches},
        "raw": {"count": len(raw), "unique_idx": len(grouped), "original_count": len(original), "original_unique_idx": len({item["record"]["idx"] for item in original}), "helper_count": len(helpers), "helper_unique_idx": len({item["record"]["idx"] for item in helpers}), "per_file": [{"path": rel(path), "records": sum(item["path"] == rel(path) for item in raw)} for path in raw_paths]},
        "duplicates": {"idx_count": len(duplicates), "extra_records": len(raw) - len(grouped), "multiplicity_histogram": dict(sorted(Counter(len(group) for group in grouped.values()).items())), "provenance_group_counts": dict(duplicate_provenance), "changed_fields_comparison_counts": dict(diff_fields), "scientific_mismatches": scientific_mismatches, "full_identical_groups": sum(all(item["record"] == group[0]["record"] for item in group) for group in grouped.values() if len(group) > 1), "scientific_fields_exclude_exactly": ["seconds", "helper"], "groups": duplicates},
        "merge": {"finished_records_not_exact_raw_rows": [r["idx"] for r in finished if canonical(r) not in raw_full_multiset], "raw_idx_missing_from_merged": sorted(raw_ids - merged_ids), "full_multiset_raw_excess_count": sum((raw_full_multiset - merged_full_multiset).values()), "full_multiset_merged_excess_count": sum((merged_full_multiset - raw_full_multiset).values()), "scientific_multiset_raw_excess_count": sum((raw_science_multiset - merged_science_multiset).values()), "scientific_multiset_merged_excess_count": sum((merged_science_multiset - raw_science_multiset).values()), "scientific_unique_sets_equal": set(raw_science_multiset) == set(merged_science_multiset), "first_by_idx_lexicographic_file_order_mismatch_idx": mismatches(first_sorted), "last_by_idx_lexicographic_file_order_mismatch_idx": mismatches(last_sorted), "last_by_idx_reverse_lexicographic_file_order_mismatch_idx": mismatches(last_reverse), "ordering_note": "Merged finished records equal first-by-idx in ascending filename order, equivalently last-by-idx in descending filename order. Chronological completion order is not recorded; no chronological last-write claim is made.", "selected_original_records": sum("helper" not in r for r in finished), "selected_helper_records": sum("helper" in r for r in finished), "selected_sources": selected_sources, "discarded_raw_metadata_records": dropped},
        "classification": {"independent_counts": dict(classes), "conditional_tail_counts": {"finite_bounded": len(finite_tail), "no_eventual_ray_bond": len(no_finite_tail) + len(no_bond), "undetermined": len(unknown), "unfinished": len(unfinished)}, "stored_summary": summary, "recomputed_summary_with_producer_label_meanings": summary_recomputed, "summary_mismatches": summary_mismatches, "rate_metadata_internal_inconsistency_idx": rate_issues, "no_ray_bond_observed_idx": ids(no_bond), "unfinished_vacuously_all_INF_idx": [r["idx"] for r in unfinished if all(v >= INF for v in r["L"])], "producer_summarize_caveat": "On merged placeholders, all([]) would classify all 11 unfinished as no ray bond; states=None would also raise TypeError at states>STATE_CAP. On raw glob without deduplication it counts 831, not 664. Stored summary thus requires a custom merge/aggregation path absent from the supplied producer scripts; its numbers are independently reproducible with explicit unfinished handling."},
        "undetermined": {"total": cohort_group(unknown), "full_30": cohort_group(full), "capped": cohort_group(capped), "full_30_and_capped_idx": sorted(set(ids(full)) & set(ids(capped))), "residual_neither_full_nor_capped_idx": sorted(set(ids(unknown)) - set(ids(full)) - set(ids(capped))), "full_30_endpoint_rise_L30_gt_L1": cohort_group(rising), "full_30_endpoint_flat_L30_eq_L1": cohort_group(flat), "full_30_endpoint_fall_idx": [r["idx"] for r in full if r["L"][-1] < r["L"][0]], "full_30_any_decrease_idx": [r["idx"] for r in full if any(a > b for a, b in zip(r["L"], r["L"][1:]))], "full_30_last_ten_rise_L30_gt_L20": cohort_group(late_rising), "endpoint_rise_but_flat_s20_to_s30": {**cohort_group(early_only), "examples": [{"idx": r["idx"], "L": r["L"]} for r in early_only[:5]]}, "endpoint_delta_histogram": dict(sorted(Counter(r["L"][-1] - r["L"][0] for r in full).items())), "last_ten_delta_histogram": dict(sorted(Counter(r["L"][-1] - r["L"][19] for r in full).items())), "capped_endpoint_rise": cohort_group([r for r in capped if r["L"][-1] > r["L"][0]]), "capped_endpoint_flat": cohort_group([r for r in capped if r["L"][-1] == r["L"][0]]), "rising_wording_caveat": "240 means only L(30)>L(1), not growth throughout the final ten levels: 26 of 240 are constant from s20 through s30. All 403 full-depth undetermined sequences are nondecreasing. The 55/71/29 counts correspond to endpoint increments 29/15/10, not certified eventual rates."},
        "bounded_tail_analysis": {"conditional_authority": "Recurrence words derived from recorded rate metadata, conditional on correctness of the DP and repeat detection; no DP replay in this lane", "observed_minimum_histogram": dict(sorted(Counter(min(r["L"]) for r in bounded).items())), "recorded_tail_words": [{"word": json.loads(word), "count": len(group), "idx": group} for word, group in sorted(tail_groups.items())], "finite_at_every_recurring_depth": cohort_group(finite_tail), "eventually_no_ray_bond_after_early_finite_bonds": cohort_group(no_finite_tail), "nonconstant_finite_recurring_words": cohort_group(variable_tail), "constant_finite_recurring_words": cohort_group(constant_tail), "constant_tail_value_histogram": dict(sorted(Counter(cycle(r)[0] for r in constant_tail).items())), "finite_tail_minimum_histogram": dict(sorted(Counter(min(cycle(r)) for r in finite_tail).items())), "finite_tail_maximum_histogram": dict(sorted(Counter(max(cycle(r)) for r in finite_tail).items())), "mixed_finite_and_INF_recurring_words_idx": [r["idx"] for r in bounded if any(v < INF for v in cycle(r)) and any(v >= INF for v in cycle(r))], "all_gain_zero_records_including_always_no_bond": len(bounded) + len(no_bond), "details": tail_details, "headline_caveat": "204 zero-gain labels include 10 with only early finite bonds and an all-INF tail. Only 194 recorded zero-gain cases have finite recurring bonds. Of those, 187 settle to a single size (17 at 2, 167 at 3, 3 at 4) and 7 vary periodically between 2 and 3. The 173/30/1 headline records observed minima, not settled limits."},
        "P1": {"preregistered_population": len(expected), "majority_threshold": (len(expected) + 1) // 2, "detected_label_share_all_families": fraction(len(bounded), len(expected)), "detected_label_share_finished": fraction(len(bounded), len(finished)), "finite_tail_bounded_share_all_families": fraction(len(finite_tail), len(expected)), "finite_tail_bounded_share_finished": fraction(len(finite_tail), len(finished)), "unresolved_families": len(unknown) + len(unfinished), "conditional_finite_bounded_share_range": {"lower": fraction(len(finite_tail), len(expected)), "upper": fraction(len(finite_tail) + len(unknown) + len(unfinished), len(expected))}, "additional_bounded_needed_for_majority_using_recorded_labels": (len(expected) + 1) // 2 - len(bounded), "additional_bounded_needed_for_majority_using_finite_tails": (len(expected) + 1) // 2 - len(finite_tail), "interpretation": "The procedure detected fewer than half as bounded; it does not establish that fewer than half actually have bounded finite least ray bonds because 458 families remain unresolved. P1 as a claim about the underlying property is undecided, not falsified by treating missing classifications as nonbounded."},
        "validation_file_accounting_only": {"stored": validation, "cases_equal_agree_plus_disagree": validation["cases"] == validation["agree"] + len(validation["disagree"]), "chains_match_4_through_9": validation["chains"] == [list(range(4, 10)), list(range(4, 10))], "not_replayed_in_this_lane": True},
        "controls": controls,
        "limitations": ["No independent DP or SAT recomputation in this record-audit lane.", "Shared dlang semantics are used only to reconstruct the 664 expected family indices.", "Raw records contain elapsed worker timings but no start/finish timestamps or termination logs; the reported three-and-a-half-hour stop and chronological winner order cannot be verified from these files.", "Coverage reconciliation proves accounting, not correctness of an L value or eventual classification.", "Exactly matching scientific duplicate fields corroborates unchanged outputs but does not independently validate the shared producing implementation.", "Tail classifications above are conditional deductions from recorded repeats, not new theorem evidence."],
        "resources": {"wall_seconds": round(time.monotonic() - started, 4), "process_cpu_seconds": round(time.process_time() - cpu_started, 4), "peak_rss_kib_linux": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss},
    }
    output = HERE / "record_audit.json"
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"output": rel(output), "raw": len(raw), "unique_raw": len(grouped), "merged": len(merged), "classes": dict(classes), "scientific_duplicate_mismatches": len(scientific_mismatches), "finite_tail_bounded": len(finite_tail), "early_finite_then_no_tail": ids(no_finite_tail), "full30_endpoint_rise": len(rising), "last_ten_rise": len(late_rising), "controls_pass": True, "resources": result["resources"]}, sort_keys=True))


if __name__ == "__main__":
    main()
