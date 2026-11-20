"""Cross-check numerical claims shared by the independent arms of this study."""

import json
import os
import subprocess
import sys
from collections import Counter
from itertools import product

from sources import DATA, ROOT


def read(name):
    return json.loads((DATA / (name + ".json")).read_text())


def check_knot_relations():
    # Each clause excludes one odd assignment. Every proper projection is full
    # because a forgotten distinction can complete the parity of the others.
    for size in range(3, 7):
        names = [f"x{i}" for i in range(size)]
        clauses = [" ".join(("~" if bit else "") + name for name, bit in zip(names, word))
                   for word in product((0, 1), repeat=size) if sum(word) % 2]
        arguments = [sys.executable, "-B", "-m", "knotlab", "check", "--cnf", ";".join(clauses),
                     "--loops", *names[:-1], "--contact", names[-1], "--json"]
        out = subprocess.check_output(arguments, env={**os.environ, "PYTHONPATH": str(ROOT / "tools")})
        result = json.loads(out)
        assert result["is_knot"] and len(result["allowed"]) == 2**(size-1)


def check_selection():
    counts = read("rule_census")
    assert [counts["local_radius"][k]["rule_count"] for k in ("1", "2")] == [64, 1048576]
    for k, expected in (("1", (6, 8)), ("2", (22, 80))):
        row = counts["local_radius"][k]["counts_over_all_rules"]
        assert (row["commutes"], row["enabled_diamond"]) == expected
    oriented = counts["oriented_disagreement_conservation"]["counts"]
    assert (oriented["persistent"], oriented["persistent_and_complemented"],
            oriented["persistent_and_reflected"]) == (7, 3, 1)
    radii = read("radius_boundary")
    assert [row["model_count"] for row in radii["radii"]] == [1, 1, 16, 386016]
    compact = radii["radius_four_bounded_compact_motion_search"]
    assert compact["entire_window_completed"] and compact["starts_exhausted_without_a_translation"] == 128
    wide = read("compact_window")["expanded_window"]
    assert wide["verdict"] == "completed" and wide["witness"] is None
    assert (wide["initial_span_cap"], wide["event_cap"], wide["completed_negative_starts_including_reflections"]) == (12, 16, 2048)
    obstruction = read("no_repair_audit")
    assert (obstruction["counts"]["closed_facts"], obstruction["counts"]["closed_states"]) == (340, 184)
    conflict = obstruction["contradiction"]
    assert (conflict["forced_extra_event"], conflict["sole_declared_event"]) == (7, 8)
    for row in read("propagation")["scattering"]["cases"][:2]:
        assert (row["reachable_states"], row["commuting_event_pairs"]) == (625, 554)


def check_geometry():
    pairs = read("port_pairings")
    assert len(pairs) == 16 and sum(row["source_knots"] for row in pairs.values()) == 638
    census = Counter()
    for row in pairs.values():
        for loc in row["counts"]:
            census[loc["radius"], loc["degree"], loc["matchings"]] += loc["knots"]
    assert census[2, 2, 1] == 595 and census[2, 1, 0] == 28
    assert (census[1, 4, 0], census[2, 4, 1], census[2, 4, 0]) == (15, 13, 2)
    physical = read("permutation_controls")
    assert sum(row["allowed_assignments"] for row in physical["two_knot_controls"]) == 2032
    unnamed = physical["different_after_forgetting_names"]
    assert all((row["support_before"], row["support_after"]) == (4, 6) for row in unnamed)
    assert sum(row["all_assignments_exhausted"] for row in unnamed) == 2560
    moving = read("decorated_transport")
    assert moving["overlap_proof"] == {"overlapping_words": 224, "coenabled_overlaps": 4}
    for size in (9, 81):
        for row in moving[str(size)]["rows"]:
            assert row["shifts"] == size and row["events"] == 2 * size
            if size == 9:
                assert (row["code_states"], row["coenabled_pairs"]) == (512, 216)
    ends = read("holdout_landmarks")["cases"].values()
    assert sum(len(row["launches"]) for row in ends) == 306
    assert sum(row["phase_a_readings"] for row in ends) == 9524
    assert sum(row["unit_translations_with_both_endpoint_readings"] for row in ends) == 9218
    assert all(not row["unreachable_landmarks"] for row in ends)


def check_switch():
    uniform = read("uniform_exchange")["cases"]
    early = read("exchange")["cases"]
    assert {v["separation_old_knot_steps"] for v in uniform.values()} == {4, 8, 20, 31, 32, 47, 80, 97}
    for name, v in uniform.items():
        d = v["separation_old_knot_steps"]
        for row in v["sampled_orders"]:
            assert row["ordinary"] == row["cleanup"] == d+5 and row["exact_target"] == v["target"]
        assert all(row["matched_menus"] == 2*d+11 for row in v["neighborhood_verification"])
        assert v["max_observed_dynamic_full_holder_steps"] <= 8
        if name in early:
            assert early[name]["minimal_trace"]["minimum_events"] == 2*d+10
    exact = uniform["T4"]["all_sibling_quotient_outcomes"]
    assert exact["direct_literal_states"] == exact["physical_states_from_exact_sibling_orbit_sizes"] == 365
    assert (exact["direct_literal_transitions"], exact["terminals"], exact["minimum_and_maximum_event_count"]) == (2381, 1, [18, 18])
    assert (exact["quotient_states"], exact["quotient_transitions"]) == (33, 46)
    broader = early["T4"]["exact_interleaved_fair_census"]
    assert (broader["sibling_quotient_states"], broader["quotient_transitions"]) == (5778, 28746)
    approach = early["T81"]["external_approach"]
    assert approach["ordinary_events"] == 104 and approach["separate_release"]["second_ring_intact"]
    assert uniform["d97-arms30-4"]["co_knotted_steps_between_seam_supports"] == 96


if __name__ == "__main__":
    check_knot_relations()
    check_selection()
    check_geometry()
    check_switch()
    print("Verified motion-law, physical exchange and endpoint receipts.")
