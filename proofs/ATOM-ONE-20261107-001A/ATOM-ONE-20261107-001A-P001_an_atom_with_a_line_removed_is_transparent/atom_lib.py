"""A Fano atom with a line removed is transparent, for ATOM-ONE-20261107-001A.

- The signed Fano planes: signs on the 21 incidences, up to flipping a point or a line (not-all-equal is unchanged by flipping all three
  literals of a line). Exactly one class has no not-all-equal colouring: the plain Fano plane.
- Freeness: in the Fano plane, removing any line together with any other element leaves that element's three variables free.
- Configurations: a Fano atom is the Heawood graph with some vertices contracted (its cuts); every closed side is a relation on the
  variables of its cut's three edges.
- Real spaces: the relation each closed side presents, and the relation an atom sends through each cut when one of its lines is removed.
"""
import collections
import importlib.util
import itertools
import sys
from pathlib import Path

import networkx as nx
import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


F = [(0, 1, 2), (0, 3, 4), (0, 5, 6), (1, 3, 5), (1, 4, 6), (2, 3, 6), (2, 4, 5)]
assert all(len(set(a) & set(b)) == 1 for a, b in itertools.combinations(F, 2))
INC = [(l, p) for l in range(7) for p in F[l]]
ELEMS = [("P", p) for p in range(7)] + [("L", l) for l in range(7)]


def nae_solutions(nv, lines):
    """all assignments of nv variables; lines: list of (variables, signs); not-all-equal on the literals value xor sign"""
    A = np.array(list(itertools.product((0, 1), repeat=nv)), dtype=np.int8)
    ok = np.ones(len(A), dtype=bool)
    for vs, ss in lines:
        t = (A[:, list(vs)] ^ np.array(ss, dtype=np.int8)).sum(axis=1)
        ok &= (t > 0) & (t < 3)
    return A[ok]


# ------------------------------------------------------------------------------------------------ signed Fano planes
def sign_classes():
    """(number of gauge classes, the classes that are knots), a class given by a representative sign word over INC"""
    gens = [sum(1 << i for i, (l, q) in enumerate(INC) if q == p) for p in range(7)] + \
           [sum(1 << i for i, (m, q) in enumerate(INC) if m == l) for l in range(7)]
    span = {0}
    for g in gens:
        span |= {s ^ g for s in span}
    rep = {}
    for s in range(1 << len(INC)):
        if s not in rep:
            r = min(s ^ g for g in span)
            for g in span:
                rep[s ^ g] = r
    reps = sorted(set(rep.values()))
    knots = []
    for s in reps:
        lines = [(F[l], tuple((s >> INC.index((l, p))) & 1 for p in F[l])) for l in range(7)]
        if len(nae_solutions(7, lines)) == 0:
            knots.append(s)
    return len(span), reps, knots


def opened(elems):
    """the Fano plane with the given elements opened: a line removed, a point split into one copy per remaining line through it.
    Returns (variables, lines as tuples of variable indices)."""
    var = {}
    for p in range(7):
        if ("P", p) not in elems:
            var[("P", p)] = len(var)
    lines = {}
    for l in range(7):
        if ("L", l) in elems:
            continue
        vs = []
        for p in F[l]:
            if ("P", p) in elems:
                var[("C", p, l)] = len(var)
                vs.append(var[("C", p, l)])
            else:
                vs.append(var[("P", p)])
        lines[l] = tuple(vs)
    return var, lines


def channels(var, X0):
    """the variables of element X0's three channels in an opened plane (a line: its points; a point: its copies), None where the
    channel's own line or point is opened too (that channel is unconstrained)"""
    if X0[0] == "L":
        return [var.get(("P", p)) for p in F[X0[1]]]
    return [var.get(("C", X0[1], l)) for l in range(7) if X0[1] in F[l]]


def freeness(removed_kind="L"):
    """for every element X0 and every other element D of the given kind (a line removed, or for 'P' a point opened): the patterns the
    Fano plane minus X0 and D shows on X0's channels, against all patterns"""
    out = []
    for X0 in ELEMS:
        for D in ELEMS:
            if D == X0 or D[0] != removed_kind:
                continue
            var, lines = opened({X0, D})
            AN = nae_solutions(len(var), [(vs, (0, 0, 0)) for vs in lines.values()])
            ch = [v for v in channels(var, X0) if v is not None]
            pats = {tuple(int(x) for x in row[ch]) for row in AN}
            out.append((X0, D, len(pats), 2 ** len(ch)))
    return out


# ------------------------------------------------------------------------------------------------ configurations without the knot
COLL = [p for p in itertools.permutations(range(7)) if {frozenset(p[q] for q in l) for l in F} == {frozenset(l) for l in F}]
LIDX = {frozenset(l): i for i, l in enumerate(F)}


def act(g, X):
    return frozenset(("P", g[v]) if k == "P" else ("L", LIDX[frozenset(g[p] for p in F[v])]) for k, v in X)


def nbrs(v):
    return [("L", i) for i in range(7) if v[1] in F[i]] if v[0] == "P" else [("P", p) for p in F[v[1]]]


def configurations():
    """every set of contracted Heawood vertices leaving at least one line, up to collineations"""
    seen, reps = set(), []
    for k in range(1, 15):
        for X in itertools.combinations(ELEMS, k):
            X = frozenset(X)
            if X in seen:
                continue
            seen |= {act(g, X) for g in COLL}
            if any(("L", i) not in X for i in range(7)):
                reps.append(X)
    return reps


