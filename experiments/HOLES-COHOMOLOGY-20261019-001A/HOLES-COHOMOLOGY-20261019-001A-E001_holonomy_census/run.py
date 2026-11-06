#!/usr/bin/env python3
"""Producer for HOLES-COHOMOLOGY-20261019-001A-E001 (frozen contract: contract.json).

Networks of permutation contact: a witness at every vertex, and on every edge a
link whose middle value names a permutation of the witness values. Forgetting
the witnesses leaves the composite on the middle values.

Composites are computed by backtracking over witness values, never from
holonomy. Linear relaxations are solved by exact elimination (F2, F3, Q) and by
integer elimination (Z); every verdict is stored with a certificate, either a
solution or a combination of equations that reads 0 = c with c nonzero. The
predictions are computed separately from holonomies, fixed points and orbits.
"""

from __future__ import annotations

import json
import math
import random
import sys
import time
from collections import defaultdict
from fractions import Fraction
from itertools import combinations, permutations, product
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
ARTIFACT = ROOT / "artifacts" / "HOLES-COHOMOLOGY-20261019-001A" / HERE.name
sys.path.insert(0, str(ROOT / "tools"))

from knotlab import Relation, check_knot  # noqa: E402

SEED = 20261019


# ---------------------------------------------------------------- permutations

def ident(n):
    return tuple(range(n))


def after(p, q):
    """p after q."""
    return tuple(p[x] for x in q)


def inverse(p):
    out = [0] * len(p)
    for x, y in enumerate(p):
        out[y] = x
    return tuple(out)


def cycle(n, points):
    out = list(range(n))
    for i, x in enumerate(points):
        out[x] = points[(i + 1) % len(points)]
    return tuple(out)


def from_cycles(n, cycles):
    out = list(range(n))
    for points in cycles:
        for i, x in enumerate(points):
            out[x] = points[(i + 1) % len(points)]
    return tuple(out)


def fixed(p):
    return frozenset(x for x in range(len(p)) if p[x] == x)


def cycle_type(p):
    seen, sizes = set(), []
    for x in range(len(p)):
        if x in seen:
            continue
        size, y = 0, x
        while y not in seen:
            seen.add(y)
            y = p[y]
            size += 1
        sizes.append(size)
    return tuple(sorted(sizes))


def generated(gens, n):
    group = {ident(n)}
    frontier = [ident(n)]
    while frontier:
        g = frontier.pop()
        for h in gens:
            k = after(h, g)
            if k not in group:
                group.add(k)
                frontier.append(k)
    return group


def orbits(gens, n):
    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for h in gens:
        for x in range(n):
            parent[find(x)] = find(h[x])
    sizes = defaultdict(int)
    for x in range(n):
        sizes[find(x)] += 1
    return sorted(sizes.values())


# ---------------------------------------------------------------- graphs

def ring_edges(length):
    return [(i, (i + 1) % length) for i in range(length)]


GRAPHS = {
    "C3": (3, ring_edges(3)),
    "C4": (4, ring_edges(4)),
    "C5": (5, ring_edges(5)),
    "C6": (6, ring_edges(6)),
    "theta": (5, [(0, 2), (2, 1), (0, 3), (3, 1), (0, 4), (4, 1)]),
    "K4": (4, [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)]),
    "K23": (5, [(0, 2), (0, 3), (0, 4), (1, 2), (1, 3), (1, 4)]),
    "prism": (6, [(0, 1), (1, 2), (0, 2), (3, 4), (4, 5), (3, 5), (0, 3), (1, 4), (2, 5)]),
    "bouquet2": (5, [(0, 1), (1, 2), (2, 0), (0, 3), (3, 4), (4, 0)]),
    "bouquet3": (7, [(0, 1), (1, 2), (2, 0), (0, 3), (3, 4), (4, 0), (0, 5), (5, 6), (6, 0)]),
}


