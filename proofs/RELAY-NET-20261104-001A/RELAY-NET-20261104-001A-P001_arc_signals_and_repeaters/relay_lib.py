"""Relay networks, for RELAY-NET-20261104-001.

A network is a tree of plane pieces (plane cubic bipartite graphs) joined through 3-edge cuts by families_lib.graph_splice: each splice
deletes a vertex of each side, of opposite roles. The side that loses a point receives at that cut (it is split there); the side that
loses a line emits. An opened Fano handle is attached at a point (strip_lib.halo_space) and creation is decided by the validated pipeline.

The signal at a cut: the part of the network upstream of the cut, with the cut's out-line restored (everything downstream collapses to it,
by the reduction lemma of STRIP-RELAY-20261103-001A), and the set of out-line patterns that each pinned pair of handle points leaves: one
pattern (single), two with two points fixed (arc), or more (lost)."""
import collections
import itertools
import sys
from pathlib import Path

import networkx as nx

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "proofs/STRIP-RELAY-20261103-001A/STRIP-RELAY-20261103-001A-P001_heights_and_reduction"))
sys.path.insert(0, str(ROOT / "proofs/SPLICE-TREE-20261102-001C/SPLICE-TREE-20261102-001C-P001_opened_cuts_interact"))
import strip_lib as SL  # noqa: E402
import elim_lib as E  # noqa: E402

PL, FL, HP, CL, G, TL, J = SL.PL, SL.FL, SL.HP, SL.CL, SL.G, SL.TL, SL.HP.J
PIECES = {"cube": lambda: FL.octahedral(0), "prism3": lambda: PL.prism(3), "prism4": lambda: PL.prism(4), "strip": lambda: PL.prism(6),
          "grid16": lambda: FL.octahedral(1), "grid64": lambda: FL.octahedral(2), "tube": lambda: FL.tube(4, 1)}


class Net:
    """pieces[name] is a plane cubic bipartite graph; role[name][node] is 'point' or 'line'; C is the spliced graph on (name, node)"""

    def __init__(self, g0, name0, role0=None):
        self.pieces = {name0: g0}
        c = nx.bipartite.color(g0)
        self.role = {name0: dict(role0) if role0 else {v: ("point" if c[v] == 0 else "line") for v in g0}}
        self.C = nx.relabel_nodes(g0, {v: (name0, v) for v in g0})
        self.cuts = []

    def present(self, name, role):
        return sorted(v for v in self.pieces[name] if self.role[name][v] == role and (name, v) in self.C)

    def attach(self, old, vold, new, gnew, vnew):
        r_old = self.role[old][vold]
        cn = nx.bipartite.color(gnew)
        r_new = "line" if r_old == "point" else "point"
        self.role[new] = {v: (r_new if cn[v] == cn[vnew] else r_old) for v in gnew}
        self.pieces[new] = gnew
        h = FL.graph_splice(self.C, (old, vold), gnew, vnew)
        assert h is not None
        org = nx.get_node_attributes(h, "origin")
        self.C = nx.relabel_nodes(h, {v: (x if side == 0 else (new, x)) for v, (side, x) in org.items()})
        self.cuts.append(((old, vold, r_old), (new, vnew, r_new)))

    def space(self):
        col = nx.bipartite.color(self.C)
        ref = next(iter(self.C))
        swap = (col[ref] == 0) != (self.role[ref[0]][ref[1]] == "point")
        return SL.labelled(self.C, swap=swap)


def far_halo(net, z, lines_by_piece=False):
    """creation beyond distance 3 from an opened Fano handle at point z (pipeline, four census far sides): number of creating lines by
    piece"""
    (H2, s2, n2), pts, lns = net.space()
    hs = SL.halo_space(H2, s2, n2, z, (0, 1, 2))
    gm = nx.Graph()
    gm.add_edges_from((("p", q), ("l", kk)) for kk, L in enumerate(hs.lines) for q in L)
    dist = nx.multi_source_dijkstra_path_length(gm, [("p", q) for q in range(hs.nF)] + [("l", kk) for kk in range(hs.nh)])
    Hands = [hs.handle(M) for M in range(hs.nh)]
    out = collections.Counter()
    for L in range(hs.nh, len(hs.lines)):
        if dist[("l", L)] <= 3:
            continue
        R = hs.transfer(L)
        if any(HP.creates(hs, M, L, F, Hands[M], R) for M in range(hs.nh) for fname, F in SL.FARS):
            out[lns[hs.qline[L]][0]] += 1
    return out


