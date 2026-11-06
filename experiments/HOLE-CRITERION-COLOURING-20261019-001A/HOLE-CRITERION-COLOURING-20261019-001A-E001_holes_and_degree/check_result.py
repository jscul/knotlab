#!/usr/bin/env python3
"""Independent check of HOLE-CRITERION-COLOURING-20261019-001A-E001; imports no producer code.

Recomputes the producer's numbers with separately written code:

- the graphs on 2..5 vertices up to isomorphism, by adjacency-matrix
  certificates, against the known counts 2, 4, 11, 34 (OEIS A000088);
- every reduced GF(2) Betti number of the universality sweep, from the full
  face list with knotlab's homology;
- each roster graph from its own construction (Petersen as the Kneser graph
  K(5,2), the Mycielskians from the shadow construction), its chromatic number
  by backtracking, and B_hole from every vertex set up to one past B_hole;
- the Nullstellensatz degree in the primal form (is 1 a combination of the
  products m*f of degree at most B?) where the monomial space is small, and
  from a separately written moment solver up to a size limit;

then the controls and the frozen decision rule. Two positive controls show the
recomputation can return the other answer: a colourable instance has no
refutation in either form, and the two-colour edge has a hole.

    python3 -B check_result.py
"""

from __future__ import annotations

import json
import sys
import time
from itertools import combinations, permutations, product
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "tools"))
from knotlab.space import homology  # noqa: E402

ARTIFACT = ROOT / "artifacts" / "HOLE-CRITERION-COLOURING-20261019-001A" / HERE.name
KNOWN_GRAPH_COUNTS = {2: 2, 3: 4, 4: 11, 5: 34}  # OEIS A000088
PRIMAL_COLUMN_LIMIT = 40_000
DUAL_UNKNOWN_LIMIT = 60_000
CAP = 7
CONTRACT_PREFIXES = [("K3,", "K3"), ("K4,", "K4"), ("K5,", "K5"), ("K6,", "K6"), ("C5,", "C5"), ("C7,", "C7"),
                     ("Petersen,", "Petersen"), ("W5 ", "W5"), ("W7 ", "W7"), ("Moser spindle,", "Moser"),
                     ("Mycielskian of K3 ", "M(K3)"), ("Grötzsch graph ", "Grotzsch"), ("Mycielskian of K4 ", "M(K4)")]


# ---------------------------------------------------------------- graphs

def certificate(s: int, edges: set[tuple[int, int]]) -> int:
    """Smallest upper-triangle adjacency bit string over all relabellings."""
    pairs = list(combinations(range(s), 2))
    best = None
    for perm in permutations(range(s)):
        moved = {tuple(sorted((perm[a], perm[b]))) for a, b in edges}
        code = sum(1 << k for k, pair in enumerate(pairs) if pair in moved)
        best = code if best is None else min(best, code)
    return best


def graph_classes(s: int) -> set[int]:
    pairs = list(combinations(range(s), 2))
    return {certificate(s, {pairs[k] for k in range(len(pairs)) if mask >> k & 1})
            for mask in range(1 << len(pairs))}


def mycielski(vertices: list, edges: set[frozenset]) -> tuple[list, set[frozenset]]:
    shadow = {v: ("shadow", v) for v in vertices}
    hub = ("hub",)
    out = set(edges)
    for e in edges:
        a, b = sorted(e, key=repr)
        out |= {frozenset((a, shadow[b])), frozenset((b, shadow[a]))}
    out |= {frozenset((shadow[v], hub)) for v in vertices}
    return vertices + [shadow[v] for v in vertices] + [hub], out


