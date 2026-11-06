"""Checks for TWIST-COUNT-20261030-001A-P001 (the knot's junction is a similitude; unbranched twists count in polynomial time).

  0 dependency artifacts bound by the hashes recorded in manifest.json
  1 the Hadamard form #col = (3/2)^n sum_chi (-1/3)^(|chi|/2) (-1)^|sigma & chi| on small graphs under random signings; one flipped
    incidence of a non-colourable system gives #col(H - L)
  2 pages (planar branches with a square face) under every sign class: Hadamard tensors even with matchgate identity 0; untwisted classes
    (the interior agrees with a Kasteleyn signing up to switching) are exactly those with the split form
  3 the similitude MGI(W) = (alpha^2 + alpha beta + beta^2) MGI(F) as a polynomial identity (generic even F, symbolic alpha, beta), for all
    8 odd square patterns and 4 signs of the untwisted branch's legs; the host's and the other branch's incidence signs act as X on legs
    and change the sign; random checks on all 64 sign choices
  4 junctions of two twisted pages leave the matchgate class (cube and 6-prism pages; exclusive crossings), and generic matchgate pages do
    too; one untwisted page keeps every junction in the class
  5 junction tensor networks on trisum trees under the Kasteleyn signing and local, two-leaf and global twists: exact against direct
    counts; a good root exists iff no square has three twisted branches, and from it every junction is a matchgate signature
  6 controls that must fire
Run: .venv/bin/python -B check.py [--write]   (networkx, numpy, sympy, python-sat; about two minutes)"""
import collections, hashlib, itertools, json, os, random, sys, time
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
P = lambda r: os.path.join(ROOT, "proofs", r)  # noqa: E731
for p in (P("THREEFOLD-SPACES-20261030-001A/THREEFOLD-SPACES-20261030-001A-P001_three_fold_spaces_are_built_from_the_fano_plane"),
          P("THREEFOLD-SURFACES-20261030-001A/THREEFOLD-SURFACES-20261030-001A-P001_fano_atoms_are_handles"),
          P("THREEFOLD-GRAMMAR-20261030-001A/THREEFOLD-GRAMMAR-20261030-001A-P001_fano_leaves_and_planar_glue"),
          P("THREEFOLD-AMPLITUDE-20261030-001A/THREEFOLD-AMPLITUDE-20261030-001A-P001_five_per_handle_tuttes_number_per_planar_piece"),
          P("THREEFOLD-AMPLITUDE-20261030-001B/THREEFOLD-AMPLITUDE-20261030-001B-P001_the_amplitude_by_computation"),
          P("THREEFOLD-SPIN-20261030-001A/THREEFOLD-SPIN-20261030-001A-P001_kasteleyn_faces_and_even_spin_structures"),
          P("SEYMOUR-COUNT-20261030-001A/SEYMOUR-COUNT-20261030-001A-P001_the_trisum_law"),
          P("SEYMOUR-COUNT-20261030-001B/SEYMOUR-COUNT-20261030-001B-P001_polynomial_counting_on_seymours_cubic_bound"), HERE):
    sys.path.insert(0, p)
import networkx as nx  # noqa: E402
import numpy as np  # noqa: E402
import sympy as sp  # noqa: E402
import amplitude_lib as AM  # noqa: E402
import computation_lib as CL  # noqa: E402
import trisum_lib as TL  # noqa: E402
import seymour_lib as SY  # noqa: E402
import twist_lib as TW  # noqa: E402

T0 = time.time()
out, ok_all = {}, True


def report(key, ok, detail):
    global ok_all
    out[key] = {"ok": bool(ok), "detail": detail}
    ok_all &= bool(ok)
    print(("PASS " if ok else "FAIL ") + key + ": " + json.dumps(detail, default=str)[:3000], flush=True)


def system(G, lines, sign):
    """the signed system of a cubic bipartite graph: lines in sorted order, negations as (line index, point index)"""
    pts = sorted((v for v in G if v not in lines), key=str)
    lns = sorted(lines, key=str)
    pid = {v: k for k, v in enumerate(pts)}
    H = [tuple(sorted(pid[w] for w in G[l])) for l in lns]
    neg = [(i, pid[p]) for i, l in enumerate(lns) for p in G[l] if frozenset((l, p)) in sign]
    return H, neg, lns, pid


