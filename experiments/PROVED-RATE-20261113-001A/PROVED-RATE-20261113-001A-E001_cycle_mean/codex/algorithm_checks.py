"""Bounded independent checks for graph_algorithms; run with Python -B.

The oracle enumerates simple directed cycles, without SCC decomposition or
Karp dynamic programming.  Only small synthetic graphs are read or created.
"""

from fractions import Fraction
import json
import random
import time

from graph_algorithms import INF, analyze_graph


def _independent_trim(adj, close_cost):
    """Use a separate forward search from every node, not reverse reachability."""
    retained = set()
    for start in range(len(adj)):
        pending = [start]
        seen = {start}
        while pending:
            node = pending.pop()
            if close_cost[node] < INF:
                retained.add(start)
                break
            for target, _ in adj[node]:
                if target not in seen:
                    seen.add(target)
                    pending.append(target)
    return retained


def _brute_mean(adj, retained):
    minimum = None
    for start in sorted(retained):
        # Restrict each cycle to its least-indexed vertex as the initial node.
        pending = [(start, (start,), 0)]
        while pending:
            node, path, total = pending.pop()
            for target, cost in adj[node]:
                if target == start:
                    mean = Fraction(total + cost, len(path))
                    if minimum is None or mean < minimum:
                        minimum = mean
                elif target in retained and target > start and target not in path:
                    pending.append((target, path + (target,), total + cost))
    return minimum


def _brute_empty(retained, close_cost, empty_next):
    good = bad = missing = 0
    for start in retained:
        path = []
        node = start
        while node is not None and node not in path:
            path.append(node)
            node = empty_next[node]
        if node is None:
            missing += 1
        elif all(close_cost[v] < INF for v in path[path.index(node):]):
            good += 1
        else:
            bad += 1
    return True if good else None if missing else False, good, bad, missing


def _check(adj, close_cost, empty_next, complete=True, expected=None):
    retained = _independent_trim(adj, close_cost)
    brute = _brute_mean(adj, retained)
    bounded, good, bad, missing = _brute_empty(retained, close_cost, empty_next)
    calls = 0

    def checkpoint():
        nonlocal calls
        calls += 1

    result = analyze_graph(adj, close_cost, empty_next, complete, checkpoint)
    expected_fraction = None if brute is None else f"{brute.numerator}/{brute.denominator}"
    assert result["lambda"] == expected_fraction, (adj, close_cost, result, brute)
    assert result["lambda_float"] == (None if brute is None else float(brute))
    assert result["lambda_status"] == ("complete" if complete else "partial")
    assert result["trimmed_nodes"] == len(retained)
    assert result["bounded_all"] is bounded, (adj, close_cost, empty_next, result, bounded)
    assert result["bounded_good_starts"] == good
    assert result["bounded_bad_starts"] == bad
    assert result["bounded_affected_starts"] == missing
    assert result["zero_mean"] == (brute == 0)
    assert calls > 0
    if expected:
        for name, value in expected.items():
            assert result[name] == value, (name, result, value)
    return result


