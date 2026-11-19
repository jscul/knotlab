"""Independently grade the repeating frontier states by small source-to-sink flows."""

from collections import deque
from itertools import combinations
from pathlib import Path
import hashlib
import json

import networkx as nx
import closure

HERE = Path(__file__).resolve().parent


def capacity_bound(graph, left, right, limit):
    """Return the minimum separating cut capacity, pooled at limit."""
    if left & right:
        return limit
    residual = [adj.copy() for adj in graph]
    value = 0
    while value < limit:
        prev = {s: -1 for s in left}
        todo = deque(left)
        end = None
        while todo and end is None:
            current = todo.popleft()
            for other, capacity in residual[current].items():
                if not capacity or other in prev:
                    continue
                prev[other] = current
                if other in right:
                    end = other
                    break
                todo.append(other)
        if end is None:
            return value
        extra = limit - value
        current = end
        while prev[current] != -1:
            parent = prev[current]
            extra = min(extra, residual[parent][current])
            current = parent
        current = end
        while prev[current] != -1:
            parent = prev[current]
            residual[parent][current] -= extra
            residual[current][parent] += extra
            current = parent
        value += extra
    return value


def boundary_check(rows, high):
    width = max(map(max, rows)) + 1
    exterior = len(rows)
    sites = [[] for _ in range(width)]
    graph = [{} for _ in range(exterior + 1)]
    for i, row in enumerate(rows):
        for bit in row:
            sites[bit].append(i)
    for endpoints in sites:
        if len(endpoints) == 1:
            endpoints.append(exterior)
        a, b = endpoints
        graph[a][b] = graph[a].get(b, 0) + 1
        graph[b][a] = graph[b].get(a, 0) + 1
    actual = frozenset(rows[high])
    loose = frozenset(i for i, edge in enumerate(sites) if exterior in edge)
    assert len(loose) == 6
    common = actual & loose
    single = sorted(actual ^ loose)
    holders = {i: next(v for v in sites[i] if v not in (high, exterior)) for i in single}
    colors = nx.algorithms.bipartite.color(nx.Graph([(u,v) for u in range(exterior)
                                                     for v in graph[u] if v < exterior]))
    pairs = {}
    for x, y in combinations(sorted(actual | loose), 2):
        a, b = sites[x]
        c, d = sites[y]
        pairs[x, y] = min(capacity_bound(graph, {a, c}, {b, d}, 7),
                          capacity_bound(graph, {a, d}, {b, c}, 7))
    survivors = []
    for selected in combinations(single, 6 - len(common)):
        near = {holders[i] for i in selected}
        if len(near) != len(selected) or len({colors[i] for i in near}) != 1:
            continue
        candidate = common | set(selected)
        outside = common | (set(single) - set(selected))
        if all(pairs[pair] <= 6 for support in (candidate, outside)
               for pair in combinations(sorted(support), 2)):
            survivors.append(sorted(candidate))
    assert sorted(actual) in survivors
    return {"width": width, "sites": len(rows), "boundary_bits": len(actual | loose),
            "pair_checks": len(pairs), "true_six_place": sorted(actual),
            "surviving_six_place_sets": survivors}


def shortest_from_any(graph, starts, goals):
    todo = deque((s, [s]) for s in sorted(starts))
    seen = set(starts)
    while todo:
        state, path = todo.popleft()
        if state in goals:
            return path
        for following in sorted(graph.successors(state)):
            if following not in seen:
                seen.add(following)
                todo.append((following, [*path, following]))
    raise ValueError("no path to a marked frontier")


def replay(path, starts, representatives, moves):
    assert path[0] in starts
    rows, high = representatives[path[0]]
    for state, following in zip(path, path[1:]):
        # Compute the holders from the actual replay, independently of a canonical history.
        same, names, _ = closure.snapshot(rows, state.prior_shrinks, high)
        assert same == state
        parents, outputs = min((parents, outputs) for parents, outputs, nxt in moves[state]
                              if nxt == following)
        fresh_site = len(rows)
        rows = closure.J.advance(rows, tuple(names[i] for i in parents), outputs)
        if outputs == 3:
            high = fresh_site
    assert closure.snapshot(rows, path[-1].prior_shrinks, high)[0] == path[-1]
    assert closure.actual_triples(rows)
    return rows, high


def run():
    starts, records, arcs, _, _ = closure.explore()
    graph = nx.DiGraph()
    graph.add_nodes_from(records)
    graph.add_edges_from((state, nxt) for state, moves in arcs.items() for _, _, nxt in moves)
    positives = {s for s in records if s.prior_shrinks >= 0 and s.shrinks == 1
                 and any(len(g) == 3 for g in closure.OLD.possible_parents(s.frontier))}
    useful = set(positives)
    for s in positives:
        useful.update(nx.ancestors(graph, s))
    trim = graph.subgraph(useful)
    components = list(nx.strongly_connected_components(trim))
    repeating = [sorted(c) for c in components if len(c) > 1 or any(trim.has_edge(s, s) for s in c)]
    reports = []
    starts = set(starts.values())
    for component in sorted(repeating):
        start = component[0]
        subgraph = trim.subgraph(component)
        before = shortest_from_any(trim, starts, {start})
        after = shortest_from_any(trim, {start}, positives)
        lap = [start]
        for a, b in sorted(subgraph.edges()):
            lap.extend(shortest_from_any(subgraph, {lap[-1]}, {a})[1:])
            lap.append(b)
        lap.extend(shortest_from_any(subgraph, {lap[-1]}, {start})[1:])
        measurements = []
        for repeats in (1, 3, 12, 24):
            full = [*before, *(lap[1:] * repeats), *after[1:]]
            rows, high = replay(full, starts, records, arcs)
            out = boundary_check(rows, high)
            measurements.append({"repetitions": repeats,
                                 "history_sha256": hashlib.sha256(json.dumps(rows).encode()).hexdigest(), **out})
        reports.append({"component_size": len(component), "round_trip_steps": len(lap)-1,
                        "prior_shrinks": start.prior_shrinks, "measurements": measurements})
    assert len(positives) == 104 and len(trim) == 400 and len(repeating) == 6
    return {"frontiers_reaching_a_one_shrink_positive": len(trim), "positive_frontiers": len(positives),
            "strong_components": len(components), "cycles_tested": reports}


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
