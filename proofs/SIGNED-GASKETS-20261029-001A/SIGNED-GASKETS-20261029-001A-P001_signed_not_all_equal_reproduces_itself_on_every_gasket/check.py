"""Checks for SIGNED-GASKETS-20261029-001A-P001 (signed not-all-equal reproduces itself on every level-k Sierpinski gasket).

The proof is in proof.md; these checks replay every finite ingredient and test the theorems on the levels that can be computed.
  0 dependency artifacts bound by the hashes recorded in manifest.json
  1 closed forms of the law on all eight tuples: (-1)^((a xor b)(a xor c)) - [a=b=c] = (-1)^a ((a+b+c)|3) = (-1)^a sin(pi E/3)/sin(pi/3)
    = (-1)^a (w^E - w^-E)/(w - w^-1) with w = exp(i pi/3); 4 w = 1 + s_a s_b + s_a s_c - 3 s_b s_c in spins; the product of the
    Eisenstein field in the basis (omega, omega-bar), a-corner as output; the row matrices M_c = w(., ., c): M_0 M_1 = I = M_0 + M_1,
    M_0^3 = -I
  2 exactness: the corner relation of SG_k is lambda_k w, exactly (integers by the Chinese remainder theorem), for k = 1 to 14
  3 the sector formula for lambda_k (Theorem 2's proof) equals the direct value for k = 1 to 7
  4 the family w_theta: R_k = lambda_k(theta) w_theta for k = 1 to 7 at six angles (floating point, relative error below 1e-9),
    with lambda nonzero at generic angles and zero at theta = pi/2; and symbolically in zeta = exp(i theta) for k = 2 and 3; the
    support of w_theta is the full cube except at theta = pi/3 (mod pi), where it is not-all-equal
  5 modulo 3: R_k = (-1)^(N_k) w for k = 1 to 21, N_k = (k+1)(k+2)/2 - 3, so lambda_k = (-1)^floor(k/2) mod 3
  6 the edge-set lemma: for k = 1 to 4 the edge sets with even degree off the corners are exactly the empty set, the bottom row and the
    left column
  7 the corner relation's support (not-all-equal) is a knot under K1-K3 (knotlab check)
  8 controls that must fire: unsigned not-all-equal is not exact on SG_2; one flipped sign breaks exactness on SG_3; dropping the factor
    (-1)^a from w_theta breaks exactness on SG_2
Run: .venv/bin/python -B check.py [--write]   (numpy, sympy)"""
import cmath, hashlib, itertools, json, math, os, subprocess, sys, time
import numpy as np
import sympy as sp

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
import gasket_lib as G  # noqa: E402

T0 = time.time()
out, ok_all = {}, True


def report(key, ok, detail):
    global ok_all
    out[key] = {"ok": bool(ok), "detail": detail}
    ok_all &= bool(ok)
    print(("PASS " if ok else "FAIL ") + key + ": " + json.dumps(detail, default=str)[:2500], flush=True)


W = G.NAE_SIGNED
TU = G.TUPLES
idx = lambda t: t[0] * 4 + t[1] * 2 + t[2]

# ---------------------------------------------------------------- 0
man = json.load(open(os.path.join(HERE, "manifest.json")))
mism = {r: d for r, d in man["parent_bindings"].items()
        if hashlib.sha256(open(os.path.join(ROOT, r), "rb").read()).hexdigest() != d}
report("0 dependency artifacts bound by hash", not mism, {"parents": len(man["parent_bindings"]), "mismatched": mism})

# ---------------------------------------------------------------- 1 closed forms
leg = lambda n: (0, 1, -1)[n % 3]
om = cmath.exp(1j * math.pi / 3)
c1 = all(W[idx(t)] == (-1) ** ((t[0] ^ t[1]) & (t[0] ^ t[2])) - (1 if t[0] == t[1] == t[2] else 0) for t in TU)
c2 = all(W[idx(t)] == (-1) ** t[0] * leg(sum(t)) for t in TU)
E = lambda t: sum((-1) ** x for x in t)
c3 = all(abs(W[idx(t)] - (-1) ** t[0] * math.sin(math.pi * E(t) / 3) / math.sin(math.pi / 3)) < 1e-12 for t in TU)
c4 = all(abs(W[idx(t)] - (-1) ** t[0] * (om ** E(t) - om ** (-E(t))) / (om - 1 / om)) < 1e-12 for t in TU)
s = lambda x: (-1) ** x
c5 = all(4 * W[idx(t)] == 1 + s(t[0]) * s(t[1]) + s(t[0]) * s(t[2]) - 3 * s(t[1]) * s(t[2]) for t in TU)
x = sp.symbols("x")
mod = sp.Poly(x ** 2 - x + 1, x)  # omega = x, omega-bar = 1 - x
e = {0: sp.Poly(x, x), 1: sp.Poly(1 - x, x)}
def coords(p):  # p = c1 x + c0 = alpha x + beta (1 - x)  ->  (alpha, beta) = (c1 + c0, c0)
    r = p.rem(mod)
    c1, c0 = r.coeff_monomial(x), r.coeff_monomial(1)
    return (c1 + c0, c0)
