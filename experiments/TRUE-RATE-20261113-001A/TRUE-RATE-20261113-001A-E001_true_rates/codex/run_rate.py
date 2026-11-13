#!/usr/bin/env python
"""Foreground, bounded, append-and-resume runner for the true-rate study.

The parent computes one deterministic lane itself.  At most two forked
children compute the other lanes; no multiprocessing helpers are started.
"""
from __future__ import annotations

import argparse
from contextlib import contextmanager
import errno
import fcntl
import gc
import importlib
import json
import math
import os
from pathlib import Path
import resource
import signal
import stat
import sys
import time

# Apply before loading the study or its NumPy dependency.  This runner is CPU
# only, with one numerical-library thread per process.
for _name in (
    "OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "BLIS_NUM_THREADS",
    "OMP_THREAD_LIMIT",
):
    os.environ[_name] = "1"
for _name in ("CUDA_VISIBLE_DEVICES", "HIP_VISIBLE_DEVICES", "ROCR_VISIBLE_DEVICES"):
    os.environ[_name] = ""

HERE = Path(__file__).resolve().parent
MEMORY_MIB = 2304  # Three processes are below the aggregate 8 GiB ceiling.
MAX_COMMAND_SECONDS = 1190.0
ALARM_GRACE = 0.5
SHUTDOWN_RESERVE = 0.5


class JournalError(ValueError):
    """An existing journal cannot safely be resumed."""


class _FamilyAlarm(BaseException):
    """Bypass ordinary study exceptions at the outer family time limit."""


class _CommandExpired(BaseException):
    pass


class _CommandSignal(BaseException):
    def __init__(self, signum):
        self.signum = signum


def resolve_output(name):
    """Return a canonical output inside CODEX, rejecting escaped symlinks."""
    if not name:
        raise ValueError("--output must name a file inside CODEX")
    raw = Path(name)
    try:
        target = (raw if raw.is_absolute() else HERE / raw).resolve()
    except (OSError, RuntimeError) as exc:
        raise ValueError(f"--output cannot be resolved safely: {exc}") from exc
    try:
        relative = target.relative_to(HERE)
    except ValueError as exc:
        raise ValueError("--output must resolve inside CODEX") from exc
    if not relative.parts:
        raise ValueError("--output must name a file, not the CODEX directory")
    return target


def _open_journal(output):
    """Open through directory descriptors so a symlink race cannot escape.

    resolve_output accepts nested and absolute paths.  Descriptor traversal
    then refuses replacement symlinks, including ones introduced after that
    resolution.  Missing directories are created only after input checks.
    """
    parts = output.relative_to(HERE).parts
    directory = os.open(HERE, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC)
    try:
        for part in parts[:-1]:
            try:
                child = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC,
                                dir_fd=directory)
            except FileNotFoundError:
                try:
                    os.mkdir(part, dir_fd=directory)
                except FileExistsError:
                    pass
                child = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC,
                                dir_fd=directory)
            os.close(directory)
            directory = child
        fd = os.open(parts[-1], os.O_RDWR | os.O_APPEND | os.O_CREAT | os.O_NOFOLLOW |
                     os.O_CLOEXEC | os.O_NONBLOCK, 0o644, dir_fd=directory)
        try:
            if not stat.S_ISREG(os.fstat(fd).st_mode):
                raise ValueError("--output must be a regular file inside CODEX")
            return os.fdopen(fd, "a+b")
        except BaseException:
            os.close(fd)
            raise
    finally:
        os.close(directory)


