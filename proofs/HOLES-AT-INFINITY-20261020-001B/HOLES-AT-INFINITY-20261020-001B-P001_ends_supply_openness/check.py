#!/usr/bin/env python3
"""Checks for HOLES-AT-INFINITY-20261020-001B-P001: ends supply open distinctions.

Each infinite graph is a neighbour function with a root, studied through
truncations of the ball B_R of radius R about the root.

- The open truncation keeps the parity constraint at every vertex of B_R and
  every edge incident to B_R, so the edges leaving the ball are free. Once R is
  past the finite sides of the cuts in question, its projection onto the edges
  near the root is the infinite system's projection (proof, Lemma 3). The
  checks confirm that the projection is stable in R.
- The closed truncation keeps only the edges inside B_R. Its fundamental cycles
  are the finite circuits used to call a parity loop-supplied, and the sphere
  of radius R tells which sides of a cut are infinite.

The theorems are uniform and proved in proof.md. These checks calibrate them on
the declared graphs and radii. Each check also runs once on a deliberately
wrong input, which it must reject.

    python3 -B check.py          verify result.json against a fresh run
    python3 -B check.py --write  write result.json
"""

from __future__ import annotations

import json
import random
import sys
from collections import deque
from itertools import product
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from knotlab.knots import check_knot  # noqa: E402
from knotlab.relations import Relation  # noqa: E402


def parity(x: int) -> int:
    return bin(x).count("1") & 1


# ------------------------------------------------------------------ graphs

class Graph:
    """A locally finite graph given by a neighbour function and a root."""

    def __init__(self, name, root, nbrs, ends):
        self.name, self.root, self.nbrs, self.ends = name, root, nbrs, ends

    def plus_edge(self, u, v):
        base = self.nbrs

        def nbrs(w):
            out = set(base(w))
            if w == u:
                out.add(v)
            if w == v:
                out.add(u)
            return out

        return Graph(f"{self.name} + edge {u}-{v}", self.root, nbrs, "modified")


def ray():
    return Graph("ray", (0,), lambda v: {(v[0] + 1,)} | ({(v[0] - 1,)} if v[0] > 0 else set()), "one end; a tree")


def line():
    return Graph("line", (0,), lambda v: {(v[0] - 1,), (v[0] + 1,)}, "two ends; a tree")


def _tripod_nbrs(v):
    if v == ("c",):
        return {("a", j, 1) for j in range(3)}
    _, j, i = v
    return {("a", j, i - 1) if i > 1 else ("c",), ("a", j, i + 1)}


def tripod():
    return Graph("tripod", ("c",), _tripod_nbrs, "three ends; a tree")


def folded_tripod(n):
    def nbrs(v):
        out = _tripod_nbrs(v)
        if v != ("c",) and v[2] > n:
            out |= {("a", k, v[2]) for k in range(3) if k != v[1]}
        return out

    return Graph(f"tripod folded beyond {n}", ("c",), nbrs, "one end")


def folded_line(n):
    def nbrs(v):
        out = {(v[0] - 1,), (v[0] + 1,)}
        if abs(v[0]) > n:
            out.add((-v[0],))
        return out

    return Graph(f"line folded beyond {n}", (0,), nbrs, "one end")


def ladder(two_way):
    def nbrs(v):
        i, s = v
        out = {(i + 1, s), (i, 1 - s)}
        if two_way or i > 0:
            out.add((i - 1, s))
        return out

    return Graph("two-way ladder" if two_way else "one-way ladder", (0, 0), nbrs,
                 "two ends" if two_way else "one end")


def tree3():
    def nbrs(w):
        out = {w + (a,) for a in range(3) if not w or a != w[-1]}
        if w:
            out.add(w[:-1])
        return out

    return Graph("3-regular tree", (), nbrs, "a Cantor set of ends; a tree")


def grid():
    return Graph("square grid", (0, 0),
                 lambda v: {(v[0] + 1, v[1]), (v[0] - 1, v[1]), (v[0], v[1] + 1), (v[0], v[1] - 1)}, "one end")


def ekey(u, v):
    return (u, v) if repr(u) <= repr(v) else (v, u)


