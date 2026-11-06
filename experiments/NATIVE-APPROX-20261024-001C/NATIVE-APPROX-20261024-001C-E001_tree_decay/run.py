#!/usr/bin/env python3
"""Producer of NATIVE-APPROX-20261024-001C-E001 (boundary influence on native trees).

For each knot, pin probability q and depth L, 100 random native trees are drawn: knots sit at levels 0 to L - 1, every knot has one
parent edge in a uniformly chosen place and two child places, and each child place is a pin (uniform value) with probability q,
otherwise a knot of the next level, or a boundary leaf if the next level is L. The width of a tree is the largest minus the smallest
probability that the root edge is 1, over all values of the boundary leaves. It is computed exactly by interval propagation: a knot's
probability for its parent edge is a ratio of affine functions in each child probability separately, with a positive denominator
(every pair of places of a knot sees all four values), so over a box of child probabilities its extremes are at the corners.
Rows are appended to rows.jsonl as settings finish; result.json is written at the end by summarize().

    python3 -B run.py            run everything (skips settings already in rows.jsonl)
"""

from __future__ import annotations

import hashlib
import itertools
import json
import math
import random
import statistics
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUT = ROOT / "artifacts/NATIVE-APPROX-20261024-001C/NATIVE-APPROX-20261024-001C-E001_tree_decay"
CUBE = list(itertools.product((0, 1), repeat=3))

OPEN = ["000,011,101", "000,011,110", "000,101,110", "001,010,111", "001,100,111", "010,100,111"]
DECAYING = ["000", "000,110", "011,101"]
PERSISTENT = ["000,011,101,110", "001,010,100,111", "001,010,100", "011,101,110", "000,111"]
KNOTS = OPEN + DECAYING + PERSISTENT
DEPTHS = [4, 6, 8, 10, 12, 14, 16]
PINS = [0.0, 0.2]
TREES = 100


def relation(label):
    excluded = {tuple(int(ch) for ch in word) for word in label.split(",")}
    return frozenset(t for t in CUBE if t not in excluded)


def is_knot(R):
    return 0 < len(R) < 8 and all(len({(t[i], t[j]) for t in R}) == 4 for i, j in ((0, 1), (0, 2), (1, 2)))


def node_map(R, s):
    """the probability that place s is 1, as a function of the probabilities of the other two places (in increasing order)"""
    o = [k for k in range(3) if k != s]
    table = []
    for a, b in itertools.product((0, 1), repeat=2):
        allowed = []
        for v in (0, 1):
            t = [0, 0, 0]
            t[s], t[o[0]], t[o[1]] = v, a, b
            allowed.append(tuple(t) in R)
        table.append((a, b, allowed[0], allowed[1]))

    def f(p1, p2):
        z0 = z1 = 0.0
        for a, b, al0, al1 in table:
            w = (p1 if a else 1.0 - p1) * (p2 if b else 1.0 - p2)
            z0 += w * al0
            z1 += w * al1
        return z1 / (z0 + z1)
    return f


def seed_of(label, q, L, i):
    return int(hashlib.sha256(f"{label}|{q}|{L}|{i}".encode()).hexdigest()[:16], 16)


def draw_tree(rng, L, q):
    """nested description: ('knot', slot, child1, child2) | ('pin', v) | ('leaf',)"""
    def node(level):
        s = rng.randrange(3)
        kids = []
        for _ in range(2):
            if rng.random() < q:
                kids.append(("pin", rng.randrange(2)))
            elif level + 1 == L:
                kids.append(("leaf",))
            else:
                kids.append(node(level + 1))
        return ("knot", s, kids[0], kids[1])
    return node(0)


def envelope(tree, maps):
    """(lo, hi, has_leaf): the exact range of P(parent edge = 1) over all boundary values"""
    if tree[0] == "pin":
        return float(tree[1]), float(tree[1]), False
    if tree[0] == "leaf":
        return 0.0, 1.0, True
    _, s, c1, c2 = tree
    lo1, hi1, h1 = envelope(c1, maps)
    lo2, hi2, h2 = envelope(c2, maps)
    f = maps[s]
    vals = [f(a, b) for a in (lo1, hi1) for b in (lo2, hi2)]
    return min(vals), max(vals), h1 or h2