def model(X):
    """variables: each uncontracted point, and for each contracted point one variable per edge (the point beyond); returns
    (number of variables, real lines, their variables, each cut's channel variables)"""
    var = {}
    for p in range(7):
        if ("P", p) not in X:
            var[("P", p)] = len(var)
    for v in sorted(X):
        if v[0] == "P":
            for w in nbrs(v):
                var[(v, w)] = len(var)

    def ev(line_vertex, point_vertex):
        return var[(point_vertex, line_vertex)] if point_vertex in X else var[point_vertex]

    real = [i for i in range(7) if ("L", i) not in X]
    lv = {i: tuple(ev(("L", i), ("P", p)) for p in F[i]) for i in real}
    cv = {v: (tuple(ev(v, ("P", p)) for p in F[v[1]]) if v[0] == "L" else tuple(var[(v, w)] for w in nbrs(v))) for v in sorted(X)}
    return len(var), real, lv, cv


PAIR = np.array([min(c, 7 - c) for c in range(8)])


def invariant_for_every_relation(X):
    """for each outgoing cut X0: is the relation on X0 the same, whichever real line is removed, for every choice of nonempty
    complement-closed relations on the other cuts? (For every pattern on X0, the complement-pair patterns of the other cuts compatible
    with it must not depend on the removed line; singleton products show this is also necessary.)"""
    nv, real, lv, cv = model(X)
    sols = {a: nae_solutions(nv, [(lv[i], (0, 0, 0)) for i in real if i != a]) for a in real}
    out = {}
    for X0 in sorted(X):
        others = [c for c in sorted(X) if c != X0]
        fib = []
        for a in real:
            AN = sols[a]
            code = lambda c: AN[:, cv[c][0]].astype(np.int64) + 2 * AN[:, cv[c][1]] + 4 * AN[:, cv[c][2]]  # noqa: E731
            key = code(X0)
            for c in others:
                key = key * 4 + PAIR[code(c)]
            fib.append(frozenset(np.unique(key).tolist()))
        out[X0] = all(f == fib[0] for f in fib)
    return out


# ------------------------------------------------------------------------------------------------ real spaces
def real_space_report(S, PO, TL):
    """for every Fano atom of S: each closed side's relation on its cut (a point side should accept one antipodal pair, a line side the
    six other patterns), and the relation the atom's side sends through each cut when each of its lines is removed (should be free)"""
    parts, types, pown, lown, xs = PO.structure(S)
    n = len(S.H)
    tree = nx.Graph()
    tree.add_nodes_from(range(len(parts)))
    for k, sides in xs.items():
        b1, b2 = sorted(sides)
        tree.add_edge(b1, b2)

    def sols(lines, pts):
        rel = {q: j for j, q in enumerate(pts)}
        return TL.solutions([tuple(rel[q] for q in S.H[x]) for x in lines], [S.s[x] for x in lines], len(pts))

    c = collections.Counter()
    for A in range(len(parts)):
        if types[A] != "heawood":
            continue
        LA = [x for x in range(n) if lown[x] == A]
        cuts = [k for k in xs if A in xs[k]]
        info = {}
        for k in cuts:
            b2 = [b for b in xs[k] if b != A][0]
            h = tree.copy()
            h.remove_edge(A, b2)
            comp = nx.node_connected_component(h, b2)
            far = [x for x in range(n) if lown[x] in comp]
            near = [x for x in range(n) if lown[x] not in comp]
            ports = sorted({q for x in far for q in S.H[x]} & {q for x in near for q in S.H[x]})
            info[k] = (far, ports)
        V = sorted({q for x in LA for q in S.H[x]} | {q for k in cuts for q in info[k][1]})
        side = {}
        for k in cuts:
            far, ports = info[k]
            fpts = sorted({q for x in far for q in S.H[x]} | set(ports))
            AN = sols(far, fpts)
            on = [q for q in fpts if q in V]
            side[k] = (on, {tuple(int(v) for v in row[[fpts.index(q) for q in on]]) for row in AN})
            R = {tuple(int(v) for v in row[[fpts.index(q) for q in ports]]) for row in AN}
            kind = xs[k][A][0]                      # the contracted vertex's kind in A: 'L' = the side acts as a line
            anti = lambda P: len(P) == 2 and all(tuple(1 - x for x in p) in P for p in P)  # noqa: E731
            allp = set(itertools.product((0, 1), repeat=len(ports)))
            ok = anti(R) if kind == "P" else (len(ports) == 3 and anti(allp - R))
            c["closed sides"] += 1
            c["closed sides: %s side, %d ports, as the theorem says" % ("point" if kind == "P" else "line", len(ports))] += ok
            c["closed sides: %s side, %d ports" % ("point" if kind == "P" else "line", len(ports))] += 1
        for k in cuts:
            far, ports = info[k]
            sent = set()
            for a in LA:
                AN = sols([x for x in LA if x != a], V)
                keep = np.ones(len(AN), dtype=bool)
                for j in cuts:
                    if j != k:
                        on, Rj = side[j]
                        idx = [V.index(q) for q in on]
                        keep &= np.array([tuple(int(v) for v in row[idx]) in Rj for row in AN], dtype=bool)
                pats = {tuple(int(v) for v in row[[V.index(q) for q in ports]]) for row in AN[keep]}
                c["(atom, cut, removed line)"] += 1
                c["... the relation sent is free"] += len(pats) == 2 ** len(ports)
                sent.add(frozenset(pats))
            c["(atom, cut)"] += 1
            c["... the same relation whichever line is removed"] += len(sent) == 1
    return c
