#!/usr/bin/env python3
"""Checks for CYCLE-TRACTABILITY-20261021-001A-P001. The statements are in proof.md.

Checks:
- Theorem 1. For H in {3-colouring (K3), not-all-equal, one-in-three, three random structures on three values} and
  q in {2, 3}, on random systems of the equal-top lift (with hidden variables): every system's free sets are exactly
  the sets with at most one visible variable in each component of the system's constraint hypergraph.
- The projection (a, s) -> s and the embedding s -> (0, s) are homomorphisms between each lift and H.
- Corollary 2. The endomorphism cores of the K3 and not-all-equal lifts (q = 2) have 3 and 2 elements and are K3 and
  not-all-equal; neither K3 nor not-all-equal has a Siggers polymorphism (exhaustive search, which finds one for the
  Z3 law and for parity), so neither is Taylor;
  K3 and not-all-equal themselves violate elimination; a lifted 3-colouring instance is satisfiable exactly when the
  graph is 3-colourable, on random graphs.
- With a constant the K3 lift violates elimination (an explicit system), and without the constant it does not.
- Theorem 3. For H in {K3, not-all-equal, one-in-three} and q in {2, 3}, the shifted lift (the equal-top lift plus the
  relation 'first coordinate goes up by one') has exactly q * |Aut H|^q endomorphisms, all bijective, so it is a core;
  on random systems its free sets are exactly the sets with at most one visible variable in each component of all
  atoms; a shifted 3-colouring instance is satisfiable exactly when the graph is 3-colourable and the first-coordinate
  offsets are consistent.
- Proposition 4. x + y + z = 0 over Z3 with the constants 0 and 1 is a core with no nontrivial endomorphism and keeps
  x - y + z (illustration); one-in-three is a core with no nontrivial endomorphism (so its equal-top lift composes
  like cycles with a rigid core), and its shifted lift is a core whose only automorphisms are the q translations
  (sharpness).

Controls, each of which must be rejected:
- 'every law composing like cycles has a polynomial-time constraint problem' (the K3 lift is homomorphically equivalent
  to K3);
- 'the core of a law composing like cycles composes like cycles' (K3 violates elimination);
- 'the lift still composes like cycles with constants added' (the explicit system);
- 'every core composing like cycles has a polynomial-time constraint problem' (the shifted K3 lift is such a core).

    python3 -B check.py          verify result.json against a fresh run
    python3 -B check.py --write  write result.json
"""

from __future__ import annotations

import json
import random
import sys
from itertools import combinations, product
from pathlib import Path

HERE = Path(__file__).resolve().parent

K3 = {(x, y) for x in range(3) for y in range(3) if x != y}
NAE = {t for t in product((0, 1), repeat=3) if len(set(t)) > 1}
ONE3 = {(1, 0, 0), (0, 1, 0), (0, 0, 1)}


# ------------------------------------------------------------------ helpers

def lift(H, colours, q):
    enc = lambda a, s: a * colours + s
    return [{tuple(enc(a, s) for s in t) for a in range(q) for t in R} for R in H], q * colours


def shifted(H, colours, q):
    rels, D = lift(H, colours, q)
    up = {(a * colours + s, (a + 1) % q * colours + t) for a in range(q) for s in range(colours) for t in range(colours)}
    return rels + [up], D


def offsets_consistent(n, equal, up, q):
    adj = {v: [] for v in range(n)}
    for u, v in equal:
        adj[u].append((v, 0))
        adj[v].append((u, 0))
    for u, v in up:
        adj[u].append((v, 1))
        adj[v].append((u, -1))
    pot = {}
    for s in range(n):
        if s in pot:
            continue
        pot[s], stack = 0, [s]
        while stack:
            u = stack.pop()
            for v, d in adj[u]:
                want = (pot[u] + d) % q
                if v not in pot:
                    pot[v] = want
                    stack.append(v)
                elif pot[v] != want:
                    return False
    return True


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
            need = 1
            for v in Y:
                need *= rg[v]
            fr[Y] = len({tuple(s[v] for v in Y) for s in S}) == need
    return fr


def elimination_failures(fr):
    cs = [Y for Y in fr if len(Y) > 1 and not fr[Y] and all(fr[tuple(u for u in Y if u != w)] for w in Y)]
    out = []
    for C1, C2 in combinations(cs, 2):
        for y in sorted(set(C1) & set(C2)):
            if fr[tuple(sorted((set(C1) | set(C2)) - {y}))]:
                out.append((C1, C2, y))
    return cs, out


