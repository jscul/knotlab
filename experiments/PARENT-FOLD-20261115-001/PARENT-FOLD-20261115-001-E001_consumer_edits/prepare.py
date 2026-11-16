"""Seal executable sources before generating this experiment's supplied-piece stream."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import sys
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
TICKET = HERE.parent.name
NOTES = ROOT / "research" / TICKET
OUT = ROOT / "artifacts" / TICKET / HERE.name
JOINT = "FOLD-TWO-OUTPUT-20261115-001"
ORDER = "TRIPLE-ORDER-20261115-001"


def read(path):
    return json.loads(path.read_bytes())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, value):
    with path.open("xb") as file:
        file.write(json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode() + b"\n")


def bind():
    joint_dir = ROOT / "experiments" / JOINT / (JOINT + "-E001_joint_tables")
    files = [HERE / name for name in ("identity.json", "contract.json", "prepare.py", "job.py",
                                      "parent_engine.py", "parent_checker.py", "fold.py", "controls.py", "wire_return.py")]
    files += [NOTES / "panels.py", NOTES / "preregistration.md", joint_dir / "joint_solver.py",
              joint_dir / "checker.py", ROOT / "research" / ORDER / "panels.py",
              ROOT / "research" / JOINT / "tasks.py"]
    sources = {str(file.relative_to(ROOT)): sha(file) for file in files}
    write(OUT / "design.json", dict(sources=sources, cpu=min(os.sched_getaffinity(0)),
          python=sys.version, host=platform.machine(), joint_solver_dir=str(joint_dir.relative_to(ROOT)),
          timing_blocks=8, parents=36, edits=72, created_unix_ns=time.time_ns()))


def panel():
    design = read(OUT / "design.json")
    if any(sha(ROOT / file) != digest for file, digest in design["sources"].items()):
        raise ValueError("a source changed after binding")
    sys.path.insert(0, str(NOTES))
    from panels import build
    public, grades = build("oracle")
    if len(public) != 36 or len(grades) != 36:
        raise ValueError("incomplete panel")
    hints = {key: value["base"]["anchor"] for key, value in grades.items()}
    for name, value in (("public", public), ("hints", hints), ("grades", grades)):
        write(OUT / (name + ".json"), value)
    write(OUT / "data-bound.json", {f:sha(OUT / f) for f in
          ("design.json", "public.json", "hints.json", "grades.json")})


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("bind", "panel"))
    args = parser.parse_args()
    (bind if args.action == "bind" else panel)()
