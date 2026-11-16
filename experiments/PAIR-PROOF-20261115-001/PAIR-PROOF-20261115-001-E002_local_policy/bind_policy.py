"""Bind the frozen model, legal public inputs and complete sources to the paired held benchmark."""
import hashlib
import json
import os
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
TICKET = HERE.parent.name
OUT = ROOT / "artifacts" / TICKET / HERE.name
PREV = HERE.parent / (TICKET+"-E001_shared_witnesses")
PARENT = "PARENT-FOLD-20261115-001"
LEGACY = ROOT / "experiments" / PARENT / (PARENT+"-E001_consumer_edits")
JOINT = ROOT / "experiments/FOLD-TWO-OUTPUT-20261115-001/FOLD-TWO-OUTPUT-20261115-001-E001_joint_tables"


def read(path):
    return json.loads(path.read_bytes())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, obj):
    data = json.dumps(obj, separators=(",", ":"), sort_keys=True, allow_nan=False).encode()+b"\n"
    if path.exists():
        if path.read_bytes()!=data:
            raise FileExistsError(path)
        return
    with path.open("xb") as f:
        f.write(data)


def name(path):
    return str(path.relative_to(ROOT))


def main():
    freeze = read(OUT/"freeze.json")
    if any(sha(ROOT/f)!=digest for f,digest in freeze["sources_and_inputs"].items()):
        raise ValueError("training or model changed since freeze")
    model,public=OUT/"model.json",OUT/"blind/public.json"
    if sha(model)!=freeze["model_sha256"]:
        raise ValueError("model changed")
    grades=read(OUT/"blind/grades.json")
    broken={}
    for pid,p in grades.items():
        ids=[eid for eid,v in p["edits"].items() if v["kind"]=="broken"]
        if len(ids)!=1: raise ValueError("each parent needs one two-bit counterpart")
        broken[pid]=ids[0]
    write(OUT/"broken.json",broken)
    sources=[*(HERE/n for n in ["contract.json","identity.json","job.py","local_policy.py","make_panels.py","train.py","bind_policy.py"]),
             *(PREV/n for n in ["compact_control.py","packed_faces.py","pair_solver.py","pair_checker.py"]),
             *(LEGACY/n for n in ["controls.py","parent_engine.py","parent_checker.py","wire_return.py"]),
             JOINT/"joint_solver.py",JOINT/"checker.py"]
    data=[model,public,OUT/"broken.json",OUT/"freeze.json",OUT/"training-cost.json",OUT/"blind/origin.json"]
    arms={n:{"mode":n} for n in ("ordinary","compact","no-proof","balanced","fixed","same-menu","learned")}
    write(OUT/"design.json",dict(sources={name(p):sha(p) for p in sources},
          data={name(p):sha(p) for p in data}, arms=arms, cpu=min(os.sched_getaffinity(0)), python=sys.version,
          model=name(model),public=name(public),broken=name(OUT/"broken.json")))
    print(len(broken),"parents with two counterfactual consumer edits each",len(arms),"methods")


if __name__=="__main__":
    main()
