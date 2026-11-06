#!/usr/bin/env python3
"""Producer for HOLE-CRITERION-COLOURING-20261019-001A-E001: holes of partial-colouring shapes.

Exploratory exact enumeration over the roster frozen in contract.json.

(a) For every graph on s = 2..5 vertices up to isomorphism and N = 2..2s+1
    colours, the reduced GF(2) homology of the complex of partial proper
    colourings Ind(G □ K_N) in dimensions s-2 and s-1.
(b) For each roster graph G with N colours: B_hole, the largest B such that
    every vertex set S with 2 <= |S| <= B has no hole in dimension |S|-2, and
    the exact Nullstellensatz degree of the functional N-colouring system over
    GF(2), from the moment equations.

Self-contained; imports nothing from tools/knotlab (the checker uses it).

    python3 -B run.py    writes raw_rows.jsonl and result.json under artifacts/
"""

from __future__ import annotations

import json
import resource
import time
from itertools import combinations, permutations, product
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUT = ROOT / "artifacts" / "HOLE-CRITERION-COLOURING-20261019-001A" / HERE.name
CONST = -1
UNKNOWN_BUDGET = 400_000
DEGREE_BUDGET = 7


# ---------------------------------------------------------------- homology

def colourings(vertices: list[int], edges: set[frozenset], N: int, size: int) -> list[tuple]:
    """Partial proper colourings of `vertices` that colour exactly `size` of them (-1 = uncoloured)."""
    out = []
    pairs = [(a, b) for a, b in combinations(range(len(vertices)), 2)
             if frozenset((vertices[a], vertices[b])) in edges]
    for chosen in combinations(range(len(vertices)), size):
        for colours in product(range(N), repeat=size):
            assignment = [-1] * len(vertices)
            for position, colour in zip(chosen, colours):
                assignment[position] = colour
            if all(not (assignment[a] >= 0 and assignment[a] == assignment[b]) for a, b in pairs):
                out.append(tuple(assignment))
    return out


def rank_gf2(rows: list[set]) -> int:
    pivots: dict[int, set] = {}
    for row in rows:
        r = set(row)
        while r:
            top = max(r)
            if top in pivots:
                r ^= pivots[top]
            else:
                pivots[top] = r
                break
    return len(pivots)


def top_holes(vertices: list[int], edges: set[frozenset], N: int) -> tuple[int, int]:
    """(dim H~_{s-2}, dim H~_{s-1}) of the partial proper colouring complex of G[vertices]."""
    s = len(vertices)
    full = colourings(vertices, edges, N, s)
    mid = colourings(vertices, edges, N, s - 1)
    low = colourings(vertices, edges, N, s - 2) if s >= 2 else []
    index_mid = {f: i for i, f in enumerate(mid)}
    index_low = {f: i for i, f in enumerate(low)}

    def faces(f: tuple, index: dict) -> set:
        out = set()
        for position, colour in enumerate(f):
            if colour >= 0:
                g = list(f)
                g[position] = -1
                out.add(index[tuple(g)])
        return out

    rank_top = rank_gf2([faces(f, index_mid) for f in full])
    rank_mid = rank_gf2([faces(f, index_low) for f in mid]) if s >= 2 else 0
    return len(mid) - rank_mid - rank_top, len(full) - rank_top


# ---------------------------------------------------------------- graphs

def canonical(s: int, edges: set[frozenset]) -> tuple:
    best = None
    for perm in permutations(range(s)):
        key = tuple(sorted(tuple(sorted((perm[a], perm[b]))) for a, b in (tuple(e) for e in edges)))
        if best is None or key < best:
            best = key
    return best


def all_graphs(s: int) -> list[set[frozenset]]:
    pairs = list(combinations(range(s), 2))
    seen = {}
    for mask in range(1 << len(pairs)):
        edges = {frozenset(pairs[k]) for k in range(len(pairs)) if mask >> k & 1}
        key = canonical(s, edges)
        seen.setdefault(key, edges)
    return [seen[k] for k in sorted(seen, key=lambda k: (len(k), k))]


def degrees(n: int, edges: set[frozenset]) -> list[int]:
    return [sum(1 for e in edges if v in e) for v in range(n)]


def chromatic_number(n: int, edges: set[frozenset]) -> int:
    for k in range(1, n + 1):
        if colourings(list(range(n)), edges, k, n):
            return k
    return n


def clique_number(n: int, edges: set[frozenset]) -> int:
    best = 1 if n else 0
    for size in range(2, n + 1):
        if any(all(frozenset(p) in edges for p in combinations(c, 2)) for c in combinations(range(n), size)):
            best = size
    return best


def complete(n): return {frozenset(p) for p in combinations(range(n), 2)}
def cycle(n): return {frozenset((i, (i + 1) % n)) for i in range(n)}


