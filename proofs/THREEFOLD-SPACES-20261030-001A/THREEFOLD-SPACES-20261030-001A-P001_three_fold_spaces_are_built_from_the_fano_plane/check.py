"""Checks for THREEFOLD-SPACES-20261030-001A-P001 (the knot's three-fold spaces are built from the Fano plane).

  0 dependency artifacts bound by the hashes recorded in manifest.json
  1 the dictionary on instances: the Fano plane and its compositions with 13 and 19 points are cubic, connected, not 2-colourable,
    minimally so, sign-nonsingular (|det| = per), and their digraphs (n <= 13) have no even dicycle; on 300 random cubic triple systems
    with 7 to 11 points, 2-colourable <=> not sign-nonsingular, and (n <= 9) <=> some digraph has an even dicycle
  2 the splice calculus: tight cuts of the 13-point splice; the sign of every perfect matching factorizes across the cut (also on a
    2-colourable splice with mixed signs); Fano minus a line forces its line monochromatic, Fano minus a point forces the three completed
    lines to act as one line
  3 closure and infinitude: Fano compositions with 7, 13, 19, 25 and 49 points are not 2-colourable; the dual gadgets with 7, 13 and 19
    triangles (from point and line splices) are exact at the knot angle with lambda(0) = 5, 25, 125
  4 the reduction lemma, partial: every signing of the Heawood graph with one negative edge is not sign-nonsingular (twisted Fano planes
    are 2-colourable); planar cubic bipartite examples (cube, hexagonal prism) have no sign-nonsingular signing with at most two negative
    edges
  5 the premise of the previous recommendation is false: the 13-point splice is a linear connected cubic triple system, not 2-colourable,
    not the Fano plane
  6 mixed gluings: among all gadgets with at most five triangles, those whose contacts are all two-fold with one base incidence or
    three-fold with odd base count have no two-fold contact (the base-slot count forces it)
  7 controls that must fire
Run: .venv/bin/python -B check.py [--write]   (numpy, sympy, networkx, python-sat; about a minute)"""
import hashlib, itertools, json, os, random, sys, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
SS_A = os.path.join(ROOT, "proofs/SPACE-SELECTION-20261030-001A/SPACE-SELECTION-20261030-001A-P001_the_gadget_criterion")
sys.path.insert(0, HERE)
sys.path.insert(0, SS_A)
import threefold_lib as T  # noqa: E402
import gadget_lib as G  # noqa: E402

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
P13 = T.point_splice(F, 0, F, F[0])
L13 = T.line_splice(F, F[0], F, 0)
P19 = T.point_splice(P13, 0, F, F[0])
L19 = T.line_splice(P13, P13[0], F, 0)
COMP = {"Fano": F, "point splice 13": P13, "line splice 13": L13, "point splice 19": P19, "line splice 19": L19}

# ---------------------------------------------------------------- 1 the dictionary
d1 = {}
ok1 = True
for name, H in COMP.items():
    n = T.npoints(H)
    s, dt, pm = T.sns(H)
    minimal = all(T.colourable_sat([l for j, l in enumerate(H) if j != i]) for i in range(len(H)))
    rec = {"points": n, "cubic": T.is_cubic(H), "connected": T.connected(H), "2-colourable": T.colourable_sat(H), "minimal": minimal,
           "det": dt, "per": pm}
    if n <= 13:
        M = T.perfect_matchings(H)[0]
        rec["even dicycle"] = T.has_even_dicycle(T.digraph(H, M))
    ok1 &= rec["cubic"] and rec["connected"] and not rec["2-colourable"] and minimal and s and not rec.get("even dicycle", False)
    d1[name] = rec


def random_cubic(n, rng):
    for _ in range(2000):
        slots = [p for p in range(n) for _ in range(3)]
        rng.shuffle(slots)
        H = [tuple(sorted(slots[3 * i:3 * i + 3])) for i in range(n)]
        if all(len(set(l)) == 3 for l in H) and T.connected(H):
            return H
    return None


