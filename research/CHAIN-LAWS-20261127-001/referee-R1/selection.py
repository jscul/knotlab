"""Compare each cut with ordinary growth on the same start, at observed rounds."""

import argparse
from collections import Counter, defaultdict
from dataclasses import dataclass
from fractions import Fraction
import gzip
from itertools import chain
import json
from pathlib import Path
from random import Random
import resource
import sys
from time import perf_counter


HERE = Path(__file__).resolve().parent
STUDY = HERE.parent
RESEARCH = STUDY.parent
ORDINARY = RESEARCH / "CHAIN-STEP-20261127-001" / "referee-R1"
CENSUS = RESEARCH / "FORBID-EDITS-20261126-001" / "starts.json"
CUTS = ("one_fewer", "arity_floor")
HORIZON = 6
PILOT_COUNT = 72
PILOT_SEED = 41189


@dataclass(frozen=True)
class History:
    last: int
    stop: str
    chains: int
    witnesses: int

    def at(self, stage):
        if stage > self.last:
            raise ValueError("The requested round was not reached")
        return bool(self.witnesses & (1 << stage))

    def first_by(self, stage):
        if stage > self.last:
            raise ValueError("The requested observation window was not completed")
        before = self.witnesses & ((1 << (stage + 1)) - 1)
        return (before & -before).bit_length() - 1 if before else None


def read_rows(path):
    opener = gzip.open if path.suffix == ".gz" else open
    with opener(path, "rt") as source:
        yield from map(json.loads, source)


def encoded(stages):
    return sum(1 << number for number in stages)


def frozen_observations(ids):
    arms = {arm: {} for arm in CUTS}
    chain_counts = {}
    for arm, histories in arms.items():
        for shard in range(8):
            path = STUDY / "out" / f"{arm}_{shard}.jsonl"
            for item in read_rows(path):
                start = item["start"]
                if start not in ids:
                    continue
                assert start % 8 == shard and start not in histories
                stages = [row for row in item["rows"] if "round" in row]
                last = len(stages) - 1
                assert [row["round"] for row in stages] == list(range(last + 1))
                stop = item["rows"][-1].get("stopped", "horizon")
                if stop == "horizon":
                    assert last == HORIZON
                else:
                    assert last < HORIZON and item["rows"][-1]["after round"] == last
                chain_rounds, witness_rounds = [], []
                for stage in stages:
                    number, count = stage["round"], stage["chains"]
                    carried = stage.get("carried steps", 0)
                    assert 0 <= stage.get("every law needed", 0) <= carried <= min(3, count)
                    if count:
                        chain_rounds.append(number)
                        chain_counts[(arm, start, number)] = count
                    if carried:
                        witness_rounds.append(number)
                histories[start] = History(last, stop, encoded(chain_rounds), encoded(witness_rounds))
        assert set(histories) == ids
    return arms, chain_counts


def valid_chain(supports, ids):
    if len(ids) != 8 or len(set(ids)) != 8:
        return False
    knots = [set(supports[i]) for i in ids]
    return all(len(knot) == 3 for knot in knots) and all(
        len(knots[i] & knots[j]) == int(j == i + 1)
        for i in range(8) for j in range(i + 1, 8)
    )


