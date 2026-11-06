"""Checks for INTERFERENCE-20261029-001A-P001 (interference across the two/three boundary).

A *gadget* is a sum over hidden bits of a product of functions of at most two variables (visible or hidden).
  0 dependency artifacts bound by the hashes recorded in manifest.json
  1 the 34 three-bit knots (K1-K3 on allowed states) in 16 classes up to coordinate order
  2 Theorem 1 (nonnegative values): on 20,000 random gadgets (3 visible, up to 3 hidden bits, values in {0,1,2}) the support
    equals the existential projection of the factor supports and is majority-closed; none is a knot
  3 Theorem 2 (zero hidden bits): exhaustively over all 16^3 triples of binary supports on the three pairs of a three-bit
    system, the support of the product (signed or not) is never a knot
  4 Theorem 3 (one hidden bit per clause): every clause of width 1..8 with every sign pattern equals
    sum_h u(h) prod_i k_i(h, x_i) with u = (1, -1), k_i(0, .) = 1, k_i(1, x) = [literal i false]; on 300 random 3-CNFs
    (6-8 variables, up to 10 clauses) the gadget with one hidden bit per clause equals the formula on every assignment;
    every relation on three bits (all 256) equals its gadget with one hidden bit per excluded tuple
  5 Theorem 4 (census): for each of the 16 classes, Cayley's hyperdeterminant of the indicator; an exact real rank-2
    decomposition of the indicator, or of the indicator times a pairwise sign when the hyperdeterminant is negative
    (not-all-equal and twisted not-all-equal), verified symbolically, gives an exact gadget with one hidden bit; every
    such decomposition has a negative entry (as Theorem 1 forces)
  6 parity of n bits from one hidden bit and Hadamard edges, n = 1..10: sum_h prod_i (-1)^(h x_i) = 2 [x_1 + ... + x_n even]
  7 controls that must fire: a perturbed decomposition is rejected; the unscaled not-all-equal indicator has complex
    eigenvalues (no real rank-2 decomposition); replacing the census gadgets' factors by their absolute values gives a
    support strictly larger than the knot; a 2-CNF relation is rejected by the knot test
Run: .venv/bin/python -B check.py [--write]   (numpy, sympy)"""
import hashlib, itertools, json, os, random, sys, time
import numpy as np
import sympy as sp

T0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
out, ok_all = {}, True


def report(key, ok, detail):
    global ok_all
    out[key] = {"ok": bool(ok), "detail": detail}
    ok_all &= bool(ok)
    print(("PASS " if ok else "FAIL ") + key + ": " + json.dumps(detail, default=str)[:1500], flush=True)


# ---------------------------------------------------------------- 0 dependencies
man = json.load(open(os.path.join(HERE, "manifest.json")))
mism = {}
for rel, digest in man["parent_bindings"].items():
    got = hashlib.sha256(open(os.path.join(ROOT, rel), "rb").read()).hexdigest()
    if got != digest:
        mism[rel] = got
report("0 dependency artifacts bound by hash", not mism, {"parents": len(man["parent_bindings"]), "mismatched": mism})

# ---------------------------------------------------------------- 1 knots
CUBE3 = list(itertools.product((0, 1), repeat=3))
PERMS = list(itertools.permutations(range(3)))


def is_knot(R, n=3):
    """K1-K3 on allowed states: constrained as a whole, every proper subset of coordinates free, nonempty"""
    R = set(R)
    if not R or len(R) == 2 ** n:
        return False
    for drop in range(n):
        keep = [i for i in range(n) if i != drop]
        if len({tuple(t[i] for i in keep) for t in R}) != 2 ** (n - 1):
            return False
    return True


KNOTS = [frozenset(R) for k in range(1, 8) for R in itertools.combinations(CUBE3, k) if is_knot(R)]


def canon(K):
    return min(tuple(sorted(tuple(t[q[i]] for i in range(3)) for t in K)) for q in PERMS)


CLASSES = sorted({canon(K) for K in KNOTS})


def kind(K):
    E = [s for s in CUBE3 if s not in K]
    if len(E) == 4:
        return "parity"
    if len(E) == 3:
        return "three excluded"
    if len(E) == 2:
        return "two excluded at distance two" if sum(a != b for a, b in zip(*E)) == 2 else "not-all-equal type"
    return "atom"


report("1 the 34 three-bit knots in 16 classes", len(KNOTS) == 34 and len(CLASSES) == 16,
       {"knots": len(KNOTS), "classes": len(CLASSES)})


def majority_closed(R):
    R = set(R)
    for a, b, c in itertools.product(R, repeat=3):
        if tuple(int(x + y + z >= 2) for x, y, z in zip(a, b, c)) not in R:
            return False
    return True


