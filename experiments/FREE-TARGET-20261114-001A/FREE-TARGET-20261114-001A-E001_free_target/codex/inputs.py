"""Read-only input loading for the specified 66-family computation."""
from __future__ import annotations

import gzip
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys

sys.dont_write_bytecode = True
for _name in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ[_name] = "1"

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
PATHS_FILE = ROOT / "experiments/EVERY-RAY-20261113-001A/EVERY-RAY-20261113-001A-E001_min_over_paths/codex/paths_dp.py"
SAMPLE = PATHS_FILE.parent / "sample"
CENSUS_FILE = ROOT / "artifacts/REACH-CENSUS-20261113-001A/REACH-CENSUS-20261113-001A-E001_reach_census/families.jsonl.gz"
POPULATION = HERE / "population.json"


def digest(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1048576), b""):
            h.update(block)
    return h.hexdigest()


def load_paths():
    name = "free_target_authorized_paths"
    if name not in sys.modules:
        spec = importlib.util.spec_from_file_location(name, PATHS_FILE)
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
    return sys.modules[name]


def selected_rows():
    merged, origins = {}, {}
    for filename in ("G.jsonl", "phase2.jsonl"):
        seen = set()
        with (SAMPLE / filename).open() as stream:
            for line in stream:
                if not line.strip():
                    continue
                row = json.loads(line)
                key = row["key"]
                if key in seen:
                    raise ValueError(f"duplicate key in {filename}: {key}")
                seen.add(key)
                if filename == "G.jsonl" or key in merged:
                    merged[key] = row
                    origins[key] = filename
    return {key: dict(merged[key], population_source=origins[key])
            for key in sorted(merged) if merged[key].get("class_path") == "grows"}


def freeze_population():
    rows = selected_rows()
    if len(rows) != 66:
        raise ValueError(f"population count {len(rows)} != 66; stop")
    result = dict(schema_version=1, count=len(rows), keys=list(rows),
                  sources={str((SAMPLE / n).relative_to(ROOT)): digest(SAMPLE / n)
                           for n in ("G.jsonl", "phase2.jsonl")},
                  rows=[dict(key=key, c=row["c"], lambda_path=row["lambda_path"],
                             L_path=row["L_path"], source=row["population_source"])
                        for key, row in rows.items()])
    with POPULATION.open("x") as stream:
        json.dump(result, stream, indent=2, sort_keys=True)
        stream.write("\n")
    return result


def load_population():
    result = json.loads(POPULATION.read_text())
    if result["count"] != 66 or len(result["keys"]) != 66 or len(set(result["keys"])) != 66:
        raise ValueError("invalid frozen population")
    for path, expected in result["sources"].items():
        if digest(ROOT / path) != expected:
            raise ValueError(f"population input changed: {path}")
    if result["keys"] != list(selected_rows()):
        raise ValueError("frozen keys differ from the specified merged population")
    return result


def load_census(keys):
    selected, keys = {}, set(keys)
    with gzip.open(CENSUS_FILE, "rt") as stream:
        for line in stream:
            row = json.loads(line)
            key = row["key"]
            if key in keys:
                if key in selected:
                    raise ValueError(f"duplicate selected census key: {key}")
                selected[key] = row
    if set(selected) != keys:
        raise ValueError(f"missing census keys: {sorted(keys - set(selected))}")
    return selected


if __name__ == "__main__":
    value = freeze_population()
    print(json.dumps(dict(count=value["count"], path=str(POPULATION))))
