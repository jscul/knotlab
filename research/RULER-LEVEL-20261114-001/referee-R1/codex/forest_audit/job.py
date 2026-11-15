"""Independent truth-table referee for T1 and the across-level application.

No producer code is opened or imported. Inherited referee engines are used
only for cross-checks; the principal model/support/forest logic below is fresh.
"""
from __future__ import annotations

import hashlib
import importlib.util
import itertools as it
import random
import resource
import sys
import time
from collections import Counter, deque
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
OLD = ROOT / "research/LEVEL-REACH-20261114-001/referee-R1/codex"


def canonical(rows):
    out = set()
    for row in rows:
        if len(row) != 3 or len(set(row)) != 3:
            raise ValueError("a knot must have three distinct distinctions")
        out.add(tuple(sorted(row)))
    return sorted(out)


def incidence(rows, n):
    rows = canonical(rows)
    adj = [[] for _ in range(n + len(rows))]
    parent = list(range(len(adj)))
    def find(v):
        while parent[v] != v:
            parent[v] = parent[parent[v]]
            v = parent[v]
        return v
    forest = True
    for j, row in enumerate(rows, n):
        for v in row:
            if v < 0 or v >= n:
                raise ValueError("distinction outside declared carrier")
            adj[v].append(j)
            adj[j].append(v)
            a, b = find(v), find(j)
            if a == b:
                forest = False
            else:
                parent[a] = b
    distances = []
    for u in range(n):
        dist = {u: 0}
        queue = deque([u])
        while queue:
            v = queue.popleft()
            for w in adj[v]:
                if w not in dist:
                    dist[w] = dist[v] + 1
                    queue.append(w)
        distances.append([None if v not in dist else dist[v] // 2 for v in range(n)])
        assert all(dist[v] % 2 == 0 for v in range(n) if v in dist)
    return forest, distances


def truth_bonds(rows, n):
    """Enumerate all models and every candidate support, with exact bitsets.

Non-full supersets of a known minimal non-full support cannot be bonds.
Every other support tests every assignment by intersecting truth-table columns.
No incidence-forest theorem is used in this computation.
"""
    rows = canonical(rows)
    masks = [sum(1 << v for v in row) for row in rows]
    states = [state for state in range(1 << n)
              if all(state & mask not in (0, mask) for mask in masks)]
    if not states:
        return {"states": 0, "bonds": [0], "tested_supports": 1}
    columns = [[0, 0] for _ in range(n)]
    for i, state in enumerate(states):
        for v in range(n):
            columns[v][(state >> v) & 1] |= 1 << i
    all_states = (1 << len(states)) - 1
    bonds, tested = [], 0
    for size in range(1, n + 1):
        for support in it.combinations(range(n), size):
            mask = sum(1 << v for v in support)
            if any(mask & b == b for b in bonds):
                continue
            tested += 1
            cells = [all_states]
            full = True
            for v in support:
                next_cells = []
                for cell in cells:
                    c0, c1 = cell & columns[v][0], cell & columns[v][1]
                    if not c0 or not c1:
                        full = False
                        break
                    next_cells.extend((c0, c1))
                if not full:
                    break
                cells = next_cells
            if not full:
                bonds.append(mask)
    return {"states": len(states), "bonds": bonds, "tested_supports": tested}


def members(mask, n):
    return [v for v in range(n) if (mask >> v) & 1]


def crossing_least(bonds, A, B):
    am = sum(1 << v for v in A)
    bm = sum(1 << v for v in B)
    candidates = [b for b in bonds if b & am and b & bm]
    return min((b.bit_count() for b in candidates), default="none")


def descending_exists(rows, levels, k, s):
    """Literal consecutive-knot meeting definition, independent of BFS."""
    ends = set()
    for i in range(s):
        candidates = {j for j, row in enumerate(rows)
                      if {levels[v] for v in row} == {k + i, k + i + 1}}
        if i:
            candidates = {j for j in candidates
                          if any(set(rows[j]) & set(rows[h]) for h in ends)}
        ends = candidates
    return bool(ends)


def audit_pattern(rows, n, levels=None):
    rows = canonical(rows)
    forest, dist = incidence(rows, n)
    truth = truth_bonds(rows, n)
    violations = []
    pairs = 0
    for u, v in it.combinations(range(n), 2):
        actual = crossing_least(truth["bonds"], [u], [v])
        expected = "none" if dist[u][v] is None else dist[u][v] + 2
        pairs += 1
        if actual != expected:
            violations.append({"pair": [u, v], "distance_knots": dist[u][v],
                               "expected": expected, "actual": actual})
    pair_bonds = [b for b in truth["bonds"] if b.bit_count() == 2]
    triple_bonds = sorted(tuple(members(b, n)) for b in truth["bonds"] if b.bit_count() == 3)
    faithful = not pair_bonds and triple_bonds == rows
    out = {"n": n, "knots": rows, "forest": forest, "states": truth["states"],
           "bonds": [members(b, n) for b in truth["bonds"]],
           "tested_supports": truth["tested_supports"], "pairs": pairs,
           "T1_violations": violations, "faithful": faithful}
    if levels is not None:
        assert len(levels) == n
        assert all(max(levels[v] for v in row) - min(levels[v] for v in row) <= 1 for row in rows)
        out["levels"] = levels
        counts = Counter()
        addresses = []
        for lev in levels:
            addresses.append(format(counts[lev], f"0{lev}b") if lev else "")
            counts[lev] += 1
            assert counts[lev] <= 1 << lev
        out["addresses"] = addresses
        queries = []
        for k in range(min(levels), max(levels)):
            for target in range(k + 1, max(levels) + 1):
                A = [v for v in range(n) if levels[v] == k]
                B = [v for v in range(n) if levels[v] == target]
                actual = crossing_least(truth["bonds"], A, B)
                d = min((dist[a][b] for a in A for b in B if dist[a][b] is not None), default=None)
                chain = descending_exists(rows, levels, k, target - k)
                expected = "none" if d is None else d + 2
                queries.append({"k": k, "s": target - k, "L": actual,
                                "minimum_distance_knots": d, "formula": expected,
                                "descending_chain": chain,
                                "path_without_descending_chain": d is not None and not chain,
                                "match": actual == expected,
                                "chain_iff_distance_s": chain == (d == target - k)})
        out["level_queries"] = queries
    return out


def load_old():
    sys.path.insert(0, str(OLD))
    import fresh_search
    spec = importlib.util.spec_from_file_location("inherited_brute_supports", OLD / "brute_audit/brute_supports.py")
    brute = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(brute)
    return fresh_search, brute


def controls():
    # The detour is also realizable at address levels 1,2,3 with no overfull level.
    fixtures = [
        ("isolates", [], 5, [4, 4, 5, 6, 6]),
        ("one_knot", [(0, 1, 2)], 4, [4, 5, 5, 6]),
        ("two_knot_path", [(0, 1, 2), (2, 3, 4)], 5, [4, 4, 5, 6, 6]),
        ("three_knot_path", [(0, 1, 2), (2, 3, 4), (4, 5, 6)], 7, [4, 4, 5, 5, 6, 7, 7]),
        ("shared_high_degree", [(0, 1, 2), (0, 3, 4), (0, 5, 6), (0, 7, 8)], 10,
         [5, 4, 4, 5, 5, 6, 6, 5, 5, 7]),
        ("disconnected", [(0, 1, 2), (2, 3, 4), (5, 6, 7)], 9,
         [4, 4, 5, 6, 6, 4, 5, 5, 6]),
        ("within_level_detour", [(0, 1, 2), (1, 3, 4), (3, 5, 6)], 7,
         [1, 2, 2, 2, 2, 3, 3]),
        ("nonmonotone_path", [(0, 1, 2), (2, 3, 4), (4, 5, 6), (6, 7, 8)], 9,
         [5, 5, 6, 6, 5, 5, 6, 7, 7]),
        ("duplicate_dedup", [(0, 1, 2), (2, 1, 0), (2, 3, 4)], 6,
         [4, 4, 5, 6, 6, 5]),
        ("negative_shared_two", [(0, 1, 2), (0, 1, 3)], 4, None),
        ("negative_Berge_cycle", [(0, 1, 2), (2, 3, 4), (0, 4, 5)], 6, None),
    ]
    search, brute = load_old()
    out = []
    for name, rows, n, levels in fixtures:
        row = audit_pattern(rows, n, levels)
        row["name"] = name
        targets = [(0, n - 1)]
        if name == "negative_shared_two":
            targets = [(2, 3)]
        if name == "within_level_detour":
            targets = [(0, 5)]
        checks = []
        for u, v in targets:
            fresh = search.search(canonical(rows), n, [u], [v], cap=n, seconds=30)
            inherited = brute.least_bond(canonical(rows), n, [u], [v], cap=n)
            direct = brute.enumerated_bonds(canonical(rows), n, [u], [v])
            actual = crossing_least([sum(1 << v for v in b) for b in row["bonds"]], [u], [v])
            # The earlier SAT enumerator uses an exhausted cap even when none exists.
            normalize = lambda value: "none" if value == f"> {n}" else value
            checks.append({"pair": [u, v], "truth": actual, "fresh_search": fresh,
                           "brute_supports": inherited, "old_truth_table": direct,
                           "all_agree": all(normalize(x["L"]) == actual for x in (fresh, inherited, direct))})
        row["engine_crosschecks"] = checks
        if row["forest"]:
            assert not row["T1_violations"] and row["faithful"]
            assert all(q["match"] and q["chain_iff_distance_s"] for q in row.get("level_queries", []))
        else:
            assert name.startswith("negative_")
        assert all(c["all_agree"] for c in checks)
        out.append(row)
    malformed_rejected = False
    try:
        canonical([(0, 0, 1)])
    except ValueError:
        malformed_rejected = True
    assert malformed_rejected
    return {"fixtures": out, "malformed_rejected": malformed_rejected}


def exhaustive_seven():
    n = 7
    triples = list(it.combinations(range(n), 3))
    counts = Counter()
    violations = []
    for t in range(4):
        for rows in it.combinations(triples, t):
            forest, _ = incidence(rows, n)
            if not forest:
                counts["rejected_cyclic"] += 1
                continue
            row = audit_pattern(rows, n)
            counts["forests"] += 1
            counts[f"forests_{t}_knots"] += 1
            counts["pairs"] += row["pairs"]
            counts["bonds"] += len(row["bonds"])
            counts["truth_projections"] += row["tested_supports"]
            if row["T1_violations"] or not row["faithful"] or not row["states"]:
                violations.append(row)
    return {"n": n, "coverage": "every labelled 3-uniform incidence forest on seven distinctions, including isolates",
            "counts": dict(counts), "violations": violations}


def random_forest(seed):
    rng = random.Random(seed)
    rows, levels = [], []
    target_knots = rng.randint(2, 5)
    for i in range(target_knots):
        if not levels or (rng.random() < 0.20 and len(levels) + 3 + 2 * (target_knots - i - 1) <= 13):
            start = len(levels)
            level = rng.randint(4, 7)
            new = [level, level, level] if rng.random() < .35 else [level, level + 1, level + 1]
            levels.extend(new)
            rows.append((start, start + 1, start + 2))
        else:
            anchor = rng.randrange(len(levels))
            level = levels[anchor]
            choices = [(level, level)]
            if level < 8:
                choices.extend([(level, level + 1), (level + 1, level + 1)])
            if level > 4:
                choices.extend([(level - 1, level), (level - 1, level - 1)])
            a, b = rng.choice(choices)
            start = len(levels)
            levels.extend([a, b])
            rows.append((anchor, start, start + 1))
    if len(levels) < 13 and rng.random() < .5:
        levels.append(rng.randint(4, 8))
    return rows, len(levels), levels


def random_batch(batch):
    rows = []
    for j in range(10):
        seed = 141100 + 10 * batch + j
        pattern, n, levels = random_forest(seed)
        row = audit_pattern(pattern, n, levels)
        row["seed"] = seed
        rows.append(row)
    return {"patterns": rows,
            "violations": [r for r in rows if not r["forest"] or r["T1_violations"] or not r["faithful"]
                           or any(not q["match"] or not q["chain_iff_distance_s"] for q in r["level_queries"])]}


def setup(params):
    pass


def cases():
    yield "controls", {"kind": "controls"}
    yield "exhaustive_seven", {"kind": "exhaustive"}
    for batch in range(12):
        yield f"random_{batch:02}", {"kind": "random", "batch": batch}


def run(case_id, payload):
    started = time.monotonic()
    if payload["kind"] == "controls":
        result = controls()
    elif payload["kind"] == "exhaustive":
        result = exhaustive_seven()
    else:
        result = random_batch(payload["batch"])
    result["resources"] = {"seconds": time.monotonic() - started,
                           "max_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                           "compute_workers": 1}
    return result
