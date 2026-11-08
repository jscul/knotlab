#!/usr/bin/env python3
"""Checks for TRISUM-READ-20261107-001C: one size past, four junctions.

    python3 -B check.py          verify result.json against a fresh run
    python3 -B check.py --write  write result.json from a fresh run
Run with the repository's .venv (numpy, networkx). Uses up to 3 processes; the full-memory enumerator once, near 10 GB."""
import os

for _v in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

import datetime  # noqa: E402
import gzip  # noqa: E402
import hashlib  # noqa: E402
import json  # noqa: E402
import random  # noqa: E402
import subprocess  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from multiprocessing import Pool  # noqa: E402
from pathlib import Path  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
import order_lib as OL  # noqa: E402
ML = OL.ML
TR = ML.TR
A = ML.A

FROZEN = "e15fce8fa9d18a219df2b6fa82eaff9ef96d4d0ff3adb7a9839335bfa0b94d29"   # ticket A's predictions.json
EXPECTED = []   # the frozen statements that fail on this space, as scored after its map was computed
GEN = """
import json, sys
sys.path.insert(0, {a!r})
import family_lib as FAM
FA = FAM.FA
G = FA.trisum_brace(7, 4, FAM.CUBES)
Hg, kap, nsq = FA.pfaffian_signing(G)
mn, nu = FA.min_signing(Hg, kap)
print(json.dumps([list(l) for l in FA.edge_atoms(Hg, mn)]))
"""
RL = TR.load("tr_refine_lib", ROOT / "proofs/REFINE-READ-20261107-001A/REFINE-READ-20261107-001A-P001_pair_refinement_determines_the_atoms"
             / "refine_lib.py")
TR.engine()
T0 = time.time()
OUT = {}
SPACE = json.loads((HERE / "space.json").read_text())
MAP = json.load(gzip.open(HERE / "map.json.gz", "rt"))
H = [tuple(l) for l in MAP["lines"]]
N = MAP["points"]
WIDTH, START, ORDER = OL.fixed_order(H, N)


def check(name, ok, info):
    OUT[name] = {"pass": bool(ok), "info": info}
    print("PASS" if ok else "FAIL", name, json.dumps(info, default=str), round(time.time() - T0, 1), "s", flush=True)
    if not ok:
        sys.exit(1)


def table(d):
    return {str(L): (None if v is None else [int(x) for x in v]) for L, v in d.items()}


def lean_task(M):
    out, ns = OL.exact_row(H, N, M, ORDER)
    stored = MAP["rows"][str(M)]
    return M, ns == stored["solutions"] and table(out) == stored["row"]


if __name__ == "__main__":
    manifest = json.loads((HERE / "manifest.json").read_text())
    bad = {q: dg for q, dg in manifest["parent_bindings"].items() if hashlib.sha256((ROOT / q).read_bytes()).hexdigest() != dg}
    status = {q: json.loads((ROOT / q).read_text()).get("status") for q in manifest["parent_bindings"]
              if q.endswith(("manifest.json", "result.json")) and q.startswith("proofs/")}
    check("0 dependency artifacts bound by hash; tickets A and B Proved",
          not bad and all(s in ("Proved", "passed") for s in status.values()), {"mismatched": bad, "statuses": status})

    env = dict(os.environ, PYTHONHASHSEED="0")
    regen = json.loads(subprocess.run([sys.executable, "-B", "-c", GEN.format(a=str(A))], env=env, check=True, capture_output=True,
                                      text=True, cwd=str(ROOT)).stdout.strip().splitlines()[-1])
    st = TR.structure(H)
    pr = (A / "predictions.json").read_bytes()
    chosen = datetime.datetime.fromisoformat(SPACE["chosen at"])
    PROV = json.loads((HERE / "provenance.json").read_text())
    finished = datetime.datetime.fromisoformat(PROV["finished"])
    sizes = [c[0] for c in SPACE["candidates (lines, seed)"]]
    check("1 the space: the generator with four trisums at seed 7 (hash seed 0) gives exactly the stored lines, the smallest of the "
          "candidates; it has 62 points, 6 atoms and four junctions; it was chosen, with the predictions frozen as ticket A froze them, "
          "before its map was computed",
          regen == SPACE["space"]["lines"] == MAP["lines"]
          and hashlib.sha256(json.dumps(MAP["lines"]).encode()).hexdigest() == SPACE["space"]["lines sha256"]
          and len(H) == min(sizes) and sizes.count(min(sizes)) == 1 and len(st["atoms"]) == 6 and len(st["trisectors"]) == 4
          and hashlib.sha256(pr).hexdigest() == FROZEN and finished is not None and finished > chosen
          and sorted(MAP["rows"], key=int) == [str(M) for M in range(len(H))] and all(len(r["row"]) == len(H) - 1 for r in MAP["rows"].values()),
          {"points": N, "lines": len(H), "atoms": len(st["atoms"]), "junctions": len(st["trisectors"]), "leaves": st["leaves"],
           "junction lines carrying an atom": sorted(st["junction"] & st["loaded"]), "chosen at": SPACE["chosen at"],
           "map finished": PROV["finished"], "solutions per row": sorted({r["solutions"] for r in MAP["rows"].values()})})

    rows = sorted({0, *random.Random(7).sample(range(1, len(H)), 2)})
    with Pool(3) as pool:
        lean = pool.map(lean_task, rows)
    a = OL.lean_solutions(H, [(0, 0, 0)] * len(H), N, 0, ORDER)
    b = ML.lean_solutions(H, [(0, 0, 0)] * len(H), N, skip=0)
    same_lean = a.shape == b.shape and bool((a == b).all())
    del b
    c = TR.engine().TL.solutions(H, [(0, 0, 0)] * len(H), N, skip=0)
    same_full = a.shape == c.shape and bool((a == c).all())
    del a, c
    check("2 the engines agree: three rows recomputed in the fixed order equal the stored rows; on row 0 the fixed-order enumeration, "
          "ticket B's lean enumeration (breadth-first from point 0) and CHAIN-TRANSFER A's full-memory one return the same solution array",
          all(x[1] for x in lean) and same_lean and same_full,
          {"rows": rows, "equal": sum(x[1] for x in lean), "order": {"start": START, "most lines open": WIDTH},
           "row 0 arrays equal (fixed order = ticket B's lean)": same_lean, "row 0 arrays equal (fixed order = full memory)": same_full})

    ex = {int(m): {int(L): (None if v is None else tuple(bool(x) for x in v)) for L, v in r["row"].items()} for m, r in MAP["rows"].items()}
    rep = TR.report(H, ex, RL)
    fails = [k for k, v in rep.items() if k.startswith("P") and v is not True]
    check("3 the frozen statements on the four-junction space: the outcomes are as reported (" +
          ("every one of P1 to P7 holds" if not EXPECTED else "failures listed in EXPECTED") + ")",
          fails == EXPECTED, {"report": {k: v for k, v in rep.items() if not k.startswith("P")}, "failing": fails})

    alone = sum(1 for r in MAP["rows"].values() for v in r["row"].values() if v is not None and v[1] and not (v[0] or v[2] or v[3]))
    entries = sum(1 for r in MAP["rows"].values() for v in r["row"].values() if v is not None)
    check("4 yes/no creation is native here too: census 6 never creates where none of the three order-free far sides does",
          alone == 0, {"non-degenerate entries": entries, "census 6 alone": alone})

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
