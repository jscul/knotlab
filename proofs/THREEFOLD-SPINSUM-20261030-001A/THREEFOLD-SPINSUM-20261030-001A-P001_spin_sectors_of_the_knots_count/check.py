"""Checks for THREEFOLD-SPINSUM-20261030-001A-P001 (spin sectors of the knot's count).

  0 dependency artifacts bound by the hashes recorded in manifest.json
  1 the spin sum: 2^-g sum_q (-1)^Arf(q) N_q equals #col(H) (= 0) and #col(H - L), on all 16 Fano maps with every contact and on four
    13-point maps with contacts in both atoms
  2 the knot's sign class is the only non-colourable Kasteleyn class: every nonzero twist of every tested map is Kasteleyn and 2-colourable
  3 the Fano sectors: 8, 8, 8 | 24 closed and 16, 16, 16 | 28 opened on every map and contact; the even sectors are the knot's own
  4 genus 2: the sector matrices indexed by the two handles' spin structures have rank 4 (no factorization over handles)
  5 controls that must fire
Run: .venv/bin/python -B check.py [--write]   (networkx, python-sat, sympy; a few seconds)"""
import collections, hashlib, itertools, json, os, sys, time
from fractions import Fraction as Fr
import networkx as nx
import sympy

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
P = lambda r: os.path.join(ROOT, "proofs", r)  # noqa: E731
for p in (P("THREEFOLD-SPACES-20261030-001A/THREEFOLD-SPACES-20261030-001A-P001_three_fold_spaces_are_built_from_the_fano_plane"),
          P("THREEFOLD-SURFACES-20261030-001A/THREEFOLD-SURFACES-20261030-001A-P001_fano_atoms_are_handles"),
          P("THREEFOLD-AMPLITUDE-20261030-001A/THREEFOLD-AMPLITUDE-20261030-001A-P001_five_per_handle_tuttes_number_per_planar_piece"),
          P("THREEFOLD-SPIN-20261030-001A/THREEFOLD-SPIN-20261030-001A-P001_kasteleyn_faces_and_even_spin_structures"), HERE):
    sys.path.insert(0, p)
import threefold_lib as T  # noqa: E402
import surface_lib as SL  # noqa: E402
import amplitude_lib as AM  # noqa: E402
import spin_lib as S  # noqa: E402
import sector_lib as X  # noqa: E402

T0 = time.time()
out, ok_all = {}, True


def report(key, ok, detail):
    global ok_all
    out[key] = {"ok": bool(ok), "detail": detail}
    ok_all &= bool(ok)
    print(("PASS " if ok else "FAIL ") + key + ": " + json.dumps(detail, default=str)[:3000], flush=True)


# ---------------------------------------------------------------- 0
man = json.load(open(os.path.join(HERE, "manifest.json")))
mism = {r: dg for r, dg in man["parent_bindings"].items()
        if hashlib.sha256(open(os.path.join(ROOT, r), "rb").read()).hexdigest() != dg}
report("0 dependency artifacts bound by hash", not mism, {"parents": len(man["parent_bindings"]), "mismatched": mism})

F7 = T.FANO
H13 = T.point_splice(F7, 0, F7, F7[0])
SPACES = {"Fano": (F7, 1, None, list(range(7))), "13-point": (H13, 2, 4, None)}


def setup(H, g, limit):
    E = S.graph_of(H)
    maps = SL.min_genus_rotations(E, g)[:limit] if limit else SL.min_genus_rotations(E, g)
    return E, maps, S.perfect_matchings(E)


def lines_in_both_atoms(E):
    cut = S.tight_cuts(E)[0]
    G = nx.MultiGraph()
    G.add_nodes_from(SL.vertices(E))
    G.add_edges_from((E[k][0], E[k][1], k) for k in range(len(E)) if k not in cut)
    shores = list(nx.connected_components(G))
    return [min(v[1] for v in Y if v[0] == 'L') for Y in shores], cut, shores


