"""Resumable frozen gates G1/G2 and explicit-panel G3 for REACH-CENSUS.

No validation starts at import. The runner can reuse ``gate664_cases`` and
``check_g1`` for its all-664 pass at census caps. G3 deliberately requires an
explicit supplied panel and computed reference rows: the frozen spec does not
uniquely define the smallest-block pool or its class/multidefinition allocation.
The default files are validation_g1.jsonl, validation_g2.jsonl, and
validation_g3.jsonl. The full runner can explicitly supply its own G1 file
inside CODEX. Returned summaries belong to the lead's gates.json / REPORT.
"""

import argparse
import hashlib
import importlib.util
import json
import multiprocessing as mp
import os
from pathlib import Path
import signal
import threading
import time


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


DP = _load("reach_validation_dp", HERE / "reach_dp.py")
BRUTE = _load("reach_validation_brute", HERE / "brute_check.py")
PR_PATH = DP.PR_DIR / "rates_all.jsonl"
BD_ROWS_PATH = (ROOT / "artifacts/BOND-DEPTH-20261112-001A/"
                "BOND-DEPTH-20261112-001A-E001_spine_bonds/runs_merged.jsonl")
REF_ROWS_PATH = ROOT / "research/PROVED-RATE-20261113-001/referee-R1/codex/recomputed.jsonl"
G3_SELECTION_QUESTION = (
    "The frozen spec does not define the eligible pool/cutoff or ranking for "
    "'among the smallest-block families', or a unique allocation/selection "
    "procedure satisfying 150 total, at least 10 of each computed class where "
    "available, and at least 40 families with more than one definition. The "
    "full census is forbidden at this hand-off. Which explicitly supplied "
    "family keys and computed reference rows constitute the G3 panel?"
)
CAP_COMPARISON_QUESTION = (
    "For the all-664 census-cap G1 repeat, which comparisons are required "
    "when PR is incomplete at its larger cap or its completed graph exceeds "
    "the new cap? The affected comparisons are pending, rather than semantic "
    "mismatches, until that cap-comparison rule is clarified."
)
AGGREGATE_MEMORY_BYTES = 7_500_000_000
_POOL_ACTIVITY = None
_POOL_SLOT = None


def _jsonl(path):
    with Path(path).open() as stream:
        for number, line in enumerate(stream, 1):
            if line.strip():
                try:
                    yield json.loads(line)
                except json.JSONDecodeError as exc:
                    raise ValueError(f"invalid JSON at {path}:{number}") from exc


def _by_idx(path):
    out = {}
    for row in _jsonl(path):
        if "idx" not in row:
            continue
        if row["idx"] in out:
            raise ValueError(f"duplicate idx {row['idx']} in {path}")
        out[row["idx"]] = row
    return out


def gate664_cases(all_664=False):
    """BD.families_one_def cases, with immutable PR/BD/referee expectations.

    The ordinary validation subset requires PR complete and nodes <= 20,000.
    ``all_664=True`` removes only that validation-size filter, as required for
    the full runner's census-cap gate. Family identity remains BD's LS index.
    """
    bd = _load("reach_validation_bd", DP.BD_PATH)
    families = bd.families_one_def()
    if len(families) != 664:
        raise ValueError(f"BD.families_one_def returned {len(families)}, expected 664")
    pr = _by_idx(PR_PATH)
    old = _by_idx(BD_ROWS_PATH)
    referee = _by_idx(REF_ROWS_PATH)
    cases = []
    for idx, defs in families:
        if idx not in pr or idx not in old:
            raise ValueError(f"missing PR or BD reference for idx {idx}")
        if not all_664 and not (pr[idx].get("complete") is True and pr[idx].get("nodes", 20001) <= 20000):
            continue
        cases.append(dict(idx=idx, defs=defs, key=DP.canonical(defs),
                          pr=pr[idx], bd=old[idx], referee=referee.get(idx),
                          allow_cap_skips=all_664))
    return cases


def _compare(mismatches, field, observed, expected, source, **context):
    if observed != expected:
        mismatches.append(dict(field=field, observed=observed, expected=expected,
                               source=source, **context))


def _compare_required(mismatches, observed, expected, field, source):
    if field not in expected:
        mismatches.append(dict(field=field, source=source, kind="reference field missing"))
    elif field not in observed:
        mismatches.append(dict(field=field, source=source, kind="computed field missing",
                               expected=expected[field]))
    else:
        _compare(mismatches, field, observed[field], expected[field], source)


