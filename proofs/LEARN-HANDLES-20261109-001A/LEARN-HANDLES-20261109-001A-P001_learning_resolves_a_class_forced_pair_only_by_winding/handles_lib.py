"""Learning in handles, for LEARN-HANDLES-20261109-001A.

Knot spaces on lattice tori as in COUNT-SURFACES-20261107-001A (surface_lib): points are the up triangles, lines the down triangles and
faces the vertices of T. A signing puts a bit on every side; side k of line i is B-edge 3i + k, and its ends are the faces of the line's
corners k + 1 and k + 2. Under a signing s and a state x a line agrees at one corner (satisfied) or at three (violated); deg(v) counts the
corners agreeing at face v, the even faces D are those where deg is even, and E is the sum of floor(deg / 2).

A class-forced law is a Kasteleyn signing (no even face) in a sign class that no state satisfies. A least state of it has one violated
line l0 and one face w0 of deg 3. The learner holds x fixed and re-signs one side at a time, on a violated line or with an end at an even
face (A26); re-signing side k of line i toggles the agreement of the line's corners k + 1 and k + 2. After the split at l0 every line
agrees at one face f(i). A hole (deg 0) at v moves along a line i at v to f(i), by re-signing the side between them (then f(i) = v), and
a hole that enters a face of deg >= 2 is absorbed there. The dissonance is resolved when every deg is 1: a perfect matching of the lines
with the faces, and then no line is violated, no face over-agrees and no face is even."""
import random
import sys
from collections import deque
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "proofs/COUNT-SURFACES-20261107-001A/COUNT-SURFACES-20261107-001A-P001_the_count_reads_the_euler_characteristic"))
import surface_lib as SL  # noqa: E402

LABELS = [(0, 0), (0, 1), (1, 0), (1, 1)]


def class_forced_tori(max_points=40):
    """the two Fano tori and every thin torus of even index up to max_points, as (p, q, r)"""
    out = list(SL.FANO_TORI)
    for N in range(2, max_points + 1, 2):
        out += [t for t in SL.hnf_sublattices(N) if SL.torus_kind(*t) == "thin"]
    return out


