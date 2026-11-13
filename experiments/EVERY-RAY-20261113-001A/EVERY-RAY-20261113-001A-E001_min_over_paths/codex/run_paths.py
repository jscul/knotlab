"""Resumable all-path computation; N workers includes the computing parent.

Only this invocation's forked processes are monitored.  Fork/Pipe uses no
manager or resource-tracker auxiliary process.  All writes stay under CODEX.
"""
from __future__ import annotations

import argparse
from collections import deque
from datetime import datetime, timezone
import hashlib
import json
import multiprocessing as mp
from multiprocessing.connection import wait
import os
from pathlib import Path
import signal
import threading
import time

from paths_dp import HERE, compute_family, load_census_records, rss_bytes


def permitted(path):
    path = Path(path).resolve()
    if not path.is_relative_to(HERE):
        raise ValueError(f"Output must be inside CODEX: {path}")
    return path


def dump(path, obj):
    path = permitted(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    with tmp.open("w") as stream:
        stream.write(json.dumps(obj, indent=2, sort_keys=True) + "\n")
        stream.flush()
        os.fsync(stream.fileno())
    tmp.replace(path)
    descriptor = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def code_fingerprint():
    """Fingerprint executable producer and its actual permitted dependencies."""
    import paths_dp
    modules = (paths_dp, paths_dp.CENSUS, paths_dp.GA, paths_dp.L, paths_dp.CENSUS.LS)
    files = {Path(__file__).resolve(), *(Path(module.__file__).resolve() for module in modules)}
    files.add(HERE / "call_symmetry.py")
    hashes = {str(path.relative_to(paths_dp.ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
              for path in sorted(files)}
    encoded = json.dumps(hashes, sort_keys=True, separators=(",", ":")).encode()
    archive = hashlib.sha256()
    with paths_dp.CENSUS_RECORDS.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            archive.update(block)
    return dict(code_fingerprint=hashlib.sha256(encoded).hexdigest(), code_sha256=hashes,
                census_archive_sha256=archive.hexdigest())


def read_rows(path, recover=False):
    path = Path(path)
    if not path.exists():
        return []
    rows, offset = [], 0
    size = path.stat().st_size
    last_line = b""
    with path.open("rb") as stream:
        for number, line in enumerate(stream, 1):
            last_line = line
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as exc:
                if recover and stream.tell() == size:
                    permitted(path)
                    digest = hashlib.sha256(line).hexdigest()
                    backup = path.with_name(path.name + ".interrupted_tail." + digest + ".bin")
                    if backup.exists():
                        if backup.read_bytes() != line:
                            raise ValueError("Interrupted-tail preservation collision")
                    else:
                        backup.write_bytes(line)
                    with path.open("r+b") as repair:
                        repair.truncate(offset)
                    print(json.dumps(dict(resume_recovery=str(path), preserved_tail=str(backup))), flush=True)
                    break
                raise ValueError(f"Invalid JSONL line {number} in {path}") from exc
            offset += len(line)
    if recover and rows and offset == size and size and not last_line.endswith(b"\n"):
        permitted(path)
        with path.open("ab") as stream:
            stream.write(b"\n")
    return rows


def _failure(key, census_row, error):
    from paths_dp import self_call_count
    return dict(key=key, c=self_call_count(key), first_ray_class=None if census_row is None else census_row.get("class"),
                path_class="unresolved", status="error", **{"class": "unresolved"},
                error=error, complete=False, seconds=None, nodes=0, L_path=[], lambda_path=None)


def _worker(connection, options):
    signal.signal(signal.SIGUSR1, lambda *_: None)
    while True:
        payload = connection.recv()
        if payload is None:
            break
        key, census_row = payload
        connection.send(compute_family(key, census_row=census_row, **options))
    connection.close()


def run_tasks(keys, output, workers=1, census_records=None, progress=True,
              force_dp=False, check_fixed_rays=True, seconds=300, node_cap=300_000):
    """Append/fsync one row per key, skipping every existing recorded key.

    ``keys`` is any iterable of unique family-key strings. ``census_records``
    may supply an already loaded key->row dictionary; otherwise the authorized
    archive is loaded once.  The full runner passes all population keys, so c=1
    and S1/S2/S3 rows are carried as well as the newly computed c>=2 rows.
    Atomic ``<output>.run_info.json`` telemetry is saved before work, after
    every fsynced row, and on exit; resumed attempts retain prior telemetry.
    """
    if not 1 <= workers <= 3:
        raise ValueError("workers must be 1..3, including the computing parent")
    keys = list(keys)
    if len(set(keys)) != len(keys):
        raise ValueError("Task list has duplicate family keys")
    records = load_census_records() if census_records is None else census_records
    missing = [key for key in keys if key not in records]
    if missing:
        raise ValueError(f"{len(missing)} keys are missing from the census input")
    output = permitted(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    existing = read_rows(output, recover=True)
    seen = {row["key"] for row in existing}
    if len(seen) != len(existing):
        raise ValueError("Duplicate keys in existing output")
    requested = set(keys)
    del existing
    tasks = deque(key for key in keys if key not in seen)
    work_lock, write_lock, info_lock = threading.Lock(), threading.Lock(), threading.RLock()
    started = time.monotonic()
    telemetry_path = output.with_name(output.name + ".run_info.json")
    provenance = code_fingerprint()
    requested_options = dict(force_dp=force_dp, check_fixed_rays=check_fixed_rays,
                             seconds=seconds, node_cap=node_cap)
    history = []
    if telemetry_path.exists():
        previous = json.loads(telemetry_path.read_text())
        if seen and previous.get("code_fingerprint") != provenance["code_fingerprint"]:
            raise ValueError("Existing rows were made by different code; preserve them and use a fresh output")
        if seen and previous.get("census_archive_sha256") != provenance["census_archive_sha256"]:
            raise ValueError("Existing rows use a different census archive; use a fresh output")
        if seen and previous.get("options") != requested_options:
            raise ValueError("Existing rows use different computation options; use a fresh output")
        history = previous.get("history", [])
        if not isinstance(history, list):
            raise ValueError("Existing run telemetry history is not a list")
        history = history + [{key: value for key, value in previous.items() if key != "history"}]
    elif seen:
        history = [dict(status="unrecorded_previous_attempt", recorded_rows=len(seen),
                        wall_seconds=None, aggregate_peak_rss_bytes=None)]
    info = dict(requested=len(keys), resumed=sum(key in requested for key in seen), written=0,
                workers=workers, processes_include_parent=True, resource_tracker=False,
                aggregate_peak_rss_bytes=rss_bytes(), wall_seconds=0, memory_stops=[],
                schema_version=1, status="starting", attempt=len(history) + 1, history=history,
                started_at=datetime.now(timezone.utc).isoformat(), updated_at=None,
                telemetry_path=str(telemetry_path), output=str(output), own_process_ids=[os.getpid()],
                options=requested_options)
    info.update(provenance)
    pending_parent = [False]
    stop_monitor = threading.Event()
    context = mp.get_context("fork")
    children, active = {}, {}
    options = info["options"]

    def persist():
        with info_lock:
            info["wall_seconds"] = round(time.monotonic() - started, 6)
            info["updated_at"] = datetime.now(timezone.utc).isoformat()
            info["own_process_ids"] = [os.getpid()] + [process.pid for process in children.values()]
            total = rss_bytes() + sum(rss_bytes(process.pid) for process in children.values() if process.is_alive())
            info["aggregate_peak_rss_bytes"] = max(info["aggregate_peak_rss_bytes"], total)
            dump(telemetry_path, info)

    persist()

    def take():
        with work_lock:
            return tasks.popleft() if tasks else None

    idle_handler = signal.signal(signal.SIGUSR1, lambda *_: None)
    with output.open("a", buffering=1) as journal:
        def append(row):
            with write_lock:
                journal.write(json.dumps(row, sort_keys=True) + "\n")
                journal.flush()
                os.fsync(journal.fileno())
                with info_lock:
                    info["written"] += 1
                persist()
                if progress and (info["written"] % 25 == 0 or row["status"] in
                                 ("timeout", "error", "memory_limit", "aggregate_memory_limit")):
                    print(json.dumps(dict(done=info["resumed"] + info["written"], total=len(keys),
                                          seconds=round(time.monotonic() - started, 2),
                                          last_status=row["status"])), flush=True)

        # Fork before starting threads, with at most N-1 children.
        for _ in range(min(workers - 1, max(0, len(tasks) - 1))):
            parent, child = context.Pipe()
            process = context.Process(target=_worker, args=(child, options))
            process.start()
            child.close()
            children[parent] = process
            key = take()
            parent.send((key, records[key]))
            active[parent] = key
        info["status"] = "running"
        persist()

        def collect():
            while active and not stop_monitor.is_set():
                ready = wait(list(active), timeout=.25)
                for connection in ready:
                    if stop_monitor.is_set():
                        return
                    key = active[connection]
                    try:
                        row = connection.recv()
                    except (EOFError, OSError):
                        row = _failure(key, records[key], "owned worker exited without a result")
                    append(row)
                    if children[connection].is_alive():
                        key = take()
                        try:
                            connection.send(None if key is None else (key, records[key]))
                        except (BrokenPipeError, OSError):
                            if key is not None:
                                append(_failure(key, records[key], "owned worker exited before accepting its next family"))
                        else:
                            if key is not None:
                                active[connection] = key
                                continue
                    active.pop(connection)

        def monitor():
            last_interruption = 0
            while not stop_monitor.wait(.1):
                values = {os.getpid(): rss_bytes()}
                values.update({p.pid: rss_bytes(p.pid) for p in children.values() if p.is_alive()})
                total = sum(values.values())
                with info_lock:
                    info["aggregate_peak_rss_bytes"] = max(info["aggregate_peak_rss_bytes"], total)
                if total > 7_500_000_000 and time.monotonic() - last_interruption > 1:
                    candidates = {pid: rss for pid, rss in values.items()
                                  if pid != os.getpid() or pending_parent[0]}
                    if candidates:
                        pid = max(candidates, key=candidates.get)
                        try:
                            os.kill(pid, signal.SIGUSR1)
                            with info_lock:
                                info["memory_stops"].append(dict(pid=pid, aggregate_rss_bytes=total))
                        except ProcessLookupError:
                            pass
                        last_interruption = time.monotonic()

        collector = threading.Thread(target=collect, daemon=True)
        monitor_thread = threading.Thread(target=monitor, daemon=True)
        collector.start()
        monitor_thread.start()
        try:
            while (key := take()) is not None:
                pending_parent[0] = True
                row = compute_family(key, census_row=records[key], **options)
                pending_parent[0] = False
                append(row)
            collector.join()
            info["status"] = "done"
        except BaseException as exc:
            with info_lock:
                info["status"] = "interrupted" if isinstance(exc, (KeyboardInterrupt, SystemExit)) else "error"
                info["interruption"] = repr(exc)
            raise
        finally:
            pending_parent[0] = False
            stop_monitor.set()
            monitor_thread.join()
            collector.join()
            for connection, process in children.items():
                if process.is_alive():
                    try:
                        connection.send(None)
                    except (BrokenPipeError, OSError):
                        pass
                process.join(timeout=2)
                # This invocation alone created every process in this list.
                if process.is_alive():
                    process.terminate()
                    process.join()
                connection.close()
            signal.signal(signal.SIGUSR1, idle_handler)
            persist()
    return info


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workers", type=int, required=True, choices=(1, 2, 3))
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    out = permitted(args.out)
    out.mkdir(parents=True, exist_ok=True)
    records = load_census_records()
    # This mandatory gate is part of the future full-run entry point.  The
    # hand-off never calls main(), and its 60-case rehearsal is separate.
    import validate_paths as validation
    manifest = json.loads((HERE / "gate_last_keys.json").read_text())
    wanted = sorted(manifest["keys"])
    if len(wanted) != 224 or len(set(wanted)) != 224:
        raise ValueError("G-last manifest must contain exactly 224 distinct keys")
    by_key = {case["key"]: case for case in manifest["cases"]}
    cases = [dict(by_key.get(key, {}), key=key, census=records[key]) for key in wanted]
    gate = validation.run_jobs("G-last", cases, out / "gate_last_all224.jsonl",
                               workers=args.workers, config=validation._code_fingerprint(300, 300_000))
    dump(out / "gate_last_all224.json", gate)
    if gate.get("passed") is not True or gate.get("rows") != 224:
        raise RuntimeError("Full population not started: mandatory all-224 G-last gate did not pass completely")
    info = run_tasks(sorted(records), out / "families.jsonl", workers=args.workers, census_records=records)
    info["input"] = "artifacts/REACH-CENSUS-20261113-001A/REACH-CENSUS-20261113-001A-E001_reach_census/families.jsonl.gz"
    dump(out / "run_info.json", info)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
