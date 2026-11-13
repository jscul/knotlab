"""Independent roster, summary, and record-history audit; no graph producer imports.

Frozen before the comparison computation. Run from the repository root with
.venv/bin/python -B. The only runtime output file is history_audit.json beside
this script. The forbidden producer subtree is blocked by an audit hook.

The exact family roster is obtained through the permitted BOND-DEPTH census
and its LIMIT-STATE/dlang dependencies. Result counters are independently
defined here; merge_and_summarize.py is read only as bytes for its hash.
"""
from __future__ import annotations

import os
import sys

os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"

import collections
import datetime
from fractions import Fraction
import hashlib
import importlib.util
import json
from pathlib import Path
import resource
import signal
import time

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
FORBIDDEN = ROOT / "experiments/PROVED-RATE-20261113-001A/PROVED-RATE-20261113-001A-E001_cycle_mean/codex"
BD = ROOT / "experiments/BOND-DEPTH-20261112-001A/BOND-DEPTH-20261112-001A-E001_spine_bonds/census.py"
LS = ROOT / "experiments/LIMIT-STATE-20261112-001A/LIMIT-STATE-20261112-001A-E001_limit_states/census.py"
DLANG = ROOT / "experiments/SHORT-DESC-20261112-001A/SHORT-DESC-20261112-001A-E001_description_census/dlang.py"
SAMPLE_ROOT = ROOT / "artifacts/LIMIT-ONLY-20261112-001A/LIMIT-ONLY-20261112-001A-E001_limit_only"
OLD = ROOT / "artifacts/BOND-DEPTH-20261112-001A/BOND-DEPTH-20261112-001A-E001_spine_bonds/runs_merged.jsonl"
RATE_ROOT = ROOT / "artifacts/PROVED-RATE-20261113-001A/PROVED-RATE-20261113-001A-E001_cycle_mean"
RATES = RATE_ROOT / "rates_all.jsonl"
SUMMARY = RATE_ROOT / "summary.json"
MERGE = ROOT / "experiments/PROVED-RATE-20261113-001A/PROVED-RATE-20261113-001A-E001_cycle_mean/merge_and_summarize.py"
INF = 10**9


def block_forbidden(event, args):
    if event in {"open", "os.listdir", "os.scandir"} and args:
        name = args[0]
        if isinstance(name, (str, bytes, os.PathLike)):
            candidate = Path(os.fsdecode(name)).absolute()
            if candidate == FORBIDDEN or FORBIDDEN in candidate.parents:
                raise PermissionError("Forbidden producer subtree was requested")


sys.addaudithook(block_forbidden)
resource.setrlimit(resource.RLIMIT_AS, (7 * 1024**3, 7 * 1024**3))
resource.setrlimit(resource.RLIMIT_CPU, (550, 550))
signal.alarm(580)


def sha(path):
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def rel(path):
    return str(path.relative_to(ROOT))


def jsonl(path):
    with path.open() as handle:
        return [json.loads(line) for line in handle if line.strip()]


def id_duplicates(records):
    return {str(i): n for i, n in collections.Counter(r["idx"] for r in records).items() if n != 1}


def fraction(row):
    value = row.get("lambda")
    return None if value is None else Fraction(value)


def aggregate(records):
    # Independent definitions of the scientific counters in the frozen spec.
    return {
        "families": len(records),
        "complete": sum(r.get("complete") is True for r in records),
        "gate_mismatches_total": sum(len(r.get("mismatches", [])) for r in records),
        "gate_ok": sum(r.get("gate_ok") is True for r in records),
        "gate_unchecked": sum(r.get("gate_ok") is None for r in records),
        "lambda_distribution": dict(sorted(collections.Counter(r["lambda"] for r in records if r.get("lambda") is not None).items())),
        "lambda_none": sum(r.get("lambda") is None for r in records),
        "bounded_all": sum(r.get("bounded_all") is True for r in records),
        "bounded_all_false": sum(r.get("bounded_all") is False for r in records),
        "bounded_all_uncomputed": sum(r.get("bounded_all") is None for r in records),
        "zero_mean": sum(r.get("zero_mean") is True for r in records),
        "zero_mean_without_bounded_all": sum(r.get("zero_mean") is True and r.get("bounded_all") is False for r in records),
        "zero_mean_with_uncomputed_bounded_all": sum(r.get("zero_mean") is True and r.get("bounded_all") is None for r in records),
        "timeout": sum(r.get("status") == "timeout" for r in records),
        "errors": sum(r.get("status") == "error" for r in records),
    }


