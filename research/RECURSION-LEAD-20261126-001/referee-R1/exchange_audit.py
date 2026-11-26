"""Recount the two exchange preparations against every recorded recurrence row."""

import argparse
import json
from collections import Counter, defaultdict
from itertools import combinations, groupby, islice
from pathlib import Path

import growth
from exchange import exchange, holders, kernel_basis, parity_columns, positions, renaming, sharing


RECORD = Path(__file__).resolve().parents[1]
STEPS = 4


def shape(pattern):
    shared, loose = sharing(pattern)
    seen, pending = {0}, [0]
    while pending:
        new = set(shared[pending.pop()]) - seen
        seen.update(new)
        pending.extend(new)
    ring = len(pattern) >= 3 and len(seen) == len(pattern) and all(
        sorted(around.values()) == [1, 1] for around in shared
    )
    return {
        "knots": len(pattern),
        "most shared distinctions at a knot": max(map(Counter.total, shared), default=0),
        "one ring": ring,
        "loose": loose,
    }


def step(start, pinned):
    stage, status, births = growth.round_detail(start)
    return stage, status, births, exchange(stage, pinned) if status == "funded" else None


def outcome(status, result):
    if result is None:
        return f"does not grow ({status})"
    return "lawful" if result.lawful else "exchange not lawful"


def follow(start, pinned, first):
    seen = [start]
    attempts = [first]
    record, witness = [], None
    for turn in range(STEPS):
        stage, status, births, result = attempts[turn]
        if result is None or not result.lawful:
            record.append(outcome(status, result))
            break

        for previous, old in enumerate(seen):
            witness = renaming(result.supports, old)
            if witness is not None:
                if previous == 0:
                    record.append("returns to the start")
                elif previous == len(seen) - 1:
                    record.append(f"fixed at step {previous}")
                else:
                    record.append(f"cycle back to step {previous}")
                return record, attempts, witness

        record.append(f"a new start ({len(result.supports)} knots)")
        seen.append(result.supports)
        if turn < STEPS - 1:
            attempts.append(step(result.supports, pinned))
    return record, attempts, witness


def line_graph_reading(start, births):
    """The claimed four-distinction change per pair of old shared distinctions."""
    shared = [(d, held) for d, held in holders(start).items() if len(held) == 2]
    pair_births = defaultdict(list)
    for birth in births:
        if len(birth.parents) == 2:
            pair_births[tuple(sorted(birth.parents))].append(birth.taken)
    expected = set()
    for knot in range(len(start)):
        neighbors = [(d, b if a == knot else a) for d, (a, b) in shared if knot in (a, b)]
        for (first, a), (second, b) in combinations(neighbors, 2):
            found = pair_births[tuple(sorted((a, b)))]
            if len(found) != 1:
                return None
            expected.add(frozenset((first, second)) | found[0])
    return expected


def literal_kernel(names, basis):
    """Enumerate every allowed change before taking the least through each distinction."""
    words = [0]
    unresolved = 0
    for dependency in basis:
        words.extend([word ^ dependency for word in words])
        unresolved |= dependency
    fixed = frozenset(set(names) - {names[i] for i in positions(unresolved)})
    words.sort(key=int.bit_count)
    minima, supports = {}, set()
    for size, equal_size in groupby(words, key=int.bit_count):
        if not unresolved:
            break
        resolved = 0
        for word in equal_size:
            if word & unresolved:
                supports.add(frozenset(names[i] for i in positions(word)))
                resolved |= word & unresolved
        minima.update((names[i], size) for i in positions(resolved))
        unresolved ^= resolved
    assert unresolved == 0
    return supports, minima, fixed, len(words)


