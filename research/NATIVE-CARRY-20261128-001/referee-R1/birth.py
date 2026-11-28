"""Check the time of every pair decision and the choice a set witnesses in its closure."""

import argparse
import gzip
import json
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from itertools import combinations, product
from pathlib import Path


HERE = Path(__file__).resolve().parent
RESEARCH = HERE.parents[1]
ENGINE = RESEARCH / "FORBID-EDITS-20261126-001"
sys.path.insert(0, str(ENGINE))
import forbid


def holdings(knots):
    holders = defaultdict(list)
    for i, knot in enumerate(knots):
        for distinction in knot:
            holders[distinction].append(i)
    return holders


def pairs_at_birth(stages):
    """Decide at the end of the later distinction's birth round, using only that stage."""
    previous = set()
    eligible = set()
    decision = {}
    natural_failure = None
    for r, knots in enumerate(stages):
        held = holdings(knots)
        newly_born = set(held) - previous
        for x, y in combinations(sorted(held), 2):
            if x not in newly_born and y not in newly_born:
                continue
            then = (tuple(held[x]), tuple(held[y]))
            decision[x, y] = (r, then)
            if set(then[0]).isdisjoint(then[1]) and max(map(len, then)) == 2:
                eligible.add((x, y))
        if natural_failure is None:
            for u, v in combinations(range(len(knots)), 2):
                count = sum(tuple(sorted((x, y))) in eligible for x, y in product(knots[u], knots[v]))
                if count % 2:
                    natural_failure = r
                    break
        previous = set(held)
    return eligible, decision, natural_failure


@dataclass(frozen=True)
class Cell:
    pair: tuple
    owners: int
    column: int
    legal: bool


def build_cells(knots, eligible):
    """Put sign in bit zero and the four cross pairs in the remaining bits."""
    held = holdings(knots)
    assert all(len(owners) == 2 for owners in held.values())
    pair_bits = {uv: 1 << (i + 1) for i, uv in enumerate(combinations(range(len(knots)), 2))}
    cells = []
    for x, y in combinations(sorted(held), 2):
        a, b = held[x]
        c, d = held[y]
        if not set((a, b)).isdisjoint((c, d)):
            continue
        crosses = sum(pair_bits[tuple(sorted((u, v)))] for u, v in product((a, b), (c, d)))
        sign = int((a < c < b) != (a < d < b))
        cells.append(Cell((x, y), sum(1 << u for u in (a, b, c, d)), crosses | sign, (x, y) in eligible))
    assert {cell.pair for cell in cells if cell.legal} == eligible
    return cells


def can_close_odd(cells):
    """Test whether some selection of these columns gives zero coverage and sign one."""
    basis = {}
    for cell in cells:
        value = cell.column
        while value:
            pivot = value.bit_length() - 1
            if pivot not in basis:
                basis[pivot] = value
                break
            value ^= basis[pivot]
    return 0 in basis


def reader_kind(choice, knots):
    """A failing-pair component must belong to one reader, with one value per knot."""
    neighbors = defaultdict(set)
    for cell in choice:
        x, y = cell.pair
        neighbors[x].add(y)
        neighbors[y].add(x)
    if all(len(others) == 1 for others in neighbors.values()):
        return "strict"
    unseen = set(neighbors)
    while unseen:
        part = {unseen.pop()}
        todo = list(part)
        while todo:
            for y in neighbors[todo.pop()] & unseen:
                unseen.remove(y)
                part.add(y)
                todo.append(y)
        if any(len(part.intersection(knot)) > 1 for knot in knots):
            return "no split"
    return "larger readers"


def all_sets(knots, cells):
    """Enumerate every subset without pruning supersets, then test inclusion minimality."""
    groups = defaultdict(lambda: [0, 0])
    for cell in cells:
        counts = groups[cell.owners]
        counts[0] += 1
        counts[1] ^= cell.column
    sets = {}
    for size in range(4, len(knots) + 1):
        for subset in combinations(range(len(knots)), size):
            mask = sum(1 << i for i in subset)
            total = value = 0
            for owners, (count, xor) in groups.items():
                if owners & mask == owners:
                    total += count
                    value ^= xor
            if total and value < 2:
                sets[mask] = {
                    "size": size,
                    "sign": value,
                    "minimal": not any(proper & mask == proper for proper in sets),
                }
    return sets


