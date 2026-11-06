#!/usr/bin/env python3
"""Producer for KNOT-COMPETITION-20261019-001B-E002: does competition give growing separation?

Confirmatory exact enumeration over the roster frozen in contract.json:
triangle strips and rings counted per triangle and per pair, the strict
not-all-equal strip, and a strict chain of atoms as the positive control. One
raw row per rule. Self-contained; imports nothing from tools/knotlab or from
E001.

    python3 -B run.py    writes raw_rows.jsonl and result.json under artifacts/
"""

from __future__ import annotations

import json
import resource
import time
from collections import Counter, deque
from itertools import combinations, product
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUT = ROOT / "artifacts" / "KNOT-COMPETITION-20261019-001B" / HERE.name

DIFFER = frozenset({(0, 1), (1, 0)})
NAE = frozenset(t for t in product((0, 1), repeat=3) if len(set(t)) == 2)
ATOM = frozenset(t for t in product((0, 1), repeat=3) if not (t[0] and t[1] and not t[2]))

Rule = tuple[tuple[int, ...], frozenset[tuple[int, ...]], int]  # scope, allowed local states, weight


def costs(n: int, rules: list[Rule]) -> list[int]:
    total = [0] * (1 << n)
    for scope, ok, weight in rules:
        for state in range(1 << n):
            if tuple((state >> v) & 1 for v in scope) not in ok:
                total[state] += weight
    return total


def circuits(n: int, allowed: list[int]) -> list[int]:
    size_allowed = len(allowed)
    free_prev = {0}
    found: list[int] = []
    for k in range(1, n + 1):
        candidates = set()
        for base in free_prev:
            for i in range(n):
                bit = 1 << i
                if base & bit:
                    continue
                cand = base | bit
                if cand in candidates:
                    continue
                rest, ok = cand, True
                while rest:
                    low = rest & -rest
                    if cand ^ low not in free_prev:
                        ok = False
                        break
                    rest ^= low
                if ok:
                    candidates.add(cand)
        free_now = set()
        for cand in candidates:
            if (1 << k) <= size_allowed and len({a & cand for a in allowed}) == (1 << k):
                free_now.add(cand)
            else:
                found.append(cand)
        if not free_now:
            break
        free_prev = free_now
    return found


def layout_steps(n: int, rules: list[Rule]) -> dict[tuple[int, int], int | None]:
    adjacent = [set() for _ in range(n)]
    for scope, _, _ in rules:
        for a, b in combinations(set(scope), 2):
            adjacent[a].add(b)
            adjacent[b].add(a)
    steps = {}
    for source in range(n):
        seen = {source: 0}
        queue = deque([source])
        while queue:
            v = queue.popleft()
            for w in adjacent[v]:
                if w not in seen:
                    seen[w] = seen[v] + 1
                    queue.append(w)
        for target in range(source + 1, n):
            steps[(source, target)] = seen.get(target)
    return steps


def describe(n: int, rules: list[Rule], allowed: list[int]) -> dict[str, object]:
    row: dict[str, object] = {"allowed": len(allowed), "nothing_allowed": not allowed}
    if not allowed:
        return row
    found = circuits(n, allowed)
    sizes = Counter(bin(c).count("1") for c in found)
    separation: dict[tuple[int, int], int] = {}
    for c in found:
        size = bin(c).count("1")
        if size < 2:
            continue
        members = [i for i in range(n) if c >> i & 1]
        for pair in combinations(members, 2):
            if pair not in separation or size < separation[pair]:
                separation[pair] = size
    steps = layout_steps(n, rules)
    by_steps: dict[int, set[int]] = {}
    for pair, step in steps.items():
        if pair in separation and step is not None:
            by_steps.setdefault(step, set()).add(separation[pair])
    ordered = sorted(by_steps.items())
    levels = sorted(set(separation.values()))
    row.update({
        "circuit_sizes": {str(k): v for k, v in sorted(sizes.items())},
        "bonds": sum(v for k, v in sizes.items() if k >= 3),
        "ties": sizes.get(2, 0),
        "separations": levels,
        "levels": len(levels),
        "separation_by_layout_steps": {str(k): sorted(v) for k, v in ordered},
        "never_decreasing": all(max(a[1]) <= min(b[1]) for a, b in zip(ordered, ordered[1:])),
        "from_first_vertex": [separation.get((0, j)) for j in range(1, n)],
    })
    return row


def triangle_rules(n: int, ring: bool, per_triangle: bool) -> list[Rule]:
    count = n if ring else n - 2
    triangles = [(i % n, (i + 1) % n, (i + 2) % n) for i in range(count)]
    weights: Counter = Counter()
    for t in triangles:
        for a, b in combinations(t, 2):
            weights[tuple(sorted((a, b)))] += 1
    return [(pair, DIFFER, w if per_triangle else 1) for pair, w in sorted(weights.items())]


