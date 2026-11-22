"""All labelled binary supports through five names, direct coin laws and affine counts."""

from fractions import Fraction
from functools import cache
from itertools import permutations
from math import prod


def entries(mask):
    while mask:
        bit = mask & -mask
        yield bit.bit_length() - 1
        mask ^= bit


def support(words):
    return sum(1 << w for w in words)


def split(n, mask, coord):
    """Split by the coordinate, deleting its position in either returned truth table."""
    width = 1 << coord
    block = (1 << width) - 1
    halves = [0, 0]
    for offset in range(0, 1 << n, 2 * width):
        target = offset // 2
        halves[0] |= ((mask >> offset) & block) << target
        halves[1] |= ((mask >> (offset + width)) & block) << target
    return halves


@cache
def passes(n, mask):
    if not mask:
        return False
    if mask.bit_count() == 1 or n == 0:
        return True
    for coord in range(n):
        lo, hi = split(n, mask, coord)
        if lo and hi and lo.bit_count() != hi.bit_count():
            return False
        if any(part and not passes(n - 1, part) for part in (lo, hi)):
            return False
    return True


def first_bad_prefix(n, mask):
    """Deterministic unequal split; the other coordinates can follow in any order."""

    def search(m, names, prefix):
        for j, physical in enumerate(names):
            halves = split(len(names), m, j)
            counts = [h.bit_count() for h in halves]
            if all(counts) and counts[0] != counts[1]:
                return {
                    "prefix_name_values": prefix,
                    "next_name": physical,
                    "conditional_child_counts": counts,
                    "F_zero": "1/2",
                    "U_zero": str(Fraction(counts[0], sum(counts))),
                }
            for bit, h in enumerate(halves):
                if h and not passes(len(names) - 1, h):
                    return search(
                        h, names[:j] + names[j + 1 :], prefix + [(physical, bit)]
                    )
        return None

    return search(mask, tuple(range(n)), []) if mask else None


def fair_distribution(n, mask, order):
    """Physically explicit reveal tree; no conditional completion counts enter its probabilities."""
    if not mask:
        return {}
    frontier = [(tuple(entries(mask)), Fraction(1))]
    for coord in order:
        next_level = []
        for words, weight in frontier:
            options = [[w for w in words if (w >> coord) & 1 == b] for b in (0, 1)]
            feasible = [s for s in options if s]
            next_level.extend((s, weight / len(feasible)) for s in feasible)
        frontier = next_level
    assert all(len(s) == 1 for s, _ in frontier)
    return {s[0]: weight for s, weight in frontier}


def affine_masks(n):
    """Generate each vector subspace by adjoining a vector, independently of the reveal tests."""
    spaces = {frozenset({0})}
    queue = list(spaces)
    while queue:
        current = queue.pop()
        for v in range(1 << n):
            if v not in current:
                larger = current | {w ^ v for w in current}
                if larger not in spaces:
                    spaces.add(larger)
                    queue.append(larger)
    translated = {support(w ^ t for w in s) for s in spaces for t in range(1 << n)}
    return translated


def gaussian_count(n, k):
    return prod((1 << n) - (1 << j) for j in range(k)) // prod(
        (1 << k) - (1 << j) for j in range(k)
    )


def xor_closed(mask):
    if not mask:
        return False
    anchor = next(entries(mask))
    points = {w ^ anchor for w in entries(mask)}
    return all((a ^ b) in points for a in points for b in points)


