#!/usr/bin/env python
"""Foreground, append-and-resume TRUE-BOND runner. The full run is not automatic."""
from __future__ import annotations

import argparse
import fcntl
import json
import multiprocessing as mp
import os
from pathlib import Path
import resource
import signal
import sys
import time

# Set before importing BD/numpy in this process or spawned processes.
for variable in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ[variable] = "1"

from true_bond import FamilyDP, HERE, bd_ray_values, study_families


def compute_family(task):
    idx, defs, smax, seconds_limit = task
    started = time.monotonic()
    row = {"idx": idx, "L": [None] * 12, "L_ray": [None] * 12,
           "generic_summaries": 0, "seconds": None, "peak_mb": None,
           "status": "running", "smax": smax, "generic_by_s": [], "ray_check": []}
    dp = None
    try:
        row["stage"] = "BD_reference"
        dp = FamilyDP(defs, deadline=started + seconds_limit)
        reference, bd_result = bd_ray_values(defs, smax)
        row["bd_reference"] = reference
        row["bd_repeat"] = bd_result.get("rate")
        row["shape"] = {"locals": dp.locals, "self_calls": dp.nchild, "knots": len(dp.knots)}
        row["stage"] = "ray_check"
        for s, expected in enumerate(reference, 1):
            if expected is None:
                row["status"] = "incomplete_ray_reference"
                break
            observed = dp.least(s, expected, ray_only=True)
            row["L_ray"][s - 1] = observed
            check = {"s": s, "expected": expected, "observed": observed, "pass": observed == expected}
            row["ray_check"].append(check)
            if observed != expected:
                row["status"] = "failed_ray_check"
                break
        if row["status"] == "running" and len(reference) != smax:
            row["status"] = "incomplete_ray_reference"
        if row["status"] == "running":
            row["stage"] = "true_minimum"
        for s, observed in enumerate(row["L_ray"][:smax], 1):
            if row["status"] != "running":
                break
            row["active_s"] = s
            row["L"][s - 1] = dp.least(s, observed)
            row["generic_summaries"] = len(dp.generic)
            row["generic_by_s"].append({"s": s, "cap": observed - 2, "size": len(dp.generic)})
            if row["L"][s - 1] is None:
                row["status"] = "failed_missing_ray_bound"
                break
        if row["status"] == "running":
            row["status"] = "done"
            row["stage"] = "complete"
    except TimeoutError as exc:
        row["status"] = "timeout"
        row["error"] = str(exc)
    except MemoryError:
        row["status"] = "memory_limit"
        row["error"] = "per-worker address-space limit reached"
    except Exception as exc:
        row["status"] = "error"
        row["error"] = f"{type(exc).__name__}: {exc}"
    finally:
        if dp is not None:
            row["fixed_point_rounds"] = dp.generic_rounds
            row["operations"] = dp.operations
            row["generic_summaries"] = len(dp.generic)
        row["seconds"] = round(time.monotonic() - started, 6)
        # Linux ru_maxrss is KiB. Each spawned worker handles exactly one family.
        row["peak_mb"] = round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024, 3)
    return row


def _worker(task, sender, memory_mb):
    try:
        signal.signal(signal.SIGTERM, signal.SIG_DFL)
        signal.signal(signal.SIGINT, signal.SIG_DFL)
        signal.pthread_sigmask(signal.SIG_UNBLOCK, {signal.SIGINT, signal.SIGTERM})
        if memory_mb:
            limit = memory_mb * 1024 * 1024
            resource.setrlimit(resource.RLIMIT_AS, (limit, limit))
        sender.send(compute_family(task))
    finally:
        sender.close()


