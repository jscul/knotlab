"""Replay Part C with separation by the canonical knot test on named distinctions."""

import argparse
from collections import Counter
from itertools import combinations, islice, product
import json
from pathlib import Path
from random import Random
import resource
from time import perf_counter

from part_c import ARMS, CENSUS, SAMPLE, SEED, basis, component_changes, grow, holders_of, mask, shared_pairs, start_supports


CONTROL_COUNT = 8**5
MAX_EXPLICIT_DISTINCTIONS = 22
MAX_EXPLICIT_LAWS = 16
STATS = ("choices", "changes >= 1", "changes >= 2", "unread >= 1", "unread >= 2")
PREDICATES = ("no listed law holds both", "no canonical knot holds both")


def generator(laws, names):
    """Use each free distinction in turn to generate an allowed change."""
    pivots = basis(laws)
    equations = sorted(pivots.items(), reverse=True)
    changes = []
    for d in names:
        free = 1 << d
        if free in pivots:
            continue
        change = free
        for pivot, law in equations:
            if (change & law).bit_count() % 2:
                change |= pivot
        assert all((change & law).bit_count() % 2 == 0 for law in laws)
        changes.append(change)
    assert len(changes) + len(pivots) == len(names)
    columns = {d: mask(i for i, x in enumerate(changes) if x & (1 << d)) for d in names}
    return changes, columns


def components(columns):
    """Keep basis-column names through elimination and join every fundamental circuit."""
    leaders = {d: d for d in columns}
    pivots = {}
    circuits = []

    def leader(d):
        while leaders[d] != d:
            d = leaders[d]
        return d

    for d, value in columns.items():
        support = frozenset({d})
        while value and value & -value in pivots:
            pivot_col, pivot_support = pivots[value & -value]
            value ^= pivot_col
            support ^= pivot_support
        if value:
            pivots[value & -value] = value, support
        else:
            circuits.append(sorted(support))
            for other in support:
                leaders[leader(other)] = leader(d)
    return {d: leader(d) for d in columns}, circuits


def in_a_canonical_knot(columns, components_of, a, b):
    # Zero columns are singleton circuits. Equal nonzero columns already form a
    # two-distinction circuit. For other pairs the matroid component criterion applies.
    return columns[a] != 0 and columns[b] != 0 and columns[a] != columns[b] and components_of[a] == components_of[b]


def minimal_supports(candidates):
    supports = []
    for candidate in sorted(candidates, key=int.bit_count):
        if not any(candidate & support == support for support in supports):
            supports.append(candidate)
    return supports


def exhaustive_control(limit):
    labels = range(5)
    pair_masks = [(a, b, (1 << a) | (1 << b)) for a, b in combinations(labels, 2)]
    sums = [0] * (1 << len(labels))
    features = Counter()
    for values in islice(product(range(8), repeat=len(labels)), limit):
        columns = dict(zip(labels, values, strict=True))
        membership, _ = components(columns)
        zeros = []
        for support in range(1, len(sums)):
            least = support & -support
            sums[support] = values[least.bit_length() - 1] ^ sums[support ^ least]
            if not sums[support]:
                zeros.append(support)
        knots = [support for support in minimal_supports(zeros) if support.bit_count() >= 3]
        for a, b, pair in pair_masks:
            assert in_a_canonical_knot(columns, membership, a, b) == any(k & pair == pair for k in knots)
        nonzero = [v for v in values if v]
        features["with zero columns"] += 0 in values
        features["with parallel nonzero columns"] += len(set(nonzero)) < len(nonzero)
        features["with three or more distinctions in a knot"] += bool(knots)
    return {"matrices checked": limit, "column pairs checked": limit * len(pair_masks), **features}