def ball(g, radius):
    dist = {g.root: 0}
    queue = deque([g.root])
    while queue:
        u = queue.popleft()
        if dist[u] < radius:
            for w in sorted(g.nbrs(u), key=repr):
                if w not in dist:
                    dist[w] = dist[u] + 1
                    queue.append(w)
    return dist


def near_edges(g, r):
    """The edges incident to the ball of radius r."""
    dist = ball(g, r)
    return sorted({ekey(u, w) for u in dist for w in g.nbrs(u)}, key=repr)


class Truncation:
    def __init__(self, g, radius, closed):
        self.g, self.radius, self.closed = g, radius, closed
        self.dist = ball(g, radius)
        keys = {ekey(u, w) for u in self.dist for w in g.nbrs(u) if not closed or w in self.dist}
        self.edges = sorted(keys, key=repr)
        self.index = {e: k for k, e in enumerate(self.edges)}

    def rows(self, charge):
        out = []
        for v in self.dist:
            mask = 0
            for w in self.g.nbrs(v):
                k = self.index.get(ekey(v, w))
                if k is not None:
                    mask |= 1 << k
            out.append((mask, charge.get(v, 0) & 1))
        return out


# ------------------------------------------------------------------ GF(2)

def solve(nvars, rows):
    """A particular solution and a null-space basis of a GF(2) system, or None."""
    piv = []
    for mask, rhs in rows:
        for col, pm, pr in piv:
            if mask >> col & 1:
                mask ^= pm
                rhs ^= pr
        if mask == 0:
            if rhs:
                return None
            continue
        col = (mask & -mask).bit_length() - 1
        piv = [(c, pm ^ mask, pr ^ rhs) if pm >> col & 1 else (c, pm, pr) for c, pm, pr in piv]
        piv.append((col, mask, rhs))
    pivcols = {c for c, _, _ in piv}
    x0 = sum(1 << c for c, _, pr in piv if pr)
    basis = []
    for f in range(nvars):
        if f not in pivcols:
            vec = 1 << f
            for c, pm, _ in piv:
                if pm >> f & 1:
                    vec |= 1 << c
            basis.append(vec)
    return x0, basis


def span_basis(vectors):
    basis = {}
    for v in vectors:
        while v:
            top = v.bit_length() - 1
            if top in basis:
                v ^= basis[top]
            else:
                basis[top] = v
                break
    return basis


def reduce(v, basis):
    while v:
        top = v.bit_length() - 1
        if top not in basis:
            return v
        v ^= basis[top]
    return 0


def compress(vec, positions):
    return sum(1 << j for j, k in enumerate(positions) if vec >> k & 1)


class Projection:
    """An affine space of assignments to n chosen variables (bit j = variable j)."""

    def __init__(self, x0, basis, positions):
        self.n = len(positions)
        self.span = span_basis(compress(b, positions) for b in basis)
        self.x0 = reduce(compress(x0, positions), self.span)

    def constant(self, f):
        """The value of the parity of mask f if it is constant, else None."""
        if any(parity(f & b) for b in self.span.values()):
            return None
        return parity(f & self.x0)

    def same(self, other):
        if self.n != other.n or len(self.span) != len(other.span):
            return False
        if any(reduce(b, other.span) for b in self.span.values()):
            return False
        return reduce(self.x0 ^ other.x0, self.span) == 0

    def points(self):
        vecs = list(self.span.values())
        out = set()
        for bits in product((0, 1), repeat=len(vecs)):
            v = self.x0
            for b, on in zip(vecs, bits):
                if on:
                    v ^= b
            out.add(v)
        return out


def project(trunc, charge, keys, extra=()):
    sol = solve(len(trunc.edges), trunc.rows(charge) + list(extra))
    if sol is None:
        return None
    return Projection(*sol, [trunc.index[k] for k in keys])


# ------------------------------------------------------------------ classification

