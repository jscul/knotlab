"""Referee R1 for SPEC-MERGE-20261117-001: rerun every solved test run that made a speculative merge, and check its state.

  .venv/bin/python -B referee_verify.py > referee_verify.json

For every run of A0, AE, A, Aloc and their random-pair controls that the study stored as solved with at least one merge, the
study's driver is rerun from the same seeds with debug=True. The rerun must reproduce the stored flips, charged work and merge
count, and the state it reports is checked here, with the referee's own test, on freshly generated original knots (every knot
has its three members not all equal). The planted state is also checked to satisfy every knot.
"""
from __future__ import annotations

import json
import sys
from multiprocessing import Pool
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
EXP = ROOT / "experiments/SPEC-MERGE-20261117-001A/SPEC-MERGE-20261117-001A-E001_spec_merge"
ART = ROOT / "artifacts/SPEC-MERGE-20261117-001A/SPEC-MERGE-20261117-001A-E001_spec_merge"
sys.path.insert(0, str(EXP))
ARMS = ("A0", "Arand0", "AE", "AErand", "A", "Arand", "Aloc", "Arandloc")


def nae_ok(knots, x):
    s = x[knots].astype(np.int64).sum(axis=1)
    return bool(np.all((s == 1) | (s == 2)))


def todo():
    out = []
    for part in ("test_fixed", "test_tuned"):
        for line in open(ART / part / "results.jsonl"):
            r = json.loads(line)
            res = r["result"]
            if res["arm"] not in ARMS:
                continue
            i = int(r["case"].split("|")[-1])
            for k, x in enumerate(res["runs"]):
                if x["solved"] and x["merges"] > 0 and x["cpu"] < 30:
                    out.append((res["cell"], res["arm"], i, k, x["flips"], x["work"], x["merges"]))
    return out


def one(t):
    cell, arm, i, k, flips, work, merges = t
    import job
    import slow_loop as S
    import spec_merge as M
    job.setup({"stage": "test"})
    pols = json.loads((ART / "policies.json").read_text())
    _, fam, a, w, n, cap, _ = job.CELL[cell]
    seed = job.SEED_TEST + i
    inst = S.planted(fam, n, a, seed, w=w)
    pol = {"A0": job.A0, "Arand0": job.A0, "AE": job.AE, "AErand": job.AE, "A": pols["A"], "Arand": pols["A"],
           "Aloc": pols["Aloc"], "Arandloc": pols["Aloc"]}[arm]
    mode = "random" if arm in ("Arand0", "AErand", "Arand", "Arandloc") else "coflip"
    res = M.run_spec(inst, job.NOV, S.run_seed("test", cell, seed, k), cap, pol, mode=mode, debug=True)
    knots = np.array(inst.knots, dtype=np.int64)
    return {"cell": cell, "arm": arm, "i": i, "run": k, "same": [res["flips"] == flips, res["work"] == work,
                                                              res["merges"] == merges],
            "solved": res["solved"], "state_ok": nae_ok(knots, np.asarray(res["state"], np.uint8)),
            "planted_ok": nae_ok(knots, inst.hidden.astype(np.uint8)), "n_final": res["n_final"]}


if __name__ == "__main__":
    jobs = todo()
    with Pool(4) as p:
        rs = p.map(one, jobs, chunksize=4)
    summ = {"runs": len(rs), "reproduced_all_three": sum(all(r["same"]) for r in rs),
            "solved_on_rerun": sum(r["solved"] for r in rs), "state_satisfies_every_knot": sum(r["state_ok"] for r in rs),
            "planted_ok": sum(r["planted_ok"] for r in rs), "by_cell_arm": {}}
    for r in rs:
        key = f"{r['cell']}|{r['arm']}"
        d = summ["by_cell_arm"].setdefault(key, [0, 0])
        d[0] += 1
        d[1] += r["state_ok"] and all(r["same"])
    summ["mismatches"] = [r for r in rs if not (all(r["same"]) and r["state_ok"] and r["solved"])][:20]
    print(json.dumps(summ, indent=1))
