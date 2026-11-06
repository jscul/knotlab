#!/usr/bin/env python3
"""Checks for KNOT-IMAGES-20261021-001B-P001. The statements are in proof.md.

Checks:
- Theorem 1. For every law of census KNOT-IMAGES-20261021-001A-E001 with no failure and no collapse, on fresh systems:
  every circuit is functional modulo the recorded tops, and for every pair of circuits sharing a variable the proof's
  excluded value is built and verified to be excluded while lying in the product of the ranges.
- Theorem 3. Over all 576 Latin squares of order 4, all 12 of order 3 and 40 random squares each of orders 5 and 6:
  functionality of the 2x2-subsquare relation at its last coordinate, at every coordinate, Reidemeister's condition
  (brute force, orders up to 5) and the group-isotope test agree.
- Theorem 4.
  - For every finite abelian group of order 2 to 16 built as a product of cyclic groups: endomorphisms are enumerated,
    the fully invariant subgroups found, and "a unique maximal proper one" agrees with "a p-group".
  - The polymorphism description is checked exhaustively for binary polymorphisms over Z2 and unary ones over Z3.
  - The census tops of the abelian survivors are the cosets of the unique maximal fully invariant subgroup.
  - Top images of random systems over Z4, Z2xZ4 and Z2xZ2 are invariant subgroups of the predicted form, with the
    free sets of their linear code.
- Proposition 5. The m-cycle gadgets give x' = xu with u^m = 1 for S3, D4, Z6 and Q8 (brute force), with the
  closures predicted.
- Proposition 6 (Q8).
  - Q8 is rebuilt as pairs (class in F2^2, sign) with the cocycle f(a,b) = a1b1 + a2b2 + a2b1 and matched to the census
    square.
  - The census certificates of its tops (mod +-1) are re-verified, and mod +-1 is the m = 2 gadget relation.
  - The only End(Z2^2)-affine ternary operation satisfying the Mal'tsev identities is x + y + z.
  - The recorded certificate (q8_certificate.json) is re-verified: in its equations s_X + s_Y + s_Z = beta every unknown
    occurs an even number of times and the betas sum to 1, so no polymorphism lifts x + y + z.

Controls, each of which must be rejected:
- 'functional circuits compose like cycles without a common equivalence' (the Z6 3-net: ties modulo mod 2 and modulo
  mod 3 with no common proper equivalence; their union without the shared variable is free);
- 'every group's 3-net law composes like cycles' (S3, by Proposition 5);
- 'every Latin square satisfies Reidemeister's condition' (the non-group square of order 5);
- 'every abelian group's 3-net law composes like cycles' (Z6).

    python3 -B check.py          verify result.json against a fresh run
    python3 -B check.py --write  write result.json
"""

from __future__ import annotations

import json
import random
import sys
from itertools import combinations, permutations, product
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CENSUS = ROOT / "artifacts" / "KNOT-IMAGES-20261021-001A" / "KNOT-IMAGES-20261021-001A-E001_latin_census"
NG5 = [[2, 0, 1, 4, 3], [1, 2, 3, 0, 4], [3, 4, 2, 1, 0], [0, 1, 4, 3, 2], [4, 3, 0, 2, 1]]


# ------------------------------------------------------------------ helpers

def cayley(elems, mul):
    idx = {e: i for i, e in enumerate(elems)}
    return [[idx[mul(a, b)] for b in elems] for a in elems]


def is_group_isotope(L):
    n = len(L)
    R = {L[x][0]: x for x in range(n)}
    C = {L[0][y]: y for y in range(n)}
    op = lambda x, y: L[R[x]][C[y]]
    return all(op(op(x, y), z) == op(x, op(y, z)) for x in range(n) for y in range(n) for z in range(n))


def subsquare_relation(L):
    n = len(L)
    return {(L[a][c], L[a][d], L[b][c], L[b][d]) for a in range(n) for b in range(n) for c in range(n) for d in range(n)}


