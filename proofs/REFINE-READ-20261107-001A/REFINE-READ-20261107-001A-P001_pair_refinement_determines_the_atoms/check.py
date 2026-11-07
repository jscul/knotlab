#!/usr/bin/env python3
"""Checks for REFINE-READ-20261107-001A: pair refinement determines the atoms.

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
import refine_lib as RF  # noqa: E402

T0 = time.time()
OUT = {}
SPACES = RF.NG.spaces()


def check(name, ok, info):
    OUT[name] = {"pass": bool(ok), "info": info}
    print("PASS" if ok else "FAIL", name, json.dumps(info, default=str), round(time.time() - T0, 1), "s", flush=True)
    if not ok:
        sys.exit(1)


def task(i):
    src, nm, S, ex = SPACES[i]
    kind, c = RF.report(src, nm, S, ex)
    return ("saved" if src.startswith("saved") else "fresh") + ", " + kind, c


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
    K1 = "colour refinement: spaces where a class holds lines of two atoms"
    KN = "pair refinement on the native map: spaces where a pair class holds pairs within and across atoms"
    KY = "pair refinement on the yes/no map: spaces where a pair class holds pairs within and across atoms"
    KO = "spaces with yes/no twins across atoms"
    check("1 colour refinement on the native map puts lines of two different atoms in one class in many spaces, Fano trees included",
          tot[K1] > 0, {"by kind": {k: {kk: v[kk] for kk in ("spaces", K1)} for k, v in sorted(rows.items())}, "all": tot[K1]})
    check("2 pair refinement on the native map never puts a pair within an atom and a pair across atoms in one class: in every space the "
          "atom partition is a union of stable pair classes, so every automorphism of the map preserves it",
          tot[KN] == 0, {"spaces": tot["spaces"], "spaces mixing": tot[KN]})
    check("3 control: on the yes/no creation relation alone, pair refinement mixes them, at least wherever lines of two atoms are yes/no "
          "twins (GLUE-READ C's obstruction)",
          tot[KY] >= tot[KO] > 0, {"spaces mixing on the yes/no map": tot[KY], "spaces with yes/no twins across atoms": tot[KO],
                                   "by kind": {k: {kk: v[kk] for kk in ("spaces", KY, KO)} for k, v in sorted(rows.items())}})

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
