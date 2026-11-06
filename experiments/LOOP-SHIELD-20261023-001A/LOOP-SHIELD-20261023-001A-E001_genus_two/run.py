#!/usr/bin/env python3
"""Producer for LOOP-SHIELD-20261023-001A-E001: exact line counts on genus-2 square-tiled surfaces in all 16 twists.

Each surface is an L-shaped table: a bottom block of (A + B) x C unit cells and a top block of A x D cells over columns 0..A-1, with
opposite sides glued by translation. Its lattice graph has a vertex at every corner class, a bottom and a left edge per cell, and one
cone vertex of degree 12 (genus 2). Edges carry homology coordinates: their signed crossings with four core curves, h1 (row 0),
h2 (the top row of the top block), v1 (column 0) and v2 (column A), so a closed walk's coordinates are (h1.g, h2.g, v1.g, v2.g).
The twist alpha in {0,1}^4 is the class a = alpha_1 h1 + alpha_2 h2 + alpha_3 v1 + alpha_4 v2 mod 2; its value on an edge is
alpha.o_e mod 2, so it evaluates to a.g on a closed walk g (the twist dual to a).

Counting is done by lineev.c (compiled here with gcc -O2) on worker threads. Every orientation and its reversal have the
same classification (a global sheet swap), so all surfaces but the checks are enumerated over masks whose top bit is 0 and doubled;
the 24-edge symmetric surface is also enumerated in full as a control.

    python3 -B run.py    writes raw_rows.jsonl (surface by surface) and result.json under artifacts/
"""

from __future__ import annotations

import json
import os
import resource
import shutil
import subprocess
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor
from fractions import Fraction
from itertools import product
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUT = ROOT / "artifacts" / "LOOP-SHIELD-20261023-001A" / HERE.name
WORKERS = min(24, os.cpu_count() or 1)
J = [[0, 0, 1, 1], [0, 0, 1, 0], [-1, -1, 0, 0], [-1, 0, 0, 0]]     # J[j][k] = b_j . b_k for (h1, h2, v1, v2)
ROSTER = [  # (family, label, kind, parameters, half)
    ("F_check", "torus 3x3 s=0", "torus", (3, 3, 0), False),
    ("F_check", "L(2,1,2,1)", "lsurf", (2, 1, 2, 1), False),
    ("F_check", "L(2,2,2,2) full", "lsurf", (2, 2, 2, 2), False),
    ("F_small", "L(2,2,2,2)", "lsurf", (2, 2, 2, 2), True),
    ("F_small", "L(2,1,2,3)", "lsurf", (2, 1, 2, 3), True),
    ("F_mid", "L(2,1,3,2)", "lsurf", (2, 1, 3, 2), True),
    ("F_mid", "L(3,1,2,2)", "lsurf", (3, 1, 2, 2), True),
    ("F_mid", "L(2,2,3,1)", "lsurf", (2, 2, 3, 1), True),
    ("F_mid", "L(2,3,2,2)", "lsurf", (2, 3, 2, 2), True),
    ("F_large", "L(3,2,2,2)", "lsurf", (3, 2, 2, 2), True),
    ("F_large", "L(2,2,2,4)", "lsurf", (2, 2, 2, 4), True),
]


def l_surface(A, B, C, D):
    """Vertices, edges (tail, head, coordinates) and cell count of the L-shaped table; checks genus 2 and closedness."""
    cells = [(x, y) for y in range(C) for x in range(A + B)] + [(x, y) for y in range(C, C + D) for x in range(A)]
    pos = {c: i for i, c in enumerate(cells)}
    N = len(cells)
    right = [pos[((x + 1) % (A + B if y < C else A), y)] for (x, y) in cells]
    up = [pos[(x, (y + 1) % (C + D if x < A else C))] for (x, y) in cells]
    parent = list(range(4 * N))                      # corner k of cell s: 0 bottom-left, 1 bottom-right, 2 top-left, 3 top-right

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    for s in range(N):
        for a, b in ((4 * s + 1, 4 * right[s]), (4 * s + 2, 4 * up[s]), (4 * s + 3, 4 * right[s] + 2), (4 * s + 3, 4 * up[s] + 1)):
            ra, rb = find(a), find(b)
            if ra != rb:
                parent[rb] = ra
    roots = sorted({find(i) for i in range(4 * N)})
    vid = {r: i for i, r in enumerate(roots)}
    corner = lambda s, k: vid[find(4 * s + k)]
    edges = []
    for s, (x, y) in enumerate(cells):
        bottom = [0, 0, -1 if x == 0 else 0, -1 if x == A else 0]
        left = [1 if y == 0 else 0, 1 if y == C + D - 1 else 0, 0, 0]
        edges.append((corner(s, 0), corner(s, 1), tuple(bottom)))
        edges.append((corner(s, 0), corner(s, 2), tuple(left)))
    V = len(roots)
    assert V - len(edges) + N == -2, "not genus 2"
    for s in range(N):                               # each cell boundary is closed in homology
        b, l, r, t = edges[2 * s][2], edges[2 * s + 1][2], edges[2 * right[s] + 1][2], edges[2 * up[s]][2]
        assert all(b[i] + r[i] - t[i] - l[i] == 0 for i in range(4))
    # the core loops have coordinates equal to the columns of J
    row0 = [edges[2 * pos[(x, 0)]][2] for x in range(A + B)]
    rowtop = [edges[2 * pos[(x, C + D - 1)]][2] for x in range(A)]
    col0 = [edges[2 * pos[(0, y)] + 1][2] for y in range(C + D)]
    colA = [edges[2 * pos[(A, y)] + 1][2] for y in range(C)]
    for loop, k in ((row0, 0), (rowtop, 1), (col0, 2), (colA, 3)):
        assert [sum(v[i] for v in loop) for i in range(4)] == [J[i][k] for i in range(4)]
    return V, edges, N


