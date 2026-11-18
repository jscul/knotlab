"""Verify identical allowed states with opposite complete-round feasibility."""

import importlib.util
import json
from collections import Counter
from itertools import combinations, product
from pathlib import Path


PROOFS = Path(__file__).resolve().parents[2]
PREDECESSOR = (
    PROOFS / "CUBIC-FROM-A-KNOT-20261117-001"
    / "CUBIC-FROM-A-KNOT-20261117-001-P001_local_growth"
)
AXES = "xyz"
DIAGONALS = {"001_111": ("z001", "z111"), "101_011": ("z101", "z011")}
COMMON = (("W", ("x100", "y010")), ("A", ("x110",)), ("B", ("y110",)))


def load_source(name):
    spec = importlib.util.spec_from_file_location(name, PREDECESSOR / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def cube_attachment():
    stars = {}
    for point in sorted(product(range(2), repeat=3), key=lambda p: (sum(p), p)):
        parent = "".join(map(str, point))
        incoming = []
        for axis, value in enumerate(point):
            if value:
                pred = list(point)
                pred[axis] -= 1
                incoming.append(AXES[axis] + "".join(map(str, pred)))
        stars[parent] = tuple(incoming + [axis + parent for axis in AXES])
    return stars


def cube_rows(stars, indexes, cut):
    points, states, _ = cut.seed_to_cube()
    original = {
        sum(value << indexes["z" + "".join(map(str, p))] for p, value in zip(points, state))
        for state in states
    }
    rows = original
    for vertex, star in stars.items():
        mask = sum(1 << indexes[p] for p in star if p not in ("x" + vertex, "y" + vertex))
        x = 1 << indexes["x" + vertex]
        y = 1 << indexes["y" + vertex]
        rows = {
            row | (free * y) | ((((row & mask).bit_count() + free) % 2) * x)
            for row in rows for free in (0, 1)
        }
    vertical = sum(1 << indexes["z" + vertex] for vertex in stars)
    assert len(rows) == 2048 and {row & vertical for row in rows} == original
    for star in stars.values():
        mask = sum(1 << indexes[p] for p in star)
        assert all((row & mask).bit_count() % 2 == 0 for row in rows)
    return rows


def grow(base, steps, rules):
    stars = dict(base)
    old = set().union(*stars.values())
    records = []
    for name, consumed in steps:
        fresh = tuple(f"{name.lower()}{i}" for i in range(3))
        assert name not in stars and len(set(fresh)) == 3 and old.isdisjoint(fresh)
        assert all(sum(bit in support for support in stars.values()) == 1 for bit in consumed)
        assert rules.legal_local_move(stars, consumed, fresh)
        records.append({"junction": name, "consumed": list(consumed), "fresh": list(fresh)})
        stars[name] = consumed + fresh
        old.update(fresh)
    return stars, records


def compare_states(base_rows, indexes, histories):
    """Replay the two sequences of equations with identical coordinate names in both histories."""
    for stage, (left, right) in enumerate(zip(*histories, strict=True)):
        assert left["fresh"] == right["fresh"]
        assert [indexes[bit] for bit in left["fresh"]] == list(range(24 + 3 * stage, 27 + 3 * stage))
    inputs = [
        [sum(1 << indexes[p] for p in step["consumed"]) for step in history]
        for history in histories
    ]
    assignments = {
        parity: [bits for bits in range(8) if bits.bit_count() % 2 == parity]
        for parity in (0, 1)
    }
    counts = [0] * (1 + len(inputs[0]))
    for base_row in base_rows:
        previous = {base_row}
        counts[0] += 1
        for stage, (left_mask, right_mask) in enumerate(zip(*inputs)):
            offset = 24 + 3 * stage
            extended = set()
            for row in previous:
                left = (row & left_mask).bit_count() % 2
                right = (row & right_mask).bit_count() % 2
                assert assignments[left] == assignments[right]
                extended.update(row | (addition << offset) for addition in assignments[left])
            assert len(extended) == 4 * len(previous)
            assert {row & ((1 << offset) - 1) for row in extended} == previous
            counts[stage + 1] += len(extended)
            previous = extended
    assert counts == [len(base_rows) * 4**stage for stage in range(len(counts))]
    return counts


def round_record(stars, rules):
    users, neighbors = rules.incidence(stars)
    loose = rules.loose_ports(users)
    live = sorted(loose)
    pairs = {pair for pair in combinations(live, 2) if neighbors[pair[0]] & neighbors[pair[1]]}
    triples = [
        triple for triple in combinations(live, 3)
        if all(pair in pairs for pair in combinations(triple, 2))
        and not set.intersection(*(neighbors[p] for p in triple))
    ]
    covered = {pair for triple in triples for pair in combinations(triple, 2)}
    groups = sorted(pairs - covered) + triples
    demand = Counter(parent for group in groups for parent in group)
    deficient = [p for p in live if demand[p] > len(loose[p])]
    result = {
        "required_multiple_groups": groups,
        "loose_bits": {p: sorted(loose[p]) for p in live},
        "capacity_and_demand": {p: [len(loose[p]), demand[p]] for p in live},
        "deficient": deficient,
        "feasible": not deficient,
    }
    if deficient:
        try:
            rules.parent_groups(stars)
        except ValueError as error:
            assert "too many loose ports" in str(error)
            return result
        raise AssertionError("The predecessor policy accepted the deficient snapshot")

    prescribed, _ = rules.parent_groups(stars)
    assert sorted(g for g in prescribed if len(g) > 1) == sorted(groups)
    remaining = {p: sorted(loose[p], reverse=True) for p in live}
    allocation = []
    for index, group in enumerate(prescribed):
        consumed = tuple(remaining[p].pop() for p in group)
        fresh = tuple(f"round-{index}-{j}" for j in range(3))
        assert rules.legal_local_move(stars, consumed, fresh)
        allocation.append(consumed)
    assert not any(remaining.values())
    result["one_complete_allocation"] = allocation
    return result


def main():
    rules = load_source("check")
    base = cube_attachment()
    labels = sorted(set().union(*base.values()))
    assert len(labels) == 24
    indexes = {bit: i for i, bit in enumerate(labels)}
    rows = cube_rows(base, indexes, load_source("cut_control"))
    branches = {}
    histories = []
    one_more_rounds = {}
    for name, diagonal in DIAGONALS.items():
        stars, history = grow(base, (("U", diagonal), *COMMON), rules)
        assert len(stars) == 12 and len(set().union(*stars.values())) == 36
        branches[name] = {"serial_moves": history, "next_round": round_record(stars, rules)}
        further, extra = grow(stars, (("N", ("w0",)),), rules)
        further_round = round_record(further, rules)
        one_more_rounds[name] = {
            "feasible": further_round["feasible"],
            "deficient": further_round["deficient"],
            "join_counts_by_parent_count": dict(sorted(Counter(
                len(group) for group in further_round.get("one_complete_allocation", [])
            ).items())),
        }
        histories.append(history + extra)
    for step in histories[0]:
        for bit in step["fresh"]:
            indexes[bit] = len(indexes)
    counts = compare_states(rows, indexes, histories)
    assert counts == [2048, 8192, 32768, 131072, 524288, 2097152]
    assert one_more_rounds["001_111"]["join_counts_by_parent_count"] == {1: 7, 2: 5, 3: 1}
    assert one_more_rounds["101_011"]["deficient"] == ["001", "111"]
    assert branches["001_111"]["next_round"]["feasible"]
    assert branches["101_011"]["next_round"]["deficient"] == ["001", "111"]

    # This rival first join is legal too, but changes the allowed states.
    rival = ("z001", "x100")
    assert rules.legal_local_move(base, rival, ("u0", "u1", "u2"))
    mismatch = (1 << indexes["z111"]) | (1 << indexes["x100"])
    disagreements = sum((row & mismatch).bit_count() % 2 for row in rows)
    assert 0 < disagreements < len(rows)
    assert not rules.legal_local_move(base, DIAGONALS["001_111"], ("z001", "u1", "u2"))
    return {
        "attachment_distinctions": len(labels),
        "rows_at_attachment_and_after_each_addition": counts[:-1],
        "one_further_common_singleton": {
            "input": "w0", "distinctions": len(indexes), "equal_complete_states": counts[-1],
            "rounds": one_more_rounds,
        },
        "old_row_lifts_per_addition": 4,
        "comparison": "Literal equality of full allowed states on the same distinction names at the attachment and after each tested addition",
        "branches": branches,
        "legal_wrong_first_join": {"inputs": rival, "disagreeing_attachment_rows": disagreements},
        "reused_fresh_bit_rejected": True,
    }


if __name__ == "__main__":
    print(json.dumps(main(), indent=2, sort_keys=True))
