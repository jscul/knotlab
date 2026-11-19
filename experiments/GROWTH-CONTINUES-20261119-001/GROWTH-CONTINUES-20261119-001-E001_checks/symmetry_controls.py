"""Compare the constrained incidence screen with direct permutation controls."""

import itertools
import json
import random

import networkx as nx

from symmetry_check import classify


def oracle(n, blocks, opens):
    family = set(map(frozenset, blocks))
    co_block = {pair for block in blocks for pair in itertools.permutations(block, 2)}
    for image in itertools.permutations(range(n)):
        if any(v == w or opens[v] != opens[w] or (v, w) in co_block for v, w in enumerate(image)):
            continue
        if all(frozenset(image[v] for v in block) in family for block in blocks):
            return image
    return None


def require_match(n, blocks, opens):
    expected = "certified" if oracle(n, blocks, opens) is not None else "excluded_all"
    result = classify(n, blocks, opens, None)
    if result["verdict"] != expected:
        raise AssertionError((n, blocks, opens, expected, result))
    return result


def main():
    n = 4
    edges = list(itertools.combinations(range(n), 2))
    exhaustive = 0
    for mask in range(1 << len(edges)):
        blocks = [pair for i, pair in enumerate(edges) if mask >> i & 1]
        require_match(n, blocks, [2] * n)
        exhaustive += 1
    rng = random.Random(202611190560)
    randomized = 0
    for n in (5, 6, 7):
        universe = list(itertools.combinations(range(n), 2))
        for i in range(48):
            probability = (i % 12) / 11
            blocks = [pair for pair in universe if rng.random() < probability]
            opens = [rng.randint(1, 3) for _ in range(n)] if i % 4 == 0 else [2] * n
            require_match(n, blocks, opens)
            randomized += 1

    odd = require_match(3, [], [1] * 3)
    if odd["involution"] or odd["verdict"] != "certified":
        raise AssertionError("expected an order-three witness")
    exact_cycle = nx.frucht_graph()
    adjacency_maps = list(nx.algorithms.isomorphism.GraphMatcher(exact_cycle, exact_cycle).isomorphisms_iter())
    obstruction = classify(len(exact_cycle), [tuple(sorted(pair)) for pair in exact_cycle.edges()],
                           [2] * len(exact_cycle), None)
    if len(adjacency_maps) != 1 or obstruction["verdict"] != "excluded_all" \
            or obstruction["reason"] != "exhaustive constrained incidence search":
        raise AssertionError(obstruction)
    print(json.dumps({
        "exact_labeled_four_junction_cases": exhaustive,
        "randomized_cases": randomized,
        "odd_positive": odd,
        "regular_asymmetric_control": obstruction,
        "independent_adjacency_automorphisms": len(adjacency_maps),
        "closed": classify(0, [], [], None),
    }, indent=2))


if __name__ == "__main__":
    main()
