"""Reconstruct late descriptions and directly compare observed rounds to two references."""

import argparse
import gzip
import json
from collections import Counter, defaultdict
from dataclasses import dataclass
from functools import cache
from itertools import combinations, islice
from math import comb
from pathlib import Path
from time import perf_counter


HERE = Path(__file__).resolve().parent
READINGS = ("sig0", "sig1")
DESCRIPTIONS = (
    "exact",
    "support",
    "degrees",
    "constants_and_growing",
    "constants_and_degrees",
    "constants_and_leading_coefficients",
    "all_differences",
    "constants_and_all_growing_differences",
)
NAMES = {}
TYPES = []


def frozen(value):
    return tuple(frozen(v) for v in value) if isinstance(value, list) else value


def signature_number(signature):
    key = frozen(signature)
    if key not in NAMES:
        NAMES[key] = len(TYPES)
        TYPES.append(key)
    return NAMES[key]


def differences(values):
    return [b - a for a, b in zip(values, values[1:])]


def dimension(counts):
    if len(counts) < 8:
        return None
    current = counts[-8:]
    for d in range(1, 5):
        if len(set(current)) == 1 and current[0] > 0:
            return d
        current = differences(current)
    return None


def coefficients(values):
    out = []
    while values:
        out.append(values[0])
        values = differences(values)
    while out and out[-1] == 0:
        out.pop()
    return tuple(out)


@cache
def basis(r, k):
    if r < 0:
        return (-1) ** k * comb(k - r - 1, k)
    return comb(r, k)


def evaluate(poly, r):
    return sum(a * basis(r, j) for j, a in enumerate(poly))


@cache
def values_at(polys, r):
    return {key: n for key, p in polys if (n := evaluate(p, r))}


def tail_polynomials(rows, d):
    # The last d observations determine degree at most d-1. Move each fit to
    # the common binomial basis at round zero, including for capped runs.
    sample = rows[-d:]
    start = len(rows) - d + 1
    result = []
    for key in set().union(*sample):
        provisional = coefficients([row.get(key, 0) for row in sample])
        absolute = coefficients([evaluate(provisional, r-start) for r in range(d)])
        if absolute:
            result.append((key, absolute))
    result = tuple(sorted(result))
    first = len(rows) + 1
    for r in range(len(rows), 0, -1):
        if values_at(result, r) != rows[r-1]:
            break
        first = r
    assert len(rows) - first + 1 >= d
    return result, first


def describe(polys, name):
    if name == "exact":
        return polys
    out = []
    for key, p in polys:
        degree = len(p) - 1
        if name == "support":
            value = ()
        elif name == "degrees":
            value = (degree,)
        elif name == "constants_and_growing":
            value = ("growing",) if degree else ("constant", p[0])
        elif name == "constants_and_degrees":
            value = ("degree", degree) if degree else ("constant", p[0])
        elif name == "constants_and_leading_coefficients":
            value = (degree, p[-1])
        elif name == "all_differences":
            value = p[1:]
        elif name == "constants_and_all_growing_differences":
            value = ("differences", *p[1:]) if degree else ("constant", p[0])
        else:
            raise ValueError(name)
        out.append((key, value))
    return tuple(out)


@dataclass
class View:
    start: dict
    rows: list
    polys: tuple
    first: int


def read_starts(phase, prefix):
    cells = defaultdict(list)
    visited = 0
    filename = HERE.parent / f"phase{phase}_grown.jsonl.gz"
    with gzip.open(filename, "rt") as f:
        for line in islice(f, prefix):
            s = json.loads(line)
            visited += 1
            d = dimension([r["n"] for r in s["rows"]])
            assert (d is None and not s["kind"].startswith("dim ")) or s["kind"] == f"dim {d}"
            if d is None:
                continue
            start = {k: s[k] for k in ("n knots", "index", "stars")}
            for reading in READINGS:
                rows = []
                for round_row in s["rows"]:
                    row = {signature_number(k): n for k, n in round_row[reading]}
                    assert len(row) == len(round_row[reading]) and sum(row.values()) == round_row["n"]
                    rows.append(row)
                polys, first = tail_polynomials(rows, d)
                cells[d, reading].append(View(start, rows, polys, first))
    return cells, visited


def subset(a, b):
    return all(n <= b.get(k, 0) for k, n in a.items())


def nested(a, b):
    return subset(a, b) or subset(b, a)


def comparison(view, reference):
    common = min(len(view.rows), len(reference.rows))
    start = None
    for r in range(common, 0, -1):
        if not nested(view.rows[r-1], reference.rows[r-1]):
            break
        start = r
    return common, start


def counts_named(counts):
    return [[TYPES[k], v] for k, v in sorted(counts.items())]


