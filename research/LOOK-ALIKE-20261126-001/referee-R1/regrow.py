#!/usr/bin/env python3
"""Reconstruct ordinary growth from shared-distinction incidence and loose counts."""

import argparse
from collections import Counter, defaultdict
from fractions import Fraction
import gzip
from itertools import combinations, permutations, product
import json
from math import comb
from pathlib import Path
import random
import resource
from time import perf_counter


ROOT = Path(__file__).resolve().parent.parent
SEED = 231976
FIVE_SAMPLE = 180
KNOT_LIMIT = 30_000
BURST_INDICES = {1177, 1771, 2083, 2683, 2902, 3101, 3156}
BOUND_DIMENSION_INDEX = 1740


def read_rows(phase):
    with gzip.open(ROOT / f"phase{phase}_grown.jsonl.gz", "rt") as infile:
        return [json.loads(line) for line in infile]


def start_incidence(stars):
    """A distinction's one holder makes it loose. Two holders meet in it."""
    holders = defaultdict(list)
    for knot, star in enumerate(stars):
        if len(star) < 3 or len(set(star)) != len(star):
            raise ValueError(f"Invalid start knot {star}")
        for distinction in star:
            holders[distinction].append(knot)

    neighbours = [set() for _ in stars]
    loose = [0] * len(stars)
    for group in holders.values():
        if len(group) == 1:
            loose[group[0]] += 1
        else:
            first, second = group
            if second in neighbours[first]:
                raise ValueError("Two start knots share more than one distinction")
            neighbours[first].add(second)
            neighbours[second].add(first)
    return neighbours, loose


def overlap_classes(size):
    """Enumerate connected starts by directly quotienting all permutations."""
    pairs = list(combinations(range(size), 2))
    weights = {pair: 1 << i for i, pair in enumerate(pairs)}
    orders = list(permutations(range(size)))
    representatives = {}
    expected = set()
    for mask in range(1 << len(pairs)):
        if mask in representatives:
            continue
        common = [pair for pair in pairs if mask & weights[pair]]
        reached = {0}
        for _ in range(size - 1):
            for left, right in common:
                if left in reached or right in reached:
                    reached.update((left, right))
        if len(reached) != size:
            continue
        for order in orders:
            renamed = sum(weights[tuple(sorted((order[a], order[b])))] for a, b in common)
            representatives.setdefault(renamed, (mask, []))[1].append(order)
        symmetry = representatives[mask][1]
        places = [sum(knot in pair for pair in common) for knot in range(size)]
        choices = [range(max(0, 3 - degree), 4) for degree in places]
        for loose in product(*choices):
            key = min(tuple(loose[knot] for knot in order) for order in symmetry)
            expected.add((mask, key))
    return pairs, representatives, expected


def census_check(data):
    results = {}
    for size in range(1, 6):
        pairs, representatives, expected = overlap_classes(size)
        observed = Counter()
        index_to_overlap = defaultdict(set)
        overlap_to_index = defaultdict(set)
        inconsistent_fields = []
        records = [row for row in data if row["n knots"] == size]
        for row in records:
            neighbours, loose = start_incidence(row["stars"])
            mask = sum(1 << i for i, (a, b) in enumerate(pairs) if b in neighbours[a])
            common, orders = representatives[mask]
            key = min(tuple(loose[knot] for knot in order) for order in orders)
            observed[common, key] += 1
            index_to_overlap[row["graph"]].add(common)
            overlap_to_index[common].add(row["graph"])
            if loose != row["loose"] or len(loose) != size:
                inconsistent_fields.append(case_id(row))
        without_loose = sorted(mask for mask, loose in expected if not any(loose))
        census_expected = {key for key in expected if any(key[1])}
        omitted = []
        for mask in without_loose:
            stars = [[] for _ in range(size)]
            shared = []
            for distinction, (first, second) in enumerate(pairs):
                if mask & (1 << distinction):
                    stars[first].append(distinction)
                    stars[second].append(distinction)
                    shared.append((first, second))
            _, end, _, _ = regrow(stars, 1)
            omitted.append({"sharing_pairs": shared, "loose_by_knot": [0] * size, "end": end})
        results[size] = {
            "overlap_classes": len(overlap_to_index),
            "expected_if_all_dead_allowed": len(expected),
            "excluded_starts_with_no_loose_distinctions": omitted,
            "census_expected_starts": len(census_expected),
            "recorded_starts": len(records),
            "missing_census_classes": sorted(census_expected - observed.keys()),
            "extra_census_classes": sorted(observed.keys() - census_expected),
            "duplicate_classes": sum(count - 1 for count in observed.values()),
            "graph_label_bijection": all(
                len(classes) == 1
                for groups in (index_to_overlap, overlap_to_index)
                for classes in groups.values()
            ),
            "inconsistent_loose_fields": inconsistent_fields,
        }
    return results