def ordinary_observations(census, ids):
    # The imports are from the earlier independent checks under ordinary growth.
    # inspect checks complete stages using the exact two-holder extension
    # conditions. The current rival checks enter separately through incidence.
    sys.path.insert(0, str(ORDINARY))
    from census_six import ChainTables, inspect
    from recount import advance, ordered_chains, supports_of

    witnesses = {}
    for row in read_rows(ORDINARY / "census_six.jsonl.gz"):
        start = row["census_entry"]
        assert start not in witnesses and row["witness_knot_ids"] is not None
        witnesses[start] = tuple(row["witness_knot_ids"])
    original = json.loads((ORDINARY / "census_six.json").read_text())
    assert original["unresolved_starts"] == []
    assert len(witnesses) == original["totals"]["certified_starts"] == original["totals"]["chain_positive"]
    tables = ChainTables()
    histories, counts = {}, Counter()
    for start in sorted(ids):
        supports = supports_of(census[start])
        chain_rounds, witness_rounds = [], []
        for stage in range(HORIZON + 1):
            counts["stages_reached"] += 1
            if stage == HORIZON:
                chain_exists = next(ordered_chains(supports), None) is not None
                assert (start in witnesses) == chain_exists
                if chain_exists:
                    assert valid_chain(supports, witnesses[start])
                    chain_rounds.append(stage)
                    witness_rounds.append(stage)
                    counts["prior_witnesses_checked_for_chain_identity"] += 1
                stop = "horizon"
                break
            candidates = iter(ordered_chains(supports))
            first = next(candidates, None)
            if first is not None:
                chain_rounds.append(stage)
                cert, attempts = inspect(supports, chain([first], candidates), start, tables)
                counts["earlier_chain_positive_stages"] += 1
                counts["earlier_candidate_chains_tried"] += attempts["chains_tried"]
                if cert is not None:
                    assert valid_chain(supports, cert)
                    witness_rounds.append(stage)
                    counts["earlier_stages_with_full_witness"] += 1
                elif attempts["unresolved_alternative_cover"]:
                    raise ValueError(f"Undecided ordinary stage {start}, {stage}")
            following = advance(supports)
            if following.status != "funded":
                stop = following.status
                assert start not in witnesses
                break
            supports = following.supports
        histories[start] = History(stage, stop, encoded(chain_rounds), encoded(witness_rounds))
    return histories, dict(counts)


def group_histories(histories):
    grouped = defaultdict(list)
    for start, history in sorted(histories.items()):
        grouped[history].append(start)
    return [
        {"last_round": h.last, "next_round": h.stop, "rounds_with_chain": rounds(h.chains),
         "rounds_with_full_witness": rounds(h.witnesses), "census_entries": entries}
        for h, entries in sorted(grouped.items(), key=lambda pair: (pair[0].last, pair[0].stop, pair[0].witnesses, pair[0].chains))
    ]


def restore_histories(record):
    result = {}
    for row in record:
        h = History(row["last_round"], row["next_round"], encoded(row["rounds_with_chain"]),
                    encoded(row["rounds_with_full_witness"]))
        for entry in row["census_entries"]:
            assert entry not in result
            result[entry] = h
    return result


def rounds(mask):
    return [stage for stage in range(HORIZON + 1) if mask & (1 << stage)]


def independent_observations(ids, raw, chain_counts):
    # The complete step audit gives one result per chain on each distinct
    # ordered stage. The incidence table maps a reused stage to each start.
    completed = json.loads((HERE / "growth_counts.json").read_text())
    assert completed["starts_processed"] == completed["census_size"] and not completed["archive_mismatches"]
    incidence, counts_by_stage = {}, {}
    for row in read_rows(HERE / "step_incidence.jsonl.gz"):
        identity = (row["arm"], row["start"], row["round"])
        if row["start"] in ids:
            assert identity not in incidence
            stage = row["stage"]
            incidence[identity] = stage
            count = chain_counts[identity]
            assert count == counts_by_stage.setdefault(stage, count)
    assert incidence.keys() == chain_counts.keys()
    ranks = defaultdict(set)
    hits = {"first_three": set(), "all_chains": set()}
    frozen_hits = set()
    for row in read_rows(HERE / "step_passes.jsonl.gz"):
        stage, rank = row["stage"], row["chain_index"]
        if stage not in counts_by_stage:
            continue
        assert rank not in ranks[stage]
        assert type(row["all_gates"]) is bool and type(row["frozen"]) is bool
        ranks[stage].add(rank)
        if rank < 3 and row["frozen"]:
            frozen_hits.add(stage)
        if row["all_gates"]:
            hits["all_chains"].add(stage)
            if rank < 3:
                hits["first_three"].add(stage)
    for stage, count in counts_by_stage.items():
        assert ranks[stage] == set(range(count))
    comparisons = {}
    for scope, positive in hits.items():
        stage_numbers = defaultdict(list)
        for (arm, start, number), stage in incidence.items():
            assert (stage in frozen_hits) == raw[arm][start].at(number)
            if stage in positive:
                stage_numbers[arm, start].append(number)
        comparisons[scope] = {
            arm: {start: History(h.last, h.stop, h.chains, encoded(stage_numbers[arm, start]))
                  for start, h in histories.items()}
            for arm, histories in raw.items()
        }
    return comparisons


