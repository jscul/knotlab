"""Freeze the fixed method before generating the fresh benchmark cases."""
from datetime import datetime, timezone
import os
from pathlib import Path
import platform
import sys

from job import DEFAULT, HERE, JOINT, NOTES, RANK, ROOT, check_hashes, read, sha, write_new


def now():
    return datetime.now(timezone.utc).isoformat()


def bind(out):
    out.mkdir(parents=True, exist_ok=True)
    sources = [HERE / name for name in ("advice.py","contract.json","job.py","prepare.py","probes.py","verifier.py")]
    sources += [NOTES / name for name in ("panels.py","assess.py","preregistration.md")]
    sources += [JOINT / name for name in ("checker.py","joint_solver.py","primitive_reference.py")]
    sources += [RANK / "solver.py"]
    sys.path[:0] = [str(HERE), str(NOTES), str(JOINT), str(RANK)]
    import panels, probes, verifier
    for module in (panels,probes,verifier):
        sources.extend(ROOT / name for name in getattr(module,"SOURCE_DEPENDENCIES",()))
    cpu = min(os.sched_getaffinity(0)) if hasattr(os,"sched_getaffinity") else None
    write_new(out / "design.json", dict(frozen_utc=now(), cpu=cpu, python=platform.python_version(),
              sources={str(p.relative_to(ROOT)):sha(p) for p in sources}))


def release(out):
    d=read(out / "design.json")
    check_hashes(ROOT, d["sources"])
    sys.path.insert(0, str(NOTES))
    import panels
    from advice import advice
    opened = now()
    data = {"design.json":sha(out/"design.json")}
    previous = set()
    for split,size in (("calibration",48), ("held",192)):
        public, grades = panels.build(split)
        if len(public) != size or len(grades) != size or set(grades) != {r["id"] for r in public}:
            raise ValueError("panel size or labels inconsistent")
        if any(set(r) != {"n","outputs","id"} or len(r["outputs"]) != 2 for r in public):
            raise ValueError("nonpublic solver fields")
        keys = {(r["n"], *sorted(r["outputs"])) for r in public}
        if len(keys) != size or keys & previous:
            raise ValueError("duplicate truth problem")
        previous.update(keys)
        values = {split:public, split + "-grades":grades}
        if split == "calibration":
            values.update(advice(public))
        for name,value in values.items():
            filename = name + ".json"
            write_new(out / filename, value)
            data[filename] = sha(out / filename)
    write_new(out / "data-bound.json", dict(opened_utc=opened, sealed_utc=now(), **data))


if __name__ == "__main__":
    fn = {"bind":bind,"release":release}[sys.argv[1]]
    fn(Path(sys.argv[2]).resolve() if len(sys.argv)>2 else DEFAULT)
