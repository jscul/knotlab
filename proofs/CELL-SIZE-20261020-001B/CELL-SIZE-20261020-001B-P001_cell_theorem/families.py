"""Families with explicit cells (short cycles), and checks of the cell conditions:
(C1) cells have length <= L; (C2) every edge on a cell; (C3) for each cell C and edge e=uv of C, a u-v path avoiding E(C).
Reports L, the largest shortest-detour length ell, and 3-connectivity (brute force) when requested."""
from collections import deque
from itertools import combinations, product

def norm(u, v):
    return (u, v) if u < v else (v, u)

class Fam:
    def __init__(self, name, edges, cells):
        self.name = name
        self.edges = sorted({norm(*e) for e in edges})
        self.idx = {e: i for i, e in enumerate(self.edges)}
        verts = sorted({x for e in self.edges for x in e})
        self.vmap = {v: i for i, v in enumerate(verts)}
        self.n = len(verts)
        self.E = [(self.vmap[a], self.vmap[b]) for a, b in self.edges]
        self.cells = [sorted(self.idx[norm(*e)] for e in c) for c in cells]
        self.adj = [[] for _ in range(self.n)]
        for i, (a, b) in enumerate(self.E):
            self.adj[a].append((b, i)); self.adj[b].append((a, i))

    def detour(self, cell, e):
        u, v = self.E[e]
        banned = set(cell)
        dist = {u: 0}; q = deque([u])
        while q:
            x = q.popleft()
            if x == v:
                return dist[x]
            for y, i in self.adj[x]:
                if i not in banned and y not in dist:
                    dist[y] = dist[x] + 1; q.append(y)
        return None

    def report(self, three_conn=False):
        L = max(len(c) for c in self.cells)
        covered = set(i for c in self.cells for i in c)
        c2 = covered == set(range(len(self.E)))
        ell, bad = 0, 0
        for c in self.cells:
            for e in c:
                d = self.detour(c, e)
                if d is None:
                    bad += 1
                else:
                    ell = max(ell, d)
        out = {"name": self.name, "n": self.n, "m": len(self.E), "cells": len(self.cells), "L": L, "C2": c2,
               "C3_failures": bad, "ell": ell, "maxdeg": max(len(a) for a in self.adj)}
        if three_conn:
            out["3-connected"] = self.three_connected()
        return out

    def connected_without(self, removed):
        start = next(v for v in range(self.n) if v not in removed)
        seen = {start}; q = [start]
        while q:
            x = q.pop()
            for y, _ in self.adj[x]:
                if y not in removed and y not in seen:
                    seen.add(y); q.append(y)
        return len(seen) == self.n - len(removed)

    def three_connected(self):
        if self.n < 4: return False
        for a, b in combinations(range(self.n), 2):
            if not self.connected_without({a, b}):
                return False
        return True

def grid(a, b):
    V = lambda r, c: (r, c)
    edges = [(V(r, c), V(r, c + 1)) for r in range(a) for c in range(b - 1)] + [(V(r, c), V(r + 1, c)) for r in range(a - 1) for c in range(b)]
    cells = [[(V(r, c), V(r, c + 1)), (V(r + 1, c), V(r + 1, c + 1)), (V(r, c), V(r + 1, c)), (V(r, c + 1), V(r + 1, c + 1))]
             for r in range(a - 1) for c in range(b - 1)]
    return edges, cells

def triangulated_grid(a, b, rng):
    edges, squares = grid(a, b)
    cells = []
    edges = list(edges)
    for r in range(a - 1):
        for c in range(b - 1):
            p, q_, s, t = (r, c), (r, c + 1), (r + 1, c), (r + 1, c + 1)
            corner_bl = (r == 0 and c == 0); corner_tr = (r == a - 2 and c == b - 2)
            corner_br = (r == 0 and c == b - 2); corner_tl = (r == a - 2 and c == 0)
            if corner_bl or corner_tr:
                diag = (p, t)        # keeps the corner vertex at degree 3
            elif corner_br or corner_tl:
                diag = (q_, s)
            else:
                diag = (p, t) if rng.random() < 0.5 else (q_, s)
            edges.append(diag)
            if diag == (p, t):
                cells += [[(p, q_), (q_, t), (p, t)], [(p, s), (s, t), (p, t)]]
            else:
                cells += [[(p, q_), (p, s), (q_, s)], [(q_, t), (s, t), (q_, s)]]
    return edges, cells

