"""Resumable, single-process A2--A4 independent gate (never a population run).

The scientific panel is frozen from the completed 300-row smoke. Its smallest
block ordering must be supplied explicitly; without it only a pending summary
is written. No DP code is imported: smoke values are comparison inputs only.
All durable files belong to the requested CODEX output directory.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import itertools
import json
import os
from pathlib import Path
import random
import resource
import threading
import time
import traceback
import uuid

import brute_paths as B

HERE, ROOT = B.HERE, B.ROOT
CLASSES = ("grows", "bounded", "mixed by residue", "lost at large depths",
           "none at any depth", "unresolved")
SCHEMA = "every-ray-independent-brute-A2-A4-v1"
TOTAL_SECONDS = 3600.0
OWN_MEMORY_BYTES = 3_000_000_000


def permitted(path):
    path = Path(path).resolve()
    if not path.is_relative_to(HERE):
        raise ValueError(f"output must remain in CODEX: {path}")
    return path


def dump(path, value):
    path = permitted(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    with tmp.open("w") as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write("\n")
        stream.flush()
        os.fsync(stream.fileno())
    tmp.replace(path)


def append(path, value):
    path = permitted(path)
    with path.open("a") as stream:
        stream.write(json.dumps(value, sort_keys=True) + "\n")
        stream.flush()
        os.fsync(stream.fileno())


def read_rows(path, *, recover=False):
    """Recover only an interrupted final line, preserving its exact bytes."""
    path = Path(path)
    if not path.exists():
        return []
    rows, offset, needs_newline = [], 0, False
    size = path.stat().st_size
    with path.open("rb") as stream:
        for number, line in enumerate(stream, 1):
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                if not recover or stream.tell() != size:
                    raise ValueError(f"invalid JSON at {path}:{number}")
                permitted(path)
                tail = path.with_name(path.name + f".interrupted-{time.time_ns()}.bin")
                tail.write_bytes(line)
                with path.open("r+b") as repair:
                    repair.truncate(offset)
                break
            if not isinstance(row, dict):
                raise ValueError(f"non-object JSON at {path}:{number}")
            rows.append(row)
            offset = stream.tell()
            if recover and offset == size and not line.endswith(b"\n"):
                needs_newline = True
    if needs_newline:
        permitted(path)
        with path.open("ab") as repair:
            repair.write(b"\n")
            repair.flush()
            os.fsync(repair.fileno())
    return rows


def sha_file(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def code_fingerprint():
    files = (Path(__file__), Path(B.__file__), B.LS_PATH, Path(B.LS.L.__file__))
    return {str(p.relative_to(ROOT)): sha_file(p) for p in files}


def path_class(row):
    for field in ("path_class", "class_path", "class"):
        if field in row:
            return row[field]
    raise ValueError("smoke row has no over-paths class")


def horizon(row):
    exact = row.get("exact_eventual_boundedness")
    if isinstance(exact, dict):
        onset, period = exact.get("depth_threshold"), exact.get("period")
        valid = (isinstance(onset, int) and not isinstance(onset, bool) and onset >= 0
                 and isinstance(period, int) and not isinstance(period, bool) and period >= 1)
        if valid:
            return min(8, max(3, onset + period)), dict(
                rule="min(8,max(3,depth_threshold+period))", depth_threshold=onset,
                period=period, certificate_field="exact_eventual_boundedness")
    return 4, dict(rule="4 without an exact residue certificate")


def candidate_rows(smoke_rows):
    """Independently recover block sizes; do not use a DP's flat encoding."""
    candidates, exclusions, questions = [], [], []
    seen = set()
    for row in smoke_rows:
        key = row.get("key")
        if not isinstance(key, str) or key in seen:
            raise ValueError("smoke must contain one canonical-key row per family")
        seen.add(key)
        try:
            defs = json.loads(key)
            p = B.prepare_paths(defs)
            if p["c"] < 2 or not p["body"]["own"] or not any(p["limits"][len(defs) - 1]):
                exclusions.append(dict(key=key, reason="not c>=2 non-S1/S2/S3"))
                continue
            cls = path_class(row)
            if cls not in CLASSES:
                raise ValueError(f"unrecognised over-paths class {cls!r}")
            end, source = horizon(row)
            values = row.get("L_path")
            if not isinstance(values, list) or len(values) < end:
                questions.append(dict(key=key, question="smoke record lacks L_path values through its A2 horizon"))
                # The family remains in the panel; only missing comparisons
                # are skipped, rather than replacing it by an easier family.
            candidates.append(dict(key=key, **{"class": cls}, c=p["c"],
                                   n_defs=len(defs), main_size=p["main_size"], s_size=p["s_size"],
                                   main_own=p["root"]["own"], s_own=p["body"]["own"],
                                   s_max=end, horizon=source, dp_values=values,
                                   dp_values_uncarried=row.get("L_path_uncarried"),
                                   dp_complete=row.get("complete"), dp_status=row.get("status")))
        except (ValueError, KeyError, TypeError) as exc:
            questions.append(dict(key=key, question=f"cannot admit smoke candidate: {exc}"))
    return candidates, exclusions, questions


