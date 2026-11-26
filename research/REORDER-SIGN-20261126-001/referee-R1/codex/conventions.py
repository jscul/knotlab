"""Exact left and right exterior multiplication on the grown ternary.

Run with python3 -B. All coefficients have the common positive magnitude
1/sqrt(32). The check retains their signs and compares the same named words.
"""

import itertools
import json
from collections import Counter


PARENTS = ("a", "b", "c")
MODES = tuple(mode for x in PARENTS for mode in (x, x + "y", x + "z"))
RANK = {mode: index for index, mode in enumerate(MODES)}


def insert(state, mode, side):
    """Multiply by an unoccupied mode on the indicated side."""
    occupied, sign = state
    index = RANK[mode]
    assert not occupied & (1 << index)
    if side == "left":
        passed = occupied & ((1 << index) - 1)
    else:
        assert side == "right"
        passed = occupied >> (index + 1)
    return occupied | (1 << index), sign * (-1) ** (passed.bit_count() % 2)


def birth(state, modes, side):
    """An internal yz monomial always means c_y^dagger c_z^dagger."""
    sequence = reversed(modes) if side == "left" else modes
    for mode in sequence:
        state = insert(state, mode, side)
    return state


def prepare(parent_order, child_order, old, fresh, parent_side, child_side):
    state = 0, 1
    for parent in parent_order:
        if parent in old:
            state = insert(state, parent, parent_side)
    for child in child_order:
        state = birth(state, fresh[child], child_side)
    return state


def words():
    for old_bits in itertools.product((0, 1), repeat=3):
        if sum(old_bits) % 2:
            continue
        old = {x for x, present in zip(PARENTS, old_bits) if present}
        for first_bits in itertools.product((0, 1), repeat=3):
            fresh = {}
            for x, first in zip(PARENTS, first_bits):
                second = first ^ (x in old)
                pair = ((x + "y", first), (x + "z", second))
                fresh[x] = tuple(name for name, present in pair if present)
            yield old, fresh


def occupied_relative_sign(parent_order, child_order, old):
    listed = [x for x in parent_order if x in old]
    inversions = sum(
        child_order.index(first) > child_order.index(second)
        for first, second in itertools.combinations(listed, 2)
    )
    return (-1) ** inversions


def check_prefixes(old, fresh, child_order, counts):
    state = 0, 1
    for parent in PARENTS:
        if parent in old:
            state = insert(state, parent, "right")
    for child in child_order:
        modes = fresh[child]
        append = birth(state, modes, "right")
        local = birth(state, modes, "left")
        occupied = state[0]
        prefix_sign = (-1) ** ((len(modes) % 2) * (occupied.bit_count() % 2))
        assert append == (local[0], local[1] * prefix_sign)
        counts["prefix_string_stage_agreements"] += 1
        counts["uncompensated_stage_differences"] += append != local
        state = append


def middle_birth_witness(previous):
    occupied = sum(1 << RANK[mode] for mode in previous)
    local = birth((occupied, 1), ("by",), "left")
    append = birth((occupied, 1), ("by",), "right")
    assert local[0] == append[0]
    return {
        "occupied_before_b_child": previous,
        "ordinary_left_sign": local[1],
        "early_first_append_sign": append[1],
        "compensating_string": local[1] * append[1],
    }


def run():
    counts = Counter()
    for old, fresh in words():
        k = len(old)
        reversal = (-1) ** (k * (k - 1) // 2)
        internal = (-1) ** sum(len(fresh[x]) == 2 for x in PARENTS)
        reversed_pairs = {x: tuple(reversed(fresh[x])) for x in PARENTS}
        for child_order in itertools.permutations(PARENTS):
            check_prefixes(old, fresh, child_order, counts)
            for parent_order in itertools.permutations(PARENTS):
                args = parent_order, child_order, old, fresh
                append = prepare(*args, "right", "right")
                local_fixed_start = prepare(*args, "right", "left")
                local_from_vacuum = prepare(*args, "left", "left")
                parent_rev = prepare(parent_order[::-1], child_order, old, fresh,
                                     "right", "right")
                child_rev = prepare(parent_order, child_order[::-1], old, fresh,
                                    "right", "right")
                full_rev = prepare(parent_order, child_order, old, reversed_pairs,
                                   "left", "left")
                assert local_fixed_start == (append[0], append[1] * reversal)
                assert child_rev == parent_rev == local_fixed_start
                assert local_from_vacuum == append
                assert local_from_vacuum[1] == (
                    reversal * occupied_relative_sign(parent_order, child_order, old)
                )
                assert full_rev == (local_from_vacuum[0], local_from_vacuum[1] * internal)
                counts["history_word_comparisons"] += 1
                counts["fixed_start_left_vs_append_differences"] += local_fixed_start != append
                counts["chronological_left_vs_append_agreements"] += local_from_vacuum == append
                counts["whole_mode_reversal_vs_chronological_left_differences"] += full_rev != local_from_vacuum
    witnesses = [middle_birth_witness(["b", "c"]), middle_birth_witness(["a", "ay", "b"])]
    assert [case["compensating_string"] for case in witnesses] == [1, -1]
    return {"counts": dict(counts), "middle_birth": witnesses}


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
