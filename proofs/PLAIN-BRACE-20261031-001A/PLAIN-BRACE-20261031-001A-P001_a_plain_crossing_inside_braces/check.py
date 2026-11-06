"""Checks for PLAIN-BRACE-20261031-001A-P001 (a plain crossing inside braces).

  0 dependency artifacts bound by the hashes recorded in manifest.json
  1 the cube junction: every labelling of a cube page gives one tensor; S' = N W is nonsingular with characteristic polynomial
    (x^2 - 19x - 1)(x^2 + 7x + 13) and distinct squared eigenvalues
  2 the site is a matrix power: direct counts of the K3,3 instances (k = 1..7 junctions) equal sum R (S'^k), R the rest of K3,3
  3 the lattice condition: (19 + sqrt 365)/2 is a unit of norm -1 and no root of unity; (-7 + i sqrt 3)/2 has norm 13 and its
    quotient by its conjugate is no root of unity; the squared eigenvalue products are distinct for every count vector of total <= 8
  4 recovery: #col(K3,3) = 6 from the counts at k = 1, 3, 5, 7, by an exact rational formula (and by the algebraic Vandermonde solve)
  5 the instances (k = 1, 3, 5, 7): plain, cubic bipartite, certified Pfaffian, non-planar, host planar and cyclically 4-edge-connected,
    three twisted branches at every junction, no good root; braces by the direct test (k <= 5); for even k the site makes no net crossing
    and the host is not planar
  6 controls: a single plain cube junction is not a crossing; three counts cannot give the identity; the plain ladder steps of a family
    of pages (cube, prisms, truncated octahedron) are nonsingular and each generates a 4-dimensional commutative algebra. Observations:
    the unreversed site (cap replaced by a rung) also spans the exact crossing; pairs of steps of this family generate 6 dimensions
Run: .venv/bin/python -B check.py [--write]   (networkx, numpy, sympy, mpmath)"""
import hashlib, itertools, json, os, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
P = lambda r: os.path.join(ROOT, "proofs", r)  # noqa: E731
for p in (P("THREEFOLD-AMPLITUDE-20261030-001A/THREEFOLD-AMPLITUDE-20261030-001A-P001_five_per_handle_tuttes_number_per_planar_piece"),
          P("THREEFOLD-AMPLITUDE-20261030-001B/THREEFOLD-AMPLITUDE-20261030-001B-P001_the_amplitude_by_computation"),
          P("TWIST-COUNT-20261030-001A/TWIST-COUNT-20261030-001A-P001_the_knots_junction_is_a_similitude"),
          P("SOFT-CROSS-20261031-001A/SOFT-CROSS-20261031-001A-P001_a_soft_crossing_interpolates_to_a_sharp_one"),
          P("PLAIN-COUNT-20261031-001A/PLAIN-COUNT-20261031-001A-P001_signs_interpolate_away"),
          P("PLAIN-COUNT-20261031-001B/PLAIN-COUNT-20261031-001B-P001_plain_pages_are_always_twisted"), HERE):
    sys.path.insert(0, p)
import networkx as nx  # noqa: E402
import sympy as sp  # noqa: E402
import mpmath  # noqa: E402
import amplitude_lib as AM  # noqa: E402
import twist_lib as TW  # noqa: E402
import cross_lib as X  # noqa: E402
import computation_lib as CL  # noqa: E402
import plain_lib as PL  # noqa: E402
import page_lib as PG  # noqa: E402
import brace_lib as BL  # noqa: E402

T0 = time.time()
out, ok_all = {}, True
x = sp.Symbol('x')


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

# ---------------------------------------------------------------- 1 the cube junction
col = nx.bipartite.color(BL.CUBE)
tensors = set()
for f in BL.faces(BL.CUBE):
    for ff in (list(f), list(reversed(f))):
        for st in range(4):
            lab = tuple(ff[st:] + ff[:st])
            if col[lab[0]] == 0:
                tensors.add(tuple(BL.page_tensor(BL.CUBE, lab).flatten()))