def reference_table(views, refs, d):
    per_ref = {name: {"coarse_by_nested": Counter(), "first_agreeing_round": Counter(),
                      "nested_at_last_common": 0, "equal_at_last_common": 0,
                      "equal_polynomials": 0,
                      "common_round": Counter()} for name in refs}
    both = Counter()
    lone_only_example = None
    for v in views:
        common_flags = []
        for name, ref in refs.items():
            table = per_ref[name]
            h, first = comparison(v, ref)
            coarse = describe(v.polys, "constants_and_growing") == describe(ref.polys, "constants_and_growing")
            table["coarse_by_nested"][f"coarse={coarse}, nested={first is not None}"] += 1
            table["first_agreeing_round"][str(first) if first is not None else "never"] += 1
            table["common_round"][h] += 1
            table["nested_at_last_common"] += first is not None
            table["equal_at_last_common"] += v.rows[h-1] == ref.rows[h-1]
            table["equal_polynomials"] += v.polys == ref.polys
            common_flags.append(first is not None)
        key = tuple(refs)
        both["both" if all(common_flags) else key[0] if common_flags[0]
             else key[1] if common_flags[1] else "neither"] += 1
        if d == 2 and common_flags == [True, False] and lone_only_example is None:
            r = min(len(v.rows), *(len(ref.rows) for ref in refs.values()))
            lone_only_example = {"start": v.start, "round": r, "counts": counts_named(v.rows[r-1]),
                                 "reference_counts": {name: counts_named(ref.rows[r-1])
                                                      for name, ref in refs.items()}}
    return {"reference_by_reference": per_ref, "nested_with_references": both,
            "first_example_comparable_to_lone_only": lone_only_example}


def incomparable_example(a, b, r):
    left, right = a.rows[r-1], b.rows[r-1]
    assert not nested(left, right)
    return {"round": r, "first_start": a.start, "second_start": b.start,
            "first_counts": counts_named(left), "second_counts": counts_named(right)}


def check_class(group):
    # Models with the same polynomial, first round of fit, and horizon have
    # identical observed counts on their common fitted rounds; one counts
    # comparisons for the full multiplicity of each pair of such models.
    types = defaultdict(list)
    for v in group:
        types[v.polys, v.first, len(v.rows)].append(v)
    tally = Counter()
    witness = None
    for a, b in combinations(types.values(), 2):
        left, right = a[0], b[0]
        weight = len(a)*len(b)
        stop = min(len(left.rows), len(right.rows))
        begin = max(left.first, right.first)
        if left.polys == right.polys and stop >= begin:
            continue
        if stop < begin:
            tally["no_jointly_settled_round"] += weight
            assert stop >= 1
        failed = [r for r in range(begin, stop+1)
                  if not nested(left.rows[r-1], right.rows[r-1])]
        last_fails = not nested(left.rows[stop-1], right.rows[stop-1])
        if failed:
            tally["some_jointly_settled_incomparable"] += weight
            if len(failed) == stop - begin + 1:
                tally["every_jointly_settled_incomparable"] += weight
        if last_fails:
            tally["last_common_incomparable"] += weight
            if witness is None:
                witness = incomparable_example(left, right, stop)
    return {"starts": len(group), "pairs": comb(len(group), 2),
            "different_exact_polynomials": len({v.polys for v in group}),
            "incomparable": {k: tally[k] for k in (
                "last_common_incomparable", "some_jointly_settled_incomparable",
                "every_jointly_settled_incomparable", "no_jointly_settled_round")},
            "last_common_witness": witness}


def summary(views, refs, d):
    descriptions = {}
    coarse = [describe(v.polys, "constants_and_growing") for v in views]
    for name in DESCRIPTIONS:
        keys = [describe(v.polys, name) for v in views]
        groups = Counter(keys)
        same = len(set(zip(coarse, keys))) == len(set(coarse)) == len(groups)
        descriptions[name] = {"classes": len(groups), "same_partition_as_constants_and_growing": same,
                              "reference_memberships": {
            key: groups[describe(ref.polys, name)] for key, ref in refs.items()}}
    coarse_groups = defaultdict(list)
    for v in views:
        coarse_groups[describe(v.polys, "constants_and_growing")].append(v)
    classes = []
    for key, group in sorted(coarse_groups.items(), key=lambda item: -len(item[1])):
        tally = check_class(group)
        if d == 2:
            tally["description"] = [[TYPES[k], val] for k, val in key]
        classes.append(tally)
    independent = [len(v.rows)-v.first+1-d for v in views]
    return {"starts": len(views), "descriptions": descriptions,
            "minimum_observations_beyond_interpolation": min(independent),
            "common_reference_comparison": reference_table(views, refs, d),
            "classes_if_nonconstant_polynomials_are_replaced_by_growing": classes}


