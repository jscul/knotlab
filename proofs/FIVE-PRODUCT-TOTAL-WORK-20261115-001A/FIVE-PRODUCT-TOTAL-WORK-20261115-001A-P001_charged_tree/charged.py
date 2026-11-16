"""Paid source checks and affine queries on explicit Boolean relations."""

from collections import Counter, namedtuple
from functools import cache
from math import inf


def require(ok, why):
    if not ok:
        raise ValueError(why)


def parity(word):
    return word.bit_count() % 2


def words(mask):
    while mask:
        low = mask & -mask
        yield low.bit_length() - 1
        mask ^= low


def full_space(n):
    return (1 << (1 << n)) - 1


@cache
def affine_hull(points):
    if not points:
        return 0
    origin = (points & -points).bit_length() - 1
    basis = {}
    for x in words(points):
        delta = x ^ origin
        while delta:
            j = delta.bit_length() - 1
            if j not in basis:
                basis[j] = delta
                break
            delta ^= basis[j]
    span = [origin]
    for delta in basis.values():
        span.extend([x ^ delta for x in span])
    return sum(1 << x for x in span)


@cache
def query_points(n, mask):
    return sum(parity(mask & x) << x for x in range(1 << n))


@cache
def partitions(n, cell):
    cuts = set()
    for q in range(1, 1 << n):
        yes = cell & query_points(n, q)
        no = cell ^ yes
        if yes and no:
            cuts.add(min(yes, no))
    return tuple(sorted(cuts))


Costs = namedtuple("Costs", "weighted normalized checks_only_at_leaves free_leaves checks_only")


def exact_costs(n, rich, plain):
    """Exhaust every affine subcase. Each input set is an integer bit mask on F2^n.

    The first entry is the full paid minimum, allowing every productive check
    and every nonconstant question on the actual geometric cell. Use this
    exhaustive routine on small dimensions. A shared honest point gives infinity.
    """
    full = full_space(n)
    require(rich >= 0 and plain >= 0 and not ((rich | plain) & ~full), "row outside input space")
    if rich & plain:
        return Costs(*(inf for _ in range(5)))

    @cache
    def visit(cell):
        if not cell:
            return Costs(0, 0, 0, 1, 0)
        left, right = rich & cell, plain & cell
        if not left or not right:
            return Costs(1, 1, 1, 1, 1)
        h_left, h_right = affine_hull(left), affine_hull(right)
        weighted = normalized = checks_only = inf
        for target in (h_left, h_right):
            if target != cell:
                future = visit(target)
                weighted = min(weighted, 1 + future.weighted)
                normalized = min(normalized, 1 + future.normalized)
                checks_only = min(checks_only, 1 + future.checks_only)
        late = checks_only
        simultaneous = h_left & h_right
        free = visit(simultaneous).free_leaves if simultaneous != cell else inf
        for low in partitions(n, cell):
            high = cell ^ low
            a, b = visit(low), visit(high)
            weighted = min(weighted, 1 + a.weighted + b.weighted)
            late = min(late, 1 + a.checks_only_at_leaves + b.checks_only_at_leaves)
            if low & left and high & left and low & right and high & right:
                normalized = min(normalized, 1 + a.normalized + b.normalized)
            if simultaneous == cell:
                free = min(free, a.free_leaves + b.free_leaves)
        return Costs(weighted, normalized, late, free, checks_only)

    result = visit(full)
    visit.cache_clear()
    return result


def audit_tree(n, rich, plain, tree, initial=None):
    """A source name alone means the paid call must return the empty hull."""
    full = full_space(n)
    cell = full if initial is None else initial
    require(not cell & ~full and affine_hull(cell) == cell, "initial case must be affine")
    counts = Counter()

    def walk(state, node):
        require(state, "instruction applied after a geometric contradiction")
        if isinstance(node, list) and len(node) == 3 and type(node[0]) is int:
            q, zero, one = node
            require(0 < q < 1 << n, "unavailable query coordinate")
            high = state & query_points(n, q)
            low = state ^ high
            require(low and high, "query is constant in the current affine case")
            counts["splits"] += 1
            counts["structural_child_continuations"] += 2
            if all(part & side for part in (low, high) for side in (rich, plain)):
                counts["splits_dividing_both_sides"] += 1
            return 1 + max(walk(low, zero), walk(high, one))
        terminal = isinstance(node, str)
        if terminal:
            side, child = node, None
        else:
            require(isinstance(node, list) and len(node) == 2, "malformed source call")
            side, child = node
        require(side in ("rich", "plain"), "unknown side")
        counts[side + "_calls"] += 1
        source = rich if side == "rich" else plain
        remaining = affine_hull(state & source)
        if terminal:
            require(not remaining, "claimed empty check still has a witness")
            counts["leaves"] += 1
            return 1
        require(remaining, "extra instructions after an empty source call")
        return 1 + walk(remaining, child)

    depth = walk(cell, tree)
    return {key: counts[key] for key in ("splits", "rich_calls", "plain_calls", "leaves",
                                          "splits_dividing_both_sides", "structural_child_continuations")} | {
        "total_work": counts["splits"] + counts["rich_calls"] + counts["plain_calls"],
        "maximum_paid_path": depth, "named_citations": 0}


def path_sources(m, charge=1):
    n = m + 1
    rich = plain = 0
    for x in range(1 << n):
        p = x & (x >> 1)
        s, u, v = parity(p), parity(p & 1), parity(p & 6)
        rich |= 1 << (x | (s << n) | (u << (n + 1)) | (v << (n + 2)))
        for private in range(4):
            plain |= 1 << (x | ((s ^ charge) << n) | (private << (n + 1)))
    return n + 3, rich, plain


def public_tree(coordinates):
    if not coordinates:
        return ["rich", "plain"]
    child = public_tree(coordinates[1:])
    return [1 << coordinates[0], child, child]
