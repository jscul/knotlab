#!/usr/bin/env python3
"""Check DEEP-HOLES-20261020-001B-P001: the depth of a charge hole.

For every declared charge network this builds the certificates that the prose
proof describes and verifies them by substitution into equations rebuilt here:

1. Holes at a scope: the reduced homology H~_1 of the complex of partial
   assignments, for the 34 knots on three Boolean variables and for the
   sum-mod-3 knot, over F2, F3, F5 and Q. Theorem: rank |E| - 1 for Boolean
   knots (E the excluded set), so only atoms have no hole.
2. The charge-sum refutation at level 3 (the stars) over F_p for a Z_p
   network: summing every vertex's net flow counts each edge twice with
   opposite signs, leaving 0 = c(V).
3. The sweep refutation at the toggle width over Z (so over every ring): an
   optimal toggle path carries the flux across the current cut one vertex at a
   time; each step is an integer combination of marginal equations inside one
   bag of at most tgw edges, and the steps telescope to 0 = 1.
4. The Fourier solution one level below the toggle width, over every field in
   which p is invertible (Q, F3, F5 for Z2; Q, F2, F5 for Z3, through the
   extension by a cube root of unity and a trace):
   z[S,f] = p^(-|S|) * sum over cuts g inside S of h(g) * zeta^(-<f,g>),
   with h(delta u) = zeta^(-<c,u>) for vertex labellings u reachable from 0
   by cheap toggles, and 0 for other cuts.

Controls: a sweep certificate with one step removed, the charge-sum
certificate over a field of the wrong characteristic, and the Fourier
construction at the toggle width itself must all fail.

    python3 -B check.py          verify result.json against a fresh run
    python3 -B check.py --write  write result.json from a fresh run
"""

from __future__ import annotations

import heapq
import json
import sys
from collections import Counter, defaultdict
from fractions import Fraction
from itertools import combinations, product
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from knotlab.choice import two_loop_knots  # noqa: E402

CENSUS = ROOT / "artifacts/DEEP-HOLES-20261020-001A/DEEP-HOLES-20261020-001A-E001_charge_census"


# ---------------------------------------------------------------- networks and equations

class Network:
    """A Z_p charge network on a graph: edges oriented tail -> head, vertex v asks out-flow minus in-flow = c(v)."""

    def __init__(self, n, edges, p, charge):
        self.n, self.edges, self.p, self.charge = n, [tuple(e) for e in edges], p, charge
        self.stars = [[i for i, e in enumerate(self.edges) if v in e] for v in range(n)]
        self.cache = {}

    def outflow(self, v, values):
        return sum((x if self.edges[i][0] == v else -x) for i, x in zip(self.stars[v], values)) % self.p

    def local(self, bag):
        if bag not in self.cache:
            members = set(bag)
            inside = [v for v in range(self.n) if set(self.stars[v]) <= members]
            position = {e: k for k, e in enumerate(bag)}
            self.cache[bag] = [f for f in product(range(self.p), repeat=len(bag))
                               if all(self.outflow(v, [f[position[e]] for e in self.stars[v]]) == self.charge[v] % self.p
                                      for v in inside)]
        return self.cache[bag]

    def equation(self, label):
        if label == "n:":
            return {"v:|": 1}, 1
        big_text, e_text, f_text = label[2:].split("|")
        big = tuple(int(t) for t in big_text.split(","))
        e = int(e_text)
        f = tuple(int(t) for t in f_text.split(",")) if f_text else ()
        small = tuple(x for x in big if x != e)
        assert f in self.local(small), label
        at = big.index(e)
        form = Counter({var(small, f): 1})
        for g in self.local(big):
            if g[:at] + g[at + 1:] == f:
                form[var(big, g)] -= 1
        return dict(form), 0

    def labels(self, level):
        out = ["n:"]
        for k in range(1, level + 1):
            for big in combinations(range(len(self.edges)), k):
                for at, e in enumerate(big):
                    small = big[:at] + big[at + 1:]
                    out += [label(big, e, f) for f in self.local(small)]
        return out


