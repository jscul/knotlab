"""Replay the named five-knot closure and its archived exact receipts."""

import argparse
from collections import Counter
from fractions import Fraction
import gzip
from hashlib import sha256
from itertools import combinations, product
import json
from pathlib import Path
import resource
from time import perf_counter


ARCHIVE = (
    Path(__file__).resolve().parents[3]
    / "artifacts/ERASURE-AND-CLOSING-SIGNS-20261121-001B"
    / "ERASURE-AND-CLOSING-SIGNS-20261121-001B-E001_closures"
)
ARCHIVE_FILES = (
    "panels_histories.json.gz", "panels_witnesses.json", "internal_receipts.json.gz"
)
PANEL_ORDER = ("T", "E", "M", "S")


def read_archive(name):
    path = ARCHIVE / name
    reader = gzip.open if path.suffix == ".gz" else Path.open
    with reader(path, "rt") as raw:
        return json.load(raw)


def occurrences(rows):
    held = {}
    for holder, row in enumerate(rows):
        for name in row:
            held.setdefault(name, []).append(holder)
    assert all(1 <= len(holders) <= 2 for holders in held.values())
    return held


def meeting_sets(holder_count, held):
    meetings = [set() for _ in range(holder_count)]
    for owners in held.values():
        if len(owners) == 2:
            left, right = owners
            meetings[left].add(right)
            meetings[right].add(left)
    return meetings


def components(meetings):
    seen = set()
    for holder in range(len(meetings)):
        if holder in seen:
            continue
        current = {holder}
        pending = [holder]
        while pending:
            for other in meetings[pending.pop()] - current:
                current.add(other)
                pending.append(other)
        seen.update(current)
        yield current


def first_groups(rows):
    held = occurrences(rows)
    loose = {owners[0]: [] for owners in held.values() if len(owners) == 1}
    for name, owners in held.items():
        if len(owners) == 1:
            loose[owners[0]].append(name)
    live = sorted(loose)
    witnesses = meeting_sets(len(rows), held)
    pairs = {
        frozenset((a, b)) for a, b in combinations(live, 2)
        if any({a, b} <= witness for witness in witnesses)
    }
    groups = []
    for size in range(len(live), 2, -1):
        for parents in map(frozenset, combinations(live, size)):
            if any(parents <= witness for witness in witnesses + groups):
                continue
            if all(frozenset(pair) in pairs for pair in combinations(parents, 2)):
                groups.append(parents)
    groups.extend(pair for pair in pairs if not any(pair <= group for group in groups))
    cost = Counter(parent for group in groups for parent in group)
    return sorted(tuple(sorted(group)) for group in groups), loose, cost


def named_minimum(histories, witnesses):
    candidates = []
    parity_cuts_read = 0
    for (panel, draw), sample in histories.items():
        for cut in sample["laws"]["parity"]["cuts"]:
            parity_cuts_read += 1
            rows = cut["after_rows"]
            held = occurrences(rows)
            meetings = meeting_sets(len(rows), held)
            for group in components(meetings):
                if len(group) != 5 or any(len(rows[holder]) != 4 for holder in group):
                    continue
                if any(meetings[holder] != group - {holder} for holder in group):
                    continue
                assert len({name for holder in group for name in rows[holder]}) == 10
                new = group.intersection(range(cut["before_holder_count"], len(rows)))
                if not new:
                    continue
                assert len(new) == 1
                terminal = new.pop()
                key = (5, 10, len(rows[terminal]), cut["age"], PANEL_ORDER.index(panel), draw,
                       terminal)
                candidates.append((key, panel, draw, len(rows) == 5))

    # The admitted classification requires either five all-pairs groups or six
    # groups meeting three against three. Below ten names, the latter would
    # have exactly nine names, all between six singleton groups.
    nine_name_pattern = [
        tuple(3 * left + right for right in range(3)) for left in range(3)
    ] + [
        tuple(3 * left + right for left in range(3)) for right in range(3)
    ]
    nine_name_groups, nine_name_loose, nine_name_cost = first_groups(nine_name_pattern[:-1])
    assert nine_name_groups == [(0, 1), (0, 2), (1, 2)]
    assert all(nine_name_cost[h] == 2 > len(nine_name_loose[h]) == 1 for h in range(3))

    key, panel, draw, whole = min(candidates)
    assert whole and (key, panel, draw, whole) == min(c for c in candidates if c[3])
    for label in ("whole", "component", "whole_arity_at_least_three",
                  "component_arity_at_least_three"):
        record = witnesses[label]
        assert (record["panel"], record["draw"], record["age"], record["holder"]) == (
            panel, draw, key[3], key[-1]
        ), label
    return (panel, draw), {
        "parity_cuts_read_for_ties": parity_cuts_read,
        "reached_five_knot_ten_name_candidates": len(candidates),
        "whole_candidates": sum(entry[3] for entry in candidates),
        "ranking_key": key,
        "nine_name_rival_parent_groups": nine_name_groups,
        "nine_name_rival_owed_and_loose": [
            [nine_name_cost[h], len(nine_name_loose[h])] for h in sorted(nine_name_loose)
        ],
    }


