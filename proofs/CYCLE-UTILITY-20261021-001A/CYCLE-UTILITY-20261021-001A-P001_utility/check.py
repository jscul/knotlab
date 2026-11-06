#!/usr/bin/env python3
"""Checks for CYCLE-UTILITY-20261021-001A-P001. The statements are in proof.md.

Checks:
- Proposition 1 (codes). The Simonis-Ashikhmin code, the row space over F_3 of a 6 x 9 matrix with entries in F_3^2
  (reproduced in Abbe and Spirkl, arXiv 1909.12175, p. 7), is rebuilt:
  - it has 729 codewords, every projection has a power of 9 elements (almost affine), and its matroid is the
    non-Pappus matroid (exactly the eight lines of rank 2, every other set of rank min(|X|, 3));
  - its own free sets satisfy elimination;
  - its only unary polymorphisms are 0, the identity and negation;
  - one copy of the code with identified coordinates defines the equivalence x - y in <(1,2)> on the alphabet;
  - the system with visible coordinates c1, c2, c4, c5 and w1, w2 attached to c1, c2 by that equivalence (three copies
    of the code in all) has the circuits {c1,w1}, {c2,w2}, {c1,c2,c4,c5}, {c1,c4,c5,w2}, {c2,c4,c5,w1}, and violates
    elimination;
  - the code's image modulo that equivalence has free sets the code does not have.
- Proposition 2 (complexity). Controls of hardness: 1-in-3, not-all-equal and 3-colouring each give an explicit system
  that violates elimination. The laws with trivial tops (Z3, parity, the GF(4) law) keep x - y + z as a polymorphism
  with all constants added.
- Proposition 4 (constants can destroy composing like cycles). Explicit systems with one constant violate elimination
  in parity beside J and in K4, both of which compose like cycles without constants. Random sampling (with constants
  drawn for a quarter of the atoms, and only systems with three or more nonconstant visible variables) finds failures
  in K4 and in parity beside J, and none in Z3, parity and the full lift, which keep x - y + z with constants.
- Proposition 3 (counting). For the lifted Z3 law and for K4 the counting matrix M(x, y) = #{z : (x, y, z) in R} is
  positive everywhere and has two non-proportional rows, so the relation is not balanced; for the Z3 law it is
  constant.

Controls, each of which must be rejected:
- 'uniform fibres of one code force a law composing like cycles' (the non-Pappus code);
- 'composing like cycles makes counting tractable' (the lifted Z3 law is not balanced);
- 'every law with a polynomial-time constraint problem composes like cycles' (x <= y fails elimination);
- 'some NP-hard law composes like cycles' (1-in-3, not-all-equal and 3-colouring all fail);
- 'adding constants preserves composing like cycles' (parity beside J, and K4).

    python3 -B check.py          verify result.json against a fresh run
    python3 -B check.py --write  write result.json
"""

from __future__ import annotations

import json
import math
import random
import sys
from itertools import combinations, product
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]

ROWS = """10 10 00 10 00 10 10 10 00
01 01 00 01 00 01 01 01 00
00 00 00 10 10 21 01 10 10
00 00 00 02 01 20 12 02 01
00 10 10 01 00 01 00 11 10
00 01 01 21 00 21 00 10 01"""
NON_PAPPUS_LINES = {(1, 2, 3), (4, 5, 6), (1, 5, 7), (1, 6, 8), (2, 4, 7), (2, 6, 9), (3, 4, 8), (3, 5, 9)}
THETA_SYSTEM = [5, 3, 0, 3, 1, 5, 4, 5, 2]       # coordinate j of one copy -> variable; visible variables 3 and 5
THETA_VISIBLE = (3, 5)

M3 = sorted(t for t in product(range(3), repeat=3) if sum(t) % 3 == 0)
G = (0, 1, 2, 2)
LIFT = sorted(t for t in product(range(4), repeat=3) if tuple(G[x] for x in t) in set(M3))


# ------------------------------------------------------------------ helpers

