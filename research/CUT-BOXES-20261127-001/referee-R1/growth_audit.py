"""Reconstruct the recorded growth stages and check the scope of their counts."""

import argparse
from collections import Counter, defaultdict
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path
import random
import sys


HERE = Path(__file__).resolve().parent
RESEARCH = HERE.parent.parent
UPPER = RESEARCH / "UPPER-GROWN-20261127-001"
STARTS = RESEARCH / "FORBID-EDITS-20261126-001" / "starts.json"
sys.path.insert(0, str(RESEARCH / "NAE-LAYER-20261127-001" / "referee-R1"))
from growth_rule import advance, holders, supports_of


BOX_FIELDS = (
    "boxes",
    "boxes read",
    "upper missing exactly one",
    "a birth needed",
    "reads a born distinction",
)


def rows(path):
    return [json.loads(line) for line in path.read_text().splitlines()]


def start_number(record):
    prefix, number = record["start"].split()
    assert prefix == "census"
    return int(number)


def connected(owners, count):
    neighbours = [set() for _ in range(count)]
    for pair in owners.values():
        if len(pair) == 2:
            first, second = pair
            neighbours[first].add(second)
            neighbours[second].add(first)
    seen, pending = {0}, [0]
    while pending:
        more = neighbours[pending.pop()] - seen
        seen.update(more)
        pending.extend(more)
    return len(seen) == count


def scan_stage(supports):
    owners = holders(supports)
    assert connected(owners, len(supports))
    return {
        "distinctions": len(owners),
        "knots": len(supports),
        "loose distinctions": sum(len(owners_of_one) == 1 for owners_of_one in owners.values()),
        "three places at every knot": all(len(support) == 3 for support in supports),
    }


def ordinary_stages(supports):
    stages = [supports]
    stop = None
    for _ in range(2):
        nxt = advance(stages[-1])
        if nxt.status != "funded":
            stop = nxt.status
            break
        old = holders(stages[-1])
        new = holders(nxt.supports)
        assert nxt.supports[:len(stages[-1])] == stages[-1]
        assert all(birth.fresh for birth in nxt.births)
        paid = Counter(name for birth in nxt.births for name in birth.inputs)
        made = Counter(name for birth in nxt.births for name in birth.fresh)
        assert paid == Counter(name for name, own in old.items() if len(own) == 1)
        assert made == Counter(name for name, own in new.items() if len(own) == 1)
        assert not (made.keys() & old.keys())
        stages.append(nxt.supports)
    return stages, stop


def recount(starts, chosen, archive):
    by_scope = defaultdict(Counter)
    at_start = Counter()
    stops = Counter()
    box_fields = Counter({field: 0 for field in BOX_FIELDS})
    opportunity_starts = defaultdict(set)
    maxima = defaultdict(Counter)
    for number in chosen:
        reconstructed, stop = ordinary_stages(supports_of(starts[number]))
        at_start[starts[number][0]] += 1
        stops[len(reconstructed), stop or "round limit"] += 1
        observed = archive[number]["rounds"]
        assert len(observed) == len(reconstructed), (number, stop, observed)
        for turn, (record, supports) in enumerate(zip(observed, reconstructed, strict=True)):
            stage = scan_stage(supports)
            assert record["round"] == turn, (number, record)
            for field in ("distinctions", "knots"):
                assert record[field] == stage[field], (number, field, record, stage)
            search = "full" if stage["distinctions"] <= 19 else "local"
            assert record["search"] == search, (number, search, record)
            assert all(record[key] == 0 for key in BOX_FIELDS), (number, record)
            assert not record["examples"], (number, record)
            box_fields.update({key: record[key] for key in BOX_FIELDS})
            for scope in ("all", search, f"round {turn}", f"round {turn} {search}"):
                tally = by_scope[scope]
                tally["stages"] += 1
                tally["closed stages"] += stage["loose distinctions"] == 0
                tally["stages with a birth"] += turn > 0
                tally["stages with at least 12 distinctions"] += stage["distinctions"] >= 12
                tally["stages with at least 12 knots"] += stage["knots"] >= 12
                tally["stages with at least 8 recorded bonds"] += record["bonds"] >= 8
                opportunity = stage["distinctions"] >= 12 and record["bonds"] >= 8
                tally["passes both necessary counts"] += opportunity
                tally["both necessary counts with a birth"] += opportunity and turn > 0
                tally["both necessary counts with at least 12 knots"] += opportunity and stage["knots"] >= 12
                tally["stages with all knots three-place"] += stage["three places at every knot"]
                tally["recorded bonds"] += record["bonds"]
                maxima[scope]["distinctions"] = max(maxima[scope]["distinctions"], stage["distinctions"])
                maxima[scope]["knots"] = max(maxima[scope]["knots"], stage["knots"])
                maxima[scope]["recorded bonds"] = max(maxima[scope]["recorded bonds"], record["bonds"])
                if opportunity:
                    opportunity_starts[scope].add(number)

    return {
        "starts by number of knots": at_start,
        "round stops": {f"after {length} stages, {status}": count for (length, status), count in stops.items()},
        "coverage": {scope: {**tally, "distinct starts passing both counts": len(opportunity_starts[scope]),
                             "maxima": maxima[scope]}
                     for scope, tally in by_scope.items()},
        "box field sums from records": box_fields,
    }


