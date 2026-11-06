#!/usr/bin/env python3
"""Check CELL-SIZE-20261020-001B-P001: Tseitin size from cell systems.

Executable checks on declared instances:

1. Cell conditions (C1)-(C3): grids (non-corner squares; the 8 corner boundary edges exceptional), triangulated
   grids, walls with degree-2 vertices suppressed (r = 2..10), 3D grids. Also: faces pairwise share at most one
   edge, every inner face shares at most one edge with the outer face (plane families), and 3-connectivity for
   the small plane instances.
2. Detour systems under the selection rule of the proof (conflict radius 2*ell, p = 1/(N+1)): every detour
   avoids the restricted edges and no free edge carries more than L detours (wall14, trigrid14x14, grid3d6x6x6).
3. Retention, exhaustive (compiled C): every single selectable cell of wall3, trigrid4x5, grid4x5, grid3d2x3x3
   and grid3d2x2x5 keeps every cut within the factor L+1, and no nontrivial cut vanishes. Control: two bricks of
   wall3 at distance 2 (below the radius rule) make cuts vanish.
4. Kill probabilities on wall20: exact selection probabilities p(1-p)^|conflicts| against sampling.
5. The constants of the theorem for walls.
6. Transfer to a topological minor: a wall inside a grid with extra pendant structure; restriction values that
   make every vertex outside the wall even exist and are found; renaming along subdivided paths trivializes the
   degree-2 constraints and yields the suppressed wall with odd total charge.

    python3 -B check.py          verify result.json against a fresh run
    python3 -B check.py --write  write result.json
"""

from __future__ import annotations

import json
import math
import random
import subprocess
import sys
import tempfile
from collections import deque
from itertools import combinations
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import families as fm  # noqa: E402

C_RETAIN = r"""
#include <stdio.h>
#include <stdlib.h>
typedef unsigned __int128 u128;
static int popc(u128 x) { return __builtin_popcountll((unsigned long long)x) + __builtin_popcountll((unsigned long long)(x >> 64)); }
int main(void) {
    int n, m; if (scanf("%d %d", &n, &m) != 2) return 1;
    u128 star[64] = {0};
    for (int i = 0; i < m; i++) { int u, v; if (scanf("%d %d", &u, &v) != 2) return 1; star[u] |= ((u128)1) << i; star[v] |= ((u128)1) << i; }
    int k; if (scanf("%d", &k) != 1) return 1;
    double gworst = 0; long gvan = 0;
    for (int t = 0; t < k; t++) {
        int c; if (scanf("%d", &c) != 1) return 1; u128 del = 0;
        for (int j = 0; j < c; j++) { int e; if (scanf("%d", &e) != 1) return 1; del |= ((u128)1) << e; }
        u128 cut = 0; double w = 0; long van = 0;
        unsigned long long total = 1ULL << n;
        for (unsigned long long i = 1; i < total; i++) {
            int v = __builtin_ctzll(i); cut ^= star[v];
            int g = popc(cut), h = popc(cut & ~del);
            if (h == 0) { if (g > 0) van++; continue; }
            double r = (double)g / h; if (r > w) w = r;
        }
        if (w > gworst) gworst = w; gvan += van;
    }
    printf("SUMMARY %.6f %ld\n", gworst, gvan);
    return 0;
}
"""


# ---------------------------------------------------------------- helpers

def grid_with_exceptions(a, b):
    """2D grid; cells are the non-corner squares; U = the boundary edges at the four corners."""
    edges, squares = fm.grid(a, b)
    cells, U = [], []
    for r in range(a - 1):
        for c in range(b - 1):
            corner = r in (0, a - 2) and c in (0, b - 2)
            sq = squares[r * (b - 1) + c]
            if corner:
                for e in sq:
                    (x1, y1), (x2, y2) = e
                    on_boundary = (x1 == x2 and x1 in (0, a - 1)) or (y1 == y2 and y1 in (0, b - 1))
                    if on_boundary:
                        U.append(e)
            else:
                cells.append(sq)
    return edges, cells, U


def conflicts(F, radius):
    verts = [sorted({v for e in c for v in F.E[e]}) for c in F.cells]
    by_vertex = {}
    for i, vs in enumerate(verts):
        for v in vs:
            by_vertex.setdefault(v, []).append(i)
    out = []
    for i, vs in enumerate(verts):
        dist = {v: 0 for v in vs}
        q = deque(vs)
        while q:
            x = q.popleft()
            if dist[x] >= radius:
                continue
            for y, _ in F.adj[x]:
                if y not in dist:
                    dist[y] = dist[x] + 1
                    q.append(y)
        s = set()
        for v in dist:
            s.update(by_vertex.get(v, []))
        s.discard(i)
        out.append(s)
    return out