def roster_graphs() -> dict[str, tuple[list, set[frozenset]]]:
    def clique(n):
        return list(range(n)), {frozenset(p) for p in combinations(range(n), 2)}

    def ring(n):
        return list(range(n)), {frozenset((i, (i + 1) % n)) for i in range(n)}

    def odd_wheel(rim):
        vs, es = ring(rim)
        return vs + ["hub"], es | {frozenset((v, "hub")) for v in vs}

    kneser = [frozenset(p) for p in combinations(range(5), 2)]
    petersen = (kneser, {frozenset((a, b)) for a, b in combinations(kneser, 2) if not a & b})
    tips = ["a", "b1", "c1", "d1", "b2", "c2", "d2"]
    moser = (tips, {frozenset(p) for p in [("a", "b1"), ("a", "c1"), ("b1", "c1"), ("b1", "d1"), ("c1", "d1"),
                                           ("a", "b2"), ("a", "c2"), ("b2", "c2"), ("b2", "d2"), ("c2", "d2"),
                                           ("d1", "d2")]})
    return {"K3": clique(3), "K4": clique(4), "K5": clique(5), "K6": clique(6), "C5": ring(5), "C7": ring(7),
            "Petersen": petersen, "W5": odd_wheel(5), "W7": odd_wheel(7), "Moser": moser,
            "M(K3)": mycielski(*clique(3)), "Grotzsch": mycielski(*ring(5)), "M(K4)": mycielski(*clique(4))}


def chromatic(vertices: list, edges: set[frozenset]) -> int:
    order = sorted(vertices, key=lambda v: -sum(v in e for e in edges))
    neighbours = {v: {u for e in edges if v in e for u in e if u != v} for v in vertices}

    def colourable(k: int) -> bool:
        colour: dict = {}

        def place(i: int) -> bool:
            if i == len(order):
                return True
            v = order[i]
            for c in range(k):
                if all(colour.get(u) != c for u in neighbours[v]):
                    colour[v] = c
                    if place(i + 1):
                        return True
                    del colour[v]
            return False

        return place(0)

    return next(k for k in range(1, len(vertices) + 1) if colourable(k))


# ---------------------------------------------------------------- homology

def betti(vertices: list, edges: set[frozenset], N: int) -> dict[int, int]:
    """Reduced GF(2) Betti numbers of Ind(G[vertices] □ K_N) from its full face list."""
    inside = [tuple(e) for e in edges if all(v in vertices for v in e)]
    faces = []
    for size in range(len(vertices) + 1):
        for chosen in combinations(vertices, size):
            for colours in product(range(N), repeat=size):
                pick = dict(zip(chosen, colours))
                if all(not (a in pick and b in pick and pick[a] == pick[b]) for a, b in inside):
                    faces.append(frozenset((repr(v), c) for v, c in pick.items()))
    return homology(faces)


# ---------------------------------------------------------------- Nullstellensatz

def eliminate(rows, constant_bit: int = 0) -> tuple[dict[int, int], bool]:
    """Leading-bit GF(2) elimination; reports whether a row reduced to the constant alone."""
    basis: dict[int, int] = {}
    for row in rows:
        while row:
            lead = row.bit_length() - 1
            if lead == constant_bit:
                return basis, True
            if lead in basis:
                row ^= basis[lead]
            else:
                basis[lead] = row
                break
    return basis, False


def dual_refutes(vertices: list, edges: set[frozenset], N: int, B: int) -> bool | None:
    """True if the degree-B moment equations have no GF(2) solution; None past the size limit."""
    nbrs = {v: {u for e in edges if v in e for u in e if u != v} for v in vertices}
    unknowns: dict[frozenset, int] = {frozenset(): 1}
    frontier = [frozenset()]
    for _ in range(B):
        grown = set()
        for T in frontier:
            used = {v for v, _ in T}
            for v in vertices:
                if v in used:
                    continue
                blocked = {c for u, c in T if u in nbrs[v]}
                grown |= {T | {(v, c)} for c in range(N) if c not in blocked}
        frontier = sorted(grown, key=lambda t: sorted((repr(v), c) for v, c in t))
        for T in frontier:
            unknowns[T] = len(unknowns) + 1
        if len(unknowns) > DUAL_UNKNOWN_LIMIT:
            return None
    rows = [(1 << unknowns[frozenset()]) | 1]
    for T, bit in unknowns.items():
        if len(T) >= B:
            continue
        used = {v for v, _ in T}
        for v in vertices:
            if v in used:
                continue
            blocked = {c for u, c in T if u in nbrs[v]}
            row = 1 << bit
            for c in range(N):
                if c not in blocked:
                    row ^= 1 << unknowns[T | {(v, c)}]
            rows.append(row)
    return eliminate(rows)[1]


def primal_columns(variables: int, B: int) -> int:
    from math import comb
    return sum(comb(variables, k) for k in range(B + 1))