def cut_round(supports, law):
    proposal = advance(supports)
    if proposal.status != "funded":
        return proposal.status, supports, ()
    fresh = []
    for birth in proposal.births:
        ordinary = len(birth.fresh)
        floor = max(0, 3 - len(birth.parents))
        count = max(floor, ordinary - 1) if law == "A129" else floor
        assert 0 <= count <= ordinary
        fresh.append(count)
    new_supports = supports + tuple(
        birth.inputs + birth.fresh[:count] for birth, count in zip(proposal.births, fresh, strict=True)
    )
    assert scan_stage(new_supports)["loose distinctions"] == sum(fresh)
    return "funded", new_supports, tuple(fresh)


def cut_census(starts, chosen):
    results = {}
    for law in ("A129", "A130"):
        counts = Counter()
        closed = []
        for number in chosen:
            supports = supports_of(starts[number])
            for turn in (1, 2):
                status, supports, fresh = cut_round(supports, law)
                counts[f"attempts in round {turn}"] += 1
                counts[f"round {turn} {status}"] += 1
                if status != "funded":
                    break
                counts[f"round {turn} births"] += len(fresh)
                counts[f"round {turn} births with no fresh distinction"] += fresh.count(0)
                if any(fresh):
                    continue
                stage = scan_stage(supports)
                closed.append({"start": number, "round": turn, "supports": supports, **stage})
                break
        results[law] = {"counts": counts, "newly closed stages": closed}
    return results


def cubic_supports(record):
    by_knot = [[] for _ in range(record["points"])]
    for distinction, (first, second) in enumerate(record["links"]):
        by_knot[first].append(distinction)
        by_knot[second].append(distinction)
    return tuple(map(tuple, by_knot))


