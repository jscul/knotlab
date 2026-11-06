"""Checks for SOFT-CROSS-20261031-001A-P001 (a soft crossing interpolates to a sharp one).

  0 dependency artifacts bound by the hashes recorded in manifest.json
  1 the dead cap: the cube minus an edge, unsigned, counts 3 whatever its two attachments see
  2 the soft crossing from the explicit page signings: Hadamard straight entries (40000, -1112, 3336, -192), turning entries 0, both pages
    twisted
  3 snakes: crossover-type with straight entries sigma_1 Lambda^(k-1), Lambda = (810000, 7506, -22518, -432), k = 1..6; the tensor
    prediction equals the direct count of K3,3 instances for k = 1..7 under three signings
  4 the lattice condition: valuations at 5, 139, 3 of Lambda; squared products distinct for every count vector of total m <= 8
  5 long edges: colour matrix 3^k M^k on actual graphs (k = 1..4); an exact edge recovered by interpolation
  6 end to end: 9 #col(K3,3, sigma) recovered from four counts of Pfaffian instances, three signings; every instance certified Pfaffian
  7 controls: a single host point on wire B makes the system singular; an exclusive crossing cannot be sharpened; K3,3 itself is never
    non-colourable; a signed cube cap is not dead
Run: .venv/bin/python -B check.py [--write]   (networkx, numpy, sympy; about a minute)"""
import collections, hashlib, itertools, json, os, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
P = lambda r: os.path.join(ROOT, "proofs", r)  # noqa: E731
for p in (P("THREEFOLD-AMPLITUDE-20261030-001A/THREEFOLD-AMPLITUDE-20261030-001A-P001_five_per_handle_tuttes_number_per_planar_piece"),
          P("THREEFOLD-AMPLITUDE-20261030-001B/THREEFOLD-AMPLITUDE-20261030-001B-P001_the_amplitude_by_computation"),
          P("TWIST-COUNT-20261030-001A/TWIST-COUNT-20261030-001A-P001_the_knots_junction_is_a_similitude"), HERE):
    sys.path.insert(0, p)
import networkx as nx  # noqa: E402
import numpy as np  # noqa: E402
import sympy as sp  # noqa: E402
import amplitude_lib as AM  # noqa: E402
import twist_lib as TW  # noqa: E402
import cross_lib as X  # noqa: E402

T0 = time.time()
out, ok_all = {}, True
ALL4 = list(itertools.product((0, 1), repeat=4))


def report(key, ok, detail):
    global ok_all
    out[key] = {"ok": bool(ok), "detail": detail}
    ok_all &= bool(ok)
    print(("PASS " if ok else "FAIL ") + key + ": " + json.dumps(detail, default=str)[:3000], flush=True)


def cap_counts(neg_edges=()):
    """F(xu, xp) for the cube minus the edge (u, v): u's colour xu, v sees an outside point of colour xp"""
    cube = nx.hypercube_graph(3)
    col = nx.bipartite.color(cube)
    u, v = (0, 0, 0), (1, 0, 0)
    h = cube.copy()
    h.remove_edge(u, v)
    pts = [w for w in h if col[w] == col[u]]
    lns = [w for w in h if col[w] != col[u]]
    F = {}
    for xu, xp in itertools.product((0, 1), repeat=2):
        cnt = 0
        others = [w for w in pts if w != u]
        for bits in itertools.product((0, 1), repeat=len(others)):
            x = dict(zip(others, bits))
            x[u] = xu
            good = True
            for l in lns:
                seen = [x[w] ^ (1 if frozenset((l, w)) in neg_edges else 0) for w in h[l]]
                if l == v:
                    seen.append(xp)
                good &= len(set(seen)) == 2
            cnt += good
        F[(xu, xp)] = cnt
    return F, h, col