def select_panel(candidates, order):
    """Random(7) breaks size ties, then quotas draw from that frozen ranking."""
    if order not in ("max_then_sum", "s_then_main"):
        raise ValueError("panel ordering requires an explicit approved choice")
    ranked = sorted(candidates, key=lambda row: row["key"])
    random.Random(7).shuffle(ranked)
    if order == "max_then_sum":
        metric = lambda row: (max(row["main_size"], row["s_size"]), row["main_size"] + row["s_size"])
    else:
        metric = lambda row: (row["s_size"], row["main_size"])
    ranked.sort(key=metric)  # stable: the seeded permutation breaks equal sizes
    selected, keys = [], set()

    def take(predicate, required):
        need = required - sum(predicate(row) for row in selected)
        for row in ranked:
            if need <= 0:
                break
            if row["key"] not in keys and predicate(row):
                selected.append(row)
                keys.add(row["key"])
                need -= 1

    available_classes = Counter(row["class"] for row in candidates)
    for cls in CLASSES:
        take(lambda row, cls=cls: row["class"] == cls, min(10, available_classes[cls]))
    take(lambda row: row["n_defs"] > 1, 40)
    take(lambda row: row["c"] >= 3, 20)
    take(lambda row: True, 120)
    if len(selected) > 120:
        raise ValueError("quota selection unexpectedly exceeds the 120-family contract")
    # Processing order also follows size ranking; quota admission does not
    # preferentially schedule a class before the others.
    selected.sort(key=lambda row: ranked.index(row))
    got_classes = Counter(row["class"] for row in selected)
    quotas = dict(
        families=dict(required=120, available=len(candidates), selected=len(selected), met=len(selected) == 120),
        by_class={cls: dict(required=min(10, available_classes[cls]), available=available_classes[cls],
                            selected=got_classes[cls], met=got_classes[cls] >= min(10, available_classes[cls]))
                  for cls in CLASSES},
        several_definitions=dict(required=40, available=sum(row["n_defs"] > 1 for row in candidates),
                                 selected=sum(row["n_defs"] > 1 for row in selected)),
        c_ge_3=dict(required=20, available=sum(row["c"] >= 3 for row in candidates),
                    selected=sum(row["c"] >= 3 for row in selected)))
    for name in ("several_definitions", "c_ge_3"):
        quotas[name]["met"] = quotas[name]["selected"] >= quotas[name]["required"]
    return selected, quotas


def compare_depth(value, observed):
    """A missing or >7 DP value agrees with no bond through size seven."""
    if value is not None and (isinstance(value, bool) or not isinstance(value, int) or value < 0):
        return dict(passed=None, status="pending_ambiguity", question="DP depth value is not a nonnegative integer or null")
    expected = value if value is not None and value <= 7 else None
    return dict(passed=observed == expected, status="equal" if observed == expected else "mismatch",
                dp_value=value, dp_through_size_7=expected, brute_through_size_7=observed,
                none_means="no bond through size seven")


