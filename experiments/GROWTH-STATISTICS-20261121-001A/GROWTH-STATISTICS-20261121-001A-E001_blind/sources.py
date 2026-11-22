"""Reconstruct the terminal source laws, without putting source labels in any reading."""

from array import array
from collections import deque
from dataclasses import dataclass
from fractions import Fraction
from functools import cache
from importlib.util import module_from_spec, spec_from_file_location
from itertools import combinations, product
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
PROOFS = ROOT / "proofs"
PINWHEEL_NATIVE = PROOFS / "PINWHEEL-NATIVE-20261107-001A" / (
    "PINWHEEL-NATIVE-20261107-001A-P001_a_finite_rule_regrows_the_pinwheel"
)
PINWHEEL_ROUND = PROOFS / "PINWHEEL-ROUND-20261107-001A" / (
    "PINWHEEL-ROUND-20261107-001A-P001_isotropy_makes_circles_round"
)
CUBIC = PROOFS / "CUBIC-FROM-A-KNOT-20261117-001" / (
    "CUBIC-FROM-A-KNOT-20261117-001-P001_local_growth"
)
FOLD = PROOFS / "FOLD-20261112-001A" / (
    "FOLD-20261112-001A-P001_folded_direction"
)
FOLD_KINDS = (((0, 0), (0, 1), (1, 0)), ((0, 0), (0, 2), (1, 2)))
Point = tuple[int, int]


def load_record(name, path):
    spec = spec_from_file_location(name, path)
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def distances(adjacency, starts, limit=None):
    reached = {node: 0 for node in starts}
    queue = deque(reached)
    while queue:
        node = queue.popleft()
        steps = reached[node] + 1
        if limit is not None and steps > limit:
            continue
        for other in adjacency[node]:
            if other not in reached:
                reached[other] = steps
                queue.append(other)
    return reached


@dataclass
class Pattern:
    knots: list[tuple[int, ...]]
    owners: list[list[int]]
    meeting: list[tuple[int, ...]]
    truncated: list[int]
    segments: list[tuple[int, int]] | None = None
    points: list[Point] | None = None


def pattern_from_knots(knots, size, truncated=None, segments=None, points=None):
    owners = [[] for _ in range(size)]
    for i, knot in enumerate(knots):
        if len(set(knot)) != len(knot):
            raise ValueError("A knot repeats a distinction")
        for distinction in knot:
            owners[distinction].append(i)
    meeting = [tuple({other for knot in rows for other in knots[knot] if other != i}) for i, rows in enumerate(owners)]
    if truncated is None:
        truncated = [i for i, rows in enumerate(owners) if len(rows) == 1]
    return Pattern(knots, owners, meeting, truncated, segments, points)


def cubic_groups(live, neighbors):
    """Use the accepted parallel policy with the common-neighbor census indexed locally."""
    candidates = {}
    for a in live:
        two_steps = set().union(*(neighbors[b] for b in neighbors[a]))
        candidates[a] = (two_steps & live) - {a}
    triples = []
    pairs_used = set()
    pairs = []
    for a in sorted(live):
        for b in sorted(candidates[a]):
            if b <= a:
                continue
            pairs.append((a, b))
            for c in sorted(candidates[a] & candidates[b]):
                if c > b and not (neighbors[a] & neighbors[b] & neighbors[c]):
                    group = (a, b, c)
                    triples.append(group)
                    pairs_used.update(combinations(group, 2))
    return [*triples, *(pair for pair in pairs if pair not in pairs_used)]


def cubic_pattern(depth):
    checks = [(0, 1, 2)]
    available = {0: [0, 1, 2]}
    neighbors = [set()]
    births = [{0: ()}]
    next_distinction = 3
    for _ in range(depth):
        groups = cubic_groups(set(available), neighbors)
        demand = dict.fromkeys(available, 0)
        for group in groups:
            for parent in group:
                demand[parent] += 1
        groups.extend((parent,) for parent in sorted(available) for _ in range(3 - demand[parent]))
        new_available = {}
        born = {}
        for group in groups:
            child = len(checks)
            old = tuple(available[parent].pop() for parent in group)
            fresh = list(range(next_distinction, next_distinction + 3))
            next_distinction += 3
            checks.append(old + tuple(fresh))
            new_available[child] = fresh
            born[child] = group
            neighbors.append(set(group))
            for parent in group:
                neighbors[parent].add(child)
        if any(available.values()):
            raise ValueError("The complete-round rule left an open distinction")
        available = new_available
        births.append(born)
    return pattern_from_knots(checks, next_distinction), births


