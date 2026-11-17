"""Referee R1 for CARRIER-20261117-001: carriers of bounded reach by SAT, with the referee's own orbits, pieces, projections and
bond search (nothing from the study's routines is used to compute a value; the routines' stored outputs are only compared).

  ../../../.venv/bin/python -B referee_carrier.py [part] > referee_carrier_<part>.json      (from this directory)

The pattern P_N is the census's `pattern(key, N)`, the object under study (as in KEEP-REACH-R1).  Address (n, y) is variable
y + 2^n - 1; its children are (n + 1, 2y) and (n + 1, 2y + 1).  Orbits at level n are the components of the level under the
placement's used words (KEEP-REACH-R1's `orbits`).  For a top orbit O_u at level 3 and an orbit O_v at level 3 + s:
- the block piece is O_u, O_v and the children of O_v's addresses;
- the stem piece (depth 2) is O_u, the orbits at levels 4 and 5 that hold O_v's ancestors, and O_v;
- the two-orbit piece is O_u and O_v.
The projection of P_N's states onto a piece is enumerated exactly by CaDiCaL with blocking clauses on the piece's variables.  A bond
is a set of the piece holding an address of O_u and one of O_v, constrained in the projection, with every subset one smaller free.

Parts:
  tiers0, tiers1, tiers2 (four patterns each) every orbit pair, s = 1 .. N - 3, at N = 7 and 8, for the 12 counterexamples: least block bond, least stem bond, against the
          stored every-depth sequences at the tier r = N - 3 - s (this covers r = 0, 1, 2 and so every tier of -147 and -111)
  caseii  stems whose O_v does not descend from O_u (case (ii)), against stems where it does, at N = 8
  deep    one size past the study's depth 11: at N = 12, for six of the 12 and s = 5, 7, 9, a pair whose least carrier bond is at
          most 5, found by search over 24 random pairs, and the bond checked on the whole pattern by SAT
  deep2   at N = 12, the two distinct ca1efb37ad88 patterns at s = 7 and 9, pairs in order, where deep's random sample missed
  all7    every pair at s = 7, N = 10 and 11, for two ca1efb37ad88 patterns, where the depth-12 sample found no carrier
  cap     the owner's point (c): at N = 10, s = 7, for three of the 13, whether every stem projection is a product of its upper part
          and O_v (then no stem bond exists of any size), and the uncapped least bond where it is not
  thirteen one description of each of the five distinct patterns among the 13, N = 9, s = 5 and 6: a stem bond of at most 6,
          checked on the whole pattern (the stored 6, 6 as an upper bound)
"""
from __future__ import annotations

import itertools
import json
import random
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "experiments/LEVEL-REACH-20261114-001A/LEVEL-REACH-20261114-001A-E001_level_reach/codex"))
sys.path.insert(0, str(ROOT / "research/KEEP-REACH-20261117-001/referee-R1"))
from pattern import pattern  # noqa: E402  (the object under study)
from pysat.solvers import Cadical195  # noqa: E402
from referee_two_orbit_sat import orbits  # noqa: E402  (the referee's own orbits, from KEEP-REACH-R1)

THIRD = json.load(open(ROOT / "research/KEEP-REACH-20261117-001/third_class.json"))["third"]
BLOCK = json.load(open(HERE.parent / "block_25.json"))
TWELVE = ["bace53f8f952-147", "bace53f8f952-111", "bace53f8f952-58"] + [f"ca1efb37ad88-{i}" for i in
                                                                         (361, 364, 367, 375, 378, 386, 389, 418, 835)]
THIRTEEN = [f"8db5da810c00-{i}" for i in (73, 76, 79, 81, 84, 86, 89, 92, 94, 97, 100, 103, 106)]


def vid(n, y):
    return y + (1 << n) - 1


