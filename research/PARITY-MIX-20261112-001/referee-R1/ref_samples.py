#!/usr/bin/env python3
"""Referee PARITY-MIX-R1, the frozen samples on 6 x 6 and 8 x 8 regenerated (random.Random("PARITY-MIX|n|n|k|s"), rng.sample of the
n * n cells, as frozen: k = 0, 3, ..., 36 with 20 each on 6 x 6; k = 0, 4, ..., 64 with 10 each on 8 x 8), re-read with the referee's
lighter encoding (ref_parity_fast.py, ref_parity_enum.py): survival, and for survivors the fixing measures and their sources.
Also, for the kind sets whose stitch holds flip-blind triples (ref_fb.py), every 4 x 4 placement (one state check per translation class,
every member of a surviving class analysed).

    python3 -B ref_samples.py p6|p8 [workers]     (result_p6.jsonl / result_p8.jsonl)
    python3 -B ref_samples.py alt4 [workers]      (result_alt4.jsonl)"""
import json
import random
import sys
import time
from multiprocessing import Pool
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import ref_parity as RP  # noqa: E402
import ref_parity_fast as F  # noqa: E402
import ref_parity_enum as E  # noqa: E402
from pysat.solvers import Glucose4  # noqa: E402

SAMPLED = {"p6": (6, list(range(0, 37, 3)), 20), "p8": (8, list(range(0, 65, 4)), 10)}
ALT = [{"orbits": ["0011", "01"], "P": 4, "kinds": [[1, 3], [5, 6]]},
       {"orbits": ["000000111111", "0011", "01"], "P": 12, "kinds": [[1, 6], [2, 7], [6, 7]]}]


def sample_job(arg):
    part, i = arg
    n, ks, N = SAMPLED[part]
    st = RP.setup(RP.hs()[i])
    func = RP.census(st)["functional slots"]
    rows = []
    t0 = time.time()
    for k in ks:
        for s in range(N):
            rng = random.Random("%s|%d|%d|%d|%d" % ("PARITY-MIX", n, n, k, s))
            K = frozenset(rng.sample(list(range(n * n)), k))
            with Glucose4(bootstrap_with=F.light_cnf(st, n, K)) as sv:
                alive = sv.solve()
            row = {"k": k, "sample": s, "state": alive}
            if alive and 0 < k < n * n:
                row = {"sample": s, **E.analyse_light(st, n, K, func, alive)}
            rows.append(row)
    return {"i": i, "harmony": st["name"], "n": n, "rows": rows, "seconds": round(time.time() - t0, 1)}


def alt_job(h):
    st = RP.setup(h)
    func = RP.census(st)["functional slots"]
    rows = []
    t0 = time.time()
    for orb in RP.classes(4, 4):
        alive = RP.solve(RP.Arr(st, 4, 4, orb[0]).cl)
        for K in orb:
            rows.append({"cells": sorted(K), **RP.analyse(st, 4, 4, K, func)} if alive else {"cells": sorted(K), "k": len(K), "state": False})
    return {"harmony": st["name"], "kinds": h["kinds"], "n": 4, "rows": rows, "seconds": round(time.time() - t0, 1)}


def main():
    part = sys.argv[1]
    workers = int(sys.argv[2]) if len(sys.argv) > 2 else 4
    t0 = time.time()
    out = HERE / f"result_{part}.jsonl"
    if part in SAMPLED:
        census = json.loads((HERE / "result_census.json").read_text())["rows"]
        args = [(part, i) for i, r in enumerate(census) if r["flip-blind triples"]]
        fn = sample_job
    else:
        args, fn = ALT, alt_job
    with Pool(workers) as pool:
        for res in pool.imap_unordered(fn, args):
            with open(out, "a") as fh:
                fh.write(json.dumps(res) + "\n")
            print(res["harmony"][:50], len(res["rows"]), sum(1 for r in res["rows"] if r["state"]), res["seconds"], "s", flush=True)
    print("done", round(time.time() - t0, 1), "s")


if __name__ == "__main__":
    main()
