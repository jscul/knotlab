"""Checks for THREEFOLD-AMPLITUDE-20261030-001A-P001 (five per handle, Tutte's number per planar piece).

  0 dependency artifacts bound by the hashes recorded in manifest.json
  1 the amplitude identity: on gadgets of eight three-fold spaces (7 to 43 triangles, two corner lines each), the knot's corner relation is
    exact with lambda(0) = (-1)^(n-1) A(H, L) (so -125 at 22 triangles)
  2 the point lemma at every point of five spaces and of five signed cores, some with a point twice on a line: no colouring of the rest when
    p's three incidences all see p's value; A(H, l_i) colourings when only the incidence on l_i sees the complement
  3 brace amplitudes at every corner: Heawood 5; doubled square 1 with an odd number of negated classes (colourable with an even number);
    planar braces (cube, 6- to 14-prisms, truncated octahedron) = Tutte matchings = arborescence number in each colour class, not
    colourable with the Kasteleyn signing; trisum of three cubes 6 with its Pfaffian signing, not colourable
  4 the factorization on eleven spaces up to 90 points: A(H) equals the product of the braces' amplitudes; with doubled-square glue A = 5^atoms
  5 controls that must fire
Run: .venv/bin/python -B check.py [--write]   (networkx, numpy, sympy; about five seconds)"""
import collections, hashlib, itertools, json, os, sys, time
import networkx as nx

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
TA = os.path.join(ROOT, "proofs/THREEFOLD-SPACES-20261030-001A/THREEFOLD-SPACES-20261030-001A-P001_three_fold_spaces_are_built_from_the_fano_plane")
GA = os.path.join(ROOT, "proofs/THREEFOLD-GRAMMAR-20261030-001A/THREEFOLD-GRAMMAR-20261030-001A-P001_fano_leaves_and_planar_glue")
for p in (TA, GA, HERE):
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


def system_of(g):
    col = nx.bipartite.color(g)
    pts = sorted((v for v in g if col[v] == 0), key=str)
    pid = {v: k for k, v in enumerate(pts)}
    return [tuple(sorted(pid[w] for w in g[v])) for v in sorted(g, key=str) if col[v] == 1]


def prism(k):
    g = nx.Graph()
    m = 2 * k
    for i in range(m):
        g.add_edges_from([(('u', i), ('u', (i + 1) % m)), (('v', i), ('v', (i + 1) % m)), (('u', i), ('v', i))])
    return system_of(g)


# ---------------------------------------------------------------- 0
man = json.load(open(os.path.join(HERE, "manifest.json")))
mism = {r: dg for r, dg in man["parent_bindings"].items()
        if hashlib.sha256(open(os.path.join(ROOT, r), "rb").read()).hexdigest() != dg}
report("0 dependency artifacts bound by hash", not mism, {"parents": len(man["parent_bindings"]), "mismatched": mism})

F7 = T.FANO
H13 = T.point_splice(F7, 0, F7, F7[0])
SPACES = {"Fano (7)": F7, "Fano splice (13)": H13, "Fano composition (19)": T.point_splice(H13, 0, F7, F7[0]),
          "3-cycle of blocks (21)": M.decorate([(0, 1, 1), (0, 0, 2), (1, 2, 2)], []),
          "tripod core (22)": M.decorate([(0, 1, 1), (0, 2, 2), (0, 3, 3), (1, 2, 3)], []),
          "5-cycle of blocks (35)": M.decorate([(0, 1, 1), (1, 2, 2), (2, 3, 3), (3, 4, 4), (4, 0, 0)], []),
          "Fano composition (25)": T.point_splice(T.point_splice(H13, 0, F7, F7[0]), 0, F7, F7[0]),
          "twisted cube (43)": M.decorate(M.K4, M.kasteleyn_signing(M.K4))}

