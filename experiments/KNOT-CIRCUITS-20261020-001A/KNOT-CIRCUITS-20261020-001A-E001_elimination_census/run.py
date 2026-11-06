#!/usr/bin/env python3
"""Producer for KNOT-CIRCUITS-20261020-001A-E001 (exploratory; see contract.json).

A set of variables is constrained when its projection is smaller than the
product of the variables' ranges. Circuits are minimal constrained sets, and
knots are circuits with at least 3 variables. A failure is a pair of circuits
sharing a variable e whose union without e is unconstrained.

1. Boolean relations of arity 2 and 3. Search systems of two copies for a
   failure, and hubs of two small knots for a failure between knots.
2. Binary relations on three elements. Search systems of two or three copies,
   then the binary pp-closure.
3. Coset laws of small groups, and the GF(4)-linear law. Use an explicit
   construction where some subgroup has two maximal normal subgroups, and
   random cosets otherwise.

Writes artifacts/KNOT-CIRCUITS-20261020-001A/<this folder>/:
result.json, raw_rows.jsonl and run_output.txt.

    python3 -B run.py
"""

from __future__ import annotations

import json
import random
import sys
import time
from itertools import combinations, permutations, product
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUT = ROOT / "artifacts" / "KNOT-CIRCUITS-20261020-001A" / HERE.name
LOG = []
START = time.time()


def log(msg):
    line = f"[{time.time() - START:.0f}s] {msg}"
    LOG.append(line)
    print(line, flush=True)


# ------------------------------------------------------------------ circuits relative to ranges

def range_sizes(S, n):
    return [len({t[i] for t in S}) for i in range(n)]


def is_constrained(S, Y, sizes):
    full = 1
    for i in Y:
        full *= sizes[i]
    return len({tuple(t[i] for i in Y) for t in S}) < full


def circuits(S, n):
    sizes = range_sizes(S, n)
    found = []
    for size in range(2, n + 1):
        for Y in combinations(range(n), size):
            if any(set(C) <= set(Y) for C in found):
                continue
            if is_constrained(S, Y, sizes):
                found.append(Y)
    return found, sizes


def absolute_failure(S, n, q):
    """The same test with every variable's alternatives taken to be the whole domain."""
    found = []
    for size in range(1, n + 1):
        for Y in combinations(range(n), size):
            if not any(set(C) <= set(Y) for C in found) and len({tuple(t[i] for i in Y) for t in S}) < q ** size:
                found.append(Y)
    for C1, C2 in combinations(found, 2):
        for e in sorted(set(C1) & set(C2)):
            Y = tuple(sorted((set(C1) | set(C2)) - {e}))
            if len({tuple(t[i] for i in Y) for t in S}) == q ** len(Y):
                return True
    return False


def failure(S, n, knots_only=False):
    found, sizes = circuits(S, n)
    for C1, C2 in combinations(found, 2):
        if knots_only and (len(C1) < 3 or len(C2) < 3):
            continue
        for e in sorted(set(C1) & set(C2)):
            Y = tuple(sorted((set(C1) | set(C2)) - {e}))
            if not is_constrained(S, Y, sizes):
                return [list(C1), list(C2), e]
    return None


def system(R, copies, n_total, n_vis, q):
    out = set()
    for a in product(range(q), repeat=n_total):
        if all(tuple(a[v] for v in tup) in R for tup in copies):
            out.add(a[:n_vis])
    return out


def is_knot(S, n):
    if n < 3 or not S:
        return False
    found, _ = circuits(S, n)
    return found == [tuple(range(n))]


# ------------------------------------------------------------------ part 1: Boolean relations

def affine(R):
    return all(tuple(a ^ b ^ c for a, b, c in zip(t1, t2, t3)) in R for t1 in R for t2 in R for t3 in R)


def bijunctive(R):
    return all(tuple((a & b) | (b & c) | (a & c) for a, b, c in zip(t1, t2, t3)) in R
               for t1 in R for t2 in R for t3 in R)


def boolean_failure_search(R, k):
    for n_total in range(3, 6):
        tuples = list(product(range(n_total), repeat=k))
        for n_vis in range(max(3, n_total - 2), n_total + 1):
            for i, t1 in enumerate(tuples):
                for t2 in tuples[i:]:
                    if not set(range(n_vis)) <= set(t1) | set(t2):
                        continue
                    S = system(R, (t1, t2), n_total, n_vis, 2)
                    if S:
                        f = failure(S, n_vis)
                        if f:
                            return {"copies": [list(t1), list(t2)], "n_total": n_total, "n_vis": n_vis, "circuits": f}
    return None


