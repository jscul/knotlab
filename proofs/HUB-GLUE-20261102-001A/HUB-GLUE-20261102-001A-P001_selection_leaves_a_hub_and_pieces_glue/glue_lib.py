"""Signed knot (not-all-equal) systems on cubic triple systems: failure, signings, splices, 3-edge cuts, circuits."""
import itertools
import json
import math
from pathlib import Path

import numpy as np

FANO = [(1, 2, 5), (0, 6, 2), (3, 2, 4), (4, 0, 5), (6, 3, 5), (4, 6, 1), (0, 1, 3)]
K4 = [(1, 2, 3), (0, 2, 3), (0, 1, 3), (0, 1, 2)]
_X = {}


def states(n):
    if n not in _X:
        _X[n] = np.array(list(itertools.product((0, 1), repeat=n)), dtype=np.int8)
    return _X[n]


def sat_matrix(lines, signs, n):
    """sat[x, i]: does assignment x satisfy the signed knot on line i?"""
    X = states(n)
    cols = []
    for L, s in zip(lines, signs):
        v = [X[:, p] ^ s[j] for j, p in enumerate(L)]
        cols.append(~((v[0] == v[1]) & (v[1] == v[2])))
    return np.stack(cols, axis=1)


def fails_globally(lines, signs, n):
    sat = sat_matrix(lines, signs, n)
    return (not sat.all(axis=1).any()) and all(np.delete(sat, i, axis=1).all(axis=1).any() for i in range(len(lines)))


def removal(lines, signs, n, i):
    """the solutions after line i is removed, as tuples"""
    sat = sat_matrix(lines, signs, n)
    return [tuple(int(v) for v in x) for x in states(n)[np.delete(sat, i, axis=1).all(axis=1)]]


def failing_signings(lines, n, first_only=False):
    """signings with the first incidence of each line positive (line switching) on which the knot fails"""
    out = []
    for bits in itertools.product((0, 1), repeat=2 * len(lines)):
        signs = [[0, bits[2 * i], bits[2 * i + 1]] for i in range(len(lines))]
        sat = sat_matrix(lines, signs, n)
        if not sat.all(axis=1).any():
            out.append(signs)
            if first_only:
                break
    return out


def dual(lines, signs, n):
    """points and lines exchanged; each incidence keeps its sign"""
    dl, ds = [], []
    for p in range(n):
        inc = [(i, L.index(p)) for i, L in enumerate(lines) if p in L]
        dl.append(tuple(i for i, _ in inc))
        ds.append([signs[i][j] for i, j in inc])
    return dl, ds, len(lines)


def splice(H1, s1, n1, li, H2, s2, n2, pt, all_choices=False):
    """remove line li of H1 and point pt of H2; join the line's i-th point to the i-th line through the point.
    Returns (lines, signs, n, side, ports) for a sign choice on the three new incidences that keeps failure
    (or the list of all such choices with all_choices)."""
    L = H1[li]
    rest1 = [(l, s) for i, (l, s) in enumerate(zip(H1, s1)) if i != li]
    relabel, k = {}, 0
    for p in range(n2):
        if p != pt:
            relabel[p] = n1 + k
            k += 1
    through = [(l, s) for l, s in zip(H2, s2) if pt in l]
    others = [(l, s) for l, s in zip(H2, s2) if pt not in l]
    lines = [l for l, _ in rest1] + [tuple(relabel[q] for q in l) for l, _ in others]
    signs = [list(s) for _, s in rest1] + [list(s) for _, s in others]
    joins = []
    for i, (l, s) in enumerate(through):
        keep = [(relabel[q], s[j]) for j, q in enumerate(l) if q != pt]
        joins.append((tuple(q for q, _ in keep) + (L[i],), [sg for _, sg in keep]))
    n = n1 + n2 - 1
    side = [0] * n1 + [1] * (n2 - 1)
    found = []
    for tw in itertools.product((0, 1), repeat=3):
        ls = lines + [j[0] for j in joins]
        ss = signs + [j[1] + [tw[i]] for i, j in enumerate(joins)]
        sat = sat_matrix(ls, ss, n)
        if not sat.all(axis=1).any():
            found.append((ls, ss, n, side, set(L)))
            if not all_choices:
                return found[0]
    return found if all_choices else None


