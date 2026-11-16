"""Time one empty-to-warm deployment in an isolated worker."""
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
PREVIOUS = "FOLD-TWO-OUTPUT-20261115-001"
OLD = ROOT / "experiments" / PREVIOUS / (PREVIOUS + "-E001_joint_tables")
METHODS = ("lex", "fixed", "reference", "learned", "cofactor", "prior-generic", "transitions")
POSITIONS = (0, 1, 6, 2, 5, 3, 4)
REPEATS = 10


def encoded(x):
    return json.dumps(x, separators=(",", ":"), sort_keys=True, allow_nan=False).encode()


def read(path):
    return json.loads(path.read_bytes())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_new(path, obj, durable=False):
    with path.open("xb") as f:
        f.write(encoded(obj) + b"\n")
        if durable:
            f.flush()
            os.fsync(f.fileno())


def check_hashes(base, inventory):
    for name, digest in inventory.items():
        if sha(base / name) != digest:
            raise ValueError(f"changed frozen input: {name}")


def setup(params):
    global OUT, TASKS, CPU
    OUT = Path(params.get("data_dir", DEFAULT)).resolve()
    design = read(OUT / "design.json")
    check_hashes(ROOT, design["sources"])
    seal = read(OUT / "held-bound.json")
    # A worker never opens the training or held grade files.
    check_hashes(OUT, {p: seal[p] for p in ("held.json", "model.json", "design.json")})
    TASKS = read(OUT / "held.json")
    if len(TASKS) != 192 or any(set(r) != {"n", "outputs", "id"} for r in TASKS):
        raise ValueError("unexpected public deployment inputs")
    CPU = design["cpu"]
    sys.path[:0] = [str(HERE), str(OLD)]


def cases():
    # Every forward block is counterbalanced by its reversed order of methods.
    # Every method gets the identical, preselected ordering of the tasks.
    for repeat in range(REPEATS):
        order = POSITIONS if repeat < 5 else POSITIONS[::-1]
        for slot in order:
            arm = METHODS[(slot + repeat % 5) % len(METHODS)]
            yield f"warm-{repeat}-{arm}", {"repeat": repeat, "arm": arm}


def factory(arm):
    if arm == "reference":
        from primitive_reference import PrimitiveReference
        return PrimitiveReference
    if arm == "prior-generic":
        from joint_solver import JointSolver
        return JointSolver
    from solver import OrderedSolver
    if arm == "lex":
        return OrderedSolver
    if arm == "cofactor":
        from solver import FixedRanker
        return lambda n: OrderedSolver(n, ranker=FixedRanker(n))
    from policy import Ranker, fixed_model
    model = read(OUT / "model.json") if arm == "learned" else fixed_model()
    if arm == "transitions":
        model["channel"] = "transitions"
    return lambda n: OrderedSolver(n, ranker=Ranker(n, model))


def public_return(result):
    circuit = result["circuit"]
    return {**{k: result[k] for k in ("n", "triple", "class_count", "width", "summary_wires")},
            "circuit": {"gates": circuit["gates"], "outputs": circuit["outputs"]}}


def run(case_id, case):
    if CPU is not None:
        os.sched_setaffinity(0, {CPU})
    start, cpu = time.perf_counter_ns(), time.process_time_ns()
    from checker import JointChecker
    make = factory(case["arm"])
    startup_cpu = time.process_time_ns() - cpu
    startup_wall = time.perf_counter_ns() - start
    records, engines = [], {}
    for task in TASKS:
        start, cpu = time.perf_counter_ns(), time.process_time_ns()
        n, targets = task["n"], tuple(task["outputs"])
        init_cpu = solve_cpu = verify_cpu = verify_wall = return_bytes = 0
        result = certificate = failure = None
        try:
            if n not in engines:
                engines[n] = make(n), JointChecker(n)
            engine, checker = engines[n]
            init_cpu = time.process_time_ns() - cpu
            s = time.process_time_ns()
            try:
                result = engine.solve(targets)
            finally:
                solve_cpu = time.process_time_ns() - s
            v, w = time.process_time_ns(), time.perf_counter_ns()
            try:
                certificate = checker.verify(targets, result)
            finally:
                verify_cpu = time.process_time_ns() - v
                verify_wall = time.perf_counter_ns() - w
            return_bytes = len(encoded(public_return(result)))
        except (ValueError, LookupError, RuntimeError, AssertionError, TypeError, ArithmeticError) as exc:
            failure = f"{type(exc).__name__}: {exc}"
        charged_cpu, charged_wall = time.process_time_ns() - cpu, time.perf_counter_ns() - start
        records.append(dict(id=task["id"], result=result, certificate=certificate, failure=failure,
                            cpu_ns=charged_cpu, wall_ns=charged_wall, init_cpu_ns=init_cpu,
                            synth_cpu_ns=solve_cpu, verify_cpu_ns=verify_cpu, verify_wall_ns=verify_wall,
                            return_bytes=return_bytes))
    path = OUT / (case_id + ".jsonl.gz")
    with gzip.open(path, "xb", compresslevel=1) as f:
        for row in records:
            f.write(encoded(row) + b"\n")
    return dict(**case, file=path.name, sha256=sha(path), cpu=CPU, tasks=len(records),
                startup_cpu_ns=startup_cpu, startup_wall_ns=startup_wall)
