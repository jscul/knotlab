"""Referee R1 oracle library for CARRY-STRANDS-20261116-001 (written fresh).

Nothing here imports or copies the study's strands.py / gates.py / job.py or
SEQUENTIAL-WALL's atoms.py.  Definitions come from the proof's text
(proofs/CARRY-STRANDS-20261116-001B/.../proof.md) and the decision note.
Strahler numbers come from the referee's own earlier library
(research/SEQUENTIAL-WALL-20261116-001/referee-R1/referee_core.py).

A pattern is (n, atoms, held): atoms a list of triples (a, b, c), "a and b
together demand c"; held a set of distinctions.

Carry laws, within one phase with forced set F (only unforced distinctions
are ever carried):
  begin    atom (a, b -> c), a, b in F: carry c (needs a free slot);
  follow   atom (x, b -> c), b in F, x carried: carry c;
  open use atom (x, y -> c), x, y carried: carry c;
  release  drop one carried distinction.
Spend-only: states are multisets; follow replaces x by c, open use replaces
x and y by c.  Keep: states are sets; follow may keep x; open use may keep
x, y, both or neither; the size never exceeds w.
"""

import math
import os
import sys
from collections import defaultdict, deque

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "research", "SEQUENTIAL-WALL-20261116-001", "referee-R1"))
import referee_core as RC  # noqa: E402  (referee code, not study code)

INF = RC.INF


class Capped(Exception):
    pass


# ------------------------------------------------------------------ basics

def closure(n, atoms, held):
    f = RC.closure_worklist(n, atoms, held)
    return {v for v in range(n) if f[v]}


def native_R(n, atoms, held):
    _, R = RC.rounds_py(n, atoms, held)
    return R


def sigma(n, atoms, held, brute=False):
    """Least Strahler number (leaves 0) of a derivation tree with leaves in
    `held`.  Knuth's generalized Dijkstra; with brute=True also the
    exhaustive set enumeration of referee_core, and the two must agree."""
    s = RC.strahler_knuth(n, atoms, held)
    if brute:
        s2 = RC.strahler_sets(n, atoms, held)
        assert s == s2, ("sigma methods disagree", s, s2)
    return s


def rounds_of(L):
    """ceil(log2(1 + L)) for an integer L >= 0."""
    return int(L).bit_length()


# ------------------------------------------------------------------ one phase

def split_rules(atoms, F):
    """Classify the atoms for a phase with forced set F (c not in F only)."""
    begin = set()
    rule = defaultdict(set)      # x -> {c}: one demander forced
    joint = defaultdict(set)     # x -> {(y, c)}: neither demander forced
    for a, b, c in atoms:
        if c in F:
            continue
        fa, fb = (a in F), (b in F)
        if fa and fb:
            begin.add(c)
        elif fa:
            rule[b].add(c)
        elif fb:
            rule[a].add(c)
        elif a != b:
            joint[a].add((b, c))
            joint[b].add((a, c))
    return sorted(begin), {k: sorted(v) for k, v in rule.items()}, {k: sorted(v) for k, v in joint.items()}


def _succ_spend(M, w, begin, rule, joint, copy=False):
    """Successors of a multiset state M (sorted tuple) under the spend-only
    law; with copy=True also the copy step M -> M + x (x carried)."""
    out = []
    L = len(M)
    distinct = sorted(set(M))
    if L < w:
        for c in begin:
            out.append(tuple(sorted(M + (c,))))
        if copy:
            for x in distinct:
                out.append(tuple(sorted(M + (x,))))
    for x in distinct:
        i = M.index(x)
        rest = M[:i] + M[i + 1:]
        out.append(rest)                                   # release
        for c in rule.get(x, ()):
            out.append(tuple(sorted(rest + (c,))))         # follow, spend x
        for y, c in joint.get(x, ()):
            if y > x and y in rest:                       # each unordered pair once
                j = rest.index(y)
                r2 = rest[:j] + rest[j + 1:]
                out.append(tuple(sorted(r2 + (c,))))       # open use, spend both
    return out


def _succ_keep(S, w, begin, rule, joint):
    """Successors of a set state S (frozenset) under the keep law."""
    out = []
    for c in begin:
        if c not in S and len(S) < w:
            out.append(S | {c})
    for x in S:
        less = S - {x}
        out.append(less)                                   # release
        for c in rule.get(x, ()):
            out.append(less | {c})                         # follow, spend
            if len(S | {c}) <= w:
                out.append(S | {c})                        # follow, keep x
        for y, c in joint.get(x, ()):
            if y not in S:
                continue
            for T in (S - {x, y}, S - {x}, S - {y}, S):
                U = T | {c}
                if len(U) <= w:
                    out.append(U)
    return out


