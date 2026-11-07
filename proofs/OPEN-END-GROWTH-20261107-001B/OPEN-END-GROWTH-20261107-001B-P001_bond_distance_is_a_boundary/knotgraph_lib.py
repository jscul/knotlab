"""Hub-free parity laws as knot graphs.

Every knot is a vertex with exactly three incident distinctions (edges). A distinction shared by two knots
is an edge between them; a distinction held by one knot (an original leg or an open end) is an edge to an
outside vertex INF that carries no constraint. The allowed states satisfy: the three edges at every knot
sum to 0. Columns (values in a basis of the allowed states) decide implied checks and knots exactly as in
LOGIC-AXIS A.
"""

from __future__ import annotations

import random
from itertools import combinations

INF = "INF"


class KnotGraph:
    def __init__(self, ends: dict[int, list], inc: dict, legs: tuple[int, int, int]):
        self.ends = ends          # edge id -> [endpoint, endpoint] (vertex name or INF)
        self.inc = inc            # vertex -> list of three edge ids
        self.legs = legs          # the three distinctions of the seed knot

    @staticmethod
    def seed() -> "KnotGraph":
        return KnotGraph({0: ["X", INF], 1: ["X", INF], 2: ["X", INF]}, {"X": [0, 1, 2]}, (0, 1, 2))

    def substitute(self, gadget: dict) -> "KnotGraph":
        """Replace every knot by a copy of the gadget (vertices, legs, internal edges, open ends)."""
        ends = {e: list(v) for e, v in self.ends.items()}
        inc: dict = {}
        nxt = max(ends) + 1
        for v, edges in self.inc.items():
            name = {x: (v, x) for x in gadget["verts"]}
            for x in gadget["verts"]:
                inc[name[x]] = []
            for leg_vertex, e in zip(gadget["legs"], edges):
                slot = 0 if ends[e][0] == v else 1
                assert ends[e][slot] == v
                ends[e][slot] = name[leg_vertex]
                inc[name[leg_vertex]].append(e)
            for x, y in gadget["edges"]:
                ends[nxt] = [name[x], name[y]]
                inc[name[x]].append(nxt)
                inc[name[y]].append(nxt)
                nxt += 1
            for x in gadget["open_ends"]:
                ends[nxt] = [name[x], INF]
                inc[name[x]].append(nxt)
                nxt += 1
        assert all(len(v) == 3 for v in inc.values())
        return KnotGraph(ends, inc, self.legs)

    def columns(self) -> dict[int, int]:
        edges = sorted(self.ends)
        index = {e: i for i, e in enumerate(edges)}
        rows = []
        for inc in self.inc.values():
            m = 0
            for e in inc:
                m ^= 1 << index[e]
            rows.append(m)
        basis: list[tuple[int, int]] = []
        for r in rows:
            for p, b in basis:
                if r >> p & 1:
                    r ^= b
            if r:
                p = r.bit_length() - 1
                basis = [(q, b ^ r if b >> p & 1 else b) for q, b in basis]
                basis.append((p, r))
        pivots = {p for p, _ in basis}
        sols = []
        for free in range(len(edges)):
            if free in pivots:
                continue
            s = 1 << free
            for p, b in basis:
                if b >> free & 1:
                    s |= 1 << p
            sols.append(s)
        col = {}
        for e, i in index.items():
            c = 0
            for j, s in enumerate(sols):
                if s >> i & 1:
                    c |= 1 << j
            col[e] = c
        return col

    def outside_edges(self):
        return [e for e, ends in self.ends.items() if INF in ends]

    def knot_of(self, e):
        a, b = self.ends[e]
        return a if b == INF else b

    def tree_path(self, u, v):
        """Knots on the path from u to v in the knot graph (breadth-first; meaningful on trees)."""
        prev = {u: None}
        queue = [u]
        for x in queue:
            if x == v:
                break
            for e in self.inc[x]:
                for y in self.ends[e]:
                    if y != INF and y != x and y not in prev:
                        prev[y] = x
                        queue.append(y)
        path, x = [], v
        while x is not None:
            path.append(x)
            x = prev[x]
        return path[::-1]

    def cut(self, knots) -> list[int]:
        inside = set(knots)
        return sorted(e for e, (a, b) in self.ends.items() if (a in inside) != (b in inside))