def expected_at(case, s, *, uncarried=False):
    values = case.get("dp_values_uncarried" if uncarried else "dp_values")
    if not isinstance(values, list) or len(values) < s:
        return None, False
    return values[s - 1], True


def run_controls():
    """Known free target, three-member bond, and repeated-port alternatives."""
    free = [(3, 1, [("SELF", (0, 3, 2)), ("SELF", (0, 3, 2))])]
    simple = [(3, 1, [("K", (0, 1, 3)), ("SELF", (0, 3, 2)), ("SELF", (0, 3, 2))])]
    alternative = [(3, 1, [("K", (0, 1, 3)), ("SELF", (0, 3, 2)), ("SELF", (0, 0, 3))])]
    several = simple + [(3, 1, [(0, (0, 1, 2)), (0, (0, 0, 3))])]
    cases, mismatches = [], []
    for name, defs, expected in (("no_bond", free, None), ("simple_bond", simple, 3),
                                 ("alternative_and_repeated_port", alternative, 2),
                                 ("several_main_entries", several, 2)):
        paths = []
        row = B.brute(defs, 1, on_path=paths.append)
        checks = dict(least_size=row["least_size"] == expected, all_paths=row["checked_paths"] == 2,
                      complete=row["complete"] is True)
        if name in ("alternative_and_repeated_port", "several_main_entries"):
            checks["path_alternatives_3_and_2"] = [r["least_size"] for r in paths] == [3, 2]
            checks["repeated_port_identity"] = paths[1]["copy_ports"][1][0] == paths[1]["copy_ports"][1][1]
        for check, passed in checks.items():
            if not passed:
                mismatches.append(dict(control=name, check=check, observed=row, paths=paths))
        cases.append(dict(control=name, checks=checks, result=row, paths=paths))
    p = B.prepare_paths(alternative)
    path_list = [B.path_at(p, 3, i) for i in range(B.path_count(p, 3))]
    direct = list(itertools.product(p["entries"], p["continuations"], p["continuations"]))
    if path_list != direct:
        mismatches.append(dict(control="all_SELF_choices", expected=direct, observed=path_list))
    carried_defs = [(3, 3, [("SELF", (0, 3, 4)), ("SELF", (3, 4, 5))])]
    carried_paths = []
    B.brute(carried_defs, 1, on_path=carried_paths.append)
    if [row["carried_target_ports"] for row in carried_paths] != [[0], []]:
        mismatches.append(dict(control="actual_main_port_identity_loss", observed=carried_paths))
    # A scalar evaluator checks every state of an example whose non-chosen
    # call has non-TOP G, independently of the vectorised CNF evaluator.
    side_defs = [(3, 1, [("K", (0, 1, 3)), ("SELF", (0, 1, 2)), ("SELF", (0, 3, 2))])]
    side = B.prepare_paths(side_defs)
    side_path = B.path_at(side, 1, 0)
    instance = B.path_cnf(side_defs, 1, side_path, prepared=side)
    vector_models = set(map(int, B._enumerate_models(instance["clauses"], instance["n"], lambda: None)))
    direct_models = set()
    side_limit_rejections = 0
    for assignment in range(1 << instance["n"]):
        admitted = True
        for depth, copy in enumerate(instance["copies"]):
            flat = side["root"] if depth == 0 else side["body"]
            env = copy["ports"] + copy["own"]
            for call_index, (target, arguments) in enumerate(flat["calls"]):
                bits = [(assignment >> env[a]) & 1 for a in arguments]
                if target == "K":
                    admitted &= len(set(bits)) > 1
                elif call_index != copy["selected_flat_call"]:
                    allowed = bool(side["limits"][target][sum(bit << j for j, bit in enumerate(bits))])
                    side_limit_rejections += not allowed
                    admitted &= allowed
        if admitted:
            direct_models.add(assignment)
    if vector_models != direct_models or not side_limit_rejections:
        mismatches.append(dict(control="nonchosen_limit_relation", vector=sorted(vector_models),
                               direct=sorted(direct_models), side_limit_rejections=side_limit_rejections))
    cap = B.brute(alternative, 4, max_variables=7)
    if cap.get("skipped_paths") != 16 or cap.get("complete") is not False:
        mismatches.append(dict(control="all_over_cap_paths_recorded", observed=cap))
    for label, value, observed, expected in (("above_seven", 8, None, True),
                                              ("finite_mismatch", 3, 2, False),
                                              ("missing_bond", None, None, True)):
        if compare_depth(value, observed)["passed"] != expected:
            mismatches.append(dict(control=label, value=value, observed=observed))
    return dict(gate="independent-brute-controls", passed=not mismatches, cases=cases,
                enumerated_depth_three_paths=len(path_list), variable_cap_control=cap,
                actual_identity_carried_ports=[row["carried_target_ports"] for row in carried_paths],
                nonchosen_limit_models_checked=1 << instance["n"],
                nonchosen_limit_rejections=side_limit_rejections,
                mismatches=mismatches)


