"""Referee R1 for MEET-ORDERS-20261118-001 (own code; the study's melib.py and job.py are not imported).

  ../../../.venv/bin/python -B referee_meet.py <part> > referee_meet_<part>.json      (from this directory)

The KF3 move set and the number of orders are the referee's own from KNOT-CAP-R1 (`measure` from referee_cap.py, Eppstein's matching
formula with the crossing graph's colouring), with a new vectorised enumeration of the knot sets.  States are labelled (S, G): the
allowed states and the co-knotted pairs, which is all KF3 reads.

Parts:
  thm1    Theorem 1 against the exact chance of two orders after the second new distinction, for every bracketing of a line of
          4 to 9 distinctions, and 200 random bracketings each of 10, 11 and 12 (the study's finite check ran every bracketing to
          11; 12 is one size past).
  five    the three five-starts (end, next to an end, middle) exactly to n = 9: two orders and the whole distribution of the
          number of orders at each n (the study: next 163213/181890072 and end 1810423/995045688 at n = 9).
  tie     the n0 = 8 tie at n0 + 4: the two bracketings (x,((x,(x,x)),(x,(x,x)))) and (x,(((x,x),x),((x,x),x))), exact to n = 12;
          and two other same-bare-bracketing pairs at n0 = 8 as controls.
  meet    the post hoc meeting-pattern reading, one size past (n0 = 8, to n0 + 3): group the bracketings by the meeting pattern as
          an abstract incidence (knots and distinctions, up to renaming); is the signature (labelled bases and the mass by largest
          odd set at each level) the same within a group and different between groups?
  extra   the six-starts' labelled counts and two-order chances with this engine; and A100: one redundant knot added to each
          five-start, against the fewest-knot value at n = 7.
"""
import itertools
import json
import random
import sys
from collections import Counter, defaultdict
from fractions import Fraction
from pathlib import Path

import networkx as nx
import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "research/KNOT-CAP-20261117-001/referee-R1"))
import referee_cap as RC  # noqa: E402  (the referee's own KNOT-CAP-R1 code: base, measure)


def pc(x):
    return bin(x).count("1")


def line_states(n):
    """The line 0..n-1: constants and the prefix cuts with their complements."""
    full = (1 << n) - 1
    st = {0, full}
    for k in range(1, n):
        P = (1 << k) - 1
        st |= {P, full ^ P}
    return tuple(sorted(st))


def bracketings(a, b):
    if b - a <= 1:
        return [()]
    out = []
    for c in range(a + 1, b):
        for L in bracketings(a, c):
            for R in bracketings(c, b):
                out.append(((a, c, b),) + L + R)
    return out


def random_bracketing(a, b, rng):
    """A uniform random bracketing of a..b (uniform over triangulations, by the Catalan recursion)."""
    from functools import lru_cache

    @lru_cache(None)
    def cat(k):
        return 1 if k <= 1 else sum(cat(i) * cat(k - 1 - i) for i in range(k))

    def rec(a, b):
        if b - a <= 1:
            return ()
        steps = b - a
        w = [cat(c - a - 1 + 0) * cat(b - c - 1) for c in range(a + 1, b)]
        # number of bracketings of a..c is cat(c - a - 1) when counting knots c - a - 1
        c = rng.choices(range(a + 1, b), weights=w)[0]
        return ((a, c, b),) + rec(a, c) + rec(c, b)
    return rec(a, b)


def pairs_of(knots):
    return frozenset((min(x, y), max(x, y)) for k in knots for x, y in itertools.combinations(k, 2))


def pins(S, n, G):
    full = (1 << len(S)) - 1
    O = [sum(1 << i for i, s in enumerate(S) if (s >> u) & 1) for u in range(n)]
    Z = [full ^ o for o in O]
    out = []
    for u, v in sorted(G):
        ne = (O[u] & Z[v]) | (Z[u] & O[v])
        out.append(((u, n, v), Z[u] & Z[v], O[u] & O[v]))         # B(u, p, v): where u = v, p takes their value
        out.append(((u, v, n), ne & Z[v], ne & O[v]))             # B(u, v, p): where u != v, p takes v's value
        out.append(((v, u, n), ne & Z[u], ne & O[u]))             # B(v, u, p): where u != v, p takes u's value
    return out, O, Z, full