# ---------------------------------------------------------------- 0
man = json.load(open(os.path.join(HERE, "manifest.json")))
mism = {r: dg for r, dg in man["parent_bindings"].items()
        if hashlib.sha256(open(os.path.join(ROOT, r), "rb").read()).hexdigest() != dg}
report("0 dependency artifacts bound by hash", not mism, {"parents": len(man["parent_bindings"]), "mismatched": mism})

# ---------------------------------------------------------------- 1 the dead cap
F, _, _ = cap_counts()
report("1 the cube minus an edge, unsigned, is a dead cap", set(F.values()) == {3}, {"F(xu, xp)": {str(k): v for k, v in F.items()}})

# ---------------------------------------------------------------- 2 the soft crossing
inc, pts, att, sq = TW.page(X.PAGE, X.SQUARE)
FQ = TW.page_tensor(inc, pts, att, set(X.SIGN_Q))
FR = TW.page_tensor(inc, pts, att, set(X.SIGN_R))
W = TW.junction(FQ, FR, (0, 0, 0), (0, 0, 1))
Wt = X.hada(W)
sigma1 = [Wt[s] for s in X.STRAIGHT]
ok2 = sigma1 == [40000, -1112, 3336, -192] and all(Wt[s] == 0 for s in X.TURNING) and TW.split_of(FQ) is None and \
    TW.split_of(FR) is None and TW.mgi(Wt) != 0
report("2 the soft crossing from the explicit page signings", ok2, {"straight": sigma1, "turning": [Wt[s] for s in X.TURNING],
       "pages twisted": [TW.split_of(FQ) is None, TW.split_of(FR) is None], "MGI": TW.mgi(Wt)})

# ---------------------------------------------------------------- 3 snakes
LAMBDA = [810000, 7506, -22518, -432]
d3, ok3 = {"Hadamard straight entries": {}, "instances": {}}, True
for k in range(1, 7):
    St = X.hada(X.snake_tensor(W, k)) * 9 ** (k - 1)
    st = [St[s] for s in X.STRAIGHT]
    d3["Hadamard straight entries"][k] = st
    ok3 &= all(St[s] == 0 for s in X.TURNING) and st == [a * b ** (k - 1) for a, b in zip(sigma1, LAMBDA)]


def rest_tensor(signs):
    """the K3,3 part with l_f, pi_e and their cap, on the snake's legs (A_in, B_in, A_out, B_out)"""
    Pp, Ll = X.K33_POINTS, X.K33_LINES
    s = lambda p, l: 1 if (p, l) in signs else 0  # noqa: E731
    R = np.zeros((2, 2, 2, 2), dtype=object)
    for x in itertools.product((0, 1), repeat=3):
        for z0, z2, z3 in itertools.product((0, 1), repeat=3):
            good = 1
            for l in Ll:
                seen = []
                for i, p in enumerate(Pp):
                    if (p, l) == X.E_EDGE:
                        seen.append(z3 ^ s(p, l))
                    elif (p, l) == X.F_EDGE:
                        seen.append(z2 ^ s(p, l))
                    else:
                        seen.append(x[i] ^ s(p, l))
                good *= X.nae(*seen)
            if good:
                R[z0, x[0], z2, z3] += 3 * sum(X.nae(x[2], z0, f) for f in (0, 1))
    return R


SIGNINGS = {"unsigned": 0b000000000, "two negations": 0b000010001, "five negations": 0b101100110}
COUNTS = {}
for name, mask in SIGNINGS.items():
    signs = X.k33_signs(mask)
    R = rest_tensor(signs)
    for k in range(1, 8):
        H, neg = X.k33_instance(k, signs).system()
        direct = AM.count(H, neg)
        pred = sum(R[z] * X.snake_tensor(W, k)[z] for z in ALL4) * 9 ** (k - 1)
        COUNTS[(name, k)] = direct
        ok3 &= pred == direct
    d3["instances"][name] = {k: str(COUNTS[(name, k)])[:24] + ("..." if len(str(COUNTS[(name, k)])) > 24 else "") for k in (1, 3, 7)}
