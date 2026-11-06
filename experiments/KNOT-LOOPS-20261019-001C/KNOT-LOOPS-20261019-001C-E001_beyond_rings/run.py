#!/usr/bin/env python3
"""Producer for KNOT-LOOPS-20261019-001C-E001: beyond rings.

(a) Networks: one copy of a three-variable knot placement on every edge of a
    small graph (edges oriented from lower to higher vertex), witnesses at the
    vertices; the composite on the edges' middle distinctions after forgetting
    the witnesses, split by whether every edge transfer is a permutation.
(b) Many-valued links with permutation transfers: Z3, transpositions, S3.
(c) Sampled three-valued knots: bits remembered by rings as they grow.

    python3 -B run.py    writes raw_rows.jsonl and result.json under artifacts/
"""

from __future__ import annotations

import json
import math
import random
import resource
import time
from itertools import combinations, permutations, product
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUT = ROOT / "artifacts" / "KNOT-LOOPS-20261019-001C" / HERE.name
IDENTITY, SWAP = 0b1001, 0b0110


def grid(n: int) -> list[tuple[int, int]]:
    edges = []
    for r in range(n):
        for c in range(n):
            if c + 1 < n:
                edges.append((r * n + c, r * n + c + 1))
            if r + 1 < n:
                edges.append((r * n + c, (r + 1) * n + c))
    return edges


GRAPHS = {
    "C4": (4, [(0, 1), (1, 2), (2, 3), (0, 3)]),
    "K4": (4, list(combinations(range(4), 2))),
    "K23": (5, [(0, 2), (0, 3), (0, 4), (1, 2), (1, 3), (1, 4)]),
    "prism": (6, [(0, 1), (1, 2), (0, 2), (3, 4), (4, 5), (3, 5), (0, 3), (1, 4), (2, 5)]),
    "grid3": (9, grid(3)),
    "K33": (6, [(i, j) for i in range(3) for j in range(3, 6)]),
}


def adjacent(p, q):
    return sum(x != y for x, y in zip(p, q)) == 1


def knots3() -> list[frozenset]:
    cube = list(product((0, 1), repeat=3))
    return [frozenset(E) for r in range(1, 9) for E in combinations(cube, r)
            if all(not adjacent(p, q) for p, q in combinations(E, 2))]


def transfers(excluded, win, wout):
    mid = 3 - win - wout
    table = []
    for m in (0, 1):
        mask = 0
        for a, b in product((0, 1), repeat=2):
            state = [0, 0, 0]
            state[win], state[wout], state[mid] = a, b, m
            if tuple(state) not in excluded:
                mask |= 1 << (2 * a + b)
        table.append(mask)
    return table


def ring_kind(table):
    has_swap, has_id = SWAP in table, IDENTITY in table
    return "every_length" if has_swap and has_id else ("odd_lengths" if has_swap else "never")


def value_masks(n_edges):
    """value_mask[e][v]: bitset of the middle patterns whose edge e has value v."""
    size = 1 << n_edges
    masks = [[0, 0] for _ in range(n_edges)]
    for e in range(n_edges):
        block = (1 << (1 << e)) - 1
        ones = 0
        for start in range(1 << e, size, 1 << (e + 1)):
            ones |= block << start
        masks[e] = [((1 << size) - 1) ^ ones, ones]
    return masks


def network_composite(n_vertices, edges, table, value_mask):
    """Bitsets over middle patterns (bit e of a pattern = edge e's middle value)."""
    n_edges = len(edges)
    size = 1 << n_edges
    full = (1 << size) - 1
    allowed = 0
    for w in range(1 << n_vertices):
        current = full
        for e, (u, v) in enumerate(edges):
            pair = 2 * (w >> u & 1) + (w >> v & 1)
            mask = 0
            for val in (0, 1):
                if table[val] >> pair & 1:
                    mask |= value_mask[e][val]
            current &= mask
            if not current:
                break
        allowed |= current
    perm_patterns = full
    for e in range(n_edges):
        mask = 0
        for val in (0, 1):
            if table[val] in (IDENTITY, SWAP):
                mask |= value_mask[e][val]
        perm_patterns &= mask
    return size, full, allowed, perm_patterns


def holonomy_excluded(n_vertices, edges, table, pattern) -> bool:
    """For a pattern whose transfers are all permutations: is some cycle's swap count odd?"""
    swap = [table[pattern >> e & 1] == SWAP for e in range(len(edges))]
    adjacency = {v: [] for v in range(n_vertices)}
    for e, (u, v) in enumerate(edges):
        adjacency[u].append((v, swap[e]))
        adjacency[v].append((u, swap[e]))
    colour = {}
    for start in range(n_vertices):
        if start in colour:
            continue
        colour[start] = 0
        stack = [start]
        while stack:
            u = stack.pop()
            for v, s in adjacency[u]:
                want = colour[u] ^ s
                if v not in colour:
                    colour[v] = want
                    stack.append(v)
                elif colour[v] != want:
                    return True
    return False


