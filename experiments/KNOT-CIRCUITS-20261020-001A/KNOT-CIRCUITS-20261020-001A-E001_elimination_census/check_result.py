#!/usr/bin/env python3
"""Independent check of KNOT-CIRCUITS-20261020-001A-E001. It imports no producer code.

- Affinity is recomputed by linear algebra over GF(2): a relation is affine
  when it is a coset of the span of its differences. Bijunctivity is
  recomputed by comparing the relation with the conjunction of its unary and
  binary projections.
- Every recorded failure is rebuilt from its definition and verified with this
  file's own routines:
  - systems of copies;
  - pairs of knots joined on shared variables;
  - binary relations replayed from their derivations.
  Circuits are found here by testing that every set one smaller is
  unconstrained.
- Mal'tsev polymorphisms are searched with a different entry order, and
  isolated values are recomputed.
- Groups are rebuilt from their own presentations:
  - integers mod m;
  - pairs;
  - permutations filtered by sign;
  - quaternion arithmetic;
  - a semidirect product Z3 x| Z4.
  Their subgroups come from brute force over subsets. The congruence
  condition is recomputed, a failure is constructed independently where it
  fails, and fresh random cosets (another seed) replicate the no-failure
  verdicts.
- The prediction flags and controls are recomputed.
"""

from __future__ import annotations

import json
import random
import sys
from itertools import combinations, permutations, product
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
ART = ROOT / "artifacts" / "KNOT-CIRCUITS-20261020-001A" / HERE.name


# ------------------------------------------------------------------ circuits, checked by one-smaller subsets

def ranges(S, n):
    return [sorted({t[i] for t in S}) for i in range(n)]


def free(S, Y, rg):
    need = 1
    for i in Y:
        need *= len(rg[i])
    return len({tuple(t[i] for i in Y) for t in S}) == need


def is_circuit(S, Y, rg):
    if len(Y) < 2 or free(S, Y, rg):
        return False
    return all(free(S, tuple(v for v in Y if v != w), rg) for w in Y)


def verify_failure(S, n, C1, C2, e):
    rg = ranges(S, n)
    C1, C2 = tuple(sorted(C1)), tuple(sorted(C2))
    if C1 == C2 or e not in C1 or e not in C2:
        return False
    if not (is_circuit(S, C1, rg) and is_circuit(S, C2, rg)):
        return False
    return free(S, tuple(sorted((set(C1) | set(C2)) - {e})), rg)


def build(R, copies, n_total, n_vis, q):
    sols = set()
    for a in product(range(q), repeat=n_total):
        if all(tuple(a[v] for v in c) in R for c in copies):
            sols.add(a[:n_vis])
    return sols


def is_knot(K, n):
    rg = ranges(K, n)
    return n >= 3 and all(len(r) >= 2 for r in rg) and is_circuit(K, tuple(range(n)), rg)


# ------------------------------------------------------------------ Boolean classifications

def affine_gf2(R):
    R = sorted(R)
    r0 = R[0]
    vecs = [tuple(a ^ b for a, b in zip(t, r0)) for t in R]
    basis = []
    for v in vecs:
        v = list(v)
        for b in basis:
            p = next(i for i, x in enumerate(b) if x)
            if v[p]:
                v = [x ^ y for x, y in zip(v, b)]
        if any(v):
            basis.append(v)
    return len(R) == 2 ** len(basis)


def bijunctive_by_projections(R, k):
    pairs = {(i, j): {(t[i], t[j]) for t in R} for i in range(k) for j in range(k)}
    closure = {t for t in product((0, 1), repeat=k) if all((t[i], t[j]) in pairs[(i, j)] for (i, j) in pairs)}
    return closure == set(R)


# ------------------------------------------------------------------ three elements

def maltsev_search(R, q):
    R = list(R)
    Rs = set(R)
    k = len(R[0])
    entries = sorted([(x, y, z) for x in range(q) for y in range(q) for z in range(q) if x != y and y != z], reverse=True)
    m = {}
    for x in range(q):
        for y in range(q):
            m[(x, x, y)] = y
            m[(y, x, x)] = y
    trip = [(a, b, c) for a in R for b in R for c in R]

    def ok():
        for a, b, c in trip:
            keys = [(a[i], b[i], c[i]) for i in range(k)]
            if all(key in m for key in keys) and tuple(m[key] for key in keys) not in Rs:
                return False
        return True

    def go(i):
        if i == len(entries):
            return True
        for v in reversed(range(q)):
            m[entries[i]] = v
            if ok() and go(i + 1):
                return True
        del m[entries[i]]
        return False

    return go(0)


