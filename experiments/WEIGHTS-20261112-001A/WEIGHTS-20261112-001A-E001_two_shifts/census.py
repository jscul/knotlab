"""The frozen census of WEIGHTS-20261112-001A-E001 (contract.json beside this file): are two unlengthened shifts the rule beyond one
box of knot kinds?

Kinds: the 738 sets of three offsets up to translation in the box [0, 3] x [-3, 3] (171 of them lie in COMMON-FOLD's box
[0, 2] x [-2, 2]). D(k) = the L-infinity diameter of a kind (1 to 6). Weightings W2(r, beta), beta in {0, 1, 2}: a sample draws kinds
one at a time without replacement, each with probability proportional to exp(-beta D(k)) among those left (beta = 0: uniform); its
bases are the first r = 3, 4, 5 kinds drawn (nested prefixes). Seeds: random.Random(70000 + 1000 w + i), w the index of beta, i the
sample. Stopping rule, per weighting: samples i = 0, 1, ... until at least 40 travelling bases with a kind outside the old box have
been classified, or 300 samples.

Per base: COMMON-FOLD's classification (outcome, tied, certified travelling; its census.py, read_base) unchanged; for travelling
bases SHIFT-COUNT's certified second-direction search (sets of 2-4 cells in [0, 2]^2, primitive shifts with entries up to 6 both
senses, multiples up to 4; its census.py, run_base) as the main arm; for travelling bases without a certified second direction in the
main arm, the enlarged arm: sets of 2-4 cells in [0, 3]^2 and primitive shifts with entries up to 8 (multiples up to 4). Stratum: "old
box" when every kind of the base lies in [0, 2] x [-2, 2], else "new kinds". Calibration: the enlarged arm on COMMON-FOLD's travelling
bases with one certified direction in SHIFT-COUNT.

    .venv/bin/python -B experiments/WEIGHTS-20261112-001A/WEIGHTS-20261112-001A-E001_two_shifts/census.py --part census | calibration [--workers 6]
Output: artifacts/WEIGHTS-20261112-001A/WEIGHTS-20261112-001A-E001_two_shifts/{census,calibration}.jsonl
"""
from __future__ import annotations

import importlib.util
import itertools
import json
import math
import multiprocessing as mp
import os
import random
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
OUT = os.path.join(ROOT, "artifacts", "WEIGHTS-20261112-001A", "WEIGHTS-20261112-001A-E001_two_shifts")
spec = importlib.util.spec_from_file_location("sc", os.path.join(ROOT, "experiments/SHIFT-COUNT-20261112-001A/SHIFT-COUNT-20261112-001A-E001_second_direction/census.py"))
S = importlib.util.module_from_spec(spec)
spec.loader.exec_module(S)
C, T = S.C, S.T
BETAS = (0, 1, 2)
RS = (3, 4, 5)
SC_ROWS = os.path.join(ROOT, "artifacts/SHIFT-COUNT-20261112-001A/SHIFT-COUNT-20261112-001A-E001_second_direction/rows.jsonl")


def kinds2():
    cells = [(x, y) for x in range(0, 4) for y in range(-3, 4)]
    return sorted({C.norm(t) for t in itertools.combinations(cells, 3)})


K2 = kinds2()
OLD = set(C.KINDS)


def diam(k):
    return max(max(abs(a[0] - b[0]), abs(a[1] - b[1])) for a in k for b in k)


def draw(w, i):
    rng = random.Random(70000 + 1000 * w + i)
    beta = BETAS[w]
    left = list(K2)
    out = []
    for _ in range(max(RS)):
        ws = [math.exp(-beta * diam(k)) for k in left]
        x = rng.random() * sum(ws)
        acc = 0.0
        for j, wt in enumerate(ws):
            acc += wt
            if acc >= x:
                break
        out.append(left.pop(j))
    return out


