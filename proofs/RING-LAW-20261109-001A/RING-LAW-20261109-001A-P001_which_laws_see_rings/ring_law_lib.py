"""Networks of rule-60 rings with any self-blind contact law (RING-LAW-20261109-001A).

A network is a dart permutation (REROUTE-20261109-001B's reroute_lib) laid out cell by cell by LOOP-NET-20261108-001A's loopnet_lib,
g cells per contact, every own cell reading its left neighbour and itself (rule 60). A contact's law is a pair (u, v) of 4-bit tables
(SEPARATE-20261108-001A's net_lib convention, entry (l << 1) | r): c <- u(l_a, r_a) xor v(l_b, r_b), where l and r are the contact's left
(arriving) and right (leaving) neighbours on the ring through dart 2c (u) and the ring through dart 2c + 1 (v). Reading conventions:
- c needs ring X at lag T when c(T), as a function of the first row, depends on X's own cells (net_lib's needs);
- c binds ring X at lag T (A32) when no assignment of the cells outside X's own cells makes c(T) constant in X's own cells, that is,
  when every minimally decisive set of c(T) meets X;
- a ring's plain first need is on time for a contact when the contact needs it at its light-cone lag, the fewest steps by which X's
  cells reach the contact through the cells' reads.
Affine laws give a linear automaton, where binding is needing and both are read exactly from row orbits. For any law, a pair of first
rows differing only in X's cells and differing at c(T) witnesses that c needs X at T; a SAT solver decides needing and binding exactly
on c's backward cone."""
import collections
import itertools
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "proofs/REROUTE-20261109-001B/REROUTE-20261109-001B-P001_rerouting_keeps_persistence"))
import reroute_lib as RR  # noqa: E402

LN = RR.P.LN
NL = LN.N
ONES = np.uint64(0xFFFFFFFFFFFFFFFF)


def anf(w):
    """ANF coefficients (constant, l, r, l r) of the 2-input table w"""
    t = [(w >> i) & 1 for i in range(4)]
    return t[0], t[0] ^ t[2], t[0] ^ t[1], t[0] ^ t[1] ^ t[2] ^ t[3]


def classify(law):
    ua, va = anf(law[0]), anf(law[1])
    nonlinear = bool(ua[3] or va[3])
    return {"affine": not nonlinear, "sees the routing": nonlinear or ua[1] != va[1],
            "both rings pass": bool(ua[1] or ua[3]) and bool(va[1] or va[3])}