def run_tasks(tasks, workers, memory_mb):
    """Bounded owned children, including explicit lost-worker recovery.

    fork plus Pipes needs no resource-tracker child or queue helper process.
    A new child handles each family so RSS high-water marks are per-family.
    """
    context = mp.get_context("fork")
    pending = iter(tasks)
    active = {}
    exhausted = False
    try:
        while active or not exhausted:
            while len(active) < workers and not exhausted:
                try:
                    task = next(pending)
                except StopIteration:
                    exhausted = True
                    break
                receiver, sender = context.Pipe(duplex=False)
                process = context.Process(target=_worker, args=(task, sender, memory_mb))
                started = time.monotonic()
                previous_mask = signal.pthread_sigmask(signal.SIG_BLOCK, {signal.SIGINT, signal.SIGTERM})
                try:
                    process.start()
                    active[process.pid] = (process, receiver, task, started, 0.0)
                except BaseException:
                    if process.pid is not None:
                        if process.is_alive():
                            process.kill()
                        process.join()
                    receiver.close()
                    raise
                finally:
                    sender.close()
                    signal.pthread_sigmask(signal.SIG_SETMASK, previous_mask)
            for pid, (process, receiver, task, started, peak) in list(active.items()):
                # Reading only this runner's own child status, never peer tasks.
                try:
                    for line in Path(f"/proc/{pid}/status").read_text().splitlines():
                        if line.startswith("VmHWM:"):
                            peak = max(peak, int(line.split()[1]) / 1024)
                            break
                except FileNotFoundError:
                    pass
                active[pid] = (process, receiver, task, started, peak)
                elapsed = time.monotonic() - started
                row = None
                if receiver.poll():
                    try:
                        row = receiver.recv()
                    except (EOFError, OSError):
                        pass
                expired = elapsed > task[3] + 1.0
                if row is None and (process.exitcode is not None or expired):
                    if process.is_alive():
                        process.kill()
                    process.join()
                    # A result may have arrived between the first poll and
                    # exitcode observation. Drain it before declaring failure.
                    if receiver.poll():
                        try:
                            row = receiver.recv()
                        except (EOFError, OSError):
                            pass
                    if row is None:
                        row = {"idx": task[0], "L": [None] * 12, "L_ray": [None] * 12,
                               "generic_summaries": 0, "seconds": round(elapsed, 6),
                               "peak_mb": round(peak, 3), "smax": task[2],
                               "status": "timeout" if expired else "worker_crash",
                               "error": "worker did not return a result", "worker_exitcode": process.exitcode}
                if row is not None:
                    process.join(timeout=1)
                    if process.is_alive():
                        process.kill()
                        process.join()
                    receiver.close()
                    del active[pid]
                    yield row
            if active:
                time.sleep(0.02)
    finally:
        for process, receiver, _, _, _ in active.values():
            if process.is_alive():
                process.kill()
            process.join()
            receiver.close()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workers", type=int, default=1, help="1..3 workers; parent plus workers <=4 processes")
    parser.add_argument("--only", nargs="+", type=int)
    parser.add_argument("--smax", type=int, choices=range(1, 13), default=12)
    parser.add_argument("--output", default="true_rates.jsonl", help="basename inside CODEX")
    parser.add_argument("--seconds-limit", type=float, default=1100, help="per family, <1200 seconds")
    parser.add_argument("--memory-mb", type=int, default=1024, help="per-worker address-space ceiling (MiB)")
    args = parser.parse_args(argv)
    if not 1 <= args.workers <= 3:
        parser.error("--workers must be 1..3 (including the coordinator, at most 4 processes)")
    if not 0 < args.seconds_limit < 1200:
        parser.error("--seconds-limit must be positive and below 1200")
    if args.memory_mb < 128:
        parser.error("--memory-mb must be at least 128")
    if Path(args.output).name != args.output or args.output in (".", ".."):
        parser.error("--output must be a filename inside CODEX")
    output = HERE / args.output
    if output.is_symlink():
        parser.error("--output cannot be a symlink")
    families = study_families()
    only = sorted(set(args.only)) if args.only else sorted(families)
    missing = set(only) - set(families)
    if missing:
        parser.error(f"indices outside the 226-family study: {sorted(missing)}")
    with output.open("a+", buffering=1) as stream:
        try:
            fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            parser.error("another runner is writing this exact output file")
        completed = set()
        stream.seek(0)
        if output.stat().st_size:
            for number, line in enumerate(stream, 1):
                if not line.strip():
                    continue
                try:
                    completed.add(json.loads(line)["idx"])
                except (ValueError, KeyError, TypeError) as exc:
                    parser.error(f"invalid existing JSONL line {number}: {exc}; nothing appended")
            if not line.endswith("\n"):
                parser.error("existing JSONL lacks a final newline; nothing appended")
        stream.seek(0, os.SEEK_END)
        tasks = [(idx, families[idx], args.smax, args.seconds_limit) for idx in only if idx not in completed]
        def retain(row):
            encoded = json.dumps(row, sort_keys=True)
            stream.write(encoded + "\n")
            stream.flush()
            os.fsync(stream.fileno())
            print(json.dumps({key: row[key] for key in ("idx", "status", "seconds", "peak_mb")}), flush=True)
        previous = signal.signal(signal.SIGTERM, lambda signum, frame: sys.exit(143))
        rows = run_tasks(tasks, args.workers, args.memory_mb)
        try:
            for row in rows:
                retain(row)
        finally:
            rows.close()
            signal.signal(signal.SIGTERM, previous)
    return 0


if __name__ == "__main__":
    sys.exit(main())
