"""Checks for COPRIME-DICHOTOMY-20261027-001A-P001.

  1 Lemma 1 on free graded algebras (characters mod d, classes 2 to 4), their criterion quotients and the examples, at every
    divisor d' of d: the four conditions agree; the criterion at d implies it at every divisor; criterion quotients satisfy it
  2 independent counts (BEYOND-CLASS2-20261027-001A's group-law layered count, read-only) at r = 3, 4, 6: every sector of an
    algebra satisfying the criterion at the sector's order equals prod_theta |Z1(F_p^theta)|^(dim n_theta); a four-way control
    with a (P3) failure falls below it
  3 class 4 (cd_lib's braid model): random free data of a class-4 criterion quotient lift on knot surgeries at slopes d/1 and d/p;
    the free class-4 algebra on the same generators obstructs (control)
Run: python3 -B check.py [--write]"""
import glob
import json
import os
import sys
import time
import numpy as np

T_START = time.time()
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
sys.path.insert(1, glob.glob(os.path.join(ROOT, "proofs/BEYOND-CLASS2-20261027-001A/*P001_*"))[0])
sys.path.insert(2, glob.glob(os.path.join(ROOT, "proofs/COPRIME-CLASS2-20261026-001B/*P001_*"))[0])
from cd_lib import (GLie, BraidAlg, CyclicBraidModel, free_graded, criterion, criterion_quotient, lemma1, pair_failures,
                    triple_failures, root_of_unity)  # noqa: E402
import bc_lib as Bc  # noqa: E402  (read-only: GradedLie, z1, direct_count)
import cp_lib as C  # noqa: E402  (read-only: closed-braid presentations, connected sums)

out = {}
ok_all = True


def report(key, ok, detail):
    global ok_all
    out[key] = {"ok": bool(ok), "detail": detail}
    ok_all &= bool(ok)
    print(("PASS " if ok else "FAIL ") + key + ": " + json.dumps(detail, default=str)[:700], flush=True)


def divisors(n):
    return [k for k in range(1, n + 1) if n % k == 0]


def four_way(p, d, e=1):
    return GLie.from_brackets(p, d, "x y w z u t".split(), [1, 1, 1, 2, 2, 3], [e, -e, -e, 0, 0, -e],
                              {("x", "y"): {"z": 1}, ("w", "x"): {"u": 1}, ("w", "z"): {"t": 1}, ("y", "u"): {"t": -1}})


def cross_layer(p, d, e=1):
    return GLie.from_brackets(p, d, "x y z a b".split(), [1, 1, 2, 3, 3], [0, e, e, e, 2 * e],
                              {("x", "y"): {"z": 1}, ("x", "z"): {"a": 1}, ("y", "z"): {"b": 1}})


def to_bc(L, r):
    """the same algebra as BEYOND-CLASS2-20261027-001A's GradedLie (class <= 3), characters mod r"""
    br = {}
    for i in range(L.D):
        for j in range(i + 1, L.D):
            v = L.br(L.unit(i), L.unit(j))[0]
            if v.any(): br[(L.names[i], L.names[j])] = {L.names[k]: int(v[k]) for k in np.nonzero(v)[0]}
    return Bc.GradedLie(L.p, r, L.names, [int(x) for x in L.layer], [int(c) for c in L.chars], br)


