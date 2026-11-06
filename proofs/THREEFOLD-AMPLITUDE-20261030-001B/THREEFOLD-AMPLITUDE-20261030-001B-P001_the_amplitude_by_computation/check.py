"""Checks for THREEFOLD-AMPLITUDE-20261030-001B-P001 (the amplitude by computation).

  0 dependency artifacts bound by the hashes recorded in manifest.json
  1 the census up to 10 points (SAT, THREEFOLD-GRAMMAR-20261030-001B): every class is not colourable, has one amplitude at every line, the
    same as its transpose at every point, and equal to the product of its brace amplitudes
  2 every space up to 22 points: the law is exact at every corner line with lambda(0) = (-1)^(n-1) 5^(Fano atoms); twisted classes have one
    amplitude equal to the product of their brace amplitudes
  3 planar glue: omnitruncations of 13 maps (amplitude = spanning trees of the map = arborescence numbers) and the glue of 6 hypermaps
    (amplitude = hypertrees of both hypergraphs = arborescence numbers, not the hypermap's spanning trees)
  4 trisums of three prisms along a square face, 11 triples x 4 gluings, and 6 nested trisums: Pfaffian braces, one amplitude shared with
    the transpose, colourable without the signing; the amplitude depends on the gluing
  5 controls that must fire
Run: .venv/bin/python -B check.py [--write]   (networkx, numpy, sympy, python-sat; about six minutes, mostly the SAT census)"""
import collections, hashlib, json, os, sys, time
import networkx as nx

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
TA = os.path.join(ROOT, "proofs/THREEFOLD-SPACES-20261030-001A/THREEFOLD-SPACES-20261030-001A-P001_three_fold_spaces_are_built_from_the_fano_plane")
GA = os.path.join(ROOT, "proofs/THREEFOLD-GRAMMAR-20261030-001A/THREEFOLD-GRAMMAR-20261030-001A-P001_fano_leaves_and_planar_glue")
GB = os.path.join(ROOT, "proofs/THREEFOLD-GRAMMAR-20261030-001B/THREEFOLD-GRAMMAR-20261030-001B-P001_census_with_doubled_incidences")
AA = os.path.join(ROOT, "proofs/THREEFOLD-AMPLITUDE-20261030-001A/THREEFOLD-AMPLITUDE-20261030-001A-P001_five_per_handle_tuttes_number_per_planar_piece")
for p in (TA, GA, GB, AA, HERE):
    sys.path.insert(0, p)
import threefold_lib as T  # noqa: E402
import grammar_lib as M  # noqa: E402
import census_lib as C  # noqa: E402
import amplitude_lib as AM  # noqa: E402
import computation_lib as CL  # noqa: E402

T0 = time.time()
out, ok_all = {}, True


def report(key, ok, detail):
    global ok_all
    out[key] = {"ok": bool(ok), "detail": detail}
    ok_all &= bool(ok)
    print(("PASS " if ok else "FAIL ") + key + ": " + json.dumps(detail, default=str)[:3000], flush=True)


def transpose(H, neg=()):
    HT = [tuple(i for i, l in enumerate(H) for q in l if q == p) for p in range(1 + max(p for l in H for p in l))]
    return HT, [(p, i) for (i, p) in neg]


def one_amplitude(H, neg=()):
    """(amplitudes at lines, transposed amplitudes at points, colourable, transpose colourable)"""
    HT, negT = transpose(H, neg)
    return (sorted({AM.amplitude(H, L, neg) for L in range(len(H))}), sorted({AM.amplitude(HT, p, negT) for p in range(len(HT))}),
            AM.colourable(H, neg), AM.colourable(HT, negT))


# ---------------------------------------------------------------- 0
man = json.load(open(os.path.join(HERE, "manifest.json")))
mism = {r: dg for r, dg in man["parent_bindings"].items()
        if hashlib.sha256(open(os.path.join(ROOT, r), "rb").read()).hexdigest() != dg}
report("0 dependency artifacts bound by hash", not mism, {"parents": len(man["parent_bindings"]), "mismatched": mism})

# ---------------------------------------------------------------- 1 the census
census = {}
d1, ok1 = {}, True
for tw in (False, True):
    per_n, dist, kinds_seen, bad = {}, collections.Counter(), collections.Counter(), []
    for n in range(1, 11):
        census[(tw, n)] = C.census(n, tw)
        for H, cnt in census[(tw, n)]:
            neg = [(0, 0)] if tw else []
            a, aT, col, colT = one_amplitude(H, neg)
            prod, kinds = CL.brace_product(H, M, AM)
            good = not col and not colT and len(a) == 1 and a == aT == [prod]
            if not good:
                bad.append((H, a, aT, prod))
            dist[a[0] if a else None] += 1
            kinds_seen.update(set(kinds))
        per_n[n] = len(census[(tw, n)])
    d1["twisted" if tw else "untwisted"] = {"classes per n": per_n, "classes": sum(per_n.values()), "amplitude distribution": dict(sorted(dist.items())),
                                            "brace kinds met": dict(kinds_seen), "failures": bad[:3]}
    ok1 &= not bad
