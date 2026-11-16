"""Bind code, train and seal once, then release the held public tables in a separate process."""
import argparse
from datetime import datetime, timezone
from itertools import combinations
import json
import os
from pathlib import Path
import platform
import sys
import time

from job import DEFAULT, HERE, NOTES, OLD, PREVIOUS, ROOT, check_hashes, encoded, read, sha, write_new


def utc():
    return datetime.now(timezone.utc).isoformat()


def choose_cpu():
    if not hasattr(os, "sched_getaffinity"):
        return None
    allowed = sorted(os.sched_getaffinity(0))
    def sample():
        ticks = {}
        for line in Path("/proc/stat").read_text().splitlines():
            name, *rest = line.split()
            if name.startswith("cpu") and name[3:].isdigit():
                values = list(map(int, rest[:8]))
                ticks[int(name[3:])] = (values[3], sum(values))
        return ticks
    if not Path("/proc/stat").is_file():
        return allowed[0]
    old = sample()
    time.sleep(.25)
    recent = sample()
    return max(allowed, key=lambda i: (recent[i][0] - old[i][0]) / max(1, recent[i][1] - old[i][1]))


def bind(out):
    out.mkdir(parents=True, exist_ok=True)
    sources = [HERE / f for f in ("contract.json", "prepare.py", "job.py", "solver.py", "policy.py")]
    sources += [NOTES / f for f in ("preregistration.md", "panels.py", "assess.py")]
    sources += [OLD / f for f in ("checker.py", "joint_solver.py", "primitive_reference.py")]
    sources.append(ROOT / "research" / PREVIOUS / "tasks.py")
    prior = ROOT / "artifacts" / PREVIOUS / OLD.name
    sources += [prior / f for f in ("primary.json", "sensitivity.json", "grades.json")]
    # Some immutable predecessor modules or public fixtures can be used to exclude
    # prior examples. Importing declarations in this binder never fits a model.
    sys.path[:0] = [str(HERE), str(NOTES), str(OLD)]
    import panels, solver, policy
    for module in (panels, solver, policy):
        for name in getattr(module, "SOURCE_DEPENDENCIES", ()):
            path = Path(name)
            sources.append(path if path.is_absolute() else ROOT / path)
    write_new(out / "design.json", dict(frozen_utc=utc(), cpu=choose_cpu(), python=platform.python_version(),
              sources={str(p.relative_to(ROOT)): sha(p) for p in sources}), durable=True)


def panel_integrity(public, grades, expected):
    if len(public) != expected or len(grades) != expected or {r["id"] for r in public} != set(grades):
        raise ValueError("unexpected panel size or key collision")
    if any(set(r) != {"id", "n", "outputs"} or len(r["outputs"]) != 2 for r in public):
        raise ValueError("nonpublic solver fields")
    if len({(r["n"], *sorted(r["outputs"])) for r in public}) != expected:
        raise ValueError("duplicate pair of truth tables")


def train(out):
    if any((out / f).exists() for f in ("model.json", "train-receipt.json", "held.json")):
        raise ValueError("training must precede release, in an unused model slot")
    d = read(out / "design.json")
    check_hashes(ROOT, d["sources"])
    if d["cpu"] is not None:
        os.sched_setaffinity(0, {d["cpu"]})
    sys.path[:0] = [str(HERE), str(NOTES)]
    log = out / "fit-attempts.jsonl"
    previous = [json.loads(s) for s in log.read_text().splitlines()] if log.exists() else []
    phases = {}
    def mark(label, c, w):
        phases[label] = dict(cpu_ns=time.process_time_ns() - c, wall_ns=time.perf_counter_ns() - w)
    started = utc()
    cpu, wall = time.process_time_ns(), time.perf_counter_ns()
    try:
        import panels, policy
        mark("imports", cpu, wall)
        c, w = time.process_time_ns(), time.perf_counter_ns()
        public, grades = panels.build_train()
        panel_integrity(public, grades, 48)
        labels = {k: {"width": v["width"], "minimizers": v["minimizers"]} for k, v in grades.items()}
        mark("training_tasks_and_labels", c, w)
        c, w = time.process_time_ns(), time.perf_counter_ns()
        model, diagnostics = policy.fit(public, labels)
        mark("fit", c, w)
        c, w = time.process_time_ns(), time.perf_counter_ns()
        write_new(out / "model.json", model, durable=True)
        sealed = read(out / "model.json")
        if encoded(sealed) != encoded(model):
            raise ValueError("model round trip changed parameters")
        group_check = public[0]
        eligible = tuple(combinations(range(group_check["n"]), 3))
        order = list(policy.Ranker(group_check["n"], sealed).order(tuple(group_check["outputs"]), eligible))
        if len(order) != len(eligible) or set(order) != set(eligible):
            raise ValueError("invalid ranking after reloading the trained policy")
        digest = sha(out / "model.json")
        mark("freeze_and_validate", c, w)
    except Exception as exc:
        with log.open("ab") as file:
            file.write(encoded(dict(status="failed", started=started, finished=utc(), cpu_ns=time.process_time_ns()-cpu,
                                    wall_ns=time.perf_counter_ns()-wall, error=repr(exc), phases=phases)) + b"\n")
        raise
    fit_cpu, fit_wall = time.process_time_ns() - cpu, time.perf_counter_ns() - wall
    attempt = dict(status="ok", started=started, finished=utc(), cpu_ns=fit_cpu, wall_ns=fit_wall, phases=phases)
    with log.open("ab") as file:
        file.write(encoded(attempt) + b"\n")
    write_new(out / "train.json", public)
    write_new(out / "train-grades.json", grades)
    write_new(out / "fit-diagnostics.json", diagnostics)
    write_new(out / "train-receipt.json", dict(cpu_ns=fit_cpu+sum(r["cpu_ns"] for r in previous),
              wall_ns=fit_wall+sum(r["wall_ns"] for r in previous), attempts=1+len(previous), phases=phases,
              cpu=d["cpu"], started=started, frozen_utc=attempt["finished"], model_sha256=digest,
              files={n:sha(out/n) for n in ("design.json", "train.json", "train-grades.json",
                                              "fit-attempts.jsonl", "fit-diagnostics.json", "model.json")}), durable=True)