def count_supports():
    out = {}
    all_good = {}
    for n in range(6):
        width = 1 << n
        total = (1 << width) - 1
        if n <= 4:
            candidates = range(1, total + 1)
            partition = {"literal_nonempty_masks": total}
        else:
            good4 = all_good[n - 1]
            halves = (0, *sorted(good4))
            highbit = width // 2
            candidates = [
                u | (v << highbit)
                for u in halves
                for v in halves
                if (u or v) and (not u or not v or u.bit_count() == v.bit_count())
            ]
            invalid_slice = (1 << width) - len(halves) ** 2
            unequal_sizes = len(halves) ** 2 - 1 - len(candidates)
            partition = {
                "excluded_by_at_least_one_failing_four_bit_slice": invalid_slice,
                "excluded_by_first_fair_split_of_unequal_nonempty_slices": unequal_sizes,
                "remaining_ordered_pairs_checked_on_all_coordinates": len(candidates),
            }
            assert sum(partition.values()) == total
        actual = {m for m in candidates if passes(n, m)}
        all_good[n] = actual
        separate = affine_masks(n)
        assert actual == separate
        for m in actual:
            assert xor_closed(m)
        dimensions = {
            k: sum(m.bit_count() == 1 << k for m in actual) for k in range(n + 1)
        }
        assert dimensions == {
            k: (1 << (n - k)) * gaussian_count(n, k) for k in range(n + 1)
        }
        if n <= 4:
            assert all(((m in actual) == xor_closed(m)) for m in candidates)
            fixed_checked = 0
            for m in sorted(actual):
                for order in permutations(range(n)):
                    law = fair_distribution(n, m, order)
                    assert all(p == Fraction(1, m.bit_count()) for p in law.values())
                    fixed_checked += 1
        else:
            fixed_checked = 0
        out[str(n)] = {
            "all_nonempty": total,
            "nonempty_passing": len(actual),
            "failing": total - len(actual),
            "empty_no_normalized_distribution": 1,
            "distinct_affine_masks": len(separate),
            "difference": 0,
            "good_by_dimension": dimensions,
            "partition": partition,
            "independent_literal_fixed_orders_checked_on_passing_supports": fixed_checked,
            "all_passing_masks_little_endian_coordinate_zero": sorted(actual),
        }
    return out


def control_checks():
    examples = {
        "zero_coordinates_singleton": (0, [0]),
        "empty_one_bit": (1, []),
        "fixed_singleton": (3, [5]),
        "full_cube": (3, range(8)),
        "even": (3, [w for w in range(8) if w.bit_count() % 2 == 0]),
        "odd": (3, [w for w in range(8) if w.bit_count() % 2]),
        "nonlinear_AND_graph": (
            3,
            [a | (b << 1) | ((a & b) << 2) for a in (0, 1) for b in (0, 1)],
        ),
        "ternary_not_all_equal": (3, range(1, 7)),
        "pinned_restricted_AND": (3, [0, 2]),
        "two_even_laws_overlap": (
            4,
            [
                w
                for w in range(16)
                if (w & 7).bit_count() % 2 == 0 and (w & 14).bit_count() % 2 == 0
            ],
        ),
        "even_width_NAE_restricted_by_odd_parity_on_same_names": (
            4,
            [w for w in range(1, 15) if w.bit_count() % 2],
        ),
    }
    out = {}
    for desc, (n, words) in examples.items():
        m = support(words)
        orders = list(permutations(range(n)))
        laws = {
            ",".join(map(str, order)): fair_distribution(n, m, order)
            for order in orders
        }
        mixture = {
            w: sum(q[w] for q in laws.values()) / len(orders) for w in entries(m)
        }
        if m:
            assert all(sum(q.values()) == 1 for q in laws.values())
        good_orders = [
            key for key, q in laws.items() if m and len(set(q.values())) == 1
        ]
        bad = first_bad_prefix(n, m)
        assert (bad is None) == (not m or passes(n, m))
        moved = support(w ^ ((1 << n) - 1) for w in entries(m))
        assert passes(n, moved) == passes(n, m)
        out[desc] = {
            "distinctions": n,
            "allowed_integer_words": list(entries(m)),
            "all_orders_pass": passes(n, m),
            "passing_fixed_orders": good_orders,
            "first_bad_prefix": bad,
            "all_fixed_order_laws": {
                k: {w: str(v) for w, v in q.items()} for k, q in laws.items()
            },
            "uniform_random_order_distribution": {
                w: str(v) for w, v in mixture.items()
            },
            "actual_uniform": {w: str(Fraction(1, m.bit_count())) for w in entries(m)},
            "rejection_chance_uniform_cube": str(1 - Fraction(m.bit_count(), 2**n)),
        }
    assert set(out["nonlinear_AND_graph"]["passing_fixed_orders"]) == {
        "0,1,2",
        "0,2,1",
        "1,0,2",
        "1,2,0",
    }
    assert (
        len(
            set(
                out["ternary_not_all_equal"][
                    "uniform_random_order_distribution"
                ].values()
            )
        )
        == 1
    )
    return out
