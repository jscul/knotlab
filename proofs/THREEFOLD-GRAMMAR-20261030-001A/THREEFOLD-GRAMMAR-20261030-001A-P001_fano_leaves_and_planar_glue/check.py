"""Checks for THREEFOLD-GRAMMAR-20261030-001A-P001 (Fano leaves and planar glue).

  0 dependency artifacts bound by the hashes recorded in manifest.json
  1 the approved grammar is incomplete: the twisted cube (43 points) is a linear connected cubic triple system, minimally not
    2-colourable, whose tight-cut decomposition contains a planar brace (the cube) besides Heawood graphs and doubled squares, while Fano
    compositions and cycles of Fano blocks (plain, twisted, spliced) decompose into Heawood graphs and doubled squares only
  2 structure: every computed decomposition has cubic pieces; a brace with a parallel pair has four vertices (the doubled hexagon is
    not a brace); the doubled square is sign-nonsingular exactly for an odd number of negated parallel classes; every leaf is simple
  3 the one-twist lemma: the Heawood graph (21 single negations, none SNS; one Pfaffian class, the trivial one); planar braces (cube,
    hexagonal prism, truncated octahedron) and non-planar trisums (three cubes along a 4-cycle, 16 vertices; that graph with two more
    cubes along one of its 4-cycles, 24 vertices): braces, one Pfaffian class each, every 4-cycle edge-disjoint from another, at least
    two (three for the trisums) pairwise edge-disjoint 4-cycles, no SNS signing with at most one negated edge
  4 Fano leaves on every constructed system: all leaves of the decomposition are Heawood graphs (Fano blocks or dual blocks; the Fano
    splice has one of each)
  5 decoration: Kasteleyn signings of the cube, the hexagonal prism and the truncated octahedron, and the 3-cycle and tripod cores with
    repeated incidences, decorate to linear connected cubic triple systems that are not 2-colourable (43, 45, 90, 21, 22 points); every
    line removal of the smaller ones leaves a 2-colourable system (the duality's conditions for knot spaces)
  6 controls that must fire
Run: .venv/bin/python -B check.py [--write]   (networkx, python-sat, numpy, sympy; a few minutes)"""
import collections, hashlib, itertools, json, os, sys, time
import networkx as nx

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
TA = os.path.join(ROOT, "proofs/THREEFOLD-SPACES-20261030-001A/THREEFOLD-SPACES-20261030-001A-P001_three_fold_spaces_are_built_from_the_fano_plane")
sys.path.insert(0, HERE)
sys.path.insert(0, TA)
import threefold_lib as T  # noqa: E402
import grammar_lib as M  # noqa: E402

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

F = T.FANO
linear = lambda H: all(len(set(a) & set(b)) <= 1 for a, b in itertools.combinations(H, 2))  # noqa: E731


def summary(H):
    br = M.decompose(M.multigraph(H))
    types = collections.Counter(M.brace_type(b)[0] for b in br)
    leaves = collections.Counter(M.brace_type(b)[0] for b in br if M.brace_type(b)[1] == 1)
    cubic = all(sum(nb.values()) == 3 for b in br for nb in b.values())
    return dict(types), dict(leaves), cubic, br


def minimal(H):
    return all(T.colourable_sat([l for j, l in enumerate(H) if j != i]) for i in range(len(H)))


# ---------------------------------------------------------------- 1 the approved grammar is incomplete
d1 = {}
CUBE43 = M.decorate(M.K4, M.kasteleyn_signing(M.K4))
types43, leaves43, cubic43, _ = summary(CUBE43)
d1["twisted cube: points, linear, connected, 2-colourable, minimal"] = (T.npoints(CUBE43), linear(CUBE43), T.connected(CUBE43),
                                                                        T.colourable_sat(CUBE43), minimal(CUBE43))
d1["twisted cube: brace types, leaves"] = (types43, leaves43)
gen = {"Fano splice (13)": T.point_splice(F, 0, F, F[0]), "line splice (13)": T.line_splice(F, F[0], F, 0),
       "Fano composition (19)": T.point_splice(T.point_splice(F, 0, F, F[0]), 0, F, F[0]),
       "3-cycle of blocks (21)": M.decorate([(0, 1, 1), (0, 0, 2), (1, 2, 2)], []),
       "5-cycle of blocks (35)": M.decorate([(0, 1, 1), (1, 2, 2), (2, 3, 3), (3, 4, 4), (4, 0, 0)], []),
       "twisted 2-cycle spliced pair (27)": T.point_splice(M.T14, 0, M.T14, M.T14[0])}
