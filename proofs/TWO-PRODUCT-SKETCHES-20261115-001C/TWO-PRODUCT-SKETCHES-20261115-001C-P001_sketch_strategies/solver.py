"""Exact path rank profiles, a two-block sketch tree, and its adversary embeddings."""

from collections import Counter


def parity(v):
    return v.bit_count() & 1


def rank(rows):
    pivots = {}
    for value in rows:
        while value:
            i = value.bit_length() - 1
            if i not in pivots:
                pivots[i] = value
                break
            value ^= pivots[i]
    return len(pivots)


def path_half_rank(m, mask):
    if type(m) is not int or m < 0 or not 0 <= mask < 1 << m:
        raise ValueError("invalid literal edge mask")
    rows = [0] * (m + 1)
    for i in range(m):
        if mask >> i & 1:
            rows[i] ^= 1 << (i + 1)
            rows[i + 1] ^= 1 << i
    return rank(rows) // 2


def rank_profiles(m):
    """Count all binary edge masks by the two complementary half-ranks."""
    if type(m) is not int or m < 0:
        raise ValueError("invalid edge count")
    counts = {(0, 0, 0, 0): 1}
    for _ in range(m):
        new = Counter()
        for (zero, one, last, odd), count in counts.items():
            for digit in (0, 1):
                old_odd = odd if digit == last else 0
                new[(zero + int(digit == 0 and not old_odd),
                     one + int(digit == 1 and not old_odd), digit, 1 - old_odd)] += count
        counts = new
    result = Counter()
    for (zero, one, _, _), count in counts.items():
        result[zero, one] += count
    return result


def bundled_mask(pair_count, chosen):
    """On 2h reports match odd coordinates to differences of consecutive evens."""
    chosen = tuple(chosen)
    if pair_count < 1 or any(not 0 <= j < pair_count for j in chosen):
        raise ValueError("bad bundle")
    m = 2 * pair_count - 1
    return sum(1 << edge for j in set(chosen) for edge in (2 * j, 2 * j + 1) if edge < m)


def raw_factors(pair_count):
    # Each product (y_j, z_j) is represented by two linear forms on the raw reports.
    return [(1 << (2*j + 1), (1 << (2*j)) ^ ((1 << (2*j + 2)) if j + 1 < pair_count else 0))
            for j in range(pair_count)]


def actual_products(r, s, point):
    """Quadratic sums for the two blocks in canonical unsimplified coordinates."""
    q = []
    start = 0
    for size in (r, s):
        total = 0
        for j in range(start, start + 2 * size, 2):
            total ^= (point >> j) & (point >> (j + 1)) & 1
        start += 2 * size
        q.append(total)
    return tuple(q)


def sides(r, s, point):
    """Return the exact evaluator predicates on K_(r,s) (or scalar K_r when s=0)."""
    q1, q2 = actual_products(r, s, point)
    width = 2 * (r + s)
    p1 = (point >> width) & 1
    if not s:
        return p1 == q1, (p1 ^ 1) == q1
    p2, delta = (point >> (width + 1)) & 1, (point >> (width + 2)) & 1
    return (p1, p2) == (q1, q2), (p1 ^ delta, p2 ^ delta ^ 1) == (q1, q2)


def child_embedding(r, s, query, answer):
    """Return smaller live block sizes and an affine map into this query answer.

    Inputs of each block are interleaved x,y. At the end are p1,p2,delta with
    the second discrepancy 1+delta. A scalar child has just its p bit.
    """
    if min(r, s) < 1 or answer not in (0, 1):
        raise ValueError("two nonempty groups and a Boolean answer are required")
    total = r + s
    width = 2 * total
    if not 0 < query < 1 << (width + 3):
        raise ValueError("a nonconstant query is required")
    if query == 1 << (width + 2):
        live = 0 if answer else 1
        size = (r, s)[live]
        shift = 2*r if live else 0

        def odd_group(point):
            bits = (point & ((1 << (2*size)) - 1)) << shift
            return bits | ((point >> (2*size)) << (width + live)) | (answer << (width + 2))

        return (size, 0), odd_group

    for pair in range(total):
        group = int(pair >= r)
        coeff = ((query >> (2*pair)) & 3) | (((query >> (width + group)) & 1) << 2)
        if coeff:
            break
    one = next(t for t in (0, 1, 2, 7) if parity(coeff & t))
    counts = [r, s]
    counts[group] -= 1
    both = 0 not in counts
    child = tuple(counts) if both else (max(counts), 0)
    small_width = width - 2

    def map_point(point):
        before = (1 << (2*pair)) - 1
        raw = point & ((1 << small_width) - 1)
        raw = (raw & before) | ((raw & ~before) << 2)
        if both:
            packed = raw | ((point >> small_width) << width)
        else:
            surviving = 1 - group
            # The removed group is honest on both sides, hence its discrepancy is 0.
            packed = raw | ((point >> small_width) << (width + surviving)) | (group << (width + 2))
        if parity(query & packed) != answer:
            packed ^= (one & 3) << (2*pair)
            packed ^= (one >> 2) << (width + group)
        return packed

    return child, map_point


def low_union_count(m, bound):
    """Count pairs whose complemented-mask union omits one color and has small cover.

    For 2*bound below the whole-path cover, the four omitted-color events are disjoint.
    """
    if 2*bound >= (m+1)//2:
        raise ValueError("the four events need not be disjoint")
    counts = {(0, 0): 1}
    for _ in range(m):
        new = Counter()
        for (used, odd), count in counts.items():
            new[used, 0] += count                         # the one omitted color
            more = used + (not odd)
            if more <= bound:
                new[more, 1 - odd] += 3 * count           # one of the three included colors
        counts = new
    return 4 * sum(counts.values())
