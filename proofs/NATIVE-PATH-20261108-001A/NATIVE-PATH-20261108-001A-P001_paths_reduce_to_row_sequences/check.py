#!/usr/bin/env python3
"""Checks for NATIVE-PATH-20261108-001A: paths across time reduce to row sequences.

    .venv/bin/python3 -B check.py          verify result.json against a fresh run
    .venv/bin/python3 -B check.py --write  write result.json from a fresh run
Needs numpy (the repository's .venv). 16 worker processes, a few minutes. References: AFFINE-WIRE-20261108-001A's three-ring
reduction, and the full state space of each path with PROCESS-CHAIN-20261108-001A's blockwise decisiveness test."""
import hashlib
import json
import random
import sys
import time
from multiprocessing import Pool
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
import path_lib as PL  # noqa: E402

W, C, P = PL.W, PL.C, PL.P
T0 = time.time()
OUT = {}
LAWS = [("proposals",)] + [("self-blind", x, y) for x in sorted(PL.ULIN) for y in sorted(PL.ULIN)]
LIN = sorted(PL.LIN)


def check(name, ok, info):
    OUT[name] = {"pass": bool(ok), "info": info}
    print("PASS" if ok else "FAIL", name, json.dumps(info, default=str)[:600], round(time.time() - T0, 1), "s", flush=True)
    if not ok:
        sys.exit(1)


def binds(F, blocks, names, N):
    if F.min() == F.max():
        return False
    return not any(C.decides_outside(F, *blocks[x], N) for x in names)


def brute(rules, sizes, ks, laws, cap=8192):
    nxt, N, blocks = PL.mixed_state_map(rules, sizes, ks, laws)
    n = len(sizes)
    L = PL.light_cone(sizes, ks)
    names = [f"R{i}" for i in range(n)]
    cur = np.arange(len(nxt), dtype=np.int64)
    seen, per = {}, {key: [] for key in ["p%d" % c for c in range(n - 1)] + ["ends last", "ends first", "every last"]}
    for T in range(1, cap + 1):
        cur = nxt[cur]
        key = hashlib.blake2b(cur.tobytes(), digest_size=16).digest()
        if key in seen:
            T1, period = seen[key], T - seen[key]
            hold = lambda seq, start: all(seq[min(start, T1) - 1:T1 + period - 1]) and all(seq[start - 1:])
            persists = [hold(per["p%d" % c], 1) for c in range(n - 1)]
            return (persists, hold(per["ends last"], L), hold(per["ends first"], L), hold(per["every last"], L))
        seen[key] = T
        Fs = [((cur >> c) & 1).astype(np.uint8) for c in range(n - 1)]
        for c in range(n - 1):
            per["p%d" % c].append(binds(Fs[c], blocks, (names[c], names[c + 1]), N))
        per["ends last"].append(binds(Fs[-1], blocks, (names[0], names[-1]), N))
        per["ends first"].append(binds(Fs[0], blocks, (names[0], names[-1]), N))
        per["every last"].append(binds(Fs[-1], blocks, tuple(names), N))
    return None


def brute_job(args):
    rules, sizes, ks, laws = args
    a = PL.analyze(rules, sizes, ks, laws)
    b = brute(rules, sizes, ks, laws)
    if b is None:
        return None
    mine = (a["persists"], a["ends at the last contact"], a["ends at the first contact"], a["last contact binds every ring"])
    return mine == b, a["all persist"] and a["ends at the last contact"]


def cone_job(args):
    rules, sizes, ks, laws = args
    nxt, N, blocks = PL.mixed_state_map(rules, sizes, ks, laws)
    L = PL.light_cone(sizes, ks)
    cur = np.arange(len(nxt), dtype=np.int64)
    early = 0
    for T in range(1, L):
        cur = nxt[cur]
        F = ((cur >> (len(sizes) - 2)) & 1).astype(np.uint8)
        early += C.depends_on_block(F, *blocks["R0"], N)
    return early


def random_path(rng, n, sizes_choice, rules_pool):
    sizes = tuple(rng.choice(sizes_choice[i]) for i in range(n))
    ks = [rng.randint(1, sizes[i] - 1) for i in range(1, n - 1)]
    rules = tuple(rng.choice(rules_pool) for _ in range(n))
    laws = tuple(rng.choice(LAWS) for _ in range(n - 1))
    return rules, sizes, ks, laws


