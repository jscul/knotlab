#!/usr/bin/env python3
"""Checks for LOOP-HOMOLOGY-20261021-001A-P001. The statements are in proof.md.

A link is a knot with two of its variables chosen as witnesses (in and out); the others are its middle distinctions.
For each value of the middle distinctions the link has a transfer, the relation it allows between the witnesses. A
ring of k copies passes each copy's out-witness to the next copy's in-witness and forgets the witnesses.

Checks:
- Theorem 1 (dichotomy). For every link of every knot below, exactly one of these holds: some product of transfers is
  the full relation, or the transfers permute the blocks of a partition into two or more blocks. With a full product
  of length l, the share of patterns a ring of k = max(8, 2l) copies excludes is at most (1 - |M|^-l)^floor(k/l);
  with blocks, some ring length from 9 to 16 (to 12 for Boolean links) excludes a positive share.
  Knots: every Boolean knot on three and four variables (all witness placements); group 3-nets, twisted affine knots,
  dressed knots and random knots on three to six values (all placements with equal witness ranges).
- Corollary 2 (two values). For Boolean links, group-like, no full product, a block system, an affine law and parity
  coincide.
- Theorem 3 (networks). For knots of laws composing like cycles (parity, x - z + y and x + y + z over F3, z = 2x + y
  over F5, the 3-net of Z2 x Z2, z = wx + y over GF(4), the 3-net of Z4 and a dressed parity knot) and eight graphs, the
  top image of a network's visible relation has index |A|^(E-V) |H0| (twisted first cohomology), and its free sets of
  edges are those of the frame matroid of the gain graph (trees and unicyclic components with gain other than 1), and
  of the linear criterion. The 3-nets of Z6 and S3 remember |G|^b1 classes with graphic free sets.
- Theorem 4 (the claim as stated). Failing systems for the 3-nets of Z6 (ties modulo 2 and 3) and S3 (Thomsen's
  configuration, doubled); the selector law of the holes-cohomology epic (three loops bound as not-all-three, and a
  doubled failing system); random systems of the dressed parity law and of three twisted affine laws, which satisfy
  elimination, the dressed one with the free sets of its parity projection.

Controls, each of which must be rejected:
- 'every group-like knot composes like cycles' (Z6 and S3);
- 'a knot whose law composes like cycles has permutation transfers' (dressed parity);
- 'a group-like knot whose law composes like cycles remembers a loop at every length' (x + y + z over F3);
- 'networks alone tell cycle-like composition apart' (Z6 and S3 networks are graphic with |G|^b1 classes);
- 'binding loops through fixed points keeps cycle-like composition' (the selector law);
- 'in a law composing like cycles no two loops bind' (two triangles over F3 form one circuit).

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


# ------------------------------------------------------------------ transfers and rings

def link(R, wi, wo):
    """The transfers of the link of R with in-witness wi and out-witness wo, as n x n bit masks."""
    ar = len(next(iter(R)))
    mids = [c for c in range(ar) if c not in (wi, wo)]
    W = sorted({t[wi] for t in R})
    if W != sorted({t[wo] for t in R}):
        return None
    idx = {w: a for a, w in enumerate(W)}
    n = len(W)
    T = {}
    for t in R:
        m = tuple(t[c] for c in mids)
        T[m] = T.get(m, 0) | (1 << (idx[t[wi]] * n + idx[t[wo]]))
    return n, T


def compose(P, Q, n):
    row_mask = (1 << n) - 1
    out = 0
    for a in range(n):
        row = (P >> (a * n)) & row_mask
        acc, b = 0, 0
        while row:
            if row & 1:
                acc |= (Q >> (b * n)) & row_mask
            row >>= 1
            b += 1
        out |= acc << (a * n)
    return out


def has_fixed(P, n):
    return any((P >> (a * n + a)) & 1 for a in range(n))


def is_permutation(P, n):
    rows = [(P >> (a * n)) & ((1 << n) - 1) for a in range(n)]
    return all(bin(r).count("1") == 1 for r in rows) and len(set(rows)) == n


def shortest_full_product(T, n):
    """Length of a shortest product of transfers that is the full relation, or None if there is none."""
    full = (1 << (n * n)) - 1
    depth = {}
    queue = []
    for P in T.values():
        if P not in depth:
            depth[P] = 1
            queue.append(P)
    if full in depth:
        return 1
    i = 0
    while i < len(queue):
        P = queue[i]
        i += 1
        for Q in T.values():
            R = compose(P, Q, n)
            if R not in depth:
                depth[R] = depth[P] + 1
                if R == full:
                    return depth[R]
                queue.append(R)
    return None


def set_partitions(items):
    if not items:
        yield []
        return
    first, rest = items[0], items[1:]
    for p in set_partitions(rest):
        for i in range(len(p)):
            yield p[:i] + [[first] + p[i]] + p[i + 1:]
        yield [[first]] + p


def block_systems(T, n):
    out = []
    for p in set_partitions(list(range(n))):
        if len(p) < 2:
            continue
        blk = {a: bi for bi, B in enumerate(p) for a in B}
        if all(len({blk[c] for a in B for c in range(n) if (P >> (a * n + c)) & 1}) == 1
               for P in T.values() for B in p):
            out.append(p)
    return out


def ring_excluded(T, n, kmax):
    """Share of middle patterns that a ring of k copies excludes, k = 1..kmax."""
    ident = sum(1 << (a * n + a) for a in range(n))
    full = (1 << (n * n)) - 1
    dist, out, M = {ident: 1}, [], len(T)
    for k in range(1, kmax + 1):
        nd = {}
        for P, c in dist.items():
            if P == full:   # a full product stays full
                nd[full] = nd.get(full, 0) + c * M
                continue
            for Q in T.values():
                R = compose(P, Q, n)
                nd[R] = nd.get(R, 0) + c
        dist = nd
        allowed = sum(c for P, c in dist.items() if has_fixed(P, n))
        out.append(1 - allowed / M ** k)
    return out


def is_knot(R):
    ar = len(next(iter(R)))
    rg = [len({t[i] for t in R}) for i in range(ar)]
    if len(R) == math.prod(rg) or min(rg) < 2:
        return False
    for drop in range(ar):
        keep = [i for i in range(ar) if i != drop]
        if len({tuple(t[i] for i in keep) for t in R}) != math.prod(rg[i] for i in keep):
            return False
    return True


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


def elimination_failures(fr):
    cs = [Y for Y in fr if len(Y) > 1 and not fr[Y] and all(fr[tuple(u for u in Y if u != w)] for w in Y)]
    out = []
    for C1, C2 in combinations(cs, 2):
        for y in sorted(set(C1) & set(C2)):
            if fr[tuple(sorted((set(C1) | set(C2)) - {y}))]:
                out.append((C1, C2, y))
    return cs, out


def random_system(rng, rels, nmax):
    n, cons = 0, []
    for _ in range(rng.randint(1, 4)):
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


# ------------------------------------------------------------------ knots

def rel(D, f):
    return frozenset(t for t in product(range(D), repeat=3) if f(*t))


S3 = list(permutations(range(3)))
S3_INDEX = {g: i for i, g in enumerate(S3)}
GF4_W = [0, 2, 3, 1]   # multiplication by a generator w of GF(4)* on 0, 1, w = 2, w^2 = 3; addition is XOR

KNOTS = {
    "parity": rel(2, lambda a, m, c: (a + m + c) % 2 == 0),
    "not-all-equal": rel(2, lambda a, m, c: len({a, m, c}) > 1),
    "F3, c = a + m": rel(3, lambda a, m, c: c == (a + m) % 3),
    "F3, a + m + c = 0": rel(3, lambda a, m, c: (a + m + c) % 3 == 0),
    "F5, c = 2a + m": rel(5, lambda a, m, c: c == (2 * a + m) % 5),
    "Z5 3-net": rel(5, lambda a, m, c: c == (a + m) % 5),
    "Z4 3-net": rel(4, lambda a, m, c: c == (a + m) % 4),
    "Z2xZ2 3-net": rel(4, lambda a, m, c: c == a ^ m),
    "GF4, c = wa + m": rel(4, lambda a, m, c: c == GF4_W[a] ^ m),
    "Z6 3-net": rel(6, lambda a, m, c: c == (a + m) % 6),
    "S3 3-net": frozenset((i, j, S3_INDEX[tuple(S3[i][S3[j][x]] for x in range(3))]) for i in range(6) for j in range(6)),
    "dressed parity": rel(4, lambda x, y, z: (x // 2 + y // 2 + z // 2) % 2 == 0),
    "dressed Z3": rel(6, lambda x, y, z: (x // 2 + y // 2 + z // 2) % 3 == 0),
}


def random_knot(rng, D, density):
    while True:
        R = frozenset(t for t in product(range(D), repeat=3) if rng.random() < density)
        if R and is_knot(R) and all(len({t[i] for t in R}) == D for i in range(3)):
            return R


def random_block_knot(rng, D, size):
    """A random knot whose transfers (in = 0, out = 2) map blocks of the given size onto blocks."""
    blocks = [list(range(i, i + size)) for i in range(0, D, size)]
    r = len(blocks)
    while True:
        R = set()
        for m in range(D):
            shift = rng.randrange(r)
            for bi, B in enumerate(blocks):
                C = blocks[(bi + shift) % r]
                while True:
                    pairs = {(a, c) for a in B for c in C if rng.random() < 0.6}
                    if {a for a, _ in pairs} == set(B) and {c for _, c in pairs} == set(C):
                        break
                R |= {(a, m, c) for a, c in pairs}
        R = frozenset(R)
        if is_knot(R) and all(len({t[i] for t in R}) == D for i in range(3)):
            return R


def boolean_knots(ar):
    pts = list(product((0, 1), repeat=ar))
    for mask in range(1, 1 << len(pts)):
        R = frozenset(pts[i] for i in range(len(pts)) if mask >> i & 1)
        if is_knot(R):
            yield R


def affine_boolean(R):
    return all(tuple(a ^ b ^ c for a, b, c in zip(x, y, z)) in R for x in R for y in R for z in R)


# ------------------------------------------------------------------ networks

GRAPHS = {
    "C3": (3, [(0, 1), (1, 2), (2, 0)]),
    "C4": (4, [(0, 1), (1, 2), (2, 3), (3, 0)]),
    "C5": (5, [(0, 1), (1, 2), (2, 3), (3, 4), (4, 0)]),
    "C4 mixed": (4, [(0, 1), (2, 1), (2, 3), (0, 3)]),
    "K4": (4, [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)]),
    "K23": (5, [(0, 2), (0, 3), (0, 4), (1, 2), (1, 3), (1, 4)]),
    "theta": (4, [(0, 1), (1, 3), (0, 2), (2, 3), (0, 3)]),
    "two triangles": (5, [(0, 1), (1, 2), (2, 0), (2, 3), (3, 4), (4, 2)]),
}

# knots of laws composing like cycles: (elements of the top group A, linear part of the transfer on A, top map)
CLC_KNOTS = {
    "parity": (2, (0, 1), lambda x: x),
    "F3, c = a + m": (3, (0, 1, 2), lambda x: x),
    "F3, a + m + c = 0": (3, (0, 2, 1), lambda x: x),
    "F5, c = 2a + m": (5, (0, 2, 4, 1, 3), lambda x: x),
    "Z2xZ2 3-net": (4, (0, 1, 2, 3), lambda x: x),
    "GF4, c = wa + m": (4, tuple(GF4_W), lambda x: x),
    "Z4 3-net": (2, (0, 1), lambda x: x % 2),
    "dressed parity": (2, (0, 1), lambda x: x // 2),
}


def network_relation(R, V, E):
    """Visible relation of a network: middle values on the edges (u, v), witnesses at the vertices, in = u, out = v."""
    W = sorted({t[0] for t in R})
    fib = {}
    for a, m, c in R:
        fib.setdefault((a, c), []).append(m)
    out = set()
    for f in product(W, repeat=V):
        choices = [fib.get((f[u], f[v]), []) for u, v in E]
        if all(choices):
            out.update(product(*choices))
    return out


def homogeneous(V, E, q, phi):
    """Number of f: V -> A with f(v) = phi(f(u)) on every edge (u, v), by propagation from each component's root."""
    inv = [0] * q
    for a in range(q):
        inv[phi[a]] = a
    adj = {v: [] for v in range(V)}
    for u, v in E:
        adj[u].append((v, phi))
        adj[v].append((u, inv))
    total, seen = 1, set()
    for root in range(V):
        if root in seen:
            continue
        comp = []
        stack = [root]
        seen.add(root)
        while stack:
            x = stack.pop()
            comp.append(x)
            for y, _ in adj[x]:
                if y not in seen:
                    seen.add(y)
                    stack.append(y)
        good = 0
        for a in range(q):
            val, stack, ok = {root: a}, [root], True
            while stack and ok:
                x = stack.pop()
                for y, step in adj[x]:
                    want = step[val[x]]
                    if y not in val:
                        val[y] = want
                        stack.append(y)
                    elif val[y] != want:
                        ok = False
                        break
            good += ok
        total *= good
    return total


