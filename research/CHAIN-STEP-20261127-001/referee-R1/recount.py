"""Recount chains and replay ordered stage supports independently of the study."""

import argparse
from collections import Counter, defaultdict
import gzip
from hashlib import sha256
from itertools import islice, permutations
import json
from pathlib import Path
from random import Random
import sys


HERE = Path(__file__).resolve().parent
STUDY = HERE.parent
RESEARCH = STUDY.parent
GROWTH = RESEARCH / "NAE-LAYER-20261127-001" / "referee-R1"
sys.path.insert(0, str(GROWTH))
from growth_rule import advance, supports_of

CENSUS_FILE = RESEARCH / "FORBID-EDITS-20261126-001" / "starts.json"
EARLIER = RESEARCH / "FOUR-CLAUSE-20261127-001"
PREVIOUS = RESEARCH / "UPPER-GROWN-20261127-001"
CHAIN_LENGTH = 8
CHAIN_CAP = 1_000
CHECKED_PER_STAGE = 3
LAST_ROUND = 6
CONVERSE_CAP = 19


def load_census():
    return json.loads(CENSUS_FILE.read_text())


def read_jsonl(path):
    with path.open() as rows:
        yield from map(json.loads, rows)


def census_index(row):
    label, index = row["start"].split()
    if label != "census":
        raise ValueError(row["start"])
    return int(index)


def archive_records():
    return [list(read_jsonl(STUDY / "out" / f"cs_{chunk}.jsonl")) for chunk in range(12)]


def census_audit(census, chunks):
    roster = list(range(len(census)))
    pilot_10 = set(Random(1).sample(roster, 10))
    upper_grown = set(Random(20261128).sample([i for i in roster if i not in pilot_10], 1_000))
    used = pilot_10 | upper_grown | {420}
    four_clause = set(Random(20261130).sample([i for i in roster if i not in used], 600))
    pool = [i for i in roster if i not in used | four_clause]
    expected = sorted(Random(20261131).sample(pool, 1_000))
    observed_chunks = [list(map(census_index, rows)) for rows in chunks]
    observed = {i for chunk in observed_chunks for i in chunk}

    prior_archives = {
        "upper_growth": {census_index(row) for p in (PREVIOUS / "out").glob("census_*.jsonl") for row in read_jsonl(p)},
        "four_clause": {census_index(row) for p in (EARLIER / "out").glob("four_*.jsonl") for row in read_jsonl(p)},
    }
    saved_pilots = {
        p.name: {census_index(row) for row in read_jsonl(p)}
        for p in sorted((PREVIOUS / "pilot").glob("*.jsonl"))
    }
    return {
        "census_size": len(roster),
        "census_sha256": sha256(CENSUS_FILE.read_bytes()).hexdigest(),
        "seed": 20261131,
        "eligible_pool_size": len(pool),
        "excluded_union_size": len(roster) - len(pool),
        "sample_size": len(observed),
        "chunk_sizes": list(map(len, observed_chunks)),
        "chunks_match_seed_and_order": [chunk == expected[i::12] for i, chunk in enumerate(observed_chunks)],
        "earlier_seeded_rosters_match_archives": {
            "upper_growth": upper_grown == prior_archives["upper_growth"],
            "four_clause": four_clause == prior_archives["four_clause"],
            "ten_start_pilot": pilot_10 == saved_pilots["p10.jsonl"],
        },
        "earlier_archive_overlap": {name: sorted(observed & starts) for name, starts in prior_archives.items()},
        "saved_pilot_overlap": {name: sorted(observed & starts) for name, starts in saved_pilots.items()},
        "saved_pilot_eligible": {name: sorted(set(pool) & starts) for name, starts in saved_pilots.items()},
        "earlier_witness_census_420_drawn": 420 in observed,
        "validation_witnesses_drawn": sorted(observed & {2439, 5260}),
    }