def arc_lemma(H, s, n, z):
    """for every line other than the port lines and every arc signal (ports a, b fixed and disagreeing, c free): is the line frozen, and
    does it have a corner on the own arc between a and b?"""
    g = CL.Geometry(H, s, n, z)
    Q = g.Q
    out = collections.Counter()
    allowed = [w for w in itertools.product((0, 1), repeat=3) if g.port_class(w) is not None]
    for j in range(len(H)):
        if j in g.through:
            continue
        img = collections.defaultdict(set)
        for w, t in Q.transfer(j):
            img[w].add(t)
        for a, b in itertools.combinations(range(3), 2):
            on_arc = g.face_of_arc[(a, b)] in g.lfaces[j]
            for va in (0, 1):
                S = [w for w in allowed if w[a] == va and g.port_class(w) in (a, b)]
                T = set().union(*[img[w] for w in S])
                kind = "frozen" if CL.frozen_form(T) else ("one pattern" if len(T) == 1 else "%d patterns" % len(T))
                out[("near" if j not in g.beyond else "beyond", "on the arc" if on_arc else "off the arc", kind)] += 1
    return out


def chain(kind, d, pick, m=3, start=0, adjacent=False, first="grid16", ring="strip"):
    """grid1 <- c1 <- ... <- cm <- ring: each station loses a line towards grid1 (its first node) and a point towards the ring, at
    distance d from it (pick-th such point; adjacent: the nearest). With start = i > 0, only pieces c_i .. ring are built, c_i closed (its
    out-line present). Returns (network, names from grid1 to the ring, the out-line of the first piece built)."""
    gs = [PIECES[first]()] + [PIECES[kind]() for _ in range(m)]
    names = ["grid1"] + ["c%d" % (i + 1) for i in range(m)]
    n0 = Net(gs[0], "grid1")
    vout = {"grid1": n0.present("grid1", "point")[0]}
    vin = {}
    for i in range(1, m + 1):
        g = gs[i]
        vin[names[i]] = sorted(g.nodes)[0]
        n0.attach(names[i - 1], vout[names[i - 1]], names[i], g, vin[names[i]])
        dist = nx.single_source_shortest_path_length(g, vin[names[i]])
        cands = n0.present(names[i], "point")
        if adjacent:
            cands = [x for x in cands if dist[x] == 1]
        else:
            cands = [x for x in cands if dist[x] == d]
        if not cands:
            return None, None, None
        vout[names[i]] = cands[pick % len(cands)]
    rg = PIECES[ring]()
    if start == 0:
        n0.attach(names[m], vout[names[m]], "ring", rg, sorted(rg.nodes)[0])
        return n0, names + ["ring"], None
    n = Net(gs[start], names[start], role0=n0.role[names[start]])
    for i in range(start + 1, m + 1):
        n.attach(names[i - 1], vout[names[i - 1]], names[i], gs[i], vin[names[i]])
    n.attach(names[m], vout[names[m]], "ring", rg, sorted(rg.nodes)[0])
    return n, names[start:] + ["ring"], vin[names[start]]


def signal(kind, d, pick, start, ring_point, m=3):
    """the signal leaving c_start towards grid1, for the handle at ring_point (a (piece, node) pair)"""
    n, names, out_line = chain(kind, d, pick, m=m, start=start)
    (H2, s2, n2), pts, lns = n.space()
    z = pts.index(ring_point)
    hs = SL.halo_space(H2, s2, n2, z, (0, 1, 2))
    L = next(L for L in range(hs.nh, len(hs.lines)) if lns[hs.qline[L]] == (names[0], out_line))
    img = collections.defaultdict(set)
    for w, t in hs.transfer(L):
        img[w].add(t)
    prof = collections.Counter()
    for M in range(hs.nh):
        rows = [(tuple(int(r[q]) for q in hs.ports), r) for r in hs.handle(M)]
        for p, a in itertools.combinations(hs.hpts, 2):
            if len({(int(r[p]), int(r[a])) for w, r in rows}) < 4:
                continue
            for pv, av in itertools.product((0, 1), repeat=2):
                P = {w for w, r in rows if int(r[p]) == pv and int(r[a]) == av}
                T = set().union(*[img[w] for w in P if w in img])
                prof["single" if len(T) == 1 else ("arc" if CL.frozen_form(T) else ("empty" if not T else "lost"))] += 1
    return prof


