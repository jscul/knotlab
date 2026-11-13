"""Resumable reach census. --workers includes the computing parent process.

The CLI never writes outside CODEX. A family has an independent 300-second
alarm, a 300,000-node cap, and a 3 GB resident-memory stop. A monitor reads only
our own process IDs and interrupts a family if aggregate RSS exceeds 7.5 GB.
"""
from __future__ import annotations

import argparse
from collections import deque
import gzip
import hashlib
import json
import multiprocessing as mp
from multiprocessing.connection import wait
import os
from pathlib import Path
import random
import signal
import threading
import time

from reach_dp import HERE, ROOT, compute_family, rss_bytes


def permitted(path):
    path = Path(path).resolve()
    if not path.is_relative_to(HERE):
        raise ValueError(f"Output must be inside CODEX: {path}")
    return path


def dump(path, obj):
    path = permitted(path)
    tmp = path.with_name(path.name+".tmp")
    tmp.write_text(json.dumps(obj, indent=2, sort_keys=True)+"\n")
    tmp.replace(path)


def read_rows(path, recover=False):
    path = Path(path)
    if not path.exists():
        return []
    rows = []
    size = path.stat().st_size
    offset = 0
    with path.open("rb") as stream:
        for number, line in enumerate(stream, 1):
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as exc:
                if recover and stream.tell() == size:
                    permitted(path)
                    digest = hashlib.sha256(line).hexdigest()
                    backup = path.with_name(path.name+".interrupted_tail."+digest+".bin")
                    if backup.exists():
                        if backup.read_bytes() != line:
                            raise ValueError("Interrupted-tail preservation collision")
                    else:
                        backup.write_bytes(line)
                    with path.open("r+b") as repair:
                        repair.truncate(offset)
                    print(json.dumps(dict(resume_recovery=str(path), preserved_tail=str(backup))), flush=True)
                    break
                raise ValueError(f"Invalid JSONL line {number} in {path}; preserve and repair it before resume") from exc
            offset += len(line)
    if recover and rows and offset == size and size and not line.endswith(b"\n"):
        permitted(path)
        with path.open("ab") as stream:
            stream.write(b"\n")
    return rows


def all_keys():
    gate = json.loads((HERE/"replay_gate.json").read_text())
    if gate.get("passed") is not True or hashlib.sha256((HERE/"draws.jsonl.gz").read_bytes()).hexdigest() != gate["draws_sha256"]:
        raise ValueError("G0 or the persisted draw archive failed verification")
    with gzip.open(HERE/"draws.jsonl.gz", "rt") as stream:
        return sorted({json.loads(line)["key"] for line in stream})


def _worker(connection, force_dp, ray):
    signal.signal(signal.SIGUSR1, lambda *_: None)
    while True:
        key = connection.recv()
        if key is None:
            break
        connection.send(compute_family(key, ray=ray, force_dp=force_dp))
    connection.close()