def maximal_pairwise_sets(current, available, excluded, links):
    """Yield maximal sets of three or more with every pair linked."""
    if len(current) + len(available) < 3:
        return
    if not available and not excluded:
        yield tuple(sorted(current))
        return
    pivot = max(available | excluded, key=lambda knot: len(available & links[knot]))
    for knot in sorted(available - links[pivot]):
        yield from maximal_pairwise_sets(
            (*current, knot), available & links[knot], excluded & links[knot], links
        )
        available.remove(knot)
        excluded.add(knot)


def join_plan(neighbours, active):
    """Maximal groups without one common neighbour, then uncovered pairs."""
    holders = defaultdict(set)
    for knot in active:
        for witness in neighbours[knot]:
            holders[witness].add(knot)
    links = [set() for _ in neighbours]
    for block in holders.values():
        for knot in block:
            links[knot].update(block - {knot})

    groups = []
    covered = [set() for _ in neighbours]
    for knot, linked in enumerate(links):
        later = {other for other in linked if other > knot}
        if len(later) < 2:
            continue
        earlier = linked - later
        for group in maximal_pairwise_sets((knot,), later, earlier, links):
            if set.intersection(*(neighbours[member] for member in group)):
                continue
            groups.append(group)
            for first, second in combinations(group, 2):
                covered[first].add(second)

    groups.extend(
        (knot, other)
        for knot, linked in enumerate(links)
        for other in sorted(linked - covered[knot])
        if other > knot
    )
    demand = [0] * len(neighbours)
    for group in groups:
        for knot in group:
            demand[knot] += 1
    return groups, demand


def pack(counter):
    return [[item, count] for item, count in sorted(counter.items())]


def unpack(value):
    if isinstance(value, list):
        return tuple(unpack(item) for item in value)
    return value


def birth_readings(parents, fresh, previous):
    sig0 = []
    sig1 = Counter()
    for group, count in zip(parents, fresh, strict=True):
        places = len(group) + count
        kind = "offshoot" if len(group) == 1 else "join"
        signature = (kind, len(group), count, places)
        sig0.append(signature)
        sig1[signature, tuple(sorted(previous[parent] for parent in group))] += 1
    return sig0, Counter(sig0), sig1


def ten_knot_block(parents, fresh, previous):
    members = defaultdict(list)
    for knot, group in enumerate(parents):
        for parent in group:
            if fresh[knot] > 0:
                members[parent].append(knot)
    witness, block = max(members.items(), key=lambda pair: len(pair[1]))
    common = set.intersection(*(set(parents[knot]) for knot in block))
    return block, {
        "round": 2,
        "live_knots": sum(count > 0 for count in fresh),
        "largest_common_neighbour_block": len(block),
        "largest_blocks": sum(len(group) == len(block) for group in members.values()),
        "common_neighbours_of_block": sorted(common),
        "common_neighbour_sig0": previous[witness],
        "block_members_and_fresh_counts": [(knot, fresh[knot]) for knot in block],
        "binomial_subsets": [],
    }


def mark_subsets(number, marks, parents, trace):
    from_parents = [[marks[parent] for parent in group] for group in parents]
    marks = [frozenset().union(*subsets) for subsets in from_parents]
    subset_size = number - 1
    counts = Counter(marks)
    trace["binomial_subsets"].append({
        "round": number,
        "subsets_expected": comb(10, subset_size),
        "distinct_birth_subsets": len(counts),
        "one_birth_per_subset_of_expected_size": (
            len(counts) == comb(10, subset_size)
            and all(len(subset) == subset_size and count == 1 for subset, count in counts.items())
        ),
        "each_birth_has_one_parent_per_immediate_subset": all(
            Counter(subset for subset in parents_of_birth if subset)
            == Counter(birth_mark - {knot} for knot in birth_mark)
            for parents_of_birth, birth_mark in zip(from_parents, marks, strict=True)
        ),
        "parent_counts": dict(Counter(map(len, parents))),
    })
    return marks