def components(n, cons):
    parent = list(range(n))

    def f(x):
        while parent[x] != x:
            x = parent[x]
        return x
    for _, vs in cons:
        for v in vs[1:]:
            parent[f(v)] = f(vs[0])
    return [f(v) for v in range(n)]


def endomorphisms(rels, D):
    out, g = [], [None] * D

    def ok():
        return all(tuple(g[v] for v in t) in R for R in rels for t in R if all(g[v] is not None for v in t))

    def go(i):
        if i == D:
            out.append(tuple(g))
            return
        for v in range(D):
            g[i] = v
            if ok():
                go(i + 1)
        g[i] = None
    go(0)
    return out


def siggers_exists(rels, D):
    """Is there a 4-ary polymorphism s with s(a,r,e,a) = s(r,a,r,e) for all a, r, e? Exhaustive search."""
    args = list(product(range(D), repeat=4))
    parent = {x: x for x in args}

    def f(x):
        while parent[x] != x:
            x = parent[x]
        return x
    for a, r, e in product(range(D), repeat=3):
        parent[f((a, r, e, a))] = f((r, a, r, e))
    var = {x: f(x) for x in args}
    names = sorted(set(var.values()))
    idx = {v: i for i, v in enumerate(names)}
    cons = []
    for R in rels:
        k = len(next(iter(R)))
        for ts in product(sorted(R), repeat=4):
            cons.append((R, tuple(idx[var[tuple(t[i] for t in ts)]] for i in range(k))))
    return bool(solve_first(D, len(names), cons))


def solve_first(D, n, cons):
    by_var = {}
    for ci, (R, vs) in enumerate(cons):
        for v in set(vs):
            by_var.setdefault(v, []).append(ci)
    a = [None] * n
    order = sorted(range(n), key=lambda v: -len(by_var.get(v, ())))

    def consistent(v):
        for ci in by_var.get(v, ()):
            R, vs = cons[ci]
            if all(a[u] is not None for u in vs) and tuple(a[u] for u in vs) not in R:
                return False
        return True

    def go(i):
        if i == n:
            return True
        v = order[i]
        for x in range(D):
            a[v] = x
            if consistent(v) and go(i + 1):
                return True
        a[v] = None
        return False
    return go(0)


def random_system(rng, rels, nmax):
    n, cons = 0, []
    for _ in range(rng.randint(1, 5)):
        R = rng.choice(rels)
        vs = []
        for _ in range(len(next(iter(R)))):
            if n == 0 or (n < nmax and rng.random() < 0.5):
                vs.append(n)
                n += 1
            else:
                vs.append(rng.randrange(n))
        cons.append((R, tuple(vs)))
    return n, cons


# ------------------------------------------------------------------ run

