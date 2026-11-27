"""Independent replay of the birth-sign constructions and two-reader scores."""

import argparse
import json
from collections import Counter, defaultdict
from fractions import Fraction
from itertools import combinations, permutations, product
from math import cos, pi, sin, sqrt
from pathlib import Path

import numpy as np


BITS3 = tuple(product((0, 1), repeat=3))
WORDS = tuple(product((0, 1), repeat=6))
WORD_INDEX = {word: index for index, word in enumerate(WORDS)}
IDENTITY_WORDS = np.eye(len(WORDS), dtype=np.int64)
PARENTS = ((0, 1, 2), (1, 3, 4), (0, 3, 5))

PAULIS = {
    "I": np.eye(2, dtype=complex),
    "X": np.array([[0, 1], [1, 0]], dtype=complex),
    "Y": np.array([[0, -1j], [1j, 0]]),
    "Z": np.diag([1, -1]).astype(complex),
}
I, X, Y, Z = PAULIS.values()
I4 = np.eye(4, dtype=complex)
AXES = "XYZ"
CHSH_SIGNS = (1, 1, 1, -1)
TOLERANCE = 1e-12


def bit_string(word):
    return "".join(map(str, word))


def flip(word, places):
    return tuple(bit ^ (place in places) for place, bit in enumerate(word))


class Question:
    def __init__(self, changes=(), signs=()):
        self.changes = tuple(changes)
        self.signs = tuple(signs)
        self.destinations = np.array([WORD_INDEX[flip(word, self.changes)] for word in WORDS])
        self.multipliers = np.array([(-1) ** sum(word[i] for i in self.signs) for word in WORDS])

    def apply(self, columns):
        shifted = np.empty_like(columns)
        shifted[self.destinations] = self.multipliers[:, None] * columns
        return shifted


def signed_identity(matrix):
    for sign in (1, -1):
        if np.array_equal(matrix, sign * IDENTITY_WORDS):
            return sign
    return None


def target(setting, answer):
    if sum(setting) == 1:
        return Fraction(1, 4) if sum(answer) % 2 == 0 else Fraction(0)
    if sum(setting) == 3:
        return Fraction(1, 4) if sum(answer) % 2 == 1 else Fraction(0)
    return Fraction(1, 8)


def exact_table(reads, preparation, normalizer):
    table = {}
    for setting in BITS3:
        row = {}
        for answer in BITS3:
            projected = preparation
            for pair, choice, bit in zip(reads, setting, answer, strict=True):
                projected = projected + (-1) ** bit * pair[choice].apply(projected)
            row[answer] = Fraction(int(np.sum(projected * projected)), normalizer * 4**3)
        assert sum(row.values()) == 1
        table[setting] = row
    scored = [setting for setting in BITS3 if sum(setting) % 2]
    score = sum(
        probability
        for setting in scored
        for answer, probability in table[setting].items()
        if target(setting, answer)
    ) / len(scored)
    matches = sum(probability == target(setting, answer) for setting, row in table.items()
                  for answer, probability in row.items())
    return {
        "score": str(score),
        "matches_of_64": matches,
        "probabilities": {
            bit_string(setting): {bit_string(answer): str(probability) for answer, probability in row.items()}
            for setting, row in table.items()
        },
    }


def read_algebra(reads, allowed):
    matrices = [[read.apply(IDENTITY_WORDS) for read in pair] for pair in reads]
    assert all(np.array_equal(matrix, matrix.T) and np.array_equal(matrix @ matrix, IDENTITY_WORDS)
               for pair in matrices for matrix in pair)
    cross_commuting = sum(
        np.array_equal(left @ right, right @ left)
        for first, second in combinations(matrices, 2)
        for left, right in product(first, second)
    )
    contexts = [matrices[0][a] @ matrices[1][b] @ matrices[2][c]
                for a, b, c in BITS3 if (a + b + c) % 2]
    products = Counter(str(signed_identity(a @ b @ c @ d)) for a, b, c, d in permutations(contexts))
    context_commuting = sum(np.array_equal(a @ b, b @ a) for a, b in combinations(contexts, 2))
    return {
        "cross_reader_commuting_pairs_of_12": cross_commuting,
        "scored_context_commuting_pairs_of_6": context_commuting,
        "reader_product_squares": [signed_identity((a @ b) @ (a @ b)) for a, b in matrices],
        "context_product_signs_over_24_orders": dict(sorted(products.items())),
        "allowed_words_left_by_each_read": [
            [sum(read.destinations[word] not in allowed for word in allowed) for read in pair] for pair in reads
        ],
    }


