"""Replay both rival growth rules and count eight-knot chains at each stage."""

import argparse
from collections import Counter, defaultdict
from dataclasses import dataclass, replace
from functools import cache
import gzip
from hashlib import sha256
from itertools import combinations, permutations
import json
from pathlib import Path
import resource
from time import perf_counter
import sys


HERE = Path(__file__).resolve().parent
STUDY = HERE.parent
RESEARCH = STUDY.parent
ROOT = RESEARCH.parent
CENSUS_FILE = RESEARCH / "FORBID-EDITS-20261126-001" / "starts.json"
PRIOR_GROWTH = RESEARCH / "NAE-LAYER-20261127-001" / "referee-R1"
PRIOR_CHAIN = RESEARCH / "CHAIN-STEP-20261127-001" / "referee-R1"
RIVAL_ARCHIVE = (
    ROOT / "artifacts" / "FORBIDDING-JOIN-20261120-001B"
    / "FORBIDDING-JOIN-20261120-001B-E001_free_readings" / "exact_readings.json.gz"
)
ARMS = ("one_fewer", "arity_floor")
LAST_ROUND = 6
CHAIN_CAP = 1_000
FIRST_CHAINS = 3

sys.path.insert(0, str(PRIOR_GROWTH))
from growth_rule import Birth, Growth, advance as ordinary_advance, supports_of


@dataclass(frozen=True)
class Stage:
    round: int
    supports: tuple[tuple[int, ...], ...]
    chains: tuple[tuple[int, ...], ...]
    births: tuple[Birth, ...]


@cache
def load_census():
    """Literal starting supports in the recorded zero-based census order."""
    return tuple(supports_of(start) for start in json.loads(CENSUS_FILE.read_text()))


def apply_allowance(plan, arm):
    if arm == "ordinary" or plan.status != "funded":
        return plan

    births = []
    for birth in plan.births:
        floor = max(0, 3 - len(birth.parents))
        ordinary = len(birth.fresh)
        count = min(ordinary, max(floor, ordinary - 1)) if arm == "one_fewer" else min(ordinary, floor)
        # Keep the first names in each ordinary allocation. Later births in
        # this round keep their names even when an earlier birth drops one.
        births.append(replace(birth, fresh=birth.fresh[:count]))
    old_count = len(plan.supports) - len(births)
    supports = plan.supports[:old_count] + tuple(birth.inputs + birth.fresh for birth in births)
    return Growth("funded", supports, tuple(births), {})


def advance(supports, arm):
    """Compare the cutoffs on one fresh ordinary proposal for these supports."""
    if arm not in (*ARMS, "ordinary"):
        raise ValueError(f"Unknown growth rule {arm}")
    # Both cuts retain at least three places and at most two holders per
    # distinction. The precursor's no-implication argument therefore still
    # applies to ordinary proposals on each reached rival stage.
    return apply_allowance(ordinary_advance(supports), arm)


def ordered_chains(supports, length=8):
    """Count each chain once, using the frozen priority for ordered selection."""
    eligible = [knot for knot, support in enumerate(supports) if len(support) == 3]
    if len(eligible) < length:
        return

    holders = defaultdict(list)
    for knot, support in enumerate(supports):
        for distinction in support:
            holders[distinction].append(knot)
    # The frozen tie-break follows first appearance in the displayed
    # supports. Traversing holder pairs in this order preserves it.
    meetings = {knot: Counter() for knot in eligible}
    for together in holders.values():
        for first, second in combinations(together, 2):
            if first in meetings and second in meetings:
                meetings[first][second] += 1
                meetings[second][first] += 1
    one_shared = {
        knot: tuple(other for other, count in neighbors.items() if count == 1)
        for knot, neighbors in meetings.items()
    }

    def extend(chain, excluded):
        last = chain[-1]
        if len(chain) == length:
            if length == 1 or chain[0] < last:
                yield chain
            return
        exclude_later = excluded.union(meetings[last], (last,))
        for following in one_shared[last]:
            if following not in excluded:
                yield from extend(chain + (following,), exclude_later)

    for first in eligible:
        yield from extend((first,), set())