def ordered_chains(supports, length=CHAIN_LENGTH):
    """Enumerate distinct chains, with the archived tie-break for the sampled prefix."""
    eligible = [knot for knot, support in enumerate(supports) if len(support) == 3]
    if len(eligible) < length:
        return

    # Traverse shared distinctions in first-occurrence order to recover the
    # archive's order of candidate extensions. The count is independent of it.
    distinctions = {}
    for knot, support in enumerate(supports):
        for distinction in support:
            distinctions.setdefault(distinction, []).append(knot)
    allowed = set(eligible)
    sharing = [0] * len(supports)
    repeated = [0] * len(supports)
    candidate_order = [[] for _ in supports]
    for holders in distinctions.values():
        if len(holders) != 2 or not allowed.issuperset(holders):
            continue
        first, second = holders
        for knot, other in ((first, second), (second, first)):
            mask = 1 << other
            if sharing[knot] & mask:
                repeated[knot] |= mask
            else:
                candidate_order[knot].append(other)
                sharing[knot] |= mask

    single_sharing = [shares & ~duplicates for shares, duplicates in zip(sharing, repeated, strict=True)]

    def extend(chain, blocked):
        last = chain[-1]
        if len(chain) == length:
            if chain[0] < last or length == 1:
                yield chain
            return
        possible = single_sharing[last] & ~blocked
        blocked_next = blocked | sharing[last] | (1 << last)
        for following in candidate_order[last]:
            if possible & (1 << following):
                yield from extend(chain + (following,), blocked_next)

    for knot in eligible:
        yield from extend((knot,), 0)


def stage_rows(index, start, recorded):
    """Yield one stage per completed round and next-round funding at every stage."""
    supports = supports_of(start)
    for round_number in range(LAST_ROUND + 1):
        following = advance(supports)
        chains = list(islice(ordered_chains(supports), CHAIN_CAP))
        yield {
            "start": index,
            "round": round_number,
            "supports": supports,
            "checked_chains": chains[:CHECKED_PER_STAGE],
            "all_chains": chains,
            "chain_count": len(chains),
            "next_growth_status": following.status,
            "recorded": recorded.get(round_number),
        }
        if following.status != "funded":
            break
        supports = following.supports


def pilot_stages():
    """Small archived prefix with exceptions, early checked rows, and maximum size."""
    census = load_census()
    archived = {census_index(rec): rec["rounds"] for chunk in archive_records() for rec in chunk}
    pilot_indices = {90, 2030, 3609, 5260}
    for round_number in range(2, LAST_ROUND + 1):
        available = [(i, row) for i in sorted(archived) for row in archived[i] if row["round"] == round_number]
        pilot_indices.add(next(i for i, row in available if row["chains"]))
        pilot_indices.add(max(available, key=lambda item: item[1]["distinctions"])[0])
    for index in sorted(pilot_indices):
        recorded = {row["round"]: row for row in archived.get(index, [])}
        yield from stage_rows(index, census[index], recorded)


def detector_control():
    """Compare to literal tuple enumeration on small meeting patterns."""
    systems = [
        ([(2 * i, 2 * i + 1, 2 * i + 2) for i in range(8)], 8),
        ([(0, 1, 2), (2, 3, 4), (4, 5, 6), (6, 7, 0)], 3),
        ([(0, 1, 2), (1, 2, 3), (3, 4, 5), (5, 6, 7)], 3),
        ([(0, 1, 2), (2, 3, 4, 5), (5, 6, 7), (7, 8, 9)], 2),
    ]
    counts = []
    for supports, length in systems:
        support_sets = list(map(set, supports))
        expected = {
            chain for chain in permutations([i for i, support in enumerate(supports) if len(support) == 3], length)
            if chain[0] < chain[-1] and all(
                len(support_sets[chain[i]] & support_sets[chain[j]]) == int(j - i == 1)
                for i in range(length) for j in range(i + 1, length)
            )
        }
        observed = list(ordered_chains(supports, length))
        if set(observed) != expected or len(observed) != len(expected):
            raise RuntimeError("Chain detector failed its literal enumeration control")
        counts.append(len(observed))
    return counts


def named_witness_audit(census):
    path = EARLIER / "referee-R1" / "witness_checks.json"
    earlier = json.loads(path.read_text())
    checks = {}
    for key in ("census_420", "census_5260"):
        witness = earlier[key]
        index = witness["census_entry"]
        supports = supports_of(census[index])
        checks[key] = []
        for old_supports in witness["knots_by_round"]:
            checks[key].append([list(row) for row in supports] == old_supports)
            supports = advance(supports).supports
    return checks


