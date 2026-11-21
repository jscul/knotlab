"""Independent finite word and density checks for the split-knot meter.

Run from the study root with Python 3. No third-party packages are needed.
"""
from collections import Counter
from fractions import Fraction
from itertools import product


def parity(word):
    return sum(word) % 2 == 0


def nae(word):
    return len(set(word)) == 2


def assert_meter(rows, total, expected):
    """Trace over the final source by grouping equal residual ordinary words."""
    meter = Counter()
    for source, a, b in rows:
        for other, c, d in rows:
            if source == other:
                meter[((a, b), (c, d))] += Fraction(1, total)
    for a, b, c, d in product(range(2), repeat=4):
        x, y = (a, b), (c, d)
        assert meter[x, y] == (expected / 2 if a == b and c == d else 0)
    return meter


def jointly_cleared_parity(words):
    rows = []
    for a, c, b in words:
        p = a ^ c
        # Both readers copy to private registers without changing the source.
        move_a = (a ^ p, c, b)
        move_b = (a, c, b ^ b)
        joined = (a ^ p, c, b ^ b)
        assert all(w == (a, c, b) or not parity(w) for w in (move_a, move_b))
        assert parity(joined) and p == b
        rows.append((joined, p, b))
    assert_meter(rows, len(words), Fraction(1))


def reached_nae(words):
    rows = []
    for a, c, b in words:
        if a != c:
            continue  # The common filter's explicit refusal, before any target interaction.
        private_a = a
        clear_first = (a, c ^ (private_a == 0), b)
        clear_second = (clear_first[0] ^ (private_a == 1), clear_first[1], b)
        assert nae(clear_first) and nae(clear_second) and clear_second[:2] == (0, 1)
        private_b = b
        cleared = clear_second[:2] + (b ^ private_b,)
        assert nae(cleared)
        rows.append((cleared, private_a, private_b ^ 1))
    chance = Fraction(len(rows), len(words))
    assert chance == Fraction(1, 3)
    assert_meter(rows, len(words), chance)
    marked = [(residual + (a,), a, b) for residual, a, b in rows]
    # Keeping a which-row tag eliminates both off-diagonal terms.
    assert sum(x[0] == y[0] and x[1:] != y[1:] for x in marked for y in marked) == 0
    return chance


def source_gram(words):
    rows = {w[:2] for w in words}
    return [[sum((a, c, b) in words and (a, c, d) in words for a, c in rows)
             for d in range(2)] for b in range(2)]


def product_probe(p):
    # The second path applies J at the first reader and minus J at the second.
    # On input 00 its contribution is minus 11.
    # Each local analyzer has signs + and -, hence four fine records.
    branches = {}
    for u, v in product(range(2), repeat=2):
        t = (-1) ** (u + v)
        vertices = {(0, 0): 1, (1, 1): -t}
        branch = {(i, j): Fraction(p, 8) * a * b
                  for i, a in vertices.items() for j, b in vertices.items()}
        assert branch[(0, 0), (1, 1)] == -t * p / 8
        assert sum(val for (i, j), val in branch.items() if i == j) == p / 4
        branches[u, v] = branch
    return branches


def main():
    words = tuple(product(range(2), repeat=3))
    even = {w for w in words if parity(w)}
    six = {w for w in words if nae(w)}
    assert source_gram(even) == [[2, 0], [0, 2]]
    assert source_gram(six) == [[3, 2], [2, 3]]
    by_b = [{w[:2] for w in six if w[2] == b} for b in range(2)]
    assert by_b[0] - by_b[1] == {(1, 1)}
    assert by_b[1] - by_b[0] == {(0, 0)}
    assert by_b[0] & by_b[1] == {(0, 1), (1, 0)}
    for u, v in product(even, repeat=2):
        if u[:2] == v[:2] or u[2] == v[2]:
            assert u[2] == v[2] and (u[0] ^ u[1]) == (v[0] ^ v[1])
    jointly_cleared_parity(even)
    chance = reached_nae(six)
    for p in (Fraction(1), chance):
        assert len(product_probe(p)) == 4
    # Two independent supplied sources, with only yes/no heralds recorded.
    flags = Counter((u[0] == u[1], v[0] == v[1]) for u, v in product(six, repeat=2))
    assert flags == {(True, True): 4, (False, True): 8, (True, False): 8, (False, False): 16}
    print("4 parity words: both single-reader moves preserve the parity sector.")
    print("4/4 joined resets stay lawful; either half alone fails on 2/4 words.")
    print("6 not-all-equal words: 2/6 coherent successes, 4/6 refusals.")
    print("Normalized source eigenvalues: parity 1/2,1/2; not-all-equal 5/6,1/6.")
    print("On 00 each of four sign records weighs 1/4 after a joined parity reset,")
    print("or 1/12 per original not-all-equal launch; the surviving off-diagonal sign agrees.")
    print("Two independent heralds: 4/36 both accept, 16/36 just one accepts, 16/36 neither accepts.")


if __name__ == "__main__":
    main()
