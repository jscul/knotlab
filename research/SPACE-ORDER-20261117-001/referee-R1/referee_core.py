"""Referee R1 for SPACE-ORDER-20261117-001: the referee's own library (no code from the study or SEQUENTIAL-WALL).

Every law here is an atom law: an atom (a, b -> c) sets c once a and b are set.
- two-demand: knot (f, x, y) with free member f gives (f, y -> x) and (f, x -> y);
- one-demand: knot with demanded member c and others a, b gives (a, b -> c);
- not-all-equal from a planted not-all-equal state: a set pair of equal values forces the third to differ, and from planted held
  values every forced value is the planted one, so the law is the atom law (u, v -> w) with w the knot's odd member.

Rounds and phases are computed as least labels by Knuth's generalized Dijkstra (superior functions):
- round(c) = min over atoms of max(round(a), round(b)) + 1 (synchronous rounds);
- phase(c) = min over atoms of g(phase(a), phase(b)), g(i, j) = max(i, j) if i != j else i + 1. This is the phase of the
  untangling law: c is reached in phase max(i, j) through the two-place rule an earlier-set premise gives, or begins in phase
  i + 1 when both premises were set in phase i. Held distinctions have label 0.
Steps apart is breadth-first distance over co-knotted pairs.
"""
from __future__ import annotations

import heapq
from collections import deque

import numpy as np

INF = 1 << 60


def weave(L):
    """Knots (v(i,j), v(i+1,j), v(i,j+1)) and (v(i+1,j), v(i,j+1), v(i+1,j+1)), v(i,j) = i mod L + L (j mod L)."""
    ks = []
    for j in range(L):
        for i in range(L):
            v = lambda a, b: (a % L) + L * (b % L)
            ks.append((v(i, j), v(i + 1, j), v(i, j + 1)))
    for j in range(L):
        for i in range(L):
            v = lambda a, b: (a % L) + L * (b % L)
            ks.append((v(i + 1, j), v(i, j + 1), v(i + 1, j + 1)))
    return np.array(ks, dtype=np.int64)


def neighbours(knots, n):
    nb = [set() for _ in range(n)]
    for a, b, c in knots.tolist():
        nb[a].update((b, c))
        nb[b].update((a, c))
        nb[c].update((a, b))
    return [list(s) for s in nb]


def steps_from(nb, sources):
    n = len(nb)
    d = [-1] * n
    q = deque()
    for s in set(int(x) for x in sources):
        d[s] = 0
        q.append(s)
    while q:
        v = q.popleft()
        for u in nb[v]:
            if d[u] < 0:
                d[u] = d[v] + 1
                q.append(u)
    return np.array(d, dtype=np.int64)


def two_demand(knots, free):
    out = []
    for (k0, k1, k2), f in zip(knots.tolist(), free.tolist()):
        mem = (k0, k1, k2)
        x, y = [mem[p] for p in range(3) if p != f]
        out.append((mem[f], y, x))
        out.append((mem[f], x, y))
    return np.array(out, dtype=np.int64)


def one_demand(knots, dem):
    out = []
    for (k0, k1, k2), c in zip(knots.tolist(), dem.tolist()):
        mem = (k0, k1, k2)
        a, b = [mem[p] for p in range(3) if p != c]
        out.append((a, b, mem[c]))
    return np.array(out, dtype=np.int64)


def nae_atoms(knots, state):
    out = []
    for t in knots.tolist():
        vals = [int(state[u]) for u in t]
        assert min(vals) != max(vals), "planted state must be not-all-equal"
        odd = [p for p in range(3) if vals.count(vals[p]) == 1][0]
        a, b = [t[p] for p in range(3) if p != odd]
        out.append((a, b, t[odd]))
    return np.array(out, dtype=np.int64)


class Atoms:
    def __init__(self, n, atoms):
        self.n = n
        self.a, self.b, self.c = (atoms[:, i].tolist() for i in range(3))
        prem = [[] for _ in range(n)]
        for j, (x, y) in enumerate(zip(self.a, self.b)):
            prem[x].append(j)
            prem[y].append(j)
        self.prem = prem

    def labels(self, held, kind):
        """Least labels (kind 'round' or 'phase'); INF for unset."""
        n, a, b, c, prem = self.n, self.a, self.b, self.c, self.prem
        lab = [INF] * n
        fin = [False] * n
        h = []
        for v in set(int(x) for x in held):
            lab[v] = 0
            h.append((0, v))
        heapq.heapify(h)
        rnd = kind == "round"
        while h:
            lv, v = heapq.heappop(h)
            if fin[v] or lv != lab[v]:
                continue
            fin[v] = True
            for j in prem[v]:
                u = b[j] if a[j] == v else a[j]
                if not fin[u]:
                    continue
                lu = lab[u]
                if rnd:
                    cand = (lv if lv > lu else lu) + 1
                else:
                    cand = (lv if lv > lu else lu) if lv != lu else lv + 1
                w = c[j]
                if cand < lab[w]:
                    lab[w] = cand
                    heapq.heappush(h, (cand, w))
        return np.array(lab, dtype=np.int64)

    def k_star(self, order, frac=0.5):
        """Least k with at least frac * n set when order[:k] is held (one incremental closure)."""
        need = [2] * len(self.c)
        setv = [False] * self.n
        size = 0
        for k, v0 in enumerate(order.tolist(), start=1):
            st = [v0]
            while st:
                v = st.pop()
                if setv[v]:
                    continue
                setv[v] = True
                size += 1
                for j in self.prem[v]:
                    need[j] -= 1
                    if need[j] == 0 and not setv[self.c[j]]:
                        st.append(self.c[j])
            if size >= frac * self.n:
                return k, size
        return len(order), size


def reading(at: Atoms, nb, held):
    r = at.labels(held, "round")
    p = at.labels(held, "phase")
    s = r < INF
    assert np.array_equal(s, p < INF)
    d = steps_from(nb, held)
    return {"set": int(s.sum()), "R": int(r[s].max()), "P": int(p[s].max()), "D": int(d[s].max()), "phase": p}


def role_swaps(knots, role, n_swaps, rng):
    """The referee's degree- and role-preserving swaps: pick a role with probability proportional to its slots, two slots of
    that role in different knots, exchange their members unless a knot would hold a distinction twice."""
    K = knots.copy()
    slots = {}
    for r in np.unique(role):
        kk, pp = np.nonzero(role == r)
        slots[int(r)] = (kk, pp)
    keys = sorted(slots)
    w = np.array([len(slots[r][0]) for r in keys], float)
    w /= w.sum()
    done = 0
    while done < n_swaps:
        r = keys[int(rng.choice(len(keys), p=w))]
        kk, pp = slots[r]
        i, j = rng.integers(0, len(kk), 2)
        p, q = kk[i], kk[j]
        if p == q:
            continue
        x, y = K[p, pp[i]], K[q, pp[j]]
        if x == y or y in K[p] or x in K[q]:
            continue
        K[p, pp[i]], K[q, pp[j]] = y, x
        done += 1
    return K


def pair_multiplicity(knots):
    """Share of co-knotted pairs that lie in two or more knots."""
    from collections import Counter
    cnt = Counter()
    for a, b, c in knots.tolist():
        for u, v in ((a, b), (a, c), (b, c)):
            cnt[(u, v) if u < v else (v, u)] += 1
    vals = np.array(list(cnt.values()))
    return float(np.mean(vals >= 2)), int(len(vals))