def stage_rows(supports, arm):
    """Yield every reached stage, with all chains and the births into it."""
    current = Growth("funded", tuple(map(tuple, supports)), (), {})
    for round_number in range(LAST_ROUND + 1):
        yield Stage(round_number, current.supports, tuple(ordered_chains(current.supports)), current.births)
        if round_number == LAST_ROUND:
            break
        current = advance(current.supports, arm)
        if current.status != "funded":
            break


def read_jsonl(path):
    reader = gzip.open if path.suffix == ".gz" else open
    with reader(path, "rt") as stream:
        yield from map(json.loads, stream)


def frozen_rows(arm, size):
    records = {}
    for chunk in range(8):
        rows = list(read_jsonl(STUDY / "out" / f"{arm}_{chunk}.jsonl"))
        if [row["start"] for row in rows] != list(range(chunk, size, 8)):
            raise ValueError(f"Invalid census roster for {arm}, chunk {chunk}")
        records.update((row["start"], row["rows"]) for row in rows)
    return records


def literal_chain_controls():
    cases = (
        (tuple((2 * i, 2 * i + 1, 2 * i + 2) for i in range(8)), 8),
        (((0, 1, 2), (2, 3, 4), (4, 5, 6), (6, 7, 0)), 3),
        (((0, 1, 2), (1, 2, 3), (3, 4, 5), (5, 6, 7)), 3),
        (((0, 1, 2), (2, 3, 4, 5), (5, 6, 7), (7, 8, 9)), 2),
    )
    counts = []
    for supports, length in cases:
        eligible = {knot: set(support) for knot, support in enumerate(supports) if len(support) == 3}
        expected = {
            chain for chain in permutations(eligible, length) if chain[0] < chain[-1] and all(
                len(eligible[chain[first]] & eligible[chain[second]]) == (second == first + 1)
                for first, second in combinations(range(length), 2)
            )
        }
        observed = tuple(ordered_chains(supports, length))
        if set(observed) != expected or len(observed) != len(expected):
            raise ValueError("Chain enumeration disagrees with a literal support test")
        counts.append(len(observed))
    return counts


def archived_growth_controls(pilot):
    """Compare literal support names and supplies against archived rival replays."""
    with gzip.open(RIVAL_ARCHIVE, "rt") as stream:
        sources = json.load(stream)["sources"]
    if pilot:
        sources = sources[:3] + sources[-3:]
    counts = Counter()
    mismatches = []
    for source in sources:
        for arm, rows in source["laws"]["nae"].items():
            supports = tuple(map(tuple, source["initial_supports"]))
            for row in rows:
                case = [source["name"], arm, row["age"]]
                transition = row.get("transition")
                if transition is not None:
                    ordinary = ordinary_advance(supports)
                    grown = apply_allowance(ordinary, arm)
                    counts["transition_statuses"] += 1
                    if grown.status != transition["status"]:
                        mismatches.append(case + ["transition status"])
                    births = [{
                        "knot": birth.knot, "parents": list(birth.parents), "inputs": list(birth.inputs),
                        "p": len(birth.parents), "D": birth.demand, "q": len(plan.fresh), "f": len(birth.fresh),
                        "old_inputs_already_imply_law": not plan.fresh, "ordinary_fresh": list(plan.fresh),
                        "fresh": list(birth.fresh),
                    } for birth, plan in zip(grown.births, ordinary.births, strict=True)]
                    counts["birth_records"] += len(births)
                    if births != transition.get("births", []):
                        mismatches.append(case + ["birth records"])
                    supports = grown.supports
                    next_growth = advance(supports, arm)
                    recorded_next = transition.get("following_funding")
                    if recorded_next is not None:
                        counts["next_funding_checks"] += 1
                        status = "ready" if next_growth.status == "funded" else next_growth.status
                        shortages = {str(knot): n for knot, n in next_growth.shortages.items()}
                        if (status, shortages) != (recorded_next["status"], recorded_next["shortages"]):
                            mismatches.append(case + ["next funding"])
                counts["ordered_support_arrays"] += 1
                if supports != tuple(map(tuple, row["supports"])):
                    mismatches.append(case + ["ordered supports"])
    return {"sources": len(sources), **counts, "mismatches": mismatches}


