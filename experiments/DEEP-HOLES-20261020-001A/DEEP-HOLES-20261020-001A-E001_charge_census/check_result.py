#!/usr/bin/env python3
"""Independent check of DEEP-HOLES-20261020-001A-E001; imports no producer code.

- Graphs: each recorded graph is cubic and connected, the classes are pairwise
  non-isomorphic (canonical forms by brute force over vertex orders), and the
  counts are 1, 2 and 5 on 4, 6 and 8 vertices (OEIS A002851).
- Parameters: treewidth and cutwidth by brute force over vertex orders on the
  graphs, toggle widths by threshold search (breadth first at each width), the
  separator number by brute force; the line graph's treewidth by a separate
  subset recursion.
- Holes: Boolean scope ranks from the Euler characteristic and the one
  2-cycle of the full join (no linear algebra); the sum-mod-3 rank by
  fraction-free elimination.
- Levels: every stored certificate is verified by substitution into
  equations rebuilt here from their names: the refutation at the reported
  level cancels every variable and leaves a nonzero constant (mod p for F_p),
  and the solution one level below satisfies every equation of that level.
- Predictions P1-P6 and the controls are re-derived from the recomputed values.
"""

from __future__ import annotations

import gzip
import json
from collections import Counter, defaultdict
from fractions import Fraction
from itertools import combinations, permutations, product
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
ARTIFACT = ROOT / "artifacts" / "DEEP-HOLES-20261020-001A" / HERE.name
PRIME = {"F2": 2, "F3": 3, "F5": 5, "Q": None}


def adjacency_of(n, edges):
    adj = [set() for _ in range(n)]
    for a, b in edges:
        adj[a].add(b)
        adj[b].add(a)
    return adj


def canonical(n, edges):
    best = None
    for order in permutations(range(n)):
        relabelled = tuple(sorted(tuple(sorted((order[a], order[b]))) for a, b in edges))
        if best is None or relabelled < best:
            best = relabelled
    return best


def elimination_width(n, adj, order):
    graph = [set(s) for s in adj]
    width = 0
    gone = set()
    for v in order:
        later = graph[v] - gone
        width = max(width, len(later))
        for x, y in combinations(later, 2):
            graph[x].add(y)
            graph[y].add(x)
        gone.add(v)
    return width


def treewidth_brute(n, adj):
    return min(elimination_width(n, adj, order) for order in permutations(range(n)))


def treewidth_subsets(n, adj):
    """Treewidth as min over orders, by memoized recursion on the set of vertices still present."""
    memo = {}

    def degree_after(eliminated, v):
        # vertices outside eliminated+v reachable from v through eliminated vertices
        seen, todo, out = {v}, [v], set()
        while todo:
            x = todo.pop()
            for y in adj[x]:
                if y in seen:
                    continue
                seen.add(y)
                if y in eliminated:
                    todo.append(y)
                else:
                    out.add(y)
        return len(out)

    def solve(eliminated):
        if len(eliminated) == n:
            return -1
        if eliminated in memo:
            return memo[eliminated]
        best = min(max(degree_after(eliminated, v), solve(eliminated | {v}))
                   for v in range(n) if v not in eliminated)
        memo[eliminated] = best
        return best

    return solve(frozenset())


def cut_size(edges, U):
    return sum(1 for a, b in edges if (a in U) != (b in U))


def cutwidth_brute(n, edges):
    return min(max(cut_size(edges, set(order[:i])) for i in range(1, n)) for order in permutations(range(n)))


def toggle_width_threshold(n, edges, monotone=False):
    stars = [{i for i, e in enumerate(edges) if v in e} for v in range(n)]
    for k in range(1, len(edges) + 1):
        start, goal = frozenset(), frozenset(range(n))
        seen, todo = {start}, [start]
        while todo:
            U = todo.pop()
            cut = {i for i, (a, b) in enumerate(edges) if (a in U) != (b in U)}
            for v in range(n):
                if monotone and v in U:
                    continue
                if len(cut | stars[v]) <= k:
                    W = U ^ {v}
                    if W not in seen:
                        seen.add(W)
                        todo.append(W)
        if goal in seen:
            return k
    return None


