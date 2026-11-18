"""Gate checks for MEET-ORDERS-20261118-001B (run before the freeze; all must pass).

  ../../../.venv/bin/python -B checks.py
"""
import itertools
import random
import sys
from fractions import Fraction

import networkx as nx

sys.path.insert(0, ".")
import melib as M

FAILS = []


def check(name, ok, detail=""):
    print(("PASS " if ok else "FAIL ") + name + (" -- " + str(detail) if detail else ""), flush=True)
    if not ok:
        FAILS.append(name)


# G1. Exact values of the referee of KNOT-CAP-20261117-001 (fresh code there, nothing shared with this engine).
FAN5 = [(0, 1, 2), (0, 2, 3), (0, 3, 4)]
MID5 = [(0, 1, 2), (0, 2, 4), (2, 3, 4)]
FAN6 = [(0, 1, 2), (0, 2, 3), (0, 3, 4), (0, 4, 5)]
NONFAN6 = [(1, 2, 3), (1, 3, 4), (0, 1, 4), (0, 4, 5)]
lf, lm = M.exact(5, FAN5, 8), M.exact(5, MID5, 8)
check("G1a five-starts 5/12, 11/18 at 7; 173/6552, 233/2457 at 8",
      [L["two"] for L in lf[2:]] == [Fraction(5, 12), Fraction(173, 6552)]
      and [L["two"] for L in lm[2:]] == [Fraction(11, 18), Fraction(233, 2457)])
la, lb = M.exact(6, FAN6, 9), M.exact(6, NONFAN6, 9)
check("G1b six-starts 51/140 at 8 and 9409/339822 at 9 from both",
      [L["two"] for L in la[2:]] == [Fraction(51, 140), Fraction(9409, 339822)] == [L["two"] for L in lb[2:]])

# G2. The pruned move enumeration equals a brute-force one (every combination of 1..3 candidate knots, the referee's checks)
# on random bases grown by KF3 with random pair sets.


def brute_moves(S, n, G):
    cands, O, Z, full = M.candidates(S, n, G)
    N = len(S)
    ties = {(Z[u], O[u]) for u in range(n)}
    out = []
    for r in (1, 2, 3):
        for combo in itertools.combinations(range(len(cands)), r):
            a0 = a1 = full
            for c in combo:
                a0 &= full ^ cands[c][2]
                a1 &= full ^ cands[c][1]
            if (a0 | a1) != full or (a0, a1) in ties or M.pc(a0) + M.pc(a1) >= 2 * N:
                continue
            red = False
            for d in combo:
                b0 = b1 = full
                for c in combo:
                    if c != d:
                        b0 &= full ^ cands[c][2]
                        b1 &= full ^ cands[c][1]
                if (b0, b1) == (a0, a1):
                    red = True
                    break
            if not red:
                out.append((a0, a1, tuple(cands[c][0] for c in combo)))
    return sorted(out)


rng = random.Random("MEET-ORDERS-G2")
agree = 0
for trial in range(40):
    T = rng.choice(M.bracketings(0, rng.choice([4, 5])))
    n = len(T) + 2
    S, G = M.base(n, T), M.pairs_of(T)
    for step in range(rng.choice([0, 1, 2])):
        _, top = M.zero_cost_top(S, n, G)
        a0, a1, ks = rng.choice(top)
        S, G = M.apply(S, n, a0, a1), G | M.pairs_of(ks)
        n += 1
    extra = rng.sample([p for p in itertools.combinations(range(n), 2) if p not in G], 2)
    G2 = G | frozenset(extra)
    agree += sorted(M.moves(S, n, G2)) == brute_moves(S, n, G2)
check("G2 pruned moves = brute force on 40 random bases", agree == 40, f"{agree}/40")

# G3. Canonical form: invariant under random renaming, and separates non-isomorphic pairs (checked with networkx).
rng = random.Random("MEET-ORDERS-G3")
inv = 0
sep_ok = 0
samples = []
for trial in range(30):
    T = rng.choice(M.bracketings(0, 5))
    n = 6
    S, G = M.base(n, T), M.pairs_of(T)
    for step in range(2):
        _, top = M.zero_cost_top(S, n, G)
        a0, a1, ks = rng.choice(top)
        S, G = M.apply(S, n, a0, a1), G | M.pairs_of(ks)
        n += 1
    perm = list(range(n))
    rng.shuffle(perm)
    S2 = tuple(sorted(sum(1 << perm[u] for u in range(n) if (s >> u) & 1) for s in S))
    G2 = frozenset((min(perm[u], perm[v]), max(perm[u], perm[v])) for u, v in G)
    inv += M.canon(S, n, G) == M.canon(S2, n, G2)
    samples.append((S, n, G))


def as_graph(S, n, G):
    H = nx.Graph()
    for u in range(n):
        H.add_node(("d", u), kind="d")
    for i, s in enumerate(S):
        H.add_node(("s", i), kind="s")
        for u in range(n):
            if (s >> u) & 1:
                H.add_edge(("s", i), ("d", u), kind="in")
    for u, v in G:
        H.add_edge(("d", u), ("d", v), kind="pair")
    return H


