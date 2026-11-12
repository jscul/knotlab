"""The frozen census of SHIFT-COUNT-20261112-001B-E001 (contract.json beside this file): does bond distance across keep growing on
one-direction bases? The advisor's structural discriminator, then translation tests and one exhaustive step.

Bases: FAR-BOUND's five creeping bases ((17, 4), (17, 5), (109, 3), (112, 4), (183, 4)) and its five one-direction bases that stayed
bounded to 23 across (by its exploratory second_direction.json), all fixed now.
  S1 (structure, from FAR-BOUND's far.jsonl): for each base, the least certified bond at its largest certified |y|: the largest gap in
     across-count between consecutive cells of S u {x}; "relay" when it is at most 6, "two clusters" when it exceeds |y| / 2.
  S2 (translation): for each two-cluster bond, the far cluster (the cells within 6 across-counts of x, with x) translated by s u for
     s = 1 .. 12, the near cluster kept: is the same-size set a certified bond at y + s, y + 2 s and at y + s * ceil(40 / s)? Reported:
     the least s working at all three (none: "no translation").
  S3 (one more step, creeping bases): the exhaustive least certified bond at 10 along and y = 27 * sign (the sign of the base's
     largest rise; 27 = 23 mod 4), |S| <= 6, the strip [min(0,y) - 2, max(0,y) + 2]; "censored" if none within the cap.
Certificates and windows as in FAR-BOUND's census. Each base in its own process, written as it finishes, capped at 3,600 s.

    .venv/bin/python -B experiments/SHIFT-COUNT-20261112-001B/SHIFT-COUNT-20261112-001B-E001_growth_signature/census.py [--workers 5]
Output: artifacts/SHIFT-COUNT-20261112-001B/SHIFT-COUNT-20261112-001B-E001_growth_signature/rows.jsonl
"""
from __future__ import annotations

import importlib.util
import json
import math
import multiprocessing as mp
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
OUT = os.path.join(ROOT, "artifacts", "SHIFT-COUNT-20261112-001B", "SHIFT-COUNT-20261112-001B-E001_growth_signature")
spec = importlib.util.spec_from_file_location("fb", os.path.join(ROOT, "experiments/FAR-BOUND-20261112-001A/FAR-BOUND-20261112-001A-E001_bounded_far/census.py"))
F = importlib.util.module_from_spec(spec)
spec.loader.exec_module(F)
T, C = F.T, F.C
FAR = os.path.join(ROOT, "artifacts/FAR-BOUND-20261112-001A/FAR-BOUND-20261112-001A-E001_bounded_far/far.jsonl")
CREEP = [(17, 4), (17, 5), (109, 3), (112, 4), (183, 4)]
BOUNDED = [(11, 5), (109, 4), (137, 4), (97, 5), (133, 4)]


def frame_of(sm):
    tr = sm["travels"]
    tp, g, u = T.frame(tuple(tr["t"]))
    fr = T.Frame(sm["kinds"], tp, u)
    a0 = min(fr.co(tuple(c))[0] for c in tr["A"])
    return fr, a0


def classify_set(fr, a0, S, alpha, y):
    lo, hi = min(min(fr.co(tuple(c))[1] for c in S), y) - 2, max(max(fr.co(tuple(c))[1] for c in S), y) + 2
    t = F.Tester(fr, a0, alpha, lo, hi, a0 - 2, a0 + alpha + 3)
    v = t.classify([tuple(c) for c in S], fr.cell(a0 + alpha, y))
    t.close()
    return v


def run(key, q):
    sm = {(x["sample"], x["r"]): x for x in T.samples()}[key]
    fr, a0 = frame_of(sm)
    far = {(r["sample"], r["r"]): r for r in map(json.loads, open(FAR)) if "far" in r}[key]["far"]
    best = None
    for t, v in far.items():
        alpha, y = map(int, t.split(","))
        if v.get("set") and (best is None or abs(y) > abs(best[1]) or (abs(y) == abs(best[1]) and alpha == 10)):
            best = (alpha, y, v["set"], v["b_cert"])
    res = {"key": list(key)}
    if best is None:
        res["S1"] = "no certified far bond"
        q.put(res)
        return
    alpha, y, S, b = best
    acr = sorted([fr.co(tuple(c))[1] for c in S] + [y])
    gap = max(b2 - b1 for b1, b2 in zip(acr, acr[1:]))
    kind = "relay" if gap <= 6 else ("two clusters" if gap > abs(y) / 2 else "between")
    res["S1"] = {"target": [alpha, y], "b": b, "across-counts": acr, "largest gap": gap, "kind": kind}
    if kind == "two clusters":
        near = [c for c in S if abs(fr.co(tuple(c))[1] - y) > 6]
        farc = [c for c in S if abs(fr.co(tuple(c))[1] - y) <= 6]
        found = None
        for s in range(1, 13):
            ok = True
            for yy in (y + s * (1 if y > 0 else -1), y + 2 * s * (1 if y > 0 else -1), y + s * math.ceil(40 / s) * (1 if y > 0 else -1)):
                d = yy - y
                S2 = near + [list(fr.cell(fr.co(tuple(c))[0], fr.co(tuple(c))[1] + d)) for c in farc]
                if classify_set(fr, a0, S2, alpha, yy) != "bond":
                    ok = False
                    break
            if ok:
                found = s
                break
        res["S2"] = {"least translation working at three offsets": found}
    if key in CREEP:
        sgn = 1 if any(abs(int(t.split(",")[1])) >= 19 and t.split(",")[1][0] != "-" and v["b_cert"] and v["b_cert"] >= 6 for t, v in far.items()) else -1
        yy = 27 * sgn
        lo, hi = min(0, yy) - 2, max(0, yy) + 2
        tester = F.Tester(fr, a0, 10, lo, hi, a0 - 2, a0 + 13)
        strip = [fr.cell(a0, bb) for bb in range(lo, hi + 1)]
        firsts = [v["set"] for v in far.values() if v.get("set")]
        r_ = F.least(tester, strip, fr.cell(a0, 0), fr.cell(a0 + 10, yy), 6, firsts)
        tester.close()
        b23 = far.get(f"10,{23 * sgn}", {}).get("b_cert")
        res["S3"] = {"y": yy, "b_cert(27)": r_["b_cert"], "b_win(27)": r_["b_win"], "b_cert(23)": b23}
    q.put(res)


def main():
    workers = int(sys.argv[sys.argv.index("--workers") + 1]) if "--workers" in sys.argv else 5
    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, "rows.jsonl")
    pending, live = list(CREEP + BOUNDED), []
    while pending or live:
        while pending and len(live) < workers:
            k = pending.pop(0)
            q = mp.Queue()
            p = mp.Process(target=run, args=(k, q))
            p.start()
            live.append((k, p, q, time.time()))
        time.sleep(0.5)
        for e in list(live):
            k, p, q, st = e
            if not q.empty():
                res = q.get()
                p.join()
                with open(path, "a") as f:
                    f.write(json.dumps({**res, "seconds": round(time.time() - st, 1)}) + "\n")
                live.remove(e)
            elif time.time() - st > 3600:
                p.terminate()
                p.join()
                with open(path, "a") as f:
                    f.write(json.dumps({"key": list(k), "dropped at the cap": 3600}) + "\n")
                live.remove(e)


if __name__ == "__main__":
    main()
