"""A growth history under the knot test (ticket GROWTH-LAW-20261107-001A).

Relations are kept as (names, rows), a row being an int whose bit i is the value of names[i]. Every verdict is computed from the
allowed rows alone, as the canonical test asks: a set T of variables is a knot (K1-K3, erasure as forgetting) when the relation's
shadow on T is constrained while its shadow on every T minus one variable is free, and some state is allowed. So the knots are the
minimal constrained sets of size at least 3 (minimal constrained sets of size 1 are pinned variables, of size 2 ties).

Substrates are the hub-free parity laws of OPEN-END-GROWTH-20261107-001B: knots are three-place parity checks, a distinction held
by two knots is a seam and one held by one knot is an open end. The open-end rule grows from one knot with three open ends by
letting any knot that holds at least two open ends sprout at one of them; it grows the thread P_n (Proposition 4 there).

Histories are written with the world as variables:
- seam bits: for each seam, which of its two knots came first (bit 1: the lower-numbered knot did);
- pair bits: for each pair of knots, which came first;
- existence bits: which potential sites exist, when the substrate itself varies.
"""
from __future__ import annotations

import itertools
import random
from collections import Counter, defaultdict, deque


# ---------------------------------------------------------------------------------------------- relations and their knots
class Rel:
    def __init__(self, names, rows):
        self.names = tuple(names)
        if len(set(self.names)) != len(self.names):
            raise ValueError("variable names must be distinct")
        self.rows = frozenset(rows)
        self.index = {v: i for i, v in enumerate(self.names)}

    @property
    def n(self):
        return len(self.names)

    def mask(self, names):
        m = 0
        for v in names:
            m |= 1 << self.index[v]
        return m

    def shadow_size(self, m):
        return len({r & m for r in self.rows})

    def is_free(self, m):
        k = bin(m).count("1")
        return len(self.rows) >= 1 << k and self.shadow_size(m) == 1 << k

    def names_of(self, m):
        return tuple(v for i, v in enumerate(self.names) if m >> i & 1)

    def restrict(self, fixed):
        """keep the rows that agree with fixed (a dict name -> 0/1), on the same variables"""
        want = [(self.index[v], b) for v, b in fixed.items()]
        return Rel(self.names, [r for r in self.rows if all((r >> i & 1) == b for i, b in want)])

    def shadow(self, names):
        """the relation seen on names, as a relation over them"""
        pos = [self.index[v] for v in names]
        return Rel(names, {sum(((r >> p) & 1) << j for j, p in enumerate(pos)) for r in self.rows})


def product(R, S):
    """the product relation on disjoint variables"""
    shift = R.n
    return Rel(R.names + S.names, [r | (s << shift) for r in R.rows for s in S.rows])


def from_predicate(names, pred):
    names = tuple(names)
    return Rel(names, [r for r in range(1 << len(names)) if pred({v: r >> i & 1 for i, v in enumerate(names)})])


def minimal_constrained(R, max_size=None):
    """all minimal constrained sets (bitmasks), found level by level: a set is a candidate only when every subset one smaller is
    free; it is minimal constrained when its own shadow is not free"""
    if not R.rows:
        raise ValueError("an empty relation has no knots (K3)")
    n = R.n
    max_size = n if max_size is None else max_size
    found = []
    free_prev = {0}
    for k in range(1, max_size + 1):
        free_now = set()
        seen = set()
        for F in free_prev:
            top = F.bit_length()
            for j in range(top, n):
                T = F | (1 << j)
                if T in seen:
                    continue
                seen.add(T)
                if any((T & ~(1 << i)) not in free_prev for i in range(n) if T >> i & 1):
                    continue
                if R.is_free(T):
                    free_now.add(T)
                else:
                    found.append(T)
        if not free_now:
            break
        free_prev = free_now
    return found


def knots(R, max_size=None):
    return [T for T in minimal_constrained(R, max_size) if bin(T).count("1") >= 3]


