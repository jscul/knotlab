"""Checks for THREEFOLD-SPACES-20261030-001C-P001 (odd cycles of Fano planes: beyond Fano compositions).

  0 dependency artifacts bound by the hashes recorded in manifest.json
  1 the erratum for ticket A, Theorem 4: the 27-point splice of two twisted 2-cycles is a linear connected cubic triple system that is not
    2-colourable and not a Fano composition (27 is not 1 mod 6); the 14-point twisted system has a tight cut whose contraction repeats a
    point in a line, which A's induction did not allow
  2 the block lemma: Fano minus a line forces its three ports to one colour and allows both colours
  3 cycles of k Fano blocks (k = 1..7): linear, connected, cubic on 7k points; not 2-colourable iff k is odd, as the core x_i != x_(i+1)
    predicts
  4 twisted cycles: one connecting line twisted at its single port turns that inequality into an equality; not 2-colourable iff k is
    even (k = 1..6); the twisted 2-cycle is isomorphic to the system found by SAT at 14 points, which is sign-nonsingular with its twist
    (|det| = per = 320); ticket B: no twisted system on at most 13 points
  5 the knot side: the dual gadgets of the 3-cycle (21 triangles) are exact at the knot (lambda(0) = 125); the 5-cycle (35 points) and the
    27-point system satisfy the duality's conditions for every corner line (not 2-colourable; 2-colourable after deleting any line)
  6 controls that must fire
Run: .venv/bin/python -B check.py [--write]   (python-sat, networkx, numpy, sympy; about a minute)"""
import hashlib, itertools, json, os, sys, time
import networkx as nx

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
TA = os.path.join(ROOT, "proofs/THREEFOLD-SPACES-20261030-001A/THREEFOLD-SPACES-20261030-001A-P001_three_fold_spaces_are_built_from_the_fano_plane")
TB_RES = os.path.join(ROOT, "proofs/THREEFOLD-SPACES-20261030-001B/THREEFOLD-SPACES-20261030-001B-P001_exhaustive_classification_of_small_three_fold_spaces/result.json")
SS_A = os.path.join(ROOT, "proofs/SPACE-SELECTION-20261030-001A/SPACE-SELECTION-20261030-001A-P001_the_gadget_criterion")
sys.path.insert(0, HERE)
sys.path.insert(0, TA)
sys.path.insert(0, SS_A)
import threefold_lib as T  # noqa: E402
import cycles_lib as C  # noqa: E402
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

linear = lambda H: all(len(set(a) & set(b)) <= 1 for a, b in itertools.combinations(H, 2))  # noqa: E731
T14 = C.T14_FOUND

# ---------------------------------------------------------------- 1 the erratum
d1 = {}
H27 = T.point_splice(T14, 0, T14, T14[0])
d1["27-point splice of two copies of the 14-point twisted system at the twisted incidence: points, cubic, linear, connected, 2-colourable"] = (
    T.npoints(H27), T.is_cubic(H27), linear(H27), T.connected(H27), T.colourable_sat(H27))
d1["27 mod 6 (Fano compositions have 7 + 6k points)"] = 27 % 6
# the gap: contract the Fano block {0, 3, 4, 5, 6, 11, 12} of T14 to one point
blk = {0, 3, 4, 5, 6, 11, 12}
inside = [l for l in T14 if set(l) <= blk]
contracted = [tuple('t' if p in blk else p for p in l) for l in T14 if not set(l) <= blk]
d1["T14: lines inside the block, contraction of the remaining lines"] = (len(inside), contracted)
gap = any(len(set(l)) < 3 for l in contracted)
ok1 = d1["27-point splice of two copies of the 14-point twisted system at the twisted incidence: points, cubic, linear, connected, 2-colourable"] == (27, True, True, True, False) \
    and d1["27 mod 6 (Fano compositions have 7 + 6k points)"] == 3 and len(inside) == 6 and gap
report("1 erratum: the classification by Fano compositions fails at 27 points; contractions can repeat a point", ok1, d1)

# ---------------------------------------------------------------- 2 the block lemma
L, P = C.block(0)
cols = [c for c in itertools.product((0, 1), repeat=7) if all(not (c[a] == c[b] == c[e]) for a, b, e in L)]
d2 = {"proper colourings of Fano minus a line": len(cols), "ports always equal": all(c[0] == c[1] == c[2] for c in cols),
      "port colours that occur": sorted({c[0] for c in cols})}
report("2 a Fano block forces its ports to one colour, either colour", d2["ports always equal"] and d2["port colours that occur"] == [0, 1], d2)

# ---------------------------------------------------------------- 3 cycles of blocks
d3 = {}
ok3 = True
for k in range(1, 8):
    H, conn, ports = C.cycle_of_blocks(k)
    col = T.colourable_sat(H)
    rec = (T.npoints(H), T.is_cubic(H), linear(H), T.connected(H), col, C.core_colourable(k))
    d3[f"k={k}: points, cubic, linear, connected, 2-colourable, core 2-colourable"] = rec
    ok3 &= rec[:4] == (7 * k, True, True, True) and col == (k % 2 == 0) and col == rec[5]
