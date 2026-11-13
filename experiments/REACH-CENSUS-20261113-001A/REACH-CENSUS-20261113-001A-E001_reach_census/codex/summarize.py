#!/usr/bin/env python3
"""Join the frozen reach-census draws and family records.

Usage: .venv/bin/python -B PATH/TO/summarize.py DIR

The default invocation reports point bounds, counts, and exact histograms.  The
specification does not fix finite-sample quantiles or how the seeded random
stream is reused, so interval endpoints stay pending until explicit CLI choices
are supplied.  P1 and P3 additionally require their bootstrap sampling frames.
No bootstrap resamples distinct families: the sampling units are draw positions,
including repeated occurrences of the same family.
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from dataclasses import dataclass
from fractions import Fraction
import gzip
import hashlib
import json
import math
from pathlib import Path
import random
import sys
from typing import Any, Callable, Iterable, Sequence


SEED = 20261113
RESAMPLES = 2000
EXPECTED_DRAWS = 223261
SETTLED = (
    "S1 limit dead", "S2 no copy", "S3 no own distinctions",
    "S4 free own distinctions",
)
COMPUTED = (
    "unresolved", "none at any depth", "lost at large depths", "bounded",
    "grows", "mixed by residue",
)
CLASSES = SETTLED + COMPUTED
CLASS_INDEX = {name: index for index, name in enumerate(COMPUTED)}
P1_CLASSES = frozenset(("grows", "bounded", "mixed by residue", "unresolved"))
CELL_ORDER = ("all", "forever", "dies_with_dead_usual_limit", "alive_only_in_limit")
QUANTILES = ("linear", "nearest-rank", "lower", "higher", "midpoint")
STREAM_POLICIES = ("reset-per-group", "shared")
P1_FRAMES = ("conditional", "computed")
P3_FRAMES = ("independent-cells", "pooled-computed")


def compact(value: Any) -> str:
    return json.dumps(value, separators=(",", ":"), sort_keys=True, allow_nan=False)


def canonical_key(value: Any) -> str:
    if not isinstance(value, str):
        raise ValueError("key must be a JSON string")
    decoded = json.loads(value)
    if not isinstance(decoded, list):
        raise ValueError("key must encode a definitions list")
    return compact(decoded)


def ratio(numerator: int, denominator: int) -> float | None:
    return numerator / denominator if denominator else None


def exact_share(numerator: int, denominator: int) -> dict[str, Any]:
    return {"numerator": numerator, "denominator": denominator,
            "share": ratio(numerator, denominator)}


def band(count: int, unresolved: int, denominator: int) -> dict[str, Any]:
    return {"numerator_low": count, "numerator_high": count + unresolved,
            "denominator": denominator, "low": ratio(count, denominator),
            "high": ratio(count + unresolved, denominator)}


def pending(reason: str) -> dict[str, Any]:
    return {"status": "pending", "low": None, "high": None, "reason": reason}


@dataclass(frozen=True)
class Draw:
    key: str
    fate: str


@dataclass
class Family:
    key: str
    cls: str | None
    n_defs: int | None
    s_own: int | None
    usual_limit_alive: bool | None
    lambda_value: str | None
    lambda_float: float | None
    uniform_cost_bound: int | float | None
    onset_depth: int | float | None


def read_jsonl(path: Path) -> tuple[list[tuple[int, dict[str, Any]]], dict[str, Any]]:
    """Read complete valid rows, retaining explicit evidence of a partial file."""
    info: dict[str, Any] = {"path": str(path.resolve()), "exists": path.is_file(),
                            "rows": 0, "done_rows": 0, "errors": []}
    rows: list[tuple[int, dict[str, Any]]] = []
    if not info["exists"]:
        return rows, info
    opener = gzip.open if path.suffix == ".gz" else open
    line_number = 0
    try:
        with opener(path, "rt", encoding="utf-8") as handle:
            while True:
                try:
                    line = handle.readline()
                except (EOFError, OSError, UnicodeError) as exc:
                    info["errors"].append({"line": line_number + 1,
                                           "error": f"{type(exc).__name__}: {exc}"})
                    break
                if not line:
                    break
                line_number += 1
                if not line.strip():
                    continue
                try:
                    row = json.loads(line)
                    if not isinstance(row, dict):
                        raise ValueError("row must be a JSON object")
                except (ValueError, TypeError) as exc:
                    info["errors"].append({"line": line_number,
                                           "error": f"{type(exc).__name__}: {exc}"})
                    continue
                if row.get("kind") == "done":
                    info["done_rows"] += 1
                    continue
                rows.append((line_number, row))
    except (EOFError, OSError, UnicodeError) as exc:
        info["errors"].append({"line": line_number + 1,
                               "error": f"{type(exc).__name__}: {exc}"})
    info["rows"] = len(rows)
    info["read_without_errors"] = not info["errors"]
    return rows, info


def read_draws(path: Path) -> tuple[list[Draw], dict[str, Any]]:
    rows, info = read_jsonl(path)
    draws: list[Draw] = []
    key_pool: dict[str, str] = {}
    identities: set[tuple[int, int]] = set()
    workers: Counter[str] = Counter()
    info.update(invalid_rows=[], noncanonical_keys=0, duplicate_draw_identities=0)
    for line, row in rows:
        try:
            key = canonical_key(row["key"])
            if not isinstance(row.get("fate"), str):
                raise ValueError("fate must be a string")
            if key != row["key"]:
                info["noncanonical_keys"] += 1
            key = key_pool.setdefault(key, key)
            worker, try_index = row.get("worker"), row.get("try_index")
            if (isinstance(worker, int) and not isinstance(worker, bool)
                    and isinstance(try_index, int) and not isinstance(try_index, bool)):
                identity = (worker, try_index)
                if identity in identities:
                    info["duplicate_draw_identities"] += 1
                identities.add(identity)
            workers[str(worker)] += 1
            draws.append(Draw(key, row["fate"]))
        except (KeyError, ValueError, TypeError, json.JSONDecodeError) as exc:
            info["invalid_rows"].append({"line": line, "error": str(exc)})
    info.update(usable_draw_rows=len(draws), distinct_families=len(key_pool),
                draws_by_worker=dict(sorted(workers.items())),
                expected_full_draw_count=EXPECTED_DRAWS,
                matches_expected_full_draw_count=len(draws) == EXPECTED_DRAWS)
    return draws, info


def nonnegative_integer(value: Any) -> int | None:
    return value if isinstance(value, int) and not isinstance(value, bool) and value >= 0 else None


def finite_number(value: Any) -> int | float | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    return value if math.isfinite(value) else None


def compatible_field(row: dict[str, Any], field: str,
                     issues: list[str]) -> Any:
    """Read the producer's declared flat fields and exact-test compatibility alias."""
    aliases = (field, "depth_threshold") if field == "onset_depth" else (field,)
    sources = [row]
    nested = row.get("exact_eventual_boundedness")
    if isinstance(nested, dict):
        sources.append(nested)
    present = [source[name] for source in sources for name in aliases
               if name in source and source[name] is not None]
    if not present:
        return None
    if any(value != present[0] for value in present[1:]):
        issues.append(f"conflicting compatibility aliases for {field}")
        return None
    return present[0]


