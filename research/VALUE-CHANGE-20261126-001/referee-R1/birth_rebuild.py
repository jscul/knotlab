"""Replay the Part A census sample and evaluate the signed reading of rule R."""

import argparse
from collections import Counter, defaultdict
from functools import reduce
import gzip
from itertools import combinations, product
import json
from operator import xor
from pathlib import Path
from random import Random


HERE = Path(__file__).resolve().parent
STUDY = HERE.parent
CENSUS = STUDY.parent / "FORBID-EDITS-20261126-001" / "starts.json"
SEED = 20261128
SAMPLE_SIZE = 300
ROUNDS = 6


def start_supports(entry):
    count, shared, loose = entry
    holders = [(u, v) for u, v, multiplicity in shared for _ in range(multiplicity)]
    holders.extend((u,) for u, multiplicity in enumerate(loose) for _ in range(multiplicity))
    return [tuple(d for d, group in enumerate(holders) if u in group) for u in range(count)]


def ownership(knots):
    owners = defaultdict(set)
    for u, places in enumerate(knots):
        assert len(places) == len(set(places))
        for d in places:
            owners[d].add(u)
    assert all(1 <= len(group) <= 2 for group in owners.values())
    return owners


def candidate_groups(knot_count, owners, eligible):
    meetings = [set() for _ in range(knot_count)]
    for group in owners.values():
        if len(group) == 2:
            u, v = group
            meetings[u].add(v)
            meetings[v].add(u)
    pairs = [(u, v) for u, v in combinations(sorted(eligible), 2) if meetings[u] & meetings[v]]
    candidates = {u: set() for u in eligible}
    for u, v in pairs:
        candidates[u].add(v)
        candidates[v].add(u)

    def maximal_sets(chosen, remaining, earlier):
        if not remaining and not earlier:
            yield tuple(sorted(chosen))
            return
        pivot = max(remaining | earlier, key=lambda u: (len(remaining & candidates[u]), -u))
        for u in sorted(remaining - candidates[pivot]):
            yield from maximal_sets(chosen | {u}, remaining & candidates[u], earlier & candidates[u])
            remaining.remove(u)
            earlier.add(u)

    larger = sorted(
        group for group in maximal_sets(set(), set(eligible), set())
        if len(group) >= 3 and not set.intersection(*(meetings[u] for u in group))
    )
    represented = {pair for group in larger for pair in combinations(group, 2)}
    return larger + [pair for pair in pairs if pair not in represented]


def funding(knots, owners):
    available = defaultdict(list)
    for d, group in sorted(owners.items()):
        if len(group) == 1:
            available[next(iter(group))].append(d)
    if not available:
        return "closed", [], []

    groups = candidate_groups(len(knots), owners, available)
    demand = Counter(u for group in groups for u in group)
    if any(demand[u] > len(ds) for u, ds in available.items()):
        return "stalled", [], []
    for u, ds in sorted(available.items()):
        groups.extend((u,) for _ in range(len(ds) - demand[u]))
    by_holder = {u: iter(ds) for u, ds in available.items()}
    inputs = [tuple(sorted(next(by_holder[u]) for u in group)) for group in groups]
    assert Counter(d for ds in inputs for d in ds) == Counter(d for ds in available.values() for d in ds)
    return "growing", groups, inputs


def mask(indices):
    return reduce(int.__or__, (1 << i for i in indices), 0)


def eliminate(vector, basis):
    while vector and vector.bit_length() in basis:
        vector ^= basis[vector.bit_length()]
    return vector


def append_births(knots, owners, inputs):
    first = len(knots)
    newborn = range(first, first + len(inputs))
    provisional = knots + inputs
    provisional_owners = ownership(provisional)
    next_groups = candidate_groups(len(provisional), provisional_owners, newborn)
    demand = Counter(u for group in next_groups for u in group)

    basis = {}
    for support in knots:
        remainder = eliminate(mask(support), basis)
        if remainder:
            basis[remainder.bit_length()] = remainder

    first_fresh = max(owners) + 1
    next_knots = list(knots)
    for u, ds in zip(newborn, inputs, strict=True):
        implied = eliminate(mask(ds), basis) == 0
        fresh_count = demand[u] if implied else max(demand[u], 3 - len(ds), 1)
        next_knots.append(ds + tuple(range(first_fresh, first_fresh + fresh_count)))
        first_fresh += fresh_count
    return next_knots


