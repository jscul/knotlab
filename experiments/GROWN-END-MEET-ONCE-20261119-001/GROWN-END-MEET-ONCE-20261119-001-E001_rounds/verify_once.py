"""Independently replay the seven-junction meet-once witness."""

from collections import Counter
from hashlib import sha256
import json
from pathlib import Path

from readings import ROOT, bond_readings
from verify import Arrangement, check, exact_table  # imported after readings adds the archived verifier directory


def audit_supports(supports):
    stage = Arrangement.parse(supports)
    meeting_counts = Counter(tuple(holders) for holders in stage.owners.values() if len(holders) == 2)
    assert all(n == 1 for n in meeting_counts.values())
    tables, bonds, _ = bond_readings(stage)
    assert all(len(s) >= 3 for s in stage.stars)
    assert set(stage.masks) <= set(bonds), "a junction support has a nontrivial parity on a proper subset"
    return tables[1], {"junctions": len(stage.stars), "distinctions": len(stage.labels),
                       "bonds_by_support_minimal_xor": len(bonds), "pair_entries": len(tables[1]),
                       "meets_once": True, "all_junction_supports_are_bonds": True}


def audit(witness):
    start, current, following = witness["stages"]
    pairs_start, stage_start = audit_supports(start)
    pairs_current, stage_current = audit_supports(current)
    pairs_next, stage_next = audit_supports(following)
    for supports, expected in ((start, pairs_start), (current, pairs_current), (following, pairs_next)):
        assert exact_table(Arrangement.parse(supports), 100_000)[0] == expected
    x, y = witness["exchanged"]
    partner = witness["distinctions_at_the_four_junctions"]["AD"]
    swap = {x: y, y: x}
    labels = Arrangement.parse(current).labels
    permutation = {i: swap.get(i, i) for i in labels}
    case = {"a": {"start": start, "current": current, "next": following}, "permutation": permutation}
    result = check(case, 100_000, unrestricted=True)
    assert result["current_tables_match"] and result["reading"]["keeps_reading"] and result["reachable_a"]
    assert all(permutation[i] == i for s in Arrangement.parse(current).live for i in current[s])
    assert len(result["extensions"]) == 4
    for variant in ("fixes_given_old_mapping", "allows_within_parent_repair", "also_matches_round_junctions"):
        assert result["extensions"][variant] is None
    assert result["extensions"]["unrestricted_next_matching"]
    assert {x, y, partner}.isdisjoint(Arrangement.parse(current).loose)
    targets = [tuple(sorted((a, partner))) for a in (x, y)]
    distances = {"current": [pairs_current[pair] for pair in targets], "next": [pairs_next[pair] for pair in targets]}
    for key, table, pairs in (("current", stage_current, pairs_current), ("next", stage_next, pairs_next)):
        assert distances[key] == witness["tables"][key]["D_02_and_D_12"]
        assert table["bonds_by_support_minimal_xor"] == witness["tables"][key]["bond_count"]
        assert table["pair_entries"] == witness["tables"][key]["pair_count"]
        table_digest = sha256(json.dumps(list(pairs.values()), separators=(",", ":")).encode()).hexdigest()
        assert table_digest == witness["tables"][key]["lexicographic_distance_table_sha256"]
        table["verified_production_full_table_sha256"] = table_digest
    return {"start": stage_start, "current": stage_current, "next": stage_next, "distances": distances,
            "pair_methods_agree_on_all_stages": True, "all_live_supports_fixed_pointwise": True,
            "verification": result}


def main():
    experiment = Path(__file__).resolve().parent
    source = ROOT / "artifacts" / experiment.parent.name / experiment.name / "two_histories.json"
    data = json.loads(source.read_text())
    print(json.dumps(audit(data["seven_at_round_one"]), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
