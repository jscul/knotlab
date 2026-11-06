#!/usr/bin/env python3
"""Producer for KNOT-COMPETITION-20261019-001B-E001: near and far under both readings.

Exploratory exact enumeration over the roster frozen in contract.json. For each
uniform rule and each reading it computes the allowed states, the circuits of
their shape (minimal sets that are not free), and the separation of every pair:
the size of the smallest circuit of size two or more containing it. It then
compares separation with the rule's layout, the path length between variables
that share a rule instance. One raw row per rule and reading. Imports nothing
from tools/knotlab.

    python3 -B run.py    writes raw_rows.jsonl and result.json under artifacts/
"""

from __future__ import annotations

import json
import resource
import time
from collections import Counter, deque
from itertools import combinations, product
from math import gcd
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUT = ROOT / "artifacts" / "KNOT-COMPETITION-20261019-001B" / HERE.name

AGREE = frozenset({(0, 0), (1, 1)})
DIFFER = frozenset({(0, 1), (1, 0)})
TRIPLE_TYPES = {
    "NAE": frozenset(t for t in product((0, 1), repeat=3) if len(set(t)) == 2),
    "EVEN": frozenset(t for t in product((0, 1), repeat=3) if sum(t) % 2 == 0),
    "ODD": frozenset(t for t in product((0, 1), repeat=3) if sum(t) % 2 == 1),
    "OR3": frozenset(t for t in product((0, 1), repeat=3) if any(t)),
    "ATOM": frozenset(t for t in product((0, 1), repeat=3) if not (t[0] and t[1] and not t[2])),
}

Rule = tuple[tuple[int, ...], frozenset[tuple[int, ...]]]


def violation_counts(n: int, rules: list[Rule]) -> list[int]:
    counts = [0] * (1 << n)
    for scope, ok in rules:
        bad = {loc for loc in product((0, 1), repeat=len(scope)) if loc not in ok}
        if not bad:
            continue
        for state in range(1 << n):
            if tuple((state >> v) & 1 for v in scope) in bad:
                counts[state] += 1
    return counts


def circuits(n: int, allowed: list[int]) -> list[int]:
    """Minimal non-free sets of variables (as bitmasks), level by level."""
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


def whole_is_knot(n: int, allowed: list[int]) -> bool:
    if not allowed or len(allowed) == 1 << n:
        return False
    for i in range(n):
        mask = ((1 << n) - 1) ^ (1 << i)
        if len({a & mask for a in allowed}) != 1 << (n - 1):
            return False
    return True


def layout_steps(n: int, rules: list[Rule]) -> dict[tuple[int, int], int | None]:
    adjacent = [set() for _ in range(n)]
    for scope, _ in rules:
        for a, b in combinations(set(scope), 2):
            adjacent[a].add(b)
            adjacent[b].add(a)
    steps: dict[tuple[int, int], int | None] = {}
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
    by_steps: dict[str, list[int]] = {}
    for pair, step in steps.items():
        if pair in separation:
            by_steps.setdefault(str(step) if step is not None else "none", set()).add(separation[pair])
    by_steps = {key: sorted(values) for key, values in sorted(by_steps.items())}
    finite = sorted(set(separation.values()))
    near_and_far = len(finite) >= 2
    ordered = sorted((int(k), v) for k, v in by_steps.items() if k != "none")
    monotone = all(max(a[1]) <= min(b[1]) for a, b in zip(ordered, ordered[1:]))
    layout_levels = sorted({s for s in steps.values() if s is not None})
    row.update({
        "whole_is_knot": whole_is_knot(n, allowed),
        "circuit_sizes": {str(k): v for k, v in sorted(sizes.items())},
        "fixed_variables": sizes.get(1, 0),
        "ties": sizes.get(2, 0),
        "bonds": sum(v for k, v in sizes.items() if k >= 3),
        "pairs_related": len(separation),
        "pairs_unrelated": n * (n - 1) // 2 - len(separation),
        "separations": finite,
        "separation_by_layout_steps": by_steps,
        "layout_step_values": layout_levels,
        "near_and_far": near_and_far,
        "follows_layout": near_and_far and monotone,
        "flattens_layout": (not near_and_far) and len(separation) > 0 and len(layout_levels) >= 2,
    })
    return row


def readings(n: int, rules: list[Rule]) -> dict[str, list[int]]:
    counts = violation_counts(n, rules)
    low = min(counts)
    return {
        "strict": [s for s, c in enumerate(counts) if c == 0],
        "competition": [s for s, c in enumerate(counts) if c == low],
        "least_violations": low,
    }


