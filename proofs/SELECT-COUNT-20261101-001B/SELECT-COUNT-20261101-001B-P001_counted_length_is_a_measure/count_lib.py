"""Counted length on the knot's spaces (SELECT-COUNT-20261101-001B): exact colouring counts by variable elimination.

A system is a list of lines, each a tuple of point labels. A colouring gives every point 0 or 1 and makes every line not-all-equal. An
incidence can be *fixed* (it reads a given value instead of its point's colour: a slot) or *twisted* (it reads its point's colour
exchanged). Counts are exact integers (numpy int64; every count here is far below 2^63)."""
import itertools

import numpy as np


def _line_factor(entries):
    """entries: per incidence ('var', point, twist) or ('const', value); returns (variables, table) of the not-all-equal indicator"""
    variables = sorted({e[1] for e in entries if e[0] == "var"})
    pos = {v: i for i, v in enumerate(variables)}
    table = np.zeros((2,) * len(variables), dtype=np.int64)
    for assign in itertools.product((0, 1), repeat=len(variables)):
        reads = [(assign[pos[e[1]]] ^ e[2]) if e[0] == "var" else e[1] for e in entries]
        table[assign] = 0 if len(set(reads)) == 1 else 1
    return tuple(variables), table


def count(lines, points, fixed=None, slots=None, twists=None):
    """number of colourings of `points` (the points of `fixed` are given and not counted) making every line of `lines` not-all-equal;
    slots: {(line index, point): value} incidences that read a value; twists: {(line index, point)} incidences read exchanged."""
    fixed, slots, twists = fixed or {}, slots or {}, twists or set()
    free = set(points) - set(fixed)
    factors = []
    for i, L in enumerate(lines):
        entries = []
        for p in L:
            t = 1 if (i, p) in twists else 0
            if (i, p) in slots:
                entries.append(("const", slots[(i, p)]))
            elif p in fixed:
                entries.append(("const", fixed[p] ^ t))
            elif p in free:
                entries.append(("var", p, t))
            else:
                raise ValueError("point %r of line %d is neither counted, fixed nor a slot" % (p, i))
        factors.append(_line_factor(entries))
    total = 1
    lonely = free - {v for vs, _ in factors for v in vs}
    total *= 2 ** len(lonely)
    remaining = free - lonely
    while remaining:
        scope = {}
        for vs, _ in factors:
            for v in vs:
                if v in remaining:
                    scope.setdefault(v, set()).update(vs)
        v = min(remaining, key=lambda u: (len(scope[u]), str(u)))
        inv = [f for f in factors if v in f[0]]
        rest = [f for f in factors if v not in f[0]]
        union = sorted(set().union(*[set(vs) for vs, _ in inv]), key=str)
        idx = {u: k for k, u in enumerate(union)}
        prod = np.ones((2,) * len(union), dtype=np.int64)
        for vs, tab in inv:
            shape = [2 if u in vs else 1 for u in union]
            order = sorted(range(len(vs)), key=lambda k: idx[vs[k]])
            prod = prod * np.transpose(tab, order).reshape(shape)
        new = prod.sum(axis=idx[v])
        factors = rest + [(tuple(u for u in union if u != v), new)]
        remaining.discard(v)
    for vs, tab in factors:
        assert vs == (), vs
        total *= int(tab)
    return total


def points_of(lines):
    return sorted({p for L in lines for p in L}, key=str)


def amplitude(lines, line):
    """half the number of colourings of the system without `line`"""
    rest = [L for i, L in enumerate(lines) if i != line]
    return count(rest, points_of(lines)) // 2


def side_weights(lines, cut, shore):
    """for a cut (edges between ('l', i) and ('p', p) vertices) and one shore, the number of colourings of the shore's points proper on
    its lines, for each assignment of values to the cut edges (in cut order): a port point takes its edge's value, a slot reads it"""
    pts = [v[1] for v in shore if v[0] == "p"]
    lns = [v[1] for v in shore if v[0] == "l"]
    edges = []
    for a, b in cut:
        l, p = (a, b) if a[0] == "l" else (b, a)
        edges.append((l[1], p[1], p in shore))
    sub = [lines[i] for i in lns]
    out = {}
    for w in itertools.product((0, 1), repeat=len(edges)):
        fixed, slots, ok = {}, {}, True
        for (li, p, port_inside), val in zip(edges, w):
            if port_inside:
                if fixed.get(p, val) != val:
                    ok = False
                fixed[p] = val
            else:
                slots[(lns.index(li), p)] = val
        out[w] = count(sub, pts, fixed=fixed, slots=slots) if ok else 0
    return out


def transpose(lines):
    """points become lines and lines become points"""
    pts = points_of(lines)
    return [tuple(i for i, L in enumerate(lines) if p in L) for p in pts]


def ring(units):
    """a ring of units: units[i] = (lines, (line index, point)) is a system with one incidence removed; unit i's port point is joined to
    unit i+1's slot line. Points are relabelled (unit index, point)."""
    out = []
    r = len(units)
    for i, (lines, (li, p)) in enumerate(units):
        for j, L in enumerate(lines):
            if j == li:
                pp = units[(i - 1) % r][1][1]
                out.append(tuple((i, q) for q in L if q != p) + (((i - 1) % r, pp),))
            else:
                out.append(tuple((i, q) for q in L))
    return out