@contextmanager
def _locked(stream, deadline):
    # A second invocation may be appending.  Do not let its lock consume an
    # unbounded part of this command's foreground budget.
    while True:
        if time.monotonic() >= deadline:
            raise _CommandExpired
        try:
            fcntl.flock(stream.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            break
        except OSError as exc:
            if exc.errno not in (errno.EAGAIN, errno.EACCES):
                raise
            time.sleep(0.01)
    try:
        yield
    finally:
        fcntl.flock(stream.fileno(), fcntl.LOCK_UN)


def _unique_object(pairs):
    obj = {}
    for key, value in pairs:
        if key in obj:
            raise ValueError(f"duplicate object key {key!r}")
        obj[key] = value
    return obj


def _invalid_constant(value):
    raise ValueError(f"non-finite JSON constant {value}")


def read_recorded(stream, known_indices):
    """Strictly validate all existing bytes, returning every recorded index.

    Timeout and error rows count as recorded just like successful rows.  No
    scientific success predicate is used to decide whether to skip a family.
    """
    stream.seek(0)
    seen = set()
    for number, raw in enumerate(stream, 1):
        if not raw.endswith(b"\n"):
            raise JournalError(f"existing JSONL line {number} lacks a final newline; nothing appended")
        if not raw.strip():
            raise JournalError(f"existing JSONL line {number} is blank; nothing appended")
        try:
            row = json.loads(raw.decode("utf-8"), object_pairs_hook=_unique_object,
                             parse_constant=_invalid_constant)
        except (UnicodeError, ValueError, RecursionError) as exc:
            raise JournalError(f"invalid existing JSONL line {number}: {exc}; nothing appended") from exc
        if not isinstance(row, dict) or type(row.get("idx")) is not int:
            raise JournalError(f"existing JSONL line {number} needs an integer idx; nothing appended")
        idx = row["idx"]
        if idx not in known_indices:
            raise JournalError(f"unknown idx {idx} in existing JSONL line {number}; nothing appended")
        if idx in seen:
            raise JournalError(f"duplicate idx {idx} in existing JSONL line {number}; nothing appended")
        seen.add(idx)
    return seen


def append_result(stream, row, known_indices, deadline):
    """Append one flushed, fsynced row unless another run recorded its idx."""
    if not isinstance(row, dict) or type(row.get("idx")) is not int or row["idx"] not in known_indices:
        raise ValueError("computed result does not identify a study family")
    encoded = (json.dumps(row, sort_keys=True, allow_nan=False) + "\n").encode("utf-8")
    with _locked(stream, deadline):
        if row["idx"] in read_recorded(stream, known_indices):
            return False
        stream.seek(0, os.SEEK_END)
        stream.write(encoded)
        stream.flush()
        os.fsync(stream.fileno())
    return True


def _memory_limit():
    requested = MEMORY_MIB * 1024 * 1024
    soft, hard = resource.getrlimit(resource.RLIMIT_AS)
    finite = [value for value in (soft, hard) if value != resource.RLIM_INFINITY]
    limit = min([requested] + finite)
    resource.setrlimit(resource.RLIMIT_AS, (limit, limit))


def _error_result(study, idx, seconds, status, message):
    factory = getattr(study, "error_result", None)
    if factory is not None:
        row = factory(idx, seconds, status, message)
    else:
        # No graph or scientific quantity was established by an outer failure.
        row = {"idx": idx, "closed": False, "complete": False,
               "gate_ok": None, "gate_status": "not_computed", "mismatches": [],
               "lambda": None, "lambda_float": None, "lambda_status": "not_computed",
               "bounded_all": None, "zero_mean": None, "stage": "runner",
               "seconds": round(seconds, 6), "status": status, "error": message}
    row.setdefault("peak_mb", round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024, 3))
    return row


def compute_family(study, idx, defs, reference, seconds_limit):
    """Use cooperative study checks plus a slightly later outer SIGALRM."""
    started = time.monotonic()

    def alarm(signum, frame):
        raise _FamilyAlarm

    previous = signal.signal(signal.SIGALRM, alarm)
    signal.setitimer(signal.ITIMER_REAL, seconds_limit + ALARM_GRACE)
    try:
        row = study.run_family(idx, defs=defs, reference=reference, seconds_limit=seconds_limit)
        if not isinstance(row, dict) or type(row.get("idx")) is not int or row["idx"] != idx:
            raise ValueError("run_family returned an invalid or different idx")
        # Reject invalid JSON before it can damage the append-only journal.
        json.dumps(row, allow_nan=False)
        return row
    except _FamilyAlarm:
        return _error_result(study, idx, time.monotonic() - started, "timeout",
                             "outer per-family SIGALRM limit reached")
    except MemoryError:
        return _error_result(study, idx, time.monotonic() - started, "memory_limit",
                             f"per-process address-space ceiling is {MEMORY_MIB} MiB")
    except Exception as exc:
        return _error_result(study, idx, time.monotonic() - started, "error",
                             f"{type(exc).__name__}: {exc}")
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, previous)


