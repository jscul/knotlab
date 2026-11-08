"""Rings of cuts on surfaces (GENUS-CUT-20261108-001A), on LATTICE-NET-20261108-001A's lattice_lib and LOOP-NET-20261108-001A's loopnet_lib.

A network's positions embed its ring graph G in an oriented surface; the faces of the embedding are the contact graph's closed routes
that change ring at every contact (loopnet_lib.faces). The dual graph G* has a vertex for each face and, for each contact, a dual edge
joining the faces that hold its two out-corners. A ring of cuts is a cycle of G*: cutting it freezes the contacts whose dual edges it
uses. Vectors over GF(2) are Python ints (bit e = contact e)."""
from __future__ import annotations

import itertools
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "proofs/LATTICE-NET-20261108-001A/LATTICE-NET-20261108-001A-P001_odd_tori_compose_rings_of_cuts_separate"))
import lattice_lib as T  # noqa: E402

LN = T.LN
N = T.N


def ring_index(rot):
    return {v: i for i, v in enumerate(sorted(rot, key=repr))}


def dual(sizes, contacts):
    """faces, genus, and the dual edge (face, face) of every contact"""
    fs, g = LN.faces(sizes, contacts)
    face_of = {(R, x): fi for fi, f in enumerate(fs) for (R, x, y, l) in f}
    return fs, g, [(face_of[(ra, c)], face_of[(rb, c)]) for c, (ra, pa, rb, pb, law) in enumerate(contacts)]


def components(nv, pairs):
    parent = list(range(nv))

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a
    for u, w in pairs:
        parent[find(u)] = find(w)
    return len({find(a) for a in range(nv)})


def graph_pieces(rot, edges, cut):
    ring = ring_index(rot)
    cut = set(cut)
    return components(len(ring), [(ring[u], ring[w]) for e, (u, w) in enumerate(edges) if e not in cut])


def native_pieces(sizes, contacts, rot, edges, cut):
    """the pieces of the relation 'an uncut contact on ring X needs ring Y' (exact walk counts), and how many uncut contacts need every ring"""
    ring = ring_index(rot)
    ins = T.in_sets(sizes, contacts, cut)
    rc = T.ring_contacts(rot, edges, ring)
    pairs, full, uncut = [], 0, [c for c in range(len(contacts)) if c not in set(cut)]
    for c in uncut:
        ra, pa, rb, pb, law = contacts[c]
        need = T.rings_needed(T.reach(ins, c)[0], rc, cut)
        full += need == set(rc)
        pairs += [(ra, y) for y in need] + [(rb, y) for y in need]
    return components(len(rc), pairs), full, len(uncut)


def rank(vectors):
    basis = {}
    for v in vectors:
        while v:
            top = v.bit_length() - 1
            if top not in basis:
                basis[top] = v
                break
            v ^= basis[top]
    return len(basis)


def cycle_space(nf, dual_edges, cut):
    """a basis of the cycle space of the dual subgraph on the cut contacts' dual edges (fundamental cycles of a spanning forest)"""
    parent, tree, adj = list(range(nf)), [], {}

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a
    extra = []
    for e in cut:
        f1, f2 = dual_edges[e]
        if find(f1) != find(f2):
            parent[find(f1)] = find(f2)
            tree.append(e)
            adj.setdefault(f1, []).append((f2, e))
            adj.setdefault(f2, []).append((f1, e))
        else:
            extra.append(e)

    def path(a, b):
        prev, todo = {a: None}, [a]
        while todo:
            x = todo.pop()
            if x == b:
                break
            for y, e in adj.get(x, []):
                if y not in prev:
                    prev[y] = (x, e)
                    todo.append(y)
        vec, x = 0, b
        while prev[x] is not None:
            x, e = prev[x]
            vec ^= 1 << e
        return vec
    return [(1 << e) ^ (path(*dual_edges[e]) if dual_edges[e][0] != dual_edges[e][1] else 0) for e in extra]


def boundaries(rot, edges):
    """the boundaries of the dual faces: for each ring, the vector of its contacts (a contact joining a ring to itself would cancel)"""
    ring = ring_index(rot)
    out = {}
    for e, (u, w) in enumerate(edges):
        for v in (u, w):
            out[ring[v]] = out.get(ring[v], 0) ^ (1 << e)
    return list(out.values())