def var(bag, f):
    return "v:" + ",".join(map(str, bag)) + "|" + ",".join(map(str, f))


def label(big, e, f):
    return f"m:{','.join(map(str, big))}|{e}|{','.join(map(str, f))}"


def marginal(net, small, big, g, scale, into):
    """Add scale times the equations whose sum reads z[small,g] - sum of z[big,f] over f extending g."""
    added = [e for e in big if e not in small]
    current = tuple(small)
    partial = [g]
    for e in added:
        bigger = tuple(sorted(current + (e,)))
        at = bigger.index(e)
        nxt = []
        for h in partial:
            into[label(bigger, e, h)] = into.get(label(bigger, e, h), 0) + scale
            for f in net.local(bigger):
                if f[:at] + f[at + 1:] == h:
                    nxt.append(f)
        current, partial = bigger, nxt


def combine(net, certificate):
    combined, constant = Counter(), 0
    for name, y in certificate.items():
        if y == 0:
            continue
        form, c = net.equation(name)
        for v, a in form.items():
            combined[v] += y * a
        constant += y * c
    return combined, constant


def refutes(net, certificate, modulus=None):
    combined, constant = combine(net, certificate)
    if modulus:
        return all(a % modulus == 0 for a in combined.values()) and constant % modulus != 0
    return all(a == 0 for a in combined.values()) and constant != 0


# ---------------------------------------------------------------- 1. holes at a scope

def rank(matrix, p):
    rows = [[Fraction(a) if p is None else a % p for a in row] for row in matrix]
    r = 0
    columns = len(rows[0]) if rows else 0
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
    pairs = [((i, a), (j, b)) for i, j in ((0, 1), (0, 2), (1, 2)) for a in range(q) for b in range(q)]
    index = {pair: k for k, pair in enumerate(pairs)}
    matrix = []
    for t in allowed:
        row = [0] * len(pairs)
        row[index[((1, t[1]), (2, t[2]))]] += 1
        row[index[((0, t[0]), (2, t[2]))]] -= 1
        row[index[((0, t[0]), (1, t[1]))]] += 1
        matrix.append(row)
    return len(pairs) - (3 * q - 1) - (rank(matrix, p) if matrix else 0)


def hole_checks():
    fields = {"F2": 2, "F3": 3, "F5": 5, "Q": None}
    boolean = all(scope_hole(2, [tuple(int(x) for x in r) for r in k.rows], p) == 8 - len(k.rows) - 1
                  for k in two_loop_knots() for p in fields.values())
    sum3 = [t for t in product(range(3), repeat=3) if (t[0] + t[1] - t[2]) % 3 == 1]
    sum3_ranks = {name: scope_hole(3, sum3, p) for name, p in fields.items()}
    return {"boolean_knots": len(two_loop_knots()), "boolean_rank_is_excluded_minus_one": boolean,
            "sum_mod_3_ranks": sum3_ranks}


# ---------------------------------------------------------------- 2. charge-sum refutation at level 3

def charge_sum_certificate(net):
    p = net.p
    cert = {"n:": sum(net.charge) % p}
    for v in range(net.n):
        bag = tuple(sorted(net.stars[v]))
        for e in bag:
            sign = 1 if net.edges[e][0] == v else -1
            for a in range(p):
                if a:
                    marginal(net, (e,), bag, (a,), sign * a, cert)
        marginal(net, (), bag, (), -net.charge[v], cert)
    return cert


# ---------------------------------------------------------------- 3. toggle width and the sweep refutation

def cut(net, U):
    return {i for i, (a, b) in enumerate(net.edges) if (a in U) != (b in U)}