def _fixtures():
    cases = [
        # Empty and acyclic graphs; no cycle is assigned a numeric rate.
        ([], [], [], True, {"lambda": None, "bounded_all": False}),
        ([[]], [0], [None], False, {"lambda": None, "bounded_all": None}),
        ([[(1, 2)], [(2, 1)], []], [INF, INF, 1], [None] * 3, False,
         {"lambda": None, "trimmed_nodes": 3}),
        # Self loops, rational means, negative integer costs, parallel arcs.
        ([[(0, 5)]], [1], [None], False, {"lambda": "5/1"}),
        ([[(0, 0)]], [1], [0], True, {"lambda": "0/1", "bounded_all": True}),
        ([[(1, 0)], [(0, 1)]], [0, 0], [1, None], False, {"lambda": "1/2"}),
        ([[(1, 0)], [(2, 0)], [(0, 1)]], [0] * 3, [1, 2, None], False,
         {"lambda": "1/3"}),
        ([[(1, -3)], [(0, 1)]], [0, 0], [None, None], False, {"lambda": "-1/1"}),
        ([[(0, 6), (0, 2), (0, 3)]], [0], [None], False, {"lambda": "2/1"}),
        # A dead zero loop is excluded by trimming; both retained SCCs run Karp.
        ([[(0, 2), (1, 0)], [(1, 3)], [(2, 0)]], [INF, 1, INF], [1, None, 2], False,
         {"lambda": "2/1", "trimmed_nodes": 2, "cyclic_sccs": 2}),
        # A zero mean need not pass the empty-W closing test.
        ([[(1, 0), (2, 1)], [(0, 0)], [(2, 0)]], [0, INF, 0], [1, 0, 2], True,
         {"lambda": "0/1", "bounded_all": True, "bounded_bad_starts": 2}),
        ([[(1, 0)], [(0, 0), (2, 1)], []], [0, INF, 0], [1, 0, None], False,
         {"lambda": "0/1", "bounded_all": None, "bounded_bad_starts": 2}),
        ([[(1, 0)], [(0, 0), (2, 1)], [(2, 0)]], [0, INF, INF], [1, 0, 2], True,
         {"lambda": "0/1", "bounded_all": False}),
        # A finite-close transient may enter a non-close empty cycle outside trim.
        ([[(1, 0)], [(1, 0)]], [0, INF], [1, 1], True,
         {"trimmed_nodes": 1, "lambda": None, "bounded_all": False}),
        # Transients into a good cycle need no finite closing themselves.
        ([[(1, 0)], [(2, 0)], [(2, 0)]], [INF, INF, 1], [1, 2, 2], True,
         {"bounded_all": True, "bounded_good_starts": 3}),
        # A known good witness wins even if another capped trajectory is unknown.
        ([[(0, 0)], []], [0, 0], [0, None], False,
         {"bounded_all": True, "bounded_affected_starts": 1}),
        # Every component must be calculated, even after zero has been found.
        ([[(0, 0)], [(1, -1)]], [0, 0], [0, None], False,
         {"lambda": "-1/1", "cyclic_sccs": 2}),
    ]
    for adj, closing, empty, complete, expected in cases:
        _check(adj, closing, empty, complete, expected)
    return len(cases)


def _exhaustive_topologies():
    cases = 0
    for size in range(1, 4):
        for mask in range(1 << (size * size)):
            adj = [[] for _ in range(size)]
            for source in range(size):
                for target in range(size):
                    if mask & (1 << (source * size + target)):
                        adj[source].append((target, (source * 3 + target * 5 + mask) % 7 - 2))
            close = [0 if (mask + node) % 3 else INF for node in range(size)]
            empty = []
            for edges in adj:
                zeros = [target for target, cost in edges if cost == 0]
                empty.append(zeros[0] if zeros else None)
            _check(adj, close, empty, complete=all(node is not None for node in empty))
            cases += 1
    return cases


def _randomized(seed=20261113, per_size=100):
    randomizer = random.Random(seed)
    cases = 0
    for size in range(1, 8):
        for _ in range(per_size):
            adj = [[] for _ in range(size)]
            for source in range(size):
                for target in range(size):
                    if randomizer.random() < 0.30:
                        adj[source].append((target, randomizer.randrange(-3, 10)))
                        if randomizer.random() < 0.15:
                            adj[source].append((target, randomizer.randrange(-3, 10)))
            close = [INF if randomizer.random() < 0.45 else randomizer.randrange(5)
                     for _ in range(size)]
            empty = []
            for edges in adj:
                zeros = [target for target, cost in edges if cost == 0]
                empty.append(randomizer.choice(zeros) if zeros else None)
            _check(adj, close, empty, complete=all(node is not None for node in empty))
            cases += 1
    return cases


def _large_iterative_fixture():
    # Exceeds Python's normal recursion depth without paying for a large Karp SCC.
    size = 2500
    adj = [[(node + 1, 0)] for node in range(size - 1)] + [[(size - 1, 0)]]
    close = [INF] * (size - 1) + [1]
    result = analyze_graph(adj, close, list(range(1, size)) + [size - 1], True)
    assert result["lambda"] == "0/1"
    assert result["trimmed_nodes"] == size
    assert result["sccs"] == size
    assert result["cyclic_sccs"] == 1
    assert result["bounded_good_starts"] == size
    return 1


def _checkpoint_cancellation():
    class StopRequested(Exception):
        pass

    calls = 0

    def checkpoint():
        nonlocal calls
        calls += 1
        if calls == 5:
            raise StopRequested

    try:
        analyze_graph([[(0, 0)]], [0], [0], True, checkpoint)
    except StopRequested:
        pass
    else:
        raise AssertionError("checkpoint cancellation was not propagated")
    return 1


def main():
    started = time.perf_counter()
    result = {
        "fixtures": _fixtures(),
        "exhaustive_topologies_n_le_3": _exhaustive_topologies(),
        "randomized_graphs_n_le_7": _randomized(),
        "large_iterative_fixture": _large_iterative_fixture(),
        "checkpoint_cancellation": _checkpoint_cancellation(),
        "seed": 20261113,
        "status": "passed",
    }
    result["seconds"] = time.perf_counter() - started
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
