"""Checks for PLAIN-COUNT-20261031-001A-P001 (signs interpolate away: plain Pfaffian triple systems are #P-hard to count).

  0 dependency artifacts bound by the hashes recorded in manifest.json
  1 long edges remove signs: for signed K3,3 systems, plain counts at L + 1 lengths give the signed count at t = -1 and the count with
    the signs dropped at t = 1
  2 switching inside the pages: the k_S-snake instances of SOFT-CROSS A keep their counts with 2 negations per Q page and 4 per R page
  3 end to end through plain instances: for k_S = 1, 3, 5, 7 the plain counts at L + 1 lengths (L = 6 k_S) give the signed instance
    counts at t = -1, and these give 9 #col(K3,3) = 54 (SOFT-CROSS A, Corollary 6): K3,3 counted from plain Pfaffian instances only
  4 the plain instances are triple systems with Pfaffian incidence graphs: no signs, cubic bipartite, certified Pfaffian (pieces planar,
    glued Kasteleyn signing non-colourable), non-planar, three twisted branches at every junction and no good root (lengths 1 and 2)
  5 signed hosts: K3,3 signings with 2 and 5 negations, k_S = 1, host negations removed the same way
  6 controls: q(1) is the count with the signs dropped, not the signed count; L counts leave q(-1) undetermined
Run: .venv/bin/python -B check.py [--write]   (networkx, numpy, sympy; about fifteen minutes, mostly section 3)"""
import hashlib, itertools, json, os, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
P = lambda r: os.path.join(ROOT, "proofs", r)  # noqa: E731
for p in (P("THREEFOLD-AMPLITUDE-20261030-001A/THREEFOLD-AMPLITUDE-20261030-001A-P001_five_per_handle_tuttes_number_per_planar_piece"),
          P("THREEFOLD-AMPLITUDE-20261030-001B/THREEFOLD-AMPLITUDE-20261030-001B-P001_the_amplitude_by_computation"),
          P("TWIST-COUNT-20261030-001A/TWIST-COUNT-20261030-001A-P001_the_knots_junction_is_a_similitude"),
          P("SOFT-CROSS-20261031-001A/SOFT-CROSS-20261031-001A-P001_a_soft_crossing_interpolates_to_a_sharp_one"), HERE):
    sys.path.insert(0, p)
import networkx as nx  # noqa: E402
import numpy as np  # noqa: E402
import sympy as sp  # noqa: E402
import amplitude_lib as AM  # noqa: E402
import twist_lib as TW  # noqa: E402
import cross_lib as X  # noqa: E402
import plain_lib as PL  # noqa: E402

T0 = time.time()
out, ok_all = {}, True
SIGMA1 = [40000, -1112, 3336, -192]
LAMBDA = [810000, 7506, -22518, -432]
KS = (1, 3, 5, 7)
SIGNINGS = {"unsigned": 0b000000000, "two negations": 0b000010001, "five negations": 0b101100110}


def report(key, ok, detail):
    global ok_all
    out[key] = {"ok": bool(ok), "detail": detail}
    ok_all &= bool(ok)
    print(("PASS " if ok else "FAIL ") + key + ": " + json.dumps(detail, default=str)[:3000], flush=True)


def count(B):
    return AM.count(*B.system())


def plain_series(Bm):
    """plain counts at lengths 1..L+1, and the largest plain instance"""
    L = len(Bm.neg)
    counts, big = {}, 0
    for k in range(1, L + 2):
        Bu = PL.unsign(Bm, k)
        counts[k] = count(Bu)
        big = max(big, Bu.g.number_of_nodes())
    return L, counts, big


def through_snakes(Z):
    Xs = np.zeros((2, 2, 2, 2), dtype=object)
    for z in itertools.product((0, 1), repeat=4):
        Xs[z] = (1 if z[1] == z[3] else 0) * (-1 if z[0] == z[2] else 2)
    Xt = X.hada(Xs)
    Mx = sp.Matrix([[sp.Rational(SIGMA1[i] * LAMBDA[i] ** (kS - 1), 16) for i in range(4)] for kS in KS])
    c = Mx.LUsolve(sp.Matrix([Z[kS] for kS in KS]))
    return sum(c[i] * sp.Rational(Xt[s], 16) for i, s in enumerate(X.STRAIGHT))


# ---------------------------------------------------------------- 0
man = json.load(open(os.path.join(HERE, "manifest.json")))
mism = {r: dg for r, dg in man["parent_bindings"].items()
        if hashlib.sha256(open(os.path.join(ROOT, r), "rb").read()).hexdigest() != dg}
report("0 dependency artifacts bound by hash", not mism, {"parents": len(man["parent_bindings"]), "mismatched": mism})

# ---------------------------------------------------------------- 1 long edges remove signs
d1, ok1 = {}, True
for name in ("two negations", "five negations"):
    signs = X.k33_signs(SIGNINGS[name])
    Bk = X.Builder()
    for p_ in X.K33_POINTS:
        for l_ in X.K33_LINES:
            Bk.edge(p_, l_, (p_, l_) in signs)
    L, counts, big = plain_series(Bk)
    signed, dropped = count(Bk), AM.count(*X.k33_system(set()))
    qm, qp = PL.value_at(counts, L, -1), PL.value_at(counts, L, 1)
    d1[name] = {"L": L, "q(-1)": str(qm), "signed count": signed, "q(1)": str(qp), "count with signs dropped": dropped}
    ok1 &= qm == signed and qp == dropped
