#!/usr/bin/env python3
"""Checks for HANDLE-EMERGENCE-20261102-001B: how a handle creates.

    python3 -B check.py          verify result.json against a fresh run
    python3 -B check.py --write  write result.json from a fresh run
Run with the repository's .venv (numpy, networkx). About three minutes."""
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


def pair_of(t):
    return frozenset([t, tuple(1 - b for b in t)])


def odd_port(t, sigma, X):
    """the port where the pattern t departs from the excluded all-equal pair {sigma, not sigma}"""
    d = [i for i in range(3) if t[i] != sigma[i]]
    if len(d) == 2:
        d = [i for i in range(3) if t[i] == sigma[i]]
    return X[d[0]]


ROWS = []
for i1, i2 in itertools.product(sorted(SP), repeat=2):
    H1, s1, n1 = SP[i1]
    H2, s2, n2 = SP[i2]
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
            I = sorted({tuple(int(b) for b in r) for r in A[:, X]})
            cs = E.circuits(S, n)
            ties = [m for m in cs if bin(m).count("1") == 2]
            rep = E.tie_classes(n, ties)
            knots = [m for m in cs if bin(m).count("1") >= 3]
            can = {m: E.canon(m, rep) for m in knots}
            allk = set(can.values())
            cross = {m: bool(m & inner and m & outer) for m in knots}
            base = {can[m] for m in knots if not cross[m]}
            gen = E.closure(allk, base, n)
            three = {c for c in allk if bin(c).count("1") == 3}
            gen3 = E.closure(three, base & three, n)
            new = [m for m in knots if cross[m] and can[m] not in gen]
            ROWS.append(dict(near=i1, far=i2, li=li, M=line, X=X, P=P, I=I, A=A, n=n, rep=rep, new=new, ports=ports,
                             line_meets=sorted(set(line) & set(H1[li])), local_ok=(gen & three) == gen3,
                             planar=PL.incidence_planar(H1), crossing=sum(cross.values())))
print("    computed %d removals" % len(ROWS), round(time.time() - T0, 1), "s", flush=True)

# ------------------------------------------------------------------------------------------------ 1. the shape of new knots
shape = collections.Counter()
ok1 = True
for r in ROWS:
    hub = r["rep"][r["M"][0]]
    for m in r["new"]:
        pts = E.bits(m)
        hubpts = [v for v in pts if r["rep"][v] == hub]
        near = [v for v in pts if v in r["P"] and r["rep"][v] != hub]
        far = [v for v in pts if v not in r["P"]]
        good = len(pts) == 3 and len(hubpts) == 1 and len(near) == 1 and len(far) == 1 and near[0] not in r["ports"]
        ok1 &= good
        shape["new knots"] += 1
        shape["of three points: one in the removed line's tie class, one near point off the ports, one far point"] += good
total_new = shape["new knots"]
check("1 every new knot at a single opened cut, over all ordered pairs of census spaces (lines 0 and 1 of the first spliced into point 0 "
      "of the second), has three points: one in the removed line's tie class (the hub), one near point off the ports, one far point",
      ok1 and total_new > 0, dict(shape))

# ------------------------------------------------------------------------------------------------ 2. generation of three-point knots is local
loc = collections.Counter(r["local_ok"] for r in ROWS)
check("2 the size lemma's consequence: at every removal, the three-point knots generated by eliminations among all knots are exactly "
      "those generated using three-point knots alone (a derivation never grows, so a three-point knot is decided inside its four-point "
      "extensions)", loc[False] == 0 and loc[True] == len(ROWS), {"removals where the two agree": loc[True], "removals": len(ROWS)})

# ------------------------------------------------------------------------------------------------ 3. pin and separate
info3 = collections.Counter()
ok3 = True
for r in ROWS:
    A, X = r["A"], r["X"]
    hub = r["rep"][r["M"][0]]
    for m in r["new"]:
        pts = E.bits(m)
        h = next(v for v in pts if r["rep"][v] == hub)
        a = next(v for v in pts if v in r["P"] and r["rep"][v] != hub)
        c = next(v for v in pts if v not in r["P"])
        pinned = None
        for hv, av in itertools.product((0, 1), repeat=2):
            T = {tuple(int(b) for b in row) for row in A[(A[:, h] == hv) & (A[:, a] == av)][:, X]}
            Tc = {tuple(int(b) for b in row) for row in A[(A[:, h] == 1 - hv) & (A[:, a] == 1 - av)][:, X]}
            if len(T) == 1 and Tc == {tuple(1 - b for b in next(iter(T)))}:
                pinned = next(iter(T))
        sep = pinned is not None and any(
            pinned not in {tuple(int(b) for b in row) for row in A[A[:, c] == cv][:, X]} and
            tuple(1 - b for b in pinned) not in {tuple(int(b) for b in row) for row in A[A[:, c] == 1 - cv][:, X]} for cv in (0, 1))
        ok3 &= sep
        info3["new knots"] += 1
        info3["hub and near point pin one pattern (its complement for the complementary values); the far point separates the pair"] += sep
