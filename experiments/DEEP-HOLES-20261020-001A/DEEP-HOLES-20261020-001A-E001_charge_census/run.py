#!/usr/bin/env python3
"""Producer for DEEP-HOLES-20261020-001A-E001 (frozen contract: contract.json).

Charge networks: knots on the vertices of a cubic graph, distinctions on its
edges. For each network, placement and coefficient ring, the least level at
which the affine relaxation refutes the network is found by building the
level-k system for k = 3, 4, ... and solving it exactly. Every verdict is
stored with a certificate: a solution one level below the refuting level, and
a combination of equations reading 0 = c (c nonzero) at it.

Graph parameters (treewidth, cutwidth, toggle width, separator number) are
computed separately and never enter the linear algebra.
"""

from __future__ import annotations

import gzip
import heapq
import json
import random
import sys
import time
from collections import defaultdict
from fractions import Fraction
from itertools import combinations, permutations, product
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
ARTIFACT = ROOT / "artifacts" / "DEEP-HOLES-20261020-001A" / HERE.name
sys.path.insert(0, str(ROOT / "tools"))

from knotlab.choice import two_loop_knots  # noqa: E402

SEED = 20261020
MAX_LEVEL = 8
MAX_VARS = {"F": 400_000, "Q": 160_000}


# ---------------------------------------------------------------- cubic graphs

def connected(n, edges):
    adjacency = defaultdict(set)
    for a, b in edges:
        adjacency[a].add(b)
        adjacency[b].add(a)
    seen, todo = {0}, [0]
    while todo:
        x = todo.pop()
        for y in adjacency[x] - seen:
            seen.add(y)
            todo.append(y)
    return len(seen) == n


def labelled_cubic(n):
    """Every 3-regular graph on vertices 0..n-1 with vertex 0 adjacent to 1, 2, 3."""
    out = []
    degree = [0] * n
    edges = [(0, 1), (0, 2), (0, 3)]
    degree[0] = 3
    for v in (1, 2, 3):
        degree[v] = 1
    present = set(edges)

    def extend(v, low):
        if v < n and degree[v] == 3:
            while v < n and degree[v] == 3:
                v += 1
            low = v + 1
        if v == n:
            out.append(sorted(edges))
            return
        for w in range(max(low, v + 1), n):
            if degree[w] < 3 and (v, w) not in present:
                edges.append((v, w))
                present.add((v, w))
                degree[v] += 1
                degree[w] += 1
                extend(v, w + 1)
                degree[v] -= 1
                degree[w] -= 1
                present.discard((v, w))
                edges.pop()

    extend(1, 2)
    return out


def isomorphic(n, e1, e2):
    a1 = [set() for _ in range(n)]
    a2 = [set() for _ in range(n)]
    for a, b in e1:
        a1[a].add(b)
        a1[b].add(a)
    for a, b in e2:
        a2[a].add(b)
        a2[b].add(a)
    mapping = {}

    def place(v):
        if v == n:
            return True
        for w in range(n):
            if w in mapping.values():
                continue
            if all((u in a1[v]) == (mapping[u] in a2[w]) for u in mapping):
                mapping[v] = w
                if place(v + 1):
                    return True
                del mapping[v]
        return False

    return place(0)


def invariant(n, edges):
    adjacency = [set() for _ in range(n)]
    for a, b in edges:
        adjacency[a].add(b)
        adjacency[b].add(a)
    triangles = sorted(sum(1 for x, y in combinations(sorted(adjacency[v]), 2) if y in adjacency[x]) for v in range(n))
    squares = sorted(sum(len((adjacency[x] & adjacency[y]) - {v}) for x, y in combinations(sorted(adjacency[v]), 2))
                     for v in range(n))
    return (tuple(triangles), tuple(squares))


