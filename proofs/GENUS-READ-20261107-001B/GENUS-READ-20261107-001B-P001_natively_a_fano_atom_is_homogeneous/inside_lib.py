"""Creation inside a Fano atom, by composition, for GENUS-READ-20261107-001B.

A Fano atom is the Heawood graph with contracted vertices X (its cuts), numbered as the builders number the Fano plane. By ATOM-ONE A
every closed side shows exactly its lost element (equality of copies behind a lost point, not-all-equal behind a lost line) together with
deep relations: singles (its three channels and one deep point) and pairs (channels and two deep points), bit layout channels + 8 x +
16 w. Creation at a gluing line b of the atom, with a line a of the atom removed, is TL.verdict_from_masks over the masks of b's points
with one or two further points (PENDANT-LINE A): the atom's variables; deep points of one side, alone, in pairs or with an atom variable;
deep points of two sides. Every side of a Fano tree is a Fano atom with closed Fano-tree sides of its own (side_state), so the states it
can show are generated from the leaves; their union is reached as a fixed point.
"""

import importlib.util, itertools, sys
from pathlib import Path
import numpy as np
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path); mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod; spec.loader.exec_module(mod); return mod
AL = load("gr_b_atom_lib", ROOT / "proofs/ATOM-ONE-20261107-001A/ATOM-ONE-20261107-001A-P001_an_atom_with_a_line_removed_is_transparent/atom_lib.py")
PL = load("gr_b_port_lib", ROOT / "proofs/GLUE-READ-20261106-001A/GLUE-READ-20261106-001A-P001_creation_is_decided_by_the_receiving_cut/port_lib.py")
TL = PL.TL
F = [tuple(l) for l in TL.F]          # the Fano plane as GL builds it (its own line numbering)


def nbrs(v):
    return [("L", i) for i in range(7) if v[1] in F[i]] if v[0] == "P" else [("P", p) for p in F[v[1]]]


def model(X):
    """as atom_lib.model, on this numbering"""
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
PYI = TL.PYI
W1 = np.array([[1 << (y * 2 + v) for v in (0, 1)] for y in range(6)], dtype=np.int64)
W2 = np.array([[[1 << (y * 4 + v + 2 * w) for w in (0, 1)] for v in (0, 1)] for y in range(6)], dtype=np.int64)

def masks1(M):
    return set((M * W1).reshape(-1, 12).sum(axis=1).tolist())

def masks2(M):
    return set((M * W2).reshape(-1, 24).sum(axis=1).tolist())

def s_arr(rels):
    out = np.zeros((len(rels), 8, 2), dtype=bool)
    for i, r in enumerate(rels):
        for c in range(8):
            for v in (0, 1):
                out[i, c, v] = (r >> (c + 8 * v)) & 1
    return out

def p_arr(rels):
    out = np.zeros((len(rels), 8, 2, 2), dtype=bool)
    for i, r in enumerate(rels):
        for b in range(32):
            if (r >> b) & 1:
                out[i, b & 7, (b >> 3) & 1, (b >> 4) & 1] = True
    return out

