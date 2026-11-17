"""Post hoc diagnostic of SLOW-LOOP-20261117-001A, not frozen: why do the knots the search attends to most make poor probe
targets? On 6 test instances per cell, Novelty+ (the cell's re-tuned setting) runs one epoch of n flips from the test's
first initial state; the 3% most attended knots and as many uniformly drawn knots then each get the three tie probes (budget
4,000, as in the slow loop) on the unchanged pattern. Reported per group: the share of knots with a tie found, the mean
number of knots meeting the knot's three distinctions, and the share violated at the end of the epoch.

  python3 attention_diag.py <retuned.json> <out.json>
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import job  # noqa: E402
import slow_loop as S  # noqa: E402


def main():
    tun = json.loads(Path(sys.argv[1]).read_text())
    out = {}
    rng = np.random.default_rng(5)
    for cell in ("local-w10-3200", "local-w40-3200", "block-3200", "embed-3200"):
        rows = {"attended": [], "random": []}
        for i in range(6):
            inst, _ = job._inst(cell, job.SEED_TEST + i)
            n, m = inst.n, inst.m
            x, r = S.initial_state(n, S.run_seed("test", cell, job.SEED_TEST + i, 0))
            h, _ = S._handle(n, inst.knots, np.zeros(inst.knots.shape, np.uint8), x, np.full(n, -1, np.int64), r, 1, 0)
            o = np.zeros(5)
            S.lib().fl_run(h, 4, np.array(list(tun[cell]["NOV"]) + [0, 0], float), n, o)
            vis = np.zeros(m, np.int32)
            xs = np.zeros(n, np.uint8)
            S.lib().fl_get(h, xs, np.zeros(n, np.int64), np.zeros(2, np.uint64), None, vis, np.zeros(m, np.uint8))
            S.lib().fl_free(h)
            k = max(1, int(0.03 * m))
            top = np.argsort(-vis, kind="stable")[:k]
            ran = rng.choice(m, k, replace=False)
            deg = np.bincount(inst.knots.reshape(-1), minlength=n)
            e = xs[inst.knots].sum(axis=1)
            viol = (e == 0) | (e == 3)
            for name, ks in (("attended", top), ("random", ran)):
                for kk in ks:
                    pr = np.ones(m, np.uint8)
                    pr[kk] = 0
                    h2, _ = S._handle(n, inst.knots, np.zeros(inst.knots.shape, np.uint8), xs, np.full(n, -1, np.int64),
                                      np.array([1, 2], np.uint64), 1, 0, pr)
                    so = np.zeros(6)
                    tb = np.zeros(3 * 16, np.int32)
                    bb = np.zeros(6 * 16, np.int32)
                    S.lib().sl_probe(h2, 2, 0, 4000, 0.0, 2, 0, tb, 16, bb, 16, so)
                    S.lib().fl_free(h2)
                    rows[name].append((int(so[1]) > 0, float(deg[inst.knots[kk]].mean()), bool(viol[kk]),
                                       float(so[3])))
        out[cell] = {g: {"knots": len(v), "tie_found_share": float(np.mean([a for a, *_ in v])),
                         "mean_member_degree": float(np.mean([b for _, b, *_ in v])),
                         "violated_share": float(np.mean([c for *_, c, _ in v])),
                         "probe_work_mean": float(np.mean([d for *_, d in v]))} for g, v in rows.items()}
        print(cell, json.dumps(out[cell]))
    Path(sys.argv[2]).write_text(json.dumps({"label": "post hoc diagnostic, not frozen", "cells": out}, indent=1))


if __name__ == "__main__":
    main()
