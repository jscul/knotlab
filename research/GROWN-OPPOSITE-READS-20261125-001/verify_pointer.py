"""Check every schedule of the fixed occupied-mark decoder at sizes five and seven."""

import json
from collections import Counter, defaultdict, deque
from functools import cache
from itertools import combinations
from pathlib import Path
from runpy import run_path


ROOT = Path(__file__).resolve().parents[2]
TICKET = "GROWN-OPPOSITE-READS-20261125-001"


def archives():
    family = ROOT / "artifacts" / TICKET / f"{TICKET}-E001_grown_preparations"
    return run_path(str(family / "check.py"))["archives"]()


def source_holdings(size):
    return tuple(tuple(sorted(((i - 1) % size, i, size + 2 * i, size + 2 * i + 1)))
                 for i in range(size))


def distances_from(pointer, neighbors):
    distance = {pointer: 0}
    queue = deque([pointer])
    while queue:
        source = queue.popleft()
        for following in sorted(neighbors[source]):
            if following not in distance:
                distance[following] = distance[source] + 1
                queue.append(following)
    assert len(distance) == len(neighbors)
    return distance


def physical_moves(grown, motion):
    stage = motion["motion_stage"].MotionStage(grown)
    mask = motion["mask"]
    holders_with_loose_marks = {stage.owners[mark][0] for mark in stage.loose}
    old_shared = tuple(sorted(
        mark for mark, holders in stage.owners.items()
        if len(holders) == 2 and holders_with_loose_marks.isdisjoint(holders)
    ))
    old_set = set(old_shared)
    old_mask = mask(old_shared)
    old_pairs = {
        pair for row in stage.stars for pair in combinations(sorted(old_set.intersection(row)), 2)
    }
    neighbors = defaultdict(set)
    for a, b in old_pairs:
        neighbors[a].add(b)
        neighbors[b].add(a)
    assert all(len(neighbors[mark]) == 2 for mark in old_shared)

    _, full_basis, shortest, _ = motion["ring_generators"](stage, pinned=False)
    by_pair = defaultdict(set)
    for mark in old_shared:
        response = stage.minimum_response(mark, pinned_loose=False)
        assert response.minimum_size == 4 and response.listed_all_supports
        for support in response.supports:
            seen = tuple(sorted(support & old_set))
            assert seen in old_pairs and mark in seen
            assert stage.allowed_change(support)
            move = mask(support)
            assert move in shortest and move & old_mask == mask(seen)
            by_pair[seen].add(move)
    assert set(by_pair) == old_pairs

    # Full-word fibers above old patterns have equal size. Each lawful
    # translation is its own inverse and commutes with the old projection.
    rank = len(full_basis)
    projection_rank = len(motion["basis"](word & old_mask for word in full_basis))
    assert projection_rank == len(old_shared)
    holder_masks = tuple(map(mask, grown))
    other_marks = sorted(set(stage.owners) - old_set)
    for pair, moves in by_pair.items():
        # Independently enumerate all possible four-mark supports containing
        # exactly this old pair and compare to the archived shortest ties.
        pair_mask = mask(pair)
        literal = set()
        for rest in combinations(other_marks, 2):
            change = pair_mask | mask(rest)
            if all((change & row).bit_count() % 2 == 0 for row in holder_masks):
                literal.add(change)
        assert literal == moves
        for move in moves:
            for word in (0, *full_basis):
                moved = word ^ move
                assert moved ^ move == word
                assert moved & old_mask == ((word & old_mask) ^ (move & old_mask))
    mixing_shifts = motion["all_words"](motion["basis"](move & old_mask for move in shortest))
    return old_shared, neighbors, by_pair, rank - projection_rank, mixing_shifts


