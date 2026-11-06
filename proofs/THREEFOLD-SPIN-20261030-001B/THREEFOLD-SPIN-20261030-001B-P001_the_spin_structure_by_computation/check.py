"""Checks for THREEFOLD-SPIN-20261030-001B-P001 (the spin structure by computation).

  0 dependency artifacts bound by the hashes recorded in manifest.json
  1 every three-fold space up to 22 points: on its minimal maps (all, or the first found by SAT) faces of length 2 mod 4, three distinct
    faces at every vertex, Arf invariant 0, the form vanishing on all matching differences, which realize exactly 3^h classes
  2 the 35-point space with trisum glue and the 43-point twisted cube: the same on sampled maps and sampled matchings
  3 trisums of prisms: rigid of genus one; on all minimal maps the Pfaffian signing is Kasteleyn, Arf 0, three even classes realized
  4 the Heawood torus: Kasteleyn determinants 24, 8, 8, 8 (in absolute value); the Cimasoni-Reshetikhin sum gives 2 x 24
  5 non-minimal maps (seeded random rotations): the same signs are sometimes Kasteleyn with an odd spin structure, only from genus 3 on
  6 controls that must fire
Run: .venv/bin/python -B check.py [--write]   (networkx, python-sat, sympy; a few minutes)"""
import collections, hashlib, itertools, json, os, random, sys, time
import sympy

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
P = lambda r: os.path.join(ROOT, "proofs", r)  # noqa: E731
for p in (P("THREEFOLD-SPACES-20261030-001A/THREEFOLD-SPACES-20261030-001A-P001_three_fold_spaces_are_built_from_the_fano_plane"),
          P("THREEFOLD-GRAMMAR-20261030-001A/THREEFOLD-GRAMMAR-20261030-001A-P001_fano_leaves_and_planar_glue"),
          P("THREEFOLD-GRAMMAR-20261030-001B/THREEFOLD-GRAMMAR-20261030-001B-P001_census_with_doubled_incidences"),
          P("THREEFOLD-SURFACES-20261030-001A/THREEFOLD-SURFACES-20261030-001A-P001_fano_atoms_are_handles"),
          P("THREEFOLD-AMPLITUDE-20261030-001B/THREEFOLD-AMPLITUDE-20261030-001B-P001_the_amplitude_by_computation"),
          P("THREEFOLD-SPIN-20261030-001A/THREEFOLD-SPIN-20261030-001A-P001_kasteleyn_faces_and_even_spin_structures")):
    sys.path.insert(0, p)
import threefold_lib as T  # noqa: E402
import grammar_lib as M  # noqa: E402
import census_lib as C  # noqa: E402
import surface_lib as SL  # noqa: E402
import computation_lib as CL  # noqa: E402
import spin_lib as S  # noqa: E402
from pysat.solvers import Solver  # noqa: E402

T0 = time.time()
out, ok_all = {}, True


def report(key, ok, detail):
    global ok_all
    out[key] = {"ok": bool(ok), "detail": detail}
    ok_all &= bool(ok)
    print(("PASS " if ok else "FAIL ") + key + ": " + json.dumps(detail, default=str)[:3000], flush=True)


def minimal_maps(edges, g, limit=None):
    V, E = len(SL.vertices(edges)), len(edges)
    cnf, r = SL._model(edges, E - V + 2 - 2 * g, fix_first=False)
    res = []
    with Solver(name='cadical153', bootstrap_with=cnf.clauses) as s:
        while (limit is None or len(res) < limit) and s.solve():
            m = set(l for l in s.get_model() if l > 0)
            bits = {v: int(r(v) in m) for v in SL.vertices(edges)}
            res.append(bits)
            s.add_clause([-r(v) if bits[v] else r(v) for v in SL.vertices(edges)])
    return res


def some_perfect_matchings(edges, cap, rnd):
    """up to `cap` perfect matchings, by depth-first search with shuffled edge orders"""
    inc = SL.incident(edges)
    lines = sorted([v for v in inc if v[0] == 'L'], key=str)
    order = {l: rnd.sample(inc[l], len(inc[l])) for l in lines}
    res = []

    def rec(k, used, chosen):
        if len(res) >= cap:
            return
        if k == len(lines):
            res.append(chosen)
            return
        for e in order[lines[k]]:
            p = SL.head(edges, e, lines[k])
            if p not in used:
                rec(k + 1, used | {p}, chosen | (1 << e))
    rec(0, frozenset(), 0)
    return res


