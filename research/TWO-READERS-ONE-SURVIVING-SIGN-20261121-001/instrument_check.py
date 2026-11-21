"""Independent integer process check for the actual three-word controls and binary keeper meters."""
from fractions import Fraction
from itertools import product

import numpy as np


tensor = np.kron
outer = np.outer


def identity(n):
    return np.eye(n, dtype=np.int64)


def gram(matrix):
    vector = matrix.reshape(-1)
    return outer(vector, vector)


def check_ternary_reference():
    # All nine physical target addresses are present. Restrict inputs only via Q⊗Q below.
    one = identity(3)
    c = np.roll(one, 1, axis=0)
    swap = one[[1, 0, 2]]
    rotations = (one, c, c.T)
    g = tensor(c, c)
    nine = identity(9)
    q = 3 * one - np.ones((3, 3), dtype=np.int64)
    d = c - c.T
    raw_ports = (nine + g + g.T, nine - g, nine + g - 2 * g.T)
    port_norms = (9, 6, 18)
    assert np.array_equal(sum(18 * k.T @ k // n for k, n in zip(raw_ports, port_norms)), 18 * nine)
    r = np.array([1, -1, 0])
    s = np.array([1, 1, -2])
    raw_meter = raw_ports[0] @ tensor(r, r)
    assert np.array_equal(2 * raw_meter, 3 * tensor(r, r) + tensor(s, s))
    assert Fraction(int(raw_meter @ raw_meter), 9 * 4 * 4) == Fraction(1, 8)
    # Account for the fixed source transposition at B, then every physical turn at A.
    source = np.stack([tensor(turn, swap) @ raw_meter for turn in rotations])
    rho = sum(outer(v, v) for v in source)
    code = tensor(q, q)
    assert np.array_equal(2 * rho, 3 * (code - 3 * tensor(d, d)))
    for u, v in product(range(3), repeat=2):
        corrected = tensor(rotations[-u], rotations[v] @ swap) @ source[(u + v) % 3]
        assert np.array_equal(corrected, raw_meter)
    # Compute each complete data operation directly with both returned reference words retained
    # as Kraus indices. The hidden ternary choice is another independent Kraus index.
    nports = (1, 2, 2)
    for i, j in product(range(3), repeat=2):
        left, right = raw_ports[i].reshape(3, 3, 3, 3), raw_ports[j].reshape(3, 3, 3, 3)
        kraus = np.einsum("amci,bndj,rij->rmnabcd", left, right, source.reshape(3, 3, 3))
        matrices = kraus.reshape(27, 9, 9) @ code
        vectors = matrices.reshape(27, 81)
        actual = vectors.T @ vectors
        actual_den = 3 * 18 * port_norms[i] * port_norms[j] * 81
        sign = 1 if (i == 0) == (j == 0) else -1
        projected = code - 3 * sign * tensor(d, d)  # 18 P_t on the physical word space
        rotated = tensor(d, one) @ projected
        predicted = 3 * gram(projected) + gram(rotated)
        predicted_den = 6 * 18**2 * 2 * nports[i] * nports[j]
        assert np.array_equal(actual * predicted_den, predicted * actual_den)
    print("Nine three-port conditional data operations checked exactly on the physical word basis.")
    print("All nine pairs of distributed turn shares recover the unturned coherent reference.")


def check_coherent_meter():
    one = identity(2)
    x = one[[1, 0]]
    z = np.diag([1, -1])
    jmat = x @ z
    observable = -tensor(jmat, jmat)
    hadamard = np.array([[1, 1], [1, -1]])
    ctrl_x = np.block([[one, 0 * one], [0 * one, x]])
    lifted = tensor(one, hadamard)
    ctrl_z = lifted @ ctrl_x @ lifted // 2
    left, right = ctrl_x @ ctrl_z, ctrl_z @ ctrl_x
    assert np.array_equal(left[-2:, -2:], jmat)
    assert np.array_equal(right[-2:, -2:], -jmat)
    branches = {}
    for a, b in product(range(2), repeat=2):
        ka = (tensor(hadamard, one) @ left).reshape(2, 2, 2, 2)[a]
        kb = (tensor(hadamard, one) @ right).reshape(2, 2, 2, 2)[b]
        for tag in (1, -1):
            # 2√2 K_ab, for the two separately recorded source ports.
            raw = tensor(ka[:, 0, :], kb[:, 0, :]) + tag * tensor(ka[:, 1, :], kb[:, 1, :])
            sign = tag * (-1)**(a + b)
            assert np.array_equal(raw, identity(4) + sign * observable)
            branches[tag, a, b] = raw
    for tag1, tag2 in product((1, -1), repeat=2):
        for a, b, c, d in product(range(2), repeat=4):
            first, second = branches[tag1, a, b], branches[tag2, c, d]
            same = tag1 * (-1)**(a + b) == tag2 * (-1)**(c + d)
            assert np.array_equal(second @ first, 2 * first if same else 0 * first)
    target = identity(4)[:, 0]
    for t in (1, -1):
        two_p = identity(4) + t * observable
        pure = outer(two_p @ target, two_p @ target)  # twice normalized conditional state
        assert Fraction(int(pure[0, 0] + pure[3, 3]), 2) == 1
        # After the mixed-reference measurement the normalized state is P_t/2.
        assert Fraction(int(two_p[0, 0] + two_p[3, 3]), 4) == Fraction(1, 2)
        assert Fraction(int(np.trace(pure @ two_p)), 8) == Fraction(1, 2)
    print("Eight conditional coherent operators and all 64 pairs of repeat records checked.")
    print("On 00, the next ordinary values agree with probability 1 after the coherent read and 1/2 after the mixed read.")


if __name__ == "__main__":
    check_ternary_reference()
    check_coherent_meter()
