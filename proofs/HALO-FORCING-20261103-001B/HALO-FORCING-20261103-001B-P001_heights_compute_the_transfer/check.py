#!/usr/bin/env python3
"""Checks for HALO-FORCING-20261103-001B: heights compute the transfer.

    python3 -B check.py          verify result.json against a fresh run
    python3 -B check.py --write  write result.json from a fresh run
Run with the repository's .venv (numpy, networkx). About five minutes."""
import collections
import hashlib
import itertools
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "proofs/HANDLE-EMERGENCE-20261102-001A/HANDLE-EMERGENCE-20261102-001A-P001_a_planar_removed_side_creates_nothing"))
import planar_lib as PL  # noqa: E402
import transfer_lib as TL  # noqa: E402

G = PL.G
T0 = time.time()
OUT = {}


def check(name, ok, info):
    OUT[name] = {"pass": bool(ok), "info": info}
    print("PASS" if ok else "FAIL", name, json.dumps(info, default=str)[:900], round(time.time() - T0, 1), "s", flush=True)
    if not ok:
        print(json.dumps(info, default=str, indent=1))
        sys.exit(1)


# ------------------------------------------------------------------------------------------------ 0. bindings
manifest = json.loads((HERE / "manifest.json").read_text())
bad = {p: d for p, d in manifest["parent_bindings"].items() if hashlib.sha256((ROOT / p).read_bytes()).hexdigest() != d}
status = {p: json.loads((ROOT / p).read_text()).get("status") for p in manifest["parent_bindings"]
          if p.endswith(".json") and p.startswith("proofs/")}
check("0 dependency artifacts bound by hash; upstream proofs Proved", not bad and all(s in ("Proved", "passed") for s in status.values()),
      {"mismatched": bad, "statuses": status})

SP = {idx: (H, s, n) for idx, n, H, s in G.census_spaces(ROOT)}
SPACES = [("census %d" % i,) + SP[i] for i in sorted(SP) if PL.incidence_planar(SP[i][0])]
for size, seed in ((10, 0), (10, 1), (12, 0), (12, 1), (14, 0)):
    SPACES.append(("grown %d points, seed %d" % (size, seed),) + PL.to_space(PL.grow(size, seed)))
for k in (5, 6):
    SPACES.append(("prism over a %d-cycle" % (2 * k),) + PL.to_space(PL.prism(k)))


def enumerate_split(Q, n, z, s):
    pts = sorted(set(range(n + 3)) - {z})
    idx = {p: i for i, p in enumerate(pts)}
    A = G.states(len(pts))[G.sat_matrix([tuple(idx[q] for q in L) for L in Q.lines], [list(x) for x in s], len(pts)).all(axis=1)]
    return A, idx, pts


# ------------------------------------------------------------------------------------------------ 1. corner matchings are the solutions
info1 = collections.Counter()
ok1 = True
for name, H, s, n in SPACES:
    if n > 10:
        continue
    for z in range(n):
        Q = TL.Split(H, [list(x) for x in s], n, z)
        A, idx, pts = enumerate_split(Q, n, z, s)
        sols = {tuple(int(r[idx[q]]) for q in pts) for r in A}
        opts = [[i for i, e in enumerate(Q.edges) if e[0] == k] for k in range(len(Q.lines))]
        got = set()
        count = 0
        for choice in itertools.product(*opts):
            if len({Q.edges[i][1] for i in choice}) != len(choice):
                continue
            count += 1
            v = Q.solution_of(dict(enumerate(choice)))
            vec = tuple(v[q] for q in pts)
            got.add(vec)
            got.add(tuple(1 - b for b in vec))
        good = got == sols and 2 * count == len(sols)
        ok1 &= good
        info1["point splits"] += 1
        info1["point splits whose corner matchings are exactly the solutions up to complement"] += good
        info1["lines with two corners in one face (double edges)"] += sum(1 for k in range(len(Q.lines))
                                                                          if len({Q.edges[i][1] for i in opts[k]}) < 3)
check("1 corner matchings: on every point split of the planar census spaces and of the 10-point grown and prism spaces, choosing for each "
      "line one corner, with each face receiving exactly one, gives a bijection with the solutions up to complement (the three port "
      "lines have two corners in the merged face, so the line-face graph has double edges)", ok1 and info1["point splits"] > 0, dict(info1))

# ------------------------------------------------------------------------------------------------ 2. heights decide the transfer
info2 = collections.Counter()
ok2 = True
for name, H, s, n in SPACES:
    for z in range(n):
        Q = TL.Split(H, [list(x) for x in s], n, z)
        A, idx, pts = enumerate_split(Q, n, z, s)
        for L in range(len(Q.lines)):
            X = list(Q.lines[L])
            enum = {(tuple(int(r[idx[y]]) for y in Q.ports), tuple(int(r[idx[q]]) for q in X)) for r in A}
            ht = Q.transfer(L)
            ok2 &= enum == ht
            info2["(split, line) pairs"] += 1
            info2["transfer by heights equal to enumeration"] += enum == ht
            info2["transfer size %d" % len(ht)] += 1
check("2 heights decide the transfer: on every point split of the planar census, five grown and two prism spaces (to 14 points), for every "
      "line, the pairs (port pattern, line pattern) found by shortest paths and parity halving equal those of the enumerated solutions",
      ok2 and info2["(split, line) pairs"] > 0, dict(info2))

OUT["seconds"] = round(time.time() - T0, 1)
print("ALL OK", OUT["seconds"], "s")
result = {"schema_version": 3, "artifact_id": manifest["artifact_id"], "kind": "proof", "ticket": manifest["ticket"], "proof": manifest["proof"],
          "status": "passed", "claim": manifest["claim"], "checks": {k: v for k, v in OUT.items() if k != "seconds"}}
text = json.dumps(result, indent=1, sort_keys=True, default=str) + "\n"
if "--write" in sys.argv:
    (HERE / "result.json").write_text(text)
elif not (HERE / "result.json").exists() or json.loads((HERE / "result.json").read_text()) != json.loads(text):
    print("result.json does not match a fresh run; rerun with --write after review")
    sys.exit(1)
