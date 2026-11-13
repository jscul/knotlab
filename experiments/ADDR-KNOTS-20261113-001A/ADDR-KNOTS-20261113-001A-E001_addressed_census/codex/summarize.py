#!/usr/bin/env python3
"""Frozen level-12 addressed-census summary; no sampling or SAT work occurs here.

Usage: .venv/bin/python -B summarize.py DIR

Only the observed, complete key records contribute to descriptive tables.  Coverage
and validation are reported separately, so a smoke run remains useful without being
presented as the registered census.  All W weights are empirical draw frequencies.
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


class Ambiguities:
    def __init__(self) -> None:
        catalog = Path(__file__).with_name("summary_ambiguities.json")
        self.catalog = json.loads(catalog.read_text())
        self.questions = {row["id"]: row for row in self.catalog["questions"]}
        self.events: dict[str, dict[str, Any]] = {}

    def add(self, name: str, output: str, details: Any = None) -> None:
        question = self.questions[name]
        event = self.events.setdefault(name, {
            "id": name, "question": question["question"],
            "affected_outputs": [], "occurrences": 0, "examples": [],
        })
        if output not in event["affected_outputs"]:
            event["affected_outputs"].append(output)
        event["occurrences"] += 1
        if details is not None and len(event["examples"]) < 12:
            if details not in event["examples"]:
                event["examples"].append(details)

    def rows(self) -> list[dict[str, Any]]:
        return [self.events[name] for name in sorted(self.events)]


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
    key_rows: dict[str, dict[str, Any]] = {}
    serial_to_id: dict[str, str] = {}
    duplicate_records = 0
    files = sorted((directory / "keys").glob("worker-*.jsonl"))
    for path in files:
        for raw in read_jsonl(path, errors):
            row, problems = prepare_record(raw)
            if row is None:
                errors.append({"file": str(path), "key_id": raw.get("key_id"), "errors": problems})
                continue
            kid, serial = row["key_id"], canonical(row["key"])
            if kid in key_rows:
                # Wall time may differ on a replay; scientific fields may not.
                ignored = {"wall_n", "level_wall_n", "total_wall_seconds", "peak_rss_mb"}
                left = {k: v for k, v in key_rows[kid].items() if k not in ignored}
                right = {k: v for k, v in row.items() if k not in ignored}
                if left != right:
                    errors.append({"key_id": kid, "error": "conflicting repeated key records"})
                duplicate_records += 1
                continue
            if serial in serial_to_id and serial_to_id[serial] != kid:
                errors.append({"key_id": kid, "error": "same normalized key has different key_ids"})
                continue
            key_rows[kid] = row
            serial_to_id[serial] = kid
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


def group_patterns(records: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    groups: dict[str, dict[str, dict[str, Any]]] = defaultdict(dict)
    for row in records:
        groups[row["pattern_hash"]][row["key_id"]] = row
    return [{"pattern_hash": pattern, "representations": list(representations.values())}
            for pattern, representations in sorted(groups.items())]


def values(unit: dict[str, Any], field: str) -> list[Any]:
    result = {}
    for row in unit["representations"]:
        value = row.get(field)
        result[canonical(value)] = value
    return list(result.values())


def one(unit: dict[str, Any], field: str) -> Any:
    possibilities = values(unit, field)
    return possibilities[0] if len(possibilities) == 1 else None


def unit_row(unit: dict[str, Any], fields: Iterable[str]) -> dict[str, Any] | None:
    result = {"pattern_hash": unit["pattern_hash"]}
    for field in fields:
        possibilities = values(unit, field)
        if len(possibilities) != 1:
            return None
        result[field] = possibilities[0]
    return result


def fate_table(rows: list[dict[str, Any]], denominator: int | None = None) -> dict[str, Any]:
    counts = Counter(row["fate"] for row in rows)
    denominator = len(rows) if denominator is None else denominator
    return {"units_with_fate": len(rows), "denominator": denominator,
            "counts": {fate: counts[fate] for fate in FATES},
            "shares": {fate: counts[fate] / denominator if denominator else None for fate in FATES}}


def count_fates(units: list[dict[str, Any]], amb: Ambiguities, output: str) -> dict[str, Any]:
    rows, conflicts = [], []
    for unit in units:
        row = unit_row(unit, ("fate",))
        if row is None:
            conflicts.append(unit["pattern_hash"])
            amb.add("pattern_solver_outcome", output, {"pattern_hash": unit["pattern_hash"], "fates": values(unit, "fate")})
        else:
            rows.append(row)
    result = fate_table(rows, len(units))
    result.update({"distinct_patterns": len(units), "ambiguous_pattern_count": len(conflicts),
                   "status": "skipped_affected_fate_cells" if conflicts else "computed"})
    if conflicts:
        # Lower counts are useful coverage information, not a complete partition.
        result["determined_counts"] = result.pop("counts")
        result["determined_share_lower_bounds"] = result.pop("shares")
    return result


def census_shares(items: list[dict[str, Any]], coverage: dict[str, Any], amb: Ambiguities) -> dict[str, Any]:
    result = {}
    for population in ("W", "E"):
        draws = [item["record"] for item in items if item["population"] == population]
        units = group_patterns(draws)
        section: dict[str, Any] = {"raw_distinct_patterns": count_fates(units, amb, f"shares.{population}.raw")}
        section["accepted_draw_frequencies"] = fate_table(draws)
        if population == "W":
            section["raw_fair_coin_draw_mass"] = fate_table(draws, coverage["draws"].get("W", 0))
            section["raw_fair_coin_draw_mass"]["unresolved_or_rejected_draws"] = (
                coverage["draws"].get("W", 0) - len(draws))
        for minimum_s in (2, 3):
            name = f"given_s_ge_{minimum_s}"
            selected, uncertain = [], []
            for unit in units:
                membership = {row["s"] >= minimum_s for row in unit["representations"]}
                if len(membership) > 1:
                    uncertain.append(unit["pattern_hash"])
                    amb.add("pattern_condition_s", f"shares.{population}.{name}", {
                        "pattern_hash": unit["pattern_hash"], "s_values": sorted(values(unit, "s")), "minimum_s": minimum_s})
                elif True in membership:
                    selected.append(unit)
            distinct = count_fates(selected, amb, f"shares.{population}.{name}")
            if uncertain:
                distinct.update({"status": "skipped_conditional_membership_ambiguity", "ambiguous_membership_patterns": len(uncertain),
                                 "definite_members_only": True})
                distinct["definite_members_fate_table"] = {name: distinct.pop(name) for name in ("counts", "shares") if name in distinct}
            section[name] = {"distinct_patterns": distinct,
                             "draw_frequencies": fate_table([row for row in draws if row["s"] >= minimum_s])}
            if population == "W":
                denominator_counts = coverage["W_s_condition_draw_counts"][str(minimum_s)]
                raw_mass = fate_table([row for row in draws if row["s"] >= minimum_s], denominator_counts["true"])
                raw_mass["conditional_draw_counts"] = denominator_counts
                if denominator_counts["unknown"]:
                    raw_mass["status"] = "skipped_missing_s_membership_metadata"
                    raw_mass["shares"] = {fate: None for fate in FATES}
                section[name]["raw_fair_coin_draw_mass"] = raw_mass
        section["given_density_bin"] = []
        for bin_index, label in enumerate(BIN_LABELS):
            selected = [unit for unit in units if values(unit, "density_bin") == [bin_index]]
            section["given_density_bin"].append({"bin": label,
                "distinct_patterns": count_fates(selected, amb, f"shares.{population}.density.{label}"),
                "draw_frequencies": fate_table([row for row in draws if row["density_bin"] == bin_index])})
        result[population] = section
    return result


def settled_summary(items: list[dict[str, Any]], coverage: dict[str, Any], amb: Ambiguities) -> dict[str, Any]:
    result = {}
    for population in ("W", "E"):
        rows = [item["record"] for item in items if item["population"] == population]
        units = group_patterns(rows)
        flags = []
        denominator = coverage["draws"].get(population, 0)
        for field in ("s1", "single_placement", "first_letter_settled", "settled_union"):
            yes = [unit for unit in units if values(unit, field) == [True]]
            uncertain = [unit for unit in units if len(values(unit, field)) != 1]
            if uncertain:
                amb.add("pattern_settled", f"settled.{population}.{field}", {
                    "patterns": len(uncertain), "examples": [unit["pattern_hash"] for unit in uncertain[:4]], "flag": field})
            draw_count = sum(bool(row[field]) for row in rows)
            flags.append({"flag": field, "draws": draw_count,
                          "fair_coin_draw_mass" if population == "W" else "draw_share": draw_count / denominator if denominator else None,
                          "accepted_draw_share": draw_count / len(rows) if rows else None,
                          "distinct_patterns_true": len(yes) if not uncertain else None,
                          "distinct_patterns_definitely_true": len(yes), "ambiguous_distinct_patterns": len(uncertain),
                          "status": "skipped_affected_distinct_share" if uncertain else "computed"})
        result[population] = {"flags_overlap": True, "draw_denominator": denominator, "flags": flags,
                              "unsettled_draw_fates": fate_table([row for row in rows if not row["settled_union"]])}
    return result


def descriptive_stats(rows: list[dict[str, Any]]) -> dict[str, Any]:
    fate_rows = [row for row in rows if row.get("fate") in FATES]
    death_rows = [row for row in rows if row.get("_first_death_known", True)]
    hist = Counter(row["first_death"] for row in death_rows)
    curves = []
    for i in range(LEVELS):
        first_deaths = sum(row["first_death"] is not None and row["first_death"] <= i + 1 for row in death_rows)
        verdict_options = [set(options[i] for options in row.get("_verdict_options", [row["verdict_n"]])) for row in rows]
        curves.append({"level": i + 1, "first_death_by_level": first_deaths,
                       "first_death_share": first_deaths / len(rows) if rows and len(death_rows) == len(rows) else None,
                       "dead_at_level": sum(options == {0} for options in verdict_options) if all(len(options) == 1 for options in verdict_options) else None,
                       "undecided_at_level": sum(options == {None} for options in verdict_options) if all(len(options) == 1 for options in verdict_options) else None,
                       "ambiguous_solver_outcomes_at_level": sum(len(options) > 1 for options in verdict_options),
                       "empty_at_level": sum(row["knots_n"][i] == 0 for row in rows)})
    ratios_11 = [row["join_n"][10] / row["join_n"][9] for row in rows if row["join_n"][9] != 0]
    ratios_12 = [row["join_n"][11] / row["join_n"][10] for row in rows if row["join_n"][10] != 0]
    fate_result = fate_table(fate_rows, len(rows))
    if len(fate_rows) != len(rows):
        fate_result["status"] = "skipped_affected_fate_cells"
        fate_result["determined_counts"] = fate_result.pop("counts")
        fate_result["determined_share_lower_bounds"] = fate_result.pop("shares")
    return {"units": len(rows), "fates": fate_result, "mean_rho_max": mean(row["rho_max"] for row in rows),
            "mean_rho12": mean(row["rho12"] for row in rows),
            "first_death_histogram": {str(level): hist[level] for level in range(1, LEVELS + 1)},
            "no_observed_death": hist[None], "ambiguous_first_death_patterns": len(rows) - len(death_rows), "death_by_level": curves,
            "mean_knots_n": [mean(row["knots_n"][i] for row in rows) for i in range(LEVELS)],
            "joining": {"mean_J10": mean(row["join_n"][9] for row in rows),
                        "mean_J11": mean(row["join_n"][10] for row in rows),
                        "mean_J12": mean(row["join_n"][11] for row in rows),
                        "mean_J11_over_J10_nonzero_denominator": mean(ratios_11),
                        "mean_J12_over_J11_nonzero_denominator": mean(ratios_12),
                        "J10_zero": sum(row["join_n"][9] == 0 for row in rows),
                        "J11_zero": sum(row["join_n"][10] == 0 for row in rows)},
            "null_verdicts_n": [curve["undecided_at_level"] for curve in curves]}


DESCRIPTIVE_FIELDS = ("fate", "first_death", "verdict_n", "rho_max", "rho12", "join_n", "knots_n")


def descriptive_tables(items: list[dict[str, Any]], amb: Ambiguities) -> dict[str, Any]:
    result = {}
    for population in ("W", "E"):
        rows = [item["record"] for item in items if item["population"] == population]
        units = group_patterns(rows)
        sections = []
        for unit_type in ("distinct_patterns", "draw_frequencies"):
            # Bin-only summaries remain available when the same pattern has
            # several activity classes among its descriptions.
            for bin_index in (None, *range(len(BIN_LABELS))):
                if unit_type == "draw_frequencies":
                    selected = [row for row in rows if bin_index is None or row["density_bin"] == bin_index]
                else:
                    selected = []
                    for unit in units:
                        if bin_index is not None and values(unit, "density_bin") != [bin_index]:
                            continue
                        row = unit_row(unit, ("rho_max", "rho12", "join_n", "knots_n"))
                        if row is None:
                            continue
                        row["fate"] = one(unit, "fate")
                        row["first_death"] = one(unit, "first_death")
                        row["_first_death_known"] = len(values(unit, "first_death")) == 1
                        row["_verdict_options"] = values(unit, "verdict_n")
                        row["verdict_n"] = row["_verdict_options"][0] if len(row["_verdict_options"]) == 1 else [None] * LEVELS
                        selected.append(row)
                stats = descriptive_stats(selected)
                stats.update({"unit": unit_type, "class_variable": "none", "activity_class": "all",
                              "density_bin": BIN_LABELS[bin_index] if bin_index is not None else "all",
                              "status": "computed", "ambiguous_patterns_affecting_group": 0,
                              "determined_members_only": False})
                sections.append(stats)
            for class_field in ("rel_class", "letter_class"):
                for activity in CLASSES:
                    for bin_index in (None, *range(len(BIN_LABELS))):
                        selected, ambiguous_count = [], 0
                        if unit_type == "draw_frequencies":
                            selected = [row for row in rows if row[class_field] == activity and
                                        (bin_index is None or row["density_bin"] == bin_index)]
                        else:
                            for unit in units:
                                if bin_index is not None and values(unit, "density_bin") != [bin_index]:
                                    continue
                                possible_classes = values(unit, class_field)
                                if activity not in possible_classes:
                                    continue
                                if len(possible_classes) > 1:
                                    ambiguous_count += 1
                                    amb.add("pattern_class" if class_field == "rel_class" else "pattern_letter_class",
                                            f"descriptive.{population}.{class_field}.{activity}",
                                            {"pattern_hash": unit["pattern_hash"], "classes": possible_classes})
                                    continue
                                # Density and joining remain determined even if
                                # budgeted outcomes of equal patterns disagree.
                                row = unit_row(unit, ("rho_max", "rho12", "join_n", "knots_n"))
                                if row is None:
                                    ambiguous_count += 1
                                    amb.add("pattern_solver_outcome", f"descriptive.{population}.{class_field}.{activity}",
                                            {"pattern_hash": unit["pattern_hash"]})
                                    continue
                                row["fate"] = one(unit, "fate")
                                row["first_death"] = one(unit, "first_death")
                                row["_first_death_known"] = len(values(unit, "first_death")) == 1
                                row["_verdict_options"] = values(unit, "verdict_n")
                                row["verdict_n"] = row["_verdict_options"][0] if len(row["_verdict_options"]) == 1 else [None] * LEVELS
                                if len(values(unit, "fate")) > 1 or len(row["_verdict_options"]) > 1:
                                    amb.add("pattern_solver_outcome", f"descriptive.{population}.{class_field}.{activity}",
                                            {"pattern_hash": unit["pattern_hash"]})
                                selected.append(row)
                        stats = descriptive_stats(selected)
                        stats.update({"unit": unit_type, "class_variable": class_field, "activity_class": activity,
                                      "density_bin": BIN_LABELS[bin_index] if bin_index is not None else "all",
                                      "status": "skipped_affected_group_complete_statistics" if ambiguous_count else "computed",
                                      "ambiguous_patterns_affecting_group": ambiguous_count,
                                      "determined_members_only": bool(ambiguous_count)})
                        sections.append(stats)
        result[population] = {"death_after_level_12": "censored; no all-level inference", "groups": sections}
    return result


def exact_activity_inventory(items: list[dict[str, Any]], amb: Ambiguities) -> dict[str, Any]:
    result = {}
    for population in ("W", "E"):
        rows = [item["record"] for item in items if item["population"] == population]
        units = group_patterns(rows)
        result[population] = {}
        for class_field, degree_field in (("rel_class", "rel_degree"), ("letter_class", "letter_degree")):
            counts = Counter((row[class_field], row.get(degree_field)) for row in rows)
            distinct = Counter()
            ambiguous = 0
            for unit in units:
                labels = {(row[class_field], row.get(degree_field)) for row in unit["representations"]}
                if len(labels) == 1:
                    distinct[next(iter(labels))] += 1
                else:
                    ambiguous += 1
                    amb.add("pattern_class" if class_field == "rel_class" else "pattern_letter_class",
                            f"activity_inventory.{population}.{class_field}", {"pattern_hash": unit["pattern_hash"],
                            "exact_classes": sorted([list(label) for label in labels], key=canonical)})
            result[population][class_field] = {
                "rows": [{"class": activity, "degree": degree, "draws": counts[(activity, degree)],
                          "distinct_patterns_unambiguous": distinct[(activity, degree)]}
                         for activity, degree in sorted(set(counts) | set(distinct), key=canonical)],
                "ambiguous_distinct_patterns": ambiguous,
                "degree_note": "The producer's exact polynomial degree is retained; inference compares the polynomial class against exponential."}
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


def arm_stats(rows: list[dict[str, Any]], unit: str) -> dict[str, Any]:
    counts = Counter(row["fate"] for row in rows)
    patterns = defaultdict(list)
    cluster_counts = Counter(row["cluster"] for row in rows if row["cluster"] is not None)
    for row in rows:
        patterns[row["pattern_hash"]].append(row)
    decided_patterns, fu_patterns, mixed_patterns = 0, 0, 0
    for representations in patterns.values():
        outcomes = {None if row["fate"] is None else row["fate"] == "FU" for row in representations}
        if outcomes == {False}:
            decided_patterns += 1
        elif outcomes == {True}:
            fu_patterns += 1
        else:
            mixed_patterns += 1
    clusters_per_pattern = [{row["cluster"] for row in group} for group in patterns.values()]
    unknown_fates = counts[None]
    unknown_clusters = sum(row["cluster"] is None for row in rows)
    null_counts = []
    for i in range(LEVELS):
        options = [set(value[i] for value in row.get("_verdict_options", [row["verdict_n"]])) for row in rows]
        null_counts.append(sum(value == {None} for value in options) if all(len(value) == 1 for value in options) else None)
    return {"unit": unit, "units": len(rows), "distinct_patterns": len(patterns),
            "decided": sum(counts[fate] for fate in ("F1", "F2", "F3")), "FU": counts["FU"],
            "ambiguous_fate_patterns": unknown_fates, "ambiguous_cluster_patterns": unknown_clusters,
            "FU_share": counts["FU"] / len(rows) if rows and not unknown_fates else None,
            "decided_distinct_patterns": decided_patterns, "FU_distinct_patterns": fu_patterns,
            "mixed_decision_distinct_patterns": mixed_patterns,
            "FU_distinct_pattern_share": fu_patterns / len(patterns) if patterns and not mixed_patterns else None,
            "patterns_with_multiple_clusters": sum(len(clusters) > 1 for clusters in clusters_per_pattern),
            "automaton_classes": len(cluster_counts) if not unknown_clusters else None,
            "known_automaton_classes": len(cluster_counts),
            "decided_automaton_classes": len({row["cluster"] for row in rows if row["fate"] in ("F1", "F2", "F3") and row["cluster"] is not None}) if not unknown_clusters and not unknown_fates else None,
            "automaton_class_counts": dict(sorted(cluster_counts.items())),
            "fates": {fate: counts[fate] for fate in FATES},
            "mean_rho_max": mean(row["rho_max"] for row in rows),
            "mean_rho12": mean(row["rho12"] for row in rows),
            "null_verdicts_n": null_counts,
            "death_share_FU_alive": (counts["F1"] + counts["F2"]) / len(rows) if rows and not unknown_fates else None,
            "death_share_FU_dead": (counts["F1"] + counts["F2"] + counts["FU"]) / len(rows) if rows and not unknown_fates else None}


def ordinary_eligible(stats: dict[str, Any]) -> bool:
    return stats["decided"] >= 30 and stats["decided_automaton_classes"] >= 5 and stats["FU_share"] < 0.10


def w_eligible(stats: dict[str, Any]) -> bool | None:
    by_draw = ordinary_eligible(stats)
    if stats["mixed_decision_distinct_patterns"] or stats["patterns_with_multiple_clusters"]:
        # An arm with fewer than 30 possible patterns is ineligible under one
        # reading even if its repeated draw count is large.
        if not by_draw and stats["decided_distinct_patterns"] < 30:
            return False
        return None
    by_pattern = (stats["decided_distinct_patterns"] >= 30 and
                  stats["decided_automaton_classes"] >= 5 and
                  stats["FU_distinct_pattern_share"] is not None and stats["FU_distinct_pattern_share"] < 0.10)
    return by_draw if by_draw == by_pattern else None


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


def assignment_verdict(delta: float, interval95: list[float], corrected: list[float] | None) -> str:
    if corrected is not None and (corrected[1] < 0 or corrected[0] > 0) and abs(delta) >= 0.10:
        return "differs"
    if interval95[0] >= -0.10 and interval95[1] <= 0.10:
        return "same"
    return "unclear" if corrected is not None else "skipped_corrected_interval_ambiguity"


def matched_analysis(items: list[dict[str, Any]], population: str, exclude_settled: bool,
                     amb: Ambiguities, rng: random.Random) -> dict[str, Any]:
    source_rows = [item["record"] for item in items if item["population"] == population]
    units = group_patterns(source_rows)
    rows: list[dict[str, Any]] = []
    affected: dict[tuple[int, str], list[str]] = defaultdict(list)
    possible_decided: dict[tuple[int, str], set[str]] = defaultdict(set)
    possible_decided_clusters: dict[tuple[int, str], set[str]] = defaultdict(set)
    analysis_name = f"matched.{population}.{'settled_excluded' if exclude_settled else 'settled_included'}"
    f0_count = 0
    settled_count = 0
    if population == "W":
        f0_count = sum(row["fate"] == "F0" for row in source_rows)
        settled_count = sum(row["fate"] != "F0" and row["settled"] for row in source_rows) if exclude_settled else 0
        rows = [row for row in source_rows if row["fate"] != "F0" and (not exclude_settled or not row["settled"])]
    else:
        for unit in units:
            fates = values(unit, "fate")
            if fates == ["F0"]:
                f0_count += 1
                continue
            if exclude_settled and values(unit, "settled") == [True]:
                settled_count += 1
                continue
            classes, bins = values(unit, "rel_class"), values(unit, "density_bin")
            if any(fate in ("F1", "F2", "F3") for fate in fates):
                for bin_index in bins:
                    for activity in classes:
                        possible_decided[(bin_index, activity)].add(unit["pattern_hash"])
                        possible_decided_clusters[(bin_index, activity)].update(values(unit, "cluster"))
            reasons = []
            if len(fates) > 1:
                reasons.append("pattern_solver_outcome")
            if len(classes) > 1:
                reasons.append("pattern_class")
            if len(values(unit, "cluster")) > 1:
                reasons.append("pattern_cluster")
            if exclude_settled and len(values(unit, "settled")) > 1:
                reasons.append("pattern_settled")
            # Arm counts and density means do not require a unique cluster;
            # cluster ambiguity blocks only eligibility and inference.  A
            # differing per-level null after a forced F1/F2 likewise does not
            # make that pattern's death response ambiguous.
            selected = unit_row(unit, ("rho_max", "rho12", "density_bin", "rel_class"))
            membership_ambiguous = (len(classes) > 1 or len(bins) > 1 or
                                    exclude_settled and len(values(unit, "settled")) > 1)
            if selected is None and not reasons:
                reasons.append("pattern_solver_outcome")
            if reasons:
                for reason in reasons:
                    amb.add(reason, analysis_name, {"pattern_hash": unit["pattern_hash"], "classes": classes, "bins": bins})
                for bin_index in bins:
                    for activity in classes:
                        affected[(bin_index, activity)].append(unit["pattern_hash"])
                if membership_ambiguous or selected is None:
                    continue
            selected["fate"] = one(unit, "fate")
            selected["cluster"] = one(unit, "cluster")
            selected["_verdict_options"] = values(unit, "verdict_n")
            selected["verdict_n"] = selected["_verdict_options"][0] if len(selected["_verdict_options"]) == 1 else [None] * LEVELS
            rows.append(selected)
    cells = []
    cell_rows = []
    for bin_index, label in enumerate(BIN_LABELS):
        exponential = [row for row in rows if row["density_bin"] == bin_index and row["rel_class"] == "exponential"]
        for comparator in COMPARATORS:
            comparison = [row for row in rows if row["density_bin"] == bin_index and row["rel_class"] == comparator]
            left_stats, right_stats = arm_stats(comparison, "draws" if population == "W" else "distinct_patterns"), arm_stats(exponential, "draws" if population == "W" else "distinct_patterns")
            affected_patterns = set(affected[(bin_index, comparator)] + affected[(bin_index, "exponential")])
            eligibility: bool | None
            if affected_patterns:
                # Missing representative/cluster rules need not obscure a
                # definite failure of a necessary eligibility threshold.
                can_reach_threshold = all(
                    len(possible_decided[(bin_index, activity)]) >= 30 and
                    len(possible_decided_clusters[(bin_index, activity)]) >= 5
                    for activity in (comparator, "exponential"))
                eligibility = None if can_reach_threshold else False
            elif population == "W":
                left_ok, right_ok = w_eligible(left_stats), w_eligible(right_stats)
                eligibility = False if False in (left_ok, right_ok) else (True if left_ok is True and right_ok is True else None)
                if eligibility is None:
                    amb.add("w_eligibility", analysis_name + "." + label + "." + comparator,
                            {"C": comparator, "bin": label, "left": left_stats["units"], "right": right_stats["units"]})
            else:
                eligibility = ordinary_eligible(left_stats) and ordinary_eligible(right_stats)
            cell = {"bin_index": bin_index, "bin": label, "C": comparator,
                    "exponential": right_stats, "comparison": left_stats, "eligible": eligibility,
                    "status": "eligibility_ambiguous" if eligibility is None else ("eligible" if eligibility else "ineligible"),
                    "ambiguous_patterns_affecting_cell": len(affected_patterns),
                    "maximum_possible_decided_patterns": {
                        "comparison": len(possible_decided[(bin_index, comparator)]) if population == "E" else None,
                        "exponential": len(possible_decided[(bin_index, "exponential")]) if population == "E" else None},
                    "assignments": {}, "verdict": None}
            if affected_patterns:
                cell["affected_inference_only_when_membership_and_fate_are_determined"] = True
            cells.append(cell)
            cell_rows.append((comparison, exponential))
    eligible_count = sum(cell["eligible"] is True for cell in cells)
    unknown_count = sum(cell["eligible"] is None for cell in cells)
    family_m = eligible_count if not unknown_count else None
    for cell, (left, right) in zip(cells, cell_rows):
        if cell["eligible"] is not True:
            continue
        bootstraps = bootstrap_deltas(left, right, rng, "draw" if population == "W" else "automaton_class")
        for assignment in ("FU_alive", "FU_dead"):
            field = "death_share_" + assignment
            delta = cell["comparison"][field] - cell["exponential"][field]
            samples = bootstraps[assignment]
            interval95 = [quantile(samples, 0.025), quantile(samples, 0.975)]
            tail = 0.05 / (2 * family_m) if family_m else None
            corrected = [quantile(samples, tail), quantile(samples, 1 - tail)] if tail is not None else None
            verdict = assignment_verdict(delta, interval95, corrected)
            cell["assignments"][assignment] = {"delta": delta, "interval95": interval95,
                "bonferroni_interval": corrected, "bonferroni_m": family_m,
                "bonferroni_confidence": 1 - 0.05 / family_m if family_m else None, "verdict": verdict}
        opinions = {assignment["verdict"] for assignment in cell["assignments"].values()}
        if len(opinions) == 1:
            cell["verdict"] = next(iter(opinions))
        elif any(opinion.startswith("skipped") for opinion in opinions):
            cell["verdict"] = "skipped_corrected_interval_ambiguity"
        else:
            cell["verdict"] = "unclear"
        cell["status"] = "computed" if family_m is not None else "95_percent_only_correction_family_ambiguous"
    return {"population": population, "unit": "empirical_W_draw_frequency" if population == "W" else "distinct_pattern",
            "settled_excluded": exclude_settled, "F0_excluded": True,
            "F0_units_excluded": f0_count, "settled_units_excluded_after_F0": settled_count,
            "FU_retained": True, "bootstrap_resamples": BOOTSTRAPS,
            "bootstrap_seed": BOOTSTRAP_SEED,
            "bootstrap_unit": "draw" if population == "W" else "automaton_class",
            "bootstrap_cluster": None if population == "W" else "automaton_class, independently within each arm",
            "bootstrap_scheme": "iid empirical draws, independently within each arm" if population == "W" else
                "automaton-class cluster resampling, independently within each arm, retaining within-cluster sizes",
            "eligible_cells": eligible_count, "eligibility_unknown_cells": unknown_count,
            "bonferroni_m": family_m, "bonferroni_m_range": [eligible_count, eligible_count + unknown_count],
            "bonferroni_family": "eligible cells within this population and settled-exclusion analysis",
            "correction_note": "Corrected intervals depend on all eligible cells; an unknown eligibility prevents a unique m." if unknown_count else None,
            "cells": cells}


def predictions(key_rows: dict[str, dict[str, Any]], primary: dict[str, Any], amb: Ambiguities,
                coverage_complete: bool) -> dict[str, Any]:
    rows = list(key_rows.values())
    settled = [row for row in rows if row["single_placement"] or row["first_letter_settled"]]
    p1_failures = [row for row in settled if row["fate"] != "F3"]
    f0_failures = [row for row in p1_failures if row["fate"] == "F0"]
    if f0_failures:
        amb.add("p1_f0", "predictions.P1", {"keys": len(f0_failures), "examples": [row["key_id"] for row in f0_failures[:6]]})
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
        "P1": {"status": "literal_failure_with_F0_inconsistency" if f0_failures else ("fails_run_invalid" if p1_failures else "no_failure_observed"),
               "descriptions_checked": len(settled), "literal_non_F3_count": len(p1_failures),
               "F0_inconsistency_count": len(f0_failures), "other_failure_count": len(p1_failures) - len(f0_failures),
               "failing_key_ids": [row["key_id"] for row in p1_failures],
               "literal_rule_invalidates_run": bool(p1_failures),
               "note": "F0 is retained. No exception to P1 is silently added; the frozen inconsistency requires clarification." if f0_failures else None},
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


def logistic_matrix(items: list[dict[str, Any]], population: str, amb: Ambiguities) -> dict[str, Any]:
    source = [item["record"] for item in items if item["population"] == population]
    source = [row for row in source if row["fate"] != "F0" and not row["settled"]]
    rows, skipped = [], []
    if population == "W":
        rows = source
    else:
        # Filter after grouping; a settled/unsettled disagreement must not silently
        # become an unsettled representative through pre-filtering.
        all_units = group_patterns(item["record"] for item in items if item["population"] == population)
        for unit in all_units:
            if values(unit, "fate") == ["F0"] or values(unit, "settled") == [True]:
                continue
            reasons = []
            for field, question in (("settled", "pattern_settled"), ("rel_class", "pattern_class"),
                                    ("cluster", "pattern_cluster"), ("fate", "pattern_solver_outcome")):
                if len(values(unit, field)) != 1:
                    reasons.append(question)
                    amb.add(question, f"logistic.{population}", {"pattern_hash": unit["pattern_hash"]})
            row = unit_row(unit, ("settled", "rel_class", "cluster", "fate", "density_bin"))
            if reasons or row is None:
                skipped.append({"pattern_hash": unit["pattern_hash"], "reasons": reasons})
            else:
                rows.append(row)
    columns = ["intercept", "class_bounded", "class_polynomial", "class_exponential"] + [f"density_bin_{i}" for i in range(1, len(BIN_LABELS))]
    matrix = []
    for row in rows:
        response = None if row["fate"] == "FU" else int(row["fate"] in ("F1", "F2"))
        x = [1] + [int(row["rel_class"] == activity) for activity in CLASSES[1:]] + [int(row["density_bin"] == i) for i in range(1, len(BIN_LABELS))]
        matrix.append({"pattern_hash": row["pattern_hash"], "death": response, "fate": row["fate"],
                       "automaton_class": row["cluster"], "X": x, "frequency_weight": 1})
    fu = sum(row["death"] is None for row in matrix)
    statsmodels_available = importlib.util.find_spec("statsmodels") is not None
    if fu:
        amb.add("logistic_fu_response", f"logistic.{population}", {"FU": fu})
    result = {"population": population, "settled_excluded": True, "F0_excluded": True,
              "response": "1 for F1/F2; 0 for F3; FU null pending explicit response rule",
              "reference_class": "finitary", "reference_density_bin": BIN_LABELS[0],
              "columns": columns, "design_matrix": matrix, "skipped_ambiguous_units": skipped,
              "cluster_variable": "automaton_class", "FU": fu,
              "statsmodels_available": statsmodels_available,
              "fit_skip_reasons": (["pattern_assignment_ambiguity"] if skipped else []) +
                                  (["FU_response_ambiguity"] if fu else []) +
                                  (["statsmodels_unavailable"] if not statsmodels_available else []),
              "fit": {"status": "not_attempted"}}
    if skipped:
        result["fit"] = {"status": "skipped_pattern_assignment_ambiguity"}
    elif fu:
        result["fit"] = {"status": "skipped_FU_response_ambiguity"}
    elif not statsmodels_available:
        result["fit"] = {"status": "skipped_statsmodels_unavailable", "matrix_location": "this summary.json logistic section"}
    elif not matrix:
        result["fit"] = {"status": "skipped_no_eligible_data"}
    else:
        try:
            import numpy as np
            import statsmodels.api as sm
            x = np.asarray([row["X"] for row in matrix], dtype=float)
            y = np.asarray([row["death"] for row in matrix], dtype=float)
            clusters = [row["automaton_class"] for row in matrix]
            fitted = sm.GLM(y, x, family=sm.families.Binomial()).fit(cov_type="cluster", cov_kwds={"groups": clusters})
            result["fit"] = {"status": "computed", "coefficients": fitted.params.tolist(),
                             "cluster_robust_standard_errors": fitted.bse.tolist(),
                             "p_values": fitted.pvalues.tolist(), "interval95": fitted.conf_int().tolist(),
                             "converged": bool(fitted.converged)}
        except Exception as error:
            result["fit"] = {"status": "failed", "error": str(error), "error_type": type(error).__name__}
    return result


def fmt(value: Any) -> str:
    if value is None:
        return "—"
    if isinstance(value, float):
        return f"{value:.4f}"
    return str(value).replace("|", "\\|").replace("\n", " ")


def table(headers: list[str], rows: Iterable[Iterable[Any]]) -> list[str]:
    return ["| " + " | ".join(headers) + " |", "| " + " | ".join("---" for _ in headers) + " |"] + [
        "| " + " | ".join(fmt(value) for value in row) + " |" for row in rows]


def render_markdown(summary: dict[str, Any]) -> str:
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
            if population == "W":
                groups.append((f"s >= {minimum_s}, all conditional W draw mass", part["raw_fair_coin_draw_mass"]))
        for part in section["given_density_bin"]:
            groups += [(part["bin"] + ", distinct", part["distinct_patterns"]),
                       (part["bin"] + ", draws", part["draw_frequencies"])]
        for label, part in groups:
            shares = part.get("shares", {})
            fate_rows.append([population, label, part.get("denominator"), *[shares.get(fate) for fate in FATES], part.get("status", "computed")])
    lines += table(["Population", "Condition and unit", "Denominator", *FATES, "Status"], fate_rows)
    lines += ["", "Rejected or missing W draws retain their mass outside the five fate cells. Accepted-draw fractions are shown separately. "
              "A skipped distinct-pattern row has determined lower counts in summary.json; no representative description is chosen.", "",
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
              "The correction family is the eligible cells within each displayed analysis; an unknown eligibility leaves m unresolved.", ""]
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
    lines += ["", "P1 literal failures, P2 returns, P4 witnesses, and H-dens/H-bound failure cells are listed by key or cell in summary.json. "
              "An incomplete census cannot establish an absence across the registered population.", "",
              "## Logistic sensitivity", ""]
    lines += table(["Population", "Matrix rows", "FU", "Skipped ambiguous units", "Fit"], [
        (population, len(section["design_matrix"]), section["FU"], len(section["skipped_ambiguous_units"]), section["fit"]["status"])
        for population, section in summary["logistic"].items()])
    lines += ["", "The full design matrix, cluster labels, column definitions, and any fit are stored in summary.json. "
              "FU responses stay null until their treatment is specified.", "",
              "## Ambiguities and affected outputs", ""]
    if not summary["ambiguities"]:
        lines.append("No data-dependent ambiguity in the catalog was triggered by these observed records.")
    for ambiguity in summary["ambiguities"]:
        lines += [f"- **{ambiguity['id']}**: {ambiguity['question']} Affected outputs: " + "; ".join(ambiguity["affected_outputs"]) + "."]
    lines += ["", "The frozen ambiguity catalog is summary_ambiguities.json beside summarize.py. "
              "All data-dependent questions and examples are also in summary.json. No claim extends beyond the twelve levels read.", ""]
    return "\n".join(lines)


def build_summary(directory: Path) -> dict[str, Any]:
    amb = Ambiguities()
    items, keys, coverage = load_records(directory)
    validation = validation_summary(directory)
    shares = census_shares(items, coverage, amb)
    settled = settled_summary(items, coverage, amb)
    descriptive = descriptive_tables(items, amb)
    inventory = exact_activity_inventory(items, amb)
    rng = random.Random(BOOTSTRAP_SEED)
    matched = {}
    for population in ("E", "W"):
        for exclude in (True, False):
            name = f"{population}_{'settled_excluded' if exclude else 'settled_included'}"
            matched[name] = matched_analysis(items, population, exclude, amb, rng)
    used_keys = {item["record"]["key_id"]: item["record"] for item in items}
    coverage["complete_keys_not_referenced_by_observed_draws"] = len(set(keys) - set(used_keys))
    prediction = predictions(used_keys, matched["E_settled_excluded"], amb, coverage["registered_coverage_complete"])
    logistic = {population: logistic_matrix(items, population, amb) for population in ("E", "W")}
    solver_undecided = {"complete_keys": null_summary(used_keys.values()),
                        **{population + "_draws": null_summary(item["record"] for item in items if item["population"] == population)
                           for population in ("W", "E")}}
    scientific_failures = prediction["P1"]["literal_rule_invalidates_run"]
    return {"schema_version": 1, "levels": list(range(1, LEVELS + 1)),
            "preregistration": "research/ADDR-KNOTS-20261113-001/preregistration.md",
            "scope_note": "Registered coverage is complete." if coverage["registered_coverage_complete"] else
                "INCOMPLETE REGISTERED COVERAGE: all descriptive results below concern only observed complete key records. Missing keys and validation are not inferred.",
            "coverage": coverage, "validation": validation, "solver_undecided": solver_undecided,
            "registered_run_ready_for_interpretation": coverage["registered_coverage_complete"] and validation["required_core_gate_checks_passed"] and not scientific_failures,
            "weighting": {"W": "ordinary empirical draw frequency; no additional 2^-bits factor",
                          "rejected_W_draws": "retained outside fate cells in raw fair-coin draw mass; accepted-conditional fractions also reported",
                          "E": "distinct patterns for primary inference; reference code lengths never enter counts"},
            "density_bins": [{"label": label, "lower_inclusive": BIN_LIMITS[i], "upper_exclusive": None if math.isinf(BIN_LIMITS[i + 1]) else BIN_LIMITS[i + 1]}
                             for i, label in enumerate(BIN_LABELS)],
            "fate_shares": shares, "settled": settled, "descriptive": descriptive,
            "exact_activity_classes": inventory,
            "matched_density": matched, "predictions": prediction, "logistic": logistic,
            "ambiguities": amb.rows(), "ambiguity_catalog": amb.catalog,
            "authority": "finite computed census; no all-level theorem or change to the canonical knot test"}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    args = parser.parse_args(argv)
    directory = args.directory
    if not directory.is_dir():
        parser.error("DIR must be an existing output directory")
    summary = build_summary(directory)
    json_path, markdown_path = directory / "summary.json", directory / "summary.md"
    json_path.write_text(json.dumps(summary, indent=2, sort_keys=True, allow_nan=False) + "\n")
    markdown_path.write_text(render_markdown(summary))
    print(json.dumps({"summary_json": str(json_path), "summary_md": str(markdown_path),
                      "coverage_complete": summary["coverage"]["registered_coverage_complete"],
                      "validation": summary["validation"]["status"],
                      "ambiguities": len(summary["ambiguities"]),
                      "registered_run_ready_for_interpretation": summary["registered_run_ready_for_interpretation"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
