"""Checks for THREEFOLD-SPACES-20261030-001B-P001 (exhaustive classification of small three-fold spaces).

  0 dependency artifacts bound by the hashes recorded in manifest.json
  1 SAT with lexicographic symmetry breaking (CaDiCaL): a minimally non-2-colourable cubic triple system exists on n points for
    n = 3..13 only at n = 7 and n = 13; with one twisted incidence, for no n = 3..13
  2 replays: the same answers with a second solver (Glucose 4) for n = 3..12 (untwisted and twisted), and without symmetry breaking
    (CaDiCaL) for n = 3..9
  3 enumeration: all symmetry-broken solutions at n = 7 and n = 13, up to isomorphism of incidence graphs: one class each, the Fano plane
    and the Fano splice (point and line splices are isomorphic)
  4 the knot side: the 13-point system has three orbits of lines under its automorphisms; for each orbit as corner line and each of the
    six corner placements, the dual three-fold gadget (13 triangles) is exact at the knot with lambda(0) = 25
  5 phase-pure gadgets (contacts two-fold with one base incidence or three-fold with odd base count) up to six triangles: 1, 0, 2, 24,
    256, 3248, none with a lock and none exact at the knot (they need seven triangles)
  6 controls that must fire
Run: .venv/bin/python -B check.py [--write]   (python-sat, networkx; about ten minutes)"""
import collections, hashlib, itertools, json, os, sys, time
import networkx as nx
from pysat.solvers import Solver

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
TA = os.path.join(ROOT, "proofs/THREEFOLD-SPACES-20261030-001A/THREEFOLD-SPACES-20261030-001A-P001_three_fold_spaces_are_built_from_the_fano_plane")
SS_A = os.path.join(ROOT, "proofs/SPACE-SELECTION-20261030-001A/SPACE-SELECTION-20261030-001A-P001_the_gadget_criterion")
sys.path.insert(0, HERE)
sys.path.insert(0, TA)
sys.path.insert(0, SS_A)
import sat_lib as S  # noqa: E402
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


def solve(n, twisted, lex, solver):
    cnf, pool, x = S.build(n, twisted, lex)
    t = time.time()
    with Solver(name=solver, bootstrap_with=cnf.clauses) as s:
        ok = s.solve()
        H = S.decode(s.get_model(), x, n) if ok else None
    return ok, H, round(time.time() - t, 1)


# ---------------------------------------------------------------- 1 the main certificates
d1 = {"untwisted": {}, "twisted": {}}
ANS = {}
for twisted in (False, True):
    for n in range(3, 14):
        ok, H, sec = solve(n, twisted, True, 'cadical153')
        ANS[(twisted, n)] = ok
        d1["twisted" if twisted else "untwisted"][n] = ("SAT" if ok else "UNSAT", sec)
        if ok:
            assert T.is_cubic(H) and not T.colourable(H, twist=(0, 0) if twisted else None)
ok1 = all(ANS[(False, n)] == (n in (7, 13)) for n in range(3, 14)) and not any(ANS[(True, n)] for n in range(3, 14))
report("1 non-colourable cubic triple systems exist only on 7 and 13 points (n <= 13); twisted ones on none", ok1, d1)

# ---------------------------------------------------------------- 2 replays
d2 = {"Glucose 4 with symmetry breaking": {}, "CaDiCaL without symmetry breaking": {}}
ok2 = True
for twisted in (False, True):
    for n in range(3, 13):
        ok, H, sec = solve(n, twisted, True, 'glucose4')
        d2["Glucose 4 with symmetry breaking"][f"{'tw' if twisted else 'un'} {n}"] = ("SAT" if ok else "UNSAT", sec)
        ok2 &= ok == ANS[(twisted, n)]
    for n in range(3, 10):
        ok, H, sec = solve(n, twisted, False, 'cadical153')
        d2["CaDiCaL without symmetry breaking"][f"{'tw' if twisted else 'un'} {n}"] = ("SAT" if ok else "UNSAT", sec)
        ok2 &= ok == ANS[(twisted, n)]
report("2 the answers replay with a second solver and without symmetry breaking", ok2, d2)

# ---------------------------------------------------------------- 3 enumeration at 7 and 13


def bgraph(H):
    g = nx.Graph()
    for i, l in enumerate(H):
        g.add_node(('L', i), kind='L')
        for p in l:
            g.add_node(('P', p), kind='P')
            g.add_edge(('L', i), ('P', p))
    return g


nm = lambda a, b: a['kind'] == b['kind']  # noqa: E731
F = T.FANO
P13 = T.point_splice(F, 0, F, F[0])
L13 = T.line_splice(F, F[0], F, 0)
d3 = {}
classes = {}
for n in (7, 13):
    cnf, pool, x = S.build(n, False, True)
    reps, cls = 0, []
    with Solver(name='cadical153', bootstrap_with=cnf.clauses) as s:
        while s.solve():
            model = s.get_model()
            H = S.decode(model, x, n)
            reps += 1
            g = bgraph(H)
            if not any(nx.is_isomorphic(g, c, node_match=nm) for c in cls):
                cls.append(g)
            m = set(v for v in model if v > 0)
            s.add_clause([-x(l, p) if x(l, p) in m else x(l, p) for l in range(n) for p in range(n)])
    classes[n] = cls
    d3[f"n = {n}: symmetry-broken solutions, isomorphism classes"] = (reps, len(cls))
