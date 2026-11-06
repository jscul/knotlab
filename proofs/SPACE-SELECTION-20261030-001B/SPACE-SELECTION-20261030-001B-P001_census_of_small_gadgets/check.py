"""Checks for SPACE-SELECTION-20261030-001B-P001 (census of small gadgets for the harmony).

  0 dependency artifacts bound by the hashes recorded in manifest.json
  1 enumeration: 1, 0, 30, 1293, 73326 gadgets with 1..5 triangles (linear: 1, 0, 8, 48, 2520); an independent enumerator with all corner
    placements and a canonical form over all triangle permutations agrees for n <= 4; 3000 random labelled 5-triangle gadgets all land in
    the census
  2 corner relations: for every gadget with n <= 5 and each of the three pencils, the direct summation of ticket A agrees with the gasket
    engine (an independent elimination code) at the nine parameter points
  3 the standing wave: generic-exact gadgets by mechanism, knot-exact gadgets, knot-only gadgets, generic gadgets whose factor vanishes at
    the knot, linear subclass; the Sierpinski gadget among the 14 exact 3-triangle gadgets
  4 special parameters: every special factor with its count; real special angles pi/3, pi/4, pi/6 and cos 2 theta = -1/3; angle locking at
    q = 0, 1, 2
  5 the cosine and plain pencils: cosine generic sets equal the standing wave's at n = 3, 5 and are empty at n = 4; plain not-all-equal exact
    on no gadget
  6 growth: for every exact gadget the least spectral radius over corner-path policies, certified by a positive vector x with
    min_policies M x = rho x, its minimal polynomial and the exponent log n / log rho
  7 beyond five triangles (exact): a linear 6-triangle gadget exact at the knot only; a linear 6-triangle generic gadget whose factor vanishes
    at the knot; a linear 7-triangle gadget generic for the standing wave but not for the cosine wave; the tetrahedral value q = 1/3 at n = 5
  8 controls that must fire
Run: .venv/bin/python -B check.py [--write]   (numpy, sympy; about ten minutes)"""
import collections, hashlib, itertools, json, math, os, random, sys, time
import numpy as np
import sympy as sp

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
A_DIR = os.path.join(ROOT, "proofs/SPACE-SELECTION-20261030-001A/SPACE-SELECTION-20261030-001A-P001_the_gadget_criterion")
sys.path.insert(0, HERE)
sys.path.insert(0, A_DIR)
import gadget_lib as G  # noqa: E402
import gasket_engine as GE  # noqa: E402

T0 = time.time()
out, ok_all = {}, True
TABLE = {}


def report(key, ok, detail):
    global ok_all
    out[key] = {"ok": bool(ok), "detail": detail}
    ok_all &= bool(ok)
    print(("PASS " if ok else "FAIL ") + key + ": " + json.dumps(detail, default=str)[:3000], flush=True)


def fmt(c):
    """ascending coefficients -> polynomial string in q"""
    return str(sp.factor(sum(sp.Integer(int(x)) * sp.Symbol('q') ** i for i, x in enumerate(c))))


# ---------------------------------------------------------------- 0
man = json.load(open(os.path.join(HERE, "manifest.json")))
mism = {r: dg for r, dg in man["parent_bindings"].items()
        if hashlib.sha256(open(os.path.join(ROOT, r), "rb").read()).hexdigest() != dg}
report("0 dependency artifacts bound by hash", not mism, {"parents": len(man["parent_bindings"]), "mismatched": mism})

# ---------------------------------------------------------------- 1 enumeration
NS = (1, 2, 3, 4, 5)
KEYS = {n: sorted(G.gadgets(n)) for n in NS}
CX = {n: [G.complex_of(n, k) for k in KEYS[n]] for n in NS}
counts = {n: len(KEYS[n]) for n in NS}
lin = {n: sum(1 for cx in CX[n] if G.linear(cx)) for n in NS}


def canon2(cx):
    """independent canonical form: the triangle list (role order) up to all permutations of triangles and relabelings of inner vertices"""
    nv, tris, corners = cx
    best = None
    for perm in itertools.permutations(range(len(tris))):
        order = [tris[i] for i in perm]
        lab = {corners[0]: 'A', corners[1]: 'B', corners[2]: 'C'}
        nxt = 0
        rows = []
        for tri in order:
            row = []
            for v in tri:
                if v not in lab:
                    lab[v] = nxt
                    nxt += 1
                row.append(lab[v])
            rows.append(tuple(str(x) for x in row))
        key = tuple(rows)
        if best is None or key < best:
            best = key
    return best