def regrow(stars, rounds, check_burst=False):
    neighbours, loose = start_incidence(stars)
    groups, demand = join_plan(neighbours, [i for i, count in enumerate(loose) if count > 0])
    previous = [("start", 0, 0, len(star)) for star in stars]
    observed, end = [], "rounds"
    total = len(stars)
    trace = None
    for number in range(1, rounds + 1):
        shortage = [owing > held for owing, held in zip(demand, loose, strict=True)]
        if any(shortage):
            end = f"stalls at round {number}"
            break

        parents = groups + [
            (knot,)
            for knot, (held, owing) in enumerate(zip(loose, demand, strict=True))
            for _ in range(held - owing)
        ]
        if not parents:
            end = f"closes at round {number}"
            break

        # All older loose distinctions have been taken. The sharing witnesses
        # of the new live knots are precisely their parents (Lemma R).
        groups, demand = join_plan([set(group) for group in parents], range(len(parents)))
        # Under not-all-equal no birth's constraint is implied. Every birth is live.
        loose = [max(owing, 3 - len(group), 1) for group, owing in zip(parents, demand, strict=True)]
        sig0, reading0, reading1 = birth_readings(parents, loose, previous)
        observed.append({"n": len(parents), "sig0": reading0, "sig1": reading1})

        if check_burst and number == 2:
            block, trace = ten_knot_block(parents, loose, previous)
            if len(block) == 10:
                index = {knot: label for label, knot in enumerate(block)}
                marks = [frozenset({index[knot]}) if knot in index else frozenset() for knot in range(len(parents))]
        if trace and trace["largest_common_neighbour_block"] == 10 and 3 <= number <= 11:
            marks = mark_subsets(number, marks, parents, trace)

        previous = sig0
        total += len(parents)
        if total > KNOT_LIMIT:
            end = "bound"
            break
    return observed, end, total, trace


def classify(counts, end):
    if end.startswith(("stalls", "closes")):
        return end.split()[0]
    if len(counts) < 10:
        return "unread"
    differences = counts[-8:]
    for dimension in range(1, 5):
        if len(set(differences)) == 1 and differences[0] > 0:
            return f"dim {dimension}"
        differences = [later - earlier for earlier, later in zip(differences, differences[1:])]
    ratios = [Fraction(later, earlier) for earlier, later in zip(counts[-5:], counts[-4:])]
    if min(ratios) > Fraction(105, 100) and max(ratios) - min(ratios) < Fraction(1, 100):
        return f"rate {float(ratios[-1]):.2f}"
    return "unread"


def case_id(row):
    return [row["n knots"], row["index"]]


def initial_stall_check(rows):
    by_size = defaultdict(Counter)
    discrepancies = []
    for row in rows:
        neighbours, loose = start_incidence(row["stars"])
        _, demand = join_plan(neighbours, [knot for knot, count in enumerate(loose) if count])
        short = [i for i, (owing, held) in enumerate(zip(demand, loose, strict=True)) if owing > held]
        terminal = "stalls" if short else ("can grow" if any(loose) else "closes")
        by_size[row["n knots"]][terminal] += 1
        if bool(short) != (row["end"] == "stalls at round 1") or (short and row["rows"]):
            discrepancies.append({"case": case_id(row), "loose": loose, "demand": demand, "recorded_end": row["end"]})
    return dict(by_size), discrepancies


def compare_growth(row):
    size, index = case_id(row)
    start = perf_counter()
    burst = size == 5 and index in BURST_INDICES
    observed, end, total, trace = regrow(row["stars"], 24 if size == 5 else 20, burst)
    grow_seconds = perf_counter() - start
    counts = [measured["n"] for measured in observed]
    kind = classify(counts, end)
    recorded = row["rows"]
    failures = []
    for field, actual, expected in (
        ("end", end, row["end"]), ("knots", total, row["knots"]),
        ("kind", kind, row["kind"]), ("rounds", len(counts), len(recorded)),
    ):
        if actual != expected:
            failures.append({"field": field, "reconstructed": actual, "recorded": expected})
    matches = Counter()
    first_mismatch = set()
    for number, (measured, expected) in enumerate(zip(observed, recorded), 1):
        for field in ("n", "sig0", "sig1"):
            expected_value = expected[field]
            if field != "n":
                expected_value = Counter({unpack(key): count for key, count in expected[field]})
            if measured[field] == expected_value:
                matches[field] += 1
            elif field not in first_mismatch:
                first_mismatch.add(field)
                failures.append({
                    "field": field,
                    "round": number,
                    "reconstructed": measured[field] if field == "n" else pack(measured[field]),
                    "recorded": expected[field],
                })
    result = {
        "start_knots": size,
        "census_index": index,
        "loose_by_knot": row["loose"],
        "counts_per_round": counts,
        "kind": kind,
        "end": end,
        "knots": total,
        "matches_by_field": dict(matches),
        "differences": failures,
        "growth_seconds": round(grow_seconds, 6),
    }
    if burst:
        result["round2_block_and_burst"] = trace
    return result