def read_families(path: Path) -> tuple[dict[str, Family], dict[str, Any]]:
    rows, info = read_jsonl(path)
    families: dict[str, Family] = {}
    fingerprints: dict[str, str] = {}
    conflicts: set[str] = set()
    info.update(invalid_rows=[], field_issues=[], noncanonical_keys=0,
                identical_duplicate_rows=0, conflicting_keys=[])
    for line, row in rows:
        try:
            key = canonical_key(row["key"])
            if key != row["key"]:
                info["noncanonical_keys"] += 1
            normalized = dict(row, key=key)
            fingerprint = hashlib.sha256(compact(normalized).encode()).hexdigest()
            if key in fingerprints:
                if fingerprints[key] == fingerprint:
                    info["identical_duplicate_rows"] += 1
                else:
                    conflicts.add(key)
                    families.pop(key, None)
                continue
            fingerprints[key] = fingerprint
            issues: list[str] = []
            cls = row.get("class")
            if cls not in CLASSES:
                issues.append("class is absent or is not a specified class")
                cls = None
            n_defs = nonnegative_integer(row.get("n_defs"))
            if n_defs == 0:
                n_defs = None
            s_own = nonnegative_integer(row.get("s_own"))
            usual = row.get("usual_limit_alive")
            if not isinstance(usual, bool):
                usual = None
                issues.append("usual_limit_alive is absent or is not boolean")
            lam, lam_float = row.get("lambda"), None
            if lam is not None:
                try:
                    if isinstance(lam, bool):
                        raise ValueError("boolean lambda")
                    exact_lambda = Fraction(lam)
                    lam, lam_float = str(exact_lambda), float(exact_lambda)
                except (ValueError, TypeError, ZeroDivisionError, OverflowError):
                    issues.append("lambda is not an exact finite fraction")
                    lam = None
            bound = finite_number(compatible_field(row, "uniform_cost_bound", issues))
            onset = finite_number(compatible_field(row, "onset_depth", issues))
            families[key] = Family(key, cls, n_defs, s_own, usual,
                                   lam, lam_float, bound, onset)
            if issues:
                info["field_issues"].append({"line": line, "key": key, "issues": issues})
        except (KeyError, ValueError, TypeError, json.JSONDecodeError) as exc:
            info["invalid_rows"].append({"line": line, "error": str(exc)})
    info["conflicting_keys"] = sorted(conflicts)
    info["usable_distinct_records"] = len(families)
    return families, info


