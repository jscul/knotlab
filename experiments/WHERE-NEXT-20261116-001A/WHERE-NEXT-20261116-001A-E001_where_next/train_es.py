"""Train the learned arms and tune the hand-written arms (WHERE-NEXT-20261116-001A).

Every flip and CPU second spent here is charged to the arm it served.

  train_es.py tune  --out DIR            tune A1-A4, A6, A7 on 64 training instances at n = 800
  train_es.py train --arm L3 --seed 0 --out DIR [--tuning DIR/tuning.json]

Learned arms (flags of nae_engine.c):
  L1  learned what, uniform where, no memory
  L2w learned where, probSAT what (cb from tuning), no memory
  L2  learned where and what, no memory
  L3  learned where and what, ages and recent counts, recurrent state
Training: OpenAI-ES (antithetic, centred ranks, Adam) on a curriculum of `rand` sizes 200, 400, 800; the kept
weights are those with the best validation score at n = 800.
"""
from __future__ import annotations

import argparse
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

ARMS = {"L1": 0, "L2w": E.LEARN_WHERE | E.WHAT_PROBSAT, "L2": E.LEARN_WHERE,
        "L3": E.LEARN_WHERE | E.MEM_AGE | E.MEM_RNN}
ALPHA, POOL = 2.1, 2000
TRAIN_SEED0, VAL_SEED0 = 1_000_000, 2_000_000
# (n, iterations, instances per iteration, flip cap ~ 20x the calibrated probSAT median)
CURRICULUM = [(200, 120, 16, 60_000), (400, 100, 16, 300_000), (800, 40, 32, 1_500_000)]
VAL_N, VAL_CAP, VAL_COUNT = 800, 1_500_000, 64
L = E.layout()


def param_mask(flags: int) -> np.ndarray:
    """Weights that the flags let act; ES perturbs only these."""
    HID, HR, DW, DK = L["HID"], L["HR"], L["DW"], L["DK"]
    m = np.zeros(L["NTHETA"], dtype=bool)
    if not flags & E.WHAT_PROBSAT:
        cols = [0, 1, 2] + ([3, 4, 5, 6] if flags & E.MEM_AGE else []) + \
            (list(range(DW, DW + HR)) if flags & E.MEM_RNN else [])
        for j in range(HID):
            for i in cols:
                m[L["W_W1"] + j * (DW + HR) + i] = True
        m[L["W_B1"]:L["W_W2"] + HID] = True
    if flags & E.LEARN_WHERE:
        cols = [0, 1, 2, 3, 7] + ([4, 5, 6] if flags & E.MEM_AGE else []) + \
            (list(range(DK, DK + HR)) if flags & E.MEM_RNN else [])
        for j in range(HID):
            for i in cols:
                m[L["K_W1"] + j * (DK + HR) + i] = True
        m[L["K_B1"]:L["K_W2"] + HID] = True
    if flags & E.MEM_RNN:
        m[L["R_WH"]:L["R_B"] + HR] = True
    return m


def init_theta(flags: int, rng: np.random.Generator) -> np.ndarray:
    """First layers random, output weights zero: the agent starts uniform but the ES signal is first order."""
    HID, HR, DW, DK, DS = L["HID"], L["HR"], L["DW"], L["DK"], L["DS"]
    th = np.zeros(L["NTHETA"])
    mask = param_mask(flags)
    w = rng.normal(0, 1 / math.sqrt(DW + HR), HID * (DW + HR))
    th[L["W_W1"]:L["W_B1"]] = w
    k = rng.normal(0, 1 / math.sqrt(DK + HR), HID * (DK + HR))
    th[L["K_W1"]:L["K_B1"]] = k
    th[L["R_WH"]:L["R_B"]] = rng.normal(0, 0.5 / math.sqrt(HR + DS), L["R_B"] - L["R_WH"])
    th[~mask] = 0.0
    th[L["W_W2"]:L["W_W2"] + HID] = 0.0
    th[L["K_W2"]:L["K_W2"] + HID] = 0.0
    return th


def run_seed(*parts) -> int:
    return int.from_bytes(hashlib.sha256("|".join(map(str, parts)).encode()).digest()[:8], "little")


def score(r: dict, cap: int) -> float:
    return math.log(r["flips"]) if r["solved"] else math.log(cap) + math.log1p(r["minviol"])


_INST: dict = {}


def inst(seed: int, n: int, family: str = "rand", alpha: float = ALPHA) -> E.Instance:
    key = (family, n, alpha, seed)
    if key not in _INST:
        if len(_INST) > 4000:
            _INST.clear()
        _INST[key] = E.planted(family, n, alpha, seed)
    return _INST[key]


def _eval(task):
    theta, flags, algo, params, n, seeds, purpose, cap = task
    t0 = time.process_time()
    out = []
    for s in seeds:
        r = E.run(inst(s, n), algo, params, theta=theta, flags=flags, seed=run_seed(purpose, s), max_flips=cap)
        out.append((score(r, cap), r["flips"], r["solved"], r["cpu"], r["work"]))
    return out, time.process_time() - t0


