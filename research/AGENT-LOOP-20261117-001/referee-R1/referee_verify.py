"""Referee R1 for AGENT-LOOP-20261117-001: rerun loop runs and check their states with the referee's own test.

  .venv/bin/python -B referee_verify.py [workers] > referee_verify.json

For instances 0-9 of every cell and every arm under the slow loop (GN, GNf, GNco, DrC0/1, DrR0/1, DrCf0/1, DrRf0/1), all
five runs are rerun with the study's driver from the same seeds (debug=True). Each rerun must reproduce its stored flips and
work; each solved state, mapped back to the original distinctions, is checked by the referee's own test on freshly generated
original knots (no knot has its three members equal); and every class the slow loop merged is checked against the planted
state (a proved tie must hold in it).
"""
from __future__ import annotations

import json
import sys
from multiprocessing import Pool
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
EXP = ROOT / "experiments/AGENT-LOOP-20261117-001A/AGENT-LOOP-20261117-001A-E001_agent_loop"
ART = ROOT / "artifacts/AGENT-LOOP-20261117-001A/AGENT-LOOP-20261117-001A-E001_agent_loop"
sys.path.insert(0, str(EXP))
ARMS = ("GN", "GNf", "GNco", "DrC0", "DrC1", "DrR0", "DrR1", "DrCf0", "DrCf1", "DrRf0", "DrRf1")


def todo():
    out = []
    for line in open(ART / "test" / "results.jsonl"):
        r = json.loads(line)
        res = r["result"]
        i = int(r["case"].split("|")[-1])
        if res["arm"] in ARMS and i < 10:
            out.append((res["cell"], res["arm"], i, [(x["flips"], x["work"], x["solved"]) for x in res["runs"]]))
    return out


def one(t):
    cell, arm, i, stored = t
    import agent_loop as G
    import job
    import slow_loop as S
    job.setup({})
    _, fam, a, w, n, cap = job.CELL[cell]
    seed = job.SEED_TEST + i
    inst = S.planted(fam, n, a, seed, w=w)
    knots = np.array(inst.knots, dtype=np.int64)
    hid = inst.hidden.astype(np.uint8)
    rows = []
    for r in range(5):
        rs = S.run_seed("test", cell, seed, r)
        if arm == "GN":
            res = G.run_loop(inst, "nov", rs, cap, target="random", debug=True)
        elif arm == "GNf":
            res = G.run_loop(inst, "nov", rs, cap, pol=dict(G.GPR, unit=job.UNIT), target="random", debug=True)
        elif arm == "GNco":
            res = G.run_loop(inst, "nov", rs, cap, target="coflip", debug=True)
        else:
            th, fl = job._dr(int(arm[-1]))
            pol = dict(G.GPR, unit=job.UNIT) if arm[3] == "f" else G.GPR
            res = G.run_loop(inst, "agent", rs, cap, pol=pol, memory="carry" if arm[2] == "C" else "restart",
                             theta=th, flags=fl, debug=True)
        same = (res["flips"], res["work"], res["solved"]) == tuple(stored[r])
        st = np.asarray(res["state"], np.uint8)
        s = st[knots].sum(axis=1)
        ok = bool(np.all((s == 1) | (s == 2))) if res["solved"] else None
        # a proved tie holds in every allowed state: x_v = x_root(v) ^ rpar(v), the planted state included
        ties_ok = bool(np.all((hid ^ hid[res["root"]]) == res["rpar"]))
        rows.append({"same": same, "solved": res["solved"], "state_ok": ok, "ties_hold_in_planted": ties_ok,
                     "classes": int(len(np.unique(res["root"])))})
    return {"cell": cell, "arm": arm, "i": i, "runs": rows}


if __name__ == "__main__":
    with Pool(int(sys.argv[1]) if len(sys.argv) > 1 else 8) as p:
        rs = p.map(one, todo(), chunksize=1)
    runs = [x for r in rs for x in r["runs"]]
    print(json.dumps({"runs": len(runs), "reproduced": sum(x["same"] for x in runs),
                      "solved": sum(x["solved"] for x in runs),
                      "solved_state_satisfies_every_knot": sum(x["state_ok"] is True for x in runs),
                      "every_merge_holds_in_planted": sum(x["ties_hold_in_planted"] for x in runs),
                      "mismatches": [{"cell": r["cell"], "arm": r["arm"], "i": r["i"], "run": k, **x}
                                     for r in rs for k, x in enumerate(r["runs"])
                                     if not (x["same"] and x["ties_hold_in_planted"] and (x["state_ok"] or not x["solved"]))][:20]},
                     indent=1))
