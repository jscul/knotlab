"""Referee R1 oracle library for SEQUENTIAL-WALL-20261116-001 (written fresh).

Nothing here imports or copies the study's atoms.py / gates.py / job.py.
Definitions are taken from the proof's text
(proofs/SEQUENTIAL-WALL-20261116-001B/.../proof.md) and the sampling protocol
from the contract and job.py (read, not run).

An atom is a triple (a, b, c): a and b together demand c (clause ~a ~b c).
"""

import heapq
from collections import deque

import numpy as np

INF = float("inf")


def combine(i, j):
    """Horton-Strahler combination with leaves 0."""
    if i == INF or j == INF:
        return INF
    return i + 1 if i == j else max(i, j)


# ---------------------------------------------------------------- pure Python
# (small patterns; used for Theorem 1 by brute force)

def closure_worklist(n, atoms, held):
    """Least model: counter-based worklist (not rounds)."""
    need = [2] * len(atoms)
    occ = [[] for _ in range(n)]
    for j, (a, b, c) in enumerate(atoms):
        occ[a].append(j)
        occ[b].append(j)
    forced = [False] * n
    q = deque()
    for v in held:
        if not forced[v]:
            forced[v] = True
            q.append(v)
    while q:
        v = q.popleft()
        for j in occ[v]:
            need[j] -= 1
            if need[j] == 0:
                c = atoms[j][2]
                if not forced[c]:
                    forced[c] = True
                    q.append(c)
    return forced


def rounds_py(n, atoms, held):
    S = set(held)
    R = 0
    while True:
        add = {c for (a, b, c) in atoms if a in S and b in S and c not in S}
        if not add:
            return S, R
        S |= add
        R += 1


def phases_py(n, atoms, held):
    """Forcing law, literally as in the proof: phase t reads each atom with a
    demander in P_{t-1} as the two-place rule from the other demander, and P_t
    is everything reachable from P_{t-1} along those rules."""
    phase = [INF] * n
    P = set(held)
    for v in P:
        phase[v] = 0
    t = 0
    while True:
        adj = {}
        for (a, b, c) in atoms:
            if a in P:
                adj.setdefault(b, []).append(c)
            if b in P:
                adj.setdefault(a, []).append(c)
        seen = set(P)
        q = deque(P)
        while q:
            u = q.popleft()
            for w in adj.get(u, ()):
                if w not in seen:
                    seen.add(w)
                    q.append(w)
        new = seen - P
        if not new:
            return P, phase, t
        t += 1
        for v in new:
            phase[v] = t
        P = seen


def strahler_sets(n, atoms, held, H=None):
    """Exact sigma by explicit enumeration of derivation-tree values by height.

    T_h(v) = the SET of Strahler numbers of derivation trees of v of height
    <= h; T_{h+1}(v) = T_0(v) U {combine(i, j) : (a, b -> v), i in T_h(a),
    j in T_h(b)} (children are chosen independently, so this is exactly the
    set of values of trees of height <= h + 1).  A tree that is least in
    Strahler number and, among those, fewest in nodes repeats no label on a
    root-to-leaf path (replacing the upper occurrence's subtree by the lower
    one never raises the number, since combine is monotone and a subtree's
    number is at most its supertree's, and it removes nodes), so its height is
    at most n - 1.  Hence min T_{n}(v) is sigma(v), INF when T_n(v) is empty."""
    if H is None:
        H = n
    held = set(held)
    T0 = [{0} if v in held else set() for v in range(n)]
    T = [set(s) for s in T0]
    for _ in range(H):
        newT = [set(T[v]) for v in range(n)]
        for (a, b, c) in atoms:
            if T[a] and T[b]:
                tc = newT[c]
                for i in T[a]:
                    for j in T[b]:
                        tc.add(combine(i, j))
        T = newT
    return [min(s) if s else INF for s in T]


def knuth_superior(n, atoms, held, leaf_value, op):
    """Knuth (1977) generalized Dijkstra for a superior function op
    (monotone, op(x, y) >= max(x, y)): the least value over finite derivation
    trees.  Values are finalized in nondecreasing order."""
    occ = [[] for _ in range(n)]
    for j, (a, b, c) in enumerate(atoms):
        occ[a].append(j)
        occ[b].append(j)
    final = [None] * n
    best = [INF] * n
    heap = []
    for v in set(held):
        best[v] = leaf_value
        heap.append((leaf_value, v))
    heapq.heapify(heap)
    while heap:
        d, v = heapq.heappop(heap)
        if final[v] is not None:
            continue
        final[v] = d
        for j in occ[v]:
            a, b, c = atoms[j]
            if final[c] is not None:
                continue
            fa, fb = final[a], final[b]
            if fa is None or fb is None:
                continue
            x = op(fa, fb)
            if x < best[c]:
                best[c] = x
                heapq.heappush(heap, (x, c))
    return [INF if f is None else f for f in final]


