"""Lane B (NEXT-DIRECTION-SCAN-20261031-001B): is the knot's sign class a free fermion at every coupling, or only at the counting point?

#col is an even-subgraph (Ising high-temperature) sum on the incidence graph: points [1,0,1,0], lines [1,0,x^2,0], a negated incidence
contributes -1 when its edge is used, and the counting point is x^2 = -1/3. In the colour basis the same sum is the three-body Ising model of
the triple system: a line weighs 1+3x^2 when its three points (after negation) agree and 1-x^2 otherwise (Z_col = 2^#points Z_even).

The polynomial algorithm of TWIST-COUNT-20261030-001A runs while every trisum junction satisfies the matchgate identity (MGI). Here the
junction is computed at general x and the identity is tested as a polynomial in x:
  1. junctions of two pages in the knot's class (the glued Kasteleyn signing);
  2. why single pages work: their tensors lie in a two-parameter family closed under junctions, and the similitude of TWIST-COUNT A,
     Theorem 4, holds at general x (MGI(W) = c_Q(x) MGI(F_R) for a symbolic F_R);
  3. twisted pairs: the couplings at which a doubly twisted junction satisfies the identity;
  4. depth two: closed branches that carry a junction at a second square, their defect from the family, and the zeros shared by every
     junction of two such branches;
  5. consistency: host tensor x junction = the brute-force three-body Ising sum of the glued system, as polynomials in x, at depth one
     and depth two;
  6. control: junctions of generic matchgate pages.
Run: .venv/bin/python -B fermion.py [--write]"""
import itertools
import json
import random
import sys
import time
from pathlib import Path

import networkx as nx
import numpy as np
import sympy as sp

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
for p in ("proofs/TWIST-COUNT-20261030-001A/TWIST-COUNT-20261030-001A-P001_the_knots_junction_is_a_similitude",
          "proofs/THREEFOLD-AMPLITUDE-20261030-001B/THREEFOLD-AMPLITUDE-20261030-001B-P001_the_amplitude_by_computation"):
    sys.path.insert(0, str(ROOT / p))
import twist_lib as TW  # noqa: E402
import computation_lib as CL  # noqa: E402

x = sp.Symbol('x')
T0 = time.time()
OUT = {}
EVEN = [y for y in itertools.product((0, 1), repeat=4) if sum(y) % 2 == 0]


def check(name, ok, info):
    OUT[name] = {"pass": bool(ok), "info": info}
    print("PASS" if ok else "FAIL", name, json.dumps(info, default=str)[:900], round(time.time() - T0, 1), "s", flush=True)
    if not ok:
        print(json.dumps(info, default=str, indent=1))
        sys.exit(1)


def faces_of(g):
    ok, emb = nx.check_planarity(g)
    assert ok
    seen, out = set(), []
    for u, v in emb.edges():
        if (u, v) not in seen:
            out.append(emb.traverse_face(u, v, mark_half_edges=seen))
    return out


def squares_of(g):
    col = nx.bipartite.color(g)
    out = []
    for f in faces_of(g):
        if len(f) == 4:
            i0 = [k for k in range(4) if col[f[k]] == 0][0]
            out.append(tuple(f[i0:] + f[:i0]))
    return out


def gf2_solve(rows, rhs):
    piv = {}
    for r, b in zip(rows, rhs):
        for c, (pr, pb) in piv.items():
            if r >> c & 1:
                r ^= pr
                b ^= pb
        if r == 0:
            if b:
                return None
            continue
        c = r.bit_length() - 1
        for c2 in list(piv):
            if piv[c2][0] >> c & 1:
                piv[c2] = (piv[c2][0] ^ r, piv[c2][1] ^ b)
        piv[c] = (r, b)
    return sum(1 << c for c, (r, b) in piv.items() if b)