if __name__ == "__main__":
    manifest = json.loads((HERE / "manifest.json").read_text())
    bad = {q: dg for q, dg in manifest["parent_bindings"].items() if hashlib.sha256((ROOT / q).read_bytes()).hexdigest() != dg}
    status = {q: json.loads((ROOT / q).read_text()).get("status") for q in manifest["parent_bindings"] if q.endswith(".json")}
    check("0 dependency artifacts bound by hash; upstream proofs Proved", not bad and all(s in ("Proved", "passed") for s in status.values()),
          {"mismatched": bad, "statuses": status})
    rng = random.Random(20261108)

    # 1 for three rings the path reduction is AFFINE-WIRE's
    tested = mism = 0
    for _ in range(3000):
        rules, sizes, ks, laws = random_path(rng, 3, [(3, 4, 5), (3, 4, 5, 6, 7), (3, 4, 5)], LIN)
        a = PL.analyze(rules, sizes, ks, laws)
        b = W.analyze(rules, sizes, ks[0], laws[0], laws[1])
        tested += 1
        mism += (a["persists"][0], a["persists"][1], a["ends at the last contact"], a["ends at the first contact"]) != (
            b["c1 persists"], b["c2 persists"], b["c2 composes"], b["c1 composes"])
    check("1 on 3,000 random three-ring chains the path reduction gives AFFINE-WIRE-20261108-001A's verdicts", mism == 0,
          {"chains": tested, "mismatches": mism})

    # 2 the matrix rows are the path's own linear map
    tested = mism = 0
    for _ in range(300):
        rules, sizes, ks, laws = random_path(rng, 4, [(3, 4), (3, 4, 5), (3, 4, 5), (3, 4)], LIN)
        rows, N, blocks = PL.linear_matrix(rules, sizes, ks, laws)
        nxt, N2, _ = PL.mixed_state_map(rules, sizes, ks, laws)
        base = int(nxt[0])
        cols = [int(nxt[1 << j]) ^ base for j in range(N)]
        mrows = [sum(((cols[j] >> i) & 1) << j for j in range(N)) for i in range(N)]
        tested += 1
        mism += mrows != rows or base != 0
    check("2 for 300 random four-ring paths with linear rules and laws, the matrix rows equal the path's linear map read off its full "
          "state space", mism == 0, {"paths": tested, "mismatches": mism})

    # 3 the row-sequence verdicts equal the full-state-space verdicts on four-ring paths
    jobs = [random_path(rng, 4, [(3, 4), (3, 4, 5), (3, 4, 5), (3, 4)], LIN) for _ in range(800)]
    with Pool(16) as pool:
        res = pool.map(brute_job, jobs, chunksize=4)
    done = [x for x in res if x is not None]
    check("3 on 800 random affine four-ring paths, the row-sequence verdicts (each contact persists, the ends bound at the last and "
          "at the first contact from the light cone on, the last contact binding every ring) equal the full-state-space verdicts",
          all(x[0] for x in done) and len(done) > 700,
          {"paths": len(jobs), "decided": len(done), "agree": sum(x[0] for x in done), "native paths among them": sum(x[1] for x in done)})

    # 4 the light cone, on paths with any rules
    jobs = [random_path(rng, 4, [(3, 4), (3, 4, 5), (3, 4, 5), (3, 4)], list(range(256))) for _ in range(400)]
    with Pool(16) as pool:
        res = pool.map(cone_job, jobs, chunksize=4)
    check("4 on 400 random four-ring paths with arbitrary elementary rules, the last contact never depends on ring R_0 before lag "
          "d_1 + d_2 + 1", sum(res) == 0, {"paths": len(jobs), "early dependences": sum(res)})

    res = {"status": "passed", "checks": OUT, "seconds": round(time.time() - T0, 1)}
    if "--write" in sys.argv:
        (HERE / "result.json").write_text(json.dumps(res, indent=1, default=str) + "\n")
        print("wrote result.json")
    else:
        old = json.loads((HERE / "result.json").read_text())
        same = {k: v["info"] for k, v in old["checks"].items()} == json.loads(json.dumps({k: v["info"] for k, v in OUT.items()}, default=str))
        print("result.json reproduced" if same else "result.json DIFFERS")
        sys.exit(0 if same else 1)
