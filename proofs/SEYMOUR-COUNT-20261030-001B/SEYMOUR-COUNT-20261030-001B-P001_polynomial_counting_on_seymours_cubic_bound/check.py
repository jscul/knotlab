"""Checks for SEYMOUR-COUNT-20261030-001B-P001 (polynomial counting on Seymour's cubic bound).

  0 dependency artifacts bound by the hashes recorded in manifest.json
  1 Berman: on planar braces, at every line, |det| of the line-face matrix = the number of Tutte matchings (a permanent) = the amplitude by
    direct count; at every square face, in both labellings, the restricted determinants = restricted permanents = the leaning split
  2 weighted rows: with child weights on square lines, |det| = the weighted permanent; as a polynomial in the weights, every coefficient
    of the determinant has one sign
  3 the trisum tree found by search: leaves planar braces, squares disjoint trisectors of the whole brace on no 4-cycle, each a face of its
    three leaves, leaves and squares a tree; on the smaller braces every trisector avoids 4-cycles and there are at most n - 5
  4 brace amplitudes by the tree against direct counts: 44 trisums of prisms, 14 nested trisums, 6 depth-3 chains and 3 stars; the
    transposed tree and every choice of root square agree
  5 the whole pipeline (tight cuts, braces, trees) on three-fold spaces against direct counts, 22 to 118 points
  6 scale: trisums and a chain of omnitruncations (208 to 480 vertices) against direct counts with a glued Kasteleyn signing; trisums of
    omnitruncated grids (472 to 1720 vertices) where variable elimination would need factors on 17 to 30 variables
  7 controls that must fire
Run: .venv/bin/python -B check.py [--write]   (networkx, python-sat, numpy, sympy; about two minutes)"""
import collections, hashlib, itertools, json, os, random, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
P = lambda r: os.path.join(ROOT, "proofs", r)  # noqa: E731
for p in (P("THREEFOLD-SPACES-20261030-001A/THREEFOLD-SPACES-20261030-001A-P001_three_fold_spaces_are_built_from_the_fano_plane"),
          P("THREEFOLD-SURFACES-20261030-001A/THREEFOLD-SURFACES-20261030-001A-P001_fano_atoms_are_handles"),
          P("THREEFOLD-GRAMMAR-20261030-001A/THREEFOLD-GRAMMAR-20261030-001A-P001_fano_leaves_and_planar_glue"),
          P("THREEFOLD-AMPLITUDE-20261030-001A/THREEFOLD-AMPLITUDE-20261030-001A-P001_five_per_handle_tuttes_number_per_planar_piece"),
          P("THREEFOLD-AMPLITUDE-20261030-001B/THREEFOLD-AMPLITUDE-20261030-001B-P001_the_amplitude_by_computation"),
          P("THREEFOLD-SPIN-20261030-001A/THREEFOLD-SPIN-20261030-001A-P001_kasteleyn_faces_and_even_spin_structures"),
          P("SEYMOUR-COUNT-20261030-001A/SEYMOUR-COUNT-20261030-001A-P001_the_trisum_law"), HERE):
    sys.path.insert(0, p)
import networkx as nx  # noqa: E402
import sympy  # noqa: E402
import threefold_lib as T  # noqa: E402
import grammar_lib as M  # noqa: E402
import amplitude_lib as AM  # noqa: E402
import computation_lib as CL  # noqa: E402
import trisum_lib as TL  # noqa: E402
import seymour_lib as SY  # noqa: E402

T0 = time.time()
out, ok_all = {}, True


def report(key, ok, detail):
    global ok_all
    out[key] = {"ok": bool(ok), "detail": detail}
    ok_all &= bool(ok)
    print(("PASS " if ok else "FAIL ") + key + ": " + json.dumps(detail, default=str)[:3000], flush=True)


# ---------------------------------------------------------------- builders
def sq(name):
    return tuple((name, j) for j in range(4))


def lines_of(G, point):
    col = nx.bipartite.color(G)
    return {v for v in G if col[v] != col[point]}