def reverse_closure(records):
    """Test each candidate last cohort of the 12-knot positive records."""
    counts = Counter()
    witnesses = defaultdict(list)
    for case, record in records:
        full = cubic_supports(record)
        counts["systems processed"] += 1
        assert scan_stage(full)["loose distinctions"] == 0
        target = Counter(full)
        for size in range(1, len(full)):
            for remove in combinations(range(len(full)), size):
                if len({d for index in remove for d in full[index]}) != 3 * size:
                    continue
                counts["candidate cohorts with no shared distinction"] += 1
                old = tuple(row for index, row in enumerate(full) if index not in remove)
                old_owners = holders(old)
                if not connected(old_owners, len(old)):
                    continue
                counts["candidate cohorts with connected predecessor"] += 1
                proposal = advance(old)
                if proposal.status != "funded":
                    counts[f"proposal {proposal.status}"] += 1
                    continue
                counts["proposal funded"] += 1
                old_owner = {name: owners[0] for name, owners in old_owners.items() if len(owners) == 1}
                erased_by_parents = defaultdict(list)
                for i in remove:
                    erased_by_parents[tuple(sorted(old_owner[x] for x in full[i]))].append(full[i])
                wanted = Counter({parents: len(erased) for parents, erased in erased_by_parents.items()})
                if Counter(birth.parents for birth in proposal.births) != wanted:
                    continue
                counts["matches erased supports"] += 1
                # Old loose distinctions of one holder are interchangeable. Compare
                # parent rosters and then establish the actual within-holder relabeling.
                rename = {}
                for birth in proposal.births:
                    erased = erased_by_parents[birth.parents].pop()
                    assert len(set(birth.parents)) == len(birth.parents)
                    desired = {old_owner[x]: x for x in erased}
                    rename.update((x, desired[old_owner[x]]) for x in birth.inputs)
                assert set(rename) == set(rename.values()) == set(old_owner)
                for law in ("A129", "A130"):
                    _, regrown, fresh = cut_round(old, law)
                    if not any(fresh):
                        renamed = tuple(tuple(sorted(rename.get(x, x) for x in row)) for row in regrown)
                        assert Counter(renamed) == target
                        witnesses[law].append({"record": case, "knots": len(full), "erased knot indices": remove,
                                               "old supports": old, "regrown supports": regrown,
                                               "regrown supports renamed within each old holder": renamed,
                                               "recorded boxes in restored system": record["boxes"]})
    return {"counts": counts, "witnesses": witnesses}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--limit", type=int)
    parser.add_argument("--reverse-limit", type=int)
    args = parser.parse_args()
    starts = json.loads(STARTS.read_text())
    assert len(starts) == 7075
    population = list(range(len(starts)))
    pilot_files = [UPPER / "pilot" / name for name in ("p10.jsonl", "p3.jsonl")]
    pilot = set(random.Random(1).sample(population, 10))
    assert pilot == set(map(start_number, rows(pilot_files[0])))
    chosen = sorted(random.Random(20261128).sample([n for n in population if n not in pilot], 1000))
    other_pilot = tuple(map(start_number, rows(pilot_files[1])))
    assert not set(chosen).intersection(other_pilot)
    source_files = sorted((UPPER / "out").glob("census_*.jsonl"))
    assert len(source_files) == 8
    archive = {}
    for index, path in enumerate(source_files):
        shard = rows(path)
        assert path.name == f"census_{index}.jsonl"
        assert list(map(start_number, shard)) == chosen[index::8], path
        archive.update((start_number(row), row) for row in shard)
    closed_files = sorted((UPPER / "out").glob("cubic_*.jsonl"))
    assert len(closed_files) == 12
    closed = [(f"{path.name}:{j}", row) for path in closed_files for j, row in enumerate(rows(path), 1)]
    assert Counter(row["points"] for _, row in closed) == {4: 1, 6: 2, 8: 5, 10: 19, 12: 85}
    positives = [(case, row) for case, row in closed if row["boxes"]]
    comparison = [(case, row) for case, row in closed if not row["boxes"]]
    assert len(positives) == 49
    result = {
        "sample": {"archive starts": len(starts), "excluded pilot": sorted(pilot), "seed": 20261128,
                   "additional pilot starts absent from the sample": other_pilot,
                   "matched roster, including order in each shard": len(archive), "reconstructed starts": len(chosen[:args.limit])},
        "input sha256": {str(path.relative_to(RESEARCH)): sha256(path.read_bytes()).hexdigest()
                         for path in [STARTS, *pilot_files, *source_files, *closed_files]},
        "ordinary": recount(starts, chosen[:args.limit], archive),
        "fresh-count cuts on the same starts": cut_census(starts, chosen[:args.limit]),
        "fresh-count cuts from a constructed predecessor": {
            "systems with a recorded box": reverse_closure(positives[:args.reverse_limit]),
            "systems with no recorded box": reverse_closure(comparison[:args.reverse_limit]),
        },
    }
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