class Net:
    def __init__(self, sig, g, law):
        cyc = RR.cycles(sig)
        ring_of = {d: i for i, r in enumerate(cyc) for d in r}
        rot = {i: [d >> 1 for d in r] for i, r in enumerate(cyc)}
        edges = [(ring_of[2 * e], ring_of[2 * e + 1]) for e in range(len(sig) // 2)]
        sizes, contacts = LN.network(rot, edges, g)
        self.law = law
        self.contacts = [(ra, pa, rb, pb, law) for (ra, pa, rb, pb, _) in contacts]
        self.rings, self.N, self.blocks = NL.layout(sizes, self.contacts)
        self.E = len(self.contacts)
        self.own = [(b, R[j - 1]) for R in self.rings for j, b in enumerate(R) if b >= self.E]
        ua, va = anf(law[0]), anf(law[1])
        self.con = []
        for c, (ra, pa, rb, pb, lw) in enumerate(self.contacts):
            A, B = self.rings[ra], self.rings[rb]
            self.con.append((c, ((A[pa - 1], A[(pa + 1) % len(A)], ua), (B[pb - 1], B[(pb + 1) % len(B)], va))))
        self.reads = collections.defaultdict(set)
        for b, l in self.own:
            self.reads[b] |= {b, l}
        for c, sides in self.con:
            for l, r, (u0, u1, u2, u3) in sides:
                if u1 or u3:
                    self.reads[c].add(l)
                if u2 or u3:
                    self.reads[c].add(r)

    def ring_cells(self, X):
        s, n = self.blocks[X]
        return list(range(s, s + n))

    def contact_rings(self, c):
        ra, pa, rb, pb, lw = self.contacts[c]
        return ra, rb

    # ---------- dynamics, 64 first rows per word
    def step(self, x):
        y = np.empty_like(x)
        for b, l in self.own:
            y[b] = x[l] ^ x[b]
        for c, sides in self.con:
            v = np.zeros_like(x[0])
            for l, r, (u0, u1, u2, u3) in sides:
                if u0:
                    v ^= ONES
                if u1:
                    v ^= x[l]
                if u2:
                    v ^= x[r]
                if u3:
                    v ^= x[l] & x[r]
            y[c] = v
        return y

    def light_cone(self, X):
        """the fewest steps by which X's own cells reach each cell through the reads"""
        rev = collections.defaultdict(set)
        for b, rs in self.reads.items():
            for a in rs:
                rev[a].add(b)
        reach, frontier, dist, T = set(self.ring_cells(X)), set(self.ring_cells(X)), {}, 0
        while frontier:
            T += 1
            nxt = {b for a in frontier for b in rev[a] if b not in reach}
            for b in nxt:
                dist[b] = T
            reach |= nxt
            frontier = nxt
        return dist

    def witnessed_needs(self, X, H, W, rng):
        """{contact: lags T <= H at which a sampled pair of first rows differing only in X's cells differs at the contact}"""
        cells = self.ring_cells(X)
        rand = lambda k: rng.integers(0, 2 ** 63, size=(k, W), dtype=np.uint64) ^ (rng.integers(0, 2, size=(k, W), dtype=np.uint64) << np.uint64(63))
        x = rand(self.N)
        y = x.copy()
        y[cells] = rand(len(cells))
        out = collections.defaultdict(set)
        for T in range(1, H + 1):
            x, y = self.step(x), self.step(y)
            d = (x[:self.E] ^ y[:self.E]).any(axis=1)
            for c in np.nonzero(d)[0]:
                out[int(c)].add(T)
        return out

    # ---------- the linear automaton of an affine law (constants dropped: they do not change any dependence)
    def linear_rows(self):
        assert classify(self.law)["affine"]
        rows = [0] * self.N
        for b, l in self.own:
            rows[b] = (1 << l) | (1 << b)
        for c, sides in self.con:
            v = 0
            for l, r, (u0, u1, u2, u3) in sides:
                if u1:
                    v ^= 1 << l
                if u2:
                    v ^= 1 << r
            rows[c] = v
        return rows

    def affine_persistence(self, c, cap=10 ** 6):
        """exact for an affine law: whether c needs (so binds) both its rings at every lag; None if the row orbit exceeds cap"""
        o = NL.orbit(self.linear_rows(), 1 << c, cap)
        if o is None:
            return None
        seq, T1, p = o
        ra, rb = self.contact_rings(c)
        ma, mb = NL.mask(self.blocks, ra), NL.mask(self.blocks, rb)
        return all(r & ma and r & mb for r in seq)


# ---------- exact decisions on a contact's backward cone (CNF by Tseitin)
class Enc:
    def __init__(self):
        self.n, self.cl = 0, []

    def var(self):
        self.n += 1
        return self.n

    def AND(self, a, b):
        z = self.var()
        self.cl += [[-z, a], [-z, b], [z, -a, -b]]
        return z

    def XOR(self, a, b):
        z = self.var()
        self.cl += [[-z, a, b], [-z, -a, -b], [z, -a, b], [z, a, -b]]
        return z

    def const(self, val):
        z = self.var()
        self.cl.append([z] if val else [-z])
        return z


def cone_value(net, enc, c, T, init):
    """the CNF variable of c's value at lag T, with init(cell) the variable of a first-row cell"""
    gate = {b: ("own", l) for b, l in net.own}
    for cc, sides in net.con:
        gate[cc] = ("con", sides)
    memo = {}
    order = []
    # iterative post-order over (cell, t)
    stack = [(c, T, False)]
    while stack:
        cell, t, done = stack.pop()
        if t == 0 or (cell, t) in memo:
            continue
        g = gate[cell]
        deps = [(g[1], t - 1), (cell, t - 1)] if g[0] == "own" else [(x, t - 1) for l, r, a in g[1] for x in (l, r)]
        if not done:
            stack.append((cell, t, True))
            for d in deps:
                if d[1] > 0 and d not in memo:
                    stack.append((d[0], d[1], False))
            continue
        val = lambda k: init(k[0]) if k[1] == 0 else memo[k]
        if g[0] == "own":
            z = enc.XOR(val((g[1], t - 1)), val((cell, t - 1)))
        else:
            terms, cst = [], 0
            for l, r, (u0, u1, u2, u3) in g[1]:
                cst ^= u0
                if u1:
                    terms.append(val((l, t - 1)))
                if u2:
                    terms.append(val((r, t - 1)))
                if u3:
                    terms.append(enc.AND(val((l, t - 1)), val((r, t - 1))))
            if not terms:
                z = enc.const(cst)
            else:
                z = terms[0]
                for x in terms[1:]:
                    z = enc.XOR(z, x)
                if cst:
                    z = enc.XOR(z, enc.const(1))
        memo[(cell, t)] = z
    return init(c) if T == 0 else memo[(c, T)]


def solve(clauses):
    from pysat.solvers import Cadical153
    with Cadical153(bootstrap_with=clauses) as s:
        return s.solve()


def needs_exactly(net, c, X, T):
    """does c(T) depend on X's own cells? (two copies sharing every other first-row cell)"""
    enc = Enc()
    Xc = set(net.ring_cells(X))
    shared, a, b = {}, {}, {}

    def init(own):
        def f(cell):
            d = own if cell in Xc else shared
            if cell not in d:
                d[cell] = enc.var()
            return d[cell]
        return f
    za, zb = cone_value(net, enc, c, T, init(a)), cone_value(net, enc, c, T, init(b))
    enc.cl.append([enc.XOR(za, zb)])
    return solve(enc.cl)


def binds_exactly(net, c, X, T):
    """A32 at lag T: True when no assignment of the other cells makes c(T) constant over X's own cells"""
    enc = Enc()
    Xc = net.ring_cells(X)
    shared = {}
    t1, t0 = enc.const(1), enc.const(0)
    outs = []
    for bits in itertools.product((0, 1), repeat=len(Xc)):
        fixed = {cell: (t1 if bit else t0) for cell, bit in zip(Xc, bits)}

        def f(cell, fixed=fixed):
            if cell in fixed:
                return fixed[cell]
            if cell not in shared:
                shared[cell] = enc.var()
            return shared[cell]
        outs.append(cone_value(net, enc, c, T, f))
    for z in outs[1:]:
        enc.cl.append([-enc.XOR(outs[0], z)])
    return not solve(enc.cl)