def quantile(values: Sequence[float], probability: float, *, convention: str) -> float:
    """Explicit finite-sample conventions; there is deliberately no default."""
    if not values:
        raise ValueError("a quantile needs at least one value")
    if not 0 <= probability <= 1:
        raise ValueError("probability must be in [0, 1]")
    ordered = sorted(values)
    if convention == "nearest-rank":
        return ordered[max(0, math.ceil(probability * len(ordered)) - 1)]
    position = (len(ordered) - 1) * probability
    lo, hi = math.floor(position), math.ceil(position)
    if convention == "linear":
        return ordered[lo] + (ordered[hi] - ordered[lo]) * (position - lo)
    if convention == "lower":
        return ordered[lo]
    if convention == "higher":
        return ordered[hi]
    if convention == "midpoint":
        return (ordered[lo] + ordered[hi]) / 2
    raise ValueError(f"unknown quantile convention: {convention}")


def resample_counts(labels: Sequence[int], rng: random.Random) -> list[int]:
    """Exactly len(labels) individual-draw choices, using Random.choice semantics."""
    counts = [0] * len(COMPUTED)
    size = len(labels)
    choose = rng.randrange
    for _ in range(size):
        counts[labels[choose(size)]] += 1
    return counts


def bootstrap_class_bands(labels: Sequence[int], *, rng: random.Random,
                          quantile_function: Callable[[Sequence[float], float], float],
                          resamples: int = RESAMPLES) -> dict[str, Any]:
    """Bootstrap all resolved class bands on one common set of draw resamples."""
    size = len(labels)
    if not size:
        return {name: {"status": "undefined", "low": None, "high": None,
                       "reason": "zero computed draws"}
                for name in COMPUTED if name != "unresolved"}
    lows = [[] for _ in COMPUTED]
    highs = [[] for _ in COMPUTED]
    for _ in range(resamples):
        counts = resample_counts(labels, rng)
        for index, name in enumerate(COMPUTED):
            if name == "unresolved":
                continue
            lows[index].append(counts[index] / size)
            highs[index].append((counts[index] + counts[0]) / size)
    return {name: {"status": "complete", "low": quantile_function(lows[index], .025),
                   "high": quantile_function(highs[index], .975), "resamples": resamples}
            for index, name in enumerate(COMPUTED) if name != "unresolved"}