def is_knot_set(R, names):
    """K1-K3 on the shadow over names, directly"""
    m = R.mask(names)
    if R.is_free(m) or not R.rows:
        return False
    return all(R.is_free(m & ~(1 << R.index[v])) for v in names)


def is_2cnf(R):
    """a Boolean relation is defined by 2-clauses exactly when it is closed under the majority operation"""
    rows = list(R.rows)
    for x, y, z in itertools.combinations_with_replacement(rows, 3):
        if ((x & y) | (y & z) | (x & z)) not in R.rows:
            return False
    return True


# ---------------------------------------------------------------------------------------------- threads, rings and their laws
def thread(n):
    """the thread P_n of the open-end rule: knots 0..n-1; seams s0..s(n-2); open ends; each knot's three distinctions"""
    if n == 1:
        return {0: ("a0", "b0", "c0")}, []
    dist = {}
    for i in range(n):
        own = []
        if i > 0:
            own.append(f"s{i - 1}")
        if i < n - 1:
            own.append(f"s{i}")
        while len(own) < 3:
            own.append(f"o{i}{'abc'[len(own)]}")
        dist[i] = tuple(own)
    return dist, [(i, i + 1) for i in range(n - 1)]


def parity_law(dist):
    """the hub-free parity law: at each knot its three distinctions sum to 0"""
    names = sorted({d for ds in dist.values() for d in ds})
    idx = {v: i for i, v in enumerate(names)}
    checks = [sum(1 << idx[d] for d in ds) for ds in dist.values()]
    rows = [r for r in range(1 << len(names)) if all(bin(r & c).count("1") % 2 == 0 for c in checks)]
    return Rel(names, rows)


def bonds(dist, edges):
    """the knots of a hub-free parity law, independently: the cuts delta(U) of the knot graph (open ends to infinity) with U and
    the rest plus infinity both connected and at least three distinctions (OPEN-END-GROWTH-20261107-001B, Proposition 1)"""
    knots_ = list(dist)
    holders = defaultdict(list)
    for k, ds in dist.items():
        for d in ds:
            holders[d].append(k)
    out = set()
    for size in range(1, len(knots_) + 1):
        for U in itertools.combinations(knots_, size):
            U = set(U)
            cut = frozenset(d for d, hs in holders.items() if (len([h for h in hs if h in U]) == 1 and len(hs) == 2) or (len(hs) == 1 and hs[0] in U))
            if len(cut) < 3:
                continue
            if not _connected(U, edges) or not _connected_with_inf(set(knots_) - U, edges, holders):
                continue
            out.add(cut)
    return out


def _connected(U, edges):
    U = set(U)
    if not U:
        return False
    start = next(iter(U))
    seen = {start}
    q = deque([start])
    while q:
        u = q.popleft()
        for a, b in edges:
            for x, y in ((a, b), (b, a)):
                if x == u and y in U and y not in seen:
                    seen.add(y)
                    q.append(y)
    return seen == U


def _connected_with_inf(W, edges, holders):
    """W plus the vertex at infinity is connected (W may be empty: infinity alone is connected)"""
    if not W:
        return True
    inf_nb = {hs[0] for d, hs in holders.items() if len(hs) == 1}
    seen = set(x for x in W if x in inf_nb)
    q = deque(seen)
    while q:
        u = q.popleft()
        for a, b in edges:
            for x, y in ((a, b), (b, a)):
                if x == u and y in W and y not in seen:
                    seen.add(y)
                    q.append(y)
    return seen == set(W)