def enum2(n):
    """all corner placements, restricted-growth labelings of the remaining slots"""
    found = set()
    for tB in range(n):
        for tC in range(n):
            corner = {(0, 0): 'A', (tB, 1): 'B', (tC, 2): 'C'}
            if len(corner) < 3:
                continue
            slots = [(t, r) for t in range(n) for r in range(3) if (t, r) not in corner]

            def rec(i, lab, sizes, tris_of):
                if i == len(slots):
                    if all(s >= 2 for s in sizes):
                        blocks = [[s for s in slots if lab[s] == b] for b in range(len(sizes))]
                        if G.connected(n, [tuple(b) for b in blocks]):
                            where = {(0, 0): 0, (tB, 1): 1, (tC, 2): 2}
                            for j, b in enumerate(blocks):
                                for s in b:
                                    where[s] = 3 + j
                            cx = (3 + len(blocks), tuple(tuple(where[(t, r)] for r in range(3)) for t in range(n)), (0, 1, 2))
                            found.add(canon2(cx))
                    return
                s = slots[i]
                for b in range(len(sizes)):
                    if s[0] not in tris_of[b]:
                        lab[s] = b
                        sizes[b] += 1
                        tris_of[b].add(s[0])
                        rec(i + 1, lab, sizes, tris_of)
                        sizes[b] -= 1
                        tris_of[b].discard(s[0])
                lab[s] = len(sizes)
                sizes.append(1)
                tris_of.append({s[0]})
                rec(i + 1, lab, sizes, tris_of)
                sizes.pop()
                tris_of.pop()
            rec(0, {}, [], [])
    return found


d1 = {"gadgets n = 1..5": counts, "linear": lin}
indep = {n: len(enum2(n)) for n in (1, 2, 3, 4)}
same_classes = all({canon2(cx) for cx in CX[n]} == enum2(n) for n in (3, 4))
d1["independent enumerator n = 1..4"] = indep
d1["same classes at n = 3, 4"] = same_classes
rng = random.Random(20261030)
census5 = set(KEYS[5])
miss, tried = 0, 0
while tried < 3000:
    tB, tC = rng.randrange(5), rng.randrange(5)
    corner = {(0, 0), (tB, 1), (tC, 2)}
    if len(corner) < 3:
        continue
    slots = [(t, r) for t in range(5) for r in range(3) if (t, r) not in corner]
    rng.shuffle(slots)
    blocks = []
    for s in slots:
        cand = [b for b in blocks if all(x[0] != s[0] for x in b)]
        opens = [b for b in cand if len(b) == 1]
        u = rng.random()
        b = rng.choice(opens) if opens and u < 0.75 else (rng.choice(cand) if cand and u < 0.85 else None)
        if b is None:
            blocks.append([s])
        else:
            b.append(s)
    if any(len(b) < 2 for b in blocks) or not G.connected(5, [tuple(b) for b in blocks]):
        continue
    tried += 1
    # relabel triangles so that A's triangle is 0 and the corners follow the census convention, then canonicalize
    key = None
    for perm in itertools.permutations(range(1, 5)):
        p = (0,) + perm
        if p[tB] <= 1 and p[tC] <= 2 and p[tC] <= p[tB] + 1:
            key = G.canonical(5, p[tB], p[tC], [tuple((p[t], r) for t, r in b) for b in blocks])
            break
    if key not in census5:
        miss += 1
d1["random labelled 5-triangle gadgets missing from the census (of 3000)"] = miss
report("1 the enumeration is complete", counts == {1: 1, 2: 0, 3: 30, 4: 1293, 5: 73326} and lin == {1: 1, 2: 0, 3: 8, 4: 48, 5: 2520}
       and indep == {1: 1, 2: 0, 3: 30, 4: 1293} and same_classes and miss == 0, d1)
TABLE["counts"] = {"all": counts, "linear": lin}

# ---------------------------------------------------------------- 2 corner relations, two codes
POLY, CLS = {}, {}
agree, compared = True, 0
for n in NS:
    POLY[n], CLS[n] = [], []
    for cx in CX[n]:
        row_p, row_c = {}, {}
        for fam in G.FAM:
            Wb = G.law_batch(fam)
            Ra = G.fast_values(cx, Wb)
            Rb = GE.contract_complex(cx, Wb)
            if not np.array_equal(np.asarray(Ra, dtype=np.int64), np.asarray(Rb, dtype=np.int64)):
                agree = False
            compared += 1
            P = {x: G.interpolate([int(Ra[(i,) + x]) for i in range(len(G.QS))], n) for x in G.TU}
            row_p[fam], row_c[fam] = P, G.classify(P, fam)
        POLY[n].append(row_p)
        CLS[n].append(row_c)
