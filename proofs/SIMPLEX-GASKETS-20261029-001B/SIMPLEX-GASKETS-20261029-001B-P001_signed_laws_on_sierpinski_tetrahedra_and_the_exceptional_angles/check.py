"""Checks for SIMPLEX-GASKETS-20261029-001B-P001 (signed laws on Sierpinski tetrahedra and the exceptional angles).

  0 dependency artifacts bound by the hashes recorded in manifest.json
  1 the census engine agrees with direct enumeration: every census law exact on SG^3_2 or SG^4_2 and 40 random laws there, and 6 laws on SG^3_3
  2 the census: every law f(x_0, m) (m = ones among the non-base corners) with values in {-1, 0, 1}, first nonzero +1, on SG^3_k for k = 2 to 5
    (3,280 laws) and SG^4_k for k = 2, 3 (29,524 laws); exact laws grouped by the levels where they are exact
  3 families: sine waves, cosine waves, parity, and their complement and non-base-flip images; every family law is exact exactly at the levels
    its theorem allows, except where its factor vanishes (listed); the knot laws outside the families are 6 (d = 3) and 2 (d = 4); the knot laws
    exact at every computed level are exactly the standing waves
  4 Theorem 1 (cosine waves): (-1)^(x_0) cos(theta E) reproduces itself when #T is odd and becomes a multiple of the sine wave when #T is even,
    for d = 2 to 6 at three angles (floating point, error relative to the sum of absolute values), and exactly for the integer cases (d = 2: k = 1 to 8; d = 4: k = 1 to 3)
  5 Theorem 2 (theta = pi/4 fails at even levels): y^2 - 2 divides lambda_(d,k) exactly when k is even, in every computed case; floating point
  6 exceptional angles: lambda_(d,k) factored for d = 2 (k <= 8), 3 (k <= 5), 4 (k <= 3); every irreducible factor other than y and y^2 - 2 has a
    non-real root, so its real roots are irrational multiples of pi; the exceptional angles listed
  7 Theorem 4 (parity in every dimension): even parity exact exactly at powers of 2, odd parity exactly at powers of 2 in even dimension (and
    k = 1), factor 2^(C(k+d-1, d-1) - d), for d = 2 (k <= 8), 3 (k <= 5), 4 (k <= 3), 5 (k <= 2)
  8 Lemma 3 (complement always, non-base flip at odd k) on every census law it applies to; the flip fails at even k for the Legendre law
  9 controls that must fire
Run: .venv/bin/python -B check.py [--write]   (numpy, sympy; about five minutes)"""
import hashlib, itertools, json, math, os, random, sys, time
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


# ---------------------------------------------------------------- 0
man = json.load(open(os.path.join(HERE, "manifest.json")))
mism = {r: dg for r, dg in man["parent_bindings"].items()
        if hashlib.sha256(open(os.path.join(ROOT, r), "rb").read()).hexdigest() != dg}
report("0 dependency artifacts bound by hash", not mism, {"parents": len(man["parent_bindings"]), "mismatched": mism})

# ---------------------------------------------------------------- 2 the census (run first; check 1 uses its results)
LEVELS = {3: (2, 3, 4, 5), 4: (2, 3)}
census = {}
for d, ks in LEVELS.items():
    ex = {}
    for vals in S.census_laws(d):
        row = {}
        for k in ks:
            ok, lam = S.is_exact(d, k, vals)
            if ok:
                row[k] = int(lam)
        if row:
            ex[vals] = row
    census[d] = ex
    print(f"   census d = {d}: {len(ex)} exact laws ({time.time() - T0:.0f} s)", flush=True)
groups = {}
for d, ex in census.items():
    g = {}
    for vals, row in ex.items():
        key = ",".join(map(str, sorted(row)))
        g.setdefault(key, {"laws": 0, "knots": 0})
        g[key]["laws"] += 1
        g[key]["knots"] += S.knot_support(d, vals)
    groups[f"d={d}"] = g
report("2 census of the signed laws f(x_0, m) (exact laws by levels; knots among them)",
       len(census[3]) == 75 and len(census[4]) == 75, {"total laws": {"d=3": 3280, "d=4": 29524},
                                                      "exact on some level": {"d=3": len(census[3]), "d=4": len(census[4])}, "by levels": groups})

# ---------------------------------------------------------------- 1 engine against direct enumeration
rng = random.Random(20261029)
bf_ok, bf_n = True, 0
for d, k in ((3, 2), (4, 2)):
    laws = [v for v, row in census[d].items() if k in row]
    pool = list(S.census_laws(d))
    laws += rng.sample(pool, 40)
    for vals in laws:
        W = S.census_table(d, vals)
        bf_ok &= all(S.brute_relation(d, k, W)[x] == int(S.contract(d, k, W)[x]) for x in S.tuples(d))
        bf_n += 1
