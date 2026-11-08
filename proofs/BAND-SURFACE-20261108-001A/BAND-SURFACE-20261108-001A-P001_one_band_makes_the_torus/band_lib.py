"""Bands on a loop of rings (BAND-SURFACE-20261108-001A), on GROW-NET-20261108-001A's grow_lib.

A loop of n rings is GROW-NET's dihedron; a band is a second loop of n rings, ring (i, 1) joined to its partner (i, 0) by one contact
(single rungs) or two (double rungs). A rotation system says where each new contact sits in its rings' cyclic orders. The n x 2 torus is
the double-rung band with every ring listing E, N, W, S counterclockwise."""
from __future__ import annotations

import itertools
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "proofs/GROW-NET-20261108-001A/GROW-NET-20261108-001A-P001_bands_grow_single_rings_do_not"))
import grow_lib as G  # noqa: E402

LN = G.LN


def loop_and_band(n, double):
    """the contacts at each ring, unordered, and the edges: rows 0 and 1 are loops; rungs join (i, 0) and (i, 1)"""
    edges, inc = [], {(i, r): [] for i in range(n) for r in (0, 1)}
    for r in (0, 1):
        for i in range(n):
            e = len(edges)
            edges.append(((i, r), ((i + 1) % n, r)))
            inc[(i, r)].append(e)
            inc[((i + 1) % n, r)].append(e)
    for i in range(n):
        for _ in range(2 if double else 1):
            e = len(edges)
            edges.append(((i, 0), (i, 1)))
            inc[(i, 0)].append(e)
            inc[(i, 1)].append(e)
    return inc, edges


def rotations(inc):
    verts = sorted(inc)
    opts = [[[inc[v][0]] + list(p) for p in itertools.permutations(inc[v][1:])] for v in verts]
    for choice in itertools.product(*opts):
        yield {v: list(c) for v, c in zip(verts, choice)}


def genus_and_faces(rot, edges):
    sizes, contacts = LN.network(rot, edges, 2)
    fs, g = LN.faces(sizes, contacts)
    return g, sorted(len(f) for f in fs)