report("3 a cycle of k Fano blocks is not 2-colourable iff k is odd", ok3, d3)

# ---------------------------------------------------------------- 4 twisted cycles


def colourable_twisted(H, twist):
    from pysat.solvers import Solver
    with Solver(name='cadical153') as s:
        for i, l in enumerate(H):
            lits = [(p + 1) * (-1 if twist == (i, p) else 1) for p in l]
            s.add_clause(lits)
            s.add_clause([-x for x in lits])
        return s.solve()


d4 = {}
ok4 = True
for k in range(1, 7):
    H, conn, ports = C.cycle_of_blocks(k)
    li = conn[0]
    single = H[li][2]
    col = colourable_twisted(H, (li, single))
    d4[f"k={k}: twisted at the single port of one connecting line: 2-colourable, core"] = (col, C.core_colourable(k, 1))
    ok4 &= col == (k % 2 == 1) and col == C.core_colourable(k, 1)
H2, conn2, _ = C.cycle_of_blocks(2)


def bgraph(H, twist):
    g = nx.Graph()
    for i, l in enumerate(H):
        g.add_node(('L', i), kind='L')
        for p in l:
            g.add_node(('P', p), kind='P')
            g.add_edge(('L', i), ('P', p), tw=(twist == (i, p)))
    return g


iso = nx.is_isomorphic(bgraph(H2, (conn2[0], H2[conn2[0]][2])), bgraph(T14, (0, 0)),
                       node_match=lambda a, b: a['kind'] == b['kind'], edge_match=lambda a, b: a['tw'] == b['tw'])
s14 = T.sns(T14, [(0, 0)])
d4["twisted 2-cycle ~ the system found by SAT at 14 points (twist marked)"] = iso
d4["the 14-point system: untwisted 2-colourable, twisted 2-colourable, signed SNS (det, per)"] = (T.colourable(T14), T.colourable(T14, twist=(0, 0)), s14)
bres = json.load(open(TB_RES))["checks"]
tw = bres["1 non-colourable cubic triple systems exist only on 7 and 13 points (n <= 13); twisted ones on none"]["detail"]["twisted"]
d4["ticket B: twisted systems on n = 3..13"] = sorted({v[0] for v in tw.values()})
ok4 &= iso and d4["the 14-point system: untwisted 2-colourable, twisted 2-colourable, signed SNS (det, per)"][:2] == (True, False) and s14[0] and abs(s14[1]) == 320 \
    and d4["ticket B: twisted systems on n = 3..13"] == ["UNSAT"]
report("4 one twist makes even cycles odd; the twisted 2-cycle is the smallest twisted system", ok4, d4)

# ---------------------------------------------------------------- 5 the knot side


def knot_exact(cx):
    W = G.law_batch('sine', (0,))
    R = G.fast_values(cx, W)[0]
    lam = int(R[0, 0, 1])
    return bool(lam != 0 and all(int(R[x]) == lam * G.FAM['sine'](x, 0) for x in G.TU)), lam


H21, _, _ = C.cycle_of_blocks(3)
H35, _, _ = C.cycle_of_blocks(5)
d5 = {}
ex21 = {}
for L0 in (H21[0], H21[-1]):
    ex21[str(L0)] = knot_exact(T.gadget_from(H21, L0))
d5["3-cycle (21 triangles): corner line -> (exact, lambda(0))"] = ex21
dual = {}
for name, H in (("5-cycle (35 points)", H35), ("27-point splice", H27)):
    dual[name] = (not T.colourable_sat(H), all(T.colourable_sat([l for j, l in enumerate(H) if j != i]) for i in range(len(H))))
d5["duality conditions: not 2-colourable, 2-colourable after deleting any line"] = dual
ok5 = all(v == (True, 125) for v in ex21.values()) and all(v == (True, True) for v in dual.values())
report("5 the knot is exact on gadgets dual to odd cycles of Fano planes and to the 27-point system", ok5, d5)

# ---------------------------------------------------------------- 6 controls
ctrl = {}
H4, conn4, _ = C.cycle_of_blocks(4)
ctrl["even cycles of blocks are 2-colourable"] = T.colourable_sat(H4)
ctrl["twisting a doubled port makes the connecting line vacuous (3-cycle becomes 2-colourable)"] = colourable_twisted(H21, (len(H21) - 3, H21[len(H21) - 3][0]))
mis = T.point_splice(T14, 0, [(1, 2, 0)] + T14[1:], (1, 2, 0))
ctrl["splicing the twisted systems with mis-paired cut edges gives a 2-colourable system"] = T.colourable_sat(mis)
report("6 controls fire", all(ctrl.values()), ctrl)

out["ok"] = ok_all
out["seconds"] = round(time.time() - T0, 1)
print("ALL OK" if ok_all else "SOME CHECK FAILED", out["seconds"], "s")
if "--write" in sys.argv:
    json.dump({"schema_version": 1, "artifact_id": "THREEFOLD-SPACES-20261030-001C-P001", "status": "Proved" if ok_all else "Failed",
               "checks": out}, open(os.path.join(HERE, "result.json"), "w"), indent=1, default=str)
sys.exit(0 if ok_all else 1)