class Pattern:
    def __init__(self, idx, N):
        self.idx, self.N = idx, N
        self.key = THIRD[idx]["key"]
        K = pattern(self.key, N)
        self.cl = []
        for a, b, c in K.tolist():
            self.cl.append([a + 1, b + 1, c + 1])
            self.cl.append([-(a + 1), -(b + 1), -(c + 1)])
        self.orb = {n: orbits(self.key, n) for n in range(0, N + 1)}
        self.where = {n: {y: i for i, o in enumerate(self.orb[n]) for y in o} for n in self.orb}

    def orbit_of(self, n, ys):
        ids = {self.where[n][y] for y in ys}
        assert len(ids) == 1, (n, ids)
        return self.orb[n][ids.pop()]

    def project(self, vars_):
        """Exact projection of all states of P_N onto vars_ (list of 0-based variables), as an int array of rows."""
        rows = []
        with Cadical195(bootstrap_with=self.cl) as S:
            for v in vars_:                       # register every piece variable, even one no clause mentions (it is free)
                S.add_clause([v + 1, -(v + 1)])
            while S.solve():
                m = S.get_model()
                bits = [1 if m[v] > 0 else 0 for v in vars_]
                rows.append(sum(b << i for i, b in enumerate(bits)))
                S.add_clause([-(v + 1) if b else (v + 1) for v, b in zip(vars_, bits)])
        return np.array(sorted(rows), dtype=np.int64)

    def is_bond(self, vars_):
        """Constrained on the whole pattern, with every subset one smaller free (direct SAT, no projection)."""
        with Cadical195(bootstrap_with=self.cl) as S:
            def free(vs):
                return all(S.solve(assumptions=[(v + 1) if (m >> i) & 1 else -(v + 1) for i, v in enumerate(vs)])
                           for m in range(1 << len(vs)))
            return (not free(vars_)) and all(free(vars_[:i] + vars_[i + 1:]) for i in range(len(vars_)))


def least_bond(rows, n, umask, vmask, cap=8):
    """Least |S| with S meeting umask and vmask, the projection onto S not full, every subset one smaller full."""
    if len(rows) == 0:
        return None, None
    bits = ((rows[:, None] >> np.arange(n)) & 1).astype(np.int64)
    free_prev = {(i,) for i in range(n) if len(np.unique(bits[:, i])) == 2}
    for size in range(2, min(n, cap) + 1):
        cands = [S for S in itertools.combinations(range(n), size)
                 if all(T in free_prev for T in itertools.combinations(S, size - 1))]
        if not cands:
            return None, None
        free_now = set()
        w = 1 << np.arange(size)
        for S in cands:
            d = len(np.unique(bits[:, list(S)] @ w)) if len(rows) >= (1 << size) else 0
            if d == (1 << size):
                free_now.add(S)
            elif any((umask >> i) & 1 for i in S) and any((vmask >> i) & 1 for i in S):
                return size, S
        free_prev = free_now
    return None, None


def pieces(P, U, lv, V, kind):
    """Variables of a piece (O_u first, then O_v, then the rest), with the masks of O_u's and O_v's positions."""
    k = 3
    if kind == "two":
        parts = [[vid(k, u) for u in U], [vid(lv, v) for v in V]]
    elif kind == "block":
        kids = sorted({(v << 1) | b for v in V for b in (0, 1)})
        parts = [[vid(k, u) for u in U], [vid(lv, v) for v in V]] + ([[vid(lv + 1, c) for c in kids]] if lv < P.N else [])
    elif kind == "stem":
        anc = [P.orbit_of(n, {v >> (lv - n) for v in V}) for n in (k + 1, k + 2)]
        parts = [[vid(k, u) for u in U]] + [[vid(n, a) for a in A] for n, A in zip((k + 1, k + 2), anc)] + [[vid(lv, v) for v in V]]
        parts = [parts[0], parts[3], parts[1], parts[2]]          # O_u, O_v, then the ancestors
    vars_ = [v for p in parts for v in p]
    umask = (1 << len(parts[0])) - 1
    vmask = ((1 << len(parts[1])) - 1) << len(parts[0])
    return vars_, umask, vmask


def least_over_pairs(P, s, kind, pairs=None, cap=8, want=None):
    lv = 3 + s
    best, arg = None, None
    allpairs = [(U, V) for U in P.orb[3] for V in P.orb[lv]] if pairs is None else pairs
    for U, V in allpairs:
        vars_, um, vm = pieces(P, U, lv, V, kind)
        rows = P.project(vars_)
        b, S = least_bond(rows, len(vars_), um, vm, cap if best is None else min(cap, best))
        if b is not None and (best is None or b < best):
            best, arg = b, (U, V, [vars_[i] for i in S])
            if want is not None and best <= want:
                break
    return best, arg


