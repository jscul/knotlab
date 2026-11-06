#!/usr/bin/env python3
"""Independent check of CUTWIDTH-DEPTH-20261020-001A-E001; imports no producer code.

- Widths recomputed by separate algorithms: cutwidth by memoized recursion on
  the set of placed vertices; toggle width, its monotone version and the cut
  game by threshold search (breadth first at each width).
- The 12-vertex cubic classes: each connected and cubic, pairwise
  non-isomorphic by canonical breadth-first codes (minimum over every start
  vertex and every order of newly reached neighbours), 85 of them; the small
  graphs: pairwise non-isomorphic by minimum relabelling over all vertex
  orders, numbering 2, 6, 21 and 112 (OEIS A001349).
- Depth certificates: every stored sweep refutation re-verified by
  substitution with bags of at most cutwidth + 1 edges; at level cutwidth, no
  toggle path of that cost reaches V, and 100 fresh random equations hold on
  the Fourier solution.
- Predictions P1-P5 re-derived.
"""

from __future__ import annotations

import gzip
import json
import random
from collections import Counter
from fractions import Fraction
from functools import lru_cache
from itertools import permutations, product
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
ARTIFACT = ROOT / "artifacts" / "CUTWIDTH-DEPTH-20261020-001A" / HERE.name


def adjacency(n, edges):
    adj = [set() for _ in range(n)]
    for a, b in edges:
        adj[a].add(b)
        adj[b].add(a)
    return adj


def cut_size(edges, members):
    return sum(1 for a, b in edges if (a in members) != (b in members))


def cutwidth(n, edges):
    @lru_cache(maxsize=None)
    def best(placed):
        if len(placed) == n:
            return 0
        return min(max(cut_size(edges, placed | {v}), best(placed | {v})) for v in range(n) if v not in placed)

    return best(frozenset())


def game(n, edges, kind, monotone=False):
    stars = [{i for i, e in enumerate(edges) if v in e} for v in range(n)]
    for k in range(0, len(edges) + 1):
        start, goal = frozenset(), frozenset(range(n))
        seen, todo = {start}, [start]
        while todo:
            U = todo.pop()
            cut = {i for i, (a, b) in enumerate(edges) if (a in U) != (b in U)}
            for v in range(n):
                if monotone and v in U:
                    continue
                W = U ^ {v}
                cost = len(cut | stars[v]) if kind == "toggle" else cut_size(edges, W)
                if cost <= k and W not in seen:
                    seen.add(W)
                    todo.append(W)
        if goal in seen:
            return k
    return None


def bfs_code(n, adj):
    best = None
    for start in range(n):
        stack = [({start: 0}, [start], 0)]
        while stack:
            labels, queue, head = stack.pop()
            if head == len(queue):
                if len(labels) == n:
                    code = tuple(sorted(tuple(sorted((labels[a], labels[b]))) for a in range(n) for b in adj[a] if a < b))
                    if best is None or code < best:
                        best = code
                continue
            x = queue[head]
            fresh = sorted(y for y in adj[x] if y not in labels)
            for order in permutations(fresh):
                new_labels = dict(labels)
                for y in order:
                    new_labels[y] = len(new_labels)
                stack.append((new_labels, queue + list(order), head + 1))
    return best


def min_relabel(n, edges):
    return min(tuple(sorted(tuple(sorted((p[a], p[b]))) for a, b in edges)) for p in permutations(range(n)))


class Network:
    def __init__(self, n, edges, charge):
        self.n, self.edges, self.charge = n, [tuple(e) for e in edges], charge
        self.stars = [[i for i, e in enumerate(self.edges) if v in e] for v in range(n)]
        self.cache = {}

    def local(self, bag):
        if bag not in self.cache:
            members = set(bag)
            inside = [v for v in range(self.n) if set(self.stars[v]) <= members]
            position = {e: k for k, e in enumerate(bag)}
            self.cache[bag] = [f for f in product((0, 1), repeat=len(bag))
                               if all(sum(f[position[e]] for e in self.stars[v]) % 2 == self.charge[v] for v in inside)]
        return self.cache[bag]

    def equation(self, name):
        if name == "n:":
            return {"v:|": 1}, 1
        big_text, e_text, f_text = name[2:].split("|")
        big = tuple(int(t) for t in big_text.split(","))
        e = int(e_text)
        f = tuple(int(t) for t in f_text.split(",")) if f_text else ()
        small = tuple(x for x in big if x != e)
        if f not in self.local(small):
            raise ValueError("not a local solution")
        at = big.index(e)
        form = Counter({"v:" + ",".join(map(str, small)) + "|" + ",".join(map(str, f)): 1})
        for g in self.local(big):
            if g[:at] + g[at + 1:] == f:
                form["v:" + ",".join(map(str, big)) + "|" + ",".join(map(str, g))] -= 1
        return form, 0


def refutes(net, cert):
    combined, constant = Counter(), 0
    for name, y in cert.items():
        if y:
            form, c = net.equation(name)
            for v, a in form.items():
                combined[v] += y * a
            constant += y * c
    return all(a == 0 for a in combined.values()) and constant != 0


