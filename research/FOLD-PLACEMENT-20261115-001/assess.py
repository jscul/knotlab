"""Compute the frozen stream comparison from paid, per-program receipts."""
from collections import Counter, defaultdict
import gzip
import hashlib
from itertools import combinations
import json
from pathlib import Path
from statistics import median
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
FAMILY = HERE.name + "-E001_fixed_inputs"
DEFAULT = ROOT / "artifacts" / HERE.name / FAMILY
sys.path.insert(0, str(ROOT / "experiments" / HERE.name / FAMILY))
from job import METHODS


def read(path):
    return json.loads(path.read_bytes())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def row_counts(row, expected):
    result = row["result"]
    work = result["work"]
    time = result.get("timing", {})
    hist = result.get("template_computed_arg_histogram", [0, 0, 0, 0])
    return {
        "tasks": 1,
        "exact": int(result.get("truth") == expected and result["status"] == "exact"
                     and result.get("circuit") is not None),
        "wall_ns": row["wall_ns"], "cpu_ns": row["cpu_ns"], "init_ns": row["init_ns"],
        "search_ns": round(time.get("search_seconds", 0) * 1e9),
        "verify_ns": round(time.get("verification_seconds", 0) * 1e9),
        "build_ns": round(time.get("build_seconds", 0) * 1e9),
        "tests": (work.get("binary_placement_trials", 0) + work.get("ternary_placement_tests", 0)
                  + work.get("placement_group_trials", 0)),
        "rejections": (work.get("binary_placement_failures", 0) + work.get("ternary_placement_failures", 0)
                       + work.get("placement_group_failures", 0)),
        "group_trials": work.get("placement_group_trials", 0),
        "group_failures": work.get("placement_group_failures", 0),
        "group_source_reads": work.get("placement_source_bit_reads", 0),
        "quotient_reads": work.get("placement_quotient_bit_reads", 0),
        "packed_group_shifts": work.get("placement_packed_shifts", 0),
        "packed_group_masks": work.get("placement_packed_masks", 0),
        "packed_group_comparisons": work.get("placement_packed_column_comparisons", 0),
        "group_rows_equivalent": work.get("placement_cofactor_rows_equivalent", 0),
        "factor_bit_reads": work.get("factor_truth_bit_reads", 0),
        "uses": result.get("template_uses", 0),
        "uses_0_computed": hist[0], "uses_1_computed": hist[1],
        "uses_2_computed": hist[2], "uses_3_computed": hist[3],
        "physical_nands": result.get("expanded_NANDs") or 0,
        "verified_rows": work.get("verification_rows", 0),
    }


def center(rows):
    return {k: median([r[k] for r in rows]) for k in rows[0]}


def group_opportunities(panel, grades):
    """Count every raw triple that really has a one-bit interface, independently of search order."""
    layouts = []
    for group in combinations(range(9), 3):
        positions = sum(1 << i for i in group)
        mask = sum(1 << row for row in range(512) if row & positions == 0)
        offsets = [sum(((v >> j) & 1) << i for j, i in enumerate(group)) for v in range(8)]
        layouts.append((group, mask, offsets))
    counts = defaultdict(list)
    for row in panel:
        t = row["truth"]
        groups = [g for g, mask, offsets in layouts if len({(t >> shift) & mask for shift in offsets}) == 2]
        if tuple(row["hint"]) not in groups:
            raise ValueError("supplied group does not transmit exactly one bit")
        grade = grades[row["id"]]
        counts[f"{grade['depth']}-{grade['kind']}"].append(len(groups))
    return {"eligible_per_task": len(layouts), "total_one_bit_groups": sum(map(sum, counts.values())),
            "total_triples": len(panel) * len(layouts), "valid_per_case_by_cell": counts}


