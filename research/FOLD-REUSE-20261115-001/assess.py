"""Bind inputs before a run, then summarize the returned programs and measured work."""

import argparse
import json
import math
import statistics
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

import panels
from source_fold import DEFAULT_OUT, ROOT, STUDY, canonical, file_sha, write_new

HERE = Path(__file__).resolve().parent
EXP = ROOT / "experiments" / STUDY / (STUDY + "-E001_second_learner")
METHODS = ("first_plain", "first_fold", "median_plain", "median_fold")


def read(path):
    return json.loads(path.read_bytes())


def bind(out):
    sources = [EXP / name for name in ("identity.json", "contract.json", "learner.py", "protocol.py", "job.py")]
    sources.extend(HERE / name for name in ("panels.py", "source_fold.py", "assess.py", "preregistration.md"))
    published_tasks = panels.tasks()
    write_new(out / "panel.json", published_tasks)
    stamp = read(out / "freeze.json")["utc"] if (out / "freeze.json").exists() else datetime.now(timezone.utc).isoformat()
    record = {
        "utc": stamp, "ticket": STUDY, "tasks": len(published_tasks),
        "sources": {str(p.relative_to(ROOT)): file_sha(p) for p in sources},
        "inputs": {name: file_sha(out / name) for name in ("panel.json", "fold.json", "source_cost.json")},
    }
    write_new(out / "freeze.json", record)
    return record


def expression_table(expr, n, dag):
    total = 1 << n
    lanes = (1 << total) - 1
    op, *args = expr
    if op == "input":
        j, = args
        return sum(1 << x for x in range(total) if (x >> j) & 1)
    cols = [expression_table(child, n, dag) for child in args]
    if op == "FOLD":
        regs = cols + [0, lanes]
        for left, right in dag["gates"]:
            regs.append(lanes ^ (regs[left] & regs[right]))
        return regs[dag["output"]]
    a, b = cols
    if op == "AND":
        return a & b
    if op == "OR":
        return a | b
    if op == "XOR":
        return a ^ b
    raise ValueError(f"Unknown expression operation {op}")


def interpret(run, panel, dag):
    row_data = {}
    for raw in run["rows"]:
        task = panel[raw["id"]]
        n = task["n"]
        total = 1 << n
        fit = raw["fit"]
        attempts = raw["attempts"]
        proposed = [expression_table(rec["expr"], n, dag) for rec in attempts]
        if proposed[-1] != task["truth"] or fit["final_expr"] != attempts[-1]["expr"]:
            raise ValueError("Recorded result differs from target")
        if any(expression_table(p["expr"], n, dag) != truth for p, truth in zip(fit["proposals"], proposed, strict=True)):
            raise ValueError("Learner and checker saw different proposals")
        if any(proposed[0] >> x & 1 != label for x, label in raw["examples"]):
            raise ValueError("First proposal was inconsistent with an initial example")
        initial_rows = len(raw["examples"])
        failed = sum(rec["counterexample"] is not None for rec in attempts)
        if failed != len(attempts) - 1 or failed != fit["checker_failures"]:
            raise ValueError("A proposal was left unchecked or a failure dropped")
        holdout_errors = (proposed[0] ^ task["truth"]).bit_count()
        item = {
            "tasks": 1, "initial_labels": initial_rows, "held_rows": total - initial_rows,
            "first_correct_held_rows": total - initial_rows - holdout_errors, "first_exact": int(not holdout_errors),
            "certified_tasks": 1, "final_correct_rows": total, "checks": len(attempts), "failed_checks": failed,
            "verifier_rows": sum(c["rows"] for c in attempts), "verifier_nands": sum(c["nand_evaluations"] for c in attempts),
            "hypotheses_inspected": fit["hypotheses_inspected"],
            "first_fit_label_tests": fit.get("consistency_label_tests", 0),
            "median_order_comparisons": fit.get("order_comparisons", 0),
            "final_uses_fold": int(bool(fit["final_macro_uses"])), "total_output_bytes": raw["output_bytes"],
            "final_physical_gates": attempts[-1]["physical_gates"],
        }
        row_data[raw["id"]] = {
            "work": item, "truth_trace": proposed, "counterexamples": [x["counterexample"] for x in attempts],
            "task_wall_s": raw["wall_ns"] * 1e-9, "check_wall_s": sum(x["wall_ns"] for x in attempts) * 1e-9,
        }
    if set(row_data) != set(panel):
        raise ValueError("A paired task is missing")
    return row_data


def stats(vals):
    return {"median": statistics.median(vals), "range": [min(vals), max(vals)]}


def scientific_rows(rows):
    return {id_: {k: v for k, v in row.items() if not k.endswith("_wall_s")} for id_, row in rows.items()}