def _run_lane(study, indices, families, reference, output, seconds_limit, deadline):
    known = set(families)
    with _open_journal(output) as stream:
        for idx in indices:
            # Preserve enough foreground time for the hard family alarm and
            # reaping.  Unstarted indices remain absent and resumable.
            if time.monotonic() + seconds_limit + ALARM_GRACE >= deadline:
                return
            with _locked(stream, deadline):
                if idx in read_recorded(stream, known):
                    continue
            row = compute_family(study, idx, families[idx], reference.get(idx), seconds_limit)
            if append_result(stream, row, known, deadline):
                progress = {key: row.get(key) for key in ("idx", "status", "closed", "complete", "seconds")}
                print(json.dumps(progress, sort_keys=True, allow_nan=False), flush=True)
            del row
            gc.collect()


def _interrupt(signum, frame):
    raise _CommandSignal(signum)


def _child_lane(study, indices, families, reference, output, seconds_limit, deadline, previous_mask):
    # Even a signal delivered immediately upon unblocking must exit the child,
    # rather than returning from main into an embedding caller's code.
    try:
        signal.pthread_sigmask(signal.SIG_SETMASK, previous_mask)
        _run_lane(study, indices, families, reference, output, seconds_limit, deadline)
    except _CommandExpired:
        os._exit(0)
    except _CommandSignal as exc:
        os._exit(128 + exc.signum)
    except BaseException as exc:
        print(f"run_rate.py: child lane failed: {type(exc).__name__}: {exc}",
              file=sys.stderr, flush=True)
        os._exit(1)
    os._exit(0)


def _reap_ready(children):
    for pid in list(children):
        try:
            got, status = os.waitpid(pid, os.WNOHANG)
        except InterruptedError:
            continue
        if got:
            children.pop(pid)
            if os.waitstatus_to_exitcode(status) != 0:
                yield pid, os.waitstatus_to_exitcode(status)


def _stop_children(children):
    """Signal and reap only the children created by this invocation."""
    for pid in children:
        try:
            os.kill(pid, signal.SIGTERM)
        except ProcessLookupError:
            pass
    until = time.monotonic() + 0.15
    while children and time.monotonic() < until:
        list(_reap_ready(children))
        if children:
            time.sleep(0.01)
    for pid in children:
        try:
            os.kill(pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
    for pid in list(children):
        while True:
            try:
                os.waitpid(pid, 0)
                break
            except InterruptedError:
                continue
        children.pop(pid)


def _arguments(argv):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workers", type=int, default=1,
                        help="1..3 total processes, including this active parent")
    parser.add_argument("--only", nargs="+", type=int, metavar="IDX")
    parser.add_argument("--seconds-limit", type=float, default=60.0,
                        help="positive finite per-family seconds, below 1190 (default: 60)")
    parser.add_argument("--output", default="true_rates.jsonl",
                        help="relative or absolute output path resolving inside CODEX")
    parser.add_argument("--command-seconds", type=float, default=MAX_COMMAND_SECONDS,
                        help="foreground command ceiling, at most 1190 seconds")
    args = parser.parse_args(argv)
    if not 1 <= args.workers <= 3:
        parser.error("--workers must be 1..3 total processes, including the parent")
    if not math.isfinite(args.seconds_limit) or not 0 < args.seconds_limit < MAX_COMMAND_SECONDS:
        parser.error("--seconds-limit must be finite, positive, and below 1190")
    if not math.isfinite(args.command_seconds) or not 0 < args.command_seconds <= MAX_COMMAND_SECONDS:
        parser.error("--command-seconds must be finite, positive, and at most 1190")
    return args


