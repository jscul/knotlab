"""Shared-runner window job: exactly one case per specified census family."""
from __future__ import annotations

from pathlib import Path
import sys
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import inputs

_records = _keys = _weights = None


def setup(params):
    global _records, _keys, _weights
    if params:
        raise ValueError("the frozen window job takes no tunable parameters")
    _records = inputs.load_records()
    _keys = inputs.population(_records)
    _weights = inputs.weights(_keys)
    if sum(_weights.values()) != 6028:
        raise ValueError("population draw weight differs from frozen 6028")
    inputs.verify_sources()


def cases():
    if _keys is None:
        raise RuntimeError("setup must precede cases")
    for key in _keys:
        yield key, dict(key=key)


def run(case_id, payload):
    import window
    if payload != dict(key=case_id) or case_id not in _weights:
        raise ValueError("case is outside the census population")
    return window.run_family(case_id, _records[case_id], _weights[case_id])
