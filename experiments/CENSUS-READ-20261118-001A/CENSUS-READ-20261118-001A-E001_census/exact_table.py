"""An exact bond table with no limit on either side's size (the method of the RING-READ-20261118-001 referee, written afresh).

Every connected inner side J (the outside vertex o excluded) is grown from its least junction r by include/exclude branching on a
frontier junction.  A branch is cut when the maximum flow from J to the excluded junctions and o exceeds L: every side containing
J and avoiding them then has a cut of more than L distinctions.  At a leaf (no frontier left) J is a bond when its cut has at most
L distinctions and its complement, with o, is connected.  The table: for every pair, the smallest bond holding both, minus one,
for bonds of at most L distinctions; other pairs pooled at L.
"""
from collections import defaultdict, deque
from itertools import combinations


def capacities(stars):
    n = len(stars)
    own = defaultdict(list)
    for j, s in enumerate(stars):
        for b in s:
            own[b].append(j)
    cap = defaultdict(lambda: defaultdict(int))
    for b, js in own.items():
        u, v = (js[0], js[1]) if len(js) == 2 else (js[0], n)
        cap[u][v] += 1
        cap[v][u] += 1
    return n, {u: dict(vs) for u, vs in cap.items()}, own


def flow_exceeds(cap, J, sink, L):
    flow = defaultdict(int)
    total = 0
    while total <= L:
        prev = {s: None for s in J}
        dq = deque(J)
        hit = None
        while dq and hit is None:
            u = dq.popleft()
            for v, c in cap.get(u, {}).items():
                if v in prev or c - flow[(u, v)] <= 0:
                    continue
                prev[v] = u
                if v in sink:
                    hit = v
                    break
                dq.append(v)
        if hit is None:
            return False
        v = hit
        while prev[v] is not None:
            u = prev[v]
            flow[(u, v)] += 1
            flow[(v, u)] -= 1
            v = u
        total += 1
    return True


def exact_table(stars, H):
    """Exact distances up to H (bonds of at most H + 1 distinctions); other pairs pooled at H + 1."""
    L = H + 1
    n, cap, own = capacities(stars)
    o = n
    masks = [sum(1 << b for b in s) for s in stars]
    best = {}

    def complement_connected(J):
        seen, stack = {o}, [o]
        while stack:
            x = stack.pop()
            for y in cap.get(x, {}):
                if y not in J and y not in seen:
                    seen.add(y)
                    stack.append(y)
        return len(seen) + len(J) == n + 1

    def go(J, X):
        if flow_exceeds(cap, J, X | {o}, L):
            return
        front = {v for u in J for v in cap.get(u, {}) if v != o and v not in J and v not in X}
        if not front:
            c = sum(c for u in J for v, c in cap.get(u, {}).items() if v not in J)
            if c <= L and complement_connected(J):
                w = 0
                for u in J:
                    w ^= masks[u]
                bits = [i for i in range(w.bit_length()) if w >> i & 1]
                for p in combinations(bits, 2):
                    if best.get(p, L + 1) > c - 1:
                        best[p] = c - 1
            return
        w = max(front, key=lambda v: (sum(cap[v].get(u, 0) for u in J), -v))
        go(J | {w}, X)
        go(J, X | {w})

    for r in range(n):
        go(frozenset([r]), frozenset(range(r)))
    labels = sorted(own)
    return {p: min(best.get(p, H + 1), H + 1) for p in combinations(labels, 2)}
