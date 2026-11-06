"""Checks for THREEFOLD-SPIN-20261030-001A-P001 (Kasteleyn faces and even spin structures).

  0 dependency artifacts bound by the hashes recorded in manifest.json
  1 base pieces: every minimal map of the Heawood graph (trivial signing), the doubled square (odd signings) and three planar braces
    (Kasteleyn signings) satisfies the face condition with every vertex on three distinct faces
  2 the splice lemma on spaces: on minimal maps of the 13-, 19-, 21- and 22-point spaces every tight cut is crossed by exactly three faces,
    each using two of its edges, every vertex lies on three distinct faces, and every face has length 2 mod 4
  3 the Fano space: on all 16 maps the form is well defined on all 256 cycle-space elements, has Arf invariant 0 for every one of the 24
    perfect matchings, vanishes on all matching differences, and the matchings fall 8, 8, 8 into its three zero classes
  4 the 13-point space: on all 128 maps Arf 0 and vanishing on all 192 matching differences, which realize the 9 classes even on both handles
  5 genus one: the classes of single-cycle matching differences span H_1 of every Heawood map
  6 controls that must fire
Run: .venv/bin/python -B check.py [--write]   (networkx, python-sat; about fifteen seconds)"""
import collections, hashlib, itertools, json, os, random, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
TA = os.path.join(ROOT, "proofs/THREEFOLD-SPACES-20261030-001A/THREEFOLD-SPACES-20261030-001A-P001_three_fold_spaces_are_built_from_the_fano_plane")
GA = os.path.join(ROOT, "proofs/THREEFOLD-GRAMMAR-20261030-001A/THREEFOLD-GRAMMAR-20261030-001A-P001_fano_leaves_and_planar_glue")
SA = os.path.join(ROOT, "proofs/THREEFOLD-SURFACES-20261030-001A/THREEFOLD-SURFACES-20261030-001A-P001_fano_atoms_are_handles")
for p in (TA, GA, SA, HERE):
    sys.path.insert(0, p)
import threefold_lib as T  # noqa: E402
import grammar_lib as M  # noqa: E402
import surface_lib as SL  # noqa: E402
import spin_lib as S  # noqa: E402
from pysat.solvers import Solver  # noqa: E402

T0 = time.time()
out, ok_all = {}, True


def report(key, ok, detail):
    global ok_all
    out[key] = {"ok": bool(ok), "detail": detail}
    ok_all &= bool(ok)
    print(("PASS " if ok else "FAIL ") + key + ": " + json.dumps(detail, default=str)[:2500], flush=True)


def minimal_maps(edges, g, limit=None):
    """rotation systems (bit maps) of genus g, all of them or the first `limit` found by SAT"""
    if limit is None:
        return SL.min_genus_rotations(edges, g)
    V, E = len(SL.vertices(edges)), len(edges)
    cnf, r = SL._model(edges, E - V + 2 - 2 * g, fix_first=False)
    res = []
    with Solver(name='cadical153', bootstrap_with=cnf.clauses) as s:
        while len(res) < limit and s.solve():
            m = set(l for l in s.get_model() if l > 0)
            bits = {v: int(r(v) in m) for v in SL.vertices(edges)}
            res.append(bits)
            s.add_clause([-r(v) if bits[v] else r(v) for v in SL.vertices(edges)])
    return res


# ---------------------------------------------------------------- 0
man = json.load(open(os.path.join(HERE, "manifest.json")))
mism = {r: dg for r, dg in man["parent_bindings"].items()
        if hashlib.sha256(open(os.path.join(ROOT, r), "rb").read()).hexdigest() != dg}
report("0 dependency artifacts bound by hash", not mism, {"parents": len(man["parent_bindings"]), "mismatched": mism})

F7 = T.FANO
H13 = T.point_splice(F7, 0, F7, F7[0])
H19 = T.point_splice(H13, 0, F7, F7[0])

# ---------------------------------------------------------------- 1 base pieces
d1, ok1 = {}, True
E7 = S.graph_of(F7)
maps7 = SL.min_genus_rotations(E7, 1)
rows = collections.Counter()
for bits in maps7:
    rot = SL.rotation(E7, bits)
    fc = S.face_condition(E7, rot)
    rows[(tuple(sorted(collections.Counter(L for L, ok in fc).items())), all(ok for L, ok in fc), S.three_distinct_faces(E7, rot))] += 1
d1["Heawood graph, trivial signing: maps by (face lengths, Kasteleyn, three distinct faces)"] = {str(k): v for k, v in rows.items()}
ok1 &= len(maps7) == 16 and set(rows) == {(((6, 7),), True, True)}
DS = [(0, 1, 1), (0, 0, 1)]
Eds = S.graph_of(DS)
maps_ds = SL.min_genus_rotations(Eds, 0)
classes = [(0, 0), (0, 1), (1, 0), (1, 1)]
ds = collections.defaultdict(set)
for k in range(5):
    for cls in itertools.combinations(classes, k):
        neg = S.negated(Eds, cls)
        for bits in maps_ds:
            rot = SL.rotation(Eds, bits)
            ds[k].add(all(ok for L, ok in S.face_condition(Eds, rot, neg)) and S.three_distinct_faces(Eds, rot))