def free_map(S, n):
    rg = [len({s[v] for s in S}) for v in range(n)]
    fr = {}
    for k in range(1, n + 1):
        for Y in combinations(range(n), k):
            need = 1
            for v in Y:
                need *= rg[v]
            fr[Y] = len({tuple(s[v] for v in Y) for s in S}) == need
    return fr


def circuits(fr):
    return [Y for Y in fr if len(Y) > 1 and not fr[Y] and all(fr[tuple(u for u in Y if u != w)] for w in Y)]


def elimination_failures(fr):
    cs = circuits(fr)
    out = []
    for C1, C2 in combinations(cs, 2):
        for y in sorted(set(C1) & set(C2)):
            if fr[tuple(sorted((set(C1) | set(C2)) - {y}))]:
                out.append((C1, C2, y))
    return cs, out


def solve(rels, domains, cons):
    """All solutions of a system; domains[v] lists values of variable v; cons are (relation set, variables)."""
    n = len(domains)
    order = []
    for _, vs in cons:
        for v in vs:
            if v not in order:
                order.append(v)
    order += [v for v in range(n) if v not in order]
    pos = {v: i for i, v in enumerate(order)}
    by_last = {}
    for R, vs in cons:
        by_last.setdefault(max(pos[v] for v in vs), []).append((R, vs))
    out, a = [], [0] * n

    def go(i):
        if i == n:
            out.append(tuple(a))
            return
        v = order[i]
        for x in domains[v]:
            a[v] = x
            if all(tuple(a[u] for u in vs) in R for R, vs in by_last.get(i, ())):
                go(i + 1)
    go(0)
    return out


def cycle_tops_laws():
    out = {}
    for X in ((), ((2, 2, 2),), ((2, 2, 3),), ((2, 2, 3), (2, 3, 2)), ((2, 2, 3), (2, 3, 2), (3, 2, 2))):
        out["L-{" + ",".join("".join(map(str, t)) for t in X) + "}"] = (4, [sorted(set(LIFT) - set(X))])
    not_two = {t for t in product((0, 1), repeat=3) if sum(t) != 2}
    K6 = {tuple(2 * a + b for a, b in zip(u, w)) for u in M3 for w in not_two}
    for a in (0, 1):
        g7 = list(range(6)) + [a]
        out[f"K6 lift at {a}"] = (7, [sorted({t for t in product(range(7), repeat=3) if tuple(g7[x] for x in t) in K6} - {(a, a, a)})])
    P3 = sorted(t for t in product((0, 1), repeat=3) if sum(t) % 2 == 0)
    out["parity + J"] = (5, [P3, [(2, 2), (3, 3), (3, 4), (4, 3)]])
    K4 = sorted(set(LIFT) - {(2, 2, 2)})
    out["K4 + Z3"] = (7, [K4, sorted(tuple(x + 4 for x in t) for t in M3)])
    out["parity"] = (2, [P3])
    out["Z3"] = (3, [M3])
    return out


# ------------------------------------------------------------------ run

