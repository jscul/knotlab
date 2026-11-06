"""Checks for PLAIN-COUNT-20261031-001B-P001 (plain pages are always twisted).

  0 dependency artifacts bound by the hashes recorded in manifest.json
  1 Euler: on a family of planar cubic bipartite graphs, the sum of 6 - |f| over faces is 12, there are at least six square faces, and
    every square face meets at most five faces, so some square face avoids it
  2 every plain page of the family is twisted: the cut test (plain signing against the glued Kasteleyn signing on the page's own edges)
    for every (graph, square face); the tensor test (no split form) where the page is small enough to enumerate
  3 plain trisum braces: trisum trees of plain pages (one and two squares) are braces, Pfaffian (certified), colourable when plain, and
    have three twisted branches at every square, with no good root
  4 non-2-colourable systems: in the census (n = 7..N_CENSUS) only the Fano plane occurs and its incidence graph is a brace; splices of
    Fano blocks (13 to 25 points) are non-colourable and not braces; no system has a nice cycle of length 4 or 8, while nice 6-cycles
    occur (every nice cycle of a plain non-colourable system has length 2 mod 4)
  5 controls: the cut test is not degenerate (switched Kasteleyn signings are untwisted, one extra negation on a square face away from
    the junction twists); the Heawood graph is a brace with no 4-cycle, non-colourable when plain; every graph of the family is
    colourable when plain and non-colourable under its Kasteleyn signing
Run: .venv/bin/python -B check.py [--write]   (networkx, numpy, scipy, python-sat)"""
import hashlib, itertools, json, os, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
P = lambda r: os.path.join(ROOT, "proofs", r)  # noqa: E731
for p in (P("THREEFOLD-AMPLITUDE-20261030-001A/THREEFOLD-AMPLITUDE-20261030-001A-P001_five_per_handle_tuttes_number_per_planar_piece"),
          P("THREEFOLD-AMPLITUDE-20261030-001B/THREEFOLD-AMPLITUDE-20261030-001B-P001_the_amplitude_by_computation"),
          P("TWIST-COUNT-20261030-001A/TWIST-COUNT-20261030-001A-P001_the_knots_junction_is_a_similitude"),
          P("THREEFOLD-GRAMMAR-20261030-001B/THREEFOLD-GRAMMAR-20261030-001B-P001_census_with_doubled_incidences"), HERE):
    sys.path.insert(0, p)
import networkx as nx  # noqa: E402
import amplitude_lib as AM  # noqa: E402
import computation_lib as CL  # noqa: E402
import twist_lib as TW  # noqa: E402
import census_lib as CE  # noqa: E402
import page_lib as PG  # noqa: E402

T0 = time.time()
out, ok_all = {}, True
N_CENSUS = 10
SPLICES = {"a point block": ([0], []), "a line block": ([], [0]), "two point blocks": ([0, 1], []),
           "a point and a line block": ([0], [3]), "three line blocks": ([], [0, 1, 2])}
FAM = PG.family(CL.omnitruncation)


def report(key, ok, detail):
    global ok_all
    out[key] = {"ok": bool(ok), "detail": detail}
    ok_all &= bool(ok)
    print(("PASS " if ok else "FAIL ") + key + ": " + json.dumps(detail, default=str)[:3000], flush=True)


def system(g, neg=()):
    """(lines as point-index tuples, negated (line index, point index)) of a cubic bipartite graph, colour class 0 as points"""
    col = nx.bipartite.color(g)
    pts = sorted((v for v in g if col[v] == 0), key=str)
    lns = sorted((v for v in g if col[v] == 1), key=str)
    pid = {v: i for i, v in enumerate(pts)}
    H = [tuple(sorted(pid[w] for w in g[l])) for l in lns]
    N = [(i, pid[w]) for i, l in enumerate(lns) for w in g[l] if frozenset((l, w)) in set(neg)]
    return H, N


def page_twisted(g, S):
    """cut test: plain against the Kasteleyn signing of the page, on its own edges"""
    kap = TW.kasteleyn_tree_signing([(g, [S])])
    own = TW.own_edges(g, [S])
    return not TW.coboundary(own, {e for e in own if e in kap}), kap


