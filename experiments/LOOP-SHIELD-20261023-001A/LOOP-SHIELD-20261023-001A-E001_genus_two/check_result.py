#!/usr/bin/env python3
"""Independent check of the genus-2 line counts; imports no producer code.

Parses raw_rows.jsonl, the frozen contract and result.json, and:
- checks the roster, the totals, the swap-invariance test, and that the halved enumeration of L(2,2,2,2) equals the full one;
- matches the 3 x 3 torus row to the exact counts of TWIST-RELATIONS-20261022-001A-P001;
- builds L(2,1,2,1) by its own construction (lattice points of the L-shaped region glued along its sides) and enumerates all 2^16
  orientations in all 16 twists with its own classification, comparing every tally;
- checks the diagonal reflection of L(2,2,2,2): it exchanges the h and v core curves, so every count of twist (a1,a2,a3,a4) and
  class (d1,d2,d3,d4) must equal the count of twist (a3,a4,a1,a2) and class (d3,d4,d1,d2);
- recomputes the dual pairs (P1), the specificity test (P2) and the verdict;
- replays L(3,1,2,2) on 20,000 random orientations with its own classification and compares category frequencies with the exact counts.

    python3 -B check_result.py
"""

from __future__ import annotations

import json
import math
import random
from fractions import Fraction
from math import gcd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
ART = ROOT / "artifacts/LOOP-SHIELD-20261023-001A" / HERE.name
EXACT = ROOT / "proofs/TWIST-RELATIONS-20261022-001A/TWIST-RELATIONS-20261022-001A-P001_harmonic_structure/result.json"
LABELS = ["torus 3x3 s=0", "L(2,1,2,1)", "L(2,2,2,2) full", "L(2,2,2,2)", "L(2,1,2,3)", "L(2,1,3,2)", "L(3,1,2,2)", "L(2,2,3,1)",
          "L(2,3,2,2)", "L(3,2,2,2)", "L(2,2,2,4)"]
JMAT = ((0, 0, 1, 1), (0, 0, 1, 0), (-1, -1, 0, 0), (-1, 0, 0, 0))
TWISTS = [tuple((i >> (3 - k)) & 1 for k in range(4)) for i in range(16)]


# ------------------------------------------------------------------ own surface construction

def surface(A, B, C, D):
    """Lattice points of the L-region glued along its sides; edges are the bottom and left sides of each cell."""
    W, H = A + B, C + D
    inside = lambda x, y: (0 <= x <= W and 0 <= y <= C) or (0 <= x <= A and C <= y <= H)
    pts = [(x, y) for x in range(W + 1) for y in range(H + 1) if inside(x, y)]
    parent = {p: p for p in pts}

    def root(p):
        while parent[p] != p:
            parent[p] = parent[parent[p]]
            p = parent[p]
        return p

    def glue(p, q):
        a, b = root(p), root(q)
        if a != b:
            parent[a] = b

    for (x, y) in pts:
        if x == W and y <= C:
            glue((x, y), (0, y))            # right side of the bottom block
        if x == A and C <= y <= H:
            glue((x, y), (0, y))            # right side of the top block
        if y == H and x <= A:
            glue((x, y), (x, 0))            # top of the left columns
        if y == C and A <= x <= W:
            glue((x, y), (x, 0))            # top of the right columns
    names = {}
    for p in pts:
        names.setdefault(root(p), len(names))
    vid = lambda p: names[root(p)]
    cells = [(x, y) for y in range(C) for x in range(W)] + [(x, y) for y in range(C, H) for x in range(A)]
    edges = []
    for (x, y) in cells:
        edges.append((vid((x, y)), vid((x + 1, y)), (0, 0, -int(x == 0), -int(x == A))))      # bottom side, crossed by v1, v2
        edges.append((vid((x, y)), vid((x, y + 1)), (int(y == 0), int(y == H - 1), 0, 0)))    # left side, crossed by h1, h2
    return len(names), edges


# ------------------------------------------------------------------ own classification