def bootstrap_p1(labels: Sequence[int], *, rng: random.Random,
                 quantile_function: Callable[[Sequence[float], float], float],
                 frame: str, resamples: int = RESAMPLES) -> dict[str, Any]:
    indices = {CLASS_INDEX[name] for name in P1_CLASSES}
    if frame == "conditional":
        labels = [value for value in labels if value in indices]
    elif frame != "computed":
        raise ValueError(f"unknown P1 frame: {frame}")
    if not labels:
        return {"status": "undefined", "low": None, "high": None,
                "reason": "zero draws in the bootstrap sampling frame"}
    lows, highs = [], []
    undefined = 0
    for _ in range(resamples):
        counts = resample_counts(labels, rng)
        denominator = sum(counts[index] for index in indices)
        if not denominator:
            undefined += 1
        else:
            lows.append(counts[CLASS_INDEX["bounded"]] / denominator)
            highs.append((counts[CLASS_INDEX["bounded"]] + counts[0]) / denominator)
    if undefined:
        return {"status": "undefined", "low": None, "high": None,
                "reason": "some resamples have zero conditional denominator; none were discarded",
                "zero_denominator_resamples": undefined, "resamples": resamples}
    return {"status": "complete", "low": quantile_function(lows, .025),
            "high": quantile_function(highs, .975), "resamples": resamples}


def bootstrap_p3(limit_only: Sequence[int], forever: Sequence[int], *, rng: random.Random,
                 quantile_function: Callable[[Sequence[float], float], float],
                 frame: str, resamples: int = RESAMPLES) -> dict[str, Any]:
    if frame not in P3_FRAMES:
        raise ValueError(f"unknown P3 frame: {frame}")
    if not limit_only or not forever:
        return {"status": "undefined", "low": None,
                "reason": "a comparison cell has zero computed draws"}
    lows, undefined = [], 0
    pooled = [(0, value) for value in limit_only] + [(1, value) for value in forever]
    for _ in range(resamples):
        if frame == "independent-cells":
            a, b = resample_counts(limit_only, rng), resample_counts(forever, rng)
            na, nb = len(limit_only), len(forever)
        else:
            a, b = [0] * len(COMPUTED), [0] * len(COMPUTED)
            for _ in pooled:
                cell, value = pooled[rng.randrange(len(pooled))]
                (a if cell == 0 else b)[value] += 1
            na, nb = sum(a), sum(b)
        if not na or not nb:
            undefined += 1
        else:
            grows = CLASS_INDEX["grows"]
            lows.append(a[grows] / na - (b[grows] + b[0]) / nb)
    if undefined:
        return {"status": "undefined", "low": None,
                "reason": "some resamples have an empty comparison cell; none were discarded",
                "empty_cell_resamples": undefined, "resamples": resamples}
    return {"status": "complete", "low": quantile_function(lows, .025),
            "resamples": resamples}


class BootstrapEngine:
    """Callable engines share an explicit quantile and explicit stream policy.

    Group execution order is CELL_ORDER, classes then P1 for each cell, then P3.
    Class bands within a cell share resamples.  ``reset-per-group`` initializes
    Random(SEED) for every nonempty bootstrap group.  ``shared`` uses one stream
    in the documented group order.  Sampling uses repeated randrange(n), which
    matches Random.choice on the individual draw positions exactly.
    """

    def __init__(self, *, quantile_function: Callable[[Sequence[float], float], float],
                 stream_policy: str, seed: int = SEED, resamples: int = RESAMPLES):
        if stream_policy not in STREAM_POLICIES:
            raise ValueError(f"unknown stream policy: {stream_policy}")
        self.quantile_function = quantile_function
        self.stream_policy = stream_policy
        self.seed, self.resamples = seed, resamples
        self.shared_rng = random.Random(seed)
        self.groups: list[str] = []

    def rng(self, group: str) -> random.Random:
        self.groups.append(group)
        return self.shared_rng if self.stream_policy == "shared" else random.Random(self.seed)