def glue(pieces, S):
    G = nx.Graph()
    for g in pieces:
        G.add_edges_from(g.edges())
    G.remove_edges_from([(S[j], S[(j + 1) % 4]) for j in range(4)])
    assert all(d == 3 for _, d in G.degree())
    return G


def multi_square_prism(k, labels, flips, tag):
    """the 2k-prism with the square faces u_j u_(j+1) v_(j+1) v_j at j = 0, 2, 4, ... labelled (flip exchanges c0 and c2)"""
    m = 2 * k
    g = nx.Graph()
    for i in range(m):
        g.add_edges_from([(('u', i), ('u', (i + 1) % m)), (('v', i), ('v', (i + 1) % m)), (('u', i), ('v', i))])
    mp = {}
    for t, (lab, f) in enumerate(zip(labels, flips)):
        face = [('u', 2 * t), ('u', 2 * t + 1), ('v', 2 * t + 1), ('v', 2 * t)]
        mp.update(dict(zip(face, list(lab) if not f else [lab[2], lab[1], lab[0], lab[3]])))
    return nx.relabel_nodes(g, lambda v: mp.get(v, (tag, v)))


def label_face(g, f, S, flip, col):
    """label the 4-face f of g by the square S, starting at a vertex of colour 0"""
    cyc = [next(v for v in f if col[v] == 0)]
    while len(cyc) < 4:
        cyc.append(next(w for w in g[cyc[-1]] if w in f and w not in cyc))
    return dict(zip(cyc, list(S) if not flip else [S[2], S[1], S[0], S[3]]))


def omni_piece(mapg, squares, flips, tag, rng):
    """the omnitruncation of a planar map with disjoint, non-adjacent 4-faces labelled by the given squares"""
    g = CL.omnitruncation(mapg)
    col = nx.bipartite.color(g)
    faces = [f for f in SY.plane_faces(g) if len(f) == 4]
    rng.shuffle(faces)
    used, mp, chosen = set(), {}, []
    for f in faces:
        if len(chosen) < len(squares) and not (f & used) and not any(set(g[v]) & used for v in f):
            chosen.append(f)
            used |= f
    for f, S, fl in zip(chosen, squares, flips):
        mp.update(label_face(g, f, S, fl, col))
    return nx.relabel_nodes(g, lambda v: mp.get(v, (tag, v)))


def permanent(A):
    """Ryser's formula"""
    n = len(A)
    total = 0
    for S in range(1, 1 << n):
        prod = 1
        for r in range(n):
            s = sum(A[r][c] for c in range(n) if S >> c & 1)
            if s == 0:
                prod = 0
                break
            prod *= s
        total += (-1) ** bin(S).count('1') * prod
    return (-1) ** n * total