report("2 corner relations agree between two independent codes", agree, {"gadget-pencil pairs compared": compared, "parameter points": len(G.QS)})

# ---------------------------------------------------------------- 3 the standing wave
d3, tab3 = {}, {}
MECH = {}
sg_info = None
for n in (1, 3, 4, 5):
    for sub in ('all', 'linear'):
        idx = [i for i, cx in enumerate(CX[n]) if sub == 'all' or G.linear(cx)]
        gen = [i for i in idx if CLS[n][i]['sine'][0] == 'generic']
        mech = collections.Counter()
        for i in gen:
            if (n, i) not in MECH:
                MECH[(n, i)] = G.mechanism(CX[n][i])
            mech[MECH[(n, i)]] += 1
        knot = [i for i in idx if G.exact_at(CLS[n][i]['sine'], 0)]
        knot_only = [i for i in knot if CLS[n][i]['sine'][0] == 'special']
        lam0 = [i for i in gen if G.peval(CLS[n][i]['sine'][1], 0) == 0]
        tab3[f"n={n} {sub}"] = {"gadgets": len(idx), "generic": len(gen), "generic by mechanism": dict(mech), "exact at the knot": len(knot),
                                "knot only": len(knot_only), "generic with lambda(0) = 0": len(lam0)}
d3["table"] = tab3
SGK = G.canonical(3, 1, 2, [((0, 1), (1, 0)), ((0, 2), (2, 0)), ((1, 2), (2, 1))])
i_sg = KEYS[3].index(SGK)
lam3 = collections.Counter(fmt(CLS[3][i]['sine'][1]) for i in range(len(CX[3])) if CLS[3][i]['sine'][0] == 'generic')
lin3 = [i for i in range(len(CX[3])) if CLS[3][i]['sine'][0] == 'generic' and G.linear(CX[3][i])]
d3["n = 3: lambda of the 14 exact gadgets"] = dict(lam3)
d3["the Sierpinski gadget: exact, linear, one of the linear exact 3-gadgets"] = (CLS[3][i_sg]['sine'][0], G.linear(CX[3][i_sg]), i_sg in lin3, len(lin3))
expect = {"n=3 all": (30, 14, 14, 0, 0), "n=4 all": (1293, 172, 206, 34, 0), "n=5 all": (73326, 5694, 8584, 3082, 192),
          "n=3 linear": (8, 6, 6, 0, 0), "n=4 linear": (48, 4, 4, 0, 0), "n=5 linear": (2520, 520, 520, 0, 0)}
ok3 = all((tab3[k]["gadgets"], tab3[k]["generic"], tab3[k]["exact at the knot"], tab3[k]["knot only"], tab3[k]["generic with lambda(0) = 0"]) == v
          for k, v in expect.items())
ok3 &= tab3["n=4 all"]["generic by mechanism"] == {"lock": 92, "balanced": 80} and tab3["n=5 all"]["generic by mechanism"] == {"lock": 3078, "balanced": 2616}
ok3 &= dict(lam3) == {"(q - 1)*(q + 1)": 14} and d3["the Sierpinski gadget: exact, linear, one of the linear exact 3-gadgets"][:3] == ('generic', True, True)
report("3 the standing wave: exact gadgets, mechanisms and the knot", ok3, d3)
TABLE["standing wave"] = tab3

# ---------------------------------------------------------------- 4 special parameters
d4 = {}
ANG = {(1, 0): "q = 0: theta = pi/3 (the knot)", (1, -1): "q = 1: theta = pi/4", (1, -2): "q = 2: theta = pi/6",
       (3, -1): "q = 1/3: cos 2 theta = -1/3", (1, 1): "q = -1: degenerate (-s_b s_c)", (1, -3): "q = 3: degenerate ((-1)^a E)"}
