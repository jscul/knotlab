"""The census of handles, for FACE-CLAIM-20261103-001B.

A handle is a non-planar knot space H minus one of its lines li, attached at point z of a plane knot space (halo_pipeline.HaloSpace); the
order of li's points decides which port joins which line through z. On a ladder (the prism over a 20-cycle, z = 0) the third line through
z is the one whose far corner lies on the long face opposite z, so the port in position 2 is the 'bottom' port: the far lines of the
bottom face read the opposite face of that port, and the far lines of the top face read the own arc between the other two ports."""
import collections
import itertools
import sys
from pathlib import Path

import networkx as nx

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "proofs/HANDLE-EMERGENCE-20261102-001A/HANDLE-EMERGENCE-20261102-001A-P001_a_planar_removed_side_creates_nothing"))
sys.path.insert(0, str(ROOT / "proofs/HALO-FORCING-20261103-001C/HALO-FORCING-20261103-001C-P001_the_reach_on_ladders_and_grids"))
sys.path.insert(0, str(ROOT / "proofs/FACE-CLAIM-20261103-001A/FACE-CLAIM-20261103-001A-P001_the_reading_lemma_and_the_claim_rule"))
import planar_lib as PL  # noqa: E402
import halo_pipeline as HP  # noqa: E402
import claim_lib as CL  # noqa: E402

G, TL = PL.G, HP.TL
SP = {idx: (H, s, n) for idx, n, H, s in G.census_spaces(ROOT)}
FARS = [("K4^(3)", SP[1]), ("census 6", SP[6]), ("the Fano plane", SP[21]), ("census 58", SP[58])]
LADDER = PL.to_space(PL.prism(10))


def spaces():
    """the non-planar census spaces and every splice of the Fano plane with a planar census space, both ways, up to isomorphism of the
    incidence graph; returns [(name, (lines, signs, n), parts)] with parts[i] the origin of line i"""
    out = []
    for idx in sorted(SP):
        if not PL.incidence_planar(SP[idx][0]):
            H, s, n = SP[idx]
            out.append(("census %d" % idx, (H, s, n), ["atom"] * len(H)))
    HF, sF, nF = SP[21]
    for i in sorted(SP):
        H, s, n = SP[i]
        if not PL.incidence_planar(H):
            continue
        for zs in range(n):
            ls, ss, nn, side, ports = G.splice(HF, sF, nF, 0, H, s, n, zs)
            npl = sum(1 for L in H if zs not in L)
            out.append(("Fano minus a line into census %d at point %d" % (i, zs), (ls, ss, nn), ["Fano"] * 6 + ["glue"] * npl + ["cut"] * 3))
        for l in range(len(H)):
            ls, ss, nn, side, ports = G.splice(H, s, n, l, HF, sF, nF, 0)
            nfo = sum(1 for L in HF if 0 not in L)
            out.append(("census %d minus line %d into the Fano plane at point 0" % (i, l), (ls, ss, nn),
                        ["glue"] * (len(H) - 1) + ["Fano"] * nfo + ["cut"] * 3))
    keep, graphs = [], []
    for name, (H, s, n), parts in out:
        g = nx.Graph()
        g.add_edges_from((("p", q), ("l", k)) for k, L in enumerate(H) for q in L)
        for v in g.nodes:
            g.nodes[v]["t"] = v[0]
        if any(nx.is_isomorphic(g, h, node_match=lambda a, b: a["t"] == b["t"]) for h in graphs):
            continue
        keep.append((name, ([tuple(L) for L in H], [list(x) for x in s], n), parts))
        graphs.append(g)
    return keep


def reorder(H, s, li, perm):
    H = [tuple(L) for L in H]
    s = [list(x) for x in s]
    L0, S0 = H[li], s[li]
    H[li] = tuple(L0[p] for p in perm)
    s[li] = [S0[p] for p in perm]
    return H, s


