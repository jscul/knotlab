#!/usr/bin/env python3
"""Checks for SPLICE-TREE-20261102-001C: opened cuts interact, and no hub-level feature decides how.

    python3 -B check.py          verify result.json against a fresh run
    python3 -B check.py --write  write result.json from a fresh run
Run with the repository's .venv (numpy). About four minutes."""
import collections
import hashlib
import itertools
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "proofs/SPLICE-TREE-20261102-001A/SPLICE-TREE-20261102-001A-P001_a_removal_opens_the_cuts_that_point_away"))
sys.path.insert(0, str(HERE))
import tree_lib as T  # noqa: E402
import elim_lib as E  # noqa: E402

G = T.G
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
K4, FANO = SP[1], SP[21]
NAME = {id(K4): "K4", id(FANO): "Fano"}
CLASSES = ["generated from knots crossing none", "new at one opened cut", "carried", "joint"]


def cut_masks(cuts, n):
    return [(sum(1 << v for v in c["points"] - c["ports"]), ((1 << n) - 1) & ~sum(1 << v for v in c["points"])) for c in cuts]


def knots_of(ls, ss, n, M, bound=None):
    """the knots of the space without line M as bitmasks, their tie classes, and the set of all classes"""
    cs = E.circuits(G.removal(ls, ss, n, M), n, bound)
    rep = E.tie_classes(n, [m for m in cs if bin(m).count("1") == 2])
    knots = [m for m in cs if bin(m).count("1") >= 3]
    can = {m: E.canon(m, rep) for m in knots}
    return knots, can, set(can.values())


def classify(ls, ss, n, cuts, M):
    """each knot crossing an opened cut: (number of opened cuts it crosses, its class)"""
    opened = [c for c in cuts if set(ls[M]) <= c["points"]]
    knots, can, allk = knots_of(ls, ss, n, M)
    masks = cut_masks(opened, n)
    k_of = {m: sum(1 for inner, outer in masks if m & inner and m & outer) for m in knots}
    gen0 = E.closure(allk, {can[m] for m in knots if k_of[m] == 0}, n)
    lower = {k: E.closure(allk, {can[m] for m in knots if k_of[m] < k}, n) for k in range(2, len(opened) + 1)}
    out = {}
    for m in knots:
        k = k_of[m]
        if k == 0:
            continue
        if can[m] in gen0:
            out[m] = (k, CLASSES[0])
        elif k == 1:
            out[m] = (k, CLASSES[1])
        else:
            out[m] = (k, CLASSES[2] if can[m] in lower[k] else CLASSES[3])
    return opened, out


def shared_ports(opened):
    return set().union(*[a["ports"] & b["ports"] for a, b in itertools.combinations(opened, 2)])


# ------------------------------------------------------------------------------------------------ 1. the method
info1 = collections.Counter()
ok1 = True
for pieces, edges, bound in [([K4, FANO, K4], [(0, 0, 1, 0), (1, 3, 2, 0)], None), ([FANO, K4, FANO], [(0, 0, 1, 0), (1, 1, 2, 0)], 6)]:
    ls, ss, n, piece, cuts = T.assemble(pieces, edges)
    for M in range(len(ls)):
        S = G.removal(ls, ss, n, M)
        same = set(G.circuits(S, n, bound)) == {frozenset(E.bits(m)) for m in E.circuits(S, n, bound)}
        ok1 &= same
        info1["(a) removals where the bitmask circuits equal glue_lib.circuits"] += same
        info1["(a) removals compared"] += 1
for li in (0, 3):
    ls, ss, n, piece, cuts = T.assemble([K4, FANO, K4], [(0, 0, 1, 0), (1, li, 2, 0)])
    for M in range(len(ls)):
        opened = [c for c in cuts if set(ls[M]) <= c["points"]]
        knots, can, allk = knots_of(ls, ss, n, M)
        masks = cut_masks(opened, n)
        k_of = {m: sum(1 for inner, outer in masks if m & inner and m & outer) for m in knots}
        for k in range(1, len(opened) + 1):
            base = {can[m] for m in knots if k_of[m] < k}
            same = E.closure(allk, base, n) == E.closure_forward(allk, base)
            ok1 &= same
            info1["(b) closures where the per-target computation equals forward elimination"] += same
            info1["(b) closures compared"] += 1
