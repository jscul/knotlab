#!/usr/bin/env python3
"""Independent check of the exact 4 x 4 counts; imports no producer code.

Parses raw_rows.jsonl, the frozen contract and result.json, and:
- checks the roster, the totals, the exact duality (contractible = cross in every twisted sector) and the test agreement;
- matches the 3 x 3 rows to the exact counts of TWIST-RELATIONS-20261022-001A-P001;
- checks exact symmetries the counts must have: the 90-degree rotation exchanges 4 x 3 and 3 x 4 (sector (a, b) <-> (b, a), class
  (x, y) <-> (-y, x)) and maps the square 4 x 4 onto itself; the relabelled mirror maps shear s to Lh - s;
- recomputes every comparison of the identity and the verdict;
- replays the sheared 4 x 4 torus (shear 1) on 300,000 random orientations with its own Python classification and compares
  frequencies with the exact counts.

    python3 -B check_result.py
"""

from __future__ import annotations

import json
import math
import random
import sys
from fractions import Fraction
from math import gcd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
ART = ROOT / "artifacts/ODD-LOOP-20261023-001A" / HERE.name
EXACT = ROOT / "proofs/TWIST-RELATIONS-20261022-001A/TWIST-RELATIONS-20261022-001A-P001_harmonic_structure/result.json"
ROSTER = [("F_check", 3, 3, 0), ("F_check", 3, 3, 1), ("F_small", 4, 3, 0), ("F_small", 4, 3, 1), ("F_small", 4, 3, 2),
          ("F_small", 3, 4, 0), ("F_small", 3, 4, 1), ("F_five", 5, 3, 0), ("F_five", 5, 3, 1), ("F_five", 5, 3, 2),
          ("F_four", 4, 4, 0), ("F_four", 4, 4, 1), ("F_four", 4, 4, 2)]
SECTORS = ((0, 0), (1, 0), (0, 1), (1, 1))
REPLAY = (4, 4, 1)


def norm(c):
    a, b = c
    return (a, b) if a > 0 or (a == 0 and b > 0) else (-a, -b)


def lines(row, q):
    return {tuple(map(int, k.split(","))): v for k, v in row[f"lines{q}"].items()}


# ------------------------------------------------------------------ independent classification (replay)

