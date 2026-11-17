"""Referee R1 for STATE-RULES-20261117-001: fresh, independent code (nothing imported from the study).

  ../../../.venv/bin/python -B referee_fresh.py > referee_fresh.json      (from this directory)

A base is a set of states (ints, bit x = distinction x).  B(x, y, z) excludes x = z != y.  A step adds distinction p = n with up
to K betweenness knots on triples containing p, in any of the three roles; it is admitted when every old state extends, p is
constrained (N' < 2N) and p is not equal to an old distinction in every state.  Extensions are distinct state sets.
Orders: k = chromatic number of the crossing graph of the splits; lam = the least number of chains of nested oriented splits
covering them, by brute force over orientations with Dilworth (independent of Eppstein's matching formula, which is also coded
and compared).

1. S4 and S3 on a line of n = 3 .. 10: the zero-cost extensions (N' = N) number C(n, 3) and are all two orders (k = lam = 2);
   every admitted extension has k, lam <= 2; exactly n + 1 keep a line, all at N + 2.
2. S2: one knot per step, fewest states, uniform among the fewest extensions, from the line of three, the 2 x 2 cut system and the
   three-leaf star, 20 runs each to n = 13: (k, lam) at every step.
3. R7 and R8, exactly: fewest states with up to three knots from one knot, the probability of two orders at n = 5, 6 and 7,
   counting extensions one by one, and at n = 6 counting each class of outcome once (classes by brute-force canonical form).
"""
import itertools
import json
import math
import random
import sys
from collections import Counter
from fractions import Fraction

import networkx as nx


def ok_btw(t, x, y, z):
    return not ((((t >> x) ^ (t >> z)) & 1) == 0 and (((t >> x) ^ (t >> y)) & 1) == 1)


def line(n):
    out = set()
    for c in range(n + 1):
        a = sum(1 << i for i in range(c, n))
        out |= {a, ((1 << n) - 1) ^ a}
    return frozenset(out)


def base(n, knots):
    return frozenset(s for s in range(1 << n) if all(ok_btw(s, *k) for k in knots))


def knots_with(n):
    p = n
    out = []
    for u, v in itertools.combinations(range(n), 2):
        out += [(u, p, v), (u, v, p), (v, u, p)]
    return out


def extensions(S, n, K):
    """{new state set: number of knot sets giving it} over admitted steps with 1..K knots."""
    S = sorted(S)
    N = len(S)
    allowed = []
    for k in knots_with(n):
        a = []
        for s in S:
            a.append(tuple(b for b in (0, 1) if ok_btw(s | (b << n), *k)))
        allowed.append(a)
    cols = [tuple((s >> u) & 1 for s in S) for u in range(n)]
    out = Counter()
    for r in range(1, K + 1):
        for combo in itertools.combinations(range(len(allowed)), r):
            vals = []
            dead = False
            for i in range(N):
                sset = set((0, 1))
                for c in combo:
                    sset &= set(allowed[c][i])
                if not sset:
                    dead = True
                    break
                vals.append(sset)
            if dead:
                continue
            Np = sum(len(v) for v in vals)
            if Np >= 2 * N:
                continue
            if any(all(vals[i] == {cols[u][i]} for i in range(N)) for u in range(n)):
                continue
            new = frozenset(S[i] | (b << n) for i in range(N) for b in vals[i])
            out[new] += 1
    return out


def splits(S, n):
    full = (1 << n) - 1
    return sorted({min(s, full ^ s) for s in S if s not in (0, full)})


def crosses(a, b, full):
    return all(x for x in (a & b, a & (full ^ b), (full ^ a) & b, (full ^ a) & (full ^ b)))


def chrom(sp, full):
    s = len(sp)
    adj = [[j for j in range(s) if j != i and crosses(sp[i], sp[j], full)] for i in range(s)]
    for k in range(1, s + 1):
        col = {}
        def bt(i):
            if i == s:
                return True
            for c in range(k):
                if all(col.get(j) != c for j in adj[i]):
                    col[i] = c
                    if bt(i + 1):
                        return True
                    del col[i]
            return False
        if bt(0):
            return k
    return 0


