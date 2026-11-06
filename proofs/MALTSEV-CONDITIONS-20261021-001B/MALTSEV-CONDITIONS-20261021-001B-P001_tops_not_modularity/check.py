#!/usr/bin/env python3
"""Checks for MALTSEV-CONDITIONS-20261021-001B-P001. The statements are in proof.md.

Values: the lifts live on {0,1,2,3} with g = (0,1,2,2) (3 is read as 2); shadows on pairs encoded as 2a+b.

Checks:
- Theorem 1. The explicit Hagemann-Mitschke terms p1, p2 and Gumm terms p, j for K4 are polymorphisms and satisfy
  their identities; K4 is not rectangular, so it has no Mal'tsev polymorphism.
- Theorem 2 (restriction lemma).
  - (a) On 20 random ternary polymorphisms of K6 found by a small solver, every fibre restriction is a polymorphism of
    'not exactly two ones'.
  - (b) K4's terms restricted to the class {2,3} are polymorphisms of the block relation and satisfy the identities.
- Theorem 3. The ternary and 4-ary polymorphisms of 'not exactly two ones' are exactly the conjunctions and the
  constants; there is no Hagemann-Mitschke chain and no Day chain among them (exhaustive); K6 composes like cycles
  (its constrained sets equal those of x+y+z=0 over Z3 on 300 random systems).
- Corollary 4. x+y+z=0 over Z6 and the Z2xZ2 law with its two line congruences have the Mal'tsev polymorphism
  x-y+z, and each has a failure (explicit systems); x+y+z=0 over Z2xZ2 alone has binary parity's free sets.
- Theorem 5. Explicit operations Mal'tsev modulo the tops for the lifts K4 (exact on {0,1,3}) and the GF(4) lift, and
  for the shadows K6 and K4x4; the pp-definitions used (the kernel of g for the lifts, equal first components for the
  shadows); the shadow operation failing for the Z3 law paired with itself; the census's solver witnesses for L223 and
  L233 re-verified.
- Census agreement with MALTSEV-CONDITIONS-20261021-001A-E001.

Controls, each of which must be rejected:
- 'composing like cycles implies congruence modularity' (K6);
- 'composing like cycles implies congruence n-permutability for some n' (K6);
- 'a Mal'tsev polymorphism implies composing like cycles' (Z6, and Z2xZ2 with its line congruences);
- 'every law is Mal'tsev on its tops' (the Boolean neither-knot, which is simple and has no Mal'tsev polymorphism).

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
CENSUS = ROOT / "artifacts" / "MALTSEV-CONDITIONS-20261021-001A" / "MALTSEV-CONDITIONS-20261021-001A-E001_conditions_census"
G = (0, 1, 2, 2)
GF4_MUL = [[0, 0, 0, 0], [0, 1, 2, 3], [0, 2, 3, 1], [0, 3, 1, 2]]


def lift_value(r):
    return {0: 0, 1: 1, 2: 3}[r % 3]


def v(x, y):
    return x if x == y else lift_value(2 * G[x] + 2 * G[y])


def p1(x, y, z):
    if y == z:
        return x
    if x == y:
        return v(x, z)
    return lift_value(G[x] + G[y] - G[z])


def p2(x, y, z):
    if x == y:
        return z
    if y == z:
        return v(x, y)
    return lift_value(2 * G[x] + G[y] + G[z])


def gumm_p(x, y, z):
    """Gumm's p: p(x,z,z) = x and p(x,x,z) = j(x,x,z)."""
    return x if y == z else lift_value(G[x] - G[y] + G[z])


def gumm_j(x, y, z):
    """Gumm's j1, with j2 the third projection: j1(x,y,x) = x and j1(x,z,z) = z."""
    return z if z in (x, y) else lift_value(G[z])


def is_pol(f, R, ar=3):
    k = len(next(iter(R)))
    Rs = sorted(R)
    return all(tuple(f(*(t[i] for t in ts)) for i in range(k)) in R for ts in product(Rs, repeat=ar))