def paired(ordinary_positive, cut_positive, group):
    ordinary_ids = group & ordinary_positive
    cut_ids = group & cut_positive
    return {"starts": len(group), "both": len(ordinary_ids & cut_ids),
            "ordinary_only": len(ordinary_ids - cut_ids), "cut_only": len(cut_ids - ordinary_ids),
            "neither": len(group - (ordinary_ids | cut_ids))}


def exact_change(change):
    return {"rate_difference_fraction": str(change), "percentage_points": round(100 * float(change), 6)}


def compare_common_windows(ordinary, rival, group):
    obs_ordinary = {i for i in group if ordinary[i].witnesses}
    ord_same_window = {i for i in group if ordinary[i].first_by(rival[i].last) is not None}
    obs_rival = {i for i in group if rival[i].witnesses}
    both = ord_same_window & obs_rival
    cut_first = {i: rival[i].first_by(rival[i].last) for i in both}
    ord_first = {i: ordinary[i].first_by(rival[i].last) for i in both}
    timing_changes = [i for i in sorted(both) if ord_first[i] != cut_first[i]]
    return {
        "starts": len(group),
        "ordinary_ever_observed": len(obs_ordinary),
        "ordinary_ever_through_that_starts_last_cut_round": len(ord_same_window),
        "cut_ever_through_its_last_round": len(obs_rival),
        "change_in_count_from_shortening_the_ordinary_window_to_the_cut_window": len(ord_same_window) - len(obs_ordinary),
        "change_in_count_from_switching_law_at_the_same_window": len(obs_rival) - len(ord_same_window),
        "ordinary_and_cut_over_the_common_window": paired(ord_same_window, obs_rival, group),
        "first_witness_for_starts_with_both_within_the_common_window": {
            "ordinary_earlier": sum(ord_first[i] < cut_first[i] for i in both),
            "same_round": sum(ord_first[i] == cut_first[i] for i in both),
            "cut_earlier": sum(ord_first[i] > cut_first[i] for i in both),
        },
        "examples_of_different_onsets_in_census_order": [
            {"census_entry": i, "ordinary_first_round": ord_first[i], "cut_first_round": cut_first[i]}
            for i in timing_changes[:3]
        ],
    }


def ordinary_summary(ordinary):
    summary = json.loads((ORDINARY / "stage_readings_omitted_summary.json").read_text())
    overlap = 0
    for row in summary["first_qualifying_rank_by_stage"]:
        start, t = row["start"], row["round"]
        if start in ordinary:
            assert ordinary[start].at(t) == (row.get("strict_all_roles") is not None)
            overlap += 1
    counts = []
    for t in range(HORIZON + 1):
        observed = [h for h in ordinary.values() if h.last >= t]
        counts.append({
            "round": t, "reached": len(observed), "stages_with_chain": sum(bool(h.chains & (1 << t)) for h in observed),
            "stages_with_full_witness": sum(h.at(t) for h in observed),
            "first_full_witness_at_this_round": sum(h.first_by(t) == t for h in observed),
            "earlier_full_witness_but_none_at_this_round": sum(h.first_by(t) is not None and not h.at(t) for h in observed),
        })
    return {
        "by_round": counts, "earlier_sample_stage_results_matched": overlap,
        "earlier_sample_result_source": str((ORDINARY / "stage_readings_omitted_summary.json").relative_to(RESEARCH.parent)),
    }