def stage_mismatches(stage):
    recorded = stage["recorded"]
    if recorded is None:
        return {"absent from archived output": True}
    supports = stage["supports"]
    distinctions = len({d for support in supports for d in support})
    expected = {
        "round": stage["round"],
        "knots": len(supports),
        "distinctions": distinctions,
        "chains": stage["chain_count"],
    }
    mismatches = {field: [recorded.get(field), value] for field, value in expected.items() if recorded.get(field) != value}
    mapped = len(recorded.get("mapped", ()))
    if mapped != len(stage["checked_chains"]):
        mismatches["checked chains"] = [mapped, len(stage["checked_chains"])]
    converse_eligible = stage["round"] in (1, 2) and distinctions <= CONVERSE_CAP
    if ("converse" in recorded) != converse_eligible:
        mismatches["converse eligibility"] = ["converse" in recorded, converse_eligible]
    return mismatches


def accumulate(counter, stage):
    recorded = stage["recorded"] or {}
    count = stage["chain_count"]
    checked = len(stage["checked_chains"])
    mapped = recorded.get("mapped", ())
    counter["stage_rows"] += 1
    counter["stages_with_chain"] += bool(count)
    counter["chains_capped_total"] += count
    counter["largest_stage_chain_count"] = max(counter["largest_stage_chain_count"], count)
    counter["stages_at_chain_cap"] += count == CHAIN_CAP
    counter["checked_chains"] += checked
    counter["unchecked_chains_among_counted"] += count - checked
    counter["stages_next_" + stage["next_growth_status"]] += 1
    counter["archived_steps_on_checked_chains"] += sum(row["a step"] for row in mapped)
    counter["archived_every_chain_law_needed"] += sum(row["every chain law needed"] for row in mapped)
    counter["archived_steps_with_every_chain_law_needed"] += sum(
        row["a step"] and row["every chain law needed"] for row in mapped
    )
    if "converse" in recorded:
        counter["converse_rows"] += 1
        counter["converse_rows_with_at_least_17_distinctions"] += recorded["distinctions"] >= 17
        counter["converse_rows_with_at_least_8_three_place_knots"] += sum(len(r) == 3 for r in stage["supports"]) >= 8
        counter["converse_rows_with_chain"] += bool(count)
        for field in ("patterns", "steps"):
            counter["archived_converse_" + field] += recorded["converse"][field]


def full_recount(census, chunks):
    archive = HERE / "stages.jsonl.gz"
    rounds = defaultdict(Counter)
    mismatches = []
    first_steps = {"grew": Counter(), "did_not_grow": Counter()}
    starts_with_chain = set()
    starts_with_step = set()
    archive_table = {census_index(rec): rec["rounds"] for chunk in chunks for rec in chunk}
    with archive.open("wb") as compressed, gzip.GzipFile(fileobj=compressed, mode="wb", mtime=0, filename="") as output:
        for index, recorded_rows in sorted(archive_table.items()):
            stage_count = 0
            first_step = None
            by_round = {row["round"]: row for row in recorded_rows}
            for stage in stage_rows(index, census[index], by_round):
                round_number = stage["round"]
                stage_count += 1
                differences = stage_mismatches(stage)
                if differences:
                    mismatches.append([index, round_number, differences])
                accumulate(rounds[round_number], stage)
                output.write((json.dumps(stage, separators=(",", ":")) + "\n").encode())
                if stage["chain_count"]:
                    starts_with_chain.add(index)
                mapped = (stage["recorded"] or {}).get("mapped", ())
                if first_step is None and any(row["a step"] for row in mapped):
                    first_step = round_number
                    starts_with_step.add(index)
            if stage_count != len(recorded_rows):
                mismatches.append([index, "total stages", [len(recorded_rows), stage_count]])
            cohort = "grew" if stage_count > 1 else "did_not_grow"
            first_steps[cohort][first_step if first_step is not None else "none by round 6"] += 1

    n_growing_at_start = rounds[0]["stages_next_funded"]
    for round_number, counts in rounds.items():
        denominator = counts["stage_rows"] if round_number > 0 else n_growing_at_start
        counts["growing_start_denominator"] = denominator
        counts["share_of_growing_starts_with_chain"] = counts["stages_with_chain"] / denominator
    return {
        "rounds": dict(sorted(rounds.items())),
        "first_archived_step_on_a_checked_chain": first_steps,
        "starts_with_any_chain": len(starts_with_chain),
        "starts_with_any_archived_step_on_a_checked_chain": len(starts_with_step),
        "starts_with_chain_but_no_archived_step_on_a_checked_chain": sorted(starts_with_chain - starts_with_step),
        "stage_archive_sha256": sha256(archive.read_bytes()).hexdigest(),
        "structural_mismatches": mismatches,
    }


def archived_stages():
    with gzip.open(HERE / "stages.jsonl.gz", "rt") as rows:
        yield from map(json.loads, rows)


