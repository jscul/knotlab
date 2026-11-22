"""Bond readings from the recorded parity cycle and not-all-equal laws."""

from collections import deque
from itertools import combinations

import numpy as np
from pysat.solvers import Minisat22
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import dijkstra

from sources import FOLD, distances, fold_knots, load_record


class CycleBonds:
    """The source parity law identifies bonds with simple vertex cycles."""

    def __init__(self, edges, boundary):
        self.edges = edges
        self.n = max(max(edge) for edge in self.edges) + 1
        self.adj = [dict() for _ in range(self.n)]
        for index, (a, b) in enumerate(self.edges):
            self.adj[a][b] = index
            self.adj[b][a] = index
        self.margin = distances(self.adj, boundary)
        self.network = None

    @classmethod
    def from_pattern(cls, pattern):
        boundary = {vertex for e in pattern.truncated for vertex in pattern.segments[e]}
        return cls(pattern.segments, boundary)

    def crop(self, center, radius):
        reached = distances(self.adj, self.edges[center], limit=radius)
        remap = {v: index for index, v in enumerate(reached)}
        kept = {e for u in reached for v, e in self.adj[u].items() if v in reached}
        old_ids = sorted(kept)
        edges = [(remap[a], remap[b]) for a, b in (self.edges[e] for e in old_ids)]
        boundary = {remap[v] for v, steps in reached.items() if steps == radius or self.margin[v] == 0}
        return CycleBonds(edges, boundary), {old: new for new, old in enumerate(old_ids)}

    def flow_arcs(self):
        if self.network is not None:
            return self.network
        edge_array = np.asarray(self.edges, dtype=np.int64)
        a, b = edge_array.T
        ids = 2 * np.arange(self.n, dtype=np.int64)
        starts = np.concatenate([ids, np.column_stack((2 * a + 1, 2 * b + 1)).ravel()])
        ends = np.concatenate([ids + 1, np.column_stack((2 * b, 2 * a)).ravel()])
        costs = np.concatenate([np.zeros(self.n, dtype=np.int32), np.ones(2 * len(self.edges), dtype=np.int32)])
        self.network = starts, ends, costs
        return self.network

    def least_cycle(self, e, f):
        """Integral two-unit min-cost flow after splitting vertices to give capacity one."""
        a, b = self.edges[e]
        c, d = self.edges[f]
        shared = set((a, b)) & set((c, d))
        if shared:
            center, = shared
            start, end = (b if a == center else a), (d if c == center else c)
            lengths = {start: 0, center: -1}
            pending = deque([start])
            while pending:
                u = pending.popleft()
                if u == end:
                    return lengths[u] + 2
                for v in self.adj[u]:
                    if v not in lengths:
                        lengths[v] = lengths[u] + 1
                        pending.append(v)
            return None

        source, sink = 2 * self.n, 2 * self.n + 1
        order = sink + 1
        arc_start, arc_end, arc_cost = self.flow_arcs()
        keep = np.ones(len(arc_start), dtype=bool)
        keep[[self.n + 2 * e, self.n + 2 * e + 1, self.n + 2 * f, self.n + 2 * f + 1]] = False
        starts = np.concatenate([arc_start[keep], [source, source, 2 * c + 1, 2 * d + 1]])
        ends = np.concatenate([arc_end[keep], [2 * a, 2 * b, sink, sink]])
        costs = np.concatenate([arc_cost[keep], [0, 0, 0, 0]])
        adjacency = csr_matrix((costs, (starts, ends)), shape=(order, order))
        first, previous = dijkstra(adjacency, indices=source, directed=True, return_predecessors=True)
        if not np.isfinite(first[sink]):
            return None

        reversed_arcs = []
        vertex = sink
        while vertex != source:
            parent = int(previous[vertex])
            reversed_arcs.append((vertex, parent))
            vertex = parent
        reverse_start, reverse_end = np.asarray(reversed_arcs, dtype=np.int64).T
        on_path = np.isin(starts * order + ends, reverse_end * order + reverse_start)
        usable = np.isfinite(first[starts]) & np.isfinite(first[ends]) & ~on_path
        start, end = starts[usable], ends[usable]
        reduced = costs[usable] + first[start] - first[end]
        if (reduced < 0).any():
            raise ValueError("Dijkstra reduced costs must be nonnegative")
        residual = csr_matrix((np.concatenate([reduced, np.zeros(len(reverse_start))]),
                               (np.concatenate([start, reverse_start]), np.concatenate([end, reverse_end]))),
                              shape=(order, order))
        remaining = dijkstra(residual, indices=source, directed=True)[sink]
        return int(2 * first[sink] + remaining) + 2 if np.isfinite(remaining) else None

    def exact(self, e, f):
        if e == f:
            return 0
        cycle = self.least_cycle(e, f)
        if cycle is None:
            return None
        # A shorter cycle using external distinctions needs a path from both ends to the boundary.
        no_exit_floor = max(1 + sum(self.margin[v] for v in self.edges[edge]) for edge in (e, f))
        return cycle - 1 if cycle <= no_exit_floor else None

    def short_bonds(self, e):
        if min(self.margin[v] for v in self.edges[e]) < 2:
            raise ValueError("A short bond could leave the available substitution")
        a, b = self.edges[e]
        paths = [(a, (a,), (e,))]
        cycles = []
        while paths:
            node, visited, support = paths.pop()
            for next_node, edge in self.adj[node].items():
                if edge == e or next_node in visited:
                    continue
                if next_node == b and len(support) in (2, 3):
                    cycles.append(tuple(sorted((*support, edge))))
                elif len(support) < 3:
                    paths.append((next_node, (*visited, next_node), (*support, edge)))
        return cycles


