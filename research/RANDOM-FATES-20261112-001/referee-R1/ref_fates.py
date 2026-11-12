"""Referee RANDOM-FATES-R1: the referee's own code for stage 1's census (no import of fates.py or census.py).

- The processes as the pre-registration's table defines them. To re-read the census's own bases, they draw their random numbers in
  the frozen order from the frozen seeds (sha256 of "label:run:grow", first 12 hex digits), so the regenerated growths can be
  matched against the recorded death knots, knot counts and sizes; a mismatch would mean the record is not what the seeds give.
- Growth to the first contradiction with Glucose 4 (the census used CaDiCaL).
- Tie classes: exact, by the referee's own method (states with random phases rule pairs out; every pair left is refuted twice).
- Least bonds: exact search by size; sizes 2 and 3 over every distinction; sizes 4 and 5 over every distinction when the base is
  small enough, otherwise over a lens with no cap (the census capped its lens at the 40 nearest)."""
import hashlib
import itertools
import random
from collections import defaultdict, deque

import numpy as np
from pysat.solvers import Glucose4


def seed_of(*parts):
    return int(hashlib.sha256(":".join(map(str, parts)).encode()).hexdigest()[:12], 16)


def nae_clauses(t):
    a, b, c = t
    return [[a + 1, b + 1, c + 1], [-(a + 1), -(b + 1), -(c + 1)]]


# ---------------------------------------------------------------- processes (pre-registration's table; frozen draw order)

def gen_uniform(n, rng):
    seen, total = set(), n * (n - 1) * (n - 2) // 6
    while True:
        if len(seen) >= total:
            yield None
            continue
        t = tuple(sorted(rng.sample(range(n), 3)))
        if t not in seen:
            seen.add(t)
            yield t


def gen_x(q, rng):
    n, seen = 3, {(0, 1, 2)}
    yield (0, 1, 2)
    while True:
        if rng.random() < q:
            t = None
            for _ in range(1000):
                c = tuple(sorted(rng.sample(range(n), 3)))
                if c not in seen:
                    t = c
                    break
            if t is None:
                yield None
                continue
        else:
            a, b = rng.sample(range(n), 2)
            t = tuple(sorted((a, b, n)))
            n += 1
        seen.add(t)
        yield t


def gen_o(q, rng, local):
    n, knots, seen = 3, [(0, 1, 2)], {(0, 1, 2)}
    nb = defaultdict(set)
    for x, y in itertools.combinations((0, 1, 2), 2):
        nb[x].add(y)
        nb[y].add(x)
    yield (0, 1, 2)
    while True:
        k = knots[rng.randrange(len(knots))]
        p, r = rng.sample(k, 2)
        if rng.random() < q:
            if local:
                near = set()
                for s in (p, r):
                    for y in nb[s]:
                        near.add(y)
                        near |= nb[y]
                cand = sorted(z for z in near - {p, r} if tuple(sorted((p, r, z))) not in seen)
                if not cand:
                    yield None
                    continue
                z = rng.choice(cand)
            else:
                z = None
                for _ in range(1000):
                    c = rng.randrange(n)
                    if c not in (p, r) and tuple(sorted((p, r, c))) not in seen:
                        z = c
                        break
                if z is None:
                    yield None
                    continue
        else:
            z = n
            n += 1
        t = tuple(sorted((p, r, z)))
        seen.add(t)
        knots.append(t)
        for x, y in itertools.combinations(t, 2):
            nb[x].add(y)
            nb[y].add(x)
        yield t


def gen_newest(w, q, rng):
    n, seen = 3, {(0, 1, 2)}
    yield (0, 1, 2)
    while True:
        if rng.random() < q:
            miss = [t for t in itertools.combinations(range(max(0, n - w), n), 3) if t not in seen]
            if not miss:
                yield None
                continue
            t = rng.choice(miss)
        else:
            a, b = rng.sample(range(max(0, n - w + 1), n), 2)
            t = tuple(sorted((a, b, n)))
            n += 1
        seen.add(t)
        yield t


def gen_tree(rng):
    n = 3
    yield (0, 1, 2)
    while True:
        a = rng.randrange(n)
        yield (a, n, n + 1)
        n += 2


def make(label, rng):
    if label.startswith("U"):
        return gen_uniform(int(label[1:]), rng)
    if label == "T":
        return gen_tree(rng)
    if label.startswith("X"):
        return gen_x(float(label[1:]), rng)
    if label.startswith("Og"):
        return gen_o(float(label[2:]), rng, False)
    if label.startswith("Ol"):
        return gen_o(float(label[2:]), rng, True)
    if label.startswith("L"):
        w, q = label[1:].split("_")
        return gen_newest(int(w), float(q), rng)
    raise ValueError(label)


def grow(label, run, seed_tag="grow", horizon=None):
    """(knots, dead): knots fed one move at a time until the first contradiction or the horizon"""
    rng = random.Random(seed_of(label, run, seed_tag))
    if horizon is None:
        horizon = 50 * int(label[1:]) if label.startswith("U") else (300 if label == "T" else 2000)
    g = make(label, rng)
    knots = []
    with Glucose4() as s:
        for _ in range(horizon):
            t = next(g)
            if t is None:
                continue
            knots.append(t)
            for c in nae_clauses(t):
                s.add_clause(c)
            if not s.solve():
                return knots, True
    return knots, False


# ---------------------------------------------------------------- meeting-pattern counts

def neighbours(n, knots):
    nb = [set() for _ in range(n)]
    for t in knots:
        for x, y in itertools.combinations(t, 2):
            nb[x].add(y)
            nb[y].add(x)
    return nb


