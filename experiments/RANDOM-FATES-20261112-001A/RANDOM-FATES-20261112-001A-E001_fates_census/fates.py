"""Random meeting patterns under the not-all-equal law (NAE): the processes, growth to a contradiction, and the readings.

Frozen library of RANDOM-FATES-20261112-001A-E001 (contract.json beside this file). A knot is a sorted triple of distinctions;
distinctions are 0, 1, 2, ... in order of arrival. NAE on a knot {a, b, c} is the two clauses (a or b or c) and
(not a or not b or not c), with no signs. A set S of distinctions is free when every pattern on S extends to an allowed state;
since NAE is complement-closed, the patterns with a fixed first value suffice. A bond is a constrained set all of whose proper
parts are free; bond distance of u, v is one less than the size of the smallest bond containing both.
"""

from __future__ import annotations

import itertools
import random
from collections import defaultdict, deque

import numpy as np
from pysat.solvers import Solver

SOLVER = "cadical153"


def cls(t):
    a, b, c = t
    return [[a + 1, b + 1, c + 1], [-(a + 1), -(b + 1), -(c + 1)]]


# ----------------------------------------------------------------------------------------------------------------------
# Processes. Each is an endless generator of knots (None for a step that adds nothing).
# ----------------------------------------------------------------------------------------------------------------------

def proc_uniform(n, rng):
    """U(n): distinct uniformly random triples of n distinctions, in a uniformly random order."""
    seen = set()
    total = n * (n - 1) * (n - 2) // 6
    while True:
        if len(seen) >= total:
            yield None
            continue
        t = tuple(sorted(rng.sample(range(n), 3)))
        if t in seen:
            continue
        seen.add(t)
        yield t


def proc_expand(q, rng):
    """X(q): from one knot; each step a closing knot on a uniform new triple of existing distinctions (probability q) or a
    knot of one new distinction and a uniform pair of existing ones."""
    n = 3
    seen = {(0, 1, 2)}
    yield (0, 1, 2)
    while True:
        if rng.random() < q:
            for _ in range(1000):
                t = tuple(sorted(rng.sample(range(n), 3)))
                if t not in seen:
                    break
            else:
                yield None
                continue
        else:
            a, b = rng.sample(range(n), 2)
            t = tuple(sorted((a, b, n)))
            n += 1
        seen.add(t)
        yield t


def proc_overlap(q, rng, local):
    """O(q): from one knot; each step picks a uniform knot and a uniform pair {p, r} of it (so a pair is picked in proportion
    to the knots on it), then a third distinction: new (probability 1 - q) or existing, uniform over all distinctions
    (global) or over those within two steps of p or r (local), never making a knot twice."""
    n = 3
    knots = [(0, 1, 2)]
    seen = {(0, 1, 2)}
    nbr = defaultdict(set)
    for x, y in itertools.combinations((0, 1, 2), 2):
        nbr[x].add(y)
        nbr[y].add(x)
    yield (0, 1, 2)
    while True:
        k = knots[rng.randrange(len(knots))]
        p, r = rng.sample(k, 2)
        if rng.random() < q:
            if local:
                ball = set()
                for s in (p, r):
                    for y in nbr[s]:
                        ball.add(y)
                        ball |= nbr[y]
                cand = sorted(z for z in ball - {p, r} if tuple(sorted((p, r, z))) not in seen)
                if not cand:
                    yield None
                    continue
                z = rng.choice(cand)
            else:
                for _ in range(1000):
                    z = rng.randrange(n)
                    if z not in (p, r) and tuple(sorted((p, r, z))) not in seen:
                        break
                else:
                    yield None
                    continue
        else:
            z = n
            n += 1
        t = tuple(sorted((p, r, z)))
        seen.add(t)
        knots.append(t)
        for x, y in itertools.combinations(t, 2):
            nbr[x].add(y)
            nbr[y].add(x)
        yield t


def proc_band(w, q, rng):
    """L(w, q): each step a closing knot on a uniform missing triple of the newest w distinctions (probability q; nothing
    when all are knots) or a new distinction with a uniform pair of the w - 1 newest before it."""
    n = 3
    seen = {(0, 1, 2)}
    yield (0, 1, 2)
    while True:
        if rng.random() < q:
            lo = max(0, n - w)
            miss = [t for t in itertools.combinations(range(lo, n), 3) if t not in seen]
            if not miss:
                yield None
                continue
            t = rng.choice(miss)
        else:
            lo = max(0, n - w + 1)
            a, b = rng.sample(range(lo, n), 2)
            t = tuple(sorted((a, b, n)))
            n += 1
        seen.add(t)
        yield t


