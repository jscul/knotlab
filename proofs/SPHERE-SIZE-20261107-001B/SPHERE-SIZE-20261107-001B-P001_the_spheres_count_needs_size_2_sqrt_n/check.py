#!/usr/bin/env python3
"""Checks for SPHERE-SIZE-20261107-001B: the sphere's count needs resolution size 2^Theta(sqrt n).

    python3 -B check.py          verify result.json against a fresh run
    python3 -B check.py --write  write result.json from a fresh run
Run with the repository's .venv. Single process; a few minutes."""
import hashlib
import json
import math
import random
import sys
import time
from functools import lru_cache
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
import packing_lib as P  # noqa: E402

W = P.W
T0 = time.time()
OUT = {}


def check(name, ok, info):
    OUT[name] = {"pass": bool(ok), "info": info}
    print("PASS" if ok else "FAIL", name, json.dumps(info, default=str), round(time.time() - T0, 1), "s", flush=True)
    if not ok:
        sys.exit(1)


def ball_size(R):
    """points within distance R in the bulk triangular lattice (the largest a ball can be on K_k)"""
    return 3 * R * R + 3 * R + 1


if __name__ == "__main__":
    manifest = json.loads((HERE / "manifest.json").read_text())
    bad = {q: dg for q, dg in manifest["parent_bindings"].items() if hashlib.sha256((ROOT / q).read_bytes()).hexdigest() != dg}
    status = {q: json.loads((ROOT / q).read_text()).get("status") for q in manifest["parent_bindings"]
              if q.endswith(".json") and q.startswith("proofs/")}
    check("0 dependency artifacts bound by hash; upstream proofs Proved", not bad and all(s in ("Proved", "passed") for s in status.values()),
          {"mismatched": bad, "statuses": status})

    # 1. the hard-core packing: separation and coverage (formula against Monte Carlo)
    info1, ok1 = {}, True
    rng = random.Random(1)
    for k, s, dsep, trials in ((16, 1, 6, 2000), (20, 2, 6, 1500)):
        K = W.sphere(k)
        cache = lru_cache(maxsize=None)(lambda p, K=K: W.bfs(K["adj"], [p], K["n"]))
        eps = 1.0 / ball_size(2 * s + dsep)
        dcor = W.bfs(K["adj"], list(K["corner_pts"]), K["n"])
        pts = rng.sample([p for p in range(K["n"]) if dcor[p] > 2 * s + 4], 4)
        est, sep = P.sample_coverage(K, s, dsep, eps, rng, trials, pts)
        rows = []
        for p in pts:
            f = P.coverage_bound(K, s, dsep, eps, p, cache)
            sd = math.sqrt(f * (1 - f) / trials)
            rows.append({"formula (lower bound)": round(f, 4), "Monte Carlo": round(est[p], 4), "at least the bound, within 4 sd": est[p] >= f - 4 * sd})
        ok1 &= (sep is None or sep >= dsep) and all(r["at least the bound, within 4 sd"] for r in rows)
        info1["k=%d, s=%d, separation %d, eps=1/%d" % (k, s, dsep, ball_size(2 * s + dsep))] = {
            "packings": trials, "smallest separation seen": sep, "coverage per point": rows}
    check("1 the hard-core packing keeps islands at least the separation apart, and each point's coverage probability is at least "
          "sum_c eps (1 - eps)^(|B(c, 2s + d_sep)| - 1) (Monte Carlo, within 4 standard deviations; the formula counts every nearby point "
          "as a competitor, so it is a lower bound, exact when all of them may propose)", ok1, info1)

    # 2. the constants of the size bound at the proof's parameters (s = 1, separation 17)
    s, dsep = 1, 17
    M = ball_size(2 * s + dsep)
    eps = 1.0 / M
    p_fixed = ball_size(s) * eps * (1 - eps) ** (M - 1)       # coverage lower bound for points away from the corners
    q = p_fixed / 2                                            # ... and the literal is satisfied (uniform colour)
    R_ind = 2 * (3 * s + dsep)                                 # events farther apart than this are independent
    V = ball_size(R_ind)
    per_literal_bits = -math.log2(1 - q) / V                   # survival <= 2^(-per_literal_bits * (W - N_c))
    info2 = {"island radius s": s, "separation": dsep, "proposal probability eps": "1/%d" % M,
             "coverage lower bound p": round(p_fixed, 6), "literal satisfied with probability at least": round(q, 6),
             "independence distance": R_ind, "points per independence ball V": V,
             "survival exponent per wide-clause literal (bits)": "%.3g" % per_literal_bits,
             "size bound": "S >= 2^(%.3g (c(1) k - 1 - N_c))" % per_literal_bits}
    check("2 the constants at the proof's parameters (s = 1, separation 17): coverage probability, literal probability, independence "
          "distance and the resulting size exponent, S >= 2^(alpha (c(1) k - 1 - N_c)) with alpha > 0 absolute", per_literal_bits > 0,
          info2)

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