def enlarged(kinds):
    old_box, old_prim = S.BOX3, S.PRIM
    S.BOX3 = [(x, y) for x in range(4) for y in range(4)]
    S.PRIM = sorted({(a // math.gcd(abs(a), abs(b)), b // math.gcd(abs(a), abs(b))) for a in range(-8, 9) for b in range(-8, 9) if (a, b) != (0, 0)})
    try:
        return S.run_base(kinds)
    finally:
        S.BOX3, S.PRIM = old_box, old_prim


def per_base(kinds):
    rb = C.read_base(kinds)
    cls = C.classify(rb)
    res = {"kinds": [list(map(list, k)) for k in kinds], "outcome": rb["outcome"], "class": cls,
           "stratum": "old box" if all(k in OLD for k in kinds) else "new kinds",
           "diameters": [diam(k) for k in kinds]}
    if cls == "travels":
        m = S.run_base(kinds)
        res["main"] = {k: m[k] for k in ("certified directions", "forced, uncertified", "rank forced", "rank certified")}
        if m["rank certified"] < 2:
            e = enlarged(kinds)
            res["enlarged"] = {k: e[k] for k in ("certified directions", "forced, uncertified", "rank forced", "rank certified")}
    return res


def job_sample(item, q):
    w, i = item
    order = draw(w, i)
    q.put({"beta": BETAS[w], "sample": i, "by r": {r: per_base(order[:r]) for r in RS}})


def job_cal(item, q):
    q.put({"enlarged": {k: v for k, v in enlarged(item["kinds"]).items() if k != "certificates"}})


def run_pool(jobs, target, path, workers, cap, stop=None):
    live = []
    pending = list(jobs)
    while pending or live:
        while pending and len(live) < workers and not (stop and stop()):
            it = pending.pop(0)
            q = mp.Queue()
            p = mp.Process(target=target, args=(it, q))
            p.start()
            live.append((it, p, q, time.time()))
        if stop and stop() and not live:
            break
        time.sleep(0.5)
        for e in list(live):
            it, p, q, st = e
            if not q.empty():
                res = q.get()
                p.join()
                tag = it if isinstance(it, tuple) else {"sample": it.get("sample"), "r": it.get("r")}
                with open(path, "a") as f:
                    f.write(json.dumps({"item": tag, "seconds": round(time.time() - st, 1), **res}) + "\n")
                live.remove(e)
            elif time.time() - st > cap:
                p.terminate()
                p.join()
                tag = it if isinstance(it, tuple) else {"sample": it.get("sample"), "r": it.get("r")}
                with open(path, "a") as f:
                    f.write(json.dumps({"item": tag, "dropped at the cap": cap}) + "\n")
                live.remove(e)


def main():
    part = sys.argv[sys.argv.index("--part") + 1]
    workers = int(sys.argv[sys.argv.index("--workers") + 1]) if "--workers" in sys.argv else 6
    os.makedirs(OUT, exist_ok=True)
    if part == "calibration":
        sc = [r for r in map(json.loads, open(SC_ROWS)) if "rank certified" in r and r["rank certified"] < 2 and r["sample"] != "base16"]
        sms = {(x["sample"], x["r"]): x for x in T.samples()}
        jobs = [{"sample": r["sample"], "r": r["r"], "kinds": sms[(r["sample"], r["r"])]["kinds"]} for r in sc]
        run_pool(jobs, job_cal, os.path.join(OUT, "calibration.jsonl"), workers, 3600)
        return
    path = os.path.join(OUT, "census.jsonl")
    for w in range(len(BETAS)):
        def count_new():
            n = 0
            if not os.path.exists(path):
                return 0
            for line in open(path):
                r = json.loads(line)
                if r.get("beta") != BETAS[w]:
                    continue
                for x in r["by r"].values():
                    if x["class"] == "travels" and x["stratum"] == "new kinds":
                        n += 1
            return n
        jobs = [(w, i) for i in range(300)]
        run_pool(jobs, job_sample, path, workers, 3600, stop=lambda: count_new() >= 40)


if __name__ == "__main__":
    main()
