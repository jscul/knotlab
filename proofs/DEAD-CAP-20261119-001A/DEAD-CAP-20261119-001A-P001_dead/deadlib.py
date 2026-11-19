"""DEAD-CAP-20261119-001A-P001: the relayed map of a start within five places, dead knots included, read piece by piece.

For a start (sizes, edges with one entry per shared distinction) this computes, from the definitions:
- the live knots, the blocks N(w) ∩ live with at least two points (one per knot w, live or dead), each live knot's demand d (its
  candidate partners) and open count;
- pendant points: spares (no ray), and ray pendants with R = 1 or 2 rays;
- the pieces (components of the point-block incidence graph) and each piece's cycle rank.

Then the theorem's reading:
- **a tree piece:** its pendant rays, plus a relay's two when it is finite and the start has two or more pieces;
- **a one-cycle piece:** its round-weight W = A(z)/(1 - z)^j, built from the cycle's points and blocks and the trees hanging off the
  cycle;
- **a piece of cycle rank two or more:** exponential, with no rate given.

Rationals in z are kept as (numerator, power of (1 - z)) with integer coefficient lists of length NS."""
import itertools
from collections import Counter, defaultdict

import networkx as nx

NS = 80


def pmul(a, b):
    c = [0] * NS
    nb = [(j, y) for j, y in enumerate(b) if y]
    for i, x in enumerate(a):
        if x:
            for j, y in nb:
                if i + j >= NS:
                    break
                c[i + j] += x * y
    return c


def padd(a, b):
    return [x + y for x, y in zip(a, b)]


def mono(c):
    p = [0] * NS
    for i, x in enumerate(c):
        p[i] = x
    return p


ONE, Z, ONEZ, OMZ = mono([1]), mono([0, 1]), mono([1, 1]), mono([1, -1])


def ppow(p, k):
    r = ONE
    for _ in range(k):
        r = pmul(r, p)
    return r


class Rat:
    """num / (1 - z)^j."""

    def __init__(self, num, j=0):
        self.num, self.j = num, j

    def __mul__(self, o):
        return Rat(pmul(self.num, o.num), self.j + o.j)

    def __add__(self, o):
        j = max(self.j, o.j)
        return Rat(padd(pmul(self.num, ppow(OMZ, j - self.j)), pmul(o.num, ppow(OMZ, j - o.j))), j)

    def series(self):
        inv = [1] * NS  # 1/(1-z)
        s = self.num
        for _ in range(self.j):
            s = pmul(s, inv)
        return s


R_ONE = Rat(ONE)


def analyse(sizes, edges):
    n = len(sizes)
    sh = Counter()
    nb = defaultdict(set)
    for a, b in edges:
        sh[a] += 1
        sh[b] += 1
        nb[a].add(b)
        nb[b].add(a)
    opn = [sizes[k] - sh[k] for k in range(n)]
    live = {k for k in range(n) if opn[k] >= 1}
    blocks = {w: frozenset(nb[w] & live) for w in range(n) if len(nb[w] & live) >= 2}
    of = defaultdict(list)
    for w, B in blocks.items():
        for k in B:
            of[k].append(w)
    partners = {k: set().union(*[blocks[w] for w in of[k]]) - {k} if of[k] else set() for k in live}
    d = {k: len(partners[k]) for k in live}
    dsum = {k: sum(len(blocks[w]) - 1 for w in of[k]) for k in live}
    Rr = {1: 2, 2: 1}
    spares = {k: (opn[k] - d[k]) if opn[k] >= 3 else 0 for k in live}
    raypend = {k: (opn[k] - d[k]) if opn[k] <= 2 else 0 for k in live}
    rays = {k: raypend[k] * Rr.get(opn[k], 0) for k in live}
    G = nx.Graph()
    G.add_nodes_from(('p', k) for k in live)
    for w, B in blocks.items():
        for k in B:
            G.add_edge(('b', w), ('p', k))
    pieces = []
    for comp in nx.connected_components(G):
        H = G.subgraph(comp)
        pts = sorted(x[1] for x in comp if x[0] == 'p')
        rank = H.number_of_edges() - H.number_of_nodes() + 1
        pieces.append({'points': pts, 'blocks': sorted(x[1] for x in comp if x[0] == 'b'), 'rank': rank,
                       'rays': sum(rays[k] for k in pts), 'H': H})
    return {'n': n, 'open': opn, 'live': live, 'blocks': blocks, 'of': dict(of), 'd': d, 'dsum': dsum, 'spares': spares,
            'raypend': raypend, 'rays': rays, 'pieces': pieces, 'nb': nb}


