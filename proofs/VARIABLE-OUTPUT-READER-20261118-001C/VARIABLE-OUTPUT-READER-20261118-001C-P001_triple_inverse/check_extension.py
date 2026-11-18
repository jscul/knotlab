"""Check the two induction bases and the first unary extensions against full duals."""

from collections import Counter
from hashlib import sha256
from itertools import combinations, product
import json
from pathlib import Path

import check_gluing as bonds
from check_core import matrix_from_pairs, retained_part


HERE = Path(__file__).resolve().parent
WITNESS_SHA256 = "7685dbb6636b3611a6e8a1f090bba446365feeaad00f22437594bfa3b6fd93ca"


def extend(scopes, marks, table, anchor, count, width):
    owners, _ = bonds.incidence(scopes)
    assert len(owners[anchor]) == 1 and anchor not in marks
    hist = bonds.anchor_histogram(table, width, anchor)
    fresh = tuple(range(width, width + count))
    extended = (*scopes, (anchor, *fresh))
    bonds.replay(extended)
    assert bonds.marked_permission(extended, marks) == bonds.marked_permission(scopes, marks)
    after = bonds.scalar_table(bonds.minimal_dual(extended), width + count)
    assert all(after[pair] == value for pair, value in table.items())
    for x, y in product(range(width), fresh):
        expected = count if x == anchor else bonds.delta(table, x, anchor) + count - 1
        assert after[x, y] == expected
    assert all(after[pair] == count for pair in combinations(fresh, 2))
    increase = Counter(after.values())[4] - Counter(table.values())[4]
    assert increase == count * hist[5 - count]
    tip = bonds.anchor_histogram(after, width + count, fresh[0])
    assert (tip[2], tip[3]) == ((2, hist[2]) if count == 2 else (0, 3))
    return after, (hist[2], hist[3]), (tip[2], tip[3]), increase


def run():
    raw = (HERE / "witness.json").read_bytes()
    assert sha256(raw).hexdigest() == WITNESS_SHA256
    records = {}
    for fixture in json.loads(raw).values():
        if not isinstance(fixture, dict):
            continue
        width = fixture["width"]
        sides = (fixture["legal_side"], fixture["forbidden_side"])
        marks = tuple(tuple(side["marked"]) for side in sides)
        scopes = tuple(tuple(map(tuple, side["checks"])) for side in sides)
        before = tuple(bonds.scalar_table(bonds.minimal_dual(stars), width) for stars in scopes)
        kept = [retained_part(matrix_from_pairs(table, width), t)
                for table, t in zip(before, marks, strict=True)]
        assert kept[0] == kept[1] == tuple(range(16))
        mapping = tuple(fixture["label_map"])
        assert mapping[18] == 18
        assert tuple(bonds.marked_permission(stars, t)["legal_triple"]
                     for stars, t in zip(scopes, marks, strict=True)) == (True, False)
        steps = {}
        for k in (2, 3):
            names = (*mapping, *range(width, width + k))
            tests = [extend(stars, t, matrix, 18, k, width)
                     for stars, t, matrix in zip(scopes, marks, before, strict=True)]
            (left, *left_stats), (right, *right_stats) = tests
            assert left_stats == right_stats and left_stats[0] == (0, 3)
            incident = [pair for pair in combinations(range(width + k), 2)
                        if any(x in pair for x in marks[0])]
            assert all(left[a, b] == bonds.delta(right, names[a], names[b]) for a, b in incident)
            assert all(retained_part(matrix_from_pairs(table, width + k), t) == old_part
                       for table, t, old_part in zip((left, right), marks, kept, strict=True))
            steps[k] = {"added_distance_four_pairs_per_side": left_stats[2],
                        "new_tip_counts_at_two_and_three": left_stats[1],
                        "retained_part_on_both_sides": kept[0],
                        "verified_marked_pairs": len(incident)}
        records[width] = {"unmarked_loose_anchor": 18, "old_tip_counts_at_two_and_three": (0, 3),
                          "actual_old_distance_four_counts": [Counter(m.values())[4] for m in before],
                          "first_steps": steps}
    assert set(records) == {27, 28}
    return records


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, sort_keys=True))
