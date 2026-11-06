"""Checks for PLAIN-BRACE-20261031-001B-P001 (counting on plain Pfaffian braces is #P-hard).

  0 dependency artifacts bound by the hashes recorded in manifest.json
  1 Hall's condition on examples: planar cubic bipartite graphs that are cyclically 4-edge-connected are braces; a graph with a cyclic
    3-edge cut is not
  2 the pieces, exhaustively: a site with k = 1, 2, 3 junctions is the ladder with 3k rungs, and every vertex set containing a cycle has at
    least four boundary edges (ports counted); the same for the cube junction; replacing a square of small planar braces by the cube
    junction gives braces
  3 weaving: a source with a 2-edge cut (not a brace), K3,3 and the Heawood graph, woven into prism and truncated-octahedron frames: hosts
    planar and cyclically 4-edge-connected, instances plain, cubic bipartite and certified Pfaffian; the smallest instance passes the
    direct brace test
  4 single-site interpolation inside a woven instance: the counts with 1, 3, 5, 7 junctions at one site give, by ticket A's formula, the
    count with that site restored
  5 the frame factor: #col of plain prisms is nonzero, and with every site restored the count is #col(source) #col(frame)
  6 controls: the source drawn without a frame keeps its 2-edge cut (host not cyclically 4-edge-connected, instance not a brace); an even
    number of junctions at one site leaves the host non-planar
Run: .venv/bin/python -B check.py [--write]   (networkx, numpy, sympy; about a minute)"""
import hashlib, itertools, json, os, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
P = lambda r: os.path.join(ROOT, "proofs", r)  # noqa: E731
for p in (P("THREEFOLD-AMPLITUDE-20261030-001A/THREEFOLD-AMPLITUDE-20261030-001A-P001_five_per_handle_tuttes_number_per_planar_piece"),
          P("THREEFOLD-AMPLITUDE-20261030-001B/THREEFOLD-AMPLITUDE-20261030-001B-P001_the_amplitude_by_computation"),
          P("TWIST-COUNT-20261030-001A/TWIST-COUNT-20261030-001A-P001_the_knots_junction_is_a_similitude"),
          P("SOFT-CROSS-20261031-001A/SOFT-CROSS-20261031-001A-P001_a_soft_crossing_interpolates_to_a_sharp_one"),
          P("PLAIN-COUNT-20261031-001A/PLAIN-COUNT-20261031-001A-P001_signs_interpolate_away"),
          P("PLAIN-COUNT-20261031-001B/PLAIN-COUNT-20261031-001B-P001_plain_pages_are_always_twisted"),
          P("PLAIN-BRACE-20261031-001A/PLAIN-BRACE-20261031-001A-P001_a_plain_crossing_inside_braces"), HERE):
    sys.path.insert(0, p)
import networkx as nx  # noqa: E402
import sympy as sp  # noqa: E402
import amplitude_lib as AM  # noqa: E402
import twist_lib as TW  # noqa: E402
import cross_lib as X  # noqa: E402
import computation_lib as CL  # noqa: E402
import plain_lib as PL  # noqa: E402
import page_lib as PG  # noqa: E402
import brace_lib as BL  # noqa: E402
import weave_lib as WV  # noqa: E402

T0 = time.time()
out, ok_all = {}, True
F_COEF = [sp.Rational(-53451621, 2804438), sp.Rational(521319, 200317), sp.Rational(-23524, 200317), sp.Rational(853, 2804438)]


def report(key, ok, detail):
    global ok_all
    out[key] = {"ok": bool(ok), "detail": detail}
    ok_all &= bool(ok)
    print(("PASS " if ok else "FAIL ") + key + ": " + json.dumps(detail, default=str)[:3000], flush=True)


def count(B):
    return AM.count(*B.system())


