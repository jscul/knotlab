"""Count the groups in the three-knot witness directly by subsets."""
from collections import Counter
from itertools import combinations
from time import process_time
import json
import sys


def members_groups(places, members):
    meets = [{v for v, other in enumerate(places) if u != v and set(p) & set(other)}
             for u, p in enumerate(places)]
    pairs = {pair for pair in combinations(members, 2) if any(set(pair) <= row for row in meets)}
    complete = []
    for k in range(3, len(members) + 1):
        for subset in combinations(members, k):
            if all(p in pairs for p in combinations(subset, 2)):
                complete.append(frozenset(subset))
    larger = [q for q in complete if not any(q < r for r in complete)
              and not any(q <= row for row in meets)]
    groups = sorted(tuple(sorted(q)) for q in larger)
    groups.extend(sorted(p for p in pairs if not any(set(p) <= q for q in larger)))
    return groups


def direct(mark):
    # Start knots, then the round-1 join, two receiver and two sender offshoots.
    places = [[0, 3, 4, 7], [1, 2, 5, 6, 8], [0, 1, 2]]
    start_roster = members_groups(places, [0, 1])
    places.extend([[3, 5], [4, 1], [7, 1], [6, 0], [8, 0]])
    first_demand = members_groups(places, range(3, 8))
    owed = Counter(p for group in first_demand for p in group)
    assert set(owed.values()) == {4}
    for u in range(3, 8):
        first_fresh = 9 + 4 * (u - 3)
        places[u].extend(range(first_fresh, first_fresh + 4))
    if mark:
        places[6].append(29)
    # Round-2 parents are the ten pairs of the five members, in this order.
    # Each uses the next loose distinction of its parents. The third input
    # is the oldest eligible distinction held by a knot meeting both.
    second_inputs = [[9, 13, 0], [10, 17, 0], [11, 21, 1], [12, 25, 1],
                     [14, 18, 0], [15, 22, 2], [16, 26, 2], [19, 23, 2],
                     [20, 27, 2], [24, 28, 1]]
    if mark:
        second_inputs.append([29, 1])
    for inputs, parents in zip(second_inputs, list(combinations(range(3, 8), 2)) + ([(6,)] if mark else [])):
        counts = Counter(d for places_u in places for d in places_u)
        common = [u for u, row in enumerate(places)
                  if u not in parents and all(set(row) & set(places[p]) for p in parents)]
        exclude = set.union(*(set(places[p]) for p in parents))
        eligible = {d for u in common for d in places[u] if counts[d] >= 2 and d not in exclude}
        assert min(eligible) == inputs[-1]
        assert all(counts[d] == 1 and d in places[p] for p, d in zip(parents, inputs[:-1]))
    places.extend(second_inputs)
    groups = members_groups(places, range(8, len(places)))
    own = [list(group) for group in groups if 12 in group]
    return {"mark": mark, "initial_groups": start_roster, "initial_usable": [3, 3],
            "round_two_group_count_per_member": [owed[u] for u in range(3, 8)],
            "round_two_usable": [4, 4, 4, 5 if mark else 4, 4], "receiver_parents": [4, 5],
            "demand_groups_of_receiver_join": own, "fresh": len(own), "places": 3 + len(own)}


if __name__ == "__main__":
    started = process_time()
    cases = [False] if sys.argv[1] == "pilot" else [False, True]
    print(json.dumps({"direct": [direct(mark) for mark in cases],
                      "cpu_seconds": round(process_time() - started, 6)}, indent=2))
