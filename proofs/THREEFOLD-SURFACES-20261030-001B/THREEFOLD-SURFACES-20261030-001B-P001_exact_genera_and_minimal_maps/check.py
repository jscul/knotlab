"""Checks for THREEFOLD-SURFACES-20261030-001B-P001 (exact genera and minimal maps by SAT).

  0 dependency artifacts bound by the hashes recorded in manifest.json
  1 every three-fold space up to 22 points (the 8 classes of THREEFOLD-GRAMMAR-20261030-001B) and every twisted one (24 classes): the
    exact orientable genus of the incidence graph equals the sum of its braces' genera, i.e. the number of Heawood braces, plus one for
    the twisted 22-point class whose glue is the trisum of three cubes (rigid, genus 1)
  2 larger spaces: Fano compositions of 4 and 5 planes (25, 31), cycles of 5 and 7 Fano blocks (35, 49), the twisted cube (43), the
    hexagonal prism (45) and truncated octahedron (90) as glue, and the 35-point space whose glue is the trisum of three cubes: genus =
    number of Heawood braces (+1 for the trisum)
  3 minimal maps up to 19 points: the number of minimum-genus rotation systems is 16, 128 and 1024 (the formula of ticket A); every one is a
    standard connected sum at every tight cut; orbits under automorphisms and mirroring and face profiles reported
  4 the splice lemma beyond the Heawood graph: the trisum of three cubes and the Petersen graph keep their genus under vertex deletion and
    splice additively; K3,3 does not and K3,3 spliced with K3,3 loses a handle, while one rigid side suffices
  5 controls that must fire
Run: .venv/bin/python -B check.py [--write]   (python-sat, networkx; about 12 minutes)"""
import collections, hashlib, itertools, json, os, random, sys, time
import networkx as nx

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
TA = os.path.join(ROOT, "proofs/THREEFOLD-SPACES-20261030-001A/THREEFOLD-SPACES-20261030-001A-P001_three_fold_spaces_are_built_from_the_fano_plane")
GA = os.path.join(ROOT, "proofs/THREEFOLD-GRAMMAR-20261030-001A/THREEFOLD-GRAMMAR-20261030-001A-P001_fano_leaves_and_planar_glue")
GB = os.path.join(ROOT, "proofs/THREEFOLD-GRAMMAR-20261030-001B/THREEFOLD-GRAMMAR-20261030-001B-P001_census_with_doubled_incidences")
SA = os.path.join(ROOT, "proofs/THREEFOLD-SURFACES-20261030-001A/THREEFOLD-SURFACES-20261030-001A-P001_fano_atoms_are_handles")
for p in (TA, GA, GB, SA, HERE):
    sys.path.insert(0, p)
import threefold_lib as T  # noqa: E402
import grammar_lib as M  # noqa: E402
import census_lib as C  # noqa: E402
import surface_lib as S  # noqa: E402

T0 = time.time()
out, ok_all = {}, True


def report(key, ok, detail):
    global ok_all
    out[key] = {"ok": bool(ok), "detail": detail}
    ok_all &= bool(ok)
    print(("PASS " if ok else "FAIL ") + key + ": " + json.dumps(detail, default=str)[:2500], flush=True)


def heawood_braces(H):
    return sum(1 for b in M.decompose(M.multigraph(H)) if M.brace_type(b)[0] == 'heawood')


def brace_genera(H):
    """the braces' genera (Heawood 1, doubled squares and planar braces 0, any other brace by SAT) and whether every non-planar brace
    keeps its genus when any vertex is deleted (the hypothesis of ticket A's genus formula)"""
    total, rigid, kinds = 0, True, collections.Counter()
    for b in M.decompose(M.multigraph(H)):
        t = M.brace_type(b)[0]
        kinds[t] += 1
        if t == 'heawood':
            total += 1
        elif t == 'other':
            edges = [(u, w) for u in b for w in b[u] for _ in range(b[u][w]) if str(u) < str(w)]
            gb = S.genus(edges)
            total += gb
            rigid &= all(S.genus_reduced([e for e in edges if v not in e]) == gb for v in b)
    return total, rigid, dict(kinds)


def exact_genus(H, lo):
    return S.genus(S.from_nx(M.bipartite(H)), lo=max(0, lo))


# ---------------------------------------------------------------- 0
man = json.load(open(os.path.join(HERE, "manifest.json")))
mism = {r: dg for r, dg in man["parent_bindings"].items()
        if hashlib.sha256(open(os.path.join(ROOT, r), "rb").read()).hexdigest() != dg}
report("0 dependency artifacts bound by hash", not mism, {"parents": len(man["parent_bindings"]), "mismatched": mism})