def strahler_knuth(n, atoms, held):
    return knuth_superior(n, atoms, held, 0, combine)


def fringe_knuth(n, atoms, held):
    """Fewest held leaves (with multiplicity) of a derivation tree, exact ints."""
    return knuth_superior(n, atoms, held, 1, lambda x, y: x + y)


def strahler_relax_from_inf(n, atoms, held):
    """Relaxation downward from INF (a third method)."""
    s = [INF] * n
    for v in held:
        s[v] = 0
    while True:
        ch = False
        for (a, b, c) in atoms:
            x = combine(s[a], s[b])
            if x < s[c]:
                s[c] = x
                ch = True
        if not ch:
            return s


# ---------------------------------------------------------------- vectorized
# (random patterns at n up to 2^16, circuits)

def random_atoms(n, m, rng):
    """m atoms, each an ordered triple of three distinct uniform distinctions
    (rejection sampling: uniform over ordered distinct triples)."""
    t = rng.integers(0, n, size=(m, 3), dtype=np.int64)
    while True:
        bad = (t[:, 0] == t[:, 1]) | (t[:, 0] == t[:, 2]) | (t[:, 1] == t[:, 2])
        nb = int(bad.sum())
        if nb == 0:
            return t
        t[bad] = rng.integers(0, n, size=(nb, 3), dtype=np.int64)


def rounds_np(n, A, held_mask):
    a, b, c = A[:, 0], A[:, 1], A[:, 2]
    S = held_mask.copy()
    R = 0
    while True:
        fire = S[a] & S[b] & ~S[c]
        if not fire.any():
            return S, R
        S[c[fire]] = True
        R += 1


def _csr(n, tails, heads):
    order = np.argsort(tails, kind="stable")
    t, h = tails[order], heads[order]
    indptr = np.zeros(n + 1, dtype=np.int64)
    np.add.at(indptr, t + 1, 1)
    np.cumsum(indptr, out=indptr)
    return indptr, h


def _reach_np(n, sources_mask, tails, heads):
    """Frontier BFS from sources along tail -> head; returns reached mask."""
    indptr, nbr = _csr(n, tails, heads)
    seen = sources_mask.copy()
    frontier = np.flatnonzero(seen)
    while frontier.size:
        st, en = indptr[frontier], indptr[frontier + 1]
        ln = en - st
        tot = int(ln.sum())
        if tot == 0:
            break
        # gather all neighbour indices of the frontier
        rep = np.repeat(st - np.concatenate([[0], np.cumsum(ln)[:-1]]), ln)
        idx = np.arange(tot) + rep
        cand = nbr[idx]
        cand = cand[~seen[cand]]
        if cand.size == 0:
            break
        cand = np.unique(cand)
        seen[cand] = True
        frontier = cand
    return seen


def phases_np(n, A, held_mask):
    a, b, c = A[:, 0], A[:, 1], A[:, 2]
    P = held_mask.copy()
    phase = np.where(P, 0, -1).astype(np.int64)
    t = 0
    sizes = []
    while True:
        ma, mb = P[a], P[b]
        tails = np.concatenate([b[ma], a[mb]])
        heads = np.concatenate([c[ma], c[mb]])
        keep = ~P[heads]
        reach = _reach_np(n, P, tails[keep], heads[keep])
        new = reach & ~P
        k = int(new.sum())
        if k == 0:
            return P, phase, t, sizes
        t += 1
        P |= new
        phase[new] = t
        sizes.append(k)


def strahler_knuth_np(n, A, held_mask):
    atoms = [tuple(x) for x in A.tolist()]
    return knuth_superior(n, atoms, np.flatnonzero(held_mask).tolist(), 0, combine)


def fringe_knuth_np(n, A, held_mask):
    atoms = [tuple(x) for x in A.tolist()]
    return knuth_superior(n, atoms, np.flatnonzero(held_mask).tolist(), 1, lambda x, y: x + y)


# ---------------------------------------------------------------- circuits

def layered_circuit(width, depth, rng):
    """Inputs true w.p. 1/2; each gate AND/OR w.p. 1/2 reading two distinct
    gates of the layer below."""
    inputs = rng.random(width) < 0.5
    layers = []
    for _ in range(depth):
        x = rng.integers(0, width, width)
        y = rng.integers(0, width, width)
        while True:
            bad = x == y
            if not bad.any():
                break
            y[bad] = rng.integers(0, width, int(bad.sum()))
        is_and = rng.random(width) < 0.5
        layers.append((is_and, x, y))
    return inputs, layers


def layered_eval(inputs, layers):
    vals = [inputs.copy()]
    for is_and, x, y in layers:
        u, v = vals[-1][x], vals[-1][y]
        vals.append(np.where(is_and, u & v, u | v))
    return vals


