"""Checks for WAVE-UNIQUENESS-20261029-001A-P001 (symmetric laws: four levels force the standing wave).

  0 dependency artifacts bound by the hashes recorded in manifest.json
  1 level 2 for two-sector laws: R_2 = sum_ijk P_ji P_ki G_jk u_i v_j v_k (symbolic identity, general vectors)
  2 the sector formulas: for biorthogonal laws R_k = Z_k(1) u1 v1 v1 + Z_k(2) u2 v2 v2, k = 3, 4, 5, against exact integer corner relations at
    random rational points
  3 level 3: eliminating the sector ratio r (after removing the powers of p - q) gives (p-q)^3 (p^2+1)(q^2+1)(pq-1) K(p, q) up to sign, K
    irreducible of degree 10 and symmetric
  4 the line pq = 1 with r = -p is the family of standing waves (y^2 = (1+p)^2/p) and satisfies levels 2 and 3 identically; r = +p (the cosine
    wave) fails level 3; the chart {v1, v2} = {(1,0), (0,1)} gives only the equality law
  5 level 4: K meets the level-4 condition with a common ratio exactly at the 32 roots of an irreducible factor of degree 32 (16 laws, in
    pairs exchanged by swapping the sectors), and not at the 36 roots of the other factor; K meets p + q = 0 only at degenerate points
  6 level 5: the 16 laws fail level 5 (80-digit sector formula and double-precision corner relation)
  7 tangent pencils: level 2 (saturated by det(u1, u2)) is a curve; level 3 leaves p in {0, 1, +-i}: p = +-i has R_2 = 0, p = 1 is the limit
    law (-1)^a E of the waves, p = 0 and the other chart give the two frozen laws
  8 rank one in the base corner: R_k = u_a (Q^k)_(bc) times scalar factors (k = 2, 3), so exactness forces Q^2 proportional to Q: products and
    u(a)[b = c]
  9 the final classes are exact at every level 2 to 8 (exact integers): waves (including y = 2 and equality), products, u(a)[b = c], the two frozen laws
 10 knots: among the final classes only signed not-all-equal (y = 1) has a knot support
 11 controls that must fire
Run: .venv/bin/python -B check.py [--write]   (sympy, mpmath, numpy; a few minutes)"""
import hashlib, itertools, json, os, random, sys, time
import numpy as np
import sympy as sp
import mpmath as mp

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
import wave_lib as WL  # noqa: E402
import gasket_engine as GE  # noqa: E402

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

R2, R3 = WL.relation(2), WL.relation(3)
TU = list(itertools.product((0, 1), repeat=3))

# ---------------------------------------------------------------- 1 level 2 for two-sector laws
a, b, c, d, e, f, g, h = sp.symbols("a b c d e f g h")
u = {1: (a, b), 2: (c, d)}
v = {1: (e, f), 2: (g, h)}
fw = WL.two_sector(u[1], v[1], u[2], v[2])
direct = [sp.expand(x.subs(dict(zip(WL.P, fw)))) for x in R2]
Pm = {(i, j): WL.dot(u[i], v[j]) for i in (1, 2) for j in (1, 2)}
Gm = {(i, j): WL.dot(v[i], v[j]) for i in (1, 2) for j in (1, 2)}
pred = [sp.expand(sum(Pm[(j, i)] * Pm[(k, i)] * Gm[(j, k)] * u[i][xa] * v[j][xb] * v[k][xc]
                      for i in (1, 2) for j in (1, 2) for k in (1, 2))) for xa, xb, xc in WL.CORNERS6]
report("1 level 2: R_2 = sum P_ji P_ki G_jk u_i v_j v_k for every two-sector law", all(sp.expand(x - y) == 0 for x, y in zip(direct, pred)),
       {"symbolic identity in eight vector entries": True})

