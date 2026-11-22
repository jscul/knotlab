"""Disjoint development fixtures for the observation path. This file never reads a draw."""

import json
import math
import random
import resource
import sys
import time
from collections import Counter
from fractions import Fraction
from itertools import combinations

from bonds import CycleBonds, NAEBonds
from prepare import knot_reading, main_observations, select_roots, shape_scale
from sources import CUBIC, PINWHEEL_NATIVE, PINWHEEL_ROUND, ROOT, cubic_pattern, distances
from sources import fold_pattern, load_record, pattern_from_knots, planar_pattern


def check_cubic():
    orig = load_record("cubic_replay", CUBIC / "check.py")
    pattern, births = cubic_pattern(5)
    before, before_births, _ = orig.grow_parallel(5)
    old_map = orig.recover_coordinates(before_births)
    new_maps = orig.recover_coordinates(births)
    actual = Counter(tuple(sorted(new_maps[knot] for knot in owners)) for owners in pattern.owners)
    assert actual == orig.point_incidence(before[-1], old_map)
    assert [len(level) for level in births] == [math.comb(i + 2, 2) for i in range(6)]
    inventory = cubic_pattern(9)[0]
    assert [[6, 0, [[0, 3], [1, 12]], [1] * 6]] * 2 in [
        knot_reading(inventory, root) for root in range(len(inventory.meeting))
    ]
    return {"rounds": 5, "distinctions": len(pattern.meeting), "local_interior_fixture": True}


def check_symbolic():
    native = load_record("native_reference", PINWHEEL_NATIVE / "native_lib.py")
    geometric = load_record("geometric_reference", PINWHEEL_ROUND / "sub_lib.py")
    level = 3
    _, rows = native.grow(level)
    tiles, _ = geometric.tiling_rule("pinwheel", level)
    graph = geometric.build_graph(tiles)
    pattern = planar_pattern("pinwheel", level)
    known = {}
    for endpoints, distinction in zip(pattern.segments, rows, strict=True):
        tile, side, start, stop = distinction["inc"][0]
        o, p, q = tiles[tile]
        left, right = {"S": (o, q), "L": (o, p), "H": (q, p)}[side]
        for endpoint, fraction in zip(endpoints, (start, stop), strict=True):
            point = tuple(Fraction(a) + fraction * (b - a) for a, b in zip(left, right))
            assert known.setdefault(endpoint, point) == point
    assert len(set(known.values())) == len(known)
    geometry = {frozenset(graph["coords"][i] for i in pair) for pair in graph["segs"]}
    assert {frozenset(known[i] for i in pair) for pair in pattern.segments} == geometry
    return {"level": level, "distinctions": len(geometry), "exact_endpoint_match": True}


def check_cycles():
    edges = [(0, 1), (1, 2), (2, 0), (1, 3), (2, 3), (3, 4), (4, 2)]
    pattern = pattern_from_knots([(0, 1, 2), (1, 3, 4), (4, 5, 6)], len(edges), segments=edges)
    solver = CycleBonds.from_pattern(pattern)
    cycles = []
    for count in range(3, len(edges) + 1):
        for support in combinations(range(len(edges)), count):
            degree = Counter(v for i in support for v in edges[i])
            if set(degree.values()) != {2}:
                continue
            adjacency = {i: set() for i in degree}
            for i in support:
                a, b = edges[i]
                adjacency[a].add(b)
                adjacency[b].add(a)
            if len(distances(adjacency, [next(iter(degree))])) == len(degree):
                cycles.append(set(support))
    for a, b in combinations(range(len(edges)), 2):
        expected = min((len(cycle) for cycle in cycles if {a, b} <= cycle), default=None)
        assert solver.least_cycle(a, b) == expected
    return {"pair_count": math.comb(len(edges), 2), "cycles": len(cycles)}


def check_fold():
    sys.path.insert(0, str(ROOT / "tools"))
    from knotlab import Relation, check_knot

    radii = (3, 5, 7)
    pattern = fold_pattern(12, 25)
    begin = time.perf_counter()
    oracle = NAEBonds(max(radii), random.Random("small fold-only fixture"))
    root = pattern.points.index((0, 0))
    _, rows = main_observations(pattern, root, None, oracle, radii)
    for row in rows:
        targets = {pattern.points[witness["target"]] for witness in row["proofs"]}
        r = row["r"]
        # Independent check against the terminal theorem's known positive supports.
        assert {(sign * r, y) for sign in (-1, 1) for y in range(-2, 3)} <= targets
        for item in row["proofs"]:
            support = item["support"]
            table = {tuple((bits >> i) & 1 for i in range(len(support))) for bits in item["realized_rows"]}
            names = tuple(map(str, support))
            knot = check_knot(Relation(names, frozenset(table)), names[:-1], names[-1])
            assert knot.is_knot
    oracle.solver.delete()
    return {"wall_seconds": time.perf_counter() - begin, "radii": list(radii),
            "queried": [row["queried"] for row in rows],
            "certified": [row["certified"] for row in rows], "unresolved": [row["unresolved"] for row in rows]}


def planar_resource_fixture(family, depth):
    begin = time.perf_counter()
    pattern = planar_pattern(family, depth)
    cycle = CycleBonds.from_pattern(pattern)
    setup = time.perf_counter() - begin
    radii = (3, 5, 7)
    shapes = (6, 9, 11)
    roots, margins, _ = select_roots(pattern, cycle, random.Random("development roots"), radii, shapes, count=1)
    readings = []
    for radius in shapes:
        matrix, details = shape_scale(pattern, cycle, margins, roots[0], radius,
                                      random.Random(f"development scale {radius}"))
        assert details["attempted"] == 66
        if matrix[1] is not None:
            first, second, *_ = details["selected"]
            assert matrix[1][0][1] == cycle.least_cycle(first, second) - 1
        for values in matrix[1:]:
            if values is None:
                continue
            for a, b, c in combinations(range(12), 3):
                three = sorted((values[a][b], values[a][c], values[b][c]))
                assert three[0] > 0 and three[2] <= three[0] + three[1]
        readings.append({key: value for key, value in details.items() if key not in ("selected", "pairs")})
    return {"source_depth": depth, "source_distinctions": len(pattern.meeting), "setup_wall_seconds": setup,
            "max_meeting_margin": max(margins.values()), "readings": readings}


def main():
    begin = time.perf_counter()
    results = {"cubic_round_reference": check_cubic(), "symbolic_reference": check_symbolic(),
               "cycles_by_enumeration": check_cycles(), "fold_support": check_fold(),
               "planar_resource": {"pinwheel_level_5": planar_resource_fixture("pinwheel", 5),
                                   "pinwheel_level_6": planar_resource_fixture("pinwheel", 6),
                                   "periodic_level_12": planar_resource_fixture("periodic", 12)}}
    results.update(total_wall_seconds=time.perf_counter() - begin,
                   peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    print(json.dumps(results, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
