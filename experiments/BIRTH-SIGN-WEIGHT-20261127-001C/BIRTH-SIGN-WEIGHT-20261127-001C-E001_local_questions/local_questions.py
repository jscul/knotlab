"""Exact local questions on the three allowed completions of a not-all-equal birth."""

import argparse
import json
from collections import Counter
from itertools import permutations, product

import sympy as sp


def equal(word):
    return word[0] == word[1]


def orbit_weights(words):
    """Swap the two births and independently exchange their two fresh places."""
    categories = [sum(map(equal, pair)) for pair in product(words, repeat=2)]
    multiplicity = Counter(categories)
    return sp.Matrix(len(words), len(words), [
        sp.Rational(1, len(multiplicity) * multiplicity[k]) for k in categories
    ])


def reinforced_weights(words):
    """Initialize one token per permitted word and reinforce the drawn class."""
    counts = Counter(map(equal, words))
    def probability(i, j):
        first, second = equal(words[i]), equal(words[j])
        return sp.Rational(counts[second] + (first == second),
                           len(words) * (len(words) + 1) * counts[second])
    return sp.Matrix(len(words), len(words), probability)


def projector(basis):
    columns = sp.Matrix.hstack(*basis)
    return columns * (columns.T * columns).inv() * columns.T


def local_questions(words, kernel_sign=1):
    n = len(words)
    identity = sp.eye(n)
    toggles = []
    for bit in range(2):
        toggle = sp.zeros(n)
        for i, word in enumerate(words):
            moved = tuple(v ^ (pos == bit) for pos, v in enumerate(word))
            j = words.index(moved) if moved in words else i
            toggle[j, i] = 1
        toggles.append(toggle)

    summed = sum(toggles, sp.zeros(n))
    moves = summed - sp.diag(*summed.diagonal())
    change = sp.zeros(n)
    for value, _, basis in moves.eigenvects():
        sign = kernel_sign if value == 0 else sp.sign(value)
        change += sign * projector(basis)
    invariant = sp.Matrix.vstack(*(m - identity for m in toggles)).nullspace()
    reflection = 2 * projector(invariant) - identity
    equality = sp.diag(*(1 if equal(w) else -1 for w in words))
    a = [change, equality]
    b = [-equality * reflection * equality, reflection]
    for m in a + b:
        assert m == m.T and (m * m).applyfunc(sp.simplify) == identity
    return a, b, toggles, moves


def density(weights, coherent):
    probabilities = list(weights)
    assert sum(probabilities) == 1 and all(x > 0 for x in probabilities)
    if coherent:
        amplitudes = sp.Matrix([sp.sqrt(x) for x in probabilities])
        return amplitudes * amplitudes.T
    return sp.diag(*probabilities)


def setting_tables(state, a, b):
    """Born probabilities computed directly on the named fresh words."""
    identity = sp.eye(a[0].rows)
    tables = {}
    correlations = []
    for x, y in product(range(2), repeat=2):
        joint = sp.zeros(2)
        for i, j in product(range(2), repeat=2):
            left = (identity + (-1)**i * a[x]) / 2
            right = (identity + (-1)**j * b[y]) / 2
            observable = sp.kronecker_product(left, right)
            joint[i, j] = sp.simplify((state * observable).trace())
        assert sum(joint) == 1 and all(v >= 0 for v in joint)
        tables[x, y] = joint
        correlations.append(sp.simplify(joint[0, 0] + joint[1, 1] - joint[0, 1] - joint[1, 0]))
    for setting in range(2):
        assert (tables[setting, 0] - tables[setting, 1]) * sp.ones(2, 1) == sp.zeros(2, 1)
        assert sp.ones(1, 2) * (tables[0, setting] - tables[1, setting]) == sp.zeros(1, 2)
    score = sp.simplify(sum(correlations[:3]) - correlations[3])
    return tables, score


def encoded_sibling(words):
    # Columns give equal amplitudes over words in each class.
    classes = [True, False]
    return sp.Matrix([[sp.sympify(int(equal(w) == k)) / sp.sqrt(sum(equal(v) == k for v in words))
                       for k in classes] for w in words])


def as_rows(matrix):
    return [[str(v) for v in row] for row in matrix.tolist()]


