"""Checks for HANDLE-COUNT-20261106-001A-P001 (which handles cost: tight cuts are free, junctions are paid for by atoms).

  0 dependency artifacts bound by the hashes recorded in manifest.json
  1 Lemma 1, the Hadamard form at every coupling: a line's weight becomes (-1)^(s.y) [2lam+6, 0, 2lam-2, 0], a point's equality EVEN
  2 Lemma 2, arity three is free: the K4-with-centre gadget realizes every even ternary signature by perfect matchings (symbolic)
  3 Lemma 3, two matchgates: every even 4-ary tensor is M + C with MGI(M) = MGI(C) = 0 (symbolic, and random integer and Gaussian tensors)
  4 Theorem 1 exercised: the brace-and-junction evaluation equals a direct count on trisum braces (Kasteleyn and random signings) and on
    plain three-fold spaces with trisum glue, at lam = 0, 2, -1/2, 1+i; every evaluation splits exactly the junctions that violate MGI
  5 Corollary 1 (lam = 0): with the root of TWIST-COUNT Lemma 5, a junction violates MGI only at or above a square with three twisted
    branches
  6 Theorem 2: end pieces have a face of length 0 mod 4 off their square, negated by every Pfaffian signing; planar braces have >= 6
    squares; in plain spaces every non-Heawood brace's Pfaffian class lives on its contracted vertices; J + p <= a + |sigma| - 2
  7 controls that must fail
Run: .venv/bin/python -B check.py [--write]   (networkx, sympy, python-sat)"""
import hashlib
import itertools
import json
import os
import random
import sys
import time
from fractions import Fraction

import networkx as nx
import sympy as sp

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
for d in ("proofs/THREEFOLD-SPACES-20261030-001A/THREEFOLD-SPACES-20261030-001A-P001_three_fold_spaces_are_built_from_the_fano_plane",
          "proofs/THREEFOLD-GRAMMAR-20261030-001A/THREEFOLD-GRAMMAR-20261030-001A-P001_fano_leaves_and_planar_glue",
          "proofs/SEYMOUR-COUNT-20261030-001B/SEYMOUR-COUNT-20261030-001B-P001_polynomial_counting_on_seymours_cubic_bound",
          "proofs/TWIST-COUNT-20261030-001A/TWIST-COUNT-20261030-001A-P001_the_knots_junction_is_a_similitude"):
    sys.path.insert(0, os.path.join(ROOT, d))
sys.path.insert(0, HERE)
import grammar_lib as M  # noqa: E402
import seymour_lib as SL  # noqa: E402
import twist_lib as TW  # noqa: E402
import junction_lib as JL  # noqa: E402
import families as FA  # noqa: E402

T0 = time.time()
OUT = {}
OK_ALL = True


def report(name, ok, detail):
    global OK_ALL
    OK_ALL &= bool(ok)
    OUT[name] = {"ok": bool(ok), "detail": detail}
    print(("PASS " if ok else "FAIL ") + name, flush=True)


def colourable_signed(H, negs):
    from pysat.solvers import Solver
    neg = set(map(tuple, negs))
    with Solver(name='cadical153') as s:
        for i, l in enumerate(H):
            lits = [(p + 1) * (-1 if (i, p) in neg else 1) for p in l]
            s.add_clause(lits)
            s.add_clause([-x for x in lits])
        return s.solve()


# ---------------------------------------------------------------- 0
man = json.load(open(os.path.join(HERE, "manifest.json")))
mism = {r: dg for r, dg in man["parent_bindings"].items()
        if hashlib.sha256(open(os.path.join(ROOT, r), "rb").read()).hexdigest() != dg}
report("0 dependency artifacts bound by hash", not mism, {"parents": len(man["parent_bindings"]), "mismatched": mism})

