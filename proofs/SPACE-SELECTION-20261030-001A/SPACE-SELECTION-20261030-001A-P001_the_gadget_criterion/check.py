"""Checks for SPACE-SELECTION-20261030-001A-P001 (the gadget criterion: when the standing wave reproduces itself on a gluing).

  0 dependency artifacts bound by the hashes recorded in manifest.json
  1 the pencil: (-1)^a sin(theta E)/sin(theta) = K + q M with q = sin(3 theta)/sin(theta) = 1 + 2 cos(2 theta), K signed not-all-equal, M the
    all-equal indicator; its sector form; the cosine wave and the gauge relations between the three pencils
  2 flip parity: every gadget with n <= 5 has sum of base incidences n - 1, so n + N_odd is odd; the standing wave's corner relation is
    flip-invariant and the cosine wave's has parity (-1)^n, so the cosine wave is exact on no gadget with an even number of triangles (n <= 4)
  3 the criterion: the eight functions s_A zeta^(eps . s) are independent iff zeta^4 != 1; for every gadget with n <= 4 the standing wave is
    exact for all q iff the six mixed sector sums vanish identically; Z(+++) has leading term zeta^(3n-3); lambda is monic of degree n - 1
  4 mechanisms (n <= 4, every gadget): locking implies exactness, balanced cancellation implies exactness, locking at pi/3, pi/4, pi/6 implies
    exactness at q = 0, 1, 2 where lambda does not vanish; the Sierpinski gadget is locked, the twin gadget is balanced and not locked (so the
    conjectured criterion 'locking plus odd flip parity' is refuted), and two gadgets with 6 and 7 triangles cancel only algebraically
  5 substitution: exact gadgets compose (lambda multiplies); the level-2 Sierpinski gadget has lambda (q^2 - 1)^4
  6 interference: every 3-graph with at most 9 edges on at most 6 vertices is 2-colourable, and the 7-edge non-2-colourable 3-graphs on 7
    vertices are the 30 labelled Fano planes (3-regular); with Seymour's theorem no nonnegative law with support not-all-equal is exact on a
    gadget with fewer than 7 triangles; the plain knot is exact on no gadget with n <= 4, the signed knot on the Sierpinski gadget
  7 tadpoles: the Pasch tadpole contributes the constant h(q) = (q - 1)(q + 1)(q^2 + 3); attaching one or two to the Sierpinski gadget keeps it
    exact, linear, with lambda multiplied by h and corner growth 2, so growth exponents log(3 + 4j)/log 2 are unbounded
  8 the knot on sectors: at theta = pi/3 a vertex of three triangles with odd base count has factor -i sqrt3 s1 s2 s3 NAE(s); a vertex of two
    with odd base count locks; at generic angle no factor at odd sector sum vanishes
  9 controls that must fire
Run: .venv/bin/python -B check.py [--write]   (sympy, numpy; a few minutes)"""
import hashlib, itertools, json, math, os, sys, time
import numpy as np
import sympy as sp

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
import gadget_lib as G  # noqa: E402

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

TU = G.TU
th, z, qs_ = sp.symbols("theta zeta q")
spin = lambda x: 1 - 2 * x  # noqa: E731

# ---------------------------------------------------------------- 1 the pencil
d1 = {}
qth = sp.sin(3 * th) / sp.sin(th)
d1["q = sin3t/sint = 1 + 2cos2t"] = sp.simplify(sp.expand_trig(qth - 1 - 2 * sp.cos(2 * th))) == 0
ok_pencil = True
for x in TU:
    E = sum(spin(v) for v in x)
    w = (-1) ** x[0] * sp.sin(th * E) / sp.sin(th)
    pen = G.FAM['sine'](x, qth)
    ok_pencil &= sp.simplify(sp.expand_trig(w - pen)) == 0
    # sector form: w = (zeta - 1/zeta)^-1 sum_sigma sigma s_a zeta^(sigma E), zeta = exp(i theta), at three angles to 40 digits
    sec = sum(sg * spin(x[0]) * z ** (sg * E) for sg in (1, -1)) / (z - 1 / z)
    for tv in (sp.Rational(3, 10), sp.Rational(7, 5), sp.Rational(1, 3) + sp.I / 4):
        ok_pencil &= abs(complex(sp.N(sec.subs(z, sp.exp(sp.I * tv)) - w.subs(th, tv), 40))) < 1e-30
d1["(-1)^a sin(theta E)/sin(theta) = K + q M and its sector form, all eight states"] = ok_pencil
ok_cos = True
pth = sp.cos(3 * th) / sp.cos(th)
for x in TU:
    E = sum(spin(v) for v in x)
    ok_cos &= sp.simplify(sp.expand_trig((-1) ** x[0] * sp.cos(th * E) / sp.cos(th) - G.FAM['cosine'](x, pth))) == 0