def fibres(K, e):
    out = {}
    for t in K:
        out.setdefault(t[:e] + t[e + 1:], set()).add(t[e])
    return [frozenset(s) for s in out.values()]


def rectangular(K, k):
    return all(not (a != b and a & b) for e in range(k) for a in fibres(K, e) for b in fibres(K, e))


def two_pols(R, ar):
    args = list(product((0, 1), repeat=ar))
    k = len(next(iter(R)))
    Rs = sorted(R)
    out = []
    for tab in product((0, 1), repeat=2 ** ar):
        f = dict(zip(args, tab))
        if all(tuple(f[tuple(t[i] for t in ts)] for i in range(k)) in R for ts in product(Rs, repeat=ar)):
            out.append(f)
    return out


def is_conjunction_or_constant(f):
    vals = set(f.values())
    if len(vals) == 1:
        return True
    ar = len(next(iter(f)))
    S = [i for i in range(ar) if all(f[a] <= a[i] for a in f)]
    return all(f[a] == int(all(a[i] for i in S)) for a in f)


def hm_chain(P3):
    B = (0, 1)
    reach = {i for i, f in enumerate(P3) if all(f[(x, y, y)] == x for x in B for y in B)}
    frontier = list(reach)
    while frontier:
        i = frontier.pop()
        for j, g in enumerate(P3):
            if j not in reach and all(P3[i][(x, x, y)] == g[(x, y, y)] for x in B for y in B):
                reach.add(j)
                frontier.append(j)
    return any(all(P3[i][(x, x, y)] == y for x in B for y in B) for i in reach)


def day_chain(P4):
    B = (0, 1)
    ok = [i for i, f in enumerate(P4) if all(f[(x, y, y, x)] == x for x in B for y in B)]
    reach = {(i, 0) for i in ok if all(P4[i][a] == a[0] for a in P4[i])}
    frontier = list(reach)
    while frontier:
        i, par = frontier.pop()
        for j in ok:
            if par == 0:
                same = all(P4[i][(x, x, u, u)] == P4[j][(x, x, u, u)] for x in B for u in B)
            else:
                same = all(P4[i][(x, y, y, u)] == P4[j][(x, y, y, u)] for x in B for y in B for u in B)
            if same and (j, 1 - par) not in reach:
                reach.add((j, 1 - par))
                frontier.append((j, 1 - par))
    return any(all(P4[i][a] == a[3] for a in P4[i]) for i, _ in reach)


def solve_system(R, D, n, cons):
    out = []
    for a in product(range(D), repeat=n):
        if all(tuple(a[v2] for v2 in c) in R for c in cons):
            out.append(a)
    return out


def free_fn(S, n):
    rg = [len({t[i] for t in S}) for i in range(n)]
    memo = {}

    def f(Y):
        Y = tuple(sorted(Y))
        if Y not in memo:
            memo[Y] = len({tuple(t[i] for i in Y) for t in S}) == prod(rg[i] for i in Y)
        return memo[Y]

    return f


def subsets(n):
    return [Y for k in range(1, n + 1) for Y in combinations(range(n), k)]


def has_failure(S, n):
    f = free_fn(S, n)
    cs = [Y for Y in subsets(n) if not f(Y) and all(f(tuple(x for x in Y if x != w)) for w in Y)]
    return any(f(tuple(sorted((set(a) | set(b)) - {e}))) for a, b in combinations(cs, 2) for e in set(a) & set(b))