def birth_sign_study():
    holders = Counter(place for parent in PARENTS for place in parent)
    shared_places = {place for place, count in holders.items() if count == 2}
    readers = tuple((next(iter(shared_places.difference(parent))),
                     next(place for place in parent if holders[place] == 1)) for parent in PARENTS)
    allowed = tuple(index for index, word in enumerate(WORDS)
                    if all(sum(word[place] for place in parent) % 2 == 0 for parent in PARENTS))
    allowed_set = set(allowed)
    assert len(allowed) == 8
    changes = []
    for parent in PARENTS:
        candidates = [WORDS[index] for index in allowed if index and all(WORDS[index][p] == 0 for p in parent)]
        assert len(candidates) == 1
        changes.append(tuple(p for p, bit in enumerate(candidates[0]) if bit))

    phases = np.zeros((len(WORDS), 1), dtype=np.int64)
    for index in allowed:
        shared_values = [WORDS[index][s] for s, _ in readers]
        phases[index, 0] = (-1) ** sum(a * b for a, b in combinations(shared_values, 2))
    signed_changes = [Question(change, (loose,)) for change, (_, loose) in zip(changes, readers, strict=True)]
    assert all(np.array_equal(read.apply(phases), phases) for read in signed_changes)
    closing_product_checks = 0
    for order in permutations(signed_changes):
        for index in allowed:
            sign = 1
            shifted = index
            for read in order:
                sign *= read.multipliers[shifted]
                shifted = read.destinations[shifted]
            bare_sign = (-1) ** sum(WORDS[index][loose] for _, loose in readers)
            assert sign == -bare_sign
            assert phases[shifted, 0] == -phases[index, 0]
            closing_product_checks += 1

    preparations = {"signed": phases, "positive": abs(phases), "mixture": IDENTITY_WORDS[:, allowed]}
    change_reads = [(Question(signs=(s,)), Question(change))
                    for (s, _), change in zip(readers, changes, strict=True)]
    rephased_reads = [(Question(signs=(s,)), signed_change)
                      for (s, _), signed_change in zip(readers, signed_changes, strict=True)]
    confined_reads = [(Question((loose,), (s,)), Question((s,))) for s, loose in readers]
    value_reads = [(Question(signs=(s,)), Question(signs=(loose,))) for s, loose in readers]
    unsigned_reads = [(Question((loose,)), Question((s,))) for s, loose in readers]
    families = {
        "value": value_reads,
        "change": change_reads,
        "rephased_change": rephased_reads,
        "confined": confined_reads,
        "confined_without_sign": unsigned_reads,
    }
    results = {}
    for name, reads in families.items():
        algebra = read_algebra(reads, allowed_set)
        assert algebra["cross_reader_commuting_pairs_of_12"] == 12
        assert algebra["scored_context_commuting_pairs_of_6"] == 6
        results[name] = {
            "reads_by_reader": [[{"flips": q.changes, "sign_reads": q.signs} for q in pair] for pair in reads],
            "algebra": algebra,
            "preparations": {key: exact_table(reads, state, len(allowed)) for key, state in preparations.items()},
        }

    for name, preparation in (("change", "signed"), ("rephased_change", "positive"), ("confined", "signed")):
        family = results[name]
        assert family["preparations"][preparation]["matches_of_64"] == 64
        assert family["preparations"][preparation]["score"] == "1"
        assert family["algebra"]["reader_product_squares"] == [-1] * 3
        assert family["algebra"]["context_product_signs_over_24_orders"] == {"-1": 24}
    assert results["confined"]["algebra"]["allowed_words_left_by_each_read"] == [[8, 8]] * 3
    for name in ("change", "rephased_change"):
        assert results[name]["algebra"]["allowed_words_left_by_each_read"] == [[0, 0]] * 3
    for (s, loose), change in zip(readers, changes, strict=True):
        assert set(change) - {s, loose} == {other for _, other in readers if other != loose}
    for name in ("value", "confined_without_sign"):
        assert results[name]["algebra"]["reader_product_squares"] == [1] * 3
        assert results[name]["algebra"]["context_product_signs_over_24_orders"] == {"1": 24}
    assert results["value"]["preparations"]["signed"]["score"] == "3/4"
    assert results["value"]["preparations"]["signed"]["matches_of_64"] == 56
    assert results["confined_without_sign"]["preparations"]["signed"]["score"] == "5/8"

    phase_controls = {}
    for keep in BITS3:
        if 0 < sum(keep) < 3:
            reads = [confined_reads[i] if sign_kept else unsigned_reads[i] for i, sign_kept in enumerate(keep)]
            algebra = read_algebra(reads, allowed_set)
            observed = exact_table(reads, phases, len(allowed))
            phase_controls[bit_string(keep)] = {
                "score": observed["score"], "matches_of_64": observed["matches_of_64"], **algebra,
            }
    return {
        "reader_pairs_shared_then_loose": readers,
        "allowed_word_signs": {bit_string(WORDS[index]): int(phases[index, 0]) for index in allowed},
        "signed_steps_close_odd_word_and_order_checks": closing_product_checks,
        "read_families": results,
        "partial_sign_controls_1_means_kept": phase_controls,
    }