def classify(V, edges, x, alpha):
    """('c',), ('x',) or ('w', direction), and whether a strong component is swap-invariant."""
    K = len(alpha)
    t = [sum(a * o for a, o in zip(alpha, off)) & 1 for (_u, _w, off) in edges]
    n = 2 * V
    out = [[] for _ in range(n)]
    for (u, w, _o), bit, te in zip(edges, x, t):
        pairs = [(2 * u, 2 * w + te), (2 * w + 1 - te, 2 * u + 1)] if bit else [(2 * w + te, 2 * u), (2 * u + 1, 2 * w + 1 - te)]
        for i, j in pairs:
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
        stack = [(r, iter(out[r]))]
        while stack:
            v, it = stack[-1]
            w = next(it, None)
            if w is None:
                order.append(v)
                stack.pop()
            elif not seen[w]:
                seen[w] = True
                stack.append((w, iter(out[w])))
    comp = [-1] * n
    for r in reversed(order):
        if comp[r] >= 0:
            continue
        comp[r] = r
        stack = [r]
        while stack:
            v = stack.pop()
            for w in rev[v]:
                if comp[w] < 0:
                    comp[w] = r
                    stack.append(w)
    inv = any(comp[2 * v] == comp[2 * v + 1] for v in range(V))
    parent, pos = list(range(V)), [(0,) * K for _ in range(V)]

    def find(v):
        acc = (0,) * K
        while parent[v] != v:
            acc = tuple(a + b for a, b in zip(acc, pos[v]))
            v = parent[v]
        return v, acc

    gens = []
    for (u, w, off), te in zip(edges, t):
        if comp[2 * u] != comp[2 * w + te]:
            continue
        (ru, pu), (rw, pw) = find(u), find(w)
        d = tuple(a + b - c for a, b, c in zip(pu, off, pw))
        if ru == rw:
            if any(d):
                gens.append(d)
        else:
            parent[rw], pos[rw] = ru, d
    odd = any(sum(a * b for a, b in zip(alpha, g)) & 1 for g in gens)
    if not gens:
        return ("c",), inv, odd
    g0 = gens[0]
    if any(g0[i] * g[j] - g0[j] * g[i] for g in gens for i in range(K) for j in range(i + 1, K)):
        return ("x",), inv, odd
    k = 0
    for v in g0:
        k = gcd(k, abs(v))
    d = tuple(v // k for v in g0)
    if next(v for v in d if v) < 0:
        d = tuple(-v for v in d)
    return ("w", d), inv, odd


def tally(V, edges, xs, twists):
    res = {a: {"n": 0, "c": 0, "x": 0, "inv": 0, "mis": 0, "lines": {}} for a in twists}
    for x in xs:
        for a in twists:
            cat, inv, odd = classify(V, edges, x, a)
            r = res[a]
            r["n"] += 1
            r["inv"] += inv
            r["mis"] += (inv != odd) if any(a) else inv
            if cat[0] == "w":
                key = ",".join(map(str, cat[1]))
                r["lines"][key] = r["lines"].get(key, 0) + 1
            else:
                r[cat[0]] += 1
    return res


def solve(v):
    M = [list(map(Fraction, JMAT[i])) + [Fraction(v[i])] for i in range(4)]
    for c in range(4):
        p = next(r for r in range(c, 4) if M[r][c] != 0)
        M[c], M[p] = M[p], M[c]
        for r in range(4):
            if r != c and M[r][c] != 0:
                f = M[r][c] / M[c][c]
                M[r] = [a - f * b for a, b in zip(M[r], M[c])]
    return tuple(int(M[i][4] / M[i][i]) for i in range(4))


def norm(d):
    return d if next(v for v in d if v) > 0 else tuple(-v for v in d)


def main() -> int:
    contract = json.loads((HERE / "contract.json").read_text())
    result = json.loads((ART / "result.json").read_text())
    rows = [json.loads(line) for line in (ART / "raw_rows.jsonl").read_text().splitlines()]
    assert contract["status"] == "Frozen" and result["experiment_id"] == contract["experiment_id"] and len(rows) == result["rows"]
    assert [r["label"] for r in rows] == LABELS
    by = {r["label"]: r for r in rows}

    # controls
    fails = []
    for r in rows:
        for s, d in r["sectors"].items():
            if d["c"] + d["x"] + sum(d["lines"].values()) != d["n"] or d["n"] != 1 << r["edges"]:
                fails.append(f"totals {r['label']} {s}")
            if d["mis"] or (not any(r["twists"][int(s)]) and d["inv"]):
                fails.append(f"swap-invariance {r['label']} {s}")
    if by["L(2,2,2,2) full"]["sectors"] != by["L(2,2,2,2)"]["sectors"]:
        fails.append("halving")
    assert not fails and result["controls_ok"] and not result["control_failures"], fails

    # the torus row against TWIST-RELATIONS-20261022-001A-P001
    ex = json.loads(EXACT.read_text())["checks"]["exhaustive"]["3x3 s=0"]
    t = by["torus 3x3 s=0"]
    for s, a in enumerate(t["twists"]):
        key = "".join(map(str, a))
        d = t["sectors"][str(s)]
        assert Fraction(d["c"], d["n"]) == Fraction(ex["P_contractible"][key]), key
        for cls, cnt in ex["odd_lines"][key].items():
            assert d["lines"].get(cls, 0) == cnt, (key, cls)

    # own enumeration of L(2,1,2,1)
    V, edges = surface(2, 1, 2, 1)
    assert V - len(edges) + 8 == -2
    xs = ([(m >> e) & 1 for e in range(len(edges))] for m in range(1 << len(edges)))
    own = tally(V, edges, xs, TWISTS)
    row = by["L(2,1,2,1)"]
    for s, a in enumerate(row["twists"]):
        assert {k: v for k, v in row["sectors"][str(s)].items()} == own[tuple(a)], (a, row["sectors"][str(s)], own[tuple(a)])

    # diagonal reflection of L(2,2,2,2)
    for label in ("L(2,2,2,2)", "L(2,2,2,2) full"):
        r = by[label]
        tab = {tuple(a): r["sectors"][str(s)] for s, a in enumerate(r["twists"])}
        for a, d in tab.items():
            b = (a[2], a[3], a[0], a[1])
            e = tab[b]
            assert (d["c"], d["x"], d["inv"]) == (e["c"], e["x"], e["inv"]), (label, a)
            for cls, cnt in d["lines"].items():
                v = tuple(map(int, cls.split(",")))
                w = norm((v[2], v[3], v[0], v[1]))
                assert e["lines"].get(",".join(map(str, w)), 0) == cnt, (label, a, cls)

    # P1, P2 and the verdict, recomputed
    tested, p1, p2_fail = 0, True, []
    for r in rows:
        if not r["label"].startswith("L("):
            continue
        counts = {}
        for s, d in r["sectors"].items():
            for cls, cnt in d["lines"].items():
                counts[(tuple(r["twists"][int(s)]), tuple(map(int, cls.split(","))))] = cnt
        for c in sorted({c for (_a, c) in counts}):
            x = solve(c)
            odd = [a for a in TWISTS if sum(p * q for p, q in zip(a, c)) & 1]
            vals = {a: counts.get((a, c), 0) for a in odd}
            if not any(vals.values()):
                continue
            tested += 1
            for a in odd:
                b = tuple((p + q) & 1 for p, q in zip(a, x))
                if vals[a] != vals[b]:
                    p1 = False
            if len(set(vals.values())) == 1:
                p2_fail.append((r["label"], x))
    a = result["analysis"]
    assert tested == a["classes_with_odd_lines"] and p1 == a["P1_dual_pairs_equal"] and (not p2_fail) == a["P2_not_all_equal"]
    verdict = "refuted" if not p1 else ("supported" if not p2_fail else "partially supported")
    assert verdict == result["verdict"], (verdict, result["verdict"])

    # replay of L(3,1,2,2)
    V, edges = surface(3, 1, 2, 2)
    rng = random.Random("loop-shield-genus-two")
    m = 20000
    sample = tally(V, edges, ([rng.getrandbits(1) for _ in edges] for _ in range(m)), TWISTS)
    r = by["L(3,1,2,2)"]
    worst = 0.0
    for s, a in enumerate(r["twists"]):
        d, o = r["sectors"][str(s)], sample[tuple(a)]
        cats = [("c", d["c"], o["c"]), ("x", d["x"], o["x"])] + [(k, v, o["lines"].get(k, 0)) for k, v in d["lines"].items()]
        assert all(k in d["lines"] for k in o["lines"]), (a, o["lines"])
        for _k, exact, obs in cats:
            p = exact / d["n"]
            if 0 < p < 1:
                worst = max(worst, abs(obs / m - p) / math.sqrt(p * (1 - p) / m))
    assert worst <= 5, worst
    print(f"checked: {len(rows)} rows, verdict {verdict}; {tested} classes with lone odd lines, dual pairs equal: {p1}, classes with all "
          f"twists equal: {p2_fail}; torus row matches the exact counts; own enumeration of L(2,1,2,1) matches; diagonal reflection of "
          f"L(2,2,2,2) exact; replay of L(3,1,2,2) ({m} orientations) worst {worst:.2f} sigma")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
