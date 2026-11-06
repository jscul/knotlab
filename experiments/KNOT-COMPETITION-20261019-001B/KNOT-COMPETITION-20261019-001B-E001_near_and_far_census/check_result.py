#!/usr/bin/env python3
"""Independent check of the exploratory census; imports no producer code.

Parses the raw rows, checks the frozen theorem checks and controls from them,
and recomputes every circulant pairwise row on at most seven variables, under
both readings, through tools/knotlab (Relation, bonds, ties): a separate code
path from the producer's bitmask search. One row is then deliberately altered
to show that the comparison can fail.
"""

from __future__ import annotations

import json
import sys
from itertools import combinations, product
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
ARTIFACT = ROOT / "artifacts/KNOT-COMPETITION-20261019-001B/KNOT-COMPETITION-20261019-001B-E001_near_and_far_census"
sys.path.insert(0, str(ROOT / "tools"))
from knotlab import Relation, bonds, ties  # noqa: E402


def parse_name(name: str) -> tuple[int, dict[int, str]]:
    head, body = name[1:].split("[")
    signs = {}
    for part in body.rstrip("]").split(","):
        signs[int(part[:-1])] = part[-1]
    return int(head), signs


def allowed_states(n: int, signs: dict[int, str], reading: str) -> list[tuple[bool, ...]]:
    pairs = {}
    for d, s in signs.items():
        for i in range(n):
            pairs[tuple(sorted((i, (i + d) % n)))] = s
    def broken(x):
        return sum((x[i] == x[j]) if s == "d" else (x[i] != x[j]) for (i, j), s in pairs.items())
    states = list(product((False, True), repeat=n))
    counts = [broken(x) for x in states]
    target = 0 if reading == "strict" else min(counts)
    return [x for x, c in zip(states, counts) if c == target]


def recompute(row: dict) -> dict:
    n, signs = parse_name(row["name"])
    allowed = allowed_states(n, signs, row["reading"])
    if not allowed:
        return {"allowed": 0}
    names = tuple(f"v{i}" for i in range(n))
    relation = Relation(names, frozenset(allowed))
    found_bonds = bonds(relation)
    found_ties = ties(relation)
    separation = {}
    for group in list(found_bonds) + list(found_ties):
        members = sorted(int(v[1:]) for v in group)
        for pair in combinations(members, 2):
            separation[pair] = min(separation.get(pair, 99), len(group))
    return {
        "allowed": len(allowed),
        "bonds": len(found_bonds),
        "ties": len(found_ties),
        "separations": sorted(set(separation.values())),
    }


def main() -> int:
    result = json.loads((ARTIFACT / "result.json").read_text())
    rows = [json.loads(line) for line in (ARTIFACT / "raw_rows.jsonl").read_text().splitlines()]
    assert len(rows) == result["rows"] == 1774
    assert result["theorem_checks"] == {
        "strict_pairwise_rules_with_bonds": [], "readings_disagree_on_satisfiable_rules": []}
    assert result["controls"]["frustrated_rings_flatten"] is True
    assert result["controls"]["symmetric_rules_constant_separation"] is True
    pairwise_strict = [r for r in rows if r["family"] == "circulant_pairwise" and r["reading"] == "strict"]
    assert not any(r.get("near_and_far") for r in pairwise_strict)
    assert all(r.get("bonds", 0) == 0 for r in pairwise_strict)
    competition = [r for r in rows if r["family"] == "circulant_pairwise" and r["reading"] == "competition"]
    assert sum(bool(r.get("near_and_far")) for r in competition) == 178
    assert all(len(r["separations"]) <= 2 for r in competition if r.get("near_and_far"))
    assert result["triangular_competition_equals_strict_nae_triangles"] == {"3": True, "4": True}

    checked = 0
    for row in rows:
        if row["family"] != "circulant_pairwise" or row["n"] > 7:
            continue
        mine = recompute(row)
        theirs = {key: row.get(key) for key in mine}
        if row.get("nothing_allowed"):
            theirs = {"allowed": 0}
        assert mine == theirs, (row["name"], row["reading"], mine, theirs)
        checked += 1

    # The comparison can fail: alter one recomputed row.
    sample = next(r for r in rows if r["name"] == "C5[1d]" and r["reading"] == "competition")
    altered = dict(sample, separations=[3, 4])
    assert recompute(sample)["separations"] != altered["separations"]

    print(f"exploratory census structure passed; {checked} rows on at most seven variables recomputed "
          "through tools/knotlab (V0 parse and V1 recomputation; no theorem authority)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