# ------------------------------------------------------------------ leaf states
def leaf_state(kind):
    """the deep relations of a closed leaf atom behind a cut of the given kind, as seen on the cut's three channels (in order):
    kind 'P' (the atom lost a point there): the leaf is the Fano plane minus line 0, channels its points F[0];
    kind 'L' (the atom lost a line there): the leaf is the Fano plane minus point 0, its lines through 0 carrying the channels."""
    if kind == "P":
        lines = [F[l] for l in range(1, 7)]
        AN = AL.nae_solutions(7, [(l, (0, 0, 0)) for l in lines])
        ch = list(F[0]); deep = [p for p in range(7) if p not in ch]
    else:
        thr = [l for l in range(7) if 0 in F[l]]
        var = {p: p - 1 for p in range(1, 7)}
        copies = {l: 6 + j for j, l in enumerate(thr)}
        lines = [tuple(copies[l] if p == 0 else var[p] for p in F[l]) for l in range(7)]
        AN = AL.nae_solutions(9, [(l, (0, 0, 0)) for l in lines])
        ch = [copies[l] for l in thr]; deep = list(range(6))
    code = AN[:, ch[0]].astype(np.int64) + 2 * AN[:, ch[1]] + 4 * AN[:, ch[2]]
    S1, S2 = set(), set()
    for q in deep:
        r = 0
        for c, v in zip(code.tolist(), AN[:, q].tolist()):
            r |= 1 << (c + 8 * v)
        S1.add(TL.canon1(r))
    for q, w in itertools.combinations(deep, 2):
        r = 0
        for c, v, u in zip(code.tolist(), AN[:, q].tolist(), AN[:, w].tolist()):
            r |= 1 << (c + 8 * v + 16 * u)
        S2.add(TL.canon2(r))
    return frozenset(S1), frozenset(S2)

# ------------------------------------------------------------------ inside an atom
def inner(X, states, yperm=(0, 1, 2)):
    """{(a, b): far-side vector} for real lines a != b of the atom with contracted set X; states: {cut vertex: (singles, pairs)};
    yperm: the order in which the gluing line's points meet the far side"""
    nv, real, lv, cv = model(X)
    cuts = sorted(X)
    out = {}
    for a in real:
        lines = [(lv[i], (0, 0, 0)) for i in real if i != a]
        AN = AL.nae_solutions(nv, lines)
        keep = np.ones(len(AN), dtype=bool)
        for c in cuts:
            vs = cv[c]
            code = AN[:, vs[0]].astype(np.int64) + 2 * AN[:, vs[1]] + 4 * AN[:, vs[2]]
            keep &= ((code == 0) | (code == 7)) if c[0] == "P" else ((code != 0) & (code != 7))
        AN = AN[keep]
        ccode = {c: AN[:, cv[c][0]].astype(np.int64) + 2 * AN[:, cv[c][1]] + 4 * AN[:, cv[c][2]] for c in cuts}
        for b in real:
            if b == a:
                continue
            Y = [lv[b][k] for k in yperm]
            yc = AN[:, Y[0]].astype(np.int64) + 2 * AN[:, Y[1]] + 4 * AN[:, Y[2]]
            if len(set(yc.tolist())) != 6 or 0 in yc or 7 in yc:
                out[(a, b)] = None
                continue
            yi = np.array([PYI[v] for v in yc.tolist()])
            others = [j for j in range(nv) if j not in Y]
            m1, m2 = set(), set()
            for j in others:
                T = np.zeros((6, 2), dtype=bool); T[yi, AN[:, j]] = True
                m1 |= masks1(T[None])
            for j, k in itertools.combinations(others, 2):
                T = np.zeros((6, 2, 2), dtype=bool); T[yi, AN[:, j], AN[:, k]] = True
                m2 |= masks2(T[None])
            for c in cuts:
                S1, S2 = states[c]
                sa, pa = s_arr(sorted(S1)), p_arr(sorted(S2))
                Tc = np.zeros((6, 8), dtype=bool); Tc[yi, ccode[c]] = True
                m1 |= masks1(np.einsum("ya,iav->iyv", Tc, sa) > 0)
                m2 |= masks2(np.einsum("ya,iavw->iyvw", Tc, pa) > 0)
                for j in others:
                    T = np.zeros((6, 8, 2), dtype=bool); T[yi, ccode[c], AN[:, j]] = True
                    m2 |= masks2(np.einsum("yab,iav->iyvb", T, sa) > 0)
            for c, d in itertools.combinations(cuts, 2):
                sa, sb = s_arr(sorted(states[c][0])), s_arr(sorted(states[d][0]))
                T = np.zeros((6, 8, 8), dtype=bool); T[yi, ccode[c], ccode[d]] = True
                m2 |= masks2(np.einsum("yab,iav,jbw->ijyvw", T, sa, sb) > 0)
            out[(a, b)] = TL.verdict_from_masks(m1, m2)
    return out