def torus(Lh, Lv, s):
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
    return Lh * Lv, edges, None


def spec(kind, params):
    V, edges, N = (l_surface if kind == "lsurf" else torus)(*params)
    K = len(edges[0][2])
    twists = list(product((0, 1), repeat=K))
    text = "\n".join([f"{V} {len(edges)} {K}"] + [f"{u} {w} " + " ".join(map(str, o)) for u, w, o in edges]
                     + [str(len(twists))] + [" ".join(map(str, a)) for a in twists]) + "\n"
    return text, twists, V, len(edges), N


def parse(out):
    sectors, joint = {}, {}
    for line in out.splitlines():
        p = line.split()
        if p[0] == "sector":
            d = {"lines": {}}
            for item in p[2:]:
                k, v = item.rsplit("=", 1)
                if k.startswith("w:"):
                    d["lines"][k[2:]] = int(v)
                else:
                    d[k] = int(v)
            sectors[int(p[1])] = d
        else:
            joint[(int(p[1]), int(p[2]))] = {k[2:]: int(v) for k, v in (item.rsplit("=", 1) for item in p[3:])}
    return sectors, joint


def merge(acc, part, factor=1):
    sectors, joint = part
    for s, d in sectors.items():
        a = acc[0].setdefault(s, {"lines": {}})
        for k, v in d.items():
            if k == "lines":
                for c, n in v.items():
                    a["lines"][c] = a["lines"].get(c, 0) + factor * n
            else:
                a[k] = a.get(k, 0) + factor * v
    for key, d in joint.items():
        a = acc[1].setdefault(key, {})
        for c, n in d.items():
            a[c] = a.get(c, 0) + factor * n


