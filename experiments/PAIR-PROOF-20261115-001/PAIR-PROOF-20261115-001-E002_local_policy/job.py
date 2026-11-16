"""Fresh-process held deployment, from cold imports to serialized exact returns.

Only the harness reads IDs, the edit list and offline broken-panel membership.
Parent and policy receive FIELDS and a separate gate/pin/to edit.  Private
grades are never opened.  setup binds bytes without importing a solver or
parsing the model/public panel; run reads the complete public file and, for
the learned arm, loads its model inside the paid CPU/wall interval.

longrun launch must use --workers 1 --max-cases-per-worker 1.  Each case is one
complete panel/block/arm deployment, with persistent public geometry within
that stream and independent semantic/observation caches for sibling edits.
The permanent gzip research receipt is written after the paid answer return;
actual answer serialization, receipt construction and all method work are
inside the interval, matching E001's accounting boundary.

Required design.json: cpu, sources:{path:sha256}, data:{path:sha256},
arms:{name:{mode}}, model:path.  Paths are repository-relative or absolute.
Optional public/broken paths default to OUT/blind/public.json and
OUT/broken.json; model_key selects a wrapper field if the saved file wraps
the direct policy dictionary.  data must bind public, broken and model.
Params: data_dir, panels=mixed,broken, begin=0, count=8, arms (or methods).
"""

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
PREV = ROOT / "experiments/PARENT-FOLD-20261115-001/PARENT-FOLD-20261115-001-E001_consumer_edits"
PROOFS = HERE.parent / "PAIR-PROOF-20261115-001-E001_shared_witnesses"
JOINT = ROOT / "experiments/FOLD-TWO-OUTPUT-20261115-001/FOLD-TWO-OUTPUT-20261115-001-E001_joint_tables"
FIELDS = ("n", "upstream_count", "gates", "frontier", "outputs", "pieces")
EDIT_FIELDS = ("gate", "pin", "to")
MODES = ("ordinary", "compact", "no-proof", "balanced", "fixed", "same-menu", "learned")
SOURCE_DEPENDENCIES = tuple(str(path.relative_to(ROOT)) for path in (
    HERE / "local_policy.py",
    PROOFS / "pair_solver.py", PROOFS / "compact_control.py",
    PROOFS / "packed_faces.py", PROOFS / "pair_checker.py",
    PREV / "parent_engine.py", PREV / "controls.py", PREV / "wire_return.py",
    PREV / "parent_checker.py", JOINT / "joint_solver.py", JOINT / "checker.py",
))
_USED_PID = None


def encoded(obj):
    return json.dumps(obj, separators=(",", ":"), sort_keys=True, allow_nan=False).encode()


def load(path):
    return json.loads(Path(path).read_bytes())


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _path(value):
    return (ROOT / value).resolve()


def _names(value):
    names = tuple(part.strip() for part in value.split(","))
    if not names or any(not name for name in names) or len(set(names)) != len(names):
        raise ValueError("names must be a nonempty comma list without duplicates")
    return names


