"""Allocations of loose distinctions to children, and exact old-word distributions under each.

An allocation at one funded round decides, for every knot u, which of u's named loose distinctions is
paid to which of the births that contain u.  The round's births (parents and fresh counts) are fixed by
the holdings; only the naming of the paid distinctions varies.

For one start, one law and one allocation the exact objects are, for an old assignment x of all
distinctions present before the round:

    old(x)    1 if x is an allowed word of the old structure
    ext(x)    number of ways to give the new distinctions values so that every child is lawful
              = product over children c of comp_c(x), comp_c depending only on the old inputs of c
    uniform present words      weight(x) = old(x) * ext(x)
    old-word weighting         weight(x) = old(x) * [ext(x) >= 1]   (each old word has equal weight,
                                divided equally among its extensions, so its mass is 1/(old count))

Both are exact integer weights; their normalised forms are the joint distributions of ALL old
distinctions.  Because comp_c depends only on the loose (paid) distinctions, the distribution of every
other old distinction given the loose ones is the same under every allocation, so the total variation
between two allocations equals the total variation of the marginals on the loose distinctions.  The
script that uses this reduction also verifies it against the full joint on small structures.
"""

from collections import Counter
from itertools import permutations, product
from math import factorial, prod

import numpy as np

from engine import births_of_knot, canonical_allocation, holders_of, loose_of

CHUNK = 1 << 22


# ----------------------------------------------------------------------------------------------
# Allocation classes
# ----------------------------------------------------------------------------------------------

def knot_classes(plan, knot):
    """Allocations of one knot's loose distinctions, with identical unary copies identified.

    Returns the list of orders (lists of distinctions in birth order for that knot).
    """
    loose = plan.loose[knot]
    own = births_of_knot(plan)[knot]
    group_slots = [i for i in own if len(plan.parents[i]) > 1]
    unary_slots = [i for i in own if len(plan.parents[i]) == 1]
    assert len(own) == len(loose) and own == group_slots + unary_slots
    result = []
    for chosen in permutations(loose, len(group_slots)):
        rest = sorted(set(loose) - set(chosen))
        result.append(list(chosen) + rest)
    return result


def raw_count(plan, knot):
    return factorial(len(plan.loose[knot]))


def all_classes(plan):
    """Cartesian product over the knots that have loose distinctions: dict knot -> order."""
    knots = [k for k, ds in plan.loose.items() if ds]
    lists = [knot_classes(plan, k) for k in knots]
    for combo in product(*lists):
        yield dict(zip(knots, combo, strict=True))


def class_count(plan):
    return prod(len(knot_classes(plan, k)) for k, ds in plan.loose.items() if ds)


def raw_total(plan):
    return prod(raw_count(plan, k) for k, ds in plan.loose.items() if ds)


def children_inputs(plan, allocation):
    """For every birth the tuple of paid distinctions, in parent order."""
    own = births_of_knot(plan)
    pos = {k: {birth: j for j, birth in enumerate(own[k])} for k in own}
    return [tuple(allocation[p][pos[p][i]] for p in ps) for i, ps in enumerate(plan.parents)]


def relabelling(plan, sigma, tau):
    """The permutation of old loose distinctions that carries allocation sigma onto tau."""
    a, b = children_inputs(plan, sigma), children_inputs(plan, tau)
    pi = {}
    for ins, outs in zip(a, b, strict=True):
        for x, y in zip(ins, outs, strict=True):
            assert pi.setdefault(x, y) == y
    assert sorted(pi) == sorted(pi.values())
    return pi


# ----------------------------------------------------------------------------------------------
# Old words
# ----------------------------------------------------------------------------------------------

def structure_columns(stars):
    """Sorted distinction names, and the loose ones."""
    owners = holders_of(stars)
    names = sorted(owners)
    loose = sorted(d for d, hs in owners.items() if len(hs) == 1)
    return names, loose


def _allowed_mask(x, rows_masks, law):
    ok = np.ones(x.shape, dtype=bool)
    for mask, size in rows_masks:
        ones = np.bitwise_count(x & np.uint64(mask))
        ok &= (ones % 2 == 0) if law == "parity" else ((ones > 0) & (ones < size))
    return ok


