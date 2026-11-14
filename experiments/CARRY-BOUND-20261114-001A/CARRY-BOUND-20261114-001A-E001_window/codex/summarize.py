"""Summarize completed CARRY runner records without making new certificates.

Only the thread runs this CLI after its frozen runs.  Full mode refuses a
missing population record.  Gate-only mode accepts a smoke subset and emits
no P1--P5 observables.  P3 and witness attribution follow resolved A4 and A6.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from fractions import Fraction
import hashlib
import json
import math
from pathlib import Path
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))
import inputs
if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))
from longrun import load_results

STRATA = ("I", "T", "O", "X")
FEATURES = ("B", "widened_B", "tie", "other")
GROWTH_METHODS = ("G", "G2", "G2_live")
P3_DEFINITION = ("Among in-scope I families without a window bound on every repeating residue, "
                 "the family has no carried position sharing a knot with an own distinction on "
                 "every residue left without a window bound (A4).")
ATTRIBUTION_RULE = ("Per repeating residue, select the first of B, widened_B, tie, other present "
                    "in any tied least U witness. A bounded family takes the lowest-priority "
                    "reading needed by any of its repeating residues (A6).")


def _source(path):
    path = Path(path)
    if not path.is_absolute():
        path = ROOT / path
    path = path.resolve()
    if not path.is_relative_to(ROOT):
        raise ValueError("only repository source material is permitted")
    file = path / "results.jsonl" if path.is_dir() else path
    return {"path": str(file.relative_to(ROOT)), "sha256": inputs.digest(file)}, load_results(path)


def wilson(success, total):
    """Descriptive 95% Wilson score interval, accepting integer draw counts."""
    if not total:
        return None
    z = 1.959963984540054
    p = success / total
    denominator = 1 + z * z / total
    center = (p + z * z / (2 * total)) / denominator
    half = z * math.sqrt(p * (1 - p) / total + z * z / (4 * total * total)) / denominator
    return [max(0.0, center - half), min(1.0, center + half)]


def _share(success, total):
    return {"success": success, "total": total,
            "share": success / total if total else None, "wilson95": wilson(success, total)}


def _fraction(cell):
    return Fraction(cell["success"], cell["total"]) if cell["total"] else None


def _rates(rows, field, *, classification_complete=True):
    count_success = sum(row[field] is True for row in rows)
    weight_success = sum(row["weight"] for row in rows if row[field] is True)
    known = [row for row in rows if row[field] is not None]
    result = {"count": _share(count_success, len(rows)),
              "weight": _share(weight_success, sum(row["weight"] for row in rows)),
              "undecided_count": sum(row[field] is None for row in rows),
              "undecided_weight": sum(row["weight"] for row in rows if row[field] is None),
              "denominator_complete": classification_complete}
    if classification_complete:
        result["sensitivity_excluding_undecided"] = {
            "count": _share(sum(row[field] is True for row in known), len(known)),
            "weight": _share(sum(row["weight"] for row in known if row[field] is True),
                             sum(row["weight"] for row in known))}
    else:
        result["sensitivity_excluding_undecided"] = {
            "status": "skipped", "reason": "failed rows have unknown scope or stratum"}
    return result


def _count_weight(rows):
    return {"count": len(rows), "weight": sum(row["weight"] for row in rows)}


def _annotate(key, record, weight):
    raw = record.get("result") if record.get("status") == "ok" else None
    raw = raw if isinstance(raw, dict) else {}
    scope = raw.get("scope", {}).get("in_scope")
    scope = scope if isinstance(scope, bool) else None
    stratum = raw.get("stratum")
    stratum = stratum if stratum in STRATA else None
    window = raw.get("window") or {}
    valid = (record.get("status") == "ok" and not raw.get("invalid") and not raw.get("caps")
             and raw.get("gate_a", {}).get("passed") is True
             and raw.get("gate_b", {}).get("passed") is True
             and raw.get("gate_e", {}).get("passed") is True)
    bounded_certificate = bool(valid and window.get("complete") is True
                               and window.get("verdict") == "bounded")
    growth_certificate = bool(valid and scope is True and any(
        raw.get("growth", {}).get(name, {}).get("certified") is True
        and raw.get("growth", {}).get(name, {}).get("complete") is not False
        for name in GROWTH_METHODS))
    if bounded_certificate and growth_certificate:
        # A failed gate overrides both certificates.  Keep the raw evidence.
        valid, bounded_certificate, growth_certificate = False, False, False
    bounded = True if bounded_certificate else False if growth_certificate else None
    growing = True if growth_certificate else False if bounded_certificate else None
    return {"key": key, "key_sha256": hashlib.sha256(key.encode()).hexdigest(),
            "weight": int(weight), "runner_status": record.get("status"),
            "scope": scope, "stratum": stratum, "valid": valid,
            "bounded": bounded, "growing": growing,
            "outcome": "bounded" if bounded else "growing" if growing else "undecided",
            "raw": raw, "window": window}


def gate_report(records):
    """Read a/b/e only; absent or unfinished checks are unavailable, not passed."""
    result = {}
    for letter in ("a", "b", "e"):
        passed, failed, unavailable, not_applicable = [], [], [], []
        for key, record in sorted(records.items()):
            raw = record.get("result") if record.get("status") == "ok" else None
            gate = raw.get("gate_" + letter) if isinstance(raw, dict) else None
            if not isinstance(gate, dict):
                unavailable.append(key)
                continue
            if letter == "a" and gate.get("complete") is not True:
                unavailable.append(key)
                continue
            if (letter == "b" and gate.get("complete") is not True
                    and raw.get("window", {}).get("complete") is not True):
                unavailable.append(key)
                continue
            if gate.get("passed") is False:
                failed.append(key)
            elif gate.get("passed") is True:
                if letter == "b" and gate.get("applicable") is False:
                    not_applicable.append(key)
                else:
                    passed.append(key)
            else:
                unavailable.append(key)
        result[letter] = {"status": "failed" if failed else "unavailable" if unavailable else "passed",
                          "passed_count": len(passed), "not_applicable_count": len(not_applicable),
                          "failed": failed, "unavailable": unavailable}
    result["passed"] = all(result[letter]["status"] == "passed" for letter in ("a", "b", "e"))
    return result


def _threshold(share, relation, threshold, *, classification_complete, gates_passed):
    if share is None:
        return {"status": "skipped", "reason": "empty denominator", "threshold_met": None}
    value = share if isinstance(share, Fraction) else Fraction(str(share))
    target = Fraction(str(threshold))
    met = value >= target if relation == ">=" else value <= target
    if not classification_complete:
        return {"status": "skipped", "reason": "scope/stratum classification incomplete",
                "threshold_met": None, "known_subset_threshold_met": met}
    return {"status": "recorded" if gates_passed else "unpromoted_gate_failure_or_gap",
            "threshold_met": met, "criterion": relation, "threshold": threshold,
            "comparison_arithmetic": "exact rational"}


def _strata(rows, classification_complete):
    grouped = defaultdict(list)
    for row in rows:
        scope = "in_scope" if row["scope"] is True else "out_of_scope" if row["scope"] is False else "unknown_scope"
        grouped[(scope, row["stratum"] or "unknown_stratum")].append(row)
    return [{"scope": scope, "stratum": stratum, **_count_weight(group),
             "bounded": _rates(group, "bounded", classification_complete=classification_complete),
             "growing": _rates(group, "growing", classification_complete=classification_complete)}
            for (scope, stratum), group in sorted(grouped.items())]


def _window_verdict_rates(rows, classification_complete):
    """Separate the recorded window reading from the resolved global outcome."""
    classified = []
    for row in rows:
        verdict = row["window"].get("verdict")
        known = row["valid"] and row["window"].get("complete") is True and verdict in (
            "bounded", "progressions", "none")
        classified.append((row, verdict if known else "undecided", known))
    resolved = [(row, verdict) for row, verdict, known in classified if known]
    result = {}
    for category in ("bounded", "progressions", "none", "undecided"):
        result[category] = {
            "count": _share(sum(verdict == category for _, verdict, _ in classified), len(classified)),
            "weight": _share(sum(row["weight"] for row, verdict, _ in classified if verdict == category),
                             sum(row["weight"] for row, _, _ in classified)),
            "denominator_complete": classification_complete,
            "undecided_count": sum(not known for _, _, known in classified),
            "undecided_weight": sum(row["weight"] for row, _, known in classified if not known)}
        if classification_complete:
            result[category]["sensitivity_excluding_undecided"] = {
                "count": _share(sum(verdict == category for _, verdict in resolved), len(resolved)),
                "weight": _share(sum(row["weight"] for row, verdict in resolved if verdict == category),
                                 sum(row["weight"] for row, _ in resolved))}
        else:
            result[category]["sensitivity_excluding_undecided"] = {
                "status": "skipped", "reason": "failed rows have unknown scope or stratum"}
    result["qualification"] = ("none means the completed size-at-most-six window search found no bound on any "
                               "repeating residue; it is not a proof of no bond or of growth. Caps, invalid gates "
                               "and failed records count as undecided even if a local window reading is present.")
    return result


def _reading_rates(rows, getter):
    selected = []
    for row in rows:
        value = getter(row)
        selected.append(dict(row, feature=value))
    if any(row["feature"] is None for row in selected):
        return {"status": "skipped", "reason": "requested readings absent in one or more bounded records",
                "available_count": sum(row["feature"] is not None for row in selected),
                "denominator": _count_weight(rows)}
    return _rates(selected, "feature")


def _p3_explanation(row):
    """Read A4 on completed repeating residues; never invent capped phases."""
    window = row["window"]
    if (not row["valid"] or window.get("complete") is not True
            or window.get("verdict") not in ("progressions", "none")):
        return None
    residues = window.get("residues") or []
    period = window.get("period")
    if not isinstance(period, int) or period < 1 or len(residues) != period:
        return None
    if any(not isinstance(residue.get("U"), int) and residue.get("U") != "> 6"
           for residue in residues):
        return None
    unbounded = [residue for residue in residues if not isinstance(residue["U"], int)]
    if not unbounded or any(not isinstance(residue.get("knot_meeting_some"), bool)
                            for residue in unbounded):
        return None
    return all(residue["knot_meeting_some"] is False for residue in unbounded)


def _readings(rows):
    bounded = [row for row in rows if row["scope"] is True and row["bounded"] is True]

    def B_theorem(row):
        residues = row["window"].get("residues") or []
        if not residues or any("B_covered" not in residue for residue in residues):
            return None
        return all(residue["B_covered"] is True for residue in residues)

    result = {"denominator": "valid in-scope window-bounded families",
              "attribution_rule": ATTRIBUTION_RULE,
              "exclusive_family_readings": {},
              "secondary_B_theorem_every_repeating_residue": _reading_rates(bounded, B_theorem),
              "secondary_nonexclusive_minimum_witness_readings": {}}
    for feature in FEATURES:
        def exclusive(row, feature=feature):
            reading = row["window"].get("exclusive_reading")
            return reading == feature if reading in FEATURES else None

        result["exclusive_family_readings"][feature] = _reading_rates(bounded, exclusive)
        feature_result = {}
        for name, residue_quantifier, witness_quantifier in (
                ("every_residue_some_witness", all, "any"),
                ("some_residue_some_witness", any, "any"),
                ("every_residue_every_witness", all, "every")):
            field = feature + "_" + witness_quantifier

            def reading(row, field=field, quantifier=residue_quantifier):
                residues = row["window"].get("residues") or []
                if not residues or any(field not in residue.get("readings", {}) for residue in residues):
                    return None
                return quantifier(residue["readings"][field] is True for residue in residues)

            feature_result[name] = _reading_rates(bounded, reading)
        result["secondary_nonexclusive_minimum_witness_readings"][feature] = feature_result
    return result


def _bond_sizes(rows):
    family_maximum, family_minimum, saved_state, saved_witness = Counter(), Counter(), Counter(), Counter()
    family_maximum_weight, family_minimum_weight = Counter(), Counter()
    residue_count, residue_weight = Counter(), Counter()
    for row in rows:
        residues = row["window"].get("residues") or []
        finite = [residue["U"] for residue in residues if isinstance(residue.get("U"), int)]
        if row["scope"] is True and row["bounded"] is True and finite:
            family_maximum[str(max(finite))] += 1
            family_minimum[str(min(finite))] += 1
            family_maximum_weight[str(max(finite))] += row["weight"]
            family_minimum_weight[str(min(finite))] += row["weight"]
        for residue in residues:
            size = str(residue.get("U", "missing"))
            residue_count[size] += 1
            residue_weight[size] += row["weight"]
        for state in row["window"].get("state_bonds") or []:
            size = str(state.get("g", "missing"))
            saved_state[size] += 1
            saved_witness[size] += len(state.get("least_bonds") or [])
    return {"bounded_in_scope_family_maximum_U_count": dict(sorted(family_maximum.items())),
            "bounded_in_scope_family_minimum_U_count": dict(sorted(family_minimum.items())),
            "bounded_in_scope_family_maximum_U_weight": dict(sorted(family_maximum_weight.items())),
            "bounded_in_scope_family_minimum_U_weight": dict(sorted(family_minimum_weight.items())),
            "all_recorded_repeating_residue_U_count": dict(sorted(residue_count.items())),
            "all_recorded_repeating_residue_U_draw_weight": dict(sorted(residue_weight.items())),
            "saved_state_least_size_count": dict(sorted(saved_state.items())),
            "saved_equal_minimum_witness_count": dict(sorted(saved_witness.items())),
            "units": "residue totals count phases, and saved-state totals include transient states; neither is a family share"}


def _residue_records(rows, *, only_I=False, without_bound=False):
    result = []
    for row in rows:
        if only_I and not (row["scope"] is True and row["stratum"] == "I"):
            continue
        residues = row["window"].get("residues") or []
        if without_bound:
            residues = [residue for residue in residues if not isinstance(residue.get("U"), int)]
        if not residues:
            continue
        result.append({"key_sha256": row["key_sha256"], "weight": row["weight"],
            "scope": row["scope"], "stratum": row["stratum"], "valid": row["valid"],
            "preperiod": row["window"].get("preperiod"), "period": row["window"].get("period"),
            "residues": residues})
    return result


def _selection():
    file = HERE / "sample.json"
    if not file.exists():
        return None
    return json.loads(file.read_text())


def _selected_keys(sample, field):
    if sample is None:
        return None
    return [item if isinstance(item, str) else item["key"] for item in sample.get(field, [])]


def _sample_paths(path, rows_by_key, sample):
    source, records = _source(path)
    expected = _selected_keys(sample, "path")
    classes, weights, statuses, details = Counter(), Counter(), Counter(), []
    for key, record in sorted(records.items(), key=lambda item: inputs.carry_order(item[0])):
        parent = rows_by_key.get(key)
        value = record.get("result") or {}
        category = str(value.get("class", "missing_class")) if record.get("status") == "ok" else "runner_" + str(record.get("status"))
        classes[category] += 1
        weights[category] += parent["weight"] if parent else 0
        statuses[str(record.get("status"))] += 1
        details.append({"key_sha256": hashlib.sha256(key.encode()).hexdigest(),
            "weight": parent["weight"] if parent else None,
            "stratum": parent["stratum"] if parent else None,
            "runner_status": record.get("status"), "path_class": value.get("class"),
            "bounded_upper_certificate": record.get("status") == "ok" and value.get("class") == "bounded",
            "reported": {name: value[name] for name in ("bound", "L_path", "lambda_path", "period", "preperiod", "caps") if name in value}})
    return {"source": source, "records": len(records), "runner_statuses": dict(statuses),
            "classes_count": dict(classes), "classes_weight": dict(weights),
            "selection_complete": None if expected is None else set(records) == set(expected),
            "missing_keys": None if expected is None else sorted(set(expected) - set(records)),
            "extra_keys": None if expected is None else sorted(set(records) - set(expected)),
            "families": details,
            "scope": "frozen sample only; a growing path minimum does not certify growth of the free bond"}


def _sample_direct(path, rows_by_key, sample):
    source, records = _source(path)
    selected = _selected_keys(sample, "direct")
    hashes = {row["key_sha256"]: key for key, row in rows_by_key.items()}
    if len(hashes) != len(rows_by_key):
        raise ValueError("family SHA-256 collision")
    expected = None if selected is None else {
        f"{hashlib.sha256(key.encode()).hexdigest()}:s={s}" for key in selected for s in range(1, 7)}
    counts, weights, statuses, details = defaultdict(Counter), defaultdict(Counter), Counter(), []
    for case_id, record in sorted(records.items()):
        value = record.get("result") or {}
        digest, delimiter, depth = case_id.partition(":s=")
        key = value.get("key") or hashes.get(digest)
        s = value.get("s") if value.get("s") is not None else int(depth) if delimiter and depth.isdigit() else None
        parent = rows_by_key.get(key)
        status = str(value.get("status", "missing_status")) if record.get("status") == "ok" else "runner_" + str(record.get("status"))
        minimum = value.get("minimum")
        category = str(minimum) if status in ("exact_minimum", "sizes_through_6_excluded") else status
        counts[str(s)][category] += 1
        weights[str(s)][category] += parent["weight"] if parent else 0
        statuses[status] += 1
        details.append({"case": case_id, "key_sha256": parent["key_sha256"] if parent else digest,
            "s": s, "weight": parent["weight"] if parent else None, "stratum": parent["stratum"] if parent else None,
            "runner_status": record.get("status"), "status": status, "minimum": minimum,
            "cutoff_depth": value.get("cutoff_depth"), "cap": value.get("cap"),
            "completed_lower_sizes": value.get("completed_lower_sizes", value.get("by_size")),
            "verified_bond": value.get("verification", {}).get("is_bond")})
    return {"source": source, "records": len(records), "statuses": dict(statuses),
            "by_absolute_depth_count": {s: dict(counts[s]) for s in sorted(counts)},
            "by_absolute_depth_weight": {s: dict(weights[s]) for s in sorted(weights)},
            "selection_complete": None if expected is None else set(records) == expected,
            "missing_cases": None if expected is None else sorted(expected - set(records)),
            "extra_cases": None if expected is None else sorted(set(records) - expected),
            "cases": details,
            "scope": "finite readings are upper bounds only; '> 6' and growth through depth 6 are not growth certificates"}


def summarize_population(window_path, *, paths_path=None, direct_path=None):
    source, records = _source(window_path)
    census = inputs.load_records()
    keys = inputs.population(census)
    if set(records) != set(keys):
        raise ValueError(f"refuse incomplete or foreign window population: expected {len(keys)}, "
                         f"missing {len(set(keys) - set(records))}, extra {len(set(records) - set(keys))}")
    weights = inputs.weights(keys)
    rows = [_annotate(key, records[key], weights[key]) for key in keys]
    rows_by_key = {row["key"]: row for row in rows}
    unknown = [row for row in rows if row["scope"] is None or row["stratum"] is None]
    classification_complete = not unknown
    gates = gate_report(records)
    questions = []
    if unknown:
        questions.append("One or more failed window records have no scope/stratum; affected prediction and sensitivity denominators are skipped.")
    mismatched_weights = [row["key_sha256"] for row in rows
                          if row["raw"].get("weight") is not None and row["raw"]["weight"] != row["weight"]]
    if mismatched_weights:
        questions.append("Producer weights differ from the authorized draw archive; summary uses archive weights and leaves prediction promotion blocked.")
    eligible = [row for row in rows if row["scope"] is True]
    in_stratum = {s: [row for row in eligible if row["stratum"] == s] for s in STRATA}
    bounded_rates = {s: _rates(in_stratum[s], "bounded", classification_complete=classification_complete) for s in STRATA}
    growing_rates = {s: _rates(in_stratum[s], "growing", classification_complete=classification_complete) for s in STRATA}
    gates_passed = gates["passed"] and not mismatched_weights
    I_share, O_share = bounded_rates["I"]["weight"]["share"], bounded_rates["O"]["weight"]["share"]
    gap = I_share - O_share if I_share is not None and O_share is not None else None
    I_exact, O_exact = _fraction(bounded_rates["I"]["weight"]), _fraction(bounded_rates["O"]["weight"])
    gap_exact = I_exact - O_exact if I_exact is not None and O_exact is not None else None
    I_count, O_count = bounded_rates["I"]["count"]["share"], bounded_rates["O"]["count"]["share"]
    count_gap = I_count - O_count if I_count is not None and O_count is not None else None
    T = in_stratum["T"]
    if len(T) != 5:
        questions.append(f"Frozen P4 names five in-scope T families; completed classifications currently supply {len(T)}.")
    all_growth = _rates(eligible, "growing", classification_complete=classification_complete)
    P3_rows = [dict(row, p3_explanation=_p3_explanation(row))
               for row in in_stratum["I"] if row["bounded"] is not True]
    P3_rates = _rates(P3_rows, "p3_explanation", classification_complete=classification_complete)
    sensitivity_gap = {"status": "skipped", "reason": "classification incomplete or empty resolved stratum"}
    if classification_complete:
        I_sensitivity = bounded_rates["I"]["sensitivity_excluding_undecided"]
        O_sensitivity = bounded_rates["O"]["sensitivity_excluding_undecided"]
        I_sweight, O_sweight = _fraction(I_sensitivity["weight"]), _fraction(O_sensitivity["weight"])
        I_scount, O_scount = _fraction(I_sensitivity["count"]), _fraction(O_sensitivity["count"])
        if I_sweight is not None and O_sweight is not None:
            sensitivity_gap = {"weight_gap": float(I_sweight - O_sweight),
                "count_gap": float(I_scount - O_scount) if I_scount is not None and O_scount is not None else None,
                "test": _threshold(I_sweight - O_sweight, ">=", 0.2,
                                   classification_complete=True, gates_passed=gates_passed)}
    predictions = {
        "P1": {"definition": "in-scope I weight window-bounded at every sufficiently large depth",
               "stratum": "I", "rates": bounded_rates["I"],
               "test": _threshold(I_exact, ">=", 0.8, classification_complete=classification_complete,
                                  gates_passed=gates_passed)},
        "P2": {"definition": "I minus O shares window-bounded at every sufficiently large depth",
               "I": bounded_rates["I"], "O": bounded_rates["O"],
               "weight_gap": gap, "count_gap": count_gap,
               "sensitivity_excluding_undecided": sensitivity_gap,
               "test": _threshold(gap_exact, ">=", 0.2, classification_complete=classification_complete,
                                  gates_passed=gates_passed),
               "qualification": "O's count and draw-weight Wilson intervals are reported separately; the frozen comparison is underpowered"},
        "P3": {"definition": P3_DEFINITION,
               "denominator": "in-scope I families lacking a valid completed every-residue window bound",
               "rates": P3_rates,
               "test": _threshold(_fraction(P3_rates["weight"]), ">=", 0.8,
                                  classification_complete=classification_complete, gates_passed=gates_passed),
               "uncertainty": "caps, incomplete windows, invalid gates or missing residue flags make the explanation unknown; unknown counts false in full shares and is omitted from sensitivity",
               "families": [{"key_sha256": row["key_sha256"], "weight": row["weight"],
                             "explanation": row["p3_explanation"]} for row in P3_rows],
               "per_residue_readings": _residue_records(P3_rows, without_bound=True)},
        "P4": {"definition": "all five in-scope T families window-bounded at every sufficiently large depth",
               "expected_families": 5, "observed_families": len(T), "rates": bounded_rates["T"],
               "test": _threshold(_fraction(bounded_rates["T"]["count"]), ">=", 1.0,
                                  classification_complete=classification_complete and len(T) == 5,
                                  gates_passed=gates_passed),
               "families": [{"key": row["key"], "key_sha256": row["key_sha256"], "weight": row["weight"],
                              "outcome": row["outcome"], "window": row["window"],
                              "caps": row["raw"].get("caps"), "runner_status": row["runner_status"]} for row in T]},
        "P5": {"definition": "in-scope weight with an uncapped valid G, G2 or live-quotient G2 growth certificate",
               "rates": all_growth, "by_stratum": growing_rates,
               "test": _threshold(_fraction(all_growth["weight"]), "<=", 0.05,
                                  classification_complete=classification_complete, gates_passed=gates_passed)}}
    verdicts, verdict_weights = Counter(), Counter()
    for row in rows:
        verdicts[row["outcome"]] += 1
        verdict_weights[row["outcome"]] += row["weight"]
    progressions = [row for row in rows if row["window"].get("verdict") == "progressions"]
    out_of_scope = [row for row in rows if row["scope"] is False]
    sample = _selection()
    return {"schema_version": 1, "mode": "completed_population", "source": source,
        "population": {"families": len(rows), "draw_weight": sum(weights.values()),
                       "classification_complete": classification_complete,
                       "unknown_classification": [{"key_sha256": row["key_sha256"], "weight": row["weight"],
                                                    "runner_status": row["runner_status"]} for row in unknown]},
        "rules": {"uncertainty": "caps, invalid gates and failed runner records override local certificates to undecided; undecided counts as not bounded and not growing in full shares",
                  "resolved": "valid window-bounded is resolved bounded; valid uncapped in-scope G/G2/G2_live certified is resolved growing; partial window bounds alone leave both global claims undecided",
                  "sensitivity": "exclude observable-specific undecided; skip affected denominators if scope/stratum classification is unavailable",
                  "P3": P3_DEFINITION,
                  "exclusive_readings": ATTRIBUTION_RULE,
                  "intervals": "Wilson95 count intervals use families as Bernoulli units; draw-weight intervals treat archived repeated draws as Bernoulli units and are descriptive, with no claim of independence between repeats of one family",
                  "gate_scope": "this summary checks recorded a/b/e; c/d and synthetic controls remain the separate lead-owned gates report",
                  "no_new_certificate": "all classifications are readings of runner certificates; finite direct and path results are not growth certificates for the free bond"},
        "gate_a_b_e": gates, "weight_mismatches": mismatched_weights,
        "producer_ambiguities": [{"key_sha256": row["key_sha256"], "weight": row["weight"],
                                  "questions": row["raw"]["ambiguities"]} for row in rows
                                 if row["raw"].get("ambiguities")],
        "caps_and_failures": [{"key_sha256": row["key_sha256"], "weight": row["weight"],
                               "runner_status": row["runner_status"], "invalid": row["raw"].get("invalid"),
                               "caps": row["raw"].get("caps", [])} for row in rows
                              if row["runner_status"] != "ok" or row["raw"].get("invalid") or row["raw"].get("caps")],
        "strata": _strata(rows, classification_complete),
        "outcomes_count": dict(verdicts), "outcomes_weight": dict(verdict_weights),
        "predictions": predictions,
        "out_of_scope": {**_count_weight(out_of_scope),
                         "bounded_upper_certificates": _rates(out_of_scope, "bounded", classification_complete=classification_complete),
                         "keys": [row["key_sha256"] for row in out_of_scope],
                         "qualification": "upper bounds to covered targets remain upper bounds; these families are excluded from lower-bound population predictions"},
        "bond_sizes": _bond_sizes(rows), "readings": _readings(rows),
        "readings_by_stratum": {s: _readings(in_stratum[s]) for s in STRATA},
        "bond_sizes_by_stratum": {s: _bond_sizes(in_stratum[s]) for s in STRATA},
        "window_verdicts_by_stratum": {s: _window_verdict_rates(in_stratum[s], classification_complete)
                                       for s in STRATA},
        "progressions_only": {**_count_weight(progressions),
                              "families": _residue_records(progressions),
                              "qualification": "finite bounds on some residues; absence of a window bound on others is undecided"},
        "samples": {"paths": _sample_paths(paths_path, rows_by_key, sample) if paths_path else {"status": "not_supplied"},
                    "direct": _sample_direct(direct_path, rows_by_key, sample) if direct_path else {"status": "not_supplied"}},
        "questions": questions}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--window", type=Path, required=True)
    parser.add_argument("--paths", type=Path)
    parser.add_argument("--direct", type=Path)
    parser.add_argument("--check-gates", action="store_true", help="smoke records only; emit a/b/e checks and no predictions")
    parser.add_argument("--output", type=Path, default=HERE / "summary.json")
    args = parser.parse_args()
    if args.check_gates:
        source, records = _source(args.window)
        result = {"schema_version": 1, "mode": "gate_only", "source": source,
                  "records": len(records), "gate_a_b_e": gate_report(records),
                  "predictions_computed": False}
    else:
        result = summarize_population(args.window, paths_path=args.paths, direct_path=args.direct)
    output = args.output if args.output.is_absolute() else HERE / args.output
    inputs.dump(output, result)
    print(json.dumps({"mode": result["mode"], "output": str(output),
                      "predictions_computed": result["mode"] == "completed_population"}))


if __name__ == "__main__":
    main()
