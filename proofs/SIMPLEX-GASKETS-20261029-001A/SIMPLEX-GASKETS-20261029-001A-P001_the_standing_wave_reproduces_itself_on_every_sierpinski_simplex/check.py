"""Checks for SIMPLEX-GASKETS-20261029-001A-P001 (the standing wave reproduces itself on every Sierpinski simplex).

The proof is in proof.md; these checks replay every finite ingredient and test the theorems on the cases that can be computed.
  0 dependency artifacts bound by the hashes recorded in manifest.json
  1 closed forms, d = 1 to 7, on all tuples: sin(theta E)/sin(theta) = U_(E-1)(y/2) with y = 2 cos(theta) (integer polynomial in y, divisible by y
    when E is even); the two-sector form (1/D) sum_s s (-1)^(x_0) zeta^(sE); w_(pi - theta) = (-1)^d w_theta; the Legendre law (-1)^(x_0) (E|3) equals
    (-1)^d w_(pi/3) and 1 + sum_i s_0 s_i modulo 3; at y = 2 the law is tau = (-1)^(x_0) E = 1 + sum_i s_0 s_i, at y = -2 it is (-1)^d tau; d = 1
    gives y times equality
  2 exactness of the Legendre law by exact integers for d = 2 (k <= 7), 3 (k <= 5), 4 (k <= 3), 5 to 7 (k <= 2), with lambda = (-1)^N mod 3
  3 the factor as a polynomial in y, for d = 2 (k <= 5), 3 (k <= 4), 4 (k <= 3), 5 and 6 (k = 2), modulo three primes at d#T + 3 values of y:
    R = lambda(y) w(y) at every value (a polynomial identity, by degree), lambda monic of degree d(#T - 1) and of that parity, lambda(2) = 2^N,
    lambda(-2) = (-1)^(d(#T-1)) 2^N, level 2: lambda = y^d (y^2 - 2)^(d(d-1)/2); the integer polynomial (Chinese remainder theorem) at y = 1 against
    check 2
  4 the sector formula of the proof, lambda = D^(1 - #T) Z(1), against the direct factor at three angles for d = 2 (k <= 5), 3 (k <= 3), 4 and 5 (k = 2)
  5 the edge-set lemma: tau reproduces itself with factor exactly 2^N (exact integers) in the cases of check 2, which counts the edge sets by their odd
    corners (the counts are nonnegative); direct enumeration for d = 2 (k <= 4), 3 (k <= 3), 4 and 5 (k = 2)
  6 nonvanishing: no factor polynomial of check 3 shares a root with 2 cos(2 pi/n) for n = p^m or 2 p^m (p an odd prime) up to 60 (exact gcd with the
    minimal polynomial); the n whose roots occur are listed; floating-point exactness at theta = pi/q, q = 3, 5, 7, 9
  7 the knot criterion: for d = 2 to 9 and theta = j pi/q (2 <= q <= 13) and two generic angles, the support of w_theta passes K1-K3 exactly when the
    criterion says; knotlab on six named supports
  8 towers: the level-2 and level-3 towers have corner relation lambda^((n^m - 1)/(n - 1)) w (exact integers); two up simplices share at most one
    vertex; the similarity dimensions log C(k+d-1, d)/log k
  9 floating point: the wave at four angles reproduces itself for d = 2 (k <= 6), 3 (k <= 4), 4 (k <= 3), 5 and 6 (k = 2), with the factor equal to
    the polynomial of check 3 where it is available
 10 controls that must fire (and one positive case: in d = 3 a sum of two waves is again a wave)
Run: .venv/bin/python -B check.py [--write]   (numpy, sympy)"""
import cmath, hashlib, itertools, json, math, os, subprocess, sys, time
import numpy as np
import sympy as sp

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
import simplex_lib as S  # noqa: E402

T0 = time.time()
out, ok_all = {}, True


