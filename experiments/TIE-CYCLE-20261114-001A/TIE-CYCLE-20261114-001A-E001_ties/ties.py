"""TIE-CYCLE-20261114-001A, the thread's tie test: the full product semigroup of a family's per-call port relations (from
CENSUS-FORGET's records, Codex's relation encoding: bit 8*a+b), checked for a self-tie (end port j equal or opposite to start port j
in every pair) and, as a frozen variant, a self-coupling parity (alpha.a xor alpha.b constant on every pair, not implied by the two
projections separately)."""
from itertools import product


def pairs(rel):
    return [(a, b) for a in range(8) for b in range(8) if rel >> (8 * a + b) & 1]


def compose(r1, r2):
    out = 0
    for a in range(8):
        mids = [m for m in range(8) if r1 >> (8 * a + m) & 1]
        if not mids:
            continue
        for b in range(8):
            if any(r2 >> (8 * m + b) & 1 for m in mids):
                out |= 1 << (8 * a + b)
    return out


def closure(gens, cap=100_000):
    seen = set(gens); frontier = list(gens)
    while frontier:
        p = frontier.pop()
        for g in gens:
            q = compose(p, g)
            if q and q not in seen:
                seen.add(q); frontier.append(q)
                if len(seen) > cap:
                    return None
    return seen


def bit(x, j):
    return (x >> j) & 1


def self_tie(rel):
    P = pairs(rel)
    if not P:
        return None
    for j in range(3):
        if all(bit(a, j) == bit(b, j) for a, b in P):
            return ("equal", j)
        if all(bit(a, j) != bit(b, j) for a, b in P):
            return ("opposite", j)
    return None


def par(x, mask):
    return bin(x & mask).count("1") & 1


def self_parity(rel):
    P = pairs(rel)
    if not P:
        return None
    A = {a for a, _ in P}; B = {b for _, b in P}
    for mask in range(1, 8):
        vals = {par(a, mask) ^ par(b, mask) for a, b in P}
        if len(vals) == 1:
            implied = len({par(a, mask) for a in A}) == 1 and len({par(b, mask) for b in B}) == 1
            if not implied:
                return mask
    return None


def classify(Rhex):
    gens = [int(h, 16) for h in Rhex]
    S = closure(gens)
    if S is None:
        return dict(status="cap")
    tie = next((t for t in (self_tie(r) for r in S) if t), None)
    parity = next((m for m in (self_parity(r) for r in S) if m), None)
    return dict(status="ok", semigroup_size=len(S), tie_cycle=bool(tie), tie=tie, parity_cycle=bool(parity), parity_mask=parity)


def rectangular(rel):
    P = pairs(rel)
    A = {a for a, _ in P}; B = {b for _, b in P}
    return len(P) == len(A) * len(B)


def idempotent_types(S):
    """For each non-rectangular idempotent E of the semigroup S: its core {x : xEx} with the preorder x <= y iff (x, y) in E,
    and its type: 'order' when two core classes are comparable, else a conserved label, classified as 'tie' (one bit),
    'parity' (a linear form of several bits) or 'nonlinear'. Returns the set of types found."""
    types = set()
    for E in S:
        if compose(E, E) != E or rectangular(E):
            continue
        core = [x for x in range(8) if E >> (8 * x + x) & 1]
        le = lambda x, y: bool(E >> (8 * x + y) & 1)
        classes = []
        for x in core:
            for c in classes:
                if le(x, c[0]) and le(c[0], x):
                    c.append(x); break
            else:
                classes.append([x])
        if len(classes) < 2:
            types.add("non-rectangular, one class")
            continue
        comparable = any(le(c[0], d[0]) for c in classes for d in classes if c is not d)
        if comparable:
            types.add("order"); continue
        # a conserved label: which linear forms separate the classes consistently?
        label = {x: i for i, c in enumerate(classes) for x in c}
        one_bit = any(all((bit(x, j) == bit(y, j)) == (label[x] == label[y]) for x in core for y in core) for j in range(3))
        linear = any(all((par(x, m) == par(y, m)) == (label[x] == label[y]) for x in core for y in core) for m in range(1, 8))
        types.add("tie" if one_bit else ("parity" if linear else "nonlinear label"))
    return types


def classify_full(Rhex):
    gens = [int(h, 16) for h in Rhex]
    S = closure(gens)
    if S is None:
        return dict(status="cap")
    tie = next((t for t in (self_tie(r) for r in S) if t), None)
    parity = next((m for m in (self_parity(r) for r in S) if m), None)
    return dict(status="ok", semigroup_size=len(S), tie_cycle=bool(tie), parity_cycle=bool(parity),
                idempotent_types=sorted(idempotent_types(S)))