# ---------------------------------------------------------------- 2 Theorem 1: nonnegative gadgets
def random_gadget(rng, hidden, values):
    nv = 3 + hidden
    pairs = [(i, j) for i in range(nv) for j in range(i + 1, nv)]
    chosen = [p for p in pairs if rng.random() < 0.6]
    facs = [(p, {ab: rng.choice(values) for ab in itertools.product((0, 1), repeat=2)}) for p in chosen]
    return nv, facs


def gadget_value(nv, facs, x):
    tot = 0
    for hb in itertools.product((0, 1), repeat=nv - 3):
        z = tuple(x) + hb
        p = 1
        for (i, j), f in facs:
            p *= f[(z[i], z[j])]
            if p == 0:
                break
        tot += p
    return tot


rng = random.Random(20261029)
bad1, knots1, nonmaj = 0, 0, 0
for trial in range(20000):
    hidden = rng.randint(0, 3)
    nv, facs = random_gadget(rng, hidden, (0, 1, 2))
    supp = {x for x in CUBE3 if gadget_value(nv, facs, x) != 0}
    proj = set()
    for z in itertools.product((0, 1), repeat=nv):
        if all(f[(z[i], z[j])] != 0 for (i, j), f in facs):
            proj.add(z[:3])
    bad1 += supp != proj
    knots1 += is_knot(supp)
    nonmaj += not majority_closed(supp)
report("2 Theorem 1: nonnegative gadgets have majority-closed supports, never a knot", bad1 == 0 and knots1 == 0 and nonmaj == 0,
       {"random gadgets": 20000, "support != projection": bad1, "knot supports": knots1, "not majority-closed": nonmaj})

# ---------------------------------------------------------------- 3 Theorem 2: zero hidden bits
BIN = [frozenset(S) for k in range(0, 5) for S in itertools.combinations(list(itertools.product((0, 1), repeat=2)), k)]
knots0 = 0
for s01, s02, s12 in itertools.product(BIN, repeat=3):
    supp = {x for x in CUBE3 if (x[0], x[1]) in s01 and (x[0], x[2]) in s02 and (x[1], x[2]) in s12}
    knots0 += is_knot(supp)
report("3 Theorem 2: a product of binary functions (any signs) never has a knot as support", knots0 == 0,
       {"triples of binary supports": len(BIN) ** 3, "knot supports": knots0})


# ---------------------------------------------------------------- 4 Theorem 3: one hidden bit per clause
def clause_gadget(signs, x):
    """signs[i] = 1 for a positive literal; value sum_h u(h) prod_i k_i(h, x_i)"""
    term0 = 1
    term1 = -1
    for s, xi in zip(signs, x):
        lit_false = (xi == 0) if s == 1 else (xi == 1)
        term1 *= 1 if lit_false else 0
    return term0 + term1


cl_bad = 0
cl_count = 0
for k in range(1, 9):
    for signs in itertools.product((0, 1), repeat=k):
        cl_count += 1
        for x in itertools.product((0, 1), repeat=k):
            truth = int(any((xi == 1) if s == 1 else (xi == 0) for s, xi in zip(signs, x)))
            cl_bad += clause_gadget(signs, x) != truth
cnf_bad = 0
for trial in range(300):
    n = rng.randint(6, 8)
    m = rng.randint(1, 10)
    F = []
    for _ in range(m):
        vs = rng.sample(range(n), 3)
        F.append([(v, rng.randint(0, 1)) for v in vs])
    for x in itertools.product((0, 1), repeat=n):
        truth = int(all(any((x[v] == 1) if s == 1 else (x[v] == 0) for v, s in cl) for cl in F))
        tot = 0
        for hb in itertools.product((0, 1), repeat=m):
            p = 1
            for h, cl in zip(hb, F):
                if h == 1:
                    p *= -1
                    for v, s in cl:
                        lit_false = (x[v] == 0) if s == 1 else (x[v] == 1)
                        if not lit_false:
                            p = 0
                            break
                if p == 0:
                    break
            tot += p
        cnf_bad += tot != truth
rel_bad = 0
for k in range(0, 9):
    for R in itertools.combinations(CUBE3, k):
        R = set(R)
        Z = [b for b in CUBE3 if b not in R]
        for x in CUBE3:
            val = 1
            for b in Z:  # one hidden bit per excluded tuple: 1 - [x = b]
                val *= 1 + (-1) * int(x == b)
            rel_bad += val != int(x in R)
report("4 Theorem 3: one hidden bit per clause (inclusion-exclusion); one per excluded tuple",
       cl_bad == 0 and cnf_bad == 0 and rel_bad == 0,
       {"clauses checked (width 1-8, all signs)": cl_count, "clause mismatches": cl_bad, "random 3-CNFs": 300,
        "CNF mismatches": cnf_bad, "relations on three bits": 256, "relation mismatches": rel_bad})