# ---------------------------------------------------------------- many-valued links

def compose_perm(p, q):  # first p then q
    return tuple(q[p[i]] for i in range(len(p)))


def has_fixed_point(p):
    return any(p[i] == i for i in range(len(p)))


Z3 = [tuple((w + m) % 3 for w in range(3)) for m in range(3)]
TRANSPOSITIONS = [(0, 2, 1), (2, 1, 0), (1, 0, 2)]  # the transposition fixing m
S3 = list(permutations(range(3)))


def is_many_valued_knot(states_allowed, sizes) -> bool:
    """Excluded set nonempty and no line along one variable fully excluded."""
    all_states = set(product(*[range(s) for s in sizes]))
    excluded = all_states - states_allowed
    if not excluded:
        return False
    for i, s in enumerate(sizes):
        for rest in product(*[range(t) for j, t in enumerate(sizes) if j != i]):
            line = [rest[:i] + (x,) + rest[i:] for x in range(s)]
            if all(state in excluded for state in line):
                return False
    return True


def link_states(perms):
    return {(w, m, perms[m][w]) for m in range(len(perms)) for w in range(3)}


def ring_allowed(perms, k):
    allowed = set()
    for pattern in product(range(len(perms)), repeat=k):
        p = (0, 1, 2)
        for m in pattern:
            p = compose_perm(p, perms[m])
        if has_fixed_point(p):
            allowed.add(pattern)
    return allowed


# ---------------------------------------------------------------- sampled three-valued knots

def mat_from_relation(rel, m):
    return sum(1 << (3 * a + b) for a in range(3) for b in range(3) if (a, m, b) in rel)


def mat_mul(x, y):
    out = 0
    for a in range(3):
        for c in range(3):
            if any(x >> (3 * a + b) & 1 and y >> (3 * b + c) & 1 for b in range(3)):
                out |= 1 << (3 * a + c)
    return out


DIAGONAL = sum(1 << (3 * i + i) for i in range(3))
PERM_MATS = {sum(1 << (3 * i + p[i]) for i in range(3)) for p in S3}


