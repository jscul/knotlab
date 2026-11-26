"""Rebuild the exploratory starts and check exchange by a second parity search."""

import argparse
import json
from collections import defaultdict
from functools import cache
from heapq import heapify, heappop, heappush
from itertools import combinations
from pathlib import Path
from random import Random

import growth
from exchange import exchange, kernel_basis, parity_columns, positions, renaming
from exchange_audit import follow, line_graph_reading, outcome, shape, step


def literal(pattern, pins, bound):
    """Match parity syndromes of two halves of each candidate change."""
    names, columns = parity_columns(pattern, pins)
    basis = kernel_basis(columns)
    possible = 0
    for word in basis:
        possible |= word

    @cache
    def by_syndrome(size):
        buckets = defaultdict(list)
        for parts in combinations(range(len(names)), size):
            word = syndrome = 0
            for index in parts:
                word |= 1 << index
                syndrome ^= columns[index]
            buckets[syndrome].append(word)
        return buckets

    active = possible
    moves, minima = set(), {}
    for length in range(1, bound + 1):
        if not active:
            break
        half = length // 2
        matches = 0
        right = by_syndrome(length - half)
        for syndrome, choices in by_syndrome(half).items():
            for tail in right.get(syndrome, ()):
                first_tail = (tail & -tail).bit_length()
                for head in choices:
                    # Break each support after its first `half` names, once.
                    if head.bit_length() < first_tail and (head | tail) & active:
                        word = head | tail
                        moves.add(word)
                        matches |= word
        minima.update({names[i]: length for i in positions(matches & active)})
        active &= ~matches
    return {
        "supports": set(frozenset(names[i] for i in positions(move)) for move in moves),
        "minima": minima,
        "fixed": frozenset(set(names) - {names[i] for i in positions(possible)}),
        "flippable without a bounded witness": frozenset(names[i] for i in positions(active)),
        "kernel dimension": len(basis),
    }


def from_sharing(n, shared, loose):
    rows = [set() for _ in range(n)]
    for distinction, (first, second) in enumerate(shared):
        rows[first].add(distinction)
        rows[second].add(distinction)
    distinction = len(shared)
    for row, count in zip(rows, loose, strict=True):
        row.update(range(distinction, distinction + count))
        distinction += count
    return tuple(map(frozenset, rows))


def tree(n, rng):
    """Use the recorded labelled-tree weighting with bare loose counts."""
    code = [rng.randrange(n) for _ in range(n - 2)]
    degree = [1 + code.count(i) for i in range(n)]
    remaining = degree.copy()
    leaves = [i for i in range(n) if degree[i] == 1]
    heapify(leaves)
    shared = []
    for other in code:
        leaf = heappop(leaves)
        shared.append((leaf, other))
        remaining[other] -= 1
        if remaining[other] == 1:
            heappush(leaves, other)
    shared.append(tuple(leaves))
    demand = [0] * n
    for first, second in shared:
        demand[first] += degree[second] - 1
        demand[second] += degree[first] - 1
    return from_sharing(n, shared, [max(3 - degree[i], demand[i]) for i in range(n)])


def trial(name, start):
    record = {"start": name, "start shape": shape(start), "start pattern": [sorted(row) for row in start]}
    for mode, pinned in (("pinned", True), ("free", False)):
        first = step(start, pinned)
        _, status, births, result = first
        chain, _, witness = follow(start, pinned, first)
        entry = {"growth status": status, "outcome": outcome(status, result), "orbit": chain}
        if result is not None:
            entry.update({
                "moves": len(result.supports),
                "first parent counts": [len(birth.parents) for birth in births],
                "unpinned distinctions with no allowed change": len(result.missing),
                "failures": result.failures,
            })
            if result.lawful:
                entry["output shape"] = shape(result.supports)
                entry["renaming"] = witness
                entry["is the ring with two loose per knot"] = bool(
                    renaming(result.supports, growth.ring(len(start), 2))
                ) if len(start) >= 3 else False
                if pinned:
                    entry["pair formula matches"] = line_graph_reading(start, births) == set(result.supports)
        record[mode] = entry
    return record


