"""Post hoc check of SLOW-LOOP-20261117-001A, not frozen: the attention counts at an eager policy.

  python3 posthoc_analyze.py <test dir> <posthoc dir> <posthoc_summary.json>

RNDO is the oracle policy GO with uniformly drawn targets, run on the test's instances from the test's initial states. Same
statistics as analyze.py: per instance the geometric mean of five runs, per cell the median, 99% paired bootstrap; R against
the better of NOV and PS re-chosen per resample; GO/RNDO; moves found per 10^6 probe incidences.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import analyze as A  # noqa: E402
import job  # noqa: E402


def main():
    test, ph, out = sys.argv[1:4]
    data, bad = A.load(test)
    pdata, pbad = A.load(ph)
    rng = np.random.default_rng(20261117)
    res = {}
    for name, *_ in job.CELLS:
        arms = {a: data[name][a] for a in ("NOV", "PS", "GO")}
        arms["RNDO"] = pdata[name]["RNDO"]
        idx = sorted(set.intersection(*[set(v) for v in arms.values()]))
        fw = {a: A.figures(v, "work") for a, v in arms.items()}
        fc = {a: A.figures(v, "cpu") for a, v in arms.items()}
        fh = {a: A.hits(arms[a]) for a in ("GO", "RNDO")}
        runs = [r for i in idx for r in arms["RNDO"][i]["runs"]]
        row = {"instances": len(idx),
               "RNDO_R_W": A.boot(fw, "RNDO", ["NOV", "PS"], idx, rng),
               "RNDO_R_CPU": A.boot(fc, "RNDO", ["NOV", "PS"], idx, rng),
               "GO_R_W": A.boot(fw, "GO", ["NOV", "PS"], idx, rng),
               "GO/RNDO_W": A.boot(fw, "GO", ["RNDO"], idx, rng),
               "GO/RNDO_CPU": A.boot(fc, "GO", ["RNDO"], idx, rng),
               "finds_medians": {a: float(np.median([fh[a][i] for i in idx])) for a in fh},
               "RNDO_censored": sum(not r["solved"] for r in runs) / len(runs),
               "RNDO_unverified": sum(r["solved"] and not r["verified"] for r in runs),
               "RNDO_ties": float(np.median([np.median([r["ties"] for r in arms["RNDO"][i]["runs"]]) for i in idx])),
               "RNDO_n_final": float(np.median([np.median([r["n_final"] for r in arms["RNDO"][i]["runs"]])
                                                for i in idx]))}
        if all(fh["GO"][i] > 0 and fh["RNDO"][i] > 0 for i in idx):
            row["finds GO/RNDO"] = A.boot(fh, "GO", ["RNDO"], idx, rng)
        res[name] = row
    Path(out).write_text(json.dumps({"label": "post hoc, not frozen", "cells": res, "not_ok": {**bad, **pbad}},
                                    indent=1))
    f = lambda t: f"{t[0]:.2f} [{t[1]:.2f}, {t[2]:.2f}]"
    print("| Cell | GO R_W | RNDO R_W | GO/RNDO W | GO/RNDO CPU | finds GO, RNDO |")
    print("| --- | --- | --- | --- | --- | --- |")
    for name, r in res.items():
        fm = r["finds_medians"]
        print(f"| {name} | {f(r['GO_R_W'])} | {f(r['RNDO_R_W'])} | {f(r['GO/RNDO_W'])} | {f(r['GO/RNDO_CPU'])} | "
              f"{fm['GO']:.0f}, {fm['RNDO']:.0f} |")


if __name__ == "__main__":
    main()
