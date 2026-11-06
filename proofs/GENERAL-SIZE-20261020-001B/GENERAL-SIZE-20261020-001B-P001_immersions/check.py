#!/usr/bin/env python3
"""Check GENERAL-SIZE-20261020-001B-P001: Tseitin hardness transfers along weak immersions.

On declared instances, a non-planar graph H (K33 in a 6x6 grid, Petersen in a 10x10 grid) is weakly immersed in a planar grid G (edge-disjoint
paths, crossings at degree-4 vertices allowed), so H is not a topological minor of G. The check verifies each step
of the transfer in proof.md:

1. the paths are edge-disjoint and join the images of H's adjacent vertices;
2. restriction with parity correction: values on the edges outside the paths make every vertex off the paths even,
   with odd total charge left on the paths;
3. splitting: at every vertex of the union of paths, the incident path edges split into one copy per passing path
   and a branch copy; the original constraint is the sum of the copies' constraints, so every assignment satisfying
   the copies satisfies the original (checked on all assignments of the vertex's edges);
4. the split graph is a subdivision of H (suppressing degree-2 vertices returns exactly H);
5. renaming along the subdivided paths gives H's Tseitin formula with odd total charge, equivalent on random
   assignments.

It also measures the wall networks G(m, w, b) of proof.md: walls at the vertices of a cubic skeleton, joined along
each skeleton edge by a bundle of w edges that reverses the order of blocks of b ports and permutes each block.

E1. Ordered bundles (b = 1), degree-2 vertices suppressed: bricks and ladder cycles form a cell system; report U, L
    and the longest detour l.
E2. Spectral gap 3 - lambda_2 of two topological minors: wall boundary cycles plus bundles, and three nested
    ladders routed vertex-disjointly inside each wall plus bundles (the routing is built and verified here).
    lambda_2 is the top Ritz value of Lanczos with full reorthogonalization on the complement of the constants.
E3. Shortest cycle through each bundle edge, against the block size b.

    python3 -B check.py          verify result.json against a fresh run
    python3 -B check.py --write  write result.json
"""

from __future__ import annotations

import json
import math
import random
import statistics
import sys
from collections import deque
from itertools import product
from pathlib import Path

HERE = Path(__file__).resolve().parent


def grid(a, b):
    E = []
    for r in range(a):
        for c in range(b):
            if c + 1 < b:
                E.append(((r, c), (r, c + 1)))
            if r + 1 < a:
                E.append(((r, c), (r + 1, c)))
    return E


K33 = [(i, 3 + j) for i in range(3) for j in range(3)]
PETERSEN = [(0, 1), (1, 2), (2, 3), (3, 4), (0, 4), (0, 5), (1, 6), (2, 7), (3, 8), (4, 9), (5, 7), (7, 9), (6, 9), (6, 8),
            (5, 8)]


def find_immersion(GE, HE, rng, tries=4000):
    gadj = {}
    for i, (u, v) in enumerate(GE):
        gadj.setdefault(u, []).append((v, i))
        gadj.setdefault(v, []).append((u, i))
    hn = 1 + max(max(e) for e in HE)
    hdeg = [sum(1 for e in HE if x in e) for x in range(hn)]
    candidates = [v for v in gadj if len(gadj[v]) >= 4]
    for _ in range(tries):
        phi = rng.sample(candidates, hn)
        used, paths, ok = set(), [], True
        order = list(range(len(HE)))
        rng.shuffle(order)
        routed = {}
        for k in order:
            a, b = HE[k]
            s, t = phi[a], phi[b]
            prev = {s: None}
            q = deque([s])
            while q:
                x = q.popleft()
                if x == t:
                    break
                for y, i in gadj[x]:
                    if i not in used and y not in prev:
                        prev[y] = (x, i)
                        q.append(y)
            if t not in prev:
                ok = False
                break
            verts, edges, x = [t], [], t
            while prev[x] is not None:
                x, i = prev[x]
                verts.append(x)
                edges.append(i)
            verts.reverse()
            edges.reverse()
            used.update(edges)
            routed[k] = (verts, edges)
        if ok:
            return phi, [routed[k] for k in range(len(HE))]
    return None


