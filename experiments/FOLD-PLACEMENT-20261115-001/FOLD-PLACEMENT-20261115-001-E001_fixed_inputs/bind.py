"""Bind anonymous public inputs, a separate answer key, and the source of the timed study."""
from datetime import datetime, timezone
import platform
import sys

from job import CANDIDATES, DEFAULT, HERE, LIBRARY, NOTES, PEEL, ROOT, read, sha, write_new


def bind(out):
    if any((out / name).exists() for name in ("design.json", "panel.json", "grades.json", "given.json")):
        raise ValueError("binding requires a fresh study directory")
    out.mkdir(parents=True, exist_ok=True)
    sys.path.insert(0, str(NOTES))
    from tasks import tasks, grading
    panel = tasks()
    grades = grading()
    if len(panel) != 48 or len(grades) != 48 or len({r["truth"] for r in panel}) != 48:
        raise ValueError("expected 48 different labelled target truth tables")
    if {r["id"] for r in panel} != set(grades):
        raise ValueError("public/private identity mismatch")
    for row in panel:
        if set(row) != {"id", "n", "truth", "hint"} or row["n"] != 9 or len(set(row["hint"])) != 3:
            raise ValueError("ambiguous public input")
    candidate = next(p for p in read(CANDIDATES)["proposals"] if p["truth"] == 106)
    if candidate["nand_gates"] != 6:
        raise ValueError("unexpected given circuit")
    entry = {k: candidate[k] for k in ("truth", "expr", "dag")}
    write_new(out / "panel.json", panel)
    write_new(out / "grades.json", grades)
    write_new(out / "given.json", entry)
    sources = [HERE / x for x in ("bind.py", "job.py", "placement.py", "contract.json")]
    sources += [NOTES / x for x in ("tasks.py", "assess.py", "preregistration.md")]
    sources += [PEEL / "solver.py", PEEL / "peel.py", LIBRARY / "library_solver.py", CANDIDATES]
    write_new(out / "design.json", {
        "frozen_utc": datetime.now(timezone.utc).isoformat(),
        "python": platform.python_version(),
        "sources": {str(p.relative_to(ROOT)): sha(p) for p in sources},
        "data": {k: sha(out / k) for k in ("panel.json", "grades.json", "given.json")},
    })


if __name__ == "__main__":
    from pathlib import Path
    bind(Path(sys.argv[1]).resolve() if sys.argv[1:] else DEFAULT)