def cyclic_subsets_ok(g, ports):
    """every vertex set inducing a cycle has at least 4 boundary edges, port edges counted (exhaustive)"""
    nodes = sorted(g, key=str)
    idx = {v: i for i, v in enumerate(nodes)}
    E = [(idx[a], idx[b]) for a, b in g.edges()]
    pmask = sum(1 << idx[v] for v in ports)
    worst = 99
    for Y in range(1, 1 << len(nodes)):
        inside = [(a, b) for a, b in E if Y >> a & 1 and Y >> b & 1]
        nv = bin(Y).count("1")
        if len(inside) < nv:                       # a forest has fewer edges than vertices; test cycles exactly
            parent = list(range(len(nodes)))

            def find(u):
                while parent[u] != u:
                    parent[u] = parent[parent[u]]
                    u = parent[u]
                return u
            cyc = False
            for a, b in inside:
                ra, rb = find(a), find(b)
                if ra == rb:
                    cyc = True
                    break
                parent[ra] = rb
            if not cyc:
                continue
        bd = sum(1 for a, b in E if (Y >> a & 1) != (Y >> b & 1)) + bin(Y & pmask).count("1")
        worst = min(worst, bd)
    return worst


# ---------------------------------------------------------------- 0
man = json.load(open(os.path.join(HERE, "manifest.json")))
mism = {r: dg for r, dg in man["parent_bindings"].items()
        if hashlib.sha256(open(os.path.join(ROOT, r), "rb").read()).hexdigest() != dg}
report("0 dependency artifacts bound by hash", not mism, {"parents": len(man["parent_bindings"]), "mismatched": mism})

# ---------------------------------------------------------------- 1 Hall's condition on examples
fam = {f"{2 * n}-prism": nx.circular_ladder_graph(2 * n) for n in range(2, 7)}
fam.update({f"flags of {nm}": CL.omnitruncation(m) for nm, m in (("K4", nx.complete_graph(4)), ("triangular prism", nx.circular_ladder_graph(3)),
                                                                 ("square pyramid", nx.wheel_graph(5)))})
d1, ok1 = {}, True
for nm, g in fam.items():
    g = nx.convert_node_labels_to_integers(g)
    c4, br = BL.cyclic4(g), PG.is_brace(g)
    d1[nm] = {"vertices": g.number_of_nodes(), "cyclically 4-edge-connected": c4, "brace": br}
    ok1 &= (not c4) or br
cube = nx.convert_node_labels_to_integers(nx.hypercube_graph(3))
colc = nx.bipartite.color(cube)
pnt = [v for v in cube if colc[v] == 0][0]
lin = [v for v in cube if colc[v] == 1][0]
a_ = cube.copy(); a_.remove_node(pnt)
b_ = cube.copy(); b_.remove_node(lin)
J3 = nx.disjoint_union(a_, b_)
deg2a = [v for v in J3 if J3.degree(v) == 2 and v < a_.number_of_nodes()]
deg2b = [v for v in J3 if J3.degree(v) == 2 and v >= a_.number_of_nodes()]
J3.add_edges_from(zip(deg2a, deg2b))
d1["two cubes minus a vertex, joined by three edges"] = {"bipartite cubic": nx.is_bipartite(J3) and all(d == 3 for _, d in J3.degree()),
                                                         "cyclically 4-edge-connected": BL.cyclic4(J3), "brace": PG.is_brace(J3)}
ok1 &= not BL.cyclic4(J3) and not PG.is_brace(J3)
report("1 Hall's condition on examples: cyclically 4-edge-connected planar cubic bipartite graphs are braces; a cyclic 3-cut is not", ok1, d1)

