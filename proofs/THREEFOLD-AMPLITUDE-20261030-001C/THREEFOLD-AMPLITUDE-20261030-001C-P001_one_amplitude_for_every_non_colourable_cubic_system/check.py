"""Checks for THREEFOLD-AMPLITUDE-20261030-001C-P001 (one amplitude for every non-colourable cubic system).

  0 dependency artifacts bound by the hashes recorded in manifest.json
  1 the half-angle: summing out a vertex with couplings +-i pi/6 leaves sqrt(3) times not-all-equal; with the inserted spin it leaves
    2i sin(pi m/6) (exact, sympy); at the knot's own angle pi/3 the constraint is not obtained
  2 the two-way count #col(H) + 6 N_H(L) = 2 sum_p M[L,p] N_HT(p) + R(L), and #col(H) = #col(HT), on 400 random signed cubic systems with up
    to 7 points, colourable or not (brute force)
  3 the Ising sums themselves, both orders of summation, in exact cyclotomic arithmetic on small systems and the Fano plane
  4 one amplitude: A(H, L) at every line equals A(HT, p) at every point, on spaces, cores and trisums of prisms
  5 the signed dictionary on random signed cubic systems: not colourable <=> sign-nonsingular; then every line deletion is colourable
  6 consequences: the law's lambda(0) on two spaces with non-planar trisum glue equals (-1)^(n-1) times the product of brace amplitudes;
    Tutte matchings of planar braces are the same for outer white and black triangles
  7 controls that must fire
Run: .venv/bin/python -B check.py [--write]   (networkx, numpy, sympy; about fifteen seconds)"""
import collections, hashlib, itertools, json, os, random, sys, time
import networkx as nx
import sympy

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
TA = os.path.join(ROOT, "proofs/THREEFOLD-SPACES-20261030-001A/THREEFOLD-SPACES-20261030-001A-P001_three_fold_spaces_are_built_from_the_fano_plane")
GA = os.path.join(ROOT, "proofs/THREEFOLD-GRAMMAR-20261030-001A/THREEFOLD-GRAMMAR-20261030-001A-P001_fano_leaves_and_planar_glue")
AA = os.path.join(ROOT, "proofs/THREEFOLD-AMPLITUDE-20261030-001A/THREEFOLD-AMPLITUDE-20261030-001A-P001_five_per_handle_tuttes_number_per_planar_piece")
for p in (TA, GA, AA):
    sys.path.insert(0, p)
import threefold_lib as T  # noqa: E402
import grammar_lib as M  # noqa: E402
import amplitude_lib as AM  # noqa: E402

T0 = time.time()
out, ok_all = {}, True


def report(key, ok, detail):
    global ok_all
    out[key] = {"ok": bool(ok), "detail": detail}
    ok_all &= bool(ok)
    print(("PASS " if ok else "FAIL ") + key + ": " + json.dumps(detail, default=str)[:2500], flush=True)


# ------------------------------------------------------------------------------------------------ signed systems by incidence
# A system is a list of lines (tuples of points); sg[i][k] is the sign (0/1) of the k-th incidence of line i.
def transpose(H, sg):
    n = 1 + max(p for l in H for p in l)
    HT, sgT, pos = [[] for _ in range(n)], [[] for _ in range(n)], {}
    for i, l in enumerate(H):
        for k, p in enumerate(l):
            pos[(i, k)] = (p, len(HT[p]))
            HT[p].append(i)
            sgT[p].append(sg[i][k])
    return HT, sgT, pos


def proper(vals):
    return len(set(vals)) == 2


def table(H, sg):
    """for every colouring: the colouring and its list of improper lines"""
    n = 1 + max(p for l in H for p in l)
    return [(x, [i for i, l in enumerate(H) if not proper([x[p] ^ sg[i][k] for k, p in enumerate(l)])])
            for x in itertools.product((0, 1), repeat=n)]


def neg_of(H, sg):
    return [(i, p) for i, l in enumerate(H) for k, p in enumerate(l) if sg[i][k]]