def branch_tensor(g, S, sign):
    """F(y0..y3) of a closed branch: g holds the branch's own edges (no square edges) and the four square vertices S = (c0, c1, c2, c3)
    with one leg each; sum over even subgraphs with leg values y, x^2 per internal line of degree 2, (-1)^|sign & chi|. Points are the
    colour class of c0."""
    col = nx.bipartite.color(g)
    pc = col[S[0]]
    own = [frozenset(e) for e in g.edges()]
    idx = {e: k for k, e in enumerate(own)}
    legs = []
    for i in range(4):
        (w,) = list(g[S[i]])
        legs.append(frozenset((S[i], w)))
    internal = [v for v in g if v not in S]
    rows = [sum(1 << idx[e] for e in own if v in e) for v in internal]
    G_own = nx.Graph([tuple(e) for e in own])
    span = [0]
    for cyc in nx.cycle_basis(G_own):
        m = 0
        for a, b in zip(cyc, cyc[1:] + cyc[:1]):
            m ^= 1 << idx[frozenset((a, b))]
        span += [s ^ m for s in span]
    kmask = sum(1 << idx[e] for e in own if e in sign)
    lmasks = [sum(1 << idx[e] for e in own if v in e) for v in internal if col[v] != pc]
    F = {}
    for y in itertools.product((0, 1), repeat=4):
        z0 = None if sum(y) % 2 else gf2_solve(rows + [1 << idx[l] for l in legs], [0] * len(rows) + list(y))
        if z0 is None:
            F[y] = sp.Integer(0)
            continue
        coef = {}
        for c in span:
            chi = z0 ^ c
            k = sum(1 for lm in lmasks if bin(chi & lm).count("1") == 2)
            coef[k] = coef.get(k, 0) + (-1) ** bin(chi & kmask).count("1")
        F[y] = sp.expand(sum(v * x ** (2 * k) for k, v in coef.items()))
    return F


def junction(FQ, FR):
    """W(host legs): c0, c2 points (even parity of host, Q, R legs), c1, c3 lines (even parity, x^2 at degree 2)"""
    W = {}
    for yh in itertools.product((0, 1), repeat=4):
        tot = 0
        for yq in EVEN:
            yr = tuple((yh[i] + yq[i]) % 2 for i in range(4))
            w = 1
            for i in (1, 3):
                if yh[i] + yq[i] + yr[i] == 2:
                    w = w * x ** 2
            tot += w * FQ[yq] * FR[yr]
        W[yh] = sp.expand(tot)
    return W


def mgi(f):
    return sp.expand(f[(0, 0, 0, 0)] * f[(1, 1, 1, 1)] - f[(1, 1, 0, 0)] * f[(0, 0, 1, 1)] + f[(1, 0, 1, 0)] * f[(0, 1, 0, 1)]
                     - f[(1, 0, 0, 1)] * f[(0, 1, 1, 0)])


PAGES = {"cube": nx.convert_node_labels_to_integers(nx.hypercube_graph(3)),
         "6-prism": nx.circular_ladder_graph(6),
         "truncated octahedron": nx.convert_node_labels_to_integers(CL.omnitruncation(nx.complete_graph(4)))}


def glue(parts):
    """parts: list of (tag, g, [squares as tuples of g's vertices], [square names]); the square vertices of square name n become
    ('sq', n, k). Returns the leaves (relabelled graphs with their squares) for TW.kasteleyn_tree_signing and the glued graph."""
    leaves, G = [], nx.Graph()
    for tag, g, sqs, names in parts:
        rel = {v: (tag, v) for v in g}
        for S, n in zip(sqs, names):
            for k in range(4):
                rel[S[k]] = ('sq', n, k)
        h = nx.relabel_nodes(g, rel)
        sq_named = [tuple(('sq', n, k) for k in range(4)) for n in names]
        leaves.append((h, sq_named))
        sqe = {frozenset((Sn[j], Sn[(j + 1) % 4])) for Sn in sq_named for j in range(4)}
        G.add_edges_from(tuple(e) for e in map(frozenset, h.edges()) if e not in sqe)
    return leaves, G


