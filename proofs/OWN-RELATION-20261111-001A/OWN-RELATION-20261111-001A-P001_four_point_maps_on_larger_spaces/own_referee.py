#!/usr/bin/env python3
"""Referee (own_referee.py) for OWN-RELATION-20261111-001A, fresh code: it imports nothing from own_lib or the learning line, and reads
only spaces.json (written by check.py --part export) and result_census.json.

R1. The classes, recomputed: the self-dual maps of four inputs, their orbits under permuting and negating inputs and negating the
    output found by closing under generators, the orbits that use all four inputs (expected: four), and which of them contain a map
    that, with one input fixed at 0, is a mod-3 bit (a function of the count of three literals, equal at counts 0 and 3, not constant).
R2. On every exported space (every tenth space read, by label, and every space with a C or D instance): floor states from the lines
    and signs alone; every free four-point set; every decided output classified by orbit; per-space counts compared with the census."""
import itertools
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent


def value(t, x):
    return (t >> (x[0] * 8 + x[1] * 4 + x[2] * 2 + x[3])) & 1


def from_fn(f):
    t = 0
    for x in itertools.product((0, 1), repeat=4):
        t |= int(f(x)) << (x[0] * 8 + x[1] * 4 + x[2] * 2 + x[3])
    return t


GENS = [lambda t: from_fn(lambda x: value(t, (x[1], x[0], x[2], x[3]))),
        lambda t: from_fn(lambda x: value(t, (x[1], x[2], x[3], x[0]))),
        lambda t: from_fn(lambda x: value(t, (1 - x[0], x[1], x[2], x[3]))),
        lambda t: t ^ 0xFFFF]


def orbits():
    selfdual = [t for t in range(1 << 16)
                if all(value(t, x) != value(t, tuple(1 - v for v in x)) for x in itertools.product((0, 1), repeat=4))]
    left, out = set(selfdual), []
    while left:
        seed = min(left)
        orb, todo = {seed}, [seed]
        while todo:
            t = todo.pop()
            for g in GENS:
                u = g(t)
                if u not in orb:
                    orb.add(u)
                    todo.append(u)
        out.append(orb)
        left -= orb
    return selfdual, out


def uses_all(t):
    return all(any(value(t, x) != value(t, x[:i] + (1 - x[i],) + x[i + 1:]) for x in itertools.product((0, 1), repeat=4))
               for i in range(4))


def mod3_bit(h):
    """h: 8 values of three inputs; a function of the literal count, equal at 0 and 3, not constant"""
    for eps in itertools.product((0, 1), repeat=3):
        val = {}
        ok = True
        for x in itertools.product((0, 1), repeat=3):
            c = sum(a ^ e for a, e in zip(x, eps))
            if val.setdefault(c, h[x]) != h[x]:
                ok = False
                break
        if ok and val[0] == val[3] and len(set(val.values())) > 1:
            return True
    return False


def restrictions(t):
    for r in range(4):
        h = {}
        for x in itertools.product((0, 1), repeat=3):
            full = list(x)
            full.insert(r, 0)
            h[x] = value(t, tuple(full))
        yield h


def r1():
    selfdual, orbs = orbits()
    four = [o for o in orbs if uses_all(min(o))]
    named = {"A": from_fn(lambda x: 2 * x[0] + x[1] + x[2] + x[3] >= 3), "B": from_fn(lambda x: x[0] + x[1] + (x[0] ^ x[2] ^ x[3]) >= 2),
             "C": from_fn(lambda x: (x[0] ^ x[1] ^ x[2]) if x[3] == x[0] else int(x[0] + x[1] + x[2] >= 2)),
             "D": from_fn(lambda x: x[0] ^ int(len(set(x[1:])) > 1))}
    label = {}
    for o in four:
        names = [k for k, t in named.items() if t in o]
        label[min(o)] = names[0] if len(names) == 1 else "?"
    capable = sorted(label[min(o)] for o in four if any(mod3_bit(h) for t in o for h in restrictions(t)))
    return {"self-dual maps": len(selfdual), "orbits using all four inputs": len(four), "named": sorted(label.values()),
            "orbits that can give a mod-3 bit": capable}, {t: label[min(o)] for o in four for t in o}


def floor(space, signs):
    n = space["n"]
    x = np.arange(1 << n, dtype=np.int64)
    ok = np.ones(1 << n, dtype=bool)
    for i, pts in enumerate(space["lines"]):
        v = [((x >> p) & 1) ^ signs[3 * i + j] for j, p in enumerate(pts)]
        ok &= ~((v[0] == v[1]) & (v[1] == v[2]))
    return x[ok]


def count_space(space, cls_of):
    counts = {"A": 0, "B": 0, "C": 0, "D": 0}
    n = space["n"]
    for signs in space["classes"]:
        st = floor(space, signs)
        if len(st) == 0:
            continue
        bits = ((st[:, None] >> np.arange(n)[None, :]) & 1).astype(np.int64)
        for Q in itertools.combinations(range(n), 4):
            key = bits[:, Q[0]] * 8 + bits[:, Q[1]] * 4 + bits[:, Q[2]] * 2 + bits[:, Q[3]]
            size = np.bincount(key, minlength=16)
            if (size == 0).any():
                continue
            ones = np.zeros((16, n), dtype=np.int64)
            np.add.at(ones, key, bits)
            decided = np.all((ones == 0) | (ones == size[:, None]), axis=0)
            for o in np.nonzero(decided)[0]:
                if o in Q:
                    continue
                t = sum(int(ones[p, o] > 0) << p for p in range(16))
                if t in cls_of:
                    counts[cls_of[t]] += 1
    return counts


def main():
    out1, cls_of = r1()
    spaces = json.loads((HERE / "spaces.json").read_text())["spaces"]
    census = {r["label"]: r for r in json.loads((HERE / "result_census.json").read_text())["checks"]["result"]["rows"]}
    rows = []
    for sp in spaces:
        mine = count_space(sp, cls_of)
        theirs = {k: census[sp["label"]]["tally"].get(k, 0) for k in "ABCD"}
        rows.append({"label": sp["label"], "referee": mine, "census": theirs, "agree": mine == theirs})
    res = {"R1 classes": out1, "R2 spaces": rows,
           "passed": out1["orbits using all four inputs"] == 4 and out1["orbits that can give a mod-3 bit"] == ["C", "D"]
           and all(r["agree"] for r in rows)}
    (HERE / "referee.json").write_text(json.dumps(res, indent=1) + "\n")
    print("referee passed" if res["passed"] else "referee FAILED")
    sys.exit(0 if res["passed"] else 1)


if __name__ == "__main__":
    main()
