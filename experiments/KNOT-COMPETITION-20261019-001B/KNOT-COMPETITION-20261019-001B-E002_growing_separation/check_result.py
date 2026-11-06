#!/usr/bin/env python3
"""Independent check of the growing-separation test; imports no producer code.

Parses the raw rows, checks the frozen decision fields, and recomputes the
strips counted per triangle and per pair, the strict not-all-equal strip and
the atom chain on at most nine variables through tools/knotlab (Relation,
bonds, ties). A deliberately altered expectation shows the comparison can fail.
"""

from __future__ import annotations

import json
import sys
from collections import Counter
from itertools import combinations, product
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
ARTIFACT = ROOT / "artifacts/KNOT-COMPETITION-20261019-001B/KNOT-COMPETITION-20261019-001B-E002_growing_separation"
sys.path.insert(0, str(ROOT / "tools"))
from knotlab import Relation, bonds, ties  # noqa: E402


def strip_pairs(n: int) -> Counter:
    weights: Counter = Counter()
    for i in range(n - 2):
        for a, b in combinations((i, i + 1, i + 2), 2):
            weights[(a, b)] += 1
    return weights


def least_states(n: int, cost) -> list[tuple[bool, ...]]:
    states = list(product((False, True), repeat=n))
    values = [cost(x) for x in states]
    low = min(values)
    return [x for x, v in zip(states, values) if v == low]


def separations(n: int, allowed: list[tuple[bool, ...]]) -> list[int]:
    relation = Relation(tuple(f"v{i}" for i in range(n)), frozenset(allowed))
    sep = {}
    for group in list(bonds(relation)) + list(ties(relation)):
        members = sorted(int(v[1:]) for v in group)
        for pair in combinations(members, 2):
            sep[pair] = min(sep.get(pair, 99), len(group))
    return sorted(set(sep.values()))


def main() -> int:
    result = json.loads((ARTIFACT / "result.json").read_text())
    rows = [json.loads(line) for line in (ARTIFACT / "raw_rows.jsonl").read_text().splitlines()]
    assert len(rows) == result["rows"] == 53
    assert result["status"] == "passed" and result["compilation_ok"] is True
    assert result["positive_control_levels"] == [2, 3, 4, 5, 6]
    assert result["H_grow"] is True and result["H_flat"] is False
    by = {(r["family"], r["n"]): r for r in rows}

    checked = 0
    for n in range(5, 10):
        weights = strip_pairs(n)
        per_triangle = least_states(n, lambda x: sum(w for (a, b), w in weights.items() if x[a] == x[b]))
        per_pair = least_states(n, lambda x: sum(1 for (a, b) in weights if x[a] == x[b]))
        nae = [x for x in product((False, True), repeat=n)
               if all(len({x[i], x[i + 1], x[i + 2]}) == 2 for i in range(n - 2))]
        assert sorted(per_triangle) == sorted(nae), n
        assert separations(n, per_triangle) == by[("strip_per_triangle", n)]["separations"], n
        assert separations(n, per_pair) == by[("strip_per_pair", n)]["separations"], n
        assert len(per_pair) == by[("strip_per_pair", n)]["allowed"], n
        checked += 3
    for n in (5, 7, 9):
        chain = [x for x in product((False, True), repeat=n)
                 if all(not (x[i] and x[i + 1] and not x[i + 2]) for i in range(0, n - 2, 2))]
        assert separations(n, chain) == by[("atom_chain_control", n)]["separations"], n
        checked += 1

    # The comparison can fail: the per-pair strip on six variables is not the growing one.
    assert by[("strip_per_pair", 6)]["separations"] != by[("strip_per_triangle", 6)]["separations"]
    print(f"confirmatory result structure passed; {checked} rows recomputed through tools/knotlab "
          "(V0 parse and V1 recomputation; no theorem authority)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
