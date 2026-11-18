"""Finite calibration of the scalar distance reader on legal parity rearrangements."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from collections import Counter, defaultdict
from dataclasses import dataclass
from itertools import combinations, product
from pathlib import Path
from random import Random

import networkx as nx

ROOT = Path(__file__).resolve().parents[3]
SOURCE = (
    ROOT / "proofs" / "CUBIC-FROM-A-KNOT-20261117-001"
    / "CUBIC-FROM-A-KNOT-20261117-001-P001_local_growth" / "check.py"
)
SOURCE_SHA256 = "038a6845675cbc158e1abd0b55e72addd935c4dee9e6bb8153abe82a543894e8"
SEEDS = (113, 271)
FRESH = ("new-a", "new-b", "new-c")
Star = frozenset[str]
Pair = tuple[str, str]
Table = dict[Pair, int]


@dataclass(frozen=True)
class Fixture:
    edges: tuple[tuple[int, int], ...]
    loose: tuple[int, ...]
    history: tuple[tuple[int, ...], ...]


def load_rule():
    assert hashlib.sha256(SOURCE.read_bytes()).hexdigest() == SOURCE_SHA256
    spec = importlib.util.spec_from_file_location("cubic_rules", SOURCE)
    rules = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(rules)
    return rules


def incidence_graph(fixture: Fixture) -> nx.Graph:
    graph = nx.Graph()
    graph.add_nodes_from((index, {"loose": count}) for index, count in enumerate(fixture.loose))
    graph.add_edges_from(fixture.edges)
    return graph


def descendants(fixture: Fixture):
    graph = incidence_graph(fixture)
    neighbors = {vertex: set(graph[vertex]) for vertex in graph}
    front = tuple(vertex for vertex, count in enumerate(fixture.loose) if count)
    new_knot = len(fixture.loose)
    for size in (1, 2, 3):
        for parents in combinations(front, size):
            if any(not neighbors[a] & neighbors[b] for a, b in combinations(parents, 2)):
                continue
            if size == 3 and set.intersection(*(neighbors[node] for node in parents)):
                continue
            loose = tuple(count - (i in parents) for i, count in enumerate(fixture.loose))
            yield Fixture(
                fixture.edges + tuple((parent, new_knot) for parent in parents),
                loose + (3,),
                fixture.history + (parents,),
            )


def reachable_layers(max_size: int):
    current = [Fixture((), (3,), ())]
    yield current, 0
    for _ in range(2, max_size + 1):
        following = []
        buckets = defaultdict(list)
        attempted = 0
        for fixture in current:
            for arrival in descendants(fixture):
                attempted += 1
                graph = incidence_graph(arrival)
                key = tuple(sorted((graph.degree(node), graph.nodes[node]["loose"]) for node in graph))
                bucket = buckets[key]
                if any(nx.is_isomorphic(graph, known, node_match=lambda a, b: a == b)
                       for known in bucket):
                    continue
                following.append(arrival)
                bucket.append(graph)
        current = following
        yield current, attempted


def graph_shape_count(fixtures: list[Fixture]) -> int:
    buckets = defaultdict(list)
    for fixture in fixtures:
        graph = incidence_graph(fixture)
        bucket = buckets[tuple(sorted(degree for _, degree in graph.degree()))]
        if not any(nx.is_isomorphic(graph, prior) for prior in bucket):
            bucket.append(graph)
    return sum(map(len, buckets.values()))


def named_checks(fixture: Fixture, seed: int) -> dict[str, tuple[str, ...]]:
    labels = [f"bit-{i:03d}" for i in range(3 * len(fixture.loose))]
    Random(seed).shuffle(labels)
    checks = {str(index): [] for index in range(len(fixture.loose))}
    for left, right in fixture.edges:
        bit = labels.pop()
        checks[str(left)].append(bit)
        checks[str(right)].append(bit)
    for vertex, count in enumerate(fixture.loose):
        checks[str(vertex)].extend(labels.pop() for _ in range(count))
    assert not labels
    return {vertex: tuple(bits) for vertex, bits in checks.items()}


def distance_table(checks: dict[str, tuple[str, ...]]) -> tuple[Table, Counter]:
    """Enumerate the dual row space independently of the decoder."""
    labels = sorted({name for bits in checks.values() for name in bits})
    positions = {bit: index for index, bit in enumerate(labels)}
    span = [0]
    for bits in checks.values():
        equation = sum(1 << positions[bit] for bit in bits)
        span += [row ^ equation for row in span]
    assert len(set(span)) == len(span) == 2 ** len(checks)
    minimal = []
    for equation in sorted(span[1:], key=lambda row: (row.bit_count(), row)):
        if all(equation & prior != prior for prior in minimal):
            minimal.append(equation)
    table = {}
    for equation in minimal:
        support = tuple(bit for index, bit in enumerate(labels) if equation & (1 << index))
        for pair in combinations(support, 2):
            table.setdefault(pair, len(support) - 1)
    assert len(table) == len(labels) * (len(labels) - 1) // 2
    return table, Counter(row.bit_count() for row in minimal)


def table_labels(table: Table) -> set[str]:
    return {bit for pair in table for bit in pair}


def normalize_distance_pairs(table: Table) -> Table:
    normalized = {}
    for (left, right), distance in table.items():
        pair = tuple(sorted((left, right)))
        if normalized.setdefault(pair, distance) != distance:
            raise ValueError(f"Conflicting distances for unordered pair {pair!r}")
    return normalized


def clique_stars(labels: set[str], edges: set[Pair]) -> set[Star]:
    graph = nx.Graph()
    graph.add_nodes_from(sorted(labels))
    graph.add_edges_from(sorted(edges))
    return {frozenset(clique) for clique in nx.find_cliques(graph) if len(clique) >= 3}


def star_pairs(stars: set[Star]) -> set[Pair]:
    return {pair for star in stars for pair in combinations(sorted(star), 2)}


def prune(edges: set[Pair], smaller: set[Star], support_size: int) -> set[Pair]:
    crossed = set()
    for first, second in combinations(smaller, 2):
        if first & second and len(first) + len(second) - 2 <= support_size:
            crossed.update(tuple(sorted(pair)) for pair in product(first - second, second - first))
    return edges - crossed


def read_stages(table: Table) -> dict[int, set[Star]]:
    table = normalize_distance_pairs(table)
    labels = table_labels(table)
    stars, stages = set(), {}
    for support_size in (3, 4, 5, 6):
        raw = {pair for pair, delta in table.items() if delta < support_size}
        stars = clique_stars(labels, prune(raw, stars, support_size))
        stages[support_size] = stars
    return stages


def recover_stars(table: Table) -> set[Star]:
    """Reconstruct the declared star roster from an anonymous scalar table."""
    return read_stages(table)[6]


def two_threshold_reader(table: Table) -> set[Star]:
    table = normalize_distance_pairs(table)
    labels = table_labels(table)
    little = clique_stars(labels, {pair for pair, delta in table.items() if delta <= 3})
    raw = {pair for pair, delta in table.items() if delta <= 5}
    return clique_stars(labels, prune(raw, little, 6))


def serial_options(rules, checks: dict[str, tuple[str, ...]]) -> set[tuple[str, ...]]:
    users, _ = rules.incidence(checks)
    loose = rules.loose_ports(users)
    for bit, owners in users.items():
        if len(owners) == 2:
            assert not rules.legal_local_move(checks, (bit,), FRESH)
    for bits in loose.values():
        assert not rules.legal_local_move(checks, (bits[0], bits[0]), FRESH)
        if len(bits) >= 2:
            assert not rules.legal_local_move(checks, tuple(bits[:2]), FRESH)
    allowed = set()
    for size in (1, 2, 3):
        for parents in combinations(sorted(loose), size):
            choices = [loose[parent] for parent in parents]
            # The original predicate reads only membership and the producing
            # knots. Distinct loose bits at one producer can substitute freely.
            if rules.legal_local_move(checks, tuple(bits[0] for bits in choices), FRESH):
                allowed.update(tuple(sorted(selection)) for selection in product(*choices))
    return allowed


def parallel_output(rules, checks: dict[str, tuple[str, ...]]) -> tuple[Counter | None, str | None]:
    try:
        groups, _ = rules.parent_groups(checks)
    except ValueError as blocked:
        return None, str(blocked)
    return Counter(tuple(sorted(tuple(sorted(checks[knot])) for knot in group)) for group in groups), None


def table_graph(table: Table) -> tuple[tuple, nx.Graph]:
    graph = nx.Graph()
    graph.add_weighted_edges_from((a, b, distance) for (a, b), distance in table.items())
    for node in graph:
        graph.nodes[node]["row_profile"] = tuple(sorted(data["weight"] for data in graph[node].values()))
    return tuple(sorted(nx.get_node_attributes(graph, "row_profile").values())), graph


def same_table(left: nx.Graph, right: nx.Graph) -> bool:
    return nx.is_isomorphic(left, right, node_match=lambda a, b: a == b, edge_match=lambda a, b: a == b)


def named_family(fixture: Fixture) -> dict:
    degrees = [degree for _, degree in incidence_graph(fixture).degree()]
    shape = {(1, 1, 1, 3): "star", (1, 1, 2, 2): "path", (2, 2, 2, 2): "four_cycle"}
    return {
        "shape": shape.get(tuple(sorted(degrees))),
        "shared_junction_pairs": fixture.edges,
        "loose_ports_by_junction": fixture.loose,
        "star_sizes_by_junction": [degree + loose for degree, loose in zip(degrees, fixture.loose)],
        "parent_sets_in_one_legal_history": fixture.history,
    }


def check_fixture(rules, fixture: Fixture) -> tuple[dict, tuple, nx.Graph]:
    readings = []
    for index, seed in enumerate(SEEDS):
        checks = named_checks(fixture, seed)
        truth = set(map(frozenset, checks.values()))
        table, minimal = distance_table(checks)
        stages = read_stages(table)
        location = f"history {fixture.history!r}, renaming seed {seed}"
        for size, stars in stages.items():
            expected = {star for star in truth if len(star) <= size}
            if stars != expected:
                raise AssertionError(
                    f"{location}: support threshold {size} recovered "
                    f"{len(stars - expected)} extra and {len(expected - stars)} missing stars"
                )
        if index == 1:
            truncated = {(right, left): min(distance, 6)
                         for (left, right), distance in table.items()}
            if recover_stars(truncated) != truth:
                raise AssertionError(f"{location}: reversed, truncated table gave different stars")
        recovered = stages[6]
        pilot = two_threshold_reader(table)
        labels = table_labels(table)
        raw = {pair for pair, delta in table.items() if delta <= 5}
        naive = clique_stars(labels, raw)
        possible = serial_options(rules, checks)
        parallel, block = parallel_output(rules, checks)
        recovered_checks = {
            f"recovered-{i}": bits for i, bits in enumerate(sorted(tuple(sorted(s)) for s in recovered))
        }
        decoded_serial = serial_options(rules, recovered_checks)
        decoded_parallel, decoded_block = parallel_output(rules, recovered_checks)
        if decoded_serial != possible:
            raise AssertionError(f"{location}: recovered serial options differ from the original")
        if (decoded_parallel, decoded_block) != (parallel, block):
            raise AssertionError(f"{location}: recovered parallel output differs from the original")
        row_key, graph = table_graph(table)
        if index == 0:
            reference_key, reference_graph = row_key, graph
        else:
            assert row_key == reference_key and same_table(graph, reference_graph)
        readings.append({
            "repaired_star_sets_exact": True,
            "all_stage_star_sets_exact": True,
            "serial_and_parallel_outputs_exact": True,
            "pilot_star_sets_exact": pilot == truth,
            "pilot_added_stars": len(pilot - truth),
            "pilot_missing_stars": len(truth - pilot),
            "naive_star_sets_exact": naive == truth,
            "naive_extra_adjacencies": len(raw - star_pairs(truth)),
            "naive_extra_maximal_cliques": len(naive - truth),
            "serial_legal_loose_bit_sets": len(possible),
            "serial_illegal_old_bit_sets": sum(
                1 for size in (1, 2, 3) for _ in combinations(labels, size)
            ) - len(possible),
            "parallel_block_reason": block,
            "parallel_group_counts_by_size": None if parallel is None else dict(Counter(
                len(group) for group, count in parallel.items() for _ in range(count)
            )),
            "minimal_support_size_histogram": dict(minimal),
            "distance_histogram": dict(Counter(table.values())),
        })
    assert readings[0] == readings[1]
    return {**readings[0], "reversed_and_truncated_reader_exact": True}, reference_key, reference_graph


def run(max_size: int) -> dict:
    rules = load_rule()
    layers, four_junctions, first_block, first_pilot_failure = [], [], None, None
    for size, (fixtures, attempted) in enumerate(reachable_layers(max_size), start=1):
        tables = defaultdict(list)
        stats = Counter()
        for fixture in fixtures:
            outcome, profile, table = check_fixture(rules, fixture)
            stats["repaired_star_sets_exact"] += outcome["repaired_star_sets_exact"]
            stats["all_stage_star_sets_exact"] += outcome["all_stage_star_sets_exact"]
            stats["serial_and_parallel_outputs_exact"] += outcome["serial_and_parallel_outputs_exact"]
            stats["reversed_and_truncated_reader_exact"] += outcome["reversed_and_truncated_reader_exact"]
            stats["pilot_star_sets_exact"] += outcome["pilot_star_sets_exact"]
            stats["naive_star_sets_exact"] += outcome["naive_star_sets_exact"]
            stats["parallel_blocked"] += outcome["parallel_block_reason"] is not None
            stats["serial_legal_loose_bit_sets"] += outcome["serial_legal_loose_bit_sets"]
            stats["serial_illegal_old_bit_sets"] += outcome["serial_illegal_old_bit_sets"]
            stats["sum_naive_extra_adjacencies"] += outcome["naive_extra_adjacencies"]
            if outcome["parallel_block_reason"] and first_block is None:
                first_block = {"junctions": size, **named_family(fixture), **outcome}
            if not outcome["pilot_star_sets_exact"] and first_pilot_failure is None:
                first_pilot_failure = {"junctions": size, **named_family(fixture), **outcome}
            bucket = tables[profile]
            if not any(same_table(table, prior) for prior in bucket):
                bucket.append(table)
            if size == 4:
                four_junctions.append({**named_family(fixture), **outcome})
        layers.append({
            "junctions": size,
            "bits": 3 * size,
            "serial_extensions_considered": attempted,
            "ordinary_graph_shapes": graph_shape_count(fixtures),
            "incidence_presentations": len(fixtures),
            "exact_distance_table_classes": sum(map(len, tables.values())),
            **dict(stats),
        })
    return {
        "predecessor_rule_sha256": SOURCE_SHA256,
        "renaming_seeds": SEEDS,
        "truncation_sentinel_for_distances_above_five": 6,
        "max_junctions": max_size,
        "by_size": layers,
        "four_junction_families": four_junctions,
        "first_parallel_capacity_block": first_block,
        "first_two_threshold_failure": first_pilot_failure,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--max-size", type=int, default=7, choices=range(1, 8))
    print(json.dumps(run(parser.parse_args().max_size), indent=2, sort_keys=True))