def close(left, right):
    return np.allclose(left, right, atol=TOLERANCE, rtol=0)


def chsh_operator(a0, a1, b0, b1):
    return np.kron(a0, b0 + b1) + np.kron(a1, b0 - b1)


def landau_square(a0, a1, b0, b1):
    return 4 * I4 - np.kron(a0 @ a1 - a1 @ a0, b0 @ b1 - b1 @ b0)


def pauli_products():
    return {a + b: np.kron(first, second) for (a, first), (b, second) in product(PAULIS.items(), repeat=2)}


def stabilizer_states(paulis):
    # An unsigned triple closes exactly when its first two products give its third up to sign.
    states = []
    groups = []
    labels = [label for label in paulis if label != "II"]
    for first, second, third in combinations(labels, 3):
        multiplication = paulis[first] @ paulis[second]
        sign = next((s for s in (1, -1) if np.array_equal(multiplication, s * paulis[third])), None)
        if sign is None:
            continue
        groups.append((first, second, third))
        for a, b in product((1, -1), repeat=2):
            profile = dict.fromkeys(paulis, 0)
            profile.update({"II": 1, first: a, second: b, third: sign * a * b})
            density = (I4 + a * paulis[first] + b * paulis[second] + sign * a * b * paulis[third]) / 4
            assert np.trace(density) == 1 and np.array_equal(density @ density, density)
            assert all(np.trace(density @ matrix) == profile[name] for name, matrix in paulis.items())
            states.append((density, profile))
    assert len(groups) == 15
    assert len({tuple(profile.values()) for _, profile in states}) == len(states) == 60
    return states


def pauli_scores(profile):
    settings = tuple(product(AXES, (1, -1)))
    best_distinct = None
    counts = Counter()
    for (a0, s0), (a1, s1), (b0, t0), (b1, t1) in product(settings, repeat=4):
        score = (s0 * t0 * profile[a0 + b0] + s0 * t1 * profile[a0 + b1]
                 + s1 * t0 * profile[a1 + b0] - s1 * t1 * profile[a1 + b1])
        counts[score] += 1
        if a0 != a1 and b0 != b1:
            best_distinct = score if best_distinct is None else max(score, best_distinct)
    return counts, best_distinct


def serialize_counts(counts):
    return {str(value): count for value, count in sorted(counts.items())}


def born_two_readers(density, a_reads, b_reads):
    dimension = a_reads[0].shape[0]
    identity = np.eye(dimension)
    answers = tuple(product((1, -1), repeat=2))
    table = []
    correlations = []
    for a, b in product(a_reads, b_reads):
        probabilities = [float(np.trace(density @ np.kron((identity + s * a) / 2, (identity + t * b) / 2)).real)
                         for s, t in answers]
        assert close(sum(probabilities), 1) and min(probabilities) >= -TOLERANCE
        table.append(probabilities)
        correlations.append(sum(s * t * p for (s, t), p in zip(answers, probabilities, strict=True)))
    return {
        "probabilities_00_01_10_11_answers_pp_pm_mp_mm": table,
        "correlations_00_01_10_11": correlations,
        "score": float(np.dot(CHSH_SIGNS, correlations)),
    }


