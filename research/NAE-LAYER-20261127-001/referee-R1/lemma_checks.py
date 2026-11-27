"""Literal checks of forcing, loose projections, and changes of one distinction."""

import argparse
import itertools
import json
import time
from collections import Counter, deque
from pathlib import Path


def mask(places):
    return sum(1 << place for place in places)


def places(bits):
    while bits:
        bit = bits & -bits
        yield bit
        bits ^= bit


def allowed(rows, word):
    return all(word & row and row & ~word for row in rows)


def checks_for_sizes(max_holders=4, max_names=8):
    """One member per renaming of holders and distinctions in the stated class."""
    systems = []
    for h in range(1, max_holders + 1):
        pairs = list(itertools.combinations(range(h), 2))
        permutations = list(itertools.permutations(range(h)))
        seen = set()
        for counts in itertools.product(range(5), repeat=len(pairs)):
            shared = dict(zip(pairs, counts))
            degrees = [sum(c for group, c in shared.items() if i in group) for i in range(h)]
            if max(degrees) > 4 or sum(counts) > max_names:
                continue
            connected = {0}
            for _ in range(h - 1):
                for (a, b), c in shared.items():
                    if c and (a in connected or b in connected):
                        connected.update((a, b))
            if len(connected) != h:
                continue
            for arities in itertools.product((3, 4), repeat=h):
                loose = tuple(a - d for a, d in zip(arities, degrees))
                if min(loose) < 0 or sum(loose) + sum(counts) > max_names:
                    continue
                signature = loose + counts
                if signature in seen:
                    continue
                for perm in permutations:
                    renamed_counts = tuple(shared[tuple(sorted((perm[a], perm[b])))] for a, b in pairs)
                    seen.add(tuple(loose[i] for i in perm) + renamed_counts)
                holders = [[] for _ in range(h)]
                n = 0
                for group, multiplicity in list(zip(((i,) for i in range(h)), loose)) + list(shared.items()):
                    for _ in range(multiplicity):
                        for i in group:
                            holders[i].append(n)
                        n += 1
                systems.append((n, tuple(mask(row) for row in holders)))
    return systems


def propagate(rows, ones, zeros):
    steps = 0
    while True:
        old_steps = steps
        for row in rows:
            if row & ones and row & zeros:
                continue
            free = row & ~(ones | zeros)
            if not free:
                return False, steps
            if free & (free - 1):
                continue
            if row & ones:
                zeros |= free
            else:
                ones |= free
            steps += 1
        if old_steps == steps:
            return True, steps


def all_pins(n, rows, solutions):
    """Compare forcing against membership in projections of literal solutions."""
    positive = []
    for i in range(n):
        positive.append(sum(1 << w for w in solutions if w & (1 << i)))
    solutions_bits = sum(1 << w for w in solutions)
    counts = Counter()
    max_steps = 0
    pending = [(0, 0, 0, solutions_bits)]
    while pending:
        i, ones, zeros, compatible = pending.pop()
        if i == n:
            extends, steps = propagate(rows, ones, zeros)
            assert bool(compatible) == extends, (rows, ones, zeros)
            counts["partial_words"] += 1
            counts["extendible" if extends else "contradictory"] += 1
            counts["at_least_two_forced"] += int(steps >= 2)
            max_steps = max(max_steps, steps)
            continue
        bit = 1 << i
        pending.extend((
            (i + 1, ones, zeros, compatible),
            (i + 1, ones | bit, zeros, compatible & positive[i]),
            (i + 1, ones, zeros | bit, compatible & ~positive[i]),
        ))
    return counts, max_steps


def blocked_by(row, word):
    ones = row & word
    zeros = row & ~word
    for side in (ones, zeros):
        if side and not side & (side - 1):
            return side
    return 0


def escape(rows, s, t, d, root):
    """Find and directly play the simultaneous common changes from the proof."""
    diff = s ^ t
    k, other = sorted((row for row in rows if row & d), key=lambda row: blocked_by(row, s) != d)
    assert blocked_by(k, s) == d and blocked_by(other, s) != d
    assert root & k and not root & (diff | other)
    common_at_other = other & ~diff
    danger = common_at_other if common_at_other.bit_count() == 1 else 0
    queue = deque([root])
    parent = {root: None}
    while queue:
        here = queue.popleft()
        if here == danger:
            continue
        blockers = [row for row in rows if not row & diff and blocked_by(row, s) == here]
        assert len(blockers) <= 1
        if not blockers:
            break
        for child in places(blockers[0] ^ here):
            if child not in parent:
                parent[child] = here
                queue.append(child)
    else:
        raise AssertionError(("no safe end", rows, s, t, d, root))
    changes = []
    while here is not None:
        changes.append(here)
        here = parent[here]
    a, b = s, t
    for bit in changes:
        a ^= bit
        b ^= bit
        assert allowed(rows, a) and allowed(rows, b)
    assert allowed(rows, a ^ d) and (a ^ d ^ b).bit_count() == diff.bit_count() - 1
    return changes


