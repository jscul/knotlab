"""Weaves, their shuffled twins, and the not-all-equal laws (SPACE-ORDER-20261117-001).

The weave W(L) is the six-regular one-pair weave on L x L distinctions,
v(i, j) = (i mod L) + L (j mod L), with the knots (v(i,j), v(i+1,j), v(i,j+1))
and (v(i+1,j), v(i,j+1), v(i+1,j+1)) for all i, j: every distinction lies in
six knots.  Its twin R6 is the same pattern after degree-preserving knot swaps
(two knots exchange one member each), which keep every distinction in six
knots and destroy the steps-apart structure.

Atom law: each knot demands one of its members, chosen uniformly and kept
through swaps; the atom library of SEQUENTIAL-WALL-20261116-001A computes
rounds, phases and Strahler numbers.

Not-all-equal law: held distinctions take their values in a planted state; a
knot with two set members of one value sets the third to the other value.
Rounds: synchronous.  Phases: at a phase's start every knot with exactly one
set member x = b gives the two-place rules y = b -> z = not b and
z = b -> y = not b; knots with two equal set members begin; the phase sets
every literal reachable from the beginnings.
"""

import os
import sys
from collections import deque

import numpy as np
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import breadth_first_order

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
SW = os.path.join(ROOT, "experiments", "SEQUENTIAL-WALL-20261116-001A",
                  "SEQUENTIAL-WALL-20261116-001A-E001_rounds_phases")
sys.path.insert(0, SW)
import atoms as A  # noqa: E402

INF = A.INF


def weave(L):
    i, j = np.meshgrid(np.arange(L), np.arange(L), indexing="ij")
    i, j = i.ravel(), j.ravel()
    v = lambda a, b: (a % L) + L * (b % L)
    up = np.stack([v(i, j), v(i + 1, j), v(i, j + 1)], 1)
    down = np.stack([v(i + 1, j), v(i, j + 1), v(i + 1, j + 1)], 1)
    return np.concatenate([up, down]).astype(np.int64)


def three_class_state(L):
    assert L % 3 == 0
    i, j = np.meshgrid(np.arange(L), np.arange(L), indexing="ij")
    c = (i + 2 * j).ravel() % 3
    return (c == 2).astype(np.int8)


def knots_of(knots, n):
    lists = [[] for _ in range(n)]
    for k, t in enumerate(knots.tolist()):
        for u in t:
            lists[u].append(k)
    return lists


def zero_energy_sweeps(knots, state, sweeps, rng):
    """Flip one distinction at a time, at random, whenever no knot holding it
    has both other members equal to its new value; 'sweeps' times n tries."""
    n = len(state)
    s = state.copy().tolist()
    kl = knots_of(knots, n)
    K = knots.tolist()
    for v in rng.integers(0, n, sweeps * n).tolist():
        nb = 1 - s[v]
        ok = True
        for k in kl[v]:
            a, b = [u for u in K[k] if u != v]
            if s[a] == nb and s[b] == nb:
                ok = False
                break
        if ok:
            s[v] = nb
    return np.array(s, dtype=np.int8)


def nae_ok(knots, state):
    x = state[knots]
    return np.all(x.min(1) != x.max(1))


def knot_swaps(knots, demand, n_swaps, rng, state=None):
    """Degree-preserving swaps: knots p, q exchange members at positions a, b.
    Rejected when a knot would hold a distinction twice, or (with a planted
    state) become monochromatic.  The demanded position stays with the knot."""
    K = knots.copy()
    m = len(K)
    acc = 0
    tries = 0
    while acc < n_swaps:
        tries += 1
        p, q = rng.integers(0, m, 2)
        if p == q:
            continue
        a, b = rng.integers(0, 3, 2)
        x, y = K[p, a], K[q, b]
        if x == y or y in K[p] or x in K[q]:
            continue
        kp = K[p].copy(); kp[a] = y
        kq = K[q].copy(); kq[b] = x
        if state is not None:
            if state[kp].min() == state[kp].max() or state[kq].min() == state[kq].max():
                continue
        K[p], K[q] = kp, kq
        acc += 1
    return K, tries


def atom_pattern(knots, demand, held):
    idx = np.arange(len(knots))
    c = knots[idx, demand]
    others = np.stack([knots[idx, (demand + 1) % 3], knots[idx, (demand + 2) % 3]], 1)
    return A.Pattern(int(knots.max()) + 1, np.stack([others[:, 0], others[:, 1], c], 1), held)


