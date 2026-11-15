#!/usr/bin/env python3
"""Replay crossing reads, count their classes independently and check the saved census."""

import argparse
import json
from collections import Counter, defaultdict
from itertools import combinations, product
from pathlib import Path


def require(condition, message):
    if not condition:
        raise ValueError(message)


def tables_by_size(q, limit):
    """Literal crossing on original ordered pairs. Each table takes the OR of its pair reads."""
    pair_reads = []
    for x, y in product(range(q), repeat=2):
        u, v = x, y
        reads = 0
        for power in range(q):
            reads |= 1 << (q * power + u)
            u, v = v, (2 * v - u) % q
        require((u, v) == (x, y), "crossing failed to return to its ordered input")
        pair_reads.append(reads)

    tables = []
    for size in range(limit + 1):
        level = []
        for entries in combinations(range(q * q), size):
            reads = 0
            table = 0
            for entry in entries:
                table |= 1 << entry
                reads |= pair_reads[entry]
            level.append((table, reads))
        tables.append(level)
    return tables


def menu_mask(q, powers):
    return sum(((1 << q) - 1) << (q * k) for k in powers)


def submasks(mask):
    remaining = mask
    while remaining:
        yield remaining
        remaining = (remaining - 1) & mask
    yield 0


def count_by_inclusion_exclusion(q, powers):
    """Work in (x,d). Count all subtable choices under a proposed set of yes answers."""
    mask = menu_mask(q, powers)
    cumulative = {}
    for report in submasks(mask):
        cells = sum(
            all(report & (1 << (q * k + (x + k * d) % q)) for k in powers)
            for x, d in product(range(q), repeat=2)
        )
        cumulative[report] = 1 << cells
    exact = {}
    for report in submasks(mask):
        size = sum(
            (-1) ** ((report ^ subset).bit_count()) * cumulative[subset]
            for subset in submasks(report)
        )
        require(size >= 0, "negative class size from inclusion–exclusion")
        if size:
            exact[report] = size
    return exact


def smallest_disjoint(tables, mask):
    """Search cardinalities in order, including sizes below the theoretical minimum."""
    for size, level in enumerate(tables[1:], 1):
        seen = defaultdict(list)
        for table, reads in level:
            others = seen[reads & mask]
            for other in others:
                if not (table & other):
                    return size, other, table
            others.append(table)
    raise ValueError("no disjoint equal-size ambiguity in the search range")


def pair_list(q, table):
    return [list(divmod(i, q)) for i in range(q * q) if table & (1 << i)]


def sorted_counts(counts):
    return {str(key): value for key, value in sorted(counts.items())}


def census(q, limit):
    tables = tables_by_size(q, limit)
    require(sum(map(len, tables)) == {3: 512, 5: 68406}[q], "wrong table coverage")
    by_menu_size = []
    menus_checked = 0
    for length in range(1, q + 1):
        canonical = None
        for powers in combinations(range(q), length):
            menus_checked += 1
            mask = menu_mask(q, powers)
            counts = Counter(reads & mask for level in tables for _, reads in level)
            for level in tables[:length]:
                require(all(counts[reads & mask] == 1 for _, reads in level),
                        "a table below the proposed ambiguity size was confused")
            minimum, left, right = smallest_disjoint(tables, mask)
            require(minimum == length, "the first disjoint confusion changed")
            if q == 3:
                exact = count_by_inclusion_exclusion(q, powers)
                require(dict(counts) == exact, "crossing and inclusion–exclusion disagree")
            profile = {
                "distinct_reports": len(counts),
                "classes_by_class_size": sorted_counts(Counter(counts.values())),
                "minimum_disjoint_equal_size": minimum,
            }
            if canonical is not None:
                require(profile == canonical, "menus of the same size have different profiles")
                continue
            canonical = profile
            row = {
                "powers": list(powers),
                "distinct_reports": len(counts),
                "minimum_disjoint_equal_size": minimum,
                "minimal_witness_original_pairs": [pair_list(q, left), pair_list(q, right)],
            }
            if q == 3:
                row.update({
                    "fixed_message_bits": (len(counts) - 1).bit_length(),
                    "number_of_classes_by_class_size": profile["classes_by_class_size"],
                    "all_values_class_by_table_size": sorted_counts(Counter(
                        size for size, level in enumerate(tables)
                        for _, reads in level if (reads & mask) == mask)),
                    # Canonical powers are consecutive from zero, so this is the
                    # class size for each possible Boolean answer vector, zeros included.
                    "class_sizes_in_binary_report_order": [
                        counts[report] for report in range(1 << (q * length))
                    ],
                })
            by_menu_size.append(row)
    return tables, by_menu_size, menus_checked


