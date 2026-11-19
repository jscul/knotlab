"""The referee's exact least bond through a set of marked distinctions, by mixed-integer programming (scipy's HiGHS), for
graphs too large for shore enumeration.  Own code, written for LATER-BOND-READING-R1.

A graph is a list of bundles (u, v, w): w parallel distinctions joining u and v (a cut crosses all or none).  A bond is a cut with
both shores connected.  K(marks) is the least total weight of a bond crossing every marked bundle, or None when none exists.

Formulation: y_v in {0, 1} is the shore of v; c_e >= |y_u - y_v| for each bundle; each marked bundle has y_u + y_v = 1, and the
first marked bundle's u is put on shore 1 (complementing both shores leaves the cut unchanged).  Each shore is connected by a
single-commodity flow from its root (the first marked bundle's two ends): every other vertex on the shore consumes one unit,
carried only along adjacencies inside the shore."""
import itertools
from collections import defaultdict

import numpy as np


def least_bond(n, bundles, marks, time_limit=600):
    from scipy.optimize import milp, LinearConstraint, Bounds
    from scipy.sparse import lil_matrix
    marks = sorted(set(marks))
    if not marks:
        raise ValueError("no marks")
    adj = sorted({(min(u, v), max(u, v)) for u, v, w in bundles if u != v})
    arcs = [(a, b) for a, b in adj] + [(b, a) for a, b in adj]
    nb, na = len(bundles), len(arcs)
    # variables: y (n), c (nb), f1 (na), f0 (na)
    Y, C, F1, F0 = 0, n, n + nb, n + nb + na
    nv = n + nb + 2 * na
    cost = np.zeros(nv)
    for i, (u, v, w) in enumerate(bundles):
        cost[C + i] = w
    rows, lo, hi = [], [], []

    def add(coefs, l, h):
        rows.append(coefs)
        lo.append(l)
        hi.append(h)
    for i, (u, v, w) in enumerate(bundles):
        if u == v:
            continue
        add({C + i: 1, Y + u: -1, Y + v: 1}, 0, np.inf)
        add({C + i: 1, Y + u: 1, Y + v: -1}, 0, np.inf)
    for i in marks:
        u, v, w = bundles[i]
        add({Y + u: 1, Y + v: 1}, 1, 1)
    r1, r0 = bundles[marks[0]][0], bundles[marks[0]][1]
    add({Y + r1: 1}, 1, 1)
    big = n
    inn, out = defaultdict(list), defaultdict(list)
    for k, (a, b) in enumerate(arcs):
        out[a].append(k)
        inn[b].append(k)
        add({F1 + k: 1, Y + a: -big}, -np.inf, 0)
        add({F1 + k: 1, Y + b: -big}, -np.inf, 0)
        add({F0 + k: 1, Y + a: big}, -np.inf, big)
        add({F0 + k: 1, Y + b: big}, -np.inf, big)
    for x in range(n):
        if x != r1:
            co = {F1 + k: 1 for k in inn[x]}
            for k in out[x]:
                co[F1 + k] = co.get(F1 + k, 0) - 1
            co[Y + x] = co.get(Y + x, 0) - 1
            add(co, 0, 0)          # inflow - outflow = y_x
        if x != r0:
            co = {F0 + k: 1 for k in inn[x]}
            for k in out[x]:
                co[F0 + k] = co.get(F0 + k, 0) - 1
            co[Y + x] = co.get(Y + x, 0) + 1
            add(co, 1, 1)          # inflow - outflow = 1 - y_x
    A = lil_matrix((len(rows), nv))
    for r, co in enumerate(rows):
        for j, v in co.items():
            A[r, j] = v
    integrality = np.zeros(nv)
    integrality[Y:Y + n] = 1
    bounds = Bounds(np.zeros(nv), np.concatenate([np.ones(n), np.ones(nb), np.full(2 * na, big), ]))
    res = milp(cost, constraints=LinearConstraint(A.tocsr(), lo, hi), integrality=integrality, bounds=bounds,
               options={"time_limit": time_limit, "mip_rel_gap": 0})
    if res.status == 2:
        return None, None
    if res.status != 0:
        raise RuntimeError(f"milp status {res.status}: {res.message}")
    y = [int(round(res.x[Y + v])) for v in range(n)]
    val = sum(w for u, v, w in bundles if y[u] != y[v])
    return val, y


def check_bond(n, bundles, y, marks):
    """Is the partition y a bond (both shores connected) crossing every mark?  Returns its weight or None."""
    nb = defaultdict(set)
    for u, v, w in bundles:
        nb[u].add(v)
        nb[v].add(u)
    for side in (0, 1):
        S = [v for v in range(n) if y[v] == side]
        if not S:
            return None
        seen, st = {S[0]}, [S[0]]
        while st:
            a = st.pop()
            for b in nb[a]:
                if y[b] == side and b not in seen:
                    seen.add(b)
                    st.append(b)
        if len(seen) != len(S):
            return None
    if any(y[bundles[i][0]] == y[bundles[i][1]] for i in marks):
        return None
    return sum(w for u, v, w in bundles if y[u] != y[v])


def brute(n, bundles, marks):
    best = None
    for bits in range(1, 2 ** (n - 1)):
        y = [(bits >> v) & 1 for v in range(n)]
        val = check_bond(n, bundles, y, marks)
        if val is not None and (best is None or val < best):
            best = val
    return best


def selftest(trials=300, seed=3):
    import random
    rng = random.Random(seed)
    bad = 0
    done = 0
    for _ in range(trials):
        n = rng.randint(4, 10)
        order = list(range(n))
        rng.shuffle(order)
        bundles = [(order[i], rng.choice(order[:i]), rng.randint(1, 4)) for i in range(1, n)]
        for _ in range(rng.randint(0, 2 * n)):
            a, b = rng.sample(range(n), 2)
            bundles.append((a, b, rng.randint(1, 4)))
        k = rng.randint(1, min(4, len(bundles)))
        marks = rng.sample(range(len(bundles)), k)
        b = brute(n, bundles, marks)
        m, y = least_bond(n, bundles, marks)
        done += 1
        if b != m or (y is not None and check_bond(n, bundles, y, marks) != m):
            bad += 1
    return {"trials": done, "disagreements with enumeration": bad}


if __name__ == "__main__":
    print(selftest())
