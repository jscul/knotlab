"""Rebuild the sampled parity growth and the two reader tests in Part C."""

import argparse
from collections import Counter, defaultdict
import gzip
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path
from random import Random
import resource
from time import perf_counter, process_time


HERE = Path(__file__).resolve().parent
STUDY = HERE.parent
CENSUS = STUDY.parent / "FORBID-EDITS-20261126-001" / "starts.json"
ARMS = ("ordinary", "one_fewer", "arity_floor")
SEED = 20261129
SAMPLE = 300
CHANGES = "largest e, middle read for changes"
UNREAD = "largest e, middle unread"


def start_supports(entry):
    count, shared, loose = entry
    owners = [(a, b) for a, b, multiplicity in shared for _ in range(multiplicity)]
    owners.extend((a,) for a, multiplicity in enumerate(loose) for _ in range(multiplicity))
    return [tuple(d for d, knots in enumerate(owners) if a in knots) for a in range(count)]


def holders_of(knots):
    holders = defaultdict(list)
    for i, support in enumerate(knots):
        assert len(support) == len(set(support))
        for d in support:
            holders[d].append(i)
    assert all(1 <= len(owners) <= 2 for owners in holders.values())
    return holders


def group_roster(knot_count, holders, members):
    meetings = [set() for _ in range(knot_count)]
    for owners in holders.values():
        if len(owners) == 2:
            a, b = owners
            meetings[a].add(b)
            meetings[b].add(a)
    pairs = [pair for pair in combinations(sorted(members), 2) if meetings[pair[0]] & meetings[pair[1]]]
    joins = {a: set() for a in members}
    for a, b in pairs:
        joins[a].add(b)
        joins[b].add(a)

    def maximal_joinable(group, remaining, passed):
        if not remaining and not passed:
            if len(group) >= 3 and not set.intersection(*(meetings[a] for a in group)):
                yield tuple(sorted(group))
            return
        pivot = max(remaining | passed, key=lambda a: (len(joins[a] & remaining), -a))
        for a in sorted(remaining - joins[pivot]):
            yield from maximal_joinable(group + (a,), joins[a] & remaining, joins[a] & passed)
            remaining.remove(a)
            passed.add(a)

    larger = sorted(maximal_joinable((), set(members), set()))
    covered = {pair for group in larger for pair in combinations(group, 2)}
    return larger + [pair for pair in pairs if pair not in covered]


def mask(distinctions):
    result = 0
    for d in distinctions:
        result |= 1 << d
    return result


def remainder(vector, pivots):
    while vector:
        least = vector & -vector
        if least not in pivots:
            break
        vector ^= pivots[least]
    return vector


def basis(vectors):
    pivots = {}
    for vector in vectors:
        vector = remainder(vector, pivots)
        if vector:
            pivots[vector & -vector] = vector
    return pivots


def step(knots, arm):
    holders = holders_of(knots)
    loose = defaultdict(list)
    for d, owners in sorted(holders.items()):
        if len(owners) == 1:
            loose[owners[0]].append(d)
    if not loose:
        return [], []

    parents = group_roster(len(knots), holders, loose)
    uses = Counter(a for group in parents for a in group)
    if any(uses[a] > len(ds) for a, ds in loose.items()):
        return [], []
    for a, ds in sorted(loose.items()):
        parents.extend((a,) for _ in range(len(ds) - uses[a]))
    payments = {a: iter(ds) for a, ds in loose.items()}
    inputs = [tuple(sorted(next(payments[a]) for a in group)) for group in parents]

    # A scratch round contains every planned birth before any receives a ration.
    provisional = knots + inputs
    groups = group_roster(len(provisional), holders_of(provisional), range(len(knots), len(provisional)))
    demand = Counter(a for group in groups for a in group)
    old_laws = basis(mask(support) for support in knots)
    first_fresh = max(holders) + 1
    births = []
    for i, support in enumerate(inputs, start=len(knots)):
        minimum = max(0, 3 - len(support))
        implied = remainder(mask(support), old_laws) == 0
        ordinary = demand[i] if implied else max(demand[i], minimum, 1)
        if arm == "ordinary":
            fresh = ordinary
        elif arm == "one_fewer":
            fresh = min(ordinary, max(minimum, ordinary - 1))
        else:
            fresh = min(ordinary, minimum)
        births.append(support + tuple(range(first_fresh, first_fresh + fresh)))
        # Retain the first fresh names of the ordinary proposal after cutting.
        first_fresh += ordinary
    return births, parents


