"""Check the sparse bounds and equality cases using the crossing instruction."""

from collections import defaultdict
from itertools import combinations, permutations
from math import comb
import json


def require(condition, message):
    if not condition:
        raise ValueError(message)


def state(p, intercept, slope):
    """Encode the original pair (x, y) with y = x + slope."""
    return p * intercept + (intercept + slope) % p


def value(p, index, column):
    x, y = divmod(index, p)
    return (x + column * (y - x)) % p


def mask(indices):
    result = 0
    for index in indices:
        result |= 1 << index
    return result


def crossing_signatures(p):
    signatures = []
    for index in range(p * p):
        original = divmod(index, p)
        left, right = original
        observed = 0
        for k in range(p):
            require(left == value(p, index, k), "first strand disagrees with the word")
            require(right == value(p, index, k + 1), "second strand disagrees")
            observed |= 1 << (k * p + left)
            left, right = right, (2 * right - left) % p
        require((left, right) == original, "p forward crossings did not return the pair")
        signatures.append(observed)
    return signatures


def read_table(indices, signatures):
    observed = 0
    for index in indices:
        observed |= signatures[index]
    return observed


def compatible(observed, signatures):
    return mask(i for i, word in enumerate(signatures) if word & observed == word)


def check_sparse_tables(p, signatures):
    count = 0
    for size in range(p):
        for table in combinations(range(p * p), size):
            observed = read_table(table, signatures)
            require(compatible(observed, signatures) == mask(table), "outside state covered")
            for omit in range(size):
                rest = read_table(table[:omit] + table[omit + 1 :], signatures)
                require(rest != observed, "a sparse table member had no private query")
            count += 1
    return count


def pairs_from_derangements(p, f, g, signatures):
    """Reconstruct common sets from the two differing affine functions."""
    columns = tuple(k for k in range(p) if value(p, f, k) != value(p, g, k))
    if len(columns) == p:
        return set()
    require(len(columns) == p - 1, "differing nonparallel functions must agree once")
    pairs = set()
    for images in permutations(columns):
        if any(a == b for a, b in zip(columns, images)):
            continue
        common = set()
        for a, b in zip(columns, images):
            fa = value(p, f, a)
            slope = (value(p, g, b) - fa) * pow((b - a) % p, -1, p) % p
            intercept = (fa - a * slope) % p
            common.add(state(p, intercept, slope))
        require(len(common) == p - 1 and f not in common and g not in common,
                "connectors failed to give the required common states")
        require(read_table(common | {f}, signatures) == read_table(common | {g}, signatures),
                "derangement constructed distinguishable tables")
        pair = tuple(sorted((mask(common | {f}), mask(common | {g}))))
        require(pair not in pairs, "two derangements gave the same unordered tie")
        pairs.add(pair)
    return pairs


def derangement_count(n):
    previous, current = 1, 0
    for size in range(2, n + 1):
        previous, current = current, (size - 1) * (previous + current)
    return previous if n == 0 else current


def check_equal_size(p, signatures):
    groups = defaultdict(list)
    for table in combinations(range(p * p), p):
        groups[read_table(table, signatures)].append(mask(table))

    disjoint, one_replaced = set(), set()
    for tables in groups.values():
        for left, right in combinations(tables, 2):
            shared = (left & right).bit_count()
            pair = tuple(sorted((left, right)))
            if shared == 0:
                disjoint.add(pair)
            if shared == p - 1:
                one_replaced.add(pair)

    classes = sorted(mask(state(p, x, slope) for x in range(p)) for slope in range(p))
    require(disjoint == set(combinations(classes, 2)), "disjoint equality cases differ")
    all_queries = (1 << (p * p)) - 1
    require(set(groups[all_queries]) == set(classes), "unexpected fully visible table")

    predicted = set()
    for f, g in combinations(range(p * p), 2):
        predicted.update(pairs_from_derangements(p, f, g, signatures))
    require(one_replaced == predicted, "shared-state equality cases differ")
    require(len(one_replaced) == comb(p, 2) * p * p * derangement_count(p - 1),
            "shared-state tie count differs")
    return len(disjoint), len(one_replaced)


def check_controls(p, signatures):
    pencil = tuple(state(p, 0, d) for d in range(p))
    only_pencil = compatible(read_table(pencil, signatures), signatures)
    require(only_pencil == mask(pencil), "threshold-sized uniquely readable table grew")
    for removed in pencil:
        smaller = [i for i in pencil if i != removed]
        require(read_table(smaller, signatures) != read_table(pencil, signatures),
                "pencil member was redundant")

    parallel = [state(p, x, 0) for x in range(p)]
    extra = state(p, 0, 1)
    require(extra not in parallel, "added state must be new")
    require(read_table(parallel, signatures) == read_table(parallel + [extra], signatures),
            "size-p and size-(p+1) tables should tie")
    joint_pin = 1 << extra
    require(bool(joint_pin & mask(parallel)) != bool(joint_pin & mask(parallel + [extra])),
            "joint pin failed to separate the two tied tables")
    require(read_table([], signatures) != read_table([extra], signatures),
            "one-strand tests must detect nonemptiness")

    if p >= 3:
        common = [state(p, x, 0) for x in range(1, p)]
        observed = read_table(common + [state(p, 0, 1)], signatures)
        require(observed == read_table(common + [state(p, 0, 2)], signatures),
                "shared nonzero constants should hide the changed slope")
        require(observed != read_table(parallel, signatures), "shared tie should omit a query")


def main():
    census = []
    for p in (2, 3, 5):
        signatures = crossing_signatures(p)
        sparse = check_sparse_tables(p, signatures)
        disjoint, shared = check_equal_size(p, signatures)
        check_controls(p, signatures)
        census.append({
            "prime": p,
            "sparse_tables": sparse,
            "threshold_tables": comb(p * p, p),
            "disjoint_ties": disjoint,
            "single_replacement_ties": shared,
        })

    # One prime beyond the exhaustive fields. Try every normalized replacement
    # and every table size used by the controls without enumerating 49 choose 7.
    p = 7
    signatures = crossing_signatures(p)
    check_controls(p, signatures)
    normalized = pairs_from_derangements(p, state(p, 0, 0), state(p, 0, 1), signatures)
    require(len(normalized) == derangement_count(p - 1), "larger-field count differs")
    print(json.dumps({
        "status": "passed",
        "exhaustive": census,
        "larger_prime": p,
        "normalized_single_replacement_ties": len(normalized),
    }))


if __name__ == "__main__":
    main()