def report(key, ok, detail):
    global ok_all
    out[key] = {"ok": bool(ok), "detail": detail}
    ok_all &= bool(ok)
    print(("PASS " if ok else "FAIL ") + key + ": " + json.dumps(detail, default=str)[:3000], flush=True)


def s(x):
    return (-1) ** x


# ---------------------------------------------------------------- 0
man = json.load(open(os.path.join(HERE, "manifest.json")))
mism = {r: dg for r, dg in man["parent_bindings"].items()
        if hashlib.sha256(open(os.path.join(ROOT, r), "rb").read()).hexdigest() != dg}
report("0 dependency artifacts bound by hash", not mism, {"parents": len(man["parent_bindings"]), "mismatched": mism})

# ---------------------------------------------------------------- 1 closed forms
yv = sp.symbols("y")
c = {}
for d in range(1, 8):
    TU = S.tuples(d)
    ok_u = ok_sec = ok_pi = ok_leg = ok_m3 = ok_tau = ok_div = True
    for th in (0.37, 1.1, 2.0, 2.9):
        w = S.wave(d, th)
        zeta = cmath.exp(1j * th)
        for x in TU:
            ok_u &= abs(s(x[0]) * S.cheb_u(S.E(x) - 1, 2 * math.cos(th)) - w[x]) < 1e-9
            sec = sum(sg * s(x[0]) * zeta ** (sg * S.E(x)) for sg in (1, -1)) / (zeta - 1 / zeta)
            ok_sec &= abs(sec - w[x]) < 1e-9
        ok_pi &= np.allclose(S.wave(d, math.pi - th), (-1) ** d * w)
    L, tau, w3 = S.legendre(d), S.tau(d), S.wave(d, math.pi / 3)
    for x in TU:
        ok_leg &= abs(L[x] - (-1) ** d * w3[x]) < 1e-12
        ok_m3 &= (L[x] - (1 + sum(s(x[0]) * s(x[i]) for i in range(1, d + 1)))) % 3 == 0
        ok_tau &= tau[x] == 1 + sum(s(x[0]) * s(x[i]) for i in range(1, d + 1)) == S.wave_at(d, 2)[x] and S.wave_at(d, -2)[x] == (-1) ** d * tau[x]
        if S.E(x) % 2 == 0:
            ok_div &= sp.rem(sp.expand(S.cheb_u(S.E(x) - 1, yv)), yv) == 0
    c[d] = all((ok_u, ok_sec, ok_pi, ok_leg, ok_m3, ok_tau, ok_div))
w1 = S.wave_at(1, yv)
eq_ok = all(sp.expand(w1[x] - (yv if x[0] == x[1] else 0)) == 0 for x in S.tuples(1))
report("1 closed forms of the standing wave (d = 1 to 7, all tuples)", all(c.values()) and eq_ok,
       {"per d: Chebyshev form, two sectors, pi - theta, Legendre = (-1)^d w_(pi/3) and 1 + sum s_0 s_i mod 3, tau at y = +-2, y | U for even E": c,
        "d = 1 is y [x_0 = x_1]": eq_ok})

# ---------------------------------------------------------------- 2 exactness of the Legendre law, exact integers
CASES = [(2, k) for k in range(1, 8)] + [(3, k) for k in range(1, 6)] + [(4, k) for k in range(1, 4)] + [(5, 1), (5, 2), (6, 1), (6, 2), (7, 2)]
lamL = {}
ex_ok = True
for d, k in CASES:
    L = S.legendre(d)
    ok, lam = S.proportional_int(S.corner_relation_int(d, k, L), L)
    nT, N = S.counts(d, k)
    lamL[(d, k)] = lam
    ex_ok &= ok and (lam - (-1) ** N) % 3 == 0
report("2 the Legendre law is exact, lambda = (-1)^N mod 3 (exact integers)", ex_ok, {f"d={d} k={k}": str(v) for (d, k), v in lamL.items()})

