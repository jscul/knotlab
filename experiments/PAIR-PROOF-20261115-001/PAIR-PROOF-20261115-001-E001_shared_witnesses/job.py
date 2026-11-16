"""Charge each independent deployment from importing the solver to serialized verified returns."""
import gzip
import hashlib
import json
import os
from pathlib import Path
import sys
from time import perf_counter_ns, process_time_ns


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
TICKET = HERE.parent.name
OUT = ROOT / "artifacts" / TICKET / HERE.name
PREDECESSOR = "PARENT-FOLD-20261115-001"
PREV_NAME = PREDECESSOR + "-E001_consumer_edits"
PREV = ROOT / "experiments" / PREDECESSOR / PREV_NAME
DATA = ROOT / "artifacts" / PREDECESSOR / PREV_NAME / "explicit-piece"
JOINT = ROOT / "experiments/FOLD-TWO-OUTPUT-20261115-001/FOLD-TWO-OUTPUT-20261115-001-E001_joint_tables"
FIELDS = ("n", "upstream_count", "gates", "frontier", "outputs", "pieces")


def encoded(obj):
    return json.dumps(obj, separators=(",", ":"), sort_keys=True, allow_nan=False).encode()


def load(file):
    return json.loads(file.read_bytes())


def sha(file):
    return hashlib.sha256(file.read_bytes()).hexdigest()


def setup(params):
    global DEST, ARMS, PANELS, START, COUNT, CPU, CASES_FILE, BROKEN, SOURCE
    DEST = Path(params.get("data_dir", OUT)).resolve()
    design = load(DEST / "design.json")
    for filename, expected in design["sources"].items():
        if sha(ROOT / filename) != expected:
            raise ValueError("changed frozen source: " + filename)
    for filename, expected in design["data"].items():
        if sha(ROOT / filename) != expected:
            raise ValueError("changed bound input: " + filename)
    CPU = design["cpu"]
    SOURCE = design
    ARMS = tuple(params["arms"].split(",")) if "arms" in params else tuple(design["arms"])
    if not set(ARMS) <= set(design["arms"]):
        raise ValueError("unknown arm")
    PANELS = tuple(params.get("panels", "broken,mixed").split(","))
    START, COUNT = int(params.get("begin", 0)), int(params.get("count", 8))
    CASES_FILE = DATA / "public.json"
    BROKEN = load(DEST / "stream.json")
    sys.path[:0] = [str(HERE), str(PREV), str(JOINT)]


def cases():
    n = len(ARMS)
    interleave = [0]
    for j in range(1, n):
        interleave.append((j + 1)//2 if j % 2 else n-j//2)
    for block in range(START, START + COUNT):
        panels = PANELS if block % 2 == 0 else tuple(reversed(PANELS))
        for panel in panels:
            offset = ((n//2 + 1)*block + (3 if panel == "mixed" else 0)) % n
            order = interleave if block % 4 < 2 else reversed(interleave)
            for idx in order:
                arm = ARMS[(offset + idx) % n]
                yield f"{panel}-{block}-{arm}", dict(panel=panel, block=block, arm=arm)


def _call(phases, label, fn, *args):
    start = process_time_ns()
    try:
        return fn(*args)
    finally:
        phases[label] = process_time_ns() - start


def run(key, params):
    os.sched_setaffinity(0, {CPU})
    arm, panel, block = (params[k] for k in ("arm","panel","block"))
    arm_spec = SOURCE["arms"][arm]
    # Offline diagnostic advice is supplied free, then each chosen observation is read and checked.
    advice = None
    if "advice" in arm_spec:
        advice = load(DEST / "plans.json")[arm_spec["advice"]]
    start, wall = process_time_ns(), perf_counter_ns()
    from parent_engine import Parent
    from wire_return import attach_physical
    if arm_spec["mode"] == "ordinary":
        from controls import ordinary_exact
        from parent_checker import Checker
    elif arm_spec["mode"] == "compact":
        from compact_control import compact as ordinary_exact
        from pair_checker import PairChecker as Checker
    else:
        from pair_solver import prepare_history, solve
        from pair_checker import PairChecker as Checker
    inputs = load(CASES_FILE)
    if block % 2:
        inputs.reverse()
    startup = process_time_ns() - start
    trace, geometry = [], {}
    for case in inputs:
        parent_start = process_time_ns()
        phases = {}
        row = dict(id=case["id"], phases=phases, acquisition={}, original_check={}, edits=[], failure=None)
        try:
            original = {k:case[k] for k in FIELDS}
            parent = _call(phases, "solver_history", Parent, original)
            def build_checker():
                if arm_spec["mode"] == "ordinary":
                    return Checker(case)
                return Checker(case, geometry_cache=geometry)
            checker = _call(phases, "checker_history", build_checker)
            history = None
            if arm_spec.get("history"):
                history, row["acquisition"] = _call(phases, "acquire", prepare_history, parent)
                row["original_check"] = _call(phases, "original_proof_verify", checker.verify_history, history)
            edits = case["edits"] if block % 2 == 0 else reversed(case["edits"])
            for edit in edits:
                eid = edit["id"]
                if panel == "broken" and eid != BROKEN[case["id"]]:
                    continue
                before = process_time_ns()
                timing = {}
                child = dict(id=eid, phases=timing, failure=None, work={}, check={}, answer=None)
                try:
                    single = {k:edit[k] for k in ("gate","pin","to")}
                    state = _call(timing, "update", parent.edit, single)
                    if arm_spec["mode"] in ("ordinary", "compact"):
                        stage, child["work"] = _call(timing, "solve", ordinary_exact, state)
                    else:
                        requests = advice[case["id"]][eid] if advice is not None else None
                        stage, child["work"] = _call(timing, "solve", solve, state, arm_spec["mode"], history, requests)
                    answer = _call(timing, "link", attach_physical, original, stage)
                    if "pair_proofs" in stage:
                        answer["pair_proofs"] = stage["pair_proofs"]
                    child["check"] = _call(timing, "verify", checker.verify, edit, answer)
                    payload = _call(timing, "serialize", encoded, answer)
                    child["bytes"] = len(payload)
                    child["answer"] = answer
                except Exception as exc:
                    child["failure"] = f"{type(exc).__name__}: {exc}"
                child["cpu_ns"] = process_time_ns() - before
                row["edits"].append(child)
        except Exception as exc:
            row["failure"] = f"{type(exc).__name__}: {exc}"
        row["cpu_ns"] = process_time_ns() - parent_start
        trace.append(row)
    duration, elapsed = process_time_ns()-start, perf_counter_ns()-wall
    # Permanent research traces and checksums are written after the complete paid return.
    path = DEST / (key + ".jsonl.gz")
    with gzip.open(path, "xb", compresslevel=2) as file:
        for row in trace:
            file.write(encoded(row) + b"\n")
    failures = sum(bool(r["failure"]) + sum(bool(c["failure"]) for c in r["edits"]) for r in trace)
    return dict(**params, file=path.name, sha256=sha(path), cpu_ns=duration, wall_ns=elapsed,
                startup_ns=startup, parents=len(trace), edits=sum(len(r["edits"]) for r in trace), failures=failures)