def stored(idx, kind, s, r):
    if kind == "block":
        seqs = BLOCK[idx]["sequences"]
        r0 = BLOCK[idx]["r0"]
        tier = f"r={r}" if r <= r0 else f"r>={r0 + 1}"
        return seqs[tier][s - 1] if s - 1 < len(seqs[tier]) else "beyond"
    f = HERE.parent / "head" / f"{idx}_d2.json"
    if not f.exists():
        return "not run by the study"
    h = json.load(open(f))
    if s <= 2:
        return "n/a"
    tiers = h["sequences"]
    tier = next(iter(tiers)) if len(tiers) == 1 else (f"r={r}" if f"r={r}" in tiers else [t for t in tiers if t.startswith("r>=")][0])
    seq = tiers[tier]
    j = s - 3
    return seq[j] if j < len(seq) else "beyond"


def part_tiers(group=None):
    out = []
    pats = TWELVE if group is None else TWELVE[4 * group: 4 * group + 4]
    for idx in pats:
        for N in (7, 8):
            P = Pattern(idx, N)
            for s in range(1, N - 2):
                r = N - 3 - s
                row = {"pattern": idx, "N": N, "s": s, "r": r}
                for kind in ("block", "stem"):
                    if kind == "stem" and s <= 2:
                        continue
                    t = time.time()
                    b, arg = least_over_pairs(P, s, kind)
                    row[kind] = b
                    row[kind + "_stored"] = stored(idx, kind, s, r)
                    row[kind + "_agree"] = b == row[kind + "_stored"] if isinstance(row[kind + "_stored"], (int, type(None))) else None
                    row[kind + "_seconds"] = round(time.time() - t, 1)
                out.append(row)
                print(json.dumps(row), file=sys.stderr, flush=True)
    return out


def part_caseii():
    out = []
    for idx in ["bace53f8f952-58", "ca1efb37ad88-361", "8db5da810c00-73"]:
        P = Pattern(idx, 8)
        for s in (3, 4, 5):
            lv = 3 + s
            res = {"pattern": idx, "N": 8, "s": s}
            for case in ("i", "ii"):
                pairs = [(U, V) for U in P.orb[3] for V in P.orb[lv]
                         if (all((v >> s) in set(U) for v in V)) == (case == "i")]
                b, arg = least_over_pairs(P, s, "stem", pairs=pairs)
                res[f"case_{case}_pairs"] = len(pairs)
                res[f"case_{case}_least_stem_bond"] = b
            res["stored_least"] = stored(idx, "stem", s, 8 - 3 - s)
            out.append(res)
            print(json.dumps(res), file=sys.stderr, flush=True)
    return out


DEEP = ["bace53f8f952-147", "bace53f8f952-111", "bace53f8f952-58", "ca1efb37ad88-361", "ca1efb37ad88-418", "ca1efb37ad88-835"]


def part_deep(N=12, svals=(5, 7, 9)):
    out = []
    rng = random.Random(5)
    for idx in DEEP:
        P = Pattern(idx, N)
        for s in svals:
            lv = 3 + s
            pairs = [(U, V) for U in P.orb[3] for V in P.orb[lv]]
            rng.shuffle(pairs)
            t = time.time()
            found = None
            for kind in (("block", "stem") if idx.startswith("bace53f8f952-1") else ("stem", "block")):
                b, arg = least_over_pairs(P, s, kind, pairs=pairs[:24], cap=5, want=5)
                if b is not None and b <= 5:
                    found = {"kind": kind, "size": b, "bond_on_whole_pattern": P.is_bond(arg[2])}
                    break
            row = {"pattern": idx, "N": N, "s": s, "found": found, "seconds": round(time.time() - t, 1)}
            out.append(row)
            print(json.dumps(row), file=sys.stderr, flush=True)
    return out


def part_thirteen():
    """One description of each of the five distinct patterns among the 13, at N = 9 and s = 5, 6 (the study's 6, 6): a stem bond of
    at most 6, searched over the pairs in order and checked on the whole pattern (the upper bound; the lower bound is the study's
    LRAT-certified search, not repeated)."""
    out = []
    for idx in ("8db5da810c00-73", "8db5da810c00-76", "8db5da810c00-81", "8db5da810c00-89", "8db5da810c00-100"):
        P = Pattern(idx, 9)
        for s in (5, 6):
            t = time.time()
            b, arg = least_over_pairs(P, s, "stem", cap=6, want=6)
            row = {"pattern": idx, "N": 9, "s": s, "stem_bond_of_at_most_6_found": b,
                   "bond_on_whole_pattern": P.is_bond(arg[2]) if arg else None, "stored": stored(idx, "stem", s, 9 - 3 - s),
                   "seconds": round(time.time() - t, 1)}
            out.append(row)
            print(json.dumps(row), file=sys.stderr, flush=True)
    return out