def steps(nb, src, cap=None):
    d = {src: 0}
    q = deque([src])
    while q:
        x = q.popleft()
        if cap is not None and d[x] >= cap:
            continue
        for y in nb[x]:
            if y not in d:
                d[y] = d[x] + 1
                q.append(y)
    return d


# ---------------------------------------------------------------- the referee's reader

class Base:
    def __init__(self, n, knots, samples=400, seed=12345):
        self.n = n
        self.knots = list(knots)
        self.used = sorted({v for t in knots for v in t})
        self.s = Glucose4(bootstrap_with=[c for t in knots for c in nae_clauses(t)])
        self.ok = self.s.solve()
        rng = random.Random(seed)
        rows = []
        if self.ok:
            for _ in range(samples):
                self.s.set_phases([v + 1 if rng.random() < 0.5 else -(v + 1) for v in range(n)])
                self.s.solve()
                rows.append(self._row(self.s.get_model(), rng))
        self.rng = rng
        self.R = np.array(rows, dtype=np.uint8).reshape(-1, n)
        self.memo = {}

    def close(self):
        self.s.delete()

    def _row(self, m, rng):
        row = [rng.randrange(2) for _ in range(self.n)]
        for lit in m:
            if 0 < abs(lit) <= self.n:
                row[abs(lit) - 1] = 1 if lit > 0 else 0
        return row

    def extends(self, vs, bits):
        key = (tuple(vs), tuple(bits))
        if key in self.memo:
            return self.memo[key]
        if np.any(np.all(self.R[:, list(vs)] == np.array(bits, dtype=np.uint8), axis=1)):
            self.memo[key] = True
            return True
        used = set(self.used)
        ok = self.s.solve(assumptions=[v + 1 if b else -(v + 1) for v, b in zip(vs, bits) if v in used])
        if ok:
            self.R = np.vstack([self.R, np.array([self._row(self.s.get_model(), self.rng)], dtype=np.uint8)])
        self.memo[key] = ok
        return ok

    def free(self, vs):
        return all(self.extends(vs, (0,) + rest) for rest in itertools.product((0, 1), repeat=len(vs) - 1))

    def bond(self, S):
        return (not self.free(S)) and all(self.free([x for x in S if x != y]) for y in S)

    def ties(self):
        """exact tie classes: list of sorted member lists (classes of two or more)"""
        live = self.used
        R = self.R[:, live].astype(bool)
        Z = R ^ R[0:1, :]
        groups = defaultdict(list)
        for j, v in enumerate(live):
            groups[Z[:, j].tobytes()].append(v)
        classes = []
        for g in groups.values():
            # within a group, every pair has the same relation in every sampled state; refute or confirm against the first
            rest = list(g)
            while len(rest) > 1:
                a = rest[0]
                cls, keep = [a], []
                for v in rest[1:]:
                    e = int(self.R[0, a] ^ self.R[0, v])
                    if self.extends([a, v], (0, 1 - e)):
                        keep.append(v)          # a state separates them (the new state is added to the sample)
                    else:
                        cls.append(v)
                if len(cls) > 1:
                    classes.append(sorted(cls))
                rest = keep
        return classes

    def _patterns_seen(self, cols):
        """for each candidate set (rows of `cols`, indices of distinctions), whether every pattern up to the mirror occurs in R"""
        R = self.R
        last = R[:, cols[:, -1]]
        code = np.zeros((R.shape[0], cols.shape[0]), dtype=np.int64)
        for i in range(cols.shape[1] - 1):
            code |= ((R[:, cols[:, i]] ^ last).astype(np.int64)) << i
        need = 1 << (cols.shape[1] - 1)
        seen = np.zeros((cols.shape[0], need), dtype=bool)
        for k in range(need):
            seen[:, k] = np.any(code == k, axis=0)
        return seen.all(axis=1)

    def least_bond(self, u, v, pool4, pool5, max_size=5):
        """least size of a bond containing u and v, searched exactly: sizes 2 and 3 over every distinction, size 4 with the other
        two from pool4, size 5 with the other three from pool5 (lists of distinctions). None when nothing up to max_size."""
        if not self.free([u, v]):
            return 2
        others = [w for w in self.used if w not in (u, v)]
        o = np.array(others)
        cols = np.stack([np.full(len(o), u), np.full(len(o), v), o], axis=1)
        for i in np.where(~self._patterns_seen(cols))[0]:
            if self.bond([u, v, int(o[i])]):
                return 3
        for size, pool in ((4, pool4), (5, pool5)):
            if size > max_size:
                break
            pool = [w for w in pool if w not in (u, v)]
            if len(pool) < size - 2:
                continue
            for chunk in _chunks(itertools.combinations(pool, size - 2), 200000):
                ex = np.array(chunk)
                cols = np.concatenate([np.full((len(ex), 1), u), np.full((len(ex), 1), v), ex], axis=1)
                for i in np.where(~self._patterns_seen(cols))[0]:
                    if self.bond([u, v, *map(int, ex[i])]):
                        return size
        return None


def _chunks(it, k):
    buf = []
    for x in it:
        buf.append(x)
        if len(buf) == k:
            yield buf
            buf = []
    if buf:
        yield buf


def lens(nb, u, v, d, slack):
    du = steps(nb, u, cap=d + slack)
    dv = steps(nb, v, cap=d + slack)
    return sorted(w for w in du if w in dv and du[w] + dv[w] <= d + slack)