check("3 pin and separate: for every new knot {h, a, c}, the hub point h and the near point a pin the ports to one pattern t (and to its "
      "complement when both values flip), and each value of the far point c excludes one pattern of the pair {t, not t}",
      ok3 and info3["new knots"] == total_new, dict(info3))

# ------------------------------------------------------------------------------------------------ 4. necessary, not sufficient
info4 = collections.Counter()
for r in ROWS:
    if len(r["I"]) != 6:
        info4["removals with %d port patterns" % len(r["I"])] += 1
        info4["removals with %d port patterns and new knots" % len(r["I"])] += bool(r["new"])
        continue
    A, X = r["A"], r["X"]
    h = r["M"][0]
    pinned, separated = set(), set()
    for a in sorted(r["P"] - r["ports"] - set(r["M"])):
        for hv, av in itertools.product((0, 1), repeat=2):
            T = {tuple(int(b) for b in row) for row in A[(A[:, h] == hv) & (A[:, a] == av)][:, X]}
            if len(T) == 1:
                pinned.add(pair_of(next(iter(T))))
    for c in sorted(set(range(r["n"])) - r["P"]):
        T0c = {tuple(int(b) for b in row) for row in A[A[:, c] == 0][:, X]}
        for t in r["I"]:
            if t not in T0c:
                separated.add(pair_of(t))
    meet = bool(pinned & separated)
    info4["six-pattern removals, %s, %s" % ("a pinned pair is separated" if meet else "no pinned pair separated",
                                            "with new knots" if r["new"] else "none new")] += 1
check("4 over every removal of the census pairs: new knots need a six-pattern interface and a complementary pair that the hub and one "
      "near point pin and one far point separates; that is not sufficient",
      info4["six-pattern removals, no pinned pair separated, with new knots"] == 0 and
      all(v == 0 for k, v in info4.items() if k.startswith("removals with") and k.endswith("and new knots")) and
      info4["six-pattern removals, a pinned pair is separated, none new"] > 0 and
      info4["six-pattern removals, a pinned pair is separated, with new knots"] > 0, dict(info4))

# ------------------------------------------------------------------------------------------------ 5. how the Fano plane creates
info5 = collections.Counter()
ok5 = True
for r in ROWS:
    if r["near"] not in (21, 58) or len(r["I"]) != 6:
        continue
    A, X = r["A"], r["X"]
    h = r["M"][0]
    tied = [p for p in X if len({(int(row[h]), int(row[p])) for row in A}) == 2]
    sigma = next(t for t in itertools.product((0, 1), repeat=3) if t not in r["I"])
    odd = set()
    for a in sorted(r["P"] - r["ports"] - set(r["M"])):
        for hv, av in itertools.product((0, 1), repeat=2):
            T = {tuple(int(b) for b in row) for row in A[(A[:, h] == hv) & (A[:, a] == av)][:, X]}
            if len(T) == 1:
                odd.add(odd_port(next(iter(T)), sigma, X))
    name = "Fano" if r["near"] == 21 else "census 58"
    meets = len(r["line_meets"])
    info5["%s: removed line meets the closing line in %d, hub tied to %d port(s)" % (name, meets, len(tied))] += 1
    if r["near"] == 21:
        ok5 &= meets == 1 and tied == r["line_meets"] and odd == set(r["line_meets"])
    info5["%s: pinned pairs' odd ports %s" % (name, "= the hub's port" if odd and odd <= set(tied) else
                                              ("off the hub" if odd else "none pinned"))] += 1
    info5["%s: removals with new knots" % name] += bool(r["new"])
fano_total = sum(v for k, v in info5.items() if k.startswith("Fano: removed line"))
check("5 how the Fano plane creates: on a Fano removed side every six-pattern removal has its line meet the closing line in one port, the "
      "hub tied to that port, and every pinned pair's odd port equal to it; census 58 creates also with the line missing the closing line "
      "and the hub tied to no port", ok5 and fano_total > 0, dict(info5))

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