def state_checks(n, rows, solutions):
    seen = {min(solutions)}
    queue = deque(seen)
    directions = {}
    while queue:
        state = queue.popleft()
        changeable = 0
        for i in range(n):
            bit = 1 << i
            other = state ^ bit
            if other in solutions:
                changeable |= bit
                if other not in seen:
                    seen.add(other)
                    queue.append(other)
        directions[state] = changeable
    assert seen == solutions
    pair_count = 0
    for i, j in itertools.combinations(range(n), 2):
        selection = (1 << i) | (1 << j)
        assert len({word & selection for word in solutions}) == 4
        pair_count += 1
    loose = sum(bit for bit in places((1 << n) - 1) if sum(bool(row & bit) for row in rows) == 1)
    full = 1 << loose.bit_count()
    ring_free = n - loose.bit_count() == len(rows) - 1
    actual = {state & loose for state in solutions}
    assert len(actual) == full - (2 if ring_free else 0)
    counts = Counter(tested_pairs=pair_count, ring_free=int(ring_free), ring_present=int(not ring_free))
    if ring_free:
        parity = {0: 0}
        queue = deque([0])
        while queue:
            i = queue.popleft()
            for j, row in enumerate(rows):
                if j not in parity and rows[i] & row:
                    parity[j] = 1 - parity[i]
                    queue.append(j)
        pattern = sum(row & loose for j, row in enumerate(rows) if parity[j])
        possible = {w & loose for w in range(1 << n)}
        assert possible - actual == {pattern, pattern ^ loose}
        for i in range(len(rows)):
            reduced = rows[:i] + rows[i + 1:]
            assert {w & loose for w in range(1 << n) if allowed(reduced, w)} == possible
            counts["ring_free_knot_deletions"] += 1
    max_changes = 0
    for s, t in itertools.combinations(sorted(solutions), 2):
        counts["unordered_state_pairs"] += 1
        diff = s ^ t
        if diff & (directions[s] | directions[t]):
            continue
        counts["stuck_pairs"] += 1
        for d in places(diff):
            k, = [row for row in rows if blocked_by(row, s) == d]
            for root in places(k & ~diff):
                changed = escape(rows, s, t, d, root)
                counts["escape_choices"] += 1
                max_changes = max(max_changes, len(changed))
    return counts, max_changes


def odd_ring_control():
    # q, x, y, z are 0, 1, 2, 3. The other shared distinctions are 4 and 5.
    holdings = [[0, 4, 1], [4, 5, 2], [5, 0, 3]]
    rows = [mask(row) for row in holdings]
    projected = lambda kept: sorted({w & 15 for w in range(64) if allowed(kept, w)})
    image = projected(rows)
    missing = [w for w in range(16) if w not in image]
    assert missing == [4, 11]
    deletions = [len(projected(rows[:i] + rows[i + 1:])) for i in range(3)]
    forget = [len({w & (15 ^ (1 << i)) for w in image}) for i in range(4)]
    assert deletions == [16] * 3 and forget == [8] * 4
    words = ["".join(str((w >> i) & 1) for i in range(4)) for w in image]
    return {
        "holdings": holdings,
        "read_distinctions": [0, 1, 2, 3],
        "allowed_words": sorted(words),
        "missing_words": ["0010", "1101"],
        "after_each_knot_deletion": deletions,
        "after_forgetting_each_distinction": forget,
    }


