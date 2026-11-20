"""Replay the uniform queries in two established explosive growths."""

from argparse import ArgumentParser
from collections import Counter
from functools import reduce
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
from operator import or_
from pathlib import Path
from random import Random
import json
import sys

from deep import DRAWS, HERE, HORIZON, LAWS, LITERAL_FIXTURE, LITERAL_OPERATOR, RESEARCH, ROOT, rates


PARTNER_ANCHOR = 5
PARTNER_SEED = 20261120405
ARCHIVE_ANCHOR = 12
ARCHIVE_SEED = 20261120406
ARCHIVE_CAP = 384
PARTNER_PROOF = ROOT / ("proofs/WALL-READ-20261119-001A/"
                        "WALL-READ-20261119-001A-P001_partnered")
ARCHIVE_SOURCE = ROOT / ("artifacts/HEAVY-GROWTH-20261119-001/"
                         "HEAVY-GROWTH-20261119-001-E001_checks/sources_audit.json")
READERS = ("full_current", "growing_end")
EVENTS = (
    "funded",
    "at_least_one_recognized_release",
    "one_recognized_release",
    "two_or_more_recognized_releases",
    "both_persist_direct",
    "both_persist_indirect",
    "recurrent_source",
)
SCOPES = ("frozen_reader", "broader_existence")
SIMULTANEOUS_CELLS = 2 * len(LAWS) * len(READERS) * len(EVENTS) * len(SCOPES)


def load(name, path):
    spec = spec_from_file_location(name, path)
    module = module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def holding_supports(sizes, meetings, fixture):
    degree = Counter(holder for pair in meetings for holder in pair)
    return fixture.source_from(meetings, [size - degree[knot] for knot, size in enumerate(sizes)])


def summarize(draws, law):
    summary = {}
    bonferroni_tail = (0.025 / SIMULTANEOUS_CELLS) ** (1 / DRAWS)
    for reader in READERS:
        summary[reader] = {
            "denominator": len(draws),
            "lawful_denominator": len(draws),
            "funded_denominator": sum(draw["events_by_law"][law]["frozen_reader"]["funded"]
                                      for draw in draws),
        }
        for scope in SCOPES:
            result = {}
            for event in EVENTS:
                values = Counter(draw["events_by_law"][law][scope][event] for draw in draws)
                yes, no, unknown = values[True], values[False], values[None]
                result[event] = rates(yes, no, unknown)
                result[event]["simultaneous_binomial_95"] = [
                    bonferroni_tail if yes else 0.0, 1 - bonferroni_tail if no else 1.0,
                ]
            summary[reader][scope] = result
    return summary


def holders_of(mask, pairs):
    return frozenset(2 * pair + (mask >> pair & 1) for pair in range(pairs))


def held_masks(pair_representatives, old_count):
    """The current mask holding the children of each previous holder."""
    blocks = []
    for holder in range(old_count):
        # Side zero of a child pair is its representative mask. The other
        # child contains an older holder exactly when this one does not.
        pair, side = divmod(holder, 2)
        mask = sum(1 << index for index, child in enumerate(pair_representatives)
                   if (child >> pair & 1) != side)
        blocks.append(mask)
    return tuple(blocks)


