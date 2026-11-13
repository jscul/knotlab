"""Verify the synthesis against its four accepted authorities and the case census."""
from collections import Counter
from hashlib import sha256
import json
import os
from pathlib import Path


def load(path):
    return json.loads(path.read_text())


def main():
    family = Path(__file__).resolve().parent
    root = family.parents[2]
    manifest = load(family / "manifest.json")
    result = load(family / "result.json")
    proof = (family / "proof.md").read_text()
    assert result["source_contribution"] == manifest["source_contribution"] == 0
    assert manifest["status"] == "Proved"
    bindings = result["bindings"]
    assert bindings == manifest["parent_bindings"]
    for path, expected in bindings.items():
        assert sha256((root / path).read_bytes()).hexdigest() == expected, path

    leaves = result["accepted_results"]
    tickets = [leaf["ticket"] for leaf in leaves]
    assert len(set(tickets)) == len(tickets) == 4
    assert tickets == manifest["dependencies"]
    for leaf in leaves:
        node = load(root / "tickets" / (leaf["ticket"] + ".json"))
        assert node["fields"]["accepted_artifact_id"] == leaf["artifact_id"]
        assert node["fields"]["terminal_artifact"] == leaf["authority"]
        assert leaf["authority"] in bindings and leaf["explanation"] in bindings
        assert leaf["summary"] in proof
        assert os.path.relpath(root / leaf["explanation"], family) in proof

    outcomes_path, = [path for path in bindings if path.endswith("/outcomes.json")]
    receipt = load((root / outcomes_path).with_name("receipt.json"))
    outcomes = load(root / outcomes_path)
    rows = outcomes["rows"]
    assert len({(row["file"], row["line"]) for row in rows}) == len(rows) == 664
    counts = Counter(row["outcome"] for row in rows)
    assert counts == outcomes["totals"] == receipt["totals"] == {
        "exactly_three": 393,
        "eventually_exactly_four": 39,
        "linear": 69,
        "linear_lower_bound_only": 154,
        "larger_sizes_unresolved": 9,
    }
    print(f"Verified four accepted leaves, {len(bindings)} bound files and {len(rows)} cases.")


if __name__ == "__main__":
    main()