gen_types = {}
for name, H in gen.items():
    ty, lv, cb, _ = summary(H)
    gen_types[name] = (ty, T.colourable_sat(H))
d1["generated systems: brace types, 2-colourable"] = gen_types
ok1 = d1["twisted cube: points, linear, connected, 2-colourable, minimal"] == (43, True, True, False, True) and types43.get('planar') == 1 \
    and all(set(ty) <= {'heawood', 'doubled square'} and not col for ty, col in gen_types.values())
report("1 the twisted cube needs a planar brace; splices and cycles of Fano blocks never do", ok1, d1)

# ---------------------------------------------------------------- 2 structure
d2 = {}
DH = [(0, 1, 1), (0, 0, 2), (1, 2, 2)]            # the doubled hexagon (core of the 3-cycle)
X = M.find_tight_cut(M.multigraph(DH))
d2["doubled hexagon has a nontrivial tight cut (size of shore)"] = None if X is None else len(X)
D4 = [(0, 1, 1), (0, 0, 1)]                        # the doubled square: lines (p, q, q), (p, p, q)
classes = [(0, 0), (0, 1), (1, 0), (1, 1)]         # (line, point) parallel classes
sns_patterns = []
for k in range(5):
    for S in itertools.combinations(classes, k):
        A = T.matrix(D4)
        for (i, p) in S:
            A[i, p] = -A[i, p]
        d = T.det(A)
        P = T.permanent(abs(A))
        if abs(d) == P:
            sns_patterns.append(len(S))
d2["doubled square: numbers of negated classes over its SNS signings"] = sorted(collections.Counter(sns_patterns).items())
allbr = []
for H in list(gen.values()) + [CUBE43]:
    allbr += M.decompose(M.multigraph(H))
mult4 = all(len(b) == 4 for b in allbr if any(k > 1 for nb in b.values() for k in nb.values()))
leaves_simple = all(not any(k > 1 for nb in b.values() for k in nb.values()) for b in allbr if M.brace_type(b)[1] == 1)
d2["every brace with a parallel pair has 4 vertices; every leaf is simple (all computed decompositions)"] = (mult4, leaves_simple)
ok2 = d2["doubled hexagon has a nontrivial tight cut (size of shore)"] == 3 and set(sns_patterns) == {1, 3} and mult4 and leaves_simple
report("2 decomposition structure: multigraph braces are doubled squares, leaves are simple", ok2, d2)

# ---------------------------------------------------------------- 3 the one-twist lemma
d3 = {}
flips = [(i, p) for i, l in enumerate(F) for p in l]
d3["Heawood: single negations that are SNS (of 21), Pfaffian classes"] = (sum(1 for f in flips if T.sns(F, [f])[0]), M.pfaffian_signings(F))


def one_twist_sns(H):
    inc = [(i, p) for i, l in enumerate(H) for p in l]
    return sum(1 for e in inc if T.sns(H, [e])[0]) + int(T.sns(H)[0])


def ring(C):
    return [(C[j], C[(j + 1) % 4]) for j in range(4)]


C4 = [('c', j) for j in range(4)]
TRI = M.trisum([M.cube_on(C4, 'a'), M.cube_on(C4, 'b'), M.cube_on(C4, 'd')], C4, ring(C4))
Q4 = [('a', j) for j in range(4)]
NEST = M.trisum([TRI, M.cube_on(Q4, 'e'), M.cube_on(Q4, 'f')], Q4, ring(Q4))
braces = {name: M.cubic_planar_bipartite(name) for name in ("cube", "hexagonal prism", "truncated octahedron")}
braces["trisum of three cubes (16 vertices)"] = M.system_of(TRI)
braces["trisum of that with two cubes (24 vertices)"] = M.system_of(NEST)
recs = {}
for name, H in braces.items():
    recs[name] = {"planar": nx.check_planarity(M.bipartite(H))[0], "brace": M.find_tight_cut(M.multigraph(H)) is None,
                  "Pfaffian classes": len(M.pfaffian_signings(H)),
                  "every 4-cycle has an edge-disjoint 4-cycle": M.every_4cycle_has_a_disjoint_partner(H),
                  "pairwise edge-disjoint 4-cycles (capped at 3)": M.max_disjoint_4cycles(H),
                  "SNS signings with at most one negated edge": one_twist_sns(H)}
