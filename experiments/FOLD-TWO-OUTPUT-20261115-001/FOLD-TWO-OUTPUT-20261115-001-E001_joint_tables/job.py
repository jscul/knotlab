"""Isolated paid streams for joint synthesis with an explicit internal interface."""
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
PREVIOUS = "FOLD-PAIR-PLACE-20261115-001"
ENTRY = ROOT / "artifacts" / PREVIOUS / (PREVIOUS + "-E001_pair_first") / "given.json"
HISTORY = "FOLD-DISCOVERY-20261115-001"
ACQUISITION = ROOT / "artifacts" / HISTORY / (HISTORY + "-E001_learned_library") / "gate-freeze.json"
METHODS = ("reference", "dag-first", "primitive", "named", "flat")
BLOCK = (0, 1, 4, 2, 3)


def encoded(data):
    return json.dumps(data, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def load(path):
    return json.loads(path.read_bytes())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_new(path, value):
    with path.open("xb") as f:
        f.write(encoded(value) + b"\n")


def setup(params):
    global OUT, PANELS, CPU
    OUT = Path(params.get("data_dir", DEFAULT)).resolve()
    design = load(OUT / "design.json")
    for name, wanted in design["sources"].items():
        if sha(ROOT / name) != wanted:
            raise ValueError("bound source changed: " + name)
    for name in ("primary.json", "sensitivity.json", "given.json"):
        if sha(OUT / name) != design["data"][name]:
            raise ValueError("bound public input changed: " + name)
    CPU = design["cpu"]
    PANELS = {name: load(OUT / (name + ".json")) for name in ("primary", "sensitivity")}
    if any(set(r) != {"id", "n", "outputs"} or len(r["outputs"]) != 2
           for panel in PANELS.values() for r in panel):
        raise ValueError("unexpected public solver input")
    sys.path.insert(0, str(HERE))


def cases():
    for rep in range(10):
        configs = [("primary", "warm")]
        if rep < 5:
            configs.append(("primary", "cold"))
        if rep % 2:
            configs.reverse()
        for panel, cache in configs:
            for slot in (BLOCK if rep < len(METHODS) else BLOCK[::-1]):
                arm = METHODS[(slot + rep + 2 * int(cache == "cold")) % len(METHODS)]
                yield f"{panel}-{cache}-{rep}-{arm}", dict(panel=panel, cache=cache, repeat=rep, arm=arm)
    for rep in range(2):
        for slot in BLOCK:
            arm = METHODS[(slot + rep + 1) % len(METHODS)]
            yield f"sensitivity-warm-{rep}-{arm}", dict(panel="sensitivity", cache="warm", repeat=rep, arm=arm)


def factory(arm):
    if arm in ("reference", "dag-first"):
        from primitive_reference import PrimitiveReference
        if arm == "dag-first":
            return lambda n: PrimitiveReference(n, strategy="dag-first")
        return PrimitiveReference
    from joint_solver import JointSolver
    entry = load(OUT / "given.json") if arm != "primitive" else None
    dag = entry["dag"] if arm == "named" else None
    return lambda n: JointSolver(n, arm=arm, entry=entry, fold_dag=dag)


def public_return(r):
    c = r["circuit"]
    return dict(n=r["n"], triple=r["triple"], width=r["width"], class_count=r["class_count"],
                summary_wires=r["summary_wires"], circuit=dict(gates=c["gates"], outputs=c["outputs"]))


def run(case_id, case):
    if CPU is not None:
        os.sched_setaffinity(0, {CPU})
    t_start, cpu_start = time.perf_counter_ns(), time.process_time_ns()
    from checker import JointChecker
    make = factory(case["arm"])
    load_cpu = time.process_time_ns() - cpu_start
    load_wall = time.perf_counter_ns() - t_start
    records = []
    engines = {}
    for task in PANELS[case["panel"]]:
        start, cpu = time.perf_counter_ns(), time.process_time_ns()
        n, targets = task["n"], tuple(task["outputs"])
        init_cpu = solve_cpu = verify_cpu = verify_wall = out_bytes = 0
        result, certificate, failure = None, None, None
        try:
            if case["cache"] == "cold" or n not in engines:
                engines[n] = make(n), JointChecker(n)
            engine, checker = engines[n]
            init_cpu = time.process_time_ns() - cpu
            sol_start = time.process_time_ns()
            result = engine.solve(targets)
            solve_cpu = time.process_time_ns() - sol_start
            vc, vw = time.process_time_ns(), time.perf_counter_ns()
            certificate = checker.verify(targets, result)
            verify_cpu = time.process_time_ns() - vc
            verify_wall = time.perf_counter_ns() - vw
            out_bytes = len(encoded(public_return(result)))
        except (ValueError, LookupError, RuntimeError, AssertionError, TypeError) as error:
            failure = f"{type(error).__name__}: {error}"
        charged_cpu, charged_wall = time.process_time_ns() - cpu, time.perf_counter_ns() - start
        records.append(dict(id=task["id"], result=result, certificate=certificate, failure=failure,
                            cpu_ns=charged_cpu, wall_ns=charged_wall, init_cpu_ns=init_cpu,
                            synth_cpu_ns=solve_cpu, verify_cpu_ns=verify_cpu, verify_wall_ns=verify_wall,
                            return_bytes=out_bytes))
    dest = OUT / (case_id + ".jsonl.gz")
    with gzip.open(dest, "wb", compresslevel=1) as f:
        for r in records:
            f.write(encoded(r) + b"\n")
    return dict(**case, file=dest.name, sha256=sha(dest), tasks=len(records), cpu=CPU,
                startup_cpu_ns=load_cpu, startup_wall_ns=load_wall)
