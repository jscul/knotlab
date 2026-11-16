"""Single-process paid deployments of fixed probes, exact controls and diagnostic advice."""
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
JOINT_ID = "FOLD-TWO-OUTPUT-20261115-001"
RANK_ID = "TRIPLE-ORDER-20261115-001"
JOINT = ROOT / "experiments" / JOINT_ID / (JOINT_ID + "-E001_joint_tables")
RANK = ROOT / "experiments" / RANK_ID / (RANK_ID + "-E001_rank_triples")
HELD = ("zero-one", "primitive", "four-cofactor", "matched-exact", "full-recheck",
        "reference", "lexical", "primitive-new-check")
CALIBRATION = ("zero-one", "alternating", "blocks-two", "blocks-three",
               "oracle-menu", "skip-0", "skip-1", "skip-2", "skip-3", "matched-exact", "primitive")
CONSTANT = CALIBRATION[:4]
PRIMITIVES = ("primitive", "four-cofactor", "matched-exact", "reference", "lexical", "primitive-new-check")
SCHEDULE = (0, 1, 7, 2, 6, 3, 5, 4)
REPEATS = 8


def encoded(x):
    return json.dumps(x, separators=(",", ":"), sort_keys=True, allow_nan=False).encode()


def read(p):
    return json.loads(p.read_bytes())


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def write_new(path, data):
    with path.open("xb") as f:
        f.write(encoded(data) + b"\n")


def check_hashes(root, files):
    for name, digest in files.items():
        if sha(root / name) != digest:
            raise ValueError("changed bound file: " + name)


def setup(params):
    global OUT, CPU, PANELS, DATA
    OUT = Path(params.get("data_dir", DEFAULT)).resolve()
    design = read(OUT / "design.json")
    check_hashes(ROOT, design["sources"])
    DATA = read(OUT / "data-bound.json")
    check_hashes(OUT, {k:DATA[k] for k in ("design.json", "held.json", "calibration.json")})
    CPU = design["cpu"]
    PANELS = {k:read(OUT / (k + ".json")) for k in ("held", "calibration")}
    if any(set(t) != {"id","n","outputs"} for ts in PANELS.values() for t in ts):
        raise ValueError("unexpected public input")
    sys.path[:0] = [str(HERE), str(JOINT), str(RANK)]


def cases():
    for repeat in range(REPEATS):
        panels = [("calibration", CALIBRATION), ("held", HELD)]
        if repeat % 2:
            panels.reverse()
        for panel, methods in panels:
            if panel == "held":
                order = [(s + repeat + 3) % len(methods) for s in SCHEDULE]
            else:
                pattern = (0, 1, 10, 2, 9, 3, 8, 4, 7, 5, 6)
                order = [(s + repeat % 4) % len(methods) for s in pattern]
                if repeat >= 4:
                    order.reverse()
            for slot in order:
                arm = methods[slot]
                yield f"{panel}-{repeat}-{arm}", dict(panel=panel, repeat=repeat, arm=arm)


def factory(arm):
    if arm in ("primitive", "reference", "four-cofactor", "lexical", "full-recheck"):
        from checker import JointChecker as Verify
    else:
        from verifier import PaidVerifier as Verify
    if arm in ("primitive", "primitive-new-check"):
        from joint_solver import JointSolver as Engine
    elif arm == "reference":
        from primitive_reference import PrimitiveReference as Engine
    elif arm in ("lexical", "four-cofactor"):
        from solver import OrderedSolver, FixedRanker
        Engine = OrderedSolver if arm == "lexical" else lambda n: OrderedSolver(n, ranker=FixedRanker(n))
    else:
        from probes import ProbeSolver
        scheme = CONSTANT.index(arm) if arm in CONSTANT else 0
        Engine = lambda n: ProbeSolver(n, enabled=arm != "matched-exact", scheme=scheme)
    return Engine, Verify


def public_return(r):
    c = r["circuit"]
    return {**{k:r[k] for k in ("n","triple","class_count","width","summary_wires")},
            "circuit":{"gates":c["gates"],"outputs":c["outputs"]}, "witnesses":r.get("witnesses",[])}


def run(case_id, case):
    if CPU is not None:
        os.sched_setaffinity(0, {CPU})
    arm, panel = case["arm"], case["panel"]
    advisory = arm == "oracle-menu" or arm.startswith("skip-")
    hints = None
    if advisory:
        if panel != "calibration":
            raise ValueError("advice is confined to calibration")
        # The diagnostic grants a ready lookup table for free, then charges the
        # method for choosing, probing, and checking its certification attempts.
        filename = arm + ".json"
        check_hashes(OUT, {filename:DATA[filename]})
        hints = [{int(k):v for k,v in entry.items()} for entry in read(OUT/filename)]
    cpu, wall = time.process_time_ns(), time.perf_counter_ns()
    make, check = factory(arm)
    startup_cpu, startup_wall = time.process_time_ns() - cpu, time.perf_counter_ns() - wall
    records, engines = [], {}
    for index, task in enumerate(PANELS[panel]):
        cpu, wall = time.process_time_ns(), time.perf_counter_ns()
        n, targets = task["n"], tuple(task["outputs"])
        init_cpu = solve_cpu = verify_cpu = verify_wall = serialization_cpu = return_bytes = 0
        result = certificate = error = None
        try:
            if n not in engines:
                engines[n] = make(n), check(n)
            engine, verify = engines[n]
            init_cpu = time.process_time_ns() - cpu
            sc = time.process_time_ns()
            try:
                result = engine.solve(targets, advice=hints[index]) if advisory else engine.solve(targets)
            finally:
                solve_cpu = time.process_time_ns() - sc
            vc, vw = time.process_time_ns(), time.perf_counter_ns()
            try:
                certificate = verify.verify(targets, result)
            finally:
                verify_cpu = time.process_time_ns() - vc
                verify_wall = time.perf_counter_ns() - vw
            oc = time.process_time_ns()
            try:
                return_bytes = len(encoded(public_return(result)))
            finally:
                serialization_cpu = time.process_time_ns() - oc
        except (ValueError, LookupError, RuntimeError, AssertionError, TypeError, ArithmeticError) as exc:
            error = f"{type(exc).__name__}: {exc}"
        charged_cpu, charged_wall = time.process_time_ns() - cpu, time.perf_counter_ns() - wall
        records.append(dict(id=task["id"], result=result, certificate=certificate, failure=error,
                            cpu_ns=charged_cpu, wall_ns=charged_wall, init_cpu_ns=init_cpu, synth_cpu_ns=solve_cpu,
                            verify_cpu_ns=verify_cpu, verify_wall_ns=verify_wall, serialization_cpu_ns=serialization_cpu,
                            return_bytes=return_bytes))
    fp = OUT / (case_id + ".jsonl.gz")
    with gzip.open(fp, "xb", compresslevel=1) as f:
        for row in records:
            f.write(encoded(row) + b"\n")
    return dict(**case, file=fp.name, sha256=sha(fp), cpu=CPU, tasks=len(records),
                startup_cpu_ns=startup_cpu, startup_wall_ns=startup_wall)
