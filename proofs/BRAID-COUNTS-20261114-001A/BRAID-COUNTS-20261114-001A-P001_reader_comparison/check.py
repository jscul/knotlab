#!/usr/bin/env python3
"""Classify later reads by literal crossing and verify the ternary result by coefficients."""

import argparse
import json
from collections import Counter, defaultdict
from itertools import combinations, product
from pathlib import Path
from typing import NamedTuple


READERS = ("existence", "parity", "joint", "count")


def require(condition, message):
    if not condition:
        raise ValueError(message)


class Table(NamedTuple):
    cells: int
    reports: tuple
    differences: tuple


def low_bits(q, slots):
    return sum(1 << (q.bit_length() * i) for i in slots)


def reads_from_counts(q, packed, mask):
    # There is room for q counts per field, so addition has no carry to another field.
    parity = packed & mask
    positive = packed
    for shift in range(1, q.bit_length()):
        positive |= packed >> shift
    positive &= mask
    return positive, parity, positive | (parity << 1), packed


def orbit_records(q, limit):
    width = q.bit_length()
    masks = [low_bits(q, range(q * q)), low_bits(q, range(q))]
    cell_records = []
    for x, d in product(range(q), repeat=2):
        u, v = x, (x + d) % q
        positions = []
        for k in range(q):
            positions.append(k * q + u)
            u, v = v, (2 * v - u) % q
        require((u, v) == (x, (x + d) % q), "crossing period changed")
        cell_records.append((low_bits(q, positions), 1 << (width * d)))

    def make(indices):
        cells = occupied = difference = 0
        for i in indices:
            cells |= 1 << i
            count_word, difference_word = cell_records[i]
            occupied += count_word
            difference += difference_word
        return Table(cells, reads_from_counts(q, occupied, masks[0]),
                     reads_from_counts(q, difference, masks[1]))

    tables = [make(indices) for size in range(limit + 1)
              for indices in combinations(range(q * q), size)]
    return tables, make(tuple(range(q * q)))


def menu_masks(q, slots):
    low = low_bits(q, slots)
    return low, low, 3 * low, ((1 << q.bit_length()) - 1) * low


def histogram(counts):
    return {str(k): v for k, v in sorted(Counter(counts.values()).items())}


def coefficients(q, powers):
    """Multiply (1 + a cell's query monomial) in ordinary integer exponents."""
    tests = list(product(powers, range(q)))
    terms = Counter({(0,) * len(tests): 1})
    for x, d in product(range(q), repeat=2):
        hit = tuple((x + k * d) % q == a for k, a in tests)
        added = Counter({tuple(a + b for a, b in zip(exponents, hit)): multiplicity
                         for exponents, multiplicity in terms.items()})
        terms.update(added)
    return terms


def check_coefficients(q, powers, direct):
    slots = [q * k + a for k in powers for a in range(q)]
    calculated = [Counter() for _ in READERS]
    for exponents, mult in coefficients(q, powers).items():
        answers = [
            tuple(int(c > 0) for c in exponents),
            tuple(c % 2 for c in exponents),
            tuple(int(c > 0) + 2 * (c % 2) for c in exponents),
            exponents,
        ]
        for counts, values in zip(calculated, answers):
            key = sum(v << (q.bit_length() * i) for i, v in zip(slots, values))
            counts[key] += mult
    require(calculated == direct, "coefficient proof and literal crossing differ on a report")


def profiles(q, tables, powers, verify):
    masks = menu_masks(q, [k * q + a for k in powers for a in range(q)])
    direct = [Counter(table.reports[i] & mask for table in tables)
              for i, mask in enumerate(masks)]
    if verify:
        check_coefficients(q, powers, direct)
    return {
        name: {"classes": len(counts), "fixed_bits": (len(counts) - 1).bit_length(),
               "histogram": histogram(counts)}
        for name, counts in zip(READERS, direct)
    }


def pairs_from_mask(q, mask):
    return [list(divmod(i, q)) for i in range(q * q) if mask & (1 << i)]


def distinctions(q, tables, powers):
    """For each failed refinement, directly minimize total size over witness pairs."""
    masks = menu_masks(q, [k * q + a for k in powers for a in range(q)])
    values = {table.cells: [r & mask for r, mask in zip(table.reports, masks)] + [table.cells]
              for table in tables}
    answer = {}
    for weaker, stronger in ((0, 1), (1, 0), (2, 3), (3, 4)):
        groups = defaultdict(list)
        for cells, row in values.items():
            groups[row[weaker]].append(cells)
        best = None
        for members in groups.values():
            for a, b in combinations(members, 2):
                if values[a][stronger] == values[b][stronger]:
                    continue
                sizes = (a.bit_count(), b.bit_count())
                rank = (sum(sizes), max(sizes), min(a, b), max(a, b))
                if best is None or rank < best:
                    best = rank
        require(best is not None, "a strict separation disappeared")
        total, _, a, b = best
        target = (READERS + ("table",))[stronger]
        answer[READERS[weaker] + "_loses_" + target] = {
            "minimum_total_cells": total, "tables_x_d": [pairs_from_mask(q, a), pairs_from_mask(q, b)]}
    for fine, coarse in ((3, 0), (3, 1), (3, 2), (2, 0), (2, 1)):
        decoded = {}
        for row in values.values():
            prior = decoded.setdefault(row[fine], row[coarse])
            require(prior == row[coarse], "one of the claimed refinements failed")
    return answer