def branch_graph(G, n, side_nodes):
    """the closed branch of square n containing `side_nodes` (glued graph G minus the square's other incidences)"""
    S = tuple(('sq', n, k) for k in range(4))
    H = G.copy()
    for v in S:
        H.remove_edges_from([(v, w) for w in list(H[v]) if w not in side_nodes])
    comp = set()
    for v in side_nodes:
        comp |= nx.node_connected_component(H.subgraph([u for u in H if u not in S]), v)
    return H.subgraph(comp | set(S)).copy(), S


def three_pages(nh, nq, nr):
    parts = [('h', PAGES[nh], [squares_of(PAGES[nh])[0]], [0]), ('q', PAGES[nq], [squares_of(PAGES[nq])[0]], [0]),
             ('r', PAGES[nr], [squares_of(PAGES[nr])[0]], [0])]
    leaves, G = glue(parts)
    return leaves, G


def side(G, tag):
    return {v for v in G if v[0] == tag}


def internal_edge(G, tag):
    """an edge of page `tag` away from the square, on a cycle of the page's own edges"""
    own = nx.Graph([e for e in G.edges() if e[0][0] == tag and e[1][0] == tag])
    for e in own.edges():
        if not nx.has_bridges(own) or e not in set(nx.bridges(own)):
            return frozenset(e)


# ------------------------------------------------------------------------------------------------ 1. the knot's class at every coupling
res1, keep = {}, {}
for nq, nr in itertools.combinations_with_replacement(PAGES, 2):
    leaves, G = three_pages("cube", nq, nr)
    kappa = TW.kasteleyn_tree_signing(leaves)
    BQ, S = branch_graph(G, 0, side(G, 'q'))
    BR, _ = branch_graph(G, 0, side(G, 'r'))
    FQ, FR = branch_tensor(BQ, S, kappa), branch_tensor(BR, S, kappa)
    W = junction(FQ, FR)
    m = mgi(W)
    res1[f"{nq} x {nr}"] = {"junction MGI(x)": str(m), "pages' MGI": [str(mgi(FQ)), str(mgi(FR))]}
    keep[(nq, nr)] = (leaves, G, kappa, FQ, FR, W)
check("1 the knot's class: every junction satisfies the matchgate identity at every coupling x", all(v["junction MGI(x)"] == "0" for v in
      res1.values()), res1)

# ------------------------------------------------------------------------------------------------ 2. the similitude at every coupling
r = {y: sp.Symbol('r' + ''.join(map(str, y))) for y in EVEN}
FRs = {y: (r[y] if y in r else sp.Integer(0)) for y in itertools.product((0, 1), repeat=4)}
res2 = {}
for nq in PAGES:
    FQ = keep[tuple(sorted((nq, nq), key=list(PAGES).index))][3]
    m = mgi(junction(FQ, FRs))
    c = sp.Poly(m, *r.values()).coeff_monomial(r[(0, 0, 0, 0)] * r[(1, 1, 1, 1)])
    ok = sp.expand(m - c * mgi(FRs)) == 0
    # write the untwisted page's even entries as a split: F(0000), F(1111), ... in the knot's class
    res2[nq] = {"MGI(W) = c_Q(x) MGI(F_R) for symbolic F_R": ok, "c_Q(x)": str(sp.factor(c)),
                "c_Q at x^2 = -1/3": str(sp.factor(c.subs(x, sp.sqrt(sp.Rational(-1, 3))))),
                "page entries": {''.join(map(str, y)): str(sp.factor(FQ[y])) for y in EVEN},
                "two-parameter family (F(1010) = F(0101) = 0, F(1100) = -F(0011), F(1001) = F(0110))":
                    FQ[(1, 0, 1, 0)] == 0 and FQ[(0, 1, 0, 1)] == 0 and sp.expand(FQ[(1, 1, 0, 0)] + FQ[(0, 0, 1, 1)]) == 0
                    and sp.expand(FQ[(1, 0, 0, 1)] - FQ[(0, 1, 1, 0)]) == 0}
# the family is closed under junctions at every x: W of two symbolic members is again a member
u1, v1, u2, v2 = sp.symbols('u1 v1 u2 v2')