def open_end_histories(n):
    """every run of the open-end rule to n knots, as the final thread's birth order: a tuple t with t[i] the step at which the
    knot at position i was born (the seed has 0). Each run is simulated: a knot holding two or more open ends sprouts."""
    runs = set()

    def rec(left, right, order):
        # the thread so far occupies positions left..right of a long line; order lists positions by birth
        if len(order) == n:
            lo = min(order)
            runs.add(tuple(order.index(p) for p in range(lo, lo + n)))
            return
        if len(order) == 1:
            # the seed holds three open ends; sprouting at any of them gives the same thread up to mirror image,
            # and both mirror images are kept
            for side in (-1, 1):
                p = order[0] + side
                rec(min(left, p), max(right, p), order + [p])
            return
        # the knots holding two open ends are the two ends of the thread
        for p in (left - 1, right + 1):
            rec(min(left, p), max(right, p), order + [p])

    rec(0, 0, [0])
    return sorted(runs)


def seam_bits(birth, edges):
    """seam bit 1 when the lower-numbered knot of the seam came first"""
    return tuple(1 if birth[a] < birth[b] else 0 for a, b in edges)


def pair_bits(birth):
    n = len(birth)
    return tuple(1 if birth[i] < birth[j] else 0 for i, j in itertools.combinations(range(n), 2))


def history_relation(n, kind):
    births = open_end_histories(n)
    dist, edges = thread(n)
    if kind == "seam":
        names = [f"h_s{i}" for i in range(len(edges))]
        vecs = {seam_bits(b, edges) for b in births}
    else:
        names = [f"h_{i}{j}" for i, j in itertools.combinations(range(n), 2)]
        vecs = {pair_bits(b) for b in births}
    rows = [sum(v << i for i, v in enumerate(vec)) for vec in vecs]
    return Rel(names, rows)


def classify(R, T, groups):
    """which groups (dict group -> set of names) the knot T meets"""
    ns = set(R.names_of(T))
    return tuple(sorted(g for g, members in groups.items() if ns & members))


# ---------------------------------------------------------------------------------------------- the beginning
def ring_edges(n):
    return [(i, (i + 1) % n) for i in range(n)]


def orientation_rel(n_knots, edges, pred):
    """orientations of the seams (bit 1: the edge (a, b) points a -> b, a came first) allowed by pred(parents) where parents[v] is
    the number of v's neighbours that came before v"""
    names = [f"e{a}_{b}" for a, b in edges]
    rows = []
    for r in range(1 << len(edges)):
        parents = Counter()
        for i, (a, b) in enumerate(edges):
            parents[b if r >> i & 1 else a] += 1
        if pred([parents[v] for v in range(n_knots)]):
            rows.append(r)
    return Rel(names, rows)


def nae(names, flips=()):
    """not-all-equal on names, after flipping the variables in flips"""
    names = tuple(names)
    fl = sum(1 << i for i, v in enumerate(names) if v in flips)
    full = (1 << len(names)) - 1
    return Rel(names, [r for r in range(1 << len(names)) if (r ^ fl) not in (0, full)])


def acyclic_orientations(n_knots, edges):
    names = [f"e{a}_{b}" for a, b in edges]
    rows = []
    for r in range(1 << len(edges)):
        out = defaultdict(list)
        indeg = Counter()
        for i, (a, b) in enumerate(edges):
            x, y = (a, b) if r >> i & 1 else (b, a)
            out[x].append(y)
            indeg[y] += 1
        q = deque(v for v in range(n_knots) if indeg[v] == 0)
        seen = 0
        while q:
            u = q.popleft()
            seen += 1
            for w in out[u]:
                indeg[w] -= 1
                if indeg[w] == 0:
                    q.append(w)
        if seen == n_knots:
            rows.append(r)
    return Rel(names, rows)


def cycles_of(n_knots, edges):
    """every simple cycle of a small graph, as (edge indices, flips): flips are the edges that the cycle's direction runs
    against, so that the cycle is directed exactly when the flipped bits are all equal"""
    adj = defaultdict(list)
    for i, (a, b) in enumerate(edges):
        adj[a].append((b, i))
        adj[b].append((a, i))
    found = set()
    out = []

    def dfs(start, u, path_v, path_e):
        for w, i in adj[u]:
            if i in path_e:
                continue
            if w == start and len(path_e) >= 2:
                key = frozenset(path_e + [i])
                if key not in found:
                    found.add(key)
                    seq = path_e + [i]
                    vs = path_v + [start]
                    flips = [edges[e] for k, e in enumerate(seq) if edges[e] != (vs[k], vs[k + 1])]
                    out.append((seq, flips))
            elif w not in path_v and w > start:
                dfs(start, w, path_v + [w], path_e + [i])

    for s in range(n_knots):
        dfs(s, s, [s], [])
    return out


