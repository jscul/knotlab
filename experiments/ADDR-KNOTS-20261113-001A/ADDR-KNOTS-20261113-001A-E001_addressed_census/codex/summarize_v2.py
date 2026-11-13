#!/usr/bin/env python3
"""Addressed-census summary with the 2026-11-13 units addendum.

Usage: .venv/bin/python -B summarize_v2.py DIR [--output-prefix summary_v2]

Only the observed, complete key records contribute to descriptive tables.  Coverage
and validation are reported separately, so a smoke run remains useful without being
presented as the registered census.  All W weights are empirical draw frequencies.
No sampling of descriptions, pattern generation, or SAT solving occurs here.
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import gzip
import importlib.util
import json
import math
import os
from pathlib import Path
import random
import sys
from typing import Any, Iterable

for _thread_variable in (
    "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "BLIS_NUM_THREADS",
):
    os.environ[_thread_variable] = "1"

LEVELS = 12
BOOTSTRAPS = 2000
BOOTSTRAP_SEED = 20261115
FATES = ("F0", "F1", "F2", "F3", "FU")
CLASSES = ("finitary", "bounded", "polynomial", "exponential")
COMPARATORS = CLASSES[:-1]
BIN_LIMITS = (0.0, 1.0, 1.5, 2.1, 3.0, 4.5, math.inf)
BIN_LABELS = ("[0, 1)", "[1, 1.5)", "[1.5, 2.1)", "[2.1, 3)", "[3, 4.5)", "[4.5, infinity)")
GATES = ("V-act", "V-sat", "V-B0", "V-act-class", "V-rel", "V-code", "V-resume")
EXPECTED_W = 40000
EXPECTED_E = {2: (64, 30), 3: (5832, 3)}


def canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False)


def safe_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def density_bin(rho: float) -> int:
    for i in range(len(BIN_LABELS)):
        if BIN_LIMITS[i] <= rho < BIN_LIMITS[i + 1]:
            return i
    raise ValueError(f"invalid density {rho!r}")


def mean(values: Iterable[float]) -> float | None:
    values = list(values)
    return sum(values) / len(values) if values else None


def forced_fate(knots: list[int], verdicts: list[int | None]) -> str:
    """User's ordered rule, over nonempty levels; later nulls keep forced F1/F2."""
    live_levels = [verdicts[i] for i, count in enumerate(knots) if count]
    if not live_levels:
        return "F0"
    if live_levels[0] == 0:
        return "F1"
    if live_levels[0] == 1 and 0 in live_levels[1:]:
        return "F2"
    if all(verdict == 1 for verdict in live_levels):
        return "F3"
    return "FU"


def normalize_class(value: Any) -> str | None:
    # The producer's canonical schema has a class string and a separate degree.
    return value if value in CLASSES else None


class PatternVerdictConflict(ValueError):
    """Contradictory decided instances invalidate every downstream summary."""

    def __init__(self, conflicts: list[dict[str, Any]]) -> None:
        self.conflicts = conflicts
        super().__init__(f"{len(conflicts)} contradictory decided pattern-level verdicts")