# ---------------------------------------------------------------- 5 Theorem 4: census, one hidden bit for every class
def hdet(a):
    A = lambda i, j, k: a[i][j][k]
    return (A(0, 0, 0) ** 2 * A(1, 1, 1) ** 2 + A(0, 0, 1) ** 2 * A(1, 1, 0) ** 2 + A(0, 1, 0) ** 2 * A(1, 0, 1) ** 2
            + A(1, 0, 0) ** 2 * A(0, 1, 1) ** 2
            - 2 * (A(0, 0, 0) * A(0, 0, 1) * A(1, 1, 0) * A(1, 1, 1) + A(0, 0, 0) * A(0, 1, 0) * A(1, 0, 1) * A(1, 1, 1)
                   + A(0, 0, 0) * A(1, 0, 0) * A(0, 1, 1) * A(1, 1, 1) + A(0, 0, 1) * A(0, 1, 0) * A(1, 0, 1) * A(1, 1, 0)
                   + A(0, 0, 1) * A(1, 0, 0) * A(0, 1, 1) * A(1, 1, 0) + A(0, 1, 0) * A(1, 0, 0) * A(0, 1, 1) * A(1, 0, 1))
            + 4 * (A(0, 0, 0) * A(0, 1, 1) * A(1, 0, 1) * A(1, 1, 0) + A(0, 0, 1) * A(0, 1, 0) * A(1, 0, 0) * A(1, 1, 1)))


def tensor_of(f):
    return [[[sp.Integer(f((i, j, k))) for k in (0, 1)] for j in (0, 1)] for i in (0, 1)]


def rank2_decomposition(T):
    """exact real decomposition T = sum_{h=0,1} a_h (x) b_h (x) c_h, via the pencil of mode-3 slices; None if no real one"""
    for (x, y) in ((1, 0), (0, 1), (1, 1), (1, -1), (2, 1), (1, 2)):
        S0 = sp.Matrix(2, 2, lambda i, j: x * T[i][j][0] + y * T[i][j][1])
        if S0.det() == 0:
            continue
        # change of basis in mode 3: new slices S0 (combination) and S1 (the other slice)
        if y != 0:
            S1 = sp.Matrix(2, 2, lambda i, j: T[i][j][0])
            C = sp.Matrix([[x, y], [1, 0]])  # new coords (u0, u1) = C (t0, t1)
        else:
            S1 = sp.Matrix(2, 2, lambda i, j: T[i][j][1])
            C = sp.Matrix([[x, 0], [0, 1]])
        Mx = S1 * S0.inv()
        ev = Mx.eigenvects()
        lams = []
        for val, mult, vecs in ev:
            if not val.is_real:
                return None
            lams += [(val, v) for v in vecs]
        if len(lams) != 2:
            continue
        P = sp.Matrix.hstack(lams[0][1], lams[1][1])
        D = sp.diag(lams[0][0], lams[1][0])
        # S1 = P D P^-1 S0 ; write S0 = P Q^T  =>  Q^T = P^-1 S0 ; S1 = P D Q^T
        QT = P.inv() * S0
        # slices in new coordinates: new0 = S0 = P I Q^T, new1 = S1 = P D Q^T ; back to original mode-3 coords
        Cinv = C.inv()
        decomp = []
        for h in range(2):
            a = [sp.nsimplify(P[i, h]) for i in range(2)]
            b = [sp.nsimplify(QT[h, j]) for j in range(2)]
            newc = [sp.Integer(1), D[h, h]]  # coefficients on new0, new1
            c = [sp.simplify(Cinv[0, l] * newc[0] + Cinv[1, l] * newc[1]) for l in range(2)]
            # T(i,j,l) = sum_h a_i b_j * (new-slice coefficient pulled back): verify below
            decomp.append((a, b, c))
        # verify (the pulled-back coefficients may need the transpose of Cinv; try both)
        for trans in (False, True):
            dec2 = []
            for h, (a, b, _) in enumerate(decomp):
                newc = [sp.Integer(1), D[h, h]]
                M = Cinv.T if trans else Cinv
                c = [sp.simplify(sum(newc[r] * M[r, l] for r in range(2))) for l in range(2)]
                dec2.append((a, b, c))
            if all(sp.simplify(sum(a[i] * b[j] * c[l] for a, b, c in dec2) - T[i][j][l]) == 0
                   for i in range(2) for j in range(2) for l in range(2)):
                return dec2
    return None


