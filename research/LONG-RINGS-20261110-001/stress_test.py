"""Stress test for LONG-RINGS-20261110-001, one size past the census: every grouping of the 32 x 32 square torus's law-(12, 12)
automaton periodic under a sublattice of index at most 8 containing 32 Z^2 (the census read sides 24, 16 and 12), with ticket A's code.

    .venv/bin/python3 -B stress_test.py    writes stress_test.json beside it
"""
import collections
import importlib.util
import json
import time
from multiprocessing import Pool
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
spec = importlib.util.spec_from_file_location("run_a", ROOT / "experiments/LONG-RINGS-20261110-001A/LONG-RINGS-20261110-001A-E001_periodic_groupings/run.py")
R = importlib.util.module_from_spec(spec)
import sys  # noqa: E402
sys.modules["run_a"] = R
spec.loader.exec_module(R)
N, K = 32, 8

if __name__ == "__main__":
    t0 = time.time()
    jobs = []
    for k in range(1, K + 1):
        for a, b, c in R.hnf(k):
            if R.compatible(N, a, b, c):
                tot = 4 ** k
                step = max(1, tot // 64)
                jobs += [(N, a, b, c, lo, min(tot, lo + step)) for lo in range(0, tot, step)]
    pats = nets = 0
    on = []
    with Pool(6) as pool:
        for n, lat, npat, nnet, ot in pool.imap_unordered(R.job, jobs, chunksize=1):
            pats += npat
            nets += nnet
            on += ot
    h1 = all(r["every ring non-contractible"] and len(r["classes up to sign"]) == 1 for r in on)
    h2 = all(r["cycle"] for r in on)
    shapes = collections.Counter((tuple(r["classes up to sign"][0]) if len(r["classes up to sign"]) == 1 else "mixed", r["rings"]) for r in on)
    out = {"torus side": N, "patterns": pats, "networks": nets, "on time": len(on), "H1 parallel lines": h1, "H2 cyclic ring graph": h2,
           "on-time groupings by line class and ring count": {str(k): v for k, v in sorted(shapes.items(), key=str)},
           "seconds": round(time.time() - t0, 1)}
    (HERE / "stress_test.json").write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps(out, indent=1))
