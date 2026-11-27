"""Reproduce a bounded part of the source census and extend selected cores.

Run the exact configuration on the pilot prefixes first:
    .venv/bin/python -B research/CAPPED-CORES-20261127-001/referee-R1/redraw.py --pilot
    .venv/bin/python -B research/CAPPED-CORES-20261127-001/referee-R1/redraw.py
"""

import argparse
from collections import Counter, defaultdict
from heapq import heapify, heappop, heappush
from itertools import combinations
import json
from math import exp
from pathlib import Path
from random import Random
import resource
from time import perf_counter

from redraw_core import brute_round, first_ranks, parent_incidence_round, pieces, progress


SEED = 2026112701
MEMORY_BYTES = 2_000_000_000
SOURCE_LIMITS = {"node_cap": 5_000, "pair_cap": 250_000, "last_rank": 25}
EXTENSION_LIMITS = {"node_cap": 80_000, "pair_cap": 1_250_000, "last_rank": 32}
SOURCE_DRAWS = 3_000


def tree_plus(n, rng):
    code = [rng.randrange(n) for _ in range(n - 2)]
    remaining = Counter(code)
    ready = [knot for knot in range(n) if not remaining[knot]]
    heapify(ready)
    shares = []
    for knot in code:
        shares.append(tuple(sorted((heappop(ready), knot))))
        remaining[knot] -= 1
        if not remaining[knot]:
            heappush(ready, knot)
    shares.append(tuple(sorted(ready)))

    unshared = sorted(set(combinations(range(n), 2)) - set(shares))
    product = rng.random()
    extras = 0
    while product > exp(-1):
        extras += 1
        product *= rng.random()
    shares.extend(rng.sample(unshared, min(extras, len(unshared))))

    shared_counts = Counter(knot for pair in shares for knot in pair)
    temporary_sizes = [shared_counts[knot] + 1 for knot in range(n)]
    _, groups, _, _ = first_ranks(temporary_sizes, shares)
    demand = Counter(knot for family in groups for knot in family)
    sizes = [max(3, shared_counts[knot] + demand[knot]) for knot in range(n)]
    return sizes, shares


def grow(n, rng):
    while True:
        sizes = [rng.choice((3, 4, 5))]
        available = sizes.copy()
        shares = []
        for new in range(1, n):
            sizes.append(rng.choice((3, 4, 5)))
            if not any(available):
                break
            available.append(sizes[-1])
            count = 1 + (rng.random() < 1 / 3)
            eligible = [knot for knot in range(new) if available[knot]]
            for _ in range(min(count, len(eligible))):
                chosen = rng.choices(eligible, [available[knot] for knot in eligible])[0]
                shares.append((chosen, new))
                available[new] -= 1
                available[chosen] -= 1
                eligible.remove(chosen)
        else:
            return sizes, shares


def canonical_input(sizes, shared_distinctions):
    """Exact canonical form under renaming knots and distinctions."""
    count = len(sizes)
    matrix = [[0] * count for _ in sizes]
    for a, b in shared_distinctions:
        matrix[a][b] += 1
        matrix[b][a] += 1
    by_size = defaultdict(list)
    for knot, size in enumerate(sizes):
        by_size[size].append(knot)

    def refine(partition):
        while True:
            refined = []
            for cell in partition:
                by_neighbors = defaultdict(list)
                for knot in cell:
                    profile = tuple(tuple(sorted(matrix[knot][other] for other in group))
                                    for group in partition)
                    by_neighbors[profile].append(knot)
                refined.extend(tuple(by_neighbors[key]) for key in sorted(by_neighbors))
            if len(refined) == len(partition):
                return refined
            partition = refined

    def encode(partition):
        order = [cell[0] for cell in partition]
        places = tuple(sizes[knot] for knot in order)
        shares = tuple(matrix[a][b] for a, b in combinations(order, 2))
        return places, shares

    def search(partition):
        partition = refine(partition)
        index = next((i for i, cell in enumerate(partition) if len(cell) > 1), None)
        if index is None:
            return encode(partition)
        group = partition[index]
        possibilities = []
        used = []
        for knot in group:
            if any(all(matrix[knot][v] == matrix[other][v]
                       for v in range(count) if v != knot and v != other)
                   for other in used):
                continue
            used.append(knot)
            split = [(knot,), tuple(other for other in group if other != knot)]
            possibilities.append(search(partition[:index] + split + partition[index + 1:]))
        return min(possibilities)

    return search([tuple(by_size[size]) for size in sorted(by_size)])


