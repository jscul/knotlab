#!/usr/bin/env python3
"""After the run (not frozen), second pass: which maps of four held points occur, and why none gives a count mod 3.

For every free set Q of four held points (all 16 patterns occur) on every class of every census space, each decided output that depends
on all four is reduced to its class under permuting and negating inputs and negating the output (NPN). For each choice of one of the
four as the reference held at 0, the output's map of the other three is tested for being a 'mod-3 bit': a function of the count of
three literals taking the same value at counts 0 and 3 (exactly one, exactly two, not-all-equal, or a negation). A count mod 3 needs
two such bits on the same held points; P2 found none.

    PYTHONPATH=tools .venv/bin/python3 -B after_run_classes.py [--write]"""
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


def bit(t, p):
    return (t >> p) & 1


def transform(t, perm, neg, oneg):
    out = 0
    for p in range(16):
        x = [(p >> (3 - i)) & 1 for i in range(4)]
        y = [x[perm[i]] ^ ((neg >> i) & 1) for i in range(4)]
        q = sum(y[i] << (3 - i) for i in range(4))
        out |= (bit(t, q) ^ oneg) << p
    return out


NPN = {}


def npn(t):
    if t not in NPN:
        NPN[t] = min(transform(t, perm, neg, o) for perm in itertools.permutations(range(4)) for neg in range(16) for o in (0, 1))
    return NPN[t]


MOD3_BITS = set()
for eps in range(8):
    for vals in ((0, 1, 0, 0), (0, 0, 1, 0), (0, 1, 1, 0)):
        for o in (0, 1):
            MOD3_BITS.add(sum((vals[bin(k ^ eps).count("1")] ^ o) << k for k in range(8)))


def restrict(t, r):
    """the 3-input map at reference input r = 0 (pattern bit 3 - i is input i), inputs in their order with r removed"""
    others = [i for i in range(4) if i != r]
    out = 0
    for k in range(8):
        x = [0] * 4
        for j, i in enumerate(others):
            x[i] = (k >> (2 - j)) & 1
        p = sum(x[i] << (3 - i) for i in range(4))
        out |= bit(t, p) << k
    return out


def essential(t):
    return sum(1 for i in range(4) if any(bit(t, p) != bit(t, p ^ (1 << (3 - i))) for p in range(16)))


def job(label):
    import hold_lib as H
    kind, rest = label.split(" ", 1)
    if kind == "torus":
        K = H.SL.KnotSpace(H.SL.torus(*(int(v) for v in rest.strip("()").split(","))))
    else:
        n, g, s = (int(x.split("=")[1]) for x in rest.split())
        K = H.N.steered(n, g, s)[1]
    classes, mod3 = Counter(), Counter()
    for s in H.U.all_classes(K):
        rows = H.U.floor_states(K, s)
        if len(rows) == 0:
            continue
        for Q in itertools.combinations(range(K.n), 4):
            key = rows[:, Q[0]].astype(np.int64) * 8 + rows[:, Q[1]] * 4 + rows[:, Q[2]] * 2 + rows[:, Q[3]]
            order = np.argsort(key, kind="stable")
            ks = key[order]
            if len(np.unique(ks)) < 16:
                continue
            starts = np.searchsorted(ks, P16)
            R = rows[order]
            lo, hi = np.minimum.reduceat(R, starts, axis=0), np.maximum.reduceat(R, starts, axis=0)
            dec = np.all(lo == hi, axis=0)
            tab = (lo.astype(np.int64) << P16[:, None]).sum(axis=0)
            per_ref = Counter()
            for o in np.nonzero(dec)[0]:
                if o in Q:
                    continue
                t = int(tab[o])
                if essential(t) == 4:
                    classes[format(npn(t), "016b")] += 1
                for r in range(4):
                    if restrict(t, r) in MOD3_BITS:
                        per_ref[r] += 1
            for r, c in per_ref.items():
                mod3["(four-set, reference) with one mod-3 bit"] += c == 1
                mod3["(four-set, reference) with two or more mod-3 bits"] += c >= 2
    return {"label": label, "classes": dict(classes), "mod3": dict(mod3)}


def main():
    if os.environ.get("PYTHONHASHSEED") != "0":
        os.execve(sys.executable, [sys.executable, "-B"] + sys.argv, {**os.environ, "PYTHONHASHSEED": "0"})
    labels = [r["label"] for part in ("tori", "steered")
              for r in json.loads((HERE / ("result_%s.json" % part)).read_text())["checks"]["result"]["rows"] if "tally" in r]
    with Pool(20) as pool:
        rows = pool.map(job, labels, chunksize=1)
    classes, mod3 = Counter(), Counter()
    for r in rows:
        classes.update(r["classes"])
        mod3.update(r["mod3"])
    out = {"spaces": len(rows), "NPN classes of outputs depending on all four held points": dict(classes.most_common()),
           "mod-3 bits": dict(mod3), "mod-3 bits in total": len(MOD3_BITS), "seconds": round(time.time() - T0, 1)}
    print(json.dumps(out, indent=1)[:4000])
    if "--write" in sys.argv:
        (HERE / "result_after_classes.json").write_text(json.dumps({"rows": rows, "summary": out}, indent=1) + "\n")


if __name__ == "__main__":
    main()
