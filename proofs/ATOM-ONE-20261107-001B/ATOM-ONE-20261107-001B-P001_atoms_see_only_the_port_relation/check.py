#!/usr/bin/env python3
"""Checks for ATOM-ONE-20261107-001B: atoms see only the port relation.

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
import bound_lib as BL  # noqa: E402

PL, TL = BL.PL, BL.TL
T0 = time.time()
OUT = {}
SIX = {"000/001/010/101/110/111", "000/001/011/100/110/111", "000/010/011/100/101/111", "001/010/101/110", "001/011/100/110",
       "010/011/100/101"}


def check(name, ok, info):
    OUT[name] = {"pass": bool(ok), "info": info}
    print("PASS" if ok else "FAIL", name, json.dumps(info, default=str), round(time.time() - T0, 1), "s", flush=True)
    if not ok:
        sys.exit(1)


def task2(args):
    kind, perm, x, b, R = args
    return args, BL.case(kind, perm, x, b, R)


def task3(args):
    kind, perm, x, b, R = args
    return args, BL.case(kind, perm, x, b, R, behind_alone=True)


def cre(v):
    return v is not None and any(v)


if __name__ == "__main__":
    manifest = json.loads((HERE / "manifest.json").read_text())
    bad = {q: dg for q, dg in manifest["parent_bindings"].items() if hashlib.sha256((ROOT / q).read_bytes()).hexdigest() != dg}
    status = {q: json.loads((ROOT / q).read_text()).get("status") for q in manifest["parent_bindings"]
              if q.endswith(("manifest.json", "result.json")) and q.startswith("proofs/")}
    check("0 dependency artifacts bound by hash; upstream proofs Proved", not bad and all(s in ("Proved", "passed") for s in status.values()),
          {"mismatched": bad, "statuses": status})

    # 1
    pf = BL.passes_free()
    c1 = collections.Counter("opened %s, other element a %s: %s" % ("line" if D[0] == "L" else "point", "line" if X0[0] == "L" else "point",
                                                                    "free" if got == full else "constrained") for X0, D, got, full in pf)
    check("1 a free relation passes through a closed Fano atom: with any one element opened (a line removed, or a point split into free "
          "copies), every other element's three variables are free", len(pf) == 182 and all(got == full for X0, D, got, full in pf),
          dict(sorted(c1.items())))

    tasks = [(kind, perm, x, b, R) for kind, perm, x, b in BL.letters() for R in PL.PORT_RELATIONS]
    with Pool(22) as pool:
        # 2
        c2 = collections.Counter()
        for (kind, perm, x, b, R), res in pool.imap_unordered(task2, tasks, chunksize=4):
            if res is None:
                c2["degenerate: b shows fewer than six patterns"] += 1
                continue
            v0, v1, v2 = res
            c2["cases"] += 1
            c2["creation unchanged by every deep relation of the removal's side and every mixed pair"] += cre(v2) == cre(v0)
            c2["mixed pairs add no far side beyond GLUE-READ A's bound"] += v2 == v1
            if v2 != v0:
                where = "receiver's cut line, R among the six" if (TL.role(kind, x, b) == "cut line" and PL.name(R) in SIX) else "ELSEWHERE"
                c2["far sides added: " + where] += 1
                c2["far sides added, R = %s" % PL.name(R)] += 1
        check("2 the bound with every deep point of the removal's side, alone or paired with any deep point behind another element, for "
              "every port relation, closed atom and line (all 8,190 letters): creation is B's own; far sides change only at a receiving "
              "atom's cut lines when R is one of six relations, exactly as in GLUE-READ A's bound",
              c2["cases"] == c2["creation unchanged by every deep relation of the removal's side and every mixed pair"]
              == c2["mixed pairs add no far side beyond GLUE-READ A's bound"] and c2["far sides added: ELSEWHERE"] == 0,
              dict(sorted(c2.items())))

        # 3
        c3 = collections.Counter()
        tasks3 = [t for t in tasks if tuple(t[1]) == (0, 1, 2)]
        for (kind, perm, x, b, R), res in pool.imap_unordered(task3, tasks3, chunksize=2):
            if res is None:
                continue
            v0, v1, v2, v3 = res
            c3["cases (one slot order)"] += 1
            if cre(v3) != cre(v0):
                c3["creation changed by deep points behind B's other elements: R = %s, %s" % (PL.name(R), TL.role(kind, x, b))] += 1
            if v3 != v0:
                c3["far sides changed by deep points behind B's other elements"] += 1
        check("3 deep points behind B's other elements, with every relation their sides' exact relations allow, can add creation (at intact "
              "lines with a free or not-all-equal port relation): the closed atom's verdict is not forced by bounding them, though these "
              "points do not depend on which line of the facing atom was removed",
              any(k.startswith("creation changed") for k in c3), dict(sorted(c3.items())))

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