def toggle_path(net, k):
    """A toggle path from the empty set to V with every step's cut-plus-star at most k edges, or None."""
    start, goal = frozenset(), frozenset(range(net.n))
    previous = {start: None}
    todo = [start]
    while todo:
        U = todo.pop()
        if U == goal:
            path = []
            while previous[U] is not None:
                path.append(U)
                U = previous[U]
            return [start] + path[::-1]
        for v in range(net.n):
            if len(cut(net, U) | set(net.stars[v])) <= k:
                W = U ^ {v}
                if W not in previous:
                    previous[W] = U
                    todo.append(W)
    return None


def toggle_width(net):
    k = 1
    while toggle_path(net, k) is None:
        k += 1
    return k


def flux(net, U, bag, f):
    value = dict(zip(bag, f))
    total = 0
    for e in cut(net, U):
        a, b = net.edges[e]
        total += value[e] if a in U else -value[e]
    return total % net.p


def sweep_certificate(net, path, skip=None):
    cert = {"n:": 1}
    t = 0
    for step, (U_prev, U) in enumerate(zip(path, path[1:])):
        (v,) = tuple(U ^ U_prev)
        s = 1 if v in U else -1
        bag = tuple(sorted(cut(net, U_prev) | set(net.stars[v])))
        after, before = tuple(sorted(cut(net, U))), tuple(sorted(cut(net, U_prev)))
        t_next = (t + s * net.charge[v]) % net.p
        if step == skip:
            t = t_next
            continue
        for g in net.local(after):
            if flux(net, U, after, g) == t_next:
                marginal(net, after, bag, g, 1, cert)
        for g in net.local(before):
            if flux(net, U_prev, before, g) == t:
                marginal(net, before, bag, g, -1, cert)
        t = t_next
    return cert


# ---------------------------------------------------------------- 4. the Fourier solution below the toggle width

class Ext:
    """Arithmetic in K[zeta] for a primitive cube root of unity zeta (zeta^2 = -1 - zeta), K = Q or F_l."""

    def __init__(self, modulus):
        self.m = modulus

    def norm(self, x):
        return x if self.m is None else (x[0] % self.m, x[1] % self.m)

    def add(self, x, y):
        return self.norm((x[0] + y[0], x[1] + y[1]))

    def mul(self, x, y):
        a, b = x
        c, d = y
        return self.norm((a * c - b * d, a * d + b * c - b * d))

    def power(self, k):
        out, z = (1, 0), (0, 1)
        for _ in range(k % 3):
            out = self.mul(out, z)
        return out


def reachable(net, k):
    """Vertex labellings u (mod constants fixed by u(0)) reachable from 0 by one-vertex changes of cost <= k."""
    p, n = net.p, net.n
    start = tuple([0] * n)
    seen = {start}
    todo = [start]
    while todo:
        u = todo.pop()
        support = {i for i, (a, b) in enumerate(net.edges) if u[a] != u[b]}
        for v in range(n):
            if len(support | set(net.stars[v])) > k:
                continue
            for value in range(p):
                if value != u[v]:
                    w = list(u)
                    w[v] = value
                    w = tuple(w)
                    if w not in seen:
                        seen.add(w)
                        todo.append(w)
    return seen