def options(S, n, G):
    """KF3: every irredundant, compatible set of 1..3 knot-local knots on p = n that keeps every old state, constrains p and
    copies nothing; returns (least cost, the cheapest sets as (pin0, pin1, knots))."""
    cand, O, Z, full = pins(S, n, G)
    m = len(cand)
    N = len(S)
    P0 = np.array([c[1] for c in cand], dtype=np.int64)
    P1 = np.array([c[2] for c in cand], dtype=np.int64)
    comp = ((P0[:, None] & P1[None, :]) == 0) & ((P1[:, None] & P0[None, :]) == 0)
    ties = {(Z[u], O[u]) for u in range(n)}
    found = []

    def keep(idx, q0, q1):
        if q0 == 0 and q1 == 0:
            return
        a0, a1 = full ^ q1, full ^ q0
        if (a0, a1) in ties:
            return
        found.append((2 * N - pc(q0) - pc(q1), q0, q1, tuple(cand[i][0] for i in idx)))

    for i in range(m):
        keep((i,), int(P0[i]), int(P1[i]))
    for i, j in zip(*np.nonzero(np.triu(comp, 1))):
        i, j = int(i), int(j)
        u0, u1 = int(P0[i] | P0[j]), int(P1[i] | P1[j])
        if (u0, u1) != (int(P0[i]), int(P1[i])) and (u0, u1) != (int(P0[j]), int(P1[j])):
            keep((i, j), u0, u1)
        ks = np.nonzero(comp[i, j + 1:] & comp[j, j + 1:])[0] + j + 1
        if len(ks) == 0:
            continue
        t0, t1 = u0 | P0[ks], u1 | P1[ks]
        # irredundant: dropping any one of the three changes the union
        d_k = (t0 != u0) | (t1 != u1)
        d_j = (t0 != (P0[i] | P0[ks])) | (t1 != (P1[i] | P1[ks]))
        d_i = (t0 != (P0[j] | P0[ks])) | (t1 != (P1[j] | P1[ks]))
        for k, a, b in zip(ks[d_k & d_j & d_i].tolist(), t0[d_k & d_j & d_i].tolist(), t1[d_k & d_j & d_i].tolist()):
            keep((i, j, k), int(a), int(b))
    if not found:
        return None, []
    low = min(f[0] for f in found)
    return low - N, [f[1:] for f in found if f[0] == low]


def extend(S, n, q0, q1):
    full = (1 << len(S)) - 1
    a0, a1 = full ^ q1, full ^ q0
    return tuple(sorted([s for i, s in enumerate(S) if (a0 >> i) & 1] + [s | (1 << n) for i, s in enumerate(S) if (a1 >> i) & 1]))


def run(n0, knots, depth, keep_levels=False):
    S = line_states(n0)
    assert S == RC.base(n0, list(knots)), "not a presentation of the line"
    dist = {(S, pairs_of(knots)): Fraction(1)}
    n = n0
    levels = []
    while True:
        lam = Counter()
        two = Fraction(0)
        for (S1, G1), p in dist.items():
            mm = RC.measure(S1, n)
            lam[mm["lam"]] += p
            two += p if (mm["k"] == 2 and mm["lam"] == 2) else 0
        levels.append({"n": n, "labelled": len(dist), "two": two, "lam": dict(lam), "dist": dist if keep_levels else None})
        if n >= n0 + depth:
            return levels
        new = defaultdict(Fraction)
        for (S1, G1), p in dist.items():
            cost, top = options(S1, n, G1)
            if not top:
                continue
            for q0, q1, ks in top:
                new[(extend(S1, n, q0, q1), G1 | pairs_of(ks))] += p / len(top)
        dist = dict(new)
        n += 1


def formula(knots, n0):
    """Theorem 1, from the referee's own reading of s, p and c."""
    span = {(k[0], k[2]): k for k in knots}
    children = {k: [span[h] for h in ((k[0], k[1]), (k[1], k[2])) if h in span] for k in knots}
    parent = {ch: k for k in knots for ch in children[k]}

    def steps(k):
        return set(range(k[0] + 1, k[2] + 1))
    tot = Fraction(0)
    for k in knots:
        s = sum(1 for t in knots if t != k and not (steps(t) & steps(k)))
        p = 1 if k in parent else 0
        c = len(children[k])
        tot += Fraction(s + 2 * p + c, (n0 - 3) + 2 * (p + c))
    return tot / len(knots)


