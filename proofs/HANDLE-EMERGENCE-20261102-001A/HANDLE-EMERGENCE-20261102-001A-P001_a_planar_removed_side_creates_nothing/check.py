#!/usr/bin/env python3
"""Checks for HANDLE-EMERGENCE-20261102-001A: a planar removed side creates nothing.

    python3 -B check.py          verify result.json against a fresh run
    python3 -B check.py --write  write result.json from a fresh run
Run with the repository's .venv (numpy, networkx). About ten minutes."""
import collections
import hashlib
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
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


def opened_cut(H1, s1, n1, li, H2, s2, n2):
    """splice line li of H1 into point 0 of H2; for every removal on H1's side: interface size, crossing knots, new knots"""
    ls, ss, n, side, ports = G.splice(H1, s1, n1, li, H2, s2, n2, 0)
    X = sorted(ports)
    P = {v for v in range(n) if side[v] == 0}
    inner = sum(1 << v for v in P - ports)
    outer = sum(1 << v for v in range(n) if v not in P)
    rows = []
    for M, line in enumerate(ls):
        if not set(line) <= P:
            continue
        S = G.removal(ls, ss, n, M)
        pats = len({tuple(t[p] for p in X) for t in S})
        cs = E.circuits(S, n)
        rep = E.tie_classes(n, [m for m in cs if bin(m).count("1") == 2])
        knots = [m for m in cs if bin(m).count("1") >= 3]
        can = {m: E.canon(m, rep) for m in knots}
        cross = {m: bool(m & inner and m & outer) for m in knots}
        gen = E.closure(set(can.values()), {can[m] for m in knots if not cross[m]}, n)
        rows.append((pats, sum(cross.values()), sum(1 for m in knots if cross[m] and can[m] not in gen)))
    return n, rows


FOUR = collections.Counter()


def tally(rows, planar):
    t = collections.Counter()
    for pats, crossing, new in rows:
        t["removals"] += 1
        t["interface of %d patterns" % pats] += 1
        t["crossing knots"] += crossing
        t["new knots"] += new
        t["removals with new knots"] += new > 0
        FOUR[("planar" if planar else "non-planar", "%d patterns" % pats, "removals")] += 1
        FOUR[("planar" if planar else "non-planar", "%d patterns" % pats, "removals with new knots")] += new > 0
    return t


# ------------------------------------------------------------------------------------------------ 1. the planar spaces
SP = {idx: (H, s, n) for idx, n, H, s in G.census_spaces(ROOT)}
NEAR = []
for size, seeds in ((10, range(3)), (12, range(3)), (14, range(2))):
    for seed in seeds:
        g = PL.grow(size, seed)
        for swap in (False, True):
            NEAR.append(("grown %d points, seed %d%s" % (size, seed, ", dual reading" if swap else ""), PL.to_space(g, swap)))
for k in (5, 6, 7):
    for swap in (False, True):
        NEAR.append(("prism over a %d-cycle%s" % (2 * k, ", dual reading" if swap else ""), PL.to_space(PL.prism(k), swap)))
for swap in (False, True):
    NEAR.append(("truncated octahedron%s" % (", dual reading" if swap else ""), PL.to_space(PL.permutohedron(), swap)))
info1, ok1 = {}, True
for name, sp in NEAR:
    good = sp is not None and PL.incidence_planar(sp[0]) and all(len(L) == 3 for L in sp[0]) and \
        all(sum(p in L for L in sp[0]) == 3 for p in range(sp[2])) and G.fails_globally(*sp)
    ok1 &= good
    info1[name] = {"points": sp[2] if sp else None, "plane cubic triple system on which the knot fails": good}
check("1 the planar spaces beyond the census: grown from the cube by ladder moves (10, 12 and 14 points, both readings), prisms over "
      "10-, 12- and 14-cycles and the truncated octahedron; each is a cubic triple system with a plane incidence graph, and with its "
      "Kasteleyn signs the knot fails on it (checked by enumerating every assignment)", ok1, info1)

# ------------------------------------------------------------------------------------------------ 2. the census
info2 = collections.Counter()
for (i1, (H1, s1, n1)), (i2, (H2, s2, n2)) in [((a, SP[a]), (b, SP[b])) for a in SP for b in SP]:
    pl = PL.incidence_planar(H1)
    for li in (0, 1):
        n, rows = opened_cut(H1, s1, n1, li, H2, s2, n2)
        t = tally(rows, pl)
        key = "planar removed side" if pl else "non-planar removed side"
        info2[key + ": removals"] += t["removals"]
        info2[key + ": crossing knots"] += t["crossing knots"]
        info2[key + ": new knots"] += t["new knots"]
        info2[key + ": removals with new knots"] += t["removals with new knots"]
check("2 the census: splicing every ordered pair of census knot spaces (lines 0 and 1 of the first into point 0 of the second), no "
      "removal on a planar side creates a new knot, while non-planar sides (Fano, census 58) do",
      info2["planar removed side: removals"] > 0 and info2["planar removed side: new knots"] == 0 and
      info2["non-planar removed side: new knots"] > 0, dict(info2))

# ------------------------------------------------------------------------------------------------ 3. beyond the census
FAR = {"K4^(3)": SP[1], "census 6": SP[6], "Fano": SP[21], "census 58": SP[58]}
info3, tot3 = {}, collections.Counter()
for name, (H1, s1, n1) in NEAR:
    fars = ["K4^(3)", "census 6", "Fano", "census 58"] if n1 <= 12 else ["K4^(3)", "census 6"]
    lines = (0, n1 // 2) if n1 <= 12 else (0,)
    t = collections.Counter()
    for fname in fars:
        for li in lines:
            n, rows = opened_cut(H1, s1, n1, li, *FAR[fname])
            t.update(tally(rows, True))
    info3[name] = dict(t)
    tot3.update(t)
    print("   ", name, dict(t), round(time.time() - T0, 1), "s", flush=True)
check("3 beyond the census: every planar space of check 1 spliced into K4^(3), census 6, the Fano plane and census 58 (the last two "
      "only up to 12 points), at one or two of its lines; for every removal on the planar side, every knot crossing the opened cut is "
      "generated by eliminations from knots on one side",
      tot3["removals"] > 0 and tot3["new knots"] == 0 and tot3["interface of 6 patterns"] > 0,
      {"totals": dict(tot3), "per space": info3})

# ------------------------------------------------------------------------------------------------ 4. interfaces
four = {"%s, %s: %s" % k: v for k, v in sorted(FOUR.items())}
check("4 over checks 2 and 3: no removal with a four-pattern interface creates a new knot, on planar or non-planar sides; new knots "
      "appear only with six patterns and a non-planar removed side",
      all(v == 0 for k, v in FOUR.items() if k[2] == "removals with new knots" and (k[1] != "6 patterns" or k[0] == "planar")) and
      FOUR[("non-planar", "6 patterns", "removals with new knots")] > 0 and FOUR[("planar", "4 patterns", "removals")] > 0, four)

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