d3["Pfaffian braces"] = recs
ok3 = d3["Heawood: single negations that are SNS (of 21), Pfaffian classes"] == (0, [[]])
for name, r in recs.items():
    nonplanar = name.startswith("trisum")
    ok3 &= r["brace"] and r["Pfaffian classes"] == 1 and r["every 4-cycle has an edge-disjoint 4-cycle"] and \
        r["pairwise edge-disjoint 4-cycles (capped at 3)"] >= (3 if nonplanar else 2) and r["SNS signings with at most one negated edge"] == 0 \
        and r["planar"] != nonplanar
report("3 one negated edge never makes a brace sign-nonsingular; only the Heawood graph needs none (planar braces and trisums)", ok3, d3)

# ---------------------------------------------------------------- 4 Fano leaves on the constructed systems
d4 = {}
ok4 = True
for name, H in list(gen.items()) + [("twisted cube (43)", CUBE43)]:
    ty, lv, cb, _ = summary(H)
    kinds = M.leaf_kinds(H)
    d4[name] = ({k[1]: v for k, v in kinds.items()}, cb)
    ok4 &= set(lv) == {'heawood'} and cb and sum(lv.values()) >= 2
ok4 &= d4["Fano splice (13)"][0] == {"block": 1, "dual block": 1}
report("4 every leaf of every constructed system is a Fano piece (at least two)", ok4, d4)

# ---------------------------------------------------------------- 5 decoration
d5 = {}
ok5 = True
for name, (core, signing) in {
        "cube": (M.K4, M.kasteleyn_signing(M.K4)),
        "hexagonal prism": (M.cubic_planar_bipartite('hexagonal prism'), M.kasteleyn_signing(M.cubic_planar_bipartite('hexagonal prism'))),
        "truncated octahedron": (M.cubic_planar_bipartite('truncated octahedron'), M.kasteleyn_signing(M.cubic_planar_bipartite('truncated octahedron'))),
        "3-cycle core": ([(0, 1, 1), (0, 0, 2), (1, 2, 2)], []),
        "tripod core": ([(0, 1, 1), (0, 2, 2), (0, 3, 3), (1, 2, 3)], [])}.items():
    core_sns = T.sns(core, signing)[0] if T.npoints(core) <= 12 else None
    H = M.decorate(core, signing)
    rec = {"core SNS with the signing": core_sns, "points": T.npoints(H), "linear": linear(H), "connected": T.connected(H),
           "cubic": T.is_cubic(H), "2-colourable": T.colourable_sat(H)}
    if T.npoints(H) <= 45:
        rec["every line removal 2-colourable"] = minimal(H)
    d5[name] = rec
    ok5 &= core_sns is not False and rec["linear"] and rec["connected"] and rec["cubic"] and not rec["2-colourable"] and rec.get("every line removal 2-colourable", True)
report("5 every signed core decorates to a three-fold knot space (planar glue of any shape)", ok5, d5)

# ---------------------------------------------------------------- 6 controls
ctrl = {}
bad = [(0, 1), (1, 2)]                            # not a Kasteleyn signing of the cube
ctrl["the cube with a non-Kasteleyn signing decorates to a 2-colourable system"] = T.colourable_sat(M.decorate(M.K4, bad))
ctrl["the 2-cycle core (two blocks, untwisted) is 2-colourable"] = T.colourable_sat(M.decorate([(0, 1, 1), (0, 0, 1)], []))
ctrl["a planar cubic bipartite graph with the trivial signing is not SNS"] = not T.sns(M.cubic_planar_bipartite('hexagonal prism'))[0]
ctrl["the Fano plane is a single brace"] = M.find_tight_cut(M.multigraph(F)) is None
ctrl["K3,3 (three lines on the same three points) has no Pfaffian signing"] = M.pfaffian_signings([(0, 1, 2)] * 3) == []
report("6 controls fire", all(ctrl.values()), ctrl)

out["ok"] = ok_all
out["seconds"] = round(time.time() - T0, 1)
print("ALL OK" if ok_all else "SOME CHECK FAILED", out["seconds"], "s")
if "--write" in sys.argv:
    json.dump({"schema_version": 1, "artifact_id": "THREEFOLD-GRAMMAR-20261030-001A-P001", "status": "Proved" if ok_all else "Failed",
               "checks": out}, open(os.path.join(HERE, "result.json"), "w"), indent=1, default=str)
sys.exit(0 if ok_all else 1)
