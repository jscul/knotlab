"""Finite checks for the parity argument and the guessed-setting examples."""
import argparse
from collections import Counter
from fractions import Fraction
from itertools import combinations, product
from time import perf_counter


def examples():
    result = {}
    for n in (2, 3):
        settings = list(product(range(2), repeat=n))
        target = lambda st: int(sum(st) == 2)
        worlds = [(s, v) for s in settings for v in settings if sum(v) % 2 == target(s)]
        projections = {}
        for s in settings:
            survivors = [v for guess, v in worlds if guess == s]
            for size in range(1, n):
                for keep in combinations(range(n), size):
                    def rec(v):
                        return tuple((s[i], v[i]) for i in keep)
                    hist = Counter(rec(v) for v in survivors)
                    key = keep, tuple(s[i] for i in keep)
                    assert projections.setdefault(key, hist) == hist
            assert all(sum(v) % 2 == target(s) for v in survivors)
        result[n] = (len(worlds), len(survivors))
    # Nonzero local completion multiplicities, three on a match and one otherwise.
    corr = []
    for x, y in product(range(2), repeat=2):
        mass = Counter()
        for p, r, q in product(range(2), repeat=3):
            s = q ^ (p*r)
            mass[q ^ s] += (3 if x == p else 1) * (3 if y == r else 1)
        corr.append(Fraction(mass[0] - mass[1], mass.total()))
    print("guessing: (worlds, survivors per setting)", result)
    print("positive weights: correlations", *corr, "CHSH", sum(corr[:3]) - corr[3])


def subspaces(n):
    found = {frozenset([0])}
    todo = list(found)
    for space in todo:
        for v in range(1, 1 << n):
            if v not in space:
                larger = space | {w ^ v for w in space}
                if larger not in found:
                    todo.append(larger)
                    found.add(larger)
    return sorted(found, key=lambda a: (len(a), sorted(a)))


def mermin(dims, prefix):
    n = sum(dims)
    universe = range(1 << n)
    def part(v, i):
        return (v >> sum(dims[:i])) % (1 << dims[i])
    def mask(values):
        return sum(1 << v for v in values)
    local = [[mask(v for v in universe if part(v, i) in s) for s in subspaces(d)]
             for i, d in enumerate(dims)]
    score_settings = [(0, 0, 0), (0, 1, 1), (1, 0, 1), (1, 1, 0)]
    settings = list(product(range(2), repeat=3))
    flips = {tuple((-1)**(int(any(st)) + sum(r[2*i+b] for i,b in enumerate(st)))
                   for st in score_settings) for r in product(range(2), repeat=6)}
    outcome_masks = [(fs, mask(v for v in universe if
                               sum((f & part(v, i)).bit_count() for i, f in enumerate(fs)) % 2))
                     for fs in product(*(range(1,1<<d) for d in dims))]
    functionals = dict(outcome_masks)
    readings = [tuple(functionals[tuple(f[i][s[i]] for i in range(3))] for s in score_settings)
                for f in product(*(list(product(range(1,1<<d), repeat=2)) for d in dims))]
    marginals = {}
    def support(m, keep):
        key = m, keep
        if key not in marginals:
            marginals[key] = frozenset(tuple(part(v, i) for i in keep) for v in universe if m >> v & 1)
        return marginals[key]
    best = passed = examined = 0
    for w in subspaces(n)[:prefix]:
        wm = mask(w)
        for rules in product(*(list(product(side, repeat=2)) for side in local)):
            vs = {s: wm & rules[0][s[0]] & rules[1][s[1]] & rules[2][s[2]] for s in settings}
            examined += 1
            # Pair supports imply the single supports by forgetting one more reader.
            agree = all(support(vs[s], keep) == support(vs[tuple(s[i] if i in keep else 1-s[i]
                          for i in range(3))], keep) for keep in combinations(range(3),2)
                        for s in settings if s[3-sum(keep)] == 0)
            if not agree:
                continue
            passed += 1
            for outcomes in readings:
                # A nonconstant homogeneous bit is balanced; a constant bit is zero.
                es = tuple(int(not (vs[s] & f)) for s,f in zip(score_settings, outcomes))
                best = max(best, max(sum(a*b for a,b in zip(signs, es)) for signs in flips))
    print("dimensions", dims, "rule tuples", examined, "passing support", passed,
          "best win", Fraction(1,2) + Fraction(best,8))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--pilot", action="store_true")
    args = parser.parse_args()
    begin = perf_counter()
    examples()
    for dims in [(1,1,1), (2,1,1)]:
        mermin(dims, 1 if args.pilot else None)
    print("seconds", round(perf_counter()-begin, 3))
