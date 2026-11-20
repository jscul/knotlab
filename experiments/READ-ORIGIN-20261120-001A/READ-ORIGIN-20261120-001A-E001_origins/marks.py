"""Exact physical controls for source marks and origin ambiguity."""

from collections import Counter, defaultdict, deque
from dataclasses import dataclass
from itertools import combinations
from pathlib import Path
from random import Random
import json
import sys

from pysat.solvers import Minisat22

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BASE = "ORDINARY-DYNAMICS-20261120-001A"
sys.path.insert(0, str(ROOT / "experiments" / BASE / f"{BASE}-E001_ordinary"))
from end_operator import End, from_stars, step

OUT = ROOT / "artifacts" / HERE.parent.name / HERE.name / "marks.json"
LAWS = ("parity", "nae")
ANCHOR, LEFT, RIGHT = range(3)
POINTER = ((0, 1, 2), (0, 3, 4), (1, 5, 6))


def physical(stars):
    holders = defaultdict(list)
    neighbors = [set() for _ in stars]
    assert all(len(star) == len(set(star)) for star in stars)
    for knot, star in enumerate(stars):
        for distinction in star:
            holders[distinction].append(knot)
    pairs = Counter()
    for hs in holders.values():
        assert 1 <= len(hs) <= 2
        if len(hs) == 2:
            a, b = hs
            pairs[a, b] += 1
            neighbors[a].add(b)
            neighbors[b].add(a)
    return holders, neighbors, pairs


def rank(words):
    basis = {}
    for word in words:
        while word:
            high = word.bit_length()
            if high not in basis:
                basis[high] = word
                break
            word ^= basis[high]
    return len(basis)


def check_lawful(stars):
    from_stars(stars)  # Certifies connected ordinary incidence and holder counts.
    assert all(len(row) >= 3 for row in stars)
    masks = [sum(1 << d for d in row) for row in stars]
    total_rank = rank(masks)
    assert all(total_rank - rank(word & ~mask for word in masks) == 1 for mask in masks)
    clauses = [[sign * (d + 1) for d in row] for row in stars for sign in (-1, 1)]
    count = 0
    with Minisat22(bootstrap_with=clauses) as solver:
        for row in stars:
            for a in range(1, (1 << len(row)) - 1):
                assert solver.solve(assumptions=[
                    (d + 1) * (1 if a & (1 << i) else -1) for i, d in enumerate(row)
                ])
                count += 1
    return {"parity_exact_local_projections": len(stars), "nae_legal_local_rows_extended": count}


def ordered_rows(counter):
    return [{"parents": parents, "fresh": fresh, "multiplicity": count}
            for (parents, fresh), count in sorted(counter.items())]


def full_reference(stars, law):
    turn = step(from_stars(stars), law)
    assert turn.status == "extend"
    return Counter(zip(turn.parents, turn.fresh, strict=True))


@dataclass(frozen=True)
class Birth:
    parents: tuple
    consumed: tuple
    supplied: tuple

    @property
    def star(self):
        return self.consumed + self.supplied

    @property
    def shape(self):
        return self.parents, len(self.supplied)


def ordinary_births(stars, law):
    plan = full_reference(stars, law)
    holders, _, _ = physical(stars)
    loose = {v: iter(sorted(d for d in row if len(holders[d]) == 1))
             for v, row in enumerate(stars)}
    next_name = max(holders) + 1
    births = []
    for (parents, fresh), count in sorted(plan.items()):
        for _ in range(count):
            consumed = tuple(next(loose[v]) for v in parents)
            births.append(Birth(parents, consumed, tuple(range(next_name, next_name + fresh))))
            next_name += fresh
    assert all(next(row, None) is None for row in loose.values())
    return tuple(births)


def marked_read(stars, originals, law):
    """Reconstruct the shallowest unfinished cohort using a full origin mark."""
    holders, neighbors, _ = physical(stars)
    assert originals
    distances = dict.fromkeys(originals, 0)
    todo = deque(originals)
    while todo:
        knot = todo.popleft()
        for other in neighbors[knot] - distances.keys():
            distances[other] = distances[knot] + 1
            todo.append(other)
    assert len(distances) == len(stars)
    for hs in holders.values():
        if len(hs) == 2 and not set(hs) <= originals:
            u, v = hs
            assert abs(distances[u] - distances[v]) == 1
    loose = [locations[0] for locations in holders.values() if len(locations) == 1]
    if not loose:
        return distances, None, Counter()
    level = min(distances[q] for q in loose)
    supply = {}
    for u, row in enumerate(stars):
        if distances[u] != level:
            continue
        old = sum(1 for d in row for other in holders[d] if other != u and
                  (distances[other] < level or level == 0 and other in originals))
        if len(row) > old:
            supply[u] = len(row) - old
    witness_level = max(0, level - 1)
    blocks = [tuple(neighbors[v] & supply.keys()) for v in distances if distances[v] == witness_level]
    turn = step(End(supply, tuple(blocks)), law)
    assert turn.status == "extend"
    remaining = Counter(zip(turn.parents, turn.fresh, strict=True))
    for v, star in enumerate(stars):
        if distances[v] != level + 1:
            continue
        parents = tuple(sorted(u for u in neighbors[v] if distances[u] == level))
        entry = (parents, len(star) - len(parents))
        assert remaining[entry] > 0
        remaining[entry] -= 1
    return distances, level, +remaining