def part_all7():
    """Where the depth-12 sample of 24 pairs found no carrier of at most 5 (ca1efb37ad88 at s = 7), search every pair, at N = 10
    and 11 (remaining depth 0 and 1; the study's stem tier is r >= 0), stopping at the first stem bond of at most 5."""
    out = []
    for idx in ("ca1efb37ad88-361", "ca1efb37ad88-835"):
        for N in (10, 11):
            P = Pattern(idx, N)
            s = 7
            pairs = [(U, V) for U in P.orb[3] for V in P.orb[3 + s]]
            t = time.time()
            b, arg = least_over_pairs(P, s, "stem", pairs=pairs, cap=5, want=5)
            row = {"pattern": idx, "N": N, "s": s, "pairs": len(pairs), "least_stem_bond_cap5": b,
                   "bond_on_whole_pattern": P.is_bond(arg[2]) if arg else None,
                   "pair_case": None if not arg else ("i" if all((v >> s) in set(arg[0]) for v in arg[1]) else "ii"),
                   "seconds": round(time.time() - t, 1)}
            out.append(row)
            print(json.dumps(row), file=sys.stderr, flush=True)
    return out


def part_deep2(N=12):
    """Depth 12, one size past: for the two distinct ca1efb37ad88 patterns at s = 7 and 9, every pair in order (case (i) pairs come
    first), stopping at the first stem bond of at most 5, checked on the whole pattern."""
    out = []
    for idx in ("ca1efb37ad88-361", "ca1efb37ad88-835"):
        P = Pattern(idx, N)
        for s in (7, 9):
            pairs = [(U, V) for U in P.orb[3] for V in P.orb[3 + s]]
            t = time.time()
            b, arg = least_over_pairs(P, s, "stem", pairs=pairs, cap=5, want=5)
            row = {"pattern": idx, "N": N, "s": s, "least_stem_bond_cap5": b,
                   "bond_on_whole_pattern": P.is_bond(arg[2]) if arg else None, "seconds": round(time.time() - t, 1)}
            out.append(row)
            print(json.dumps(row), file=sys.stderr, flush=True)
    return out


def part_cap(N=10, s=7):
    """The owner's point (c): is "no stem bond of at most 8" a cap?  For every pair at s = 7, test whether the stem piece's projection
    is the product of its upper part (O_u and the two ancestors) and O_v.  A product has no bond meeting both sides, of any size."""
    out = []
    for idx in ("8db5da810c00-73", "8db5da810c00-89", "8db5da810c00-100"):
        P = Pattern(idx, N)
        lv = 3 + s
        prod, nonprod = 0, []
        for U in P.orb[3]:
            for V in P.orb[lv]:
                vars_, um, vm = pieces(P, U, lv, V, "stem")
                rows = P.project(vars_)
                nu, nvv = len(U), len(V)
                upper = ~vm & ((1 << len(vars_)) - 1)
                A = {int(r) & upper for r in rows}
                B = {int(r) & vm for r in rows}
                if len(rows) == len(A) * len(B):
                    prod += 1
                else:
                    nonprod.append(least_bond(rows, len(vars_), um, vm, cap=len(vars_))[0])
        row = {"pattern": idx, "N": N, "s": s, "pairs": prod + len(nonprod), "stem_projection_is_product": prod,
               "least_bonds_of_the_others_uncapped": nonprod}
        out.append(row)
        print(json.dumps(row), file=sys.stderr, flush=True)
    return out


if __name__ == "__main__":
    part = sys.argv[1]
    if part.startswith("tiers"):
        res = part_tiers(int(part[5:]) if len(part) > 5 else None)
    else:
        res = {"caseii": part_caseii, "deep": part_deep, "thirteen": part_thirteen, "cap": part_cap,
               "all7": part_all7, "deep2": part_deep2}[part]()
    print(json.dumps(res, indent=1, default=str))
