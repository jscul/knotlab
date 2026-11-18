"""Referee R1 for NAE-METRIC-20261118-001 (own code; the study's naelib.py, job.py and the pinned metriclib are not imported).

  ../../../.venv/bin/python -B referee_nae.py <part> > referee_nae_<part>.json      (from this directory)

A knot is (law, places): the law a set of allowed patterns on its places (bit i = the value at place i), of arity three or four.
Free, bond and b as in the note (b infinite when no bond holds the pair).  The full bond matrix is found by testing every set; for
larger bases a bounded search (every set holding the pair up to a size) gives b exactly when the size reaches the bound used.

Parts:
  glue      1,500 random glued bases: two random blocks sharing one distinction y (not-all-equal, betweenness, parity, four-place
            not-all-equal, mixed within a block); Lemma 1 (each side's b is its own), Lemma 2 (b - 1 adds across y), the bond count;
            and a control with the clause "not all ones" (not complement-closed), where nothing is claimed.
  rings     rings of 3 to 10 knots, every knot's law drawn from not-all-equal and the three betweenness placements (any mixture):
            to 8 knots every pair exactly (full bond matrix, 4 mixtures); at 9 and 10 the 12 farthest pairs and 8 others (bounded search
            to steps + 2, 3 mixtures): b = steps + 1.
  cacti     150 random cacti of knots and rings (mixed laws, up to 18 distinctions): b - 1 = steps on every pair (bounded search).
  sp        graph-like bases (each distinction in at most two knots, knots meeting at most once), knot graph of maximum degree 3,
            every knot's law drawn at random (not only one twist), 10 to 15 distinctions: the triangle inequality, by series-parallel
            or not (no K4 minor).
  sp_plain  the same with every knot not-all-equal.
  (The series-parallel failures found by `sp` were extracted, and their single-twist variants rechecked with an independent
  freedom test (np.unique), into referee_nae_sp_failures.json and referee_nae_sp_single_twist.json.)
"""
import itertools
import json
import math
import random
import sys
from collections import Counter
from multiprocessing import Pool

import networkx as nx
import numpy as np


def sw(R, mask):
    return frozenset(p ^ mask for p in R)


NAE3 = frozenset(range(1, 7))
BETW = [sw(NAE3, 1 << i) for i in range(3)]            # middle at place i
P3E = frozenset([0, 3, 5, 6])
NAE4 = frozenset(range(1, 15))
CLAUSE = frozenset(range(7))


def states(n, knots):
    by_last = {}
    for R, t in knots:
        by_last.setdefault(max(t), []).append((R, t))
    P = np.zeros(1, dtype=np.int64)
    for v in range(n):
        P = np.concatenate([P, P | (1 << v)])
        for R, t in by_last.get(v, []):
            pat = np.zeros(len(P), dtype=np.int64)
            for i, u in enumerate(t):
                pat |= ((P >> u) & 1) << i
            allowed = np.zeros(1 << len(t), dtype=bool)
            allowed[list(R)] = True
            P = P[allowed[pat]]
    return P


class B:
    def __init__(self, n, st):
        self.n, self.st, self.c = n, st, {}

    def free(self, m):
        if m not in self.c:
            code = np.zeros(len(self.st), dtype=np.int64)
            k = 0
            for v in range(self.n):
                if (m >> v) & 1:
                    code |= ((self.st >> v) & 1) << k
                    k += 1
            self.c[m] = bool(np.all(np.bincount(code, minlength=1 << k)))
        return self.c[m]

    def bond(self, m):
        return not self.free(m) and all(self.free(m & ~(1 << i)) for i in range(self.n) if (m >> i) & 1)

    def matrix(self):
        D = [[math.inf] * self.n for _ in range(self.n)]
        bonds = []
        for m in range(1, 1 << self.n):
            if self.bond(m):
                bonds.append(m)
                vs = [i for i in range(self.n) if (m >> i) & 1]
                for x, y in itertools.combinations(vs, 2):
                    D[x][y] = D[y][x] = min(D[x][y], len(vs) - 1)
        return D, bonds

    def b_bounded(self, x, y, smax):
        others = [z for z in range(self.n) if z not in (x, y)]
        for s in range(2, smax + 1):
            for extra in itertools.combinations(others, s - 2):
                m = (1 << x) | (1 << y)
                for z in extra:
                    m |= 1 << z
                if self.bond(m):
                    return s - 1
        return None