def histogram(records: dict[str, Family], weights: Counter[str], *, field: str,
              classes: Iterable[str]) -> dict[str, Any]:
    selected = frozenset(classes)
    bins: dict[Any, Counter[str]] = defaultdict(Counter)
    missing = Counter()
    for key, weight in weights.items():
        record = records.get(key)
        if record is None or record.cls not in selected:
            continue
        value = getattr(record, field)
        destination = missing if value is None else bins[value]
        destination["draws"] += weight
        destination["distinct_families"] += 1
    def sort_key(value: Any) -> Any:
        return Fraction(value) if field == "lambda_value" else value
    entries = []
    for value in sorted(bins, key=sort_key):
        entry = {"value": value, "draws": bins[value]["draws"],
                 "distinct_families": bins[value]["distinct_families"]}
        if field == "lambda_value":
            entry["float"] = float(Fraction(value))
        entries.append(entry)
    return {"histogram": entries,
            "not_available": {"draws": missing["draws"],
                              "distinct_families": missing["distinct_families"]},
            "binning": "one bin per exact recorded value; no numeric binning"}


def group_summary(draws: Sequence[Draw], records: dict[str, Family]) -> dict[str, Any]:
    weights = Counter(draw.key for draw in draws)
    by_draw: Counter[str] = Counter()
    by_family: Counter[str] = Counter()
    missing_draws = missing_families = invalid_class_draws = invalid_class_families = 0
    for key, weight in weights.items():
        record = records.get(key)
        if record is None:
            missing_draws += weight
            missing_families += 1
        elif record.cls is None:
            invalid_class_draws += weight
            invalid_class_families += 1
        else:
            by_draw[record.cls] += weight
            by_family[record.cls] += 1
    nd, nf = sum(by_draw[name] for name in COMPUTED), sum(by_family[name] for name in COMPUTED)
    ud, uf = by_draw["unresolved"], by_family["unresolved"]
    computed_classes = {}
    for name in COMPUTED:
        entry: dict[str, Any] = {"draws": by_draw[name], "distinct_families": by_family[name],
                                 "observed_draw_share": exact_share(by_draw[name], nd),
                                 "observed_distinct_family_share": exact_share(by_family[name], nf)}
        if name == "unresolved":
            entry["draw_share_band"] = pending("The spec does not define unresolved assigned against/for its own class.")
            entry["distinct_family_share_band"] = pending("The unresolved share is reported exactly, separately.")
        else:
            entry["draw_share_band"] = band(by_draw[name], ud, nd)
            entry["distinct_family_share_band"] = band(by_family[name], uf, nf)
        computed_classes[name] = entry
    p1d, p1f = sum(by_draw[name] for name in P1_CLASSES), sum(by_family[name] for name in P1_CLASSES)
    return {
        "draw_count": len(draws), "distinct_family_count": len(weights),
        "class_counts": {name: {"draws": by_draw[name], "distinct_families": by_family[name]}
                         for name in CLASSES},
        "coverage": {"missing_family_record_draws": missing_draws,
                     "missing_family_record_distinct_families": missing_families,
                     "invalid_class_draws": invalid_class_draws,
                     "invalid_class_distinct_families": invalid_class_families,
                     "all_draws_have_class": not (missing_draws or invalid_class_draws)},
        "computed": {"draw_count": nd, "distinct_family_count": nf,
                     "classes": computed_classes,
                     "unresolved_draw_share": exact_share(ud, nd),
                     "unresolved_distinct_family_share": exact_share(uf, nf),
                     "p1_bounded_conditional_share": {
                         "denominator_classes": sorted(P1_CLASSES),
                         "draws": band(by_draw["bounded"], ud, p1d),
                         "distinct_families": band(by_family["bounded"], uf, p1f)}},
        "lambda_distribution": histogram(records, weights, field="lambda_value", classes=COMPUTED),
        "bounded_uniform_cost_bound_distribution": histogram(records, weights, field="uniform_cost_bound", classes=("bounded",)),
        "bounded_onset_depth_distribution": histogram(records, weights, field="onset_depth", classes=("bounded",)),
    }


def labels_for(draws: Sequence[Draw], records: dict[str, Family]) -> list[int]:
    return [CLASS_INDEX[records[draw.key].cls] for draw in draws
            if draw.key in records and records[draw.key].cls in CLASS_INDEX]


