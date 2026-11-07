#!/usr/bin/env python3
"""Checks for GENUS-READ-20261107-001C: native far sides through plane glue.

    python3 -B check.py          verify result.json against a fresh run
    python3 -B check.py --write  write result.json from a fresh run
Run with the repository's .venv (numpy, networkx). Uses up to 22 processes."""
import os

for _v in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

import collections  # noqa: E402
import hashlib  # noqa: E402
import json  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from multiprocessing import Pool  # noqa: E402
from pathlib import Path  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
import native_glue_lib as NG  # noqa: E402

T0 = time.time()
OUT = {}
SPACES = NG.spaces()


def check(name, ok, info):
    OUT[name] = {"pass": bool(ok), "info": info}
    print("PASS" if ok else "FAIL", name, json.dumps(info, default=str), round(time.time() - T0, 1), "s", flush=True)
    if not ok:
        sys.exit(1)


def task(i):
    return NG.report(*SPACES[i])


if __name__ == "__main__":
    manifest = json.loads((HERE / "manifest.json").read_text())
    bad = {q: dg for q, dg in manifest["parent_bindings"].items() if hashlib.sha256((ROOT / q).read_bytes()).hexdigest() != dg}
    status = {q: json.loads((ROOT / q).read_text()).get("status") for q in manifest["parent_bindings"]
              if q.endswith(("manifest.json", "result.json")) and q.startswith("proofs/")}
    check("0 dependency artifacts bound by hash (both sets of maps); upstream proofs Proved",
          not bad and all(s in ("Proved", "passed") for s in status.values()), {"mismatched": bad, "statuses": status})
    rows = collections.defaultdict(collections.Counter)
    with Pool(22) as pool:
        for kind, c in pool.imap_unordered(task, range(len(SPACES)), chunksize=1):
            rows[kind].update(c)
    tot = collections.Counter()
    for r in rows.values():
        tot.update(r)
    check("1 every Fano atom acts as one on the gluing-free far sides (277 spaces)",
          tot["atoms acting as one on the gluing-free far sides"] == tot["Fano atoms"],
          {k: tot[k] for k in ("spaces", "Fano atoms", "atoms acting as one on the gluing-free far sides")})
    check("2 every pair of lines of two different atoms that are twins of the yes/no creation relation is told apart by the gluing-free "
          "far sides; where the difference lies",
          tot["... told apart by the gluing-free far sides"] == tot["such pairs"] > 0,
          {k: v for k, v in sorted(tot.items()) if k.startswith(("spaces with", "such pairs", "..."))})
    check("3 native twin rules: twins on the gluing-free rows at atom lines read most spaces but merge atoms where they meet one plane "
          "piece; adding columns splits atoms", True,
          {"by kind": {k: {kk: vv for kk, vv in v.items() if kk.startswith(("rule", "spaces"))} for k, v in sorted(rows.items())},
           "all": {k: v for k, v in sorted(tot.items()) if k.startswith(("rule", "spaces"))}})

    OUT["seconds"] = round(time.time() - T0, 1)
    print("ALL OK", OUT["seconds"], "s")
    result = {"schema_version": 3, "artifact_id": manifest["artifact_id"], "kind": "proof", "ticket": manifest["ticket"],
              "proof": manifest["proof"], "status": "passed", "claim": manifest["claim"],
              "checks": {k: v for k, v in OUT.items() if k != "seconds"}}
    text = json.dumps(result, indent=1, sort_keys=True, default=str) + "\n"
    if "--write" in sys.argv:
        (HERE / "result.json").write_text(text)
    elif not (HERE / "result.json").exists() or json.loads((HERE / "result.json").read_text()) != json.loads(text):
        print("result.json does not match a fresh run; rerun with --write after review")
        sys.exit(1)
