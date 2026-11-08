"""Growing networks of rings (GROW-NET-20261108-001A), on GENUS-CUT-20261108-001A's genus_lib and LOOP-NET-20261108-001A's loopnet_lib.

A network is a rotation system rot = {ring: [contact ids in cyclic order]} with edges = [(ring, ring)] per contact, read with equally
spaced contacts, so that every corner has the same weight and a contact persists exactly when every count of returns to it is even
(LOOP-NET-20261108-001A, Theorem 2). Vectors over GF(2) are Python ints."""
from __future__ import annotations

import itertools
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "proofs/GENUS-CUT-20261108-001A/GENUS-CUT-20261108-001A-P001_two_rings_of_cuts_per_handle"))
import genus_lib as Gl  # noqa: E402

LN = Gl.LN


def out_sets(rot, nedges):
    """for each contact, the contacts its out-corners lead to, mod 2 (two corners to the same contact cancel)"""
    out = [0] * nedges
    for v, lst in rot.items():
        m = len(lst)
        for i in range(m):
            out[lst[i]] ^= 1 << lst[(i + 1) % m]
    return out


def odd_contacts(rot, nedges, first_only=False):
    """contacts with some odd return count, exact: for each contact c the vectors A^k e_c, k >= 1, are followed until the next lies in the
    span of the earlier ones; each later vector is a sum of these, so bit c stays 0 if it is 0 on them"""
    out = out_sets(rot, nedges)

    def step(v):
        nxt = 0
        while v:
            low = v & -v
            nxt ^= out[low.bit_length() - 1]
            v ^= low
        return nxt
    bad = []
    for c in range(nedges):
        v, basis = step(1 << c), {}
        while v:
            if v >> c & 1:
                bad.append(c)
                break
            x = v
            while x:
                top = x.bit_length() - 1
                if top not in basis:
                    break
                x ^= basis[top]
            if not x:
                break
            basis[x.bit_length() - 1] = x
            v = step(v)
        if bad and first_only:
            return bad
    return bad


def balanced(rot, nedges):
    return not odd_contacts(rot, nedges, first_only=True)


def reaches(rot, nedges, src, dst):
    """some walk length from src to dst has an odd count (the contact graph mod 2)"""
    out = out_sets(rot, nedges)
    v, basis = 1 << src, {}
    while v:
        if v >> dst & 1:
            return True
        x = v
        while x:
            top = x.bit_length() - 1
            if top not in basis:
                break
            x ^= basis[top]
        if not x:
            return False
        basis[x.bit_length() - 1] = x
        nxt, y = 0, v
        while y:
            low = y & -y
            nxt ^= out[low.bit_length() - 1]
            y ^= low
        v = nxt
    return False


def attachments(rot, edges, m):
    """every way to attach a new ring 'new' by m contacts: the rings it touches (with repetition), where each new contact is inserted in
    the touched ring's cyclic order (after its position-th contact, the contacts inserted one after another), and the new ring's order"""
    verts = sorted(rot, key=repr)
    for targets in itertools.combinations_with_replacement(verts, m):
        per = sorted(Counter(targets).items(), key=lambda t: repr(t[0]))
        slot_choices = [[(v, s) for s in itertools.product(range(len(rot[v])), repeat=k)] for v, k in per]
        for slots in itertools.product(*slot_choices):
            for order in itertools.permutations(range(1, m)):
                new_rot = {v: list(l) for v, l in rot.items()}
                new_edges = list(edges)
                ids = []
                for (v, s) in slots:
                    for pos in s:
                        e = len(new_edges)
                        new_edges.append((v, "new"))
                        ids.append(e)
                        lst = new_rot[v]
                        lst.insert((pos % len(lst)) + 1, e)
                new_rot["new"] = [ids[0]] + [ids[i] for i in order]
                yield new_rot, new_edges


def bubble(rot, edges, ring, pos):
    """attach a new two-contact ring to `ring` at two consecutive places, after its pos-th contact p and before the next contact q;
    returns the network and (p, q)"""
    new_rot = {v: list(l) for v, l in rot.items()}
    lst = new_rot[ring]
    p, q = lst[pos], lst[(pos + 1) % len(lst)]
    c1, c2 = len(edges), len(edges) + 1
    lst.insert(pos + 1, c2)
    lst.insert(pos + 1, c1)
    new_rot["new"] = [c1, c2]
    return new_rot, list(edges) + [(ring, "new"), (ring, "new")], (p, q)


def rect_torus(n, m):
    dirs = ((1, 0), (0, 1), (-1, 0), (0, -1))
    verts = [(i, j) for i in range(n) for j in range(m)]
    edges, eid = [], {}
    for v in verts:
        for d in dirs[:2]:
            w = ((v[0] + d[0]) % n, (v[1] + d[1]) % m)
            eid[(v, d)] = eid[(w, (-d[0], -d[1]))] = len(edges)
            edges.append((v, w))
    return {v: [eid[(v, d)] for d in dirs] for v in verts}, edges


def half_turn(n, m, rot, edges, e):
    """the half-turn about the midpoint of contact e of the n x m torus, as a map automorphism (dart map), checked by loopnet_lib.flip's
    propagation, or None"""
    return LN.flip(rot, edges, e)


def platonic_graph(name):
    import networkx as nx
    G = {"tetrahedron": nx.complete_graph(4), "cube": nx.hypercube_graph(3), "octahedron": nx.octahedral_graph(),
         "dodecahedron": nx.dodecahedral_graph(), "icosahedron": nx.icosahedral_graph()}[name]
    return nx.convert_node_labels_to_integers(G)


def truncation(G):
    """every vertex of a plane graph replaced by a cycle of its edge ends"""
    import networkx as nx
    ok, emb = nx.check_planarity(G)
    T = nx.Graph()
    for u, v in G.edges():
        T.add_edge((u, v), (v, u))
    for v in G.nodes():
        nb = list(emb.neighbors_cw_order(v))
        for i in range(len(nb)):
            T.add_edge((v, nb[i]), (v, nb[(i + 1) % len(nb)]))
    return nx.convert_node_labels_to_integers(T)


def rectification(G):
    """the medial graph of a plane graph: a vertex per edge, joined when consecutive round a face"""
    import networkx as nx
    ok, emb = nx.check_planarity(G)
    M, seen = nx.Graph(), set()
    for u, v in G.edges():
        for a, b in ((u, v), (v, u)):
            if (a, b) in seen:
                continue
            f = emb.traverse_face(a, b)
            cyc = [frozenset((f[i], f[(i + 1) % len(f)])) for i in range(len(f))]
            for i in range(len(cyc)):
                M.add_edge(cyc[i], cyc[(i + 1) % len(cyc)])
            for i in range(len(f)):
                seen.add((f[i], f[(i + 1) % len(f)]))
    return nx.convert_node_labels_to_integers(M)
