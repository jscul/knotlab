"""The extended cluster rule (CLUSTER-ALL-20261119-001B), from RING-PAIR-20261119-001's cover model.

A start is knots with places (sizes) sharing distinctions (edges, one entry per shared distinction).  Live knots have open
distinctions (places - shared >= 1); a knot's round-1 demand d is the number of round-1 groups containing it.
- **Out of scope:** a round-1 group of three or more knots (a hyperedge) sharing two or more knots with another block.
- **Stall:** some live knot has d > open (the census's "cannot start").
- **Blocks:** for every knot w, the live knots sharing a distinction with w are pairwise candidates through w: one simplex when
  there are two or more; simplices sharing two or more knots merge into one block whose clusters are the sets connected through
  its edges.  Pairs covered by a round-1 group of three or more are not edges; such a group is a hyperedge block whose clusters
  are one knot or all of it, made in one round (weight y^(2 - |G|) on top of its knots').
- **Pendants:** each live knot w has s = open - d surplus offshoots.  An offshoot's demand is open - 1 (it pairs with each other
  child of w), and the floor gives a one-parent junction max(d, 2) fresh distinctions; so an offshoot is a leaf when open >= 3
  (series y), the start of an endless chain when open = 2 (y / (1 - y)), and a point carrying two endless chains when open = 1
  (y / (1 - y)^2), unless that point takes the start's only loose distinction (its parity is then implied and it closes: y).  A knot's weight in the clusters is y prod over its pendants (1 + U_p).
- **Relay:** a finite component of the complex (a tree of blocks with no chains) closes at its top, the cluster of all its points.
  When other live knots exist, the top's parity is not implied, the floor gives it one fresh distinction, and that offshoot
  carries two endless chains: y^(m + 1) / (1 - y)^2 for a top of m points.
- **Count:** junctions of round t = [y^(t+1)] of the clusters' series, the dissymmetry count of the block tree (deck orbits where
  the complex has cycles), plus one per knot that is not live (a round-0 junction only)."""
import itertools
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / 'experiments/JOIN-GROWTH-20261118-001B/JOIN-GROWTH-20261118-001B-E001_joins'))
import joinlib as J  # noqa: E402


def _mul(a, b, N):
    out = [0] * (N + 1)
    for i, x in enumerate(a):
        if x:
            for j in range(N + 1 - i):
                if b[j]:
                    out[i + j] += x * b[j]
    return out


def _geom(k, N):
    """y / (1 - y)^k up to y^N (k = 0: y)."""
    s = [0] * (N + 1)
    for n in range(1, N + 1):
        # coefficient of y^n in y (1 - y)^(-k) = C(n - 1 + k - 1, k - 1); k = 0 gives only y^1
        if k == 0:
            s[n] = 1 if n == 1 else 0
        else:
            from math import comb
            s[n] = comb(n - 1 + k - 1, k - 1)
    return s


def analyse(sizes, edges):
    n = len(sizes)
    sh = [0] * n
    nb = defaultdict(set)
    for a, b in edges:
        sh[a] += 1
        sh[b] += 1
        nb[a].add(b)
        nb[b].add(a)
    opn = [sizes[k] - sh[k] for k in range(n)]
    live = [k for k in range(n) if opn[k] >= 1]
    P = J.S.from_junctions(J.stars_from(sizes, edges))
    groups = P.groups_among(live)
    hyper = [tuple(sorted(g)) for g in groups if len(g) > 2]
    covered = {p for G in hyper for p in itertools.combinations(G, 2)}
    d = [0] * n
    for g in groups:
        for j in g:
            d[j] += 1
    if any(d[k] > opn[k] for k in live):
        return {'scope': True, 'stall': True}
    ls = set(live)
    simp = []
    for w in range(n):
        B = tuple(sorted(nb[w] & ls))
        if len(B) >= 2:
            simp.append(B)
    # merge simplices sharing two or more points (an edge) into one block, a face-connected piece; its graph is the union of the
    # simplices' edges
    groups_ = [set(B) for B in simp]
    edges_of = [set(itertools.combinations(B, 2)) - covered for B in simp]
    keep = [i for i in range(len(simp)) if edges_of[i]]
    groups_ = [groups_[i] for i in keep]
    edges_of = [edges_of[i] for i in keep]
    merged = True
    while merged:
        merged = False
        for i in range(len(groups_)):
            for j in range(i + 1, len(groups_)):
                if len(groups_[i] & groups_[j]) >= 2:
                    groups_[i] |= groups_.pop(j)
                    edges_of[i] |= edges_of.pop(j)
                    merged = True
                    break
            if merged:
                break
    for g, e in zip(groups_, edges_of):           # drop points the remaining edges no longer reach
        pts = {x for p in e for x in p}
        g &= pts
    blocks = [tuple(sorted(g)) for g in groups_]
    bedges = [e for e in edges_of]
    for G in hyper:
        if any(len(set(G) & set(B)) >= 2 for B in blocks) or any(len(set(G) & set(H)) >= 2 for H in hyper if H != G):
            return {'scope': False, 'why': 'a round-1 group of three sharing two knots with another block'}
    nh = len(blocks)
    blocks += hyper                               # a round-1 group of three or more: all its points or one
    bedges += [None] * len(hyper)
    pend = {k: [] for k in live}
    for k in live:
        s = opn[k] - d[k]
        kind = 0 if opn[k] >= 3 else (1 if opn[k] == 2 else 2)
        if kind == 2 and len(live) == 1:
            kind = 0                  # the start's only loose distinction: its offshoot takes every loose bit, implied, closes
        pend[k] = [kind] * s
    return {'scope': True, 'stall': False, 'n': n, 'live': live, 'blocks': blocks, 'bedges': bedges, 'pend': pend, 'open': opn,
            'demand': d, 'hyper': len(hyper)}