for vals in [v for v, row in census[3].items() if 3 in row][:3] + rng.sample(list(S.census_laws(3)), 3):
    W = S.census_table(3, vals)
    bf_ok &= all(S.brute_relation(3, 3, W)[x] == int(S.contract(3, 3, W)[x]) for x in S.tuples(3))
    bf_n += 1
report("1 the census engine agrees with direct enumeration", bf_ok, {"laws compared": bf_n})

# ---------------------------------------------------------------- 3 families
nT = lambda d, k: math.comb(k + d - 1, d)
pow2 = lambda k: k & (k - 1) == 0
fam = {}   # vals -> (name, allowed levels by theorem)
for d, ks in LEVELS.items():
    F = {}
    for name, th in (("sine pi/3", math.pi / 3), ("sine pi/6", math.pi / 6), ("sine pi/4", math.pi / 4), ("sine pi/2", math.pi / 2)):
        v = S.wave_law(d, th, "sin")
        if v is not None and v not in F:
            F[v] = (name, set(ks))
    for name, th in (("cosine pi/6", math.pi / 6), ("cosine pi/4", math.pi / 4)):
        v = S.wave_law(d, th, "cos")
        if v is not None and v not in F:
            F[v] = (name, {k for k in ks if nT(d, k) % 2 == 1})
    F[S.parity_law(d, 0)] = ("even parity", {k for k in ks if pow2(k)})
    F[S.parity_law(d, 1)] = ("odd parity", {k for k in ks if pow2(k) and d % 2 == 0})
    base = dict(F)
    for v, (name, lv) in base.items():
        c = S.complement(d, v)
        F.setdefault(c, (name + " (complemented)", lv))
    base = dict(F)
    for v, (name, lv) in base.items():
        W = S.census_table(d, v)
        Wc = S.census_table(d, S.complement(d, v))
        anti = np.array_equal(Wc, W) or np.array_equal(Wc, -W)
        cw = W.copy()
        for x in S.tuples(d):
            cw[x] = W[tuple(1 - b for b in x)]
        if np.array_equal(cw, W) or np.array_equal(cw, -W):
            fv = S.flip(d, v)
            F.setdefault(fv, (name + " (non-base flip)", {k for k in lv if k % 2 == 1}))
    fam[d] = F
fam_ok = True
fam_rep, zeros, sporadic, every = {}, {}, {}, {}
for d, ks in LEVELS.items():
    rows = {}
    for v, (name, lv) in fam[d].items():
        got = set(census[d].get(v, {}))
        rows[f"{name} {S.code(v)}"] = {"knot": S.knot_support(d, v), "allowed": sorted(lv), "exact": sorted(got)}
        fam_ok &= got <= lv
        for k in sorted(lv - got):
            zeros.setdefault(f"d={d}", []).append(f"{name} at k={k}")
    fam_rep[f"d={d}"] = rows
    kn = [v for v in census[d] if S.knot_support(d, v)]
    sporadic[f"d={d}"] = {S.code(v): sorted(census[d][v]) for v in kn if v not in fam[d]}
    every[f"d={d}"] = sorted(fam[d].get(v, ("?",))[0] + " " + S.code(v) for v in kn if set(census[d][v]) == set(ks))
# the levels where a family law is allowed but not exact must be zeros of its factor: checked below by floating point
zero_ok = True
for d, items in zeros.items():
    dd = int(d[2:])
    for it in items:
        name, k = it.rsplit(" at k=", 1)
        k = int(k)
        th = {"pi/3": math.pi / 3, "pi/6": math.pi / 6, "pi/4": math.pi / 4, "pi/2": math.pi / 2}[name.split()[1]]
        f = S.wave(dd, th) if name.startswith("sine") else S.cwave(dd, th)
        if "parity" in name:
            zero_ok = False
            continue
        zero_ok &= float(np.max(np.abs(S.corner_relation_float(dd, k, f)))) < 1e-6
fam_ok &= zero_ok and len(sporadic["d=3"]) == 6 and len(sporadic["d=4"]) == 2
fam_ok &= every["d=3"] == sorted(["sine pi/3 " + S.code(S.wave_law(3, math.pi / 3)), "sine pi/6 " + S.code(S.wave_law(3, math.pi / 6))])
fam_ok &= every["d=4"] == sorted(["sine pi/3 " + S.code(S.wave_law(4, math.pi / 3)), "cosine pi/6 " + S.code(S.wave_law(4, math.pi / 6, "cos"))])
report("3 families exact exactly where their theorems allow (except vanishing factors); sporadic knots 6 and 2; every-level knots = waves", fam_ok,
       {"families": fam_rep, "allowed but factor zero (confirmed by floating point)": zeros, "sporadic knot laws": sporadic,
        "knot laws exact at every computed level": every})