def check_growth_order(pilot):
    """Compare literal identities against the shared production growth code."""
    experiments = RESEARCH.parent / "experiments"
    paths = (
        experiments / "NAE-GROWTH-20261119-001B" / "NAE-GROWTH-20261119-001B-E001_nae",
        experiments / "FORBIDDING-JOIN-20261120-001B" / "FORBIDDING-JOIN-20261120-001B-E001_free_readings",
    )
    sys.path[:0] = list(map(str, paths))
    import naelib
    from rival_growth import grow

    pilot_indices = {0, 20, 87, 90, 424, 463, 2030, 3609}
    previous_start = None
    expected_supports = None
    supports_checked = 0
    funding_checked = 0
    differences = []
    for row in archived_stages():
        start = row["start"]
        if pilot and start not in pilot_indices:
            continue
        supports = tuple(map(tuple, row["supports"]))
        if start == previous_start:
            supports_checked += 1
            if supports != expected_supports:
                differences.append([start, row["round"], "ordered supports"])
        expected_supports, info = grow(supports, "nae", "ordinary", naelib)
        funding_checked += 1
        if info["status"] != row["next_growth_status"]:
            differences.append([start, row["round"], "funding"])
        previous_start = start
    return {"ordered_support_checks": supports_checked, "funding_checks": funding_checked, "differences": differences}


def sensitivity_to_saved_pilot_overlap(pilot_overlap):
    excluded = {i for indices in pilot_overlap.values() for i in indices}
    round_counts = defaultdict(Counter)
    joint_converse_opportunity = 0
    for stage in archived_stages():
        recorded = stage["recorded"]
        joint_converse_opportunity += (
            "converse" in recorded and recorded["distinctions"] >= 17
            and sum(len(support) == 3 for support in stage["supports"]) >= 8
        )
        if stage["start"] not in excluded:
            accumulate(round_counts[stage["round"]], stage)
    return {
        "excluded_census_entries": sorted(excluded),
        "converse_rows_meeting_both_necessary_chain_size_bounds_before_exclusion": joint_converse_opportunity,
        "round_2_without_overlap": dict(round_counts[2]),
        "round_6_without_overlap": dict(round_counts[6]),
        "checked_chains_without_overlap": sum(row["checked_chains"] for row in round_counts.values()),
        "archived_steps_without_overlap": sum(row["archived_steps_on_checked_chains"] for row in round_counts.values()),
        "archived_steps_with_every_chain_law_needed_without_overlap": sum(
            row["archived_steps_with_every_chain_law_needed"] for row in round_counts.values()
        ),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pilot", action="store_true", help="Time a small cross-section without writing files")
    parser.add_argument("--verify-order", action="store_true", help="Compare the saved archive to the shared growth rule")
    args = parser.parse_args()
    summary_path = HERE / "recount.json"
    if args.verify_order:
        result = check_growth_order(args.pilot)
        print(json.dumps(result))
        if not args.pilot:
            summary = json.loads(summary_path.read_text())
            summary["production_growth_order_check"] = result
            summary["prior_pilot_overlap_sensitivity"] = sensitivity_to_saved_pilot_overlap(
                summary["sample"]["saved_pilot_overlap"]
            )
            summary_path.write_text(json.dumps(summary, indent=2) + "\n")
        return
    controls = detector_control()
    if args.pilot:
        stages = list(pilot_stages())
        mismatches = [stage_mismatches(stage) for stage in stages if stage["recorded"] is not None]
        print(json.dumps({
            "pilot_stages": len(stages),
            "pilot_starts": sorted({stage["start"] for stage in stages}),
            "pilot_checked_chains": sum(len(stage["checked_chains"]) for stage in stages),
            "archived_stage_mismatches": [mismatch for mismatch in mismatches if mismatch],
            "detector_controls": controls,
        }))
        return

    census = load_census()
    chunks = archive_records()
    summary = {
        "sample": census_audit(census, chunks),
        "archived_named_witness_support_matches": named_witness_audit(census),
        "detector_control_counts": controls,
        "chain_length": CHAIN_LENGTH,
        "chain_cap": CHAIN_CAP,
        "checked_per_stage_cap": CHECKED_PER_STAGE,
        "converse_distinction_cap": CONVERSE_CAP,
        **full_recount(census, chunks),
    }
    summary_path.write_text(json.dumps(summary, indent=2) + "\n")


if __name__ == "__main__":
    main()
