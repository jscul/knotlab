"""Checks for THREEFOLD-SURFACES-20261030-001A-P001 (Fano atoms are handles).

  0 dependency artifacts bound by the hashes recorded in manifest.json
  1 the permutation table at a 3-edge cut (exhaustive over S3): the connected-sum inequality, D >= 0 when a side's transition is a
    3-cycle, D >= -4 with equality only at (id, id), D = -2 only when both transitions fix an edge, and D = 0 for two 3-cycles iff inverse
  2 the face-tracing identity 2(g - g1 - g2) = D on random rotation systems of three splices, for all rotations at the contracted vertices
  3 the Heawood graph: girth 6, genus 1, genus 1 after deleting a vertex; 16 torus rotation systems, one orbit under automorphisms and
    mirroring, eight per chirality, all faces hexagons; any two faces share exactly one edge (dual K7); the faces around the points, and
    around the lines, form Fano planes on the seven faces
  4 the splice lemma on examples: the Heawood graph spliced into seven graphs R (two bijections each) has genus genus(R) + 1; K3,3
    spliced with K3,3 has genus 1 (K3,3 minus a vertex is planar)
  5 the 13-point space: 128 = 16 * 16 / 2 minimum-genus rotation systems, every one a standard connected sum (transitions inverse
    3-cycles, both induced embeddings Heawood maps), faces 8 hexagons and 3 decagons
  6 the genus formula on examples (Fano 7, splice 13, composition 19, 3-cycle of blocks 21, tripod core 22, and the twisted cube 43):
    genus = number of Heawood braces; the trisum of three cubes has genus 1 and keeps it after deleting any vertex; the doubled square has
    4 planar rotation systems
  7 controls that must fire
Run: .venv/bin/python -B check.py [--write]   (python-sat, networkx; a few minutes)"""
import collections, hashlib, itertools, json, os, random, sys, time
import networkx as nx

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
TA = os.path.join(ROOT, "proofs/THREEFOLD-SPACES-20261030-001A/THREEFOLD-SPACES-20261030-001A-P001_three_fold_spaces_are_built_from_the_fano_plane")
GA = os.path.join(ROOT, "proofs/THREEFOLD-GRAMMAR-20261030-001A/THREEFOLD-GRAMMAR-20261030-001A-P001_fano_leaves_and_planar_glue")
for p in (TA, GA, HERE):
    sys.path.insert(0, p)
import threefold_lib as T  # noqa: E402
import grammar_lib as M  # noqa: E402
import surface_lib as S  # noqa: E402

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

# ---------------------------------------------------------------- 1 the permutation table
d1 = {}
ident = (0, 1, 2)
cyc3 = set(S.CYCLES3)
fixes = lambda p: any(p[i] == i for i in range(3))  # noqa: E731
sum_ineq = all(S.D(t, p, r, S.inverse(r)) <= 0 for t in S.S3 for p in S.S3 for r in S.CYCLES3)
Dmax = {(t, p): max(S.D(t, p, r, rt) for r in S.CYCLES3 for rt in S.CYCLES3) for t in S.S3 for p in S.S3}
d1["connected-sum inequality D(tau, pi, r, r^-1) <= 0 (72 cases)"] = sum_ineq
d1["max D >= 0 whenever tau or pi is a 3-cycle"] = all(v >= 0 for (t, p), v in Dmax.items() if t in cyc3 or p in cyc3)
d1["max D >= -4, equality only at (id, id)"] = (min(Dmax.values()) == -4 and [k for k, v in Dmax.items() if v == -4] == [(ident, ident)])
d1["max D = -2 only when both transitions fix an edge"] = all(fixes(t) and fixes(p) for (t, p), v in Dmax.items() if v == -2)
d1["two 3-cycles: max D = 0 iff pi = tau^-1, else 2"] = all((Dmax[(t, p)] == 0) == (p == S.inverse(t)) and Dmax[(t, p)] in (0, 2)
                                                              for t in cyc3 for p in cyc3)
d1["max D distribution"] = sorted(collections.Counter(Dmax.values()).items())
report("1 the permutation table at a 3-edge cut", all(v is True for k, v in d1.items() if k != "max D distribution"), d1)

# ---------------------------------------------------------------- 2 the face-tracing identity
HW = S.from_nx(M.bipartite(T.FANO))
K33 = S.from_nx(nx.complete_bipartite_graph(3, 3))
CUBE = S.from_nx(nx.convert_node_labels_to_integers(nx.hypercube_graph(3)))
PET = S.from_nx(nx.petersen_graph())
rnd = random.Random(20261030)
tested = bad = 0
for A, R in ((HW, HW), (HW, PET), (K33, CUBE)):
    x, y = A[0][0], R[0][0]
    G = S.splice(A, x, R, y, (1, 2, 0))
    Y = {('a', v) for v in S.vertices(A) if v != x}
    Yb = set(S.vertices(G)) - Y
    for trial in range(100):
        rot = S.random_rotation(G, rnd)
        c, tau, pi = S.cut_data(G, rot, Y)
        g = S.genus_of(G, rot)
        for r in S.CYCLES3:
            for rt in S.CYCLES3:
                g1 = S.genus_of(*S.contract_side(G, rot, Y, c, r, 'X'))
                g2 = S.genus_of(*S.contract_side(G, rot, Yb, c, rt, 'Z'))
                tested += 1
                bad += 2 * (g - g1 - g2) != S.D(tau, pi, r, rt)
