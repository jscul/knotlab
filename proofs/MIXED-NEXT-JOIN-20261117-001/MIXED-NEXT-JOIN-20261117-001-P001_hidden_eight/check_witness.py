"""Two full-state witness checks for next joins after the attached-eight restriction."""

from __future__ import annotations

import hashlib
import importlib.util
import json
from collections import Counter
from functools import reduce
from itertools import combinations, product
from operator import xor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SOURCE = (
    ROOT / "proofs" / "CUBIC-FROM-A-KNOT-20261117-001"
    / "CUBIC-FROM-A-KNOT-20261117-001-P001_local_growth" / "check.py"
)
SOURCE_DIGEST = "038a6845675cbc158e1abd0b55e72addd935c4dee9e6bb8153abe82a543894e8"
AXES = "xyz"
VERTICES = tuple(product((0, 1), repeat=3))
ATTACHMENT = ("new0", "new1", "new2")
NEXT_FRESH = ("later0", "later1", "later2")
Checks = dict[str, tuple[str, ...]]


def load_rules():
    assert hashlib.sha256(SOURCE.read_bytes()).hexdigest() == SOURCE_DIGEST
    spec = importlib.util.spec_from_file_location("cubic_rules", SOURCE)
    rules = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(rules)
    return rules


def name(vertex: tuple[int, ...]) -> str:
    return "".join(map(str, vertex))


def port(axis: int, vertex: tuple[int, ...]) -> str:
    return AXES[axis] + name(vertex)


def base_model() -> tuple[Checks, tuple[str, ...], tuple[int, ...]]:
    checks = {}
    for vertex in VERTICES:
        incoming = tuple(
            port(axis, tuple(0 if i == axis else value for i, value in enumerate(vertex)))
            for axis, value in enumerate(vertex) if value
        )
        checks[name(vertex)] = incoming + tuple(port(axis, vertex) for axis in range(3))
    marked = tuple(port(2, vertex) for vertex in VERTICES)
    full = (1 << len(marked)) - 1
    words = {0, full}
    for axis in range(3):
        word = sum(point[axis] << index for index, point in enumerate(VERTICES))
        words.update((word, word ^ full))
    assert len(words) == 8
    return checks, marked, tuple(sorted(words))


def packed(word: int, positions: tuple[int, ...]) -> int:
    return sum(((word >> source) & 1) << index for index, source in enumerate(positions))