# ---------------------------------------------------------------- 2 sector formulas against exact corner relations
rng = random.Random(20261029)
sec_ok, sec_n = True, 0
for _ in range(4):
    pv, qv = sp.Rational(rng.randint(-7, 7), rng.randint(1, 3)), sp.Rational(rng.randint(-7, 7), rng.randint(1, 3))
    if pv == qv:
        continue
    Av, Bv = sp.Rational(rng.randint(1, 5)), sp.Rational(rng.randint(-5, 5) or 1, rng.randint(1, 2))
    uu, vv = WL.generic(pv, qv, Av, Bv)
    fr = WL.two_sector(uu[1], vv[1], uu[2], vv[2])
    den = sp.ilcm(*[sp.fraction(x)[1] for x in fr])
    fint = [int(x * den) for x in fr]
    W = np.zeros((2, 2, 2), dtype=object)
    for xa, xb, xc in TU:
        W[xa, xb, xc] = fint[3 * xa + xb + xc]
    for k in (3, 4, 5):
        nT = k * (k + 1) // 2
        R = GE.corner_relation_int(2, k, W, primes=GE.PRIMES)
        Z = {s: WL.sector_Z(k, uu, vv, s) for s in (1, 2)}
        for xa, xb, xc in WL.CORNERS6:
            predv = sum(Z[s] * uu[s][xa] * vv[s][xb] * vv[s][xc] for s in (1, 2))
            sec_ok &= sp.Rational(int(R[xa, xb, xc])) == predv * den ** nT
        sec_n += 1
report("2 the sector formulas R_k = Z_k(1) u1 v1 v1 + Z_k(2) u2 v2 v2 (k = 3, 4, 5) equal the exact corner relations", sec_ok,
       {"point-level pairs": sec_n})

# ---------------------------------------------------------------- 3 level 3 elimination
p, q, A, B, r = sp.symbols("p q A B r")
uu, vv = WL.generic(p, q, A, B)


def Lr(k):
    Z = {s: WL.sector_Z(k, uu, vv, s) for s in (1, 2)}
    expr = sp.expand((Z[1] - Z[2]).subs(B, r * A))
    expr = sp.factor(expr)
    num = sp.numer(sp.together(expr))
    # drop the powers of A and of (p - q)
    keep = [fa ** m for fa, m in sp.factor_list(num)[1] if fa.free_symbols - {A} and sp.simplify(fa - (p - q)) != 0 and sp.simplify(fa + (p - q)) != 0]
    return sp.expand(sp.Mul(*keep))


n2, n3 = Lr(2), Lr(3)
res23 = sp.factor_list(sp.resultant(n2, n3, r))
facs = {str(fa): m for fa, m in res23[1]}
K = [fa for fa, m in res23[1] if sp.Poly(fa, p, q).total_degree() == 10][0]
kinfo = {"factors (degree, multiplicity)": [(sp.Poly(fa, p, q).total_degree(), m) for fa, m in res23[1]],
         "K symmetric": sp.expand(K - K.subs({p: q, q: p}, simultaneous=True)) == 0, "K irreducible over Q": len(sp.factor_list(K)[1]) == 1,
         "has p*q - 1": "p*q - 1" in facs, "has p**2 + 1 and q**2 + 1": "p**2 + 1" in facs and "q**2 + 1" in facs}
report("3 level 3: the resultant is (p-q)^m (p^2+1)(q^2+1)(pq-1) K with K irreducible, symmetric, of degree 10",
       kinfo["K symmetric"] and kinfo["K irreducible over Q"] and kinfo["has p*q - 1"] and kinfo["has p**2 + 1 and q**2 + 1"], kinfo)