c6 = all(coords(e[b] * e[c]) == (W[idx((0, b, c))], W[idx((1, b, c))]) for b in (0, 1) for c in (0, 1))
M = {c: np.array([[W[idx((p, q, c))] for q in (0, 1)] for p in (0, 1)]) for c in (0, 1)}
I2 = np.eye(2, dtype=int)
c7 = (M[0] @ M[1] == I2).all() and (M[0] + M[1] == I2).all() and (np.linalg.matrix_power(M[0], 3) == -I2).all()
report("1 closed forms of signed not-all-equal",
       c1 and c2 and c3 and c4 and c5 and c6 and c7,
       {"(-1)^((a^b)(a^c)) - [a=b=c]": c1, "(-1)^a ((a+b+c)|3)": c2, "(-1)^a sin(pi E/3)/sin(pi/3)": c3,
        "two Eisenstein phases": c4, "4w in spins": c5, "Eisenstein product, a as output": c6,
        "row matrices M_0 M_1 = I = M_0 + M_1, M_0^3 = -I": c7})

# ---------------------------------------------------------------- 2 exactness, exact integers
lams = {}
exact_all = True
for k in range(1, 15):
    R = G.corner_relation(k, W)
    ok, lam = G.proportional(R, W)
    lams[k] = lam
    exact_all &= ok
report("2 exact on SG_k for k = 1 to 14 (exact integers)", exact_all, {"lambda_k": lams})

# ---------------------------------------------------------------- 3 sector formula
sec = {k: G.sector_lambda(k) for k in range(1, 8)}
report("3 sector formula equals the direct factor for k = 1 to 7", all(sec[k] == lams[k] for k in sec), {"sector formula": sec})

# ---------------------------------------------------------------- 4 the family w_theta
fam = {}
fam_ok = True
for theta in (0.3, 0.7, 1.1, math.pi / 3, 2.0, 2.7):
    wt = G.w_theta(theta)
    row = {}
    for k in range(1, 8):
        R = G.corner_relation_float(k, wt)
        t0 = max(TU, key=lambda t: abs(wt[idx(t)]))
        lam = R[t0] / wt[idx(t0)]
        err = max(abs(R[t] - lam * wt[idx(t)]) for t in TU) / max(1e-300, max(abs(R[t]) for t in TU))
        row[k] = (float(lam), float(err))
        fam_ok &= err < 1e-9 and abs(lam) > 1e-9
    fam[f"{theta:.4f}"] = row
R_half = G.corner_relation_float(3, G.w_theta(math.pi / 2))
half_zero = float(np.abs(R_half).max()) < 1e-9
supp = {f"{th:.4f}": [ "".join(map(str, t)) for t in TU if abs(G.w_theta(th)[idx(t)]) < 1e-12] for th in (0.3, 0.7, 1.1, math.pi / 3, 2.0, 2 * math.pi / 3)}
supp_ok = all((v == ["000", "111"]) == (abs(float(th) - math.pi / 3) < 1e-3 or abs(float(th) - 2 * math.pi / 3) < 1e-3) for th, v in supp.items())
z = sp.symbols("z")
def wsym(t):
    Ev = E(t)
    return sp.cancel((-1) ** t[0] * (z ** Ev - z ** (-Ev)) / (z - 1 / z))
def sym_relation(k):
    Vv = [(i, j) for i in range(k + 1) for j in range(k + 1 - i)]
    tris = [((i, j), (i + 1, j), (i, j + 1)) for i in range(k) for j in range(k - i)]
    corners = [(0, 0), (k, 0), (0, k)]
    internal = [v for v in Vv if v not in corners]
    ws = {t: wsym(t) for t in TU}
    R = {}
    for cv in TU:
        tot = 0
        for bits in itertools.product((0, 1), repeat=len(internal)):
            val = dict(zip(internal, bits)); val.update(zip(corners, cv))
            term = 1
            for (a, b, c) in tris:
                term *= ws[(val[a], val[b], val[c])]
            tot += term
        R[cv] = sp.cancel(tot)
    return R, ws
