"""Checks for SOFT-CROSS-20261031-001B-P001 (counting under branched twists is #P-hard).

  0 dependency artifacts bound by the hashes recorded in manifest.json
  1 merge paths: on the actual graph, a path of k capped lines between two points, its last line capped onto a free absorber point, acts
    by 2 (3M)^k (k = 1..5)
  2 the absorber: a point closing three lines through three caps is free (factor 2), and each line sees a free colour of its own (3M each)
  3 the reduction: for six formulas, #col(G_k) = 2^(D/3) 9^(kD) p((-1/3)^k) at D + 2 values of k, with p computed from the formula alone;
    D + 1 counts recover every coefficient of p, and p(1) = #formula
  4 the composition: every G_k is an unsigned connected cubic bipartite graph with 10kD + 2D/3 vertices, so SOFT-CROSS A's universality
    applies; in A's instances every junction of a snake with two or more junctions has three twisted branches, and no root is good
  5 controls: D counts leave #formula undetermined; absorbers without caps keep the form but recover a wrong number; the error terms of p
    are nonzero, so no single count suffices
Run: .venv/bin/python -B check.py [--write]   (networkx, numpy, sympy; under a minute)"""
import hashlib, itertools, json, os, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
P = lambda r: os.path.join(ROOT, "proofs", r)  # noqa: E731
for p in (P("THREEFOLD-AMPLITUDE-20261030-001A/THREEFOLD-AMPLITUDE-20261030-001A-P001_five_per_handle_tuttes_number_per_planar_piece"),
          P("THREEFOLD-AMPLITUDE-20261030-001B/THREEFOLD-AMPLITUDE-20261030-001B-P001_the_amplitude_by_computation"),
          P("TWIST-COUNT-20261030-001A/TWIST-COUNT-20261030-001A-P001_the_knots_junction_is_a_similitude"),
          P("SOFT-CROSS-20261031-001A/SOFT-CROSS-20261031-001A-P001_a_soft_crossing_interpolates_to_a_sharp_one"), HERE):
    sys.path.insert(0, p)
import networkx as nx  # noqa: E402
import sympy as sp  # noqa: E402
import amplitude_lib as AM  # noqa: E402
import twist_lib as TW  # noqa: E402
import cross_lib as X  # noqa: E402
import hard_lib as HL  # noqa: E402

T0 = time.time()
out, ok_all = {}, True
M = sp.Matrix([[1, 2], [2, 1]])


def report(key, ok, detail):
    global ok_all
    out[key] = {"ok": bool(ok), "detail": detail}
    ok_all &= bool(ok)
    print(("PASS " if ok else "FAIL ") + key + ": " + json.dumps(detail, default=str)[:3000], flush=True)


# ---------------------------------------------------------------- 0
man = json.load(open(os.path.join(HERE, "manifest.json")))
mism = {r: dg for r, dg in man["parent_bindings"].items()
        if hashlib.sha256(open(os.path.join(ROOT, r), "rb").read()).hexdigest() != dg}
report("0 dependency artifacts bound by hash", not mism, {"parents": len(man["parent_bindings"]), "mismatched": mism})

# ---------------------------------------------------------------- 1 merge paths
d1, ok1 = {}, True
for k in range(1, 6):
    B = X.Builder()
    a, b = ('pt', 'end', 0), ('pt', 'end', 1)
    last = HL.merge_path(B, a, b, k, 'x')
    B.cap(('A', 'x'), last, ('pt', 'absorber', 'x'))
    H, pid = HL.lines(B)
    T = sp.Matrix(2, 2, lambda i, j: AM.count(H, fix={pid[a]: i, pid[b]: j}))
    d1[k] = [list(T.row(0)), list(T.row(1))]
    ok1 &= T == 2 * (3 * M) ** k and (3 * M) ** k == 9 ** k * sp.Matrix([[1, 1], [1, 1]]) / 2 + (-3) ** k * sp.Matrix([[1, -1], [-1, 1]]) / 2
report("1 merge paths act by 2 (3M)^k = 2 (9^k P+ + (-3)^k P-) on the actual graph", ok1, {"transfer matrices": d1})

# ---------------------------------------------------------------- 2 the absorber
B = X.Builder()
ends = [(('pt', 'e', i, 0), ('pt', 'e', i, 1)) for i in range(3)]
lns = []
for i, (a, b) in enumerate(ends):
    li = ('ln', 'w', i)
    B.edge(a, li)
    B.edge(li, b)
    lns.append(li)
HL.absorber(B, lns, 'x')
H, pid = HL.lines(B)
ok2, bad = True, []
for z in itertools.product((0, 1), repeat=6):
    fix = {pid[v]: z[2 * i + s] for i, e in enumerate(ends) for s, v in enumerate(e)}
    want = 2 * 27 * M[z[0], z[1]] * M[z[2], z[3]] * M[z[4], z[5]]
    got = AM.count(H, fix=fix)
    if got != want:
        ok2 = False
        bad.append((z, got, want))
report("2 the absorber is free (factor 2) and each of its three lines acts by 3M", ok2, {"boundary patterns": 64, "mismatches": bad[:5]})

