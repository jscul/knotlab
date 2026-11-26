"""Rebuild the start-sign and reader-convention tests using occupation states.

Each reader's local listing is (x, y, z). The full vector is grown by left
creation. Its coefficients are then checked on every fresh-pair completion
before reducing the vector to the old distinctions.
"""

import argparse
import json
from functools import cache
from itertools import combinations, permutations, product
from pathlib import Path
from random import Random


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
ARCHIVED_RECEIPT = (
    ROOT
    / "artifacts/REORDER-CONFIRM-20261126-001"
    / "REORDER-CONFIRM-20261126-001-E001_schedules/results.json"
)
SAMPLE_SEED = 20261131
LOCAL_ASSIGNMENTS = tuple(product(("yz", "zy"), ("y", "z"), ("F1", "F2")))


def word_label(word, n):
    return "".join(str(word >> j & 1) for j in range(n))


def order_label(order):
    return "".join("abcdef"[j] for j in order)


@cache
def even_words(n):
    return tuple(sorted(
        (word for word in range(1 << n) if word.bit_count() % 2 == 0),
        key=lambda word: word_label(word, n),
    ))


def sign_string(signs):
    return "".join("+" if sign == 1 else "-" for sign in signs)


def sign_from_count(count):
    return 1 - 2 * (count % 2)


def add_creator(occupation, mode):
    bit = 1 << mode
    assert not occupation & bit
    return occupation | bit, sign_from_count((occupation & (bit - 1)).bit_count())


def parent_state(n, *, order=None, signs=None):
    if order is None:
        assert signs is not None
        return {
            sum(1 << (3 * j) for j in range(n) if word >> j & 1): sign
            for word, sign in zip(even_words(n), signs, strict=True)
        }
    state = {}
    for word in even_words(n):
        occupation, phase = 0, 1
        for j in order:
            if word >> j & 1:
                occupation, multiplier = add_creator(occupation, 3 * j)
                phase *= multiplier
        state[occupation] = phase
    return state


def grow(state, order, pair_products):
    for j in order:
        x, y, z = (3 * j + k for k in range(3))
        left, right = (y, z) if pair_products[j] == "yz" else (z, y)
        grown = {}
        for occupation, coefficient in state.items():
            if occupation >> x & 1:
                for mode in (y, z):
                    final, sign = add_creator(occupation, mode)
                    grown[final] = coefficient * sign
            else:
                grown[occupation] = coefficient
                intermediate, right_sign = add_creator(occupation, right)
                final, left_sign = add_creator(intermediate, left)
                grown[final] = coefficient * right_sign * left_sign
        assert len(grown) == 2 * len(state)
        state = grown
    return state


@cache
def local_completions(pair_product, old):
    if old:
        return {0b011: 1, 0b101: 1}
    return {0: 1, 0b110: 1 if pair_product == "yz" else -1}


def reduce_state(state, pair_products):
    n = len(pair_products)
    assert len(state) == 1 << (2 * n - 1)
    reduced = {}
    completions = {}
    for occupation, coefficient in state.items():
        old = 0
        for j, pair_product in enumerate(pair_products):
            chunk = occupation >> (3 * j) & 7
            old_bit = chunk & 1
            old |= old_bit << j
            coefficient *= local_completions(pair_product, old_bit)[chunk]
        assert coefficient == reduced.setdefault(old, coefficient)
        completions[old] = completions.get(old, 0) + 1
    assert set(completions) == set(even_words(n))
    assert set(completions.values()) == {1 << n}
    return tuple(reduced[word] for word in even_words(n))


def majorana(occupation, mode, primed):
    bit = 1 << mode
    exponent = 2 * (occupation & (bit - 1)).bit_count()
    if primed:
        exponent += 3 if occupation & bit else 1
    return occupation ^ bit, exponent


@cache
def project_flip(pair_product, record, kind):
    """Columns of the projected flip, in powers of i, or None for zero."""
    fresh = {"y": 1, "z": 2}[record]
    prefactor = {"F1": 3, "F2": 1, "F3": 1}[kind]
    actions = []
    for old in (0, 1):
        source = local_completions(pair_product, old)
        target = local_completions(pair_product, old ^ 1)
        phases = []
        for occupation, coefficient in source.items():
            intermediate, fresh_phase = majorana(occupation, fresh, kind == "F2")
            final, old_phase = majorana(intermediate, 0, kind == "F1")
            sign = coefficient * target[final]
            phases.append((prefactor + fresh_phase + old_phase + (2 if sign < 0 else 0)) % 4)
        assert phases[0] == phases[1] or (phases[0] - phases[1]) % 4 == 2
        actions.append(phases[0] if phases[0] == phases[1] else None)
    assert (actions[0] is None) == (actions[1] is None)
    return None if actions[0] is None else tuple(actions)


