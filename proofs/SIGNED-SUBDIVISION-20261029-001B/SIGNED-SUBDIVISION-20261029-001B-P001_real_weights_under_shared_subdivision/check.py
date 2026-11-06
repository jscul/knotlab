"""Checks for SIGNED-SUBDIVISION-20261029-001B-P001 (real weights under shared subdivision).

Weighted rules: arbitrary nonzero real weights on a knot's tuples, on every up triangle (S2) or on every triangle with one placement
for up and one for down triangles (S1).  F(x) is the fine sum over fine assignments restricting to the coarse assignment x, W(x) the
coarse weight; exact: F = c W with c != 0; support-exact: same support (ss_lib.py, rw_lib.py).
  0 dependency artifacts bound by the hashes recorded in manifest.json
  1 122 shapes; sign classes (sign patterns modulo the sign gauge) number 944, the gauge orbits of SIGNED-SUBDIVISION-20261029-001A;
    real gauge ranks and the number of free magnitudes in the gauge slice
  2 positivity: the counted rules that are support-exact at scale 2 (coarse sides 2, 3, 4) and scale 3 (sides 2, 3) are exactly the
    22 and 6 counted-exact shapes; control: random positive real weights give the counted supports
  3 sign-parity obstruction: a coarse-forbidden x whose fine extensions all use each tuple equally often mod 2 (tested by flipping the
    sign of one tuple at a time: |F| must stay equal to the count), or a coarse-allowed x with no extension; witnesses at scale 2
    (coarse sides 2, 3) and scale 3 (side 2); the refinement per sign class (one sign-coherent forbidden x in every class) excludes no
    further shape at these sizes; the open shapes are listed
  4 affine shapes: the explicit solution families are complete on every torus used (exact counts); in the gauge slice, over every sign
    class, the real exact weightings are the classes of plus-minus-one weights, at scale 2 on coarse sides 2 to 6 and at scale 3 on
    sides 2 to 4; sides 2 to 4 alone admit one more class for each parity law on up triangles, which side 6 removes
  5 symmetric slices: the atoms excluding 000 or 111 (S2, S1) with weights constant on Hamming classes have no exact weighting on the
    coarse 2-torus at scale 2 (gcd of the equations and gcd of resultants)
  6 controls that must fire: a magnitude 1.01 breaks an exact weighting; the explicit families are incomplete for not-all-equal on
    all triangles; the obstruction finds no witness on an exact shape
Run: .venv/bin/python -B check.py [--write]   (numpy, sympy)"""
import hashlib, itertools, json, os, random, sys, time
from collections import Counter
import numpy as np
import sympy as sp

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
import ss_lib as S  # noqa: E402
import rw_lib as R  # noqa: E402

T0 = time.time()
out, ok_all = {}, True


def report(key, ok, detail):
    global ok_all
    out[key] = {"ok": bool(ok), "detail": detail}
    ok_all &= bool(ok)
    print(("PASS " if ok else "FAIL ") + key + ": " + json.dumps(detail, default=str)[:2500], flush=True)


def name(s, P1, P2):
    ex = lambda P: " ".join("".join(map(str, t)) for t in sorted(set(S.cube) - P))
    return f"{s} {S.kind(P1)} excl {ex(P1)}" + (f" / {ex(P2)}" if P2 is not None else "")


def ones(P1, P2):
    return S.wvec(P1, [1] * len(P1)), (S.wvec(P2, [1] * len(P2)) if P2 is not None else None)


# ---------------------------------------------------------------- 0
man = json.load(open(os.path.join(HERE, "manifest.json")))
mism = {r: d for r, d in man["parent_bindings"].items()
        if hashlib.sha256(open(os.path.join(ROOT, r), "rb").read()).hexdigest() != d}
report("0 dependency artifacts bound by hash", not mism, {"parents": len(man["parent_bindings"]), "mismatched": mism})

# ---------------------------------------------------------------- 1
SHAPES = S.rule_shapes()
NAMES = [name(*x) for x in SHAPES]
CLASSES, FREE = {}, {}
for nm, (s, P1, P2) in zip(NAMES, SHAPES):
    CLASSES[nm] = R.sign_classes(P1, P2)
    FREE[nm] = R.slice_free(P1, P2)
