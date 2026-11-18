"""Trace the changed distance-four pairs and locate the common junction at width 19."""

from collections import Counter
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path


HERE = Path(__file__).resolve()
PREVIOUS = HERE.parents[2] / "VARIABLE-OUTPUT-READER-20261118-001B"
WITNESS = PREVIOUS / "VARIABLE-OUTPUT-READER-20261118-001B-P001_width_nineteen" / "near_witness.json"
EXPECTED_SHA256 = "960ec63a1a23da44e6c70a489fd8bd27f6ab6152efe8a7599c47a72b2adb42da"
WIDTH = 19


def bit_names(mask):
    return tuple(i for i in range(WIDTH) if mask & (1 << i))


def minimum_bonds(checks):
    span = {0: ()}
    for i, junction in enumerate(checks):
        equation = sum(1 << bit for bit in junction)
        span.update({value ^ equation: (*indices, i) for value, indices in span.items()})
    assert len(span) == 1 << len(checks)
    minimal = []
    for word in sorted(span, key=lambda m: (m.bit_count(), m)):
        if word and all(word & smaller != smaller for smaller in minimal):
            minimal.append(word)
    entries = {}
    for i, j in combinations(range(WIDTH), 2):
        mask = (1 << i) | (1 << j)
        through = [m for m in minimal if m & mask == mask]
        length = min(m.bit_count() for m in through)
        entries[i, j] = (length - 1, [(bit_names(m), span[m]) for m in through
                                      if m.bit_count() == length])
    return entries


def adjacent_at_minimum(entries, i):
    distances = {j: entries[tuple(sorted((i, j)))][0] for j in range(WIDTH) if j != i}
    nearest = min(distances.values())
    return nearest, tuple(sorted((i, *(j for j, d in distances.items() if d == nearest))))


def analyze(side):
    checks = side["junction_supports"]
    marks = side["marked"]
    entries = minimum_bonds(checks)
    parents = [adjacent_at_minimum(entries, i)[1] for i in marks]
    assert parents == [tuple(checks[owner[0]]) for owner in side["owners"]]
    # These two unmarked rows have exactly four nearest partners, all at distance four.
    # Both recover the same five distinctions. Check the recovered support against incidence.
    visible = {i: group for i in range(WIDTH) if i not in marks
               for dist, group in (adjacent_at_minimum(entries, i),) if dist == 4 and len(group) == 5}
    assert len(visible) == 2 and set(visible.values()) == {tuple(checks[5])}
    witness = next(iter(visible.values()))
    touches = [tuple(sorted(set(parent) & set(witness))) for parent in parents]
    assert all(touches) == bool(side["neighbor_common_to_all_parents"])
    counts = Counter(d for d, _ in entries.values())
    assert counts[4] == side["bond_distance_histogram"]["4"]
    return entries, {"nearest_closed_groups_of_marks": parents, "two_unmarked_rows": sorted(visible),
                     "visible_five_distinction_support": witness, "intersection_with_each_parent": touches,
                     "pair_witnesses_in_incidence": side["pairwise_parent_common_neighbors"],
                     "all_parent_common_neighbors_in_incidence": side["neighbor_common_to_all_parents"],
                     "distance_four_pairs": counts[4]}


def run():
    data = WITNESS.read_bytes()
    assert sha256(data).hexdigest() == EXPECTED_SHA256
    prior = json.loads(data)
    first, legal = analyze(prior["legal_side"])
    second, forbidden = analyze(prior["forbidden_side"])
    mapping = prior["map_legal_to_forbidden"]
    marked = set(prior["legal_side"]["marked"])
    crossings = []
    same_marked = 0
    for pair, (d, old_witnesses) in first.items():
        image = tuple(sorted(mapping[i] for i in pair))
        e, new_witnesses = second[image]
        if marked.intersection(pair):
            assert d == e
            same_marked += 1
        if (d == 4) != (e == 4):
            which = old_witnesses if d == 4 else new_witnesses
            assert len(which) == 1 and which[0][1] == (5,)
            crossings.append({"legal_side_pair": pair, "forbidden_side_pair": image,
                              "distances": (d, e), "legal_side_shortest_bonds": old_witnesses,
                              "forbidden_side_shortest_bonds": new_witnesses})
    gains = sum(item["distances"][1] == 4 for item in crossings)
    assert (same_marked, gains, len(crossings) - gains) == (51, 4, 3)
    retained = (5, 6)
    mapped = tuple(sorted(mapping[i] for i in retained))
    d, old = first[retained]
    e, new = second[mapped]
    assert d == e == 4 and {indices for _, indices in old} == {(5,), (0, 1, 2)}
    assert {indices for _, indices in new} == {(0, 1, 2)}
    return {"input_sha256": sha256(data).hexdigest(), "legal": legal, "forbidden": forbidden,
            "marked_pairs_preserved": same_marked, "number_entering_distance_four": gains,
            "number_leaving_distance_four": len(crossings) - gains, "changes": crossings,
            "pair_retaining_another_five_distinction_bond": {
                "legal_side_pair": retained, "forbidden_side_pair": mapped,
                "legal_side_shortest_bonds": old, "forbidden_side_shortest_bonds": new}}


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, sort_keys=True))