rng = random.Random(20261030)
agree_sns, agree_dic, tested, tested_dic = 0, 0, 0, 0
for k in range(300):
    n = 7 + k % 5
    H = random_cubic(n, rng)
    if H is None:
        continue
    col = T.colourable(H)
    s = T.sns(H)[0]
    tested += 1
    agree_sns += int(col == (not s))
    if n <= 9:
        evens = [T.has_even_dicycle(T.digraph(H, M)) for M in T.perfect_matchings(H)[:3]]
        tested_dic += 1
        agree_dic += int(all(e == col for e in evens))
d1["random cubic systems: colourable <=> not SNS"] = (agree_sns, tested)
d1["random cubic systems n <= 9: colourable <=> even dicycle (three matchings each)"] = (agree_dic, tested_dic)
ok1 &= agree_sns == tested and agree_dic == tested_dic and tested >= 250
report("1 the dictionary: not 2-colourable = minimal = sign-nonsingular = no even dicycle", ok1, d1)

# ---------------------------------------------------------------- 2 the splice calculus


def splice_with_maps(H1, t, H2, jM):
    """point splice keeping track of lines and points; returns (H, cut lines, piece maps)"""
    M = H2[jM]
    lines, keys = [], []
    through = [i for i, l in enumerate(H1) if t in l]
    for i, l in enumerate(H1):
        if t not in l:
            lines.append([('1', p) for p in l]); keys.append(('1', i))
    for k, i in enumerate(through):
        lines.append([('1', p) for p in H1[i] if p != t] + [('2', M[k])]); keys.append(('1*', i, k))
    for j, l in enumerate(H2):
        if j != jM:
            lines.append([('2', q) for q in l]); keys.append(('2', j))
    pts = sorted({p for l in lines for p in l})
    pid = {p: a for a, p in enumerate(pts)}
    H = [tuple(sorted(pid[p] for p in l)) for l in lines]
    return H, keys, pts, pid, through, M


def sign_of(matching_line_to_point, nl):
    return T.perm_sign(list(matching_line_to_point[i] for i in range(nl)))


def factorization(H1, t, H2, jM):
    H, keys, pts, pid, through, M = splice_with_maps(H1, t, H2, jM)
    mats = T.perfect_matchings(H)
    n1, n2 = len(H1), len(H2)
    pidx1 = {p: p for p in range(T.npoints(H1))}
    res, ref = [], None
    for mu in mats:
        m1, m2 = {}, {}
        cut = None
        for li, key in enumerate(keys):
            p = pts[mu[li]]
            if key[0] == '1':
                m1[key[1]] = p[1]
            elif key[0] == '2':
                m2[key[1]] = p[1]
            else:
                _, i, k = key
                if p == ('2', M[k]):
                    cut = k
                    m1[i] = t
                else:
                    m1[i] = p[1]
        m2[jM] = M[cut]
        sH = T.perm_sign(list(mu))
        s1 = sign_of(m1, n1)
        s2 = sign_of(m2, n2)
        res.append((sH, s1, s2, cut))
    r0 = res[0]
    ok = all((a * r0[0]) == (b * r0[1]) * (c * r0[2]) for a, b, c, _ in res)
    per_cut = {}
    for a, b, c, k in res:
        per_cut.setdefault(k, set()).add((b * r0[1], c * r0[2]))
    return ok, len(res), {k: sorted(v) for k, v in per_cut.items()}