def arf_fast(edges, rot, neg, D, H1, fund, inc):
    """Arf invariant from q on a basis of H_1 and on pairwise sums (which give the intersection form), by symplectic reduction"""
    n = len(H1)
    basis = []
    for m in fund:
        v, mm = int("".join(map(str, S.hclass(m, H1))), 2), m
        for bv, bm in basis:
            if v ^ bv < v:
                v, mm = v ^ bv, mm ^ bm
        if v:
            basis.append((v, mm))
            basis.sort(reverse=True)

    def rep(t):
        mm = 0
        for bv, bm in basis:
            if t ^ bv < t:
                t, mm = t ^ bv, mm ^ bm
        assert t == 0
        return mm
    units = [1 << (n - 1 - i) for i in range(n)]
    qi = [S.q_of(rep(u), edges, rot, neg, D, inc) for u in units]
    B = [[0] * n for _ in range(n)]
    for i, j in itertools.combinations(range(n), 2):
        B[i][j] = B[j][i] = (S.q_of(rep(units[i] ^ units[j]), edges, rot, neg, D, inc) + qi[i] + qi[j]) % 2

    def qv(x):
        return (sum(q for q, a in zip(qi, x) if a) + sum(B[i][j] for i, j in itertools.combinations(range(n), 2) if x[i] and x[j])) % 2

    def bil(x, y):
        return sum(B[i][j] for i in range(n) if x[i] for j in range(n) if y[j]) % 2
    vecs = [[int(k == i) for k in range(n)] for i in range(n)]
    arf = 0
    while vecs:
        a = vecs.pop(0)
        k = next((k for k, v in enumerate(vecs) if bil(a, v)), None)
        if k is None:
            return 'degenerate'
        b = vecs.pop(k)
        arf ^= qv(a) & qv(b)
        vecs = [[(x + bil(v, b) * ya + bil(v, a) * yb) % 2 for x, ya, yb in zip(v, a, b)] for v in vecs]
    return arf


def study(edges, maps, pms, neg=frozenset()):
    """per map: (faces ok, three distinct faces, Arf, form vanishes on differences, number of classes realized, number of zeros of q)"""
    fund = S.fundamental_cycles(edges)
    rows = collections.Counter()
    for bits in maps:
        rot = SL.rotation(edges, bits)
        g = SL.genus_of(edges, rot)
        H1 = S.h1_basis(edges, rot)
        reps = S.class_representatives(edges, H1, fund)
        qv = S.form(edges, rot, neg, pms[0], H1, reps)
        realized = {S.hclass(D ^ pms[0], H1) for D in pms}
        rows[(all(ok for L, ok in S.face_condition(edges, rot, neg)), S.three_distinct_faces(edges, rot), S.gauss_arf(qv.values(), g),
              all(qv[h] == 0 for h in realized), len(realized), sum(1 for v in qv.values() if v == 0))] += 1
    return rows


# ---------------------------------------------------------------- 0
man = json.load(open(os.path.join(HERE, "manifest.json")))
mism = {r: dg for r, dg in man["parent_bindings"].items()
        if hashlib.sha256(open(os.path.join(ROOT, r), "rb").read()).hexdigest() != dg}
report("0 dependency artifacts bound by hash", not mism, {"parents": len(man["parent_bindings"]), "mismatched": mism})

# ---------------------------------------------------------------- 1 every space up to 22 points
F7 = T.FANO
spaces = [("Fano (7)", F7, 1, None), ("13-point splice", T.point_splice(F7, 0, F7, F7[0]), 2, None)]
by19 = []
for n, L in ((1, 3), (7, 2)):
    for H, cnt in C.census(n):
        for Sset in C.covers(H, L):
            pts, lns = [p for k, p in Sset if k == 'P'], [i for k, i in Sset if k == 'L']
            by19.append(C.decorate_pieces(H, pts, lns))
cls19 = C.classify(by19)
for k, (H, cnt, t) in enumerate(cls19):
    spaces.append((f"19-point class {k}", H, 3, 128))
spaces += [("21-point 3-cycle of blocks", M.decorate([(0, 1, 1), (0, 0, 2), (1, 2, 2)], []), 3, 64),
           ("22-point tripod", M.decorate([(0, 1, 1), (0, 2, 2), (0, 3, 3), (1, 2, 3)], []), 3, 64)]
d1, ok1 = {}, len(cls19) == 4
for name, H, g, limit in spaces:
    E = S.graph_of(H)
    maps = minimal_maps(E, g, limit)
    pms = S.perfect_matchings(E)
    rows = study(E, maps, pms)
    d1[name] = {"genus (Fano atoms)": g, "maps": len(maps), "perfect matchings": len(pms),
                "maps by (faces 2 mod 4, three distinct faces, Arf, form 0 on differences, classes realized, zeros of q)": {str(k): v for k, v in rows.items()}}
    ok1 &= set(rows) == {(True, True, 0, True, 3 ** g, 2 ** (g - 1) * (2 ** g + 1))}