def marginal_control(tables):
    q = 3
    first_two = menu_mask(q, (0, 1))
    by_marginals = defaultdict(Counter)
    by_table = {}
    for level in tables:
        for table, reads in level:
            by_marginals[reads & first_two][reads >> 6] += 1
            by_table[table] = reads
    diagonal = (1 << 0) | (1 << 4)    # (0,0), (1,1)
    exchanged = (1 << 1) | (1 << 3)  # (0,1), (1,0)
    left, right = by_table[diagonal], by_table[exchanged]
    require((left & first_two) == (right & first_two),
            "altered-read control has different original marginal supports")
    require((left >> 6, right >> 6) == (3, 4),
            "repeated crossing failed to distinguish the two tables")
    require((right & 7) != (right >> 6),
            "doing nothing twice incorrectly reproduced the true second crossing")
    return {
        "original_marginal_reports": len(by_marginals),
        "tables_whose_marginals_determine_the_whole_third_support": sum(
            sum(counts.values()) for counts in by_marginals.values() if len(counts) == 1),
        "best_uniform_correct_whole_third_support_from_marginals": sum(
            max(counts.values()) for counts in by_marginals.values()),
        "number_of_tables": len(by_table),
    }


def compute():
    ternary_tables, ternary, ternary_menus = census(3, 9)
    five_tables, five, five_menus = census(5, 5)
    return {
        "ternary_menus_checked": ternary_menus,
        "ternary_tables": sum(map(len, ternary_tables)),
        "ternary": ternary,
        "ternary_marginal_reader": marginal_control(ternary_tables),
        "five_label_sparse_menus_checked": five_menus,
        "five_label_sparse_max_table_size": len(five_tables) - 1,
        "five_label_sparse_tables": sum(map(len, five_tables)),
        "five_label_sparse": five,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true", help="print the recomputed scientific data")
    parser.add_argument("--expected", type=Path, default=Path(__file__).with_name("census.json"),
                        help="expected census to compare against in normal check mode")
    args = parser.parse_args()
    data = compute()
    if args.emit:
        print(json.dumps(data, indent=2))
        return
    require(data == json.loads(args.expected.read_text()), "recomputed result differs from the census")
    print(json.dumps({
        "status": "passed",
        "ternary_menus_checked": data["ternary_menus_checked"],
        "ternary_tables": data["ternary_tables"],
        "ternary_answer_classes": [row["distinct_reports"] for row in data["ternary"]],
        "ternary_fixed_bits": [row["fixed_message_bits"] for row in data["ternary"]],
        "ternary_class_profiles": [row["number_of_classes_by_class_size"] for row in data["ternary"]],
        "ternary_disjoint_minima": [row["minimum_disjoint_equal_size"] for row in data["ternary"]],
        "ternary_marginal_reader": data["ternary_marginal_reader"],
        "five_label_sparse_menus_checked": data["five_label_sparse_menus_checked"],
        "five_label_sparse_tables": data["five_label_sparse_tables"],
        "five_label_sparse_answer_classes": [row["distinct_reports"] for row in data["five_label_sparse"]],
        "five_label_disjoint_minima": [row["minimum_disjoint_equal_size"] for row in data["five_label_sparse"]],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
