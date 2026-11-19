"""Referee R1 for MEET-ONCE-20261119-001: the referee's own table read to distance 8 (every bond of at most nine distinctions,
enumerated with a flow bound), its invariant, and an exact states test.  No study code imported.

The junction graph: one vertex per junction, plus the outside vertex o when some distinction is loose; one edge per distinction
(a shared distinction joins its two junctions, a loose one joins its junction to o).  The equation space is the graph's cut
space, and its bonds (cuts whose two sides are connected) are the bonds of the arrangement.

Bonds of size at most L: every bond has a side S without the root (o if present, else junction 0); S is enumerated as a connected
set grown from its least vertex m (vertices below m and the root held out).  At each step one neighbour of S still free is either
added to S or held out; a branch is cut when the maximum flow from S to the held-out set exceeds L, since every cut extending it
is then larger than L.  When no free neighbour is left, every neighbour of S is held out, so the cut is exactly the edges leaving
S; it is kept when its size is at most L and the rest of the graph is connected.  Each bond is found once, from its side S.
"""
from collections import defaultdict, deque
from itertools import combinations


def graph(stars):
    """stars on distinctions 0..nb-1.  Returns (vertices, root, edges: list of (u, v) per distinction, adjacency multiset)."""
    own = defaultdict(list)
    for j, s in enumerate(stars):
        for b in s:
            own[b].append(j)
    n = len(stars)
    nb = 1 + max(own)
    loose = any(len(own[b]) == 1 for b in range(nb))
    o = n if loose else None
    edges = []
    for b in range(nb):
        js = own[b]
        edges.append((js[0], o) if len(js) == 1 else (js[0], js[1]))
    V = n + (1 if loose else 0)
    adj = defaultdict(list)                            # vertex -> list of (neighbour, distinction)
    for b, (u, v) in enumerate(edges):
        adj[u].append((v, b))
        adj[v].append((u, b))
    return V, (o if loose else 0), edges, adj


def flow_exceeds(V, adj, S, T, L):
    """Is the maximum number of edge-disjoint paths from S to T more than L?  (Undirected unit edges; augmenting paths.)"""
    used = {}                                          # (distinction, direction) -> 1 when flow goes u -> v along it
    flow = 0
    while flow <= L:
        prev = {x: None for x in S}
        q = deque(S)
        hit = None
        while q and hit is None:
            x = q.popleft()
            for y, b in adj[x]:
                if y in prev:
                    continue
                # residual capacity of x -> y along b: 1 - f(x->y) + f(y->x), with f in {0, 1}, flow on b one way only
                if used.get((b, x, y)):
                    continue
                prev[y] = (x, b)
                if y in T:
                    hit = y
                    break
                q.append(y)
        if hit is None:
            return False
        y = hit
        while prev[y] is not None:
            x, b = prev[y]
            if used.get((b, y, x)):
                del used[(b, y, x)]
            else:
                used[(b, x, y)] = 1
            y = x
        flow += 1
    return True


def small_bonds(stars, L=9):
    """Every bond of at most L distinctions, as bitmasks of distinctions."""
    V, root, edges, adj = graph(stars)
    verts = [v for v in range(len(stars)) if v != root]        # junctions other than the root
    found = set()

    def rest_connected(S):
        rest = [v for v in range(V) if v not in S]
        if not rest:
            return False
        seen = {rest[0]}
        st = [rest[0]]
        while st:
            x = st.pop()
            for y, _ in adj[x]:
                if y not in S and y not in seen:
                    seen.add(y)
                    st.append(y)
        return len(seen) == len(rest)

    def go(S, T):
        if flow_exceeds(V, adj, S, T, L):
            return
        free = None
        for x in S:
            for y, _ in adj[x]:
                if y not in S and y not in T:
                    free = y
                    break
            if free is not None:
                break
        if free is None:
            cut = [b for x in S for y, b in adj[x] if y not in S]
            if len(cut) <= L and rest_connected(S):
                found.add(sum(1 << b for b in cut))
            return
        go(S | {free}, T)
        go(S, T | {free})

    for m in verts:
        go(frozenset([m]), frozenset([root] + [v for v in verts if v < m]))
    return found


