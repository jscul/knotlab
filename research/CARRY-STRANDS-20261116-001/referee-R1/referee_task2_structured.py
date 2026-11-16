"""Referee R1, task 2: structured families rebuilt from the definitions
(fresh code only): ladders, pyramids, subdivided trees.

Every spend-only run is computed twice: by the BFS over carried states and
by the search-free tree DP (referee_carry.spend_min_steps).  Where the BFS
over carried states is too large (subdivided trees at w = 3), the DP alone
gives the spend-only phases and rounds; the DP is validated against the BFS
per distinction in referee_dp_vs_bfs.py.
"""

import json
import math
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import referee_carry as R  # noqa: E402


def both(n, atoms, H, w, law, cap=3_000_000):
    t0 = time.time()
    try:
        r = R.run_law(n, atoms, H, w, law, cap=cap)
        rec = {"P": r["P"], "T": r["T"], "L": r["L"], "states": r["states"], "phase_of": r["phase"]}
    except R.Capped as e:
        rec = {"capped": int(e.args[0])}
    if law == "spend":
        d = R.run_spend_dp(n, atoms, H, w)
        rec["dp"] = {"P": d["P"], "T": d["T"], "L": d["L"]}
        if "P" in rec:
            rec["dp_agrees"] = (d["P"] == rec["P"] and d["L"] == rec["L"] and d["phase"] == rec["phase_of"])
    rec["sec"] = round(time.time() - t0, 2)
    return rec


def main():
    out = {"ladder": {}, "pyramid": {}, "subtree": {}}
    for k in (8, 32, 128):
        n, at, H, top = R.ladder(k)
        sig = R.sigma(n, at, H)
        row = {"n": n, "sigma_top": sig[top]}
        for w, law in ((1, "spend"), (2, "spend"), (2, "keep")):
            r = both(n, at, H, w, law)
            r["phase_top"] = r["phase_of"][top]
            del r["phase_of"]
            row[f"w{w}{'k' if law == 'keep' else ''}"] = r
        out["ladder"][k] = row
        print("ladder", k, {kk: (v["P"], v["T"]) if isinstance(v, dict) and "P" in v else v for kk, v in row.items()}, flush=True)
    for h in range(4, 13):
        n, at, H, top = R.pyramid(h)
        sig = R.sigma(n, at, H)
        row = {"n": n, "sigma_top": sig[top]}
        for w in (1, 2, 3, 4):
            if w == 4 and h > 10:
                continue
            for law in (("spend",) if w == 1 else ("spend", "keep")):
                r = both(n, at, H, w, law)
                r["phase_top"] = r["phase_of"][top]
                del r["phase_of"]
                row[f"w{w}{'k' if law == 'keep' else ''}"] = r
        P_ok = all(row[k]["P"] == math.ceil(h / int(k[1])) for k in row if k.startswith("w"))
        T_ok = all(row[k]["T"] == h for k in row if k.startswith("w"))
        row["P_eq_ceil_h_over_w_all"] = P_ok
        row["T_eq_h_all"] = T_ok
        out["pyramid"][h] = row
        print("pyramid", h, {kk: (v["P"], v["T"]) for kk, v in row.items() if kk.startswith("w")}, P_ok, T_ok, flush=True)
    for d, ell in ((4, 4), (4, 8), (3, 16), (4, 16), (6, 4), (6, 16)):
        n, at, H, top = R.subdivided_tree(d, ell)
        sig = R.sigma(n, at, H)
        row = {"n": n, "sigma_top": sig[top]}
        for w in (1, 2, 3):
            for law in (("spend",) if w == 1 else ("spend", "keep")):
                if w == 3 and (d, ell) in ((4, 16), (6, 16), (6, 4)):
                    dp = R.run_spend_dp(n, at, H, w)
                    row[f"w3{'k' if law == 'keep' else ''}"] = {"bfs": "not run (state space too large)",
                                                                "dp": {"P": dp["P"], "T": dp["T"], "L": dp["L"]}} \
                        if law == "spend" else {"bfs": "not run"}
                    continue
                r = both(n, at, H, w, law, cap=2_500_000)
                if "phase_of" in r:
                    r["phase_top"] = r["phase_of"][top]
                    del r["phase_of"]
                row[f"w{w}{'k' if law == 'keep' else ''}"] = r
        out["subtree"][f"d{d}-l{ell}"] = row
        print("subtree", d, ell, {kk: (v.get("P"), v.get("T"), v.get("dp", {}).get("T"), v.get("sec")) for kk, v in row.items() if kk.startswith("w")}, flush=True)
    with open(os.path.join(HERE, "referee_task2_structured.json"), "w") as fh:
        json.dump(out, fh, indent=1)


if __name__ == "__main__":
    main()