def chordless(cycle_edges, edges):
    vs = {x for e in cycle_edges for x in edges[e]}
    return not any(a in vs and b in vs and i not in cycle_edges for i, (a, b) in enumerate(edges))


def linear_orders_rel(n):
    """the n! linear orders of n events on their pair bits (bit 1: the lower-numbered event first)"""
    names = [f"b{i}{j}" for i, j in itertools.combinations(range(n), 2)]
    rows = set()
    for perm in itertools.permutations(range(n)):
        pos = {v: k for k, v in enumerate(perm)}
        rows.add(sum((1 if pos[i] < pos[j] else 0) << k for k, (i, j) in enumerate(itertools.combinations(range(n), 2))))
    return Rel(names, rows)


# ---------------------------------------------------------------------------------------------- Euler's count
def chi_steps_1d(steps):
    """each step is ('seed',), ('sprout',) or ('close',): a sprout adds one knot and one seam, a close adds one seam between two
    knots already present; the Euler characteristic of the knot graph (knots minus seams) is the sum of the steps' changes"""
    change = {"seed": 1, "sprout": 0, "close": -1}
    return sum(change[s[0]] for s in steps)


def grow_1d(rule, steps, rng):
    """grow a knot graph from one knot with three open ends. rule: 'open-end' (sprout at a knot holding >= 2 open ends),
    'sprout' (at any open end), 'close' (sprout or join two open ends of different knots with a seam).
    Returns the knot graph (knots, seams), the step log and the open-end counts."""
    openc = {0: 3}
    seams = []
    log = [("seed",)]
    for _ in range(steps):
        if rule == "open-end":
            cand = [k for k, c in openc.items() if c >= 2]
        else:
            cand = [k for k, c in openc.items() if c >= 1]
        if not cand:
            break
        if rule == "close" and rng.random() < 0.3:
            pairs = [(a, b) for a in cand for b in cand if a < b and (a, b) not in seams]
            if pairs:
                a, b = rng.choice(pairs)
                openc[a] -= 1
                openc[b] -= 1
                seams.append((a, b))
                log.append(("close", a, b))
                continue
        k = rng.choice(cand)
        new = len(openc)
        openc[k] -= 1
        openc[new] = 2
        seams.append((k, new))
        log.append(("sprout", k, new))
    return list(openc), seams, log, openc


def cyclomatic(knots_, seams):
    """seams minus knots plus components"""
    parent = {k: k for k in knots_}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    comps = len(knots_)
    for a, b in seams:
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb
            comps -= 1
    return len(seams) - len(knots_) + comps


def chi_steps_2d(tris):
    """grow a closed surface by adding its triangles in the given order; for each step, a = edges of the triangle already present
    and b = vertices already present; the step changes the Euler characteristic of the grown complex by (3 - b) - (3 - a) + 1.
    Returns the kinds and the total."""
    have_v, have_e = set(), set()
    kinds = Counter()
    total = 0
    for t in tris:
        es = [frozenset(p) for p in itertools.combinations(t, 2)]
        a = sum(e in have_e for e in es)
        b = sum(v in have_v for v in t)
        d = a - b + 1
        total += d
        kinds[{(0, 0): "first", (1, 2): "add", (2, 3): "cap", (3, 3): "end", (1, 3): "pinch"}.get((a, b), f"other{a}{b}")] += 1
        have_v.update(t)
        have_e.update(es)
    return kinds, total


