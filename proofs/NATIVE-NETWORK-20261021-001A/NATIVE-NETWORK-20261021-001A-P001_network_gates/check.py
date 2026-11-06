#!/usr/bin/env python3
"""Checks for NATIVE-NETWORK-20261021-001A-P001. The statements are in proof.md.

A pair is a system of two knots that share exactly one distinction e, with the same range in both:
K(x1, x2, e) and K(y1, y2, e), with e in any of the three positions of each copy (nine placements).

Checks:
- Theorem 1(a)-(e). For the main knot of every census law composing like cycles (eleven laws), in all nine placements:
  the knot passes K1-K3; with e visible the pair's circuits are exactly the two knots and {x1, x2, y1, y2}; with e
  forgotten the only circuit is {x1, x2, y1, y2}, so nothing is lost, nothing is tied, and the pair is no hub.
  The same holds after a random relabelling of the values (recoding).
- Theorem 1(f). Random systems of each census law (with hidden variables, so erasure and restriction by the law's own
  relations) satisfy elimination. With constants added, random systems of the affine laws x + y + z = 0 over F2, F3
  and F5 satisfy elimination, while parity beside J and K4 each violate it in an explicit pinned system.
- Theorem 1(g). Random systems of parity expanded by its pp-definable relation x + y + z + w = 0 satisfy elimination;
  the equal-top lift of K3 does on random systems while K3 itself does not (x != e != z); the 3-net of Z6 = Z2 x Z3
  violates it (ties modulo 2 and 3).
- Remarks. The 3-net of S3 passes the pair test in all nine placements, yet its law violates elimination in Thomsen's
  configuration doubled; two not-all-three knots sharing e form a hub.

Controls, each of which must be rejected:
- 'a pair of knots in a law composing like cycles can be a common hub';
- 'pinning preserves composing like cycles in every such law' (parity beside J, K4);
- 'homomorphic equivalence transports composing like cycles' (the lift of K3 and K3);
- 'products transport composing like cycles' (Z6);
- 'a law whose pairs all pass composes like cycles' (S3);
- 'every pair of knots sharing one distinction passes the hub test' (not-all-three).

    python3 -B check.py          verify result.json against a fresh run
    python3 -B check.py --write  write result.json
"""

from __future__ import annotations

import json
import math
import random
import sys
from itertools import combinations, permutations, product
from pathlib import Path

HERE = Path(__file__).resolve().parent

# ------------------------------------------------------------------ laws

M3 = sorted(t for t in product(range(3), repeat=3) if sum(t) % 3 == 0)
LIFT_MAP = (0, 1, 2, 2)
LIFT = sorted(t for t in product(range(4), repeat=3) if tuple(LIFT_MAP[x] for x in t) in set(M3))
P3 = sorted(t for t in product((0, 1), repeat=3) if sum(t) % 2 == 0)


def census_laws():
    """The census laws composing like cycles of CYCLE-TOPS-20261021-001, as (domain size, relations)."""
    out = {}
    for X in ((), ((2, 2, 2),), ((2, 2, 3),), ((2, 2, 3), (2, 3, 2)), ((2, 2, 3), (2, 3, 2), (3, 2, 2))):
        out["L-{" + ",".join("".join(map(str, t)) for t in X) + "}"] = (4, [sorted(set(LIFT) - set(X))])
    not_two = {t for t in product((0, 1), repeat=3) if sum(t) != 2}
    K6 = {tuple(2 * a + b for a, b in zip(u, w)) for u in M3 for w in not_two}
    for a in (0, 1):
        g7 = list(range(6)) + [a]
        out[f"K6 lift at {a}"] = (7, [sorted({t for t in product(range(7), repeat=3)
                                             if tuple(g7[x] for x in t) in K6} - {(a, a, a)})])
    out["parity + J"] = (5, [P3, [(2, 2), (3, 3), (3, 4), (4, 3)]])
    out["K4 + Z3"] = (7, [sorted(set(LIFT) - {(2, 2, 2)}), sorted(tuple(x + 4 for x in t) for t in M3)])
    out["parity"] = (2, [P3])
    out["Z3"] = (3, [M3])
    return out


def affine(p):
    return sorted(t for t in product(range(p), repeat=3) if sum(t) % p == 0)


# ------------------------------------------------------------------ systems

def solve(D, n, cons):
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
        for x in range(D):
            a[v] = x
            if all(tuple(a[u] for u in vs) in R for R, vs in by_last.get(i, ())):
                go(i + 1)
    go(0)
    return out


def free_map(S, n):
    rg = [len({s[v] for s in S}) for v in range(n)]
    fr = {}
    for k in range(1, n + 1):
        for Y in combinations(range(n), k):
            fr[Y] = len({tuple(s[v] for v in Y) for s in S}) == math.prod(rg[v] for v in Y)
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


def system_circuits(D, cons, n, visible):
    S = solve(D, n, [(set(R), vs) for R, vs in cons])
    P = {tuple(s[v] for v in visible) for s in S}
    return elimination_failures(free_map(P, len(visible))) if P else ([], [])