# ---------------------------------------------------------------- 4 Theorem 1: cosine waves
cw_rep, cw_ok, well = {}, True, 0
for d, ks in ((2, range(1, 9)), (3, range(1, 6)), (4, range(1, 4)), (5, (1, 2)), (6, (1, 2))):
    for k in ks:
        for th in (0.37, 1.1, 2.6):
            c, w = S.cwave(d, th), S.wave(d, th)
            R = S.corner_relation_float(d, k, c)
            scale = float(np.max(np.abs(S.corner_relation_float(d, k, np.abs(c)))))   # the sum of absolute values of the terms
            target = c if nT(d, k) % 2 == 1 else w
            t0 = max(S.tuples(d), key=lambda t: abs(target[t]))
            lam = R[t0] / target[t0]
            err = float(np.max(np.abs(R - lam * target))) / scale
            cw_ok &= err < 1e-12
            well += abs(lam) * abs(target[t0]) > 1e-6 * scale
            cw_rep[f"d={d} k={k} theta={th}"] = ["cos" if nT(d, k) % 2 else "sin", float(f"{lam:.6g}"), f"{err:.0e}"]
cw_ok &= well >= 0.9 * len(cw_rep)
# exact: the cosine wave at pi/6 in d = 2 is (-1)^(x_0) [not all equal]; the sine wave at pi/6 is (-1)^(x_0) sign(E) (1 or 2)
C6 = S.table(2, lambda x: (-1) ** x[0] * (1 if abs(S.E(x)) == 1 else 0))
W6 = S.table(2, lambda x: (-1) ** x[0] * (1 if S.E(x) > 0 else -1) * (1 if abs(S.E(x)) == 1 else 2))
ex_rep = {}
for k in range(1, 9):
    R = S.corner_relation_int(2, k, C6)
    ok, lam = S.proportional_int(R, C6 if nT(2, k) % 2 else W6)
    cw_ok &= ok
    ex_rep[f"d=2 k={k}"] = ("cos " if nT(2, k) % 2 else "sin ") + str(lam)
C4 = np.array(S.census_table(4, S.wave_law(4, math.pi / 6, "cos")), dtype=object)
for k in (1, 2, 3):
    ok, lam = S.proportional_int(S.corner_relation_int(4, k, C4), C4)
    cw_ok &= ok
    ex_rep[f"d=4 k={k}"] = "cos " + str(lam)
report("4 Theorem 1: the cosine wave reproduces itself iff #T is odd, else becomes the sine wave", cw_ok,
       {"floating point (form, factor, error relative to the sum of absolute values)": cw_rep, "cases with a clearly nonzero factor": f"{well}/{len(cw_rep)}",
        "exact integers (cosine wave at pi/6)": ex_rep})

# ---------------------------------------------------------------- 5 and 6: the factor polynomials, theta = pi/4, exceptional angles
yv = sp.symbols("y")
PC = [(2, k) for k in range(2, 9)] + [(3, k) for k in range(2, 6)] + [(4, 2), (4, 3)]
polys, ang, p4_ok, irr_ok = {}, {}, True, True
for d, k in PC:
    co = S.lambda_poly(d, k, primes=S.PRIMES)[0]
    co4 = S.lambda_poly(d, k, primes=S.PRIMES[:4])[0]
    irr_ok &= co == co4
    P = sp.Poly(list(reversed(co)), yv)
    polys[(d, k)] = P
    div = sp.rem(P.as_expr(), yv ** 2 - 2, yv) == 0
    p4_ok &= div == (k % 2 == 0)
    facs = sp.factor_list(P.as_expr())[1]
    angles, info = [], []
    for f, mult in facs:
        fp = sp.Poly(f, yv)
        rr = sp.real_roots(fp)
        inside = [r for r in rr if -2 < r < 2]
        if f in (yv, yv ** 2 - 2):
            angles += [0.5] if f == yv else [0.25]
        else:
            irr_ok &= len(rr) < fp.degree()      # a non-real root: no root is 2 cos(r pi) with r rational
            angles += sorted({round(float(sp.acos(sp.N(r, 30) / 2) / sp.pi), 10) for r in inside if r > 0})
        info.append(f"deg {fp.degree()} x{mult}: {len(inside)} roots in (-2,2)")
    ang[f"d={d} k={k}"] = {"factors": info, "exceptional theta/pi in (0, 1/2]": sorted(angles)}
