"""Run paired method blocks on new labels, one isolated process for each method stream."""
import gzip
import hashlib
import json
import os
from pathlib import Path
import sys
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
TICKET = HERE.parent.name
NOTES = ROOT / "research" / TICKET
DEFAULT = ROOT / "artifacts" / TICKET / HERE.name
FIRST = "FOLD-PLACEMENT-20261115-001"
PREV = ROOT / "experiments" / FIRST / (FIRST + "-E001_fixed_inputs")
FIRST_OUT = ROOT / "artifacts" / FIRST / PREV.name
METHODS = ("reference-primitive", "triple-primitive", "triple-named", "triple-flat",
           "atomic-primitive", "guided-primitive", "guided-named", "guided-flat")
BLOCK = (0, 1, 7, 2, 6, 3, 5, 4)


def encoded(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def read(path):
    return json.loads(path.read_bytes())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_new(path, value):
    with path.open("xb") as out:
        out.write(encoded(value) + b"\n")


def setup(params):
    global OUT, PUBLIC
    OUT = Path(params.get("data_dir", DEFAULT)).resolve()
    design = read(OUT / "design.json")
    for name, expected in design["sources"].items():
        if sha(ROOT / name) != expected:
            raise ValueError("bound source changed: " + name)
    for name in ("panel.json", "given.json"):
        if sha(OUT / name) != design["data"][name]:
            raise ValueError("bound public input changed: " + name)
    PUBLIC = read(OUT / "panel.json")
    if any(set(row) != {"id", "n", "truth"} for row in PUBLIC):
        raise ValueError("private field in unhinted input")
    old = "FOLD-DEPTH-20261115-001"
    sys.path[:0] = [str(HERE), str(PREV), str(ROOT / "experiments" / old / (old + "-E001_supplied_fold"))]


def cases():
    for repeat in range(8):
        for cache in (("warm", "cold") if repeat % 2 == 0 else ("cold", "warm")):
            if cache == "cold" and repeat > 1:
                continue
            for i in BLOCK:
                method = METHODS[(i + repeat + 4 * int(cache == "cold")) % len(METHODS)]
                yield f"{cache}-{repeat}-{method}", dict(method=method, cache=cache, repeat=repeat)


def factory(method):
    strategy, arm = method.split("-")
    if strategy == "reference":
        from peel import PeelSolver
        return lambda: PeelSolver(9, "primitive", trace_limit=0)
    entry = None if method in ("triple-primitive", "atomic-primitive") else read(OUT / "given.json")
    dag = entry["dag"] if arm == "named" else None
    if strategy == "triple":
        from placement import PlacementSolver
        return lambda: PlacementSolver(9, arm=arm, entry=entry, fold_dag=dag, strategy="placement", trace_limit=0)
    from pair_solver import PairSolver
    return lambda: PairSolver(9, arm=arm, entry=entry, fold_dag=dag, strategy=strategy, trace_limit=0)


def run(case_id, payload):
    cpu_id = None
    if hasattr(os, "sched_setaffinity"):
        cpu_id = max(os.sched_getaffinity(0))
        os.sched_setaffinity(0, {cpu_id})
    start, cpu = time.perf_counter_ns(), time.process_time_ns()
    create = factory(payload["method"])
    startup_cpu = time.process_time_ns() - cpu
    startup = time.perf_counter_ns() - start
    rows = []
    engine = None
    for task in PUBLIC:
        start, cpu = time.perf_counter_ns(), time.process_time_ns()
        if engine is None or payload["cache"] == "cold":
            engine = create()
        init = time.perf_counter_ns() - start
        try:
            result = engine.solve(task["truth"])
            size = len(encoded(result["circuit"]))
        except (ValueError, RuntimeError, AssertionError) as err:
            result = {"status": "error", "error": repr(err), "circuit": None, "work": {}}
            size = 0
        used_cpu = time.process_time_ns() - cpu
        used_wall = time.perf_counter_ns() - start
        rows.append(dict(id=task["id"], result=result, cpu_ns=used_cpu, wall_ns=used_wall,
                         init_ns=init, return_bytes=size))
    file = OUT / (case_id + ".jsonl.gz")
    with gzip.open(file, "wb", compresslevel=1) as out:
        for row in rows:
            out.write(encoded(row) + b"\n")
    return dict(**payload, file=file.name, sha256=sha(file), tasks=len(rows),
                startup_ns=startup, startup_cpu_ns=startup_cpu, affinity=cpu_id)