# ---------------------------------------------------------------- 3 the reduction
FORMULAS = {
    "F1": [('a', 'b', 'c'), ('a', 'b', 'b')],
    "F2": [('a', 'b', 'c'), ('a', 'b', 'd'), ('a', 'a', 'd')],
    "F3": [('a', 'b', 'c'), ('b', 'c', 'd'), ('c', 'd', 'a'), ('d', 'a', 'b')],
    "F4 (unsatisfiable)": [('a', 'a', 'a')],
    "F5 (single occurrences)": [('a', 'b', 'c')],
    "F6": [('a', 'b', 'c'), ('c', 'd', 'e'), ('e', 'a', 'b'), ('b', 'd', 'd'), ('a', 'c', 'e')],
}
d3, ok3, COUNTS, POLY = {}, True, {}, {}
for name, F in FORMULAS.items():
    D = 3 * len(F)
    p, t = HL.path_polynomial(F)
    POLY[name] = (p, t)
    counts = {}
    for k in range(2, D + 4):
        H, neg = HL.build(F, k).system()
        counts[k] = AM.count(H, neg)
    COUNTS[name] = counts
    form = all(counts[k] == 2 ** (D // 3) * 9 ** (k * D) * p.eval(sp.Rational(-1, 3) ** k) for k in counts)
    s, c = HL.recover(F, {k: counts[k] for k in range(2, D + 3)})
    coeffs = [p.coeff_monomial(t ** j) for j in range(D + 1)]
    exact = list(c) == coeffs
    truth = HL.count_formula(F)
    d3[name] = {"D": D, "k": [2, D + 3], "largest graph (vertices)": HL.build(F, D + 3).g.number_of_nodes(), "form at every k": form,
                "coefficients recovered": exact, "recovered": str(s), "p(1)": str(p.eval(1)), "#formula": truth}
    ok3 &= form and exact and s == truth == p.eval(1)
report("3 the reduction: counts follow 2^(D/3) 9^(kD) p((-1/3)^k); D + 1 of them recover p and #formula = p(1)", ok3, d3)

# ---------------------------------------------------------------- 4 the composition
d4, ok4 = {"G_k": {}, "A's instances": {}}, True
for name, F in FORMULAS.items():
    D = 3 * len(F)
    for k in (2, 5):
        g = HL.build(F, k)
        pts = {v for v in g.g if X.is_point(v)}
        shape = all(d == 3 for _, d in g.g.degree()) and all((u in pts) != (v in pts) for u, v in g.g.edges()) and not g.neg and \
            nx.is_connected(g.g) and g.g.number_of_nodes() == 10 * k * D + 2 * D // 3
        ok4 &= shape
    d4["G_k"][name] = "unsigned connected cubic bipartite, 10kD + 2D/3 vertices (k = 2, 5)"
for k in (1, 3, 5):
    Bk = X.k33_instance(k, set())
    lv = X.leaves_of(Bk)
    squares = lv[0][1]
    kap = TW.kasteleyn_tree_signing(lv)
    tw = TW.twisted_branches(lv, squares, set(Bk.neg), kap)
    per = [sum(tw[(S, i)] for i in range(len(lv)) if (S, i) in tw) for S in squares]
    root = TW.good_root(lv, squares, tw)
    d4["A's instances"][k] = {"junctions": len(squares), "twisted branches per junction": per, "good root": root}
    if k >= 3:
        ok4 &= all(n == 3 for n in per) and root is None
report("4 the composition: G_k are unsigned cubic bipartite; A's snakes with two or more junctions have branched twists", ok4, d4)

# ---------------------------------------------------------------- 5 controls
ctrl = {}
for name in ("F1", "F3"):
    F = FORMULAS[name]
    D = 3 * len(F)
    rows = sp.Matrix([[sp.Rational(-1, 3) ** (k * j) for j in range(D + 1)] for k in range(2, D + 2)])
    null = rows.nullspace()
    ctrl[f"{name}: D counts leave #formula undetermined"] = len(null) == 1 and sum(null[0]) != 0
    p, t = POLY[name]
    ctrl[f"{name}: the error terms of p are nonzero"] = any(p.coeff_monomial(t ** j) != 0 for j in range(1, D + 1))
    bare = {}
    for k in range(2, D + 4):
        H, neg = HL.build(F, k, capped=False).system()
        bare[k] = AM.count(H, neg)
    s_bare, c_bare = HL.recover(F, {k: bare[k] for k in range(2, D + 3)})
    pred = sum(c_bare[j] * sp.Rational(-1, 3) ** ((D + 3) * j) for j in range(D + 1)) * 2 ** (D // 3) * 9 ** ((D + 3) * D)
    ctrl[f"{name}: absorbers without caps keep the form but recover a wrong number"] = pred == bare[D + 3] and \
        s_bare != HL.count_formula(F)
    ctrl[f"{name}: recovered without caps"] = str(s_bare)
report("5 controls fire", all(v is True for kk, v in ctrl.items() if not kk.endswith("recovered without caps")), ctrl)

out["ok"] = ok_all
out["seconds"] = round(time.time() - T0, 1)
print("ALL OK" if ok_all else "SOME CHECK FAILED", out["seconds"], "s")
if "--write" in sys.argv:
    json.dump({"schema_version": 1, "artifact_id": "SOFT-CROSS-20261031-001B-P001", "status": "Proved" if ok_all else "Failed",
               "checks": out}, open(os.path.join(HERE, "result.json"), "w"), indent=1, default=str)
sys.exit(0 if ok_all else 1)
