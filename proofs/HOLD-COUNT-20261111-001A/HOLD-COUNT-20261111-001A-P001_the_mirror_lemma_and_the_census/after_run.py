#!/usr/bin/env python3
"""After the run (not frozen): why one reference point buys nothing in the census range.

A reading with a reference r is a reading of four held points (T and r) restricted to r = 0. If no decided output depends on r, the
restricted reading is a self-dual map of T alone and the mirror lemma forbids the count mod 3. So this asks, on every space and class of
the census: for every set Q of four points whose 16 patterns all occur among the floor states, how many held points each decided output
point really depends on (its essential inputs). It also asks, for every triple that reads parity, whether the triple fixes every point.

    PYTHONPATH=tools .venv/bin/python3 -B after_run.py [--write]"""
import itertools
import json
import os
import sys
import time
from collections import Counter
from multiprocessing import Pool
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
T0 = time.time()
P16 = np.arange(16)


def essential(table, k=4):
    """the inputs (bit 3 - i of the pattern is input i) a 16-entry truth table depends on"""
    out = 0
    for i in range(k):
        b = 1 << (k - 1 - i)
        if any(((table >> p) & 1) != ((table >> (p ^ b)) & 1) for p in range(1 << k)):
            out += 1
    return out


def four_held(rows, n):
    tally = Counter()
    for Q in itertools.combinations(range(n), 4):
        key = rows[:, Q[0]].astype(np.int64) * 8 + rows[:, Q[1]] * 4 + rows[:, Q[2]] * 2 + rows[:, Q[3]]
        order = np.argsort(key, kind="stable")
        ks = key[order]
        if len(np.unique(ks)) < 16:
            continue
        tally["free four-sets"] += 1
        starts = np.searchsorted(ks, P16)
        R = rows[order]
        lo, hi = np.minimum.reduceat(R, starts, axis=0), np.maximum.reduceat(R, starts, axis=0)
        dec = np.all(lo == hi, axis=0)
        tab = (lo.astype(np.int64) << P16[:, None]).sum(axis=0)
        for o in np.nonzero(dec)[0]:
            if o in Q:
                continue
            tally["decided outputs with %d essential inputs" % essential(int(tab[o]))] += 1
    return tally


def job(label):
    import hold_lib as H
    kind, rest = label.split(" ", 1)
    if kind == "torus":
        t = tuple(int(v) for v in rest.strip("()").split(","))
        K = H.SL.KnotSpace(H.SL.torus(*t))
    else:
        n, g, s = (int(x.split("=")[1]) for x in rest.split())
        S, K = H.N.steered(n, g, s)
    tally, fixes = Counter(), Counter()
    for s in H.U.all_classes(K):
        rows = H.U.floor_states(K, s)
        if len(rows) == 0:
            continue
        tally.update(four_held(rows, K.n))
        for T in itertools.combinations(range(K.n), 3):
            tabs = H.decided_tables(rows, T)
            if tabs and any(H.is_parity(t) for t in tabs.values()):
                fixes["parity triples"] += 1
                fixes["parity triples fixing every point"] += len(tabs) == K.n - 3
                fixes["floor states = 8 at a parity triple"] += len(rows) == 8
    return {"label": label, "points": K.n, "four held": dict(tally), "parity triples": dict(fixes)}


def main():
    if os.environ.get("PYTHONHASHSEED") != "0":
        os.execve(sys.executable, [sys.executable, "-B"] + sys.argv, {**os.environ, "PYTHONHASHSEED": "0"})
    labels = [r["label"] for part in ("tori", "steered")
              for r in json.loads((HERE / ("result_%s.json" % part)).read_text())["checks"]["result"]["rows"] if "tally" in r]
    with Pool(20) as pool:
        rows = pool.map(job, labels, chunksize=1)
    total4, totalp = Counter(), Counter()
    for r in rows:
        total4.update(r["four held"])
        totalp.update(r["parity triples"])
    by4 = sorted((r["label"], r["four held"].get("decided outputs with 4 essential inputs", 0)) for r in rows
                 if r["four held"].get("decided outputs with 4 essential inputs", 0))
    out = {"spaces": len(rows), "four held, all spaces": dict(total4), "parity triples, all spaces": dict(totalp),
           "spaces with a decided output depending on all four held points": by4, "seconds": round(time.time() - T0, 1)}
    print(json.dumps(out, indent=1)[:4000])
    if "--write" in sys.argv:
        (HERE / "result_after.json").write_text(json.dumps({"rows": rows, "summary": out}, indent=1) + "\n")


if __name__ == "__main__":
    main()