def proc_tree(rng):
    """T: the control with no cycle of knots: each step a knot of one uniform existing distinction and two new ones."""
    n = 3
    yield (0, 1, 2)
    while True:
        a = rng.randrange(n)
        t = (a, n, n + 1)
        n += 2
        yield t


# ----------------------------------------------------------------------------------------------------------------------
# Growth to a contradiction.
# ----------------------------------------------------------------------------------------------------------------------

def grow(gen, horizon):
    """Feed up to `horizon` moves of knots to an incremental solver, stopping at the first contradiction. Returns
    (knots, dead): when dead, the last knot is the one after which no state is allowed."""
    knots = []
    with Solver(name=SOLVER) as s:
        for _ in range(horizon):
            t = next(gen)
            if t is None:
                continue
            knots.append(t)
            for c in cls(t):
                s.add_clause(c)
            if not s.solve():
                return knots, True
    return knots, False


def death_core(knots):
    """An inclusion-minimal set of knots with no allowed state (deletion-based, from the solver's cores). Exact."""
    vmax = max(v for t in knots for v in t) + 1
    sel = [vmax + 1 + i for i in range(len(knots))]
    with Solver(name=SOLVER) as s:
        for i, t in enumerate(knots):
            for c in cls(t):
                s.add_clause(c + [-sel[i]])
        assert not s.solve(assumptions=sel)
        core_set = set(s.get_core())
        keep = [x for x in sel if x in core_set]
        i = 0
        while i < len(keep):
            trial = keep[:i] + keep[i + 1:]
            if not s.solve(assumptions=trial):
                c2 = set(s.get_core())
                keep = [x for x in trial if x in c2]
            else:
                i += 1
    return [knots[x - vmax - 1] for x in keep]


# ----------------------------------------------------------------------------------------------------------------------
# Meeting-pattern counts.
# ----------------------------------------------------------------------------------------------------------------------

def adjacency(n, knots):
    nbr = [set() for _ in range(n)]
    for t in knots:
        for x, y in itertools.combinations(t, 2):
            nbr[x].add(y)
            nbr[y].add(x)
    return nbr


def steps_from(nbr, src, cap=None):
    dist = {src: 0}
    dq = deque([src])
    while dq:
        x = dq.popleft()
        if cap is not None and dist[x] >= cap:
            continue
        for y in nbr[x]:
            if y not in dist:
                dist[y] = dist[x] + 1
                dq.append(y)
    return dist


def pair_counts(knots):
    pc = defaultdict(int)
    for t in knots:
        for x, y in itertools.combinations(t, 2):
            pc[(x, y)] += 1
    return pc


# ----------------------------------------------------------------------------------------------------------------------
# Readings under NAE.
# ----------------------------------------------------------------------------------------------------------------------