def three_edge_cuts(lines, n):
    """nontrivial 3-edge cuts of the incidence graph, as (point side points, point side lines); both shores have 2 or more vertices"""
    m = len(lines)
    nv = n + m                                            # vertices: points 0..n-1, lines n..n+m-1
    eu = np.array([p for i, L in enumerate(lines) for p in L], dtype=np.int64)
    ev = np.array([n + i for i, L in enumerate(lines) for p in L], dtype=np.int64)
    cuts = set()
    total = 2 ** (nv - 1)                                 # the last vertex always on the far side
    chunk = 2 ** 20
    for start in range(1, total, chunk):
        masks = np.arange(start, min(start + chunk, total), dtype=np.int64)
        size = np.zeros(len(masks), dtype=np.int64)
        for j in range(nv):
            size += (masks >> j) & 1
        keep = (size >= 2) & (nv - size >= 2)
        cross = np.zeros(len(masks), dtype=np.int64)
        for u, v in zip(eu, ev):
            cross += ((masks >> u) ^ (masks >> v)) & 1
        for mask in masks[keep & (cross == 3)]:
            mask = int(mask)
            pts = {j for j in range(n) if mask >> j & 1}
            lns = {j - n for j in range(n, nv) if mask >> j & 1}
            if len(pts) - len(lns) == -1:
                pts = set(range(n)) - pts
                lns = set(range(m)) - lns
            cuts.add((frozenset(pts), frozenset(lns)))
    return sorted(cuts, key=lambda c: (len(c[0]), sorted(c[0])))


def contract(lines, signs, n, pts, lns):
    """the two contractions of a 3-edge cut: the point side closed by a new line through its three ports, the line side closed by a
    new point on its three slot lines; old signs kept, new incidences searched. Returns (point piece fails, line piece fails)."""
    pts, lns = sorted(pts), sorted(lns)
    cut = [(p, i) for i, L in enumerate(lines) if i not in lns for p in L if p in pts]
    if len({p for p, _ in cut}) != 3 or len({i for _, i in cut}) != 3:
        return None                                      # a port or a slot line meets two cut edges: the contraction is not simple
    ports = sorted({p for p, _ in cut})
    pmap = {p: k for k, p in enumerate(pts)}
    P_lines = [tuple(pmap[p] for p in lines[i]) for i in lns]
    P_signs = [list(signs[i]) for i in lns]
    point_ok = any(not sat_matrix(P_lines + [tuple(pmap[p] for p in ports)], P_signs + [list(tw)], len(pts)).all(axis=1).any()
                   for tw in itertools.product((0, 1), repeat=3))
    qpts = [p for p in range(n) if p not in pts]
    qmap = {p: k for k, p in enumerate(qpts)}
    newp = len(qpts)
    Q_lines, Q_signs, slots = [], [], []
    for i, L in enumerate(lines):
        if i in lns:
            continue
        keep = [(qmap[p], signs[i][j]) for j, p in enumerate(L) if p not in pts]
        if len(keep) == 3:
            Q_lines.append(tuple(q for q, _ in keep))
            Q_signs.append([s for _, s in keep])
        else:
            slots.append(len(Q_lines))
            Q_lines.append(tuple(q for q, _ in keep) + (newp,))
            Q_signs.append([s for _, s in keep] + [0])
    line_ok = False
    for tw in itertools.product((0, 1), repeat=3):
        ss = [list(s) for s in Q_signs]
        for t, i in zip(tw, slots):
            ss[i][-1] = t
        if not sat_matrix(Q_lines, ss, newp + 1).all(axis=1).any():
            line_ok = True
            break
    return point_ok, line_ok, len(ports) == 3 and len(slots) == 3


def circuits(sol, n, maxsize=None):
    """the minimal constrained sets (range-relative) of a set of assignments, up to a size bound"""
    ranges = [len({t[v] for t in sol}) for v in range(n)]
    arr = np.array(sol, dtype=np.int64)
    found = []
    for r in range(1, (maxsize or n) + 1):
        for Y in itertools.combinations(range(n), r):
            if any(C <= set(Y) for C in found):
                continue
            codes = (arr[:, list(Y)] * (2 ** np.arange(r))).sum(axis=1)
            if len(np.unique(codes)) < math.prod(ranges[v] for v in Y):
                found.append(frozenset(Y))
    return found


def census_spaces(root):
    """the census substrates on which the signed knot fails, with one failing signing each"""
    census = json.loads((Path(root) / "research/MUTUAL-SELECTION-20261031-001C/census.json").read_text())
    rows = [(int(n), [tuple(L) for L in row["lines"]]) for n, v in sorted(census.items(), key=lambda kv: int(kv[0])) for row in v["rows"]]
    out = []
    for idx, (n, lines) in enumerate(rows):
        if len({frozenset(L) for L in lines}) < n:
            continue
        sg = failing_signings(lines, n, first_only=True)
        if sg:
            out.append((idx, n, lines, sg[0]))
    return out