sym_ok = True
for k in (2, 3):
    R, ws = sym_relation(k)
    t0 = (0, 0, 1)
    lam = sp.cancel(R[t0] / ws[t0])
    sym_ok &= all(sp.cancel(R[t] - lam * ws[t]) == 0 for t in TU)
report("4 the family w_theta reproduces itself on every SG_k tested",
       fam_ok and half_zero and supp_ok and sym_ok,
       {"lambda_k(theta) and relative error": fam, "theta = pi/2 gives R = 0 on SG_3": half_zero,
        "zero tuples of w_theta (knot support only at pi/3 and 2 pi/3)": supp, "symbolic in zeta, k = 2 and 3": sym_ok})

# ---------------------------------------------------------------- 5 modulo 3
m3 = {}
m3_ok = True
for k in range(1, 22):
    R3 = G.corner_relation_mod(k, W, 3)
    Nk = (k + 1) * (k + 2) // 2 - 3
    sign = (-1) ** Nk
    m3_ok &= all((R3[t] - sign * W[idx(t)]) % 3 == 0 for t in TU) and (sign - (-1) ** (k // 2)) % 3 == 0
    m3[k] = int(R3[0, 0, 1]) % 3
report("5 modulo 3 the corner relation is (-1)^N_k w (k = 1 to 21)", m3_ok and all((lams[k] - m3[k]) % 3 == 0 for k in lams),
       {"lambda_k mod 3": m3})

# ---------------------------------------------------------------- 6 the edge-set lemma
lem = {}
lem_ok = True
for k in range(1, 5):
    sets = G.even_edge_sets(k)
    bottom = frozenset(((i, 0), (i + 1, 0)) for i in range(k))
    left = frozenset(((0, j), (0, j + 1)) for j in range(k))
    lem[k] = len(sets)
    lem_ok &= set(sets) == {frozenset(), bottom, left}
report("6 edge-set lemma: only the empty set, the bottom row and the left column (k = 1 to 4)", lem_ok, {"edge sets found": lem})

# ---------------------------------------------------------------- 7 knot check
env = dict(os.environ, PYTHONPATH=os.path.join(ROOT, "tools"))
kl = subprocess.run([sys.executable, "-B", "-m", "knotlab", "check", "--cnf", "a b c; ~a ~b ~c", "--loops", "a", "b", "--contact", "c", "--json"],
                    capture_output=True, text=True, env=env, cwd=ROOT)
kj = json.loads(kl.stdout)
report("7 the support of the corner relation is a knot (K1-K3)", kj["is_knot"] and sorted(kj["allowed"]) == ["001", "010", "011", "100", "101", "110"],
       {k: kj[k] for k in ("is_knot", "binding", "invisible_in_parts", "loss_on_erasure", "coexistence", "allowed")})

# ---------------------------------------------------------------- 8 controls
ctrl = {}
unsigned = G.law(set(), {"000", "111"})
ctrl["unsigned not-all-equal is not exact on SG_2"] = not G.proportional(G.corner_relation(2, unsigned), unsigned)[0]
flip = G.law({"011"}, {"000", "111"})
ctrl["one flipped sign (only 011 negative) is not exact on SG_3"] = not G.proportional(G.corner_relation(3, flip), flip)[0]
nosign = [math.sin(1.1 * E(t)) / math.sin(1.1) for t in TU]
Rn = G.corner_relation_float(2, nosign)
t0 = max(TU, key=lambda t: abs(nosign[idx(t)]))
lamn = Rn[t0] / nosign[idx(t0)]
ctrl["w_theta without (-1)^a is not exact on SG_2"] = max(abs(Rn[t] - lamn * nosign[idx(t)]) for t in TU) > 1e-6
report("8 controls fire", all(ctrl.values()), ctrl)

out["lambda"] = {str(k): str(v) for k, v in lams.items()}
out["ok"] = ok_all
out["seconds"] = round(time.time() - T0, 1)
print("ALL OK" if ok_all else "SOME CHECK FAILED", out["seconds"], "s")
if "--write" in sys.argv:
    json.dump({"schema_version": 1, "artifact_id": "SIGNED-GASKETS-20261029-001A-P001", "status": "Proved" if ok_all else "Failed",
               "checks": out}, open(os.path.join(HERE, "result.json"), "w"), indent=1, default=str)
sys.exit(0 if ok_all else 1)