def read_jsonl(path: Path, errors: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    opener = gzip.open if path.suffix == ".gz" else open
    try:
        with opener(path, "rt", encoding="utf-8") as stream:
            for line_number, line in enumerate(stream, 1):
                if not line.strip():
                    continue
                try:
                    row = json.loads(line)
                    if not isinstance(row, dict):
                        raise ValueError("record is not a JSON object")
                    row["_summary_source"] = {"file": str(path), "line": line_number}
                    rows.append(row)
                except (ValueError, TypeError) as error:
                    errors.append({"file": str(path), "line": line_number, "error": str(error)})
    except (OSError, EOFError) as error:
        errors.append({"file": str(path), "error": str(error)})
    return rows


def prepare_record(raw: dict[str, Any]) -> tuple[dict[str, Any] | None, list[str]]:
    problems: list[str] = []
    key = raw.get("key")
    if not (isinstance(key, list) and len(key) == 5 and isinstance(key[0], int)
            and isinstance(key[4], list)):
        return None, ["key must be [s, sw, d0, d1, placements]"]
    arrays = ("knots_n", "join_n", "verdict_n", "conflicts_n", "wall_n")
    if any(not isinstance(raw.get(name), list) or len(raw[name]) != LEVELS for name in arrays):
        return None, ["all five level arrays must have length 12"]
    if not isinstance(raw.get("pattern_hash"), str) or not raw["pattern_hash"]:
        return None, ["pattern_hash is missing"]
    if not isinstance(raw.get("key_id"), str) or not raw["key_id"]:
        return None, ["key_id is missing"]
    knots, joins, verdicts = raw["knots_n"], raw["join_n"], raw["verdict_n"]
    for i in range(LEVELS):
        if not isinstance(knots[i], int) or isinstance(knots[i], bool) or knots[i] < 0:
            problems.append(f"knots_n[{i}] is not a nonnegative integer")
        if (not isinstance(joins[i], int) or isinstance(joins[i], bool) or joins[i] < 0
                or isinstance(knots[i], int) and joins[i] > knots[i]):
            problems.append(f"join_n[{i}] is invalid")
        if verdicts[i] not in (0, 1, None) or isinstance(verdicts[i], bool):
            problems.append(f"verdict_n[{i}] must be 0, 1, or null")
        if not safe_number(raw["wall_n"][i]) or raw["wall_n"][i] < 0:
            problems.append(f"wall_n[{i}] is invalid")
        conflict = raw["conflicts_n"][i]
        if conflict is not None and (not isinstance(conflict, int) or isinstance(conflict, bool) or conflict < 0):
            problems.append(f"conflicts_n[{i}] is invalid")
        if knots[i] == 0 and verdicts[i] != 1:
            problems.append(f"empty level {i + 1} must be alive")
    if problems:
        return None, problems
    fate = forced_fate(knots, verdicts)
    first_death = next((i + 1 for i, verdict in enumerate(verdicts) if verdict == 0), None)
    returned = any(verdicts[i] == 0 and 1 in verdicts[i + 1:] for i in range(LEVELS))
    rho = [knots[i] / (2 ** (i + 1)) for i in range(LEVELS)]
    flags = raw.get("flags", {})
    if not isinstance(flags, dict):
        flags = {}
    single = len(key[4]) == 1
    if "single_placement" in flags and flags["single_placement"] is not single:
        problems.append("flags.single_placement disagrees with normalized key")
    first_letter = flags.get("first_letter_settled")
    if not isinstance(first_letter, bool):
        problems.append("flags.first_letter_settled is missing or not Boolean")
    if raw.get("fate") != fate:
        problems.append(f"producer fate {raw.get('fate')!r} differs from frozen fate {fate}")
    if raw.get("first_death") != first_death:
        problems.append("producer first_death disagrees with verdicts")
    if raw.get("return") is not returned:
        problems.append("producer return disagrees with verdicts")
    for name, actual in (("rho_max", max(rho)), ("rho12", rho[-1])):
        if not safe_number(raw.get(name)) or not math.isclose(raw[name], actual, rel_tol=1e-12, abs_tol=1e-12):
            problems.append(f"producer {name} disagrees with knot counts")
    for name in ("rel_class", "letter_class"):
        if normalize_class(raw.get(name)) is None:
            problems.append(f"{name} is missing or not a canonical class")
    if raw.get("automaton_class") is None:
        problems.append("automaton_class is missing")
    if problems:
        return None, problems
    row = dict(raw)
    row.update({
        "s": key[0], "fate": fate, "first_death": first_death,
        "return": returned, "rho_max": max(rho), "rho12": rho[-1],
        "density_bin": density_bin(max(rho)), "s1": key[0] == 1,
        "single_placement": single, "first_letter_settled": first_letter,
        "settled": single or first_letter,
        "settled_union": key[0] == 1 or single or first_letter,
        "cluster": canonical(raw["automaton_class"]),
        "null_before_death": first_death is not None and any(
            verdicts[i] is None for i in range(first_death - 1) if knots[i]),
    })
    return row, []


def load_records(directory: Path) -> tuple[list[dict[str, Any]], dict[str, dict[str, Any]], dict[str, Any]]:
    errors: list[dict[str, Any]] = []
    raw_verdict_records: list[dict[str, Any]] = []
    key_rows: dict[str, dict[str, Any]] = {}
    serial_to_id: dict[str, str] = {}
    duplicate_records = 0
    files = sorted((directory / "keys").glob("worker-*.jsonl"))
    for path in files:
        for raw in read_jsonl(path, errors):
            raw_verdict_records.append(raw)
            row, problems = prepare_record(raw)
            if row is None:
                errors.append({"file": str(path), "key_id": raw.get("key_id"), "errors": problems})
                continue
            kid, serial = row["key_id"], canonical(row["key"])
            if kid in key_rows:
                previous = key_rows[kid]
                if previous["key"] == row["key"] and previous["pattern_hash"] == row["pattern_hash"]:
                    resolved, _ = merge_pattern_verdicts({"previous": previous, "incoming": row})
                    # Keep the first record's metadata. A replay may resolve
                    # its budgeted outcomes, but cannot replace its labels.
                    key_rows[kid] = {**previous, **{field: resolved[kid][field] for field in (
                        "verdict_n", "fate", "first_death", "return", "null_before_death", "undecided_after")}}
                # Replays may differ in timing and budgeted outcomes. Decided
                # contradictions must already have stopped, never be discarded.
                ignored = {"wall_n", "level_wall_n", "total_wall_seconds", "peak_rss_mb",
                           "_summary_source", "verdict_n", "conflicts_n", "phase_n", "fate",
                           "first_death", "return", "null_before_death", "undecided_after"}
                left = {k: v for k, v in previous.items() if k not in ignored}
                right = {k: v for k, v in row.items() if k not in ignored}
                if left != right:
                    errors.append({"key_id": kid, "error": "conflicting repeated key records"})
                duplicate_records += 1
                continue
            if serial in serial_to_id and serial_to_id[serial] != kid:
                previous_id = serial_to_id[serial]
                resolved, _ = merge_pattern_verdicts({previous_id: key_rows[previous_id], kid: row})
                key_rows[previous_id] = resolved[previous_id]
                errors.append({"key_id": kid, "error": "same normalized key has different key_ids"})
                continue
            key_rows[kid] = row
            serial_to_id[serial] = kid
    # Even a row rejected for incorrect derived metadata may expose opposite
    # decided verdicts. It must not disappear from the contradiction check.
    conflicts = pattern_verdict_conflicts(raw_verdict_records)
    if conflicts:
        raise PatternVerdictConflict(conflicts)
    draw_path = directory / "draws.jsonl.gz"
    draws = read_jsonl(draw_path, errors) if draw_path.exists() else []
    if not draw_path.exists():
        errors.append({"file": str(draw_path), "error": "missing draw population"})
    accepted = []
    missing = Counter()
    rejected = Counter()
    seen_draws = set()
    duplicates = 0
    population_counts = Counter()
    e_roster: dict[int, dict[Any, set[Any]]] = defaultdict(lambda: defaultdict(set))
    w_indices = set()
    w_s_conditions = {minimum: Counter() for minimum in (2, 3)}
    for draw in draws:
        population = draw.get("population")
        if population not in ("W", "E"):
            errors.append({"error": "draw population must be W or E", "draw": draw})
            continue
        identity = (population, draw.get("index")) if population == "W" else (
            population, draw.get("s"), draw.get("a"), draw.get("j"))
        if None in identity or not all(isinstance(value, (str, int)) for value in identity):
            errors.append({"error": "draw identity is missing", "identity": list(identity)})
            continue
        if identity in seen_draws:
            duplicates += 1
            errors.append({"error": "duplicate draw identity", "identity": list(identity)})
            continue
        seen_draws.add(identity)
        population_counts[population] += 1
        if population == "W":
            w_indices.add(draw["index"])
            sampled_s = draw.get("s")
            if sampled_s is None and isinstance(draw.get("key"), list) and draw["key"]:
                sampled_s = draw["key"][0]
            for minimum in (2, 3):
                if isinstance(sampled_s, int):
                    membership = "true" if sampled_s >= minimum else "false"
                elif draw.get("rejected") == "s":
                    # The declared s-code rejection is s > 5.
                    membership = "true"
                else:
                    membership = "unknown"
                w_s_conditions[minimum][membership] += 1
        else:
            e_roster[draw["s"]][draw["a"]].add(draw["j"])
        if draw.get("rejected") is not None:
            rejected[(population, str(draw["rejected"]))] += 1
            continue
        kid = draw.get("key_id")
        if kid is None and "key" in draw:
            kid = serial_to_id.get(canonical(draw["key"]))
        if kid not in key_rows:
            missing[population] += 1
            continue
        record = key_rows[kid]
        if "key" in draw and canonical(draw["key"]) != canonical(record["key"]):
            errors.append({"identity": list(identity), "error": "draw key does not match key_id"})
            continue
        if "s" in draw and draw["s"] != record["s"]:
            errors.append({"identity": list(identity), "error": "draw s does not match normalized key"})
            continue
        accepted.append({"population": population, "draw": draw, "record": record})
    w_complete = len(w_indices) == EXPECTED_W and (
        w_indices == set(range(EXPECTED_W)) or w_indices == set(range(1, EXPECTED_W + 1)))
    e_complete = set(e_roster) == set(EXPECTED_E) and all(
        len(e_roster[s]) == automata and all(len(js) == lists for js in e_roster[s].values())
        and set(e_roster[s]) in (set(range(automata)), set(range(1, automata + 1)))
        and all(js in (set(range(lists)), set(range(1, lists + 1))) for js in e_roster[s].values())
        for s, (automata, lists) in EXPECTED_E.items())
    coverage = {
        "key_files": [str(path.relative_to(directory)) for path in files],
        "complete_key_records": len(key_rows), "duplicate_key_records": duplicate_records,
        "draws": dict(population_counts), "registered_draws": {"W": EXPECTED_W, "E": 19416},
        "accepted_draws_with_complete_keys": dict(Counter(item["population"] for item in accepted)),
        "accepted_draws_missing_complete_keys": dict(missing),
        "rejected_draws": [{"population": pop, "cause": cause, "draws": count}
                           for (pop, cause), count in sorted(rejected.items())],
        "duplicate_draws": duplicates, "W_population_complete": w_complete,
        "W_s_condition_draw_counts": {str(minimum): {label: counts[label] for label in ("true", "false", "unknown")}
                                       for minimum, counts in w_s_conditions.items()},
        "E_population_complete": e_complete,
        "registered_coverage_complete": w_complete and e_complete and not missing and not errors,
        "errors": errors,
    }
    return accepted, key_rows, coverage


def validation_summary(directory: Path) -> dict[str, Any]:
    candidates = (directory / "validation.json", Path(__file__).resolve().parent / "validation.json")
    path = next((candidate for candidate in candidates if candidate.exists()), None)
    if path is None:
        return {"status": "missing", "path": None, "searched_paths": [str(candidate) for candidate in candidates],
                "gates": {}, "all_required_gates_passed": False,
                "required_core_gate_checks_passed": False, "all_assertions_passed": False,
                "note": "Observed descriptive tables are still reported; no validation pass is inferred."}
    try:
        raw = json.loads(path.read_text())
    except (OSError, ValueError) as error:
        return {"status": "unreadable", "path": str(path), "error": str(error),
                "all_required_gates_passed": False, "required_core_gate_checks_passed": False,
                "all_assertions_passed": False}
    gates = raw.get("gates", {})
    accepted_statuses = ("passed", "passed_with_skipped_ambiguous_assertions")
    checks = {name: isinstance(gates.get(name), dict) and (
        gates[name].get("status") == "passed" or
        gates[name].get("status") == "passed_with_skipped_ambiguous_assertions" and
        gates[name].get("required_core_checks_passed") is True) for name in GATES}
    core_pass = raw.get("status") in accepted_statuses and all(checks.values())
    all_assertions = raw.get("status") == "passed" and all(checks.values())
    return {"status": raw.get("status", "unspecified"), "path": str(path), "gates": gates,
            "required_gate_passes": checks, "required_core_gate_checks_passed": core_pass,
            "all_required_gates_passed": all_assertions, "all_assertions_passed": all_assertions,
            "skipped_assertion_disclosure": "The master validation explicitly reports skipped ambiguous assertions; this is not an all-assertions pass."
                if raw.get("status") == "passed_with_skipped_ambiguous_assertions" else None,
            "validation_record": raw}


def pattern_verdict_conflicts(records: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in records:
        if isinstance(row.get("pattern_hash"), str) and isinstance(row.get("verdict_n"), list) and len(row["verdict_n"]) == LEVELS:
            groups[row["pattern_hash"]].append(row)
    conflicts = []
    for pattern_hash, members in sorted(groups.items()):
        for i in range(LEVELS):
            decided = {value: [row for row in members if type(row["verdict_n"][i]) is int and row["verdict_n"][i] == value]
                       for value in (0, 1)}
            if decided[0] and decided[1]:
                conflicts.append({"pattern_hash": pattern_hash, "level": i + 1,
                                  "dead_key_ids": [row.get("key_id") for row in decided[0]],
                                  "alive_key_ids": [row.get("key_id") for row in decided[1]],
                                  "decided_records": [
                                      {"key_id": row.get("key_id"), "verdict": row["verdict_n"][i],
                                       "source": row.get("_summary_source")}
                                      for value in (0, 1) for row in decided[value]]})
    return conflicts


def merge_pattern_verdicts(keys: dict[str, dict[str, Any]]) -> tuple[dict[str, dict[str, Any]], dict[str, Any]]:
    """Use all complete descriptions, across populations, before forming units."""
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in keys.values():
        groups[row["pattern_hash"]].append(row)
    conflicts = pattern_verdict_conflicts(keys.values())
    if conflicts:
        raise PatternVerdictConflict(conflicts)
    resolutions = []
    merged = {}
    changed_fates = []
    resolved_description_levels = 0
    for pattern_hash, members in sorted(groups.items()):
        members.sort(key=lambda row: row["key"])
        first = members[0]
        for field in ("knots_n", "join_n"):
            if any(row[field] != first[field] for row in members):
                raise ValueError(f"equal pattern hash has unequal {field}: {pattern_hash}")
        verdicts = []
        for i in range(LEVELS):
            decided = {value: [row["key_id"] for row in members if row["verdict_n"][i] == value]
                       for value in (0, 1)}
            verdict = 0 if decided[0] else 1 if decided[1] else None
            verdicts.append(verdict)
            unknown = [row["key_id"] for row in members if row["verdict_n"][i] is None]
            if unknown and verdict is not None:
                resolved_description_levels += len(unknown)
                resolutions.append({"pattern_hash": pattern_hash, "level": i + 1,
                                    "verdict": verdict, "decided_key_ids": decided[verdict],
                                    "resolved_key_ids": unknown})
        first_death = next((i + 1 for i, verdict in enumerate(verdicts) if verdict == 0), None)
        fate = forced_fate(first["knots_n"], verdicts)
        returned = any(verdicts[i] == 0 and 1 in verdicts[i + 1:] for i in range(LEVELS))
        for row in members:
            result = dict(row)
            result.update({"verdict_n": list(verdicts), "fate": fate, "first_death": first_death,
                           "return": returned,
                           "null_before_death": first_death is not None and any(
                               verdicts[i] is None for i in range(first_death - 1) if first["knots_n"][i]),
                           "undecided_after": fate in ("F1", "F2") and first_death is not None
                               and any(value is None for value in verdicts[first_death:])})
            if result["s1"] and fate != "F0":
                raise ValueError(f"s=1 description has a knot: {row['key_id']}")
            if row["fate"] != fate:
                changed_fates.append({"key_id": row["key_id"], "pattern_hash": pattern_hash,
                                      "before": row["fate"], "after": fate})
            merged[row["key_id"]] = result
    return merged, {"patterns": len(groups), "conflicts": [], "resolved_pattern_levels": len(resolutions),
                    "resolved_description_levels": resolved_description_levels,
                    "resolutions": resolutions, "changed_description_fates": changed_fates,
                    "rule": "any decided verdict at each level; contradictory decided verdicts stop the summary"}


def group_patterns(records: Iterable[dict[str, Any]], split_class: bool = False) -> list[dict[str, Any]]:
    """Unsplit units use hashes; every class split uses (hash, rel_class).

    Repeated records represent empirical draws and contribute frequency, while
    distinct descriptions alone determine labels. Key comparison is numeric.
    """
    groups: dict[tuple[str, ...], list[dict[str, Any]]] = defaultdict(list)
    for row in records:
        identity = (row["pattern_hash"], row["rel_class"]) if split_class else (row["pattern_hash"],)
        groups[identity].append(row)
    units = []
    for identity, draws in sorted(groups.items()):
        members = sorted({row["key_id"]: row for row in draws}.values(), key=lambda row: row["key"])
        first = members[0]
        # Only scientific fields enter a summary unit; timings remain in raw records.
        row = {field: first[field] for field in (
            "pattern_hash", "knots_n", "join_n", "verdict_n", "fate", "first_death", "return",
            "rho_max", "rho12", "density_bin", "join_growth", "null_before_death", "undecided_after")}
        row.update({"unit_id": list(identity), "rel_class": first["rel_class"] if split_class else None,
                    "relative_classes": sorted({member["rel_class"] for member in members}),
                    "rel_degrees": sorted({member.get("rel_degree") for member in members}, key=canonical),
                    "cluster": first["cluster"], "automaton_class": first["automaton_class"],
                    "letter_class": first["letter_class"], "letter_degree": first.get("letter_degree"),
                    "first_key_id": first["key_id"], "first_key": first["key"],
                    "s": min(member["s"] for member in members),
                    "single_placement": any(member["single_placement"] for member in members),
                    "first_letter_settled": any(member["first_letter_settled"] for member in members),
                    "settled": any(member["settled"] for member in members),
                    "description_count": len(members), "draw_frequency": len(draws),
                    "representations": members})
        row["s1"] = row["s"] == 1
        row["settled_union"] = row["s1"] or row["settled"]
        units.append(row)
    return units


def expand_draws(units: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    return [unit for unit in units for _ in range(unit["draw_frequency"])]


def fate_table(rows: list[dict[str, Any]], denominator: int | None = None) -> dict[str, Any]:
    counts = Counter(row["fate"] for row in rows)
    denominator = len(rows) if denominator is None else denominator
    return {"units_with_fate": len(rows), "denominator": denominator,
            "counts": {fate: counts[fate] for fate in FATES},
            "shares": {fate: counts[fate] / denominator if denominator else None for fate in FATES},
            "status": "computed"}


def count_fates(units: list[dict[str, Any]]) -> dict[str, Any]:
    return {**fate_table(units), "distinct_patterns": len(units), "ambiguous_pattern_count": 0}


def census_shares(items: list[dict[str, Any]], coverage: dict[str, Any]) -> dict[str, Any]:
    result = {}
    for population in ("W", "E"):
        units = group_patterns(item["record"] for item in items if item["population"] == population)
        draws = expand_draws(units)
        section = {"raw_distinct_patterns": count_fates(units),
                   "accepted_draw_frequencies": fate_table(draws),
                   "s_condition_rule": "least s among descriptions of the unsplit pattern unit"}
        if population == "W":
            raw_mass = fate_table(draws, coverage["draws"].get("W", 0))
            raw_mass["unresolved_or_rejected_draws"] = coverage["draws"].get("W", 0) - len(draws)
            section["raw_fair_coin_draw_mass"] = raw_mass
        for minimum_s in (2, 3):
            selected = [unit for unit in units if unit["s"] >= minimum_s]
            section[f"given_s_ge_{minimum_s}"] = {
                "distinct_patterns": count_fates(selected),
                "draw_frequencies": fate_table(expand_draws(selected))}
        section["given_density_bin"] = [
            {"bin": label, "distinct_patterns": count_fates([u for u in units if u["density_bin"] == i]),
             "draw_frequencies": fate_table(expand_draws(u for u in units if u["density_bin"] == i))}
            for i, label in enumerate(BIN_LABELS)]
        result[population] = section
    return result


def settled_summary(items: list[dict[str, Any]], coverage: dict[str, Any]) -> dict[str, Any]:
    result = {}
    for population in ("W", "E"):
        units = group_patterns(item["record"] for item in items if item["population"] == population)
        draw_count = sum(unit["draw_frequency"] for unit in units)
        flags = []
        denominator = coverage["draws"].get(population, 0)
        for field in ("s1", "single_placement", "first_letter_settled", "settled_union"):
            yes = [unit for unit in units if unit[field]]
            frequency = sum(unit["draw_frequency"] for unit in yes)
            flags.append({"flag": field, "draws": frequency,
                          "fair_coin_draw_mass" if population == "W" else "draw_share":
                              frequency / denominator if denominator else None,
                          "accepted_draw_share": frequency / draw_count if draw_count else None,
                          "distinct_patterns_true": len(yes), "ambiguous_distinct_patterns": 0,
                          "status": "computed"})
        result[population] = {"flags_overlap": True, "draw_denominator": denominator, "flags": flags,
                              "settled_rule": "any description in the unit is single-placement or first-letter-settled",
                              "unsettled_draw_fates": fate_table(expand_draws(u for u in units if not u["settled_union"]))}
    return result


def descriptive_stats(rows: list[dict[str, Any]]) -> dict[str, Any]:
    hist = Counter(row["first_death"] for row in rows)
    curves = []
    for i in range(LEVELS):
        first_deaths = sum(row["first_death"] is not None and row["first_death"] <= i + 1 for row in rows)
        curves.append({"level": i + 1, "first_death_by_level": first_deaths,
                       "first_death_share": first_deaths / len(rows) if rows else None,
                       "dead_at_level": sum(row["verdict_n"][i] == 0 for row in rows),
                       "undecided_at_level": sum(row["verdict_n"][i] is None for row in rows),
                       "empty_at_level": sum(row["knots_n"][i] == 0 for row in rows)})
    ratios_11 = [row["join_n"][10] / row["join_n"][9] for row in rows if row["join_n"][9] != 0]
    ratios_12 = [row["join_n"][11] / row["join_n"][10] for row in rows if row["join_n"][10] != 0]
    growth = Counter(row["join_growth"] for row in rows)
    return {"units": len(rows), "fates": fate_table(rows),
            "mean_rho_max": mean(row["rho_max"] for row in rows), "mean_rho12": mean(row["rho12"] for row in rows),
            "first_death_histogram": {str(level): hist[level] for level in range(1, LEVELS + 1)},
            "no_observed_death": hist[None], "death_by_level": curves,
            "mean_knots_n": [mean(row["knots_n"][i] for row in rows) for i in range(LEVELS)],
            "joining": {"mean_J10": mean(row["join_n"][9] for row in rows),
                        "mean_J11": mean(row["join_n"][10] for row in rows),
                        "mean_J12": mean(row["join_n"][11] for row in rows),
                        "mean_J11_over_J10_nonzero_denominator": mean(ratios_11),
                        "mean_J12_over_J11_nonzero_denominator": mean(ratios_12),
                        "J10_zero": sum(row["join_n"][9] == 0 for row in rows),
                        "J11_zero": sum(row["join_n"][10] == 0 for row in rows),
                        "growth_counts": {label: growth[label] for label in ("constant", "grows", "other")}},
            "null_verdicts_n": [curve["undecided_at_level"] for curve in curves]}


def descriptive_tables(items: list[dict[str, Any]]) -> dict[str, Any]:
    result = {}
    for population in ("W", "E"):
        source = [item["record"] for item in items if item["population"] == population]
        unsplit = group_patterns(source)
        class_units = group_patterns(source, split_class=True)
        sections = []
        for weighted in (False, True):
            for class_field in (None, "rel_class", "letter_class"):
                units = class_units if class_field else unsplit
                for activity in CLASSES if class_field else ("all",):
                    for bin_index in (None, *range(len(BIN_LABELS))):
                        selected = [unit for unit in units if (class_field is None or unit[class_field] == activity)
                                    and (bin_index is None or unit["density_bin"] == bin_index)]
                        stats = descriptive_stats(expand_draws(selected) if weighted else selected)
                        stats.update({"unit": "draw_frequencies" if weighted else
                                      "pattern_relative_class" if class_field else "distinct_patterns",
                                      "class_variable": class_field or "none", "activity_class": activity,
                                      "density_bin": BIN_LABELS[bin_index] if bin_index is not None else "all",
                                      "status": "computed", "ambiguous_patterns_affecting_group": 0,
                                      "determined_members_only": False})
                        sections.append(stats)
        result[population] = {"death_after_level_12": "censored; no all-level inference", "groups": sections}
    return result


def exact_activity_inventory(items: list[dict[str, Any]]) -> dict[str, Any]:
    result = {}
    for population in ("W", "E"):
        units = group_patterns((item["record"] for item in items if item["population"] == population), split_class=True)
        result[population] = {}
        for class_field, degree_field in (("rel_class", "rel_degrees"), ("letter_class", "letter_degree")):
            memberships, frequencies = Counter(), Counter()
            for unit in units:
                degrees = unit[degree_field] if class_field == "rel_class" else [unit[degree_field]]
                for degree in degrees:
                    label = unit[class_field], degree
                    memberships[label] += 1
                    frequencies[label] += unit["draw_frequency"]
            result[population][class_field] = {
                "rows": [{"class": activity, "degree": degree,
                          "class_units_with_degree": memberships[(activity, degree)],
                          "member_unit_draw_frequency": frequencies[(activity, degree)]}
                         for activity, degree in sorted(memberships, key=canonical)],
                "units_with_multiple_relative_degrees": [
                    {"unit_id": unit["unit_id"], "degrees": unit["rel_degrees"]}
                    for unit in units if len(unit["rel_degrees"]) > 1] if class_field == "rel_class" else [],
                "degree_note": "Relative degree memberships can overlap within a (pattern hash, rel_class) unit; "
                               "the primary polynomial arm is one class. Letter class and degree use the first description."}
    return result


def null_summary(rows: Iterable[dict[str, Any]]) -> dict[str, Any]:
    rows = list(rows)
    with_null = [row for row in rows if None in row["verdict_n"]]
    return {"units": len(rows), "units_with_any_null_verdict": len(with_null),
            "null_level_verdicts": sum(row["verdict_n"].count(None) for row in rows),
            "FU_death_unresolved_units": sum(row["fate"] == "FU" for row in rows),
            "forced_F1_F2_units_with_later_null": sum(row["fate"] in ("F1", "F2") for row in with_null),
            "null_verdicts_n": [sum(row["verdict_n"][i] is None for row in rows) for i in range(LEVELS)],
            "note": "A null after an already forced F1 or F2 does not turn that fate into FU."}


def arm_stats(rows: list[dict[str, Any]], weighted: bool = False) -> dict[str, Any]:
    counts = Counter(row["fate"] for row in rows)
    weights = [row["draw_frequency"] if weighted else 1 for row in rows]
    total = sum(weights)
    weighted_counts = {fate: sum(w for row, w in zip(rows, weights) if row["fate"] == fate) for fate in FATES}
    cluster_counts = Counter(row["cluster"] for row in rows)
    decided = sum(counts[fate] for fate in ("F1", "F2", "F3"))
    decided_clusters = {row["cluster"] for row in rows if row["fate"] in ("F1", "F2", "F3")}
    return {"unit": "pattern_relative_class", "units": len(rows),
            "distinct_patterns": len({row["pattern_hash"] for row in rows}),
            "decided": decided, "FU": counts["FU"],
            "FU_share": counts["FU"] / len(rows) if rows else None,
            "automaton_classes": len(cluster_counts), "decided_automaton_classes": len(decided_clusters),
            "automaton_class_counts": dict(sorted(cluster_counts.items())),
            "fates": {fate: counts[fate] for fate in FATES}, "weight": total,
            "weight_unit": "accepted_W_draw_frequency" if weighted else "class_unit_count",
            "weighted_fates": weighted_counts,
            "mean_rho_max": sum(row["rho_max"] * w for row, w in zip(rows, weights)) / total if total else None,
            "mean_rho12": sum(row["rho12"] * w for row, w in zip(rows, weights)) / total if total else None,
            "null_verdicts_n": [sum(row["verdict_n"][i] is None for row in rows) for i in range(LEVELS)],
            "death_share_FU_alive": (weighted_counts["F1"] + weighted_counts["F2"]) / total if total else None,
            "death_share_FU_dead": (weighted_counts["F1"] + weighted_counts["F2"] + weighted_counts["FU"]) / total if total else None}


def ordinary_eligible(stats: dict[str, Any]) -> bool:
    return (stats["decided"] >= 30 and stats["decided_automaton_classes"] >= 5
            and stats["FU_share"] is not None and stats["FU_share"] < 0.10)


def quantile(sorted_values: list[float], probability: float) -> float:
    position = (len(sorted_values) - 1) * probability
    lo = math.floor(position)
    hi = math.ceil(position)
    return sorted_values[lo] * (hi - position) + sorted_values[hi] * (position - lo) if lo != hi else sorted_values[lo]


def bootstrap_deltas(left: list[dict[str, Any]], right: list[dict[str, Any]], rng: random.Random,
                     unit: str = "automaton_class") -> dict[str, list[float]]:
    """E resamples automaton classes; W resamples individual empirical draws.

    Arms are resampled independently.  The same sampled units supply both FU
    assignments, so their disagreement reflects response treatment rather than
    two unrelated Monte Carlo samples.
    """
    arms = []
    for rows in (left, right):
        if unit == "draw":
            arms.append([[int(row["fate"] in ("F1", "F2")), int(row["fate"] == "FU"), 1]
                         for row in rows])
            continue
        if unit != "automaton_class":
            raise ValueError(f"unknown bootstrap unit {unit!r}")
        totals: dict[str, list[int]] = defaultdict(lambda: [0, 0, 0])
        for row in rows:
            aggregate = totals[row["cluster"]]
            aggregate[0] += row["fate"] in ("F1", "F2")
            aggregate[1] += row["fate"] == "FU"
            aggregate[2] += 1
        arms.append([totals[cluster] for cluster in sorted(totals)])
    draws = {"FU_alive": [], "FU_dead": []}
    # NumPy is optional.  Batched index arrays avoid a large B-by-cluster allocation.
    try:
        import numpy as np
    except ImportError:
        np = None
    if np is not None:
        generator = np.random.default_rng(rng.getrandbits(64))
        arrays = [np.asarray(arm, dtype=np.int64) for arm in arms]
        for start in range(0, BOOTSTRAPS, 64):
            batch = min(64, BOOTSTRAPS - start)
            sampled = []
            for array in arrays:
                indices = generator.integers(0, len(array), size=(batch, len(array)))
                sampled.append(array[indices].sum(axis=1))
            for assignment, fu_multiplier in (("FU_alive", 0), ("FU_dead", 1)):
                a, b = sampled
                delta = (a[:, 0] + fu_multiplier * a[:, 1]) / a[:, 2] - (b[:, 0] + fu_multiplier * b[:, 1]) / b[:, 2]
                draws[assignment].extend(float(value) for value in delta)
    else:
        for _ in range(BOOTSTRAPS):
            sampled = []
            for arm in arms:
                total = [0, 0, 0]
                for _ in range(len(arm)):
                    selected = arm[rng.randrange(len(arm))]
                    for index in range(3):
                        total[index] += selected[index]
                sampled.append(total)
            a, b = sampled
            draws["FU_alive"].append(a[0] / a[2] - b[0] / b[2])
            draws["FU_dead"].append((a[0] + a[1]) / a[2] - (b[0] + b[1]) / b[2])
    return {assignment: sorted(samples) for assignment, samples in draws.items()}


def assignment_verdict(delta: float, interval95: list[float], corrected: list[float]) -> str:
    if (corrected[1] < 0 or corrected[0] > 0) and abs(delta) >= 0.10:
        return "differs"
    if interval95[0] >= -0.10 and interval95[1] <= 0.10:
        return "same"
    return "unclear"


def matched_analysis(items: list[dict[str, Any]], population: str, exclude_settled: bool,
                     rng: random.Random) -> dict[str, Any]:
    units = group_patterns((item["record"] for item in items if item["population"] == population), split_class=True)
    f0 = [unit for unit in units if unit["fate"] == "F0"]
    settled = [unit for unit in units if unit["fate"] != "F0" and exclude_settled and unit["settled"]]
    rows = [unit for unit in units if unit["fate"] != "F0" and (not exclude_settled or not unit["settled"])]
    weighted = population == "W"
    cells, cell_rows = [], []
    for bin_index, label in enumerate(BIN_LABELS):
        exponential = [row for row in rows if row["density_bin"] == bin_index and row["rel_class"] == "exponential"]
        for comparator in COMPARATORS:
            comparison = [row for row in rows if row["density_bin"] == bin_index and row["rel_class"] == comparator]
            left_stats, right_stats = arm_stats(comparison, weighted), arm_stats(exponential, weighted)
            eligible = ordinary_eligible(left_stats) and ordinary_eligible(right_stats)
            cells.append({"bin_index": bin_index, "bin": label, "C": comparator,
                          "exponential": right_stats, "comparison": left_stats, "eligible": eligible,
                          "status": "eligible" if eligible else "ineligible", "assignments": {}, "verdict": None})
            cell_rows.append((comparison, exponential))
    family_m = sum(cell["eligible"] for cell in cells)
    for cell, (left, right) in zip(cells, cell_rows):
        bootstrap = bootstrap_deltas(expand_draws(left) if weighted else left,
                                     expand_draws(right) if weighted else right,
                                     rng, "draw" if weighted else "automaton_class") if cell["eligible"] else None
        for assignment in ("FU_alive", "FU_dead"):
            field = "death_share_" + assignment
            shares = [cell[arm][field] for arm in ("comparison", "exponential")]
            delta = shares[0] - shares[1] if all(value is not None for value in shares) else None
            outcome = {"delta": delta, "interval95": None, "bonferroni_interval": None,
                       "bonferroni_m": family_m, "verdict": "ineligible"}
            if bootstrap is not None:
                samples = bootstrap[assignment]
                interval95 = [quantile(samples, 0.025), quantile(samples, 0.975)]
                tail = 0.05 / (2 * family_m)
                corrected = [quantile(samples, tail), quantile(samples, 1 - tail)]
                outcome.update({"interval95": interval95, "bonferroni_interval": corrected,
                                "bonferroni_confidence": 1 - 0.05 / family_m,
                                "verdict": assignment_verdict(delta, interval95, corrected)})
            cell["assignments"][assignment] = outcome
        if cell["eligible"]:
            verdicts = {case["verdict"] for case in cell["assignments"].values()}
            cell["verdict"] = next(iter(verdicts)) if len(verdicts) == 1 else "unclear"
            cell["status"] = "computed"
    return {"population": population, "unit": "pattern_relative_class",
            "weighting": "summed accepted W draw frequencies" if weighted else "unweighted class units",
            "eligibility_unit": "class units, including FU fraction and decided automaton-class counts",
            "settled_excluded": exclude_settled, "F0_excluded": True,
            "F0_units_excluded": len(f0), "F0_draws_excluded": sum(unit["draw_frequency"] for unit in f0),
            "settled_units_excluded_after_F0": len(settled),
            "settled_draws_excluded_after_F0": sum(unit["draw_frequency"] for unit in settled),
            "FU_retained": True, "bootstrap_resamples": BOOTSTRAPS, "bootstrap_seed": BOOTSTRAP_SEED,
            "bootstrap_unit": "draw" if weighted else "automaton_class",
            "bootstrap_cluster": None if weighted else "first-description automaton class, independently within each arm",
            "bootstrap_scheme": "iid empirical W draws, independently within each arm" if weighted else
                "automaton-class cluster resampling, independently within each arm, retaining within-cluster sizes",
            "eligible_cells": family_m, "eligibility_unknown_cells": 0, "bonferroni_m": family_m,
            "bonferroni_family": "eligible cells within this population and settled-exclusion analysis", "cells": cells}


def predictions(key_rows: dict[str, dict[str, Any]], primary: dict[str, Any],
                coverage_complete: bool) -> dict[str, Any]:
    rows = list(key_rows.values())
    f0 = [row for row in rows if row["fate"] == "F0"]
    settled_f0 = [row for row in f0 if row["settled"]]
    settled = [row for row in rows if row["fate"] != "F0" and row["settled"]]
    p1_failures = [row for row in settled if row["fate"] != "F3"]
    returns = [row for row in rows if row["return"]]
    late = [row for row in rows if not row["settled"] and row["rel_class"] == "exponential"
            and row["first_death"] is not None and row["first_death"] >= 9 and not row["null_before_death"]]
    late_open = [row for row in rows if not row["settled"] and row["rel_class"] == "exponential"
                 and row["first_death"] is not None and row["first_death"] >= 9 and row["null_before_death"]]
    hd_fail = [cell for cell in primary["cells"] if cell["eligible"] is True and cell["verdict"] == "differs"]
    unresolved = [cell for cell in primary["cells"] if cell["eligible"] is None or
                  cell["eligible"] is True and (cell["verdict"] or "").startswith("skipped")]
    bound_cells = [cell for cell in primary["cells"] if cell["C"] == "bounded" and cell["bin_index"] >= 2]
    eligible_bound = [cell for cell in bound_cells if cell["eligible"] is True]
    bound_unknown = [cell for cell in bound_cells if cell["eligible"] is None]
    bound_fail, direction_open = [], []
    for cell in eligible_bound:
        if cell["verdict"] == "same":
            bound_fail.append(cell)
        elif cell["verdict"] == "differs":
            deltas = [case["delta"] for case in cell["assignments"].values()]
            if all(delta > 0 for delta in deltas):
                bound_fail.append(cell)
            elif not all(delta < 0 for delta in deltas):
                direction_open.append(cell)
    if bound_fail:
        hbound = "fails"
    elif not eligible_bound and not bound_unknown:
        hbound = "not_testable_at_s_le_3" if coverage_complete else "not_testable_in_observed_subset"
    elif bound_unknown or direction_open or any((cell["verdict"] or "").startswith("skipped") for cell in eligible_bound):
        hbound = "unresolved_ambiguity"
    else:
        hbound = "no_failure_observed"
    hdens = "fails" if hd_fail else ("unresolved_ambiguity" if unresolved else "no_failure_observed")
    observed_hdens, observed_hbound = hdens, hbound
    if not coverage_complete:
        hdens = ("observed_subset_failure_signal" if hd_fail else
                 "observed_subset_unresolved_ambiguity" if unresolved else
                 "not_testable_in_observed_subset" if primary["eligible_cells"] == 0 else
                 "observed_subset_no_failure_signal")
        hbound = ("observed_subset_failure_signal" if bound_fail else
                  "observed_subset_unresolved_ambiguity" if hbound == "unresolved_ambiguity" else
                  "not_testable_in_observed_subset" if not eligible_bound else
                  "observed_subset_no_failure_signal")
    def refs(cells: list[dict[str, Any]]) -> list[dict[str, str]]:
        return [{"bin": cell["bin"], "C": cell["C"], "verdict": cell["verdict"]} for cell in cells]
    return {
        "scope": "registered population" if coverage_complete else "observed complete keys only; incomplete registered coverage",
        "P1": {"status": "fails_run_invalid" if p1_failures else "no_failure_observed",
               "descriptions_checked": len(settled), "descriptions_excluded_F0": len(f0),
               "settled_descriptions_excluded_F0": len(settled_f0),
               "s1_descriptions_excluded_F0": sum(row["s1"] for row in f0),
               "non_F3_count": len(p1_failures),
               "failing_key_ids": [row["key_id"] for row in p1_failures],
               "invalidates_run": bool(p1_failures),
               "note": "P1 applies only to descriptions with a knot; F0 descriptions, including s=1, are excluded and counted."},
        "P2": {"status": "fails_return_observed" if returns else "no_return_observed", "returns": len(returns),
               "key_ids": [row["key_id"] for row in returns]},
        "P4": {"status": "observed" if late else ("undecided_earlier_levels" if late_open else ("fails" if coverage_complete else "not_observed_in_incomplete_coverage")),
               "qualifying_keys": [row["key_id"] for row in late],
               "late_first_observed_death_with_earlier_null": [row["key_id"] for row in late_open]},
        "H-dens": {"status": hdens,
                   "registered_status": observed_hdens if coverage_complete else "not_evaluated_in_incomplete_coverage",
                   "observed_cell_signal": observed_hdens,
                   "failure_cells": refs(hd_fail), "eligible_cells": primary["eligible_cells"]},
        "H-bound": {"status": hbound,
                    "registered_status": observed_hbound if coverage_complete else "not_evaluated_in_incomplete_coverage",
                    "observed_cell_signal": observed_hbound, "failure_cells": refs(bound_fail),
                    "eligible_bounded_cells_rho_max_ge_1_5": len(eligible_bound),
                    "eligibility_unknown_bounded_cells_rho_max_ge_1_5": len(bound_unknown),
                    "direction_unresolved_cells": refs(direction_open)},
    }


def logistic_matrix(items: list[dict[str, Any]], population: str) -> dict[str, Any]:
    units = group_patterns((item["record"] for item in items if item["population"] == population), split_class=True)
    rows = [unit for unit in units if unit["fate"] != "F0" and not unit["settled"]]
    columns = ["intercept", "class_bounded", "class_polynomial", "class_exponential"] + [
        f"density_bin_{i}" for i in range(1, len(BIN_LABELS))]
    available = importlib.util.find_spec("statsmodels") is not None
    assignments = {}
    for assignment, fu_is_dead in (("FU_alive", False), ("FU_dead", True)):
        matrix = []
        for row in rows:
            response = int(row["fate"] in ("F1", "F2") or fu_is_dead and row["fate"] == "FU")
            x = [1] + [int(row["rel_class"] == activity) for activity in CLASSES[1:]] + [
                int(row["density_bin"] == i) for i in range(1, len(BIN_LABELS))]
            matrix.append({"unit_id": row["unit_id"], "pattern_hash": row["pattern_hash"],
                           "rel_class": row["rel_class"], "first_key_id": row["first_key_id"],
                           "death": response, "fate": row["fate"],
                           "automaton_class": row["cluster"], "X": x,
                           "frequency_weight": row["draw_frequency"] if population == "W" else 1})
        if not available:
            fit = {"status": "skipped_statsmodels_unavailable", "matrix_location": "this assignment's design_matrix"}
        elif not matrix:
            fit = {"status": "skipped_no_eligible_data"}
        else:
            try:
                import numpy as np
                import statsmodels.api as sm
                x = np.asarray([row["X"] for row in matrix], dtype=float)
                y = np.asarray([row["death"] for row in matrix], dtype=float)
                weights = np.asarray([row["frequency_weight"] for row in matrix], dtype=float)
                clusters = [row["automaton_class"] for row in matrix]
                fitted = sm.GLM(y, x, family=sm.families.Binomial(), freq_weights=weights).fit(
                    cov_type="cluster", cov_kwds={"groups": clusters})
                fit = {"status": "computed", "coefficients": fitted.params.tolist(),
                       "cluster_robust_standard_errors": fitted.bse.tolist(), "p_values": fitted.pvalues.tolist(),
                       "interval95": fitted.conf_int().tolist(), "converged": bool(fitted.converged)}
            except Exception as error:
                fit = {"status": "failed", "error": str(error), "error_type": type(error).__name__}
        assignments[assignment] = {"response": "FU as dead" if fu_is_dead else "FU as alive",
                                   "design_matrix": matrix, "fit": fit}
    return {"population": population, "unit": "pattern_relative_class", "settled_excluded": True,
            "F0_excluded": True, "reference_class": "finitary", "reference_density_bin": BIN_LABELS[0],
            "columns": columns, "cluster_variable": "first-description automaton_class",
            "FU": sum(row["fate"] == "FU" for row in rows), "statsmodels_available": available,
            "assignments": assignments}


def fmt(value: Any) -> str:
    if value is None:
        return "—"
    if isinstance(value, float):
        return f"{value:.4f}"
    return str(value).replace("|", "\\|").replace("\n", " ")


def table(headers: list[str], rows: Iterable[Iterable[Any]]) -> list[str]:
    return ["| " + " | ".join(headers) + " |", "| " + " | ".join("---" for _ in headers) + " |"] + [
        "| " + " | ".join(fmt(value) for value in row) + " |" for row in rows]


def render_markdown(summary: dict[str, Any], json_name: str = "summary.json") -> str:
    lines = ["# Frozen addressed-census summary", "", summary["scope_note"], "",
             "W weights are ordinary empirical fair-coin draw frequencies. Code lengths are never multiplied into those frequencies.", "",
             "## Coverage and validation", ""]
    coverage = summary["coverage"]
    lines += table(["Population", "Draws present", "Registered draws", "Draws with complete key"], [
        (population, coverage["draws"].get(population, 0), coverage["registered_draws"][population],
         coverage["accepted_draws_with_complete_keys"].get(population, 0)) for population in ("W", "E")])
    lines += ["", f"Coverage complete: {coverage['registered_coverage_complete']}. Validation: {summary['validation']['status']}. "
              f"Required core gate checks passed: {summary['validation']['required_core_gate_checks_passed']}. "
              f"All assertions passed: {summary['validation']['all_assertions_passed']}.",
              f"Validation record: {fmt(summary['validation'].get('path'))}. " + (summary['validation'].get('skipped_assertion_disclosure') or ""),
              "Missing keys, rejected draws, duplicate identities, and record errors are retained in summary.json.", "",
              f"Solver budgets: {summary['solver_undecided']['complete_keys']['null_level_verdicts']} null level verdicts in "
              f"{summary['solver_undecided']['complete_keys']['units_with_any_null_verdict']} complete keys; "
              f"{summary['solver_undecided']['complete_keys']['FU_death_unresolved_units']} FU keys. "
              "A later null preserves an already determined F1 or F2.", "",
              "## Fate shares", ""]
    fate_rows = []
    for population, section in summary["fate_shares"].items():
        groups = [("raw distinct patterns", section["raw_distinct_patterns"]),
                  ("accepted draw frequencies", section["accepted_draw_frequencies"])]
        if population == "W":
            groups.append(("all W draw mass", section["raw_fair_coin_draw_mass"]))
        for minimum_s in (2, 3):
            part = section[f"given_s_ge_{minimum_s}"]
            groups += [(f"s >= {minimum_s}, distinct", part["distinct_patterns"]),
                       (f"s >= {minimum_s}, draws", part["draw_frequencies"])]
        for part in section["given_density_bin"]:
            groups += [(part["bin"] + ", distinct", part["distinct_patterns"]),
                       (part["bin"] + ", draws", part["draw_frequencies"])]
        for label, part in groups:
            shares = part.get("shares", {})
            fate_rows.append([population, label, part.get("denominator"), *[shares.get(fate) for fate in FATES], part.get("status", "computed")])
    lines += table(["Population", "Condition and unit", "Denominator", *FATES, "Status"], fate_rows)
    lines += ["", "Rejected or missing W draws retain their mass outside the five fate cells. Accepted-draw fractions are shown separately. "
              "Unsplit counts use pattern hashes; s conditions use each pattern unit's least s, including for its summed draw frequency.", "",
              "## Settled weight", ""]
    settled_rows = []
    for population, section in summary["settled"].items():
        for flag in section["flags"]:
            settled_rows.append([population, flag["flag"], flag["draws"], flag.get("fair_coin_draw_mass", flag.get("draw_share")),
                                 flag["accepted_draw_share"], flag["distinct_patterns_true"], flag["ambiguous_distinct_patterns"]])
    lines += table(["Population", "Flag (overlaps allowed)", "Draws", "Raw draw mass/share", "Accepted share", "Distinct true", "Ambiguous patterns"], settled_rows)
    lines += ["", "The union includes s = 1, single distinct placement, and first-letter-settled. "
              "The primary comparison excludes single-placement and first-letter-settled units; F0 is separately excluded.", "",
              "## Joining and death summaries", "",
              "The measured joining counts do not assign activity class. Complete first-death histograms and death-by-level curves "
              "for every relative class, letter class, density bin, and class-by-bin group are in summary.json. "
              "Deaths after level 12 are censored.", ""]
    growth_rows = []
    death_rows = []
    for population, section in summary["descriptive"].items():
        for group in section["groups"]:
            if group["density_bin"] != "all" or group["class_variable"] != "rel_class":
                continue
            join = group["joining"]
            growth_rows.append([population, group["unit"], group["activity_class"], group["units"], group["mean_rho_max"], group["mean_rho12"],
                                join["mean_J10"], join["mean_J11"], join["mean_J12"], group["status"]])
            death_rows.append([population, group["unit"], group["activity_class"],
                               ", ".join(str(group["first_death_histogram"][str(n)]) for n in range(1, LEVELS + 1)), group["no_observed_death"]])
    lines += table(["Population", "Unit", "Relative class", "Units", "Mean rho_max", "Mean rho12", "Mean J10", "Mean J11", "Mean J12", "Status"], growth_rows)
    lines += [""] + table(["Population", "Unit", "Relative class", "First deaths at levels 1 through 12", "No observed death"], death_rows)
    lines += ["", "## Matched-density comparisons", "",
              "Each eligible E cell uses 2,000 automaton-class cluster resamples; W instead uses 2,000 resamples of empirical draws, "
              "independently within each arm, seed 20261115. "
              "FU remains in the denominator and is assigned dead and alive separately. A combined verdict requires agreement. "
              "Eligibility counts class units; W death shares use draw frequency. The correction family is the eligible cells within each displayed analysis.", ""]
    for name, analysis in summary["matched_density"].items():
        lines += [f"### {name}", "", f"Eligible cells: {analysis['eligible_cells']}; eligibility unknown: {analysis['eligibility_unknown_cells']}; "
                  f"Bonferroni m: {fmt(analysis['bonferroni_m'])}.", ""]
        cell_rows = []
        for cell in analysis["cells"]:
            left, right = cell["comparison"], cell["exponential"]
            assignments = cell["assignments"]
            for assignment in ("FU_alive", "FU_dead"):
                outcome = assignments.get(assignment, {})
                cell_rows.append([cell["bin"], cell["C"], assignment, left["units"], right["units"], left["decided"], right["decided"],
                                  f"{left['FU']}/{right['FU']}", f"{left['decided_automaton_classes']}/{right['decided_automaton_classes']}",
                                  outcome.get("delta"), outcome.get("interval95"), outcome.get("bonferroni_interval"), cell["eligible"],
                                  outcome.get("verdict", cell["status"]), cell["verdict"]])
        lines += table(["Bin", "C", "FU assignment", "C units", "Exp units", "C decided", "Exp decided", "FU C/exp", "Decided clusters C/exp", "Delta", "95%", "Corrected", "Eligible", "Assignment verdict", "Combined"], cell_rows)
        lines += [""]
    lines += ["## Frozen predictions", ""]
    lines += table(["Rule", "Observed status"], [(rule, outcome["status"]) for rule, outcome in summary["predictions"].items() if isinstance(outcome, dict)])
    lines += ["", "P1 failures and excluded F0 counts, P2 returns, P4 witnesses, and H-dens/H-bound failure cells are listed by key or cell in summary.json. "
              "An incomplete census cannot establish an absence across the registered population.", "",
              "## Logistic sensitivity", ""]
    lines += table(["Population", "FU assignment", "Matrix rows", "FU units", "Fit"], [
        (population, assignment, len(case["design_matrix"]), section["FU"], case["fit"]["status"])
        for population, section in summary["logistic"].items() for assignment, case in section["assignments"].items()])
    lines += ["", "Both design matrices, first-description cluster labels, frequency weights and column definitions "
              "are stored in summary.json. FU is assigned alive and dead separately; no null response is fitted.", "",
              "## Addendum unit rules", "",
              "Every class split, including the secondary letter-class split, uses (pattern hash, relative class). "
              "Automaton class and letter class come from the first description in numeric sorted key order within the unit. "
              "Settled means any member is single-placement or first-letter-settled. s is the least member s. "
              "Relative polynomial degrees are retained as memberships, without duplicating a primary class unit.", "",
              "Verdicts are merged across all descriptions of a pattern before any summary; contradictory decided verdicts "
              "stop the program and list their pattern hashes, levels and key IDs. "
              f"Resolved pattern-level nulls: {summary['verdict_merge']['resolved_pattern_levels']}. "
              f"Resolved description-level nulls: {summary['verdict_merge']['resolved_description_levels']}.", "",
              "All eleven original ambiguities are resolved by codex_spec_addendum.md. "
              "No claim extends beyond the twelve levels read.", ""]
    return "\n".join(lines).replace("summary.json", json_name)


def build_summary(directory: Path) -> dict[str, Any]:
    items, raw_keys, coverage = load_records(directory)
    keys, merge = merge_pattern_verdicts(raw_keys)
    items = [{**item, "record": keys[item["record"]["key_id"]]} for item in items]
    validation = validation_summary(directory)
    shares = census_shares(items, coverage)
    settled = settled_summary(items, coverage)
    descriptive = descriptive_tables(items)
    inventory = exact_activity_inventory(items)
    rng = random.Random(BOOTSTRAP_SEED)
    matched = {}
    for population in ("E", "W"):
        for exclude in (True, False):
            name = f"{population}_{'settled_excluded' if exclude else 'settled_included'}"
            matched[name] = matched_analysis(items, population, exclude, rng)
    used_keys = {item["record"]["key_id"]: item["record"] for item in items}
    coverage["complete_keys_not_referenced_by_observed_draws"] = len(set(keys) - set(used_keys))
    prediction = predictions(used_keys, matched["E_settled_excluded"], coverage["registered_coverage_complete"])
    logistic = {population: logistic_matrix(items, population) for population in ("E", "W")}
    solver_undecided = {"raw_complete_keys": null_summary(raw_keys.values()),
                        "complete_keys": null_summary(used_keys.values()),
                        **{population + "_draws": null_summary(item["record"] for item in items if item["population"] == population)
                           for population in ("W", "E")}}
    metadata_fields = ("unit_id", "pattern_hash", "rel_class", "relative_classes", "rel_degrees", "cluster",
                       "letter_class", "letter_degree", "first_key_id", "first_key", "s", "s1", "settled",
                       "single_placement", "first_letter_settled", "description_count", "draw_frequency", "fate")
    unit_metadata = {}
    for population in ("W", "E"):
        source = [item["record"] for item in items if item["population"] == population]
        unsplit, class_units = group_patterns(source), group_patterns(source, split_class=True)
        unit_metadata[population] = {
            "distinct_patterns": len(unsplit), "pattern_relative_class_units": len(class_units),
            "class_units": [{field: unit[field] for field in metadata_fields} for unit in class_units],
            "unsplit_units": [{field: unit[field] for field in metadata_fields} for unit in unsplit]}
    return {"schema_version": 2, "levels": list(range(1, LEVELS + 1)),
            "preregistration": "research/ADDR-KNOTS-20261113-001/preregistration.md",
            "specification_addendum": "research/ADDR-KNOTS-20261113-001/codex_spec_addendum.md",
            "scope_note": "Registered coverage is complete." if coverage["registered_coverage_complete"] else
                "INCOMPLETE REGISTERED COVERAGE: all descriptive results below concern only observed complete key records. Missing keys and validation are not inferred.",
            "coverage": coverage, "validation": validation, "solver_undecided": solver_undecided,
            "verdict_merge": merge, "units": unit_metadata,
            "registered_run_ready_for_interpretation": coverage["registered_coverage_complete"]
                and validation["required_core_gate_checks_passed"] and not prediction["P1"]["invalidates_run"],
            "weighting": {"W": "ordinary empirical accepted draw frequency; no additional 2^-bits factor",
                          "rejected_W_draws": "excluded from weighted shares and bootstrap; counted separately, including raw draw mass outside fate cells",
                          "E": "unweighted (pattern hash, relative class) units for class-split inference",
                          "s_conditions": "least s of each unit; weighted conditionals sum all accepted draws of selected units"},
            "density_bins": [{"label": label, "lower_inclusive": BIN_LIMITS[i], "upper_exclusive": None if math.isinf(BIN_LIMITS[i + 1]) else BIN_LIMITS[i + 1]}
                             for i, label in enumerate(BIN_LABELS)],
            "fate_shares": shares, "settled": settled, "descriptive": descriptive,
            "exact_activity_classes": inventory, "matched_density": matched, "predictions": prediction,
            "logistic": logistic, "ambiguities": [],
            "authority": "finite computed census; no all-level theorem or change to the canonical knot test"}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    parser.add_argument("--output-prefix", default="summary", help="output filename prefix; use summary_v2 to preserve prior smoke summaries")
    args = parser.parse_args(argv)
    directory = args.directory
    if not directory.is_dir():
        parser.error("DIR must be an existing output directory")
    if Path(args.output_prefix).name != args.output_prefix or args.output_prefix in ("", ".", ".."):
        parser.error("--output-prefix must be a filename prefix")
    try:
        summary = build_summary(directory)
    except PatternVerdictConflict as error:
        print(json.dumps({"status": "stopped_contradictory_decided_verdicts", "conflicts": error.conflicts},
                         indent=2, sort_keys=True), file=sys.stderr)
        return 2
    json_path = directory / f"{args.output_prefix}.json"
    markdown_path = directory / f"{args.output_prefix}.md"
    json_path.write_text(json.dumps(summary, indent=2, sort_keys=True, allow_nan=False) + "\n")
    markdown_path.write_text(render_markdown(summary, json_path.name))
    print(json.dumps({"summary_json": str(json_path), "summary_md": str(markdown_path),
                      "coverage_complete": summary["coverage"]["registered_coverage_complete"],
                      "validation": summary["validation"]["status"],
                      "ambiguities": len(summary["ambiguities"]),
                      "registered_run_ready_for_interpretation": summary["registered_run_ready_for_interpretation"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