def separator_brute(n, edges):
    best = None
    for mask in range(1 << len(edges)):
        size = bin(mask).count("1")
        if best is not None and size >= best:
            continue
        kept = [e for i, e in enumerate(edges) if not (mask >> i) & 1]
        adj = adjacency_of(n, kept)
        seen, largest = set(), 0
        for s in range(n):
            if s in seen:
                continue
            comp, todo = {s}, [s]
            while todo:
                x = todo.pop()
                for y in adj[x] - comp:
                    comp.add(y)
                    todo.append(y)
            seen |= comp
            largest = max(largest, len(comp))
        if 2 * largest <= n:
            best = size
    return best


def rank_bareiss(matrix):
    """Rank over Q by fraction-free elimination."""
    rows = [list(r) for r in matrix]
    rank, prev = 0, 1
    columns = len(rows[0]) if rows else 0
    for c in range(columns):
        pivot = next((i for i in range(rank, len(rows)) if rows[i][c]), None)
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        for i in range(rank + 1, len(rows)):
            rows[i] = [(rows[rank][c] * rows[i][j] - rows[i][c] * rows[rank][j]) // prev for j in range(columns)]
        prev = rows[rank][c]
        rank += 1
    return rank


def rank_mod(matrix, p):
    rows = [[a % p for a in r] for r in matrix]
    rank = 0
    columns = len(rows[0]) if rows else 0
    for c in range(columns):
        pivot = next((i for i in range(rank, len(rows)) if rows[i][c]), None)
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        inv = pow(rows[rank][c], p - 2, p)
        rows[rank] = [a * inv % p for a in rows[rank]]
        for i in range(len(rows)):
            if i != rank and rows[i][c]:
                f = rows[i][c]
                rows[i] = [(a - f * b) % p for a, b in zip(rows[i], rows[rank])]
        rank += 1
    return rank


def sum3_rank(ring):
    allowed = [t for t in product(range(3), repeat=3) if (t[0] + t[1] - t[2]) % 3 == 1]
    pairs = [((i, a), (j, b)) for i, j in ((0, 1), (0, 2), (1, 2)) for a in range(3) for b in range(3)]
    index = {pair: k for k, pair in enumerate(pairs)}
    matrix = []
    for t in allowed:
        row = [0] * len(pairs)
        row[index[((1, t[1]), (2, t[2]))]] += 1
        row[index[((0, t[0]), (2, t[2]))]] -= 1
        row[index[((0, t[0]), (1, t[1]))]] += 1
        matrix.append(row)
    r = rank_bareiss(matrix) if ring == "Q" else rank_mod(matrix, PRIME[ring])
    return len(pairs) - (9 - 1) - r


class Instance:
    def __init__(self, n, edges, group, charge):
        self.n, self.edges, self.group, self.charge = n, [tuple(e) for e in edges], group, charge
        self.q = {"Z2": 2, "Z3": 3, "NAE": 2}[group]
        self.stars = [[i for i, e in enumerate(self.edges) if v in e] for v in range(n)]
        self.cache = {}

    def ok(self, v, values):
        if self.group == "Z2":
            return sum(values) % 2 == self.charge[v] % 2
        if self.group == "Z3":
            total = 0
            for i, x in zip(self.stars[v], values):
                total += x if self.edges[i][0] == v else -x
            return total % 3 == self.charge[v] % 3
        return len(set(values)) > 1

    def local(self, bag):
        if bag not in self.cache:
            members = set(bag)
            inside = [v for v in range(self.n) if set(self.stars[v]) <= members]
            position = {e: k for k, e in enumerate(bag)}
            self.cache[bag] = [f for f in product(range(self.q), repeat=len(bag))
                               if all(self.ok(v, [f[position[e]] for e in self.stars[v]]) for v in inside)]
        return self.cache[bag]

    def equation(self, label):
        if label == "n:":
            return {"v:|": 1}, 1
        big_text, e_text, f_text = label[2:].split("|")
        big = tuple(int(t) for t in big_text.split(","))
        e = int(e_text)
        f = tuple(int(t) for t in f_text.split(",")) if f_text else ()
        small = tuple(x for x in big if x != e)
        if f not in self.local(small):
            raise ValueError("equation for an assignment that is not a local solution")
        at = big.index(e)
        form = Counter({"v:" + ",".join(map(str, small)) + "|" + ",".join(map(str, f)): 1})
        for g in self.local(big):
            if g[:at] + g[at + 1:] == f:
                form["v:" + ",".join(map(str, big)) + "|" + ",".join(map(str, g))] -= 1
        return {k: v for k, v in form.items() if v}, 0

    def labels(self, level):
        out = ["n:"]
        for k in range(1, level + 1):
            for big in combinations(range(len(self.edges)), k):
                for at, e in enumerate(big):
                    small = big[:at] + big[at + 1:]
                    out += [f"m:{','.join(map(str, big))}|{e}|{','.join(map(str, f))}" for f in self.local(small)]
        return out


def value(text, ring):
    return Fraction(text) if ring == "Q" else int(text)


def verify_solution(inst, level, solution, ring):
    p = PRIME[ring]
    x = {k: value(v, ring) for k, v in solution.items()}
    for label in inst.labels(level):
        form, c = inst.equation(label)
        total = sum(a * x.get(v, 0) for v, a in form.items()) - c
        if (total % p if p else total) != 0:
            return False
    return True


def verify_refutation(inst, certificate, ring):
    p = PRIME[ring]
    combined, constant = Counter(), 0
    for label, y in certificate["refutation"].items():
        coefficient = value(y, ring)
        form, c = inst.equation(label)
        for v, a in form.items():
            combined[v] += coefficient * a
        constant += coefficient * c
    if p:
        return all(a % p == 0 for a in combined.values()) and constant % p != 0
    return all(a == 0 for a in combined.values()) and constant != 0


def main() -> int:
    result = json.loads((ARTIFACT / "result.json").read_text())
    rows = [json.loads(line) for line in (ARTIFACT / "raw_rows.jsonl").read_text().splitlines()]
    with gzip.open(ARTIFACT / "certificates.json.gz", "rt") as handle:
        certificates = json.load(handle)
    failures: list[str] = []

    def expect(condition, message):
        if not condition:
            failures.append(message)

    graphs = {r["graph"]: (r["vertices"], [tuple(e) for e in r["edges"]]) for r in rows if r["part"] == "graph"}
    counts = Counter(n for n, _ in graphs.values())
    expect(dict(counts) == {4: 1, 6: 2, 8: 5}, "graph counts 1, 2, 5")
    forms = set()
    params = {}
    for g, (n, edges) in graphs.items():
        adj = adjacency_of(n, edges)
        expect(all(len(a) == 3 for a in adj), f"{g}: cubic")
        forms.add(canonical(n, edges))
        line_adj = [set() for _ in edges]
        for i, j in combinations(range(len(edges)), 2):
            if set(edges[i]) & set(edges[j]):
                line_adj[i].add(j)
                line_adj[j].add(i)
        params[g] = {"treewidth": treewidth_brute(n, adj), "line_graph_treewidth": treewidth_subsets(len(edges), line_adj),
                     "cutwidth": cutwidth_brute(n, edges), "toggle_width": toggle_width_threshold(n, edges),
                     "toggle_width_monotone": toggle_width_threshold(n, edges, monotone=True),
                     "separator_number": separator_brute(n, edges)}
        for key, v in params[g].items():
            expect(result["graphs"][g][key] == v, f"{g}: {key} {result['graphs'][g][key]} vs {v}")
    expect(len(forms) == len(graphs), "graphs pairwise non-isomorphic")

    knot_row = next(r for r in rows if r["part"] == "knot_holes")
    for entry in knot_row["ranks"]:
        excluded = entry["excluded"]
        triangles = 8 - excluded
        b2 = 1 if excluded == 0 else 0
        expected = 1 - 6 + 12 - (triangles - b2)
        expect(entry["rank"] == expected, f"knot {entry['knot']} {entry['ring']}: hole rank")
    for ring, rank in knot_row["sum_mod_3_ranks"].items():
        expect(rank == sum3_rank(ring), f"sum mod 3 hole rank over {ring}")

    for r in (r for r in rows if r["part"] == "nae"):
        n, edges = graphs[r["graph"]]
        stars = [[i for i, e in enumerate(edges) if v in e] for v in range(n)]
        possible = any(all(len({x[i] for i in s}) > 1 for s in stars) for x in product((0, 1), repeat=len(edges)))
        expect(possible == r["possible"], f"{r['graph']}: NAE possible")

    verified = Counter()
    level_rows = [r for r in rows if r["part"] in ("level", "control_even")]
    for r in level_rows:
        n, edges = graphs[r["graph"]]
        group = r.get("group", "Z2")
        inst = Instance(n, edges, group, r["charge"])
        key = f"{r['graph']}|{group}|{r.get('placement', 'even')}"
        for ring, outcome in r["levels"].items():
            if ring == "Z":
                matched = "F2" if group == "Z2" else "F3"
                cert = certificates.get(f"{key}|{matched}|3")
                ok = outcome["level"] == 3 and cert is not None and not cert["feasible"] and \
                    verify_refutation(inst, cert, matched)
                expect(ok, f"{key} Z: refutation at level 3 through {matched}")
                verified["Z"] += ok
                continue
            level = outcome.get("level")
            if level is not None:
                cert = certificates.get(f"{key}|{ring}|{level}")
                expect(cert is not None and not cert["feasible"] and verify_refutation(inst, cert, ring),
                       f"{key} {ring}: refutation at {level}")
                verified["refutations"] += 1
                if level > 3:
                    below = certificates.get(f"{key}|{ring}|{level - 1}")
                    expect(below is not None and below["feasible"] and verify_solution(inst, level - 1, below["solution"], ring),
                           f"{key} {ring}: solution at {level - 1}")
                    verified["solutions"] += 1
            elif outcome.get("never_refuted"):
                top = outcome["last_feasible_level"]
                cert = certificates.get(f"{key}|{ring}|{top}")
                expect(cert is not None and cert["feasible"] and verify_solution(inst, top, cert["solution"], ring),
                       f"{key} {ring}: solution at {top}")
                verified["solutions"] += 1

    results = [r for r in rows if r["part"] == "level"]
    matched = {"Z2": ("F2", "Z"), "Z3": ("F3", "Z")}
    mismatched = {"Z2": ("F3", "F5", "Q"), "Z3": ("F2", "F5", "Q")}
    p1 = all(r["levels"][ring]["level"] == 3 for r in results for ring in matched[r["group"]])
    resolved = [(r, ring) for r in results for ring in mismatched[r["group"]]
                if ring in r["levels"] and r["levels"][ring]["resolved"]]
    p2 = bool(resolved) and all(r["levels"][ring]["level"] == params[r["graph"]]["toggle_width"] for r, ring in resolved)
    p3 = knot_row["rank_is_excluded_minus_one"] and all(v > 0 for v in knot_row["sum_mod_3_ranks"].values()) and \
        all(r.get("hole_bound") == 2 for r in rows if r["part"] in ("level", "nae"))
    by_tw = defaultdict(set)
    for r in results:
        if r["group"] == "Z2" and r["placement"] == "single" and r["levels"]["F3"]["resolved"]:
            by_tw[params[r["graph"]]["treewidth"]].add(r["levels"]["F3"]["level"])
    p4 = any(len(v) > 1 for v in by_tw.values())
    by_graph = defaultdict(set)
    for r, ring in resolved:
        by_graph[(r["graph"], r["group"], ring)].add(r["levels"][ring]["level"])
    p5 = all(len(v) == 1 for v in by_graph.values())
    p6 = all(r["possible"] for r in rows if r["part"] == "nae")
    recomputed = {"P1": p1, "P2": p2, "P3": p3, "P4": p4, "P5": p5, "P6": p6}
    expect(recomputed == result["predictions"], f"predictions {recomputed} vs {result['predictions']}")
    print(json.dumps({"verified": dict(verified), "predictions": recomputed,
                      "levels_by_treewidth": {str(k): sorted(v) for k, v in by_tw.items()}}, indent=1))
    print(f"{'passed' if not failures else 'FAILED'}: recomputation agrees (V1, exploratory evidence only)")
    for failure in failures[:30]:
        print("  failed:", failure)
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
