"""Referee R1 for KNOT-CAP-20261117-001: the six-starts' first difference at n = 10, exactly (referee_cap.exact, own code).

  ../../../.venv/bin/python -B referee_cap_n10.py > referee_cap_n10.json      (from this directory)
"""
import json

import referee_cap as R

out = {}
for start in ("fan6", "nonfan6"):
    L = R.exact(start, 10)[-1]
    out[start] = {"n": L["n"], "two_orders": str(L["two_orders"]), "two_orders_float": float(L["two_orders"]),
                  "lam": {str(k): float(v) for k, v in L["lam"].items()}, "labelled_bases": L["labelled_bases"]}
print(json.dumps(out, indent=1))
