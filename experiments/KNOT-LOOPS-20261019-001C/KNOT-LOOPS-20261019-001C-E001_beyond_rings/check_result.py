#!/usr/bin/env python3
"""Independent check of KNOT-LOOPS-20261019-001C-E001; imports no producer code.

- Network composites by backtracking over witness assignments (the producer uses
  bitsets): every placement on C4, K4 and K23, every third placement on the
  prism, the 3x3 grid and K33, compared with the raw rows.
- Many-valued rings recounted by dynamic programming over permutation products
  (the producer enumerates patterns), and the knot condition rechecked.
- Sampled three-valued knots: bits recomputed by brute force for k <= 4 on the
  first 200 samples, after redrawing the samples from the declared seed.
- Post hoc, labelled as such: excluded network patterns split into those an
  odd cycle of permutation edges explains and those it does not (memory that
  is not group holonomy).
"""

from __future__ import annotations

import json
import math
import random
from collections import Counter
from itertools import combinations, permutations, product
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
ARTIFACT = ROOT / "artifacts" / "KNOT-LOOPS-20261019-001C" / HERE.name
GRAPHS = {
    "C4": (4, [(0, 1), (1, 2), (2, 3), (0, 3)]),
    "K4": (4, list(combinations(range(4), 2))),
    "K23": (5, [(0, 2), (0, 3), (0, 4), (1, 2), (1, 3), (1, 4)]),
    "prism": (6, [(0, 1), (1, 2), (0, 2), (3, 4), (4, 5), (3, 5), (0, 3), (1, 4), (2, 5)]),
    "grid3": (9, [(r * 3 + c, r * 3 + c + 1) for r in range(3) for c in range(2)]
              + [(r * 3 + c, (r + 1) * 3 + c) for r in range(2) for c in range(3)]),
    "K33": (6, [(i, j) for i in range(3) for j in range(3, 6)]),
}


def allowed_pair(excluded, win, wout, a, m, b) -> bool:
    state = [0, 0, 0]
    state[win], state[wout], state[3 - win - wout] = a, b, m
    return tuple(state) not in excluded


def table_kind(excluded, win, wout, m) -> str:
    pairs = {(a, b) for a, b in product((0, 1), repeat=2) if allowed_pair(excluded, win, wout, a, m, b)}
    if pairs == {(0, 0), (1, 1)}:
        return "identity"
    if pairs == {(0, 1), (1, 0)}:
        return "swap"
    return "other"


def satisfiable(n, edges, pattern, excluded, win, wout) -> bool:
    """Backtracking search for a witness assignment satisfying every edge copy."""
    incident = {v: [(e, a, b) for e, (a, b) in enumerate(edges) if max(a, b) == v] for v in range(n)}
    w = [0] * n

    def place(v: int) -> bool:
        if v == n:
            return True
        for value in (0, 1):
            w[v] = value
            if all(allowed_pair(excluded, win, wout, w[a], pattern[e], w[b]) for e, a, b in incident[v]):
                if place(v + 1):
                    return True
        return False

    return place(0)


def odd_permutation_cycle(n, edges, kinds) -> bool:
    adjacency = {v: [] for v in range(n)}
    for (u, v), kind in zip(edges, kinds):
        if kind in ("identity", "swap"):
            s = kind == "swap"
            adjacency[u].append((v, s))
            adjacency[v].append((u, s))
    colour = {}
    for start in range(n):
        if start in colour:
            continue
        colour[start] = 0
        stack = [start]
        while stack:
            u = stack.pop()
            for v, s in adjacency[u]:
                if v not in colour:
                    colour[v] = colour[u] ^ s
                    stack.append(v)
                elif colour[v] != colour[u] ^ s:
                    return True
    return False


