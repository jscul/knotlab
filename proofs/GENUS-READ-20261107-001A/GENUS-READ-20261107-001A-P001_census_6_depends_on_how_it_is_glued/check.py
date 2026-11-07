#!/usr/bin/env python3
"""Checks for GENUS-READ-20261107-001A: census 6 depends on how it is glued.

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
import gluing_lib as GL  # noqa: E402

TL = GL.TL
T0 = time.time()
OUT = {}
SPACES, MAPS = GL.FL.saved()
SAMPLE = list(range(0, len(SPACES), 3))          # every third saved space; every fourth removal in each


def check(name, ok, info):
    OUT[name] = {"pass": bool(ok), "info": info}
    print("PASS" if ok else "FAIL", name, json.dumps(info, default=str), round(time.time() - T0, 1), "s", flush=True)
    if not ok:
        sys.exit(1)


def space_task(i):
    src, nm, S = SPACES[i]
    ex = MAPS[i]
    c = collections.Counter()
    for a in range(0, len(S.H), 4):
        AN = TL.solutions(S.H, S.s, S.n, skip=a)
        for b in range(len(S.H)):
            if b == a:
                continue
            vs = GL.orders_verdicts(AN, S, b)
            c["stored order reproduces the stored map"] += vs[0] == ex[a].get(b)
            c["(removal, gluing line) pairs"] += 1
            if vs[0] is None:
                c["degenerate"] += 1
                continue
            c["non-degenerate"] += 1
            for f, nm_ in enumerate(("K4^(3)", "census 6", "the Fano plane", "census 58")):
                c["%s: the same at every order" % nm_] += len({v[f] for v in vs}) == 1
            c["creation: the same at every order"] += len({any(v) for v in vs}) == 1
            c["census 6 creates at %d of 6 orders" % sum(v[1] for v in vs)] += 1
    return c


if __name__ == "__main__":
    manifest = json.loads((HERE / "manifest.json").read_text())
    bad = {q: dg for q, dg in manifest["parent_bindings"].items() if hashlib.sha256((ROOT / q).read_bytes()).hexdigest() != dg}
    status = {q: json.loads((ROOT / q).read_text()).get("status") for q in manifest["parent_bindings"]
              if q.endswith(("manifest.json", "result.json")) and q.startswith("proofs/")}
    check("0 dependency artifacts bound by hash; upstream proofs Proved", not bad and all(s in ("Proved", "passed") for s in status.values()),
          {"mismatched": bad, "statuses": status})

    # 1
    rep = GL.symmetry_report()
    info1 = {name: {"points": n, "signed automorphisms": na, "point orbits": orb, "orbit of the split point": so,
                    "permutations of the split point's lines realized": acts} for name, n, na, orb, so, acts in rep}
    acts = {name: a for name, n, na, orb, so, a in rep}
    check("1 the far sides' symmetry at the split point: the stabilizer realizes all six permutations of its three lines for K4^(3), the "
          "Fano plane and census 58, and only two for census 6, which has three inequivalent gluings",
          acts == {"K4^(3)": 6, "census 6": 2, "the Fano plane": 6, "census 58": 6}, info1)

    # 2
    with Pool(22) as pool:
        c2 = collections.Counter()
        for c in pool.imap_unordered(space_task, SAMPLE, chunksize=1):
            c2.update(c)
    nd = c2["non-degenerate"]
    check("2 computed, on every third saved space and every fourth removal: the stored order reproduces the stored maps; K4^(3), the "
          "Fano plane, census 58 and creation itself are the same at every order of the gluing line's points; census 6 is not",
          c2["stored order reproduces the stored map"] == c2["(removal, gluing line) pairs"]
          and all(c2["%s: the same at every order" % f] == nd for f in ("K4^(3)", "the Fano plane", "census 58"))
          and c2["creation: the same at every order"] == nd and c2["census 6: the same at every order"] < nd,
          dict(sorted(c2.items()), spaces=len(SAMPLE)))

    # 3
    S = GL.G.GL.base(*GL.G.GL.FANO)
    c3 = collections.Counter()
    for a in range(7):
        AN = TL.solutions(S.H, S.s, S.n, skip=a)
        for b in range(7):
            if b != a:
                vs = GL.orders_verdicts(AN, S, b)
                c3["ordered pairs"] += 1
                c3["census 6 at the stored order"] += vs[0][1]
                c3["native vector %s" % (GL.native(vs),)] += 1
    check("3 the Fano plane alone: at its stored orders census 6 creates at 14 of the 42 ordered pairs (BRACE-TREE A); natively every "
          "pair is the same, census 6 creating at two of the six orders (one gluing of three)",
          c3["census 6 at the stored order"] == 14 and c3["native vector (False, 2, True, True)"] == 42, dict(c3))

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
