#!/usr/bin/env python3
"""Checks for SPHERE-WIDTH-20261107-001A: the sphere's count needs resolution width Theta(sqrt n).

    python3 -B check.py          verify result.json against a fresh run
    python3 -B check.py --write  write result.json from a fresh run
Run with the repository's .venv (networkx, python-sat). Single process; several minutes."""
import hashlib
import json
import random
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
import width_lib as W  # noqa: E402

F = W.F
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

    # 1. the window criterion for label states, against a solver; feasible cases realized
    info1, ok1 = {}, True
    rng = random.Random(3)
    for k in (4, 5, 6):
        K = W.sphere(k)
        pts = [p for p in range(K["n"]) if p not in K["corner_pts"]]
        agree = dis = infeas = valid = tried = 0
        for trial in range(12):
            z0 = rng.choice(pts)
            x = W.random_label_state(K, z0, rng)
            P = rng.sample([p for p in range(K["n"]) if p != z0], rng.randint(3, K["n"] // 4))
            peb = {p: x[p] for p in P}
            for z in rng.sample([p for p in pts if p not in peb], 6):
                T = W.trivialize(K, z)
                f, s, a, D = W.feasible(K, T, peb)
                g = W.solver_feasible(K, T, peb)
                agree += f == g
                dis += f != g
                infeas += not g
                if f:
                    y, L = W.realize(K, T, peb, s, a, D)
                    v = F.violated(K, y)
                    tried += 1
                    valid += len(v) == 1 and z in K["lines"][v[0]] and all(y[p] == c for p, c in peb.items())
        ok1 &= dis == 0 and infeas > 0 and valid == tried
        info1["k=%d" % k] = {"(pebbled colours, vortex) pairs": agree + dis, "criterion agrees with the solver": agree,
                             "infeasible": infeas, "feasible cases realized as a state with exactly one violated line, at the vortex, "
                             "matching every pebble": "%d of %d" % (valid, tried)}
    check("1 window criterion on the sphere: pebbled colours (from random label states) admit a label state with the vortex at z exactly "
          "when the sheet system has no negative cycle (solver comparison), and the largest solution under the pebbles' upper bounds is "
          "a valid single-defect state", ok1, info1)

    # 2. obstruction certificates
    info2, ok2 = {}, True
    rng = random.Random(5)
    for k in (5, 6, 7):
        K = W.sphere(k)
        pts = [p for p in range(K["n"]) if p not in K["corner_pts"]]
        found = ineq = sep = through_z = 0
        worst = 0.0
        for trial in range(30):
            z = rng.choice(pts)
            x = W.random_label_state(K, z, rng)
            P = rng.sample([p for p in range(K["n"]) if p != z and p not in K["adj"][z]], rng.randint(4, K["n"] // 3))
            peb = {p: x[p] for p in P}
            Tz = W.trivialize(K, z)
            assert W.obstruction(K, Tz, peb) is None
            for z2 in rng.sample([p for p in pts if p not in peb and p != z], 5):
                T2 = W.trivialize(K, z2)
                ob = W.obstruction(K, T2, peb)
                if ob is None:
                    continue
                cyc, walk, bsum, a = ob
                L, r = len(walk) - 1, len(cyc)
                H2 = W.holonomy(T2, walk)
                found += 1
                ineq += bsum <= -1 and L <= 3 * r - 6 + H2
                if z in walk:
                    through_z += 1
                    sep += 1
                else:
                    Hz = W.holonomy(Tz, walk)
                    sep += (H2 - Hz) % 6 == 0 and H2 != Hz
                worst = max(worst, L / r)
        ok2 &= found > 0 and ineq == found and sep == found
        info2["k=%d" % k] = {"obstructions found (feasible at z, not at z')": found, "negative cycle with L <= 3r - 6 + H": ineq,
                             "walk separates z from z' (holonomy differs by a nonzero multiple of 6) or passes through z": sep,
                             "of which through z": through_z, "largest L / r": round(worst, 2)}
    check("2 obstruction certificates: whenever pebbled colours admit the vortex at z but not at z', the negative cycle of the sheet "
          "system closes into a walk of length L <= 3r - 6 + H through its r pebbles (H its label holonomy), and the walk separates z "
          "from z' or passes through z", ok2, info2)

    # 3. the pebble game, simulated
    info3, ok3 = {}, True
    for k in (6, 8):
        K = W.sphere(k)
        z0 = max(range(K["n"]), key=lambda x: (min(W.bfs(K["adj"], [x], K["n"])[c] for c in K["corner_pts"]), -x))
        for M in (4, 8, 12):
            d1 = W.Duplicator(K, 4, z0)
            s1 = W.spoiler_chaser(K, d1, M, 30)
            d2 = W.Duplicator(K, 4, z0)
            s2 = W.spoiler_ring(K, d2, M, 4, random.Random(M))
            ok3 &= s1 and s2
            info3["k=%d, M=%d" % (k, M)] = {"chaser: Duplicator survives 30 placements": s1, "chaser: vortex moves": d1.moves,
                                            "ring builder: Duplicator survives": s2, "ring builder: vortex moves": d2.moves}
    check("3 the pebble game, simulated (an illustration, not a proof): Duplicator answering from label states whose vortex sits where "
          "the pebble density is lowest survives a chaser and a ring-building Spoiler with up to 12 pebbles on K_6 and K_8", ok3, info3)

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