def fourier_solution(net, k, field):
    """The explicit level-k solution; None when the toggle relations are inconsistent (k at or above tgw)."""
    p = net.p
    labels_reached = reachable(net, k)
    h = {}
    for u in labels_reached:
        g = tuple((u[b] - u[a]) % p for a, b in net.edges)
        weight = sum(c * x for c, x in zip(net.charge, u)) % p
        if g in h and h[g] != weight:
            return None
        h[g] = weight
    cuts = defaultdict(list)
    for u in product(range(p), repeat=net.n):
        if u[0] != 0:
            continue
        g = tuple((u[b] - u[a]) % p for a, b in net.edges)
        cuts[frozenset(i for i, x in enumerate(g) if x)].append(g)
    modulus = {"Q": None, "F2": 2, "F3": 3, "F5": 5}[field]
    solution = {}
    for size in range(k + 1):
        for bag in combinations(range(len(net.edges)), size):
            inside = [g for support, gs in cuts.items() if support <= set(bag) for g in gs]
            for f in net.local(bag):
                if p == 2:
                    total = sum((-1) ** ((h[g] + sum(f[j] * g[e] for j, e in enumerate(bag))) % 2)
                                for g in inside if g in h)
                    value = Fraction(total, 2 ** size) if modulus is None else total * pow(2, -size, modulus) % modulus
                else:
                    ext = Ext(modulus)
                    acc = (0, 0)
                    for g in inside:
                        if g in h:
                            acc = ext.add(acc, ext.power(-(h[g] + sum(f[j] * g[e] for j, e in enumerate(bag)))))
                    trace = 2 * acc[0] - acc[1]
                    if modulus is None:
                        value = Fraction(trace, 2 * 3 ** size)
                    elif modulus == 2:
                        # over F4 = F2(zeta) the scale 3^(-|S|) is 1; the F2 solution is Tr(zeta * z) = a + b
                        a, b = acc
                        value = (a + b) % 2
                    else:
                        value = trace * pow(2 * 3 ** size, -1, modulus) % modulus
                if value:
                    solution[var(bag, f)] = value
    return solution


def solves(net, level, solution, modulus):
    for name in net.labels(level):
        form, c = net.equation(name)
        total = sum(a * solution.get(v, 0) for v, a in form.items()) - c
        if (total % modulus if modulus else total) != 0:
            return False
    return True


# ---------------------------------------------------------------- beyond the census: cubic graphs on 10 vertices

def cubic_graphs_on(n):
    """Connected cubic graphs on n vertices up to isomorphism (vertex 0 adjacent to 1, 2, 3; invariant buckets)."""
    found = []
    degree = [0] * n
    edges = [(0, 1), (0, 2), (0, 3)]
    degree[0] = 3
    for v in (1, 2, 3):
        degree[v] = 1

    def grow(v, low):
        if v < n and degree[v] == 3:
            while v < n and degree[v] == 3:
                v += 1
            low = v + 1
        if v == n:
            found.append(list(edges))
            return
        for w in range(max(low, v + 1), n):
            if degree[w] < 3 and (v, w) not in edges:
                edges.append((v, w))
                degree[v] += 1
                degree[w] += 1
                grow(v, w + 1)
                degree[v] -= 1
                degree[w] -= 1
                edges.pop()

    grow(1, 2)
    classes = []
    for es in found:
        adj = [set() for _ in range(n)]
        for a, b in es:
            adj[a].add(b)
            adj[b].add(a)
        seen, todo = {0}, [0]
        while todo:
            x = todo.pop()
            for y in adj[x] - seen:
                seen.add(y)
                todo.append(y)
        if len(seen) < n:
            continue
        key = (tuple(sorted(sum(1 for x, y in combinations(sorted(adj[v]), 2) if y in adj[x]) for v in range(n))),
               tuple(sorted(sum(len((adj[x] & adj[y]) - {v}) for x, y in combinations(sorted(adj[v]), 2)) for v in range(n))))
        if not any(k == key and isomorphic(n, adj, other) for k, other in classes):
            classes.append((key, adj))
    return [sorted((a, b) for a in range(n) for b in adj[a] if a < b) for _, adj in classes]


def isomorphic(n, adj1, adj2):
    mapping = {}

    def place(v):
        if v == n:
            return True
        for w in range(n):
            if w not in mapping.values() and all((u in adj1[v]) == (mapping[u] in adj2[w]) for u in mapping):
                mapping[v] = w
                if place(v + 1):
                    return True
                del mapping[v]
        return False

    return place(0)