def compatible_rows(columns, period, group, n):
    patterns = np.arange(1 << n)
    allowed = np.ones((len(columns), len(patterns)), dtype=bool)
    for index, y in group:
        allowed &= ((columns[:, None] >> (y % period)) & 1) == (patterns >> index) & 1
    return allowed


class PeriodicRows:
    """Recorded across-period transfer with infinite past and future.

    Random valid rows are only a fast path to certify freeness. Hard cases use
    exact transfer reachability on the same period panel.
    """

    def __init__(self, half_width, rng):
        source = load_record("fold_transfer", FOLD / "check.py")
        self.periods = []
        self.boards = []
        for period in range(3, 9):
            adjacency = source.transition(period)
            past, future = source.recurrent(adjacency)
            choices = [np.flatnonzero(row & future).tolist() for row in adjacency]
            initial = np.flatnonzero(past & future).tolist()
            states = np.empty((192, 2 * half_width + 1), dtype=np.uint16)
            for sample in states:
                current = rng.choice(initial)
                sample[0] = current
                for column in range(1, len(sample)):
                    current = rng.choice(choices[current])
                    sample[column] = current
            jumps = {0: np.eye(len(adjacency), dtype=np.int16), 1: adjacency.T.astype(np.int16)}
            self.periods.append((period, adjacency.T.astype(np.int16), past, future, jumps))
            self.boards.append((period, states))
        self.half_width = half_width
        self.full = (1 << (192 * len(self.boards))) - 1
        self.masks = {}

    def mask(self, point):
        if point not in self.masks:
            x, y = point
            values = np.concatenate([(states[:, x + self.half_width] >> (y % period)) & 1
                                     for period, states in self.boards])
            self.masks[point] = int.from_bytes(np.packbits(values, bitorder="little").tobytes(), "little")
        return self.masks[point]

    def sample_patterns(self, support):
        states = [self.full]
        for point in reversed(support):
            ones = self.mask(point)
            states = [piece for value in states for piece in (value & ~ones, value & ones)]
        return {index for index, value in enumerate(states) if value}

    def exact_patterns(self, support):
        groups = {}
        for i, (x, y) in enumerate(support):
            groups.setdefault(x, []).append((i, y))
        result = set()
        for period, transition, past, future, jumps in self.periods:
            columns = np.arange(len(past))
            previous = None
            for x, group in sorted(groups.items()):
                compatible = compatible_rows(columns, period, group, len(support))
                if previous is None:
                    reached = compatible & past[:, None]
                else:
                    gap = x - previous
                    for length in range(max(jumps) + 1, gap + 1):
                        jumps[length] = ((transition @ jumps[length - 1]) != 0).astype(np.int16)
                    reached = compatible & ((jumps[gap] @ reached) != 0)
                previous = x
            result.update(np.flatnonzero((reached & future[:, None]).any(axis=0)).tolist())
            if len(result) == 1 << len(support):
                break
        return result


def free_parts(rows, size):
    for forgotten in range(size):
        low = (1 << forgotten) - 1
        if len({(row & low) | ((row >> (forgotten + 1)) << forgotten) for row in rows}) != 1 << (size - 1):
            return False
    return True


class NAEBonds:
    """Certify a bounded support query through allowed-state projections.

    The finite clauses can only exclude infinite assignments. The transfer
    rows can only realize assignments. An unresolved gap is preserved.
    """

    def __init__(self, radius, rng):
        x_limit = radius + 4
        points, knots = fold_knots(x_limit, 2 * radius + 8)
        self.literal = {point: index for index, point in enumerate(points, start=1)}
        clauses = [[sign * (i + 1) for i in knot] for knot in knots for sign in (-1, 1)]
        self.solver = Minisat22(bootstrap_with=clauses)
        self.rows = PeriodicRows(x_limit, rng)
        self.cache = {}

    def excluded(self, support, realized):
        last = (1 << len(support)) - 1
        for row in range((last + 1) // 2):
            if row in realized or (last ^ row) in realized:
                continue
            literals = [self.literal[p] if row & (1 << i) else -self.literal[p] for i, p in enumerate(support)]
            if not self.solver.solve(assumptions=literals):
                return row
        return None

    def projection(self, support):
        if support in self.cache:
            return self.cache[support]
        size = len(support)
        realized = self.rows.sample_patterns(support)
        if len(realized) == 1 << size:
            return "absent", None
        rejected = self.excluded(support, realized)
        if rejected is not None and free_parts(realized, size):
            result = ("certified", {"missing_row": rejected, "realized_rows": sorted(realized), "coverage": "valid_paths"})
        else:
            realized = self.rows.exact_patterns(support) | realized
            if len(realized) == 1 << size:
                result = ("absent", None)
            elif rejected is not None and free_parts(realized, size):
                result = ("certified", {"missing_row": rejected, "realized_rows": sorted(realized), "coverage": "period_transfer"})
            elif any(self.excluded(part, self.rows.sample_patterns(part)) is not None
                     for part in combinations(support, size - 1)):
                result = ("absent", None)
            else:
                result = ("unresolved", None)
        self.cache[support] = result
        return result

    def query(self, pattern, root, target):
        x0, y0 = pattern.points[root]
        helpers = (set(pattern.meeting[root]) | set(pattern.meeting[target])) - {root, target}
        unresolved = False
        for count in (1, 2):
            for additions in combinations(sorted(helpers), count):
                positions = [pattern.points[i] for i in (*additions, root, target)]
                support = tuple(sorted((x - x0, y - y0) for x, y in positions))
                status, evidence = self.projection(support)
                if status == "certified":
                    return status, {"support": support, **evidence}
                unresolved |= status == "unresolved"
        return ("unresolved" if unresolved else "absent"), None
