"""Compare closed-part counts with exact joint measurements on explicit states."""
import argparse
from collections import Counter
from fractions import Fraction
from itertools import combinations, product


def parity(n):
    return n.bit_count() % 2


def knots_of(holders, n):
    return [[i for i, pair in enumerate(holders) if v in pair] for v in range(n)]


def incompatible(holders):
    return {(i, j) for i, j in combinations(range(len(holders)), 2)
            if set(holders[i]).isdisjoint(holders[j])}


def operators(count, negative):
    # The ith value toggles bit i. Its sign records already occupied earlier
    # bits whose values anticommute with it. Every such map squares to +I.
    return [(1 << i, sum(1 << j for j in range(i) if (j, i) in negative))
            for i in range(count)]


def action(ops, word, basis):
    sign = 1
    for j in reversed(word):
        x, z = ops[j]
        if parity(z & basis):
            sign = -sign
        basis ^= x
    return basis, sign


def stabilised_state(ops, knots, closure_sign):
    # Apply the projectors I+K one by one to |0>, omitting common positive factors.
    state = {0: 1}
    for knot in knots[:-1]:
        enlarged = state.copy()
        for basis, value in state.items():
            other, sign = action(ops, knot, basis)
            enlarged[other] = enlarged.get(other, 0) + sign * value
        state = {b: a for b, a in enlarged.items() if a}
    assert state
    for knot, required in zip(knots, [1] * (len(knots) - 1) + [closure_sign]):
        for basis, value in state.items():
            other, sign = action(ops, knot, basis)
            assert sign * value == required * state.get(other, 0)
    return state


def probabilities(ops, state, read, limit=None):
    # Expand the product of the outcome projectors (I +/- O)/2.
    norm2 = sum(x*x for x in state.values())
    moments = []
    for subset in range(1 << len(read)):
        word = [v for i, v in enumerate(read) if subset >> i & 1]
        moment = 0
        for basis, value in state.items():
            other, sign = action(ops, word, basis)
            moment += value * sign * state.get(other, 0)
        moments.append(moment)
    values = []
    for w in range(min(limit or len(moments), len(moments))):
        numerator = sum((-1 if parity(s & w) else 1) * m for s, m in enumerate(moments))
        values.append(Fraction(numerator, len(moments) * norm2))
    return values


def two_closures(pilot):
    holders = list(combinations((0, 1, 2, 3), 2)) + list(combinations((0, 4, 5, 6), 2))
    knots = knots_of(holders, 7)
    negative = incompatible(holders)
    ops = operators(len(holders), negative)
    assert all(sum(tuple(sorted((i, j))) in negative for i in k for j in h) % 2 == 0
               for k, h in combinations(knots, 2))
    # All seven knots even, an allowed choice for this closure.
    state = stabilised_state(ops, knots, 1)
    read = knots[0]
    assert len(read) == 6 and [k for k in knots if set(k) <= set(read)] == [read]
    table = probabilities(ops, state, read, 8 if pilot else None)
    counts = Counter(table)
    classical = sum(parity(w) == 0 for w in range(len(table)))
    if not pilot:
        assert classical == 32 and counts == {Fraction(0): 48, Fraction(1, 16): 16}
        print("shared six:", classical, "closed-part words; probabilities", dict(counts))
        halves = {(parity(w & 7), parity(w >> 3)) for w, p in enumerate(table) if p}
        assert len(halves) == 1
        print("two triples in the shared knot, parity bits:", halves)


