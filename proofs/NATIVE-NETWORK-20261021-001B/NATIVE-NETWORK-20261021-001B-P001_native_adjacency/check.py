#!/usr/bin/env python3
"""Checks for NATIVE-NETWORK-20261021-001B-P001. The statements are in proof.md.

A declared substrate is one system of a law; its visible distinctions carry the matroid of its free sets. Circuits of
three or more distinctions are contacts (bonds), circuits of two are ties. A route joins x to y through circuits that
share distinctions; the bond distance is the least size of a circuit containing x and y, minus one.

Checks:
- Theorems 1 and 2. On random systems of the eleven census laws composing like cycles and of two affine laws: every
  two distinctions joined by a route lie on one common circuit; the bond distance satisfies the triangle inequality;
  its finite classes are the route classes. Two not-all-three knots sharing a distinction violate both.
- Theorem 2 (chains). For chains of k atoms {e_(i-1), l_i, e_i} in eight laws composing like cycles, the circuits are
  exactly the runs {e_i, l_(i+1), ..., l_j, e_j}, so the bond distance from e_i to e_j is j - i + 1.
- Theorem 3. In affine laws over F2, F3 and F5: erasing a variable leaves the circuits that avoid it, and pinning it
  leaves the minimal nonempty traces C - z of two or more elements (random systems; a one-element trace is a variable
  that the pin makes single-valued, hence free). In a chain of four atoms: erasing the shared interior
  leaves one bond on the ends and the private loops; erasing a private loop separates the ends; pinning a shared
  distinction separates them and ties its two neighbours in each atom; pinning a private loop ties its neighbours and
  shortens the end-to-end bond by one.
- Theorem 4. The triangle of three parity contacts has the matroid of K4; its 24 automorphisms are transitive on the
  six distinctions and carry the drawn contact {A, B, k1} to the loop's knot {k1, k2, k3}.
- Theorem 5. Parity has a substrate with the Fano matroid (not graphic) and the 3-net of Z3 one with U(2,4) (not binary).

Controls, each of which must be rejected:
- 'routes compose in every substrate' and 'bond size minus one is a metric in every substrate' (not-all-three);
- 'erasing a chain's shared distinctions separates its ends';
- 'pinning a private loop separates a chain's ends';
- 'allowed states tell drawn contacts from a loop's knot';
- 'the parity law fixes a graph'.

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


def net(p):
    """The 3-net of Z_p: z = x + y."""
    return sorted((a, b, (a + b) % p) for a in range(p) for b in range(p))


def zero_sum(p):
    return sorted(t for t in product(range(p), repeat=3) if sum(t) % p == 0)


# ------------------------------------------------------------------ systems and matroids

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
    fr = {(): True}
    for k in range(1, n + 1):
        for Y in combinations(range(n), k):
            fr[Y] = len({tuple(s[v] for v in Y) for s in S}) == math.prod(rg[v] for v in Y)
    return fr


def circuits(fr):
    return sorted((Y for Y in fr if len(Y) > 1 and not fr[Y] and all(fr[tuple(u for u in Y if u != w)] for w in Y)),
                  key=lambda c: (len(c), c))


def matroid(D, cons, n, visible):
    S = solve(D, n, [(set(R), vs) for R, vs in cons])
    P = {tuple(s[v] for v in visible) for s in S}
    if not P:
        return None
    fr = free_map(P, len(visible))
    return fr, circuits(fr)


def bond_distance(cs, m):
    INF = math.inf
    d = [[0 if i == j else INF for j in range(m)] for i in range(m)]
    for C in cs:
        for a, b in combinations(C, 2):
            d[a][b] = d[b][a] = min(d[a][b], len(C) - 1)
    return d


def route_classes(cs, m):
    parent = list(range(m))

    def find(x):
        while parent[x] != x:
            x = parent[x]
        return x
    for C in cs:
        for v in C[1:]:
            parent[find(v)] = find(C[0])
    return [find(v) for v in range(m)]


def analyse(cs, m):
    d = bond_distance(cs, m)
    cls = route_classes(cs, m)
    pairs = [(x, y) for x in range(m) for y in range(x + 1, m) if cls[x] == cls[y]]
    composed = all(d[x][y] < math.inf for x, y in pairs)
    triangle = all(d[x][z] <= d[x][y] + d[y][z] for x in range(m) for y in range(m) for z in range(m))
    classes_match = all((d[x][y] < math.inf) == (cls[x] == cls[y]) for x in range(m) for y in range(m))
    return {"route_pairs": len(pairs), "routes_compose": composed, "triangle": triangle, "classes_match": classes_match}


def random_system(rng, rels, nmax):
    n, cons = 0, []
    for _ in range(rng.randint(2, 4)):
        R = rng.choice(rels)
        vs = []
        for _ in range(len(R[0])):
            if n == 0 or (n < nmax and rng.random() < 0.55):
                vs.append(n)
                n += 1
            else:
                vs.append(rng.randrange(n))
        cons.append((R, tuple(vs)))
    return n, cons


def chain(R, k):
    """Atoms (e_(i-1), l_i, e_i); variables e_i = 2i, l_i = 2i - 1."""
    return [(R, (2 * i - 2, 2 * i - 1, 2 * i)) for i in range(1, k + 1)], 2 * k + 1


def chain_runs(k):
    """The runs {e_i, l_(i+1), ..., l_j, e_j} as sets of variable indices."""
    out = []
    for i in range(k):
        for j in range(i + 1, k + 1):
            out.append(tuple([2 * i] + [2 * m - 1 for m in range(i + 1, j + 1)] + [2 * j]))
    return sorted((tuple(sorted(c)) for c in out), key=lambda c: (len(c), c))


# ------------------------------------------------------------------ run

def run():
    checks, controls, failures = {}, {}, []
    rng = random.Random("native-network-adjacency")
    laws = census_laws()
    laws["Z3 3-net"] = (3, [net(3)])
    laws["x + y + z = 0 over F5"] = (5, [zero_sum(5)])

    # Theorems 1 and 2 on random systems
    thm12 = {}
    for name, (D, rels) in laws.items():
        st = {"systems": 0, "nonempty": 0, "route_pairs": 0, "routes_compose": 0, "triangle": 0, "classes_match": 0}
        while st["systems"] < 40:
            n, cons = random_system(rng, rels, 6)
            st["systems"] += 1
            vis = sorted(rng.sample(range(n), max(2, min(n, rng.randint(3, 6))))) if n >= 2 else [0]
            res = matroid(D, cons, n, vis)
            if res is None:
                continue
            a = analyse(res[1], len(vis))
            st["nonempty"] += 1
            st["route_pairs"] += a["route_pairs"]
            for k in ("routes_compose", "triangle", "classes_match"):
                st[k] += a[k]
        thm12[name] = st
    NAND = [t for t in product((0, 1), repeat=3) if t != (1, 1, 1)]
    _, hub_cs = matroid(2, [(NAND, (0, 1, 4)), (NAND, (2, 3, 4))], 5, [0, 1, 2, 3, 4])
    hub = analyse(hub_cs, 5)
    hub["circuits"] = [list(c) for c in hub_cs]
    thm12["not-all-three hub"] = hub
    checks["theorems_1_2_random"] = thm12
    ok12 = all(s["routes_compose"] == s["triangle"] == s["classes_match"] == s["nonempty"] > 0
               for k, s in thm12.items() if k != "not-all-three hub")
    ok_hub = not hub["routes_compose"] and not hub["triangle"]
    if not (ok12 and ok_hub):
        failures.append("Theorems 1 and 2")

    # Theorem 2: chains
    chain_laws = {"parity": (2, P3), "Z3": (3, M3), "Z3 3-net": (3, net(3)), "L-{}": (4, laws["L-{}"][1][0]),
                  "L-{222} (K4)": (4, laws["L-{222}"][1][0]), "Z4 3-net": (4, net(4)),
                  "F5, c = 2a + m": (5, sorted((a, m, (2 * a + m) % 5) for a in range(5) for m in range(5))),
                  "K6 lift at 0": (7, laws["K6 lift at 0"][1][0])}
    chains = {}
    for name, (D, R) in chain_laws.items():
        rows = {}
        for k in range(1, (3 if D >= 5 else 4) + 1):
            cons, n = chain(R, k)
            _, cs = matroid(D, cons, n, list(range(n)))
            d = bond_distance(cs, n)
            rows[k] = {"circuits_are_runs": cs == chain_runs(k),
                       "end_to_end_distance": d[0][2 * k],
                       "distances_j_minus_i_plus_1": all(d[2 * i][2 * j] == j - i + 1
                                                         for i in range(k + 1) for j in range(i + 1, k + 1))}
        chains[name] = rows
    checks["theorem_2_chains"] = chains
    if not all(r["circuits_are_runs"] and r["distances_j_minus_i_plus_1"] for rows in chains.values() for r in rows.values()):
        failures.append("Theorem 2 chains")

    # Theorem 3: erasure is deletion, pinning is contraction, in affine laws; chains
    affine_laws = {"F2 (parity)": (2, [P3]), "F3 (3-net)": (3, [net(3)]), "F5 (x + y + z = 0)": (5, [zero_sum(5)])}
    delcon = {}
    for name, (D, rels) in affine_laws.items():
        st = {"systems": 0, "deletion_matches": 0, "contraction_checks": 0, "contraction_matches": 0}
        while st["systems"] < 50:
            n, cons = random_system(rng, rels, 6)
            if n < 3:
                continue
            vis = list(range(n))
            res = matroid(D, cons, n, vis)
            if res is None:
                continue
            st["systems"] += 1
            _, cs = res
            z = rng.randrange(n)
            rest = [v for v in vis if v != z]
            idx = {v: i for i, v in enumerate(rest)}
            _, cs_del = matroid(D, cons, n, rest)
            want_del = sorted((tuple(idx[v] for v in C) for C in cs if z not in C), key=lambda c: (len(c), c))
            st["deletion_matches"] += cs_del == want_del
            traces = {tuple(idx[v] for v in C if v != z) for C in cs}
            traces = {t for t in traces if t}
            # circuits of M/z of two or more elements: a loop of M/z is single-valued once z is pinned, hence free
            want_con = sorted((t for t in traces if len(t) > 1 and not any(set(u) < set(t) for u in traces)),
                              key=lambda c: (len(c), c))
            for a in range(D):
                res_a = matroid(D, cons + [([(a,)], (z,))], n, rest)
                if res_a is None:
                    continue
                st["contraction_checks"] += 1
                st["contraction_matches"] += res_a[1] == want_con
        delcon[name] = st
    sep = {}
    for name, (D, rels) in affine_laws.items():
        R = rels[0]
        cons, n = chain(R, 4)            # e0 l1 e1 l2 e2 l3 e3 l4 e4 = 0..8
        ends = (0, 8)
        out = {}
        keep = [0, 1, 3, 5, 7, 8]        # erase shared interior e1, e2, e3
        _, cs = matroid(D, cons, n, keep)
        out["erase_shared_interior_one_bond"] = cs == [tuple(range(6))]
        keep = [v for v in range(n) if v != 3]          # erase private l2
        _, cs = matroid(D, cons, n, keep)
        i0, i8 = keep.index(0), keep.index(8)
        out["erase_private_loop_separates"] = not any(i0 in C and i8 in C for C in cs)
        pin_shared, pin_private = [], []
        for a in range(D):
            keep = [v for v in range(n) if v != 4]      # pin shared e2
            res = matroid(D, cons + [([(a,)], (4,))], n, keep)
            if res is not None:
                cs = res[1]
                pos = {v: i for i, v in enumerate(keep)}
                ties = sorted(C for C in cs if len(C) == 2)
                pin_shared.append(not any(pos[0] in C and pos[8] in C for C in cs)
                                  and ties == sorted([(pos[2], pos[3]), (pos[5], pos[6])]))
            keep = [v for v in range(n) if v != 3]      # pin private l2
            res = matroid(D, cons + [([(a,)], (3,))], n, keep)
            if res is not None:
                cs = res[1]
                pos = {v: i for i, v in enumerate(keep)}
                d = bond_distance(cs, len(keep))
                ties = sorted(C for C in cs if len(C) == 2)
                pin_private.append(ties == [(pos[2], pos[4])] and d[pos[0]][pos[8]] == 4)
        out["pin_shared_separates_and_ties"] = bool(pin_shared) and all(pin_shared)
        out["pin_private_ties_and_shortens"] = bool(pin_private) and all(pin_private)
        sep[name] = out
    checks["theorem_3"] = {"deletion_and_contraction": delcon, "chain_of_four": sep}
    if not (all(s["deletion_matches"] == s["systems"] > 0 and s["contraction_matches"] == s["contraction_checks"] > 0
                for s in delcon.values()) and all(all(v.values()) for v in sep.values())):
        failures.append("Theorem 3")

    # Theorem 4: the triangle of three parity contacts
    _, tri = matroid(2, [(P3, (0, 1, 3)), (P3, (1, 2, 4)), (P3, (2, 0, 5))], 6, list(range(6)))
    tri_set = {frozenset(c) for c in tri}
    edges = list(combinations(range(4), 2))
    k4 = set()
    for r in (3, 4):
        for es in combinations(range(6), r):
            deg = {}
            for i in es:
                for v in edges[i]:
                    deg[v] = deg.get(v, 0) + 1
            if len(deg) == r and all(c == 2 for c in deg.values()):
                k4.add(frozenset(es))
    iso_k4 = any({frozenset(p[x] for x in c) for c in tri_set} == k4 for p in permutations(range(6)))
    auts = [p for p in permutations(range(6)) if {frozenset(p[x] for x in c) for c in tri_set} == tri_set]
    checks["theorem_4"] = {
        "circuits": [list(c) for c in tri], "isomorphic_to_M_K4": iso_k4, "automorphisms": len(auts),
        "transitive": {p[0] for p in auts} == set(range(6)),
        "drawn_contact_to_loop_knot": any({p[0], p[1], p[3]} == {3, 4, 5} for p in auts)}
    t4 = checks["theorem_4"]
    if not (iso_k4 and len(auts) == 24 and t4["transitive"] and t4["drawn_contact_to_loop_knot"]):
        failures.append("Theorem 4")

    # Theorem 5: substrates of the law that fix no graph
    cols = [v for v in product((0, 1), repeat=3) if any(v)]
    cons, n = [(P3, (10, 10, 10))], 11              # variable 10 is pinned to 0 by z + z + z = 0
    for i, v in enumerate(cols):
        xs = [k for k in range(3) if v[k]]
        x = 3 + i
        if len(xs) == 1:
            cons.append((P3, (x, xs[0], 10)))
        elif len(xs) == 2:
            cons.append((P3, (x, xs[0], xs[1])))
        else:
            cons += [(P3, (n, 0, 1)), (P3, (x, n, 2))]
            n += 1
    fr7, fano = matroid(2, cons, n, list(range(3, 10)))
    rank7 = max(len(Y) for Y in fr7 if fr7[Y])
    N3 = net(3)
    # visible u1 = 0, u2 = 1, x3 = u1 + u2 = 2, x4 = u1 + 2 u2 = 3 ; hidden t = u2 + u2 = 4
    fr4, u24 = matroid(3, [(N3, (0, 1, 2)), (N3, (1, 1, 4)), (N3, (0, 4, 3))], 5, [0, 1, 2, 3])
    checks["theorem_5"] = {
        "fano_circuits": len(fano), "fano_lines": sum(len(c) == 3 for c in fano), "fano_ties": sum(len(c) == 2 for c in fano),
        "fano_rank": rank7, "fano_not_graphic": rank7 == 3 and len(fano) == 14 and not any(len(c) == 2 for c in fano),
        "u24_circuits": [list(c) for c in u24],
        "u24_is_uniform": u24 == [c for c in combinations(range(4), 3)]}
    t5 = checks["theorem_5"]
    if not (t5["fano_not_graphic"] and t5["fano_lines"] == 7 and t5["u24_is_uniform"]):
        failures.append("Theorem 5")

    controls["routes_compose_in_every_substrate"] = {"rejected": not hub["routes_compose"]}
    controls["bond_size_minus_one_is_a_metric_in_every_substrate"] = {"rejected": not hub["triangle"]}
    controls["erasing_shared_distinctions_separates_chain_ends"] = {
        "rejected": all(v["erase_shared_interior_one_bond"] for v in sep.values())}
    controls["pinning_private_loop_separates_chain_ends"] = {
        "rejected": all(v["pin_private_ties_and_shortens"] for v in sep.values())}
    controls["allowed_states_tell_drawn_contacts_from_loop_knot"] = {"rejected": t4["drawn_contact_to_loop_knot"]}
    controls["parity_law_fixes_a_graph"] = {"rejected": t5["fano_not_graphic"]}
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
