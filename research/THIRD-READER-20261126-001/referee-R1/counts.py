"""Rebuild the shared-triple inventory from the joined-ring construction and ordinary growth.

The archive is opened only after the independent stage and partition calculations.
Use --pilot for one family through the same two growth rounds.
"""

import argparse
from collections import Counter, defaultdict, deque
from functools import cache
from gzip import open as gzip_open
from itertools import combinations
import json
from pathlib import Path
import resource
from time import perf_counter


HERE = Path(__file__).resolve().parent
FAMILIES = (
    ("three rings of five, detour (the referee's 30 knots)", 3, 5, True, False),
    ("three rings of five, direct links", 3, 5, False, False),
    ("three rings of four, detour", 3, 4, True, False),
    ("two rings of five, detour", 2, 5, True, False),
    ("three rings of five, detour, one loose distinction at the first chain's middle knot",
     3, 5, True, True),
)


def rebuild_start(ring_count, size, detour, extra_loose):
    rings = tuple(tuple(range(r * size, (r + 1) * size)) for r in range(ring_count))
    pairs = tuple(combinations(range(ring_count), 2))
    block_size = 5 if detour else 2
    new_knots = ring_count * size
    distinction_holders = [(ring[i], ring[(i + 1) % size]) for ring in rings for i in range(size)]
    distinction_holders += [(knot,) for ring in rings for knot in ring for _ in range(2)]
    used_attachments = Counter()
    for r, s in pairs:
        left, right = new_knots, new_knots + 1
        new_knots += block_size
        for ring, connector in ((r, left), (s, right)):
            first = used_attachments[ring]
            distinction_holders.extend([(rings[ring][first], connector),
                                        (rings[ring][(first + 2) % size], connector)])
            used_attachments[ring] += 1
        distinction_holders.append((left, right))
        if detour:
            chain = (left, left + 2, left + 3, left + 4, right)
            for pair in zip(chain, chain[1:]):
                distinction_holders.extend([pair, pair])
        else:
            distinction_holders.append((left, right))
    if extra_loose:
        distinction_holders.append((ring_count * size + 3,))
    knots = [[] for _ in range(new_knots)]
    for distinction, holders in enumerate(distinction_holders):
        for knot in holders:
            knots[knot].append(distinction)
    lineages = tuple(frozenset((r,)) for r in range(ring_count) for _ in range(size))
    lineages += (frozenset(("middle",)),) * (new_knots - ring_count * size)
    return tuple(map(tuple, knots)), lineages


def holders_of(knots):
    holders = defaultdict(list)
    for knot, support in enumerate(knots):
        for distinction in support:
            holders[distinction].append(knot)
    return dict(holders)


def neighbours_of(knots):
    neighbours = [set() for _ in knots]
    for owners in holders_of(knots).values():
        assert len(owners) in (1, 2)
        if len(owners) == 2:
            left, right = owners
            neighbours[left].add(right)
            neighbours[right].add(left)
    return neighbours


def birth_groups(knots, live):
    neighbours = neighbours_of(knots)
    pairs = [pair for pair in combinations(live, 2) if neighbours[pair[0]] & neighbours[pair[1]]]
    following = defaultdict(set)
    for first, second in pairs:
        following[first].add(second)
    valid = []

    def visit(group, remaining, common):
        if len(group) >= 3 and not common:
            valid.append(frozenset(group))
        for child in sorted(remaining):
            visit(group + (child,), remaining & following[child], common & neighbours[child])

    for knot in live:
        visit((knot,), following[knot], neighbours[knot])
    maximal = [group for group in valid if not any(group < other for other in valid)]
    covered = {pair for group in maximal for pair in combinations(sorted(group), 2)}
    return sorted(tuple(sorted(group)) for group in maximal) + [pair for pair in pairs if pair not in covered]


def mask(distinctions):
    value = 0
    for distinction in distinctions:
        value |= 1 << distinction
    return value


def bit_positions(value):
    while value:
        bit = value & -value
        yield bit.bit_length() - 1
        value ^= bit