W, N = BL.matrices()
S = N * W
cp = sp.factor(S.charpoly(x).as_expr())
ev = list(S.eigenvals())
sq = {sp.expand(e ** 2) for e in ev}
ok1 = len(tensors) == 1 and S.rank() == 4 and sp.expand(cp - (x ** 2 - 19 * x - 1) * (x ** 2 + 7 * x + 13)) == 0 and len(ev) == 4 and len(sq) == 4
report("1 the cube junction: one tensor, S' = N W nonsingular, characteristic polynomial (x^2 - 19x - 1)(x^2 + 7x + 13)", ok1,
       {"distinct cube page tensors": len(tensors), "S' (colour basis)": S.tolist(), "characteristic polynomial": str(cp),
        "eigenvalues": [str(sp.simplify(e)) for e in ev]})

# ---------------------------------------------------------------- 2 the site is a matrix power
R = BL.k33_rest()
Z, d2, ok2 = {}, {}, True
for k in range(1, 8):
    Bk = BL.k33_instance(k)
    Z[k] = AM.count(*Bk.system())
    Sk = S ** k
    pred = sum(R[(a, b, c, d)] * Sk[BL.ST.index((a, b)), BL.ST.index((c, d))] for a, b, c, d in itertools.product((0, 1), repeat=4))
    d2[k] = {"vertices": Bk.g.number_of_nodes(), "direct count": Z[k], "sum R (S'^k)": int(pred)}
    ok2 &= pred == Z[k]
report("2 the site acts by S'^k: direct counts of K3,3 instances equal the prediction (k = 1..7)", ok2, d2)

# ---------------------------------------------------------------- 3 the lattice condition
eps = (19 + sp.sqrt(365)) / 2
pi_ = (-7 + sp.I * sp.sqrt(3)) / 2
pib = sp.conjugate(pi_)
cert = {"eps * conj(eps) = -1": sp.expand(eps * (19 - sp.sqrt(365)) / 2) == -1, "eps > 1": bool(eps > 1),
        "pi * conj(pi) = 13 (a prime)": sp.expand(pi_ * pib) == 13 and sp.isprime(13),
        "(pi / conj(pi))^6 != 1": sp.simplify(sp.expand((pi_ / pib) ** 6) - 1) != 0,
        "eigenvalues are eps, -1/eps, pi, conj(pi)": {sp.simplify(e) for e in ev} == {sp.simplify(eps), sp.simplify(-1 / eps),
                                                                                       sp.simplify(pi_), sp.simplify(pib)}}
mpmath.mp.dps = 60
lam = [mpmath.mpf(19) / 2 + mpmath.sqrt(365) / 2, mpmath.mpf(19) / 2 - mpmath.sqrt(365) / 2,
       mpmath.mpc(-7, mpmath.sqrt(3)) / 2, mpmath.mpc(-7, -mpmath.sqrt(3)) / 2]
distinct = {}
for m in range(1, 9):
    vals = []
    for n in itertools.product(range(m + 1), repeat=4):
        if sum(n) == m:
            v = mpmath.mpc(1)
            for l_, e in zip(lam, n):
                v *= l_ ** (2 * e)
            vals.append(v)
    distinct[m] = all(abs(a - b) > mpmath.mpf(10) ** -30 * max(1, abs(a)) for a, b in itertools.combinations(vals, 2))
ok3 = all(cert.values()) and all(distinct.values())
report("3 the lattice condition: algebraic certificate, and distinct squared products for totals <= 8", ok3,
       {**{k: bool(v) for k, v in cert.items()}, "distinct for total m": distinct})

