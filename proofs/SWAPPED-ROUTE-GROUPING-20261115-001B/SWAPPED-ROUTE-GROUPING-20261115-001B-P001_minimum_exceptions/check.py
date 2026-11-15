"""Compare the optimizer with explicit branch orders and deletion subsets."""

from collections import Counter, defaultdict
import hashlib
from importlib.util import module_from_spec, spec_from_file_location
from itertools import combinations, product
import json
from pathlib import Path
from random import Random

import solver


ROOT = Path(__file__).resolve().parents[3]
PREDECESSOR = (ROOT / "proofs/TWO-RELAY-PADDING-20261115-001D"
               / "TWO-RELAY-PADDING-20261115-001D-P001_nested_pair_grouping/check.py")
EXPECTED_SHA256 = "1aee23c9aa74c04ede148bf94dd5134b68b3f62f5bc29b1361b4e83f4ed3ffc7"


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def predecessor():
    require(hashlib.sha256(PREDECESSOR.read_bytes()).hexdigest() == EXPECTED_SHA256,
            "predecessor changed")
    spec = spec_from_file_location("two_use_nested_reader", PREDECESSOR)
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def partitions(n):
    """Enumerate partitions into singles and pairs, named by the first position."""
    labels = list(range(n))

    def visit(left):
        if not left:
            yield tuple(labels)
            return
        first, *rest = left
        yield from visit(rest)
        for i, partner in enumerate(rest):
            labels[partner] = first
            yield from visit(rest[:i] + rest[i+1:])
            labels[partner] = partner

    yield from visit(list(range(n)))


def reorder(middles, pads, swaps):
    ms, ps = [], []
    for i, swap in enumerate(swaps):
        for branch in ((1, 0) if swap else (0, 1)):
            j = 2*i + branch
            ms.append(middles[j])
            ps.extend(pads[2*j:2*j+2])
    return ms, ps


def complete_pairs(word):
    positions = defaultdict(list)
    for i, name in enumerate(word):
        positions[name].append(i)
    require(all(len(points) <= 2 for points in positions.values()), "oracle received a third use")
    return [(name, points[0], points[1]) for name, points in positions.items() if len(points) == 2]


def conflicts(pairs):
    return [(first, second) for (first, a, b), (second, c, d) in combinations(pairs, 2)
            if a < c < b < d or c < a < d < b]


def fixed_optimum(word):
    pairs = complete_pairs(word)
    bad = conflicts(pairs)
    names = [name for name, _, _ in pairs]
    for number in range(len(names) + 1):
        for removed in combinations(names, number):
            if all(a in removed or b in removed for a, b in bad):
                return number
    raise AssertionError("all pairs can always be removed")


def confirm_trace(old, middles, pads, answer):
    swaps, removed = answer
    require(len(swaps) == len(middles) // 2 and all(s in (0, 1) for s in swaps),
            "trace contains an illegal orientation")
    require(tuple(sorted(set(removed))) == removed, "exception IDs repeated or unordered")
    word = old.named_word(*reorder(middles, pads, swaps))
    paired = {name for name, _, _ in complete_pairs(word)}
    require(set(removed) <= paired, "singletons or foreign roles removed")
    require(all(a in removed or b in removed for a, b in conflicts(complete_pairs(word))),
            "trace leaves alternating pairs")
    old.match_positions(word, omitted=removed)


