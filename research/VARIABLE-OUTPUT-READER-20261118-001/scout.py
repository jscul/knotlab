"""Replay the bounded reader pilot with two or three fresh distinctions per move.

The seed is the inherited three-place even-parity junction. Each later
junction uses the inherited one-, two-, or three-parent test and takes one
loose distinction per parent. The output count can be two or three at every
move, independently of the parents and of the earlier counts. The control
uses three throughout. The actual menu records sets of consumed identities.
Each allowed fresh count can be paired with every member of that menu.
The even-parity equation leaves all but one of its fresh bits free over
every previously allowed assignment.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from itertools import combinations, product
from pathlib import Path

import networkx as nx
from networkx.algorithms.isomorphism import GraphMatcher


ROOT = Path(__file__).resolve().parents[2]
READER = (
    ROOT / "proofs/BOND-NEXT-JOIN-20261117-001"
    / "BOND-NEXT-JOIN-20261117-001-P001_distance_reader" / "check_rearrangements.py"
)
READER_DIGEST = "2a27ca668cef0fc3f26492789958073161a2af572cf113f60b9e849ed973143a"
PARENT_COUNTS = (1, 2, 3)
FRESH_FOR_PARENT_TEST = ("unused-a", "unused-b", "unused-c")
Pair = tuple[int, int]
Table = dict[Pair, int | None]
Checks = dict[int, tuple[int, ...]]


@dataclass(frozen=True)
class Fixture:
    meetings: tuple[Pair, ...]
    loose_counts: tuple[int, ...]
    history: tuple[tuple[tuple[int, ...], int], ...]

    def checks(self) -> Checks:
        supports = [[] for _ in self.loose_counts]
        for bit, (left, right) in enumerate(self.meetings):
            supports[left].append(bit)
            supports[right].append(bit)
        next_bit = len(self.meetings)
        for support, count in zip(supports, self.loose_counts, strict=True):
            support.extend(range(next_bit, next_bit + count))
            next_bit += count
        return {i: tuple(support) for i, support in enumerate(supports)}

    def successor(self, parents: tuple[int, ...], fresh_count: int) -> Fixture:
        new_junction = len(self.loose_counts)
        meetings = self.meetings + tuple((parent, new_junction) for parent in parents)
        loose = tuple(count - (i in parents) for i, count in enumerate(self.loose_counts))
        return Fixture(meetings, (*loose, fresh_count), (*self.history, (parents, fresh_count)))

    def meeting_graph(self) -> nx.Graph:
        graph = nx.Graph()
        graph.add_nodes_from((i, {"loose": count}) for i, count in enumerate(self.loose_counts))
        graph.add_edges_from(self.meetings)
        return graph


@dataclass(frozen=True)
class Measured:
    fixture: Fixture
    stars: frozenset[frozenset[int]]
    span: frozenset[int]
    menu: frozenset[frozenset[int]]
    table: Table


def load_reader():
    assert hashlib.sha256(READER.read_bytes()).hexdigest() == READER_DIGEST
    spec = importlib.util.spec_from_file_location("scout_predecessor_reader", READER)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def same_attributes(left, right):
    return left == right


def legal_parent_sets(rules, checks: Checks):
    users, _ = rules.incidence(checks)
    available = rules.loose_ports(users)
    for size in PARENT_COUNTS:
        for parents in combinations(sorted(available), size):
            consumed = tuple(available[parent][0] for parent in parents)
            # The inherited predicate separates its three-fresh guard from
            # the test on parents and loose identities. Supply three unused
            # names to exercise the latter without choosing an output count.
            if rules.legal_local_move(checks, consumed, FRESH_FOR_PARENT_TEST):
                yield parents, tuple(available[parent] for parent in parents)


def advance(rules, fixtures, fresh_counts):
    buckets = defaultdict(list)
    attempted = Counter()
    for fixture in fixtures:
        for parents, _ in legal_parent_sets(rules, fixture.checks()):
            for count in fresh_counts:
                nxt = fixture.successor(parents, count)
                attempted[len(parents)] += 1
                graph = nxt.meeting_graph()
                signature = tuple(sorted((graph.degree(i), n) for i, n in enumerate(nxt.loose_counts)))
                # A meeting graph with loose counts specifies the full parity
                # incidence up to renaming. Loose identities at one parent
                # are interchangeable for generating the next graph.
                if not any(
                    nx.is_isomorphic(graph, prior, node_match=same_attributes)
                    for _, prior in buckets[signature]
                ):
                    buckets[signature].append((nxt, graph))
    return [nxt for bucket in buckets.values() for nxt, _ in bucket], attempted


def actual_menu(rules, checks):
    menu = set()
    for _, available in legal_parent_sets(rules, checks):
        for consumed in product(*available):
            assert rules.legal_local_move(checks, consumed, FRESH_FOR_PARENT_TEST)
            menu.add(frozenset(consumed))
    return frozenset(menu)


def mask(bits):
    return sum(1 << bit for bit in bits)


def bits(word):
    while word:
        least = word & -word
        yield least.bit_length() - 1
        word ^= least


def parity_span(checks):
    span = [0]
    for support in checks.values():
        equation = mask(support)
        span.extend([prior ^ equation for prior in span])
    assert len(span) == len(set(span)) == 1 << len(checks)
    return frozenset(span)


def full_table(span, width):
    """In this parity relation the minimal nonzero dual supports are bonds."""
    bonds = []
    table = dict.fromkeys(combinations(range(width), 2), None)
    for word in sorted(span - {0}, key=lambda row: (row.bit_count(), row)):
        if any(word & smaller == smaller for smaller in bonds):
            continue
        bonds.append(word)
        assert word.bit_count() >= 3
        for pair in combinations(bits(word), 2):
            if table[pair] is None:
                table[pair] = word.bit_count() - 1
    return table


def measure(rules, fixture):
    checks = fixture.checks()
    stars = frozenset(frozenset(support) for support in checks.values())
    span = parity_span(checks)
    width = len(set().union(*stars))
    return Measured(fixture, stars, span, actual_menu(rules, checks), full_table(span, width))


def observed_graph(table: Table, truncate: bool):
    graph = nx.Graph()
    for (i, j), distance in table.items():
        # The full table distinguishes infinity from every integer.
        # The cutoff table uses one color for every entry above five.
        color = -1 if distance is None else distance
        if truncate and (distance is None or distance > 5):
            color = 6
        graph.add_edge(i, j, scalar=color)
    for bit in graph:
        graph.nodes[bit]["profile"] = tuple(sorted(row["scalar"] for row in graph[bit].values()))
    key = tuple(sorted(graph.nodes[bit]["profile"] for bit in graph))
    return key, graph


def transported_sets(roster, isometry):
    return {frozenset(isometry[bit] for bit in group) for group in roster}


def ordered_groups(groups):
    return sorted(tuple(sorted(group)) for group in groups)


def check_map(current, other, isometry, mode):
    stars = transported_sets(current.stars, isometry)
    menu = transported_sets(current.menu, isometry)
    renamed_bits = tuple(1 << isometry[i] for i in range(len(isometry)))
    span = {sum(renamed_bits[bit] for bit in bits(word)) for word in current.span}
    if (stars, span, menu) == (other.stars, other.span, other.menu):
        return
    counterexample = {
        "outcome": "scalar_isometry_changes_the_presentation_or_menu",
        "mode": mode,
        "left_history": current.fixture.history,
        "right_history": other.fixture.history,
        "left_junctions": ordered_groups(current.stars),
        "right_junctions": ordered_groups(other.stars),
        "bit_map_from_left_to_right": dict(sorted(isometry.items())),
        "changed_junction_supports_in_right_names": ordered_groups(stars ^ other.stars),
        "changed_dual_equations_in_right_names": sorted(span ^ other.span),
        "changed_menu_choices_in_right_names": ordered_groups(menu ^ other.menu),
        "full_entries_changed_under_map": [
            (pair, value, other.table[tuple(sorted(isometry[i] for i in pair))])
            for pair, value in current.table.items()
            if value != other.table[tuple(sorted(isometry[i] for i in pair))]
        ],
    }
    print(json.dumps(counterexample, indent=2, sort_keys=True), file=sys.stderr)
    raise SystemExit(1)


def census(reader, rules, fresh_counts, expected_population):
    fixtures = [Fixture((), (3,), ())]
    attempted = Counter()
    # Both indices span all sizes. Mixed output totals allow two different
    # junction counts to have the same number of observed distinctions.
    seen = {"full": defaultdict(list), "cutoff_five": defaultdict(list)}
    stages = []
    earliest_decoder_failure = None
    for size, expected in enumerate(expected_population, start=1):
        assert len(fixtures) == expected
        widest_bond_distance = 0
        infinity_entries = 0
        failures = 0
        compared = Counter()
        menu_counts = Counter()
        for fixture in fixtures:
            measured = measure(rules, fixture)
            wider = max((delta for delta in measured.table.values() if delta is not None), default=0)
            widest_bond_distance = max(widest_bond_distance, wider)
            infinity_entries += sum(delta is None for delta in measured.table.values())
            menu_counts.update(map(len, measured.menu))
            cutoff = {
                pair: value if value is not None and value <= 5 else 6
                for pair, value in measured.table.items()
            }
            failures += reader.recover_stars(cutoff) != measured.stars
            for mode, old in seen.items():
                key, graph = observed_graph(measured.table, truncate=mode == "cutoff_five")
                for other, candidate_graph in [(measured, graph), *old[key]]:
                    matcher = GraphMatcher(
                        graph, candidate_graph, node_match=same_attributes, edge_match=same_attributes
                    )
                    count = 0
                    for isometry in matcher.isomorphisms_iter():
                        count += 1
                        compared[mode] += 1
                        check_map(measured, other, isometry, mode)
                        # Equal star rosters under a map give an incidence
                        # isomorphism, so a distinct representative is an error.
                        assert measured is other
                    assert measured is not other or count > 0
                old[key].append((measured, graph))
        if failures and earliest_decoder_failure is None:
            earliest_decoder_failure = size
        stages.append({
            "junctions": size,
            "incidence_types": len(fixtures),
            "extensions_from_previous_representatives_by_parent_count": dict(sorted(attempted.items())),
            "serial_menu_choices_by_parent_count": dict(sorted(menu_counts.items())),
            "table_isometries_checked": dict(sorted(compared.items())),
            "maximum_finite_bond_distance": widest_bond_distance,
            "infinite_pair_entries": infinity_entries,
            "inherited_decoder_failures": failures,
        })
        if size < len(expected_population):
            fixtures, attempted = advance(rules, fixtures, fresh_counts)
    return {
        "fresh_counts": fresh_counts,
        "incidence_types_total": sum(expected_population),
        "stages": stages,
        "first_inherited_decoder_failure": earliest_decoder_failure,
        "outcome": "all_checked_table_isometries_preserved_junctions_allowed_states_and_serial_menu",
    }


def literal_decoder_control(reader, rules):
    # The inherited growth module makes knotlab available.
    from knotlab import Relation, check_knot

    checks = {0: (0, 1, 2)}
    for consumed, fresh in ((0, (3, 4)), (1, (5, 6))):
        assert rules.legal_local_move(checks, (consumed,), FRESH_FOR_PARENT_TEST)
        assert set(fresh).isdisjoint(set().union(*checks.values()))
        checks[len(checks)] = (consumed, *fresh)
    width = 7
    equations = tuple(mask(support) for support in checks.values())
    allowed = tuple(
        row for row in range(1 << width)
        if all((row & equation).bit_count() % 2 == 0 for equation in equations)
    )
    assert len(allowed) == 16

    def projection(support):
        names = tuple(f"p{i}" for i in support)
        rows = frozenset(tuple(bool(word & (1 << i)) for i in support) for word in allowed)
        return Relation(names, rows)

    bonds, table = [], {}
    tested = 0
    for size in range(3, width + 1):
        for support in combinations(range(width), size):
            projected = projection(support)
            tested += 1
            if check_knot(projected, projected.variables[:-1], projected.variables[-1]).is_knot:
                bonds.append(support)
                for pair in combinations(support, 2):
                    table.setdefault(pair, size - 1)
    assert tested == 99
    assert table == full_table(parity_span(checks), width)
    actual = {frozenset(support) for support in checks.values()}
    phantom = frozenset((3, 4, 5, 6))
    assert reader.recover_stars(table) == actual | {phantom}
    unrestricted = projection(tuple(sorted(phantom)))
    assert unrestricted.is_full()
    return {
        "all_binary_assignments_tested": 1 << width,
        "joint_states": len(allowed),
        "actual_junctions": ordered_groups(actual),
        "canonical_K1_K2_K3_supports_checked": tested,
        "bonds": bonds,
        "bond_distance_counts": dict(sorted(Counter(table.values()).items())),
        "phantom_junction_from_predecessor": tuple(sorted(phantom)),
        "actual_projected_states_on_phantom": len(unrestricted.rows),
    }


def run():
    absent = {(0, 1): None}
    six = {(0, 1): 6}
    assert observed_graph(absent, False)[0] != observed_graph(six, False)[0]
    assert observed_graph(absent, True)[0] == observed_graph(six, True)[0]
    reader = load_reader()
    rules = reader.load_rule()
    literal = literal_decoder_control(reader, rules)
    fixed = census(reader, rules, (3,), (1, 1, 2, 6, 21))
    variable = census(reader, rules, (2, 3), (1, 2, 5, 25, 132, 880))
    assert fixed["first_inherited_decoder_failure"] is None
    assert variable["first_inherited_decoder_failure"] == 3
    return {
        "scope": "bounded exploratory pilot",
        "predecessor_reader_sha256": READER_DIGEST,
        "seed_distinctions": 3,
        "allowed_parent_counts": PARENT_COUNTS,
        "actual_serial_menu_items": "sets of consumed identities",
        "naming_checks": "self and cross-table isometries across all checked junction counts",
        "literal_seven_bit_control": literal,
        "fixed_three_fresh_control": fixed,
        "variable_two_or_three_fresh": variable,
    }


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, sort_keys=True))
