#!/usr/bin/env python3
"""Referee FAR-BOUND-R1, the 8 bases dropped at the far part's 1,800-second cap, rerun with a longer cap. This uses the census's own
code (experiments/FAR-BOUND-20261112-001A/.../census.py, imported unchanged, its output folder redirected here), so it is a completion
of the census's data for question (ii), not an independent recomputation. The 26 decided rows are copied in as done, so only the 8
dropped bases run.

    python3 -B ref_far_dropped.py [cap seconds] [workers]      (writes far_dropped/far.jsonl)"""
import importlib.util
import json
import os
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SRC = ROOT / "experiments" / "FAR-BOUND-20261112-001A" / "FAR-BOUND-20261112-001A-E001_bounded_far" / "census.py"
ART = ROOT / "artifacts" / "FAR-BOUND-20261112-001A" / "FAR-BOUND-20261112-001A-E001_bounded_far"


def main():
    cap = sys.argv[1] if len(sys.argv) > 1 else "5400"
    workers = sys.argv[2] if len(sys.argv) > 2 else "3"
    out = HERE / "far_dropped"
    out.mkdir(exist_ok=True)
    shutil.copy(ART / "recheck.jsonl", out / "recheck.jsonl")
    if not (out / "far.jsonl").exists():
        rows = [json.loads(l) for l in (ART / "far.jsonl").read_text().splitlines()]
        (out / "far.jsonl").write_text("".join(json.dumps(r) + "\n" for r in rows if "far" in r))
    spec = importlib.util.spec_from_file_location("fbcensus", SRC)
    C = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(C)
    C.OUT = str(out)
    sys.argv = [str(SRC), "--part", "far", "--workers", workers, "--cap", cap]
    C.main()


if __name__ == "__main__":
    main()
