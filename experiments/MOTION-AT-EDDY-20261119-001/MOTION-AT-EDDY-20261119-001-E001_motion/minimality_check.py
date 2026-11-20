"""Literal closed ring states and independent symmetry and speed controls."""

import argparse
import json
from itertools import combinations
from pathlib import Path

from motion_stage import load_case_record


HERE = Path(__file__).resolve().parent
OUT = HERE.parents[2] / "artifacts" / HERE.parent.name / HERE.name / "minimality_check.json"
PHASES = ((0, 1, 4), (0, 1, 2, 4), (0, 1, 2, 4, 5), (0, 1, 2, 5))
TOGGLE = (2, 5, 4, 0)


def xor(rows):
    value = frozenset()
    for row in rows:
        value ^= frozenset(row)
    return value


def ring_reading(case):
    data = load_case_record(case)
    source = data["stages"]["0"]["stars"]
    stars = list(map(frozenset, data["stages"]["1"]["stars"]))
    n = len(source)
    rim = []
    for i in range(n):
        e, = set(source[i]) & set(source[(i + 1) % n])
        rim.append(e)
    slots = []
    for i in range(n):
        prev, nxt = (i - 1) % n, (i + 1) % n
        c, = [s for s in stars[n:] if s & stars[prev] and s & stars[nxt]]
        slots.append(frozenset((rim[prev], rim[i])) | (c & stars[prev]) | (c & stars[nxt]))
    for i, slot in enumerate(slots):
        assert len(slot) == 4 and all(len(slot & s) % 2 == 0 for s in stars)
        assert {j for j, other in enumerate(slots) if j != i and slot & other} == {(i-1) % n, (i+1) % n}
    return stars, frozenset(rim), slots


def closed_bare_five():
    stars, rim, slots = ring_reading("R0")
    ordinary = sorted(set.union(set(), *(set(row) for row in slots), set(rim)))
    assert len(ordinary) == 15
    masks = [sum(1 << ordinary.index(e) for e in row if e in ordinary) for row in stars]
    allowed = {
        frozenset(ordinary[j] for j in range(15) if mask & (1 << j))
        for mask in range(1 << 15) if all((mask & s).bit_count() % 2 == 0 for s in masks)
    }
    pred, reflection_hist = set(), {}
    for mask in range(32):
        selected = {i for i in range(5) if mask & (1 << i)}
        word = xor(slots[i] for i in selected)
        fixed = [axis for axis in range(5) if {(axis - i) % 5 for i in selected} == selected]
        assert fixed
        if len(selected) not in (0, 5):
            step = {(i + 1) % 5 for i in selected}
            assert all({(axis - i) % 5 for i in step} != step for axis in fixed)
        for z in (frozenset(), rim):
            pred.add(z ^ word)
            reflection_hist[len(fixed)] = reflection_hist.get(len(fixed), 0) + 1
    assert pred == allowed and len(pred) == 64
    return dict(ordinary_bits=len(ordinary), full_assignments_tested=1 << 15,
                physical_closed_states=len(allowed), reflections_fixing_each_state={
                    str(k): v for k, v in sorted(reflection_hist.items())})


def full_orbit():
    stars, rim, slots = ring_reading("R31")
    n = len(slots)
    states, weights = set(), []
    for direction in (-1, 1):
        initial = xor(slots[(direction * j) % n] for j in PHASES[0])
        state = initial
        for t in range(4 * n):
            i, p = divmod(t, 4)
            expected = xor(slots[(direction * (i + j)) % n] for j in PHASES[p])
            assert expected == state and state not in states
            assert all(len(state & s) % 2 == 0 for s in stars)
            assert all(len((state ^ rim) & s) % 2 == 0 for s in stars)
            states.add(state)
            if direction == 1 and i == 0:
                weights.append(len(state))
            state ^= slots[(direction * (i + TOGGLE[p])) % n]
        assert state == initial
    shifted = xor(slots[j+1] for j in PHASES[0])
    initial = xor(slots[j] for j in PHASES[0])
    return dict(physical_states_across_both_orbits=len(states), directed_period=4 * n,
                period_in_completed_copies=n, phase_weights=weights,
                changed_bits_between_consecutive_copies=len(initial ^ shifted))


