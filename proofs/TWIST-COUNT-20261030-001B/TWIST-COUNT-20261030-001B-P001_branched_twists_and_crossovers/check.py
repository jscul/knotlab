"""Checks for TWIST-COUNT-20261030-001B-P001 (branched twists: a junction cannot cross wires).

  0 dependency artifacts bound by the hashes recorded in manifest.json
  1 the junction formula per slice, W = |Q||R| - Q_row R_row - Q_col R_col + Q R (pointwise), with incidence signs as leg flips
  2 no line wire: random nonnegative tensors (whenever a slice of the junction is confined to one host parity class, at most one value of
    z1 survives); no junction of realizable pages is proportional to a crossover, over all sign classes and incidence signs
  3 soft crossings: over all pairs of sign classes of five realizable pages and all incidence signs, the crossover-type junctions (zero
    turning entries); twisted truncated-octahedron pages give some off the matchgate class with all four straight entries nonzero, never
    an exact crossover
  4 controls: a junction with a signed branch is an exact crossover; the square's points can carry a wire
Run: .venv/bin/python -B check.py [--write]   (numpy, networkx, python-sat; about a minute)"""
import collections, hashlib, itertools, json, os, random, sys, time
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
P = lambda r: os.path.join(ROOT, "proofs", r)  # noqa: E731
for p in (P("THREEFOLD-SPACES-20261030-001A/THREEFOLD-SPACES-20261030-001A-P001_three_fold_spaces_are_built_from_the_fano_plane"),
          P("THREEFOLD-SURFACES-20261030-001A/THREEFOLD-SURFACES-20261030-001A-P001_fano_atoms_are_handles"),
          P("THREEFOLD-GRAMMAR-20261030-001A/THREEFOLD-GRAMMAR-20261030-001A-P001_fano_leaves_and_planar_glue"),
          P("THREEFOLD-AMPLITUDE-20261030-001A/THREEFOLD-AMPLITUDE-20261030-001A-P001_five_per_handle_tuttes_number_per_planar_piece"),
          P("THREEFOLD-AMPLITUDE-20261030-001B/THREEFOLD-AMPLITUDE-20261030-001B-P001_the_amplitude_by_computation"),
          P("THREEFOLD-SPIN-20261030-001A/THREEFOLD-SPIN-20261030-001A-P001_kasteleyn_faces_and_even_spin_structures"),
          P("SEYMOUR-COUNT-20261030-001A/SEYMOUR-COUNT-20261030-001A-P001_the_trisum_law"),
          P("SEYMOUR-COUNT-20261030-001B/SEYMOUR-COUNT-20261030-001B-P001_polynomial_counting_on_seymours_cubic_bound"),
          P("TWIST-COUNT-20261030-001A/TWIST-COUNT-20261030-001A-P001_the_knots_junction_is_a_similitude"), HERE):
    sys.path.insert(0, p)
import networkx as nx  # noqa: E402
import numpy as np  # noqa: E402
import computation_lib as CL  # noqa: E402
import trisum_lib as TL  # noqa: E402
import twist_lib as TW  # noqa: E402

T0 = time.time()
out, ok_all = {}, True
rng = random.Random(20261030)
ALL4 = list(itertools.product((0, 1), repeat=4))
TURN = [(1, 1, 0, 0), (0, 1, 1, 0), (0, 0, 1, 1), (1, 0, 0, 1)]


def report(key, ok, detail):
    global ok_all
    out[key] = {"ok": bool(ok), "detail": detail}
    ok_all &= bool(ok)
    print(("PASS " if ok else "FAIL ") + key + ": " + json.dumps(detail, default=str)[:3000], flush=True)


def flip(F, legs):
    """X on the given legs (complementing those arguments)"""
    G = np.zeros((2, 2, 2, 2), dtype=object)
    for z in ALL4:
        G[tuple(z[k] ^ (1 if k in legs else 0) for k in range(4))] = F[z]
    return G


def formula(FQ, FR, s1, s3):
    """the junction by the slice formula, signs as leg flips"""
    Q = flip(FQ, {k for k, s in ((1, s1[1]), (3, s3[1])) if s})
    R = flip(FR, {k for k, s in ((1, s1[2]), (3, s3[2])) if s})
    W = np.zeros((2, 2, 2, 2), dtype=object)
    for x0, x2 in itertools.product((0, 1), repeat=2):
        q = {(a, b): Q[x0, a, x2, b] for a in (0, 1) for b in (0, 1)}
        r = {(a, b): R[x0, a, x2, b] for a in (0, 1) for b in (0, 1)}
        tot = sum(q.values()) * sum(r.values())
        for z1, z3 in itertools.product((0, 1), repeat=2):
            row = sum(q[(z1, b)] for b in (0, 1)) * sum(r[(z1, b)] for b in (0, 1))
            col = sum(q[(a, z3)] for a in (0, 1)) * sum(r[(a, z3)] for a in (0, 1))
            W[x0, z1 ^ s1[0], x2, z3 ^ s3[0]] = tot - row - col + q[(z1, z3)] * r[(z1, z3)]
    return W