def assess(out):
    design = read(out / "design.json")
    for name, wanted in design["data"].items():
        if sha(out / name) != wanted:
            raise ValueError("bound data changed: " + name)
    panel = read(out / "panel.json")
    grades = read(out / "grades.json")
    streams = defaultdict(dict)
    cells = defaultdict(list)
    counts = defaultdict(dict)
    all_failures = []
    for line in (out / "results.jsonl").read_text().splitlines():
        receipt = json.loads(line)
        if receipt["status"] != "ok":
            raise ValueError(f"unresolved runner error in {receipt['case']}")
        run = receipt["result"]
        cache, method, repeat = run["cache"], run["method"], run["repeat"]
        if repeat in streams[cache, method]:
            raise ValueError("repeated stream receipt")
        source = out / run["file"]
        if sha(source) != run["sha256"]:
            raise ValueError("raw stream hash mismatch")
        with gzip.open(source, "rt") as handle:
            raw = [json.loads(row) for row in handle]
        totals = Counter()
        partial = defaultdict(Counter)
        vector = []
        for task, row in zip(panel, raw, strict=True):
            if task["id"] != row["id"]:
                raise ValueError("unexpected task order")
            item = row_counts(row, task["truth"])
            if not item["exact"]:
                all_failures.append((cache, method, repeat, row["id"]))
            totals.update(item)
            grade = grades[row["id"]]
            for label in [str(grade["depth"]), f"{grade['depth']}-{grade['kind']}", grade["kind"]]:
                partial[label].update(item)
            shape = json.dumps(grade["normalized_structure"], separators=(",", ":"))
            partial[f"shape/{grade['depth']}/{grade['kind']}/{shape}"].update(item)
            if grade["kind"] == "negative":
                partial["edit-at-hint" if grade["edit_at_hint"] else "edit-away"].update(item)
            work = row["result"]["work"]
            vector.append((item["tests"], item["group_trials"], item["group_failures"],
                           work.get("binary_placement_trials", 0), work.get("ternary_placement_tests", 0),
                           item["uses"], tuple(item[f"uses_{i}_computed"] for i in range(4))))
        totals.update(startup_ns=run["startup_ns"], paid_ns=run["startup_ns"] + totals["wall_ns"],
                      paid_cpu_ns=run["startup_cpu_ns"] + totals["cpu_ns"])
        streams[cache, method][repeat] = totals
        counts[cache, method][repeat] = vector
        for label, row in partial.items():
            cells[cache, method, label].append(row)
    summary = {"warm": {}, "cold": {}}
    by_cell = {"warm": {}, "cold": {}}
    for cache, n in (("warm", 5), ("cold", 3)):
        for method in METHODS:
            run = streams[cache, method]
            if set(run) != set(range(n)):
                raise ValueError(f"incomplete group {cache}, {method}")
            if any(counts[cache, method][0] != counts[cache, method][i] for i in range(1, n)):
                raise ValueError("semantic work differs on repeated deterministic stream")
            summary[cache][method] = center(list(run.values()))
            summary[cache][method]["paid_repeats_ns"] = [run[i]["paid_ns"] for i in range(n)]
            summary[cache][method]["cpu_repeats_ns"] = [run[i]["paid_cpu_ns"] for i in range(n)]
            by_cell[cache][method] = {label: center(v) for (c, m, label), v in cells.items()
                                      if (c, m) == (cache, method)}
            if "-named-" in method:
                flat = method.replace("-named-", "-flat-")
                if counts[cache, method] != counts[cache, flat]:
                    raise ValueError("named vs flat placement search differs: " + method)
    warm = summary["warm"]
    primitive = min((m for m in METHODS if "primitive-blind" in m), key=lambda m: warm[m]["paid_ns"])

    def compare(method, reference):
        a, b = warm[method], warm[reference]
        pct = 100 * (b["paid_ns"] - a["paid_ns"]) / b["paid_ns"]
        wins = sum(x < y for x, y in zip(a["paid_repeats_ns"], b["paid_repeats_ns"], strict=True))
        return {"reference": reference, "percent_saved": pct, "paired_wins": wins,
                "lower_cpu": a["paid_cpu_ns"] < b["paid_cpu_ns"],
                "passes": (not all_failures and pct >= 10 and wins >= 4
                           and a["paid_cpu_ns"] < b["paid_cpu_ns"])}

    decision = {}
    for m in METHODS:
        against = [compare(m, primitive)]
        if m.endswith("-hint"):
            against.append(compare(m, m.removesuffix("-hint") + "-blind"))
        decision[m] = {"comparisons": against, "qualifies": all(test["passes"] for test in against)}
    blind = [m for m in METHODS if m.endswith("-named-blind") and decision[m]["qualifies"]]
    hinted = [m for m in METHODS if m.endswith("-hint") and decision[m]["qualifies"]]
    outcome = "blind" if blind else "hint-only" if hinted else "stop"
    return {"tasks": len(panel), "assignments": 512, "measured_returns": sum(
                int(r["tasks"]) for series in streams.values() for r in series.values()),
            "failures": all_failures, "benchmark": primitive, "decision": outcome,
            "qualifying_blind": blind, "qualifying_hinted": hinted, "comparisons": decision,
            "methods": summary, "cells": by_cell, "group_opportunities": group_opportunities(panel, grades),
            "design_sha256": sha(out / "design.json")}


if __name__ == "__main__":
    out = Path(sys.argv[1]).resolve() if sys.argv[1:] else DEFAULT
    result = assess(out)
    (out / "result.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({k: result[k] for k in ("tasks", "measured_returns", "benchmark", "decision",
                                             "qualifying_blind", "qualifying_hinted")}, indent=2))
