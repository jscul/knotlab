"""A rule that reads the atoms from the far-side map, for FAR-READ-20261106-001B. Frozen here for ticket C.

Creation is the creation map's: for a removal a and a gluing line b, ex[a][b] is None (b shows fewer than six patterns) or the tuple of
four booleans (K4^(3), census 6, the Fano plane, census 58). "a creates at b" means some far side does.

The rule:
1. Twins: two lines that create at each other and at the same other lines. The lines in twin classes of two or more are the atom lines.
2. Atom twins: two atom lines that create at each other and at the same other atom lines. Their classes are the candidates.
3. Split by parts that act as one: a set S of atom lines acts as one when every atom line outside S receives the same far-side vector
   from each line of S. A candidate of six or more lines that is partitioned into two or more such sets of three or more lines is
   split into the finest such partition, and each part is examined again.
4. Reattach: a line left single by step 1 joins the one class of three or more lines with whose lines it creates both ways through
   the Fano plane, when that class acts as one and the line sends every atom line outside it the class's far-side vector.
The classes are read as the atoms, and their number as the genus.
"""
import importlib.util
import itertools
import sys
from pathlib import Path

import networkx as nx

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


FRA = ROOT / "proofs/FAR-READ-20261106-001A/FAR-READ-20261106-001A-P001_the_far_side_map"
FL = load("fr_far_lib", FRA / "far_lib.py")
AT, G = FL.AT, FL.G

MIN_SPLIT, MIN_PART = 6, 3


def closure(seed, universe, vec):
    """the smallest set containing seed that acts as one toward every line of universe outside it"""
    S = set(seed)
    changed = True
    while changed:
        changed = False
        for x in universe - S:
            if len({vec(a, x) for a in S}) > 1:
                S.add(x)
                changed = True
    return S


def parts_acting_as_one(M, universe, vec):
    """the sets inside M that act as one, generated from pairs and from unions of overlapping ones"""
    Ms = set(M)
    found = set()
    for a, b in itertools.combinations(sorted(Ms), 2):
        C = frozenset(closure({a, b}, universe, vec))
        if C < Ms:
            found.add(C)
    changed = True
    while changed:
        changed = False
        for X, Y in itertools.combinations(list(found), 2):
            if X & Y and not (X <= Y or Y <= X):
                U = frozenset(closure(set(X | Y), universe, vec))
                if U < Ms and U not in found:
                    found.add(U)
                    changed = True
    return found


def finest_partition(M, sets):
    Ms = frozenset(M)
    cands = sorted((s for s in sets if len(s) >= MIN_PART), key=len)
    best = [None]

    def search(rest, chosen):
        if not rest:
            if len(chosen) >= 2 and (best[0] is None or len(chosen) > len(best[0])):
                best[0] = list(chosen)
            return
        x = min(rest)
        for s in cands:
            if x in s and s <= rest:
                search(rest - s, chosen + [s])

    search(Ms, [])
    return best[0]


def split(M, universe, vec):
    if len(M) < MIN_SPLIT:
        return [frozenset(M)]
    part = finest_partition(M, parts_acting_as_one(M, universe, vec))
    if part is None:
        return [frozenset(M)]
    return [q for p in part for q in split(p, universe, vec)]


def read_atoms(n, ex, steps=4, reattach_through="the Fano plane"):
    """the classes the rule returns after the given number of steps"""
    out = G.creates(ex)
    vec = lambda a, b: ex[a].get(b)  # noqa: E731
    first = G.twin_classes(n, out)
    AL = set().union(*[c for c in first if len(c) >= 2])
    cls = G.twin_classes(n, out, keep=AL, restrict=AL)
    if steps >= 3:
        cls = [q for M in cls for q in split(M, AL, vec)]
    if steps >= 4:
        if reattach_through == "the Fano plane":
            both = lambda a, b: bool(ex[a].get(b)) and bool(ex[a][b][2]) and bool(ex[b].get(a)) and bool(ex[b][a][2])  # noqa: E731
        else:
            both = lambda a, b: b in out[a] and a in out[b]  # noqa: E731
        cls = [set(c) for c in cls]
        for s in sorted(next(iter(c)) for c in first if len(c) == 1):
            fits = []
            for C in cls:
                if len(C) < MIN_PART or not all(both(s, c) for c in C):
                    continue
                rest = AL - C - {s}
                rep = next(iter(C))
                if all(len({vec(c, x) for c in C}) == 1 and vec(s, x) == vec(rep, x) for x in rest):
                    fits.append(C)
            if len(fits) == 1:
                fits[0].add(s)
        cls = [frozenset(c) for c in cls]
    return cls
