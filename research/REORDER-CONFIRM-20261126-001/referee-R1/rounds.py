"""Exact occupation-space replay of the gate and the round predictions."""

import argparse
import json
from fractions import Fraction
from functools import cache
from itertools import combinations, permutations, product
from math import factorial, prod
from pathlib import Path
from random import Random
from string import ascii_lowercase
from time import perf_counter

import numpy as np
from scipy import sparse


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CONFIRM = ROOT / "artifacts/REORDER-CONFIRM-20261126-001"
CONFIRM = CONFIRM / "REORDER-CONFIRM-20261126-001-E001_schedules/results.json"
PREVIOUS = ROOT / "research/REORDER-SIGN-20261126-001/verify_fock.json"
SEED = 20261126


def name(order):
    return "".join(ascii_lowercase[i] for i in order)


def word_label(word, n):
    return "".join(str((word >> j) & 1) for j in range(n))


class Measurements:
    def __init__(self, n):
        self.n = n
        self.size = 1 << n
        self.labels = np.arange(self.size)
        self.weight = np.array([int(i).bit_count() for i in self.labels])
        self.parity = (-1) ** self.weight
        self.even = self.labels[self.parity == 1]
        self.observables = tuple(product(range(3), repeat=n))
        self.combinations = np.zeros((self.size, self.size), dtype=int)
        self.characters = self.parity[self.labels[:, None] & self.labels]
        self.hadamard_pairs = []
        self.physical = np.zeros((self.size, self.size), dtype=np.int32)
        for j in range(n):
            bit = 1 << j
            bit_value = (self.labels & bit) != 0
            parents = bit_value[:, None]
            spectators = bit_value[None, :]
            local = parents + 2 * (parents ^ spectators) + 4 * spectators
            self.physical |= local.astype(np.int32) << (3 * j)
            selected = self.labels[bit_value]
            unselected = selected ^ bit
            self.hadamard_pairs.append((np.ix_(selected, unselected), np.ix_(selected, selected)))
            letter = 1 + bit_value[:, None]
            self.combinations += 3 ** (n - j - 1) * letter * bit_value

    def direct(self, amplitudes):
        """Square exact overlaps with each joint eigenvector of the X/Z settings."""
        overlaps = np.tile(amplitudes, (self.size, 1))
        for low, high in self.hadamard_pairs:
            left, right = overlaps[low], overlaps[high]
            overlaps[low] = left + right
            overlaps[high] = left - right
        return overlaps ** 2

    def denominator(self, amplitudes):
        return int(amplitudes @ amplitudes) * 2 ** self.weight

    def projector(self, moment_numerators):
        return moment_numerators[self.combinations] @ self.characters

    def target(self):
        weights = self.weight
        amplitudes = (self.parity == 1) * (-1) ** (weights * (weights - 1) // 2)
        numerator, denominator = self.direct(amplitudes), self.denominator(amplitudes)
        if self.n == 3:
            # The predecessor's benchmark specifies all eight probability rows.
            for setting in self.labels:
                for outcome in self.labels:
                    if self.parity[setting] == -1:
                        expected = Fraction(1, 8)
                    else:
                        expected = Fraction(int(self.parity[outcome] == (-1 if setting else 1)), 4)
                    assert Fraction(int(numerator[setting, outcome]), int(denominator[setting])) == expected
        return numerator, denominator


@cache
def measurement(n):
    return Measurements(n)


class Occupations:
    """Mode labels stay fixed while the listing changes the CAR signs."""

    def __init__(self, n, listing=None):
        self.n = n
        self.measure = measurement(n)
        self.modes = 3 * n
        self.dimension = 1 << self.modes
        self.words = np.arange(self.dimension, dtype=np.int32)
        self.sign = np.empty((self.modes, self.dimension), dtype=np.int8)
        self.compact_index = np.full(self.dimension, -1, dtype=np.int32)
        self.compact_index[self.measure.physical.ravel()] = np.arange(4 ** n, dtype=np.int32)
        earlier = np.ones(self.dimension, dtype=np.int8)
        for mode in range(self.modes) if listing is None else listing:
            self.sign[mode] = earlier
            earlier[(self.words & (1 << mode)) != 0] *= -1

    def step(self, mode, words, creator):
        bit = 1 << mode
        occupied = (words & bit) != 0
        return words ^ bit, self.sign[mode, words] * (occupied != creator)

    def create(self, mode, state):
        words, amplitudes = state
        vacant = (words & (1 << mode)) == 0
        source = words[vacant]
        return source | (1 << mode), self.sign[mode, source] * amplitudes[vacant]

    def start(self, sigma, signs=None):
        old = self.measure.even
        words = np.zeros(old.size, dtype=np.int32)
        amplitudes = np.ones(old.size, dtype=np.int64) if signs is None else np.array(signs)
        for j in sigma:
            occupied = (old & (1 << j)) != 0
            amplitudes[occupied] *= self.sign[3 * j, words[occupied]]
            words[occupied] |= 1 << (3 * j)
        return words, amplitudes

    def birth(self, j, state):
        words, amplitudes = state
        x = 3 * j
        occupied = (words & (1 << x)) != 0
        even = words[~occupied], amplitudes[~occupied]
        odd = words[occupied], amplitudes[occupied]
        pair = self.create(x + 1, self.create(x + 2, even))
        branches = (even, pair, self.create(x + 1, odd), self.create(x + 2, odd))
        return tuple(np.concatenate(pieces) for pieces in zip(*branches))

    def grow(self, state, order):
        for j in order:
            state = self.birth(j, state)
        return state

    def compact(self, state):
        words, amplitudes = state
        indices = self.compact_index[words]
        assert np.all(indices >= 0)
        result = np.zeros(4 ** self.n, dtype=np.int64)
        np.add.at(result, indices, amplitudes)
        return result

    def dense(self, state):
        result = np.zeros(self.dimension, dtype=np.int64)
        np.add.at(result, *state)
        return result

    def flip(self, j, words, kind):
        """Apply the Majorana on y first, then the Majorana on x."""
        x, y = 3 * j, 3 * j + 1
        intermediate = words ^ (1 << y)
        sign = self.sign[y, words] * self.sign[x, intermediate]
        primed = x if kind == "F1" else y
        sign = sign * (1 - 2 * ((words >> primed) & 1))
        return intermediate ^ (1 << x), sign if kind == "F1" else -sign

    def readout(self, kind):
        """Precompute exact actions of products of I, Z and the stated flip."""
        physical = self.measure.physical.ravel()
        targets, phases = [], []
        for kinds in self.measure.observables:
            words = physical
            sign = np.ones(physical.size, dtype=np.int8)
            for j, action in enumerate(kinds):
                if action == 1:
                    sign *= 1 - 2 * ((words >> (3 * j)) & 1)
                if action == 2:
                    words, change = self.flip(j, words, kind)
                    sign *= change
            targets.append(self.compact_index[words])
            phases.append(sign)
        targets = np.array(targets)
        assert np.all(targets >= 0)
        return targets, np.array(phases)

    def probabilities(self, state, readout):
        amplitudes = self.compact(state)
        targets, phases = readout
        moment_numerators = np.sum(amplitudes * phases * amplitudes[targets], axis=1)
        norm = int(amplitudes @ amplitudes)
        return self.measure.projector(moment_numerators), norm

    def verify_block_factor(self):
        physical = self.measure.physical
        for j in range(self.n):
            actual, sign = self.flip(j, physical, "F1")
            expected = physical[self.measure.labels ^ (1 << j)]
            assert np.array_equal(actual, expected) and np.all(sign == 1)


class TensorMatrices:
    """Independent sparse tensor construction with integer entries."""

    def __init__(self, n):
        dimension = 1 << (3 * n)
        one = sparse.identity(dimension, dtype=np.int64, format="csr")
        self.vacuum = np.zeros(dimension, dtype=np.int64)
        self.vacuum[0] = 1
        self.measure = measurement(n)
        local_identity = sparse.identity(2, dtype=np.int64, format="csr")
        local_parity = sparse.diags([1, -1], dtype=np.int64, format="csr")
        local_create = sparse.csr_matrix([[0, 0], [1, 0]], dtype=np.int64)
        create = []
        for mode in range(3 * n):
            operator = sparse.identity(1, dtype=np.int64, format="csr")
            for j in reversed(range(3 * n)):
                factor = local_parity if j < mode else local_identity
                if j == mode:
                    factor = local_create
                operator = sparse.kron(operator, factor, format="csr")
            create.append(operator)
        self.parent_creators = create[::3]
        self.births, self.readers = [], []
        for x in range(0, 3 * n, 3):
            y, z = x + 1, x + 2
            number = create[x] @ create[x].T
            self.births.append((one + create[y] @ create[z]) @ (one - number)
                               + (create[y] + create[z]) @ number)
            self.readers.append((one, one - 2 * number,
                                 (create[x] - create[x].T) @ (create[y] + create[y].T)))

    def start(self, sigma, signs=None):
        state = np.zeros_like(self.vacuum)
        for index, word in enumerate(self.measure.even):
            basis = self.vacuum
            for j in sigma:
                if int(word) & (1 << j):
                    basis = self.parent_creators[j] @ basis
            state += basis if signs is None else signs[index] * basis
        return state

    def probabilities(self, base, order):
        state = base
        for j in order:
            state = self.births[j] @ state
        moments = []
        for settings in self.measure.observables:
            measured = state
            for j, action in enumerate(settings):
                if action:
                    measured = self.readers[j][action] @ measured
            moments.append(state @ measured)
        return self.measure.projector(np.array(moments)), int(state @ state)


def ascending_listing(n):
    return tuple(range(0, 3 * n, 3)) + tuple(i for i in range(3 * n) if i % 3 != 0)


def archived_listing(order, n):
    labels = ascending_listing(n)
    return tuple(labels[i] for i in order)


def creation_orders(n, random):
    ascending = tuple(range(n))
    return {"ascending": ascending, "descending": ascending[::-1],
            "random": tuple(random.sample(range(n), n))}


def orders(n, smoke):
    result = list(permutations(range(n)))
    return result[:2] if smoke else result


def correlation_numerators(table, measure):
    return table @ measure.parity


def contradiction(numerators, denominators, measure):
    even = measure.even
    denominators = np.broadcast_to(denominators, numerators.shape)
    if np.any(np.abs(numerators[even]) != denominators[even]):
        return False
    values = np.zeros(measure.size, dtype=np.int64)
    values[even] = numerators[even] // denominators[even]
    values *= values[0]
    return bool(np.any(values[even[:, None] ^ even] != values[even, None] * values[even]))


def check_close(value, archived):
    assert abs(value - Fraction(str(archived))) < Fraction(1, 10**9), (value, archived)


def gate_replay():
    archived = json.loads(PREVIOUS.read_text())
    occupation = Occupations(3, ascending_listing(3))
    measure = occupation.measure
    results = {}
    for sigma in ((0, 1, 2), (2, 1, 0)):
        base = occupation.start(sigma)
        state_by_order = {pi: occupation.grow(base, pi) for pi in orders(3, False)}
        combined = sum(occupation.compact(state) for state in state_by_order.values())
        occupied_words = np.flatnonzero(np.any(combined.reshape(8, 8), axis=1))
        coherent_words = [word_label(int(word), 3) for word in occupied_words]
        coherent_norm = Fraction(int(combined @ combined), 36 * 32)
        for kind in ("F1", "F2"):
            label = "parents_created_" + "_".join(name(sigma)) + "/" + kind
            receipt = archived[label]
            assert set(receipt) == {"orders", "order_blind_best_mermin_score", "coherent_sum_old_words_present",
                                    "coherent_sum_norm_squared_over_36"}
            readout = occupation.readout(kind)
            average = np.zeros(4, dtype=np.int64)
            order_rows = {}
            for pi, state in state_by_order.items():
                table, norm = occupation.probabilities(state, readout)
                numerators = correlation_numerators(table, measure)
                denominator = 8 * norm
                row = receipt["orders"][name(pi)]
                assert set(row) == {"ZZZ_XXZ_XZX_ZXX", "full_contradiction", "product_P",
                                    "order_parity_relative_to_parents_creation", "scored_win_fixed_labels"}
                scored = numerators[measure.even]
                correlations = [Fraction(int(v), denominator) for v in scored]
                for value, previous in zip(correlations, row["ZZZ_XXZ_XZX_ZXX"], strict=True):
                    check_close(value, previous)
                check_close(prod(correlations), row["product_P"])
                relative_order = [sigma.index(j) for j in pi]
                relative_parity = sum(i > j for i, j in combinations(relative_order, 2)) % 2
                assert row["order_parity_relative_to_parents_creation"] == relative_parity
                assert row["full_contradiction"] == contradiction(numerators, denominator, measure)
                win = Fraction(1, 2) + (correlations[0] - sum(correlations[1:])) / 8
                check_close(win, row["scored_win_fixed_labels"])
                average += scored
                order_rows[name(pi)] = [str(value) for value in correlations]
            best = max(abs(Fraction(int(average[0] - average[1:] @ measure.characters[u, measure.even[1:]]),
                                    6 * denominator)) for u in measure.labels)
            check_close(best, receipt["order_blind_best_mermin_score"])
            check_close(coherent_norm, receipt["coherent_sum_norm_squared_over_36"])
            assert coherent_words == receipt["coherent_sum_old_words_present"]
            assert set(order_rows) == set(receipt["orders"])
            results[label] = {"order_correlations": order_rows, "order_blind_best_score": str(best),
                              "coherent_sum_old_words": coherent_words, "normalized_coherent_sum_norm_squared": str(coherent_norm),
                              "nonzero_coherent_coefficients": int(np.count_nonzero(combined))}
    assert set(results) == set(archived)
    return {"order_rows": 24, "summary_rows": 4, "coherent_norm_fields_checked": 4,
            "relative_order_parity_fields_checked": 24, "case_groups": results}


def gate_car(smoke):
    pair_checks = 0
    for listing in (ascending_listing(3), archived_listing(Random(SEED).sample(range(9), 9), 3)):
        occupation = Occupations(3, listing)
        words = occupation.words[:16] if smoke else occupation.words
        for i, j in product(range(9), repeat=2):
            for first, second in ((True, True), (False, False), (True, False)):
                source_a, amplitude_a = occupation.step(j, words, first)
                target_a, sign_a = occupation.step(i, source_a, second)
                source_b, amplitude_b = occupation.step(i, words, second)
                target_b, sign_b = occupation.step(j, source_b, first)
                assert np.array_equal(target_a, target_b)
                actual = amplitude_a * sign_a + amplitude_b * sign_b
                assert np.all(actual == int(i == j and first != second))
                pair_checks += words.size
    return {"listings": 2, "basis_states_per_listing": words.size,
            "individual_relation_checks": pair_checks, "failures": 0}


def gate_second_path(smoke):
    gate_random, p2_random = Random(SEED + 1), Random(SEED + 3)
    result = {}
    for n in (3, 4):
        original = creation_orders(n, gate_random)
        p2 = creation_orders(n, p2_random)
        assert original == p2, (original, p2)
        occupation = Occupations(n)
        matrices = TensorMatrices(n)
        readout = occupation.readout("F1")
        occupation.verify_block_factor()
        inputs = [(sigma, None) for sigma in original.values()]
        if n == 3:
            inputs.extend(((2, 1, 0), (1, *signs)) for signs in product((-1, 1), repeat=3))
        counts = 0
        initial_vectors = set()
        for sigma, signs in inputs:
            matrix_base = matrices.start(sigma, signs)
            initial_vectors.add(matrix_base.tobytes())
            base = occupation.start(sigma, signs)
            for order in orders(n, smoke):
                left, left_norm = matrices.probabilities(matrix_base, order)
                grown = occupation.grow(base, order)
                right, right_norm = occupation.probabilities(grown, readout)
                assert np.array_equal(left * right_norm, right * left_norm)
                effective = effective_amplitudes(occupation, grown)
                direct = occupation.measure.direct(effective)
                direct_denominator = occupation.measure.denominator(effective)
                assert np.array_equal(right * direct_denominator[:, None], direct * right_norm * (1 << n))
                counts += 1
        configs = len(set(inputs)) * len(orders(n, smoke))
        result[f"n{n}"] = {"table_runs": counts, "distinct_input_configurations": configs,
                            "distinct_state_and_order_inputs": len(initial_vectors) * len(orders(n, smoke)),
                            "probability_cells": counts * 4 ** n, "random_order": name(original["random"])}
    return result


def gate_listings(smoke):
    random = Random(SEED + 2)
    result = {}
    for n in (3, 4):
        asc = ascending_listing(n)
        block = tuple(range(3 * n))
        listings = [asc, block, asc[::-1]]
        listings.extend(archived_listing(random.sample(range(3 * n), 3 * n), n) for _ in range(20))
        if smoke:
            listings = listings[:4]
        ascending = tuple(range(n))
        cases = ((ascending, ascending[::-1]), ("F1", "F2")) if n == 3 else ((ascending,), ("F1",))
        reference = {}
        differing_order_tables = 0
        for listing_index, listing in enumerate(listings):
            occupation = Occupations(n, listing)
            for sigma, kind in product(*cases):
                readout = occupation.readout(kind)
                base = occupation.start(sigma)
                for order in orders(n, smoke):
                    table, norm = occupation.probabilities(occupation.grow(base, order), readout)
                    key = sigma, kind, order
                    if listing_index == 0:
                        reference[key] = (table, norm)
                    else:
                        expected, expected_norm = reference[key]
                        assert np.array_equal(table * expected_norm, expected * norm)
        for sigma, kind in product(*cases):
            distinct = {reference[sigma, kind, order][0].tobytes() for order in orders(n, smoke)}
            differing_order_tables += int(len(distinct) > 1)
        configurations = len(reference)
        result[f"n{n}"] = {"listings": len(listings), "distinct_listings": len(set(listings)),
                            "reference_tables": configurations, "table_runs": len(listings) * configurations,
                            "comparisons_to_reference": (len(listings) - 1) * configurations,
                            "probability_cells_compared": (len(listings) - 1) * configurations * 4 ** n,
                            "creation_and_reader_setups_with_commit_order_contrast": differing_order_tables}
    return result


def birth_commutation(smoke):
    occupation = Occupations(3, ascending_listing(3))
    words = occupation.words[:32] if smoke else occupation.words
    signed_nonzero = signed_zero = unsigned_nonzero = unsigned_zero = 0
    for i, j in permutations(range(3), 2):
        for word in words:
            basis = np.array([word]), np.array([1])
            ij = occupation.dense(occupation.grow(basis, (j, i)))
            ji = occupation.dense(occupation.grow(basis, (i, j)))
            both_occupied = bool((word & (1 << (3 * i))) and (word & (1 << (3 * j))))
            assert np.array_equal(ij, -ji if both_occupied else ji)
            nonzero = bool(np.any(ij))
            signed_nonzero += both_occupied and nonzero
            signed_zero += both_occupied and not nonzero
            unsigned_nonzero += not both_occupied and nonzero
            unsigned_zero += not both_occupied and not nonzero
    return {"basis_states": words.size, "ordered_birth_pairs": 6, "failures": 0,
            "nonzero_minus_sign": signed_nonzero, "zero_minus_sign": signed_zero,
            "nonzero_plus_sign": unsigned_nonzero, "zero_plus_sign": unsigned_zero}


def order_pair_signs(smoke):
    result = {}
    for n in (3, 4):
        occupation = Occupations(n)
        base = occupation.start(tuple(range(n)))
        by_order = {order: occupation.compact(occupation.grow(base, order)).reshape(1 << n, -1)
                    for order in orders(n, smoke)}
        pairs = coefficients = changed_signs = 0
        for (left_order, left), (right_order, right) in combinations(by_order.items(), 2):
            changed = [(i, j) for i, j in combinations(range(n), 2)
                       if (left_order.index(i) < left_order.index(j)) != (right_order.index(i) < right_order.index(j))]
            signs = np.ones(1 << n, dtype=np.int64)
            for i, j in changed:
                mask = (1 << i) | (1 << j)
                signs[(occupation.measure.labels & mask) == mask] *= -1
            assert np.array_equal(left, right * signs[:, None])
            pairs += 1
            coefficients += int(np.count_nonzero(left))
            changed_signs += int(np.count_nonzero(left != right))
        result[f"n{n}"] = {"pairs_of_orders": pairs, "nonzero_coefficients_compared": coefficients,
                            "coefficients_changing_sign": changed_signs, "failures": 0}
    return result


def effective_amplitudes(occupation, state):
    amplitudes = occupation.compact(state).reshape(occupation.measure.size, -1)
    assert np.all(amplitudes == amplitudes[:, :1])
    assert np.array_equal(amplitudes[:, 0] != 0, occupation.measure.parity == 1)
    assert np.all(np.abs(amplitudes[occupation.measure.even]) == 1)
    return amplitudes[:, 0]


def round_tables(n, occupation, sigmas, smoke):
    measure = occupation.measure
    target, denominator = measure.target()
    result = {}
    ascending_tables = []
    ascending_sum = np.zeros(4 ** n, dtype=np.int64)
    occupation.verify_block_factor()
    for label, sigma in sigmas.items():
        base = occupation.start(sigma)
        cyclic = {sigma[k:] + sigma[:k]: sum(1 << j for j in sigma[:k]) for k in range(n)}
        candidates = orders(n, smoke)
        if smoke:
            candidates = sorted(set(candidates) | set(cyclic))
        carrying, shifts, matches = [], {}, {}
        for pi in candidates:
            state = occupation.grow(base, pi)
            amplitudes = effective_amplitudes(occupation, state)
            table = measure.direct(amplitudes)
            assert np.array_equal(measure.denominator(amplitudes), denominator)
            assert np.array_equal(table.sum(axis=1), denominator)
            values = correlation_numerators(table, measure)
            carries = contradiction(values, denominator, measure)
            fixed_matches = int(np.count_nonzero(table == target))
            matches[fixed_matches] = matches.get(fixed_matches, 0) + 1
            if carries:
                carrying.append(name(pi))
            if pi in cyclic:
                moved = cyclic[pi]
                remap = measure.labels ^ (measure.labels[:, None] & moved)
                relabelled = table[measure.labels[:, None], remap]
                moved_matches = int(np.count_nonzero(relabelled == target))
                shifts[name(pi)] = {"fixed_label_matches": fixed_matches, "relabeled_matches": moved_matches}
                assert moved_matches == 4 ** n
            assert carries == (pi in cyclic)
            assert (fixed_matches == 4 ** n) == (pi == sigma)
            if label == "ascending":
                ascending_tables.append(table)
                ascending_sum += occupation.compact(state)
        result[label] = {"sigma": name(sigma), "orders": len(candidates), "carrying_orders": carrying,
                         "noncarrying_orders": len(candidates) - len(carrying),
                         "probability_cells_compared_to_target": len(candidates) * 4 ** n,
                         "fixed_label_match_counts": matches, "shifts": shifts}
    return result, ascending_tables, ascending_sum


def joint_weighting(n, occupation, smoke):
    measure = occupation.measure
    candidates = orders(n, smoke)
    carrying = 0
    for sigma in candidates:
        base = occupation.start(sigma)
        for pi in candidates:
            amplitudes = effective_amplitudes(occupation, occupation.grow(base, pi))
            table = measure.direct(amplitudes)
            numerators = correlation_numerators(table, measure)
            carries = contradiction(numerators, measure.denominator(amplitudes), measure)
            assert carries == any(pi == sigma[k:] + sigma[:k] for k in range(n))
            carrying += carries
    pairs = len(candidates) ** 2
    return {"pairs": pairs, "carrying": carrying, "share": str(Fraction(carrying, pairs))}


def mixture(n, occupation, tables, coherent, carrying, smoke):
    measure = occupation.measure
    count = len(tables)
    total = np.sum(tables, axis=0)
    numerators = correlation_numerators(total, measure)
    denominator = total.sum(axis=1)
    averages = [Fraction(int(numerators[t]), int(denominator[t])) for t in measure.even]
    sharp = [word_label(int(t), n) for t, value in zip(measure.even, averages, strict=True) if abs(value) == 1]
    coherent_by_spectator = coherent.reshape(measure.size, -1)
    assert np.all(coherent_by_spectator == coherent_by_spectator[:, :1])
    coherent_amplitudes = coherent_by_spectator[:, 0]
    old_words = np.flatnonzero(coherent_amplitudes)
    support = [word_label(int(word), n) for word in old_words]
    nonzero = coherent[coherent != 0]
    if not smoke:
        assert sharp == ["0" * n]
        assert support == ["0" * n] and len(nonzero) == 1 << n
        assert np.all(np.abs(nonzero) == count)
    coherent_correlations = correlation_numerators(measure.direct(coherent_amplitudes), measure)
    if not smoke:
        assert np.all(coherent_correlations[measure.even[1:]] == 0)
    assert not contradiction(numerators, denominator, measure)
    return {"orders": count, "carrying": carrying, "share": str(Fraction(carrying, count)),
            "mean_even_setting_correlations": {word_label(int(t), n): str(value)
                                               for t, value in zip(measure.even, averages, strict=True)},
            "sharp_even_setting_masks": sharp, "coherent_sum_old_words": support,
            "nonzero_coherent_coefficients": len(nonzero),
            "coherent_sum_nonzero_correlations_with_nonempty_even_flips": int(
                np.count_nonzero(coherent_correlations[measure.even[1:]])),
            "coherent_sum_absolute_amplitudes": sorted(map(int, np.unique(np.abs(nonzero)))),
            "normalized_coherent_sum_norm_squared": str(Fraction(int(coherent @ coherent), count ** 2 * 2 ** (2 * n - 1)))}


def round_predictions(smoke):
    random = Random(SEED + 3)
    p2, p7 = {}, {"joint_sigma_pi": {}}
    for n in (3, 4, 5, 6):
        start_time = perf_counter()
        n_key = f"n{n}"
        occupation = Occupations(n)
        sigmas = creation_orders(n, random)
        p2[n_key], tables, coherent = round_tables(n, occupation, sigmas, smoke)
        p7[n_key] = mixture(n, occupation, tables, coherent, len(p2[n_key]["ascending"]["carrying_orders"]), smoke)
        if n < 5:
            p7["joint_sigma_pi"][n_key] = joint_weighting(n, occupation, smoke)
        p2[n_key]["elapsed_seconds_including_p7"] = round(perf_counter() - start_time, 3)
    return p2, p7


def verify_receipts(result):
    receipt = json.loads(CONFIRM.read_text())
    gate = result["gate"]
    assert receipt["gate"]["a_replay"]["rows_compared"] == gate["replay"]["order_rows"] + gate["replay"]["summary_rows"]
    assert all(receipt["gate"]["b_anticommutation"][key]["failures"] == 0 for key in ("ascending", "random"))
    assert receipt["gate"]["c_second_path"]["tables_compared"] == sum(row["table_runs"] for row in gate["matrix_path"].values())
    for key, row in gate["listings"].items():
        stated = receipt["gate"]["d_listing_gauge"][key]
        assert stated["listings"] == row["listings"] and stated["tables"] == row["table_runs"] and stated["differing"] == 0
    claim = receipt["P1"]
    assert claim["commutation_identity"]["basis_states"] == result["P1"]["commutation_identity"]["basis_states"]
    assert claim["commutation_identity"]["failures"] == result["P1"]["commutation_identity"]["failures"]
    for key, row in result["P1"]["reordering_sign"].items():
        assert all(claim["reordering_sign"][key][field] == row[field] for field in ("pairs_of_orders", "failures"))
    for n in (3, 4, 5, 6):
        key = f"n{n}"
        for creation in ("ascending", "descending", "random"):
            actual = result["P2"][key][creation]
            claim = receipt["P2"][key][creation]
            assert all(claim[field] == actual[field] for field in ("sigma", "orders", "carrying_orders"))
            assert claim["carrying"] == len(actual["carrying_orders"])
            assert set(claim["shifts"]) == set(actual["shifts"])
            for shift, cells in actual["shifts"].items():
                row = claim["shifts"][shift]
                assert row["fixed_labels"] == (cells["fixed_label_matches"] == 4 ** n)
                assert row["after_relabelling_moved"] == (cells["relabeled_matches"] == 4 ** n)
        actual = result["P7"][key]
        claim = receipt["P7"][key]
        assert all(claim[field] == actual[field] for field in ("orders", "carrying", "share", "coherent_sum_old_words"))
        assert claim["mixture_all_sharp"] == (len(actual["sharp_even_setting_masks"]) == 2 ** (n - 1))
        if n < 5:
            row = receipt["P7"]["joint_sigma_pi"][key]
            assert all(row[field] == value for field, value in result["P7"]["joint_sigma_pi"][key].items())
    return {"gate_and_P1_P2_P7_receipt_disagreements": 0,
            "P2_comparison": "The receipt stores carrying orders and agreement flags. The referee recomputed all probability cells."}


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--smoke", action="store_true", help="Time a bounded subset with the same arithmetic")
    cli.add_argument("--write", action="store_true", help="Save the completed replay to rounds.json")
    options = cli.parse_args()
    if options.smoke and options.write:
        cli.error("A timing subset cannot be written as a complete replay")
    start = perf_counter()
    timings = {}

    def timed(action, *arguments):
        before = perf_counter()
        result = action(*arguments)
        timings[action.__name__] = round(perf_counter() - before, 3)
        return result

    gate = {"replay": timed(gate_replay), "anticommutation": timed(gate_car, options.smoke),
            "matrix_path": timed(gate_second_path, options.smoke), "listings": timed(gate_listings, options.smoke)}
    p1 = {"commutation_identity": timed(birth_commutation, options.smoke),
          "reordering_sign": timed(order_pair_signs, options.smoke)}
    p2, p7 = timed(round_predictions, options.smoke)
    result = {"stage": "timing subset" if options.smoke else "full independent replay", "gate": gate,
              "P1": p1, "P2": p2, "P7": p7}
    if not options.smoke:
        result["receipt_comparison"] = timed(verify_receipts, result)
        cases = [row for size in p2.values() for row in size.values() if isinstance(row, dict)]
        result["P2_totals"] = {
            "orders": sum(row["orders"] for row in cases),
            "distinct_creation_and_commit_pairs": sum(
                len({row["sigma"] for row in size.values() if isinstance(row, dict)}) * size["ascending"]["orders"]
                for size in p2.values()),
            "carrying_orders": sum(len(row["carrying_orders"]) for row in cases),
            "noncarrying_orders": sum(row["noncarrying_orders"] for row in cases),
            "probability_cells_compared_to_target": sum(row["probability_cells_compared_to_target"] for row in cases),
            "fixed_label_cells_for_matching_orders": sum(row["shifts"][row["sigma"]]["fixed_label_matches"] for row in cases),
            "cyclic_shift_cells_matching_after_relabelling": sum(
                cells["relabeled_matches"] for row in cases for cells in row["shifts"].values()),
        }
    result["elapsed_seconds"] = timings
    result["total_elapsed_seconds"] = round(perf_counter() - start, 3)
    rendered = json.dumps(result, indent=2) + "\n"
    if options.smoke:
        print(json.dumps({"elapsed_seconds": timings, "total_elapsed_seconds": result["total_elapsed_seconds"],
                          "rounds": {key: value["elapsed_seconds_including_p7"] for key, value in p2.items()}}, indent=2))
    else:
        if options.write:
            (HERE / "rounds.json").write_text(rendered)
            print(json.dumps({"P2_totals": result["P2_totals"], "elapsed_seconds": timings}, indent=2))
        else:
            print(rendered, end="")


if __name__ == "__main__":
    main()