def rand_tensor(p_zero, top=3, symmetric=True):
    F = np.zeros((2, 2, 2, 2), dtype=object)
    for z in ALL4:
        if z[0] == 0 or not symmetric:
            v = 0 if rng.random() < p_zero else rng.randint(1, top)
            F[z] = v
            if symmetric:
                F[tuple(1 - t for t in z)] = v
    return F


CROSS = []
for a, b in itertools.product((0, 1), repeat=2):
    X = np.zeros((2, 2, 2, 2), dtype=object)
    for z in ALL4:
        X[z] = 1 if (z[0] == z[2] ^ a and z[1] == z[3] ^ b) else 0
    CROSS.append(X)


def is_crossover(W):
    for X in CROSS:
        nz = [W[z] for z in ALL4 if X[z]]
        if all(W[z] == 0 for z in ALL4 if not X[z]) and nz[0] != 0 and len(set(nz)) == 1:
            return True
    return False


# ---------------------------------------------------------------- 0
man = json.load(open(os.path.join(HERE, "manifest.json")))
mism = {r: dg for r, dg in man["parent_bindings"].items()
        if hashlib.sha256(open(os.path.join(ROOT, r), "rb").read()).hexdigest() != dg}
report("0 dependency artifacts bound by hash", not mism, {"parents": len(man["parent_bindings"]), "mismatched": mism})

# ---------------------------------------------------------------- 1 the junction formula
agree = 0
for trial in range(300):
    FQ, FR = rand_tensor(0.3, 5, symmetric=False), rand_tensor(0.3, 5, symmetric=False)
    s1, s3 = tuple(rng.randint(0, 1) for _ in range(3)), tuple(rng.randint(0, 1) for _ in range(3))
    agree += (TW.junction(FQ, FR, s1, s3) == formula(FQ, FR, s1, s3)).all()
report("1 the junction formula per slice, with incidence signs as leg flips", agree == 300, {"random tensors and signs agreeing": f"{agree}/300"})

# ---------------------------------------------------------------- 2 no line wire
hits = viol = 0
for trial in range(20000):
    FQ, FR = rand_tensor(0.6, 2), rand_tensor(0.6, 2)
    s1, s3 = tuple(rng.randint(0, 1) for _ in range(3)), tuple(rng.randint(0, 1) for _ in range(3))
    W = TW.junction(FQ, FR, s1, s3)
    for x0, x2 in itertools.product((0, 1), repeat=2):
        sl = {(z1, z3): W[x0, z1, x2, z3] for z1 in (0, 1) for z3 in (0, 1)}
        for c in (0, 1):
            if any(sl.values()) and all(v == 0 for (z1, z3), v in sl.items() if z1 ^ z3 != c):
                hits += 1
                viol += len({z1 for (z1, z3), v in sl.items() if v != 0}) > 1
d2 = {"random nonnegative junctions": {"slices confined to one host parity class": hits, "with two values of z1": viol}}
pages = {}
for name, g, face in (("cube", TL.prism_piece(2), list(TL.C4)), ("6-prism", TL.prism_piece(3), list(TL.C4)),
                      ("8-prism", TL.prism_piece(4), list(TL.C4)), ("truncated octahedron", CL.omnitruncation(nx.complete_graph(4)), None),
                      ("Omni(K2,3)", CL.omnitruncation(nx.complete_bipartite_graph(2, 3)), None)):
    inc, pts, att, sq = TW.page(g, face)
    seen = {}
    for sign in TW.page_sign_classes(inc):
        F = TW.page_tensor(inc, pts, att, sign)
        seen.setdefault(tuple(F.flatten()), F)
    pages[name] = list(seen.values())
SIGNS = [((0, a, b), (0, c, d)) for a, b, c, d in itertools.product((0, 1), repeat=4)]
crossovers, tested = 0, 0
small = pages["cube"] + pages["6-prism"]
for FQ, FR in itertools.combinations_with_replacement(small, 2):
    for s1, s3 in SIGNS:
        tested += 1
        crossovers += is_crossover(TW.junction(FQ, FR, s1, s3))
d2["cube and 6-prism pages, all pairs and signs"] = {"junctions": tested, "crossovers": crossovers}
ok2 = hits > 0 and viol == 0 and crossovers == 0
report("2 no line wire: a junction confined to one host parity class pins z1; no junction of pages is a crossover", ok2, d2)

# ---------------------------------------------------------------- 3 soft crossings
EV = TW.EVEN
ti = [EV.index(t) for t in TURN]
di, i0, i5, i10 = EV.index((1, 1, 1, 1)), EV.index((0, 0, 0, 0)), EV.index((0, 1, 0, 1)), EV.index((1, 0, 1, 0))