def enumerate_surface(binary, text, E, half):
    total = 1 << (E - 1 if half else E)
    pieces = WORKERS * 8
    step = -(-total // pieces)
    ranges = [(i * step, min(total, (i + 1) * step)) for i in range(pieces) if i * step < total]

    def one(r):
        return parse(subprocess.run([binary, "exh", str(r[0]), str(r[1])], input=text, capture_output=True, text=True,
                                    check=True).stdout)

    acc = ({}, {})
    with ThreadPoolExecutor(WORKERS) as ex:
        for part in ex.map(one, ranges):
            merge(acc, part, 2 if half else 1)
    return acc


def solve(v):
    """x with J x = v (J is unimodular)."""
    M = [list(map(Fraction, J[i])) + [Fraction(v[i])] for i in range(4)]
    for c in range(4):
        p = next(r for r in range(c, 4) if M[r][c] != 0)
        M[c], M[p] = M[p], M[c]
        for r in range(4):
            if r != c and M[r][c] != 0:
                f = M[r][c] / M[c][c]
                M[r] = [a - f * b for a, b in zip(M[r], M[c])]
    x = [M[i][4] / M[i][i] for i in range(4)]
    assert all(q.denominator == 1 for q in x)
    return tuple(int(q) for q in x)


def analyse(rows):
    out = []
    for r in rows:
        if r["kind"] != "lsurf":
            continue
        twists = [tuple(a) for a in r["twists"]]
        counts = {}
        for s, d in r["sectors"].items():
            for c, n in d["lines"].items():
                counts[(twists[int(s)], tuple(map(int, c.split(","))))] = n
        classes = sorted({c for (_a, c) in counts})
        rec = {"label": r["label"], "classes": []}
        for c in classes:
            x = solve(c)
            odd = [a for a in twists if sum(p * q for p, q in zip(a, c)) & 1]
            vals = {a: counts.get((a, c), 0) for a in odd}
            if not any(vals.values()):
                rec["classes"].append({"coordinates": list(c), "class": list(x), "odd_lines": False})
                continue
            pairs, seen = [], set()
            for a in odd:
                b = tuple((p + q) & 1 for p, q in zip(a, x))
                if a in seen:
                    continue
                seen |= {a, b}
                pairs.append({"twists": ["".join(map(str, a)), "".join(map(str, b))], "counts": [vals[a], vals[b]],
                              "equal": vals[a] == vals[b]})
            pair_values = sorted({p["counts"][0] for p in pairs})
            rec["classes"].append({"coordinates": list(c), "class": list(x), "odd_lines": True,
                                   "counts": {"".join(map(str, a)): v for a, v in vals.items()},
                                   "dual_pairs": pairs, "dual_pairs_equal": all(p["equal"] for p in pairs),
                                   "distinct_pair_values": pair_values, "not_all_equal": len(pair_values) > 1})
        out.append(rec)
    tested = [c for rec in out for c in rec["classes"] if c["odd_lines"]]
    return {"surfaces": out, "classes_with_odd_lines": len(tested),
            "P1_dual_pairs_equal": bool(tested) and all(c["dual_pairs_equal"] for c in tested),
            "P2_not_all_equal": bool(tested) and all(c["not_all_equal"] for c in tested),
            "P2_failures": [(rec["label"], c["class"]) for rec in out for c in rec["classes"] if c["odd_lines"] and not c["not_all_equal"]]}


def controls(rows):
    fails = []
    for r in rows:
        twisted = [any(a) for a in r["twists"]]
        for s, d in r["sectors"].items():
            if d["c"] + d["x"] + sum(d["lines"].values()) != d["n"]:
                fails.append(f"totals {r['label']} twist {s}")
            if d["mis"]:
                fails.append(f"swap-invariance test {r['label']} twist {s}")
            if d["n"] != 1 << r["edges"]:
                fails.append(f"orientations {r['label']}")
            if not twisted[int(s)] and d["inv"]:
                fails.append(f"untwisted flagged {r['label']}")
    full = next(r for r in rows if r["label"] == "L(2,2,2,2) full")
    half = next(r for r in rows if r["label"] == "L(2,2,2,2)")
    if full["sectors"] != half["sectors"] or full["joint"] != half["joint"]:
        fails.append("half enumeration differs from the full one on L(2,2,2,2)")
    return fails


def main() -> int:
    contract = json.loads((HERE / "contract.json").read_text())
    assert contract["status"] == "Frozen" and contract["evidence_stage"] == "confirmatory"
    OUT.mkdir(parents=True, exist_ok=True)
    raw = OUT / "raw_rows.jsonl"
    if raw.exists():
        raw.unlink()
    started = time.time()
    build = Path(tempfile.mkdtemp(prefix="lineev-"))
    binary = str(build / "lineev")
    subprocess.run(["gcc", "-O2", "-o", binary, str(HERE / "lineev.c")], check=True)
    gcc = subprocess.run(["gcc", "--version"], capture_output=True, text=True).stdout.splitlines()[0]
    rows = []
    try:
        for fam, label, kind, params, half in ROSTER:
            text, twists, V, E, N = spec(kind, params)
            sectors, joint = enumerate_surface(binary, text, E, half)
            row = {"family": fam, "label": label, "kind": kind, "params": list(params), "vertices": V, "edges": E, "cells": N,
                   "half_enumeration": half, "twists": [list(a) for a in twists],
                   "sectors": {str(s): sectors[s] for s in sorted(sectors)},
                   "joint": {f"{a},{b}": joint[(a, b)] for a, b in sorted(joint)}}
            rows.append(row)
            with open(raw, "a") as f:
                f.write(json.dumps(row, sort_keys=True) + "\n")
            print(fam, label, E, round(time.time() - started), flush=True)
    finally:
        shutil.rmtree(build, ignore_errors=True)
    fails = controls(rows)
    result = {"schema_version": 1, "experiment_id": contract["experiment_id"], "ticket": contract["ticket"],
              "evidence_stage": contract["evidence_stage"], "controls_ok": not fails, "control_failures": fails,
              "rows": len(rows), "compiler": gcc, "workers": WORKERS}
    if fails:
        result["verdict"] = "invalid"
    else:
        a = analyse(rows)
        result["analysis"] = a
        if not a["P1_dual_pairs_equal"]:
            result["verdict"] = "refuted"
        else:
            result["verdict"] = "supported" if a["P2_not_all_equal"] else "partially supported"
    result["wall_seconds"] = round(time.time() - started, 1)
    result["max_rss_mib"] = round(resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss / 1024, 1)
    (OUT / "result.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({k: result[k] for k in ("controls_ok", "verdict", "wall_seconds") if k in result}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