def start_rows(index, start, arm, witnesses):
    knots, lineage, rounds = grow(start, arm)
    holders = holders_of(knots)
    names = sorted(holders)
    universe = mask(names)
    laws = [mask(knot) for knot in knots]
    changes_basis, columns = generator(laws, names)
    belonging, circuits = components(columns)
    regions = [set() for _ in start]
    for support, origins in zip(knots, lineage, strict=True):
        if len(origins) == 1:
            regions[next(iter(origins))].update(support)
    origins = range(len(start))
    choices = [((a,), b) for a, b in combinations(origins, 2)]
    choices.extend(((a, c), b) for a, c in combinations(origins, 2) for b in origins if b not in (a, c))
    tallies = {kind: Counter() for kind in (*PREDICATES, "both", "listed only", "canonical only")}
    candidates = Counter()
    for sources, b in choices:
        left = set().union(*(regions[a] for a in sources))
        right = regions[b]
        if not left or not right or left & right:
            candidates["overlapping or empty"] += 1
            continue
        a_mask, b_mask = mask(left), mask(right)
        listed = not any(law & a_mask and law & b_mask for law in laws)
        canonical = not any(in_a_canonical_knot(columns, belonging, a, d) for a in left for d in right)
        kinds = []
        if listed:
            kinds.append(PREDICATES[0])
        if canonical:
            kinds.append(PREDICATES[1])
        if not kinds:
            candidates["neither"] += 1
            continue
        kinds.append("both" if listed and canonical else "listed only" if listed else "canonical only")
        conditioned, unread = shared_pairs(laws, a_mask, b_mask, universe)
        assert conditioned == component_changes(holders, len(knots), left, right)
        for kind in kinds:
            tally = tallies[kind]
            tally.update(dict(zip(STATS, (1, conditioned >= 1, conditioned >= 2, unread >= 1, unread >= 2), strict=True)))
        for label, threshold in (
            ("canonical separation and changes >= 2", canonical and conditioned >= 2),
            ("canonical separation and unread >= 2", canonical and unread >= 2),
            ("canonical separation and unread >= 1", canonical and unread >= 1),
            ("conditioned shared pair excluded by canonical separation", listed and not canonical and conditioned >= 1),
            ("canonical separation despite a listed law holding both", canonical and not listed),
        ):
            if not threshold:
                continue
            order = (len(names), len(knots), index, ARMS.index(arm), sources, b)
            if label in witnesses and order >= witnesses[label][0]:
                continue
            witnesses[label] = order, {
                "census index": index, "arm": arm, "funded rounds": rounds, "start knot places": start,
                "final knot places": knots, "left reader lineages": sources, "right reader lineage": b,
                "left reader distinctions": sorted(left), "right reader distinctions": sorted(right),
                "middle distinctions": sorted(set(names) - left - right),
                "a listed law holds distinctions of both readers": not listed,
                "a canonical knot holds distinctions of both readers": not canonical,
                "e, middle read for changes": conditioned, "e, middle unread": unread,
                "allowed changes basis": [list(as_distinctions(x)) for x in changes_basis],
                "basis-column components": [sorted(d for d in belonging if belonging[d] == root)
                                            for root in sorted(set(belonging.values()))],
                "fundamental circuits": circuits,
                "cross-reader pairs of equal nonzero columns": [[a, d] for a in sorted(left) for d in sorted(right)
                                                                if columns[a] != 0 and columns[a] == columns[d]],
            }
    assert len(choices) == candidates.total() + sum(tallies[kind]["choices"] for kind in ("both", "listed only", "canonical only"))
    return {"census index": index, "arm": arm, "funded rounds": rounds, "knots": len(knots), "candidate choices": len(choices),
            "disjoint choices accepted by neither predicate": candidates["neither"],
            "overlapping or empty choices": candidates["overlapping or empty"], "tallies": tallies}


def as_distinctions(value):
    while value:
        least = value & -value
        yield least.bit_length() - 1
        value ^= least


def direct_witness_check(witness):
    names = sorted({d for knot in witness["final knot places"] for d in knot})
    positions = {d: i for i, d in enumerate(names)}
    rules = [mask(positions[d] for d in knot) for knot in witness["final knot places"]]
    a = mask(positions[d] for d in witness["left reader distinctions"])
    b = mask(positions[d] for d in witness["right reader distinctions"])
    readers = a | b
    if len(rules) > MAX_EXPLICIT_LAWS:
        return {"direct law sum enumeration": "not run", "listed laws": len(rules)}
    # Enumerate sums of the listed laws directly, with no allowed-change generator.
    sums = {0: 0}
    for i, rule in enumerate(rules):
        sums.update({z ^ rule: support | (1 << i) for z, support in sums.items()})
    minimal = minimal_supports(sums.keys() - {0})
    canonical = [support for support in minimal if support.bit_count() >= 3]
    crossing = [support for support in canonical if support & a and support & b]
    assert bool(crossing) == witness["a canonical knot holds distinctions of both readers"]
    report = {
        "distinctions": len(names), "law sums enumerated": len(sums),
        "number of canonical knots of size >= 3": len(canonical),
    }
    crossing_support = min(crossing, key=lambda z: (z.bit_count(), z), default=0)
    if crossing_support:
        assert sum(law & crossing_support == law for law in sums) == 2
        report["crossing canonical knot"] = [names[i] for i in as_distinctions(crossing_support)]
        report["listed laws summed to obtain the crossing knot (indices from zero)"] = list(
            as_distinctions(sums[crossing_support])
        )
    if len(names) > MAX_EXPLICIT_DISTINCTIONS:
        report["direct allowed-state enumeration"] = "not run"
        return report

    allowed = [x for x in range(1 << len(names)) if all((x & rule).bit_count() % 2 == 0 for rule in rules)]
    z_reads = [z for z in sums if not z & ~readers]

    def answer_profiles(xs):
        return {tuple((x & z & a).bit_count() % 2 for z in z_reads) for x in xs}

    conditioned = answer_profiles({x & readers for x in allowed})
    unread = answer_profiles(x for x in allowed if not x & ~readers)
    assert len(conditioned) == 1 << witness["e, middle read for changes"]
    assert len(unread) == 1 << witness["e, middle unread"]
    report.update({"allowed states enumerated": len(allowed), "number of answer profiles after middle changes": len(conditioned),
                   "number of unread answer profiles": len(unread)})
    if crossing_support:
        places = list(as_distinctions(crossing_support))
        projection = {"".join(str((x >> i) & 1) for i in places) for x in allowed}
        assert projection == {"".join(map(str, row)) for row in product(range(2), repeat=len(places)) if sum(row) % 2 == 0}
        report["crossing knot projected allowed states"] = sorted(projection)
    return report


