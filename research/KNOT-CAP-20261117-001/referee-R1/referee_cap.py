"""Referee R1 for KNOT-CAP-20261117-001 (own code; nothing from the study's caplib.py or STATE-RULES' rules.py).

  ../../../.venv/bin/python -B referee_cap.py > referee_cap.json      (from this directory)

Moves (A99): add distinction p = n with an irredundant set of 1..3 betweenness knots on p and two old distinctions; every old state
extends, p constrained (N' < 2N) and not equal to an old distinction in every state.  KF3: each new knot's two old distinctions
already share a knot; fewest states; uniform over knot sets.  Caps: after the move every distinction in at most c knots
(degree cap), or every pair in at most m knots (pair cap).  Distributions are propagated exactly over labelled bases (renaming
before each read does not change the class distribution, since it maps moves one to one).

1. T1, T2: from one knot under c = 3 and under m = 2 (with and without knot-locality): the first step's outcome, and whether any
   move is allowed afterwards.
2. The six-starts (fan6, nonfan6), exactly to n = 9: the distribution of (k, lam), of two orders, and of coarse features (N,
   splits, crossings); and the five-starts (fan5, mid5) to n = 8.
3. The five-start pair choice: every set of three betweenness knots on five distinctions whose base is a line; does every such
   set have a distinction in all three knots?
"""
import itertools
import json
import sys
from collections import Counter, defaultdict
from fractions import Fraction

import networkx as nx

SEEDS = {"line": (3, [(0, 1, 2)]),
         "fan6": (6, [(0, 1, 2), (0, 2, 3), (0, 3, 4), (0, 4, 5)]),
         "nonfan6": (6, [(1, 2, 3), (1, 3, 4), (4, 1, 0), (0, 4, 5)]),
         "fan5": (5, [(0, 1, 2), (0, 2, 3), (0, 3, 4)]),
         "mid5": (5, [(0, 1, 2), (0, 2, 4), (2, 3, 4)])}


def pc(x):
    return bin(x).count("1")


def ok_btw(s, x, y, z):
    return not ((((s >> x) ^ (s >> z)) & 1) == 0 and (((s >> x) ^ (s >> y)) & 1) == 1)


def base(n, knots):
    return tuple(s for s in range(1 << n) if all(ok_btw(s, *k) for k in knots))


def cols(S, n):
    O = [0] * n
    for i, s in enumerate(S):
        for u in range(n):
            if (s >> u) & 1:
                O[u] |= 1 << i
    full = (1 << len(S)) - 1
    return O, [full ^ o for o in O], full


def candidates(S, n, knots, local):
    O, Z, full = cols(S, n)
    p = n
    pairs = {(min(a, b), max(a, b)) for k in knots for a, b in itertools.combinations(k, 2)} if local else None
    out = []
    for u, v in itertools.combinations(range(n), 2):
        if local and (u, v) not in pairs:
            continue
        eq = (O[u] & O[v]) | (Z[u] & Z[v])
        ne = full ^ eq
        out.append(((u, p, v), full ^ (O[u] & O[v]), full ^ (Z[u] & Z[v])))      # p between u and v
        out.append(((u, v, p), eq | (ne & Z[v]), eq | (ne & O[v])))                # v between u and p
        out.append(((v, u, p), eq | (ne & Z[u]), eq | (ne & O[u])))                # u between v and p
    return out, O, Z, full


