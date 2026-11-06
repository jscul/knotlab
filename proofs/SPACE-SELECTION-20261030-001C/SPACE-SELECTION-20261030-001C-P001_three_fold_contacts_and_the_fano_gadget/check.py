"""Checks for SPACE-SELECTION-20261030-001C-P001 (three-fold contacts: the knot on phases, the Fano gadget, and the corrected interference
bound).

  0 dependency artifacts bound by the hashes recorded in manifest.json
  1 the error in ticket A, Theorem 5: the one-triangle gadget is exact for plain not-all-equal; 'R(000) = 0 iff G + ABC is not 2-colourable'
    fails; the correct identity R_plain(000) = number of proper colourings of G with A = B = C = 0 (all gadgets n <= 4)
  2 the corrected bound: no 2-colourable 3-graph with at most 5 edges (on at most 8 vertices, enough after pruning) forces two vertices equal;
    Fano minus a line forces its three points equal (6 edges); plain not-all-equal exact on no gadget with 2 <= n <= 5 (ticket B)
  3 duality at the knot angle: every three-fold gadget has one base incidence per contact, and its mixed sector sums at zeta = exp(i pi/3)
    equal (-i sqrt3)^(n-1) eps_A eps_B eps_C N*(eps) (all 282 three-fold gadgets with n <= 5 and the 64 Fano gadgets); the knot is exact
    iff the dual is 2-colourable and the dual plus the corner line is not
  4 the Fano gadgets: 64 classes, linear, dual plus corner line a 3-regular non-2-colourable 7-edge 3-graph, exact for the signed knot
    (lambda(0) = 5) and for plain not-all-equal, not generic for the standing wave
  5 controls that must fire
Run: .venv/bin/python -B check.py [--write]   (numpy, sympy; about a minute)"""
import hashlib, itertools, json, os, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
A_DIR = os.path.join(ROOT, "proofs/SPACE-SELECTION-20261030-001A/SPACE-SELECTION-20261030-001A-P001_the_gadget_criterion")
B_RES = os.path.join(ROOT, "proofs/SPACE-SELECTION-20261030-001B/SPACE-SELECTION-20261030-001B-P001_census_of_small_gadgets/result.json")
sys.path.insert(0, HERE)
sys.path.insert(0, A_DIR)
import gadget_lib as G  # noqa: E402
import fano_lib as F  # noqa: E402

T0 = time.time()
out, ok_all = {}, True


def report(key, ok, detail):
    global ok_all
    out[key] = {"ok": bool(ok), "detail": detail}
    ok_all &= bool(ok)
    print(("PASS " if ok else "FAIL ") + key + ": " + json.dumps(detail, default=str)[:2500], flush=True)


# ---------------------------------------------------------------- 0
man = json.load(open(os.path.join(HERE, "manifest.json")))
mism = {r: dg for r, dg in man["parent_bindings"].items()
        if hashlib.sha256(open(os.path.join(ROOT, r), "rb").read()).hexdigest() != dg}
report("0 dependency artifacts bound by hash", not mism, {"parents": len(man["parent_bindings"]), "mismatched": mism})

ALL = {n: [G.complex_of(n, k) for k in sorted(G.gadgets(n))] for n in (1, 3, 4)}

# ---------------------------------------------------------------- 1 the error in ticket A
d1 = {}
one = ALL[1][0]
c1 = G.classify(G.relation_polys(one, 'plain'), 'plain')
d1["one-triangle gadget: plain NAE exact (any law is)"] = G.exact_at(c1, 0)
ident_ok, wrong_red, cnt = True, 0, 0
W0 = G.law_batch('plain', (0,))
for n in (1, 3, 4):
    for cx in ALL[n]:
        R = G.fast_values(cx, W0)[0]
        nv, tris, corners = cx
        inner = [v for v in range(nv) if v not in corners]
        proper0 = 0
        for s in itertools.product((0, 1), repeat=len(inner)):
            col = {0: 0, 1: 0, 2: 0}
            col.update(zip(inner, s))
            if all(not (col[a] == col[b] == col[c]) for a, b, c in tris):
                proper0 += 1
        ident_ok &= int(R[0, 0, 0]) == proper0
        ga = list(tris) + [corners]
        a_says = not F.two_colourable(ga, range(nv))
        wrong_red += int((int(R[0, 0, 0]) == 0) != a_says)
        cnt += 1