def homology_rank(nf, dual_edges, cut, bnd):
    """(dimension of the cut's dual cycle space, dimension of its image in the surface's homology mod 2)"""
    Z = cycle_space(nf, dual_edges, cut)
    rb = rank(bnd)
    return len(Z), rank(Z + bnd) - rb


def tree_cotree(rot, edges, dual_edges, nf, rng):
    """a spanning tree T of the ring graph, a spanning tree of the dual on the other contacts, the 2g left over, and their fundamental
    dual cycles (as contact vectors)"""
    ring = ring_index(rot)
    order = list(range(len(edges)))
    rng.shuffle(order)
    parent = list(range(len(ring)))

    def find(p, a):
        while p[a] != a:
            p[a] = p[p[a]]
            a = p[a]
        return a
    Tset = set()
    for e in order:
        u, w = ring[edges[e][0]], ring[edges[e][1]]
        if find(parent, u) != find(parent, w):
            parent[find(parent, u)] = find(parent, w)
            Tset.add(e)
    rest = [e for e in order if e not in Tset]
    parent2, Tstar = list(range(nf)), []
    for e in rest:
        f1, f2 = dual_edges[e]
        if find(parent2, f1) != find(parent2, f2):
            parent2[find(parent2, f1)] = find(parent2, f2)
            Tstar.append(e)
    X = [e for e in rest if e not in set(Tstar)]
    cycles = cycle_space(nf, dual_edges, Tstar + X)
    return Tset, Tstar, X, cycles


# ---------- networks
def gl23_maps():
    """orientably regular maps from GL(2,3): darts are the 48 matrices, a vertex is a coset g<x>, an edge {g, gy}; returns
    {(vertex degree, face degree): (rot, edges)} for the first generating pair of each type"""
    G = [m for m in itertools.product(range(3), repeat=4) if (m[0] * m[3] - m[1] * m[2]) % 3]
    one = (1, 0, 0, 1)

    def mul(a, b):
        return ((a[0] * b[0] + a[1] * b[2]) % 3, (a[0] * b[1] + a[1] * b[3]) % 3, (a[2] * b[0] + a[3] * b[2]) % 3, (a[2] * b[1] + a[3] * b[3]) % 3)

    def order(m):
        k, p = 1, m
        while p != one:
            p, k = mul(p, m), k + 1
        return k

    def generated(gens):
        S, todo = {one}, [one]
        while todo:
            a = todo.pop()
            for g in gens:
                b = mul(a, g)
                if b not in S:
                    S.add(b)
                    todo.append(b)
        return S
    out = {}
    for x in G:
        for y in G:
            if order(y) != 2:
                continue
            key = (order(x), order(mul(x, y)))
            if key in out or len(generated([x, y])) != 48:
                continue
            vert = {}
            for g in G:
                if g not in vert:
                    h = g
                    while True:
                        vert[h] = g
                        h = mul(h, x)
                        if h == g:
                            break
            edge_of, edges = {}, []
            for g in G:
                if g not in edge_of:
                    gy = mul(g, y)
                    edge_of[g] = edge_of[gy] = len(edges)
                    edges.append((vert[g], vert[gy]))
            rot = {}
            for g in G:
                if vert[g] not in rot:
                    cyc, h = [], g
                    while True:
                        cyc.append(edge_of[h])
                        h = mul(h, x)
                        if h == g:
                            break
                    rot[vert[g]] = cyc
            out[key] = (rot, edges)
    return out


def double_torus(n, length):
    """two copies of the n x n square torus lattice cross-glued along a vertical slit of `length` horizontal contacts h(0, j),
    j < length: a double cover of the torus branched at the two faces at the slit's ends, of genus 2"""
    slit = {(0, j) for j in range(length)}
    s = lambda p: 1 if (p[0] % n, p[1] % n) in slit else 0
    edges, H, V = [], {}, {}
    for c in (0, 1):
        for i in range(n):
            for j in range(n):
                H[(c, (i, j))] = len(edges)
                edges.append(((c, (i, j)), (c ^ s((i, j)), ((i + 1) % n, j))))
                V[(c, (i, j))] = len(edges)
                edges.append(((c, (i, j)), (c, (i, (j + 1) % n))))
    rot = {}
    for c in (0, 1):
        for i in range(n):
            for j in range(n):
                w = ((i - 1) % n, j)
                rot[(c, (i, j))] = [H[(c, (i, j))], V[(c, (i, j))], H[(c ^ s(w), w)], V[(c, (i, (j - 1) % n))]]
    return rot, edges
