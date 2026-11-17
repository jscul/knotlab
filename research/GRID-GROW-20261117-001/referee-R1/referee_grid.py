"""Referee R1 for GRID-GROW-20261117-001 (own code; nothing imported from the study).

  ../../../.venv/bin/python -B referee_grid.py > referee_grid.json      (from this directory)

1. G1: the box-betweenness base equals the cut system and d = 2 L1, brute force over all states, every Young diagram of at most
   16 cells in a 5 x 5 box (the study: 4 x 4).
2. G2, G3 one size past: every step (shape, outer corner) in the 4 x 4 and 5 x 5 boxes (6 x 6 with --six), the old base taken as its exact cut system:
   - new line: minimum knots; every single-knot cover, its cells and kind;
   - filled cell: minimum knots; EVERY minimum cover (not only the local ones), whether all its knots are betweenness knots; the
     covers using only cells within L1 distance 2 of p; the other cells of S within that distance;
   - the unit-square four-place parity.
3. G5: do the states name the placements?  Two shapes whose bases are the same up to renaming distinctions (their L1 metrics are
   isometric) are read the same by any rule that sees only the states.  For every pair of such shapes in the 4 x 4 and 5 x 5 boxes
   that are not mirror images, compare their placements (numbers of new-line and fill steps).
4. Growth from the three-cell L to 4 x 4 in the study's two orders with local minimum covers: totals and knots per distinction.
   Also: from the states of a straight run, the base-level fill at every interior distinction (three knots on it and its two
   neighbours) gives the cut system of a Young diagram, so the base admits fills the drawing forbids.
5. The four-place unit-square parity under the canonical knot test; states per distinction of the r x c cut system.
"""
from __future__ import annotations

import itertools
import json
import os
import subprocess
import sys
from collections import defaultdict

import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
PATS = list(itertools.product((0, 1), repeat=3))
KNOTS = [frozenset(ex) for k in range(1, 5) for ex in itertools.combinations(PATS, k)
         if all(sum(a != b for a, b in zip(x, y)) != 1 for x, y in itertools.combinations(ex, 2))]
assert len(KNOTS) == 34


def is_btw(ex):
    """Betweenness in some place order: one complementary pair, not the constant pair."""
    ex = sorted(ex)
    return len(ex) == 2 and tuple(1 - v for v in ex[0]) == ex[1] and len(set(ex[0])) == 2


def shapes(R, C):
    out = []
    for rows in itertools.product(range(R + 1), repeat=C):     # rows[y] = length of row y
        if rows[0] > 0 and all(rows[i] >= rows[i + 1] for i in range(C - 1)):
            out.append(frozenset((x, y) for y in range(C) for x in range(rows[y])))
    return out


def corners(S, R, C):
    return [(x, y) for x in range(R) for y in range(C) if (x, y) not in S
            and (x == 0 or (x - 1, y) in S) and (y == 0 or (x, y - 1) in S)]


def cuts(cells):
    n = len(cells)
    full = (1 << n) - 1
    out = {0, full}
    for k in sorted({c[0] for c in cells})[1:]:
        m = sum(1 << i for i, c in enumerate(cells) if c[0] >= k); out |= {m, full ^ m}
    for k in sorted({c[1] for c in cells})[1:]:
        m = sum(1 << i for i, c in enumerate(cells) if c[1] >= k); out |= {m, full ^ m}
    return out


