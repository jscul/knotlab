#!/usr/bin/env python3
"""Checks for GLUE-READ-20261106-001A: creation is decided by the receiving cut.

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
import port_lib as PL  # noqa: E402

TL, TR, RD = PL.TL, PL.TR, PL.RD
SINGLES, PAIRS = PL.deep_relations()
FARS = [f for f, F in TL.SL.FARS]
T0 = time.time()
OUT = {}


def check(name, ok, info):
    OUT[name] = {"pass": bool(ok), "info": info}
    print("PASS" if ok else "FAIL", name, json.dumps(info, default=str), round(time.time() - T0, 1), "s", flush=True)
    if not ok:
        sys.exit(1)


def law_task(args):
    R, kind = args
    local = (kind, R, frozenset(), frozenset())
    every = (kind, R, frozenset(SINGLES[R]), frozenset(PAIRS[R]))
    c = collections.Counter()
    for (perm, x, b) in TL.final_letters(kind):
        v0 = TL.final_verdict(local, perm, x, b, deep=False)
        v1 = TL.final_verdict(every, perm, x, b)
        cre0, cre1 = v0 is not None and any(v0), v1 is not None and any(v1)
        role = TL.role(kind, x, b)
        c["last atoms"] += 1
        c["creation unchanged by every deeper relation"] += cre0 == cre1
        c["... far sides added at a line already receiving"] += cre0 and cre1 and v0 != v1
        c["the native statement holds"] += cre0 == PL.native(kind, R, perm, x, b)
        if R == 255:
            c["free ports: the touching rule holds"] += cre0 == TL.touching(kind, x, b)
        c[("table", PL.name(R), role, "receives" if cre0 else "silent")] += 1
    return c


if __name__ == "__main__":
    manifest = json.loads((HERE / "manifest.json").read_text())
    bad = {q: dg for q, dg in manifest["parent_bindings"].items() if hashlib.sha256((ROOT / q).read_bytes()).hexdigest() != dg}
    status = {q: json.loads((ROOT / q).read_text()).get("status") for q in manifest["parent_bindings"]
              if q.endswith(("manifest.json", "result.json")) and q.startswith("proofs/")}
    check("0 dependency artifacts bound by hash; upstream proofs Proved", not bad and all(s in ("Proved", "passed") for s in status.values()),
          {"mismatched": bad, "statuses": status})

    with Pool(22) as pool:
        # 1-3
        c = collections.Counter()
        for r in pool.imap_unordered(law_task, [(R, kind) for R in PL.PORT_RELATIONS for kind in ("line", "point")], chunksize=1):
            c.update(r)
        n = c["last atoms"]
        check("1 deeper points never decide: for every port relation (15) and every closed last atom (its lost element, port permutation "
              "and line), creation with every compatible deeper relation at once equals creation from the atom alone; deeper relations "
              "only add far sides at lines already receiving",
              n == c["creation unchanged by every deeper relation"] > 0,
              {"last atoms": n, "unchanged": c["creation unchanged by every deeper relation"],
               "far sides added": c["... far sides added at a line already receiving"],
               "singles per port relation": sorted(len(SINGLES[R]) for R in PL.PORT_RELATIONS),
               "pairs per port relation": sorted(len(PAIRS[R]) for R in PL.PORT_RELATIONS)})
        table = {"%s; %s" % (k[1], k[2]): {} for k in c if isinstance(k, tuple)}
        for k, v in c.items():
            if isinstance(k, tuple):
                table["%s; %s" % (k[1], k[2])][k[3]] = v
        check("2 the native statement: an emitting atom's lines receive exactly when the removal's side allows its three ports to be equal; "
              "a receiving atom's cut line receives exactly when the side does not force the other two ports equal, and its intact line "
              "exactly when the side tells the ports apart (its relation is not invariant under permuting them)",
              n == c["the native statement holds"], {"holds": c["the native statement holds"], "table": dict(sorted(table.items()))})
        check("3 free ports give the touching rule", c["free ports: the touching rule holds"] == 546,
              {"letters with free ports": c["free ports: the touching rule holds"]})

        # 4
        spaces = RD.census_spaces()
        tasks = [(i, M) for i, (nm, S) in enumerate(spaces) for M in range(len(S.H))]
        exact = [dict() for _ in spaces]
        for (i, M), (M_, row, ns) in zip(tasks, pool.imap(TR.exact_row, [(spaces[i][1], M) for i, M in tasks], chunksize=1)):
            exact[i][M] = row
        c4 = collections.Counter()
        for r in pool.starmap(PL.side_test, [(S, ex) for (nm, S), ex in zip(spaces, exact)]):
            c4.update(r)
        rows = collections.defaultdict(dict)
        for (tag, what), v in c4.items():
            rows[tag][what] = v
        check("4 computed, on BRACE-TREE C's 111 fresh spaces (exact creation maps): for every removal anywhere and every line of a Fano "
              "atom not holding it, replacing the removal's side of the facing cut by the relation it shows on the shared points leaves "
              "creation unchanged",
              all(v["pairs"] == v["creation unchanged"] for v in rows.values()) and len(rows) > 0, dict(sorted(rows.items())))

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