def compare(old, middles, pads):
    answer = solver.optimal_order(middles, pads)
    confirm_trace(old, middles, pads, answer)
    by_order = [fixed_optimum(old.named_word(*reorder(middles, pads, swaps)))
                for swaps in product((0, 1), repeat=len(middles)//2)]
    require(len(answer[1]) == min(by_order), "global optimum differs from subset enumeration")
    return len(answer[1]), by_order[0]


def interval_control(old, middles, pads):
    """Expand full orders, cut them anywhere and test every ordered vertex pair."""
    stages = len(middles) // 2
    expanded = {}
    for swaps in product((0, 1), repeat=stages):
        word = old.named_word(*reorder(middles, pads, swaps))
        route = [0]
        for i, swap in enumerate(swaps):
            offset = 11*i + 5*swap
            route.extend([offset+j for j in range(1, 6)])
            route.append(11*(i+1))
        for j, u in enumerate(route):
            for k in range(j, len(route)):
                subword = word[j:k]
                count = len(complete_pairs(subword)) - fixed_optimum(subword)
                key = (u, route[k])
                expanded[key] = max(expanded.get(key, -1), count)
    layout = solver.Layout(middles, pads)
    scores, _ = solver._interval_tables(layout)
    for u, row in enumerate(scores):
        for v, value in enumerate(row):
            require(value == expanded.get((u, v), -1), "wrong feasible or infeasible subinterval")
    opposite_copies = 0
    for first, second in layout.copies:
        require(scores[first.end][second.start] == scores[second.end][first.start] == -1,
                "two images of one physical position appear on the same path")
        opposite_copies += 1
    return len(scores)**2, len(scores)**2 - len(expanded), opposite_copies


def sparse_labels(n, pair_count, rng):
    positions = list(range(n))
    rng.shuffle(positions)
    labels = list(range(n))
    for k in range(0, 2*pair_count, 2):
        labels[positions[k+1]] = labels[positions[k]]
    return labels


def run():
    old = predecessor()
    require(solver.optimal_order([], []) == ((), ()), "empty layout")
    histogram = Counter()
    better = 0
    for middles, pads in product(partitions(4), partitions(8)):
        optimum, supplied = compare(old, middles, pads)
        histogram[optimum] += 1
        better += optimum < supplied
    require(sum(histogram.values()) == 7640, "incomplete two-stage census")

    worst_middles = (0, 0, 2, 2)
    worst_pads = (0, 1, 0, 1, 4, 5, 4, 5)
    worst_swaps, worst_removed = solver.optimal_order(worst_middles, worst_pads)
    confirm_trace(old, worst_middles, worst_pads, (worst_swaps, worst_removed))
    worst_by_order = [fixed_optimum(old.named_word(*reorder(worst_middles, worst_pads, swaps)))
                      for swaps in product((0, 1), repeat=2)]
    require(worst_by_order == [4] * 4 and len(worst_removed) == max(histogram),
            "two-stage extremal witness")

    rng = Random(20261115)
    larger = 0
    for stages in (3, 4, 5, 6):
        for _ in range(10):
            ms = sparse_labels(2*stages, rng.randrange(min(stages, 3) + 1), rng)
            ps = sparse_labels(4*stages, rng.randrange(6), rng)
            compare(old, ms, ps)
            larger += 1
    compare(old, sparse_labels(8, 4, rng), sparse_labels(16, 8, rng))
    larger += 1

    cells, absent, incompatible_copies = interval_control(old, [0, 1, 1, 0],
                                                          [2, 0, 1, 3, 0, 1, 3, 2])
    # Each branch contains the same three names, so both legal readings are ABCABC.
    ms, ps = [0, 0], [0, 1, 0, 1]
    require(compare(old, ms, ps) == (2, 2), "single-stage crossing triple")
    layout = solver.Layout(ms, ps)
    scores, _ = solver._interval_tables(layout)
    require(scores[2][6] == -1 and scores[7][11] == 1 and scores[0][11] == 1,
            "incompatible split fixture changed")
    # Skip A on the first branch, open B, then use its other physical occurrence
    # on the opposite path. Treating an impossible 2->6 interval as empty
    # would retain B and the suffix pair C, beating the actual score 1.
    fake_score = 1 + 0 + scores[7][11]
    require(fake_score > scores[0][11], "invalid split did not distinguish the recurrence")

    # The same bare integer can belong to the two disjoint role namespaces.
    ms, ps = [0, 1], [1, 0, 2, 3]
    proper, _ = compare(old, ms, ps)
    erased = [name // 2 for name in old.named_word(ms, ps)]
    erased_minimum = min(fixed_optimum(erased), fixed_optimum(erased[3:] + erased[:3]))
    require((proper, erased_minimum) == (0, 1), "role erasure was not detected")

    # Distinct stage pairs can all improve under a swap. No whole-stage swap
    # can change the alternating order for names occupying four distinct stages.
    groups = 18
    ms = [x for i in range(groups) for x in (2*i, 2*i+1, 2*i, 2*i+1)]
    ps = list(range(2*len(ms)))
    answer = solver.optimal_order(ms, ps)
    confirm_trace(old, ms, ps, answer)
    require(not answer[1] and sum(answer[0]) == groups, "independent stage pairs")
    distinct = 15
    ms = [x for i in range(2*distinct) for x in (i % distinct, distinct+i)]
    ps = list(range(2*len(ms)))
    answer = solver.optimal_order(ms, ps)
    confirm_trace(old, ms, ps, answer)
    require(len(answer[1]) == distinct - 1, "invariant complete conflict family")
    rejected = 0
    for ms, ps in [([0], [0, 1]), ([0, 1], [0, 1]), ([0, 1], [0, 0, 0, 1]),
                   ([0, 0, 0, 1], list(range(8))), ([-1, 0], [1, 2, 3, 4]),
                   ([0, 1], [0, 1, 2, 6])]:
        try:
            solver.optimal_order(ms, ps)
        except ValueError:
            rejected += 1
    require(rejected == 6, "invalid shape, third use or out-of-range label accepted")
    return {
        "status": "passed",
        "two_stage_typed_layouts": sum(histogram.values()),
        "two_stage_explicit_orders": 4 * sum(histogram.values()),
        "two_stage_minimum_histogram": dict(sorted(histogram.items())),
        "two_stage_improved_over_supplied_order": better,
        "two_stage_worst_witness": {"middles": worst_middles, "pads": worst_pads,
                                    "swaps": worst_swaps, "removed": worst_removed,
                                    "minimum_for_each_of_four_orders": worst_by_order},
        "larger_exhaustive_layouts": larger,
        "ordered_subintervals_compared": cells,
        "unreachable_subintervals": absent,
        "incompatible_copies_of_physical_positions": incompatible_copies,
        "impossible_split_fake_retained": fake_score,
        "impossible_split_actual_retained": scores[0][11],
        "role_erasure_fake_exceptions": erased_minimum,
        "role_preservation_actual_exceptions": proper,
        "independent_swaps_in_witness": groups,
        "invariant_complete_conflict_optimum": len(answer[1]),
        "malformed_layouts_rejected": rejected,
    }


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, sort_keys=True))
