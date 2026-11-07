#!/usr/bin/env python3
"""Checks for SPHERE-COUNT-20261106-001A: the violated line can be pinned.

    python3 -B check.py          verify result.json against a fresh run
    python3 -B check.py --write  write result.json from a fresh run
Run with the repository's .venv (python-sat, networkx, numpy). Single process; a few minutes."""
import hashlib
import itertools
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
import pin_lib as P  # noqa: E402

T0 = time.time()
OUT = {}


def check(name, ok, info):
    OUT[name] = {"pass": bool(ok), "info": info}
    print("PASS" if ok else "FAIL", name, json.dumps(info, default=str), round(time.time() - T0, 1), "s", flush=True)
    if not ok:
        sys.exit(1)


if __name__ == "__main__":
    manifest = json.loads((HERE / "manifest.json").read_text())
    bad = {q: dg for q, dg in manifest["parent_bindings"].items() if hashlib.sha256((ROOT / q).read_bytes()).hexdigest() != dg}
    status = {q: json.loads((ROOT / q).read_text()).get("status") for q in manifest["parent_bindings"]
              if q.endswith(".json") and q.startswith("proofs/")}
    check("0 dependency artifacts bound by hash; upstream proofs Proved", not bad and all(s in ("Proved", "passed") for s in status.values()),
          {"mismatched": bad, "statuses": status})

    # 1. blocking configurations in the bulk, both neighbour classes, radius 0..3
    M = P.U(0, 0)
    info1, ok1 = {}, True
    found = {}
    for name, Mp in (("U(1,0)", P.U(1, 0)), ("U(1,-1)", P.U(1, -1))):
        for r in (0, 1, 2, 3):
            cfg, it = P.blocking_configuration(Mp, r)
            good = cfg is not None and P.local_validity(cfg, M) and not P.can_move_bulk(cfg, M, Mp, r)
            info1["%s, r=%d" % (name, r)] = {"blocking configuration found": cfg is not None, "locally valid and blocked": good,
                                             "search iterations": it}
            ok1 &= good
            found[(name, r)] = cfg
    check("1 in the bulk, for both classes of adjacent line and every radius r <= 3, the two-level search finds a colouring of the ball "
          "of radius r+1 in which every triangle is not-all-equal except M, and from which no recolouring within radius r makes the "
          "adjacent line the only violated one", ok1, info1)

    # 2. the r=3 blocking configuration: which of the six adjacent lines can the violated line reach at all within radius 2?
    cfg = found[("U(1,0)", 3)]
    nbrs = {"U(1,0)": P.U(1, 0), "U(-1,0)": P.U(-1, 0), "U(0,1)": P.U(0, 1), "U(0,-1)": P.U(0, -1), "U(-1,1)": P.U(-1, 1),
            "U(1,-1)": P.U(1, -1)}
    reach = {}
    for name, Mp in nbrs.items():
        dom = P.ball(set(M) | set(Mp), 3)
        reach[name] = [P.can_move_bulk(cfg, M, Mp, r) if dom <= set(cfg) else None for r in (0, 1, 2)]
    blocked = [nm for nm, v in reach.items() if v and not any(x for x in v if x is not None)]
    # rows of the configuration, for the record
    xs = [p[0] for p in cfg]; ys = [p[1] for p in cfg]
    rows = []
    for y in range(max(ys), min(ys) - 1, -1):
        rows.append(" " * (y - min(ys)) + " ".join(str(cfg[(x, y)]) if (x, y) in cfg else "." for x in range(min(xs), max(xs) + 1)))
    check("2 the blocking configuration for U(1,0) at r=3 (concentric alternating rings around the violated line): within radius 2 "
          "the violated line reaches only some of its six adjacent lines", len(blocked) >= 3, {"reach at r = 0, 1, 2": reach,
                                                                                               "blocked directions": blocked,
                                                                                               "configuration rows": rows})

    # 3. global blocking states on the octahedral space K_8
    info3, ok3 = {}, True
    for r in (2, 3):
        Mc, res = P.global_blocking(8, r)
        info3["r=%d" % r] = {"violated line": Mc, "adjacent lines": len(res),
                             "adjacent lines with a blocking whole-sphere state": sum(1 for v in res.values() if v[0]),
                             "search iterations": {str(j): v[1] for j, v in res.items()}}
        ok3 &= len(res) == 6 and all(v[0] for v in res.values())
    check("3 on the octahedral knot space K_8 (256 points), for the line farthest from the corners and each of its six adjacent lines, "
          "there is a whole-sphere state violating only that line from which the violated line cannot move to the adjacent line by "
          "changing points within distance r, for r = 2 and r = 3", ok3, info3)

    # 4. random states do move
    tally = P.random_state_moves(8, 25, seed=7)
    check("4 from 25 random states of K_8 (random solver phases), every adjacent line is reached, at the least radius shown",
          None not in tally and sum(tally.values()) > 100, {"least radius: count": {str(k): v for k, v in sorted(tally.items(), key=str)}})

    # 5. label states
    span_ok, span3_bad = True, 0
    for T in (P.U(0, 0), P.D(0, 0)):
        subs = [P.SUB(p) for p in T]
        assert sorted(subs) == [0, 1, 2]
        for labs in itertools.product(range(6), repeat=3):
            # span: labels lie in an arc of at most two consecutive values
            s = set(labs)
            arc2 = any(s <= {a, (a + 1) % 6} for a in range(6))
            arc3 = any(s <= {a, (a + 1) % 6, (a + 2) % 6} for a in range(6))
            cols = {P.colour(l, sb) for l, sb in zip(labs, subs)}
            if arc2:
                span_ok &= len(cols) == 2
            elif arc3:
                span3_bad += len(cols) == 1
    z = (0, 0)
    ring = [(1, 0), (0, 1), (-1, 1), (-1, 0), (0, -1), (1, -1)]
    tris = [(z, ring[j], ring[(j + 1) % 6]) for j in range(6)]
    vortex = {}
    for orient in (1, -1):
        for rot in range(6):
            lab = {ring[j]: (rot + orient * j) % 6 for j in range(6)}
            for v in (0, 1):
                col = {p: P.colour(lab[p], P.SUB(p)) for p in ring}
                col[z] = v
                bad = [j for j, T in enumerate(tris) if len({col[p] for p in T}) == 1]
                kinds = ["U" if any(set(T) == set(P.U(x, y)) for (x, y) in T) else "D" for T in [tris[j] for j in bad]]
                vortex[(orient, rot, v)] = (len(bad), kinds)
    one_each = all(cnt == 1 for (o, rt, v), (cnt, kd) in vortex.items())
    plus_line = all(vortex[(1, rt, v)][1] == ["U"] for rt in range(6) for v in (0, 1))
    minus_face = all(vortex[(-1, rt, v)][1] == ["D"] for rt in range(6) for v in (0, 1))
    check("5 label states: labels on a triangle within two consecutive values always give a not-all-equal colouring (three "
          "consecutive values can fail: the control); a point whose six neighbours carry 0..5 in cyclic order is a vortex: whatever its "
          "colour, exactly one of its six triangles is monochromatic, a line when the labels increase counterclockwise and a face when "
          "they decrease, so violated lines and full faces are the vortices and antivortices of the labels",
          span_ok and span3_bad > 0 and one_each and plus_line and minus_face,
          {"two consecutive values always not-all-equal": span_ok, "three consecutive values, monochromatic cases (control)": span3_bad,
           "vortex: exactly one monochromatic triangle in all 24 cases": one_each,
           "counterclockwise labels: always a line": plus_line, "clockwise labels: always a face": minus_face})

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