report("3 snakes: crossover-type, straight entries sigma_1 Lambda^(k-1); predictions equal direct instance counts", ok3, d3)

# ---------------------------------------------------------------- 4 the lattice condition
vals = {pr: [sp.multiplicity(pr, abs(v)) for v in LAMBDA] for pr in (2, 3, 5, 139)}
ok4 = vals[5] == [4, 0, 0, 0] and vals[139] == [0, 1, 1, 0] and vals[3] == [4, 3, 4, 3] and \
    all(abs(v) == 2 ** vals[2][i] * 3 ** vals[3][i] * 5 ** vals[5][i] * 139 ** vals[139][i] for i, v in enumerate(LAMBDA))
distinct = {}
for m in range(1, 9):
    prods = {}
    for n in itertools.product(range(m + 1), repeat=4):
        if sum(n) != m:
            continue
        val = 1
        for a, e in zip(LAMBDA, n):
            val *= a ** (2 * e)
        prods.setdefault(val, []).append(n)
    distinct[m] = all(len(v) == 1 for v in prods.values())
    ok4 &= distinct[m]
report("4 the lattice condition: valuations of Lambda separate count vectors; squared products distinct", ok4,
       {"valuations (2, 3, 5, 139)": vals, "distinct for total m": distinct})

# ---------------------------------------------------------------- 5 long edges
d5, ok5 = {}, True
Mm = sp.Matrix([[1, 2], [2, 1]])
base = nx.relabel_nodes(nx.hypercube_graph(3), lambda v: v)
col = nx.bipartite.color(base)
pts_, lns_ = [v for v in base if col[v] == 0], [v for v in base if col[v] == 1]
P0, L0 = pts_[0], [l for l in lns_ if base.has_edge(pts_[0], l)][0]
negset = {frozenset((lns_[1], w)) for w in list(base[lns_[1]])[:1]}
Zl = {}
for k in range(0, 5):
    Bd = X.Builder()
    name = {v: (('pt' if col[v] == 0 else 'ln'), 'C', v) for v in base}
    for a, b in base.edges():
        if {a, b} == {P0, L0}:
            continue
        pa, lb = (a, b) if col[a] == 0 else (b, a)
        Bd.edge(name[pa], name[lb], frozenset((lb, pa)) in negset)
    if k == 0:
        Bd.edge(name[P0], name[L0])
    else:
        X.long_edge(Bd, name[P0], name[L0], k, 'e')
    H, neg = Bd.system()
    Zl[k] = AM.count(H, neg)
# predicted: Z_k = sum_ab R(a, b) (3^k M^k)(a, b), with R from k = 0 (identity) not directly available; check the eigen form
# Z_k = 9^k c_plus + (-3)^k c_minus and the exact edge Z_0 = c_plus + c_minus
cplus, cminus = sp.symbols('cplus cminus')
sol = sp.solve([sp.Eq(9 * cplus - 3 * cminus, Zl[1]), sp.Eq(81 * cplus + 9 * cminus, Zl[2])], [cplus, cminus])
recovered = sol[cplus] + sol[cminus]
consistent = all(Zl[k] == 9 ** k * sol[cplus] + (-3) ** k * sol[cminus] for k in (3, 4))
d5 = {"counts with long edge of k pairs": Zl, "recovered exact edge (from k = 1, 2)": recovered, "consistent at k = 3, 4": consistent}
ok5 = recovered == Zl[0] and consistent and Mm.eigenvals() == {3: 1, -1: 1}
report("5 long edges: counts 9^k c+ + (-3)^k c-; the exact edge is recovered by interpolation", ok5, d5)

# ---------------------------------------------------------------- 6 end to end
d6, ok6 = {"recovered": {}, "Pfaffian certificates": {}}, True
Xs = np.zeros((2, 2, 2, 2), dtype=object)
for z in ALL4:
    Xs[z] = (1 if z[1] == z[3] else 0) * (-1 if z[0] == z[2] else 2)