def knot_pool(R, k, cap=10):
    pool = {}
    for n_total in range(3, 5):
        tuples = list(product(range(n_total), repeat=k))
        for n_vis in range(3, n_total + 1):
            for m in (1, 2):
                for copies in combinations(tuples, m) if m == 2 else ((t,) for t in tuples):
                    if not set(range(n_vis)) <= set(v for t in copies for v in t):
                        continue
                    S = system(R, copies, n_total, n_vis, 2)
                    if is_knot(S, n_vis):
                        key = (n_vis, frozenset(S))
                        pool.setdefault(key, {"copies": [list(t) for t in copies], "n_total": n_total, "n_vis": n_vis})
    if k == 3:
        for p1 in permutations(range(3)):
            for p2 in permutations(range(3)):
                # variables x=0, y=1, e=2, s=3 visible, h=4 hidden: R(.., h, ..) and R(.., h, ..)
                t1 = tuple((0, 1, 4)[p1[i]] for i in range(3))
                t2 = tuple((4, 2, 3)[p2[i]] for i in range(3))
                S = system(R, (t1, t2), 5, 4, 2)
                if is_knot(S, 4):
                    pool.setdefault((4, frozenset(S)), {"copies": [list(t1), list(t2)], "n_total": 5, "n_vis": 4})
    items = sorted(pool.items(), key=lambda kv: (kv[0][0], sorted(kv[0][1])))
    return items[:cap]


def hub(K1, n1, K2, n2, shared):
    """Join K1 (variables 0..n1-1) and K2 on fresh variables, identifying K2 position b with K1 position a for (a, b) in shared."""
    pos2 = {b: a for a, b in shared}
    fresh = [b for b in range(n2) if b not in pos2]
    index = {b: n1 + j for j, b in enumerate(fresh)}
    index.update(pos2)
    N = n1 + len(fresh)
    S = set()
    for t1 in K1:
        for t2 in K2:
            if all(t1[a] == t2[b] for a, b in shared):
                full = list(t1) + [None] * len(fresh)
                for b in fresh:
                    full[index[b]] = t2[b]
                S.add(tuple(full))
    C1 = tuple(range(n1))
    C2 = tuple(sorted(index[b] for b in range(n2)))
    return S, N, C1, C2


def knot_hub_search(pool):
    """Each pool relation is a knot on open variables, so sharing at most two of its variables keeps both knots as
    circuits of the join; only the elimination test is needed, and a found witness is re-verified in full."""
    for (k1, d1), (k2, d2) in product(pool, repeat=2):
        n1, K1 = k1
        n2, K2 = k2
        shares = [[(a, b)] for a in range(n1) for b in range(n2)]
        shares += [[(a1, b1), (a2, b2)] for a1, a2 in combinations(range(n1), 2) for b1 in range(n2) for b2 in range(n2)
                   if b1 != b2]
        for shared in shares:
            S, N, C1, C2 = hub(K1, n1, K2, n2, shared)
            sizes = range_sizes(S, N)
            for a, _ in shared:
                Y = tuple(sorted((set(C1) | set(C2)) - {a}))
                if not is_constrained(S, Y, sizes):
                    found, _ = circuits(S, N)
                    if C1 in found and C2 in found:
                        return {"knot1": d1, "knot2": d2, "shared": [list(p) for p in shared], "eliminated": a}
    return None


def boolean_part(rows):
    for k in (2, 3):
        for mask in range(1, 2 ** (2 ** k) - 1):
            R = {t for i, t in enumerate(product((0, 1), repeat=k)) if mask >> i & 1}
            row = {"part": "boolean", "k": k, "relation": sorted(R), "affine": affine(R), "bijunctive": bijunctive(R)}
            row["failure"] = boolean_failure_search(R, k)
            pool = knot_pool(R, k)
            row["knot_pool"] = len(pool)
            row["knot_failure"] = knot_hub_search(pool) if pool else None
            row["any_failure"] = bool(row["failure"] or row["knot_failure"])
            rows.append(row)
        log(f"boolean arity {k} done")


# ------------------------------------------------------------------ part 2: binary relations on three elements

def has_maltsev(R, q):
    R = sorted(R)
    Rs = set(R)
    k = len(R[0])
    free = [(x, y, z) for x in range(q) for y in range(q) for z in range(q) if x != y and y != z]
    m = {}
    for x in range(q):
        for y in range(q):
            m[(x, x, y)] = y
            m[(y, x, x)] = y
    triples = [(a, b, c) for a in R for b in R for c in R]

    def consistent():
        for a, b, c in triples:
            out = []
            for i in range(k):
                key = (a[i], b[i], c[i])
                if key not in m:
                    break
                out.append(m[key])
            else:
                if tuple(out) not in Rs:
                    return False
        return True

    def go(i):
        if i == len(free):
            return True
        for v in range(q):
            m[free[i]] = v
            if consistent() and go(i + 1):
                return True
        del m[free[i]]
        return False

    return go(0)