class Torus:
    def __init__(self, p, q, r):
        S = SL.torus(p, q, r)
        K = SL.KnotSpace(S)
        assert K.simple() and K.chi == 0 and all(d == 3 for d in K.d)
        self.S, self.K, self.n, self.V, self.params = S, K, K.n, K.V, (p, q, r)
        self.name = "torus(%d,%d,%d)" % (p, q, r)
        self.fv = [[S.vert[K.lines[i]][c] for c in range(3)] for i in range(self.n)]
        assert all(len(set(f)) == 3 for f in self.fv)
        self.lines_at = [[] for _ in range(self.V)]
        for i in range(self.n):
            for c in range(3):
                self.lines_at[self.fv[i][c]].append(i)
        self.adj = [set() for _ in range(self.V)]
        for t in range(S.nt):
            a, b, c = S.vert[t]
            for u, w in ((a, b), (b, c), (a, c)):
                self.adj[u].add(w)
                self.adj[w].add(u)
        self.classes = SL.labelled_classes(K)
        self.sat = SL.satisfiable_classes(p, q, r)
        self.forced = [lab for lab in LABELS if lab not in self.sat]
        # each side's contribution to the holonomy along the two loops of SL.loops: the class of a flat sign change is its sum
        idx = SL.edge_index(K)
        self.contrib = [[0, 0] for _ in range(3 * self.n)]
        for j, (di, dj) in enumerate(SL.loops(S)):
            for P, k in SL.staircase(0, 0, di, dj):
                b, c = P[(k + 1) % 3], P[(k + 2) % 3]
                self.contrib[idx[S.canon(((b[0] + c[0]) // 2, (b[1] + c[1]) // 2))[0]]][j] ^= 1
        for lab, s in self.classes.items():
            assert self.label(s) == lab
        self._dist = {}

    # ------------------------------------------------------------------------------------------------ signs, states, tallies
    def label(self, s):
        return tuple(sum(s[e] & self.contrib[e][j] for e in range(3 * self.n)) % 2 for j in (0, 1))

    def ends(self, i, k):
        return self.fv[i][(k + 1) % 3], self.fv[i][(k + 2) % 3]

    def side(self, i, u, w):
        cs = [c for c in range(3) if self.fv[i][c] in (u, w)]
        assert len(cs) == 2
        return 3 - cs[0] - cs[1]

    def agree(self, s, x):
        out = []
        for i in range(self.n):
            L = [x[self.K.pt[i][k]] ^ s[3 * i + k] for k in range(3)]
            out.append([c for c in range(3) if L[(c + 1) % 3] == L[(c + 2) % 3]])
        return out

    def tally(self, s, x):
        """(violated lines, deg per face, even faces, E)"""
        A = self.agree(s, x)
        viol = [i for i in range(self.n) if len(A[i]) == 3]
        deg = [0] * self.V
        for i in range(self.n):
            for c in A[i]:
                deg[self.fv[i][c]] += 1
        D = [v for v in range(self.V) if deg[v] % 2 == 0]
        assert D == self.K.even_faces(s)
        return viol, deg, D, sum(d // 2 for d in deg)

    def dist(self, t):
        if t not in self._dist:
            d, dq = {t: 0}, deque([t])
            while dq:
                u = dq.popleft()
                for w in self.adj[u]:
                    if w not in d:
                        d[w] = d[u] + 1
                        dq.append(w)
            self._dist[t] = d
        return self._dist[t]

    def systole(self, delta):
        """the fewest sides of a closed walk of T whose class (holonomy) is delta"""
        if delta == (0, 0):
            return 0
        step = {}
        for i in range(self.n):
            for k in range(3):
                u, w = self.ends(i, k)
                cb = tuple(self.contrib[3 * i + k])
                step.setdefault(u, []).append((w, cb))
                step.setdefault(w, []).append((u, cb))
        best = None
        for a in range(self.V):
            d, dq = {(a, (0, 0)): 0}, deque([(a, (0, 0))])
            while dq:
                v, h = dq.popleft()
                if (v, h) == (a, delta):
                    break
                for w, cb in step[v]:
                    st = (w, (h[0] ^ cb[0], h[1] ^ cb[1]))
                    if st not in d:
                        d[st] = d[(v, h)] + 1
                        dq.append(st)
            if (a, delta) in d and (best is None or d[(a, delta)] < best):
                best = d[(a, delta)]
        return best

    # ------------------------------------------------------------------------------------------------ least states
    def violation_counts(self, s):
        n = self.n
        assert n <= 22
        X = np.arange(1 << n, dtype=np.int64)
        viol = np.zeros(1 << n, dtype=np.int8)
        for i in range(n):
            ys = [((X >> self.K.pt[i][k]) & 1) ^ s[3 * i + k] for k in range(3)]
            viol += ((ys[0] == ys[1]) & (ys[1] == ys[2])).astype(np.int8)
        return viol

    def least_states_brute(self, s):
        viol = self.violation_counts(s)
        m = int(viol.min())
        idx = np.flatnonzero(viol == m)
        return m, [[(int(a) >> p) & 1 for p in range(self.n)] for a in idx]

    def least_states_sat(self, s, rng, cap, tries=None):
        """states violating exactly one line, found by SAT with the line forced monochromatic and random phases"""
        from pysat.solvers import Solver
        cl = self.K.clauses(s)
        found, tries = {}, tries or 20 * cap
        for t in range(tries):
            l0 = t % self.n
            lits = [(self.K.pt[l0][k] + 1) * (1 if s[3 * l0 + k] == 0 else -1) for k in range(3)]
            hard = [c for j, c in enumerate(cl) if j // 2 != l0]
            hard += [[lits[0], -lits[1]], [-lits[0], lits[1]], [lits[1], -lits[2]], [-lits[1], lits[2]]]
            with Solver(name="cadical153", bootstrap_with=hard) as so:
                so.set_phases([v if rng.random() < 0.5 else -v for v in range(1, self.n + 1)])
                if not so.solve():
                    continue
                mdl = so.get_model()
            x = [int(mdl[p] > 0) for p in range(self.n)]
            found[tuple(x)] = x
            if len(found) >= cap:
                break
        return list(found.values())

    # ------------------------------------------------------------------------------------------------ the split and the matching
    def split(self, s, x, k):
        """re-sign side k of the violated line: returns (signing, f, deg, l0, w0)"""
        viol, deg, D, E = self.tally(s, x)
        assert len(viol) == 1 and E == 1 and D == []
        l0 = viol[0]
        w0 = deg.index(3)
        s2 = list(s)
        s2[3 * l0 + k] ^= 1
        A = self.agree(s2, x)
        assert all(len(a) == 1 for a in A)
        f = [self.fv[i][A[i][0]] for i in range(self.n)]
        deg2 = [0] * self.V
        for v in f:
            deg2[v] += 1
        return s2, f, deg2, l0, w0

    def cheapest_matching(self, f, lab):
        """a perfect matching M in class lab (accepted by the class-lab signing) moving the fewest lines off f: MaxSAT over states y of that
        signing, one soft clause per line asking it to agree at f(i)"""
        from pysat.examples.rc2 import RC2
        from pysat.formula import WCNF
        s = self.classes[lab]
        w = WCNF()
        for c in self.K.clauses(s):
            w.append(c)
        nv = self.n
        for i in range(self.n):
            c = self.fv[i].index(f[i])
            a, b = [(self.K.pt[i][k] + 1) * (1 if s[3 * i + k] == 0 else -1) for k in ((c + 1) % 3, (c + 2) % 3)]
            nv += 1
            w.append([nv, a, -b])
            w.append([nv, -a, b])
            w.append([-nv], weight=1)
        with RC2(w) as rc:
            mdl = rc.compute()
            if mdl is None:
                return None, None
            cost = rc.cost
        y = [int(mdl[p] > 0) for p in range(self.n)]
        A = self.agree(s, y)
        assert all(len(a) == 1 for a in A)
        return [self.fv[i][A[i][0]] for i in range(self.n)], cost

    def realize(self, f, deg, M):
        """move the holes from f to M: every line with f(i) != M(i) is re-signed once, when one end of its side is even. Returns
        (moves [(line, side)], lines left over); left-over lines form alternating cycles that no hole reaches"""
        f, deg = list(f), list(deg)
        pend = {i for i in range(self.n) if f[i] != M[i]}
        moves, progress = [], True
        while pend and progress:
            progress = False
            for i in sorted(pend):
                a, b = M[i], f[i]
                if deg[a] % 2 == 0 or deg[b] % 2 == 0:
                    moves.append((i, self.side(i, a, b)))
                    deg[a] += 1
                    deg[b] -= 1
                    f[i] = a
                    pend.discard(i)
                    progress = True
                    break
        return moves, sorted(pend)

    def replay(self, s, x, moves):
        """apply the re-signings to s with x fixed; every one must be at a dissonance. Returns the final signing and the per-step check"""
        s, ok = list(s), True
        for (i, k) in moves:
            viol, _, D, _ = self.tally(s, x)
            u, w = self.ends(i, k)
            ok &= (i in viol) or (u in D) or (w in D)
            s[3 * i + k] ^= 1
        return s, ok

    # ------------------------------------------------------------------------------------------------ local rules
    def run_rule(self, f, deg, w0, rule, rng, budget):
        """move the holes one after another (nearer to w0 first) until each is absorbed; returns (resolved, steps, moves)"""
        f, deg = list(f), list(deg)
        dt = self.dist(w0)
        holes = sorted([v for v in range(self.V) if deg[v] == 0], key=lambda v: dt[v])
        moves, steps = [], 0
        for h in holes:
            last = None
            while deg[h] == 0:
                if steps >= budget:
                    return False, steps, moves
                cand = [(i, f[i]) for i in self.lines_at[h]]
                if rule == "no_reversal":
                    cand = [c for c in cand if c[1] != last] or cand
                    best = min(dt[w] for _, w in cand)
                    i, w = rng.choice([c for c in cand if dt[c[1]] == best])
                else:
                    i, w = rng.choice(cand)
                moves.append((i, self.side(i, h, w)))
                deg[h] += 1
                deg[w] -= 1
                f[i] = h
                steps += 1
                last, h = h, w
                if deg[h] != 0:
                    break
        return all(d == 1 for d in deg), steps, moves
