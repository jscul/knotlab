#!/usr/bin/env python3
"""Checks for PLANAR-THEOREM-20261102-001B: crossing knots separated by one port are 2-sums.

    python3 -B check.py          verify result.json against a fresh run
    python3 -B check.py --write  write result.json from a fresh run
Run with the repository's .venv (numpy). About three minutes."""
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
sys.path.insert(0, str(ROOT / "proofs/HANDLE-EMERGENCE-20261102-001A/HANDLE-EMERGENCE-20261102-001A-P001_a_planar_removed_side_creates_nothing"))
sys.path.insert(0, str(ROOT / "proofs/SPLICE-TREE-20261102-001C/SPLICE-TREE-20261102-001C-P001_opened_cuts_interact"))
import planar_lib as PL  # noqa: E402
import elim_lib as E  # noqa: E402

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
NEAR = [("census %d" % i,) + SP[i] for i in (6, 14, 38, 45, 21, 58)]
for seed in (0, 1):
    NEAR.append(("grown 10 points, seed %d" % seed,) + PL.to_space(PL.grow(10, seed)))
FAR = [SP[i] for i in (1, 6, 21, 58)]

info = collections.Counter()
ok = True
for name, H1, s1, n1 in NEAR:
    kind = "plane" if PL.incidence_planar(H1) else "non-planar"
    for H2, s2, n2 in FAR:
        for li in (0, 1):
            ls, ss, n, side, ports = G.splice(H1, s1, n1, li, H2, s2, n2, 0)
            X = sorted(ports)
            P = {v for v in range(n) if side[v] == 0}
            inner = sum(1 << v for v in P - ports)
            outer = sum(1 << v for v in range(n) if v not in P)
            for M, line in enumerate(ls):
                if not set(line) <= P:
                    continue
                S = G.removal(ls, ss, n, M)
                A = np.array(S, dtype=np.int8)
                patterns = len({tuple(int(b) for b in r) for r in A[:, X]})
                cs = E.circuits(S, n)
                rep = E.tie_classes(n, [m for m in cs if bin(m).count("1") == 2])
                circ = {E.canon(m, rep) for m in cs}
                knots = [m for m in cs if bin(m).count("1") >= 3]

                def T(Y, y):
                    msk = np.all(A[:, Y] == y, axis=1)
                    return {tuple(int(b) for b in r) for r in A[msk][:, X]}
                for m in knots:
                    if not (m & inner and m & outer):
                        continue
                    pts = E.bits(m)
                    U = [v for v in pts if v in P]
                    V = [v for v in pts if v not in P]
                    seps = set()
                    for u in itertools.product((0, 1), repeat=len(U)):
                        Tu = T(U, u)
                        for v in itertools.product((0, 1), repeat=len(V)):
                            Tv = T(V, v)
                            if Tu & Tv:
                                continue
                            for j in range(3):
                                a, b = {t[j] for t in Tu}, {t[j] for t in Tv}
                                if len(a) == 1 and len(b) == 1 and a != b:
                                    seps.add(X[j])
                    if not seps:
                        continue
                    info["%s near sides: separated crossing knots" % kind] += 1
                    info["at %d-pattern removals" % patterns] += 1
                    outside = all(y not in pts for y in seps)
                    good = outside
                    Kc = E.canon(m, rep)
                    kinds = set()
                    for y in seps:
                        K1 = E.canon(sum(1 << q for q in U) | (1 << y), rep)
                        K2 = E.canon(sum(1 << q for q in V) | (1 << y), rep)
                        raw1, raw2 = len(U) + 1, len(V) + 1
                        tie1 = bin(K1).count("1") < raw1        # y tied to the near point (then U is one point)
                        tie2 = bin(K2).count("1") < raw2        # y tied to the far point (then V is one point)
                        if tie1 or tie2:
                            other = K2 if tie1 else K1
                            fine = (len(U) == 1 if tie1 else len(V) == 1) and other in circ and other == Kc
                            kinds.add("tie")
                        else:
                            fine = K1 in circ and K2 in circ and E.canon((K1 | K2) & ~(1 << rep[y]), rep) == Kc
                            kinds.add("2-sum")
                        good &= fine
                    ok &= good
                    info["%s near sides: separated crossing knots accounted for" % kind] += good
                    label = ("a class-level 2-sum through a separating port" if "2-sum" in kinds else
                             "only degenerate (every separating port tied to the knot's lone point on one side)")
                    info["%s near sides, %d-pattern removals: %s" % (kind, patterns, label)] += 1
check("1 on splices of six near sides (four plane, two non-planar) and two 10-point plane near sides into K4^(3), census 6, the Fano plane "
      "and census 58 (lines 0 and 1, every removal on the near side), every crossing knot one of whose excluded patterns is separated by a "
      "single port y has y outside the knot, and its near part with y and its far part with y are circuits: eliminating y from them "
      "gives the knot, or (degenerate) one of them is a tie and the knot is tie-equivalent to the other, a one-sided circuit", ok and sum(v for k, v in info.items() if k.endswith("separated crossing knots")) > 0, dict(info))

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