def detour_path(F, cell, e):
    u, v = F.E[e]
    banned = set(cell)
    prev = {u: None}
    q = deque([u])
    while q:
        x = q.popleft()
        if x == v:
            break
        for y, i in F.adj[x]:
            if i not in banned and y not in prev:
                prev[y] = (x, i)
                q.append(y)
    if v not in prev:
        return None
    path, x = [], v
    while prev[x] is not None:
        x, i = prev[x]
        path.append(i)
    return path


def cell_report(F, U=()):
    Uidx = {F.idx[fm.norm(*e)] for e in U}
    L = max(len(c) for c in F.cells)
    covered = {i for c in F.cells for i in c}
    c2 = covered | Uidx == set(range(len(F.E)))
    ell, fails = 0, 0
    for c in F.cells:
        for e in c:
            P = detour_path(F, c, e)
            if P is None:
                fails += 1
            else:
                ell = max(ell, len(P))
    share = max((len(set(a) & set(b)) for a, b in combinations(F.cells, 2)), default=0)
    count = {}
    for c in F.cells:
        for e in c:
            count[e] = count.get(e, 0) + 1
    outer = {e for e in range(len(F.E)) if count.get(e, 0) == 1}
    outer_share = max((len(set(c) & outer) for c in F.cells), default=0)
    return {"n": F.n, "m": len(F.E), "cells": len(F.cells), "L": L, "C2_all_but_exceptional": c2,
            "exceptional": len(Uidx), "C3_failures": fails, "ell": ell, "max_shared_edges_between_cells": share,
            "max_cell_edges_on_single_cell_edges": outer_share}


def run_retain(exe, F, masks):
    lines = [f"{F.n} {len(F.E)}"] + [f"{u} {v}" for u, v in F.E] + [str(len(masks))]
    lines += [" ".join([str(len(m))] + [str(e) for e in sorted(m)]) for m in masks]
    out = subprocess.run([str(exe)], input="\n".join(lines) + "\n", capture_output=True, text=True,
                         timeout=3600).stdout.split()
    return float(out[1]), int(out[2])


# ---------------------------------------------------------------- transfer to a topological minor

