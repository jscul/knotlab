#!/usr/bin/env python3
"""Stress test for REBASE-KNOTS-20261109-001, one size past check 3 (four tubes, rows 1 to 7): the native reading from a later row of a
tube that never grows, on the 5 x 4 tube at g = 2 and the 3 x 4 tube at g = 3, rows 0 to 9. Writes stress_test.json beside this file."""
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "proofs/REBASE-KNOTS-20261109-001A/REBASE-KNOTS-20261109-001A-P001_no_row_after_the_first_is_open"))
import check as C  # noqa: E402

T0 = time.time()
out = {}
for n, m, g in ((5, 4, 2), (3, 4, 3)):
    out["%d x %d, g = %d" % (n, m, g)] = C.readings(n, m, g, set(range(0, 10)), None)
    print(n, m, g, round(time.time() - T0), "s", flush=True)
out["pass"] = all(r[0] == {"as if open: binds / native: binds": sum(r[0].values())}
                  and all(set(c) == {"as if open: binds / native: fails"} for t0, c in r.items() if t0 >= 1) for r in out.values()
                  if isinstance(r, dict))
out["seconds"] = round(time.time() - T0)
(HERE / "stress_test.json").write_text(json.dumps(out, indent=1, default=str) + "\n")
print("PASS" if out["pass"] else "FAIL")
