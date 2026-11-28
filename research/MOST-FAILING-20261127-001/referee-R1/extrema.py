"""Exact extrema and their signs by a trellis of attainable parity sums.

Each holder type is replaced by the parity of its chosen pairs. We keep a
partial sum only if the unused types can still complete all checks. Appending a
final, cost-free sign bit makes the last two possible sums even and odd.
"""

from itertools import combinations
from math import comb, isqrt


def _column_coordinates(columns):
    """Express columns in a basis built from right to left.

    The second item for a column is the new basis bit it introduces, or zero.
    That bit must vanish as soon as this column has been processed.
    """
    basis = {}
    result = []
    for column in reversed(columns):
        residual = column
        coordinates = 0
        introduced = 0
        while residual:
            pivot = residual.bit_length()
            if pivot not in basis:
                introduced = 1 << len(basis)
                basis[pivot] = (residual, introduced)
                coordinates ^= introduced
                break
            vector, bit = basis[pivot]
            residual ^= vector
            coordinates ^= bit
        result.append((coordinates, introduced))
    return result[::-1]


def _volume(columns):
    """Count feasible partial sums across all cuts in this processing order."""
    prefix = _column_coordinates(columns[::-1])[::-1]
    suffix = _column_coordinates(columns)
    # Initially the prefix has rank zero and the suffix has full rank. The
    # logarithm of the intersection size is rank(prefix) + rank(suffix) - rank.
    width = 0
    states = 1
    for (_, enters), (_, leaves) in zip(prefix, suffix):
        width += bool(enters) - bool(leaves)
        states += 1 << width
    return states


def _group_order(columns, sign):
    """Select the cheaper of a few fixed traversal orders before doing search."""
    count = len(columns)
    natural = list(range(count))
    if count < 22:
        return natural
    without_sign = [column % sign for column in columns]
    orders = [natural, sorted(natural, key=without_sign.__getitem__)]
    checks = sign.bit_length() - 1
    knots = (1 + isqrt(1 + 8 * checks)) // 2
    if knots * (knots - 1) // 2 == checks:
        # In the census a row is indexed by an unordered pair of knots.
        # Gathering types that involve the same last knots reduces the largest
        # trellis. An arbitrary row ordering still gives an exact search.
        pairs = list(combinations(range(knots), 2))
        owners = [
            tuple(sorted({k for j, pair in enumerate(pairs) if col >> j & 1 for k in pair},
                         reverse=True))
            for col in without_sign
        ]
        orders.append(sorted(natural, key=owners.__getitem__))
    return min(orders, key=lambda order: _volume([columns[i] for i in order] + [sign]))


def _merge(old, candidate):
    """Combine disjoint families of partial choices attaining one parity sum."""
    high, high_count, witness, low, low_count, holders = old
    next_high, next_high_count, next_witness, next_low, next_low_count, next_holders = candidate
    if next_high > high:
        high, high_count, witness = next_high, next_high_count, next_witness
    elif next_high == high:
        high_count += next_high_count
    if next_low < low:
        low, low_count = next_low, next_low_count
    elif next_low == low:
        low_count += next_low_count
    return high, high_count, witness, low, low_count, max(holders, next_holders)