def primal_refutes(vertices: list, edges: set[frozenset], N: int, B: int) -> bool:
    """Is 1 in the GF(2) span of the multilinear products m*f with deg(m) + deg(f) <= B?"""
    var = {(v, c): k for k, (v, c) in enumerate(product(vertices, range(N)))}
    axioms = [frozenset({frozenset({var[v, c]}) for c in range(N)} | {frozenset()}) for v in vertices]
    axioms += [frozenset({frozenset({var[v, c], var[v, d]})}) for v in vertices for c, d in combinations(range(N), 2)]
    axioms += [frozenset({frozenset({var[a, c], var[b, c]})}) for a, b in (tuple(e) for e in edges) for c in range(N)]
    column: dict[frozenset, int] = {}
    for k in range(B + 1):
        for chosen in combinations(range(len(var)), k):
            column[frozenset(chosen)] = len(column)
    assert column[frozenset()] == 0

    def products():
        for f in axioms:
            degree = max(len(t) for t in f)
            for k in range(B - degree + 1):
                for chosen in combinations(range(len(var)), k):
                    m = frozenset(chosen)
                    row = 0
                    for t in f:
                        row ^= 1 << column[m | t]
                    if row:
                        yield row

    return eliminate(products())[1]


# ---------------------------------------------------------------- main