def member(u, v):
    F = {y: sp.Integer(0) for y in itertools.product((0, 1), repeat=4)}
    F.update({(0, 0, 0, 0): 1, (1, 1, 0, 0): u, (0, 0, 1, 1): -u, (1, 0, 0, 1): v, (0, 1, 1, 0): v, (1, 1, 1, 1): v * v - u * u})
    return F


Wm = junction(member(u1, v1), member(u2, v2))
res2["closure of the family under junctions (symbolic members, every x)"] = (
    mgi(Wm) == 0 and Wm[(1, 0, 1, 0)] == 0 and Wm[(0, 1, 0, 1)] == 0 and sp.expand(Wm[(1, 1, 0, 0)] + Wm[(0, 0, 1, 1)]) == 0
    and sp.expand(Wm[(1, 0, 0, 1)] - Wm[(0, 1, 1, 0)]) == 0)
check("2 single pages at every coupling: each lies in a two-parameter family that is closed under junctions, and Theorem 4's similitude "
      "holds", all(v["MGI(W) = c_Q(x) MGI(F_R) for symbolic F_R"] and v["two-parameter family (F(1010) = F(0101) = 0, F(1100) = -F(0011), "
                                                                       "F(1001) = F(0110))"] for k, v in res2.items() if k in PAGES)
      and res2["closure of the family under junctions (symbolic members, every x)"], res2)

# ------------------------------------------------------------------------------------------------ 3. twisted pairs
res3 = {}
for (nq, nr), (leaves, G, kappa, FQ0, FR0, W0) in keep.items():
    eq, er = internal_edge(G, 'q'), internal_edge(G, 'r')
    for label, flips in (("Q twisted", {eq}), ("both twisted", {eq, er})):
        sigma = set(kappa) ^ flips
        tw = TW.twisted_branches(leaves, [tuple(('sq', 0, k) for k in range(4))], sigma, kappa)
        BQ, S = branch_graph(G, 0, side(G, 'q'))
        BR, _ = branch_graph(G, 0, side(G, 'r'))
        m = sp.factor(mgi(junction(branch_tensor(BQ, S, sigma), branch_tensor(BR, S, sigma))))
        zeros = sorted({str(z) if z in (0, 1, -1, sp.I, -sp.I) else str(sp.N(z, 8)) for z in sp.solve(m, x)}) if m != 0 else ["every x"]
        res3[f"{nq} x {nr}, {label}"] = {"twisted branches": sum(tw.values()), "MGI(x)": str(m), "zeros": zeros,
                                         "at x^2 = -1/3": str(sp.simplify(m.subs(x, sp.sqrt(sp.Rational(-1, 3)))))}
one = [v for k, v in res3.items() if k.endswith("Q twisted")]
two = [v for k, v in res3.items() if k.endswith("both twisted")]
AFFINE = {"0", "1", "-1", "I", "-I"}
for v in two:
    v["zeros off the affine couplings 0, +-1, +-i"] = [z for z in v["zeros"] if z not in AFFINE]
check("3 twists: one twisted page keeps the identity at every x; two twisted pages break it at the counting point and keep it only at "
      "isolated couplings, always including the affine ones x = 0, +-1, +-i",
      all(v["MGI(x)"] == "0" and v["twisted branches"] == 1 for v in one)
      and all(v["MGI(x)"] != "0" and v["twisted branches"] == 2 and v["at x^2 = -1/3"] != "0" and AFFINE <= set(v["zeros"]) for v in two),
      res3)

# ------------------------------------------------------------------------------------------------ 4. depth two: where the class stays free
def two_square_page(name):
    g = PAGES[name]
    sqs = squares_of(g)
    return g, sqs[0], next(T for T in sqs if not set(T) & set(sqs[0]))


def depth_two_parts(tag, page, kids, n_parent, n_child):
    g, S1, S2 = two_square_page(page)
    out = [(tag, g, [S1, S2], [n_parent, n_child])]
    for j, k in enumerate(kids):
        out.append((tag + str(j), PAGES[k], [squares_of(PAGES[k])[0]], [n_child]))
    return out