Xt = X.hada(Xs)
for name, mask in SIGNINGS.items():
    signs = X.k33_signs(mask)
    Mx = sp.Matrix([[sp.Rational(sigma1[i] * LAMBDA[i] ** (k - 1), 16) for i in range(4)] for k in (1, 3, 5, 7)])
    c = Mx.LUsolve(sp.Matrix([COUNTS[(name, k)] for k in (1, 3, 5, 7)]))
    target = sum(c[i] * sp.Rational(Xt[s], 16) for i, s in enumerate(X.STRAIGHT))
    Hk, negk = X.k33_system(signs)
    direct = AM.count(Hk, negk)
    d6["recovered"][name] = {"recovered": str(target), "#col(K3,3)": direct}
    ok6 &= target == 9 * direct
for k in (1, 3, 5, 7):
    good, pieces = X.certify_pfaffian(X.k33_instance(k, set()), TW, AM)
    d6["Pfaffian certificates"][k] = {"planar pieces": pieces, "certified": good,
                                      "vertices": X.k33_instance(k, set()).g.number_of_nodes()}
    ok6 &= good
report("6 end to end: 9 #col(K3,3) recovered from four counts of certified Pfaffian instances", ok6, d6)

# ---------------------------------------------------------------- 7 controls
ctrl = {}
alt = [X.hada(X.snake_tensor(W, k, wire_b_line=False)) for k in (1, 3, 5, 7)]
Malt = sp.Matrix([[a[s] for s in X.STRAIGHT] for a in alt])
ctrl["a single host point on wire B makes the one-site system singular"] = Malt.det() == 0
# an exclusive crossing (zero double entry) from cube pages
ginc, gpts, gatt, gsq = TW.page(nx.relabel_nodes(nx.hypercube_graph(3), lambda v: v), None)
excl = None
cube_t = [TW.page_tensor(ginc, gpts, gatt, s) for s in TW.page_sign_classes(ginc)]
for A_, B_ in itertools.product(cube_t, repeat=2):
    for s1, s3 in (((0, 0, 0), (0, 0, 0)), ((0, 1, 0), (0, 1, 0)), ((0, 0, 1), (0, 1, 1))):
        Wx = X.hada(TW.junction(A_, B_, s1, s3))
        if all(Wx[t] == 0 for t in X.TURNING) and Wx[1, 1, 1, 1] == 0 and TW.mgi(Wx) != 0:
            excl = [Wx[s] for s in X.STRAIGHT]
            break
    if excl:
        break
ctrl["an exclusive crossing (double entry 0) leaves the double state unrecoverable"] = excl is not None and excl[3] == 0
Hk, negk = X.k33_system(set())
ctrl["K3,3 is colourable under every signing (not Pfaffian)"] = all(AM.colourable(*X.k33_system(X.k33_signs(m))) for m in range(512))
_, h, _ = cap_counts()
nondead = [tuple(sorted(e)) for e in h.edges() if len(set(cap_counts({frozenset(e)})[0].values())) > 1]
ctrl["a cube cap with one negated edge is not dead (for some edge)"] = len(nondead) > 0
report("7 controls fire", all(ctrl.values()), {**ctrl, "exclusive crossing straight entries": excl, "non-dead single negations": len(nondead)})

out["ok"] = ok_all
out["seconds"] = round(time.time() - T0, 1)
print("ALL OK" if ok_all else "SOME CHECK FAILED", out["seconds"], "s")
if "--write" in sys.argv:
    json.dump({"schema_version": 1, "artifact_id": "SOFT-CROSS-20261031-001A-P001", "status": "Proved" if ok_all else "Failed",
               "checks": out}, open(os.path.join(HERE, "result.json"), "w"), indent=1, default=str)
sys.exit(0 if ok_all else 1)