d1["(-1)^a cos(theta E)/cos(theta) = (-1)^a NAE + p (-1)^a [a=b=c], p = 2cos2t - 1"] = ok_cos
t = sp.Symbol('t')
d1["sine_q = -(s_a s_b s_c) cosine_(-q)"] = all(sp.expand(G.FAM['sine'](x, t) + spin(x[0]) * spin(x[1]) * spin(x[2]) * G.FAM['cosine'](x, -t)) == 0 for x in TU)
d1["sine_q = -(s_b s_c) plain_(-q)"] = all(sp.expand(G.FAM['sine'](x, t) + spin(x[1]) * spin(x[2]) * G.FAM['plain'](x, -t)) == 0 for x in TU)
d1["q = 0 is signed NAE (-1)^a (E|3)"] = all(G.FAM['sine'](x, 0) == (-1) ** x[0] * (0, 1, -1)[sum(spin(v) for v in x) % 3] for x in TU)
report("1 the pencil through the knot and its sector form", all(d1.values()), d1)

# ---------------------------------------------------------------- the gadgets with at most four triangles
ALL = {n: sorted(G.gadgets(n)) for n in (1, 2, 3, 4)}
CX = {n: [G.complex_of(n, k) for k in ALL[n]] for n in ALL}
CLS = {n: [{f: G.classify(G.relation_polys(cx, f), f) for f in G.FAM} for cx in CX[n]] for n in ALL}

# ---------------------------------------------------------------- 2 flip parity
d2 = {"gadget counts n = 1..4": [len(ALL[n]) for n in ALL]}
G5 = G.gadgets(5)
d2["gadget count n = 5"] = len(G5)
par_ok = True
for n, keys in list(ALL.items()) + [(5, sorted(G5))]:
    for k in keys:
        cx = G.complex_of(n, k)
        m = G.base_parity(cx)
        if sum(m.values()) != n - 1 or (n + sum(1 for v in m.values() if v % 2)) % 2 != 1:
            par_ok = False
d2["sum of base incidences = n - 1 and n + N_odd odd (all gadgets n <= 5)"] = par_ok
flip_ok, cos_parity, cos_even_exact = True, True, 0
for n in (3, 4):
    for cx in CX[n]:
        for fam, sgn in (('sine', 1), ('cosine', (-1) ** n)):
            P = G.relation_polys(cx, fam)
            for x in TU:
                y = tuple(1 - b for b in x)
                if P[y] != [sgn * c for c in P[x]]:
                    if fam == 'sine':
                        flip_ok = False
                    else:
                        cos_parity = False
for i, cx in enumerate(CX[4]):
    k, lam, g = CLS[4][i]['cosine']
    if k == 'generic' or (k == 'special' and any(G.exact_at(CLS[4][i]['cosine'], tv) for tv in range(-6, 7))):
        cos_even_exact += 1
d2["standing wave corner relation flip-invariant (n = 3, 4)"] = flip_ok
d2["cosine corner relation has flip parity (-1)^n (n = 3, 4)"] = cos_parity
d2["cosine wave exact on n = 4 gadgets (generic or at integer p)"] = cos_even_exact
report("2 flip parity is automatic; the cosine wave needs an odd number of triangles", par_ok and flip_ok and cos_parity and cos_even_exact == 0, d2)

# ---------------------------------------------------------------- 3 the criterion
d3 = {}
fun = []
for e in itertools.product((1, -1), repeat=3):
    fun.append([spin(x[0]) * z ** (e[0] * spin(x[0]) + e[1] * spin(x[1]) + e[2] * spin(x[2])) for x in TU])
det = sp.factor(sp.Matrix(fun).det())
d3["det of the eight sector functions"] = str(det)
num = sp.Poly(sp.numer(sp.together(det)), z)
roots = [r for r in num.all_roots() if r != 0]
d3["vanishes exactly when zeta^4 = 1"] = bool(roots) and all(sp.simplify(r ** 4 - 1) == 0 for r in roots)
crit_ok, lead_ok, monic_ok, cnt = True, True, True, 0
for n in (1, 3, 4):
    for i, cx in enumerate(CX[n]):
        Z = G.sector_sums(cx)
        mixed_zero = all(not Z[e] for e in Z if G.mixed(e))
        generic = CLS[n][i]['sine'][0] == 'generic'
        crit_ok &= mixed_zero == generic
        top = max(Z[(1, 1, 1)]) if Z[(1, 1, 1)] else None
        lead_ok &= top == 3 * n - 3 and Z[(1, 1, 1)][top] == 1
        lead_ok &= all(Z[tuple(-v for v in e)] == {k: -c for k, c in Z[e].items()} for e in Z)
        if generic:
            lam = CLS[n][i]['sine'][1]
            monic_ok &= len(lam) == n and lam[-1] == 1
            cnt += 1
