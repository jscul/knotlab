"""Independent finite reference for zero-order recognition, plus indexed scale controls."""
import json
from collections import Counter
from itertools import combinations, product
from random import Random

from solver import zero_order


def partitions(n):
    """Generate each partition into singletons and pairs once, canonically named."""
    def visit(labels, open_names, next_name):
        if len(labels) == n:
            yield tuple(labels)
            return
        yield from visit([*labels, next_name], [*open_names, next_name], next_name + 1)
        for i, name in enumerate(open_names):
            yield from visit([*labels, name], open_names[:i] + open_names[i + 1:], next_name)
    yield from visit([], [], 0)


def oriented_word(middles, pads, bits):
    """Literally permute the supplied triples. Tuple labels distinguish the two roles."""
    word = []
    for i, flipped in enumerate(bits):
        for b in (flipped, 1 - flipped):
            j = 2 * i + b
            word += [("middle", middles[j]), ("pad", pads[2*j]), ("pad", pads[2*j + 1])]
    return word


def crossings(word):
    """Reference checks endpoint inequalities for every pair of repeated names."""
    positions = {}
    for i, name in enumerate(word):
        positions.setdefault(name, []).append(i)
    pairs = [(x, p, q) for x, occurrences in positions.items() if len(occurrences) == 2
             for p, q in [occurrences]]
    return {frozenset((x, y)) for (x, a, c), (y, b, d) in combinations(pairs, 2)
            if a < b < c < d or b < a < d < c}


