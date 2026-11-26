"""Exact independent calculation for the nine-mode fermionic referee check.

Use the exterior basis with creators written in ascending basis order.
Apply chronological operations on the left. A named creator product,
such as c_y† c_z†, acts right to left. Drop positive common normalization
factors until probabilities, which are stored as integer ratios.
"""

import argparse
from fractions import Fraction
from functools import cache
from itertools import combinations, permutations, product
import json
from math import gcd
from pathlib import Path


READERS = "abc"
ORDERS = tuple(permutations(range(3)))
WORDS = tuple(product((0, 1), repeat=3))
EVEN_WORDS = tuple(word for word in WORDS if sum(word) % 2 == 0)
PAIR_ORDERS = tuple(product(("yz", "zy"), repeat=3))
RECORDS = tuple(product("yz", repeat=3))
FLIPS = tuple(product("12", repeat=3))
SCORED_SETTINGS = (0, 6, 5, 3)  # ZZZ, FFZ, FZF, ZFF
DIMENSION = 2**9


def label(order):
    return "".join(READERS[reader] for reader in order)


def signed_sum(*states):
    combined = {}
    for state in states:
        for mask, coefficient in state.items():
            combined[mask] = combined.get(mask, 0) + coefficient
    return {mask: coefficient for mask, coefficient in combined.items() if coefficient}


def sign(parity):
    return (-1) ** (parity % 2)


def ladder(mask, mode, dagger):
    bit = 1 << mode
    if bool(mask & bit) == dagger:
        return None
    return mask ^ bit, sign((mask & (bit - 1)).bit_count())


def create(state, mode):
    created = {}
    for mask, coefficient in state.items():
        result = ladder(mask, mode, True)
        if result is not None:
            target, phase = result
            created[target] = phase * coefficient
    return created


def majorana(mask, mode, difference=False):
    # difference=True represents gamma'/i = c† - c.
    dagger = not bool(mask & (1 << mode))
    target, phase = ladder(mask, mode, dagger)
    if difference and not dagger:
        phase = -phase
    return target, phase


@cache
def occupation_read(x):
    return tuple((mask, sign(mask >> x)) for mask in range(DIMENSION))


@cache
def pair_flip(x, record, flip):
    action = []
    for mask in range(DIMENSION):
        toggled, phase = majorana(mask, record, difference=(flip == "2"))
        target, second_phase = majorana(toggled, x, difference=(flip == "1"))
        # F1 = (gamma'_x/i) gamma_record. F2 = -gamma_x (gamma'_record/i).
        action.append((target, phase * second_phase if flip == "1" else -phase * second_phase))
    return tuple(action)


def readers(modes, records, flips):
    return tuple(
        (occupation_read(x), pair_flip(x, y if record == "y" else z, flip))
        for (x, y, z), record, flip in zip(modes, records, flips, strict=True)
    )


def basis(order, within=(0, 1, 2)):
    names = [(reader, mode) for reader in order for mode in within]
    return tuple(tuple(names.index((reader, mode)) for mode in range(3)) for reader in range(3))


def old_word(mask, modes):
    return tuple((mask >> x) & 1 for x, _, _ in modes)


def initial_state(modes, chronology):
    state = {}
    for word in EVEN_WORDS:
        term = {0: 1}
        for reader in chronology:
            if word[reader]:
                term = create(term, modes[reader][0])
        state.update(term)
    return state


def birth(state, triplet, pair_order):
    x, y, z = triplet
    left, right = (y, z) if pair_order == "yz" else (z, y)
    empty_parent = {mask: c for mask, c in state.items() if (mask >> x) & 1 == 0}
    occupied_parent = {mask: c for mask, c in state.items() if (mask >> x) & 1}
    return signed_sum(
        empty_parent,
        create(create(empty_parent, right), left),
        create(occupied_parent, y),
        create(occupied_parent, z),
    )


def grow(start, modes, chronology, pair_orders):
    state = start
    for reader in chronology:
        state = birth(state, modes[reader], pair_orders[reader])
    return state


