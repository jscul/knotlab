"""Literal finite controls for pure descendants of a held subset."""

import argparse
from collections import Counter
from itertools import combinations
import json
from pathlib import Path
import random

from interface_check import anchored_groups, children, maximal_blocks, wired_realization


def graph_fixture(n, mask):
    """Any graph occurs by giving each deleted edge a private third candidate."""
    base = set(range(n))
    points = set(base)
    blocks = {frozenset(base)}
    for j, (a, b) in enumerate(combinations(range(n), 2)):
        if mask & (1 << j):
            continue
        z = len(points)
        points.add(z)
        blocks.update((frozenset((a, z)), frozenset((b, z))))
    return base, points, blocks


def mixed_fixture(rng):
    base = set(range(5))
    points = set(range(8))
    blocks = {frozenset(base)}
    for z in points - base:
        for a in rng.sample(sorted(base), rng.randrange(2, 5)):
            block = {z, a}
            if rng.randrange(2):
                block.add(rng.choice(sorted(points - block)))
            blocks.add(frozenset(block))
    for pair in combinations(sorted(points - base), 2):
        if rng.randrange(2):
            blocks.add(frozenset(pair))
    return base, points, maximal_blocks(blocks)


def positive_age_realization(points, desired_blocks):
    """One funded physical step produces the specified held blocks."""
    block_rows = sorted((sorted(row) for row in desired_blocks))
    intended = []
    fresh = len(block_rows)
    for x in sorted(points):
        group = [i for i, b in enumerate(block_rows) if x in b] + list(range(fresh, fresh + 3))
        fresh += 3
        intended.append(frozenset(group))
    old_pairs = {frozenset(ab) for row in intended for ab in combinations(sorted(row), 2)}
    old_points = set(range(fresh))
    maximal = anchored_groups(old_points, old_pairs, old_points)
    old_holders = sorted(old_pairs | (maximal - set(intended)), key=lambda b: sorted(b))
    produced = anchored_groups(old_points, set(old_holders), old_points)
    assert produced == set(intended)
    old_physical = [[i for i, b in enumerate(old_holders) if x in b] for x in range(fresh)]
    opens = Counter(x for g in intended for x in g)
    wired_realization(old_physical, opens)
    assert maximal_blocks(children(intended).values()) == set(desired_blocks)
    return dict(old_live_old_holder_ids=old_physical,
                open_distinctions=[opens[x] for x in sorted(old_points)],
                birth_parents_labelled_in_desired_order=[sorted(g) for g in intended])