fl4 = {}
for d, ks in ((2, range(2, 9)), (3, range(2, 6)), (4, (2, 3)), (5, (2,))):
    for k in ks:
        m = float(np.max(np.abs(S.corner_relation_float(d, k, S.wave(d, math.pi / 4)))))
        fl4[f"d={d} k={k}"] = "zero" if m < 1e-9 else "nonzero"
        p4_ok &= (m < 1e-9) == (k % 2 == 0)
report("5 Theorem 2: theta = pi/4 is exceptional exactly at the even levels (y^2 - 2 | lambda iff k even)", p4_ok, {"floating point corner relation at pi/4": fl4})
small = [min(a for a in ang[f"d=2 k={k}"]["exceptional theta/pi in (0, 1/2]"]) for k in range(3, 9)]
report("6 exceptional angles: rational ones only pi/2 and pi/4 (even k); every other factor has a non-real root", irr_ok,
       {"per level": ang, "smallest exceptional theta/pi, d = 2, k = 3..8": small,
        "ratios": [round(b / a, 3) for a, b in zip(small, small[1:])]})

# ---------------------------------------------------------------- 7 Theorem 4: parity in every dimension
par, par_ok = {}, True
for d, ks in ((2, range(1, 9)), (3, range(1, 6)), (4, range(1, 4)), (5, (1, 2))):
    for k in ks:
        for b in (0, 1):
            v = S.parity_law(d, b)
            ok, lam = S.is_exact(d, k, v)
            want = pow2(k) and (b == 0 or d % 2 == 0 or k == 1)
            par_ok &= ok == want and (not ok or lam == 2 ** (math.comb(k + d - 1, d - 1) - d))
            par[f"d={d} k={k} {'even' if b == 0 else 'odd'}"] = lam if ok else "not exact"
report("7 Theorem 4: parity exact exactly at powers of 2 (odd parity only in even dimension), factor 2^(C(k+d-1,d-1) - d)", par_ok, par)

# ---------------------------------------------------------------- 8 Lemma 3
lem_ok, lem_n = True, 0
for d, ks in LEVELS.items():
    for v, row in census[d].items():
        W = S.census_table(d, v)
        assert census[d].get(S.complement(d, v)) is not None
        lem_ok &= {k: abs(l) for k, l in census[d][S.complement(d, v)].items()} == {k: abs(l) for k, l in row.items()}
        cw = W.copy()
        for x in S.tuples(d):
            cw[x] = W[tuple(1 - b for b in x)]
        if np.array_equal(cw, W) or np.array_equal(cw, -W):
            fr = census[d].get(S.flip(d, v), {})
            for k, l in row.items():
                if k % 2 == 1:
                    lem_ok &= abs(fr.get(k, 0)) == abs(l)
                    lem_n += 1
L3 = S.wave_law(3, math.pi / 3)
even_fail = all(not S.is_exact(3, k, S.flip(3, L3))[0] for k in (2, 4))
report("8 Lemma 3: complement always, non-base flip at odd k (same |factor|); the flip of the Legendre law fails at k = 2, 4", lem_ok and even_fail,
       {"flip instances checked": lem_n, "flip fails at even k": even_fail})

# ---------------------------------------------------------------- 9 controls
ctrl = {}
ctrl["a random census law is not exact on SG^3_3"] = not S.is_exact(3, 3, (1, -1, 1, 1, 0, 1, -1, 0))[0]
ctrl["the cosine wave at pi/6 (d = 2) is not proportional to itself on SG^2_3 (#T = 6 even)"] = not S.proportional_int(S.corner_relation_int(2, 3, C6), C6)[0]
ctrl["odd parity in d = 3 becomes even parity on SG^3_2"] = S.is_exact(3, 2, S.parity_law(3, 0))[0] and not S.is_exact(3, 2, S.parity_law(3, 1))[0]
report("9 controls fire", all(ctrl.values()), ctrl)

out["census"] = {f"d={d}": {S.code(v): row for v, row in ex.items()} for d, ex in census.items()}
out["lambda_polynomials"] = {f"d={d} k={k}": str(P.as_expr()) for (d, k), P in polys.items() if P.degree() <= 30}
out["ok"] = ok_all
out["seconds"] = round(time.time() - T0, 1)
print("ALL OK" if ok_all else "SOME CHECK FAILED", out["seconds"], "s")
if "--write" in sys.argv:
    json.dump({"schema_version": 1, "artifact_id": "SIMPLEX-GASKETS-20261029-001B-P001", "status": "Proved" if ok_all else "Failed",
               "checks": out}, open(os.path.join(HERE, "result.json"), "w"), indent=1, default=str)
sys.exit(0 if ok_all else 1)