class Classifier:
    """Finite circuits and infinite sides, read from the closed truncation at a large radius.

    A parity of edges F (a mask over keys) is
    - "loop" if some fundamental cycle of the closed truncation meets F oddly;
    - otherwise F is a cut, and it is "end" if both of its sides reach the sphere,
    - and "constant" if one side misses the sphere; that side is finite and the
      parity's value is the charge of that side.
    """

    def __init__(self, g, radius, keys):
        t = Truncation(g, radius, closed=True)
        qpos = {k: j for j, k in enumerate(keys)}
        parent = {g.root: None}
        order = [g.root]
        queue = deque([g.root])
        while queue:
            u = queue.popleft()
            for w in sorted(g.nbrs(u), key=repr):
                if w in t.dist and w not in parent:
                    parent[w] = u
                    order.append(w)
                    queue.append(w)
        path = {g.root: 0}
        for w in order[1:]:
            e = ekey(w, parent[w])
            path[w] = path[parent[w]] ^ ((1 << qpos[e]) if e in qpos else 0)
        tree = {ekey(w, parent[w]) for w in order[1:]}
        cycles = []
        for e in t.edges:
            if e not in tree:
                u, w = e
                cycles.append(path[u] ^ path[w] ^ ((1 << qpos[e]) if e in qpos else 0))
        self.loops = span_basis(cycles)
        self.path = path
        self.sphere = [w for w, d in t.dist.items() if d == radius]
        self.radius = radius

    def label(self, f, w):
        return parity(f & self.path[w])

    def classify(self, f, charge):
        if any(parity(f & b) for b in self.loops.values()):
            return "loop", None
        labels = {self.label(f, w) for w in self.sphere}
        if labels == {0, 1}:
            return "end", None
        finite = 1 - labels.pop()
        return "constant", sum(c for v, c in charge.items() if self.label(f, v) == finite) & 1


# ------------------------------------------------------------------ Theorem 1

def classification_check(g, r, charge, r_open, r_big, swap_labels=False):
    keys = near_edges(g, r)
    projections = [project(Truncation(g, r_open + k, closed=False), charge, keys) for k in range(3)]
    stable = all(p.same(projections[0]) for p in projections[1:])
    proj = projections[0]
    cls = Classifier(g, r_big, keys)
    counts = {"loop": 0, "end": 0, "constant": 0}
    mismatches = 0
    for f in range(1 << len(keys)):
        kind, value = cls.classify(f, charge)
        if swap_labels and kind == "end":
            kind, value = "constant", 0
        counts[kind] += 1
        if proj.constant(f) != (value if kind == "constant" else None):
            mismatches += 1
    return {"graph": g.name, "ends": g.ends, "near_edges": len(keys), "parities": 1 << len(keys),
            "counts": counts, "mismatches": mismatches, "stable_in_radius": stable,
            "radii": {"near": r, "open": r_open, "closed": r_big}}


def finite_baseline(g, r, radius):
    """A closed truncation is a finite graph: its open parities are exactly the loop-supplied ones."""
    keys = near_edges(g, r)
    t = Truncation(g, radius, closed=True)
    proj = project(t, {}, keys)
    cls = Classifier(g, radius, keys)
    loop_only = all((proj.constant(f) is None) == any(parity(f & b) for b in cls.loops.values())
                    for f in range(1 << len(keys)))
    open_count = sum(proj.constant(f) is None for f in range(1 << len(keys)))
    return {"graph": g.name, "radius": radius, "open_parities": open_count, "open_iff_loop": loop_only}


# ------------------------------------------------------------------ Theorem 2

def vertex_knots(g, r, charge, r_open, r_big, closed_control=False):
    keys = near_edges(g, r)
    qpos = {k: j for j, k in enumerate(keys)}
    if closed_control:
        proj = project(Truncation(g, r_open, closed=True), {}, keys)
    else:
        proj = project(Truncation(g, r_open, closed=False), charge, keys)
    cls = Classifier(g, r_big, keys)
    rows, agree = [], True
    for v in ball(g, r - 1):
        inc = sorted({ekey(v, w) for w in g.nbrs(v)}, key=repr)
        d = len(inc)
        if d < 3:
            continue
        pos = [qpos[e] for e in inc]
        sub = Projection(proj.x0, list(proj.span.values()), pos)
        names = tuple(f"e{j}" for j in range(d))
        relation = Relation(names, frozenset(tuple(bool(p >> j & 1) for j in range(d)) for p in sub.points()))
        report = check_knot(relation, names[:-1], names[-1])
        predicted = all(cls.classify(sum(1 << pos[j] for j in range(d) if s >> j & 1), charge)[0] != "constant"
                        for s in range(1, (1 << d) - 1))
        sources = sorted({cls.classify(1 << p, charge)[0] for p in pos})
        rows.append({"vertex": repr(v), "degree": d, "knot": report.is_knot, "predicted": predicted,
                     "edge_sources": sources})
        agree &= report.is_knot == predicted
    return {"graph": g.name, "closed_truncation": closed_control, "vertices": len(rows),
            "knots": sum(row["knot"] for row in rows), "agree_with_prediction": agree,
            "edge_sources": sorted({s for row in rows for s in row["edge_sources"]}),
            "sample": rows[:4]}


