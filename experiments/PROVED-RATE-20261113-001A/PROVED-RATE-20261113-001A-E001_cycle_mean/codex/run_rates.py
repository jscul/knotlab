"""Run the specified 664-family calculation, with bounded family workers."""

import argparse
import collections
import hashlib
import json
import multiprocessing as mp
import os
from pathlib import Path
import signal
import sys
import time
import traceback
from multiprocessing.connection import wait

# Apply before importing NumPy (including through ray_dp / BD).
for _name in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ[_name] = "1"

from ray_dp import BD, BD_PATH, RECORD_PATH, FamilyDP, INF

HERE = Path(__file__).resolve().parent
NODE_CAP = 2_000_000
FAMILY_SECONDS = 1_200


class FamilyTimeout(Exception):
    pass


def record_class(record):
    """Classify only where the literal requested definition is unambiguous."""
    if record.get("unfinished"):
        return "capped", None
    values = record.get("L", [])
    if len(values) == 30:
        if values[-1] > values[0]:
            return "rising", None
        if values[-1] == values[0]:
            return "flat", None
        return "capped", None
    if not values:
        return "capped", None
    if len(values) < 30:
        tail = values[-8:]
        finite_tail = [v for v in tail if v < INF]
        if len(tail) < 8 and len(set(finite_tail)) <= 1:
            return None, "Fewer than 8 depths; last-8 finite-constant predicate unspecified."
        if not finite_tail:
            return None, "No finite value in the last 8 depths; constant finite predicate unspecified."
        if len(set(finite_tail)) == 1 and any(v >= INF for v in tail):
            return None, "Constant finite values mixed with INF; last-8 predicate unspecified."
        if len(tail) == 8 and len(set(tail)) == 1 and tail[0] < INF:
            return "bounded", None
    return "capped", None


def build_graph(ctx, result, checkpoint):
    starts = ctx.start_nodes()
    nodes = list(starts)
    ids = {node: i for i, node in enumerate(nodes)}
    start_cost = {ids[node]: cost for node, cost in starts.items()}
    adj, close_cost, empty_next = [], [], []
    hit_cap = False
    i = 0
    try:
        while i < len(nodes):
            if i % 128 == 0:
                result["nodes"] = len(nodes)
                result["expanded_nodes"] = i
                checkpoint()
            node = nodes[i]
            edges = []
            empty = None
            for W, node2, cost in ctx.middle(node):
                j = ids.get(node2)
                if j is None:
                    if len(nodes) >= NODE_CAP:
                        hit_cap = True
                        continue
                    j = len(nodes)
                    ids[node2] = j
                    nodes.append(node2)
                edges.append((j, cost))
                if not W:
                    assert cost == 0
                    empty = j
            adj.append(edges)
            close_cost.append(ctx.close(node))
            empty_next.append(empty)
            i += 1
    finally:
        # Also retain exact discovered/expanded counts if the family alarm
        # interrupts graph expansion in the middle of a node.
        result["nodes"] = len(nodes)
        result["expanded_nodes"] = len(empty_next)
    # The specification requires the frontier to empty BEFORE the node cap.
    result["complete"] = not hit_cap and len(nodes) < NODE_CAP
    result["edges"] = sum(map(len, adj))
    return adj, close_cost, empty_next, start_cost


def recompute_layers(adj, close_cost, start_cost, values, checkpoint):
    layer = start_cost
    computed, mismatches = [], []
    for s, recorded in enumerate(values, 1):
        checkpoint()
        best = INF
        for node, cost in layer.items():
            if close_cost[node] < INF:
                best = min(best, cost + close_cost[node])
        computed.append(best)
        if best != recorded:
            mismatches.append(dict(s=s, yours=best, record=recorded))
        if s == len(values):
            break
        next_layer = {}
        for node, cost in layer.items():
            for node2, delta in adj[node]:
                nc = cost + delta
                if nc < next_layer.get(node2, INF):
                    next_layer[node2] = nc
        layer = next_layer
    return computed, mismatches