def frame_independent(V, edges, q, phi):
    """Frame matroid of the gain graph: every component is a tree or has one cycle, whose gain is not 1."""
    inv = [0] * q
    for a in range(q):
        inv[phi[a]] = a
    parent = list(range(V))

    def find(x):
        while parent[x] != x:
            x = parent[x]
        return x
    for u, v in edges:
        parent[find(u)] = find(v)
    comps = {}
    for e in edges:
        comps.setdefault(find(e[0]), []).append(e)
    for es in comps.values():
        verts = {x for e in es for x in e}
        if len(es) == len(verts) - 1:
            continue
        if len(es) > len(verts):
            return False
        cyc = list(es)
        while True:   # strip leaves to leave the unique cycle
            deg = {}
            for u, v in cyc:
                deg[u] = deg.get(u, 0) + 1
                deg[v] = deg.get(v, 0) + 1
            leaves = {x for x, d in deg.items() if d == 1}
            if not leaves:
                break
            cyc = [e for e in cyc if e[0] not in leaves and e[1] not in leaves]
        gain = list(range(q))
        start = cyc[0][0]
        cur, used = start, set()
        while len(used) < len(cyc):
            i = next(i for i, e in enumerate(cyc) if i not in used and cur in e)
            used.add(i)
            u, v = cyc[i]
            step = phi if u == cur else inv
            gain = [step[g] for g in gain]
            cur = v if u == cur else u
        if gain == list(range(q)):
            return False
    return True