# ------------------------------------------------------------------ Theorem 3

def fold_pair(plain, folded, n, charge):
    r = n - 1
    keys = near_edges(plain, r)
    radius = n + 3
    same = project(Truncation(plain, radius, False), charge, keys).same(
        project(Truncation(folded, radius, False), charge, keys))
    root_edges = [1 << j for j, e in enumerate(keys) if plain.root in e]
    plain_cls = Classifier(plain, n + 5, keys)
    folded_cls = Classifier(folded, n + 5, keys)
    return {"pair": f"{plain.name} / {folded.name}", "ball_radius": r, "same_projection": same,
            "root_edges_plain": sorted({plain_cls.classify(f, charge)[0] for f in root_edges}),
            "root_edges_folded": sorted({folded_cls.classify(f, charge)[0] for f in root_edges})}


def one_edge(g, r, charge, cap, inside=False, same_side=False):
    """Add one edge far outside the ball across an end-supplied cut; the ball's projection must not change."""
    keys = near_edges(g, r)
    far = r + 3
    cls = Classifier(g, far, keys)
    base = project(Truncation(g, far + 1, False), charge, keys)
    tried = unchanged = became_loop = 0
    for f in range(1, 1 << len(keys)):
        if tried == cap:
            break
        if cls.classify(f, charge)[0] != "end":
            continue
        side0 = [w for w in cls.sphere if cls.label(f, w) == 0]
        side1 = [w for w in cls.sphere if cls.label(f, w) == 1]
        u = side0[0]
        v = side0[-1] if same_side else side1[0]
        if inside:
            near = [w for w, d in ball(g, r).items() if d == r and cls.label(f, w) == 0]
            u = near[0]
        if u == v or v in g.nbrs(u):
            continue
        tried += 1
        h = g.plus_edge(u, v)
        unchanged += project(Truncation(h, far + 1, False), charge, keys).same(base)
        became_loop += Classifier(h, far + 2, keys).classify(f, charge)[0] == "loop"
    return {"graph": g.name, "end_supplied_parities_tried": tried, "projection_unchanged": unchanged,
            "became_loop_supplied": became_loop}


# ------------------------------------------------------------------ Theorem 4

def one_ended_moments(g, r, charge, r_open, r_big, wrong_side=False):
    keys = near_edges(g, r)
    proj = project(Truncation(g, r_open, False), charge, keys)
    cls = Classifier(g, r_big, keys)
    total = sum(charge.values()) & 1
    mismatches = end_cuts = 0
    for f in range(1 << len(keys)):
        kind, value = cls.classify(f, charge)
        end_cuts += kind == "end"
        if kind == "constant":
            tangle = -1 if (value ^ (total if wrong_side else 0)) else 1
        else:
            tangle = 0
        c = proj.constant(f)
        haar = 0 if c is None else (-1 if c else 1)
        mismatches += haar != tangle
    return {"graph": g.name, "moments": 1 << len(keys), "mismatches": mismatches, "end_separating_cuts": end_cuts}


def clusters(g, radius, window=5):
    """The dangling edges of the open truncation, grouped by component of G minus the ball."""
    dist = ball(g, radius + window)
    inner = {w for w, d in dist.items() if d <= radius}
    dangling = sorted({ekey(u, w) for u in inner for w in g.nbrs(u) if w not in inner}, key=repr)
    outer = {}
    for e in dangling:
        outer.setdefault(e[0] if e[0] not in inner else e[1], []).append(e)
    comp = {}
    for start in sorted(outer, key=repr):
        if start in comp:
            continue
        comp[start] = start
        queue = deque([start])
        while queue:
            u = queue.popleft()
            for w in g.nbrs(u):
                if w in dist and w not in inner and w not in comp:
                    comp[w] = start
                    queue.append(w)
    groups = {}
    for w, es in outer.items():
        groups.setdefault(comp[w], []).extend(es)
    return groups, comp


