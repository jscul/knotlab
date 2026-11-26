"""Rebuild the connected mixed-parent example and follow the same two old parities."""
import argparse
import json
import random
import sys
from itertools import combinations
from pathlib import Path
from time import perf_counter

from built_changes import Span, advance, assemble, bits, first_funding, incidences, odd, places, read, ring

HERE = Path(__file__).resolve().parent


def source(central_loose=0, minimum=2):
    rings = ring(0, 4) + ring(4, 4)
    meetings = rings + [(0, 8), (2, 8), (4, 8)]
    live = set(range(8)) | ({8} if central_loose else set())
    demand = first_funding(9, meetings, live)
    loose = [max(minimum, demand[i]) for i in range(8)] + [central_loose]
    return assemble(9, meetings, loose), [bits(range(4)), bits(range(4, 8))], loose, meetings


def joint_readers(stage, labels, max_knots):
    """Can the pooled observations of selected holders determine a named bit?"""
    laws = [bits(row) for row in stage]
    readings = {}
    for count in range(1, max_knots + 1):
        hits = [0, 0, 0, 0]
        examples = [None, None, None, None]
        sets = 0
        for selection in combinations(range(len(laws)), count):
            observed = 0
            for k in selection:
                observed |= laws[k]
            known = Span(laws + [1 << i for i in places(observed)])
            single = [not known.remainder(f) for f in [*labels, labels[0] ^ labels[1]]]
            for i, yes in enumerate([*single, all(single)]):
                if yes:
                    hits[i] += 1
                    if examples[i] is None:
                        examples[i] = selection
            sets += 1
        readings[str(count)] = {"holder_sets_checked": sets, "counts_for_first_second_sum_both": hits,
                                 "first_examples_in_the_same_order": examples}
    return readings


def relabel_check(start, named, trials=12, seed=462739):
    """Rename all distinctions and knots, alter within-knot allocation order, and regrow."""
    rng = random.Random(seed)
    checks = []
    for _ in range(trials):
        names = sorted(incidences(start))
        rng.shuffle(names)
        renamed = []
        for knot in start:
            ordered = [names[d] for d in knot]
            rng.shuffle(ordered)
            renamed.append(tuple(ordered))
        rng.shuffle(renamed)
        labels = [bits(names[d] for d in places(f)) for f in named]
        now = tuple(renamed)
        samples = []
        for t in range(3):
            info = read(now, labels)
            observed = [info[key] for key in ("class_bits", "whole_held_rank", "named_value_rank_on_states",
                                               "named_change_rank_on_shortest_moves")]
            assert observed == ([0, 0, 2, 2] if t == 0 else [2, 2, 2, 0])
            samples.append(observed)
            if t < 2:
                now, reason = advance(now)
                assert now is not None, reason
        checks.append(samples)
    return {"seed": seed, "trials": len(checks), "columns": ["class bits", "whole-held rank", "joint value rank",
                                                              "joint change rank on shortest moves"],
            "source_through_round_two": checks}


def compare_growth(start, rounds):
    """Compare independent supports to the recorded engine, without consulting any class reader."""
    experiments = HERE.parents[2] / "experiments"
    for subdir in ("NAE-GROWTH-20261119-001B/NAE-GROWTH-20261119-001B-E001_nae",
                   "FORBIDDING-JOIN-20261120-001B/FORBIDDING-JOIN-20261120-001B-E001_free_readings"):
        sys.path.insert(0, str(experiments / subdir))
    import naelib
    from rival_growth import grow

    independent = reference = start
    checks = []
    for t in range(1, rounds + 1):
        independent, reason = advance(independent)
        reference, info = grow(reference, "parity", "ordinary", naelib)
        if independent is None:
            checks.append({"round": t, "independent": reason, "engine": info["status"]})
            assert reference is None
            break
        assert independent == reference
        checks.append({"round": t, "exact_ordered_supports_equal": True, "knots": len(independent)})
    return checks


def run(rounds, central_loose=0, minimum=2, certificate_at=(0, 1)):
    stage, named, loose, meetings = source(central_loose, minimum)
    start = stage
    rows = []
    old_read = None
    for t in range(rounds + 1):
        tick = perf_counter()
        info = read(stage, named, certificate=t in certificate_at)
        info["round"] = t
        if t == 1:
            old_holders = incidences(start)
            names = set(old_holders)
            parents = [[old_holders[x][0] for x in born if x in names] for born in stage[len(start):]]
            info["parents_at_first_round"] = parents
            info["births_with_parents_from_both_rings"] = [
                len(start) + j for j, row in enumerate(parents)
                if set(row).intersection(range(4)) and set(row).intersection(range(4, 8))
            ]
            if t in certificate_at:
                info["pooled_holder_observations"] = joint_readers(stage, named, 4)
        if old_read is not None:
            mask = bits(incidences(old_read))
            old_laws = Span(bits(row) for row in old_read)
            new_laws = Span(bits(row) for row in stage)
            old_rank = mask.bit_count() - len(old_laws)
            new_allowed = list(new_laws.orthogonal(bits(incidences(stage))))
            old_projection = Span(z & mask for z in new_allowed)
            assert len(old_projection) == old_rank
            assert all(not odd(row & z) for row in old_laws.rows.values() for z in old_projection.rows.values())
            info["projection_to_previous_allowed_rank"] = old_rank
        info["seconds"] = round(perf_counter() - tick, 5)
        rows.append(info)
        print(t, info["knots"], info["distinctions"], info["class_bits"], info["whole_held_rank"],
              info["named_value_rank_on_states"], info["named_change_rank_on_shortest_moves"],
              info["seconds"], flush=True)
        if t < rounds:
            old_read = stage
            stage, end = advance(stage)
            if stage is None:
                break
    result = {"construction": "Two four-knot rings. Knot 8 meets knots 0 and 2 of the first ring and knot 4 of the second.",
              "meetings": meetings, "loose_by_knot": loose, "stages": rows}
    if central_loose == 0 and minimum == 2 and rounds >= 2:
        result["renaming_and_allocation_control"] = relabel_check(start, named)
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rounds", type=int, required=True)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--minimum", type=int, default=2)
    parser.add_argument("--central-loose", type=int, default=0)
    parser.add_argument("--compare-growth", action="store_true")
    args = parser.parse_args()
    data = run(args.rounds, args.central_loose, args.minimum)
    if args.compare_growth:
        data["comparison_with_the_recorded_growth_engine"] = compare_growth(
            source(args.central_loose, args.minimum)[0], args.rounds)
    if args.output:
        args.output.write_text(json.dumps(data, indent=1) + "\n")