def ids(mask):
    return [i for i in range(mask.bit_length()) if mask >> i & 1]


def inspect(start, stages, baseline, closed_row, reader_row, evidence, round_counts, sample_rows):
    knots = stages[-1]
    size = len(knots)
    r = len(stages) - 1
    eligible, decisions, natural_failure = pairs_at_birth(stages)
    cells = build_cells(knots, eligible)
    legal_cells = [cell for cell in cells if cell.legal]
    held_rounds = []
    for round_number, stage in enumerate(stages):
        held_rounds.extend([round_number] * (len(stage) - len(held_rounds)))
    held = holdings(knots)
    for cell in cells:
        x, y = cell.pair
        birth_round = max(held_rounds[held[x][0]], held_rounds[held[y][0]])
        earliest_second = min(held_rounds[held[x][1]], held_rounds[held[y][1]])
        assert birth_round == decisions[cell.pair][0] and cell.legal == (earliest_second <= birth_round)
    birth_odd = can_close_odd(legal_cells)
    whole_odd = can_close_odd(cells)
    assert baseline["closing round"] == r and baseline["knots"] == size
    assert baseline["unheld pairs"] == len(cells) and baseline["locally decidable pairs"] == len(eligible)
    assert baseline["natural rule: first round without a state"] == natural_failure
    assert baseline["birth choices attain odd"] == birth_odd and baseline["whole choices attain odd"] == whole_odd
    assert closed_row["birth choices attain odd"] == birth_odd
    sets = all_sets(knots, cells)
    restricted = sets if len(cells) == len(legal_cells) else all_sets(knots, legal_cells)
    ambient = (1 << size) - 1
    minimal_odd = {m for m, s in sets.items() if s["minimal"] and s["sign"]}
    stored_minimal = {sum(1 << i for i in item["set"]): item["sign"] for item in closed_row["minimal carriers"]}
    assert {m: s["sign"] for m, s in sets.items() if s["minimal"]} == stored_minimal
    assert (ambient in sets) == closed_row["whole closure a carrier"]
    assert sets.get(ambient, {}).get("sign") == closed_row["whole closure sign"]
    assert (natural_failure is None) == (ambient in restricted or not legal_cells)
    if natural_failure is None:
        expected = "odd" if restricted.get(ambient, {}).get("sign") else "even"
        assert baseline["natural rule closing sign"] == expected
    odd = {m for m, s in sets.items() if s["sign"]}
    odd_legal = set()
    min_reader_counts = Counter()
    all_reader_counts = Counter()
    certificates = []
    for mask in sorted(sets):
        choice = [cell for cell in cells if cell.owners & mask == cell.owners]
        readers = reader_kind(choice, knots)
        all_reader_counts[readers] += 1
        if readers != "no split":
            active = {d for cell in choice for d in cell.pair}
            active_knots = sorted({i for d in active for i in held[d]})
            assert readers == "strict" and len(choice) == 3 and len(active) == 6 and len(active_knots) == 4
            assert {tuple(held[d]) for d in active} == set(combinations(active_knots, 2))
            assert sum(1 << i for i in active_knots) in minimal_odd and mask in odd
        if mask not in odd:
            continue
        is_legal = all(cell.legal for cell in choice)
        if is_legal:
            odd_legal.add(mask)
        if mask in minimal_odd:
            min_reader_counts[readers] += 1
        if r > 1 or ((odd and not minimal_odd) and "odd set with only even minimal subsets" not in evidence):
            certificates.append({
                "knots": ids(mask),
                "minimal": mask in minimal_odd,
                "split": readers,
                "interleavings in listed order": sum(c.column & 1 for c in choice),
                "failing pairs": [cell.pair for cell in choice],
                "birth-forbidden pairs": [cell.pair for cell in choice if not cell.legal],
            })
    strict = bool(min_reader_counts["strict"])
    no_split = bool(min_reader_counts["no split"])
    other_birth_choice_splits = bool(reader_row and reader_row["general"])
    if reader_row:
        assert birth_odd and reader_row["closing round"] == r
        if any(mask in odd_legal and reader_kind([c for c in cells if c.owners & mask == c.owners], knots) == "strict"
               for mask in minimal_odd):
            assert reader_row["strict"]
    stats = round_counts[r]
    finished_ambient_odd = ambient in odd
    tallies = {
        "closures": 1,
        "closures with distinct finished and birth candidate rosters": len(legal_cells) != len(cells),
        "finished candidates": len(cells),
        "birth candidates": len(legal_cells),
        "forbidden at birth": len(cells) - len(legal_cells),
        "an arbitrary finished choice can close odd": whole_odd,
        "an arbitrary birth choice can close odd": birth_odd,
        "natural rule keeps a state": natural_failure is None,
        "natural rule closes odd": natural_failure is None and restricted.get(ambient, {}).get("sign", 0),
        "all finished candidates jointly commute": ambient in sets,
        "all finished candidates jointly close odd": sets.get(ambient, {}).get("sign", 0),
        "closures with an odd minimal whole-choice set": bool(minimal_odd),
        "odd minimal whole-choice sets": len(minimal_odd),
        "closures with a birth-legal odd minimal whole-choice set": bool(minimal_odd & odd_legal),
        "birth-legal odd minimal whole-choice sets": len(minimal_odd & odd_legal),
        "closures with birth-forbidden odd minimal whole-choice sets": bool(minimal_odd - odd_legal),
        "odd minimal whole-choice sets that split strictly": min_reader_counts["strict"],
        "odd minimal whole-choice sets with no reader split": min_reader_counts["no split"],
        "all nonempty commuting whole-choice sets": len(sets),
        "all nonempty commuting whole-choice sets that split strictly": all_reader_counts["strict"],
        "all nonempty commuting whole-choice sets that split only with larger readers": all_reader_counts["larger readers"],
        "closures with a splitting whole-choice set of any size": bool(all_reader_counts["strict"] or all_reader_counts["larger readers"]),
        "closures with a strictly splitting odd minimal whole-choice set": strict,
        "closures with only nonsplitting odd minimal whole-choice sets": no_split and not strict,
        "closures with both strictly splitting and nonsplitting odd minimal whole-choice sets": no_split and strict,
        "closures with only nonsplitting minima but a different splitting birth choice": no_split and not strict and other_birth_choice_splits,
        "closures with only nonsplitting minima and no splitting birth choice": no_split and not strict and not other_birth_choice_splits,
        "closures with an odd whole-choice set of any size": bool(odd),
        "closures with a birth-legal odd whole-choice set of any size": bool(odd_legal),
        "odd whole-choice sets of any size": len(odd),
        "birth-legal odd whole-choice sets of any size": len(odd_legal),
        "odd-attaining closures with no odd minimal whole-choice set": birth_odd and not minimal_odd,
        "odd-attaining closures with no odd whole-choice set of any size": birth_odd and not odd,
        "odd-attaining closures whose only odd whole-choice sets are nonminimal": birth_odd and bool(odd) and not minimal_odd,
        "entire closure odd with some odd minimal set": finished_ambient_odd and bool(minimal_odd),
        "entire closure odd with only even minimal sets": finished_ambient_odd and not minimal_odd,
        "birth-odd closures with a proper odd set only and with an odd minimal set": birth_odd and bool(minimal_odd) and not finished_ambient_odd,
        "birth-odd closures with a proper odd set only and no odd minimal set": birth_odd and bool(odd) and not minimal_odd and not finished_ambient_odd,
        "closures with an odd set using every eligible internal cell": any(s["sign"] for s in restricted.values()),
        "closures with an odd minimal set using every eligible internal cell": any(s["sign"] and s["minimal"] for s in restricted.values()),
        "odd sets using every eligible internal cell": sum(s["sign"] for s in restricted.values()),
        "odd minimal sets using every eligible internal cell": sum(s["sign"] and s["minimal"] for s in restricted.values()),
    }
    stats["knots in largest closure"] = max(stats["knots in largest closure"], size)
    for key, value in tallies.items():
        stats[key] += int(value)
    if odd and not minimal_odd:
        evidence.setdefault("odd set with only even minimal subsets", {
            "census start index": start, "closing round": r, "holdings": knots,
            "odd choices": certificates,
            "even minimal subsets": [
                {
                    "knots": ids(mask),
                    "cells": sum(c.owners & mask == c.owners for c in cells),
                    "interleavings in listed order": sum(c.column & 1 for c in cells if c.owners & mask == c.owners),
                }
                for mask, s in sets.items() if s["minimal"] and not s["sign"]
            ],
        })
    if minimal_odd and natural_failure is not None:
        example = "odd minimal set with a proper selection in the ambient closure"
        if example not in evidence:
            witness = min(minimal_odd)
            evidence[example] = {
                "census start index": start, "closing round": r, "holdings": knots, "subset": ids(witness),
                "internal pairs": [c.pair for c in cells if c.owners & witness == c.owners],
                "other birth-eligible pairs": [c.pair for c in legal_cells if c.owners & witness != c.owners],
                "first round without a natural-rule state": natural_failure,
            }
    if r > 1:
        omitted_pairs = {str(c.pair): decisions[c.pair] for c in cells if not c.legal}
        sample_rows.append({
            "census start index": start, "closing round": r, "knots by round": [len(stage) for stage in stages],
            "finished holdings": knots, "number of finished candidates": len(cells),
            "birth-eligible pairs": sorted(eligible),
            "birth-forbidden pairs with decision round and original holders": omitted_pairs,
            "any odd birth choice": birth_odd, "any odd finished choice": whole_odd,
            "first natural failure round": natural_failure, "odd whole-choice sets": certificates,
            "odd subsets with every birth-eligible internal cell": [ids(m) for m, s in restricted.items() if s["sign"]],
        })


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--probe", type=int, help="check a prefix of closure indices without writing the final files")
    args = parser.parse_args()
    starts = json.loads((ENGINE / "starts.json").read_text())
    with (RESEARCH / "LOCAL-COMMUTE-20261127-001/results.jsonl").open() as handle:
        old = {s["start"]: s for s in map(json.loads, handle) if "closing round" in s}
    with (RESEARCH / "READER-SPLIT-20261127-001/results.jsonl").open() as handle:
        readers = {s["start"]: s for s in map(json.loads, handle)}
    with gzip.open(HERE.parent / "rows.jsonl.gz", "rt") as handle:
        closed = {s["start index"]: s for s in map(json.loads, handle) if s["population"] == "census starts"}
    assert set(readers) == {s for s in old if old[s]["birth choices attain odd"]}
    assert old.keys() == closed.keys()
    evidence = {}
    round_counts = defaultdict(Counter)
    later = []
    indices = list(old)[:args.probe]
    for index in indices:
        baseline = old[index]
        stages = [forbid.supports_of(starts[index])]
        for _ in range(baseline["closing round"]):
            assert any(len(owners) == 1 for owners in holdings(stages[-1]).values())
            next_stage, status, _ = forbid.grown(stages[-1], "parity", "ordinary")
            assert status == "funded"
            stages.append(next_stage)
        inspect(index, stages, baseline, closed[index], readers.get(index), evidence, round_counts, later)
    result = {
        "weighting": "One vote per census start for closure tallies. One per subset of knots per closure for set tallies.",
        "roster": "Closure indices of the commutation-at-birth census, grown afresh from the archived starts.",
        "method": "Exact event-time eligibility and direct all-subset enumeration on the 1,819 closures. Reader split means the separated-reader study's two conditions.",
        "counts by closing round": dict(sorted(round_counts.items())),
        "examples": evidence,
    }
    if args.probe is not None:
        print(json.dumps(result["counts by closing round"]))
        return
    assert len(later) == 106
    (HERE / "birth.json").write_text(json.dumps(result, indent=2) + "\n")
    with (HERE / "birth_later.jsonl").open("w") as handle:
        for row in later:
            handle.write(json.dumps(row) + "\n")


if __name__ == "__main__":
    main()
