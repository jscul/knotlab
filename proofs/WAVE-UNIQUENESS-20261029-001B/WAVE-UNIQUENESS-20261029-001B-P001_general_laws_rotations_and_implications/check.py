"""Checks for WAVE-UNIQUENESS-20261029-001B-P001 (general three-bit laws: rotations of the wave and implication laws).

  0 dependency artifacts bound by the hashes recorded in manifest.json
  1 level 2 for two-sector laws u1 v1 y1 + u2 v2 y2: R_2 = sum C_ijk u_i v_j y_k with C_ijk = <v_i, u_j><y_i, u_k><y_j, v_k> (symbolic)
  2 the hexagon: the six off-diagonal conditions are the edges of a hexagon on the six cross pairings; exactly five minimal vertex covers
    (three of size four, two of size three); each size-four cover makes the law symmetric in a pair of roles (random instances)
  3 the cyclic branch (u2 = J v1, v2 = J y1, y2 = J u1, ratio c) in all eight coordinate charts: level 2 holds exactly for c = +-1, level 3
    exactly when one of u1, v1, y1 is a coordinate vector (c = 1 for e0, c = -1 for e1)
  4 implication laws: the vanishing pairings behind the closure argument (symbolic); every one of the twelve types (rotations, complement,
    reflection of e0 v y + Jv Jy e1) is exact at every level 2 to 9 with factor <v, y>^(k-1) (exact integers)
  5 rank one in a corner: R_k = u (x) M^k times a scalar for w = u(a) M[b][c] (k = 2, 3, symbolic), so exactness forces M^2 = cM: products and
    u(a)[b = c]; the images in the other corners are exact at levels 2 to 8
  6 knots: the implication laws and the rank-one laws have no knot support; the rotations of signed not-all-equal are the knots that persist
  7 controls that must fire
Run: .venv/bin/python -B check.py [--write]   (sympy, numpy; about a minute)"""
import hashlib, itertools, json, os, random, sys, time
import numpy as np
import sympy as sp

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
ADIR = os.path.join(ROOT, "proofs/WAVE-UNIQUENESS-20261029-001A/WAVE-UNIQUENESS-20261029-001A-P001_symmetric_laws_four_levels_force_the_wave")
sys.path.insert(0, ADIR)
import general_lib as GL  # noqa: E402
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

R2, R3 = GL.relation(2), GL.relation(3)
TU = GL.TU

# ---------------------------------------------------------------- 1 level 2 coefficient identity
S = sp.symbols("u10 u11 v10 v11 y10 y11 u20 u21 v20 v21 y20 y21")
u = {1: S[0:2], 2: S[6:8]}
v = {1: S[2:4], 2: S[8:10]}
y = {1: S[4:6], 2: S[10:12]}
w = GL.two_sector(u[1], v[1], y[1], u[2], v[2], y[2])
direct = {t: sp.expand(R2[t].subs({GL.G[s]: w[s] for s in TU})) for t in TU}
pred = {t: sp.expand(sum(GL.dot(v[i], u[j]) * GL.dot(y[i], u[k]) * GL.dot(y[j], v[k]) * u[i][t[0]] * v[j][t[1]] * y[k][t[2]]
                         for i in (1, 2) for j in (1, 2) for k in (1, 2))) for t in TU}
report("1 level 2: R_2 = sum <v_i,u_j><y_i,u_k><y_j,v_k> u_i v_j y_k for every two-sector law", all(direct[t] == pred[t] for t in TU),
       {"symbolic identity in twelve vector entries": True})

# ---------------------------------------------------------------- 2 the hexagon
# cross pairings: X1=<v1,u2> X2=<v2,u1> Y1=<y1,u2> Y2=<y2,u1> Z1=<y1,v2> Z2=<y2,v1>
names = ["X1", "X2", "Y1", "Y2", "Z1", "Z2"]
def cross(i, j, k):
    """the factors of C_ijk that are cross pairings (diagonal ones are nonzero)"""
    f = []
    for (a_, b_), kind in (((i, j), "vu"), ((i, k), "yu"), ((j, k), "yv")):
        if a_ != b_:
            f.append({("vu", 1, 2): "X1", ("vu", 2, 1): "X2", ("yu", 1, 2): "Y1", ("yu", 2, 1): "Y2", ("yv", 1, 2): "Z1", ("yv", 2, 1): "Z2"}[(kind, a_, b_)])
    return f