# ---------------------------------------------------------------- 3 the factor as a polynomial in y = 2 cos(theta)
PCASES = [(2, 2), (2, 3), (2, 4), (2, 5), (3, 2), (3, 3), (3, 4), (4, 2), (4, 3), (5, 2), (6, 2)]
polys, pdet = {}, {}
p_ok = True
for d, k in PCASES:
    nT, N = S.counts(d, k)
    deg = d * (nT - 1)
    co, ident, per = S.lambda_poly(d, k)
    co2 = S.lambda_poly(d, k, primes=S.PRIMES[3:6])[0]
    P = sp.Poly(list(reversed(co)), yv)
    good = (ident and co == co2 and len(co) - 1 == deg and co[-1] == 1
            and all(cf == 0 for i, cf in enumerate(co) if (i - deg) % 2)
            and P.eval(2) == 2 ** N and P.eval(-2) == (-1) ** deg * 2 ** N
            and P.eval(1) == (-1) ** deg * lamL[(d, k)])
    if k == 2:
        good &= sp.expand(P.as_expr() - yv ** d * (yv ** 2 - 2) ** (d * (d - 1) // 2)) == 0
    p_ok &= good
    polys[(d, k)] = co
    pdet[f"d={d} k={k}"] = {"degree": len(co) - 1, "d(#T-1)": deg, "monic": co[-1] == 1, "R = lambda w at all samples": ident,
                            "same polynomial from three other primes": co == co2, "lambda(2) = 2^N": P.eval(2) == 2 ** N, "lambda(1)": int(P.eval(1)),
                            "factors": str(sp.factor_list(P.as_expr())) if deg <= 30 else "degree " + str(deg)}
report("3 lambda is a monic integer polynomial in y = 2 cos(theta) of degree d(#T-1), lambda(2) = 2^N, level 2 closed form", p_ok, pdet)

# ---------------------------------------------------------------- 4 the sector formula
sec = {}
sec_ok = True
for d, k in [(2, 2), (2, 3), (2, 4), (2, 5), (3, 2), (3, 3), (4, 2), (5, 2)]:
    for th in (0.41, 1.3, 2.2):
        lam_dir = S.proportional_float(S.corner_relation_float(d, k, S.wave(d, th)), S.wave(d, th))[0]
        lam_sec = S.sector_lambda(d, k, th)
        good = abs(lam_sec.imag) < 1e-7 * max(1, abs(lam_dir)) and abs(lam_sec.real - lam_dir) < 1e-7 * max(1, abs(lam_dir))
        sec_ok &= good
        sec[f"d={d} k={k} theta={th}"] = [round(lam_dir, 9), round(lam_sec.real, 9)]
report("4 the sector formula lambda = D^(1-#T) Z(1) equals the direct factor", sec_ok, sec)

# ---------------------------------------------------------------- 5 the edge-set lemma
lem = {}
lem_ok = True
for d, k in CASES:
    nT, N = S.counts(d, k)
    tau = S.tau(d)
    Rt = S.corner_relation_int(d, k, tau)
    lem_ok &= all(Rt[x] == 2 ** N * tau[x] for x in S.tuples(d))
enum = {}
for d, k in [(2, 1), (2, 2), (2, 3), (2, 4), (3, 2), (3, 3), (4, 2), (5, 2)]:
    found = S.edge_sets(d, k)
    want = {frozenset()} | set(S.axis_paths(d, k))
    enum[f"d={d} k={k}"] = len(found)
    lem_ok &= set(found) == want and len(found) == d + 1
report("5 edge-set lemma: tau reproduces itself with factor 2^N; the only even edge sets are the empty set and the d axis paths", lem_ok,
       {"tau exact with 2^N in every case of check 2": True, "edge sets found by enumeration (d + 1 expected)": enum})


# ---------------------------------------------------------------- 6 nonvanishing at rational angles
def psi(n):
    """minimal polynomial of 2 cos(2 pi/n) over Q (n >= 3), checked against the cyclotomic polynomial"""
    roots = [2 * math.cos(2 * math.pi * m / n) for m in range(1, (n + 1) // 2) if math.gcd(m, n) == 1]
    coeffs = np.poly(roots)
    P = sp.Poly([int(round(float(cf))) for cf in coeffs], yv)
    x = sp.symbols("x")
    assert sp.expand(sp.Poly(P.as_expr().subs(yv, x + 1 / x) * x ** P.degree(), x).as_expr() - sp.cyclotomic_poly(n, x)) == 0
    return P


def odd_prime_power(m):
    f = sp.factorint(m)
    return len(f) == 1 and 2 not in f


PSI = {n: psi(n) for n in range(3, 61)}
hits = {}
nv_ok = True
for (d, k), co in polys.items():
    P = sp.Poly(list(reversed(co)), yv)
    found = [n for n, Q in PSI.items() if sp.gcd(P, Q).degree() > 0]
    hits[f"d={d} k={k}"] = found
    nv_ok &= not any(odd_prime_power(n) or (n % 2 == 0 and odd_prime_power(n // 2)) for n in found)
flt = {}
for d, k in [(2, 4), (3, 3), (4, 2), (5, 2)]:
    for q in (3, 5, 7, 9):
        w = S.wave(d, math.pi / q)
        lam, err = S.proportional_float(S.corner_relation_float(d, k, w), w)
        flt[f"d={d} k={k} pi/{q}"] = round(lam, 6)
        nv_ok &= err < 1e-9 and abs(lam) > 1e-9
report("6 no zero at theta = j pi/q with q an odd prime power (exact gcd with minimal polynomials, n <= 60)", nv_ok,
       {"n <= 60 with 2 cos(2 pi m/n) a root (theta = 2 pi m/n)": hits, "floating-point factor at pi/q": flt})


# ---------------------------------------------------------------- 7 the knot criterion
def support(d, j, q):
    """weights t (number of ones) where sin(theta (d+1-2t)) is nonzero, theta = j pi/q exactly (q = None: an irrational multiple of pi)"""
    keep = []
    for t in range(d + 2):
        Ev = d + 1 - 2 * t
        zero = (Ev == 0) if q is None else (Ev * j) % q == 0
        if not zero:
            keep.append(t)
    return keep


def criterion(d, j, q):
    if q is not None and (2 * j) % q == 0:   # sin(2 theta) = 0
        return False
    if d % 2 == 1:
        return True
    return q is not None and q % 2 == 1 and q <= d + 1


crit = {}
k_ok = True
for d in range(2, 10):
    angles = [(j, q) for q in range(2, 14) for j in range(1, q) if math.gcd(j, q) == 1] + [(None, None)]
    for j, q in angles:
        keep = support(d, j, q)
        allowed = [x for x in S.tuples(d) if sum(x) in keep]
        kn = S.is_knot(allowed, d + 1)
        if q is not None:
            w = S.wave(d, j * math.pi / q)
            num = sorted({sum(x) for x in S.tuples(d) if abs(w[x]) > 1e-9})
            k_ok &= num == keep or (2 * j) % q == 0
        k_ok &= kn == criterion(d, j, q)
        if kn:
            crit.setdefault(d, []).append("generic" if q is None else f"{j}pi/{q}")
env = dict(os.environ, PYTHONPATH=os.path.join(ROOT, "tools"))
named = {"d=3 pi/3 (not exactly two ones)": (3, 1, 3), "d=3 pi/4 (odd parity)": (3, 1, 4), "d=4 pi/5 (five-place not-all-equal)": (4, 1, 5),
         "d=4 pi/3 (not one or four ones)": (4, 1, 3), "d=5 pi/3 (not zero, three or six ones)": (5, 1, 3), "d=6 pi/7 (seven-place not-all-equal)": (6, 1, 7)}
kl = {}
for name, (d, j, q) in named.items():
    keep = support(d, j, q)
    var = "abcdefg"[: d + 1]
    excl = [x for x in S.tuples(d) if sum(x) not in keep]
    cnf = "; ".join(" ".join((v if b == 0 else "~" + v) for v, b in zip(var, x)) for x in excl)
    r = subprocess.run([sys.executable, "-B", "-m", "knotlab", "check", "--cnf", cnf, "--loops", *var[:-1], "--contact", var[-1], "--json"],
                       capture_output=True, text=True, env=env, cwd=ROOT)
    kj = json.loads(r.stdout)
    want = sorted("".join(map(str, x)) for x in S.tuples(d) if sum(x) in keep)
    kl[name] = {"is_knot": kj["is_knot"], "allowed matches": sorted(kj["allowed"]) == want}
    k_ok &= kj["is_knot"] and sorted(kj["allowed"]) == want
report("7 knot criterion (K1-K3 on supports, d = 2 to 9) and knotlab on named supports", k_ok, {"knot angles (q <= 13) per d": crit, "knotlab": kl})

# ---------------------------------------------------------------- 8 towers
tw = {}
tw_ok = True
for d, k, m in [(2, 2, 2), (2, 2, 3), (2, 3, 2), (2, 4, 2), (3, 2, 2), (3, 2, 3), (3, 3, 2), (4, 2, 2)]:
    L = S.legendre(d)
    n = S.counts(d, k)[0]
    lam1 = lamL[(d, k)]
    ok, lam = S.proportional_int(S.corner_relation_int(d, k, L, primes=S.PRIMES, cx=S.tower(d, k, m)), L)
    good = ok and lam == lam1 ** ((n ** m - 1) // (n - 1))
    tw_ok &= good
    tw[f"d={d} k={k} m={m}"] = str(lam)
share = True
for d in range(2, 6):
    for k in range(2, 5):
        if d >= 4 and k > 3:
            continue
        simp = S.gasket(d, k)[1]
        share &= all(len(set(a) & set(b)) <= 1 for a, b in itertools.combinations(simp, 2))
KS = (2, 3, 4, 10, 100, 10 ** 6)
dimf = lambda d, k: math.log(math.comb(k + d - 1, d)) / math.log(k)
dims = {f"d={d}": [round(dimf(d, k), 4) for k in KS] for d in range(2, 7)}
cnt = all(S.counts(d, k)[0] == math.comb(k + d - 1, d) for d in range(1, 6) for k in range(1, 6) if not (d >= 4 and k > 4))
# d - log(d!)/log k <= dimension <= d (from k^d/d! <= C(k+d-1, d) <= k^d), increasing in k on the samples
bounds = all(d - math.log(math.factorial(d)) / math.log(k) - 1e-12 <= dimf(d, k) <= d for d in range(2, 7) for k in KS)
incr = all(dimf(d, a) < dimf(d, b) for d in range(2, 7) for a, b in zip(KS, KS[1:]))
tw_ok &= share and cnt and bounds and incr
report("8 towers: lambda^((n^m-1)/(n-1)) at level m; up simplices share at most one vertex; dimensions log C(k+d-1,d)/log k -> d",
       tw_ok, {"tower factors": tw, "up simplices share <= 1 vertex (d <= 5, k <= 4)": share, "#T = C(k+d-1, d)": cnt,
               "similarity dimension at k = 2, 3, 4, 10, 100, 10^6": dims,
               "d - log(d!)/log k <= dimension <= d, increasing in k": bounds and incr})

# ---------------------------------------------------------------- 9 floating point at several angles
fl = {}
fl_ok = True
for d, ks in ((2, range(2, 7)), (3, range(2, 5)), (4, range(2, 4)), (5, (2,)), (6, (2,))):
    for k in ks:
        for th in (0.37, 1.1, 2 * math.pi / 5, 2.5):
            w = S.wave(d, th)
            lam, err = S.proportional_float(S.corner_relation_float(d, k, w), w)
            good = err < 1e-9
            if (d, k) in polys:
                co = polys[(d, k)]
                y0 = 2 * math.cos(th)
                scale = sum(abs(cf) * abs(y0) ** i for i, cf in enumerate(co))
                good &= abs(S.poly_eval(co, y0) - lam) <= 1e-9 * max(1.0, scale)
            fl_ok &= good
            fl[f"d={d} k={k} theta={th:.4f}"] = [round(lam, 6), f"{err:.1e}"]
report("9 the wave reproduces itself at four angles (floating point), factor = lambda(2 cos theta)", fl_ok, fl)

# ---------------------------------------------------------------- 10 controls
ctrl = {}
L3 = S.legendre(3)
ctrl["the unsigned support of the Legendre law (d = 3) is not exact on SG^3_2"] = not S.proportional_int(S.corner_relation_int(3, 2, abs(L3)), abs(L3))[0]
L3f = L3.copy()
L3f[(0, 0, 0, 1)] = -L3f[(0, 0, 0, 1)]
ctrl["one flipped sign of the Legendre law (d = 3) is not exact on SG^3_2"] = not S.proportional_int(S.corner_relation_int(3, 2, L3f), L3f)[0]
nos = np.abs(S.wave(3, 1.1)) * np.sign(np.array(S.table(3, lambda x: math.sin(1.1 * S.E(x)) / math.sin(1.1)), dtype=float))
ctrl["the wave without (-1)^(x_0) (d = 3, theta = 1.1) is not exact on SG^3_2"] = S.proportional_float(S.corner_relation_float(3, 2, nos), nos)[1] > 1e-6
two = S.wave(4, 0.7) + S.wave(4, 1.3)
ctrl["a sum of two waves (d = 4, theta = 0.7 and 1.3) is not exact on SG^4_2"] = S.proportional_float(S.corner_relation_float(4, 2, two), two)[1] > 1e-6
# in d = 2 and 3 a sum of two waves is again a wave (one free ratio g(3)/g(1), resp. g(4)/g(2)): exact, with y^2 = 2 + g(4)/g(2) here
two3 = S.wave(3, 0.7) + S.wave(3, 1.3)
g2, g4 = two3[(0, 0, 0, 1)], two3[(0, 0, 0, 0)]
y3 = math.sqrt(2 + g4 / g2)
ctrl["(not a control) in d = 3 the sum of two waves is the wave at y^2 = 2 + g(4)/g(2), and exact"] = (
    np.allclose(two3 / g2, np.array(S.wave_at(3, y3), dtype=float) / y3) and S.proportional_float(S.corner_relation_float(3, 2, two3), two3)[1] < 1e-9)
sg = np.array(S.table(4, lambda x: (-1) ** x[0] * int(np.sign(S.E(x)))), dtype=float)
ctrl["(-1)^(x_0) sign(E) on five places (not a wave) is not exact on SG^4_2"] = S.proportional_float(S.corner_relation_float(4, 2, sg), sg)[1] > 1e-6
R0 = S.corner_relation_float(3, 2, S.wave(3, math.pi / 4))
ctrl["at theta = pi/4 (a root of y^2 - 2) the corner relation of SG^3_2 vanishes"] = float(np.max(np.abs(R0))) < 1e-9
report("10 controls fire", all(ctrl.values()), ctrl)

out["lambda_legendre"] = {f"d={d} k={k}": str(v) for (d, k), v in lamL.items()}
out["lambda_polynomials"] = {f"d={d} k={k}": co for (d, k), co in polys.items()}
out["ok"] = ok_all
out["seconds"] = round(time.time() - T0, 1)
print("ALL OK" if ok_all else "SOME CHECK FAILED", out["seconds"], "s")
if "--write" in sys.argv:
    json.dump({"schema_version": 1, "artifact_id": "SIMPLEX-GASKETS-20261029-001A-P001", "status": "Proved" if ok_all else "Failed",
               "checks": out}, open(os.path.join(HERE, "result.json"), "w"), indent=1, default=str)
sys.exit(0 if ok_all else 1)
