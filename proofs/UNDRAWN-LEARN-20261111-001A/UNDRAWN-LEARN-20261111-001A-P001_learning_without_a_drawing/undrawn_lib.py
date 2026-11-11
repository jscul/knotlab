"""Learning without a drawing (research/UNDRAWN-LEARN-20261111-001/preregistration.md).

The dissonance is felt at knots alone: W = 2 x (violated knots), floor 0, so the floor states are the states satisfying every knot under
any law, and a sign may change only at a violated knot. No face of any drawing is read. The credit learner's cooling, which asked
whether a face's neighbourhood ever cleared of dissonance, reads distinctions instead: a distinction is dissonant when it lies in a
violated knot, its neighbourhood is itself and the distinctions it shares a knot with, and a knot is cooled when its three distinctions
stay pinned. The engine below carries that in the shape the credit learner reads (its "faces" are distinctions); the learner, its probe,
budgets and harness are SHARED-COUNT-20261111-001's, unchanged."""
import itertools
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "proofs/SHARED-COUNT-20261111-001A/SHARED-COUNT-20261111-001A-P001_counting_through_a_shared_distinction"))
import join_lib as J  # noqa: E402

F = J.F
PL = F._parity_lib()
W, C, I = PL.W, PL.C, PL.I


class KnotEngine(W.Engine):
    """W = 2 x violated knots. Units of dissonance for the credit rule: ag[p] = 1 + 2 x (violated knots through distinction p), odd, and
    at least 3 exactly when p lies in a violated knot; face[i] = knot i's three distinctions."""

    def __init__(self, K, S, s, x):
        self.n = K.n
        self.V = K.n
        self.pt = [list(K.pt[i]) for i in range(K.n)]
        self.face = [list(self.pt[i]) for i in range(K.n)]
        self.sites_of_point = [[(i, k) for i in range(K.n) for k in range(3) if self.pt[i][k] == p] for p in range(K.n)]
        self.s, self.x = list(s), list(x)
        self.L = [[self.x[self.pt[i][k]] ^ self.s[3 * i + k] for k in range(3)] for i in range(K.n)]
        self.viol = [self.L[i][0] == self.L[i][1] == self.L[i][2] for i in range(K.n)]
        self.ag = [1] * self.V
        for i in range(K.n):
            if self.viol[i]:
                for p in self.pt[i]:
                    self.ag[p] += 2
        self.W = 2 * sum(self.viol)

    def delta(self, sites):
        by_line = {}
        for (i, k) in sites:
            by_line.setdefault(i, []).append(k)
        d, dag, nv = 0, {}, {}
        for i, ks in by_line.items():
            new = list(self.L[i])
            for k in ks:
                new[k] ^= 1
            nv[i] = new[0] == new[1] == new[2]
            ch = nv[i] - self.viol[i]
            d += 2 * ch
            if ch:
                for p in self.pt[i]:
                    dag[p] = dag.get(p, 0) + 2 * ch
        return d, nv, dag

    def learn_sites(self):
        """a sign changes only where dissonance shows: at a violated knot"""
        return [(i, k) for i in range(self.n) if self.viol[i] for k in range(3)]

    def region_dissonant(self, faces, lines):
        return any(self.viol[i] for i in lines)


def run(sp, targets, seed, budget=8_000_000):
    """PARITY-FIVE-20261111-001's run, step for step, with KnotEngine in place of the drawn engine and floor 0"""
    I.probe = F.sturdy_probe_k
    params = dict(C.PARAMS, budget=budget)
    rng = random.Random(seed)
    s, x = sp.start()
    E = KnotEngine(sp.K, sp.S, s, x)
    W.m1(E, 0, rng)
    rows = []
    for tg in targets:
        steps, probes, r, stalls, credit = C.learn(E, sp.K, sp.ports, tg, 0, rng, params)
        m = F.read_map_k(sp.K, E.s, sp.ports)
        row = {"target": tg, "stopped": steps is not None, "steps": steps, "probes": probes, "radius": r, "map at the stop": m}
        if steps is None:
            row["outcome"] = "not stopped"
        else:
            E.flip(rng.choice(sp.movable))
            w = W.m1(E, 0, rng)
            after = F.read_map_k(sp.K, E.s, sp.ports) if w == 0 else None
            row["map after the disturbance"] = after
            row["outcome"] = "inexact stop" if m != tg else "learned, held" if after == tg else "learned, not held"
        rows.append(row)
    return rows


# ---------------------------------------------------------------- laws modulo gauge, and a base with no drawing

def law_transversal(K):
    """one signing from each law: signings modulo flipping a distinction (its literals in every knot) and complementing a knot (its three
    literals). Returns the free coordinates; every law is one signing supported on them."""
    m = K.nl if hasattr(K, "nl") else K.n
    gens = []
    real = K.real if hasattr(K, "real") else K.n
    for p in range(real):
        g = 0
        for i in range(m):
            for k in range(3):
                if K.pt[i][k] == p:
                    g |= 1 << (3 * i + k)
        if g:
            gens.append(g)
    gens += [0b111 << (3 * i) for i in range(m)]
    piv = F.echelon(gens)
    return [c for c in range(3 * m) if c not in piv], m