def sg_of(H, neg):
    negs = set(neg)
    return [[1 if (i, p) in negs else 0 for p in l] for i, l in enumerate(H)]


def random_system(n, rng, signed=True):
    perms = [list(range(n)) for _ in range(3)]
    for p in perms[1:]:
        rng.shuffle(p)
    H = [(perms[0][i], perms[1][i], perms[2][i]) for i in range(n)]
    sg = [[rng.randint(0, 1) if signed else 0 for _ in range(3)] for _ in range(n)]
    for i, l in enumerate(H):                       # repeated incidences carry equal signs
        for a in range(3):
            for b in range(a):
                if l[a] == l[b]:
                    sg[i][a] = sg[i][b]
    return H, sg


def two_way(H, sg):
    """both sides of the two-way count at every line, and #col(H), #col(HT)"""
    n = len(H)
    HT, sgT, pos = transpose(H, sg)
    dH, dT = table(H, sg), table(HT, sgT)
    colH = sum(1 for x, b in dH if not b)
    colT = sum(1 for x, b in dT if not b)
    NH = [sum(1 for x, b in dH if b == [L]) for L in range(n)]
    NT = [sum(1 for x, b in dT if b == [p]) for p in range(n)]
    rows = []
    for L in range(n):
        rhs = 0
        for k, p in enumerate(H[L]):
            rhs += 2 * NT[p]
            q, kk = pos[(L, k)]
            for y, b in dT:
                if b:
                    continue
                s = [1 - 2 * (y[w] ^ sgT[q][j]) for j, w in enumerate(HT[q])]
                rhs += s[kk] * (1 if sum(s) > 0 else -1)
        rows.append((colH + 6 * NH[L], rhs))
    return colH, colT, rows


# ---------------------------------------------------------------- 0
man = json.load(open(os.path.join(HERE, "manifest.json")))
mism = {r: dg for r, dg in man["parent_bindings"].items()
        if hashlib.sha256(open(os.path.join(ROOT, r), "rb").read()).hexdigest() != dg}
report("0 dependency artifacts bound by hash", not mism, {"parents": len(man["parent_bindings"]), "mismatched": mism})

# ---------------------------------------------------------------- 1 the half-angle
def cis(x):
    """exp(i x), exactly, for rational multiples of pi"""
    return sympy.cos(x) + sympy.I * sympy.sin(x)


d1, ok1 = {}, True
for m in (1, -1, 3, -3):
    c = sympy.simplify(sum(cis(sympy.pi * s * m / 6) for s in (1, -1)))
    si = sympy.simplify(sum(s * cis(sympy.pi * s * m / 6) for s in (1, -1)))
    d1[f"m = {m}"] = {"sum_s exp(i pi s m/6)": str(c), "sum_s s exp(i pi s m/6)": str(si)}
    ok1 &= sympy.simplify(c - (sympy.sqrt(3) if abs(m) == 1 else 0)) == 0
    ok1 &= sympy.simplify(si - 2 * sympy.I * sympy.sin(sympy.pi * m / 6)) == 0
    ok1 &= sympy.simplify(m * si - sympy.I * (1 if abs(m) == 1 else 6)) == 0
report("1 summing out a vertex at the half-angle leaves sqrt(3) times not-all-equal", ok1, d1)

# ---------------------------------------------------------------- 2 the two-way count
rng = random.Random(20261030)
d2 = collections.Counter()
ok2 = True
for trial in range(400):
    n = rng.choice([2, 3, 4, 5, 6, 7])
    H, sg = random_system(n, rng)
    colH, colT, rows = two_way(H, sg)
    good = colH == colT and all(a == b for a, b in rows)
    ok2 &= good
    d2["systems"] += 1
    d2["colourable" if colH else "not colourable"] += 1
    d2["repeated incidences"] += any(len(set(l)) < 3 for l in H)
    d2["failures"] += not good
report("2 the two-way count holds at every line and #col(H) = #col(HT)", ok2 and d2["failures"] == 0, dict(d2))