def part_thm1():
    out = {}
    rng = random.Random(3)
    for n0 in range(4, 13):
        if n0 <= 9:
            Ts = bracketings(0, n0 - 1)
        else:
            Ts = [random_bracketing(0, n0 - 1, rng) for _ in range(200 if n0 < 12 else 120)]
        bad = 0
        for T in Ts:
            two = run(n0, T, 2)[-1]["two"]
            bad += two != formula(T, n0)
        out[n0] = {"bracketings_checked": len(Ts), "all": n0 <= 9, "mismatches": bad}
        print("thm1", n0, json.dumps(out[n0]), file=sys.stderr, flush=True)
    return out


FIVE = {"end": ((0, 1, 2), (0, 2, 3), (0, 3, 4)), "next to an end": ((0, 1, 3), (0, 3, 4), (1, 2, 3)),
        "middle": ((0, 1, 2), (0, 2, 4), (2, 3, 4))}


def part_five():
    out = {}
    for name, T in FIVE.items():
        lv = run(5, T, 4)
        out[name] = [{"n": L["n"], "labelled": L["labelled"], "two": str(L["two"]),
                      "lam": {str(k): str(v) for k, v in sorted(L["lam"].items())}} for L in lv]
        print("five", name, json.dumps(out[name][-1]), file=sys.stderr, flush=True)
    for a, b in (("end", "next to an end"), ("end", "middle")):
        out[f"{a} vs {b}: first n where the distributions differ"] = next(
            (x["n"] for x, y in zip(out[a], out[b]) if x["lam"] != y["lam"] or x["two"] != y["two"]), None)
    return out


def parse(s):
    """Bracket string (step first, as in the study) -> knots on 0..m: 'x' is a step, '(L,R)' a knot."""
    pos = [0]

    def rec(i):
        if s[i] == "x":
            a = pos[0]
            pos[0] += 1
            return i + 1, [], a, pos[0]
        assert s[i] == "("
        i, KL, a, c = rec(i + 1)
        assert s[i] == ","
        i, KR, c2, b = rec(i + 1)
        assert s[i] == ")" and c2 == c
        return i + 1, KL + KR + [(a, c, b)], a, b
    _, K, a, b = rec(0)
    return tuple(K), b + 1


def part_tie():
    out = {}
    pair = ["(x,((x,(x,x)),(x,(x,x))))", "(x,(((x,x),x),((x,x),x)))"]
    lv = {}
    for s in pair:
        T, n0 = parse(s)
        assert n0 == 8 and len(T) == 6
        L = run(n0, T, 4)
        lv[s] = [{"n": x["n"], "labelled": x["labelled"], "two": str(x["two"]),
                  "lam": {str(k): str(v) for k, v in sorted(x["lam"].items())}} for x in L]
        print("tie", s, json.dumps(lv[s][-1]), file=sys.stderr, flush=True)
    out["pair"] = lv
    out["same_distribution_at_n0+4"] = lv[pair[0]][-1]["lam"] == lv[pair[1]][-1]["lam"]
    out["same_through_n0+3"] = all(x["lam"] == y["lam"] for x, y in zip(lv[pair[0]][:4], lv[pair[1]][:4]))
    # controls: two other pairs with one bare bracketing at n0 = 8, the same way against the other way
    ctl = [("(x,(x,(x,(x,(x,(x,x))))))", "(x,(x,(x,(x,((x,x),x)))))"), ("((x,x),(x,(x,(x,(x,x)))))", "((x,x),(x,(x,((x,x),x))))")]
    out["controls"] = []
    for s1, s2 in ctl:
        r = []
        for s in (s1, s2):
            T, n0 = parse(s)
            r.append(run(n0, T, 4)[-1]["lam"])
        out["controls"].append({"pair": [s1, s2], "same_at_n0+4": r[0] == r[1]})
        print("tie control", s1, s2, r[0] == r[1], file=sys.stderr, flush=True)
    return out


def odd_sets(S, n, n0):
    m = n0 - 1
    low = (1 << n0) - 1
    ext = defaultdict(list)
    for s in S:
        ext[s & low].append(s)
    pref = [0] + [(1 << k) - 1 for k in range(1, m + 1)] + [low]
    if len(S) != 2 * n0 or any(len(ext[P]) != 1 for P in pref):
        return None
    return [tuple(i for i in range(n0) if ((ext[pref[i]][0] >> u) & 1) != ((ext[pref[i + 1]][0] >> u) & 1)) for u in range(n0, n)]