def enumerate_rows(checks: Checks, marked: tuple[str, ...],
                   cut_words: tuple[int, ...]) -> tuple[tuple[str, ...], frozenset[int], dict]:
    """Eliminate a parity matrix once, keeping each RHS as a mask of marked values."""
    labels = tuple(sorted({bit for check in checks.values() for bit in check}))
    positions = {bit: index for index, bit in enumerate(labels)}
    equations = tuple(sum(1 << positions[bit] for bit in check) for check in checks.values())
    mark_positions = tuple(positions[bit] for bit in marked)
    pivots = {}
    system = [(equation, 0) for equation in equations]
    system.extend((1 << position, 1 << index) for index, position in enumerate(mark_positions))
    for equation, rhs in system:
        while equation:
            pivot = equation.bit_length() - 1
            if pivot not in pivots:
                pivots[pivot] = equation, rhs
                break
            existing, previous_rhs = pivots[pivot]
            equation ^= existing
            rhs ^= previous_rhs
        else:
            raise AssertionError("The parity/marked equations are not independent")
    ordered = tuple(sorted(pivots.items()))

    def solve(free_values: int, marked_values: int) -> int:
        result = free_values
        for pivot, (equation, rhs) in ordered:
            if ((equation & result).bit_count() ^ (rhs & marked_values).bit_count()) & 1:
                result |= 1 << pivot
        return result

    kernel = [0]
    for position in range(len(labels)):
        if position not in pivots:
            generator = solve(1 << position, 0)
            kernel.extend(tuple(row ^ generator for row in kernel))
    rows = frozenset(solve(0, marked_values) ^ vector
                     for marked_values in cut_words for vector in kernel)
    assert all(not (equation & row).bit_count() & 1 for equation in equations for row in rows)
    hist = Counter(packed(row, mark_positions) for row in rows)
    assert hist == {word: len(kernel) for word in cut_words}
    return labels, rows, {
        "distinctions": len(labels),
        "junctions": len(checks),
        "rank_with_marked_coordinates_fixed": len(pivots),
        "rows_per_cut_word": len(kernel),
        "allowed_rows": len(rows),
        "row_digest": hashlib.sha256(b"".join(
            row.to_bytes((len(labels) + 7) // 8, "little") for row in sorted(rows)
        )).hexdigest(),
    }


def direct_extensions(old_labels: tuple[str, ...], new_labels: tuple[str, ...],
                      old_rows: frozenset[int], consumed: tuple[str, ...]) -> frozenset[int]:
    embedding = tuple(new_labels.index(bit) for bit in old_labels)
    add_masks = tuple(
        sum(((value >> index) & 1) << new_labels.index(bit)
            for index, bit in enumerate(ATTACHMENT))
        for value in range(8)
    )
    consumed_mask = sum(1 << old_labels.index(bit) for bit in consumed)
    out = set()
    for word in old_rows:
        transferred = sum(((word >> source) & 1) << target for source, target in enumerate(embedding))
        parity = (word & consumed_mask).bit_count() & 1
        out.update(transferred | mask for mask in add_masks if mask.bit_count() & 1 == parity)
    return frozenset(out)


def reflection_check(rules, checks: Checks, marked: tuple[str, ...], cut_words: tuple[int, ...],
                     labels: tuple[str, ...], rows: frozenset[int]) -> dict:
    permutation = dict.fromkeys(labels)
    for vertex in VERTICES:
        x, y, z = vertex
        for axis in range(3):
            source = port(axis, vertex)
            permutation[source] = port(1 - axis, (y, x, z)) if z == 1 and axis < 2 else source
    assert set(permutation.values()) == set(labels)
    assert all(permutation[bit] == bit for bit in marked)
    marked_id = {bit: i for i, bit in enumerate(marked)}
    assert all(
        len({
            ((word >> marked_id[port(2, (x, y, 0))])
             ^ (word >> marked_id[port(2, (x, y, 1))])) & 1
            for x, y in product((0, 1), repeat=2)
        }) == 1 for word in cut_words
    )
    positions = tuple(labels.index(permutation[label]) for label in labels)
    assert {
        sum(((row >> index) & 1) << target for index, target in enumerate(positions))
        for row in rows
    } == rows
    illegal = ("z101", "x101")
    legal = tuple(permutation[bit] for bit in illegal)
    assert legal == ("z101", "y011")
    assert not rules.legal_local_move(checks, illegal, ATTACHMENT)
    assert rules.legal_local_move(checks, legal, ATTACHMENT)
    users, neighbors = rules.incidence(checks)
    legal_parents = tuple(users[bit][0] for bit in legal)
    assert all(len(users[bit]) == 1 for bit in illegal + legal)
    return {
        "allowed_rows_checked": len(rows),
        "nontrivial_swaps": [(bit, image) for bit, image in sorted(permutation.items()) if bit < image],
        "fixed_marked_bits": marked,
        "same_producer_pair": illegal,
        "same_producer": users[illegal[0]][0],
        "reflected_legal_pair": legal,
        "reflected_parents": legal_parents,
        "common_neighbors": sorted(neighbors[legal_parents[0]] & neighbors[legal_parents[1]]),
        "exact_state_preserving": True,
    }


def serial_options(rules, checks: Checks) -> set[tuple[str, ...]]:
    users, _ = rules.incidence(checks)
    loose = sorted(bit for ports in rules.loose_ports(users).values() for bit in ports)
    return {
        group for size in (1, 2, 3) for group in combinations(loose, size)
        if rules.legal_local_move(checks, group, NEXT_FRESH)
    }


def parallel_outcome(rules, checks: Checks) -> dict:
    try:
        groups, _ = rules.parent_groups(checks)
    except ValueError as error:
        return {"available": False, "reason": str(error)}
    return {"available": True, "group_count_by_size": dict(Counter(map(len, groups)))}


def successor_check(rules, checks: Checks, marked: tuple[str, ...], cut_words: tuple[int, ...],
                    old_labels: tuple[str, ...], old_rows: frozenset[int]) -> dict:
    a, b, c, d = "z001", "z101", "z011", "z111"
    diagonals = (a, d), (b, c)
    assert all(
        ((word >> marked.index(a)) ^ (word >> marked.index(b))
         ^ (word >> marked.index(c)) ^ (word >> marked.index(d))) & 1 == 0
        for word in cut_words
    )
    assert all(rules.legal_local_move(checks, consumed, ATTACHMENT) for consumed in diagonals)
    models = tuple({**checks, "arrival": consumed + ATTACHMENT} for consumed in diagonals)
    first, second = (enumerate_rows(model, marked, cut_words) for model in models)
    labels, rows, dimensions = first
    assert first == second and dimensions["allowed_rows"] == 8192
    assert all(direct_extensions(old_labels, labels, old_rows, pair) == rows for pair in diagonals)
    possible_a, possible_b = (serial_options(rules, model) for model in models)
    assert (a,) not in possible_a and (a,) in possible_b

    ordered_rows = tuple(sorted(rows))
    columns = {
        bit: sum(((word >> position) & 1) << row_index for row_index, word in enumerate(ordered_rows))
        for position, bit in enumerate(labels)
    }

    def signature(consumed: tuple[str, ...]) -> int:
        return reduce(xor, (columns[bit] for bit in consumed), 0)

    functions_a, functions_b = ({signature(move) for move in roster}
                                for roster in (possible_a, possible_b))
    mimics = sorted(move for move in possible_a if signature(move) == columns[a])
    assert not mimics, "An A-join reproduces the singleton relation"
    return {
        **dimensions,
        "A_consumed": diagonals[0],
        "B_consumed": diagonals[1],
        "common_fresh_bits": ATTACHMENT,
        "complete_allowed_row_sets_equal": True,
        "direct_truth_table_agreement": True,
        "serial_literal_options_by_arity": {
            "A": dict(Counter(map(len, possible_a))),
            "B": dict(Counter(map(len, possible_b))),
        },
        "serial_literal_option_counts": {
            "A": len(possible_a), "B": len(possible_b), "shared": len(possible_a & possible_b),
        },
        "next_parity_function_counts": {
            "A": len(functions_a), "B": len(functions_b), "shared": len(functions_a & functions_b),
            "A_only": len(functions_a - functions_b), "B_only": len(functions_b - functions_a),
        },
        "one_parent_witness": {
            "bit": a,
            "legal_in_A": False,
            "legal_in_B": True,
            "functionally_matching_A_options_of_any_arity": mimics,
        },
        "parallel_outcomes": {label: parallel_outcome(rules, model)
                              for label, model in zip(("A", "B"), models)},
        "extension_comparison_scope": "Next parity functions on the same named old rows",
    }


def run() -> dict:
    rules = load_rules()
    checks, marked, cut_words = base_model()
    labels, rows, dimensions = enumerate_rows(checks, marked, cut_words)
    assert dimensions["allowed_rows"] == 2048 and len(labels) == 24
    return {
        "predecessor_rule_sha256": SOURCE_DIGEST,
        "cut_words_in_marked_bit_order": cut_words,
        "base": dimensions,
        "reflection": reflection_check(rules, checks, marked, cut_words, labels, rows),
        "equal_state_successors": successor_check(rules, checks, marked, cut_words, labels, rows),
    }


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, sort_keys=True))