def ordinary_reached_stages(supports, rounds):
    final_round = max(rounds)
    for round_number in range(final_round + 1):
        if round_number in rounds:
            yield Stage(round_number, supports, tuple(ordered_chains(supports)), ())
        if round_number == final_round:
            break
        growth = ordinary_advance(supports)
        if growth.status != "funded":
            break
        supports = growth.supports


def archived_chain_priority(census, pilot):
    """Check the frozen first-three order on the prior ordinary-growth archive."""
    records = defaultdict(dict)
    for row in read_jsonl(PRIOR_CHAIN / "stage_readings.jsonl.gz"):
        records[row["start"]][row["round"], row["chain_number"]] = tuple(row["chain_law_indices"])
    starts = sorted(records)[:8] if pilot else sorted(records)
    mismatches = []
    count = 0
    stage_count = 0
    for start in starts:
        expected = records[start]
        ordinary = ordinary_reached_stages(census[start], {round_number for round_number, _ in expected})
        observed = {(stage.round, i): chain for stage in ordinary
                    for i, chain in enumerate(stage.chains[:FIRST_CHAINS], start=1)}
        for key in sorted(expected.keys() | observed.keys()):
            if expected.get(key) != observed.get(key):
                mismatches.append([start, *key, expected.get(key), observed.get(key)])
        count += len(expected)
        stage_count += len({round_number for round_number, _ in expected})
    return {"starts": len(starts), "stages": stage_count, "first_three_chain_identities": count, "mismatches": mismatches}


def compare_frozen(arm, start, stages, next_growth, recorded, counts, mismatches):
    observed = {stage.round: (len(stage.supports), min(CHAIN_CAP, len(stage.chains))) for stage in stages}
    expected = {row["round"]: (row["knots"], row["chains"]) for row in recorded if "round" in row}
    for round_number in sorted(expected.keys() | observed.keys()):
        counts["stage_records_compared"] += 1
        if expected.get(round_number) != observed.get(round_number):
            mismatches.append([arm, start, round_number, expected.get(round_number), observed.get(round_number)])

    last = stages[-1].round
    observed_stop = None if last == LAST_ROUND else (next_growth.status, last)
    expected_stop = (recorded[-1]["stopped"], recorded[-1]["after round"]) if "stopped" in recorded[-1] else None
    counts["terminal_records_compared"] += 1
    if expected_stop != observed_stop:
        mismatches.append([arm, start, "terminal", expected_stop, observed_stop])


def holders_profile(supports):
    """Literal knot indices with distinction names erased, retaining multiplicities."""
    held = defaultdict(list)
    for knot, support in enumerate(supports):
        for distinction in support:
            held[distinction].append(knot)
    return Counter(map(tuple, held.values()))


def ordinary_comparison(rival, ordinary):
    counts = Counter()
    counts["stages"] = 1
    if ordinary is None:
        counts["unreached_ordinary_stages"] = 1
        return counts
    counts["same_ordered_supports"] += rival.supports == ordinary.supports
    counts["same_supports_up_to_distinction_renaming"] += (
        holders_profile(rival.supports) == holders_profile(ordinary.supports)
    )
    counts["ordinary_chain_positive_stages"] += bool(ordinary.chains)
    counts["same_chain_count"] += len(rival.chains) == len(ordinary.chains)
    counts["same_chain_law_index_order"] += rival.chains == ordinary.chains
    counts["same_first_three_chain_law_indices"] += rival.chains[:FIRST_CHAINS] == ordinary.chains[:FIRST_CHAINS]
    return counts


