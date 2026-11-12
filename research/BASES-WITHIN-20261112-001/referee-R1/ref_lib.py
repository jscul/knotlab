"""Referee BASES-WITHIN-R1: the referee's own code (no import of the author's modules).

Harmonies are rebuilt from the window graph: for a set of kinds (0, a, b) of span L = max b, the vertices are binary words of
length L, an edge joins x_0..x_(L-1) to x_1..x_L when every kind holds at place 0 of x_0..x_L. Bi-infinite states are bi-infinite
walks. After removing, again and again, every vertex with no edge in or no edge out, the kinds form a harmony exactly when something
is left and every vertex left has one edge in and one edge out: the walks left are then disjoint cycles, so every state repeats;
a vertex left with two edges out (or in) gives a walk that leaves one cycle for good, which does not repeat."""
import itertools
import math


def nae(x, y, z):
    return not (x == y == z)


# ---------------------------------------------------------------- harmonies

def kind_sets(span, max_kinds=3):
    """sets of 1 to max_kinds kinds (a, b), 0 < a < b <= span, with max b == span"""
    kinds = [(a, b) for b in range(2, span + 1) for a in range(1, b)]
    for r in range(1, max_kinds + 1):
        for S in itertools.combinations(kinds, r):
            if max(b for _, b in S) == span:
                yield S


def window_cycles(S):
    """the cycles of the pruned window graph as words (one per cycle), or None if the kinds are not a harmony"""
    L = max(b for _, b in S)
    nv = 1 << L
    out = {v: [] for v in range(nv)}
    inn = {v: [] for v in range(nv)}
    for x in range(1 << (L + 1)):
        bits = [(x >> i) & 1 for i in range(L + 1)]
        if all(nae(bits[0], bits[a], bits[b]) for a, b in S):
            u = x & (nv - 1)            # bits 0..L-1
            v = x >> 1                  # bits 1..L
            out[u].append(v)
            inn[v].append(u)
    alive = set(range(nv))
    changed = True
    while changed:
        changed = False
        for v in list(alive):
            if not any(w in alive for w in out[v]) or not any(w in alive for w in inn[v]):
                alive.discard(v)
                changed = True
    if not alive:
        return None
    for v in alive:
        if sum(w in alive for w in out[v]) != 1 or sum(w in alive for w in inn[v]) != 1:
            return None
    seen = set()
    words = []
    for v0 in sorted(alive):
        if v0 in seen:
            continue
        word = []
        v = v0
        while v not in seen:
            seen.add(v)
            word.append(v & 1)          # the symbol at the window's first place
            v = [w for w in out[v] if w in alive][0]
        assert v == v0
        words.append(tuple(word))
    return words


def canon(w):
    return min(tuple(w[(i + r) % len(w)] for i in range(len(w))) for r in range(len(w)))


def harmonies(max_span=8, max_period=16):
    """distinct state sets of NAE harmonies of 1 to 3 kinds, span 2..max_span, with P <= max_period:
    list of dicts {orbits: sorted canonical words as strings, P, kinds: one kind set giving it}"""
    seen = {}
    for L in range(2, max_span + 1):
        for S in kind_sets(L):
            cyc = window_cycles(S)
            if cyc is None:
                continue
            key = tuple(sorted(set(canon(c) for c in cyc)))
            seen.setdefault(key, S)
    out = []
    for key, S in seen.items():
        P = 1
        for w in key:
            P = P * len(w) // math.gcd(P, len(w))
        if P <= max_period:
            out.append({"orbits": ["".join(map(str, w)) for w in key], "P": P, "kinds": [list(k) for k in S]})
    return sorted(out, key=lambda h: (sum(len(o) for o in h["orbits"]), h["orbits"]))


def states(h):
    """all states as tuples of length P (every shift of every orbit word)"""
    P = h["P"]
    out = set()
    for o in h["orbits"]:
        p = len(o)
        for r in range(p):
            out.add(tuple(int(o[(i + r) % p]) for i in range(P)))
    return sorted(out)


# ---------------------------------------------------------------- outer patterns

def canonical_pattern(n, E):
    return min(tuple(sorted(tuple(sorted(p[x] for x in e)) for e in E)) for p in itertools.permutations(range(n)))


def connected(n, E):
    comp = {0}
    grow = True
    while grow:
        grow = False
        for e in E:
            if comp & set(e) and not set(e) <= comp:
                comp |= set(e)
                grow = True
    return comp == set(range(n))


def outer_patterns(max_vars=6, max_knots=4):
    found = set()
    for n in range(3, max_vars + 1):
        triples = list(itertools.combinations(range(n), 3))
        for m in range(1, max_knots + 1):
            for E in itertools.combinations(triples, m):
                if set(itertools.chain(*E)) != set(range(n)) or not connected(n, E):
                    continue
                found.add((n, canonical_pattern(n, E)))
    return sorted(found)


FANO = ((0, 1, 2), (0, 3, 4), (0, 5, 6), (1, 3, 5), (1, 4, 6), (2, 3, 6), (2, 4, 5))


def outer_states(n, E):
    return [s for s in itertools.product((0, 1), repeat=n) if all(nae(s[a], s[b], s[c]) for a, b, c in E)]


# ---------------------------------------------------------------- O[I] by brute force over rows (slow, for cross-checks)

def lives_slow(n, E, W, shifts=None):
    """O[I] with rows in W (tuples of length P), knot k = (a, b, c) with shifts (sa, sb, sc): NAE(x_(a,i+sa), x_(b,i+sb), x_(c,i+sc))"""
    P = len(W[0])
    if shifts is None:
        shifts = [(0, 0, 0)] * len(E)

    def ok(rows, k):
        (a, b, c), (sa, sb, sc) = E[k], shifts[k]
        return all(nae(rows[a][(i + sa) % P], rows[b][(i + sb) % P], rows[c][(i + sc) % P]) for i in range(P))
    last = {}
    for k, e in enumerate(E):
        last.setdefault(max(e), []).append(k)
    rows = [None] * n

    def go(j):
        if j == n:
            return True
        for w in W:
            rows[j] = w
            if all(ok(rows, k) for k in last.get(j, [])) and go(j + 1):
                return True
        rows[j] = None
        return False
    return go(0)


def incidence_tree(n, E):
    """a spanning tree of the incidence graph (distinctions 0..n-1, knots n..n+e-1); returns the incidences (k, position) off the
    tree: the free shifts after the gauge (shift each row, shift each knot's place) has set every tree incidence to 0"""
    adj = {}
    for k, e in enumerate(E):
        for pos, x in enumerate(e):
            adj.setdefault(x, []).append((n + k, (k, pos)))
            adj.setdefault(n + k, []).append((x, (k, pos)))
    seen = {0}
    tree = set()
    stack = [0]
    while stack:
        u = stack.pop()
        for v, inc in adj[u]:
            if v not in seen:
                seen.add(v)
                tree.add(inc)
                stack.append(v)
    assert len(seen) == n + len(E)
    return [(k, pos) for k in range(len(E)) for pos in range(3) if (k, pos) not in tree]