def spot_check(net, k, samples, rng):
    n = net.n
    reach, todo = {frozenset()}, [frozenset()]
    while todo:
        U = todo.pop()
        cut = {i for i, (a, b) in enumerate(net.edges) if (a in U) != (b in U)}
        for v in range(n):
            if len(cut | set(net.stars[v])) <= k and (U ^ {v}) not in reach:
                reach.add(U ^ {v})
                todo.append(U ^ {v})
    if frozenset(range(n)) in reach:
        return False
    h = {}
    for U in reach:
        h[frozenset(i for i, (a, b) in enumerate(net.edges) if (a in U) != (b in U))] = (-1) ** (sum(net.charge[v] for v in U) % 2)
    cuts = {frozenset(i for i, (a, b) in enumerate(net.edges) if (a in U) != (b in U))
            for U in (frozenset(v for v in range(n - 1) if (m >> v) & 1) for m in range(1 << (n - 1)))}

    def z(bag, f):
        members = set(bag)
        total = 0
        for gamma in cuts:
            if gamma <= members and gamma in h:
                total += h[gamma] * (-1) ** (sum(f[j] for j, e in enumerate(bag) if e in gamma) % 2)
        return Fraction(total, 2 ** len(bag))

    if z((), ()) != 1:
        return False
    for _ in range(samples):
        size = rng.randint(1, k)
        big = tuple(sorted(rng.sample(range(len(net.edges)), size)))
        e = rng.choice(big)
        small = tuple(x for x in big if x != e)
        f = rng.choice(net.local(small))
        at = big.index(e)
        if z(small, f) != sum(z(big, g) for g in net.local(big) if g[:at] + g[at + 1:] == f):
            return False
    return True


def main() -> int:
    result = json.loads((ARTIFACT / "result.json").read_text())
    rows = [json.loads(line) for line in (ARTIFACT / "raw_rows.jsonl").read_text().splitlines()]
    with gzip.open(ARTIFACT / "certificates.json.gz", "rt") as handle:
        certificates = json.load(handle)
    failures = []

    def expect(condition, message):
        if not condition:
            failures.append(message)

    graphs = [r for r in rows if r["part"] == "graph"]
    for r in graphs:
        n, edges = r["vertices"], [tuple(e) for e in r["edges"]]
        recomputed = {"cutwidth": cutwidth(n, edges), "toggle_width": game(n, edges, "toggle"),
                      "monotone_toggle_width": game(n, edges, "toggle", monotone=True),
                      "cut_game": game(n, edges, "cut"), "max_degree": max(len(a) for a in adjacency(n, edges))}
        for key, value in recomputed.items():
            expect(r[key] == value, f"{r['family']} n={n} {edges}: {key} {r[key]} vs {value}")
        r.update(recomputed)

    twelve = [r for r in graphs if r["family"] == "cubic" and r["vertices"] == 12]
    codes = set()
    for r in twelve:
        adj = adjacency(12, [tuple(e) for e in r["edges"]])
        expect(all(len(a) == 3 for a in adj), "12-vertex graph not cubic")
        codes.add(bfs_code(12, adj))
    expect(len(twelve) == 85 and len(codes) == 85, f"12-vertex cubic classes: {len(twelve)} rows, {len(codes)} distinct")
    for n, published in ((3, 2), (4, 6), (5, 21), (6, 112)):
        small = [r for r in graphs if r["family"] == "small" and r["vertices"] == n]
        forms = {min_relabel(n, [tuple(e) for e in r["edges"]]) for r in small}
        expect(len(small) == published == len(forms), f"connected graphs on {n} vertices: {len(small)}, {len(forms)} distinct")

    rng = random.Random(7)
    verified = 0
    for key, item in certificates.items():
        index = int(key.split("|")[1])
        row = next(r for r in twelve if r.get("sample_index") == index)
        net = Network(12, item["edges"], [1] + [0] * 11)
        cert = {k: int(v) for k, v in item["sweep"].items()}
        largest = max(len(k[2:].split("|")[0].split(",")) for k in cert if k.startswith("m:"))
        expect(refutes(net, cert) and largest <= row["cutwidth"] + 1, f"cubic12 {index}: sweep refutation")
        expect(spot_check(net, row["cutwidth"], 100, rng), f"cubic12 {index}: Fourier consistency at cutwidth")
        verified += 1

    usable = [r for r in graphs if r["vertices"] >= 3]
    sub = [r for r in usable if r["max_degree"] <= 3]
    recomputed = {
        "P1": all(r["toggle_width"] == r["monotone_toggle_width"] == r["cutwidth"] + 1 for r in sub),
        "P2": all(r["cutwidth"] + 1 <= r["toggle_width"] <= r["monotone_toggle_width"] <= r["cutwidth"] + r["max_degree"] // 2
                  for r in usable),
        "P3": all(r["cut_game"] == r["cutwidth"] for r in usable),
        "P4": all(r["toggle_width"] == r["monotone_toggle_width"] for r in usable),
        "P5": len(twelve) == 85 and verified == 85 and not any("cubic12" in f for f in failures),
    }
    expect(recomputed == result["predictions"], f"predictions {recomputed} vs {result['predictions']}")
    print(json.dumps({"graphs": len(graphs), "max_degree_at_most_3": len(sub), "cubic_12_distinct": len(codes),
                      "certificates_verified": verified, "predictions": recomputed}, indent=1))
    print(f"{'passed' if not failures else 'FAILED'}: recomputation agrees (V1, exploratory evidence only)")
    for failure in failures[:30]:
        print("  failed:", failure)
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