def grow(start, arm):
    knots = start.copy()
    lineage = [frozenset({i}) for i in range(len(start))]
    completed = 0
    for _ in range(2):
        births, parents = step(knots, arm)
        if not births:
            break
        lineage.extend(frozenset().union(*(lineage[a] for a in group)) for group in parents)
        knots.extend(births)
        completed += 1
    return knots, lineage, completed


def laws_within(laws, middle):
    """Eliminate on the unread distinctions, retaining combinations that cancel there."""
    pivots = {}
    retained = []
    for law in laws:
        while outside := law & middle:
            least = outside & -outside
            if least not in pivots:
                pivots[least] = law
                break
            law ^= pivots[least]
        else:
            retained.append(law)
    return retained


def shared_pairs(laws, left, right, universe):
    """Count independent value-law projections modulo the annihilator of the changes."""
    read = (left | right) & universe
    left &= read
    retained_laws = laws_within(laws, universe ^ read)
    left_projections = [law & left for law in retained_laws]
    # With the middle read for changes, the retained laws annihilate the projected changes.
    changes = len(basis(retained_laws + left_projections)) - len(basis(retained_laws))
    # With the middle unread, the changes must avoid it, so every restricted law annihilates them.
    restricted = [law & read for law in laws]
    unread = len(basis(restricted + left_projections)) - len(basis(restricted))
    return changes, unread


def component_changes(holders, knot_count, left, right):
    """Cross-check the change count using incidence ranks from holder components."""
    middle = set(holders) - (left | right)

    def rank_on(distinctions):
        classes = list(range(knot_count + 1))
        joins = 0

        def leader(a):
            while classes[a] != a:
                a = classes[a]
            return a

        for d in distinctions:
            owners = holders[d]
            a = leader(owners[0])
            b = leader(owners[1] if len(owners) == 2 else knot_count)
            if a != b:
                classes[a] = b
                joins += 1
        return joins

    return rank_on(left | middle) + rank_on(right | middle) - rank_on(holders) - rank_on(middle)


def census_row(index, start, arm):
    knots, lineage, rounds = grow(start, arm)
    regions = [set() for _ in start]
    for support, origins in zip(knots, lineage, strict=True):
        if len(origins) == 1:
            regions[next(iter(origins))].update(support)

    pairs = [((a,), b) for a, b in combinations(range(len(start)), 2)]
    pairs.extend(((a, c), b) for a, c in combinations(range(len(start)), 2) for b in range(len(start)) if b not in (a, c))
    row = {
        "start": index, "arm": arm, "rounds": rounds, "pairs": len(pairs), "knots": len(knots),
        "separated pairs": 0, "pairs with e >= 1": 0, "pairs with e >= 2": 0, CHANGES: 0, UNREAD: 0,
    }
    frozen = row.copy()
    corruptions = Counter()
    witness = None
    holders = holders_of(knots)
    universe = mask(holders)
    laws = [mask(support) for support in knots]
    # The frozen program assigned bit positions in the string order of the recorded names.
    lexical = sorted(holders, key=str)
    lexical_bits = {d: 1 << bit for bit, d in enumerate(lexical)}
    lexical_universe = (1 << len(lexical)) - 1
    seen_pairs = set()

    def record(record_row, counts):
        changes, unread = counts
        record_row["separated pairs"] += 1
        record_row["pairs with e >= 1"] += changes >= 1
        record_row["pairs with e >= 2"] += changes >= 2
        record_row[CHANGES] = max(record_row[CHANGES], changes)
        record_row[UNREAD] = max(record_row[UNREAD], unread)

    for sources, b in pairs:
        left = set().union(*(regions[a] for a in sources))
        right = regions[b]
        a_mask, b_mask = mask(left), mask(right)
        if not left or not right or left & right or any(law & a_mask and law & b_mask for law in laws):
            continue
        seen_pairs.add(frozenset((frozenset(left), frozenset(right))))
        corrected_counts = shared_pairs(laws, a_mask, b_mask, universe)
        assert corrected_counts[0] == component_changes(holders, len(knots), left, right)
        assert corrected_counts[1] == 0
        record(row, corrected_counts)

        # Deliberately carry repeated names through the archival integer encoding.
        left_sum = sum(lexical_bits[d] for a in sources for d in regions[a])
        frozen_left = mask(d for bit, d in enumerate(lexical) if left_sum & (1 << bit))
        frozen_counts = corrected_counts
        if frozen_left != a_mask or left_sum & ~lexical_universe:
            corruptions["separated choices with a changed integer mask"] += 1
            corruptions["effective reader overlap"] += bool(frozen_left & b_mask)
            corruptions["bits carried past the available names"] += bool(left_sum & ~lexical_universe)
            frozen_counts = shared_pairs(laws, frozen_left, b_mask, universe)
            corruptions["changed conditioned shared-pair count"] += frozen_counts[0] != corrected_counts[0]
            corruptions["changed unread shared-pair count"] += frozen_counts[1] != corrected_counts[1]
            if witness is None and frozen_counts != corrected_counts:
                witness = {
                    "census index": index, "arm": arm, "rounds completed": rounds,
                    "start knot places": start, "final knot places": knots,
                    "first reader lineages": sources, "second reader lineage": b,
                    "first reader's intended distinctions": sorted(left),
                    "second reader's distinctions": sorted(right),
                    "repeated distinctions in the first reader": sorted(regions[sources[0]] & regions[sources[1]]),
                    "first reader's effective frozen distinctions": [d for d in lexical if frozen_left & (1 << d)],
                    "distinction order in the frozen mask": lexical,
                    "frozen integer mask": left_sum,
                    "corrected counts (change, unread)": corrected_counts,
                    "frozen counts (change, unread)": frozen_counts,
                }
        record(frozen, frozen_counts)

    corruptions["repeated separated choices of the same reader sets"] = row["separated pairs"] - len(seen_pairs)
    return row, frozen, corruptions, witness