def equivariance(stars, originals, law, remaining, rng):
    new_by_old = list(range(len(stars)))
    shuffled_bits = sorted(set().union(*map(set, stars)))
    rng.shuffle(new_by_old)
    fresh_names = shuffled_bits.copy()
    rng.shuffle(fresh_names)
    rename = dict(zip(shuffled_bits, fresh_names, strict=True))
    recoded = [None] * len(stars)
    for v, row in enumerate(stars):
        recoded[new_by_old[v]] = tuple(rename[d] for d in row)
    recovered = marked_read(tuple(recoded), {new_by_old[v] for v in originals}, law)[2]
    translated = Counter({(tuple(sorted(new_by_old[v] for v in parents)), fresh): n
                          for (parents, fresh), n in remaining.items()})
    assert recovered == translated


def bonds_for_pointer(stars, law):
    width = max(max(row) for row in stars) + 1
    masks = [sum(1 << d for d in row) for row in stars]
    allowed = []
    for assignment in range(1 << width):
        totals = [(assignment & mask).bit_count() for mask in masks]
        if law == "parity":
            accepted = all(n % 2 == 0 for n in totals)
        else:
            accepted = all(0 < n < len(row) for n, row in zip(totals, stars, strict=True))
        if accepted:
            allowed.append(assignment)
    minima = []
    for arity in range(1, width + 1):
        for marks in combinations(range(width), arity):
            word = sum(1 << d for d in marks)
            if any(bond & word == bond for bond in minima):
                continue
            if len({assignment & word for assignment in allowed}) != 1 << arity:
                minima.append(word)
    by_arity = {}
    for arity in (2, 3):
        values = Counter()
        for marks in combinations(range(width), arity):
            mark_word = sum(1 << d for d in marks)
            best = min((word.bit_count() for word in minima if word & mark_word == mark_word), default=0)
            values[best] += 1
        by_arity[arity] = dict(sorted(values.items()))
    return {"allowed_assignments": len(allowed), "bonds": len(minima),
            "minimum_common_bond_sizes_zero_means_absent": by_arity}


def pointer_panel():
    result = {"stars": POINTER, "fixed_old_holder": ANCHOR, "fixed_old_distinction": 2,
              "lawfulness": check_lawful(POINTER), "laws": {}}
    roots = ({ANCHOR, LEFT}, {ANCHOR, RIGHT}, {ANCHOR, LEFT, RIGHT})
    swap = {0: 1, 1: 0, 2: 2, 3: 5, 4: 6, 5: 3, 6: 4}
    assert tuple(tuple(sorted(swap[d] for d in POINTER[v])) for v in (ANCHOR, RIGHT, LEFT)) == POINTER
    holder_map, neighbors, pairs = physical(POINTER)
    assert len(holder_map) == 7 and len(neighbors[LEFT]) == len(neighbors[RIGHT]) == 1
    assert set(pairs.values()) == {1}
    for law in LAWS:
        readings = []
        for originals in roots:
            raw_source = tuple(POINTER[v] for v in sorted(originals))
            assert check_lawful(raw_source)["parity_exact_local_projections"] == len(originals)
            distances, depth, roster = marked_read(POINTER, originals, law)
            assert depth == 0
            for v in distances.keys() - originals:
                incoming = tuple(sorted(neighbors[v] & originals))
                source_order = sorted(originals)
                expected = tuple(source_order.index(u) for u in incoming)
                assert full_reference(raw_source, law)[expected, len(POINTER[v]) - len(incoming)] > 0
            equivariance(POINTER, originals, law, roster, Random(20261120029 + len(readings)))
            readings.append({"old_holders": sorted(originals), "depths": distances,
                             "remaining": ordered_rows(roster), "remaining_count": sum(roster.values())})
        assert [row["remaining_count"] for row in readings] == [3, 3, 4]
        assert ((LEFT, RIGHT), 2) in full_reference(POINTER, law)
        assert all(row["parents"] in ((ANCHOR,), (LEFT,)) for row in readings[0]["remaining"])
        assert all(row["parents"] in ((ANCHOR,), (RIGHT,)) for row in readings[1]["remaining"])

        source = POINTER[:2]
        first = ordinary_births(source, law)
        assert first[0].star == POINTER[RIGHT]
        completed = source + tuple(event.star for event in first)
        old_boundary = marked_read(completed, {ANCHOR, LEFT}, law)[2]
        new_boundary = marked_read(completed, set(range(len(completed))), law)[2]
        assert old_boundary == new_boundary == full_reference(completed, law)
        second = ordinary_births(completed, law)
        pair_a = next((i, e) for i, e in enumerate(second, len(completed)) if e.parents == (2, 3))
        expanded = completed + tuple(event.star for event in second)
        _, ordinary, sharing = physical(expanded)
        course = (ANCHOR, 2, pair_a[0], 3)
        assert all(course[(i + 1) % len(course)] in ordinary[v] for i, v in enumerate(course))
        assert max(sharing.values()) == 1
        result["laws"][law] = {"compatible_origin_readings": readings,
                               "bond_control": bonds_for_pointer(POINTER, law),
                               "true_boundary": {"knots": len(completed),
                                                 "common_next": ordered_rows(old_boundary),
                                                 "same_literal_sources_for_continuation": True},
                               "physical_cycle_after_two_steps": course}
    return result