# ---------------------------------------------------------------- 1 the Hadamard form
lam = sp.Symbol('lam')
ok1, d1 = True, {}
for s in itertools.product((0, 1), repeat=3):
    for y in itertools.product((0, 1), repeat=3):
        tot = 0
        for x in itertools.product((0, 1), repeat=3):
            v = [a ^ b for a, b in zip(x, s)]
            w = lam if v[0] == v[1] == v[2] else 1
            tot += w * (-1) ** sum(a * b for a, b in zip(x, y))
        want = (-1) ** sum(a * b for a, b in zip(s, y)) * {0: 2 * lam + 6, 1: 0, 2: 2 * lam - 2, 3: 0}[sum(y)]
        ok1 &= sp.expand(tot - want) == 0
for dgr in (1, 2, 3, 4):
    for y in itertools.product((0, 1), repeat=dgr):
        tot = sum((-1) ** sum(a * b for a, b in zip(x, y)) for x in ((0,) * dgr, (1,) * dgr))
        ok1 &= tot == (2 if sum(y) % 2 == 0 else 0)
d1["line"] = "w_lam(x xor s) -> (-1)^(s.y) [2lam+6, 0, 2lam-2, 0], all 8 sign patterns"
d1["points"] = "equality on d legs -> 2 EVEN_d, d = 1..4"
d1["u"] = "ratio (lam-1)/(lam+3); lam = 0 gives -1/3 (the knot's law), lam = -3 a pole (the dimer law)"
report("1 Lemma 1: the Hadamard form at every coupling and signing (symbolic)", ok1, d1)

# ---------------------------------------------------------------- 2 arity three is free
f000, u1, u2, u3 = sp.symbols('f000 u1 u2 u3', nonzero=True)
# K4 gadget: external nodes 1, 2, 3 (a triangle, weights w23, w13, w12) and a centre c joined by spokes u1, u2, u3
w23, w13, w12 = f000 / (3 * u1), f000 / (3 * u2), f000 / (3 * u3)
E = {frozenset((1, 2)): w12, frozenset((1, 3)): w13, frozenset((2, 3)): w23,
     frozenset((1, 'c')): u1, frozenset((2, 'c')): u2, frozenset((3, 'c')): u3}


def perfmatch(nodes):
    nodes = sorted(nodes, key=str)
    if not nodes:
        return sp.Integer(1)
    if len(nodes) % 2:
        return sp.Integer(0)
    a = nodes[0]
    tot = sp.Integer(0)
    for b in nodes[1:]:
        e = frozenset((a, b))
        if e in E:
            tot += E[e] * perfmatch([v for v in nodes if v not in (a, b)])
    return tot


gad = {}
for z in itertools.product((0, 1), repeat=3):
    keep = [k for k, b in zip((1, 2, 3), z) if not b] + ['c']
    gad[z] = sp.simplify(perfmatch(keep))
want2 = {(0, 0, 0): f000, (0, 1, 1): u1, (1, 0, 1): u2, (1, 1, 0): u3}
ok2 = all(sp.simplify(gad[z] - want2.get(z, 0)) == 0 for z in gad)
report("2 Lemma 2: every even ternary signature [f000, f011, f101, f110] with nonzero f011, f101, f110 is the perfect-matching signature "
       "of a planar K4-with-centre gadget (symbolic); degenerate cases are classical (Valiant; Cai-Gorenstein)", ok2,
       {"gadget": {str(z): str(v) for z, v in gad.items()}})

# ---------------------------------------------------------------- 3 two matchgates
syms = sp.symbols('h0000 h1111 h1100 h0011 h1010 h0101 h1001 h0110')
names = ['0000', '1111', '1100', '0011', '1010', '0101', '1001', '0110']
ok3, d3 = True, {}
for anchor in range(8):
    hat = {tuple(int(c) for c in nm): s for nm, s in zip(names, syms)}
    # make the anchor the only entry guaranteed nonzero: the split solves for its complementary entry
    a = tuple(int(c) for c in names[anchor])
    b = tuple(1 - c for c in a)
    pair = next(p for p in JL.PAIRS if a in p[:2])
    Mh = dict(hat)
    Mh[b] = 0
    rest = JL.mgi(Mh)
    Mh[b] = -rest / (pair[2] * hat[a])
    ok3 &= sp.simplify(JL.mgi(Mh)) == 0