def compare_g1(case, result, *, node_cap=DP.NODE_CAP):
    """Compare a supplied census result with all applicable G1 references."""
    mismatches = []
    _compare(mismatches, "status", result.get("status"), "done", "new computation")
    for field in ("nodes", "complete", "lambda", "bounded_all"):
        _compare_required(mismatches, result, case["pr"], field, "PR")
    old_values = case["bd"].get("L")
    new_values = result.get("L_ray", [])
    if old_values is None:
        mismatches.append(dict(field="L", source="BD", kind="reference field missing"))
    else:
        for depth, expected in enumerate(old_values, 1):
            observed = new_values[depth - 1] if depth <= len(new_values) else None
            _compare(mismatches, "L_ray", observed, expected, "BD", s=depth)
    referee = case.get("referee")
    if referee is not None:
        exact = referee.get("exact_eventual_boundedness", {})
        for field in ("eventually_bounded", "period", "missing_residues"):
            _compare_required(mismatches, result, exact, field, "referee")
    pending = []
    if case.get("allow_cap_skips"):
        # Only the all-664 repeat has this explicitly reported ambiguity. The
        # frozen <=20k validation remains a strict comparison throughout.
        resource_stop = result.get("status") in (
            "timeout", "memory_limit", "aggregate_memory_limit", "block_size")
        incompatible_pr = (case["pr"].get("complete") is not True or
                           case["pr"].get("nodes", 0) > node_cap)
        strict = []
        for item in mismatches:
            affected = resource_stop or (incompatible_pr and (
                item.get("source") == "PR" or
                (result.get("complete") is not True and
                 item.get("source") in ("BD", "referee"))))
            if affected:
                pending.append(dict(item, question=CAP_COMPARISON_QUESTION,
                                    computed_status=result.get("status"),
                                    computed_complete=result.get("complete"),
                                    PR_complete=case["pr"].get("complete"),
                                    PR_nodes=case["pr"].get("nodes"), node_cap=node_cap))
            else:
                strict.append(item)
        mismatches = strict
    passed = False if mismatches else None if pending else True
    return dict(gate="G1", idx=case["idx"], key=case["key"],
                gate_ok=passed, passed=passed, mismatches=mismatches,
                pending_comparisons=pending,
                BD_depths=len(old_values) if old_values is not None else 0,
                referee_checked=referee is not None, result=result)


def check_g1(case, result=None, *, seconds=DP.FAMILY_SECONDS, node_cap=DP.NODE_CAP):
    """Compute with force_dp or compare a runner-supplied result at its caps."""
    if result is None:
        result = DP.compute_family(case["key"], force_dp=True, seconds=seconds, node_cap=node_cap)
    return compare_g1(case, result, node_cap=node_cap)


def wrapped_key(case):
    defs = DP.normalized(case["defs"])
    if len(defs) != 1:
        raise ValueError("G2 wraps a one-definition family")
    return DP.canonical(defs + [(3, 0, [(0, (0, 1, 2))])])


def check_g2(case, baseline=None, wrapped=None, *, seconds=DP.FAMILY_SECONDS,
             node_cap=DP.NODE_CAP):
    """Actual DP class and lambda are compared, bypassing settled classes."""
    if baseline is None:
        baseline = DP.compute_family(case["key"], force_dp=True, seconds=seconds, node_cap=node_cap)
    key = wrapped_key(case)
    if wrapped is None:
        wrapped = DP.compute_family(key, force_dp=True, seconds=seconds, node_cap=node_cap)
    mismatches = []
    for label, result in (("baseline", baseline), ("wrapped", wrapped)):
        _compare(mismatches, f"{label}.status", result.get("status"), "done", "G2 force_dp")
    for field in ("lambda", "complete", "class"):
        _compare_required(mismatches, wrapped, baseline, field, "G2 baseline")
    original_values, wrapped_values = baseline.get("L_ray", []), wrapped.get("L_ray", [])
    for depth in range(2, 31):
        expected = original_values[depth - 2] if depth - 1 <= len(original_values) else None
        observed = wrapped_values[depth - 1] if depth <= len(wrapped_values) else None
        if expected is None or observed is None:
            mismatches.append(dict(field="L_ray", source="G2 baseline", s=depth,
                                   expected=expected, observed=observed,
                                   kind="required depth missing"))
        else:
            _compare(mismatches, "L_ray", observed, expected, "G2 baseline", s=depth)
    return dict(gate="G2", idx=case["idx"], key=case["key"], wrapped_key=key,
                gate_ok=not mismatches, mismatches=mismatches,
                baseline=baseline, wrapped=wrapped)


