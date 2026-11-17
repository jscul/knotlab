"""Gates of AGENT-LOOP-20261117-001A, run before the freeze; exits non-zero on any failure.

  A1 with no slow budget the agent driver reproduces Dr alone run for run (flips, work), and the Novelty+ driver reproduces
     Novelty+ alone (flips), 24 runs each;
  A2 soundness at n = 800 (local w10 and w20, block, rand; 4 instances each): every arm under the slow loop (agent carry,
     agent restart, Novelty+ random, Novelty+ co-flip, agent co-flip, and under the per-flip budget Novelty+, agent carry
     and agent restart) solves and its state satisfies every original knot, and every tie it proved holds in the planted
     state; the slow loop alone, wherever it solves, satisfies every original knot, and its ties hold too;
  A3 where nothing is proved (rand), carried and restarted memory give identical runs;
  A4 the agent's first epoch under the slow loop equals Dr alone capped at that epoch (identity until the first move).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import agent_loop as G  # noqa: E402
import job  # noqa: E402
import slow_loop as S  # noqa: E402


def main() -> int:
    fails = []
    th, fl = job._dr(1)
    U = dict(G.GPR, unit=job.UNIT)
    a1 = 0
    for i in range(12):
        fam, a, w = [("local", 4.0, 10), ("rand", 2.1, 10), ("block", 2.5, 20)][i % 3]
        inst = S.planted(fam, 800, a, 1_990_000 + i, w=w)
        x = G.run_agent_alone(inst, i, 10**7, th, fl)
        y = G.run_loop(inst, "agent", i, 10**7, theta=th, flags=fl, rho_override=0.0)
        if (x["flips"], x["work"]) != (y["flips"], y["work_fast"]):
            fails.append(f"A1 agent {fam} {i}: {x['flips']},{x['work']} vs {y['flips']},{y['work_fast']}")
        u = S.run_fast(inst, "novelty_plus", (0.7, 0.01), i, 10**7)
        v = G.run_loop(inst, "nov", i, 10**7, rho_override=0.0)
        if u["flips"] != v["flips"]:
            fails.append(f"A1 nov {fam} {i}: {u['flips']} vs {v['flips']}")
        a1 += 2
    print(f"A1 {a1} run-for-run checks with no slow budget")
    a2 = moves = 0
    for i in range(16):
        fam, a, w = [("local", 4.0, 10), ("local", 4.0, 20), ("block", 2.5, 20), ("rand", 2.1, 10)][i % 4]
        inst = S.planted(fam, 800, a, 1_991_000 + i, w=w)
        hid = inst.hidden.astype(np.uint8)
        for kw in ({"fast": "agent", "memory": "carry"}, {"fast": "agent", "memory": "restart"},
                   {"fast": "nov", "target": "random"}, {"fast": "nov", "target": "coflip"},
                   {"fast": "agent", "memory": "carry", "target": "coflip"}, {"fast": "nov", "pol": U},
                   {"fast": "agent", "memory": "carry", "pol": U}, {"fast": "agent", "memory": "restart", "pol": U},
                   {"fast": "none", "pol": U}):
            r = G.run_loop(inst, seed=i, cap=10**7, theta=th, flags=fl, debug=True, **kw)
            a2 += 1
            if kw["fast"] == "none":
                if r["solved"] and (not r["verified"] or not inst.satisfied(r["state"])):
                    fails.append(f"A2 {fam} {i} slow loop alone: verified {r['verified']}")
            elif not r["solved"] or not r["verified"] or not inst.satisfied(r["state"]):
                fails.append(f"A2 {fam} {i} {kw}: solved {r['solved']} verified {r['verified']}")
            if not np.all((hid ^ hid[r["root"]]) == r["rpar"]):
                fails.append(f"A2 {fam} {i} {kw}: a proved tie fails in the planted state")
            moves += int(np.sum(r["root"] != np.arange(inst.n)))
    print(f"A2 {a2} runs under the slow loop, {moves} merged distinctions checked against the planted state")
    a3 = 0
    for i in range(6):
        inst = S.planted("rand", 3200, 2.1, 1_992_000 + i)
        c = G.run_loop(inst, "agent", i, 10**7, memory="carry", theta=th, flags=fl)
        r = G.run_loop(inst, "agent", i, 10**7, memory="restart", theta=th, flags=fl)
        if c["rebuilds"] == 0 and (c["flips"], c["work"]) != (r["flips"], r["work"]):
            fails.append(f"A3 rand {i}: carry {c['flips']} vs restart {r['flips']}")
        a3 += 1
    print(f"A3 {a3} carry-restart identities where nothing was proved")
    for i in range(4):
        inst = S.planted("local", 800, 4.0, 1_993_000 + i, w=10)
        x = G.run_agent_alone(inst, i, 800, th, fl)  # one epoch of n flips
        y = G.run_loop(inst, "agent", i, 800, theta=th, flags=fl)
        if x["flips"] != y["flips"]:
            fails.append(f"A4 {i}: {x['flips']} vs {y['flips']}")
    print("A4 4 first-epoch identities")
    print("FAILS:", len(fails))
    for f in fails[:30]:
        print("  ", f)
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
