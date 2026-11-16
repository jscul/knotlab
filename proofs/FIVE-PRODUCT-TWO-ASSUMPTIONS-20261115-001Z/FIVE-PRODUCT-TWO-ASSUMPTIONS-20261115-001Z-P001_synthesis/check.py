"""Verify this synthesis against its named terminal proof families and notes."""
from hashlib import sha256
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[2]


def read(path):
    return json.loads(path.read_text())


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


ledger = read(BASE / "ledger_inputs.json")
scope = ledger["scope_id"]
assert ledger["source_contribution"] == 0
assert {r["ticket"] for r in ledger["accepted_inputs"]} == {scope+"A", scope+"B"}
for row in ledger["accepted_inputs"]:
    node = read(ROOT / "tickets" / (row["ticket"]+".json"))
    assert node["status_class"] == "proved"
    assert node["fields"]["accepted_artifact_id"] == row["artifact_id"]
    for name in ("manifest", "result"):
        assert digest(ROOT / row[name]) == row[name+"_sha256"]
    manifest, result = read(ROOT / row["manifest"]), read(ROOT / row["result"])
    assert manifest["status"] == "Proved" and result["status"] == "passed"
    assert row["claim"] == manifest["claim"] == result["claim"]
for path, expected in read(BASE / "note_inputs.json").items():
    assert digest(ROOT / path) == expected
print(json.dumps({"status":"passed","source_contribution":0,"bound_tickets":[r["ticket"] for r in ledger["accepted_inputs"]]}))
