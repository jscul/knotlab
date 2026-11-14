"""Freeze post-census sample lists from finished runner results only.

Run 'paths' after the 5,964-case window run; run 'direct' after path DP.
Each stage writes its immutable input list before its corresponding job runs.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
import json
from pathlib import Path
import sys
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import inputs
from scope import SyntaxPreparation, identity_cycle, scope
from window import carried_sequence
sys.path.insert(0, str(inputs.ROOT / "scripts"))
from longrun import load_results


def results_file(path):
    path = Path(path).resolve()
    return path / "results.jsonl" if path.is_dir() else path


def freeze_paths(source):
    target = HERE / "sample.json"
    if target.exists():
        raise FileExistsError("preserve existing sample; stages cannot be selected again")
    records = load_results(source)
    if len(records) != 5964:
        raise ValueError("path sampling requires all 5964 final window records")
    selected, cells, missing, ambiguity = [], defaultdict(list), [], []
    cell_by_I_family = []
    for key, record in sorted(records.items(), key=lambda item: inputs.carry_order(item[0])):
        prep = SyntaxPreparation(key)
        if not scope(prep)["in_scope"]:
            continue
        is_I = identity_cycle(prep)
        row = record.get("result") or {}
        cell = None
        if is_I:
            # A5 is syntactic even when a cap or failed runner has no Q_s residues.
            carried = carried_sequence(prep)
            meeting_mask = sum(1 << j for j in carried["knot_meeting_positions"])
            repeating = carried["masks"][carried["preperiod"]:]
            meeting = any(mask & meeting_mask for mask in repeating)
            cell = ("1" if carried["period"] == 1 else "more", "yes" if meeting else "no")
            cell_by_I_family.append(dict(key=key, cell=list(cell), carried=carried))
        if not is_I and (record["status"] != "ok" or not row):
            missing.append(dict(key=key, status=record["status"],
                                question="scope/stratum unavailable in timed-out or failed window result"))
            continue
        w = row.get("window") or {}
        if record["status"] == "ok" and w.get("verdict") == "bounded" and not row.get("caps") and not row.get("invalid"):
            continue
        item = dict(key=key, stratum="I" if is_I else row["stratum"],
                    window_verdict=w.get("verdict", "undecided"), weight=row.get("weight"),
                    runner_status=record["status"])
        if not is_I:
            selected.append(item)
            continue
        item["cell"] = list(cell)
        cells[cell].append(item)
    for cell in sorted(cells):
        selected.extend(cells[cell][:30])
    selected.sort(key=lambda item: inputs.carry_order(item["key"]))
    result = dict(schema_version=1, window_source=str(results_file(source)),
                  window_source_sha256=inputs.digest(results_file(source)), population_records=len(records),
                  path_ready=True, path=selected, paths=selected, direct_ready=False, direct=[],
                  I_cells={"/".join(cell): dict(eligible=len(rows), selected=min(30, len(rows)))
                           for cell, rows in sorted(cells.items())},
                  unclassified_failures=missing, ambiguities=ambiguity,
                  I_syntactic_cells=cell_by_I_family,
                  cell_rule="A5: R_s period and any knot-meeting phase of its repeating part, independent of Q_s completion",
                  selection="sha256('CARRY:'+key); all eligible T/O/X; first <=30 I per specified cell")
    inputs.dump(target, result)
    return result


def freeze_direct(source):
    target = HERE / "sample.json"
    result = json.loads(target.read_text())
    if result.get("direct_ready"):
        raise ValueError("direct sample already frozen")
    original = json.loads(target.read_text())
    keys = {row["key"] for row in result["path"]}
    records = load_results(source)
    if set(records) != keys:
        raise ValueError("every frozen path family must have a final record before direct selection")
    remaining = []
    for row in result["path"]:
        record = records[row["key"]]
        value = record.get("result") or {}
        # EVERY-RAY's unchanged entry point returns class='bounded' only with its complete residue certificate.
        bounded = record["status"] == "ok" and value.get("class") == "bounded"
        if not bounded:
            remaining.append(row)
    remaining.sort(key=lambda item: inputs.carry_order(item["key"]))
    result.update(direct_ready=True, direct=remaining[:60],
                  path_source=str(results_file(source)), path_source_sha256=inputs.digest(results_file(source)),
                  direct_eligible=len(remaining), direct_limit=60)
    # Preserve the exact pre-path sample as a distinct immutable stage before the permitted extension.
    backup = HERE / "sample_paths_frozen.json"
    if backup.exists():
        raise FileExistsError("pre-path sample backup already exists")
    inputs.dump(backup, original)
    inputs.dump(target, result)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("stage", choices=("paths", "direct"))
    parser.add_argument("--results", type=Path, required=True)
    args = parser.parse_args()
    result = freeze_paths(args.results) if args.stage == "paths" else freeze_direct(args.results)
    print(json.dumps(dict(stage=args.stage, path=len(result["path"]), direct=len(result["direct"]),
                          ambiguities=len(result["ambiguities"]))))


if __name__ == "__main__":
    main()