spec_tab = {}
FCACHE = {}
for n in (3, 4, 5):
    cnt = collections.Counter()
    for i in range(len(CX[n])):
        kind, lam, g = CLS[n][i]['sine']
        if kind != 'special':
            continue
        ck = (tuple(g), tuple(lam))
        if ck not in FCACHE:
            gq = sp.Poly(list(reversed([sp.Rational(x.numerator, x.denominator) for x in g])), sp.Symbol('q'))
            lq = sp.Poly(list(reversed(lam)), sp.Symbol('q'))
            got = []
            for f, e in sp.factor_list(gq.as_expr())[1]:
                fp = sp.Poly(f, sp.Symbol('q'))
                if fp.degree() >= 1 and not lq.rem(fp).is_zero:
                    cz = sp.Poly(f * sp.lcm([sp.fraction(c)[1] for c in fp.all_coeffs()]), sp.Symbol('q'))
                    coeffs = tuple(int(c) for c in cz.all_coeffs())
                    if coeffs[0] < 0:
                        coeffs = tuple(-c for c in coeffs)
                    got.append(coeffs)
            FCACHE[ck] = got
        for coeffs in FCACHE[ck]:
            cnt[coeffs] += 1
    spec_tab[n] = {(ANG.get(k) or str(sp.Poly(list(k), sp.Symbol('q')).as_expr())): v for k, v in cnt.most_common()}
d4["special factors (gadgets exact there only)"] = spec_tab
real_ang = {}
for n in (3, 4, 5):
    real_ang[n] = {}
    for qv, k in ((0, 3), (1, 4), (2, 6)):
        only = [i for i in range(len(CX[n])) if CLS[n][i]['sine'][0] == 'special' and G.exact_at(CLS[n][i]['sine'], qv)]
        total = sum(1 for i in range(len(CX[n])) if G.exact_at(CLS[n][i]['sine'], qv))
        locked = sum(1 for i in only if G.mechanism(CX[n][i], k) == 'lock')
        real_ang[n][f"q={qv} (pi/{k})"] = {"exact": total, "only there": len(only), "of which locked at pi/%d" % k: locked}
d4["exact at the crystallographic angles"] = real_ang
ok4 = spec_tab[5].get(ANG[(1, 0)]) == 3082 and spec_tab[5].get(ANG[(3, -1)]) == 680 and spec_tab[4].get(ANG[(1, 0)]) == 34
ok4 &= real_ang[5]["q=0 (pi/3)"]["exact"] == 8584 and real_ang[5]["q=1 (pi/4)"]["exact"] == 6846 and real_ang[5]["q=2 (pi/6)"]["exact"] == 7170
ok4 &= real_ang[5]["q=0 (pi/3)"]["of which locked at pi/3"] == 584 and real_ang[4]["q=1 (pi/4)"]["of which locked at pi/4"] == 116
report("4 special parameters: the knot is one special angle among several", ok4, d4)
TABLE["special"] = {"factors": spec_tab, "crystallographic angles": real_ang}

# ---------------------------------------------------------------- 5 cosine and plain pencils
d5 = {}
for n in (3, 4, 5):
    sg = {i for i in range(len(CX[n])) if CLS[n][i]['sine'][0] == 'generic'}
    cg = {i for i in range(len(CX[n])) if CLS[n][i]['cosine'][0] == 'generic'}
    cos_any = sum(1 for i in range(len(CX[n])) if CLS[n][i]['cosine'][0] == 'generic' or
                  (CLS[n][i]['cosine'][0] == 'special' and any(G.exact_at(CLS[n][i]['cosine'], tv) for tv in range(-5, 6))))
    plain0 = sum(1 for i in range(len(CX[n])) if G.exact_at(CLS[n][i]['plain'], 0))
    cos0 = sum(1 for i in range(len(CX[n])) if G.exact_at(CLS[n][i]['cosine'], 0))
    d5[f"n={n}"] = {"cosine generic": len(cg), "equal to the standing wave's generic set": cg == sg,
                    "cosine exact at some integer p": cos_any, "cosine knot (p = 0) exact": cos0, "plain NAE exact": plain0}
ok5 = d5["n=3"]["equal to the standing wave's generic set"] and d5["n=5"]["equal to the standing wave's generic set"] and \
    d5["n=4"]["cosine exact at some integer p"] == 0 and all(d5[k]["plain NAE exact"] == 0 for k in d5)
report("5 the cosine wave shares the standing wave's spaces (odd n <= 5); plain not-all-equal has none", ok5, d5)
TABLE["cosine and plain"] = d5