def cubic_graphs(n):
    classes = []
    for edges in labelled_cubic(n):
        if not connected(n, edges):
            continue
        key = invariant(n, edges)
        if not any(k == key and isomorphic(n, edges, rep) for k, rep in classes):
            classes.append((key, edges))
    return [edges for _, edges in classes]


def name_graph(n, edges):
    if n == 4:
        return "K4"
    adjacency = [set() for _ in range(n)]
    for a, b in edges:
        adjacency[a].add(b)
        adjacency[b].add(a)
    colour = {0: 0}
    todo = [0]
    bipartite = True
    while todo:
        x = todo.pop()
        for y in adjacency[x]:
            if y not in colour:
                colour[y] = 1 - colour[x]
                todo.append(y)
            elif colour[y] == colour[x]:
                bipartite = False
    triangles = sum(invariant(n, edges)[0]) // 3
    if n == 6:
        return "K33" if bipartite else "prism"
    if bipartite:
        return "cube"
    if triangles == 0:
        return "wagner"
    return f"cubic8_t{triangles}"


# ---------------------------------------------------------------- graph parameters (prediction side)

def cut(edges, U):
    return {i for i, (a, b) in enumerate(edges) if (a in U) != (b in U)}


def star(edges, v):
    return {i for i, (a, b) in enumerate(edges) if v in (a, b)}


def toggle_width(n, edges, monotone=False):
    """Bottleneck path from the empty set to V, toggling one vertex at a time."""
    full = (1 << n) - 1
    stars = [sum(1 << i for i in star(edges, v)) for v in range(n)]
    cuts = {}

    def cutmask(U):
        if U not in cuts:
            cuts[U] = sum(1 << i for i, (a, b) in enumerate(edges) if ((U >> a) & 1) != ((U >> b) & 1))
        return cuts[U]

    best = {0: 0}
    heap = [(0, 0)]
    while heap:
        cost, U = heapq.heappop(heap)
        if U == full:
            return cost
        if cost > best.get(U, 99):
            continue
        for v in range(n):
            if monotone and (U >> v) & 1:
                continue
            step = bin(cutmask(U) | stars[v]).count("1")
            new = max(cost, step)
            W = U ^ (1 << v)
            if new < best.get(W, 99):
                best[W] = new
                heapq.heappush(heap, (new, W))
    return None


def cutwidth(n, edges):
    full = (1 << n) - 1
    width = {0: 0}
    for U in range(1, full + 1):
        size = sum(1 for a, b in edges if ((U >> a) & 1) != ((U >> b) & 1))
        width[U] = max(size, min(width[U ^ (1 << v)] for v in range(n) if (U >> v) & 1))
    return width[full]


def treewidth(n, adjacency):
    """Exact treewidth by dynamic programming over elimination prefixes."""
    full = (1 << n) - 1

    def q(S, v):
        seen, todo, out = {v}, [v], set()
        while todo:
            x = todo.pop()
            for y in adjacency[x]:
                if y in seen:
                    continue
                seen.add(y)
                if (S >> y) & 1:
                    todo.append(y)
                else:
                    out.add(y)
        return len(out)

    tw = {0: -1}
    for S in sorted(range(1, full + 1), key=lambda s: bin(s).count("1")):
        tw[S] = min(max(tw[S ^ (1 << v)], q(S ^ (1 << v), v)) for v in range(n) if (S >> v) & 1)
    return tw[full]


def separator_number(n, edges):
    for size in range(len(edges) + 1):
        for removed in combinations(range(len(edges)), size):
            kept = [e for i, e in enumerate(edges) if i not in removed]
            parent = list(range(n))

            def find(x):
                while parent[x] != x:
                    parent[x] = parent[parent[x]]
                    x = parent[x]
                return x

            for a, b in kept:
                parent[find(a)] = find(b)
            sizes = defaultdict(int)
            for v in range(n):
                sizes[find(v)] += 1
            if max(sizes.values()) * 2 <= n:
                return size
    return None


