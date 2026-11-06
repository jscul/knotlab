"""The frozen region of a port class, for FACE-CLAIM-20261103-001C.

For a port pattern w of class k, a gluing line is frozen when w fixes two of its points, so that it shows two patterns. The reading lemma
(ticket A) freezes every line with a corner on a face barred by k. Two-sided unit propagation extends this: start from the class's seeds
(port k's line takes its far corner, the own arcs at port k carry no skip), and repeatedly match a line or face with one corner left and
block the other corners of a matched line or face. A line's claim types: the port patterns under which it can claim the face of its frozen
corner, at each of the two fixed values."""
import collections
import itertools
import sys
from pathlib import Path

import networkx as nx

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "proofs/FACE-CLAIM-20261103-001A/FACE-CLAIM-20261103-001A-P001_the_reading_lemma_and_the_claim_rule"))
import claim_lib as CL  # noqa: E402


def propagate(g, k):
    """points whose values unit propagation fixes relative to the ports, for class k (g: claim_lib.Geometry); None on a contradiction"""
    Q = g.Q
    ofi = [fi for (kk, fi, p, q) in g.corners]
    st = [None] * len(Q.edges)
    for ci, ((kk, f, p, q), (k2, fi, p2, q2)) in enumerate(zip(Q.edges, g.corners)):
        if fi in g.arc and k in g.arc[fi]:
            st[ci] = False
        if kk == g.through[k]:
            st[ci] = g.z not in (p2, q2)
    byline, byface = collections.defaultdict(list), collections.defaultdict(list)
    for ci, (kk, f, p, q) in enumerate(Q.edges):
        byline[kk].append(ci)
        byface[f].append(ci)
    changed = True
    while changed:
        changed = False
        for groups in (byline, byface):
            for key, cs in groups.items():
                m = [c for c in cs if st[c] is True]
                u = [c for c in cs if st[c] is None]
                if len(m) > 1:
                    return None
                if m:
                    for c in u:
                        st[c] = False
                        changed = True
                elif len(u) == 1:
                    st[u[0]] = True
                    changed = True
    gr = nx.Graph()
    gr.add_nodes_from(Q.points)
    for kk, cs in byline.items():
        if any(st[c] is True for c in cs):
            gr.add_edges_from(itertools.combinations(Q.lines[kk], 2))
    for ci, (kk, f, p, q) in enumerate(Q.edges):
        if st[ci] is not None:
            gr.add_edge(p, q)
    det = set()
    for y in Q.ports:
        det |= nx.node_connected_component(gr, y)
    return det


def frozen_lines(g, j):
    """for gluing line j: {port pattern: (y1, y2, b1, b2)} for the patterns that freeze it (two patterns, two points fixed), the transfer,
    and the image map"""
    R = g.Q.transfer(j)
    img = collections.defaultdict(set)
    for w, t in R:
        img[w].add(t)
    return {w: CL.frozen_form(T) for w, T in img.items() if CL.frozen_form(T)}, R, img


def claim_type(img, ff):
    """number of port patterns under which the line claims its frozen corner at each fixed value"""
    y1, y2, b1, b2 = ff
    C1 = {v for v, ts in img.items() if any(t[y1] == b1 and t[y2] != b2 for t in ts)}
    C2 = {v for v, ts in img.items() if any(t[y2] == b2 and t[y1] != b1 for t in ts)}
    return len(C1), len(C2)