def rss_bytes():
    try:
        return int(Path("/proc/self/statm").read_text().split()[1]) * os.sysconf("SC_PAGE_SIZE")
    except (FileNotFoundError, IndexError, ValueError):
        return int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss) * 1024


def depth_result(case, s, total, paths, *, skipped=0, terminal=False, error=None):
    best_rows = [row for row in paths if row.get("least_size") is not None]
    best_row = min(best_rows, key=lambda row: (row["least_size"], row["path_index"]), default=None)
    best = best_row["least_size"] if best_row else None
    uncarried_rows = [row for row in best_rows if row["uncarried"]]
    uncarried_best_row = min(uncarried_rows, key=lambda row: (row["least_size"], row["path_index"]), default=None)
    uncarried_best = uncarried_best_row["least_size"] if uncarried_best_row else None
    complete = len(paths) == total and not skipped and error is None
    expected, available = expected_at(case, s)
    if complete and available:
        comparison = compare_depth(expected, best)
    elif not available:
        comparison = dict(passed=None, status="pending_ambiguity", question="missing smoke L_path value at this depth")
    else:
        comparison = dict(passed=None, status="not_compared_incomplete_paths")
    expected_uncarried, available_uncarried = expected_at(case, s, uncarried=True)
    if complete and available_uncarried:
        uncarried_comparison = compare_depth(expected_uncarried, uncarried_best)
    else:
        uncarried_comparison = dict(passed=None, status="not_compared_incomplete_paths" if not complete else "missing_L_path_uncarried")
    return dict(key=case["key"], s=s, s_max=case["s_max"], total_paths=total,
                checked_paths=len(paths), skipped_paths=skipped, complete=complete,
                terminal=terminal or complete, status="complete" if complete else
                "skipped_variable_cap" if skipped else "incomplete",
                least_size=best, witness=best_row.get("witness") if best_row else None,
                target_path=best_row.get("path") if best_row else None,
                target_path_index=best_row.get("path_index") if best_row else None,
                least_size_uncarried=uncarried_best,
                uncarried_paths=sum(row["uncarried"] for row in paths),
                uncarried_target_path=uncarried_best_row.get("path") if uncarried_best_row else None,
                comparison=comparison, uncarried_comparison=uncarried_comparison,
                dp_complete=case.get("dp_complete"), error=error)