def canonical_offsets(n: int, signs: dict[int, str]) -> str:
    """Name of the circulant class under the multipliers of Z_n."""
    best = None
    for u in range(1, n):
        if gcd(u, n) != 1:
            continue
        mapped = {}
        for d, s in signs.items():
            e = (u * d) % n
            mapped[min(e, n - e)] = s
        key = tuple(mapped.get(d, "-") for d in range(1, n // 2 + 1))
        best = key if best is None or key < best else best
    return "".join(s[0] if s != "-" else "-" for s in best)


def circulant_pairwise():
    for n in range(4, 11):
        offsets = list(range(1, n // 2 + 1))
        for choice in product(("-", "agree", "differ"), repeat=len(offsets)):
            if all(c == "-" for c in choice):
                continue
            signs = {d: c for d, c in zip(offsets, choice) if c != "-"}
            pairs = {}
            for d, c in signs.items():
                for i in range(n):
                    pair = tuple(sorted((i, (i + d) % n)))
                    pairs[pair] = AGREE if c == "agree" else DIFFER
            rules = [(pair, ok) for pair, ok in sorted(pairs.items())]
            name = "C{}[{}]".format(n, ",".join(f"{d}{'a' if c == 'agree' else 'd'}" for d, c in signs.items()))
            yield {"family": "circulant_pairwise", "name": name, "n": n,
                   "class": f"C{n}:{canonical_offsets(n, signs)}"}, n, rules


def circulant_three_place():
    for n in range(5, 10):
        for a, b in combinations(range(1, n), 2):
            for kind, ok in TRIPLE_TYPES.items():
                rules = [((i, (i + a) % n, (i + b) % n), ok) for i in range(n)]
                yield {"family": "circulant_three_place", "name": f"T{n}[{a},{b}]{kind}", "n": n,
                       "type": kind}, n, rules


def torus_rules(width: int, vectors: list[tuple[int, int]], ok) -> list[Rule]:
    index = lambda x, y: (x % width) + width * (y % width)
    pairs = set()
    for x in range(width):
        for y in range(width):
            for dx, dy in vectors:
                pair = tuple(sorted((index(x, y), index(x + dx, y + dy))))
                pairs.add(pair)
    return [(pair, ok) for pair in sorted(pairs)]


def triangles(width: int) -> list[tuple[int, int, int]]:
    index = lambda x, y: (x % width) + width * (y % width)
    out = []
    for x in range(width):
        for y in range(width):
            out.append((index(x, y), index(x + 1, y), index(x, y + 1)))
            out.append((index(x + 1, y), index(x, y + 1), index(x + 1, y + 1)))
    return out


def lattice_controls():
    for width in (3, 4):
        yield ({"family": "lattice", "name": f"triangular{width}x{width}_differ", "n": width * width},
               width * width, torus_rules(width, [(1, 0), (0, 1), (-1, 1)], DIFFER))
        yield ({"family": "lattice", "name": f"triangular{width}x{width}_nae_triangles", "n": width * width},
               width * width, [(t, TRIPLE_TYPES["NAE"]) for t in triangles(width)])
    yield ({"family": "lattice", "name": "square4x4_differ", "n": 16},
           16, torus_rules(4, [(1, 0), (0, 1)], DIFFER))


def symmetric_controls():
    for n in range(4, 10):
        for kind, ok in (("agree", AGREE), ("differ", DIFFER)):
            yield ({"family": "symmetric", "name": f"K{n}_{kind}", "n": n},
                   n, [(pair, ok) for pair in combinations(range(n), 2)])


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    started = time.time()
    rows = []
    allowed_sets = {}
    for generator in (circulant_pairwise, circulant_three_place, lattice_controls, symmetric_controls):
        for meta, n, rules in generator():
            states = readings(n, rules)
            for reading in ("strict", "competition"):
                row = dict(meta)
                row["reading"] = reading
                row["instances"] = len(rules)
                row["least_violations"] = states["least_violations"]
                row.update(describe(n, rules, states[reading]))
                rows.append(row)
                allowed_sets[(meta["name"], reading)] = states[reading]
    wall = time.time() - started
    with (OUT / "raw_rows.jsonl").open("w") as handle:
        for row in rows:
            handle.write(json.dumps(row, sort_keys=True) + "\n")

    def select(family=None, reading=None):
        return [r for r in rows if (family is None or r["family"] == family)
                and (reading is None or r["reading"] == reading)]

    pairwise_families = ("circulant_pairwise", "lattice", "symmetric")
    strict_pairwise_bonds = [r["name"] for r in rows if r["reading"] == "strict"
                             and r["family"] in pairwise_families and "nae_triangles" not in r["name"]
                             and r.get("bonds", 0) > 0]
    mismatches = []
    by_name: dict[str, dict[str, dict]] = {}
    for r in rows:
        by_name.setdefault(r["name"], {})[r["reading"]] = r
    for name, pair in by_name.items():
        if pair["strict"]["least_violations"] == 0 and \
                allowed_sets[(name, "strict")] != allowed_sets[(name, "competition")]:
            mismatches.append(name)
    rings = [r for r in select("circulant_pairwise", "competition")
             if r["n"] % 2 == 1 and r["name"] == f"C{r['n']}[1d]"]
    ring_control = all(
        r["separations"] == [3] and r["bonds"] == r["n"] * (r["n"] - 1) * (r["n"] - 2) // 6 for r in rings
    ) and all(by_name[r["name"]]["strict"]["nothing_allowed"] for r in rings)
    symmetric_constant = all(len(r.get("separations", [])) <= 1 for r in select("symmetric"))

    def summary(family: str, reading: str) -> dict[str, object]:
        chosen = select(family, reading)
        return {
            "rules": len(chosen),
            "nothing_allowed": sum(r["nothing_allowed"] for r in chosen),
            "with_bonds": sum(r.get("bonds", 0) > 0 for r in chosen),
            "whole_is_knot": sum(bool(r.get("whole_is_knot")) for r in chosen),
            "near_and_far": sum(bool(r.get("near_and_far")) for r in chosen),
            "follows_layout": sum(bool(r.get("follows_layout")) for r in chosen),
            "flattens_layout": sum(bool(r.get("flattens_layout")) for r in chosen),
        }

    signal = sorted({r["class"] for r in select("circulant_pairwise", "competition") if r.get("near_and_far")})
    signal_examples = [
        {k: r[k] for k in ("name", "least_violations", "allowed", "separations", "separation_by_layout_steps",
                           "follows_layout", "bonds", "ties")}
        for r in select("circulant_pairwise", "competition") if r.get("near_and_far")
    ][:12]
    lattice = {r["name"] + ":" + r["reading"]: {k: r.get(k) for k in (
        "allowed", "least_violations", "bonds", "ties", "separations", "separation_by_layout_steps",
        "near_and_far", "follows_layout")} for r in select("lattice")}
    taf_equals = {
        width: allowed_sets[(f"triangular{width}x{width}_differ", "competition")]
        == allowed_sets[(f"triangular{width}x{width}_nae_triangles", "strict")]
        for width in (3, 4)
    }
    result = {
        "schema_version": 1,
        "experiment_id": "KNOT-COMPETITION-20261019-001B-E001",
        "ticket": "KNOT-COMPETITION-20261019-001B",
        "evidence_stage": "exploratory",
        "raw_rows": str((OUT / "raw_rows.jsonl").relative_to(ROOT)),
        "rows": len(rows),
        "theorem_checks": {
            "strict_pairwise_rules_with_bonds": strict_pairwise_bonds,
            "readings_disagree_on_satisfiable_rules": mismatches,
        },
        "controls": {
            "frustrated_rings_flatten": ring_control,
            "frustrated_rings_checked": [r["name"] for r in rings],
            "symmetric_rules_constant_separation": symmetric_constant,
        },
        "summary": {f"{family}:{reading}": summary(family, reading)
                    for family in ("circulant_pairwise", "circulant_three_place", "lattice", "symmetric")
                    for reading in ("strict", "competition")},
        "signal_circulant_pairwise_classes_with_near_and_far": signal,
        "signal_examples": signal_examples,
        "lattice": lattice,
        "triangular_competition_equals_strict_nae_triangles": {str(k): v for k, v in taf_equals.items()},
        "wall_seconds": round(wall, 2),
        "peak_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        "status": "passed" if not strict_pairwise_bonds and not mismatches and ring_control and symmetric_constant
        else "stopped",
    }
    (OUT / "result.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({k: result[k] for k in ("status", "rows", "wall_seconds", "theorem_checks", "controls")},
                     indent=1))
    return 0 if result["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
