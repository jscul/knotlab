"""Exact whole-stage locality and law deletions for the chains beyond the checked prefix."""

import argparse
from collections import Counter, defaultdict
from concurrent.futures import ProcessPoolExecutor
from contextlib import ExitStack
import gzip
from itertools import chain as concatenate
import json
from multiprocessing import get_context
from pathlib import Path
import resource
from time import perf_counter

from failure_rule import ChainTables, ROLES, chain_names, counted, off_chain
from other_bonds_controls import SYSTEMS, truth_table
from other_bonds_determination import Stage as Reducer, carried_pairs
from other_bonds_paired import BASE_SEED, SAMPLE_COUNT, Source, ThirdIndices, examine_pair, state_matrix, witness_columns
from stage_readings import mapped_carriers, stage_solver


HERE = Path(__file__).resolve().parent
EXPECTED_WORDS = [format(word, "03b") for word in range(7)]
RESULTS = ("original_step", "arbitrary_bonds_all_roles", "strict_all_roles", "strict_any_role")


def json_lines(path):
    with gzip.open(path, "rt", encoding="utf-8") as source:
        yield from map(json.loads, source)


def stage_id(row):
    return row["start"], row["round"]


def normalized(pair):
    return tuple(sorted(tuple(sorted(carrier)) for carrier in pair))


def compact_reduction(result):
    return {name: result[name] for name in (
        "mandatory", "candidate_groups", "two_touching_groups", "two_touching_groups_left_to_examine",
        "three_touching_group_covers", "determining_three_touching_bonds",
    )}


def classification(lower_exact, lower_unread, upper, deletions, defining, determines):
    upper_ok = [image == EXPECTED_WORDS for image in upper]
    law_needed = [all(row[role] for row in deletions) for role in range(3)]
    upper_unread = [not any(determines[pair][pair == role] for pair in range(3)) for role in range(3)]
    original_roles = [lower_exact and lower_unread and exact for exact in upper_ok]
    broad_roles = [original_roles[i] and defining[i] and upper_unread[i] for i in range(3)]
    strict_roles = [broad_roles[i] and law_needed[i] for i in range(3)]
    return {
        "four_exact_lower_clauses": lower_exact,
        "lower_unread_at_source_knots": lower_unread,
        "upper_images": upper,
        "role_passes_defining_lower_bond_locality": defining,
        "upper_111_restored_by_single_law_deletion": deletions,
        "role_needs_every_single_chain_law": law_needed,
        "role_passes_arbitrary_lower_bond_locality": upper_unread,
        "strict_roles": strict_roles,
        "original_step": all(original_roles),
        "every_law_needed_for_all_three_roles": all(law_needed),
        "arbitrary_bonds_all_roles": all(broad_roles),
        "strict_all_roles": all(strict_roles),
        "strict_any_role": any(strict_roles),
    }


def completed_prefix():
    """Read the independent checks completed for the originally checked chains."""
    paired = {}
    for stage in json_lines(HERE / "other_bonds_paired_all.jsonl.gz"):
        paired[stage_id(stage)] = {
            normalized(row["pair"]): {"counts": row["counts"], "bonds": row["bonds"]}
            for row in stage["fixed_pairs"]
        }
    reduced = defaultdict(dict)
    function_checks = 0
    for row in json_lines(HERE / "other_bonds_determination_counts.jsonl.gz"):
        key = normalized(row["pair"]), row["mode"] == "both"
        result = compact_reduction(row)
        assert set(result["mandatory"]) == set().union(*map(set, key[0]))
        assert not result["two_touching_groups_left_to_examine"] and not result["determining_three_touching_bonds"]
        if key in reduced[stage_id(row)]:
            assert reduced[stage_id(row)][key] == result
        reduced[stage_id(row)][key] = result
        function_checks += 1
    prefix = defaultdict(list)
    for row in json_lines(HERE / "stage_readings.jsonl.gz"):
        index = stage_id(row)
        carriers = row["carriers"]
        fixed = [bool(paired[index][normalized(carriers[i:i+2])]["bonds"]) for i in (0, 2, 4)]
        words = [image["words"] for image in row["upper_images"]]
        defining = [all(entry["mixed_fixes_by_upper_pair_and_function"][pair][pair != role] > 0
                        for entry in row["defining_lower_triples"] for pair in range(3)) for role in range(3)]
        fields = row["frozen_fields"]
        flags = classification(fields["lower triples miss exactly their triple"], fields["no lower reading read at a knot"],
                               words, row["by_single_chain_law_deletion_upper_111_restored"], defining, [(v, v) for v in fixed])
        assert flags["original_step"] == fields["a step"]
        assert flags["every_law_needed_for_all_three_roles"] == fields["every chain law needed"]
        prefix[index].append({"chain_rank": row["chain_number"], **flags})
    assert function_checks == 6 * sum(map(len, prefix.values()))
    reported = json.loads((HERE / "other_bonds_paired_all.json").read_text())
    assert sum(row["strict_all_roles"] for stage in prefix.values() for row in stage) == reported[
        "chain_and_stage_counts"]["frozen_positives_needing_all_laws_surviving_fixed_pair_test"]
    return prefix, paired, reduced


