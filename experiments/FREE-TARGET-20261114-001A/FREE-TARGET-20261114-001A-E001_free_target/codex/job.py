"""Shared-runner job for FREE-TARGET-20261114-001A, one frozen key per case."""
from __future__ import annotations

import gc
import json
from pathlib import Path
import sys
import time

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import inputs
from limits import LimitReached, Limits
import relations

_population = None
_census = None
_paths = None
_params = {}


def setup(params):
    global _population, _census, _paths, _params
    allowed = {"internal_seconds", "memory_bytes", "max_stored_products", "max_levels"}
    unknown = set(params) - allowed
    if unknown:
        raise ValueError(f"unknown job parameters: {sorted(unknown)}")
    _params = dict(internal_seconds=1650.0, memory_bytes=6_000_000_000,
                   max_stored_products=250_000, max_levels=100_000)
    for key, value in params.items():
        _params[key] = float(value) if key == "internal_seconds" else int(value)
    if not 0 < _params["internal_seconds"] <= 1650:
        raise ValueError("internal_seconds must fit the 1800-second outer timeout")
    if not 0 < _params["memory_bytes"] <= 6_000_000_000:
        raise ValueError("internal RSS ceiling must be at most 6 GB inside the 7G worker limit")
    _population = inputs.load_population()
    _census = inputs.load_census(_population["keys"])
    _paths = inputs.load_paths()
    manifest = HERE / "source_manifest.json"
    if not manifest.exists():
        raise ValueError("freeze source_manifest.json before preparing a run")
    source_manifest = json.loads(manifest.read_text())
    for name, expected in source_manifest["sha256"].items():
        if inputs.digest(inputs.ROOT / name) != expected:
            raise ValueError(f"frozen source changed: {name}")


def cases():
    if _population is None:
        raise RuntimeError("setup(params) must run before cases()")
    for key in _population["keys"]:
        yield key, dict(key=key)


def run(case_id, payload):
    if _population is None or payload["key"] != case_id or case_id not in _census:
        raise ValueError("case is not one of the frozen, loaded census keys")
    import bounded
    import independent
    import witness_check

    gc.collect()
    budget = Limits(_params["internal_seconds"], _params["memory_bytes"])
    population_row = next(row for row in _population["rows"] if row["key"] == case_id)
    result = dict(key=case_id, c=population_row["c"],
                  lambda_path=population_row["lambda_path"], L_path=population_row["L_path"],
                  R_i=[], r=None, recurring_word=None, bounded_certificate=None,
                  verdict="unresolved", reason=None, invalid=False,
                  gate_a=None, gate_b=None, gate_c=None, internal_limits=dict(_params))
    prep = None
    try:
        prep = _paths.Preparation(json.loads(case_id))
        result["preparation"] = prep.info()
        calls = relations.per_call(prep, budget.checkpoint)
        result["R_i"] = [{k: v for k, v in call.items() if k != "relation"} for call in calls]
        if len(calls) != population_row["c"]:
            raise ValueError("SELF count differs from the frozen population row")
        try:
            result["semigroup"] = relations.semigroup(
                [call["relation"] for call in calls], budget.checkpoint,
                _params["max_stored_products"], _params["max_levels"])
        except LimitReached as exc:
            result["semigroup"] = dict(complete=False, reason=exc.reason, detail=str(exc))
            result["reason"] = exc.reason
        result["r"] = result["semigroup"].get("r")
        result["recurring_word"] = result["semigroup"].get("recurring_word")
        result["gate_a"] = independent.audit(prep, calls, result["semigroup"], budget.checkpoint)
        if not result["gate_a"]["passed"]:
            result["invalid"] = True
        budget.checkpoint(force=True)
        search = bounded.search(prep, result["recurring_word"], budget.checkpoint)
        result["bounded_search"] = search
        result["bounded_certificate"] = search.get("certificate")
        if not result["bounded_certificate"] and result["reason"] is None:
            result["reason"] = search.get("reason", "no certificate at k <= 5")
        if result["bounded_certificate"]:
            result["gate_b"] = witness_check.check(prep, result["bounded_certificate"], budget.checkpoint)
            result["bounded_certificate"]["witnesses"] = result["gate_b"].get("depths", [])
            result["bounded_certificate"]["witness_features"] = result["gate_b"].get("features", {})
            if not result["gate_b"]["passed"]:
                result["invalid"] = True
        else:
            result["gate_b"] = dict(passed=True, applicable=False, mismatches=[],
                                    detail="no bounded certificate to replay")
    except LimitReached as exc:
        result.update(reason=exc.reason, limit_detail=str(exc))
    except MemoryError:
        # Free temporary state before serializing a conservative incomplete case.
        gc.collect()
        result.update(reason="memory", limit_detail="Python MemoryError")
    finally:
        grow = result["r"] is not None
        bounded_found = result["bounded_certificate"] is not None
        result["gate_c"] = dict(passed=not (grow and bounded_found),
                                mismatches=([dict(detail="both certificates found")] if grow and bounded_found else []))
        result["invalid"] = result["invalid"] or not result["gate_c"]["passed"]
        if bounded_found and result["gate_b"] is None:
            result["gate_b"] = dict(passed=False, applicable=True,
                                    mismatches=[dict(detail="bounded certificate replay did not finish")])
            result["invalid"] = True
        if grow:
            result["verdict"] = "grows"
        elif bounded_found:
            result["verdict"] = "bounded"
        else:
            result["verdict"] = "unresolved"
        if result["verdict"] != "unresolved":
            result["reason"] = None
        result.update(budget.metrics())
    return result
