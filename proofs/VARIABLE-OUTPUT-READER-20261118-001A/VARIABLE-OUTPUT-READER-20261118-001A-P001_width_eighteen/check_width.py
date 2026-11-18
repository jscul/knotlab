"""Compare the designated seven-junction table with every reachable width-18 table.

The archived scout supplies the literal joint parity rules and parent law.
Each eligible parent supplies one of its present loose distinctions. The
move may add two or three fresh distinctions independently of its inputs.
The scalar observer receives all current identities, with no history.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from functools import cache
from itertools import combinations
from pathlib import Path

import networkx as nx
from networkx.algorithms.isomorphism import GraphMatcher


ROOT = Path(__file__).resolve().parents[3]
SCOUT = ROOT / "research/VARIABLE-OUTPUT-READER-20261118-001/scout.py"
SCOUT_SHA256 = "ae7a660bad9a83bea896dd3287182772df7cbe462038e4e1251b5fc824d13434"
WIDTH = 18
FRESH_COUNTS = (2, 3)
MAX_JUNCTIONS = 8
PAIRS = tuple(combinations(range(WIDTH), 2))
TARGET_HISTORY = (
    ((0,), 3), ((0,), 2), ((0,), 3),
    ((1, 2), 2), ((1, 3), 3), ((2, 3), 2),
)
CHAIN_HISTORY = tuple(((i,), 3) for i in range(5))


@cache
def inherited():
    assert hashlib.sha256(SCOUT.read_bytes()).hexdigest() == SCOUT_SHA256
    spec = importlib.util.spec_from_file_location("width_eighteen_archived_scout", SCOUT)
    scout = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = scout
    spec.loader.exec_module(scout)
    reader = scout.load_reader()
    return scout, reader, reader.load_rule()


def width(fixture):
    return len(fixture.meetings) + sum(fixture.loose_counts)


def replay(history):
    scout, _, rules = inherited()
    fixture = scout.Fixture((), (3,), ())
    for parents, fresh in history:
        options = {group for group, _ in scout.legal_parent_sets(rules, fixture.checks())}
        assert parents in options and fresh in FRESH_COUNTS
        fixture = fixture.successor(parents, fresh)
    assert width(fixture) == WIDTH
    return fixture


def target_fixture():
    """Return the designated seven-junction fixture in the archived birth order."""
    return replay(TARGET_HISTORY)


def extendible_width(current, depth):
    remaining = WIDTH - current
    return any(2 * additional <= remaining <= 3 * additional
               for additional in range(MAX_JUNCTIONS - depth + 1))


def incidence_colors(fixture):
    """A cheap necessary invariant. Exact graph matching resolves remaining ties."""
    neighbors = [set() for _ in fixture.loose_counts]
    for left, right in fixture.meetings:
        neighbors[left].add(right)
        neighbors[right].add(left)
    colors = tuple((n, len(adj)) for n, adj in zip(fixture.loose_counts, neighbors, strict=True))
    for _ in range(2):
        colors = tuple((color, tuple(sorted(colors[j] for j in adjacent)))
                       for color, adjacent in zip(colors, neighbors, strict=True))
    return colors


def colored_incidence(fixture, colors):
    graph = fixture.meeting_graph()
    nx.set_node_attributes(graph, dict(enumerate(colors)), "incidence_color")
    return graph


def same_attributes(left, right):
    return left == right


def next_layer(fixtures, depth):
    scout, _, rules = inherited()
    buckets = defaultdict(list)
    same_literal_incidence = set()
    stats = Counter()
    parent_counts = Counter()
    for fixture in fixtures:
        old_width = width(fixture)
        if old_width == WIDTH:
            continue
        assert extendible_width(old_width, depth - 1)
        for parents, _ in scout.legal_parent_sets(rules, fixture.checks()):
            for fresh in FRESH_COUNTS:
                stats["attempted_extensions"] += 1
                parent_counts[str(len(parents))] += 1
                new_width = old_width + fresh
                if not extendible_width(new_width, depth):
                    reason = "width_exceeded" if new_width > WIDTH else "unreachable_width_remainder"
                    stats[reason] += 1
                    continue
                candidate = fixture.successor(parents, fresh)
                assert width(candidate) == new_width
                literal = (candidate.meetings, candidate.loose_counts)
                if literal in same_literal_incidence:
                    stats["equal_numbered_incidence_rejected"] += 1
                    continue
                same_literal_incidence.add(literal)
                colors = incidence_colors(candidate)
                key = tuple(sorted(colors))
                graph = colored_incidence(candidate, colors)
                for _, prior in buckets[key]:
                    stats["exact_incidence_tests"] += 1
                    if nx.is_isomorphic(graph, prior, node_match=same_attributes):
                        stats["isomorphic_incidence_rejected"] += 1
                        break
                else:
                    buckets[key].append((candidate, graph))
    following = tuple(fixture for bucket in buckets.values() for fixture, _ in bucket)
    assert (
        len(following) + stats["width_exceeded"] + stats["unreachable_width_remainder"]
        + stats["equal_numbered_incidence_rejected"] + stats["isomorphic_incidence_rejected"]
        == stats["attempted_extensions"]
    )
    return following, {
        **stats,
        "attempted_extensions_by_parent_count": dict(parent_counts),
        "retained_prefix_types_by_width": dict(Counter(str(width(f)) for f in following)),
    }


@cache
def generate_width_fixtures():
    """Retain one representative per current incidence among useful prefixes."""
    scout, _, _ = inherited()
    current = (scout.Fixture((), (3,), ()),)
    selected = []
    stages = []
    for depth in range(2, MAX_JUNCTIONS + 1):
        current, audit = next_layer(current, depth)
        exact = [fixture for fixture in current if width(fixture) == WIDTH]
        selected.extend(exact)
        stages.append({
            "junctions": depth, **audit, "width_eighteen_types": len(exact),
        })
    assert current and all(width(fixture) == WIDTH for fixture in current)
    selected.sort(key=lambda fixture: (len(fixture.loose_counts), fixture.history))
    return tuple(selected), stages


def width_fixtures():
    """Return unique physical fixtures in increasing junction count and history order."""
    return generate_width_fixtures()[0]


def width_records():
    """Yield archived Measured records for all width-18 fixtures."""
    scout, _, rules = inherited()
    for fixture in width_fixtures():
        yield scout.measure(rules, fixture)


def full_table(fixture):
    scout, _, _ = inherited()
    return scout.full_table(scout.parity_span(fixture.checks()), WIDTH)


def observed_value(value, cutoff):
    if cutoff is not None and (value is None or value > cutoff):
        return cutoff + 1
    return -1 if value is None else value


def pair_histogram(table, cutoff):
    return Counter(observed_value(value, cutoff) for value in table.values())


def colored_rows(table, cutoff):
    rows = [[0 for _ in range(WIDTH)] for _ in range(WIDTH)]
    for i, j in PAIRS:
        rows[i][j] = rows[j][i] = observed_value(table[i, j], cutoff)
    return tuple(map(tuple, rows))


def row_profiles(rows):
    return tuple(tuple(sorted(value for j, value in enumerate(row) if i != j))
                 for i, row in enumerate(rows))


def refined_profiles(rows, profiles):
    return tuple(
        (profiles[i], tuple(sorted((value, profiles[j]) for j, value in enumerate(row) if i != j)))
        for i, row in enumerate(rows)
    )


def scalar_graph(rows, refined):
    graph = nx.Graph()
    graph.add_nodes_from((i, {"profile": signature}) for i, signature in enumerate(refined))
    graph.add_edges_from((i, j, {"scalar": rows[i][j]}) for i, j in PAIRS)
    return graph


@dataclass(frozen=True)
class TargetObservation:
    cutoff: int | None
    histogram: Counter
    profiles: Counter
    refined: Counter
    graph: nx.Graph


def make_target_observation(table, cutoff):
    rows = colored_rows(table, cutoff)
    profiles = row_profiles(rows)
    refined = refined_profiles(rows, profiles)
    return TargetObservation(
        cutoff, pair_histogram(table, cutoff), Counter(profiles), Counter(refined),
        scalar_graph(rows, refined),
    )


def candidate_graph(table, target, counters):
    counters["tables_tested"] += 1
    if pair_histogram(table, target.cutoff) != target.histogram:
        return None
    counters["pair_histogram_matches"] += 1
    rows = colored_rows(table, target.cutoff)
    profiles = row_profiles(rows)
    if Counter(profiles) != target.profiles:
        return None
    counters["row_profile_multiset_matches"] += 1
    refined = refined_profiles(rows, profiles)
    if Counter(refined) != target.refined:
        return None
    counters["weighted_neighbor_profile_matches"] += 1
    return scalar_graph(rows, refined)


def isometries(left, right):
    return GraphMatcher(
        left, right, node_match=same_attributes, edge_match=same_attributes
    ).isomorphisms_iter()


def actual_moves(menu):
    return {(operands, fresh) for operands in menu for fresh in FRESH_COUNTS}


def describe_moves(moves):
    by_inputs = Counter((len(operands), fresh) for operands, fresh in moves)
    return {
        str(count): {str(fresh): by_inputs[count, fresh] for fresh in FRESH_COUNTS}
        for count in (1, 2, 3)
    }


def ordered_moves(moves):
    return sorted((tuple(sorted(operands)), fresh) for operands, fresh in moves)


def map_table(table, isometry):
    return {tuple(sorted((isometry[i], isometry[j]))): value for (i, j), value in table.items()}


def assess_isometry(origin, candidate, isometry):
    scout, _, _ = inherited()
    assert set(isometry) == set(isometry.values()) == set(range(WIDTH))
    relabel = lambda group: frozenset(isometry[bit] for bit in group)
    moves = {(relabel(operands), fresh) for operands, fresh in actual_moves(origin.menu)}
    missing = actual_moves(candidate.menu) - moves
    extra = moves - actual_moves(candidate.menu)
    transported_span = {
        sum(1 << isometry[bit] for bit in scout.bits(word)) for word in origin.span
    }
    return {
        "actual_menu": not (missing or extra),
        "junction_roster": {relabel(star) for star in origin.stars} == candidate.stars,
        "allowed_states": transported_span == candidate.span,
        "full_scalar_table": map_table(origin.table, isometry) == candidate.table,
    }, {"only_in_candidate_menu": ordered_moves(missing), "only_in_mapped_menu": ordered_moves(extra)}


def compare_fixture(origin, fixture, table, target, counters):
    graph = candidate_graph(table, target, counters)
    if graph is None:
        return None
    scout, _, rules = inherited()
    candidate = None
    totals = Counter()
    maps = []
    first_change = None
    for mapping in isometries(target.graph, graph):
        if candidate is None:
            candidate = scout.measure(rules, fixture)
            assert candidate.table == table
        totals["maps"] += 1
        maps.append(tuple(mapping[bit] for bit in range(WIDTH)))
        preserves, differences = assess_isometry(origin, candidate, mapping)
        assert target.cutoff is not None or preserves["full_scalar_table"]
        totals.update({f"preserves_{name}": int(yes) for name, yes in preserves.items()})
        if not preserves["actual_menu"] and first_change is None:
            first_change = {
                "target_to_candidate": [mapping[i] for i in range(WIDTH)], **differences
            }
    counters["scalar_isometries"] += totals["maps"]
    if candidate is None:
        return None
    same_incidence = nx.is_isomorphic(
        origin.fixture.meeting_graph(), fixture.meeting_graph(), node_match=same_attributes
    )
    counters["isometric_types"] += 1
    counters["other_isometric_types"] += int(not same_incidence)
    return {
        "junctions": len(fixture.loose_counts), "history": fixture.history,
        "same_incidence_type_as_target": same_incidence,
        "menu_choices_on_existing_identities": scout.ordered_groups(candidate.menu),
        "menu_by_parent_count_and_fresh_count": describe_moves(actual_moves(candidate.menu)),
        "scalar_maps_target_to_candidate": sorted(maps),
        "isometry_counts": dict(totals), "first_menu_change": first_change,
    }


def relabel_control(origin, observations):
    scout, _, rules = inherited()
    permutation = {i: (7 * i + 5) % WIDTH for i in range(WIDTH)}
    checks = {
        vertex: tuple(permutation[bit] for bit in support)
        for vertex, support in origin.fixture.checks().items()
    }
    span = scout.parity_span(checks)
    named = scout.Measured(
        origin.fixture, frozenset(map(frozenset, checks.values())), span,
        scout.actual_menu(rules, checks), scout.full_table(span, WIDTH),
    )
    assert map_table(origin.table, permutation) == named.table and named.table != origin.table
    checked, menu_preserving = {}, {}
    for mode, target in observations.items():
        profile_counts = Counter()
        graph = candidate_graph(named.table, target, profile_counts)
        assert graph is not None
        maps = tuple(isometries(target.graph, graph))
        assert permutation in maps
        assert all(assess_isometry(origin, named, permutation)[0].values())
        checked[mode] = len(maps)
        menu_preserving[mode] = sum(
            assess_isometry(origin, named, mapping)[0]["actual_menu"] for mapping in maps
        )
    return {
        "permutation": [permutation[i] for i in range(WIDTH)], "table_isometries": checked,
        "menu_preserving_maps": menu_preserving,
    }


def negative_controls(origin, observations):
    chain = replay(CHAIN_HISTORY)
    chain_table = full_table(chain)
    assert width(chain) == WIDTH and len(chain.loose_counts) == 6
    chain_counts = {}
    for mode, observation in observations.items():
        counters = Counter()
        graph = candidate_graph(chain_table, observation, counters)
        assert graph is None or next(isometries(observation.graph, graph), None) is None
        chain_counts[mode] = dict(counters)

    # A genuine input can cease to be legal under an arbitrary bijection.
    # This swap must fail the scalar test in both observation modes.
    _, _, rules = inherited()
    users, _ = rules.incidence(origin.fixture.checks())
    shared = next(bit for bit in sorted(users) if len(users[bit]) == 2)
    loose = next(bit for bit in sorted(users) if len(users[bit]) == 1)
    wrong = dict(enumerate(range(WIDTH)))
    wrong[shared], wrong[loose] = loose, shared
    preserves, difference = assess_isometry(origin, origin, wrong)
    altered = map_table(origin.table, wrong)
    assert not preserves["actual_menu"] and difference["only_in_mapped_menu"]
    assert all(
        colored_rows(altered, reading.cutoff) != colored_rows(origin.table, reading.cutoff)
        for reading in observations.values()
    )
    return {
        "off_target_chain": {"width": WIDTH, "history": chain.history, "filters": chain_counts},
        "rejected_swap": {
            "shared_and_loose": [shared, loose],
            "example_wrong_transported_choice": difference["only_in_mapped_menu"][0],
        },
    }


def row_profile_decoy(origin, fixture, table, cutoff):
    """Check a near match again without weighted neighbor-profile filtering."""
    scout, _, rules = inherited()
    target_rows = colored_rows(origin.table, cutoff)
    candidate_rows = colored_rows(table, cutoff)
    target_graph = scalar_graph(target_rows, row_profiles(target_rows))
    graph = scalar_graph(candidate_rows, row_profiles(candidate_rows))
    assert next(isometries(target_graph, graph), None) is None
    return {
        "junctions": len(fixture.loose_counts), "history": fixture.history,
        "menu_by_parent_count_and_fresh_count": describe_moves(
            actual_moves(scout.actual_menu(rules, fixture.checks()))
        ),
        "no_isometry_without_neighbor_profile_filter": True,
    }


def fixed_three_depth_six():
    scout, _, rules = inherited()
    controls = [scout.Fixture((), (3,), ())]
    for _ in range(5):
        controls, _ = scout.advance(rules, controls, (3,))
    assert all(width(fixture) == WIDTH for fixture in controls)
    return len(controls)


def run():
    assert observed_value(None, None) != observed_value(6, None)
    assert observed_value(None, 5) == observed_value(6, 5)
    assert observed_value(None, 4) == observed_value(5, 4)
    scout, reader, rules = inherited()
    literal = scout.literal_decoder_control(reader, rules)
    origin = scout.measure(rules, target_fixture())
    expected_triples = sum(len(operands) == 3 for operands in origin.menu)
    assert expected_triples == 12
    observations = {
        name: make_target_observation(origin.table, cutoff)
        for name, cutoff in (("full", None), ("through_five", 5), ("through_four_exploratory", 4))
    }
    fixtures, stages = generate_width_fixtures()
    by_size = Counter(str(len(fixture.loose_counts)) for fixture in fixtures)
    assert set(by_size) == {"6", "7", "8"}
    stats = {mode: defaultdict(Counter) for mode in observations}
    matched = {mode: [] for mode in observations}
    decoys = {mode: [] for mode in observations}

    for fixture in fixtures:
        table = full_table(fixture)
        depth = str(len(fixture.loose_counts))
        for mode, target in observations.items():
            counters = stats[mode][depth]
            old_profile_count = counters["row_profile_multiset_matches"]
            entry = compare_fixture(origin, fixture, table, target, counters)
            if entry is not None:
                matched[mode].append(entry)
            elif counters["row_profile_multiset_matches"] > old_profile_count:
                decoys[mode].append(row_profile_decoy(origin, fixture, table, target.cutoff))

    summaries = {}
    relabel = relabel_control(origin, observations)
    for mode, records in matched.items():
        equal_type, = (record for record in records if record["same_incidence_type_as_target"])
        assert equal_type["isometry_counts"]["maps"] == relabel["table_isometries"][mode]
        assert equal_type["isometry_counts"]["preserves_actual_menu"] == relabel["menu_preserving_maps"][mode]
        summaries[mode] = {
            "filters_by_junction_count": {
                depth: {name: counter[name] for name in (
                    "tables_tested", "pair_histogram_matches", "row_profile_multiset_matches",
                    "weighted_neighbor_profile_matches", "isometric_types",
                    "other_isometric_types", "scalar_isometries",
                )} for depth, counter in stats[mode].items()
            },
            "matching_types": records,
            "nonisometric_row_profile_matches": decoys[mode],
            "actual_menu_changes": sum(
                row["isometry_counts"]["maps"] - row["isometry_counts"]["preserves_actual_menu"]
                for row in records
            ),
        }
    fixed_six = fixed_three_depth_six()
    assert fixed_six == by_size["6"]
    return {
        "width": WIDTH,
        "scout_sha256": SCOUT_SHA256,
        "eligible_parent_counts": (1, 2, 3),
        "fresh_counts_at_every_legal_input_choice": FRESH_COUNTS,
        "target": {
            "history": TARGET_HISTORY,
            "junctions": origin.fixture.checks(),
            "menu_by_parent_count_and_fresh_count": describe_moves(actual_moves(origin.menu)),
        },
        "population": {**dict(by_size), "total": len(fixtures)},
        "generation": stages,
        "observations": summaries,
        "controls": {
            "relabeling": relabel,
            "six_junction_types_by_archived_fixed_three_enumerator": fixed_six,
            "literal_seven_bit": {
                "canonical_supports_checked": literal["canonical_K1_K2_K3_supports_checked"],
                "all_states_on_phantom": literal["actual_projected_states_on_phantom"],
            },
            **negative_controls(origin, observations),
        },
    }


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, sort_keys=True))