def layered_to_atoms(inputs, layers):
    """Distinction 0 is the held t; layer L gate i is 1 + L*width + i."""
    w = len(inputs)
    T = 0
    rows = []
    for L, (is_and, x, y) in enumerate(layers):
        base_prev = 1 + L * w
        base = 1 + (L + 1) * w
        g = base + np.arange(w)
        xp, yp = base_prev + x, base_prev + y
        ia = is_and
        io = ~is_and
        rows.append(np.stack([xp[ia], yp[ia], g[ia]], 1))
        rows.append(np.stack([xp[io], np.full(int(io.sum()), T), g[io]], 1))
        rows.append(np.stack([yp[io], np.full(int(io.sum()), T), g[io]], 1))
    n = 1 + (len(layers) + 1) * w
    A = np.concatenate(rows).astype(np.int64)
    held = np.zeros(n, dtype=bool)
    held[T] = True
    held[1 + np.flatnonzero(inputs)] = True
    return n, A, held


def unlayered_circuit(n_in, n_gates, rng):
    inputs = rng.random(n_in) < 0.5
    gates = []
    for g in range(n_gates):
        k = n_in + g
        x = int(rng.integers(0, k))
        y = int(rng.integers(0, k))
        while y == x:
            y = int(rng.integers(0, k))
        gates.append((bool(rng.random() < 0.5), x, y))
    return inputs, gates


def unlayered_eval(inputs, gates):
    vals = [bool(v) for v in inputs]
    for is_and, x, y in gates:
        vals.append((vals[x] and vals[y]) if is_and else (vals[x] or vals[y]))
    return np.array(vals, dtype=bool)


def unlayered_to_atoms(inputs, gates):
    """Node i (input or gate) is distinction i + 1; distinction 0 is t."""
    T = 0
    n = 1 + len(inputs) + len(gates)
    atoms = []
    for gi, (is_and, x, y) in enumerate(gates):
        g = 1 + len(inputs) + gi
        if is_and:
            atoms.append((x + 1, y + 1, g))
        else:
            atoms.append((x + 1, T, g))
            atoms.append((y + 1, T, g))
    held = np.zeros(n, dtype=bool)
    held[T] = True
    held[1 + np.flatnonzero(inputs)] = True
    return n, np.array(atoms, dtype=np.int64).reshape(-1, 3), held


# ---------------------------------------------------------------- dual law

def dual_law_py(n, atoms, held):
    """Theorem 6's dual law, from the proof's text.  An atom is dead once a
    demander is known unforced.  Phase 0 seeds = unheld distinctions no atom
    demands; later phases seed every unheld, not-yet-unforced distinction all
    of whose atoms are dead.  In each phase, for every open distinction with
    exactly one live atom (a, b -> v) at the phase's start, follow the rules
    a -> v and b -> v ('a demander unforced -> it unforced').  Returns
    (unforced list, dual phase list (INF if never), P_dual = number of
    reachability computations that added something)."""
    held = set(held)
    by_c = [[] for _ in range(n)]
    for j, (a, b, c) in enumerate(atoms):
        by_c[c].append(j)
    unf = [False] * n
    dphase = [INF] * n
    t = 0
    while True:
        dead = [unf[a] or unf[b] for (a, b, c) in atoms]
        seeds = []
        adj = {}
        for v in range(n):
            if v in held or unf[v]:
                continue
            live = [j for j in by_c[v] if not dead[j]]
            if t == 0:
                if not by_c[v]:
                    seeds.append(v)
            elif not live:
                seeds.append(v)
            if len(live) == 1:
                a, b, _ = atoms[live[0]]
                adj.setdefault(a, []).append(v)
                adj.setdefault(b, []).append(v)
        start = [v for v in range(n) if unf[v]] + seeds
        seen = set(start)
        q = deque(start)
        while q:
            u = q.popleft()
            for w in adj.get(u, ()):
                if w not in seen and w not in held:
                    seen.add(w)
                    q.append(w)
        new = [v for v in seen if not unf[v]]
        if not new:
            return unf, dphase, t
        for v in new:
            unf[v] = True
            dphase[v] = t
        t += 1


def dual_strahler_topo(n, atoms, held, topo):
    """Least generalized Strahler number of a derivation of unforcedness, by
    DP along a topological order (pattern acyclic).  Each atom contributes the
    lesser number of its two demanders; the node takes the largest, plus one
    when the largest occurs at two or more atoms; undemanded unheld = 0;
    held = INF.  The node function is monotone, so the DP gives the least."""
    held = set(held)
    by_c = [[] for _ in range(n)]
    for (a, b, c) in atoms:
        by_c[c].append((a, b))
    d = [INF] * n
    for v in topo:
        if v in held:
            continue
        if not by_c[v]:
            d[v] = 0
            continue
        vals = [min(d[a], d[b]) for (a, b) in by_c[v]]
        mx = max(vals)
        if mx == INF:
            continue
        d[v] = mx + 1 if vals.count(mx) >= 2 else mx
    return d