def centered_ranks(x: np.ndarray) -> np.ndarray:
    r = np.empty(len(x))
    r[np.argsort(x)] = np.arange(len(x))
    return r / (len(x) - 1) - 0.5


def train(arm: str, seed: int, out: Path, pairs: int, sigma: float, lr: float, workers: int,
          what_params: tuple, curriculum=CURRICULUM):
    flags = ARMS[arm]
    mask = param_mask(flags)
    d = int(mask.sum())
    rng = np.random.default_rng(run_seed("es", arm, seed))
    theta = init_theta(flags, rng)
    params = what_params if flags & E.WHAT_PROBSAT else ()
    m1, m2 = np.zeros(d), np.zeros(d)
    b1, b2, eps_adam = 0.9, 0.999, 1e-8
    val_seeds = [VAL_SEED0 + i for i in range(VAL_COUNT)]
    out.mkdir(parents=True, exist_ok=True)
    log = open(out / "log.jsonl", "w")
    acct = {"flips": 0, "work": 0, "cpu_engine": 0.0, "cpu_workers": 0.0}
    t_main0, wall0 = time.process_time(), time.perf_counter()
    best = (float("inf"), theta.copy(), None)
    step_no = 0

    def charge(res):
        for r in res:
            acct["cpu_workers"] += r[1]
            for x in r[0]:
                acct["flips"] += x[1]
                acct["cpu_engine"] += x[3]
                acct["work"] += x[4]

    with Pool(workers) as pool:
        def validate(tag):
            nonlocal best
            res = pool.map(_eval, [(theta, flags, "policy", params, VAL_N, [s], f"val|{arm}|{seed}|{tag}", VAL_CAP)
                                   for s in val_seeds])
            charge(res)
            v = float(np.mean([r[0][0][0] for r in res]))
            solved = int(sum(r[0][0][2] for r in res))
            med = float(np.median([r[0][0][1] for r in res]))
            if v < best[0]:
                best = (v, theta.copy(), tag)
            row = {"tag": tag, "val_n": VAL_N, "val_mean_log_flips": v, "val_median_flips": med, "val_solved": solved,
                   **acct}
            log.write(json.dumps(row) + "\n")
            log.flush()
            print(f"[{arm} s{seed}] {tag} val n={VAL_N} mean log {v:.3f} median {med:.0f} solved {solved}/{VAL_COUNT} "
                  f"flips {acct['flips']:.3g} cpu {acct['cpu_workers']:.0f}s", flush=True)

        for stage, (n, iters, batch, cap) in enumerate(curriculum):
            last = stage == len(curriculum) - 1
            for it in range(iters):
                if last and it % 10 == 0:
                    validate(f"stage{stage}-it{it}")
                seeds = [TRAIN_SEED0 + int(i) for i in rng.choice(POOL, batch, replace=False)]
                noise = rng.standard_normal((pairs, d))
                tasks = []
                for k in range(pairs):
                    for sgn in (1, -1):
                        th = theta.copy()
                        th[mask] += sgn * sigma * noise[k]
                        tasks.append((th, flags, "policy", params, n, seeds, f"train|{arm}|{seed}|{stage}|{it}", cap))
                res = pool.map(_eval, tasks)
                charge(res)
                fit = np.array([-np.mean([x[0] for x in r[0]]) for r in res])
                ranks = centered_ranks(fit)
                g = ((ranks[0::2] - ranks[1::2])[:, None] * noise).sum(0) / (2 * pairs * sigma)
                step_no += 1
                m1 = b1 * m1 + (1 - b1) * g
                m2 = b2 * m2 + (1 - b2) * g * g
                theta[mask] += lr * (m1 / (1 - b1 ** step_no)) / (np.sqrt(m2 / (1 - b2 ** step_no)) + eps_adam)
                if it % 10 == 0:
                    log.write(json.dumps({"stage": stage, "n": n, "it": it, "train_mean_log_flips": float(-fit.mean()),
                                          **acct}) + "\n")
                    log.flush()
                    print(f"[{arm} s{seed}] stage {stage} n={n} it {it} train mean log {-fit.mean():.3f} "
                          f"cpu {acct['cpu_workers']:.0f}s", flush=True)
        validate("final")
    summary = {"arm": arm, "flags": flags, "seed": seed, "what_params": list(params), "pairs": pairs, "sigma": sigma,
               "lr": lr, "curriculum": curriculum, "val": [VAL_N, VAL_CAP, VAL_COUNT], "dim": d,
               "best_val_mean_log_flips": best[0], "best_tag": best[2], **acct,
               "cpu_main": time.process_time() - t_main0, "wall": time.perf_counter() - wall0,
               "engine_sha256": hashlib.sha256(E.SRC.read_bytes()).hexdigest()}
    summary["cpu_total"] = summary["cpu_workers"] + summary["cpu_main"]
    np.save(out / "theta_best.npy", best[1])
    np.save(out / "theta_final.npy", theta)
    (out / "summary.json").write_text(json.dumps(summary, indent=1))
    print(json.dumps(summary), flush=True)