d2 = {}
K43 = [(1, 2, 3), (0, 2, 3), (0, 1, 3), (0, 1, 2)]            # all triples of four points: cubic, 2-colourable (its incidence graph is the cube)
fact_fano = factorization(F, 0, F, 0)
fact_mixed = factorization(K43, 0, F, 0)
fact_mixed2 = factorization(F, 0, K43, 0)
d2["sign factorization, Fano o Fano: holds, matchings, (piece signs) per cut edge"] = fact_fano
d2["sign factorization, K4^(3) o Fano and Fano o K4^(3) (2-colourable, mixed signs): holds"] = (fact_mixed[0], fact_mixed[1], fact_mixed2[0], fact_mixed2[1])
d2["tight cuts of the 13-point splice (point-type shores)"] = [(len(X), len(P)) for X, P in T.tight_cuts(P13)]
fm = [l for l in F if l != F[0]]
props = [c for c in itertools.product((0, 1), repeat=7) if all(not (c[a] == c[b] == c[e]) for a, b, e in fm)]
d2["Fano minus a line: proper colourings, all make the line monochromatic"] = (len(props), all(c[0] == c[1] == c[2] for c in props))
# Fano minus the point 0: the three pairs (1,2), (3,4), (5,6) completed by a, b, c act as the line (a, b, c)
acts = True
for abc in itertools.product((0, 1), repeat=3):
    ext = False
    for c in itertools.product((0, 1), repeat=6):
        col = dict(zip(range(1, 7), c))
        if not all(not (col[x] == col[y] == col[z]) for x, y, z in [l for l in F if 0 not in l]):
            continue
        if all(not (col[x] == col[y] == v) for (x, y), v in zip([(1, 2), (3, 4), (5, 6)], abc)):
            ext = True
            break
    acts &= ext == (len(set(abc)) > 1)
d2["Fano minus a point acts as a line on its three completions"] = acts
ok2 = fact_fano[0] and all(v == [(1, 1)] for v in fact_fano[2].values()) and fact_mixed[0] and fact_mixed2[0] and \
    d2["tight cuts of the 13-point splice (point-type shores)"] == [(6, 7)] and d2["Fano minus a line: proper colourings, all make the line monochromatic"][1] and acts
report("2 the splice calculus: signs factorize across tight cuts; Fano pieces act as points and lines", ok2, d2)

# ---------------------------------------------------------------- 3 closure and infinitude
d3 = {}
P25 = T.point_splice(P19, 0, F, F[0])
# a composition of eight Fano planes (49 points): seven successive point splices
TOWER = F
for _ in range(7):
    TOWER = T.point_splice(TOWER, 0, F, F[0])
d3["point counts"] = {"P25": T.npoints(P25), "seven-fold": T.npoints(TOWER)}
d3["not 2-colourable (SAT): 25-point, 49-point"] = (not T.colourable_sat(P25), not T.colourable_sat(TOWER))
d3["cubic and connected: 25-point, 49-point"] = (T.is_cubic(P25) and T.connected(P25), T.is_cubic(TOWER) and T.connected(TOWER))


def knot_exact(cx):
    W = G.law_batch('sine', (0,))
    R = G.fast_values(cx, W)[0]
    lam = int(R[0, 0, 1])
    return bool(lam != 0 and all(int(R[x]) == lam * G.FAM['sine'](x, 0) for x in G.TU)), lam


gad = {}
for name, H in (("Fano", F), ("point splice 13", P13), ("line splice 13", L13), ("point splice 19", P19)):
    cx = T.gadget_from(H, H[0])
    gad[name] = (len(cx[1]), knot_exact(cx))
d3["dual gadgets: triangles, (knot exact, lambda(0))"] = gad
ok3 = all(d3["not 2-colourable (SAT): 25-point, 49-point"]) and all(d3["cubic and connected: 25-point, 49-point"]) and \
    d3["point counts"] == {"P25": 25, "seven-fold": 49} and \
    [v[1] for v in gad.values()] == [(True, 5), (True, 25), (True, 25), (True, 125)]
report("3 Fano compositions give knot spaces with 7 + 6k triangles", ok3, d3)

# ---------------------------------------------------------------- 4 the reduction lemma, partial
d4 = {}
flips = [(i, p) for i, l in enumerate(F) for p in l]
twisted_sns = sum(1 for f in flips if T.sns(F, [f])[0])
twisted_col = sum(1 for f in flips if T.colourable(F, twist=f))
d4["Fano with one negated incidence: SNS cases, colourable cases (of 21)"] = (twisted_sns, twisted_col)


def bip_to_H(points, lines, adj):
    pid = {p: i for i, p in enumerate(points)}
    return [tuple(sorted(pid[q] for q in adj[l])) for l in lines]


