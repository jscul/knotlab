#!/usr/bin/env python3
"""Checks for NATIVE-PATHS-20261101-001B: routes in the knot's spaces are fixed by the space and carry at most one bit.

    python3 -B check.py          verify result.json against a fresh run
    python3 -B check.py --write  write result.json from a fresh run
Run with the repository's .venv (networkx, numpy, pysat)."""
import collections
import hashlib
import itertools
import json
import random
import sys
import time
from pathlib import Path

import numpy as np
from pysat.solvers import Minisat22

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "proofs/NATIVE-PATHS-20261101-001A/NATIVE-PATHS-20261101-001A-P001_two_kinds_of_interface"))
import paths_lib as P  # noqa: E402

C = P.C
T0 = time.time()
OUT = {}


def check(name, ok, info):
    OUT[name] = {"pass": bool(ok), "info": info}
    print("PASS" if ok else "FAIL", name, json.dumps(info, default=str)[:600], round(time.time() - T0, 1), "s", flush=True)
    if not ok:
        print(json.dumps(info, default=str, indent=1))
        sys.exit(1)


# ------------------------------------------------------------------------------------------------ 0. bindings
manifest = json.loads((HERE / "manifest.json").read_text())
bad = {p: d for p, d in manifest["parent_bindings"].items() if hashlib.sha256((ROOT / p).read_bytes()).hexdigest() != d}
status = {p: json.loads((ROOT / p).read_text()).get("status") for p in manifest["parent_bindings"] if p.endswith(".json")}
check("0 dependency artifacts bound by hash; upstream proofs Proved", not bad and all(s in ("Proved", "passed") for s in status.values()),
      {"mismatched": bad, "statuses": status})

EQ2, NE2 = frozenset({(0, 0), (1, 1)}), frozenset({(0, 1), (1, 0)})
EQ3 = frozenset({(0, 0, 0), (1, 1, 1)})


def parity(m):
    return frozenset((x, y) for x in (0, 1) for y in (0, 1) if (x ^ y) == m % 2)


# ------------------------------------------------------------------------------------------------ 1-4. the decomposition
def decompose(H):
    """2-edge cuts with both shores' relations; 3-edge cuts as proper splice cuts or shifts; crossing counts"""
    V = frozenset(P.incidence_graph(H).nodes())
    two = []
    for cut, comps in P.nontrivial_cuts(H, 2):
        two.append({"shore": frozenset(comps[0]), "rel": {frozenset(S): P.accepted(H, *P.shore_data(H, cut, S)) for S in comps}})
    proper, shifts, shift_found, twist_rule = [], [], True, True
    for cut, comps in P.nontrivial_cuts(H, 3):
        sides = []
        for S in comps:
            pts, lns, ports, slots = P.shore_data(H, cut, S)
            sides.append((len(ports), len(pts), P.accepted(H, pts, lns, ports, slots)))
        point_side = next(s for s in sides if s[0] == 3)
        twisted = point_side[2] != EQ3
        ends = collections.Counter(v for e in cut for v in e)
        doubled = [v for v, c in ends.items() if c == 2]
        if doubled:
            w = doubled[0]
            Y = frozenset(next(c for c in comps if w in c)) - {w}
            match = [t for t in two if Y in t["rel"]]
            shift_found &= len(match) == 1
            twist_rule &= bool(match) and (match[0]["rel"][Y] == NE2) == twisted
            shifts.append((frozenset(comps[0]), twisted))
        else:
            proper.append((frozenset(comps[0]), twisted, point_side[1], len(point_side[2])))

    def cross(X, Y):
        return bool(X & Y and X - Y and Y - X and V - (X | Y))

    pairs = lambda A, B: sum(cross(a[0], b[0]) for a in A for b in B)  # noqa: E731
    twos = [(t["shore"],) for t in two]
    return {"2-edge cuts": len(two),
            "proper splice cuts (plain, twisted)": [sum(not p[1] for p in proper), sum(p[1] for p in proper)],
            "shifts (plain, twisted)": [sum(not s[1] for s in shifts), sum(s[1] for s in shifts)],
            "proper point sides (points, states)": sorted({(p[2], p[3]) for p in proper}),
            "crossings": {"proper-proper": pairs(proper, proper) // 2, "proper-2cut": pairs(proper, twos),
                          "2cut-2cut": pairs(twos, twos) // 2, "shift-shift": pairs(shifts, shifts) // 2, "shift-proper": pairs(shifts, proper),
                          "shift-2cut": pairs(shifts, twos)},
            "every doubled-vertex cut is the shift of a 2-edge cut": shift_found, "twist rule": twist_rule}