def isolated_value(R, q):
    for c in range(q):
        if (c, c) in R and all(c not in t for t in R if t != (c, c)):
            return c
    return None


def three_element_search(R, q=3):
    for n_total in range(3, 5):
        tuples = list(product(range(n_total), repeat=2))
        for n_vis in range(3, n_total + 1):
            for m in (2, 3):
                for copies in combinations(tuples, m):
                    if not set(range(n_vis)) <= set(v for t in copies for v in t):
                        continue
                    S = system(R, copies, n_total, n_vis, q)
                    if S:
                        f = failure(S, n_vis)
                        if f:
                            return {"copies": [list(t) for t in copies], "n_total": n_total, "n_vis": n_vis, "circuits": f}
    return None


def binary_closure(R, q=3, cap=700):
    rels = [frozenset(R), frozenset((x, x) for x in range(q))]
    deriv = [("R",), ("eq",)]
    seen = {rels[0]: 0, rels[1]: 1}
    i = 0
    while i < len(rels) and len(rels) < cap:
        for j in range(i + 1):
            A, B = rels[i], rels[j]
            cands = [(frozenset((y, x) for x, y in A), ("conv", i)),
                     (frozenset((x, z) for (x, y) in A for (y2, z) in B if y == y2), ("comp", i, j)),
                     (frozenset((x, z) for (x, y) in B for (y2, z) in A if y == y2), ("comp", j, i)),
                     (A & B, ("and", i, j))]
            for C, d in cands:
                if C and C not in seen:
                    seen[C] = len(rels)
                    rels.append(C)
                    deriv.append(d)
        i += 1
    return rels, deriv


def closure_hub(rels):
    for i, T1 in enumerate(rels):
        l1 = {x for x, _ in T1}
        r1 = {y for _, y in T1}
        if len(T1) == len(l1) * len(r1):
            continue
        for j, T2 in enumerate(rels):
            l2 = {x for x, _ in T2}
            r2 = {y for _, y in T2}
            if l2 != r1 or len(T2) == len(l2) * len(r2):
                continue
            C = {(x, z) for (x, y) in T1 for (y2, z) in T2 if y == y2}
            if len(C) == len(l1) * len(r2):
                return i, j
    return None


def three_element_part(rows):
    q = 3
    for mask in range(1, 2 ** 9 - 1):
        R = {t for i, t in enumerate(product(range(q), repeat=2)) if mask >> i & 1}
        row = {"part": "three", "relation": sorted(R), "maltsev": has_maltsev(R, q), "isolated_value": isolated_value(R, q)}
        f = three_element_search(R, q)
        row["failure"] = f
        row["closure_failure"] = None
        if f is None:
            rels, deriv = binary_closure(R, q)
            h = closure_hub(rels)
            if h is not None:
                row["closure_failure"] = {"T1": h[0], "T2": h[1], "derivations": deriv[:max(h) + 1]}
        row["any_failure"] = bool(row["failure"] or row["closure_failure"])
        rows.append(row)
    log("three-element binary relations done")


# ------------------------------------------------------------------ part 3: groups

def perm_group(gens, deg):
    G = {tuple(range(deg))}
    frontier = list(G)
    while frontier:
        new = []
        for g in frontier:
            for h in gens:
                x = tuple(g[h[i]] for i in range(deg))
                if x not in G:
                    G.add(x)
                    new.append(x)
        frontier = new
    return sorted(G)


def regular(elements, op):
    ix = {e: i for i, e in enumerate(elements)}
    return perm_group([tuple(ix[op(e, f)] for f in elements) for e in elements], len(elements))


def table(elems):
    n = len(elems)
    ix = {p: i for i, p in enumerate(elems)}
    deg = len(elems[0])
    mul = [[ix[tuple(elems[a][elems[b][i]] for i in range(deg))] for b in range(n)] for a in range(n)]
    ident = ix[tuple(range(deg))]
    inv = [next(b for b in range(n) if mul[a][b] == ident) for a in range(n)]
    return mul, inv, ident