n_classes = sum(len(c[0]) for c in CLASSES.values())
sizes_ok = all(sum(c[1]) == 2 ** (len(P1) + (len(P2) if P2 is not None else 0))
               for (s, P1, P2), c in zip(SHAPES, CLASSES.values()))
slice_dims = Counter((f"{s} {S.kind(P1)}", len(FREE[nm][0])) for nm, (s, P1, P2) in zip(NAMES, SHAPES))
report("1 shapes, sign classes and gauge slices", len(SHAPES) == 122 and n_classes == 944 and sizes_ok,
       {"shapes": len(SHAPES), "sign classes": n_classes, "class sizes partition the sign patterns": sizes_ok,
        "free magnitudes per kind": {f"{k} ({d} free)": v for (k, d), v in sorted(slice_dims.items())}})

# ---------------------------------------------------------------- 2 positivity
def counted_support_exact(P1, P2, sizes):
    for m, k in sizes:
        r = S.decide(m, k, *ones(P1, P2), primes=S.PRIMES[:3])
        if r["vacuous"] or not r["support_exact"]:
            return False
    return True


SUP2 = {nm for nm, (s, P1, P2) in zip(NAMES, SHAPES) if counted_support_exact(P1, P2, ((2, 2), (3, 2), (4, 2)))}
SUP3 = {nm for nm, (s, P1, P2) in zip(NAMES, SHAPES) if counted_support_exact(P1, P2, ((2, 3), (3, 3)))}
EXACT2 = {nm for nm, (s, P1, P2) in zip(NAMES, SHAPES) if all(S.decide(m, 2, *ones(P1, P2), primes=S.PRIMES[:3])["exact"] for m in (2, 3))}
EXACT3 = {nm for nm, (s, P1, P2) in zip(NAMES, SHAPES) if S.decide(2, 3, *ones(P1, P2), primes=S.PRIMES[:3])["exact"]}
rng = np.random.default_rng(29)
pos_bad = 0
for idx in rng.choice(len(SHAPES), 12, replace=False):
    s, P1, P2 = SHAPES[idx]
    w1 = S.wvec(P1, [1] * len(P1)).astype(float) * rng.uniform(0.5, 2.0, 8)
    w2 = None if P2 is None else S.wvec(P2, [1] * len(P2)).astype(float) * rng.uniform(0.5, 2.0, 8)
    Ff = R.fine_float(2, 2, w1, w2)
    Fc = S.fine_sums(2, 2, *ones(P1, P2), S.PRIMES[0])
    pos_bad += sum((Ff[x] > 1e-300) != (Fc[x] != 0) for x in Fc)
report("2 positivity: counted support-exact shapes are the counted-exact ones (22 at scale 2, 6 at scale 3)",
       SUP2 == EXACT2 and len(SUP2) == 22 and SUP3 == EXACT3 and len(SUP3) == 6 and pos_bad == 0,
       {"support-exact with counts, scale 2 (sides 2-4)": len(SUP2), "equal to the counted-exact shapes": SUP2 == EXACT2,
        "support-exact with counts, scale 3 (sides 2-3)": len(SUP3), "equal at scale 3": SUP3 == EXACT3,
        "random positive weights: support mismatches with the counts (12 shapes, coarse 2-torus)": pos_bad})

# ---------------------------------------------------------------- 3 sign-parity obstruction
def witness(P1, P2, m, k):
    """('O1', x) | ('O2', x) | None, and the per-sign-class coherent forbidden states"""
    Fc = R.fine_exact(m, k, *ones(P1, P2))
    W = S.coarse_weights(m, *ones(P1, P2), S.PRIMES[0])
    allowed = {x for x in W if W[x]}
    o1 = sorted(x for x in allowed if Fc[x] == 0)
    if o1:
        return ("O1", o1[0]), None
    forb = sorted(x for x in Fc if x not in allowed and Fc[x] > 0)
    same = {x: True for x in forb}
    n1 = len(P1)
    n = n1 + (len(P2) if P2 is not None else 0)
    for t in range(n):
        e = [1] * n
        e[t] = -1
        w1 = S.wvec(P1, e[:n1])
        w2 = None if P2 is None else S.wvec(P2, e[n1:])
        Fs = R.fine_exact(m, k, w1, w2)
        for x in forb:
            if same[x] and abs(Fs[x]) != Fc[x]:
                same[x] = False
    o2 = [x for x in forb if same[x]]
    return (("O2", o2[0]) if o2 else None), (Fc, forb)