# ------------------------------------------------------------------ states of closed Fano-tree sides
PERMS = list(itertools.permutations(range(3)))


def symmetrize(state):
    """close a state under permutations of its three channels"""
    S1, S2 = state
    return (frozenset(TL.canon1(TL._permute(r, 16, pi)) for r in S1 for pi in PERMS),
            frozenset(TL.canon2(TL._permute(r, 32, pi)) for r in S2 for pi in PERMS))


def side_state(e, children):
    """the state, on the channels of element e, of a closed side whose adjacent Fano atom lost e toward its parent and has a closed
    child side at each element in children ({element: state}); everything else of the atom present."""
    X = frozenset([e]) | frozenset(children)
    nv, real, lv, cv = model(X)
    AN = AL.nae_solutions(nv, [(lv[i], (0, 0, 0)) for i in real])
    keep = np.ones(len(AN), dtype=bool)
    code = {c: AN[:, cv[c][0]].astype(np.int64) + 2 * AN[:, cv[c][1]] + 4 * AN[:, cv[c][2]] for c in X}
    for c in children:
        keep &= ((code[c] == 0) | (code[c] == 7)) if c[0] == "P" else ((code[c] != 0) & (code[c] != 7))
    AN = AN[keep]
    code = {c: v[keep] for c, v in code.items()}
    ce = code[e]
    others = [j for j in range(nv) if j not in cv[e]]
    S1, S2 = set(), set()
    for j in others:
        r = 0
        for a, v in zip(ce.tolist(), AN[:, j].tolist()):
            r |= 1 << (a + 8 * v)
        S1.add(TL.canon1(r))
    for j, k in itertools.combinations(others, 2):
        r = 0
        for a, v, w in zip(ce.tolist(), AN[:, j].tolist(), AN[:, k].tolist()):
            r |= 1 << (a + 8 * v + 16 * w)
        S2.add(TL.canon2(r))
    def rel_e_c(c):                       # pairs (code on e, code on c) present
        return set(zip(ce.tolist(), code[c].tolist()))
    for c, (C1, C2) in children.items():
        ec = rel_e_c(c)
        for s in C1:
            r = 0
            for a, b in ec:
                for v in (0, 1):
                    if (s >> (b + 8 * v)) & 1:
                        r |= 1 << (a + 8 * v)
            S1.add(TL.canon1(r))
        for t in C2:
            r = 0
            for a, b in ec:
                for v in (0, 1):
                    for w in (0, 1):
                        if (t >> (b + 8 * v + 16 * w)) & 1:
                            r |= 1 << (a + 8 * v + 16 * w)
            S2.add(TL.canon2(r))
        for j in others:
            trip = set(zip(ce.tolist(), code[c].tolist(), AN[:, j].tolist()))
            for s in C1:
                r = 0
                for a, b, u in trip:
                    for v in (0, 1):
                        if (s >> (b + 8 * v)) & 1:
                            r |= 1 << (a + 8 * v + 16 * u)
                S2.add(TL.canon2(r))
    for c, d in itertools.combinations(sorted(children), 2):
        trip = set(zip(ce.tolist(), code[c].tolist(), code[d].tolist()))
        for s in children[c][0]:
            for s2 in children[d][0]:
                r = 0
                for a, b, b2 in trip:
                    for v in (0, 1):
                        if (s >> (b + 8 * v)) & 1:
                            for w in (0, 1):
                                if (s2 >> (b2 + 8 * w)) & 1:
                                    r |= 1 << (a + 8 * v + 16 * w)
                S2.add(TL.canon2(r))
    return symmetrize((frozenset(S1), frozenset(S2)))


def union(s, t):
    return (s[0] | t[0], s[1] | t[1])


