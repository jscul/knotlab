"""Find exact local certificates for absent words on three disjoint agreement readings."""
from collections import Counter, defaultdict
from functools import cache
from itertools import combinations


def members(mask):
    while mask:
        bit = mask & -mask
        yield bit.bit_length() - 1
        mask ^= bit


def mask_of(indices):
    return sum(1 << x for x in indices)


@cache
def partitions(size):
    """Set partitions of size 6--9 into three unlabelled pairs or triples."""
    def rec(xs, parts):
        if not xs:
            if len(parts) == 3:
                yield tuple(parts)
            return
        left = 2 - len(parts)
        for size in (2, 3):
            if 2 * left <= len(xs) - size <= 3 * left:
                for tail in combinations(xs[1:], size - 1):
                    chosen = (xs[0], *tail)
                    rest = tuple(x for x in xs if x not in chosen)
                    yield from rec(rest, [*parts, chosen])
    return tuple(rec(tuple(range(size)), []))


@cache
def bit_columns(n):
    """Use one bit per assignment and fix the first raw bit using global complement."""
    full = (1 << (1 << (n - 1))) - 1
    columns = [0]
    for j in range(n - 1):
        run = 1 << j
        columns.append((full // ((1 << run) + 1)) << run)
    return full, columns


def agree(group, full, cols):
    zeros, ones = full, full
    for v in group:
        zeros &= full ^ cols[v]
        ones &= cols[v]
    return zeros | ones


def ordered_shape(laws):
    """Identify repeated systems, with any ordering of tied knots sufficient."""
    incidence = Counter(x for law in laws for x in law)
    laws = sorted(laws, key=lambda k: (len(k), sorted(incidence[x] for x in k), k))
    address = defaultdict(list)
    for j, law in enumerate(laws):
        for x in law:
            address[x].append(j)
    names = sorted(address, key=lambda x: (address[x], x))
    return tuple(tuple(address[x]) for x in names), names


@cache
def partial_certificates(shape):
    """Minimal source laws and all three reading conditions must exclude the word."""
    n = len(shape)
    num_laws = max(max(owners) for owners in shape) + 1
    raw_laws = [tuple(x for x, owners in enumerate(shape) if i in owners) for i in range(num_laws)]
    boundary = tuple(x for x, owners in enumerate(shape) if len(owners) == 1)
    interior = tuple(x for x, owners in enumerate(shape) if len(owners) > 1)
    full, columns = bit_columns(n)
    bad = [agree(l, full, columns) for l in raw_laws]
    allowed, deleted = full, []
    for b in bad:
        allowed &= ~b
    for i, b in enumerate(bad):
        only = b
        for j, other in enumerate(bad):
            if i != j:
                only &= ~other
        deleted.append(only)
    if not all(deleted):
        return ()
    reading = {}
    result = []
    for held in range(max(6, len(boundary)), min(n, 9) + 1):
        # At most held-3 variables can be merged or supplied as additional
        # not-all-equal laws (one per negative reading).
        if n - num_laws > held - 3:
            continue
        for extra in combinations(interior, held - len(boundary)):
            selected = (*boundary, *extra)
            for partition in partitions(held):
                groups = tuple(tuple(sorted(selected[j] for j in indexes)) for indexes in partition)
                for group in groups:
                    if group not in reading:
                        yes = agree(group, full, columns)
                        reading[group] = (full ^ yes, yes)
                r0, r1, r2 = (reading[g] for g in groups)
                for v0, r0v in enumerate(r0):
                    for v1, r1v in enumerate(r1):
                        r01 = r0v & r1v
                        if not r01 & allowed:
                            continue
                        for v2, r2v in enumerate(r2):
                            cell = r01 & r2v
                            if cell & allowed or not (r0v & r2v & allowed and r1v & r2v & allowed):
                                continue
                            if all(cell & only for only in deleted):
                                result.append(tuple(zip(groups, (v0, v1, v2))))
    return tuple(result)


def clauses(supports):
    """Return three signed local restrictions, allowing a positive pair to be padded."""
    h = len(supports)
    support_masks = [mask_of(row) for row in supports]
    covered, twice = [0], [0]
    for knot in support_masks:
        old = len(covered)
        twice.extend(twice[i] | (covered[i] & knot) for i in range(old))
        covered.extend(covered[i] | knot for i in range(old))
    certs, stats = set(), Counter()
    for subset in range(1, 1 << h):
        total = subset.bit_count()
        d = covered[subset].bit_count()
        private = (covered[subset] ^ twice[subset]).bit_count()
        if d < 6 or d > total + 6 or private > 9:
            continue
        stats['subsets inspected'] += 1
        laws = [supports[i] for i in members(subset)]
        shape, names = ordered_shape(laws)
        local = partial_certificates(shape)
        if local:
            stats['subsets certifying a word'] += 1
        map_group = {}
        for words in local:
            triplet = []
            for group, value in words:
                if group not in map_group:
                    map_group[group] = mask_of(names[v] for v in group)
                m = map_group[group]
                # A two-place agreement can get a third member only when it is
                # required to agree. Every other holder-contained reading is a
                # function at one source knot, and cannot participate in a box.
                if (len(group) == 3 or not value) and any(m & law == m for law in support_masks):
                    break
                triplet.append((m, value))
            if len(triplet) == 3:
                certs.add(tuple(sorted(triplet)))
    return sorted(certs), dict(stats)
