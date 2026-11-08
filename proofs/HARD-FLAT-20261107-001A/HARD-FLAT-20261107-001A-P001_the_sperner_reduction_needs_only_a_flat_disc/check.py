#!/usr/bin/env python3
"""Checks for HARD-FLAT-20261107-001A: the Sperner reduction needs only a flat disc.

    python3 -B check.py          verify result.json against a fresh run
    python3 -B check.py --write  write result.json from a fresh run
Run with the repository's .venv (pysat, numpy, networkx). Single process; a few minutes."""
import hashlib
import json
import math
import random
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
import flatdisc_lib as FD  # noqa: E402
SM, GL = FD.SM, FD.GL

T0 = time.time()
OUT = {}


def check(name, ok, info):
    OUT[name] = {"pass": bool(ok), "info": info}
    print("PASS" if ok else "FAIL", name, json.dumps(info, default=str)[:600], round(time.time() - T0, 1), "s", flush=True)
    if not ok:
        sys.exit(1)


def spheres(rng, grown_count, min_tris):
    out = [("K_%d" % m, SM.octahedral(m)) for m in (4, 6, 8, 10)]
    out += [("T(%d,%d,%d)" % p, SM.tube(*p)) for p in ((3, 12, 0), (4, 16, 1), (3, 30, 0), (5, 20, 0))]
    got = 0
    while got < grown_count:
        G, why = GL.grow(lambda r, G, cv: [v for v in cv if rng.random() < 0.12], maxrings=60)
        if why == "closed":
            S = SM.from_triangles("g", G.tris)
            if S.nt >= min_tris and not GL.is_K(S):
                out.append(("grown%d" % S.nt, S))
                got += 1
    return out


if __name__ == "__main__":
    manifest = json.loads((HERE / "manifest.json").read_text())
    bad = {q: dg for q, dg in manifest["parent_bindings"].items() if hashlib.sha256((ROOT / q).read_bytes()).hexdigest() != dg}
    status = {q: json.loads((ROOT / q).read_text()).get("status") for q in manifest["parent_bindings"]
              if q.endswith(".json") and q.startswith("proofs/")}
    check("0 dependency artifacts bound by hash; upstream proofs Proved", not bad and all(s in ("Proved", "passed") for s in status.values()),
          {"mismatched": bad, "statuses": status})

    rng = random.Random(20261107)
    cases = spheres(rng, 8, 100)
    datas = {name: FD.build_general(S) for name, S in cases}

    # 1 holonomy: flat at three-point faces, label shift 5 (-1) at the six digons, on every sphere
    rows, ok = [], True
    for name, S in cases:
        h = FD.holonomies(datas[name])
        rows.append([name, datas[name]["n"], h])
        ok &= h == {2: [5], 3: [0]} and len(FD.F.corner_faces(datas[name])) == 6
    check("1 on every sphere tested the frames are flat at three-point faces and have label holonomy -1 at each of the six digons",
          ok, {"[sphere, points, {face size: holonomies}]": rows})

    # 2 flat states: exactly one violated line, through the vortex, wherever a cut star exists
    rows, ok = [], True
    for name, S in cases:
        fs = FD.flat_states(datas[name], rng, 6)
        good = all(len(v) == 1 and all(z in datas[name]["lines"][l] for l in v) for z, v in fs)
        rows.append([name, len(fs), good])
        ok &= good and len(fs) > 0
    check("2 flat states: with a cut star from a random vortex, exactly one line is violated and it passes through the vortex", ok,
          {"[sphere, flat states built, all with one violated line at the vortex]": rows})

    # 3 flat radius, elimination width and the cut paths from the rim of the largest flat disc
    rows, ok, thin = [], True, []
    for name, S in cases:
        D = datas[name]
        K, s = SM.kasteleyn(S)
        w = SM.elimination_width(S, K)
        r, v = FD.flat_radius(S)
        rp = FD.rim_paths(D, v, r, rng) if r >= 2 else None
        rows.append([name, K.n, r, round(r / math.sqrt(K.n), 2), w, round(w / math.sqrt(K.n), 2), rp])
        if r >= 2 and not name.startswith("T("):
            ok &= rp is True
        if name.startswith("T(3,"):
            thin.append(rp)
    grown = [x[3] for x in rows if x[0].startswith("grown")]
    check("3 on K_m and on every grown sphere the rim of the largest flat disc (radius at least 2) reaches the six corners by disjoint "
          "cut paths; on the thin tubes of circumference 9 the largest disc reaches around the band and its paths fail",
          ok and thin and not any(thin),
          {"[sphere, points, flat radius, r/sqrt(n), elimination width, w/sqrt(n), cut paths]": rows,
           "grown r/sqrt(n) range": [min(grown), max(grown)]})

    out = {"status": "passed", "checks": OUT}
    res_path = HERE / "result.json"
    if "--write" in sys.argv:
        res_path.write_text(json.dumps(out, indent=1, default=str) + "\n")
        print("wrote", res_path)
    else:
        old = json.loads(res_path.read_text())
        same = json.loads(json.dumps(out, default=str))["checks"] == old["checks"]
        print("result.json reproduced" if same else "result.json DIFFERS")
        sys.exit(0 if same else 1)
