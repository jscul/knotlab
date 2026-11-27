"""Independent change-reader check using full named-word projectors and numerical eigenspaces."""

import argparse
import itertools
import json
import os
import resource
import time
from collections import Counter
from math import sqrt

for variable in ('OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ[variable] = '1'
cap = 512 * 1024 * 1024
resource.setrlimit(resource.RLIMIT_AS, (cap, cap))

import numpy as np


def permitted(old):
    return sorted((x for x in itertools.product((0, 1), repeat=2) if len(set((old,) + x)) > 1),
                  key=lambda x: (x[0] != x[1], x))


def encode(old, order):
    names = permitted(old)
    return [names[i] for i in order]


def operator_questions(words, null_sign):
    toggles = []
    for bit in range(2):
        t = np.zeros((3, 3))
        for i, w in enumerate(words):
            q = tuple((1 - v if j == bit else v) for j, v in enumerate(w))
            t[words.index(q) if q in words else i, i] = 1
        toggles.append(t)
    eye = np.eye(3)
    z = np.diag([1 if a == b else -1 for a, b in words])
    moves = toggles[0] + toggles[1]
    np.fill_diagonal(moves, 0)
    eigenvalues, v = np.linalg.eigh(moves)
    signs = np.where(np.abs(eigenvalues) < 1e-10, null_sign, np.sign(eigenvalues))
    x = (v * signs) @ v.T
    eig_error, vectors = np.linalg.eigh((eye - toggles[0]) + (eye - toggles[1]))
    common = vectors[:, np.abs(eig_error) < 1e-10]
    assert common.shape == (3, 1)
    reflection = 2 * common @ common.T - eye
    return (x, z), (-z @ reflection @ z, reflection), toggles


def states(old, a_words, b_words):
    # The third birth has the opposite founder input. Sum it out after
    # preparing it, before any reader setting is selected.
    c_words = permitted(1 - old)
    triples = list(itertools.product(a_words, b_words, c_words))
    equal = lambda a: a[0] == a[1]
    signature = lambda t: (int(equal(t[0])) + int(equal(t[1])), equal(t[2]))
    multiplicity = Counter(map(signature, triples))
    weights = np.array([1 / (len(multiplicity) * multiplicity[signature(t)]) for t in triples])
    amplitudes = np.sqrt(weights.reshape(9, 3))
    pure = amplitudes @ amplitudes.T
    dephased = np.diag(weights.reshape(9, 3).sum(axis=1))
    assert np.linalg.matrix_rank(pure, tol=1e-10) == 1
    rho4 = pure.reshape(3, 3, 3, 3)
    reduced_a, reduced_b = np.trace(rho4, axis1=1, axis2=3), np.trace(rho4, axis1=0, axis2=2)
    p_a, p_b = np.diag(reduced_a), np.diag(reduced_b)
    product_value = np.kron(np.sqrt(p_a), np.sqrt(p_b))
    modes = [(equal(a), equal(b)) for a, b in itertools.product(a_words, b_words)]
    encoded_dephased = pure * np.array([[x == y for y in modes] for x in modes])
    # Draw two E/M colors from an urn starting with one E, two M,
    # reinforcing the first color by one. Mixed words have two names each.
    reinforced = np.array([
        (1 if a else 2)/3 * ((1 if b else 2) + (a == b))/4
        / ((1 if a else 2) * (1 if b else 2)) for a, b in modes])
    alt = np.sqrt(reinforced)
    return {'coherent': pure, 'named_dephased': dephased, 'class_dephased': encoded_dephased,
            'product_same_values': np.outer(product_value, product_value),
            'product_full_local_states': np.kron(reduced_a, reduced_b),
            'reinforced_coherent': np.outer(alt, alt)}


def outcomes(rho, a, b):
    eye = np.eye(3)
    return [[float(np.trace(rho @ np.kron((eye + s*a)/2, (eye + t*b)/2)))
             for t in (1, -1)] for s in (1, -1)]


def score_tables(rho, first, second):
    tables = np.array([[outcomes(rho, a, b) for b in second] for a in first])
    assert np.all(tables > -1e-12) and np.allclose(tables.sum(axis=(2, 3)), 1)
    assert np.allclose(tables.sum(axis=3)[:, 0], tables.sum(axis=3)[:, 1])
    assert np.allclose(tables.sum(axis=2)[0, :], tables.sum(axis=2)[1, :])
    e = np.sum(tables * [[1, -1], [-1, 1]], axis=(2, 3))
    score = float(e[0, 0] + e[0, 1] + e[1, 0] - e[1, 1])
    return {'probabilities': tables.tolist(), 'correlations': e.tolist(), 'CHSH': score}


def one_fixture(old, a_order=(0, 1, 2), b_order=(0, 1, 2)):
    a_words = encode(old, a_order)
    b_words = encode(old, b_order)
    preparations = states(old, a_words, b_words)
    results = {}
    for sign in (-1, 1):
        first, _, _ = operator_questions(a_words, sign)
        _, second, _ = operator_questions(b_words, sign)
        results[str(sign)] = {name: score_tables(rho, first, second)
                              for name, rho in preparations.items()}
    return results


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--pilot', action='store_true')
    args = parser.parse_args()
    started = time.perf_counter()
    if args.pilot:
        w = permitted(0)
        first, second, _ = operator_questions(w, 1)
        rho = states(0, w, w)['coherent']
        results = {'pilot': True, 'first_setting_pair': outcomes(rho, first[0], second[0])}
    else:
        results = {'pilot': False, 'tables': one_fixture(0)}
        words = permitted(0)
        first, second, toggles = operator_questions(words, 1)
        rho = states(0, words, words)['coherent']
        results['one_toggle_replaces_Alice_change'] = [
            score_tables(rho, (t, first[1]), second)['CHSH'] for t in toggles]
        assert np.allclose(results['one_toggle_replaces_Alice_change'], [2, 2])
        quantum = (12 * sqrt(2) + 2) / 9
        predicted = {'coherent': quantum, 'named_dephased': 0, 'class_dephased': 2/9,
                     'product_same_values': 4 * sqrt(2) / 3,
                     'product_full_local_states': 32 * sqrt(2) / 27,
                     'reinforced_coherent': (4 * sqrt(2) * (1 + sqrt(3)) + 2) / 9}
        for report in results['tables'].values():
            for key, value in predicted.items():
                assert abs(report[key]['CHSH'] - value) < 1e-12
        reference = results['tables']
        largest_delta = 0
        for i, image in enumerate(itertools.permutations(range(3))):
            # Six basis orderings and the complement of the prepared founder
            # with independent orderings on the two local alphabets.
            other_order = tuple(reversed(image))
            trial = one_fixture(i % 2, image, other_order)
            for sign, modes in reference.items():
                for name, original in modes.items():
                    delta = np.abs(np.array(original['probabilities'])
                                   - trial[sign][name]['probabilities']).max()
                    largest_delta = max(largest_delta, float(delta))
        assert largest_delta < 1e-12
        results['six_reorderings_including_complement_max_probability_error'] = largest_delta
        results['coherent_fraction_to_exceed_two'] = {
            'named_dephased': 2 / quantum, 'class_dephased': (2 - 2/9) / (quantum - 2/9)}
        results['null_sign_max_probability_difference'] = {
            name: float(np.abs(np.array(reference['-1'][name]['probabilities'])
                               - reference['1'][name]['probabilities']).max())
            for name in reference['1']}
    results['seconds'] = time.perf_counter() - started
    results['peak_kib'] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    print(json.dumps(results, indent=2))


if __name__ == '__main__':
    main()