def eliminate(images):
    """Return independent images and dependencies among the original images."""
    pivots = {}
    dependencies = []
    for index, image in enumerate(images):
        combination = 1 << index
        while image:
            pivot = image & -image
            if pivot not in pivots:
                pivots[pivot] = image, combination
                break
            old_image, old_combination = pivots[pivot]
            image ^= old_image
            combination ^= old_combination
        if not image:
            dependencies.append(combination)
    return tuple(image for image, _ in pivots.values()), dependencies


def rank(rows):
    return len(eliminate(rows)[0])


def combination(vectors, coefficients):
    result = 0
    for index in bit_positions(coefficients):
        result ^= vectors[index]
    return result


def ordinary_round(knots, lineages):
    holders = holders_of(knots)
    loose = defaultdict(deque)
    for distinction, owners in sorted(holders.items()):
        if len(owners) == 1:
            loose[owners[0]].append(distinction)
    groups = birth_groups(knots, sorted(loose))
    spending = Counter(knot for group in groups for knot in group)
    assert loose and all(spending[knot] <= len(bits) for knot, bits in loose.items())
    groups += [(knot,) for knot in sorted(loose) for _ in range(len(loose[knot]) - spending[knot])]
    inputs = tuple(tuple(loose[parent].popleft() for parent in group) for group in groups)
    assert not any(loose.values())
    lookahead = birth_groups(knots + inputs, list(range(len(knots), len(knots) + len(inputs))))
    demand = Counter(knot for group in lookahead for knot in group)
    original_laws = tuple(map(mask, knots))
    law_rank = rank(original_laws)
    first_fresh = len(holders)
    births = []
    child_lineages = []
    for knot, (parents, spent) in enumerate(zip(groups, inputs, strict=True), start=len(knots)):
        implied = rank((*original_laws, mask(spent))) == law_rank
        fresh_count = demand[knot] if implied else max(demand[knot], 3 - len(spent), 1)
        fresh = tuple(range(first_fresh, first_fresh + fresh_count))
        first_fresh += fresh_count
        lineage = frozenset().union(*(lineages[parent] for parent in parents))
        child_lineages.append(lineage)
        births.append({"knot": knot, "parents": parents, "inputs": spent,
                       "fresh": fresh, "demand": demand[knot], "implied": implied,
                       "lineage": sorted(lineage, key=str)})
    return (knots + tuple(birth["inputs"] + birth["fresh"] for birth in births),
            lineages + tuple(child_lineages), births)