def wheel(rim: int) -> set[frozenset]:
    return {frozenset((0, i)) for i in range(1, rim + 1)} | {frozenset((1 + i, 1 + (i + 1) % rim)) for i in range(rim)}


def petersen() -> set[frozenset]:
    return ({frozenset((i, (i + 1) % 5)) for i in range(5)} | {frozenset((i, i + 5)) for i in range(5)}
            | {frozenset((5 + i, 5 + (i + 2) % 5)) for i in range(5)})


def moser() -> set[frozenset]:
    return {frozenset(p) for p in [(0, 1), (0, 2), (1, 2), (1, 3), (2, 3), (0, 4), (0, 5), (4, 5), (4, 6), (5, 6), (3, 6)]}


def mycielskian(n: int, edges: set[frozenset]) -> tuple[int, set[frozenset]]:
    out = set(edges)
    for e in edges:
        a, b = tuple(e)
        out.add(frozenset((a, n + b)))
        out.add(frozenset((b, n + a)))
    for i in range(n):
        out.add(frozenset((n + i, 2 * n)))
    return 2 * n + 1, out


def roster() -> list[tuple[str, int, set[frozenset], int]]:
    m3 = mycielskian(3, complete(3))
    m4 = mycielskian(4, complete(4))
    grotzsch = mycielskian(5, cycle(5))
    return [
        ("K3", 3, complete(3), 2), ("K4", 4, complete(4), 3), ("K5", 5, complete(5), 4), ("K6", 6, complete(6), 5),
        ("C5", 5, cycle(5), 2), ("C7", 7, cycle(7), 2), ("Petersen", 10, petersen(), 2),
        ("W5", 6, wheel(5), 3), ("W7", 8, wheel(7), 3), ("Moser", 7, moser(), 3),
        ("M(K3)", m3[0], m3[1], 3), ("Grotzsch", grotzsch[0], grotzsch[1], 3), ("M(K4)", m4[0], m4[1], 4),
    ]


# ---------------------------------------------------------------- Nullstellensatz degree

def ns_feasible(n: int, edges: set[frozenset], N: int, B: int) -> tuple[bool | None, int]:
    """Do normalized moments exist through degree B? (None if over budget.)"""
    adjacency = {v: {u for e in edges if v in e for u in e if u != v} for v in range(n)}
    index: dict[tuple, int] = {}
    layers: list[list[tuple]] = [[()]]
    index[()] = 0
    for size in range(1, B + 1):
        layer = []
        for T in layers[-1]:
            coloured = {v for v, _ in T}
            last = max(coloured) if coloured else -1
            for v in range(last + 1, n):
                taken = {c for u, c in T if u in adjacency[v]}
                for c in range(N):
                    if c not in taken:
                        U = T + ((v, c),)
                        layer.append(U)
        for U in layer:
            index[U] = len(index)
        layers.append(layer)
        if len(index) > UNKNOWN_BUDGET:
            return None, len(index)
    rows = [{index[()], CONST}]
    for size in range(0, B):
        for T in layers[size]:
            coloured = {v for v, _ in T}
            for v in range(n):
                if v in coloured:
                    continue
                taken = {c for u, c in T if u in adjacency[v]}
                row = {index[tuple(sorted(T + ((v, c),)))] for c in range(N) if c not in taken}
                row ^= {index[T]}
                rows.append(row)
    pivots: dict[int, set] = {}
    for row in rows:
        r = set(row)
        while r:
            top = max(r)
            if top == CONST:
                return False, len(index)
            if top in pivots:
                r ^= pivots[top]
            else:
                pivots[top] = r
                break
    return True, len(index)