def parameters(n, edges):
    adjacency = [set() for _ in range(n)]
    for a, b in edges:
        adjacency[a].add(b)
        adjacency[b].add(a)
    line = [set() for _ in edges]
    for i, j in combinations(range(len(edges)), 2):
        if set(edges[i]) & set(edges[j]):
            line[i].add(j)
            line[j].add(i)
    return {"treewidth": treewidth(n, adjacency), "line_graph_treewidth": treewidth(len(edges), line),
            "cutwidth": cutwidth(n, edges), "toggle_width": toggle_width(n, edges),
            "toggle_width_monotone": toggle_width(n, edges, monotone=True),
            "separator_number": separator_number(n, edges)}


# ---------------------------------------------------------------- networks and relaxations

class Network:
    def __init__(self, n, edges, q, knot, label):
        self.n, self.edges, self.q, self.knot, self.label = n, edges, q, knot, label
        self.stars = [sorted(star(edges, v)) for v in range(n)]
        self._local = {}

    def local(self, bag):
        if bag not in self._local:
            inside = [v for v in range(self.n) if set(self.stars[v]) <= set(bag)]
            out = []
            for f in product(range(self.q), repeat=len(bag)):
                value = dict(zip(bag, f))
                if all(self.knot(v, [value[e] for e in self.stars[v]]) for v in inside):
                    out.append(f)
            self._local[bag] = out
        return self._local[bag]

    def size(self, level):
        return sum(len(self.local(bag)) for k in range(level + 1) for bag in combinations(range(len(self.edges)), k))

    def system(self, level):
        equations = [("n:", {"v:|": 1}, 1)]
        for k in range(1, level + 1):
            for big in combinations(range(len(self.edges)), k):
                rows = self.local(big)
                for at, e in enumerate(big):
                    small = big[:at] + big[at + 1:]
                    extensions = defaultdict(list)
                    for g in rows:
                        extensions[g[:at] + g[at + 1:]].append(g)
                    for f in self.local(small):
                        coefs = {name(small, f): 1}
                        for g in extensions[f]:
                            coefs[name(big, g)] = -1
                        equations.append((f"m:{','.join(map(str, big))}|{e}|{','.join(map(str, f))}", coefs, 0))
        return equations


def name(bag, f):
    return "v:" + ",".join(map(str, bag)) + "|" + ",".join(map(str, f))


def tseitin2(edges, charge):
    def knot(v, values):
        return sum(values) % 2 == charge[v] % 2
    return knot


def tseitin3(edges, charge):
    signs = {}
    for i, (a, b) in enumerate(edges):
        signs[(a, i)] = 1
        signs[(b, i)] = -1

    def knot(v, values):
        stars = [i for i, e in enumerate(edges) if v in e]
        return sum(signs[(v, i)] * x for i, x in zip(stars, values)) % 3 == charge[v] % 3
    return knot


def nae(v, values):
    return len(set(values)) > 1


def var_order(variable):
    bag = variable[2:].split("|")[0]
    return (-(bag.count(",") + 1 if bag else 0), variable)