def round_six_support_exception(start, supports, rival, arm):
    ordinary = tuple(ordinary_reached_stages(supports, set(range(LAST_ROUND + 1))))
    first_change = next(left.round for left, right in zip(rival, ordinary, strict=True)
                        if left.supports != right.supports)
    preceding = rival[first_change - 1].supports
    ordinary_births = ordinary_advance(preceding).births
    changed_births = [{
        "knot": birth.knot, "parents": birth.parents, "demand": birth.demand,
        "ordinary_fresh": len(ordinary_birth.fresh), "rival_fresh": len(birth.fresh),
    } for birth, ordinary_birth in zip(rival[first_change].births, ordinary_births, strict=True)
        if birth.fresh != ordinary_birth.fresh]
    return {
        "start": start, "starting_supports": supports, "first_different_round": first_change,
        "first_different_births": changed_births,
        "stages": [{
            "round": left.round,
            "rival_knot_count": len(left.supports), "rival_chain_count": len(left.chains),
            "ordinary_knot_count": len(right.supports), "ordinary_chain_count": len(right.chains),
        } for left, right in zip(rival, ordinary, strict=True)],
        "rival_next_funding": advance(rival[-1].supports, arm).status,
        "round_six_rival_supports": rival[-1].supports, "round_six_ordinary_supports": ordinary[-1].supports,
    }


def summary_rows(counts):
    return [{"category": category, "count": n} for category, n in sorted(counts.items())]


def compare_rivals(start, supports, results, next_growth, comparison, exceptional):
    first, second = map(results.get, ARMS)
    different_support_stages = [a.round for a, b in zip(first, second) if a.supports != b.supports]
    comparison["starts_with_support_differences"] += bool(different_support_stages)
    for a, b in zip(first, second):
        comparison["common_stages"] += 1
        comparison["common_stage_ordered_support_differences"] += a.supports != b.supports
        comparison["common_stage_distinction_renaming_differences"] += (
            a.supports != b.supports and holders_profile(a.supports) != holders_profile(b.supports)
        )
        comparison["common_stage_knot_count_differences"] += len(a.supports) != len(b.supports)
        comparison["common_stage_chain_count_differences"] += len(a.chains) != len(b.chains)
        comparison["common_stage_ordered_chain_differences"] += a.chains != b.chains
        comparison["common_stage_first_three_chain_differences"] += a.chains[:FIRST_CHAINS] != b.chains[:FIRST_CHAINS]
        if a.chains or b.chains:
            comparison["common_chain_positive_stages"] += 1
            comparison["common_chain_positive_stage_support_differences"] += a.supports != b.supports

    comparison["stages_only_one_fewer"] += max(0, len(first) - len(second))
    comparison["stages_only_arity_floor"] += max(0, len(second) - len(first))
    terminal_a = first[-1].round, next_growth[ARMS[0]].status
    terminal_b = second[-1].round, next_growth[ARMS[1]].status
    comparison["starts_with_different_terminal_marks"] += terminal_a != terminal_b
    comparison["starts_with_same_terminal_mark_but_different_supports"] += (
        terminal_a == terminal_b and bool(different_support_stages)
    )
    if different_support_stages:
        first_difference = different_support_stages[0]
        comparison[f"first_support_difference_round_{first_difference}"] += 1
    if terminal_a == terminal_b:
        return

    difference = different_support_stages[0] if different_support_stages else None
    allowances = []
    if difference is not None:
        left, right = first[difference], second[difference]
        plan = ordinary_advance(first[difference - 1].supports)
        for old, new, ordinary in zip(left.births, right.births, plan.births, strict=True):
            if len(old.fresh) != len(new.fresh):
                allowances.append({
                    "knot": old.knot, "parents": len(old.parents), "parent_knots": old.parents,
                    "inputs": old.inputs, "demand": old.demand, "ordinary_fresh": len(ordinary.fresh),
                    "one_fewer_fresh": len(old.fresh), "arity_floor_fresh": len(new.fresh),
                })
    exceptional.append({
        "start": start, "starting_supports": supports, "first_different_round": difference,
        "changed_grants": allowances,
        "stage_knot_counts": {arm: [len(stage.supports) for stage in results[arm]] for arm in ARMS},
        "stage_chain_counts": {arm: [len(stage.chains) for stage in results[arm]] for arm in ARMS},
        "terminal": {arm: [results[arm][-1].round, next_growth[arm].status] for arm in ARMS},
        "shortages": {arm: next_growth[arm].shortages for arm in ARMS},
    })