report("2 the face-tracing identity 2(g - g1 - g2) = D", bad == 0 and tested == 1200, {"tested": tested, "failures": bad})

# ---------------------------------------------------------------- 3 the Heawood graph and its map
d3 = {}
hw = nx.Graph(HW)
d3["girth"] = nx.girth(hw)
d3["genus"] = S.genus(HW)
d3["genus after deleting a vertex (every vertex)"] = sorted({S.genus_reduced([e for e in HW if v not in e]) for v in S.vertices(HW)})
mins = S.min_genus_rotations(HW, 1)
autos = S.automorphisms(HW)
rots = [S.rotation(HW, b) for b in mins]
orbit_all = {S.canonical(HW, r, autos) for r in rots}
nbrkey = lambda r: frozenset((v, a, b) for v, s in r.items() for a, b in s.items())  # noqa: E731
orbit_aut = set()
r0 = rots[0]
for a in autos:
    # image of r0 under the automorphism a, as a successor map on edge indices of HW
    eidx = {frozenset(e): i for i, e in enumerate(HW)}
    img = {}
    for v, s in r0.items():
        img[a[v]] = {eidx[frozenset((a[HW[e][0]], a[HW[e][1]]))]: eidx[frozenset((a[HW[f][0]], a[HW[f][1]]))] for e, f in s.items()}
    orbit_aut.add(nbrkey(img))
d3["torus rotation systems"] = len(mins)
d3["orbits under automorphisms and mirroring"] = len(orbit_all)
d3["automorphisms; images of one map without mirroring (8 = chiral)"] = (len(autos), len(orbit_aut))
fs = S.faces(HW, rots[0])
d3["face lengths"] = sorted(len(f) for f in fs)
fv = [set(t for e, t in f) | set(S.head(HW, e, t) for e, t in f) for f in fs]
d3["every two faces share exactly one edge (dual K7)"] = all(
    sum(1 for e in range(len(HW)) if any(ee == e for ee, t in fs[i]) and any(ee == e for ee, t in fs[j])) == 1
    for i, j in itertools.combinations(range(7), 2))
triples = {}
for kind in ('P', 'L'):
    trip = [frozenset(k for k in range(7) if v in fv[k]) for v in S.vertices(HW) if v[0] == kind]
    pairs = collections.Counter(p for t in trip for p in itertools.combinations(sorted(t), 2))
    triples[kind] = all(len(t) == 3 for t in trip) and len(pairs) == 21 and set(pairs.values()) == {1}
d3["faces around points form a Fano plane; faces around lines form a Fano plane"] = (triples['P'], triples['L'])
ok3 = d3["girth"] == 6 and d3["genus"] == 1 and d3["genus after deleting a vertex (every vertex)"] == [1] and len(mins) == 16 and \
    len(orbit_all) == 1 and len(orbit_aut) == 8 and d3["face lengths"] == [6] * 7 and d3["every two faces share exactly one edge (dual K7)"] \
    and triples['P'] and triples['L']
report("3 the Heawood graph: genus 1, rigid, a unique chiral torus map whose dual is K7 with two Fano colour classes", ok3, d3)

# ---------------------------------------------------------------- 4 the splice lemma on examples
d4 = {}
ok4 = True
Rs = {"K3,3": K33, "Petersen": PET, "cube": CUBE, "Heawood": HW, "Moebius-Kantor": S.from_nx(nx.LCF_graph(16, [5, -5], 8)),
      "Pappus": S.from_nx(nx.pappus_graph()), "Desargues": S.from_nx(nx.desargues_graph())}
for name, R in Rs.items():
    gR = S.genus(R)
    gs = [S.genus(S.splice(HW, HW[0][0], R, R[0][0], perm)) for perm in ((0, 1, 2), (1, 0, 2))]
    d4[name] = {"genus(R)": gR, "genus of the two splices": gs}
    ok4 &= gs == [gR + 1, gR + 1]
kk = S.genus(S.splice(K33, 0, K33, 0))
d4["K3,3 spliced with K3,3 (genus 1 each): genus"] = kk
d4["K3,3 minus a vertex: genus"] = S.genus_reduced([e for e in K33 if 0 not in e])
ok4 &= kk == 1 and d4["K3,3 minus a vertex: genus"] == 0
report("4 Heawood atoms add exactly one handle to any graph; without rigidity additivity fails (K3,3)", ok4, d4)