def transfer_demo(rng):
    """G: an a x b grid plus pendant paths and a pendant triangle; S: the wall inside the grid (vertical edges kept
    where x+y even, degree-1 vertices dropped). Restriction values make every vertex outside S even; renaming along
    the subdivided paths of S gives the suppressed wall with odd total charge."""
    a, b = 6, 9
    V = lambda x, y: (x, y)
    edges = set()
    for x in range(a):
        for y in range(b - 1):
            edges.add(fm.norm(V(x, y), V(x, y + 1)))
    for x in range(a - 1):
        for y in range(b):
            edges.add(fm.norm(V(x, y), V(x + 1, y)))
    extra = [(V(2, 3), ("p", 0)), (("p", 0), ("p", 1)), (("p", 1), ("p", 2)), (("p", 2), V(3, 7)),
             (V(0, 0), ("t", 0)), (("t", 0), ("t", 1)), (("t", 1), V(0, 0))]
    for e in extra:
        edges.add(fm.norm(*e) if isinstance(e[0][0], int) and isinstance(e[1][0], int) else tuple(sorted(e, key=str)))
    edges = sorted(edges, key=str)
    # the wall S inside the grid: horizontal edges along rows y (here: edges (x,y)-(x+1,y) are "rows" in x);
    # keep all edges (x,y)-(x,y+1) and the edges (x,y)-(x+1,y) with x+y even
    S = set()
    for x in range(a):
        for y in range(b - 1):
            S.add(fm.norm(V(x, y), V(x, y + 1)))
    for x in range(a - 1):
        for y in range(b):
            if (x + y) % 2 == 0:
                S.add(fm.norm(V(x, y), V(x + 1, y)))
    while True:
        deg = {}
        for u, v in S:
            deg[u] = deg.get(u, 0) + 1
            deg[v] = deg.get(v, 0) + 1
        ones = {v for v, d in deg.items() if d == 1}
        if not ones:
            break
        S = {e for e in S if e[0] not in ones and e[1] not in ones}
    VS = {v for e in S for v in e}
    allv = sorted({v for e in edges for v in e}, key=str)
    charge = {v: 0 for v in allv}
    charge[rng.choice(allv)] = 1
    F_edges = [e for e in edges if e not in S]
    # parity correction: spanning forest of (V, F) rooted at S-vertices; fix every non-S vertex bottom-up
    adj = {v: [] for v in allv}
    for e in F_edges:
        adj[e[0]].append((e[1], e))
        adj[e[1]].append((e[0], e))
    value = {e: rng.randrange(2) for e in F_edges}
    seen, order, parent = set(), [], {}
    for root in [v for v in allv if v in VS]:
        if root in seen:
            continue
        seen.add(root)
        q = deque([root])
        while q:
            x = q.popleft()
            order.append(x)
            for y, e in adj[x]:
                if y not in seen and y not in VS:
                    seen.add(y)
                    parent[y] = (x, e)
                    q.append(y)
    reached_all = all(v in seen for v in allv)
    for v in reversed(order):
        if v in VS or v not in parent:
            continue
        par = charge[v] + sum(value[e] for _, e in adj[v])
        if par % 2:
            _, e = parent[v]
            value[e] ^= 1
    newcharge = {v: (charge[v] + sum(value[e] for _, e in adj[v])) % 2 for v in allv}
    outside_even = all(newcharge[v] == 0 for v in allv if v not in VS)
    total_S = sum(newcharge[v] for v in VS) % 2
    # renaming along degree-2 paths of S: x_{e_j} := y_P + sigma_j, sigma_1 = 0, sigma_{j+1} = sigma_j + c(w_j);
    # the end vertex t of each path receives the pushed charge sigma_m
    sadj = {}
    for e in S:
        u, v = e
        sadj.setdefault(u, []).append((v, e))
        sadj.setdefault(v, []).append((u, e))
    branch = {v for v, ns in sadj.items() if len(ns) != 2}
    wcharge = {v: newcharge[v] for v in branch}
    paths, used = [], set()
    for s0 in sorted(branch, key=str):
        for t0, e0 in sadj[s0]:
            if e0 in used:
                continue
            verts, pedges = [s0, t0], [e0]
            used.add(e0)
            while verts[-1] not in branch:
                nxt = [(w, f) for w, f in sadj[verts[-1]] if f != pedges[-1]][0]
                verts.append(nxt[0])
                pedges.append(nxt[1])
                used.add(nxt[1])
            sigma = [0]
            for w in verts[1:-1]:
                sigma.append(sigma[-1] ^ newcharge[w])
            paths.append((verts, pedges, sigma))
            wcharge[verts[-1]] ^= sigma[-1]
    total_W = sum(wcharge.values()) % 2
    equivalent, inner_trivial = True, True
    for _ in range(300):
        y = [rng.randrange(2) for _ in paths]
        xval = {}
        for (verts, pedges, sigma), yp in zip(paths, y):
            for f, sg in zip(pedges, sigma):
                xval[f] = yp ^ sg
        for verts, pedges, sigma in paths:
            for j, w in enumerate(verts[1:-1]):
                if (xval[pedges[j]] ^ xval[pedges[j + 1]]) != newcharge[w]:
                    inner_trivial = False
        for bv in branch:
            s_side = (sum(xval[f] for _, f in sadj[bv]) + newcharge[bv]) % 2
            w_side = wcharge[bv]
            for (verts, pedges, sigma), yp in zip(paths, y):
                if verts[0] == bv:
                    w_side ^= yp
                if verts[-1] == bv:
                    w_side ^= yp
            if s_side != (w_side % 2):
                equivalent = False
    trivial_ok = inner_trivial and equivalent
    merged = paths
    reference_edges, _ = fm.wall(4)
    return {"grid": f"{a}x{b} plus pendant path and triangle", "wall_vertices_in_G": len(VS),
            "all_vertices_reached_by_correction_forest": reached_all, "outside_vertices_even": outside_even,
            "wall_total_charge_odd": total_S == 1, "branch_vertices": len(branch),
            "suppressed_wall_edges": len(merged), "suppressed_total_charge_odd": total_W == 1,
            "renamed_inner_constraints_trivial": trivial_ok}


# ---------------------------------------------------------------- run