def partnered_kernel():
    counts = [6]
    rosters = {}
    forbidden = {1: ()}
    for age in range(1, PARTNER_ANCHOR):
        pairs = counts[-1] // 2
        complement = (1 << pairs) - 1
        removed = set(forbidden[age])
        assert removed == {mask ^ complement for mask in removed}
        representatives = tuple(mask for mask in range((complement + 1) // 2) if mask not in removed)
        rosters[age] = tuple(mask for rep in representatives for mask in (rep, rep ^ complement))
        counts.append(2 * len(representatives))
        forbidden[age + 1] = held_masks(representatives, counts[-2])
        assert len(set(forbidden[age + 1])) == counts[-2]

    # Finite check of the compulsory two-step ancestry argument. The proof
    # in deep_explosive.md extends it to every later size.
    for age in range(2, PARTNER_ANCHOR):
        older_pairs = counts[age - 2] // 2
        earlier = [sum(1 << holder for holder in holders_of(mask, older_pairs))
                   for mask in rosters[age - 1]]
        everything = (1 << counts[age - 2]) - 1
        for later in rosters[age]:
            assert reduce(or_, (earlier[i] for i in holders_of(later, counts[age - 1] // 2))) == everything
    return counts, rosters, forbidden


def partnered_literal(fixture, counts, rosters, forbidden):
    wall_job = load("wall_read_partnered_job", PARTNER_PROOF / "job.py")
    opens, blocks = wall_job.partnered(3)
    sizes, meetings = wall_job.hub_start(opens, blocks)
    source = holding_supports(sizes, meetings, fixture)
    controls = {}
    for law in LAWS:
        fixture.certify_source(source, law)
        frames, layers = fixture.trajectory(source, law, 3)
        assert len(frames) == 4
        previous = tuple(range(counts[0]))
        for age, (births, _) in enumerate(layers, 1):
            actual = {frozenset(birth.parents): birth for birth in births}
            assert len(actual) == counts[age]
            current = []
            for mask in rosters[age]:
                expected = frozenset(previous[i] for i in holders_of(mask, counts[age - 1] // 2))
                birth = actual[expected]
                assert len(birth.fresh) == (1 << (counts[age] // 2 - 1)) - counts[age - 1] // 2
                current.append(birth.knot)
            previous = tuple(current)
        # At age 3 the complete physical roster still fits. Rebuild its
        # age-4 parent proposals alone from the historical ordinary operator.
        # The impossible-to-materialize fresh distinctions are symbolic.
        operator = sys.modules["end_operator"]
        end = operator.from_stars(frames[-1])
        literal = set(map(frozenset, operator.proposals(end)))
        indexed = [holders_of(mask, counts[3] // 2) for mask in rosters[4]]
        expected = {frozenset(previous[i] for i in parents) for parents in indexed}
        assert expected == literal
        # Check each age-5 exclusion by assembling a real age-4 co-child
        # roster one parent membership at a time at the audited age-4 cut.
        for holder, mask in enumerate(forbidden[5]):
            expected_witness = {i for i, parents in enumerate(indexed) if holder in parents}
            assert expected_witness == holders_of(mask, counts[4] // 2)
        controls[law] = {
            "source_supports_k1_k3": len(source),
            "literal_births_through_age_three": sum(counts[1:4]),
            "age_four_parent_rosters_verified": len(literal),
            "age_five_held_choices_verified": len(forbidden[5]),
        }
    return source, controls


def permitted_mask(rank, forbidden):
    value = rank
    for blocked in forbidden:
        if blocked > value:
            break
        value += 1
    return value


def hypothesis_rates(**updates):
    result = dict.fromkeys(EVENTS, False)
    result["funded"] = True
    result.update(updates)
    assert tuple(result) == EVENTS
    return result


def partnered(fixture):
    counts, rosters, forbidden = partnered_kernel()
    source, controls = partnered_literal(fixture, counts, rosters, forbidden)
    pairs = counts[-1] // 2
    blocked = sorted(forbidden[PARTNER_ANCHOR])
    population = (1 << pairs) - len(blocked)
    assert (pairs, len(blocked)) == (2043, 24)
    rng = Random(PARTNER_SEED)
    draws = []
    for _ in range(DRAWS):
        rank = rng.randrange(population)
        mask = permitted_mask(rank, blocked)
        assert mask not in blocked and mask < 1 << pairs
        assert rank == mask - sum(b < mask for b in blocked)
        events = hypothesis_rates()
        draws.append({
            "scorer_rank_hex": hex(rank),
            "scorer_actual_parent_mask_hex": hex(mask),
            "shared_forward_readings": "age_five_to_twenty_one",
            "events_by_law": {
                law: {scope: events for scope in SCOPES} for law in LAWS
            },
        })
    trace = []
    for age in range(PARTNER_ANCHOR, PARTNER_ANCHOR + HORIZON + 1):
        inclusive = {
            PARTNER_ANCHOR: "1",
            PARTNER_ANCHOR + 1: f"N[{age}]/2",
        }.get(age, f"N[{age}]")
        trace.append({
            "age": age,
            "full_current": {
                "previous_holders": f"N[{age - 1}]/2",
                "previous_holder_arity": f"(N[{age - 2}] + N[{age}])/2",
            },
            "growing_end": {
                "live_knots": f"N[{age}]",
                "loose": f"N[{age + 1}]/2",
                "witnessed_degree": f"N[{age}]-2",
                "witness_count_at_holder": f"N[{age - 1}]/2",
                "size_of_each_witnessed_set": f"N[{age}]/2",
            },
            "inclusive_descendants_of_each_query": inclusive,
        })
    return {
        "source_supports": source,
        "checks_by_law": controls,
        "seed": PARTNER_SEED,
        "weighting": "uniform individual births with replacement",
        "cohort_size": "2^2043-24",
        "anchor_age": PARTNER_ANCHOR,
        "followup_parent_steps": HORIZON,
        "roster_counts_through_age_four": counts,
        "held_masks_at_age_five_hex": list(map(hex, blocked)),
        "count_recurrence": "N[t+1] = 2^(N[t]/2) - N[t-1]",
        "age_five_to_twenty_one": trace,
        "summary_by_law": {law: summarize(draws, law) for law in LAWS},
        "draws": draws,
    }


def literal_archive(source, law, fixture):
    stars = source
    frames = [stars]
    cohorts = [tuple(range(len(source)))]
    records = {}
    for age in range(1, ARCHIVE_ANCHOR + HORIZON + 1):
        status, births, _ = fixture.literal_turn(stars, law)
        assert status in ("closed", "extend")
        assert len(births) <= ARCHIVE_CAP
        if status == "extend":
            records[age] = {birth.knot: birth for birth in births}
            stars = stars + tuple(birth.support for birth in births)
        cohorts.append(tuple(birth.knot for birth in births))
        frames.append(stars)
    return frames, cohorts, records


def archive_ancestry(anchor, records):
    masks = {holder: 1 << i for i, holder in enumerate(anchor)}
    ancestry = {ARCHIVE_ANCHOR: masks}
    for age, births in records.items():
        if age <= ARCHIVE_ANCHOR:
            continue
        masks = {holder: reduce(or_, (masks[p] for p in birth.parents))
                 for holder, birth in births.items()}
        ancestry[age] = masks
    return ancestry


def relay_evidence(fixture, frames, records):
    previous = None
    endpoint_reports = {}
    for age in range(24, ARCHIVE_ANCHOR + HORIZON + 1):
        _, ordinary, loose = fixture.incidence(frames[age])
        _, witnessed = fixture.witnessed_end(ordinary, loose)
        assert set(map(len, loose.values())) == {2}
        assert len(loose) == age - 22
        ends = frozenset(holder for holder, d in witnessed.degree if d == 1)
        assert len(ends) == 2
        assert witnessed.number_of_edges() == len(loose) - 1
        one_end = min(ends)
        seen = {one_end}
        walk = [one_end]
        for holder in walk:
            for following in set(witnessed[holder]) - seen:
                seen.add(following)
                walk.append(following)
        assert seen == set(loose) and max(dict(witnessed.degree()).values()) <= 2
        if previous is None:
            relay, = records[23]
            assert all(records[age][holder].parents == (relay,) for holder in ends)
        else:
            assert {records[age][holder].parents for holder in ends} == {(p,) for p in previous}
        report = {"witnessed_path_ends": sorted(ends), "loose_per_holder": 2}
        if age == 25:
            shared, = [birth for birth in records[age].values() if frozenset(birth.parents) == previous]
            report["direct_birth"] = {"knot": shared.knot, "parents": shared.parents,
                                      "fresh": len(shared.fresh)}
        endpoint_reports[age] = report
        previous = ends
    return endpoint_reports


def archive(fixture):
    original = json.loads(ARCHIVE_SOURCE.read_bytes())["named_archive_starts"]["start-00"]
    source = tuple(map(tuple, original["gate"]["literal_supports"]))
    assert source == holding_supports(original["sizes"], original["meetings"], fixture)
    law_records = {}
    for law in LAWS:
        fixture.certify_source(source, law)
        frames, cohorts, records = literal_archive(source, law, fixture)
        assert list(map(len, cohorts[:21])) == original["round_junction_counts"]
        assert list(map(len, cohorts[21:23])) == [9, 1]
        anchor = cohorts[ARCHIVE_ANCHOR]
        assert len(anchor) == 67 and len(cohorts[ARCHIVE_ANCHOR + 1]) == 322
        ancestry = archive_ancestry(anchor, records)
        top, = records[22].values()
        assert ancestry[22][top.knot] == (1 << len(anchor)) - 1
        if law == "parity":
            assert not top.fresh and not any(cohorts[23:])
            relay = None
        else:
            assert len(top.fresh) == 1
            follow, = records[23].values()
            assert follow.parents == (top.knot,) and len(follow.fresh) == 2
            relay = relay_evidence(fixture, frames, records)
        law_records[law] = (cohorts, records, ancestry, relay)

    cohorts, _, _, _ = law_records["parity"]
    assert cohorts[:23] == law_records["nae"][0][:23]
    population = len(cohorts[ARCHIVE_ANCHOR])
    rng = Random(ARCHIVE_SEED)
    draws = []
    for _ in range(DRAWS):
        rank = rng.randrange(population)
        participation = {}
        events_by_law = {}
        for law, (_, _, ancestry, relay) in law_records.items():
            participation[law] = {
                age: sum(bool(mask >> rank & 1) for mask in ancestry.get(age, {}).values())
                for age in range(ARCHIVE_ANCHOR, ARCHIVE_ANCHOR + HORIZON + 1)
            }
            assert participation[law][22] == 1
            if law == "nae":
                assert all(ancestry[24][holder] >> rank & 1 for holder in relay[24]["witnessed_path_ends"])
                assert ancestry[25][relay[25]["direct_birth"]["knot"]] >> rank & 1
                events = hypothesis_rates(
                    at_least_one_recognized_release=True,
                    two_or_more_recognized_releases=True,
                    both_persist_direct=True,
                )
                broader = events | {"both_persist_indirect": None}
            else:
                events = broader = hypothesis_rates()
            events_by_law[law] = {"frozen_reader": events, "broader_existence": broader}
        draws.append({
            "scorer_rank": rank,
            "scorer_actual_anchor_knot": cohorts[ARCHIVE_ANCHOR][rank],
            "inclusive_descendants_by_law_and_age": participation,
            "events_by_law": events_by_law,
        })
    return {
        "archive_original_draw": original["identifier"],
        "source_supports": source,
        "checks_by_law": {
            law: {
                "source_supports_k1_k3": len(source),
                "fresh_at_age_twenty_two": len(next(iter(records[22].values())).fresh),
                "cohort_sizes": list(map(len, cohorts)),
                "relay_reading": relay,
            } for law, (cohorts, records, _, relay) in law_records.items()
        },
        "seed": ARCHIVE_SEED,
        "weighting": "uniform individual births with replacement",
        "cohort_size": population,
        "anchor_age": ARCHIVE_ANCHOR,
        "followup_parent_steps": HORIZON,
        "literal_birth_cap": ARCHIVE_CAP,
        "summary_by_law": {law: summarize(draws, law) for law in LAWS},
        "draws": draws,
    }


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="Write a new receipt at this path.")
    args = parser.parse_args()
    fixture = load("explosive_literal_fixture", LITERAL_FIXTURE)
    result = {
        "paired_across_readers_and_laws": True,
        "simultaneous_binomial_cell_count": SIMULTANEOUS_CELLS,
        "hosts": {"partnered": partnered(fixture), "archive_00": archive(fixture)},
        "sha256": {
            str(path.relative_to(ROOT)): sha256(path.read_bytes()).hexdigest()
            for path in (HERE / "explosive.py", HERE / "deep.py", LITERAL_FIXTURE, LITERAL_OPERATOR,
                         PARTNER_PROOF / "proof.md", PARTNER_PROOF / "job.py", ARCHIVE_SOURCE,
                         RESEARCH / "explosive_preregistration.md", RESEARCH / "preregistration.md")
        },
    }
    raw = json.dumps(result, sort_keys=True, separators=(",", ":")) + "\n"
    if args.output:
        with args.output.open("x", encoding="utf-8") as receipt:
            receipt.write(raw)
    else:
        print(raw, end="")


if __name__ == "__main__":
    main()
