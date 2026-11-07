#!/usr/bin/env python3
"""Checks for ATOM-ONE-20261107-001C: the exception, saved and fresh.

    python3 -B check.py          verify result.json against a fresh run
    python3 -B check.py --write  write result.json from a fresh run
Run with the repository's .venv (numpy, networkx). Uses up to 22 processes. The exact creation maps are GLUE-READ B's (saved spaces) and
FAR-READ C's (fresh spaces), both bound by hash."""
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
import exc_lib as XL  # noqa: E402

FL = XL.load("ao_c_far_lib", ROOT / "proofs/FAR-READ-20261106-001A/FAR-READ-20261106-001A-P001_the_far_side_map/far_lib.py")
FRESH = ROOT / "proofs/FAR-READ-20261106-001C/FAR-READ-20261106-001C-P001_fresh_spaces/maps.json.gz"
T0 = time.time()
OUT = {}


def check(name, ok, info):
    OUT[name] = {"pass": bool(ok), "info": info}
    print("PASS" if ok else "FAIL", name, json.dumps(info, default=str), round(time.time() - T0, 1), "s", flush=True)
    if not ok:
        sys.exit(1)


def all_spaces():
    spaces, maps = FL.saved()
    fs, fm = FL.G.load_maps(FRESH)
    return [("saved " + src, S, ex) for (src, nm, S), ex in zip(spaces, maps)] + [(src, S, ex) for (src, nm, S), ex in zip(fs, fm)]


SPACES = all_spaces()


def task(i):
    src, S, ex = SPACES[i]
    return src, XL.space_report(S, ex)


if __name__ == "__main__":
    manifest = json.loads((HERE / "manifest.json").read_text())
    bad = {q: dg for q, dg in manifest["parent_bindings"].items() if hashlib.sha256((ROOT / q).read_bytes()).hexdigest() != dg}
    status = {q: json.loads((ROOT / q).read_text()).get("status") for q in manifest["parent_bindings"]
              if q.endswith(("manifest.json", "result.json")) and q.startswith("proofs/")}
    check("0 dependency artifacts bound by hash (both sets of exact maps included); upstream proofs Proved",
          not bad and all(s in ("Proved", "passed") for s in status.values()), {"mismatched": bad, "statuses": status})

    rows = collections.defaultdict(collections.Counter)
    with Pool(22) as pool:
        for src, c in pool.imap_unordered(task, range(len(SPACES)), chunksize=1):
            rows["saved" if src.startswith("saved") else "fresh"].update(c)
            rows["saved" if src.startswith("saved") else "fresh"]["spaces"] += 1
    rows = {k: dict(sorted(v.items())) for k, v in sorted(rows.items())}
    explore = "--explore" in sys.argv
    for part in ("saved", "fresh"):
        r = rows[part]
        n = r["(removal, atom line) pairs"]
        check("%d %s spaces: at every removal and line of a Fano atom not holding it, the exact far-side vector equals the verdict of "
              "the atom's real side with the removal's side replaced by its port relation, and equals the atom's own verdict"
              % (1 if part == "saved" else 2, part),
              explore or (r["exact = the real side of B with R, far side by far side"] == n and r["exact = B's own verdict, far side by far side"] == n),
              r)
    tot = collections.Counter()
    for r in rows.values():
        tot.update(r)
    check("3 the exception: at every receiving cut whose relation has six patterns, at the cut lines, the real removal's side adds no far "
          "side to the atom's own verdict",
          explore or tot["... exception lines where the real removal's side adds a far side to B's own verdict"] == 0,
          {k: tot[k] for k in ("receiving cuts where the relation has six patterns (removal, cut)",
                               "... exception lines (a receiver's cut line, six patterns)",
                               "... exception lines where B's own verdict lacks census 6 or K4^(3) (room to add)",
                               "... exception lines where the real removal's side adds a far side to B's own verdict")})

    OUT["seconds"] = round(time.time() - T0, 1)
    print("ALL OK", OUT["seconds"], "s")
    if explore:
        sys.exit(0)
    result = {"schema_version": 3, "artifact_id": manifest["artifact_id"], "kind": "proof", "ticket": manifest["ticket"],
              "proof": manifest["proof"], "status": "passed", "claim": manifest["claim"],
              "checks": {k: v for k, v in OUT.items() if k != "seconds"}}
    text = json.dumps(result, indent=1, sort_keys=True, default=str) + "\n"
    if "--write" in sys.argv:
        (HERE / "result.json").write_text(text)
    elif not (HERE / "result.json").exists() or json.loads((HERE / "result.json").read_text()) != json.loads(text):
        print("result.json does not match a fresh run; rerun with --write after review")
        sys.exit(1)
