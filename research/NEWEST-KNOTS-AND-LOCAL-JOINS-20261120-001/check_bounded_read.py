"""Compare a bounded reading of a marked meeting with the length of its shortest bypass."""
from collections import Counter, deque
from itertools import combinations
import json


def distances(holders, meetings, seeds):
    neighbors = {holder: set() for holder in holders}
    for left, right in meetings:
        neighbors[left].add(right)
        neighbors[right].add(left)
    queue = deque(seeds)
    result = {holder: 0 for holder in seeds}
    while queue:
        current = queue.popleft()
        for other in neighbors[current]:
            if other not in result:
                result[other] = result[current] + 1
                queue.append(other)
    return result


def compare(holders, meetings, marked, radius):
    a, b = meetings[marked]
    remainder = [m for i, m in enumerate(meetings) if i != marked]
    read = {h for h, depth in distances(holders, meetings, (a, b)).items() if depth <= radius}
    induced = [m for m in remainder if set(m) <= read]
    local_separates = b not in distances(read, induced, (a,))
    bypass = distances(holders, remainder, (a,)).get(b)
    expected = bypass is None or bypass > 2 * radius + 1
    assert local_separates == expected
    return local_separates, bypass


def finite_census():
    counts = Counter()
    # All connected simple labelled holdings from two through five knots.
    # This isolates the permission test. Payment is checked on the physical preparations.
    for size in range(2, 6):
        holders = tuple(range(size))
        possible = tuple(combinations(holders, 2))
        for mask in range(1, 1 << len(possible)):
            meetings = [pair for i, pair in enumerate(possible) if mask & (1 << i)]
            if len(distances(holders, meetings, (0,))) != size:
                continue
            counts["connected_presentations"] += 1
            for index, meeting in enumerate(meetings):
                for radius in range(3):
                    compare(holders, meetings, index, radius)
                    counts["marked_radius_queries"] += 1
                # Each parallel name survives removal of the one tested name.
                assert compare(holders, [*meetings, meeting], index, 0) == (False, 1)
                counts["parallel_controls"] += 1
    return dict(counts)


def sharp_examples():
    cases = []
    for radius in range(1, 6):
        pair = []
        for size in (2 * radius + 2, 2 * radius + 3):
            holders = list(range(size))
            meetings = [(i, (i + 1) % size) for i in holders]
            answer, bypass = compare(holders, meetings, 0, radius)
            assert answer == (size == 2 * radius + 3)
            pair.append(dict(holders=size, other_route=bypass, permission=answer))
        cases.append(dict(radius=radius, comparisons=pair))
    return cases



def funded_threshold(size, radius):
    """Cyclic holders, with a live terminal on each of two consecutive spent holders."""
    holders = tuple(range(size + 2))
    meetings = [(i, (i + 1) % size) for i in range(size)]
    meetings.extend([(0, size), (1, size + 1)])
    spent = {0, 1}
    live = set(holders) - spent
    # Every meeting represents one distinct shared bit. Each live holder also has six private bits.
    blocks = []
    for h in holders:
        neighbors = {b if a == h else a for a, b in meetings if h in (a, b)}
        blocks.append(neighbors & live)
    pairs = {frozenset(pair) for block in blocks for pair in combinations(sorted(block), 2)}
    unheld = []
    for k in range(3, len(live) + 1):
        for group in combinations(sorted(live), k):
            if all(frozenset(pair) in pairs for pair in combinations(group, 2)):
                if not any(set(group) <= block for block in blocks):
                    unheld.append(frozenset(group))
    maximal = [g for g in unheld if not any(g < other for other in unheld)]
    ordinary = maximal + [pair for pair in pairs if not any(pair <= big for big in maximal)]
    local, bypass = compare(holders, meetings, 0, radius)
    donor_group = frozenset(blocks[0] | blocks[1])
    assert donor_group not in ordinary and not (blocks[0] & blocks[1])
    funded = {}
    for law in ("parity", "not_all_equal"):
        for rule, extra in (("whole_holdings", False), ("bounded", local)):
            roster = [*ordinary, *([donor_group] if extra else [])]
            demand = Counter(h for group in roster for h in group)
            assert all(demand[h] <= 6 for h in live)
            unary = sum(6 - demand[h] for h in live)
            assert unary > 1
            funded[law + "_" + rule] = dict(
                funded=True, actual_donors=sorted(donor_group) if extra else [],
                births=len(roster) + unary, maximum_multi_parent_demand=max(demand.values()),
            )
    return dict(holders=size + 2, cyclic_holders=size, other_route=bypass, cases=funded)


if __name__ == "__main__":
    print(json.dumps(dict(census=finite_census(), sharp=sharp_examples(),
                          paid=[funded_threshold(n, 2) for n in (6, 7)]), indent=2))
