#!/usr/bin/env python3
"""Checks for SELECT-COUNT-20261101-001B: counted length is a measure on the knot's spaces.

    python3 -B check.py          verify result.json against a fresh run
    python3 -B check.py --write  write result.json from a fresh run
Run with the repository's .venv (networkx, numpy, pysat)."""
import collections
import hashlib
import itertools
import json
import math
import random
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "proofs/NATIVE-PATHS-20261101-001A/NATIVE-PATHS-20261101-001A-P001_two_kinds_of_interface"))
sys.path.insert(0, str(HERE))
import paths_lib as P  # noqa: E402
import count_lib as K  # noqa: E402

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

SP = P.spaces()
BLOCKS = {"Fano": 1, "chain of 2": 2, "chain of 3": 3, "chain of 4": 4, "star of 4": 4, "cycle of 3 blocks": 3, "cycle of 5 blocks": 5,
          "cycle of 7 blocks": 7, "twisted cube": 6, "3-cycle spliced into Fano": 4}
GLUE = {"twisted cube": 2}


def brute_count(lines):
    pts = K.points_of(lines)
    idx = {p: i for i, p in enumerate(pts)}
    a = np.arange(1 << len(pts), dtype=np.int64)
    ok = np.ones(1 << len(pts), dtype=bool)
    for L in lines:
        s = sum(((a >> idx[p]) & 1) for p in L)
        ok &= (s != 0) & (s != len(L))
    return int(ok.sum())


# ------------------------------------------------------------------------------------------------ 1. one amplitude, values
AMP, ok1, info1 = {}, True, {}
for name, H in SP.items():
    amps = sorted({K.amplitude(H, i) for i in range(len(H))})
    AMP[name] = amps[0]
    want = 5 ** BLOCKS[name] * GLUE.get(name, 1)
    ok1 &= len(amps) == 1 and amps[0] == want and K.count(H, K.points_of(H)) == 0
    info1[name] = {"amplitude at every line": amps, "5^blocks x glue": want,
                   "counted length / log 5": round(math.log(amps[0]) / math.log(5), 6)}
brute = {}
for name in ("Fano", "chain of 2", "cycle of 3 blocks"):
    H = SP[name]
    brute[name] = brute_count([L for i, L in enumerate(H) if i != 0]) // 2 == AMP[name]
check("1 one amplitude: on each of the ten knot's spaces, half the number of colourings of H minus a line is the same at every line; it "
      "is 5 per Fano block, times 2 for the twisted cube's glue; the counter agrees with brute force on three spaces", ok1 and all(brute.values()),
      {"spaces": info1, "brute force agrees (Fano, chain of 2, cycle of 3)": brute})

# ------------------------------------------------------------------------------------------------ 2. uniform sides, factorization
ok2, info2 = True, {}
for name, H in SP.items():
    tally = collections.Counter()
    for k in (2, 3):
        for cut, comps in P.nontrivial_cuts(H, k):
            ws = [K.side_weights(H, cut, frozenset(S)) for S in comps]
            vals = [sorted({v for v in w.values() if v}) for w in ws]
            sizes = sorted(sum(1 for v in w.values() if v) for w in ws)
            disjoint = not any(ws[0][w] and ws[1][w] for w in ws[0])
            good = all(len(v) == 1 for v in vals) and vals[0][0] * vals[1][0] == AMP[name] and disjoint
            ok2 &= good
            pair = sorted(round(math.log(v[0]) / math.log(5), 6) for v in vals)
            tally["%d-edge, states %s, log5 counts %s" % (k, "/".join(map(str, sizes)), pair)] += 1
    info2[name] = dict(tally)
check("2 at every nontrivial 2- and 3-edge cut of the ten spaces each side has the same count for every channel assignment it accepts "
      "(and none for the others), and the two sides' counts multiply to the amplitude: a(X) a(X-bar) = A(H)", ok2, info2)

# ------------------------------------------------------------------------------------------------ 3. routes
ok3, info3 = True, {}
for k in (3, 5, 7):
    lines, conn, ports = P.C.cycle_of_blocks(k)
    port = [ports[i][2] for i in range(k)]
    junction = [(conn[i], ports[(i + 1) % k][2]) for i in range(k)]
    unit_lines = [[j for j, L in enumerate(lines) if j not in conn and all(7 * i <= p < 7 * i + 7 for p in L)] + [conn[i]]
                  for i in range(k)]
    tally = collections.Counter()
    for i in range(k):
        for m in range(1, k):
            units = [(i + t) % k for t in range(m)]
            pts = [p for u in units for p in range(7 * u, 7 * u + 7)]
            lns = [j for u in units for j in unit_lines[u]]
            sub = [lines[j] for j in lns]
            last = units[-1]
            slot_line = lns.index(junction[last][0])
            table = {(x, y): K.count(sub, pts, fixed={port[i]: x}, slots={(slot_line, junction[last][1]): y}) for x in (0, 1) for y in (0, 1)}
            ok3 &= table == {(x, y): (5 ** m if (x ^ y) == m % 2 else 0) for x in (0, 1) for y in (0, 1)}
            tally["m = %d" % m] += 1
    info3["cycle of %d blocks" % k] = dict(tally)