def run_tasks(keys, output, workers=1, force_dp=False, ray="first", progress=True):
    """One writer, newline append and fsync per result; skip existing keys.

    N-1 children plus the parent provide N computing processes, with no
    multiprocessing manager or resource-tracker process. No peer PIDs are read.
    """
    if not 1 <= workers <= 4:
        raise ValueError("workers must be 1..4, including the parent")
    output = permitted(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    existing = read_rows(output, recover=True)
    seen = {r["key"] for r in existing}
    if len(seen) != len(existing):
        raise ValueError("Duplicate keys in existing output")
    requested = set(keys)
    if len(requested) != len(keys):
        raise ValueError("Task list has duplicate family keys")
    tasks = deque(k for k in keys if k not in seen)
    work_lock, write_lock = threading.Lock(), threading.Lock()
    started = time.monotonic()
    info = dict(requested=len(keys), resumed=sum(k in requested for k in seen), written=0,
                workers=workers, aggregate_peak_rss_bytes=rss_bytes(), wall_seconds=0,
                memory_stops=[], processes_include_parent=True)
    pending_parent = [False]
    stop_monitor = threading.Event()
    context = mp.get_context("fork")
    children, active = {}, {}

    def take():
        with work_lock:
            return tasks.popleft() if tasks else None

    idle_handler = signal.signal(signal.SIGUSR1, lambda *_: None)
    with output.open("a", buffering=1) as journal:
        def append(row):
            with write_lock:
                journal.write(json.dumps(row, sort_keys=True)+"\n")
                journal.flush()
                os.fsync(journal.fileno())
                info["written"] += 1
                if progress and (info["written"] % 25 == 0 or row["status"] in ("timeout", "error", "memory_limit", "aggregate_memory_limit")):
                    print(json.dumps(dict(done=info["resumed"]+info["written"], total=len(keys),
                                          seconds=round(time.monotonic()-started, 2),
                                          last_status=row["status"])), flush=True)

        # Fork before starting our collector/monitor threads.
        for _ in range(min(workers-1, max(0, len(tasks)-1))):
            parent, child = context.Pipe()
            process = context.Process(target=_worker, args=(child, force_dp, ray))
            process.start()
            child.close()
            children[parent] = process
            key = take()
            parent.send(key)
            active[parent] = key

        def collect():
            while active:
                ready = wait(list(active), timeout=.25)
                for connection in ready:
                    key = active[connection]
                    try:
                        row = connection.recv()
                    except (EOFError, OSError):
                        row = dict(key=key, ray=ray, status="error", **{"class":"unresolved"},
                                   error="owned worker exited without a result", complete=False, seconds=None)
                    append(row)
                    if children[connection].is_alive():
                        key = take()
                        connection.send(key)
                        if key is not None:
                            active[connection] = key
                            continue
                    active.pop(connection)

        def monitor():
            last_interruption = 0
            while not stop_monitor.wait(.1):
                values = {os.getpid():rss_bytes()}
                values.update({p.pid:rss_bytes(p.pid) for p in children.values() if p.is_alive()})
                total = sum(values.values())
                info["aggregate_peak_rss_bytes"] = max(info["aggregate_peak_rss_bytes"], total)
                if total > 7_500_000_000 and time.monotonic()-last_interruption > 1:
                    candidates = {pid:rss for pid,rss in values.items() if pid != os.getpid() or pending_parent[0]}
                    if candidates:
                        pid = max(candidates, key=candidates.get)
                        try:
                            os.kill(pid, signal.SIGUSR1)
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
                row = compute_family(key, ray=ray, force_dp=force_dp)
                pending_parent[0] = False
                append(row)
            collector.join()
        finally:
            pending_parent[0] = False
            stop_monitor.set()
            monitor_thread.join()
            for connection, process in children.items():
                if process.is_alive():
                    try:
                        connection.send(None)
                    except (BrokenPipeError, OSError):
                        pass
                process.join(timeout=2)
                # Only a process created by this invocation can be terminated.
                if process.is_alive():
                    process.terminate()
                    process.join()
                connection.close()
    signal.signal(signal.SIGUSR1, idle_handler)
    info["wall_seconds"] = round(time.monotonic()-started, 6)
    return info


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workers", type=int, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--only-gate664", action="store_true")
    parser.add_argument("--alt-ray", action="store_true")
    args = parser.parse_args()
    out = permitted(args.out)
    out.mkdir(parents=True, exist_ok=True)
    # Imported lazily so the independent validation module can import run_tasks.
    from validation import run_gate1
    gate = run_gate1(out/"gate664.jsonl", workers=args.workers, all664=True)
    dump(out/"gate664.json", gate)
    if args.only_gate664:
        return 2 if gate["passed"] is False else 0
    if gate["passed"] is False:
        print("G1 did not pass; full census not started", flush=True)
        return 2
    keys = all_keys()
    info = run_tasks(keys, out/"families.jsonl", args.workers)
    dump(out/"run_info.json", info)
    if args.alt_ray:
        rows = read_rows(out/"families.jsonl")
        eligible = sorted(r["key"] for r in rows if not r.get("class", "").startswith("S") and r.get("alt_differs"))
        selected = random.Random(20261113).sample(eligible, min(3000, len(eligible)))
        manifest = dict(seed=20261113, eligible=len(eligible), keys=selected)
        selection_path = out/"alt_selection.json"
        if selection_path.exists() and json.loads(selection_path.read_text()) != manifest:
            raise ValueError("Existing alternative selection differs; do not change a frozen sample")
        if not selection_path.exists():
            dump(selection_path, manifest)
        dump(out/"alt_run_info.json", run_tasks(selected, out/"alt_families.jsonl", args.workers, ray="last"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