def tags_of(G, tag):
    return {v for v in G if isinstance(v[0], str) and v[0].startswith(tag)}


cubeS = squares_of(PAGES["cube"])[0]
res4, loci, deep_keep = {}, [], {}
SHAPES = [("6-prism", ("cube", "cube")), ("6-prism", ("cube", "6-prism")), ("truncated octahedron", ("cube", "cube"))]
for (pq, kq), (pr, kr) in itertools.combinations_with_replacement(SHAPES, 2):
    parts = [('h', PAGES["cube"], [cubeS], [0])] + depth_two_parts('q', pq, kq, 0, 1) + depth_two_parts('r', pr, kr, 0, 2)
    leaves, G = glue(parts)
    kappa = TW.kasteleyn_tree_signing(leaves)
    sq = lambda n: {('sq', n, k) for k in range(4)}
    BQ, S = branch_graph(G, 0, tags_of(G, 'q') | sq(1))
    BR, _ = branch_graph(G, 0, tags_of(G, 'r') | sq(2))
    FQ, FR = branch_tensor(BQ, S, kappa), branch_tensor(BR, S, kappa)
    cube_page = keep[("cube", "cube")][3]
    m = sp.factor(mgi(junction(FQ, FR)))
    entry = {"branch vertices": [BQ.number_of_nodes(), BR.number_of_nodes()],
             "Q's defect F(1001) - F(0110)": str(sp.factor(FQ[(1, 0, 0, 1)] - FQ[(0, 1, 1, 0)])),
             "Q's other relations hold (cross entries 0, F(1100) = -F(0011))": FQ[(1, 0, 1, 0)] == 0 and FQ[(0, 1, 0, 1)] == 0
             and sp.expand(FQ[(1, 1, 0, 0)] + FQ[(0, 0, 1, 1)]) == 0,
             "junction with a single knot-class page: MGI": str(mgi(junction(FQ, cube_page))),
             "junction of the two branches: MGI(x)": str(m)}
    if m != 0:
        entry["vanishes at x^2 = -1/3"] = sp.simplify(m.subs(x, sp.sqrt(sp.Rational(-1, 3)))) == 0
        loci.append({str(f) for f, e in sp.factor_list(m)[1]})
    res4[f"{pq}{list(kq)} x {pr}{list(kr)}"] = entry
    deep_keep[f"{pq}{list(kq)} x {pr}{list(kr)}"] = (G, kappa, BQ, BR, S)
common = set.intersection(*loci) if loci else set()
res4["factors common to every two-branch junction"] = sorted(common)
zero_pairs = [k for k, v in res4.items() if isinstance(v, dict) and v.get("junction of the two branches: MGI(x)") == "0"]
res4["pairs whose junction keeps the identity at every x (both branches in one rotated two-parameter family)"] = zero_pairs
check("4 depth two: knot-class junctions of deep branches break the identity; the couplings common to every breaking junction are exactly "
      "the counting point x^2 = -1/3 and the affine couplings x = 0, +-1, +-i", len(loci) >= 4
      and all(v["vanishes at x^2 = -1/3"] for v in res4.values() if isinstance(v, dict) and "vanishes at x^2 = -1/3" in v)
      and all(v["junction with a single knot-class page: MGI"] == "0" for v in res4.values() if isinstance(v, dict) and "branch vertices" in v)
      and common == {"x", "x - 1", "x + 1", "x**2 + 1", "3*x**2 + 1"}, res4)