def bfs_phase(atoms, F, w, law, cap=3_000_000):
    """BFS from the empty state.  law in {'spend', 'keep', 'copy'}.
    Returns ({distinction: first distance}, number of states)."""
    begin, rule, joint = split_rules(atoms, F)
    if law == "keep":
        start = frozenset()
        succ = lambda s: _succ_keep(s, w, begin, rule, joint)  # noqa: E731
    else:
        start = ()
        cp = law == "copy"
        succ = lambda s: _succ_spend(s, w, begin, rule, joint, copy=cp)  # noqa: E731
    dist = {start: 0}
    first = {}
    frontier = [start]
    d = 0
    while frontier:
        nxt = []
        for s in frontier:
            for v in s:
                if v not in first:
                    first[v] = d
            for t in succ(s):
                if t not in dist:
                    dist[t] = d + 1
                    nxt.append(t)
            if len(dist) > cap:
                raise Capped(len(dist))
        frontier = nxt
        d += 1
    return first, len(dist)


def run_law(n, atoms, held, w, law, cap=3_000_000, with_sigma_F=False):
    """All phases.  Returns dict: phase (list, -1 = never), P, L (per phase),
    T, states, and optionally per-phase sigma_F checks."""
    F = set(held)
    phase = [-1] * n
    for v in F:
        phase[v] = 0
    Ls, states, t = [], 0, 0
    firsts = []
    while True:
        first, ns = bfs_phase(atoms, F, w, law, cap=cap)
        states += ns
        new = [v for v in first if v not in F]
        if not new:
            break
        t += 1
        Ls.append(max(first[v] for v in new))
        if with_sigma_F:
            sF = sigma(n, atoms, F)
            firsts.append({v: (first[v], sF[v]) for v in new})
        for v in new:
            phase[v] = t
        F |= set(new)
    out = {"phase": phase, "P": t, "L": Ls, "T": sum(rounds_of(L) for L in Ls), "states": states,
           "forced": F}
    if with_sigma_F:
        out["firsts"] = firsts
    return out


# ------------------------------------------------------------------ pebble game

def pebble_reach(n, atoms, F, w):
    """Black pebble game with sliding, F free, at most w pebbles, as a
    search over pebble configurations (bitmasks over all n distinctions).
    Moves, scanning the atoms directly:
      place  on c (not in F, not pebbled) when some atom (a, b -> c) has a
             and b each in F or pebbled, and fewer than w pebbles are down;
      slide  a pebble from a pebbled demander u of an atom (u, x -> c) to c
             (c not in F, not pebbled) when x is in F or pebbled, x != u;
      remove any pebble.
    Returns the set of distinctions pebbled in some reachable configuration."""
    Fm = 0
    for v in F:
        Fm |= 1 << v
    ats = [(a, b, c) for (a, b, c) in atoms if not (Fm >> c) & 1]
    seen = {0}
    stack = [0]
    union = 0
    while stack:
        C = stack.pop()
        union |= C
        cnt = bin(C).count("1")
        free = Fm | C
        nxt = []
        b_ = C
        while b_:
            low = b_ & -b_
            nxt.append(C ^ low)                            # remove
            b_ ^= low
        for a, b, c in ats:
            if (C >> c) & 1:
                continue
            ha, hb = (free >> a) & 1, (free >> b) & 1
            if not (ha and hb):
                continue
            if cnt < w:
                nxt.append(C | (1 << c))                   # place
            for u, x in ((a, b), (b, a)):
                if (C >> u) & 1 and u != x:
                    nxt.append((C & ~(1 << u)) | (1 << c))  # slide u -> c
        for D in nxt:
            if D not in seen:
                seen.add(D)
                stack.append(D)
    return {v for v in range(n) if (union >> v) & 1}


def pebble_phases(n, atoms, held, w):
    F = set(held)
    phase = [-1] * n
    for v in F:
        phase[v] = 0
    t = 0
    while True:
        new = pebble_reach(n, atoms, F, w) - F
        if not new:
            return phase, t, F
        t += 1
        for v in new:
            phase[v] = t
        F |= new


def one_phase_reach(atoms, F, w, law):
    first, _ = bfs_phase(atoms, F, w, law)
    return set(first) - set(F)


# ------------------------------------------------------------------ generators