def flat_torus(p, q):
    """the triangular lattice on the p x q torus (vertices (i, j) mod (p, q)), two triangles per cell"""
    tris = []
    for i in range(p):
        for j in range(q):
            a, b, c, d = (i, j), ((i + 1) % p, j), (i, (j + 1) % q), ((i + 1) % p, (j + 1) % q)
            tris.append((a, b, d))
            tris.append((a, d, c))
    return tris


def euler_char(tris):
    V = {v for t in tris for v in t}
    E = {frozenset(e) for t in tris for e in itertools.combinations(t, 2)}
    return len(V) - len(E) + len(tris)


def disc_growth(tris, rng, order="random"):
    """grow by disc moves only (ADD: one present edge and a new vertex; CAP: two present edges, the third vertex present; END: all
    three edges present), from one triangle; return the kinds used and how many triangles were never placed (stuck)"""
    edge_tris = defaultdict(list)
    for k, t in enumerate(tris):
        for e in itertools.combinations(t, 2):
            edge_tris[frozenset(e)].append(k)
    placed = {0}
    have_v = set(tris[0])
    have_e = {frozenset(e) for e in itertools.combinations(tris[0], 2)}
    kinds = Counter({"first": 1})
    while len(placed) < len(tris):
        moves = []
        for e in have_e:
            for k in edge_tris[e]:
                if k in placed:
                    continue
                t = tris[k]
                es = [frozenset(p) for p in itertools.combinations(t, 2)]
                a = sum(x in have_e for x in es)
                b = sum(v in have_v for v in t)
                kind = {(1, 2): "add", (2, 3): "cap", (3, 3): "end"}.get((a, b))
                if kind == "cap":
                    # the two present edges must meet at a vertex whose star closes: true for two edges of one triangle
                    pass
                if kind:
                    moves.append((k, kind))
        if not moves:
            break
        moves = sorted(set(moves))
        k, kind = moves[0] if order == "first" else rng.choice(moves)
        placed.add(k)
        kinds[kind] += 1
        have_v.update(tris[k])
        have_e.update(frozenset(p) for p in itertools.combinations(tris[k], 2))
    return kinds, len(tris) - len(placed)


# ---------------------------------------------------------------------------------------------- pumping
def random_symmetric_law(k, rng, density):
    """a radius-1 law with k hidden labels per knot on threads and rings. Windows: inner (left, centre, right) with all three
    inner knots; next-to-end (end label, centre, right); end (end label, neighbour). A law allows a window or its mirror image."""
    inner = set()
    for t in itertools.product(range(k), repeat=3):
        if rng.random() < density:
            inner.add(t)
            inner.add(t[::-1])
    nexts = {t for t in itertools.product(range(k), repeat=3) if rng.random() < density}
    ends = {t for t in itertools.product(range(k), repeat=2) if rng.random() < density}
    return inner, nexts, ends


def thread_lengths(law, k, nmax):
    """the thread lengths 4..nmax that the law allows. Knots 1..n: the window at knot 1 is (l1, l2) in ends; at knot 2 it is
    (l1, l2, l3) in nexts (l1 the end's label); at knots 3..n-2 (l_{i-1}, l_i, l_{i+1}) in inner; at knot n-1 it is
    (l_n, l_{n-1}, l_{n-2}) in nexts and at knot n (l_n, l_{n-1}) in ends. A transfer matrix on consecutive label pairs."""
    inner, nexts, ends = law
    allowed = set()
    cur = set()
    for a, b in ends:
        for c in range(k):
            if (a, b, c) in nexts:
                cur.add((b, c))           # knots 1..3 placed; windows at knots 1 and 2 checked
    i = 3
    while i < nmax and cur:
        for b, c in cur:                  # end with n = i + 1: windows at knots i and i + 1
            if any((d, c) in ends and (d, c, b) in nexts for d in range(k)):
                allowed.add(i + 1)
                break
        cur = {(c, d) for b, c in cur for d in range(k) if (b, c, d) in inner}   # window at knot i, inner
        i += 1
    return allowed