class Network:
    """A connected graph with a fixed backtracking order (breadth first from vertex 0)."""

    def __init__(self, vertices, edges):
        self.vertices, self.edges = vertices, list(edges)
        adjacency = defaultdict(list)
        for e, (u, v) in enumerate(self.edges):
            adjacency[u].append(v)
            adjacency[v].append(u)
        order, seen = [0], {0}
        for x in order:
            for y in sorted(adjacency[x]):
                if y not in seen:
                    seen.add(y)
                    order.append(y)
        assert len(order) == vertices, "graph must be connected"
        self.order = order
        position = {v: i for i, v in enumerate(order)}
        # for each vertex in order: the edges to earlier vertices, as (edge, earlier vertex, earlier is tail)
        self.back = []
        for v in order:
            self.back.append([(e, (b if a == v else a), a != v)
                              for e, (a, b) in enumerate(self.edges)
                              if v in (a, b) and position[b if a == v else a] < position[v]])

    def satisfiable(self, allowed, values):
        """Backtracking over witness values; allowed[e] is the set of allowed (tail, head) pairs."""
        assignment = {}
        order, back = self.order, self.back

        def place(i):
            if i == len(order):
                return True
            v = order[i]
            for x in range(values):
                ok = True
                for e, w, w_is_tail in back[i]:
                    pair = (assignment[w], x) if w_is_tail else (x, assignment[w])
                    if pair not in allowed[e]:
                        ok = False
                        break
                if ok:
                    assignment[v] = x
                    if place(i + 1):
                        return True
            return False

        return place(0)

    def holonomies(self, perms):
        """Fundamental holonomies at vertex 0 for a breadth-first spanning tree (prediction side only)."""
        n = len(perms[0])
        g = {0: ident(n)}
        tree = set()
        for v in self.order[1:]:
            for e, (a, b) in enumerate(self.edges):
                if a == v and b in g:
                    g[v] = after(inverse(perms[e]), g[b])
                    tree.add(e)
                    break
                if b == v and a in g:
                    g[v] = after(perms[e], g[a])
                    tree.add(e)
                    break
        return [after(inverse(g[b]), after(perms[e], g[a]))
                for e, (a, b) in enumerate(self.edges) if e not in tree], tree


def graph_pairs(p):
    return frozenset((x, p[x]) for x in range(len(p)))


# ---------------------------------------------------------------- P1, P2, P6: composites

GROUPS = {
    "Z2": (2, sorted(generated([(1, 0)], 2))),
    "Z3": (3, sorted(generated([(1, 2, 0)], 3))),
    "S3": (3, sorted(permutations(range(3)))),
    "C6": (5, sorted(generated([from_cycles(5, [(0, 1), (2, 3, 4)])], 5))),
    "S4": (4, sorted(permutations(range(4)))),
}


def predicted_fraction(group, n, b1):
    total = Fraction(0)
    for size in range(1, n + 1):
        for points in combinations(range(n), size):
            stabilizer = sum(1 for g in group if all(g[x] == x for x in points))
            total += (-1) ** (size + 1) * Fraction(stabilizer, len(group)) ** b1
    return total


def group_census(rows):
    out = {}
    for gname, (n, group) in GROUPS.items():
        pairs = [graph_pairs(g) for g in group]
        for name, (vertices, edges) in GRAPHS.items():
            if gname == "S4" and len(edges) > 4:
                continue
            if gname in ("S3", "C6") and len(edges) > 6:
                continue
            net = Network(vertices, edges)
            b1 = len(edges) - vertices + 1
            allowed_count = mismatches = 0
            by_types = defaultdict(set)
            for pattern in product(range(len(group)), repeat=len(edges)):
                ok = net.satisfiable([pairs[i] for i in pattern], n)
                allowed_count += ok
                hol, _ = net.holonomies([group[i] for i in pattern])
                common = frozenset(range(n)).intersection(*[fixed(h) for h in hol])
                mismatches += ok != bool(common)
                if b1 == 2:
                    by_types[tuple(cycle_type(h) for h in hol)].add(ok)
            fraction = predicted_fraction(group, n, b1)
            row = {"part": "group", "graph": name, "group": gname, "values": n, "edges": len(edges),
                   "b1": b1, "patterns": len(group) ** len(edges), "allowed": allowed_count,
                   "predicted_allowed": str(fraction * len(group) ** len(edges)),
                   "allowed_fraction": str(Fraction(allowed_count, len(group) ** len(edges))),
                   "p1_mismatches": mismatches}
            if b1 == 2:
                row["p6_mixed_type_pairs"] = sorted([list(map(list, k)) for k, v in by_types.items() if len(v) > 1])
                row["p6_type_pairs"] = len(by_types)
            rows.append(row)
            out[(name, gname)] = row
    # P6 for S4: theta with tree edges fixed to the identity, both non-tree edges ranging over S4
    n, group = GROUPS["S4"]
    vertices, edges = GRAPHS["theta"]
    net = Network(vertices, edges)
    _, tree = net.holonomies([ident(n)] * len(edges))
    by_types = defaultdict(set)
    allowed_count = mismatches = 0
    free_edges = [e for e in range(len(edges)) if e not in tree]
    for choice in product(group, repeat=len(free_edges)):
        perms = [ident(n)] * len(edges)
        for e, p in zip(free_edges, choice):
            perms[e] = p
        ok = net.satisfiable([graph_pairs(p) for p in perms], n)
        allowed_count += ok
        hol, _ = net.holonomies(perms)
        mismatches += ok != bool(frozenset(range(n)).intersection(*[fixed(h) for h in hol]))
        by_types[tuple(cycle_type(h) for h in hol)].add(ok)
    rows.append({"part": "group_gauge_fixed", "graph": "theta", "group": "S4", "values": n,
                 "tree_edges_identity": sorted(tree), "patterns": len(group) ** 2, "allowed": allowed_count,
                 "p1_mismatches": mismatches,
                 "p6_mixed_type_pairs": sorted([list(map(list, k)) for k, v in by_types.items() if len(v) > 1]),
                 "p6_type_pairs": len(by_types)})
    return out