def render_canonical(key):
    sizes, entries = key
    return {
        "knot_places": sizes,
        "shared_distinctions": [pair for pair, multiplicity in
                                zip(combinations(range(len(sizes)), 2), entries)
                                for _ in range(multiplicity)],
    }


def numbered_distinctions(sizes, shared):
    held = [[] for size in sizes]
    for distinction, (a, b) in enumerate(shared):
        held[a].append(distinction)
        held[b].append(distinction)
    next_distinction = len(shared)
    for distinctions, size in zip(held, sizes):
        missing = size - len(distinctions)
        distinctions.extend(range(next_distinction, next_distinction + missing))
        next_distinction += missing
    return held


def controls():
    rng = Random(271)
    for count in range(1, 8):
        for _ in range(24):
            incidence = {knot: {parent for parent in range(5) if rng.random() < 0.4}
                         for knot in range(count)}
            calculated, _, _ = parent_incidence_round(incidence)
            if calculated != brute_round(incidence):
                raise RuntimeError(f"round rule disagreed with exhaustive subsets: {incidence}")
    star = progress(range(1), ((0,),) * 4, **EXTENSION_LIMITS)
    if star["rank_widths"] != [1, 4, 6, 4, 1, 0]:
        raise RuntimeError("common-parent control failed")
    for sampler in (tree_plus, grow):
        for n in (7, 11):
            for _ in range(3):
                sizes, shares = sampler(n, rng)
                inverse = [(n - 1 - b, n - 1 - a) for a, b in reversed(shares)]
                if canonical_input(sizes, shares) != canonical_input(sizes[::-1], inverse):
                    raise RuntimeError("renaming changed the canonical input")
    return {"exhaustive_subset_comparisons": 168, "common_parent_m4": star["rank_widths"],
            "input_renaming_comparisons": 12}


def find_source_cap(piece_inputs):
    for index, (rank_zero, rank_one) in enumerate(piece_inputs):
        result = progress(rank_zero, rank_one, **SOURCE_LIMITS)
        if result["stop"] == "cap":
            return "capped", index, result
        if result["stop"] == "rank horizon":
            return "rank horizon", index, result
    return "empty rank", None, None


def extension_record(rank_zero, rank_one):
    result = progress(rank_zero, rank_one, **EXTENSION_LIMITS)
    widths = result["rank_widths"]
    result["last_width_ratios"] = [
        [after, before] for before, after in zip(widths[-6:-1], widths[-5:]) if before
    ] if len(widths) >= 6 else [[after, before] for before, after in zip(widths, widths[1:])
                              if before]
    result["ranks_with_equal_consecutive_incidence_dimensions"] = [
        rank for rank in range(1, len(widths) - 1)
        if widths[rank - 1] == widths[rank] == widths[rank + 1]
    ]
    if result["stop"] == "empty rank":
        result["classification"] = "finished by enumeration"
    elif result["subset_pattern"]:
        result["classification"] = "common-parent subset pattern"
    else:
        result["classification"] = "unresolved beyond the exact rank prefix"
    return result