def run():
    checks, controls, failures = {}, {}, []

    # Proposition 1: the non-Pappus code
    Mx = [[(int(e[0]), int(e[1])) for e in r.split()] for r in ROWS.splitlines()]
    enc = lambda v: 3 * v[0] + v[1]
    dec = [(x // 3, x % 3) for x in range(9)]
    C = set()
    for coeffs in product(range(3), repeat=6):
        w = [(0, 0)] * 9
        for c, r in zip(coeffs, Mx):
            w = [((w[j][0] + c * r[j][0]) % 3, (w[j][1] + c * r[j][1]) % 3) for j in range(9)]
        C.add(tuple(enc(v) for v in w))
    Cl = sorted(C)
    rank, almost_affine = {}, True
    for k in range(1, 10):
        for Y in combinations(range(9), k):
            s = len({tuple(c[j] for j in Y) for c in Cl})
            r = round(math.log(s, 9))
            almost_affine = almost_affine and 9 ** r == s
            rank[Y] = r
    lines = {tuple(i + 1 for i in Y) for Y in rank if len(Y) == 3 and rank[Y] == 2}
    non_pappus = lines == NON_PAPPUS_LINES and all(rank[Y] == min(len(Y), 3) for Y in rank
                                                    if tuple(i + 1 for i in Y) not in NON_PAPPUS_LINES)
    code_fr = {Y: rank[Y] == len(Y) for Y in rank}
    _, code_fail = elimination_failures(code_fr)
    # unary polymorphisms
    unary, f = [], [None] * 9

    def consistent():
        return all(tuple(f[v] for v in c) in C for c in Cl if all(f[v] is not None for v in c))

    def go(i):
        if i == 9:
            unary.append(tuple(f))
            return
        for val in range(9):
            f[i] = val
            if consistent():
                go(i + 1)
        f[i] = None
    go(0)
    neg = tuple(enc(((-dec[x][0]) % 3, (-dec[x][1]) % 3)) for x in range(9))
    # the equivalence defined by one copy
    theta = set()
    for c in Cl:
        val, ok = {}, True
        for j in range(9):
            v = THETA_SYSTEM[j]
            if v in val and val[v] != c[j]:
                ok = False
                break
            val[v] = c[j]
        if ok:
            theta.add((val[THETA_VISIBLE[0]], val[THETA_VISIBLE[1]]))
    diff = lambda a, b: ((dec[a][0] - dec[b][0]) % 3, (dec[a][1] - dec[b][1]) % 3)
    line = {(0, 0), (1, 2), (2, 1)}
    theta_is_line = theta == {(a, b) for a in range(9) for b in range(9) if diff(a, b) in line}
    # the failing system: visible c1, c2, c4, c5, w1, w2
    proj = {(c[0], c[1], c[3], c[4]) for c in Cl}
    S = {p + (w1, w2) for p in proj for w1 in range(9) for w2 in range(9) if (p[0], w1) in theta and (p[1], w2) in theta}
    names = ["c1", "c2", "c4", "c5", "w1", "w2"]
    cs, fl = elimination_failures(free_map(S, 6))
    # the image modulo the equivalence
    cls = {}
    for a in range(9):
        cls.setdefault(min(b for b in range(9) if (a, b) in theta), len(cls))
    cl = {a: cls[min(b for b in range(9) if (a, b) in theta)] for a in range(9)}
    image = {tuple(cl[x] for x in c) for c in Cl}
    image_fr = free_map(image, 9)
    differ = sorted(tuple(i + 1 for i in Y) for Y in image_fr if image_fr[Y] != code_fr[Y])
    prop1 = {"codewords": len(Cl), "almost_affine": almost_affine, "non_pappus": non_pappus,
             "code_alone_satisfies_elimination": not code_fail, "unary_polymorphisms": len(unary),
             "unary_are_zero_identity_negation": sorted(unary) == sorted([tuple([0] * 9), tuple(range(9)), neg]),
             "theta_is_line_congruence": theta_is_line, "theta_pairs": len(theta),
             "failing_system_tuples": len(S), "failing_system_circuits": [[names[v] for v in C] for C in cs],
             "failing_system_failures": [[[names[v] for v in C1], [names[v] for v in C2], names[y]] for C1, C2, y in fl],
             "image_sets_with_other_freeness": len(differ), "example": differ[:3]}
    checks["proposition_1"] = prop1
    if not (len(Cl) == 729 and almost_affine and non_pappus and not code_fail and prop1["unary_are_zero_identity_negation"]
            and theta_is_line and fl and differ):
        failures.append("Proposition 1")

    # Proposition 2: hardness controls and trivial-top laws with constants
    def two_copy_failure(R, D, shape):
        doms = [list(range(D))] * shape[0]
        S2 = solve(None, doms, [(set(R), vs) for vs in shape[1]])
        S2 = {tuple(s[v] for v in shape[2]) for s in S2}
        cs2, fl2 = elimination_failures(free_map(S2, len(shape[2])))
        return bool(fl2), [list(C) for C in cs2]
    one_in_three = [(1, 0, 0), (0, 1, 0), (0, 0, 1)]
    nae = [t for t in product((0, 1), repeat=3) if len(set(t)) > 1]
    neq3 = [(a, b) for a in range(3) for b in range(3) if a != b]
    hard = {
        "one_in_three": two_copy_failure(one_in_three, 2, (5, [(0, 1, 3), (2, 1, 4)], (0, 1, 2))),
        "not_all_equal": two_copy_failure(nae, 2, (4, [(0, 2, 3), (1, 2, 3)], (0, 1, 2, 3))),
        "three_colouring": two_copy_failure(neq3, 3, (3, [(0, 1), (1, 2)], (0, 1, 2))),
    }
    gf4 = lambda a, b: 0 if a == 0 or b == 0 else {0: 1, 1: 2, 2: 3}[({1: 0, 2: 1, 3: 2}[a] + {1: 0, 2: 1, 3: 2}[b]) % 3]
    trivial_top_laws = {
        "Z3": (3, [M3], lambda x, y, z: (x - y + z) % 3),
        "parity": (2, [sorted(t for t in product((0, 1), repeat=3) if sum(t) % 2 == 0)], lambda x, y, z: x ^ y ^ z),
        "GF(4)": (4, [sorted((x, y, x ^ gf4(2, y)) for x in range(4) for y in range(4))], lambda x, y, z: x ^ y ^ z),
    }
    maltsev_with_constants = {}
    for name, (D, rels, m) in trivial_top_laws.items():
        rels_c = rels + [[(a,)] for a in range(D)]
        maltsev_with_constants[name] = all(tuple(m(a[i], b[i], c[i]) for i in range(len(R[0]))) in set(R)
                                           for R in rels_c for a in R for b in R for c in R)
    checks["proposition_2"] = {"hard_laws_fail": {k: v[0] for k, v in hard.items()},
                               "hard_law_circuits": {k: v[1] for k, v in hard.items()},
                               "maltsev_with_constants": maltsev_with_constants}
    if not (all(v[0] for v in hard.values()) and all(maltsev_with_constants.values())):
        failures.append("Proposition 2")

    # Proposition 4: constants can destroy composing like cycles
    laws = cycle_tops_laws()
    P3 = laws["parity"][1][0]
    J = laws["parity + J"][1][1]
    K4 = laws["L-{222}"][1][0]

    def explicit(D, cons, n, keep):
        S4 = solve(None, [list(range(D))] * n, [(set(R), vs) for R, vs in cons])
        S4 = {tuple(s[v] for v in keep) for s in S4}
        cs4, fl4 = elimination_failures(free_map(S4, len(keep)))
        return {"tuples": sorted(S4) if len(S4) <= 12 else len(S4), "circuits": [list(C) for C in cs4],
                "failures": [[list(a), list(b), y] for a, b, y in fl4]}
    # parity beside J: J(x0, x1), J(x2, x0), x1 = 3, J(x0, x3); visible x0, x2, x3
    pj = explicit(5, [(J, (0, 1)), (J, (2, 0)), ([(3,)], (1,)), (J, (0, 3))], 4, [0, 2, 3])
    # K4: K4(x0, x1, x1), K4(x1, x2, x3), K4(x3, x3, x1), x2 = 2; visible x0, x1, x2, x3
    k4 = explicit(4, [(K4, (0, 1, 1)), (K4, (1, 2, 3)), (K4, (3, 3, 1)), ([(2,)], (2,))], 4, [0, 1, 2, 3])
    # parity beside J and K4 without constants are census survivors; sampling with constants
    rng = random.Random("cycle-utility-constants")
    sampled = {}
    for name in ("parity + J", "L-{222}", "Z3", "parity", "L-{}"):
        D, rels = laws[name]
        main = [set(R) for R in rels]
        systems, fails = 0, 0
        while systems < 150:
            n, cons, uses = 0, [], 0
            for _ in range(rng.randint(2, 5)):
                if n > 0 and rng.random() < 0.25:
                    cons.append(({(rng.randrange(D),)}, (rng.randrange(n),)))
                    uses += 1
                    continue
                R = rng.choice(main)
                vs = []
                for _ in range(len(next(iter(R)))):
                    if n == 0 or (n < 7 and rng.random() < 0.5):
                        vs.append(n)
                        n += 1
                    else:
                        vs.append(rng.randrange(n))
                cons.append((R, tuple(vs)))
            if uses == 0:
                continue
            S5 = solve(None, [list(range(D))] * n, cons)
            if not S5:
                continue
            keep = [v for v in range(n) if rng.random() < 0.75]
            S5 = {tuple(s[v] for v in keep) for s in S5}
            if sum(1 for v in range(len(keep)) if len({s[v] for s in S5}) > 1) < 3:
                continue
            systems += 1
            fails += bool(elimination_failures(free_map(S5, len(keep)))[1])
        sampled[name] = {"systems": systems, "failures": fails}
    checks["proposition_4"] = {"parity_J_with_constant_3": pj, "k4_with_constant_2": k4, "sampled": sampled}
    if not (pj["failures"] and k4["failures"] and sampled["parity + J"]["failures"] and sampled["L-{222}"]["failures"]):
        failures.append("Proposition 4")

    # Proposition 3: counting matrices
    def counting(R, D):
        Mm = [[sum(1 for z in range(D) if (x, y, z) in R) for y in range(D)] for x in range(D)]
        positive = all(v > 0 for row in Mm for v in row)
        nonprop = any(Mm[a][i] * Mm[b][j] != Mm[a][j] * Mm[b][i] for a in range(D) for b in range(D) for i in range(D) for j in range(D))
        return Mm, positive, nonprop
    lift_m, lift_pos, lift_np = counting(set(LIFT), 4)
    k4_m, k4_pos, k4_np = counting(set(LIFT) - {(2, 2, 2)}, 4)
    z3_m, z3_pos, z3_np = counting(set(M3), 3)
    checks["proposition_3"] = {"lift_matrix": lift_m, "lift_one_block_rank_above_one": lift_pos and lift_np,
                               "k4_matrix": k4_m, "k4_one_block_rank_above_one": k4_pos and k4_np,
                               "z3_matrix": z3_m, "z3_rank_one": z3_pos and not z3_np}
    if not (lift_pos and lift_np and k4_pos and k4_np and z3_pos and not z3_np):
        failures.append("Proposition 3")

    # controls
    controls["uniform_fibres_force_composition_like_cycles"] = {"rejected": almost_affine and bool(fl)}
    controls["composing_like_cycles_makes_counting_tractable"] = {"rejected": lift_pos and lift_np}
    le = two_copy_failure([(0, 0), (0, 1), (1, 1)], 2, (3, [(0, 2), (1, 2)], (0, 1, 2)))
    controls["every_tractable_law_composes_like_cycles"] = {"x_le_y_fails": le[0], "rejected": le[0]}
    controls["some_np_hard_law_composes_like_cycles"] = {"rejected": all(v[0] for v in hard.values())}
    controls["adding_constants_preserves_composing_like_cycles"] = {"rejected": bool(pj["failures"] and k4["failures"])}
    for k, v in controls.items():
        if not v["rejected"]:
            failures.append(f"control not rejected: {k}")
    return checks, controls, failures


def main() -> int:
    write = "--write" in sys.argv[1:]
    checks, controls, failures = run()
    manifest = json.loads((HERE / "manifest.json").read_text())
    result = {
        "schema_version": 3, "artifact_id": manifest["artifact_id"], "kind": "proof", "ticket": manifest["ticket"],
        "proof": manifest["proof"], "status": "passed" if not failures else "failed", "claim": manifest["claim"],
        "foundation_contract": manifest["foundation_contract"], "semantic_domains": manifest["semantic_domains"],
        "evidence_modes": manifest["evidence_modes"], "thesis_alignment": manifest["thesis_alignment"],
        "safe_conclusions": manifest["safe_to_conclude"], "checks": checks, "controls": controls, "failures": failures,
    }
    path = HERE / "result.json"
    text = json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False, default=str) + "\n"
    if write:
        path.write_text(text)
    elif not path.exists() or json.loads(path.read_text()) != json.loads(text):
        print("result.json does not match a fresh run; rerun with --write after review")
        return 1
    print(f"{result['status']}: failures {failures}")
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