# ---------------------------------------------------------------- 3 the Ising sums in exact arithmetic
z12 = sympy.exp(sympy.I * sympy.pi / 6)


def ising_sums(H, sg, L):
    """sum_s Omega(s) and sum_s s_L m_L(s) Omega(s) over spins on all points and lines, Omega = z12^(sum_e tau_e s_w s_p)"""
    n = len(H)
    inc = [(i, p, 1 - 2 * sg[i][k]) for i, l in enumerate(H) for k, p in enumerate(l)]
    c0, c1 = collections.Counter(), collections.Counter()
    for sp in itertools.product((1, -1), repeat=n):
        for sl in itertools.product((1, -1), repeat=n):
            E = sum(t * sl[i] * sp[p] for i, p, t in inc)
            c0[E] += 1
            c1[E] += sl[L] * sum(t * sp[p] for i, p, t in inc if i == L)
    Z0 = sum(c * z12 ** E for E, c in c0.items())
    Z1 = sum(c * z12 ** E for E, c in c1.items())
    return sympy.nsimplify(sympy.expand_complex(sympy.simplify(Z0))), sympy.nsimplify(sympy.expand_complex(sympy.simplify(Z1)))


d3, ok3 = [], True
rng3 = random.Random(7)
samples = [("Fano plane", [tuple(l) for l in T.FANO], [[0] * 3 for _ in range(7)]),
           ("doubled square, one class negated", [(0, 1, 1), (0, 0, 1)], [[1, 0, 0], [0, 0, 0]])]
for k in range(10):
    H, sg = random_system(rng3.choice([3, 4, 5]), rng3)
    samples.append((f"random {k}", H, sg))
for name, H, sg in samples:
    n = len(H)
    colH, colT, rows = two_way(H, sg)
    Z0, Z1 = ising_sums(H, sg, 0)
    want0 = sympy.sqrt(3) ** n * colH
    want1 = sympy.I * sympy.sqrt(3) ** (n - 1) * rows[0][0]
    good = sympy.simplify(Z0 - want0) == 0 and sympy.simplify(Z1 - want1) == 0
    ok3 &= good
    d3.append({"system": name, "points": n, "#col": colH, "sum Omega": str(Z0), "inserted sum": str(Z1), "as predicted": good})
report("3 the Ising sums equal sqrt(3)^n #col(H) and i sqrt(3)^(n-1) (#col(H) + 6 N_H(L))", ok3, d3)

# ---------------------------------------------------------------- 4 one amplitude, shared with the transpose
def amplitudes_both(H, neg=()):
    HT = [tuple(i for i, l in enumerate(H) for q in l if q == p) for p in range(1 + max(p for l in H for p in l))]
    negT = [(p, i) for (i, p) in neg]
    return sorted({AM.amplitude(H, L, neg) for L in range(len(H))}), sorted({AM.amplitude(HT, p, negT) for p in range(len(HT))}), \
        AM.colourable(HT, negT)


C4 = [('c', j) for j in range(4)]


def prism_on(k, tag, flip=False):
    m = 2 * k
    g = nx.Graph()
    for i in range(m):
        g.add_edges_from([(('u', i), ('u', (i + 1) % m)), (('v', i), ('v', (i + 1) % m)), (('u', i), ('v', i))])
    face = [('u', 0), ('u', 1), ('v', 1), ('v', 0)]
    target = C4 if not flip else [C4[2], C4[1], C4[0], C4[3]]
    mp = dict(zip(face, target))
    return nx.relabel_nodes(g, lambda v: mp.get(v, (tag, v)))


def trisum_system(ks, flips):
    g = nx.Graph()
    for t, (k, f) in enumerate(zip(ks, flips)):
        g.add_edges_from(prism_on(k, 'abc'[t], f).edges())
    g.remove_edges_from([(C4[j], C4[(j + 1) % 4]) for j in range(4)])
    col = nx.bipartite.color(g)
    if col[C4[0]] != 0:
        col = {v: 1 - c for v, c in col.items()}
    pts = sorted((v for v in g if col[v] == 0), key=str)
    pid = {v: k for k, v in enumerate(pts)}
    return [tuple(sorted(pid[w] for w in g[v])) for v in sorted(g, key=str) if col[v] == 1]