# ---------------------------------------------------------------- 0
man = json.load(open(os.path.join(HERE, "manifest.json")))
mism = {r: dg for r, dg in man["parent_bindings"].items()
        if hashlib.sha256(open(os.path.join(ROOT, r), "rb").read()).hexdigest() != dg}
report("0 dependency artifacts bound by hash", not mism, {"parents": len(man["parent_bindings"]), "mismatched": mism})

# ---------------------------------------------------------------- 1 Euler
d1, ok1 = {}, True
for name, g in FAM.items():
    assert nx.is_bipartite(g) and all(d == 3 for _, d in g.degree()) and nx.is_biconnected(g)
    fs = PG.faces(g)
    curv = sum(6 - len(f) for f in fs)
    sqs = [f for f in fs if len(f) == 4]
    meet = max(sum(1 for f in fs if set(f) & set(S)) for S in sqs)
    avoid = all(any(not (set(Q) & set(S)) for Q in sqs) for S in sqs)
    d1[name] = {"vertices": g.number_of_nodes(), "square faces": len(sqs), "most faces meeting a square": meet}
    ok1 &= curv == 12 and len(sqs) >= 6 and meet <= 5 and avoid
report("1 Euler: at least six square faces, at most five faces meet a square, some square face avoids each square", ok1,
       {"graphs": len(FAM), "square faces (min, max)": [min(v["square faces"] for v in d1.values()), max(v["square faces"] for v in d1.values())],
        "vertices (min, max)": [min(v["vertices"] for v in d1.values()), max(v["vertices"] for v in d1.values())],
        "most faces meeting a square": max(v["most faces meeting a square"] for v in d1.values())})

# ---------------------------------------------------------------- 2 every plain page is twisted
pages = tensors = twisted_cut = twisted_tensor = 0
for name, g in FAM.items():
    for S in PG.squares(g):
        pages += 1
        tw, _ = page_twisted(g, S)
        twisted_cut += tw
        if g.number_of_nodes() <= 40:
            inc, pts, att, sq = TW.page(g, list(S))
            tensors += 1
            twisted_tensor += TW.split_of(TW.page_tensor(inc, pts, att, set())) is None
ok2 = twisted_cut == pages and twisted_tensor == tensors
report("2 every plain page is twisted (cut test on every page, tensor test on the small ones)", ok2,
       {"pages": pages, "twisted (cut test)": twisted_cut, "tensor tests": tensors, "twisted (tensor test)": twisted_tensor})

# ---------------------------------------------------------------- 3 plain trisum braces
TO = FAM["flags of K4"]                                   # the truncated octahedron
CUBE, P6 = FAM["4-prism"], FAM["6-prism"]
to_sq = PG.squares(TO)
disjoint = [(a, b) for a, b in itertools.combinations(to_sq, 2) if not set(a) & set(b)]
TREES = {
    "three truncated octahedra": [(TO, {'X': to_sq[0]}), (TO, {'X': to_sq[1]}), (TO, {'X': to_sq[2]})],
    "cube, 6-prism, truncated octahedron": [(CUBE, {'X': PG.squares(CUBE)[0]}), (P6, {'X': PG.squares(P6)[0]}), (TO, {'X': to_sq[0]})],
    "three cubes": [(CUBE, {'X': PG.squares(CUBE)[0]})] * 3,
    "two squares: a truncated octahedron with four cubes": [(TO, {'X': disjoint[0][0], 'Y': disjoint[0][1]})]
        + [(CUBE, {'X': PG.squares(CUBE)[0]})] * 2 + [(CUBE, {'Y': PG.squares(CUBE)[1]})] * 2,
}
d3, ok3 = {}, True
for name, pieces in TREES.items():
    G, leaves, sqs = PG.glue(pieces)
    kap = TW.kasteleyn_tree_signing(leaves)
    pf = not AM.colourable(*system(G, kap))
    plain_col = AM.colourable(*system(G))
    tw = TW.twisted_branches(leaves, sqs, set(), kap)
    per = [sum(tw[(S, i)] for i in range(len(leaves)) if (S, i) in tw) for S in sqs]
    root = TW.good_root(leaves, sqs, tw)
    brace = PG.is_brace(G) if G.number_of_nodes() <= 70 else None
    d3[name] = {"vertices": G.number_of_nodes(), "brace": brace, "Pfaffian (glued signing non-colourable)": pf, "plain colourable": plain_col,
                "twisted branches per square": per, "good root": root}
    ok3 &= pf and plain_col and all(n == 3 for n in per) and root is None and brace is not False