# ------------------------------------------------------------ not-all-equal

def nae_rounds(knots, n, held, values):
    val = np.full(n, -1, dtype=np.int8)
    val[held] = values[held]
    r = 0
    while True:
        x = val[knots]
        unset = x < 0
        nset = 3 - unset.sum(1)
        cand = nset == 2
        if not cand.any():
            return val, r
        xs = x[cand]
        un = unset[cand]
        a = np.where(un[:, 0], xs[:, 1], xs[:, 0])
        b = np.where(un[:, 2], xs[:, 1], xs[:, 2])
        eq = a == b
        if not eq.any():
            return val, r
        tgt = knots[cand][eq][un[eq]]
        newv = (1 - a[eq]).astype(np.int8)
        assert np.all((val[tgt] < 0))
        r += 1
        # consistency: one value per target
        order = np.argsort(tgt)
        t2, v2 = tgt[order], newv[order]
        assert np.all((t2[1:] != t2[:-1]) | (v2[1:] == v2[:-1])), "conflicting forcings"
        val[t2] = v2


def _reach_literals(n, src_lits, tails, heads):
    """Literal node 2v + b.  BFS from src_lits along tails -> heads."""
    N = 2 * n
    s = N
    rows = np.concatenate([tails, np.full(len(src_lits), s)])
    cols = np.concatenate([heads, src_lits])
    g = csr_matrix((np.ones(len(rows), dtype=np.int8), (rows, cols)), shape=(N + 1, N + 1))
    order = breadth_first_order(g, s, directed=True, return_predecessors=False)
    return order[order != s]


def nae_phases(knots, n, held, values):
    val = np.full(n, -1, dtype=np.int8)
    val[held] = values[held]
    phase = np.where(val >= 0, 0, -1).astype(np.int64)
    t = 0
    while True:
        x = val[knots]
        unset = x < 0
        nset = 3 - unset.sum(1)
        # beginnings: two set equal, third unset
        two = nset == 2
        xs, un = x[two], unset[two]
        a = np.where(un[:, 0], xs[:, 1], xs[:, 0])
        b = np.where(un[:, 2], xs[:, 1], xs[:, 2])
        eq = a == b
        starts = 2 * knots[two][eq][un[eq]] + (1 - a[eq])
        # rules from knots with exactly one set member x = b
        one = nset == 1
        K1, X1, U1 = knots[one], x[one], unset[one]
        bvals = X1.max(1)  # the one set value
        pos_set = np.argmax(~U1, axis=1)
        others = np.stack([K1[np.arange(len(K1)), (pos_set + 1) % 3], K1[np.arange(len(K1)), (pos_set + 2) % 3]], 1)
        y, z = others[:, 0], others[:, 1]
        tails = np.concatenate([2 * y + bvals, 2 * z + bvals])
        heads = np.concatenate([2 * z + (1 - bvals), 2 * y + (1 - bvals)])
        if len(starts) == 0:
            return val, phase, t
        lits = _reach_literals(n, starts.astype(np.int64), tails.astype(np.int64), heads.astype(np.int64))
        vs, bs = lits // 2, (lits % 2).astype(np.int8)
        keep = val[vs] < 0
        vs, bs = vs[keep], bs[keep]
        if len(vs) == 0:
            return val, phase, t
        order = np.argsort(vs)
        vs, bs = vs[order], bs[order]
        assert np.all((vs[1:] != vs[:-1]) | (bs[1:] == bs[:-1])), "both values reached"
        t += 1
        val[vs] = bs
        phase[vs] = t


def nae_rank(knots, n, held, values):
    """Least Strahler number of a derivation of each set value (relaxation from
    infinity): a held value has 0; via a knot whose two other members hold the
    same value b with numbers i, j, the third gets combine(i, j)."""
    final, _ = nae_rounds(knots, n, held, values)
    r = np.where(np.isin(np.arange(n), held), 0, INF).astype(np.int64)
    K = knots
    while True:
        best = r.copy()
        for p in range(3):
            q1, q2 = (p + 1) % 3, (p + 2) % 3
            u, v, w = K[:, q1], K[:, q2], K[:, p]
            ok = (final[u] >= 0) & (final[u] == final[v]) & (final[w] >= 0) & (final[w] != final[u])
            cand = A.combine(r[u], r[v])
            cand = np.where(ok, cand, INF)
            np.minimum.at(best, w, cand)
        upd = best < r
        if not upd.any():
            return r
        r = best


