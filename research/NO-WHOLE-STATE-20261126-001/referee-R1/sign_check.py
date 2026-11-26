"""Test exact operator actions on basis words and count alternating occurrences."""
import argparse
import json
from itertools import combinations
from pathlib import Path

DATA = next((Path(__file__).resolve().parents[3] / "artifacts" /
             "FOUR-READINGS-20261120-001A").glob("*/census.json"))


def act(sequence, basis):
    """Act right to left with i^p X^x Z^z. Phases are powers of i."""
    phase = 0
    for p, x, z in reversed(sequence):
        phase += p + 2 * ((z & basis).bit_count() % 2)
        basis ^= x
    return phase % 4, basis


def check(knots, operators, scalar):
    # A Pauli word translates by a fixed mask and has an affine phase on bits.
    # Zero and the single-bit inputs therefore determine the full action.
    width = max(max(x, z).bit_length() for _, x, z in operators)
    basis = [0] + [1 << bit for bit in range(width)]
    for op in operators:
        assert all(act([op, op], word) == (0, word) for word in basis)
    word = sum(knots, [])
    spans = [[i for i, d in enumerate(word) if d == v] for v in range(len(operators))]
    alternating = 0
    unheld_failures = 0
    for a, b in combinations(range(len(operators)), 2):
        ab = act([operators[a], operators[b]], 0)
        ba = act([operators[b], operators[a]], 0)
        assert ab[1] == ba[1]
        if (ab[0] - ba[0]) % 4 == 2:
            unheld_failures += any(a in knot and b in knot for knot in knots)
            i, j = spans[a]
            k, ell = spans[b]
            alternating += i < k < j < ell or k < i < ell < j
        else:
            assert ab == ba
    assert unheld_failures == 0
    expanded = [operators[v] for v in word]
    assert all(act(expanded, w) == (2 * (alternating % 2), w) for w in basis)
    if not scalar:
        return alternating
    signs = []
    for knot in knots:
        factors = [operators[v] for v in knot]
        sign = act(factors, 0)[0]
        assert sign in (0, 2)
        assert all(act(factors, w) == (sign, w) for w in basis)
        signs.append(sign // 2)
    assert sum(signs) % 2 == alternating % 2 == 1
    return signs, alternating


def closure():
    knots = [[0, 1, 2], [1, 3, 4], [3, 0, 5], [2, 4, 5]]
    ops = [None] * 6
    for bit, (held, loose) in enumerate([(0, 4), (1, 5), (3, 2)]):
        mask = 1 << bit
        ops[held] = (1, mask, mask)  # Y
        ops[loose] = (0, mask, 0)    # X
    # Certify exactly R even on unheld pairs.
    for a, b in combinations(range(6), 2):
        same = act([ops[a], ops[b]], 0) == act([ops[b], ops[a]], 0)
        assert same == any(a in knot and b in knot for knot in knots)
    groups = [[ops[d] for d in k] for k in knots]
    for first, second in combinations(groups, 2):
        assert all(act(first + second, w) == act(second + first, w) for w in range(8))
    # Apply each knot to |000> - |111>.
    signs = []
    for group in groups:
        p, w = act(group, 0)
        q, v = act(group, 7)
        assert (w, v) == (7, 0) and p == q and p in (0, 2)
        signs.append(1 - p // 2)
    cost = check(knots, ops, scalar=False)
    assert signs == [0, 0, 0, 1] and cost == 1
    print("fixture: six commuting knot pairs, eigenvalue bits", signs, "interleavings", cost)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--limit", type=int)
    args = parser.parse_args()
    witnesses = [r for r in json.loads(DATA.read_text()) if r["pauli_i_phase_X_bits_Z_bits"]]
    rows = witnesses[:args.limit]
    for r in rows:
        knots = [[i for i, pair in enumerate(r["sharing"]) if k in pair] for k in range(r["n"])]
        signs, cost = check(knots, r["pauli_i_phase_X_bits_Z_bits"], scalar=True)
        if r["n"] == 5:
            print("five mutually meeting knots: eigenvalue bits", signs, "interleavings", cost)
    if args.limit is None:
        assert len(rows) == 115
    print("certificates", len(rows), "all involutions, held pairs commute, total sign odd")
    closure()


if __name__ == "__main__":
    main()