def study(pilot):
    words = [w for w in product(range(2), repeat=2) if len(set((0, *w))) > 1]
    positive = orbit_weights(words)
    a, b, toggles, moves = local_questions(words)
    coherent = density(positive, True)
    if pilot:
        return {'words': words, 'joint_weight': as_rows(positive),
                'first_correlation': str(sp.simplify((coherent * sp.kronecker_product(a[0], b[0])).trace()))}

    marginal = positive * sp.ones(len(words), 1)
    independent = marginal * marginal.T
    reinforced = reinforced_weights(words)
    assert reinforced * sp.ones(len(words), 1) == sp.ones(len(words), 1) / 3
    preparations = {'coherent': coherent, 'mixture': density(positive, False),
                    'matched_independent_coherent': density(independent, True),
                    'ordinary_marginal_reinforced_coherent': density(reinforced, True)}
    amplitudes = positive.applyfunc(sp.sqrt)
    preparations['product_of_actual_local_states'] = sp.kronecker_product(
        amplitudes * amplitudes.T, amplitudes.T * amplitudes)
    pair_classes = [tuple(map(equal, pair)) for pair in product(words, repeat=2)]
    preparations['class_dephased'] = sp.Matrix(coherent.rows, coherent.cols, lambda i, j:
        coherent[i, j] if pair_classes[i] == pair_classes[j] else 0)
    encoded = encoded_sibling(words)
    pair_encoding = sp.kronecker_product(encoded, encoded)
    encoded_a, encoded_b = [[(encoded.T * m * encoded).applyfunc(sp.simplify) for m in reads]
                            for reads in [a, b]]
    outcomes, scores = {}, {}
    for name, state in preparations.items():
        tables, score = setting_tables(state, a, b)
        scores[name] = score
        outcomes[name] = {'score': str(score), 'score_decimal': float(score),
                          'tables': {f'{x}{y}': as_rows(v) for (x, y), v in tables.items()}}
        # A diagonal state also has weight on the antisymmetric complement.
        if name != 'mixture':
            small = (pair_encoding.T * state * pair_encoding).applyfunc(sp.simplify)
            recovered = (pair_encoding * small * pair_encoding.T - state).applyfunc(sp.simplify)
            assert recovered == sp.zeros(len(words)**2)
            assert setting_tables(small, encoded_a, encoded_b) == (tables, score)

    reversed_a, reversed_b, _, _ = local_questions(words, kernel_sign=-1)
    # The unused kernel is empty in the coherent preparations. It is populated
    # by a mixture of named words, so its convention must also be checked there.
    kernel_scores = {}
    kernel_outcome_differences = {}
    for name, state in preparations.items():
        new_tables, new_score = setting_tables(state, reversed_a, reversed_b)
        kernel_scores[name] = str(new_score)
        changes = []
        for (x, y), table in new_tables.items():
            original = sp.Matrix(outcomes[name]['tables'][f'{x}{y}']).applyfunc(sp.sympify)
            changes.extend(abs(value) for value in (original - table))
        kernel_outcome_differences[name] = str(max(changes))
    assert kernel_scores['coherent'] == str(scores['coherent'])
    assert kernel_scores['mixture'] == str(scores['mixture'])
    replaced = [setting_tables(coherent, [toggle, a[1]], b)[1] for toggle in toggles]

    for permuted in permutations(words):
        permuted = list(permuted)
        transform = sp.Matrix([list(sp.eye(3).row(words.index(w))) for w in permuted])
        for ordered in [permuted, [tuple(1 - d for d in w) for w in permuted]]:
            new_a, new_b, _, _ = local_questions(ordered)
            assert new_a + new_b == [transform * m * transform.T for m in a + b]
            assert orbit_weights(ordered) == transform * positive * transform.T

    visibility = {name: sp.simplify((2 - scores[name]) / (scores['coherent'] - scores[name]))
                  for name in ['mixture', 'class_dephased']}
    assert scores['coherent'] > 2 and scores['ordinary_marginal_reinforced_coherent'] < 2
    assert replaced == [2, 2] and all(0 < threshold < 1 for threshold in visibility.values())
    return {'words': words, 'joint_weight': as_rows(positive), 'move_matrix': as_rows(moves),
            'encoded_reads': {'alice': list(map(as_rows, encoded_a)), 'bob': list(map(as_rows, encoded_b))},
            'outcomes': outcomes, 'threshold_fraction_coherent': {k: str(v) for k, v in visibility.items()},
            'opposite_zero_mode_scores': kernel_scores, 'one_toggle_in_place_of_change': list(map(str, replaced)),
            'opposite_zero_mode_max_probability_difference': kernel_outcome_differences,
            'local_name_permutations': 6, 'founder_complements_checked': 2}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pilot', action='store_true')
    print(json.dumps(study(parser.parse_args().pilot), indent=2))