pairs = 0
for (A, B) in itertools.combinations(samples[:14], 2):
    if A[1] != B[1]:
        continue
    iso = nx.is_isomorphic(as_graph(*A), as_graph(*B), node_match=lambda x, y: x["kind"] == y["kind"],
                           edge_match=lambda x, y: x["kind"] == y["kind"])
    sep_ok += iso == (M.canon(*A) == M.canon(*B))
    pairs += 1
check("G3a canonical form invariant under renaming (30 bases)", inv == 30, f"{inv}/30")
check("G3b canonical form equality = isomorphism (networkx)", sep_ok == pairs, f"{sep_ok}/{pairs}")

# G4. Labelled and canonical exact runs agree (two orders and number of orders) on the five-starts to n = 8.
ok = True
for T in (FAN5, MID5, [(0, 1, 3), (0, 3, 4), (1, 2, 3)]):
    A, B = M.exact(5, T, 8, use_canon=True), M.exact(5, T, 8, use_canon=False)
    ok &= all(x["two"] == y["two"] and x["lam"] == y["lam"] for x, y in zip(A, B))
check("G4 labelled = canonical exact runs (three five-starts to n = 8)", ok)

# G5. Bracketings: Catalan counts; the mirror and the nesting strings behave.
cat = [1, 1, 2, 5, 14, 42, 132, 429]
check("G5a bracketings counted by Catalan(n - 2), n = 3..9", [len(M.bracketings(0, n - 1)) for n in range(3, 10)] == cat[1:8])
check("G5b fan of five is a chain, middle five is balanced",
      M.nesting(FAN5, 0, 4) == "(((x,x),x),x)" == M.nesting([(0, 1, 3), (0, 3, 4), (1, 2, 3)], 0, 4)
      and M.nesting(MID5, 0, 4) == "((x,x),(x,x))")
check("G5c every bracketing presents the line (n = 5..8)",
      all(M.base(n, T) == M.base(n, M.bracketings(0, n - 1)[0]) and len(M.base(n, T)) == 2 * n
          for n in range(5, 9) for T in M.bracketings(0, n - 1)))

# G6. The formula: chain closed form; and a mutant (both child moves keeping two orders) must disagree somewhere.
check("G6a chain closed form = formula, n = 5..12",
      all(M.formula([(0, i, i + 1) for i in range(1, n - 1)]) == M.chain_formula(n) for n in range(5, 13)))


def mutant(knots):
    n0 = len(knots) + 2
    parent, children, within, holders = M.relations(knots)
    tot = Fraction(0)
    for k in knots:
        inc = len(knots) - 1 - len(within[k]) - len(holders[k])
        p = 1 if k in parent else 0
        c = len(children[k])
        tot += Fraction(inc + 2 * p + 2 * c, (n0 - 3) + 2 * (p + c))
    return tot / len(knots)


def exact2(knots):
    return M.exact(len(knots) + 2, knots, len(knots) + 4)[2]["two"]


check("G6b formula = exact on every presentation of 5 and 6", all(M.formula(T) == exact2(T) for n in (5, 6) for T in M.bracketings(0, n - 1)))
check("G6c the mutant formula disagrees with exact somewhere", any(mutant(T) != exact2(T) for T in M.bracketings(0, 4)))

# G7. Lemma B classification on every presentation of 4..7 and every first knot (the frozen run repeats it to 11).
ok = all(M.classify_second_step(T, k)["ok"] for n in range(4, 8) for T in M.bracketings(0, n - 1) for k in T)
check("G7 Lemma B classification holds for n0 = 4..7", ok)

# G8. Lemma C's two-order criterion against the measured number of orders on every labelled base of the three five-starts to
# n = 8 whose new distinctions are fills of triples; a mutant criterion (no exception at a shared middle) must disagree.
import job


def mutant_criterion(sets):
    return bool(sets) and not any(x < v < z for (u, v, w) in sets for (x, y, z) in sets if (u, v, w) != (x, y, z))


agree = total = mdis = 0
for T in (FAN5, MID5, [(0, 1, 3), (0, 3, 4), (1, 2, 3)]):
    for L in M.exact(5, T, 8, use_canon=False):
        for (S, G), q in L["dist"].items():
            sets = M.odd_sets(S, L["n"], 5)
            if sets is not None and all(len(s) == 3 for s in sets):
                total += 1
                truth = M.two_orders(M.measure(S, L["n"]))
                agree += job.criterion(sets) == truth
                mdis += mutant_criterion(sets) != truth
check("G8a Lemma C criterion = measured two orders (five-starts, labelled, to n = 8)", agree == total, f"{agree}/{total}")
check("G8b the mutant criterion disagrees somewhere", mdis > 0, f"{mdis} disagreements")

print("ALL PASS" if not FAILS else "FAILED: " + ", ".join(FAILS))
sys.exit(1 if FAILS else 0)