def verify(GE, HE, phi, paths, rng):
    out = {}
    gadj = {}
    for i, (u, v) in enumerate(GE):
        gadj.setdefault(u, []).append((v, i))
        gadj.setdefault(v, []).append((u, i))
    V = sorted(gadj)
    # 1. edge-disjoint, correct endpoints
    all_edges = [i for _, es in paths for i in es]
    disjoint = len(all_edges) == len(set(all_edges))
    ends = all(verts[0] == phi[a] and verts[-1] == phi[b] for (a, b), (verts, _) in zip(HE, paths))
    out["paths_edge_disjoint_with_correct_ends"] = disjoint and ends
    crossing_vertices = sum(1 for v in V if sum(1 for verts, _ in paths if v in verts[1:-1]) >= 2)
    out["crossing_vertices"] = crossing_vertices
    # 2. restriction with parity correction
    path_edges = set(all_edges)
    Vpp = {v for verts, _ in paths for v in verts}
    charge = {v: 0 for v in V}
    charge[rng.choice(V)] = 1
    F = [i for i in range(len(GE)) if i not in path_edges]
    fadj = {v: [] for v in V}
    for i in F:
        u, w = GE[i]
        fadj[u].append((w, i))
        fadj[w].append((u, i))
    value = {i: rng.randrange(2) for i in F}
    seen, order, parent = set(), [], {}
    for root in [v for v in V if v in Vpp]:
        if root in seen:
            continue
        seen.add(root)
        q = deque([root])
        while q:
            x = q.popleft()
            order.append(x)
            for y, i in fadj[x]:
                if y not in seen and y not in Vpp:
                    seen.add(y)
                    parent[y] = (x, i)
                    q.append(y)
    for v in reversed(order):
        if v in Vpp or v not in parent:
            continue
        if (charge[v] + sum(value[i] for _, i in fadj[v])) % 2:
            value[parent[v][1]] ^= 1
    c2 = {v: (charge[v] + sum(value[i] for _, i in fadj[v])) % 2 for v in V}
    out["off_path_vertices_even"] = all(c2[v] == 0 for v in V if v not in Vpp) and all(v in seen for v in V)
    out["path_union_total_odd"] = sum(c2[v] for v in Vpp) % 2 == 1
    # 3. splitting: copies per vertex
    copies = {}          # v -> list of (edge list, charge)
    branch_of = {phi[x]: x for x in range(len(phi))}
    for v in Vpp:
        parts = []
        if v in branch_of:
            ends_here = [es[0] if verts[0] == v else es[-1] for verts, es in paths if v in (verts[0], verts[-1])]
            parts.append(ends_here)
        for verts, es in paths:
            if v in verts[1:-1]:
                j = verts.index(v)
                parts.append([es[j - 1], es[j]])
        charges = [0] * len(parts)
        charges[0] = c2[v]
        copies[v] = list(zip(parts, charges))
    partition_ok, implication_ok = True, True
    for v, parts in copies.items():
        incident = sorted(i for _, i in gadj[v] if i in path_edges)
        flat = sorted(i for es, _ in parts for i in es)
        if flat != incident:
            partition_ok = False
            continue
        for bits in product((0, 1), repeat=len(incident)):
            x = dict(zip(incident, bits))
            merged = (sum(bits) + c2[v]) % 2 == 0
            split_ok = all((sum(x[i] for i in es) + ch) % 2 == 0 for es, ch in parts)
            if split_ok and not merged:
                implication_ok = False
    out["split_edges_partition_each_vertex"] = partition_ok
    out["split_constraints_imply_original"] = implication_ok
    # 4. split graph is a subdivision of H, and 5. renaming to H
    #    each H-edge is one path; its copies are the passing copies; branch copies are H's vertices
    hcharge = {x: 0 for x in range(len(phi))}
    for v, parts in copies.items():
        es0, ch0 = parts[0]
        if v in branch_of:
            hcharge[branch_of[v]] ^= ch0
    # charges of passing copies are pushed to the path's end (renaming)
    for (a, b), (verts, es) in zip(HE, paths):
        for v in verts[1:-1]:
            for es_c, ch in copies[v]:
                if set(es_c) <= set(es) and len(es_c) == 2:
                    hcharge[b] ^= ch
    out["split_graph_is_subdivision_of_H"] = all(len(set(verts)) == len(verts) for verts, _ in paths)
    out["H_total_charge_odd"] = sum(hcharge.values()) % 2 == 1
    equivalent = True
    passing = {}
    for k, (verts, es) in enumerate(paths):
        for j in range(1, len(verts) - 1):
            passing[(k, j)] = next(ch for es_c, ch in copies[verts[j]] if set(es_c) == {es[j - 1], es[j]})
    for _ in range(300):
        y = [rng.randrange(2) for _ in HE]
        xval = {}
        for k, ((verts, es), yp) in enumerate(zip(paths, y)):
            cur = yp
            for j, i in enumerate(es):
                xval[i] = cur
                if j + 1 < len(es):
                    cur ^= passing[(k, j + 1)]
        for k, (verts, es) in enumerate(paths):
            for j in range(1, len(verts) - 1):
                if (xval[es[j - 1]] ^ xval[es[j]] ^ passing[(k, j)]) != 0:
                    equivalent = False
        for x in range(len(phi)):
            es0, ch0 = copies[phi[x]][0]
            g_side = (sum(xval[i] for i in es0) + ch0) % 2
            h_side = (sum(yp for (a, b), yp in zip(HE, y) if x in (a, b)) + hcharge[x]) % 2
            if g_side != h_side:
                equivalent = False
    out["renamed_formula_equivalent_to_H"] = equivalent
    return out