def p3_point(limit_only: dict[str, Any], forever: dict[str, Any], *, weight: str) -> dict[str, Any]:
    a = limit_only["computed"]["classes"]
    b = forever["computed"]["classes"]
    count = "draws" if weight == "draws" else "distinct_families"
    na = limit_only["computed"]["draw_count" if weight == "draws" else "distinct_family_count"]
    nb = forever["computed"]["draw_count" if weight == "draws" else "distinct_family_count"]
    low = high = None
    if na and nb:
        low = a["grows"][count] / na - (b["grows"][count] + b["unresolved"][count]) / nb
        high = (a["grows"][count] + a["unresolved"][count]) / na - b["grows"][count] / nb
    return {"low": low, "high": high, "limit_only_denominator": na, "forever_denominator": nb,
            "unresolved_assignment_low": "against limit-only growth, for forever growth",
            "unresolved_assignment_high": "for limit-only growth, against forever growth"}


def agreement_matrix(records: dict[str, Family], alternative: dict[str, Family],
                     draw_keys: set[str]) -> dict[str, Any]:
    matrix = {first: {last: 0 for last in CLASSES} for first in CLASSES}
    paired = agrees = missing = invalid = not_drawn = 0
    for key, last in alternative.items():
        if key not in draw_keys:
            not_drawn += 1
            continue
        first = records.get(key)
        if first is None:
            missing += 1
        elif first.cls not in CLASSES or last.cls not in CLASSES:
            invalid += 1
        else:
            matrix[first.cls][last.cls] += 1
            paired += 1
            agrees += first.cls == last.cls
    return {"weight": "distinct sampled families", "rows": "first-call class",
            "columns": "last-call class", "matrix": matrix,
            "paired_distinct_families": paired, "same_class": exact_share(agrees, paired),
            "coverage": {"alternative_records_missing_first_call_record": missing,
                         "alternative_records_with_invalid_class": invalid,
                         "alternative_records_not_in_draws": not_drawn,
                         "first_call_draw_families_without_alternative_record": len(draw_keys - alternative.keys()),
                         "note": "No eligibility or absent alternative records are inferred."}}