# ---------------------------------------------------------------- 1 every space up to 22 points
spaces = {False: [("Fano (7)", T.FANO)], True: []}
for tw in (False, True):
    byN = collections.defaultdict(list)
    for n in range(1, 11):
        for H, c in C.census(n, tw):
            for L in range(2, 2 * n + 1):
                if n + 6 * L > 22:
                    break
                for Sset in C.covers(H, L):
                    pts, lns = [p for k, p in Sset if k == 'P'], [i for k, i in Sset if k == 'L']
                    byN[n + 6 * L].append(C.decorate_pieces(H, pts, lns, (0, 0)) if tw else (C.decorate_pieces(H, pts, lns), None))
    for N in sorted(byN):
        cls = C.classify([D for D, t in byN[N]], [t for D, t in byN[N]] if tw else None)
        for k, (H, cnt, t) in enumerate(cls):
            spaces[tw].append((f"{N}-point class {k}", H))
d1 = {}
ok1 = True
for tw in (False, True):
    rows = []
    for name, H in spaces[tw]:
        h = heawood_braces(H)
        pred, rigid, kinds = brace_genera(H)
        g = exact_genus(H, pred - 1)
        rows.append((name, h, pred, g) if pred == h else (name, h, pred, g, kinds))
        ok1 &= g == pred and rigid
    d1["twisted" if tw else "untwisted"] = {"classes": len(rows), "genus = sum of the braces' genera": all(r[3] == r[2] for r in rows),
                                             "genus = number of Heawood braces": all(r[3] == r[1] for r in rows),
                                             "(name, Heawood braces, sum of brace genera, genus[, braces when non-planar glue])": rows}
ok1 &= len(spaces[False]) == 8 and len(spaces[True]) == 24
report("1 every space up to 22 points (8 untwisted, 24 twisted classes): genus = sum of the braces' genera", ok1 and d1["untwisted"]["genus = number of Heawood braces"], d1)

# ---------------------------------------------------------------- 2 larger spaces
d2 = {}
ok2 = True
F7 = T.FANO
big = {}
comp = T.point_splice(F7, 0, F7, F7[0])
for k in range(3, 6):
    comp = T.point_splice(comp, 0, F7, F7[0])
    if k >= 4:
        big[f"Fano composition of {k} planes ({T.npoints(comp)})"] = (comp, 0)
big["5-cycle of Fano blocks (35)"] = (M.decorate([(0, 1, 1), (1, 2, 2), (2, 3, 3), (3, 4, 4), (4, 0, 0)], []), 0)
big["7-cycle of Fano blocks (49)"] = (M.decorate([(i, (i + 1) % 7, (i + 1) % 7) for i in range(7)], []), 0)
big["twisted cube (43)"] = (M.decorate(M.K4, M.kasteleyn_signing(M.K4)), 0)
for glue in ('hexagonal prism', 'truncated octahedron'):
    P = M.cubic_planar_bipartite(glue)
    D = M.decorate(P, M.kasteleyn_signing(P))
    big[f"{glue} as glue ({T.npoints(D)})"] = (D, 0)
CORE35 = [(0, 1, 2), (0, 1, 3), (0, 4, 5), (1, 6, 7), (2, 6, 8), (2, 7, 9), (3, 4, 6), (3, 5, 7), (4, 8, 8), (5, 9, 9)]
big["trisum of three cubes as glue (35)"] = (M.decorate(CORE35, [(0, 0)]), 1)
for name, (H, extra) in big.items():
    kinds = collections.Counter(M.brace_type(b)[0] for b in M.decompose(M.multigraph(H)))
    h = kinds.get('heawood', 0)
    t1 = time.time()
    g = exact_genus(H, h + extra - 1)
    d2[name] = {"vertices": 2 * T.npoints(H), "braces": dict(kinds), "genus": g, "predicted": h + extra, "seconds": round(time.time() - t1, 1)}
    ok2 &= g == h + extra and T.is_cubic(H) and not T.colourable_sat(H)
report("2 larger spaces: genus = number of Heawood braces (+1 for the trisum glue)", ok2, d2)