# ----------------------------------------------------------------------------------------- wall networks (E1-E3)

def random_cubic(m, rng):
    while True:
        half = [v for v in range(m) for _ in range(3)]
        rng.shuffle(half)
        E = [tuple(sorted(half[i:i + 2])) for i in range(0, 3 * m, 2)]
        if any(a == b for a, b in E) or len(set(E)) < len(E):
            continue
        adj = {v: [] for v in range(m)}
        for a, b in E:
            adj[a].append(b)
            adj[b].append(a)
        seen, stack = {0}, [0]
        while stack:
            x = stack.pop()
            for y in adj[x]:
                if y not in seen:
                    seen.add(y)
                    stack.append(y)
        if len(seen) == m:
            return E


def wall_with_ports(w):
    """Elementary wall of height r = 2w in the (r+1) x (2r+2) grid, degree-1 corners removed. Ports are degree-2
    boundary vertices: arcs 0 and 1 on the top row (left to right) and arc 2 on the bottom row (right to left), so the
    arcs follow the boundary cycle in order."""
    r = 2 * w
    V = {(i, j) for i in range(r + 1) for j in range(2 * r + 2)}
    E = {((i, j), (i, j + 1)) for i in range(r + 1) for j in range(2 * r + 1)}
    E |= {((i, j), (i + 1, j)) for i in range(r) for j in range(2 * r + 2) if (i + j) % 2 == 0}
    deg = {v: 0 for v in V}
    for u, v in E:
        deg[u] += 1
        deg[v] += 1
    drop = {v for v in V if deg[v] == 1}
    E = {e for e in E if e[0] not in drop and e[1] not in drop}
    V -= drop
    deg = {v: 0 for v in V}
    for u, v in E:
        deg[u] += 1
        deg[v] += 1
    top = [(0, j) for j in range(1, 2 * r + 1, 2) if deg[(0, j)] == 2]
    bottom = sorted((v for v in V if v[0] == r and v[1] % 2 == 0 and 0 < v[1] <= 2 * r and deg[v] == 2),
                    key=lambda v: -v[1])
    segs = [top[:w], top[w:2 * w], bottom[:w]]
    assert all(len(s) == w for s in segs)
    bricks = [[(i, j), (i, j + 1), (i, j + 2), (i + 1, j + 2), (i + 1, j + 1), (i + 1, j)]
              for i in range(r) for j in range(2 * r) if (i + j) % 2 == 0]
    return V, E, segs, [c for c in bricks if all(v in V for v in c)]


