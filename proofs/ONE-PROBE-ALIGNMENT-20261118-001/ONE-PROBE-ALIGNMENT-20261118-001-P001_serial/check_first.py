"""Exact anonymous readout of one temporary betweenness probe.

The matrix and its isometries receive only the joint allowed rows. Original,
root-port and probe identities enter afterward to grade possible actions.
"""

from collections import Counter, defaultdict
from dataclasses import dataclass
from functools import cache
from importlib.util import module_from_spec, spec_from_file_location
from itertools import combinations, permutations, product
import json
from math import factorial, prod
from pathlib import Path
from random import Random


PREDECESSOR = (
    "proofs/BOOTSTRAP-ALIGNMENT-20261117-001/"
    "BOOTSTRAP-ALIGNMENT-20261117-001-P001_distance_start/check_seed.py"
)
OLD = tuple(range(8))
ROOT_OUTPUTS = (8, 9)


@cache
def seed_checker():
    path = Path(__file__).resolve().parents[3] / PREDECESSOR
    spec = spec_from_file_location("bootstrap_literal_seed", path)
    source = module_from_spec(spec)
    spec.loader.exec_module(source)
    return source


def full_matrix(rows, width):
    """Packed rows, low bit first. Return a tuple matrix, with None for infinity."""
    return seed_checker().bond_table(rows, width)[0]


def probe_extension(rows, width, pair):
    """Adjoin fresh p,q satisfying both B(p,a,q) and B(p,b,q)."""
    a, b = (1 << i for i in pair)
    return frozenset(
        row | (p << width) | (q << (width + 1))
        for row in rows for p, q in product(range(2), repeat=2)
        if p != q or (bool(row & a) == bool(row & b) == p)
    )


def check_projections(rows, base, width):
    mask = (1 << width) - 1
    assert {row & mask for row in rows} == base
    opposites = {row | (1 << i) for row in base for i in (width, width + 1)}
    assert opposites <= rows
    columns = [tuple(bool(row & (1 << i)) for row in rows) for i in range(width + 2)]
    assert all(set(column) == {False, True} for column in columns)
    assert all(len(set(zip(a, b))) == 4 for a, b in combinations(columns, 2))


def reordered(matrix, order):
    return tuple(tuple(matrix[a][b] for b in order) for a in order)


@dataclass(frozen=True)
class CanonicalTable:
    matrix: tuple
    name_map: tuple
    blocks: tuple
    block_maps: tuple

    @property
    def permutations(self):
        return len(self.block_maps) * prod(factorial(len(block)) for block in self.blocks)


def canonical_table(matrix):
    """Compress exact distance twins, then exhaust the colored quotient permutations."""
    width = len(matrix)
    twins = []
    for i in range(width):
        for block in twins:
            j = block[0]
            if all(matrix[i][k] == matrix[j][k] for k in range(width) if k not in (i, j)):
                block.append(i)
                break
        else:
            twins.append([i])

    def color(i, j):
        distance = matrix[i][j]
        return width if distance is None else distance

    colors = [(len(block), color(*block[:2]) if len(block) > 1 else 0) for block in twins]
    links = [[color(a[0], b[0]) for b in twins] for a in twins]
    groups = defaultdict(list)
    for i, key in enumerate(colors):
        profile = tuple(sorted((other, links[i][j]) for j, other in enumerate(colors) if i != j))
        groups[key, profile].append(i)
    best_key = None
    best_orders = []
    for parts in product(*(permutations(groups[key]) for key in sorted(groups))):
        order = tuple(i for part in parts for i in part)
        key = tuple(links[i][j] for i, j in combinations(order, 2))
        if best_key is None or key < best_key:
            best_key, best_orders = key, [order]
        elif key == best_key:
            best_orders.append(order)

    order = best_orders[0]
    block_maps = tuple(tuple(order.index(i) for i in variant) for variant in best_orders)
    names = tuple(i for j in order for i in twins[j])
    name_map = tuple(names.index(i) for i in range(width))
    blocks = tuple(tuple(name_map[i] for i in twins[j]) for j in order)
    return CanonicalTable(reordered(matrix, names), name_map, blocks, block_maps)


def action_orbits(table, arity, ordered=False):
    """Permutations within each twin block act freely on distinct action positions."""
    width = len(table.matrix)
    block_of = {name: j for j, block in enumerate(table.blocks) for name in block}
    choices = permutations(range(width), arity) if ordered else combinations(range(width), arity)
    orbits = defaultdict(set)
    for action in choices:
        images = [tuple(mapping[block_of[i]] for i in action) for mapping in table.block_maps]
        key = min(images) if ordered else min(tuple(sorted(image)) for image in images)
        orbits[key].add(action)
    return sorted(orbits.values(), key=min)


def step_distance(chart, a, b):
    return (chart[a] ^ chart[b]).bit_count()


