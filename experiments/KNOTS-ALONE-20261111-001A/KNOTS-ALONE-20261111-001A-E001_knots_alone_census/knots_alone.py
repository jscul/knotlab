"""Knots alone (KNOTS-ALONE-20261111-001A-E001): what a uniform knot law reads of a world of knots alone.

A world is a finite set of distinctions 0..V-1 and a set T of three-element subsets, its knots; nothing else is given.
A uniform law puts one symmetric three-place relation on every knot, given by the weights (number of 1s) it allows:

    PAR {1,3}   parity (complement: {0,2})
    NAE {1,2}   not all equal (its own complement)
    OR  {1,2,3} the clause (complement: NAND {0,1,2})
    NOL {0,2,3} not exactly one 1 (complement: {0,1,3})

These are the four classes, up to complementing every distinction, of symmetric three-place relations that pass K1-K3.

Readings, all from the world's allowed states (every knot's relation holds), other distinctions quantified away:
- allowed: some state; frozen distinction: one value only;
- tie: a pair of unfrozen distinctions whose four value pairs do not all occur;
- 3-bond: a triple whose pairs all occur in full but whose eight patterns do not (a three-place knot of the world);
- native: allowed, and every knot of T is a 3-bond;
- faithful: native, no frozen distinction, no tie, and the 3-bonds are exactly T;
- bond distance: the least size of a bond (a constrained set of three or more whose every co-1 subset is free) through
  two distinctions, minus one.
"""

from __future__ import annotations

import itertools
import time
import random
from collections import defaultdict, deque

import numpy as np
from pysat.card import CardEnc, EncType
from pysat.formula import IDPool
from pysat.solvers import Minisat22

LAWS = {"PAR": frozenset({1, 3}), "NAE": frozenset({1, 2}), "OR": frozenset({1, 2, 3}), "NOL": frozenset({0, 2, 3})}


# ----------------------------------------------------------------------------------------------------------------------
# Worlds
# ----------------------------------------------------------------------------------------------------------------------

def norm(T):
    return tuple(sorted(tuple(sorted(t)) for t in T))


def degrees(V, T):
    deg = [0] * V
    for t in T:
        for v in t:
            deg[v] += 1
    return deg


def edges_of(T):
    count = defaultdict(int)
    for t in T:
        for e in itertools.combinations(t, 2):
            count[e] += 1
    return count


def connected(V, T):
    adj = defaultdict(set)
    for t in T:
        for a, b in itertools.combinations(t, 2):
            adj[a].add(b)
            adj[b].add(a)
    seen, stack = {0}, [0]
    while stack:
        u = stack.pop()
        for w in adj[u]:
            if w not in seen:
                seen.add(w)
                stack.append(w)
    return len(seen) == V


def link_cycles(V, T, v):
    """The cycle lengths of the link of v, or None if the link is not 2-regular."""
    adj = defaultdict(list)
    for t in T:
        if v in t:
            a, b = [x for x in t if x != v]
            adj[a].append(b)
            adj[b].append(a)
    if any(len(n) != 2 for n in adj.values()):
        return None
    seen, lengths = set(), []
    for start in adj:
        if start in seen:
            continue
        length, prev, cur = 0, None, start
        while True:
            seen.add(cur)
            length += 1
            nxt = adj[cur][0] if adj[cur][0] != prev else adj[cur][1]
            prev, cur = cur, nxt
            if cur == start:
                break
        lengths.append(length)
    return sorted(lengths)


def is_surface(V, T):
    """Every co-knotted pair in exactly two knots and every link a single cycle: a closed triangulated surface."""
    if any(c != 2 for c in edges_of(T).values()):
        return False
    for v in range(V):
        lc = link_cycles(V, T, v)
        if lc is None or len(lc) != 1:
            return False
    return connected(V, T)


def euler(V, T):
    return V - len(edges_of(T)) + len(T)