def hub(hub_kind, recv_kind, ring_kind, hi=0, ri=(0, 1), via_strips=False, near=False):
    """a hub piece receiving from a ring at a point and emitting into two receivers at lines (directly, or through strips); the lines
    are the ri-th present ones, or (near) the two nearest the receiving point"""
    n = Net(PIECES[hub_kind](), "hub")
    h0 = n.present("hub", "point")[hi]
    rg = PIECES[ring_kind]()
    n.attach("hub", h0, "ring", rg, sorted(rg.nodes)[0])
    dh = nx.single_source_shortest_path_length(n.pieces["hub"], h0)
    for gname, idx in zip(("A", "B"), ri):
        lns_ = n.present("hub", "line")
        h = min(lns_, key=lambda v: (dh[v], v)) if near else lns_[idx % len(lns_)]
        if via_strips:
            st = PL.prism(6)
            sname = "strip to " + gname
            s_in = sorted(st.nodes)[0]
            n.attach("hub", h, sname, st, s_in)
            dist = nx.single_source_shortest_path_length(st, s_in)
            s_out = max(n.present(sname, "line"), key=lambda v: (dist[v], -v))
            gr = PIECES[recv_kind]()
            n.attach(sname, s_out, gname, gr, sorted(gr.nodes)[0])
        else:
            gr = PIECES[recv_kind]()
            n.attach("hub", h, gname, gr, sorted(gr.nodes)[0])
    return n


def exact_vs_pipeline(net, z, M, parts=None):
    """exact creation (join method) against the pipeline at every gluing line showing six patterns, for removal M and the four far sides"""
    (H2, s2, n2), pts, lns = net.space()
    hs = SL.halo_space(H2, s2, n2, z, (0, 1, 2))
    AN = CL.solutions(hs.lines, hs.signs, hs.n, skip=M)
    Hand = hs.handle(M)
    out = collections.Counter()
    for L in range(hs.nh, len(hs.lines)):
        if len({tuple(int(b) for b in r) for r in AN[:, list(hs.lines[L])]}) != 6:
            continue
        piece = lns[hs.qline[L]][0]
        for fname, F in SL.FARS:
            exact = bool(J.new_knots(E, G, AN, hs.lines, hs.signs, hs.n, L, F, 3)[0])
            pipe = HP.creates(hs, M, L, F, Hand)
            out[(piece, "exact %s, pipeline %s" % (exact, pipe))] += 1
    return out


def small_chain(first, station, m, d, pick, ring_kind):
    """c0 <- c1 <- ... <- cm <- ring of small pieces (as `chain`, with any first piece)"""
    n = Net(PIECES[first](), "c0")
    cur, v = "c0", n.present("c0", "point")[0]
    names = ["c0"]
    for i in range(m):
        g = PIECES[station]()
        name = "c%d" % (i + 1)
        vin = sorted(g.nodes)[0]
        n.attach(cur, v, name, g, vin)
        dist = nx.single_source_shortest_path_length(g, vin)
        cands = [x for x in n.present(name, "point") if dist[x] == d]
        if not cands:
            return None, None
        v = cands[pick % len(cands)]
        cur = name
        names.append(name)
    rg = PIECES[ring_kind]()
    n.attach(cur, v, "ring", rg, sorted(rg.nodes)[0])
    return n, names + ["ring"]


def two_cut(a, b, c, va=0, vb=0):
    """c0 <- c1 <- c2 (the handle's piece), c1's two cut vertices as far apart as possible (vb-th choice)"""
    n = Net(PIECES[a](), "c0")
    v = n.present("c0", "point")[va]
    g = PIECES[b]()
    vin = sorted(g.nodes)[0]
    n.attach("c0", v, "c1", g, vin)
    dist = nx.single_source_shortest_path_length(g, vin)
    cands = sorted(n.present("c1", "point"), key=lambda x: -dist[x])
    v2 = cands[min(vb, len(cands) - 1)]
    g2 = PIECES[c]()
    n.attach("c1", v2, "c2", g2, sorted(g2.nodes)[0])
    return n, ["c0", "c1", "c2"]


def exact_far(net, z, M):
    """exact creation against the pipeline at every gluing line beyond distance 3 that shows six patterns"""
    (H2, s2, n2), pts, lns = net.space()
    hs = SL.halo_space(H2, s2, n2, z, (0, 1, 2))
    gm = nx.Graph()
    gm.add_edges_from((("p", q), ("l", kk)) for kk, L in enumerate(hs.lines) for q in L)
    dist = nx.multi_source_dijkstra_path_length(gm, [("p", q) for q in range(hs.nF)] + [("l", kk) for kk in range(hs.nh)])
    AN = CL.solutions(hs.lines, hs.signs, hs.n, skip=M)
    Hand = hs.handle(M)
    out = collections.Counter()
    for L in range(hs.nh, len(hs.lines)):
        if dist[("l", L)] <= 3 or len({tuple(int(b) for b in r) for r in AN[:, list(hs.lines[L])]}) != 6:
            continue
        piece = lns[hs.qline[L]][0]
        for fname, F in SL.FARS:
            exact = bool(J.new_knots(E, G, AN, hs.lines, hs.signs, hs.n, L, F, 3)[0])
            pipe = HP.creates(hs, M, L, F, Hand)
            out[(piece, "exact %s, pipeline %s" % (exact, pipe))] += 1
    return out
