#!/usr/bin/env python3
"""Checks for MATROID-CONVERSE-20261021-001B-P001. The statements are in proof.md.

A set of variables is free when its projection is the full product of their ranges (KNOT-CIRCUITS-20261020-001B-P001).

Checks:
- Proposition 1 (single relations).
  - Support relations of 200 random downsets on up to 6 elements (all singletons included) have exactly those free sets.
  - The Vamos matroid is the free-set family of its support relation and of the union of two explicit GF(7) codes
    (all 256 subsets).
  - For each, the projection onto a dependent pair of pairs is a knot with a direct case, and two copies fail.
- Theorem 2 (top lemma). For S3, D5, AGL(1,5), Z4 and Z9: random subdirect subgroups R of H1 x H2 x H3, with each Hi
  a subgroup of at least two elements, are the full product exactly when their image in the product of tops is full.
- Theorem 3 (group laws). Random systems over random laws of subgroups of G^3 for the same groups: the free sets
  are those of the direct sum, over top primes p, of the GF(p) codes read from the top image; no top is non-abelian.
- Corollary 4. The Vamos matroid is connected, not binary and not ternary.
- Proposition 6. In the lift K4, the shadow K6 and x+y+z=0 over Z9, all proper equivalence relations found among
  binary projections of systems of at most two copies have proper joins; over Z6 two of them join to the total relation.
- Census agreement with MATROID-CONVERSE-20261021-001A-E001.

Controls, each of which must be rejected:
- 'the top lemma holds without a unique maximal congruence' (Z6, which has two maximal subgroups);
- 'a single relation's law composes like cycles' (the Vamos support relation);
- 'the matroid of a group-law system is read in one characteristic' (an S3 system with circuits of both top primes);
- 'every law has a unique maximal pp-definable equivalence' (Z6, whose law does not compose like cycles).

    python3 -B check.py          verify result.json against a fresh run
    python3 -B check.py --write  write result.json
"""

from __future__ import annotations

import json
import random
import sys
from itertools import combinations, product
from math import prod
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CENSUS = ROOT / "artifacts" / "MATROID-CONVERSE-20261021-001A" / "MATROID-CONVERSE-20261021-001A-E001_matroid_census"
C1 = [(3, 2, 0, 1), (4, 2, 0, 1), (5, 2, 0, 0), (6, 2, 0, 0), (0, 6, 2, 5), (1, 6, 2, 5), (4, 2, 3, 3), (5, 2, 3, 3)]
C2 = [(1, 2, 3, 5), (1, 2, 3, 5), (1, 0, 1, 0), (1, 0, 2, 0), (1, 1, 0, 0), (1, 2, 0, 0), (0, 0, 1, 1), (0, 0, 1, 2)]
SPECIAL = {(0, 1, 2, 3), (0, 1, 4, 5), (0, 1, 6, 7), (2, 3, 4, 5), (2, 3, 6, 7)}
GROUPS = {"S3": ([(1, 0, 2), (1, 2, 0)], 3), "D5": ([(1, 2, 3, 4, 0), (0, 4, 3, 2, 1)], 5),
          "AGL(1,5)": ([(1, 2, 3, 4, 0), (0, 2, 4, 1, 3)], 5), "Z4": ([(1, 2, 3, 0)], 4),
          "Z9": ([tuple((i + 1) % 9 for i in range(9))], 9)}


# ------------------------------------------------------------------ relations

def proj(S, Y):
    return {tuple(t[i] for i in Y) for t in S}


def subsets(n):
    return [Y for k in range(1, n + 1) for Y in combinations(range(n), k)]


def free_fn(S, n):
    rg = [len({t[i] for t in S}) for i in range(n)]
    memo = {}

    def f(Y):
        Y = tuple(sorted(Y))
        if Y not in memo:
            memo[Y] = len(proj(S, Y)) == prod(rg[i] for i in Y)
        return memo[Y]

    return f


def circuits(free, n):
    return [Y for Y in subsets(n) if not free(Y) and all(free(tuple(x for x in Y if x != w)) for w in Y)]


def has_failure(free, n):
    cs = circuits(free, n)
    return any(free(tuple(sorted((set(a) | set(b)) - {e}))) for a, b in combinations(cs, 2) for e in set(a) & set(b))