def coherent_classes(P1, P2, m, k, Fc, forb, reps):
    n1 = len(P1)
    bad = []
    for sg in reps:
        Fs = R.fine_exact(m, k, S.wvec(P1, sg[:n1]), None if P2 is None else S.wvec(P2, sg[n1:]))
        if not any(abs(Fs[x]) == Fc[x] for x in forb):
            bad.append(sg)
    return bad


EXCL2, EXCL3, OPEN2, OPEN3, refine_gain = {}, {}, [], [], []
for nm, (s, P1, P2) in zip(NAMES, SHAPES):
    reps = CLASSES[nm][0]
    if nm not in SUP2:
        for m in (2, 3):
            wit, data = witness(P1, P2, m, 2)
            if wit:
                EXCL2[nm] = (m, wit[0], wit[1])
                break
            if not coherent_classes(P1, P2, m, 2, data[0], data[1], reps):
                refine_gain.append((nm, "scale 2", m))
        if nm not in EXCL2:
            OPEN2.append(nm)
    if nm not in SUP3:
        wit, data = witness(P1, P2, 2, 3)
        if wit:
            EXCL3[nm] = (2, wit[0], wit[1])
        else:
            if not coherent_classes(P1, P2, 2, 3, data[0], data[1], reps):
                refine_gain.append((nm, "scale 3", 2))
            OPEN3.append(nm)
KIND = {nm: f"{s} {S.kind(P1)}" for nm, (s, P1, P2) in zip(NAMES, SHAPES)}
open2_kinds = Counter(KIND[nm] for nm in OPEN2)
open3_kinds = Counter(KIND[nm] for nm in OPEN3)
report("3 sign-parity obstruction: 54 shapes excluded at scale 2, 34 at scale 3, for every real weighting",
       len(EXCL2) == 54 and len(EXCL3) == 34 and not refine_gain and len(OPEN2) == 46,
       {"excluded at scale 2": len(EXCL2), "of which on the coarse 2-torus": sum(1 for v in EXCL2.values() if v[0] == 2),
        "kinds of witness at scale 2": Counter(v[1] for v in EXCL2.values()),
        "excluded at scale 3 (coarse 2-torus)": len(EXCL3), "kinds of witness at scale 3": Counter(v[1] for v in EXCL3.values()),
        "shapes the per-class refinement would add": refine_gain,
        "open at scale 2": len(OPEN2), "open at scale 2 by kind": open2_kinds,
        "open at scale 3": len(OPEN3), "open at scale 3 by kind": open3_kinds})
out["excluded"] = {"scale 2": {k: [v[0], v[1], v[2]] for k, v in EXCL2.items()},
                   "scale 3": {k: [v[0], v[1], v[2]] for k, v in EXCL3.items()}}
out["open"] = {"scale 2": OPEN2, "scale 3": OPEN3}

# ---------------------------------------------------------------- 4 affine shapes: real exact weightings
AFFINE = [(nm, x) for nm, x in zip(NAMES, SHAPES) if nm in SUP2]
tabs_cache = {}


def tabs(nm, P1, P2, sizes):
    res = []
    for m, k in sizes:
        if (nm, m, k) not in tabs_cache:
            tabs_cache[(nm, m, k)] = R.tables(m, k, P1, P2)
        res.append(tabs_cache[(nm, m, k)])
    return res


def exact_points(nm, P1, P2, sides):
    """per sign class: solve exactly on the smallest prefix of the sides whose system is zero-dimensional (gcd and real roots for
    one magnitude, a lexicographic Groebner basis for two), then keep a point only if the equations of the remaining sides vanish
    there (exact substitution, or reduction modulo the minimal polynomial) and every F(x0) stays nonzero"""
    free, _ = FREE[nm]
    syms = sp.symbols(f"m0:{len(free)}", positive=True)
    pts, used, dropped = [], [], []
    for sg in CLASSES[nm][0]:
        for nb in range(1, len(sides) + 1):
            eqs, Fx0s = R.system(tabs(nm, P1, P2, sides[:nb]), sg, free, syms)
            try:
                kind, sol = R.positive_solutions(eqs, Fx0s, syms)
            except ValueError:
                continue  # positive-dimensional on this prefix: add a side
            if kind == "points":
                break
        else:
            raise ValueError(f"{nm}: no zero-dimensional prefix of {sides}")
        used.append(nb)
        extra = sides[nb:]
        if extra and sol:
            eqs2, F2 = R.system(tabs(nm, P1, P2, extra), sg, free, syms)
            keep = [q for q in sol if all(R.vanishes_at(e, syms, q) for e in eqs2) and not any(R.vanishes_at(f, syms, q) for f in F2)]
            dropped += [(sg, [str(v) for v in q], [m for m, k in sides[:nb]]) for q in sol if q not in keep]
            sol = keep
        pts += [(sg, q) for q in sol]
    return pts, max(used), dropped