def frame_reading():
    _, rim, slots = ring_reading("R31")
    n = len(slots)

    def other(current, previous):
        neighbors = {(current - 1) % n, (current + 1) % n}
        assert previous in neighbors
        next_index, = neighbors - {previous}
        return next_index

    def travel(frames):
        a, b, c = frames
        prev = slots.index(a ^ b)
        cur = slots.index(b ^ c)
        return b, c, c ^ slots[other(cur, prev)]

    def reverse(frames):
        b, c, d = frames
        cur = slots.index(b ^ c)
        nxt = slots.index(c ^ d)
        return b ^ slots[other(cur, nxt)], b, c

    initial = (frozenset(), slots[0], slots[0] ^ slots[1])
    frames, seen = initial, set()
    bias = rim ^ slots[12]
    while frames not in seen:
        seen.add(frames)
        new = travel(frames)
        assert reverse(new) == frames
        assert travel(tuple(x ^ bias for x in frames)) == tuple(x ^ bias for x in new)
        frames = new
    assert frames == initial and len(seen) == 2*n
    return dict(physical_triple_period=len(seen), individual_change_period=n,
                checked_inverse_and_simultaneous_offset=True)


def latitude_of_claim():
    # A legitimate bare seven-ring has a chiral closed state outside the pure carrier span.
    n = 7
    occupied = {0, 1, 3}
    slots = [{i, (i - 1) % n, n + 2*i, n + 2*i + 1} for i in range(n)]
    rim_offset = frozenset(range(n)) ^ xor(slots[i] for i in occupied)
    assert not any({(a - i) % n for i in occupied} == occupied for a in range(n))
    assert len(rim_offset) == 9
    bins = {}
    for stride in (1, 2, 4):
        phases = [set(stride*x for x in phase) for phase in PHASES]
        for j in range(4):
            target = phases[j+1] if j < 3 else {x + stride for x in phases[0]}
            assert phases[j] ^ target == {stride*TOGGLE[j]}
        bins[str(stride)] = dict(events=4, displacement=stride, reader_radius=6*stride)
    return dict(outside_pure_span=dict(bare_circumference=n, coefficients=sorted(occupied),
                                      old_rim_offset=True, physical_weight=len(rim_offset)),
                rescaled_four_guard_laws=bins)


def light_chiral_moves(n):
    """Check the invariant single occupied site on every light, chiral 3-to-4 move."""
    def pair_distance(i, j):
        return min((i-j) % n, (j-i) % n)

    def lone_site(word):
        if len(word) == 4:
            return next(i for i in word if (i-1) % n not in word and (i+1) % n not in word)
        for gap in (1, 2):
            pairs = [(i, j) for i, j in combinations(word, 2) if pair_distance(i, j) == gap]
            if pairs:
                assert len(pairs) == 1
                anchor, = word.difference(pairs[0])
                return anchor
        return None

    anchors = {}
    for k in (3, 4):
        for values in combinations(range(n), k):
            word = frozenset(values)
            runs = sum((i-1) % n not in word for i in word)
            if 2*(k+runs) > 12:
                continue
            # A fixing reflection must send the first occupied site to some occupied site.
            if any(all((values[0]+j-i) % n in word for i in word) for j in word):
                continue
            anchors[word] = lone_site(word)
    moves = 0
    for word, anchor in anchors.items():
        if len(word) == 4:
            assert anchor is not None
            for i in word:
                prior = word - {i}
                if prior in anchors:
                    assert anchors[prior] == anchor
                    moves += 1
    return dict(circumference=n, light_chiral_words=len(anchors),
                adjacent_word_pairs=moves, every_move_preserves_one_physical_position=True)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--verify", action="store_true")
    args = p.parse_args()
    result = dict(bare_five=closed_bare_five(), bare_thirty_one=full_orbit(),
                  three_frame_control=frame_reading(), scope_controls=latitude_of_claim(),
                  peak_weight_controls=[light_chiral_moves(n) for n in (13, 31)])
    if args.verify:
        assert result == json.loads(OUT.read_text())
        print("Verified all 64 closed five-ring states, the 31-ring periods, affine memory and scope controls.")
    else:
        OUT.write_text(json.dumps(result, indent=2) + "\n")


if __name__ == "__main__":
    main()
