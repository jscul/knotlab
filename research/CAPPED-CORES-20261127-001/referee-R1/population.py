"""Compare two rules for which drawn starts cross a count limit.

The first rule stops at a piece still open at rank 25. The second keeps
looking for a count limit among later pieces. A rank stop can only mask a
count stop in a start with more than one piece.
"""

import argparse
from functools import lru_cache
import json
from pathlib import Path
from random import Random
import resource
from time import perf_counter, process_time

from redraw import SEED, SOURCE_DRAWS, SOURCE_LIMITS, canonical_input, pieces, progress, tree_plus
from redraw_core import first_ranks


MEMORY_LIMIT = 1_500_000_000
HERE = Path(__file__).resolve().parent


def archived_prefix(n):
    path = HERE.parent / "runs" / f"tree+_{n}.jsonl"
    rows = [json.loads(line) for line in path.read_text().splitlines()]
    return [row["draw"] for row in rows[:-1]], rows[-1]


def archived_count_difference(n, later_piece_summary):
    path = HERE.parents[1] / "TWO-EXCEPTIONS-20261127-001" / "counts" / f"tree+_{n}.json"
    earlier = json.loads(path.read_text())
    return [
        sum(later_piece_summary["capped distinct starts"].values())
        - earlier["distinct accepted starts"]["core over the cap"],
        sum(later_piece_summary["capped accepted draws with repeats"].values())
        - earlier["accepted draws with repeats"]["core over the cap"],
    ]


@lru_cache(maxsize=8192)
def piece_result(knot_count, rank_one):
    return progress(range(knot_count), rank_one, **SOURCE_LIMITS)


def trace_piece(piece):
    knots, rank_one = piece
    renaming = {knot: local for local, knot in enumerate(knots)}
    local_rank_one = tuple(sorted(tuple(renaming[knot] for knot in family) for family in rank_one))
    trace = piece_result(len(knots), local_rank_one)
    return record_piece(piece, trace)


def record_piece(piece, trace):
    knots, rank_one = piece
    return {
        "rank_zero_knots": knots,
        "rank_one_parent_sets": rank_one,
        "stop": trace["stop"],
        "rank_widths": trace["rank_widths"],
        "completed_node_count": trace["completed_node_count"],
        "criterion": trace.get("criterion"),
        "lower_bound": trace.get("lower_bound"),
        "next_rank": trace.get("next_rank"),
        "highest_parent_share_occurrences_on_completed_transitions": max(
            (round_["parent_share_occurrences"] for round_ in trace["round_transitions"]),
            default=0,
        ),
    }


def raise_pair_guard(witness):
    later_piece = witness["piece_traces"][-1]
    limits = {**SOURCE_LIMITS, "pair_cap": 13_200_000}
    piece = later_piece["rank_zero_knots"], later_piece["rank_one_parent_sets"]
    return {"draws_zero_based": witness["draws_zero_based"], "limits": limits,
            "later_piece": record_piece(piece, progress(*piece, **limits))}


