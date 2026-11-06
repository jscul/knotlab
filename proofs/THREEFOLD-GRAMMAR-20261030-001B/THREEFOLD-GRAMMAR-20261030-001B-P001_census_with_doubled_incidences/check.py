"""Checks for THREEFOLD-GRAMMAR-20261030-001B-P001 (census with doubled incidences).

  0 dependency artifacts bound by the hashes recorded in manifest.json
  1 untwisted census: connected cubic multi-systems that are not 2-colourable, n = 1..10, classes 1, 0, 1, 1, 2, 2, 8, 12, 36, 97; on
    every class: not 2-colourable by brute force, sign-nonsingular, every brace a Heawood graph, doubled square, planar brace or
    non-planar Pfaffian brace (one occurs, in a twisted class: the trisum of three cubes), every leaf
    a Heawood graph or doubled square; the only class with distinct points per line is the Fano plane
  2 twisted census (twist at line 0, point 0): n = 1..10, classes 0, 1, 1, 3, 7, 19, 54, 166, 515, 1726; twisted non-colourable by brute
    force, twisted sign-nonsingular, 2-colourable once the twist is removed, the same brace and leaf types, no Heawood leaf contains the
    twisted incidence, no class with distinct points per line; the twisted 10-point core whose glue is the trisum of three cubes
    decorates (ticket A, Theorem 6) to an untwisted 35-point system that is not 2-colourable and keeps that brace
  3 symmetry breaking replayed: without the lexicographic constraints (Glucose instead of CaDiCaL) the census has the same classes for
    n <= 5
  4 the spectrum: decorating every census core at every cover of its repeated incidences by at least two Fano pieces, up to 22 points,
    gives the sizes 7, 13, 19, 21, 22 with 1, 1, 4, 1, 1 classes (every decoration simple, cubic, connected, not 2-colourable; every
    class minimal, and the untwisted ones linear); twisted, with the twisted incidence tracked through the decoration: 14, 15, 18, 20, 21, 22 with 1, 1, 1,
    11, 7, 3 classes; the twisted doubled square with blocks on both points is T14
  5 independent SAT on systems with distinct points per line (encoder of THREEFOLD-SPACES-20261030-001B): no untwisted system at 14
    points; exactly one twisted class at 14 points, T14, which is not a brace
  6 controls that must fire
Run: .venv/bin/python -B check.py [--write]   (python-sat, networkx, numpy, sympy; about 25 minutes, mostly section 5)"""
import collections, hashlib, itertools, json, multiprocessing, os, sys, time
import networkx as nx

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
GA = os.path.join(ROOT, "proofs/THREEFOLD-GRAMMAR-20261030-001A/THREEFOLD-GRAMMAR-20261030-001A-P001_fano_leaves_and_planar_glue")
TA = os.path.join(ROOT, "proofs/THREEFOLD-SPACES-20261030-001A/THREEFOLD-SPACES-20261030-001A-P001_three_fold_spaces_are_built_from_the_fano_plane")
TB = os.path.join(ROOT, "proofs/THREEFOLD-SPACES-20261030-001B/THREEFOLD-SPACES-20261030-001B-P001_exhaustive_classification_of_small_three_fold_spaces")
for p in (TB, TA, GA, HERE):
    sys.path.insert(0, p)
import threefold_lib as T  # noqa: E402
import grammar_lib as M  # noqa: E402
import census_lib as C  # noqa: E402

UNTWISTED = {1: 1, 2: 0, 3: 1, 4: 1, 5: 2, 6: 2, 7: 8, 8: 12, 9: 36, 10: 97}
TWISTED = {1: 0, 2: 1, 3: 1, 4: 3, 5: 7, 6: 19, 7: 54, 8: 166, 9: 515, 10: 1726}
SPECTRUM = {7: 1, 13: 1, 19: 4, 21: 1, 22: 1}
TWISTED_SPECTRUM = {14: 1, 15: 1, 18: 1, 20: 11, 21: 7, 22: 3}
NMAX, BOUND, REPLAY = 10, 22, 5


def sat14(twisted):
    """section 5 worker: all symmetry-broken solutions at 14 points with distinct points per line (twisted or not), with classes"""
    import sat_lib as S
    from pysat.solvers import Solver
    t0 = time.time()
    cnf, pool, x = S.build(14, twisted, True)
    sols = []
    with Solver(name='cadical153', bootstrap_with=cnf.clauses) as s:
        while s.solve():
            model = s.get_model()
            sols.append(S.decode(model, x, 14))
            m = set(v for v in model if v > 0)
            s.add_clause([-x(l, p) if x(l, p) in m else x(l, p) for l in range(14) for p in range(14)])
    classes = C.classify(sols, [(0, 0)] * len(sols) if twisted else None)
    return {"solutions": len(sols), "classes": [H for H, c, t in classes],
            "brace": [M.find_tight_cut(M.multigraph(H)) is None for H, c, t in classes], "seconds": round(time.time() - t0)}


def without_line(H, i, twist):
    """H minus line i, with the twist re-indexed (dropped with its line)"""
    rest = [l for j, l in enumerate(H) if j != i]
    if twist is None or twist[0] == i:
        return rest, None
    return rest, (twist[0] - (twist[0] > i), twist[1])