def ring_bits_by_dp(mats, max_k):
    counts = {sum(1 << (3 * i + i) for i in range(3)): 1}
    bits = {}
    for k in range(1, max_k + 1):
        nxt = {}
        for x, c in counts.items():
            for y in mats:
                z = mat_mul(x, y)
                nxt[z] = nxt.get(z, 0) + c
        counts = nxt
        allowed = sum(c for x, c in counts.items() if x & DIAGONAL)
        total = len(mats) ** k
        bits[k] = math.log2(total / allowed) if allowed else float("inf")
    return bits


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    started = time.time()
    rows = []
    knots = knots3()
    placements = [(e, i, j) for e in knots for i in range(3) for j in range(3) if i != j]

    # (a) networks
    network_summary = {}
    for name, (n_vertices, edges) in GRAPHS.items():
        edges = [tuple(sorted(e)) for e in edges]
        masks = value_masks(len(edges))
        summary = {"placements": 0, "with_nonpermutation_exclusions": 0, "holonomy_rule_mismatches": 0,
                   "by_ring_kind": {}}
        for excluded, win, wout in placements:
            table = transfers(excluded, win, wout)
            size, full, allowed, perm_patterns = network_composite(n_vertices, edges, table, masks)
            excluded_set = full & ~allowed
            ex_perm = excluded_set & perm_patterns
            ex_nonperm = excluded_set & ~perm_patterns
            mismatches = 0
            p = perm_patterns
            while p:
                low = p & -p
                pattern = low.bit_length() - 1
                predicted = holonomy_excluded(n_vertices, edges, table, pattern)
                mismatches += predicted != bool(ex_perm >> pattern & 1)
                p ^= low
            allowed_count = bin(allowed).count("1")
            kind = ring_kind(table)
            row = {"part": "network", "graph": name, "excluded": sorted(excluded), "win": win, "wout": wout,
                   "transfers": table, "ring_kind": kind, "patterns": size,
                   "excluded_total": bin(excluded_set).count("1"),
                   "excluded_permutation_patterns": bin(ex_perm).count("1"),
                   "excluded_nonpermutation_patterns": bin(ex_nonperm).count("1"),
                   "holonomy_rule_mismatches": mismatches,
                   "bits": round(math.log2(size / allowed_count), 6) if allowed_count else None}
            rows.append(row)
            summary["placements"] += 1
            summary["with_nonpermutation_exclusions"] += row["excluded_nonpermutation_patterns"] > 0
            summary["holonomy_rule_mismatches"] += mismatches
            bucket = summary["by_ring_kind"].setdefault(kind, {"placements": 0, "constrained": 0,
                                                              "with_nonpermutation_exclusions": 0})
            bucket["placements"] += 1
            bucket["constrained"] += row["excluded_total"] > 0
            bucket["with_nonpermutation_exclusions"] += row["excluded_nonpermutation_patterns"] > 0
        network_summary[name] = summary
        print(name, json.dumps(summary), flush=True)

    # (b) many-valued links with permutation transfers
    many_valued = {}
    for name, perms in (("Z3", Z3), ("transpositions", TRANSPOSITIONS), ("S3", S3)):
        states = link_states(perms)
        entry = {"middle_values": len(perms), "is_knot": is_many_valued_knot(states, (3, len(perms), 3)),
                 "by_length": {}}
        for k in range(1, 7):
            allowed = ring_allowed(perms, k)
            total = len(perms) ** k
            swapped = {(p[1], p[0]) + p[2:] for p in allowed} if k >= 2 else allowed
            entry["by_length"][str(k)] = {"allowed": len(allowed), "patterns": total,
                                          "bits": round(math.log2(total / len(allowed)), 6) if allowed else None,
                                          "order_matters": swapped != allowed}
        many_valued[name] = entry
        rows.append({"part": "many_valued", "link": name, **entry})
        print(name, json.dumps(entry), flush=True)

    # (c) sampled three-valued knots
    rng = random.Random(20261019)
    states27 = list(product(range(3), repeat=3))
    samples = []
    attempts = 0
    while len(samples) < 2000:
        attempts += 1
        excluded = {s for s in states27 if rng.random() < 0.25}
        allowed = set(states27) - excluded
        if is_many_valued_knot(allowed, (3, 3, 3)):
            samples.append(allowed)
    sampled_rows = []
    for allowed in samples:
        mats = [mat_from_relation(allowed, m) for m in range(3)]
        bits = ring_bits_by_dp(mats, 7)
        all_perm = all(x in PERM_MATS for x in mats)
        sampled_rows.append({"all_permutations": all_perm, "bits": {str(k): round(v, 6) for k, v in bits.items()},
                             "permutation_transfers": sum(x in PERM_MATS for x in mats)})
    for r in sampled_rows:
        rows.append({"part": "sampled", **r})

    def stats(group, k):
        values = [r["bits"][str(k)] for r in group]
        return {"count": len(values), "min": min(values) if values else None, "max": max(values) if values else None,
                "mean": round(sum(values) / len(values), 6) if values else None}

    by_perm = {}
    for count in range(4):
        group = [r for r in sampled_rows if r["permutation_transfers"] == count]
        by_perm[str(count)] = {"k1": stats(group, 1), "k7": stats(group, 7)}

    with (OUT / "raw_rows.jsonl").open("w") as handle:
        for row in rows:
            handle.write(json.dumps(row, sort_keys=True) + "\n")
    result = {
        "schema_version": 1,
        "experiment_id": "KNOT-LOOPS-20261019-001C-E001",
        "ticket": "KNOT-LOOPS-20261019-001C",
        "evidence_stage": "exploratory",
        "raw_rows": str((OUT / "raw_rows.jsonl").relative_to(ROOT)),
        "networks": network_summary,
        "many_valued": many_valued,
        "sampled": {"samples": len(samples), "attempts": attempts, "by_permutation_transfers": by_perm},
        "controls": {
            "C4_matches_ring_theorem": network_summary["C4"]["with_nonpermutation_exclusions"] == 0,
            "holonomy_rule_exact_on_permutation_patterns": all(s["holonomy_rule_mismatches"] == 0
                                                               for s in network_summary.values()),
            "Z3_constant_and_symmetric": all(
                abs(v["bits"] - math.log2(3)) < 1e-6 and not v["order_matters"]
                for v in many_valued["Z3"]["by_length"].values()),
        },
        "wall_seconds": round(time.time() - started, 1),
        "peak_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
    }
    result["status"] = "passed" if all(result["controls"].values()) else "control_failed"
    (OUT / "result.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({k: result[k] for k in ("status", "controls", "sampled", "wall_seconds")}, indent=1))
    return 0 if result["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