def main() -> int:
    started = time.time()
    result = json.loads((ARTIFACT / "result.json").read_text())
    rows = [json.loads(line) for line in (ARTIFACT / "raw_rows.jsonl").read_text().splitlines()]
    contract = json.loads((HERE / "contract.json").read_text())
    failures: list[str] = []

    def expect(condition: bool, message: str) -> None:
        if not condition:
            failures.append(message)

    universality = [r for r in rows if r["part"] == "universality"]
    roster = [r for r in rows if r["part"] == "roster"]

    # graphs up to isomorphism
    for s, count in KNOWN_GRAPH_COUNTS.items():
        classes = graph_classes(s)
        expect(len(classes) == count, f"own enumeration finds {len(classes)} graphs on {s} vertices")
        produced = [certificate(s, {tuple(e) for e in r["edges"]}) for r in universality if r["s"] == s]
        expect(sorted(produced) == sorted(classes), f"producer's graphs on {s} vertices are not one per class")

    # every Betti number of the sweep
    recomputed = 0
    for r in universality:
        vertices = list(range(r["s"]))
        edges = {frozenset(e) for e in r["edges"]}
        for N in range(2, 2 * r["s"] + 2):
            b = betti(vertices, edges, N)
            got = r["holes"][str(N)]
            expect(b.get(r["s"] - 2, 0) == got["dim_s_minus_2"] and b.get(r["s"] - 1, 0) == got["dim_s_minus_1"],
                   f"Betti numbers differ for s={r['s']} edges={r['edges']} N={N}: {b} vs {got}")
            recomputed += 1
    no_hole = all(r["holes"][str(2 * r["s"] - 1)]["dim_s_minus_2"] == 0 for r in universality)
    expect(result["universality_no_hole_at_2s_minus_1"] == no_hole, "universality flag misreported")
    complete = [r for r in universality if r["edge_count"] == r["s"] * (r["s"] - 1) // 2]
    control_complete = all(r["holes"][str(2 * r["s"] - 2)]["dim_s_minus_2"] > 0
                           and r["holes"][str(2 * r["s"] - 1)]["dim_s_minus_2"] == 0 for r in complete)
    expect(len(complete) == 4 and control_complete == result["control_complete_graphs_sharp"],
           "complete-graph control misreported")

    # roster, from independent constructions
    graphs = roster_graphs()
    entries = contract["public_inputs"]["roster"]
    expect(len(entries) == len(CONTRACT_PREFIXES) == len(graphs)
           and all(entry.startswith(prefix) for entry, (prefix, _) in zip(entries, CONTRACT_PREFIXES)),
           "contract roster differs from the checker's reading of it")
    frozen = [(key, int(entry.rsplit("N=", 1)[1])) for entry, (_, key) in zip(entries, CONTRACT_PREFIXES)]
    expect([(r["graph"], r["N"]) for r in roster] == frozen[:len(roster)], "roster differs from the contract")
    expect(len(roster) == len(frozen) or bool(result["theorem_check_violations"]),
           "roster ended early without a violation")
    rechecks = []
    for r in roster:
        vertices, edges = graphs[r["graph"]]
        N = r["N"]
        expect((len(vertices), len(edges)) == (r["vertices"], r["edges"]), f"{r['graph']}: size differs")
        chi = chromatic(vertices, edges)
        expect(r["chromatic"] in (None, chi) and chi > N, f"{r['graph']}: chromatic number {chi} vs {r['chromatic']}")
        top = min(len(vertices), CAP, r["B_hole"] + 1)
        holed_at_top = 0
        for size in range(2, top + 1):
            for S in combinations(vertices, size):
                if betti(list(S), edges, N).get(size - 2, 0):
                    expect(size > r["B_hole"], f"{r['graph']}: hole at {S} inside B_hole")
                    holed_at_top += 1
        if r["B_hole_capped"]:
            expect(holed_at_top == 0 and r["B_hole"] == min(len(vertices), CAP), f"{r['graph']}: cap misreported")
        else:
            expect(holed_at_top == r["sets_with_hole_at_first_failing_size"] > 0,
                   f"{r['graph']}: {holed_at_top} sets with a hole at size {top}")
        expect(r["slack_at_least"] == r["ns_feasible_through"] - r["B_hole"], f"{r['graph']}: slack bound")
        if r["ns_degree"] is not None:
            expect(r["ns_feasible_through"] == r["ns_degree"] - 1 and r["slack"] == r["ns_degree"] - 1 - r["B_hole"],
                   f"{r['graph']}: slack arithmetic")
        entry = {"graph": r["graph"], "chromatic": chi}
        degree, below = r["ns_degree"], r["ns_feasible_through"]
        if below >= 1:
            dual_below = dual_refutes(vertices, edges, N, below)
            entry["dual_feasible_through"] = dual_below
            expect(dual_below in (False, None), f"{r['graph']}: own moment solver refutes at {below}")
        if degree is not None:
            dual_at = dual_refutes(vertices, edges, N, degree)
            entry["dual_refutes_at_degree"] = dual_at
            expect(dual_at in (True, None), f"{r['graph']}: own moment solver finds moments at {degree}")
        columns = primal_columns(len(vertices) * N, degree if degree is not None else below)
        if columns <= PRIMAL_COLUMN_LIMIT:
            if below >= 1:
                entry["primal_refutes_below"] = primal_refutes(vertices, edges, N, below)
                expect(not entry["primal_refutes_below"], f"{r['graph']}: primal refutation at degree {below}")
            if degree is not None:
                entry["primal_refutes_at_degree"] = primal_refutes(vertices, edges, N, degree)
                expect(entry["primal_refutes_at_degree"], f"{r['graph']}: no primal refutation at degree {degree}")
        rechecks.append(entry)

    # the criterion itself, and the reported summary
    violations = [r["graph"] for r in roster if r["ns_degree"] is not None and r["ns_degree"] <= r["B_hole"]]
    expect(violations == result["theorem_check_violations"], "theorem-check violations misreported")
    expect(result["status"] == ("passed" if control_complete and result["control_odd_cycle_hole_at_two"]
                                and not violations else "stopped"), "status misreported")
    odd = next((r for r in roster if r["graph"] == "C5"), None)
    expect(odd is not None and odd["B_hole"] == 1 and result["control_odd_cycle_hole_at_two"],
           "odd-cycle control fails")

    # positive controls: the recomputation can return the other answer
    vs4, es4 = graphs["K4"]
    expect(not primal_refutes(vs4, es4, 4, 3) and dual_refutes(vs4, es4, 4, 4) is False,
           "control: K4 with four colours is refuted")
    expect(betti([0, 1], {frozenset((0, 1))}, 2) == {0: 1}, "control: the two-colour edge has no hole")

    print(json.dumps({"rechecks": rechecks}, indent=1))
    print(f"{'passed' if not failures else 'FAILED'}: {recomputed} Betti pairs, {len(roster)} roster entries, "
          f"{round(time.time() - started)} s (V1 recomputation; no theorem authority)")
    for failure in failures:
        print("  failed:", failure)
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