def physical_minimum(sample, cut, receipts, witness):
    before = sample["source_rows"]
    groups, loose, cost = first_groups(before)
    assert groups == [tuple(range(4))]
    assert all(len(loose[h]) == cost[h] == 1 for h in range(4))
    inputs = sorted(loose[h][0] for h in range(4))
    row_sum = sorted(name for name, owners in occurrences(before).items() if len(owners) == 1)
    assert row_sum == inputs

    closing = len(before)
    rows = before + [inputs]
    names = sorted(occurrences(rows))
    assert sorted(map(len, occurrences(rows).values())) == [2] * len(names)
    assert cut["after_rows"] == rows == witness["after_rows"] == receipts["physical_rows_in_table_order"]
    assert before == witness["before_rows"] and cut["whole_closed"] and cut["age"] == 1
    assert receipts["physical_names_in_word_integer_order"] == names
    assert receipts["component_physical_holders"] == list(range(len(rows)))
    assert cut["births"] == [{
        "holder": closing, "parents": list(groups[0]), "inputs": inputs, "new_names": [],
        "fresh": 0, "old_span_rows": list(range(closing)), "support": inputs,
    }]
    assert receipts["choice"] == {
        "age": cut["age"], "draw": sample["draw"], "fresh": 0, "holder": closing,
        "panel": sample["panel"], "parents": list(groups[0]),
    }
    return rows, names, closing


def row_masks(rows, names):
    indexes = {name: i for i, name in enumerate(names)}
    return [sum(1 << indexes[name] for name in row) for row in rows]


def parity(word, mask):
    return (word & mask).bit_count() % 2


def allowed_words(masks, charges, width):
    equations = list(zip(masks, charges, strict=True))
    return [word for word in range(1 << width)
            if all(parity(word, mask) == charge for mask, charge in equations)]


def local_word(word, row, positions):
    return sum(((word >> positions[name]) & 1) << i for i, name in enumerate(row))


def drop_bit(word, bit):
    return ((word >> (bit + 1)) << bit) | (word & ((1 << bit) - 1))


def projection_report(words, width):
    bindings = set(words)
    whole_constrained = len(bindings) < 1 << width
    proper_subsets_free = all(
        len({drop_bit(word, bit) for word in bindings}) == 1 << (width - 1)
        for bit in range(width)
    )
    return {
        "allowed": [format(word, f"0{width}b") for word in sorted(bindings)],
        "binding": whole_constrained, "coexistence": bool(bindings),
        "invisible_in_parts": proper_subsets_free,
        "loss_on_erasure": whole_constrained and proper_subsets_free,
    }


def ordinary_replay(rows, names, closing, archived):
    masks = row_masks(rows, names)
    positions = {name: i for i, name in enumerate(names)}
    old = allowed_words(masks[:closing], [0] * closing, len(names))
    terminal_row = rows[closing]
    width = len(terminal_row)
    projected = Counter(local_word(word, terminal_row, positions) for word in old)
    assert len(old) == 64
    assert projected == {word: 8 for word in range(1 << width) if word.bit_count() % 2 == 0}
    result = {}
    for sign, odd in (("even", 0), ("odd", 1)):
        charges = [odd if holder == closing else 0 for holder in range(len(rows))]
        words = allowed_words(masks, charges, len(names))
        assert words == ([] if odd else old)
        omissions = []
        for omit in range(len(rows)):
            reduced = allowed_words(masks[:omit] + masks[omit + 1:],
                                    charges[:omit] + charges[omit + 1:], len(names))
            assert len(reduced) == 64
            omissions.append({"holder": omit, "global_word_count": len(reduced),
                              "least_completion": reduced[0]})
        ordinary = {
            "admitted_complete_words": len(words), "word_integers": words, "polarities": charges,
            "per_deleted_physical_rule": omissions,
            "closing_projection_in_full_whole": projection_report(
                (local_word(word, terminal_row, positions) for word in words), width
            ),
            "closing_rule_in_isolation": projection_report(
                (word for word in range(1 << width) if word.bit_count() % 2 == odd), width
            ),
        }
        assert ordinary == archived[sign], sign
        result[sign] = ordinary
    before_closure = {
        "closed_odd_post_step_trial_count": 0, "each_old_word_even_extensions": 1,
        "each_old_word_single_odd_extensions": 0, "old_state_count": len(old),
        "input_word_multiplicities_in_local_slot_order": [projected[w] for w in range(1 << width)],
        "no_ordinary_answer_trigger_in_roster": True, "ordinary_zero_grant": 0,
    }
    assert before_closure == archived["before_closure"]
    result["before_closure"] = before_closure
    return old, result


