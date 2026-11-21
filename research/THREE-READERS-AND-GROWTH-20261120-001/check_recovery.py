"""Check the holder reconstruction on explicit finite families using allowed words alone."""
from collections import Counter
from itertools import combinations, product
import json

import numpy as np


def physical(pairs, loose):
    rows = [set() for _ in loose]
    count = 0
    for left, right in pairs:
        rows[left].add(count)
        rows[right].add(count)
        count += 1
    for holder, quantity in enumerate(loose):
        for _ in range(quantity):
            rows[holder].add(count)
            count += 1
    return tuple(frozenset(row) for row in rows)


def families():
    four = tuple(combinations(range(4), 2))
    for mask in range(64):
        repeated = [p for i, p in enumerate(four) if mask & (1 << i)]
        yield "four_multiply_met", physical([*four, *repeated], [0] * 4)
    for shares in product(range(1, 4), repeat=3):
        meetings = [pair for pair, n in zip(((0, 1), (1, 2), (2, 0)), shares) for _ in range(n)]
        for loose in ((0, 0, 0), (1, 0, 0)):
            candidate = physical(meetings, loose)
            if min(map(len, candidate)) >= 3:
                yield "three_multiply_met", candidate
    for n in (3, 5, 7):
        meetings = [(0, i + 1) for i in range(n)] + [(i+1, (i+1) % n+1) for i in range(n)]
        for centre_loose in (0, 1):
            yield "odd_return", physical(meetings, [centre_loose] + [0] * n)
    for count in (2, 3, 4):
        mid = count + 1
        meetings = [p for i in range(1, mid) for p in ((0, i), (0, i), (i, mid))]
        for left, right in product((0, 1), (0, 1, 2)):
            if count + right >= 3:
                yield "forced_values", physical(meetings, [left] + [0] * count + [right])


def mask(places):
    return sum(1 << i for i in places)


def exact_projection(allowed_words, places):
    part = allowed_words & mask(places)
    return (not np.any(part == 0) and not np.any(part == mask(places))
            and len(np.unique(part)) == (1 << len(places)) - 2)


def from_states(allowed, words, size):
    chosen = words[allowed]
    paired = [{x} for x in range(size)]
    identical = [{x} for x in range(size)]
    for x, y in combinations(range(size), 2):
        a, b = 1 << x, 1 << y
        base = words[(words & (a | b)) == 0]
        corners = ~allowed[base] & allowed[base | a] & allowed[base | b] & allowed[base | a | b]
        if np.any(corners):
            paired[x].add(y)
            paired[y].add(x)
        outside = chosen & ~(a | b)
        if np.all(allowed[outside | a]) and np.all(allowed[outside | b]):
            identical[x].add(y)
            identical[y].add(x)
    loose = {x for x in range(size) if exact_projection(chosen, paired[x])}
    recovered = set()
    todo = [frozenset(paired[x]) for x in loose]
    while todo:
        holder = todo.pop()
        if holder in recovered:
            continue
        recovered.add(holder)
        for x in holder - loose:
            other = frozenset((paired[x] - holder) | identical[x])
            if other not in recovered:
                todo.append(other)
    return paired, identical, loose, recovered


def check(rows):
    names = sorted(set.union(set(), *rows))
    size = len(names)
    words = np.arange(1 << size, dtype=np.int64)
    fails = np.zeros(len(words), dtype=np.int16)
    physical_failures = []
    for row in rows:
        part = words & mask(row)
        failure = (part == 0) | (part == mask(row))
        physical_failures.append(failure)
        fails += failure
    allowed = fails == 0
    kept = words[allowed]
    if not all(exact_projection(kept, row) for row in rows):
        return size, "unlawful"
    if not all(np.any(failure & (fails == 1)) for failure in physical_failures):
        return size, "implied"
    owners = [{j for j, row in enumerate(rows) if x in row} for x in names]
    paired, identical, loose, found = from_states(allowed, words, size)
    assert paired == [{y for y in names if owners[x] & owners[y]} for x in names]
    assert identical == [{y for y in names if owners[x] == owners[y]} for x in names]
    assert loose == {x for x in names if len(owners[x]) == 1}
    if loose:
        assert found == set(rows)
    return size, "open_recovered" if loose else "closed"


if __name__ == "__main__":
    counts = {}
    widths = Counter()
    for family, rows in families():
        size, answer = check(rows)
        widths[size] += 1
        counts.setdefault(family, Counter())[answer] += 1
    print(json.dumps({"checks": counts, "names_per_case": dict(sorted(widths.items()))}, indent=2))