def triangle_failures(D, n):
    return sum(1 for x, z in itertools.combinations(range(n), 2) for y in range(n)
               if y not in (x, z) and D[x][z] > D[x][y] + D[y][z])


def steps(knots, n):
    G = nx.Graph()
    for i, (_, t) in enumerate(knots):
        for v in t:
            G.add_edge(("k", i), ("d", v))
    sp = dict(nx.all_pairs_shortest_path_length(G))
    return lambda x, y: sp[("d", x)][("d", y)] // 2


# ---------------- glue ----------------

def random_block(rng, n_lo, n_hi, kinds):
    """A random block on distinctions 0..n-1 (connected primal graph, no cut distinction): knots of the given kinds."""
    while True:
        n = rng.randint(n_lo, n_hi)
        kn = []
        for _ in range(rng.randint(2, 4)):
            kind = rng.choice(kinds)
            if kind == "NAE4" and n >= 4:
                kn.append((NAE4, tuple(rng.sample(range(n), 4))))
            elif kind == "P":
                kn.append((rng.choice([P3E, sw(P3E, 7)]), tuple(rng.sample(range(n), 3))))
            elif kind == "B":
                kn.append((rng.choice(BETW), tuple(rng.sample(range(n), 3))))
            elif kind == "C":
                kn.append((CLAUSE, tuple(rng.sample(range(n), 3))))
            else:
                kn.append((NAE3, tuple(rng.sample(range(n), 3))))
        G = nx.Graph()
        G.add_nodes_from(range(n))
        for _, t in kn:
            G.add_edges_from(itertools.combinations(t, 2))
        if nx.is_biconnected(G) and len(states(n, kn)):
            return n, kn


def glue_case(seed):
    rng = random.Random(seed)
    control = seed % 10 == 9
    kinds = ["C", "N"] if control else rng.choice([["N"], ["B", "N"], ["P"], ["NAE4", "N"], ["P", "N", "B"]])
    nL, kL = random_block(rng, 3, 5, kinds)
    nR, kR = random_block(rng, 3, 5, kinds)
    yL, yR = rng.randrange(nL), rng.randrange(nR)
    # relabel: left distinctions 0..nL-1 with y = yL; right distinctions nL..nL+nR-2, with yR mapped to yL
    mapR = {}
    nxt = nL
    for v in range(nR):
        if v == yR:
            mapR[v] = yL
        else:
            mapR[v] = nxt
            nxt += 1
    n = nxt
    knots = kL + [(R, tuple(mapR[v] for v in t)) for R, t in kR]
    st = states(n, knots)
    if len(st) == 0:
        return None
    y = yL
    L = [v for v in range(nL) if v != y]
    Rr = [mapR[v] for v in range(nR) if v != yR]
    ybits = set(int((s >> y) & 1) for s in st)
    base = B(n, st)
    D, bonds = base.matrix()
    sL, sR = states(nL, kL), states(nR, [(R, t) for R, t in kR])
    DL, bondsL = B(nL, sL).matrix()
    DR0, bondsR = B(nR, sR).matrix()
    inv = {mapR[v]: v for v in range(nR)}
    lemma1 = all(D[a][c] == DL[a][c] for a, c in itertools.combinations(list(range(nL)), 2)) and \
        all(D[a][c] == DR0[inv[a]][inv[c]] for a, c in itertools.combinations(Rr + [y], 2))
    add_ok = add_n = 0
    for x in L:
        for z in Rr:
            add_n += 1
            lhs = D[x][z] - 1
            rhs = (D[x][y] - 1) + (D[y][z] - 1)
            add_ok += (lhs == rhs)
    thruL = sum(1 for m in bondsL if (m >> y) & 1)
    thruR = sum(1 for m in bondsR if (m >> yR) & 1)
    count_ok = len(bonds) == len(bondsL) + len(bondsR) + thruL * thruR
    return {"control": control, "kinds": "".join(kinds), "y_takes_both": len(ybits) == 2, "lemma1": lemma1,
            "triples": add_n, "additive": add_ok, "bond_count": count_ok}