# ---------------------------------------------------------------- 5 the minimum-genus embeddings of the 13-point space
d5 = {}
H13 = T.point_splice(T.FANO, 0, T.FANO, T.FANO[0])
G13 = S.from_nx(M.bipartite(H13))
X = M.find_tight_cut(M.multigraph(H13))
Y = set(X)
mins13 = S.min_genus_rotations(G13, 2)
standard, profiles = 0, collections.Counter()
for b in mins13:
    rot = S.rotation(G13, b)
    c, tau, pi = S.cut_data(G13, rot, Y)
    if tau in S.CYCLES3 and pi == S.inverse(tau):
        g1 = S.genus_of(*S.contract_side(G13, rot, Y, c, S.inverse(tau), 'X'))
        g2 = S.genus_of(*S.contract_side(G13, rot, set(S.vertices(G13)) - Y, c, tau, 'Z'))
        standard += (g1, g2) == (1, 1)
    profiles[tuple(sorted(len(f) for f in S.faces(G13, rot)))] += 1
d5["minimum-genus rotation systems"] = len(mins13)
d5["standard connected sums with Heawood maps on both sides"] = standard
d5["face profiles"] = {str(k): v for k, v in profiles.items()}
ok5 = len(mins13) == 128 and standard == 128 and list(profiles) == [tuple([6] * 8 + [10] * 3)]
report("5 every minimum-genus embedding of the 13-point space is a connected sum of two Heawood maps (128 = 16 * 16 / 2)", ok5, d5)

# ---------------------------------------------------------------- 6 the genus formula on examples
d6 = {}
ok6 = True
F7 = T.FANO
C4 = [('c', j) for j in range(4)]
TRI = M.trisum([M.cube_on(C4, 'a'), M.cube_on(C4, 'b'), M.cube_on(C4, 'd')], C4, [(C4[j], C4[(j + 1) % 4]) for j in range(4)])
examples = {"Fano (7)": F7, "Fano splice (13)": H13, "Fano composition (19)": T.point_splice(H13, 0, F7, F7[0]),
            "3-cycle of blocks (21)": M.decorate([(0, 1, 1), (0, 0, 2), (1, 2, 2)], []),
            "tripod core (22)": M.decorate([(0, 1, 1), (0, 2, 2), (0, 3, 3), (1, 2, 3)], []),
            "twisted cube (43)": M.decorate(M.K4, M.kasteleyn_signing(M.K4))}
for name, H in examples.items():
    br = M.decompose(M.multigraph(H))
    kinds = collections.Counter(M.brace_type(b)[0] for b in br)
    h = kinds.get('heawood', 0)
    G = S.from_nx(M.bipartite(H))
    t1 = time.time()
    g = S.genus(G, lo=max(0, h - 1))
    d6[name] = {"braces": dict(kinds), "genus": g, "seconds": round(time.time() - t1, 1)}
    ok6 &= g == h and set(kinds) <= {'heawood', 'doubled square', 'planar'}
tri = S.from_nx(TRI)
d6["trisum of three cubes: genus, genus after deleting a vertex"] = (S.genus(tri), sorted({S.genus_reduced([e for e in tri if v not in e])
                                                                                           for v in S.vertices(tri)}))
ok6 &= d6["trisum of three cubes: genus, genus after deleting a vertex"] == (1, [1])
DS = [('p', 'l'), ('p', 'l'), ('q', 'm'), ('q', 'm'), ('p', 'm'), ('q', 'l')]
d6["doubled square: planar rotation systems (of 16)"] = sum(1 for bits in itertools.product((0, 1), repeat=4)
                                                             if S.genus_of(DS, S.rotation(DS, dict(zip('pqlm', bits)))) == 0)
ok6 &= d6["doubled square: planar rotation systems (of 16)"] == 4
report("6 genus = number of Heawood braces on the examples; trisum glue keeps its genus under vertex deletion", ok6, d6)

# ---------------------------------------------------------------- 7 controls
ctrl = {}
r13 = S.random_rotation(G13, random.Random(7))
ctrl["a random rotation system of the 13-point space has genus at least 2"] = S.genus_of(G13, r13) >= 2
mr = S.rotation(G13, mins13[0])
ctrl["the mirror of a minimum-genus embedding is minimum-genus and changes every rotation"] = \
    S.genus_of(G13, S.mirror(mr)) == 2 and all(S.mirror(mr)[v] != mr[v] for v in mr)
ctrl["additivity fails without rigidity (K3,3 spliced with K3,3 has genus 1, not 2)"] = kk == 1
ctrl["a planar graph (the cube) has genus 0 by SAT"] = S.genus(CUBE) == 0
report("7 controls fire", all(ctrl.values()), ctrl)

out["ok"] = ok_all
out["seconds"] = round(time.time() - T0, 1)
print("ALL OK" if ok_all else "SOME CHECK FAILED", out["seconds"], "s")
if "--write" in sys.argv:
    json.dump({"schema_version": 1, "artifact_id": "THREEFOLD-SURFACES-20261030-001A-P001", "status": "Proved" if ok_all else "Failed",
               "checks": out}, open(os.path.join(HERE, "result.json"), "w"), indent=1, default=str)
sys.exit(0 if ok_all else 1)