def solve(rels, doms, cons):
    n = len(doms)
    order = []
    for _, c in cons:
        for v in c:
            if v not in order:
                order.append(v)
    order += [v for v in range(n) if v not in order]
    pos = {v: i for i, v in enumerate(order)}
    at = {}
    for k, c in cons:
        at.setdefault(max(pos[v] for v in c), []).append((rels[k] if isinstance(rels, dict) else rels, c))
    out, a = [], [None] * n

    def go(i):
        if i == n:
            out.append(tuple(a))
            return
        v = order[i]
        for x in doms[v]:
            a[v] = x
            if all(tuple(a[w] for w in c) in R for R, c in at.get(i, ())):
                go(i + 1)
        a[v] = None

    go(0)
    return out


def fibres(K, e):
    g = {}
    for t in K:
        g.setdefault(t[:e] + t[e + 1:], set()).add(t[e])
    return g


def direct_case(K, k):
    for e in range(k):
        g = fibres(K, e)
        others = [i for i in range(k) if i != e]
        for size in range(k - 1):
            for T in combinations(range(k - 1), size):
                groups = {}
                for rest, fb in g.items():
                    groups.setdefault(tuple(rest[p] for p in T), []).append(fb)
                if all(all(a & b for a in grp for b in grp) for grp in groups.values()):
                    return e, [others[p] for p in T]
    return None


def two_copies_fail(K, k, shared, e):
    rg = [sorted({t[i] for t in K}) for i in range(k)]
    second, nxt = [], k
    for p in range(k):
        if p in shared:
            second.append(p)
        else:
            second.append(nxt)
            nxt += 1
    doms = rg + [rg[p] for p in range(k) if p not in shared]
    S = solve(K, doms, [(None, tuple(range(k))), (None, tuple(second))])
    f = free_fn(S, len(doms))
    cs = set(circuits(f, len(doms)))
    return tuple(range(k)) in cs and tuple(sorted(second)) in cs and f(tuple(sorted((set(range(k)) | set(second)) - {e})))


# ------------------------------------------------------------------ groups

def perm_group(gens, n):
    G = {tuple(range(n))}
    frontier = list(G)
    while frontier:
        x = frontier.pop()
        for s in gens:
            y = tuple(s[x[i]] for i in range(n))
            if y not in G:
                G.add(y)
                frontier.append(y)
    G = sorted(G)
    idx = {g: i for i, g in enumerate(G)}
    return G, [[idx[tuple(a[b[i]] for i in range(n))] for b in G] for a in G]


def generated(elems, mul, k):
    H = {tuple([0] * k)} | set(elems)
    frontier = list(H)
    while frontier:
        x = frontier.pop()
        for y in list(H):
            for z in (tuple(mul[a][b] for a, b in zip(x, y)), tuple(mul[a][b] for a, b in zip(y, x))):
                if z not in H:
                    H.add(z)
                    frontier.append(z)
    return frozenset(H)


def subgroup_tops(mul, order):
    subs = {frozenset(t[0] for t in generated([(a,), (b,)], mul, 1)) for a in range(order) for b in range(order)}
    inv = [next(j for j in range(order) if mul[i][j] == 0) for i in range(order)]
    top = {}
    for H in subs:
        normals = [N for N in subs if N < H and all(mul[mul[h][m]][inv[h]] in N for h in H for m in N)]
        top[H] = [N for N in normals if not any(N < N2 for N2 in normals)]
    return subs, top


def coset_map(H, mu, mul):
    return {h: frozenset(mul[h][m] for m in mu) for h in H}


def gf_rank(vectors, p):
    rows, r = [list(v) for v in vectors], 0
    width = len(rows[0]) if rows else 0
    for c in range(width):
        piv = next((i for i in range(r, len(rows)) if rows[i][c] % p), None)
        if piv is None:
            continue
        rows[r], rows[piv] = rows[piv], rows[r]
        inv = pow(rows[r][c], p - 2, p)
        rows[r] = [x * inv % p for x in rows[r]]
        for i in range(len(rows)):
            if i != r and rows[i][c] % p:
                fct = rows[i][c]
                rows[i] = [(x - fct * y) % p for x, y in zip(rows[i], rows[r])]
        r += 1
    return r


def derived_equivalences(K, q):
    """Equivalence relations with full ranges among the binary projections of systems of at most two copies of K
    on four variables (two of them hidden)."""
    out = set()
    triples = list(product(range(4), repeat=3))
    for c1 in triples:
        for c2 in [None] + triples:
            cons = [(None, c1)] + ([(None, c2)] if c2 else [])
            S = solve(K, [list(range(q))] * 4, cons)
            R = frozenset(proj(S, (0, 1)))
            if {a for a, _ in R} != set(range(q)) or {b for _, b in R} != set(range(q)):
                continue
            if all((a, a) in R for a in range(q)) and all((b, a) in R for a, b in R) and \
                    all((a, d) in R for a, b in R for c, d in R if b == c):
                out.add(R)
    return out