class Reader:
    """The allowed states of a base, read exactly through an incremental solver, with a growing sample of states used
    only to show that patterns occur."""

    def __init__(self, n, knots, samples=200, seed=0):
        self.n = n
        self.knots = list(knots)
        self.used = set(v for t in self.knots for v in t)
        self.s = Solver(name=SOLVER, bootstrap_with=[c for t in self.knots for c in cls(t)])
        self.ok = self.s.solve()
        self.calls = 1
        self.rng = random.Random(seed)
        rows = []
        if self.ok:
            for _ in range(samples):
                self.s.set_phases([v + 1 if self.rng.random() < 0.5 else -(v + 1) for v in range(n)])
                self.s.solve()
                self.calls += 1
                rows.append(self._row(self.s.get_model()))
        self.rows = np.array(rows, dtype=np.uint8).reshape(-1, n)
        self.cache = {}

    def close(self):
        self.s.delete()

    def _row(self, m):
        row = [self.rng.randrange(2) for _ in range(self.n)]   # a distinction in no knot is free
        for lit in m:
            if 0 < abs(lit) <= self.n:
                row[abs(lit) - 1] = 1 if lit > 0 else 0
        return row

    def _add_row(self, m):
        self.rows = np.vstack([self.rows, np.array([self._row(m)], dtype=np.uint8)])

    def _assume(self, vs, bits):
        return [v + 1 if b else -(v + 1) for v, b in zip(vs, bits) if v in self.used]

    def extends(self, vs, bits):
        """Does the pattern `bits` on distinctions `vs` extend to an allowed state? Exact."""
        key = (tuple(vs), tuple(bits))
        if key in self.cache:
            return self.cache[key]
        if len(self.rows) and np.any(np.all(self.rows[:, list(vs)] == np.array(bits, dtype=np.uint8), axis=1)):
            self.cache[key] = True
            return True
        r = self.s.solve(assumptions=self._assume(vs, bits))
        self.calls += 1
        if r:
            self._add_row(self.s.get_model())
        self.cache[key] = r
        return r

    def free(self, vs):
        vs = list(vs)
        return all(self.extends(vs, (0,) + rest) for rest in itertools.product((0, 1), repeat=len(vs) - 1))

    def free_by_sample(self, S):
        """True only when every pattern on S, up to complement, occurs in the sample (so S is free)."""
        sub = self.rows[:, list(S)]
        code = np.zeros(len(sub), dtype=np.int64)
        last = sub[:, -1]
        for i in range(len(S) - 1):
            code |= ((sub[:, i] ^ last).astype(np.int64)) << i
        return len(np.unique(code)) == (1 << (len(S) - 1))

    def tie_classes(self):
        """Classes of two or more distinctions tied together (each pair equal in every state or unequal in every state),
        as lists of (distinction, relation to the class's first member). Exact: every tie is shown by the solver."""
        verified = set()
        live = sorted(self.used)                       # a distinction in no knot is tied to nothing
        while True:
            R = self.rows
            norm = R ^ R[0:1, :]
            groups = defaultdict(list)
            for v in live:
                groups[norm[:, v].tobytes()].append(v)
            pending = None
            for g in groups.values():
                if len(g) < 2:
                    continue
                for v in g[1:]:
                    if (g[0], v) not in verified:
                        pending = (g[0], v)
                        break
                if pending:
                    break
            if pending is None:
                break
            r, v = pending
            e = int(R[0, r] ^ R[0, v])
            ok = self.s.solve(assumptions=self._assume([r, v], [0, 1 - e]))
            self.calls += 1
            if ok:
                self._add_row(self.s.get_model())
            else:
                verified.add((r, v))
        R = self.rows
        norm = R ^ R[0:1, :]
        groups = defaultdict(list)
        for v in live:
            groups[norm[:, v].tobytes()].append(v)
        return [[(v, int(R[0, g[0]] ^ R[0, v])) for v in g] for g in groups.values() if len(g) >= 2]

    def is_bond(self, S):
        if self.free(S):
            return False
        return all(self.free([x for x in S if x != y]) for y in S)

    def least_bond_with(self, u, v, exhaustive4, lens, lens_max):
        """(size, kind) of the smallest bond containing u and v: size 2 and 3 over all distinctions, size 4 over all when
        exhaustive4, then sizes up to lens_max with the rest from the lens. (None, 'none') when nothing is found."""
        if not self.free([u, v]):
            return 2, "all"
        others = [w for w in range(self.n) if w not in (u, v) and w in self.used]
        for w in others:
            S = [u, v, w]
            if not self.free_by_sample(S) and self.is_bond(S):
                return 3, "all"
        if exhaustive4 and self._size4(u, v, others):
            return 4, "all"
        L = [w for w in lens if w not in (u, v)]
        for size in range(4 if not exhaustive4 else 5, lens_max + 1):
            for extra in itertools.combinations(L, size - 2):
                S = [u, v, *extra]
                if not self.free_by_sample(S) and self.is_bond(S):
                    return size, "lens"
        return None, "none"

    def _size4(self, u, v, others):
        R = self.rows
        o = np.array(others)
        if len(o) < 2:
            return None
        Wi, Xi = np.triu_indices(len(o), 1)
        for lo in range(0, len(Wi), 200000):
            W, X = o[Wi[lo:lo + 200000]], o[Xi[lo:lo + 200000]]
            code = ((R[:, u][:, None] ^ R[:, X]).astype(np.int8) | ((R[:, v][:, None] ^ R[:, X]).astype(np.int8) << 1)
                    | ((R[:, W] ^ R[:, X]).astype(np.int8) << 2))
            present = np.zeros((len(W), 8), dtype=bool)
            for k in range(8):
                present[:, k] = np.any(code == k, axis=0)
            for i in np.where(~present.all(axis=1))[0]:
                S = [u, v, int(W[i]), int(X[i])]
                if self.is_bond(S):
                    return S
        return None

    def unnamed_hollow_triples(self, free_pairs_ok):
        """Every triple, not a knot, whose three pairs are free and which is constrained (exhaustive; small bases only)."""
        n = self.n
        kset = set(self.knots)
        out = []
        for t in itertools.combinations(sorted(self.used), 3):
            if t in kset or not all(free_pairs_ok(a, b) for a, b in itertools.combinations(t, 2)):
                continue
            if self.free_by_sample(t):
                continue
            if not self.free(t):
                out.append(t)
        return out