def g3_selection_pending():
    return dict(gate="G3", status="pending selection", gate_ok=None, passed=None,
                question=G3_SELECTION_QUESTION, families=0, depths=0, mismatches=[])


def check_g3(key, dp_result, *, ray="first"):
    """Run G3 only for an explicitly supplied family and computed DP row."""
    defs = DP.normalized(json.loads(key))
    if dp_result.get("key") != key:
        raise ValueError("G3 reference row key differs from the supplied family")
    if dp_result.get("ray", "first") != ray:
        raise ValueError("G3 reference row ray differs from the requested ray")
    if str(dp_result.get("class", "")).startswith("S"):
        raise ValueError("G3 requires a computed family, not a settled-class row")
    depths = BRUTE.admissible_depths(defs, max_variables=22, max_depth=10, ray=ray)
    checks, mismatches = [], []
    values = dp_result.get("L_ray", [])
    started = time.perf_counter()
    for depth in depths:
        result = BRUTE.brute(defs, depth, max_size=7, ray=ray, max_variables=22)
        expected = values[depth - 1] if depth <= len(values) else None
        if expected is None:
            okay = False
            problem = "required DP depth missing"
        elif result["status"] == "found":
            okay = result["least_size"] == expected
            problem = "least size differs"
        elif result["status"] == "none up to 7":
            okay = expected > 7
            problem = "bounded-search disagreement"
        else:
            okay = False
            problem = "ray CNF dead or brute skipped"
        checks.append(dict(s=depth, expected=expected, agree=okay, brute=result))
        if not okay:
            mismatches.append(dict(field="L_ray", source="independent G3", s=depth,
                                   expected=expected, observed=result["least_size"],
                                   brute_status=result["status"], kind=problem))
    return dict(gate="G3", key=key, ray=ray, **{"class": dp_result.get("class")},
                n_defs=len(defs), gate_ok=not mismatches if depths else None,
                status="checked" if depths else "no admissible depths",
                depths=depths, checks=checks, mismatches=mismatches,
                seconds=time.perf_counter() - started)


def _fingerprint(gate, seconds, node_cap, ray="first"):
    files = [Path(__file__), HERE / "reach_dp.py"]
    if gate == "G3":
        files.append(HERE / "brute_check.py")
    return dict(gate=gate, seconds=seconds, node_cap=node_cap, ray=ray,
                code={path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in files})


def _output_path(gate):
    if gate not in ("G1", "G2", "G3"):
        raise ValueError("unknown validation gate")
    return HERE / f"validation_{gate.lower()}.jsonl"


def _resume_rows(path):
    """Recover only our own interrupted trailing write; preserve its bytes."""
    if not path.exists():
        return []
    data = path.read_bytes()
    lines = data.splitlines(keepends=True)
    rows, offset = [], 0
    for number, raw in enumerate(lines, 1):
        try:
            row = json.loads(raw)
        except json.JSONDecodeError:
            if number != len(lines):
                raise ValueError(f"invalid interior JSON at {path}:{number}")
            with path.open("r+b") as stream:
                stream.truncate(offset)
            recovery = dict(kind="recovered interrupted trailing write",
                            raw_tail=raw.decode("utf-8", errors="replace"))
            with path.open("a") as stream:
                stream.write(json.dumps(recovery, separators=(",", ":")) + "\n")
            return rows
        if isinstance(row, dict):
            rows.append(row)
        offset += len(raw)
    if data and not data.endswith(b"\n"):
        with path.open("a") as stream:
            stream.write("\n")
    return rows


def _identity(row, gate):
    return row.get("key") if gate == "G3" else row.get("idx")


