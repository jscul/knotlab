"""Heights and reduction across 3-edge cuts, for STRIP-RELAY-20261103-001A.

Plane pieces are built from plane cubic bipartite graphs by families_lib.graph_splice, which deletes a vertex of each of two graphs and
joins their neighbours through a 3-edge cut; each node keeps its origin (side, original node). A side of a cut that holds neither the
attachment point nor the gluing line acts on the cut as the vertex it lost (HANDLE-LOCALITY), so the reduced space is that side's own
original graph with the vertex restored. `compare` attaches the same handle at corresponding points of the spliced and the reduced spaces,
with each port on corresponding lines (the line across the cut corresponds to the restored vertex), and compares creation."""
import collections
import itertools
import sys
from pathlib import Path

import networkx as nx

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
for d in ["proofs/HANDLE-EMERGENCE-20261102-001A/HANDLE-EMERGENCE-20261102-001A-P001_a_planar_removed_side_creates_nothing",
          "proofs/HALO-FORCING-20261103-001C/HALO-FORCING-20261103-001C-P001_the_reach_on_ladders_and_grids",
          "proofs/PHASE-HALO-20261103-001A/PHASE-HALO-20261103-001A-P001_opposite_faces_carry_the_halo",
          "proofs/FACE-CLAIM-20261103-001A/FACE-CLAIM-20261103-001A-P001_the_reading_lemma_and_the_claim_rule"]:
    sys.path.insert(0, str(ROOT / d))
import planar_lib as PL  # noqa: E402
import halo_pipeline as HP  # noqa: E402
import families_lib as FL  # noqa: E402
import claim_lib as CL  # noqa: E402

G, TL = PL.G, HP.TL
SP = {idx: (H, s, n) for idx, n, H, s in G.census_spaces(ROOT)}
FARS = [("K4^(3)", SP[1]), ("census 6", SP[6]), ("the Fano plane", SP[21]), ("census 58", SP[58])]


def labelled(g, swap=False):
    """the knot space of a plane cubic bipartite graph with its node labels: (space, points (nodes), lines (nodes))"""
    col = nx.bipartite.color(g)
    pts = sorted(v for v in g if col[v] == (1 if swap else 0))
    lns = sorted(v for v in g if col[v] == (0 if swap else 1))
    return PL.to_space(g, swap=swap), pts, lns


def arm_on_grid(level, k, choice=0):
    """a ring (the prism over a 2k-cycle minus a vertex) spliced onto the dual of the octahedron subdivided `level` times"""
    gg, gp = FL.octahedral(level), PL.prism(k)
    cg, cp = nx.bipartite.color(gg), nx.bipartite.color(gp)
    v1 = [v for v in gg.nodes if cg[v] == 1][choice]
    v2 = next(v for v in gp.nodes if cp[v] != cg[v1])
    return gg, gp, v1, v2, FL.graph_splice(gg, v1, gp, v2)


def halo_space(H, s, n, z, li_order, handle=21, li=0):
    """the handle (census space minus line li, its points in li_order) attached at point z"""
    HF, sF, nF = SP[handle]
    HF = [tuple(L) for L in HF]
    sF = [list(x) for x in sF]
    HF[li] = tuple(HF[li][i] for i in li_order)
    sF[li] = [sF[li][i] for i in li_order]
    return HP.HaloSpace(HF, sF, li, H, s, n, z, G)


def compare(pieces, z, handle=21, li=0):
    """creation at every gluing line on z's side, in the spliced space and in z's reduced space, with aligned ports.
    pieces: (originals {side: graph}, removed {side: vertex}, spliced graph h)"""
    origs, removed, h = pieces
    (H2, s2, n2), pts, lns = labelled(h)
    org = nx.get_node_attributes(h, "origin")
    side, zn = org[pts[z]]
    g0 = origs[side]
    swap = zn not in labelled(g0)[1]
    (Hr, sr, nr), rpts, rlns = labelled(g0, swap=swap)
    zr = rpts.index(zn)
    rline = {v: j for j, v in enumerate(rlns)}
    # the lines through z in the spliced space, and their counterparts in the reduced space
    through = [k for k, L in enumerate(H2) if z in L]
    mates = []
    for k in through:
        s_, node = org[lns[k]]
        mates.append(rline[node] if s_ == side else rline[removed[side]])
    rthrough = [k for k, L in enumerate(Hr) if zr in L]
    assert sorted(mates) == sorted(rthrough)
    # port i joins through[i] in the spliced space; in the reduced space the port at position j must be the one joining mates^-1(rthrough[j])
    order = [mates.index(rthrough[j]) for j in range(3)]
    hs = halo_space(H2, s2, n2, z, (0, 1, 2), handle, li)
    hr = halo_space(Hr, sr, nr, zr, order, handle, li)
    assert [hr.ports[j] for j in range(3)] == [hs.ports[order[j]] for j in range(3)]
    gm = nx.Graph()
    gm.add_edges_from((("p", q), ("l", kk)) for kk, L in enumerate(hs.lines) for q in L)
    dist = nx.multi_source_dijkstra_path_length(gm, [("p", q) for q in range(hs.nF)] + [("l", kk) for kk in range(hs.nh)])
    Hm = [hs.handle(M) for M in range(hs.nh)]
    Hr_ = [hr.handle(M) for M in range(hr.nh)]
    rq = {j: L for L, j in hr.qline.items()}
    out = collections.Counter()
    for L in range(hs.nh, len(hs.lines)):
        s_, node = org[lns[hs.qline[L]]]
        if s_ != side:
            continue
        Lr = rq[rline[node]]
        Rm, Rr = hs.transfer(L), hr.transfer(Lr)
        for M in range(hs.nh):
            for fname, F in FARS:
                a = bool(HP.creates(hs, M, L, F, Hm[M], Rm))
                b = bool(HP.creates(hr, M, Lr, F, Hr_[M], Rr))
                band = "far" if dist[("l", L)] > 3 else "near"
                out["%s: spliced %s, reduced %s" % (band, a, b)] += 1
    return out


