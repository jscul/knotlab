#!/usr/bin/env python3
"""Stress test one size past (after the run, descriptive): the pinning rule found by the census (with the block's knots as block
triples, a root has ties outside its copy exactly when its block distinction is not spare, and then reaches its farthest
distinction) on blocks past the frozen range: 150 random living connected blocks on 6 distinctions with 6 to 12 knots and 150 on 7
with 5 to 12 knots (seed 20261112), each on the chain of 8 knots, substituted once.

    .venv/bin/python3 -B stress_one_size_past.py"""
import itertools
import json
import random
import sys
from multiprocessing import Pool
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import subst_lib as S  # noqa: E402


def sample(seed=20261112):
    rng = random.Random(seed)
    out = []
    for m, lo, hi in ((6, 6, 12), (7, 5, 12)):
        triples = list(itertools.combinations(range(m), 3))
        got = 0
        while got < 150:
            k = rng.randint(lo, hi)
            E = rng.sample(triples, k)
            if set(itertools.chain(*E)) != set(range(m)) or not S.connected(m, E) or not S.solutions(m, E):
                continue
            out.append((m, sorted(E)))
            got += 1
    return out


def job(B):
    m, E = B
    T = S.binding_sets(m, E)["the block's knots"]
    spare = set(S.star_colouring((m, E)))
    Q, addr = S.iterate(S.chain(8), (m, E), T, 1)
    inv = {a: i for i, a in addr.items()}
    res = []
    for p in range(m):
        root = inv[(0, p)]
        tied = S.tie_class(Q, root)
        d = S.distances(Q, root)
        cross = sum(1 for v in tied if addr[v][0] != 0)
        res.append({"distinction": p, "spare": p in spare, "ties outside the copy": cross,
                    "reaches the far end": max(d[v] for v in tied) == max(d.values())})
    agree = all((r["spare"]) == (r["ties outside the copy"] == 0) for r in res)
    full = all(r["reaches the far end"] for r in res if not r["spare"])
    return {"block": [m, E], "agree": agree, "non-spare reach the far end": full, "roots": res}


if __name__ == "__main__":
    bl = sample()
    with Pool(8) as pool:
        rows = pool.map(job, bl, chunksize=4)
    out = {"status": "descriptive, after the run (stress test one size past)", "blocks": len(rows),
           "rule held": sum(r["agree"] for r in rows), "non-spare reach the far end": sum(r["non-spare reach the far end"] for r in rows),
           "exceptions": [r for r in rows if not (r["agree"] and r["non-spare reach the far end"])][:10], "rows": rows}
    (HERE / "result_stress_one_size_past.json").write_text(json.dumps(out, indent=1) + "\n")
    print({k: v for k, v in out.items() if k != "rows"})