r3 = random.Random(3)
cnt = 0
for trial in range(4000):
    hat = {}
    for nm in names:
        z = tuple(int(c) for c in nm)
        if r3.random() < 0.3:
            continue
        hat[z] = r3.randint(-9, 9) if trial % 2 else JL.GQ(r3.randint(-5, 5), r3.randint(-5, 5))
    if not any(bool(v) for v in hat.values()):
        continue
    Mh, Ch = JL.split_hat(hat)
    same = all(Mh.get(z, 0) + Ch.get(z, 0) == hat.get(z, 0) for z in set(hat) | set(Mh) | set(Ch))
    ok3 &= same and not JL.mgi(Mh) and not JL.mgi(Ch) and sum(1 for v in Ch.values() if v) <= 1
    cnt += 1
d3["symbolic"] = "for each of the 8 entries as anchor, solving MGI for the complementary entry gives MGI(M) = 0 identically"
d3["random"] = f"{cnt} random even tensors (integer and Gaussian, about 30% zero entries): M + C = hat, MGI(M) = MGI(C) = 0, C one entry"
report("3 Lemma 3: every even 4-ary tensor is the sum of two matchgate signatures", ok3, d3)

# ---------------------------------------------------------------- 4 Theorem 1 exercised
LAMS = [0, 2, Fraction(-1, 2), JL.GQ(1, 1)]
pool = FA.planar_pool()
braces = []
for seed in range(1, 13):
    G = FA.trisum_brace(seed, 1 + seed % 3, pool)
    H, kap, nsq = FA.pfaffian_signing(G)
    braces.append((seed, G, H, kap, nsq))
ok4, d4 = True, {"trisum braces": [], "plain spaces": []}
r4 = random.Random(4)
for seed, G, H, kap, nsq in braces:
    row = {"seed": seed, "points": len(H), "junctions": nsq, "lam": {}}
    ok4 &= not colourable_signed(H, kap)                       # the glued Kasteleyn signing is Pfaffian: not colourable
    rnd = [(i, p) for i, l in enumerate(H) for p in l if r4.random() < 0.2]
    for name, sg in (("Kasteleyn", kap), ("random", rnd)):
        for lm in LAMS:
            d = JL.direct_count(H, sg, lm)
            v, rep = JL.count_by_braces(H, sg, lm)
            recs = [x for rr in rep["trisum records"] for x in rr]
            okr = d == v and all(nev == 2 ** bad for _, hosted, bad, nev in recs) and rep["ternary tensors even"]
            ok4 &= okr
            row["lam"][f"{name} {lm}"] = {"count": JL.num_json(v), "violating junctions": sum(b for _, h, b, n in recs),
                                          "hosted": sum(h for _, h, b, n in recs), "evaluations": sum(n for *_, n in recs), "ok": okr}
    d4["trisum braces"].append(row)
CORE35 = [(0, 1, 2), (0, 1, 3), (0, 4, 5), (1, 6, 7), (2, 6, 8), (2, 7, 9), (3, 4, 6), (3, 5, 7), (4, 8, 8), (5, 9, 9)]
plain = [("CORE35 decorated (THREEFOLD-SURFACES B, 35 points)", M.decorate(CORE35, [(0, 0)]))]
for seed in (1, 4):
    G = FA.trisum_brace(seed, 1, pool)
    H, kap, nsq = FA.pfaffian_signing(G)
    plain.append((f"trisum brace seed {seed} decorated", M.decorate(H, kap)))
for name, H in plain:
    ok4 &= not colourable_signed(H, [])
    row = {"space": name, "points": len(H), "lam": {}}
    for lm in (0, 2, JL.GQ(1, 1)):
        d = JL.direct_count(H, [], lm)
        v, rep = JL.count_by_braces(H, [], lm)
        recs = [x for rr in rep["trisum records"] for x in rr]
        okr = d == v and all(nev == 2 ** bad for _, hosted, bad, nev in recs) and rep["ternary tensors even"]
        if lm == 0:
            okr &= d == 0 and all(bad == 0 for _, h, bad, n in recs)    # the knot's law on its own space: every junction a matchgate
        ok4 &= okr
        row["lam"][str(lm)] = {"count": JL.num_json(v), "braces": dict(rep["braces"]), "junctions": rep["junctions"],
                               "violating": sum(b for _, h, b, n in recs), "ok": okr}
    d4["plain spaces"].append(row)
