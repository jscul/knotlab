"""Replay four scalar-read rounds on a disjoint parity system and test a batch identification."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from collections import Counter
from itertools import combinations, permutations
from random import Random

from check_construction import (
    CUBE,
    GROWTH,
    ROOT,
    compile_alignment,
    cube_frames,
    cut_rows_in_chart,
    load_source,
    locally_generated_target,
    steps_from,
)
from check_probe import PAIRS, WIDTH, ProbeProjection, literal_probe_graph, recover_cube, seed_fixture


PURE_READER = (
    ROOT / "proofs/BOND-NEXT-JOIN-20261117-001"
    / "BOND-NEXT-JOIN-20261117-001-P001_distance_reader" / "check_rearrangements.py"
)
PURE_READER_DIGEST = "2a27ca668cef0fc3f26492789958073161a2af572cf113f60b9e849ed973143a"


def load_pure_reader():
    assert hashlib.sha256(PURE_READER.read_bytes()).hexdigest() == PURE_READER_DIGEST
    spec = importlib.util.spec_from_file_location("bootstrap_pure_reader", PURE_READER)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def pure_table(checks):
    """The admitted pure short-support theorem supplies the grader's scalar observations."""
    stars = [frozenset(bits) for bits in checks.values()]
    labels = sorted(set().union(*stars))
    supports = stars + [
        left ^ right for left, right in combinations(stars, 2)
        if left & right and len(left) + len(right) - 2 <= 6
    ]
    table = dict.fromkeys(combinations(labels, 2), 6)
    for support in supports:
        for pair in combinations(sorted(support), 2):
            table[pair] = min(table[pair], len(support) - 1)
    return labels, table


def observation(probe_graph, checks, rng):
    """Produce the exact global threshold-two graph and a restricted scalar query."""
    pure_bits = {bit for support in checks.values() for bit in support}
    names = sorted(probe_graph.keys() | pure_bits)
    observed = list(range(len(names)))
    if rng is not None:
        rng.shuffle(observed)
    rename = dict(zip(names, observed, strict=True))
    actual = {j: tuple(rename[bit] for bit in bits) for j, bits in checks.items()}
    pure_labels, table = pure_table(actual)
    two = {rename[bit]: {rename[n] for n in ns} for bit, ns in probe_graph.items()}
    two.update({bit: set() for bit in pure_labels})
    for (left, right), distance in table.items():
        if distance == 2:
            two[left].add(right)
            two[right].add(left)
    assert max(len(two[bit]) for bit in pure_labels) == 2

    def threshold_five(labels):
        return {pair: table[pair] for pair in combinations(sorted(labels), 2)}

    return two, threshold_five, actual, rename


def probe_component(two):
    high = {bit for bit, neighbors in two.items() if len(neighbors) == 33}
    if len(high) != 8:
        raise ValueError("Expected eight distinctions of threshold-two degree 33")
    root = min(high)
    component, pending = {root}, [root]
    while pending:
        following = two[pending.pop()] - component
        component.update(following)
        pending.extend(following)
    if len(component) != 64 or not high <= component:
        raise ValueError("The threshold-two component did not isolate the queried relation")
    return component


def read_snapshot(two, threshold_five, pure):
    """The policy sees threshold tests on current labels, plus the supplied laws."""
    probed = probe_component(two)
    cube = recover_cube({bit: two[bit] for bit in probed})
    ordinary_bits = two.keys() - probed
    stars = pure.recover_stars(threshold_five(ordinary_bits))
    ordered_stars = sorted(tuple(sorted(star)) for star in stars)
    return cube, dict(enumerate(ordered_stars))


def allocate_round(read, observed_bits, growth):
    """Choose one permitted allocation, allowing ties among actual loose distinctions."""
    users, _ = growth.incidence(read)
    available = {j: sorted(bits) for j, bits in growth.loose_ports(users).items()}
    groups, _ = growth.parent_groups(read)
    moves = []
    next_fresh = max(observed_bits) + 1
    for parents in groups:
        consumed = tuple(available[parent].pop() for parent in parents)
        fresh = tuple(range(next_fresh, next_fresh + 3))
        next_fresh += len(fresh)
        moves.append((consumed, fresh))
    assert all(not ports for ports in available.values())
    return moves