def frozen_by_heights(g, p):
    """for each port pattern w (of a class), whether p is frozen (one parity of its height difference to port 0 feasible) and whether, for
    that parity, the difference is fixed (halved range 0). g: claim_lib.Geometry"""
    Q = g.Q
    ports = Q.ports
    terms = ports + [p]
    D = TL.shortest(Q.graph(), terms)
    out = {}
    for w in itertools.product((0, 1), repeat=3):
        if g.port_class(w) is None:
            continue
        par = {ports[i]: (w[i] ^ w[0] ^ Q.x0[ports[i]] ^ Q.x0[ports[0]]) for i in range(3)}
        feas = []
        for b in (0, 1):
            pp = dict(par)
            pp[p] = b
            ok, dist = _halved(D, terms, pp)
            if ok:
                feas.append(dist[ports[0]][p] + dist[p][ports[0]])
        out[w] = (len(feas) == 1, len(feas) == 1 and feas[0] == 0)
    return out


def _halved(D, terms, par):
    W = {a: {b: (D[a][b] - par[b] + par[a]) // 2 for b in terms if b in D[a]} for a in terms}
    dist = {a: dict(W[a]) for a in terms}
    for a in terms:
        dist[a][a] = min(dist[a].get(a, 0), 0)
    for k in terms:
        for i in terms:
            if k not in dist[i]:
                continue
            for j in terms:
                if j in dist[k] and dist[i][k] + dist[k][j] < dist[i].get(j, 1 << 60):
                    dist[i][j] = dist[i][k] + dist[k][j]
    return all(dist[a][a] >= 0 for a in terms), dist


def dumbbell(mid, level1, level2, receive2=False):
    """grid1 -- mid -- grid2: mid (a prism, or another plane cubic bipartite graph) loses two vertices as far apart as possible, spliced
    into grid1 (split at a point: its cut vertices are lines) and into grid2 (its cut vertices are lines too if receive2, else points).
    Returns (spliced graph, part of each node, the removed vertex of grid1 and of grid2)."""
    g1, g2 = FL.octahedral(level1), FL.octahedral(level2)
    c1 = nx.bipartite.color(g1)
    v1 = next(v for v in g1.nodes if c1[v] == 1)
    cm = nx.bipartite.color(mid)
    a = next(v for v in mid.nodes if cm[v] != c1[v1])
    da = nx.single_source_shortest_path_length(mid, a)
    h1 = FL.graph_splice(g1, v1, mid, a)
    o1 = nx.get_node_attributes(h1, "origin")
    inv = {o: v for v, o in o1.items()}
    for d in sorted(set(da.values()), reverse=True):
        for b in sorted(v for v in mid.nodes if da[v] == d):
            bb = inv[(1, b)]
            ch = nx.bipartite.color(h1)
            c2 = nx.bipartite.color(g2)
            for v3 in sorted(g2.nodes):
                if c2[v3] == ch[bb]:
                    continue
                h = FL.graph_splice(h1, bb, g2, v3)
                if h is None:
                    continue
                col = nx.bipartite.color(h)
                o = nx.get_node_attributes(h, "origin")
                part = {v: ("grid2" if oo[0] == 1 else ("grid1" if o1[oo[1]][0] == 0 else "strip")) for v, oo in o.items()}
                r1 = {col[v] for v in h if part[v] == "grid1" for w in h[v] if part[w] == "strip"}
                r2 = {col[v] for v in h if part[v] == "grid2" for w in h[v] if part[w] == "strip"}
                if r1 == {1} and r2 == ({1} if receive2 else {0}):
                    return h, part, v1, v3
    return None, None, None, None