def agreement(sizes):
    """Compare bare and once-grown rings under both preparations."""
    results = []
    for n in sizes:
        start = growth.ring(n, 2)
        stage, status, _ = growth.advance(start)
        assert status == "funded"
        for rounds, current in ((0, start), (1, stage)):
            for mode, pinned in (("pinned", True), ("free", False)):
                exact = exchange(current, pinned)
                maximum = max(exact.minima.values(), default=0)
                direct = literal(current, exact.pins, bound=max(6, maximum))
                assert not direct["flippable without a bounded witness"]
                assert set(exact.supports) == direct["supports"]
                assert exact.minima == direct["minima"]
                assert exact.missing == direct["fixed"]
                results.append({
                    "ring knots": n,
                    "rounds": rounds,
                    "mode": mode,
                    "allowed kernel dimension": direct["kernel dimension"],
                    "longest minimum": maximum,
                    "moves from both searches": len(exact.supports),
                    "unpinned distinctions with no change": len(exact.missing),
                    "pinned distinctions": len(exact.pins),
                    "all shortest supports and minima agree": True,
                })
    return results


def controls(pilot):
    ring_sharing = [(i, (i + 1) % 7) for i in range(7)]
    additional_sharing = [(i, i + 7) for i in range(7) for _ in range(3)]
    long_pattern = from_sharing(14, ring_sharing + additional_sharing, [24] + [0] * 13)
    exact = exchange(long_pattern, False)
    bound = literal(long_pattern, exact.pins, bound=6)
    assert bound["kernel dimension"] > 22
    assert bound["flippable without a bounded witness"] == frozenset(range(7))
    assert set(exact.supports) - bound["supports"] == {frozenset(range(7))}

    all_across = from_sharing(6, [(a, b) for a in range(3) for b in range(3, 6)], [0] * 6)
    within_and_across = from_sharing(6, [*combinations(range(3), 2), *combinations(range(3, 6), 2),
                                         *((a, a + 3) for a in range(3))], [0] * 6)
    assert shape(all_across) == shape(within_and_across)
    assert renaming(all_across, within_and_across) is None
    base = growth.ring(5, 2)
    recoded = tuple(frozenset(101 + 17 * d for d in row) for row in reversed(base))
    assert renaming(base, recoded) is not None
    assert {frozenset(101 + 17 * d for d in row) for row in exchange(base, False).supports} == set(
        exchange(recoded, False).supports
    )

    closed, status, _ = growth.advance(growth.ring(3, 1))
    assert status == "funded"
    assert growth.advance(closed)[1] == "closed"
    exchanged_closed = exchange(closed, False)
    assert exchanged_closed.lawful
    witness = renaming(exchanged_closed.supports, closed)
    assert witness is not None

    rings = [trial(f"ring with {n} knots and {loose} loose at each", growth.ring(n, loose))
             for n in ([5] if pilot else range(3, 11)) for loose in range(1, 5)]
    chain = from_sharing(5, [(i, i + 1) for i in range(4)], [2] * 5)
    variants = [
        trial("chain of five knots with two loose at each", chain),
        trial("ring of five knots with loose counts 2, 3, 2, 4, 2",
              from_sharing(5, [(i, (i + 1) % 5) for i in range(5)], [2, 3, 2, 4, 2])),
    ]
    rng = Random(20261207)
    trees = [trial(f"sample {i + 1} of bare trees with {n} knots", tree(n, rng))
             for n in ([5] if pilot else range(5, 9)) for i in range(3)]
    joined = [trial(name, start) for name, start in list(growth.joined().items())[3:(4 if pilot else 9)]]
    return {
        "agreement on a reproducible ring panel": agreement([5] if pilot else range(4, 11)),
        "ring exploration and loose-count controls": rings,
        "constructed variants": variants,
        "seeded bare trees": trees,
        "joined rings": joined,
        "renaming controls": {"exact recoding preserved": True, "equal inventories but different sharing rejected": True},
        "closed control": {"description": "three-knot ring with one loose distinction at each closes under one growth round",
                           "exchange alone fixes the closed pattern": witness},
        "legacy cutoff control": {
            "description": "seven knots in a ring, each sharing three distinctions with an additional knot, and 24 loose at the first",
            "input pattern": [sorted(row) for row in long_pattern],
            "kernel dimension": bound["kernel dimension"],
            "exact moves": len(exact.supports),
            "moves at cutoff six": len(bound["supports"]),
            "omitted flippable distinctions": sorted(bound["flippable without a bounded witness"]),
            "omitted support": list(range(7)),
        },
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pilot", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = controls(args.pilot)
    if args.output:
        args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(f"Exact supports and minima agree in {len(report['agreement on a reproducible ring panel'])} comparisons")
    for panel in ("ring exploration and loose-count controls", "constructed variants", "seeded bare trees", "joined rings"):
        for row in report[panel]:
            print(row["start"], "pinned", " -> ".join(row["pinned"]["orbit"]), "free", " -> ".join(row["free"]["orbit"]))


if __name__ == "__main__":
    main()