d3["generic exactness <=> six mixed sector sums vanish identically (all gadgets n <= 4)"] = crit_ok
d3["Z(+++) = zeta^(3n-3) + lower terms, and Z(-eps) = -Z(eps)"] = lead_ok
d3["lambda monic of degree n - 1 on the generic-exact gadgets"] = (monic_ok, cnt)
report("3 exactness is the vanishing of the six mixed sector sums", crit_ok and lead_ok and monic_ok and "zeta" in str(det), d3)

# ---------------------------------------------------------------- 4 mechanisms
d4 = {}
mech_ok, angle_ok = True, True
tally = {}
for n in (1, 3, 4):
    for i, cx in enumerate(CX[n]):
        mech = G.mechanism(cx)
        generic = CLS[n][i]['sine'][0] == 'generic'
        if mech in ('lock', 'balanced') and not generic:
            mech_ok = False
        if generic:
            tally[(n, mech)] = tally.get((n, mech), 0) + 1
        for k, qv in ((3, 0), (4, 1), (6, 2)):
            if G.mechanism(cx, k) == 'lock':
                lam = CLS[n][i]['sine'][1]
                if G.peval(lam, qv) != 0 and not G.exact_at(CLS[n][i]['sine'], qv):
                    angle_ok = False
d4["locked or balanced => exact (all gadgets n <= 4)"] = mech_ok
d4["locked at pi/k => exact at q = 1 + 2cos(2pi/k) where lambda != 0"] = angle_ok
d4["generic-exact by mechanism"] = {f"n={a} {b}": c for (a, b), c in sorted(tally.items())}
SG = G.complex_of(3, G.canonical(3, 1, 2, [((0, 1), (1, 0)), ((0, 2), (2, 0)), ((1, 2), (2, 1))]))
TWIN = G.complex_of(4, G.canonical(4, 0, 1, [((0, 2), (2, 0)), ((1, 0), (2, 1), (3, 0)), ((1, 1), (3, 1)), ((2, 2), (3, 2))]))
cls_sg, cls_tw = G.classify(G.relation_polys(SG, 'sine'), 'sine'), G.classify(G.relation_polys(TWIN, 'sine'), 'sine')
d4["Sierpinski gadget: mechanism, lambda"] = (G.mechanism(SG), cls_sg[0], cls_sg[1])
d4["twin gadget (A,B,v3)(v4,v5,C)(v3,v4,v6)(v4,v5,v6): mechanism, exact, flip parity odd"] = (
    G.mechanism(TWIN), cls_tw[0], (4 + sum(1 for v in G.base_parity(TWIN).values() if v % 2)) % 2 == 1)
ALG = {6: (5, 4, (((0, 1), (1, 2), (3, 1)), ((0, 2), (4, 0)), ((1, 0), (2, 2), (3, 2), (4, 1)), ((1, 1), (2, 0), (5, 0)), ((2, 1), (3, 0), (5, 2)))),
       7: (6, 1, (((0, 1), (4, 2)), ((0, 2), (3, 0)), ((1, 0), (3, 2)), ((1, 1), (2, 0), (5, 0)), ((2, 1), (6, 2)), ((2, 2), (3, 1), (4, 0)),
                  ((4, 1), (5, 1)), ((5, 2), (6, 0))))}
alg_ok = True
for n, key in ALG.items():
    cx = G.complex_of(n, key)
    Z = G.sector_sums(cx)
    c = G.classify(G.relation_polys(cx, 'sine'), 'sine')
    d4[f"{n}-triangle gadget (linear {G.linear(cx)}): mixed sums vanish, generic exact, mechanism"] = (
        all(not Z[e] for e in Z if G.mixed(e)), c[0], G.mechanism(cx))
    alg_ok &= c[0] == 'generic' and G.mechanism(cx) == 'algebraic' and all(not Z[e] for e in Z if G.mixed(e))
report("4 locking and balanced cancellation suffice; neither is necessary",
       mech_ok and angle_ok and d4["Sierpinski gadget: mechanism, lambda"][:2] == ('lock', 'generic') and
       d4["twin gadget (A,B,v3)(v4,v5,C)(v3,v4,v6)(v4,v5,v6): mechanism, exact, flip parity odd"] == ('balanced', 'generic', True) and alg_ok, d4)