def outcome(ordinary, rival, ids, census):
    funded = {i for i in ids if ordinary[i].last == HORIZON}
    survivors = {i for i in ids if rival[i].last == HORIZON}
    assert survivors <= funded
    assert all((rival[i].last > 0) == (i in funded) for i in ids)
    positive = {i for i in funded if ordinary[i].at(HORIZON)}
    cut_six = {i for i in survivors if rival[i].at(HORIZON)}
    cut_ever = {i for i in ids if rival[i].witnesses}
    p = Fraction(len(positive), len(funded))
    q = Fraction(len(positive & survivors), len(survivors))
    r = Fraction(len(cut_six), len(survivors))
    landmark = []
    for t in range(HORIZON + 1):
        observed = {i for i in ids if rival[i].last >= t}
        at_t = {i for i in observed if rival[i].at(t)}
        earlier = {i for i in observed if rival[i].first_by(t) is not None}
        row = {"round": t, "reached": len(observed), "witness_at_round": len(at_t),
               "had_witness_by_round_among_reached": len(earlier),
               "witness_at_round_and_reached_six": len(at_t & survivors),
               "no_witness_at_round_and_reached_six": len(survivors - at_t),
               "witness_at_round_and_stopped_before_six": len(at_t - survivors),
               "no_witness_at_round_and_stopped_before_six": len(observed - (at_t | survivors))}
        ordinary_at_t = {i for i in observed if ordinary[i].at(t)}
        row["matched_on_starts_reaching_this_cut_round"] = paired(ordinary_at_t, at_t, observed)
        row["matched_on_same_round_six_survivors"] = paired(ordinary_at_t, at_t, survivors)
        landmark.append(row)
    by_last = []
    for t in range(HORIZON + 1):
        group = {i for i in ids if rival[i].last == t}
        last_positive = {i for i in group if rival[i].at(t)}
        cut_first = {i: rival[i].first_by(t) for i in group}
        first = Counter(str(k) if k is not None else "none" for k in cut_first.values())
        row = {"last_funded_round": t, "starts": len(group),
               "next_round_status": dict(Counter(rival[i].stop for i in group)),
               "ordinary_witness_at_six": len(group & positive), "cut_witness_at_last_round": len(last_positive),
               "cut_witness_any_observed_round": len(group & cut_ever), "cut_first_witness": dict(sorted(first.items()))}
        ordinary_seen = {i for i in group if ordinary[i].first_by(t) is not None}
        ordinary_last = {i for i in group if ordinary[i].at(t)}
        row["matched_at_last_cut_round"] = paired(ordinary_last, last_positive, group)
        row["matched_ever_through_last_cut_round"] = paired(ordinary_seen, cut_ever, group)
        onset = Counter()
        for i in ordinary_seen & cut_ever:
            first_o, first_c = ordinary[i].first_by(t), cut_first[i]
            which = "ordinary_earlier" if first_o < first_c else "cut_earlier" if first_c < first_o else "same_round"
            onset[which] += 1
        row["onset_for_both_positive_in_common_window"] = dict(sorted(onset.items()))
        by_last.append(row)
    return {
        "unit": "One vote per census start in the stated population. The two laws are applied to the same identity.",
        "round_six_joint_counts_on_both_survivors": paired(positive, cut_six, survivors),
        "ordinary_six_on_starts_funded_under_both_but_stopped_by_cut": {
            "starts": len(funded - survivors), "ordinary_witnesses": len(positive - survivors)},
        "realized_round_six_outcome_over_all_starts": paired(positive, cut_six, ids),
        "realized_round_six_outcome_definition": "Count a reached round-six stage with a witness. A start that stopped earlier contributes zero reached witnesses at round six. Its step at that round is unobserved.",
        "ordinary_at_six_vs_cut_at_any_observed_round": paired(positive, cut_ever, ids),
        "conditional_difference_ordinary_reference": {
            "ordinary_on_ordinary_survivors": f"{len(positive)}/{len(funded)}",
            "ordinary_on_cut_survivors": f"{len(positive & survivors)}/{len(survivors)}",
            "cut_on_cut_survivors": f"{len(cut_six)}/{len(survivors)}",
            "change_from_selecting_cut_survivor_ids_under_ordinary": exact_change(q - p),
            "change_from_switching_law_on_same_survivor_ids": exact_change(r - q),
            "total_change_in_conditional_share": exact_change(r - p),
        },
        "examples_on_both_survivors": {
            label: [{"census_entry": i, "starting_knot_count": census[i][0],
                     "starting_meeting_pattern": census[i],
                     "ordinary_certified_rounds": rounds(ordinary[i].witnesses),
                     "cut_positive_rounds": rounds(rival[i].witnesses)} for i in sorted(group)[:3]]
            for label, group in (("ordinary_only", (survivors & positive) - cut_six),
                                 ("cut_only", cut_six - positive), ("neither", survivors - (cut_six | positive)))
        },
        "by_last_observed_cut_round": by_last,
        "by_observed_round": landmark,
        "common_window": {
            "all_starts": compare_common_windows(ordinary, rival, ids),
            "both_reached_six": compare_common_windows(ordinary, rival, survivors),
            "both_funded_at_least_once_but_cut_stopped": compare_common_windows(ordinary, rival, funded - survivors),
        },
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pilot", action="store_true", help="use 72 reproducibly chosen census entries")
    parser.add_argument("--join-complete", action="store_true", help="add complete per-chain results to an existing ordinary census replay")
    args = parser.parse_args()
    begin = perf_counter()
    census = json.loads(CENSUS.read_text())
    ids = set(range(len(census)))
    if args.pilot:
        ids = set(Random(PILOT_SEED).sample(range(len(census)), PILOT_COUNT))
    raw, chain_counts = frozen_observations(ids)
    path = HERE / ("selection_pilot.json" if args.pilot else "selection_counts.json")
    if args.join_complete:
        previous = json.loads(path.read_text())
        ordinary = restore_histories(previous["ordinary_by_census_entry"])
        assert ids == ordinary.keys()
        counts = previous["ordinary_replay_counts"]
    else:
        ordinary, counts = ordinary_observations(census, ids)
    results = {
        "starts": len(ids),
        "ordinary_sources": [str(p.relative_to(RESEARCH.parent)) for p in
                             (CENSUS, ORDINARY / "census_six.jsonl.gz", ORDINARY / "census_six.json")],
        "ordinary_gate": "All three choices pass on one chain. Every chain law is needed and every upper reading varies at some fixed value of every single stage bond. Candidate chains are searched until a witness is certified or all fail.",
        "ordinary_earlier_rounds": "On each reached stage before six, the earlier ordinary-growth checker certifies occurrences in chain order. At round six the earlier independent census supplies each positive witness. The replay checks its identity and structural coverage against the regrown stage.",
        "archived_cut_gate": "At least one of the first three chains passes the frozen test. This count omits the all-stage-bond locality test and does not require every law to be needed.",
        "rounds": "Round six means six completed growth rounds. No round is assigned to a cut after a closed or stalled stage.",
        "pilot_selection": {"count": PILOT_COUNT, "seed": PILOT_SEED} if args.pilot else None,
        "ordinary_replay_counts": counts,
        "ordinary_round_counts": ordinary_summary(ordinary),
        "archived_cut_first_three_frozen": {
            arm: outcome(ordinary, histories, ids, census)
            for arm, histories in raw.items()
        },
    }
    results["ordinary_by_census_entry"] = group_histories(ordinary)
    timing = {"seconds": round(perf_counter() - begin, 3),
              "peak_resident_KiB": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}
    if args.join_complete:
        results["timing"] = previous["timing"]
        matched = independent_observations(ids, raw, chain_counts)
        results["full_gate_cut_by_chain_selection"] = {
            scope: {arm: outcome(ordinary, histories, ids, census) for arm, histories in arms.items()}
            for scope, arms in matched.items()
        }
        timing = {"seconds": round(perf_counter() - begin, 3),
                  "peak_resident_KiB": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}
        results["join_timing"] = timing
        results["cut_sources"] = ["step_incidence.jsonl.gz", "step_passes.jsonl.gz", "growth_counts.json"]
    else:
        results["timing"] = timing
    path.write_text(json.dumps(results, indent=2) + "\n")
    print(json.dumps({"starts": len(ids), **counts, **timing}))


if __name__ == "__main__":
    main()
