"""Referee R1 for AGENT-LOOP-20261117-001: could the memory test have seen a memory effect at all?

  .venv/bin/python -B referee_memory_power.py run [workers]    -> referee_memory_power_runs.jsonl (one line per case)
  .venv/bin/python -B referee_memory_power.py summary          -> referee_memory_power.json

M1 compares carried against restarted memory at the slow loop's rebuilds. Restarting wipes the agent's memory (ages, recent
flip and visit counts, recurrent state) once per rebuild. If wiping it far more often costs the agent nothing, no carry rule
could have beaten restarting; if planting wrong memory at every rebuild costs nothing, no carry rule could have hurt. Either
way the test would have no power. Two positive controls measure this in the study's own regime (under the slow loop, per-flip
budget, the M1-flips arms), plus the agent alone on the block cells:

  DrRf          the study's restarted arm (must reproduce the stored runs)
  DrRf+W-K      the same, with the memory also wiped every K flips between rebuilds (a fresh handle from the current values,
                fresh memory and random stream, exactly as the study's restart path does at a rebuild), K = 100, 500, 2000
  DrCf          the study's carried arm (must reproduce the stored runs)
  DrCf+SCR      the same, with the carried memory scrambled at every rebuild: ages and recent flip counts permuted among the
                new distinctions, visit ages and counts among the new knots (values, random stream, step, recurrent state kept)
  A:CONT, A:WIPE-K, A:SCR-K   the agent alone, run in chunks of K flips: on one handle (must reproduce the stored Dr runs),
                wiped every K, or scrambled every K (carried onto the unchanged pattern by the carry rule, then permuted)

The driver changes are the referee's (wrappers around the study's agent_loop and handle, which are the object under test).
Instances, seeds and initial states are the study's. A run capped at 30 times the cell's reference median counts at the cap.
Statistic: per instance the geometric mean of five runs' flips, per cell the median, the ratio to the reference arm with a 99%
paired bootstrap over instances, per Dr seed.
"""
from __future__ import annotations

import json
import sys
from multiprocessing import Pool
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
EXP = ROOT / "experiments/AGENT-LOOP-20261117-001A/AGENT-LOOP-20261117-001A-E001_agent_loop"
ART = ROOT / "artifacts/AGENT-LOOP-20261117-001A/AGENT-LOOP-20261117-001A-E001_agent_loop"
sys.path.insert(0, str(EXP))
sys.path.insert(0, str(EXP / "agent"))
OUT = HERE / "referee_memory_power_runs.jsonl"
CELLS = ("block-w40-3200", "local-w30-3200", "block-w20-3200")
LOOP_ARMS = ("DrRf", "DrRf+W-100", "DrRf+W-500", "DrRf+W-2000", "DrCf", "DrCf+SCR")
ALONE_ARMS = ("A:CONT", "A:WIPE-200", "A:WIPE-1000", "A:WIPE-5000", "A:SCR-1000", "A:SCR-5000")
CAP = {"block-w40-3200": 2_000_000, "block-w20-3200": 2_000_000, "local-w30-3200": 1_000_000}  # >= 30x every reference median
B = 10_000


def _scramble(st, rng):
    p = rng.permutation(len(st.lastflip))
    q = rng.permutation(len(st.lastvisit))
    st.lastflip, st.fcnt, st.fcnt_t = st.lastflip[p], st.fcnt[p], st.fcnt_t[p]
    st.lastvisit, st.vcnt, st.vcnt_t = st.lastvisit[q], st.vcnt[q], st.vcnt_t[q]
    return st