d3["n = 7 class is the Fano plane"] = nx.is_isomorphic(classes[7][0], bgraph(F), node_match=nm)
d3["n = 13 class is the point splice; point splice ~ line splice"] = (nx.is_isomorphic(classes[13][0], bgraph(P13), node_match=nm),
                                                                      nx.is_isomorphic(bgraph(P13), bgraph(L13), node_match=nm))
ok3 = len(classes[7]) == 1 and len(classes[13]) == 1 and d3["n = 7 class is the Fano plane"] and all(d3["n = 13 class is the point splice; point splice ~ line splice"])
report("3 on 7 and 13 points the non-colourable cubic triple system is unique: the Fano plane and the Fano splice", ok3, d3)

# ---------------------------------------------------------------- 4 the knot side at 13
g13 = bgraph(P13)
autos = list(nx.algorithms.isomorphism.GraphMatcher(g13, g13, node_match=nm).isomorphisms_iter())
orbits = []
seen = set()
for i in range(len(P13)):
    if i in seen:
        continue
    orb = {a[('L', i)][1] for a in autos}
    seen |= orb
    orbits.append(sorted(orb))


def knot_exact(cx):
    W = G.law_batch('sine', (0,))
    R = G.fast_values(cx, W)[0]
    lam = int(R[0, 0, 1])
    return bool(lam != 0 and all(int(R[x]) == lam * G.FAM['sine'](x, 0) for x in G.TU)), lam


res4 = {}
ok4 = True
for orb in orbits:
    L0 = P13[orb[0]]
    vals = set()
    for order in itertools.permutations(range(3)):
        cx = T.gadget_from(P13, L0, order)
        e, lam = knot_exact(cx)
        ok4 &= e
        vals.add(lam)
    res4[f"orbit of line {orb[0]} (size {len(orb)})"] = sorted(vals)
d4 = {"automorphisms of the 13-point system": len(autos), "line orbits": [len(o) for o in orbits], "lambda(0) per corner-line orbit (6 placements)": res4}
ok4 &= sorted(len(o) for o in orbits) == [3, 4, 6] and all(v == [25] for v in res4.values())
report("4 every corner line of the 13-point system gives knot-exact three-fold gadgets", ok4, d4)

# ---------------------------------------------------------------- 5 phase-pure gadgets up to six triangles


def partitions_pp(slots):
    found = []

    def rec(i, blocks):
        if i == len(slots):
            if all(len(b) in (2, 3) for b in blocks):
                for b in blocks:
                    nb = sum(1 for t, r in b if r == 0)
                    if (len(b) == 2 and nb != 1) or (len(b) == 3 and nb % 2 == 0):
                        return
                found.append([tuple(b) for b in blocks])
            return
        if sum(1 for b in blocks if len(b) == 1) > len(slots) - i:
            return
        s = slots[i]
        for b in blocks:
            if len(b) < 3 and all(x[0] != s[0] for x in b):
                b.append(s)
                rec(i + 1, blocks)
                b.pop()
        blocks.append([s])
        rec(i + 1, blocks)
        blocks.pop()
    rec(0, [])
    return found


d5 = {}
ok5 = True
counts = []
for n in (1, 2, 3, 4, 5, 6):
    keys = set()
    for tB in range(min(n, 2)):
        for tC in range(min(n, 3)):
            if tC > tB + 1:
                continue
            slots = [(t, r) for t in range(n) for r in range(3) if (t, r) not in {(0, 0), (tB, 1), (tC, 2)}]
            for blocks in partitions_pp(slots):
                if G.connected(n, blocks):
                    keys.add(G.canonical(n, tB, tC, blocks))
    locks = exact = 0
    for key in keys:
        cx = G.complex_of(n, key)
        inc = G.incidences(cx)
        locks += int(any(len(l) == 2 for v, l in inc.items() if v not in cx[2]))
        exact += int(n > 1 and knot_exact(cx)[0])
    counts.append(len(keys))
    d5[f"n={n}"] = {"phase-pure gadgets": len(keys), "with a lock": locks, "exact at the knot (n > 1)": exact}
    ok5 &= locks == 0 and exact == 0
ok5 &= counts == [1, 0, 2, 24, 256, 3248]
report("5 phase-pure gadgets up to six triangles: no locks, none exact at the knot", ok5, d5)

# ---------------------------------------------------------------- 6 controls
ctrl = {}
for n in (8, 9):
    cnf, pool, x = S.build(n, False, True, noncolour=False)
    with Solver(name='cadical153', bootstrap_with=cnf.clauses) as s:
        ctrl[f"without the non-colourability clauses the encoding is satisfiable at n = {n}"] = s.solve()
ctrl["the encoding finds the Fano plane at n = 7 with the twist removed but not with it"] = ANS[(False, 7)] and not ANS[(True, 7)]
ctrl["a 2-colourable cubic system's dual gadget is not exact"] = not knot_exact(T.gadget_from([(1, 2, 3), (0, 2, 3), (0, 1, 3), (0, 1, 2)], (1, 2, 3)))[0]
report("6 controls fire", all(ctrl.values()), ctrl)

out["ok"] = ok_all
out["seconds"] = round(time.time() - T0, 1)
print("ALL OK" if ok_all else "SOME CHECK FAILED", out["seconds"], "s")
if "--write" in sys.argv:
    json.dump({"schema_version": 1, "artifact_id": "THREEFOLD-SPACES-20261030-001B-P001", "status": "Proved" if ok_all else "Failed",
               "checks": out}, open(os.path.join(HERE, "result.json"), "w"), indent=1, default=str)
sys.exit(0 if ok_all else 1)