def stage_read(knots):
    holders = holders_of(knots)
    width = len(holders)
    assert set(holders) == set(range(width))
    whole = (1 << width) - 1
    knot_laws = tuple(map(mask, knots))
    laws = eliminate(knot_laws)[0]
    columns = tuple(mask(holders[d]) for d in range(width))

    @cache
    def supported(region):
        unit_masks = tuple(1 << d for d in bit_positions(region))
        _, change_coeffs = eliminate(columns[d] for d in bit_positions(region))
        _, law_coeffs = eliminate(law & (whole ^ region) for law in laws)
        return (tuple(combination(unit_masks, word) for word in change_coeffs),
                tuple(combination(laws, word) for word in law_coeffs))

    def inventory(regions):
        a, b, m = regions
        assert a & b == a & m == b & m == 0
        assert a | b | m == whole
        E = {}
        for reader, own in zip("ABM", regions, strict=True):
            x, z = supported(own)
            E[reader] = own.bit_count() - len(x) - len(z)
            column_cut = (rank(columns[d] for d in bit_positions(own))
                          + rank(columns[d] for d in bit_positions(whole ^ own)) - len(laws))
            assert E[reader] == column_cut
        pair_masks = {"AB": a | b, "AM": a | m, "BM": b | m}
        e = {}
        for pair, part in pair_masks.items():
            own = a if pair[0] == "A" else b
            x, z = supported(part)
            e[pair] = rank(mask(i for i, law in enumerate(z) if (move & own & law).bit_count() % 2)
                           for move in x)
        estimates = {"from A": E["A"] - e["AB"] - e["AM"],
                     "from B": E["B"] - e["AB"] - e["BM"],
                     "from M": E["M"] - e["AM"] - e["BM"]}
        spaces = [supported(part) for part in pair_masks.values()]
        excess = [len(full) - rank(vector for space in spaces for vector in space[kind])
                  for kind, full in enumerate(supported(whole))]
        g = sum(excess)
        assert set(estimates.values()) == {g}
        estimates["fourth route (changes, laws)"] = excess

        project = [rank(move & region for move in supported(whole)[0]) for region in (a, b, a | b)]
        value_information = project[0] + project[1] - project[2]
        cross_laws = len(supported(a | b)[1]) - len(supported(a)[1]) - len(supported(b)[1])
        change_information = len(supported(a | b)[0]) - len(supported(a)[0]) - len(supported(b)[0])
        separated = not any(a & law and b & law for law in knot_laws)
        assert value_information == cross_laws
        assert value_information + change_information == E["A"] + E["B"] - E["M"]
        if separated:
            assert e["AB"] == change_information == 0 and g == value_information
        result = {"E": E, "pairs with the third unread": e, "triples": estimates}
        return {"inventory": result, "distinctions per reader": [a.bit_count(), b.bit_count(), m.bit_count()],
                "separated ring readers": separated, "uniform-word value information in bits": value_information,
                "cross-reader change dimension": change_information}

    return width, len(laws), inventory


def read_family(description, ring_count, size, detour, extra_loose):
    knots, lineage = rebuild_start(ring_count, size, detour, extra_loose)
    births = []
    for round_number in range(3):
        holders = holders_of(knots)
        width, law_rank, inventory = stage_read(knots)
        measurements = {}
        for choice in ("places", "own"):
            regions = []
            for r in range(ring_count):
                from_ring = [lineage[k] == {r} for k in range(len(knots))]
                holds = any if choice == "places" else all
                regions.append(mask(d for d, owners in holders.items() if holds(from_ring[k] for k in owners)))
            pairs = {f"rings {r} and {s}, middle the rest": (regions[r], regions[s])
                     for r, s in combinations(range(ring_count), 2)}
            if ring_count == 3:
                pairs["rings 0 and 2 together, ring 1, middle the rest"] = (regions[0] | regions[2], regions[1])
            whole = (1 << width) - 1
            measurements[choice] = {pair: inventory((a, b, whole ^ (a | b))) for pair, (a, b) in pairs.items()}
        yield {"family": description, "round": round_number, "knots": len(knots), "distinctions": width,
               "independent laws": law_rank, "births": births, "measurements": measurements}, knots
        if round_number < 2:
            knots, lineage, births = ordinary_round(knots, lineage)
            assert all(len(birth["lineage"]) == 1 for birth in births)


def controls():
    # One even-parity knot on three readers supplies a value-type shared triple.
    _, _, inventory = stage_read(((0, 1, 2),))
    control = inventory((1, 2, 4))
    assert control["inventory"]["triples"] == {
        "from A": 1, "from B": 1, "from M": 1, "fourth route (changes, laws)": [0, 1]}
    assert control["uniform-word value information in bits"] == 0
    return {"one even-parity knot shared by all three readers": control}


def load_archive(path):
    with gzip_open(path, "rt") as source:
        return {(row["family"], row["round"]): row for row in map(json.loads, source)}


