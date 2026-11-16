"""Bind a paid comparison to immutable parent circuits, solver/checker sources and legal advice."""
import hashlib
import json
import os
from pathlib import Path
import platform
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from job import DATA, HERE, JOINT, OUT, PREV, ROOT, TICKET, load, sha

NOTES = ROOT / "research" / TICKET


def write(path, value):
    data = json.dumps(value, separators=(",", ":"), sort_keys=True, allow_nan=False).encode() + b"\n"
    if path.exists():
        if path.read_bytes() != data:
            raise FileExistsError(path)
        return
    with path.open("xb") as file:
        file.write(data)


def bind(plans, arms, destination=OUT):
    # Binding reads the predecessor's archived grade for the stream schedule.
    # Neither the grade nor a target width enters a solver or verifier.
    legacy = load(DATA / "data-bound.json")
    for name in ("public.json", "grades.json", "design.json"):
        if sha(DATA / name) != legacy[name]:
            raise ValueError("changed parent input: " + name)
    grades = load(DATA / "grades.json")
    broken = {}
    for pid, before in grades.items():
        edits = [eid for eid, record in before["edits"].items() if record["kind"] == "broken"]
        if len(edits) != 1:
            raise ValueError("each parent must supply one two-bit edit")
        broken[pid] = edits[0]
    for name in ("stream.json", "plans.json"):
        write(destination / name, broken if name == "stream.json" else plans)
    decisions = tuple(path for path in (NOTES / "protocol.md", NOTES / "coverage.py",
                                        HERE / "oracle_plans.py") if path.is_file())
    sources = [HERE / k for k in ("job.py","bind.py","prepare.py","contract.json","identity.json","packed_faces.py",
                                   "pair_checker.py","pair_solver.py")]
    if (HERE / "compact_control.py").exists():
        sources.append(HERE / "compact_control.py")
    sources += [*decisions, PREV / "controls.py", PREV / "parent_engine.py", PREV / "parent_checker.py",
                PREV / "wire_return.py", JOINT / "joint_solver.py", JOINT / "checker.py"]
    data = [DATA / "public.json", DATA / "grades.json", DATA / "data-bound.json",
            destination / "stream.json", destination / "plans.json", OUT / "coverage.json",
            OUT / "oracle_advice.json"]
    cpu = min(os.sched_getaffinity(0))
    design = dict(arms=arms, cpu=cpu, platform=platform.machine(), python=sys.version,
                  sources={str(p.relative_to(ROOT)):sha(p) for p in sources},
                  data={str(p.relative_to(ROOT)):sha(p) for p in data})
    write(destination / "design.json", design)
