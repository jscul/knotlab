#!/usr/bin/env python3
"""LOGIC-AXIS-20261107-001C-E001 (exploratory): substitution towers of parity knots with nothing drawn.

Run with the workspace interpreter (needs scipy for the mixed-integer program):

    .venv/bin/python -B experiments/LOGIC-AXIS-20261107-001C/LOGIC-AXIS-20261107-001C-E001_towers_with_nothing_drawn/run.py

Writes artifacts/LOGIC-AXIS-20261107-001C/LOGIC-AXIS-20261107-001C-E001_towers_with_nothing_drawn/run/result.json.

Model. A hub-free parity law is a knot graph: each knot is a vertex whose three distinctions are its
incident edges; a distinction shared by two knots is an edge between them; a distinction in one knot (an
original leg, or a dangling loop) is an edge to an outside vertex INF that carries no constraint. The
implied parity checks are the cuts delta(U) for sets U of knots, so the K1-K3 knots are the bonds.
Bond distance between two distinctions = least bond through both, minus one: a minimum cut over U that
contains a path between the two edges' chosen endpoints (connectivity by a unit flow). Hubbed gadgets
are handled by an exhaustive circuit search on the allowed states.
"""

from __future__ import annotations

import json
import math
import random
import sys
import time
from itertools import combinations
from pathlib import Path

import numpy as np
from scipy.optimize import Bounds, LinearConstraint, milp
from scipy.sparse import lil_matrix

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUT = ROOT / "artifacts" / "LOGIC-AXIS-20261107-001C" / "LOGIC-AXIS-20261107-001C-E001_towers_with_nothing_drawn" / "run"
INF = "INF"
RNG = random.Random(20261107)

# --- gadgets (hub-free): vertices, legs a,b,c, internal edges, dangling loops -------------------------
GADGETS = {
    "G0 corner triangle (2026-10-20 refinement; no new loops)": {
        "verts": ["A", "B", "C"], "legs": ["A", "B", "C"],
        "edges": [("A", "B"), ("B", "C"), ("C", "A")], "loops": []},
    "G1 star, a loop at each corner knot": {
        "verts": ["A", "B", "C", "O"], "legs": ["A", "B", "C"],
        "edges": [("A", "O"), ("B", "O"), ("C", "O")], "loops": ["A", "B", "C"]},
    "G2 hexagon, a loop on each edge knot": {
        "verts": ["A", "B", "C", "P", "Q", "R"], "legs": ["A", "B", "C"],
        "edges": [("A", "P"), ("P", "B"), ("B", "Q"), ("Q", "C"), ("C", "R"), ("R", "A")], "loops": ["P", "Q", "R"]},
    "G4 prism, a loop at each outer knot": {
        "verts": ["A", "B", "C", "A2", "B2", "C2"], "legs": ["A", "B", "C"],
        "edges": [("A", "A2"), ("B", "B2"), ("C", "C2"), ("A2", "B2"), ("B2", "C2"), ("C2", "A2")], "loops": ["A", "B", "C"]},
}
MAX_LEVEL = {"G0": 5, "G1": 5, "G2": 4, "G4": 4}


class Tower:
    """Knot graph: vertices with three incident edge ids; edges with two endpoint slots (vertex or INF)."""

    def __init__(self):
        self.ends: dict[int, list] = {0: ["X", INF], 1: ["X", INF], 2: ["X", INF]}
        self.inc = {"X": [0, 1, 2]}
        self.next_edge = 3
        self.original = (0, 1, 2)  # a, b, c

    def substitute(self, g: dict) -> "Tower":
        t = Tower.__new__(Tower)
        t.ends = {e: list(v) for e, v in self.ends.items()}
        t.inc = {}
        t.next_edge = self.next_edge
        t.original = self.original
        for v, edges in self.inc.items():
            name = {x: (v, x) if not isinstance(v, tuple) else v + (x,) for x in g["verts"]}
            for x in g["verts"]:
                t.inc[name[x]] = []
            for leg_vertex, e in zip(g["legs"], edges):
                if t.ends[e][0] == v:
                    t.ends[e][0] = name[leg_vertex]
                elif t.ends[e][1] == v:
                    t.ends[e][1] = name[leg_vertex]
                else:
                    raise AssertionError("edge does not meet the substituted knot")
                t.inc[name[leg_vertex]].append(e)
            for x, y in g["edges"]:
                e = t.next_edge
                t.next_edge += 1
                t.ends[e] = [name[x], name[y]]
                t.inc[name[x]].append(e)
                t.inc[name[y]].append(e)
            for x in g["loops"]:
                e = t.next_edge
                t.next_edge += 1
                t.ends[e] = [name[x], INF]
                t.inc[name[x]].append(e)
        assert all(len(v) == 3 for v in t.inc.values())
        return t

    # parity law on the edges
    def columns(self):
        edges = sorted(self.ends)
        index = {e: i for i, e in enumerate(edges)}
        rows = []
        for v, inc in self.inc.items():
            m = 0
            for e in inc:
                m ^= 1 << index[e]
            rows.append(m)
        basis = []
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
        return col, len(sols)