class Locality:
    """Stage-scoped caches for fixed-pair testing and complete reduction by function."""

    def __init__(self, supports, choices, seed, paired, reduced):
        self.supports = supports
        self.source = Source(supports)
        self.reducer = Reducer(supports)
        self.choices = choices
        self.seed = seed
        self.samples = None
        self.fixed_cache = paired.copy()
        self.reduced_archive = reduced
        self.functions = {}
        self.memo_counts = Counter()
        self.work_seconds = Counter()

    def close(self):
        self.source.solver.delete()
        self.reducer.solver.delete()

    def reset_solvers(self):
        unread = self.source.nonlocal_cache
        self.close()
        self.source = Source(self.supports)
        self.source.nonlocal_cache = unread
        self.reducer = Reducer(self.supports)
        self.memo_counts["solver_restarts"] += 1

    def fixed(self, pair):
        if pair not in self.fixed_cache:
            tick = perf_counter()
            if self.samples is None:
                columns = witness_columns(self.source.supports, self.source.model, SAMPLE_COUNT, self.seed)
                self.samples = columns, state_matrix(columns, SAMPLE_COUNT)
            counts, bonds = examine_pair(self.source, pair, *self.samples, SAMPLE_COUNT, self.choices)
            self.fixed_cache[pair] = {"counts": counts, "bonds": bonds}
            self.memo_counts["new_exact_fixed_pair_checks"] += 1
            self.work_seconds["fixed_pair"] += perf_counter() - tick
        else:
            self.memo_counts["reused_exact_fixed_pair_checks"] += 1
        return self.fixed_cache[pair]["bonds"]

    def function(self, pair, both):
        pair = normalized(pair)
        key = pair, both
        if key in self.functions:
            self.memo_counts["reused_reducer_checks_within_omitted_stage"] += 1
            return self.functions[key]
        if key in self.reduced_archive:
            reduced = self.reduced_archive[key]
            self.memo_counts["reused_reducer_checks_from_archived_prefix"] += 1
        else:
            tick = perf_counter()
            reduced = compact_reduction(self.reducer.reducer(pair, both))
            self.memo_counts["new_exact_reducer_checks"] += 1
            self.work_seconds["reducer"] += perf_counter() - tick
        fixed = self.fixed(pair)
        other_bonds = []
        required = [self.reducer.upper_literal(pair, both, 0), -self.reducer.upper_literal(pair, both, 1)]
        for groups in reduced["two_touching_groups_left_to_examine"]:
            a, b = normalized(groups)
            for bond in self.fixed((a, b)):
                triple = (a, b, tuple(bond["third"]))
                if self.reducer.determining(triple, required):
                    other_bonds.append({"groups": triple, "missing_words": bond["missing_words"]})
        result = {"pair": pair, "both": both, "fixed_pair_bonds": fixed, **reduced,
                  "determining_bonds_with_two_other_touching_carriers": other_bonds}
        result["determining_bond_exists"] = bool(fixed or other_bonds or reduced["determining_three_touching_bonds"])
        self.functions[key] = result
        return result


