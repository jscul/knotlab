"""Checks for SOFT-CROSS-20261031-001C-P001 (end to end: formulas counted through certified Pfaffian instances).

  0 dependency artifacts bound by the hashes recorded in manifest.json
  1 the drawings: for each formula and k, G_k (ticket B) is non-planar, G_k minus the edge e1 is planar, and in that embedding a face at
    one end of e1 and a face at the other share the edge e2 (no common end with e1): a drawing with one crossing, e1 x e2
  2 the instances: G_k with the crossing replaced by a k_S-snake (ticket A; e1 as wire B, e2 as wire A), k_S = 1, 3, 5, 7: each is certified
    Pfaffian (planar pieces, glued Kasteleyn signing non-colourable), is itself non-planar, and has three twisted branches at every junction
    with no good root
  3 end to end: the four counts per k give 9 #col(G_k), equal to the direct count; D + 1 values of k give #formula exactly
  4 control: replacing the compensated crossover by the bare exact crossover (no compensation of the inserted line) recovers wrong values
Run: .venv/bin/python -B check.py [--write]   (networkx, numpy, sympy; about a minute)"""
import hashlib, itertools, json, os, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
P = lambda r: os.path.join(ROOT, "proofs", r)  # noqa: E731
for p in (P("THREEFOLD-AMPLITUDE-20261030-001A/THREEFOLD-AMPLITUDE-20261030-001A-P001_five_per_handle_tuttes_number_per_planar_piece"),
          P("THREEFOLD-AMPLITUDE-20261030-001B/THREEFOLD-AMPLITUDE-20261030-001B-P001_the_amplitude_by_computation"),
          P("TWIST-COUNT-20261030-001A/TWIST-COUNT-20261030-001A-P001_the_knots_junction_is_a_similitude"),
          P("SOFT-CROSS-20261031-001A/SOFT-CROSS-20261031-001A-P001_a_soft_crossing_interpolates_to_a_sharp_one"),
          P("SOFT-CROSS-20261031-001B/SOFT-CROSS-20261031-001B-P001_counting_under_branched_twists_is_sharp_p_hard")):
    sys.path.insert(0, p)
import networkx as nx  # noqa: E402
import numpy as np  # noqa: E402
import sympy as sp  # noqa: E402
import amplitude_lib as AM  # noqa: E402
import twist_lib as TW  # noqa: E402
import cross_lib as X  # noqa: E402
import hard_lib as HL  # noqa: E402

T0 = time.time()
out, ok_all = {}, True
SIGMA1 = [40000, -1112, 3336, -192]
LAMBDA = [810000, 7506, -22518, -432]
KS = (1, 3, 5, 7)
CASES = {   # formula, crossing edges (e1 = wire B, e2 = wire A)
    "(a, a, b)": ([('a', 'a', 'b')], (('pt', 'q', 0, 0), ('ln', 'C', 0)), (('pt', 'q', 0, 1), ('ln', 'M', ('a', 1), 0))),
    "(b, a, c)(c, b, c)": ([('b', 'a', 'c'), ('c', 'b', 'c')], (('pt', 'q', 0, 0), ('ln', 'C', 0)),
                           (('pt', 'q', 1, 1), ('ln', 'M', ('b', 1), 0))),
}


def report(key, ok, detail):
    global ok_all
    out[key] = {"ok": bool(ok), "detail": detail}
    ok_all &= bool(ok)
    print(("PASS " if ok else "FAIL ") + key + ": " + json.dumps(detail, default=str)[:3000], flush=True)


def one_crossing(g, e1, e2):
    """g - e1 is planar and some face at each end of e1 contains e2 (as a shared edge), e2 disjoint from e1"""
    h = g.copy()
    h.remove_edge(*e1)
    ok, emb = nx.check_planarity(h)
    if not ok or set(e1) & set(e2):
        return False
    seen, fs = set(), []
    for u, v in emb.edges():
        if (u, v) not in seen:
            fs.append(emb.traverse_face(u, v, mark_half_edges=seen))
    edges = lambda f: {frozenset((f[i], f[(i + 1) % len(f)])) for i in range(len(f))}  # noqa: E731
    E2 = frozenset(e2)
    return any(E2 in edges(a) and E2 in edges(b) and a is not b for a in fs if e1[0] in a for b in fs if e1[1] in b)


def instance(F, k, kS, eB, eA):
    """G_k with the crossing of eB (wire B) and eA (wire A) replaced by a kS-snake, as in cross_lib.k33_instance"""
    B = HL.build(F, k)
    (P1, L1), (P2, L2) = eB, eA
    B.g.remove_edge(P1, L1)
    B.g.remove_edge(P2, L2)
    pe, lf = ('pt', 'pi_e'), ('ln', 'l_f')
    B.edge(pe, L1)
    B.edge(P2, lf)
    B.snake(kS, lf, P1, L2, pe)
    B.cap('c', lf, pe)
    return B


