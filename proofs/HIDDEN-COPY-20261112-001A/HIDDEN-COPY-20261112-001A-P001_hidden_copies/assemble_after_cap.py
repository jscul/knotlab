#!/usr/bin/env python3
"""The endo part stopped at its frozen one-hour cap with 1,001 of its 1,267 (harmony, kind set) pairs saved; as frozen, it is reported
with the pairs reached. This writes result_endo.json from the saved rows, so that the binary part (which reads it) can run.

    .venv/bin/python3 -B assemble_after_cap.py"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
rows = json.loads((HERE / "partial" / "endo.json").read_text())
res = {"status": "stopped at its cap; assembled from the pairs saved",
       "checks": {"result": {"rows": sorted(rows, key=lambda r: (r["i"], r["j"])), "pairs saved": len(rows), "pairs frozen": 1267}}}
(HERE / "result_endo.json").write_text(json.dumps(res, indent=1, default=str) + "\n")
print(len(rows))
