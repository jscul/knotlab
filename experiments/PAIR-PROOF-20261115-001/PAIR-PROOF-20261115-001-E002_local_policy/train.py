"""Fit the local request policy from public training circuits and seal it before blind generation."""
from time import process_time_ns, perf_counter_ns

START_CPU = process_time_ns()
START_WALL = perf_counter_ns()

import hashlib
import json
import os
from pathlib import Path
import sys
from datetime import datetime, timezone

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUT = ROOT / "artifacts" / HERE.parent.name / HERE.name
FIELDS = ("n", "upstream_count", "gates", "frontier", "outputs", "pieces")
EDIT_FIELDS = ("gate", "pin", "to")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_once(path, obj):
    data = json.dumps(obj, sort_keys=True, separators=(",", ":"), allow_nan=False).encode() + b"\n"
    if path.exists():
        if path.read_bytes() != data:
            raise FileExistsError(path)
        return
    with path.open("xb") as stream:
        stream.write(data)


def main():
    if (OUT / "blind" / "public.json").exists() or (OUT / "model.json").exists():
        raise FileExistsError("Training requires a fresh model and an unopened blind panel.")
    os.sched_setaffinity(0, {min(os.sched_getaffinity(0))})
    import local_policy

    train = OUT / "train" / "public.json"
    origin = OUT / "train" / "origin.json"
    public = json.loads(train.read_bytes())
    stripped = [{**{k:p[k] for k in FIELDS}, "edits":[{k:q[k] for k in EDIT_FIELDS} for q in p["edits"]]}
                for p in public]
    fit_start = process_time_ns()
    model, selection = local_policy.fit(stripped, radii=(0, 1, 2, 4))
    fit_cpu = process_time_ns() - fit_start
    model_path = OUT / "model.json"
    write_once(model_path, model)
    write_once(OUT / "training-selection.json", selection)
    files = [model_path, train, origin, OUT / "training-selection.json", HERE / "local_policy.py",
             HERE / "make_panels.py", HERE / "charge_train.py", HERE / "contract.json",
             HERE / "identity.json", Path(__file__).resolve()]
    hashes = {str(p.relative_to(ROOT)):sha(p) for p in files}
    selection_kind = type(model).__name__
    write_once(OUT / "freeze.json", dict(
        scope="Fit on stripped, public train inputs before generating held circuits.",
        frozen_utc=datetime.now(timezone.utc).isoformat(), model_sha256=sha(model_path), sources_and_inputs=hashes,
        offered_radii=[0,1,2,4], training_parents=len(stripped),
        training_edits=sum(len(p["edits"]) for p in stripped), model_type=selection_kind,
        fit_cpu_ns=fit_cpu, train_process_cpu_ns=process_time_ns()-START_CPU, train_wall_ns=perf_counter_ns()-START_WALL,
        cpu=min(os.sched_getaffinity(0)), python=sys.version))
    print("Frozen", sha(model_path), "fit CPU", round(fit_cpu/1e9,3), flush=True)


if __name__ == "__main__":
    main()
