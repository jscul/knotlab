"""After the run (exploratory, not a registered test): the largest tie class over a growth's whole life, for the census's own
first runs of a few settings (regenerated with census.py's seeds), at 10%, 20%, ..., 100% of the knots before the end.
Run from the repository root: .venv/bin/python -B research/RANDOM-FATES-20261112-001/life_ties.py
"""
import json
import os
import random
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "experiments", "RANDOM-FATES-20261112-001A", "RANDOM-FATES-20261112-001A-E001_fates_census"))
sys.argv = [sys.argv[0]]
import census as C  # noqa: E402
import fates as F  # noqa: E402

out = {}
for lab, kind, p, n in [("U200", "U", 200, 200), ("X0.35", "X", 0.35, None), ("X0.3", "X", 0.3, None), ("Og0.3", "Og", 0.3, None),
                        ("Ol0.3", "Ol", 0.3, None), ("L6_0.5", "L", (6, 0.5), None)]:
    rows = []
    for run in range(10):
        rng = random.Random(C.seed_of(lab, run, "grow"))
        H = 50 * n if kind == "U" else C.HORIZON
        knots, dead = F.grow(C.make_gen(kind, p, rng, n=n), H)
        if not dead:
            continue
        M = len(knots) - 1
        traj = []
        for f in (0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.95, 1.0):
            m = max(1, int(round(f * M)))
            K = knots[:m]
            N = max(v for t in K for v in t) + 1
            rd = F.Reader(N, K, samples=60, seed=run)
            cl = rd.tie_classes()
            rd.close()
            used = len({v for t in K for v in t})
            big = max((len(c) for c in cl), default=1)
            traj.append([f, m, used, big, round(big / used, 3)])
        rows.append({"run": run, "knots_at_end": M + 1, "trajectory": traj})
    out[lab] = rows
    print(lab, [[t[4] for t in r["trajectory"]] for r in rows][:5], flush=True)
json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "life_ties.json"), "w"), indent=1)
