"""Finite replay of the marked cut-path witnesses in cube_interface.md."""

from __future__ import annotations

import json
from collections import Counter
from itertools import product

Point = tuple[int, int, int]
Edge = tuple[Point, int]
MARKS = frozenset((point, 2) for point in product(range(2), repeat=3))
OFFSETS = ((0, 0, 0), (1, 0, 0), (0, 1, 0), (0, 0, 1), (1, 1, 1), (2, 0, 1), (0, 2, 1))
ORDERS = ((0, 1, 2), (2, 1, 0))
ANCHOR_MAX = 3
BOX_MAX = 8


def shift(point: Point, axis: int, delta: int = 1) -> Point:
    return tuple(value + (delta if index == axis else 0) for index, value in enumerate(point))


def neighbors(point: Point):
    for axis, value in enumerate(point):
        yield shift(point, axis), (point, axis)
        if value:
            lower = shift(point, axis, -1)
            yield lower, (lower, axis)


def extend(path: list[Point], target: Point, order: tuple[int, ...]) -> None:
    assert all(a <= b for a, b in zip(path[-1], target))
    for axis in order:
        while path[-1][axis] < target[axis]:
            path.append(shift(path[-1], axis))
    assert path[-1] == target


def witness(source: Edge, offset: Point, order: tuple[int, ...]) -> tuple[list[Point], str]:
    anchor, axis = source
    start = anchor if source in MARKS and anchor[2] == 0 else shift(anchor, axis)
    path = [start]
    if max(start[:2]) >= 2:
        case = "outside_footprint"
    elif start[2] <= 1:
        case = "height_zero" if start[2] == 0 else "height_one"
        horizontal = tuple(i for i in order if i != 2)
        exit_axis = max(horizontal, key=start.__getitem__)
        if start[2] == 1:
            assert axis != 2 and start[exit_axis] == 1
        escape = shift(start, exit_axis, 2 - start[exit_axis])
        extend(path, escape, order)
    elif start[2] == 2:
        case = "height_two"
        path.append(shift(start, 2))
    else:
        case = "above_marks"
    base = tuple(max(value, bound) for value, bound in zip(start, (2, 2, 3)))
    extend(path, base, order)
    target = tuple(value + delta for value, delta in zip(base, offset))
    extend(path, target, order)
    return path, case


def cut(vertices: set[Point]) -> set[Edge]:
    return {edge for point in vertices for other, edge in neighbors(point) if other not in vertices}


def connected(vertices: set[Point], excluded: set[Edge], adjacency: dict) -> bool:
    root = next(iter(vertices))
    seen, stack = {root}, [root]
    while stack:
        for other, edge in adjacency[stack.pop()]:
            if other in vertices and other not in seen and edge not in excluded:
                seen.add(other)
                stack.append(other)
    return len(seen) == len(vertices)


def validate_cuts() -> dict:
    box = set(product(range(BOX_MAX + 1), repeat=3))
    adjacency = {point: tuple((other, edge) for other, edge in neighbors(point) if other in box)
                 for point in box}
    cases, orientations, touched = Counter(), Counter(), Counter()
    bounds = {"max_path_length_minus_offset_sum": 0, "max_cut_size_minus_offset_term_and_one": 0}
    by_source = Counter()
    for anchor in product(range(ANCHOR_MAX + 1), repeat=3):
        for axis in range(3):
            source = (anchor, axis)
            status = ("bottom_mark" if anchor[2] == 0 else "upper_mark") if source in MARKS else "unmarked"
            by_source[status] += 1
            for offset, order in product(OFFSETS, ORDERS):
                path, case = witness(source, offset, order)
                vertices = set(path)
                assert len(vertices) == len(path) and vertices < box
                assert all(not (point in vertices and shift(point, i) in vertices) for point, i in MARKS)
                boundary = cut(vertices)
                assert all(point in box and shift(point, i) in box for point, i in boundary)
                assert source in boundary
                for target_axis in range(3):
                    target = path[-1], target_axis
                    assert source != target and target in boundary
                mark_count = len(boundary & MARKS)
                assert mark_count <= 2
                excluded = boundary | MARKS
                assert connected(vertices, excluded, adjacency)
                assert connected(box - vertices, excluded, adjacency)
                steps, offset_sum = len(path) - 1, sum(offset)
                assert steps <= 7 + offset_sum
                assert len(boundary) - 1 <= 4 * steps + 5 <= 4 * offset_sum + 33
                bounds["max_path_length_minus_offset_sum"] = max(
                    bounds["max_path_length_minus_offset_sum"], steps - offset_sum
                )
                bounds["max_cut_size_minus_offset_term_and_one"] = max(
                    bounds["max_cut_size_minus_offset_term_and_one"],
                    len(boundary) - 1 - 4 * offset_sum,
                )
                cases[case] += 1
                orientations[axis] += 1
                touched[mark_count] += 1
    for point in product(range(ANCHOR_MAX + 1), repeat=3):
        boundary = cut({point})
        assert len(boundary & MARKS) <= 2
        assert connected(box - {point}, boundary | MARKS, adjacency)
    return {
        "anchor_coordinate_max": ANCHOR_MAX,
        "enclosing_box_coordinate_max": BOX_MAX,
        "source_count_by_mark": dict(by_source),
        "target_offsets": OFFSETS,
        "monotone_axis_orders": ORDERS,
        "paths_checked": sum(cases.values()),
        "source_target_checks": 3 * sum(cases.values()),
        "paths_by_source_orientation": dict(orientations),
        "paths_by_escape_case": dict(cases),
        "cut_mark_count_histogram": dict(touched),
        "junction_stars_checked": (ANCHOR_MAX + 1) ** 3,
        **bounds,
    }


if __name__ == "__main__":
    print(json.dumps(validate_cuts(), indent=2, sort_keys=True))