def replay(R, derivations, q):
    rels = []
    for d in derivations:
        if d[0] == "R":
            rels.append(frozenset(map(tuple, R)))
        elif d[0] == "eq":
            rels.append(frozenset((x, x) for x in range(q)))
        elif d[0] == "conv":
            rels.append(frozenset((y, x) for x, y in rels[d[1]]))
        elif d[0] == "comp":
            A, B = rels[d[1]], rels[d[2]]
            rels.append(frozenset((x, z) for x, y in A for y2, z in B if y == y2))
        elif d[0] == "and":
            rels.append(rels[d[1]] & rels[d[2]])
    return rels


# ------------------------------------------------------------------ groups from their own presentations

def zmod(m):
    els = list(range(m))
    return els, lambda a, b: (a + b) % m


def own_groups():
    out = {f"Z{m}": zmod(m) for m in (2, 3, 4, 5, 8, 9, 6)}
    out["Z2xZ2"] = ([(a, b) for a in (0, 1) for b in (0, 1)], lambda u, v: (u[0] ^ v[0], u[1] ^ v[1]))

    def compose(p, r):
        return tuple(p[r[i]] for i in range(len(p)))

    def sign(p):
        s = 1
        for i, j in combinations(range(len(p)), 2):
            if p[i] > p[j]:
                s = -s
        return s

    out["S3"] = (list(permutations(range(3))), compose)
    out["A4"] = ([p for p in permutations(range(4)) if sign(p) == 1], compose)
    rot, ref = (1, 2, 3, 0), (0, 3, 2, 1)
    d4 = {tuple(range(4))}
    while True:
        new = {compose(a, b) for a in d4 | {rot, ref} for b in d4 | {rot, ref}} | d4
        if new == d4:
            break
        d4 = new
    out["D4"] = (sorted(d4), compose)

    def hamilton(p, r):
        a1, b1, c1, d1 = p
        a2, b2, c2, d2 = r
        return (a1 * a2 - b1 * b2 - c1 * c2 - d1 * d2, a1 * b2 + b1 * a2 + c1 * d2 - d1 * c2,
                a1 * c2 - b1 * d2 + c1 * a2 + d1 * b2, a1 * d2 + b1 * c2 - c1 * b2 + d1 * a2)

    units = [tuple(s if i == j else 0 for i in range(4)) for j in range(4) for s in (1, -1)]
    out["Q8"] = (units, hamilton)
    out["Dic3"] = ([(a, b) for a in range(3) for b in range(4)],
                   lambda u, v: ((u[0] + (v[0] if u[1] % 2 == 0 else -v[0])) % 3, (u[1] + v[1]) % 4))
    return out


def brute_subgroups(els, op):
    ident = next(e for e in els if all(op(e, x) == x for x in els))
    others = [e for e in els if e != ident]
    subs = []
    for mask in range(1 << len(others)):
        H = {ident} | {others[i] for i in range(len(others)) if mask >> i & 1}
        if len(els) % len(H) == 0 and all(op(a, b) in H for a in H for b in H):
            subs.append(frozenset(H))
    return subs, ident


def two_maximal_normal(els, op, subs, ident):
    inv = {a: next(b for b in els if op(a, b) == ident) for a in els}
    for H in sorted(subs, key=len):
        if len(H) < 2:
            continue
        normal = [N for N in subs if N < H and all(op(op(h, x), inv[h]) in N for h in H for x in N)]
        maximal = [N for N in normal if not any(N < M for M in normal)]
        if len(maximal) >= 2:
            return H, maximal[0], maximal[1], inv
    return None