def is_knot(R):
    """K1-K3 on allowed states, relative to the ranges."""
    R = set(map(tuple, R))
    ar = len(next(iter(R)))
    rg = [len({t[i] for t in R}) for i in range(ar)]
    if min(rg) < 2 or len(R) == math.prod(rg):
        return False
    return all(len({tuple(t[i] for i in range(ar) if i != d) for t in R}) == math.prod(rg[i] for i in range(ar) if i != d)
               for d in range(ar))


def pair(R, i, j):
    """K(x1, x2, e) and K(y1, y2, e) with e = variable 4 at position i of the first copy and j of the second."""
    v1, v2 = [0, 1], [2, 3]
    v1.insert(i, 4)
    v2.insert(j, 4)
    return [(R, tuple(v1)), (R, tuple(v2))]


def random_system(rng, rels, nmax, consts=None, pin_prob=0.0):
    n, cons = 0, []
    for _ in range(rng.randint(1, 4)):
        R = rng.choice(rels)
        vs = []
        for _ in range(len(R[0])):
            if n == 0 or (n < nmax and rng.random() < 0.5):
                vs.append(n)
                n += 1
            else:
                vs.append(rng.randrange(n))
        cons.append((R, tuple(vs)))
    if consts:
        for v in range(n):
            if rng.random() < pin_prob:
                cons.append(([(rng.choice(consts),)], (v,)))
    return n, cons


def sample_laws(rng, D, rels, systems, nmax=6, consts=None, pin_prob=0.0):
    st = {"systems": 0, "nonempty": 0, "elimination_failures": 0}
    while st["systems"] < systems:
        n, cons = random_system(rng, rels, nmax, consts, pin_prob)
        S = solve(D, n, [(set(R), vs) for R, vs in cons])
        st["systems"] += 1
        if not S:
            continue
        keep = sorted(rng.sample(range(n), max(1, min(n, rng.randint(2, 5)))))
        P = {tuple(s[v] for v in keep) for s in S}
        st["nonempty"] += 1
        st["elimination_failures"] += bool(elimination_failures(free_map(P, len(keep)))[1])
    return st


# ------------------------------------------------------------------ run