aff = {}
for nm, (s, P1, P2) in AFFINE:
    t = time.time()
    p24, u24, d24 = exact_points(nm, P1, P2, [(m, 2) for m in (2, 3, 4)])
    p26, u26, d26 = exact_points(nm, P1, P2, [(m, 2) for m in (2, 3, 4, 5, 6)])
    p3, u3, d3 = exact_points(nm, P1, P2, [(m, 3) for m in (2, 3, 4)])
    fmt = lambda pts: [(sg, [str(v) for v in q]) for sg, q in pts]
    aff[nm] = {"scale 2, sides 2-4": fmt(p24), "scale 2, sides 2-6": fmt(p26), "scale 3, sides 2-4": fmt(p3),
               "sides solved before substitution (scale 2, scale 3)": [u26, u3],
               "points exact on the solved sides that fail later (sign class, magnitudes, solved sides)":
                   {"scale 2": d26, "scale 3": d3}}
    print(f"   {nm}: {len(p24)} / {len(p26)} / {len(p3)} exact points ({time.time() - t:.1f} s)", flush=True)
c_unit = all(all(q == ["1"] * len(q) for sg, q in aff[nm][key]) for nm in aff for key in ("scale 2, sides 2-6", "scale 3, sides 2-4"))
twisted = {nm for nm in aff if "not-all-equal" in nm}
c_count2 = all(len(aff[nm]["scale 2, sides 2-6"]) == (2 if nm in twisted else 1) for nm in aff)
c_count3 = all(len(aff[nm]["scale 3, sides 2-4"]) == (6 if nm in twisted else 0) for nm in aff)
extra = {nm: [(sg, p) for sg, p in aff[nm]["scale 2, sides 2-4"] if (sg, p) not in aff[nm]["scale 2, sides 2-6"]] for nm in aff}
extra = {nm: v for nm, v in extra.items() if v}
c_extra = set(extra) == {nm for nm in aff if nm.startswith("S2 parity")} and all(len(v) == 1 for v in extra.values())
report("4 affine shapes: real exact weightings are the plus-minus-one exact classes (scale 2 sides 2-6, scale 3 sides 2-4)",
       c_unit and c_count2 and c_count3 and c_extra,
       {"every exact point has all free magnitudes 1": c_unit,
        "exact classes per shape at scale 2: 1 (parity, three-excluded), 2 (twisted)": c_count2,
        "exact classes per shape at scale 3: 6 (twisted), 0 (others)": c_count3,
        "extra exact points on sides 2-4 only (scale 2)": extra, "they occur exactly for the two parity laws on up triangles": c_extra,
        "distinct irrational magnitudes exact on a smaller torus only": sorted({v for nm in aff for key in ("scale 2", "scale 3")
            for sg, q, sd in aff[nm]["points exact on the solved sides that fail later (sign class, magnitudes, solved sides)"][key]
            for v in q if v != "1"})})
out["affine"] = aff

# ---------------------------------------------------------------- 5 symmetric slices of the open symmetric atoms
a, b = sp.symbols("a b")


