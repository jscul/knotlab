#!/usr/bin/env python3
"""Checks for NATIVE-PATHS-20261101-001A: two kinds of interface in the knot's spaces.

    python3 -B check.py          verify result.json against a fresh run
    python3 -B check.py --write  write result.json from a fresh run
Run with the repository's .venv (networkx, pysat)."""
import hashlib
import itertools
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
import paths_lib as P  # noqa: E402

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
ok1 = all(P.T.is_cubic(H) and P.incidence_graph(H).number_of_nodes() == 2 * P.T.npoints(H) and not P.colourable(H)
          and __import__("networkx").is_connected(P.incidence_graph(H)) for H in SP.values())
check("1 ten knot's spaces: Fano, splice chains of 2-4 Fano planes, a star of 4, cycles of 3, 5 and 7 Fano blocks, the twisted cube (43 "
      "points) and the 3-cycle spliced into Fano; all connected, cubic, not 2-colourable", ok1, {n: P.T.npoints(H) for n, H in SP.items()})

# ------------------------------------------------------------------------------------------------ 2-3. 2-edge cuts
EQ2, NE2 = frozenset({(0, 0), (1, 1)}), frozenset({(0, 1), (1, 0)})
NEG = frozenset({(0, 1), (1, 0)})
info2, info3, bal_ok, par_ok, atom_ok = {}, {}, True, True, True
for name, H in SP.items():
    cuts = P.nontrivial_cuts(H, 2)
    kinds = {}
    for cut, comps in cuts:
        rels = []
        for S in comps:
            pts, lns, ports, slots = P.shore_data(H, cut, S)
            bal_ok &= len(pts) == len(lns) and len(ports) == 1 and len(slots) == 1
            rels.append(P.accepted(H, pts, lns, ports, slots))
        par_ok &= sorted(rels, key=sorted) == sorted([EQ2, NE2], key=sorted)
        atom_ok &= all(P.atom_relation(H, e) == NEG for e in cut)
        key = "sizes " + "/".join(str(len(c)) for c in sorted(comps, key=len))
        kinds[key] = kinds.get(key, 0) + 1
    info2[name] = len(cuts)
    info3[name] = kinds
check("2 balance: every nontrivial 2-edge cut of the ten spaces has, on each side, as many points as lines, one port point and one slot "
      "(3(p - l) = a - b with a + b = 2)", bal_ok and sum(info2.values()) > 0, {"nontrivial 2-edge cuts": info2})
check("3 at every nontrivial 2-edge cut of a knot's space one side accepts exactly equality and the other exactly disequality on (port "
      "colour, slot value), and cutting either edge alone leaves an exact negation (the atom lemma): complementary two-place parity, "
      "no hub", par_ok and atom_ok, {"cuts by shore sizes": info3})

# ------------------------------------------------------------------------------------------------ 4. 3-edge cuts, with signs
CUBE3 = frozenset(itertools.product((0, 1), repeat=3))
EQ3 = frozenset({(0, 0, 0), (1, 1, 1)})
info4, ok4 = {}, True
for name in ("chain of 3", "star of 4", "cycle of 3 blocks", "twisted cube", "3-cycle spliced into Fano"):
    H = SP[name]
    cuts = P.nontrivial_cuts(H, 3)
    kinds = {}
    for cut, comps in cuts:
        sides = []
        for S in comps:
            pts, lns, ports, slots = P.shore_data(H, cut, S)
            sides.append((len(ports), len(slots), P.accepted(H, pts, lns, ports, slots)))
        point_side = next(s for s in sides if s[0] == 3)[2]
        line_side = next(s for s in sides if s[1] == 3)[2]
        pair = sorted(point_side)
        good = len(pair) == 2 and all(a ^ b == 1 for a, b in zip(*pair)) and line_side == CUBE3 - point_side
        ok4 &= good
        key = "plain (v = 000)" if point_side == EQ3 else "twisted (v != 000)"
        kinds[key] = kinds.get(key, 0) + 1
    info4[name] = {"nontrivial 3-edge cuts": len(cuts), **kinds}
plain_in_trees = all(set(info4[n]) - {"nontrivial 3-edge cuts"} <= {"plain (v = 000)"} for n in ("chain of 3", "star of 4"))
twisted_in_cycles = any("twisted (v != 000)" in info4[n] for n in ("cycle of 3 blocks", "twisted cube", "3-cycle spliced into Fano"))
check("4 across every nontrivial 3-edge cut the point side accepts one antipodal pair {v, v-bar} (equality up to signs on the channels: a "
      "hub) and the line side exactly its complement (not-all-equal up to signs: the knot); v = 000 in splice trees, twisted in cyclic "
      "spaces, so KNOT-COMPOSE's 'exactly equality and not-all-equal' holds only up to signs", ok4 and plain_in_trees and twisted_in_cycles,
      info4)

# ------------------------------------------------------------------------------------------------ 5. where 2-edge cuts occur
expected = {"Fano": 0, "chain of 2": 0, "chain of 3": 0, "chain of 4": 0, "star of 4": 0, "cycle of 3 blocks": 3, "cycle of 5 blocks": 10,
            "cycle of 7 blocks": 21, "twisted cube": 3, "3-cycle spliced into Fano": 3}
check("5 splice trees have no nontrivial 2-edge cut (3-edge-connected); a cycle of k blocks has k(k-1)/2 (every pair of junctions); the "
      "twisted cube has 3; so the knot's spaces with cycles compose without hubs, which corrects KNOT-COMPOSE's 'only through hubs'",
      info2 == expected, {"nontrivial 2-edge cuts": info2})

# ------------------------------------------------------------------------------------------------ 6. control
# a colourable cubic system with a 2-edge cut: two copies of K4^(3) with the incidences (1, line 0) and (5, line 4) swapped
G = [(5, 2, 3), (0, 2, 3), (0, 1, 3), (0, 1, 2), (1, 6, 7), (4, 6, 7), (4, 5, 7), (4, 5, 6)]
deg = [sum(p in L for L in G) for p in range(8)]
ctrl_cuts = P.nontrivial_cuts(G, 2) if deg == [3] * 8 else []
ctrl_rels = [[P.accepted(G, *P.shore_data(G, cut, S)) for S in comps] for cut, comps in ctrl_cuts]
control = deg == [3] * 8 and P.colourable(G) and bool(ctrl_cuts) and any(len(r) > 2 for rels in ctrl_rels for r in rels)
check("6 control: in a colourable cubic system with a 2-edge cut (two K4^(3) joined crosswise) the sides are not both two-place parity, so "
      "the parity interface is a property of the knot's spaces", control,
      {"degrees ok": deg == [3] * 8, "2-edge cuts": len(ctrl_cuts), "side relation sizes": [[len(r) for r in rels] for rels in ctrl_rels]})

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