def random_link_census(rows, rng):
    total = mismatches = 0
    for name, (vertices, edges) in GRAPHS.items():
        net = Network(vertices, edges)
        for n in (3, 4, 5):
            for index in range(10):
                links = [[tuple(rng.sample(range(n), n)) for _ in range(2)] for _ in edges]
                count = bad = 0
                for pattern in product((0, 1), repeat=len(edges)):
                    perms = [links[e][m] for e, m in enumerate(pattern)]
                    ok = net.satisfiable([graph_pairs(p) for p in perms], n)
                    hol, _ = net.holonomies(perms)
                    common = frozenset(range(n)).intersection(*[fixed(h) for h in hol])
                    count += ok
                    bad += ok != bool(common)
                total += 1
                mismatches += bad
                rows.append({"part": "random_links", "graph": name, "values": n, "index": index,
                             "links": [[list(p) for p in pair] for pair in links],
                             "allowed": count, "p1_mismatches": bad})
    return total, mismatches


def relational_control(rows, rng):
    """Control 3: links that are not permutations break the per-loop holonomy rule."""
    breaks = 0
    for name in ("theta", "K4", "bouquet2"):
        vertices, edges = GRAPHS[name]
        net = Network(vertices, edges)
        n = 3
        for index in range(20):
            links = []
            for _ in edges:
                pair = []
                for _ in range(2):
                    p = tuple(rng.sample(range(n), n))
                    rel = set(graph_pairs(p))
                    rel.add((rng.randrange(n), rng.randrange(n)))
                    pair.append(frozenset(rel))
                links.append(pair)
            bad = 0
            for pattern in product((0, 1), repeat=len(edges)):
                rels = [links[e][m] for e, m in enumerate(pattern)]
                truth = net.satisfiable(rels, n)
                naive = per_loop_relational_rule(net, rels, n)
                bad += truth != naive
            breaks += bad > 0
            rows.append({"part": "relational_control", "graph": name, "index": index, "mismatches": bad})
    return breaks


def per_loop_relational_rule(net, rels, n):
    """Some base value u with (u, u) in every lasso's composed relation, loops treated separately."""
    _, tree = net.holonomies([ident(n)] * len(net.edges))
    paths = {0: frozenset((x, x) for x in range(n))}
    for v in net.order[1:]:
        for e in tree:
            a, b = net.edges[e]
            if a == v and b in paths:
                paths[v] = compose_rel(paths[b], frozenset((y, x) for x, y in rels[e]))
                break
            if b == v and a in paths:
                paths[v] = compose_rel(paths[a], rels[e])
                break
    for u in range(n):
        if all((u, u) in compose_rel(compose_rel(paths[a], rels[e]), frozenset((y, x) for x, y in paths[b]))
               for e, (a, b) in enumerate(net.edges) if e not in tree):
            return True
    return False


def compose_rel(first, second):
    return frozenset((a, c) for a, b in first for b2, c in second if b == b2)


# ---------------------------------------------------------------- P3, P4: selector bouquets and shapes

def bouquet(k):
    edges = []
    for i in range(k):
        x, y = 1 + 2 * i, 2 + 2 * i
        edges += [(0, x), (x, y), (y, 0)]
    return Network(2 * k + 1, edges)


def bouquet_composite(net, holonomies, decoys, n):
    """Allowed selector patterns, by backtracking on the bouquet network."""
    k = len(holonomies)
    allowed = set()
    for s in product((0, 1), repeat=k):
        perms = []
        for i in range(k):
            a, b = decoys[i]
            closing = inverse(after(b, a))
            c = after(holonomies[i], closing) if s[i] else closing
            perms += [a, b, c]
        if net.satisfiable([graph_pairs(p) for p in perms], n):
            allowed.add(s)
    return allowed


def shape(allowed, k):
    faces = set()
    for size in range(k + 1):
        for chosen in combinations(range(k), size):
            seen = {tuple(s[i] for i in chosen) for s in allowed}
            if len(seen) == 2 ** size:
                faces.add(frozenset(chosen))
    return faces


def nerve(holonomies, n):
    k = len(holonomies)
    fixes = [fixed(h) for h in holonomies]
    return {frozenset(chosen) for size in range(k + 1) for chosen in combinations(range(k), size)
            if frozenset(range(n)).intersection(*[fixes[i] for i in chosen])}


def minimal_nonfaces(faces, k):
    out = []
    for size in range(1, k + 1):
        for chosen in combinations(range(k), size):
            S = frozenset(chosen)
            if S not in faces and all(S - {i} in faces for i in S):
                out.append(S)
    return out


KNOT_CACHE: dict = {}