def crossover_hat(compensated):
    Xs = np.zeros((2, 2, 2, 2), dtype=object)
    for z in itertools.product((0, 1), repeat=4):
        if compensated:
            Xs[z] = (1 if z[1] == z[3] else 0) * (-1 if z[0] == z[2] else 2)
        else:
            Xs[z] = (1 if z[1] == z[3] else 0) * (1 if z[0] == z[2] else 0)
    return X.hada(Xs)


def through_snakes(Z, compensated=True):
    Xt = crossover_hat(compensated)
    Mx = sp.Matrix([[sp.Rational(SIGMA1[i] * LAMBDA[i] ** (kS - 1), 16) for i in range(4)] for kS in KS])
    c = Mx.LUsolve(sp.Matrix([Z[kS] for kS in KS]))
    return sum(c[i] * sp.Rational(Xt[s], 16) for i, s in enumerate(X.STRAIGHT))


# ---------------------------------------------------------------- 0
man = json.load(open(os.path.join(HERE, "manifest.json")))
mism = {r: dg for r, dg in man["parent_bindings"].items()
        if hashlib.sha256(open(os.path.join(ROOT, r), "rb").read()).hexdigest() != dg}
report("0 dependency artifacts bound by hash", not mism, {"parents": len(man["parent_bindings"]), "mismatched": mism})

# ---------------------------------------------------------------- 1-3
d1, d2, d3, ok1, ok2, ok3 = {}, {}, {}, True, True, True
DIRECT, Z_ALL = {}, {}
for name, (F, e1, e2) in CASES.items():
    D = 3 * len(F)
    ks = list(range(2, D + 3))
    d2[name] = {"instances": 0, "certified": 0, "non-planar": 0, "junctions with three twisted branches": 0, "junctions": 0,
                "good roots": 0, "largest instance (vertices)": 0}
    recovered = {}
    for k in ks:
        G = HL.build(F, k)
        ok1 &= not nx.check_planarity(G.g)[0] and one_crossing(G.g, e1, e2)
        DIRECT[(name, k)] = AM.count(*G.system())
        Z = {}
        for kS in KS:
            Bi = instance(F, k, kS, e1, e2)
            Z[kS] = AM.count(*Bi.system())
            good, _ = X.certify_pfaffian(Bi, TW, AM)
            lv = X.leaves_of(Bi)
            kap = TW.kasteleyn_tree_signing(lv)
            tw = TW.twisted_branches(lv, lv[0][1], set(Bi.neg), kap)
            per = [sum(tw[(S, i)] for i in range(len(lv)) if (S, i) in tw) for S in lv[0][1]]
            root = TW.good_root(lv, lv[0][1], tw)
            s = d2[name]
            s["instances"] += 1
            s["certified"] += good
            s["non-planar"] += not nx.check_planarity(Bi.g)[0]
            s["junctions"] += len(per)
            s["junctions with three twisted branches"] += sum(n == 3 for n in per)
            s["good roots"] += root is not None
            s["largest instance (vertices)"] = max(s["largest instance (vertices)"], Bi.g.number_of_nodes())
        Z_ALL[(name, k)] = Z
        nine = through_snakes(Z)
        recovered[k] = nine / 9
        ok3 &= nine == 9 * DIRECT[(name, k)]
    s = d2[name]
    ok2 &= s["certified"] == s["non-planar"] == s["instances"] == 4 * len(ks) and \
        s["junctions with three twisted branches"] == s["junctions"] and s["good roots"] == 0
    total, _ = HL.recover(F, recovered)
    truth = HL.count_formula(F)
    d3[name] = {"k": [ks[0], ks[-1]], "9 #col(G_k) through snakes = direct": all(recovered[k] == DIRECT[(name, k)] for k in ks),
                "#formula recovered": str(total), "#formula": truth}
    ok3 &= total == truth
    d1[name] = {"k": [ks[0], ks[-1]], "crossing": [e1, e2]}
report("1 the drawings: G_k non-planar, one crossing e1 x e2 for every k", ok1, d1)
report("2 the instances: certified Pfaffian, non-planar, three twisted branches at every junction, no good root", ok2, d2)
report("3 end to end: 9 #col(G_k) through the snakes equals the direct count; #formula recovered exactly", ok3, d3)

# ---------------------------------------------------------------- 4 control
d4 = {}
for name, (F, e1, e2) in CASES.items():
    D = 3 * len(F)
    wrong = [k for k in range(2, D + 3) if through_snakes(Z_ALL[(name, k)], compensated=False) != 9 * DIRECT[(name, k)]]
    d4[name] = {"k with a wrong value without compensation": wrong}
ok4 = all(len(v["k with a wrong value without compensation"]) > 0 for v in d4.values())
report("4 control: the bare exact crossover (no compensation) recovers wrong values", ok4, d4)

out["ok"] = ok_all
out["seconds"] = round(time.time() - T0, 1)
print("ALL OK" if ok_all else "SOME CHECK FAILED", out["seconds"], "s")
if "--write" in sys.argv:
    json.dump({"schema_version": 1, "artifact_id": "SOFT-CROSS-20261031-001C-P001", "status": "Proved" if ok_all else "Failed",
               "checks": out}, open(os.path.join(HERE, "result.json"), "w"), indent=1, default=str)
sys.exit(0 if ok_all else 1)