# ---------------------------------------------------------------- 1 the amplitude identity
d1 = {}
ok1 = True
for name, H in SPACES.items():
    n = T.npoints(H)
    rows = []
    for L0 in (H[0], H[len(H) // 2]):
        exact, lam = AM.lambda0(T.gadget_from(H, L0))
        A = AM.amplitude(H, H.index(L0))
        rows.append({"corner line": L0, "exact": exact, "lambda(0)": sorted(lam), "(-1)^(n-1) A": (-1) ** (n - 1) * A})
        ok1 &= exact and lam == {(-1) ** (n - 1) * A}
    d1[name] = rows
report("1 the knot's exactness factor is lambda(0) = (-1)^(n-1) A(H, L)", ok1, d1)

# ---------------------------------------------------------------- 2 the point lemma
def lemma_points(H, neg=()):
    negs = set(neg)
    amps = {L: AM.amplitude(H, L, neg) for L in range(len(H))}
    pts = sorted({p for l in H for p in l})
    good = 0
    for p in pts:
        inc, N = AM.point_counts(H, p, neg)
        t = [1 if (i, p) in negs else 0 for i, k in inc]
        ok = True
        for c in (0, 1):
            shown = [c ^ ti for ti in t]
            ok &= N[tuple(shown)] == 0
            for j in range(3):
                y = list(shown)
                y[j] ^= 1
                ok &= N[tuple(y)] == amps[inc[j][0]]
        good += ok
    return len(pts), good


CORES = {"3-cycle core (repeated points)": ([(0, 1, 1), (0, 0, 2), (1, 2, 2)], []),
         "tripod core (repeated points)": ([(0, 1, 1), (0, 2, 2), (0, 3, 3), (1, 2, 3)], []),
         "doubled square, one class negated": ([(0, 1, 1), (0, 0, 1)], [(0, 0)]),
         "cube core, Kasteleyn signing": (M.K4, M.kasteleyn_signing(M.K4)),
         "trisum core of the 35-point space, one twist (repeated points)":
             ([(0, 1, 2), (0, 1, 3), (0, 4, 5), (1, 6, 7), (2, 6, 8), (2, 7, 9), (3, 4, 6), (3, 5, 7), (4, 8, 8), (5, 9, 9)], [(0, 0)])}
d2 = {}
ok2 = True
for name in ("Fano (7)", "Fano splice (13)", "Fano composition (19)", "3-cycle of blocks (21)", "tripod core (22)"):
    n_p, good = lemma_points(SPACES[name])
    d2[name] = {"points": n_p, "points obeying the lemma": good}
    ok2 &= good == n_p
for name, (H, neg) in CORES.items():
    col = AM.colourable(H, neg)
    n_p, good = lemma_points(H, neg)
    rep = sum(1 for l in H if len(set(l)) < 3)
    d2[name] = {"colourable": col, "lines with a repeated point": rep, "points": n_p, "points obeying the lemma": good}
    ok2 &= not col and good == n_p
report("2 the point lemma holds at every point", ok2, d2)

# ---------------------------------------------------------------- 3 brace amplitudes
d3 = {}
d3["Heawood: amplitude at every line"] = sorted({AM.amplitude(F7, L) for L in range(7)})
DS = [(0, 1, 1), (0, 0, 1)]
classes = [(0, 0), (0, 1), (1, 0), (1, 1)]
ds = {}
for k in range(5):
    for S in itertools.combinations(classes, k):
        neg = list(S)
        if AM.colourable(DS, neg):
            ds.setdefault("colourable", set()).add(k)
        else:
            ds.setdefault("amplitudes when not colourable", set()).update({AM.amplitude(DS, L, neg) for L in range(2)})
            ds.setdefault("negated classes when not colourable", set()).add(k)
d3["doubled square"] = {k: sorted(v) for k, v in ds.items()}
planar = {}
okp = True
glues = {"cube": M.K4, **{f"{2 * k}-prism": prism(k) for k in range(3, 8)}, "truncated octahedron": M.cubic_planar_bipartite('truncated octahedron')}
for name, P in glues.items():
    neg = M.kasteleyn_signing(P)
    amps = sorted({AM.amplitude(P, L, neg) for L in range(len(P))})
    tm = sorted({AM.tutte_matchings(P, L) for L in range(len(P))})
    arb = [AM.arborescence_number(P, c) for c in range(3)]
    col = AM.colourable(P, neg)
    planar[name] = {"amplitudes": amps, "Tutte matchings": tm, "arborescence numbers": arb, "colourable": col}
    okp &= len(amps) == 1 and amps == tm and set(arb) == set(amps) and not col
d3["planar braces"] = planar
C4 = [('c', j) for j in range(4)]
TRI = M.trisum([M.cube_on(C4, 'a'), M.cube_on(C4, 'b'), M.cube_on(C4, 'd')], C4, [(C4[j], C4[(j + 1) % 4]) for j in range(4)])
HT = system_of(TRI)
sig = M.pfaffian_signings(HT, limit=1)[0]
d3["trisum of three cubes: amplitudes, colourable"] = (sorted({AM.amplitude(HT, L, sig) for L in range(len(HT))}), AM.colourable(HT, sig))
ok3 = d3["Heawood: amplitude at every line"] == [5] and ds.get("amplitudes when not colourable") == {1} and \
    ds.get("negated classes when not colourable") == {1, 3} and ds.get("colourable") == {0, 2, 4} and okp and \
    d3["trisum of three cubes: amplitudes, colourable"] == ([6], False)
report("3 brace amplitudes: Heawood 5, doubled square 1, planar braces Tutte's number, trisum of three cubes 6", ok3, d3)

# ---------------------------------------------------------------- 4 the factorization
d4 = {}
ok4 = True


def brace_factor(b):
    t = M.brace_type(b)[0]
    if t == 'heawood':
        return 5, t
    if t == 'doubled square':
        return 1, t
    g = nx.Graph([(u, w) for u in b for w in b[u]])
    pts = sorted([v for v in b if M.kind(v) == 'P'], key=str)
    pid = {v: k for k, v in enumerate(pts)}
    Hb = [tuple(sorted(pid[w] for w in b[v])) for v in sorted(b, key=str) if M.kind(v) == 'L']
    if t == 'planar':
        return AM.arborescence_number(Hb, 0), t
    return AM.amplitude(Hb, 0, M.pfaffian_signings(Hb, limit=1)[0]), t


factor_spaces = dict(SPACES)
for glue in ('hexagonal prism', 'truncated octahedron'):
    P = M.cubic_planar_bipartite(glue)
    factor_spaces[f"{glue} as glue ({T.npoints(M.decorate(P, M.kasteleyn_signing(P)))})"] = M.decorate(P, M.kasteleyn_signing(P))
CORE35 = [(0, 1, 2), (0, 1, 3), (0, 4, 5), (1, 6, 7), (2, 6, 8), (2, 7, 9), (3, 4, 6), (3, 5, 7), (4, 8, 8), (5, 9, 9)]
factor_spaces["trisum of three cubes as glue (35)"] = M.decorate(CORE35, [(0, 0)])
for name, H in factor_spaces.items():
    br = M.decompose(M.multigraph(H))
    facs = [brace_factor(b) for b in br]
    prod = 1
    for f, t in facs:
        prod *= f
    A = AM.amplitude(H, 0)
    A2 = AM.amplitude(H, len(H) - 1)
    kinds = collections.Counter(t for f, t in facs)
    d4[name] = {"amplitude (two corners)": (A, A2), "braces": dict(kinds), "product of brace amplitudes": prod}
    ok4 &= A == A2 == prod
    if set(kinds) <= {'heawood', 'doubled square'}:
        ok4 &= A == 5 ** kinds['heawood']
report("4 the amplitude is the product of the braces' amplitudes (5^atoms with doubled-square glue)", ok4, d4)

# ---------------------------------------------------------------- 5 controls
ctrl = {}
P = M.K4
ctrl["the cube core without its Kasteleyn signs is colourable"] = AM.colourable(P, [])
ctrl["a signing of the cube core with one face of the wrong parity is colourable"] = AM.colourable(P, [(0, 1), (1, 2)])
NAE = AM.knot_table()
plain = NAE.copy()
for a, b, c in itertools.product((0, 1), repeat=3):
    plain[a, b, c] = 0 if a == b == c else 1
R = AM.corner_relation(T.gadget_from(SPACES["tripod core (22)"], SPACES["tripod core (22)"][0]), plain)
ctrl["plain not-all-equal on the 22-triangle gadget gives +125: the sign comes from the signed knot"] = R[(0, 0, 1)] == 125
ctrl["the Fano plane is not 2-colourable but every line deletion is"] = not AM.colourable(F7) and all(AM.count(F7, drop=L) > 0 for L in range(7))
report("5 controls fire", all(ctrl.values()), ctrl)

out["ok"] = ok_all
out["seconds"] = round(time.time() - T0, 1)
print("ALL OK" if ok_all else "SOME CHECK FAILED", out["seconds"], "s")
if "--write" in sys.argv:
    json.dump({"schema_version": 1, "artifact_id": "THREEFOLD-AMPLITUDE-20261030-001A-P001", "status": "Proved" if ok_all else "Failed",
               "checks": out}, open(os.path.join(HERE, "result.json"), "w"), indent=1, default=str)
sys.exit(0 if ok_all else 1)