# ---------------------------------------------------------------- 4 the wave line and the special chart
L2w = sp.factor(n2.subs(q, 1 / p))
wave_ok = sp.simplify(n2.subs({q: 1 / p, r: -p})) == 0 and sp.simplify(n3.subs({q: 1 / p, r: -p})) == 0
cos_fails = sp.simplify(n3.subs({q: 1 / p, r: p})) != 0 and sp.simplify(n2.subs({q: 1 / p, r: p})) == 0
uw, vw = WL.generic(p, 1 / p, 1, -p)
fwave = [sp.simplify(x) for x in WL.two_sector(uw[1], vw[1], uw[2], vw[2])]
ysq = (1 + p) ** 2 / p
wv = [ysq - 1, 1, -1, -1, 1, ysq - 1]            # (-1)^a U_(E-1)(y/2) with U_2(y/2) = y^2 - 1
ratio_ok = all(sp.simplify(fwave[i] * wv[0] - fwave[0] * wv[i]) == 0 for i in range(6))
# the chart v1 = (1, 0), v2 = (0, 1)
A_, B_ = sp.symbols("A_ B_")
uc = {1: tuple(A_ * x for x in WL.J((0, 1))), 2: tuple(B_ * x for x in WL.J((1, 0)))}
vc = {1: (1, 0), 2: (0, 1)}
Zc = {k: {s: sp.expand(WL.sector_Z(k, uc, vc, s)) for s in (1, 2)} for k in (2, 3)}
chart = sp.solve([Zc[2][1] - Zc[2][2], Zc[3][1] - Zc[3][2]], [B_], dict=True)
eq_law = [sp.simplify(x.subs(B_, -A_)) for x in WL.two_sector(uc[1], vc[1], uc[2], vc[2])]
eq_ok = all(sp.simplify(eq_law[i] * 1 - eq_law[0] * [1, 0, 0, 0, 0, 1][i]) == 0 for i in range(6))
report("4 the wave line (r = -p) is the standing waves and passes levels 2-3; the cosine wave (r = +p) fails level 3; the special chart gives equality",
       wave_ok and cos_fails and ratio_ok and chart == [{B_: -A_}] and eq_ok,
       {"r = -p solves L2 and L3 identically": wave_ok, "r = +p solves L2 but not L3": cos_fails,
        "law at r = -p is proportional to (-1)^a U_(E-1)(y/2), y^2 = (1+p)^2/p": ratio_ok, "special chart solutions": str(chart),
        "special chart law is equality": eq_ok})

# ---------------------------------------------------------------- 5 level 4 and the intersection
mp.mp.dps = 80
n4 = Lr(4)
res24 = sp.factor_list(sp.resultant(n2, n4, r))
K4 = [fa for fa, m in res24[1] if sp.Poly(fa, p, q).total_degree() == 22][0]
f24 = [(sp.Poly(fa, p, q).total_degree(), m) for fa, m in res24[1]]
RK = sp.factor_list(sp.resultant(K, K4, q))
rk = [(sp.Poly(fa, p).degree(), m) for fa, m in RK[1]]
F32 = [fa for fa, m in RK[1] if sp.Poly(fa, p).degree() == 32][0]
F36 = [fa for fa, m in RK[1] if sp.Poly(fa, p).degree() == 36][0]
fK4 = sp.lambdify((p, q), K4, "mpmath")
f3 = sp.lambdify((p, q, r), n3, "mpmath")
f4 = sp.lambdify((p, q, r), n4, "mpmath")
Kc = [sp.lambdify(p, cf, "mpmath") for cf in sp.Poly(K, q).all_coeffs()]
N2c = [sp.lambdify((p, q), cf, "mpmath") for cf in sp.Poly(n2, r).all_coeffs()]


def points(F):
    pts = []
    for pv in mp.polyroots([mp.mpf(int(x)) for x in sp.Poly(F, p).all_coeffs()], maxsteps=4000, extraprec=4000):
        qv = min(mp.polyroots([cf(pv) for cf in Kc], maxsteps=3000, extraprec=3000), key=lambda qq: abs(fK4(pv, qq)) / (1 + abs(fK4(pv, 0))))
        best = None
        for rv in mp.polyroots([cf(pv, qv) for cf in N2c], maxsteps=500, extraprec=500):
            s = max(abs(f3(pv, qv, rv)) / (1 + abs(f3(pv, qv, 0))), abs(f4(pv, qv, rv)) / (1 + abs(f4(pv, qv, 0))))
            if best is None or s < best[0]:
                best = (s, rv)
        pts.append((pv, qv, best[1], best[0]))
    return pts


P32, P36 = points(F32), points(F36)
common32 = sum(1 for x in P32 if x[3] < mp.mpf(10) ** -50)
common36 = sum(1 for x in P36 if x[3] < mp.mpf(10) ** -6)
plus = sp.factor_list(sp.factor(K.subs(q, -p)))
plus_deg = sorted(str(fa) for fa, m in plus[1])
gcd0 = sp.factor(sp.gcd(K.subs(p, 0), K4.subs(p, 0)))           # the factor p of res_q(K, K4): only q = 0, i.e. p = q (degenerate)
report("5 level 4: K meets the level-4 condition with a common ratio at exactly the 32 roots of the degree-32 factor",
       common32 == 32 and common36 == 0 and set(plus_deg) <= {"p", "p**2 + 1"} and (1, 6) in rk and (2, 32) in rk and str(gcd0) == "q**2",
       {"res(L2, L4) factors (degree, multiplicity)": f24, "res_q(K, K4) factors (degree in p, multiplicity)": rk,
        "points with a common ratio: degree-32 factor": common32, "degree-36 factor": common36, "K on p + q = 0": plus_deg,
        "gcd(K(0, q), K4(0, q)) (the factor p: only q = 0, degenerate)": str(gcd0)})

