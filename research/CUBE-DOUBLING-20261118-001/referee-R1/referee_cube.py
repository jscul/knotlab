"""Referee R1 for CUBE-DOUBLING-20261118-001 (own code; nothing from the study's check.py or STATE-RULES' rules.py).

  ../../../.venv/bin/python -B referee_cube.py [1|2|3|4] > referee_cube_<part>.json      (from this directory)
  ../../../.venv/bin/python -B referee_cube.py 3 33 > referee_cube_3_to33.json         (part 3 a full doubling further)

Semantics from scratch. A state is an int over n bits (bit u = distinction u's value); B(x, y, z) forbids x = z != y. A step adds
p = n with one to three knots, each on p and two old distinctions: B(u, p, v), B(u, v, p) or B(v, u, p). A99: every old state
extends, p is constrained (N' < 2N) and not a copy. An extension is the new state set; the cheapest rule takes one with fewest
states, ties broken in any way.

1. L4, one size past: every admitted extension of Q_s with up to three knots, s = 2..5, by closing the knots' allowed masks under
   intersection; the least cost, how many extensions reach it, and each one classified by which pair of old states doubles (a
   split's pair: a subdivision; the constants: a pendant), compared with the single knot B(u, p, v) or B(v', v, p) the proof names.
2. L5 by existence, without the proof's certificates: after a subdivision and after a pendant from Q_s, s = 1..5, every zero-cost
   admitted extension with up to three knots, found by testing every complement-respecting assignment of p (including those that
   put p against the constants); are they exactly the fills of the 2^s - 1 unoccupied orientations? (For s <= 3 also by the full
   closure.) Then the proof's L5 certificates, s = 1..8, read with this code's semantics.
3. Every tie rule at once: from one knot, every class of base reachable by cheapest steps (classes up to renaming the distinctions,
   read as sets of orientations up to the cube's symmetries), to n = 24; at each n the states and splits, whether n = 2^d gives
   Q_d, and the uniform distribution over distinct cheapest extensions (the study's weighting) with the number of orders lambda.
   Also to n = 33: Q_5 at 32 and the step after it. At every class before a cube, whether the free steps are exactly the fills of
   every unoccupied orientation (L3 and L5 together, read off every reachable base).
4. Side checks: the median hull of what is present after either step, against the cube the rule fills; and up to four knots per
   step (does the theorem need exactly three, or at least three?).
"""
import itertools
import json
import sys
import time
from collections import defaultdict
from fractions import Fraction

import networkx as nx
import numpy as np


def pc(x):
    return bin(x).count("1")


def cube(s):
    """Q_s: distinction i has orientation the bits of i; states are the constants and the coordinate splits."""
    n = 1 << s
    full = (1 << n) - 1
    st = {0, full}
    for j in range(s):
        m = sum(1 << i for i in range(n) if (i >> j) & 1)
        st |= {m, full ^ m}
    return sorted(st), n


def allowed(S, n, knots):
    return all(not ((((S >> x) ^ (S >> z)) & 1) == 0 and (((S >> x) ^ (S >> y)) & 1) == 1) for x, y, z in knots)


def extend(st, n, knots):
    """The new state set when p = n is added with the given knots (each a triple naming p)."""
    return sorted(S | (b << n) for S in st for b in (0, 1) if allowed(S | (b << n), n + 1, knots))


def cols(st, n):
    O = [sum(1 << i for i, S in enumerate(st) if (S >> u) & 1) for u in range(n)]
    full = (1 << len(st)) - 1
    return O, [full ^ o for o in O], full


def knot_values(st, n):
    """For every knot on p and two old distinctions: (knot, allow0, allow1), masks over the old states where p = 0 (1) is allowed."""
    O, Z, full = cols(st, n)
    p = n
    out = []
    for u, v in itertools.combinations(range(n), 2):
        out.append(((u, p, v), full ^ (O[u] & O[v]), full ^ (Z[u] & Z[v])))      # p between u and v
        out.append(((u, v, p), full ^ (Z[u] & O[v]), full ^ (O[u] & Z[v])))      # v between u and p
        out.append(((v, u, p), full ^ (Z[v] & O[u]), full ^ (O[v] & Z[u])))      # u between v and p
    return out, O, Z, full