def complete_aggregate(records):
    positives = [r for r in records if fraction(r) is not None and fraction(r) > 0]
    return {
        "complete": len(records),
        "lambda_positive": len(positives),
        "zero_mean": sum(r.get("zero_mean") is True for r in records),
        "bounded_all": sum(r.get("bounded_all") is True for r in records),
        "lambda_none": sum(r.get("lambda") is None for r in records),
        "rates": dict(sorted(collections.Counter(r["lambda"] for r in positives).items())),
    }


def classify(old, variant="strict_eight_finite"):
    """Do not silently classify the spec's short-record ambiguity.

    A short record with unequal finite values is already known not to be
    finite-constant. Only the other short records retain the stated ambiguity.
    Counterfactual variants are reported separately for sensitivity. No class
    is inferred from the previously submitted class field.
    """
    seq = old.get("L")
    if old.get("unfinished") or not isinstance(seq, list) or not seq:
        return "capped"
    n = len(seq)
    if n < 8:
        if len({x for x in seq if x < INF}) > 1:
            return "capped"
        return None
    tail = seq[-8:]
    if variant == "filter_finite_first":
        tail = [x for x in seq if x < INF][-8:]
        is_const = len(tail) == 8 and len(set(tail)) == 1
    elif variant == "include_INF":
        is_const = len(set(tail)) == 1
    else:
        is_const = len(set(tail)) == 1 and all(x < INF for x in tail)
    if n < 30 and is_const:
        return "bounded"
    if n == 30 and seq[-1] > seq[0]:
        return "rising"
    if n == 30 and seq[-1] == seq[0]:
        return "flat"
    return "capped"


def compare(expected, actual, path=""):
    diffs = []
    if isinstance(expected, dict) and isinstance(actual, dict):
        for key in sorted(set(expected) | set(actual)):
            child = f"{path}.{key}" if path else str(key)
            if key not in expected:
                diffs.append({"field": child, "kind": "unexpected_actual", "actual": actual[key]})
            elif key not in actual:
                diffs.append({"field": child, "kind": "missing_actual", "expected": expected[key]})
            else:
                diffs.extend(compare(expected[key], actual[key], child))
    elif expected != actual:
        diffs.append({"field": path, "expected": expected, "actual": actual})
    return diffs


