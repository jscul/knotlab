"""Compile the bounded attachment from measured adjacency and audit its replay."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from collections import Counter, deque
from dataclasses import dataclass, replace
from itertools import combinations, permutations, product
from pathlib import Path
from random import Random
from typing import TypeVar


ROOT = Path(__file__).resolve().parents[3]
GROWTH = (
    ROOT / "proofs/CUBIC-FROM-A-KNOT-20261117-001"
    / "CUBIC-FROM-A-KNOT-20261117-001-P001_local_growth"
)
ALIGNED = (
    ROOT / "proofs/ALIGNED-NEXT-JOIN-20261117-001"
    / "ALIGNED-NEXT-JOIN-20261117-001-P001_aligned_reader"
)
SOURCE_DIGESTS = {
    GROWTH / "check.py": "038a6845675cbc158e1abd0b55e72addd935c4dee9e6bb8153abe82a543894e8",
    ALIGNED / "check_aligned.py": "caeec42b1cb75491e43d0510d8af6ac53c96b8bf754189eb45cd6af01e006b14",
    ALIGNED / "read_frontier.py": "652c0ee41e6437918335c9b6a610e920a6a55ab3ed15ca46cfcc0242816ac4df",
}
Point = tuple[int, int, int]
Label = int | str
Identity = TypeVar("Identity", int, str)
Chart = dict[int, Point]
Adjacency = dict[int, set[int]]
Checks = dict[Point, tuple[Label, ...]]
CUBE = frozenset(product((0, 1), repeat=3))


@dataclass(frozen=True)
class Move:
    point: Point
    incoming: tuple[Label, ...]
    outgoing: tuple[Label, ...]
    fresh: tuple[str, ...]
    original: int | None


@dataclass(frozen=True)
class LocalTarget:
    sites: frozenset[Point]
    holders: Counter[tuple[Point, ...]]
    mark_holders: frozenset[tuple[Point, ...]]
    tip_orders_checked: int


def load_source(name: str, path: Path):
    assert hashlib.sha256(path.read_bytes()).hexdigest() == SOURCE_DIGESTS[path]
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def steps_from(adjacency: dict[Identity, set[Identity]], root: Identity) -> dict[Identity, int]:
    steps = {root: 0}
    pending = deque([root])
    while pending:
        vertex = pending.popleft()
        for neighbor in adjacency[vertex] - steps.keys():
            steps[neighbor] = steps[vertex] + 1
            pending.append(neighbor)
    if steps.keys() != adjacency.keys():
        raise ValueError("The measured adjacency is disconnected")
    return steps


def compatible_chart(adjacency: Adjacency, chart: Chart) -> bool:
    return (
        len(adjacency) == len(CUBE)
        and adjacency.keys() == chart.keys()
        and set(chart.values()) == CUBE
        and all(
            (right in adjacency[left]) == (sum(a != b for a, b in zip(u, v)) == 1)
            for (left, u), (right, v) in combinations(chart.items(), 2)
        )
        and all(
            left not in neighbors
            and all(right in chart and left in adjacency[right] for right in neighbors)
            for left, neighbors in adjacency.items()
        )
    )


def cube_frames(adjacency: Adjacency) -> tuple[Chart, ...]:
    """Recover each frame from an origin and an ordering of its measured neighbors."""
    if len(adjacency) != 8 or any(
        len(neighbors) != 3
        or vertex in neighbors
        or any(vertex not in adjacency.get(neighbor, ()) for neighbor in neighbors)
        for vertex, neighbors in adjacency.items()
    ):
        raise ValueError("Expected eight IDs with symmetric degree-three adjacency")
    steps = {root: steps_from(adjacency, root) for root in adjacency}
    charts = []
    for root in sorted(adjacency):
        for neighbors in permutations(sorted(adjacency[root])):
            chart = {
                bit: tuple(int(steps[neighbor][bit] < steps[root][bit]) for neighbor in neighbors)
                for bit in adjacency
            }
            if not compatible_chart(adjacency, chart):
                raise ValueError("The measured graph failed the classical Q3 check")
            charts.append(chart)
    assert len({tuple(sorted(chart.items())) for chart in charts}) == 48
    return tuple(charts)


def locally_generated_target(growth) -> LocalTarget:
    """Generate the target by ordinary growth, and read its sites from incidence."""
    snapshots, _, _ = growth.grow_parallel(4)
    checks = snapshots[-1]
    _, adjacency = growth.incidence(checks)
    root, = (junction for junction, bits in checks.items() if len(bits) == 3)
    tips = sorted(junction for junction, neighbors in adjacency.items() if len(neighbors) == 1)
    assert len(tips) == 3
    steps = steps_from(adjacency, root)
    extent, = {steps[tip] for tip in tips}
    assert extent == 4
    tip_steps = {tip: steps_from(adjacency, tip) for tip in tips}
    reference = None
    orders = 0
    for ordered_tips in permutations(tips):
        chart = {}
        for vertex, grade in steps.items():
            doubled = tuple(extent + grade - tip_steps[tip][vertex] for tip in ordered_tips)
            assert all(value >= 0 and value % 2 == 0 for value in doubled)
            point = tuple(value // 2 for value in doubled)
            assert sum(point) == grade
            chart[vertex] = point
        sites = frozenset(chart.values())
        assert len(sites) == len(checks) == 35 and CUBE <= sites
        holders = growth.point_incidence(checks, chart)
        marks = frozenset((point, (point[0], point[1], point[2] + 1)) for point in CUBE)
        assert all(holders[ends] == 1 for ends in marks)
        current = (sites, holders, marks)
        if reference is None:
            reference = current
        assert current == reference
        orders += 1
    assert orders == 6
    return LocalTarget(*reference, orders)


def compile_alignment(adjacency: Adjacency, chart: Chart, target: LocalTarget) -> tuple[Move, ...]:
    """Compile the entire bounded update from one compatible measured frame."""
    if not compatible_chart(adjacency, chart):
        raise ValueError("Chart disagrees with the measured adjacency")
    original_at = {point: bit for bit, point in chart.items()}
    order = sorted(target.sites, key=lambda point: (point not in CUBE, sum(point), point))
    given = {}
    moves = []
    next_fresh = 0
    for point in order:
        incoming = tuple(
            given[point[:axis] + (value - 1,) + point[axis + 1:]][axis]
            for axis, value in enumerate(point)
            if value
        )
        original = original_at.get(point)
        count = 3 if original is None else 2
        fresh = tuple(f"fresh-{i}" for i in range(next_fresh, next_fresh + count))
        next_fresh += count
        outgoing = fresh if original is None else (*fresh, original)
        given[point] = outgoing
        moves.append(Move(point, incoming, outgoing, fresh, original))
    return tuple(moves)


def cut_rows_in_chart(chart: Chart, old_ids: tuple[int, ...]) -> set[tuple[int, ...]]:
    return {(0,) * len(old_ids), (1,) * len(old_ids)} | {
        tuple(chart[bit][axis] ^ flip for bit in old_ids)
        for axis in range(3)
        for flip in (0, 1)
    }


def audit_replay(moves, old_ids, old_rows, growth, target):
    """Replay exact old identities and check all prefixes using binary elimination."""
    checks: Checks = {}
    indexes = {bit: i for i, bit in enumerate(old_ids)}
    old_scope = set(old_ids)
    used_originals = set()
    old_mask = (1 << len(old_ids)) - 1
    row_counts = []
    arities = Counter()
    for move in moves:
        assert move.point not in checks and set(move.incoming) <= indexes.keys()
        assert len(move.fresh) == len(set(move.fresh)) and indexes.keys().isdisjoint(move.fresh)
        if move.original is None:
            assert len(used_originals) == len(old_scope)
            assert growth.legal_local_move(checks, move.incoming, move.fresh)
            assert move.outgoing == move.fresh
        else:
            assert move.original in old_scope - used_originals
            assert move.original not in move.incoming
            assert len(move.fresh) == 2 and move.outgoing == (*move.fresh, move.original)
            if checks:
                users, _ = growth.incidence(checks)
                assert all(len(users[used]) == 1 for used in move.incoming)
                assert move.original not in users
            else:
                assert not move.incoming
            used_originals.add(move.original)
        checks[move.point] = (*move.incoming, *move.outgoing)
        arities[len(checks[move.point])] += 1
        indexes.update({bit: i for i, bit in enumerate(move.fresh, start=len(indexes))})
        equations = growth.encode(checks, indexes)
        rank = growth.binary_rank(equations)
        assert rank == len(equations) == len(checks)
        assert not growth.projected_equations(equations, old_mask)
        row_count = len(old_rows) << (len(indexes) - rank - len(old_ids))
        previous = row_counts[-1] if row_counts else len(old_rows)
        assert row_count == previous * 2 ** (len(move.fresh) - 1)
        row_counts.append(row_count)

    users, _ = growth.incidence(checks)
    shared = sum(len(owners) == 2 for owners in users.values())
    loose = sum(len(owners) == 1 for owners in users.values())
    assert users.keys() == indexes.keys() and used_originals == old_scope
    assert all(len(users[bit]) == 2 for bit in old_ids)
    holders = Counter(tuple(sorted(owners)) for owners in users.values())
    assert holders == target.holders
    assert {tuple(sorted(users[bit])) for bit in old_ids} == target.mark_holders
    assert (len(checks), len(users), shared, loose) == (35, 105, 60, 45)
    assert row_counts[7] == 2048 and row_counts[-1] == 2 ** 65
    return checks, {
        "parity_junctions": len(checks),
        "rank": rank,
        "arity_histogram": dict(sorted(arities.items())),
        "reused_old_distinctions": len(used_originals),
        "fresh_distinctions": len(users) - len(old_ids),
        "shared_distinctions": shared,
        "loose_distinctions": loose,
        "two_fresh_attachments": len(used_originals),
        "legal_three_fresh_moves": len(checks) - len(used_originals),
        "prefixes_with_exact_old_projection": len(row_counts),
        "states_after_attachment": row_counts[7],
        "states_at_I4": row_counts[-1],
        "full_incidence_and_original_roles_match_local_target": True,
    }


def bind_aligned_model(moves, checks, old_ids, old_rows, model, aligned):
    """Verify the parity rows and the literal old relation under one bit bijection."""
    outgoing = {move.point: move.outgoing for move in moves}
    bit_labels = tuple(outgoing[point][axis] for point, axis in model.wires)
    assert len(set(bit_labels)) == len(model.wires) == 105
    assert set(checks) == set(model.vertices)
    assert set(bit_labels) == {bit for support in checks.values() for bit in support}
    for point, mask in zip(model.vertices, model.stars, strict=True):
        assert set(checks[point]) == {bit_labels[i] for i in aligned.bits(mask)}
    old_indices = {bit: i for i, bit in enumerate(old_ids)}
    marks = tuple(bit_labels[i] for i in model.mark_bits)
    assert set(marks) == old_indices.keys()
    transported = {
        sum(row[old_indices[bit]] << i for i, bit in enumerate(marks))
        for row in old_rows
    }
    assert transported == aligned.CUT_WORDS
    return bit_labels


def audit_reader(moves, checks, old_ids, old_rows, data, growth, aligned, reader, seed):
    """Evaluate the reader on a shuffled scalar table of the actual mixed relation."""
    bit_labels = bind_aligned_model(moves, checks, old_ids, old_rows, data.model, aligned)
    shuffled = list(bit_labels)
    Random(seed).shuffle(shuffled)
    assert shuffled != list(bit_labels)
    indexes = {bit: i for i, bit in enumerate(shuffled)}
    equations = growth.encode(checks, indexes)
    old_mask = sum(1 << indexes[bit] for bit in old_ids)
    old_words = tuple(
        sum(value << indexes[bit] for bit, value in zip(old_ids, row, strict=True))
        for row in old_rows
    )
    short_supports = {
        sum(1 << indexes[bit_labels[i]] for i in aligned.bits(support))
        for support in data.mixed
    }

    # The audited isomorphism transfers completeness of the inherited census.
    # Recompute each reported projection from the replay equations and literal rows.
    projections = {}

    def project(support):
        if support not in projections:
            required = growth.projected_equations(equations, support | old_mask)
            submasks = [0]
            for index in aligned.bits(support):
                submasks.extend([word | (1 << index) for word in submasks])
            overlap = support & old_mask
            projections[support] = {
                word for word in submasks
                if any(
                    (word ^ old) & overlap == 0
                    and all((check & (word | old)).bit_count() % 2 == 0 for check in required)
                    for old in old_words
                )
            }
        return projections[support]

    for support in short_supports:
        arity = support.bit_count()
        assert 0 < len(project(support)) < 2 ** arity
        for i in aligned.bits(support):
            assert len(project(support ^ (1 << i))) == 2 ** (arity - 1)
    for bits in checks.values():
        support = sum(1 << indexes[bit] for bit in bits)
        assert project(support) == {
            sum(value << indexes[bit] for bit, value in zip(bits, values, strict=True))
            for values in product((0, 1), repeat=len(bits)) if sum(values) % 2 == 0
        }
        names = tuple(f"p{indexes[bit]}" for bit in bits)
        rows = frozenset(
            tuple(bool(word & (1 << indexes[bit])) for bit in bits)
            for word in project(support)
        )
        assert aligned.check_knot(aligned.Relation(names, rows), names[:-1], names[-1]).is_knot

    scalar_rows = reader.sparse_rows(len(shuffled), short_supports)
    result = reader.read_frontier(scalar_rows)
    users, neighbors = growth.incidence(checks)
    loose = {
        point: tuple(sorted(indexes[bit] for bit in ports))
        for point, ports in growth.loose_ports(users).items()
    }
    expected_input_sets = {
        ports: {indexes[bit] for bit in checks[point]} - set(ports)
        for point, ports in loose.items()
    }
    expected_pairs = {
        tuple(sorted((loose[p], loose[q])))
        for p, q in combinations(loose, 2) if neighbors[p] & neighbors[q]
    }
    actual_pairs = {
        tuple(sorted((p, q))) for p, adjacent in result["adjacent"].items() for q in adjacent
    }
    groups, _ = growth.parent_groups(checks)
    expected_groups = Counter(tuple(sorted(loose[point] for point in group)) for group in groups)
    assert result["incoming"] == expected_input_sets
    assert actual_pairs == expected_pairs and len(actual_pairs) == 30
    assert Counter(result["groups"]) == expected_groups
    counts = dict(sorted(Counter(map(len, result["groups"])).items()))
    assert len(result["triplets"]) == 15 and counts == {1: 3, 2: 12, 3: 6}
    threshold_counts = Counter(
        scalar_rows[i].get(j, "above_five")
        for i, j in combinations(range(len(scalar_rows)), 2)
    )
    return {
        "anonymous_distinctions": len(scalar_rows),
        "thresholded_pairs": {str(k): v for k, v in threshold_counts.items()},
        "minimal_supports_at_most_six": len(short_supports),
        "recomputed_support_and_erasure_projections": len(projections),
        "exact_junction_knot_projections": len(checks),
        "live_triplets": len(result["triplets"]),
        "candidate_pairs": len(actual_pairs),
        "required_joins": len(result["groups"]),
        "required_joins_by_parent_count": counts,
        "reader_permutation_seed": seed,
    }


def reject_wrong_chart(adjacency, chart, old_ids, old_rows, target):
    left = min(adjacency)
    right = min(adjacency[left])
    wrong_chart = dict(chart)
    wrong_chart[left], wrong_chart[right] = chart[right], chart[left]
    assert cut_rows_in_chart(wrong_chart, old_ids) != set(old_rows)
    try:
        compile_alignment(adjacency, wrong_chart, target)
    except ValueError:
        return {"swapped_adjacent_original_ids": [left, right], "rejected": True}
    raise AssertionError("The compiler accepted an incompatible chart")


def audit_frame_covariance(first, second, renaming):
    """Check the entire roster of move schedules under one common renaming."""
    for frame, plan in first.items():
        transported_frame = tuple(sorted((renaming[bit], point) for bit, point in frame))
        transported_plan = tuple(
            replace(
                move,
                incoming=tuple(renaming.get(bit, bit) for bit in move.incoming),
                outgoing=tuple(renaming.get(bit, bit) for bit in move.outgoing),
                original=renaming.get(move.original),
            )
            for move in plan
        )
        assert second[transported_frame] == transported_plan
    return len(first)


def run() -> dict:
    from check_probe import measured_cube, seed_fixture

    growth = load_source("bootstrap_inherited_growth", GROWTH / "check.py")
    aligned = load_source("bootstrap_inherited_aligned", ALIGNED / "check_aligned.py")
    reader = load_source("bootstrap_inherited_reader", ALIGNED / "read_frontier.py")
    target = locally_generated_target(growth)
    data = aligned.short_supports(4)
    summaries = {}
    plans = []
    old_labels = []
    adjacencies = []
    for seed in (0, 1729):
        adjacency = measured_cube(seed)
        old_ids, old_rows = seed_fixture(seed)
        assert set(old_ids) == adjacency.keys() and len(set(old_rows)) == 8
        charts = cube_frames(adjacency)
        plans.append({})
        old_labels.append(old_ids)
        adjacencies.append(adjacency)
        replay_counts = None
        for index, chart in enumerate(charts):
            assert cut_rows_in_chart(chart, old_ids) == set(old_rows)
            moves = compile_alignment(adjacency, chart, target)
            checks, current = audit_replay(moves, old_ids, old_rows, growth, target)
            bind_aligned_model(moves, checks, old_ids, old_rows, data.model, aligned)
            plans[-1][tuple(sorted(chart.items()))] = moves
            if index == 0:
                replay_counts = current
                reader_counts = audit_reader(
                    moves, checks, old_ids, old_rows, data, growth, aligned, reader, seed + 321
                )
            assert current == replay_counts
        summaries[seed] = {
            "compatible_frames_replayed": len(charts),
            "replay": replay_counts,
            "reader": reader_counts,
            "incompatible_chart": reject_wrong_chart(adjacency, charts[0], old_ids, old_rows, target),
        }
    renaming = dict(zip(*old_labels, strict=True))
    assert any(left != right for left, right in renaming.items())
    expected_renamed_graph = {
        renaming[bit]: {renaming[other] for other in neighbors}
        for bit, neighbors in adjacencies[0].items()
    }
    assert adjacencies[1] == expected_renamed_graph
    return {
        "namings": {str(seed): summary for seed, summary in summaries.items()},
        "local_target": {
            "junctions": len(target.sites),
            "tip_orders_checked": target.tip_orders_checked,
            "shared_output_roles_for_originals": len(target.mark_holders),
        },
        "whole_plans_covariant_under_common_renaming": audit_frame_covariance(*plans, renaming),
        "source_sha256": {str(path.relative_to(ROOT)): digest for path, digest in SOURCE_DIGESTS.items()},
    }


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, sort_keys=True))