def summarize_exceptions(exceptions):
    counts = {
        "first_changed_round": Counter(), "starting_knot_count": Counter(), "per_start_changed_grants": Counter(),
        "terminal_marks": Counter(), "changed_grant_patterns": Counter(),
        "one_fewer_stall_shortage": Counter(),
    }
    for row in exceptions:
        counts["first_changed_round"][row["first_different_round"]] += 1
        counts["starting_knot_count"][len(row["starting_supports"])] += 1
        counts["per_start_changed_grants"][len(row["changed_grants"])] += 1
        counts["terminal_marks"][tuple(tuple(row["terminal"][arm]) for arm in ARMS)] += 1
        for grant in row["changed_grants"]:
            counts["changed_grant_patterns"][tuple(grant[key] for key in (
                "parents", "demand", "ordinary_fresh", "one_fewer_fresh", "arity_floor_fresh"
            ))] += 1
        shortages = row["shortages"]["one_fewer"]
        removed = {grant["knot"] for grant in row["changed_grants"] if not grant["arity_floor_fresh"]}
        counts["one_fewer_stall_shortage"][tuple(sorted(shortages.values()))] += 1
        counts["zero_fresh_grants_match_shortage_holders"] = counts.get("zero_fresh_grants_match_shortage_holders", 0) + (
            bool(shortages) and shortages.keys() == removed
        )
    result = {key: summary_rows(counter) for key, counter in counts.items() if isinstance(counter, Counter)}
    result["zero_fresh_grants_match_shortage_holders"] = counts.get("zero_fresh_grants_match_shortage_holders", 0)
    result["chain_positive_starts"] = sum(any(any(chains) for chains in row["stage_chain_counts"].values()) for row in exceptions)
    result["changed_grant_key"] = ["parents", "demand", "ordinary fresh", "one fewer fresh", "arity floor fresh"]
    result["records"] = exceptions
    return result