# ---------------------------------------------------------------- 1 the spin sum and 3 the Fano sectors
d1, ok1 = {}, True
d3, ok3 = {}, True
DATA = {}
for name, (H, g, limit, lines) in SPACES.items():
    E, maps, pms = setup(H, g, limit)
    n = len(H)
    if lines is None:
        lines, cut, shores = lines_in_both_atoms(E)
    evB = X.even_subgraphs(E)
    evL = {L: X.even_subgraphs(E, ('L', L)) for L in lines}
    colH = AM.count(H)
    colL = {L: AM.count(H, drop=L) for L in lines}
    good, total = 0, 0
    fano_rows = collections.Counter()
    DATA[name] = (E, maps, pms, evB, evL, lines)
    for bits in maps:
        rot = SL.rotation(E, bits)
        H1 = S.h1_basis(E, rot)
        qref = S.form(E, rot, frozenset(), pms[0], H1)
        realized = {S.hclass(D ^ pms[0], H1) for D in pms}
        EB = X.class_sums(evB, H1)
        forms = X.spin_structures(qref, g)
        NB = {beta: Fr(3, 2) ** n * X.sector(q, EB) for beta, q in forms}
        total += 1
        good += sum((-1) ** X.arf(q, g) * NB[beta] for beta, q in forms) / 2 ** g == colH
        for L in lines:
            EL = X.class_sums(evL[L], H1)
            NL = {beta: 2 * Fr(3, 2) ** (n - 1) * X.sector(q, EL) for beta, q in forms}
            total += 1
            good += sum((-1) ** X.arf(q, g) * NL[beta] for beta, q in forms) / 2 ** g == colL[L]
            if name == "Fano":
                fano_rows[tuple(sorted((X.arf(q, g), X.induced(q, qref, realized), int(NB[beta]), int(NL[beta])) for beta, q in forms))] += 1
    d1[name] = {"genus": g, "maps": len(maps), "contacts": lines, "#col(H)": colH, "#col(H - L)": colL,
                "identities checked": total, "identities holding": good}
    ok1 &= good == total and colH == 0
    if name == "Fano":
        d3["(Arf, knot-induced, N(B), N(B - L)) over all maps and contacts"] = {str(k): v for k, v in fano_rows.items()}
        ok3 &= dict(fano_rows) == {((0, True, 8, 16), (0, True, 8, 16), (0, True, 8, 16), (1, False, 24, 28)): 16 * 7}
        ok3 &= Fr(3 * 16 - 28, 2) == 2 * 5 and 3 * 8 - 24 == 0
report("1 the spin sum recovers #col(H) = 0 and #col(H - L) on every map and contact", ok1, d1)
report("3 Fano sectors: 8, 8, 8 | 24 closed and 16, 16, 16 | 28 opened; the even ones are the knot's own", ok3, d3)

# ---------------------------------------------------------------- 2 the knot's sign class is the only non-colourable one
d2, ok2 = {}, True
for name, (H, g, limit, _) in SPACES.items():
    E, maps, pms, *_ = DATA[name]
    tally = collections.Counter()
    for bits in maps:
        rot = SL.rotation(E, bits)
        H1 = S.h1_basis(E, rot)
        for beta in X.classes_of(g):
            c = 0
            for b, cc in zip(beta, H1):
                if b:
                    c ^= cc
            negE = frozenset(k for k in range(len(E)) if c >> k & 1)
            kast = all(ok for L, ok in S.face_condition(E, rot, negE))
            neg = [(E[k][0][1], E[k][1][1]) for k in negE]
            tally[("knot's class" if not any(beta) else "nonzero twist", kast, AM.colourable(H, neg))] += 1
    d2[name] = {"(class, Kasteleyn, 2-colourable)": {str(k): v for k, v in tally.items()}}
    ok2 &= set(tally) == {("knot's class", True, False), ("nonzero twist", True, True)}
