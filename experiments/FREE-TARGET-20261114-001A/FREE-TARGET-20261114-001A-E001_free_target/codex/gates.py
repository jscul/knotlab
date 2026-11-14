"""Run the specified gates without running the full 66-case job."""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import time

import controls
import independent
import inputs
from limits import LimitReached, Limits
import relations


def latest_records(directory):
    latest = {}
    path = Path(directory) / "results.jsonl"
    if path.exists():
        with path.open() as stream:
            for line in stream:
                row = json.loads(line)
                latest[row["case"]] = row
    return latest


def relation_gates(population, paths):
    rows = []
    for key in population["keys"]:
        budget = Limits()
        prep = paths.Preparation(json.loads(key))
        calls = relations.per_call(prep, budget.checkpoint)
        try:
            sem = relations.semigroup([row["relation"] for row in calls], budget.checkpoint)
        except LimitReached as exc:
            sem = dict(complete=False, reason=exc.reason, detail=str(exc))
        audit = independent.audit(prep, calls, sem, budget.checkpoint)
        rows.append(dict(key=key, c=len(calls),
                         R_i=[{k: v for k, v in row.items() if k != "relation"} for row in calls],
                         semigroup=sem, gate_a=audit, **budget.metrics()))
    with (inputs.HERE / "gate_relations.jsonl").open("w") as stream:
        for row in rows:
            stream.write(json.dumps(row, sort_keys=True) + "\n")
    return rows


def mutant_panel(population, paths, which):
    rows = []
    for key in population["keys"][:10]:
        prep = paths.Preparation(json.loads(key))
        flat = prep.flat(prep.S)
        indices = [j for j, (kind, _) in enumerate(flat["calls"]) if kind == prep.S]
        dropped = indices[0 if which == "first" else -1]
        before = relations.per_call(prep)
        after = relations.per_call(prep, drop_side=dropped)
        fresh = independent.derive(prep, dropped_side=dropped)
        mismatches = [dict(call=i, produced=value["hex"], independent=f"0x{independent.packed(table):016x}")
                      for i, (value, table) in enumerate(zip(after, fresh))
                      if value["relation"] != independent.packed(table)]
        changed = [i for i, (old, new) in enumerate(zip(before, after)) if old["hex"] != new["hex"]]
        rows.append(dict(key=key, dropped_flat_call=dropped,
                         R_i_before=[r["hex"] for r in before], R_i_after=[r["hex"] for r in after],
                         changed_calls=changed, mismatches=mismatches))
    changed_count = sum(bool(row["changed_calls"]) for row in rows)
    return dict(selection=f"{which} SELF side relation in the first 10 frozen keys",
                families=rows, changed_families=changed_count,
                passed=changed_count >= 1 and not any(row["mismatches"] for row in rows),
                mismatches=[dict(key=row["key"], **m) for row in rows for m in row["mismatches"]])


def collect(run_dir=None, recompute=False):
    start = time.monotonic()
    population, paths = inputs.load_population(), inputs.load_paths()
    if recompute or not (inputs.HERE / "gate_relations.jsonl").exists():
        rows = relation_gates(population, paths)
    else:
        rows = [json.loads(line) for line in (inputs.HERE / "gate_relations.jsonl").read_text().splitlines()]
    a_mismatches = [dict(key=row["key"], **m) for row in rows for m in row["gate_a"]["mismatches"]]
    if set(row["key"] for row in rows) != set(population["keys"]) or len(rows) != 66:
        a_mismatches.append(dict(detail="gate(a) coverage is not exactly the frozen 66 keys"))
    synthetic = controls.run()
    first_panel = mutant_panel(population, paths, "first")
    last_panel = mutant_panel(population, paths, "last")
    (inputs.HERE / "controls.json").write_text(json.dumps(synthetic, indent=2) + "\n")
    (inputs.HERE / "mutants.json").write_text(json.dumps(first_panel, indent=2) + "\n")
    (inputs.HERE / "mutants_last_call.json").write_text(json.dumps(last_panel, indent=2) + "\n")
    result = dict(population_count=66, controls=synthetic,
                  a=dict(passed=not a_mismatches, families=66,
                         calls=sum(row["c"] for row in rows),
                         certifying_P_r_families=sum(row["semigroup"].get("r") is not None for row in rows),
                         recurring_word_families=sum(row["semigroup"].get("recurring_word") is not None for row in rows),
                         by_family=[dict(key=row["key"], **row["gate_a"]) for row in rows], mismatches=a_mismatches),
                  b=dict(status="pending_smoke", passed=None, mismatches=[]),
                  c=dict(status="pending_smoke", passed=None, mismatches=[]),
                  d=dict(**last_panel, initial_first_call_panel=first_panel,
                         observable="R_i change, as permitted by the user specification"))
    bounded_control_file = inputs.HERE / "bounded_controls.json"
    result["bounded_controls"] = (json.loads(bounded_control_file.read_text())
                                   if bounded_control_file.exists() else
                                   dict(passed=False, mismatches=[dict(detail="bounded controls have not run")]))
    if run_dir is not None:
        from witness_check import check
        all_records = latest_records(run_dir)
        b_rows, c_rows, run_errors = [], [], []
        for key, record in all_records.items():
            if key not in population["keys"]:
                run_errors.append(dict(key=key, detail="runner case is outside the population"))
                continue
            if record["status"] != "ok":
                run_errors.append(dict(key=key, detail="non-ok runner status", status=record["status"]))
                continue
            value = record["result"]
            certificate = value.get("bounded_certificate")
            if certificate is not None:
                budget = Limits()
                checked = check(paths.Preparation(json.loads(key)), certificate, budget.checkpoint)
                b_rows.append(dict(key=key, **checked, **budget.metrics()))
            both = value.get("r") is not None and certificate is not None
            c_rows.append(dict(key=key, passed=not both,
                               mismatches=([dict(detail="both certificates found")] if both else [])))
        bm = [dict(key=row["key"], **m) for row in b_rows for m in row["mismatches"]]
        cm = [dict(key=row["key"], **m) for row in c_rows for m in row["mismatches"]]
        result["b"] = dict(passed=not bm and not run_errors, status="checked_available_certificates",
                           certificates_checked=len(b_rows), by_family=b_rows, mismatches=bm,
                           run_errors=run_errors)
        result["c"] = dict(passed=not cm and not run_errors, status="checked_available_cases",
                           cases_checked=len(c_rows), by_family=c_rows, mismatches=cm,
                           run_errors=run_errors)
        result["run_directory"] = str(Path(run_dir).resolve().relative_to(inputs.ROOT))
    result["seconds"] = round(time.monotonic() - start, 6)
    result["all_applicable_passed"] = all(result[key].get("passed") is True
                                           for key in ("controls", "bounded_controls", "a", "b", "c", "d"))
    (inputs.HERE / "gates.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path)
    parser.add_argument("--recompute-relations", action="store_true")
    args = parser.parse_args()
    result = collect(args.run_dir, args.recompute_relations)
    print(json.dumps({k: ({f: v for f, v in value.items() if f in ("passed", "status", "families", "calls", "certificates_checked", "cases_checked", "changed_families", "mismatches") and not (f == "families" and isinstance(v, list))}
                          if isinstance(value, dict) else value)
                      for k, value in result.items() if k != "run_directory"}, sort_keys=True))
