"""boxes.py: clauses on agreements of agreements (one layer up) on a stage.  UPPER-GROWN-20261127-001; README.md.

A **box** is six agreement readings A0, A1, B0, B1, C0, C1 on pairwise disjoint carriers (two or three distinctions)
such that each of the eight triples (Ai, Bj, Ck) is a bond of the stage (RING-BOND's definition: no knot reads a
reading, every two take all four pairs, the three miss a triple) missing exactly one triple, and that missing triple is
(a_i, b_j, c_k) for values a_0, a_1, b_0, b_1, c_0, c_1 fixed per reading.  Then the upper readings
U_A = [A0 + A1 = a_0 + a_1 + 1] (and likewise U_B, U_C) cannot all hold: if they did, some (Ai, Bj, Ck) would take its
missing triple (the referee's argument).  For each box the stage's own image of (U_A, U_B, U_C) is read by a solver, with
which knots' laws are needed for the missing upper word (each law removed in turn)."""
import sys, json, itertools, collections
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'research' / 'RING-BOND-20261127-001'))
import ringbond as RB
from pysat.solvers import Minisat22


def find_boxes(bonds, limit=None):
    """bonds: ringbond.bonds(...)['bonds'] (or local ones), each with 'readings' and 'missing'.  Returns the boxes."""
    rid = {}; T = collections.defaultdict(set)              # (reading a, value a, reading b, value b) -> {(c, value c)}
    def key(r): return (tuple(r[0]), r[1])
    for b in bonds:
        if len(b['missing']) != 1: continue
        rs = [key(r) for r in b['readings']]; w = [int(ch) for ch in b['missing'][0]]
        for p in itertools.permutations(range(3)):
            a, bb, c = p
            T[(rs[a], w[a], rs[bb], w[bb])].add((rs[c], w[c]))
    by_a = collections.defaultdict(set)                      # (reading a, value) -> {(reading b, value)}
    for (ra, va, rb, vb) in T: by_a[(ra, va)].add((rb, vb))
    mask = {}
    def m(r):                                                # the carrier of a (reading, value) key as a bitmask
        if r[0] not in mask: mask[r[0]] = sum(1 << x for x in r[0][0])
        return mask[r[0]]
    out, seen = [], set()
    for a0 in list(by_a):
        ma0 = m(a0); partners = set()
        for bb in by_a[a0]: partners |= by_a[bb]
        for a1 in partners:
            if a1 <= a0 or ma0 & m(a1): continue
            mA = ma0 | m(a1)
            common_b = sorted(x for x in by_a[a0] & by_a[a1] if not mA & m(x))
            for p, b0 in enumerate(common_b):
                mb0 = m(b0)
                t00 = T.get((a0[0], a0[1], b0[0], b0[1]), set()) & T.get((a1[0], a1[1], b0[0], b0[1]), set())
                if len(t00) < 2: continue
                for b1 in common_b[p + 1:]:
                    if mb0 & m(b1): continue
                    mAB = mA | mb0 | m(b1)
                    C = t00 & T.get((a0[0], a0[1], b1[0], b1[1]), set()) & T.get((a1[0], a1[1], b1[0], b1[1]), set())
                    C = sorted(c for c in C if not mAB & m(c))
                    for q, c0 in enumerate(C):
                        for c1 in C[q + 1:]:
                            if m(c0) & m(c1): continue
                            k = frozenset([frozenset([a0, a1]), frozenset([b0, b1]), frozenset([c0, c1])])
                            if k in seen: continue
                            seen.add(k); out.append(((a0, a1), (b0, b1), (c0, c1)))
                            if limit and len(out) >= limit: return out
    return out


def upper_image(sup, box, drop=None):
    """missing words of (U_A, U_B, U_C) on the stage (law index `drop` removed), by a solver"""
    names = sorted({x for r in sup for x in r} | {x for pair in box for (C, v) in pair for x in C[0]})
    var = {x: i + 1 for i, x in enumerate(names)}; top = [len(names)]
    def fresh():
        top[0] += 1; return top[0]
    cl = []
    for i, r in enumerate(sup):
        if i == drop: continue
        v = [var[x] for x in r]; cl += [v, [-u for u in v]]
    def agree(xs):
        r = fresh()
        for x in xs[1:]: cl.extend([[-r, -xs[0], x], [-r, xs[0], -x]])
        cl.extend([[r] + [-x for x in xs], [r] + list(xs)]); return r
    def xnor(p, q):                                             # r <-> (p == q)
        r = fresh(); cl.extend([[-r, -p, q], [-r, p, -q], [r, p, q], [r, -p, -q]]); return r
    ups = []
    for (r0, v0), (r1, v1) in box:
        l0 = agree([var[x] for x in r0[0]]); l1 = agree([var[x] for x in r1[0]])
        u = xnor(l0, l1)                                       # [L0 = L1]
        ups.append(u if (v0 + v1) % 2 == 1 else -u)           # U = [L0 + L1 = v0 + v1 + 1]
    s = Minisat22(bootstrap_with=cl); miss = []
    for w in itertools.product((0, 1), repeat=3):
        if not s.solve(assumptions=[u if b else -u for u, b in zip(ups, w)]): miss.append(''.join(map(str, w)))
    s.delete(); return miss


def read_box(sup, box, n_start):
    """the box's upper missing words, the laws they need, whether a birth (a knot past the n_start start knots) is
    needed, and whether the box reads a born distinction"""
    miss = upper_image(sup, box)
    start_names = {x for r in sup[:n_start] for x in r}
    rec = {'box': [[[list(r[0][0]), r[1]] for r in pair] for pair in box], 'upper missing': miss,
           'reads a born distinction': any(x not in start_names for pair in box for (C, v) in pair for x in C[0])}
    if miss:
        need = [q for q in range(len(sup)) if set(upper_image(sup, box, drop=q)) != set(miss)]
        rec['laws needed'] = need; rec['a birth needed'] = any(q >= n_start for q in need)
    return rec
