"""Native paths in the knot's spaces (NATIVE-PATHS-20261101-001A): shared library.

A knot's space is a connected cubic system (lines of three distinct points, every point on three lines) on which not-all-equal fails.
Its incidence graph has a vertex ('l', i) per line and ('p', p) per point. A nontrivial k-edge cut splits the incidence graph into two
shores of more than one vertex each. For a shore S, a port is a point of S whose cut edge leaves S, and a slot is a line of S whose cut
edge leaves S; the shore's accepted relation lists (port colours..., slot values...) that extend to a colouring of S proper on every
line of S, a slot reading the given value in place of its missing point."""
import itertools
import sys
from pathlib import Path

import networkx as nx
from pysat.solvers import Minisat22

ROOT = Path(__file__).resolve().parents[3]
for d in ("THREEFOLD-SPACES-20261030-001A/THREEFOLD-SPACES-20261030-001A-P001_three_fold_spaces_are_built_from_the_fano_plane",
          "THREEFOLD-SPACES-20261030-001C/THREEFOLD-SPACES-20261030-001C-P001_odd_cycles_of_fano_planes",
          "THREEFOLD-GRAMMAR-20261030-001A/THREEFOLD-GRAMMAR-20261030-001A-P001_fano_leaves_and_planar_glue"):
    sys.path.insert(0, str(ROOT / "proofs" / d))
import threefold_lib as T  # noqa: E402
import cycles_lib as C  # noqa: E402
import grammar_lib as M  # noqa: E402

FANO = T.FANO


def chain(k):
    H = FANO
    for _ in range(k - 1):
        H = T.point_splice(H, T.npoints(H) - 1, FANO, FANO[0])
    return H


def star():
    return T.point_splice(T.point_splice(T.point_splice(FANO, 0, FANO, FANO[0]), 1, FANO, FANO[0]), 2, FANO, FANO[0])


def cycle(k):
    return C.cycle_of_blocks(k)[0]


def twisted_cube():
    return M.decorate(M.K4, M.kasteleyn_signing(M.K4))


def spaces():
    cyc3 = cycle(3)
    return {"Fano": FANO, "chain of 2": chain(2), "chain of 3": chain(3), "chain of 4": chain(4), "star of 4": star(),
            "cycle of 3 blocks": cyc3, "cycle of 5 blocks": cycle(5), "cycle of 7 blocks": cycle(7),
            "twisted cube": twisted_cube(), "3-cycle spliced into Fano": T.point_splice(FANO, 0, cyc3, cyc3[0])}


def incidence_graph(H):
    g = nx.Graph()
    g.add_edges_from((("l", i), ("p", p)) for i, L in enumerate(H) for p in L)
    return g


def nontrivial_cuts(H, k):
    """all edge sets of size k that are exactly the edges between two shores of more than one vertex each (removal leaves two
    components and every removed edge joins them)"""
    g = incidence_graph(H)
    E = list(g.edges())
    out = []
    for cut in itertools.combinations(E, k):
        h = g.copy()
        h.remove_edges_from(cut)
        comps = list(nx.connected_components(h))
        if len(comps) == 2 and min(map(len, comps)) > 1 and all((a in comps[0]) != (b in comps[0]) for a, b in cut):
            out.append((cut, comps))
    return out


def shore_data(H, cut, S):
    """(points, lines, ports, slots) of shore S: ports are points of S with a cut edge, slots are (line, missing point) of S's lines"""
    points = sorted(v[1] for v in S if v[0] == "p")
    lines = sorted(v[1] for v in S if v[0] == "l")
    ports, slots = [], []
    for a, b in cut:
        l, p = (a, b) if a[0] == "l" else (b, a)
        if p in S:
            ports.append(p[1])
        else:
            slots.append((l[1], p[1]))
    return points, lines, ports, slots


def accepted(H, points, lines, ports, slots, override=None):
    """accepted (port colours..., slot values...) of a shore under not-all-equal, by one SAT call per channel assignment"""
    idx = {p: i + 1 for i, p in enumerate(points)}
    nv = len(points)
    svar = {}
    for s in slots:
        nv += 1
        svar[s] = nv
    clauses = []
    for li in lines:
        lits = [svar[(li, p)] if (li, p) in svar else idx[p] for p in H[li]]
        clauses += [lits, [-x for x in lits]]
    chan = [idx[p] for p in ports] + [svar[s] for s in slots]
    out = set()
    for vals in itertools.product((0, 1), repeat=len(chan)):
        with Minisat22(bootstrap_with=clauses + [[v if b else -v] for v, b in zip(chan, vals)]) as S:
            if S.solve():
                out.add(vals)
    return frozenset(out)


def atom_relation(H, edge):
    """cut one incidence (line, point): accepted (point colour, value the line reads) of the rest of H"""
    (a, b) = edge
    l, p = (a, b) if a[0] == "l" else (b, a)
    points = sorted({q for L in H for q in L})
    return accepted(H, points, list(range(len(H))), [p[1]], [(l[1], p[1])])


def colourable(H):
    return T.colourable_sat(H)


def crossing(cuts_shores, V):
    return sum(1 for X, Y in itertools.combinations(cuts_shores, 2) if X & Y and X - Y and Y - X and V - (X | Y))
