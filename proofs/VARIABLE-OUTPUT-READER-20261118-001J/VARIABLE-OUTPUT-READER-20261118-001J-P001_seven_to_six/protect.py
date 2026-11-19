"""Verify the 21-, 33- and 45-bit histories and their clipped pair certificates."""

import argparse
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
from itertools import combinations
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
LITERAL = (
    HERE.parents[1]
    / "VARIABLE-OUTPUT-READER-20261118-001G"
    / "VARIABLE-OUTPUT-READER-20261118-001G-P001_two_three_fresh"
    / "six_check.py"
)
spec = spec_from_file_location("literal_wired_shores", LITERAL)
literal = module_from_spec(spec)
spec.loader.exec_module(literal)

STARS = (
    ("T", "Ta Tb Tc"),
    ("a", "Ta aU aA aB"),
    ("b", "Tb bU bA bC"),
    ("U", "aU bU Uc u0"),
    ("c", "Tc Uc cB cC"),
    ("A", "aA bA At A0"),
    ("B", "aB cB Bt B0"),
    ("C", "bC cC Ct C0"),
    ("t", "At Bt Ct f g"),
    ("X", "u0 A0 x0 x1 x2"),
    ("Y", "B0 C0 y0 y1 y2"),
    ("D", "f x0 d0 d1 d2"),
    ("E", "g y0 e0 e1 e2"),
    ("J", "d0 e0 j0 j1 j2"),
    ("M", "x1 j0 m0 m1 m2"),
    ("R", "d1 e1 r0 r1 r2"),
    ("N", "x2 r0 n0 n1 n2"),
)
FRONTIER = ("u0", "A0", "B0", "C0", "f", "g")


def equation_space(stars):
    words = {0}
    for star in stars:
        words |= {word ^ star for word in words}
    return words


def short_bonds_and_table(words, width):
    bonds = []
    table = [[7] * width for _ in range(width)]
    for weight in range(1, 7):
        for word in sorted(w for w in words if w.bit_count() == weight):
            if any(word & bond == bond for bond in bonds):
                continue
            bonds.append(word)
            for a, b in combinations(literal.bits(word), 2):
                table[a][b] = table[b][a] = min(table[a][b], weight)
    return set(bonds), table


def forcing_pair(star, table):
    degree = star.bit_count()
    for a, b in combinations(literal.bits(star), 2):
        if table[a][b] != degree:
            continue
        common = literal.mask(
            x for x in range(len(table))
            if x in (a, b) or (table[a][x] <= degree and table[b][x] <= degree)
        )
        if common == star:
            return a, b
    raise AssertionError(f"No pair forces star {star}")


def threshold_cliques(table, size):
    width = len(table)
    following = [
        literal.mask(j for j in range(i + 1, width) if table[i][j] <= size)
        for i in range(width)
    ]

    def extend(selected, available, needed):
        if not needed:
            yield selected
            return
        while available.bit_count() >= needed:
            first = available & -available
            available ^= first
            vertex = first.bit_length() - 1
            yield from extend(selected | first, available & following[vertex], needed - 1)

    yield from extend(0, (1 << width) - 1, size)


def screen_extra_words(words, table):
    record = {}
    for size in range(3, 7):
        possible = list(threshold_cliques(table, size))
        outsiders = [word for word in possible if word not in words]
        short = sorted((word for word in words if word.bit_count() < 2 * size), key=int.bit_count)
        survivors = [
            word for word in outsiders
            if not any((word ^ true_word).bit_count() < size for true_word in short)
        ]
        assert not survivors, (size, survivors)
        record[str(size)] = {
            "pairwise_close_sets": len(possible),
            "outside_true_space": len(outsiders),
            "no_shorter_translate": len(survivors),
        }
    return record


def outcome(site_count):
    sites = [(site, labels.split()) for site, labels in STARS[:site_count]]
    names = list(dict.fromkeys(bit for _, row in sites for bit in row))
    index = {name: i for i, name in enumerate(names)}
    history = tuple((site, tuple(index[bit] for bit in row)) for site, row in sites)
    literal.replay(history)
    holders, adjacent = literal.incidence(history)
    legal = literal.direct_triples(holders, adjacent)
    marked = sorted(sorted(names[i] for i in group) for group in legal)
    expected_marks = sorted(
        sorted(("e2", m, n)) for m in ("m0", "m1", "m2") for n in ("n0", "n1", "n2")
    ) if site_count == len(STARS) else []
    assert marked == expected_marks

    stars = [literal.mask(row) for _, row in history]
    words = equation_space(stars)
    assert len(words) == 1 << site_count
    bonds, table = short_bonds_and_table(words, len(names))
    physical_bonds = literal.wired_bonds(history, holders)
    assert bonds == {bond for bond in physical_bonds if bond.bit_count() <= 6}
    assert literal.mask(index[bit] for bit in FRONTIER) in bonds

    frontier_squares = {}
    for bit in FRONTIER:
        ends = holders[index[bit]]
        if len(ends) == 1:
            assert site_count == 9
            continue
        a, b = ends
        paths = [
            [a, c, d, b] for c in sorted(adjacent[a] - {b})
            for d in sorted((adjacent[c] & adjacent[b]) - {a})
        ]
        assert paths, (bit, ends)
        frontier_squares[bit] = paths[0]

    pairs = {
        site: [names[x] for x in forcing_pair(star, table)]
        for (site, _), star in zip(history, stars, strict=True)
    }
    return {
        "width": len(names),
        "sites": site_count,
        "all_bonds": len(physical_bonds),
        "bonds_through_six": len(bonds),
        "pairs_through_six": sum(table[a][b] <= 6 for a, b in combinations(range(len(names)), 2)),
        "frontier_square_bypasses": frontier_squares,
        "forcing_pairs": pairs,
        "candidate_screen": screen_extra_words(words, table),
        "legal_triples": marked,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="Write the verified record")
    args = parser.parse_args()
    result = {
        "literal_checker_sha256": sha256(LITERAL.read_bytes()).hexdigest(),
        "chronological_stars": {site: names.split() for site, names in STARS},
        "frontier": FRONTIER,
        "controls": [outcome(n) for n in (9, 13, 17)],
    }
    record = json.dumps(result, sort_keys=True, indent=2) + "\n"
    output = HERE / "protect.json"
    if args.write:
        output.write_text(record)
    else:
        assert output.read_text() == record
    print("Verified the 21-, 33- and 45-bit controls, with 0, 0 and 9 legal triples.")


if __name__ == "__main__":
    main()