def nae_incremental_k_star(knots, n, order, values, frac=0.5):
    """Least k with at least frac*n distinctions set when the first k of order
    are held, by one incremental propagation."""
    kl = knots_of(knots, n)
    K = knots.tolist()
    val = [-1] * n
    size = 0
    target = frac * n
    for k, v0 in enumerate(order.tolist(), start=1):
        if val[v0] >= 0:
            continue
        q = deque([(v0, int(values[v0]))])
        while q:
            v, b = q.popleft()
            if val[v] >= 0:
                continue
            val[v] = b
            size += 1
            for kk in kl[v]:
                a, c = [u for u in K[kk] if u != v]
                va, vc = val[a], val[c]
                if va == b and vc < 0:
                    q.append((c, 1 - b))
                elif vc == b and va < 0:
                    q.append((a, 1 - b))
        if size >= target:
            return k, size
    return n, size


# ------------------------------------------------- roles, twins and distance

def two_demand_atoms(knots, free):
    """Each knot demands two members: with f its free member and x, y the
    others, the atoms (f, y -> x) and (f, x -> y)."""
    idx = np.arange(len(knots))
    f = knots[idx, free]
    x = knots[idx, (free + 1) % 3]
    y = knots[idx, (free + 2) % 3]
    return np.concatenate([np.stack([f, y, x], 1), np.stack([f, x, y], 1)])


def one_demand_atoms(knots, demand):
    idx = np.arange(len(knots))
    c = knots[idx, demand]
    a = knots[idx, (demand + 1) % 3]
    b = knots[idx, (demand + 2) % 3]
    return np.stack([a, b, c], 1)


def role_swaps(knots, role, n_swaps, rng):
    """Degree- and role-preserving swaps: two knots exchange members whose
    slots carry the same role label (role is an m x 3 integer array that
    stays with the slots).  Rejected when a knot would hold a distinction
    twice.  Every distinction keeps how many knots it has in each role."""
    K = knots.copy()
    m = len(K)
    by_role = {}
    for r in np.unique(role):
        ks, ps = np.nonzero(role == r)
        by_role[int(r)] = (ks, ps)
    roles = list(by_role)
    weights = np.array([len(by_role[r][0]) for r in roles], dtype=float)
    weights /= weights.sum()
    acc = tries = 0
    while acc < n_swaps:
        tries += 1
        r = roles[int(rng.choice(len(roles), p=weights))]
        ks, ps = by_role[r]
        i, j = rng.integers(0, len(ks), 2)
        p, a, q, b = ks[i], ps[i], ks[j], ps[j]
        if p == q:
            continue
        x, y = K[p, a], K[q, b]
        if x == y or y in K[p] or x in K[q]:
            continue
        K[p, a], K[q, b] = y, x
        acc += 1
    return K, tries


def nae_roles(knots, state):
    """Role of each slot under a not-all-equal state: 2 * value + (1 if the
    member is the knot's odd one else 0)."""
    x = state[knots].astype(np.int64)
    s = x.sum(1, keepdims=True)
    odd = np.where(s == 1, x == 1, x == 0)
    return 2 * x + odd.astype(np.int64)


def steps_from(knots, n, sources):
    """Steps apart from the nearest source (breadth-first over co-knotted pairs)."""
    a, b, c = knots[:, 0], knots[:, 1], knots[:, 2]
    rows = np.concatenate([a, b, b, c, a, c])
    cols = np.concatenate([b, a, c, b, c, a])
    g = csr_matrix((np.ones(len(rows), dtype=np.int8), (rows, cols)), shape=(n, n)).tocsr()
    dist = np.full(n, -1, dtype=np.int64)
    frontier = np.unique(np.asarray(sources, dtype=np.int64))
    dist[frontier] = 0
    d = 0
    while len(frontier):
        d += 1
        nb = np.unique(g[frontier].indices)
        nb = nb[dist[nb] < 0]
        dist[nb] = d
        frontier = nb
    return dist


def free_spin_fraction(knots, state):
    """Share of distinctions that can flip without making a knot monochromatic."""
    n = len(state)
    bad = np.zeros(n, dtype=bool)
    for p in range(3):
        v = knots[:, p]
        u, w = knots[:, (p + 1) % 3], knots[:, (p + 2) % 3]
        nb = 1 - state[v]
        bad[v[(state[u] == nb) & (state[w] == nb)]] = True
    return float((~bad).mean())