def pointer_census(pointer, old_shared, neighbors, by_pair, motion):
    distance = distances_from(pointer, neighbors)
    routes = {}
    blind_full_shift = 0
    old_mask = motion["mask"](old_shared)
    for sender in old_shared:
        if sender == pointer:
            continue
        routes[sender] = []
        for destination in sorted(neighbors[sender]):
            if distance[destination] >= distance[sender]:
                continue
            pair = tuple(sorted((sender, destination)))
            for full_move in sorted(by_pair[pair]):
                routes[sender].append(full_move & old_mask)
                blind_full_shift ^= full_move
        assert routes[sender]
    assert ((blind_full_shift & old_mask).bit_count() % 2) == 0

    def potential(word):
        return sum(distance[mark] for mark in motion["bits"](word))

    examined = 0

    @cache
    def visit(word):
        nonlocal examined
        following = [word ^ move for sender, choices in routes.items()
                     if word & (1 << sender) for move in choices]
        if not following:
            assert not (word & ~(1 << pointer))
            return {int(bool(word))}, 0, 1
        examined += len(following)
        assert all(potential(future) < potential(word) for future in following)
        branches = [visit(future) for future in following]
        return (set().union(*(branch[0] for branch in branches)),
                1 + max(branch[1] for branch in branches),
                sum(branch[2] for branch in branches))

    words = sorted(motion["all_words"](1 << mark for mark in old_shared))
    max_firings = 0
    schedules = 0
    ordinary = {0: Counter(), 1: Counter()}
    blind = {0: Counter(), 1: Counter()}
    decoded = {0: Counter(), 1: Counter()}
    trials = {}
    for word in words:
        sign_bit = word.bit_count() % 2
        ends, maximum, count = visit(word)
        assert ends == {sign_bit}
        max_firings = max(max_firings, maximum)
        schedules += count
        baseline_pointer = (word >> pointer) & 1
        blind_pointer = ((word ^ blind_full_shift) >> pointer) & 1
        ordinary[sign_bit][baseline_pointer] += 1
        blind[sign_bit][blind_pointer] += 1
        value, = ends
        decoded[sign_bit][value] += 1
        trials[word] = (value, maximum, count)
    assert max_firings == sum(distance.values())
    assert all(blind[parity] == ordinary[parity] == {0: len(words) // 4, 1: len(words) // 4}
               for parity in (0, 1))
    summary = {
        "patterns": len(words),
        "old_projected_transitions_including_all_ties": examined,
        "complete_schedules_summed_over_starting_patterns": schedules,
        "maximum_firings": max_firings,
        "decoded_pointer_counts_by_old_parity": decoded,
        "plain_pointer_counts_by_old_parity": ordinary,
        "pointer_counts_after_blind_fixed_traversal_by_old_parity": blind,
        "blind_traversal_full_translation": list(motion["bits"](blind_full_shift)),
    }
    return summary, trials


def preparation_readout(source, pointer, old_shared, by_pair, mixing_shifts, trials, motion):
    source_stage = motion["motion_stage"].MotionStage(source)
    response = source_stage.minimum_response(pointer, pinned_loose=False)
    assert response.listed_all_supports
    mask = motion["mask"]
    old_mask = mask(old_shared)
    pulses = {
        "pulse_then_grow": {mask(support) for support in response.supports},
        "grow_then_pulse": {move for pair, moves in by_pair.items()
                            if pointer in pair for move in moves},
    }
    outcomes = {}
    for name, moves in pulses.items():
        raw_patterns = {move & old_mask for move in moves}
        # The source is zero. Growth fixes inherited values, so it does not
        # change the old projection of either arm's pulse.
        raw_parities = {pattern.bit_count() % 2 for pattern in raw_patterns}
        mixed_patterns = {pattern ^ shift for pattern in raw_patterns for shift in mixing_shifts}
        assert {pattern.bit_count() % 2 for pattern in mixed_patterns} == raw_parities
        decoded = {trials[pattern][0] for pattern in mixed_patterns}
        raw_parity, = raw_parities
        pointer_value, = decoded
        outcomes[name] = {
            "pulse_supports": [list(motion["bits"](move)) for move in sorted(moves)],
            "raw_old_parity": raw_parity,
            "mixed_old_pattern_count": len(mixed_patterns),
            "terminal_pointer_value": pointer_value,
        }
    return outcomes


def verify_relabeling(grown, source, pointer, detected, original_trials, outcomes, motion):
    old_shared, neighbors, by_pair, fiber_rank, mixing_shifts = detected
    labels = sorted({mark for row in grown for mark in row})
    # This permutation of the odd-sized roster also changes the old marks' order.
    rename = {mark: labels[(1 - 2 * i) % len(labels)] for i, mark in enumerate(labels)}
    assert len(set(rename.values())) == len(labels)
    assert any(rename[mark] not in old_shared for mark in old_shared)

    def renamed_rows(rows):
        return [tuple(sorted(rename[mark] for mark in row)) for row in reversed(rows)]

    def renamed_word(word):
        return motion["mask"](rename[mark] for mark in motion["bits"](word))

    new_shared, new_neighbors, new_by_pair, new_rank, new_mixing = physical_moves(
        renamed_rows(grown), motion
    )
    assert set(new_shared) == {rename[mark] for mark in old_shared}
    assert new_neighbors == {rename[mark]: {rename[v] for v in local}
                             for mark, local in neighbors.items()}
    assert new_by_pair == {
        tuple(sorted(rename[mark] for mark in pair)): {renamed_word(move) for move in moves}
        for pair, moves in by_pair.items()
    }
    assert new_rank == fiber_rank
    assert new_mixing == {renamed_word(move) for move in mixing_shifts}
    for mark, trials in original_trials.items():
        _, actual = pointer_census(rename[mark], new_shared, new_neighbors, new_by_pair, motion)
        assert actual == {renamed_word(word): outcome for word, outcome in trials.items()}
        if mark == pointer:
            recoded = preparation_readout(renamed_rows(source), rename[pointer], new_shared,
                                          new_by_pair, new_mixing, actual, motion)
            for name, arm in outcomes.items():
                recoded_supports = {frozenset(support) for support in recoded[name]["pulse_supports"]}
                assert recoded_supports == {frozenset(rename[m] for m in support)
                                            for support in arm["pulse_supports"]}
                for key in ("raw_old_parity", "mixed_old_pattern_count", "terminal_pointer_value"):
                    assert recoded[name][key] == arm[key]
    return {
        "holder_rows_reversed": True,
        "mark_renaming": rename,
        "transported_preparation_pointer": rename[pointer],
        "detected_shared_marks": new_shared,
        "transported_pointer_pattern_trials": sum(map(len, original_trials.values())),
    }


def verify_size(size, motion, advance, archive):
    source = source_holdings(size)
    event, grown = advance(source, "parity")
    assert event["status"] == "grown" and event["births"] == size
    if size == 5:
        assert source == tuple(tuple(sorted(row)) for row in archive["stages"]["0"]["stars"])
        assert grown == archive["stages"]["1"]["stars"]
    assert tuple(tuple(row) for row in grown[:size]) == source
    detected = physical_moves(grown, motion)
    old_shared, neighbors, by_pair, fiber_rank, mixing_shifts = detected
    old_counts = Counter(mark for row in source for mark in row)
    assert set(old_shared) == {mark for mark, count in old_counts.items() if count == 2}
    assert len(old_shared) == len(by_pair) == size and fiber_rank == 2 * size
    pointers, trials = {}, {}
    for pointer in old_shared:
        pointers[pointer], trials[pointer] = pointer_census(
            pointer, old_shared, neighbors, by_pair, motion
        )
    # The named preparation address is v0 in both source presentations.
    reference = 0
    outcomes = preparation_readout(source, reference, old_shared, by_pair,
                                   mixing_shifts, trials[reference], motion)
    values = {name: arm["terminal_pointer_value"] for name, arm in outcomes.items()}
    signs = {name: (-1)**value for name, value in values.items()}
    return {
        "grown_holdings": grown,
        "old_shared": old_shared,
        "shortest_wedges_for_each_neighbor_pair": {
            f"{a},{b}": [list(motion["bits"](move)) for move in sorted(moves)]
            for (a, b), moves in sorted(by_pair.items())
        },
        "full_words_per_old_pattern": 1 << fiber_rank,
        "terminal_full_words_per_old_parity_and_pointer": 1 << fiber_rank,
        "pointer_pattern_trials": sum(p["patterns"] for p in pointers.values()),
        "maximum_firings": max(p["maximum_firings"] for p in pointers.values()),
        "named_preparation_pointer": reference,
        "prepared_arms": outcomes,
        "terminal_pointer_for_pulse_then_grow": values["pulse_then_grow"],
        "terminal_pointer_for_grow_then_pulse": values["grow_then_pulse"],
        "decoded_sign_by_arm": signs,
        "decoded_sign_by_arm_if_convention_reversed": {name: -sign for name, sign in signs.items()},
        "relabeling_control": verify_relabeling(grown, source, reference, detected,
                                              trials, outcomes, motion),
        "per_pointer": pointers,
    }


def results():
    motion, advance, record = archives()
    return {n: verify_size(n, motion, advance, record) for n in (5, 7)}


if __name__ == "__main__":
    print(json.dumps(results(), indent=2, sort_keys=True))