def build_summary(draws: Sequence[Draw], records: dict[str, Family],
                  alternative: dict[str, Family], *, quantile_convention: str | None = None,
                  stream_policy: str | None = None, p1_frame: str | None = None,
                  p3_frame: str | None = None, resamples: int = RESAMPLES) -> dict[str, Any]:
    cells: dict[str, list[Draw]] = {name: [] for name in CELL_ORDER}
    unassigned, g4_failures = Counter(), 0
    for draw in draws:
        cells["all"].append(draw)
        record = records.get(draw.key)
        usual = record.usual_limit_alive if record else None
        if draw.fate == "forever":
            cells["forever"].append(draw)
            g4_failures += usual is False
        elif usual is False:
            cells["dies_with_dead_usual_limit"].append(draw)
        elif usual is True:
            cells["alive_only_in_limit"].append(draw)
        else:
            unassigned[draw.key] += 1
    output_cells = {}
    for name in CELL_ORDER:
        members = cells[name]
        summary = group_summary(members, records)
        ndefs: dict[str, list[Draw]] = {"1": [], ">1": [], "not_available": []}
        s_own: dict[str, list[Draw]] = defaultdict(list)
        for draw in members:
            record = records.get(draw.key)
            number = record.n_defs if record else None
            ndefs["1" if number == 1 else ">1" if number is not None and number > 1 else "not_available"].append(draw)
            own = record.s_own if record else None
            s_own[str(own) if own is not None else "not_available"].append(draw)
        summary["by_n_defs"] = {key: group_summary(value, records) for key, value in ndefs.items()}
        summary["by_s_own"] = {key: group_summary(s_own[key], records)
                               for key in sorted(s_own, key=lambda key: (key == "not_available", int(key) if key != "not_available" else 0))}
        output_cells[name] = summary
    questions = [
        {"question": "Which finite-sample quantile convention defines the bootstrap 2.5% and 97.5% endpoints?",
         "affected": "all bootstrap endpoints", "choice": quantile_convention},
        {"question": "Is Random(20261113) reset per bootstrap group or shared, and in which group order?",
         "affected": "all bootstrap endpoints", "choice": stream_policy},
        {"question": "For the unresolved class itself, what does assigning unresolved against/for its own share mean?",
         "affected": "unresolved class low/high bands only; its observed share is exact", "choice": None},
        {"question": "Does P1 resample its conditional denominator directly, or all computed draws before conditioning?",
         "affected": "P1 bootstrap endpoints only", "choice": p1_frame},
        {"question": "Does P3 resample each comparison cell independently or pool the two cells before regrouping?",
         "affected": "P3 bootstrap lower endpoint only", "choice": p3_frame},
    ]
    base_missing = [name for name, value in (("quantile convention", quantile_convention),
                                            ("stream policy", stream_policy)) if value is None]
    engine = None
    if not base_missing:
        q = lambda values, p: quantile(values, p, convention=quantile_convention)
        engine = BootstrapEngine(quantile_function=q, stream_policy=stream_policy, resamples=resamples)
    bootstrap_reason = "Unspecified " + " and ".join(base_missing) if base_missing else ""
    for name in CELL_ORDER:
        labels = labels_for(cells[name], records)
        computed = output_cells[name]["computed"]
        intervals = (bootstrap_class_bands(labels, rng=engine.rng(f"cell:{name}:classes"),
                                          quantile_function=engine.quantile_function, resamples=resamples)
                     if engine else {})
        for cls in COMPUTED:
            if cls == "unresolved":
                computed["classes"][cls]["bootstrap_95_interval"] = pending("Unresolved's own uncertainty band is not defined.")
            else:
                computed["classes"][cls]["bootstrap_95_interval"] = intervals.get(cls, pending(bootstrap_reason))
        if engine and p1_frame:
            interval = bootstrap_p1(labels, rng=engine.rng(f"cell:{name}:p1"),
                                    quantile_function=engine.quantile_function, frame=p1_frame, resamples=resamples)
        else:
            interval = pending("; ".join(filter(None, (bootstrap_reason, "Unspecified P1 bootstrap frame" if not p1_frame else ""))))
        computed["p1_bounded_conditional_share"]["bootstrap_95_interval"] = interval
    difference = {"definition": "computed limit-only grows share minus computed forever grows share",
                  "draws": p3_point(output_cells["alive_only_in_limit"], output_cells["forever"], weight="draws"),
                  "distinct_families": p3_point(output_cells["alive_only_in_limit"], output_cells["forever"], weight="families")}
    if engine and p3_frame:
        difference["bootstrap_low_2_5_percent"] = bootstrap_p3(
            labels_for(cells["alive_only_in_limit"], records), labels_for(cells["forever"], records),
            rng=engine.rng("p3"), quantile_function=engine.quantile_function, frame=p3_frame, resamples=resamples)
    else:
        difference["bootstrap_low_2_5_percent"] = pending("; ".join(filter(None, (bootstrap_reason, "Unspecified P3 bootstrap frame" if not p3_frame else ""))))
    return {
        "schema_version": 1,
        "classes": {"settled": list(SETTLED), "computed": list(COMPUTED)},
        "basis": "available valid draws joined to available nonconflicting family records; missing records are not unresolved families",
        "distinct_family_shares": "exact counts of the sampled set; no bootstrap interval",
        "cell_definitions": {"all": "all usable draw rows",
                             "forever": "stored fate == forever",
                             "dies_with_dead_usual_limit": "stored fate != forever and family usual_limit_alive == false",
                             "alive_only_in_limit": "stored fate != forever and family usual_limit_alive == true"},
        "cells": output_cells, "total": output_cells["all"],
        "cell_membership_coverage": {"non_forever_draws_without_usual_limit_record": sum(unassigned.values()),
                                     "non_forever_distinct_families_without_usual_limit_record": len(unassigned),
                                     "unassigned_family_keys": sorted(unassigned),
                                     "forever_draws_with_dead_usual_limit": g4_failures},
        "p3_grows_share_difference": difference,
        "alternative_ray_agreement": agreement_matrix(records, alternative, {draw.key for draw in draws}),
        "bootstrap": {"seed": SEED, "resamples": resamples,
                      "sampling_unit": "individual draw positions, including repeated families",
                      "sampling_method": "repeated Random.randrange(n), identical to repeated Random.choice on individual draw positions",
                      "quantile_convention": quantile_convention, "stream_policy": stream_policy,
                      "p1_frame": p1_frame, "p3_frame": p3_frame,
                      "group_order": "cells all, forever, dies_with_dead_usual_limit, alive_only_in_limit; classes then P1 in each; P3 last",
                      "class_band_resamples": "all resolved class bands in one cell share its resamples",
                      "executed_groups": engine.groups if engine else [],
                      "stratified_breakdowns": "point counts and bands only; the spec requests bootstrap intervals per primary cell"},
        "compatibility_aliases": {"onset_depth": ["onset_depth", "depth_threshold",
                                                    "exact_eventual_boundedness.onset_depth",
                                                    "exact_eventual_boundedness.depth_threshold"],
                                  "uniform_cost_bound": ["uniform_cost_bound", "exact_eventual_boundedness.uniform_cost_bound"],
                                  "conflicting_aliases": "reported and excluded from the affected distribution"},
        "ambiguities": questions,
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("directory", type=Path, help="DIR containing families.jsonl and alt_families.jsonl; writes DIR/summary.json")
    parser.add_argument("--draws", type=Path, help="explicit draws.jsonl.gz; otherwise CODEX/draws.jsonl.gz, then DIR/draws.jsonl.gz")
    parser.add_argument("--quantile-convention", choices=QUANTILES, help="explicit endpoint rule; linear uses position (n-1)*p, nearest-rank uses ceil(n*p)")
    parser.add_argument("--bootstrap-stream-policy", choices=STREAM_POLICIES, help="explicit RNG reuse; see bootstrap metadata for group order")
    parser.add_argument("--p1-bootstrap-frame", choices=P1_FRAMES, help="explicit P1 resampling population")
    parser.add_argument("--p3-bootstrap-frame", choices=P3_FRAMES, help="explicit P3 resampling population")
    args = parser.parse_args(argv)
    code_directory = Path(__file__).resolve().parent
    directory = args.directory.resolve()
    if not directory.is_relative_to(code_directory):
        parser.error(f"output directory must resolve inside CODEX: {code_directory}")
    if not directory.is_dir():
        parser.error(f"output directory does not exist: {directory}")
    code_draws = code_directory / "draws.jsonl.gz"
    draws_path = args.draws.resolve() if args.draws else (code_draws if code_draws.is_file() else directory / "draws.jsonl.gz")
    draws, draw_info = read_draws(draws_path)
    records, family_info = read_families(directory / "families.jsonl")
    alternatives, alt_info = read_families(directory / "alt_families.jsonl")
    result = build_summary(draws, records, alternatives, quantile_convention=args.quantile_convention,
                           stream_policy=args.bootstrap_stream_policy, p1_frame=args.p1_bootstrap_frame,
                           p3_frame=args.p3_bootstrap_frame)
    keys = {draw.key for draw in draws}
    result["inputs"] = {"draws": draw_info, "families": family_info, "alternative_families": alt_info,
                        "draws_selection": "explicit --draws" if args.draws else "CODEX path preferred, DIR path used only when CODEX path absent"}
    result["coverage"] = {"draw_family_keys_without_record": sorted(keys - records.keys()),
                          "family_record_keys_not_in_draws": sorted(records.keys() - keys),
                          "usable_draws": len(draws), "usable_distinct_draw_families": len(keys),
                          "available_matched_family_records": len(keys & records.keys()),
                          "all_draw_families_have_record": not (keys - records.keys()),
                          "note": "Missing files, invalid rows, conflicting duplicate records, and unfinished inputs are reported; no rows are fabricated."}
    output = directory / "summary.json"
    output.write_text(json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")
    print(f"Wrote {output} ({len(draws)} usable draws; {len(keys & records.keys())}/{len(keys)} families joined).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