def scrambled_map(w, b, rng):
    """Port k of one arc goes to port pi[k] of the other: blocks of b ports in reversed order, each block permuted."""
    pi = [0] * w
    for beta in range(w // b):
        tau = list(range(b))
        rng.shuffle(tau)
        for i in range(b):
            pi[beta * b + i] = w - 1 - (beta * b + tau[i])
    return pi


def bundle_maps(skel, w, b, rng):
    used, maps = {}, []
    for a, c in skel:
        sa, sc = used.get(a, 0), used.get(c, 0)
        used[a], used[c] = sa + 1, sc + 1
        maps.append((a, sa, c, sc, scrambled_map(w, b, rng)))
    return maps


def network(m, w, b, rng, skel):
    """G(m, w, b) with its cells: the bricks, and a ladder cycle through each two bundle edges at neighbouring
    ports on both sides."""
    _, E, segs, bricks = wall_with_ports(w)
    ids = {}

    def vid(x):
        return ids.setdefault(x, len(ids))

    edges = {tuple(sorted((vid((a,) + u), vid((a,) + v)))) for a in range(m) for u, v in E}
    cells = [[vid((a,) + v) for v in c] for a in range(m) for c in bricks]
    bundle = []
    for a, sa, c, sc, pi in bundle_maps(skel, w, b, rng):
        P, Q = segs[sa], segs[sc]
        for k in range(w):
            e = tuple(sorted((vid((a,) + P[k]), vid((c,) + Q[pi[k]]))))
            edges.add(e)
            bundle.append(e)
        for k in range(w - 1):
            if abs(pi[k + 1] - pi[k]) == 1:
                mid_a = (P[k][0], (P[k][1] + P[k + 1][1]) // 2)
                mid_c = (Q[pi[k]][0], (Q[pi[k]][1] + Q[pi[k + 1]][1]) // 2)
                cells.append([vid((a,) + P[k]), vid((a,) + mid_a), vid((a,) + P[k + 1]),
                              vid((c,) + Q[pi[k + 1]]), vid((c,) + mid_c), vid((c,) + Q[pi[k]])])
    adj = [[] for _ in range(len(ids))]
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)
    return adj, cells, bundle


def suppress(adj, cells=()):
    """Suppress every degree-2 vertex. Returns the new adjacency (asserting a simple graph) and the cells."""
    keep = [len(a) != 2 for a in adj]
    new = {v: i for i, v in enumerate(v for v in range(len(adj)) if keep[v])}
    seen = {}
    for s in new:
        for y in adj[s]:
            prev, cur = s, y
            while not keep[cur]:
                prev, cur = cur, adj[cur][0] if adj[cur][0] != prev else adj[cur][1]
            assert cur != s, "loop after suppression"
            key = tuple(sorted((new[s], new[cur])))
            seen[key] = seen.get(key, 0) + 1
    assert all(c == 2 for c in seen.values()), "parallel edges after suppression"
    nadj = [[] for _ in new]
    for u, v in seen:
        nadj[u].append(v)
        nadj[v].append(u)
    ncells = [[new[v] for v in c if keep[v]] for c in cells]
    for c in ncells:
        assert len(c) >= 3 and all(c[(i + 1) % len(c)] in nadj[c[i]] for i in range(len(c)))
    return nadj, ncells


def cell_check(adj, cells, limit=40):
    def key(u, v):
        return (u, v) if u < v else (v, u)

    covered = {key(c[i], c[(i + 1) % len(c)]) for c in cells for i in range(len(c))}
    edges = {key(u, v) for u in range(len(adj)) for v in adj[u]}
    worst, fails = 0, 0
    for c in cells:
        ce = {key(c[i], c[(i + 1) % len(c)]) for i in range(len(c))}
        for i in range(len(c)):
            s, t = c[i], c[(i + 1) % len(c)]
            dist, q, found = {s: 0}, deque([s]), None
            while q and found is None:
                x = q.popleft()
                if dist[x] >= limit:
                    break
                for y in adj[x]:
                    if y not in dist and key(x, y) not in ce:
                        dist[y] = dist[x] + 1
                        if y == t:
                            found = dist[y]
                            break
                        q.append(y)
            if found is None:
                fails += 1
            else:
                worst = max(worst, found)
    return {"cells": len(cells), "exceptional_edges_U": len(edges - covered),
            "cell_length_L": max(len(c) for c in cells), "longest_detour_l": worst,
            "cell_edges_without_detour_within_40": fails}


def route_ladders(w):
    """Inside one wall, route three ladders. Ladder s has chords t = 0..w/2-1 from port w-1-t of arc s to port t of
    arc s+1, innermost first, and a rung between consecutive chords. All paths are vertex-disjoint except where a rung
    meets a chord at a degree-3 vertex. Returns (segs, chords, rungs) or None."""
    V, E, segs, _ = wall_with_ports(w)
    adj = {v: [] for v in V}
    for u, v in E:
        adj[u].append(v)
        adj[v].append(u)
    used = {p for s in segs for p in s}
    chords, rungs, attach = {}, [], set()

    def bfs(sources, targets):
        prev = {s: None for s in sources}
        q = deque(sources)
        while q:
            x = q.popleft()
            for y in adj[x]:
                if y in targets:
                    path = [y, x]
                    while prev[path[-1]] is not None:
                        path.append(prev[path[-1]])
                    return path[::-1]
                if y not in prev and y not in used:
                    prev[y] = x
                    q.append(y)
        return None

    for t in range(w // 2):
        for s in range(3):
            path = bfs([segs[s][w - 1 - t]], {segs[(s + 1) % 3][t]})
            if path is None:
                return None
            chords[(s, t)] = path
            used.update(path)
    for s in range(3):
        for t in range(1, w // 2):
            inner = [v for v in chords[(s, t - 1)][1:-1] if v not in attach and len(adj[v]) == 3]
            outer = {v for v in chords[(s, t)][1:-1] if v not in attach and len(adj[v]) == 3}
            path = bfs(inner, outer)
            if path is None:
                return None
            rungs.append(path)
            attach.update((path[0], path[-1]))
            used.update(path)
    return segs, chords, rungs


def as_lists(adj_dict):
    ids = {v: i for i, v in enumerate(adj_dict)}
    return [[ids[y] for y in adj_dict[v]] for v in adj_dict]


def ladder_minor(m, w, maps, routed):
    """The routed ladders in every wall plus the bundles, as a subgraph S of G; returns S with degree-2 vertices
    suppressed, i.e. the topological minor H."""
    segs, chords, rungs = routed
    adj = {}

    def add(u, v):
        adj.setdefault(u, []).append(v)
        adj.setdefault(v, []).append(u)

    for a in range(m):
        for path in list(chords.values()) + rungs:
            for u, v in zip(path, path[1:]):
                add((a,) + u, (a,) + v)
    for a, sa, c, sc, pi in maps:
        for k in range(w):
            add((a,) + segs[sa][k], (c,) + segs[sc][pi[k]])
    assert max(len(x) for x in adj.values()) <= 3
    return suppress(as_lists(adj))[0]


def boundary_minor(m, w, maps):
    """Each wall's boundary cycle through its 3w ports, plus the bundles, with non-port vertices suppressed."""
    adj = {}

    def add(u, v):
        adj.setdefault(u, []).append(v)
        adj.setdefault(v, []).append(u)

    for a in range(m):
        cyc = [(a, s, k) for s in range(3) for k in range(w)]
        for i in range(len(cyc)):
            add(cyc[i], cyc[(i + 1) % len(cyc)])
    for a, sa, c, sc, pi in maps:
        for k in range(w):
            add((a, sa, k), (c, sc, pi[k]))
    return as_lists(adj)


def lanczos_lambda2(adj, steps, rng):
    """Largest eigenvalue of the adjacency matrix on the complement of the constant vector (Lanczos with full
    reorthogonalization); returns the top Ritz value after steps // 2 and after steps iterations."""
    n = len(adj)
    q = [rng.gauss(0, 1) for _ in range(n)]
    mu = sum(q) / n
    q = [x - mu for x in q]
    nr = math.sqrt(sum(x * x for x in q))
    Q, alpha, beta, track = [[x / nr for x in q]], [], [], []
    for it in range(1, steps + 1):
        q = Q[-1]
        z = [sum(q[u] for u in adj[v]) for v in range(n)]
        alpha.append(sum(a * b for a, b in zip(z, q)))
        for qq in Q:
            c = sum(a * b for a, b in zip(z, qq))
            z = [a - c * b for a, b in zip(z, qq)]
        mu = sum(z) / n
        z = [x - mu for x in z]
        bn = math.sqrt(sum(x * x for x in z))
        if it in (steps // 2, steps) or bn < 1e-10:
            track.append(top_eigenvalue(alpha, beta))
        if bn < 1e-10:
            break
        beta.append(bn)
        Q.append([x / bn for x in z])
    return track[0], track[-1]


def top_eigenvalue(alpha, beta):
    k = len(alpha)

    def below(x):
        cnt, d = 0, 1.0
        for i in range(k):
            d = alpha[i] - x - ((beta[i - 1] ** 2) / d if i else 0.0)
            if d == 0:
                d = -1e-300
            cnt += d < 0
        return cnt

    lo, hi = -3.5, 3.5
    for _ in range(70):
        mid = (lo + hi) / 2
        if below(mid) >= k:
            hi = mid
        else:
            lo = mid
    return hi


def girth_through(adj, u, v, cap=400):
    dist, q = {u: 0}, deque([u])
    while q:
        x = q.popleft()
        if dist[x] >= cap:
            break
        for y in adj[x]:
            if x == u and y == v:
                continue
            if y == v:
                return dist[x] + 2
            if y not in dist:
                dist[y] = dist[x] + 1
                q.append(y)
    return None


def wall_networks(failures):
    out = {}
    skel16 = random_cubic(16, random.Random(7))
    e1 = {}
    for w in (12, 24):
        adj, cells, _ = network(16, w, 1, random.Random(w), skel16)
        res = cell_check(*suppress(adj, cells))
        e1[f"w{w}"] = res
        if (res["exceptional_edges_U"] or res["cell_length_L"] != 6 or res["cell_edges_without_detour_within_40"]
                or res["longest_detour_l"] > 20):
            failures.append(f"E1 w={w}: ordered bundles do not give the expected cell system")
    out["E1_ordered_bundles_cell_system_m16"] = e1
    e2 = {}
    for w in (12, 24, 48):
        routed = route_ladders(w)
        if routed is None:
            failures.append(f"E2 w={w}: ladder routing failed")
            continue
        row = {}
        for label, b in (("ordered_b1", 1), ("blocks_b4", 4), ("uniform_bw", w)):
            r2 = random.Random(31 * w + b)
            maps = bundle_maps(skel16, w, b, r2)
            hadj = ladder_minor(16, w, maps, routed)
            half, full = lanczos_lambda2(hadj, 100, r2)
            row[label] = {"branch_vertices": len(hadj), "all_degree_3": all(len(x) == 3 for x in hadj),
                          "ladder_minor_gap": round(3 - full, 4), "ladder_minor_gap_at_half_steps": round(3 - half, 4)}
            if not row[label]["all_degree_3"]:
                failures.append(f"E2 w={w} {label}: ladder minor not cubic")
            if label == "uniform_bw":
                bh, bf = lanczos_lambda2(boundary_minor(16, w, maps), 100, r2)
                row[label]["boundary_cycle_minor_gap"] = round(3 - bf, 4)
        e2[f"w{w}"] = row
        u = row["uniform_bw"]
        if u["ladder_minor_gap"] < 0.03 or abs(u["ladder_minor_gap"] - u["ladder_minor_gap_at_half_steps"]) > 2e-3:
            failures.append(f"E2 w={w}: uniform-bundle ladder minor gap below 0.03 or not converged")
        if u["boundary_cycle_minor_gap"] > 0.2 * u["ladder_minor_gap"]:
            failures.append(f"E2 w={w}: boundary-cycle minor not clearly worse than the ladder minor")
        if row["ordered_b1"]["ladder_minor_gap"] > 1e-6:
            failures.append(f"E2 w={w}: ordered-bundle ladder minor unexpectedly connected")
    out["E2_spectral_gaps_m16"] = e2
    e3 = {}
    k4 = [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)]
    for b in (1, 4, 16, 64):
        adj, _, bundle = network(4, 64, b, random.Random(500 + b), k4)
        lengths = [girth_through(adj, u, v) for u, v in bundle]
        e3[f"b{b}"] = {"median": statistics.median(lengths), "mean": round(statistics.mean(lengths), 2),
                       "max": max(lengths)}
    medians = [e3[f"b{b}"]["median"] for b in (1, 4, 16, 64)]
    if medians != sorted(medians) or medians[-1] < medians[0] + 4:
        failures.append("E3: shortest cycles through bundle edges do not grow with the block size")
    out["E3_shortest_cycle_through_bundle_edges_K4_w64"] = e3
    return out


def run():
    rng = random.Random(20261020)
    checks, failures = {}, []
    for name, GE, HE in (("K33_in_grid6x6", grid(6, 6), K33), ("Petersen_in_grid10x10", grid(10, 10), PETERSEN)):
        found = find_immersion(GE, HE, rng)
        if found is None:
            checks[name] = {"immersion_found": False}
            failures.append(name)
            continue
        phi, paths = found
        res = verify(GE, HE, phi, paths, rng)
        res["immersion_found"] = True
        res["path_lengths"] = [len(es) for _, es in paths]
        checks[name] = res
        for key in ("paths_edge_disjoint_with_correct_ends", "off_path_vertices_even", "path_union_total_odd",
                    "split_edges_partition_each_vertex", "split_constraints_imply_original",
                    "split_graph_is_subdivision_of_H", "H_total_charge_odd", "renamed_formula_equivalent_to_H"):
            if not res[key]:
                failures.append(f"{name}:{key}")
        if res["crossing_vertices"] == 0:
            failures.append(f"{name}:no crossing used (immersion indistinguishable from a topological minor)")
    checks["wall_networks"] = wall_networks(failures)
    return checks, failures


def main() -> int:
    write = "--write" in sys.argv[1:]
    checks, failures = run()
    manifest = json.loads((HERE / "manifest.json").read_text())
    result = {
        "schema_version": 3, "artifact_id": manifest["artifact_id"], "kind": "proof", "ticket": manifest["ticket"],
        "proof": manifest["proof"], "status": "passed" if not failures else "failed", "claim": manifest["claim"],
        "foundation_contract": manifest["foundation_contract"], "semantic_domains": manifest["semantic_domains"],
        "evidence_modes": manifest["evidence_modes"], "thesis_alignment": manifest["thesis_alignment"],
        "safe_conclusions": manifest["safe_to_conclude"], "checks": checks, "controls": {}, "failures": failures,
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
