"""Rebuild the subset-closure symmetry counts from holder incidence."""

import argparse
from collections import deque
from itertools import combinations, permutations
import json
import resource
import time


def closure(label_count):
    knots = range(1 << label_count)
    holders = sorted(
        (subset, subset | (1 << label))
        for subset in knots
        for label in range(label_count)
        if not subset & (1 << label)
    )
    places = [set() for _ in knots]
    for distinction, (first, second) in enumerate(holders):
        places[first].add(distinction)
        places[second].add(distinction)
    return holders, [tuple(sorted(place_set)) for place_set in places]


def induced_maps(holders, label_count, fix_founder):
    def swap_labels(subset, first, second):
        if (subset >> first & 1) != (subset >> second & 1):
            return subset ^ ((1 << first) | (1 << second))
        return subset

    knots = range(1 << label_count)
    knot_maps = [
        [swap_labels(subset, label, label + 1) for subset in knots]
        for label in range(label_count - 1)
    ]
    if not fix_founder:
        knot_maps.extend(
            [subset ^ (1 << label) for subset in knots] for label in range(label_count)
        )
    identities = {pair: index for index, pair in enumerate(holders)}
    for mapping in knot_maps:
        induced = tuple(
            identities[tuple(sorted((mapping[first], mapping[second])))]
            for first, second in holders
        )
        assert len(set(induced)) == len(holders)
        yield induced


def pair_orbits(unheld_pairs, distinction_maps):
    unseen = set(unheld_pairs)
    while unseen:
        first = min(unseen)
        orbit = {first}
        queue = deque([first])
        while queue:
            left, right = queue.popleft()
            for mapping in distinction_maps:
                image = tuple(sorted((mapping[left], mapping[right])))
                if image not in orbit:
                    orbit.add(image)
                    queue.append(image)
        assert orbit <= unseen
        unseen.difference_update(orbit)
        yield orbit


def interleaved_pairs(places):
    positions = [[] for _ in range(sum(map(len, places)) // 2)]
    index = 0
    for knot in places:
        for distinction in knot:
            positions[distinction].append(index)
            index += 1
    interleaved = set()
    for first, second in combinations(range(len(positions)), 2):
        start, end = positions[first]
        other_start, other_end = positions[second]
        if (start < other_start < end) != (start < other_end < end):
            interleaved.add((first, second))
    return interleaved


def closing_sign(places, anticommuting):
    """Cancel each repeated distinction by commuting past the intervening ones."""
    sign = 0
    remaining = []
    for knot in places:
        for distinction in knot:
            if distinction not in remaining:
                remaining.append(distinction)
                continue
            index = remaining.index(distinction)
            for other in remaining[index + 1 :]:
                sign ^= tuple(sorted((distinction, other))) in anticommuting
            remaining.pop(index)
    assert not remaining
    return sign


def knot_commutator(places, anticommuting):
    """Encode which products of two knots anticommute, one bit per pair."""
    result = 0
    for index, (first, second) in enumerate(combinations(places, 2)):
        swaps = sum(
            tuple(sorted((left, right))) in anticommuting
            for left in first
            for right in second
        )
        result |= (swaps % 2) << index
    return result


def kernel_basis(columns):
    pivots = {}
    relations = []
    for index, column in enumerate(columns):
        coefficients = 1 << index
        while column:
            pivot = column.bit_length() - 1
            if pivot not in pivots:
                pivots[pivot] = column, coefficients
                break
            previous_column, previous_coefficients = pivots[pivot]
            column ^= previous_column
            coefficients ^= previous_coefficients
        if not column:
            relations.append(coefficients)
    assert len(relations) + len(pivots) == len(columns)
    return relations


def selected_pairs(coefficients, orbits):
    return {
        pair
        for index, orbit in enumerate(orbits)
        if coefficients >> index & 1
        for pair in orbit
    }


def six_pair_witness(holders):
    identities = {pair: index for index, pair in enumerate(holders)}
    return {
        tuple(sorted((identities[0, first], identities[second, second | third])))
        for first, second, third in permutations((1, 2, 4))
    }


def describe_distinctions(pairs, holders, label_count):
    def subset_name(subset):
        names = [
            chr(ord("a") + label) for label in range(label_count) if subset >> label & 1
        ]
        return "{" + ",".join(names) + "}"

    return [
        [[subset_name(knot) for knot in holders[distinction]] for distinction in pair]
        for pair in sorted(pairs)
    ]


def run_closure(label_count, pilot):
    holders, places = closure(label_count)
    unheld_pairs = {
        (first, second)
        for first, second in combinations(range(len(holders)), 2)
        if set(holders[first]).isdisjoint(holders[second])
    }
    interleaved = interleaved_pairs(places)
    rule_r_failures = knot_commutator(places, unheld_pairs).bit_count()
    assert rule_r_failures > 0
    assert knot_commutator(places, set()) == closing_sign(places, set()) == 0
    for fix_founder in (False, True):
        maps = tuple(induced_maps(holders, label_count, fix_founder))
        orbits = list(pair_orbits(unheld_pairs, maps))
        assert sum(map(len, orbits)) == len(unheld_pairs)
        checked_orbits = orbits[:2] if pilot else orbits
        columns = [knot_commutator(places, orbit) for orbit in checked_orbits]
        signs = [len(orbit & interleaved) % 2 for orbit in checked_orbits]
        assert signs == [closing_sign(places, orbit) for orbit in checked_orbits]
        result = {
            "labels": label_count,
            "knots": len(places),
            "distinctions": len(holders),
            "unheld_pairs": len(unheld_pairs),
            "anticommuting_knot_pairs_under_rule_r": rule_r_failures,
            "symmetry": "fixed founder" if fix_founder else "holders only",
            "orbit_sizes": sorted(map(len, orbits)),
            "orbit_columns_checked": len(checked_orbits),
        }
        if not pilot:
            basis = kernel_basis(columns)
            sign_mask = sum(bit << index for index, bit in enumerate(signs))
            odd_basis = [vector for vector in basis if (vector & sign_mask).bit_count() % 2]
            odd_count = 1 << (len(basis) - 1) if odd_basis else 0
            result.update(
                commutation_rank=len(orbits) - len(basis),
                commuting_choices=1 << len(basis),
                even_closings=(1 << len(basis)) - odd_count,
                odd_closings=odd_count,
            )
            for vector in basis:
                pairs = selected_pairs(vector, orbits)
                assert knot_commutator(places, pairs) == 0
                sign = (vector & sign_mask).bit_count() % 2
                assert sign == closing_sign(places, pairs) == closing_sign(places[::-1], pairs)
            if label_count == 3 and fix_founder:
                witness = six_pair_witness(holders)
                assert len(witness) == 6 and witness in orbits
                assert knot_commutator(places, witness) == 0
                assert closing_sign(places, witness) == closing_sign(places[::-1], witness) == 1
                result["six_pair_witness"] = describe_distinctions(witness, holders, label_count)
            if label_count == 4 and odd_basis:
                witness = selected_pairs(min(odd_basis, key=int.bit_count), orbits)
                result["one_odd_witness_pair_count"] = len(witness)
        yield result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pilot", action="store_true")
    options = parser.parse_args()
    started = time.perf_counter()
    cpu_started = time.process_time()
    results = [result for labels in (3, 4) for result in run_closure(labels, options.pilot)]
    print(json.dumps({
        "pilot": options.pilot,
        "results": results,
        "wall_seconds": time.perf_counter() - started,
        "cpu_seconds": time.process_time() - cpu_started,
        "peak_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
    }, indent=2))


if __name__ == "__main__":
    main()