def eight_knots():
    holders = [(u, v) for u, v in combinations(range(8), 2) if (u ^ v).bit_count() == 1]
    knots = knots_of(holders, 8)
    # Three disjoint routes from 0 to 7. The interior of each supplies the
    # two-place holder in the 2-against-3 example. Copy the second value.
    role = {}
    for j, (a, b) in enumerate([(1, 3), (2, 6), (4, 5)]):
        role[(0, a)] = (0, j)
        role[(min(a, b), max(a, b))] = (1, j)
        role[(b, 7)] = (1, j)
    negative = set()
    for i, j in combinations(range(len(holders)), 2):
        a = role.get(holders[i])
        b = role.get(holders[j])
        if a and b and a[0] != b[0] and a[1] != b[1]:
            negative.add((i, j))
    assert negative <= incompatible(holders)
    ops = operators(len(holders), negative)
    state = stabilised_state(ops, knots, -1)
    for v, read in enumerate(knots):
        table = probabilities(ops, state, read)
        assert table == [Fraction(1, 4) if parity(w) == (v == 7) else 0 for w in range(8)]
    print("eight-knot R3 state: all 64 single-knot probabilities matched")


def reader_tables():
    # The first reader records (a_x,a'_x) and answers their XOR. The
    # second reader records and answers b_y. Test complete-record marginals.
    for odd in (True, False):
        first = {}
        second = {}
        corr = []
        for x, y in product((0, 1), repeat=2):
            legal = [(a, t, b) for a, t, b in product((0, 1), repeat=3)
                     if a ^ t ^ b == (x & y & odd)]
            left, right = Counter((a, t) for a, t, b in legal), Counter(b for a, t, b in legal)
            assert len(legal) == 4 and left == first.setdefault(x, left)
            assert right == second.setdefault(y, right)
            corr.append(sum(Fraction((-1) ** (a ^ t ^ b), 4) for a, t, b in legal))
        chsh = sum(corr[:3]) - corr[3]
        assert chsh == (4 if odd else 2)
        print("last sign", int(odd), "correlations", list(map(int, corr)), "CHSH", chsh)


def birth():
    knots = [{0, 1, 2}, {1, 3, 4}, {3, 0, 5}]
    for after in (False, True):
        if after:
            knots.append({2, 4, 5})
        neg = {(i, j) for i, j in combinations(range(6), 2)
               if not any({i, j} <= knot for knot in knots)}
        ops = operators(6, neg)
        triple = [2, 4, 5]
        assert all(action(ops, triple * 2, w) == (w, 1 if after else -1) for w in range(64))
        for a, b in combinations(map(sorted, knots[:3]), 2):
            left = action(ops, a + b, 0)
            right = action(ops, b + a, 0)
            assert left[0] == right[0] and left[1] * right[1] == (1 if after else -1)
        print("after birth" if after else "before birth", "triple squared", 1 if after else -1)


def central_products():
    holders = list(combinations(range(5), 2))
    ops = operators(len(holders), incompatible(holders))
    knots = knots_of(holders, 5)
    for knot in knots:
        for d in range(len(holders)):
            # The two orders of the same factors differ only by a scalar sign.
            assert action(ops, knot + [d], 0) == action(ops, [d] + knot, 0)
        assert action(ops, knot, 0)[0] != 0
    stabilised_state(ops, knots, -1)
    print("five central knot products; zero scalar knot products in the full representation")


def rational_chsh():
    # On (|00>+|11>)/sqrt(2) the correlator is tr(A^T B)/2.
    # The coordinate pair below gives the coefficients of Z and X.
    readers = ((1, 0), (0, 1)), ((Fraction(4, 5), Fraction(3, 5)),
                                  (Fraction(4, 5), Fraction(-3, 5)))
    correlators = []
    for a, b in product(*readers):
        assert sum(t*t for t in a) == sum(t*t for t in b) == 1
        e = sum(s*t for s, t in zip(a, b))
        weights = [(1 + u*v*e) / 4 for u, v in product((-1, 1), repeat=2)]
        assert all((20*w).denominator == 1 and w >= 0 for w in weights)
        assert sum(weights) == 1
        correlators.append(e)
    score = sum(correlators[:3]) - correlators[3]
    assert score == Fraction(14, 5) and 4 < score**2 < 8
    print("equal-amplitude stabiliser state; rational setting counts out of 20; CHSH", score)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pilot", action="store_true")
    args = parser.parse_args()
    two_closures(args.pilot)
    if not args.pilot:
        eight_knots()
        reader_tables()
        birth()
        central_products()
        rational_chsh()