report("2 every nonzero Kasteleyn twist is 2-colourable; the knot's class is not", ok2, d2)

# ---------------------------------------------------------------- 4 genus 2: no factorization over handles
d4, ok4 = {}, True
E, maps, pms, evB, evL, lines = DATA["13-point"]
_, cut, shores = lines_in_both_atoms(E)
ranks = collections.Counter()
for bits in maps:
    rot = SL.rotation(E, bits)
    H1 = S.h1_basis(E, rot)
    qref = S.form(E, rot, frozenset(), pms[0], H1)
    side = []
    for Y in shores:
        side.append(sorted({S.hclass(Z, H1) for Z in evB if all(E[k][0] in Y and E[k][1] in Y for k in range(len(E)) if Z >> k & 1)}))
    forms = X.spin_structures(qref, 2)
    EB = X.class_sums(evB, H1)
    for which, Esum, norm in [("closed", EB, Fr(3, 2) ** 13)] + [(f"contact {L} opened", X.class_sums(evL[L], H1), 2 * Fr(3, 2) ** 12) for L in lines]:
        vals = {(tuple(q[h] for h in side[0]), tuple(q[h] for h in side[1])): norm * X.sector(q, Esum) for beta, q in forms}
        R1, R2 = sorted({k[0] for k in vals}), sorted({k[1] for k in vals})
        Mx = sympy.Matrix(len(R1), len(R2), lambda i, j: vals[(R1[i], R2[j])])
        ranks[(which, len(side[0]), len(side[1]), Mx.rank())] += 1
d4["(matrix, classes on side 1, on side 2, rank), by map"] = {str(k): v for k, v in ranks.items()}
ok4 &= all(k[1] == 4 and k[2] == 4 and k[3] == 4 for k in ranks) and sum(ranks.values()) == len(maps) * 3
d4["amplitude of the 13-point space at both contacts"] = {L: AM.amplitude(H13, L) for L in lines}
ok4 &= set(d4["amplitude of the 13-point space at both contacts"].values()) == {25}
report("4 genus 2: sector matrices have rank 4, so sectors do not factor over handles, though the amplitude does (25 = 5 x 5)", ok4, d4)

# ---------------------------------------------------------------- 5 controls
ctrl = {}
E7, maps7, pms7, evB7, evL7, _ = DATA["Fano"]
rot = SL.rotation(E7, maps7[0])
H1 = S.h1_basis(E7, rot)
qref = S.form(E7, rot, frozenset(), pms7[0], H1)
forms = X.spin_structures(qref, 1)
EBhalf = X.class_sums(evB7, H1, Fr(1, 4))           # a real coupling x = 1/2
bal = [sum((-1) ** X.arf(q, 1) * X.sector(q, EBhalf) for beta, q in forms if X.arf(q, 1) == a) for a in (0, 1)]
ctrl["at another coupling (x = 1/2) the even and odd sectors do not balance"] = bal[0] != -bal[1]
ctrl["the coordinate dot product in place of the intersection form mislabels the knot's spin structures"] = \
    any(all(q[h] == (qref[h] + sum(x * y for x, y in zip(a, h))) % 2 for h in q) for beta, q in forms if X.arf(q, 1) == 1
        for a in {S.hclass(D ^ pms7[0], H1) for D in pms7})
report("5 controls fire", all(ctrl.values()), ctrl)

out["ok"] = ok_all
out["seconds"] = round(time.time() - T0, 1)
print("ALL OK" if ok_all else "SOME CHECK FAILED", out["seconds"], "s")
if "--write" in sys.argv:
    json.dump({"schema_version": 1, "artifact_id": "THREEFOLD-SPINSUM-20261030-001A-P001", "status": "Proved" if ok_all else "Failed",
               "checks": out}, open(os.path.join(HERE, "result.json"), "w"), indent=1, default=str)
sys.exit(0 if ok_all else 1)
