"""Referee R1 for SPEC-MERGE-20261117-001: which check undid each round, the contradiction check or the stall test?

  .venv/bin/python -B referee_undo.py > referee_undo.json

The stored runs count contradiction undos and stall undos per run, but the round log does not say which undid which round, and a
round consistent with the planted state can still contradict once an earlier wrong round has been kept. So the runs are rerun
with the study's own driver, unchanged, from the same seeds; the only addition is a wrapper around `slow_loop.reduce_pattern` that
records, for every rebuild, how many merges it was given and whether it found a contradiction. A rebuild with more merges than
the active ones is a round being merged (its round log entry is the next one), and if it found a contradiction the round was
undone at once; a kept-False round that did not contradict was undone by the stall test. Each rerun must reproduce the stored
flips, work and round log exactly.
"""
from __future__ import annotations

import json
import sys
from collections import defaultdict
from multiprocessing import Pool
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
EXP = ROOT / "experiments/SPEC-MERGE-20261117-001A/SPEC-MERGE-20261117-001A-E001_spec_merge"
ART = ROOT / "artifacts/SPEC-MERGE-20261117-001A/SPEC-MERGE-20261117-001A-E001_spec_merge"
sys.path.insert(0, str(EXP))
WANT = {("local-w10-3200", "AE"), ("local-w10-3200", "A0"), ("local-w10-3200", "A"), ("local-w10-3200", "Aloc"),
        ("rand-3200", "AE"), ("rand-3200", "A0"), ("rand3-3200", "AE")}


def todo():
    out = []
    for part in ("test_fixed", "test_tuned"):
        for line in open(ART / part / "results.jsonl"):
            r = json.loads(line)
            res = r["result"]
            if (res["cell"], res["arm"]) not in WANT:
                continue
            i = int(r["case"].split("|")[-1])
            for k, x in enumerate(res["runs"]):
                if x.get("round_log"):
                    out.append((res["cell"], res["arm"], i, k, x["flips"], x["work"], x["round_log"]))
    return out


def one(t):
    cell, arm, i, k, flips, work, rlog = t
    import job
    import slow_loop as S
    import spec_merge as M
    job.setup({"stage": "test"})
    calls = []
    orig = S.reduce_pattern

    def wrapped(knots0, shadows, ties, new_ties):
        out = orig(knots0, shadows, ties, new_ties)
        calls.append((int(len(new_ties)), bool(ties.contradiction)))
        return out
    S.reduce_pattern = wrapped
    try:
        pols = json.loads((ART / "policies.json").read_text())
        _, fam, a, w, n, cap, _ = job.CELL[cell]
        seed = job.SEED_TEST + i
        inst = S.planted(fam, n, a, seed, w=w)
        pol = {"A0": job.A0, "AE": job.AE, "A": pols["A"], "Aloc": pols["Aloc"]}[arm]
        res = M.run_spec(inst, job.NOV, S.run_seed("test", cell, seed, k), cap, pol, mode="coflip")
    finally:
        S.reduce_pattern = orig
    same = res["flips"] == flips and res["work"] == work and res["round_log"] == rlog
    # walk the rebuilds: a call with more merges than are active merges a round
    active, merge_calls = 0, []
    for nt, contra in calls:
        if nt > active:
            merge_calls.append(contra)
        active = nt if not (nt > active and contra) else active
    kinds = []
    for (cons, kept), contra in zip(res["round_log"], merge_calls):
        kinds.append((cons, "kept" if kept else ("contra" if contra else "stall")))
    return {"cell": cell, "arm": arm, "same": same, "rounds": len(res["round_log"]), "merge_calls": len(merge_calls),
            "kinds": kinds, "contra_undos": res["contra_undos"], "stall_undos": res["stall_undos"]}


if __name__ == "__main__":
    with Pool(int(sys.argv[1]) if len(sys.argv) > 1 else 6) as p:
        rs = p.map(one, todo(), chunksize=2)
    summ = {"runs": len(rs), "reproduced": sum(r["same"] for r in rs),
            "walk_consistent": sum(r["rounds"] == r["merge_calls"]
                                   and sum(k == "contra" for _, k in r["kinds"]) == r["contra_undos"]
                                   and sum(k == "stall" for _, k in r["kinds"]) == r["stall_undos"] for r in rs),
            "table": {}}
    for r in rs:
        t = summ["table"].setdefault(f"{r['cell']}|{r['arm']}", defaultdict(int))
        for cons, kind in r["kinds"]:
            t[f"{'right' if cons else 'wrong'}_{kind}"] += 1
    for key, t in summ["table"].items():
        for lab in ("right", "wrong"):
            reach = t[f"{lab}_kept"] + t[f"{lab}_stall"]
            t[f"{lab}_kept_share_at_stall_test"] = round(t[f"{lab}_kept"] / reach, 4) if reach else None
    print(json.dumps(summ, indent=1))