def signature(n0, T, depth):
    lv = run(n0, T, depth, keep_levels=True)
    sig = []
    for L in lv:
        mass = Counter()
        for (S, G), p in L["dist"].items():
            o = odd_sets(S, L["n"], n0)
            mass["state added" if o is None else ("line" if not o else f"largest {max(map(len, o))}")] += p
        sig.append((L["labelled"], tuple(sorted((k, str(v)) for k, v in mass.items()))))
    return tuple(sig)


def incidence(T):
    H = nx.Graph()
    for i, k in enumerate(T):
        H.add_node(("k", i), t="k")
        for v in k:
            H.add_node(("d", v), t="d")
            H.add_edge(("k", i), ("d", v))
    return H


def part_meet(n0=8, depth=3):
    m = n0 - 1
    seen, reps = set(), []
    for T in bracketings(0, m):
        key = tuple(sorted(T))
        mir = tuple(sorted((m - k[2], m - k[1], m - k[0]) for k in T))
        if key in seen or mir in seen:
            continue
        seen.add(key)
        reps.append(T)
    groups = []
    for T in reps:
        H = incidence(T)
        for g in groups:
            if nx.is_isomorphic(g[0], H, node_match=lambda a, b: a["t"] == b["t"]):
                g[1].append(T)
                break
        else:
            groups.append((H, [T]))
    print("meet", n0, len(reps), "presentations up to mirror,", len(groups), "meeting patterns", file=sys.stderr, flush=True)
    sigs = []
    for H, Ts in groups:
        s = {signature(n0, T, depth) for T in Ts}
        sigs.append(s)
        print("meet group", len(Ts), "presentations,", len(s), "signatures", file=sys.stderr, flush=True)
    flat = [x for s in sigs for x in s]
    return {"n0": n0, "depth": depth, "presentations_up_to_mirror": len(reps), "meeting_patterns": len(groups),
            "groups_with_one_signature": sum(1 for s in sigs if len(s) == 1),
            "group_sizes_and_signatures": [[len(Ts), len(s)] for (H, Ts), s in zip(groups, sigs)],
            "distinct_signatures": len(set(flat)),
            "signatures_shared_between_groups": len(flat) - len(set(flat))}


def part_extra():
    """(a) The six-starts with this engine: labelled (S, G) bases at n = 10 (the study: 13,368 and 13,364) and two orders at 8, 9.
    (b) A100, the fewest-knot population: add one redundant knot (any a < c < b not present; the states stay the line's) to each
    five-start and read the chance of two orders at n = 7 against the fewest-knot value."""
    out = {"six_starts": {}, "one_redundant_knot": {}}
    six = {"fan6": ((0, 1, 2), (0, 2, 3), (0, 3, 4), (0, 4, 5)), "nonfan6": ((1, 2, 3), (1, 3, 4), (0, 1, 4), (0, 4, 5))}
    for name, T in six.items():
        lv = run(6, T, 4)
        out["six_starts"][name] = {"labelled_at_10": lv[-1]["labelled"], "two_at_8": str(lv[2]["two"]), "two_at_9": str(lv[3]["two"]),
                                   "two_at_10": str(lv[4]["two"])}
        print("extra six", name, json.dumps(out["six_starts"][name]), file=sys.stderr, flush=True)
    for name, T in FIVE.items():
        base_two = run(5, T, 2)[-1]["two"]
        vals = Counter()
        for k in itertools.combinations(range(5), 3):
            if k in T:
                continue
            T2 = T + (k,)
            vals[str(run(5, T2, 2)[-1]["two"])] += 1
        out["one_redundant_knot"][name] = {"fewest_knot_value": str(base_two), "with_one_more_knot": dict(vals)}
        print("extra redundant", name, json.dumps(out["one_redundant_knot"][name]), file=sys.stderr, flush=True)
    return out


if __name__ == "__main__":
    part = sys.argv[1]
    res = {"thm1": part_thm1, "five": part_five, "tie": part_tie, "meet": part_meet, "extra": part_extra}[part]()
    print(json.dumps(res, indent=1, default=str))
