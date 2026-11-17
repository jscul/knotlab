"""Referee R1 for AGENT-LOOP-20261117-001: does SIGNED-NAV's carry rule, applied to an unchanged pattern, continue the run exactly?

  .venv/bin/python -B referee_carry_identity.py > referee_carry_identity.json

The agent alone on the study's instances 0-19 of block w40 and local w30 (both Dr seeds, five runs), its state carried through
the rule with identity maps every 1,000 flips; each run must reproduce the study's stored Dr run (flips) exactly.
"""
import json
import sys

import numpy as np

import referee_memory_power as P

sys.path.insert(0, str(P.EXP))
sys.path.insert(0, str(P.EXP / "agent"))


def one(cell, i, ds):
    import engine as AE
    import handle as AH
    import job
    import slow_loop as S
    job.setup({})
    th, fl = job._dr(ds)
    _, fam, a, w, n, cap = job.CELL[cell]
    seed = job.SEED_TEST + i
    inst = S.planted(fam, n, a, seed, w=w)
    ai = AE.Instance(n, inst.knots)
    out = []
    for r in range(5):
        rs = S.run_seed("test", cell, seed, r)
        h = AH.AgentHandle(ai, "policy", (), th, fl, rs)
        flips = 0
        while flips < cap:
            o = h.run(min(1000, cap - flips))
            flips += o["flips"]
            if o["solved"]:
                break
            st = h.state()
            h.close()
            dm, par, km = AH.identity_maps(ai)
            h = AH.AgentHandle(ai, "policy", (), th, fl, rs, state=AH.carry(st, n, ai.m, dm, par, km))
        h.close()
        out.append(flips)
    return out


if __name__ == "__main__":
    st = P.stored()
    res = {}
    for cell in ("block-w40-3200", "local-w30-3200"):
        same = sum(one(cell, i, ds) == st[(cell, i, f"Dr{ds}")] for i in range(20) for ds in (0, 1))
        res[cell] = {"instances_x_seeds": 40, "identical_to_stored_Dr": same}
    print(json.dumps(res, indent=1))