report("4 Theorem 1: brace-and-junction evaluation = direct count (12 trisum braces x 2 signings x 4 couplings; 3 plain spaces x 3 "
       "couplings), each piece evaluated 2^(violating junctions) times, ternary tensors even", ok4, d4)

# ---------------------------------------------------------------- 5 Corollary 1 at lam = 0
r5 = random.Random(5)
st5 = {"signings": 0, "violations": 0, "at or above a branched square": 0, "unexplained": 0, "counts equal": 0}
for seed, G, H, kap, nsq in braces:
    g = JL.labelled(H)
    sgr = JL.simple_graph(g)
    tree = SL.trisum_tree(sgr, {v for v in sgr if v[0] == 'L'})
    leaves, squares = tree
    kappa = TW.kasteleyn_tree_signing(leaves)
    at, ttree = TW.tree_structure(leaves, squares)
    for rep_ in range(4):
        sign = kappa ^ {frozenset(e) for e in sgr.edges() if r5.random() < 0.2}
        tw = TW.twisted_branches(leaves, squares, sign, kappa)
        branched = {S for S in squares if all(tw[(S, i)] for i in at[S])}
        D2 = [S for S in squares if sum(tw[(S, i)] for i in at[S]) == 2]
        root = next(i for i in at[D2[0]] if tw[(D2[0], i)]) if D2 else 0
        signset = set()
        for e in sign:
            a, b = tuple(e)
            l, p = (a, b) if a[0] == 'L' else (b, a)
            signset.add((l[1], p[1]))
        val, recs, ns, npc = JL.trisum_eval(g, lambda v: JL.vertex_factor(g, v, signset, 0, {}), root=root, tree=tree)
        jm = JL.trisum_eval.last_junction_mgi
        st5["signings"] += 1
        st5["counts equal"] += JL.direct_count(H, signset, 0) == val
        for D, m in jm.items():
            if not m:
                continue
            st5["violations"] += 1
            closed = [i for i in at[D] if root not in TW.branch_leaves(ttree, D, i)]
            below = set()
            for i in closed:
                for k in TW.branch_leaves(ttree, D, i):
                    below |= {S2 for S2 in leaves[k][1] if S2 != D}
            if D in branched or below & branched:
                st5["at or above a branched square"] += 1
            else:
                st5["unexplained"] += 1
ok5 = st5["unexplained"] == 0 and st5["counts equal"] == st5["signings"] and st5["violations"] > 0
report("5 Corollary 1 (lam = 0): from the root of TWIST-COUNT Lemma 5 a junction violates MGI only at or above a square with three twisted "
       "branches", ok5, st5)

# ---------------------------------------------------------------- 6 Theorem 2
ok6, d6 = True, {}
st6a = {"end pieces": 0, "with a far face 0 mod 4": 0, "far face odd under 6 Pfaffian signings each": 0, "planar pieces": 0,
        "pieces with >= 6 squares": 0}
r6 = random.Random(6)
for seed, G, H, kap, nsq in braces:
    lines = {v for v in G if nx.bipartite.color(G)[v] == 1}
    leaves, squares = SL.trisum_tree(G, lines)
    kappa = TW.kasteleyn_tree_signing(leaves)
    sigs = [kappa]
    for _ in range(5):                                      # switchings of a Pfaffian signing are Pfaffian
        U = {v for v in G if r6.random() < 0.5}
        sigs.append(kappa ^ {frozenset(e) for e in G.edges() if (e[0] in U) != (e[1] in U)})
    for h, sqs in leaves:
        fs = FA.faces_of(h)
        st6a["planar pieces"] += 1
        st6a["pieces with >= 6 squares"] += sum(1 for f in fs if len(f) == 4) >= 6
        if len(sqs) != 1:
            continue
        S = sqs[0]
        sqe = {frozenset((S[j], S[(j + 1) % 4])) for j in range(4)}
        st6a["end pieces"] += 1
        far = [f for f in fs if len(f) % 4 == 0 and not ({frozenset((f[j], f[(j + 1) % len(f)])) for j in range(len(f))} & sqe)]
        if far:
            st6a["with a far face 0 mod 4"] += 1
            f = far[0]
            fe = {frozenset((f[j], f[(j + 1) % len(f)])) for j in range(len(f))}
            st6a["far face odd under 6 Pfaffian signings each"] += all(len(fe & s) % 2 == 1 for s in sigs)