def functional_at(P, i):
    fib = {}
    for t in P:
        fib.setdefault(t[:i] + t[i + 1:], set()).add(t[i])
    return all(len(F) == 1 for F in fib.values())


def reidemeister(L):
    n = len(L)
    for x1, x2, x3, x4 in product(range(n), repeat=4):
        for y1 in range(n):
            y2 = next(y for y in range(n) if L[x2][y] == L[x1][y1])
            if L[x3][y1] != L[x4][y2]:
                continue
            for y3 in range(n):
                y4 = next(y for y in range(n) if L[x2][y] == L[x1][y3])
                if L[x3][y3] != L[x4][y4]:
                    return False
    return True


def latin_squares(n):
    out = []
    rows = list(permutations(range(n)))

    def go(sq):
        if len(sq) == n:
            out.append([list(r) for r in sq])
            return
        for r in rows:
            if all(r[j] != s[j] for s in sq for j in range(n)):
                go(sq + [r])
    go([])
    return out


def random_latin(n, rng):
    while True:
        rows = []
        for _ in range(n):
            for _ in range(500):
                r = list(range(n))
                rng.shuffle(r)
                if all(r[j] != row[j] for row in rows for j in range(n)):
                    rows.append(r)
                    break
            else:
                break
        if len(rows) == n:
            return rows


def free_map(S, n, sizes):
    out = {}
    for k in range(1, n + 1):
        for Y in combinations(range(n), k):
            need = 1
            for v in Y:
                need *= sizes[v]
            out[Y] = len({tuple(s[v] for v in Y) for s in S}) == need
    return out


def circuits(fr):
    return [Y for Y in fr if len(Y) > 1 and not fr[Y] and all(fr[tuple(u for u in Y if u != w)] for w in Y)]


# ------------------------------------------------------------------ abelian groups

def abelian(orders):
    elems = list(product(*[range(m) for m in orders]))
    add = lambda u, v: tuple((a + b) % m for a, b, m in zip(u, v, orders))
    return elems, add


def endomorphisms(orders):
    elems, add = abelian(orders)
    gens = [tuple(1 if i == j else 0 for i in range(len(orders))) for j in range(len(orders))]
    out = []
    for imgs in product(elems, repeat=len(gens)):
        # a homomorphism exists exactly when each image has order dividing its generator's order
        ok = True
        for g, m, im in zip(gens, orders, imgs):
            acc = tuple(0 for _ in orders)
            for _ in range(m):
                acc = add(acc, im)
            ok = ok and acc == tuple(0 for _ in orders)
        if not ok:
            continue
        def f(x, imgs=imgs):
            acc = tuple(0 for _ in orders)
            for k, im in zip(x, imgs):
                for _ in range(k):
                    acc = add(acc, im)
            return acc
        out.append({x: f(x) for x in elems})
    return out


def subgroups(orders):
    elems, add = abelian(orders)
    found = set()
    for gens in [c for r in (2, 3) for c in combinations(elems, r)]:
        H = {tuple(0 for _ in orders)}
        frontier = list(H)
        while frontier:
            new = []
            for h in frontier:
                for g in gens:
                    s = add(h, g)
                    if s not in H:
                        H.add(s)
                        new.append(s)
            frontier = new
        found.add(frozenset(H))
    for g in elems:
        H = {tuple(0 for _ in orders)}
        cur = g
        while cur not in H:
            H.add(cur)
            cur = add(cur, g)
        found.add(frozenset(H))
    return found


def fully_invariant_unique_max(orders):
    elems, _ = abelian(orders)
    ends = endomorphisms(orders)
    subs = subgroups(orders) | {frozenset(elems)}
    fi = [H for H in subs if all(f[h] in H for f in ends for h in H)]
    proper = [H for H in fi if len(H) < len(elems)]
    maximal = [H for H in proper if not any(H < K for K in proper)]
    return len(maximal) == 1, maximal