def acyclic(V, edges):
    parent = list(range(V))

    def find(x):
        while parent[x] != x:
            x = parent[x]
        return x
    for u, v in edges:
        a, b = find(u), find(v)
        if a == b:
            return False
        parent[a] = b
    return True


# ------------------------------------------------------------------ run

def dichotomy_entry(T, n, kmax=16):
    """With a full product of length l, ring shares are computed to length max(8, 2l) and checked against the bound
    there; with blocks, to length kmax, and some length from 9 on must exclude a positive share."""
    ell = shortest_full_product(T, n)
    blocks = block_systems(T, n)
    entry = {"full_product_length": ell, "block_systems": len(blocks),
             "group_like": all(is_permutation(P, n) for P in T.values())}
    ok = (ell is None) != (not blocks)
    if ell is not None:
        k = max(8, 2 * ell)
        exc = ring_excluded(T, n, k)
        bound = (1 - len(T) ** -ell) ** (k // ell)
        ok = ok and exc[-1] <= bound + 1e-12
        entry["ring_length_checked"] = k
    else:
        exc = ring_excluded(T, n, kmax)
        ok = ok and max(exc[8:]) > 0
        entry["ring_length_checked"] = kmax
    entry["consistent"] = ok
    return entry, exc


def run():
    checks, controls, failures = {}, {}, []
    rng = random.Random("loop-homology")

    # Corollary 2: Boolean knots, every placement
    boolean = {}
    for ar in (3, 4):
        st = {"knots": 0, "placements": 0, "all_five_agree": 0, "parity_placements": 0, "dichotomy_consistent": 0}
        for R in boolean_knots(ar):
            st["knots"] += 1
            pts = list(product((0, 1), repeat=ar))
            parity = R in ({t for t in pts if sum(t) % 2 == 0}, {t for t in pts if sum(t) % 2 == 1})
            affine = affine_boolean(R)
            for wi, wo in permutations(range(ar), 2):
                n, T = link(R, wi, wo)
                entry, _ = dichotomy_entry(T, n, 12)
                key = (entry["group_like"], entry["full_product_length"] is None, entry["block_systems"] > 0, affine, parity)
                st["placements"] += 1
                st["all_five_agree"] += len(set(key)) == 1
                st["parity_placements"] += parity
                st["dichotomy_consistent"] += entry["consistent"]
        boolean[f"{ar} variables"] = st
    checks["corollary_2_boolean"] = boolean
    if not all(s["all_five_agree"] == s["placements"] == s["dichotomy_consistent"] > 0 for s in boolean.values()):
        failures.append("Corollary 2")

    # Theorem 1: many-valued links
    named = dict(KNOTS)
    for i in range(12):
        named[f"random, 3 values #{i}"] = random_knot(rng, 3, rng.choice((0.5, 0.6, 0.7)))
    for i in range(8):
        named[f"random, 4 values #{i}"] = random_knot(rng, 4, rng.choice((0.4, 0.5, 0.6)))
    for i in range(6):
        named[f"random blocks, 4 values #{i}"] = random_block_knot(rng, 4, 2)
    for i in range(4):
        named[f"random blocks, 6 values #{i}"] = random_block_knot(rng, 6, rng.choice((2, 3)))
    thm1, memory = {}, {}
    for name, R in named.items():
        rows = []
        for wi, wo in permutations(range(3), 2):
            L = link(R, wi, wo)
            if L is None:
                continue
            n, T = L
            entry, exc = dichotomy_entry(T, n)
            entry["placement"] = [wi, wo]
            rows.append(entry)
            if (wi, wo) == (0, 2):
                memory[name] = [round(math.log2(1 / (1 - e)), 4) if e < 1 else None for e in exc[:8]]
        thm1[name] = rows
    summary = {"links": sum(len(r) for r in thm1.values()),
               "full_product": sum(e["full_product_length"] is not None for r in thm1.values() for e in r),
               "block_system": sum(e["block_systems"] > 0 for r in thm1.values() for e in r),
               "block_system_not_group_like": sum(e["block_systems"] > 0 and not e["group_like"]
                                                  for r in thm1.values() for e in r),
               "consistent": sum(e["consistent"] for r in thm1.values() for e in r)}
    checks["theorem_1"] = {"summary": summary, "links": thm1, "ring_bits_k1_to_8": memory}
    if not (summary["consistent"] == summary["links"] > 0 and summary["full_product"] > 0
            and summary["block_system_not_group_like"] > 0):
        failures.append("Theorem 1")

    # Theorem 3: networks of knots from laws composing like cycles, and of the Z6 and S3 3-nets
    thm3 = {}
    for name, (q, phi, top) in CLC_KNOTS.items():
        R = KNOTS[name]
        M = sorted({t[1] for t in R})
        rows = {}
        for gname, (V, E) in GRAPHS.items():
            S = network_relation(R, V, E)
            Stop = {tuple(top(x) for x in s) for s in S}
            Mtop = sorted({top(x) for x in M})
            h0 = homogeneous(V, E, q, phi)
            fr_top = free_map(Stop, len(E))
            fr_full = free_map(S, len(E))
            frame = {Y: frame_independent(V, [E[e] for e in Y], q, phi) for Y in fr_top}
            linear = {Y: homogeneous(V, [E[e] for e in Y], q, phi) == q ** (V - len(Y)) for Y in fr_top}
            rows[gname] = {
                "bits": round(math.log2(len(M) ** len(E) / len(S)), 4),
                "bits_modulo_tops": round(math.log2(len(Mtop) ** len(E) / len(Stop)), 4),
                "twisted_H1_bits": round((len(E) - V) * math.log2(q) + math.log2(h0), 4),
                "frame_matroid": fr_top == frame, "linear_criterion": fr_top == linear,
                "full_free_sets_equal_top": fr_full == fr_top,
            }
        thm3[name] = rows
    for name in ("Z6 3-net", "S3 3-net"):
        R = KNOTS[name]
        rows = {}
        for gname, (V, E) in GRAPHS.items():
            S = network_relation(R, V, E)
            fr = free_map(S, len(E))
            rows[gname] = {"bits": round(math.log2(6 ** len(E) / len(S)), 4),
                           "b1_log2_order": round((len(E) - V + 1) * math.log2(6), 4),
                           "graphic": fr == {Y: acyclic(V, [E[e] for e in Y]) for Y in fr}}
        thm3[name] = rows
    two = network_relation(KNOTS["F3, a + m + c = 0"], 5, GRAPHS["two triangles"][1])
    fr_two = free_map(two, 6)
    thm3["two triangles over F3, x + y + z = 0"] = {
        "each_triangle_free": fr_two[(0, 1, 2)] and fr_two[(3, 4, 5)],
        "six_edges_a_circuit": not fr_two[(0, 1, 2, 3, 4, 5)] and all(fr_two[Y] for Y in combinations(range(6), 5))}
    checks["theorem_3"] = thm3
    clc_ok = all(r["bits_modulo_tops"] == r["twisted_H1_bits"] and r["frame_matroid"] and r["linear_criterion"]
                 for name in CLC_KNOTS for r in thm3[name].values())
    grp_ok = all(r["bits"] == r["b1_log2_order"] and r["graphic"]
                 for name in ("Z6 3-net", "S3 3-net") for r in thm3[name].values())
    z4_extra = all(r["bits"] == 2 * r["bits_modulo_tops"] for r in thm3["Z4 3-net"].values())
    pair_ok = all(thm3["two triangles over F3, x + y + z = 0"].values())
    if not (clc_ok and grp_ok and z4_extra and pair_ok):
        failures.append("Theorem 3")

    # Theorem 4: the claim as stated
    thm4 = {}
    P6 = KNOTS["Z6 3-net"]
    S = solve(6, 8, [(P6, (0, 3, 4)), (P6, (4, 3, 1)), (P6, (1, 5, 6)), (P6, (6, 5, 7)), (P6, (7, 5, 2))])
    cs, fl = elimination_failures(free_map({s[:3] for s in S}, 3))
    thm4["Z6_ties_modulo_2_and_3"] = {"circuits": [list(c) for c in cs], "failures": len(fl)}
    RS3 = KNOTS["S3 3-net"]

    def thomsen(x1, x2, x3, y1, y2, y3, l1, l2, l3):
        return [(RS3, (x1, y2, l1)), (RS3, (x2, y1, l1)), (RS3, (x1, y3, l2)), (RS3, (x3, y1, l2)),
                (RS3, (x2, y3, l3)), (RS3, (x3, y2, l3))]
    S = solve(6, 16, thomsen(0, 1, 2, 4, 5, 6, 7, 8, 9) + thomsen(0, 1, 3, 10, 11, 12, 13, 14, 15))
    cs, fl = elimination_failures(free_map({s[:4] for s in S}, 4))
    thm4["S3_doubled_Thomsen"] = {"circuits": [list(c) for c in cs], "failures": len(fl)}
    transpositions = [{0: 3, 3: 0}, {1: 3, 3: 1}, {2: 3, 3: 2}]
    sel = [frozenset({(w, 0, w) for w in range(4)} | {(w, 1, p.get(w, w)) for w in range(4)}) for p in transpositions]
    tri = sorted({s[:3] for s in solve(4, 4, [(sel[0], (3, 0, 3)), (sel[1], (3, 1, 3)), (sel[2], (3, 2, 3))])})
    S = solve(4, 7, [(sel[0], (5, 0, 5)), (sel[1], (5, 1, 5)), (sel[2], (5, 2, 5)),
                     (sel[0], (6, 3, 6)), (sel[1], (6, 4, 6)), (sel[2], (6, 2, 6))])
    cs, fl = elimination_failures(free_map({s[:5] for s in S}, 5))
    thm4["selector_law"] = {"three_loops": [list(t) for t in tri], "not_all_three": tri == sorted(
        t for t in product((0, 1), repeat=3) if t != (1, 1, 1)), "doubled_circuits": [list(c) for c in cs],
        "doubled_failures": len(fl)}
    sampled = {}
    for name, D in (("dressed parity", 4), ("F3, a + m + c = 0", 3), ("F5, c = 2a + m", 5), ("GF4, c = wa + m", 4)):
        st = {"systems": 0, "nonempty": 0, "elimination_failures": 0, "free_sets_of_parity_projection": 0}
        while st["systems"] < 120:
            n, cons = random_system(rng, [KNOTS[name]], 5)
            S = solve(D, n, cons)
            st["systems"] += 1
            if not S:
                continue
            st["nonempty"] += 1
            fr = free_map(S, n)
            st["elimination_failures"] += bool(elimination_failures(fr)[1])
            if name == "dressed parity":
                st["free_sets_of_parity_projection"] += fr == free_map({tuple(x // 2 for x in s) for s in S}, n)
        if name != "dressed parity":
            del st["free_sets_of_parity_projection"]
        sampled[name] = st
    thm4["sampled_laws"] = sampled
    thm4["dressed_parity_transfers_are_permutations"] = all(
        is_permutation(P, 4) for P in link(KNOTS["dressed parity"], 0, 2)[1].values())
    refl = ring_excluded(link(KNOTS["F3, a + m + c = 0"], 0, 2)[1], 3, 4)
    thm4["F3_x_plus_y_plus_z_rings_excluded_k1_to_4"] = [round(e, 4) for e in refl]
    checks["theorem_4"] = thm4
    ok4 = (thm4["Z6_ties_modulo_2_and_3"]["failures"] > 0 and thm4["S3_doubled_Thomsen"]["failures"] > 0
           and thm4["selector_law"]["not_all_three"] and thm4["selector_law"]["doubled_failures"] > 0
           and all(s["elimination_failures"] == 0 and s["nonempty"] > 0 for s in sampled.values())
           and sampled["dressed parity"]["free_sets_of_parity_projection"] == sampled["dressed parity"]["nonempty"]
           and not thm4["dressed_parity_transfers_are_permutations"]
           and refl[0] == 0 and refl[2] == 0 and refl[1] > 0 and refl[3] > 0)
    if not ok4:
        failures.append("Theorem 4")

    # controls
    controls["every_group_like_knot_composes_like_cycles"] = {
        "rejected": thm4["Z6_ties_modulo_2_and_3"]["failures"] > 0 and thm4["S3_doubled_Thomsen"]["failures"] > 0}
    controls["cycle_composing_knots_have_permutation_transfers"] = {
        "rejected": not thm4["dressed_parity_transfers_are_permutations"]
        and sampled["dressed parity"]["elimination_failures"] == 0}
    controls["group_like_cycle_composing_knots_remember_at_every_length"] = {"rejected": refl[0] == 0}
    controls["networks_alone_tell_cycle_composition_apart"] = {"rejected": grp_ok}
    controls["binding_loops_through_fixed_points_keeps_cycle_composition"] = {
        "rejected": thm4["selector_law"]["doubled_failures"] > 0}
    controls["no_two_loops_bind_in_cycle_composing_laws"] = {"rejected": pair_ok}
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
