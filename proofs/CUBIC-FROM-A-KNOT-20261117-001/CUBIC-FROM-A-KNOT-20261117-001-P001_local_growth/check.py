"""Check local parity growth and recover the finite cubic fixtures after growth."""

from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from itertools import combinations, product
from math import comb
from pathlib import Path
from random import Random

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "tools"))
from knotlab import Relation, check_knot

Checks = dict[str, tuple[str, ...]]
Groups = dict[str, tuple[str, ...]]
Point = tuple[int, int, int]
AXES: tuple[Point, ...] = ((1, 0, 0), (0, 1, 0), (0, 0, 1))


def seed() -> Checks:
    return {"k0": ("p0", "p1", "p2")}


def incidence(checks: Checks) -> tuple[dict[str, list[str]], dict[str, set[str]]]:
    users = defaultdict(list)
    neighbors = {knot: set() for knot in checks}
    for knot, bits in checks.items():
        assert len(bits) == len(set(bits))
        for bit in bits:
            users[bit].append(knot)
    for owners in users.values():
        assert len(owners) in (1, 2)
        if len(owners) == 2:
            left, right = owners
            neighbors[left].add(right)
            neighbors[right].add(left)
    return dict(users), neighbors


def loose_ports(users: dict[str, list[str]]) -> dict[str, list[str]]:
    loose = defaultdict(list)
    for bit, owners in users.items():
        if len(owners) == 1:
            loose[owners[0]].append(bit)
    return dict(loose)


def parent_groups(checks: Checks) -> tuple[tuple[tuple[str, ...], ...], dict]:
    users, neighbors = incidence(checks)
    loose = loose_ports(users)
    front = sorted(loose)
    pairs = {
        (first, second) for first, second in combinations(front, 2)
        if neighbors[first] & neighbors[second]
    }
    triangles = [
        triple for triple in combinations(front, 3)
        if all(pair in pairs for pair in combinations(triple, 2))
    ]
    triples = [
        (a, b, c) for a, b, c in triangles
        if not neighbors[a] & neighbors[b] & neighbors[c]
    ]
    paired_in_triples = {pair for triple in triples for pair in combinations(triple, 2)}
    groups = [*triples, *sorted(pairs - paired_in_triples)]
    demand = Counter(parent for group in groups for parent in group)
    for parent in front:
        remaining = len(loose[parent]) - demand[parent]
        if remaining < 0:
            raise ValueError("The selected parent groups require too many loose ports")
        groups.extend([(parent,)] * remaining)
    return tuple(groups), {
        "front_knots": len(front),
        "candidate_pairs": len(pairs),
        "common_neighbor_triangles_rejected": len(triangles) - len(triples),
        "parent_group_sizes": dict(Counter(map(len, groups))),
    }


def legal_local_move(checks: Checks, consumed: tuple[str, ...], fresh: tuple[str, ...]) -> bool:
    users, neighbors = incidence(checks)
    if len(fresh) != 3 or len(set(fresh)) != 3 or set(fresh) & users.keys():
        return False
    if not 1 <= len(consumed) <= 3 or any(len(users.get(bit, ())) != 1 for bit in consumed):
        return False
    parents = [users[bit][0] for bit in consumed]
    if len(parents) != len(set(parents)):
        return False
    if any(not neighbors[left] & neighbors[right] for left, right in combinations(parents, 2)):
        return False
    return len(parents) < 3 or not set.intersection(*(neighbors[parent] for parent in parents))


