"""Exact counting of allowed words of a structure by variable elimination (independent of allocations)."""

from itertools import product

import numpy as np

from engine import LAWS, lawful_word


def relation_table(law, size, dtype=np.int64):
    table = np.zeros((2,) * size, dtype=dtype)
    for word in product((0, 1), repeat=size):
        table[word] = int(lawful_word(law, word))
    return table


def count_words(stars, law, big=False):
    """Number of 0/1 assignments to all distinctions making every knot lawful (exact, Python int).

    ``big`` keeps every table as Python integers (needed beyond 62 distinctions)."""
    assert law in LAWS
    dtype = object if big else np.int64
    names = sorted({d for row in stars for d in row})
    index = {d: i for i, d in enumerate(names)}
    factors = [(tuple(index[d] for d in row), relation_table(law, len(row), dtype)) for row in stars]
    remaining = set(index.values())
    while remaining:
        # greedy: eliminate the variable whose merged factor is smallest
        best, best_width = None, None
        for v in remaining:
            scope = set()
            for vs, _ in factors:
                if v in vs:
                    scope.update(vs)
            width = len(scope)
            if best is None or width < best_width:
                best, best_width = v, width
        v = best
        touching = [(vs, t) for vs, t in factors if v in vs]
        rest = [(vs, t) for vs, t in factors if v not in vs]
        scope = sorted(set().union(*(set(vs) for vs, _ in touching)) - {v})
        letters = {x: i for i, x in enumerate(sorted(set(scope) | {v}))}
        args = []
        for vs, t in touching:
            args.append(t)
            args.append([letters[x] for x in vs])
        args.append([letters[x] for x in scope])
        merged = np.einsum(*args)
        rest.append((tuple(scope), merged))
        factors = rest
        remaining.discard(v)
    total = 1
    for vs, t in factors:
        assert vs == ()
        total *= int(t)
    return total


def brute_count(stars, law):
    names = sorted({d for row in stars for d in row})
    assert len(names) <= 22
    index = {d: i for i, d in enumerate(names)}
    n = len(names)
    x = np.arange(1 << n, dtype=np.uint64)
    ok = np.ones(x.shape, dtype=bool)
    for row in stars:
        mask = np.uint64(sum(1 << index[d] for d in row))
        ones = np.bitwise_count(x & mask)
        ok &= (ones % 2 == 0) if law == "parity" else ((ones > 0) & (ones < len(row)))
    return int(ok.sum())