def end_moments(g, r, charge, r_open, r_big, omega, other):
    """Haar moments of the solutions whose hole went to the end omega, against the tangle of omega."""
    keys = near_edges(g, r)
    t = Truncation(g, r_open, False)
    groups, comp = clusters(g, r_open)
    target = comp[omega(r_open + 1)]
    extra = [(sum(1 << t.index[e] for e in es), int(start == target)) for start, es in groups.items()]
    conditioned = project(t, charge, keys, extra)
    plain = project(t, charge, keys)
    cls = Classifier(g, r_big, keys)
    result = {"graph": g.name, "clusters": len(groups), "moments": 1 << len(keys)}
    for name, end in (("own_end", omega), ("wrong_end", other)):
        mismatches = 0
        w_end = end(r_big)
        for f in range(1 << len(keys)):
            kind, value = cls.classify(f, charge)
            if kind == "loop":
                tangle = 0
            elif kind == "constant":
                tangle = -1 if value else 1
            else:
                small = 1 - cls.label(f, w_end)
                tangle = -1 if sum(c for v, c in charge.items() if cls.label(f, v) == small) & 1 else 1
            c = conditioned.constant(f)
            mismatches += (0 if c is None else (-1 if c else 1)) != tangle
        result[f"mismatches_{name}"] = mismatches
    result["unconditioned_end_cut_moments_zero"] = all(
        plain.constant(f) is None for f in range(1 << len(keys)) if cls.classify(f, charge)[0] == "end")
    return result


# ------------------------------------------------------------------ Proposition 5

def escape_paths(seed, trees, depth, fake_horizon=False):
    """Finite shadow of Proposition 5: in a binary tree with dangling edges at the horizon, every solution's
    one-path from the charged root reaches the horizon, and with no horizon the system is unsatisfiable."""
    rng = random.Random(seed)
    checked = unsat_without_horizon = paths_to_horizon = bad = 0
    for _ in range(trees):
        nodes = [()]
        frontier = [()]
        while frontier:
            w = frontier.pop()
            if len(w) < depth:
                for b in (0, 1):
                    if rng.random() < 0.65:
                        nodes.append(w + (b,))
                        frontier.append(w + (b,))
        node_set = set(nodes)
        horizon = [w for w in nodes if len(w) == depth]
        if fake_horizon:
            dead = [w for w in nodes if 0 < len(w) < depth and w + (0,) not in node_set and w + (1,) not in node_set]
            if not dead:
                continue
            horizon = [dead[0]]
        edges = [(w[:-1], w) for w in nodes if w] + [(w, "beyond") for w in horizon]
        index = {e: k for k, e in enumerate(edges)}
        rows = []
        for w in nodes:
            mask = 0
            for e in edges:
                if w in e:
                    mask |= 1 << index[e]
            rows.append((mask, 1 if w == () else 0))
        sol = solve(len(edges), rows)
        if sol is None:
            unsat_without_horizon += not horizon
            bad += bool(horizon)
            continue
        checked += 1
        x0, basis = sol
        for _ in range(8):
            x = x0
            for b in basis:
                if rng.random() < 0.5:
                    x ^= b
            w = ()
            while True:
                kids = [c for c in (w + (0,), w + (1,)) if c in node_set and x >> index[(w, c)] & 1]
                if not kids:
                    break
                w = kids[0]
            reached = len(w) == depth and x >> index[(w, "beyond")] & 1
            paths_to_horizon += bool(reached)
            bad += not reached
    return {"trees_satisfiable": checked, "unsatisfiable_without_horizon": unsat_without_horizon,
            "paths_reaching_horizon": paths_to_horizon, "paths_failing": bad}


# ------------------------------------------------------------------ run