def run(pilot):
    began = perf_counter()
    census = load_census()
    recorded = {arm: frozen_rows(arm, len(census)) for arm in ARMS}
    controls = {
        "literal_chain_counts": literal_chain_controls(),
        "earlier_growth_replay": archived_growth_controls(pilot),
        "earlier_chain_priority": archived_chain_priority(census, pilot),
    }
    controls_done = perf_counter()
    selected = (0, 3, 8, 19, 20, 47, 87, 90, 1312, 1334, 1591, 1675, 2030, 2176, 3609, 5097, 7074)
    indices = selected if pilot else range(len(census))
    rounds = {arm: [Counter() for _ in range(LAST_ROUND + 1)] for arm in ARMS}
    terminal = {arm: Counter() for arm in ARMS}
    archive_checks = {arm: Counter() for arm in ARMS}
    matched_ordinary = {arm: [Counter() for _ in range(LAST_ROUND + 1)] for arm in ARMS}
    matched_ordinary_chain_free = {arm: [] for arm in ARMS}
    round_six_support_exceptions = {arm: [] for arm in ARMS}
    positive_supports = {arm: set() for arm in ARMS}
    positive_starts = {arm: set() for arm in ARMS}
    comparison = Counter()
    mismatches = []
    exceptional = []

    for start in indices:
        supports = census[start]
        histories = {arm: tuple(stage_rows(supports, arm)) for arm in ARMS}
        next_growth = {arm: advance(stages[-1].supports, arm) for arm, stages in histories.items()}
        positive_rounds = {stage.round for stages in histories.values() for stage in stages if stage.chains}
        ordinary = {stage.round: stage for stage in ordinary_reached_stages(supports, positive_rounds)} if positive_rounds else {}
        for arm, stages in histories.items():
            compare_frozen(arm, start, stages, next_growth[arm], recorded[arm][start], archive_checks[arm], mismatches)
            terminal[arm][stages[-1].round, next_growth[arm].status] += 1
            for stage in stages:
                counts = rounds[arm][stage.round]
                counts["reached_stages"] += 1
                chain_count = len(stage.chains)
                counts["chain_positive_stages"] += bool(chain_count)
                counts["chain_occurrences"] += chain_count
                counts["first_three_occurrences"] += min(FIRST_CHAINS, chain_count)
                counts["max_chains"] = max(counts["max_chains"], chain_count)
                counts["stages_reaching_frozen_chain_cap"] += chain_count >= CHAIN_CAP
                if chain_count:
                    positive_supports[arm].add(stage.supports)
                    positive_starts[arm].add(start)
                    matched = ordinary.get(stage.round)
                    matched_ordinary[arm][stage.round].update(ordinary_comparison(stage, matched))
                    if matched is not None and not matched.chains:
                        matched_ordinary_chain_free[arm].append({
                            "start": start, "starting_supports": supports, "round": stage.round,
                            "ordinary_supports": matched.supports, "rival_supports": stage.supports,
                            "rival_chains": stage.chains,
                            "rival_next_funding": advance(stage.supports, arm).status,
                        })
                    if stage.round == LAST_ROUND and matched is not None and stage.supports != matched.supports:
                        round_six_support_exceptions[arm].append(round_six_support_exception(start, supports, stages, arm))
        compare_rivals(start, supports, histories, next_growth, comparison, exceptional)

    result = {
        "census_size": len(census), "starts_processed": len(indices), "pilot_start_indices": selected if pilot else None,
        "census_sha256": sha256(CENSUS_FILE.read_bytes()).hexdigest(),
        "last_materialized_round": LAST_ROUND,
        "last_round_funding_check": "test whether the reached round-six stage can fund round seven",
        "last_round_funding_in_terminal_marks": True,
        "controls": controls, "archive_mismatches": mismatches,
        "law_counts": {arm: {
            "rounds": [{"round": i, **counts} for i, counts in enumerate(rounds[arm])],
            "terminal_marks": summary_rows(terminal[arm]),
            "round_seven_next_funding": {status: n for (round_number, status), n in terminal[arm].items()
                                         if round_number == LAST_ROUND},
            "archive_checks": archive_checks[arm],
            "distinct_chain_positive_ordered_support_arrays": len(positive_supports[arm]),
            "starts_with_chain": len(positive_starts[arm]),
            "comparison_with_matched_ordinary_stages": {
                "total": sum(matched_ordinary[arm], Counter()),
                "per_round": [{"round": i, **counts} for i, counts in enumerate(matched_ordinary[arm]) if counts],
                "ordinary_chain_free_cases": matched_ordinary_chain_free[arm],
                "round_six_support_exceptions": round_six_support_exceptions[arm],
            },
        } for arm in ARMS},
        "between_laws": comparison,
        "different_terminal_starts": summarize_exceptions(exceptional),
        "seconds": {"controls_and_input": round(controls_done - began, 3), "recount": round(perf_counter() - controls_done, 3)},
        "peak_resident_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
    }
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pilot", action="store_true", help="time selected census entries and a subset of the controls")
    parsed = parser.parse_args()
    print(json.dumps(run(parsed.pilot), indent=2))