def rank(vectors) -> int:
    basis: dict[int, int] = {}
    r = 0
    for v in vectors:
        while v:
            h = v.bit_length() - 1
            if h in basis:
                v ^= basis[h]
            else:
                basis[h] = v
                r += 1
                break
    return r


def implied(col, s) -> bool:
    total = 0
    for e in s:
        total ^= col[e]
    return total == 0


def is_knot(col, s) -> bool:
    s = list(s)
    return len(s) >= 3 and implied(col, s) and rank(col[e] for e in s) == len(s) - 1


def smallest_knot(col, u, v, max_size):
    others = [w for w in col if w not in (u, v)]
    target = col[u] ^ col[v]
    for extra in range(1, max_size - 1):
        half = extra // 2
        table: dict[int, list] = {}
        for combo in combinations(others, half):
            x = 0
            for w in combo:
                x ^= col[w]
            table.setdefault(x, []).append(combo)
        for combo in combinations(others, extra - half):
            x = target
            for w in combo:
                x ^= col[w]
            for partner in table.get(x, ()):
                if set(partner) & set(combo):
                    continue
                s = (u, v) + tuple(partner) + tuple(combo)
                if is_knot(col, s):
                    return len(s)
    return None


def random_cubic_gadget(rng: random.Random, n: int, open_ends: int):
    """A random connected knot graph on n knots with three legs and the given number of open ends,
    no self-loops or parallel edges; None if the random pairing fails."""
    stubs = [v for v in range(n) for _ in range(3)]
    rng.shuffle(stubs)
    legs = stubs[:3]
    opens = stubs[3:3 + open_ends]
    rest = stubs[3 + open_ends:]
    if len(rest) % 2:
        return None
    edges = [(rest[i], rest[i + 1]) for i in range(0, len(rest), 2)]
    if any(a == b for a, b in edges) or len({frozenset(e) for e in edges}) != len(edges):
        return None
    adj = {v: set() for v in range(n)}
    for a, b in edges:
        adj[a].add(b)
        adj[b].add(a)
    seen, stack = {0}, [0]
    while stack:
        x = stack.pop()
        for y in adj[x]:
            if y not in seen:
                seen.add(y)
                stack.append(y)
    if len(seen) != n:
        return None
    return {"verts": list(range(n)), "legs": legs, "edges": edges, "open_ends": opens}


def random_cubic_tree(rng: random.Random, n: int) -> KnotGraph:
    """A random tree on n knots (max degree 3 inside the tree), padded with outside edges to degree 3."""
    parent = {0: None}
    deg = {0: 0}
    for v in range(1, n):
        choices = [u for u in parent if deg[u] < 3]
        u = rng.choice(choices)
        parent[v] = u
        deg[u] += 1
        deg[v] = 1
    ends, inc, e = {}, {v: [] for v in range(n)}, 0
    for v, u in parent.items():
        if u is not None:
            ends[e] = [u, v]
            inc[u].append(e)
            inc[v].append(e)
            e += 1
    for v in range(n):
        while len(inc[v]) < 3:
            ends[e] = [v, INF]
            inc[v].append(e)
            e += 1
    outside = [x for x, en in ends.items() if INF in en]
    return KnotGraph(ends, inc, tuple(outside[:3]))


GADGETS = {
    "G0 corner triangle": {"verts": ["A", "B", "C"], "legs": ["A", "B", "C"],
                           "edges": [("A", "B"), ("B", "C"), ("C", "A")], "open_ends": []},
    "G1 star": {"verts": ["A", "B", "C", "O"], "legs": ["A", "B", "C"],
                "edges": [("A", "O"), ("B", "O"), ("C", "O")], "open_ends": ["A", "B", "C"]},
    "G2 hexagon": {"verts": ["A", "B", "C", "P", "Q", "R"], "legs": ["A", "B", "C"],
                   "edges": [("A", "P"), ("P", "B"), ("B", "Q"), ("Q", "C"), ("C", "R"), ("R", "A")],
                   "open_ends": ["P", "Q", "R"]},
    "G4 prism": {"verts": ["A", "B", "C", "A2", "B2", "C2"], "legs": ["A", "B", "C"],
                 "edges": [("A", "A2"), ("B", "B2"), ("C", "C2"), ("A2", "B2"), ("B2", "C2"), ("C2", "A2")],
                 "open_ends": ["A", "B", "C"]},
}