# ---------------------------------------------------------------- 2 the pieces
d2, ok2 = {}, True
for k in (1, 2, 3):
    Bs = X.Builder()
    pr = BL.site(Bs, 'x', k)
    ports = [pr['A'][0], pr['A'][1], pr['B'][0], pr['B'][1]]
    host_site = Bs.g.subgraph([v for v in Bs.g if not PL.is_page(v)]).copy()
    for S_ in [s_ for s_ in PL.squares_of(Bs)]:
        host_site.add_edges_from((S_[i], S_[(i + 1) % 4]) for i in range(4))
    ladder = nx.is_isomorphic(host_site, nx.ladder_graph(3 * k))
    worst = cyclic_subsets_ok(host_site, ports)
    d2[f"site with {k} junctions"] = {"vertices": host_site.number_of_nodes(), "ladder with 3k rungs": ladder,
                                      "fewest boundary edges of a set with a cycle": worst}
    ok2 &= ladder and worst >= 4
Jn = nx.Graph()
C = [('c', i) for i in range(4)]
for nm in ('q', "q'"):
    for i in range(4):
        Jn.add_edge((nm, i), (nm, (i + 1) % 4))
        Jn.add_edge(('c', i), (nm, i))
worst = cyclic_subsets_ok(Jn, C)
d2["cube junction (square edges deleted, host edges as ports)"] = {"2-edge-connected": nx.edge_connectivity(Jn) >= 2,
                                                                   "fewest boundary edges of a set with a cycle": worst}
ok2 &= nx.edge_connectivity(Jn) >= 2 and worst >= 4
glued = {}
for nm in ("4-prism", "6-prism", "flags of K4"):
    g = nx.convert_node_labels_to_integers(fam[nm])
    S_ = PG.squares(g)[0]
    h = g.copy()
    h.remove_edges_from((S_[i], S_[(i + 1) % 4]) for i in range(4))
    for tag in ('q', "q'"):
        for i in range(4):
            h.add_edge((tag, i), (tag, (i + 1) % 4))
            h.add_edge(S_[i], (tag, i))
    glued[nm] = PG.is_brace(h)
d2["a square replaced by the cube junction gives a brace"] = glued
ok2 &= all(glued.values())
report("2 the pieces: sites are ladders, sets with a cycle have >= 4 boundary edges (sites, cube junction); glued examples are braces",
       ok2, d2)

# ---------------------------------------------------------------- 3 weaving
TO = WV.named(CL.omnitruncation(nx.complete_graph(4)), 'F')
SOURCES = {"two halves (2-edge cut)": WV.two_halves(), "K3,3": WV.named(nx.complete_bipartite_graph(3, 3), 'g'),
           "Heawood": WV.named(nx.heawood_graph(), 'g')}
CASES = [("two halves (2-edge cut)", "prism 12", WV.prism(6), 0), ("two halves (2-edge cut)", "prism 12", WV.prism(6), 1),
         ("two halves (2-edge cut)", "truncated octahedron", TO, 2), ("K3,3", "prism 6", WV.prism(3), 6),
         ("Heawood", "prism 14", WV.prism(7), 0)]
d3, ok3 = {"source is a brace": {nm: PG.is_brace(nx.convert_node_labels_to_integers(G)) for nm, G in SOURCES.items()}}, True
WOVEN = {}
for sname, fname, F, seed in CASES:
    G = SOURCES[sname]
    pos = WV.drawing(F, G, seed)
    Bw, cr = WV.build(F, G, pos)
    H, neg = Bw.system()
    host = PL.leaves(Bw)[0][0]
    good, lv, kap = PL.certify(Bw, TW, AM)
    rec = {"crossings": len(cr), "vertices": Bw.g.number_of_nodes(), "signs": len(neg), "host planar": nx.check_planarity(host)[0],
           "host cyclically 4-edge-connected": BL.cyclic4(host), "certified Pfaffian": good}
    if Bw.g.number_of_nodes() <= 260:
        rec["brace (direct test)"] = PG.is_brace(Bw.g)
    d3[f"{sname} in {fname}, seed {seed}"] = rec
    WOVEN[(sname, fname, seed)] = (F, G, pos, cr)
    ok3 &= not neg and rec["host planar"] and rec["host cyclically 4-edge-connected"] and good and rec.get("brace (direct test)", True)
    print("   ", sname, fname, seed, rec, round(time.time() - T0, 1), "s", flush=True)