def solve_field(equations, p=None):
    """Row echelon elimination over F_p (p prime) or Q (p None); a solution or a refutation."""
    names = sorted({v for _, coefs, _ in equations for v in coefs}, key=var_order)
    rank = {v: i for i, v in enumerate(names)}
    pivots = {}
    one = Fraction(1) if p is None else 1
    for label, coefs, c in equations:
        row = {}
        for v, a in coefs.items():
            a = Fraction(a) if p is None else a % p
            if a:
                row[rank[v]] = a
        const = Fraction(c) if p is None else c % p
        hist = {label: one}
        while row:
            v = min(row)
            if v not in pivots:
                break
            prow, pc, ph = pivots[v]
            f = row[v]
            for j, a in prow.items():
                value = row.get(j, 0) - f * a
                if p is not None:
                    value %= p
                if value:
                    row[j] = value
                else:
                    row.pop(j, None)
            const = const - f * pc
            if p is not None:
                const %= p
            for e, a in ph.items():
                value = hist.get(e, 0) - f * a
                if p is not None:
                    value %= p
                if value:
                    hist[e] = value
                else:
                    hist.pop(e, None)
        if not row:
            if const:
                return {"feasible": False, "refutation": hist, "constant": const}
            continue
        v = min(row)
        scale = 1 / row[v] if p is None else pow(row[v], p - 2, p)
        if p is None:
            row = {j: a * scale for j, a in row.items()}
            hist = {e: a * scale for e, a in hist.items()}
            const = const * scale
        else:
            row = {j: a * scale % p for j, a in row.items()}
            hist = {e: a * scale % p for e, a in hist.items()}
            const = const * scale % p
        pivots[v] = (row, const, hist)
    x = {}
    for v in sorted(pivots, reverse=True):
        row, c, _ = pivots[v]
        value = c - sum(a * x.get(j, 0) for j, a in row.items() if j != v)
        x[v] = value % p if p is not None else value
    return {"feasible": True, "solution": {names[v]: value for v, value in x.items() if value}}


def encode(result):
    out = {"feasible": result["feasible"]}
    if "solution" in result:
        out["solution"] = {k: str(v) for k, v in result["solution"].items()}
    if "refutation" in result:
        out["refutation"] = {k: str(v) for k, v in result["refutation"].items()}
        out["constant"] = str(result["constant"])
    return out


RING_PRIME = {"F2": 2, "F3": 3, "F5": 5, "Q": None}


def least_level(net, ring, start=3, cap=MAX_LEVEL, certificates=None, key=None, log=None):
    """Raise the level until the relaxation refutes; keep the last solution and the refutation."""
    budget = MAX_VARS["Q" if ring == "Q" else "F"]
    previous = None
    for level in range(start, min(cap, len(net.edges)) + 1):
        variables = net.size(level)
        if variables > budget:
            return {"level": None, "resolved": False, "last_feasible_level": level - 1, "variables": variables}
        started = time.time()
        result = solve_field(net.system(level), RING_PRIME[ring])
        if log:
            log(f"    {key} {ring} level {level}: {'feasible' if result['feasible'] else 'refuted'} "
                f"({variables} variables, {time.time() - started:.1f}s)")
        if not result["feasible"]:
            if certificates is not None:
                certificates[f"{key}|{ring}|{level}"] = encode(result)
                if previous is not None:
                    certificates[f"{key}|{ring}|{level - 1}"] = encode(previous)
            return {"level": level, "resolved": True, "variables": variables}
        previous = result
    if certificates is not None and previous is not None:
        certificates[f"{key}|{ring}|{min(cap, len(net.edges))}"] = encode(previous)
    return {"level": None, "resolved": level == len(net.edges), "last_feasible_level": level,
            "never_refuted": True}


# ---------------------------------------------------------------- holes

def rank_mod(matrix, p):
    """Rank over F_p (p prime) or Q (p None) of a list of rows."""
    rows = [[Fraction(a) if p is None else a % p for a in row] for row in matrix]
    r, columns = 0, len(rows[0]) if rows else 0
    for c in range(columns):
        pivot = next((i for i in range(r, len(rows)) if rows[i][c]), None)
        if pivot is None:
            continue
        rows[r], rows[pivot] = rows[pivot], rows[r]
        inv = 1 / rows[r][c] if p is None else pow(rows[r][c], p - 2, p)
        rows[r] = [a * inv if p is None else a * inv % p for a in rows[r]]
        for i in range(len(rows)):
            if i != r and rows[i][c]:
                f = rows[i][c]
                rows[i] = [a - f * b if p is None else (a - f * b) % p for a, b in zip(rows[i], rows[r])]
        r += 1
    return r