def wall(r):
    """Elementary wall of height r: rows 0..r, columns 0..2r+1; vertical edges where x+y even; drop degree-1 corners;
    then suppress degree-2 vertices. Cells = bricks (after suppression)."""
    H = r; W = 2 * r + 1
    edges = set()
    for y in range(H + 1):
        for x in range(W):
            edges.add(norm((x, y), (x + 1, y)))
    for y in range(H):
        for x in range(W + 1):
            if (x + y) % 2 == 0:
                edges.add(norm((x, y), (x, y + 1)))
    # bricks: for each row y, bricks between consecutive vertical edges at x and x+2 with (x+y) even
    bricks = []
    for y in range(H):
        xs = [x for x in range(W + 1) if (x + y) % 2 == 0]
        for x0, x1 in zip(xs, xs[1:]):
            cyc = [norm((x0, y), (x0, y + 1)), norm((x1, y), (x1, y + 1))]
            cyc += [norm((x, y), (x + 1, y)) for x in range(x0, x1)]
            cyc += [norm((x, y + 1), (x + 1, y + 1)) for x in range(x0, x1)]
            bricks.append(cyc)
    # drop degree-1 vertices repeatedly
    while True:
        deg = {}
        for a, b in edges:
            deg[a] = deg.get(a, 0) + 1; deg[b] = deg.get(b, 0) + 1
        ones = {v for v, d in deg.items() if d == 1}
        if not ones: break
        edges = {e for e in edges if e[0] not in ones and e[1] not in ones}
    bricks = [[e for e in c] for c in bricks if all(e in edges for e in c)]
    # suppress degree-2 vertices: merge their two edges; track cells as cycles of merged edges
    return suppress(edges, bricks)

def suppress(edges, cells):
    """Suppress degree-2 vertices; edges become chains. Returns (edges, cells) on branch vertices."""
    adj = {}
    for a, b in edges:
        adj.setdefault(a, []).append(b); adj.setdefault(b, []).append(a)
    branch = {v for v, ns in adj.items() if len(ns) != 2}
    chain_of = {}       # original edge -> merged edge (pair of branch vertices)
    merged = set()
    for s in branch:
        for t in adj[s]:
            path = [s, t]
            while path[-1] not in branch:
                nxt = [w for w in adj[path[-1]] if w != path[-2]][0]
                path.append(nxt)
            me = norm(path[0], path[-1])
            merged.add(me)
            for a, b in zip(path, path[1:]):
                chain_of[norm(a, b)] = me
    newcells = []
    for c in cells:
        mc = sorted({chain_of[e] for e in c})
        newcells.append([tuple(e) for e in mc])
    return sorted(merged), newcells

def grid3(a, b, c):
    V = lambda x, y, z: (x, y, z)
    edges, cells = [], []
    for x, y, z in product(range(a), range(b), range(c)):
        for dx, dy, dz in ((1, 0, 0), (0, 1, 0), (0, 0, 1)):
            if x + dx < a and y + dy < b and z + dz < c:
                edges.append((V(x, y, z), V(x + dx, y + dy, z + dz)))
    for x, y, z in product(range(a), range(b), range(c)):
        for (d1, d2) in (((1, 0, 0), (0, 1, 0)), ((1, 0, 0), (0, 0, 1)), ((0, 1, 0), (0, 0, 1))):
            p = (x, y, z); q1 = tuple(p[i] + d1[i] for i in range(3)); q2 = tuple(p[i] + d2[i] for i in range(3))
            s = tuple(p[i] + d1[i] + d2[i] for i in range(3))
            if all(s[i] < (a, b, c)[i] for i in range(3)):
                cells.append([(p, q1), (p, q2), (q1, s), (q2, s)])
    return edges, cells

def _demo():
    import random
    rng = random.Random(1)
    out = []
    for a, b in ((4, 4), (5, 6), (8, 8)):
        out.append(Fam(f"grid{a}x{b}", *grid(a, b)).report(three_conn=(a * b <= 30)))
    for a, b in ((4, 4), (5, 6), (8, 8)):
        out.append(Fam(f"trigrid{a}x{b}", *triangulated_grid(a, b, rng)).report(three_conn=(a * b <= 30)))
    for r in (2, 3, 4, 5, 6, 8):
        out.append(Fam(f"wall{r}", *wall(r)).report(three_conn=(r <= 4)))
    for dims in ((2, 2, 2), (3, 3, 3), (3, 4, 5)):
        out.append(Fam("grid3d" + "x".join(map(str, dims)), *grid3(*dims)).report(three_conn=False))
    for o in out:
        print(o)