ok1 &= d1["untwisted"]["classes"] == 160 and d1["twisted"]["classes"] == 2492
report("1 the census: not colourable, one amplitude shared with the transpose, the product of the brace amplitudes", ok1, d1)

# ---------------------------------------------------------------- 2 every space up to 22 points
spaces = {False: [("Fano (7)", T.FANO, None)], True: []}
for tw in (False, True):
    byN = collections.defaultdict(list)
    for n in range(1, 11):
        for H, cnt in census[(tw, n)]:
            for L in range(2, 2 * n + 1):
                if n + 6 * L > 22:
                    break
                for Sset in C.covers(H, L):
                    pts, lns = [p for k, p in Sset if k == 'P'], [i for k, i in Sset if k == 'L']
                    byN[n + 6 * L].append(C.decorate_pieces(H, pts, lns, (0, 0)) if tw else (C.decorate_pieces(H, pts, lns), None))
    for N in sorted(byN):
        cls = C.classify([D for D, t in byN[N]], [t for D, t in byN[N]] if tw else None)
        for k, (H, cnt, t) in enumerate(cls):
            spaces[tw].append((f"{N}-point class {k}", H, t))
d2, ok2 = {"untwisted": {}, "twisted": {}}, True
for name, H, t in spaces[False]:
    n = T.npoints(H)
    prod, kinds = CL.brace_product(H, M, AM)
    h = kinds.count('heawood')
    lams = set()
    exact_all = True
    for L0 in H:
        exact, lam = AM.lambda0(T.gadget_from(H, L0))
        exact_all &= exact
        lams |= lam
    d2["untwisted"][name] = {"corner lines": len(H), "exact at all": exact_all, "lambda(0)": sorted(lams), "Fano atoms": h}
    ok2 &= exact_all and lams == {(-1) ** (n - 1) * 5 ** h} and prod == 5 ** h
for name, H, t in spaces[True]:
    neg = [t]
    a, aT, col, colT = one_amplitude(H, neg)
    prod, kinds = CL.brace_product(H, M, AM)
    d2["twisted"][name] = {"amplitudes": a, "transposed": aT, "product": prod, "braces": dict(collections.Counter(kinds))}
    ok2 &= not col and len(a) == 1 and a == aT == [prod]
ok2 &= len(spaces[False]) == 8 and len(spaces[True]) == 24
report("2 every space up to 22 points: the law exact at every corner with lambda(0) = (-1)^(n-1) 5^atoms; twisted classes", ok2, d2)

# ---------------------------------------------------------------- 3 planar glue
MAPS = {"triangle": nx.cycle_graph(3), "4-cycle": nx.cycle_graph(4), "5-cycle": nx.cycle_graph(5), "K4": nx.complete_graph(4),
        "cube": nx.hypercube_graph(3), "octahedron": nx.octahedral_graph(), "triangular prism": nx.circular_ladder_graph(3),
        "square pyramid": nx.wheel_graph(5), "W6": nx.wheel_graph(6), "W7": nx.wheel_graph(7), "K2,3": nx.complete_bipartite_graph(2, 3),
        "pentagonal prism": nx.circular_ladder_graph(5), "dodecahedron": nx.dodecahedral_graph()}
d3, ok3 = {"omnitruncations": {}, "hypermaps": {}}, True
for name, g in MAPS.items():
    H = CL.system_of(CL.omnitruncation(g))
    neg = M.kasteleyn_signing(H)
    amps = sorted({AM.amplitude(H, L, neg) for L in range(len(H))})
    arb = [AM.arborescence_number(H, c) for c in range(3)]
    tau = CL.spanning_trees(g)
    row = {"lines": len(H), "amplitudes": amps, "arborescence numbers": arb, "spanning trees of the map": tau}
    if len(H) <= 12:
        row["Tutte matchings"] = sorted({AM.tutte_matchings(H, L) for L in range(len(H))})
        ok3 &= row["Tutte matchings"] == amps
    d3["omnitruncations"][name] = row
    ok3 &= amps == [tau] and set(arb) == {tau} and not AM.colourable(H, neg)
HYP = {"K2,3": nx.complete_bipartite_graph(2, 3), "K2,4": nx.complete_bipartite_graph(2, 4), "6-cycle": nx.cycle_graph(6),
       "cube": nx.hypercube_graph(3), "hexagonal prism": nx.circular_ladder_graph(6), "3x4 grid": nx.grid_2d_graph(3, 4)}
for name, G in HYP.items():
    col = nx.bipartite.color(G)
    U, W = [v for v in G if col[v] == 0], [v for v in G if col[v] == 1]
    H = CL.system_of(CL.hypermap_glue(G))
    neg = M.kasteleyn_signing(H)
    amps = sorted({AM.amplitude(H, L, neg) for L in range(len(H))})
    arb = [AM.arborescence_number(H, c) for c in range(3)]
    ht = (CL.hypertrees(G, W), CL.hypertrees(G, U))
    tauG = CL.spanning_trees(G)
    d3["hypermaps"][name] = {"lines": len(H), "amplitudes": amps, "arborescence numbers": arb, "hypertrees (both hypergraphs)": ht,
                             "spanning trees of the hypermap": tauG}
    ok3 &= len(amps) == 1 and set(arb) == set(amps) == set(ht) and tauG != amps[0]