def read_base(n, knots, rng, full=True, pairs_per_d=8, ds=(1, 2, 3), exhaustive4_max=600, triples_max=150,
              lens_cap=40, samples=200, seed=0):
    """The frozen reading of one base. Returns a dict of plain values."""
    out = {"n_used": 0, "knots": len(knots)}
    rd = Reader(n, knots, samples=samples, seed=seed)
    used = sorted(rd.used)
    out["n_used"] = len(used)
    if not rd.ok:
        out["state"] = False
        rd.close()
        return out
    out["state"] = True
    classes = rd.tie_classes()
    sizes = sorted((len(c) for c in classes), reverse=True)
    out["classes"] = len(classes)
    out["class_sizes_top"] = sizes[:10]
    out["largest_class"] = sizes[0] if sizes else 1
    out["tied_pairs"] = sum(s * (s - 1) // 2 for s in sizes)
    out["tied_distinctions"] = sum(sizes)
    nbr = adjacency(n, knots)
    # how far forcing reaches: steps apart of tied pairs
    reach, tsteps = 0, []
    budget = 300
    for c in sorted(classes, key=len):
        mem = [v for v, _ in c]
        srcs = mem if len(mem) <= 20 else rng.sample(mem, 20)
        for a in srcs:
            if budget <= 0:
                break
            budget -= 1
            dist = steps_from(nbr, a)
            for b in mem:
                if b != a:
                    d = dist.get(b)
                    if d is not None:
                        reach = max(reach, d)
                        if len(tsteps) < 2000:
                            tsteps.append(d)
    out["tie_reach"] = reach
    out["tie_steps_median"] = float(np.median(tsteps)) if tsteps else None
    if classes:
        big = max(classes, key=len)
        idx = [v for v, _ in big]
        out["largest_class_index_span"] = max(idx) - min(idx)
        out["largest_class_relations"] = [sum(1 for _, e in big if e == 0), sum(1 for _, e in big if e == 1)]
    pc = pair_counts(knots)
    out["max_knots_on_pair"] = max(pc.values()) if pc else 0
    out["pairs_in_two_or_more"] = sum(1 for x in pc.values() if x >= 2)
    out["co_knotted_pairs"] = len(pc)
    if full:
        tied_with = {}
        for c in classes:
            for v, _ in c:
                tied_with[v] = c[0][0]
        free_pair = lambda a, b: not (a in tied_with and tied_with.get(b) == tied_with[a])
        if len(used) <= triples_max:
            hol = rd.unnamed_hollow_triples(free_pair)
            out["unnamed_hollow_triples"] = len(hol)
            out["faithful"] = (not classes) and not hol and all(
                free_pair(a, b) for t in knots for a, b in itertools.combinations(t, 2))
        prof = {}
        for d in ds:
            res = []
            tries = 0
            while len(res) < pairs_per_d and tries < 50 * pairs_per_d:
                tries += 1
                u = rng.choice(used)
                dist = steps_from(nbr, u, cap=d)
                vs = sorted(x for x, dd in dist.items() if dd == d)
                if not vs:
                    continue
                v = rng.choice(vs)
                du = steps_from(nbr, u, cap=d + 1)
                dv = steps_from(nbr, v, cap=d + 1)
                lens = sorted((w for w in du if w in dv and du[w] + dv[w] <= d + 1), key=lambda w: (du[w] + dv[w], w))
                lens = lens[:lens_cap]
                size, kind = rd.least_bond_with(u, v, exhaustive4=len(used) <= exhaustive4_max, lens=lens,
                                                lens_max=min(d + 2, 5))
                res.append([u, v, size, kind])
            prof[str(d)] = res
        out["bond_profile"] = prof
        balls = []
        for _ in range(3):
            u = rng.choice(used)
            dist = steps_from(nbr, u, cap=6)
            balls.append([sum(1 for x in dist.values() if x <= r) for r in range(1, 7)])
        out["step_balls"] = balls
    out["solver_calls"] = rd.calls
    rd.close()
    return out