def coeff(s1, s3):
    """the bilinear junction in the Hadamard basis, as a tensor C[yh, yq, yr] on even indices"""
    C = np.zeros((8, 8, 8), dtype=np.float64)
    for a, yq in enumerate(EV):
        Q = np.zeros((2, 2, 2, 2), dtype=object)
        Q[yq] = 1
        FQ = TW.hada(Q) / 16
        for b, yr in enumerate(EV):
            R = np.zeros((2, 2, 2, 2), dtype=object)
            R[yr] = 1
            W = TW.hada(TW.junction(FQ, TW.hada(R) / 16, s1, s3))
            for c, yh in enumerate(EV):
                C[c, a, b] = float(W[yh])
    return C


COEF = {k: coeff(*k) for k in SIGNS}
d3, ok3 = {}, True
example = None
for name in pages:
    V = np.array([[float(TW.hada(F)[y]) for y in EV] for F in pages[name]])
    rows = collections.Counter()
    for k, C in COEF.items():
        A = np.einsum('cab,ia->icb', C, V)
        for i in range(len(V)):
            Wt = A[i] @ V.T
            turn = np.abs(Wt[ti]).max(axis=0)
            for j in np.where((turn < 0.5) & (np.abs(Wt).max(axis=0) > 0.5))[0]:
                st = tuple(int(round(Wt[x, j])) for x in (i0, i5, i10, di))
                if st[3] == 0:
                    rows["crossover-type, zero double entry"] += 1
                    continue
                mg = st[0] * st[3] + st[1] * st[2] == 0
                rows["crossover-type, nonzero double entry, " + ("matchgate" if mg else "off the matchgate class")] += 1
                if not mg:
                    rows["  of which rank 1 (independent soft wires)"] += st[0] * st[3] == st[1] * st[2]
                    rows["  of which exact crossovers"] += len(set(st)) == 1
                    if example is None:
                        FQ, FR = pages[name][i], pages[name][j]
                        Wexact = TW.hada(TW.junction(FQ, FR, *k))
                        example = {"pages": name, "page classes": (i, j), "signs (c1, c3)": k,
                                   "straight entries (0000, 0101, 1010, 1111), exact": [int(Wexact[y]) for y in
                                                                                       ((0, 0, 0, 0), (0, 1, 0, 1), (1, 0, 1, 0), (1, 1, 1, 1))],
                                   "turning entries, exact": [int(Wexact[y]) for y in TURN], "MGI, exact": int(TW.mgi(Wexact))}
    d3[name] = dict(rows)
d3["first soft crossing"] = example
ok3 = example is not None and example["MGI, exact"] != 0 and all(t == 0 for t in example["turning entries, exact"]) and \
    all(v != 0 for v in example["straight entries (0000, 0101, 1010, 1111), exact"]) and \
    sum(v.get("  of which exact crossovers", 0) for v in d3.values() if isinstance(v, dict)) == 0
report("3 soft crossings: twisted truncated-octahedron pages give crossover-type junctions off the matchgate class with every straight entry "
       "nonzero; none is an exact crossover", ok3, d3)

# ---------------------------------------------------------------- 4 controls
ctrl = {}
reps = [z for z in ALL4 if z[0] == 0]
Rv = [2, -2, -1, -1, -1, 2, 3, 1]
Qv = [Fraction(1, 7), Fraction(4, 7), 0, 0, Fraction(2, 7), Fraction(1, 7), 0, 0]
Qs, Rs = np.zeros((2, 2, 2, 2), dtype=object), np.zeros((2, 2, 2, 2), dtype=object)
for z, q, r in zip(reps, Qv, Rv):
    Qs[z] = Qs[tuple(1 - t for t in z)] = q
    Rs[z] = Rs[tuple(1 - t for t in z)] = r
ctrl["a junction with a signed branch (negative entries) is an exact crossover"] = is_crossover(TW.junction(Qs, Rs, (0, 0, 0), (0, 0, 0)))
Qw = np.zeros((2, 2, 2, 2), dtype=object)
for z in ALL4:
    Qw[z] = 1 if z[0] == z[2] else 0
Wp = TW.junction(Qw, rand_tensor(0.0, 3), (0, 0, 0), (0, 0, 0))
ctrl["the square's points can carry a wire: W vanishes off x0 = x2 with both colours of c0 alive"] = \
    all(Wp[z] == 0 for z in ALL4 if z[0] != z[2]) and any(Wp[0, a, 0, b] for a in (0, 1) for b in (0, 1)) and \
    any(Wp[1, a, 1, b] for a in (0, 1) for b in (0, 1))
report("4 controls fire", all(ctrl.values()), ctrl)

out["ok"] = ok_all
out["seconds"] = round(time.time() - T0, 1)
print("ALL OK" if ok_all else "SOME CHECK FAILED", out["seconds"], "s")
if "--write" in sys.argv:
    json.dump({"schema_version": 1, "artifact_id": "TWIST-COUNT-20261030-001B-P001", "status": "Proved" if ok_all else "Failed",
               "checks": out}, open(os.path.join(HERE, "result.json"), "w"), indent=1, default=str)
sys.exit(0 if ok_all else 1)
