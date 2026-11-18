"""Post hoc (written after the freeze, not a prediction): the five-start chains (same way, the end; other way, next to an end),
split by the first two fills, with the chance of two orders after the third and fourth new distinctions.

  ../../../.venv/bin/python -B posthoc.py > ../../../artifacts/MEET-ORDERS-20261118-001B/MEET-ORDERS-20261118-001B-E001_census/posthoc.txt
"""
import sys
sys.path.insert(0, '.')
from fractions import Fraction
from collections import defaultdict
import melib as M
ST = {"end": [(0,1,2),(0,2,3),(0,3,4)], "next": [(1,2,3),(0,1,3),(0,3,4)]}
DEPTH = {"end": {(0,1,2):"A",(0,2,3):"B",(0,3,4):"C"}, "next": {(1,2,3):"A",(0,1,3):"B",(0,3,4):"C"}}
def run_from(S, n, G, steps):
    dist = {M.canon(S, n, G): Fraction(1)}
    for _ in range(steps):
        new = defaultdict(Fraction)
        for (S1, G1), p in dist.items():
            for (S2, G2), q in M.step_dist(S1, n, G1).items():
                new[M.canon(S2, n + 1, G2)] += p * q
        dist = new; n += 1
    return sum(p for (S1, G1), p in dist.items() if M.two_orders(M.measure(S1, n)))
for name, K in ST.items():
    S0, G0 = M.base(5, K), M.pairs_of(K)
    parent, children, within, holders = M.relations(K)
    _, top0 = M.zero_cost_top(S0, 5, G0)
    for a0, a1, ks in top0:
        first = [k for k in K if M.old_pairs(ks, 5) == M.pairs_of([k])][0]
        S1, G1 = M.apply(S0, 5, a0, a1), G0 | M.pairs_of(ks)
        _, top1 = M.zero_cost_top(S1, 6, G1)
        for b0, b1, ks2 in top1:
            S2, G2 = M.apply(S1, 6, b0, b1), G1 | M.pairs_of(ks2)
            odd = M.odd_sets(S2, 7, 5)
            # describe the second fill by its odd set relative to the knots' depths
            lab = tuple(sorted(odd[1]))
            v8 = run_from(S2, 7, G2, 1); v9 = run_from(S2, 7, G2, 2)
            print(name, "first", DEPTH[name][first], "second odd set", lab, "two orders at 7:", M.two_orders(M.measure(S2,7)), "at 8:", v8, "at 9:", v9)