def nae_strip(n: int) -> list[Rule]:
    return [((i, i + 1, i + 2), NAE, 1) for i in range(n - 2)]


def nae_ring(n: int) -> list[Rule]:
    return [((i, (i + 1) % n, (i + 2) % n), NAE, 1) for i in range(n)]


def atom_chain(n: int) -> list[Rule]:
    return [((i, i + 1, i + 2), ATOM, 1) for i in range(0, n - 2, 2)]


def least(n: int, rules: list[Rule]) -> tuple[list[int], int]:
    c = costs(n, rules)
    low = min(c)
    return [s for s, v in enumerate(c) if v == low], low


def strict(n: int, rules: list[Rule]) -> list[int]:
    c = costs(n, rules)
    return [s for s, v in enumerate(c) if v == 0]


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    started = time.time()
    rows = []
    compilation = {}
    for n in range(5, 15):
        for name, rules in (("strip_per_triangle", triangle_rules(n, False, True)),
                            ("strip_per_pair", triangle_rules(n, False, False))):
            allowed, low = least(n, rules)
            rows.append({"family": name, "n": n, "reading": "competition", "least_cost": low,
                         **describe(n, rules, allowed)})
            if name == "strip_per_triangle":
                strict_states = strict(n, nae_strip(n))
                compilation[f"strip{n}"] = allowed == strict_states
                rows.append({"family": "strip_nae_strict", "n": n, "reading": "strict", "least_cost": 0,
                             **describe(n, nae_strip(n), strict_states)})
    for n in range(6, 15):
        for name, rules in (("ring_per_triangle", triangle_rules(n, True, True)),
                            ("ring_per_pair", triangle_rules(n, True, False))):
            allowed, low = least(n, rules)
            rows.append({"family": name, "n": n, "reading": "competition", "least_cost": low,
                         **describe(n, rules, allowed)})
            if name == "ring_per_triangle":
                ring_strict = strict(n, nae_ring(n))
                compilation[f"ring{n}"] = (allowed == ring_strict) if ring_strict else None
    for n in (5, 7, 9, 11, 13):
        rules = atom_chain(n)
        rows.append({"family": "atom_chain_control", "n": n, "reading": "strict", "least_cost": 0,
                     **describe(n, rules, strict(n, rules))})
    wall = time.time() - started
    with (OUT / "raw_rows.jsonl").open("w") as handle:
        for row in rows:
            handle.write(json.dumps(row, sort_keys=True) + "\n")

    def family(name: str) -> list[dict]:
        return [r for r in rows if r["family"] == name]

    control = family("atom_chain_control")
    control_levels = [r["levels"] for r in control]
    control_ok = (all(b >= a for a, b in zip(control_levels, control_levels[1:]))
                  and next(r["levels"] for r in control if r["n"] == 9) >= 3)
    compilation_ok = all(v is not False for v in compilation.values())
    strip = family("strip_per_triangle")
    h_grow = any(r["levels"] >= 3 and r["never_decreasing"] for r in strip)
    table = {name: {str(r["n"]): {"levels": r.get("levels"), "separations": r.get("separations"),
                                   "never_decreasing": r.get("never_decreasing"),
                                   "allowed": r["allowed"], "least_cost": r["least_cost"]}
                    for r in family(name)}
             for name in ("strip_per_triangle", "strip_nae_strict", "strip_per_pair",
                          "ring_per_triangle", "ring_per_pair", "atom_chain_control")}
    result = {
        "schema_version": 1,
        "experiment_id": "KNOT-COMPETITION-20261019-001B-E002",
        "ticket": "KNOT-COMPETITION-20261019-001B",
        "evidence_stage": "confirmatory",
        "raw_rows": str((OUT / "raw_rows.jsonl").relative_to(ROOT)),
        "rows": len(rows),
        "compilation_check": compilation,
        "compilation_ok": compilation_ok,
        "positive_control_levels": control_levels,
        "positive_control_ok": control_ok,
        "H_grow": h_grow,
        "H_flat": all(r["levels"] <= 2 for r in strip),
        "table": table,
        "wall_seconds": round(wall, 2),
        "peak_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        "status": "passed" if compilation_ok and control_ok else "invalid",
    }
    (OUT / "result.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({k: result[k] for k in ("status", "rows", "wall_seconds", "compilation_ok",
                                              "positive_control_levels", "H_grow", "H_flat")}, indent=1))
    return 0 if result["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
