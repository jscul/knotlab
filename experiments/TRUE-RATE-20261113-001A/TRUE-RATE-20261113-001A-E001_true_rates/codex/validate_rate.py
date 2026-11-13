"""Bounded requested validation; never the 226-family study.

All outputs stay in CODEX.  Existing validation evidence is not overwritten.
"""
from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import resource
import sys
import time

for name in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ[name] = "1"

from true_rate import (HERE, ROOT, TB_PATH, GRAPH_PATH, REFERENCE_PATH, RAY_REFERENCE_PATH,
                       Budget, RateComputation, graph_module, reference_rows, run_family,
                       study_families, tb_module)


# Ten low-cost families, ordered by own count, completed-reference table size,
# SELF count, and index.  These are validation fixtures, not a random sample.
SMALL_IDS = [429, 212, 105, 470, 549, 973, 441, 989, 1311, 774]


def no_side_control(defs, seconds):
    """Delete every SELF after the first in a fresh in-memory definition."""
    own = []
    seen = False
    for callee, args in defs[0][2]:
        if callee == "SELF":
            if seen:
                continue
            seen = True
        own.append((callee, tuple(args)))
    changed = [(3, defs[0][1], own)]
    true = run_family("hand_no_side_from_429", defs=changed, seconds_limit=seconds)
    path = GRAPH_PATH.parent / "ray_dp.py"
    spec = importlib.util.spec_from_file_location("true_rate_validation_bd_ray", path)
    ray = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = ray
    spec.loader.exec_module(ray)
    dp = ray.FamilyDP(changed)
    budget = Budget(time.monotonic() + seconds)
    starts = dp.start_nodes()
    nodes = list(starts)
    ids = {summary: i for i, summary in enumerate(nodes)}
    adj, closing = [], []
    cursor = 0
    while cursor < len(nodes):
        budget.check()
        edges = []
        for _, target, cost in dp.middle(nodes[cursor]):
            if target not in ids:
                if len(nodes) >= 50_000:
                    raise RuntimeError("validation-only BD ray graph cap")
                ids[target] = len(nodes)
                nodes.append(target)
            edges.append((ids[target], cost))
        adj.append(edges)
        closing.append(dp.close(nodes[cursor]))
        cursor += 1
    result = graph_module().analyze_graph(adj, closing, [None] * len(nodes), True, budget.check)
    layer = {ids[summary]: cost for summary, cost in starts.items()}
    values = []
    for s in range(12):
        budget.check()
        value = min((cost + closing[node] for node, cost in layer.items()
                     if closing[node] < ray.INF), default=math.inf)
        values.append(None if math.isinf(value) else value)
        following = {}
        for source, cost in layer.items():
            for target, weight in adj[source]:
                candidate = cost + weight
                if candidate < following.get(target, math.inf):
                    following[target] = candidate
        layer = following
    return {"source_idx": 429, "defs": changed, "true": true,
            "ray": {"lambda": result["lambda"], "nodes": len(nodes), "L": values},
            "pass": true["closed"] and true["complete"] and true["analysis_complete"]
            and true["lambda_true"] == result["lambda"] and true["L"] == values,
            "comparator": "BD ray DP, via PROVED-RATE's literal-equivalent ray_dp.py"}