def ring_lengths(law, k, nmax):
    """the ring lengths 3..nmax the law allows: closed walks of that length on label pairs with every triple inner"""
    inner = law[0]
    allowed = set()
    for start in itertools.product(range(k), repeat=2):
        cur = {start}
        for length in range(1, nmax + 1):
            cur = {(b, c) for a, b in cur for c in range(k) if (a, b, c) in inner}
            if not cur:
                break
            if length >= 3 and start in cur:
                allowed.add(length)
    return allowed


def counter_law(K):
    """the control: labels 0..K-1 are distances from a seed (label 0). Inner windows rise or fall by one, with the seed's
    (1, 0, 1) the only turn; ends may have any label one away from their neighbour's. Threads up to about 2K are allowed and no
    ring, since a ring's labels would need a largest one, which no window allows; the labels needed grow with the length."""
    inner = set()
    for b in range(K):
        for a, c in ((b - 1, b + 1), (b + 1, b - 1)):
            if 0 <= a < K and 0 <= c < K:
                inner.add((a, b, c))
    if K > 1:
        inner.add((1, 0, 1))
    ends = {(a, b) for a in range(K) for b in range(K) if abs(a - b) == 1}
    return inner, set(inner), ends


def labelled_thread(law, k, n):
    """a labelling l_1..l_n of the thread of n knots (n >= 4) that the law allows, or None. Dynamic programming over consecutive
    label pairs with back pointers: layer j maps the pair (l_{j+2}, l_{j+3}) to the pair before it (layer 0 to the end label l_1)."""
    inner, nexts, ends = law
    layers = [{}]
    for a, b in ends:
        for c in range(k):
            if (a, b, c) in nexts and (b, c) not in layers[0]:
                layers[0][(b, c)] = a                    # knots 1..3 placed: (l2, l3) <- l1
    while len(layers) < n - 3:                           # place knots 4..n-1, checking the inner window of the knot before
        nxt = {}
        for (b, c) in layers[-1]:
            for d in range(k):
                if (b, c, d) in inner and (c, d) not in nxt:
                    nxt[(c, d)] = (b, c)
        layers.append(nxt)
    for (b, c) in layers[-1]:                            # knot n: windows at knots n-1 and n
        for d in range(k):
            if (d, c) in ends and (d, c, b) in nexts:
                seq = [d, c, b]
                pair = (b, c)
                for j in range(len(layers) - 1, 0, -1):
                    pair = layers[j][pair]
                    seq.append(pair[0])
                seq.append(layers[0][pair])
                labels = seq[::-1]
                assert len(labels) == n and windows_ok(law, labels)
                return labels
    return None


def windows_ok(law, labels, ring=False):
    """does the labelled thread (or ring) have every window in the law?"""
    inner, nexts, ends = law
    n = len(labels)
    if ring:
        return all((labels[i - 1], labels[i], labels[(i + 1) % n]) in inner for i in range(n))
    if n < 4:
        return False
    ok = (labels[0], labels[1]) in ends and (labels[0], labels[1], labels[2]) in nexts
    ok = ok and (labels[-1], labels[-2]) in ends and (labels[-1], labels[-2], labels[-3]) in nexts
    return ok and all((labels[i - 1], labels[i], labels[i + 1]) in inner for i in range(2, n - 2))


def pump(labels, r=1):
    """the proof's construction: positions p >= r + 2 (1-based: p - r - 1 >= 1 so the window holds no end knot) spaced 2r + 1
    apart; two with equal radius-r windows; glue the segment between them into a ring"""
    n = len(labels)
    seen = {}
    p = r + 2                              # 1-based position; window p-r..p+r must avoid knots 1 and n
    while p + r <= n - 1:
        w = tuple(labels[p - 1 - r: p + r])
        if w in seen:
            q = seen[w]
            return labels[q - 1: p - 1]
        seen[w] = p
        p += 2 * r + 1
    return None