def sparse_family(size):
    assert size >= 7 and size % 2
    meetings = {tuple(sorted((u, (u + 1) % size))) for u in range(size)}
    for u in range(size):
        meetings.add((u, u + size))
        for width in (1, 2):
            meetings.add(tuple(sorted((size + u, size + (u + width) % size))))
    stars = [[] for _ in range(2 * size)]
    for distinction, meeting in enumerate(sorted(meetings)):
        for knot in meeting:
            stars[knot].append(distinction)
    for u in range(size):
        stars[u].extend((len(meetings) + 2 * u, len(meetings) + 2 * u + 1))
    assert set(map(len, stars)) == {5}
    return tuple(map(tuple, stars))


def check_family(size):
    original = sparse_family(size)
    initial_flags = set(range(2 * size))
    result = {"odd_live_count": size, "original_count": len(original),
              "source_distinctions": len(physical(original)[0]),
              "lawfulness": check_lawful(original), "laws": {}}
    for law in LAWS:
        stars = original
        checks = []
        for age in range(1, 6):
            events = ordinary_births(stars, law)
            assert len(events) == size and all(len(event.parents) == len(event.supplied) == 2
                                               for event in events)
            advance = (1 << len(events)) - 1
            if size == 7:
                masks = set(range(advance))
            else:
                masks = {0, (1 << (size // 2)) - 1}
                for j in range(size):
                    masks.update((1 << j, advance ^ (1 << j)))
            for mask in sorted(masks):
                present = stars + tuple(event.star for j, event in enumerate(events) if mask & (1 << j))
                expected = Counter(event.shape for j, event in enumerate(events) if not mask & (1 << j))
                size_mark = {v for v, row in enumerate(present) if len(row) == 5}
                assert size_mark == initial_flags
                assert set(map(len, present[2 * size:])) <= {4}
                assert max(physical(present)[2].values()) == 1
                _, level, marked = marked_read(present, size_mark, law)
                assert level == age - 1 and marked == expected
                # Same call as the external marker benchmark after a joint renaming.
                if mask in (0, 1):
                    equivariance(present, initial_flags, law, expected, Random(20261120101 + age))
            stars += tuple(event.star for event in events)
            checks.append({"new_age": age, "births": len(events), "new_support_size": 4,
                           "snapshots_before_completion_including_empty": len(masks)})
        result["laws"][law] = checks
    return result


def repeated_calibration():
    original = ((0, 1, 2, 5), (0, 3, 4, 5))
    counts = {}
    for law in LAWS:
        stars = original
        for _ in range(3):
            stars += tuple(event.star for event in ordinary_births(stars, law))
            bundles = {pair: n for pair, n in physical(stars)[2].items() if n > 1}
            assert bundles == {(0, 1): 2}
        counts[law] = len(stars)
    return {"repeated_pair": [0, 1], "multiplicity": 2, "layers_checked": 3,
            "knots_after_three_layers": counts}


def main():
    payload = {"proof_scope": "exact finite controls of symbolic all-age statements",
               "pointer_control": pointer_panel(),
               "repeated_meeting_calibration": repeated_calibration(),
               "arity_family": [check_family(n) for n in (7, 9, 13, 17)]}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2) + "\n")


if __name__ == "__main__":
    main()