def summary(rows):
    totals = {}
    for arm in ARMS:
        cohort = [row for row in rows if row["arm"] == arm]
        totals[arm] = {}
        for kind in (*PREDICATES, "both", "listed only", "canonical only"):
            counts = [row["tallies"][kind] for row in cohort]
            totals[arm][kind] = {stat: {"reader choices": sum(row[stat] for row in counts),
                                       "starts": sum(row[stat] > 0 for row in counts)} for stat in STATS}
        totals[arm]["canonical positive starts"] = {
            stat: [row["census index"] for row in cohort if row["tallies"][PREDICATES[1]][stat]]
            for stat in STATS if stat != "choices"
        }
    return totals


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--limit", type=int, default=SAMPLE)
    parser.add_argument("--controls", type=int, default=CONTROL_COUNT)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--pilot", type=Path)
    args = parser.parse_args()
    assert 1 <= args.limit <= SAMPLE and 1 <= args.controls <= CONTROL_COUNT

    start_time = perf_counter()
    controls = exhaustive_control(args.controls)
    control_seconds = perf_counter() - start_time
    growth_started = perf_counter()
    census = json.loads(CENSUS.read_text())
    indices = sorted(Random(SEED).sample(range(len(census)), SAMPLE))[:args.limit]
    witnesses = {}
    rows = [start_rows(index, start_supports(census[index]), arm, witnesses) for index in indices for arm in ARMS]
    original = json.loads((Path(__file__).parent / "part_c.json").read_text())
    for row, archived in zip(rows, original["rows"]):
        recorded = archived["corrected"]
        assert (row["census index"], row["arm"], row["funded rounds"], row["knots"], row["candidate choices"]) == (
            recorded["start"], recorded["arm"], recorded["rounds"], recorded["knots"], recorded["pairs"]
        )
        tally = row["tallies"][PREDICATES[0]]
        assert tuple(tally[stat] for stat in STATS) == (recorded["separated pairs"], recorded["pairs with e >= 1"],
                                                      recorded["pairs with e >= 2"], 0, 0)
    growth_seconds = perf_counter() - growth_started
    witness_started = perf_counter()
    for _, witness in witnesses.values():
        witness["direct check"] = direct_witness_check(witness)
    witness_seconds = perf_counter() - witness_started
    totals = summary(rows)
    result = {
        "growth arms": ARMS, "census weighting": "uniform over census entries, without replacement",
        "seed": SEED, "start limit": args.limit, "full sample size": SAMPLE, "original corrected rows matched": len(rows),
        "exhaustive generator controls": controls, "totals": totals,
        "smallest witnesses": {condition: witness for condition, (_, witness) in witnesses.items()},
        "run": {"control seconds": control_seconds, "sample seconds": growth_seconds, "witness seconds": witness_seconds,
                "total checked seconds": perf_counter() - start_time,
                "peak resident KiB": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                "virtual memory cap KiB": resource.getrlimit(resource.RLIMIT_AS)[0] // 1024,
                "processes": 1, "calculation threads": 1},
    }
    if args.pilot:
        pilot = json.loads(args.pilot.read_text())
        result["pilot projection"] = {
            "file": args.pilot.name, "controls seconds": pilot["run"]["control seconds"] * CONTROL_COUNT / pilot["exhaustive generator controls"]["matrices checked"],
            "sample seconds": pilot["run"]["sample seconds"] * SAMPLE / pilot["start limit"],
            "witness seconds in pilot": pilot["run"]["witness seconds"],
        }
    with args.output.open("w") as handle:
        header = json.dumps(result, indent=2)[:-2]
        handle.write(header + ',\n  "rows": [\n')
        handle.write(",\n".join("    " + json.dumps(row) for row in rows))
        handle.write("\n  ]\n}\n")
    print(json.dumps({arm: total[PREDICATES[1]] for arm, total in totals.items()}))
    print(json.dumps(result["run"]))


if __name__ == "__main__":
    main()