def cutwidth(n, edges):
    width = {0: 0}
    for U in range(1, 1 << n):
        size = sum(1 for a, b in edges if ((U >> a) & 1) != ((U >> b) & 1))
        width[U] = max(size, min(width[U ^ (1 << v)] for v in range(n) if (U >> v) & 1))
    return width[(1 << n) - 1]


def monotone_toggle_width(net):
    best = {frozenset(): 0}
    for size in range(net.n):
        for U in [u for u in best if len(u) == size]:
            for v in range(net.n):
                if v not in U:
                    cost = max(best[U], len(cut(net, U) | set(net.stars[v])))
                    W = U | {v}
                    if cost < best.get(W, 99):
                        best[W] = cost
    return best[frozenset(range(net.n))]


def lazy_z(net, h, cuts, bag, f):
    inside = [g for support, gs in cuts.items() if support <= set(bag) for g in gs]
    total = sum((-1) ** ((h[g] + sum(f[j] * g[e] for j, e in enumerate(bag))) % 2) for g in inside if g in h)
    return Fraction(total, 2 ** len(bag))


def spot_check(net, k, samples, rng):
    """Random marginal equations of the level-k system, evaluated on the Fourier solution (p = 2, over Q)."""
    labels_reached = reachable(net, k)
    h = {}
    for u in labels_reached:
        g = tuple((u[b] - u[a]) % 2 for a, b in net.edges)
        weight = sum(c * x for c, x in zip(net.charge, u)) % 2
        if g in h and h[g] != weight:
            return False
        h[g] = weight
    cuts = defaultdict(list)
    for u in product(range(2), repeat=net.n):
        if u[0] == 0:
            g = tuple((u[b] - u[a]) % 2 for a, b in net.edges)
            cuts[frozenset(i for i, x in enumerate(g) if x)].append(g)
    if lazy_z(net, h, cuts, (), ()) != 1:
        return False
    for _ in range(samples):
        size = rng.randint(1, k)
        big = tuple(sorted(rng.sample(range(len(net.edges)), size)))
        e = rng.choice(big)
        small = tuple(x for x in big if x != e)
        options = net.local(small)
        f = rng.choice(options)
        at = big.index(e)
        rhs = sum(lazy_z(net, h, cuts, big, g) for g in net.local(big) if g[:at] + g[at + 1:] == f)
        if lazy_z(net, h, cuts, small, f) != rhs:
            return False
    return True


def line_graph_treewidth(edges):
    """Treewidth of the line graph (the network's variable graph) by dynamic programming over subsets."""
    m = len(edges)
    adjacency = [set() for _ in range(m)]
    for i, j in combinations(range(m), 2):
        if set(edges[i]) & set(edges[j]):
            adjacency[i].add(j)
            adjacency[j].add(i)

    def q(S, v):
        seen, todo, out = {v}, [v], set()
        while todo:
            x = todo.pop()
            for y in adjacency[x]:
                if y not in seen:
                    seen.add(y)
                    if (S >> y) & 1:
                        todo.append(y)
                    else:
                        out.add(y)
        return len(out)

    tw = {0: -1}
    for S in sorted(range(1, 1 << m), key=lambda s: bin(s).count("1")):
        tw[S] = min(max(tw[S ^ (1 << v)], q(S ^ (1 << v), v)) for v in range(m) if (S >> v) & 1)
    return tw[(1 << m) - 1]


def extended_roster():
    import random
    rng = random.Random(20261020)
    rows = []
    for edges in cubic_graphs_on(10):
        net = Network(10, edges, 2, [1] + [0] * 9)
        k = toggle_width(net)
        cert = sweep_certificate(net, toggle_path(net, k))
        largest = max(len(name[2:].split("|")[0].split(",")) for name in cert if name.startswith("m:"))
        row = {"edges": edges, "cutwidth": cutwidth(10, edges), "toggle_width": k,
               "line_graph_treewidth": line_graph_treewidth(edges),
               "monotone_toggle_width": monotone_toggle_width(net),
               "sweep_refutes": refutes(net, cert) and largest <= k,
               "fourier_consistent_below_and_spot_checked": spot_check(net, k - 1, 300, rng),
               "fourier_inconsistent_at_toggle_width": fourier_solution_consistent(net, k) is False}
        if row["line_graph_treewidth"] + 1 < k:
            solution = fourier_solution(net, k - 1, "Q")
            row["full_solution_below_toggle_width_verified"] = solution is not None and solves(net, k - 1, solution, None)
        rows.append(row)
    return rows