def part_glue(count=1500, workers=16):
    with Pool(workers) as P:
        rows = [r for r in P.map(glue_case, range(count), chunksize=8) if r is not None]
    out = {}
    for ctl in (False, True):
        R = [r for r in rows if r["control"] == ctl and r["y_takes_both"]]
        out["clause control" if ctl else "complement-closed and parity"] = {
            "bases": len(R), "lemma1_holds": sum(r["lemma1"] for r in R), "separated_triples": sum(r["triples"] for r in R),
            "additive": sum(r["additive"] for r in R), "bond_count_identity": sum(r["bond_count"] for r in R),
            "by_kinds": dict(Counter(r["kinds"] for r in R))}
    out["parity bases with y fixed (excluded)"] = sum(1 for r in rows if not r["y_takes_both"])
    return out


# ---------------- rings and cacti ----------------

def ring_knots(m, laws, offset=0):
    ts = [((2 * i) % (2 * m) + offset, 2 * i + 1 + offset, (2 * i + 2) % (2 * m) + offset) for i in range(m)]
    return [(R, t) for R, t in zip(laws, ts)], 2 * m


def ring_case(args):
    """m <= 8: the full bond matrix (every pair, exact, infinity included).  m = 9, 10: bounded search (to steps + 2) on the 12
    farthest pairs and 8 random ones."""
    m, seed = args
    rng = random.Random(f"ring-{m}-{seed}")
    laws = [NAE3 if seed == 0 else rng.choice([NAE3] + BETW) for _ in range(m)]
    kn, n = ring_knots(m, laws)
    base = B(n, states(n, kn))
    st = steps(kn, n)
    off = 0
    worst = 0
    if m <= 8:
        D, _ = base.matrix()
        pairs = list(itertools.combinations(range(n), 2))
        for x, y in pairs:
            off += D[x][y] != st(x, y) + 1
            worst = max(worst, D[x][y])
        tri = triangle_failures(D, n)
    else:
        allp = sorted(itertools.combinations(range(n), 2), key=lambda p: -st(*p))
        pairs = allp[:12] + rng.sample(allp[12:], 8)
        for x, y in pairs:
            s = st(x, y)
            b = base.b_bounded(x, y, s + 2)
            off += b != s + 1
            worst = max(worst, b if b else 0)
        tri = None
    return {"m": m, "mixture": "plain" if seed == 0 else "".join("N" if R == NAE3 else "B" for R in laws), "pairs": len(pairs),
            "exhaustive": m <= 8, "off": off, "largest_b": worst, "floor_m2_plus_2": m // 2 + 2, "triangle_failures": tri}


def part_rings(workers=16):
    jobs = [(m, s) for m in range(3, 9) for s in range(4)] + [(m, s) for m in (9, 10) for s in range(3)]
    with Pool(workers) as P:
        rows = P.map(ring_case, jobs, chunksize=1)
    return {"rows": rows, "pairs": sum(r["pairs"] for r in rows), "off": sum(r["off"] for r in rows),
            "largest_b_as_predicted": sum(r["largest_b"] == r["floor_m2_plus_2"] for r in rows), "rings": len(rows)}


def cactus_case(seed):
    rng = random.Random(f"cactus-{seed}")
    knots, n = [], 0
    attach = [None]
    while n < 12:
        a = rng.choice(attach) if attach != [None] else None
        if rng.random() < 0.5:
            m = rng.randint(3, 4)
            laws = [rng.choice([NAE3] + BETW) for _ in range(m)]
            ts = []
            ring = [a if (i == 0 and a is not None) else None for i in range(m)]
            ids = []
            for i in range(m):
                if i == 0 and a is not None:
                    ids.append(a)
                else:
                    ids.append(n)
                    n += 1
            for i in range(m):
                p = n
                n += 1
                ts.append((ids[i], p, ids[(i + 1) % m]))
            knots += list(zip(laws, ts))
            attach += [v for t in ts for v in t]
        else:
            t = [a] if a is not None else []
            while len(t) < 3:
                t.append(n)
                n += 1
            rng.shuffle(t)
            knots.append((rng.choice([NAE3] + BETW), tuple(t)))
            attach += t
        attach = [v for v in attach if v is not None]
    if n > 18:
        return None
    base = B(n, states(n, knots))
    st = steps(knots, n)
    off = 0
    pairs = 0
    for x, y in itertools.combinations(range(n), 2):
        s = st(x, y)
        b = base.b_bounded(x, y, s + 2)
        pairs += 1
        off += b != s + 1
    return {"n": n, "knots": len(knots), "pairs": pairs, "off": off}


def part_cacti(count=150, workers=16):
    with Pool(workers) as P:
        rows = [r for r in P.map(cactus_case, range(count), chunksize=1) if r is not None]
    return {"cacti": len(rows), "pairs": sum(r["pairs"] for r in rows), "off": sum(r["off"] for r in rows),
            "largest_n": max(r["n"] for r in rows), "bad": [r for r in rows if r["off"]][:3]}


# ---------------- series-parallel graph-like ----------------

def series_parallel(G):
    H = nx.Graph(G)
    changed = True
    while changed:
        changed = False
        for v in list(H.nodes()):
            if v not in H:
                continue
            d = H.degree(v)
            if d <= 1:
                H.remove_node(v)
                changed = True
            elif d == 2:
                a, b = list(H.neighbors(v))
                H.remove_node(v)
                H.add_edge(a, b)
                changed = True
    return H.number_of_nodes() == 0


def sp_case(seed, plain=False):
    rng = random.Random(f"sp-{seed}" if not plain else f"sp-plain-{seed}")
    while True:
        k = rng.randint(4, 9)
        G = nx.Graph()
        G.add_nodes_from(range(k))
        for _ in range(rng.randint(k, 2 * k)):
            a, b = rng.sample(range(k), 2)
            if G.degree(a) < 3 and G.degree(b) < 3:
                G.add_edge(a, b)
        if not nx.is_connected(G) or nx.is_tree(G):
            continue
        slots = {v: [] for v in range(k)}
        n = 0
        for a, b in G.edges():
            slots[a].append(n)
            slots[b].append(n)
            n += 1
        for v in range(k):
            while len(slots[v]) < 3:
                slots[v].append(n)
                n += 1
        if not 10 <= n <= 15:
            continue
        knots = []
        for v in range(k):
            t = list(slots[v])
            rng.shuffle(t)
            knots.append((NAE3 if plain else rng.choice([NAE3] + BETW), tuple(t)))
        st = states(n, knots)
        if len(st) == 0:
            continue
        D, _ = B(n, st).matrix()
        return {"plain": plain, "k": k, "n": n, "series_parallel": series_parallel(G), "biconnected": nx.is_biconnected(G),
                "betweenness_knots": sum(R != NAE3 for R, _ in knots), "fails": triangle_failures(D, n) > 0}


def sp_plain(seed):
    return sp_case(seed, plain=True)


def part_sp_plain(count=160, workers=16):
    with Pool(workers) as P:
        rows = P.map(sp_plain, range(count), chunksize=1)
    out = {}
    for spv in (True, False):
        R = [r for r in rows if r["series_parallel"] == spv]
        out["series-parallel" if spv else "with a K4 minor"] = {"bases": len(R), "failing": sum(r["fails"] for r in R)}
    return out


def part_sp(count=160, workers=16):
    with Pool(workers) as P:
        rows = P.map(sp_case, range(count), chunksize=1)
    out = {}
    for spv in (True, False):
        R = [r for r in rows if r["series_parallel"] == spv]
        out["series-parallel" if spv else "with a K4 minor"] = {"bases": len(R), "failing": sum(r["fails"] for r in R),
                                                               "n_range": [min(r["n"] for r in R), max(r["n"] for r in R)] if R else None,
                                                               "with_betweenness": sum(r["betweenness_knots"] > 0 for r in R)}
    return out


if __name__ == "__main__":
    part = sys.argv[1]
    f = {"glue": part_glue, "rings": part_rings, "cacti": part_cacti, "sp": part_sp, "sp_plain": part_sp_plain}[part]
    print(json.dumps(f(), indent=1, default=str))
