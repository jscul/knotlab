#!/usr/bin/env python3
"""Checks for SPHERE-WIDTH-20261107-001B: grid Sperner needs resolution width Theta(m).

    python3 -B check.py          verify result.json against a fresh run
    python3 -B check.py --write  write result.json from a fresh run
Run with the repository's .venv (python-sat). Single process; a few minutes."""
import hashlib
import json
import random
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
import disk_lib as DL  # noqa: E402

W = DL.W
T0 = time.time()
OUT = {}


def check(name, ok, info):
    OUT[name] = {"pass": bool(ok), "info": info}
    print("PASS" if ok else "FAIL", name, json.dumps(info, default=str), round(time.time() - T0, 1), "s", flush=True)
    if not ok:
        sys.exit(1)


def dist(u, v):
    return max(abs(u[0] - v[0]), abs(u[1] - v[1]), abs(u[0] + u[1] - v[0] - v[1]))


def clustered(m, rng, inner):
    P = set()
    for _ in range(rng.randint(1, 3)):
        v = rng.choice(inner)
        for _ in range(rng.randint(3, 12)):
            P.add(v)
            v = rng.choice([u for u in inner if dist(u, v) == 1])
    return P


if __name__ == "__main__":
    manifest = json.loads((HERE / "manifest.json").read_text())
    bad = {q: dg for q, dg in manifest["parent_bindings"].items() if hashlib.sha256((ROOT / q).read_bytes()).hexdigest() != dg}
    status = {q: json.loads((ROOT / q).read_text()).get("status") for q in manifest["parent_bindings"]
              if q.endswith(".json") and q.startswith("proofs/")}
    check("0 dependency artifacts bound by hash; upstream proofs Proved", not bad and all(s in ("Proved", "passed") for s in status.values()),
          {"mismatched": bad, "statuses": status})

    # 1. certificates on the disk
    info1, ok1 = {}, True
    rng = random.Random(8)
    for m in (10, 12):
        V, tris, _ = W.grid(m)
        bc = W.boundary_colours(m)
        inner = [v for v in V if v not in bc]
        n_cert = n_struct = n_sep = n_bd = n_int = n_int_len = 0
        worst_ratio, worst_depth = 0.0, 0
        for trial in range(25):
            T0_, col = W.random_state(m, rng)
            P = clustered(m, rng, inner) - set(T0_)
            peb = {v: col[v] for v in P}
            peb.update(bc)
            free = [T for T in tris if not any(v in peb for v in T)]
            for T in rng.sample(free, min(8, len(free))):
                cert = DL.certificate(m, T, peb)
                if cert is None:
                    continue
                cyc, segs, walk = cert
                n_cert += 1
                neg = [sg for sg in segs if sg[4] < 0]
                # boundary features: adjacent boundary pebbles of different colours, or short boundary chords near the foot of T's ray
                foot_x = sum(W.pos(v)[0] for v in T) / 3.0 + 0.1
                near_foot = lambda v: v[1] <= 4 and abs(W.pos(v)[0] - foot_x) <= 5  # noqa: E731
                feature = lambda sg: sg[0] in bc and sg[1] in bc and (  # noqa: E731
                    (dist(sg[0], sg[1]) <= 1 and peb[sg[0]] != peb[sg[1]]) or (near_foot(sg[0]) and near_foot(sg[1])))
                struct = all(len(sg[2]) - 1 <= 4 and (sg[0] in P or sg[1] in P or feature(sg)) for sg in neg)
                n_struct += struct
                h0, h1 = DL.winding3(T0_, walk), DL.winding3(T, walk)
                n_sep += h0 != h1 or any(v in walk for v in T0_)
                if any(v in bc for v in cyc):
                    n_bd += 1
                    worst_depth = max(worst_depth, max(DL.depth(m, v) for v in walk))
                else:
                    n_int += 1
                    L, r = len(walk) - 1, len(cyc)
                    n_int_len += L <= 2 * r - 3 + abs(h1)
                    worst_ratio = max(worst_ratio, L / r)
        ok1 &= n_cert > 0 and n_struct == n_cert and n_sep == n_cert and n_int_len == n_int
        info1["m=%d" % m] = {"certificates (feasible at the state's triangle, not at T)": n_cert,
                             "negative terms only at segments of length <= 4 that touch a Spoiler pebble or a boundary feature (a colour "
                             "change, or a chord near the foot of the ray)": n_struct,
                             "walk winds differently around the two triangles (or meets the old one)": n_sep,
                             "through boundary pebbles": n_bd, "deepest vertex of those walks": worst_depth,
                             "pure Spoiler walks": n_int, "of which length <= 2r - 3 + |H|": n_int_len,
                             "largest length / pebbles (pure walks)": round(worst_ratio, 2)}
    check("1 certificates on the Sperner disk: every obstruction's negative terms come from segments of length at most 4 that touch a "
          "Spoiler pebble or a boundary feature (a colour change, or a chord near the foot of the trivializing ray), its walk separates the two triangles, and walks avoiding the boundary "
          "satisfy length <= 2r - 3 + |H|", ok1, info1)

    # 2. locality on the disk
    info2, ok2 = {}, True
    m = 18
    V, tris, _ = W.grid(m)
    bc = W.boundary_colours(m)
    chain = [(3 + i, 3) for i in range(12)]
    for omega in (0, 1, 2, 3, 4, 5, 6):
        cols, c = [], 2
        for i in range(len(chain)):
            cols.append(c)
            if i < omega:
                c = (c + 1) % 3
        peb = dict(zip(chain, cols))
        peb.update(bc)
        free = [T for T in tris if not any(v in peb for v in T)]
        feas = [T for T in free if W.feasible_by_window(m, T, peb)]
        blocked = [T for T in free if T not in feas]
        far_blocked = sum(1 for T in blocked if min(dist(v, p) for v in T for p in chain) >= 4)
        info2["chain of 12, net winding %d" % omega] = {"feasible": len(feas), "blocked": len(blocked),
                                                        "blocked at distance >= 4 from the chain": far_blocked}
        ok2 &= (far_blocked == 0) if omega <= 4 else (len(feas) == 0)
    check("2 locality on the disk (m = 18): a chain of 12 pebbles whose colours advance omega times blocks only triangles within distance 3 "
          "of it for omega <= 4, and for omega >= 5 its colours fit no single-full-triangle state at all, so consistent answers never "
          "produce it", ok2, info2)

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