d1["doubled square: planar maps, and whether every one is Kasteleyn with three distinct faces, by number of negated classes"] = \
    {"planar maps": len(maps_ds), **{k: sorted(v) for k, v in ds.items()}}
ok1 &= len(maps_ds) > 0 and ds[1] == {True} and ds[3] == {True} and ds[0] == {False} and ds[2] == {False} and ds[4] == {False}
planar = {}
for name, P in [("cube", M.K4), ("hexagonal prism", M.cubic_planar_bipartite('hexagonal prism')),
                ("truncated octahedron", M.cubic_planar_bipartite('truncated octahedron'))]:
    Ep = S.graph_of(P)
    neg = S.negated(Ep, M.kasteleyn_signing(P))
    mp = SL.min_genus_rotations(Ep, 0)
    good = [all(ok for L, ok in S.face_condition(Ep, SL.rotation(Ep, b), neg)) and S.three_distinct_faces(Ep, SL.rotation(Ep, b)) for b in mp]
    planar[name] = {"planar maps": len(mp), "all Kasteleyn with three distinct faces": all(good)}
    ok1 &= len(mp) == 2 and all(good)
d1["planar braces with their Kasteleyn signings"] = planar
report("1 base pieces: Heawood, doubled square and planar braces are Kasteleyn on every minimal map", ok1, d1)

# ---------------------------------------------------------------- 2 the splice lemma on spaces
SPACES = {"13-point splice": (H13, 2, None), "19-point composition": (H19, 3, 256),
          "21-point 3-cycle of blocks": (M.decorate([(0, 1, 1), (0, 0, 2), (1, 2, 2)], []), 3, 64),
          "22-point tripod": (M.decorate([(0, 1, 1), (0, 2, 2), (0, 3, 3), (1, 2, 3)], []), 3, 64)}
d2, ok2 = {}, True
MAPS = {}
for name, (H, g, limit) in SPACES.items():
    E = S.graph_of(H)
    cuts = S.tight_cuts(E)
    maps = minimal_maps(E, g, limit)
    MAPS[name] = (E, maps)
    tally = collections.Counter()
    for bits in maps:
        rot = SL.rotation(E, bits)
        lens = collections.Counter(len(f) for f in SL.faces(E, rot))
        crossing = all(sorted(S.crossing_faces(E, rot, c)) == [2, 2, 2] for c in cuts)
        tally[(all(L % 4 == 2 for L in lens), S.three_distinct_faces(E, rot), crossing)] += 1
    d2[name] = {"genus": g, "tight cuts": len(cuts), "maps checked": len(maps),
                "maps by (faces 2 mod 4, three distinct faces, each cut crossed by three faces using two of its edges)": {str(k): v for k, v in tally.items()}}
    ok2 &= set(tally) == {(True, True, True)} and len(cuts) >= 1
ok2 &= len(MAPS["13-point splice"][1]) == 128
report("2 splice lemma: every tight cut crossed by three faces, three distinct faces everywhere, every face of length 2 mod 4", ok2, d2)

# ---------------------------------------------------------------- 3 the Fano space
d3, ok3 = {}, True
pms7 = S.perfect_matchings(E7)
fund7 = S.fundamental_cycles(E7)
all_elems = []
for coeffs in itertools.product((0, 1), repeat=len(fund7)):
    Z = 0
    for c, m in zip(coeffs, fund7):
        if c:
            Z ^= m
    all_elems.append(Z)
inc7 = SL.incident(E7)
tally = collections.Counter()
for bits in maps7:
    rot = SL.rotation(E7, bits)
    H1 = S.h1_basis(E7, rot)
    D0 = pms7[0]
    qv, ill = {}, 0
    for Z in all_elems:
        h, q = S.hclass(Z, H1), S.q_of(Z, E7, rot, frozenset(), D0, inc7)
        ill += h in qv and qv[h] != q
        qv.setdefault(h, q)
    arfs = {S.gauss_arf(S.form(E7, rot, frozenset(), D, H1).values(), 1) for D in pms7}
    on_diff = {qv[S.hclass(D ^ D0, H1)] for D in pms7}
    split = collections.Counter(S.hclass(D ^ D0, H1) for D in pms7)
    zeros = sorted(h for h, q in qv.items() if q == 0)
    tally[(ill, tuple(sorted(arfs, key=str)), tuple(on_diff), tuple(sorted(split.values())), sorted(split) == zeros)] += 1
d3["maps by (ill-defined evaluations, Arf over all 24 matchings, q on differences, class sizes, classes = zeros of q)"] = \
    {str(k): v for k, v in tally.items()}
ok3 &= set(tally) == {(0, (0,), (0,), (8, 8, 8), True)} and len(pms7) == 24
report("3 the Fano space: Arf 0 for every matching, matchings split 8, 8, 8 over the three even classes", ok3, d3)