def random_coset(rng, els, op, inv, ident, n):
    gens = [tuple(rng.choice(els) for _ in range(n)) for _ in range(rng.randint(1, 3))]
    H = {tuple([ident] * n)}
    frontier = list(H)
    while frontier:
        new = []
        for h in frontier:
            for g in gens:
                x = tuple(op(a, b) for a, b in zip(h, g))
                if x not in H:
                    H.add(x)
                    new.append(x)
        frontier = new
    t0 = tuple(rng.choice(els) for _ in range(n))
    return {tuple(op(a, b) for a, b in zip(h, t0)) for h in H}


def has_failure(S, n):
    rg = ranges(S, n)
    circ = [Y for size in range(2, n + 1) for Y in combinations(range(n), size) if is_circuit(S, Y, rg)]
    for C1, C2 in combinations(circ, 2):
        for e in set(C1) & set(C2):
            if free(S, tuple(sorted((set(C1) | set(C2)) - {e})), rg):
                return True
    return False


def gf4_mult(a, b):
    # GF(4) as polynomials over GF(2) mod x^2 + x + 1, elements as bit pairs (high bit = x)
    r = 0
    for i in range(2):
        if b >> i & 1:
            r ^= a << i
    if r & 4:
        r ^= 0b111
    return r


def main() -> int:
    result = json.loads((ART / "result.json").read_text())
    rows = [json.loads(line) for line in (ART / "raw_rows.jsonl").read_text().splitlines()]
    problems = []
    report = {}

    boolean = [r for r in rows if r["part"] == "boolean"]
    verified = {"system": 0, "knot_hub": 0}
    for r in boolean:
        R = {tuple(t) for t in r["relation"]}
        k = r["k"]
        if affine_gf2(R) != r["affine"]:
            problems.append(f"affine flag differs for {r['relation']}")
        if bijunctive_by_projections(R, k) != r["bijunctive"]:
            problems.append(f"bijunctive flag differs for {r['relation']}")
        f = r["failure"]
        if f:
            S = build(R, [tuple(c) for c in f["copies"]], f["n_total"], f["n_vis"], 2)
            C1, C2, e = f["circuits"]
            if verify_failure(S, f["n_vis"], C1, C2, e):
                verified["system"] += 1
            else:
                problems.append(f"system witness fails for {r['relation']}")
        h = r["knot_failure"]
        if h:
            d1, d2 = h["knot1"], h["knot2"]
            K1 = build(R, [tuple(c) for c in d1["copies"]], d1["n_total"], d1["n_vis"], 2)
            K2 = build(R, [tuple(c) for c in d2["copies"]], d2["n_total"], d2["n_vis"], 2)
            n1, n2 = d1["n_vis"], d2["n_vis"]
            shared = {b: a for a, b in h["shared"]}
            fresh = [b for b in range(n2) if b not in shared]
            pos = {b: n1 + j for j, b in enumerate(fresh)}
            pos.update(shared)
            N = n1 + len(fresh)
            S = set()
            for t1 in K1:
                for t2 in K2:
                    if all(t1[a] == t2[b] for b, a in shared.items()):
                        full = list(t1) + [None] * len(fresh)
                        for b in fresh:
                            full[pos[b]] = t2[b]
                        S.add(tuple(full))
            ok = is_knot(K1, n1) and is_knot(K2, n2) and verify_failure(
                S, N, tuple(range(n1)), tuple(sorted(pos[b] for b in range(n2))), h["eliminated"])
            if ok:
                verified["knot_hub"] += 1
            else:
                problems.append(f"knot hub witness fails for {r['relation']}")
    report["boolean_witnesses_verified"] = verified

    three = [r for r in rows if r["part"] == "three"]
    tv = {"system": 0, "closure": 0}
    for r in three:
        R = {tuple(t) for t in r["relation"]}
        if maltsev_search(R, 3) != r["maltsev"]:
            problems.append(f"Mal'tsev flag differs for {r['relation']}")
        iso = [c for c in range(3) if (c, c) in R and all(c not in t for t in R if t != (c, c))]
        if (iso[0] if iso else None) != r["isolated_value"]:
            problems.append(f"isolated value differs for {r['relation']}")
        f = r["failure"]
        if f:
            S = build(R, [tuple(c) for c in f["copies"]], f["n_total"], f["n_vis"], 3)
            if verify_failure(S, f["n_vis"], *f["circuits"]):
                tv["system"] += 1
            else:
                problems.append(f"three-element system witness fails for {r['relation']}")
        c = r["closure_failure"]
        if c:
            rels = replay(r["relation"], c["derivations"], 3)
            T1, T2 = rels[c["T1"]], rels[c["T2"]]
            S = {(x, e, z) for x, e in T1 for e2, z in T2 if e == e2}
            if verify_failure(S, 3, (0, 1), (1, 2), 1):
                tv["closure"] += 1
            else:
                problems.append(f"closure witness fails for {r['relation']}")
    report["three_witnesses_verified"] = tv

    grp = {r["name"]: r for r in rows if r["part"] == "group"}
    rng = random.Random(7)
    gcheck = {}
    for name, (els, op) in own_groups().items():
        subs, ident = brute_subgroups(els, op)
        bad = two_maximal_normal(els, op, subs, ident)
        holds = bad is None
        inv = {a: next(b for b in els if op(a, b) == ident) for a in els}
        built = None
        if bad:
            H, N1, N2, _ = bad
            S = {(x, e, z) for x in H for e in H for z in H if op(x, inv[e]) in N1 and op(e, inv[z]) in N2}
            idx = {g: i for i, g in enumerate(els)}
            S = {tuple(idx[g] for g in t) for t in S}
            built = verify_failure(S, 3, (0, 1), (1, 2), 1)
        random_fail = 0
        if holds:
            idx = {g: i for i, g in enumerate(els)}
            for n in (3, 4):
                for _ in range(150):
                    S = {tuple(idx[g] for g in t) for t in random_coset(rng, els, op, inv, ident, n)}
                    if len(S) < len(els) ** n and has_failure(S, n):
                        random_fail += 1
        gcheck[name] = {"subgroups": len(subs), "condition_holds": holds, "construction_fails": built,
                        "random_failures": random_fail}
        if name in grp and grp[name]["condition_holds"] != holds:
            problems.append(f"congruence condition differs for {name}")
        if not holds and not built:
            problems.append(f"independent construction does not fail for {name}")
        if holds and random_fail:
            problems.append(f"random coset failure for {name}, which meets the condition")
    gf_fail = 0
    for n in (3, 4):
        for _ in range(150):
            gens = [tuple(rng.randrange(4) for _ in range(n)) for _ in range(rng.randint(1, 3))]
            span = {tuple([0] * n)}
            for g in gens:
                span = {tuple(s[i] ^ gf4_mult(c, g[i]) for i in range(n)) for s in span for c in range(4)}
            t0 = tuple(rng.randrange(4) for _ in range(n))
            S = {tuple(s[i] ^ t0[i] for i in range(n)) for s in span}
            if len(S) < 4 ** n and has_failure(S, n):
                gf_fail += 1
    gcheck["GF(4)-linear"] = {"random_failures": gf_fail}
    report["groups_independent"] = gcheck

    p1 = all(r["any_failure"] != affine_gf2({tuple(t) for t in r["relation"]}) for r in boolean)
    p2 = all(bool(r["knot_failure"]) == (not r["affine"] and not r["bijunctive"]) for r in boolean)
    p3 = (not any(r["any_failure"] for r in three if r["maltsev"])
          and all(r["any_failure"] == (r["isolated_value"] is None) for r in three if not r["maltsev"]))
    p4 = all(gcheck[name]["condition_holds"] == (not grp[name]["any_failure"]) for name in gcheck if name in grp
             and name != "GF(4)-linear") and gf_fail == 0 and not grp["GF(4)-linear"]["any_failure"]
    flags = {"P1": p1, "P2": p2, "P3": p3, "P4": p4}
    if flags != result["predictions"]:
        problems.append(f"prediction flags differ: {flags} vs {result['predictions']}")
    report["predictions_recomputed"] = flags
    status = "passed: recomputation agrees (V1, exploratory evidence only)" if not problems else "failed"
    text = json.dumps(report, indent=2, sort_keys=True) + "\n" + status + "\n" + "\n".join(problems) + "\n"
    (ART / "check_output.txt").write_text(text)
    print(text)
    return 0 if not problems else 1


if __name__ == "__main__":
    sys.exit(main())