def grow_parallel(
    depth: int, reverse_ports: bool = False
) -> tuple[list[Checks], list[Groups], list[dict]]:
    checks = seed()
    snapshots, births, records = [dict(checks)], [{"k0": ()}], []
    next_port = 3
    for _ in range(depth):
        groups, record = parent_groups(checks)
        loose = loose_ports(incidence(checks)[0])
        available = {
            parent: sorted(bits, reverse=not reverse_ports) for parent, bits in loose.items()
        }
        new_checks, parents_by_child = {}, {}
        for parents in groups:
            consumed = tuple(available[parent].pop() for parent in parents)
            fresh = tuple(f"p{id_}" for id_ in range(next_port, next_port + 3))
            next_port += 3
            assert legal_local_move(checks, consumed, fresh)
            child = f"k{len(checks) + len(new_checks)}"
            new_checks[child] = consumed + fresh
            parents_by_child[child] = parents
        assert all(not remaining for remaining in available.values())
        checks.update(new_checks)
        assert set(loose_ports(incidence(checks)[0])) == set(new_checks)
        snapshots.append(dict(checks))
        births.append(parents_by_child)
        records.append(record)
    return snapshots, births, records


def add(point: Point, direction: Point) -> Point:
    return tuple(a + b for a, b in zip(point, direction))


def recover_coordinates(births: list[Groups]) -> dict[str, Point]:
    """Audit the trace after generation. No coordinate enters the growth rule."""
    root, = births[0]
    coordinates = {root: (0, 0, 0)}
    assert len(births[1]) == 3
    for child, direction in zip(births[1], AXES):
        assert births[1][child] == (root,)
        coordinates[child] = direction
    for rank, group in enumerate(births[2:], start=2):
        for child, parents in group.items():
            incoming = [coordinates[parent] for parent in parents]
            if len(incoming) == 1:
                point, = incoming
                direction, = [axis for axis, value in zip(AXES, point) if value]
                target = add(point, direction)
            else:
                target = tuple(max(column) for column in zip(*incoming))
            assert sum(target) == rank
            predecessors = {
                tuple(a - b for a, b in zip(target, axis))
                for axis, value in zip(AXES, target) if value
            }
            assert set(incoming) == predecessors
            coordinates[child] = target
    return coordinates


def point_incidence(checks: Checks, coordinates: dict[str, Point]) -> Counter:
    users, _ = incidence(checks)
    return Counter(tuple(sorted(coordinates[knot] for knot in owners)) for owners in users.values())


def check_layers(snapshots: list[Checks], coordinates: dict[str, Point]) -> list[int]:
    counts = []
    for rank, snapshot in enumerate(snapshots):
        expected = {point for point in product(range(rank + 1), repeat=3) if sum(point) <= rank}
        assert {coordinates[knot] for knot in snapshot} == expected
        assert len(snapshot) == len(expected) == comb(rank + 3, 3)
        expected_sharing = {
            tuple(sorted((point, add(point, direction))))
            for point in expected for direction in AXES if sum(point) < rank
        }
        actual = point_incidence(snapshot, coordinates)
        assert {holders for holders in actual if len(holders) == 2} == expected_sharing
        assert all(actual[holders] == 1 for holders in expected_sharing)
        assert {holders[0]: count for holders, count in actual.items() if len(holders) == 1} == {
            point: 3 for point in expected if sum(point) == rank
        }
        counts.append(comb(rank + 2, 2))
    return counts


def binary_rank(rows: tuple[int, ...]) -> int:
    basis = {}
    for row in rows:
        while row:
            pivot = row.bit_length()
            if pivot in basis:
                row ^= basis[pivot]
            else:
                basis[pivot] = row
                break
    return len(basis)


def encode(checks: Checks, bit_ids: dict[str, int]) -> tuple[int, ...]:
    return tuple(sum(1 << bit_ids[bit] for bit in bits) for bits in checks.values())


def projected_equations(equations: tuple[int, ...], kept_mask: int) -> tuple[int, ...]:
    """Return generators of the row-space subspace supported on the kept bits."""
    outside_pivots, restricted = {}, []
    for row in equations:
        while row & ~kept_mask:
            pivot = (row & ~kept_mask).bit_length()
            if pivot in outside_pivots:
                row ^= outside_pivots[pivot]
            else:
                outside_pivots[pivot] = row
                break
        else:
            if row:
                restricted.append(row)
    return tuple(restricted)


