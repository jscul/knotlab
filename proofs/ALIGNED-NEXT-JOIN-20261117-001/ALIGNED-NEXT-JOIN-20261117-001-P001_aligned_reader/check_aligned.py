"""Exact short-support and symmetry check for the aligned mixed parity branch."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from functools import reduce
from itertools import combinations, product
from math import factorial, isqrt, prod
from operator import or_, xor
from pathlib import Path

import networkx as nx

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tools"))
from knotlab import Relation, check_knot

SOURCE = (
    ROOT / "proofs" / "CUBIC-FROM-A-KNOT-20261117-001"
    / "CUBIC-FROM-A-KNOT-20261117-001-P001_local_growth" / "check.py"
)
SOURCE_DIGEST = "038a6845675cbc158e1abd0b55e72addd935c4dee9e6bb8153abe82a543894e8"
SUPPORT_LIMIT = 6
SENTINEL = 6
AXES = ((1, 0, 0), (0, 1, 0), (0, 0, 1))
MARK_VERTICES = tuple(product((0, 1), repeat=3))
CUT_DIRECTIONS = tuple(sum(point[axis] << i for i, point in enumerate(MARK_VERTICES))
                       for axis in range(3))
CUT_WORDS = {0, 255} | set(CUT_DIRECTIONS) | {word ^ 255 for word in CUT_DIRECTIONS}
BAD_PLANES = {
    frozenset((left, right, left ^ right))
    for left, right in combinations(range(1, 8), 2)
    if {left, right, left ^ right} != {3, 5, 6}
}
FRESH = ("future-a", "future-b", "future-c")
Point = tuple[int, int, int]
Wire = tuple[Point, int]


@dataclass(frozen=True)
class Model:
    vertices: tuple[Point, ...]
    wires: tuple[Wire, ...]
    endpoints: tuple[tuple[int, int], ...]
    adjacency: tuple[tuple[tuple[int, int], ...], ...]
    stars: tuple[int, ...]
    mark_bits: tuple[int, ...]


@dataclass(frozen=True)
class ShortSupports:
    model: Model
    ordinary: frozenset[int]
    linear: frozenset[int]
    mixed: frozenset[int]
    short_cuts: int
    affine_words: int
    cut_vertex_limit: int


def bits(mask: int):
    while mask:
        least = mask & -mask
        yield least.bit_length() - 1
        mask ^= least


def name(wire: Wire) -> str:
    point, axis = wire
    return "xyz"[axis] + ",".join(map(str, point))


def model_at(stage: int) -> Model:
    if stage < 4:
        raise ValueError("The aligned model starts once both ends of every marked bit are used")
    vertices = tuple(sorted(
        (point for point in product(range(stage + 1), repeat=3) if sum(point) <= stage),
        key=lambda point: (sum(point), point),
    ))
    vertex_ids = {point: index for index, point in enumerate(vertices)}
    outside = len(vertices)
    wires = tuple((point, axis) for point in vertices for axis in range(3))
    adjacency = [[] for _ in range(outside + 1)]
    stars = [0] * outside
    endpoints = []
    for wire, (point, axis) in enumerate(wires):
        target = tuple(x + y for x, y in zip(point, AXES[axis]))
        left, right = vertex_ids[point], vertex_ids.get(target, outside)
        mask = 1 << wire
        adjacency[left].append((right, mask))
        adjacency[right].append((left, mask))
        stars[left] |= mask
        if right != outside:
            stars[right] |= mask
        endpoints.append((left, right))
    marked = tuple(wires.index((point, 2)) for point in MARK_VERTICES)
    assert all(endpoints[bit][1] != outside for bit in marked)
    return Model(vertices, wires, tuple(endpoints), tuple(map(tuple, adjacency)), tuple(stars), marked)


def mask_of(indices) -> int:
    return sum(1 << index for index in indices)


def component_cuts(model: Model, removed: int) -> tuple[int, ...]:
    """Return the boundaries of connected components separated from the exterior."""
    outside = len(model.vertices)
    unseen = set(range(outside + 1))
    boundaries = []
    for root in (outside, *range(outside)):
        if root not in unseen:
            continue
        unseen.remove(root)
        component, pending = [root], [root]
        while pending:
            for neighbor, edge in model.adjacency[pending.pop()]:
                if neighbor in unseen and not removed & edge:
                    unseen.remove(neighbor)
                    pending.append(neighbor)
                    component.append(neighbor)
        if root != outside:
            boundary = reduce(xor, (model.stars[vertex] for vertex in component), 0)
            assert boundary & ~removed == 0
            boundaries.append(boundary)
    return tuple(boundaries)


def small_cuts(model: Model) -> tuple[dict[int, int], int]:
    marked = mask_of(model.mark_bits)
    # One positive exit per occupied coordinate line. Only the four marked
    # vertical lines can lose an exit. Discrete Loomis–Whitney bounds |U|² by
    # the product of the three projection sizes, whose sum is at most 10.
    budget = SUPPORT_LIMIT + 4
    volume = isqrt(max(a * b * (budget - a - b)
                      for a in range(1, budget) for b in range(1, budget - a)))
    assert volume == 6
    neighbors = tuple(
        mask_of(neighbor for neighbor, edge in incident
                if neighbor < len(model.vertices) and not edge & marked)
        for incident in model.adjacency[:-1]
    )
    frontier = {1 << vertex for vertex in range(len(model.vertices))}
    parts = []
    for size in range(1, volume + 1):
        following = set()
        for members in frontier:
            adjacent = reduce(or_, (neighbors[vertex] for vertex in bits(members)), 0)
            cut = reduce(xor, (model.stars[vertex] for vertex in bits(members)), 0)
            unmarked_size = (cut & ~marked).bit_count()
            if unmarked_size <= SUPPORT_LIMIT:
                parts.append((members, adjacent, cut, unmarked_size))
            if size < volume:
                following.update(members | (1 << vertex) for vertex in bits(adjacent & ~members))
        frontier = following
    parts.sort(key=lambda item: (item[3], item[0]))
    cuts = {0: 0}
    # A disconnected support has uniquely determined unmarked components.
    # Their unmarked cut costs add, while the marked portions still XOR.
    def collect(start: int, members: int, forbidden: int, cut: int, cost: int) -> None:
        for index in range(start, len(parts)):
            component, adjacent, boundary, length = parts[index]
            if cost + length > SUPPORT_LIMIT:
                break
            if component & forbidden or (members | component).bit_count() > volume:
                continue
            joined = members | component
            combined = cut ^ boundary
            assert joined not in cuts
            cuts[joined] = combined
            collect(index + 1, joined, forbidden | component | adjacent, combined, cost + length)
    collect(0, 0, 0, 0, 0)
    return cuts, volume


def embed(word: int, positions: tuple[int, ...]) -> int:
    return mask_of(positions[index] for index in bits(word))


def minimal_supports(candidates: set[int]) -> frozenset[int]:
    minimal = set()
    for word in sorted(candidates - {0}, key=lambda mask: (mask.bit_count(), mask)):
        smaller = (word - 1) & word
        while smaller and smaller not in minimal:
            smaller = (smaller - 1) & word
        if not smaller:
            minimal.add(word)
    return frozenset(minimal)


def short_supports(stage: int) -> ShortSupports:
    """Return all actual minimal supports of size at most six, as wire bitmasks."""
    model = model_at(stage)
    marked = mask_of(model.mark_bits)
    assert not component_cuts(model, marked)
    cuts, limit = small_cuts(model)
    mark_masks = tuple(embed(word, model.mark_bits) for word in range(256))
    mark_coordinates = {word: i for i, word in enumerate(mark_masks)}
    signatures = tuple(
        ((word.bit_count() & 1) << 3)
        | sum(((word & direction).bit_count() & 1) << axis
              for axis, direction in enumerate(CUT_DIRECTIONS))
        for word in range(256)
    )
    words = {}
    for cut in cuts.values():
        other = cut & ~marked
        retained = mark_coordinates[cut & marked]
        available = SUPPORT_LIMIT - other.bit_count()
        for word, mask in enumerate(mark_masks):
            if word.bit_count() <= available:
                check = other | mask
                syndrome = signatures[retained ^ word]
                assert words.setdefault(check, syndrome) == syndrome
    by_signature = defaultdict(set)
    for word, syndrome in words.items():
        by_signature[syndrome].add(word)
    mixed = set(by_signature[0])
    # The constant part of the cut row is free. Among even syndromes,
    # a two-dimensional observation is free only for the even-weight plane.
    # Every larger obstruction therefore contains one of these bad planes.
    for plane in sorted(map(sorted, BAD_PLANES)):
        first, second, _ = sorted(plane, key=lambda code: len(by_signature[code]))
        for left, right in product(by_signature[first], by_signature[second]):
            joined = left | right
            if joined.bit_count() <= SUPPORT_LIMIT:
                mixed.add(joined)
    return ShortSupports(
        model,
        minimal_supports({word for word in cuts.values() if word.bit_count() <= SUPPORT_LIMIT}),
        minimal_supports(by_signature[0]),
        minimal_supports(mixed),
        len(cuts),
        len(words),
        limit,
    )


def threshold_matrix(width: int, supports: frozenset[int]) -> list[list[int]]:
    out = [[SENTINEL] * width for _ in range(width)]
    for i in range(width):
        out[i][i] = 0
    for support in supports:
        distance = support.bit_count() - 1
        for left, right in combinations(bits(support), 2):
            out[left][right] = out[right][left] = min(out[left][right], distance)
    return out


def truncated_table(stage: int) -> dict[tuple[Wire, Wire], int]:
    """Return actual distances through five, with 6 denoting any larger value."""
    data = short_supports(stage)
    size = len(data.model.wires)
    matrix = threshold_matrix(size, data.mixed)
    return {(data.model.wires[i], data.model.wires[j]): matrix[i][j]
            for i, j in combinations(range(size), 2)}


def projected_rows(model: Model, support: int) -> frozenset[int]:
    """Check a projection directly by component parity, independently of short-cut search."""
    retained = tuple(bits(support))
    marked = mask_of(model.mark_bits)
    common = support & marked
    constraints = component_cuts(model, support | marked)
    old_words = tuple(embed(word, model.mark_bits) for word in sorted(CUT_WORDS))
    allowed = set()
    for ordinal in range(1 << len(retained)):
        fixed = embed(ordinal, retained)
        for old in old_words:
            if (fixed ^ old) & common:
                continue
            if all(not (parity & (fixed | old)).bit_count() & 1 for parity in constraints):
                allowed.add(ordinal)
                break
    return frozenset(allowed)


def verify_projections(data: ShortSupports) -> dict:
    checked = {}
    canonical = set()
    for support in sorted(data.mixed):
        rows = checked.setdefault(support, projected_rows(data.model, support))
        arity = support.bit_count()
        assert 0 < len(rows) < (1 << arity)
        for bit in bits(support):
            deletion = support ^ (1 << bit)
            if deletion not in checked:
                checked[deletion] = projected_rows(data.model, deletion)
            assert len(checked[deletion]) == 1 << (arity - 1)
        key = arity, support not in data.linear
        if arity < 3 or key in canonical:
            continue
        labels = tuple(name(data.model.wires[index]) for index in bits(support))
        values = frozenset(tuple(bool(row & (1 << i)) for i in range(arity)) for row in rows)
        assert check_knot(Relation(labels, values), labels[:-1], labels[-1]).is_knot
        canonical.add(key)
    return {
        "validated_minimal_supports": len(data.mixed),
        "independent_projections_checked": len(checked),
        "canonical_knot_checks": sorted(canonical),
    }


def twins(matrix: list[list[int]]) -> list[tuple[int, ...]]:
    pending = set(range(len(matrix)))
    out = []
    while pending:
        root = min(pending)
        group = tuple(x for x in sorted(pending)
                      if all(matrix[root][z] == matrix[x][z]
                             for z in range(len(matrix)) if z not in (root, x)))
        pending.difference_update(group)
        out.append(group)
    return out


def quotient_isometries(matrix: list[list[int]], groups: list[tuple[int, ...]]):
    size = len(groups)
    quotient = [[matrix[left[0]][right[0]] for right in groups] for left in groups]

    def colors(values):
        names = {value: i for i, value in enumerate(sorted(set(values)))}
        return [names[value] for value in values]

    shade = colors([(len(group), matrix[group[0]][group[-1]]) for group in groups])
    while True:
        refined = colors([(shade[i], tuple(sorted((shade[j], quotient[i][j])
                                                 for j in range(size) if j != i)))
                          for i in range(size)])
        if len(set(refined)) == len(set(shade)):
            shade = refined
            break
        shade = refined
    graph = nx.Graph()
    graph.add_nodes_from((index, {"color": code}) for index, code in enumerate(shade))
    graph.add_weighted_edges_from((i, j, quotient[i][j]) for i, j in combinations(range(size), 2)
                                  if quotient[i][j] < SENTINEL)
    matcher = nx.algorithms.isomorphism.GraphMatcher(
        graph, graph, node_match=lambda a, b: a == b, edge_match=lambda a, b: a == b
    )
    yield from matcher.isomorphisms_iter()


def grade_isometries(model: Model, matrix: list[list[int]]) -> dict:
    assert hashlib.sha256(SOURCE.read_bytes()).hexdigest() == SOURCE_DIGEST
    spec = importlib.util.spec_from_file_location("cubic_rules", SOURCE)
    rules = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(rules)
    checks = {str(index): tuple(map(str, bits(star))) for index, star in enumerate(model.stars)}
    loose = rules.loose_ports(rules.incidence(checks)[0])
    triplets = {frozenset(map(int, wires)) for wires in loose.values()}
    assert all(len(group) == 3 for group in triplets)
    parent_groups, _ = rules.parent_groups(checks)
    parallel = {frozenset(frozenset(map(int, loose[parent])) for parent in group)
                for group in parent_groups}
    assert len(parent_groups) == len(parallel)
    literal = set()
    serial_parent_pairs = []
    for count in (1, 2, 3):
        for parents in combinations(loose, count):
            if rules.legal_local_move(checks, tuple(loose[parent][0] for parent in parents), FRESH):
                literal.update(frozenset(map(int, group))
                               for group in product(*(loose[parent] for parent in parents)))
                if count == 2:
                    serial_parent_pairs.append([
                        sorted(name(model.wires[int(bit)]) for bit in loose[parent])
                        for parent in parents
                    ])

    groupings = twins(matrix)
    quotient_count, tested = 0, 0
    defects = {}
    wire_ids = range(len(model.wires))

    def test(permutation: list[int]) -> None:
        nonlocal tested
        tested += 1
        assert all(matrix[i][j] == matrix[permutation[i]][permutation[j]]
                   for i, j in combinations(wire_ids, 2))

        def image(members):
            return frozenset(permutation[bit] for bit in members)

        for label, original, moved in (
            ("boundary_triplet", triplets, {image(group) for group in triplets}),
            ("literal_serial", literal, {image(group) for group in literal}),
            ("parallel_group", parallel,
             {frozenset(image(triplet) for triplet in group) for group in parallel}),
        ):
            if original != moved and label not in defects:
                defects[label] = [(name(model.wires[i]), name(model.wires[j]))
                                  for i, j in enumerate(permutation) if i != j]

    for group in groupings:
        for left, right in zip(group, group[1:]):
            permutation = list(wire_ids)
            permutation[left], permutation[right] = right, left
            test(permutation)
    for mapping in quotient_isometries(matrix, groupings):
        quotient_count += 1
        if all(i == j for i, j in mapping.items()):
            continue
        permutation = list(wire_ids)
        for left, right in mapping.items():
            for source, target in zip(groupings[left], groupings[right]):
                permutation[source] = target
        test(permutation)
    triple_twins = {frozenset(group) for group in groupings if len(group) == 3}
    return {
        "twin_class_sizes": dict(Counter(map(len, groupings))),
        "boundary_triplets": len(triplets),
        "boundary_triplets_in_exact_size_three_twin_classes": len(triplets & triple_twins),
        "false_size_three_twin_classes": sorted(
            sorted(name(model.wires[bit]) for bit in group) for group in triple_twins - triplets
        ),
        "serial_literal_groups_by_size": dict(Counter(map(len, literal))),
        "parallel_parent_groups_by_size": dict(Counter(map(len, parallel))),
        "quotient_automorphisms": quotient_count,
        "exact_automorphism_group_order": quotient_count * prod(factorial(len(g)) for g in groupings),
        "generators_checked": tested,
        "all_boundary_triplets_invariant": "boundary_triplet" not in defects,
        "all_serial_options_invariant": "literal_serial" not in defects,
        "all_parallel_groups_invariant": "parallel_group" not in defects,
        "truncated_cutoff_sufficient": not defects,
        "defects": defects,
        "grading_only": {
            "boundary": [
                {
                    "loose_triplet": sorted(name(model.wires[int(bit)]) for bit in wires),
                    "incoming": sorted(name(model.wires[bit]) for bit in bits(model.stars[int(parent)])
                                       if model.endpoints[bit][1] == int(parent)),
                }
                for parent, wires in loose.items()
            ],
            "legal_parent_pairs_as_triplets": serial_parent_pairs,
        },
    }


def run() -> dict:
    reports = {}
    for stage in (4, 5):
        data = short_supports(stage)
        size = len(data.model.wires)
        matrix = threshold_matrix(size, data.mixed)
        ordinary_table = threshold_matrix(size, data.ordinary)
        linear_table = threshold_matrix(size, data.linear)

        def roster(supports):
            return sorted(sorted(name(data.model.wires[i]) for i in bits(support))
                          for support in supports)

        reports[f"I{stage}"] = {
            "junctions": len(data.model.vertices),
            "distinctions": size,
            "cut_vertex_limit": data.cut_vertex_limit,
            "unmarked_short_vertex_cuts": data.short_cuts,
            "short_affine_words_including_zero": data.affine_words,
            "short_minimal_supports_by_size": dict(Counter(word.bit_count() for word in data.mixed)),
            "nonlinear_minimal_supports": roster(data.mixed - data.linear),
            "added_supports_relative_to_pure_parity": roster(data.mixed - data.ordinary),
            "removed_supports_relative_to_pure_parity": roster(data.ordinary - data.mixed),
            "pair_threshold_differences_from_pure": sum(
                matrix[i][j] != ordinary_table[i][j] for i, j in combinations(range(size), 2)
            ),
            "pair_threshold_differences_from_affine_hull": sum(
                matrix[i][j] != linear_table[i][j] for i, j in combinations(range(size), 2)
            ),
            "exact_threshold_histogram": dict(Counter(matrix[i][j]
                                                      for i, j in combinations(range(size), 2))),
            "projection_controls": verify_projections(data),
            "automorphism_controls": grade_isometries(data.model, matrix),
            "display_wires": [name(wire) for wire in data.model.wires],
            "upper_triangle_in_display_order": [matrix[i][i+1:] for i in range(size)],
        }
    compare = ("added_supports_relative_to_pure_parity", "removed_supports_relative_to_pure_parity")
    return {
        "intended_cutoff": SENTINEL - 1,
        "sentinel_for_larger_distances": SENTINEL,
        "defect_support_lists_identical_at_both_stages": all(
            reports["I4"][key] == reports["I5"][key] for key in compare
        ),
        "stages": reports,
    }


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, sort_keys=True))