def count_coverage(counts, phase, stage, result, name, cutoff_examples, compare_literal):
    if result is None:
        return
    names, columns = parity_columns(stage, result.pins)
    basis = kernel_basis(columns)
    dimension = len(basis)
    retained = frozenset().union(*result.supports)
    assert retained == set(result.minima)
    assert set(holders(stage)) - retained == result.pins | result.missing
    counts["funded stages"] += 1
    counts["stage distinctions"] += len(names) + len(result.pins)
    counts["pinned distinctions omitted from exchange"] += len(result.pins)
    counts["unpinned distinctions omitted from exchange"] += len(result.missing)
    counts["stages omitting an unpinned distinction"] += bool(result.missing)
    counts["largest minimum"] = max(counts["largest minimum"], max(result.minima.values(), default=0))
    counts["largest dimension"] = max(counts["largest dimension"], dimension)
    counts["largest input width"] = max(counts["largest input width"], len(names) + len(result.pins))
    counts["dimension above 22"] += dimension > 22
    if compare_literal:
        supports, minima, fixed, assignments = literal_kernel(names, basis)
        assert supports == set(result.supports), (name, phase, "shortest supports differ")
        assert minima == result.minima, (name, phase, "minima differ")
        assert fixed == result.missing, (name, phase, "unflippable distinctions differ")
        counts["complete kernel comparisons"] += 1
        counts["complete kernel words including zero"] += assignments
    long = {d: size for d, size in result.minima.items() if size > 6}
    counts["dimension above 22 and minimum above six"] += dimension > 22 and bool(long)
    if dimension > 22 and long:
        exact_differences = [sorted(row) for row in result.supports if len(row) > 6]
        assert exact_differences
        counts["distinctions with a minimum above the old cutoff"] += len(long)
        counts["supports beyond the old cutoff"] += len(exact_differences)
        if len(cutoff_examples) < 12:
            cutoff_examples.append({
                "case": name,
                "phase": phase,
                "kernel dimension": dimension,
                "minimum above six": long,
                "stages": [sorted(row) for row in stage],
                "supports beyond cutoff": exact_differences,
            })

    # Only the older full-kernel branch used fixed-width masks.
    if dimension <= 22 and len(names) + len(result.pins) > 64:
        counts["width above 64 and dimension at most 22"] += 1
        high = set(sorted(set(names) | result.pins)[64:])
        counts["flippable distinction above bit 63 in the full-kernel branch"] += bool(high & result.minima.keys())


def inputs(population):
    if population == "census":
        return [(f"census {i}", pattern) for i, pattern in enumerate(growth.census())]
    return [(f"held out {n}-{j}", pattern) for (n, j), pattern in growth.heldout().items()]


