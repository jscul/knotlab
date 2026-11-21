"""Check the clean three-word experiment without using the B287 implementation.

P exchanges a and b, Q exchanges a and c, and R exchanges b and c.
Their ordinary actions really are exchanges of two names on a ternary knot.
All amplitude controls in this file are explicit mathematical additions.
"""
from fractions import Fraction
from itertools import permutations, product

import sympy as sp


def test_ordinary():
    def swap(word, first, second):
        bits = list(word)
        bits[first], bits[second] = bits[second], bits[first]
        return tuple(bits)

    for law in ("parity", "nae"):
        words = [w for w in product((0, 1), repeat=3)
                 if (sum(w) % 2 == 0 if law == "parity" else len(set(w)) == 2)]
        for first, second, third in permutations(range(3)):
            for word in words:
                v = swap(word, first, second)
                v = swap(v, first, third)
                v = swap(v, first, second)
                assert v == swap(word, second, third) and v in words
        print(law, "accepted complete ternary words", len(words))


def pulse(size, left, right, idle, ordered_phase=1, inverse=False):
    """Moving block in a chosen frame. ordered_phase is the phase for left→right."""
    phase = -sp.I if inverse else sp.I
    result = sp.eye(size) / idle if inverse else sp.eye(size) * idle
    for index in (left, right):
        result[index, index] = 1 / sp.sqrt(2)
    result[right, left] = phase * ordered_phase / sp.sqrt(2)
    result[left, right] = phase / (sp.sqrt(2) * ordered_phase)
    return result


def completed(left, right, size, idle):
    result = sp.eye(size) * idle
    result[left, left] = result[right, right] = 0
    result[left, right] = result[right, left] = 1
    return result


def assert_equal(first, second):
    assert all(sp.simplify(v) == 0 for v in first - second)


def check_composition():
    x, y, z = sp.symbols("x y z", nonzero=True)
    # Full exchanges normalized to unit amplitude on the moving pair,
    # with independent idle phases. Read the multiplier on each input word.
    for size in (3, 4):
        p, q, r = (completed(i, j, size, t) for i, j, t in
                   ((0, 1, x), (0, 2, y), (1, 2, z)))
        comparison = r.inv() * p * q * p
        wanted = [y/z, x, x] + ([x**2*y/z] if size == 4 else [])
        assert_equal(comparison, sp.diag(*wanted))
        shared = comparison.subs({y: x, z: x})
        assert_equal(shared, sp.diag(1, x, x, *([x**2] if size == 4 else [])))
        assert_equal(p*p, sp.diag(1, 1, *([x**2] * (size-2))))
        for labels in product((1, -1), repeat=size):
            frame = sp.diag(*labels)
            for a, b in ((0, 1), (0, 2), (1, 2)):
                sign = labels[a]*labels[b]
                assert_equal(completed(a, b, size, sign),
                             sign * frame * completed(a, b, size, 1) * frame)
    print("Direct/indirect full exchange fixes the normalized shared idle factor to 1.")
    print("If phases are address-dependent the separate sign frames survive.")


def check_ports():
    u, p, q, r, alpha, beta = sp.symbols("u p q r alpha beta", nonzero=True)
    size = 3
    ket = sp.eye(size)[:, 0]
    offer = pulse(size, 0, 1, u, p)
    inverse_offer = pulse(size, 0, 1, u, p, inverse=True)
    assert_equal(inverse_offer * offer, sp.eye(size))
    unsigned_compensation = completed(0, 1, size, 1) * pulse(size, 0, 1, u)**2
    assert_equal(unsigned_compensation, sp.diag(sp.I, sp.I, u**2))
    split = pulse(size, 0, 2, u, q)
    undo_split = pulse(size, 0, 2, u, q, inverse=True)
    direct_recombine = pulse(size, 1, 2, u, r, inverse=True)
    # Four forward pulses already return every ordinary word, without any
    # additional full swap. The same splitter and its inverse cancel q.
    four = undo_split * offer**4 * split * ket
    assert_equal(four, sp.Matrix([(u**4-1)/2, 0, sp.I*q*(u**4+1)/2]))
    out = direct_recombine * offer**2 * split * ket
    assert_equal(out, sp.Matrix([0, (sp.I*p + q*u**2/r)/2,
                                  (r*p + sp.I*q*u**2)/2]))
    # Allow a full swap whose moving sector phase is alpha, fixed sector beta.
    full = sp.Matrix([[0, alpha, 0], [alpha, 0, 0], [0, 0, beta]])
    compensated = undo_split * full.inv() * offer**2 * split * ket
    assert_equal(compensated, sp.Matrix([(sp.I*p/alpha + u**2/beta)/2, 0,
                                         q*(p/alpha + sp.I*u**2/beta)/2]))
    # The elementary return has a third possible ordinary word.
    single = undo_split * offer * split * ket
    assert_equal(single, sp.Matrix([1/(2*sp.sqrt(2))+u/2, sp.I*p/(2*u),
                                    sp.I*q*(u/2-1/(2*sp.sqrt(2)))]))
    phases = [1, (1+sp.I)/sp.sqrt(2), -(1+sp.I)/sp.sqrt(2)]
    for choice, expected_return, single_return in zip(
            phases, (Fraction(1, 2), 1, 1), (None, Fraction(5, 8), Fraction(1, 8))):
        settings = {u:choice, p:1, q:1, r:1, alpha:1, beta:1}
        for vector, port in ((out, 1), (compensated, 0)):
            v = vector.subs(settings)
            assert_equal(v.H*v, sp.eye(1))
            assert sp.simplify(sp.Abs(v[port])**2 - expected_return) == 0
        if single_return is not None:
            prob = sp.Abs(single.subs(settings)[0])**2
            assert sp.simplify(prob-single_return) == 0
            # Words a and b both drive 011 on the fully connected two-bit keeper.
            other = sp.Abs(single.subs(settings)[1])**2
            assert sp.simplify(other - Fraction(1, 4)) == 0
            assert sp.simplify(prob + other - (single_return + Fraction(1, 4))) == 0
    # The signed full swaps remain an ordinary group representation. Their frame
    # can change a compensated result while the bypass result stays the same.
    sign_change = {u:phases[1], p:1, q:1, r:1, alpha:-1, beta:1}
    assert sp.simplify(four[0].subs(u, 1)) == 0
    assert sp.simplify(sp.Abs(four[0].subs(u, phases[1]))**2) == 1
    assert sp.simplify(compensated.subs(sign_change)[0]) == 0
    assert sp.simplify(sp.Abs(out.subs(sign_change)[1])**2) == 1
    print("Two-pulse port 1/2 or 1 with aligned frames. One-pulse ports 5/8 and 1/8.")


if __name__ == "__main__":
    test_ordinary()
    check_composition()
    check_ports()