def main() -> int:
    result = json.loads((ARTIFACT / "result.json").read_text())
    rows = [json.loads(line) for line in (ARTIFACT / "raw_rows.jsonl").read_text().splitlines()]
    failures: list[str] = []

    def expect(condition: bool, message: str) -> None:
        if not condition:
            failures.append(message)

    networks = [r for r in rows if r["part"] == "network"]
    by_key = {(r["graph"], tuple(map(tuple, r["excluded"])), r["win"], r["wout"]): r for r in networks}
    cube = list(product((0, 1), repeat=3))
    knots = [frozenset(E) for size in range(1, 9) for E in combinations(cube, size)
             if all(sum(x != y for x, y in zip(p, q)) != 1 for p, q in combinations(E, 2))]
    expect(len(knots) == 34, "knot count")

    brute_checked = 0
    unexplained = Counter()
    unexplained_kinds = Counter()
    for name, (n, edges) in GRAPHS.items():
        stride = 1 if name in ("C4", "K4", "K23") else 3
        for index, (excluded, win, wout) in enumerate(
                (e, i, j) for e in knots for i in range(3) for j in range(3) if i != j):
            row = by_key[(name, tuple(sorted(excluded)), win, wout)]
            kinds = [table_kind(excluded, win, wout, m) for m in (0, 1)]
            if index % stride == 0:
                count = sum(1 for pattern in product((0, 1), repeat=len(edges))
                            if not satisfiable(n, edges, pattern, excluded, win, wout))
                expect(count == row["excluded_total"], f"{name} {sorted(excluded)} {win}{wout}: excluded count")
                brute_checked += 1
            # post hoc split (all graphs, all placements), recomputed from the definition
            if row["excluded_total"]:
                for pattern in product((0, 1), repeat=len(edges)):
                    excluded_here = not satisfiable(n, edges, pattern, excluded, win, wout)
                    if excluded_here and not odd_permutation_cycle(n, edges, [kinds[pattern[e]] for e in range(len(edges))]):
                        unexplained[name] += 1
                        unexplained_kinds[(name, tuple(sorted(kinds)))] += 1

    # many-valued rings by dynamic programming over products
    links = {"Z3": [tuple((w + m) % 3 for w in range(3)) for m in range(3)],
             "transpositions": [(0, 2, 1), (2, 1, 0), (1, 0, 2)],
             "S3": list(permutations(range(3)))}
    for name, perms in links.items():
        counts = {(0, 1, 2): 1}
        recorded = result["many_valued"][name]["by_length"]
        for k in range(1, 7):
            nxt = Counter()
            for p, c in counts.items():
                for q in perms:
                    nxt[tuple(q[p[i]] for i in range(3))] += c
            counts = nxt
            allowed = sum(c for p, c in counts.items() if any(p[i] == i for i in range(3)))
            expect(allowed == recorded[str(k)]["allowed"], f"{name} k={k}: allowed count")
        states = {(w, m, perms[m][w]) for m in range(len(perms)) for w in range(3)}
        lines_ok = all(any((w, m, x) in states for x in range(3)) for w in range(3) for m in range(len(perms))) and \
            all(any((x, m, b) in states for x in range(3)) for b in range(3) for m in range(len(perms))) and \
            all(any((w, m, b) in states for m in range(len(perms))) for w in range(3) for b in range(3))
        expect(lines_ok and result["many_valued"][name]["is_knot"], f"{name}: knot condition")

    # sampled knots: redraw and recompute by brute force
    rng = random.Random(20261019)
    states27 = list(product(range(3), repeat=3))
    samples = []
    while len(samples) < 2000:
        excluded = {s for s in states27 if rng.random() < 0.25}
        allowed = set(states27) - excluded
        full_lines = any(all((w, m, x) not in allowed for x in range(3)) for w in range(3) for m in range(3)) or \
            any(all((x, m, b) not in allowed for x in range(3)) for m in range(3) for b in range(3)) or \
            any(all((w, x, b) not in allowed for x in range(3)) for w in range(3) for b in range(3))
        if excluded and not full_lines:
            samples.append(allowed)
    sampled_rows = [r for r in rows if r["part"] == "sampled"]
    expect(len(sampled_rows) == 2000, "sample count")
    for allowed, row in zip(samples[:200], sampled_rows[:200]):
        for k in range(1, 5):
            ok = sum(1 for pattern in product(range(3), repeat=k)
                     if any(all((w[i], pattern[i], w[(i + 1) % k]) in allowed for i in range(k))
                            for w in product(range(3), repeat=k)))
            bits = math.log2(3 ** k / ok) if ok else float("inf")
            expect(abs(bits - row["bits"][str(k)]) < 1e-5, f"sampled bits k={k}")

    expect(all(result["controls"].values()), "controls")
    print(json.dumps({"brute_force_network_placements": brute_checked,
                      "post_hoc_unexplained_by_permutation_cycles": dict(unexplained),
                      "post_hoc_unexplained_by_transfer_kinds": {f"{g} {k}": v for (g, k), v in unexplained_kinds.items()}},
                     indent=1))
    print(f"{'passed' if not failures else 'FAILED'}: recomputation agrees (V1, exploratory evidence only)")
    for failure in failures[:20]:
        print("  failed:", failure)
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