def admitted(a0, a1, O, Z, full, N):
    if (a0 | a1) != full or pc(a0) + pc(a1) >= 2 * N:
        return False
    return not any((a0 & O[u]) == 0 and (a1 & Z[u]) == 0 for u in range(len(O)))       # a copy of u


def closure(st, n, maxk=3):
    """Every (a0, a1) reachable as the intersection of one to maxk knots' allowed masks, as packed ints a0 | a1 << N."""
    N = len(st)
    kv, O, Z, full = knot_values(st, n)
    vals = np.unique(np.array([a0 | (a1 << N) for _, a0, a1 in kv], dtype=np.uint64))
    reach = set(int(x) for x in vals)
    frontier = vals
    for _ in range(maxk - 1):
        new = set()
        step = max(1, 4_000_000 // len(vals))
        for i in range(0, len(frontier), step):
            block = (frontier[i:i + step, None] & vals[None, :]).ravel()
            new.update(int(x) for x in np.unique(block))
        frontier = np.array(sorted(new - reach), dtype=np.uint64)
        reach |= new
    mask = (1 << N) - 1
    return [(x & mask, x >> N) for x in reach], O, Z, full


def apply(st, n, a0, a1):
    return sorted([S for i, S in enumerate(st) if (a0 >> i) & 1] + [S | (1 << n) for i, S in enumerate(st) if (a1 >> i) & 1])


def cheapest(st, n):
    ext, O, Z, full = closure(st, n)
    N = len(st)
    adm = [(a0, a1) for a0, a1 in ext if admitted(a0, a1, O, Z, full, N)]
    low = min(pc(a0) + pc(a1) for a0, a1 in adm)
    return low - N, [(a0, a1) for a0, a1 in adm if pc(a0) + pc(a1) == low], len(adm), O, Z, full


def part1():
    out = {}
    for s in (2, 3, 4, 5):
        t = time.time()
        st, n = cube(s)
        cost, top, nadm, O, Z, full = cheapest(st, n)
        kinds = defaultdict(int)
        matched = 0
        for a0, a1 in top:
            both = a0 & a1
            pair = [st[i] for i in range(len(st)) if (both >> i) & 1]
            new = apply(st, n, a0, a1)
            if 0 in pair:
                kinds["pendant (the constants double)"] += 1
                # p copies some v: read v from the states where p is forced
                v = next(u for u in range(n) if all(((S >> u) & 1) == ((S >> n) & 1) for S in new if S & ((1 << n) - 1) not in (0, (1 << n) - 1)))
                matched += new == extend(st, n, [((n - 1) ^ v, v, n)])
            else:
                kinds["subdivision (a split doubles)"] += 1
                S = pair[0]
                j = next(j for j in range(s) if S in (sum(1 << i for i in range(n) if (i >> j) & 1), ((1 << n) - 1) ^ sum(1 << i for i in range(n) if (i >> j) & 1)))
                # p's orientation off split j is read from a state of each other split
                o = 0
                for jj in range(s):
                    if jj == j:
                        continue
                    m = sum(1 << i for i in range(n) if (i >> jj) & 1)
                    Sx = next(x for x in new if x & ((1 << n) - 1) == m)
                    o |= ((Sx >> n) & 1) << jj
                u, v = o & ~(1 << j), o | (1 << j)
                matched += new == extend(st, n, [(u, n, v)])
        out[s] = {"N": len(st), "admitted_extensions": nadm, "least_cost": cost, "at_least_cost": len(top),
                  "predicted": s * 2 ** (s - 1) + 2 ** s, "kinds": dict(kinds), "each_equals_the_named_single_knot": matched == len(top),
                  "seconds": round(time.time() - t, 1)}
        print("part1", s, json.dumps(out[s]), file=sys.stderr, flush=True)
    return out


def splits_of(st, n):
    full = (1 << n) - 1
    return sorted({S if not (S & 1) else full ^ S for S in st if S not in (0, full)})


def orientations(st, n):
    sp = splits_of(st, n)
    return sp, [sum(((sp[i] >> u) & 1) << i for i in range(len(sp))) for u in range(n)]


def zero_cost_fills(st, n):
    """Every zero-cost admitted extension with up to three knots, by testing every assignment f of p that respects complements:
    f's value on the all-0 state (c) and on each split's representative state.  Returns (list of (c, orientation), extensions)."""
    kv, O, Z, full = knot_values(st, n)
    N = len(st)
    sp, ori = orientations(st, n)
    k = len(sp)
    idx = {S: i for i, S in enumerate(st)}
    found = []
    for c in (0, 1):
        for o in range(1 << k):
            f1 = 0                                 # states where p = 1
            if c:
                f1 |= 1 << idx[0]
            else:
                f1 |= 1 << idx[(1 << n) - 1]
            for i, rep in enumerate(sp):
                if (o >> i) & 1:
                    f1 |= 1 << idx[rep]
                else:
                    f1 |= 1 << idx[((1 << n) - 1) ^ rep]
            f0 = full ^ f1
            covers = set()
            for _, a0, a1 in kv:
                if (a0 & f0) == f0 and (a1 & f1) == f1:          # consistent: allows f on every state
                    covers.add((f0 & ~a1 | f1 & ~a0) & full)     # forbids the other value there
            covers = sorted(covers)
            ok = full in covers or any((a | b) == full for a, b in itertools.combinations(covers, 2)) or \
                any((a | b | c3) == full for a, b, c3 in itertools.combinations(covers, 3))
            if ok and admitted(f0, f1, O, Z, full, N):
                found.append((c, o))
    return found, sp, ori


def after_step(s, kind):
    st, n = cube(s)
    if kind == "subdivision":
        return extend(st, n, [(0, n, 1)]), n + 1            # p between 0...0 and 10...0
    return extend(st, n, [(n - 1, 0, n)]), n + 1             # p copies 0...0, plus {p}


def part2():
    out = {}
    for s in (1, 2, 3, 4, 5):
        for kind in ("subdivision", "pendant"):
            t = time.time()
            st, n = after_step(s, kind)
            found, sp, ori = zero_cost_fills(st, n)
            occupied = set(ori)
            unocc = [o for o in range(1 << len(sp)) if o not in occupied]
            row = {"splits": len(sp), "unoccupied": len(unocc), "zero_cost_fills": len(found),
                   "fills_are_exactly_the_unoccupied": sorted(o for c, o in found if c == 0) == sorted(unocc),
                   "zero_cost_steps_against_the_constants": sum(1 for c, _ in found if c == 1)}
            if s <= 3:
                N = len(st)
                ext, O, Z, full = closure(st, n)
                zc = {(a0, a1) for a0, a1 in ext if admitted(a0, a1, O, Z, full, N) and pc(a0) + pc(a1) == N}
                row["full_closure_zero_cost"] = len(zc)
            row["seconds"] = round(time.time() - t, 1)
            out[f"{s} {kind}"] = row
            print("part2", s, kind, json.dumps(row), file=sys.stderr, flush=True)
    # the proof's certificates (L5), s = 1..8, with this code's semantics
    certs = {}
    for s in range(1, 9):
        for kind in ("subdivision", "pendant"):
            st, n = after_step(s, kind)
            p0 = n - 1
            P = n                                              # the new point
            sp, ori = orientations(st, n)
            ok = fills = 0
            targets = set()
            if kind == "subdivision":
                # old split 0 doubled: points (x0 = 0) = (0,0,w), (x0 = 1) = (1,1,w); p0 = (1,0,w0) with w0 = 0, between 0 and 1
                pts00 = {w: w << 1 for w in range(1 << (s - 1))}
                pts11 = {w: (w << 1) | 1 for w in range(1 << (s - 1))}
                cases = []
                for w in range(1 << (s - 1)):
                    if w != 0:
                        cases.append([(pts00[w], P, pts11[w]), (pts00[0], p0, P), (pts11[0], p0, P)])
                    cases.append([(pts00[w], P, pts11[w]), (p0, pts00[w], P), (p0, pts11[w], P)])
            else:
                c = 0
                cases = [[(p0, P, x), (c, p0, P), (c, x, P)] for x in range(n - 1) if x != c]
            N = len(st)
            for ks in cases:
                new = extend(st, n, ks)
                O, Z, full = cols(st, n)
                a0 = sum(1 << i for i, S in enumerate(st) if S in new)
                a1 = sum(1 << i for i, S in enumerate(st) if (S | (1 << n)) in new)
                good = len(new) == N and admitted(a0, a1, O, Z, full, N)
                ok += good
                if good:
                    targets.add(tuple(new))
            certs[f"{s} {kind}"] = {"certificates": len(cases), "work": ok, "distinct_fills": len(targets),
                                    "unoccupied": 2 ** s - 1}
        print("part2 certs", s, certs[f"{s} subdivision"], certs[f"{s} pendant"], file=sys.stderr, flush=True)
    out["certificates"] = certs
    return out


SYM = {}


def sym_tables(k):
    if k not in SYM:
        rows = []
        for perm in itertools.permutations(range(k)):
            for flip in range(1 << k):
                rows.append([sum(((x >> perm[i]) & 1) << i for i in range(k)) ^ flip for x in range(1 << k)])
        SYM[k] = np.array(rows, dtype=np.int64)
    return SYM[k]


def canon(st, n):
    sp, ori = orientations(st, n)
    T = sym_tables(len(sp))
    R = np.sort(T[:, ori], axis=1).astype(np.uint8)
    return (len(sp), min(r.tobytes() for r in R))


def lam(st, n):
    full = (1 << n) - 1
    sp = splits_of(st, n)
    H = nx.Graph()
    sides = [(i, x) for i, a in enumerate(sp) for x in (a, full ^ a)]
    H.add_nodes_from(range(len(sides)))
    for a, b in itertools.combinations(range(len(sides)), 2):
        if sides[a][0] != sides[b][0] and (sides[a][1] | sides[b][1]) == full:
            H.add_edge(a, b)
    return len(sp) - len(nx.max_weight_matching(H, maxcardinality=True))


def part3(nmax=24):
    st = sorted(S for S in range(8) if allowed(S, 3, [(0, 1, 2)]))
    n = 3
    dist = {canon(st, n): [st, Fraction(1)]}
    levels = []
    while True:
        lamd = defaultdict(Fraction)
        Ns = set()
        ks = set()
        for key, (S, p) in dist.items():
            lamd[lam(S, n)] += p
            Ns.add(len(S))
            ks.add(key[0])
        d = n.bit_length() - 1
        is_cube = [key for key in dist if n == 1 << d and key[0] == d]
        levels.append({"n": n, "classes": len(dist), "states": sorted(Ns), "splits": sorted(ks),
                       "Q_d_with_probability_1": (n == 1 << d and len(is_cube) == len(dist)) if n == 1 << d else None,
                       "lambda": {str(k): str(v) for k, v in sorted(lamd.items())},
                       "lambda_float": {str(k): float(v) for k, v in sorted(lamd.items())}})
        print("part3", json.dumps({k: v for k, v in levels[-1].items() if k != "lambda"}), file=sys.stderr, flush=True)
        if n >= nmax:
            break
        new = {}
        not_all = 0
        for key, (S, p) in dist.items():
            found, sp, ori = zero_cost_fills(S, n)
            unocc = sorted(set(range(1 << len(sp))) - set(ori))
            if found and sorted(o for c, o in found if c == 0) != unocc or any(c == 1 for c, _ in found):
                not_all += 1                       # a free orientation with no certificate, or a free step against the constants
            if found:
                O, Z, full = cols(S, n)
                exts = []
                for c, o in found:
                    f1 = sum(1 << i for i, x in enumerate(S)
                             if (x == 0 and c) or (x == (1 << n) - 1 and not c) or
                             any(x == rep and (o >> j) & 1 for j, rep in enumerate(sp)) or
                             any(x == ((1 << n) - 1) ^ rep and not (o >> j) & 1 for j, rep in enumerate(sp)))
                    exts.append(apply(S, n, ((1 << len(S)) - 1) ^ f1, f1))
                cost = 0
            else:
                cost, top, _, O, Z, full = cheapest(S, n)
                exts = [apply(S, n, a0, a1) for a0, a1 in top]
            exts = sorted(set(tuple(e) for e in exts))
            for e in exts:
                kk = canon(list(e), n + 1)
                if kk not in new:
                    new[kk] = [list(e), Fraction(0)]
                new[kk][1] += p / len(exts)
        levels[-1]["classes_where_the_free_steps_are_not_exactly_the_unoccupied_fills"] = not_all
        dist = new
        n += 1
    return levels


def median_hull(points, k):
    hull = set(points)
    while True:
        new = {a & b | b & c | a & c for a, b, c in itertools.combinations_with_replacement(sorted(hull), 3)} - hull
        if not new:
            return hull
        hull |= new


def part4():
    """Two side checks.  (a) After a subdivision or a pendant from Q_s, the median hull of the occupied orientations (closure under
    coordinatewise majority, Mulder's median structure) against the whole cube of the s + 1 splits that the cheapest rule fills.
    (b) More knots per step: with up to four knots, from Q_s the least cost and the extensions reaching it, and after either step the
    zero-cost extensions, s = 2, 3."""
    out = {"median_hull": {}, "four_knots": {}}
    for s in (2, 3, 4, 5):
        for kind in ("subdivision", "pendant"):
            st, n = after_step(s, kind)
            sp, ori = orientations(st, n)
            out["median_hull"][f"{s} {kind}"] = {"occupied": len(set(ori)), "median_hull": len(median_hull(ori, len(sp))),
                                                 "cube": 1 << len(sp)}
    for s in (2, 3):
        st, n = cube(s)
        ext, O, Z, full = closure(st, n, maxk=4)
        N = len(st)
        adm = [(a0, a1) for a0, a1 in ext if admitted(a0, a1, O, Z, full, N)]
        low = min(pc(a0) + pc(a1) for a0, a1 in adm)
        row = {"from_Q_s_least_cost": low - N, "at_least_cost": sum(1 for a0, a1 in adm if pc(a0) + pc(a1) == low)}
        for kind in ("subdivision", "pendant"):
            st2, n2 = after_step(s, kind)
            ext, O, Z, full = closure(st2, n2, maxk=4)
            N2 = len(st2)
            row[f"zero_cost_after_{kind}"] = sum(1 for a0, a1 in ext if admitted(a0, a1, O, Z, full, N2) and pc(a0) + pc(a1) == N2)
            row["unoccupied"] = 2 ** s - 1
        out["four_knots"][s] = row
        print("part4", s, json.dumps(row), file=sys.stderr, flush=True)
    return out


def main():
    part = sys.argv[1] if len(sys.argv) > 1 else "all"
    out = {}
    if part in ("1", "all"):
        out["1_L4_extensions_of_Q_s"] = part1()
    if part in ("2", "all"):
        out["2_L5_by_existence"] = part2()
    if part in ("3", "all"):
        nmax = int(sys.argv[2]) if len(sys.argv) > 2 else 24
        out["3_every_tie_rule_from_one_knot"] = part3(nmax)
    if part in ("4", "all"):
        out["4_median_hull_and_four_knots"] = part4()
    print(json.dumps(out, indent=1, default=str))


if __name__ == "__main__":
    main()