SP = P.spaces()
DEC = {name: decompose(H) for name, H in SP.items()}
check("1 every nontrivial 3-edge cut of the ten knot's spaces is a proper splice cut (three distinct ports and slots) or the shift of a "
      "nontrivial 2-edge cut (a vertex carries two of its edges; removing it from its shore leaves the 2-edge cut); every proper cut's "
      "point side accepts two states whatever its size", all(d["every doubled-vertex cut is the shift of a 2-edge cut"] for d in DEC.values())
      and all(s == 2 for d in DEC.values() for _, s in d["proper point sides (points, states)"]),
      {n: {k: d[k] for k in ("2-edge cuts", "proper splice cuts (plain, twisted)", "shifts (plain, twisted)",
                              "proper point sides (points, states)")} for n, d in DEC.items()})
check("2 twist rule: a shift is twisted (point side {v, v-bar} with v != 000) exactly when the shore that absorbed the moved vertex "
      "accepts disequality across the 2-edge cut", all(d["twist rule"] for d in DEC.values()),
      {n: d["shifts (plain, twisted)"] for n, d in DEC.items()})
lam = all(d["crossings"]["proper-proper"] == 0 and d["crossings"]["proper-2cut"] == 0 for d in DEC.values())
fires = sum(d["crossings"]["shift-shift"] + d["crossings"]["2cut-2cut"] for d in DEC.values()) > 0
check("3 fixed by the space: in all ten spaces the proper splice cuts are pairwise non-crossing and cross no 2-edge cut; every crossing "
      "pair involves a shift or two 2-edge cuts (the crossing test fires on those)", lam and fires,
      {n: d["crossings"] for n, d in DEC.items()})


def relabel(H, rng):
    pts = sorted({p for L in H for p in L})
    perm = dict(zip(pts, rng.sample(pts, len(pts))))
    lines = [tuple(perm[p] for p in L) for L in H]
    rng.shuffle(lines)
    return lines


rng = random.Random(20261101)
inv = {}
for name in ("chain of 3", "cycle of 3 blocks", "3-cycle spliced into Fano"):
    inv[name] = [decompose(relabel(SP[name], rng)) == DEC[name] for _ in range(2)]
check("4 the decomposition is unchanged under relabelling points and reordering lines (two random relabellings of three spaces)",
      all(all(v) for v in inv.values()), inv)


# ------------------------------------------------------------------------------------------------ 5-8. cycles of Fano blocks
def cycle_parts(k):
    """lines, the junction incidences (connecting line i, port point of unit i+1), each unit's port point and line indices"""
    lines, conn, ports = C.cycle_of_blocks(k)
    junction = [(conn[i], ports[(i + 1) % k][2]) for i in range(k)]
    port = [ports[i][2] for i in range(k)]
    unit_lines = [[j for j, L in enumerate(lines) if j not in conn and all(7 * i <= p < 7 * i + 7 for p in L)] + [conn[i]]
                  for i in range(k)]
    return lines, junction, port, unit_lines


def relation_after_cut(lines, junction, J, a, b):
    """joint relation of the port colours of points a and b once the junction incidences in J are cut (None if not colourable)"""
    n = 1 + max(p for L in lines for p in L)
    nv, clauses = n, []
    cut = {junction[i] for i in J}
    for j, L in enumerate(lines):
        lits = []
        for p in L:
            if (j, p) in cut:
                nv += 1
                lits.append(nv)
            else:
                lits.append(p + 1)
        clauses += [lits, [-x for x in lits]]
    with Minisat22(bootstrap_with=clauses) as S:
        if not S.solve():
            return None
        return frozenset((x, y) for x in (0, 1) for y in (0, 1) if S.solve(assumptions=[(a + 1) if x else -(a + 1), (b + 1) if y else -(b + 1)]))


arc_ok, arc_info = True, {}
for k in (3, 5, 7):
    lines, junction, port, unit_lines = cycle_parts(k)
    seen = collections.Counter()
    for i in range(k):
        for m in range(1, k):
            units = [(i + t) % k for t in range(m)]
            pts = sorted(p for u in units for p in range(7 * u, 7 * u + 7))
            lns = sorted(j for u in units for j in unit_lines[u])
            last = units[-1]
            rel = P.accepted(lines, pts, lns, [port[i]], [junction[last]])
            arc_ok &= rel == parity(m)
            seen["disequality" if rel == NE2 else "equality" if rel == EQ2 else "other"] += 1
    arc_info["cycle of %d blocks" % k] = dict(seen)
check("5 in cycles of 3, 5 and 7 Fano blocks every arc of m units (1 <= m < k, every start) accepts exactly x + y = m (mod 2) on (port "
      "colour, slot value): a route through atoms carries its length mod 2", arc_ok, arc_info)