# ---------------------------------------------------------------------------------------------- substrates that vary
def existence_joint(absent_order="free"):
    """potential sites -2, -1, 0, 1 on a line, the seed at 0. History: existence e_m2, e_m1, e_p1 (the grown thread is an
    interval containing 0) and the pair bits h_m1p1, h_m2p1 (did site -1, -2 come before site 1). States: the distinction at
    each edge position x_m25, x_m15, x_m05, x_p05, x_p15 (a seam when both sites exist, an open end when one does) and each
    site's own open end u_m2, u_m1, u_0, u_p1. An existing site's three distinctions sum to 0; variables of sites that do not
    exist are free (forgotten). The pair bits of a pair that does not exist are free (absent_order="free", the forgetting
    reading) or, in the control, set to 0 (absent_order="zero"), so that their value says which sites exist."""
    names = ["e_m2", "e_m1", "e_p1", "h_m1p1", "h_m2p1",
             "x_m25", "x_m15", "x_m05", "x_p05", "x_p15", "u_m2", "u_m1", "u_0", "u_p1"]
    site_dist = {-2: ("x_m25", "x_m15", "u_m2"), -1: ("x_m15", "x_m05", "u_m1"), 0: ("x_m05", "x_p05", "u_0"),
                 1: ("x_p05", "x_p15", "u_p1")}

    def ok(v):
        exists = {-2: v["e_m2"], -1: v["e_m1"], 0: 1, 1: v["e_p1"]}
        if exists[-2] and not exists[-1]:
            return False
        for s, ds in site_dist.items():
            if exists[s] and sum(v[d] for d in ds) % 2:
                return False
        # the order: births after the seed interleave the left chain (-1 then -2) with the right one (1)
        if exists[1] and exists[-2]:
            if v["h_m2p1"] and not v["h_m1p1"]:     # -2 before 1 needs -1 before 1
                return False
        if absent_order == "zero":
            if not (exists[1] and exists[-1]) and v["h_m1p1"]:
                return False
            if not (exists[1] and exists[-2]) and v["h_m2p1"]:
                return False
        return True
    return from_predicate(names, ok), {"existence": {"e_m2", "e_m1", "e_p1"}, "order": {"h_m1p1", "h_m2p1"},
                                       "state": set(names[5:])}


def substrate_restrictions(R):
    """the relation restricted to each fixed substrate (each allowed value of the existence bits)"""
    out = []
    for em2, em1, ep1 in itertools.product((0, 1), repeat=3):
        S = R.restrict({"e_m2": em2, "e_m1": em1, "e_p1": ep1})
        if S.rows:
            out.append(((em2, em1, ep1), S))
    return out


def state_reading_joint(n):
    """the control rule that reads a state: on the thread P_n, an inner knot that is the parent of its right neighbour has its
    own open end set to 1, and the parent of its left neighbour has it set to 0. So the history depends on the states."""
    dist, edges = thread(n)
    X = parity_law(dist)
    H = history_relation(n, "seam")
    J = product(H, X)
    keep = []
    for r in J.rows:
        v = {name: r >> i & 1 for i, name in enumerate(J.names)}
        good = True
        for i in range(1, n - 1):
            own = dist[i][2]
            right_child = v[f"h_s{i}"] == 1          # knot i came before knot i+1
            left_child = v[f"h_s{i - 1}"] == 0       # knot i came before knot i-1
            if right_child and v[own] != 1:
                good = False
            if left_child and not right_child and v[own] != 0:
                good = False
        if good:
            keep.append(r)
    return Rel(J.names, keep)


def pump_bound(r, k):
    """Theorem 4's bound: a thread of at least this many knots has two equal radius-r windows of inner knots at least 2r + 1
    apart (positions r + 2, r + 2 + (2r + 1), ..., n - 1 - r outnumber the k^(2r+1) windows)"""
    return (2 * r + 1) * k ** (2 * r + 1) + 2 * r + 3
