"""Frozen run for WEAVE-PAIR-20261118-001B-E001: the 3 x 1 weave pair from WEAVE-MIX-20261117-001, with the twist set explicitly.
Each part runs as its own process (--part NAME), then --merge.

- W1, symmetry: is arr2 the image of arr1 under a symmetry of the weave, up to a gauge (equal inconsistent bonds)?
- W2, gaps: both arrangements, both twist sectors (periodic; antiperiodic: knots crossing the seam read column 0 flipped), flip-even
  and flip-odd, at widths 6, 9, 12, 15, 18 and 21; the free-energy splitting between the sectors; the seam moved one column (a
  check); arr1 in one sector against arr2 in the other.
- W3, the ruler: exact correlations at width 12 along the transfer (r = 1 to 30) and around (up to 6 columns), both arrangements
  and sectors; local slopes of tau(r) = -log3 |C(r)| on r = 10 to 30; strict decrease of |C(r)| at single-row resolution, and of
  its even-r and odd-r subsequences (the two-row tick, declared in advance as an envelope reading).
"""
import json
import math
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
sys.path.append(os.path.join(ROOT, "experiments", "WEAVE-MIX-20261117-001B", "WEAVE-MIX-20261117-001B-E001_mixes"))
import twistlib as T  # noqa: E402
import mixlib as M  # noqa: E402

OUT = os.path.join(ROOT, "artifacts", "WEAVE-PAIR-20261118-001B", "WEAVE-PAIR-20261118-001B-E001_twist")
ARR1 = {(0, "U"): 1, (0, "D"): 2, (1, "U"): 0, (1, "D"): 3, (2, "U"): 2, (2, "D"): 2}
ARR2 = {(0, "U"): 1, (0, "D"): 0, (1, "U"): 0, (1, "D"): 1, (2, "U"): 2, (2, "D"): 2}
WIDTHS = (6, 9, 12, 15, 18, 21)


def as_mix(arr):
    return {(i, 0, t): arr[(i, t)] for i in range(3) for t in "UD"}


def shifted(arr, k):
    return {(i, t): arr[((i + k) % 3, t)] for i in range(3) for t in "UD"}


def w1():
    target = M.inconsistent_set(as_mix(ARR2), 3, 1)[0]
    own = M.inconsistent_set(as_mix(ARR1), 3, 1)[0]
    hits = []
    for g in T.point_group():
        for sx in range(3):
            for sy in range(2):
                img = T.image_inconsistent(ARR1, g, (sx, sy))
                if img is None:
                    continue
                if M.inconsistent_set(img, 3, 1)[0] == target:
                    hits.append({"g": g, "shift": (sx, sy)})
    return {"inconsistent_arr1": [list(b) for b in own], "inconsistent_arr2": [list(b) for b in target],
            "same_inconsistent_set": own == target, "symmetries_to_arr2": hits}


def w2():
    res = {}
    for name, arr in (("arr1", ARR1), ("arr2", ARR2)):
        for w in WIDTHS:
            for tw in (False, True):
                t = time.time()
                g = T.sector_gaps(w, arr, tw, k=6)
                g["seconds"] = round(time.time() - t, 1)
                res[f"{name}:{w}:{'anti' if tw else 'per'}"] = g
                print("W2", name, w, tw, {k: g[k] for k in ("per_site", "spin_gap", "energy_gap")}, g["seconds"], "s", flush=True)
    for w in (9, 12):                                   # the seam moved one column: arr shifted, antiperiodic
        g = T.sector_gaps(w, shifted(ARR1, 1), True, k=6)
        res[f"arr1-shift1:{w}:anti"] = g
    return res


def w3():
    res = {}
    for name, arr in (("arr1", ARR1), ("arr2", ARR2)):
        for tw in (False, True):
            c = T.correlations(12, arr, tw, rmax=30)
            rep = {"around": c["around"], "mean_spin": c["mean_spin"], "positions": {}}
            for pos, seq in c["along"].items():
                mags = [abs(x) for x in seq]
                cut = next((k for k, m in enumerate(mags) if m < 1e-8), len(mags))
                live = mags[:cut]
                single = all(live[k + 1] < live[k] for k in range(len(live) - 1))
                even = live[1::2]                    # r = 2, 4, ...
                odd = live[0::2]                     # r = 1, 3, ...
                two_row = all(even[k + 1] < even[k] for k in range(len(even) - 1)) and \
                    all(odd[k + 1] < odd[k] for k in range(len(odd) - 1))
                tau = [-math.log(m, 3) if m > 0 else float("inf") for m in mags]
                slopes = [tau[k + 1] - tau[k] for k in range(9, 29) if math.isfinite(tau[k]) and math.isfinite(tau[k + 1])]
                fit = None
                rs = [k + 1 for k in range(9, 30) if mags[k] > 1e-14]
                if len(rs) >= 3:
                    fit = float(np.polyfit(rs, [tau[r - 1] for r in rs], 1)[0])
                rep["positions"][str(pos)] = {"C": seq[:12], "single_row_decrease": single, "two_row_decrease": two_row,
                                              "live_terms": cut, "slope_fit_r10_30": fit,
                                              "local_slopes_r10_30": [round(x, 6) for x in slopes]}
            res[f"{name}:{'anti' if tw else 'per'}"] = rep
            print("W3", name, tw, {p: (v["single_row_decrease"], v["two_row_decrease"], v["slope_fit_r10_30"])
                                    for p, v in rep["positions"].items()}, flush=True)
    return res


PARTS = {"W1": w1, "W2": w2, "W3": w3}


def main():
    os.makedirs(OUT, exist_ok=True)
    if "--part" in sys.argv:
        name = sys.argv[sys.argv.index("--part") + 1]
        t0 = time.time()
        res = {"part": name, "started": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "result": PARTS[name]()}
        res["seconds"] = round(time.time() - t0)
        res["finished"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        json.dump(res, open(os.path.join(OUT, f"part_{name}.json"), "w"), indent=1, default=str)
        print("done", name, res["seconds"], "s")
        return
    if "--merge" in sys.argv:
        res = {}
        for name in PARTS:
            part = json.load(open(os.path.join(OUT, f"part_{name}.json")))
            res[name] = part["result"]
            res.setdefault("parts", {})[name] = {k: part[k] for k in ("started", "finished", "seconds")}
        json.dump(res, open(os.path.join(OUT, "results.json"), "w"), indent=1, default=str)
        print("merged")
        return
    raise SystemExit("use --part NAME (W1, W2, W3) or --merge")


if __name__ == "__main__":
    main()
