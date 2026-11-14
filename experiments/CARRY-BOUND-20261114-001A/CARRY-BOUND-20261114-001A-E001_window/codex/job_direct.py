"""Shared-runner job for the frozen post-path ``sample.json`` direct list.

One case is one selected family and one absolute depth s in 1..6.  The
shared runner owns timeout, worker, memory, retry and durable-output policy.
This module does not launch jobs or write output files itself.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))
import direct
import inputs

_ROWS = None
_KEYS = None
_CONFIG = None
_PROVENANCE = None


def setup(params):
    """Load the frozen direct list; never infer it from incomplete path output.

    Accepted sample shape is a mapping with ``direct`` as a list of keys or
    rows containing keys.  A true ``direct_ready`` flag explicitly establishes
    that the post-path selection is ready; absent readiness is an error.
    """
    global _ROWS, _KEYS, _CONFIG, _PROVENANCE
    allowed = {"sample", "seconds", "seeds", "max_variables", "max_clauses", "max_copies", "depths"}
    unknown = set(params) - allowed
    if unknown:
        raise ValueError(f"unknown direct job parameters: {sorted(unknown)}")
    inputs.verify_sources()
    path = Path(params.get("sample", HERE / "sample.json"))
    if not path.is_absolute():
        path = ROOT / path
    path = path.resolve()
    if not path.is_relative_to(ROOT):
        raise ValueError("sample must be repository material")
    sample = json.loads(path.read_text())
    if not isinstance(sample, dict) or sample.get("direct_ready") is not True:
        raise ValueError("direct sample is not explicitly post-path ready (direct_ready=true)")
    selected = sample.get("direct")
    if not isinstance(selected, list):
        raise ValueError("sample.json direct must be a frozen list")
    keys = []
    sample_rows = {}
    for item in selected:
        key = item if isinstance(item, str) else item.get("key") if isinstance(item, dict) else None
        if not isinstance(key, str):
            raise ValueError("each direct selection must be a key or a row containing key")
        keys.append(key)
        if isinstance(item, dict):
            sample_rows[key] = item
    if len(keys) > 60 or len(keys) != len(set(keys)):
        raise ValueError("direct sample must contain at most 60 unique families")
    if keys != sorted(keys, key=inputs.carry_order):
        raise ValueError("direct sample is not in frozen sha256('CARRY:' + key) order")
    if "depths" in params and str(params["depths"]) != "1,2,3,4,5,6":
        raise ValueError("direct depths are frozen at 1,2,3,4,5,6")
    archive = inputs.load_archive(keys)
    _ROWS = {}
    for key in keys:
        # The raw family and its S identity come from the authorized archive;
        # sample metadata cannot silently replace either one.
        row = dict(sample_rows.get(key, {}), **archive[key])
        row["key"] = key
        _ROWS[key] = row
    _KEYS = tuple(keys)
    _CONFIG = {"seconds": float(params.get("seconds", direct.DEFAULT_SECONDS)),
               "seeds": int(params.get("seeds", direct.DEFAULT_SEEDS)),
               "max_variables": int(params.get("max_variables", 15_000)),
               "max_clauses": int(params.get("max_clauses", 100_000)),
               "max_copies": int(params.get("max_copies", 25_000))}
    if _CONFIG["seconds"] <= 0 or _CONFIG["seeds"] < 0 or any(
            _CONFIG[name] <= 0 for name in ("max_variables", "max_clauses", "max_copies")):
        raise ValueError("invalid direct resource caps")
    _PROVENANCE = {"sample": str(path.relative_to(ROOT)),
        "sample_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "selected_families": len(keys), "depths": list(range(1, 7)),
        "implementation_sha256": {name: hashlib.sha256((HERE / name).read_bytes()).hexdigest()
                                  for name in ("brute.py", "direct.py", "job_direct.py")}}


def cases():
    if _KEYS is None:
        raise RuntimeError("shared runner must call setup(params) before cases()")
    for key in _KEYS:
        digest = hashlib.sha256(key.encode()).hexdigest()
        for s in range(1, 7):
            yield f"{digest}:s={s}", {"key": key, "s": s}


def run(case_id, payload):
    if _ROWS is None:
        raise RuntimeError("shared runner must call setup(params) before run()")
    key, s = payload["key"], int(payload["s"])
    expected = f"{hashlib.sha256(key.encode()).hexdigest()}:s={s}"
    if key not in _ROWS or case_id != expected or s not in range(1, 7):
        raise ValueError("case is outside the frozen direct sample")
    answer = direct.run_case(_ROWS[key], s, **_CONFIG)
    answer["selection"] = _PROVENANCE
    return answer