def two_bridge(alpha, beta):
    """Schubert presentation <a, b | a w = w b> of the two-bridge knot b(alpha, beta), as (generator, exponent) words"""
    alpha = abs(alpha)
    beta = beta % alpha
    if beta % 2 == 0: beta -= alpha
    eps = [1 - 2 * (((i * beta) // alpha) % 2) for i in range(1, alpha)]
    w = [(1 if i % 2 == 0 else 0, e) for i, e in enumerate(eps)]
    inv = [(g, -e) for g, e in reversed(w)]
    return 2, [[(0, 1)] + w + [(1, -1)] + inv]


# ---------------------------------------------------------------- 1 Lemma 1, restriction, criterion quotients
rows = {}
ok = True
algs = {}
for (p, d, gens, c) in [(13, 6, [0, 1, 5], 3), (13, 4, [1, 3], 4), (13, 3, [1, 2], 4), (13, 12, [1, 4, 6], 3),
                        (7, 6, [1, 2, 3], 2), (7, 3, [0, 1, 2], 3), (13, 4, [1, 2], 3), (13, 6, [1, 3], 4), (13, 4, [0, 1, 3], 3)]:
    L = free_graded(p, d, gens, c)
    algs[f"free class {c} on chars {gens} mod {d} (p={p})"] = L
    Q = criterion_quotient(L)
    algs[f"criterion quotient of free class {c} on {gens} mod {d} (p={p})"] = Q
for d in (3, 4, 6):
    algs[f"four-way (1, -1, -1) mod {d}"] = four_way(13, d)
    algs[f"cross-layer (0, 1) mod {d}"] = cross_layer(13, d)
for name, L in algs.items():
    L.check()
    per_d = {}
    for d2 in divisors(L.d):
        if d2 == 1: continue
        flags = lemma1(L.coarsen(d2))
        agree = len({flags[k] for k in list(flags)[:4]}) == 1
        per_d[d2] = {"criterion": flags["(i) P2 and P3"], "four conditions agree": agree, "P2": flags["P2 alone"],
                     "theta_d automorphism iff P2": flags["theta_d automorphism"] == flags["P2 alone"]}
        ok &= agree and flags["theta_d automorphism"] == flags["P2 alone"]
    for d2 in per_d:
        for d3 in per_d:
            if d2 % d3 == 0 and per_d[d2]["criterion"] and not per_d[d3]["criterion"]:
                ok = False; per_d[d2]["restriction violated at"] = d3
    if name.startswith("criterion quotient"):
        ok &= per_d[L.d]["criterion"]
    rows[name] = {"dim": L.D, "class": int(L.layer.max()), "by sector order": per_d}
report("1 Lemma 1, restriction to divisors, criterion quotients", ok, rows)

# ---------------------------------------------------------------- 2 independent group-law counts
ok = True
counts = []


def predicted(Lb, U, rels, k):
    p, r = Lb.p, Lb.r
    tot = 0
    for i in range(Lb.n):
        mult = pow(Lb.Z, (k * Lb.chi[i]) % r, p)
        tot += len(Bc.z1(U, rels, mult, p))
    return p ** tot


def sector_order(k, r):
    return r // np.gcd(k, r)


cases = []
# (a) class 3, r = 3, p = 7: criterion quotient on x (trivial), y (1), y' (2); 6_1 at slope 3/1 (closed braid) and 3/7 (two-bridge + mu^3)
E2 = criterion_quotient(free_graded(7, 3, [0, 1, 2], 3, ["x", "y", "v"]))
U1, R1, _ = C.presentation([1, 1, 2, -1, -3, 2, -3], 4, 3)
U2, R2 = two_bridge(9, 2); R2 = R2 + [[(0, 1)] * 3]
cases += [("criterion quotient class 3 on (0, 1, 2) mod 3", E2, 3, "S^3_3(6_1)", U1, R1, True),
          ("criterion quotient class 3 on (0, 1, 2) mod 3", E2, 3, "S^3_(3/7)(6_1)", U2, R2, True)]
# (b) r = 6, p = 7: free class 2 on characters (1, 2, 3): criterion holds at orders 2 and 3, fails at 6
F6 = free_graded(7, 6, [1, 2, 3], 2)
U3, R3 = two_bridge(9, 2); R3 = R3 + [[(0, 1)] * 6]
U4, R4 = two_bridge(7, 3); R4 = R4 + [[(0, 1)] * 6]
cases += [("free class 2 on (1, 2, 3) mod 6", F6, 6, "S^3_(6/7)(6_1)", U3, R3, None),
          ("free class 2 on (1, 2, 3) mod 6", F6, 6, "S^3_(6/7)(5_2)", U4, R4, None)]
# (c) control: four-way at r = 4, p = 5 on 6_1 (two-bridge + mu^4, slope 4/5): a (P3) failure with a nonzero local form
FW = four_way(5, 4)
U5, R5 = two_bridge(9, 2); R5 = R5 + [[(0, 1)] * 4]
cases += [("four-way (1, -1, -1) mod 4 (control)", FW, 4, "S^3_(4/5)(6_1)", U5, R5, False)]
for name, L, r, mname, U, rels, expect in cases:
    Lb = to_bc(L, r)
    for k in range(r):
        dk = sector_order(k, r)
        crit = criterion(L.coarsen(dk)) if dk > 1 else True
        pred = predicted(Lb, U, rels, k)
        if pred > 7 ** 6 and not (expect is False): continue
        cnt = Bc.direct_count(Lb, U, rels, k)
        row = {"algebra": name, "manifold": mname, "p": L.p, "sector": k, "sector order": int(dk),
               "criterion at that order": crit, "count": cnt, "rigid formula": pred}
        if crit:
            ok &= cnt == pred
        counts.append(row)
    if expect is False:
        ctrl = [c for c in counts if c["algebra"] == name and c["sector order"] == r]
        row_ok = any(c["count"] < c["rigid formula"] for c in ctrl)
        ok &= row_ok
        counts.append({"control": name, "some full-order sector below the rigid formula": row_ok})
report("2 independent counts", ok, counts)

# ---------------------------------------------------------------- 3 class 4 on knot surgeries (braid model)
ok = True
res = []
rng = np.random.default_rng(7)
p, d = 7, 3
zeta = root_of_unity(p, d)
F4 = free_graded(p, d, [0, 1, 2], 4, ["x", "y", "v"])
Q4 = criterion_quotient(F4)
F4b = free_graded(p, d, [1, 2], 4, ["y", "v"])
knots = {"6_1": ([1, 1, 2, -1, -3, 2, -3], 4), "6_1#6_1": C.connected_sum([([1, 1, 2, -1, -3, 2, -3], 4)] * 2),
         "6_3": ([1, 1, -2, 1, -2, -2], 3)}
for kname, (w, n) in knots.items():
    for q in (1, p):
        for aname, L, expect_lift in [("criterion quotient of free class 4 on (0, 1, 2)", Q4, True),
                                      ("free class 4 on (1, 2) (control)", F4b, False)]:
            A = BraidAlg(L, zeta)
            Mo = CyclicBraidModel(w, n, A, q)
            bs = 24
            free = [k for k in range(L.D) if L.chars[k] % d]
            inputs = {k: (rng.integers(0, p, (bs, len(Mo.cocycles[int(L.chars[k])]))) @ Mo.cocycles[int(L.chars[k])]) % p
                      for k in free}
            lift, ff, _ = Mo.solve(inputs)
            row = {"knot": kname, "slope": f"{d}/{q}", "algebra": aname, "dim": L.D, "fraction lifted": float(lift.mean()),
                   "dim Z1 at zeta, zeta^2": [len(Mo.cocycles[1]), len(Mo.cocycles[2])]}
            res.append(row)
            if expect_lift:
                ok &= bool(lift.all())
ctrl = [r_ for r_ in res if "control" in r_["algebra"]]
ctrl_ok = any(r_["fraction lifted"] < 1 for r_ in ctrl)
ok &= ctrl_ok
res.append({"control obstructs somewhere": ctrl_ok, "criterion quotient": {"dim": Q4.D, "pairs": pair_failures(Q4),
                                                                         "triples": triple_failures(Q4)}})
report("3 class 4 on knot surgeries", ok, res)

out["all_ok"] = ok_all
if "--write" in sys.argv:
    with open(os.path.join(HERE, "result.json"), "w") as fh:
        json.dump({"schema_version": 1, "artifact_id": "COPRIME-DICHOTOMY-20261027-001A-P001",
                   "status": "Proved" if ok_all else "Failed", "checks": out,
                   "seconds": round(time.time() - T_START, 1)}, fh, indent=1, default=str)
        fh.write("\n")
print("ALL OK" if ok_all else "SOME CHECK FAILED", round(time.time() - T_START, 1), "s")