def missing_difference(q, tables):
    results = {}
    for base_i, base in enumerate(READERS):
        results[base] = {}
        for extra_i, extra in enumerate(READERS):
            distinct = []
            largest = []
            for n in range(q + 1):
                summary = set()
                for tested in combinations(range(q), n):
                    mask = menu_masks(q, tested)[extra_i]
                    counts = Counter((t.reports[base_i], t.differences[extra_i] & mask)
                                     for t in tables)
                    summary.add((len(counts), max(counts.values())))
                require(len(summary) == 1, "relabeling the tested differences changed the answer")
                size, maximum = summary.pop()
                distinct.append(size)
                largest.append(maximum)
            results[base][extra] = {"classes": distinct, "largest_class": largest}
    return results


def binary_rank(rows):
    basis = {}
    for row in rows:
        while row:
            pivot = row.bit_length() - 1
            if pivot not in basis:
                basis[pivot] = row
                break
            row ^= basis[pivot]
    return len(basis)


def parity_rank_by_added_tests(q):
    points = list(product(range(q), repeat=2))
    original = [sum(1 << i for i, (x, d) in enumerate(points) if (x + k * d) % q == a)
                for k, a in points]
    differences = [sum(1 << i for i, (_, d) in enumerate(points) if d == a) for a in range(q)]
    ranks = []
    for size in range(q + 1):
        outcomes = {binary_rank(original + list(rows)) for rows in combinations(differences, size)}
        require(len(outcomes) == 1, "difference classes had unequal binary ranks")
        ranks.append(outcomes.pop())
    return ranks


def compute():
    result = {}
    for q, limit in ((3, 9), (5, 5)):
        tables, full = orbit_records(q, limit)
        rows = []
        checked = 0
        for size in range(1, q + 1):
            first = None
            for powers in combinations(range(q), size):
                checked += 1
                profile = profiles(q, tables, powers, q == 3)
                if first is not None:
                    require(first == profile, "profiles changed with power labels")
                    continue
                first = profile
                row = {"powers": list(powers), "readers": profile}
                if q == 3:
                    row["separators"] = distinctions(q, tables, powers)
                rows.append(row)
        # The full table and each constant-difference table have positive odd counts.
        fibres = [sum(1 << (q * x + d) for x in range(q)) for d in range(q)]
        one_fibre = next(t for t in tables if t.cells == fibres[0])
        require(full.reports[2] == one_fibre.reports[2] and full.reports[3] != one_fibre.reports[3],
                "dense counterexample no longer separates joint and exact counts")
        section = {"tables": len(tables), "maximum_size": limit, "menus": checked, "results": rows,
                   "parity_rank_with_added_differences": parity_rank_by_added_tests(q)}
        if q == 3:
            joint = [t.cells for t in tables if t.reports[2] == full.reports[2]]
            require(set(joint) == {full.cells, *fibres}, "the four-way joint class changed")
            section["largest_joint_class_x_d"] = [pairs_from_mask(q, t) for t in joint]
            section["difference_queries"] = missing_difference(q, tables)
        result[str(q)] = section
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true", help="emit the complete certificate data")
    parser.add_argument("--expected", type=Path, default=Path(__file__).with_name("comparison.json"))
    args = parser.parse_args()
    result = compute()
    if args.emit:
        print(json.dumps(result, indent=2))
        return
    require(result == json.loads(args.expected.read_text()), "recomputed result differs from saved certificate")
    print(json.dumps({
        "status": "passed",
        "ternary_tables": result["3"]["tables"], "ternary_menus": result["3"]["menus"],
        "ternary_classes_by_menu": [[r["readers"][k]["classes"] for k in READERS]
                                    for r in result["3"]["results"]],
        "reader_order": list(READERS),
        "ternary_full_menu": result["3"]["results"][-1]["readers"],
        "five_label_sparse_tables": result["5"]["tables"], "five_label_menus": result["5"]["menus"],
        "five_label_sparse_full_classes": [result["5"]["results"][-1]["readers"][k]["classes"] for k in READERS],
        "five_label_ranks_by_difference_count": result["5"]["parity_rank_with_added_differences"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
