"""Tests for sketches that are linear readouts of a matching after a change of input basis."""


def columns(m, mask):
    r = (m + 1) // 2
    return tuple((int((mask >> (2*j)) & 1) << j) |
                 (int(j + 1 < r and ((mask >> (2*j + 1)) & 1)) << (j + 1))
                 for j in range(r))


def apply(cols, v):
    out = 0
    for j, column in enumerate(cols):
        if (v >> j) & 1:
            out ^= column
    return out


def compose(s, t):
    return tuple(apply(s, c) for c in t)


def operators(m):
    if m % 2 != 1:
        raise ValueError("requires a nonsingular path with an even number of vertices")
    full = columns(m, (1 << m) - 1)
    inverse = {apply(full, x): x for x in range(1 << len(full))}
    return [tuple(inverse[v] for v in columns(m, a)) for a in range(1 << m)]


def joint_criterion(m):
    ops = operators(m)
    idempotent = [i for i, t in enumerate(ops) if compose(t, t) == t]
    good = {(i, j) for i in idempotent for j in idempotent
            if compose(ops[i], ops[j]) == compose(ops[j], ops[i])}
    winner = next(((i, j) for i, j in sorted(good) if i and j and i != j and i^j != (1 << m)-1), None)
    return idempotent, good, winner


def diagonal_profile(m, i, j, ops=None):
    matrices = operators(m) if ops is None else ops
    a, b = matrices[i], matrices[j]
    if compose(a, a) != a or compose(b, b) != b or compose(a, b) != compose(b, a):
        return None
    r = len(a)
    counts = {}
    for c in (0, 1):
        for d in (0, 1):
            size = sum(apply(a, v) == c * v and apply(b, v) == d * v for v in range(1 << r))
            rank = size.bit_length() - 1
            if size != 1 << rank:
                raise ValueError("joint eigenspace size is not a power of two")
            if rank:
                counts[c, d] = rank
    if sum(counts.values()) != r:
        raise ValueError("joint eigenspaces do not span the matching")
    return counts, diagonal_lower(counts)


def diagonal_lower(counts):
    r = sum(counts.values())
    if not counts or len({x for x, y in counts}) == 1 or len({y for x, y in counts}) == 1:
        return 1 << r
    if len(counts) == 2:
        return sum(1 << v for v in counts.values())
    return 2 * ((1 << ((r - 1) // 2)) + (1 << (r // 2)))


if __name__ == "__main__":
    for m in (3, 5, 7):
        idem, good, ex = joint_criterion(m)
        print(m,len(idem),len(good),ex,(15,15) in good)
