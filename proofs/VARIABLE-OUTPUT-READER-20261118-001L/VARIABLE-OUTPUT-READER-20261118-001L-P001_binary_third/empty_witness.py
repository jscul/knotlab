"""Replay the first binary-third complementary caps and audit their minimum width."""

from collections import Counter
from functools import reduce
from itertools import combinations
from operator import xor
from pathlib import Path
import json

from census import algebra, checker, literal, mask, previous


HERE = Path(__file__).resolve().parent


def receipt(name):
    return json.loads((HERE / name).read_text())


def first_prefix():
    choices = [row["shortest_example"] for row in receipt("frontier.json")["complementary_moves"]
               if row["loose_bits"] == 6 and row["source_parent_count"] == 3 and row["outputs"] == 2
               and row["moves_with_a_complement"]]
    return min(choices, key=lambda event: event["width_before_join"])


def trace(history):
    steps = checker.replay(history)
    shapes = [(len(row["operands"]), len(row["fresh"])) for row in steps]
    assert shapes[:3] == [(0, 3), (1, 3), (1, 3)]
    assert shapes[3:].count((2, 3)) == 1
    assert all(pair in ((2, 3), (2, 2), (3, 2)) for pair in shapes[3:])
    return steps


def earlier_census():
    archived = receipt("census.json")
    widths = [row["width"] for row in archived["stages"]]
    assert widths == list(range(12, 32, 2))
    evidence = Counter()
    for row in archived["stages"]:
        result = row["full_screen"]
        assert result["tables"] == sum(count for t, _, count in row["counts_by_shrinks_and_nonempty_menu"] if t >= 2)
        for field in ("star_changing_self_generators", "empty_star_changing_self_generators",
                      "same_table_distinct_incidences", "empty_same_table_distinct_incidences",
                      "cross_candidates", "empty_cross_candidates"):
            assert not result.get(field, 0)
        evidence.update(tables=result["tables"], live_generators=result.get("self_generators", 0),
                        empty_generators=result.get("empty_self_generators", 0), all_types=row["physical_types"])
    assert evidence == Counter(tables=1724, live_generators=494, empty_generators=2310, all_types=38945)
    return {"earlier_family_widths": widths, **evidence}


def run():
    event = first_prefix()
    width = event["width_before_join"]
    assert width == 30
    prefix = previous.named(event["junction_supports"])
    a, b = (tuple(event[key]) for key in ("first_inputs", "second_inputs"))
    before, adjacent = literal.incidence(prefix)
    boundary = tuple(sorted(bit for bit, holders in before.items() if len(holders) == 1))
    assert tuple(sorted(a + b)) == boundary and len(boundary) == 6
    assert a in literal.direct_triples(before, adjacent) and b in literal.direct_triples(before, adjacent)
    histories = [checker.named_step(prefix, operands, 2, width) for operands in (a, b)]
    steps = [trace(history) for history in histories]
    history_stars = [frozenset(mask(row) for _, row in history) for history in histories]
    first, second = history_stars
    assert first != second
    left_cap, = first - second
    right_cap, = second - first
    assert left_cap ^ right_cap == mask(boundary) == reduce(xor, (mask(row) for _, row in prefix))
    spaces = [algebra.span(stars) for stars in history_stars]
    assert spaces[0] == spaces[1]

    left, left_bonds, left_menu = checker.measure(histories[0], independent=True)
    right, right_bonds, right_menu = checker.measure(histories[1], independent=True)
    assert not left_menu and not right_menu and left_bonds == right_bonds and left == right
    assert len(left) == 496
    permutation = list(range(32))
    for x, y in zip(a, b, strict=True):
        assert before[x] == before[y]
        permutation[x], permutation[y] = y, x
    assert all(right[tuple(sorted(permutation[bit] for bit in pair))] == k for pair, k in left.items())
    assert {mask(permutation[bit] for bit in row) for _, row in histories[0]} == second
    rank = algebra.rank(spaces[0])
    return {"width": 32, "junctions": len(histories[0]), "prefix_width": width, "common_prefix": event["junction_supports"],
            "loose_prefix_distinctions": boundary, "legal_prefix_triples": sorted(literal.direct_triples(before, adjacent)),
            "final_joins": [rows[-1] for rows in steps], "legal_triples_after": [sorted(left_menu), sorted(right_menu)],
            "equation_rank": rank, "equation_space_size": len(spaces[0]), "allowed_states": 1 << (32 - rank),
            "bond_count": len(left_bonds), "all_pair_entries_checked": len(left),
            "K_upper_triangle": [left[pair] for pair in combinations(range(32), 2)],
            "identity_matching_maps_physical_support_sets": first == second,
            "identity_matching_pair_disagreements": sum(left[pair] != right[pair] for pair in left),
            "support_isomorphism_also_preserving_table": permutation, "earlier_exclusion": earlier_census()}


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
