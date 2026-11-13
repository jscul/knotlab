"""Focused consistency and provenance checks for this referee's outputs."""
import hashlib
import json
import platform
import sys
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]


def main():
    def read(name):
        return json.loads((HERE / name).read_text())

    mapping = read("mapping_audit.json")
    certificate = read("certificate_audit.json")
    rates = read("rate_recompute.json")
    knotlab = read("knotlab_nae.json")
    assert mapping["all_checks_pass"] and not mapping["mismatches"]
    census = mapping["census"]
    assert (census["eligible"], census["positive_complete_rays"],
            census["positive_complete_carried"], census["branch_bounded"],
            census["branch_bounded_carried"], census["branch_bounded_uncarried"]) == (664, 226, 20, 432, 320, 112)
    assert len(mapping["mappings"]) == 664
    endpoints = mapping["selected_linear_root_port_endpoint_check"]
    assert endpoints["passed"] and not endpoints["issues"]
    assert len(endpoints["checked_family_indices"]) == 66
    assert endpoints["counts"]["root_port_start_families"] == 66
    rows = certificate["rows"]
    assert len(rows) == 20
    assert set(r["idx"] for r in rows) == set(census["positive_complete_carried_indices"])
    ten = set(certificate["certified_ten"])
    assert ten == set(census["positive_complete_exact_three_indices"])
    assert all(r["G_states"] == list(range(8)) and r["R1_all_eight"] for r in rows)
    for row in rows:
        assert row["G_checked_with_SAT"] and row["R1_checked_with_SAT"]
        if row["idx"] not in ten:
            continue
        assert row["bonds"]
        for bond in row["bonds"]:
            assert bond["states"] == [1, 2, 3, 4, 5, 6]
            assert all(p == list(range(4)) for p in bond["pairs_after_forgetting_each_member"])
            assert not bond["own_member"]["path"]
            assert any(bond["side_member"]["path"])
            p = bond["port_position"]
            assert row["ray_arguments"][p] == p  # all ten use actual fixed points
        assert all(x["states"] == [1, 2, 3, 4, 5, 6] for x in row["other_truncation_checks"])
    assert knotlab["is_knot"]
    assert len(rates["rows"]) == 3
    expected = {105: Fraction(1, 3), 429: Fraction(1), 874: Fraction(2)}
    for row in rates["rows"]:
        assert row["uncapped_table_closed"]
        assert Fraction(row["lambda_true"]) == expected[row["idx"]]
        assert all(Fraction(x) > 0 for x in row["cyclic_component_means"])
        graph = row["ray_graph"]
        accepting = {x["id"]: x["accept_cost"] for x in graph if x["accept_cost"] is not None}
        edges = {x["id"]: {int(w): c for w, c in x["successors"].items()} for x in graph}
        live = set(accepting)
        while True:
            larger = live | {v for v, out in edges.items() if any(w in live for w in out)}
            if larger == live:
                break
            live = larger
        layer = {x["id"]: x["base_cost"] for x in graph if x["base_cost"] is not None and x["id"] in live}
        layers = []
        for depth in range(1, 31):
            layers.append(dict(layer))
            value = min(c + accepting[v] for v, c in layer.items() if v in accepting)
            assert value == row["L_depths_1_to_30"][depth - 1]
            formula = (3 + depth // 3 if row["idx"] == 105 else
                       depth + 3 if row["idx"] == 429 else 2 * depth + 3)
            assert value == formula
            following = {}
            for v, c in layer.items():
                for w, extra in edges[v].items():
                    if w in live:
                        following[w] = min(following.get(w, 10**30), c + extra)
            layer = following
        repeat = row["exact_cost_vector_repeat"]
        a, b = layers[repeat["from_depth"] - 1], layers[repeat["repeated_at_depth"] - 1]
        assert a.keys() == b.keys()
        assert all(b[v] - a[v] == repeat["gain"] for v in a)
        assert repeat["period"] == repeat["repeated_at_depth"] - repeat["from_depth"]
        assert Fraction(repeat["gain"], repeat["period"]) == expected[row["idx"]]
    assert all(r["all_rates_match"] and r["all_finite_values_match"] for r in rates["reference_comparisons"])

    # Check the mathematical difference between fixed slots and rotating slots.
    phase_checks = []
    for args in ((1, 0, 3), (1, 2, 0)):
        for p in range(2 if args[2] == 3 else 3):
            identities = [p]
            for depth in range(1, 7):
                identities.append(args[identities[-1]])
            assert all(x < 3 for x in identities)
            phase_checks.append({"args": args, "slot": p,
                                 "original_top_identity_depths_0_to_6": identities})
    output_names = ["codex_report.md", "certificate_audit.py", "certificate_audit.json", "mapping_audit.py",
                    "mapping_audit.json", "family_inventory.json", "rate_recompute.py",
                    "rate_recompute.json", "validate_audit.py", "knotlab_nae.json"]
    hashes = {name: hashlib.sha256((HERE / name).read_bytes()).hexdigest() for name in output_names}
    notes = [ROOT / "research/TRUE-RATE-20261113-001" / name for name in
             ("true_rate.md", "preregistration.md", "codex_spec.md")]
    notes.extend(sorted((ROOT / "research/TRUE-RATE-20261113-001").glob("advisor_certificate_*.md")))
    notes += [ROOT / "research/BRANCH-DEPTH-20261112-001/depth.md",
              ROOT / "research/TRUE-BOND-20261113-001/true_bond.md"]
    result = {"all_checks_pass": True,
              "independence": "Fresh code relative to the study (V2 reimplementation); AI review, no external replication or human review implied.",
              "checks": {"rule_identity_mappings": 664, "growing_ray_families": 226,
                         "full_G_and_R1": 20, "direct_SAT_bond_families": 10,
                         "bond_truncation_depths": [2, 3, 4], "fresh_exact_rate_families": [105, 429, 874],
                         "matched_finite_rate_reference_cells": 36,
                         "saved_graph_minima_and_exact_vector_period_gain_verified": True,
                         "BRANCH_linear_root_port_endpoint_certificates": 66,
                         "knotlab_NAE_projection_passes": True},
              "rotating_port_identity_controls": phase_checks,
              "output_sha256": hashes,
              "note_sha256": {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in notes},
              "python_executable": sys.executable, "python_version": platform.python_version(),
              "scope_limits": "No study implementation read/imported; no Git mutations or publishing; all writes in this directory. BRANCH outcome proofs inherited, only three of 24 exact rates freshly recomputed."}
    (HERE / "validation.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result["checks"], sort_keys=True))


if __name__ == "__main__":
    main()
