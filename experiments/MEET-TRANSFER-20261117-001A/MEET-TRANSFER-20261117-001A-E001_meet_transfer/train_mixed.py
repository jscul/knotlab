"""Mixed-meeting-pattern ES training for MEET-TRANSFER-20261117-001A.

Every iteration scores each member on instances of several training cells (a family, a size, a density, a window); its fitness
is the mean, over the cells, of the members' centred ranks within each cell, so no cell's spread dominates. Validation is the
mean over the arm's validation cells of the mean log flips. Otherwise as train_es.train (OpenAI-ES, antithetic pairs, Adam,
first layers random and output weights zero, every flip and CPU second charged).
"""
from __future__ import annotations

import hashlib
import json
import math
import sys
import time
from multiprocessing import Pool
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import engine as E  # noqa: E402
import train_es as T  # noqa: E402

D = E.LEARN_WHERE | E.MEM_AGE | E.MEM_RNN | E.MEM_SF | E.DEGNORM
ARMS = {"D": D, "Dr": D, "Dn": E.LEARN_WHERE | E.DEGNORM, "Dl": D}
TRAIN = [("rand", 2.1, 10), ("rand", 4.0, 10), ("block", 2.5, 20)]
SCHEDULE = [(200, 120, 6, 60_000), (400, 100, 6, 300_000), (800, 40, 10, 1_500_000)]  # per cell: instances, cap
# Dl, the oracle, also trains on the primary held-out pattern (local, window 10): can these reads do it at all?
CELLS = {"D": TRAIN, "Dn": TRAIN, "Dr": [("rand", 2.1, 10)], "Dl": TRAIN + [("local", 4.0, 10)]}
VAL_N, VAL_CAP, VAL_PER_CELL = 800, 1_500_000, 24
TRAIN_SEED0, VAL_SEED0, POOL = 1_000_000, 2_000_000, 2000

_INST: dict = {}


def inst(fam, alpha, w, n, seed):
    key = (fam, alpha, w, n, seed)
    if key not in _INST:
        if len(_INST) > 4000:
            _INST.clear()
        _INST[key] = E.planted(fam, n, alpha, seed, w=w)
    return _INST[key]


def _eval(task):
    theta, flags, cell, n, seeds, purpose, cap = task
    fam, alpha, w = cell
    t0 = time.process_time()
    out = []
    for s in seeds:
        r = E.run(inst(fam, alpha, w, n, s), "policy", (), theta=theta, flags=flags,
                  seed=T.run_seed(purpose, fam, alpha, n, s), max_flips=cap)
        out.append((T.score(r, cap), r["flips"], r["solved"], r["cpu"], r["work"]))
    return out, time.process_time() - t0


def _default_sigterm():
    import signal
    signal.signal(signal.SIGTERM, signal.SIG_DFL)


def train(arm: str, seed: int, out: Path, workers: int, pairs: int = 32, sigma: float = 0.1, lr: float = 0.05,
          schedule=SCHEDULE, val_per_cell: int = VAL_PER_CELL):
    flags = ARMS[arm]
    cells = CELLS[arm]
    mask = T.param_mask(flags)
    d = int(mask.sum())
    rng = np.random.default_rng(T.run_seed("es-mixed", arm, seed))
    theta = T.init_theta(flags, rng)
    m1, m2 = np.zeros(d), np.zeros(d)
    b1, b2, eps = 0.9, 0.999, 1e-8
    out.mkdir(parents=True, exist_ok=True)
    log = open(out / "log.jsonl", "w")
    acct = {"flips": 0, "work": 0, "cpu_engine": 0.0, "cpu_workers": 0.0}
    t0, w0 = time.process_time(), time.perf_counter()
    best = (float("inf"), theta.copy(), None)
    step = 0

    def charge(res):
        for r in res:
            acct["cpu_workers"] += r[1]
            for x in r[0]:
                acct["flips"] += x[1]
                acct["work"] += x[4]
                acct["cpu_engine"] += x[3]

    with Pool(workers, initializer=_default_sigterm) as pool:
        def validate(tag):
            nonlocal best
            tasks = [(theta, flags, c, VAL_N, [VAL_SEED0 + i], f"val|{arm}|{seed}|{tag}", VAL_CAP)
                     for c in cells for i in range(val_per_cell)]
            res = pool.map(_eval, tasks)
            charge(res)
            per = {}
            for (th, fl, c, n, ss, pu, cap), r in zip(tasks, res):
                per.setdefault(c, []).append(r[0][0])
            v = float(np.mean([np.mean([x[0] for x in xs]) for xs in per.values()]))
            meds = {f"{c[0]}{c[1]}": float(np.median([x[1] for x in xs])) for c, xs in per.items()}
            solved = int(sum(x[2] for xs in per.values() for x in xs))
            if v < best[0]:
                best = (v, theta.copy(), tag)
            log.write(json.dumps({"tag": tag, "val_mean_log_flips": v, "val_medians": meds, "val_solved": solved, **acct}) + "\n")
            log.flush()
            print(f"[{arm} s{seed}] {tag} val {v:.3f} {meds} solved {solved} cpu {acct['cpu_workers']:.0f}s", flush=True)

        for stage, (n, iters, batch, cap) in enumerate(schedule):
            last = stage == len(schedule) - 1
            for it in range(iters):
                if last and it % 10 == 0:
                    validate(f"stage{stage}-it{it}")
                seeds = {c: [TRAIN_SEED0 + int(i) for i in rng.choice(POOL, batch, replace=False)] for c in cells}
                noise = rng.standard_normal((pairs, d))
                tasks = []
                for k in range(pairs):
                    for sgn in (1, -1):
                        th = theta.copy()
                        th[mask] += sgn * sigma * noise[k]
                        for c in cells:
                            tasks.append((th, flags, c, n, seeds[c], f"train|{arm}|{seed}|{stage}|{it}", cap))
                res = pool.map(_eval, tasks)
                charge(res)
                per = len(cells)
                members = len(res) // per
                ranks = np.mean([T.centered_ranks(np.array([-np.mean([x[0] for x in res[j * per + q][0]])
                                                            for j in range(members)])) for q in range(per)], axis=0)
                g = ((ranks[0::2] - ranks[1::2])[:, None] * noise).sum(0) / (2 * pairs * sigma)
                step += 1
                m1 = b1 * m1 + (1 - b1) * g
                m2 = b2 * m2 + (1 - b2) * g * g
                theta[mask] += lr * (m1 / (1 - b1 ** step)) / (np.sqrt(m2 / (1 - b2 ** step)) + eps)
                if it % 10 == 0:
                    log.write(json.dumps({"stage": stage, "n": n, "it": it, **acct}) + "\n")
                    log.flush()
        validate("final")
    summary = {"arm": arm, "flags": flags, "seed": seed, "cells": cells, "schedule": schedule, "val": [VAL_N, VAL_CAP, val_per_cell],
               "dim": d, "best_val_mean_log_flips": best[0], "best_tag": best[2], **acct,
               "cpu_main": time.process_time() - t0, "wall": time.perf_counter() - w0,
               "engine_sha256": hashlib.sha256(E.SRC.read_bytes()).hexdigest(), "what_params": []}
    summary["cpu_total"] = summary["cpu_workers"] + summary["cpu_main"]
    np.save(out / "theta_best.npy", best[1])
    np.save(out / "theta_final.npy", theta)
    (out / "summary.json").write_text(json.dumps(summary, indent=1))
    return summary