def audit(population, limit=None, compare_literal=False):
    path = RECORD / f"recur_{population}.jsonl"
    rows = [json.loads(line) for line in path.read_text().splitlines()]
    cases = inputs(population)
    assert len(rows) == len(cases)
    counts, opportunities = Counter(), Counter()
    outcomes, coverage, failures = defaultdict(Counter), defaultdict(Counter), defaultdict(Counter)
    mismatches, lawful, cutoff_examples = [], [], []
    for (name, start), raw in islice(zip(cases, rows, strict=True), limit):
        counts["rows"] += 1
        geometry = shape(start)
        reconstructed = {"start": name, **geometry}
        after, status, births = growth.round_detail(start)
        counts[f"growth {status}"] += 1
        predicted_ring = geometry["one ring"] and len(start) >= 5 and len(start) != 6 and set(geometry["loose"]) == {2}
        opportunities["starts of the predicted return form"] += predicted_ring
        related = geometry["most shared distinctions at a knot"] > 2
        if status == "funded":
            grown_shared, grown_loose = sharing(after)
            loose_pair = max(grown_loose) >= 2
            doubled_pair = any(value >= 2 for around in grown_shared for value in around.values())
            opportunities["funded starts with more than two shared distinctions at a knot"] += related
            opportunities["funded starts of the predicted return form"] += predicted_ring
            opportunities["funded stages with two loose distinctions at one knot"] += loose_pair
            opportunities["funded stages with at most one loose distinction per knot"] += not loose_pair
            opportunities["funded stages with a doubled shared pair"] += doubled_pair
            opportunities["funded stages with both two-place causes"] += loose_pair and doubled_pair
            opportunities["funded stages with neither two-place cause"] += not (loose_pair or doubled_pair)
            opportunities["funded stages with no loose distinction"] += not any(grown_loose)

        for mode, pinned in (("pinned", True), ("free", False)):
            result = exchange(after, pinned) if status == "funded" else None
            first = after, status, births, result
            phase = f"{mode} first"
            count_coverage(coverage[phase], phase, after, result, name, cutoff_examples, compare_literal)
            reason = outcome(status, result)
            reconstructed[f"{mode} exchange"] = reason
            counts[f"{mode} {reason}"] += 1
            if result is None:
                continue
            if not pinned:
                assert (2 in result.minima.values()) == (loose_pair or doubled_pair)
                if not (loose_pair or doubled_pair):
                    counts[f"free without either two-place cause: {reason}"] += 1
            failures[mode][" / ".join(result.failures) or "lawful"] += 1
            if not result.lawful:
                continue
            record, attempts, witness = follow(start, pinned, first)
            outcomes[mode][" -> ".join(record)] += 1
            if record[-1].startswith("a new start"):
                counts[f"{mode} reached orbit horizon"] += 1
            else:
                counts[f"{mode} terminal after {len(record)} attempts"] += 1
            for turn, (stage, _, _, current) in enumerate(attempts[1:], start=2):
                phase = f"{mode} attempt {turn}"
                count_coverage(coverage[phase], phase, stage, current, name, cutoff_examples, compare_literal)

            immediate = record == ["returns to the start"]
            counts[f"{mode} compares after passing lawfulness"] += 1
            counts[f"{mode} lawful with starting knot count"] += len(result.supports) == len(start)
            counts[f"{mode} immediate returns"] += immediate
            if pinned:
                reconstructed.update(returns=immediate, orbit=record)
                if related:
                    counts["lawful pinned from more than two shared distinctions at a knot"] += 1
                    counts[f"such pinned orbits end at attempt {len(record)}"] += 1
                    difference = len(result.supports) - len(start)
                    comparison = "fewer" if difference < 0 else "more" if difference > 0 else "the same number of"
                    counts[f"such first exchanges have {comparison} knots"] += 1
                expected = line_graph_reading(start, births)
                counts["lawful pinned with pair formula applicable"] += expected is not None
                counts["lawful pinned with exact pair formula"] += expected == set(result.supports)
                if related:
                    counts["lawful pinned from more than two shared with exact pair formula"] += expected == set(result.supports)
                counts["lawful pinned from a predicted ring"] += predicted_ring
            else:
                assert max(grown_loose) < 2

            lawful.append({
                "start": name,
                "mode": mode,
                "start shape": geometry,
                "loose distinctions after growth": grown_loose,
                "orbit": record,
                "renaming": witness,
                "first exchanged pattern": [sorted(row) for row in result.supports],
                "first parent counts": [len(b.parents) for b in births],
                "first unpinned distinctions with no allowed change": sorted(result.missing),
                **({"pair formula matches": expected == set(result.supports)} if pinned else {}),
            })

        if reconstructed != raw:
            mismatches.append({"start": name, "fields": {
                k: {"archived": raw.get(k), "rebuilt": reconstructed.get(k)}
                for k in sorted(reconstructed.keys() | raw.keys())
                if k not in reconstructed or k not in raw or reconstructed[k] != raw[k]
            }})

    return {
        "source": f"../{path.name}",
        "available starts": len(cases),
        "field mismatches": mismatches,
        "counts": counts,
        "prediction opportunities": opportunities,
        "exchange failures": failures,
        "orbits": outcomes,
        "coverage and old cutoff": coverage,
        "old cutoff discrepancy examples": cutoff_examples,
        "lawful outputs": lawful,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("population", choices=("all", "census", "heldout"))
    parser.add_argument("--limit", type=int)
    parser.add_argument("--literal", action="store_true", help="also enumerate every allowed change")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    populations = ("census", "heldout") if args.population == "all" else (args.population,)
    report = {population: audit(population, args.limit, args.literal) for population in populations}
    if args.output:
        args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps({name: {
        "mismatches": len(data["field mismatches"]),
        "counts": data["counts"],
        "opportunities": data["prediction opportunities"],
        **({key: sum(phase[key] for phase in data["coverage and old cutoff"].values())
            for key in ("complete kernel comparisons", "complete kernel words including zero")} if args.literal else {}),
    } for name, data in report.items()}, indent=2, sort_keys=True))
    return any(data["field mismatches"] for data in report.values())


if __name__ == "__main__":
    raise SystemExit(main())