def join(R1, R2, q):
    J = set(R1) | set(R2)
    changed = True
    while changed:
        changed = False
        for a, b in list(J):
            for c, d in list(J):
                if b == c and (a, d) not in J:
                    J.add((a, d))
                    changed = True
    return frozenset(J)


# ------------------------------------------------------------------ the checks

def vamos_indep(Y):
    return len(Y) <= 3 or (len(Y) == 4 and tuple(sorted(Y)) not in SPECIAL)


def run():
    checks, controls, failures = {}, {}, []
    rng = random.Random(20261022)

    # Proposition 1
    downsets = {"downsets": 0, "exact": 0}
    for _ in range(200):
        m = rng.randint(2, 6)
        gens = [frozenset(Y) for Y in subsets(m) if rng.random() < 0.25] + [frozenset({i}) for i in range(m)]
        I = {frozenset(Y) for Y in subsets(m) if any(frozenset(Y) <= g for g in gens)}
        S = [x for x in product((0, 1), repeat=m) if frozenset(i for i in range(m) if x[i]) in I or not any(x)]
        f = free_fn(S, m)
        downsets["downsets"] += 1
        downsets["exact"] += all(f(Y) == (frozenset(Y) in I) for Y in subsets(m))
    code = lambda cols: {tuple(sum(w[i] * c[i] for i in range(4)) % 7 for c in cols) for w in product(range(7), repeat=4)}
    vrel = {"support relation": [x for x in product((0, 1), repeat=8) if vamos_indep(tuple(i for i in range(8) if x[i]))],
            "union of two GF(7) codes": sorted(code(C1) | code(C2))}
    vam = {}
    for name, S in vrel.items():
        f = free_fn(S, 8)
        row = {"tuples": len(S), "free_sets_are_vamos": all(f(Y) == vamos_indep(Y) for Y in subsets(8))}
        for C in sorted(SPECIAL):
            K = proj(S, C)
            dc = direct_case(K, 4)
            if dc:
                row["circuit"], row["direct_case"] = list(C), {"e": dc[0], "T": dc[1]}
                row["two_copies_fail"] = two_copies_fail(K, 4, set(dc[1]) | {dc[0]}, dc[0])
                break
        vam[name] = row
    checks["proposition_1_single_relations"] = {"random_downsets": downsets, "vamos": vam}
    if downsets["exact"] != downsets["downsets"] or not all(r["free_sets_are_vamos"] and r.get("two_copies_fail") for r in vam.values()):
        failures.append("Proposition 1")

    # Theorem 2: the top lemma on random subdirect subgroups
    thm2 = {}
    group_data = {}
    for name, (gens, npts) in GROUPS.items():
        G, mul = perm_group(gens, npts)
        subs, top = subgroup_tops(mul, len(G))
        group_data[name] = (G, mul, subs, top)
        unique = all(len(top[H]) == 1 for H in subs if len(H) > 1)
        nontrivial = [H for H in subs if len(H) > 1]
        row = {"order": len(G), "subgroups": len(subs), "unique_maximal_normal": unique, "subdirect_products": 0,
               "full": 0, "agree": 0}
        tries = 0
        while row["subdirect_products"] < 60 and tries < 5000:
            tries += 1
            Hs = [rng.choice(nontrivial) for _ in range(3)]
            elems = [tuple(rng.choice(sorted(H)) for H in Hs) for _ in range(rng.randint(1, 3))]
            R = generated(elems, mul, 3)
            if any(frozenset(t[i] for t in R) != Hs[i] for i in range(3)):
                continue
            mus = [top[H][0] for H in Hs]
            cm = [coset_map(Hs[i], mus[i], mul) for i in range(3)]
            image = {tuple(cm[i][t[i]] for i in range(3)) for t in R}
            full = len(R) == prod(len(H) for H in Hs)
            top_full = len(image) == prod(len(Hs[i]) // len(mus[i]) for i in range(3))
            row["subdirect_products"] += 1
            row["full"] += full
            row["agree"] += full == top_full
        thm2[name] = row
    R6 = {(x, y) for x in range(6) for y in range(6) if x % 2 == y % 2}
    image_mod3 = {(x % 3, y % 3) for x, y in R6}
    thm2["Z6 control"] = {"R_full": len(R6) == 36, "image_in_Z3_x_Z3_full": len(image_mod3) == 9}
    checks["theorem_2_top_lemma"] = thm2
    if any(r.get("agree") != r.get("subdirect_products") or not r.get("unique_maximal_normal")
           for k, r in thm2.items() if k != "Z6 control"):
        failures.append("Theorem 2")

    # Theorem 3: group-law systems read as direct sums of GF(p) codes
    thm3 = {}
    both_prime_circuits = False
    for name, (G, mul, subs, top) in group_data.items():
        order = len(G)
        nmax = {"S3": 6, "D5": 5, "AGL(1,5)": 4, "Z4": 6, "Z9": 5}[name]
        row = {"systems": 0, "matroids": 0, "equal_to_prime_codes": 0, "non_abelian_tops": 0, "systems_with_two_primes": 0}
        while row["systems"] < 60:
            law = {}
            for j in range(rng.randint(1, 3)):
                H = generated([tuple(rng.randrange(order) for _ in range(3)) for _ in range(rng.randint(1, 2))], mul, 3)
                if len(H) < order ** 3:
                    law[j] = H
            if not law:
                continue
            n = rng.randint(3, nmax)
            cons = [(rng.choice(list(law)), tuple(rng.randrange(n) for _ in range(3))) for _ in range(rng.randint(1, 4))]
            if len({v for _, c in cons for v in c}) < n:
                continue
            S = solve(law, [list(range(order))] * n, cons)
            ranges = [frozenset(t[i] for t in S) for i in range(n)]
            mus = [top[H][0] if len(H) > 1 else None for H in ranges]
            primes = [len(H) // len(mus[i]) if mus[i] is not None else 1 for i, H in enumerate(ranges)]
            row["non_abelian_tops"] += sum(1 for p in primes if p > 1 and any(p % d == 0 for d in range(2, p)))
            cm = [coset_map(ranges[i], mus[i], mul) if mus[i] is not None else None for i in range(n)]
            topvals = [sorted(set(cm[i].values())) if cm[i] else [] for i in range(n)]
            # identify each top (cyclic of prime order) with Z_p by choosing a generator coset and its powers
            label = []
            for i in range(n):
                if not cm[i]:
                    label.append(None)
                    continue
                p = primes[i]
                gen_coset = next(c for c in topvals[i] if mus[i] not in (c,))
                rep = min(gen_coset)
                lab, cur = {}, mus[i]
                for k2 in range(p):
                    lab[cur] = k2
                    cur = frozenset(mul[x][rep] for x in cur)
                label.append(lab)
            fS = free_fn(S, n)
            free_codes = {}
            for p in sorted({q for q in primes if q > 1}):
                Vp = [i for i in range(n) if primes[i] == p]
                code_p = {tuple(label[i][cm[i][t[i]]] for i in Vp) for t in S}
                free_codes[p] = (Vp, code_p)
            def free_sum(Y):
                for p, (Vp, code_p) in free_codes.items():
                    part = [Vp.index(i) for i in Y if i in Vp]
                    if part and len({tuple(c[j] for j in part) for c in code_p}) != p ** len(part):
                        return False
                return True
            row["systems"] += 1
            row["matroids"] += not has_failure(fS, n)
            row["equal_to_prime_codes"] += all(fS(Y) == free_sum(Y) for Y in subsets(n))
            if len(free_codes) > 1:
                row["systems_with_two_primes"] += 1
                cs = circuits(fS, n)
                if {primes[C[0]] for C in cs if len({primes[i] for i in C}) == 1 and primes[C[0]] > 1} >= {2, 3}:
                    both_prime_circuits = True
        thm3[name] = row
    checks["theorem_3_group_laws"] = thm3
    if any(r["matroids"] != r["systems"] or r["equal_to_prime_codes"] != r["systems"] or r["non_abelian_tops"]
           for r in thm3.values()):
        failures.append("Theorem 3")

    # Corollary 4: the Vamos matroid is connected, not binary, not ternary
    indep = {Y: vamos_indep(Y) for Y in subsets(8)}
    circ = [Y for Y in subsets(8) if not indep[Y] and all(indep.get(tuple(x for x in Y if x != w), True) for w in Y)]
    parent = list(range(8))

    def find(x):
        while parent[x] != x:
            x = parent[x]
        return x

    for C in circ:
        for x in C[1:]:
            parent[find(x)] = find(C[0])
    connected = len({find(x) for x in range(8)}) == 1
    basis = (0, 1, 2, 4)
    assert indep[basis]

    def representable(p):
        nonbasis = [e for e in range(8) if e not in basis]
        fund = {}
        for e in nonbasis:
            C = next(C for C in circ if e in C and set(C) - {e} <= set(basis))
            fund[e] = [b for b in basis if b in C]
        entries = [(e, b) for e in nonbasis for b in fund[e][1:]]  # column scaling fixes each first entry to 1
        for values in product(range(1, p), repeat=len(entries)):
            val = dict(zip(entries, values))
            val.update({(e, fund[e][0]): 1 for e in nonbasis})
            cols = {b: tuple(int(b == bb) for bb in basis) for b in basis}
            for e in nonbasis:
                cols[e] = tuple(val.get((e, bb), 0) for bb in basis)
            if all((gf_rank([cols[i] for i in Y], p) == len(Y)) == indep[Y] for Y in subsets(8)):
                return True
        return False

    cor4 = {"connected": connected, "binary": representable(2), "ternary": representable(3)}
    checks["corollary_4_vamos"] = cor4
    if not connected or cor4["binary"] or cor4["ternary"]:
        failures.append("Corollary 4")

    # Proposition 6: in laws composing like cycles, proper pp-definable equivalences have proper joins
    M3 = {t for t in product(range(3), repeat=3) if sum(t) % 3 == 0}
    lift = {t for t in product(range(4), repeat=3) if tuple((0, 1, 2, 2)[x] for x in t) in M3} - {(2, 2, 2)}
    not_two = {t for t in product(range(2), repeat=3) if sum(t) != 2}
    shadow = {tuple(2 * a + b for a, b in zip(u, w)) for u in M3 for w in not_two}
    z9 = {t for t in product(range(9), repeat=3) if sum(t) % 9 == 0}
    z6 = {t for t in product(range(6), repeat=3) if sum(t) % 6 == 0}
    prop6 = {}
    for name, K, q in (("K4 (lift)", lift, 4), ("K6 (shadow)", shadow, 6), ("x+y+z=0 over Z9", z9, 9), ("x+y+z=0 over Z6", z6, 6)):
        eqs = derived_equivalences(K, q)
        proper = [E for E in eqs if len(E) < q * q]
        joins_proper = all(len(join(a, b, q)) < q * q for a in proper for b in proper)
        biggest = max(proper, key=len) if proper else None
        prop6[name] = {"proper_equivalences_found": len(proper), "all_joins_proper": joins_proper,
                       "classes_of_largest": q - sum(1 for a in range(q) if any((b, a) in biggest for b in range(a))) if biggest else None}
    checks["proposition_6_unique_maximal_equivalence"] = prop6
    if not all(prop6[k]["all_joins_proper"] for k in ("K4 (lift)", "K6 (shadow)", "x+y+z=0 over Z9")):
        failures.append("Proposition 6")

    census = {}
    if (CENSUS / "result.json").exists():
        a = json.loads((CENSUS / "result.json").read_text())
        census = {"predictions": a["predictions"], "signal": a["signal"]}
        if not (a["predictions"]["Q1"] and a["predictions"]["Q2"] and a["predictions"]["Q3"]):
            failures.append("census agreement")
    checks["census_agreement"] = census

    controls["top_lemma_without_unique_maximal_congruence"] = {
        **thm2["Z6 control"], "rejected": not thm2["Z6 control"]["R_full"] and thm2["Z6 control"]["image_in_Z3_x_Z3_full"]}
    controls["single_relation_law_composes_like_cycles"] = {"rejected": vam["support relation"].get("two_copies_fail", False)}
    G, mul, subs, top = group_data["S3"]
    sign = {i: (sum(1 for a in range(3) for b in range(a) if G[i][b] > G[i][a]) % 2) for i in range(len(G))}
    alt = [i for i in range(len(G)) if sign[i] == 0]
    r_sign = {t for t in product(range(len(G)), repeat=3) if sum(sign[x] for x in t) % 2 == 0}
    r_alt = {t for t in product(alt, repeat=3) if mul[mul[t[0]][t[1]]][t[2]] == 0}
    S = solve({0: r_sign, 1: r_alt}, [list(range(len(G)))] * 6, [(0, (0, 1, 2)), (1, (3, 4, 5))])
    cs = circuits(free_fn(S, 6), 6)
    designed = (0, 1, 2) in cs and (3, 4, 5) in cs
    controls["group_law_matroids_in_one_characteristic"] = {"random_systems_with_both": both_prime_circuits,
                                                           "designed_S3_system": designed, "rejected": designed}
    controls["unique_maximal_equivalence_without_cycle_composition"] = {
        "Z6_joins_proper": prop6["x+y+z=0 over Z6"]["all_joins_proper"], "rejected": not prop6["x+y+z=0 over Z6"]["all_joins_proper"]}
    for name, c in controls.items():
        if not c["rejected"]:
            failures.append(f"control not rejected: {name}")
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