def controls():
    results = []
    for expected in range(3):
        # Independent parity constraints give zero, one, or two shared pairs.
        joins = [0, 0] if expected == 0 else [1] * expected
        knots, left, right = [], set(), set()
        for i, joined in enumerate(joins):
            a0, a1, b0, b1, middle, other = range(6 * i, 6 * i + 6)
            knots.extend([(a0, a1, middle), (b0, b1, middle if joined else other)])
            left.update((a0, a1))
            right.update((b0, b1))
        holders = holders_of(knots)
        laws, left_mask, right_mask, universe = [mask(k) for k in knots], mask(left), mask(right), mask(holders)
        read_mask = left_mask | right_mask
        allowed = [s for s in range(universe + 1) if not s & ~universe and all((s & law).bit_count() % 2 == 0 for law in laws)]
        projected = {s & read_mask for s in allowed}
        # For the conditioned pure state each projection is equally weighted. The ratio
        # counts the common parity constraints from projections of the allowed assignments.
        private = len({s & left_mask for s in allowed}) * len({s & right_mask for s in allowed})
        assert private == len(projected) * (1 << expected)
        assert shared_pairs(laws, left_mask, right_mask, universe) == (expected, 0)
        assert component_changes(holders, len(knots), left, right) == expected
        results.append({"expected e with middle read for changes": expected, "allowed states": len(allowed),
                        "distinct joint projections": len(projected), "product of separate projection counts": private,
                        "e with middle unread": 0})
    return results


def archive_comparison(path, observed, require_complete):
    with gzip.open(path, "rt") as handle:
        actual_rows = [json.loads(line) for line in handle]
    actual = {(row["start"], row["arm"]): row for row in actual_rows}
    assert len(actual) == len(actual_rows)
    expected_keys = {(row["start"], row["arm"]) for row in observed}
    if require_complete:
        assert set(actual) == expected_keys
        assert [(row["start"], row["arm"]) for row in actual_rows] == [
            (row["start"], row["arm"]) for row in observed
        ]
    mismatches = []
    for row in observed:
        source = actual.get((row["start"], row["arm"]), {})
        if source != row:
            differing = {key: [row.get(key), source.get(key)] for key in sorted(row.keys() | source.keys())
                         if row.get(key) != source.get(key) or (key in row) != (key in source)}
            mismatches.append({"census index": row["start"], "arm": row["arm"], "rebuilt and archived": differing})
    return {"record": path.name, "sha256": sha256(path.read_bytes()).hexdigest(),
            "matched rows": len(observed) - len(mismatches), "compared rows": len(observed),
            "mismatches": mismatches}


