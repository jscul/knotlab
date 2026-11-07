#!/usr/bin/env python3
"""Checks for FLAT-STATES-20261107-001A: flat states exist on the whole sphere.

    python3 -B check.py          verify result.json against a fresh run
    python3 -B check.py --write  write result.json from a fresh run
Run with the repository's .venv (networkx). Single process; a few minutes."""
import hashlib
import json
import random
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
import flat_lib as F  # noqa: E402

T0 = time.time()
OUT = {}
KS = range(2, 13)


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

    SP = {k: F.index_lines(F.build(k)) for k in KS}

    # 1. holonomy of the frame moves around every face
    info1, ok1 = {}, True
    for k, K in SP.items():
        tri = {F.face_holonomy(K, fi) for fi, P in enumerate(K["fpts"]) if len(P) == 3}
        cor = [F.face_holonomy(K, fi) for fi in F.corner_faces(K)]
        ok1 &= tri == {(0, 0, 0)} and len(cor) == 6 and all(h == (1, 1, 5) for h in cor)
        info1["k=%d" % k] = {"three-point faces: (sublattice, gauge, label) holonomies": sorted(tri), "corner faces": cor}
    check("1 for k = 2..12, the frame moves compose to nothing around every three-point face, and around each of the six two-point faces "
          "(the octahedron's corners) to a sublattice turn plus a complement, i.e. a label shift of -1 (label 5)", ok1, info1)

    # 2. flat states: one constant label developed over the sphere cut along six disjoint paths from z to the corners
    info2, ok2 = {}, True
    rng = random.Random(2026)
    for k, K in SP.items():
        G = F.gamma(K)
        adj = F.point_graph(K)
        cpts = {p for fi in F.corner_faces(K) for p in K["fpts"][fi]}
        zs = [p for p in range(K["n"]) if p not in cpts]
        zs = zs if len(zs) <= 15 else rng.sample(zs, 15)
        n_states = good = 0
        for z in zs:
            base = max(range(K["n"]), key=lambda p: (F.dist_from(adj, [z]).get(p, 0), -p))
            for star in (None, rng, rng):
                paths = F.cut_star(K, G, z, star)
                for zc in (0, 1):
                    x = F.flat_state(K, z, paths, base, zc)
                    v = F.violated(K, x)
                    n_states += 1
                    good += len(v) == 1 and z in K["lines"][v[0]]
        ok2 &= good == n_states
        info2["k=%d" % k] = {"points n": K["n"], "vortex positions": len(zs), "states (3 cut stars x 2 colours of z each)": n_states,
                             "exactly one violated line, through z": good}
    check("2 for k = 2..12, every tested point z (all non-corner points for k <= 3, 15 random ones otherwise), cut star (one shortest, "
          "two random) and colour of z: developing one constant label over the sphere cut along the star gives a state violating "
          "exactly one line, and that line passes through z", ok2, info2)

    # 3. local vortex steps
    info3, ok3 = {}, True
    rng = random.Random(7)
    for k in (8, 10, 12):
        K = SP[k]
        G = F.gamma(K)
        adj = F.point_graph(K)
        cpts = {p for fi in F.corner_faces(K) for p in K["fpts"][fi]}
        dc = F.dist_from(adj, list(cpts))
        far = [p for p in range(K["n"]) if dc[p] >= 4]
        zs = rng.sample(far, min(10, len(far)))
        for kind in ("shortest", "random"):
            tried = local = crowded = 0
            maxchg = 0
            for z in zs:
                paths = F.cut_star(K, G, z, None if kind == "shortest" else rng)
                dz = F.dist_from(adj, [z])
                base = max(range(K["n"]), key=lambda p: (dz[p], -p))
                x = F.flat_state(K, z, paths, base)
                for z2 in sorted(adj[z]):
                    res = F.vortex_step(K, G, adj, z, paths, z2, 3, rng)
                    tried += 1
                    if res is None:
                        crowded += 1
                        continue
                    p2, ball = res
                    y = F.flat_state(K, z2, p2, base)
                    v = F.violated(K, y)
                    chg = {p for p in range(K["n"]) if x[p] != y[p] and p not in (z, z2)}
                    local += len(v) == 1 and z2 in K["lines"][v[0]] and chg <= ball
                    maxchg = max(maxchg, len(chg))
            ok3 &= local == tried - crowded and (kind == "random" or crowded == 0)
            info3["k=%d, %s stars" % (k, kind)] = {"steps to an adjacent point": tried, "re-routed inside radius 3, valid, all changes "
                                                   "inside the ball": local, "no re-routing inside the ball (crowded star)": crowded,
                                                   "most points changed": maxchg}
    check("3 local vortex steps: from a flat state whose vortex is at distance >= 4 from the corners and whose cut star is shortest, the vortex moves to each of its six neighbours by re-routing "
          "the star inside the ball of radius 3 around it, the new state is again flat with its one violated line through the new point, "
          "and only points in the ball change colour; wandering (random) cut stars are tested the same way, a step counting as crowded when "
          "no re-routing inside the ball exists",
          ok3, info3)

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