def orientable(T):
    """Orient the triangles consistently across every edge, or report that it cannot be done (surface worlds only)."""
    T = [tuple(t) for t in T]
    edge_tris = defaultdict(list)
    for i, t in enumerate(T):
        for e in itertools.combinations(sorted(t), 2):
            edge_tris[e].append(i)
    orient = {0: T[0]}
    queue = deque([0])

    def directed(tri):
        a, b, c = tri
        return {(a, b), (b, c), (c, a)}

    while queue:
        i = queue.popleft()
        d_i = directed(orient[i])
        for e in itertools.combinations(sorted(T[i]), 2):
            for j in edge_tris[e]:
                if j == i:
                    continue
                a, b, c = T[j]
                cand = (a, b, c)
                # the shared edge must run the other way in j
                if (e[0], e[1]) in d_i:
                    want = (e[1], e[0])
                else:
                    want = (e[0], e[1])
                if want not in directed(cand):
                    cand = (a, c, b)
                if j in orient:
                    if set(directed(orient[j])) != set(directed(cand)):
                        return False
                else:
                    orient[j] = cand
                    queue.append(j)
    return True


def canon_codes_surface(T, all_flags=True, flag=None):
    """Canonical codes of a connected world in which every co-knotted pair lies in exactly two knots.

    From a flag (an ordered knot), a breadth-first traversal across edges relabels the distinctions; the traversal uses
    only the world's structure, so two worlds are isomorphic exactly when their sets of flag codes meet.
    """
    edge_tris = defaultdict(list)
    for t in T:
        for e in itertools.combinations(sorted(t), 2):
            edge_tris[e].append(t)
    flags = [p for t in T for p in itertools.permutations(t)] if all_flags else [flag]
    codes = []
    for a, b, c in flags:
        lab = {a: 0, b: 1, c: 2}
        nxt = 3
        start = tuple(sorted((a, b, c)))
        seen = {start}
        queue = deque([(a, b, c)])
        while queue:
            x, y, z = queue.popleft()
            cur = tuple(sorted((x, y, z)))
            for p, q in ((x, y), (y, z), (z, x)):
                others = [s for s in edge_tris[tuple(sorted((p, q)))] if s != cur]
                s = others[0]
                r = [w for w in s if w != p and w != q][0]
                if r not in lab:
                    lab[r] = nxt
                    nxt += 1
                if s not in seen:
                    seen.add(s)
                    queue.append((q, p, r))
        codes.append(tuple(sorted(tuple(sorted(lab[v] for v in t)) for t in T)))
    return codes


class SurfaceClasses:
    """Isomorphism classes of surface-like worlds, by flag codes."""

    def __init__(self):
        self.reps = []
        self.known = set()

    def add(self, T):
        T = norm(T)
        code = canon_codes_surface(T, all_flags=False, flag=T[0])[0]
        if code in self.known:
            return False
        codes = canon_codes_surface(T)
        self.known.update(codes)
        self.reps.append(min(codes))
        return True


def surface_worlds_sat(V, d, symmetry=True, budget=None):
    """Every closed triangulated surface on V distinctions with every distinction in d knots, up to isomorphism (d <= 7).

    Exhaustive SAT enumeration with distinction 0's link fixed as the cycle 1..d, and (sound) breadth-first symmetry
    breaking on the other labels: the least neighbour of w is nondecreasing in w for w > d.
    """
    assert 3 <= d <= 7
    if (V * d) % 3:
        return ([], 0) if budget is None else ([], 0, True)
    trip = list(itertools.combinations(range(V), 3))
    pool = IDPool()
    tv = {t: pool.id(("t", t)) for t in trip}
    clauses = []
    zero = {tuple(sorted((0, i, i % d + 1))) for i in range(1, d + 1)}
    for t in trip:
        if 0 in t:
            clauses.append([tv[t]] if t in zero else [-tv[t]])
    for v in range(1, V):
        lits = [tv[t] for t in trip if v in t]
        clauses.extend(CardEnc.equals(lits=lits, bound=d, vpool=pool, encoding=EncType.seqcounter).clauses)
    for u, v in itertools.combinations(range(V), 2):
        lits = [tv[t] for t in trip if u in t and v in t]
        clauses.extend(CardEnc.atmost(lits=lits, bound=2, vpool=pool, encoding=EncType.seqcounter).clauses)
        for l in lits:
            clauses.append([-l] + [m for m in lits if m != l])
    if d >= 6:
        for v in range(V):
            rest = [w for w in range(V) if w != v]
            for a, b, c in itertools.combinations(rest, 3):
                clauses.append([-tv[tuple(sorted((v, a, b)))], -tv[tuple(sorted((v, b, c)))], -tv[tuple(sorted((v, a, c)))]])
    if symmetry:
        adj = {}
        for u, w in itertools.combinations(range(V), 2):
            x = pool.id(("adj", u, w))
            adj[(u, w)] = adj[(w, u)] = x
            lits = [tv[t] for t in trip if u in t and w in t]
            clauses.append([-x] + lits)
            for l in lits:
                clauses.append([-l, x])
        for w in range(d + 1, V - 1):
            w2 = w + 1
            for u in range(V):
                if u in (w, w2):
                    continue
                clauses.append([-adj[(u, w2)]] + [adj[(x, w)] for x in range(0, u + 1) if x != w])
    classes = SurfaceClasses()
    n_labelled = 0
    tvars = [tv[t] for t in trip]
    start = time.time()
    complete = True
    with Minisat22(bootstrap_with=clauses) as s:
        while s.solve():
            model = s.get_model()
            pos = set(l for l in model if l > 0)
            T = [t for t in trip if tv[t] in pos]
            n_labelled += 1
            s.add_clause([-x if x in pos else x for x in tvars])
            if is_surface(V, T):
                classes.add(T)
            if budget is not None and time.time() - start > budget:
                complete = False
                break
    if budget is None:
        return classes.reps, n_labelled
    return classes.reps, n_labelled, complete


