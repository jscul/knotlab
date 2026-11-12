#!/usr/bin/env python3
"""The scale part stopped at its frozen one-hour cap with 55 of its 56 (harmony, size) cells saved; as frozen, it is reported with the
cells reached. This writes result_scale.json from the saved rows (the missing cell: the seven-orbit harmony at 9 x 9).

    .venv/bin/python3 -B assemble_after_cap.py"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
rows = [json.loads(p.read_text()) for p in sorted((HERE / "partial").glob("scale_*.json"))]
res = {"status": "stopped at its cap; assembled from the cells saved",
       "checks": {"result": {"rows": sorted(rows, key=lambda r: (r["i"], r["n"])), "cells saved": len(rows), "cells frozen": 56,
                             "missing": "the seven-orbit harmony (index 43) at 9 x 9"}}}
(HERE / "result_scale.json").write_text(json.dumps(res, indent=1) + "\n")
print(len(rows))
