"""Which cyclic sequences to fix (research/WHICH-SEQUENCES-20261112-001/preregistration.md).

Bases: one copy of (2, 0, 4) (J1) and the first 12 undrawn bases of UNDRAWN-LEARN-20261111-001's frozen search (its sizes in order, seeds
0 to 99 each, every seed with a counting law at some interface while its plain law is satisfiable and does not count there), each with its
first counting set as interface. For each base: every law (signings modulo flipping a distinction and complementing a knot), whether it
counts three at the interface (constant 0 or 1), and its sums around every cyclic sequence of two or three knots; the base's symmetries
(permutations of distinctions carrying knots to knots) and their orbits on the sequences."""
import itertools
import random
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "proofs/LAW-RIGIDITY-20261112-001B/LAW-RIGIDITY-20261112-001B-P001_a_native_rest_set"))
import native_lib as N  # noqa: E402

UL, J = N.UL, N.J
NBASES = 12


ORDER = [(6, 7), (6, 8), (7, 8), (7, 9), (8, 9), (8, 10), (7, 10), (8, 11), (9, 11), (9, 12)]
SEEDS = 200


def collect_bases(k=NBASES, pool=None):
    """the first k hits in the frozen order: sizes in ORDER, then seeds 0..SEEDS-1 (UNDRAWN-LEARN's rule for a hit)"""
    jobs = [(seed, n, m) for n, m in ORDER for seed in range(SEEDS)]
    res = pool.map(_hit_job, jobs, chunksize=4) if pool else [_hit_job(j) for j in jobs]
    out = [r for r in res if r]
    return out[:k]


def _hit_job(job):
    seed, n, m = job
    r = _hit(seed, n, m)
    return None if r is None else (r[0], seed, n, m, r[2])


def base_of(hit):
    name, seed, n, m, T = hit
    return name, UL.Undrawn(seed, n, m), T


def _hit(seed, n, m):
    B = UL.Undrawn(seed, n, m)
    X = ((np.arange(1 << B.real)[:, None] >> np.arange(B.real)[None, :]) & 1).astype(np.uint8)
    P = np.array(B.pt)
    Ts = list(itertools.combinations(range(B.real), 4))
    TI = np.array(Ts)

    def allowed(s):
        S = np.array(s, dtype=np.uint8).reshape(B.nl, 3)
        Lt = X[:, P] ^ S[None, :, :]
        return X[~((Lt[:, :, 0] == Lt[:, :, 1]) & (Lt[:, :, 1] == Lt[:, :, 2])).any(axis=1)]

    def counting_sets(st):
        if len(st) == 0:
            return np.zeros(len(Ts), dtype=bool)
        par = st[:, TI].sum(axis=2) % 2
        const = (par == par[:1]).all(axis=0)
        code = st[:, TI[:, 0]] * 4 + st[:, TI[:, 1]] * 2 + st[:, TI[:, 2]]
        full = np.array([len(np.unique(code[:, j])) == 8 if const[j] else False for j in range(len(Ts))])
        return const & full

    plain = allowed([0] * (3 * B.nl))
    if len(plain) == 0:
        return None
    hit = np.zeros(len(Ts), dtype=bool)
    for s in UL.laws(B):
        hit |= counting_sets(allowed(s))
    if not hit.any():
        return None
    T = Ts[int(np.argmax(hit))]
    if counting_sets(plain)[Ts.index(T)]:
        return None
    return ("U(%d, %d) seed %d" % (n, m, seed), B, list(T))


def sequences(pt, maxlen=3):
    """every cyclic sequence of 2 to maxlen distinct knots and distinct distinctions, each knot holding the distinction before and after
    it, as frozensets of places (knot, distinction), with its length"""
    m = len(pt)
    out = {}

    def rec(ks, ds, n):
        k, d = ks[-1], ds[-1]
        for d2 in pt[k]:
            if d2 == d:
                continue
            if d2 == ds[0] and len(ks) == n:
                out[frozenset([(ks[i], ds[i]) for i in range(n)] + [(ks[i], ds[i + 1] if i + 1 < n else d2) for i in range(n)])] = n
                continue
            if d2 in ds or len(ks) >= n:
                continue
            for k2 in range(m):
                if k2 not in ks and d2 in pt[k2]:
                    rec(ks + [k2], ds + [d2], n)
    for n in range(2, maxlen + 1):
        for k in range(m):
            for d in pt[k]:
                rec([k], [d], n)
    return sorted(out.items(), key=lambda kv: (kv[1], sorted(kv[0])))


def symmetries(pt, nd):
    """permutations of the distinctions carrying the set of knots to itself, with the knot permutation they induce"""
    knots = {frozenset(t): i for i, t in enumerate(pt)}
    out = []
    for perm in itertools.permutations(range(nd)):
        img = [frozenset(perm[d] for d in t) for t in pt]
        if all(x in knots for x in img):
            out.append((perm, [knots[x] for x in img]))
    return out


def orbits(seqs, syms):
    """orbits of the sequences under the symmetries"""
    index = {s: i for i, (s, _) in enumerate(seqs)}
    orb = [-1] * len(seqs)
    c = 0
    for i, (s, _) in enumerate(seqs):
        if orb[i] >= 0:
            continue
        for perm, kperm in syms:
            j = index.get(frozenset((kperm[k], perm[d]) for (k, d) in s))
            if j is not None:
                orb[j] = c
        c += 1
    return orb


def law_table(B, T):
    """every law: its sums on every sequence (as a bit row) and whether it counts at T; the sequences with their lengths"""
    pt = [list(t) for t in B.pt]
    seqs = sequences(pt)
    nreal = B.real
    X = ((np.arange(1 << nreal)[:, None] >> np.arange(nreal)[None, :]) & 1).astype(np.uint8)
    P = np.array(B.pt)
    rows, counts = [], []
    for law in UL.laws(B):
        S = np.array(law, dtype=np.uint8).reshape(len(pt), 3)
        Lt = X[:, P] ^ S[None, :, :]
        st = X[~((Lt[:, :, 0] == Lt[:, :, 1]) & (Lt[:, :, 1] == Lt[:, :, 2])).any(axis=1)]
        if len(st) == 0:
            continue
        par = st[:, T].sum(axis=1) % 2
        c = bool((par == par[0]).all() and len({tuple(r) for r in st[:, T[:-1]]}) == 8)
        rows.append([sum(law[3 * k + pt[k].index(d)] for (k, d) in s) % 2 for s, _ in seqs])
        counts.append(c)
    return np.array(rows, dtype=np.uint8), np.array(counts), seqs


OPTIONS = ("free", "all 0", "all 1", "all equal")


def keep(rows, cols, opt):
    if opt == "free" or not cols:
        return np.ones(len(rows), dtype=bool)
    sub = rows[:, cols]
    if opt == "all 0":
        return (sub == 0).all(axis=1)
    if opt == "all 1":
        return (sub == 1).all(axis=1)
    return (sub == sub[:, :1]).all(axis=1)


def length_rules():
    return list(itertools.product(OPTIONS, OPTIONS))


def apply_length_rule(rows, seqs, rule):
    c2 = [i for i, (_, n) in enumerate(seqs) if n == 2]
    c3 = [i for i, (_, n) in enumerate(seqs) if n == 3]
    return keep(rows, c2, rule[0]) & keep(rows, c3, rule[1])