def rank(vs):
    basis = {}
    r = 0
    for v in vs:
        while v:
            h = v.bit_length() - 1
            if h in basis:
                v ^= basis[h]
            else:
                basis[h] = v
                r += 1
                break
    return r


def is_knot(col, s):
    total = 0
    for e in s:
        total ^= col[e]
    return len(s) >= 3 and total == 0 and rank(col[e] for e in s) == len(s) - 1


def circuit_search(col, u, v, max_size):
    """Exhaustive smallest knot through u, v (meet in the middle)."""
    others = [w for w in col if w not in (u, v)]
    target = col[u] ^ col[v]
    for extra in range(1, max_size - 1):
        half = extra // 2
        table = {}
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
                    return len(s) - 1
    return None


def bond_distance(t: Tower, e: int, f: int, connected: bool = True) -> int:
    """Least bond through edges e and f, minus one (exact minimum connected cut)."""
    verts = list(t.inc)
    vindex = {v: i for i, v in enumerate(verts)}
    best = None
    def sides(edge):
        a, b = t.ends[edge]
        return [(a, b)] if b == INF else ([(b, a)] if a == INF else [(a, b), (b, a)])
    for inside_e, outside_e in sides(e):
        for inside_f, outside_f in sides(f):
            value = _cut_milp(t, verts, vindex, inside_e, outside_e, inside_f, outside_f, connected)
            if value is not None and (best is None or value < best):
                best = value
    return best - 1


def _cut_milp(t, verts, vindex, ie, oe, if_, of, connected):
    edges = sorted(t.ends)
    n, m = len(verts), len(edges)
    internal = [e for e in edges if INF not in t.ends[e]]
    k = len(internal)
    nvar = n + m + (2 * k if connected else 0)
    c = np.zeros(nvar)
    c[n:n + m] = 1.0
    rows, lo, hi = [], [], []
    A = lil_matrix((2 * m + (4 * k + n if connected else 0), nvar))
    r = 0
    for j, e in enumerate(edges):
        a, b = t.ends[e]
        if b == INF or a == INF:
            v = a if b == INF else b
            A[r, n + j] = 1
            A[r, vindex[v]] = -1
            lo.append(0)
            hi.append(np.inf)
            r += 1
        else:
            A[r, n + j] = 1
            A[r, vindex[a]] = -1
            A[r, vindex[b]] = 1
            lo.append(0)
            hi.append(np.inf)
            r += 1
            A[r, n + j] = 1
            A[r, vindex[a]] = 1
            A[r, vindex[b]] = -1
            lo.append(0)
            hi.append(np.inf)
            r += 1
    if connected:
        flows = {}
        for q, e in enumerate(internal):
            a, b = t.ends[e]
            flows[(a, b, e)] = n + m + 2 * q
            flows[(b, a, e)] = n + m + 2 * q + 1
        for (a, b, e), col in flows.items():
            for endpoint in (a, b):
                A[r, col] = 1
                A[r, vindex[endpoint]] = -1
                lo.append(-np.inf)
                hi.append(0)
                r += 1
        source, sink = ie, if_
        base = r
        for v in verts:
            want = (1 if v == source else 0) - (1 if v == sink else 0)
            lo.append(want)
            hi.append(want)
        for (a, b, e), col in flows.items():
            A[base + vindex[a], col] += 1
            A[base + vindex[b], col] -= 1
        r += n
    A = A[:r].tocsr()
    lb = np.zeros(nvar)
    ub = np.ones(nvar)
    ub[n + m:] = 1.0
    for v in (ie, if_):
        lb[vindex[v]] = 1
    for v in (oe, of):
        if v != INF:
            ub[vindex[v]] = 0
    if any(lb[i] > ub[i] for i in range(nvar)):
        return None
    integrality = np.zeros(nvar)
    integrality[:n] = 1
    res = milp(c, constraints=LinearConstraint(A, lo, hi), integrality=integrality, bounds=Bounds(lb, ub))
    if res.status != 0:
        return None
    return int(round(res.fun))