# ---------------------------------------------------------------- 5 substitution
d5 = {}
sub_ok = True
lam_sg, lam_tw = cls_sg[1], cls_tw[1]
for name, Gc, t_, H, lamG, lamH in (("SG o_0 twin", SG, 0, TWIN, lam_sg, lam_tw), ("SG o_2 twin", SG, 2, TWIN, lam_sg, lam_tw),
                                    ("twin o_3 SG", TWIN, 3, SG, lam_tw, lam_sg), ("twin o_1 SG", TWIN, 1, SG, lam_tw, lam_sg)):
    comp = G.substitute(Gc, t_, H)
    c = G.classify(G.relation_polys(comp, 'sine'), 'sine')
    d5[name] = (len(comp[1]), c[0], c[1] == G.pmul(lamG, lamH))
    sub_ok &= c[0] == 'generic' and c[1] == G.pmul(lamG, lamH)
SG2 = G.substitute_all(SG, SG)
c2 = G.classify(G.relation_polys(SG2, 'sine'), 'sine')
d5["level-2 Sierpinski gadget: triangles, kind, lambda = (q^2-1)^4"] = (len(SG2[1]), c2[0], c2[1] == G.pmul(G.pmul(lam_sg, lam_sg), G.pmul(lam_sg, lam_sg)))
sub_ok &= c2[0] == 'generic' and d5["level-2 Sierpinski gadget: triangles, kind, lambda = (q^2-1)^4"][2]
report("5 exact gadgets compose under substitution (lambda multiplies)", sub_ok, d5)

# ---------------------------------------------------------------- 6 interference
d6 = {}


def colourable(edges, nv):
    for c in itertools.product((0, 1), repeat=nv - 1):
        col = (0,) + c
        if all(not (col[a] == col[b] == col[e]) for a, b, e in edges):
            return True
    return False


small_ok = True
for nv in (3, 4, 5, 6):
    tr = list(itertools.combinations(range(nv), 3))
    cl = [(0,) + c for c in itertools.product((0, 1), repeat=nv - 1)]
    mk = [sum(1 << i for i, c in enumerate(cl) if c[e[0]] == c[e[1]] == c[e[2]]) for e in tr]
    full = (1 << len(cl)) - 1
    for E in itertools.combinations(range(len(tr)), min(9, len(tr))):
        acc = 0
        for i in E:
            acc |= mk[i]
        if acc == full:
            small_ok = False
            break
d6["every 3-graph with <= 9 edges on <= 6 vertices is 2-colourable"] = small_ok
V7 = list(itertools.combinations(range(7), 3))
cols = [(0,) + c for c in itertools.product((0, 1), repeat=6)]
mono = []
for e in V7:
    mm = 0
    for i, c in enumerate(cols):
        if c[e[0]] == c[e[1]] == c[e[2]]:
            mm |= 1 << i
    mono.append(mm)
FULL = (1 << len(cols)) - 1
found = {}


def rec(start, k, acc, chosen):
    if k == 7:
        if acc == FULL:
            deg = {}
            for i in chosen:
                for v in V7[i]:
                    deg[v] = deg.get(v, 0) + 1
            key = tuple(sorted(deg.values()))
            found[key] = found.get(key, 0) + 1
        return
    for i in range(start, len(V7) - (7 - k) + 1):
        rec(i + 1, k + 1, acc | mono[i], chosen + [i])


rec(0, 0, 0, [])
d6["7-edge non-2-colourable 3-graphs on 7 vertices, by degree sequence"] = {str(k): v for k, v in found.items()}
fano_ok = found == {(3,) * 7: 30}
plain_exact = sum(1 for n in (3, 4) for c in CLS[n] if G.exact_at(c['plain'], 0))
d6["plain NAE exact on gadgets with n = 3, 4"] = plain_exact
d6["signed NAE on the Sierpinski gadget: exact, lambda(0)"] = (G.exact_at(cls_sg, 0), G.peval(cls_sg[1], 0))
report("6 interference: a nonnegative NAE law needs at least 7 triangles, the signed knot 3",
       small_ok and fano_ok and plain_exact == 0 and d6["signed NAE on the Sierpinski gadget: exact, lambda(0)"] == (True, -1), d6)

# ---------------------------------------------------------------- 7 tadpoles
d7 = {}
PASCH = (6, ((0, 1, 2), (0, 3, 4), (1, 3, 5), (2, 4, 5)), (None, None, None))  # vertex 0 is the attachment point p (role a twice)
hp = []
for sp_ in (0, 1):
    tot = 0
    for s in itertools.product((0, 1), repeat=5):
        val = (sp_,) + s
        term = 1
        for tri in PASCH[1]:
            term *= G.FAM['sine'](tuple(val[v] for v in tri), qs_)
        tot += term
    hp.append(sp.expand(tot))