def transport(state, old_basis, new_basis):
    # Reorder each occupied exterior product by the signed coordinate change.
    positions = {
        old: new
        for old_triplet, new_triplet in zip(old_basis, new_basis, strict=True)
        for old, new in zip(old_triplet, new_triplet, strict=True)
    }
    moved = {}
    for mask, coefficient in state.items():
        new_order = [positions[p] for p in range(9) if (mask >> p) & 1]
        inversions = sum(left > right for left, right in combinations(new_order, 2))
        moved[sum(1 << p for p in new_order)] = coefficient * sign(inversions)
    return moved


def apply(action, state):
    transformed = {}
    for mask, coefficient in state.items():
        target, phase = action[mask]
        transformed[target] = phase * coefficient
    return transformed


def reduce_table(denominator, numerators):
    assert all(value >= 0 for value in numerators)
    assert all(sum(numerators[row : row + 8]) == denominator for row in range(0, 64, 8))
    divisor = gcd(denominator, *numerators)
    return denominator // divisor, tuple(value // divisor for value in numerators)


MOMENT_INDICES = tuple(
    tuple(
        sum(included * (1 + setting) * 3 ** (2 - reader)
            for reader, (included, setting) in enumerate(zip(subset, settings, strict=True)))
        for subset in WORDS
    )
    for settings in WORDS
)
CHARACTERS = tuple(
    tuple(sign(sum(left * right for left, right in zip(subset, outcomes, strict=True))) for subset in WORDS)
    for outcomes in WORDS
)


def table(state, measurements):
    """Recover joint probabilities from the commuting projector expansion."""
    transformed = [state]
    for read, flip in measurements:
        transformed = [
            image
            for source in transformed
            for image in (source, apply(read, source), apply(flip, source))
        ]
    moments = [
        sum(coefficient * state.get(mask, 0) for mask, coefficient in image.items())
        for image in transformed
    ]
    numerators = [
        sum(character * moments[index] for character, index in zip(characters, indices, strict=True))
        for indices in MOMENT_INDICES
        for characters in CHARACTERS
    ]
    return reduce_table(8 * moments[0], numerators)


def projector_table(state, measurements):
    """Independent probability calculation by successive local projections."""
    numerators = []
    for settings in WORDS:
        branches = [state]
        for setting, local in zip(settings, measurements, strict=True):
            split = []
            for branch in branches:
                image = apply(local[setting], branch)
                split.append(signed_sum(branch, image))
                split.append(signed_sum(branch, {mask: -c for mask, c in image.items()}))
            branches = split
        numerators.extend(sum(c * c for c in branch.values()) for branch in branches)
    return reduce_table(64 * sum(c * c for c in state.values()), numerators)


def ghz_target():
    numerators = []
    for settings in WORDS:
        for outcomes in WORDS:
            if sum(settings) % 2:
                numerator = 1
            else:
                required_parity = sum(settings) // 2
                numerator = 2 * (sum(outcomes) % 2 == required_parity)
            numerators.append(numerator)
    return reduce_table(8, tuple(numerators))


def correlations(probability_table):
    denominator, numerators = probability_table
    return tuple(
        Fraction(sum(sign(outcome.bit_count()) * numerators[8 * setting + outcome]
                     for outcome in range(8)), denominator)
        for setting in SCORED_SETTINGS
    )


def is_full(values):
    zzz, ffz, fzf, zff = values
    return zzz * ffz * fzf * zff == -1


def win(values):
    zzz, ffz, fzf, zff = values
    return Fraction(1, 2) + (zzz - ffz - fzf - zff) / 8


def mermin_max(values):
    return max(
        sum(coefficient * value for coefficient, value in zip(coefficients, values, strict=True))
        for coefficients in product((-1, 1), repeat=4)
        if coefficients.count(-1) % 2
    )


def occupied_inversion(order, other_order, left, right):
    return (order.index(left) < order.index(right)) != (other_order.index(left) < other_order.index(right))