def hubbed_tower(levels: int):
    """G6: corner triangle plus middle knot (u, v, w each in three knots), on explicit knots."""
    knots = [("a", "b", "c")]
    variables = ["a", "b", "c"]
    fresh = 0
    out = []
    for level in range(levels + 1):
        rows, index = [], {x: i for i, x in enumerate(variables)}
        col = _columns(variables, knots)
        explicit = {frozenset(k) for k in knots}
        tri = _three_knots(col)
        out.append({"level": level, "knots": len(knots), "variables": len(variables),
                    "old knot {a,b,c} kept": is_knot(col, ("a", "b", "c")),
                    "bond distance a-b": circuit_search(col, "a", "b", 6),
                    "three-place knots not explicit": len(tri - explicit)})
        if level == levels:
            break
        new = []
        for x, y, z in knots:
            u, v, w = f"u{fresh}", f"v{fresh}", f"w{fresh}"
            fresh += 1
            variables += [u, v, w]
            new += [(x, u, v), (y, v, w), (z, w, u), (u, v, w)]
        knots = new
    return out


def _columns(variables, knots):
    index = {x: i for i, x in enumerate(variables)}
    rows = []
    for k in knots:
        m = 0
        for x in k:
            m ^= 1 << index[x]
        rows.append(m)
    basis = []
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
    for free in range(len(variables)):
        if free in pivots:
            continue
        s = 1 << free
        for p, b in basis:
            if b >> free & 1:
                s |= 1 << p
        sols.append(s)
    col = {}
    for x, i in index.items():
        c = 0
        for j, s in enumerate(sols):
            if s >> i & 1:
                c |= 1 << j
        col[x] = c
    return col


def _three_knots(col):
    lookup = {}
    for x, c in col.items():
        lookup.setdefault(c, []).append(x)
    found = set()
    names = list(col)
    for i, x in enumerate(names):
        for y in names[i + 1:]:
            for z in lookup.get(col[x] ^ col[y], []):
                if z not in (x, y) and is_knot(col, (x, y, z)):
                    found.add(frozenset((x, y, z)))
    return found


def run():
    started = time.time()
    results = {}
    for name, g in GADGETS.items():
        key = name.split()[0]
        t = Tower()
        levels = []
        for level in range(MAX_LEVEL[key] + 1):
            if len(t.inc) > 8000:
                break
            a, b, c = t.original
            entry = {"level": level, "knots": len(t.inc), "distinctions": len(t.ends)}
            entry["bond distance a-b"] = bond_distance(t, a, b)
            if len(t.ends) <= 70:
                col, bits = t.columns()
                entry["open bits (dimension of allowed states)"] = bits
                entry["old knot {a,b,c} kept"] = is_knot(col, (a, b, c))
                explicit = {frozenset(inc) for inc in t.inc.values()}
                entry["three-place knots not explicit"] = len(_three_knots(col) - explicit)
                if len(t.ends) <= 40:
                    entry["exhaustive circuit search a-b"] = circuit_search(col, a, b, min(entry["bond distance a-b"] + 2, 12))
            else:
                entry["open bits (dimension of allowed states)"] = len(t.ends) - (len(t.inc) - 0)
            levels.append(entry)
            if level < MAX_LEVEL[key]:
                t = t.substitute(g)
        copies = len(g["verts"])
        for i in range(1, len(levels)):
            d0, d1 = levels[i - 1]["bond distance a-b"], levels[i]["bond distance a-b"]
            levels[i]["stretch"] = round(d1 / d0, 4)
            levels[i]["dimension estimate log(copies)/log(stretch)"] = (
                round(math.log(copies) / math.log(d1 / d0), 4) if d1 > d0 else "infinite (no stretch)")
        results[name] = {"copies per level": copies, "loops added per substitution": len(g["loops"]), "levels": levels}
    # bond-ball profile on one tower level (G2 level 3): bond distance from leg a to every loop/leg
    profile = {}
    t = Tower()
    for _ in range(3):
        t = t.substitute(GADGETS["G2 hexagon, a loop on each edge knot"])
    a = t.original[0]
    targets = [e for e, ends in t.ends.items() if INF in ends and e != a]
    dists = [bond_distance(t, a, e) for e in targets]
    for r in sorted(set(dists)):
        profile[r] = sum(1 for d in dists if d <= r)
    results["bond-ball profile: G2 level 3, legs and loops within bond distance r of leg a"] = profile
    # hubbed gadget by exhaustive circuit search
    results["G6 corner triangle plus middle knot (hubs, no loops)"] = hubbed_tower(2)
    # controls
    t = Tower()
    for _ in range(3):
        t = t.substitute(GADGETS["G1 star, a loop at each corner knot"])
    a, b, _ = t.original
    connected_value = bond_distance(t, a, b)
    unconnected_value = bond_distance(t, a, b, connected=False)
    results["control: G1 level 3 cut program without connectivity"] = {
        "with connectivity (bond distance)": connected_value,
        "without connectivity (two separate stars)": unconnected_value,
        "differs": connected_value != unconnected_value}
    results["runtime seconds"] = round(time.time() - started, 1)
    return results


def main():
    results = run()
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "result.json").write_text(json.dumps(results, indent=1, default=str) + "\n")
    print(json.dumps(results, indent=1, default=str)[:12000])


if __name__ == "__main__":
    main()