def sym_system(P1, both):
    classes = sorted({sum(t) for t in P1})
    val = {classes[0]: sp.Integer(1), classes[1]: a, classes[2]: b}
    w = {t: val[sum(t)] for t in P1}
    X = R.candidates_all(4)
    keep = R.allowed(X, P1, P1 if both else None)
    X = X[keep]
    U = R.usage(X, P1, P1 if both else None)
    K = sorted(P1) + (sorted(P1) if both else [])
    F = {}
    for x, u in zip(map(tuple, X[:, ::2, ::2].reshape(len(X), -1).tolist()), U.tolist()):
        F[x] = F.get(x, 0) + sp.Mul(*[w[t] ** e for t, e in zip(K, u)])
    Xc = R.candidates_all(2)
    Xc = Xc[R.allowed(Xc, P1, P1 if both else None)]
    Uc = R.usage(Xc, P1, P1 if both else None)
    W = {tuple(x.reshape(-1).tolist()): sp.Mul(*[w[t] ** e for t, e in zip(K, u)]) for x, u in zip(Xc, Uc.tolist())}
    x0 = sorted(W)[0]
    eqs = [sp.expand(F.get(x0, 0) * W[y] - F.get(y, 0) * W[x0]) for y in W]
    eqs += [sp.expand(f) for y, f in F.items() if y not in W]
    return [e for e in eqs if e != 0], sp.expand(F.get(x0, 0))


def sym_decide(eqs):
    G = sp.Integer(0)
    for e in eqs:
        G = sp.gcd(G, e)
    G = sp.factor(G)
    cof = sorted({sp.expand(sp.cancel(e / G)) for e in eqs}, key=lambda c: (sp.Poly(c, a, b).total_degree(), len(str(c))))
    res = []
    for c in cof[1:]:
        r = sp.resultant(cof[0], c, b)
        if r != 0:
            res.append(sp.Poly(r, a))
        if len(res) >= 4:
            break
    H = res[0]
    for r in res[1:]:
        H = sp.gcd(H, r)
    roots = [r for r in sp.Poly(H.as_expr(), a).real_roots() if r != 0] if H.degree() > 0 else []
    curve_nonzero = [f for f, _ in sp.factor_list(G)[1] if f.free_symbols and f not in (a, b)]
    return str(G), str(sp.factor(H.as_expr())), roots, curve_nonzero


sym = {}
for nm, (s, P1, P2) in zip(NAMES, SHAPES):
    if S.kind(P1) != "atom" or set(S.cube) - P1 not in ({(0, 0, 0)}, {(1, 1, 1)}) or (P2 is not None and P2 != P1):
        continue
    eqs, Fx0 = sym_system(P1, P2 is not None)
    G, H, roots, curve = sym_decide(eqs)
    sym[nm] = {"gcd of the equations": G, "gcd of resultants (in a)": H, "nonzero real roots": [str(r) for r in roots],
               "gcd factors other than a, b": [str(c) for c in curve]}
report("5 symmetric slices: no exact weighting of the open symmetric atoms on the coarse 2-torus",
       len(sym) == 4 and all(not v["nonzero real roots"] and not v["gcd factors other than a, b"] for v in sym.values()), sym)

# ---------------------------------------------------------------- 6 controls
ctrl = {}
nm, (s, P1, P2) = next((nm, x) for nm, x in AFFINE if nm in twisted)
sg = next(sg for sg, p in aff[nm]["scale 2, sides 2-6"])
w1 = np.array(S.wvec(P1, sg[:len(P1)]), dtype=float)
w2 = np.array(S.wvec(P2, sg[len(P1):]), dtype=float)
w1[[t[0] * 4 + t[1] * 2 + t[2] for t in sorted(P1)][0]] *= 1.01
ctrl["magnitude 1.01 breaks an exact weighting (twisted, coarse 3-torus)"] = R.float_residual(3, 2, w1, w2) > 1e-6
try:
    nae = next(x for x in SHAPES if x[0] == "S1" and set(S.cube) - x[1] == {(0, 0, 0), (1, 1, 1)} and x[2] == x[1])
    R.solutions(6, nae[1], nae[2])
    ctrl["explicit families incomplete for not-all-equal on all triangles (6-torus)"] = False
except ValueError:
    ctrl["explicit families incomplete for not-all-equal on all triangles (6-torus)"] = True
ctrl["no obstruction witness on an exact shape"] = witness(P1, P2, 2, 2)[0] is None
report("6 controls fire", all(ctrl.values()), ctrl)

out["ok"] = ok_all
out["seconds"] = round(time.time() - T0, 1)
print("ALL OK" if ok_all else "SOME CHECK FAILED", out["seconds"], "s")
if "--write" in sys.argv:
    json.dump({"schema_version": 1, "artifact_id": "SIGNED-SUBDIVISION-20261029-001B-P001",
               "status": "Proved" if ok_all else "Failed", "checks": out},
              open(os.path.join(HERE, "result.json"), "w"), indent=1, default=str)
sys.exit(0 if ok_all else 1)