d1["R_plain(000) = proper colourings with A = B = C = 0 (gadgets n <= 4)"] = (ident_ok, cnt)
d1["gadgets where 'R(000) = 0' differs from 'G + ABC not 2-colourable' (A's reduction)"] = wrong_red
report("1 ticket A's Theorem 5: the claim misses n = 1 and the proof uses the wrong hypergraph", d1["one-triangle gadget: plain NAE exact (any law is)"]
       and ident_ok and wrong_red > 0, d1)

# ---------------------------------------------------------------- 2 the corrected bound
d2 = {}
NV = 8
cols = [(0,) + c for c in itertools.product((0, 1), repeat=NV - 1)]
FULL = (1 << len(cols)) - 1
tr = list(itertools.combinations(range(NV), 3))
prop = [sum(1 << i for i, c in enumerate(cols) if not (c[a] == c[b] == c[e])) for a, b, e in tr]
pairs = list(itertools.combinations(range(NV), 2))
diff = {p: sum(1 << i for i, c in enumerate(cols) if c[p[0]] != c[p[1]]) for p in pairs}
forcing = 0
for k in range(1, 6):
    for E in itertools.combinations(range(len(tr)), k):
        m = FULL
        for i in E:
            m &= prop[i]
        if m == 0:
            continue
        used = {v for i in E for v in tr[i]}
        if any(p[0] in used and p[1] in used and (m & diff[p]) == 0 for p in pairs):
            forcing += 1
d2["2-colourable 3-graphs with <= 5 edges on 8 vertices forcing a pair equal"] = forcing
fm = [l for l in F.FANO if l != (0, 1, 2)]
cols7 = [(0,) + c for c in itertools.product((0, 1), repeat=6)]
props7 = [c for c in cols7 if all(not (c[a] == c[b] == c[e]) for a, b, e in fm)]
d2["Fano minus a line: 2-colourable, and every proper colouring makes its points 0, 1, 2 equal"] = (
    len(props7) > 0, all(c[0] == c[1] == c[2] for c in props7))
bres = json.load(open(B_RES))["checks"]
cp = bres["5 the cosine wave shares the standing wave's spaces (odd n <= 5); plain not-all-equal has none"]["detail"]
d2["ticket B: plain NAE exact on gadgets with n = 3, 4, 5"] = [cp[k]["plain NAE exact"] for k in ("n=3", "n=4", "n=5")]
report("2 the corrected bound: no nonnegative not-all-equal law is exact for 2 <= n <= 6", forcing == 0 and all(d2["Fano minus a line: 2-colourable, and every proper colouring makes its points 0, 1, 2 equal"])
       and d2["ticket B: plain NAE exact on gadgets with n = 3, 4, 5"] == [0, 0, 0], d2)

# ---------------------------------------------------------------- 3 duality at the knot angle
d3 = {}
G5 = [G.complex_of(5, k) for k in sorted(G.gadgets(5))]
small = [cx for n in (3, 4) for cx in ALL[n] if F.three_fold_odd(cx)] + [cx for cx in G5 if F.three_fold_odd(cx)]
any3 = [cx for n in (3, 4) for cx in ALL[n] if F.three_fold(cx)] + [cx for cx in G5 if F.three_fold(cx)]
any3_exact = sum(1 for cx in any3 if G.exact_at(G.classify(G.relation_polys(cx, 'sine'), 'sine'), 0))
FG = [G.complex_of(7, k) for k in sorted(F.fano_gadgets())]
base_ok, ident, crit_ok = True, True, True
exact_small = 0
for cx in small + FG:
    n = len(cx[1])
    m = G.base_parity(cx)
    base_ok &= all(v == 1 for v in m.values())
    Z = G.sector_sums(cx)
    N = F.nae_counts(cx)
    fac = F.zpow(F.MINUS_I_SQRT3, n - 1)
    for e in Z:
        lhs = F.laurent_at_zeta6(Z[e])
        rhs = (fac[0] * F.corner_sign(cx, e) * N[e], fac[1] * F.corner_sign(cx, e) * N[e])
        ident &= lhs == rhs
    cls = G.classify(G.relation_polys(cx, 'sine'), 'sine')
    knot = G.exact_at(cls, 0)
    dual_says = all(N[e] == 0 for e in N if G.mixed(e)) and N[(1, 1, 1)] > 0
    crit_ok &= knot == dual_says
    if cx in small and knot:
        exact_small += 1
