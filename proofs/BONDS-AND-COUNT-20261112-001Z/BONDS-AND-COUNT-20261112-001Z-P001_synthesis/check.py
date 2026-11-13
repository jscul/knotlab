"""Check the closure against the five accepted leaf authorities."""
from hashlib import sha256
import json
import os
from pathlib import Path


def read_json(path):
    return json.loads(path.read_text())


def main():
    family = Path(__file__).resolve().parent
    root = family.parents[2]
    result = read_json(family / "result.json")
    manifest = read_json(family / "manifest.json")
    proof = (family / "proof.md").read_text()
    assert result["source_contribution"] == manifest["source_contribution"] == 0
    assert manifest["status"] == "Proved"
    assert result["bindings"] == manifest["parent_bindings"]
    for path, expected in result["bindings"].items():
        assert sha256((root / path).read_bytes()).hexdigest() == expected, path

    leaves = result["accepted_results"]
    tickets = [leaf["ticket"] for leaf in leaves]
    assert len(tickets) == len(set(tickets)) == 5
    assert tickets == manifest["dependencies"]
    for leaf in leaves:
        node = read_json(root / "tickets" / (leaf["ticket"] + ".json"))
        assert node["status_class"] == leaf["status_class"]
        assert node["fields"]["accepted_artifact_id"] == leaf["artifact_id"]
        assert node["fields"]["terminal_artifact"] == leaf["authority"]
        for key in ("authority", "explanation"):
            assert leaf[key] in result["bindings"], leaf[key]
        assert leaf["summary"] in proof
        assert os.path.relpath(root / leaf["explanation"], family) in proof
    print(f"{len(tickets)} accepted leaves and {len(result['bindings'])} bound files verified")


if __name__ == "__main__":
    main()