def predicted_correlations(parents, commits, pair_orders, records, flips):
    """Pair cocycle and effective local overlaps in the grouped basis."""
    # F1 compresses to -X when reading the left creator in the written
    # product, otherwise to zero. F2 compresses to +X in the other case.
    overlaps = tuple(
        (-1 if flip == "1" else 1) if (read == pair_order[0]) == (flip == "1") else 0
        for pair_order, read, flip in zip(pair_orders, records, flips, strict=True)
    )
    relative_parities = tuple(
        occupied_inversion(parents, commits, left, right)
        for left, right in combinations(range(3), 2)
    )
    if sum(relative_parities) % 2:
        return (1, 0, 0, 0)
    return (1, *(-sign(parity) * overlaps[left] * overlaps[right]
                 for parity, (left, right) in zip(relative_parities, combinations(range(3), 2), strict=True)))


def check_operators(modes):
    def anticommute(mask, left, right):
        terms = []
        for first, second in ((right, left), (left, right)):
            if first[mask] is not None:
                intermediate, phase = first[mask]
                if second[intermediate] is not None:
                    target, second_phase = second[intermediate]
                    terms.append({target: phase * second_phase})
        return signed_sum(*terms)

    creations = tuple(tuple(ladder(mask, mode, True) for mask in range(DIMENSION)) for mode in range(9))
    annihilations = tuple(tuple(ladder(mask, mode, False) for mask in range(DIMENSION)) for mode in range(9))
    for left, right in product(range(9), repeat=2):
        for mask in range(DIMENSION):
            assert anticommute(mask, creations[left], creations[right]) == {}
            assert anticommute(mask, annihilations[left], annihilations[right]) == {}
            assert anticommute(mask, creations[left], annihilations[right]) == ({mask: 1} if left == right else {})

    local_actions = tuple(
        (occupation_read(x), *(pair_flip(x, record, flip) for record in (y, z) for flip in "12"))
        for x, y, z in modes
    )
    for group in local_actions:
        for action in group:
            for mask, (target, phase) in enumerate(action):
                assert action[target] == (mask, phase)
                assert (mask.bit_count() - target.bit_count()) % 2 == 0
    for left_group, right_group in combinations(local_actions, 2):
        for left, right in product(left_group, right_group):
            for mask in range(DIMENSION):
                partial, phase = right[mask]
                target, second_phase = left[partial]
                other_partial, other_phase = left[mask]
                other_target, other_second_phase = right[other_partial]
                assert (target, phase * second_phase) == (other_target, other_phase * other_second_phase)

    return {
        "CAR_mode_pair_basis_tests_per_anticommutator": 9 * 9 * DIMENSION,
        "CAR_identities": ["{c†_i,c†_j}=0", "{c_i,c_j}=0", "{c†_i,c_j}=δ_ij"],
        "all_local_observables_real_Hermitian_involutions_and_even": True,
        "all_observables_on_distinct_readers_commute": True,
    }


def check_local_restrictions(modes):
    overlaps = {}
    for x, y, z in modes:
        for order, record, flip in product(("yz", "zy"), "yz", "12"):
            zero = birth({0: 1}, (x, y, z), order)
            one = birth(create({0: 1}, x), (x, y, z), order)
            action = pair_flip(x, y if record == "y" else z, flip)
            observed = apply(action, zero)
            overlap = Fraction(sum(c * one.get(mask, 0) for mask, c in observed.items()), 2)
            expected = (-1 if flip == "1" else 1) if (record == order[0]) == (flip == "1") else 0
            assert overlap == expected
            overlaps[f"{order}/{record}/F{flip}"] = expected
    return overlaps


def fraction_average(tables):
    columns = zip(*(tuple(Fraction(n, d) for n in ns) for d, ns in tables), strict=True)
    return tuple(sum(column) / len(tables) for column in columns)


def average_correlations(tables):
    return tuple(
        sum(column) / len(tables) for column in zip(*(correlations(p) for p in tables), strict=True)
    )