# ---------------------------------------------------------------- 4 recovery
f = sp.symbols('f0:4')
h = sp.symbols('h0:4')
g = x * sum(f[j] * x ** (2 * j) for j in range(4)) - 1 - (x ** 2 - 19 * x - 1) * (x ** 2 + 7 * x + 13) * sum(h[j] * x ** j for j in range(4))
sol = sp.solve(sp.Poly(sp.expand(g), x).all_coeffs(), list(f) + list(h), dict=True)[0]
coef = [sol[f[j]] for j in range(4)]
exact = sum(coef[j] * Z[2 * j + 1] for j in range(4))
Mx = sp.Matrix([[e ** k for e in ev] for k in (1, 3, 5, 7)])
alg = sp.nsimplify(sp.simplify(sum(Mx.LUsolve(sp.Matrix([Z[k] for k in (1, 3, 5, 7)])))))
target = AM.count(*X.k33_system(set()))
ok4 = exact == target == alg and all(c.is_rational for c in coef)
report("4 recovery: #col(K3,3) = sum_j f_j Z(2j+1), with x f(x^2) = 1 mod the characteristic polynomial", ok4,
       {"rational coefficients f_0..f_3": [str(c) for c in coef], "recovered": str(exact), "algebraic Vandermonde": str(alg),
        "#col(K3,3)": target})

# ---------------------------------------------------------------- 5 the instances
d5, ok5 = {}, True
for k in (1, 3, 5, 7):
    Bk = BL.k33_instance(k)
    H, neg = Bk.system()
    bip = all(X.is_point(a) != X.is_point(b) for a, b in Bk.g.edges())
    good, lv, kap = PL.certify(Bk, TW, AM)
    host = lv[0][0]
    sqs = lv[0][1]
    tw = TW.twisted_branches(lv, sqs, set(), kap)
    per = [sum(tw[(S_, i)] for i in range(len(lv)) if (S_, i) in tw) for S_ in sqs]
    root = TW.good_root(lv, sqs, tw)
    brace = PG.is_brace(Bk.g) if k <= 5 else None
    rec = {"vertices": Bk.g.number_of_nodes(), "signs": len(neg), "certified Pfaffian": good, "non-planar": not nx.check_planarity(Bk.g)[0],
           "host cyclically 4-edge-connected": nx.check_planarity(host)[0] and BL.cyclic4(host), "twisted branches": per, "good root": root,
           "brace (direct test)": brace}
    d5[k] = rec
    ok5 &= not neg and bip and good and rec["non-planar"] and rec["host cyclically 4-edge-connected"] and all(n == 3 for n in per) \
        and root is None and brace is not False
even = {k: nx.check_planarity(PL.leaves(BL.k33_instance(k))[0][0])[0] for k in (2, 4, 6)}
d5["host planar for even k (no net crossing)"] = even
ok5 &= not any(even.values())
report("5 the instances (odd k): plain Pfaffian braces with three twisted branches at every junction; even k leaves the host non-planar",
       ok5, d5)

# ---------------------------------------------------------------- 6 controls
ctrl = {}
Rr = {(a, b, c, d): R[(a, d, c, b)] for a, b, c, d in itertools.product((0, 1), repeat=4)}   # (x_A, x_B, s_A, s_B) of the unreversed site


def phi(k):
    """unreversed site: x_A = P2, x_B = P0 (wire B enters at c1), s_A seen by L0, s_B = pi_e seen by L1"""
    G = W * (N * W) ** (k - 1)
    return {(a, b, c, d): sum(BL.nae(a, z, d) * G[BL.ST.index((z, b)), BL.ST.index((c, d))] for z in (0, 1))
            for a, b, c, d in itertools.product((0, 1), repeat=4)}


consistent = all(AM.count(*BL.k33_instance(k, unreversed=True).system()) ==
                 sum(Rr[s] * phi(k)[s] for s in Rr) for k in (1, 2, 3))