def fourier_solution_consistent(net, k):
    h = {}
    for u in reachable(net, k):
        g = tuple((u[b] - u[a]) % net.p for a, b in net.edges)
        weight = sum(c * x for c, x in zip(net.charge, u)) % net.p
        if g in h and h[g] != weight:
            return False
        h[g] = weight
    return True


# ---------------------------------------------------------------- roster and main

def roster():
    rows = [json.loads(line) for line in (CENSUS / "raw_rows.jsonl").read_text().splitlines()]
    graphs = {r["graph"]: (r["vertices"], [tuple(e) for e in r["edges"]]) for r in rows if r["part"] == "graph"}
    instances = []
    for r in rows:
        if r["part"] == "level":
            n, edges = graphs[r["graph"]]
            instances.append((f"{r['graph']}|{r['group']}|{r['placement']}", n, edges,
                              2 if r["group"] == "Z2" else 3, r["charge"]))
    return graphs, instances


def run() -> dict[str, object]:
    checks: dict[str, object] = {"holes": hole_checks()}
    graphs, instances = roster()
    census = json.loads((CENSUS / "result.json").read_text())
    tally = Counter()
    failures = []
    levels = {}
    for key, n, edges, p, charge in instances:
        net = Network(n, edges, p, charge)
        k = toggle_width(net)
        levels[key] = k
        if k != census["graphs"][key.split("|")[0]]["toggle_width"]:
            failures.append(f"{key}: toggle width")
        if not refutes(net, charge_sum_certificate(net), p):
            failures.append(f"{key}: charge-sum refutation at level 3")
        tally["charge_sum_refutations"] += 1
        path = toggle_path(net, k)
        cert = sweep_certificate(net, path)
        bags = {len(name[2:].split("|")[0].split(",")) for name in cert if name.startswith("m:")}
        if not refutes(net, cert) or max(bags) > k:
            failures.append(f"{key}: sweep refutation at level {k}")
        tally["sweep_refutations"] += 1
        fields = ("Q", "F3", "F5") if p == 2 else ("Q", "F2", "F5")
        for field in fields:
            solution = fourier_solution(net, k - 1, field)
            modulus = {"Q": None, "F2": 2, "F3": 3, "F5": 5}[field]
            if solution is None or not solves(net, k - 1, solution, modulus):
                failures.append(f"{key}: Fourier solution at level {k - 1} over {field}")
            tally["fourier_solutions"] += 1
        census_levels = census["levels"][key]
        for ring in fields:
            if census_levels.get(ring) is not None and census_levels[ring] != k:
                failures.append(f"{key}: census level over {ring}")
    # controls on the first instance of each group
    controls = {}
    for key, n, edges, p, charge in instances:
        if key not in ("K4|Z2|single", "K4|Z3|single"):
            continue
        net = Network(n, edges, p, charge)
        k = levels[key]
        path = toggle_path(net, k)
        controls[f"{key}: sweep with a step removed fails"] = not refutes(net, sweep_certificate(net, path, skip=len(path) // 2))
        wrong = 3 if p == 2 else 2
        controls[f"{key}: charge sum over the wrong characteristic fails"] = not refutes(net, charge_sum_certificate(net), wrong)
        controls[f"{key}: Fourier construction at the toggle width fails"] = fourier_solution(net, k, "Q") is None
    by_treewidth = defaultdict(set)
    for key, k in levels.items():
        if "|Z2|single" in key:
            by_treewidth[census["graphs"][key.split("|")[0]]["treewidth"]].add(k)
    checks["toggle_widths"] = {key: k for key, k in sorted(levels.items())}
    checks["levels_by_treewidth"] = {str(t): sorted(v) for t, v in sorted(by_treewidth.items())}
    checks["not_a_function_of_treewidth"] = any(len(v) > 1 for v in by_treewidth.values())
    checks["tally"] = dict(tally)
    checks["controls"] = controls
    extended = extended_roster()
    checks["cubic_graphs_on_10_vertices"] = {
        "graphs": len(extended),
        "sweep_refutes_at_toggle_width": all(r["sweep_refutes"] for r in extended),
        "fourier_consistent_below_and_spot_checked": all(r["fourier_consistent_below_and_spot_checked"] for r in extended),
        "fourier_inconsistent_at_toggle_width": all(r["fourier_inconsistent_at_toggle_width"] for r in extended),
        "toggle_width_equals_cutwidth_plus_one": all(r["toggle_width"] == r["cutwidth"] + 1 for r in extended),
        "toggle_width_equals_monotone": all(r["toggle_width"] == r["monotone_toggle_width"] for r in extended),
        "toggle_widths": sorted(r["toggle_width"] for r in extended),
        "graphs_where_depth_exceeds_line_graph_treewidth_plus_one": [
            {"edges": r["edges"], "line_graph_treewidth": r["line_graph_treewidth"], "toggle_width": r["toggle_width"],
             "full_solution_below_toggle_width_verified": r["full_solution_below_toggle_width_verified"]}
            for r in extended if "full_solution_below_toggle_width_verified" in r],
    }
    if not all(g["full_solution_below_toggle_width_verified"]
               for g in checks["cubic_graphs_on_10_vertices"]["graphs_where_depth_exceeds_line_graph_treewidth_plus_one"]):
        failures.append("10-vertex graphs: full solution below the toggle width")
    for name, ok in checks["cubic_graphs_on_10_vertices"].items():
        if ok is False:
            failures.append(f"10-vertex graphs: {name}")
    holes_ok = checks["holes"]["boolean_rank_is_excluded_minus_one"] and all(v > 0 for v in checks["holes"]["sum_mod_3_ranks"].values())
    failed = failures + [name for name, ok in controls.items() if not ok]
    if not holes_ok:
        failed.append("hole ranks")
    if not checks["not_a_function_of_treewidth"]:
        failed.append("levels are a function of treewidth")
    return {"checks": checks, "failures": failed}


def main() -> int:
    outcome = run()
    manifest = json.loads((HERE / "manifest.json").read_text())
    result = {
        "schema_version": 3, "artifact_id": manifest["artifact_id"], "kind": "proof", "ticket": manifest["ticket"],
        "proof": manifest["proof"], "status": "passed" if not outcome["failures"] else "failed",
        "claim": manifest["claim"], "foundation_contract": manifest["foundation_contract"],
        "semantic_domains": manifest["semantic_domains"], "evidence_modes": manifest["evidence_modes"],
        "thesis_alignment": manifest["thesis_alignment"], "safe_conclusions": manifest["safe_to_conclude"],
        "checks": outcome["checks"], "failures": outcome["failures"],
    }
    result = json.loads(json.dumps(result))
    path = HERE / "result.json"
    text = json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    if "--write" in sys.argv[1:]:
        path.write_text(text)
    elif not path.exists() or json.loads(path.read_text()) != result:
        print("result.json does not match a fresh run; rerun with --write after review")
        return 1
    tally = outcome["checks"]["tally"]
    print(f"{result['status']}: {tally.get('sweep_refutations', 0)} networks; every certificate verified"
          if result["status"] == "passed" else f"failed: {outcome['failures'][:10]}")
    return 0 if result["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