def knot_verdict(allowed, S):
    names = tuple(f"s{i}" for i in sorted(S))
    rows = frozenset(tuple(bool(s[i]) for i in sorted(S)) for s in allowed)
    key = (names, rows)
    if key not in KNOT_CACHE:
        relation = Relation(names, rows)
        report = check_knot(relation, names[:-1], names[-1])
        excluded = sorted(set(product((False, True), repeat=len(names))) - rows)
        KNOT_CACHE[key] = (report.is_knot, excluded == [tuple([True] * len(names))])
    return KNOT_CACHE[key]


def selector_census(rows, rng):
    summary = {}
    all_perms = {n: sorted(permutations(range(n))) for n in (3, 4, 5)}
    plan = [(2, 3, None), (2, 4, None), (3, 3, None), (3, 4, None), (3, 5, 3000), (4, 4, 3000), (4, 5, 3000)]
    for k, n, sample in plan:
        net = bouquet(k)
        if sample is None:
            tuples = list(product(all_perms[n], repeat=k))
        else:
            tuples = [tuple(rng.choice(all_perms[n]) for _ in range(k)) for _ in range(sample)]
        stats = defaultdict(int)
        examples = []
        for hol in tuples:
            decoys = [(tuple(rng.sample(range(n), n)), tuple(rng.sample(range(n), n))) for _ in range(k)]
            allowed = bouquet_composite(net, hol, decoys, n)
            faces = shape(allowed, k)
            predicted = nerve(hol, n)
            stats["tuples"] += 1
            stats["shape_mismatches"] += faces != predicted
            free_contact = all(h == ident(n) or not fixed(h) for h in hol)
            for S in minimal_nonfaces(faces, k):
                if len(S) == 2:
                    stats["ties"] += 1
                    stats["ties_under_free_contact"] += free_contact
                if len(S) >= 3:
                    is_knot, atom = knot_verdict(allowed, S)
                    stats[f"knots_among_{len(S)}_loops"] += 1
                    stats["knot_check_failures"] += not is_knot
                    stats["non_atom_knots"] += not atom
                    stats["knots_under_free_contact"] += free_contact
                    if len(examples) < 5:
                        examples.append({"holonomies": [list(h) for h in hol], "loops": sorted(S)})
            stats["free_contact_tuples"] += free_contact
        summary[f"k{k}_n{n}"] = dict(stats)
        rows.append({"part": "selector", "loops": k, "values": n, "exhaustive": sample is None,
                     **dict(stats), "knot_examples": examples})
    return summary


def complexes(k):
    subsets = list(range(2 ** k))
    out = []
    for family in range(2 ** (2 ** k)):
        members = {S for S in subsets if family >> S & 1}
        if 0 not in members:
            continue
        if all(S & ~(1 << i) in members for S in members for i in range(k) if S >> i & 1):
            out.append(members)
    return out


def complex_census(rows, rng):
    counts = {}
    mismatches = 0
    for k in range(1, 5):
        net = bouquet(k)
        listed = complexes(k)
        counts[k] = len(listed)
        for members in listed:
            facets = [S for S in members if not any(S != T and S & T == S for T in members)]
            n = len(facets) + 2
            hol = []
            for i in range(k):
                moved = [j for j, F in enumerate(facets) if not F >> i & 1] + [n - 2, n - 1]
                hol.append(cycle(n, moved))
            decoys = [(tuple(rng.sample(range(n), n)), tuple(rng.sample(range(n), n))) for _ in range(k)]
            allowed = bouquet_composite(net, hol, decoys, n)
            faces = shape(allowed, k)
            target = {frozenset(i for i in range(k) if S >> i & 1) for S in members}
            mismatches += faces != target
        rows.append({"part": "complexes", "loops": k, "complexes": len(listed), "mismatches": mismatches})
    return counts, mismatches


def size_bound(rows):
    out = {}
    for k in (2, 3, 4):
        found = 0
        perms = sorted(permutations(range(k)))
        for hol in product(perms, repeat=k):
            faces = nerve(hol, k)
            full = frozenset(range(k))
            if full not in faces and all(full - {i} in faces for i in range(k)):
                found += 1
        star = [cycle(k + 1, [j, k]) for j in range(k)]
        faces = nerve(star, k + 1)
        full = frozenset(range(k))
        star_is_knot = full not in faces and all(full - {i} in faces for i in range(k))
        out[k] = {"tuples_on_k_values": len(perms) ** k, "knots_on_k_values": found, "star_is_knot": star_is_knot}
        rows.append({"part": "size_bound", "loops": k, **out[k]})
    return out


# ---------------------------------------------------------------- P5: local reasoning

def var_name(S, f):
    return "v:" + ",".join(map(str, S)) + "|" + ",".join(map(str, f))