# ---------------------------------------------------------------- 4 the 13-point space
d4, ok4 = {}, True
E13, maps13 = MAPS["13-point splice"]
pms13 = S.perfect_matchings(E13)
fund13 = S.fundamental_cycles(E13)
inc13 = SL.incident(E13)
tally = collections.Counter()
for k, bits in enumerate(maps13):
    rot = SL.rotation(E13, bits)
    H1 = S.h1_basis(E13, rot)
    D0 = pms13[0]
    reps = S.class_representatives(E13, H1, fund13)
    qv = S.form(E13, rot, frozenset(), D0, H1, reps)
    arf = S.gauss_arf(qv.values(), 2)
    on_diff = {qv[S.hclass(D ^ D0, H1)] for D in pms13}
    realized = {S.hclass(D ^ D0, H1) for D in pms13}
    zeros = {h for h, q in qv.items() if q == 0}
    ill = 0
    if k < 4:                                       # exhaustive well-definedness on four maps
        for coeffs in itertools.product((0, 1), repeat=len(fund13)):
            Z = 0
            for c, m in zip(coeffs, fund13):
                if c:
                    Z ^= m
            ill += S.q_of(Z, E13, rot, frozenset(), D0, inc13) != qv[S.hclass(Z, H1)]
    tally[(arf, tuple(on_diff), len(realized), len(zeros), realized < zeros, ill)] += 1
d4["maps by (Arf, q on differences, classes realized, zeros of q, realized inside zeros, ill-defined evaluations)"] = \
    {str(k): v for k, v in tally.items()}
ok4 &= set(tally) == {(0, (0,), 9, 10, True, 0)} and len(pms13) == 192 and sum(tally.values()) == 128
report("4 the 13-point space: Arf 0, the form vanishes on all matching differences, 9 of the 10 even classes realized", ok4, d4)

# ---------------------------------------------------------------- 5 genus one: nice cycles span
d5, ok5 = {}, True
spans = collections.Counter()
for bits in maps7:
    rot = SL.rotation(E7, bits)
    H1 = S.h1_basis(E7, rot)
    basis = []
    for D in pms7:
        Z = D ^ pms7[0]
        if Z and len(S.cycles_of(Z, E7)) == 1:
            v = int("".join(map(str, S.hclass(Z, H1))), 2)
            S.add_to_basis(v, basis)
    spans[len(basis)] += 1
d5["rank of the classes of single nice cycles, by map"] = dict(spans)
ok5 &= dict(spans) == {2: 16}
report("5 on every Heawood map the classes of single nice cycles span H_1", ok5, d5)

# ---------------------------------------------------------------- 6 controls
ctrl = {}
rnd = random.Random(20261030)
fails = 0
trials = 0
for _ in range(200):
    rot = SL.random_rotation(E7, rnd)
    if SL.genus_of(E7, rot) == 1:
        continue
    trials += 1
    fails += not all(ok for L, ok in S.face_condition(E7, rot))
ctrl["the face condition is not automatic: some non-minimal maps of the Heawood graph have a face of length 0 mod 4"] = trials > 100 and fails > 0
ctrl["fraction of 200 random non-minimal maps failing it"] = round(fails / max(trials, 1), 3)
rot = SL.rotation(E7, maps7[0])
H1 = S.h1_basis(E7, rot)
bad = frozenset({0})
ill = 0
qv = {}
for Z in all_elems:
    h, q = S.hclass(Z, H1), S.q_of(Z, E7, rot, bad, pms7[0], inc7)
    ill += h in qv and qv[h] != q
    qv.setdefault(h, q)
ctrl["one flipped sign breaks the face condition and makes the form ill-defined"] = \
    not all(ok for L, ok in S.face_condition(E7, rot, bad)) and ill > 0
twisted = []
for c in (H1[0], H1[1], H1[0] ^ H1[1]):
    neg = frozenset(e for e in range(len(E7)) if c >> e & 1)
    assert all(ok for L, ok in S.face_condition(E7, rot, neg))
    twisted.append(S.gauss_arf(S.form(E7, rot, neg, pms7[0], H1).values(), 1))
ctrl["the three other Kasteleyn classes of a Heawood map include exactly one odd spin structure"] = sorted(twisted) == [0, 0, 1]
ctrl["Arf invariants of the three twisted classes"] = twisted
report("6 controls fire", all(v for k, v in ctrl.items() if isinstance(v, bool)), ctrl)

out["ok"] = ok_all
out["seconds"] = round(time.time() - T0, 1)
print("ALL OK" if ok_all else "SOME CHECK FAILED", out["seconds"], "s")
if "--write" in sys.argv:
    json.dump({"schema_version": 1, "artifact_id": "THREEFOLD-SPIN-20261030-001A-P001", "status": "Proved" if ok_all else "Failed",
               "checks": out}, open(os.path.join(HERE, "result.json"), "w"), indent=1, default=str)
sys.exit(0 if ok_all else 1)