def ternary_polymorphism(R, D, fixed):
    """A ternary polymorphism of R with the entries in `fixed` prescribed, by arc consistency and backtracking."""
    k = len(next(iter(R)))
    Rs = sorted(R)
    args = list(product(range(D), repeat=3))
    scopes = sorted({tuple(tuple(t[i] for t in ts) for i in range(k)) for ts in product(Rs, repeat=3)})
    by_arg = {}
    for ci, sc in enumerate(scopes):
        for a in set(sc):
            by_arg.setdefault(a, []).append(ci)
    dom = {a: ({fixed[a]} if a in fixed else set(range(D))) for a in args}

    def revise(dom, ci):
        sc = scopes[ci]
        sup = {a: set() for a in set(sc)}
        for t in Rs:
            seen, good = {}, True
            for a, x in zip(sc, t):
                if x not in dom[a] or seen.get(a, x) != x:
                    good = False
                    break
                seen[a] = x
            if good:
                for a, x in seen.items():
                    sup[a].add(x)
        changed = []
        for a, sset in sup.items():
            if sset != dom[a]:
                if not sset:
                    return None
                dom[a] = sset
                changed.append(a)
        return changed

    def propagate(dom, queue):
        queue, inq = list(queue), set(queue)
        while queue:
            ci = queue.pop()
            inq.discard(ci)
            ch = revise(dom, ci)
            if ch is None:
                return False
            for a in ch:
                for cj in by_arg[a]:
                    if cj not in inq:
                        inq.add(cj)
                        queue.append(cj)
        return True

    def go(dom, depth=0):
        free = [a for a in args if len(dom[a]) > 1]
        if not free:
            return {a: next(iter(d)) for a, d in dom.items()}
        a = min(free, key=lambda u: len(dom[u]))
        for x in sorted(dom[a]):
            d2 = {u: set(sv) for u, sv in dom.items()}
            d2[a] = {x}
            if propagate(d2, by_arg[a]):
                r = go(d2, depth + 1)
                if r is not None:
                    return r
        return None

    if not propagate(dom, range(len(scopes))):
        return None
    return go(dom)


def random_polymorphisms(R, D, count, rng):
    out = []
    tries = 0
    args = list(product(range(D), repeat=3))
    while len(out) < count and tries < 10 * count:
        tries += 1
        fixed = {a: rng.randrange(D) for a in rng.sample(args, 3)}
        f = ternary_polymorphism(R, D, fixed)
        if f is not None:
            out.append(f)
    return out