class Instance:
    def __init__(self, label, vertices, edges, perms, n):
        self.label, self.vertices, self.edges, self.perms, self.n = label, vertices, edges, perms, n
        self.constraints = [(a, b, p) for (a, b), p in zip(edges, perms)]

    def local(self, S):
        inside = [(a, b, p) for a, b, p in self.constraints if a in S and b in S]
        out = []
        for f in product(range(self.n), repeat=len(S)):
            value = dict(zip(S, f))
            if all(value[b] == p[value[a]] for a, b, p in inside):
                out.append(f)
        return out

    def system(self, level, pin=None):
        """Equations as (name, {variable: coefficient}, constant)."""
        bags = [tuple(S) for size in range(level + 1) for S in combinations(range(self.vertices), size)]
        sols = {S: self.local(S) for S in bags}
        equations = [("n:", {var_name((), ()): 1}, 1)]
        for big in bags:
            for v in big:
                small = tuple(x for x in big if x != v)
                at = big.index(v)
                extensions = defaultdict(list)
                for g in sols[big]:
                    extensions[g[:at] + g[at + 1:]].append(g)
                for f in sols[small]:
                    coefs = {var_name(small, f): 1}
                    for g in extensions[f]:
                        coefs[var_name(big, g)] = coefs.get(var_name(big, g), 0) - 1
                    name = "m:" + ",".join(map(str, big)) + "|" + str(v) + "|" + ",".join(map(str, f))
                    equations.append((name, coefs, 0))
        if pin is not None:
            for w in range(self.n):
                equations.append((f"p:{w}", {var_name((0,), (w,)): 1}, 1 if w == pin else 0))
        return equations


def solve_field(equations, p=None):
    """Row echelon elimination over F_p (p prime) or Q (p None); returns a solution or a refutation."""
    if p is None:
        conv = Fraction

        def inv(a):
            return 1 / a
    else:
        def conv(a):
            return a % p

        def inv(a):
            return pow(a, p - 2, p)
    names = sorted({v for _, coefs, _ in equations for v in coefs}, key=var_order)
    rank = {v: i for i, v in enumerate(names)}
    pivots = {}
    for name, coefs, c in equations:
        row = {}
        for v, a in coefs.items():
            a = conv(a)
            if a:
                row[rank[v]] = a
        const, hist = conv(c), {name: conv(1)}
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
            for e, a in ph.items():
                value = hist.get(e, 0) - f * a
                if p is not None:
                    value %= p
                if value:
                    hist[e] = value
                else:
                    hist.pop(e, None)
            if p is not None:
                const %= p
        if not row:
            if const:
                return {"feasible": False, "refutation": hist, "constant": const}
            continue
        v = min(row)
        scale = inv(row[v])
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


def var_order(name):
    """Bigger bags first, so elimination expresses larger bags through smaller ones."""
    bag = name[2:].split("|")[0]
    size = 0 if bag == "" else bag.count(",") + 1
    return (-size, name)