def sibling_preparation():
    words = {paid: [word for word in product((0, 1), repeat=2) if len(set((paid, *word))) == 2]
             for paid in (0, 1)}

    def equal(word):
        return word[0] == word[1]

    orbits = defaultdict(list)
    for a, b, c in product(words[0], words[0], words[1]):
        orbits[tuple(sorted((equal(a), equal(b)))), equal(c)].append((a, b, c))
    assert sorted(map(len, orbits.values())) == [1, 2, 4, 4, 8, 8]
    weights = {triple: Fraction(1, len(orbits) * len(members)) for members in orbits.values() for triple in members}
    siblings, other = defaultdict(Fraction), defaultdict(Fraction)
    for (a, b, c), weight in weights.items():
        siblings[a, b] += weight
        other[c] += weight
    assert all(weight == siblings[a, b] * other[c] for (a, b, c), weight in weights.items())

    named_words = words[0]
    amplitudes = np.array([[sqrt(siblings[a, b]) for b in named_words] for a in named_words])
    same = np.array([int(equal(word)) for word in named_words])
    mixed = (1 - same) / sqrt(2)
    isometry = np.column_stack((same, mixed))
    reduced = isometry.T @ amplitudes @ isometry
    assert close(isometry @ reduced @ isometry.T, amplitudes)
    assert close(reduced, [[1 / sqrt(3), 1 / sqrt(6)], [1 / sqrt(6), 1 / sqrt(3)]])
    assert close(np.linalg.det(reduced), 1 / 6)

    moves = []
    for place in (0, 1):
        move = np.zeros((3, 3))
        for index, word in enumerate(named_words):
            proposed = flip(word, (place,))
            move[named_words.index(proposed) if proposed in named_words else index, index] = 1
        moves.append(move)
    adjacency = sum(moves)
    adjacency -= np.diag(adjacency.diagonal())
    eigenvalues, eigenvectors = np.linalg.eigh(adjacency)
    uniform = np.ones(3) / sqrt(3)
    z_named = np.diag(2 * same - 1)
    r_named = 2 * np.outer(uniform, uniform) - np.eye(3)
    for eigenvalue, sign in zip(eigenvalues, (-1, 0, 1), strict=True):
        assert close(eigenvalue, sign * sqrt(2))

    r = (2 * sqrt(2) * X - Z) / 3
    assert close(isometry.T @ r_named @ isometry, r)
    assert close(isometry.T @ z_named @ isometry, Z)
    assert close(r_named @ isometry, isometry @ r)
    assert close(z_named @ isometry, isometry @ Z)
    b_named = (-z_named @ r_named @ z_named, r_named)
    b_reduced = (-Z @ r @ Z, r)
    assert close(b_reduced[0], (2 * sqrt(2) * X + Z) / 3)

    named = amplitudes.ravel()
    reduced = reduced.ravel()
    named_density = np.outer(named, named)
    reduced_density = np.outer(reduced, reduced)
    by_class = np.kron(isometry, isometry)
    marginal = (amplitudes**2).sum(axis=1)
    independent = np.sqrt(np.outer(marginal, marginal)).ravel()
    reinforced_class_weights = {(True, True): 1 / 6, (True, False): 1 / 6,
                                (False, True): 1 / 6, (False, False): 1 / 2}
    reinforced = []
    for a, b in product(named_words, repeat=2):
        number_within_class = 2 ** (2 - equal(a) - equal(b))
        reinforced.append(sqrt(reinforced_class_weights[equal(a), equal(b)] / number_within_class))
    controls = {
        "coherent": named_density,
        "named_mixture": np.diag(named**2),
        "class_mixture": by_class @ np.diag(reduced**2) @ by_class.T,
        "independent_coherent": np.outer(independent, independent),
        "product_of_local_states": np.kron(amplitudes @ amplitudes.T, amplitudes.T @ amplitudes),
        "reinforced_coherent": np.outer(reinforced, reinforced),
    }
    tables = {}
    for kernel_sign in (1, -1):
        x_named = (eigenvectors * [-1, kernel_sign, 1]) @ eigenvectors.T
        assert close(x_named @ isometry, isometry @ X)
        tables[str(kernel_sign)] = {name: born_two_readers(density, (x_named, z_named), b_named)
                                    for name, density in controls.items()}
    for rows in tables.values():
        assert close(rows["named_mixture"]["score"], 0)
        assert close(rows["class_mixture"]["score"], 2 / 9)
    toggles = [born_two_readers(named_density, (move, z_named), b_named)["score"] for move in moves]
    assert close(toggles, [2, 2])
    return reduced_density, (X, Z), b_reduced, {
        "current_birth_orbit_sizes": sorted(map(len, orbits.values())),
        "named_weights_01_10_11": [[str(siblings[a, b]) for b in named_words] for a in named_words],
        "third_child_weights": {bit_string(word): str(value) for word, value in other.items()},
        "reduced_amplitudes_EE_EM_ME_MM": reduced.tolist(),
        "fixed_reads_by_sign_on_unused_eigenvector": tables,
        "scores_after_substituting_either_single_toggle_for_X": toggles,
    }