def moves(S, n, knots, local=True, cap=None, pair=None):
    cands, O, Z, full = candidates(S, n, knots, local)
    N = len(S)
    ties = {(Z[u], O[u]) for u in range(n)}
    adm = lambda a0, a1: (a0 | a1) == full and (a0, a1) not in ties and pc(a0) + pc(a1) < 2 * N
    deg = Counter(x for k in knots for x in k)
    pcnt = Counter((min(a, b), max(a, b)) for k in knots for a, b in itertools.combinations(k, 2))
    out = []
    m = len(cands)
    for r in (1, 2, 3):
        for combo in itertools.combinations(range(m), r):
            a0, a1 = full, full
            parts = []
            for c in combo:
                a0 &= cands[c][1]
                a1 &= cands[c][2]
            if not adm(a0, a1):
                continue
            if r >= 2:                     # irredundant: dropping any one knot changes the states
                red = False
                for drop in combo:
                    b0, b1 = full, full
                    for c in combo:
                        if c != drop:
                            b0 &= cands[c][1]
                            b1 &= cands[c][2]
                    if (b0, b1) == (a0, a1):
                        red = True
                        break
                if red:
                    continue
            ks = [cands[c][0] for c in combo]
            if cap is not None:
                d2 = deg + Counter(x for k in ks for x in k)
                if any(v > cap for v in d2.values()):
                    continue
            if pair is not None:
                p2 = pcnt + Counter((min(a, b), max(a, b)) for k in ks for a, b in itertools.combinations(k, 2))
                if any(v > pair for v in p2.values()):
                    continue
            out.append((a0, a1, tuple(ks)))
    return out


def apply(S, n, a0, a1):
    out = []
    for i, s in enumerate(S):
        if (a0 >> i) & 1:
            out.append(s)
        if (a1 >> i) & 1:
            out.append(s | (1 << n))
    return tuple(sorted(out))


def measure(S, n):
    full = (1 << n) - 1
    sp = sorted({min(s, full ^ s) for s in S if s not in (0, full)})
    cr = [(i, j) for i, j in itertools.combinations(range(len(sp)), 2)
          if all(x for x in (sp[i] & sp[j], sp[i] & (full ^ sp[j]), (full ^ sp[i]) & sp[j], (full ^ sp[i]) & (full ^ sp[j])))]
    G = nx.Graph()
    G.add_nodes_from(range(len(sp)))
    G.add_edges_from(cr)
    if not cr:
        k = 1
    elif nx.is_bipartite(G):
        k = 2
    else:
        k = 3                                          # "3 or more"; only k <= 2 matters for two orders
    H = nx.Graph()
    sides = [(i, x) for i, a in enumerate(sp) for x in (a, full ^ a)]
    H.add_nodes_from(range(len(sides)))
    for a, b in itertools.combinations(range(len(sides)), 2):
        if sides[a][0] != sides[b][0] and (sides[a][1] | sides[b][1]) == full:
            H.add_edge(a, b)
    lam = len(sp) - len(nx.max_weight_matching(H, maxcardinality=True))
    return {"N": len(S), "splits": len(sp), "crossings": len(cr), "k": k, "lam": lam}


def exact(start, nmax, local=True, cap=None, pair=None):
    n, kn = SEEDS[start]
    dist = {(base(n, kn), tuple(sorted(kn))): Fraction(1)}
    levels = []
    stalled = Fraction(0)
    while True:
        lam = Counter()
        feat = Counter()
        two = Fraction(0)
        for (S, K), p in dist.items():
            m = measure(S, n)
            lam[m["lam"]] += p
            feat[(m["N"], m["splits"], m["crossings"], m["lam"])] += p
            if m["k"] == 2 and m["lam"] == 2:
                two += p
        levels.append({"n": n, "labelled_bases": len(dist), "two_orders": two, "lam": dict(lam), "features": dict(feat),
                       "stalled_before": stalled})
        if n >= nmax:
            break
        new = defaultdict(Fraction)
        for (S, K), p in dist.items():
            mv = moves(S, n, list(K), local, cap, pair)
            if not mv:
                stalled += p
                continue
            low = min(pc(a0) + pc(a1) for a0, a1, _ in mv)
            top = [x for x in mv if pc(x[0]) + pc(x[1]) == low]
            for a0, a1, ks in top:
                new[(apply(S, n, a0, a1), tuple(sorted(K + ks)))] += p / len(top)
        dist = dict(new)
        n += 1
        print("level", start, n, len(dist), file=sys.stderr, flush=True)
    return levels


