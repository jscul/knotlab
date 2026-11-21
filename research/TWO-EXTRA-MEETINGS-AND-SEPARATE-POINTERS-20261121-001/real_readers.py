"""Independent integer replay of the frozen real cyclic preparations and local reads."""

from fractions import Fraction
from itertools import product
import numpy as np


I = np.eye(3, dtype=int)
C = np.roll(I, 1, axis=0)
K = np.kron
J = C - C.T
Q = 3 * I - np.ones((3, 3), dtype=int)
I9 = np.eye(9, dtype=int)


def source(correlation):
    """36 times the joint density, in ordinary word order."""
    return K(Q, Q) - 3 * correlation * K(J, J)


def check_preparation():
    r = np.array([1, -1, 0])
    for sign, operation in ((-1, K(C, C)), (1, K(C, C.T))):
        v = (I9 + operation + operation @ operation) @ K(r, r)
        acceptance = Fraction(int(v @ v), 36)
        assert acceptance == Fraction(1, 2)
        rotations = [K(action, I) @ v for action in (I, C, C.T)]
        rotated = sum(np.outer(w, w) for w in rotations)
        assert np.array_equal(2 * rotated, 3 * source(sign))
        assert np.array_equal(np.diag(source(sign)), np.full(9, 4))
        print('source', sign, 'success per launch', acceptance / 4)
    assert np.array_equal(source(1) + source(-1), 2 * source(0))


def local_questions():
    words = np.eye(3, dtype=int)
    vectors = [*words, words[0]+words[1], words[0]+words[2], words[1]+words[2]]
    return [np.outer(v, v) for v in vectors]


def check_single_pair():
    questions = [K(a, b) for a in local_questions() for b in local_questions()]
    for test in questions:
        assert np.sum(test * source(1)) == np.sum(test * source(0)) == np.sum(test * source(-1))
    print('all', len(questions), 'spanning one-pair tests agree')
    plus = np.zeros(9, dtype=int)
    plus[[0, 4]] = 1
    minus = plus.copy()
    minus[4] = -1
    assert (plus ** 2 == minus ** 2).all()
    t = np.array([1, 1, 0])
    probabilities = [Fraction(int(K(t, t) @ v) ** 2, 8) for v in (plus, minus)]
    assert probabilities == [Fraction(1, 2), 0]
    print('both readers at the positive binary port, conditioned on its source sign:', probabilities)


def compare_with_reference(inverse_reference):
    # Local comparison on the target and reference. These are six times the effects.
    g = K(C, C.T if inverse_reference else C)
    marked = I9 + g + g.T
    remainder = 3 * I9 - marked
    ports = [2 * marked, remainder, remainder]
    for target, ref in product((-1, 0, 1), repeat=2):
        # (target A, target B, reference A, reference B) -> (A A, B B).
        joint = K(source(target), source(ref)).reshape((3,) * 8)
        joint = joint.transpose(0, 2, 1, 3, 4, 6, 5, 7).reshape(81, 81)
        probabilities = {}
        for i, j in product(range(3), repeat=2):
            raw = int(np.sum(joint * K(ports[i], ports[j])))
            p = Fraction(raw, 36 ** 3)
            # Reversing both local reference questions interchanges their marked charge tests.
            a, b = (1 if i == 0 else -1), (1 if j == 0 else -1)
            multiplicity = (1 if i == 0 else 2) * (1 if j == 0 else 2)
            expected = Fraction(1 + a * b * target * ref, 4 * multiplicity)
            assert p == expected
            probabilities[i, j] = p
        assert sum(probabilities.values()) == 1
        agreement = sum(p for (i, j), p in probabilities.items() if (i == 0) == (j == 0))
        print('inverse reference' if inverse_reference else 'forward reference', 'target', target, 'reference', ref, 'agreement of marked flags', agreement)


if __name__ == '__main__':
    check_preparation()
    check_single_pair()
    compare_with_reference(inverse_reference=False)
    compare_with_reference(inverse_reference=True)