def port_rule(Hands, hpts, ports, allowed, c):
    """the claim rule in port terms, for the opposite face of the port in position c and the own arc between the other two:
    opposite used iff a pair pins one pattern, of class c, and each single point allows both disagreeing values of the other two ports;
    own used iff a pair pins patterns of the other classes with the first of the other ports fixed, and each single allows both class-c
    patterns"""
    e = min(set(itertools.product((0, 1), repeat=3)) - set(allowed))

    def cls(w):
        d = [x ^ y for x, y in zip(w, e)]
        return d.index(1) if sum(d) == 1 else d.index(0)
    a, b = [i for i in range(3) if i != c]
    disagree = {(w[a], w[b]) for w in allowed if cls(w) != c}
    classc = {w for w in allowed if cls(w) == c}
    used = {"opposite": False, "own": False}
    for Hand in Hands:
        rows = [(tuple(int(r[q]) for q in ports), r) for r in Hand]
        for p, q in itertools.combinations(hpts, 2):
            if len({(int(r[p]), int(r[q])) for w, r in rows}) < 4:
                continue
            for pv, qv in itertools.product((0, 1), repeat=2):
                P = {w for w, r in rows if int(r[p]) == pv and int(r[q]) == qv} & set(allowed)
                if not P:
                    continue
                singles = [{w for w, r in rows if int(r[x]) == xv} & set(allowed) for x, xv in ((p, pv), (q, qv))]
                if len(P) == 1 and cls(next(iter(P))) == c:
                    if all({(w[a], w[b]) for w in S if cls(w) != c} >= disagree for S in singles):
                        used["opposite"] = True
                if all(cls(w) != c for w in P) and len({w[a] for w in P}) == 1:
                    if all(S >= classc for S in singles):
                        used["own"] = True
    return used


def ladder_case(args):
    """one handle (space, line li, port order) on the ladder: the pipeline's far halo by face, the claim rule at one far line of each
    face, and the port form of the rule"""
    name, (H, s, n), li, perm = args
    H, s = reorder(H, s, li, perm)
    H2, s2, n2 = LADDER
    hs = HP.HaloSpace(H, s, li, H2, s2, n2, 0, G)
    g = nx.Graph()
    g.add_edges_from((("p", q), ("l", k)) for k, L in enumerate(hs.lines) for q in L)
    dist = nx.multi_source_dijkstra_path_length(g, [("p", q) for q in range(hs.nF)] + [("l", k) for k in range(hs.nh)])
    geo = CL.Geometry(H2, s2, n2, 0)
    bottom = geo.opp[2]
    far = [L for L in range(hs.nh, len(hs.lines)) if dist[("l", L)] > 3]
    on_bottom = [L for L in far if bottom in geo.lfaces[hs.qline[L]]]
    on_top = [L for L in far if geo.lfaces[hs.qline[L]] & geo.own[0] & geo.own[1]]
    Hands = [hs.handle(M) for M in range(hs.nh)]
    R = {L: hs.transfer(L) for L in far}
    halo = {L for L in far if any(HP.creates(hs, M, L, F, Hands[M], R[L]) for M in range(hs.nh) for fname, F in FARS)}
    rule = {face: any(CL.claim_rule_at(hs, Ls[0], R[Ls[0]], Hands[M]) is True for M in range(hs.nh))
            for face, Ls in (("opposite", on_bottom), ("own", on_top))}
    allowed = sorted({w for (w, t) in R[far[0]]})
    pr = port_rule(Hands, hs.hpts, hs.ports, allowed, 2)
    return {"name": name, "li": li, "perm": list(perm), "far lines": len(far), "on bottom": len(on_bottom), "on top": len(on_top),
            "halo bottom": len(halo & set(on_bottom)), "halo top": len(halo & set(on_top)), "halo other": len(halo - set(on_bottom) - set(on_top)),
            "rule": rule, "port rule": pr}