report("1 every space up to 22 points: Kasteleyn faces, Arf 0, exactly 3^h classes realized", ok1, d1)

# ---------------------------------------------------------------- 2 larger spaces
d2, ok2 = {}, True
rnd = random.Random(20261030)
for name, H, g in [("35-point space with trisum glue", M.decorate([(0, 1, 2), (0, 1, 3), (0, 4, 5), (1, 6, 7), (2, 6, 8), (2, 7, 9), (3, 4, 6), (3, 5, 7),
                                                                   (4, 8, 8), (5, 9, 9)], [(0, 0)]), 5),
                   ("43-point twisted cube", M.decorate(M.K4, M.kasteleyn_signing(M.K4)), 6)]:
    E = S.graph_of(H)
    maps = minimal_maps(E, g, 3)
    pms = some_perfect_matchings(E, 2000, rnd)
    rows = study(E, maps, pms)
    d2[name] = {"genus": g, "maps": len(maps), "sampled perfect matchings": len(pms),
                "maps by (faces 2 mod 4, three distinct faces, Arf, form 0 on sampled differences, classes hit, zeros of q)": {str(k): v for k, v in rows.items()}}
    ok2 &= all(k[:4] == (True, True, 0, True) for k in rows) and len(maps) == 3
report("2 larger spaces (trisum glue, twisted cube): Kasteleyn faces and Arf 0 on sampled maps", ok2, d2)

# ---------------------------------------------------------------- 3 trisums of prisms
d3, ok3 = {}, True
for ks, fl in [((2, 2, 2), (False, False, False)), ((2, 2, 3), (False, False, False)), ((2, 3, 3), (False, False, True)), ((3, 3, 3), (False, False, False))]:
    Ht = CL.system_of(CL.trisum_of_prisms(ks, fl), CL.C4[0])
    E = S.graph_of(Ht)
    neg = S.negated(E, M.pfaffian_signings(Ht, limit=1)[0])
    g = SL.genus(E)
    rigid = all(SL.genus_reduced([e for e in E if v not in e]) == g for v in SL.vertices(E))
    maps = SL.min_genus_rotations(E, g)
    pms = S.perfect_matchings(E)
    rows = study(E, maps, pms, neg)
    d3[f"trisum {ks}{' (flip)' if any(fl) else ''}"] = {"genus": g, "rigid at every vertex": rigid, "minimal maps": len(maps), "perfect matchings": len(pms),
                                                        "maps by (Kasteleyn, three distinct faces, Arf, form 0 on differences, classes realized, zeros)": {str(k): v for k, v in rows.items()}}
    ok3 &= g == 1 and rigid and set(rows) == {(True, True, 0, True, 3, 3)}
report("3 trisums of prisms: rigid genus one, Kasteleyn on every minimal map, Arf 0, the three even classes", ok3, d3)

# ---------------------------------------------------------------- 4 Kasteleyn determinants of the Heawood torus
d4, ok4 = {}, True
E7 = S.graph_of(F7)
pms7 = S.perfect_matchings(E7)
lines7 = sorted({u for u, v in E7}, key=str)
points7 = sorted({v for u, v in E7}, key=str)


def det_and_sign(neg, D0):
    Mx = sympy.zeros(7, 7)
    for k, (l, p) in enumerate(E7):
        Mx[lines7.index(l), points7.index(p)] += -1 if k in neg else 1
    perm = [None] * 7
    sgn = 1
    for k, (l, p) in enumerate(E7):
        if D0 >> k & 1:
            perm[lines7.index(l)] = points7.index(p)
            sgn *= -1 if k in neg else 1
    sgn *= sympy.combinatorics.Permutation(perm).signature()
    return int(Mx.det()), sgn


import sympy.combinatorics  # noqa: E402
rows = []
for bits in SL.min_genus_rotations(E7, 1):
    rot = SL.rotation(E7, bits)
    H1 = S.h1_basis(E7, rot)
    total = 0
    dets = []
    for c in (0, H1[0], H1[1], H1[0] ^ H1[1]):
        neg = frozenset(e for e in range(len(E7)) if c >> e & 1)
        dt, eps = det_and_sign(neg, pms7[0])
        arf = S.gauss_arf(S.form(E7, rot, neg, pms7[0], H1).values(), 1)
        total += (-1) ** arf * eps * dt
        dets.append(abs(dt))
    rows.append((dets[0], tuple(sorted(dets[1:])), total))