def lattice(Lh, Lv, s):
    edges = []
    for u in range(Lh * Lv):
        x, y = u % Lh, u // Lh
        edges.append((u, y * Lh + (x + 1) % Lh, ((x + 1) // Lh, 0)))
        if y + 1 < Lv:
            edges.append((u, u + Lh, (0, 0)))
        else:
            X = x - s
            a = X // Lh
            edges.append((u, X - a * Lh, (a, 1)))
    return edges


def sector(V, edges, o, p):
    """(kind, class): kind 0 contractible, 1 cross, 2 winding, by Kosaraju on the (double cover) digraph and a lattice union-find"""
    pa, pb = p
    tw = bool(pa or pb)
    n = 2 * V if tw else V
    out = [[] for _ in range(n)]
    ts = []
    for (u, w, (a, b)), bit in zip(edges, o):
        t = (a * pa + b * pb) & 1
        ts.append(t)
        arcs = ([(u, w)] if bit else [(w, u)]) if not tw else \
            ([(2 * u, 2 * w + t), (2 * w + 1 - t, 2 * u + 1)] if bit else [(2 * w + t, 2 * u), (2 * u + 1, 2 * w + 1 - t)])
        for i, j in arcs:
            out[i].append(j)
    rev = [[] for _ in range(n)]
    for i in range(n):
        for j in out[i]:
            rev[j].append(i)
    seen, order = [False] * n, []
    for r in range(n):
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
    comp = [-1] * n
    for r in reversed(order):
        if comp[r] >= 0:
            continue
        comp[r], stack = r, [r]
        while stack:
            v = stack.pop()
            for w in rev[v]:
                if comp[w] < 0:
                    comp[w] = r
                    stack.append(w)
    parent, pos, gens = list(range(V)), [(0, 0)] * V, {}

    def find(x):
        dx = dy = 0
        while parent[x] != x:
            dx, dy = dx + pos[x][0], dy + pos[x][1]
            x = parent[x]
        return x, (dx, dy)

    for (u, w, (a, b)), t in zip(edges, ts):
        i, j = (2 * u, 2 * w + t) if tw else (u, w)
        if comp[i] != comp[j]:
            continue
        (ru, pu), (rw, pw) = find(u), find(w)
        d = (pu[0] + a - pw[0], pu[1] + b - pw[1])
        if ru == rw:
            if d != (0, 0):
                gens.setdefault(ru, []).append(d)
        else:
            parent[rw], pos[rw] = ru, d
            gens.setdefault(ru, []).extend(gens.pop(rw, []))
    kind, cls = 0, None
    for g in gens.values():
        if any(g[i][0] * g[j][1] - g[i][1] * g[j][0] for i in range(len(g)) for j in range(i + 1, len(g))):
            return 1, None
        if g:
            x, y = g[0]
            k = gcd(abs(x), abs(y))
            kind, cls = 2, norm((x // k, y // k))
    return kind, cls


def main() -> int:
    contract = json.loads((HERE / "contract.json").read_text())
    result = json.loads((ART / "result.json").read_text())
    rows = [json.loads(l) for l in (ART / "raw_rows.jsonl").read_text().splitlines()]
    assert contract["status"] == "Frozen" and result["experiment_id"] == contract["experiment_id"] and len(rows) == result["rows"]
    assert [(r["family"], r["Lh"], r["Lv"], r["s"]) for r in rows] == ROSTER
    by = {(r["Lh"], r["Lv"], r["s"]): r for r in rows}

    # controls
    fails = []
    for r in rows:
        n = r["orientations"]
        assert n == 1 << (2 * r["Lh"] * r["Lv"])
        for q in range(4):
            if r[f"contractible{q}"] + r[f"cross{q}"] + sum(r[f"lines{q}"].values()) != n:
                fails.append(f"totals {r['label']} {q}")
        for q in (1, 2, 3):
            if r[f"mis{q}"] or r[f"contractible{q}"] != r[f"cross{q}"]:
                fails.append(f"duality or test {r['label']} {q}")
        if r["mis0"] or r["inv0"]:
            fails.append(f"untwisted {r['label']}")
    assert fails == result["control_failures"] and result["controls_ok"] == (not fails)
    assert not fails, fails

    # 3 x 3 against the exact counts of the earlier proof
    ex = json.loads(EXACT.read_text())["checks"]["exhaustive"]
    for s in (0, 1):
        e, r = ex[f"3x3 s={s}"], by[(3, 3, s)]
        for q, key in enumerate(("00", "10", "01", "11")):
            assert Fraction(r[f"contractible{q}"], r["orientations"]) == Fraction(e["P_contractible"][key]), (s, q)
            for cls, cnt in e["odd_lines"][key].items():
                assert r[f"lines{q}"].get(cls, 0) == cnt, (s, q, cls)

    # exact symmetries: rotation by 90 degrees (4 x 3 <-> 3 x 4; 4 x 4 onto itself), relabelled mirror (shear s <-> Lh - s)
    def rotated_equal(r1, r2):
        for q, (a, b) in enumerate(SECTORS):
            q2 = SECTORS.index((b, a))
            if r1[f"contractible{q}"] != r2[f"contractible{q2}"]:
                return False
            l1, l2 = lines(r1, q), lines(r2, q2)
            if {norm((-y, x)): v for (x, y), v in l1.items()} != l2:
                return False
        return True

    assert rotated_equal(by[(4, 3, 0)], by[(3, 4, 0)]) and rotated_equal(by[(4, 4, 0)], by[(4, 4, 0)])

    def mirror_self(r):
        """Unsheared: the mirror x -> -x keeps every sector and maps classes (x, y) -> (-x, y)."""
        return all({norm((-x, y)): v for (x, y), v in lines(r, q).items()} == lines(r, q) for q in range(4))

    def half_shear_self(r):
        """Half shear: mirror then relabel maps the torus onto itself, sector (a, b) -> (a, a + b), class (x, y) -> (-x - y, y)."""
        for q, (a, b) in enumerate(SECTORS):
            q2 = SECTORS.index((a, (a + b) & 1))
            if r[f"contractible{q}"] != r[f"contractible{q2}"]:
                return False
            if {norm((-x - y, y)): v for (x, y), v in lines(r, q).items()} != lines(r, q2):
                return False
        return True

    for key in ((3, 3, 0), (4, 3, 0), (3, 4, 0), (5, 3, 0), (4, 4, 0)):
        assert mirror_self(by[key]), key
    for key in ((4, 3, 2), (4, 4, 2)):
        assert half_shear_self(by[key]), key

    # the identity, recomputed
    comps, diffs = 0, []
    for r in rows:
        ls = {q: lines(r, q) for q in range(4)}
        for cls in sorted(set().union(*(ls[q].keys() for q in (1, 2, 3)))):
            qs = [q for q in (1, 2, 3) if (cls[0] * SECTORS[q][0] + cls[1] * SECTORS[q][1]) & 1]
            a, b = ls[qs[0]].get(cls, 0), ls[qs[1]].get(cls, 0)
            comps += 1
            if a != b:
                diffs.append((r["label"], cls, a, b))
    assert comps == result["identity"]["comparisons"] and len(diffs) == result["identity"]["differences"]
    verdict = "supported" if not diffs else "refuted"
    assert verdict == result["verdict"]

    # replay: sheared 4 x 4 on random orientations
    m = int(sys.argv[1]) if len(sys.argv) > 1 else 300000
    edges = lattice(*REPLAY)
    r = by[REPLAY]
    rng = random.Random("odd-loop-replay")
    counts = {}
    for _ in range(m):
        o = [rng.getrandbits(1) for _ in edges]
        for q, p in enumerate(SECTORS):
            key = (q,) + sector(REPLAY[0] * REPLAY[1], edges, o, p)
            counts[key] = counts.get(key, 0) + 1
    N, worst = r["orientations"], 0.0
    for q in range(4):
        exact = {(q, 0, None): r[f"contractible{q}"], (q, 1, None): r[f"cross{q}"]}
        exact.update({(q, 2, c): v for c, v in lines(r, q).items()})
        for key, v in exact.items():
            p = v / N
            if p > 0:
                worst = max(worst, abs(counts.get(key, 0) / m - p) / math.sqrt(p * (1 - p) / m))
        assert all(k in exact for k in counts if k[0] == q), [k for k in counts if k[0] == q and k not in exact]
    assert worst <= 5, worst
    print(f"checked: {len(rows)} tori, verdict {verdict}; {comps} comparisons, {len(diffs)} differences {diffs[:5]}; 3x3 rows match the "
          f"exact counts; rotation and mirror symmetries exact; replay of 4x4 shear 1 ({m} orientations) worst {worst:.2f} sigma")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