ls, ss, n, piece, cuts = T.assemble([FANO, FANO, FANO], [(0, 0, 1, 0), (1, 3, 2, 3)])
for M in range(len(ls)):
    opened = [c for c in cuts if set(ls[M]) <= c["points"]]
    if len(opened) < 2:
        continue
    knots, can, allk = knots_of(ls, ss, n, M)
    masks = cut_masks(opened, n)
    k_of = {m: sum(1 for inner, outer in masks if m & inner and m & outer) for m in knots}
    small = {c for c in allk if bin(c).count("1") <= 5}
    for k in (1, 2):
        base = {can[m] for m in knots if k_of[m] < k}
        same = E.closure(small, base & small, n) == E.closure(allk, base, n) & small
        ok1 &= same
        info1["(c) bounded closures (knots up to 5 points, 19-point chain) equal to the full closure within the bound"] += same
        info1["(c) bounded closures compared"] += 1
hgc = json.loads((ROOT / "proofs/HUB-GLUE-20261102-001C/HUB-GLUE-20261102-001C-P001_an_opened_hub_creates_emergence/result.json").read_text())
hgc4 = next(v["info"] for k, v in hgc["checks"].items() if k.startswith("4 "))
ls, ss, n, side, ports = G.splice(FANO[0], FANO[1], 7, 0, FANO[0], FANO[1], 7, 0)
P = {v for v in range(n) if side[v] == 0}
Q = set(range(n)) - P
mine = collections.Counter()
for M, line in enumerate(ls):
    held = not set(line) <= P
    knots, can, allk = knots_of(ls, ss, n, M)
    gen = E.closure(allk, {can[m] for m in knots if set(E.bits(m)) <= P or set(E.bits(m)) <= Q | ports}, n)
    for m in knots:
        B = set(E.bits(m))
        if B & (P - ports) and B & Q:
            mine["%s: %s" % ("hub held" if held else "hub opened", "generated by eliminations" if can[m] in gen else "not generated")] += 1
same = dict(mine) == hgc4
ok1 &= same
info1["(d) HUB-GLUE C check 4 recomputed with tie classes"] = dict(mine)
info1["(d) equal to the recorded counts"] = same
check("1 the method: the bitmask circuits equal glue_lib's; the per-target closure up to tie classes equals forward elimination; a "
      "closure computed with knots up to 5 points equals the full closure within that bound (a derivation never uses a knot larger "
      "than its result); and the closure reproduces HUB-GLUE C's counts at an opened hub, which were computed with representatives",
      ok1, dict(info1))

# ------------------------------------------------------------------------------------------------ 2. the hypothesis as first posed
probe = {}
for label, pieces, edges in [("K4 > Fano > K4, disjoint hubs", [K4, FANO, K4], [(0, 0, 1, 0), (1, 0, 2, 0)]),
                             ("K4 > K4 > K4, touching hubs", [K4, K4, K4], [(0, 0, 1, 0), (1, 1, 2, 0)])]:
    ls, ss, n, piece, cuts = T.assemble(pieces, edges)
    t = collections.Counter()
    for M in range(len(ls)):
        opened, cl = classify(ls, ss, n, cuts, M)
        if len(opened) < 2:
            continue
        t["removals opening two cuts"] += 1
        t["of which with touching hubs"] += bool(shared_ports(opened))
        for k, c in cl.values():
            if k >= 2:
                t["knots crossing both opened cuts: " + c] += 1
    probe[label] = dict(t)