d7["h(s_p) constant, h(q)"] = (hp[0] == hp[1], str(sp.factor(hp[0])))
h_poly = [int(c) for c in reversed(sp.Poly(hp[0], qs_).all_coeffs())]
tad_ok = hp[0] == hp[1] and sp.factor(hp[0]) == sp.factor((qs_ - 1) * (qs_ + 1) * (qs_ ** 2 + 3))
cur = SG
lam_cur = lam_sg
for j in (1, 2):
    cur = G.attach(cur, 3 + (j - 1), PASCH, 0)
    c = G.classify(G.relation_polys(cur, 'sine'), 'sine')
    lam_cur = G.pmul(lam_cur, h_poly)
    rho = G.growth(cur)[0]
    d7[f"SG with {j} Pasch tadpole(s): triangles, linear, kind, lambda = lambda_SG h^{j}, growth, exponent"] = (
        len(cur[1]), G.linear(cur), c[0], c[1] == lam_cur, round(rho, 9), round(math.log(len(cur[1])) / math.log(rho), 4))
    tad_ok &= c[0] == 'generic' and c[1] == lam_cur and abs(rho - 2) < 1e-9 and G.linear(cur)
report("7 tadpoles keep exactness and corner growth: growth exponents are unbounded", tad_ok, d7)

# ---------------------------------------------------------------- 8 the knot on sectors
d8 = {}
zk = sp.exp(sp.I * sp.pi / 3)
ok8 = True
for sg in itertools.product((1, -1), repeat=3):
    S = sum(sg)
    f = sp.nsimplify(sp.simplify(sp.expand_complex(zk ** S - zk ** (-S))))
    nae = 0 if abs(S) == 3 else 1
    ok8 &= sp.simplify(f - (-sp.I * sp.sqrt(3) * sg[0] * sg[1] * sg[2] * nae)) == 0
d8["three triangles, odd base count: f = -i sqrt3 s1 s2 s3 NAE(s1, s2, s3)"] = ok8
lock2 = all((sp.simplify(sp.expand_complex(zk ** (a + b) - zk ** (-(a + b)))) == 0) == (a != b) for a in (1, -1) for b in (1, -1))
d8["two triangles, odd base count: f = 0 iff the sectors differ"] = lock2
d8["even base count at pi/3 never vanishes (degree <= 5)"] = all(sp.simplify(sp.expand_complex(zk ** S + zk ** (-S))) != 0 for S in range(-5, 6))
d8["generic angle: odd S never a zero (degree <= 5)"] = all(sp.expand(z ** S - z ** (-S)) != 0 for S in (-5, -3, -1, 1, 3, 5))
report("8 at the knot angle a three-fold contact acts on the sectors as the NAE knot", all(d8.values()), d8)

# ---------------------------------------------------------------- 9 controls
ctrl = {}
bad = next(cx for i, cx in enumerate(CX[3]) if CLS[3][i]['sine'][0] != 'generic')
Zb = G.sector_sums(bad)
ctrl["a non-exact 3-gadget has a nonzero mixed sector sum"] = any(Zb[e] for e in Zb if G.mixed(e))
ctrl["the eight sector functions are dependent at zeta = i"] = sp.Matrix(fun).subs(z, sp.I).det() == 0
W = G.law_batch('sine')
Wp = W.copy()
Wp[:, 0, 0, 1] += 1
Rp = G.fast_values(SG, Wp)
ctrl["a perturbed law is not exact on the Sierpinski gadget"] = not all(
    all(int(Rp[i][x]) * int(Wp[i][0, 0, 1]) == int(Rp[i][0, 0, 1]) * int(Wp[i][x]) for x in TU) for i in range(len(G.QS)))
ctrl["object and int64 summation agree on the twin gadget"] = bool((G.corner_values(TWIN, W) == G.fast_values(TWIN, W)).all())
report("9 controls fire", all(ctrl.values()), ctrl)

out["ok"] = ok_all
out["seconds"] = round(time.time() - T0, 1)
print("ALL OK" if ok_all else "SOME CHECK FAILED", out["seconds"], "s")
if "--write" in sys.argv:
    json.dump({"schema_version": 1, "artifact_id": "SPACE-SELECTION-20261030-001A-P001", "status": "Proved" if ok_all else "Failed",
               "checks": out}, open(os.path.join(HERE, "result.json"), "w"), indent=1, default=str)
sys.exit(0 if ok_all else 1)