def run():
    checks, controls, failures = {}, {}, []
    root_charge = lambda g: {g.root: 1}  # noqa: E731

    def two_charges(g):
        far = sorted((w for w, d in ball(g, 2).items() if d == 2), key=repr)[0]
        return {g.root: 1, far: 1}

    plan = [(ray(), 2), (line(), 2), (tripod(), 2), (folded_tripod(3), 2), (folded_line(3), 2),
            (ladder(False), 2), (ladder(True), 2), (tree3(), 1), (grid(), 1)]
    rows = []
    for g, r in plan:
        for label, charge in (("root", root_charge(g)), ("two", two_charges(g))):
            row = classification_check(g, r, charge, r + 4, r + 8)
            row["charge"] = label
            rows.append(row)
            if row["mismatches"] or not row["stable_in_radius"]:
                failures.append(f"Theorem 1 on {g.name} ({label} charge)")
    checks["theorem_1_classification"] = rows
    expected_end = {"ray": False, "line": True, "tripod": True, "tripod folded beyond 3": False,
                    "line folded beyond 3": False, "one-way ladder": False, "two-way ladder": True,
                    "3-regular tree": True, "square grid": False}
    for row in rows:
        if (row["counts"]["end"] > 0) != expected_end[row["graph"]]:
            failures.append(f"end-supplied parities present or absent unexpectedly on {row['graph']}")
    swapped = classification_check(tripod(), 2, root_charge(tripod()), 6, 10, swap_labels=True)
    controls["theorem_1_end_parities_called_constant"] = {"mismatches": swapped["mismatches"],
                                                          "rejected": swapped["mismatches"] > 0}

    baseline = [finite_baseline(g, r, r + 6) for g, r in ((tree3(), 1), (grid(), 1), (ladder(True), 2))]
    checks["finite_baseline"] = baseline
    if not all(row["open_iff_loop"] for row in baseline):
        failures.append("a finite closed truncation has an open parity that no loop supplies")

    knot_plan = [(tripod(), 2), (folded_tripod(3), 2), (ladder(False), 3), (ladder(True), 3), (tree3(), 3), (grid(), 2)]
    knot_rows = [vertex_knots(g, r, root_charge(g), r + 4, r + 8) for g, r in knot_plan]
    checks["theorem_2_vertex_knots"] = knot_rows
    for row in knot_rows:
        if not row["agree_with_prediction"]:
            failures.append(f"Theorem 2 on {row['graph']}")
    tree_row = knot_rows[4]
    if tree_row["knots"] != tree_row["vertices"] or tree_row["edge_sources"] != ["end"]:
        failures.append("the 3-regular tree does not carry an end-supplied knot at every vertex")
    closed_tree = vertex_knots(tree3(), 3, {}, 6, 11, closed_control=True)
    checks["theorem_2_closed_tree"] = {"vertices": closed_tree["vertices"], "knots": closed_tree["knots"]}
    if closed_tree["knots"]:
        failures.append("a finite closed tree carries a knot")
    controls["theorem_2_closed_tree_against_infinite_prediction"] = {
        "rejected": not closed_tree["agree_with_prediction"]}

    pairs = [fold_pair(tripod(), folded_tripod(n), n, {("c",): 1}) for n in (2, 3, 4)]
    pairs += [fold_pair(line(), folded_line(n), n, {(0,): 1}) for n in (2, 3, 4)]
    checks["theorem_3_folds"] = pairs
    for row in pairs:
        if not (row["same_projection"] and row["root_edges_plain"] == ["end"] and row["root_edges_folded"] == ["loop"]):
            failures.append(f"Theorem 3 fold pair {row['pair']}")
    edge_rows = [one_edge(g, r, root_charge(g), 40) for g, r in ((line(), 2), (tripod(), 2), (ladder(True), 2), (tree3(), 1))]
    checks["theorem_3_one_edge"] = edge_rows
    for row in edge_rows:
        if not (row["end_supplied_parities_tried"] and row["projection_unchanged"] == row["end_supplied_parities_tried"]
                == row["became_loop_supplied"]):
            failures.append(f"Theorem 3 one-edge construction on {row['graph']}")
    inside = one_edge(tripod(), 2, root_charge(tripod()), 10, inside=True)
    same_side = one_edge(tree3(), 1, root_charge(tree3()), 10, same_side=True)
    controls["theorem_3_edge_inside_ball"] = {**inside, "rejected": inside["projection_unchanged"] < inside["end_supplied_parities_tried"]}
    controls["theorem_3_edge_on_one_side"] = {**same_side, "rejected": same_side["became_loop_supplied"] < same_side["end_supplied_parities_tried"]}

    one_ended = [(ray(), 2), (ladder(False), 2), (grid(), 1), (folded_tripod(3), 2), (folded_line(3), 2)]
    moment_rows = [one_ended_moments(g, r, root_charge(g), r + 4, r + 8) for g, r in one_ended]
    checks["theorem_4_one_ended"] = moment_rows
    for row in moment_rows:
        if row["mismatches"] or row["end_separating_cuts"]:
            failures.append(f"Theorem 4 on {row['graph']}")
    wrong = one_ended_moments(grid(), 1, {(0, 0): 1}, 5, 9, wrong_side=True)
    controls["theorem_4_infinite_side_charge"] = {**wrong, "rejected": wrong["mismatches"] > 0}

    ends_plan = [
        (line(), 2, lambda d: (d,), lambda d: (-d,)),
        (tripod(), 2, lambda d: ("a", 0, d), lambda d: ("a", 1, d)),
        (ladder(True), 2, lambda d: (d, 0), lambda d: (-d, 0)),
        (tree3(), 1, lambda d: tuple(k % 2 for k in range(d)), lambda d: tuple((k + 1) % 2 for k in range(d))),
    ]
    end_rows = [end_moments(g, r, root_charge(g), r + 4, r + 8, om, ot) for g, r, om, ot in ends_plan]
    checks["theorem_4_each_end"] = end_rows
    for row in end_rows:
        if row["mismatches_own_end"] or not row["unconditioned_end_cut_moments_zero"]:
            failures.append(f"Theorem 4 (end tangle) on {row['graph']}")
    controls["theorem_4_wrong_end"] = {row["graph"]: row["mismatches_wrong_end"] for row in end_rows}
    controls["theorem_4_wrong_end"]["rejected"] = all(row["mismatches_wrong_end"] > 0 for row in end_rows)

    escape = escape_paths(20261020, 300, 6)
    checks["proposition_5_finite_shadow"] = escape
    if escape["paths_failing"] or not escape["trees_satisfiable"] or not escape["unsatisfiable_without_horizon"]:
        failures.append("Proposition 5 finite shadow")
    fake = escape_paths(7, 60, 6, fake_horizon=True)
    controls["proposition_5_horizon_at_a_dead_end"] = {**fake, "rejected": fake["paths_failing"] > 0}

    knot = check_knot(Relation(("A", "B", "c"), frozenset(r for r in product((False, True), repeat=3) if sum(r) % 2 == 1)),
                      ("A", "B"), "c")
    checks["knotlab_three_end_parity"] = {"is_knot": knot.is_knot, "pairwise_definable": knot.pairwise_definable,
                                          "minimum_width": knot.minimum_width}
    if not knot.is_knot:
        failures.append("knotlab rejects the three-end parity")

    for name, control in controls.items():
        if not control.get("rejected"):
            failures.append(f"control not rejected: {name}")
    return checks, controls, failures


def main() -> int:
    write = "--write" in sys.argv[1:]
    checks, controls, failures = run()
    manifest = json.loads((HERE / "manifest.json").read_text())
    result = {
        "schema_version": 3, "artifact_id": manifest["artifact_id"], "kind": "proof", "ticket": manifest["ticket"],
        "proof": manifest["proof"], "status": "passed" if not failures else "failed", "claim": manifest["claim"],
        "foundation_contract": manifest["foundation_contract"], "semantic_domains": manifest["semantic_domains"],
        "evidence_modes": manifest["evidence_modes"], "thesis_alignment": manifest["thesis_alignment"],
        "safe_conclusions": manifest["safe_to_conclude"], "checks": checks, "controls": controls, "failures": failures,
    }
    path = HERE / "result.json"
    text = json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    if write:
        path.write_text(text)
    elif not path.exists() or json.loads(path.read_text()) != json.loads(text):
        print("result.json does not match a fresh run; rerun with --write after review")
        return 1
    print(f"{result['status']}: failures {failures}")
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