d, tch = probe["K4 > Fano > K4, disjoint hubs"], probe["K4 > K4 > K4, touching hubs"]
check("2 the hypothesis that opened cuts interact only where their hubs touch fails both ways: K4 > Fano > K4 with disjoint hubs carries "
      "new knots across its second opened cut, and K4 > K4 > K4 with touching hubs has no knot crossing both opened cuts that is not "
      "generated from knots crossing none",
      d.get("of which with touching hubs", 1) == 0 and d.get("knots crossing both opened cuts: carried", 0) > 0 and
      tch.get("of which with touching hubs") == tch.get("removals opening two cuts") > 0 and
      set(tch) <= {"removals opening two cuts", "of which with touching hubs", "knots crossing both opened cuts: " + CLASSES[0]}, probe)

# ------------------------------------------------------------------------------------------------ 3-4. the sweep
chains = []
for P0, P1, P2 in itertools.product([K4, FANO], repeat=3):
    for li in range(len(P1[0])):
        chains.append(("%s > %s > %s, second line %d" % (NAME[id(P0)], NAME[id(P1)], NAME[id(P2)], li), [P0, P1, P2],
                       [(0, 0, 1, 0), (1, li, 2, 0)]))
for Ps in [(FANO, K4, K4, FANO), (K4, FANO, FANO, K4), (FANO, FANO, K4, K4), (K4, K4, K4, K4), (FANO, K4, FANO, K4)]:
    for li in (range(4) if Ps[1] is K4 else (0, 3)):
        for lj in (range(4) if Ps[2] is K4 else (0, 3)):
            chains.append(("%s > %s > %s > %s, lines %d, %d" % tuple([NAME[id(P)] for P in Ps] + [li, lj]), list(Ps),
                           [(0, 0, 1, 0), (1, li, 2, 0), (2, lj, 3, 0)]))
rows = {}
tot = collections.Counter()
sizes = collections.Counter()
k4_only = collections.Counter()
for label, pieces, edges in chains:
    ls, ss, n, piece, cuts = T.assemble(pieces, edges)
    assert G.fails_globally(ls, ss, n) and all(T.cut_shape(ls, n, c["points"]) == (3, 3, 3, 1) for c in cuts), label
    row = collections.Counter()
    for M, line in enumerate(ls):
        opened, cl = classify(ls, ss, n, cuts, M)
        if len(opened) < 2:
            continue
        row["removals opening two or more cuts"] += 1
        sp = shared_ports(opened)
        touching = bool(sp)
        through = bool(sp & set(line))
        row["of which with touching hubs"] += touching
        row["of which through a shared port"] += through
        hub = sum(1 << v for v in line)
        for m, (k, c) in cl.items():
            if c == CLASSES[0]:
                continue
            row[c] += 1
            if c == "carried":
                tot["carried knots at removals with touching hubs" if touching else "carried knots at removals with disjoint hubs"] += 1
            if c == "joint":
                sizes[bin(m).count("1")] += 1
                tot["joint knots at removals with touching hubs" if touching else "joint knots at removals with disjoint hubs"] += 1
                tot["joint knots at removals through a shared port" if through else "joint knots at removals missing every shared port"] += 1
                tot["joint knots through the removed line's hub" if m & hub else "joint knots off the removed line's hub"] += 1
    rows[label] = {"points": n, **dict(row)}
    tot["chains"] += 1
    tot["removals opening two or more cuts"] += row["removals opening two or more cuts"]
    for c in CLASSES[1:]:
        tot[c + " knots"] += row[c]
    if all(P is K4 for P in pieces):
        k4_only["chains of K4^(3) pieces alone"] += 1
        k4_only["their new, carried or joint knots"] += sum(row[c] for c in CLASSES[1:])
print("   ", json.dumps(tot), round(time.time() - T0, 1), "s", flush=True)
need = ["carried knots at removals with touching hubs", "carried knots at removals with disjoint hubs",
        "joint knots at removals with touching hubs", "joint knots at removals with disjoint hubs",
        "joint knots at removals through a shared port", "joint knots at removals missing every shared port",
        "joint knots through the removed line's hub", "joint knots off the removed line's hub"]
