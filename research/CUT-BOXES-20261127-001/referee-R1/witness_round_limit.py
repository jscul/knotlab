"""Check the two finite cases in the bound on this open stage's round of birth."""

import argparse
from collections import Counter
from itertools import combinations, islice, product
import json
from time import perf_counter


def tree(code):
    remaining = Counter(code)
    live = set(range(6))
    neighbors = [set() for _ in live]
    for parent in code:
        leaf = min(x for x in live if remaining[x] == 0)
        neighbors[leaf].add(parent)
        neighbors[parent].add(leaf)
        live.remove(leaf)
        remaining[parent] -= 1
    a, b = live
    neighbors[a].add(b)
    neighbors[b].add(a)
    return neighbors


def check(limit):
    tree_count = Counter()
    for code in islice(product(range(6), repeat=4), limit):
        neighbors = tree(code)
        degrees = [len(row) for row in neighbors]
        if max(degrees) > 3:
            continue
        live = {i for i, d in enumerate(degrees) if d < 3}
        leaves = [i for i, d in enumerate(degrees) if d == 1]
        all_funded = all(len((neighbors[next(iter(neighbors[leaf]))] - {leaf}) & live) >= 2 for leaf in leaves)
        tree_count[degrees.count(3), all_funded] += 1
    # With three newest knots, the two-loose one has one parent and the other
    # two each have two parents. Distinct two-parent joins have distinct pairs.
    roster = (({u}, set(v), set(w)) for u in range(7)
              for v, w in combinations(combinations(range(7), 2), 2))
    triple_count = Counter()
    for unary, a, b in islice(roster, limit):
        triple_count["distinct_parent_rosters"] += 1
        common = bool(unary & a & b)
        candidate = [bool(unary & a), bool(unary & b), bool(a & b)]
        if candidate[:2] == [True, True]:
            triple_count["both_required_joins_have_a_witness"] += 1
        if all(candidate) and not common:
            continue  # one three-parent birth
        if candidate == [True, True, False]:
            triple_count["two_pair_joins_with_demands_2_1_1"] += 1
    return {"six_start_knots": {f"{d}_three_member_neighborhoods_all_leaves_funded_{ok}": n
                                for (d, ok), n in sorted(tree_count.items())},
            "seven_start_knots": dict(triple_count),
            "seven_start_two_joins_with_demands_2_1_1": triple_count["two_pair_joins_with_demands_2_1_1"]}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--limit", type=int)
    args = parser.parse_args()
    start = perf_counter()
    result = check(args.limit)
    result["row_limit_per_family"] = args.limit
    result["seconds"] = round(perf_counter() - start, 6)
    print(json.dumps(result, indent=2))
