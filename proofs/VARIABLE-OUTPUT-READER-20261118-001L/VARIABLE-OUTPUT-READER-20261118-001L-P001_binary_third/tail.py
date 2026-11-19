"""Check every short ordinary shore on explicit fourth-shrink histories."""
from collections import defaultdict
from itertools import combinations
from pathlib import Path
import json

import frontier


def bitset(values):
    return sum(1 << value for value in values)


def labels(mask):
    return [i for i in range(mask.bit_length()) if mask & (1 << i)]


def loose_bits(rows):
    boundary = 0
    for row in rows:
        boundary ^= bitset(row)
    return set(labels(boundary))


def short_words(rows):
    """Visit each ordinary subset once, toggling one site per Gray-code step."""
    stars = list(map(bitset, rows))
    by_size = defaultdict(set)
    large_shores = defaultdict(dict)
    word = 0
    for index in range(1, 1 << len(rows)):
        toggled = (index & -index).bit_length() - 1
        word ^= stars[toggled]
        size = word.bit_count()
        if size > 5:
            continue
        assert size >= 3
        shore = index ^ (index >> 1)
        by_size[size].add(word)
        if shore.bit_count() >= 3:
            large_shores[size][shore] = word
    return by_size, large_shores


def options(rows, size):
    state, names, loose = frontier.J.literal_snapshot(rows)
    holder_groups = frontier.OLD.verify_literal_moves(rows, state, names, loose)
    available = sorted(bit for tips in loose.values() for bit in tips)
    parent = {bit: i for i, holder in enumerate(names) for bit in loose[holder]}
    return [group for group in combinations(available, size)
            if tuple(sorted(parent[bit] for bit in group)) in holder_groups]


def append(rows, inputs, outputs):
    assert tuple(sorted(inputs)) in options(rows, len(inputs))
    start = max(map(max, rows)) + 1
    return [*rows, (*inputs, *range(start, start + outputs))]


def pairs_through(words, cutoff, width):
    rows = [{i} for i in range(width)]
    for size in range(3, cutoff + 1):
        for word in words[size]:
            places = labels(word)
            for place in places:
                rows[place].update(places)
    return rows


def measure(prefix, rows, cap):
    depth = len(rows) - len(prefix) - 1
    width = max(map(max, rows)) + 1
    words, large = short_words(rows)
    n = len(prefix)
    x = loose_bits(prefix)
    assert len(x) == 5 and set(cap) < x
    assert large[5] == {(1 << n) - 1: bitset(x)}
    expected = {(1 << j) - 1: bitset(loose_bits(rows[:j])) for j in range(n + 1, len(rows) + 1)}
    assert large[4] == expected and not large[3]
    assert options(rows, 3) == []
    near = pairs_through(words, 4, width)
    tail = (x - set(cap)) | set(range(max(map(max, prefix)) + 1, width))
    base = loose_bits(rows[:n + 1])
    if not depth:
        q = rows[n][-2]
        assert near[q] == base
    else:
        fresh = set(rows[n][-2:])
        q, = fresh.intersection(rows[n + 1][:2])
        first = base.union(rows[n + 1][-2:])
        assert len(first) == 6 and near[q] == first
        assert all(first <= near[e] for e in first)
        for j in range(n + 2, len(rows)):
            q, = set(rows[j - 1][-2:]).intersection(rows[j][:2])
            y = rows[j][-1]
            assert y in near[q] and near[q] <= tail and max(near[q]) <= y
    assert len(words[3]) == 1
    return dict(width=width, binary_steps_after_fourth_shrink=depth, nonempty_shores=(1 << len(rows)) - 1,
                large_five_boundary=sorted(x), large_four_boundaries=[labels(w) for w in expected.values()],
                minimum_independent_tail_words=depth + 1)


def run():
    source = json.loads((Path(__file__).with_name("frontier.json")).read_text())
    positive = next(item["shortest_positive_history"] for item in source["distribution"]
                    if item["shrinks_before_special"] == 0 and item["total_shrinks"] == 3)
    prefix = [tuple(row) for row in positive["junction_supports"]]
    assert len(prefix) == 13
    results = []
    for cap in options(prefix, 3):
        for variant in (0, 1):
            rows = append(prefix, cap, 2)
            checks = []
            for depth in range(7):
                if depth in (0, 1, 2, 6):
                    checks.append(measure(prefix, rows, cap))
                if depth < 6:
                    binary = options(rows, 2)
                    assert len(binary) == 2
                    rows = append(rows, binary[(variant + depth) % 2], 2)
            results.append(dict(fourth_shrink_inputs=cap, choice_variant=variant,
                                complete_history=rows, checks=checks))
    assert len(results) == 4
    return dict(prefix_width=30, controls=results)


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