sep_ok, sep_info = True, {}
for k in (3, 5, 7):
    lines, junction, port, _ = cycle_parts(k)
    tally = collections.Counter()
    closed_fails = relation_after_cut(lines, junction, [], port[0], port[1]) is None
    for a, b in itertools.combinations(range(k), 2):
        forward = set(range(a, b))
        back = set(range(k)) - forward
        for r in range(1, k + 1):
            for J in itertools.combinations(range(k), r):
                rel = relation_after_cut(lines, junction, J, port[a], port[b])
                if rel is None:
                    sep_ok = False
                    continue
                if set(J) & forward and set(J) & back:
                    want, key = frozenset(itertools.product((0, 1), repeat=2)), "both routes cut: product"
                elif set(J) & forward:
                    want, key = parity(k - (b - a)), "back route intact: its parity"
                else:
                    want, key = parity(b - a), "forward route intact: its parity"
                sep_ok &= rel == want
                tally[key] += 1
        sep_ok &= parity(b - a) != parity(k - (b - a))
    sep_ok &= closed_fails
    sep_info["cycle of %d blocks" % k] = dict(tally, closed_cycle_fails=closed_fails)
check("6 two routes and separation: for every pair of units and every non-empty set J of junctions (cycles of 3, 5, 7 blocks) the "
      "system with J cut is colourable and the units' port colours are unrelated (a product) exactly when J meets both routes; "
      "otherwise they carry the parity of the intact route; the two routes' parities differ and the closed cycle fails", sep_ok, sep_info)


def count_table(lines, pts, lns, port_point, slot):
    """number of colourings of pts, proper on lns, for each (port colour, slot value); the slot line reads the value instead of its point"""
    n = len(pts)
    col = {p: i for i, p in enumerate(pts)}
    a = np.arange(1 << n, dtype=np.int64)
    bits = [((a >> i) & 1).astype(np.int8) for i in range(n)]
    table = {}
    for y in (0, 1):
        ok = np.ones(1 << n, dtype=bool)
        for j in lns:
            vals = [np.full(1 << n, y, dtype=np.int8) if (j, p) == slot else bits[col[p]] for p in lines[j]]
            s = vals[0] + vals[1] + vals[2]
            ok &= (s != 0) & (s != 3)
        for x in (0, 1):
            table[(x, y)] = int((ok & (bits[col[port_point]] == x)).sum())
    return table


cnt_ok, cnt_info = True, {}
lines, junction, port, unit_lines = cycle_parts(3)
for i in range(3):
    t = count_table(lines, list(range(7 * i, 7 * i + 7)), unit_lines[i], port[i], junction[i])
    cnt_ok &= t == {(0, 0): 0, (0, 1): 5, (1, 0): 5, (1, 1): 0}
    cnt_info["unit %d of the 3-cycle" % i] = {str(k): v for k, v in t.items()}
lines, junction, port, unit_lines = cycle_parts(5)
for m in (1, 2, 3):
    units = list(range(m))
    t = count_table(lines, [p for u in units for p in range(7 * u, 7 * u + 7)], [j for u in units for j in unit_lines[u]], port[0],
                    junction[m - 1])
    cnt_ok &= t == {xy: (5 ** m if (xy[0] ^ xy[1]) == m % 2 else 0) for xy in t}
    cnt_info["arc of %d units of the 5-cycle" % m] = {str(k): v for k, v in t.items()}
check("7 counting the witnesses the relations quantify away: each Fano unit has 5 colourings for each accepted pair and 0 otherwise; an "
      "arc of m units (m = 1, 2, 3) has 5^m for each accepted pair", cnt_ok, cnt_info)

# ------------------------------------------------------------------------------------------------ 9. control
lines, junction, port, _ = cycle_parts(4)
ctrl = {"colourable": P.T.colourable_sat(lines)}
agree = True
for a, b in itertools.combinations(range(4), 2):
    forward = list(range(a, b))
    back = [i for i in range(4) if i not in forward]
    r_closed = relation_after_cut(lines, junction, [], port[a], port[b])
    r_f = relation_after_cut(lines, junction, [back[0]], port[a], port[b])
    r_b = relation_after_cut(lines, junction, [forward[0]], port[a], port[b])
    agree &= r_closed == r_f == r_b == parity(b - a)
ctrl["routes agree for every pair"] = agree
check("8 control: the even cycle of 4 Fano blocks is colourable, and its two routes between any two units carry the same parity, which "
      "the closed cycle keeps", ctrl["colourable"] and agree, ctrl)

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
