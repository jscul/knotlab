"""Read-only imports and census inputs for the frozen CARRY computation."""
from __future__ import annotations

from collections import Counter
import gzip
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys

sys.dont_write_bytecode = True
for _variable in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ[_variable] = "1"

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
FT = ROOT / "experiments/FREE-TARGET-20261114-001A/FREE-TARGET-20261114-001A-E001_free_target/codex"
PATHS_DIR = ROOT / "experiments/EVERY-RAY-20261113-001A/EVERY-RAY-20261113-001A-E001_min_over_paths/codex"
CENSUS = ROOT / "experiments/CENSUS-FORGET-20261114-001A/CENSUS-FORGET-20261114-001A-E001_forget_census/full/results.jsonl"
ARCHIVE = ROOT / "artifacts/REACH-CENSUS-20261113-001A/REACH-CENSUS-20261113-001A-E001_reach_census/families.jsonl.gz"
DRAWS = ROOT / "experiments/REACH-CENSUS-20261113-001A/REACH-CENSUS-20261113-001A-E001_reach_census/codex/draws.jsonl.gz"
INVENTORY = ROOT / "research/CENSUS-FORGET-20261114-001/referee-R1/codex/target_inventory.json"
TIES = ROOT / "experiments/TIE-CYCLE-20261114-001A/TIE-CYCLE-20261114-001A-E001_ties/ties.py"


def permitted(path):
    path = Path(path).resolve()
    if not path.is_relative_to(HERE):
        raise ValueError(f"write outside CODEX forbidden: {path}")
    return path


def dump(path, value):
    path = permitted(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n")


def digest(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for part in iter(lambda: stream.read(1 << 20), b""):
            h.update(part)
    return h.hexdigest()


def module(name, path):
    if name not in sys.modules:
        spec = importlib.util.spec_from_file_location(name, path)
        mod = importlib.util.module_from_spec(spec)
        sys.modules[name] = mod
        spec.loader.exec_module(mod)
    return sys.modules[name]


def load_paths():
    for directory in (HERE, PATHS_DIR, FT):
        if str(directory) not in sys.path:
            sys.path.append(str(directory))
    return module("carry_authorized_paths", PATHS_DIR / "paths_dp.py")


def load_relations():
    load_paths()
    return module("carry_authorized_relations", FT / "relations.py")


def load_ties():
    return module("carry_authorized_ties", TIES)


def carry_order(key):
    return hashlib.sha256(("CARRY:" + key).encode()).hexdigest()


def load_records():
    """Latest census attempt per key, with failed records rejected."""
    rows = {}
    with CENSUS.open() as stream:
        for line in stream:
            rec = json.loads(line)
            rows[rec["case"]] = rec
    if any(row["status"] != "ok" for row in rows.values()):
        raise ValueError("census has a final non-ok record")
    return {key: row["result"] for key, row in rows.items()}


def population(records=None):
    records = load_records() if records is None else records
    keys = sorted((key for key, row in records.items()
                   if not row["chain"] and row["verdict"] in ("non-forgetting", "capped")), key=carry_order)
    if len(keys) != 5964:
        raise ValueError(f"specified population changed: {len(keys)} != 5964")
    return keys


def load_archive(keys):
    keys = set(keys)
    found = {}
    with gzip.open(ARCHIVE, "rt") as stream:
        for line in stream:
            row = json.loads(line)
            if row["key"] in keys:
                if row["key"] in found:
                    raise ValueError("duplicate family archive key")
                found[row["key"]] = row
    if set(found) != keys:
        raise ValueError(f"archive missing {len(keys - set(found))} keys")
    return found


load_census = load_archive


def weights(keys):
    keys = set(keys)
    counts = Counter()
    with gzip.open(DRAWS, "rt") as stream:
        for line in stream:
            row = json.loads(line)
            if row["key"] in keys:
                counts[row["key"]] += 1
    if set(counts) != keys:
        raise ValueError("population key absent from draw stream")
    return dict(counts)


def source_hashes():
    paths = [CENSUS, ARCHIVE, DRAWS, INVENTORY, TIES, FT / "inputs.py", FT / "relations.py",
             FT / "limits.py", PATHS_DIR / "paths_dp.py", PATHS_DIR / "run_paths.py",
             PATHS_DIR / "call_symmetry.py", ROOT / "scripts/longrun.py",
             ROOT / "research/CARRY-BOUND-20261114-001/preregistration.md",
             ROOT / "research/CARRY-BOUND-20261114-001/codex_spec.md",
             ROOT / "research/CARRY-BOUND-20261114-001/advisor_review2_answer.md"]
    paths.extend(Path(m.__file__).resolve() for m in
                 (load_paths().CENSUS, load_paths().CENSUS.LS, load_paths().L, load_paths().GA))
    return {str(p.relative_to(ROOT)): digest(p) for p in sorted(set(paths))}


def verify_sources():
    manifest = HERE / "source_manifest.json"
    if not manifest.exists():
        raise ValueError("freeze source_manifest.json before running the prepared jobs")
    for relative, expected in json.loads(manifest.read_text())["sha256"].items():
        if digest(ROOT / relative) != expected:
            raise ValueError(f"frozen dependency changed: {relative}")