# ---------------------------------------------------------------- 6 level 5 kills the 16 sporadic laws
def law_mp(pv, qv, rv):
    uu_, vv_ = WL.generic(pv, qv, 1, rv)
    return uu_, vv_


fails, orbit_pairs = [], 0
laws = []
for pv, qv, rv, s in P32:
    uu_, vv_ = law_mp(pv, qv, rv)
    Z5 = {s_: WL.sector_Z(5, uu_, vv_, s_) for s_ in (1, 2)}
    rel5 = abs(Z5[1] - Z5[2]) / max(abs(Z5[1]), abs(Z5[2]))
    fw6 = WL.two_sector(uu_[1], vv_[1], uu_[2], vv_[2])
    Wn = WL.table([complex(x) for x in fw6])
    Wn = Wn / np.max(np.abs(Wn))
    R5 = GE.contract(2, 5, Wn)
    lam = np.vdot(Wn.ravel(), R5.ravel()) / np.vdot(Wn.ravel(), Wn.ravel())
    err5 = float(np.linalg.norm((R5 - lam * Wn).ravel()) / np.linalg.norm(R5.ravel()))
    errs = []
    for k in (2, 3, 4):
        Rk = GE.contract(2, k, Wn)
        lk = np.vdot(Wn.ravel(), Rk.ravel()) / np.vdot(Wn.ravel(), Wn.ravel())
        errs.append(float(np.linalg.norm((Rk - lk * Wn).ravel()) / np.linalg.norm(Rk.ravel())))
    fails.append((float(rel5), err5, max(errs)))
    laws.append(Wn)
# pair the 32 points into 16 laws (normalized tables up to a global phase)
def same(W1, W2):
    i = np.unravel_index(np.argmax(np.abs(W1)), W1.shape)
    return np.allclose(W1 / W1[i], W2 / W2[i], atol=1e-8)
used, classes = set(), 0
for i in range(len(laws)):
    if i in used:
        continue
    mates = [j for j in range(len(laws)) if j != i and j not in used and same(laws[i], laws[j])]
    used |= {i, *mates}
    classes += 1
report("6 the 16 sporadic laws pass levels 2-4 and fail level 5", all(x[0] > 1e-3 and x[1] > 1e-2 and x[2] < 1e-12 for x in fails) and classes == 16,
       {"min relative level-5 sector residual (80 digits)": min(x[0] for x in fails), "min level-5 error (double precision)": min(x[1] for x in fails),
        "max level-2..4 error": max(x[2] for x in fails), "distinct laws among the 32 points": classes})