ok6 &= st6a["end pieces"] == st6a["with a far face 0 mod 4"] == st6a["far face odd under 6 Pfaffian signings each"] > 0
ok6 &= st6a["planar pieces"] == st6a["pieces with >= 6 squares"]
d6["end pieces and planar pieces"] = st6a
rows = []
for seed, G, H, kap, nsq in braces:
    a, p, js, kinds = JL.structure(H)
    rows.append({"system": f"trisum brace seed {seed}", "a": a, "p": p, "J": sum(js), "|sigma|": len(kap),
                 "holds": sum(js) + p <= a + len(kap) - 2})
st6c = []
for name, H in plain:
    a, p, js, kinds = JL.structure(H)
    rows.append({"system": name, "a": a, "p": p, "J": sum(js), "|sigma|": 0, "holds": sum(js) + p <= a - 2})
    # every non-Heawood brace: its Pfaffian class restricted to edges between genuine vertices is a cut, and it has enough contracted
    # vertices (>= j + 2 for a trisum brace, >= 3 for a planar one), every end piece meeting one
    for b in JL.decompose(JL.labelled(H)):
        t = JL.brace_kind(b)
        if t not in ('planar', 'other'):
            continue
        sg = JL.simple_graph(b)
        if t == 'planar':
            lv, sq = [(sg, [])], []
        else:
            lv, sq = SL.trisum_tree(sg, {v for v in sg if M.kind(v) == 'L'})
        kap_b = TW.kasteleyn_tree_signing(lv)
        gen = [frozenset(e) for e in sg.edges() if e[0][0] != 'X' and e[1][0] != 'X']
        cut = TW.coboundary(gen, {e for e in gen if e in kap_b})
        ncon = sum(1 for v in b if v[0] == 'X')
        need = len(sq) + 2 if t == 'other' else 3
        ends_meet = all(any(v[0] == 'X' for v in h) for h, s in lv if len(s) == 1)
        st6c.append({"space": name, "brace": t, "junctions": len(sq), "contracted": ncon, "class on contracted vertices": cut,
                     "contracted >= need": ncon >= need, "end pieces meet a contracted vertex": ends_meet})
ok6 &= all(r["holds"] for r in rows)
ok6 &= all(r["class on contracted vertices"] and r["contracted >= need"] and r["end pieces meet a contracted vertex"] for r in st6c)
d6["J + p <= a + |sigma| - 2"] = rows
d6["plain spaces: braces"] = st6c
report("6 Theorem 2: end-piece lemma, >= 6 squares per planar piece, Pfaffian classes of plain spaces live on contracted vertices, "
       "J + p <= a + |sigma| - 2", ok6, d6)

# ---------------------------------------------------------------- 6b sharpness
d6b = []
cube_pool = {'cube': pool['cube']}
C4 = [('c', 0), ('c', 1), ('c', 2), ('c', 3)]
sharp = [("trisum of three cubes", M.trisum([M.cube_on(C4, t) for t in ('q', 'r', 's')], C4, [(C4[j], C4[(j + 1) % 4]) for j in range(4)]))]
sharp += [(f"cube trisums, seed {sd}", FA.trisum_brace(sd, 1 + sd % 3, cube_pool)) for sd in (1, 2)]
ok6b = True
for name, G in sharp:
    Hg, kap, j = FA.pfaffian_signing(G)
    mn, nu = FA.min_signing(Hg, kap)
    D = FA.edge_atoms(Hg, mn)
    a, p, js, kinds = JL.structure(D)
    nonc = not colourable_signed(D, [])
    ok6b &= nonc and a == nu and sum(js) == j and p == 0 and nu >= j + 2
    d6b.append({"glue": name, "junctions": j, "fewest signs": nu, "space points": len(D), "not colourable": nonc, "a": a, "p": p,
                "J": sum(js), "J + p = a - 2": sum(js) + p == a - 2})
