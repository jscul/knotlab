"""Lane C (NEXT-DIRECTION-SCAN-20261031-001C): counting one line short of Seymour's bound.

A triple system with n points and n - 1 lines sits one line below Seymour's bound (a minimally non-2-colourable hypergraph has at least as
many lines as points). The note's Theorem 1 counts H - L in polynomial time when H is a connected non-2-colourable cubic triple system.
This lane checks the two cheap discriminators:
  1. disjoint union with Fano - L (10 colourings) puts every cubic counting instance one line short;
  2. point splitting does the same with connected instances: split a point v of a cubic system H0 off one of its lines (H1), then add the
     line {v, v', w} (H2); both are connected, have one line fewer than points and degree at most 3, are Seymour-sparse (every nonempty set
     of lines spans more points than lines), and #col(H0) = 2 #col(H1) - #col(H2).
Counting 2-colourings of cubic triple systems is #P-complete (Fan-Cai 2020; SOFT-CROSS-20261031-001B), so both deficiency-one classes are
#P-hard, and one line short of the bound only the knot's subclass (Theorem 1) is known to be easy.
Run: .venv/bin/python -B short.py [--write]"""
import itertools
import json
import sys
import time
from pathlib import Path

import networkx as nx

HERE = Path(__file__).resolve().parent
T0 = time.time()
OUT = {}


def check(name, ok, info):
    OUT[name] = {"pass": bool(ok), "info": info}
    print("PASS" if ok else "FAIL", name, json.dumps(info, default=str)[:700], round(time.time() - T0, 1), "s", flush=True)
    if not ok:
        print(json.dumps(info, default=str, indent=1))
        sys.exit(1)


def system(g):
    """a cubic triple system from a cubic bipartite graph: colour class 0 = points, lines = neighbourhoods of class 1"""
    col = nx.bipartite.color(g)
    pts = sorted((v for v in g if col[v] == 0), key=str)
    return pts, [tuple(sorted(g[l], key=str)) for l in sorted((v for v in g if col[v] == 1), key=str)]


def ncol(pts, lines):
    idx = {p: i for i, p in enumerate(pts)}
    L = [[idx[p] for p in l] for l in lines]
    tot = 0
    for c in itertools.product((0, 1), repeat=len(pts)):
        tot += all(len({c[i] for i in l}) == 2 for l in L)
    return tot


def connected(pts, lines):
    g = nx.Graph()
    g.add_nodes_from(pts)
    for l in lines:
        g.add_edges_from(itertools.combinations(l, 2))
    return nx.is_connected(g)


def degrees(pts, lines):
    d = {p: 0 for p in pts}
    for l in lines:
        for p in l:
            d[p] += 1
    return d


def sparse(lines):
    """Seymour-sparse: every nonempty set of lines spans more points than it has lines"""
    for k in range(1, len(lines) + 1):
        for F in itertools.combinations(lines, k):
            if len(set().union(*F)) <= k:
                return False
    return True


FANO = [(0, 1, 2), (0, 3, 4), (0, 5, 6), (1, 3, 5), (1, 4, 6), (2, 3, 6), (2, 4, 5)]
HEAWOOD = nx.Graph([(('p', p), ('l', i)) for i, l in enumerate(FANO) for p in l])
SYSTEMS = {"K4^(3) (cube)": nx.hypercube_graph(3), "6-prism": nx.circular_ladder_graph(6), "8-prism": nx.circular_ladder_graph(8),
           "Moebius-Kantor": nx.LCF_graph(16, [5, -5], 8), "Pappus": nx.pappus_graph(), "Fano (Heawood)": HEAWOOD}

# ------------------------------------------------------------------------------------------------ 1. disjoint union with Fano - L
fano_minus = FANO[1:]
f10 = ncol(list(range(7)), fano_minus)
res1 = {"#col(Fano - L)": f10}
for name, g in SYSTEMS.items():
    pts, lines = system(g)
    a = ncol(pts, lines)
    upts = [('k', p) for p in pts] + [('f', i) for i in range(7)]
    ulines = [tuple(('k', p) for p in l) for l in lines] + [tuple(('f', i) for i in l) for l in fano_minus]
    b = ncol(upts, ulines)
    res1[name] = {"points, lines": [len(upts), len(ulines)], "#col(H0)": a, "#col(H0 + (Fano - L))": b, "ratio": b / a if a else None}
check("1 disjoint union with Fano - L: one line short, and #col = 10 #col(H0)", f10 == 10 and all(
    v["#col(H0 + (Fano - L))"] == 10 * v["#col(H0)"] and v["points, lines"][0] == v["points, lines"][1] + 1 for k, v in res1.items()
    if isinstance(v, dict)), res1)

# ------------------------------------------------------------------------------------------------ 2. point splitting, connected
res2 = {}
for name, g in SYSTEMS.items():
    pts, lines = system(g)
    h0 = ncol(pts, lines)
    trials = []
    for v in pts[:3]:
        for j in [k for k, l in enumerate(lines) if v in l]:
            l3 = tuple(("v'" if p == v else p) for p in lines[j])
            pts1 = pts + ["v'"]
            lines1 = lines[:j] + [l3] + lines[j + 1:]
            pts2 = pts1 + ["w"]
            lines2 = lines1 + [(v, "v'", "w")]
            c1, c2 = ncol(pts1, lines1), ncol(pts2, lines2)
            ok = (2 * c1 - c2 == h0 and connected(pts1, lines1) and connected(pts2, lines2)
                  and len(pts1) == len(lines1) + 1 and len(pts2) == len(lines2) + 1
                  and max(degrees(pts1, lines1).values()) <= 3 and max(degrees(pts2, lines2).values()) <= 3)
            trials.append({"v": str(v), "split line": j, "#col(H1)": c1, "#col(H2)": c2, "ok": ok,
                           "Seymour-sparse": sparse(lines1) and sparse(lines2)})
    res2[name] = {"#col(H0)": h0, "splits checked": len(trials), "all ok": all(t["ok"] for t in trials),
                  "H1 and H2 Seymour-sparse in every split": all(t["Seymour-sparse"] for t in trials), "first": trials[0]}
check("2 point splitting: connected, one line short, degree <= 3, Seymour-sparse, and #col(H0) = 2 #col(H1) - #col(H2)", all(
    v["all ok"] and v["H1 and H2 Seymour-sparse in every split"] for v in res2.values()), res2)

# ------------------------------------------------------------------------------------------------ 3. the knot's subclass for contrast
res3 = {}
for name in ("Fano (Heawood)",):
    pts, lines = system(SYSTEMS[name])
    res3[name] = {"#col(H)": ncol(pts, lines), "#col(H - L) for each L": [ncol(pts, lines[:k] + lines[k + 1:]) for k in range(len(lines))]}
check("3 contrast: on the knot's spaces the deficiency-one count is Theorem 1's (Fano: H non-colourable, every H - L has 10)",
      res3["Fano (Heawood)"]["#col(H)"] == 0 and set(res3["Fano (Heawood)"]["#col(H - L) for each L"]) == {10}, res3)

OUT["seconds"] = round(time.time() - T0, 1)
print("ALL OK", OUT["seconds"], "s")
if "--write" in sys.argv:
    (HERE / "results.json").write_text(json.dumps(OUT, indent=1, default=str) + "\n")
