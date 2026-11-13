"""Exact finite-graph calculations for the registered cycle-mean computation.

The supplied graph already consists of start-reachable nodes.  No transition is
invented when the graph was capped.  Minimum cycle means use integer dynamic
programming and exact Fraction comparisons; floats are only output renderings.
"""

from collections import deque
from fractions import Fraction


INF = 10**9
_CHECK_MASK = (1 << 14) - 1


def _fraction_text(value):
    return None if value is None else f"{value.numerator}/{value.denominator}"


def _karp_cycle_mean(nodes, adj, checkpoint):
    """Return an exact minimum cycle mean for one cycle-bearing SCC.

    D_0(v) = 0 for every vertex is a super-source initialization.  The first
    pass retains D_n.  The second recomputes D_0 through D_(n-1), retaining only
    their per-vertex maximum ratios.  Thus no n-by-n DP table is retained.
    """
    checkpoint()
    size = len(nodes)
    local = {node: i for i, node in enumerate(nodes)}
    incoming = [[] for _ in nodes]
    work = 0
    edge_count = 0
    for node in nodes:
        source = local[node]
        for target, cost in adj[node]:
            target_local = local.get(target)
            if target_local is not None:
                incoming[target_local].append((source, cost))
                edge_count += 1
            work += 1
            if work & _CHECK_MASK == 0:
                checkpoint()

    def advance(previous):
        nonlocal work
        current = [0] * size
        for target, edges in enumerate(incoming):
            # A cycle-bearing SCC gives every vertex an internal predecessor.
            source, cost = edges[0]
            best = previous[source] + cost
            for source, cost in edges[1:]:
                candidate = previous[source] + cost
                if candidate < best:
                    best = candidate
                work += 1
                if work & _CHECK_MASK == 0:
                    checkpoint()
            current[target] = best
            work += 1
            if work & _CHECK_MASK == 0:
                checkpoint()
        return current

    final = [0] * size
    for _ in range(size):
        final = advance(final)
        checkpoint()

    previous = [0] * size
    maxima = [None] * size
    for length in range(size):
        denominator = size - length
        for vertex in range(size):
            ratio = Fraction(final[vertex] - previous[vertex], denominator)
            if maxima[vertex] is None or ratio > maxima[vertex]:
                maxima[vertex] = ratio
            work += 1
            if work & _CHECK_MASK == 0:
                checkpoint()
        if length + 1 < size:
            previous = advance(previous)
        checkpoint()
    return min(maxima), edge_count


def _empty_cycle_test(trimmed, close_cost, empty_next, checkpoint):
    """Evaluate the specified existential empty-W sufficient test.

    An outcome is attached to the entire known trajectory: 1 means a cycle all
    of whose nodes have finite close cost; 2 means another known cycle; 3 means
    a missing successor.  Trajectories may use nodes outside the trimmed set.
    """
    outcomes = bytearray(len(trimmed))
    good_cycles = bad_cycles = missing_successors = 0
    work = 0
    for start, retained in enumerate(trimmed):
        if not retained or outcomes[start]:
            continue
        path = []
        positions = {}
        node = start
        while True:
            outcome = outcomes[node]
            if outcome:
                break
            cycle_start = positions.get(node)
            if cycle_start is not None:
                outcome = 1
                for cycle_node in path[cycle_start:]:
                    if close_cost[cycle_node] >= INF:
                        outcome = 2
                    work += 1
                    if work & _CHECK_MASK == 0:
                        checkpoint()
                if outcome == 1:
                    good_cycles += 1
                else:
                    bad_cycles += 1
                break
            positions[node] = len(path)
            path.append(node)
            successor = empty_next[node]
            if successor is None:
                outcome = 3
                missing_successors += 1
                break
            node = successor
            work += 1
            if work & _CHECK_MASK == 0:
                checkpoint()
        for node in path:
            outcomes[node] = outcome
            work += 1
            if work & _CHECK_MASK == 0:
                checkpoint()
        checkpoint()

    good_starts = bad_starts = unknown_starts = 0
    for node, retained in enumerate(trimmed):
        if retained:
            outcome = outcomes[node]
            if outcome == 1:
                good_starts += 1
            elif outcome == 2:
                bad_starts += 1
            else:
                unknown_starts += 1
        if node & _CHECK_MASK == 0:
            checkpoint()
    bounded_all = True if good_starts else None if unknown_starts else False
    return {
        "bounded_all": bounded_all,
        "bounded_good_starts": good_starts,
        "bounded_bad_starts": bad_starts,
        "bounded_affected_starts": unknown_starts,
        "bounded_good_cycles": good_cycles,
        "bounded_bad_cycles": bad_cycles,
        "bounded_missing_successors": missing_successors,
    }