def compare_cell(n, draws):
    rng = Random(SEED)
    archived, archived_summary = archived_prefix(n)
    old_prefix = []
    new_prefix = []
    admitted = 0
    new_inputs = set()
    prefix_inputs = set()
    prefix_draws_with_repeats = 0
    multi_piece_inputs = 0
    masked = {}
    for draw in range(draws):
        sizes, shares = tree_plus(n, rng)
        loose, groups, offshoots, accepted = first_ranks(sizes, shares)
        if not accepted:
            continue
        admitted += 1
        key = canonical_input(sizes, shares)
        if key in new_inputs:
            if key in prefix_inputs:
                prefix_draws_with_repeats += 1
            if key in masked:
                masked[key]["draws_zero_based"].append(draw)
            continue
        new_inputs.add(key)
        piece_inputs = list(pieces(loose, groups, offshoots))
        if len(piece_inputs) > 1:
            multi_piece_inputs += 1
        if len(piece_inputs) == 1 and draw > archived[-1]:
            continue
        traces = []
        first_stop = None
        for index, piece in enumerate(piece_inputs):
            if draw > archived[-1] and index == len(piece_inputs) - 1 and first_stop is None:
                break
            row = trace_piece(piece)
            traces.append(row)
            if row["stop"] == "empty rank":
                continue
            if first_stop is None:
                first_stop = row["stop"]
            if row["stop"] != "cap":
                continue
            if draw <= archived[-1]:
                new_prefix.append(draw)
                prefix_inputs.add(key)
                prefix_draws_with_repeats += 1
                if first_stop == "cap":
                    old_prefix.append(draw)
            if first_stop == "rank horizon":
                masked[key] = {"draws_zero_based": [draw], "knot_places": sizes,
                               "shared_distinctions": shares, "piece_traces": traces}
            break
    tested_prefix = [draw for draw in archived if draw < draws]
    count = len(masked)
    repeated_count = sum(len(witness["draws_zero_based"]) for witness in masked.values())
    difference = archived_count_difference(n, archived_summary)
    return {
        "knots": n,
        "draws": draws,
        "admitted_draws": admitted,
        "distinct_admitted_starts": len(new_inputs),
        "distinct_starts_with_multiple_pieces": multi_piece_inputs,
        "archived_prefix_zero_based": tested_prefix,
        "stop_at_first_unfinished_piece_prefix": old_prefix,
        "test_later_pieces_at_rank_horizon_prefix": new_prefix,
        "later_piece_test_reproduces_prefix": new_prefix == tested_prefix,
        "prefix_same_under_both_policies": old_prefix == new_prefix,
        "prefix_draws_with_repeats": prefix_draws_with_repeats,
        "prefix_draws_with_repeats_reproduced": draws == SOURCE_DRAWS and
        prefix_draws_with_repeats == archived_summary["capped accepted draws with repeats"]["unresolved"],
        "archived_later_piece_test_totals": archived_summary,
        "archived_differences_distinct_and_with_repeats": difference,
        "additional_distinct_capped_starts": count,
        "additional_capped_draws_with_repeats": repeated_count,
        "differences_reproduced_on_all_draws": draws == SOURCE_DRAWS
        and [count, repeated_count] == difference,
        "later_piece_cap_witnesses": list(masked.values()),
        "raised_pair_guard_checks": [raise_pair_guard(row) for row in masked.values()
                                    if row["draws_zero_based"] == [734] and n == 11],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--draws", type=int, default=SOURCE_DRAWS)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    resource.setrlimit(resource.RLIMIT_AS, (MEMORY_LIMIT, MEMORY_LIMIT))
    wall_start, cpu_start = perf_counter(), process_time()
    cells = [compare_cell(n, args.draws) for n in (10, 11)]
    result = {
        "weighting": "tree+", "seed": SEED, "limits": SOURCE_LIMITS,
        "comparison": "Full draw stream for masked count limits. For the sampled prefix, compare both rules on all distinct starts through the last archived certificate. After that, only starts with multiple pieces require core checks.",
        "input_identity": "Exact up to renaming. First draw determines piece order and its classification is cached for repeats.",
        "cpu_seconds": process_time() - cpu_start, "wall_seconds": perf_counter() - wall_start,
        "peak_resident_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        "memory_limit_bytes": MEMORY_LIMIT, "cells": cells,
    }
    if args.output:
        args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(f"{result['cpu_seconds']:.2f} CPU seconds, {result['peak_resident_kib']} KiB peak RSS")
    for cell in cells:
        print({key: value for key, value in cell.items() if key in (
            "knots", "draws", "distinct_admitted_starts", "distinct_starts_with_multiple_pieces",
            "later_piece_test_reproduces_prefix", "additional_distinct_capped_starts",
            "additional_capped_draws_with_repeats")})
        print([witness["draws_zero_based"] for witness in cell["later_piece_cap_witnesses"]])


if __name__ == "__main__":
    main()
