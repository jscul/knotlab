"""The frozen census of SHIFT-COUNT-20261112-001A-E001 (contract.json beside this file): a certified search for travelling
directions on the 169 travelling bases of COMMON-FOLD-20261112-001A-E001 (and base 16 as the negative control).

Family: sets A of 2 to 4 cells of the box [0, 2] x [0, 2] holding (0, 0), every pattern p (first value 0), every primitive shift
(a, b) with |a|, |b| <= 6 (both senses), and its multiples k t, k = 1 .. 4. Forced: p on A is satisfiable and forces sigma(p) on A + k t
(window SAT on columns -30 .. 30 by rows -30 .. 30; sound). Certified: p with sigma(p) on A + k t, and every pattern on A, carried by a
doubly periodic state (COMMON-FOLD's tori) or an eventually periodic strip in the frame of t (FAR-BOUND's, P >= the kinds' along-span,
Q from 3 to 16). Per base: the primitive directions forced, certified, and forced but uncertified; rank (forced; certified), never
called less than "rank >= 1, no second direction in the family".

    .venv/bin/python -B experiments/SHIFT-COUNT-20261112-001A/SHIFT-COUNT-20261112-001A-E001_second_direction/census.py [--workers 6] [--cap 1800]
Output: artifacts/SHIFT-COUNT-20261112-001A/SHIFT-COUNT-20261112-001A-E001_second_direction/rows.jsonl, log.txt
"""
from __future__ import annotations

import importlib.util
import itertools
import json
import math
import multiprocessing as mp
import os
import sys
import time

from pysat.solvers import Minisat22

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
OUT = os.path.join(ROOT, "artifacts", "SHIFT-COUNT-20261112-001A", "SHIFT-COUNT-20261112-001A-E001_second_direction")
spec = importlib.util.spec_from_file_location("fb", os.path.join(ROOT, "experiments/FAR-BOUND-20261112-001A/FAR-BOUND-20261112-001A-E001_bounded_far/census.py"))
F = importlib.util.module_from_spec(spec)
spec.loader.exec_module(F)
T, C = F.T, F.C
BOX3 = [(x, y) for x in range(3) for y in range(3)]
PRIM = sorted({(a // math.gcd(abs(a), abs(b)), b // math.gcd(abs(a), abs(b))) for a in range(-6, 7) for b in range(-6, 7) if (a, b) != (0, 0)})


def certified(kinds, A, p, tt, fl):
    fix = list(zip(A, p)) + [((c[0] + tt[0], c[1] + tt[1]), v ^ fl) for c, v in zip(A, p)]
    pats = [list(zip(A, (0,) + q)) for q in itertools.product((0, 1), repeat=len(A) - 1)]
    if C.carried(kinds, fix) and all(C.carried(kinds, x) for x in pats):
        return True
    tp, g, u = T.frame(tt)
    fr = T.Frame(kinds, tp, u)
    s = F.along_span(fr)
    cells = [c for c, _ in fix]
    cos = [fr.co(c) for c in cells]
    X0, X1 = min(a for a, _ in cos) - 2, max(a for a, _ in cos) + 3
    ext = max(b for _, b in cos) - min(b for _, b in cos)
    evs = [e for e in (F.Eventual(fr, X0, X1, Q, P) for Q in range(max(3, ext + 1), 17) for P in range(max(1, s), 2 * s + 3)) if e.ok]
    def carried_ev(fixlist):
        return any(e.carries([c for c, _ in fixlist], [v for _, v in fixlist]) for e in evs)
    ok = carried_ev(fix) and all(carried_ev(x) for x in pats)
    for e in evs:
        e.close()
    return ok


def run_base(kinds):
    idx, cl = C.window(kinds, (-30, 30, -30, 30))
    s = Minisat22(bootstrap_with=cl)
    forced, cert = {}, {}
    for size in range(2, 5):
        for A in itertools.combinations(BOX3, size):
            if (0, 0) not in A:
                continue
            for tail in itertools.product((0, 1), repeat=size - 1):
                p = (0,) + tail
                assum = [idx[c] * (1 if v else -1) for c, v in zip(A, p)]
                if not s.solve(assumptions=assum):
                    continue
                for d in PRIM:
                    if d in cert:
                        continue
                    for k in (1, 2, 3, 4):
                        tt = (d[0] * k, d[1] * k)
                        hit = None
                        for fl in (0, 1):
                            if all(not s.solve(assumptions=assum + [idx[(c[0] + tt[0], c[1] + tt[1])] * (-1 if (v ^ fl) else 1)]) for c, v in zip(A, p)):
                                hit = fl
                                break
                        if hit is None:
                            continue
                        forced.setdefault(d, {"A": [list(c) for c in A], "p": list(p), "k": k, "sigma": hit})
                        if certified(kinds, A, p, tt, hit):
                            cert[d] = {"A": [list(c) for c in A], "p": list(p), "k": k, "sigma": hit}
                            break
    s.delete()

    def rank(ds):
        ds = list(ds)
        return 2 if any(a[0] * b[1] - a[1] * b[0] for a, b in itertools.combinations(ds, 2)) else (1 if ds else 0)
    return {"forced directions": [list(d) for d in sorted(forced)], "certified directions": [list(d) for d in sorted(cert)],
            "forced, uncertified": [list(d) for d in sorted(set(forced) - set(cert))], "rank forced": rank(forced), "rank certified": rank(cert),
            "certificates": {f"{d[0]},{d[1]}": v for d, v in cert.items()}}


def job(item, q):
    q.put(run_base(item["kinds"]))


def main():
    workers = int(sys.argv[sys.argv.index("--workers") + 1]) if "--workers" in sys.argv else 6
    cap = int(sys.argv[sys.argv.index("--cap") + 1]) if "--cap" in sys.argv else 1800
    os.makedirs(OUT, exist_ok=True)
    items = [{"sample": "base16", "r": 2, "kinds": C.BASE16}] + [{"sample": x["sample"], "r": x["r"], "kinds": x["kinds"]} for x in T.samples()]
    path = os.path.join(OUT, "rows.jsonl")
    done = set()
    if os.path.exists(path):
        done = {(r["sample"], r["r"]) for r in map(json.loads, open(path))}
    pending = [it for it in items if (it["sample"], it["r"]) not in done]
    live, t0 = [], time.time()
    while pending or live:
        while pending and len(live) < workers:
            it = pending.pop(0)
            q = mp.Queue()
            p = mp.Process(target=job, args=(it, q))
            p.start()
            live.append((it, p, q, time.time()))
        time.sleep(0.5)
        for e in list(live):
            it, p, q, st = e
            if not q.empty():
                res = q.get()
                p.join()
                with open(path, "a") as f:
                    f.write(json.dumps({"sample": it["sample"], "r": it["r"], "seconds": round(time.time() - st, 1), **res}) + "\n")
                live.remove(e)
            elif time.time() - st > cap:
                p.terminate()
                p.join()
                with open(path, "a") as f:
                    f.write(json.dumps({"sample": it["sample"], "r": it["r"], "dropped at the cap": cap}) + "\n")
                live.remove(e)
    with open(os.path.join(OUT, "log.txt"), "a") as f:
        f.write(f"finished {len(items)} items in {round(time.time() - t0, 1)} s\n")


if __name__ == "__main__":
    main()