def b_hole(n: int, edges: set[frozenset], N: int, cap: int) -> tuple[int, list | None, int, int]:
    """(B_hole, first set with a hole, sets with a hole at that size, sets of that size)."""
    best = 1
    for size in range(2, min(n, cap) + 1):
        holed = [S for S in combinations(range(n), size) if top_holes(list(S), edges, N)[0]]
        if holed:
            return best, list(holed[0]), len(holed), sum(1 for _ in combinations(range(n), size))
        best = size
    return best, None, 0, 0


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    started = time.time()
    rows = []

    # (a) universality sweep
    for s in range(2, 6):
        for edges in all_graphs(s):
            deg = degrees(s, edges)
            info = {"part": "universality", "s": s, "edges": sorted(sorted(tuple(e)) for e in edges),
                    "edge_count": len(edges), "max_degree": max(deg), "clique": clique_number(s, edges),
                    "chromatic": chromatic_number(s, edges)}
            holes = {}
            for N in range(2, 2 * s + 2):
                below, top = top_holes(list(range(s)), edges, N)
                holes[str(N)] = {"dim_s_minus_2": below, "dim_s_minus_1": top}
            vanishing = [int(N) for N, h in holes.items() if h["dim_s_minus_2"] == 0]
            threshold = None
            for N in range(2 * s + 1, 1, -1):
                if holes[str(N)]["dim_s_minus_2"] == 0:
                    threshold = N
                else:
                    break
            rows.append({**info, "holes": holes, "vanishing_N": vanishing, "threshold": threshold})
    universality = [r for r in rows if r["part"] == "universality"]

    # (b) roster
    for name, n, edges, N in roster():
        t0 = time.time()
        cap = DEGREE_BUDGET
        hole_bound, failing, holed, of_size = b_hole(n, edges, N, cap)
        ns_degree, unknowns, status, feasible_through = None, 0, "degree_budget", 0
        for B in range(1, DEGREE_BUDGET + 1):
            ok, unknowns = ns_feasible(n, edges, N, B)
            if ok is None:
                status = "over_unknown_budget"
                break
            if ok is False:
                ns_degree, status = B, "found"
                break
            feasible_through = B
        rows.append({
            "part": "roster", "graph": name, "vertices": n, "edges": len(edges), "N": N,
            "chromatic": chromatic_number(n, edges) if n <= 11 else None,
            "B_hole": hole_bound, "B_hole_capped": failing is None and hole_bound >= min(n, cap),
            "first_failing_set": failing, "sets_with_hole_at_first_failing_size": holed,
            "sets_of_first_failing_size": of_size, "ns_degree": ns_degree, "ns_status": status,
            "ns_feasible_through": feasible_through, "unknowns_at_last_degree": unknowns,
            "slack": (ns_degree - 1 - hole_bound) if ns_degree is not None else None,
            "slack_at_least": feasible_through - hole_bound,
            "seconds": round(time.time() - t0, 2),
        })
        print(rows[-1], flush=True)
        if ns_degree is not None and ns_degree <= hole_bound:
            break  # contract stop rule: a violation of NS_degree > B_hole ends the run

    with (OUT / "raw_rows.jsonl").open("w") as handle:
        for row in rows:
            handle.write(json.dumps(row, sort_keys=True) + "\n")
    roster_rows = [r for r in rows if r["part"] == "roster"]
    complete_rows = [r for r in universality if r["edge_count"] == r["s"] * (r["s"] - 1) // 2]
    control_complete = all(
        r["holes"][str(2 * r["s"] - 2)]["dim_s_minus_2"] > 0 and r["holes"][str(2 * r["s"] - 1)]["dim_s_minus_2"] == 0
        for r in complete_rows if r["s"] >= 2)
    odd = next((r for r in roster_rows if r["graph"] == "C5"), None)
    violations = [r["graph"] for r in roster_rows if r["ns_degree"] is not None and r["ns_degree"] <= r["B_hole"]]
    result = {
        "schema_version": 1,
        "experiment_id": "HOLE-CRITERION-COLOURING-20261019-001A-E001",
        "ticket": "HOLE-CRITERION-COLOURING-20261019-001A",
        "evidence_stage": "exploratory",
        "raw_rows": str((OUT / "raw_rows.jsonl").relative_to(ROOT)),
        "graphs_by_size": {str(s): sum(1 for r in universality if r["s"] == s) for s in range(2, 6)},
        "universality_no_hole_at_2s_minus_1": all(
            r["holes"][str(2 * r["s"] - 1)]["dim_s_minus_2"] == 0 for r in universality),
        "universality_exceptions": [
            {"s": r["s"], "edges": r["edges"]} for r in universality
            if r["holes"][str(2 * r["s"] - 1)]["dim_s_minus_2"] != 0],
        "thresholds": [
            {"s": r["s"], "edges": r["edge_count"], "max_degree": r["max_degree"], "threshold": r["threshold"],
             "vanishing_N": r["vanishing_N"]} for r in universality],
        "control_complete_graphs_sharp": control_complete,
        "control_odd_cycle_hole_at_two": odd is not None and odd["B_hole"] == 1,
        "theorem_check_violations": violations,
        "roster": [{k: r[k] for k in ("graph", "vertices", "edges", "N", "chromatic", "B_hole", "B_hole_capped",
                                      "ns_degree", "ns_status", "ns_feasible_through", "slack", "slack_at_least")}
                   for r in roster_rows],
        "wall_seconds": round(time.time() - started, 1),
        "peak_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
    }
    result["status"] = "passed" if control_complete and result["control_odd_cycle_hole_at_two"] and not violations else "stopped"
    (OUT / "result.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({k: result[k] for k in ("status", "universality_no_hole_at_2s_minus_1", "universality_exceptions",
                                              "control_complete_graphs_sharp", "theorem_check_violations",
                                              "wall_seconds")}, indent=1))
    return 0 if result["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