def lam_brute(sp, full):
    s = len(sp)
    if s == 0:
        return 0
    best = s
    for orient in range(1 << (s - 1)):            # orienting all splits the other way gives the same chains, reversed
        sides = [sp[i] if not (orient >> i) & 1 else full ^ sp[i] for i in range(s)]
        G = nx.Graph()
        G.add_nodes_from([("a", i) for i in range(s)] + [("b", i) for i in range(s)])
        for i in range(s):
            for j in range(s):
                if i != j and sides[i] & sides[j] == sides[i]:
                    G.add_edge(("a", i), ("b", j))
        m = nx.bipartite.maximum_matching(G, top_nodes=[("a", i) for i in range(s)])
        best = min(best, s - len(m) // 2)
    return best


def lam_eppstein(sp, full):
    G = nx.Graph()
    sides = [(i, x) for i, a in enumerate(sp) for x in (a, full ^ a)]
    G.add_nodes_from(range(len(sides)))
    for p, q in itertools.combinations(range(len(sides)), 2):
        if sides[p][0] != sides[q][0] and (sides[p][1] | sides[q][1]) == full:
            G.add_edge(p, q)
    return len(sp) - len(nx.max_weight_matching(G, maxcardinality=True))


def orders(S, n, brute=True):
    full = (1 << n) - 1
    sp = splits(S, n)
    lam = lam_brute(sp, full) if (brute and len(sp) <= 10) else lam_eppstein(sp, full)
    return chrom(sp, full), lam


def part1():
    out = []
    for n in range(3, 11):
        S = line(n)
        N = len(S)
        ext = extensions(S, n, 3)
        zero = [e for e in ext if len(e) == N]
        zero_two = sum(1 for e in zero if orders(e, n + 1) == (2, 2))
        maxk = max(orders(e, n + 1, brute=False)[0] for e in ext)
        maxl = max(orders(e, n + 1, brute=False)[1] for e in ext)
        lines = [e for e in ext if orders(e, n + 1, brute=False)[1] == 1 and len(e) == 2 * (n + 1)]
        row = {"n": n, "admitted": len(ext), "zero_cost": len(zero), "C(n,3)": math.comb(n, 3), "zero_cost_two_orders": zero_two,
               "max_k": maxk, "max_lam": maxl, "keep_a_line": len(lines), "all_line_keepers_at_N+2": all(len(e) == N + 2 for e in lines)}
        out.append(row)
        print("part1", json.dumps(row), file=sys.stderr, flush=True)
    return out


START = {"line": (3, [(0, 1, 2)]), "2x2": (4, [(0, 1, 3), (0, 2, 3), (1, 0, 2), (1, 3, 2)]),
         "star": (4, [(1, 0, 2), (1, 0, 3), (2, 0, 3)])}


def part2(runs=20, nmax=13):
    out = {}
    for name, (n0, kn) in START.items():
        seen = Counter()
        lam_check = 0
        for r in range(runs):
            rng = random.Random(f"ref:{name}:{r}")
            n, S = n0, base(n0, kn)
            seen[orders(S, n)] += 1
            while n < nmax:
                ext = extensions(S, n, 1)
                low = min(len(e) for e in ext)
                top = sorted((e for e in ext if len(e) == low), key=lambda e: sorted(e))
                S = rng.choice(top)
                n += 1
                o = orders(S, n, brute=False)
                seen[o] += 1
                if len(splits(S, n)) <= 10 and r < 3:
                    full = (1 << n) - 1
                    lam_check += lam_brute(splits(S, n), full) == o[1]
        out[name] = {"(k, lam) seen": {str(k): v for k, v in seen.items()}, "brute_lam_agreements": lam_check}
        print("part2", name, json.dumps(out[name]), file=sys.stderr, flush=True)
    return out


def canon(S, n):
    best = None
    for perm in itertools.permutations(range(n)):
        key = tuple(sorted(sum(((s >> i) & 1) << perm[i] for i in range(n)) for s in S))
        if best is None or key < best:
            best = key
    return best


def fewest(S, n):
    ext = extensions(S, n, 3)
    low = min(len(e) for e in ext)
    return [e for e in ext if len(e) == low]


def part3():
    S3 = line(3)
    d4 = fewest(S3, 3)
    assert len(d4) == 1
    S4 = d4[0]
    res = {"n4_options": len(d4), "n4_two_orders": orders(S4, 4) == (2, 2)}
    opts5 = fewest(S4, 4)
    res["n5_options"] = len(opts5)
    res["n5_classes"] = len({canon(e, 5) for e in opts5})
    p5 = Fraction(sum(orders(e, 5) == (2, 2) for e in opts5), len(opts5))
    p6 = Fraction(0)
    p7 = Fraction(0)
    p6_classes = Fraction(0)
    cls5 = {}
    for e in opts5:
        cls5.setdefault(canon(e, 5), []).append(e)
    for e5 in opts5:
        opts6 = fewest(e5, 5)
        w = Fraction(1, len(opts5) * len(opts6))
        for e6 in opts6:
            if orders(e6, 6) == (2, 2):
                p6 += w
            opts7 = fewest(e6, 6)
            p7 += w * Fraction(sum(orders(e7, 7) == (2, 2) for e7 in opts7), len(opts7))
    for c, members in cls5.items():                    # classes counted once: each class of outcome gets equal weight
        rep = members[0]
        opts6 = fewest(rep, 5)
        c6 = {}
        for e6 in opts6:
            c6.setdefault(canon(e6, 6), e6)
        two = sum(orders(e6, 6) == (2, 2) for e6 in c6.values())
        p6_classes += Fraction(1, len(cls5)) * Fraction(two, len(c6))
    res.update({"P_two_orders": {"5": str(p5), "6": str(p6), "7": str(p7)}, "P_two_orders_classes_once_6": str(p6_classes)})
    print("part3", json.dumps(res), file=sys.stderr, flush=True)
    return res


def main():
    print(json.dumps({"1_line_extensions": part1(), "2_one_knot_fewest": part2(), "3_exact_three_knot_fewest": part3()}, indent=1))


if __name__ == "__main__":
    main()