d4["maps by (knot's class |det|, other classes |det|, Cimasoni-Reshetikhin sum)"] = {str(k): v for k, v in collections.Counter(rows).items()}
ok4 &= set(rows) == {(24, (8, 8, 8), 48)}
report("4 Heawood torus: |det| 24 for the knot's class, 8 for the other three; the Cimasoni-Reshetikhin sum is 2 x 24", ok4, d4)

# ---------------------------------------------------------------- 5 non-minimal maps
d5, ok5 = {}, True
H13 = T.point_splice(F7, 0, F7, F7[0])
Ht = CL.system_of(CL.trisum_of_prisms((2, 2, 3)), CL.C4[0])
cases = [("Fano (Heawood graph)", F7, frozenset(), 1500, 11), ("13-point space", H13, frozenset(), 1500, 12),
         ("trisum (2, 2, 3)", Ht, None, 1500, 13)]
for name, H, neg, trials, seed in cases:
    E = S.graph_of(H)
    if neg is None:
        neg = S.negated(E, M.pfaffian_signings(H, limit=1)[0])
    pms = S.perfect_matchings(E)
    fund = S.fundamental_cycles(E)
    inc = SL.incident(E)
    rnd5 = random.Random(seed)
    tally = collections.Counter()
    vanish, agree, compared = True, 0, 0
    for _ in range(trials):
        rot = SL.random_rotation(E, rnd5)
        g = SL.genus_of(E, rot)
        if not all(ok for L, ok in S.face_condition(E, rot, neg)):
            tally[(g, "not Kasteleyn")] += 1
            continue
        H1 = S.h1_basis(E, rot)
        arf = arf_fast(E, rot, neg, pms[0], H1, fund, inc)
        if g <= 3:
            compared += 1
            agree += arf == S.gauss_arf(S.form(E, rot, neg, pms[0], H1, S.class_representatives(E, H1, fund)).values(), g)
        vanish &= all(S.q_of(D ^ pms[0], E, rot, neg, pms[0], inc) == 0 for D in pms[:100])
        tally[(g, "Kasteleyn, Arf", arf)] += 1
    odd = {k[0]: v for k, v in tally.items() if len(k) == 3 and k[2] == 1}
    d5[name] = {"tally (genus, kind)": {str(k): v for k, v in sorted(tally.items(), key=str)}, "odd spin structures by genus": odd,
                "form vanishes on matching differences on every Kasteleyn map": vanish,
                "fast Arf agrees with the Gauss sum (maps of genus at most 3)": f"{agree} of {compared}"}
    ok5 &= vanish and all(g >= 3 for g in odd) and agree == compared
ok5 &= bool(not d5["Fano (Heawood graph)"]["odd spin structures by genus"] and d5["13-point space"]["odd spin structures by genus"] and
            d5["trisum (2, 2, 3)"]["odd spin structures by genus"])
report("5 non-minimal maps: odd spin structures occur for the same signs, only from genus 3 on", ok5, d5)

# ---------------------------------------------------------------- 6 controls
ctrl = {}
E13 = S.graph_of(H13)
rot = SL.rotation(E13, minimal_maps(E13, 2, 1)[0])
H1 = S.h1_basis(E13, rot)
qv = S.form(E13, rot, frozenset(), S.perfect_matchings(E13)[0], H1)
realized = {S.hclass(D ^ S.perfect_matchings(E13)[0], H1) for D in S.perfect_matchings(E13)}
missing = [h for h, v in qv.items() if v == 0 and h not in realized]
ctrl["on the 13-point space one even class is not realized: the handle-even restriction is real"] = len(missing) == 1
Hc = M.K4
Ec = S.graph_of(Hc)
ctrl["the planar cube without its Kasteleyn signs is not Kasteleyn (its faces are 4-cycles)"] = \
    not all(ok for L, ok in S.face_condition(Ec, SL.rotation(Ec, SL.min_genus_rotations(Ec, 0)[0])))
report("6 controls fire", all(ctrl.values()), ctrl)

out["ok"] = ok_all
out["seconds"] = round(time.time() - T0, 1)
print("ALL OK" if ok_all else "SOME CHECK FAILED", out["seconds"], "s")
if "--write" in sys.argv:
    json.dump({"schema_version": 1, "artifact_id": "THREEFOLD-SPIN-20261030-001B-P001", "status": "Proved" if ok_all else "Failed",
               "checks": out}, open(os.path.join(HERE, "result.json"), "w"), indent=1, default=str)
sys.exit(0 if ok_all else 1)