def lattice_tori(V):
    """Every 6-regular triangulated torus with V distinctions: the triangular lattice Z^2 (neighbours +-(1,0), +-(0,1),
    +-(1,1)) modulo a sublattice of index V, kept when the quotient is a simplicial surface (Altshuler: these are all)."""
    out = SurfaceClasses()
    for a in range(1, V + 1):
        if V % a:
            continue
        c = V // a
        for b in range(c):
            # L spanned by (a, b) and (0, c); a coset (x, y) is reduced to x in [0, a), y in [0, c)
            def red(x, y):
                q, x0 = divmod(x, a)
                return x0, (y - q * b) % c
            idx = {}
            for x in range(a):
                for y in range(c):
                    idx[(x, y)] = len(idx)
            T = set()
            ok = True
            for x in range(a):
                for y in range(c):
                    for tri in (((x, y), (x + 1, y), (x + 1, y + 1)), ((x, y), (x, y + 1), (x + 1, y + 1))):
                        vs = tuple(sorted(idx[red(*p)] for p in tri))
                        if len(set(vs)) < 3:
                            ok = False
                        T.add(vs)
            if not ok or len(T) != 2 * V:
                continue
            T = sorted(T)
            if all(dg == 6 for dg in degrees(V, T)) and is_surface(V, T):
                out.add(T)
    return out.reps


def lattice_torus_with_coords(a, b, c):
    """The torus Z^2/<(a,b),(0,c)> with its coset coordinates (for the bond-distance reading), or None if not simplicial."""
    V = a * c

    def red(x, y):
        q, x0 = divmod(x, a)
        return x0, (y - q * b) % c
    idx = {}
    for x in range(a):
        for y in range(c):
            idx[(x, y)] = len(idx)
    T = set()
    for x in range(a):
        for y in range(c):
            for tri in (((x, y), (x + 1, y), (x + 1, y + 1)), ((x, y), (x, y + 1), (x + 1, y + 1))):
                vs = tuple(sorted(idx[red(*p)] for p in tri))
                if len(set(vs)) < 3:
                    return None
                T.add(vs)
    T = sorted(T)
    if len(T) != 2 * V or not is_surface(V, T):
        return None
    return V, T


def random_regular_worlds(V, d, n, seed):
    """Seeded configuration-model sample of connected simple d-regular triple systems on V distinctions."""
    rng = random.Random(seed)
    out, seen, tries = [], set(), 0
    if (V * d) % 3:
        return out
    while len(out) < n and tries < 200 * n:
        tries += 1
        pts = [v for v in range(V) for _ in range(d)]
        rng.shuffle(pts)
        T = [tuple(sorted(pts[i:i + 3])) for i in range(0, len(pts), 3)]
        if any(len(set(t)) < 3 for t in T) or len(set(T)) < len(T):
            continue
        if not connected(V, T):
            continue
        key = norm(T)
        if key in seen:
            continue
        seen.add(key)
        out.append(list(key))
    return out