def profile(A, k):
    return tuple(sorted(len(A['blocks'][w]) for w in A['of'].get(k, [])))


def hang(A, q, parent_block):
    """Generating function of the connected sets that contain point q, within what hangs from q away from parent_block."""
    g = Rat(pmul(Z, ppow(ONEZ, A['spares'][q])), A['raypend'][q] if A['open'][q] == 2 else 0)
    if A['open'][q] == 1 and A['raypend'][q]:
        raise ValueError('a two-ray pendant inside a piece')
    for w in A['of'].get(q, []):
        if w == parent_block:
            continue
        for p in A['blocks'][w]:
            if p != q:
                g = g * (R_ONE + hang(A, p, w))
    return g


def one_cycle_W(A, piece):
    """For a piece of cycle rank 1: (n, W as Rat) along its cycle of points and blocks."""
    H = piece['H']
    cyc = nx.find_cycle(H)
    nodes = [u for u, v in cyc]
    pts = [x[1] for x in nodes if x[0] == 'p']
    blks = [x[1] for x in nodes if x[0] == 'b']
    W = R_ONE
    for k in pts:
        if A['rays'][k]:
            raise ValueError('a ray on a cycle point')
        W = W * Rat(pmul(Z, ppow(ONEZ, A['spares'][k])))
        for w in A['of'][k]:
            if w not in blks:
                raise ValueError('a cycle point in a third block')
    on = set(pts)
    for w in blks:
        for p in A['blocks'][w]:
            if p not in on:
                W = W * (R_ONE + hang(A, p, w))
    return len(pts), W


def rate_of(W):
    s = W.series()
    f = lambda z: sum(c * z ** i for i, c in enumerate(s) if c)  # noqa: E731
    if abs(f(1.0) - 1) < 1e-9 and W.j == 0:
        return 1.0
    lo, hi = 0.0, 1.0
    for _ in range(100):
        mid = (lo + hi) / 2
        if f(mid) < 1:
            lo = mid
        else:
            hi = mid
    return 1 / ((lo + hi) / 2)


def char_poly(W):
    """Q(z) = (1 - z)^j - A(z): the numerator of 1 - W, as a coefficient list trimmed."""
    q = padd(ppow(OMZ, W.j), [-x for x in W.num])
    while q and q[-1] == 0:
        q.pop()
    return q


def annihilated(counts, Q, extra):
    """Whether counts satisfy the recurrence Q(E^-1) (1 - E^-1)^extra counts = 0 at every round where it applies."""
    P = Q
    for _ in range(extra):
        P = [x - y for x, y in zip(P + [0], [0] + P)]
    D = len(P) - 1
    vals = [sum(P[i] * counts[t - i] for i in range(D + 1)) for t in range(D, len(counts))]
    return len(vals), vals


def reading(A):
    """The theorem's growth class: ('closes' | 'dimension R' | 'exponential', details)."""
    pcs = A['pieces']
    many = len(pcs) >= 2
    best, detail = None, []
    order = {'closes': 0}
    out = 0
    exp = []
    for P in pcs:
        if P['rank'] == 0:
            r = P['rays'] if P['rays'] else (2 if many else 0)
            out = max(out, r)
            detail.append(('tree', r))
        elif P['rank'] == 1:
            n, W = one_cycle_W(A, P)
            bare = W.j == 0 and W.num == pmul(ppow(Z, n), ONE)
            if bare:
                out = max(out, 1)
                detail.append(('bare cycle', n))
            else:
                exp.append(rate_of(W))
                detail.append(('one cycle', round(exp[-1], 6)))
        else:
            exp.append(None)
            detail.append(('cycles', P['rank']))
    if exp:
        return 'exponential', detail
    return ('closes' if out == 0 else f'dimension {out}'), detail


# ---- exact counts from the branch system --------------------------------------------------------------------------------------
def _trunc(p, D):
    return p[:D + 1] + [0] * (NS - D - 1)


def _ser_inv_1mz(p, k, D):
    """p / (1 - z)^k, truncated at degree D."""
    s = p[:]
    for _ in range(k):
        acc, out = 0, []
        for x in s:
            acc += x
            out.append(acc)
        s = out
    return _trunc(s, D)


