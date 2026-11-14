"""Complete the prescribed negative-control G2 quotient reading from saved contexts."""
from pathlib import Path
import json
import sys
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import inputs
import gates
import window

_rows = None


def setup(params):
    global _rows
    if params:
        raise ValueError("no tunable parameters for the fixed 300 negative controls")
    inputs.verify_sources()
    records = gates.latest(HERE / "gate_families_v2")
    _rows = {r["result"]["key"]: r["result"] for r in records.values()
             if r["status"] == "ok" and r["result"].get("kind") == "negative"}
    expected, _ = gates.selections(inputs.load_records())
    if set(_rows) != set(expected):
        raise ValueError("saved negative-control contexts do not cover the fixed 300")


def cases():
    for key in sorted(_rows, key=inputs.carry_order):
        yield key, dict(key=key)


def run(case_id, payload):
    if payload != dict(key=case_id) or case_id not in _rows:
        raise ValueError("case outside the declared 300 controls")
    prep = window.paths.Preparation(json.loads(case_id))
    calls = window.relations.per_call(prep)
    return dict(key=case_id, G2_live=gates.negative_live(prep, calls, _rows[case_id]["result"]["window"]))
