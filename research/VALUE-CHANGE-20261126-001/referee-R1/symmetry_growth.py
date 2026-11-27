"""Verify founder-preserving holder incidence and symmetries after parity growth."""

import argparse
from collections import deque
from itertools import islice, permutations
import json
import resource
import time

from birth_rebuild import grow, ownership, start_supports
from symmetry_check import closure


def distances_from(start, neighbors):
    distances = {start: 0}
    remaining = deque([start])
    while remaining:
        current = remaining.popleft()
        for following in neighbors[current] - distances.keys():
            distances[following] = distances[current] + 1
            remaining.append(following)
    assert len(distances) == len(neighbors)
    return distances


def image_candidates(neighbors):
    for image in range(len(neighbors)):
        for neighbor_images in permutations(sorted(neighbors[image])):
            yield (image, *neighbor_images)


def check_automorphisms(label_count, neighbors, holders, subsets, pilot):
    distances = [distances_from(knot, neighbors) for knot in range(len(neighbors))]
    references = (0, *sorted(neighbors[0]))
    signatures = [tuple(row[ref] for ref in references) for row in distances]
    assert len(set(signatures)) == len(neighbors)
    knots_by_subset = sorted(range(len(neighbors)), key=subsets.__getitem__)

    candidates = image_candidates(neighbors)
    if pilot:
        candidates = islice(candidates, 2)
    actions = set()
    for images in candidates:
        image_lookup = {
            tuple(distances[knot][ref] for ref in images): knot for knot in range(len(neighbors))
        }
        assert image_lookup.keys() == set(signatures)
        knot_map = [image_lookup[signature] for signature in signatures]
        assert {tuple(sorted((knot_map[u], knot_map[v]))) for u, v in holders} == holders
        action = tuple(subsets[knot_map[u]] for u in knots_by_subset)
        actions.add(action)

    expected = set()
    for toggles in range(1 << label_count):
        for label_map in permutations(range(label_count)):
            expected.add(tuple(
                toggles ^ sum(1 << target for source, target in enumerate(label_map) if subset >> source & 1)
                for subset in range(1 << label_count)
            ))
    assert actions <= expected
    if not pilot:
        assert actions == expected
    return len(actions), sum(action[0] == 0 for action in actions)


def check_founder(label_count, pilot):
    start = start_supports([1, [], [label_count]])
    knots, rounds, parents, status = grow(start)
    assert status == "closed"
    owners = ownership(knots)
    assert all(len(group) == 2 for group in owners.values())
    holders = {tuple(sorted(group)) for group in owners.values()}
    assert len(holders) == len(owners)

    neighbors = [set() for _ in knots]
    for first, second in holders:
        neighbors[first].add(second)
        neighbors[second].add(first)
    assert all(len(group) == label_count for group in neighbors)

    founder_distances = distances_from(0, neighbors)
    singleton_distances = [
        distances_from(next(iter(owners[distinction] - {0})), neighbors)
        for distinction in start[0]
    ]
    subsets = [
        sum(1 << label for label, distances in enumerate(singleton_distances) if distances[knot] < depth)
        for knot, depth in sorted(founder_distances.items())
    ]
    assert subsets[0] == 0 and set(subsets) == set(range(1 << label_count))
    assert rounds == [subset.bit_count() for subset in subsets]
    for knot, actual_parents in enumerate(parents):
        subset = subsets[knot]
        expected_parents = {subset ^ (1 << label) for label in range(label_count) if subset >> label & 1}
        assert {subsets[parent] for parent in actual_parents} == expected_parents

    expected_holders, _ = closure(label_count)
    assert {tuple(sorted((subsets[u], subsets[v]))) for u, v in holders} == set(expected_holders)
    all_actions, founder_actions = check_automorphisms(label_count, neighbors, holders, subsets, pilot)
    return {
        "founder_places": label_count,
        "status": status,
        "birth_counts": [rounds.count(number) for number in range(1, max(rounds) + 1)],
        "knots": len(knots),
        "distinctions": len(owners),
        "subset_labels_by_knot": [
            [label for label in range(label_count) if subset >> label & 1] for subset in subsets
        ],
        "holder_symmetries_checked": all_actions,
        "founder_fixed_symmetries_checked": founder_actions,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pilot", action="store_true")
    options = parser.parse_args()
    started = time.perf_counter()
    started_cpu = time.process_time()
    results = [check_founder(labels, options.pilot) for labels in (3, 4)]
    print(json.dumps({
        "pilot": options.pilot,
        "results": results,
        "wall_seconds": time.perf_counter() - started,
        "cpu_seconds": time.process_time() - started_cpu,
        "peak_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
    }, indent=2))


if __name__ == "__main__":
    main()
