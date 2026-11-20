"""Cross-check the scientific readout against literal junctions and finite censuses."""

from collections import Counter
import json
from pathlib import Path

from motion_stage import load_stage, load_marks


HERE = Path(__file__).resolve().parent
DATA = HERE.parents[2] / "artifacts" / HERE.parent.name / HERE.name


def read(name):
    return json.loads((DATA / (name + ".json")).read_text())


def check_pattern():
    stage = load_stage("R31")
    old = load_stage("R31", 0)
    old_shared = {bit: frozenset(jj) for bit, jj in old.owners.items() if len(jj) == 2}
    sites = {}
    for q in stage.ordinary_quads():
        a, b = [old_shared[bit] for bit in q if bit in old_shared]
        holder, = a & b
        sites[holder] = q
    trace = read("b_updates")["cases"]["R31"]["tests"]
    for sign in (-1, 1):
        sites_on = {(sign * x) % 31 for x in (0, 1, 4)}
        initial = set()
        for x in sites_on:
            initial.symmetric_difference_update(sites[x])
        state = initial.copy()
        seen = set()
        for event in range(124):
            key = frozenset(state)
            assert key not in seen
            seen.add(key)
            assert stage.allowed_change(state)
            assert len(state) == (10, 12, 14, 12)[event % 4]
            fire = sign * (event // 4 + (2, 5, 4, 0)[event % 4]) % 31
            state.symmetric_difference_update(sites[fire])
        assert state == initial
    assert {t["events_executed"] for t in trace} == {124}
    assert all(t["stop"] == "returns_to_initial_state" for t in trace)


def check_enumeration():
    stages = read("patterns")["cases"]
    assert len(stages) == 14
    assert sum(len(row["ordinary_quads"]) for row in stages.values()) == 485
    assert sum(row["ordinary_quad_overlap_edges"] for row in stages.values()) == 650
    assert sum(len(row["target_profiles"]) for row in stages.values()) == 2899
    layers = read("layers")["cases"]
    assert sum(len(c["all_source_launches"]) for c in layers.values()) == 1028
    choices = Counter()
    for row in layers.values():
        choices.update(row["candidate_links_by_number_of_choices"])
    assert choices == {"0": 6244, "1": 15301, "2": 1651, "3": 885}
    b = read("b_updates")
    assert len(b["all_overlap_count_rules"]) == 32
    assert b["background_closed_benchmarks"]["closed_state_count"] == 32768
    assert all(r["completed_visit_budget"] and r["witness"] is None for r in b["radius_search"])
    assert not any(r["some_word_rule_realizes_same_orbit"] for r in b["same_four_phase_orbit_by_radius"][:3])
    assert b["same_four_phase_orbit_by_radius"][3]["some_word_rule_realizes_same_orbit"]
    opposing = next(x for x in b["cases"]["B81"]["tests"] if x["fixture"] == "opposing_pulses")
    collision = next(x for x in opposing["censuses"] if x["separation"] == 12)
    assert collision["complete"] and collision["states"] == 20 and len(collision["terminal_observations"]) == 2
    near = read("nearness")["cases"]
    assert sum(r["all_launches"] for r in near) == 904
    assert sum(r["checked_raw_handoffs"] for r in near) == 944
    assert sum(r["launch_count"] for r in read("transport")["cases"].values()) == 1300
    assert read("minimality_check")["bare_five"]["physical_closed_states"] == 64


def check_scattering():
    cases = read("composed_motion")
    intact, cut = cases["two85"], cases["first_cut85"]
    for case in cases.values():
        assert case["arbitrary_renaming"] and case["distinctions"] == 576
        assert sum(case["launches"].values()) == sum(case["crossed_by_full_anchor"].values())
    assert intact["crossed_by_full_anchor"]["28,54"] == 56
    assert [r["completed_shifts"] for r in intact["outermost_launches"]] == [78, 78]
    assert set(cut["crossed_by_full_anchor"]) == {"none", "54"}
    assert cut["crossed_by_full_anchor"]["54"] == 54
    for name, rows in read("seam_radius").items():
        for row in rows:
            assert len(row["images_at_radius_one"]) == 3
            expected = 3 if name == "first_cut85" and row["seam"] == 28 else 1
            assert len(row["images_at_radius_two"]) == expected


def check_ring_exchange():
    for name, d in (("T4", 4), ("T8", 8), ("T81", 20)):
        r = read("ring_transfer")[name]
        stage = load_stage(name)
        rings = load_marks(name)["ring_edges"]
        assert r["least_ordinary_wedges"] == d + 5
        assert len(r["four_bit_events"]) == 2*d + 10
        state = set(rings[0])
        for move in r["four_bit_events"]:
            event = frozenset(move)
            assert len(event) == 4
            assert any(event in stage.minimum_response(x).supports for x in event)
            state.symmetric_difference_update(event)
            assert stage.allowed_change(state)
        assert state == set(rings[1])
        for mode, group in read("ring_state")[name].items():
            assert group["targets"]["1"] is None and group["targets"]["2"] is None
            assert (group["targets"]["1,2"] is not None) == (mode != "ordinary4")


if __name__ == "__main__":
    check_pattern()
    check_enumeration()
    check_scattering()
    check_ring_exchange()
    print("Two physical 124-event orbits, exact censuses, both holdouts and three shortest transfers passed.")