def classes_across_readings(without_parents, with_parents):
    groups = defaultdict(list)
    for left, right in zip(without_parents, with_parents, strict=True):
        assert left.start == right.start
        groups[describe(left.polys, "constants_and_growing")].append(right)
    totals = Counter()
    changed = []
    for key, group in groups.items():
        tally = check_class(group)
        parent_classes = Counter(describe(v.polys, "constants_and_growing") for v in group)
        totals.update(tally["incomparable"])
        totals["pairs"] += tally["pairs"]
        if len(parent_classes) > 1:
            changed.append({"sig0_class": [[TYPES[k], val] for k, val in key],
                            "sig1_class_sizes": sorted(parent_classes.values(), reverse=True),
                            "sig1_comparisons": tally})
    return {"nestedness_tested_in": "sig1", "membership_determined_in": "sig0",
            "pairs_and_incomparable": totals, "split_classes": changed}


def parent_numbers(views):
    report = defaultdict(lambda: {
        "births": 0, "births_on_joint_polynomial_tail": 0,
        "starts": 0, "starts_with_a_late_birth": 0,
        "births_by_round": Counter(), "examples_seven_or_more": [],
    })
    for v in views:
        events = defaultdict(Counter)
        for r, counts in enumerate(v.rows, 1):
            for sig, count in counts.items():
                kind, parents, _, _ = TYPES[sig]
                if kind == "join":
                    events[parents][r] += count
        for parents, rounds in events.items():
            cell = report[parents]
            late = sum(n for r, n in rounds.items() if r >= v.first)
            cell["births"] += sum(rounds.values())
            cell["births_on_joint_polynomial_tail"] += late
            cell["starts"] += 1
            cell["starts_with_a_late_birth"] += late > 0
            cell["births_by_round"].update(rounds)
            if parents >= 7:
                cell["examples_seven_or_more"].append({
                    "start": v.start, "first_sig0_round_on_tail": v.first, "by_round": rounds,
                })
    return dict(sorted(report.items()))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prefix", type=int, help="read this many raw rows per phase")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    begin = perf_counter()
    refs = {}
    report = {
        "inputs": ["phase1_grown.jsonl.gz", "phase2_grown.jsonl.gz"],
        "prefix_per_phase": args.prefix,
        "basis": "For each kind of birth, P(r) = sum a[j] binom(r,j) in absolute round r.",
        "late_fit": "Through the final D rounds; checked backward until the preceding mismatch.",
        "descriptions": {
            "exact": "All coefficients for every kind of birth.",
            "support": "Only the kinds with a nonzero polynomial.",
            "degrees": "The degree for each kind, including degree zero.",
            "constants_and_growing": "The exact value of each constant. Every other count is called growing.",
            "constants_and_degrees": "The exact constants and the degrees of the growing counts.",
            "constants_and_leading_coefficients": "The degree and highest nonzero coefficient for each kind.",
            "all_differences": "Coefficients of orders one and higher for each kind; ignores every constant term.",
            "constants_and_all_growing_differences": "Exact constant counts and all coefficients above order zero for each growing count.",
        },
        "nested": "In each round of a suffix through the last common round, either multiset contains the other. The direction may vary. A nonempty such suffix exists exactly when the last common multisets are nested.",
        "weighting": "One per census start, one per distinct unordered pair within each class. Reference comparisons include the reference itself when present.",
        "scope": "Each phase and dimension separately. Both references have dimension two. Reference comparisons in other dimensions are descriptive only.",
    }
    for phase in (1, 2):
        stage = perf_counter()
        cells, visited = read_starts(phase, args.prefix)
        read_time = perf_counter() - stage
        if phase == 1:
            for reading in READINGS:
                all_d2 = cells[2, reading]
                refs[reading] = {
                    "one_three_place_knot": next(v for v in all_d2 if v.start["stars"] == [[0, 1, 2]]),
                    "two_three_place_knots_sharing_one_distinction": next(v for v in all_d2 if v.start["stars"] == [[0, 1, 2], [0, 3, 4]]),
                }
            report["reference_data"] = {
                reading: {name: {"start": v.start, "polynomials": counts_named(dict(v.polys)),
                                 "last_read": len(v.rows), "counts_at_last_read": counts_named(v.rows[-1])}
                          for name, v in pair.items()}
                for reading, pair in refs.items()}
        stage = perf_counter()
        tables = {f"D{d}_{reading}": summary(views, refs[reading], d)
                  for (d, reading), views in sorted(cells.items())}
        report[f"phase{phase}"] = {"raw_starts_read": visited, "cells": tables,
                                  "d2_sig1_within_sig0_classes": classes_across_readings(
                                      cells[2, "sig0"], cells[2, "sig1"]),
                                  "read_fit_seconds": round(read_time, 4),
                                  "compare_seconds": round(perf_counter()-stage, 4)}
        if phase == 1:
            report["phase1"]["d2_sig0_parent_numbers"] = parent_numbers(cells[2, "sig0"])
    report["total_seconds"] = round(perf_counter()-begin, 4)
    args.out.write_text(json.dumps(report, indent=1) + "\n")


if __name__ == "__main__":
    main()