def cases(modes, target, orders, pair_orders, records, flips):
    tables = {}
    data = {}
    projector_checks = 0
    exact_count = 0
    full_count = 0
    for parents in orders:
        start = initial_state(modes, parents)
        for commits in orders:
            table_ids = []
            for pair_order in pair_orders:
                state = grow(start, modes, commits, pair_order)
                assert len(state) == 32 and all(abs(c) == 1 for c in state.values())
                assert all(not mask.bit_count() % 2 for mask in state)
                for record, flip in product(records, flips):
                    observables = readers(modes, record, flip)
                    computed = table(state, observables)
                    if len(set(pair_order)) == len(set(record)) == 1:
                        assert computed == projector_table(state, observables)
                        projector_checks += 1
                    measured = correlations(computed)
                    prediction = predicted_correlations(parents, commits, pair_order, record, flip)
                    assert measured == prediction, (parents, commits, pair_order, record, flip, measured, prediction)
                    assert (computed == target) == (prediction == (1, -1, -1, -1))
                    exact_count += computed == target
                    full_count += is_full(measured)
                    table_ids.append(tables.setdefault(computed, len(tables)))
            data[f"{label(parents)}/{label(commits)}"] = table_ids

    return list(tables), data, {
        "cells": len(data) * len(pair_orders) * len(records) * len(flips),
        "full_contradictions": full_count,
        "fixed_label_exact_tables": exact_count,
        "independent_projector_table_matches": projector_checks,
    }


def global_variations(tables, data, target):
    variations = []
    for pair_order, record, flip in product(("yz", "zy"), "yz", FLIPS):
        index = (PAIR_ORDERS.index((pair_order,) * 3) * len(RECORDS) + RECORDS.index((record,) * 3)) * len(FLIPS)
        index += FLIPS.index(flip)
        by_parent = {}
        for parents in ORDERS:
            parent = label(parents)
            chosen = {label(order): tables[data[f"{parent}/{label(order)}"][index]] for order in ORDERS}
            by_parent[parent] = {
                "full": [order for order, entry in chosen.items() if is_full(correlations(entry))],
                "exact": [order for order, entry in chosen.items() if entry == target],
            }
        variations.append({"pair_order": pair_order, "record": record, "flips": "".join(flip), "by_parent_order": by_parent})
    return variations


def check_probability_controls(tables, data):
    # The other two readers' marginal is independent of the third setting.
    for _, outcomes in tables:
        for reader_bit in (4, 2, 1):
            for setting in range(8):
                if setting & reader_bit:
                    continue
                other_setting = setting | reader_bit
                for outcome in range(8):
                    if outcome & reader_bit:
                        continue
                    other_outcome = outcome | reader_bit
                    assert (
                        outcomes[8 * setting + outcome] + outcomes[8 * setting + other_outcome]
                        == outcomes[8 * other_setting + outcome] + outcomes[8 * other_setting + other_outcome]
                    )

    # Swap y,z together in the pair product and the read, reader by reader.
    label_swaps = 0
    for row in data.values():
        for pair_index, pair_order in enumerate(PAIR_ORDERS):
            for record_index, record in enumerate(RECORDS):
                swapped_record = tuple(
                    current if order == "yz" else ("z" if current == "y" else "y")
                    for order, current in zip(pair_order, record, strict=True)
                )
                first = (pair_index * len(RECORDS) + record_index) * len(FLIPS)
                second = RECORDS.index(swapped_record) * len(FLIPS)
                assert row[first : first + len(FLIPS)] == row[second : second + len(FLIPS)]
                label_swaps += len(FLIPS)
    return {
        "distinct_probability_tables_checked_for_no_signalling": len(tables),
        "fresh_mode_label_swap_table_matches": label_swaps,
    }


def fixed_initial_sign_patterns(modes, baseline_readers, target, re_prepared):
    order_by_signature = {
        row["physical_initial_coefficients_in_abc_basis"]: chronology
        for chronology, row in re_prepared.items()
    }
    variants = {}
    for tail in product("+-", repeat=3):
        signature = "+" + "".join(tail)
        source = {
            sum(occupied << modes[reader][0] for reader, occupied in enumerate(word)):
                (1 if coefficient == "+" else -1)
            for word, coefficient in zip(EVEN_WORDS, signature, strict=True)
        }
        carrying = []
        exact = []
        for commits in ORDERS:
            grown = grow(source, modes, commits, ("yz",) * 3)
            measured = table(grown, baseline_readers)
            if is_full(correlations(measured)):
                carrying.append(label(commits))
            if measured == target:
                exact.append(label(commits))
        prepared_by = order_by_signature.get(signature)
        assert len(carrying) == 3
        assert exact == ([prepared_by] if prepared_by is not None else [])
        variants[signature] = {"sequential_parent_preparation": prepared_by, "full": carrying, "exact": exact}
    return variants