F7 = T.FANO
H13 = T.point_splice(F7, 0, F7, F7[0])
SYSTEMS = {"Fano (7)": (F7, []), "Fano splice (13)": (H13, []), "Fano composition (19)": (T.point_splice(H13, 0, F7, F7[0]), []),
           "3-cycle of blocks (21)": (M.decorate([(0, 1, 1), (0, 0, 2), (1, 2, 2)], []), []),
           "tripod (22)": (M.decorate([(0, 1, 1), (0, 2, 2), (0, 3, 3), (1, 2, 3)], []), []),
           "twisted cube (43)": (M.decorate(M.K4, M.kasteleyn_signing(M.K4)), []),
           "3-cycle core": ([(0, 1, 1), (0, 0, 2), (1, 2, 2)], []), "doubled square, one class negated": ([(0, 1, 1), (0, 0, 1)], [(0, 0)]),
           "cube core, Kasteleyn": (M.K4, M.kasteleyn_signing(M.K4)),
           "35-point trisum core, one twist": ([(0, 1, 2), (0, 1, 3), (0, 4, 5), (1, 6, 7), (2, 6, 8), (2, 7, 9), (3, 4, 6), (3, 5, 7), (4, 8, 8),
                                                (5, 9, 9)], [(0, 0)])}
for ks, fl in [((2, 3, 3), (False, False, False)), ((2, 3, 3), (False, False, True)), ((3, 3, 4), (False, False, True)),
               ((4, 4, 4), (False, False, False))]:
    Ht = trisum_system(ks, fl)
    SYSTEMS[f"trisum of prisms {ks}{' glued with a flip' if any(fl) else ''}"] = (Ht, M.pfaffian_signings(Ht, limit=1)[0])
d4, ok4 = {}, True
for name, (H, neg) in SYSTEMS.items():
    a, aT, colT = amplitudes_both(H, neg)
    d4[name] = {"amplitudes at lines": a, "transposed, at points": aT}
    ok4 &= len(a) == 1 and a == aT and not AM.colourable(H, neg) and not colT
report("4 one amplitude at every line, equal to the transpose's at every point", ok4, d4)

# ---------------------------------------------------------------- 5 the signed dictionary
def sns(H, sg):
    n = len(H)
    S = sympy.zeros(n, n)
    P = sympy.zeros(n, n)
    for i, l in enumerate(H):
        for k, p in enumerate(l):
            S[i, p] += 1 - 2 * sg[i][k]
            P[i, p] += 1
    per = sum(sympy.prod([P[i, s[i]] for i in range(n)]) for s in itertools.permutations(range(n)))
    return per > 0 and abs(S.det()) == per


rng5 = random.Random(5)
d5 = collections.Counter()
for trial in range(300):
    H, sg = random_system(rng5.choice([3, 4, 5, 6]), rng5)
    g = nx.Graph([(('L', i), ('P', p)) for i, l in enumerate(H) for p in l])
    if not nx.is_connected(g):
        continue
    neg = neg_of(H, sg)
    col = AM.colourable(H, neg)
    s = sns(H, sg)
    d5["connected systems"] += 1
    d5["not colourable"] += not col
    d5["dictionary fails"] += col == s
    if not col:
        d5["not colourable but a line deletion is not colourable"] += not all(AM.count(H, neg, drop=L) > 0 for L in range(len(H)))
report("5 not colourable <=> sign-nonsingular, and then minimally so", d5["dictionary fails"] == 0 and
       d5["not colourable but a line deletion is not colourable"] == 0 and d5["not colourable"] > 20, dict(d5))

# ---------------------------------------------------------------- 6 consequences
d6, ok6 = {}, True


