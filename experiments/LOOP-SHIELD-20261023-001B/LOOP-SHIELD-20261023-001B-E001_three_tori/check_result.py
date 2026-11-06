#!/usr/bin/env python3
"""Independent check of the 3-torus lone-line counts; imports no producer code.

Parses raw_rows.jsonl, the frozen contract and result.json, and:
- checks the roster, totals, the swap-invariance test and the untwisted sector;
- matches the 3 x 3 torus row to the exact counts of TWIST-RELATIONS-20261022-001A-P001;
- builds the 3 x 2 x 2 torus by its own construction and classifies the first 40000 masks in all eight twists with its own code,
  comparing every tally with the slice row;
- recomputes every comparison between twists (exact variance from the joint counts), the symmetry controls and the verdict.

    python3 -B check_result.py
"""

from __future__ import annotations

import json
import math
from fractions import Fraction
from itertools import permutations
from math import gcd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
ART = ROOT / "artifacts/LOOP-SHIELD-20261023-001B" / HERE.name
EXACT = ROOT / "proofs/TWIST-RELATIONS-20261022-001A/TWIST-RELATIONS-20261022-001A-P001_harmonic_structure/result.json"
LABELS = ["torus 3x3 s=0", "2x2x2", "3x2x2 slice", "3x2x2", "3x3x2", "4x3x2", "4x4x2", "3x3x3"]