# ------------------------------------------------------------------------------------------------ 5. consistency with brute force
def brute(G, S, sign):
    """Z_col(x) of the glued system by enumerating point colourings (numpy), lines weighing 1+3x^2 when monochromatic after signs"""
    col = nx.bipartite.color(G)
    pc = col[S[0]]
    pts = [v for v in G if col[v] == pc]
    lns = [v for v in G if col[v] != pc]
    pid = {p: i for i, p in enumerate(pts)}
    c = ((np.arange(2 ** len(pts))[:, None] >> np.arange(len(pts))[None, :]) & 1).astype(np.int8)
    mono = np.zeros(len(c), dtype=np.int16)
    for l in lns:
        seen = [c[:, pid[p]] ^ int(frozenset((l, p)) in sign) for p in G[l]]
        mono += (seen[0] == seen[1]) & (seen[1] == seen[2])
    cnt = np.bincount(mono, minlength=len(lns) + 1)
    a_, b_ = 1 + 3 * x ** 2, 1 - x ** 2
    return sp.expand(sum(int(n) * a_ ** k * b_ ** (len(lns) - k) for k, n in enumerate(cnt) if n)), len(pts), len(lns)


res5 = {}
cases = [(f"{nq} x {nr}, {label}", keep[(nq, nr)][1], label) for (nq, nr) in (("cube", "cube"), ("cube", "6-prism"))
         for label in ("knot's class", "both twisted")]
for name, G, label in cases:
    kappa = keep[tuple(name.split(",")[0].split(" x "))][2]
    sign = set(kappa) if label == "knot's class" else set(kappa) ^ {internal_edge(G, 'q'), internal_edge(G, 'r')}
    BQ, S = branch_graph(G, 0, side(G, 'q'))
    BR, _ = branch_graph(G, 0, side(G, 'r'))
    BH, _ = branch_graph(G, 0, side(G, 'h'))
    res5[name] = (G, sign, BQ, BR, BH, S)
for name in list(deep_keep)[:2]:
    G, kappa, BQ, BR, S = deep_keep[name]
    BH, _ = branch_graph(G, 0, side(G, 'h'))
    res5["depth two: " + name + ", knot's class"] = (G, set(kappa), BQ, BR, BH, S)
for name, (G, sign, BQ, BR, BH, S) in list(res5.items()):
    Wl = junction(branch_tensor(BQ, S, sign), branch_tensor(BR, S, sign))
    FH = branch_tensor(BH, S, sign)
    z_net = sp.expand(sum(FH[y] * Wl[y] for y in EVEN))
    z_col, npts, nlns = brute(G, S, sign)
    res5[name] = {"points": npts, "Z_col = 2^points * (host . junction)": sp.expand(z_col - 2 ** npts * z_net) == 0,
                  "#col (x^2 = -1/3)": str(sp.nsimplify(z_col.subs(x, sp.sqrt(sp.Rational(-1, 3))) * sp.Rational(3, 4) ** nlns))}
check("5 the junction network reproduces the brute-force three-body Ising sum as a polynomial in x (depth one and depth two)", all(
    v["Z_col = 2^points * (host . junction)"] for v in res5.values()), res5)

# ------------------------------------------------------------------------------------------------ 6. control: generic matchgate pages
rng = random.Random(20261031)


def random_matchgate():
    a = {p: sp.Rational(rng.randint(-9, 9), rng.randint(1, 5)) for p in itertools.combinations(range(4), 2)}
    F = {y: sp.Integer(0) for y in itertools.product((0, 1), repeat=4)}
    F[(0, 0, 0, 0)] = sp.Integer(1)
    for (i, j), v in a.items():
        F[tuple(int(k in (i, j)) for k in range(4))] = v
    F[(1, 1, 1, 1)] = a[(0, 1)] * a[(2, 3)] - a[(0, 2)] * a[(1, 3)] + a[(0, 3)] * a[(1, 2)]
    return F


bad = 0
for t in range(20):
    FQ, FR = random_matchgate(), random_matchgate()
    assert mgi(FQ) == 0 and mgi(FR) == 0
    bad += mgi(junction(FQ, FR)) != 0
check("6 control: junctions of generic matchgate pages violate the identity, so 1-4 are not automatic", bad >= 18,
      {"generic pairs violating the identity (of 20)": bad})

OUT["seconds"] = round(time.time() - T0, 1)
print("ALL OK", OUT["seconds"], "s")
if "--write" in sys.argv:
    (HERE / "results.json").write_text(json.dumps(OUT, indent=1, default=str) + "\n")
