#!/usr/bin/env python3
"""Run GROW-HEAR-20261109-001A-E001 (frozen contract beside this file): the reach of an original ring in the growing plane.

    .venv/bin/python3 -B run.py
On GROW-HORIZON-20261109-001A's horizon_lib (every cell's dependence on the original rings' own first-row cells, positions in the
original lattice's units). Open doubling every P lags while the network has at most 9,216 rings / 4 before a doubling (to 96 x 96).
Writes artifacts/GROW-HEAR-20261109-001A/GROW-HEAR-20261109-001A-E001_hearing_reach/run/result.json."""
import json
import sys
import time
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "proofs/GROW-HORIZON-20261109-001A/GROW-HORIZON-20261109-001A-P001_while_it_doubles_every_lag_no_ring_hears_another"))
import horizon_lib as H  # noqa: E402

MAX_RINGS = 9216
RUNS = [(3, 2), (3, 4), (2, 2), (2, 4)]   # (g, P): the two g = 3 schedules and their g = 2 controls
OUT = ROOT / "artifacts/GROW-HEAR-20261109-001A/GROW-HEAR-20261109-001A-E001_hearing_reach/run/result.json"


def growing(g, P):
    run = H.Run(3, 3, g)
    X = (Fraction(0), Fraction(0))
    t, most, ever, by_lag, before = 0, Fraction(0), {}, [], []
    while True:
        if t % P == 0:
            if len(run.net.rings) * 4 > MAX_RINGS:
                break
            if t > 0:
                r, cnt = run.reach(X)
                before.append({"lag": t - 1, "side": len(run.net.cols), "reach": str(r), "contacts needing it": cnt})
            run.double()
        run.step()
        t += 1
        r, cnt = run.reach(X)
        by_lag.append((t, str(r), cnt))
        if r is not None and r > most:
            most = r
        for Y in H.heard(run, X):
            ever.setdefault(Y, t)
    heard = sorted((str(H.taxicab(Y, X, run.net.period)), lag) for Y, lag in ever.items())
    return {"g": g, "P": P, "lags read": t, "before each doubling": before, "largest reach": str(most),
            "original rings that ever hear it (distance, first lag)": heard, "reach by lag": by_lag}


def static(g, lags=60):
    run = H.Run(3, 3, g)
    X = (Fraction(0), Fraction(0))
    first = {}
    for t in range(1, lags + 1):
        run.step()
        for Y in H.heard(run, X):
            first.setdefault(str(Y), t)
    return {"g": g, "first lag each original ring hears ring (0, 0)": first}


def main():
    t0 = time.time()
    out = {"experiment_id": "GROW-HEAR-20261109-001A-E001", "growing": [growing(g, P) for g, P in RUNS],
           "static": [static(3), static(2)]}
    out["seconds"] = round(time.time() - t0)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, indent=1, default=str) + "\n")
    for r in out["growing"]:
        print("g", r["g"], "P", r["P"], "lags", r["lags read"], [(b["lag"], b["side"], b["reach"], b["contacts needing it"]) for b in r["before each doubling"]],
              "max", r["largest reach"], "heard by", r["original rings that ever hear it (distance, first lag)"])
    for s in out["static"]:
        print("static g", s["g"], s["first lag each original ring hears ring (0, 0)"])
    print(out["seconds"], "s")


if __name__ == "__main__":
    main()