def run():
    checks, controls, failures = {}, {}, []
    rng = random.Random(20261023)
    M3 = {t for t in product(range(3), repeat=3) if sum(t) % 3 == 0}
    L = {t for t in product(range(4), repeat=3) if tuple(G[x] for x in t) in M3}
    K4 = L - {(2, 2, 2)}
    not_two = {t for t in product((0, 1), repeat=3) if sum(t) != 2}
    K6 = {tuple(2 * a + b for a, b in zip(u, w)) for u in M3 for w in not_two}
    M4 = {t for t in product(range(2), repeat=4) if sum(t) % 2 == 0}
    K4x4 = {tuple(2 * a + b for a, b in zip(u, w)) for u in M4 for w in M4 | {(1, 0, 0, 0)}}
    D4 = range(4)

    # Theorem 1
    thm1 = {
        "hm_polymorphisms": is_pol(p1, K4) and is_pol(p2, K4),
        "hm_identities": all(p1(x, y, y) == x and p1(x, x, y) == p2(x, y, y) and p2(x, x, y) == y for x in D4 for y in D4),
        "gumm_polymorphisms": is_pol(gumm_p, K4) and is_pol(gumm_j, K4),
        "gumm_identities": all(gumm_j(x, y, x) == x and gumm_p(x, z, z) == x and gumm_p(x, x, z) == gumm_j(x, x, z)
                               and gumm_j(x, z, z) == z for x in D4 for y in D4 for z in D4),
        "K4_rectangular": rectangular(K4, 3),
    }
    checks["theorem_1_K4"] = thm1
    if not (thm1["hm_polymorphisms"] and thm1["hm_identities"] and thm1["gumm_polymorphisms"] and thm1["gumm_identities"]) \
            or thm1["K4_rectangular"]:
        failures.append("Theorem 1")

    # Theorem 2 (a): fibre restrictions of random polymorphisms of K6
    pols6 = random_polymorphisms(K6, 6, 20, rng)
    fibre_ok = 0
    for F in pols6:
        good = True
        for a in range(3):
            gfun = {bs: F[tuple(2 * a + b for b in bs)] % 2 for bs in product((0, 1), repeat=3)}
            good = good and all(tuple(gfun[tuple(t[i] for t in ts)] for i in range(3)) in not_two
                                for ts in product(sorted(not_two), repeat=3))
        fibre_ok += good
    # Theorem 2 (b): K4's terms on the class {2, 3}
    block = set(product((2, 3), repeat=3)) - {(2, 2, 2)}
    cls_ok = all(f(*t) in (2, 3) for f in (p1, p2, gumm_p, gumm_j) for t in product((2, 3), repeat=3)) and \
        all(is_pol(f, block) for f in (p1, p2, gumm_p, gumm_j))
    checks["theorem_2_restriction"] = {"random_K6_polymorphisms": len(pols6), "fibre_restrictions_are_polymorphisms": fibre_ok,
                                       "K4_terms_preserve_the_block": cls_ok}
    if not pols6 or fibre_ok != len(pols6) or not cls_ok:
        failures.append("Theorem 2")

    # Theorem 3
    P3, P4 = two_pols(not_two, 3), two_pols(not_two, 4)
    thm3 = {"ternary_polymorphisms": len(P3), "quaternary_polymorphisms": len(P4),
            "all_conjunctions_or_constants": all(is_conjunction_or_constant(f) for f in P3 + P4),
            "hm_chain": hm_chain(P3), "day_chain": day_chain(P4)}
    agree = 0
    systems = 0
    while systems < 300:
        n = rng.randint(3, 5)
        cons = [tuple(rng.randrange(n) for _ in range(3)) for _ in range(rng.randint(1, 4))]
        if len({x for c in cons for x in c}) < n:
            continue
        systems += 1
        S6 = solve_system(K6, 6, n, cons)
        S3 = solve_system(M3, 3, n, cons)
        f6, f3 = free_fn(S6, n), free_fn(S3, n)
        agree += all(f6(Y) == f3(Y) for Y in subsets(n))
    thm3["K6_systems"] = systems
    thm3["K6_constrained_sets_equal_Z3"] = agree
    checks["theorem_3_K6"] = thm3
    if not thm3["all_conjunctions_or_constants"] or thm3["hm_chain"] or thm3["day_chain"] or agree != systems:
        failures.append("Theorem 3")

    # Corollary 4: Mal'tsev laws that do not compose like cycles
    Z6 = {t for t in product(range(6), repeat=3) if sum(t) % 6 == 0}
    V4 = {(x, y, x ^ y) for x in range(4) for y in range(4)}
    cor4 = {
        "Z6_maltsev": is_pol(lambda x, y, z: (x - y + z) % 6, Z6),
        "Z2xZ2_maltsev": is_pol(lambda x, y, z: x ^ y ^ z, V4),
    }
    found = None
    for _ in range(3000):
        n = rng.randint(3, 5)
        cons = [tuple(rng.randrange(n) for _ in range(3)) for _ in range(rng.randint(1, 4))]
        if len({x for c in cons for x in c}) < n:
            continue
        S = solve_system(Z6, 6, n, cons)
        if S and has_failure(S, n):
            found = (n, cons)
            break
    cor4["Z6_failure_system"] = found
    # the Z2xZ2 law with its two line congruences x+y in {0,1} and x+y in {0,2}: x-y+z preserves both, and
    # the ties {x,e} and {e,y} of h1(x,e) and h2(e,y) leave {x,y} free
    h1 = {(x, y) for x in range(4) for y in range(4) if x ^ y in (0, 1)}
    h2 = {(x, y) for x in range(4) for y in range(4) if x ^ y in (0, 2)}
    cor4["Z2xZ2_line_congruences_maltsev"] = is_pol(lambda x, y, z: x ^ y ^ z, h1) and is_pol(lambda x, y, z: x ^ y ^ z, h2)
    S = [(x, e, y) for x in range(4) for e in range(4) for y in range(4) if (x, e) in h1 and (e, y) in h2]
    f = free_fn(S, 3)
    cor4["Z2xZ2_with_lines_fails"] = (not f((0, 1))) and (not f((1, 2))) and f((0, 2)) and f((0,)) and f((1,)) and f((2,))
    # x+y+z=0 over Z2xZ2 alone is binary parity on both bits: its free sets are parity's, so it composes like cycles
    P2 = {t for t in product(range(2), repeat=3) if sum(t) % 2 == 0}
    same = 0
    for _ in range(200):
        n = rng.randint(3, 5)
        cons = [tuple(rng.randrange(n) for _ in range(3)) for _ in range(rng.randint(1, 4))]
        fV, fP = free_fn(solve_system(V4, 4, n, cons), n), free_fn(solve_system(P2, 2, n, cons), n)
        same += all(fV(Y) == fP(Y) for Y in subsets(n))
    cor4["Z2xZ2_sum_zero_alone_has_parity_free_sets"] = same
    checks["corollary_4_incomparable"] = cor4
    if not (cor4["Z6_maltsev"] and cor4["Z2xZ2_maltsev"] and cor4["Z6_failure_system"] and cor4["Z2xZ2_line_congruences_maltsev"]
            and cor4["Z2xZ2_with_lines_fails"] and same == 200):
        failures.append("Corollary 4")

    # Theorem 5: Mal'tsev modulo the tops
    lift_F = lambda x, y, z: lift_value(G[x] - G[y] + G[z])
    top_lift = lambda x: {0: {0}, 1: {1}, 2: {2, 3}, 3: {2, 3}}[x]
    thm5 = {}
    thm5["K4 (lift)"] = is_pol(lift_F, K4) and all(lift_F(x, y, y) in top_lift(x) and lift_F(x, x, y) in top_lift(y) for x in D4 for y in D4) \
        and all(lift_F(x, y, y) == x and lift_F(x, x, y) == y for x in (0, 1, 3) for y in (0, 1, 3))
    MG = {(x, y, GF4_MUL[2][x] ^ GF4_MUL[3][y]) for x in range(4) for y in range(4)}
    g5 = (0, 1, 2, 3, 1)
    LG = {t for t in product(range(5), repeat=3) if tuple(g5[x] for x in t) in MG} - {(1, 1, 1)}
    h5 = {0: 0, 1: 4, 2: 2, 3: 3}
    FG = lambda x, y, z: h5[g5[x] ^ g5[y] ^ g5[z]]
    top5 = lambda x: {1, 4} if g5[x] == 1 else {x}
    thm5["GF(4) lift"] = is_pol(FG, LG) and all(FG(x, y, y) in top5(x) and FG(x, x, y) in top5(y) for x in range(5) for y in range(5)) \
        and all(FG(x, y, y) == x and FG(x, x, y) == y for x in (0, 2, 3, 4) for y in (0, 2, 3, 4))
    def F6(x, y, z):
        m = (x // 2 - y // 2 + z // 2) % 3  # the Z3 difference of the first components
        return 2 * m + (1 if m == 2 else 0)  # second component h(m)
    thm5["K6 (shadow)"] = is_pol(F6, K6) and all(F6(x, y, y) // 2 == x // 2 and F6(x, x, y) // 2 == y // 2 for x in range(6) for y in range(6))
    F44 = lambda x, y, z: 3 * ((x // 2 + y // 2 + z // 2) % 2)
    thm5["K4x4 (shadow)"] = is_pol(F44, K4x4) and all(F44(x, y, y) // 2 == x // 2 and F44(x, x, y) // 2 == y // 2 for x in D4 for y in D4)
    census_witnesses = {}
    if (CENSUS / "raw_rows.jsonl").exists():
        for line in (CENSUS / "raw_rows.jsonl").read_text().splitlines():
            r = json.loads(line)
            if r["part"] == "tops" and r["law"] in ("L223", "L233") and r["table"]:
                R = {tuple(t) for t in r["relation"]}
                tab = dict(zip(product(range(4), repeat=3), r["table"]))
                F = lambda x, y, z, tab=tab: tab[(x, y, z)]
                census_witnesses[r["law"]] = is_pol(F, R) and all(F(x, y, y) in top_lift(x) and F(x, x, y) in top_lift(y) for x in D4 for y in D4)
    thm5["census witnesses (L223, L233)"] = census_witnesses

    def linked(R, D):
        """The pp-definable relation: some tuple z with R(x, z) and R(y, z)."""
        k = len(next(iter(R)))
        return {(x, y) for x in range(D) for y in range(D)
                if any((x,) + zs in R and (y,) + zs in R for zs in product(range(D), repeat=k - 1))}

    pp = {
        "K4: kernel of g": linked(K4, 4) == {(x, y) for x in D4 for y in D4 if G[x] == G[y]},
        "GF(4) lift: kernel of g": linked(LG, 5) == {(x, y) for x in range(5) for y in range(5) if g5[x] == g5[y]},
        "K6: equal first components": linked(K6, 6) == {(x, y) for x in range(6) for y in range(6) if x // 2 == y // 2},
        "K4x4: equal first components": linked(K4x4, 4) == {(x, y) for x in D4 for y in D4 if x // 2 == y // 2},
    }
    thm5["pp-definitions"] = pp
    # the hypothesis on shadows is needed: for M = K = the Z3 law and h the identity, every pp-definable equivalence is
    # E x E, and the shadow operation (m, h(m)) is Mal'tsev modulo E x E for no proper equivalence E on Z3
    MM = {tuple(3 * a + b for a, b in zip(u, w)) for u in M3 for w in M3}
    Fid = lambda x, y, z: 4 * ((x // 3 - y // 3 + z // 3) % 3)
    proper = [{(a, b) for a in range(3) for b in range(3) if a == b or {a, b} == pair} for pair in (None, {0, 1}, {0, 2}, {1, 2})]
    thm5["identity shadow: operation preserves the law"] = is_pol(Fid, MM)
    thm5["identity shadow: fails modulo every proper E x E"] = all(
        any(not ((Fid(x, y, y) // 3, x // 3) in E and (Fid(x, y, y) % 3, x % 3) in E) for x in range(9) for y in range(9))
        for E in proper)
    checks["theorem_5_maltsev_on_tops"] = thm5
    if not all(v2 for k2, v2 in thm5.items() if not isinstance(v2, dict)) or not census_witnesses \
            or not all(census_witnesses.values()) or not all(pp.values()):
        failures.append("Theorem 5")

    census = {}
    if (CENSUS / "result.json").exists():
        a = json.loads((CENSUS / "result.json").read_text())
        census = {"predictions": a["predictions"], "signal": a["signal"]}
        if not all(a["predictions"].values()):
            failures.append("census agreement")
    checks["census_agreement"] = census

    NB = {(0, 0, 0), (0, 1, 0), (0, 1, 1), (1, 0, 1), (1, 1, 0)}
    maltsev_nb = [f for f in two_pols(NB, 3) if all(f[(x, y, y)] == x and f[(x, x, y)] == y for x in (0, 1) for y in (0, 1))]
    controls["composing_like_cycles_implies_modularity"] = {"rejected": not thm3["day_chain"] and agree == systems}
    controls["composing_like_cycles_implies_n_permutability"] = {"rejected": not thm3["hm_chain"] and agree == systems}
    controls["maltsev_implies_composing_like_cycles"] = {"rejected": bool(cor4["Z6_failure_system"] and cor4["Z2xZ2_with_lines_fails"])}
    controls["every_law_is_maltsev_on_its_tops"] = {"neither_knot_maltsev_operations": len(maltsev_nb), "rejected": not maltsev_nb}
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