def exact_orders(middles, pads):
    orderings = product((0, 1), repeat=len(middles) // 2)
    return {bits: crossings(oriented_word(middles, pads, bits)) for bits in orderings}


def agree(middles, pads, reference):
    actual = zero_order(middles, pads)
    expected = [bits for bits, clashes in reference.items() if not clashes]
    assert (actual is None) == (not expected), (middles, pads, expected, actual)
    if actual is not None:
        assert isinstance(actual, tuple) and actual in expected
    return expected


def two_stage_census():
    histogram = Counter()
    counts = Counter()
    nonconstant_obstruction = None
    partition_m = list(partitions(4))
    partition_p = list(partitions(8))
    for middles, pads in product(partition_m, partition_p):
        reference = exact_orders(middles, pads)
        valid = agree(middles, pads, reference)
        histogram[len(valid)] += 1
        for mask in reference:
            counts["individual_orders"] += 1
            counts["nested_individual_orders"] += not reference[mask]
        original = reference[(0, 0)]
        if not original:
            counts["fixed_order_nested"] += 1
        elif valid:
            counts["rescued_by_swaps"] += 1
        if not valid:
            invariant = set.intersection(*reference.values())
            counts["impossible"] += 1
            if not invariant:
                counts["unsatisfiable_variable_equations_no_invariant_crossing"] += 1
                if nonconstant_obstruction is None:
                    nonconstant_obstruction = {"middles": middles, "pads": pads}
        # For every pair at once, the mixed second difference of alternation is zero.
        assert not (reference[(0, 0)] ^ reference[(0, 1)] ^
                    reference[(1, 0)] ^ reference[(1, 1)])
    assert len(partition_m) == 10 and len(partition_p) == 764
    assert sum(histogram.values()) == 7640 and counts["rescued_by_swaps"] > 0
    assert counts["unsatisfiable_variable_equations_no_invariant_crossing"] > 0
    return {"layouts": sum(histogram.values()), "middle_partitions": len(partition_m),
            "pad_partitions": len(partition_p), "counts": dict(counts),
            "nested_orders_per_layout": dict(sorted(histogram.items())),
            "example_with_inconsistent_variable_equations": nonconstant_obstruction}


def random_pairs(length, rng):
    places = list(range(length))
    rng.shuffle(places)
    names = list(range(length))
    for a, b in zip(places[::2], places[1::2]):
        if rng.random() < .8:
            names[b] = names[a]
    return names


def scrambled_nested(stages, rng):
    """Construct a nested typed word with a literal stack, then hide its branch order."""
    names = [[], []]
    next_name = [0, 0]
    unmatched = []
    for role in (0, 1, 1, 0, 1, 1) * stages:
        if unmatched and unmatched[-1][0] == role and rng.random() < .62:
            _, name = unmatched.pop()
        else:
            name = next_name[role]
            next_name[role] += 1
            unmatched.append((role, name))
        names[role].append(name)
    bits = tuple(rng.randrange(2) for _ in range(stages))
    shuffled = oriented_word(names[0], names[1], bits)
    return ([x for role, x in shuffled if role == "middle"],
            [x for role, x in shuffled if role == "pad"])


def larger_reference():
    rng = Random(15926535)
    counts = Counter()
    for r in range(3, 9):
        for _ in range(18):
            for guaranteed in (False, True):
                if guaranteed:
                    middles, pads = scrambled_nested(r, rng)
                else:
                    middles, pads = random_pairs(2 * r, rng), random_pairs(4 * r, rng)
                reference = exact_orders(middles, pads)
                valid = agree(middles, pads, reference)
                counts["layouts"] += 1
                counts["literal_orders"] += len(reference)
                counts["accepted"] += bool(valid)
                counts["rescued_by_swaps"] += bool(valid and reference[(0,) * r])
                if guaranteed:
                    assert valid
    assert counts["rescued_by_swaps"] and counts["accepted"] < counts["layouts"]
    return {**counts, "largest_exhaustive_stages": 8, "seed": 15926535}


def controls():
    def orientations(m, p):
        reference = exact_orders(m, p)
        return set(agree(m, p, reference))

    assert zero_order([], []) == ()
    assert zero_order([0, 1], [0, 1, 2, 3]) in {(0,), (1,)}
    binary = orientations([0, 1, 0, 1], list(range(8)))
    assert binary == {(0, 1), (1, 0)}
    triple = orientations(list(range(4)), [0, 1, 0, 2, 1, 3, 4, 5])
    assert triple == {(1, 0), (1, 1)}
    cancelled = orientations([0, 1, 1, 2], [0, 0, 1, 2, 3, 4, 5, 6])
    assert len(cancelled) == 4
    assert not orientations([0, 1], [0, 1, 0, 1])
    assert len(orientations([0, 1], [0, 1, 1, 0])) == 2
    # Two unary equations demand stage 0 stay fixed, and P,Q alternate in every order.
    m, p = [0, 1, 0, 2], [0, 1, 0, 1, 2, 3, 4, 5]
    obstacle = exact_orders(m, p)
    assert not agree(m, p, obstacle)
    assert [len(obstacle[bits]) for bits in product((0, 1), repeat=2)] == [1, 1, 3, 3]
    # All three pairs can be repaired individually, while two pins contradict the binary equation.
    m, p = list(range(4)), [0, 1, 2, 3, 4, 0, 1, 2]
    conflict = exact_orders(m, p)
    assert not agree(m, p, conflict) and not set.intersection(*conflict.values())
    assert [len(conflict[bits]) for bits in product((0, 1), repeat=2)] == [3, 1, 1, 1]
    # Middle ID 0 and pad ID 0 have distinct identities. Their pairs can still alternate.
    assert zero_order([0, 0], [0, 1, 0, 2]) is None
    malformed = [([0], []), ([0, 1], [0, 1, 2]), ([0, 1], [-1, 0, 1, 2]),
                 ([0, 7], [0, 1, 2, 3]), ([0, 0, 0, 1], list(range(8))), ([0, 1], [0, 0, 0, 1])]
    for m, p in malformed:
        try:
            zero_order(m, p)
        except ValueError:
            pass
        else:
            raise AssertionError(("accepted malformed input", m, p))
    return {"binary_equation_orders": sorted(binary), "three_endpoints_pin_first_swap": sorted(triple),
            "three_endpoints_even_multiplicity": len(cancelled),
            "invariant_plus_two_pins_crossing_counts": [1, 1, 3, 3],
            "inconsistent_pins_and_xor_crossing_counts": [3, 1, 1, 1],
            "malformed_inputs_rejected": len(malformed)}


def scale_controls():
    copies = 4096
    m = [name for g in range(copies) for name in (2*g, 2*g+1, 2*g, 2*g+1)]
    p = list(range(8 * copies))
    bits = zero_order(m, p)
    assert bits is not None and len(bits) == 2 * copies
    assert all(a != b for a, b in zip(bits[::2], bits[1::2]))
    # Distinct names in the same slot of four or more stages cannot be reordered across stages.
    d = 2400
    m = [name for i in range(2 * d) for name in (i % d, d + i)]
    p = list(range(8 * d))
    assert zero_order(m, p) is None
    # The reversed mate-opening order has depth d and is accepted even in fixed order.
    m = [name for i in range(2 * d) for name in (i if i < d else 2*d - 1 - i, d + i)]
    bits = zero_order(m, p)
    assert bits is not None and len(bits) == 2 * d
    return {"independent_pair_gadgets": copies, "gap_stages": 2 * copies,
            "fixed_minimum_exceptions": copies, "minimum_after_swaps": 0,
            "invariant_crossings_in_impossible_example": d * (d - 1) // 2,
            "impossible_example_stages": 2 * d, "nested_depth_control": d}


if __name__ == "__main__":
    results = {"two_stage_census": two_stage_census(), "controls": controls(),
               "larger_reference": larger_reference(), "scale": scale_controls()}
    results["status"] = "passed"
    print(json.dumps(results, indent=2, sort_keys=True))