def laws(K):
    free, m = law_transversal(K)
    for bits in itertools.product((0, 1), repeat=len(free)):
        s = [0] * (3 * m)
        for c, b in zip(free, bits):
            s[c] = b
        yield s


def count_laws(K, ports, nreal):
    """over every law: how many have the count of len(ports) - 1 held distinctions at the interface (exact, by brute force over states)"""
    import numpy as np
    X = ((np.arange(1 << nreal)[:, None] >> np.arange(nreal)[None, :]) & 1).astype(np.uint8)
    m = len(K.pt)
    P = np.array(K.pt)
    T = list(ports)
    want = 2 ** (len(T) - 1)
    hits = total = 0
    for s in laws(K):
        S = np.array(s, dtype=np.uint8).reshape(m, 3)
        Lt = X[:, P] ^ S[None, :, :]
        ok = ~((Lt[:, :, 0] == Lt[:, :, 1]) & (Lt[:, :, 1] == Lt[:, :, 2])).any(axis=1)
        total += 1
        st = X[ok]
        if len(st) == 0:
            continue
        par = st[:, T].sum(axis=1) % 2
        if (par == par[0]).all() and len({tuple(r) for r in st[:, T[:-1]]}) == want:
            hits += 1
    return hits, total


class Undrawn:
    """a random knot pattern given with no drawing: 9 distinctions, 10 knots of three distinct distinctions, connected, no knot repeated;
    padded with one inert distinction so the engine's single count serves both"""

    def __init__(self, seed, n=9, m=10):
        rng = random.Random(seed)
        while True:
            pt = []
            while len(pt) < m:
                t = sorted(rng.sample(range(n), 3))
                if t not in pt:
                    pt.append(t)
            if len({p for t in pt for p in t}) == n and _connected(pt, n):
                break
        self.seed, self.real, self.nl, self.n = seed, n, m, m
        self.pt = pt
        self.degrees = [sum(p in t for t in pt) for p in range(n)]

    def clauses(self, s):
        cl = []
        for i in range(self.nl):
            lits = [(self.pt[i][k] + 1) * (1 if s[3 * i + k] == 0 else -1) for k in range(3)]
            cl.append(lits)
            cl.append([-x for x in lits])
        return cl


def _connected(pt, n):
    seen, todo = {0}, [0]
    while todo:
        p = todo.pop()
        for t in pt:
            if p in t:
                for q in t:
                    if q not in seen:
                        seen.add(q)
                        todo.append(q)
    return len(seen) == n


def find_undrawn(max_seed=200, n=9, m=10):
    """the first seed whose pattern has a law that counts three held distinctions at some interface while its plain law (every sign 0)
    is satisfiable and does not; returns the base, the interface (first counting set in sorted order, three held, the last read) and the
    number of laws that count there"""
    import numpy as np
    for seed in range(max_seed):
        B = Undrawn(seed, n, m)
        X = ((np.arange(1 << B.real)[:, None] >> np.arange(B.real)[None, :]) & 1).astype(np.uint8)
        P = np.array(B.pt)

        def allowed(s):
            S = np.array(s, dtype=np.uint8).reshape(B.nl, 3)
            Lt = X[:, P] ^ S[None, :, :]
            return X[~((Lt[:, :, 0] == Lt[:, :, 1]) & (Lt[:, :, 1] == Lt[:, :, 2])).any(axis=1)]

        plain = allowed([0] * (3 * B.nl))
        if len(plain) == 0:
            continue
        sets = set()
        for s in laws(B):
            st = allowed(s)
            if len(st) == 0:
                continue
            for T in itertools.combinations(range(B.real), 4):
                par = st[:, list(T)].sum(axis=1) % 2
                if (par == par[0]).all() and len({tuple(r) for r in st[:, list(T[:3])]}) == 8:
                    sets.add(T)
        if not sets:
            continue
        T = min(sets)
        ps = plain[:, list(T)].sum(axis=1) % 2
        if (ps == ps[0]).all() and len({tuple(r) for r in plain[:, list(T[:3])]}) == 8:
            continue
        return B, list(T), sorted(sets)
    return None


class UndrawnSpace:
    """the harness's space for the undrawn base: start at the plain law (every sign 0) at the solver's first satisfying state"""

    def __init__(self, B, ports):
        self.J = B
        self.K, self.S = B, None
        self.floor2 = 0
        self.ports = list(ports)
        self.movable = [p for p in range(B.real) if p not in self.ports]

    def start(self):
        s = [0] * (3 * self.J.nl)
        from pysat.solvers import Solver
        with Solver(name="cadical153", bootstrap_with=self.J.clauses(s)) as so:
            assert so.solve()
            m = so.get_model()
        return s, [int(m[p] > 0) if p < len(m) else 0 for p in range(self.J.n)]


SEARCH_ORDER = [(6, 7), (6, 8), (7, 8), (7, 9), (8, 9), (8, 10)]


def chosen_undrawn():
    """the frozen rule: the first (distinctions, knots) in SEARCH_ORDER, and in it the first seed below 100, with a counting base"""
    for n, m in SEARCH_ORDER:
        r = find_undrawn(100, n, m)
        if r:
            return r
    return None


def space(name):
    if name == "J1":
        return J.Space(1)
    if name == "J2":
        return J.Space(2)
    B, T, _ = chosen_undrawn()
    return UndrawnSpace(B, T)