def analyze_graph(adj, close_cost, empty_next, complete, checkpoint=lambda: None):
    """Trim, find SCCs iteratively, and calculate the requested exact outputs.

    ``adj[u]`` contains ``(v, integer_cost)`` pairs, including parallel arcs.
    ``close_cost[u] < INF`` means a finite accepting closing is available.
    ``empty_next[u]`` is a known empty-W successor or None if absent at the cap.

    ``bounded_all`` follows the specification's *some m* quantifier.  False
    means failure of the sufficient test, rather than an unboundedness proof.
    With no known positive witness, missing trajectories produce None.  All
    cyclic SCCs are analyzed, even after a zero minimum has been encountered.
    """
    checkpoint()
    size = len(adj)
    if len(close_cost) != size or len(empty_next) != size:
        raise ValueError("graph, closing costs, and empty successors differ in size")
    reverse = [[] for _ in adj]
    work = 0
    for source, edges in enumerate(adj):
        successor = empty_next[source]
        if successor is not None and not 0 <= successor < size:
            raise ValueError("empty-W successor is outside the indexed graph")
        for target, _ in edges:
            if not 0 <= target < size:
                raise ValueError("transition target is outside the indexed graph")
            reverse[target].append(source)
            work += 1
            if work & _CHECK_MASK == 0:
                checkpoint()
        if source & _CHECK_MASK == 0:
            checkpoint()

    trimmed = bytearray(size)
    frontier = deque()
    for node, cost in enumerate(close_cost):
        if cost < INF:
            trimmed[node] = 1
            frontier.append(node)
        if node & _CHECK_MASK == 0:
            checkpoint()
    trimmed_nodes = len(frontier)
    while frontier:
        node = frontier.popleft()
        for predecessor in reverse[node]:
            if not trimmed[predecessor]:
                trimmed[predecessor] = 1
                trimmed_nodes += 1
                frontier.append(predecessor)
            work += 1
            if work & _CHECK_MASK == 0:
                checkpoint()
        work += 1
        if work & _CHECK_MASK == 0:
            checkpoint()

    # Iterative Kosaraju first pass.  Paired stacks avoid recursion limits and
    # avoid creating a separate adjacency graph for the trimmed nodes.
    visited = bytearray(size)
    finish = []
    for start in range(size):
        if not trimmed[start] or visited[start]:
            continue
        visited[start] = 1
        stack = [start]
        offsets = [0]
        while stack:
            node = stack[-1]
            offset = offsets[-1]
            edges = adj[node]
            if offset == len(edges):
                finish.append(node)
                stack.pop()
                offsets.pop()
            else:
                offsets[-1] = offset + 1
                target = edges[offset][0]
                if trimmed[target] and not visited[target]:
                    visited[target] = 1
                    stack.append(target)
                    offsets.append(0)
            work += 1
            if work & _CHECK_MASK == 0:
                checkpoint()
        checkpoint()

    # The second pass emits one component at a time, retaining only aggregate
    # metadata once that component's exact Karp calculation has completed.
    assigned = bytearray(size)
    minimum = None
    sccs = cyclic_sccs = max_cyclic_scc_nodes = 0
    cyclic_scc_edges = 0
    for start in reversed(finish):
        if assigned[start]:
            continue
        assigned[start] = 1
        stack = [start]
        component = []
        while stack:
            node = stack.pop()
            component.append(node)
            for predecessor in reverse[node]:
                if trimmed[predecessor] and not assigned[predecessor]:
                    assigned[predecessor] = 1
                    stack.append(predecessor)
                work += 1
                if work & _CHECK_MASK == 0:
                    checkpoint()
            work += 1
            if work & _CHECK_MASK == 0:
                checkpoint()
        sccs += 1
        cyclic = len(component) > 1
        if not cyclic:
            node = component[0]
            cyclic = any(target == node for target, _ in adj[node])
        if cyclic:
            mean, edge_count = _karp_cycle_mean(component, adj, checkpoint)
            cyclic_sccs += 1
            cyclic_scc_edges += edge_count
            max_cyclic_scc_nodes = max(max_cyclic_scc_nodes, len(component))
            if minimum is None or mean < minimum:
                minimum = mean
        checkpoint()

    result = {
        "lambda": _fraction_text(minimum),
        "lambda_float": None if minimum is None else float(minimum),
        "lambda_status": "complete" if complete else "partial",
        "zero_mean": minimum == 0,
        "trimmed_nodes": trimmed_nodes,
        "sccs": sccs,
        "cyclic_sccs": cyclic_sccs,
        "cyclic_scc_edges": cyclic_scc_edges,
        "max_cyclic_scc_nodes": max_cyclic_scc_nodes,
    }
    result.update(_empty_cycle_test(trimmed, close_cost, empty_next, checkpoint))
    checkpoint()
    return result