def main(argv=None):
    started = time.monotonic()
    args = _arguments(argv)
    deadline = started + args.command_seconds - SHUTDOWN_RESERVE
    children = {}
    previous_handlers = {}
    try:
        output = resolve_output(args.output)
        _memory_limit()
        study = importlib.import_module("true_rate")
        families = study.study_families()
        if not isinstance(families, dict) or any(type(idx) is not int for idx in families):
            raise ValueError("study_families must return a dictionary of integer indices")
        selected = sorted(set(args.only) if args.only is not None else families)
        unknown = set(selected) - set(families)
        if unknown:
            raise ValueError(f"indices outside the study: {sorted(unknown)}; nothing written")
        reference = study.reference_rows()
        if not isinstance(reference, dict):
            raise ValueError("reference_rows must return a dictionary")
        # Close this descriptor before fork: flock locks inherited through the
        # same open-file description would not exclude our own other lanes.
        with _open_journal(output) as stream:
            with _locked(stream, deadline):
                recorded = read_recorded(stream, set(families))
        pending = [idx for idx in selected if idx not in recorded]
        workers = min(args.workers, len(pending))
        for signum in (signal.SIGINT, signal.SIGTERM):
            previous_handlers[signum] = signal.signal(signum, _interrupt)
        for lane in range(1, workers):
            # Register each new child before a user interrupt can start the
            # cleanup path.  Children do not inherit ownership of siblings.
            previous_mask = signal.pthread_sigmask(signal.SIG_BLOCK,
                                                    {signal.SIGINT, signal.SIGTERM})
            try:
                pid = os.fork()
                if pid == 0:
                    children.clear()
                    _child_lane(study, pending[lane::workers], families, reference, output,
                                args.seconds_limit, deadline, previous_mask)
                else:
                    children[pid] = lane
            finally:
                signal.pthread_sigmask(signal.SIG_SETMASK, previous_mask)
        child_errors = []
        if workers:
            _run_lane(study, pending[::workers], families, reference, output,
                      args.seconds_limit, deadline)
        while children:
            child_errors.extend(_reap_ready(children))
            if not children:
                break
            if time.monotonic() >= deadline:
                _stop_children(children)
                break
            time.sleep(0.02)
        with _open_journal(output) as stream:
            with _locked(stream, started + args.command_seconds - 0.05):
                recorded = read_recorded(stream, set(families))
        remaining = [idx for idx in selected if idx not in recorded]
        print(json.dumps({"runner_status": "worker_error" if child_errors else
                          "command_limit" if remaining else "done",
                          "selected": len(selected), "recorded": len(selected) - len(remaining),
                          "remaining": remaining, "workers": workers,
                          "wall_seconds": round(time.monotonic() - started, 6)}, sort_keys=True), flush=True)
        if child_errors:
            print(f"run_rate.py: child process failures: {child_errors}", file=sys.stderr, flush=True)
            return 1
        return 0
    except _CommandExpired:
        print("run_rate.py: command time budget reached; unrecorded families remain resumable",
              file=sys.stderr, flush=True)
        return 0
    except _CommandSignal as exc:
        print(f"run_rate.py: interrupted by signal {exc.signum}", file=sys.stderr, flush=True)
        return 128 + exc.signum
    except (OSError, ValueError, ImportError, MemoryError) as exc:
        print(f"run_rate.py: error: {exc}", file=sys.stderr, flush=True)
        return 2
    finally:
        # Repeated terminal interrupts must not bypass reaping our children.
        for signum in previous_handlers:
            signal.signal(signum, signal.SIG_IGN)
        _stop_children(children)
        for signum, handler in previous_handlers.items():
            signal.signal(signum, handler)


if __name__ == "__main__":
    sys.exit(main())
