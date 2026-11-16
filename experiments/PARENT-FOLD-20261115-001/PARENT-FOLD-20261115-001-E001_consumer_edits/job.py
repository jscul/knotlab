"""One fresh, single-CPU deployment per arm and timing block."""
import gzip
import hashlib
import json
import os
from pathlib import Path
import sys
from time import process_time_ns, perf_counter_ns


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
DEFAULT = ROOT / "artifacts" / HERE.parent.name / HERE.name
ARMS = ("ordinary", "ordinary-hint", "fold", "ordinary-prior", "ordinary-exact", "ordinary-exact-hint")
# Six balanced rotations and two mirrored rotations in an eight-block deployment.
ORDER = (0, 1, 5, 2, 4, 3)
PUBLIC_HISTORY = ("n", "gates", "upstream_count", "frontier", "outputs", "pieces")


def encoded(obj):
    return json.dumps(obj, separators=(",", ":"), sort_keys=True, allow_nan=False).encode()


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def setup(params):
    global OUT, BEGIN, COUNT, CPU
    OUT = Path(params.get("data_dir", DEFAULT)).resolve()
    BEGIN, COUNT = int(params.get("begin", 0)), int(params.get("count", 8))
    bound = json.loads((OUT / "data-bound.json").read_bytes())
    for file, expected in bound.items():
        if digest(OUT / file) != expected:
            raise ValueError(f"changed frozen input {file}")
    design = json.loads((OUT / "design.json").read_bytes())
    for name, expected in design["sources"].items():
        if digest(ROOT / name) != expected:
            raise ValueError(f"changed frozen source {name}")
    CPU = design["cpu"]
    sys.path[:0] = [str(HERE), str(ROOT / design["joint_solver_dir"])]


def cases():
    for repeat in range(BEGIN, BEGIN + COUNT):
        order = tuple((i + repeat) % len(ARMS) for i in ORDER)
        if repeat % 8 >= 6:
            order = tuple(reversed(order))
        for index in order:
            arm = ARMS[index]
            yield f"{repeat}-{arm}", dict(repeat=repeat, arm=arm)


def run(case_id, params):
    arm, repeat = params["arm"], params["repeat"]
    os.sched_setaffinity(0, {CPU})
    # The two designated arms receive the location as free experimental advice.
    # A process running an unhinted method never loads the location file.
    hints = json.loads((OUT / "hints.json").read_bytes()) if arm in ("fold","ordinary-hint","ordinary-exact-hint") else None
    start, wall = process_time_ns(), perf_counter_ns()
    from parent_engine import Parent, ordinary
    from parent_checker import Checker
    from wire_return import attach_physical
    choose = ordinary
    if arm == "fold":
        from fold import fold as choose
    elif arm in ("ordinary-exact","ordinary-exact-hint"):
        from controls import ordinary_exact as choose
    cases_in = json.loads((OUT / "public.json").read_bytes())
    if repeat % 2:
        cases_in.reverse()
    rows = []
    startup = process_time_ns() - start

    def query(engine, checker, original, edit, hint, solve, prior_program=None):
        phases = {}
        result = dict(id=edit["id"] if edit else None, phases=phases, answer=None,
                      work={}, edit_work={}, check={}, return_bytes=0, failure=None)
        def paid(name, fn, *args):
            before = process_time_ns()
            try:
                return fn(*args)
            finally:
                phases[name] = process_time_ns() - before
        began = process_time_ns()
        try:
            single = {k: edit[k] for k in ("gate", "pin", "to")} if edit else None
            state = paid("update", engine.edit, single)
            result["edit_work"] = state.work
            args = (state, hint, prior_program) if prior_program is not None else (state, hint)
            answer, result["work"] = paid("solve", solve, *args)
            result["origin"] = {k:answer[k] for k in ("summary_truths","retained_source_wires","output_reuse","route") if k in answer}
            answer = paid("link", attach_physical, original, answer)
            result["check"] = paid("verify", checker.verify, edit, answer)
            result["return_bytes"] = paid("serialize", lambda: len(encoded(answer)))
            result["answer"] = answer
        except Exception as exc:
            result["failure"] = f"{type(exc).__name__}: {exc}"
        result["cpu_ns"] = process_time_ns() - began
        return result

    for case in cases_in:
        entered = process_time_ns()
        row = dict(id=case["id"], setup_ns=0, history={}, prior=None, edits=[], failure=None)
        try:
            # No solver receives a case/edit id, the unseen sibling, or any grader field.
            original = {k: case[k] for k in PUBLIC_HISTORY}
            before = process_time_ns()
            parent = Parent(original)
            producer_init_ns = process_time_ns() - before
            before = process_time_ns()
            checker = Checker(case)
            checker_init_ns = process_time_ns() - before
            row["history"] = dict(producer=parent.work, checker=getattr(checker, "setup_work", {}),
                                  producer_ns=producer_init_ns, checker_ns=checker_init_ns)
            hint = tuple(hints[case["id"]]) if hints is not None else None
            row["setup_ns"] = process_time_ns() - entered
            prior_program = None
            if arm == "ordinary-prior":
                prior = row["prior"] = query(parent, checker, original, None, None, ordinary)
                if prior["failure"]:
                    raise ValueError("original global solution failed: " + prior["failure"])
                prior_program = {**prior["answer"], **prior["origin"]}
                hint = tuple(prior_program["triple"])
            edits = case["edits"] if repeat % 2 == 0 else reversed(case["edits"])
            for edit in edits:
                row["edits"].append(query(parent, checker, original, edit, hint, choose, prior_program))
        except Exception as exc:
            row["failure"] = f"{type(exc).__name__}: {exc}"
        row["cpu_ns"] = process_time_ns() - entered
        rows.append(row)
    duration, wall_time = process_time_ns() - start, perf_counter_ns() - wall
    # Research logs and their compression follow delivery of the serialized circuits.
    path = OUT / (case_id + ".jsonl.gz")
    with gzip.open(path, "xb", compresslevel=2) as fp:
        for row in rows:
            fp.write(encoded(row) + b"\n")
    failures = sum(bool(r["failure"]) + sum(bool(q["failure"]) for q in r["edits"]) for r in rows)
    return dict(**params, file=path.name, sha256=digest(path), cpu=CPU, cpu_ns=duration,
                wall_ns=wall_time, startup_ns=startup, parents=len(rows), failures=failures)