def ladder(k):
    """x0 held, two held helpers h1, h2; for i < k: (x_i, h1 -> y_i),
    (x_i, h2 -> z_i), (y_i, z_i -> x_{i+1}).  Top x_k."""
    h1, h2, x0 = 0, 1, 2
    atoms, n, x = [], 3, x0
    for _ in range(k):
        y, z, xn = n, n + 1, n + 2
        n += 3
        atoms += [(x, h1, y), (x, h2, z), (y, z, xn)]
        x = xn
    return n, atoms, {h1, h2, x0}, x


def pyramid(h):
    """Rows 0..h, row i has h + 1 - i nodes; v(i, j) demanded by v(i-1, j)
    and v(i-1, j+1); row 0 held.  Top v(h, 0)."""
    ids = {}
    for i in range(h + 1):
        for j in range(h + 1 - i):
            ids[(i, j)] = len(ids)
    atoms = [(ids[(i - 1, j)], ids[(i - 1, j + 1)], ids[(i, j)])
             for i in range(1, h + 1) for j in range(h + 1 - i)]
    return len(ids), atoms, {ids[(0, j)] for j in range(h + 1)}, ids[(h, 0)]


def subdivided_tree(d, ell):
    """Complete binary tree of height d over 2^d held leaves; every tree edge
    (child -> parent) is a chain of ell rules with one held helper g, and the
    parent is the atom over the two chain ends."""
    g = 0
    n = 1
    leaves = list(range(n, n + 2 ** d))
    n += 2 ** d
    atoms = []

    def chain(u):
        nonlocal n
        for _ in range(ell):
            atoms.append((u, g, n))
            u = n
            n += 1
        return u
    level = leaves
    while len(level) > 1:
        up = []
        for i in range(0, len(level), 2):
            l, r = chain(level[i]), chain(level[i + 1])
            atoms.append((l, r, n))
            up.append(n)
            n += 1
        level = up
    return n, atoms, {g, *leaves}, level[0]


def k_star(n, atoms, order):
    """Least k with |closure(order[:k])| >= n / 2, by binary search on the
    (monotone) closure size."""
    def size(k):
        return len(closure(n, atoms, order[:k]))
    lo, hi = 1, n
    if 2 * size(hi) < n:
        return n
    while lo < hi:
        mid = (lo + hi) // 2
        if 2 * size(mid) >= n:
            hi = mid
        else:
            lo = mid + 1
    return lo


# ------------------------------------------------------------------ spend-only distances by a tree DP

def spend_min_steps(n, atoms, F, w):
    """Second, search-free method for spend-only distances.  A spend-only run
    produces each node of the derivation tree of what it carries once, and a
    tree of Strahler number <= w is evaluated with w carried distinctions in
    exactly its number of internal nodes (Sethi-Ullman order), so the BFS
    distance to the first state carrying v is the least number of internal
    nodes of a derivation tree of v over F of Strahler number <= w.
    size_0 = 0 on F, INF elsewhere; size_s by Dijkstra with initial labels
    size_{s-1} and, per atom (a, b -> c), edges a -> c of weight
    1 + size_{s-1}(b) and b -> c of weight 1 + size_{s-1}(a).
    Returns size_w as a list (INF when no tree of number <= w)."""
    import heapq
    F = set(F)
    prev = [0 if v in F else INF for v in range(n)]
    out_edges = [[] for _ in range(n)]
    for a, b, c in atoms:
        if c in F:
            continue
        out_edges[a].append((b, c))
        out_edges[b].append((a, c))
    for _ in range(w):
        cur = list(prev)
        heap = [(cur[v], v) for v in range(n) if cur[v] < INF]
        heapq.heapify(heap)
        done = [False] * n
        while heap:
            d, u = heapq.heappop(heap)
            if done[u] or d > cur[u]:
                continue
            done[u] = True
            for other, c in out_edges[u]:
                if prev[other] == INF:
                    continue
                nd = d + 1 + prev[other]
                if nd < cur[c]:
                    cur[c] = nd
                    heapq.heappush(heap, (nd, c))
        prev = cur
    return prev


def run_spend_dp(n, atoms, held, w):
    """All phases of the spend-only law from the DP alone: phase t forces
    the v with a finite size_w over F_t; L_t = the largest such size."""
    F = set(held)
    phase = [-1] * n
    for v in F:
        phase[v] = 0
    Ls, t = [], 0
    while True:
        s = spend_min_steps(n, atoms, F, w)
        new = [v for v in range(n) if v not in F and s[v] < INF]
        if not new:
            break
        t += 1
        Ls.append(max(s[v] for v in new))
        for v in new:
            phase[v] = t
        F |= set(new)
    return {"phase": phase, "P": t, "L": Ls, "T": sum(rounds_of(L) for L in Ls), "forced": F}