def summarise(panel, depths, controls, progress, status):
    family_rows = []
    mismatches, pending, uncarried_mismatches, uncarried_pending = [], [], [], []
    checked_depths = complete_depths = finished_families = complete_families = 0
    checked_paths = skipped_paths = 0
    for case in panel["selected"]:
        family_depths = []
        for s in range(1, case["s_max"] + 1):
            row = depths.get((case["key"], s))
            if row is None:
                family_depths.append(dict(s=s, status="not_started", complete=False, terminal=False))
                continue
            family_depths.append(row)
            checked_depths += 1
            complete_depths += bool(row["complete"])
            checked_paths += row["checked_paths"]
            skipped_paths += row["skipped_paths"]
            comp = row["comparison"]
            if comp.get("passed") is False:
                mismatches.append(dict(key=case["key"], s=s, **comp))
            elif comp.get("passed") is None:
                pending.append(dict(key=case["key"], s=s, status=comp["status"],
                                    question=comp.get("question")))
            unc = row["uncarried_comparison"]
            if unc.get("passed") is False:
                uncarried_mismatches.append(dict(key=case["key"], s=s, **unc))
            elif unc.get("passed") is None:
                uncarried_pending.append(dict(key=case["key"], s=s, status=unc["status"]))
        finished = all(row.get("terminal") is True for row in family_depths)
        complete = all(row.get("complete") is True for row in family_depths)
        finished_families += finished
        complete_families += complete
        family_rows.append(dict(key=case["key"], s_max=case["s_max"],
                                finished=finished, complete=complete, depths=family_depths))
    quotas = panel["quotas"]
    quotas_met = (quotas["families"]["met"] and quotas["several_definitions"]["met"]
                  and quotas["c_ge_3"]["met"] and all(q["met"] for q in quotas["by_class"].values()))
    passed = False if mismatches or not controls["passed"] else (
        True if complete_families == 120 and quotas_met and not pending and not panel["questions"] else None)
    return dict(schema=SCHEMA, gate="G-brute", status=status, passed=passed,
                selected_families=len(panel["selected"]), requested_families=120,
                finished_families=finished_families, complete_families=complete_families,
                checked_depths=checked_depths, complete_depths=complete_depths,
                requested_depths=sum(row["s_max"] for row in panel["selected"]),
                checked_paths=checked_paths, skipped_paths=skipped_paths,
                quotas=quotas, mismatches=mismatches, pending_comparisons=pending,
                A9_uncarried=dict(mismatches=uncarried_mismatches, pending_comparisons=uncarried_pending,
                                  passed=False if uncarried_mismatches else None if uncarried_pending or complete_families != 120 else True,
                                  source="actual target-port identities, independently compared to main-port identities"),
                questions=panel["questions"], controls_passed=controls["passed"],
                timing=progress, families=family_rows,
                completeness="finished includes variable-cap skips; complete requires every path at every requested depth",
                assignment_limit=22, member_size_limit=7, workers=1)