def pendant_factor(A, q, D):
    """e_q: the series of q's pendant extensions (1 + z per spare, 1/(1 - z) per one-ray pendant, 1 + z/(1 - z)^2 per two-ray
    pendant), and phi_q = sum over its pendant points of (clusters through that point) / e_q-part, as the series
    e_q * (1 + sum phi) used in the pointing."""
    sp, rp, o = A['spares'][q], A['raypend'][q], A['open'][q]
    e = ppow(ONEZ, sp)
    pointed = [0] * NS  # sum over pendant points of the forced series, times the other factors
    # spares: factor (1+z); forced: z
    pieces = [(ONEZ, Z)] * sp
    if rp:
        if o == 2:
            one = _ser_inv_1mz(ONE, 1, D)
            forced = _ser_inv_1mz(Z, 2, D)  # sum_i z^(i+1)/(1-z)
            pieces += [(one, forced)] * rp
        elif o == 1:
            two = padd(ONE, _ser_inv_1mz(Z, 2, D))
            forced = _ser_inv_1mz(pmul(Z, ONEZ), 3, D)  # sum_{i,j} (1 + i + j) z^(1+i+j) = z(1 + z)/(1 - z)^3
            pieces += [(two, forced)] * rp
    full = ONE
    for f, _ in pieces:
        full = _trunc(pmul(full, f), D)
    for i, (f, g) in enumerate(pieces):
        prod = g
        for j, (f2, _) in enumerate(pieces):
            if j != i:
                prod = _trunc(pmul(prod, f2), D)
        pointed = padd(pointed, prod)
    return full, padd(full, pointed)


def piece_counts(A, P, T, relay):
    """Per-round junction counts of one piece to round T, from the branch system and the pointing identity."""
    D = T + 1
    inc = [(p, w) for w in P['blocks'] for p in A['blocks'][w]]
    E = {q: pendant_factor(A, q, D) for q in P['points']}
    b = {x: ONE for x in inc}
    for _ in range(D + 1):
        nb = {}
        for (p, w) in inc:
            prod = ONE
            for q in A['blocks'][w]:
                if q == p:
                    continue
                t = pmul(Z, E[q][0])
                for w2 in A['of'].get(q, []):
                    if w2 != w:
                        t = _trunc(pmul(t, b[(q, w2)]), D)
                prod = _trunc(pmul(prod, padd(ONE, t)), D)
            nb[(p, w)] = prod
        b = nb
    tot = [0] * NS
    for p in P['points']:
        r = pmul(Z, E[p][1])
        for w in A['of'].get(p, []):
            r = _trunc(pmul(r, b[(p, w)]), D)
        tot = padd(tot, r)
    out = []
    for t in range(T + 1):
        m = t + 1
        assert tot[m] % m == 0, ('pointing not integral', m, tot[m])
        out.append(tot[m] // m)
    if relay and P['rank'] == 0 and P['rays'] == 0:
        mpts = len(P['points']) + sum(A['spares'][q] for q in P['points'])  # the piece's points, its spares included
        for t in range(T + 1):
            k = t - (mpts - 1)
            if k >= 1:
                out[t] += k
    return out


def exact_counts(A, T):
    many = len(A['pieces']) >= 2
    tot = [0] * (T + 1)
    for P in A['pieces']:
        c = piece_counts(A, P, T, many)
        tot = [x + y for x, y in zip(tot, c)]
    # dead knots are junctions of round 0 too
    tot[0] += sum(1 for k in range(A['n']) if k not in A['live'])
    return tot


def branch_rate(A, P, iters=4000):
    """1/rho for a piece of rank >= 2: the largest z at which the system's least solution stays finite (bisection on floats)."""
    def ok(z):
        b = {(p, w): 1.0 for w in P['blocks'] for p in A['blocks'][w]}
        e = {}
        for q in P['points']:
            sp, rp, o = A['spares'][q], A['raypend'][q], A['open'][q]
            v = (1 + z) ** sp
            if rp and o == 2:
                v *= (1 / (1 - z)) ** rp
            elif rp and o == 1:
                v *= (1 + z / (1 - z) ** 2) ** rp
            e[q] = v
        for _ in range(iters):
            nb = {}
            for (p, w) in b:
                prod = 1.0
                for q in A['blocks'][w]:
                    if q == p:
                        continue
                    t = z * e[q]
                    for w2 in A['of'].get(q, []):
                        if w2 != w:
                            t *= b[(q, w2)]
                    prod *= 1 + t
                nb[(p, w)] = prod
            if max(nb.values()) > 1e12:
                return False
            if max(abs(nb[x] - b[x]) for x in b) < 1e-13:
                return True
            b = nb
        return True
    lo, hi = 0.0, 1.0
    for _ in range(50):
        mid = (lo + hi) / 2
        if ok(mid):
            lo = mid
        else:
            hi = mid
    return 1 / lo