def collect(out):
    freeze = bind(out)
    raw = [json.loads(line) for line in (out / "results.jsonl").read_bytes().splitlines()]
    if len(raw) != 12 or len({r["case"] for r in raw}) != 12 or any(r["status"] != "ok" for r in raw):
        raise ValueError("Expected twelve successful, distinct trial records")
    if len({r["result"]["pid"] for r in raw}) != 12:
        raise ValueError("Expected independently constructed catalogues in twelve fresh workers")
    if any(r["job_sha"] != file_sha(EXP / "job.py") or datetime.fromisoformat(r["finished_at"]) < datetime.fromisoformat(freeze["utc"]) for r in raw):
        raise ValueError("Trial predates binding or ran different source")
    panel = {r["id"]: r for r in read(out / "panel.json")}
    dag = read(out / "fold.json")
    source = read(out / "source_cost.json")
    acquisition = source["original_acquisition_wall_s"]
    samples = defaultdict(list)
    groups = {"all": list(panel)}
    groups.update({group: [i for i, t in panel.items() if t["group"] == group] for group in ("positive", "negative", "neutral")})
    for r in raw:
        trial = r["result"]
        samples[trial["method"]].append((trial, interpret(trial, panel, dag)))
    methods = {}
    signatures = {}
    for method in METHODS:
        reps = sorted(samples[method], key=lambda pair: pair[0]["repeat"])
        if [trial["repeat"] for trial, _ in reps] != [0, 1, 2]:
            raise ValueError("Missing independent timing repeat")
        outcomes = scientific_rows(reps[0][1])
        if any(scientific_rows(rows) != outcomes for _, rows in reps[1:]):
            raise ValueError("A method's deterministic proposals changed across repeats")
        signatures[method] = outcomes
        work = {}
        for group, ids in groups.items():
            combined = Counter()
            for i in ids:
                combined.update(outcomes[i]["work"])
            work[group] = dict(combined)
            work[group]["task_wall_s"] = stats([sum(rows[i]["task_wall_s"] for i in ids) for _, rows in reps])
            work[group]["check_wall_s"] = stats([sum(rows[i]["check_wall_s"] for i in ids) for _, rows in reps])
        incurred = acquisition if method.endswith("_fold") else 0
        methods[method] = {
            "work": work, "source_wall_s": incurred,
            "downstream_wall_s": stats([r["downstream_wall_ns"] * 1e-9 for r, _ in reps]),
            "downstream_cpu_s": stats([r["downstream_cpu_ns"] * 1e-9 for r, _ in reps]),
            "setup_wall_s": stats([r["setup_wall_ns"] * 1e-9 for r, _ in reps]),
            "full_wall_s": stats([incurred + r["downstream_wall_ns"] * 1e-9 for r, _ in reps]),
        }
    changes = {}
    for group, ids in groups.items():
        pairs = [(signatures["first_fold"][i]["work"]["checks"], signatures["first_plain"][i]["work"]["checks"]) for i in ids]
        changes[group] = {"fewer": sum(x < y for x, y in pairs), "equal": sum(x == y for x, y in pairs),
                          "more": sum(x > y for x, y in pairs)}
    for i in panel:
        a, b = signatures["median_fold"][i], signatures["median_plain"][i]
        if (a["truth_trace"], a["counterexamples"]) != (b["truth_trace"], b["counterexamples"]):
            raise ValueError("Common-order selector changed semantic decisions")
    for n in ("4", "5"):
        if len({r["result"]["catalogues"][n]["unordered_digest"] for r in raw}) != 1:
            raise ValueError("Arms have different sets of hypotheses")

    def extrapolate(selector):
        plain, fold = methods[selector + "_plain"], methods[selector + "_fold"]
        # A unit is 32 further *different* tasks drawn from the same mix, with
        # prebuilt catalogues and identical mean per-task cost. This is a model.
        saved = plain["work"]["all"]["task_wall_s"]["median"] - fold["work"]["all"]["task_wall_s"]["median"]
        setup_gap = acquisition + fold["setup_wall_s"]["median"] - plain["setup_wall_s"]["median"]
        return {"warm_s_saved_per_32": saved, "first_projected_32_task_batches": max(1, math.floor(setup_gap / saved) + 1) if saved > 0 else None}

    record = {
        "schema_version": 1, "artifact_id": STUDY + "-E001", "ticket": STUDY, "kind": "experiment",
        "evidence_stage": "exploratory", "panel_size": len(panel), "methods": methods,
        "primary_checks_paired": changes, "median_semantic_traces_equal": len(panel),
        "hypothesis_counts": {n: c["distinct"] for n, c in raw[0]["result"]["catalogues"].items()},
        "projections": {sel: extrapolate(sel) for sel in ("first", "median")},
        "task_outcomes": signatures,
        "bindings": {file: file_sha(out / file) for file in ("panel.json", "fold.json", "source_cost.json", "freeze.json", "results.jsonl")},
    }
    write_new(out / "result.json", record)
    return record


if __name__ == "__main__":
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("action", choices=("bind", "collect"))
    cli.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = cli.parse_args()
    if args.action == "bind":
        print(json.dumps(bind(args.out), indent=2))
    else:
        result = collect(args.out)
        for method, m in result["methods"].items():
            print(method, m["work"]["all"]["first_exact"], m["work"]["all"]["checks"], m["full_wall_s"])
