"""Referee R1 (DIRECT-REACH-20261115-001): an independent pattern builder and SAT oracle.

Written from the textual definitions (LEVEL-REACH-20261114-001 setting), not from the study's code:
- addresses of level n are the integers 0 .. 2^n - 1, first letter in the most significant bit; the heap id of address y at
  level n is y + 2^n - 1, and the child y.e is 2y + e at level n + 1;
- a state q reads the first letter a, outputs a ^ sw[q], and continues with d_a[q] on the rest;
- a word is a tuple of states acting right to left (the rightmost state reads first); the word list is
  [()] + [(q,)] + [(q, r)] in lexicographic order; a placement term t is word t // 3 with child slot t % 3 (0: none, 1: e = 0,
  2: e = 1);
- P_N holds, for every level n <= N and every placement, the NAE knot on its three members when they are distinct; a placement
  with a child member is skipped at n = N.
Nothing here imports the study's code.
"""
import gzip
import json
import random
from pathlib import Path

import numpy as np
from pysat.solvers import Cadical195

ROOT = Path('/home/jscul/p-vs-np-contact-first')
HERE = ROOT / 'research/DIRECT-REACH-20261115-001/referee-R1'
STUDY = ROOT / 'research/DIRECT-REACH-20261115-001'
CENSUS = ROOT / 'artifacts/LEVEL-REACH-20261114-001A/LEVEL-REACH-20261114-001A-E001_level_reach/records_slim.jsonl.gz'
PROFILES = {'constant-2': [2, 2, 2, 2], 'constant-3': [3, 3, 3, 3], 'half-rate': [3, 3, 4, 4]}


def load_population():
    """Population D read directly from the census records: alive, profile constant 2, constant 3 or [3, 3, 4, 4]."""
    out = []
    with gzip.open(CENSUS, 'rt') as f:
        for line in f:
            r = json.loads(line)
            prof = [lv['L_N'] for lv in r['levels']]
            if r['union'] != 'alive':
                continue
            for name, p in PROFILES.items():
                if prof == p:
                    out.append(dict(case=r['case'], key=r['key'], profile=name))
    out.sort(key=lambda d: d['case'])
    return out


def word_list(s):
    return [()] + [(q,) for q in range(s)] + [(q, r) for q in range(s) for r in range(s)]