def direct_locality_control(choices):
    """Compare complete arbitrary-bond verdicts on a small exhaustively enumerated system."""
    supports = SYSTEMS[2]
    _, _, _, equal, _, _, bonds = truth_table(supports)
    cases = (
        (((0, 1, 3), (2, 4, 5)), False),
        (((0, 1, 5), (3, 4, 7)), True),
        (((0, 1, 6), (3, 5)), True),
    )
    locality = Locality(supports, choices, BASE_SEED, {}, {})
    checks = []
    try:
        for pair, both in cases:
            left, right = map(equal.__getitem__, pair)
            value = left & right if both else left | right
            actual = {tuple(sorted(groups)) for groups, cells in bonds if all(not (c & value and c & ~value) for c in cells)}
            found = locality.function(pair, both)
            observed = {tuple(sorted((*pair, tuple(row["third"])))) for row in found["fixed_pair_bonds"]}
            for label in ("determining_three_touching_bonds", "determining_bonds_with_two_other_touching_carriers"):
                observed.update(tuple(sorted(row["groups"])) for row in found[label])
            assert actual == observed
            checks.append({"pair": pair, "both": both, "direct_determining_bonds": len(actual),
                           "canonical_two_carrier_bonds": len(found["fixed_pair_bonds"]),
                           "noncanonical_two_carrier_bonds": len(found["determining_bonds_with_two_other_touching_carriers"]),
                           "three_touching_carrier_bonds": len(found["determining_three_touching_bonds"])})
    finally:
        locality.close()
    assert any(check["noncanonical_two_carrier_bonds"] for check in checks)
    assert any(check["three_touching_carrier_bonds"] for check in checks)
    assert any(not check["direct_determining_bonds"] for check in checks)
    return checks


def analyze_stage(row, tables, choices, prefix, paired, reduced, reset_every):
    begin = perf_counter()
    start, round_ = stage_id(row)
    supports = row["supports"]
    n = 1 + max(map(max, supports))
    number_checked = len(prefix)
    assert [item["chain_rank"] for item in prefix] == list(range(1, number_checked + 1))
    locality = Locality(supports, choices, BASE_SEED + 11 * start + round_, paired, reduced)
    functions = {}
    omitted = []
    try:
        with ExitStack() as stack:
            exact_stage = None
            for rank, chain in enumerate(row["all_chains"][number_checked:], number_checked + 1):
                if reset_every and rank > number_checked + 1 and (rank - number_checked - 1) % reset_every == 0:
                    locality.reset_solvers()
                labels = chain_names(supports, chain)
                outside = off_chain(supports, chain, labels)
                signature = tuple(signed for signed, _ in outside)
                result = tables.results(signature)
                flags = counted(result)
                lower_unread = flags["lower_readings_nonlocal_to_every_raw_knot_certified"]
                deletions = [[role not in failed for role in ROLES]
                             for failed in result["roles_still_missing_111_after_deleting_chain_law"]]
                # Recover any failure of the internal-flip certificate by an exact raw check.
                small_control = (start, round_, rank) in {(87, 2, 4), (87, 2, 19)}
                if not lower_unread or small_control:
                    if exact_stage is None:
                        exact_stage = stack.enter_context(stage_solver(supports))
                    carriers = mapped_carriers(supports, chain)
                    readings = tuple(exact_stage.agreement(carrier) for carrier in carriers)
                    witness_words = exact_stage.observed(readings)
                    matches = not exact_stage.read_at_any_knot(readings, witness_words)["determining_knot_and_reading"]
                    if small_control:
                        targets = exact_stage.upper_111(readings)
                        assert matches == lower_unread
                        assert deletions == [[exact_stage.solve([p], omit=(i,)) for p in targets] for i in chain]
                        assert len(witness_words) == result["six_word_count"]
                    lower_unread = matches
                pairs = carried_pairs(supports, chain)
                by_pair = [[locality.function(pair, both) for both in (False, True)] for pair in pairs]
                indices = []
                for pair, function_results in zip(pairs, by_pair, strict=True):
                    key = normalized(pair)
                    if key not in functions:
                        functions[key] = (len(functions), function_results)
                    indices.append(functions[key][0])
                defining = [not any(role == j for j, _, _ in result["upper_reading_read_at_a_defining_lower_bond"])
                            for role in range(3)]
                determines = [[record["determining_bond_exists"] for record in pair] for pair in by_pair]
                verdict = classification(flags["four_exact_lower_clauses"], lower_unread, result["upper_words"],
                                         deletions, defining, determines)
                omitted.append({"chain_rank": rank, "chain_law_indices": chain, "upper_pair_indices": indices,
                                "exact_raw_lower_and_deletion_control": small_control, **verdict})
    finally:
        locality.close()
    return {"start": start, "round": round_, "distinctions": n, "source_laws": len(supports),
            "checked_prefix": prefix, "additional_chains": omitted,
            "upper_pairs": [pair for _, pair in functions.values()], "cache_counts": locality.memo_counts,
            "work_seconds": {k: round(seconds, 6) for k, seconds in locality.work_seconds.items()},
            "elapsed_seconds": round(perf_counter() - begin, 6)}