if __name__ == "__main__":
    T0 = time.time()
    out, ok_all = {}, True
    pool = multiprocessing.Pool(2)
    jobs = {tw: pool.apply_async(sat14, (tw,)) for tw in (False, True)}       # section 5 runs while the rest is checked

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

    # ---------------------------------------------------------------- 1, 2 the census and the predictions of ticket A
    census = {}
    C4 = [('c', j) for j in range(4)]
    TRI3 = M.trisum([M.cube_on(C4, 'a'), M.cube_on(C4, 'b'), M.cube_on(C4, 'd')], C4, [(C4[j], C4[(j + 1) % 4]) for j in range(4)])

    def properties(H, tw):
        neg = [(0, 0)] if tw else []
        rec = {"not colourable": not C.colourable(H, tw), "SNS": T.sns(H, neg)[0], "simple": C.simple(H),
               "colourable without the twist": C.colourable(H) if tw else None}
        braces, leaves, twist_in_heawood_leaf = collections.Counter(), collections.Counter(), False
        for b in M.decompose(M.multigraph(H)):
            t, k = M.brace_type(b)
            if t == 'other':
                g = nx.Graph([(u, w) for u in b for w in b[u]])
                simple_b = not any(c > 1 for u in b for c in b[u].values())
                pfaff = simple_b and len(M.pfaffian_signings(M.system_of(g))) == 1
                t = 'non-planar Pfaffian' if pfaff else 'other'
                if pfaff and nx.is_isomorphic(g, TRI3):
                    t = 'non-planar Pfaffian (trisum of three cubes)'
            braces[t] += 1
            if k == 1:
                leaves[t] += 1
                if tw and t == 'heawood' and ('P', 0) in b and ('L', 0) in b:
                    twist_in_heawood_leaf = True
        rec.update(braces=braces, leaves=leaves, twist_in_heawood_leaf=twist_in_heawood_leaf)
        return rec

    for tw, expected, key in ((False, UNTWISTED, "1 untwisted census"), (True, TWISTED, "2 twisted census")):
        t1 = time.time()
        counts, bad, braces, leaves, simple_classes, nonplanar = {}, [], collections.Counter(), collections.Counter(), [], []
        for n in range(1, NMAX + 1):
            cl = C.census(n, tw)
            census[(tw, n)] = [H for H, c in cl]
            counts[n] = len(cl)
            for H, c in cl:
                r = properties(H, tw)
                braces.update(r["braces"])
                leaves.update(r["leaves"])
                if r["simple"]:
                    simple_classes.append(H)
                if not (r["not colourable"] and r["SNS"]) or (tw and not r["colourable without the twist"]) or r["twist_in_heawood_leaf"] or \
                        not all(t in {'heawood', 'doubled square', 'planar'} or t.startswith('non-planar Pfaffian') for t in r["braces"]) or \
                        not set(r["leaves"]) <= {'heawood', 'doubled square'}:
                    bad.append((n, H, r))
                if any(t.startswith('non-planar Pfaffian') for t in r["braces"]):
                    nonplanar.append((n, H))
        extra = {}
        if tw:
            simple_ok = not simple_classes
            # ticket A, Theorem 6 on a core with non-planar glue: T14 on the twisted point, Fano blocks on the repeated points
            witness = []
            for n0, H0 in nonplanar:
                D0 = M.decorate(H0, [(0, 0)])
                kinds = collections.Counter()
                for b in M.decompose(M.multigraph(D0)):
                    g = nx.Graph([(u, w) for u in b for w in b[u]])
                    kinds['trisum of three cubes' if len(b) == 16 and nx.is_isomorphic(g, TRI3) else M.brace_type(b)[0]] += 1
                witness.append({"core": H0, "points": T.npoints(D0), "2-colourable": T.colourable_sat(D0), "braces": kinds})
            extra["cores with non-planar glue, decorated untwisted"] = witness
            simple_ok &= bool(witness) and all(not w["2-colourable"] and w["braces"].get('trisum of three cubes') for w in witness)
        else:
            simple_ok = len(simple_classes) == 1 and nx.is_isomorphic(C.graph(simple_classes[0]), C.graph(T.FANO), node_match=C._nm)
        report(key, counts == expected and not bad and simple_ok,
               {"classes by n": counts, "classes violating a prediction": bad[:3], "brace types (all classes)": braces, "leaf types": leaves,
                "classes with distinct points per line": simple_classes, "classes with non-planar glue": nonplanar, **extra,
                "seconds": round(time.time() - t1)})

    # ---------------------------------------------------------------- 3 symmetry breaking replayed
    rep = {}
    for tw in (False, True):
        for n in range(1, REPLAY + 1):
            b = C.census(n, tw, lex=False, solver='glucose4')
            a = census[(tw, n)]
            same = len(a) == len(b) and all(any(nx.is_isomorphic(C.graph(H, tw), C.graph(K, tw), node_match=C._nm, edge_match=C._em)
                                                for K, c in b) for H in a)
            rep[("twisted " if tw else "untwisted ") + str(n)] = (len(a), len(b), sum(c for K, c in b), same)
    report("3 the census without symmetry breaking has the same classes (classes, classes, labelled solutions, same)",
           all(v[3] for v in rep.values()), rep)

    # ---------------------------------------------------------------- 4 the spectrum
    d4 = {}
    ok4 = True
    for tw, expected in ((False, SPECTRUM), (True, TWISTED_SPECTRUM)):
        byN = collections.defaultdict(list)
        for n in range(1, NMAX + 1):
            for H in census[(tw, n)]:
                for L in range(2, 2 * n + 1):
                    if n + 6 * L > BOUND:
                        break
                    for S in C.covers(H, L):
                        pts, lns = [p for k, p in S if k == 'P'], [i for k, i in S if k == 'L']
                        byN[n + 6 * L].append(C.decorate_pieces(H, pts, lns, (0, 0)) if tw else (C.decorate_pieces(H, pts, lns), None))
        if not tw:
            byN[7].append((list(T.FANO), None))                  # the Fano plane has no leaves
        found, recs = {}, {}
        for N in sorted(byN):
            syss, tws = [D for D, t in byN[N]], [t for D, t in byN[N]]
            cls = C.classify(syss, tws if tw else None)
            found[N] = len(cls)
            good = all(C.simple(D) and T.is_cubic(D) and T.connected(D) and not T.colourable_sat(D, t) for D, t in byN[N])
            linear = all(all(len(set(a) & set(b)) <= 1 for a, b in itertools.combinations(H, 2)) for H, c, t in cls)
            minimal = all(all(T.colourable_sat(*without_line(H, i, t)) for i in range(len(H))) for H, c, t in cls)
            recs[N] = {"decorations": len(syss), "classes": len(cls), "all simple, cubic, connected, not colourable": good,
                       "classes linear": linear, "classes minimal": minimal}
            ok4 &= good and minimal and (linear or tw)
            if not tw and N == 19:
                dual = lambda H: [tuple(sorted(i for i, l in enumerate(H) if p in l)) for p in range(T.npoints(H))]  # noqa: E731
                orbits = []
                for H, c, t in cls:
                    if not any(nx.is_isomorphic(C.graph(dual(H)), C.graph(K), node_match=C._nm) for K in orbits):
                        orbits.append(H)
                recs[N]["classes up to point-line duality"] = len(orbits)
        d4["twisted" if tw else "untwisted"] = {"sizes and classes": found, "per size": recs}
        ok4 &= found == expected
    T14D, tw14 = C.decorate_pieces([(0, 1, 1), (0, 0, 1)], [0, 1], [], (0, 0))
    is_t14 = nx.is_isomorphic(C.graph(T14D, tw14), C.graph(M.T14, True), node_match=C._nm, edge_match=C._em)
    d4["the twisted doubled square with Fano blocks on both points is T14"] = is_t14
    report("4 the spectrum up to 22 points: untwisted 7, 13, 19, 21, 22; twisted 14, 15, 18, 20, 21, 22", ok4 and is_t14, d4)

    # ---------------------------------------------------------------- 6 controls
    ctrl = {}
    DS = [(0, 1, 1), (0, 0, 1)]
    DH = [(0, 1, 1), (0, 0, 2), (1, 2, 2)]
    ctrl["the doubled square is 2-colourable and not sign-nonsingular"] = C.colourable(DS) and not T.sns(DS)[0]
    ctrl["a decoration missing a repeated incidence leaves a repeated point"] = not C.simple(C.decorate_pieces(DH, [1, 2], []))
    ctrl["decorating a 2-colourable core gives a 2-colourable system"] = T.colourable_sat(C.decorate_pieces(DS, [0, 1], []))
    ctrl["T14 with its twist on another incidence of the twisted line is 2-colourable (twisted)"] = T.colourable_sat(M.T14, (0, 1))
    report("6 controls fire", all(ctrl.values()), ctrl)

    # ---------------------------------------------------------------- 5 independent SAT at 14 points
    res = {("twisted" if tw else "untwisted"): j.get() for tw, j in jobs.items()}
    pool.close()
    u, t = res["untwisted"], res["twisted"]
    same_as_T14 = len(t["classes"]) == 1 and nx.is_isomorphic(C.graph(t["classes"][0], True), C.graph(M.T14, True), node_match=C._nm, edge_match=C._em)
    report("5 SAT at 14 points: no untwisted system; one twisted class (T14), not a brace",
           u["solutions"] == 0 and t["solutions"] >= 1 and same_as_T14 and not any(t["brace"]), res)

    out["ok"] = ok_all
    out["seconds"] = round(time.time() - T0, 1)
    print("ALL OK" if ok_all else "SOME CHECK FAILED", out["seconds"], "s")
    if "--write" in sys.argv:
        json.dump({"schema_version": 1, "artifact_id": "THREEFOLD-GRAMMAR-20261030-001B-P001", "status": "Proved" if ok_all else "Failed",
                   "checks": out}, open(os.path.join(HERE, "result.json"), "w"), indent=1, default=str)
    sys.exit(0 if ok_all else 1)