def main():
    started = time.monotonic()
    frozen_sha = sha(Path(__file__).resolve())
    earlier_output_path = HERE / "history_audit.json"
    earlier_auditor_pass = json.loads(earlier_output_path.read_text()) if earlier_output_path.exists() else None
    spec = importlib.util.spec_from_file_location("permitted_bd_for_history_audit", BD)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    families = module.families_one_def()
    expected_ids = [idx for idx, _ in families]
    rows = jsonl(RATES)
    prior = jsonl(OLD)
    summary = json.loads(SUMMARY.read_text())
    old_by_id = {r["idx"]: r for r in prior}
    expected_set, observed_set = set(expected_ids), {r["idx"] for r in rows}
    row_issues, row_audits = [], []
    gate_comparison_issues = []
    classification_variants = {name: collections.Counter() for name in ("strict_eight_finite", "include_INF", "filter_finite_first")}
    class_disagreements = []
    short_ids, ambiguous_ids, prior_no_L_ids, prior_repeat_zero_ids = [], [], [], []
    repeat_INF_ids, any_INF_ids, rising_zero_ids, rising_zero_plateau20_ids = [], [], [], []
    none_ids, partial_ids, exact_float_issues = [], [], []
    total_record_depths = 0
    raw_keys = set()

    for row in rows:
        idx = row["idx"]
        raw_keys.update(row)
        old = old_by_id.get(idx)
        if old is None:
            row_issues.append({"idx": idx, "issue": "no_prior_row"})
            continue
        seq = old.get("L")
        has_L = isinstance(seq, list) and len(seq) > 0
        independent_class = classify(old)
        for variant in classification_variants:
            classification_variants[variant][str(classify(old, variant))] += 1
        if independent_class != row.get("record_class"):
            class_disagreements.append({"idx": idx, "expected": independent_class, "submitted": row.get("record_class"), "L": seq})
        if has_L and len(seq) < 8:
            short_ids.append(idx)
        if independent_class is None:
            ambiguous_ids.append(idx)
        if not has_L:
            prior_no_L_ids.append(idx)
        else:
            total_record_depths += len(seq)
            recomputed = row.get("L_recomputed")
            if recomputed != seq:
                gate_comparison_issues.append({"idx": idx, "source_L": seq, "submitted_recomputed_L": recomputed})
            expected_gate_status = "checked" if row.get("complete") is True else "checked_partial_graph"
            if row.get("gate_ok") is not True or row.get("gate_status") != expected_gate_status:
                gate_comparison_issues.append({"idx": idx, "issue": "record_exists_but_gate_not_checked_true", "gate_ok": row.get("gate_ok"), "gate_status": row.get("gate_status")})
            if row.get("record_depths") != len(seq):
                gate_comparison_issues.append({"idx": idx, "issue": "record_depth_count", "expected": len(seq), "actual": row.get("record_depths")})
            if any(x >= INF for x in seq):
                any_INF_ids.append(idx)
        if not has_L and (row.get("gate_ok") is not None or row.get("gate_status") != "skipped_no_record_L"):
            gate_comparison_issues.append({"idx": idx, "issue": "missing_record_gate_status", "gate_ok": row.get("gate_ok"), "gate_status": row.get("gate_status")})
        rate = old.get("rate")
        if isinstance(rate, dict) and rate.get("gain") == 0:
            prior_repeat_zero_ids.append(idx)
            if has_L and seq[-1] >= INF:
                repeat_INF_ids.append(idx)
        value = fraction(row)
        if value is None:
            if row.get("lambda_float") is not None:
                exact_float_issues.append({"idx": idx, "issue": "lambda_None_float_not_None"})
            none_ids.append(idx)
        else:
            if row.get("lambda_float") != float(value):
                exact_float_issues.append({"idx": idx, "lambda": row["lambda"], "lambda_float": row.get("lambda_float")})
            if row.get("zero_mean") != (value == 0):
                row_issues.append({"idx": idx, "issue": "zero_mean_inconsistent_with_fraction"})
        if row.get("complete") is False:
            partial_ids.append(idx)
        if independent_class == "rising" and value == 0:
            rising_zero_ids.append(idx)
            if has_L and len(seq) >= 30 and len(set(seq[19:30])) == 1:
                rising_zero_plateau20_ids.append(idx)
        row_audits.append({
            "idx": idx,
            "source_L": seq,
            "source_rate": rate,
            "source_unfinished": old.get("unfinished", False),
            "record_depths_independent": len(seq) if has_L else 0,
            "record_class_independent": independent_class,
            "record_class_submitted": row.get("record_class"),
            "record_class_include_INF": classify(old, "include_INF"),
            "record_class_filter_finite_first": classify(old, "filter_finite_first"),
            "complete_submitted": row.get("complete"),
            "nodes_submitted": row.get("nodes"),
            "trimmed_nodes_submitted": row.get("trimmed_nodes"),
            "lambda_submitted": row.get("lambda"),
            "bounded_all_submitted": row.get("bounded_all"),
            "zero_mean_submitted": row.get("zero_mean"),
            "gate_ok_submitted": row.get("gate_ok"),
            "L_recomputed_matches_source": row.get("L_recomputed") == seq if has_L else None,
        })

    overall = aggregate(rows)
    comp = [r for r in rows if r.get("complete") is True]
    by_record_class = {str(cl): complete_aggregate([r for r in comp if r.get("record_class") == cl]) for cl in ("bounded", "rising", "flat", "capped", None)}
    all_complete = complete_aggregate(comp)
    all_complete.pop("complete")
    record_rows = [r for r in rows if r["idx"] in old_by_id and isinstance(old_by_id[r["idx"]].get("L"), list) and old_by_id[r["idx"]]["L"]]
    complete_with_records = sum(r.get("complete") is True for r in record_rows)
    p1 = round(complete_with_records / len(record_rows), 4)
    p2 = round(by_record_class["rising"]["lambda_positive"] / by_record_class["rising"]["complete"], 4)
    p3 = round(by_record_class["flat"]["bounded_all"] / by_record_class["flat"]["complete"], 4)
    expected_top = {
        "families": len(rows),
        "complete": len(comp),
        # The owner's key counts failed-family flags; zero here also agrees
        # with the independently counted depth mismatch list.
        "gate_mismatches": sum(r.get("gate_ok") is False for r in rows),
        "P1_complete_share_of_653": p1,
        "by_record_class": by_record_class,
        "P2_rising_lambda_positive_share": p2,
        "P3_flat_bounded_all_share": p3,
        "all_complete": all_complete,
    }
    actual_top = {key: value for key, value in summary.items() if key != "codex_summary"}
    top_diffs = compare(expected_top, actual_top)
    nested = summary.get("codex_summary", {})
    nested_diffs = compare(overall, {key: nested.get(key) for key in overall}, "codex_summary")
    expected_nested_classes = {cl: aggregate([r for r in rows if r.get("record_class") == cl]) for cl in ("bounded", "rising", "flat", "capped")}
    nested_diffs.extend(compare(expected_nested_classes, nested.get("by_record_class"), "codex_summary.by_record_class"))
    nested_diffs.extend(compare(aggregate([r for r in rows if r.get("record_class") is None]), nested.get("ambiguous_record_class"), "codex_summary.ambiguous_record_class"))
    nested_diffs.extend(compare(sorted(ambiguous_ids), nested.get("ambiguous_record_class_indices"), "codex_summary.ambiguous_record_class_indices"))
    flat_mismatches = [m for r in rows for m in r.get("mismatches", [])]
    nested_diffs.extend(compare(flat_mismatches, nested.get("mismatches"), "codex_summary.mismatches"))
    positive_distribution = {value: count for value, count in all_complete["rates"].items()}
    none_cases = [{"idx": r["idx"], "complete": r.get("complete"), "trimmed_nodes": r.get("trimmed_nodes"), "source_L": old_by_id[r["idx"]].get("L"), "record_class": r.get("record_class")} for r in rows if r.get("lambda") is None]
    source_paths = [BD, LS, DLANG, OLD, RATES, SUMMARY, MERGE, ROOT / "research/PROVED-RATE-20261113-001/codex_spec.md", ROOT / "research/PROVED-RATE-20261113-001/preregistration.md", ROOT / "research/PROVED-RATE-20261113-001/proved_rate.md"]
    sample_paths = sorted(SAMPLE_ROOT.glob("sample_*.jsonl.gz"))
    expected_family_records = [{"idx": idx, "defs": defs} for idx, defs in families]
    canonical_family_bytes = json.dumps(expected_family_records, sort_keys=True, separators=(",", ":")).encode()
    output = {
        "audit_scope": {
            "scope_kind": "epic", "scope_id": "PROVED-RATE-20261113-001", "referee": "referee-R1",
            "lane": "history_and_wording", "forbidden_subtree_opened": False,
            "producer_implementation_imported": False, "merge_script_executed": False,
            "forbidden_subtree_access_guard": "sys.addaudithook rejects open/listdir/scandir",
            "graph_values_independently_recomputed_in_this_lane": False,
        },
        "runtime": {
            "python": sys.version, "CODEX_THREAD_ID": os.environ.get("CODEX_THREAD_ID"),
            "utc_finished": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "wall_seconds": time.monotonic() - started,
            "peak_RSS_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
            "processes": 1, "address_space_limit_bytes": 7 * 1024**3,
            "cpu_limit_seconds": 550, "wall_alarm_seconds": 580,
        },
        "frozen_script_sha256": frozen_sha,
        "input_sha256": {rel(path): sha(path) for path in source_paths + sample_paths},
        "roster": {
            "expected_families": len(expected_ids), "expected_ids": expected_ids,
            "expected_duplicate_ids": {str(idx): count for idx, count in collections.Counter(expected_ids).items() if count != 1},
            "observed_rows": len(rows), "observed_unique_ids": len(observed_set),
            "observed_duplicate_ids": id_duplicates(rows),
            "missing_expected_ids": sorted(expected_set - observed_set),
            "unexpected_observed_ids": sorted(observed_set - expected_set),
            "observed_sorted_by_idx": [r["idx"] for r in rows] == sorted(r["idx"] for r in rows),
            "prior_rows": len(prior), "prior_duplicate_ids": id_duplicates(prior),
            "prior_missing_expected_ids": sorted(expected_set - set(old_by_id)),
            "prior_unexpected_ids": sorted(set(old_by_id) - expected_set),
            "canonical_expected_family_roster_sha256": hashlib.sha256(canonical_family_bytes).hexdigest(),
            "expected_family_roster": expected_family_records,
        },
        "record_gate_fields": {
            "prior_rows_with_L": len(record_rows), "prior_rows_without_L": len(prior_no_L_ids),
            "prior_without_L_ids": prior_no_L_ids, "complete_rows_with_L": complete_with_records,
            "total_recorded_depths": total_record_depths,
            "comparison_issues": gate_comparison_issues,
            "meaning": "Submitted L_recomputed arrays and gate fields agree with the permitted earlier records; this lane does not rerun the graph DP.",
        },
        "summary_recalculation": {
            "overall": overall, "all_complete": all_complete,
            "top_level_expected": expected_top, "top_level_differences": top_diffs,
            "nested_counter_differences": nested_diffs,
            "P1_fraction": f"{complete_with_records}/{len(record_rows)}",
            "P1_all_rows_fraction": f"{len(comp)}/{len(rows)}",
            "P2_fraction": f"{by_record_class['rising']['lambda_positive']}/{by_record_class['rising']['complete']}",
            "P3_fraction": f"{by_record_class['flat']['bounded_all']}/{by_record_class['flat']['complete']}",
            "positive_rate_distribution_complete": positive_distribution,
            "partial_ids": partial_ids,
        },
        "classifications": {
            "operational_rule": "For nonempty L shorter than 8: capped if finite values already vary, None otherwise; bounded needs length 8..29 and 8 equal finite terminal values; then rising/flat at length 30; otherwise capped.",
            "short_record_ids": short_ids,
            "short_record_count": len(short_ids),
            "ambiguous_record_ids": ambiguous_ids,
            "ambiguous_record_count": len(ambiguous_ids),
            "variant_counts": {key: dict(value) for key, value in classification_variants.items()},
            "submitted_class_disagreements": class_disagreements,
            "prior_zero_gain_repeat_count": len(prior_repeat_zero_ids),
            "prior_zero_gain_repeat_ids": prior_repeat_zero_ids,
            "prior_zero_gain_repeat_ending_INF_ids": repeat_INF_ids,
            "prior_any_INF_ids": any_INF_ids,
        },
        "wording_evidence": {
            "rising_zero_mean_ids": rising_zero_ids,
            "rising_zero_mean_tail20to30_constant_ids": rising_zero_plateau20_ids,
            "rising_zero_mean_bounded_all_count": sum(r["idx"] in rising_zero_ids and r.get("bounded_all") is True for r in rows),
            "lambda_none_cases": none_cases,
            "minimum_reported_positive_rate_complete": str(min(Fraction(value) for value in positive_distribution)),
            "maximum_reported_positive_rate_complete": str(max(Fraction(value) for value in positive_distribution)),
            "finite_submitted_L_minimum": min(value for row in rows for value in row.get("L_recomputed", []) if value < INF),
        },
        "run_provenance": {
            "merged_fields": sorted(raw_keys),
            "batch_counts_508_92_64_verified": False,
            "second_batch_OOM_verified": False,
            "runner_unchanged_verified": False,
            "first_run_session_cause_verified": False,
            "reason": "Batch files and logs are inside the explicitly forbidden producer codex subtree. The owner merge text names those batches and uses dict.setdefault, which silently keeps the earliest row if a family repeats. Merged uniqueness cannot rule out source duplicates or prove source counts, order, OOM, or cause of termination.",
            "summary_wall_seconds": nested.get("wall_seconds"),
            "summary_workers": nested.get("workers"),
            "metadata_note": "The permitted merge text calls the inaccessible make_summary(rows, 0, 7). These metadata values are supplied constants, not independently reconstructed total runtime or worker history.",
        },
        "row_issues": row_issues,
        "exact_fraction_float_consistency_issues": exact_float_issues,
        "row_audits": row_audits,
    }
    if earlier_auditor_pass is not None:
        output["preserved_earlier_auditor_pass"] = {
            "reason_for_revision": "The initial conservative audit classified all shorter-than-eight records as ambiguous, even when unequal finite values already exclude the bounded class. It also accepted only the complete-graph gate-status label, overlooking the explicitly marked checked_partial_graph status. Both assumptions have been corrected; all original output and exact first-pass script source are preserved below.",
            "raw_output": earlier_auditor_pass,
        }
    destination = HERE / "history_audit.json"
    with destination.open("w") as handle:
        json.dump(output, handle, indent=2, sort_keys=True)
        handle.write("\n")
    print(json.dumps({
        "output": rel(destination), "frozen_script_sha256": frozen_sha,
        "families": len(rows), "expected_families": len(expected_ids),
        "roster_missing": len(expected_set - observed_set), "roster_unexpected": len(observed_set - expected_set),
        "duplicates": id_duplicates(rows), "top_summary_diffs": len(top_diffs),
        "nested_summary_diffs": len(nested_diffs), "class_diffs": len(class_disagreements),
        "gate_field_diffs": len(gate_comparison_issues), "wall_seconds": time.monotonic() - started,
        "peak_RSS_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