def stratum(row):
    n = 1 + max(map(max, row["supports"]))
    return row["round"], n // 50, omitted_count(row) >= 30


def omitted_count(row):
    return len(row["all_chains"]) - len(row["checked_chains"])


def timing_slice(rows):
    groups = defaultdict(list)
    for row in rows:
        groups[stratum(row)].append(row)
    chosen = {(87, 6), (1446, 4), (3609, 5)}
    for group in groups.values():
        order = sorted(group, key=lambda row: (omitted_count(row), stage_id(row)))
        chosen.add(stage_id(order[len(order) // 2]))
    chosen.add(stage_id(max(rows, key=lambda row: (max(map(max, row["supports"])), omitted_count(row)))))
    return [row for row in rows if stage_id(row) in chosen]


def initialize_worker(choices, prefix, paired, reduced, reset_every):
    global worker_inputs
    worker_inputs = ChainTables(), choices, prefix, paired, reduced, reset_every


def analyze_worker(row):
    tables, choices, prefix, paired, reduced, reset_every = worker_inputs
    key = stage_id(row)
    return analyze_stage(row, tables, choices, prefix[key], paired[key], reduced[key], reset_every)


def completed_omitted_stages(paths, roster):
    finished = {}
    for path in paths:
        for stage in json_lines(path):
            key = stage_id(stage)
            expected = roster[key]["all_chains"]
            checked = len(roster[key]["checked_chains"])
            actual = [r["chain_law_indices"] for r in stage["additional_chains"]]
            assert actual == expected[checked:checked + len(actual)]
            if actual != expected[checked:]:
                continue
            assert [r["chain_rank"] for r in stage["additional_chains"]] == list(range(checked + 1, len(expected) + 1))
            if key in finished:
                assert finished[key]["additional_chains"] == stage["additional_chains"]
            finished[key] = stage
    return finished


def aggregate(outcomes):
    counts = defaultdict(Counter)
    by_round = defaultdict(lambda: defaultdict(Counter))
    rank_minima = defaultdict(dict)
    cache_counts = Counter()
    function_counts = Counter()
    for stage in outcomes:
        start, round_ = stage_id(stage)
        prefix, others = stage["checked_prefix"], stage.get("additional_chains", [])
        pairs = stage.get("upper_pairs", [])
        cache_counts.update(stage.get("cache_counts", {}))
        for chain in others if pairs else ():
            for i in chain["upper_pair_indices"]:
                for function in pairs[i]:
                    function_counts["upper_functions_assessed"] += 1
                    function_counts["full_raw_support_mandatory"] += len(function["mandatory"]) == sum(map(len, function["pair"]))
                    function_counts["candidate_carrier_groups"] += function["candidate_groups"]
                    function_counts["noncanonical_two_touching_carrier_covers"] += len(function["two_touching_groups_left_to_examine"])
                    function_counts["three_touching_carrier_covers"] += function["three_touching_group_covers"]
                    function_counts["determining_bonds_with_three_touching_carriers"] += len(function["determining_three_touching_bonds"])
                    function_counts["determining_bonds_with_two_other_touching_carriers"] += len(
                        function["determining_bonds_with_two_other_touching_carriers"])
                function_counts["fixed_pair_bond_incidences"] += len(pairs[i][0]["fixed_pair_bonds"])
        for portion, chains in (("originally_checked", prefix), ("additional", others), ("all", prefix + others)):
            cell = Counter({"chain_occurrences": len(chains)})
            for chain in chains:
                for field in (*RESULTS, "every_law_needed_for_all_three_roles"):
                    cell[field] += chain[field]
                for i, role in enumerate(ROLES):
                    cell[f"strict_role_{role}"] += chain["strict_roles"][i]
            counts[portion].update(cell)
            by_round[portion][round_].update(cell)
        for result in RESULTS:
            found = next((c["chain_rank"] for c in prefix + others if c[result]), None)
            if found is not None:
                rank_minima[(start, round_)][result] = found
    return counts, by_round, rank_minima, cache_counts, function_counts


def prefix_results(minima):
    balance = {}
    first_by_query = {}
    for cap in (1, 2, 3, None):
        key = "all" if cap is None else str(cap)
        balance[key] = {}
        for metric in RESULTS:
            first = {}
            by_round = defaultdict(set)
            for (start, round_), ranks in minima.items():
                if metric not in ranks or (cap is not None and ranks[metric] > cap):
                    continue
                first[start] = min(first.get(start, round_), round_)
                by_round[round_].add(start)
            balance[key][metric] = {"starts_with_a_hit": len(first),
                                    "first_hit_histogram": Counter(first.values()),
                                    "starts_with_a_hit_at_each_round": {r: len(v) for r, v in sorted(by_round.items())}}
            first_by_query[key, metric] = first
    shifts = {}
    for metric in RESULTS:
        prefix, all_ = (first_by_query[key, metric] for key in ("3", "all"))
        shifts[metric] = {start: {"first_checked_prefix_round": prefix.get(start), "first_full_round": round_,
                                  "rank_in_first_full_round": minima[(start, round_)][metric]}
                          for start, round_ in sorted(all_.items()) if prefix.get(start) != round_}
    return balance, shifts


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pilot", action="store_true")
    parser.add_argument("--workers", type=int, choices=range(1, 6), default=1)
    parser.add_argument("--reset-every", type=int, default=0, help="Start fresh solvers after this many chains in a stage")
    parser.add_argument("--pilot-per-stage", type=int, help="Maximum number of omitted chains per pilot stage")
    parser.add_argument("--reuse", action="append", type=Path, default=[], help="Read complete omission stages from this archive")
    args = parser.parse_args()
    if args.reset_every < 0 or (args.pilot_per_stage is not None and (not args.pilot or args.pilot_per_stage < 1)):
        parser.error("Positive stage limits require a pilot. The restart interval cannot be negative.")
    begin = perf_counter()
    archive = list(json_lines(HERE / "stages.jsonl.gz"))
    prefix, paired, reduced = completed_prefix()
    rows = [row for row in archive if omitted_count(row)]
    selection = timing_slice(rows) if args.pilot else rows
    roster = {stage_id(row): row for row in selection}
    reuse = completed_omitted_stages(args.reuse, roster)
    remaining = [row for row in selection if stage_id(row) not in reuse]
    if args.pilot_per_stage:
        remaining = [{**row, "all_chains": row["all_chains"][:len(row["checked_chains"]) + args.pilot_per_stage]}
                     for row in remaining]
    remaining.sort(key=lambda row: (-omitted_count(row) * max(map(max, row["supports"])), stage_id(row)))
    choices = ThirdIndices(max(1 + max(map(max, row["supports"])) for row in rows))
    controls = direct_locality_control(choices)
    tag = "_parallel_pilot" if args.pilot and args.workers > 1 else "_pilot" if args.pilot else ""
    initargs = choices, prefix, paired, reduced, args.reset_every
    outcome = {}
    with ExitStack() as stack:
        output = stack.enter_context(gzip.open(HERE / f"stage_readings_omitted{tag}.jsonl.gz", "wt", encoding="utf-8", compresslevel=5))
        if args.workers > 1:
            process_pool = stack.enter_context(ProcessPoolExecutor(max_workers=args.workers, mp_context=get_context("fork"),
                                                                  initializer=initialize_worker, initargs=initargs))
            analyzed = process_pool.map(analyze_worker, remaining)
        else:
            initialize_worker(*initargs)
            analyzed = map(analyze_worker, remaining)
        expected_rows = [roster[key] for key in reuse] + remaining
        for sequence, (row, stage) in enumerate(zip(expected_rows, concatenate(reuse.values(), analyzed), strict=True), 1):
            key = stage_id(stage)
            assert stage_id(row) == key and len(stage["additional_chains"]) == omitted_count(row)
            assert stage["checked_prefix"] == prefix[key]
            assert row["checked_chains"] == row["all_chains"][:len(prefix[key])]
            assert [item["chain_law_indices"] for item in stage["additional_chains"]] == row["all_chains"][len(prefix[key]):]
            output.write(json.dumps(stage, separators=(",", ":")) + "\n")
            outcome[key] = {k: v for k, v in stage.items() if k != "upper_pairs"}
            # Keep the compact function counts in memory, rather than accumulating every carrier list.
            _, _, _, _, function_counts = aggregate([stage])
            outcome[key]["function_counts"] = function_counts
            if args.pilot:
                print(f"Timed {key[0]} round {key[1]} [{omitted_count(row)} additional chains] in {stage['elapsed_seconds']:.3f} seconds", flush=True)
            elif sequence % 50 == 0:
                print(f"Completed {sequence} of {len(selection)} omitted stages in {perf_counter() - begin:.1f} seconds", flush=True)
    stats_rows = list(outcome.values())
    if not args.pilot:
        stats_rows.extend({"start": start, "round": round_, "checked_prefix": chains}
                          for (start, round_), chains in prefix.items() if (start, round_) not in outcome)
    counts, by_round, minima, cache_counts, _ = aggregate(stats_rows)
    function_counts = Counter()
    for stage in outcome.values():
        function_counts.update(stage["function_counts"])
    if not args.pilot:
        reference = json.loads((HERE / "failure_rule_counts.json").read_text())["totals"]["omitted"]
        observed = counts["additional"]
        assert observed["original_step"] == reference["original_step"]
        assert observed["every_law_needed_for_all_three_roles"] == reference["all_eight_laws_needed_for_all_three_roles"]
        assert observed["chain_occurrences"] == reference["chains"] == sum(map(omitted_count, rows))
    prefixes, shifts = prefix_results(minima)
    summary = {
        "scope": "Arbitrary disjoint two- or three-distinction agreement carriers, three free pairs, and no lower agreement determined at a source knot. Chain ranks are one-based.",
        "role_gates": "The four original lower bonds are exact and unread at any source knot, the chosen role has seven upper words, none of its three functions is determined at any lower bond, and every individual chain law is necessary for that role.",
        "pilot": args.pilot,
        "worker_processes": args.workers,
        "worker_start_method": "fork" if args.workers > 1 else "single process",
        "solver_restart_interval_in_chains": args.reset_every,
        "reused_completed_stage_count": len(reuse),
        "reused_completed_stage_paths": [path.name for path in args.reuse],
        "reserved_witness_count_per_exact_pair_stage": SAMPLE_COUNT,
        "witness_seed_rule": f"{BASE_SEED} + 11 * census entry + round",
        "stage_count_by_round_on_full_roster": Counter(row["round"] for row in archive),
        "growing_starts": len({row["start"] for row in archive if row["round"] > 0}),
        "additional_stages_examined": len(outcome),
        "stage_scope_counts": counts,
        "by_round": by_round,
        "cache_counts": cache_counts,
        "additional_function_checks": function_counts,
        "prefix_comparisons": prefixes,
        "starts_whose_first_hit_changes_from_three_to_all": shifts,
        "first_qualifying_rank_by_stage": [{"start": start, "round": round_, **ranks}
                                          for (start, round_), ranks in sorted(minima.items())],
        "direct_small_stage_locality_controls": controls,
        "actual_omitted_chain_raw_sat_controls": [[stage["start"], stage["round"], chain["chain_rank"]]
                                                 for stage in outcome.values() for chain in stage["additional_chains"]
                                                 if chain["exact_raw_lower_and_deletion_control"]],
        "peak_resident_KiB": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        "largest_child_peak_resident_KiB": resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss,
        "elapsed_seconds": round(perf_counter() - begin, 6),
    }
    if args.pilot:
        total_by_size = Counter()
        runtime_by_size = Counter()
        chosen_by_size = Counter()
        for row in rows:
            total_by_size[stratum(row)] += omitted_count(row)
        for row in selection:
            size = stratum(row)
            chosen_by_size[size] += len(outcome[stage_id(row)]["additional_chains"])
            runtime_by_size[size] += outcome[stage_id(row)]["elapsed_seconds"]
        summary["projected_full_cpu_seconds"] = round(sum(
            runtime_by_size[size] * total / chosen_by_size[size] for size, total in total_by_size.items()), 3)
        summary["stage_timings"] = [[start, round_, stage["distinctions"], len(stage["additional_chains"]), stage["elapsed_seconds"], stage.get("work_seconds", {})]
                                    for (start, round_), stage in outcome.items()]
    destination = HERE / f"stage_readings_omitted_summary{tag}.json"
    destination.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({label: summary[label] for label in ("elapsed_seconds", "peak_resident_KiB", "stage_scope_counts",
                                                         "additional_function_checks", "projected_full_cpu_seconds")
                      if label in summary}, indent=2))


if __name__ == "__main__":
    main()
