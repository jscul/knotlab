#!/usr/bin/env python3
"""Checks for HALO-FORCING-20261103-001A: the route criterion.

    python3 -B check.py          verify result.json against a fresh run
    python3 -B check.py --write  write result.json from a fresh run
Run with the repository's .venv (numpy, networkx). About two minutes."""
import collections
import hashlib
import itertools
import json
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "proofs/HANDLE-EMERGENCE-20261102-001A/HANDLE-EMERGENCE-20261102-001A-P001_a_planar_removed_side_creates_nothing"))
sys.path.insert(0, str(ROOT / "proofs/SPLICE-TREE-20261102-001C/SPLICE-TREE-20261102-001C-P001_opened_cuts_interact"))
sys.path.insert(0, str(ROOT / "proofs/HANDLE-LOCALITY-20261103-001B/HANDLE-LOCALITY-20261103-001B-P001_where_creation_happens"))
import planar_lib as PL  # noqa: E402
import elim_lib as E  # noqa: E402
import join_lib as J  # noqa: E402
import route_lib as RL  # noqa: E402

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

src = (ROOT / "proofs/PLANAR-COMPOSE-20261102-001A/PLANAR-COMPOSE-20261102-001A-P001_the_hub_reaches_the_ports_on_a_plane_side/check.py").read_text()
exec(src[src.index("def tied_to("):src.index("def odd_index(")])
SP = {idx: (H, s, n) for idx, n, H, s in G.census_spaces(ROOT)}
FARS = [("K4^(3)", SP[1]), ("census 6", SP[6]), ("the Fano plane", SP[21]), ("census 58", SP[58])]


def lab(space, name):
    H, s, n = space
    return (H, s, n, [name] * len(H), [name] * n)


# ------------------------------------------------------------------------------------------------ 1. the criterion, knot by knot
info1 = collections.Counter()
ok1 = True
transfer = collections.defaultdict(set)
for size, seed in ((10, 0), (10, 1), (12, 0), (12, 1), (14, 0)):
    Hp = lab(PL.to_space(PL.grow(size, seed)), "plane")
    S = J.splice_pieces(G, lab(SP[21], "handle"), Hp, 0, 0)
    HS, sS, nS, llab, plab = S
    ports = list(SP[21][0][0])
    hpts = [q for q in range(nS) if plab[q] == "handle" and q not in ports]
    plines = [k for k in range(len(HS)) if llab[k] == "plane"]
    for M in range(len(HS)):
        if llab[M] == "plane":
            continue
        AN = np.array(G.removal(HS, sS, nS, M), dtype=np.int8)
        tie = {p: tied_to(AN, p, nS) for p in range(nS)}  # noqa: F821
        for L in plines:
            X = list(HS[L])
            I = {tuple(int(b) for b in r) for r in AN[:, X]}
            if len(I) != 6:
                continue
            R = frozenset((tuple(int(v) for v in r[ports]), tuple(int(v) for v in r[X])) for r in AN)
            for fname, F in FARS:
                newraw, rep, far, AF = J.new_knots(E, G, AN, HS, sS, nS, L, F, 3)
                newset = {frozenset(E.bits(m)) for m in newraw}
                TF = {(c, g): {tuple(int(v) for v in r[len(far):]) for r in AF[AF[:, far.index(c)] == g]} for c in far for g in (0, 1)}
                noroute = set()
                for r_ in hpts:
                    for o in range(nS):
                        if o == r_ or o in tie[r_] or (o in hpts and o < r_):
                            continue
                        for rv, ov in itertools.product((0, 1), repeat=2):
                            rows = AN[(AN[:, r_] == rv) & (AN[:, o] == ov)]
                            if len(rows) == 0:
                                continue
                            Tset = {tuple(int(v) for v in r[X]) for r in rows}
                            Tr = {tuple(int(v) for v in r[X]) for r in AN[AN[:, r_] == rv]}
                            To = {tuple(int(v) for v in r[X]) for r in AN[AN[:, o] == ov]}
                            for c in far:
                                if any(rep[c] == rep[q] for q in range(nS)):
                                    continue
                                for g in (0, 1):
                                    if Tset & TF[(c, g)] or not (Tr & TF[(c, g)]) or not (To & TF[(c, g)]):
                                        continue
                                    K = frozenset((r_, o, c))
                                    how = RL.route(AN, tie, X, I, Tset, I - TF[(c, g)], [(r_, rv), (o, ov)])
                                    kind = "both near points in the handle" if o in hpts else (
                                        "one near point on the gluing line" if o in X else "one near point elsewhere")
                                    info1["candidates, %s: %s, %s" % (kind, "route " + how if how else "no route",
                                                                       "new" if K in newset else "not new")] += 1
                                    if how is None:
                                        noroute.add(K)
                                    else:
                                        ok1 &= K not in newset
                ok1 &= newset == noroute
                info1["cases (removal, gluing line, far side): %s" % ("create" if newset else "no new knot")] += 1
                info1["new knots"] += len(newset)
                transfer[(M, fname, R)].add(bool(newset))
check("1 the route criterion, knot by knot: on the Fano plane attached at a point of five grown plane pieces (10 to 14 points), at every "
      "removal inside the handle, every six-pattern plane gluing line and four far sides, the new crossing knots (exact up to three points) "
      "are exactly the three-point candidates with a handle point and no route", ok1 and info1["new knots"] > 0, dict(info1))
multi = collections.Counter()
for k, v in transfer.items():
    multi["transfer classes with a single outcome" if len(v) == 1 else "transfer classes with MIXED outcomes"] += 1
check("2 the transfer lemma's consequence: creation is a function of (removal, far side, the plane piece's transfer between ports and gluing "
      "line)", all(len(v) == 1 for v in transfer.values()), dict(multi, classes=len(transfer)))

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