def table8(stars, L=9):
    """Pairs of distinctions whose least bond has at most L distinctions -> that size (the table read to distance L - 1)."""
    t = {}
    for w in sorted(small_bonds(stars, L), key=lambda w: w.bit_count()):
        s = w.bit_count()
        bits = [x for x in range(w.bit_length()) if w >> x & 1]
        for p in combinations(bits, 2):
            if p not in t:
                t[p] = s
    return t


def labelled(nb, t):
    import networkx as nx
    g = nx.Graph()
    g.add_nodes_from(range(nb))
    for (a, b), s in t.items():
        g.add_edge(a, b, d=s, ds=str(s))
    return g


def invariant(nb, t):
    import networkx as nx
    return nx.weisfeiler_lehman_graph_hash(labelled(nb, t), edge_attr="ds", iterations=5)


def span(words):
    basis = {}
    for r in words:
        while r:
            p = r.bit_length() - 1
            if p not in basis:
                basis[p] = r
                break
            r ^= basis[p]
    return basis


def in_span(basis, r):
    while r:
        p = r.bit_length() - 1
        if p not in basis:
            return False
        r ^= basis[p]
    return True


def junction_graph_iso(A, B):
    """Junction graphs isomorphic with o a plain vertex (edge multiplicities kept): then the cut spaces correspond."""
    import networkx as nx

    def jg(stars):
        V, root, edges, _ = graph(stars)
        g = nx.Graph()
        g.add_nodes_from(range(V))
        for u, v in edges:
            if g.has_edge(u, v):
                g[u][v]["m"] += 1
            else:
                g.add_edge(u, v, m=1)
        return g
    ga, gb = jg(A), jg(B)
    return nx.is_isomorphic(ga, gb, edge_match=lambda x, y: x["m"] == y["m"])


def same_states(A, B, nb, tA, tB, cap=3000000):
    """Exact: a bijection of distinctions keeping the table read to distance 8 and carrying span(A) onto span(B).  Every carrier
    keeps the full table, hence this one, so the answer is the states test.  Distinctions held by the same junctions are taken in
    increasing order (swapping two of them keeps the span).  True / False / None (cap)."""
    if len(span(sum(1 << x for x in s) for s in A)) != len(span(sum(1 << x for x in s) for s in B)):
        return False
    bB = span(sum(1 << x for x in s) for s in B)
    own = defaultdict(list)
    for j, s in enumerate(A):
        for b in s:
            own[b].append(j)
    sig = {b: tuple(sorted(own[b])) for b in range(nb)}

    def rows(t):
        r = defaultdict(list)
        for (a, b), s in t.items():
            r[a].append(s)
            r[b].append(s)
        return {x: tuple(sorted(r[x])) for x in range(nb)}
    rA, rB = rows(tA), rows(tB)

    def get(t, a, b):
        return t.get((a, b) if a < b else (b, a), 0)
    cand = {x: [y for y in range(nb) if rA[x] == rB[y]] for x in range(nb)}
    if any(not c for c in cand.values()):
        return False
    order = sorted(range(nb), key=lambda b: (len(cand[b]), sig[b], b))
    # keep twins together and in increasing order
    order = sorted(range(nb), key=lambda b: (min(order.index(c) for c in range(nb) if sig[c] == sig[b]), b))
    prev = {order[i]: order[i - 1] for i in range(1, nb) if sig[order[i]] == sig[order[i - 1]]}
    pos = {x: k for k, x in enumerate(order)}
    done_at = defaultdict(list)
    for j, s in enumerate(A):
        done_at[max(s, key=lambda b: pos[b])].append(j)
    img, used, steps = {}, set(), [0]

    def go(k):
        steps[0] += 1
        if steps[0] > cap:
            return None
        if k == nb:
            return True
        x = order[k]
        for y in cand[x]:
            if y in used or (x in prev and y < img[prev[x]]):
                continue
            if any(get(tA, x, z) != get(tB, y, w) for z, w in img.items()):
                continue
            img[x] = y
            used.add(y)
            if all(in_span(bB, sum(1 << img[b] for b in A[j])) for j in done_at[x]):
                r = go(k + 1)
                if r or r is None:
                    if not r:
                        del img[x]
                        used.discard(y)
                    return r
            del img[x]
            used.discard(y)
        return False
    return go(0)