# ---------------------------------------------------------------- 7 tangent pencils
a0, a1, b0, b1, t = sp.symbols("a0 a1 b0 b1 t")
tan_info = {}
ft = WL.tangent(p, a0, a1, b0, b1, 0)
r2t = [sp.expand(x.subs(dict(zip(WL.P, ft)))) for x in R2]
m2t = [sp.expand(r2t[i] * ft[j] - r2t[j] * ft[i]) for i in range(6) for j in range(i + 1, 6)]
det = a0 * b1 - a1 * b0
Gt = sp.groebner([x for x in m2t if x != 0] + [t * det - 1], t, a0, a1, b0, b1, p, order="lex")
sat = sorted(str(x) for x in Gt.exprs if t not in x.free_symbols)
tan_info["saturated level-2 ideal"] = sat
sol = {a1: p, b1: -(p ** 2 + 1), b0: p * (p ** 2 + 1), a0: -(2 * p ** 2 + 1)}
curve_ok = all(sp.expand(sp.sympify(x).subs(sol)) == 0 for x in sat)
fc = [sp.factor(x.subs(sol)) for x in ft]
r3c = [sp.factor(x.subs(dict(zip(WL.P, fc)))) for x in R3]
m3c = [sp.factor(sp.expand(r3c[i] * fc[j] - r3c[j] * fc[i])) for i in range(6) for j in range(i + 1, 6)]
gcd3 = sp.factor(sp.gcd_list([x for x in m3c if x != 0]))
tan_info["gcd of the level-3 minors on the curve"] = str(gcd3)
iso = all(max(abs(complex(sp.N(x.subs(dict(zip(WL.P, [y.subs(p, pv) for y in fc])))))) for x in R2) == 0 for pv in (sp.I, -sp.I))
tau = [3, 1, -1, -1, 1, 3]
p1 = [x.subs(p, 1) for x in fc]
tau_ok = all(sp.simplify(p1[i] * tau[0] - p1[0] * tau[i]) == 0 for i in range(6))
p0 = [x.subs(p, 0) for x in fc]
frozen_c = [1, 0, 0, 0, 1, 0]
fz_ok = all(sp.simplify(p0[i] * frozen_c[0] - p0[0] * frozen_c[i]) == 0 for i in range(6))
ft1 = WL.tangent(None, a0, a1, b0, b1, 1)
r2t1 = [sp.expand(x.subs(dict(zip(WL.P, ft1)))) for x in R2]
m2t1 = [sp.expand(r2t1[i] * ft1[j] - r2t1[j] * ft1[i]) for i in range(6) for j in range(i + 1, 6)]
Gt1 = sp.groebner([x for x in m2t1 if x != 0] + [t * det - 1], t, a0, a1, b0, b1, order="lex")
sat1 = sorted(str(x) for x in Gt1.exprs if t not in x.free_symbols)
tan_info["second chart, saturated level-2 ideal"] = sat1
frozen = [0, 1, 0, 0, 0, 1]
f1 = [sp.expand(x.subs({a0: 0, b1: 0, b0: a1})) for x in ft1]
fz1_ok = all(sp.simplify(f1[i] * frozen[1] - f1[1] * frozen[i]) == 0 for i in range(6)) and all(sp.expand(sp.sympify(x).subs({a0: 0, b1: 0, b0: a1})) == 0 for x in sat1)
report("7 tangent pencils: level 2 a curve, level 3 only p in {0, 1, +-i}; p = +-i has R = 0, p = 1 is (-1)^a E, p = 0 and the other chart frozen",
       curve_ok and str(gcd3) == "4*p*(p - 1)*(p**2 + 1)**7" and iso and tau_ok and fz_ok and fz1_ok,
       {**tan_info, "curve parametrization solves it": curve_ok, "p = +-i: R_2 = 0": iso, "p = 1 is (-1)^a E": tau_ok,
        "p = 0 is [a=0][b=c=0] + [a=1][b!=c]": fz_ok, "other chart: only [a=0][b!=c] + [a=b=c=1]": fz1_ok})

# ---------------------------------------------------------------- 8 rank one in the base corner
u0, u1, Q0, Q1, Q2 = sp.symbols("u0 u1 Q0 Q1 Q2")
fr = WL.rank_one(u0, u1, Q0, Q1, Q2)
Qm = sp.Matrix([[Q0, Q1], [Q1, Q2]])
r1_ok = True
for k, R in ((2, R2), (3, R3)):
    rk_ = [sp.factor(x.subs(dict(zip(WL.P, fr)))) for x in R]
    Qk = Qm ** k
    qk = [Qk[0, 0], Qk[0, 1], Qk[1, 1]]
    ratio = sp.factor(rk_[0] / (u0 * qk[0]))
    r1_ok &= all(sp.simplify(rk_[3 * xa + m] - (u0, u1)[xa] * qk[m] * ratio) == 0 for xa in (0, 1) for m in range(3))
    r1_ok &= sp.fraction(sp.together(ratio))[1].free_symbols == set()       # the scalar factor is a polynomial
report("8 rank one in the base corner: R_k = u_a (Q^k) times a scalar (k = 2, 3); hence Q^2 = cQ: products and u(a)[b = c]", r1_ok,
       {"identity holds for k = 2, 3": r1_ok})

