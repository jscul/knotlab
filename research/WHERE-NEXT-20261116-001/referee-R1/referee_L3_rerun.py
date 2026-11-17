"""How noisy is the study's single-draw L3 median? (supports task 2)

L3 is the thing under test, so it runs in the study's own engine (nae_engine.c via engine.py), with the
selected weights (policies.json). On the study's 100 test instances per cell:
  - once with the study's own run seed per instance, to check that test/results.jsonl is reproduced
    exactly (flips per instance);
  - REPS times with fresh referee seeds, to estimate L3's median with less run-to-run noise.
The study's engine is built into the referee's scratchpad (WHERE_NEXT_BUILD).

Usage: referee_L3_rerun.py N [N ...]
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
import time
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
os.environ["WHERE_NEXT_BUILD"] = str(Path("/tmp/claude-1000/-home-jscul-p-vs-np-contact-first/"
                                          "866db0bb-326b-5add-835e-78bf03179706/scratchpad/study_build"))
import numpy as np  # noqa: E402

import referee_common as C  # noqa: E402

E = C._study_engine
REPS = 5
_POL = {}


def study_seed(*parts) -> int:
    return int.from_bytes(hashlib.sha256("|".join(map(str, parts)).encode()).digest()[:8], "little")


def policy(arm):
    if arm not in _POL:
        P = json.loads((C.ART / "policies.json").read_text())[arm]
        _POL[arm] = (np.load(P["theta"]), int(P["flags"]), tuple(P["what_params"]))
    return _POL[arm]


def job(a):
    arm, fam, n, iseed, rep = a
    inst = E.planted(fam, n, C.ALPHA[fam], iseed)
    th, flags, wp = policy(arm)
    seed = study_seed("test", fam, n, iseed) if rep == "study" else C.seed_of("L3rerun", arm, fam, n, iseed, rep)
    r = E.run(inst, "policy", wp, theta=th, flags=flags, seed=seed, max_flips=C.CAP[(fam, n)], want_state=True)
    if r["solved"] and not inst.satisfied(r["state"].astype(np.int8)):
        raise RuntimeError("bad solution")
    return (arm, fam, n, iseed, rep, r["flips"], r["solved"], r["cpu"])


def main(ns, arms=("L3",)):
    t0 = time.time()
    E.lib()
    S = C.study_results()
    fam = "rand"
    jobs = [(arm, fam, n, C.TEST_SEED0[fam] + i, rep) for arm in arms for n in ns for i in range(100)
            for rep in ["study"] + list(range(REPS))]
    res = C.pool_map(job, jobs)
    out = {"task": "L3 re-run (study engine, the thing under test)", "reps": REPS, "cells": {}}
    for arm in arms:
        for n in ns:
            rows = [r for r in res if r[0] == arm and r[2] == n]
            st = S[(fam, n, arm)]
            same = sum(1 for r in rows if r[4] == "study" and st[r[3]][0] == r[5])
            fresh = {}
            for r in sorted((r for r in rows if r[4] != "study"), key=lambda r: (r[3], r[4])):
                fresh.setdefault(r[3], []).append(r[5])  # ordered by rep (imap_unordered returns short runs first)
            allf = np.concatenate([np.asarray(v, dtype=float) for v in fresh.values()])
            theirs = {k: [v[0]] for k, v in st.items()}
            per_rep = [float(np.median([fresh[k][j] for k in fresh])) for j in range(REPS)]
            cell = {"study_median": float(np.median([v[0] for v in st.values()])),
                    "study_seed_reproduced_instances": same, "instances": len(fresh),
                    "fresh_median_all": float(np.median(allf)), "fresh_runs": int(len(allf)),
                    "fresh_unsolved": int(sum(1 for r in rows if r[4] != "study" and not r[6])),
                    "fresh_median_per_rep": per_rep,
                    "fresh_over_study": C.median_ratio_boot(fresh, theirs),
                    "cpu_s": float(sum(r[7] for r in rows)),
                    "fresh_flips_by_instance": {str(k): v for k, v in sorted(fresh.items())}}
            out["cells"][f"{arm}|{fam}|{n}"] = cell
            print(arm, n, json.dumps({k: v for k, v in cell.items() if k != "fresh_flips_by_instance"}), flush=True)
    out["wall_s"] = time.time() - t0
    path = C.HERE / "referee_L3_rerun.json"
    if path.exists():
        prev = json.loads(path.read_text())
        prev["cells"].update(out["cells"])
        prev["wall_s"] = prev.get("wall_s", 0) + out["wall_s"]
        out = prev
    C.jdump(out, path)
    print("wall", time.time() - t0)


if __name__ == "__main__":
    args = sys.argv[1:]
    arms = ("L3",)
    if args and args[0].startswith("arms="):
        arms = tuple(args[0][5:].split(","))
        args = args[1:]
    main([int(x) for x in args], arms)