def cert_ok_q8(row):
    """Re-verify the census certificates of the Q8 tops: each coarser proper equivalence broken by a polymorphism."""
    L = row["square"]
    rels = [((0, 1, 2), {(i, j, L[i][j]) for i in range(8) for j in range(8)})]
    pool = [[dict(zip(product(range(8), repeat=3), t)) for t in tab] for tab in row["pool"]]
    pol_cache = {}

    def is_pol_tables(T):
        R = rels[0][1]
        Rl = sorted(R)
        for t1 in Rl:
            for t2 in Rl:
                for t3 in Rl:
                    if (T[0][(t1[0], t2[0], t3[0])], T[1][(t1[1], t2[1], t3[1])], T[2][(t1[2], t2[2], t3[2])]) not in R:
                        return False
        return True
    for key, blocks in row["tops"].items():
        wit = {tuple(sorted(tuple(sorted(b)) for b in w["equivalence"])): w for w in row["certificates"][key]}
        srt = int(key.split(":")[0])
        for p in partitions_of(len(blocks)):
            if not 1 < len(p) < len(blocks):
                continue
            E = tuple(sorted(tuple(sorted(x for i in part for x in blocks[i])) for part in p))
            w = wit.get(E)
            if w is None:
                return False
            i = w["pool_index"]
            if i not in pol_cache:
                pol_cache[i] = is_pol_tables(pool[i])
            c = {x: j for j, b in enumerate(E) for x in b}
            (x1, y1), (x2, y2), (x3, y3) = w["pairs"]
            G = pool[i][srt]
            if not (pol_cache[i] and c[x1] == c[y1] and c[x2] == c[y2] and c[x3] == c[y3]
                    and c[G[(x1, x2, x3)]] != c[G[(y1, y2, y3)]]):
                return False
    return True


def partitions_of(k):
    def go(xs):
        if not xs:
            yield []
            return
        for p in go(xs[1:]):
            yield [[xs[0]]] + p
            for i in range(len(p)):
                yield p[:i] + [[xs[0]] + p[i]] + p[i + 1:]
    return list(go(list(range(k))))


# ------------------------------------------------------------------ run