def run():
    checks, controls, failures = {}, {}, []
    rng = random.Random("native-network-gates")
    laws = census_laws()

    # Theorem 1(a)-(e): pairs of the main knot of every census law, and a recoding
    pairs = {}
    for name, (D, rels) in laws.items():
        R = rels[0]
        st = {"knot": is_knot(R), "placements": 0, "three_circuits_with_e": 0, "one_knot_after_forgetting_e": 0,
              "hubs": 0, "ties": 0, "recoded_placements_agree": 0}
        perm = list(range(D))
        rng.shuffle(perm)
        Rre = sorted(tuple(perm[x] for x in t) for t in R)
        for i, j in product(range(3), repeat=2):
            cons = pair(R, i, j)
            with_e, _ = system_circuits(D, cons, 5, [0, 1, 2, 3, 4])
            without_e, _ = system_circuits(D, cons, 5, [0, 1, 2, 3])
            st["placements"] += 1
            st["three_circuits_with_e"] += sorted(with_e) == [(0, 1, 2, 3), (0, 1, 4), (2, 3, 4)]
            st["one_knot_after_forgetting_e"] += without_e == [(0, 1, 2, 3)]
            st["hubs"] += (0, 1, 2, 3) not in without_e and not any(len(c) > 1 for c in without_e)
            st["ties"] += sum(len(c) == 2 for c in with_e + without_e)
            re_with, _ = system_circuits(D, pair(Rre, i, j), 5, [0, 1, 2, 3, 4])
            st["recoded_placements_agree"] += sorted(re_with) == sorted(with_e)
        pairs[name] = st
    checks["theorem_1_pairs"] = pairs
    if not all(s["knot"] and s["three_circuits_with_e"] == s["one_knot_after_forgetting_e"] == s["placements"] == 9
               and s["hubs"] == 0 and s["ties"] == 0 and s["recoded_placements_agree"] == 9 for s in pairs.values()):
        failures.append("Theorem 1(a)-(e)")

    # Theorem 1(f): persistence under erasure, restriction and pinning
    restricted = {name: sample_laws(rng, D, rels, 60) for name, (D, rels) in laws.items()}
    pinned = {}
    for p in (2, 3, 5):
        pinned[f"x + y + z = 0 over F{p}, with constants"] = sample_laws(
            rng, p, [affine(p)], 80, nmax=5 if p == 5 else 6, consts=list(range(p)), pin_prob=0.25)
    J = laws["parity + J"][1][1]
    K4 = laws["L-{222}"][1][0]
    _, pj = system_circuits(5, [(J, (0, 1)), (J, (2, 0)), ([(3,)], (1,)), (J, (0, 3))], 4, [0, 2, 3])
    _, k4 = system_circuits(4, [(K4, (0, 1, 1)), (K4, (1, 2, 3)), (K4, (3, 3, 1)), ([(2,)], (2,))], 4, [0, 1, 2, 3])
    checks["theorem_1_persistence"] = {
        "law_systems": restricted, "pinned_affine": pinned,
        "parity_beside_J_with_constant_3_failures": len(pj), "K4_with_constant_2_failures": len(k4)}
    if not (all(s["elimination_failures"] == 0 and s["nonempty"] > 0 for s in restricted.values())
            and all(s["elimination_failures"] == 0 and s["nonempty"] > 0 for s in pinned.values()) and pj and k4):
        failures.append("Theorem 1(f)")

    # Theorem 1(g): transports
    P4 = sorted(t for t in product((0, 1), repeat=4) if sum(t) % 2 == 0)
    S4 = solve(2, 5, [(set(P3), (0, 1, 4)), (set(P3), (4, 2, 3))])
    pp_defined = {tuple(s[:4]) for s in S4} == set(P4)
    expanded = sample_laws(rng, 2, [P3, P4], 80)
    K3 = [(x, y) for x in range(3) for y in range(3) if x != y]
    lift = [(a * 3 + x, a * 3 + y) for a in range(2) for x, y in K3]
    lift_sampled = sample_laws(rng, 6, [lift], 80)
    _, k3_fail = system_circuits(3, [(K3, (0, 1)), (K3, (1, 2))], 3, [0, 1, 2])
    Z6 = sorted((a, m, (a + m) % 6) for a in range(6) for m in range(6))
    _, z6_fail = system_circuits(6, [(Z6, (0, 3, 4)), (Z6, (4, 3, 1)), (Z6, (1, 5, 6)), (Z6, (6, 5, 7)), (Z6, (7, 5, 2))],
                                 8, [0, 1, 2])
    checks["theorem_1_transports"] = {
        "x+y+z+w=0_is_pp_definable_in_parity": pp_defined, "parity_expanded_by_it": expanded,
        "lift_of_K3_sampled": lift_sampled, "K3_failures": len(k3_fail), "Z6_failures": len(z6_fail)}
    if not (pp_defined and expanded["elimination_failures"] == 0 and lift_sampled["elimination_failures"] == 0
            and k3_fail and z6_fail):
        failures.append("Theorem 1(g)")

    # remarks: S3 passes the pair test but its law fails; not-all-three pairs are hubs
    S3 = list(permutations(range(3)))
    idx = {g: i for i, g in enumerate(S3)}
    RS3 = sorted((i, j, idx[tuple(S3[i][S3[j][x]] for x in range(3))]) for i in range(6) for j in range(6))
    s3_pairs = sum(system_circuits(6, pair(RS3, i, j), 5, [0, 1, 2, 3])[0] == [(0, 1, 2, 3)]
                   for i, j in product(range(3), repeat=2))

    def thomsen(x1, x2, x3, y1, y2, y3, l1, l2, l3):
        return [(RS3, (x1, y2, l1)), (RS3, (x2, y1, l1)), (RS3, (x1, y3, l2)), (RS3, (x3, y1, l2)),
                (RS3, (x2, y3, l3)), (RS3, (x3, y2, l3))]
    _, s3_fail = system_circuits(6, thomsen(0, 1, 2, 4, 5, 6, 7, 8, 9) + thomsen(0, 1, 3, 10, 11, 12, 13, 14, 15),
                                 16, [0, 1, 2, 3])
    NAND = [t for t in product((0, 1), repeat=3) if t != (1, 1, 1)]
    nand_with, nand_fail = system_circuits(2, pair(NAND, 2, 2), 5, [0, 1, 2, 3, 4])
    nand_without, _ = system_circuits(2, pair(NAND, 2, 2), 5, [0, 1, 2, 3])
    checks["remarks"] = {"S3_pairs_one_knot": s3_pairs, "S3_doubled_Thomsen_failures": len(s3_fail),
                         "not_all_three_pair_circuits": [list(c) for c in nand_with],
                         "not_all_three_after_forgetting_e": [list(c) for c in nand_without],
                         "not_all_three_failures": len(nand_fail)}
    if not (s3_pairs == 9 and s3_fail and nand_fail and not nand_without):
        failures.append("remarks")

    controls["pair_in_cycle_composing_law_can_be_hub"] = {"rejected": all(s["hubs"] == 0 for s in pairs.values())}
    controls["pinning_preserves_cycle_composition_in_every_such_law"] = {"rejected": bool(pj and k4)}
    controls["homomorphic_equivalence_transports_cycle_composition"] = {
        "rejected": lift_sampled["elimination_failures"] == 0 and bool(k3_fail)}
    controls["products_transport_cycle_composition"] = {"rejected": bool(z6_fail)}
    controls["law_whose_pairs_pass_composes_like_cycles"] = {"rejected": s3_pairs == 9 and bool(s3_fail)}
    controls["every_pair_passes_hub_test"] = {"rejected": not nand_without}
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