def grow(knots):
    rounds = [0] * len(knots)
    parents = [set() for _ in knots]
    for round_number in range(1, ROUNDS + 1):
        owners = ownership(knots)
        status, groups, inputs = funding(knots, owners)
        if status != "growing":
            break
        parents.extend(set(group) for group in groups)
        rounds.extend([round_number] * len(groups))
        knots = append_births(knots, owners, inputs)
    return knots, rounds, parents, funding(knots, ownership(knots))[0]


def pair_sign(first, second):
    x, z = first
    x_other, z_other = second
    return ((x & z_other).bit_count() + (z & x_other).bit_count()) % 2


def signed_supports(knots, owners):
    distinctions = {
        d: (1 << d, mask(f for f in owners if f < d and not holders & owners[f]))
        for d, holders in owners.items()
    }
    laws = [
        (mask(support), reduce(xor, (distinctions[d][1] for d in support), 0))
        for support in knots
    ]
    return distinctions, laws


def predicted_sign(u, v, rounds, parents, children, knots):
    left, right = len(knots[u]), len(knots[v])
    gap = rounds[v] - rounds[u]
    if gap == 0:
        common = len(parents[u] & parents[v]) + len(children[u] & children[v])
        return "one round", (left * right - common) % 2
    if gap == 1 and u in parents[v]:
        return "parent and child", ((left - 1) * (right - 1)) % 2
    if gap == 2:
        return "two rounds apart", (left * right - len(children[u] & parents[v])) % 2
    if gap == 1:
        return "one round apart, not parent and child", (left * right) % 2
    return "three or more apart", (left * right) % 2


def six_round_witness(knots, rounds, parents, settled_failures):
    chain = [rounds.index(6)]
    while rounds[chain[-1]] > 1:
        chain.append(min(parents[chain[-1]]))
    chain.reverse()
    assert [rounds[u] for u in chain] == list(range(1, 7))
    sizes = [len(knots[u]) for u in chain]
    ends = ((0, 1), (4, 5))
    both_even = [end for end in ends if all(sizes[i] % 2 == 0 for i in end)]
    if both_even:
        positions = both_even[0]
    else:
        positions = tuple(next(i for i in end if sizes[i] % 2) for end in ends)
    pair = tuple(chain[i] for i in positions)
    return {
        "chain": chain, "place counts": sizes, "predicted failing pair": pair,
        "settled failure confirmed": pair in settled_failures,
    }


def audit(index, knots):
    knots, rounds, parents, end = grow(knots)
    owners = ownership(knots)
    loose = {d for d, hs in owners.items() if len(hs) == 1}
    has_loose = {u for u, support in enumerate(knots) if loose.intersection(support)}
    distinctions, laws = signed_supports(knots, owners)
    children = [set() for _ in knots]
    for v, prev in enumerate(parents):
        for u in prev:
            children[u].add(v)

    totals = Counter()
    settled_failures = set()
    disagreements = []
    failed_birth_pairs = Counter()
    for u, v in combinations(range(len(knots)), 2):
        if end == "growing" and {u, v} <= has_loose:
            totals["open"] += 1
            continue
        sign = pair_sign(laws[u], laws[v])
        if sign:
            settled_failures.add((u, v))
        if rounds[u] == 0:
            totals["a start knot (not covered)"] += 1
            continue
        name, predicted = predicted_sign(u, v, rounds, parents, children, knots)
        totals[f"{name} / pairs"] += 1
        totals[f"{name} / formula right"] += int(sign == predicted)
        if sign:
            failed_birth_pairs[name] += 1
        if sign != predicted:
            disagreements.append({"knots": [u, v], "case": name, "observed": sign, "predicted": predicted})

    row = {
        "start": index, "end": end, "rounds": rounds[-1], "knots": len(knots),
        "settled failing pairs": len(settled_failures), **totals,
    }
    witness = six_round_witness(knots, rounds, parents, settled_failures) if rounds[-1] == ROUNDS else None
    closer = None
    if end == "closed" and not settled_failures:
        changes = [sorted(d for d, value in distinctions.items() if pair_sign(value, law)) for law in laws]
        closer = {
            "start": index,
            "knots": len(knots),
            "lists that are allowed changes": sum(
                all(len(set(support).intersection(ds)) % 2 == 0 for support in knots) for ds in changes
            ),
            "empty lists": changes.count([]),
            "supports": knots,
            "non-commuting distinctions by knot": changes,
        }
    return row, disagreements, failed_birth_pairs, witness, closer