def setup(params):
    global DEST, SOURCE, CPU, ARMS, PANELS, START, COUNT
    global CASES_FILE, BROKEN_FILE, MODEL_FILE, MODEL_SHA256, BROKEN
    DEST = Path(params.get("data_dir", OUT)).resolve()
    design = load(DEST / "design.json")
    if type(design.get("cpu")) is not int or design["cpu"] < 0:
        raise ValueError("design.cpu must be a nonnegative integer")
    if not isinstance(design.get("arms"), dict) or not design["arms"]:
        raise ValueError("design.arms must name frozen methods")
    if any(not isinstance(spec, dict) or spec.get("mode") not in MODES
           for spec in design["arms"].values()):
        raise ValueError("unknown frozen method mode")
    sources, data = design.get("sources"), design.get("data")
    if not isinstance(sources, dict) or not isinstance(data, dict):
        raise ValueError("design must bind sources and public inputs")
    for filename, expected in sources.items():
        if sha(_path(filename)) != expected:
            raise ValueError("changed frozen source: " + filename)
    CASES_FILE = _path(design.get("public", DEST / "blind/public.json"))
    BROKEN_FILE = _path(design.get("broken", DEST / "broken.json"))
    MODEL_FILE = _path(design["model"])
    bound = {_path(filename): expected for filename, expected in data.items()}
    if any(path.name == "grades.json" for path in bound):
        raise ValueError("private grades must be bound by the external assessor, not this job")
    if any(path not in bound for path in (CASES_FILE, BROKEN_FILE, MODEL_FILE)):
        raise ValueError("design.data must bind public, broken membership and the frozen model")
    # Confirm an immutable model binding before even hash-opening the blind file.
    MODEL_SHA256 = bound[MODEL_FILE]
    if sha(MODEL_FILE) != MODEL_SHA256:
        raise ValueError("changed frozen model")
    for path, expected in bound.items():
        if path != MODEL_FILE and sha(path) != expected:
            raise ValueError("changed bound input: " + str(path))
    BROKEN = load(BROKEN_FILE)
    if not isinstance(BROKEN, dict):
        raise ValueError("broken membership must map parent IDs to edit IDs")
    selected = params.get("arms", params.get("methods"))
    ARMS = _names(selected) if selected is not None else tuple(design["arms"])
    if not set(ARMS) <= set(design["arms"]):
        raise ValueError("unknown selected arm")
    PANELS = _names(params.get("panels", "mixed,broken"))
    if not set(PANELS) <= {"mixed", "broken"}:
        raise ValueError("panels must be mixed and/or broken")
    START, COUNT = int(params.get("begin", 0)), int(params.get("count", 8))
    if START < 0 or COUNT < 1 or START + COUNT > 8:
        raise ValueError("blocks must be a nonempty subset of 0..7")
    SOURCE, CPU = design, design["cpu"]
    # No task-facing module is imported or fitted in the longrun parent.
    sys.path[:0] = [str(HERE), str(PROOFS), str(PREV), str(JOINT)]