# ---------------------------------------------------------------- 9 the final classes at every level 2..8
def exact_levels(fl, ks=range(2, 9)):
    W = np.zeros((2, 2, 2), dtype=object)
    for xa, xb, xc in TU:
        W[xa, xb, xc] = fl[3 * xa + xb + xc]
    res = {}
    for k in ks:
        ok, lam = GE.proportional_int(GE.corner_relation_int(2, k, W, primes=GE.PRIMES), W)
        res[k] = ok
    return res
CLASSES = {"wave y = 3": WL.wave_weights(3), "wave y = 2 ((-1)^a E)": WL.wave_weights(2), "wave y = 1 (signed NAE)": WL.wave_weights(1),
           "equality": [1, 0, 0, 0, 0, 1], "product u = (1, 2), v = (1, -3)": [1 * 1 * 1, 1 * 1 * -3, 1 * 9, 2, 2 * -3, 2 * 9],
           "u(a)[b = c], u = (1, 2)": [1, 0, 1, 2, 0, 2], "frozen [a=0][b!=c] + [a=b=c=1]": [0, 1, 0, 0, 0, 1],
           "frozen [a=0][b=c=0] + [a=1][b!=c]": [1, 0, 0, 0, 1, 0]}
lev = {name: exact_levels(fl) for name, fl in CLASSES.items()}
report("9 the final classes are exact at every level 2 to 8 (exact integers)", all(all(v_.values()) for v_ in lev.values()),
       {name: all(v_.values()) for name, v_ in lev.items()})


# ---------------------------------------------------------------- 10 knots
def is_knot(fl):
    allowed = [t_ for t_ in TU if fl[3 * t_[0] + t_[1] + t_[2]] != 0]
    if not allowed or len(allowed) == 8:
        return False
    return all(len({t_[:i] + t_[i + 1:] for t_ in allowed}) == 4 for i in range(3))
kn = {name: is_knot(fl) for name, fl in CLASSES.items()}
report("10 among the final classes only signed not-all-equal is a knot", kn == {name: name == "wave y = 1 (signed NAE)" for name in CLASSES}, kn)

# ---------------------------------------------------------------- 11 controls
ctrl = {}
uc2, vc2 = WL.generic(sp.Rational(2), sp.Rational(1, 2), 1, 2)
fcos = WL.two_sector(uc2[1], vc2[1], uc2[2], vc2[2])
ctrl["the cosine wave (r = +p) is exact at level 2 but not 3"] = (lambda e: e[2] and not e[3])(exact_levels([int(x * 4) for x in fcos], ks=(2, 3)))
pk = 0.6235
qk = min(sp.Poly(K.subs(p, sp.Rational(6235, 10000)), q).nroots(), key=lambda z: abs(complex(z)))
rk2 = min(sp.Poly(n2.subs({p: sp.Rational(6235, 10000), q: qk}), r).nroots(), key=lambda z: abs(complex(n3.subs({p: sp.Rational(6235, 10000), q: qk, r: z}))))
uk, vk = WL.generic(pk, complex(qk), 1, complex(rk2))
Wk = WL.table(WL.two_sector(uk[1], vk[1], uk[2], vk[2]))
def relerr(W, k):
    R = GE.contract(2, k, W)
    l_ = np.vdot(W.ravel(), R.ravel()) / np.vdot(W.ravel(), W.ravel())
    return float(np.linalg.norm((R - l_ * W).ravel()) / np.linalg.norm(R.ravel()))
ctrl["a law on K is exact at levels 2-3 and not at 4"] = relerr(Wk, 2) < 1e-10 and relerr(Wk, 3) < 1e-10 and relerr(Wk, 4) > 1e-3
ctrl["a random law fails level 2"] = not exact_levels([3, -1, 4, 1, -5, 9], ks=(2,))[2]
report("11 controls fire", all(ctrl.values()), ctrl)

out["ok"] = ok_all
out["seconds"] = round(time.time() - T0, 1)
print("ALL OK" if ok_all else "SOME CHECK FAILED", out["seconds"], "s")
if "--write" in sys.argv:
    json.dump({"schema_version": 1, "artifact_id": "WAVE-UNIQUENESS-20261029-001A-P001", "status": "Proved" if ok_all else "Failed",
               "checks": out, "K": str(K)}, open(os.path.join(HERE, "result.json"), "w"), indent=1, default=str)
sys.exit(0 if ok_all else 1)
