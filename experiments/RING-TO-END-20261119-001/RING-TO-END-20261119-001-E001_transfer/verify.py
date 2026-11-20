"""Replay the ring pulse with exact erasure, symmetry, and asynchronous-order controls."""
from math import factorial
from pathlib import Path
import json
import subprocess
import sys

import sharp_cost

HERE = Path(__file__).resolve().parent
DATA = HERE.parents[2] / "artifacts" / HERE.parent.name / HERE.name


def main():
    replay = subprocess.check_output([sys.executable, "-B", HERE / "transfer.py"])
    measured = json.loads(replay)
    assert measured == json.loads((DATA / "transfer.json").read_text())
    fixtures = measured["fixtures"]
    bare = fixtures["R0"]["six_completed_layers"]
    assert [v["births"] for v in bare["minimum"]] == [10,15,20,25,30,35]
    for name in ("exact_two", "any_pair"):
        assert [v["births"] for v in bare[name]] == [5 * 2**t for t in range(1,7)]
    witness = fixtures["J1"]["one_pair_witness"]
    assert witness["allowed_write_counts_tested"] == {"0": True, "1": False, "2": True}
    assert (witness["second_births_without_pair"], witness["second_births_with_only_pair"]) == (56,58)
    record = json.loads((DATA / "sharp_cost.json").read_text())
    specs = {s["id"]:s for s in json.loads((HERE.parents[2] / json.loads((HERE / "inputs.json").read_text())["source"]).read_text())["cases"]}
    for name, target in record["least_equivariant_total_in_fresh_only_class"].items():
        assert sharp_cost.at_source(specs[name])[0] == target
    assert record["least_equivariant_total_in_fresh_only_class"]["J1"]["held_incidence_births"] == [56,57]
    orders = sharp_cost.delayed_and_atomic(specs["R0"])
    assert json.loads(json.dumps(orders)) == record["bare_orders"]
    assert orders["two_depth_named_linear_orders"] == factorial(30) // 3**10
    assert orders["two_depth_ideals_on_ten_ports"] == 5**10
    print("Five physical sources, whole-source minima, and all two-depth bare causal orders reconciled.")


if __name__ == "__main__":
    main()