def full_crossing_witness(n=7):
    missing_bit_01 = 1
    mask = (1 << (n * (n - 1) // 2)) - 1 - missing_bit_01
    base, points, blocks = graph_fixture(n, mask)
    source_blocks = sorted(sorted(b) for b in blocks)
    physical = positive_age_realization(points, blocks)
    pure = {x: frozenset((x,)) for x in base}
    previous_pure = {}
    current_parents = []
    generations, crossings = [], []
    for size in range(2, n + 1):
        groups = sorted(anchored_groups(points, blocks, points), key=lambda row: sorted(row))
        if size >= 3:
            u = frozenset(range(size))
            by_support = {a: x for x, a in pure.items()}
            by_previous = {a: x for x, a in previous_pure.items()}
            qa, qb = by_support[u - {0}], by_support[u - {1}]
            shared = by_previous[u - {0, 1}]
            ra, rb = by_previous[u - {0, 2}], by_previous[u - {1, 2}]
            witness = next(y for y, row in enumerate(current_parents) if {ra, rb} <= row)
            assert witness not in pure and shared not in current_parents[witness]
            marked = {qa, qb, witness}
            assert not any(marked <= block for block in blocks)
            covering = next(i for i, g in enumerate(groups) if marked <= g)
            crossings.append(dict(target_size=size, target_original_labels=sorted(u),
                                  two_available_facets=[qa, qb], common_old_parent=shared,
                                  two_old_parents_in_mixed_witness=[ra, rb],
                                  mixed_witness=witness, mixed_witness_parents=sorted(current_parents[witness]),
                                  actual_next_mixed_child=covering,
                                  actual_next_mixed_child_parents=sorted(groups[covering])))
        previous_pure, pure = pure, {
            i: frozenset().union(*(pure[x] for x in g))
            for i, g in enumerate(groups) if g <= pure.keys()
        }
        generations.append([sorted(g) for g in groups])
        current_parents = groups
        points = set(range(len(groups)))
        blocks = maximal_blocks(children(groups).values())
    return dict(initial_held_blocks=source_blocks, pure_initial_points=sorted(base),
                positive_age_physical_realization=physical, complete_later_parent_lists=generations,
                missing_face_witnesses=crossings)


def exercise(base, points, blocks):
    # Use exact group demand at the source. All children here have ≥2 parents.
    pure = {v: frozenset((v,)) for v in base}
    edges = set()
    sizes = [len(pure)]
    external_overlap = False
    for j in range(2, len(base) + 2):
        groups = sorted(anchored_groups(points, blocks, points), key=lambda row: sorted(row))
        if j == 2:
            edges = {g for g in groups if g <= base}
            assert all(len(g) == 2 for g in edges)
        expected = {
            frozenset(u) for u in combinations(sorted(base), j)
            if all(frozenset(pair) in edges for pair in combinations(u, 2))
        }
        next_pure = {}
        mixed = []
        pair_uses = Counter(pair for g in groups for pair in combinations(sorted(g), 2))
        for i, group in enumerate(groups):
            if not group <= pure.keys():
                mixed.append(group)
                continue
            support = frozenset().union(*(pure[v] for v in group))
            wanted_parents = {support - {u} for u in support}
            assert len(group) == j and {pure[v] for v in group} == wanted_parents
            assert all(pair_uses[pair] == 1 for pair in combinations(sorted(group), 2))
            next_pure[i] = support
        external_overlap |= any(len(a & b) >= 2 for a, b in combinations(mixed, 2))
        assert len(next_pure) == len(expected) and set(next_pure.values()) == expected
        sizes.append(len(next_pure))
        if not next_pure or len(groups) == 1:
            # A sole birth on the connected exact-demand stage consumes all loose bits.
            break
        blocks = maximal_blocks(children(groups).values())
        points = set(range(len(groups)))
        pure = next_pure
    return sizes, external_overlap


def relay():
    # A held triple is one whole component; a separate held pair supplies other births.
    blocks = {frozenset((0, 1, 2)), frozenset((3, 4))}
    parents = [[0, 1], [0, 2], [0, 3], [4, 5], [4, 6]]
    pure = {0, 1, 2}
    trace = []
    for age in range(7):
        points = set(range(len(parents)))
        groups = sorted(anchored_groups(points, blocks, points), key=lambda g: sorted(g))
        demand = Counter(v for g in groups for v in g)
        spare = {v: max(1, 3 - len(parents[v]), demand[v]) - demand[v] for v in points}
        births = [sorted(g) for g in groups] + [[v] for v in sorted(points) for _ in range(spare[v])]
        assert len(births) >= 2
        trace.append(dict(age=age, pure=len(pure), pure_unary=sum(len(parents[v]) == 1 for v in pure)))
        pure = {v for v, p in enumerate(births) if set(p) <= pure}
        parents = births
        blocks = maximal_blocks(children(parents).values())
    assert [x["pure"] for x in trace[:5]] == [3, 3, 1, 1, 2]
    return trace


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group()
    action.add_argument("--output", type=Path)
    action.add_argument("--verify", type=Path)
    args = parser.parse_args()
    coverage = {}
    for n in (4, 5):
        population = 1 << (n * (n - 1) // 2)
        for mask in range(population):
            exercise(*graph_fixture(n, mask))
        coverage[str(n)] = population
    larger = []
    for n in (6, 7, 8, 9):
        full = (1 << (n * (n - 1) // 2)) - 1
        sizes, _ = exercise(*graph_fixture(n, full - 1))
        larger.append(dict(base=n, one_missing_edge=sizes))
    rng = random.Random(202611192049)
    intersecting = 0
    for _ in range(80):
        _, overlap = exercise(*mixed_fixture(rng))
        intersecting += int(overlap)
    result = dict(labeled_graphs=coverage, larger=larger, interfering_controls=80,
                  controls_with_two_mixed_groups_sharing_a_pair=intersecting,
                  random_seed=202611192049, whole_component_relay=relay(),
                  one_missing_edge_full_witness=full_crossing_witness())
    text = json.dumps(result, indent=2) + "\n"
    if args.verify:
        assert json.loads(args.verify.read_text()) == result
        print("Verified the clique layers, exclusive pairs, full missing-face witnesses and relay.")
    elif args.output:
        args.output.write_text(text)
    else:
        print(text)


if __name__ == "__main__":
    main()
