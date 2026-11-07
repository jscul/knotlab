#!/usr/bin/env python3
"""Checks for FAR-READ-20261106-001A: the far-side map.

    python3 -B check.py          verify result.json against a fresh run
    python3 -B check.py --write  write result.json from a fresh run
Run with the repository's .venv (numpy, networkx). Uses up to 22 processes. The exact creation maps are GLUE-READ B's maps.json.gz,
bound by hash."""
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
import far_lib as FL  # noqa: E402

T0 = time.time()
OUT = {}
SPACES, MAPS = FL.saved()


def check(name, ok, info):
    OUT[name] = {"pass": bool(ok), "info": info}
    print("PASS" if ok else "FAIL", name, json.dumps(info, default=str), round(time.time() - T0, 1), "s", flush=True)
    if not ok:
        sys.exit(1)


def task(i):
    src, nm, S = SPACES[i]
    return FL.structure(S, MAPS[i])


if __name__ == "__main__":
    manifest = json.loads((HERE / "manifest.json").read_text())
    bad = {q: dg for q, dg in manifest["parent_bindings"].items() if hashlib.sha256((ROOT / q).read_bytes()).hexdigest() != dg}
    status = {q: json.loads((ROOT / q).read_text()).get("status") for q in manifest["parent_bindings"]
              if q.endswith(("manifest.json", "result.json")) and q.startswith("proofs/")}
    check("0 dependency artifacts bound by hash (GLUE-READ B's exact maps included); upstream proofs Proved",
          not bad and all(s in ("Proved", "passed") for s in status.values()), {"mismatched": bad, "statuses": status})

    c = collections.Counter()
    with Pool(22) as pool:
        for r in pool.imap_unordered(task, range(len(SPACES))):
            c.update(r)
    vec = collections.defaultdict(dict)
    for (k, v), x in c.items():
        if k.startswith("vector"):
            vec[k][v] = x
    allv = collections.Counter()
    for d in vec.values():
        allv.update(d)
    fano_is_c58 = all((code[2] == "F") == (code[3] == "C") for code in allv if code != "-")
    k_in_c = all(code[1] == "c" for code in allv if code != "-" and code[0] == "K")
    small_without_big = {k: {v: x for v, x in d.items() if v != "-" and v[1] == "c" and v[2] == "."} for k, d in vec.items()}
    check("1 how the far sides create together, over all 191 maps: the Fano plane and census 58 create at exactly the same pairs; K4^(3) "
          "creates only where census 6 does; census 6 creates without the Fano plane only at glue lines; so at an atom line creation is "
          "one of four strengths (none; the Fano plane and census 58; with census 6; with all four)",
          fano_is_c58 and k_in_c and not small_without_big.get("vector at a gluing atom line") and
          set(vec["vector at a gluing atom line"]) <= {"....", "..FC", ".cFC", "KcFC", "-"},
          {"vectors": {k: dict(sorted(d.items())) for k, d in sorted(vec.items())},
           "census 6 without the Fano plane": small_without_big})
    at = {k[1]: x for k, x in c.items() if k[0] == "atoms"}
    check("2 every Fano atom acts as one from outside: every atom line outside it receives the same far-side vector from each of its "
          "lines; on glue lines and in what it receives, an atom's lines differ", at["act as one on atom lines outside"] == at["count"] > 0
          and at["act as one on glue lines"] < at["count"] and at["seen alike by every atom line outside (columns)"] < at["count"], at)

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