class Aut:
    def __init__(self, key):
        s, sw, d0, d1, placements = key
        self.s = s
        self.sw = np.array(sw, dtype=np.int64)
        self.d = np.array([d0, d1], dtype=np.int64)
        self.W = word_list(s)
        self.placements = sorted({tuple(sorted(int(t) for t in p)) for p in placements})
        self.used = sorted({t // 3 for p in self.placements for t in p})

    def act_state(self, q, X, n):
        st = np.full(len(X), q, dtype=np.int64)
        res = np.zeros_like(X)
        for pos in range(n - 1, -1, -1):
            a = (X >> pos) & 1
            res |= (a ^ self.sw[st]) << pos
            st = self.d[a, st]
        return res

    def act(self, word, n, X=None):
        """Images of the level-n addresses X (default: all) under a word (tuple of states, rightmost first)."""
        if X is None:
            X = np.arange(1 << n, dtype=np.int64)
        out = np.asarray(X, dtype=np.int64).copy()
        for q in reversed(word):
            out = self.act_state(q, out, n)
        return out

    def act_bits(self, word, bits):
        """The same on one address given as a bit tuple (first letter first), returning a bit tuple (scalar code path)."""
        bits = list(bits)
        for q in reversed(word):
            st, out = q, []
            for a in bits:
                out.append(a ^ int(self.sw[st]))
                st = int(self.d[a, st])
            bits = out
        return tuple(bits)

    def level_knots(self, n, N):
        """Knots placed at level n of P_N, as sorted heap-id triples (members distinct)."""
        img = {}
        rows = []
        for p in self.placements:
            mem = []
            for t in p:
                wi, e = divmod(t, 3)
                if e and n == N:
                    mem = None
                    break
                if wi not in img:
                    img[wi] = self.act(self.W[wi], n)
                y = img[wi]
                mem.append(y + (1 << n) - 1 if e == 0 else 2 * y + (e - 1) + (1 << (n + 1)) - 1)
            if mem is None:
                continue
            M = np.sort(np.stack(mem, axis=1), axis=1)
            keep = (M[:, 0] != M[:, 1]) & (M[:, 1] != M[:, 2])
            rows.append(M[keep])
        if not rows:
            return np.empty((0, 3), dtype=np.int64)
        return np.unique(np.concatenate(rows), axis=0)

    def knots(self, N):
        parts = [self.level_knots(n, N) for n in range(N + 1)]
        K = np.concatenate(parts) if parts else np.empty((0, 3), dtype=np.int64)
        return np.unique(K, axis=0) if len(K) else K

    def orbits(self, n):
        """Orbits of level n under the used words (union-find on explicit images); list of sorted address arrays."""
        par = np.arange(1 << n)

        def find(x):
            r = x
            while par[r] != r:
                r = par[r]
            while par[x] != r:
                par[x], x = r, par[x]
            return r
        for wi in self.used:
            y = self.act(self.W[wi], n)
            for x in range(1 << n):
                a, b = find(x), find(int(y[x]))
                if a != b:
                    par[max(a, b)] = min(a, b)
        groups = {}
        for x in range(1 << n):
            groups.setdefault(find(x), []).append(x)
        return [np.array(g, dtype=np.int64) for g in sorted(groups.values())]


def hid(y, n):
    return int(y) + (1 << n) - 1


def nae_ok(vals, K):
    """vals: (S, nv) or (nv,) 0/1 array; True per row when every knot is not-all-equal."""
    v = np.atleast_2d(vals)
    s = v[:, K[:, 0]].astype(np.int8) + v[:, K[:, 1]] + v[:, K[:, 2]]
    return np.all((s != 0) & (s != 3), axis=1)


class Oracle:
    """CaDiCaL on the NAE clauses of P_N. Every model returned is checked against every knot."""

    def __init__(self, key, N, seed=0):
        self.A = Aut(key)
        self.N = N
        self.nv = (1 << (N + 1)) - 1
        self.K = self.A.knots(N)
        cls = []
        for a, b, c in self.K.tolist():
            cls.append([a + 1, b + 1, c + 1])
            cls.append([-a - 1, -b - 1, -c - 1])
        self.S = Cadical195(bootstrap_with=cls)
        self.rng = random.Random(seed)
        self.calls = 0
        self.found = []          # models found by solve(), for callers that grow their sample

    def close(self):
        self.S.delete()

    def solve(self, assumptions=()):
        self.calls += 1
        if not self.S.solve(assumptions=list(assumptions)):
            return None
        m = np.array(self.S.get_model()[: self.nv]) > 0
        if len(m) < self.nv:  # variables not in any clause
            m = np.concatenate([m, np.zeros(self.nv - len(m), dtype=bool)])
        assert nae_ok(m, self.K)[0], 'model violates a knot'
        for lit in assumptions:
            assert m[abs(lit) - 1] == (lit > 0)
        self.found.append(m)
        return m

    def alive(self):
        return self.solve() is not None

    def samples(self, count):
        """Diverse models: each from a fresh CaDiCaL on a random relabelling of the variables with random phases (a persistent
        solver with new phases returned near-identical models). Every model is checked against every knot; complements added."""
        out = []
        base = self.K.tolist()
        for _ in range(count):
            perm = list(range(self.nv))
            self.rng.shuffle(perm)
            cls = []
            for a, b, c in base:
                x, y, z = perm[a] + 1, perm[b] + 1, perm[c] + 1
                cls.append([x, y, z])
                cls.append([-x, -y, -z])
            with Cadical195(bootstrap_with=cls) as S:
                S.set_phases([v + 1 if self.rng.getrandbits(1) else -v - 1 for v in range(self.nv)])
                if not S.solve():
                    return None
                m = np.array(S.get_model()[: self.nv]) > 0
            if len(m) < self.nv:
                m = np.concatenate([m, np.zeros(self.nv - len(m), dtype=bool)])
            m = m[perm]
            assert nae_ok(m, self.K)[0], 'sample violates a knot'
            out.append(m)
        X = np.array(out, dtype=bool)
        return np.concatenate([X, ~X])          # complement closure (NAE)

    def tie_partners(self, u, cand, X):
        """Exact: the variables v in cand with u XOR v constant over all states, with the constant. X: models (rows)."""
        Xn = X ^ X[:, [u]]                       # normalise so that u = 0
        cand = np.asarray(cand)
        col = Xn[:, cand]
        live = cand[np.all(col == col[0], axis=0)]
        val = {int(v): bool(Xn[0, v]) for v in live}
        confirmed = {}
        pending = set(val)
        while pending:
            v = pending.pop()
            lit = -(v + 1) if val[v] else (v + 1)          # v != its constant value, with u = 0
            m = self.solve([-(u + 1), lit])
            if m is None:
                confirmed[v] = int(val[v])
                continue
            mn = m ^ m[u]
            for w in list(pending):
                if bool(mn[w]) != val[w]:
                    pending.discard(w)
        return confirmed

    def patterns(self, vars_, X):
        """Exact set of patterns of the projection onto vars_ (bit i = vars_[i]): from models X, then SAT for the rest."""
        vars_ = list(vars_)
        w = 1 << np.arange(len(vars_))
        seen = set(np.unique((X[:, vars_].astype(np.int64) * w).sum(axis=1)).tolist())
        for p in range(1 << len(vars_)):
            if p in seen:
                continue
            m = self.solve([(v + 1) if (p >> i) & 1 else -(v + 1) for i, v in enumerate(vars_)])
            if m is not None:
                seen.add(p)
        return seen