def lines_of(G, point):
    col = nx.bipartite.color(G)
    return {v for v in G if col[v] != col[point]}


# ---------------------------------------------------------------- 0
man = json.load(open(os.path.join(HERE, "manifest.json")))
mism = {r: dg for r, dg in man["parent_bindings"].items()
        if hashlib.sha256(open(os.path.join(ROOT, r), "rb").read()).hexdigest() != dg}
report("0 dependency artifacts bound by hash", not mism, {"parents": len(man["parent_bindings"]), "mismatched": mism})

# ---------------------------------------------------------------- 1 the Hadamard form; one flip
rng = random.Random(20261030)
d1, ok1 = {"Hadamard form": {}, "one flip": {}}, True
SMALL = {"cube": TL.prism_piece(2), "6-prism": TL.prism_piece(3), "trisum of three cubes": TL.trisum_of([TL.prism_piece(2)] * 1 +
         [TL.prism_piece(2, tag='q')] + [TL.prism_piece(2, True, tag='r')])}
for name, G in SMALL.items():
    lines = lines_of(G, TL.C4[0])
    edges = [frozenset(e) for e in G.edges()]
    basis = []
    for cyc in nx.cycle_basis(G):
        basis.append({frozenset((cyc[k], cyc[(k + 1) % len(cyc)])) for k in range(len(cyc))})
    evens = set()
    for mask in range(1 << len(basis)):
        chi = set()
        for k in range(len(basis)):
            if mask >> k & 1:
                chi ^= basis[k]
        evens.add(frozenset(chi))
    n = len(G) // 2
    agree = 0
    for trial in range(8):
        sign = {e for e in edges if rng.random() < 0.3}
        H, neg, lns, pid = system(G, lines, sign)
        direct = AM.count(H, neg)
        z = sum(Fraction(-1, 3) ** (len(chi) // 2) * (-1) ** len(chi & sign) for chi in evens)
        agree += Fraction(3, 2) ** n * z == direct
    d1["Hadamard form"][name] = {"even subgraphs": len(evens), "random signings agreeing": f"{agree}/8"}
    ok1 &= agree == 8
for name, G in (("trisum of three cubes", SMALL["trisum of three cubes"]), ("6-prism", SMALL["6-prism"])):
    lines = lines_of(G, TL.C4[0])
    leaves, squares = SY.trisum_tree(G, lines) if not nx.check_planarity(G)[0] else ([(G, [])], [])
    kappa = TW.kasteleyn_tree_signing(leaves)
    H, neg, lns, pid = system(G, lines, kappa)
    good = 0
    for i, l in enumerate(lns):
        for p in G[l]:
            flipped = kappa ^ {frozenset((l, p))}
            H2, neg2, _, _ = system(G, lines, flipped)
            good += AM.count(H2, neg2) == AM.count(H, neg, drop=i)
    d1["one flip"][name] = {"Kasteleyn signing colourable": AM.colourable(H, neg), "incidences where #col(flipped) = #col(H - L)": f"{good}/{3 * len(lns)}"}
    ok1 &= not AM.colourable(H, neg) and good == 3 * len(lns)
report("1 the Hadamard form under any signing; one flipped incidence gives #col(H - L)", ok1, d1)

# ---------------------------------------------------------------- 2 pages
PAGES = {"cube": TL.prism_piece(2), "6-prism": TL.prism_piece(3), "8-prism": TL.prism_piece(4),
         "truncated octahedron": CL.omnitruncation(nx.complete_graph(4)), "Omni(K2,3)": CL.omnitruncation(nx.complete_bipartite_graph(2, 3))}
PAGE_T = {}
d2, ok2 = {}, True
for name, g in PAGES.items():
    face = [TL.C4[0], TL.C4[1], TL.C4[2], TL.C4[3]] if TL.C4[0] in g else None
    inc, pts, att, sq = TW.page(g, face)
    kap = TW.kasteleyn_tree_signing([(g, [tuple(sq)])])
    real = {'c0': sq[0], 'c2': sq[2]}
    interior = {frozenset((l, p)) for l, ps in inc.items() for p in ps if p not in ('c0', 'c2')}
    stats = collections.Counter()
    tens = []
    for sign in TW.page_sign_classes(inc):
        F = TW.page_tensor(inc, pts, att, sign)
        Ft = TW.hada(F)
        flips = {e for e in interior if (e in {frozenset(x) for x in sign}) != (e in kap)}
        untw = TW.coboundary(interior, flips)
        spl = TW.split_of(F)
        stats[(not TW.odd_entries(Ft), TW.mgi(Ft) == 0, untw, spl is not None)] += 1
        tens.append((F, Ft, untw, spl))
    PAGE_T[name] = tens
    d2[name] = {"(even, matchgate, untwisted, split form) -> classes": {str(k): v for k, v in sorted(stats.items())}}
    ok2 &= all(k[0] and k[1] and k[2] == k[3] for k in stats)
report("2 pages: every sign class even and matchgate in the Hadamard basis; untwisted exactly when the split form holds", ok2, d2)

# ---------------------------------------------------------------- 3 the similitude
al, be = sp.symbols('alpha beta')
rs = {y: sp.Symbol('r' + ''.join(map(str, y))) for y in TW.EVEN}
Rt = np.zeros((2, 2, 2, 2), dtype=object)
for y in TW.EVEN:
    Rt[y] = rs[y]
FR_generic = TW.hada(Rt) / 16
mR = sp.expand(TW.mgi(Rt))
d3, ok3 = {"symbolic (pattern, leg signs) -> multiplier": {}, "random sign choices": {}}, True
for tau in itertools.product((0, 1), repeat=4):
    if sum(tau) % 2 == 0:
        continue
    for s1q, s3q in itertools.product((0, 1), repeat=2):
        FQ = TW.split_form(al, be, tau, s1q, s3q)
        W = TW.junction(FQ, FR_generic, (0, 0, 0), (0, 0, 0))
        m = sp.expand(TW.mgi(TW.hada(W)))
        ratio = sp.factor(sp.cancel(m / mR))
        d3["symbolic (pattern, leg signs) -> multiplier"][f"{tau} {s1q}{s3q}"] = str(ratio)
        ok3 &= sp.simplify(ratio - (al ** 2 + al * be + be ** 2)) == 0
# split forms are matchgate signatures and even, for every pattern and leg signs
split_mg = all(sp.expand(TW.mgi(TW.hada(TW.split_form(al, be, tau, a, b)))) == 0 and not TW.odd_entries(TW.hada(TW.split_form(2, 1, tau, a, b)))
               for tau in itertools.product((0, 1), repeat=4) if sum(tau) % 2 for a, b in itertools.product((0, 1), repeat=2))
d3["split forms are even matchgate signatures (all patterns, leg signs)"] = split_mg
ok3 &= split_mg
# junction signs act as X on legs: random integer checks over all 64 sign choices; the sign is (-1)^(host and other-branch incidence signs)
signs_ok, sign_seen = 0, set()
for s1, s3 in itertools.product(itertools.product((0, 1), repeat=3), repeat=2):
    a, b = rng.randint(0, 9), rng.randint(1, 9)
    tau = (1, 0, 0, 0)
    Fr = np.zeros((2, 2, 2, 2), dtype=object)
    for y in itertools.product((0, 1), repeat=4):
        Fr[y] = rng.randint(0, 7)
    Fr = Fr + Fr[::-1, ::-1, ::-1, ::-1]        # complement-symmetric, so its Hadamard tensor is even
    W = TW.junction(TW.split_form(a, b, tau), Fr, s1, s3)
    lhs, rhs = TW.mgi(TW.hada(W)), TW.mgi(TW.hada(Fr))
    eps = (-1) ** (s1[0] + s3[0] + s1[2] + s3[2])
    signs_ok += lhs == eps * (a * a + a * b + b * b) * rhs
    if rhs != 0:
        sign_seen.add(eps)
d3["random sign choices"] = {"sign choices with MGI(W) = (-1)^(host and R signs) N MGI(F)": f"{signs_ok}/64"}
ok3 &= signs_ok == 64
report("3 the similitude MGI(W) = +-(alpha^2 + alpha beta + beta^2) MGI(F), for every pattern and sign choice", ok3, d3)

# ---------------------------------------------------------------- 4 branched junctions
d4, ok4 = {}, True
for nq, nr in (("cube", "cube"), ("cube", "6-prism"), ("6-prism", "6-prism")):
    st = collections.Counter()
    excl = 0
    for (FQ, FtQ, uq, sq_), (FR, FtR, ur, sr) in itertools.product(PAGE_T[nq], PAGE_T[nr]):
        if nq == nr and id(FQ) > id(FR):
            continue
        for s1, s3 in (((0, 0, 0), (0, 0, 0)), ((0, 0, 1), (0, 1, 0)), ((0, 1, 1), (0, 1, 1))):
            Wt = TW.hada(TW.junction(FQ, FR, s1, s3))
            m = TW.mgi(Wt)
            kind = "both twisted" if not (uq or ur) else "one untwisted"
            st[(kind, m == 0)] += 1
            if not (uq or ur) and m != 0 and all(Wt[t] == 0 for t in ((1, 1, 0, 0), (0, 1, 1, 0), (0, 0, 1, 1), (1, 0, 0, 1))) and Wt[1, 1, 1, 1] == 0:
                excl += 1
    d4[f"{nq} x {nr}"] = {"(kind, matchgate) -> junctions": {str(k): v for k, v in sorted(st.items())}, "exclusive crossings": excl}
    ok4 &= st[("one untwisted", False)] == 0 and st[("both twisted", False)] > 0
# generic matchgate pages (Pfaffian parametrisation): the identity of the junction is not identically zero
A = sp.symbols('a01 a02 a03 a12 a13 a23')
Bs = sp.symbols('b01 b02 b03 b12 b13 b23')


def pf_tensor(x):
    a01, a02, a03, a12, a13, a23 = x
    t = np.zeros((2, 2, 2, 2), dtype=object)
    t[0, 0, 0, 0], t[1, 1, 0, 0], t[1, 0, 1, 0], t[1, 0, 0, 1] = 1, a01, a02, a03
    t[0, 1, 1, 0], t[0, 1, 0, 1], t[0, 0, 1, 1], t[1, 1, 1, 1] = a12, a13, a23, a01 * a23 - a02 * a13 + a03 * a12
    return t


Wg = TW.hada(TW.junction(TW.hada(pf_tensor(A)) / 16, TW.hada(pf_tensor(Bs)) / 16, (0, 0, 0), (0, 0, 0)))
mg = sp.expand(TW.mgi(Wg))
d4["generic matchgate pages"] = {"MGI of the junction identically zero": mg == 0, "terms": len(sp.Poly(mg, *A, *Bs).terms())}
ok4 &= mg != 0
report("4 junctions of two twisted pages leave the matchgate class; with one untwisted page they never do", ok4, d4)

# ---------------------------------------------------------------- 5 junction tensor networks on trisum trees
def sq_(name):
    return tuple((name, j) for j in range(4))


def multi_square_prism(k, labels, flips, tag):
    m = 2 * k
    g = nx.Graph()
    for i in range(m):
        g.add_edges_from([(('u', i), ('u', (i + 1) % m)), (('v', i), ('v', (i + 1) % m)), (('u', i), ('v', i))])
    mp = {}
    for t, (lab, f) in enumerate(zip(labels, flips)):
        face = [('u', 2 * t), ('u', 2 * t + 1), ('v', 2 * t + 1), ('v', 2 * t)]
        mp.update(dict(zip(face, list(lab) if not f else [lab[2], lab[1], lab[0], lab[3]])))
    return nx.relabel_nodes(g, lambda v: mp.get(v, (tag, v)))


def glue(pieces, S):
    G = nx.Graph()
    for g in pieces:
        G.add_edges_from(g.edges())
    G.remove_edges_from([(S[j], S[(j + 1) % 4]) for j in range(4)])
    return G


S1, S2, S3 = sq_('s1'), sq_('s2'), sq_('s3')
BRACES = {"trisum (2, 3, 4)": TL.trisum_of([TL.prism_piece(2), TL.prism_piece(3, tag='q'), TL.prism_piece(4, True, tag='r')])}
T1 = TL.trisum_of([TL.two_square_prism(3), TL.prism_piece(3, sq=TL.D4, tag='q'), TL.prism_piece(2, True, sq=TL.D4, tag='r')], sq=TL.D4)
BRACES["nested (3, 3, 2) | (2, 3)"] = TL.trisum_of([T1, TL.prism_piece(2, False, tag='s'), TL.prism_piece(3, True, tag='t')])
T3 = glue([multi_square_prism(3, [S2, S3], [0, 1], 'D'), multi_square_prism(2, [S3], [1], 'F'), multi_square_prism(2, [S3], [0], 'G')], S3)
T2 = glue([multi_square_prism(3, [S1, S2], [0, 1], 'A'), multi_square_prism(2, [S2], [0], 'E'), T3], S2)
BRACES["depth-3 chain"] = glue([T2, multi_square_prism(2, [S1], [1], 'B'), multi_square_prism(3, [S1], [0], 'C')], S1)
G = multi_square_prism(4, [S1, S2, S3], [0, 1, 0], 'H')
for t, S in enumerate([S2, S3]):
    G = glue([G, multi_square_prism(2 + t, [S], [t % 2], f'P{t}'), multi_square_prism(2, [S], [0], f'Q{t}')], S)
BRACES["star"] = glue([G, multi_square_prism(3, [S1], [1], 'R1'), multi_square_prism(2, [S1], [0], 'R2')], S1)
d5, ok5 = {}, True
for name, G in BRACES.items():
    p0 = TL.C4[0] if TL.C4[0] in G else S1[0]
    lines = lines_of(G, p0)
    leaves, squares = SY.trisum_tree(G, lines)
    kappa = TW.kasteleyn_tree_signing(leaves)
    own = [sorted(TW.own_edges(*lf), key=str) for lf in leaves]
    rows = collections.Counter()
    bad = []
    signings = [("Kasteleyn", set(kappa))]
    for trial in range(9):
        sign = set(kappa)
        if trial % 3 == 0:
            sign ^= set(rng.sample(own[rng.randrange(len(leaves))], 3))
        elif trial % 3 == 1:
            for i in rng.sample(range(len(leaves)), 2):
                sign ^= set(rng.sample(own[i], 3))
        else:
            for i in range(len(leaves)):
                sign ^= set(rng.sample(own[i], 2))
        signings.append((["local", "two leaves", "global"][trial % 3], sign))
    for kind, sign in signings:
        tw = TW.twisted_branches(leaves, squares, sign, kappa)
        at, tree = TW.tree_structure(leaves, squares)
        branched = any(all(tw[(S, i)] for i in at[S]) for S in squares)
        r = TW.good_root(leaves, squares, tw)
        cnt, rec = TW.evaluate(leaves, squares, lines, sign, r if r is not None else 0)
        H, neg, _, _ = system(G, lines, sign)
        direct = AM.count(H, neg)
        matchgate = all(m == 0 for D, j, k, m in rec)
        good = cnt == direct and (r is None) == branched and (branched or matchgate)
        if kind == "Kasteleyn":
            good &= direct == 0 and not any(tw.values())
        rows[(kind, "branched" if branched else "unbranched", "all junctions matchgate" if matchgate else "some junction off")] += 1
        if not good:
            bad.append((kind, cnt, direct, r, branched))
        ok5 &= good
    d5[name] = {"vertices": G.number_of_nodes(), "planar leaves": len(leaves), "signings": {" / ".join(k): v for k, v in sorted(rows.items())},
                "failures": bad}
report("5 junction networks: exact counts; a good root exists iff no square has three twisted branches, and then all junctions are matchgates",
       ok5, d5)

# ---------------------------------------------------------------- 6 controls
ctrl = {}
ctrl["the similitude's sign depends on the host and other-branch incidence signs (both signs occur)"] = sign_seen == {1, -1}
ctrl["(alpha + beta)^2 is not the multiplier (2, 1: 7 against 9)"] = 2 * 2 + 2 * 1 + 1 != (2 + 1) ** 2
twisted_with_split = sum(1 for name in PAGE_T for F, Ft, u, s in PAGE_T[name] if not u and s is not None)
ctrl["no twisted page has the split form"] = twisted_with_split == 0
ctrl["some branched signing has a junction off the matchgate class"] = any("some junction off" in k for v in d5.values() for k in v["signings"])
report("6 controls fire", all(ctrl.values()), ctrl)

out["ok"] = ok_all
out["seconds"] = round(time.time() - T0, 1)
print("ALL OK" if ok_all else "SOME CHECK FAILED", out["seconds"], "s")
if "--write" in sys.argv:
    json.dump({"schema_version": 1, "artifact_id": "TWIST-COUNT-20261030-001A-P001", "status": "Proved" if ok_all else "Failed",
               "checks": out}, open(os.path.join(HERE, "result.json"), "w"), indent=1, default=str)
sys.exit(0 if ok_all else 1)