def scope_hole(q, allowed, p):
    """Rank of H~_1 of the complex of partial assignments on three variables with these allowed triples."""
    pairs = [((i, a), (j, b)) for i, j in combinations(range(3), 2) for a in range(q) for b in range(q)]
    index = {pair: k for k, pair in enumerate(pairs)}
    boundary = []
    for t in allowed:
        row = [0] * len(pairs)
        faces = [((1, t[1]), (2, t[2])), ((0, t[0]), (2, t[2])), ((0, t[0]), (1, t[1]))]
        for sign, face in zip((1, -1, 1), faces):
            row[index[face]] = sign
        boundary.append(row)
    vertices = 3 * q
    cycles = len(pairs) - (vertices - 1)
    return cycles - (rank_mod(boundary, p) if boundary else 0)


def hole_census(rows):
    ranks = {}
    for knot_index, relation in enumerate(two_loop_knots()):
        allowed = [tuple(int(x) for x in r) for r in relation.rows]
        excluded = 8 - len(allowed)
        for ring in ("F2", "F3", "Q"):
            ranks[(knot_index, ring)] = (scope_hole(2, allowed, RING_PRIME[ring]), excluded)
    knot_ok = all(rank == excluded - 1 for rank, excluded in ranks.values())
    controls = {
        "atom_has_no_hole": all(scope_hole(2, [t for t in product(range(2), repeat=3) if t != (1, 1, 1)],
                                           RING_PRIME[r]) == 0 for r in ("F2", "F3", "Q")),
        "full_relation_has_no_hole": all(scope_hole(2, list(product(range(2), repeat=3)), RING_PRIME[r]) == 0
                                         for r in ("F2", "F3", "Q")),
        "parity_has_rank_three": all(scope_hole(2, [t for t in product(range(2), repeat=3) if sum(t) % 2 == 1],
                                                RING_PRIME[r]) == 3 for r in ("F2", "F3", "Q")),
    }
    sum3 = [t for t in product(range(3), repeat=3) if (t[0] + t[1] - t[2]) % 3 == 1]
    z3_ranks = {ring: scope_hole(3, sum3, RING_PRIME[ring]) for ring in ("F2", "F3", "Q")}
    rows.append({"part": "knot_holes", "boolean_knots": len(two_loop_knots()),
                 "rank_is_excluded_minus_one": knot_ok,
                 "ranks": [{"knot": k, "ring": r, "rank": v[0], "excluded": v[1]} for (k, r), v in sorted(ranks.items())],
                 "sum_mod_3_ranks": z3_ranks, "controls": controls})
    return knot_ok, z3_ranks, controls


def network_holes(net):
    """Plain hole bound: sets of at most two edges never have a hole; report the scopes' hole ranks."""
    ranks = {}
    for v in range(net.n):
        bag = tuple(net.stars[v])
        allowed = net.local(bag)
        for ring in ("F2", "F3", "Q"):
            ranks[(v, ring)] = scope_hole(net.q, allowed, RING_PRIME[ring])
    every_scope_has_hole = all(r > 0 for r in ranks.values())
    return {"hole_bound": 2 if every_scope_has_hole else None, "scope_ranks": sorted(set(ranks.values()))}


# ---------------------------------------------------------------- main