def release(out):
    if (out / "held-bound.json").exists():
        raise ValueError("held panel already sealed")
    receipt = read(out / "train-receipt.json")
    check_hashes(out, receipt["files"])
    design = read(out / "design.json")
    check_hashes(ROOT, design["sources"])
    sys.path.insert(0, str(NOTES))
    import panels
    opened = utc()
    public, grades = panels.build_test()
    panel_integrity(public, grades, 192)
    training = read(out / "train.json")
    known = {(r["n"], *sorted(r["outputs"])) for r in training}
    if any((r["n"], *sorted(r["outputs"])) in known for r in public):
        raise ValueError("training/held table collision")
    write_new(out / "held.json", public)
    write_new(out / "held-grades.json", grades)
    files = {n:sha(out/n) for n in ("held.json", "held-grades.json", "model.json", "design.json", "train-receipt.json")}
    write_new(out / "held-bound.json", dict(test_opened_utc=opened, sealed_utc=utc(), **files), durable=True)


def label_given_tables(out):
    """Price obtaining all supervisory labels when the raw training tables already exist."""
    receipt = read(out / "train-receipt.json")
    check_hashes(out, receipt["files"])
    public = read(out / "train.json")
    grades = read(out / "train-grades.json")
    if receipt["cpu"] is not None:
        os.sched_setaffinity(0, {receipt["cpu"]})
    sys.path.insert(0, str(OLD))
    c, w = time.process_time_ns(), time.perf_counter_ns()
    from checker import JointChecker
    checkers, labels = {}, {}
    for task in public:
        n, targets = task["n"], tuple(task["outputs"])
        if n not in checkers:
            checkers[n] = JointChecker(n)
        checker = checkers[n]
        common = sorted(checker._essential(targets[0]) & checker._essential(targets[1]))
        widths = {g:(checker._classes(targets, g)-1).bit_length() for g in combinations(common, 3)}
        best = min(widths.values())
        labels[task["id"]] = (best, [g for g,width in widths.items() if width == best], list(widths.values()))
    cpu, wall = time.process_time_ns() - c, time.perf_counter_ns() - w
    for k,(best, groups, widths) in labels.items():
        if (best != grades[k]["width"] or widths != grades[k]["candidate_widths"] or
                sorted(groups) != sorted(map(tuple, grades[k]["minimizers"]))):
            raise ValueError("standalone public training labels differ")
    write_new(out / "label-cost.json", dict(cpu_ns=cpu, wall_ns=wall, labels=sum(len(z[2]) for z in labels.values()),
              training_tasks=len(public), exact=True, cpu=receipt["cpu"], source_sha256=sha(OLD/"checker.py"),
              train_sha256=sha(out/"train.json")), durable=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("phase", choices=("bind", "train", "label", "release"))
    parser.add_argument("--out", type=Path, default=DEFAULT)
    args = parser.parse_args()
    {"bind":bind, "train":train, "label":label_given_tables, "release":release}[args.phase](args.out.resolve())