def solve_integer(equations):
    """Integer feasibility: unit-coefficient substitution, then column Hermite reduction of the rest."""
    rows = {name: (dict(coefs), c) for name, coefs, c in equations}
    holders = defaultdict(set)
    for name, (coefs, _) in rows.items():
        for v in coefs:
            holders[v].add(name)
    active = set(rows)
    definitions = []
    changed = True
    while changed:
        changed = False
        for name in sorted(active):
            coefs, c = rows[name]
            if not coefs:
                if c:
                    return {"feasible": False, "reason": "an equation reduces to 0 = %d" % c}
                active.discard(name)
                continue
            unit = next(((v, a) for v, a in sorted(coefs.items()) if a in (1, -1)), None)
            if unit is None:
                continue
            v, a = unit
            others = {j: b for j, b in coefs.items() if j != v}
            definitions.append((v, a, c, others))
            active.discard(name)
            for other in sorted(holders[v]):
                if other == name or other not in active:
                    continue
                ocoefs, oc = rows[other]
                k = ocoefs.pop(v)
                factor = k * a
                oc -= factor * c
                for j, b in others.items():
                    value = ocoefs.get(j, 0) - factor * b
                    if value:
                        ocoefs[j] = value
                        holders[j].add(other)
                    else:
                        ocoefs.pop(j, None)
                        holders[j].discard(other)
                rows[other] = (ocoefs, oc)
            changed = True
            break
    residual = [rows[name] for name in sorted(active) if rows[name][0]]
    for name in sorted(active):
        if not rows[name][0] and rows[name][1]:
            return {"feasible": False, "reason": "an equation reduces to 0 = %d" % rows[name][1]}
    columns = sorted({v for coefs, _ in residual for v in coefs})
    m, n = len(residual), len(columns)
    A = [[coefs.get(v, 0) for v in columns] for coefs, _ in residual]
    b = [c for _, c in residual]
    V = [[int(i == j) for j in range(n)] for i in range(n)]

    def column_op(target, source, q):
        for row in A:
            row[target] -= q * row[source]
        for row in V:
            row[target] -= q * row[source]

    def swap(i, j):
        for row in A:
            row[i], row[j] = row[j], row[i]
        for row in V:
            row[i], row[j] = row[j], row[i]

    r, pivot_rows = 0, []
    for i in range(m):
        if r == n:
            break
        for j in range(r + 1, n):
            while A[i][j]:
                if not A[i][r]:
                    swap(r, j)
                    continue
                column_op(j, r, A[i][j] // A[i][r])
                if A[i][j]:
                    swap(r, j)
        if A[i][r]:
            pivot_rows.append(i)
            r += 1
    y = [0] * n
    for t, i in enumerate(pivot_rows):
        rest = b[i] - sum(A[i][s] * y[s] for s in range(t))
        if rest % A[i][t]:
            return {"feasible": False, "reason": "column Hermite form needs a non-integer value"}
        y[t] = rest // A[i][t]
    for i in range(m):
        if sum(A[i][s] * y[s] for s in range(n)) != b[i]:
            return {"feasible": False, "reason": "a residual equation fails after the pivots are set"}
    x = {columns[j]: sum(V[j][t] * y[t] for t in range(n)) for j in range(n)}
    for v, a, c, others in reversed(definitions):
        x[v] = a * (c - sum(bv * x.get(j, 0) for j, bv in others.items()))
    for name, coefs, c in equations:
        assert sum(a * x.get(v, 0) for v, a in coefs.items()) == c, "integer solution fails an equation"
    return {"feasible": True, "solution": {v: value for v, value in x.items() if value}}


def arc_consistency(inst):
    domains = {v: set(range(inst.n)) for v in range(inst.vertices)}
    changed = True
    while changed:
        changed = False
        for a, b, p in inst.constraints:
            keep_a = {x for x in domains[a] if p[x] in domains[b]}
            keep_b = {y for y in domains[b] if any(p[x] == y for x in domains[a])}
            if keep_a != domains[a] or keep_b != domains[b]:
                domains[a], domains[b] = keep_a, keep_b
                changed = True
    return all(domains.values())


def path_consistency(inst):
    n, V = inst.n, inst.vertices
    full = {(x, y) for x in range(n) for y in range(n)}
    rel = {(u, v): set(full) for u in range(V) for v in range(V) if u != v}
    for a, b, p in inst.constraints:
        rel[(a, b)] &= {(x, p[x]) for x in range(n)}
        rel[(b, a)] &= {(p[x], x) for x in range(n)}
    changed = True
    while changed:
        changed = False
        for u, v, w in permutations(range(V), 3):
            through = {(x, z) for x, y in rel[(u, w)] for y2, z in rel[(w, v)] if y == y2}
            new = rel[(u, v)] & through
            if new != rel[(u, v)]:
                rel[(u, v)] = new
                rel[(v, u)] = {(y, x) for x, y in new}
                changed = True
    return all(rel.values())


def encode(value):
    return str(value) if isinstance(value, Fraction) else value


def ideal_contains_one(sizes, ring):
    if ring == "Q":
        return True
    if ring == "Z":
        return math.gcd(*sizes) == 1
    p = int(ring[1:])
    return any(size % p for size in sizes)


FIELDS = {"F2": 2, "F3": 3, "Q": None}


def ring_instances(rng):
    types = {2: [[1, 1], [2]], 3: [[1, 1, 1], [1, 2], [3]], 4: [[1, 1, 1, 1], [1, 1, 2], [1, 3], [2, 2], [4]],
             5: [[1, 1, 1, 1, 1], [1, 1, 1, 2], [1, 2, 2], [1, 1, 3], [2, 3], [1, 4], [5]]}
    out = []
    for length in (3, 4, 5, 6):
        for n, shapes in types.items():
            for sizes in shapes:
                cycles, start = [], 0
                for size in sorted(sizes, reverse=True):
                    cycles.append(tuple(range(start, start + size)))
                    start += size
                h = from_cycles(n, cycles)
                g = tuple(rng.sample(range(n), n))
                target = after(g, after(h, inverse(g)))
                perms = [tuple(rng.sample(range(n), n)) for _ in range(length - 1)]
                walked = ident(n)
                for p in perms:
                    walked = after(p, walked)
                perms.append(after(target, inverse(walked)))
                out.append(Instance(f"C{length} n={n} type={sizes}", length, ring_edges(length), perms, n))
    return out


def network_instances(rng):
    declared = [
        ("theta", 5, [[(0, 1)], [(2, 3, 4)]]),
        ("theta", 3, [[(0, 1)], [(1, 2)]]),
        ("theta", 4, [[(0, 1)], [(2, 3)]]),
        ("theta", 4, [[(0, 3)], [(1, 3)]]),
        ("theta", 3, [[(0, 1, 2)], [(0, 1)]]),
        ("theta", 5, [[(0, 1), (2, 3, 4)], []]),
        ("theta", 5, [[(0, 1, 2)], [(3, 4)]]),
        ("theta", 3, [[(0, 1)], [(0, 1)]]),
        ("K4", 4, [[(0, 3)], [(1, 3)], [(2, 3)]]),
        ("K4", 5, [[(0, 1)], [(2, 3, 4)], []]),
        ("bouquet2", 5, [[(0, 1)], [(2, 3, 4)]]),
        ("bouquet2", 3, [[(0, 1)], [(0, 2)]]),
    ]
    out = []
    for name, n, holonomy_cycles in declared:
        vertices, edges = GRAPHS[name]
        net = Network(vertices, edges)
        _, tree = net.holonomies([ident(n)] * len(edges))
        perms = [tuple(rng.sample(range(n), n)) if e in tree else None for e in range(len(edges))]
        g = {0: ident(n)}
        for v in net.order[1:]:
            for e in sorted(tree):
                a, b = edges[e]
                if a == v and b in g:
                    g[v] = after(inverse(perms[e]), g[b])
                    break
                if b == v and a in g:
                    g[v] = after(perms[e], g[a])
                    break
        targets = iter([from_cycles(n, cycles) for cycles in holonomy_cycles])
        for e, (a, b) in enumerate(edges):
            if e not in tree:
                h = next(targets)
                perms[e] = after(g[b], after(h, inverse(g[a])))
        out.append(Instance(f"{name} n={n} holonomies={holonomy_cycles}", vertices, edges, perms, n))
    return out


def local_census(rows, rng):
    instances = ring_instances(rng) + network_instances(rng)
    tallies = defaultdict(int)
    for inst in instances:
        net = Network(inst.vertices, inst.edges)
        hol, _ = net.holonomies(inst.perms)
        sizes = orbits(hol, inst.n)
        common = sorted(frozenset(range(inst.n)).intersection(*[fixed(h) for h in hol]))
        possible = net.satisfiable([graph_pairs(p) for p in inst.perms], inst.n)
        row = {"part": "local", "label": inst.label, "vertices": inst.vertices, "edges": inst.edges,
               "values": inst.n, "perms": [list(p) for p in inst.perms], "possible": possible,
               "prediction_side": {"holonomies": [list(h) for h in hol], "orbit_sizes": sizes,
                                   "common_fixed_points": common},
               "verdicts": {}}
        level2 = inst.system(2)
        for ring in ("F2", "F3", "Q", "Z"):
            result = solve_integer(level2) if ring == "Z" else solve_field(level2, FIELDS[ring])
            if ring == "Z" and not result["feasible"]:
                for p in (2, 3, 5):
                    modular = solve_field(level2, p)
                    if not modular["feasible"]:
                        result["mod_p_refutation"] = {"p": p, "refutation": modular["refutation"]}
                        break
            expected = ideal_contains_one(sizes, ring)
            row["verdicts"][f"level2_{ring}"] = encode_result(result)
            tallies["p5a_checked"] += 1
            tallies["p5a_mismatch"] += result["feasible"] != expected
            if not possible and result["feasible"]:
                tallies[f"level2_{ring}_fooled"] += 1
        for u in range(inst.n):
            pinned = inst.system(2, pin=u)
            for ring in ("F2", "F3", "Q", "Z"):
                result = solve_integer(pinned) if ring == "Z" else solve_field(pinned, FIELDS[ring])
                if ring == "Z" and not result["feasible"]:
                    for p in (2, 3, 5):
                        modular = solve_field(pinned, p)
                        if not modular["feasible"]:
                            result["mod_p_refutation"] = {"p": p, "refutation": modular["refutation"]}
                            break
                row["verdicts"][f"pinned{u}_{ring}"] = encode_result(result)
                tallies["p5b_checked"] += 1
                tallies["p5b_mismatch"] += result["feasible"] != (u in common)
        level3 = inst.system(3)
        for ring in ("F2", "F3", "Q"):
            result = solve_field(level3, FIELDS[ring])
            row["verdicts"][f"level3_{ring}"] = encode_result(result)
            tallies["p5c_checked"] += 1
            tallies["p5c_mismatch"] += result["feasible"] != possible
        ac, pc = arc_consistency(inst), path_consistency(inst)
        row["verdicts"]["arc_consistency_accepts"] = ac
        row["verdicts"]["path_consistency_accepts"] = pc
        tallies["p5d_checked"] += 1
        tallies["p5d_mismatch"] += (not ac) or (pc != possible)
        tallies["instances"] += 1
        tallies["impossible"] += not possible
        rows.append(row)
    return dict(tallies)


def encode_result(result):
    out = {"feasible": result["feasible"]}
    if "solution" in result:
        out["solution"] = {v: encode(a) for v, a in sorted(result["solution"].items())}
    if "refutation" in result:
        out["refutation"] = {e: encode(a) for e, a in sorted(result["refutation"].items())}
        out["constant"] = encode(result["constant"])
    if "reason" in result:
        out["reason"] = result["reason"]
    if "mod_p_refutation" in result:
        out["mod_p_refutation"] = {"p": result["mod_p_refutation"]["p"],
                                   "refutation": {e: a for e, a in sorted(result["mod_p_refutation"]["refutation"].items())}}
    return out


# ---------------------------------------------------------------- main

def main() -> int:
    started = time.time()
    rng = random.Random(SEED)
    ARTIFACT.mkdir(parents=True, exist_ok=True)
    rows: list[dict] = []

    group = group_census(rows)
    print(f"[{time.time() - started:.0f}s] group census: {len(group)} graph-group pairs", flush=True)
    random_total, random_mismatches = random_link_census(rows, rng)
    print(f"[{time.time() - started:.0f}s] random links: {random_total} assignments", flush=True)
    relational_breaks = relational_control(rows, rng)
    selectors = selector_census(rows, rng)
    print(f"[{time.time() - started:.0f}s] selectors done", flush=True)
    complex_counts, complex_mismatches = complex_census(rows, rng)
    bound = size_bound(rows)
    print(f"[{time.time() - started:.0f}s] complexes and size bound done", flush=True)
    local = local_census(rows, rng)
    print(f"[{time.time() - started:.0f}s] local reasoning done", flush=True)

    group_rows = [r for r in rows if r["part"] == "group"]
    fractions_by_group_b1 = defaultdict(set)
    for r in group_rows:
        fractions_by_group_b1[(r["group"], r["b1"])].add(r["allowed_fraction"])
    p1 = (all(r["p1_mismatches"] == 0 for r in rows if "p1_mismatches" in r) and random_mismatches == 0)
    p2 = (all(Fraction(r["predicted_allowed"]) == r["allowed"] for r in group_rows)
          and all(len(v) == 1 for v in fractions_by_group_b1.values())
          and all(r["allowed"] * GROUPS[r["group"]][1].__len__() ** r["b1"] == r["patterns"]
                  for r in group_rows if r["group"] in ("Z2", "Z3")))
    p3 = all(s.get("shape_mismatches", 0) == 0 and s.get("knot_check_failures", 0) == 0
             and s.get("non_atom_knots", 0) == 0 and s.get("ties_under_free_contact", 0) == 0
             and s.get("knots_under_free_contact", 0) == 0 for s in selectors.values())
    p4 = complex_mismatches == 0 and all(b["knots_on_k_values"] == 0 and b["star_is_knot"] for b in bound.values())
    p5 = all(local.get(key, 0) == 0 for key in ("p5a_mismatch", "p5b_mismatch", "p5c_mismatch", "p5d_mismatch"))
    p6_rows = [r for r in rows if "p6_mixed_type_pairs" in r]
    p6 = (all(not r["p6_mixed_type_pairs"] for r in p6_rows if r["group"] in ("Z2", "Z3"))
          and any(r["p6_mixed_type_pairs"] for r in p6_rows if r["group"] == "S3")
          and any(r["p6_mixed_type_pairs"] for r in p6_rows if r["group"] == "S4"))
    controls = {
        "composite_by_backtracking": True,
        "every_linear_verdict_has_certificate": all(
            ("solution" in v or "refutation" in v or "mod_p_refutation" in v)
            for r in rows if r["part"] == "local" for k, v in r["verdicts"].items() if isinstance(v, dict)),
        "relational_links_break_the_loop_rule": relational_breaks > 0,
        "level2_Q_accepts_some_impossible_instance": local.get("level2_Q_fooled", 0) > 0,
    }
    result = {
        "experiment_id": "HOLES-COHOMOLOGY-20261019-001A-E001",
        "predictions": {"P1": p1, "P2": p2, "P3": p3, "P4": p4, "P5": p5, "P6": p6},
        "signal": all((p1, p2, p3, p4, p5, p6)) and all(controls.values()),
        "controls": controls,
        "group": {f"{g} on {n}": {"b1": r["b1"], "allowed": r["allowed"], "patterns": r["patterns"],
                                  "fraction": r["allowed_fraction"]}
                  for (n, g), r in group.items()},
        "random_links": {"assignments": random_total, "mismatched_patterns": random_mismatches},
        "relational_control_assignments_broken": relational_breaks,
        "selectors": selectors,
        "complexes": {"counts_by_vertices": complex_counts, "mismatches": complex_mismatches},
        "size_bound": bound,
        "local": local,
        "p6": {f"{r['group']} on {r['graph']}": {"type_pairs": r["p6_type_pairs"],
                                                  "mixed": len(r["p6_mixed_type_pairs"])} for r in p6_rows},
        "wall_seconds": round(time.time() - started, 1),
    }
    with (ARTIFACT / "raw_rows.jsonl").open("w") as handle:
        for row in rows:
            handle.write(json.dumps(row, sort_keys=True) + "\n")
    (ARTIFACT / "result.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"predictions": result["predictions"], "controls": controls, "local": local}, indent=1))
    print("signal" if result["signal"] else "no signal")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