@cache
def phase_columns(n, flips, flip_mask):
    modes = tuple(j for j in range(n) if flip_mask >> j & 1)
    if any(flips[j] is None for j in modes):
        return None
    return tuple(sum(flips[j][word >> j & 1] for j in modes) for word in even_words(n))


@cache
def word_positions(n):
    return {word: j for j, word in enumerate(even_words(n))}


def moment(n, signs, flips, flip_mask, parity_mask):
    """Return a product expectation multiplied by the number of even words."""
    if flip_mask.bit_count() % 2:
        return 0
    phases = phase_columns(n, flips, flip_mask)
    if phases is None:
        return 0
    real, imag = 0, 0
    positions = word_positions(n)
    for word, sign, phase in zip(even_words(n), signs, phases, strict=True):
        multiplier = sign * signs[positions[word ^ flip_mask]]
        multiplier *= sign_from_count((word & parity_mask).bit_count())
        exponent = phase % 4
        if exponent % 2:
            imag += multiplier if exponent == 1 else -multiplier
        else:
            real += multiplier if exponent == 0 else -multiplier
    assert imag == 0
    return real


@cache
def masks_for_moments(n):
    return tuple(
        (flip_mask, parity_mask)
        for flip_mask in range(1 << n)
        for parity_mask in range(1 << n)
        if not flip_mask & parity_mask
    )


@cache
def full_table(n, signs, flips):
    # These are exact Walsh coefficients, with a shared denominator. For any
    # setting, Fourier inversion uniquely recovers all its outcome cells.
    return tuple(moment(n, signs, flips, f, z) for f, z in masks_for_moments(n))