def controls(modes, target, tables, data):
    baseline_readers = readers(modes, ("y",) * 3, ("1",) * 3)
    basis_orders = [basis(order) for order in ORDERS]
    basis_orders.append(basis(ORDERS[-1], within=(2, 1, 0)))
    basis_replays = 0
    out = {}
    for parents in ORDERS:
        parent_label = label(parents)
        source = initial_state(modes, parents)
        word_coefficients = {old_word(mask, modes): c for mask, c in source.items()}
        source_signature = "".join("+" if word_coefficients[word] == 1 else "-" for word in EVEN_WORDS)
        replay = []
        column = {}
        for commits in ORDERS:
            commit_label = label(commits)
            grown = grow(source, modes, commits, ("yz",) * 3)
            replay.append(grown)
            column[commit_label] = data[f"{parent_label}/{commit_label}"][0]
            for new_basis in basis_orders:
                new_start = transport(source, modes, new_basis)
                assert new_start == initial_state(new_basis, parents)
                new_state = grow(new_start, new_basis, commits, ("yz",) * 3)
                assert new_state == transport(grown, modes, new_basis)
                for f in ("1", "2"):
                    actual = table(new_state, readers(new_basis, ("y",) * 3, (f,) * 3))
                    assert actual == tables[data[f"{parent_label}/{commit_label}"][FLIPS.index((f,) * 3)]]
                    basis_replays += 1

        all_probabilities = [tables[index] for index in column.values()]
        full_probabilities = [p for p in all_probabilities if is_full(correlations(p))]
        coherent = signed_sum(*replay)
        assert {old_word(mask, modes) for mask in coherent} == {(0, 0, 0)}
        assert len(coherent) == 8
        assert all(abs(coefficient) == 6 for coefficient in coherent.values())
        out[parent_label] = {
            "physical_initial_coefficients_in_abc_basis": source_signature,
            "probability_table_ids_by_commit": column,
            "full": [order for order, index in column.items() if is_full(correlations(tables[index]))],
            "exact": [order for order, index in column.items() if tables[index] == target],
            "mermin_max_equal_mixture_all_orders": str(mermin_max(average_correlations(all_probabilities))),
            "mermin_max_equal_mixture_relative_even_orders": str(mermin_max(average_correlations(full_probabilities))),
            "coherent_sum_surviving_old_words": ["000"],
            "coherent_sum_surviving_nine_mode_basis_states": len(coherent),
        }
        assert out[parent_label]["mermin_max_equal_mixture_all_orders"] == "7/6"
        assert out[parent_label]["mermin_max_equal_mixture_relative_even_orders"] == "4/3"

    base_grown = grow(initial_state(modes, ORDERS[0]), modes, ORDERS[0], ("yz",) * 3)
    sign_erased = table({mask: abs(c) for mask, c in base_grown.items()}, baseline_readers)
    phase_erased = fraction_average([
        table({mask: c for mask, c in base_grown.items() if old_word(mask, modes) == word}, baseline_readers)
        for word in EVEN_WORDS
    ])
    expected_fractions = tuple(Fraction(n, target[0]) for n in target[1])
    return {
        "physical_preparation_order_varied": out,
        "fixed_initial_states": {
            "explanation": "Keeping either of these physical states fixed while changing the coordinate listing leaves its whole row of commit tables fixed.",
            "signed_abc_initial_coefficients": out["abc"],
            "positive_abc_initial_coefficients": out["cba"],
            "matching_basis_transport_tables": basis_replays,
            "tested_coordinate_listings": [label(order) + "/xyz" for order in ORDERS] + ["cba/zyx"],
        },
        "fixed_initial_sign_patterns_with_yz_y_F1": fixed_initial_sign_patterns(modes, baseline_readers, target, out),
        "erased_grown_amplitude_signs": {
            "win": str(win(correlations(sign_erased))),
            "target_matches": sum(a == Fraction(n, sign_erased[0]) for a, n in zip(expected_fractions, sign_erased[1], strict=True)),
        },
        "dephased_initial_words": {
            "win": str(sum(probability for index, probability in enumerate(phase_erased)
                           if index // 8 in SCORED_SETTINGS and expected_fractions[index]) / 4),
            "target_matches": sum(a == b for a, b in zip(expected_fractions, phase_erased, strict=True)),
        },
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--smoke", action="store_true", help="time a two-order, two-flip subset without writing a receipt")
    parser.add_argument("--output", type=Path, help="write the full JSON receipt here")
    args = parser.parse_args()
    modes = basis(ORDERS[0])
    target = ghz_target()
    if args.smoke:
        orders = (ORDERS[0], ORDERS[-1])
        tables, data, counts = cases(modes, target, orders, (("yz",) * 3,), (("y",) * 3,), (FLIPS[0], FLIPS[-1]))
        assert tables[data["abc/abc"][0]] == target
        assert tables[data["cba/cba"][0]] == target
        print(json.dumps(counts))
        return

    algebra = check_operators(modes)
    overlaps = check_local_restrictions(modes)
    tables, data, counts = cases(modes, target, ORDERS, PAIR_ORDERS, RECORDS, FLIPS)
    assert counts == {
        "cells": 18432,
        "full_contradictions": 1152,
        "fixed_label_exact_tables": 288,
        "independent_projector_table_matches": 1152,
    }
    receipts = {
        "description": "Exact nine-mode exterior-basis replay. A case is one choice of parent chronology, commit chronology, pair creator order, record and flip. Numerators are listed by settings then outcomes, both 000 to 111. For each case, setting 0 is Z, setting 1 is F, and outcome 0 is +1.",
        "case_counts": counts,
        "controls": {**algebra, **controls(modes, target, tables, data), **check_probability_controls(tables, data)},
        "local_F_overlap_with_X": overlaps,
        "scored_correlations_order": ["ZZZ", "FFZ", "FZF", "ZFF"],
        "initial_word_order": ["".join(map(str, word)) for word in EVEN_WORDS],
        "target_table_id": tables.index(target),
        "probability_tables": {
            str(i): {"denominator": den, "numerators": [nums[j : j + 8] for j in range(0, 64, 8)]}
            for i, (den, nums) in enumerate(tables)
        },
        "global_pair_and_record_variations": global_variations(tables, data, target),
        "full_local_case_index": {
            "description": "Each parent/commit key has a flattened 8×8×8 list of 64-cell table IDs. Pair, record and flip are in the listed axis orders, with flips the fastest varying axis.",
            "pair_order_axis": PAIR_ORDERS,
            "record_axis": ["".join(records) for records in RECORDS],
            "flip_axis": ["".join(flips) for flips in FLIPS],
            "table_ids": data,
        },
    }
    if args.output is not None:
        # Keep each probability table, summary row, and lookup row on one line.
        pretty_sections = [
            f"  {json.dumps(key)}: {json.dumps(value, separators=(',', ': '))}"
            for key, value in receipts.items()
            if key not in ("probability_tables", "global_pair_and_record_variations", "full_local_case_index")
        ]
        table_rows = ",\n".join(
            f"    {json.dumps(table_id)}: {json.dumps(entry)}"
            for table_id, entry in receipts["probability_tables"].items()
        )
        pretty_sections.append('  "probability_tables": {\n' + table_rows + "\n  }")
        global_rows = ",\n".join(
            "    " + json.dumps(row) for row in receipts["global_pair_and_record_variations"]
        )
        pretty_sections.append('  "global_pair_and_record_variations": [\n' + global_rows + "\n  ]")
        index = receipts["full_local_case_index"]
        rows = ",\n".join(f"      {json.dumps(row)}: {json.dumps(ids)}" for row, ids in data.items())
        index_sections = [
            f"    {json.dumps(key)}: {json.dumps(value)}"
            for key, value in index.items()
            if key != "table_ids"
        ]
        index_sections.append('    "table_ids": {\n' + rows + "\n    }")
        pretty_sections.append('  "full_local_case_index": {\n' + ",\n".join(index_sections) + "\n  }")
        args.output.write_text("{\n" + ",\n".join(pretty_sections) + "\n}\n", encoding="utf-8")
    print(json.dumps(counts))


if __name__ == "__main__":
    main()