def brace_product(H):
    prod, kinds = 1, []
    for b in M.decompose(M.multigraph(H)):
        t = 'theta' if len(b) == 2 else M.brace_type(b)[0]
        pts = sorted([v for v in b if M.kind(v) == 'P'], key=str)
        pid = {v: k for k, v in enumerate(pts)}
        Hb = [tuple(sorted(pid[w] for w in b[v])) for v in sorted(b, key=str) if M.kind(v) == 'L']
        f = 1 if t in ('theta', 'doubled square') else AM.amplitude(Hb, 0, M.pfaffian_signings(Hb, limit=1)[0])
        prod *= f
        kinds.append(t)
    return prod, collections.Counter(kinds)


for ks, fl in [((2, 2, 3), (False, False, False)), ((2, 3, 3), (False, False, True))]:
    P = trisum_system(ks, fl)
    H = M.decorate(P, M.pfaffian_signings(P, limit=1)[0])
    n = T.npoints(H)
    prod, kinds = brace_product(H)
    rows = []
    for L0 in (H[0], H[len(H) // 2]):
        exact, lam = AM.lambda0(T.gadget_from(H, L0))
        rows.append((exact, sorted(lam)))
        ok6 &= exact and lam == {(-1) ** (n - 1) * prod}
    d6[f"space with trisum glue {ks}{' (flip)' if any(fl) else ''}"] = {"points": n, "braces": dict(kinds), "product": prod,
                                                                       "law at two corners (exact, lambda(0))": rows}
tm = {}
for name, P in [("cube", M.K4), ("hexagonal prism", M.cubic_planar_bipartite('hexagonal prism')),
                ("truncated octahedron", M.cubic_planar_bipartite('truncated octahedron'))]:
    PT = [tuple(i for i, l in enumerate(P) for q in l if q == p) for p in range(1 + max(p for l in P for p in l))]
    white = sorted({AM.tutte_matchings(P, L) for L in range(len(P))})
    black = sorted({AM.tutte_matchings(PT, p) for p in range(len(PT))})
    tm[name] = {"outer white triangles": white, "outer black triangles": black}
    ok6 &= len(white) == 1 and white == black
d6["Tutte matchings of planar braces"] = tm
report("6 the law on spaces with trisum glue; Tutte matchings the same for white and black outer triangles", ok6, d6)

# ---------------------------------------------------------------- 7 controls
ctrl = {}
COL = [(0, 1, 3), (1, 4, 6), (0, 1, 2), (3, 4, 5), (2, 4, 5), (0, 5, 6), (2, 3, 6)]
ctrl["a colourable connected cubic system has different counts at different lines (8, 11, 13)"] = \
    AM.colourable(COL) and sorted({AM.amplitude(COL, L) for L in range(7)}) == [8, 11, 13]
colH, colT, rows = two_way(COL, [[0] * 3 for _ in range(7)])
ctrl["there the extra terms #col(H) and R(L) are nonzero, and the two-way count still holds"] = colH > 0 and all(a == b for a, b in rows) and \
    len({b for a, b in rows}) > 1
DIS = [tuple(l) for l in F7] + [tuple(p + 7 for p in l) for l in M.K4]
ctrl["a disconnected non-colourable system has two amplitudes (connectivity is needed)"] = \
    not AM.colourable(DIS) and len({AM.amplitude(DIS, L) for L in range(len(DIS))}) == 2
vals = {m: sympy.simplify(sum(cis(sympy.pi * s * m / 3) for s in (1, -1))) for m in (1, 3)}
ctrl["at the knot's own angle pi/3 summing out gives 1 and -2, not a constraint"] = vals == {1: 1, 3: -2}
report("7 controls fire", all(ctrl.values()), ctrl)

out["ok"] = ok_all
out["seconds"] = round(time.time() - T0, 1)
print("ALL OK" if ok_all else "SOME CHECK FAILED", out["seconds"], "s")
if "--write" in sys.argv:
    json.dump({"schema_version": 1, "artifact_id": "THREEFOLD-AMPLITUDE-20261030-001C-P001", "status": "Proved" if ok_all else "Failed",
               "checks": out}, open(os.path.join(HERE, "result.json"), "w"), indent=1, default=str)
sys.exit(0 if ok_all else 1)
