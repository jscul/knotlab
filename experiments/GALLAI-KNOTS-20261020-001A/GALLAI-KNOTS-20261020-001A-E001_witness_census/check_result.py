#!/usr/bin/env python3
"""Independent check of GALLAI-KNOTS-20261020-001A-E001. It imports no producer code.

- Relations: each composite relation is rebuilt as the union, over the proper
  q-colourings c of W, of the leaf patterns giving every leaf of v a colour
  other than c(v). No list-colouring search is involved.
- Blocks: found by brute force over vertex subsets, as maximal sets inducing a
  2-connected subgraph or a bridge; each is then typed as a complete graph, an
  odd cycle or neither.
- Graph counts: connected graphs on at most 5 vertices are recounted with a
  full-permutation canonical form and compared with OEIS A001349
  (1, 1, 2, 6, 21, 112).
- Every verdict, allowed count and prediction flag is recomputed.
"""

from __future__ import annotations

import json
import sys
from itertools import combinations, permutations, product
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
ART = ROOT / "artifacts" / "GALLAI-KNOTS-20261020-001A" / HERE.name


def proper_colourings(k, edges, q):
    for c in product(range(q), repeat=k):
        if all(c[a] != c[b] for a, b in edges):
            yield c


def relation(k, edges, q, leaves_at):
    owners = [v for v in range(k) for _ in range(leaves_at[v])]
    bearing = sorted({v for v in owners})
    restrictions = {tuple(c[v] for v in bearing) for c in proper_colourings(k, edges, q)}
    index = {v: i for i, v in enumerate(bearing)}
    rel = set()
    for r in restrictions:
        choices = [[x for x in range(q) if x != r[index[v]]] for v in owners]
        rel.update(product(*choices))
    return rel


def knot(rel, n, q):
    full = q ** n
    if not rel or len(rel) == full:
        return False
    return all(len({t[:i] + t[i + 1:] for t in rel}) == q ** (n - 1) for i in range(n))


def induced_connected(S, adj):
    S = set(S)
    if not S:
        return False
    start = next(iter(S))
    seen, stack = {start}, [start]
    while stack:
        u = stack.pop()
        for w in adj[u]:
            if w in S and w not in seen:
                seen.add(w)
                stack.append(w)
    return seen == S


def two_connected(S, adj):
    if len(S) < 3:
        return False
    return induced_connected(S, adj) and all(induced_connected(set(S) - {v}, adj) for v in S)


def block_types(k, edges):
    adj = {v: set() for v in range(k)}
    for a, b in edges:
        adj[a].add(b)
        adj[b].add(a)
    candidates = [set(S) for m in range(3, k + 1) for S in combinations(range(k), m) if two_connected(S, adj)]
    maximal = [S for S in candidates if not any(S < T for T in candidates)]
    types = []
    covered = set()
    for S in maximal:
        es = [(a, b) for a, b in edges if a in S and b in S]
        covered.update(es)
        m = len(S)
        if len(es) == m * (m - 1) // 2:
            types.append(f"K{m}")
        elif len(es) == m and all(len(adj[v] & S) == 2 for v in S):
            types.append(f"C{m}")
        else:
            types.append("other")
    for e in edges:
        if tuple(e) not in covered:
            types.append("K2")
    return sorted(types)


def is_gallai(types):
    return all(t.startswith("K") or (t.startswith("C") and int(t[1:]) % 2 == 1) for t in types)


def count_graphs(max_k):
    counts = []
    for k in range(1, max_k + 1):
        pairs = list(combinations(range(k), 2))
        seen = set()
        for mask in range(1 << len(pairs)):
            edges = [pairs[i] for i in range(len(pairs)) if mask >> i & 1]
            adj = {v: set() for v in range(k)}
            for a, b in edges:
                adj[a].add(b)
                adj[b].add(a)
            if not induced_connected(set(range(k)), adj):
                continue
            key = min(tuple(sorted(tuple(sorted((p[a], p[b]))) for a, b in edges)) for p in permutations(range(k)))
            seen.add(key)
        counts.append(len(seen))
    return counts


def main() -> int:
    result = json.loads((ART / "result.json").read_text())
    rows = [json.loads(line) for line in (ART / "raw_rows.jsonl").read_text().splitlines()]
    problems = []
    counts = count_graphs(5)
    if counts != [1, 1, 2, 6, 21] or result["graphs"] - sum(counts) != 112:
        problems.append(f"graph counts {counts} and total {result['graphs']} differ from A001349")
    checked = 0
    for r in rows:
        if r["skipped"]:
            continue
        k, edges, q = r["k"], [tuple(e) for e in r["edges"]], r["q"]
        deg = [0] * k
        for a, b in edges:
            deg[a] += 1
            deg[b] += 1
        leaves_at = [max(q - d, 0) for d in deg]
        rel = relation(k, edges, q, leaves_at)
        n = sum(leaves_at)
        types = block_types(k, edges)
        if len(rel) != r["allowed"]:
            problems.append(f"allowed count differs for q={q} edges={r['edges']}")
        if knot(rel, n, q) != r["knot"]:
            problems.append(f"knot verdict differs for q={q} edges={r['edges']}")
        if is_gallai(types) != r["gallai"] or types != r["blocks"]:
            problems.append(f"block decomposition differs for q={q} edges={r['edges']}: {types} vs {r['blocks']}")
        checked += 1
    done = [r for r in rows if not r["skipped"]]
    within = [r for r in done if r["regime"] == "within"]
    outside = [r for r in done if r["regime"] == "outside"]
    p1 = all(r["knot"] == r["gallai"] for r in within)
    p2 = all(r["excluded"] == 0 for r in within if not r["gallai"])
    p4 = any(r["knot"] for r in outside)
    if (p1, p2, p4) != (result["predictions"]["P1"], result["predictions"]["P2"], result["predictions"]["P4"]):
        problems.append("prediction flags differ")
    report = {"rows_rechecked": checked, "graph_counts_k_le_5": counts, "P1": p1, "P2": p2, "P4": p4}
    status = "passed: recomputation agrees (V1, exploratory evidence only)" if not problems else "failed"
    text = json.dumps(report, indent=2, sort_keys=True) + "\n" + status + "\n" + "\n".join(problems) + "\n"
    (ART / "check_output.txt").write_text(text)
    print(text)
    return 0 if not problems else 1


if __name__ == "__main__":
    sys.exit(main())