PAIRS = [(0, 1), (0, 2), (1, 2)]
census = []
neg_entry_ok = True
gadgets = {}
for key in CLASSES:
    K = frozenset(key)
    ind = tensor_of(lambda t: int(t in K))
    d0 = hdet(ind)
    V = None
    if d0 > 0:
        G = ind
        Vfun = lambda t: 1
    else:
        # search a pairwise sign with positive hyperdeterminant
        for signs in itertools.product((1, -1), repeat=12):
            vv = {}
            it = iter(signs)
            for p in PAIRS:
                vv[p] = {ab: next(it) for ab in itertools.product((0, 1), repeat=2)}
            Vfun = lambda t, vv=vv: vv[(0, 1)][(t[0], t[1])] * vv[(0, 2)][(t[0], t[2])] * vv[(1, 2)][(t[1], t[2])]
            G = tensor_of(lambda t, Vfun=Vfun: int(t in K) * Vfun(t))
            if hdet(G) > 0:
                V = vv
                break
    dec = rank2_decomposition(G)
    exact = False
    if dec is not None:
        # the one-hidden-bit gadget: sum_h k1(h,x1) k2(h,x2) k3(h,x3) * W(x), W = 1/V = V (signs)
        exact = all(sp.simplify(sum(a[x[0]] * b[x[1]] * c[x[2]] for a, b, c in dec) * Vfun(x) - int(x in K)) == 0
                    for x in CUBE3)
        entries = [e for a, b, c in dec for e in a + b + c]
        has_neg = any(sp.N(e) < 0 for e in entries)
        neg_entry_ok &= has_neg
        gadgets[key] = (dec, Vfun)
    census.append({"class": kind(K), "excluded": sorted(set(CUBE3) - K), "hyperdeterminant of indicator": int(d0),
                   "pairwise sign needed": V is not None,
                   "hyperdeterminant used": int(hdet(G)), "exact one-hidden-bit gadget": exact,
                   "decomposition": [[[str(e) for e in a], [str(e) for e in b], [str(e) for e in c]] for a, b, c in dec] if dec else None})
all_one = all(r["exact one-hidden-bit gadget"] for r in census)
report("5 Theorem 4: every three-bit knot class has an exact signed gadget with one hidden bit", all_one and neg_entry_ok,
       {"classes": len(census), "exact": sum(r["exact one-hidden-bit gadget"] for r in census),
        "indicator of real rank 2 (hyperdeterminant > 0)": sum(r["hyperdeterminant of indicator"] > 0 for r in census),
        "need a pairwise sign": [r["excluded"] for r in census if r["pairwise sign needed"]],
        "every decomposition has a negative entry": neg_entry_ok})

# ---------------------------------------------------------------- 6 parity of n bits from one hidden bit
par_bad = 0
for n in range(1, 11):
    for x in itertools.product((0, 1), repeat=n):
        val = sum(np.prod([(-1) ** (h * xi) for xi in x]) for h in (0, 1))
        par_bad += val != 2 * int(sum(x) % 2 == 0)
report("6 parity of n bits from one hidden bit and Hadamard edges (n = 1..10)", par_bad == 0, {"mismatches": par_bad})

# ---------------------------------------------------------------- 7 controls
ctrl = {}
key0 = CLASSES[0]
dec0, V0 = gadgets[key0]
a, b, c = dec0[0]
pert = [([a[0] + 1, a[1]], b, c)] + dec0[1:]
ctrl["perturbed decomposition rejected"] = not all(
    sp.simplify(sum(a_[x[0]] * b_[x[1]] * c_[x[2]] for a_, b_, c_ in pert) * V0(x) - int(x in frozenset(key0))) == 0 for x in CUBE3)
nae = frozenset(t for t in CUBE3 if t not in ((0, 0, 0), (1, 1, 1)))
ctrl["unscaled not-all-equal has no real rank-2 decomposition"] = rank2_decomposition(tensor_of(lambda t: int(t in nae))) is None
absbig = []
for key, (dec, Vf) in gadgets.items():
    K = frozenset(key)
    supp = {x for x in CUBE3 if sum(abs(sp.N(a[x[0]])) * abs(sp.N(b[x[1]])) * abs(sp.N(c[x[2]])) for a, b, c in dec) > 1e-12}
    absbig.append(supp > set(K))
ctrl["absolute values give a support strictly larger than the knot (all 16)"] = all(absbig)
ctrl["a 2-CNF relation is rejected by the knot test"] = not is_knot({t for t in CUBE3 if (not t[0]) or t[1]})
report("7 controls fire", all(ctrl.values()), ctrl)

out["census"] = census
out["ok"] = ok_all
out["seconds"] = round(time.time() - T0, 1)
print("ALL OK" if ok_all else "SOME CHECK FAILED", out["seconds"], "s")
if "--write" in sys.argv:
    res = {"schema_version": 1, "artifact_id": "INTERFERENCE-20261029-001A-P001", "status": "Proved" if ok_all else "Failed",
           "checks": out}
    json.dump(res, open(os.path.join(HERE, "result.json"), "w"), indent=1, default=str)
sys.exit(0 if ok_all else 1)