# ----------------------------------------------------------------------------------------------------------------------
# Laws, by SAT
# ----------------------------------------------------------------------------------------------------------------------

def law_clauses(T, W):
    cl = []
    for t in T:
        for bits in itertools.product((0, 1), repeat=3):
            if sum(bits) not in W:
                cl.append([-(t[i] + 1) if bits[i] else (t[i] + 1) for i in range(3)])
    return cl


def read_law_sat(V, T, W, triples=True, samples=64, seed=0):
    """Allowed, frozen, ties, 3-bonds, native and faithful, by SAT under assumptions."""
    rng = random.Random(seed)
    res = {}
    with Minisat22(bootstrap_with=law_clauses(T, W)) as s:
        if not s.solve():
            return {"allowed": False}
        seen_models = []
        for _ in range(samples):
            s.set_phases([v + 1 if rng.random() < 0.5 else -(v + 1) for v in range(V)])
            s.solve()
            m = s.get_model()
            seen_models.append(tuple(1 if m[v] > 0 else 0 for v in range(V)))
        S = np.array(seen_models, dtype=np.uint8)

        cache = {}

        def ext(vars_, pattern):
            key = (vars_, pattern)
            if key not in cache:
                cache[key] = s.solve(assumptions=[v + 1 if p else -(v + 1) for v, p in zip(vars_, pattern)])
            return cache[key]

        def count(vars_):
            pats = set(map(tuple, S[:, list(vars_)]))
            n = len(pats)
            for p in itertools.product((0, 1), repeat=len(vars_)):
                if p not in pats and ext(vars_, p):
                    n += 1
            return n

        single = [count((v,)) for v in range(V)]
        frozen = [v for v in range(V) if single[v] < 2]
        pair_count = {}
        for u, v in itertools.combinations(range(V), 2):
            pair_count[(u, v)] = count((u, v))
        ties = [p for p, n in pair_count.items() if n < 4 and p[0] not in frozen and p[1] not in frozen]
        free_pair = {p for p, n in pair_count.items() if n == 4}
        knots = set(norm(T))
        bonds3 = None
        if triples:
            bonds3 = []
            for t in itertools.combinations(range(V), 3):
                if all(q in free_pair for q in itertools.combinations(t, 2)):
                    if t in knots:
                        bonds3.append(t)   # constrained by its own relation (not all eight weights allowed)
                    elif count(t) < 8:
                        bonds3.append(t)
        native = all(all(q in free_pair for q in itertools.combinations(t, 2)) for t in knots)
        res = {"allowed": True, "frozen": len(frozen), "ties": len(ties), "native": native}
        if triples:
            extra = sorted(set(bonds3) - knots)
            res["bonds3"] = len(bonds3)
            res["extra_bonds3"] = len(extra)
            res["faithful"] = native and not frozen and not ties and not extra
    return res


# ----------------------------------------------------------------------------------------------------------------------
# Independent paths: GF(2) for parity, brute force for small worlds
# ----------------------------------------------------------------------------------------------------------------------

def gf2_solve(rows, rhs, n):
    """Rows as int bitmasks over n variables. Returns (particular, nullspace basis) or None if inconsistent."""
    rows = list(rows)
    rhs = list(rhs)
    piv_cols, r = [], 0
    for col in range(n):
        p = next((i for i in range(r, len(rows)) if rows[i] >> col & 1), None)
        if p is None:
            continue
        rows[r], rows[p] = rows[p], rows[r]
        rhs[r], rhs[p] = rhs[p], rhs[r]
        for i in range(len(rows)):
            if i != r and rows[i] >> col & 1:
                rows[i] ^= rows[r]
                rhs[i] ^= rhs[r]
        piv_cols.append(col)
        r += 1
    if any(rows[i] == 0 and rhs[i] for i in range(r, len(rows))):
        return None
    x0 = 0
    for i, col in enumerate(piv_cols):
        if rhs[i]:
            x0 |= 1 << col
    free = [c for c in range(n) if c not in piv_cols]
    basis = []
    for f in free:
        vec = 1 << f
        for i, col in enumerate(piv_cols):
            if rows[i] >> f & 1:
                vec |= 1 << col
        basis.append(vec)
    return x0, basis