def two_reader_study():
    paulis = pauli_products()
    states = stabilizer_states(paulis)
    stabilizer_scores, stabilizer_best_distinct = Counter(), Counter()
    for _, profile in states:
        counts, distinct = pauli_scores(profile)
        stabilizer_scores.update(counts)
        stabilizer_best_distinct[distinct] += 1
    assert max(stabilizer_scores) == 2 and sum(stabilizer_scores.values()) == 60 * 6**4

    density, a_reads, b_reads, sibling = sibling_preparation()
    profile = {}
    for a, b in product(AXES, repeat=2):
        value = np.trace(density @ paulis[a + b]).real
        as_fraction = Fraction(round(3 * value), 3)
        assert close(value, float(as_fraction))
        profile[a + b] = as_fraction
    assert profile == {a + b: {"XX": 1, "YY": Fraction(-1, 3), "ZZ": Fraction(1, 3)}.get(a + b, 0)
                       for a, b in product(AXES, repeat=2)}
    pauli_counts, distinct = pauli_scores(profile)
    assert sum(pauli_counts.values()) == 6**4 and max(pauli_counts) == 2 and distinct == Fraction(4, 3)
    sibling_overlap = max(np.trace(stabilizer @ density).real for stabilizer, _ in states)
    assert sibling_overlap < 1 - TOLERANCE

    table = born_two_readers(density, a_reads, b_reads)
    assert close(table["probabilities_00_01_10_11_answers_pp_pm_mp_mm"],
                 sibling["fixed_reads_by_sign_on_unused_eigenvector"]["1"]["coherent"]
                 ["probabilities_00_01_10_11_answers_pp_pm_mp_mm"])
    assert close(table["correlations_00_01_10_11"], [2 * sqrt(2) / 3, 2 * sqrt(2) / 3, 1 / 9, -1 / 9])
    assert close(table["score"], (2 + 12 * sqrt(2)) / 9)
    assert all(not close(read, sign * PAULIS[axis]) for read in b_reads for sign, axis in product((1, -1), AXES))
    actual_read_op = chsh_operator(*a_reads, *b_reads)
    assert close(actual_read_op @ actual_read_op, landau_square(*a_reads, *b_reads))
    bob_product = b_reads[0] @ b_reads[1]
    assert close(bob_product, (7 * I + 4 * sqrt(2) * 1j * Y) / 9)
    assert close(bob_product @ bob_product, (17 * I + 56 * sqrt(2) * 1j * Y) / 81)

    # Bound by the largest two squared singular values of the correlations. The displayed reads attain it.
    correlations = np.array([[float(profile[a + b]) for b in AXES] for a in AXES])
    largest_two = sorted(np.linalg.eigvalsh(correlations.T @ correlations))[-2:]
    optimum = 2 * sqrt(sum(largest_two))
    optimum_reads = ((3 * X + Z) / sqrt(10), (3 * X - Z) / sqrt(10))
    optimum_table = born_two_readers(density, a_reads, optimum_reads)
    assert close(optimum, 2 * sqrt(10) / 3) and close(optimum_table["score"], optimum)

    altered_a = (X, (X + Z) / sqrt(2))
    altered_alice_product = altered_a[0] @ altered_a[1]
    assert close(altered_alice_product @ altered_alice_product, -1j * Y)
    counterexample = born_two_readers(density, altered_a, b_reads)
    assert close(counterexample["score"], 13 * sqrt(2) / 9) and counterexample["score"] > 2

    xz = chsh_operator(X, Z, X, Z)
    assert close(xz @ xz, landau_square(X, Z, X, Z)) and close(xz @ xz, 4 * I4 + 4 * paulis["YY"])
    state = np.array([sin(pi / 8), cos(pi / 8), cos(pi / 8), -sin(pi / 8)]) / sqrt(2)
    assert close(xz @ state, 2 * sqrt(2) * state)
    state_pauli_xx = np.vdot(state, paulis["XX"] @ state).real
    assert close(state_pauli_xx, 1 / sqrt(2))
    xz_overlap = max(np.vdot(state, stabilizer @ state).real for stabilizer, _ in states)
    assert xz_overlap < 1 - TOLERANCE
    sign_cases = Counter()
    terms = [paulis[label] for label in ("XX", "XZ", "ZX", "ZZ")]
    for signs in product((1, -1), repeat=4):
        operator = sum(sign * term for sign, term in zip(signs, terms, strict=True))
        yy_coefficient = 2 * (signs[1] * signs[2] - signs[0] * signs[3])
        assert close(operator @ operator, 4 * I4 + yy_coefficient * paulis["YY"])
        largest = np.linalg.eigvalsh(operator)[-1]
        assert close(largest, 2 * sqrt(2) if yy_coefficient else 2)
        sign_cases[yy_coefficient] += 1

    commuting_tests = 0
    rotated_a = ((X + Y + Z) / sqrt(3), X)
    rotated_b = (Y, (X - 2 * Y + Z) / sqrt(6))
    for fixed, other in (((X, Z), (X, Z)), (a_reads, b_reads), (rotated_a, rotated_b)):
        for a1 in (fixed[0], -fixed[0], I, -I):
            operator = chsh_operator(fixed[0], a1, *other)
            assert close(operator @ operator, 4 * I4)
            commuting_tests += 1
        for b1 in (other[0], -other[0], I, -I):
            operator = chsh_operator(*fixed, other[0], b1)
            assert close(operator @ operator, 4 * I4)
            commuting_tests += 1

    sibling.update({
        "pauli_correlations": {label: str(value) for label, value in profile.items()},
        "signed_pauli_score_counts": serialize_counts(pauli_counts),
        "best_with_distinct_pauli_axes_at_each_reader": str(distinct),
        "largest_squared_overlap_with_listed_stabilizer_states": float(sibling_overlap),
        "prescribed_reduced_reads": table,
        "optimal_score": optimum,
        "optimal_reads": optimum_table,
        "neither_pair_anticommutes_counterexample": counterexample,
    })
    return {
        "stabilizer_states": len(states),
        "stabilizer_signed_pauli_score_counts": serialize_counts(stabilizer_scores),
        "stabilizer_distinct_axis_maximum_counts_by_state": serialize_counts(stabilizer_best_distinct),
        "sibling": sibling,
        "XZ_versus_XZ": {
            "eigenvalues": np.linalg.eigvalsh(xz).tolist(),
            "top_state_00_01_10_11": state.tolist(),
            "top_state_XX_expectation": float(state_pauli_xx),
            "top_state_largest_squared_overlap_with_listed_stabilizer_states": float(xz_overlap),
            "YY_coefficient_counts_over_16_sign_layouts": serialize_counts(sign_cases),
        },
        "commuting_reader_operator_square_equals_4I_cases": commuting_tests,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pilot", action="store_true", help="run the exact three-reader replay only")
    args = parser.parse_args()
    birth = birth_sign_study()
    if args.pilot:
        print("Rebuilt the three-reader probabilities and checked all 48 closing signs.")
        return
    record = {"P5_birth_signs": birth, "P6_two_reader": two_reader_study()}
    Path(__file__).with_name("rebuild_reads.json").write_text(json.dumps(record, indent=2) + "\n")
    print("Rebuilt the birth-sign probabilities, 60 stabilizer states, and sibling bounds.")


if __name__ == "__main__":
    main()