def parity_sequences(length):
    return [
        "".join("O" if odd else "E" for odd in word)
        for word in product((0, 1), repeat=length)
        if all(first or second for first, second in zip(word, word[1:]))
        and not any(word[i] and word[j] for i, j in combinations(range(length), 2) if j - i >= 3)
    ]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--limit", type=int, default=SAMPLE_SIZE, choices=range(1, SAMPLE_SIZE + 1), metavar="N")
    args = parser.parse_args()
    entries = json.loads(CENSUS.read_text())
    assert len(entries) == 7075
    sampled = sorted(Random(SEED).sample(range(len(entries)), SAMPLE_SIZE))

    rows = []
    formula_disagreements = {}
    cases = Counter()
    failed_birth_pairs = Counter()
    witnesses = {}
    closers = []
    for index in sampled[:args.limit]:
        row, disagreements, failures, witness, closer = audit(index, start_supports(entries[index]))
        rows.append(row)
        cases.update({key: value for key, value in row.items() if " / " in key})
        failed_birth_pairs.update(failures)
        if disagreements:
            formula_disagreements[index] = disagreements
        if witness:
            witnesses[index] = witness
        if closer:
            closers.append(closer)

    with gzip.open(STUDY / "check1_rows.jsonl.gz", "rt") as stream:
        archive_rows = {row["start"]: row for row in map(json.loads, stream)}
    archive_mismatches = [
        {"rebuild": row, "archive": archive_rows.get(row["start"])}
        for row in rows if row != archive_rows.get(row["start"])
    ]
    archive_roster_matches = sorted(archive_rows) == sampled
    recorded_lists = {
        row["start"]: row for row in map(json.loads, (STUDY / "check3_out.txt").read_text().splitlines())
        if "start" in row
    }
    compared_closer_keys = ("start", "knots", "lists that are allowed changes", "empty lists")
    closer_mismatches = [
        {"rebuild": {key: row[key] for key in compared_closer_keys}, "archive": recorded_lists.get(row["start"])}
        for row in closers
        if {key: row[key] for key in compared_closer_keys} != recorded_lists.get(row["start"])
    ]
    archived_closer_indices = set(sampled[:args.limit]).intersection(recorded_lists)
    closer_roster_matches = {row["start"] for row in closers} == archived_closer_indices
    totals = {
        "starts": len(rows),
        "ends": Counter(row["end"] for row in rows),
        "largest structure (knots)": max(row["knots"] for row in rows),
        "settled pairs of births": sum(value for key, value in cases.items() if key.endswith(" / pairs")),
        "open pairs": sum(row.get("open", 0) for row in rows),
        "settled pairs involving a start knot": sum(row.get("a start knot (not covered)", 0) for row in rows),
        "any settled failure": sum(row["settled failing pairs"] > 0 for row in rows),
        "reached six birth rounds": sum(row["rounds"] == ROUNDS for row in rows),
        "six-round chain witnesses": sum(row["settled failure confirmed"] for row in witnesses.values()),
        "closed with commuting knots": len(closers),
        "closer knots": sum(row["knots"] for row in closers),
        "closer lists that are allowed changes": sum(row["lists that are allowed changes"] for row in closers),
        "closer empty lists": sum(row["empty lists"] for row in closers),
        "archive roster matches": archive_roster_matches,
        "rebuilt rows identical to archive": len(rows) - len(archive_mismatches),
        "closer roster matches": closer_roster_matches,
        "rebuilt closer counts identical to archive": len(closers) - len(closer_mismatches),
    }
    result = {
        "census size": len(entries), "seed": SEED, "summary": totals, "case counts": cases,
        "anticommuting settled birth pairs by case": failed_birth_pairs,
        "parity sequences passing the two chain conditions": {n: parity_sequences(n) for n in (5, 6)},
        "formula disagreements": formula_disagreements, "archive mismatches": archive_mismatches,
        "closer mismatches": closer_mismatches,
        "closers": closers, "six-round witnesses": witnesses, "rows": rows,
    }
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
