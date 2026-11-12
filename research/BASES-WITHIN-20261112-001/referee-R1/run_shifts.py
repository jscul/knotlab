#!/usr/bin/env python3
"""Referee BASES-WITHIN-R1, E2 (shifted stitches), with the referee's own code.

    REF_SHIFTS_EXE=<built shifts.c> python3 -B run_shifts.py --part sample|exhaustive|fano

sample:     the author's 60 sampled assignments per pair, regenerated from the pre-registered seeding (random.Random(1000 n + 7),
            (0, s, t) per knot, patterns in order; every (0, s, t) with s, t in {0, 1} for the alternation), each decided by
            shifts.c; per-pattern counts compared with result_offsets.json.
exhaustive: every gauge class of shifts (each row shifted, each knot's place shifted; the classes all have the same size, so
            shares of classes are shares of assignments) for every harmony against every living outer pattern (the 31 connected
            ones and the Fano plane less one knot).
fano:       the same for the Fano plane (dead under not-all-equal), for every harmony with P <= 12 (fano8: P <= 8)."""
import json
import random
import sys
import time
from multiprocessing import Pool
from pathlib import Path

import ref_lib as R
import ref_shifts as S

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
AUTHOR = ROOT / "proofs/BASES-WITHIN-20261112-001A/BASES-WITHIN-20261112-001A-P001_inner_series/result_offsets.json"
PATS = R.outer_patterns() + [(7, R.FANO[:-1]), (7, R.FANO)]


def sample_job(i):
    import itertools
    h = R.harmonies()[i]
    P = h["P"]
    rng = random.Random(1000 * i + 7)
    out = []
    for n, E in PATS:
        if P == 2:
            A = [tuple((0, s, t) for (s, t) in c) for c in itertools.product([(0, 0), (0, 1), (1, 0), (1, 1)], repeat=len(E))]
        else:
            A = [tuple((0, rng.randrange(P), rng.randrange(P)) for _ in E) for _ in range(60)]
        live = S.listed(h, n, E, A)
        O = len(R.outer_states(n, E)) > 0
        out.append({"outer": [n, [list(e) for e in E]], "outer lives": O, "assignments": len(A), "lived": sum(live),
                    "ended while the outer lives": (len(A) - sum(live)) if O else 0})
    return {"i": i, "orbits": h["orbits"], "P": P, "patterns": out}


def exhaustive_job(i, fano=False):
    h = R.harmonies()[i]
    out = []
    pats = [(7, R.FANO)] if fano else PATS[:-1]
    for n, E in pats:
        t = time.time()
        r = S.exhaustive(h, n, E)
        r.update({"outer": [n, [list(e) for e in E]], "outer lives": len(R.outer_states(n, E)) > 0,
                  "seconds": round(time.time() - t, 2)})
        out.append(r)
    return {"i": i, "orbits": h["orbits"], "P": h["P"], "states": len(R.states(h)), "patterns": out}


def fano_job(i):
    return exhaustive_job(i, fano=True)


def main():
    part = sys.argv[sys.argv.index("--part") + 1]
    hs = R.harmonies()
    t0 = time.time()
    if part == "sample":
        with Pool(8) as pool:
            rows = pool.map(sample_job, range(len(hs)), chunksize=1)
        theirs = json.loads(AUTHOR.read_text())["checks"]["result"]["rows"]
        diffs = []
        for mine, th in zip(rows, theirs):
            assert mine["orbits"] == th["orbits"]
            for a, b in zip(mine["patterns"], th["patterns"]):
                assert [list(map(list, b["outer"][1]))] == [a["outer"][1]]
                if (a["lived"], a["ended while the outer lives"]) != (b["lived"], b["ended while the outer lives"]):
                    diffs.append([mine["orbits"], a["outer"], a["lived"], b["lived"]])
        res = {"rows": rows, "pairs compared": sum(len(r["patterns"]) for r in rows), "differences from the author": diffs}
    elif part == "exhaustive":
        with Pool(8) as pool:
            rows = pool.map(exhaustive_job, sorted(range(len(hs)), key=lambda i: -hs[i]["P"]), chunksize=1)
        res = {"rows": sorted(rows, key=lambda r: r["i"])}
    elif part.startswith("fano"):
        maxp = int(part[4:]) if part[4:] else 12
        idx = [i for i, h in enumerate(hs) if h["P"] <= maxp]
        with Pool(8) as pool:
            rows = pool.map(fano_job, sorted(idx, key=lambda i: -hs[i]["P"]), chunksize=1)
        res = {"rows": sorted(rows, key=lambda r: r["i"])}
    res["seconds"] = round(time.time() - t0, 1)
    (HERE / f"result_{part}.json").write_text(json.dumps(res, indent=1) + "\n")
    print("wrote", part, res["seconds"], "s")


if __name__ == "__main__":
    main()