report("3 plain trisum braces: three twisted branches at every square, no good root", ok3, d3)

# ---------------------------------------------------------------- 4 non-2-colourable systems
d4, ok4 = {"census": {}, "splices of Fano blocks": {}}, True
for n in range(7, N_CENSUS + 1):
    t1 = time.time()
    systems = [H for H, c in CE.census(n) if CE.simple(H)]
    braces = [H for H in systems if PG.is_brace(PG.incidence(H))]
    nice0 = sum(PG.nice(PG.incidence(H), PG.vertices(C)) for H in systems for L in (4, 8) for C in PG.cycles(PG.incidence(H), L))
    d4["census"][n] = {"non-2-colourable systems": len(systems), "brace incidence graphs": len(braces), "nice cycles of length 4 or 8": nice0,
                       "seconds": round(time.time() - t1, 1)}
    ok4 &= nice0 == 0 and len(braces) == len(systems) == (1 if n == 7 else 0)
    print("   n", n, d4["census"][n], flush=True)
for name, (pts_, lns_) in SPLICES.items():
    H = CE.decorate_pieces(CE.FANO, pts_, lns_)
    g = PG.incidence(H)
    nice = {L: sum(PG.nice(g, PG.vertices(C)) for C in PG.cycles(g, L)) for L in (4, 6, 8)}
    col = AM.colourable(H)
    br = PG.is_brace(g)
    d4["splices of Fano blocks"][name] = {"points": len({p for l in H for p in l}), "colourable": col, "brace": br,
                                          "nice cycles of length 4, 6, 8": [nice[4], nice[6], nice[8]]}
    ok4 &= not col and not br and nice[4] == nice[8] == 0 and nice[6] > 0
report(f"4 non-2-colourable systems (census n = 7..{N_CENSUS}, splices): only the Fano plane is a brace; nice cycles have length 2 mod 4",
       ok4, d4)

# ---------------------------------------------------------------- 5 controls
ctrl = {}
import random  # noqa: E402
rng = random.Random(5)
g = FAM["flags of K4"]
S = PG.squares(g)[0]
_, kap = page_twisted(g, S)
own = TW.own_edges(g, [S])
nondeg = True
for trial in range(20):
    U = {v for v in g if rng.random() < 0.5 and v not in S}
    switched = set(kap) ^ {frozenset((u, w)) for u in U for w in g[u] if w not in U}      # switching at U flips the cut of U
    nondeg &= TW.coboundary(own, {e for e in own if (e in switched) != (e in kap)})
Q = [Q for Q in PG.squares(g) if not set(Q) & set(S)][0]
extra = set(kap) ^ {frozenset((Q[0], Q[1]))}
nondeg &= not TW.coboundary(own, {e for e in own if (e in extra) != (e in kap)})
ctrl["the cut test is not degenerate (20 switchings untwisted; one extra negation on a far square twists)"] = nondeg
hw = PG.incidence(CE.FANO)
ctrl["Heawood: brace, no 4-cycle, plain non-colourable"] = PG.is_brace(hw) and not PG.four_cycles(hw) and not AM.colourable(*system(hw))
fam_ok = True
for name, g in FAM.items():
    kap = TW.kasteleyn_tree_signing([(g, [])])
    fam_ok &= AM.colourable(*system(g)) and not AM.colourable(*system(g, kap))
ctrl["every graph of the family: plain colourable, non-colourable under its Kasteleyn signing"] = fam_ok
report("5 controls fire", all(ctrl.values()), ctrl)

out["ok"] = ok_all
out["seconds"] = round(time.time() - T0, 1)
print("ALL OK" if ok_all else "SOME CHECK FAILED", out["seconds"], "s")
if "--write" in sys.argv:
    json.dump({"schema_version": 1, "artifact_id": "PLAIN-COUNT-20261031-001B-P001", "status": "Proved" if ok_all else "Failed",
               "checks": out}, open(os.path.join(HERE, "result.json"), "w"), indent=1, default=str)
sys.exit(0 if ok_all else 1)