def series(sizes, edges, N):
    """c(0..N-1) under the rule, or None out of scope; 'stall' when round 1 stalls."""
    out = _series(sizes, edges, N + 12)      # the hyper-blocks' downward shifts lose the top terms; keep a margin
    return out if not isinstance(out, list) else out[:N]


def _series(sizes, edges, N):
    A = analyse(sizes, edges)
    if not A['scope']:
        return None
    if A['stall']:
        return 'stall'
    n, live, blocks, pend, bedges = A['n'], A['live'], A['blocks'], A['pend'], A['bedges']
    adjb = []
    for i, B in enumerate(blocks):
        a = defaultdict(set)
        for x, z in (bedges[i] or []):
            a[x].add(z)
            a[z].add(x)
        adjb.append(a)

    def connected_in(i, S):
        S = set(S)
        if not S:
            return True
        st = [next(iter(S))]
        seen = {st[0]}
        while st:
            x = st.pop()
            for z in adjb[i][x] & S:
                if z not in seen:
                    seen.add(z)
                    st.append(z)
        return seen == S
    subsets, shiftw = {}, {}
    for i, B in enumerate(blocks):
        if bedges[i] is None:                     # hyper-block: one point, or all of them in one round
            subsets[i] = [(z,) for z in B] + [tuple(B)]
            shiftw[i] = len(B) - 2
        else:
            subsets[i] = [S for m in range(1, len(B) + 1) for S in itertools.combinations(B, m) if connected_in(i, S)]
            shiftw[i] = 0

    def down(a, k):
        if k == 0:
            return a
        assert all(x == 0 for x in a[:k]), 'negative power'
        return a[k:] + [0] * k
    one = [1] + [0] * N
    yv = [0, 1] + [0] * (N - 1)
    weight = {}
    for k in live:
        w = yv
        for kind in pend[k]:
            w = _mul(w, [a + b for a, b in zip(one, _geom(kind, N))], N)
        weight[k] = w
    # components of live knots through blocks
    parent = {k: k for k in live}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    for B in blocks:
        for v in B[1:]:
            parent[find(v)] = find(B[0])
    comps = defaultdict(list)
    for k in live:
        comps[find(k)].append(k)
    at = defaultdict(list)
    for i, B in enumerate(blocks):
        for z in B:
            at[z].append(i)
    U = {(i, z): [0] * (N + 1) for i, B in enumerate(blocks) for z in B}

    def phi(i, z):
        # sum over sets S of the block's other points with S + z connected in the block, of prod U(B, w) over S
        r = list(one)
        for S in subsets[i]:
            if z in S and len(S) >= 2:
                pr = one
                for w in S:
                    if w != z:
                        pr = _mul(pr, U[(i, w)], N)
                if bedges[i] is None:
                    pr = down(pr, shiftw[i])
                r = [a + b for a, b in zip(r, pr)]
        return r
    for _ in range(N + 1):
        new = {}
        for (i, z) in U:
            r = weight[z]
            for j in at[z]:
                if j != i:
                    r = _mul(r, phi(j, z), N)
            new[(i, z)] = r
        if new == U:
            break
        U = new
    C = [0] * (N + 1)
    C[1] += n - len(live)           # knots that are not live: round-0 junctions only
    for root, ks in comps.items():
        ks_set = set(ks)
        cb = [i for i, B in enumerate(blocks) if B[0] in ks_set]
        Cc = [0] * (N + 1)
        for x in ks:
            r = weight[x]
            for i in at[x]:
                r = _mul(r, phi(i, x), N)
            Cc = [a + b for a, b in zip(Cc, r)]
        for i in cb:
            for S in subsets[i]:
                if len(S) >= 2:
                    pr = one
                    for v in S:
                        pr = _mul(pr, U[(i, v)], N)
                    if bedges[i] is None:
                        pr = down(pr, shiftw[i])
                    Cc = [a - (len(S) - 1) * b for a, b in zip(Cc, pr)]
        # a tree of blocks (no cycle through distinct blocks) and every block simply connected: Euler count of its edges and
        # triangles is checked by blocks being face-connected unions of simplices (assumed simply connected)
        tree = len(ks) + len(cb) - sum(len(blocks[i]) for i in cb) == 1
        finite = tree and all(kind == 0 for k in ks for kind in pend[k])
        if finite and len(comps) > 1:
            m = len(ks) + sum(len(pend[k]) for k in ks)
            m -= sum(shiftw[i] for i in cb if bedges[i] is None)   # a hyperedge tops one round per extra knot early
            relay = [0] * (N + 1)
            g = _geom(2, N)           # y / (1 - y)^2
            for e in range(1, N + 1 - m):
                relay[m + e] = g[e]
            Cc = [a + b for a, b in zip(Cc, relay)]
        C = [a + b for a, b in zip(C, Cc)]
    return C[1:]