constraints = [set(cross(i, j, k)) for i, j, k in itertools.product((1, 2), repeat=3) if not i == j == k]
covers = [set(c_) for r_ in range(7) for c_ in itertools.combinations(names, r_) if all(set(c_) & con for con in constraints)]
minimal = [c_ for c_ in covers if not any(o < c_ for o in covers)]
sizes = sorted(len(c_) for c_ in minimal)
edges = sorted(tuple(sorted(con)) for con in constraints)
# size-four covers force a pair symmetry: build random instances and test
rng = random.Random(20261029)
def rv():
    return (rng.randint(-5, 5) + 1j * rng.randint(-5, 5), rng.randint(-5, 5) + 1j * rng.randint(-5, 5))
sym_ok = True
for c_ in [c_ for c_ in minimal if len(c_) == 4]:
    for _ in range(3):
        if c_ == {"X1", "X2", "Y1", "Y2"}:          # u2 orthogonal to v1, y1; u1 to v2, y2: v_i parallel y_i
            v1_, v2_ = rv(), rv(); w_ = GL.two_sector(GL.J(v2_), v1_, v1_, GL.J(v1_), v2_, v2_); pair = (1, 2)
        elif c_ == {"X1", "X2", "Z1", "Z2"}:        # u_i parallel y_i
            v1_, v2_ = rv(), rv(); w_ = GL.two_sector(GL.J(v2_), v1_, GL.J(v2_), GL.J(v1_), v2_, GL.J(v1_)); pair = (0, 2)
        else:                                       # Y1 Y2 Z1 Z2: u_i parallel v_i
            y1_, y2_ = rv(), rv(); w_ = GL.two_sector(GL.J(y2_), GL.J(y2_), y1_, GL.J(y1_), GL.J(y1_), y2_); pair = (0, 1)
        pr = [0, 1, 2]; pr[pair[0]], pr[pair[1]] = pr[pair[1]], pr[pair[0]]
        sym_ok &= all(abs(w_[t] - GL.permute(w_, pr)[t]) < 1e-9 for t in TU)
        # and the cover's pairings vanish
report("2 the hexagon of cross pairings has exactly five minimal covers; the three of size four force a pair symmetry",
       sizes == [3, 3, 4, 4, 4] and sym_ok and len(edges) == 6,
       {"constraints (edges)": edges, "minimal covers": [sorted(c_) for c_ in minimal], "size-four covers give pair-symmetric laws": sym_ok})

# ---------------------------------------------------------------- 3 the cyclic branch in eight charts
x1, x2, x3, c, t = sp.symbols("x1 x2 x3 c t")
def vec(x, ch):
    return (1, x) if ch == 0 else (x, 1)
cyc = {}
cyc_ok = True
for ch in itertools.product((0, 1), repeat=3):
    U, V, Y = vec(x1, ch[0]), vec(x2, ch[1]), vec(x3, ch[2])
    law = {k_: sp.expand(val) for k_, val in GL.cyclic(U, V, Y, c).items()}
    Dg = sp.expand(GL.dot(U, V) * GL.dot(U, Y) * GL.dot(V, Y))
    mins = {}
    for lev, R in (("2", R2), ("3", R3)):
        r = {k_: sp.expand(R[k_].subs({GL.G[s]: law[s] for s in TU})) for k_ in TU}
        mins[lev] = [m_ for m_ in (sp.expand(r[TU[i]] * law[TU[j]] - r[TU[j]] * law[TU[i]]) for i in range(8) for j in range(i + 1, 8)) if m_ != 0]
    g2 = sp.groebner(mins["2"] + [t * Dg * c - 1], t, x1, x2, x3, c, order="lex")
    lvl2 = sorted(str(sp.factor(g_)) for g_ in g2.exprs if t not in g_.free_symbols)
    res = {"level 2": lvl2}
    for cv in (1, -1):
        eqs = [e_ for e_ in (sp.expand(m_.subs(c, cv)) for m_ in mins["3"]) if e_ != 0]
        g3 = sp.groebner(eqs + [t * Dg - 1], t, x1, x2, x3, order="lex")
        res[f"level 3, c = {cv}"] = "none" if g3.exprs == [1] else sorted(str(sp.factor(g_)) for g_ in g3.exprs if t not in g_.free_symbols)
    # expected: coordinate vectors: chart 0 coordinate x = 0 gives e0 (c = 1); chart 1 coordinate x = 0 gives e1 (c = -1)
    e0 = sorted(f"x{i+1}" for i in range(3) if ch[i] == 0)
    e1 = sorted(f"x{i+1}" for i in range(3) if ch[i] == 1)
    def prod(vs):
        return "none" if not vs else ["*".join(vs)]
    cyc_ok &= lvl2 == ["(c - 1)*(c + 1)"] and res["level 3, c = 1"] == prod(e0) and res["level 3, c = -1"] == prod(e1)
    cyc[str(ch)] = res