ok6b &= d6b[0]["J + p = a - 2"]
report("6b sharpness: a Fano atom on each sign of a fewest-sign Pfaffian signing gives a plain three-fold space with a = fewest signs; "
       "for the trisum of three cubes J + p = a - 2 exactly", ok6b, d6b)

# ---------------------------------------------------------------- 7 controls
c = {}
hat = {(0, 0, 0, 0): 3, (1, 1, 1, 1): 5, (1, 1, 0, 0): 2, (0, 0, 1, 1): 7, (1, 0, 1, 0): 1, (0, 1, 0, 1): 4, (1, 0, 0, 1): 6, (0, 1, 1, 0): 2}
Mh = dict(hat)
Mh[(1, 1, 1, 1)] = 0
rest = JL.mgi(Mh)
Mh[(1, 1, 1, 1)] = JL.div(rest, 3)                      # wrong sign of the correction
c["wrong split sign leaves MGI != 0"] = JL.mgi(Mh) != 0
seed, G, H, kap, nsq = braces[0]
v_ok, rep = JL.count_by_braces(plain[0][1], [], 2)
orig = JL.vertex_factor
def scrambled(g, v, sign, lm, tensors):
    e, t = orig(g, v, sign, lm, tensors)
    if v[0] == 'X':
        return e[::-1], t                               # the right table on the wrong edge order
    return e, t
JL.vertex_factor = scrambled
try:
    v_bad, _ = JL.count_by_braces(plain[0][1], [], 2)
except AssertionError:
    v_bad = None
JL.vertex_factor = orig
c["mis-ordered contracted tensors change the count"] = v_bad != v_ok
a, p, js, kinds = JL.structure(H)
c["signs ignored: J + p <= a - 2 fails on a signed trisum brace"] = not (sum(js) + p <= a - 2)
lv, sq = SL.trisum_tree(G, {v for v in G if nx.bipartite.color(G)[v] == 1})
kappa = TW.kasteleyn_tree_signing(lv)
endp = next((h, s) for h, s in lv if len(s) == 1)
S = endp[1][0]
sqe = {frozenset((S[j], S[(j + 1) % 4])) for j in range(4)}
f = next(f for f in FA.faces_of(endp[0]) if len(f) % 4 == 0 and not ({frozenset((f[j], f[(j + 1) % len(f)])) for j in range(len(f))} & sqe))
fe = [frozenset((f[j], f[(j + 1) % len(f)])) for j in range(len(f))]
bad_sig = kappa ^ {fe[0]}
c["one extra negation on a far face makes it even (not Pfaffian)"] = len(set(fe) & bad_sig) % 2 == 0
Hb, pid, lid = FA.system(G)
negs = []
for e in bad_sig:
    x, y = tuple(e)
    l, pt = (x, y) if x in lid else (y, x)
    negs.append((lid[l], pid[pt]))
c["... and the system becomes colourable"] = colourable_signed(Hb, negs)
ok7 = all(c.values())
report("7 controls: a wrong split, mis-ordered tensors, ignored signs and a non-Pfaffian signing are all caught", ok7, c)

res = {"schema_version": 1, "artifact_id": "HANDLE-COUNT-20261106-001A-P001", "status": "passed" if OK_ALL else "failed",
       "checks": OUT, "seconds": round(time.time() - T0, 1)}
print("all ok" if OK_ALL else "SOME CHECK FAILED", res["seconds"], "s")
if "--write" in sys.argv:
    with open(os.path.join(HERE, "result.json"), "w") as fh:
        json.dump(res, fh, indent=1, default=str)
