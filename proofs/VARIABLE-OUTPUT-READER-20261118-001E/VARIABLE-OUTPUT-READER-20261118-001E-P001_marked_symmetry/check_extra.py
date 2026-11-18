"""Check the cographic exclusion, a noncographic control and two exact ternary readings."""

from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
SOURCE = (HERE.parents[1] / "VARIABLE-OUTPUT-READER-20261118-001D" /
          "VARIABLE-OUTPUT-READER-20261118-001D-P001_separator_inverse" / "active_part.json")
SOURCE_SHA = "48a711f1fa5b6eca0aa05d47eba9011bb129af985f29f8fd3ea959981ee09ed3"


def mask(values):
    return sum(1 << value for value in values)


def indices(word):
    while word:
        low = word & -word
        yield low.bit_length() - 1
        word ^= low


def minima(bonds, k):
    result = {}
    for word in sorted(bonds, key=int.bit_count):
        size = word.bit_count()
        for group in combinations(indices(word), k):
            result.setdefault(group, size)
    return result


def fano_minor():
    # Coordinate contractions are literal projection because the contracted
    # elements are independent unit columns. Check the relevant arities.
    for r in (4, 5, 6):
        ones = (1 << r) - 1
        columns = [(1 << i, ones ^ (1 << i)) for i in range(r)]
        eight = {value & 15 for pair in columns[:4] for value in pair}
        assert eight == {x for x in range(16) if x.bit_count() % 2}
        seven = {value & 7 for value in eight - {8}}
        assert seven == set(range(1, 8))
    dual_circuits = [
        mask(i for i in range(1, 8) if (i & form).bit_count() % 2)
        for form in range(1, 8)
    ]
    assert all(word.bit_count() == 4 for word in dual_circuits)
    assert len(minima(dual_circuits, 2)) == 21
    edges = tuple(combinations(range(5), 2))
    triangles = [mask(edges.index(pair) for pair in combinations(triple, 2))
                 for triple in combinations(range(5), 3)]
    maximum = max(word.bit_count() for word in range(1 << len(edges))
                  if not any(word & triangle == triangle for triangle in triangles))
    assert maximum == 6

    points = sorted(eight)
    circuits = []
    for length in range(1, 9):
        for subset in combinations(range(8), length):
            word = mask(subset)
            total = 0
            for i in subset:
                total ^= points[i]
            if not total and not any(old & word == old for old in circuits):
                circuits.append(word)
    assert set(minima(circuits, 2).values()) == {4}
    triples = minima(circuits, 3)
    assert len(triples) == 56 and set(triples.values()) == {4}
    first = circuits[0]
    inside = next(indices(first))
    outside = next(indices(255 ^ first))
    assert first ^ (1 << inside) ^ (1 << outside) not in circuits
    return {"four_bit_circuits_in_binary_control": len(circuits),
            "five_vertex_triangle_free_maximum": maximum}


def criterion_on_complete_graphs():
    counts = {}
    for n in (5, 6):
        edges = tuple(combinations(range(n), 2))
        # Every nonempty shore avoiding the final vertex and its complement
        # are both complete connected graphs, so every such cut is a bond.
        bonds = {mask(i for i, (u, v) in enumerate(edges)
                      if ((shore >> u) ^ (shore >> v)) & 1)
                 for shore in range(1, 1 << (n - 1))}
        for r in (4, 5, 6):
            table = minima(bonds, r - 1)
            reconstructed = {mask(group) for group in combinations(range(len(edges)), r)
                             if all(table.get(small) == r for small in combinations(group, r - 1))}
            assert reconstructed == {word for word in bonds if word.bit_count() == r}
            counts[(n, r)] = len(reconstructed)
    assert all(any(counts[(n, r)] for n in (5, 6)) for r in (4, 5, 6))
    return counts


def connected(side, neighbors):
    reached = side & -side
    frontier = reached
    while frontier:
        low = frontier & -frontier
        fresh = neighbors[low.bit_length() - 1] & side & ~reached
        reached |= fresh
        frontier = (frontier ^ low) | fresh
    return reached == side


def six_set_shortcut_control():
    # The complete tripartite graph with two vertices in each class.
    parts = ({0, 3}, {1, 4}, {2, 5})
    edges = [pair for pair in combinations(range(6), 2)
             if not any(set(pair) <= part for part in parts)]
    selected = {tuple(sorted(pair)) for pair in
                ((0, 1), (1, 3), (3, 2), (2, 4), (4, 5), (5, 0))}
    group = tuple(i for i, pair in enumerate(edges) if pair in selected)
    assert len(group) == 6
    neighbors = [0] * 6
    for u, v in edges:
        neighbors[u] |= 1 << v
        neighbors[v] |= 1 << u
    all_cuts = {}
    for side in range(1, 32):
        word = mask(i for i, (u, v) in enumerate(edges) if ((side >> u) ^ (side >> v)) & 1)
        all_cuts[word] = connected(side, neighbors) and connected(side ^ 63, neighbors)
    assert mask(group) not in all_cuts
    table = minima([word for word, bond in all_cuts.items() if bond], 3)
    assert all(table[triple] == 6 for triple in combinations(group, 3))
    return len(tuple(combinations(group, 3)))


def parity_control(stars, expected_changes):
    width = 1 + max(map(max, stars))
    outside = len(stars)
    neighbors = [0] * (outside + 1)
    for bit in range(width):
        holders = [u for u, star in enumerate(stars) if bit in star]
        if len(holders) == 1:
            holders.append(outside)
        u, v = holders
        neighbors[u] |= 1 << v
        neighbors[v] |= 1 << u
    rows = list(map(mask, stars))
    span = [0] * (1 << outside)
    bonds = []
    full = (1 << (outside + 1)) - 1
    for side in range(1, len(span)):
        low = side & -side
        span[side] = span[side ^ low] ^ rows[low.bit_length() - 1]
        if connected(side, neighbors) and connected(full ^ side, neighbors):
            bonds.append(span[side])

    def swap(bit):
        return 27 - bit if bit in (13, 14) else bit

    word_set = set(span)
    changes = [sum(mask(swap(i) for i in indices(word)) not in word_set
                   for word in span if word.bit_count() == k) for k in (3, 4, 5, 6)]
    assert changes == [0, 0, 0, 3]
    for k in (2, 3):
        table = minima(bonds, k)
        moved = sum(table.get(group) != table.get(tuple(sorted(map(swap, group))))
                    for group in combinations(range(width), k))
        assert moved == (0 if k == 2 else expected_changes)
    assert (table[4, 11, 13], table[4, 11, 14]) == (10, 8)
    return {"width": width, "bonds": len(bonds), "changed_ternary_entries": expected_changes,
            "changed_parity_answers_by_size_3_to_6_on_true_words": changes}


if __name__ == "__main__":
    assert sha256(SOURCE.read_bytes()).hexdigest() == SOURCE_SHA
    sources = json.loads(SOURCE.read_text())
    print("Fano exclusion and binary countercontrol", fano_minor())
    print("Recovered bonds by (complete graph order, bond size)", criterion_on_complete_graphs())
    print("Correct-size triple minima in the false six-set", six_set_shortcut_control())
    print(parity_control(sources["source_supports"], 56))
    print(parity_control(sources["completions"][0]["junction_supports"], 200))
