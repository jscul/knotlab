"""Controls for twistlib.py, run before the freeze."""
import sys
import json
import os

import numpy as np

import twistlib as T

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.append(os.path.join(ROOT, "experiments", "WEAVE-MIX-20261117-001B", "WEAVE-MIX-20261117-001B-E001_mixes"))
import mixlib as M  # noqa: E402
fails = 0


def check(name, ok, detail=""):
    global fails
    print(("ok   " if ok else "FAIL ") + name + (f"  {detail}" if detail else ""))
    fails += not ok


arrP = {(0, "U"): 3, (0, "D"): 1, (1, "U"): 2, (1, "D"): 0, (2, "U"): 1, (2, "D"): 3}   # not one of the pair
worst = 0.0
for w in (6, 9, 12):
    for tw in (False, True):
        Md = T.dense_transfer(w, arrP, tw)
        S = T.SiteTransfer(w, arrP, tw)
        for seed in range(3):
            v = np.random.default_rng(seed).random(1 << w)
            worst = max(worst, float(np.max(np.abs(Md @ v - S.matvec(v)))))
check("site-by-site transfer = dense transfer (w = 6, 9, 12, both twists, 3 vectors)", worst < 1e-9, f"{worst:.1e}")

nae = {(i, t): 0 for i in range(3) for t in "UD"}
g = T.sector_gaps(6, nae, False)
check("plain NAE, width 6, periodic: WEAVE-MIX's stored per-site 1.3979648674467648 and spin gap 0.1987467375969509",
      abs(g["per_site"] - 1.3979648674467648) < 1e-9 and abs(g["spin_gap"] - 0.1987467375969509) < 1e-7, str(g))
gm = M.sector_spectrum(9, {(i, 0, t): 0 for i in range(1) for t in "UD"}, 1, 1)
g9 = T.sector_gaps(9, nae, False)
check("plain NAE, width 9: per-site equals mixlib's", abs(g9["per_site"] - gm["per_site"]) < 1e-9, f"{g9['per_site']}, {gm['per_site']}")

ident = T.image_inconsistent(arrP, ((1, 0), (0, 1)), (0, 0))
check("the identity maps an arrangement to itself", ident == {(i, 0, t): arrP[(i, t)] for i in range(3) for t in "UD"})
check("the point group has 12 elements", len(T.point_group()) == 12)
c = T.correlations(6, nae, False, rmax=4)
check("correlations run; spin means are 0 by the flip", all(abs(x) < 1e-9 for x in c["mean_spin"]), str(c["mean_spin"]))
print("FAILURES:", fails)
sys.exit(1 if fails else 0)