def same_equations(left: tuple[int, ...], right: tuple[int, ...]) -> bool:
    return binary_rank(left) == binary_rank(right) == binary_rank(left + right)


def check_conservation(snapshots: list[Checks]) -> list[int]:
    all_bits = {bit for bits in snapshots[-1].values() for bit in bits}
    bit_ids = {bit: index for index, bit in enumerate(sorted(all_bits))}
    encoded = [encode(snapshot, bit_ids) for snapshot in snapshots]
    ranks = [binary_rank(equations) for equations in encoded]
    assert ranks == [len(snapshot) for snapshot in snapshots]
    for old, before, after in zip(snapshots, encoded, encoded[1:]):
        old_bits = {bit for bits in old.values() for bit in bits}
        old_mask = sum(1 << bit_ids[bit] for bit in old_bits)
        assert same_equations(before, projected_equations(after, old_mask))
    return ranks


def verify_actual_knot_projections(checks: Checks) -> dict:
    all_bits = {bit for bits in checks.values() for bit in bits}
    bit_ids = {bit: index for index, bit in enumerate(sorted(all_bits))}
    equations = encode(checks, bit_ids)
    reports = {}
    for bits, row in zip(checks.values(), equations):
        projected = projected_equations(equations, row)
        assert same_equations((row,), projected)
        arity = len(bits)
        if arity in reports:
            continue
        allowed = frozenset(
            values for values in product((False, True), repeat=arity)
            if all(
                (constraint & sum(1 << bit_ids[bit] for bit, value in zip(bits, values) if value))
                .bit_count() % 2 == 0
                for constraint in projected
            )
        )
        report = check_knot(Relation(bits, allowed), bits[:-1], bits[-1])
        assert report.is_knot
        reports[arity] = {
            "allowed_rows": len(allowed),
            "K1": report.binding,
            "K2": report.loss_on_erasure,
            "K3": report.coexistence,
        }
    return {"exact_projections": len(checks), "canonical_examples_by_arity": reports}


def block_control(checks: Checks, coordinates: dict[str, Point], side: int) -> dict:
    block = {knot: bits for knot, bits in checks.items() if max(coordinates[knot]) < side}
    assert len(block) == side ** 3
    prefix, replay = [], {}
    for knot, bits in block.items():
        old_bits = incidence(replay)[0]
        consumed = tuple(bit for bit in bits if bit in old_bits)
        fresh = tuple(bit for bit in bits if bit not in old_bits)
        if replay:
            assert legal_local_move(replay, consumed, fresh)
        else:
            assert knot == "k0" and not consumed and len(fresh) == 3
        replay[knot] = bits
        prefix.append(dict(replay))
    ranks = check_conservation(prefix)

    users, _ = incidence(block)
    shared = sum(len(holders) == 2 for holders in users.values())
    assert shared == 3 * (side - 1) * side ** 2
    loose = loose_ports(users)
    for knot in block:
        assert len(loose.get(knot, ())) == coordinates[knot].count(side - 1)
    assert len(users) == 3 * side ** 3
    all_bits = {bit for bits in checks.values() for bit in bits}
    bit_ids = {bit: index for index, bit in enumerate(sorted(all_bits))}
    kept_mask = sum(1 << bit_ids[bit] for bit in users)
    retained = projected_equations(encode(checks, bit_ids), kept_mask)
    assert same_equations(encode(block, bit_ids), retained)
    return {
        "side": side,
        "knots": len(block),
        "shared_bits": shared,
        "loose_bits": sum(map(len, loose.values())),
        "all_incident_bits": len(users),
        "equation_rank": ranks[-1],
        "legal_asynchronous_moves": len(prefix) - 1,
        "old_relations_preserved_per_move": True,
        "outgoing_boundary_included_in_exact_projection": True,
        "incident_knot_projections": verify_actual_knot_projections(block),
    }