d3["three-fold gadgets with odd base counts, n <= 5"] = len(small)
d3["three-fold gadgets with any base counts, n <= 5: total, exact at the knot (outside the theorem)"] = (len(any3), any3_exact)
d3["odd base counts are all equal to one"] = base_ok
d3["Z(eps) at zeta6 = (-i sqrt3)^(n-1) eps_A eps_B eps_C N*(eps), all eps"] = ident
d3["knot exact <=> dual 2-colourable and forcing equal corner phases (all three-fold gadgets tested)"] = crit_ok
d3["three-fold gadgets with n <= 5 exact at the knot"] = exact_small
report("3 at the knot angle a three-fold gluing is plain not-all-equal on its dual", base_ok and ident and crit_ok and exact_small == 0 and len(small) == 282, d3)

# ---------------------------------------------------------------- 4 the Fano gadgets
d4 = {"Fano gadgets up to isomorphism": len(FG)}
lin_ok, dual_ok, knot_ok, plain_ok, gen_none = True, True, True, True, True
lams = set()
for cx in FG:
    lin_ok &= G.linear(cx)
    lines = F.dual_lines(cx)
    tA, tB, tC = G.corner_triangles(cx)
    H = lines + [tuple(sorted((tA, tB, tC)))]
    deg = {}
    for l in H:
        for p in l:
            deg[p] = deg.get(p, 0) + 1
    dual_ok &= len(H) == 7 and sorted(deg.values()) == [3] * 7 and not F.two_colourable(H, range(7)) and F.two_colourable(lines, range(7))
    cs = G.classify(G.relation_polys(cx, 'sine'), 'sine')
    knot_ok &= G.exact_at(cs, 0)
    lams.add(G.peval(cs[1], 0))
    gen_none &= cs[0] != 'generic'
    cpl = G.classify(G.relation_polys(cx, 'plain'), 'plain')
    plain_ok &= G.exact_at(cpl, 0)
d4["all linear"] = lin_ok
d4["dual plus corner line: 7 edges, 3-regular, not 2-colourable; dual 2-colourable"] = dual_ok
d4["signed knot exact, lambda(0) values"] = (knot_ok, sorted(lams))
d4["plain not-all-equal exact (the corrected bound is sharp)"] = plain_ok
d4["standing wave not generic"] = gen_none
# all role patterns of the Fano gluing (outside the theorem): how many are exact at the knot
allfano, ex_all, ex_odd = set(), 0, 0
for tA, tB, tC in itertools.permutations(F.FANO[0]):
    at_ = {p: [l for l in F.FANO[1:] if p in l] for p in range(7)}
    opts = []
    for p in range(7):
        ls = at_[p]
        if p == tA:
            opts.append([{ls[0]: 1, ls[1]: 2}, {ls[0]: 2, ls[1]: 1}])
        elif p == tB:
            opts.append([{ls[0]: 0, ls[1]: 2}, {ls[0]: 2, ls[1]: 0}])
        elif p == tC:
            opts.append([{ls[0]: 0, ls[1]: 1}, {ls[0]: 1, ls[1]: 0}])
        else:
            opts.append([dict(zip(ls, perm)) for perm in itertools.permutations(range(3))])
    for pick in itertools.product(*opts):
        order = [tA] + [p for p in range(7) if p != tA]
        ti = {p: i for i, p in enumerate(order)}
        key = G.canonical(7, ti[tB], ti[tC], [tuple((ti[p], pick[p][l]) for p in l) for l in F.FANO[1:]])
        if key in allfano:
            continue
        allfano.add(key)
        cxf = G.complex_of(7, key)
        if G.exact_at(G.classify(G.relation_polys(cxf, 'sine'), 'sine'), 0):
            ex_all += 1
            ex_odd += int(F.three_fold_odd(cxf))