def run():
    rng = random.Random(20261020)
    checks, controls = {}, {}

    fams = {}
    for a, b in ((5, 6), (8, 8)):
        e, c, U = grid_with_exceptions(a, b)
        fams[f"grid{a}x{b}"] = (fm.Fam(f"grid{a}x{b}", e, c), U)
    for a, b in ((6, 6), (10, 10)):
        fams[f"trigrid{a}x{b}"] = (fm.Fam(f"trigrid{a}x{b}", *fm.triangulated_grid(a, b, rng)), [])
    for r in range(2, 11):
        fams[f"wall{r}"] = (fm.Fam(f"wall{r}", *fm.wall(r)), [])
    for dims in ((3, 3, 3), (4, 4, 4), (3, 4, 5)):
        fams["grid3d" + "x".join(map(str, dims))] = (fm.Fam("g3", *fm.grid3(*dims)), [])
    reports = {name: cell_report(F, U) for name, (F, U) in fams.items()}
    for name in ("trigrid6x6", "wall2", "wall3", "wall4"):
        reports[name]["three_connected"] = fams[name][0].three_connected()
    ok = all(r["C2_all_but_exceptional"] and r["C3_failures"] == 0 for r in reports.values())
    plane_ok = all(reports[n]["max_shared_edges_between_cells"] <= 1 and reports[n]["max_cell_edges_on_single_cell_edges"] <= 1
                   for n in reports if n.startswith(("trigrid", "wall")))
    walls_ell = max(reports[f"wall{r}"]["ell"] for r in range(2, 11))
    checks["cell_conditions"] = {"holds": ok, "plane_faces_share_at_most_one_edge": plane_ok,
                                 "small_plane_instances_three_connected": all(reports[n]["three_connected"] for n in ("trigrid6x6", "wall2", "wall3", "wall4")),
                                 "wall_ell_max": walls_ell, "families": reports}

    det, det_ok = {}, True
    for name, F, ell, trials in (("wall14", fm.Fam("w", *fm.wall(14)), walls_ell, 200),
                                 ("trigrid14x14", fm.Fam("t", *fm.triangulated_grid(14, 14, rng)), 4, 200),
                                 ("grid3d6x6x6", fm.Fam("g", *fm.grid3(6, 6, 6)), 3, 200)):
        conf = conflicts(F, 2 * ell)
        N = max(len(c) for c in conf)
        p = 1.0 / (N + 1)
        L = max(len(c) for c in F.cells)
        worst, avoid, selected = 0, True, 0
        for _ in range(trials):
            active = [rng.random() < p for _ in F.cells]
            sel = [i for i, x in enumerate(active) if x and not any(active[j] for j in conf[i])]
            selected += len(sel)
            D = {i for s in sel for i in F.cells[s]}
            load = {}
            for s in sel:
                for e in F.cells[s]:
                    P = detour_path(F, F.cells[s], e)
                    avoid &= P is not None and not any(i in D for i in P)
                    for i in P or []:
                        load[i] = load.get(i, 0) + 1
            if load:
                worst = max(worst, max(load.values()))
        det[name] = {"N": N, "selections": selected, "detours_avoid_D": avoid, "max_congestion": worst, "L": L}
        det_ok &= avoid and worst <= L
    checks["detour_systems"] = {"holds": det_ok, "instances": det}

    with tempfile.TemporaryDirectory() as tmp:
        src, exe = Path(tmp) / "r.c", Path(tmp) / "r"
        src.write_text(C_RETAIN)
        built = subprocess.run(["gcc", "-O2", "-o", str(exe), str(src)], capture_output=True, text=True)
        checks["c_checker_built"] = built.returncode == 0
        ret, ret_ok = {}, True
        cases = {"wall3": fm.Fam("w3", *fm.wall(3)), "trigrid4x5": fm.Fam("t", *fm.triangulated_grid(4, 5, rng)),
                 "grid3d2x3x3": fm.Fam("g", *fm.grid3(2, 3, 3)), "grid3d2x2x5": fm.Fam("g", *fm.grid3(2, 2, 5))}
        e45, c45, _ = grid_with_exceptions(4, 5)
        cases["grid4x5"] = fm.Fam("grid4x5", e45, c45)
        for name, F in cases.items():
            L = max(len(c) for c in F.cells)
            worst, van = run_retain(exe, F, [set(c) for c in F.cells])
            ret[name] = {"L": L, "worst_ratio": worst, "vanishing_cuts": van}
            ret_ok &= worst <= L + 1 + 1e-9 and van == 0
        checks["retention_exhaustive"] = {"holds": ret_ok, "instances": ret}
        F = cases["wall3"]
        conf1 = conflicts(F, 1)
        pairs = [set(F.cells[i]) | set(F.cells[j]) for i, j in combinations(range(len(F.cells)), 2) if j not in conf1[i]]
        worst, van = run_retain(exe, F, pairs)
        controls["wall3_pairs_below_radius_break_retention"] = van > 0

    F = fm.Fam("w20", *fm.wall(20))
    conf = conflicts(F, 2 * walls_ell)
    N = max(len(c) for c in conf)
    p = 1.0 / (N + 1)
    probe = rng.sample(range(len(F.cells)), 6)
    hits = {i: 0 for i in probe}
    trials = 4000
    for _ in range(trials):
        active = [rng.random() < p for _ in F.cells]
        for i in probe:
            if active[i] and not any(active[j] for j in conf[i]):
                hits[i] += 1
    zs = []
    for i in probe:
        exact = p * (1 - p) ** len(conf[i])
        zs.append(abs(hits[i] / trials - exact) / math.sqrt(exact * (1 - exact) / trials))
    q = p * (1 - p) ** N / 2
    checks["kill_probabilities_wall20"] = {"selection_matches_formula": max(zs) < 5, "largest_z": round(max(zs), 2),
                                           "N": N, "p": round(p, 6), "q": round(q, 8)}

    # constants for walls: R = edges within distance 4*ell + 3L of an edge, measured on wall40 interior
    W = fm.Fam("w40", *fm.wall(40))
    centre = len(W.E) // 2
    u, v = W.E[centre]
    radius = 4 * walls_ell + 3 * 6
    dist = {u: 0, v: 0}
    qd = deque([u, v])
    while qd:
        x = qd.popleft()
        if dist[x] >= radius:
            continue
        for y, _ in W.adj[x]:
            if y not in dist:
                dist[y] = dist[x] + 1
                qd.append(y)
    R = sum(1 for (a, b) in W.E if a in dist and b in dist)
    gamma = math.log2(1 / (1 - q)) / (R * 2 * 7)
    checks["constants_walls"] = {"L": 6, "ell": walls_ell, "N": N, "q": q, "R_at_least_measured": R,
                                 "gamma_bits_per_unit_tangle_order_order_of_magnitude": f"{gamma:.1e}"}

    checks["transfer_to_topological_minor"] = transfer_demo(rng)
    t = checks["transfer_to_topological_minor"]
    transfer_ok = (t["all_vertices_reached_by_correction_forest"] and t["outside_vertices_even"]
                   and t["wall_total_charge_odd"] and t["suppressed_total_charge_odd"] and t["renamed_inner_constraints_trivial"])

    expected = [checks["cell_conditions"]["holds"], checks["cell_conditions"]["plane_faces_share_at_most_one_edge"],
                checks["cell_conditions"]["small_plane_instances_three_connected"], checks["detour_systems"]["holds"],
                checks["c_checker_built"], checks["retention_exhaustive"]["holds"],
                checks["kill_probabilities_wall20"]["selection_matches_formula"], transfer_ok]
    failures = [i for i, x in enumerate(expected) if not x] + [k for k, x in controls.items() if not x]
    return checks, controls, failures


def main() -> int:
    write = "--write" in sys.argv[1:]
    checks, controls, failures = run()
    manifest = json.loads((HERE / "manifest.json").read_text())
    result = {
        "schema_version": 3, "artifact_id": manifest["artifact_id"], "kind": "proof", "ticket": manifest["ticket"],
        "proof": manifest["proof"], "status": "passed" if not failures else "failed", "claim": manifest["claim"],
        "foundation_contract": manifest["foundation_contract"], "semantic_domains": manifest["semantic_domains"],
        "evidence_modes": manifest["evidence_modes"], "thesis_alignment": manifest["thesis_alignment"],
        "safe_conclusions": manifest["safe_to_conclude"], "checks": checks, "controls": controls, "failures": failures,
    }
    path = HERE / "result.json"
    text = json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False, default=str) + "\n"
    if write:
        path.write_text(text)
    elif not path.exists() or json.loads(path.read_text()) != json.loads(text):
        print("result.json does not match a fresh run; rerun with --write after review")
        return 1
    print(f"{result['status']}: failures {failures}")
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