def part1():
    out = {}
    for name, kw in (("degree cap 3, knot-local", dict(local=True, cap=3)), ("degree cap 3, any pairs", dict(local=False, cap=3)),
                     ("pair cap 2, knot-local", dict(local=True, pair=2)), ("pair cap 2, any pairs", dict(local=False, pair=2))):
        lv = exact("line", 6, **kw)
        out[name] = [{"n": L["n"], "bases": L["labelled_bases"], "lam": {str(k): str(v) for k, v in L["lam"].items()},
                      "stalled_before": str(L["stalled_before"])} for L in lv]
        print("part1", name, json.dumps(out[name]), file=sys.stderr, flush=True)
    return out


def part2():
    out = {}
    for a, b, nmax in (("fan6", "nonfan6", 9), ("fan5", "mid5", 8)):
        la, lb = exact(a, nmax), exact(b, nmax)
        rows = []
        for A, B in zip(la, lb):
            fa = {str(k): v for k, v in A["features"].items()}
            fb = {str(k): v for k, v in B["features"].items()}
            tvf = sum(abs(fa.get(k, 0) - fb.get(k, 0)) for k in set(fa) | set(fb)) / 2
            rows.append({"n": A["n"], "two_orders": [str(A["two_orders"]), str(B["two_orders"])],
                         "two_orders_float": [float(A["two_orders"]), float(B["two_orders"])],
                         "lam_equal": A["lam"] == B["lam"], "lam": [{str(k): float(v) for k, v in A["lam"].items()},
                                                                      {str(k): float(v) for k, v in B["lam"].items()}],
                         "tv_features": float(tvf), "labelled_bases": [A["labelled_bases"], B["labelled_bases"]]})
            print("part2", a, b, json.dumps(rows[-1]), file=sys.stderr, flush=True)
        out[f"{a}|{b}"] = rows
    return out


def is_line(S, n):
    full = (1 << n) - 1
    if len(S) != 2 * n:
        return False
    sp = sorted({min(s, full ^ s) for s in S if s not in (0, full)})
    return all(any((a & b) in (a, b) or (a & (full ^ b)) in (a, full ^ b) for _ in [0]) for a, b in itertools.combinations(sp, 2)) \
        and all(not all(x for x in (a & b, a & (full ^ b), (full ^ a) & b, (full ^ a) & (full ^ b)))
                for a, b in itertools.combinations(sp, 2)) and measure(S, n)["lam"] == 1


def part3(n=5):
    knots = [k for k in itertools.permutations(range(n), 3) if k[0] < k[2]]
    found = []
    for combo in itertools.combinations(knots, 3):
        S = base(n, combo)
        if is_line(S, n):
            common = set(combo[0]) & set(combo[1]) & set(combo[2])
            D = {(u, v): sum(((t >> u) ^ (t >> v)) & 1 for t in S) for u in range(n) for v in range(n)}
            e = max(D, key=D.get)[0]
            order = sorted(range(n), key=lambda v: D[(e, v)])
            pos = sorted(min(order.index(c), n - 1 - order.index(c)) for c in common)
            found.append({"knots": combo, "common": sorted(common), "hub_distance_from_nearest_end": pos})
    return {"three_knot_presentations_of_a_line_of_five": len(found),
            "all_have_a_common_distinction": all(f["common"] for f in found),
            "common_count": dict(Counter(len(f["common"]) for f in found)),
            "hub_position (0 = an end, 1 = next to an end, 2 = the middle)": dict(Counter(str(f["hub_distance_from_nearest_end"]) for f in found))}


def main():
    out = {"1_tight_caps": part1(), "3_five_start_presentations": part3()}
    out["2_matched_starts_exact"] = part2()
    print(json.dumps(out, indent=1, default=str))


if __name__ == "__main__":
    main()