def probe_type(chart, root, pair):
    a, b = pair
    if root is None:
        return "old pair", f"steps {step_distance(chart, a, b)}"
    if b < 8:
        if root in pair:
            kind = "root and unused original"
        else:
            kind = "two unused originals"
        common = 7 ^ (chart[a] ^ chart[b])
        meets = not ((chart[a] ^ chart[root]) & common)
        return kind, f"steps {step_distance(chart, a, b)}, root in interval {meets}"
    if a >= 8:
        return "two root outputs", "two root outputs"
    if a == root:
        return "root and root output", "root and root output"
    return "unused original and root output", f"steps from root {step_distance(chart, root, a)}"


def phase_roles(root):
    if root is None:
        return {i: "original" for i in OLD} | {8: "probe endpoint", 9: "probe endpoint"}
    return ({i: "unused original" for i in OLD} | {root: "root"}
            | dict.fromkeys(ROOT_OUTPUTS, "root output")
            | {10: "probe endpoint", 11: "probe endpoint"})


def graders(chart, root, width):
    if root is None:
        connected = {(a, b) for a, b in permutations(OLD, 2) if step_distance(chart, a, b) == 1}
    else:
        connected = {(a, b) for a in (root, *ROOT_OUTPUTS) for b in OLD
                     if step_distance(chart, root, b) == 1}
    return {
        "connected": connected,
        "erase": {(width, width + 1)},
        "originals": {(i,) for i in OLD},
        "root": {(root,)} if root is not None else set(),
    }


class ObservationClass:
    def __init__(self, table, fixture):
        self.table = table
        self.fixture = fixture
        self.orbits = {
            "connected": action_orbits(table, 2, ordered=True),
            "erase": action_orbits(table, 2),
            "originals": action_orbits(table, 1),
            "root": action_orbits(table, 1),
        }
        self.bounds = {kind: [[len(orbit), 0] for orbit in orbits]
                       for kind, orbits in self.orbits.items()}
        self.roles = [set() for _ in self.orbits["originals"]]
        self.placement_types = Counter()
        self.preprobe_types = Counter()
        self.rows = Counter()

    def grade(self, table, chart, root, width, pair, row_count):
        assert self.table.matrix == table.matrix and self.table.permutations == table.permutations
        names = table.name_map
        for kind, valid in graders(chart, root, width).items():
            transported = {tuple(names[i] for i in action) for action in valid}
            if kind == "erase":
                transported = {tuple(sorted(action)) for action in transported}
            for orbit, bounds in zip(self.orbits[kind], self.bounds[kind], strict=True):
                matched = len(orbit & transported)
                bounds[0], bounds[1] = min(bounds[0], matched), max(bounds[1], matched)
        roles = {names[i]: role for i, role in phase_roles(root).items()}
        for orbit, observed in zip(self.orbits["originals"], self.roles, strict=True):
            observed.update(roles[i] for (i,) in orbit)
        query, details = probe_type(chart, root, pair)
        self.preprobe_types[query] += 1
        self.placement_types[f"{query}: {details}"] += 1
        self.rows[row_count] += 1

    def possible(self, kind):
        return [{"representative": min(orbit), "orbit_size": len(orbit),
                 "min_and_max_legal_members": bounds}
                for orbit, bounds in zip(self.orbits[kind], self.bounds[kind], strict=True) if bounds[1]]

    def safe(self, kind):
        return sum(len(orbit) for orbit, bounds in zip(self.orbits[kind], self.bounds[kind], strict=True)
                   if bounds[0] == len(orbit))

    def report(self):
        return {
            "matrix": self.table.matrix,
            "isometry_count": self.table.permutations,
            "twin_blocks": self.table.blocks,
            "quotient_isometries": self.table.block_maps,
            "vertex_orbits": [{"members": sorted(i for (i,) in orbit), "possible_roles": sorted(roles)}
                              for orbit, roles in zip(self.orbits["originals"], self.roles, strict=True)],
            "connected_action_orbits_with_some_legal_members": self.possible("connected"),
            "erasure_orbits_with_some_legal_members": self.possible("erase"),
            "guaranteed_choice_counts": {kind: self.safe(kind) for kind in self.orbits},
            "tested_placements": sum(self.rows.values()),
            "placement_types": dict(self.placement_types),
            "states_by_count": dict(self.rows),
            "representative_fixture": self.fixture,
        }


def gauges(source, old_rows):
    for reference in (0, *source.AXES):
        axes = [axis ^ reference if reference and axis != reference else axis for axis in source.AXES]
        chart = tuple(sum(((point & axis).bit_count() % 2) << (2 - j)
                          for j, axis in enumerate(axes)) for point in OLD)
        flip = sum(int(bool(point & reference)) << point for point in OLD)
        rows = frozenset(row ^ flip for row in old_rows)
        assert len(set(chart)) == 8 and rows == source.cut_words(chart)
        yield reference, chart, rows