def loose_marginal_counts(stars, law):
    """N(y): number of allowed old words with the loose distinctions equal to y (y indexed by the
    sorted loose distinctions, bit j = j-th loose distinction), by exhaustive enumeration."""
    names, loose = structure_columns(stars)
    n = len(names)
    assert n <= 30, "enumeration cap"
    pos = {d: i for i, d in enumerate(names)}
    rows_masks = [(sum(1 << pos[d] for d in row), len(row)) for row in stars]
    counts = np.zeros(1 << len(loose), dtype=np.int64)
    total = 1 << n
    for start in range(0, total, CHUNK):
        x = np.arange(start, min(start + CHUNK, total), dtype=np.uint64)
        ok = _allowed_mask(x, rows_masks, law)
        xs = x[ok]
        y = np.zeros(xs.shape, dtype=np.int64)
        for j, d in enumerate(loose):
            y |= ((xs >> np.uint64(pos[d])) & np.uint64(1)).astype(np.int64) << j
        counts += np.bincount(y, minlength=1 << len(loose))
    return counts


def full_allowed_words(stars, law):
    """All allowed old words as a uint64 array (small structures only)."""
    names, _ = structure_columns(stars)
    n = len(names)
    assert n <= 26
    pos = {d: i for i, d in enumerate(names)}
    rows_masks = [(sum(1 << pos[d] for d in row), len(row)) for row in stars]
    out = []
    total = 1 << n
    for start in range(0, total, CHUNK):
        x = np.arange(start, min(start + CHUNK, total), dtype=np.uint64)
        out.append(x[_allowed_mask(x, rows_masks, law)])
    return np.concatenate(out), names


def child_factor(law, bits, fresh_count):
    """comp_c as an int64 array, from the list of 0/1 input arrays of the child."""
    if fresh_count == 0:
        ones = sum(b.astype(np.int64) for b in bits)
        return (ones % 2 == 0).astype(np.int64) if law == "parity" else ((ones > 0) & (ones < len(bits))).astype(np.int64)
    if law == "parity":
        return np.full(bits[0].shape, 2 ** (fresh_count - 1), dtype=np.int64)
    equal = np.ones(bits[0].shape, dtype=bool)
    for b in bits[1:]:
        equal &= b == bits[0]
    return (2 ** fresh_count - equal.astype(np.int64))


def weights_on_loose(plan, allocation, law, loose_names):
    """ext(y) on the 2^L loose assignments (y indexed as in loose_marginal_counts)."""
    size = 1 << len(loose_names)
    y = np.arange(size, dtype=np.int64)
    column = {d: ((y >> j) & 1) for j, d in enumerate(loose_names)}
    ins = children_inputs(plan, allocation)
    ext = np.ones(size, dtype=np.int64)
    for inputs, f in zip(ins, plan.fresh_counts, strict=True):
        ext = ext * child_factor(law, [column[d] for d in inputs], f)
    return ext


def weights_on_words(plan, allocation, law, words, names):
    """ext(x) on explicit old words (uint64 array)."""
    pos = {d: i for i, d in enumerate(names)}
    ins = children_inputs(plan, allocation)
    ext = np.ones(words.shape, dtype=np.int64)
    for inputs, f in zip(ins, plan.fresh_counts, strict=True):
        bits = [((words >> np.uint64(pos[d])) & np.uint64(1)).astype(np.int64) for d in inputs]
        ext = ext * child_factor(law, bits, f)
    return ext


def tv_from_weights(a, b):
    """Exact total variation between two non-negative integer weight vectors (normalised).

    Returns (numerator, denominator) with TV = numerator/denominator; uses Python integers.
    """
    za, zb = int(a.sum()), int(b.sum())
    assert za > 0 and zb > 0
    if za == zb:
        return int(np.abs(a - b).sum()), 2 * za
    # general case: sum |a*zb - b*za| / (2 za zb); a, b below 2^40 so use object arithmetic on uniques
    pairs = Counter(zip(a.tolist(), b.tolist()))
    num = sum(abs(x * zb - y * za) * c for (x, y), c in pairs.items())
    return num, 2 * za * zb