def direct_amplitudes(G, point, lines_idx=None):
    """amplitudes at three lines by exact counting with a Pfaffian signing from a minimal map (ticket A's library)"""
    H, pid, lid, lns = TL.as_system(G, point)
    neg, _ = TL.pfaffian_signing(H)
    return {AM.amplitude(H, L, neg) for L in (lines_idx or (0, len(H) // 2, len(H) - 1))}


BRACE_CACHE = {}


def is_brace(g):
    """2-extendable: every matching of two edges extends to a perfect matching (cached by isomorphism class)"""
    key = (g.number_of_nodes(), g.number_of_edges(), nx.weisfeiler_lehman_graph_hash(g, iterations=4))
    if key not in BRACE_CACHE:
        BRACE_CACHE[key] = _is_brace(g)
    return BRACE_CACHE[key]


def _is_brace(g):
    col = nx.bipartite.color(g)
    top = [v for v in g if col[v] == 0]
    for e, f in itertools.combinations(g.edges(), 2):
        if len(set(e) | set(f)) < 4:
            continue
        h = g.copy()
        h.remove_nodes_from(set(e) | set(f))
        m = nx.bipartite.hopcroft_karp_matching(h, top_nodes=[v for v in top if v in h])
        if len(m) != h.number_of_nodes():
            return False
    return True


def tree_signing(leaves, lines):
    """a Pfaffian signing of the brace built the Robertson-Seymour-Thomas way: a Kasteleyn signing of every leaf, switched at the square
    vertices so that every square carries one negation, on (c1, c0), then glued (as frozensets of negated edges)"""
    neg = set()
    for g, sqs in leaves:
        ok, emb = nx.check_planarity(g)
        seen, faces = set(), []
        for u, v in emb.edges():
            if (u, v) not in seen:
                faces.append(emb.traverse_face(u, v, mark_half_edges=seen))
        edges = [frozenset(e) for e in g.edges()]
        eid = {e: k for k, e in enumerate(edges)}
        piv = {}
        for f in faces[:-1]:
            vec, rhs = 0, (len(f) // 2 - 1) % 2
            for a, b in zip(f, f[1:] + f[:1]):
                vec ^= 1 << eid[frozenset((a, b))]
            for b, (pv, pr) in piv.items():
                if vec >> b & 1:
                    vec, rhs = vec ^ pv, rhs ^ pr
            if vec == 0:
                assert rhs == 0
                continue
            b = vec.bit_length() - 1
            for b2 in list(piv):
                if piv[b2][0] >> b & 1:
                    piv[b2] = (piv[b2][0] ^ vec, piv[b2][1] ^ rhs)
            piv[b] = (vec, rhs)
        x = sum(1 << b for b, (pv, pr) in piv.items() if pr)
        kneg = {edges[k] for k in range(len(edges)) if x >> k & 1}
        for S in sqs:
            cyc = [frozenset((S[j], S[(j + 1) % 4])) for j in range(4)]
            delta = {e for e in cyc if (e in kneg) != (e == cyc[0])}
            W = next(W for W in itertools.product((0, 1), repeat=4) if {cyc[j] for j in range(4) if W[j] != W[(j + 1) % 4]} == delta)
            for j in range(4):
                if W[j]:
                    kneg ^= {frozenset((S[j], w)) for w in g[S[j]]}
        sqe = {frozenset((S[j], S[(j + 1) % 4])) for S in sqs for j in range(4)}
        neg |= kneg - sqe
    return neg


def few_negations(H, neg):
    """switch points and lines while one of them carries two or three negated incidences"""
    neg = set(neg)
    at_p = collections.defaultdict(list)
    for i, l in enumerate(H):
        for p in set(l):
            at_p[p].append(i)
    changed = True
    while changed:
        changed = False
        groups = [[(i, p) for p in set(l)] for i, l in enumerate(H)] + [[(i, p) for i in ls] for p, ls in at_p.items()]
        for es in groups:
            if sum(e in neg for e in es) >= 2:
                neg ^= set(es)
                changed = True
    return sorted(neg)


def elimination_width(H):
    """the largest factor scope of min-degree variable elimination on the system's primal graph (what exact elimination would build)"""
    g = nx.Graph()
    for l in H:
        g.add_nodes_from(l)
        g.add_edges_from(itertools.combinations(sorted(set(l)), 2))
    w = 0
    while g.number_of_nodes():
        v = min(g.nodes(), key=lambda u: (g.degree(u), str(u)))
        nb = list(g[v])
        w = max(w, len(nb) + 1)
        g.add_edges_from(itertools.combinations(nb, 2))
        g.remove_node(v)
    return w


# ---------------------------------------------------------------- 0
man = json.load(open(os.path.join(HERE, "manifest.json")))
mism = {r: dg for r, dg in man["parent_bindings"].items()
        if hashlib.sha256(open(os.path.join(ROOT, r), "rb").read()).hexdigest() != dg}
report("0 dependency artifacts bound by hash", not mism, {"parents": len(man["parent_bindings"]), "mismatched": mism})

# ---------------------------------------------------------------- 1 Berman on planar braces
PLANAR = {f"{2 * k}-prism": TL.prism_piece(k) for k in (2, 3, 4, 5, 6)}
PLANAR["truncated octahedron"] = TL.truncated_octahedron_piece()
PLANAR["Omni(K2,3)"] = omni_piece(nx.complete_bipartite_graph(2, 3), [TL.C4], [False], 'o', random.Random(1))
d1, ok1 = {}, True
for name, g in PLANAR.items():
    lines = lines_of(g, TL.C4[0])
    H, pid, lid, lns = TL.as_system(g, TL.C4[0])
    kneg = M.kasteleyn_signing(H)
    per_line = set()
    for L in range(len(H)):
        rows, cols, W = SY.line_face_matrix(g, lines, lns[L])
        A01 = [[W.get((w, k), 0) for k in cols] for w in rows]
        trip = (abs(SY.det(A01)), permanent(A01), AM.amplitude(H, L, kneg))
        per_line.add(trip)
        ok1 &= len(set(trip)) == 1
    col = nx.bipartite.color(g)
    splits = []
    faces4 = [f for f in SY.plane_faces(g) if len(f) == 4]
    for f in faces4:
        for flip in (False, True):
            mp = label_face(g, f, (0, 1, 2, 3), flip, {v: (col[v] if col[TL.C4[0]] == 0 else 1 - col[v]) for v in g})
            S = tuple(sorted(mp, key=mp.get))
            sf = SY.side_faces(SY.plane_faces(g), S)
            dets, pers = [], []
            for key in ("c3F0", "c3F2"):
                rows, cols, W = SY.line_face_matrix(g, lines, S[1], (S[3], sf[key]))
                A = [[W.get((w, k), 0) for k in cols] for w in rows]
                dets.append(abs(SY.det(A)))
                pers.append(permanent(A))
            direct = TL.leaning(g, S)
            splits.append(tuple(dets))
            ok1 &= tuple(dets) == tuple(pers) == direct
    d1[name] = {"lines": len(H), "(|det|, Tutte matchings, direct amplitude) over all lines": sorted(per_line),
                "square faces x labellings": 2 * len(faces4), "leaning splits": {str(k): v for k, v in sorted(collections.Counter(splits).items())}}
report("1 Berman on planar braces: |det| = Tutte matchings = direct count at every line; restricted rows give the leaning splits", ok1, d1)

# ---------------------------------------------------------------- 2 weighted rows
d2, ok2 = {"random weights": {}, "symbolic": {}}, True
rng = random.Random(20261030)
for name in ("truncated octahedron", "10-prism", "12-prism"):
    g = PLANAR[name]
    lines = lines_of(g, TL.C4[0])
    col = nx.bipartite.color(g)
    colp = {v: (col[v] if col[TL.C4[0]] == 0 else 1 - col[v]) for v in g}
    faces4 = [f for f in SY.plane_faces(g) if len(f) == 4]
    disjoint = [f for f in faces4 if not (f & set(TL.C4)) and not any(set(g[v]) & set(TL.C4) for v in f)]
    chosen = []
    for f in disjoint:
        if all(not (f & h) for h in chosen):
            chosen.append(f)
    chosen = chosen[:2]
    kids = [tuple(sorted(label_face(g, f, (0, 1, 2, 3), bool(t % 2), colp).items(), key=lambda kv: kv[1])) for t, f in enumerate(chosen)]
    kids = [tuple(v for v, _ in kv) for kv in kids]
    sf = SY.side_faces(SY.plane_faces(g), TL.C4)
    rows_ok = 0
    for trial in range(4):
        children = [(D, rng.randint(1, 9), rng.randint(1, 9)) for D in kids]
        for key in ("c3F0", "c3F2"):
            rows, cols, W = SY.line_face_matrix(g, lines, TL.C4[1], (TL.C4[3], sf[key]), children)
            A = [[W.get((w, k), 0) for k in cols] for w in rows]
            good = abs(SY.det(A)) == permanent(A)
            ok2 &= good
            rows_ok += good
    d2["random weights"][name] = {"child squares": len(kids), "restricted weighted determinants equal to weighted permanents": f"{rows_ok}/8"}
    syms = sympy.symbols(f"a0:{len(kids)}") + sympy.symbols(f"b0:{len(kids)}")
    children = [(D, syms[t], syms[len(kids) + t]) for t, D in enumerate(kids)]
    signs = set()
    for key in ("c3F0", "c3F2"):
        rows, cols, W = SY.line_face_matrix(g, lines, TL.C4[1], (TL.C4[3], sf[key]), children)
        poly = sympy.Poly(sympy.Matrix([[W.get((w, k), 0) for k in cols] for w in rows]).det(method='berkowitz').expand(), *syms)
        coeffs = poly.coeffs()
        signs |= {c > 0 for c in coeffs}
        d2["symbolic"][f"{name}, lean {key[-2:]}"] = str(poly.as_expr())
    ok2 &= len(signs) == 1
report("2 weighted rows: |det| = the weighted permanent; every coefficient of the determinant in the weights has one sign", ok2, d2)

# ---------------------------------------------------------------- test braces (sections 3 and 4)
BRACES = {}
TRIPLES = [(2, 2, 2), (2, 2, 3), (2, 3, 3), (3, 3, 3), (2, 2, 4), (2, 3, 4), (3, 3, 4), (2, 4, 4), (4, 4, 4), (2, 2, 5), (2, 3, 5)]
for ks in TRIPLES:
    for fl in [(0, 0, 0), (0, 0, 1), (0, 1, 0), (0, 1, 1)]:
        BRACES[f"trisum {ks} {''.join(map(str, fl))}"] = TL.trisum_of([TL.prism_piece(k, bool(f)) for k, f in zip(ks, fl)])
for kA, kQ, kR, fl in [(2, 2, 2, (0, 0, 0)), (3, 3, 2, (0, 0, 0)), (3, 3, 3, (0, 0, 1)), (2, 3, 3, (0, 1, 0)), (3, 2, 3, (1, 0, 0)),
                       (4, 3, 2, (0, 1, 0)), (4, 4, 3, (1, 0, 1))]:
    T1 = TL.trisum_of([TL.two_square_prism(kA, flipD=bool(fl[0])), TL.prism_piece(kQ, bool(fl[1]), sq=TL.D4, tag='q'),
                       TL.prism_piece(kR, bool(fl[2]), sq=TL.D4, tag='r')], sq=TL.D4)
    for k2, k3 in [(2, 2), (2, 3)]:
        BRACES[f"nested {(kA, kQ, kR)} {''.join(map(str, fl))} | {(k2, k3)}"] = TL.trisum_of([T1, TL.prism_piece(k2, False, tag='s'),
                                                                                            TL.prism_piece(k3, True, tag='t')])
S1, S2, S3 = sq('s1'), sq('s2'), sq('s3')
rng = random.Random(7)
for trial in range(6):
    f = [rng.random() < 0.5 for _ in range(12)]
    k = [rng.choice([2, 3, 4]) for _ in range(12)]
    T3 = glue([multi_square_prism(max(k[3], 3), [S2, S3], [f[4], f[5]], 'D'), multi_square_prism(k[5], [S3], [f[7]], 'F'),
               multi_square_prism(k[6], [S3], [f[8]], 'G')], S3)
    T2 = glue([multi_square_prism(max(k[0], 3), [S1, S2], [f[0], f[1]], 'A'), multi_square_prism(k[4], [S2], [f[6]], 'E'), T3], S2)
    BRACES[f"depth-3 chain {trial}"] = glue([T2, multi_square_prism(k[1], [S1], [f[2]], 'B'), multi_square_prism(k[2], [S1], [f[3]], 'C')], S1)
for trial in range(3):
    f = [rng.random() < 0.5 for _ in range(12)]
    G = multi_square_prism(4, [S1, S2, S3], f[:3], 'H')
    for t, S in enumerate([S2, S3]):
        G = glue([G, multi_square_prism(2 + t, [S], [f[3 + t]], f'P{t}'), multi_square_prism(2, [S], [f[5 + t]], f'Q{t}')], S)
    BRACES[f"star {trial}"] = glue([G, multi_square_prism(3, [S1], [f[8]], 'R1'), multi_square_prism(2, [S1], [f[9]], 'R2')], S1)


def first_point(G):
    return TL.C4[0] if TL.C4[0] in G else S1[0]


TREES = {}
for name, G in BRACES.items():
    lines = lines_of(G, first_point(G))
    TREES[name] = (lines,) + SY.trisum_tree(G, lines)

# ---------------------------------------------------------------- 3 the trisum tree
d3, ok3 = {"leaves per brace": collections.Counter(), "all trisectors (braces up to 48 vertices)": {}}, True
for name, G in BRACES.items():
    lines, leaves, squares = TREES[name]
    on4 = SY.four_cycle_vertices(G)
    nodes = sorted(G, key=str)
    idx = {v: i for i, v in enumerate(nodes)}
    adj = [[idx[w] for w in G[v]] for v in nodes]
    good = all(nx.check_planarity(g)[0] and is_brace(g) for g, s in leaves)
    good &= all(not (set(a) & set(b)) for a, b in itertools.combinations(squares, 2))
    good &= all(SY._components(adj, {idx[v] for v in X}, len(nodes)) == 3 and not (set(X) & on4) for X in squares)
    good &= all(sum(set(X) in [set(f) for f in SY.plane_faces(g)] for g, s in leaves if X in s) == 3 for X in squares)
    tree = nx.Graph([(('leaf', i), ('sq', X)) for i, (g, s) in enumerate(leaves) for X in s])
    good &= nx.is_tree(tree) and all(tree.degree(('sq', X)) == 3 for X in squares) and len(leaves) == 2 * len(squares) + 1
    ok3 &= good
    d3["leaves per brace"][len(leaves)] += 1
    if G.number_of_nodes() <= 48 and name.startswith(("trisum (2, 2, 2) 000", "trisum (3, 3, 3) 001", "nested (2, 2, 2)", "star 0")):
        alltri = SY.all_trisectors(G, lines)
        d3["all trisectors (braces up to 48 vertices)"][name] = {"vertices": G.number_of_nodes(), "trisectors": len(alltri)}
        ok3 &= all(not (X & on4) for X in alltri) and 0 < len(alltri) <= G.number_of_nodes() - 5
d3["leaves per brace"] = dict(d3["leaves per brace"])
report("3 the trisum tree: planar brace leaves, disjoint trisectors on no 4-cycle, faces of their leaves, a tree", ok3, d3)

# ---------------------------------------------------------------- 4 brace amplitudes by the tree against direct counts
d4, ok4 = {}, True
unswapped_wrong = 0
for name, G in BRACES.items():
    lines, leaves, squares = TREES[name]
    a = SY.tree_amplitude(leaves, squares, lines)
    roots = {SY.tree_amplitude(leaves, squares, lines, root=r) for r in range(len(squares))}
    pts = set(G) - lines
    aT = SY.tree_amplitude(*SY.trisum_tree(G, pts), pts)
    direct = direct_amplitudes(G, first_point(G))
    au = SY.tree_amplitude(leaves, squares, lines, swapped=False)
    unswapped_wrong += au not in direct
    d4[name] = {"vertices": G.number_of_nodes(), "planar pieces": len(leaves), "tree": a, "direct": sorted(direct)}
    ok4 &= direct == {a} and roots == {a} and aT == a
report("4 brace amplitudes: the tree (any root square, either colour class as lines) equals the direct count", ok4,
       {"braces": len(d4), "amplitudes": d4})

# ---------------------------------------------------------------- 5 the pipeline on three-fold spaces
d5, ok5 = {}, True
F7 = T.FANO
SPACES = {"tripod core (22)": M.decorate([(0, 1, 1), (0, 2, 2), (0, 3, 3), (1, 2, 3)], []),
          "twisted cube (43)": M.decorate(M.K4, M.kasteleyn_signing(M.K4))}
for glue_name in ("hexagonal prism", "truncated octahedron"):
    Pg = M.cubic_planar_bipartite(glue_name)
    SPACES[f"{glue_name} glue"] = M.decorate(Pg, M.kasteleyn_signing(Pg))
SPACES["trisum of three cubes glue"] = M.decorate([(0, 1, 2), (0, 1, 3), (0, 4, 5), (1, 6, 7), (2, 6, 8), (2, 7, 9), (3, 4, 6), (3, 5, 7),
                                                   (4, 8, 8), (5, 9, 9)], [(0, 0)])
for name in ("trisum (2, 3, 3) 001", "nested (2, 2, 2) 000 | (2, 3)"):
    Hc, pid, lid, lns = TL.as_system(BRACES[name], TL.C4[0])
    neg = few_negations(Hc, TL.pfaffian_signing(Hc)[0])
    SPACES[f"{name} glue"] = M.decorate(Hc, neg)
for name, H in SPACES.items():
    a, kinds = SY.space_amplitude(H)
    direct = {AM.amplitude(H, L) for L in (0, len(H) // 2, len(H) - 1)}
    d5[name] = {"points": len(H), "braces": dict(collections.Counter(kinds)), "pipeline": a, "direct": sorted(direct),
                "colourable": AM.colourable(H)}
    ok5 &= direct == {a} and not d5[name]["colourable"]
report("5 the pipeline on three-fold spaces: product over braces (trees for non-planar ones) = direct count", ok5, d5)

# ---------------------------------------------------------------- 6 scale
d6, ok6 = {"against direct counts": {}, "beyond elimination": {}}, True
rng = random.Random(3)
MAPS = {"K4": nx.complete_graph(4), "cube": nx.hypercube_graph(3), "octahedron": nx.octahedral_graph(), "dodecahedron": nx.dodecahedral_graph(),
        "icosahedron": nx.icosahedral_graph()}
BIG = {"Omni(dodecahedron) x 3": glue([omni_piece(MAPS["dodecahedron"], [S1], [f], t, rng) for t, f in zip("abc", (0, 0, 1))], S1),
       "Omni(icosahedron), Omni(cube), Omni(octahedron)": glue([omni_piece(MAPS[m], [S1], [f], t, rng)
                                                                for m, t, f in zip(("icosahedron", "cube", "octahedron"), "abc", (0, 1, 0))], S1)}
T3 = glue([omni_piece(MAPS["icosahedron"], [S2, S3], [0, 0], 'B', rng), omni_piece(MAPS["cube"], [S3], [1], 'C', rng),
           omni_piece(MAPS["K4"], [S3], [0], 'D', rng)], S3)
T2 = glue([omni_piece(MAPS["dodecahedron"], [S1, S2], [0, 1], 'A', rng), T3, omni_piece(MAPS["octahedron"], [S2], [0], 'E', rng)], S2)
BIG["depth-3 chain of omnitruncations"] = glue([T2, omni_piece(MAPS["dodecahedron"], [S1], [1], 'F', rng),
                                                omni_piece(MAPS["K4"], [S1], [0], 'G', rng)], S1)
for name, G in BIG.items():
    lines = lines_of(G, S1[0])
    t0 = time.time()
    leaves, squares = SY.trisum_tree(G, lines)
    a = SY.tree_amplitude(leaves, squares, lines)
    secs = round(time.time() - t0, 2)
    neg = tree_signing(leaves, lines)
    H, pid, lid, lns = TL.as_system(G, S1[0])
    negi = [(lid[l], pid[p]) for e in neg for l in e if l in lines for p in e if p not in lines]
    direct = {AM.amplitude(H, L, negi) for L in (0, len(H) - 1)}
    roots = {SY.tree_amplitude(leaves, squares, lines, root=r) for r in range(len(squares))}
    d6["against direct counts"][name] = {"vertices": G.number_of_nodes(), "planar pieces": len(leaves), "tree": a, "seconds": secs,
                                         "glued Kasteleyn signing colourable": AM.colourable(H, negi), "direct": sorted(direct)}
    ok6 &= direct == {a} and roots == {a} and not d6["against direct counts"][name]["glued Kasteleyn signing colourable"]
for k in (5, 7, 9):
    grid = nx.grid_2d_graph(k, k)
    G = glue([omni_piece(grid, [S1], [f], t, rng) for t, f in zip("abc", (0, 0, 1))], S1)
    lines = lines_of(G, S1[0])
    t0 = time.time()
    leaves, squares = SY.trisum_tree(G, lines)
    a = SY.tree_amplitude(leaves, squares, lines)
    secs = round(time.time() - t0, 1)
    pts = set(G) - lines
    aT = SY.tree_amplitude(*SY.trisum_tree(G, pts), pts)
    lap = nx.laplacian_matrix(grid, nodelist=sorted(grid)).toarray().tolist()
    tau = SY.det([row[1:] for row in lap[1:]])
    rhos = {sum(SY.piece_split(g, lines, squares[0])) for g, s in leaves}
    H, pid, lid, lns = TL.as_system(G, S1[0])
    w = elimination_width(H)
    d6["beyond elimination"][f"Omni({k}x{k} grid) x 3"] = {"vertices": G.number_of_nodes(), "amplitude digits": len(str(a)), "seconds": secs,
                                                          "transposed agrees": aT == a, "each piece's alpha + beta = spanning trees of the grid":
                                                          rhos == {tau}, "elimination width": w}
    ok6 &= aT == a and rhos == {tau} and w >= 17
report("6 scale: exact against direct counts to 480 vertices; omnitruncated grids to 1720 vertices", ok6, d6)

# ---------------------------------------------------------------- 7 controls
ctrl = {}
ctrl["the unswapped weights on c1's row give a wrong amplitude on some nested braces"] = unswapped_wrong > 0
name = "depth-3 chain 0"
lines, leaves, squares = TREES[name]
at = {X: [i for i, (g, s) in enumerate(leaves) if X in s] for X in squares}
X0 = squares[0]
plain = []
for i in at[X0]:
    g, s = leaves[i]
    plain.append(SY.piece_split(g, lines, X0, [(D, 1, 1) for D in s if D != X0]))
ctrl["dropping the children's weights (all weights 1) gives a wrong amplitude"] = SY.law(plain) != d4[name]["tree"]
G = BRACES["trisum (2, 3, 4) 000"]
lines, leaves, squares = TREES["trisum (2, 3, 4) 000"]
sp = [SY.piece_split(g, lines, squares[0]) for g, s in leaves]
i = next(i for i in range(3) if sp[i][0] != sp[i][1])
sp[i] = sp[i][::-1]
ctrl["reading one asymmetric piece's split from the wrong side breaks the law"] = SY.law(sp) != d4["trisum (2, 3, 4) 000"]["tree"]
K33 = nx.complete_bipartite_graph(3, 3)
HEA = nx.Graph([(('P', p), ('L', i)) for i, l in enumerate(F7) for p in l])
for gname, gg in (("K3,3", K33), ("the Heawood graph", HEA)):
    try:
        SY.trisum_tree(gg, lines_of(gg, next(iter(sorted(gg, key=str)))))
        ctrl[f"{gname} (non-planar, no square trisector) is refused by the tree"] = False
    except ValueError:
        ctrl[f"{gname} (non-planar, no square trisector) is refused by the tree"] = True
report("7 controls fire", all(ctrl.values()), ctrl)

out["ok"] = ok_all
out["seconds"] = round(time.time() - T0, 1)
print("ALL OK" if ok_all else "SOME CHECK FAILED", out["seconds"], "s")
if "--write" in sys.argv:
    json.dump({"schema_version": 1, "artifact_id": "SEYMOUR-COUNT-20261030-001B-P001", "status": "Proved" if ok_all else "Failed",
               "checks": out}, open(os.path.join(HERE, "result.json"), "w"), indent=1, default=str)
sys.exit(0 if ok_all else 1)