report("3 weaving: hosts planar and cyclically 4-edge-connected, instances plain and certified Pfaffian", ok3, d3)

# ---------------------------------------------------------------- 4 single-site interpolation inside a woven instance
d4, ok4 = {}, True
for key in (("two halves (2-edge cut)", "prism 12", 0), ("K3,3", "prism 6", 6)):
    F, G, pos, cr = WOVEN[key]
    gf = [c for c, (i, j) in enumerate(cr)]
    for c0 in (gf[0], gf[len(gf) // 2]):
        Z = {k: count(WV.build(F, G, pos, kmap={c0: k})[0]) for k in (1, 3, 5, 7)}
        rec_ = sum(F_COEF[j] * Z[2 * j + 1] for j in range(4))
        restored = count(WV.build(F, G, pos, restored={c0})[0])
        d4[f"{key[0]} in {key[1]}, site {c0}"] = {"recovered": str(rec_), "count with the site restored": restored}
        ok4 &= rec_ == restored
report("4 single-site interpolation inside woven instances recovers the count with that site restored", ok4, d4)

# ---------------------------------------------------------------- 5 the frame factor
pc = {}
for n in range(2, 11):
    Bp = X.Builder()
    for a, b in WV.prism(n).edges():
        pa, lb = (a, b) if X.is_point(a) else (b, a)
        Bp.edge(pa, lb)
    pc[2 * n] = count(Bp)
d5 = {"#col of the plain prism C_2n x K2": pc}
F, G, pos, cr = WOVEN[("two halves (2-edge cut)", "prism 12", 0)]
all_restored = count(WV.build(F, G, pos, restored=set(range(len(cr))))[0])
Bg = X.Builder()
for a, b in G.edges():
    pa, lb = (a, b) if X.is_point(a) else (b, a)
    Bg.edge(pa, lb)
d5["every site restored = #col(source) #col(frame)"] = [all_restored, count(Bg) * pc[12]]
ok5 = all(v > 0 for v in pc.values()) and all_restored == count(Bg) * pc[12]
report("5 the frame factor: plain prisms colourable; with every site restored the count factors", ok5, d5)

# ---------------------------------------------------------------- 6 controls
ctrl = {}
import numpy as np  # noqa: E402
G = WV.two_halves()
pos = {}
for v in G:
    cp, i = v[2], v[3]
    pos[v] = np.array([3.0 * cp + (0.0 if v[0] == 'pt' else 1.0), 0.37 * i + 0.11 * (v[0] == 'ln')])
Bn, crn = WV.build(nx.Graph(), G, pos)
hostn = PL.leaves(Bn)[0][0] if PL.squares_of(Bn) else Bn.g
ctrl["without a frame the 2-edge cut survives (host not cyclically 4-edge-connected)"] = not BL.cyclic4(hostn)
ctrl["... and the instance is not a brace"] = not PG.is_brace(nx.convert_node_labels_to_integers(Bn.g))
F, G2, pos2, cr2 = WOVEN[("K3,3", "prism 6", 6)]
Be, _ = WV.build(F, G2, pos2, kmap={0: 2})
ctrl["an even number of junctions at one site leaves the host non-planar"] = not nx.check_planarity(PL.leaves(Be)[0][0])[0]
report("6 controls fire", all(ctrl.values()), {**ctrl, "crossings without a frame": len(crn)})

out["ok"] = ok_all
out["seconds"] = round(time.time() - T0, 1)
print("ALL OK" if ok_all else "SOME CHECK FAILED", out["seconds"], "s")
if "--write" in sys.argv:
    json.dump({"schema_version": 1, "artifact_id": "PLAIN-BRACE-20261031-001B-P001", "status": "Proved" if ok_all else "Failed",
               "checks": out}, open(os.path.join(HERE, "result.json"), "w"), indent=1, default=str)
sys.exit(0 if ok_all else 1)