def read_parity_gf2(V, T, odd=True):
    rows = [sum(1 << v for v in t) for t in T]
    sol = gf2_solve(rows, [1 if odd else 0] * len(T), V)
    if sol is None:
        return {"allowed": False}
    _, basis = sol

    def rank(vars_):
        vecs = [sum(((b >> v) & 1) << i for i, v in enumerate(vars_)) for b in basis]
        rk, piv = 0, {}
        for x in vecs:
            while x:
                h = x.bit_length() - 1
                if h in piv:
                    x ^= piv[h]
                else:
                    piv[h] = x
                    rk += 1
                    break
        return rk
    frozen = [v for v in range(V) if rank((v,)) == 0]
    free_pair = {p for p in itertools.combinations(range(V), 2) if rank(p) == 2}
    ties = [p for p in itertools.combinations(range(V), 2)
            if p not in free_pair and p[0] not in frozen and p[1] not in frozen]
    knots = set(norm(T))
    bonds3 = [t for t in itertools.combinations(range(V), 3)
              if all(q in free_pair for q in itertools.combinations(t, 2)) and rank(t) < 3]
    native = all(all(q in free_pair for q in itertools.combinations(t, 2)) for t in knots)
    extra = set(bonds3) - knots
    return {"allowed": True, "frozen": len(frozen), "ties": len(ties), "native": native, "bonds3": len(bonds3),
            "extra_bonds3": len(extra), "faithful": native and not frozen and not ties and not extra,
            "states": 2 ** len(basis)}


def all_states(V, T, W, chunk=1 << 20):
    """Every allowed state, by brute force over all 2^V assignments (V <= 24)."""
    assert V <= 24
    allowed_w = np.zeros(4, dtype=bool)
    for w in W:
        allowed_w[w] = True
    out = []
    for start in range(0, 1 << V, chunk):
        x = np.arange(start, min(start + chunk, 1 << V), dtype=np.int64)
        ok = np.ones(len(x), dtype=bool)
        for t in T:
            w = ((x >> t[0]) & 1) + ((x >> t[1]) & 1) + ((x >> t[2]) & 1)
            ok &= allowed_w[w]
        out.append(x[ok])
    return np.concatenate(out)


def pattern_count(states, vars_):
    code = np.zeros(len(states), dtype=np.int64)
    for i, v in enumerate(vars_):
        code |= ((states >> v) & 1) << i
    return int(np.count_nonzero(np.bincount(code, minlength=1 << len(vars_))))


def read_law_brute(V, T, W):
    st = all_states(V, T, W)
    if len(st) == 0:
        return {"allowed": False}
    frozen = [v for v in range(V) if pattern_count(st, (v,)) < 2]
    free_pair = {p for p in itertools.combinations(range(V), 2) if pattern_count(st, p) == 4}
    ties = [p for p in itertools.combinations(range(V), 2)
            if p not in free_pair and p[0] not in frozen and p[1] not in frozen]
    knots = set(norm(T))
    bonds3 = [t for t in itertools.combinations(range(V), 3)
              if all(q in free_pair for q in itertools.combinations(t, 2)) and pattern_count(st, t) < 8]
    native = all(all(q in free_pair for q in itertools.combinations(t, 2)) for t in knots)
    extra = set(bonds3) - knots
    return {"allowed": True, "frozen": len(frozen), "ties": len(ties), "native": native, "bonds3": len(bonds3),
            "extra_bonds3": len(extra), "faithful": native and not frozen and not ties and not extra,
            "states": int(len(st))}


# ----------------------------------------------------------------------------------------------------------------------
# Bond distance from one distinction, from an explicit list of allowed states
# ----------------------------------------------------------------------------------------------------------------------

def enumerate_states_sat(V, T, W, cap):
    """Every allowed state by SAT with blocking clauses, or None above cap."""
    out = []
    with Minisat22(bootstrap_with=law_clauses(T, W)) as s:
        while s.solve():
            m = s.get_model()
            x = 0
            for v in range(V):
                if m[v] > 0:
                    x |= 1 << v
            out.append(x)
            if len(out) > cap:
                return None
            s.add_clause([-(v + 1) if m[v] > 0 else (v + 1) for v in range(V)])
    return np.array(out, dtype=np.int64)