def apply_round(checks, moves, rename, growth):
    """Grader: translate the proposals back to the relation's actual identities."""
    before_bits = {bit for support in checks.values() for bit in support}
    mapping = {named: bit for bit, named in rename.items()}
    physical = max(mapping.values()) + 1
    for consumed, fresh in moves:
        inputs = tuple(mapping[bit] for bit in consumed)
        assert mapping.keys().isdisjoint(fresh)
        outputs = tuple(range(physical, physical + len(fresh)))
        physical += len(fresh)
        mapping.update(zip(fresh, outputs, strict=True))
        assert growth.legal_local_move(checks, inputs, outputs)
        checks[len(checks)] = inputs + outputs
    after_bits = before_bits | {bit for support in checks.values() for bit in support}
    expected_additions = 3 * len(moves)
    assert len(after_bits) == len(before_bits) + expected_additions


def scaffold_frames(read, growth):
    """Read the classical positions from ordinary incidence and three tied tips."""
    _, adjacency = growth.incidence(read)
    root, = (j for j, bits in read.items() if len(bits) == 3)
    tips = tuple(j for j, neighbors in adjacency.items() if len(neighbors) == 1)
    assert len(tips) == 3
    from_root = steps_from(adjacency, root)
    from_tips = {tip: steps_from(adjacency, tip) for tip in tips}
    span, = {from_root[tip] for tip in tips}
    assert span == 4
    for order in permutations(tips):
        chart = {}
        for j, depth in from_root.items():
            doubled = tuple(span + depth - from_tips[tip][j] for tip in order)
            assert all(value >= 0 and value % 2 == 0 for value in doubled)
            chart[j] = tuple(value // 2 for value in doubled)
        sites = set(chart.values())
        assert len(sites) == len(read) and CUBE <= sites
        yield chart


def identify_plan(read, old_chart, scaffold_chart, growth):
    """Use only the two recovered charts to find the eight existing shared outputs."""
    users, _ = growth.incidence(read)
    directions = {
        frozenset(scaffold_chart[j] for j in owners): bit
        for bit, owners in users.items() if len(owners) == 2
    }
    replacement = {
        directions[frozenset((point, (point[0], point[1], point[2] + 1)))]: old
        for old, point in old_chart.items()
    }
    assert len(replacement) == len(old_chart) == 8
    return replacement


def owner_sets(checks, growth):
    return {bit: frozenset(owners) for bit, owners in growth.incidence(checks)[0].items()}


def audit_identification(read, cube, old_chart, scaffold_chart, old_ids, old_rows, growth, target):
    replacement = identify_plan(read, old_chart, scaffold_chart, growth)
    collapsed = {
        scaffold_chart[j]: tuple(replacement.get(bit, bit) for bit in star)
        for j, star in read.items()
    }
    direct = {
        step.point: step.incoming + step.outgoing
        for step in compile_alignment(cube, old_chart, target)
    }
    mapped_owners = owner_sets(collapsed, growth)
    direct_owners = owner_sets(direct, growth)
    assert collapsed.keys() == direct.keys()
    assert Counter(mapped_owners.values()) == Counter(direct_owners.values())
    assert all(mapped_owners[bit] == direct_owners[bit] for bit in old_ids)
    assert len(mapped_owners) == 105 and len(collapsed) == 35

    # Compare literal substitution to the independent equality-and-forgetting rule.
    pure_bits = sorted({bit for support in read.values() for bit in support})
    labels = (*old_ids, *pure_bits)
    indexes = {bit: i for i, bit in enumerate(labels)}
    assert len(labels) == len(indexes) == 113
    pure_equations = growth.encode(read, indexes)
    rank = growth.binary_rank(pure_equations)
    assert rank == 35
    old_mask = (1 << len(old_ids)) - 1
    placeholder_mask = sum(1 << indexes[bit] for bit in replacement)
    kept = ((1 << len(labels)) - 1) ^ placeholder_mask
    equalities = tuple((1 << indexes[bit]) | (1 << indexes[old]) for bit, old in replacement.items())
    projected = growth.projected_equations(pure_equations + equalities, kept)
    assert growth.same_equations(projected, growth.encode(collapsed, indexes))
    assert not growth.projected_equations(projected, old_mask)
    assert cut_rows_in_chart(old_chart, old_ids) == set(old_rows)

    # The placeholder columns have full rank: retaining the other scaffold
    # distinctions uniquely fixes their former values.
    placeholder_rank = growth.binary_rank(tuple(row & placeholder_mask for row in pure_equations))
    assert placeholder_rank == 8
    scaffold_states_before = 1 << (len(pure_bits) - rank)
    scaffold_states_after = len(old_rows) << (len(pure_bits) - rank - len(old_ids))
    assert scaffold_states_before == 2 ** 70 and scaffold_states_after == 2 ** 65
    return tuple(sorted(replacement.items())), {
        "identified_placeholders": len(replacement),
        "original_distinctions_retained": len(old_ids),
        "probe_distinctions_forgotten": WIDTH - len(old_ids),
        "untouched_scaffold_distinctions_retained": len(mapped_owners) - len(old_ids),
        "final_distinctions": len(mapped_owners),
        "parity_junctions": len(collapsed),
        "old_rows_preserved": len(old_rows),
        "rank": rank,
        "placeholder_rank_with_remaining_scaffold_bits_fixed": placeholder_rank,
        "scaffold_states_before_on_97_retained": scaffold_states_before,
        "scaffold_states_after_on_97_retained": scaffold_states_after,
    }


def cross_link_control(two, probed):
    broken = {bit: set(neighbors) for bit, neighbors in two.items()}
    left = min(bit for bit in probed if len(two[bit]) < 33)
    right = min(two.keys() - probed)
    broken[left].add(right)
    broken[right].add(left)
    try:
        probe_component(broken)
    except ValueError:
        return True
    raise AssertionError("An extra cross-component threshold-two pair should fail isolation")


def run_naming(seed, growth, pure, target):
    probe_graph, _ = literal_probe_graph()
    raw_ids, old_rows = seed_fixture(0)
    probe_lifts = ProbeProjection(old_rows, PAIRS).lifts()
    assert len(probe_lifts) == len(old_rows) and min(probe_lifts) > 0
    checks = {0: tuple(range(WIDTH, WIDTH + 3))}
    rng = Random(seed) if seed else None
    stages = []
    while True:
        two, threshold_five, actual, rename = observation(probe_graph, checks, rng)
        cube, read = read_snapshot(two, threshold_five, pure)
        observed_old = tuple(rename[bit] for bit in raw_ids)
        assert set(observed_old) == cube.keys()
        assert set(map(frozenset, read.values())) == set(map(frozenset, actual.values()))
        probed = {rename[bit] for bit in probe_graph}
        assert probed == probe_component(two)
        stages.append({"junctions_read": len(read), "observed_distinctions": len(two)})
        if len(read) == 35:
            break
        moves = allocate_round(read, two.keys(), growth)
        stages[-1]["legal_next_joins"] = len(moves)
        apply_round(checks, moves, rename, growth)
        assert len(stages) <= 4
    assert [stage["junctions_read"] for stage in stages] == [1, 4, 10, 20, 35]
    assert [stage["legal_next_joins"] for stage in stages[:-1]] == [3, 6, 10, 15]
    assert [stage["observed_distinctions"] for stage in stages] == [67, 76, 94, 124, 169]
    audits = [
        audit_identification(read, cube, old, scaffold, observed_old, old_rows, growth, target)
        for old in cube_frames(cube)
        for scaffold in scaffold_frames(read, growth)
    ]
    batches = Counter(plan for plan, _ in audits)
    outcome = audits[0][1]
    assert len(audits) == 288 and all(checked == outcome for _, checked in audits)
    assert len(batches) == 144 and set(batches.values()) == {2}
    return {
        "stages": stages,
        "frame_pairs_replayed": len(audits),
        "distinct_batch_identifications": len(batches),
        "batch_identification": outcome,
        "cross_component_threshold_two_link_rejected": cross_link_control(two, probed),
    }


def run():
    growth = load_source("bootstrap_growth_for_rounds", GROWTH / "check.py")
    pure = load_pure_reader()
    target = locally_generated_target(growth)
    return {
        "pure_reader_sha256": PURE_READER_DIGEST,
        "namings": {
            str(seed): run_naming(seed, growth, pure, target)
            for seed in (0, 1801)
        },
    }


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, sort_keys=True))