def one(t):
    cell, i, ds, arm = t
    import agent_loop as G
    import engine as AE
    import handle as AH
    import job
    import slow_loop as S
    job.setup({})
    th, fl = job._dr(ds)
    _, fam, a, w, n, cap = job.CELL[cell]
    cap = min(cap, CAP[cell])
    seed = job.SEED_TEST + i
    inst = S.planted(fam, n, a, seed, w=w)
    knots = np.array(inst.knots, dtype=np.int64)
    rows = []
    orig_carry, orig_run = AH.carry, G._Fast.run
    for r in range(5):
        rs = S.run_seed("test", cell, seed, r)
        rng = np.random.default_rng(S.run_seed("referee-power", cell, seed, r, arm))
        if arm.startswith("A:"):
            kind, K = (arm[2:].split("-") + ["5000"])[:2]
            K = int(K)
            ai = AE.Instance(n, inst.knots)
            h = AH.AgentHandle(ai, "policy", (), th, fl, rs)
            flips, solved, j = 0, False, 0
            while flips < cap:
                o = h.run(min(K, cap - flips))
                flips += o["flips"]
                if o["solved"]:
                    solved = True
                    break
                j += 1
                if kind == "CONT":
                    continue
                st = h.state()
                h.close()
                if kind == "WIPE":
                    h = AH.AgentHandle(ai, "policy", (), th, fl, S.run_seed("referee-wipe", seed, r, j), x0=st.x)
                else:
                    dm, par, km = AH.identity_maps(ai)
                    h = AH.AgentHandle(ai, "policy", (), th, fl, rs, state=_scramble(AH.carry(st, n, len(knots), dm, par, km), rng))
            x = h.state().x.astype(np.uint8)
            h.close()
            ok = None
            if solved:
                s = x[knots].sum(axis=1)
                ok = bool(np.all((s == 1) | (s == 2)))
            rows.append({"flips": flips, "solved": solved, "ok": ok})
            continue
        base, extra = (arm.split("+") + [""])[:2]
        try:
            if extra.startswith("W-"):
                K = int(extra[2:])
                cnt = [0]

                def run_chunked(self, budget, K=K, cnt=cnt):
                    tot_f = tot_w = 0
                    tot_c = 0.0
                    mv = 0
                    while tot_f < budget:
                        rr = self.h.run(min(K, budget - tot_f))
                        tot_f += rr["flips"]
                        tot_w += rr["work"]
                        tot_c += rr["cpu"]
                        mv = rr["minviol"]
                        if rr["solved"]:
                            return tot_f, True, tot_w, tot_c, mv
                        if tot_f < budget:
                            cnt[0] += 1
                            st = self.h.state()
                            ai = self.h.inst
                            self.h.close()
                            self.h = AH.AgentHandle(ai, "policy", (), th, fl, S.run_seed("referee-wipe", seed, r, cnt[0]),
                                                    x0=st.x)
                    return tot_f, False, tot_w, tot_c, mv
                G._Fast.run = run_chunked
            elif extra == "SCR":
                G.AH.carry = lambda *aa, **kk: _scramble(orig_carry(*aa, **kk), rng)
            res = G.run_loop(inst, "agent", rs, cap, pol=dict(G.GPR, unit=job.UNIT),
                             memory="carry" if base == "DrCf" else "restart", theta=th, flags=fl, debug=True)
        finally:
            G._Fast.run = orig_run
            G.AH.carry = orig_carry
        st = np.asarray(res["state"], np.uint8)
        s = st[knots].sum(axis=1)
        rows.append({"flips": res["flips"], "work": res["work"], "solved": res["solved"],
                     "ok": bool(np.all((s == 1) | (s == 2))) if res["solved"] else None, "rebuilds": res["rebuilds"]})
    return {"cell": cell, "i": i, "ds": ds, "arm": arm, "runs": rows}


def run(workers):
    done = set()
    if OUT.exists():
        for line in open(OUT):
            r = json.loads(line)
            done.add((r["cell"], r["i"], r["ds"], r["arm"]))
    jobs = [(c, i, s, a) for c in CELLS for a in LOOP_ARMS + (ALONE_ARMS if c.startswith("block") else ())
            for s in (0, 1) for i in range(50) if (c, i, s, a) not in done]
    with Pool(workers) as p, open(OUT, "a") as f:
        for r in p.imap_unordered(one, jobs):
            f.write(json.dumps(r) + "\n")
            f.flush()


def stored():
    d = {}
    for line in open(ART / "test" / "results.jsonl"):
        r = json.loads(line)
        res = r["result"]
        if res["cell"] in CELLS and res["arm"] in ("Dr0", "Dr1", "DrRf0", "DrRf1", "DrCf0", "DrCf1"):
            d[(res["cell"], int(r["case"].split("|")[-1]), res["arm"])] = [x["flips"] for x in res["runs"]]
    return d


def summary():
    res = {}
    for line in open(OUT):
        r = json.loads(line)
        res[(r["cell"], r["i"], r["ds"], r["arm"])] = r["runs"]
    st = stored()
    rng = np.random.default_rng(5)
    out = {"cells": {}}
    for c in CELLS:
        arms = LOOP_ARMS + (ALONE_ARMS if c.startswith("block") else ())
        cs = {}
        for s in (0, 1):
            have = [a for a in arms if all((c, i, s, a) in res for i in range(50))]
            g = {a: np.array([np.exp(np.mean(np.log([max(x["flips"], 1) for x in res[(c, i, s, a)]]))) for i in range(50)])
                 for a in have}
            row = {"complete_arms": have,
                   "reproduces_stored": {a: sum([x["flips"] for x in res[(c, i, s, a)]] == st[(c, i, ref)] for i in range(50))
                                         for a, ref in (("DrRf", f"DrRf{s}"), ("DrCf", f"DrCf{s}"), ("A:CONT", f"Dr{s}"))
                                         if a in have},
                   "capped": {a: sum(not x["solved"] for i in range(50) for x in res[(c, i, s, a)]) for a in have},
                   "bad_states": sum(1 for a in have for i in range(50) for x in res[(c, i, s, a)]
                                     if x["solved"] and not x["ok"])}
            for a in have:
                ref = "A:CONT" if a.startswith("A:") else ("DrCf" if a.startswith("DrCf") else "DrRf")
                if a == ref or ref not in g:
                    continue
                sel = rng.integers(0, 50, (B, 50))
                bs = np.median(g[a][sel], axis=1) / np.median(g[ref][sel], axis=1)
                row[f"{a} / {ref}"] = [round(float(np.median(g[a]) / np.median(g[ref])), 4)] + \
                    [round(float(q), 4) for q in np.quantile(bs, [0.005, 0.995])]
            if "DrCf" in g and "DrRf" in g:
                row["DrCf / DrRf (the study's M1)"] = round(float(np.median(g["DrCf"]) / np.median(g["DrRf"])), 4)
            cs[f"Dr{s}"] = row
        out["cells"][c] = cs
    (HERE / "referee_memory_power.json").write_text(json.dumps(out, indent=1))
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    if sys.argv[1] == "run":
        run(int(sys.argv[2]) if len(sys.argv) > 2 else 12)
    else:
        summary()