def groups():
    out = {}
    for m in (2, 3, 4, 5, 8, 9, 6):
        out[f"Z{m}"] = perm_group([tuple((i + 1) % m for i in range(m))], m)
    out["Z2xZ2"] = regular([(a, b) for a in (0, 1) for b in (0, 1)], lambda u, v: (u[0] ^ v[0], u[1] ^ v[1]))
    out["S3"] = perm_group([(1, 0, 2), (1, 2, 0)], 3)
    out["A4"] = perm_group([(1, 2, 0, 3), (1, 0, 3, 2)], 4)
    out["D4"] = perm_group([(1, 2, 3, 0), (3, 2, 1, 0)], 4)
    units = {("1", u): (1, u) for u in "1ijk"}
    units.update({(u, "1"): (1, u) for u in "1ijk"})
    units.update({("i", "i"): (-1, "1"), ("j", "j"): (-1, "1"), ("k", "k"): (-1, "1"), ("i", "j"): (1, "k"),
                  ("j", "k"): (1, "i"), ("k", "i"): (1, "j"), ("j", "i"): (-1, "k"), ("k", "j"): (-1, "i"),
                  ("i", "k"): (-1, "j")})
    out["Q8"] = regular([(s, u) for s in (1, -1) for u in "1ijk"],
                        lambda a, b: (a[0] * b[0] * units[(a[1], b[1])][0], units[(a[1], b[1])][1]))

    def dic(p, r):
        (k1, e1), (k2, e2) = p, r
        if e1 == 0:
            return ((k1 + k2) % 6, e2)
        k = (k1 - k2) % 6
        return ((k + 3) % 6, 0) if e2 == 1 else (k, 1)

    out["Dic3"] = regular([(k, e) for e in (0, 1) for k in range(6)], dic)
    return out


def subgroups(mul, inv, ident, n):
    subs = set()
    for gens in combinations(range(n), 3):
        H = {ident}
        frontier = [ident]
        while frontier:
            new = []
            for h in frontier:
                for g in gens:
                    x = mul[h][g]
                    if x not in H:
                        H.add(x)
                        new.append(x)
            frontier = new
        subs.add(frozenset(H))
    for g in range(n):
        H = {ident}
        x = g
        while x not in H:
            H.add(x)
            x = mul[x][g]
        subs.add(frozenset(H))
    subs.add(frozenset({ident}))
    return subs


def maximal_normal(H, subs, mul, inv):
    normal = [N for N in subs if N <= H and N != H
              and all(mul[mul[h][x]][inv[h]] in N for h in H for x in N)]
    return [N for N in normal if not any(N < M for M in normal)]


def coset_closure(T, mul, inv, ident):
    t0 = T[0]
    gens = [tuple(mul[a][inv[b]] for a, b in zip(t, t0)) for t in T[1:]]
    e = tuple(ident for _ in t0)
    H = {e}
    frontier = [e]
    while frontier:
        new = []
        for h in frontier:
            for g in gens:
                x = tuple(mul[a][b] for a, b in zip(h, g))
                if x not in H:
                    H.add(x)
                    new.append(x)
        frontier = new
    return {tuple(mul[a][b] for a, b in zip(h, t0)) for h in H}


def gf4():
    add = [[a ^ b for b in range(4)] for a in range(4)]
    exp = [1, 2, 3]  # alpha = 2, alpha^2 = alpha + 1 = 3
    def mult(a, b):
        if a == 0 or b == 0:
            return 0
        return exp[(exp.index(a) + exp.index(b)) % 3]
    return add, mult


def gf4_coset(rng, n):
    add, mult = gf4()
    gens = [tuple(rng.randrange(4) for _ in range(n)) for _ in range(rng.randint(1, 3))]
    span = {tuple([0] * n)}
    for g in gens:
        span = {tuple(add[s[i]][mult(c, g[i])] for i in range(n)) for s in span for c in range(4)}
    t0 = tuple(rng.randrange(4) for _ in range(n))
    return {tuple(add[s[i]][t0[i]] for i in range(n)) for s in span}