def tally(rows, corrupted):
    result = {}
    for arm in ARMS:
        picked = [row for row in rows if row["arm"] == arm]
        result[arm] = {
            "starts": len(picked), "reader choices": sum(row["pairs"] for row in picked),
            "starts with separated readers": sum(row["separated pairs"] > 0 for row in picked),
            "separated reader choices": sum(row["separated pairs"] for row in picked),
            "starts with e >= 1 after middle changes": sum(row[CHANGES] >= 1 for row in picked),
            "starts with e >= 2 after middle changes": sum(row[CHANGES] >= 2 for row in picked),
            "reader choices with e >= 1 after middle changes": sum(row["pairs with e >= 1"] for row in picked),
            "reader choices with e >= 2 after middle changes": sum(row["pairs with e >= 2"] for row in picked),
            "starts with e >= 1 when middle unread": sum(row[UNREAD] >= 1 for row in picked),
            "completed rounds": dict(sorted(Counter(row["rounds"] for row in picked).items())),
        }
        if corrupted:
            result[arm]["unread false-positive census indices"] = [row["start"] for row in picked if row[UNREAD] >= 1]
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--limit", type=int, default=SAMPLE, choices=range(1, SAMPLE + 1), metavar="STARTS")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--pilot", type=Path, nargs="*", default=[])
    args = parser.parse_args()
    wall, cpu = perf_counter(), process_time()
    census_bytes = CENSUS.read_bytes()
    census = json.loads(census_bytes)
    assert len(census) == 7075
    indices = sorted(Random(SEED).sample(range(len(census)), SAMPLE))[:args.limit]
    controls_result = controls()
    rows, frozen = [], []
    counts = {arm: Counter() for arm in ARMS}
    witnesses = []
    for index in indices:
        start = start_supports(census[index])
        for arm in ARMS:
            corrected, broken, corruptions, witness = census_row(index, start, arm)
            rows.append(corrected)
            frozen.append(broken)
            counts[arm].update(corruptions)
            if witness and not any(item["arm"] == arm for item in witnesses):
                witnesses.append(witness)
    comparisons = [archive_comparison(STUDY / record, data, args.limit == SAMPLE) for record, data in (
        ("square_sample.jsonl.gz", rows), ("square_sample_frozen.jsonl.gz", frozen),
    )]
    pilots = []
    for pilot in args.pilot:
        prior = json.loads(pilot.read_text())
        pilots.append({"file": pilot.name, "start limit": prior["start limit"], **prior["run"],
                       "projected seconds for 300 starts": prior["run"]["wall seconds"] * SAMPLE / prior["start limit"]})
    result = {
        "start limit": args.limit, "full sample size": SAMPLE, "seed": SEED,
        "census": str(CENSUS.relative_to(STUDY.parent.parent)), "census size": len(census),
        "census sha256": sha256(census_bytes).hexdigest(),
        "weighting": "uniform over census entries drawn without replacement",
        "growth": "parity, at most two funded rounds under each arm",
        "controls": controls_result, "source comparisons": comparisons, "pilot projections": pilots,
        "corrected totals": tally(rows, corrupted=False), "frozen totals": tally(frozen, corrupted=True),
        "repeated-name effects on separated reader choices": counts, "first changed-pair witness per arm": witnesses,
        "run": {"wall seconds": perf_counter() - wall, "CPU seconds": process_time() - cpu,
                "peak resident KiB": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                "virtual memory cap KiB": resource.getrlimit(resource.RLIMIT_AS)[0] // 1024,
                "worker processes": 1, "calculation threads per worker": 1},
    }
    with args.output.open("w") as handle:
        # Keep full corrected and frozen rows available for comparisons with other readers.
        header = json.dumps(result, indent=2)[:-2]
        handle.write(header + ',\n  "rows": [\n')
        handle.write(",\n".join("    " + json.dumps({"corrected": row, "frozen": old})
                                  for row, old in zip(rows, frozen, strict=True)))
        handle.write("\n  ]\n}\n")
    print(json.dumps({"run": result["run"], "archive matches": [item["matched rows"] for item in comparisons]}))


if __name__ == "__main__":
    main()
