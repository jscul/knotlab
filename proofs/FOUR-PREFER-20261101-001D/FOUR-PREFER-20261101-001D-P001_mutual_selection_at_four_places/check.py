#!/usr/bin/env python3
"""Checks for FOUR-PREFER-20261101-001D: mutual selection at four places (the assembled table of all 20 classes).

    python3 -B check.py          verify result.json against a fresh run
    python3 -B check.py --write  write result.json from a fresh run"""
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUT = {}


def check(name, ok, info):
    OUT[name] = {"pass": bool(ok), "info": info}
    print("PASS" if ok else "FAIL", name, json.dumps(info, default=str)[:600], flush=True)
    if not ok:
        print(json.dumps(info, default=str, indent=1))
        sys.exit(1)


manifest = json.loads((HERE / "manifest.json").read_text())
bad = {p: d for p, d in manifest["parent_bindings"].items() if hashlib.sha256((ROOT / p).read_bytes()).hexdigest() != d}
status = {p: json.loads((ROOT / p).read_text()).get("status") for p in manifest["parent_bindings"]}
check("0 dependency artifacts bound by hash; upstream proofs Proved and passed, ticket C Complete",
      not bad and all(s in ("Proved", "passed", "Complete") for s in status.values()), {"mismatched": bad, "statuses": status})

A = json.loads((ROOT / "proofs/FOUR-PREFER-20261101-001A/FOUR-PREFER-20261101-001A-P001_every_four_place_knot/result.json").read_text())
B = json.loads((ROOT / "proofs/FOUR-PREFER-20261101-001B/FOUR-PREFER-20261101-001B-P001_every_failing_class_builds_a_link/result.json").read_text())
table_a = next(v for k, v in A["checks"].items() if k.startswith("1 "))["info"]["table"]
hard_b = sorted(int(k.split()[1]) for k in next(v for k, v in B["checks"].items() if k.startswith("6 "))["info"])
verdict = {}
verdict[0] = ("count polynomial (2^(n-r) or 0)", "no: (M2) fails", "FOUR-PLACE D")
for c in (3, 11):
    verdict[c] = ("NP-complete on 4-regular systems (link pieces)", "no unless P = NP", "FOUR-PLACE C")
verdict[18] = ("never fails (signed Seymour lemma, Thomassen)", "no: (M1) fails", "FOUR-PLACE B")
verdict[19] = ("never fails (Hall matching, Tovey)", "no: (M1) fails", "A")
for c in hard_b:
    verdict[c] = ("NP-complete on 4-regular systems (link pieces, lifted)", "no unless P = NP", "B")
for c in (13, 14, 15, 16, 17):
    verdict[c] = ("never failed in any search (exact up to n = 6-8, hill-climbing to n = 14)", "open", "C")
rows = {f"class {c}": {"states": table_a[c]["states"], "relations": table_a[c]["relations"], "value-free": table_a[c]["value-free"],
                       "status": verdict[c][0], "mutually selecting": verdict[c][1], "evidence": verdict[c][2]} for c in sorted(verdict)}
check("1 every one of the 20 four-place knot classes appears once: 15 settled (none mutually selecting, unless NP-complete problems are "
      "polynomial), 5 open (the weak classes 13-17, never failing in any search)",
      sorted(verdict) == list(range(20)) and hard_b == [1, 2, 4, 5, 6, 7, 8, 9, 10, 12]
      and sum(v[1] == "open" for v in verdict.values()) == 5 and not any(v[1].startswith("yes") for v in verdict.values()), rows)

result = {"schema_version": 3, "artifact_id": manifest["artifact_id"], "kind": "proof", "ticket": manifest["ticket"], "proof": manifest["proof"],
          "status": "passed", "claim": manifest["claim"], "checks": OUT}
text = json.dumps(result, indent=1, sort_keys=True, default=str) + "\n"
if "--write" in sys.argv:
    (HERE / "result.json").write_text(text)
elif not (HERE / "result.json").exists() or json.loads((HERE / "result.json").read_text()) != json.loads(text):
    print("result.json does not match a fresh run; rerun with --write after review")
    sys.exit(1)
print("ALL OK")
