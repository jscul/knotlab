#!/usr/bin/env python3
"""The canonical check for AFFINE-WIRE-20261108-001's smallest persistently composing chain with its contacts at least two cells
apart: the knots of c2's two-time law at lags d + 1..8, by GROWTH-LAW-20261107-001A's generic K1-K3 enumerator, and knotlab check on
the parity relation of c2's eventual support.

    .venv/bin/python3 -B research/AFFINE-WIRE-20261108-001/canonical.py   writes canonical.json"""
import itertools
import json
import subprocess
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "experiments/AFFINE-WIRE-20261108-001B/AFFINE-WIRE-20261108-001B-E001_affine_search"))
sys.path.insert(0, str(ROOT / "proofs/GROWTH-LAW-20261107-001A/GROWTH-LAW-20261107-001A-P001_a_beginning_is_a_knot"))
import run as B  # noqa: E402
import growth_law_lib as G  # noqa: E402

W, C = B.W, B.C
rows = json.loads((ROOT / "artifacts/AFFINE-WIRE-20261108-001B/AFFINE-WIRE-20261108-001B-E001_affine_search/run/positives.json").read_text())["rows"]
far = sorted([r for r in rows if r[5] and r[8] >= 2], key=lambda r: (sum(r[1]), r[1], r[2], r[0]))
r = far[0]
rules, sizes, k, law1, law2 = tuple(r[0]), tuple(r[1]), r[2], tuple(r[3]), tuple(r[4])
nxt, N, blocks = W.mixed_state_map(rules, sizes, k, law1, law2)
masks = {x: W.block_mask(blocks, x) for x in "ABC"}
d = C.ring_distance(k, sizes[1])
cur = np.arange(len(nxt), dtype=np.int64)
per_lag = []
for T in range(1, 9):
    cur = nxt[cur]
    F = ((cur >> 1) & 1).astype(np.uint8)
    R = G.Rel([f"v{j}" for j in range(N)] + ["c2"], [u | (int(F[u]) << N) for u in range(1 << N)])
    kn = [S for S in G.knots(R) if S >> N & 1]
    per_lag.append({"T": T, "knots through c2(T)": len(kn),
                    "each meets A and C": all(S & masks["A"] and S & masks["C"] for S in kn) if kn else False,
                    "sizes": sorted({bin(S).count("1") for S in kn})})
mrows, N, blocks = W.linear_matrix(rules, sizes, k, law1, law2)
s2, T1, p2 = W.row_orbit(mrows, 1 << 1)
support = [j for j in range(N) if s2[-1] >> j & 1]
names = [f"x{j}" for j in support]
cnf = [" ".join((f"~{n}" if v else n) for n, v in zip(names + ["c"], vals))
       for vals in itertools.product((0, 1), repeat=len(names) + 1) if sum(vals) % 2 == 1]
env = {"PYTHONPATH": str(ROOT / "tools"), "PATH": "/usr/bin:/bin"}
kl = json.loads(subprocess.run([sys.executable, "-B", "-m", "knotlab", "check", "--cnf", ";".join(cnf), "--loops", *names,
                                "--contact", "c", "--json"], capture_output=True, text=True, env=env, cwd=ROOT, check=True).stdout)
out = {"chain (rules, sizes, k, law at c1, law at c2)": r[:5], "d": d,
       "generic enumerator, lags 1..8": per_lag,
       "every knot through c2(T) meets A and C at every lag from d + 1": all(x["each meets A and C"] for x in per_lag if x["T"] >= d + 1),
       "eventual support of c2 (cells of A, B, C)": {x: sum(1 for j in support if masks[x] >> j & 1) for x in "ABC"},
       "knotlab check of the parity relation on that support": {k_: kl[k_] for k_ in ("is_knot", "binding", "loss_on_erasure", "invisible_in_parts", "pairwise_definable")}}
(HERE / "canonical.json").write_text(json.dumps(out, indent=1) + "\n")
print(json.dumps(out, indent=1))