report("3 planar glue: spanning trees of maps, hypertrees of hypermaps, arborescence numbers", ok3, d3)

# ---------------------------------------------------------------- 4 trisums
d4, ok4 = {"trisums of prisms": {}, "nested": {}}, True
GLUINGS = [(False, False, False), (False, False, True), (False, True, False), (False, True, True)]
TRIPLES = [(2, 2, 2), (2, 2, 3), (2, 3, 3), (3, 3, 3), (2, 2, 4), (2, 3, 4), (3, 3, 4), (2, 4, 4), (4, 4, 4), (2, 2, 5), (2, 3, 5)]
for ks in TRIPLES:
    row = {}
    for fl in GLUINGS:
        H = CL.system_of(CL.trisum_of_prisms(ks, fl), CL.C4[0])
        br = M.decompose(M.multigraph(H))
        sigs = M.pfaffian_signings(H, limit=1)
        if not sigs:
            row["".join("1" if f else "0" for f in fl)] = "no Pfaffian signing"
            ok4 = False
            continue
        a, aT, col, colT = one_amplitude(H, sigs[0])
        row["".join("1" if f else "0" for f in fl)] = a[0] if len(a) == 1 else a
        ok4 &= len(br) == 1 and not col and not colT and len(a) == 1 and a == aT and AM.colourable(H)
    d4["trisums of prisms"][str(ks)] = row
for ks in [(2, 2, k) for k in (2, 3, 4, 5)]:
    ok4 &= set(d4["trisums of prisms"][str(ks)].values()) == {3 * ks[2]}
ok4 &= set(d4["trisums of prisms"]["(2, 3, 3)"].values()) == {13, 14} and set(d4["trisums of prisms"]["(4, 4, 4)"].values()) == {36, 52}


def far_face_piece(inner, tag):
    face = [('a', ('u', 2)), ('a', ('u', 3)), ('a', ('v', 3)), ('a', ('v', 2))]
    mp = dict(zip(face, CL.C4))
    return nx.relabel_nodes(inner, lambda v: mp.get(v, (tag, v)))


for ks_in, ks2 in [((2, 2, 2), (2, 2)), ((2, 2, 2), (2, 3)), ((2, 2, 3), (2, 2))]:
    for f in (False, True):
        g = nx.Graph()
        g.add_edges_from(far_face_piece(CL.trisum_of_prisms(ks_in), 'n').edges())
        g.add_edges_from(CL.prism_on(ks2[0], 'p', False).edges())
        g.add_edges_from(CL.prism_on(ks2[1], 'q', f).edges())
        g.remove_edges_from([(CL.C4[j], CL.C4[(j + 1) % 4]) for j in range(4)])
        H = CL.system_of(g, CL.C4[0])
        br = M.decompose(M.multigraph(H))
        sig = M.pfaffian_signings(H, limit=1)[0]
        a, aT, col, colT = one_amplitude(H, sig)
        d4["nested"][f"trisum{ks_in} with prisms {ks2}{' (flip)' if f else ''}"] = {"points": len(H), "braces": len(br), "amplitude": a}
        ok4 &= len(br) == 1 and not col and len(a) == 1 and a == aT
report("4 trisums: Pfaffian braces with one amplitude shared with the transpose; the amplitude depends on the gluing", ok4, d4)

# ---------------------------------------------------------------- 5 controls
ctrl = {}
ctrl["hypertrees are not spanning trees: K2,3 has 3 hypertrees and 12 spanning trees"] = \
    (CL.hypertrees(nx.complete_bipartite_graph(2, 3), [2, 3, 4]), CL.spanning_trees(nx.complete_bipartite_graph(2, 3))) == (3, 12)
Hc = CL.system_of(CL.omnitruncation(nx.complete_graph(4)))
ctrl["an omnitruncation without its Kasteleyn signs is colourable"] = AM.colourable(Hc)
ctrl["the trisum (2, 3, 3) has different amplitudes for two gluings, so the pieces' amplitudes do not determine it"] = \
    d4["trisums of prisms"]["(2, 3, 3)"]["000"] != d4["trisums of prisms"]["(2, 3, 3)"]["001"]
ctrl["the census has twisted classes that are colourable without their twist (the twist matters)"] = \
    any(AM.colourable(H) for H, c in census[(True, 5)])
report("5 controls fire", all(ctrl.values()), ctrl)

out["ok"] = ok_all
out["seconds"] = round(time.time() - T0, 1)
print("ALL OK" if ok_all else "SOME CHECK FAILED", out["seconds"], "s")
if "--write" in sys.argv:
    json.dump({"schema_version": 1, "artifact_id": "THREEFOLD-AMPLITUDE-20261030-001B-P001", "status": "Proved" if ok_all else "Failed",
               "checks": out}, open(os.path.join(HERE, "result.json"), "w"), indent=1, default=str)
sys.exit(0 if ok_all else 1)
