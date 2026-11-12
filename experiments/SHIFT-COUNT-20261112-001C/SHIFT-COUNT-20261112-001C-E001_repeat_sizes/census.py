"""The repeat-size test frozen in research/LINE-LOCK-20261112-001/preregistration.md (last section; the harmony thread's, the
advisor's design), run here as SHIFT-COUNT-20261112-001C-E001 (contract.json beside this file).

Patterns: on base 16, the parts of its heddle bonds (FAR-BOUND's control) whose patterns no doubly periodic state of period at most 8
carries; on each of the 29 bases FAR-BOUND's recheck left unresolved, the first window-only set's first part pattern that no doubly
periodic state up to 8 carries (in census order of targets). For each pattern: C = the period lattices <(n, 0), (k, m)> of the frame
(n, m <= 24, 0 <= k < n) carrying it; the divisibility fit (is C = {n, m : d1 | n, d2 | m} or one congruence on (n, k, m) within the
range); whether C holds every size past a threshold; in each of up to 5 certifying states, the count along each line (rows, columns,
diagonals of the frame) of equal neighbouring pairs along that line, and whether some count is equal on all parallel lines; and the
rival control, computed without solving: for each lattice, whether the pattern's images under the lattice collide (two cells of the
pattern identified), compared with C.

    .venv/bin/python -B experiments/SHIFT-COUNT-20261112-001C/SHIFT-COUNT-20261112-001C-E001_repeat_sizes/census.py [--workers 4] [--cap 1800]
Output: artifacts/SHIFT-COUNT-20261112-001C/SHIFT-COUNT-20261112-001C-E001_repeat_sizes/rows.jsonl, log.txt
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
OUT = os.path.join(ROOT, "artifacts", "SHIFT-COUNT-20261112-001C", "SHIFT-COUNT-20261112-001C-E001_repeat_sizes")
spec = importlib.util.spec_from_file_location("fb", os.path.join(ROOT, "experiments/FAR-BOUND-20261112-001A/FAR-BOUND-20261112-001A-E001_bounded_far/census.py"))
F = importlib.util.module_from_spec(spec)
spec.loader.exec_module(F)
T, C = F.T, F.C
REC = os.path.join(ROOT, "artifacts/FAR-BOUND-20261112-001A/FAR-BOUND-20261112-001A-E001_bounded_far/recheck.jsonl")
NMAX = 24


def lattice_solver(fr, n, k, m):
    """States invariant under n e1 and k e1 + m e2 in frame coordinates."""
    def rep(z):
        a, b = fr.co(z)
        j = b // m
        b0 = b - j * m
        a0 = (a - j * k) % n
        return (a0, b0)
    cells = [(a, b) for a in range(n) for b in range(m)]
    idx = {c: i + 1 for i, c in enumerate(cells)}
    cl = []
    for a, b in cells:
        z = fr.cell(a, b)
        for kd in fr.kinds:
            v = [idx[rep((z[0] + dx, z[1] + dy))] for dx, dy in kd]
            cl += [v, [-w for w in v]]
    return rep, idx, cl


def run_pattern(fr, cells, p):
    C_, collide, states = [], [], []
    for n in range(1, NMAX + 1):
        for m in range(1, NMAX + 1):
            for k in range(0, n):
                rep, idx, cl = lattice_solver(fr, n, k, m)
                imgs = [idx[rep(c)] for c in cells]
                col = len(set(imgs)) < len(imgs)
                lits = [w * (1 if v else -1) for w, v in zip(imgs, p)]
                if any(-l in lits for l in lits):
                    collide.append((n, k, m))
                    continue
                if col:
                    collide.append((n, k, m))
                with Minisat22(bootstrap_with=cl) as s:
                    if s.solve(assumptions=lits):
                        C_.append((n, k, m))
                        if len(states) < 5:
                            mod = set(x for x in s.get_model() if x > 0)
                            states.append((n, k, m, {c: (idx[c] in mod) for c in idx}))
    return C_, collide, states


def fit(C_):
    S = set(C_)
    allL = [(n, k, m) for n in range(1, NMAX + 1) for m in range(1, NMAX + 1) for k in range(n)]
    out = {"size": len(S)}
    best = None
    for d1 in range(1, 13):
        for d2 in range(1, 13):
            pred = {(n, k, m) for n, k, m in allL if n % d1 == 0 and m % d2 == 0}
            if pred and S and S <= pred:
                frac = len(S) / len(pred)
                if best is None or frac > best[0]:
                    best = (frac, d1, d2)
    out["best divisibility (d1 | n, d2 | m): share of predicted lattices carrying"] = best
    thr = None
    for t in range(1, NMAX + 1):
        if all((n, k, m) in S for n, k, m in allL if n >= t and m >= t):
            thr = t
            break
    out["every size from threshold"] = thr
    return out


def line_counts(state, n, k, m):
    vals = state
    res = {}
    for name, d in (("along", (1, 0)), ("across", (0, 1)), ("diagonal", (1, 1))):
        counts = []
        seen = set()
        for start in vals:
            if start in seen:
                continue
            line, z = [], start
            for _ in range(4 * n * m):
                if z in seen and z == start and line:
                    break
                seen.add(z)
                line.append(z)
                a, b = z[0] + d[0], z[1] + d[1]
                j = b // m
                b0 = b - j * m
                z = ((a - j * k) % n, b0)
                if z == start:
                    break
            cnt = sum(vals[line[i]] == vals[line[(i + 1) % len(line)]] for i in range(len(line)))
            counts.append(round(cnt / len(line), 4))
        res[name] = {"equal on all parallel lines": len(set(counts)) == 1, "values": sorted(set(counts))[:6]}
    return res


def item_patterns():
    items = []
    sm16 = {"kinds": C.BASE16, "travels": C.read_base(C.BASE16)["travels"]}
    tr = sm16["travels"]
    tp, g, u = T.frame(tuple(tr["t"]))
    fr = T.Frame(C.BASE16, tp, u)
    part = [fr.cell(0, b) for b in (0, -1, 1, 5)] + [fr.cell(8, 5)]
    for p in ((0, 0, 0, 0, 1), (0, 0, 0, 1, 0)):
        items.append({"base": "base16", "kinds": C.BASE16, "frame": [tp, u], "cells": part, "pattern": p})
    sms = {(x["sample"], x["r"]): x for x in T.samples()}
    for r in map(json.loads, open(REC)):
        if r.get("class") != "unresolved":
            continue
        sm = sms[(r["sample"], r["r"])]
        trv = sm["travels"]
        tp, g, u = T.frame(tuple(trv["t"]))
        fr = T.Frame(sm["kinds"], tp, u)
        a0 = min(fr.co(tuple(c))[0] for c in trv["A"])
        got = None
        for key, v in r["profile"].items():
            S = v.get("window-only set")
            if not S:
                continue
            alpha, y = map(int, key.split(","))
            x = fr.cell(a0 + alpha, y)
            parts = [[tuple(c) for c in S]] + [[tuple(c) for c in S if tuple(c) != tuple(s)] + [x] for s in S]
            tori = [fr.torus_solver(P, Q) for P in range(1, 9) for Q in range(1, 9)]
            tori = [t for t in tori if t]
            for P_ in parts:
                for q in itertools.product((0, 1), repeat=len(P_) - 1):
                    pat = (0,) + q
                    ok = False
                    for s, rep, idx in tori:
                        lits = [idx[rep(c)] * (1 if b else -1) for c, b in zip(P_, pat)]
                        if not any(-l in lits for l in lits) and s.solve(assumptions=lits):
                            ok = True
                            break
                    if not ok:
                        got = (P_, pat)
                        break
                if got:
                    break
            for s, _, _ in tori:
                s.delete()
            if got:
                break
        if got:
            items.append({"base": [r["sample"], r["r"]], "kinds": sm["kinds"], "frame": [tp, u], "cells": got[0], "pattern": got[1]})
        else:
            items.append({"base": [r["sample"], r["r"]], "none": "no part pattern uncarried by tori up to 8"})
    return items


def run_item(it, q):
    if "none" in it:
        q.put({"base": it["base"], "result": it["none"]})
        return
    fr = T.Frame(it["kinds"], tuple(it["frame"][0]), tuple(it["frame"][1]))
    C_, collide, states = run_pattern(fr, it["cells"], it["pattern"])
    f = fit(C_)
    lc = [{"lattice": [n, k, m], **line_counts(st, n, k, m)} for n, k, m, st in states]
    coll = set(collide)
    rival = {"lattices with colliding images": len(coll), "carrying lattices among them": len(set(C_) & coll),
             "C equals the non-colliding lattices": set(C_) == {(n, k, m) for n in range(1, NMAX + 1) for m in range(1, NMAX + 1) for k in range(n)} - coll}
    ref = []
    if not C_:
        ref.append("C empty")
    if f["every size from threshold"] is not None:
        ref.append("every size past a threshold")
    if lc and all(not any(x[d]["equal on all parallel lines"] for d in ("along", "across", "diagonal")) for x in lc):
        ref.append("no line count equal on parallel lines")
    q.put({"base": it["base"], "cells": [list(c) for c in it["cells"]], "pattern": list(it["pattern"]), "C size": len(C_),
           "C sample": C_[:12], "fit": f, "line counts": lc, "rival": rival, "tiling reading refuted by": ref})


def main():
    workers = int(sys.argv[sys.argv.index("--workers") + 1]) if "--workers" in sys.argv else 4
    cap = int(sys.argv[sys.argv.index("--cap") + 1]) if "--cap" in sys.argv else 1800
    os.makedirs(OUT, exist_ok=True)
    t0 = time.time()
    items = item_patterns()
    with open(os.path.join(OUT, "log.txt"), "a") as f:
        f.write(f"items {len(items)} prepared in {round(time.time() - t0, 1)} s\n")
    path = os.path.join(OUT, "rows.jsonl")
    live, pending = [], list(items)
    while pending or live:
        while pending and len(live) < workers:
            it = pending.pop(0)
            q = mp.Queue()
            p = mp.Process(target=run_item, args=(it, q))
            p.start()
            live.append((it, p, q, time.time()))
        time.sleep(0.5)
        for e in list(live):
            it, p, q, st = e
            if not q.empty():
                res = q.get()
                p.join()
                with open(path, "a") as f:
                    f.write(json.dumps(res, default=str) + "\n")
                live.remove(e)
            elif time.time() - st > cap:
                p.terminate()
                p.join()
                with open(path, "a") as f:
                    f.write(json.dumps({"base": it["base"], "dropped at the cap": cap}) + "\n")
                live.remove(e)
    with open(os.path.join(OUT, "log.txt"), "a") as f:
        f.write(f"finished in {round(time.time() - t0, 1)} s\n")


if __name__ == "__main__":
    main()