def matrix_witnesses(control):
    checks = {}
    for label, root, probe, original in (("bare_antipodes", None, 8, 1), ("rooted_antipodes", 0, 10, 1)):
        matrix = control[root, (0, 7)]
        swap = list(range(len(matrix)))
        swap[probe], swap[original] = swap[original], swap[probe]
        assert reordered(matrix, swap) == matrix
        checks[label] = {"queried_old_pair": (0, 7), "fixed_root": root,
                         "distance_preserving_probe_to_original_swap": (probe, original)}

    # A diagonal probe can be erased. It leaves a true neighbor and a
    # nonneighbor exchangeable even while fixing the root and probe endpoints.
    for label, root in (("bare_diagonal", None), ("rooted_diagonal", 0)):
        matrix = control[root, (0, 3)]
        swap = list(range(len(matrix)))
        swap[1], swap[3] = swap[3], swap[1]
        assert reordered(matrix, swap) == matrix
        checks[label] = {"queried_old_pair": (0, 3), "fixed_vertex": 0,
                         "distance_preserving_neighbor_to_nonneighbor_swap": (1, 3)}

    star = control[0, (8, 9)]
    assert star == control[0, (0, 8)] == control[0, (0, 9)]
    swap = (*OLD, 10, 11, 8, 9)
    assert reordered(star, swap) == star
    checks["root_star_collision"] = {"same_labeled_matrix_for_probe_pairs": ((8, 9), (0, 8), (0, 9)),
                                     "isometry_swapping_real_and_temporary_pairs": swap}

    good, mixed = control[0, (0, 1)], control[0, (1, 8)]
    good_counts, mixed_counts = (Counter(matrix[i][j] for i, j in combinations(range(len(matrix)), 2))
                                for matrix in (good, mixed))
    assert good_counts == mixed_counts
    assert canonical_table(good).matrix != canonical_table(mixed).matrix
    checks["same_histogram_distinct_tables"] = {"root": 0, "probe_pairs": ((0, 1), (1, 8)),
                                                "entries_by_distance": dict(good_counts)}
    return checks


def main():
    source = seed_checker()
    old_rows = source.seed_rows()[0]
    classes = {"bare": {}, "rooted": {}}
    control = {}
    projection_controls = Counter()
    for gauge, chart, rows in gauges(source, old_rows):
        for root in (None, *OLD):
            phase = "bare" if root is None else "rooted"
            base = rows if root is None else source.parity_extension(rows, 8, (root,))
            width = 8 if root is None else 10
            for pair in combinations(range(width), 2):
                extended = probe_extension(base, width, pair)
                check_projections(extended, base, width)
                projection_controls["unary"] += width + 2
                projection_controls["binary"] += (width + 2) * (width + 1) // 2
                matrix, supports = source.bond_table(extended, width + 2)
                table = canonical_table(matrix)
                if gauge == 0 and root in (None, 0):
                    control[root, pair] = matrix
                entry = classes[phase].get(table.matrix)
                if entry is None:
                    witness = {"gauge": gauge, "root": root, "probe_inputs": pair, "canonical_names": table.name_map,
                               "allowed_rows": len(extended), "bonds_by_support_size": dict(Counter(map(len, supports)))}
                    entry = classes[phase][table.matrix] = ObservationClass(table, witness)
                entry.grade(table, chart, root, width, pair, len(extended))

    anonymous = {}
    outcomes = {}
    rng = Random(1597)
    for phase, cases in classes.items():
        anonymous[phase] = []
        totals = defaultdict(Counter)
        for case in cases.values():
            matrix = case.table.matrix
            for _ in range(2):
                names = list(range(len(matrix)))
                rng.shuffle(names)
                transported = canonical_table(reordered(matrix, names))
                assert transported.matrix == matrix and transported.permutations == case.table.permutations
            anonymous[phase].append(case.report())
            for query, count in case.preprobe_types.items():
                totals[query]["placements"] += count
                totals[query]["safe_connected_action"] += count if case.safe("connected") else 0
                totals[query]["safe_erasure"] += count if case.safe("erase") else 0
        outcomes[phase] = dict(totals)

    # Independently use the repository K1–K3 checker on one case per phase,
    # including a rooted, four-distance witness with no three- or four-bit bond.
    bare = probe_extension(old_rows, 8, (0, 3))
    rooted = source.parity_extension(old_rows, 8, (0,))
    remote = probe_extension(rooted, 10, (1, 3))
    assert full_matrix(remote, 12)[8][10] == 4
    control_counts = {}
    for phase, rows, width in (("bare", bare, 10), ("rooted", remote, 12)):
        control_counts[phase] = source.check_oracle(rows, width, source.bond_table(rows, width)[1])

    return {
        "source": PREDECESSOR,
        "original_common_value_gauges_checked": 4,
        "unary_and_binary_projections_confirmed_full": dict(projection_controls),
        "canonical_knot_tool_confirmed_bonds_in_controls": control_counts,
        "two_random_renamings_per_class_checked": True,
        "observation_classes": anonymous,
        "outcomes_by_preprobe_pair_orbit": outcomes,
        "explicit_matrix_witnesses": matrix_witnesses(control),
    }


if __name__ == "__main__":
    print(json.dumps(main(), indent=2, sort_keys=True))
