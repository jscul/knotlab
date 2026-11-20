"""Validate cross-study identities, the four surviving rules and all primary claims."""
import hashlib
import json
from pathlib import Path
import sys

import comparison
import specificity
from specificity import DATA, ROOT


def read(name):
    return json.loads((DATA / f"{name}.json").read_text())


def file_hash(path):
    with path.open("rb") as reader:
        return hashlib.file_digest(reader, "sha256").hexdigest()


def verify():
    panel, order, local, steps = map(read, ("growth", "independent", "comparison", "interaction"))
    assert len(panel["cases"]) == 1072
    assert panel["termination_counts"] == {"age_limit": 502, "stall": 298, "junction_cap": 184, "distinction_cap": 88}
    assert list(panel["controls"]["predecessor_completed_frames"].values()) == [7] * 10
    assert panel["controls"]["invariants"]["projection_rank_and_reversed_allocations"] == 80
    path = order["path"]
    assert set(path["fully_colored_confluent_tables"]) == {"PV", "VV", "+V", "-V"}
    assert path["pointwise_old_confluent_tables"] == ["VV"]
    assert (path["all_tables"], path["allowed_inputs"], path["total_birth_orders"],
            path["total_order_and_min_lift_choices"]) == (16, 16, 49152, 388992)
    assert order["closing"]["forcible_extra_bit_fails_K2"]
    rings = read("ring_checks")
    assert (rings["veto_preparations"], rings["veto_updates_per_preparation"]) == (56, 6)
    assert (len(rings["circumferences"]), rings["plus_following_updates_per_length"]) == (8, 8)
    assert steps["growth_sha256"] == file_hash(DATA / "growth.json")
    assert steps["receiver_count_summary"]["changed_pure_birth_counts"] == 0
    assert steps["receiver_count_summary"]["matched_cells"] == 578
    for table, values in local.items():
        for tag, mask in (("quiet", 0), ("loaded", 1)):
            row = steps["run_profiles"][f"J1/source/{table}/{mask}"]["rows"]["1"]
            assert (row["births"], row["distinctions"]) == (values[tag]["births"], values[tag]["distinctions"])
    assert [local["PV"][tag]["ring_bond_balls"]["5"] for tag in ("quiet","loaded")] == [
        dict(knots=15, distinctions=20), dict(knots=18, distinctions=28)]
    spec = read("specificity")
    assert [(s["gap"], s["birth_interaction"]) for s in spec["separation"]] == [(1,-4),(2,-1),(3,0),(4,0),(8,0)]
    histories = spec["same_active_holders"]["later_under_PV"]
    for tag, target in (("rim", [5,341,1011,0]), ("loose_pairs", [5,621,1590,10])):
        assert histories[tag]["levels_age_knots_distinctions_active_loose"][-1] == target
    assert all(row["geometry_matches"] for row in spec["same_active_holders"]["first_round_by_table"].values())
    assert set(row["structure_changed"] for row in spec["one_allowed_four_change"]["tables"].values()) == {False, True}
    assert all((table[0] != table[1]) == row["structure_changed"]
               for table, row in spec["one_allowed_four_change"]["tables"].items())
    old = read("original_marks")
    assert [len(v) for v in old["pairs"].values()] == [120,80,10]
    for kind, values in old["pairs"].items():
        tally = {result: sum(r[-1] == result for r in values) for result in old["counts"][kind]}
        assert tally == old["counts"][kind]
    assert sum(row["equal"] for row in old["counts"].values()) == 56
    assert sum(row["unresolved"] for row in old["counts"].values()) == 154
    balls = read("balls")
    assert balls["growth_sha256"] == steps["growth_sha256"]
    assert balls["traces"] == 1072 and balls["radii"] == [1, 2, 3, 4, 5]
    assert (balls["all_tables_through"], balls["max_age"], balls["later_measurement_knot_limit"]) == (4, 6, 3000)
    assert balls["queries_by_certified_radius"] == {"5": 12867} and balls["literal_profiles"] == 654
    assert file_hash(DATA / balls["gzip_payload"]) == balls["payload_sha256"]
    # The existing canonical gate checks an explicit parity relation, its proper
    # projections, nonemptiness and its number of allowed joint states.
    prior = ROOT / "experiments/MOTION-LAW-20261119-001/MOTION-LAW-20261119-001-E001_rules"
    import importlib.util
    sys.path.insert(0, str(prior))
    descriptor = importlib.util.spec_from_file_location("prior_motion_verification", prior / "verify.py")
    module = importlib.util.module_from_spec(descriptor)
    descriptor.loader.exec_module(module)
    module.check_knot_relations()
    print("Canonical parity checks at arities 3–6, all 16 local contrasts, independent order controls,"
          " funding and size caps, far-end counts, longer original distances and the bond receipt passed.")


if __name__ == "__main__":
    for path, replay in ((DATA / "specificity.json", specificity.main), (DATA / "comparison.json", comparison.main)):
        original = file_hash(path)
        replay()
        assert file_hash(path) == original, path
    verify()