def cases():
    n = len(ARMS)
    interleave = [0]
    for j in range(1, n):
        interleave.append((j + 1) // 2 if j % 2 else n - j // 2)
    for block in range(START, START + COUNT):
        panels = PANELS if block % 2 == 0 else tuple(reversed(PANELS))
        for panel in panels:
            offset = ((n // 2 + 1) * block + (3 if panel == "mixed" else 0)) % n
            order = interleave if block % 4 < 2 else reversed(interleave)
            for index in order:
                arm = ARMS[(offset + index) % n]
                yield f"{panel}-{block}-{arm}", dict(panel=panel, block=block, arm=arm)


def pin():
    """Normal entry uses the frozen single CPU; never silently move it."""
    os.sched_setaffinity(0, {CPU})
    if os.sched_getaffinity(0) != {CPU}:
        raise RuntimeError("worker was not pinned to its frozen CPU")


def _call(phases, label, function, *args, **kwargs):
    start = process_time_ns()
    try:
        return function(*args, **kwargs)
    finally:
        phases[label] = process_time_ns() - start


def _imports(mode):
    from parent_engine import Parent
    from wire_return import attach_physical
    ordinary = solve = None
    if mode == "ordinary":
        from controls import ordinary_exact as ordinary
        from parent_checker import Checker
    elif mode == "compact":
        from compact_control import compact as ordinary
        from pair_checker import PairChecker as Checker
    else:
        from pair_solver import solve
        from pair_checker import PairChecker as Checker
    return Parent, attach_physical, Checker, ordinary, solve


def _policy_import():
    import local_policy
    if Path(local_policy.__file__).resolve() != HERE / "local_policy.py":
        raise ImportError("local_policy refers to an unrelated module")
    return local_policy


def _public_cases(path):
    values = load(path)
    if not isinstance(values, list) or not values:
        raise ValueError("public.json must contain a nonempty case list")
    return values


def run(key, params):
    global _USED_PID
    pid = os.getpid()
    if _USED_PID == pid:
        raise RuntimeError("each deployment requires a fresh worker; use max-cases-per-worker 1")
    _USED_PID = pid
    arm, panel, block = (params[k] for k in ("arm", "panel", "block"))
    if (arm not in ARMS or panel not in PANELS or type(block) is not int
            or not START <= block < START + COUNT or key != f"{panel}-{block}-{arm}"):
        raise ValueError("case is outside the frozen selected stream")
    mode = SOURCE["arms"][arm]["mode"]
    pin()
    start, wall = process_time_ns(), perf_counter_ns()
    startup_phases = {}
    Parent, attach_physical, Checker, ordinary, solve = _call(startup_phases, "solver_import", _imports, mode)
    policy = model = None
    if mode in ("learned", "same-menu"):
        policy = _call(startup_phases, "policy_import", _policy_import)
    if mode == "learned":
        model = _call(startup_phases, "model_load", load, MODEL_FILE)
        if "model_key" in SOURCE:
            model = model[SOURCE["model_key"]]
    inputs = _call(startup_phases, "public_load", _public_cases, CASES_FILE)
    if block % 2:
        inputs.reverse()
    startup = process_time_ns() - start
    trace, geometry = [], {}
    for case in inputs:
        parent_start, parent_wall = process_time_ns(), perf_counter_ns()
        phases = {}
        row = dict(id=case["id"], phases=phases, edits=[], failure=None)
        try:
            original = {field: case[field] for field in FIELDS}
            parent = _call(phases, "solver_history", Parent, original)
            def build_checker():
                if mode == "ordinary":
                    return Checker(case)
                return Checker(case, geometry_cache=geometry)
            checker = _call(phases, "checker_history", build_checker)
            edits = case["edits"] if block % 2 == 0 else reversed(case["edits"])
            for edit in edits:
                eid = edit["id"]
                if panel == "broken" and eid != BROKEN[case["id"]]:
                    continue
                before, child_wall = process_time_ns(), perf_counter_ns()
                timing = {}
                child = dict(id=eid, phases=timing, failure=None, work={}, check={}, answer=None)
                try:
                    single = {field: edit[field] for field in EDIT_FIELDS}
                    # Upfront on EVERY selected edit, even if the subsequent
                    # solver immediately finds one bit.  No outcome-based skip.
                    actions = None
                    if mode in ("learned", "same-menu"):
                        function = policy.propose if mode == "learned" else policy.fixed_actions
                        arguments = (model, original, single) if mode == "learned" else (original, single)
                        actions = _call(timing, "propose", function, *arguments)
                        if not isinstance(actions, list):
                            raise ValueError("policy must return a JSON-safe action list")
                        child["actions"] = actions
                        child["proposed_actions"] = len(actions)
                    state = _call(timing, "update", parent.edit, single)
                    if mode in ("ordinary", "compact"):
                        stage, child["work"] = _call(timing, "solve", ordinary, state)
                    elif mode in ("learned", "same-menu"):
                        stage, child["work"] = _call(timing, "solve", solve, state, "advice", None, actions)
                    else:
                        selected_mode = "fresh" if mode == "fixed" else mode
                        stage, child["work"] = _call(timing, "solve", solve, state, selected_mode)
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
                child["wall_ns"] = perf_counter_ns() - child_wall
                row["edits"].append(child)
        except Exception as exc:
            row["failure"] = f"{type(exc).__name__}: {exc}"
        row["cpu_ns"] = process_time_ns() - parent_start
        row["wall_ns"] = perf_counter_ns() - parent_wall
        trace.append(row)
    duration, elapsed = process_time_ns() - start, perf_counter_ns() - wall
    # Research record binding and permanent compression follow the paid return.
    path = DEST / (key + ".jsonl.gz")
    with gzip.open(path, "xb", compresslevel=2) as file:
        for row in trace:
            file.write(encoded(row) + b"\n")
    failures = sum(bool(row["failure"]) + sum(bool(child["failure"]) for child in row["edits"]) for row in trace)
    return dict(**params, mode=mode, file=path.name, sha256=sha(path), cpu_ns=duration,
                wall_ns=elapsed, startup_ns=startup, startup_phases=startup_phases,
                model_sha256=MODEL_SHA256, public_parents=len(inputs), parents=len(trace),
                edits=sum(len(row["edits"]) for row in trace), failures=failures)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Run one frozen fresh-process deployment")
    parser.add_argument("--data-dir", default=str(OUT))
    parser.add_argument("--panel", choices=("mixed", "broken"), required=True)
    parser.add_argument("--arm", required=True)
    parser.add_argument("--block", type=int, default=0)
    args = parser.parse_args()
    setup(dict(data_dir=args.data_dir, panels=args.panel, arms=args.arm, begin=args.block, count=1))
    payload = dict(panel=args.panel, block=args.block, arm=args.arm)
    print(json.dumps(run(f"{args.panel}-{args.block}-{args.arm}", payload), sort_keys=True))