def main() -> int:
    started = time.time()
    rng = random.Random(SEED)
    ARTIFACT.mkdir(parents=True, exist_ok=True)
    rows: list[dict] = []
    certificates: dict[str, dict] = {}
    lines: list[str] = []

    def log(message):
        print(message, flush=True)
        lines.append(message)

    graphs = {}
    for n in (4, 6, 8):
        for edges in cubic_graphs(n):
            label = name_graph(n, edges)
            while label in graphs:
                label += "b"
            graphs[label] = (n, edges)
    log(f"[{time.time() - started:.0f}s] graphs: {sorted(graphs)}")
    params = {g: parameters(n, edges) for g, (n, edges) in graphs.items()}
    for g, (n, edges) in graphs.items():
        rows.append({"part": "graph", "graph": g, "vertices": n, "edges": edges, **params[g]})
        log(f"  {g}: {params[g]}")

    knot_ok, z3_ranks, hole_controls = hole_census(rows)
    log(f"[{time.time() - started:.0f}s] holes: Boolean knot ranks |E|-1: {knot_ok}; sum mod 3: {z3_ranks}")

    nae_possible = {}
    for g, (n, edges) in graphs.items():
        stars = [sorted(star(edges, v)) for v in range(n)]
        nae_possible[g] = any(all(len({x[e] for e in s}) > 1 for s in stars) for x in product((0, 1), repeat=len(edges)))
        net = Network(n, edges, 2, nae, f"{g}|NAE")
        rows.append({"part": "nae", "graph": g, "possible": nae_possible[g], **network_holes(net)})

    results = []
    for g, (n, edges) in graphs.items():
        placements = {"single": {0: 1}, "three": {0: 1, 1: 1, 2: 1}}
        odd = [rng.randrange(2) for _ in range(n)]
        if sum(odd) % 2 == 0:
            odd[n - 1] ^= 1
        placements["random"] = {v: c for v, c in enumerate(odd) if c}
        for pname, charges in placements.items():
            charge = [charges.get(v, 0) for v in range(n)]
            net = Network(n, edges, 2, tseitin2(edges, charge), f"{g}|Z2|{pname}")
            key = f"{g}|Z2|{pname}"
            record = {"part": "level", "graph": g, "group": "Z2", "placement": pname, "charge": charge,
                      **network_holes(net), "levels": {}}
            for ring in ("F2", "F3", "F5", "Q"):
                if ring == "Q" and len(edges) > 9 and pname != "single":
                    continue
                cap = 3 if ring == "F2" else MAX_LEVEL
                record["levels"][ring] = least_level(net, ring, cap=cap, certificates=certificates, key=key, log=log)
            record["levels"]["Z"] = ({"level": 3, "resolved": True, "via": "F2 refutation at level 3"}
                                     if record["levels"]["F2"]["level"] == 3 else {"level": None, "resolved": False})
            rows.append(record)
            results.append(record)
            log(f"[{time.time() - started:.0f}s] {key}: " + ", ".join(
                f"{r}={v['level']}" for r, v in record["levels"].items()))
        if len(edges) <= 9:
            charge = [1 if v in (0, 1) else 0 for v in range(n)]
            net = Network(n, edges, 2, tseitin2(edges, charge), f"{g}|Z2|even")
            record = {"part": "control_even", "graph": g, "charge": charge, "levels": {}}
            for ring in ("F2", "F3", "Q"):
                record["levels"][ring] = least_level(net, ring, cap=len(edges), certificates=certificates,
                                                     key=f"{g}|Z2|even", log=log)
            rows.append(record)
    for g in ("K4", "K33", "prism"):
        n, edges = graphs[g]
        for pname, charges in {"single": {0: 1}, "three": {0: 1, 1: 1, 2: 2}}.items():
            charge = [charges.get(v, 0) for v in range(n)]
            net = Network(n, edges, 3, tseitin3(edges, charge), f"{g}|Z3|{pname}")
            key = f"{g}|Z3|{pname}"
            record = {"part": "level", "graph": g, "group": "Z3", "placement": pname, "charge": charge,
                      **network_holes(net), "levels": {}}
            for ring in ("F3", "F2", "F5", "Q"):
                if ring == "Q" and g == "K33":
                    continue
                cap = 3 if ring == "F3" else MAX_LEVEL
                record["levels"][ring] = least_level(net, ring, cap=cap, certificates=certificates, key=key, log=log)
            record["levels"]["Z"] = ({"level": 3, "resolved": True, "via": "F3 refutation at level 3"}
                                     if record["levels"]["F3"]["level"] == 3 else {"level": None, "resolved": False})
            rows.append(record)
            results.append(record)
            log(f"[{time.time() - started:.0f}s] {key}: " + ", ".join(
                f"{r}={v['level']}" for r, v in record["levels"].items()))

    matched = {"Z2": ("F2", "Z"), "Z3": ("F3", "Z")}
    mismatched = {"Z2": ("F3", "F5", "Q"), "Z3": ("F2", "F5", "Q")}
    p1 = all(r["levels"][ring]["level"] == 3 for r in results for ring in matched[r["group"]])
    resolved = [(r, ring) for r in results for ring in mismatched[r["group"]]
                if ring in r["levels"] and r["levels"][ring]["resolved"]]
    p2 = bool(resolved) and all(r["levels"][ring]["level"] == params[r["graph"]]["toggle_width"] for r, ring in resolved)
    p2_minus = all(r["levels"][ring]["level"] == params[r["graph"]]["toggle_width"] - 1 for r, ring in resolved)
    p2_plus = all(r["levels"][ring]["level"] == params[r["graph"]]["toggle_width"] + 1 for r, ring in resolved)
    p3 = (knot_ok and all(v > 0 for v in z3_ranks.values())
          and all(r.get("hole_bound") == 2 for r in rows if r["part"] in ("level", "nae")))
    by_tw = defaultdict(set)
    for r in results:
        if r["group"] == "Z2" and r["placement"] == "single" and r["levels"]["F3"]["resolved"]:
            by_tw[params[r["graph"]]["treewidth"]].add(r["levels"]["F3"]["level"])
    p4 = any(len(levels) > 1 for levels in by_tw.values())
    by_graph_ring = defaultdict(set)
    for r, ring in resolved:
        by_graph_ring[(r["graph"], r["group"], ring)].add(r["levels"][ring]["level"])
    p5 = all(len(v) == 1 for v in by_graph_ring.values())
    p6 = all(nae_possible.values())
    controls = {
        "even_charge_never_refuted": all(v.get("never_refuted") and v["resolved"] for r in rows
                                         if r["part"] == "control_even" for v in r["levels"].values()),
        **hole_controls,
        "toggle_width_minus_one_fails": not p2_minus,
        "toggle_width_plus_one_fails": not p2_plus,
    }
    unresolved = sorted(f"{r['graph']}|{r['group']}|{r['placement']}|{ring}" for r in results
                        for ring, v in r["levels"].items() if not v["resolved"])
    result = {
        "experiment_id": "DEEP-HOLES-20261020-001A-E001",
        "predictions": {"P1": p1, "P2": p2, "P3": p3, "P4": p4, "P5": p5, "P6": p6},
        "signal": all((p1, p2, p3, p4, p5, p6)) and all(controls.values()),
        "controls": controls,
        "graphs": {g: {"vertices": n, **params[g]} for g, (n, _) in graphs.items()},
        "levels": {f"{r['graph']}|{r['group']}|{r['placement']}": {ring: v["level"] for ring, v in r["levels"].items()}
                   for r in results},
        "levels_by_treewidth_F3_single": {str(k): sorted(v) for k, v in by_tw.items()},
        "unresolved": unresolved,
        "nae_possible": nae_possible,
        "sum_mod_3_scope_hole_ranks": z3_ranks,
        "wall_seconds": round(time.time() - started, 1),
    }
    with (ARTIFACT / "raw_rows.jsonl").open("w") as handle:
        for row in rows:
            handle.write(json.dumps(row, sort_keys=True) + "\n")
    with gzip.open(ARTIFACT / "certificates.json.gz", "wt") as handle:
        json.dump(certificates, handle, sort_keys=True)
    (ARTIFACT / "result.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    log(json.dumps({"predictions": result["predictions"], "controls": controls, "unresolved": unresolved}, indent=1))
    log("signal" if result["signal"] else "no signal")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