def width(label, q, L, i):
    R = relation(label)
    maps = [node_map(R, s) for s in range(3)]
    tree = draw_tree(random.Random(seed_of(label, q, L, i)), L, q)
    lo, hi, has_leaf = envelope(tree, maps)
    return max(0.0, hi - lo), has_leaf


def run_setting(label, q, L):
    ws, leaves = [], 0
    for i in range(TREES):
        w, h = width(label, q, L, i)
        ws.append(w)
        leaves += h
    return {"knot": label, "q": q, "L": L, "widths": ws, "trees_with_boundary": leaves,
            "median": statistics.median(ws), "mean": statistics.fmean(ws), "max": max(ws)}


def decay_per_level(points):
    """least-squares slope of log(median) against depth, over medians above 1e-13; returned as a factor per level"""
    pts = [(L, math.log(m)) for L, m in points if m > 1e-13]
    if len(pts) < 2:
        return None
    mx = statistics.fmean(L for L, _ in pts)
    my = statistics.fmean(y for _, y in pts)
    slope = sum((L - mx) * (y - my) for L, y in pts) / sum((L - mx) ** 2 for L, _ in pts)
    return math.exp(slope)


def summarize(rows):
    by = {(r["knot"], r["q"], r["L"]): r for r in rows}
    table = []
    for label in KNOTS:
        for q in PINS:
            meds = [(L, by[(label, q, L)]["median"]) for L in DEPTHS]
            table.append({"knot": label, "group": "open" if label in OPEN else "decaying" if label in DECAYING else "persistent",
                          "q": q, "median": [m for _, m in meds], "mean": [by[(label, q, L)]["mean"] for L in DEPTHS],
                          "max": [by[(label, q, L)]["max"] for L in DEPTHS],
                          "trees_with_boundary": [by[(label, q, L)]["trees_with_boundary"] for L in DEPTHS],
                          "decay_per_level": decay_per_level(meds)})

    def decays(label, q):
        m4, m12 = by[(label, q, 4)]["median"], by[(label, q, 12)]["median"]
        return m12 < 1e-3 and m12 <= 0.01 * m4
    P1 = {f"{label} q={q}": decays(label, q) for label in OPEN for q in PINS}
    P2 = {f"{label} q={q}": decays(label, q) for label in DECAYING for q in PINS}
    P3 = {label: by[(label, 0.0, 12)]["median"] >= 0.5 for label in PERSISTENT}
    summary = {"P1_open_knots_decay": all(P1.values()), "P2_windable_controls_decay": all(P2.values()),
               "P3_persistence_controls": all(P3.values()), "P1_by_setting": P1, "P2_by_setting": P2, "P3_by_knot": P3}
    return table, summary


def verdict_of(controls, summary):
    if not controls or not all(controls.values()) or not summary["P3_persistence_controls"]:
        return "invalid"
    if not summary["P1_open_knots_decay"]:
        return "refuted"
    return "supported" if summary["P2_windable_controls_decay"] else "inconclusive"


def main() -> int:
    assert all(is_knot(relation(label)) for label in KNOTS)
    OUT.mkdir(parents=True, exist_ok=True)
    rows_path = OUT / "rows.jsonl"
    done = set()
    if rows_path.exists():
        for line in rows_path.read_text().splitlines():
            r = json.loads(line)
            done.add((r["knot"], r["q"], r["L"]))
    t0 = time.time()
    with rows_path.open("a") as fh:
        for L in DEPTHS:
            for label in KNOTS:
                for q in PINS:
                    if (label, q, L) in done:
                        continue
                    fh.write(json.dumps(run_setting(label, q, L), sort_keys=True) + "\n")
                    fh.flush()
    rows = [json.loads(line) for line in rows_path.read_text().splitlines()]
    table, summary = summarize(rows)
    controls = json.loads((OUT / "controls.json").read_text()) if (OUT / "controls.json").exists() else {}
    verdict = verdict_of(controls, summary)
    result = {"schema_version": 1, "experiment_id": "NATIVE-APPROX-20261024-001C-E001", "ticket": "NATIVE-APPROX-20261024-001C",
              "evidence_stage": "confirmatory", "verdict": verdict, "summary": summary, "controls": controls,
              "table": table, "rows": len(rows), "wall_seconds_this_run": round(time.time() - t0, 1)}
    (OUT / "result.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"verdict": verdict, "summary": {k: v for k, v in summary.items() if not k.endswith(("setting", "knot"))}}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
