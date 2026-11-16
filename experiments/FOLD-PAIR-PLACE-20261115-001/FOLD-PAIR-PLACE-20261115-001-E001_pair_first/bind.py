"""Seal the new unhinted tables and every solver dependency before starting paired timings."""
from datetime import datetime, timezone
from pathlib import Path
import sys

from job import DEFAULT, FIRST, FIRST_OUT, HERE, NOTES, PREV, ROOT, read, sha, write_new


def bind(out):
    out.mkdir(parents=True, exist_ok=True)
    if any((out / name).exists() for name in ("design.json", "given.json", "grades.json", "panel.json")):
        raise ValueError("choose an unbound output directory")
    sys.path.insert(0, str(NOTES))
    import tasks
    panel = tasks.tasks()
    grades = tasks.grading()
    if (len(set(r["truth"] for r in panel)) != 48 or set(grades) != {r["id"] for r in panel}
            or any(set(r) != {"id", "n", "truth"} or r["n"] != 9 for r in panel)):
        raise ValueError("invalid unhinted panel")
    write_new(out / "panel.json", panel)
    write_new(out / "grades.json", grades)
    write_new(out / "given.json", read(FIRST_OUT / "given.json"))
    previous = read(FIRST_OUT / "design.json")
    sources = {name: dig for name, dig in previous["sources"].items()
               if Path(name).name in ("placement.py", "peel.py", "solver.py", "library_solver.py", "tasks.py")}
    for name, wanted in sources.items():
        if sha(ROOT / name) != wanted:
            raise ValueError("predecessor source changed: " + name)
    for p in [HERE / x for x in ("job.py", "bind.py", "pair_solver.py", "contract.json")] + [
            NOTES / x for x in ("preregistration.md", "tasks.py", "assess.py")]:
        sources[str(p.relative_to(ROOT))] = sha(p)
    inputs = {n: sha(out / n) for n in ("panel.json", "given.json", "grades.json")}
    write_new(out / "design.json", dict(frozen_utc=datetime.now(timezone.utc).isoformat(), data=inputs,
              sources=sources, prior_design_sha256=sha(FIRST_OUT / "design.json")))


if __name__ == "__main__":
    bind(Path(sys.argv[1]).resolve() if sys.argv[1:] else DEFAULT)