def compute_family(idx, defs, record, send_progress=None):
    from graph_algorithms import analyze_graph

    t0 = time.monotonic()
    klass, class_ambiguity = record_class(record)
    result = dict(idx=idx, nodes=0, expanded_nodes=0, complete=False,
                  gate_ok=None, mismatches=[], **{"lambda": None},
                  lambda_float=None, lambda_status="not_computed",
                  bounded_all=None, zero_mean=None, seconds=None,
                  status="running", stage="initialization", record_class=klass,
                  record_class_ambiguity=class_ambiguity,
                  record_depths=len(record.get("L", [])))
    stage_times = {}
    stage_started = t0
    last_progress = t0

    def checkpoint():
        nonlocal last_progress
        now = time.monotonic()
        if now - t0 >= FAMILY_SECONDS:
            raise FamilyTimeout
        if send_progress and now - last_progress >= 10:
            send_progress(dict(idx=idx, stage=result["stage"], nodes=result["nodes"],
                               expanded_nodes=result["expanded_nodes"], seconds=now-t0))
            last_progress = now

    def stage(name):
        nonlocal stage_started
        now = time.monotonic()
        stage_times[result["stage"]] = now - stage_started
        result["stage"] = name
        stage_started = now
        checkpoint()

    def alarm_handler(signum, frame):
        raise FamilyTimeout

    old_handler = signal.signal(signal.SIGALRM, alarm_handler)
    signal.setitimer(signal.ITIMER_REAL, FAMILY_SECONDS)
    try:
        ctx = FamilyDP(defs)
        stage("reachable_graph")
        adj, close_cost, empty_next, starts = build_graph(ctx, result, checkpoint)
        # Graph and its integer weights now contain everything needed below.
        del ctx
        stage("gate")
        values = record.get("L", [])
        if values:
            computed, mismatches = recompute_layers(adj, close_cost, starts, values, checkpoint)
            result["L_recomputed"] = computed
            result["mismatches"] = [dict(idx=idx, **m) for m in mismatches]
            result["gate_ok"] = not mismatches
            result["gate_status"] = "checked" if result["complete"] else "checked_partial_graph"
        else:
            result["L_recomputed"] = []
            result["gate_status"] = "skipped_no_record_L"
        stage("trim_scc_karp_bounded")
        result.update(analyze_graph(adj, close_cost, empty_next, result["complete"], checkpoint))
        result["status"] = "done"
    except FamilyTimeout:
        result["status"] = "timeout"
        result["timeout_stage"] = result["stage"]
    except Exception as exc:
        result["status"] = "error"
        result["error"] = repr(exc)
        result["traceback"] = traceback.format_exc()
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, old_handler)
        result["seconds"] = round(time.monotonic() - t0, 6)
        stage_times[result["stage"]] = time.monotonic() - stage_started
        result["stage_seconds"] = {k: round(v, 6) for k, v in stage_times.items()}
    return result


def worker_loop(conn):
    while True:
        task = conn.recv()
        if task is None:
            break
        idx, defs, record = task
        conn.send(("started", dict(idx=idx, pid=os.getpid())))
        result = compute_family(idx, defs, record,
                                lambda data: conn.send(("progress", data)))
        conn.send(("result", result))
    conn.close()


def counts(rows):
    return dict(families=len(rows), complete=sum(r["complete"] for r in rows),
                gate_mismatches_total=sum(len(r["mismatches"]) for r in rows),
                gate_ok=sum(r["gate_ok"] is True for r in rows),
                gate_unchecked=sum(r["gate_ok"] is None for r in rows),
                lambda_distribution=dict(sorted(collections.Counter(
                    r["lambda"] for r in rows if r["lambda"] is not None).items())),
                lambda_none=sum(r["lambda"] is None for r in rows),
                bounded_all=sum(r["bounded_all"] is True for r in rows),
                bounded_all_false=sum(r["bounded_all"] is False for r in rows),
                bounded_all_uncomputed=sum(r["bounded_all"] is None for r in rows),
                zero_mean=sum(r["zero_mean"] is True for r in rows),
                zero_mean_without_bounded_all=sum(r["zero_mean"] is True and
                                                r["bounded_all"] is False for r in rows),
                zero_mean_with_uncomputed_bounded_all=sum(r["zero_mean"] is True and
                                                        r["bounded_all"] is None for r in rows),
                timeout=sum(r["status"] == "timeout" for r in rows),
                errors=sum(r["status"] == "error" for r in rows))