# the cube: points = even vertices of Q3, lines = odd vertices
Q3 = K43
U = [('u', i) for i in range(6)]
Vv = [('v', i) for i in range(6)]
edges = [(('u', i), ('u', (i + 1) % 6)) for i in range(6)] + [(('v', i), ('v', (i + 1) % 6)) for i in range(6)] + [(('u', i), ('v', i)) for i in range(6)]
colr = {('u', i): i % 2 for i in range(6)}
colr.update({('v', i): (i + 1) % 2 for i in range(6)})
adj = {}
for a, b in edges:
    adj.setdefault(a, []).append(b)
    adj.setdefault(b, []).append(a)
pts = [v for v in colr if colr[v] == 0]
lns = [v for v in colr if colr[v] == 1]
PRISM = bip_to_H(pts, lns, adj)
planar_ok = {}
for name, H in (("cube", Q3), ("hexagonal prism", PRISM)):
    inc = [(i, p) for i, l in enumerate(H) for p in l]
    found = 0
    for k in (0, 1, 2):
        for S in itertools.combinations(inc, k):
            if T.sns(H, list(S))[0]:
                found += 1
    planar_ok[name] = (T.is_cubic(H), found)
d4["planar cubic bipartite examples: (cubic, SNS signings with <= 2 negative edges)"] = planar_ok
ok4 = twisted_sns == 0 and twisted_col == 21 and all(v == (True, 0) for v in planar_ok.values())
report("4 one negative edge never makes the Heawood graph or planar examples sign-nonsingular", ok4, d4)

# ---------------------------------------------------------------- 5 the false premise
lin13 = all(len(set(a) & set(b)) <= 1 for a, b in itertools.combinations(P13, 2))
d5 = {"13-point splice: linear, cubic, connected, not 2-colourable": (lin13, T.is_cubic(P13), T.connected(P13), not T.colourable(P13))}
report("5 the uniqueness premise is false at 13 points", all(d5["13-point splice: linear, cubic, connected, not 2-colourable"]), d5)

# ---------------------------------------------------------------- 6 mixed gluings
d6 = {}
ok6 = True
for n in (1, 3, 4, 5):
    pure, with_lock = 0, 0
    for key in G.gadgets(n):
        cx = G.complex_of(n, key)
        inc = G.incidences(cx)
        kinds = []
        for v, lst in inc.items():
            if v in cx[2]:
                continue
            b = sum(1 for t, r in lst if r == 0)
            if len(lst) == 2 and b == 1:
                kinds.append('lock')
            elif len(lst) == 3 and b % 2 == 1:
                kinds.append('knot')
            else:
                kinds.append('free')
        if 'free' not in kinds:
            pure += 1
            with_lock += int('lock' in kinds)
    d6[f"n={n}: gadgets with only locks and odd three-fold contacts, of which with a lock"] = (pure, with_lock)
    ok6 &= with_lock == 0
ok6 &= [v[0] for v in d6.values()] == [1, 2, 24, 256]
report("6 a gluing of phase locks and phase knots has no locks", ok6, d6)

# ---------------------------------------------------------------- 7 controls
ctrl = {}
ctrl["K4^(3) is 2-colourable and not SNS"] = T.colourable(K43) and not T.sns(K43)[0]
ctrl["removing a line from the 13-point splice makes it 2-colourable"] = T.colourable([l for j, l in enumerate(P13) if j != 5])
ctrl["the gadget dual to a 2-colourable cubic system (K4^(3), 4 triangles) is not exact at the knot"] = not knot_exact(T.gadget_from(K43, K43[0]))[0]
ctrl["a 2-colourable random cubic system on 13 points is not SNS"] = (lambda H: H is not None and T.colourable(H) and not T.sns(H)[0])(random_cubic(13, random.Random(5)))
report("7 controls fire", all(ctrl.values()), ctrl)

out["ok"] = ok_all
out["seconds"] = round(time.time() - T0, 1)
print("ALL OK" if ok_all else "SOME CHECK FAILED", out["seconds"], "s")
if "--write" in sys.argv:
    json.dump({"schema_version": 1, "artifact_id": "THREEFOLD-SPACES-20261030-001A-P001", "status": "Proved" if ok_all else "Failed",
               "checks": out}, open(os.path.join(HERE, "result.json"), "w"), indent=1, default=str)
sys.exit(0 if ok_all else 1)
