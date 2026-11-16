"""Measure full exact-return streams for blind and informed synthesis at nine inputs."""
import gzip
import hashlib
import json
from pathlib import Path
import sys
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
ID = HERE.parent.name
NOTES = ROOT / "research" / ID
DEFAULT = ROOT / "artifacts" / ID / HERE.name
OLD_DEPTH = "FOLD-DEPTH-20261115-001"
OLD_LIBRARY = "FOLD-DISCOVERY-20261115-001"
PEEL = ROOT / "experiments" / OLD_DEPTH / (OLD_DEPTH + "-E001_supplied_fold")
LIBRARY = ROOT / "experiments" / OLD_LIBRARY / (OLD_LIBRARY + "-E001_learned_library")
CANDIDATES = ROOT / "artifacts" / OLD_LIBRARY / LIBRARY.name / "candidates.json"
METHODS = ["reference-primitive-blind"] + [
    f"{strategy}-{arm}-{hint}" for strategy in ("direct", "placement")
    for arm in ("primitive", "named", "flat") for hint in ("blind", "hint")
]


def dump(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def read(path):
    return json.loads(path.read_bytes())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_new(path, value):
    with path.open("xb") as out:
        out.write(dump(value) + b"\n")


def setup(params):
    global OUT, PUBLIC
    OUT = Path(params.get("data_dir", DEFAULT)).resolve()
    frozen = read(OUT / "design.json")
    for name, expected in frozen["sources"].items():
        if sha(ROOT / name) != expected:
            raise ValueError(f"bound source changed: {name}")
    for name in ("panel.json", "given.json"):
        if sha(OUT / name) != frozen["data"][name]:
            raise ValueError(f"bound input changed: {name}")
    PUBLIC = read(OUT / "panel.json")
    if any(set(row) != {"id", "n", "truth", "hint"} for row in PUBLIC):
        raise ValueError("private fixture fields in public input")
    sys.path[:0] = [str(HERE), str(LIBRARY), str(PEEL)]


def cases():
    for rep in range(5):
        caches = ("warm", "cold") if rep % 2 == 0 else ("cold", "warm")
        for cache in caches:
            if cache == "cold" and rep >= 3:
                continue
            seq = METHODS if rep % 2 == 0 else METHODS[::-1]
            offset = (3 * rep + 5 * int(cache == "cold")) % len(seq)
            for method in seq[offset:] + seq[:offset]:
                yield f"{cache}-{rep}-{method}", dict(cache=cache, repeat=rep, method=method)


def factory(strategy, arm):
    if strategy == "reference":
        from peel import PeelSolver
        return lambda: PeelSolver(9, "primitive", trace_limit=0)
    from placement import PlacementSolver
    entry = read(OUT / "given.json") if arm != "primitive" else None
    dag = entry["dag"] if arm == "named" else None
    return lambda: PlacementSolver(9, arm=arm, entry=entry, fold_dag=dag,
                                   strategy=strategy, trace_limit=0)


def run(case_id, payload):
    strategy, arm, hint_mode = payload["method"].split("-")
    started = time.perf_counter_ns()
    cpu_start = time.process_time_ns()
    build_engine = factory(strategy, arm)
    startup_cpu = time.process_time_ns() - cpu_start
    startup = time.perf_counter_ns() - started
    engine = None
    records = []
    for task in PUBLIC:
        start = time.perf_counter_ns()
        cpu = time.process_time_ns()
        if engine is None or payload["cache"] == "cold":
            engine = build_engine()
        init = time.perf_counter_ns() - start
        before = engine.work_counters()
        try:
            if hint_mode == "hint":
                result = engine.solve(task["truth"], hint=tuple(task["hint"]))
            else:
                result = engine.solve(task["truth"])
            size = len(dump(result["circuit"]))
        except (ValueError, RuntimeError, AssertionError) as error:
            now = engine.work_counters()
            result = {"status": "error", "error": repr(error), "circuit": None,
                      "work": {k: v - before.get(k, 0) for k, v in now.items()}}
            size = 0
        cpu_ns = time.process_time_ns() - cpu
        wall_ns = time.perf_counter_ns() - start
        records.append(dict(id=task["id"], result=result, init_ns=init, cpu_ns=cpu_ns,
                            wall_ns=wall_ns, return_bytes=size))
    dest = OUT / (case_id + ".jsonl.gz")
    with gzip.open(dest, "wb", compresslevel=1) as out:
        for item in records:
            out.write(dump(item) + b"\n")
    return dict(**payload, tasks=len(records), file=dest.name, sha256=sha(dest),
                startup_ns=startup, startup_cpu_ns=startup_cpu)