keys = sorted(Rr)
span = sp.Matrix([[phi(k)[s_] for s_ in keys] for k in range(1, 9)])
tgt = sp.Matrix([[1 if (s_[2] == s_[0] and s_[3] == s_[1]) else 0 for s_ in keys]])
observations = {"the unreversed site's counts match its tensor (k = 1, 2, 3)": consistent,
                "the unreversed site also spans the exact crossing": span.rank() == sp.Matrix.vstack(span, tgt).rank()}
Wt = TW.junction(BL.page_tensor(), BL.page_tensor(), (0, 0, 0), (0, 0, 0))
Wh = X.hada(Wt)
ctrl["a single plain cube junction is not a crossing (nonzero turning entries)"] = any(Wh[t_] != 0 for t_ in X.TURNING)
sol3 = sp.solve(sp.Poly(sp.expand(g.subs(f[3], 0)), x).all_coeffs(), list(f[:3]) + list(h), dict=True)
ctrl["three counts cannot give the identity (no solution with f_3 = 0)"] = sol3 == []
fam = {"cube": BL.CUBE, "6-prism": nx.circular_ladder_graph(6), "8-prism": nx.circular_ladder_graph(8),
       "truncated octahedron": nx.convert_node_labels_to_integers(CL.omnitruncation(nx.complete_graph(4)), ordering="sorted")}
pages = {}
for name, gg in fam.items():
    gg = nx.convert_node_labels_to_integers(gg, ordering="sorted")
    cg = nx.bipartite.color(gg)
    for f_ in BL.faces(gg):
        if len(f_) != 4:
            continue
        for ff in (list(f_), list(reversed(f_))):
            for st in range(4):
                lab = tuple(ff[st:] + ff[:st])
                if cg[lab[0]] == 0:
                    F_ = BL.page_tensor(gg, lab)
                    pages.setdefault(tuple(F_.flatten()), F_)
steps = {}
for F1, F2 in itertools.product(list(pages.values()), repeat=2):
    Wt2 = TW.junction(F1, F2, (0, 0, 0), (0, 0, 0))
    Wm = sp.Matrix(4, 4, lambda i, j: Wt2[BL.ST[i][0], BL.ST[i][1], BL.ST[j][0], BL.ST[j][1]])
    steps.setdefault(tuple(Wm * N), Wm * N)
steps = list(steps.values())


def algebra_dim(gens):
    basis = []
    frontier = [sp.eye(4)]

    def add(M):
        v = sp.Matrix(list(M))
        if basis and sp.Matrix.hstack(*basis, v).rank() == len(basis):
            return False
        basis.append(v)
        return True
    add(sp.eye(4))
    for _ in range(6):
        nxt = []
        for M in frontier:
            for g_ in gens:
                if add(M * g_):
                    nxt.append(M * g_)
        frontier = nxt
    return len(basis)


ctrl["every plain ladder step of the family is nonsingular"] = all(s_.rank() == 4 for s_ in steps)
ctrl["one step generates a 4-dimensional commutative algebra (polynomials in it, which contain the identity)"] = \
    all(algebra_dim([s_]) == 4 for s_ in steps)
pair_dims = [algebra_dim([a_, b_]) for a_, b_ in itertools.combinations(steps, 2)]
observations["pairs of distinct steps: algebra dimensions"] = {d_: pair_dims.count(d_) for d_ in sorted(set(pair_dims))}
report("6 controls fire", all(ctrl.values()), {**ctrl, "distinct page tensors": len(pages), "distinct ladder steps": len(steps),
                                                 "observations (not controls)": observations})

out["ok"] = ok_all
out["seconds"] = round(time.time() - T0, 1)
print("ALL OK" if ok_all else "SOME CHECK FAILED", out["seconds"], "s")
if "--write" in sys.argv:
    json.dump({"schema_version": 1, "artifact_id": "PLAIN-BRACE-20261031-001A-P001", "status": "Proved" if ok_all else "Failed",
               "checks": out}, open(os.path.join(HERE, "result.json"), "w"), indent=1, default=str)
sys.exit(0 if ok_all else 1)