def select_rows(first, second, pilot):
    random_five = random.Random(SEED).sample(sorted(second, key=lambda row: row["index"]), FIVE_SAMPLE)
    controls = [row for row in second if (
        row["index"] in BURST_INDICES or row["index"] == BOUND_DIMENSION_INDEX
        or row["kind"] == "unread" or row["kind"].startswith("rate ")
    )]
    selected = {tuple(case_id(row)): row for row in first + random_five + controls}
    if not pilot:
        return random_five, controls, [selected[key] for key in sorted(selected)]
    pilot_cases = [(1, 0), (3, 15), (4, 154), (5, 0), (5, 660), (5, 661), (5, 1177), (5, 1740)]
    pilot_cases.extend(tuple(case_id(row)) for row in random_five[:4])
    recorded = {tuple(case_id(row)): row for row in first + second}
    return random_five, controls, [recorded[key] for key in pilot_cases]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pilot", action="store_true")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    if args.out.resolve().parent != Path(__file__).resolve().parent or not args.out.name.startswith("regrow"):
        parser.error("write only a regrow JSON file beside this script")
    start = perf_counter()
    first, second = read_rows(1), read_rows(2)
    read_time = perf_counter() - start
    census = census_check(first + second)
    initial, initial_disagreements = initial_stall_check(first + second)
    census_and_stall_time = perf_counter() - start - read_time

    sample, controls, selected = select_rows(first, second, args.pilot)
    outcomes = [compare_growth(row) for row in selected]
    field_matches = Counter()
    for outcome in outcomes:
        field_matches.update(outcome["matches_by_field"])
    results = {
        "configuration": {
            "pilot": args.pilot,
            "growth": "ordinary count with not-all-equal and nothing taken",
            "memory_ceiling_kib": resource.getrlimit(resource.RLIMIT_AS)[0] // 1024,
            "phase_rounds": {1: 20, 2: 24},
            "knot_limit_after_complete_round": KNOT_LIMIT,
            "phase2_sample_seed": SEED,
            "phase2_uniform_sample_size": FIVE_SAMPLE,
            "phase2_uniform_sample_indices": sorted(row["index"] for row in sample),
            "phase2_controls": [case_id(row) for row in controls],
        },
        "census_independent_reconstruction": census,
        "round1_stall_check_by_size": initial,
        "round1_stall_discrepancies": initial_disagreements,
        "regrowth": {
            "starts_checked_by_size": dict(Counter(result["start_knots"] for result in outcomes)),
            "recorded_starts_without_full_regrowth": {
                1: len(first) - sum(row["start_knots"] < 5 for row in outcomes),
                2: len(second) - sum(row["start_knots"] == 5 for row in outcomes),
            },
            "kinds_by_size": [
                {"start_knots": size, "counts": dict(Counter(
                    row["kind"] for row in outcomes if row["start_knots"] == size
                ))}
                for size in range(1, 6)
            ],
            "recorded_rounds_compared": sum(len(row["rows"]) for row in selected),
            "rounds_matching": dict(field_matches),
            "starts_with_differences": sum(bool(row["differences"]) for row in outcomes),
            "elapsed_seconds": round(perf_counter() - start, 3),
            "read_seconds": round(read_time, 3),
            "census_and_round1_check_seconds": round(census_and_stall_time, 3),
            "growth_seconds": round(sum(row["growth_seconds"] for row in outcomes), 3),
            "peak_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        },
        "recorded_phase2_complete_rounds_crossing_the_knot_limit": dict(Counter(
            (row["kind"] for row in second if row["end"] == "bound")
        )),
        "cases": outcomes,
    }
    args.out.write_text(json.dumps(results, indent=2) + "\n")
    print(json.dumps(results["regrowth"], sort_keys=True))


if __name__ == "__main__":
    main()