def group_part(rows, rng):
    for name, elems in groups().items():
        mul, inv, ident = table(elems)
        n = len(elems)
        subs = subgroups(mul, inv, ident, n)
        bad = None
        for H in sorted(subs, key=len):
            if len(H) < 2:
                continue
            M = maximal_normal(H, subs, mul, inv)
            if len(M) >= 2:
                bad = (H, M[0], M[1])
                break
        row = {"part": "group", "name": name, "order": n, "subgroups": len(subs), "condition_holds": bad is None}
        if bad:
            H, N1, N2 = bad
            S = {(x, e, z) for x in H for e in H for z in H if mul[x][inv[e]] in N1 and mul[e][inv[z]] in N2}
            row["construction"] = {"H": sorted(H), "N1": sorted(N1), "N2": sorted(N2), "failure": failure(S, 3),
                                   "absolute_failure": absolute_failure(S, 3, n)}
        random_fail = 0
        for dim in (3, 4):
            for _ in range(300):
                T = [tuple(rng.randrange(n) for _ in range(dim)) for _ in range(rng.randint(2, 4))]
                S = coset_closure(T, mul, inv, ident)
                if len(S) < n ** dim and failure(S, dim):
                    random_fail += 1
        row["random_failures"] = random_fail
        row["any_failure"] = bool(bad and row["construction"]["failure"]) or random_fail > 0
        rows.append(row)
        log(f"group {name} done")
    gf = 0
    for dim in (3, 4):
        for _ in range(300):
            S = gf4_coset(rng, dim)
            if len(S) < 4 ** dim and failure(S, dim):
                gf += 1
    rows.append({"part": "group", "name": "GF(4)-linear", "order": 4, "condition_holds": True, "random_failures": gf,
                 "any_failure": gf > 0})


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    rng = random.Random(20261020)
    rows = []
    boolean_part(rows)
    three_element_part(rows)
    group_part(rows, rng)

    boolean = [r for r in rows if r["part"] == "boolean"]
    three = [r for r in rows if r["part"] == "three"]
    grp = [r for r in rows if r["part"] == "group"]
    p1 = all(r["any_failure"] != r["affine"] for r in boolean) and not any(r["failure"] for r in boolean if r["affine"])
    p2 = all(bool(r["knot_failure"]) == (not r["affine"] and not r["bijunctive"]) for r in boolean)
    p3 = (not any(r["any_failure"] for r in three if r["maltsev"])
          and all(r["any_failure"] == (r["isolated_value"] is None) for r in three if not r["maltsev"])
          and not any(r["any_failure"] for r in three if r["isolated_value"] is not None))
    p4 = all(r["any_failure"] == (not r["condition_holds"]) for r in grp)
    nae_tuples = [t for t in product((0, 1), repeat=3) if len(set(t)) > 1]
    nae = next(r for r in boolean if r["k"] == 3 and r["relation"] == nae_tuples)
    by_name = {r["name"]: r for r in grp}
    controls = {
        "C1_self_complementary_rejected": nae["any_failure"],
        "C2_maltsev_suffices_rejected": by_name["Z2xZ2"]["any_failure"],
        "C3_abelian_criterion_rejected": (not by_name["S3"]["any_failure"]) and by_name["Z2xZ2"]["any_failure"],
        "C4_absolute_convention": {name: r["construction"]["absolute_failure"] for name, r in by_name.items()
                                   if "construction" in r},
    }
    summary = {
        "boolean": {"relations": len(boolean), "affine": sum(r["affine"] for r in boolean),
                    "bijunctive": sum(r["bijunctive"] for r in boolean),
                    "with_failure": sum(r["any_failure"] for r in boolean),
                    "with_knot_failure": sum(bool(r["knot_failure"]) for r in boolean)},
        "three": {"relations": len(three), "maltsev": sum(r["maltsev"] for r in three),
                  "maltsev_with_failure": sum(r["any_failure"] for r in three if r["maltsev"]),
                  "non_maltsev": sum(not r["maltsev"] for r in three),
                  "non_maltsev_with_failure": sum(r["any_failure"] for r in three if not r["maltsev"]),
                  "isolated_value": sum(r["isolated_value"] is not None for r in three),
                  "found_by_closure": sum(bool(r["closure_failure"]) for r in three)},
        "groups": {r["name"]: {"condition_holds": r["condition_holds"], "any_failure": r["any_failure"],
                               "random_failures": r["random_failures"]} for r in grp},
    }
    result = {"experiment_id": "KNOT-CIRCUITS-20261020-001A-E001", "evidence_stage": "exploratory", "summary": summary,
              "predictions": {"P1": p1, "P2": p2, "P3": p3, "P4": p4}, "controls": controls,
              "signal": p1 and p2 and p3 and p4, "wall_seconds": round(time.time() - START, 1)}
    (OUT / "result.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    with (OUT / "raw_rows.jsonl").open("w") as fh:
        for r in rows:
            fh.write(json.dumps(r, sort_keys=True, default=list) + "\n")
    log(f"summary {json.dumps(summary)}")
    log(f"predictions {result['predictions']} controls {controls} signal {result['signal']}")
    (OUT / "run_output.txt").write_text("\n".join(LOG) + "\n")


if __name__ == "__main__":
    sys.exit(main())