def make_summary(rows, wall_seconds, workers):
    summary = counts(rows)
    summary.update(by_record_class={c: counts([r for r in rows if r["record_class"] == c])
                                   for c in ("bounded", "rising", "flat", "capped")},
                   ambiguous_record_class=counts([r for r in rows if r["record_class"] is None]),
                   ambiguous_record_class_indices=[r["idx"] for r in rows if r["record_class"] is None],
                   mismatches=[m for r in rows for m in r["mismatches"]],
                   wall_seconds=round(wall_seconds, 6), workers=workers,
                   family_timeout_seconds=FAMILY_SECONDS, node_cap=NODE_CAP,
                   input_sha256={str(p.relative_to(BD_PATH.parents[3])): hashlib.sha256(p.read_bytes()).hexdigest()
                                 for p in (BD_PATH, RECORD_PATH)})
    return summary


def atomic_json(path, obj):
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n")
    tmp.replace(path)


def run(workers, selected=None):
    if not 1 <= workers <= 7:
        raise ValueError("At most seven family workers plus this parent process")
    t0 = time.monotonic()
    records_list = [json.loads(s) for s in RECORD_PATH.read_text().splitlines() if s.strip()]
    records = {r["idx"]: r for r in records_list}
    families = BD.families_one_def()
    assert len(records_list) == len(records) == len(families) == 664
    assert set(records) == {idx for idx, _ in families}
    if selected:
        families = [(idx, d) for idx, d in families if idx in selected]
    tasks = collections.deque((idx, defs, records[idx]) for idx, defs in families)
    context = mp.get_context("fork")
    children, active, rows = {}, {}, []
    progress_path = HERE / "progress.json"
    journal_path = HERE / ("rates.jsonl" if selected is None else "smoke_rates.jsonl")
    for _ in range(min(workers, len(tasks))):
        parent, child = context.Pipe()
        proc = context.Process(target=worker_loop, args=(child,))
        proc.start()
        child.close()
        children[parent] = proc
        task = tasks.popleft()
        parent.send(task)
        active[parent] = dict(idx=task[0], stage="starting", nodes=0)
    try:
        with journal_path.open("w") as journal:
            while active:
                ready = wait(list(active), timeout=10)
                for conn in ready:
                    kind, payload = conn.recv()
                    if kind in ("started", "progress"):
                        active[conn].update(payload)
                    elif kind == "result":
                        rows.append(payload)
                        journal.write(json.dumps(payload, sort_keys=True) + "\n")
                        journal.flush()
                        print(json.dumps(dict(done=len(rows), total=len(families),
                                              idx=payload["idx"], nodes=payload["nodes"],
                                              complete=payload["complete"], status=payload["status"],
                                              seconds=payload["seconds"], wall_seconds=round(time.monotonic()-t0,1))),
                              flush=True)
                        if tasks:
                            task = tasks.popleft()
                            conn.send(task)
                            active[conn] = dict(idx=task[0], stage="starting", nodes=0)
                        else:
                            conn.send(None)
                            del active[conn]
                atomic_json(progress_path, dict(done=len(rows), total=len(families),
                                               queued=len(tasks), wall_seconds=time.monotonic()-t0,
                                               active=list(active.values())))
        rows.sort(key=lambda r: r["idx"])
        journal_path.write_text("".join(json.dumps(r, sort_keys=True) + "\n" for r in rows))
        summary_path = HERE / ("summary.json" if selected is None else "smoke_summary.json")
        atomic_json(summary_path, make_summary(rows, time.monotonic()-t0, workers))
    finally:
        for conn, proc in children.items():
            if conn in active:
                try:
                    conn.send(None)
                except (BrokenPipeError, EOFError):
                    pass
            proc.join()
            conn.close()
    return rows


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, default=7)
    parser.add_argument("--only", type=int, nargs="+")
    args = parser.parse_args()
    run(args.workers, set(args.only) if args.only else None)
