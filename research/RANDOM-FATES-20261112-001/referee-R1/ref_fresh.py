#!/usr/bin/env python3
"""Referee RANDOM-FATES-R1: P4's outcomes and the uniform end density on FRESH seeds (seed tag "referee" instead of "grow"), with the
referee's generators and solver: 100 growths per setting to 2,000 moves, 100 uniform growths at n = 50, 100, 200. Writes
result_fresh.json with each setting's share still a base and a 95% Wilson interval, beside the census's share."""
import json
import math
import sys
from multiprocessing import Pool
from pathlib import Path

import ref_fates as F
from ref_regen import LABS, A

HERE = Path(__file__).resolve().parent


def job(spec):
    lab, run = spec
    knots, dead = F.grow(lab, run, seed_tag="referee")
    return {"label": lab, "run": run, "dead": dead, "knots": len(knots)}


def wilson(k, n, z=1.96):
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return [round(c - h, 3), round(c + h, 3)]


if __name__ == "__main__":
    specs = [(l, r) for l in LABS for r in range(100)] + [(f"U{n}", r) for n in (50, 100, 200) for r in range(100)]
    with Pool(int(sys.argv[1]) if len(sys.argv) > 1 else 4) as pool:
        rows = pool.map(job, specs, chunksize=4)
    census = {}
    for r in map(json.loads, open(A / "runs.jsonl")):
        census.setdefault(r["label"], []).append(r)
    out = {}
    for l in LABS:
        mine = [r for r in rows if r["label"] == l]
        alive = sum(not r["dead"] for r in mine)
        c = census[l]
        ca = sum(not r["dead"] for r in c)
        out[l] = {"fresh alive": alive, "fresh runs": len(mine), "fresh 95% interval": wilson(alive, len(mine)),
                  "census alive share": ca / len(c), "census inside the fresh interval": wilson(alive, len(mine))[0] <= ca / len(c) <= wilson(alive, len(mine))[1]}
    for n in (50, 100, 200):
        dens = sorted(r["knots"] / n for r in rows if r["label"] == f"U{n}")
        out[f"U{n}"] = {"fresh median density": dens[len(dens) // 2], "fresh q10, q90": [dens[len(dens) // 10], dens[9 * len(dens) // 10]],
                        "census median density": sorted(r["density"] for r in census[f"U{n}"])[len(census[f"U{n}"]) // 2]}
    (HERE / "result_fresh.json").write_text(json.dumps(out, indent=1) + "\n")
    print("wrote result_fresh.json")