def run_panel(args):
    invocation_started = time.monotonic()
    out = permitted(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    # Once explicitly chosen and frozen, the same policy remains authorised
    # for a resume. Omitting the option must not overwrite a finished summary
    # with a new pending-selection record.
    existing_panel = out / "brute_panel.json"
    if args.panel_order is None and existing_panel.exists():
        args.panel_order = json.loads(existing_panel.read_text())["config"]["panel_order"]
    if args.panel_order is None:
        result = dict(schema=SCHEMA, gate="G-brute", passed=None, status="pending_panel_order",
                      question="Choose max_then_sum or s_then_main as the smallest-block ordering before freezing the panel.",
                      selected_families=0, checked_families=0)
        dump(out / "brute_summary.json", result)
        print(json.dumps(dict(gate="G-brute", status=result["status"], passed=None)), flush=True)
        return result
    smoke = Path(args.smoke_jsonl).resolve()
    if not smoke.is_relative_to(HERE):
        raise ValueError("the smoke input must be the CODEX smoke output")
    smoke_rows = read_rows(smoke)
    if len(smoke_rows) != 300:
        result = dict(schema=SCHEMA, gate="G-brute", passed=None, status="pending_300_smoke_rows",
                      smoke_rows=len(smoke_rows), selected_families=0,
                      question="The addendum requires the completed 300-family smoke before panel selection.")
        dump(out / "brute_summary.json", result)
        print(json.dumps(dict(gate="G-brute", status=result["status"], passed=None)), flush=True)
        return result
    config = dict(schema=SCHEMA, code=code_fingerprint(), smoke_sha256=sha_file(smoke),
                  smoke_path=str(smoke.relative_to(ROOT)), panel_order=args.panel_order,
                  total_budget_seconds=args.seconds, max_variables=22, max_size=7, seed=7)
    panel_path = out / "brute_panel.json"
    if panel_path.exists():
        panel = json.loads(panel_path.read_text())
        if panel.get("config") != config:
            raise ValueError("frozen panel/configuration differs; preserve it and choose a fresh CODEX output directory")
    else:
        if any((out / name).exists() for name in ("brute_paths.jsonl", "brute_depths.jsonl", "brute_progress.json")):
            raise ValueError("existing run journals have no matching panel manifest")
        candidates, exclusions, questions = candidate_rows(smoke_rows)
        selected, quotas = select_panel(candidates, args.panel_order)
        panel = dict(config=config, selected=selected, quotas=quotas,
                     candidate_families=len(candidates), exclusions=exclusions, questions=questions,
                     selection="Random(7) shuffle of sorted keys; stable smallest-block sort; take class quotas, then several-definition quota, then c>=3 quota, then fill to 120; schedule in the size ranking",
                     created_utc=datetime.now(timezone.utc).isoformat())
        dump(panel_path, panel)
    controls = run_controls()
    dump(out / "brute_controls.json", controls)
    if not controls["passed"]:
        raise ValueError("independent brute controls failed; no panel computation started")
    path_rows = read_rows(out / "brute_paths.jsonl", recover=True)
    completed_paths = {}
    for row in path_rows:
        if row.get("complete") is True:
            index = (row["key"], row["s"], row["path_index"])
            if index in completed_paths and completed_paths[index] != row:
                raise ValueError("conflicting completed path records")
            completed_paths[index] = row
    depths = {(row["key"], row["s"]): row
              for row in read_rows(out / "brute_depths.jsonl", recover=True)}
    progress_path = out / "brute_progress.json"
    progress = json.loads(progress_path.read_text()) if progress_path.exists() else dict(attempts=[])
    for attempt in progress["attempts"]:
        if attempt.get("status") == "running":
            attempt["status"] = "interrupted"
            attempt["interruption_accounting"] = "elapsed at last durable one-second heartbeat"
    prior = sum(attempt["seconds"] for attempt in progress["attempts"])
    if prior >= args.seconds:
        result = summarise(panel, depths, controls, progress, "budget_exhausted")
        dump(out / "brute_summary.json", result)
        print(json.dumps({k: result[k] for k in ("gate", "status", "passed", "finished_families", "complete_families")}), flush=True)
        return result
    started = invocation_started
    attempt = dict(id=uuid.uuid4().hex, started_utc=datetime.now(timezone.utc).isoformat(),
                   seconds=0.0, status="running", process_id=os.getpid(), peak_rss_bytes=rss_bytes())
    progress["attempts"].append(attempt)
    progress.update(total_budget_seconds=args.seconds, prior_seconds=prior,
                    heartbeat_seconds=1.0, process_count=1, last_work=None)
    lock, stopped = threading.Lock(), threading.Event()

    def save_progress():
        with lock:
            attempt["seconds"] = time.monotonic() - started
            attempt["peak_rss_bytes"] = max(attempt["peak_rss_bytes"], rss_bytes())
            progress["total_seconds"] = prior + attempt["seconds"]
            dump(progress_path, progress)

    def heartbeat():
        while not stopped.wait(1.0):
            save_progress()

    def checkpoint():
        if prior + time.monotonic() - started >= args.seconds:
            raise B.BruteLimit("total brute gate wall-time budget exhausted")
        if rss_bytes() > OWN_MEMORY_BYTES:
            raise B.BruteLimit("own brute process exceeded 3 GB resident memory")

    save_progress()
    watcher = threading.Thread(target=heartbeat, daemon=True)
    watcher.start()
    final_status = "finished"
    active_case, active_s, active_total = None, None, None
    try:
        # Breadth by depth prevents the first large branching family from
        # consuming the whole gate before other families reach depth one.
        for s in range(1, 9):
            for case in panel["selected"]:
                if s > case["s_max"] or depths.get((case["key"], s), {}).get("terminal"):
                    continue
                active_case, active_s = case, s
                defs = json.loads(case["key"])
                p = B.prepare_paths(defs)
                active_total = B.path_count(p, s)
                checkpoint()
                progress["last_work"] = dict(key=case["key"], s=s, path_index=None)
                n = B.path_size(p, s)
                rows = [row for (key, depth, _), row in completed_paths.items()
                        if key == case["key"] and depth == s]
                if n > 22:
                    result = depth_result(case, s, active_total, rows, skipped=active_total, terminal=True)
                    result.update(n=n, skipped_path_ranges=[[0, active_total - 1]],
                                  skip_reason="every path has the same retained-distinction count above 22")
                else:
                    for ordinal in range(active_total):
                        index = (case["key"], s, ordinal)
                        if index in completed_paths:
                            continue
                        checkpoint()
                        progress["last_work"] = dict(key=case["key"], s=s, path_index=ordinal)
                        row = B.brute_path(defs, s, B.path_at(p, s, ordinal), prepared=p, checkpoint=checkpoint)
                        row.update(key=case["key"], path_index=ordinal, attempt_id=attempt["id"],
                                   attempt_elapsed_seconds=time.monotonic() - started)
                        append(out / "brute_paths.jsonl", row)
                        completed_paths[index] = row
                        rows.append(row)
                        save_progress()
                    result = depth_result(case, s, active_total, rows, terminal=True)
                    result["n"] = n
                result.update(attempt_id=attempt["id"], attempt_elapsed_seconds=time.monotonic() - started)
                append(out / "brute_depths.jsonl", result)
                depths[(case["key"], s)] = result
                save_progress()
                summary = summarise(panel, depths, controls, progress, "running")
                dump(out / "brute_summary.json", summary)
                print(json.dumps(dict(gate="G-brute", depth=s, completed_depths=summary["complete_depths"],
                                      finished_families=summary["finished_families"],
                                      complete_families=summary["complete_families"],
                                      mismatches=len(summary["mismatches"]),
                                      seconds=round(prior + time.monotonic() - started, 3))), flush=True)
                active_case = None
    except (B.BruteLimit, KeyboardInterrupt) as exc:
        final_status = "interrupted" if isinstance(exc, KeyboardInterrupt) else "budget_or_memory_stopped"
        attempt["stop_reason"] = str(exc) or "KeyboardInterrupt"
    except Exception as exc:
        final_status = "error"
        attempt["stop_reason"] = f"{type(exc).__name__}: {exc}"
        attempt["traceback"] = traceback.format_exc()
    finally:
        if active_case is not None:
            rows = [row for (key, depth, _), row in completed_paths.items()
                    if key == active_case["key"] and depth == active_s]
            result = depth_result(active_case, active_s, active_total or 0, rows,
                                  error=attempt.get("stop_reason", final_status))
            result["attempt_id"] = attempt["id"]
            append(out / "brute_depths.jsonl", result)
            depths[(active_case["key"], active_s)] = result
        stopped.set()
        watcher.join()
        attempt["status"] = final_status
        save_progress()
        result = summarise(panel, depths, controls, progress, final_status)
        dump(out / "brute_summary.json", result)
    print(json.dumps({k: result[k] for k in ("gate", "status", "passed", "finished_families", "complete_families")}), flush=True)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--smoke-jsonl", type=Path, default=HERE / "smoke_families.jsonl")
    parser.add_argument("--out-dir", type=Path, default=HERE / "brute_addendum")
    parser.add_argument("--panel-order", choices=("max_then_sum", "s_then_main"))
    parser.add_argument("--seconds", type=float, default=TOTAL_SECONDS,
                        help="cumulative wall-time ceiling across resumes, at most 3600")
    parser.add_argument("--controls-only", action="store_true",
                        help="run tiny synthetic controls, print JSON, and write no files")
    args = parser.parse_args()
    if not 0 < args.seconds <= TOTAL_SECONDS:
        parser.error("--seconds must be positive and no greater than 3600")
    if args.controls_only:
        result = run_controls()
        print(json.dumps(result, sort_keys=True), flush=True)
        if not result["passed"]:
            raise SystemExit(1)
        return
    run_panel(args)


if __name__ == "__main__":
    main()