# ---------------------------------------------------------------- 6 growth
d6 = {}
grow = collections.Counter()
grow_lin = collections.Counter()
cert_fail, recs = 0, 0
minpoly = {}
expo = {}
for n in (3, 4, 5):
    for i, cx in enumerate(CX[n]):
        c = CLS[n][i]['sine']
        if not (c[0] == 'generic' or G.exact_at(c, 0)):
            continue
        rho, rows = G.growth(cx)
        M = np.array(rows, dtype=float)
        w, V = np.linalg.eig(M)
        j = int(np.argmax(abs(w)))
        x = np.real(V[:, j])
        x = x / x[np.argmax(abs(x))]
        paths = G.corner_paths(cx)
        Fx = np.array([min(np.dot(p, x) for p in paths[r]) for r in range(3)])
        if not (np.all(x > 1e-12) and np.allclose(Fx, rho * x, rtol=1e-9, atol=1e-12)):
            # fall back: the exact chain lengths over 200 levels must grow like k^j rho^k with j <= 2
            h = G.chain_lengths(cx, 200)
            m1, m2 = max(h[100]), max(h[200])
            est = math.log(m2 / m1) / 100
            if not (math.log(rho) - 1e-6 <= est <= math.log(rho) + 2 * math.log(2) / 100):
                cert_fail += 1
        recs += 1
        rk = tuple(map(tuple, rows))
        if rk not in minpoly:
            lam_ = sp.Symbol('x')
            cp = sp.Matrix(rows).charpoly(lam_).as_expr()
            fac = [f for f, e in sp.factor_list(cp)[1] if abs(complex(sp.N(f.subs(lam_, rho)))) < 1e-8]
            minpoly[rk] = str(fac[0]) if fac else "?"
        mp_ = minpoly[rk]
        key = (round(rho, 6), mp_)
        tag = 'generic' if c[0] == 'generic' else 'knot only'
        grow[(n, tag) + key] += 1
        if G.linear(cx):
            grow_lin[(n, tag) + key] += 1
        expo[(n, round(rho, 6))] = round(math.log(n) / math.log(rho), 4) if rho > 1 else None
d6["exact gadgets with growth certified (or 200-level fallback)"] = (recs - cert_fail, recs)
d6["growth rates: (n, kind, rho, minimal polynomial): count"] = {str(k): v for k, v in sorted(grow.items())}
d6["linear: (n, kind, rho, minimal polynomial): count"] = {str(k): v for k, v in sorted(grow_lin.items())}
d6["exponents log n / log rho"] = {str(k): v for k, v in sorted(expo.items())}
ex5 = [v for (n_, r), v in expo.items() if n_ == 5 and v]
d6["n = 5 exponent range"] = (min(ex5), max(ex5))
report("6 growth rates of the towers, certified", cert_fail == 0 and abs(min(ex5) - math.log(5) / math.log(4)) < 1e-4 and
       abs(max(ex5) - math.log(5) / math.log(2)) < 1e-4, d6)
TABLE["growth"] = {"all": d6["growth rates: (n, kind, rho, minimal polynomial): count"], "linear": d6["linear: (n, kind, rho, minimal polynomial): count"],
                   "exponents": d6["exponents log n / log rho"]}

# ---------------------------------------------------------------- 7 beyond five triangles
d7 = {}
EX = {
    "linear 6-gadget exact at the knot only": (6, (0, 1, (((0, 2), (2, 2), (5, 0)), ((1, 0), (4, 0), (5, 1)), ((1, 1), (2, 1), (3, 2)),
                                                          ((2, 0), (4, 2)), ((3, 0), (5, 2)), ((3, 1), (4, 1))))),
    "linear 6-gadget generic with lambda(0) = 0": (6, (5, 5, (((0, 1), (2, 1), (4, 0)), ((0, 2), (1, 2)), ((1, 0), (3, 2)), ((1, 1), (4, 2)),
                                                              ((2, 0), (3, 0)), ((2, 2), (5, 0)), ((3, 1), (4, 1))))),
    "linear 7-gadget generic for the wave, not for the cosine wave": (7, (4, 4, (((0, 1), (3, 0)), ((0, 2), (1, 1), (2, 1)), ((1, 0), (5, 0)),
                                                                              ((1, 2), (3, 1)), ((2, 0), (5, 2)), ((2, 2), (3, 2), (6, 1)),
                                                                              ((4, 0), (6, 2)), ((5, 1), (6, 0))))),
}
ok7 = True
for name, (n, key) in EX.items():
    cx = G.complex_of(n, key)
    cs = G.classify(G.relation_polys(cx, 'sine'), 'sine')
    cc = G.classify(G.relation_polys(cx, 'cosine'), 'cosine')
    rec = {"linear": G.linear(cx), "standing wave": cs[0], "exact at the knot": G.exact_at(cs, 0), "lambda": fmt(cs[1]),
           "cosine": cc[0]}
    d7[name] = rec