# Extended on 2026-11-16 before any learned arm was trained, where the first tuning's optimum sat at a grid edge
# (deviation recorded in the result note); extending a grid can only strengthen the hand-written side.
GRIDS = {
    "walksat": [("walksat", (p,)) for p in (0.05, 0.1, 0.15, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8)],
    "probsat": [("probsat_poly", (cb, 1.0)) for cb in (1.0, 1.2, 1.5, 1.8, 2.1, 2.4, 2.7, 3.0, 3.5, 4.0)]
               + [("probsat_exp", (cb,)) for cb in (1.25, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 5.0)],
    "novelty_plus": [("novelty_plus", (p, wp)) for p in (0.05, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9)
                     for wp in (0.01, 0.05, 0.1, 0.2)],
    "greedy_where": [("greedy_where", (cb, 1.0, q)) for q in (0.0, 0.1, 0.2, 0.4, 0.6, 0.75, 0.9)
                     for cb in (1.5, 1.8, 2.3, 2.8)],
    "sticky": [("sticky", (cb, 1.0, q)) for q in (0.2, 0.4, 0.6, 0.8, 0.95) for cb in (1.5, 1.8, 2.3, 2.8)],
    "fms": [("fms", (eta,)) for eta in (0.05, 0.1, 0.15, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8)],
}
TUNE_N, TUNE_CAP, TUNE_COUNT = 800, 1_500_000, 64


def tune(out: Path, workers: int, family: str = "rand", n: int = TUNE_N, cap: int = TUNE_CAP,
         seed0: int = TRAIN_SEED0, count: int = TUNE_COUNT, grids: dict = GRIDS, alpha: float = ALPHA):
    seeds = [seed0 + i for i in range(count)]
    out.mkdir(parents=True, exist_ok=True)
    result = {"family": family, "n": n, "alpha": alpha, "cap": cap, "seeds": [seeds[0], seeds[-1]]}

    def _inst_task(algo, prm, s):
        return (None, 0, algo, prm, n, [s], f"tune|{family}|{n}|{algo}|{prm}", cap)

    with Pool(workers) as pool:
        for name, grid in grids.items():
            t0 = time.perf_counter()
            rows, flips, cpu = [], 0, 0.0
            for algo, prm in grid:
                if family == "rand" and alpha == ALPHA:
                    res = pool.map(_eval, [_inst_task(algo, prm, s) for s in seeds])
                else:
                    res = pool.map(_eval_family, [(family, n, alpha, algo, prm, s, cap) for s in seeds])
                sc = [r[0][0][0] for r in res]
                flips += sum(r[0][0][1] for r in res)
                cpu += sum(r[1] for r in res)
                rows.append({"algo": algo, "params": list(prm), "mean_log_flips": float(np.mean(sc)),
                             "median_flips": float(np.median([r[0][0][1] for r in res])),
                             "solved": int(sum(r[0][0][2] for r in res))})
            best = min(rows, key=lambda r: r["mean_log_flips"])
            result[name] = {"best": best, "grid": rows, "flips_total": flips, "cpu_workers": cpu,
                            "wall": time.perf_counter() - t0}
            print(name, best, f"flips {flips:.3g} cpu {cpu:.1f}s", flush=True)
    (out / "tuning.json").write_text(json.dumps(result, indent=1))
    return result


def _eval_family(task):
    family, n, alpha, algo, prm, s, cap = task
    t0 = time.process_time()
    i = E.planted(family, n, alpha, s)
    r = E.run(i, algo, prm, seed=run_seed("tune", family, n, algo, prm, s), max_flips=cap)
    return [(score(r, cap), r["flips"], r["solved"], r["cpu"], r["work"])], time.process_time() - t0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["train", "tune"])
    ap.add_argument("--arm", choices=list(ARMS))
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--tuning", type=Path)
    ap.add_argument("--pairs", type=int, default=32)
    ap.add_argument("--sigma", type=float, default=0.1)
    ap.add_argument("--lr", type=float, default=0.05)
    ap.add_argument("--workers", type=int, default=16)
    ap.add_argument("--smoke", action="store_true", help="tiny curriculum for a code check")
    a = ap.parse_args()
    if a.cmd == "train":
        wp = (2.3, 1.0)
        if a.arm == "L2w":
            rows = json.loads(a.tuning.read_text())["probsat"]["grid"]
            wp = tuple(min((r for r in rows if r["algo"] == "probsat_poly"), key=lambda r: r["mean_log_flips"])["params"])
        cur = [(200, 3, 4, 60_000), (400, 2, 4, 300_000), (800, 2, 4, 1_500_000)] if a.smoke else CURRICULUM
        if a.smoke:
            VAL_COUNT = 8
        train(a.arm, a.seed, a.out, a.pairs, a.sigma, a.lr, a.workers, wp, cur)
    else:
        tune(a.out, a.workers)
