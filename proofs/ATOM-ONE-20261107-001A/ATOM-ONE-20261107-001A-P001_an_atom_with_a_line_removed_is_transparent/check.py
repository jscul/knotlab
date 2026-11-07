#!/usr/bin/env python3
"""Checks for ATOM-ONE-20261107-001A: a Fano atom with a line removed is transparent.

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
import atom_lib as AL  # noqa: E402

FL = AL.load("ao_far_lib", ROOT / "proofs/FAR-READ-20261106-001A/FAR-READ-20261106-001A-P001_the_far_side_map/far_lib.py")
PO = AL.load("ao_port_lib", ROOT / "proofs/GLUE-READ-20261106-001A/GLUE-READ-20261106-001A-P001_creation_is_decided_by_the_receiving_cut/"
             "port_lib.py")
TL = PO.TL
T0 = time.time()
OUT = {}


def check(name, ok, info):
    OUT[name] = {"pass": bool(ok), "info": info}
    print("PASS" if ok else "FAIL", name, json.dumps(info, default=str), round(time.time() - T0, 1), "s", flush=True)
    if not ok:
        sys.exit(1)


def config_task(X):
    nl = sum(1 for v in X if v[0] == "L")
    return nl, AL.invariant_for_every_relation(X)


def space_task(i):
    spaces, maps = FL.saved()
    return AL.real_space_report(spaces[i][2], PO, TL)


if __name__ == "__main__":
    manifest = json.loads((HERE / "manifest.json").read_text())
    bad = {q: dg for q, dg in manifest["parent_bindings"].items() if hashlib.sha256((ROOT / q).read_bytes()).hexdigest() != dg}
    status = {q: json.loads((ROOT / q).read_text()).get("status") for q in manifest["parent_bindings"]
              if q.endswith(("manifest.json", "result.json")) and q.startswith("proofs/")}
    check("0 dependency artifacts bound by hash; upstream proofs Proved", not bad and all(s in ("Proved", "passed") for s in status.values()),
          {"mismatched": bad, "statuses": status})

    # 1
    ngauge, reps, knots = AL.sign_classes()
    check("1 the signed Fano planes: up to flipping points and lines there are 256 sign classes, and exactly one has no not-all-equal "
          "colouring, the plain Fano plane", len(reps) == 256 and knots == [0],
          {"gauge group": ngauge, "sign classes": len(reps), "knot classes": len(knots), "the knot class is the plain plane": knots == [0]})

    # 2
    fr = AL.freeness("L")
    c2 = collections.Counter("other element a %s: %s" % ("point" if X0[0] == "P" else "line", "free" if got == full else "not free")
                             for X0, D, got, full in fr)
    check("2 freeness: in the Fano plane, removing any line together with any other element leaves that element's three variables free",
          len(fr) == 91 and all(got == full for X0, D, got, full in fr), {"cases": len(fr), "by the other element's kind": dict(c2)})

    with Pool(22) as pool:
        # 3
        c3 = collections.Counter()
        for nl, res in pool.imap_unordered(config_task, AL.configurations(), chunksize=1):
            tag = "%s line-type cuts" % (nl if nl < 2 else "2 or more")
            for X0, same in res.items():
                c3[(tag, "configurations x outgoing cuts")] += 1
                c3[(tag, "invariant for every relation on the other cuts")] += same
        info3 = {"%s: %s" % k: v for k, v in sorted(c3.items())}
        check("3 the knot is needed: with arbitrary relations on an atom's other cuts, the relation sent is the same whichever line is "
              "removed for every atom with at most one line-type cut, but not in general",
              all(c3[(t, "configurations x outgoing cuts")] == c3[(t, "invariant for every relation on the other cuts")]
                  for t in ("0 line-type cuts", "1 line-type cuts"))
              and c3[("2 or more line-type cuts", "invariant for every relation on the other cuts")]
              < c3[("2 or more line-type cuts", "configurations x outgoing cuts")],
              dict(info3, configurations=len(AL.configurations())))

        # 4
        spaces, maps = FL.saved()
        c4 = collections.Counter()
        for c in pool.imap_unordered(space_task, range(len(spaces)), chunksize=1):
            c4.update(c)
    sides_ok = sum(v for k, v in c4.items() if k.endswith("as the theorem says"))
    check("4 computed, on the 191 saved spaces: every closed side at a Fano atom's cut accepts one antipodal pair (a point side) or the six "
          "other patterns (a line side), and every atom with a line removed sends the free relation through each of its cuts",
          sides_ok == c4["closed sides"] and c4["... the relation sent is free"] == c4["(atom, cut, removed line)"]
          and c4["... the same relation whichever line is removed"] == c4["(atom, cut)"], dict(sorted(c4.items())))

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