@cache
def reversal(n):
    return tuple(sign_from_count(word.bit_count() // 2) for word in even_words(n))


@cache
def target(n):
    return full_table(n, reversal(n), ((0, 0),) * n)


def check_ternary_target():
    moments = dict(zip(masks_for_moments(3), target(3), strict=True))
    for setting in range(8):
        for outcome in range(8):
            numerator = sum(
                sign_from_count((mask & outcome).bit_count())
                * moments[(mask & setting, mask & (7 ^ setting))]
                for mask in range(8)
            )
            if setting.bit_count() % 2:
                expected = 4
            else:
                expected = 8 if outcome.bit_count() % 2 == bool(setting) else 0
            assert numerator == expected  # Common denominator 32.


@cache
def test_reading(n, signs, flips):
    all_readers = (1 << n) - 1
    correlations = {
        t: moment(n, signs, flips, t, all_readers ^ t)
        for t in even_words(n)
    }
    norm = len(correlations)
    sharp = all(abs(value) == norm for value in correlations.values())
    carries = sharp and any(
        correlations[a] * correlations[b] != norm * correlations[a ^ b]
        for a, b in combinations(correlations, 2)
    )
    # The target itself carries, so a failing case cannot match its table.
    exact = carries and full_table(n, signs, flips) == target(n)
    return carries, exact, correlations


@cache
def characters(n):
    # Complementary masks agree on the even words. Fix the final mask bit.
    return tuple(
        tuple(sign_from_count((word & mask).bit_count()) for word in even_words(n))
        for mask in range(1 << (n - 1))
    )


def inversion_sign(order, word):
    return sign_from_count(sum(
        j > k and (word >> j & 1) and (word >> k & 1)
        for j, k in combinations(order, 2)
    ))


def shifts(order):
    return tuple(order[k:] + order[:k] for k in range(len(order)))


def p5(n, pilot):
    words = even_words(n)
    orders = tuple(permutations(range(n)))
    patterns = tuple((1,) + seq for seq in product((1, -1), repeat=len(words) - 1))
    if pilot:
        orders = orders[:3]
        patterns = patterns[:8]
    pair_products = ("yz",) * n
    flips = (project_flip("yz", "y", "F1"),) * n
    predicted_exact = {
        order: tuple(sign * inversion_sign(order, word)
                     for word, sign in zip(words, reversal(n), strict=True))
        for order in orders
    }
    predicted_carrying = {
        order: {
            tuple(s * character_sign for s, character_sign in zip(signs, character, strict=True))
            for character in characters(n)
        }
        for order, signs in predicted_exact.items()
    }
    signatures = {}
    for signs in patterns:
        state = parent_state(n, signs=signs)
        observed_carrying, observed_exact = [], []
        for order in orders:
            reduced = reduce_state(grow(state, order, pair_products), pair_products)
            carries, exact, _ = test_reading(n, reduced, flips)
            if carries:
                observed_carrying.append(order_label(order))
            if exact:
                observed_exact.append(order_label(order))
            if n == 3:
                parity_rule = signs[1] * signs[2] * signs[3] * inversion_sign(order, 0b111) == -1
                assert carries == parity_rule
        expected_carrying = [order_label(order) for order in orders if signs in predicted_carrying[order]]
        expected_exact = [order_label(order) for order in orders if signs == predicted_exact[order]]
        assert observed_carrying == expected_carrying
        assert observed_exact == expected_exact
        if observed_carrying and not pilot:
            assert set(observed_carrying) == set(shifts(observed_carrying[0]))
        signatures[sign_string(signs)] = {
            "predicted_carrying_orders": expected_carrying,
            "observed_carrying_orders": observed_carrying,
            "predicted_exact_orders": expected_exact,
            "observed_exact_orders": observed_exact,
        }
    report = {
        "even_words": [word_label(word, n) for word in words],
        "patterns": len(patterns),
        "orders_per_pattern": len(orders),
        "patterns_with_carrying_order": sum(bool(s["observed_carrying_orders"]) for s in signatures.values()),
        "pattern_order_cases_carrying": sum(len(s["observed_carrying_orders"]) for s in signatures.values()),
        "patterns_with_exact_order": sum(bool(s["observed_exact_orders"]) for s in signatures.values()),
        "pattern_order_cases_exact": sum(len(s["observed_exact_orders"]) for s in signatures.values()),
        "sets_by_sign_pattern": signatures,
    }
    if n == 3 and not pilot:
        assert "abc" in signatures["+---"]["observed_exact_orders"]
        report["anchor"] = {"sign_pattern": "+---", "order": "abc", "carrying": True, "exact_cells": 4 ** n}
    return report


def is_matched(spec):
    pair_product, record, kind = spec
    return (record == pair_product[0]) == (kind == "F1")


def config_summary(n, assignment_ids, designs, sigmas, orders, reduced_states, pilot):
    by_sigma = {}
    for sigma in sigmas:
        carried = exact = matched_assignments = unmatched_assignments = 0
        correlations_touching_unmatched = 0
        by_f2 = {}
        for design_id in assignment_ids:
            design = designs[design_id]
            pair_products, _, reader_types = zip(*design, strict=True)
            flips = tuple(project_flip(*spec) for spec in design)
            matched = all(is_matched(spec) for spec in design)
            assert matched == (None not in flips)
            matched_assignments += matched
            unmatched_assignments += not matched
            f2 = frozenset(j for j, kind in enumerate(reader_types) if kind == "F2")
            complement = frozenset(sigma) - f2
            unmatched_mask = sum(1 << j for j, flip in enumerate(flips) if flip is None)
            carry_set, exact_set = [], []
            for order in orders:
                signs = reduced_states[(sigma, order, pair_products)]
                carries, matches, correlations = test_reading(n, signs, flips)
                if carries:
                    carry_set.append(order)
                if matches:
                    exact_set.append(order)
                for t, value in correlations.items():
                    if t & unmatched_mask:
                        assert value == 0
                        correlations_touching_unmatched += 1
            shift_orders = shifts(sigma)
            expected_carry = [order for order in orders if matched and order in shift_orders]
            expected_exact = [
                order for k, order in enumerate(shift_orders)
                if matched and order in orders and frozenset(sigma[:k]) in (f2, complement)
            ]
            assert carry_set == expected_carry
            assert exact_set == expected_exact
            carried += len(carry_set)
            exact += len(exact_set)
            if matched:
                assert len(exact_set) <= 1
                label = "".join("abcdef"[j] for j in sorted(f2))
                observed = by_f2.setdefault(label, {
                    "assignments": 0,
                    "carrying_orders": sorted(map(order_label, carry_set)),
                    "exact_orders": sorted(map(order_label, exact_set)),
                })
                assert observed["carrying_orders"] == sorted(map(order_label, carry_set))
                assert observed["exact_orders"] == sorted(map(order_label, exact_set))
                observed["assignments"] += 1
        by_sigma[order_label(sigma)] = {
            "matched_assignments": matched_assignments,
            "unmatched_assignments": unmatched_assignments,
            "assignment_order_cases": len(assignment_ids) * len(orders),
            "cases_carrying": carried,
            "cases_exact": exact,
            "matched_assignments_with_exact_order": exact,
            "zero_full_correlations_toggling_any_unmatched_reader": correlations_touching_unmatched,
            "by_matched_F2_set": by_f2,
        }
        if not pilot and len(assignment_ids) == 8 ** n:
            assert carried == (4 ** n) * n
            assert exact == 2 * n * (2 ** n)
    return by_sigma


def p8(n, pilot):
    sigmas = (tuple(range(n)),)
    if n == 3:
        sigmas += (tuple(reversed(range(n))),)
    orders = tuple(permutations(range(n)))
    if pilot:
        orders = orders[:3]
    else:
        assert len(orders) in (6, 24)
    designs = tuple(product(LOCAL_ASSIGNMENTS, repeat=n))
    matched = tuple(i for i, design in enumerate(designs) if all(map(is_matched, design)))
    matched_ids = set(matched)
    unmatched = tuple(i for i in range(len(designs)) if i not in matched_ids)
    sampled = tuple(Random(SAMPLE_SEED).sample(unmatched, 256)) if n == 4 else unmatched
    if pilot:
        matched, unmatched, sampled = matched[:16], unmatched[:32], sampled[:32]
    reduced_states = {}
    for sigma in sigmas:
        state = parent_state(n, order=sigma)
        for order in orders:
            reference = reduce_state(grow(state, order, ("yz",) * n), ("yz",) * n)
            for pair_products in product(("yz", "zy"), repeat=n):
                reduced = reduce_state(grow(state, order, pair_products), pair_products)
                assert reduced == reference
                reduced_states[(sigma, order, pair_products)] = reduced
    result = {
        "all_assignments": config_summary(
            n, matched + unmatched, designs, sigmas, orders, reduced_states, pilot,
        ),
        "grown_vectors_checked_by_sigma_order_pair_product": len(reduced_states),
    }
    if n == 4:
        result["archived_sample"] = {
            "seed": SAMPLE_SEED,
            "provenance": "Reconstructed from the archived source's enumeration order and seed. The archived receipt gives aggregate counts.",
            "sampled_unmatched_design_ids": sampled,
            "by_sigma": config_summary(
                n, matched + sampled, designs, sigmas, orders, reduced_states, pilot,
            ),
        }
    return result


def f3_round(n, pilot):
    sigmas = (tuple(range(n)),)
    if n == 3:
        sigmas += (sigmas[0][::-1],)
    orders = tuple(permutations(range(n)))
    if pilot:
        orders = orders[:6]
    pair_products = ("yz",) * n
    flips = (project_flip("yz", "y", "F3"),) * n
    report = {}
    for sigma in sigmas:
        state = parent_state(n, order=sigma)
        carrying, exact = [], []
        for order in orders:
            signs = reduce_state(grow(state, order, pair_products), pair_products)
            carries, matches, _ = test_reading(n, signs, flips)
            if carries:
                carrying.append(order)
            if matches:
                exact.append(order)
        assert set(carrying) == set(shifts(sigma[::-1])) & set(orders)
        assert exact == ([sigma[::-1]] if sigma[::-1] in orders else [])
        report[order_label(sigma)] = {
            "orders_checked": len(orders),
            "carrying": list(map(order_label, carrying)),
            "exact": list(map(order_label, exact)),
        }
    return report


def diagonal_phases():
    # Real pair products u_i u_j force all unit phases u_i into {±1}, or all
    # into {±i}, when n >= 3. Their products on even words are these two sets.
    phase_counts = {}
    for n in (3, 4):
        reversal_character = {
            tuple(a * b for a, b in zip(reversal(n), character, strict=True))
            for character in characters(n)
        }
        factorizable = set(characters(n)) | reversal_character
        state = parent_state(n, order=tuple(range(n)))
        pair_products = ("yz",) * n
        carrying_diag = []
        for order in permutations(range(n)):
            signs = reduce_state(grow(state, order, pair_products), pair_products)
            if signs in factorizable:
                carrying_diag.append(order_label(order))
        phase_counts[f"n{n}"] = {
            "factorizable_sign_patterns_up_to_global_sign": len(factorizable),
            "chronological_ascending_commits_with_factorizable_phase": carrying_diag,
        }
    order = (0, 1, 3, 2)
    state = parent_state(4, order=(0, 1, 2, 3))
    signs = reduce_state(grow(state, order, ("yz",) * 4), ("yz",) * 4)
    signed_words = dict(zip(even_words(4), signs, strict=True))
    a, b, c, d = (1, 2, 4, 8)
    witness = {
        "creation_order": "abcd",
        "commit_order": "abdc",
        "h_ab_times_h_cd": signed_words[a | b] * signed_words[c | d],
        "h_ac_times_h_bd": signed_words[a | c] * signed_words[b | d],
        "h_abcd": signed_words[a | b | c | d],
    }
    assert witness["h_ab_times_h_cd"] != witness["h_ac_times_h_bd"]
    phase_counts["nonfactorizable_witness"] = witness
    return phase_counts


def compare_archive(rebuilt):
    archive = json.loads(ARCHIVED_RECEIPT.read_text())
    for n in (3, 4):
        key = f"n{n}"
        archived = archive["P5"][key]
        independent = rebuilt["P5"][key]
        assert archived["patterns"] == independent["patterns"]
        if n == 3:
            assert archived["anchor"] == {"carries": True, "exact": True}
            assert archived["patterns_with_exact_order"] == independent["patterns_with_exact_order"]
            assert archived["rule_failures"] == 0
        else:
            assert archived["with_carrying_orders"] == independent["patterns_with_carrying_order"]
            assert archived["with_exact_order"] == independent["patterns_with_exact_order"]
            assert archived["formula_with_carrying"] == independent["patterns_with_carrying_order"]
            assert archived["observed_equals_formula"] and archived["each_one_cyclic_class"]
    summaries = {}
    for n in (3, 4):
        key = f"n{n}"
        archived = archive["P8"][key]
        independent = rebuilt["P8"][key]
        registered_runs = (independent["all_assignments"] if n == 3
                           else independent["archived_sample"]["by_sigma"])
        assert set(archived["sigmas"]) == set(registered_runs)
        for row in registered_runs.values():
            assert archived["matched"] == row["matched_assignments"]
            assert archived["assignments_run"] == row["matched_assignments"] + row["unmatched_assignments"]
        assert archived["matched_runs_with_an_exact_order"] == sum(
            row["matched_assignments_with_exact_order"] for row in registered_runs.values()
        )
        assert not any(archived["failures"].values())
        summaries[key] = {
            "assignment_and_match_counts_in_archive_are_per_creation_order": True,
            "exact_matches_in_archive_are_total_across_creation_orders": True,
            "total_assignment_runs": sum(
                row["matched_assignments"] + row["unmatched_assignments"] for row in registered_runs.values()
            ),
            "total_matched_assignment_runs": sum(row["matched_assignments"] for row in registered_runs.values()),
            "total_unmatched_assignment_runs": sum(row["unmatched_assignments"] for row in registered_runs.values()),
        }
    for n in (3, 4, 5, 6):
        key = f"n{n}"
        ascending = order_label(tuple(range(n)))
        assert archive["P8"]["F3_all_readers"][key]["carrying"] == rebuilt["F3"][key][ascending]["carrying"]
    return {
        "P5": "All archived counts agree. The original receipt does not give individual sign patterns and orders.",
        "P8": summaries,
        "P8_F3": "The archived F3 control uses only the ascending creation order. The ternary descending creation order was added here.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pilot", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    check_ternary_target()
    report = {
        "method": {
            "state": "Chronological left creation and exact signed occupation states, checked on every fresh-pair completion.",
            "tables": "Exact Walsh coefficients of the outcome probabilities from the projected Z and F operators.",
            "ternary_benchmark": "Fourier inversion of the target reproduced all 64 cells of the specified four-settings benchmark.",
            "carrying": "All full correlations at even flip settings are sharp and their signs fail the character identity.",
            "exact": "All fixed-label outcome probabilities agree with the reversal-signed state read by Z and X.",
            "P5_prediction": "Use the reversal signs times the inversion signs for each exact order. A carrying order allows any additional character of the even words.",
            "P8_design_id": "Zero-based order in the product of LOCAL_ASSIGNMENTS across readers, with the last reader varying fastest.",
        },
        "local_flip_columns_powers_of_i": {
            " ".join(spec): project_flip(*spec)
            for spec in product(("yz", "zy"), ("y", "z"), ("F1", "F2", "F3"))
        },
        "P5": {f"n{n}": p5(n, args.pilot) for n in (3, 4)},
        "P8": {f"n{n}": p8(n, args.pilot) for n in (3, 4)},
        "F3": {f"n{n}": f3_round(n, args.pilot) for n in (3, 4, 5, 6)},
        "diagonal_phase_scope": diagonal_phases(),
    }
    if args.pilot:
        print("Pilot passed: three commit orders in each real-reader case, six in each complex-reader case.")
        return
    report["archive_comparison"] = compare_archive(report)
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output is None:
        print(rendered, end="")
    else:
        args.output.write_text(rendered, encoding="utf-8")


if __name__ == "__main__":
    main()