def graph_distance(V, T, src):
    adj = defaultdict(set)
    for t in T:
        for a, b in itertools.combinations(t, 2):
            adj[a].add(b)
            adj[b].add(a)
    dist = {src: 0}
    q = deque([src])
    while q:
        u = q.popleft()
        for w in adj[u]:
            if w not in dist:
                dist[w] = dist[u] + 1
                q.append(w)
    return [dist[v] for v in range(V)]


def bond_distances_from(V, T, states, src, kmax):
    """For each v != src, the least bond through src and v of size at most kmax, minus one (None if none)."""
    full = {}

    def is_full(vars_):
        key = tuple(sorted(vars_))
        if key not in full:
            full[key] = pattern_count(states, key) == 1 << len(key)
        return full[key]

    def is_bond(S):
        if is_full(S):
            return False
        return all(is_full([x for x in S if x != y]) for y in S)

    out = {}
    others = [v for v in range(V) if v != src]
    for v in others:
        found = None
        rest = [w for w in others if w != v]
        for k in range(3, kmax + 1):
            for extra in itertools.combinations(rest, k - 2):
                S = (src, v) + extra
                if is_bond(S):
                    found = k - 1
                    break
            if found is not None:
                break
        out[v] = found
    return out


def random_regular_worlds_sat(V, d, n, seed, max_tries=None):
    """Seeded sample of connected simple d-regular triple systems on V distinctions, drawn by SAT with random phases
    (each distinction in exactly d triples). The sample is biased; it serves existence questions only."""
    if (V * d) % 3:
        return []
    rng = random.Random(seed)
    trip = list(itertools.combinations(range(V), 3))
    pool = IDPool()
    tv = {t: pool.id(("t", t)) for t in trip}
    clauses = []
    for v in range(V):
        lits = [tv[t] for t in trip if v in t]
        clauses.extend(CardEnc.equals(lits=lits, bound=d, vpool=pool, encoding=EncType.seqcounter).clauses)
    out, seen = [], set()
    tries = 0
    max_tries = max_tries or 20 * n
    with Minisat22(bootstrap_with=clauses) as s:
        while len(out) < n and tries < max_tries:
            tries += 1
            s.set_phases([tv[t] if rng.random() < d / (V - 1) * 1.5 else -tv[t] for t in rng.sample(trip, len(trip))])
            if not s.solve():
                break
            pos = set(l for l in s.get_model() if l > 0)
            T = [t for t in trip if tv[t] in pos]
            s.add_clause([-tv[t] for t in T])
            if not connected(V, T):
                continue
            key = norm(T)
            if key in seen:
                continue
            seen.add(key)
            out.append(list(key))
    return out


def has_nonfacial_triangle(V, T):
    knots = set(norm(T))
    adj = defaultdict(set)
    for t in T:
        for a, b in itertools.combinations(t, 2):
            adj[a].add(b)
            adj[b].add(a)
    for a in range(V):
        for b in adj[a]:
            if b <= a:
                continue
            for c in adj[a] & adj[b]:
                if c > b and (a, b, c) not in knots:
                    return True
    return False


def three_colouring(V, T):
    """A proper 3-colouring of a connected surface world's distinctions with every knot rainbow, or None (forced
    propagation from one knot; on a strongly connected surface such a colouring is unique up to permutation)."""
    edge_tris = defaultdict(list)
    for t in T:
        for e in itertools.combinations(sorted(t), 2):
            edge_tris[e].append(t)
    col = {T[0][0]: 0, T[0][1]: 1, T[0][2]: 2}
    queue = deque([tuple(T[0])])
    done = {tuple(T[0])}
    while queue:
        t = queue.popleft()
        for e in itertools.combinations(sorted(t), 2):
            for s in edge_tris[e]:
                r = [w for w in s if w not in e][0]
                want = 3 - col[e[0]] - col[e[1]]
                if r in col:
                    if col[r] != want:
                        return None
                else:
                    col[r] = want
                if s not in done:
                    done.add(s)
                    queue.append(s)
    if len(col) < V:
        return None
    for t in T:
        if len({col[v] for v in t}) < 3:
            return None
    return col