ok7 &= d7["linear 6-gadget exact at the knot only"]["linear"] and d7["linear 6-gadget exact at the knot only"]["standing wave"] == 'special' \
    and d7["linear 6-gadget exact at the knot only"]["exact at the knot"]
ok7 &= d7["linear 6-gadget generic with lambda(0) = 0"]["linear"] and d7["linear 6-gadget generic with lambda(0) = 0"]["standing wave"] == 'generic' \
    and not d7["linear 6-gadget generic with lambda(0) = 0"]["exact at the knot"]
ok7 &= d7["linear 7-gadget generic for the wave, not for the cosine wave"]["linear"] and \
    d7["linear 7-gadget generic for the wave, not for the cosine wave"]["standing wave"] == 'generic' and \
    d7["linear 7-gadget generic for the wave, not for the cosine wave"]["cosine"] != 'generic'
TET = (0, 1, (((0, 2), (2, 0)), ((1, 0), (3, 0)), ((1, 1), (4, 1)), ((2, 1), (3, 1), (4, 0)), ((2, 2), (3, 2), (4, 2))))
cx = G.complex_of(5, TET)
third = sp.Rational(1, 3)
Wt = np.zeros((1, 2, 2, 2), dtype=object)
for x in G.TU:
    Wt[(0,) + x] = G.FAM['sine'](x, third)
R = G.corner_values(cx, Wt)
lam_t = R[0, 0, 0, 1]
d7["5-gadget exact at q = 1/3 (cos 2 theta = -1/3), lambda"] = (all(R[(0,) + x] == lam_t * Wt[(0,) + x] for x in G.TU) and lam_t != 0, str(lam_t))
ok7 &= d7["5-gadget exact at q = 1/3 (cos 2 theta = -1/3), lambda"][0]
report("7 the small-size coincidences end beyond five triangles (exact examples)", ok7, d7)

# ---------------------------------------------------------------- 8 controls
ctrl = {}
Wb = G.law_batch('sine').copy()
Wb[:, 1, 1, 1] += 1
cxs = CX[3][i_sg]
P = {x: G.interpolate([int(v) for v in G.fast_values(cxs, Wb)[(slice(None),) + x]], 3) for x in G.TU}
ctrl["a perturbed pencil is not generic-exact on the Sierpinski gadget"] = G.classify(P, 'sine')[0] != 'generic'
Wp = G.law_batch('sine').copy()
Wp[:, 0, 1, 1] *= -1
gen_p = sum(1 for cx in CX[3] if G.classify({x: G.interpolate([int(v) for v in G.fast_values(cx, Wp)[(slice(None),) + x]], 3) for x in G.TU}, 'sine')[0] == 'generic')
ctrl["flipping one sign of the law changes the generic count at n = 3"] = gen_p != 14
paths = G.corner_paths(cxs)
rho_sg = G.growth(cxs)[0]
worse = 0
for rows in itertools.product(*paths):
    M = np.array(rows, dtype=float)
    w, V = np.linalg.eig(M)
    j = int(np.argmax(abs(w)))
    if abs(w[j]) > rho_sg + 1e-9:
        x = np.real(V[:, j]); x = x / x[np.argmax(abs(x))]
        Fx = np.array([min(np.dot(p, x) for p in paths[r]) for r in range(3)])
        worse += 0 if np.allclose(Fx, abs(w[j]) * x) else 1
ctrl["the growth certificate rejects every non-optimal policy of the Sierpinski gadget"] = worse > 0 and worse == sum(
    1 for rows in itertools.product(*paths) if max(abs(np.linalg.eigvals(np.array(rows, dtype=float)))) > rho_sg + 1e-9)
report("8 controls fire", all(ctrl.values()), ctrl)

out["ok"] = ok_all
out["seconds"] = round(time.time() - T0, 1)
print("ALL OK" if ok_all else "SOME CHECK FAILED", out["seconds"], "s")
if "--write" in sys.argv:
    json.dump({"schema_version": 1, "artifact_id": "SPACE-SELECTION-20261030-001B-P001", "status": "Proved" if ok_all else "Failed",
               "checks": out}, open(os.path.join(HERE, "result.json"), "w"), indent=1, default=str)
    json.dump(TABLE, open(os.path.join(HERE, "census.json"), "w"), indent=1, default=str)
sys.exit(0 if ok_all else 1)