check("3 routes: every arc of m units of the cycles of 3, 5 and 7 Fano blocks has exactly 5^m colourings for each accepted pair (port "
      "colour, slot value) and none otherwise: counted length m log 5 along the route, where the relation keeps only m mod 2", ok3, info3)

# ------------------------------------------------------------------------------------------------ 4. rings of units
UNITS = {"Fano": (SP["Fano"], 5), "chain of 2": (SP["chain of 2"], 25), "cycle of 3 blocks": (SP["cycle of 3 blocks"], 125),
         "twisted cube": (SP["twisted cube"], 31250)}
COMBOS = [("Fano", "chain of 2"), ("Fano", "chain of 2", "Fano"), ("chain of 2", "twisted cube"), ("Fano", "twisted cube", "cycle of 3 blocks"),
          ("chain of 2", "chain of 2", "Fano", "cycle of 3 blocks"), ("Fano", "Fano", "Fano", "Fano", "chain of 2"),
          ("twisted cube", "cycle of 3 blocks", "chain of 2", "Fano", "Fano")]
ok4, info4 = True, {}
unit_rel = {}
for nm, (H, a) in UNITS.items():
    e = (0, H[0][0])
    unit_rel[nm] = sorted(P.atom_relation(H, (("l", e[0]), ("p", e[1]))))
    ok4 &= unit_rel[nm] == [(0, 1), (1, 0)]
for combo in COMBOS:
    R = K.ring([(UNITS[c][0], (0, UNITS[c][0][0][0])) for c in combo])
    pts = K.points_of(R)
    cubic = all(len(L) == 3 for L in R) and all(sum(p in L for L in R) == 3 for p in pts)
    prod = math.prod(UNITS[c][1] for c in combo)
    full = K.count(R, pts)
    row = {"units": len(combo), "cubic": cubic, "colourings": full, "product of unit amplitudes": prod}
    if len(combo) % 2:
        amps = sorted({K.amplitude(R, i) for i in range(len(R))})
        row["amplitude at every line"] = amps
        ok4 &= cubic and full == 0 and amps == [prod]
    else:
        ok4 &= cubic and full == 2 * prod
    info4[" + ".join(combo)] = row
check("4 rings of units cut from different knot's spaces: every unit accepts exactly a negation; a ring fails exactly when it has an odd "
      "number of units, and then its amplitude (at every line) is the product of the units' amplitudes, while an even ring has twice that "
      "product as colourings: the relation counts parts, the count counts what is inside them", ok4,
      {"unit relations": unit_rel, "rings": info4})

# ------------------------------------------------------------------------------------------------ 5. transposes and relabelling
ok5, info5 = True, {}
rng = random.Random(20261101)
for name, H in SP.items():
    HT = K.transpose(H)
    ampT = sorted({K.amplitude(HT, i) for i in range(len(HT))})
    pts = K.points_of(H)
    perm = dict(zip(pts, rng.sample(pts, len(pts))))
    Hr = [tuple(perm[p] for p in L) for L in H]
    rng.shuffle(Hr)
    ampR = sorted({K.amplitude(Hr, i) for i in range(0, len(Hr), 5)})
    ok5 &= ampT == [AMP[name]] and ampR == [AMP[name]]
    info5[name] = {"transpose amplitude": ampT, "relabelled amplitude": ampR}
check("5 the amplitude is unchanged by transposition (points and lines exchanged, which swaps knot sides and hub sides) and by a random "
      "relabelling of every space", ok5, info5)

# ------------------------------------------------------------------------------------------------ 6. controls
two_fano = list(SP["Fano"]) + [tuple(p + 7 for p in L) for L in SP["Fano"]]
lines4, _, _ = P.C.cycle_of_blocks(4)
ctrl = {"two disjoint Fano planes: not colourable, but every line's amplitude is 0 (not minimal), so no counted length":
            K.count(two_fano, K.points_of(two_fano)) == 0 and {K.amplitude(two_fano, i) for i in range(len(two_fano))} == {0},
        "even cycle of 4 blocks: colourable with 2 * 5^4 colourings (counts still multiply)":
            K.count(lines4, K.points_of(lines4)) == 2 * 5 ** 4,
        "relationally equal units with different counts: Fano unit and 13-point unit both accept exactly a negation, counts 5 and 25":
            unit_rel["Fano"] == unit_rel["chain of 2"] and UNITS["Fano"][1] != UNITS["chain of 2"][1]}
check("6 controls: a disconnected failing system has no amplitude, a colourable cycle still multiplies, and two parts with the same "
      "relation have different counts (counted length is not a function of relations)", all(ctrl.values()), ctrl)

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