def cubic(L):
    """Edges of the cubic lattice on L[0] x L[1] x L[2]: (tail, head, offset), one edge per vertex and axis."""
    n = L[0] * L[1] * L[2]
    coords = [(i % L[0], (i // L[0]) % L[1], i // (L[0] * L[1])) for i in range(n)]
    index = {c: i for i, c in enumerate(coords)}
    edges = []
    for c in coords:
        for k in range(3):
            d = list(c)
            d[k] += 1
            wrap = d[k] == L[k]
            d[k] %= L[k]
            edges.append((index[c], index[tuple(d)], tuple(int(wrap and j == k) for j in range(3))))
    return n, edges


def classify(n, edges, x, q):
    t = [sum(a * b for a, b in zip(q, off)) & 1 for (_u, _w, off) in edges]
    out = [[] for _ in range(2 * n)]
    for (u, w, _o), bit, te in zip(edges, x, t):
        if bit:
            out[2 * u].append(2 * w + te)
            out[2 * w + 1 - te].append(2 * u + 1)
        else:
            out[2 * w + te].append(2 * u)
            out[2 * u + 1].append(2 * w + 1 - te)
    m = 2 * n
    rev = [[] for _ in range(m)]
    for i in range(m):
        for j in out[i]:
            rev[j].append(i)
    seen, order = [False] * m, []
    for r in range(m):
        if seen[r]:
            continue
        seen[r] = True
        stack = [(r, 0)]
        while stack:
            v, i = stack.pop()
            if i < len(out[v]):
                stack.append((v, i + 1))
                w = out[v][i]
                if not seen[w]:
                    seen[w] = True
                    stack.append((w, 0))
            else:
                order.append(v)
    comp = [-1] * m
    for r in reversed(order):
        if comp[r] < 0:
            comp[r] = r
            stack = [r]
            while stack:
                v = stack.pop()
                for w in rev[v]:
                    if comp[w] < 0:
                        comp[w] = r
                        stack.append(w)
    inv = any(comp[2 * v] == comp[2 * v + 1] for v in range(n))
    parent, pot = list(range(n)), [(0, 0, 0)] * n

    def find(v):
        acc = (0, 0, 0)
        while parent[v] != v:
            acc = tuple(a + b for a, b in zip(acc, pot[v]))
            v = parent[v]
        return v, acc

    gens = []
    for (u, w, off), te in zip(edges, t):
        if comp[2 * u] == comp[2 * w + te]:
            (ru, pu), (rw, pw) = find(u), find(w)
            d = tuple(a + b - c for a, b, c in zip(pu, off, pw))
            if ru == rw:
                if any(d):
                    gens.append(d)
            else:
                parent[rw], pot[rw] = ru, d
    odd = any(sum(a * b for a, b in zip(q, g)) & 1 for g in gens)
    if not gens:
        return "c", inv, odd
    g0 = gens[0]
    cross = lambda a, b: (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])
    if any(any(cross(g0, g)) for g in gens):
        return "x", inv, odd
    k = gcd(gcd(abs(g0[0]), abs(g0[1])), abs(g0[2]))
    d = tuple(v // k for v in g0)
    if next(v for v in d if v) < 0:
        d = tuple(-v for v in d)
    return d, inv, odd


def norm(c):
    return c if next(v for v in c if v) > 0 else tuple(-v for v in c)


def main() -> int:
    contract = json.loads((HERE / "contract.json").read_text())
    result = json.loads((ART / "result.json").read_text())
    rows = [json.loads(line) for line in (ART / "raw_rows.jsonl").read_text().splitlines()]
    assert contract["status"] == "Frozen" and result["experiment_id"] == contract["experiment_id"] and len(rows) == result["rows"]
    assert [r["label"] for r in rows] == LABELS
    by = {r["label"]: r for r in rows}

    fails = []
    for r in rows:
        n0 = r["sectors"]["0"]["n"]
        assert n0 == r["amount"]
        for s, d in r["sectors"].items():
            if d["c"] + d["x"] + sum(d["lines"].values()) != d["n"] or d["n"] != n0:
                fails.append(f"totals {r['label']} {s}")
            if d["mis"] or (not any(r["twists"][int(s)]) and d["inv"]):
                fails.append(f"swap-invariance {r['label']} {s}")

    # the torus row against TWIST-RELATIONS-20261022-001A-P001
    ex = json.loads(EXACT.read_text())["checks"]["exhaustive"]["3x3 s=0"]
    t = by["torus 3x3 s=0"]
    for s, a in enumerate(t["twists"]):
        key = "".join(map(str, a))
        d = t["sectors"][str(s)]
        assert Fraction(d["c"], d["n"]) == Fraction(ex["P_contractible"][key]), key
        for cls, cnt in ex["odd_lines"][key].items():
            assert d["lines"].get(cls, 0) == cnt, (key, cls)

    # own classification of the 3 x 2 x 2 slice
    n, edges = cubic((3, 2, 2))
    row = by["3x2x2 slice"]
    own = {}
    for m in range(row["amount"]):
        x = [(m >> e) & 1 for e in range(len(edges))]
        for s, q in enumerate(row["twists"]):
            cat, inv, odd = classify(n, edges, x, q)
            d = own.setdefault(str(s), {"n": 0, "c": 0, "x": 0, "inv": 0, "mis": 0, "lines": {}})
            d["n"] += 1
            d["inv"] += inv
            d["mis"] += (inv != odd) if any(q) else inv
            if isinstance(cat, tuple):
                key = ",".join(map(str, cat))
                d["lines"][key] = d["lines"].get(key, 0) + 1
            else:
                d[cat] += 1
    assert own == row["sectors"], "slice differs from the producer"

    # comparisons, symmetry controls and verdict, recomputed
    sym_fail, unrelated = [], []
    for label in ("3x2x2", "3x3x2", "4x3x2", "4x4x2", "3x3x3"):
        r = by[label]
        tw = [tuple(a) for a in r["twists"]]
        N = r["amount"]
        L = tuple(r["sizes"])
        perms = [p for p in permutations(range(3)) if all(L[p[i]] == L[i] for i in range(3))]
        counts, joint = {}, {}
        for s, d in r["sectors"].items():
            for c, v in d["lines"].items():
                counts[(tw[int(s)], tuple(map(int, c.split(","))))] = v
        for key, d in r["joint"].items():
            s1, s2 = map(int, key.split(","))
            for c, v in d.items():
                joint[(tw[s1], tw[s2], tuple(map(int, c.split(","))))] = v
        for c in sorted({c for (_a, c) in counts}):
            odd = [a for a in tw if sum(p * q for p, q in zip(a, c)) & 1]
            total = sum(counts.get((a, c), 0) for a in odd)
            if total < 1000:
                continue
            for i, a in enumerate(odd):
                for b in odd[i + 1:]:
                    na, nb = counts.get((a, c), 0), counts.get((b, c), 0)
                    nab = joint.get((a, b, c), 0)
                    pa, pb, pab = na / N, nb / N, nab / N
                    var = N * (pa + pb - 2 * pab - (pa - pb) ** 2)
                    z = (na - nb) / math.sqrt(var) if var > 0 else (0.0 if na == nb else math.inf)
                    sym = any(norm(tuple(c[p[k]] for k in range(3))) == c and tuple(a[p[k]] for k in range(3)) == b for p in perms)
                    if sym and abs(z) >= 4:
                        sym_fail.append((label, c, a, b, z))
                    if not sym and label != "3x3x3":
                        unrelated.append((label, c, a, b, z, math.sqrt(var) / max(1, (na + nb) / 2)))
        for p in perms:
            for (a, c), v in counts.items():
                pc, pa = norm(tuple(c[p[k]] for k in range(3))), tuple(a[p[k]] for k in range(3))
                if pc == c or (a, c) > (pa, pc):
                    continue
                w = counts.get((pa, pc), 0)
                if v + w >= 500 and abs(v - w) / math.sqrt(v + w) >= 4:
                    sym_fail.append((label, c, pc, a, pa))
    assert not sym_fail, sym_fail
    assert not fails and result["controls_ok"], fails
    a = result["analysis"]
    differ = [u for u in unrelated if abs(u[4]) > 5]
    equal = [u for u in unrelated if abs(u[4]) < 2 and u[5] < 0.02]
    assert len(unrelated) == a["unrelated_comparisons"] and len(differ) == a["unrelated_differ"] and len(equal) == len(a["unrelated_equal_resolved"])
    verdict = ("inconclusive" if not unrelated else "supported" if len(differ) == len(unrelated) else "refuted" if equal else "mixed")
    assert verdict == result["verdict"], (verdict, result["verdict"])
    smallest = min((abs(u[4]) for u in unrelated), default=None)
    print(f"checked: {len(rows)} rows, verdict {verdict}; {len(unrelated)} unrelated comparisons on thin tori, {len(differ)} differ at "
          f"|z| > 5 (smallest |z| {smallest:.1f}); symmetry controls hold; torus row matches the exact counts; own classification of the "
          f"3x2x2 slice matches")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