def l1(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


# ---------- 1 ----------

def g1(cells):
    n = len(cells)
    inbox = lambda a, b, c: min(a[0], c[0]) <= b[0] <= max(a[0], c[0]) and min(a[1], c[1]) <= b[1] <= max(a[1], c[1])
    s = np.arange(1 << n, dtype=np.int64)
    bits = [(s >> i) & 1 for i in range(n)]
    ok = np.ones(len(s), bool)
    for i, k in itertools.combinations(range(n), 2):
        for j in range(n):
            if j not in (i, k) and inbox(cells[i], cells[j], cells[k]):
                ok &= ~((bits[i] == bits[k]) & (bits[i] != bits[j]))
    sts = set(map(int, s[ok]))
    cs = cuts(cells)
    d_ok = all(sum(((t >> i) ^ (t >> j)) & 1 for t in cs) == 2 * l1(cells[i], cells[j]) for i in range(n) for j in range(n))
    return sts == cs, d_ok


# ---------- 2 ----------

def step(S, p):
    old = sorted(S)
    cells = old + [p]
    P = len(old)
    olds = cuts(old)
    target = cuts(cells)
    ambient = {s | (v << P) for s in olds for v in (0, 1)}
    assert target <= ambient
    bad = sorted(ambient - target)
    bi = {s: i for i, s in enumerate(bad)}
    full = (1 << len(bad)) - 1
    cand = defaultdict(list)                       # mask of bad states killed -> list of (cells, excluded on those cells)
    for u, v in itertools.combinations(range(P), 2):
        trip = (u, v, P)
        proj = lambda s: tuple((s >> t) & 1 for t in trip)
        used = {proj(s) for s in target}
        for ex in KNOTS:
            if ex & used:
                continue
            m = sum(1 << bi[s] for s in bad if proj(s) in ex)
            if m:
                cand[m].append(((cells[u], cells[v], p), ex))
    masks = list(cand)
    kind = "fill" if p[0] > 0 and p[1] > 0 else "new line"
    out = {"p": p, "cells": len(cells), "kind": kind, "bad": len(bad)}
    if not bad:
        out["min"] = 0
        return out
    if full in cand:
        out["min"] = 1
        out["single_covers"] = [{"cells": c, "betweenness": is_btw(ex)} for c, ex in cand[full]]
        return out
    two = any((a | b) == full for a, b in itertools.combinations(masks, 2))
    out["two_suffice"] = two
    covers = []
    mset = set(masks)
    for a, b in itertools.combinations(masks, 2):
        need = full & ~(a | b)
        for c in masks:
            if (c | need) == c and c != a and c != b and (a | b | c) == full:
                covers.append(frozenset((a, b, c)))
    covers = set(covers)
    out["min"] = 2 if two else (3 if covers else ">3")
    # every knot appearing in any minimum (three-knot) cover
    knots_in_min = [(cl, ex) for cv in covers for m in cv for cl, ex in cand[m]]
    out["min_covers_by_mask"] = len(covers)
    out["all_min_cover_knots_betweenness"] = all(is_btw(ex) for _, ex in knots_in_min)
    out["non_betweenness_kinds_in_min_covers"] = sorted({str(sorted(ex)) for _, ex in knots_in_min if not is_btw(ex)})[:4]
    local = [(cv, [(cl, ex) for m in cv for cl, ex in cand[m] if all(l1(q, p) <= 2 for q in cl)]) for cv in covers]
    local_covers = set()
    for cv in covers:
        opts = [[(cl, ex) for cl, ex in cand[m] if all(l1(q, p) <= 2 for q in cl)] for m in cv]
        for combo in itertools.product(*opts):
            local_covers.add(frozenset((frozenset(cl), ex) for cl, ex in combo))
    out["local_covers"] = len(local_covers)
    out["local_cover_cells"] = sorted(sorted(map(list, cl)) for cl, _ in next(iter(local_covers))) if local_covers else None
    out["other_cells_within_2"] = sorted(q for q in old if l1(q, p) <= 2 and q not in
                                         ((p[0] - 1, p[1]), (p[0], p[1] - 1), (p[0] - 1, p[1] - 1)))
    sq = [old.index(q) for q in ((p[0] - 1, p[1] - 1), (p[0] - 1, p[1]), (p[0], p[1] - 1))] + [P]
    par = lambda s: sum((s >> t) & 1 for t in sq) % 2
    out["parity_covers"] = all(par(s) == 0 for s in target) and all(par(s) == 1 for s in bad)
    return out


def census(R, C):
    rows = []
    for S in shapes(R, C):
        for p in corners(S, R, C):
            rows.append(step(S, p))
    nl = [r for r in rows if r["kind"] == "new line" and r["min"] != 0]
    one = [r for r in rows if r["min"] == 0]
    fills = [r for r in rows if r["kind"] == "fill"]
    def nl_ok(r):
        S_cells = r["cells"]
        sc = r.get("single_covers", [])
        return r["min"] == 1 and len(sc) == 1 and sc[0]["betweenness"]
    summary = {
        "box": f"{R}x{C}", "shapes": len(shapes(R, C)), "steps": len(rows),
        "from_one_cell_cost_0": len(one),
        "new_line_steps": len(nl), "new_line_one_unique_betweenness_knot": sum(nl_ok(r) for r in nl),
        "fill_steps": len(fills), "fill_min_3_never_2": sum(r["min"] == 3 and not r["two_suffice"] for r in fills),
        "fill_all_min_cover_knots_betweenness": sum(r["all_min_cover_knots_betweenness"] for r in fills),
        "fill_exactly_one_local_cover": sum(r["local_covers"] == 1 for r in fills),
        "fill_local_cover_is_unit_square": sum(r["local_cover_cells"] is not None and
                                                all(sorted(map(tuple, k)) and set(map(tuple, k)) <=
                                                    {r["p"], (r["p"][0] - 1, r["p"][1]), (r["p"][0], r["p"][1] - 1),
                                                     (r["p"][0] - 1, r["p"][1] - 1)} for k in r["local_cover_cells"])
                                                for r in fills),
        "fills_with_other_cells_within_2": sum(bool(r["other_cells_within_2"]) for r in fills),
        "fill_parity_covers": sum(r["parity_covers"] for r in fills),
        "fill_min_covers_by_mask_range": [min(r["min_covers_by_mask"] for r in fills), max(r["min_covers_by_mask"] for r in fills)],
        "non_betweenness_kinds_seen": sorted({k for r in fills for k in r["non_betweenness_kinds_in_min_covers"]}),
    }
    ex = next((r for r in fills if r["other_cells_within_2"]), None)
    summary["example_fill_with_other_cells_within_2"] = {k: ex[k] for k in ("p", "other_cells_within_2", "local_covers")} if ex else None
    return summary


# ---------- 3: G5 ----------

def dmat(S):
    cells = sorted(S)
    return cells, [[l1(a, b) for b in cells] for a in cells]


def isometric(S1, S2):
    c1, D1 = dmat(S1)
    c2, D2 = dmat(S2)
    n = len(c1)
    if n != len(c2):
        return False
    sig = lambda D, i: tuple(sorted(D[i]))
    if sorted(sig(D1, i) for i in range(n)) != sorted(sig(D2, i) for i in range(n)):
        return False
    order = sorted(range(n), key=lambda i: -max(D1[i]))
    img = {}
    def bt(k):
        if k == n:
            return True
        i = order[k]
        for j in range(n):
            if j in img.values() or sig(D2, j) != sig(D1, i):
                continue
            if all(D1[i][i2] == D2[j][j2] for i2, j2 in img.items()):
                img[i] = j
                if bt(k + 1):
                    return True
                del img[i]
        return False
    return bt(0)


def placements(S, R, C):
    cs = corners(S, R + 1, C + 1)                      # placements ignoring the box's walls
    return {"new_line": sum(1 for p in cs if p[0] == 0 or p[1] == 0), "fill": sum(1 for p in cs if p[0] > 0 and p[1] > 0)}


def g5(R, C):
    shp = shapes(R, C)
    transpose = lambda S: frozenset((y, x) for x, y in S)
    groups = []
    for S in shp:
        for g in groups:
            if isometric(S, g[0]):
                g.append(S)
                break
        else:
            groups.append([S])
    ambiguous = []
    for g in groups:
        if len(g) < 2:
            continue
        pl = {}
        for S in g:
            key = (placements(S, R, C)["new_line"], placements(S, R, C)["fill"])
            pl.setdefault(key, []).append(sorted(S))
        if len(pl) > 1:
            ambiguous.append({"same_states_up_to_renaming": [v[0] for v in pl.values()],
                              "placements_new_line_fill": list(pl.keys())})
    return {"box": f"{R}x{C}", "shapes": len(shp), "classes_of_equal_states": len(groups),
            "classes_with_two_shapes_not_mirror_images": sum(1 for g in groups if len(g) > 1 and
                                                             not all(S == g[0] or S == transpose(g[0]) for S in g)),
            "classes_whose_placements_differ": len(ambiguous), "examples": ambiguous[:4]}


def line_vs_L():
    L = sorted({(0, 0), (1, 0), (0, 1)})
    row = sorted({(0, 0), (1, 0), (2, 0)})
    def canon(cells):
        st = cuts(cells)
        best = None
        for perm in itertools.permutations(range(3)):
            key = tuple(sorted(sum(((s >> i) & 1) << perm[i] for i in range(3)) for s in st))
            best = key if best is None or key < best else best
        return best
    return {"L_states": sorted(cuts(L)), "row_states": sorted(cuts(row)), "same_up_to_renaming": canon(L) == canon(row),
            "L_placements": corners(frozenset(L), 9, 9), "row_placements": corners(frozenset(row), 9, 9)}


def line_fills(nmax=7):
    """From the states of a line (a straight run (i, 0)), the base-level fill at each interior distinction c: add p with
    B(a, p, b), B(c, a, p), B(c, b, p) for c's two neighbours a, b.  Is the result, up to renaming, the cut system of some Young
    diagram (an isometric L1 metric, with 2 x cuts + 2 states)?"""
    out = {}
    for n in range(3, nmax + 1):
        cells = [(i, 0) for i in range(n)]
        old = sorted(cuts(cells))
        ok = []
        for k in range(1, n - 1):
            a, c, b, P = k - 1, k, k + 1, n
            sts = []
            for s in old:
                for v in (0, 1):
                    t = s | (v << P)
                    x = lambda i: (t >> i) & 1
                    if (x(a) == x(b) != x(P)) or (x(c) == x(P) != x(a)) or (x(c) == x(P) != x(b)):
                        continue
                    sts.append(t)
            m = n + 1
            D = [[sum(((t >> i) ^ (t >> j)) & 1 for t in sts) // 2 for j in range(m)] for i in range(m)]
            match = None
            for S in shapes(m, m):
                if len(S) != m:
                    continue
                cS, DS = dmat(S)
                if len(cuts(cS)) != len(sts):
                    continue
                # isometry between D and DS by backtracking
                img = {}
                def bt(i):
                    if i == m:
                        return True
                    for j in range(m):
                        if j in img.values():
                            continue
                        if all(D[i][i2] == DS[j][j2] for i2, j2 in img.items()):
                            img[i] = j
                            if bt(i + 1):
                                return True
                            del img[i]
                    return False
                if bt(0):
                    match = sorted(S)
                    break
            ok.append({"c": k, "states": len(sts), "young_diagram_up_to_renaming": match})
        out[n] = ok
    return out


# ---------- 4, 5 ----------

def grow(order):
    S = {(0, 0), (1, 0), (0, 1)}
    knots = [((1, 0), (0, 0), (0, 1))]
    added = []
    for p in order:
        r = step(frozenset(S), p)
        if r["min"] == 1:
            cl = r["single_covers"][0]["cells"]
            knots.append(cl); added.append(1)
        else:
            sq = [p, (p[0] - 1, p[1]), (p[0], p[1] - 1), (p[0] - 1, p[1] - 1)]
            knots += [((p[0] - 1, p[1]), p, (p[0], p[1] - 1)), (sq[3], sq[1], p), (sq[3], sq[2], p)]; added.append(3)
        S.add(p)
    deg = defaultdict(int)
    for k in knots:
        for c in k:
            deg[c] += 1
    return {"total": len(knots), "per_step": added, "max_per_distinction": max(deg.values()),
            "busiest": sorted(((list(c), d) for c, d in deg.items()), key=lambda t: -t[1])[:4]}


def parity_knot():
    env = dict(os.environ, PYTHONPATH=os.path.join(ROOT, "tools"))
    cnf = "; ".join(" ".join(("~" if (m >> i) & 1 else "") + v for i, v in enumerate("abcd"))
                    for m in range(16) if bin(m).count("1") % 2 == 1)     # exclude odd-weight states: a+b+c+d even
    r = subprocess.run([sys.executable, "-B", "-m", "knotlab", "check", "--cnf", cnf, "--loops", "a", "b", "c",
                        "--contact", "d", "--json"], capture_output=True, text=True, env=env, cwd=ROOT, timeout=120)
    j = json.loads(r.stdout)
    return {"cnf": cnf, "is_knot": j.get("is_knot"), "allowed_count": len(j.get("allowed", []))}


def main():
    out = {"1_G1": {}}
    for S in shapes(5, 5):
        if len(S) <= 16:
            ok, d = g1(sorted(S))
            out["1_G1"].setdefault("tested", 0)
            out["1_G1"]["tested"] += 1
            out["1_G1"].setdefault("failures", 0)
            out["1_G1"]["failures"] += (not ok) or (not d)
    out["2_census"] = [census(4, 4), census(5, 5)] + ([census(6, 6)] if "--six" in sys.argv else [])
    out["3_G5_line_vs_L"] = line_vs_L()
    out["3_G5_classes"] = [g5(4, 4), g5(5, 5)]
    out["3_G5_base_level_fills_of_a_line"] = line_fills()
    arms = [(2, 0), (3, 0), (0, 2), (0, 3), (1, 1), (2, 1), (1, 2), (3, 1), (2, 2), (1, 3), (3, 2), (2, 3), (3, 3)]
    raster = [(2, 0), (3, 0), (1, 1), (2, 1), (3, 1), (0, 2), (1, 2), (2, 2), (3, 2), (0, 3), (1, 3), (2, 3), (3, 3)]
    out["4_growth"] = {"arms then fill": grow(arms), "raster": grow(raster)}
    out["5_parity_knot"] = parity_knot()
    out["5_states_per_distinction"] = {f"{r}x{c}": (2 * (r + c) - 2) ** (1 / (r * c)) for r, c in ((4, 4), (8, 8), (16, 16))}
    print(json.dumps(out, indent=1, default=str))


if __name__ == "__main__":
    main()