def path_control():
    holdings = [[0, 1, 2], [0, 1, 3], [2, 3, 4]]
    rows = [mask(group) for group in holdings]
    s, t = mask([0, 3, 4]), mask([1, 3, 4])
    d, root, danger = 1, 4, 8
    assert allowed(rows, s) and allowed(rows, t)
    for start in (s, t):
        assert allowed(rows, start ^ danger)
        assert allowed(rows, start ^ danger ^ root)
    assert not allowed(rows, s ^ danger ^ root ^ d)
    chosen = escape(rows, s, t, d, root)
    assert chosen == [16, 4]
    return {
        "holdings": holdings,
        "s": [int(bool(s & 1 << i)) for i in range(5)],
        "t": [int(bool(t & 1 << i)) for i in range(5)],
        "target": 0,
        "unsafe_common_changes_for_target": [3, 2],
        "safe_common_changes_for_target": [b.bit_length() - 1 for b in chosen],
    }


def long_path_control(levels):
    # Each common distinction at successive levels is protected by a new knot.
    holdings = [[0, 1, 2], [0, 1, 3]]
    s = mask([0, 3])
    next_name = 4
    parents = [2]
    for _ in range(levels):
        children = []
        for parent in parents:
            left, right = next_name, next_name + 1
            next_name += 2
            holdings.append([parent, left, right])
            children.extend([left, right])
            if not s & 1 << parent:
                s |= (1 << left) | (1 << right)
        parents = children
    rows = [mask(group) for group in holdings]
    t = s ^ 3
    assert allowed(rows, s) and allowed(rows, t)
    changes = escape(rows, s, t, 1, 4)
    assert len(changes) == levels + 1
    return {"knots": len(holdings), "distinctions": next_name,
            "common_changes_per_state": [b.bit_length() - 1 for b in changes]}


def three_holder_control():
    # The seven-knot pattern with every pair of distinctions held together once.
    supports = [[0, 1, 2], [0, 3, 4], [0, 5, 6], [1, 3, 5],
                [1, 4, 6], [2, 3, 6], [2, 4, 5]]
    rows = [mask(group) for group in supports]
    assert not any(allowed(rows, w) for w in range(128))
    assert propagate(rows, 0, 0) == (True, 0)
    solutions = {w for w in range(128) if allowed(rows[1:], w)}
    assert solutions and {w & 7 for w in solutions} == {0, 7}
    return {"holdings": supports, "allowed_states": 0,
            "empty_pin_forces_nothing": True, "after_deleting_first_knot": len(solutions),
            "first_three_distinctions_after_deletion": ["000", "111"]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pilot", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    start = time.perf_counter()
    systems = checks_for_sizes()
    if args.pilot:
        # Span the enumeration, including a largest case.
        systems = [systems[i] for i in sorted({0, len(systems) // 2, len(systems) - 1})]
    totals = Counter()
    by_size = Counter()
    max_steps = max_changes = 0
    for n, rows in systems:
        solutions = {w for w in range(1 << n) if allowed(rows, w)}
        pins, steps = all_pins(n, rows, solutions)
        states, changes = state_checks(n, rows, solutions)
        totals.update(pins)
        totals.update(states)
        totals["systems"] += 1
        totals["allowed_states"] += len(solutions)
        by_size[len(rows)] += 1
        max_steps, max_changes = max(max_steps, steps), max(max_changes, changes)
    controls = {
        "odd_ring": odd_ring_control(),
        "terminal_on_other_holder": path_control(),
        "five_levels_of_blocking": long_path_control(5),
        "three_holders_per_distinction": three_holder_control(),
    }
    gluing = [mask((0, 1, 2)), mask((2, 3, 4))]
    joined = [w for w in range(32) if allowed(gluing, w)]
    assert len(joined) == 18 and len({w & ~4 for w in joined}) == 14
    controls["two_ternary_knots_sharing_one_distinction"] = {
        "states": len(joined), "loose_patterns": len({w & ~4 for w in joined})}
    binary_odd = [mask(group) for group in ((0, 1), (1, 2), (2, 0))]
    assert not any(allowed(binary_odd, w) for w in range(8))
    assert propagate(binary_odd, 0, 0) == (True, 0)
    controls["two_place_odd_ring"] = {"states": 0, "empty_pin_forces_nothing": True}
    output = {
        "scope": "Connected one- through four-knot systems of arity three or four, through eight distinctions, including repeated meetings and coincident supports. Once up to renaming.",
        "pilot": args.pilot, "systems_by_knots": by_size, "totals": totals,
        "max_forcing_steps": max_steps, "max_common_changes_per_escape": max_changes,
        "controls": controls, "seconds": round(time.perf_counter() - start, 3),
    }
    data = json.dumps(output, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(data)
    else:
        print(data, end="")


if __name__ == "__main__":
    main()