def native_inner(X, states):
    """{(a, b): (K4^(3), number of the six orders at which census 6 creates, Fano, census 58)}"""
    per = [inner(X, states, pi) for pi in PERMS]
    out = {}
    for k in per[0]:
        vs = [d[k] for d in per]
        if vs[0] is None:
            out[k] = None
            continue
        assert all(len({v[f] for v in vs}) == 1 for f in (0, 2, 3)), (k, vs)
        out[k] = (vs[0][0], sum(v[1] for v in vs), vs[0][2], vs[0][3])
    return out


# ------------------------------------------------------------------ configurations and the reachable states
COLL = [p for p in itertools.permutations(range(7)) if {frozenset(p[q] for q in l) for l in F} == {frozenset(l) for l in F}]
LIDX = {frozenset(l): i for i, l in enumerate(F)}
ELEMS = [("P", p) for p in range(7)] + [("L", l) for l in range(7)]


def act(g, X):
    return frozenset(("P", g[v]) if k == "P" else ("L", LIDX[frozenset(g[p] for p in F[v])]) for k, v in X)


def configurations():
    """every set of contracted vertices leaving at least one line, up to collineations"""
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


SIDE_E = {"P": ("L", 0), "L": ("P", 0)}       # behind a lost point the side's atom lost a line; behind a lost line, a point


def leaves():
    return {"P": symmetrize(leaf_state("P")), "L": symmetrize(leaf_state("L"))}


def reachable_max(pool=None):
    """the union of every state a closed Fano-tree side can show, behind a lost point ('P') and behind a lost line ('L'): from the
    leaves, hang at one or two elements of the side's atom children carrying the current union, until nothing new appears (the state is
    a union of single-child and two-child contributions, so one or two children reach every contribution). Returns (states, rounds)."""
    cur = leaves()
    rounds = 0
    while True:
        rounds += 1
        tasks = []
        for side in ("P", "L"):
            e = SIDE_E[side]
            rest = [j for j in ELEMS if j != e]
            for r in (1, 2):
                for J in itertools.combinations(rest, r):
                    tasks.append((side, e, J, cur))
        res = (pool.imap_unordered(_side_task, tasks, chunksize=4) if pool else map(_side_task, tasks))
        new = dict(cur)
        for side, st in res:
            new[side] = union(new[side], st)
        if new == cur:
            return cur, rounds
        cur = new


def _side_task(args):
    side, e, J, cur = args
    return side, side_state(e, {j: cur["P" if j[0] == "P" else "L"] for j in J})


# ------------------------------------------------------------------ native vectors from one set of masks
def _relabel(masks, sigma, k):
    """masks over (Y-pattern index, k further values) with the Y-pattern index mapped by sigma"""
    out = set()
    for m in masks:
        r = 0
        for y in range(6):
            for t in range(1 << k):
                if (m >> (y * (1 << k) + t)) & 1:
                    r |= 1 << (sigma[y] * (1 << k) + t)
        out.add(r)
    return out


ORDER_MAPS = []
for _pi in PERMS:
    # the gluing line read in order Y[pi[0]], Y[pi[1]], Y[pi[2]]: a pattern p (as read in the stored order) becomes (p[pi[0]], ...)
    ORDER_MAPS.append([TL.PY.index(tuple(TL.PY[y][_pi[j]] for j in range(3))) for y in range(6)])


def native_of_near_side(AN, Y, sig, others):
    """the native vector at a gluing line (K4^(3), census-6 orders out of six, Fano, census 58) from one computation of the masks"""
    mm = TL.near_masks(AN, Y, sig, others)
    if mm is None:
        return None
    m1, m2 = mm
    vs = [TL.verdict_from_masks(_relabel(m1, s, 1), _relabel(m2, s, 2)) for s in ORDER_MAPS]
    assert all(len({v[f] for v in vs}) == 1 for f in (0, 2, 3))
    return (vs[0][0], sum(v[1] for v in vs), vs[0][2], vs[0][3])