d4["every role pattern of the Fano gluing: classes, exact at the knot, of which odd"] = (len(allfano), ex_all, ex_odd)
report("4 the Fano gadgets: the smallest three-fold spaces of the knot, also exact without signs",
       len(FG) == 64 and lin_ok and dual_ok and knot_ok and lams == {5} and plain_ok and gen_none, d4)

# ---------------------------------------------------------------- 5 controls
ctrl = {}
# a Fano gluing with two base incidences on a line (outside the theorem): the identity must fail there
L0, inner = F.FANO[0], F.FANO[1:]
at = {p: [l for l in inner if p in l] for p in range(7)}


def first_gluing(lines, want):
    """a 7-triangle gluing on the given six contact lines (points 0, 1, 2 carry A, B, C) whose base counts satisfy want"""
    at_ = {p: [l for l in lines if p in l] for p in range(7)}
    opts = []
    for p in range(7):
        if p == 0:
            opts.append([{at_[p][0]: 1, at_[p][1]: 2}, {at_[p][0]: 2, at_[p][1]: 1}])
        elif p == 1:
            opts.append([{at_[p][0]: 0, at_[p][1]: 2}, {at_[p][0]: 2, at_[p][1]: 0}])
        elif p == 2:
            opts.append([{at_[p][0]: 0, at_[p][1]: 1}, {at_[p][0]: 1, at_[p][1]: 0}])
        else:
            opts.append([dict(zip(at_[p], perm)) for perm in itertools.permutations(range(3))])
    for pick in itertools.product(*opts):
        if want([sum(1 for p in l if pick[p][l] == 0) for l in lines]):
            return G.complex_of(7, G.canonical(7, 1, 2, [tuple((p, pick[p][l]) for p in l) for l in lines]))


bad = first_gluing(inner, lambda b: 2 in b)
Zb, Nb = G.sector_sums(bad), F.nae_counts(bad)
fac = F.zpow(F.MINUS_I_SQRT3, 6)
ctrl["the duality identity fails when a contact has even base count"] = any(
    F.laurent_at_zeta6(Zb[e]) != (fac[0] * F.corner_sign(bad, e) * Nb[e], fac[1] * F.corner_sign(bad, e) * Nb[e]) for e in Zb)
other = [(0, 3, 4), (0, 5, 6), (1, 3, 5), (1, 4, 6), (2, 3, 4), (2, 5, 6)]
og = first_gluing(other, lambda b: all(x == 1 for x in b))
co = G.classify(G.relation_polys(og, 'sine'), 'sine')
ctrl["an odd three-fold 7-gadget whose dual plus corner line is 2-colourable is not exact at the knot"] = (
    F.three_fold_odd(og) and F.two_colourable(other + [(0, 1, 2)], range(7)) and not G.exact_at(co, 0))
ctrl["the full Fano plane is not 2-colourable, Fano minus a line is"] = (not F.two_colourable(F.FANO, range(7))) and F.two_colourable(fm, range(7))
report("5 controls fire", all(ctrl.values()), ctrl)

out["ok"] = ok_all
out["seconds"] = round(time.time() - T0, 1)
print("ALL OK" if ok_all else "SOME CHECK FAILED", out["seconds"], "s")
if "--write" in sys.argv:
    json.dump({"schema_version": 1, "artifact_id": "SPACE-SELECTION-20261030-001C-P001", "status": "Proved" if ok_all else "Failed",
               "checks": out}, open(os.path.join(HERE, "result.json"), "w"), indent=1, default=str)
sys.exit(0 if ok_all else 1)
