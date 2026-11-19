"""The two part U starts my engine cannot finish within 6 GB: grown round by round, each round's count written as it is made, in a
process limited to 4 GB of address space (run under `ulimit -v`); the rounds reached are compared with the study's counts.

  (ulimit -v 4000000; ../../../.venv/bin/python -B early_rounds.py CASE) >> referee_loop_partu_early.jsonl
"""
import json
import sys

import job_partu as J

case = sys.argv[1]
J.setup({"only": case})
for cid, p in J.cases():
    import referee_first as RFK
    import referee_touch as RT
    sizes, edges = p["sizes"], p["edges"]
    n = len(sizes)
    M = [[0] * n for _ in range(n)]
    for a, b in edges:
        M[a][b] += 1
        M[b][a] += 1
    G = RFK.Start(RT.stars(sizes, M))
    for _ in range(36):
        try:
            r = G.step(RFK.fewest, None, None)
        except MemoryError:
            r = "memory"
        c = G.counts()
        m = min(len(c), len(p["theirs"]))
        print(json.dumps({"case": cid, "n": p["n"], "meet": p["meet"], "rounds": len(c) - 1, "step": r, "counts": c,
                          "counts equal the study's on these rounds": c[:m] == p["theirs"][:m]}), flush=True)
        if r != "ok" or len(G.bits) > 30000:
            break
