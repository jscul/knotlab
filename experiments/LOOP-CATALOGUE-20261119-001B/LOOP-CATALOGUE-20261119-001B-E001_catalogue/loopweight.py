"""A loop's round-weight W(y), from the cluster rule's own entry series (LOOP-CATALOGUE-20261119-001B; the advisor's form).

For a piece of the block graph with one cycle, going once round the loop passes blocks B_1, ..., B_m with ports a_i, b_i = a_(i+1).
  W(y) = prod_i T_i,  T_i = sum over connected sets S of B_i holding a_i and b_i of prod_(w in S - a_i) V_i(w),
where V_i(b_i) is the next port's weight with every block at it except B_i and B_(i+1), and V_i(w) for an interior point is the
rule's U(B_i, w) (the point with everything hanging from it).  The rule's rate is predicted to be 1 / y*, y* the root of W = 1 in
(0, 1).  The entry series U and phi are recomputed here exactly as in clusters._series (CLUSTER-ALL-20261119-001B)."""
import itertools
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import eddy as E  # noqa: E402
Cl = E.Cl


def entries(sizes, edges, N=40):
    A = Cl.analyse(sizes, edges)
    live, blocks, pend, bedges = A['live'], A['blocks'], A['pend'], A['bedges']
    adjb = []
    for i, B in enumerate(blocks):
        a = defaultdict(set)
        for x, z in (bedges[i] or []):
            a[x].add(z)
            a[z].add(x)
        adjb.append(a)

    def connected_in(i, S):
        S = set(S)
        st = [next(iter(S))]
        seen = {st[0]}
        while st:
            x = st.pop()
            for z in adjb[i][x] & S:
                if z not in seen:
                    seen.add(z)
                    st.append(z)
        return seen == S
    subsets = {}
    for i, B in enumerate(blocks):
        if bedges[i] is None:
            subsets[i] = [(z,) for z in B] + [tuple(B)]
        else:
            subsets[i] = [S for m in range(1, len(B) + 1) for S in itertools.combinations(B, m) if connected_in(i, S)]
    one = [1] + [0] * N
    yv = [0, 1] + [0] * (N - 1)
    weight = {}
    for k in live:
        w = yv
        for kind in pend[k]:
            w = Cl._mul(w, [a + b for a, b in zip(one, Cl._geom(kind, N))], N)
        weight[k] = w
    at = defaultdict(list)
    for i, B in enumerate(blocks):
        for z in B:
            at[z].append(i)
    U = {(i, z): [0] * (N + 1) for i, B in enumerate(blocks) for z in B}

    def down(a, k):
        return a[k:] + [0] * k if k else a

    def phi(i, z):
        r = list(one)
        for S in subsets[i]:
            if z in S and len(S) >= 2:
                pr = one
                for w in S:
                    if w != z:
                        pr = Cl._mul(pr, U[(i, w)], N)
                if bedges[i] is None:
                    pr = down(pr, len(blocks[i]) - 2)
                r = [a + b for a, b in zip(r, pr)]
        return r
    for _ in range(N + 1):
        new = {}
        for (i, z) in U:
            r = weight[z]
            for j in at[z]:
                if j != i:
                    r = Cl._mul(r, phi(j, z), N)
            new[(i, z)] = r
        if new == U:
            break
        U = new
    return A, subsets, weight, at, U, phi, N


def round_weight(sizes, edges, N=40):
    """W(y) as a list of coefficients, for a start whose only cycle piece has one cycle; None otherwise."""
    A, subsets, weight, at, U, phi, N = entries(sizes, edges, N)
    blocks, bedges = A['blocks'], A['bedges']
    cyc = [p for p in E.pieces(A) if p[2] >= 1]
    if len(cyc) != 1 or cyc[0][2] != 1:
        return None
    ks, bs = cyc[0][0], cyc[0][1]
    # the cycle of the bipartite block graph: strip leaves repeatedly
    nodes = {('k', k) for k in ks} | {('b', i) for i in bs}
    nb = defaultdict(set)
    for i in bs:
        for z in blocks[i]:
            nb[('b', i)].add(('k', z))
            nb[('k', z)].add(('b', i))
    deg = {v: len(nb[v]) for v in nodes}
    alive = set(nodes)
    stack = [v for v in nodes if deg[v] <= 1]
    while stack:
        v = stack.pop()
        if v not in alive:
            continue
        alive.discard(v)
        for u in nb[v]:
            if u in alive:
                deg[u] -= 1
                if deg[u] <= 1:
                    stack.append(u)
    # walk the cycle
    start = next(v for v in sorted(alive) if v[0] == 'k')
    order, prev, cur = [start], None, start
    while True:
        nxt = [u for u in nb[cur] if u in alive and u != prev]
        if not nxt:
            return None
        prev, cur = cur, nxt[0]
        if cur == start:
            break
        order.append(cur)
    seq = order  # k, b, k, b, ...
    m = len(seq) // 2
    W = [1] + [0] * N
    for t in range(m):
        a = seq[2 * t][1]
        bi = seq[2 * t + 1][1]
        b = seq[(2 * t + 2) % len(seq)][1]
        bnext = seq[(2 * t + 3) % len(seq)][1]
        # the next port's weight without its two cycle blocks
        vb = weight[b]
        for j in at[b]:
            if j not in (bi, bnext):
                vb = Cl._mul(vb, phi(j, b), N)
        T = [0] * (N + 1)
        for S in subsets[bi]:
            if a in S and b in S:
                pr = vb
                for w in S:
                    if w not in (a, b):
                        pr = Cl._mul(pr, U[(bi, w)], N)
                if bedges[bi] is None:
                    pr = pr[len(blocks[bi]) - 2:] + [0] * (len(blocks[bi]) - 2)
                T = [p + q for p, q in zip(T, pr)]
        W = Cl._mul(W, T, N)
    return W


def root(W, lo=1e-9, hi=1.0):
    f = lambda y: sum(c * y ** k for k, c in enumerate(W)) - 1  # noqa: E731
    if f(hi - 1e-12) < 0:
        return None
    for _ in range(200):
        mid = (lo + hi) / 2
        if f(mid) < 0:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2
