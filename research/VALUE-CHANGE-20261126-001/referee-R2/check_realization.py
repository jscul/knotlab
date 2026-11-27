"""Check the saved physical tables with ordinary real four-by-four projectors.

For a middle record m, the state used here has amplitudes D[u,u]/2 on |u,u>.
The computation uses neither the study's code nor the physical-table builder.
"""
import argparse
from itertools import product
import json
from pathlib import Path


def multiply(a, b):
    return [[sum(left * right for left, right in zip(row, column))
             for column in zip(*b)] for row in a]


def pauli(x, z, sign=0):
    return [[(1 - 2 * ((sign + (z & v).bit_count()) % 2)) if u == (v ^ x) else 0
             for v in range(4)] for u in range(4)]


def projectors(line):
    # Return eight times each projector using all three recorded answers.
    result = []
    for answers in range(8):
        p = pauli(0, 0)
        for j, read in enumerate(line):
            s = 1 - 2 * ((answers >> j) & 1)
            factor = [[int(u == v) + s * read[u][v] for v in range(4)] for u in range(4)]
            p = multiply(p, factor)
        assert all(p[u][v] == p[v][u] for u, v in product(range(4), repeat=2))
        result.append(p)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pilot", action="store_true", help="Check the first setting only")
    args = parser.parse_args()
    data = json.loads(Path(__file__).with_name("tables.json").read_text())
    square = [[pauli(1, 0), pauli(2, 0), pauli(3, 0)],
              [pauli(0, 2), pauli(0, 1), pauli(0, 3)],
              [pauli(1, 2), pauli(2, 1), pauli(3, 3, 1)]]
    assert data["middle_distinctions_least_significant_first"] == [49, 50, 55, 56, 61, 62]
    # Flipping both middle distinctions of each direct link preserves every
    # law. Conversely, the connecting knot laws require a change confined to
    # the middle to flip both distinctions or neither on each link. These
    # three pair-flips therefore exhaust the middle-only change certainties.
    supported = {3 * p + 12 * q + 48 * r for p, q, r in product(range(2), repeat=3)}
    entries = data["settings"][:1] if args.pilot else data["settings"]
    settings = {(entry["row"], entry["column"]) for entry in entries}
    assert settings == ({(0, 0)} if args.pilot else set(product(range(3), repeat=2)))
    checked = 0
    for entry in entries:
        i, j = entry["row"], entry["column"]
        rows = projectors(square[i])
        cols = projectors([row[j] for row in square])
        by_middle = entry["by_middle_record"]
        assert set(map(int, by_middle)) == supported
        raw_total = [[0] * 8 for _ in range(8)]
        corrected_total = [[0] * 8 for _ in range(8)]
        for m in range(64):
            if m not in supported:
                checked += 64
                continue
            p, q, r = (m >> k & 1 for k in (0, 2, 4))
            h = (p ^ q ^ r) + 2 * r
            d = [1 - 2 * ((u & h).bit_count() % 2) for u in range(4)]
            given = by_middle[str(m)]
            assert given["conditional_denominator"] * 8 == entry["joint_denominator"] == 4096
            for a, b in product(range(8), repeat=2):
                # tr(P_a^T D P_b D)/4. Each stored projector is scaled by 8.
                numerator = sum(rows[a][u][v] * cols[b][u][v] * d[u] * d[v]
                                for u, v in product(range(4), repeat=2))
                corrected = sum(rows[a][u][v] * cols[b][u][v]
                                for u, v in product(range(4), repeat=2))
                assert given["raw"][a][b] == 2 * numerator
                assert given["corrected"][a][b] == 2 * corrected
                raw_total[a][b] += 2 * numerator
                corrected_total[a][b] += 2 * corrected
                checked += 1
        assert raw_total == entry["raw_unsorted"]
        assert corrected_total == entry["corrected_unsorted"]
    print(f"Matched {checked} joint entries, including zeros, and both pooled tables at every tested setting.")


if __name__ == "__main__":
    main()