def _trellis(columns, sign, masks, sizes, order, n):
    adapted = _column_coordinates([columns[i] for i in order] + [sign])
    assert adapted[-1] == (1, 1)
    infinity = n + 1
    # Each entry holds the largest pair count, its multiplicity and an example,
    # the smallest positive compressed-word weight and its raw multiplicity,
    # and the largest holder count. The all-even compressed word is handled
    # separately for the minimum because a doubled group can still use two.
    states = {0: (0, 1, 0, infinity, 0, 0)}
    for i, (column, retiring) in zip(order, adapted):
        mask = masks[i]
        size = sizes[i]
        omit_one = mask ^ (mask & -mask)
        max_weights = (size, size - 1) if size % 2 == 0 else (size - 1, size)
        max_counts = (1, size) if size % 2 == 0 else (size, 1)
        witnesses = (mask, omit_one) if size % 2 == 0 else (omit_one, mask)
        following = {}
        for syndrome, (high, high_count, witness, low, low_count, holders) in states.items():
            choices = (int(bool(syndrome & retiring)),) if retiring else (0, 1)
            for parity in choices:
                after = syndrome ^ column if parity else syndrome
                if parity and syndrome == 0:
                    # The all-zero prefix is always here. Its first odd group
                    # uses one of these size positions, undercutting all other
                    # prefixes at this sum for this transition.
                    new_low, new_low_count = 1, size
                elif parity:
                    new_low, new_low_count = low + 1, low_count * size
                else:
                    new_low, new_low_count = low, low_count
                candidate = (high + max_weights[parity], high_count * max_counts[parity],
                             witness | witnesses[parity], new_low, new_low_count,
                             holders + int(bool(parity) or size >= 2))
                old = following.get(after)
                following[after] = candidate if old is None else _merge(old, candidate)
        states = following
    assert states.keys() <= {0, 1} and 0 in states
    duplicates = sum(comb(size, 2) for size in sizes)
    if duplicates:
        high, high_count, witness, low, low_count, holders = states[0]
        if 2 < low:
            low, low_count = 2, duplicates
        elif low == 2:
            low_count += duplicates
        states[0] = (high, high_count, witness, low, low_count, holders)
    return states


def _verdict(even, odd, best):
    if best is None:
        return "empty"
    if even == odd:
        return "free"
    return "forced even" if best == even else "forced odd"


def solve(n, rows, cost, groups):
    """Return sign-conditioned extrema, exact multiplicities and a maximum word.

    `rows` and `cost` are bitmasks on n positions. The holder groups must
    partition the positions and have identical columns, including the cost,
    within each group. One or more chosen positions in a group score one holder.
    """
    rows = tuple(rows)
    size_mask = (1 << n) - 1
    if any(row < 0 or row & ~size_mask for row in (*rows, cost)):
        raise ValueError("a check or cost extends past the declared positions")
    sign = 1 << len(rows)
    columns, masks, sizes = [], [], []
    used = 0
    for positions in groups:
        if not positions or any(j < 0 or j >= n for j in positions):
            raise ValueError("empty holder group or invalid position")
        mask = sum(1 << j for j in set(positions))
        size = len(positions)
        if mask.bit_count() != size or used & mask:
            raise ValueError("repeated position in holder partition")
        used |= mask
        column = 0
        for j, row in enumerate((*rows, cost)):
            part = row & mask
            if part:
                if part != mask:
                    raise ValueError("holder type has different check or sign entries")
                column |= 1 << j
        columns.append(column)
        masks.append(mask)
        sizes.append(size)
    if used != size_mask:
        raise ValueError("holder partition omits positions")

    order = _group_order(columns, sign)
    states = _trellis(columns, sign, masks, sizes, order, n)
    high = [states[b][0] if b in states else None for b in (0, 1)]
    low = [states[b][3] if b in states and states[b][4] else None for b in (0, 1)]
    holder = [states[b][5] if b in states else None for b in (0, 1)]
    best_high = max(value for value in high if value is not None)
    best_low = min((value for value in low if value is not None), default=None)
    best_holder = max(value for value in holder if value is not None)
    for b, (value, _, word, _, _, _) in states.items():
        assert word.bit_count() == value and all((r & word).bit_count() % 2 == 0 for r in rows)
        assert (cost & word).bit_count() % 2 == b
    check_rank = sum(bool(added) for _, added in _column_coordinates([c % sign for c in columns]))
    return {
        "free choices": n - check_rank,
        "max with even sign": high[0], "max with odd sign": high[1],
        "max weight": best_high, "max principle": _verdict(*high, best_high),
        "max word": states[high.index(best_high)][2],
        "maximum words": sum(states[b][1] for b in states if high[b] == best_high),
        "min nonzero with even sign": low[0], "min with odd sign": low[1],
        "min nonzero weight": best_low, "min principle": _verdict(*low, best_low),
        "minimum words": sum(states[b][4] for b in states if low[b] == best_low),
        "max holder types with even sign": holder[0], "max holder types with odd sign": holder[1],
        "max holder types": best_holder, "holder-type principle": _verdict(*holder, best_holder),
    }
