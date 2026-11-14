"""Shared-runner entry for exact READ census checks; never launches a service."""
from __future__ import annotations

import json
import os
from pathlib import Path
import sys

sys.dont_write_bytecode = True
for _name in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ[_name] = "1"
HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

ROWS = None
PHASE = "combined"


def setup(params):
    global ROWS, PHASE
    PHASE = params.get("phase", "combined")
    if PHASE not in ("coverage", "conditional", "combined"):
        raise ValueError("phase must be coverage, conditional, or combined")
    index = json.loads((HERE / "source_index.json").read_text())
    source = HERE.parents[3] / index["source"]
    stat = source.stat()
    if (stat.st_size, stat.st_mtime_ns) != (index["size"], index["mtime_ns"]):
        raise ValueError("CARRY source file changed since offset index was made")
    ROWS = index["rows"]


def cases():
    if ROWS is None:
        setup({})
    for row in ROWS:
        yield row["key"], row


def run(case_id, payload):
    if case_id != payload["key"]:
        raise ValueError("case identity mismatch")
    import coverage
    from limits import Limits
    budget = Limits(585, 2_800_000_000)
    result = coverage.run_family(payload, semantic=PHASE != "conditional",
                                 conditional=PHASE != "coverage", checkpoint=budget.checkpoint)
    result["metrics"] = budget.metrics()
    return result