def compare_archives(rows, pilot):
    original = load_archive(HERE.parent / "tripartite_out.jsonl.gz")
    predecessor = HERE.parents[1] / "VALUE-CHANGE-20261126-001"
    value_change = {name: load_archive(predecessor / name)
                    for name in ("rings_out.jsonl.gz", "rings_out_frozen.jsonl.gz")}
    mismatches = []
    counters = Counter()

    def compare(label, case, calculated, recorded):
        counters[label] += 1
        if calculated != recorded:
            mismatches.append({"check": label, "case": case, "calculated": calculated, "recorded": recorded})

    if not pilot:
        assert {(r["family"], r["round"]) for r in rows} == original.keys()
    for row in rows:
        stage = row["family"], row["round"]
        archived = {name: count for name, count in original[stage].items() if name.startswith("rings ")}
        measured = row["measurements"]["places"]
        compare("shared-triple partition keys", stage, sorted(measured), sorted(archived))
        for name, count in measured.items():
            compare("shared-triple inventories", (*stage, name), count["inventory"], archived.get(name))
        for file, values in value_change.items():
            prior = values[stage]
            compare(f"{file} knot and distinction counts", stage,
                    [row["knots"], row["distinctions"]], [prior["knots"], prior["distinctions"]])
            for choice, readers in row["measurements"].items():
                for name, count in readers.items():
                    pair = name.split(", middle the rest", 1)[0].replace(" together, ring ", " against ring ")
                    observed = prior[f"readers {choice}, {pair}"]
                    compare(f"{file} reader fields", (*stage, choice, name),
                            [count["uniform-word value information in bits"], count["separated ring readers"],
                             count["distinctions per reader"][:2], count["inventory"]["pairs with the third unread"]["AB"]],
                            [observed["e, middle changes"], observed["separated"], observed["held"],
                             observed["e, middle unread"]])
    return dict(counters), mismatches


def compare_growth(stages, families):
    """Compare literal stages and birth fields after the independent calculation."""
    import sys

    sys.path.insert(0, str(HERE.parents[1] / "BUILT-BINDING-20261126-001"))
    import repro

    fields = ("knot", "parents", "inputs", "fresh", "demand", "implied")
    count = Counter()
    for description, ring_count, size, detour, extra_loose in families:
        reference, _, _ = repro.rings_start(R=ring_count, n=size, link="detour" if detour else "double",
                                            middle_loose=extra_loose)
        for round_number in range(3):
            row, knots = stages[description, round_number]
            if round_number > 0:
                reference, status, births = repro.forbid.grown(reference, "parity", "ordinary")
                assert status == "funded" and len(births) == len(row["births"])
                for birth, original in zip(row["births"], births, strict=True):
                    archive_fields = (original["knot"], original["parents"], original["inputs"], original["fresh"],
                                      original["D"], original["old_inputs_already_imply_law"])
                    assert tuple(birth[field] for field in fields) == archive_fields
                    count["literal birth matches"] += 1
            assert knots == reference
            count["literal stage matches"] += 1
    return dict(count)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pilot", action="store_true")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--check-growth", action="store_true", help="compare literal stages with the reference engine")
    args = parser.parse_args()
    begin = perf_counter()
    rows = []
    stages = {}
    timings = {}
    families = FAMILIES[:1] if args.pilot else FAMILIES
    for family in families:
        start = perf_counter()
        for row, knots in read_family(*family):
            rows.append(row)
            stages[row["family"], row["round"]] = (row, knots)
        timings[family[0]] = perf_counter() - start
    control = controls()
    start = perf_counter()
    checks, mismatches = compare_archives(rows, args.pilot)
    comparison_time = perf_counter() - start
    start = perf_counter()
    growth_checks = compare_growth(stages, families) if args.check_growth else {}
    growth_comparison_time = perf_counter() - start
    result = {"rows": rows, "control": control, "archive comparisons": checks, "archive mismatches": mismatches,
              "growth comparisons": growth_checks,
              "timing": {"family seconds": timings, "archive comparison seconds": comparison_time,
                         "growth comparison seconds": growth_comparison_time,
                         "wall seconds before serialization": perf_counter() - begin,
                         "peak resident KiB": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}}
    summary = {**checks, **growth_checks, "births": sum(len(row["births"]) for row in rows), "mismatches": len(mismatches),
               "seconds": result["timing"]["wall seconds before serialization"]}
    if args.output:
        args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(summary))
    assert not mismatches, mismatches


if __name__ == "__main__":
    main()