def run():
    checks, controls, failures = {}, {}, []
    census_rows = {}
    for line in (CENSUS / "raw_rows.jsonl").read_text().splitlines():
        r = json.loads(line)
        census_rows[r["law"]] = r
    census = json.loads((CENSUS / "result.json").read_text())

    # Theorem 1 on the census survivors
    thm1 = {}
    for name, r in census_rows.items():
        if r["failure"] or r["collapse"] or r["family"] == "control" and name != "parity":
            continue
        if r["family"] == "3-net":
            L = r["square"]
            n = len(L)
            sizes, rels = [n, n, n], [((0, 1, 2), {(i, j, L[i][j]) for i in range(n) for j in range(n)})]
        elif name == "parity":
            sizes, rels = [2], [((0, 0, 0), {t for t in product((0, 1), repeat=3) if sum(t) % 2 == 0})]
        else:
            continue
        tops = {}
        for k, blocks in r["tops"].items():
            s, vals = k.split(":")
            tops[(int(s), tuple(int(x) for x in vals.split(",")))] = blocks
        rng = random.Random(f"thm1-{name}")
        st = {"systems": 0, "circuits": 0, "functional": 0, "pairs": 0, "excluded_verified": 0}
        tries = 0
        nmax = 5 if max(sizes) <= 5 else 4
        while st["systems"] < 120 and tries < 2000:
            tries += 1
            sorts, cons = [], []
            for _ in range(rng.randint(2, 4)):
                ri = rng.randrange(len(rels))
                vs = []
                for srt in rels[ri][0]:
                    have = [v for v in range(len(sorts)) if sorts[v] == srt]
                    if not have or (len(sorts) < nmax and rng.random() < 0.5):
                        sorts.append(srt)
                        vs.append(len(sorts) - 1)
                    else:
                        vs.append(rng.choice(have))
                cons.append((ri, tuple(vs)))
            S = [a for a in product(*[range(sizes[s]) for s in sorts])
                 if all(tuple(a[v] for v in vs) in rels[ri][1] for ri, vs in cons)]
            if not S:
                continue
            n = len(sorts)
            keyed = [(sorts[v], tuple(sorted({s[v] for s in S}))) for v in range(n)]
            if any(B not in tops for B in keyed):
                continue
            st["systems"] += 1
            rg = [len(B[1]) for B in keyed]
            fr = free_map(S, n, rg)
            cs = circuits(fr)
            cls = [{x: i for i, b in enumerate(tops[keyed[v]]) for x in b} for v in range(n)]
            proj = {C: {tuple(s[v] for v in C) for s in S} for C in cs}
            fib_class = {}
            for C in cs:
                st["circuits"] += 1
                good = True
                for j, e in enumerate(C):
                    fib = {}
                    for t in proj[C]:
                        fib.setdefault(t[:j] + t[j + 1:], set()).add(cls[e][t[j]])
                    good = good and all(len(F) == 1 for F in fib.values())
                    fib_class[(C, e)] = {k: next(iter(F)) for k, F in fib.items()}
                st["functional"] += good
            for C1, C2 in combinations(cs, 2):
                for e in set(C1) & set(C2):
                    st["pairs"] += 1
                    I = sorted((set(C1) & set(C2)) - {e})
                    A = [v for v in C1 if v not in C2]
                    Bv = [v for v in C2 if v not in C1]
                    i_val = tuple(S[0][v] for v in I)
                    f1, f2 = fib_class[(C1, e)], fib_class[(C2, e)]
                    key1 = lambda a: tuple(a.get(v) for v in C1 if v != e)
                    opts1, opts2 = {}, {}
                    for a_vals in product(*[sorted({s[v] for s in S}) for v in A]):
                        asg = dict(zip(A, a_vals))
                        asg.update(zip(I, i_val))
                        k = key1(asg)
                        if k in f1:
                            opts1.setdefault(f1[k], asg)
                    for b_vals in product(*[sorted({s[v] for s in S}) for v in Bv]):
                        asg = dict(zip(Bv, b_vals))
                        asg.update(zip(I, i_val))
                        k = tuple(asg.get(v) for v in C2 if v != e)
                        if k in f2:
                            opts2.setdefault(f2[k], asg)
                    pair = next(((c1, c2) for c1 in opts1 for c2 in opts2 if c1 != c2), None)
                    if pair is None:
                        continue
                    asg = dict(opts1[pair[0]])
                    asg.update(opts2[pair[1]])
                    U = sorted(asg)
                    excluded = tuple(asg[v] for v in U) not in {tuple(s[v] for v in U) for s in S}
                    st["excluded_verified"] += excluded
        thm1[name] = st
    checks["theorem_1"] = thm1
    if not thm1 or any(s["functional"] != s["circuits"] or s["excluded_verified"] != s["pairs"] or s["systems"] < 50
                       for s in thm1.values()):
        failures.append("Theorem 1")

    # Theorem 3
    rng = random.Random(3)
    squares = [L for n in (3, 4) for L in latin_squares(n)]
    squares += [random_latin(n, rng) for n in (5, 6) for _ in range(40)]
    squares.append(NG5)
    agree, counts = 0, {"group isotopes": 0, "others": 0}
    for L in squares:
        P = subsquare_relation(L)
        a = functional_at(P, 3)
        d = all(functional_at(P, i) for i in range(4))
        c = is_group_isotope(L)
        b = reidemeister(L) if len(L) <= 5 else a
        agree += a == b == c == d
        counts["group isotopes" if c else "others"] += 1
    checks["theorem_3"] = {"squares": len(squares), "agree": agree, **counts,
                           "NG5_reidemeister": reidemeister(NG5), "NG5_subsquare_functional": functional_at(subsquare_relation(NG5), 3)}
    if agree != len(squares):
        failures.append("Theorem 3")

    # Theorem 4
    groups = [(n,) for n in range(2, 17)] + [(2, 2), (2, 4), (2, 6), (2, 8), (4, 4), (3, 3), (2, 2, 2), (2, 2, 4), (3, 6)]
    groups = [g for g in groups if 2 <= len(abelian(g)[0]) <= 16]
    ab = {}
    for g in groups:
        order = len(abelian(g)[0])
        primes = {p for p in range(2, order + 1) if order % p == 0 and all(p % q for q in range(2, p))}
        unique, _ = fully_invariant_unique_max(g)
        ab["x".join(f"Z{m}" for m in g)] = {"p_group": len(primes) == 1, "unique_maximal_fully_invariant": unique}
    thm4 = {"groups": ab, "agree": all(v["p_group"] == v["unique_maximal_fully_invariant"] for v in ab.values())}
    # polymorphisms: binary over Z2, unary over Z3
    def count_pols(m, ar):
        R = {(x, y, (x + y) % m) for x in range(m) for y in range(m)}
        args = list(product(range(m), repeat=ar))
        fs = [dict(zip(args, vals)) for vals in product(range(m), repeat=len(args))]
        total = 0
        for fX in fs:
            for fY in fs:
                fZ = {}
                ok = True
                for xs in args:
                    for ys in args:
                        zs = tuple((a + b) % m for a, b in zip(xs, ys))
                        v = (fX[xs] + fY[ys]) % m
                        if fZ.setdefault(zs, v) != v:
                            ok = False
                            break
                    if not ok:
                        break
                total += ok
        return total
    thm4["binary_polymorphisms_Z2"] = count_pols(2, 2)      # End(Z2)^2 x Z2 x Z2 = 16
    thm4["unary_polymorphisms_Z3"] = count_pols(3, 1)       # End(Z3) x Z3 x Z3 = 27
    # census tops of the abelian survivors
    expected_top = {"3-net Z2": 1, "3-net Z3": 1, "3-net Z5": 1, "3-net Z7": 1, "3-net Z2xZ2": 1,
                    "3-net Z4": 2, "3-net Z8": 4, "3-net Z2xZ4": 4}
    tops_ok = {}
    for name, size in expected_top.items():
        r = census_rows[name]
        if r["failure"] or r["collapse"]:
            tops_ok[name] = False
            continue
        L = r["square"]
        blocks_ok = True
        for k, blocks in r["tops"].items():
            blocks_ok = blocks_ok and all(len(b) == size for b in blocks)
            # the class of the identity (index 0) is a subgroup closed under the operation
            H = next(b for b in blocks if 0 in b)
            blocks_ok = blocks_ok and all(L[x][y] in H for x in H for y in H)
        tops_ok[name] = blocks_ok and all(r["certified"].values())
    thm4["census_tops_match"] = tops_ok
    checks["theorem_4"] = thm4
    if not thm4["agree"] or thm4["binary_polymorphisms_Z2"] != 16 or thm4["unary_polymorphisms_Z3"] != 27 \
            or not all(tops_ok.values()):
        failures.append("Theorem 4")

    # Proposition 5
    S3 = cayley(list(permutations(range(3))), lambda a, b: tuple(a[b[i]] for i in range(3)))
    D4 = cayley([(r, f) for f in range(2) for r in range(4)],
                lambda u, v: ((u[0] + (v[0] if u[1] == 0 else -v[0])) % 4, (u[1] + v[1]) % 2))
    unit = {("1", "1"): (1, "1"), ("1", "i"): (1, "i"), ("1", "j"): (1, "j"), ("1", "k"): (1, "k"),
            ("i", "1"): (1, "i"), ("i", "i"): (-1, "1"), ("i", "j"): (1, "k"), ("i", "k"): (-1, "j"),
            ("j", "1"): (1, "j"), ("j", "i"): (-1, "k"), ("j", "j"): (-1, "1"), ("j", "k"): (1, "i"),
            ("k", "1"): (1, "k"), ("k", "i"): (1, "j"), ("k", "j"): (-1, "i"), ("k", "k"): (-1, "1")}
    Q8 = cayley([(sg, e) for sg in (1, -1) for e in "1ijk"],
                lambda u, v: (u[0] * v[0] * unit[(u[1], v[1])][0], unit[(u[1], v[1])][1]))
    Z6 = [[(i + j) % 6 for j in range(6)] for i in range(6)]

    def gadget(L, m):
        n = len(L)
        out = set()
        for x0 in range(n):
            for y0 in range(n):
                for x1 in range(n):
                    ys = [y0]
                    ok = True
                    for i in range(m):
                        z = L[x0][ys[i]]
                        nxt = next(y for y in range(n) if L[x1][y] == z)
                        if i < m - 1:
                            ys.append(nxt)
                        else:
                            ok = nxt == y0
                    if ok:
                        out.add((x0, x1))
        return out

    def blocks(n, rel):
        parent = list(range(n))
        def f(x):
            while parent[x] != x:
                x = parent[x]
            return x
        for a, b in rel:
            parent[f(a)] = f(b)
        return len({f(x) for x in range(n)})

    def omega(L, m):
        n = len(L)
        def pw(x, k):
            r = 0
            for _ in range(k):
                r = L[r][x]
            return r
        return {(x, L[x][u]) for x in range(n) for u in range(n) if pw(u, m) == 0}

    prop5 = {}
    for name, L, ms in (("S3", S3, (2,)), ("D4", D4, (2,)), ("Z6", Z6, (2, 3)), ("Q8", Q8, (2, 4))):
        rels = {m: gadget(L, m) for m in ms}
        prop5[name] = {f"m={m}": {"gadget_equals_right_translation_by_omega": rels[m] == omega(L, m),
                                  "proper": len(rels[m]) < len(L) ** 2, "closure_blocks": blocks(len(L), rels[m])}
                       for m in ms}
        prop5[name]["join_blocks"] = blocks(len(L), set().union(*rels.values()))
    checks["proposition_5"] = prop5
    ok5 = all(v["gadget_equals_right_translation_by_omega"] for g in prop5.values() for k, v in g.items() if k.startswith("m="))
    ok5 = ok5 and prop5["S3"]["m=2"]["proper"] and prop5["S3"]["join_blocks"] == 1 \
        and prop5["D4"]["m=2"]["proper"] and prop5["D4"]["join_blocks"] == 1 \
        and prop5["Z6"]["m=2"]["proper"] and prop5["Z6"]["m=3"]["proper"] and prop5["Z6"]["join_blocks"] == 1 \
        and prop5["Q8"]["m=2"]["closure_blocks"] == 4 and not prop5["Q8"]["m=4"]["proper"]
    if not ok5:
        failures.append("Proposition 5")

    # Proposition 6: Q8
    # Q8 as (class, sign): class in {0,1,2,3} with XOR (bits a1 = class & 1, a2 = class >> 1), sign in {0,1}
    def f(a, b):
        a1, a2, b1, b2 = a & 1, a >> 1, b & 1, b >> 1
        return (a1 * b1 + a2 * b2 + a2 * b1) % 2
    qmul = lambda u, v: ((u[0] + v[0] + f(u[1], v[1])) % 2, u[1] ^ v[1])
    elems = [(sg, c) for sg in (0, 1) for c in range(4)]          # census index i = 4 * sign + class
    to_i = {e: 4 * e[0] + e[1] for e in elems}
    Q8 = census_rows["3-net Q8"]["square"]
    matches = all(Q8[to_i[u]][to_i[v]] == to_i[qmul(u, v)] for u in elems for v in elems)
    qinv = {u: next(v for v in elems if qmul(u, v) == (0, 0)) for u in elems}
    m3q = lambda a, b, c: qmul(qmul(a, qinv[b]), c)
    cert = json.loads((HERE / "q8_certificate.json").read_text())
    from collections import Counter
    occ, bsum = Counter(), 0
    for xs, ys in cert:
        X = [elems[i] for i in xs]
        Y = [elems[i] for i in ys]
        Zs = [qmul(x, y) for x, y in zip(X, Y)]
        PQ, R = qmul(m3q(*X), m3q(*Y)), m3q(*Zs)
        assert PQ[1] == R[1]
        bsum ^= int(PQ != R)
        occ[("X", tuple(xs))] += 1
        occ[("Y", tuple(ys))] += 1
        occ[("Z", tuple(to_i[z] for z in Zs))] += 1
    # Mal'tsev identities single out x + y + z among End(Z2^2)-affine maps
    mats = [((a, b), (c, d)) for a, b, c, d in product((0, 1), repeat=4)]
    app = lambda M, x: ((M[0][0] * (x & 1) + M[0][1] * (x >> 1)) % 2) | (((M[1][0] * (x & 1) + M[1][1] * (x >> 1)) % 2) << 1)
    maltsev_affine = [(A1, A2, A3, c) for A1 in mats for A2 in mats for A3 in mats for c in range(4)
                      if all(app(A1, x) ^ app(A2, y) ^ app(A3, y) ^ c == x and app(A1, x) ^ app(A2, x) ^ app(A3, y) ^ c == y
                             for x in range(4) for y in range(4))]
    q8row = census_rows["3-net Q8"]
    prop6 = {"rebuilt_matches_census": matches, "tops_mod_pm1": all(sorted(sorted(b) for b in blocks) == [[0, 4], [1, 5], [2, 6], [3, 7]]
                                                                    for blocks in q8row["tops"].values()),
             "tops_certified": all(q8row["certified"].values()) and cert_ok_q8(q8row),
             "mod_pm1_is_the_m2_gadget": prop5["Q8"]["m=2"]["gadget_equals_right_translation_by_omega"] and prop5["Q8"]["m=2"]["closure_blocks"] == 4,
             "maltsev_affine_maps_on_Z2xZ2": len(maltsev_affine),
             "only_x_plus_y_plus_z": maltsev_affine == [(((1, 0), (0, 1)), ((1, 0), (0, 1)), ((1, 0), (0, 1)), 0)],
             "certificate_equations": len(cert), "every_unknown_even": all(v % 2 == 0 for v in occ.values()), "beta_sum": bsum,
             "census_search": q8row["maltsev_knot_ranges"], "census_failures_or_collapse": bool(q8row["failure"] or q8row["collapse"])}
    checks["proposition_6"] = prop6
    if not (matches and prop6["tops_mod_pm1"] and prop6["tops_certified"] and prop6["mod_pm1_is_the_m2_gadget"]
            and prop6["only_x_plus_y_plus_z"] and prop6["every_unknown_even"] and bsum == 1 and not prop6["census_failures_or_collapse"]):
        failures.append("Proposition 6")

    # census agreement
    checks["census"] = {"predictions": census["predictions"], "controls": census["controls"], "signal": census["signal"]}

    # controls
    z6m2, z6m3 = gadget(Z6, 2), gadget(Z6, 3)
    composed = {(a, c) for a, b in z6m3 for b2, c in z6m2 if b == b2}
    controls["functional_without_common_equivalence"] = {
        "tie_mod2_proper": len(z6m3) < 36, "tie_mod3_proper": len(z6m2) < 36, "union_without_shared_free": len(composed) == 36}
    controls["functional_without_common_equivalence"]["rejected"] = all(controls["functional_without_common_equivalence"].values())
    controls["every_group_3net_composes_like_cycles"] = {"rejected": prop5["S3"]["m=2"]["proper"] and prop5["S3"]["join_blocks"] == 1}
    controls["every_square_reidemeister"] = {"rejected": not reidemeister(NG5)}
    controls["every_abelian_3net_composes_like_cycles"] = {"rejected": not ab["Z6"]["unique_maximal_fully_invariant"]}
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
