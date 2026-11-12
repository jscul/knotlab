"""Arithmetic of harmonies without a zero (research/HARMONY-ARITH-20261112-001/preregistration.md, ticket A).

A chain pattern has one distinction x_i at every whole number i and, for each of its knot kinds (0, a, b) with 0 < a < b, one knot on
(x_i, x_{i+a}, x_{i+b}) at every i; its span W is the largest b. A law says which of the 8 value triples a knot allows. The allowed
states (bi-infinite sequences) are the bi-infinite walks of the window graph: nodes are the 2^W windows (x_i .. x_{i+W-1}), with an
edge to the next window when the W+1 values satisfy every kind anchored at i. Its core is what remains after repeatedly removing
windows with no successor or no predecessor. The chain is a harmony when the core is not empty and every core window has exactly one
core successor and one core predecessor: then every allowed state is periodic, and its minimal period is the length of its cycle
(a simple cycle revisits no window, so no shorter period exists). Literature: a one-dimensional shift of finite type all of whose
points are periodic; its cycles are its periodic orbits.

Two harmonies a and b are stitched when, at every shift i, a stitch of one fixed kind holds distinctions of both: a knot under the
same law on (a_{i+s}, a_{i+t}, b_{i+u}) or on (a_{i+s}, b_{i+t}, b_{i+u}). They overlap at offset s when a_i and b_{i+s} are one shared
distinction for every i. A state of the stitched (or overlapping) base pairs a state of each harmony satisfying every stitch; the
pairs (u, shift^k v) drawn from two orbits of periods p and q fall into gcd(p, q) offsets (k mod gcd), each the orbit of one
repeating pair sequence of period lcm(p, q). Literature: a harmony is a finite subshift; orbit as in dynamics; the offset is the
relative phase."""
import itertools
import math
from collections import Counter

LAWS = {
    "NAE": lambda a, b, c: not (a == b == c),            # the knot's law (not-all-equal)
    "odd parity": lambda a, b, c: (a ^ b ^ c) == 1,       # a knot without the mirror (control)
    "exactly one": lambda a, b, c: a + b + c == 1,        # not a knot (fails K2), control
    "clause": lambda a, b, c: bool(a or b or c),          # a knot without the mirror (control)
}


def kinds_of_span(W):
    return [(0, a, b) for a in range(1, W + 1) for b in range(a + 1, W + 1)]


def patterns(W, max_kinds=3):
    """kind sets of 1 to max_kinds kinds whose largest offset is exactly W"""
    ks = kinds_of_span(W)
    for k in range(1, max_kinds + 1):
        for S in itertools.combinations(ks, k):
            if max(b for _, _, b in S) == W:
                yield S


def window_graph(W, kinds, law):
    f = LAWS[law]
    out = {}
    for w in range(1 << W):
        x = [(w >> j) & 1 for j in range(W)]
        succ = []
        for nb in (0, 1):
            y = x + [nb]
            if all(f(y[a], y[b], y[c]) for (a, b, c) in kinds):
                succ.append((w >> 1) | (nb << (W - 1)))
        out[w] = succ
    return out


def core(out):
    alive = set(out)
    while True:
        indeg = Counter(v for w in alive for v in out[w] if v in alive)
        drop = [w for w in alive if indeg[w] == 0 or not any(v in alive for v in out[w])]
        if not drop:
            return {w: [v for v in out[w] if v in alive] for w in alive}
        alive.difference_update(drop)


def classify(W, kinds, law):
    """('empty' | 'not a harmony' | 'harmony', list of cycles as value words starting at their least window)"""
    c = core(window_graph(W, kinds, law))
    if not c:
        return "empty", []
    indeg = Counter(v for w in c for v in c[w])
    if any(len(c[w]) != 1 or indeg[w] != 1 for w in c):
        return "not a harmony", []
    seen, cycles = set(), []
    for w in sorted(c):
        if w in seen:
            continue
        word, u = [], w
        while u not in seen:
            seen.add(u)
            word.append(u & 1)
            u = c[u][0]
        cycles.append(word)
    return "harmony", cycles


def antiperiodic(word):
    L = len(word)
    return L % 2 == 0 and all(word[(i + L // 2) % L] != word[i] for i in range(L))


def offset_gcd(kinds):
    return math.gcd(*[v for k in kinds for v in k[1:]])


def canon(word):
    """least rotation of a periodic word (its orbit's name)"""
    L = len(word)
    return min(tuple(word[(i + r) % L] for i in range(L)) for r in range(L))


def stitch_kinds(span=3):
    out = []
    for s, t in itertools.combinations(range(span + 1), 2):
        for u in range(span + 1):
            out.append(("a a b", (s, t, u)))
            out.append(("a b b", (u, s, t)))
    for s in range(span + 1):
        out.append(("overlap", (s,)))
    return out


def stitched_offsets(u, v, bk, law):
    """for orbits u (period p) and v (period q): the offsets k mod gcd(p, q) whose pair orbit satisfies the stitch (or overlap) at
    every shift; returns (gcd, surviving offsets)"""
    p, q = len(u), len(v)
    g, L = math.gcd(p, q), p * q // math.gcd(p, q)
    f = LAWS[law]
    kind, off = bk
    alive = []
    for k in range(g):
        ok = True
        for i in range(L):
            a = lambda j: u[(i + j) % p]
            b = lambda j: v[(i + j + k) % q]
            if kind == "a a b":
                s, t, w = off
                ok = f(a(s), a(t), b(w))
            elif kind == "a b b":
                s, t, w = off
                ok = f(a(s), b(t), b(w))
            else:
                ok = a(0) == b(off[0])
            if not ok:
                break
        if ok:
            alive.append(k)
    return g, alive


def mirror_fixes(p, q):
    """for antiperiodic orbits of periods p and q: does flipping every value map each offset to itself? (k with k = p/2 mod p and
    k = q/2 mod q exists iff p/2 = q/2 mod gcd(p, q), iff p and q have the same power of 2)"""
    return (p // 2 - q // 2) % math.gcd(p, q) == 0