def actions_on_basis(exponents, basis):
    """Convert each real Pauli operation to its literal action on basis words."""
    positions = {word: i for i, word in enumerate(basis)}
    return {
        name: tuple(
            (positions[word ^ flip], (-1) ** (phase // 2 + parity(word, diagonal)))
            for word in basis
        )
        for name, (phase, flip, diagonal) in exponents.items()
        if phase % 2 == 0
    }


def five_group_operators(old, closing):
    a, b, c, d = old
    by_pair = {
        (a, b): (0, 1, 0), (a, c): (0, 2, 0), (a, d): (0, 4, 0),
        (b, c): (0, 0, 4), (b, d): (0, 0, 2), (c, d): (0, 0, 1),
    }
    for holder in old:
        flips = signs = 0
        for meeting, (_, flip, sign) in by_pair.items():
            if holder in meeting:
                flips |= flip
                signs |= sign
        assert not flips & signs
        by_pair[tuple(sorted((closing, holder)))] = (0, flips, signs)
    return by_pair


def all_pairs_operators(rows, closing):
    """Assign six single-factor operators and four products by named meetings."""
    old = [holder for holder in range(len(rows)) if holder != closing]
    by_pair = five_group_operators(old, closing)
    held = occurrences(rows)
    assert set(map(tuple, held.values())) == set(by_pair)
    return {name: by_pair[tuple(owners)] for name, owners in held.items()}


def after_operation(action, state):
    column, coefficient = state
    destination, sign = action[column]
    return destination, coefficient * sign


def verify_actions(actions, rows, charges, dimension):
    assert set(actions) == set(occurrences(rows))
    counts = Counter()
    for column in range(dimension):
        start = (column, 1)
        for action in actions.values():
            assert after_operation(action, after_operation(action, start)) == start
            counts["involutions"] += 1
        for row, charge in zip(rows, charges, strict=True):
            for left, right in combinations(row, 2):
                a, b = actions[left], actions[right]
                assert after_operation(a, after_operation(b, start)) == after_operation(
                    b, after_operation(a, start)
                )
                counts["same_holder_commutations"] += 1
            state = start
            for name in row:
                state = after_operation(actions[name], state)
            assert state == (column, (-1) ** charge)
            counts["signed_products"] += 1
    return dict(counts)


def projectors(actions, rows, dimension):
    """Keep integer columns of the product of the unnormalized bit projections."""
    result = []
    for row in rows:
        outcomes = []
        for answer in range(1 << len(row)):
            columns = []
            for origin in range(dimension):
                column = {origin: 1}
                for bit, name in enumerate(row):
                    updated = Counter(column)
                    requested_sign = (-1) ** ((answer >> bit) & 1)
                    for current, coefficient in column.items():
                        destination, sign = actions[name][current]
                        updated[destination] += coefficient * sign * requested_sign
                    column = {index: coefficient for index, coefficient in updated.items() if coefficient}
                columns.append(column)
            outcomes.append(columns)
        result.append(outcomes)
    return result


def one_reader(projected):
    dimension = len(projected[0])
    denominator = len(projected) * dimension
    return tuple(
        Fraction(sum(column.get(index, 0) for index, column in enumerate(columns)), denominator)
        for columns in projected
    )


def check_repeat(projected):
    for columns in projected:
        for column in columns:
            composed = Counter()
            for intermediate, first in column.items():
                for destination, second in columns[intermediate].items():
                    composed[destination] += first * second
            assert {i: value for i, value in composed.items() if value} == {
                i: value * len(projected) for i, value in column.items()
            }


def trace_table(left, right):
    """Probability is the sum of column inner products, divided by dimension."""
    denominator = len(left) * len(right) * len(left[0])
    return tuple(
        Fraction(sum(
            sum(value * column_b.get(index, 0) for index, value in column_a.items())
            for column_a, column_b in zip(columns_a, columns_b, strict=True)
        ), denominator)
        for columns_a, columns_b in product(left, right)
    )


def compare_table(archive, table, shape):
    assert tuple(archive["shape"]) == shape
    assert len(archive["numerators"]) == shape[0] * shape[1] == len(table)
    assert archive["denominator"] > 0
    assert tuple(Fraction(n, archive["denominator"]) for n in archive["numerators"]) == table


def tables_replay(rows, names, old, closing, archive, limit):
    assert archive["odd_sign_at_holder"] == closing
    assert archive["pauli_exponent_convention"] == "i^p X^x Z^z"
    assert Fraction(archive["both_inputs_independent_uniform"]) == Fraction(1, len(rows) ** 2)
    projections = {}
    operator_checks = {}
    marginals = {}
    for sign, odd in (("even", 0), ("odd", 1)):
        carrier = archive["response_summary"][sign]["named_carrier"]
        charges = [odd if holder == closing else 0 for holder in range(len(rows))]
        named = {
            name: (2 * carrier["signs"][str(name)],
                   carrier["flips_in_increasing_physical_name_positions"][str(name)], 1 << position)
            for position, name in enumerate(names)
        }
        variants = [("named_carrier", named, old)]
        if odd:
            archived_paulis = {int(name): exponents for name, exponents in
                               archive["operator_exponents_by_name"].items()}
            variants += [
                ("archived_tensor", archived_paulis, range(1 << archive["operator_tensor_bits"])),
                ("separate_three_factor", all_pairs_operators(rows, closing), range(8)),
            ]
        projections[sign] = {}
        operator_checks[sign] = {}
        for label, exponents, basis in variants:
            assert all(phase in (0, 2) for phase, _, _ in exponents.values())
            device = actions_on_basis(exponents, basis)
            stats = verify_actions(device, rows, charges, len(basis))
            operator_checks[sign][label] = stats
            if label == "named_carrier":
                assert carrier["allowed_before_signed_measurement"] == len(basis)
                assert carrier["source_acceptance"] == "1"
                assert carrier["literal_physical_word_operations"] == {
                    **stats, "accepted_words": len(basis), "carrier_words": len(basis),
                }
            local_projections = projectors(device, rows, len(basis))
            for setting in local_projections:
                check_repeat(setting)
            projections[sign][label] = local_projections
        marginals[sign] = [one_reader(p) for p in projections[sign]["named_carrier"]]
        for holder, local in enumerate(marginals[sign]):
            assert all(value == (Fraction(2, len(local)) if answer.bit_count() % 2 == charges[holder]
                                 else 0) for answer, value in enumerate(local))
            assert archive["response_summary"][sign]["full_same_holder_immediate_repeat"][str(holder)] == "1"

    summarized = {sign: {"all_cells": 0, "positive_cells": 0, "zero_cells": 0,
                         "shared_bit_checks": 0} for sign in projections}
    table_results = []
    all_settings = list(product(range(len(rows)), repeat=2))
    for sign in projections:
        assert len(archive["every_pair_exact_table"][sign]) == len(all_settings)
    for setting_idx, (h, k) in enumerate(all_settings[:limit]):
        width_h, width_k = len(rows[h]), len(rows[k])
        shape = (1 << width_h, 1 << width_k)
        intersection = sorted(set(rows[h]) & set(rows[k]))
        physical = {"holders": [h, k], "common_names": intersection, "shape": shape}
        tables = {}
        for sign, by_variant in projections.items():
            entry = archive["every_pair_exact_table"][sign][setting_idx]
            assert entry["holders"] == [h, k] and entry["common_names"] == intersection
            table = trace_table(by_variant["named_carrier"][h], by_variant["named_carrier"][k])
            compare_table(entry, table, shape)
            for label, kernels in by_variant.items():
                if label != "named_carrier":
                    assert trace_table(kernels[h], kernels[k]) == table, (sign, h, k, label)
            if sign == "even":
                positions = {name: i for i, name in enumerate(names)}
                by_word = Counter((local_word(w, rows[h], positions), local_word(w, rows[k], positions))
                                  for w in old)
                assert tuple(Fraction(by_word[a, b], len(old)) for a, b in
                             product(range(shape[0]), range(shape[1]))) == table

            assert sum(table) == 1 and all(value >= 0 for value in table)
            assert tuple(sum(table[a * shape[1]:(a + 1) * shape[1]])
                         for a in range(shape[0])) == marginals[sign][h]
            assert tuple(sum(table[b::shape[1]]) for b in range(shape[1])) == marginals[sign][k]
            positive = [i for i, probability in enumerate(table) if probability]
            assert len(positive) == (8 if h == k else 32)
            every_positive = Fraction(1, len(positive))
            assert all(table[i] == every_positive for i in positive)
            for cell in positive:
                a, b = divmod(cell, shape[1])
                if h == k:
                    assert a == b
                for name in intersection:
                    assert (a >> rows[h].index(name)) & 1 == (b >> rows[k].index(name)) & 1
            tally = summarized[sign]
            tally["all_cells"] += len(table)
            tally["positive_cells"] += len(positive)
            tally["zero_cells"] += len(table) - len(positive)
            tally["shared_bit_checks"] += len(positive) * len(intersection)
            physical[sign] = {"positive_flat_indices": positive, "positive_probability": str(every_positive)}
            tables[sign] = table
        variation = sum(abs(a - b) for a, b in zip(tables["even"], tables["odd"], strict=True)) / 2
        assert variation == (closing in (h, k))
        assert variation == Fraction(archive["sign_distinction_under_the_two_supplied_preparations"]
                                     ["all_settings_total_variation"][f"{h},{k}"])
        physical["total_variation"] = str(variation)
        table_results.append(physical)

    terminal_marginals = {sign: marginals[sign][closing] for sign in projections}
    width = len(rows[closing])
    proper_subreadings = 0
    for size in range(width):
        for keep in combinations(range(width), size):
            subreadings = []
            for distribution in terminal_marginals.values():
                marginal = Counter()
                for word, probability in enumerate(distribution):
                    marginal[tuple((word >> bit) & 1 for bit in keep)] += probability
                subreadings.append(marginal)
            assert subreadings[0] == subreadings[1]
            assert set(subreadings[0].values()) == {Fraction(1, 1 << size)}
            proper_subreadings += 1
    assert proper_subreadings == 15
    result = {
        "ordered_settings": len(table_results), "settings": table_results, "by_sign": summarized,
        "literal_operator_checks": operator_checks, "terminal_proper_subsets": proper_subreadings,
        "immediate_repeat_probability_at_each_holder": "1",
        "maximum_remote_marginal_total_variation_in_checked_settings": "0",
    }
    if limit == len(all_settings):
        variation = sum(Fraction(row["total_variation"]) for row in table_results) / len(table_results)
        summary = archive["sign_distinction_under_the_two_supplied_preparations"]
        assert variation == Fraction(9, 25) == Fraction(summary["total_variation_including_known_random_settings"])
        assert (1 + variation) / 2 == Fraction(summary["best_joint_equal_prior_success_on_this_supplied_experiment"])
        for sign, tally in summarized.items():
            archived = archive["response_summary"][sign]
            assert tally["all_cells"] == archived["all_cells"] == 6400
            assert tally["positive_cells"] == archived["positive_cells"] == 680
            assert tally["zero_cells"] == 5720
            assert tally["shared_bit_checks"] == archived["checked_shared_bit_identities_on_nonzero_cells"]
        result["total_variation_including_settings"] = str(variation)
        result["best_equal_prior_discrimination_probability"] = str((1 + variation) / 2)
    return terminal_marginals, result


def apply_swap(word, pair):
    pieces = list(word)
    a, b = pair
    pieces[a], pieces[b] = pieces[b], pieces[a]
    return "".join(pieces)


def keeper_replay(keeper, archive, terminal_marginals, width):
    ready = "110"
    swaps = ((1, 2), (0, 2))
    allowed = {
        "parity": [format(w, "03b") for w in range(8) if w.bit_count() % 2 == 0],
        "nae": [format(w, "03b") for w in range(1, 7)],
    }
    assert keeper["physical_ternary_allowed_words"] == allowed
    answers = [apply_swap(ready, swap) for swap in swaps]
    assert answers == [keeper["copied_zero"], keeper["copied_one"]] == ["101", "011"]
    assert keeper["ready"] == keeper["without_supplied_outcome_trigger"] == ready
    assert keeper["outside_sampled_source"]
    for words in allowed.values():
        for answer, swap in zip(answers, swaps, strict=True):
            assert ready in words and answer in words and apply_swap(answer, swap) == ready
    typed_receipts = {}
    for sign, marginal in terminal_marginals.items():
        actual = archive["response_summary"][sign]["external_keeper_at_actual_closing_holder"]
        write = {}
        for word, probability in enumerate(marginal):
            if not probability:
                continue
            bits = [(word >> i) & 1 for i in range(width)]
            write[str(word)] = {
                "status": "success", "probability": str(probability),
                "external_keeper_words": [answers[bit] for bit in bits],
                "swap_at_used_places": [[slot, list(swaps[bit])] for slot, bit in enumerate(bits)],
            }
        expected = {"write": write}
        for policy in ("not_ready", "disconnected"):
            expected[policy] = {"None": {
                "status": policy, "probability": "1", "external_keeper_words": [ready] * width,
                "swap_at_used_places": [],
            }}
        expected["external_failed_intake"] = {
            "external_status": "no_source", "delivered_words": [None, None],
            "external_registers_per_side": [ready] * width,
            "physical_post_step_reader_in_the_empty_odd_ordinary_whole": False,
        }
        assert expected == actual, sign
        typed_receipts[sign] = expected
    return typed_receipts


def find_cut(histories, record, law="parity"):
    sample = histories[record["panel"], record["draw"]]
    cuts = sample["laws"][law]["cuts"]
    cut = next(c for c in cuts if c["age"] == record["age"])
    if law == "parity":
        assert record["after_rows"] == cut["after_rows"]
        assert record["births"] == cut["births"]
        assert record["before_rows"] == cut["after_rows"][:cut["before_holder_count"]]
        assert record["source_rows"] == sample["source_rows"]
    return cut


def affine_count(equations, width):
    pivot = {}
    for mask, charge in equations:
        while mask and mask.bit_length() in pivot:
            previous, sign = pivot[mask.bit_length()]
            mask ^= previous
            charge ^= sign
        if mask:
            pivot[mask.bit_length()] = (mask, charge)
        elif charge:
            return 0
    return 1 << (width - len(pivot))


def scalar_pair_table(rows, axes):
    names = sorted(occurrences(rows))
    zero_rows = list(zip(row_masks(rows, names), [0] * len(rows), strict=True))
    pins = [row_masks([[name] for name in row], names) for row in axes]
    shape = tuple(1 << len(row) for row in axes)
    total = affine_count(zero_rows, len(names))
    return shape, total, tuple(
        Fraction(affine_count(zero_rows + [
            (mask, (answer >> bit) & 1) for answer, row in zip((a, b), pins, strict=True)
            for bit, mask in enumerate(row)
        ], len(names)), total)
        for a, b in product(range(shape[0]), range(shape[1]))
    )


def rotation_count(rows, rotation):
    meetings = meeting_sets(len(rows), occurrences(rows))
    assert len(list(components(meetings))) == 1
    assert all(len(order) == len(set(order)) and set(order) == meetings[h]
               for h, order in rotation.items())
    next_step = {(u, v): (v, order[(order.index(u) + 1) % len(order)])
                 for v, order in rotation.items() for u in order}
    remaining = set(next_step)
    closed_walks = 0
    while remaining:
        first = current = next(iter(remaining))
        while current in remaining:
            remaining.remove(current)
            current = next_step[current]
        assert current == first
        closed_walks += 1
    assert len(rows) - len(next_step) // 2 + closed_walks == 2
    return closed_walks


def negative_control(histories, witness, archived):
    cut = find_cut(histories, witness)
    rows = cut["after_rows"]
    names = sorted(occurrences(rows))
    assert len(rows) == 8 and names == archived["component_place_names"]
    assert archived["holders"] == list(range(len(rows)))
    assert archived["terminal"] == witness["holder"] and cut["whole_closed"]
    masks = row_masks(rows, names)
    even = allowed_words(masks, [0] * len(rows), len(names))
    odd = allowed_words(masks, [int(i == witness["holder"]) for i in range(len(rows))], len(names))
    assert len(even) == archived["ordinary_even_words"] == 32
    assert len(odd) == archived["ordinary_single_odd_words"] == 0
    rotation = {int(u): order for u, order in archived["verified_cyclic_neighbor_orders"].items()}
    cert = witness["closing_event"]["certificate"]
    assert rotation_count(rows, rotation) == rotation_count(rows, dict(cert["rotation"])) == cert["face_count"] == 6
    assert archived["operator_single_odd"] is False
    request = archived["one_disjoint_pair_when_available"]
    a, b = request["actual_holders"]
    assert not set(rows[a]) & set(rows[b])
    shape, total, table = scalar_pair_table(rows, (rows[a], rows[b]))
    assert total == len(even)
    compare_table(request["all_even"], table, shape)
    assert request["odd"] == "strict preparation refused before either holder is requested"
    return {"ordinary_even_words": len(even), "ordinary_odd_words": len(odd),
            "rotation_certificate_verified": True, "strict_odd_refused_before_requests": True,
            "checked_even_disjoint_cells": len(table)}


def positive_grant_control(histories, witness, archived):
    cut = find_cut(histories, witness)
    before, after = witness["before_rows"], cut["after_rows"]
    old_names, names = sorted(occurrences(before)), sorted(occurrences(after))
    assert names[:len(old_names)] == old_names
    old = allowed_words(row_masks(before, names), [0] * len(before), len(old_names))
    fixed = []
    free = []
    taken = set()
    chosen = witness["holder"]
    assert archived["holder"] == chosen
    for birth in cut["births"]:
        fresh = birth["new_names"]
        assert len(fresh) == birth["fresh"] > 0
        assert all(name not in taken and name not in old_names for name in fresh)
        taken.update(fresh)
        fresh_masks = row_masks([[name] for name in fresh], names)
        rule = row_masks([after[birth["holder"]]], names)[0]
        fixed.append((rule, fresh_masks[0]))
        free.extend(fresh_masks[1:])
        if birth["holder"] == chosen:
            assert birth["inputs"] == archived["old_input_names"]
            assert birth["parents"] == archived["parents"]
            assert fresh == archived["fresh_names"]
            assert fresh[0] == archived["chosen_fresh_coordinate_in_bijection"]
            assert 1 << (len(fresh) - 1) == archived["local_extensions_per_given_old_input_at_either_sign"]
    assert taken == set(names) - set(old_names)
    assert len(old) == archived["prior_count"] == 1024
    assert 1 << len(free) == archived["extensions_per_old_word_for_full_cut_at_either_sign"] == 64
    full_masks = row_masks(after, names)
    flip = row_masks([[archived["chosen_fresh_coordinate_in_bijection"]]], names)[0]
    odd_signs = [int(i == chosen) for i in range(len(after))]
    full = set()
    for old_word in old:
        for choice in range(1 << len(free)):
            word = old_word | sum(mask for bit, mask in enumerate(free) if (choice >> bit) & 1)
            for equation, dependent in fixed:
                if parity(word, equation):
                    word |= dependent
            assert all(parity(word, mask) == 0 for mask in full_masks)
            assert [parity(word ^ flip, mask) for mask in full_masks] == odd_signs
            full.add(word)
    assert len(full) == archived["native_word_count"] == archived["same_cut_with_this_sign_reversed"] == 65536
    assert affine_count(zip(full_masks, [0] * len(after), strict=True), len(names)) == len(full)
    assert affine_count(zip(full_masks, odd_signs, strict=True), len(names)) == len(full)
    return {"old_words": len(old), "words_at_either_sign": len(full),
            "fresh_distinction_for_bijection": archived["chosen_fresh_coordinate_in_bijection"]}


def unsigned_control(histories, witness, archived, parity_rows):
    cut = find_cut(histories, witness, "nae")
    assert cut["after_rows"][:-1] == witness["before_rows"] == archived["same_initial_physical_names"]
    assert not cut["whole_closed"]
    assert len(cut["births"]) == 1
    birth = cut["births"][0]
    assert birth["inputs"] == witness["inputs"] and birth["new_names"] == [10]
    assert birth["fresh"] == 1

    counts = []
    for rows in (cut["after_rows"], parity_rows):
        names = sorted(occurrences(rows))
        masks = row_masks(rows, names)
        counts.append(sum(all((word & mask) not in (0, mask) for mask in masks)
                          for word in range(1 << len(names))))
    assert counts == [archived["unsigned_count_on_its_own_reached_cut"],
                      archived["unsigned_count_reinterpreting_the_closed_parity_holdings"]] == [1106, 512]
    assert archived["reinterpreted_cut_was_an_ordinary_NAE_birth_at_that_step"] is False
    return {"actual_unsigned_fresh": birth["new_names"], "actual_unsigned_words": counts[0],
            "reinterpreted_parity_holding_words": counts[1]}


def times_pauli(first, second):
    p, x, z = first
    q, a, b = second
    return (p + q + 2 * parity(z, a)) % 4, x ^ a, z ^ b


def spanning_meetings(start, eligible, neighbors):
    parent_and_name = {start: None}
    pending = [start]
    for here in pending:
        for other, name in sorted(neighbors[here]):
            if other in eligible and other not in parent_and_name:
                parent_and_name[other] = (here, name)
                pending.append(other)
    assert parent_and_name.keys() == eligible
    return parent_and_name


def certificate_operators(rows_by_holder, cert, closing):
    """Lift operators from the certificate's named intergroup meetings."""
    groups = {anchor: set(members) for anchor, members in cert["groups"]}
    membership = {h: anchor for anchor, members in groups.items() for h in members}
    assert len(membership) == sum(map(len, groups.values()))
    assert membership.keys() <= rows_by_holder.keys()
    parts = cert["anchor_parts"]
    if cert["kind"] == "five_all_pairs":
        anchors = parts[0]
        anchor_odd = anchors[-1]
        by_pair = five_group_operators(anchors[:-1], anchor_odd)
    else:
        assert cert["kind"] == "six_three_against_three"
        left, right = parts
        anchor_odd = right[-1]
        expressions = (
            ((0, 1, 0), (0, 2, 0), (0, 3, 0)),
            ((0, 0, 2), (0, 0, 1), (0, 0, 3)),
            ((0, 1, 2), (0, 2, 1), (2, 3, 3)),
        )
        by_pair = {tuple(sorted((a, b))): expressions[i][j]
                   for i, a in enumerate(left) for j, b in enumerate(right)}
    assert set(groups) == {h for pair in by_pair for h in pair}
    holder_ids = list(rows_by_holder)
    named_owners = {name: tuple(holder_ids[i] for i in owners) for name, owners in
                    occurrences(rows_by_holder.values()).items()}
    neighbors = {h: [] for h in holder_ids}
    for name, owners in named_owners.items():
        a, b = owners
        neighbors[a].append((b, name))
        neighbors[b].append((a, name))
    operators = dict.fromkeys(named_owners, (0, 0, 0))
    covered = set()
    for route in cert["paths"]:
        crossings = []
        holders, names = route["holders"], route["named_meetings"]
        for (a, b), name in zip(zip(holders, holders[1:]), names, strict=True):
            assert named_owners[name] == tuple(sorted((a, b)))
            if membership[a] != membership[b]:
                crossings.append((tuple(sorted((membership[a], membership[b]))), name))
        [(pair, name)] = crossings
        assert pair not in covered
        covered.add(pair)
        operators[name] = by_pair[pair]
    assert covered == by_pair.keys()
    for anchor, members in groups.items():
        tree = spanning_meetings(anchor, members, neighbors)
        for holder in reversed(list(tree)[1:]):
            _, inherited = tree[holder]
            result = (0, 0, 0)
            for name in rows_by_holder[holder]:
                if name != inherited:
                    result = times_pauli(result, operators[name])
            operators[inherited] = result
    to_anchor = spanning_meetings(anchor_odd, rows_by_holder.keys(), neighbors)
    holder = closing
    while holder != anchor_odd:
        holder, inherited = to_anchor[holder]
        p, x, z = operators[inherited]
        operators[inherited] = ((p + 2) % 4, x, z)
    return operators


def disjoint_control(histories, witness, archived):
    cut = find_cut(histories, witness)
    rows_by_holder = {h: cut["after_rows"][h] for h in witness["component_holders"]}
    rows = list(rows_by_holder.values())
    closing = witness["holder"]
    other = next(h for h, row in rows_by_holder.items() if not set(row) & set(rows_by_holder[closing]))
    axes = (rows_by_holder[closing], rows_by_holder[other])
    assert archived["ordered_physical_holder_requests"] == [closing, other]
    assert archived["physical_places"] == list(axes)
    assert archived["whole_closed"] == cut["whole_closed"]
    names = sorted(occurrences(rows))
    assert archived["component_counts"] == [len(rows), len(names)]
    shape, total, even = scalar_pair_table(rows, axes)
    assert total == archived["ordinary_even_complete_words"]
    compare_table(archived["even"], even, shape)

    cert = witness["closing_event"]["certificate"]
    operators = certificate_operators(rows_by_holder, cert, closing)
    dimension = 1 << max((x | z).bit_length() for _, x, z in operators.values())
    actions = actions_on_basis(operators, range(dimension))
    stats = verify_actions(actions, rows, [int(h == closing) for h in rows_by_holder], dimension)
    raw_odd = trace_table(*projectors(actions, axes, dimension))
    assert sum(raw_odd) == 1 and all(p >= 0 for p in raw_odd)

    # Tensor with a diagonal uniform even word. Its sign shifts both records.
    positive_even = [(*divmod(i, shape[1]), value) for i, value in enumerate(even) if value]
    odd = tuple(sum(value * raw_odd[(a ^ c) * shape[1] + (b ^ d)] for c, d, value in positive_even)
                for a, b in product(range(shape[0]), range(shape[1])))
    compare_table(archived["odd"], odd, shape)
    return {"checked_cells_per_sign": len(even), "support_even": sum(bool(p) for p in even),
            "support_odd": sum(bool(p) for p in odd), "scalar_even_words": total,
            "positive_named_operator_checks": stats, "whole_closed": cut["whole_closed"]}


def cancellation_cost(rows, exponents):
    """Pair the two copies of each operator, tracking signs of exchanges."""
    names = [name for row in rows for name in row]
    exchanges = 0
    while names:
        first = names[0]
        repeated_at = names.index(first, 1)
        operator = exponents[first]
        for crossed in names[1:repeated_at]:
            other = exponents[crossed]
            exchanges += times_pauli(operator, other) != times_pauli(other, operator)
        names = names[1:repeated_at] + names[repeated_at + 1:]
    return exchanges


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--settings", type=int, choices=range(1, 26), default=25)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    start = perf_counter()
    histories = {(entry["panel"], entry["draw"]): entry for entry in read_archive(ARCHIVE_FILES[0])}
    witnesses = read_archive(ARCHIVE_FILES[1])
    receipts = read_archive(ARCHIVE_FILES[2])
    minimum, ranking = named_minimum(histories, witnesses)
    sample = histories[minimum]
    rows, names, closing = physical_minimum(sample, sample["laws"]["parity"]["cuts"][0],
                                            receipts, witnesses["whole"])
    old, ordinary = ordinary_replay(rows, names, closing, receipts["ordinary"])
    scalar_end = perf_counter()
    terminal_marginals, settings = tables_replay(rows, names, old, closing,
                                                receipts["signed"], args.settings)
    signed_end = perf_counter()
    keeper = keeper_replay(receipts["keeper"], receipts["signed"], terminal_marginals,
                           len(rows[closing]))
    control_data = receipts["sampled_controls"]
    controls = {
        "negative_component": negative_control(histories, witnesses["negative"],
                                                control_data["negative_odd_component"]),
        "positive_fresh": positive_grant_control(histories, witnesses["positive_fresh"],
                                                  control_data["actual_positive_grant"]),
        "unsigned_same_founder": unsigned_control(histories, witnesses["whole"],
                                                  control_data["same_founder_under_NAE"], rows),
    }
    controls["disjoint_positive_settings"] = {
        panel: disjoint_control(histories, witnesses["panels"][panel][role],
                                control_data["disjoint_settings_at_primary_positive_minima"][panel])
        for panel, role in (("T", "whole"), ("M", "continuing_component"))
    }
    even = {name: (0, 0, 1 << position) for position, name in enumerate(names)}
    analytic_odd = all_pairs_operators(rows, closing)
    archived_odd = {int(name): exponents for name, exponents in
                    receipts["signed"]["operator_exponents_by_name"].items()}
    costs = {"even_diagonal": cancellation_cost(rows, even),
             "separate_odd": cancellation_cost(rows, analytic_odd),
             "archived_odd": cancellation_cost(rows, archived_odd)}
    assert costs["even_diagonal"] == 0 and costs["separate_odd"] % 2 == costs["archived_odd"] % 2 == 1
    result = {
        "archive_sha256": {name: sha256((ARCHIVE / name).read_bytes()).hexdigest() for name in ARCHIVE_FILES},
        "named_sample": receipts["choice"], "physical_rows": rows, "physical_names": names,
        "ranking": ranking, "scalar": ordinary, "signed": settings, "external_keeper": keeper,
        "sampled_controls": controls, "anticommuting_exchanges_to_cancel_repeated_names": costs,
        "resources": {
            "seconds": {"archive_ranking_and_scalar": scalar_end - start,
                        "operators_and_tables": signed_end - scalar_end,
                        "keeper_and_controls": perf_counter() - signed_end,
                        "total_before_save": perf_counter() - start},
            "peak_resident_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
            "address_space_limit_bytes": resource.getrlimit(resource.RLIMIT_AS)[0],
            "threads": len(list(Path("/proc/self/task").iterdir())),
        },
    }
    with args.output.open("x") as out:
        json.dump(result, out, indent=2, sort_keys=True)
        out.write("\n")


if __name__ == "__main__":
    main()