# ---------------------------------------------------------------- 3 minimal maps up to 19 points
d3 = {}
ok3 = True
for name, H in spaces[False][:6]:
    G = S.from_nx(M.bipartite(H))
    h = heawood_braces(H)
    mins = S.min_genus_rotations(G, h)
    cuts = [set(('L', i) for i in X) | set(('P', p) for p in P) for X, P in T.tight_cuts(H)]
    standard = 0
    profiles = collections.Counter()
    rots = [S.rotation(G, b) for b in mins]
    for rot in rots:
        good = True
        for Y in cuts:
            c, tau, pi = S.cut_data(G, rot, Y)
            good &= tau in S.CYCLES3 and pi == S.inverse(tau)
        standard += good
        profiles[tuple(sorted(len(f) for f in S.faces(G, rot)))] += 1
    autos = S.automorphisms(G)
    orbits = collections.Counter(S.canonical(G, rot, autos) for rot in rots)
    predicted = 16 ** h // 2 ** len(cuts)
    d3[name] = {"atoms": h, "tight cuts": len(cuts), "minimum-genus rotation systems": len(mins), "predicted": predicted,
                "standard at every cut": standard, "automorphisms": len(autos), "orbits": len(orbits),
                "orbit sizes": sorted(orbits.values()), "face profiles": {str(k): v for k, v in profiles.items()}}
    ok3 &= len(mins) == predicted and standard == len(mins) and len(cuts) == h - 1
d3["predicted by ticket A, not enumerated: 21 points 16^3 4^2 / 2^4 = 4096; 22 points 16^3 4^3 / 2^5 = 8192"] = True
report("3 minimal maps up to 19 points: 16, 128, 1024 rotation systems, all standard connected sums", ok3, d3)

# ---------------------------------------------------------------- 4 the splice lemma beyond the Heawood graph
d4 = {}
C4 = [('c', j) for j in range(4)]
TRI = S.from_nx(M.trisum([M.cube_on(C4, 'a'), M.cube_on(C4, 'b'), M.cube_on(C4, 'd')], C4, [(C4[j], C4[(j + 1) % 4]) for j in range(4)]))
PET = S.from_nx(nx.petersen_graph())
K33 = S.from_nx(nx.complete_bipartite_graph(3, 3))
CUBE = S.from_nx(nx.convert_node_labels_to_integers(nx.hypercube_graph(3)))
HW = S.from_nx(M.bipartite(T.FANO))
pieces = {"trisum of three cubes": TRI, "Petersen": PET, "K3,3": K33}
for name, A in pieces.items():
    x = A[0][0]
    d4[name] = {"genus": S.genus(A), "genus minus the splice vertex": S.genus_reduced([e for e in A if x not in e])}
pairs = {"trisum + cube": (TRI, CUBE), "trisum + Heawood": (TRI, HW), "trisum + K3,3": (TRI, K33), "Petersen + Petersen": (PET, PET),
         "K3,3 + Petersen": (K33, PET), "K3,3 + K3,3": (K33, K33)}
for name, (A, R) in pairs.items():
    d4[name] = {"genera": (S.genus(A), S.genus(R)), "splices": [S.genus(S.splice(A, A[0][0], R, R[0][0], p)) for p in ((0, 1, 2), (1, 0, 2))]}
ok4 = d4["trisum of three cubes"] == {"genus": 1, "genus minus the splice vertex": 1} and d4["Petersen"] == {"genus": 1, "genus minus the splice vertex": 1} \
    and d4["K3,3"] == {"genus": 1, "genus minus the splice vertex": 0}
for name in ("trisum + cube", "trisum + Heawood", "trisum + K3,3", "Petersen + Petersen", "K3,3 + Petersen"):
    ok4 &= d4[name]["splices"] == [sum(d4[name]["genera"])] * 2
ok4 &= d4["K3,3 + K3,3"]["splices"] == [1, 1]
report("4 additivity holds when one side keeps its genus under vertex deletion, and fails for K3,3 with K3,3", ok4, d4)

# ---------------------------------------------------------------- 5 controls
ctrl = {}
H13 = spaces[False][1][1]
G13 = S.from_nx(M.bipartite(H13))
ctrl["the SAT bound one below the genus is unsatisfiable (13-point space, genus 1 excluded)"] = not S.faces_at_least(G13, len(G13) - len(S.vertices(G13)) + 2 - 2)
ctrl["a random rotation system of the 19-point composition has genus above 3"] = \
    S.genus_of(S.from_nx(M.bipartite(spaces[False][2][1])), S.random_rotation(S.from_nx(M.bipartite(spaces[False][2][1])), random.Random(3))) > 3
ctrl["the cube (planar) has genus 0 and the Heawood graph 1"] = S.genus(CUBE) == 0 and S.genus(HW) == 1
report("5 controls fire", all(ctrl.values()), ctrl)

out["ok"] = ok_all
out["seconds"] = round(time.time() - T0, 1)
print("ALL OK" if ok_all else "SOME CHECK FAILED", out["seconds"], "s")
if "--write" in sys.argv:
    json.dump({"schema_version": 1, "artifact_id": "THREEFOLD-SURFACES-20261030-001B-P001", "status": "Proved" if ok_all else "Failed",
               "checks": out}, open(os.path.join(HERE, "result.json"), "w"), indent=1, default=str)
sys.exit(0 if ok_all else 1)
