"""Join a resumed path run to the A79 draws under addendum A6--A9.

The bootstrap samples the entire draw archive once per replicate. Every cell
and P1 table uses that same resample and recomputes its own denominator. Family
counts are exact and receive no bootstrap interval.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from fractions import Fraction
import gzip
import hashlib
import json
import math
from pathlib import Path
import random
import sys
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
CENSUS = ROOT / "artifacts/REACH-CENSUS-20261113-001A/REACH-CENSUS-20261113-001A-E001_reach_census/families.jsonl.gz"
DRAWS = ROOT / "experiments/REACH-CENSUS-20261113-001A/REACH-CENSUS-20261113-001A-E001_reach_census/codex/draws.jsonl.gz"
CLASSES = ("grows", "bounded", "mixed by residue", "lost at large depths", "none at any depth", "unresolved")
PERSISTING = frozenset(("grows", "bounded", "mixed by residue"))
SEED, RESAMPLES = 20261113, 2000
EXPECTED_DRAWS = 223261
CELL_ORDER = ("all", "forever", "limit_only")
POPULATION_CLASSES = ("grows", "bounded", "mixed by residue", "unresolved")
BOUNDED_SPLITS = ("bounded, carried only", "bounded, uncarried")


def permitted(path):
    path = Path(path).resolve()
    if not path.is_relative_to(HERE):
        raise ValueError(f"Output must be inside CODEX: {path}")
    return path


def dump(path, value):
    path = permitted(path)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n")
    tmp.replace(path)


def json_rows(path):
    path = Path(path)
    opener = gzip.open if path.suffix == ".gz" else open
    with opener(path, "rt") as stream:
        for number, line in enumerate(stream, 1):
            if line.strip():
                try:
                    yield json.loads(line)
                except json.JSONDecodeError as exc:
                    raise ValueError(f"Invalid JSON at {path}:{number}") from exc


def load_records(path):
    records = {}
    for row in json_rows(path):
        key = row["key"]
        if key in records:
            raise ValueError(f"Duplicate family key in {path}: {key}")
        records[key] = row
    return records


def metadata(key, row):
    defs = json.loads(key)
    s = row.get("S")
    c = row.get("c")
    if c is None:
        c = 0 if s is None else sum(name == "SELF" for name, _ in defs[s][2])
    return int(c), row.get("first_ray_class", row.get("census_class", row.get("class"))), len(defs)


def share(numerator, denominator):
    return {"numerator": numerator, "denominator": denominator,
            "fraction": str(Fraction(numerator, denominator)) if denominator else None,
            "share": numerator / denominator if denominator else None}


def band(numerator, unresolved, denominator):
    return {"numerator_low": numerator, "numerator_high": numerator + unresolved,
            "denominator": denominator,
            "fraction_low": str(Fraction(numerator, denominator)) if denominator else None,
            "fraction_high": str(Fraction(numerator + unresolved, denominator)) if denominator else None,
            "low": numerator / denominator if denominator else None,
            "high": (numerator + unresolved) / denominator if denominator else None}


def pending(question):
    return {"status": "skipped_ambiguity", "question": question}


def linear_quantile(values, p):
    if not values:
        return None
    values = sorted(values)
    index = (len(values) - 1) * p
    low, high = math.floor(index), math.ceil(index)
    return values[low] + (values[high] - values[low]) * (index - low)


class SharedBootstrap:
    """Compile ratio contributions, then share each whole-archive resample.

    A draw position is the sampling unit, including duplicate family draws.
    Identical contribution vectors are compressed only after every table is
    registered; the Python RNG still draws one archive index per draw position.
    """

    def __init__(self, draw_tokens, *, resamples=RESAMPLES):
        self.draw_tokens = draw_tokens
        self.resamples = resamples
        self.metrics = []
        self.contributions = defaultdict(lambda: [[], [], []])

    def add(self, target, keys, positive, unknown, *, buckets=None, name):
        index = len(self.metrics)
        self.metrics.append((name, target))
        positive, unknown = set(positive), set(unknown)
        if positive & unknown:
            raise ValueError(f"Overlapping positive/unknown labels in {name}")
        for key in keys:
            for bucket in (0, 1, 2) if buckets is None else buckets:
                denominator, low, high = self.contributions[(key, bucket)]
                denominator.append(index)
                if key in positive:
                    low.append(index)
                if key in positive or key in unknown:
                    high.append(index)

    def run(self, rng):
        import numpy as np

        n, m = len(self.draw_tokens), len(self.metrics)
        if self.resamples < 1:
            raise ValueError("At least one bootstrap replicate is required")
        signatures, categories, draw_categories = {}, [], []
        for token in self.draw_tokens:
            signature = tuple(tuple(ids) for ids in self.contributions.get(token, ((), (), ())))
            if signature not in signatures:
                signatures[signature] = len(categories)
                categories.append(signature)
            draw_categories.append(signatures[signature])
        metric_ids, category_ids = [[], [], []], [[], [], []]
        for category, signature in enumerate(categories):
            for kind, ids in enumerate(signature):
                metric_ids[kind].extend(ids)
                category_ids[kind].extend([category] * len(ids))
        metric_ids = [np.asarray(ids, dtype=np.int64) for ids in metric_ids]
        category_ids = [np.asarray(ids, dtype=np.int64) for ids in category_ids]
        lows = np.full((self.resamples, m), np.nan)
        highs = np.full((self.resamples, m), np.nan)
        if n and m:
            for replicate in range(self.resamples):
                # Exactly n randrange(n) calls, independent of cell membership.
                sampled = np.fromiter((draw_categories[rng.randrange(n)] for _ in range(n)),
                                      dtype=np.int64, count=n)
                frequencies = np.bincount(sampled, minlength=len(categories))
                totals = [np.bincount(metric_ids[kind], weights=frequencies[category_ids[kind]],
                                      minlength=m) for kind in range(3)]
                valid = totals[0] != 0
                np.divide(totals[1], totals[0], out=lows[replicate], where=valid)
                np.divide(totals[2], totals[0], out=highs[replicate], where=valid)
        for index, (_, target) in enumerate(self.metrics):
            low = lows[:, index]
            high = highs[:, index]
            finite = ~np.isnan(low)
            used = int(finite.sum())
            defined = used == self.resamples
            target.update(status="complete" if defined else "skipped_ambiguity" if used else "undefined",
                low=linear_quantile(low.tolist(), .025) if defined else None,
                high=linear_quantile(high.tolist(), .975) if defined else None,
                resamples=self.resamples, defined_resamples=used,
                zero_denominator_resamples=self.resamples - used,
                frame="whole A79 draw archive", archive_draws=n,
                quantiles="linear at (n - 1)p", seed=SEED,
                common_archive_resample=True)
            if not used:
                target["reason"] = "zero denominator in every archive resample"
            elif not defined:
                target["question"] = ("How should zero-denominator archive resamples enter the "
                    "specified 2000-replicate linear quantiles? No undefined-replicate "
                    "convention is selected, and no replicate is silently dropped.")
        return {"seed": SEED, "resamples": self.resamples, "archive_draws": n,
                "expected_archive_draws": EXPECTED_DRAWS,
                "matches_expected_archive_draws": n == EXPECTED_DRAWS,
                "sampling_unit": "archive draw position, including repeated family draws",
                "frame": "whole A79 draw archive", "quantiles": "linear at (n - 1)p",
                "common_archive_resample": True,
                "rng": "one random.Random(20261113), n randrange(n) calls per replicate",
                "metric_order": [name for name, _ in self.metrics],
                "intervals_skipped_ambiguity": [name for name, target in self.metrics
                    if target["status"] == "skipped_ambiguity"],
                "cell_order": list(CELL_ORDER), "P1_tables_after_cells": True,
                "zero_denominator_replicates": "retain counts; skip only the affected interval without choosing an undefined-replicate convention",
                "family_count_intervals": "none; distinct-family counts are exact"}


def classes_of(rows, keys, weights):
    family, draw = Counter(), Counter()
    for key in keys:
        family[rows[key]["class"]] += 1
        draw[rows[key]["class"]] += weights.get(key, 0)
    return {name: {"families": family[name], "draws": draw[name]}
            for name in sorted(set(CLASSES) | family.keys())}


def cell_counts(rows, keys, weights):
    counts = classes_of(rows, keys, weights)
    return {"families": len(keys), "draws": sum(weights.get(k, 0) for k in keys),
            "classes": counts}


def uncarried_class(row):
    return row.get("class_path_uncarried", row.get("class_uncarried"))


def bounded_split(row):
    if row.get("class") != "bounded":
        return None
    value = row.get("bounded_split")
    if value in BOUNDED_SPLITS:
        return value
    unc = uncarried_class(row)
    if unc is not None:
        return "bounded, uncarried" if unc == "bounded" else "bounded, carried only"
    return None


def in_population(row, first_class):
    cls = row.get("class")
    return cls in PERSISTING or (cls == "unresolved" and
        not str(first_class).startswith(("S1 ", "S2 ", "S3 ")))


def ratio_table(keys, positive, unknown, weights, bootstrap, *, buckets, name):
    keys, positive, unknown = set(keys), set(positive), set(unknown)
    if not positive <= keys or not unknown <= keys:
        raise ValueError(f"Ratio labels lie outside the denominator: {name}")
    n, nd = len(keys), sum(weights.get(k, 0) for k in keys)
    p, u = sum(weights.get(k, 0) for k in positive), sum(weights.get(k, 0) for k in unknown)
    interval = {}
    result = {"count_observed": share(len(positive), n), "draw_weight_observed": share(p, nd),
        "count_band": band(len(positive), len(unknown), n),
        "draw_weight_band": band(p, u, nd), "bootstrap_95": interval}
    bootstrap.add(interval, sorted(keys), positive, unknown, buckets=buckets, name=name)
    return result


def population_cell(rows, keys, weights, meta, bootstrap, *, buckets, name):
    population = [k for k in keys if in_population(rows[k], meta[k][1])]
    population_set = set(population)
    outside = [k for k in keys if k not in population_set]
    unresolved = {k for k in population if rows[k]["class"] == "unresolved"}
    result = cell_counts(rows, population, weights)
    result["outside_population"] = cell_counts(rows, outside, weights)
    result["class_shares"] = {}
    for cls in POPULATION_CLASSES:
        positive = {k for k in population if rows[k]["class"] == cls}
        unknown = unresolved if cls != "unresolved" else set()
        item = ratio_table(population, positive, unknown, weights, bootstrap,
                           buckets=buckets, name=f"{name}.class.{cls}")
        if cls == "unresolved":
            item["band_meaning"] = "observed unresolved share; no reassignment to itself"
        result["class_shares"][cls] = item
    bounded = [k for k in population if rows[k]["class"] == "bounded"]
    missing_split = {k for k in bounded if bounded_split(rows[k]) is None}
    result["bounded_share_split"] = {}
    for label in BOUNDED_SPLITS:
        positive = {k for k in bounded if bounded_split(rows[k]) == label}
        result["bounded_share_split"][label] = ratio_table(population, positive,
            unresolved | missing_split, weights, bootstrap, buckets=buckets,
            name=f"{name}.split.{label}")
    result["bounded_split_missing_diagnostics"] = {"count": len(missing_split), "keys": sorted(missing_split)}
    return result


def p1(rows, keys, weights, bootstrap, *, exclusion_status, name, uncarried=False):
    n = len(keys)
    nd = sum(weights.get(k, 0) for k in keys)
    outcome = (lambda k: uncarried_class(rows[k])) if uncarried else (lambda k: rows[k]["class"])
    b = [k for k in keys if outcome(k) == "bounded"]
    u = [k for k in keys if outcome(k) in (None, "unresolved")]
    by_count = band(len(b), len(u), n)
    by_weight = band(sum(weights.get(k, 0) for k in b), sum(weights.get(k, 0) for k in u), nd)
    # Prediction decision uses the specified uncertainty bands; no unresolved
    # family is silently counted as bounded. Count bands are exact fractions.
    count_decision = ("undefined" if not n else "fails" if by_count["high"] < .75 else
                      "passes" if by_count["low"] >= .75 else "unresolved")
    weight_decision = ("undefined" if not nd else "fails" if by_weight["high"] <= .5 else
                       "passes" if by_weight["low"] > .5 else "unresolved")
    decision = ("fails" if "fails" in (count_decision, weight_decision) else
                "passes" if count_decision == weight_decision == "passes" else "unresolved")
    interval = {}
    bootstrap.add(interval, keys, b, u, name=name)
    return {"count": by_count, "draw_weight": by_weight,
            "bounded_observed_count": share(len(b), n),
            "bounded_observed_draw_weight": share(sum(weights.get(k, 0) for k in b), nd),
            "failure_thresholds": {"count": "< 75%", "draw_weight": "<= 50%"},
            "count_threshold_verdict": count_decision, "draw_weight_band_verdict": weight_decision,
            "prediction_verdict": decision, "exclusion_status": exclusion_status,
            "target": "uncarried boundedness" if uncarried else "boundedness over paths",
            "verdict_basis": "exact count uncertainty band and observed draw-weight uncertainty band; frozen thresholds",
            "draw_weight_bootstrap_95": interval}


def count_flag(rows, keys, field):
    positives = [k for k in keys if rows[k].get(field) is True]
    negatives = [k for k in keys if rows[k].get(field) is False]
    unknown = [k for k in keys if rows[k].get(field) not in (True, False)]
    return {"true": len(positives), "false": len(negatives), "unknown": len(unknown),
            "true_keys": positives, "unknown_keys": unknown}


def build_summary(draws, rows, census, exclusion224=None, *, resamples=RESAMPLES):
    """Build tables; ``resamples`` is injectable for tiny synthetic controls.

    Production callers pass the full draw dictionaries, preserving ``fate``.
    Legacy key-only callers can still obtain the all table; cell coverage marks
    their absent fate metadata and prevents a complete analysis declaration.
    """
    draws = [{"key": draw} if isinstance(draw, str) else draw for draw in draws]
    draw_keys = [draw["key"] for draw in draws]
    weights = Counter(draw_keys)
    requested = set(census)
    present = requested & rows.keys()
    missing, extra = sorted(requested - rows.keys()), sorted(rows.keys() - requested)
    meta = {key: metadata(key, {**census[key], **rows[key]}) for key in present}
    first_groups, c_groups, cross = defaultdict(list), defaultdict(list), defaultdict(list)
    for key in sorted(present):
        c, first, _ = meta[key]
        first_groups[first].append(key)
        c_groups[str(c)].append(key)
        cross[(first, c)].append(key)
    growers = sorted(k for k in present if rows[k].get("lambda_path", rows[k].get("lambda")) is not None
                     and Fraction(rows[k].get("lambda_path", rows[k].get("lambda"))) > 0
                     and rows[k].get("complete") is True and rows[k].get("class") == "grows")
    bounded = sorted(k for k in present if rows[k].get("class") == "bounded")
    eligible_p1 = sorted(k for k in present if meta[k][0] >= 2 and meta[k][1] == "grows")
    # All metrics are registered before any random number is consumed. Their
    # common archive resample is generated once per replicate, never per cell.
    tokens = []
    cell_weights = {name: Counter() for name in CELL_ORDER}
    fate_missing, unassigned_nonforever, forever_dead = Counter(), Counter(), Counter()
    for draw in draws:
        key, fate = draw["key"], draw.get("fate")
        usual = rows.get(key, {}).get("usual_limit_alive", census.get(key, {}).get("usual_limit_alive"))
        bucket = 0
        if fate == "forever":
            bucket = 1
            cell_weights["forever"][key] += 1
            if usual is False:
                forever_dead[key] += 1
        elif fate is not None and usual is True:
            bucket = 2
            cell_weights["limit_only"][key] += 1
        elif fate is None:
            fate_missing[key] += 1
        elif usual is None:
            unassigned_nonforever[key] += 1
        cell_weights["all"][key] += 1
        tokens.append((key, bucket))
    bootstrap = SharedBootstrap(tokens, resamples=resamples)
    cells = {}
    for cell_name in CELL_ORDER:
        cw = cell_weights[cell_name]
        keys = sorted(present if cell_name == "all" else present & cw.keys())
        buckets = None if cell_name == "all" else (1,) if cell_name == "forever" else (2,)
        first, by_c, paired = defaultdict(list), defaultdict(list), defaultdict(list)
        for key in keys:
            c, first_class, _ = meta[key]
            first[first_class].append(key)
            by_c[str(c)].append(key)
            paired[(first_class, c)].append(key)
        table = lambda selected, suffix: population_cell(rows, selected, cw, meta, bootstrap,
            buckets=buckets, name=f"cells.{cell_name}.{suffix}")
        cells[cell_name] = {
            "raw_join_counts": cell_counts(rows, keys, cw),
            "population": table(keys, "population"),
            "by_first_ray_class": {f: table(ks, f"by_first_ray_class.{f}") for f, ks in sorted(first.items())},
            "by_c": {c: table(ks, f"by_c.{c}") for c, ks in sorted(by_c.items(), key=lambda item: int(item[0]))},
            "by_first_ray_class_and_c": [{"first_ray_class": f, "c": c,
                **table(ks, f"by_first_ray_class_and_c.{f}.{c}")} for (f, c), ks in sorted(paired.items())],
        }
    all_p1 = p1(rows, eligible_p1, weights, bootstrap, name="P1.all",
                exclusion_status="all first-ray growers with c >= 2")
    excluded_keys = None
    if exclusion224 is None:
        excluded_p1 = pending("The exact 224-key exclusion manifest has not been established by G-last.")
    else:
        if len(exclusion224) != 224:
            raise ValueError(f"Expected exactly 224 exclusion keys, got {len(exclusion224)}")
        excluded_keys = [k for k in eligible_p1 if k not in exclusion224]
        excluded_p1 = p1(rows, excluded_keys, weights, bootstrap, name="P1.excluding_224",
                          exclusion_status="exact G-last key strings; no semantic identity quotient")
        excluded_p1["exclusion_keys_present_in_census"] = len(exclusion224 & census.keys())
        excluded_p1["exclusion_keys_present_in_P1"] = len(exclusion224 & set(eligible_p1))
    uncarried_p1 = p1(rows, eligible_p1, weights, bootstrap, name="P1.uncarried.all", uncarried=True,
                     exclusion_status="all first-ray growers with c >= 2")
    if excluded_keys is None:
        uncarried_excluded_p1 = pending("The exact 224-key exclusion manifest has not been established by G-last.")
    else:
        uncarried_excluded_p1 = p1(rows, excluded_keys, weights, bootstrap,
            name="P1.uncarried.excluding_224", uncarried=True,
            exclusion_status="exact G-last key strings; no semantic identity quotient")
    if missing or extra:
        for table in (all_p1, excluded_p1, uncarried_p1, uncarried_excluded_p1):
            if "prediction_verdict" in table:
                table["observed_records_only_verdict"] = table["prediction_verdict"]
                table["prediction_verdict"] = "pending_incomplete_population"
    bootstrap_info = bootstrap.run(random.Random(SEED))
    distribution = Counter()
    weighted_distribution = Counter()
    for key in sorted(present):
        value = rows[key].get("lambda_path", rows[key].get("lambda"))
        name = "None" if value is None else str(Fraction(value))
        distribution[name] += 1
        weighted_distribution[name] += weights.get(key, 0)
    rescued = sorted(k for k in present if meta[k][1] in ("none at any depth", "lost at large depths")
                     and rows[k]["class"] in ("grows", "bounded"))
    unresolved_by_c = {}
    for c, keys in sorted(c_groups.items(), key=lambda item: int(item[0])):
        unresolved = [k for k in keys if rows[k]["class"] == "unresolved"]
        unresolved_by_c[c] = {"count": share(len(unresolved), len(keys)),
            "draw_weight": share(sum(weights.get(k, 0) for k in unresolved), sum(weights.get(k, 0) for k in keys))}
    growers_uncarried = sorted(k for k in growers if uncarried_class(rows[k]) == "grows")
    growers_not_uncarried = sorted(k for k in growers if uncarried_class(rows[k]) not in (None, "grows", "unresolved"))
    growers_uncarried_unknown = sorted(k for k in growers if uncarried_class(rows[k]) in (None, "unresolved"))
    bounded_uncarried = sorted(k for k in bounded if bounded_split(rows[k]) == "bounded, uncarried")
    bounded_carried = sorted(k for k in bounded if bounded_split(rows[k]) == "bounded, carried only")
    bounded_unknown = sorted(k for k in bounded if bounded_split(rows[k]) is None)
    eligible_symmetry = [k for k in growers if meta[k][0] >= 2]
    symmetry = count_flag(rows, eligible_symmetry, "symmetry_inequivalent")
    first_carried_rows = {k: {"first_ray_carried": rows[k].get("first_ray_carried")}
                          for k in present}
    diagnostic_missing = {"uncarried_class": sorted(k for k in present
        if not str(rows[k]["class"]).startswith(("S1 ", "S2 ", "S3 ")) and uncarried_class(rows[k]) is None),
        "bounded_split": bounded_unknown, "symmetry_for_c_ge_2_growers": symmetry["unknown_keys"]}
    complete = not (missing or extra or weights.keys() - census.keys() or fate_missing or
        unassigned_nonforever or forever_dead or len(draws) != EXPECTED_DRAWS or
        exclusion224 is None or any(diagnostic_missing.values()) or
        bootstrap_info["intervals_skipped_ambiguity"])
    return {
        "experiment_id": "EVERY-RAY-20261113-001A-E001",
        "analysis_complete": complete,
        "coverage": {"complete_population_join": not missing and not extra,
            "census_families": len(census), "path_families": len(rows),
            "draws": len(draw_keys), "distinct_draw_keys": len(weights),
            "expected_draws": EXPECTED_DRAWS, "matches_expected_draws": len(draw_keys) == EXPECTED_DRAWS,
            "missing_family_keys": missing, "unexpected_family_keys": extra,
            "draw_keys_missing_from_census": sorted(weights.keys() - census.keys()),
            "draws_missing_fate": sum(fate_missing.values()),
            "nonforever_draws_missing_usual_limit": sum(unassigned_nonforever.values()),
            "forever_draws_with_dead_usual_limit": sum(forever_dead.values()),
            "missing_diagnostics": diagnostic_missing},
        "population": {"included_classes": list(POPULATION_CLASSES),
            "unresolved_membership": "include unless census class is S1, S2 or S3",
            "none_and_lost": "outside population; reported as counts",
            "counts": {"families": cells["all"]["population"]["families"],
                       "draws": cells["all"]["population"]["draws"]},
            "count_shares": "exact for this distinct-family archive; no bootstrap",
            "draw_weight_bands": "unresolved against a class for low and for it for high"},
        "cells": cells,
        "cell_definitions": {"all": "all archive draws",
            "forever": "stored fate == forever",
            "limit_only": "stored fate != forever and usual_limit_alive == true"},
        "bootstrap": bootstrap_info,
        "raw_join_counts_without_population_filter": {
            "all": cell_counts(rows, sorted(present), weights),
            "by_first_ray_class": {name: cell_counts(rows, keys, weights) for name, keys in sorted(first_groups.items())},
            "by_c": {c: cell_counts(rows, keys, weights) for c, keys in sorted(c_groups.items(), key=lambda item: int(item[0]))},
            "by_first_ray_class_and_c": [{"first_ray_class": first, "c": c, **cell_counts(rows, keys, weights)}
                for (first, c), keys in sorted(cross.items())]},
        "P1": {"all": all_p1, "excluding_224": excluded_p1,
               "uncarried": {"all": uncarried_p1, "excluding_224": uncarried_excluded_p1},
               "primary_population": "excluding_224",
               "bootstrap_order": ["all", "excluding_224", "uncarried.all", "uncarried.excluding_224"],
               "bootstrap_stream": "same whole-archive resample as all cells in each replicate"},
        "bounded_split": {"bounded, carried only": {"count": len(bounded_carried),
            "draws": sum(weights.get(k, 0) for k in bounded_carried), "keys": bounded_carried},
            "bounded, uncarried": {"count": len(bounded_uncarried),
            "draws": sum(weights.get(k, 0) for k in bounded_uncarried), "keys": bounded_uncarried},
            "unknown": {"count": len(bounded_unknown), "keys": bounded_unknown}},
        "first_ray_carried": count_flag(first_carried_rows, sorted(present), "first_ray_carried"),
        "bounded_needing_mixed_path": count_flag(rows, bounded, "mixed_path_needed"),
        "no_first_ray_bond_but_persisting_over_paths": {"count": len(rescued), "keys": rescued},
        "growers_over_paths": {"count": len(growers),
            "c_ge_2_count": sum(meta[k][0] >= 2 for k in growers),
            "one_ray_count": sum(meta[k][0] == 1 for k in growers),
            "symmetry_inequivalent": symmetry,
            "uncarried_also_grows": {"count": len(growers_uncarried),
                "draws": sum(weights.get(k, 0) for k in growers_uncarried), "keys": growers_uncarried},
            "uncarried_does_not_grow": {"count": len(growers_not_uncarried),
                "draws": sum(weights.get(k, 0) for k in growers_not_uncarried), "keys": growers_not_uncarried},
            "uncarried_unknown": {"count": len(growers_uncarried_unknown), "keys": growers_uncarried_unknown},
            "keys": growers},
        "zero_mean_cycles_using_pass_through": count_flag(rows, sorted(present), "zero_mean_cycle_uses_pass_through"),
        "lambda_distribution_without_population_filter": {name: {"families": count, "draws": weighted_distribution[name]}
            for name, count in sorted(distribution.items())},
        "unresolved_share_by_c_without_population_filter": unresolved_by_c,
        "scientific_interpretation": None,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    args = parser.parse_args()
    directory = permitted(args.directory)
    started = time.monotonic()
    rows = load_records(directory / "families.jsonl")
    census = load_records(CENSUS)
    draws = list(json_rows(DRAWS))
    if len(draws) != EXPECTED_DRAWS:
        raise ValueError(f"Expected the entire {EXPECTED_DRAWS}-draw archive, got {len(draws)}")
    manifest = HERE / "gate_last_keys.json"
    exclusion = None
    if manifest.exists():
        obj = json.loads(manifest.read_text())
        exclusion = set(obj["keys"] if isinstance(obj, dict) else obj)
    summary = build_summary(draws, rows, census, exclusion)
    summary["inputs"] = {"families": str(directory / "families.jsonl"), "census": str(CENSUS), "draws": str(DRAWS),
        "code_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    summary["summary_seconds"] = time.monotonic() - started
    dump(directory / "summary.json", summary)
    print(json.dumps({"summary": str(directory / "summary.json"), "complete_population_join": summary["coverage"]["complete_population_join"],
        "seconds": summary["summary_seconds"], "analysis_complete": summary["analysis_complete"]}), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