report("3 the cyclic branch: level 2 exactly c = +-1; level 3 exactly when a first-sector vector is a coordinate vector", cyc_ok, cyc)

# ---------------------------------------------------------------- 4 implication laws
s_, t_ = sp.symbols("s t")
vv, yy = (1, s_), (1, t_)
u1_, u2_ = (1, 0), GL.J(vv)
v1_, v2_ = vv, GL.J(yy)
y1_, y2_ = yy, (0, 1)
zero_pairs = [GL.dot(u2_, v1_), GL.dot(u1_, y2_), GL.dot(y1_, v2_), sum(u1_[x_] * v2_[x_] * y2_[x_] for x_ in (0, 1)),
              sum(u1_[x_] * v1_[x_] * y2_[x_] for x_ in (0, 1))]
mu_ = GL.dot(vv, yy)
weights_all = {"all 1: bottom <u1,v1>, left <u1,y1>, top <y1,v1>, inner": [GL.dot(u1_, v1_), GL.dot(u1_, y1_), sp.expand(GL.dot(y1_, v1_)),
                                                                       sum(u1_[x_] * v1_[x_] * y1_[x_] for x_ in (0, 1))],
               "all 2": [sp.expand(GL.dot(u2_, v2_)), GL.dot(u2_, y2_), GL.dot(y2_, v2_), sum(u2_[x_] * v2_[x_] * y2_[x_] for x_ in (0, 1))]}
sym_ok4 = all(sp.expand(z_) == 0 for z_ in zero_pairs) and weights_all["all 1: bottom <u1,v1>, left <u1,y1>, top <y1,v1>, inner"] == [1, 1, sp.expand(mu_), 1] \
    and [sp.expand(x_) for x_ in weights_all["all 2"]] == [sp.expand(mu_), 1, 1, 1]
types, imp_ok = {}, True
ROT = [(0, 1, 2), (1, 2, 0), (2, 0, 1)]
for (sv, tv) in ((2, -3), (5, 2)):
    base = {k_: int(val) for k_, val in GL.implication(sv, tv).items()}
    for refl in (False, True):
        for comp in (False, True):
            for rot in ROT:
                w_ = GL.permute(base, (0, 2, 1)) if refl else dict(base)
                w_ = GL.complement(w_) if comp else w_
                w_ = GL.permute(w_, rot)
                W = np.zeros((2, 2, 2), dtype=object)
                for k_ in TU:
                    W[k_] = w_[k_]
                mu = 1 + sv * tv
                levels_ok = True
                for k in range(2, 10):
                    ok, lam = GE.proportional_int(GE.corner_relation_int(2, k, W, primes=GE.PRIMES), W)
                    levels_ok &= ok and lam == mu ** (k - 1)
                key = f"refl={int(refl)} comp={int(comp)} rot={rot}"
                types.setdefault(key, []).append(levels_ok)
                imp_ok &= levels_ok
supps = sorted({tuple(GL.support({k_: int(v_) for k_, v_ in GL.implication(2, -3).items()}))})
report("4 implication laws: closure pairings vanish; all twelve types exact at levels 2 to 9 with factor <v,y>^(k-1)", sym_ok4 and imp_ok and len(types) == 12,
       {"vanishing pairings and the two surviving assignments (symbolic)": sym_ok4, "types checked": len(types),
        "support of e0 v y + Jv Jy e1 (a = 1 implies c = 1)": supps})