def run():
    checks, controls, failures = {}, {}, []
    rng = random.Random("cycle-tractability")

    # Theorem 1: free sets of lifted systems are partial transversals of the components
    structures = {"K3": ([K3], 3), "not-all-equal": ([NAE], 2), "one-in-three": ([ONE3], 2)}
    for i in range(3):
        k = rng.choice((2, 3))
        full = list(product(range(3), repeat=k))
        structures[f"random structure {i}"] = ([set(rng.sample(full, rng.randint(2, len(full) - 1)))], 3)
    thm1 = {}
    for name, (H, c) in structures.items():
        for q in (2, 3):
            rels, D = lift(H, c, q)
            homs = all(tuple(x % c for x in t) in R0 for R, R0 in zip(rels, H) for t in R) and \
                all(tuple(s for s in t) in R for R, R0 in zip(rels, H) for t in R0)
            st = {"systems": 0, "nonempty": 0, "partition_matroid": 0, "elimination_failures": 0, "homomorphisms": homs}
            while st["systems"] < 120:
                n, cons = random_system(rng, rels, 6)
                S = solve(D, n, cons)
                st["systems"] += 1
                if not S:
                    continue
                keep = [v for v in range(n) if rng.random() < 0.7] or [0]
                comp = components(n, cons)
                P = {tuple(s[v] for v in keep) for s in S}
                fr = free_map(P, len(keep))
                predicted = {Y: len({comp[keep[v]] for v in Y}) == len(Y) for Y in fr}
                st["nonempty"] += 1
                st["partition_matroid"] += fr == predicted
                st["elimination_failures"] += bool(elimination_failures(fr)[1])
            thm1[f"{name}, q={q}"] = st
    checks["theorem_1"] = thm1
    if not all(s["partition_matroid"] == s["nonempty"] > 0 and s["elimination_failures"] == 0 and s["homomorphisms"]
               for s in thm1.values()):
        failures.append("Theorem 1")

    # Corollary 2: cores, non-Taylor, failures of the cores, CSP equivalence
    cor = {}
    for name, (H, c) in (("K3", ([K3], 3)), ("not-all-equal", ([NAE], 2))):
        rels, D = lift(H, c, 2)
        ends = endomorphisms(rels, D)
        m = min(len(set(g)) for g in ends)
        e = next(g for g in ends if len(set(g)) == m)
        image = sorted(set(e))
        colours_onto = sorted(x % c for x in image) == list(range(c))
        induced = {tuple(x % c for x in t) for t in rels[0] if all(x in image for x in t)}
        cor[name] = {"core_size": m, "core_is_H": colours_onto and induced == H[0],
                     "H_has_siggers": siggers_exists(H, c)}
    S3 = solve(3, 3, [(K3, (0, 1)), (K3, (1, 2))])
    cs3, fl3 = elimination_failures(free_map(S3, 3))
    Snae = solve(2, 4, [(NAE, (0, 2, 3)), (NAE, (1, 2, 3))])
    csn, fln = elimination_failures(free_map(Snae, 4))
    graphs, agree = 0, 0
    liftK3, DK = lift([K3], 3, 2)
    for _ in range(40):
        nv = rng.randint(3, 6)
        edges = [(u, v) for u, v in combinations(range(nv), 2) if rng.random() < 0.55]
        if not edges:
            continue
        col = bool(solve(3, nv, [(K3, e) for e in edges]))
        lifted = bool(solve(DK, nv, [(liftK3[0], e) for e in edges]))
        graphs += 1
        agree += col == lifted
    M3 = {t for t in product(range(3), repeat=3) if sum(t) % 3 == 0}
    cor["siggers_search_finds_one_for_Z3"] = siggers_exists([M3], 3)
    cor["siggers_search_finds_one_for_parity"] = siggers_exists([{t for t in product((0, 1), repeat=3) if sum(t) % 2 == 0}], 2)
    cor["K3_fails_elimination"] = bool(fl3)
    cor["not_all_equal_fails_elimination"] = bool(fln)
    cor["random_graphs"] = graphs
    cor["lifted_instance_satisfiable_iff_3_colourable"] = agree
    checks["corollary_2"] = cor
    if not (cor["K3"]["core_size"] == 3 and cor["K3"]["core_is_H"] and not cor["K3"]["H_has_siggers"]
            and cor["not-all-equal"]["core_size"] == 2 and cor["not-all-equal"]["core_is_H"]
            and not cor["not-all-equal"]["H_has_siggers"] and fl3 and fln and agree == graphs > 0
            and cor["siggers_search_finds_one_for_Z3"] and cor["siggers_search_finds_one_for_parity"]):
        failures.append("Corollary 2")

    # constants: the K3 lift with one constant
    E = liftK3[0]
    pin = {(0,)}   # the element (0, 0)
    base = [(E, (0, 3)), (E, (3, 6)), (E, (1, 4)), (E, (4, 6)), (E, (2, 5)), (E, (5, 6)), (E, (0, 1)), (E, (1, 2))]
    with_pin = solve(DK, 7, base + [(pin, (6,))])
    without_pin = solve(DK, 7, base)
    fw = elimination_failures(free_map({s[:3] for s in with_pin}, 3))
    fo = elimination_failures(free_map({s[:3] for s in without_pin}, 3))
    checks["constants"] = {"with_constant_circuits": [list(C) for C in fw[0]], "with_constant_failures": len(fw[1]),
                           "without_constant_circuits": [list(C) for C in fo[0]], "without_constant_failures": len(fo[1])}
    if not (fw[1] and not fo[1]):
        failures.append("constants")

    # Theorem 3: shifted lifts are cores composing like cycles, with the constraint problem of H
    thm3 = {}
    for name, (H, c) in (("K3", ([K3], 3)), ("not-all-equal", ([NAE], 2)), ("one-in-three", ([ONE3], 2))):
        auts = len(endomorphisms(H, c))   # each H here is a core, so its endomorphisms are automorphisms
        for q in (2, 3):
            rels, D = shifted(H, c, q)
            ends = endomorphisms(rels, D)
            st = {"endomorphisms": len(ends), "expected": q * auts ** q,
                  "all_bijective": all(len(set(g)) == D for g in ends),
                  "systems": 0, "nonempty": 0, "partition_matroid": 0, "elimination_failures": 0}
            while st["systems"] < 120:
                n, cons = random_system(rng, rels, 6)
                S = solve(D, n, cons)
                st["systems"] += 1
                if not S:
                    continue
                keep = [v for v in range(n) if rng.random() < 0.7] or [0]
                comp = components(n, cons)
                P = {tuple(s[v] for v in keep) for s in S}
                fr = free_map(P, len(keep))
                predicted = {Y: len({comp[keep[v]] for v in Y}) == len(Y) for Y in fr}
                st["nonempty"] += 1
                st["partition_matroid"] += fr == predicted
                st["elimination_failures"] += bool(elimination_failures(fr)[1])
            thm3[f"{name}, q={q}"] = st
    split = {"instances": 0, "agree": 0, "colourable_and_consistent": 0, "colourable_but_inconsistent": 0,
             "not_colourable": 0}
    for q in (2, 3):
        (E3, up), D = shifted([K3], 3, q)
        for _ in range(30):
            nv = rng.randint(3, 6)
            equal = [(u, v) for u, v in combinations(range(nv), 2) if rng.random() < 0.7]
            ups = [(u, v) for u in range(nv) for v in range(nv) if u != v and rng.random() < 0.06]
            if not equal:
                continue
            sat = solve_first(D, nv, [(E3, e) for e in equal] + [(up, e) for e in ups])
            col = solve_first(3, nv, [(K3, e) for e in equal])
            off = offsets_consistent(nv, equal, ups, q)
            split["instances"] += 1
            split["agree"] += sat == (col and off)
            split["not_colourable" if not col else "colourable_and_consistent" if off else "colourable_but_inconsistent"] += 1
    thm3["shifted_K3_instances"] = split
    checks["theorem_3"] = thm3
    if not (all(s["all_bijective"] and s["endomorphisms"] == s["expected"] and s["partition_matroid"] == s["nonempty"] > 0
                and s["elimination_failures"] == 0 for k, s in thm3.items() if k != "shifted_K3_instances")
            and split["agree"] == split["instances"] > 0
            and min(split["colourable_and_consistent"], split["colourable_but_inconsistent"], split["not_colourable"]) > 0):
        failures.append("Theorem 3")

    # Proposition 4: a rigid core composing like cycles keeps a Mal'tsev operation (illustration), and sharpness
    M3 = {t for t in product(range(3), repeat=3) if sum(t) % 3 == 0}
    rigid = [M3, {(0,)}, {(1,)}]
    ends = endomorphisms(rigid, 3)
    maltsev = all(tuple((x - y + z) % 3 for x, y, z in zip(a, b, c)) in R for R in rigid for a in R for b in R for c in R)
    one3 = endomorphisms([ONE3], 2)
    checks["proposition_4"] = {
        "illustration_endomorphisms": [list(g) for g in ends], "illustration_x_minus_y_plus_z": maltsev,
        "one_in_three_endomorphisms": [list(g) for g in one3],
        "shifted_one_in_three_automorphisms": {q: thm3[f"one-in-three, q={q}"]["endomorphisms"] for q in (2, 3)}}
    if not (ends == [(0, 1, 2)] and maltsev and one3 == [(0, 1)]
            and all(thm3[f"one-in-three, q={q}"]["endomorphisms"] == q for q in (2, 3))):
        failures.append("Proposition 4")

    # controls
    controls["composing_like_cycles_implies_tractability"] = {
        "rejected": cor["K3"]["core_size"] == 3 and not cor["K3"]["H_has_siggers"]}
    controls["core_of_cycle_composing_law_composes_like_cycles"] = {"rejected": bool(fl3)}
    controls["lift_with_constants_composes_like_cycles"] = {"rejected": bool(fw[1])}
    controls["every_core_composing_like_cycles_is_tractable"] = {
        "rejected": thm3["K3, q=2"]["all_bijective"] and thm3["K3, q=2"]["partition_matroid"] == thm3["K3, q=2"]["nonempty"]
        and not cor["K3"]["H_has_siggers"]}
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
