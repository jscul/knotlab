"""Bind public paired tables, private fixture grades and the timed implementations."""
from datetime import datetime, timezone
import os
from pathlib import Path
import platform
import sys
import time

from job import ACQUISITION, DEFAULT, ENTRY, HERE, NOTES, ROOT, load, sha, write_new


def affinity():
    if not hasattr(os, "sched_getaffinity"):
        return None
    choices = sorted(os.sched_getaffinity(0))
    def sample():
        stats = {}
        for line in Path("/proc/stat").read_text().splitlines():
            tag, *rest = line.split()
            if tag.startswith("cpu") and tag[3:].isdigit():
                ticks = list(map(int, rest[:8]))
                stats[int(tag[3:])] = (ticks[3], sum(ticks))
        return stats
    if not Path("/proc/stat").is_file():
        return choices[0]
    first = sample()
    time.sleep(.25)
    second = sample()
    def idle_fraction(i):
        return (second[i][0] - first[i][0]) / max(1, second[i][1] - first[i][1])
    return max(choices, key=idle_fraction)


def bind(out):
    out.mkdir(parents=True, exist_ok=True)
    if any((out / k).exists() for k in ("design.json", "primary.json", "sensitivity.json", "grades.json", "given.json")):
        raise ValueError("choose a fresh unbound output directory")
    sys.path.insert(0, str(NOTES))
    import tasks
    primary, other = list(tasks.tasks()), list(tasks.sensitivity_tasks())
    grades = {"primary": tasks.grading(), "sensitivity": tasks.sensitivity_grading()}
    if len(primary) != 48 or len(other) != 4:
        raise ValueError("unexpected study size")
    all_cases = primary + other
    if len({r["id"] for r in all_cases}) != len(all_cases):
        raise ValueError("nonunique accounting ID")
    if len({(r["n"], *sorted(r["outputs"])) for r in all_cases}) != len(all_cases):
        raise ValueError("duplicate labelled joint task even after swapping the outputs")
    for name, rows in (("primary", primary), ("sensitivity", other)):
        if any(set(r) != {"id", "n", "outputs"} or len(r["outputs"]) != 2 for r in rows):
            raise ValueError("nonpublic input to a solver")
        if set(grades[name]) != {r["id"] for r in rows}:
            raise ValueError("grades misaligned")
        write_new(out / (name + ".json"), rows)
    write_new(out / "grades.json", grades)
    if load(ENTRY)["truth"] != 106:
        raise ValueError("unexpected archived ternary truth")
    write_new(out / "given.json", load(ENTRY))
    sources = [HERE / n for n in ("job.py", "bind.py", "checker.py", "joint_solver.py",
                                    "primitive_reference.py", "contract.json")]
    sources += [NOTES / n for n in ("tasks.py", "preregistration.md", "assess.py")]
    sources += [ENTRY, ACQUISITION]
    # Bind non-standard-library imports declared by the actual implementations.
    sys.path.insert(0, str(HERE))
    import joint_solver, primitive_reference
    for module in (joint_solver, primitive_reference):
        sources.extend(ROOT / p for p in getattr(module, "SOURCE_DEPENDENCIES", ()))
    data = {name: sha(out / name) for name in ("primary.json", "sensitivity.json", "grades.json", "given.json")}
    write_new(out / "design.json", dict(frozen_utc=datetime.now(timezone.utc).isoformat(), cpu=affinity(),
              python=platform.python_version(), data=data, sources={str(p.relative_to(ROOT)): sha(p) for p in sources}))


if __name__ == "__main__":
    bind(Path(sys.argv[1]).resolve() if sys.argv[1:] else DEFAULT)