# ---------------------------------------------------------------- 5 rank one in a corner
m00, m01, m10, m11, a0, a1 = sp.symbols("m00 m01 m10 m11 a0 a1")
M = sp.Matrix([[m00, m01], [m10, m11]])
wr = GL.slot_rank_one((a0, a1), M.tolist())
r1_ok = True
for k, R in ((2, R2), (3, R3)):
    Mk = M ** k
    rr = {k_: sp.factor(R[k_].subs({GL.G[s]: wr[s] for s in TU})) for k_ in TU}
    ratio = sp.factor(rr[(0, 0, 0)] / (a0 * Mk[0, 0]))
    r1_ok &= all(sp.simplify(rr[k_] - (a0, a1)[k_[0]] * Mk[k_[1], k_[2]] * ratio) == 0 for k_ in TU)
    r1_ok &= sp.fraction(sp.together(ratio))[1].free_symbols == set()
imgs = {}
for name, base in (("u(a)[b = c]", {k_: (1, 2)[k_[0]] * (1 if k_[1] == k_[2] else 0) for k_ in TU}),
                   ("product u(a) x(b) z(c)", {k_: (1, 2)[k_[0]] * (1, -3)[k_[1]] * (2, 1)[k_[2]] for k_ in TU})):
    for rot in ROT:
        w_ = GL.permute(base, rot)
        W = np.zeros((2, 2, 2), dtype=object)
        for k_ in TU:
            W[k_] = w_[k_]
        imgs[f"{name}, rotation {rot}"] = all(GE.proportional_int(GE.corner_relation_int(2, k, W, primes=GE.PRIMES), W)[0] for k in range(2, 9))
report("5 rank one in a corner: R_k = u (x) M^k times a scalar, so M^2 = cM: products and u(a)[b = c]; the rotations are exact at levels 2 to 8",
       r1_ok and all(imgs.values()), {"identity for k = 2, 3": r1_ok, **imgs})

# ---------------------------------------------------------------- 6 knots
nae = {k_: (-1) ** k_[0] * (0, 1, -1)[sum((-1) ** x_ for x_ in k_) % 3] for k_ in TU}
kn = {"implication law (2, -3)": GL.is_knot({k_: int(v_) for k_, v_ in GL.implication(2, -3).items()}),
      "u(a)[b = c]": GL.is_knot({k_: (1, 2)[k_[0]] * (1 if k_[1] == k_[2] else 0) for k_ in TU}),
      "product": GL.is_knot({k_: 1 for k_ in TU})}
kn.update({f"signed not-all-equal, rotation {rot}": GL.is_knot(GL.permute(nae, rot)) for rot in ROT})
report("6 knots: implication and rank-one laws are not knots; the rotations of signed not-all-equal are", kn == {**{k_: False for k_ in list(kn)[:3]},
       **{k_: True for k_ in list(kn)[3:]}}, kn)

# ---------------------------------------------------------------- 7 controls
ctrl = {}
def exact_at(w_, k):
    W = np.zeros((2, 2, 2), dtype=object)
    for k_ in TU:
        W[k_] = w_[k_]
    return GE.proportional_int(GE.corner_relation_int(2, k, W, primes=GE.PRIMES), W)[0]
gen = {k_: int(v_) for k_, v_ in GL.cyclic((1, 2), (1, -1), (1, 3), 1).items()}
ctrl["a cyclic law with no coordinate vector is exact at level 2 but not 3"] = exact_at(gen, 2) and not exact_at(gen, 3)
imp = {k_: int(v_) for k_, v_ in GL.implication(2, -3).items()}
imp2 = dict(imp)
imp2[(0, 0, 0)] += 1
ctrl["an implication law with one weight changed fails level 2 or 3"] = not (exact_at(imp2, 2) and exact_at(imp2, 3))
ctrl["a law with ratio c = 2 on the cyclic branch fails level 2"] = not exact_at({k_: int(v_) for k_, v_ in GL.cyclic((1, 0), (1, 2), (1, -3), 2).items()}, 2)
report("7 controls fire", all(ctrl.values()), ctrl)

out["ok"] = ok_all
out["seconds"] = round(time.time() - T0, 1)
print("ALL OK" if ok_all else "SOME CHECK FAILED", out["seconds"], "s")
if "--write" in sys.argv:
    json.dump({"schema_version": 1, "artifact_id": "WAVE-UNIQUENESS-20261029-001B-P001", "status": "Proved" if ok_all else "Failed",
               "checks": out}, open(os.path.join(HERE, "result.json"), "w"), indent=1, default=str)
sys.exit(0 if ok_all else 1)