def focused_checks():
    checks = []
    for idx in [429, 212]:
        budget = Budget(time.monotonic() + 10)
        state = RateComputation(study_families()[idx], budget)
        for round_number in range(1, 4):
            expected = state.dp.combine([state.table] * state.dp.nchild, math.inf)
            observed = {}
            for summary, cost in state._generic_round():
                observed[summary] = min(cost, observed.get(summary, math.inf))
            equal = observed == expected
            checks.append({"name": "streaming_table_equals_TB", "idx": idx,
                           "round": round_number, "pass": equal, "generated": len(observed)})
            for summary, cost in observed.items():
                state.table[summary] = min(cost, state.table.get(summary, math.inf))
    cases = [
        ("trim_excludes_nonaccepting_zero_cycle", [[(1, 2), (2, 0)], [(1, 3)], [(2, 0)]],
         [math.inf, 1, math.inf], "3/1", False, False, 2),
        ("zero_cycle", [[(1, 0)], [(2, 0)], [(1, 0)]],
         [math.inf, math.inf, 1], "0/1", True, False, 3),
        ("acyclic", [[(1, 2)], []], [math.inf, 4], None, False, True, 2),
        ("rational_mean", [[(1, 0)], [(0, 1)]], [1, math.inf], "1/2", False, False, 2),
    ]
    for name, adj, closing, expected, zero, acyclic, trimmed in cases:
        state = RateComputation(study_families()[429], Budget(time.monotonic() + 5))
        state.nodes = list(range(len(adj)))
        state.adj, state.close_cost = adj, closing
        state.complete = state.closed = True
        result = state.analyze()
        checks.append({"name": name, "result": result,
                       "pass": result["lambda_true"] == expected and result["zero_cycle"] == zero
                       and result["acyclic"] == acyclic and result["trimmed_nodes"] == trimmed})
    partial = run_family(429, seconds_limit=10, table_limit=1)
    checks.append({"name": "table_cap_retains_upper_bound", "result": partial,
                   "pass": partial["closed"] is False and partial["table_size"] == 2
                   and partial["table_reason"] == "summary_cap" and partial["upper_bound"] is True
                   and partial["analysis_complete"] and Fraction(partial["lambda_true"]) >= 1})
    capped = run_family(429, seconds_limit=10, node_limit=2)
    checks.append({"name": "node_cap_safe_partial_graph", "result": capped,
                   "pass": capped["complete"] is False and capped["nodes"] == 2
                   and capped["graph_reason"] == "node_cap" and capped["upper_bound"] is True
                   and capped["analysis_complete"]})
    tiny = run_family(429, seconds_limit=1e-6)
    checks.append({"name": "time_limit_no_invented_rate", "result": tiny,
                   "pass": tiny["upper_bound"] and tiny["lambda_true"] is None
                   and tiny["analysis_complete"] is False})
    return checks


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seconds-limit", type=float, default=30)
    parser.add_argument("--panel-seconds", type=float, default=30)
    parser.add_argument("--output", default="validation.json")
    args = parser.parse_args()
    if not (0 < args.seconds_limit <= 60 and 0 < args.panel_seconds <= 60):
        parser.error("bounded validation budgets must be in (0, 60]")
    output = (HERE / args.output).resolve()
    if output.parent != HERE or output.exists():
        parser.error("use a fresh filename directly inside CODEX")
    limit = 2304 * 1024 ** 2
    resource.setrlimit(resource.RLIMIT_AS, (limit, limit))
    started = time.monotonic()
    references = reference_rows()
    ray_rows = {r["idx"]: r for r in map(json.loads, RAY_REFERENCE_PATH.read_text().splitlines())}
    data = {"scope_kind": "ticket", "scope_id": "TRUE-RATE-20261113-001A",
            "kind": "bounded_implementation_validation", "full_study_run": False,
            "depth_convention": "uniform_depth (thread-settled)", "small_ids": SMALL_IDS,
            "small_families": [], "conditional_depth7_panel": [],
            "source_sha256": {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                              for p in [TB_PATH, GRAPH_PATH, REFERENCE_PATH, RAY_REFERENCE_PATH,
                                        HERE / "true_rate.py", HERE / "validate_rate.py"]}}

    def save():
        data["seconds"] = round(time.monotonic() - started, 6)
        temporary = output.with_suffix(".json.tmp")
        temporary.write_text(json.dumps(data, indent=2, sort_keys=True, allow_nan=False) + "\n")
        temporary.replace(output)

    for idx in SMALL_IDS:
        row = run_family(idx, seconds_limit=args.seconds_limit)
        data["small_families"].append(row)
        print(json.dumps({"section": "small_gate", "idx": idx, "status": row["status"],
                          "closed": row["closed"], "complete": row["complete"],
                          "gate_ok": row["gate_ok"], "lambda_true": row["lambda_true"],
                          "seconds": row["seconds"]}), flush=True)
        save()
    data["small_gate_pass"] = all(row["closed"] and row["complete"] and row["gate_ok"] is True
                                   and row["gate_checked"] == 12 and row["analysis_complete"]
                                   for row in data["small_families"])
    data["focused_checks"] = focused_checks()
    data["focused_checks_pass"] = all(row["pass"] for row in data["focused_checks"])
    try:
        data["no_side_control"] = no_side_control(study_families()[429], args.seconds_limit)
    except Exception as exc:
        data["no_side_control"] = {"pass": False, "error": f"{type(exc).__name__}: {exc}"}
    at_seven = []
    by_seven = []
    for idx, row in references.items():
        deficits = [None if a is None or b is None else b - a
                    for a, b in zip(row["L"], row["L_ray"])]
        if any(value is not None and value >= 3 for value in deficits[:7]):
            by_seven.append(idx)
        if deficits[6] is not None and deficits[6] >= 3:
            at_seven.append(idx)
    data["deficit_selection"] = {"by_depth7_ids": sorted(by_seven),
                                  "at_depth7_ids": sorted(at_seven),
                                  "requested_four_identification": "ambiguous",
                                  "interpretation_selected": False}
    # Report the numerically identifiable four as a CONDITIONAL panel; do not
    # silently assert that this resolves the user's 'by depth 7' wording.
    for idx in sorted(at_seven):
        row = run_family(idx, seconds_limit=args.panel_seconds)
        data["conditional_depth7_panel"].append(
            {"idx": idx, "true": row, "lambda_ray": ray_rows[idx]["lambda"],
             "lambda_ray_complete": ray_rows[idx]["complete"]})
        print(json.dumps({"section": "conditional_depth7", "idx": idx,
                          "status": row["status"], "lambda_true": row["lambda_true"],
                          "upper_bound": row["upper_bound"], "lambda_ray": ray_rows[idx]["lambda"],
                          "seconds": row["seconds"]}), flush=True)
        save()
    data["complete_requested_validation"] = False  # four-family identity remains ambiguous
    save()
    print(json.dumps({"small_gate_pass": data["small_gate_pass"],
                      "focused_checks_pass": data["focused_checks_pass"],
                      "no_side_pass": data["no_side_control"]["pass"],
                      "seconds": data["seconds"]}), flush=True)
    return 0 if (data["small_gate_pass"] and data["focused_checks_pass"]
                 and data["no_side_control"]["pass"]) else 1


if __name__ == "__main__":
    raise SystemExit(main())