def renamed_schedule_control(snapshots: list[Checks]) -> int:
    rng = Random(1729)
    for snapshot in snapshots:
        users, _ = incidence(snapshot)
        new_knots = [f"renamed-knot-{i:04d}" for i in range(len(snapshot))]
        new_bits = [f"renamed-bit-{i:04d}" for i in range(len(users))]
        rng.shuffle(new_knots)
        rng.shuffle(new_bits)
        knot_map = dict(zip(sorted(snapshot), new_knots))
        bit_map = dict(zip(sorted(users), new_bits))
        renamed = {
            knot_map[name]: tuple(bit_map[bit] for bit in reversed(bits))
            for name, bits in reversed(tuple(snapshot.items()))
        }
        groups, _ = parent_groups(snapshot)
        renamed_groups, _ = parent_groups(renamed)
        expected = Counter(tuple(sorted(knot_map[knot] for knot in group)) for group in groups)
        assert expected == Counter(tuple(sorted(group)) for group in renamed_groups)
    return len(snapshots)


def front_controls() -> dict:
    tree = seed()
    snapshots = [dict(tree)]
    pending = [("k0", "p0"), ("k0", "p1"), ("k0", "p2")]
    for i in range(1, 8):
        _, port = pending.pop(0)
        child = f"k{i}"
        fresh = tuple(f"t{i}-{position}" for position in range(3))
        assert legal_local_move(tree, (port,), fresh)
        tree[child] = (port, *fresh)
        pending.extend((child, bit) for bit in fresh)
        snapshots.append(dict(tree))
    tree_users, tree_neighbors = incidence(tree)
    assert sum(map(len, tree_neighbors.values())) == 2 * (len(tree) - 1)
    assert len(loose_ports(tree_users)) > 0
    check_conservation(snapshots)

    closed = {str(knot): tuple(f"{min(knot, other)}-{max(knot, other)}" for other in range(4)
                              if knot != other)
              for knot in range(4)}
    assert not parent_groups(closed)[0]
    assert not legal_local_move(closed, ("0-1",), ("new-a", "new-b", "new-c"))
    assert not legal_local_move(seed(), ("p0", "p1"), ("new-a", "new-b", "new-c"))
    assert legal_local_move(seed(), ("p0",), ("new-a", "new-b", "new-c"))
    assert not legal_local_move(snapshots[1], ("p0",), ("new-a", "new-b", "new-c"))
    return {
        "legal_asynchronous_tree_knots": len(tree),
        "tree_shared_bits": len(tree) - 1,
        "tree_loose_bits": sum(map(len, loose_ports(tree_users).values())),
        "closed_front_has_no_moves": True,
        "consumed_port_rejected": True,
        "two_ports_from_same_producer_rejected": True,
    }


def run() -> dict:
    snapshots, births, stage_controls = grow_parallel(9)
    assert stage_controls[0]["parent_group_sizes"] == {1: 3}
    assert stage_controls[1]["common_neighbor_triangles_rejected"] == 1
    coordinates = recover_coordinates(births)
    counts = check_layers(snapshots, coordinates)
    ranks = check_conservation(snapshots)

    alternate, alternate_births, _ = grow_parallel(9, reverse_ports=True)
    alternate_coordinates = recover_coordinates(alternate_births)
    assert snapshots != alternate
    assert check_layers(alternate, alternate_coordinates) == counts
    for first, second in zip(snapshots, alternate):
        assert point_incidence(first, coordinates) == point_incidence(second, alternate_coordinates)

    return {
        "tetrahedral_layers": counts,
        "cumulative_equation_ranks": ranks,
        "parallel_round_checks": stage_controls,
        "snapshot_renaming_checks": renamed_schedule_control(snapshots),
        "reversed_port_allocations_isomorphic_each_round": True,
        "closed_and_asynchronous_controls": front_controls(),
        "blocks": [block_control(snapshots[-1], coordinates, side) for side in (3, 4)],
        "full_tetrahedral_incident_projections": verify_actual_knot_projections(snapshots[-1]),
    }


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, sort_keys=True))