def symbolic_segments(count, distinctions):
    """Recover which ends of distinctions are identified by the recorded subdivision."""
    positions = {("S", 0): 0, ("L", 0): 0, ("S", 1): 1, ("H", 0): 1,
                 ("L", 1): 2, ("H", 1): 2, ("L", Fraction(1, 2)): 3}
    parents = array("i", range(4 * count))

    def representative(key):
        while key != parents[key]:
            parents[key] = parents[parents[key]]
            key = parents[key]
        return key

    endpoints = []
    incidences = [[] for _ in range(count)]
    for distinction, row in enumerate(distinctions):
        ends = []
        for knot, role, first, last in row["inc"]:
            ends.append((4 * knot + positions[role, first], 4 * knot + positions[role, last]))
            incidences[knot].append(distinction)
        endpoints.append(ends[0])
        if len(ends) == 2:
            matching = ends[1] if row["aligned"] else ends[1][::-1]
            for a, b in zip(ends[0], matching, strict=True):
                parents[representative(a)] = representative(b)
    root_ids = {}
    segments = []
    for a, b in endpoints:
        a, b = representative(a), representative(b)
        segments.append((root_ids.setdefault(a, len(root_ids)), root_ids.setdefault(b, len(root_ids))))
    if any(a == b for a, b in segments) or len({(min(a, b), max(a, b)) for a, b in segments}) != len(segments):
        raise ValueError("The substitution did not produce a simple cycle graph")
    return pattern_from_knots(list(map(tuple, incidences)), len(segments), segments=segments)


def planar_pattern(family, depth):
    if family == "pinwheel":
        source = load_record("symbolic_pinwheel", PINWHEEL_NATIVE / "native_lib.py")
        split = source.split_seg

        @cache
        def split_by_label(roles, alignment):
            return split({"inc": [(i, *role) for i, role in enumerate(roles)], "aligned": alignment})

        def cached_split(row):
            return split_by_label(tuple((s, a, b) for _, s, a, b in row["inc"]), row["aligned"])

        source.split_seg = cached_split
        hands, distinctions = source.grow(depth)
        return symbolic_segments(len(hands), distinctions)
    if family == "periodic":
        source = load_record("periodic_substitution", PINWHEEL_ROUND / "sub_lib.py")
        tiles, _ = source.tiling_rule("isosceles", depth)
        graph = source.build_graph(tiles)
        knots = [[] for _ in tiles]
        for distinction, owners in enumerate(graph["seg_tiles"]):
            for owner in owners:
                knots[owner].append(distinction)
        return pattern_from_knots(list(map(tuple, knots)), len(graph["segs"]), segments=graph["segs"])
    raise ValueError(f"Unknown substitution {family}")


def fold_knots(x_limit, y_limit):
    """The source's two translated NAE knots, on a finite observation window."""
    points = list(product(range(-x_limit, x_limit + 1), range(-y_limit, y_limit + 1)))
    index = {point: i for i, point in enumerate(points)}
    knots = []
    for x, y in points:
        for kind in FOLD_KINDS:
            positions = tuple((x + dx, y + dy) for dx, dy in kind)
            if all(point in index for point in positions):
                knots.append(tuple(index[point] for point in positions))
    return points, knots


def fold_pattern(x_limit, y_limit):
    points, knots = fold_knots(x_limit, y_limit)
    # A distinction with fewer than its six occurrences may meet further knots outside.
    pattern = pattern_from_knots(knots, len(points), points=points)
    pattern.truncated = [i for i, rows in enumerate(pattern.owners) if len(rows) < 6]
    return pattern