def _pool_init(activity):
    """Ignore idle SIGUSR1; compute_family temporarily installs its own guard."""
    global _POOL_ACTIVITY, _POOL_SLOT
    signal.signal(signal.SIGUSR1, signal.SIG_IGN)
    _POOL_ACTIVITY = activity
    with activity.get_lock():
        for slot in range(len(activity) // 2):
            if not activity[2 * slot]:
                activity[2 * slot] = os.getpid()
                _POOL_SLOT = slot
                break
        else:
            raise RuntimeError("no owned validation-worker activity slot")


def _pool_active(value):
    if _POOL_ACTIVITY is not None:
        with _POOL_ACTIVITY.get_lock():
            _POOL_ACTIVITY[2 * _POOL_SLOT + 1] = int(value)


def _monitor_owned_pool(pool, activity, stop, stats, limit=AGGREGATE_MEMORY_BYTES):
    """Monitor only this pool and its parent; signal only an active owned child."""
    while not stop.wait(0.1):
        pids = {process.pid for process in pool._pool if process.pid}
        with activity.get_lock():
            active = {activity[2 * slot] for slot in range(len(activity) // 2)
                      if activity[2 * slot + 1]}
        memory = {pid: DP.rss_bytes(pid) for pid in pids}
        total = DP.rss_bytes() + sum(memory.values())
        stats["peak_aggregate_rss_bytes"] = max(stats["peak_aggregate_rss_bytes"], total)
        targets = pids & active
        if total > limit and targets:
            target = max(targets, key=memory.get)
            try:
                os.kill(target, signal.SIGUSR1)
                stats["aggregate_memory_signals"] += 1
            except ProcessLookupError:
                pass


def _worker(job):
    gate, case, baseline, fingerprint = job
    seconds, node_cap = fingerprint["seconds"], fingerprint["node_cap"]
    _pool_active(True)
    try:
        if gate == "G1":
            row = check_g1(case, seconds=seconds, node_cap=node_cap)
        elif gate == "G2":
            row = check_g2(case, baseline=baseline, seconds=seconds, node_cap=node_cap)
        else:
            row = check_g3(case["key"], baseline, ray=fingerprint["ray"])
        row["validation_config"] = fingerprint
        return row
    finally:
        _pool_active(False)


def _inside_codex(path):
    path = Path(path).resolve()
    if not path.is_relative_to(HERE):
        raise ValueError("validation outputs must remain inside CODEX")
    return path


def _run(gate, jobs, *, workers=1, fingerprint, progress=None, output_path=None):
    if not 1 <= workers <= 4:
        raise ValueError("workers must be from one through four; lead schedules aggregate resources")
    path = _inside_codex(output_path) if output_path is not None else _output_path(gate)
    path.parent.mkdir(parents=True, exist_ok=True)
    old = _resume_rows(path)
    relevant = { _identity(row, gate): row for row in old
                 if row.get("validation_config") == fingerprint and row.get("gate") == gate }
    wanted = [_identity(case, gate) for case, _ in jobs]
    pending = [(gate, case, baseline, fingerprint) for case, baseline in jobs
               if _identity(case, gate) not in relevant]
    started = time.perf_counter()
    resources = dict(requested_total_process_budget=workers,
                     effective_computing_children=0 if workers == 1 else workers - 1,
                     effective_computing_processes=1 if workers == 1 else workers - 1,
                     aggregate_memory_limit_bytes=AGGREGATE_MEMORY_BYTES,
                     peak_aggregate_rss_bytes=DP.rss_bytes(), aggregate_memory_signals=0)
    if pending:
        pool = None
        stop = monitor = None
        if workers == 1:
            results = map(_worker, pending)
        else:
            # The caller's process is included in the frozen total budget.
            activity = mp.get_context("fork").Array("q", 64, lock=True)
            pool = mp.get_context("fork").Pool(workers - 1, initializer=_pool_init, initargs=(activity,))
            stop = threading.Event()
            monitor = threading.Thread(target=_monitor_owned_pool,
                                       args=(pool, activity, stop, resources), daemon=True)
            monitor.start()
            results = pool.imap_unordered(_worker, pending, chunksize=1)
        try:
            with path.open("a") as stream:
                for row in results:
                    stream.write(json.dumps(row, separators=(",", ":"), sort_keys=True) + "\n")
                    stream.flush()
                    relevant[_identity(row, gate)] = row
                    if progress is not None:
                        progress(row)
        except BaseException:
            if pool is not None:
                pool.terminate()
            raise
        finally:
            if pool is not None:
                pool.close()
                pool.join()
                stop.set()
                monitor.join(timeout=1)
    rows = [relevant[identifier] for identifier in wanted if identifier in relevant]
    mismatches = [dict(key=row.get("key"), idx=row.get("idx"), **item)
                  for row in rows for item in row.get("mismatches", [])]
    pending_comparisons = [dict(key=row.get("key"), idx=row.get("idx"), **item)
                           for row in rows for item in row.get("pending_comparisons", [])]
    passed = (False if mismatches else
              None if len(rows) != len(wanted) or not wanted or
              any(row.get("gate_ok") is not True for row in rows) else True)
    return dict(gate=gate, requested=len(wanted), completed=len(rows),
                newly_run=len(pending), gate_ok=passed, passed=passed, mismatches=mismatches,
                pending_comparisons=pending_comparisons, resources=resources,
                seconds=time.perf_counter() - started, path=str(path), rows=rows)


def run_g1(*, all_664=False, workers=1, seconds=DP.FAMILY_SECONDS,
           node_cap=DP.NODE_CAP, progress=None):
    cases = gate664_cases(all_664)
    return _run("G1", [(case, None) for case in cases], workers=workers,
                fingerprint=_fingerprint("G1", seconds, node_cap), progress=progress)


def run_gate1(out, *, workers=1, all664=False, seconds=DP.FAMILY_SECONDS,
              node_cap=DP.NODE_CAP, progress=None):
    """Full runner API: write its explicitly named G1 JSONL inside CODEX."""
    cases = gate664_cases(all664)
    result = _run("G1", [(case, None) for case in cases], workers=workers,
                  fingerprint=_fingerprint("G1", seconds, node_cap),
                  progress=progress, output_path=out)
    return {key: value for key, value in result.items() if key != "rows"}


def run_g2(*, all_664=False, workers=1, seconds=DP.FAMILY_SECONDS,
           node_cap=DP.NODE_CAP, progress=None):
    cases = gate664_cases(all_664)
    g1_config = _fingerprint("G1", seconds, node_cap)
    old = _resume_rows(_output_path("G1"))
    baselines = {row["idx"]: row["result"] for row in old
                 if row.get("gate") == "G1" and row.get("validation_config") == g1_config}
    return _run("G2", [(case, baselines.get(case["idx"])) for case in cases], workers=workers,
                fingerprint=_fingerprint("G2", seconds, node_cap), progress=progress)


def run_g3(keys=None, computed_rows=None, *, workers=1, ray="first", progress=None):
    """No implicit sampling and no hidden extra census: missing panel is pending."""
    if keys is None:
        return g3_selection_pending()
    keys = list(keys)
    if len(set(keys)) != len(keys):
        raise ValueError("the supplied G3 panel has duplicate family keys")
    if computed_rows is None:
        raise ValueError("explicit computed reference rows are required for G3")
    rows = (computed_rows if isinstance(computed_rows, dict) else
            {row["key"]: row for row in computed_rows})
    missing = [key for key in keys if key not in rows]
    if missing:
        raise ValueError(f"G3 reference rows are missing for {len(missing)} selected keys")
    jobs = [(dict(key=key), rows[key]) for key in keys]
    result = _run("G3", jobs, workers=workers,
                  fingerprint=_fingerprint("G3", None, None, ray), progress=progress)
    result["selection"] = "explicit caller-supplied keys"
    result["families"] = len(result["rows"])
    result["depths"] = sum(len(row["depths"]) for row in result["rows"])
    return result


def _progress(row):
    print(json.dumps(dict(gate=row["gate"], idx=row.get("idx"),
                          gate_ok=row.get("gate_ok"), mismatches=row.get("mismatches", []))), flush=True)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--gates", nargs="+", choices=("G1", "G2", "G3"), default=["G1", "G2", "G3"])
    parser.add_argument("--workers", type=int, default=1)
    parser.add_argument("--all-664", action="store_true")
    parser.add_argument("--only-gate664", action="store_true", help="G1 on all 664 at the supplied census caps")
    parser.add_argument("--seconds", type=float, default=DP.FAMILY_SECONDS)
    parser.add_argument("--node-cap", type=int, default=DP.NODE_CAP)
    parser.add_argument("--g3-keys", type=Path, help="JSON array of explicitly selected canonical family keys")
    parser.add_argument("--computed-jsonl", type=Path, help="computed rows for the explicit G3 panel")
    parser.add_argument("--summary", type=Path, help="optional summary JSON inside CODEX")
    args = parser.parse_args(argv)
    gates = ["G1"] if args.only_gate664 else args.gates
    summary = {}
    for gate in gates:
        if gate == "G1":
            result = run_g1(all_664=args.all_664 or args.only_gate664, workers=args.workers,
                            seconds=args.seconds, node_cap=args.node_cap, progress=_progress)
        elif gate == "G2":
            result = run_g2(all_664=args.all_664, workers=args.workers,
                            seconds=args.seconds, node_cap=args.node_cap, progress=_progress)
        elif args.g3_keys is None:
            result = g3_selection_pending()
        else:
            if args.computed_jsonl is None:
                parser.error("--g3-keys requires --computed-jsonl")
            keys = json.loads(args.g3_keys.read_text())
            result = run_g3(keys, list(_jsonl(args.computed_jsonl)), workers=args.workers, progress=_progress)
        summary[gate] = {key: value for key, value in result.items() if key != "rows"}
    if args.summary is not None:
        summary_path = _inside_codex(args.summary)
        summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 1 if any(value.get("passed", value.get("gate_ok")) is False
                    for value in summary.values()) else 0


if __name__ == "__main__":
    raise SystemExit(main())
