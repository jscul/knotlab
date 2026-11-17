"""Read-out for WEAVE-MIX-20261117-001B-E001 (frozen before running).

Arrangements of the four not-all-equal-class knots on the weave: every one with (column period, row period) = (1, 1), (2, 1),
(1, 2); 150 random ones (seeded) each with (3, 1), (1, 3), (2, 2).  For each: the set of inconsistent bonds (gauge invariant), its count per cell, and whether every distinction meets an even
number of them; per-row spectra split by the global flip at widths 6, 9, 12 (column period 1 or 3) or 6, 8, 10, 12 (column
period 2): states per distinction, the spin gap (top flip-even against top flip-odd) and the energy gap (top against second
flip-even), in log base 3 per row.  The frozen classification, at width 12 against the smaller widths:
  empty        no state;
  frozen       states per distinction below 1.01;
  ordered      spin gap below 0.01 while the energy gap is above 0.05;
  disordered   spin and energy gaps both above 0.05, each within 10% of its value at the next smaller width;
  critical     spin gap smaller at 12 than at 6, and spin gap x width at 12 within 15% of its value at 6;
  unresolved   otherwise.
For every disordered arrangement: the connected correlation of distinctions 0, 1 and 2 of a row with the same distinction r rows
away (r a multiple of the row period, up to 14) on the infinite cylinder of width 12 (rounded to the column period).
Check: arrangements with the same inconsistent set have the same spectra (the gauge).

    .venv/bin/python -B run.py      (writes artifacts/.../results.json)
"""
import hashlib
import itertools
import json
import math
import os
import random
import sys
import time

import numpy as np
import scipy.sparse as sp
from scipy.sparse.linalg import eigs

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
import mixlib as M  # noqa: E402

OUT = os.path.join(ROOT, "artifacts", "WEAVE-MIX-20261117-001B", "WEAVE-MIX-20261117-001B-E001_mixes")
WIDTHS = {1: (6, 9, 12), 2: (6, 8, 10, 12), 3: (6, 9, 12)}


def arrangements(pc, pr, sample=None, seed=None):
    keys = [(i, j, t) for i in range(pc) for j in range(pr) for t in "UD"]
    if sample is None:
        for combo in itertools.product(range(4), repeat=len(keys)):
            yield dict(zip(keys, combo))
    else:
        rng = random.Random(int.from_bytes(hashlib.sha256(seed.encode()).digest()[:8], "little"))
        seen = set()
        while len(seen) < sample:
            combo = tuple(rng.randrange(4) for _ in keys)
            if combo in seen:
                continue
            seen.add(combo)
            yield dict(zip(keys, combo))


def classify(spec):
    by = {sp_["width"]: sp_ for sp_ in spec}
    w = sorted(by)
    top = by[w[-1]]
    if top.get("empty"):
        return "empty"
    if top["per_site"] < 1.01:
        return "frozen"
    sg, eg = top["spin_gap"], top["energy_gap"]
    prev = by[w[-2]]
    if sg < 0.01 and eg > 0.05:
        return "ordered"
    finite = lambda x: x is not None and x != float("inf")
    if (finite(sg) and finite(eg) and sg > 0.05 and eg > 0.05 and not prev.get("empty")
            and finite(prev.get("spin_gap")) and finite(prev.get("energy_gap"))
            and abs(sg - prev["spin_gap"]) < 0.1 * sg and abs(eg - prev["energy_gap"]) < 0.1 * eg):
        return "disordered"
    first = by[w[0]]
    if (finite(sg) and not first.get("empty") and finite(first.get("spin_gap")) and sg < first["spin_gap"]
            and abs(sg * w[-1] - first["spin_gap"] * w[0]) < 0.15 * sg * w[-1]):
        return "critical"
    return "unresolved"


def correlation(width, arr, pc, pr):
    Ts = M.transfer_rows(width, arr, pc, pr)
    T = Ts[0].astype(np.float64)
    for X in Ts[1:]:
        T = T @ X.astype(np.float64)
    S = sp.csr_matrix(T)
    v0 = np.ones(T.shape[0])
    vals, R = eigs(S, k=1, which="LM", tol=1e-13, maxiter=50000, v0=v0)
    _, Lv = eigs(S.T.tocsr(), k=1, which="LM", tol=1e-13, maxiter=50000, v0=v0)
    lam, r, l = vals[0].real, np.abs(R[:, 0].real), np.abs(Lv[:, 0].real)
    norm = l @ r
    res = {}
    for c in range(min(3, width)):
        x0 = ((np.arange(T.shape[0]) >> c) & 1).astype(np.float64)
        m = (l * x0) @ r / norm
        var = m * (1 - m)
        out, v = [], x0 * r
        for k in range(1, 14 // pr + 1):
            v = T @ v / lam
            out.append((k * pr, float(((l * x0) @ v / norm - m * m) / var) if var > 1e-12 else None))
        res[c] = {"mean": float(m), "correlation": out}
    return res


def main():
    os.makedirs(OUT, exist_ok=True)
    res = {"started": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "families": {}}
    plan = [((1, 1), None), ((2, 1), None), ((1, 2), None), ((3, 1), 150), ((1, 3), 150), ((2, 2), 150)]
    for (pc, pr), sample in plan:
        rows = []
        t = time.time()
        for arr in arrangements(pc, pr, sample, seed=f"WM:{pc}x{pr}"):
            spec = [M.sector_spectrum(w, arr, pc, pr) for w in WIDTHS[pc]]
            cls = classify(spec)
            bad, even = M.inconsistent_set(arr, pc, pr)
            row = {"arrangement": {f"{i},{j},{u}": k for (i, j, u), k in arr.items()},
                   "inconsistent_set": [list(b) for b in bad], "all_degrees_even": even,
                   "inconsistent_per_cell": len(bad) / (pc * pr), "spectra": spec, "class": cls}
            if cls == "disordered":
                wc = 12 - 12 % pc
                try:
                    row["correlation"] = correlation(wc, arr, pc, pr)
                except Exception as exc:
                    row["correlation"] = {"error": repr(exc)}
            rows.append(row)
        counts = {}
        gauge_dev = 0.0
        by_set = {}
        for row in rows:
            key = (row["class"], row["inconsistent_per_cell"], row["all_degrees_even"])
            counts[str(key)] = counts.get(str(key), 0) + 1
            s6 = row["spectra"][0]
            sig = (s6.get("per_site", 0.0), s6.get("spin_gap"))
            k = str(row["inconsistent_set"])
            if k in by_set:
                a, b = by_set[k], sig
                for x, y in zip(a, b):
                    if x not in (None, float("inf")) and y not in (None, float("inf")):
                        gauge_dev = max(gauge_dev, abs(x - y))
                    elif x != y:
                        gauge_dev = float("inf")
            else:
                by_set[k] = sig
        res["families"][f"{pc}x{pr}"] = {"arrangements": len(rows), "inconsistent_sets": len(by_set),
                                         "same_set_max_deviation_width_6": gauge_dev,
                                         "class_by_count_and_parity": counts, "rows": rows,
                                         "seconds": round(time.time() - t, 1)}
        print(f"{pc}x{pr}", len(rows), round(time.time() - t, 1), flush=True)
    res["finished"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    with open(os.path.join(OUT, "results.json"), "w") as f:
        json.dump(res, f, indent=1, default=str)
    print("wrote", os.path.join(OUT, "results.json"), res["started"], res["finished"])


if __name__ == "__main__":
    main()