def cell(weighting, n, pilot):
    started = perf_counter()
    rng = Random(SEED)
    sampler = tree_plus if weighting == "tree+" else grow
    draw_limit = (36 if weighting == "tree+" else 160) if pilot else SOURCE_DRAWS
    retained = []
    status_by_input = {}
    statuses = Counter()
    extension_seconds = 0
    for draw in range(draw_limit):
        sizes, shares = sampler(n, rng)
        loose, groups, offshoots, accepted = first_ranks(sizes, shares)
        if not accepted:
            statuses["not accepted"] += 1
            continue
        key = canonical_input(sizes, shares)
        is_new = key not in status_by_input
        if is_new:
            piece_inputs = list(pieces(loose, groups, offshoots))
            status, piece_index, source_trace = find_source_cap(piece_inputs)
            status_by_input[key] = status
        statuses[status_by_input[key]] += 1
        if is_new and status == "capped":
            row = {
                "weighting": weighting,
                "knot_count": n,
                "first_draw_zero_based": draw,
                "first_draw_one_based": draw + 1,
                "drawn_start": {"knot_places": sizes, "shared_distinctions": shares,
                                "distinctions_by_knot": numbered_distinctions(sizes, shares)},
                "canonical_start": render_canonical(key),
                "loose_distinction_counts": loose,
                "round_one_groups": groups,
                "offshoot_counts": offshoots,
                "capped_piece_zero_based": piece_index,
                "source_cap_trace": source_trace,
            }
            print(json.dumps({field: row[field] for field in
                              ("weighting", "knot_count", "first_draw_zero_based", "drawn_start",
                               "round_one_groups", "offshoot_counts")}), flush=True)
            extension_start = perf_counter()
            row["pieces"] = [
                {"rank_zero_knots": rank_zero, "rank_one_parent_sets": rank_one,
                 **extension_record(rank_zero, rank_one)}
                for rank_zero, rank_one in piece_inputs
            ]
            extension_seconds += perf_counter() - extension_start
            retained.append(row)
            if weighting == "tree+" and len(retained) == (1 if pilot else 2):
                break
    examined = draw + 1
    return {"weighting": weighting, "knot_count": n, "source_draws_examined": examined,
            "source_draws_not_run": SOURCE_DRAWS - examined, "draw_count_by_census_status": statuses,
            "distinct_accepted_count_by_census_status": Counter(status_by_input.values()),
            "retained_distinct_capped_starts": retained, "wall_seconds": perf_counter() - started,
            "extension_seconds": extension_seconds}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pilot", action="store_true")
    arguments = parser.parse_args()
    resource.setrlimit(resource.RLIMIT_AS, (MEMORY_BYTES, MEMORY_BYTES))
    started = perf_counter()
    checked = controls()
    cells = [cell("tree+", n, arguments.pilot) for n in range(7, 12)]
    cells.append(cell("grow", 10, arguments.pilot))
    measurement = {
        "mode": "pilot" if arguments.pilot else "redraw",
        "source": "TWO-EXCEPTIONS-20261127-001 counts, with the WEIGHTINGS-20261119-001B processes",
        "seed_reset_for_each_weighting_and_knot_count": SEED,
        "selection": "retain the first distinct capped starts, in source draw order",
        "source_limits": SOURCE_LIMITS,
        "extension_limits": EXTENSION_LIMITS,
        "limit_notes": [
            "Node cap per piece includes all completed ranks, including rank zero.",
            "The round's maximal-family guard also counts singleton families and families "
            "with common parents. It uses the remaining node budget.",
            "The pair guard counts pair occurrences over parents, with multiplicity.",
            "Rank widths count distinct births by parent set, with rank zero first. "
            "Offshoots at rank one are separate even if their parents agree.",
            "A finite prefix and its ratios give no conclusion about unbounded growth.",
        ],
        "process_count": 1,
        "memory_limit_bytes": MEMORY_BYTES,
        "peak_memory_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        "wall_seconds": perf_counter() - started,
        "controls": checked,
        "cells": cells,
    }
    filename = "redraw_pilot.json" if arguments.pilot else "redraw.json"
    Path(__file__).with_name(filename).write_text(json.dumps(measurement, indent=2) + "\n")


if __name__ == "__main__":
    main()