check("3 on 96 chains of three and four K4^(3) and Fano pieces (every second splice line of three-piece chains, selected lines of "
      "four-piece chains, 10 to 19 points, all circuits): carried and joint knots occur with disjoint hubs as with touching ones, and joint "
      "knots occur at removals through a port shared by two opened cuts and at removals whose line misses every shared port, through the "
      "removed line's hub and off it: no hub-level feature decides interaction",
      tot["chains"] == 96 and all(tot[k] > 0 for k in need), {"totals": dict(tot), "per chain": rows})
check("4 two regularities on all 96 chains: every joint knot has three or four points, and chains of K4^(3) pieces alone have no new, "
      "carried or joint knot",
      set(sizes) <= {3, 4} and sum(sizes.values()) > 0 and k4_only["chains of K4^(3) pieces alone"] > 0 and
      k4_only["their new, carried or joint knots"] == 0,
      {"joint knots by size": dict(sorted(sizes.items())), **dict(k4_only)})

# ------------------------------------------------------------------------------------------------ 5. corners at a shared port
info5, ok5 = {}, True
for label, pieces, edges, far_fano in [("Fano > K4 > Fano, touching hubs", [FANO, K4, FANO], [(0, 0, 1, 0), (1, 1, 2, 0)], True),
                                       ("Fano > Fano > Fano, touching hubs", [FANO, FANO, FANO], [(0, 0, 1, 0), (1, 3, 2, 3)], True),
                                       ("Fano > K4 > K4, touching hubs", [FANO, K4, K4], [(0, 0, 1, 0), (1, 1, 2, 0)], False),
                                       ("Fano > Fano > K4, touching hubs", [FANO, FANO, K4], [(0, 0, 1, 0), (1, 3, 2, 0)], False)]:
    ls, ss, n, piece, cuts = T.assemble(pieces, edges)
    t = collections.Counter()
    for M, line in enumerate(ls):
        opened, cl = classify(ls, ss, n, cuts, M)
        if len(opened) < 2:
            continue
        joint = {m for m, (k, c) in cl.items() if c == "joint"}
        sp = shared_ports(opened) & set(line)
        if not sp:
            t["removals off the shared port with joint knots"] += bool(joint)
            continue
        p = next(iter(sp))
        L1, L2 = [L for k, L in enumerate(ls) if k != M and p in L]
        corners = set()
        for a in set(L1) - {p} - set(line):
            for b in set(L2) - {p} - set(line):
                pair = (1 << a) | (1 << b)
                if all(pair & inner and pair & outer for inner, outer in cut_masks(opened, n)):
                    corners |= {pair | (1 << x) for x in line}
        t["removals through the shared port"] += 1
        t["corners"] += len(corners)
        t["corners that are circuits"] += len(corners & set(E.circuits(G.removal(ls, ss, n, M), n, 3)))
        t["joint knots"] += len(joint)
        t["removals where the joint knots are exactly the corners"] += joint == corners
    info5[label] = dict(t)
    ok5 &= t["removals through the shared port"] == 2 and t["corners"] == t["corners that are circuits"] == 24 and \
        t["removals off the shared port with joint knots"] == 0 and \
        (t["removals where the joint knots are exactly the corners"] == 2 if far_fano else t["joint knots"] == 0)
check("5 corners at a shared port: with touching hubs, removing either line through the shared port leaves 12 corner circuits (a point "
      "of the removed line, a point of the port's other near-side line, a point of its slot line beyond the second cut); with a Fano far "
      "end they are exactly the joint knots (Fano > K4 > Fano, Fano > Fano > Fano), with a K4^(3) far end knots crossing fewer cuts "
      "generate them (Fano > K4 > K4, Fano > Fano > K4)", ok5, info5)

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
