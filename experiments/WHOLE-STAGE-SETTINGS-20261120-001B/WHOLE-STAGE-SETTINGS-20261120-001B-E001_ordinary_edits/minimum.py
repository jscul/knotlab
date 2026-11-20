"""Finite lower-bound checks on the declared domains of the small constructions."""

from collections import Counter
from itertools import combinations


def meeting_graph(size, meetings):
    graph = [set() for _ in range(size)]
    for a, b in meetings:
        graph[a].add(b)
        graph[b].add(a)
    return graph


def reached(graph, starts, omit=None):
    todo = list(starts)
    visited = set(todo)
    for holder in todo:
        fresh = graph[holder] - visited - {omit}
        visited.update(fresh)
        todo.extend(fresh)
    return visited


def skeletons(size):
    pairs = tuple(combinations(range(size), 2))
    for mask in range(1 << len(pairs)):
        if mask.bit_count() < size - 1:
            continue
        edges = tuple(pair for i, pair in enumerate(pairs) if mask & (1 << i))
        graph = meeting_graph(size, edges)
        if len(reached(graph, (0,))) == size:
            yield edges, graph


def projected_parity_possible(graph, live):
    # Join every loose distinction to one exterior holder. A written star is a
    # minimal nonempty parity support iff everything else still reaches exterior.
    return all(len(reached(graph, live - {node}, node)) == len(graph) - 1 for node in range(len(graph)))


def parent_groups(graph, live):
    live = tuple(sorted(live))
    candidate = {pair for pair in combinations(live, 2) if graph[pair[0]] & graph[pair[1]]}
    groups = []
    covered = set()
    for width in range(len(live), 2, -1):
        for group in combinations(live, width):
            within = set(combinations(group, 2))
            if within <= candidate and not set.intersection(*(graph[h] for h in group)):
                if not any(set(group) < set(larger) for larger in groups):
                    groups.append(group)
                    covered.update(within)
    return tuple(sorted(groups) + sorted(candidate - covered))


def bounded_shared_counts(slots, extra):
    if slots == 0:
        yield ()
        return
    for add in range(extra + 1):
        for rest in bounded_shared_counts(slots - 1, extra - add):
            yield (1 + add, *rest)


def smallest_funding(ceiling, separate_written_meeting, *, parity=True, literal_lawful=None):
    solutions = []
    tested = Counter()
    for size in range(2, 6):
        for edges, graph in skeletons(size):
            tested[f"connected_skeletons_{size}"] += 1
            if graph[0] & graph[1] or separate_written_meeting and 1 in graph[0]:
                continue
            for mask in range(1 << (size - 2)):
                live = {0, 1} | {i for i in range(2, size) if mask & (1 << (i - 2))}
                demand = Counter(h for group in parent_groups(graph, live) for h in group)
                if demand[0] != 2 or demand[1] != 2:
                    continue
                tested[f"funding_shape_{size}"] += 1
                if parity and not projected_parity_possible(graph, live):
                    continue
                floor = 2 + sum(max(1, demand[i]) for i in live - {0, 1})
                for counts in bounded_shared_counts(len(edges), ceiling - floor - len(edges)):
                    shared = Counter()
                    for (u, v), width in zip(edges, counts, strict=True):
                        shared[u] += width
                        shared[v] += width
                    if min(shared[0], shared[1]) < 2 or any(shared[i] < 3 for i in set(range(size)) - live):
                        continue
                    supply = [1, 1] + [max(1, demand[i], 3 - shared[i]) if i in live else 0 for i in range(2, size)]
                    words = sum(counts) + sum(supply)
                    if words <= ceiling:
                        tested[f"literal_candidates_{size}"] += 1
                        meetings = [(a, b, width) for (a, b), width in zip(edges, counts, strict=True)]
                        if literal_lawful is not None and not literal_lawful(meetings, supply):
                            tested[f"excluded_by_literal_law_{size}"] += 1
                            continue
                        solutions.append((words, edges, counts, tuple(supply)))
        if solutions:
            word_count, edges, counts, supply = min(solutions)
            return {"minimum_holders": size, "minimum_baseline_distinctions": word_count,
                    "witness": {"meetings": [(a, b, width) for (a, b), width in zip(edges, counts, strict=True)],
                                "loose": supply}, "search_counts": dict(tested),
                    "projected_law_filter": ("wired parity full law" if parity else
                                             "exact NAE projection" if literal_lawful is not None else "none"),
                    "counting_domain": "connected skeletons, live masks, positive shared multiplicities within the specimen ceiling"}
    raise AssertionError("declared comparison must have a bounded witness")


def closing_lower_bound(width):
    tested = Counter()
    # A one-parent exhausting mark is fixed by all old parity constraints summed;
    # it violates the full law of its source star. Fix labels for the p parents and Bob.
    parents = set(range(width))
    bob = width
    for size in range(width + 1, 4 if width == 2 else 6):
        for _, graph in skeletons(size):
            tested[f"connected_skeletons_{size}"] += 1
            if any(graph[bob] & graph[h] for h in parents):
                continue
            if parent_groups(graph, parents) != (tuple(range(width)),):
                continue
            if projected_parity_possible(graph, parents):
                tested[f"eligible_skeletons_{size}"] += 1
    if width == 2:
        assert tested["eligible_skeletons_3"] == 1
    else:
        assert all(not tested[f"eligible_skeletons_{size}"] for size in (4, 5))
    # With three holders the sole witness is Bob, each parent needs two shared
    # distinctions. With six holders and three loose marks, 18 places need at
    # least eight shared distinctions. Both bounds are attained by the fixtures.
    return {"minimum_holders": 3 if width == 2 else 6,
            "minimum_baseline_distinctions": 6 if width == 2 else 11,
            "search_counts": dict(tested),
            "counting_domain": "connected starts, one low-setting offer at each target parent, Bob initially spent and isolated in the active witnessed end"}