report("1 long edges remove signs: q(-1) is the signed count, q(1) the count with the signs dropped", ok1, d1)

# ---------------------------------------------------------------- 2 switching inside the pages
d2, ok2, MIN = {}, True, {}
for kS in KS:
    Bs = X.k33_instance(kS, set())
    Bm, rep = PL.minimal_page_signs(Bs)
    MIN[kS] = (Bs, Bm)
    per = sorted({(t[0], b, a) for t, (b, a) in rep.items()})
    same = count(Bs) == count(Bm)
    d2[kS] = {"negations before": len(Bs.neg), "after": len(Bm.neg), "per page (kind, before, after)": per, "count unchanged": same}
    ok2 &= same and len(Bm.neg) == 6 * kS and all((k_, b, a) in {('Q', 4, 2), ('R', 7, 4)} for k_, b, a in per)
report("2 switching inside the pages: 2 negations per Q page and 4 per R page, counts unchanged", ok2, d2)

# ---------------------------------------------------------------- 3 end to end through plain instances
d3, ok3, Z = {}, True, {}
for kS in KS:
    Bs, Bm = MIN[kS]
    t1 = time.time()
    L, counts, big = plain_series(Bm)
    Z[kS] = PL.value_at(counts, L, -1)
    d3[kS] = {"L": L, "plain counts": len(counts), "largest plain instance (vertices)": big, "q(-1) = signed instance count":
              Z[kS] == count(Bs), "seconds": round(time.time() - t1, 1)}
    ok3 &= Z[kS] == count(Bs)
    print("   k_S", kS, d3[kS], flush=True)
nine = through_snakes(Z)
d3["9 #col(K3,3) from plain counts only"] = str(nine)
ok3 &= nine == 9 * AM.count(*X.k33_system(set()))
report("3 end to end: 9 #col(K3,3) = 54 from counts of plain Pfaffian instances only", ok3, d3)

# ---------------------------------------------------------------- 4 certificates
d4, ok4 = {}, True
for kS in KS:
    Bs, Bm = MIN[kS]
    for k in (1, 2):
        Bu = PL.unsign(Bm, k)
        H, neg = Bu.system()                      # asserts degree 3
        bip = all(X.is_point(a) != X.is_point(b) for a, b in Bu.g.edges())
        good, lv, kap = PL.certify(Bu, TW, AM)
        sqs = lv[0][1]
        tw = TW.twisted_branches(lv, sqs, set(), kap)
        per = [sum(tw[(S, i)] for i in range(len(lv)) if (S, i) in tw) for S in sqs]
        root = TW.good_root(lv, sqs, tw)
        planar = nx.check_planarity(Bu.g)[0]
        d4[f"k_S={kS}, length {k}"] = {"vertices": Bu.g.number_of_nodes(), "signs": len(neg), "certified": good, "non-planar": not planar,
                                       "twisted branches": per, "good root": root}
        ok4 &= not neg and bip and good and not planar and all(n == 3 for n in per) and root is None
report("4 the plain instances: no signs, cubic bipartite, certified Pfaffian, non-planar, branched twists", ok4, d4)

# ---------------------------------------------------------------- 5 signed hosts
d5, ok5 = {}, True
for name in ("two negations", "five negations"):
    Bs = X.k33_instance(1, X.k33_signs(SIGNINGS[name]))
    Bm, rep = PL.minimal_page_signs(Bs)
    L, counts, big = plain_series(Bm)
    qm = PL.value_at(counts, L, -1)
    good, _, _ = PL.certify(PL.unsign(Bm, 1), TW, AM)
    d5[name] = {"L": L, "q(-1)": str(qm), "signed instance count": count(Bs), "certified (length 1)": good}
    ok5 &= qm == count(Bs) and good
report("5 signed hosts: host negations removed the same way", ok5, d5)

# ---------------------------------------------------------------- 6 controls
Bs, Bm = MIN[1]
L, counts, big = plain_series(Bm)
qp = PL.value_at(counts, L, 1)
Bd = X.Builder()
Bd.g, Bd.neg = Bs.g, set()
ctrl = {"q(1) is the count with the signs dropped": qp == count(Bd), "which differs from the signed count": qp != count(Bs)}
rows = sp.Matrix([[sp.Rational(-1, 3) ** (k * j) for j in range(L + 1)] for k in range(1, L + 1)])
null = rows.nullspace()
ctrl["L counts leave q(-1) undetermined"] = len(null) == 1 and sum(null[0][j] * (-1) ** j for j in range(L + 1)) != 0
report("6 controls fire", all(ctrl.values()), ctrl)

out["ok"] = ok_all
out["seconds"] = round(time.time() - T0, 1)
print("ALL OK" if ok_all else "SOME CHECK FAILED", out["seconds"], "s")
if "--write" in sys.argv:
    json.dump({"schema_version": 1, "artifact_id": "PLAIN-COUNT-20261031-001A-P001", "status": "Proved" if ok_all else "Failed",
               "checks": out}, open(os.path.join(HERE, "result.json"), "w"), indent=1, default=str)
sys.exit(0 if ok_all else 1)
