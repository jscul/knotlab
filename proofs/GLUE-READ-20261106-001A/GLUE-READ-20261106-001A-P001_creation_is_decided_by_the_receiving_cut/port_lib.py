"""Creation at an atom is decided by its cut, for GLUE-READ-20261106-001A.

The setting is CHAIN-TRANSFER A's last step. A Fano atom B with its other elements present (its closure) meets the rest of a space at
one cut, beyond which lies a removal. The removal's side shows on the cut's three ports a complement-closed relation R (the port
relation), and deeper relations: singles (ports + one point) and pairs (ports + two points). Creation at a line of B is an OR over
local configurations (PENDANT-LINE A), so feeding every deeper relation compatible with R at once bounds what any far side can do.

Port values: p = p0 + 2 p1 + 4 p2 in the literal frame of B's splice (all signs zero).
"""
import collections
import importlib.util
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


CTC = ROOT / "proofs/CHAIN-TRANSFER-20261106-001C/CHAIN-TRANSFER-20261106-001C-P001_reading_the_tree_from_creation"
RD = load("gr_read_lib", CTC / "read_lib.py")
TR, TL, GL, DL = RD.TR, RD.TL, RD.GL, RD.DL
GM = DL.BL.GM
F = TL.F


# ------------------------------------------------------------------------------------------------ relations
def relations(nbits):
    """every nonempty complement-closed relation on nbits points, as masks over the 2^nbits assignments"""
    full = (1 << nbits) - 1
    reps = [b for b in range(1 << nbits) if b < full - b]
    out = []
    for m in range(1, 1 << len(reps)):
        r = 0
        for i, b in enumerate(reps):
            if (m >> i) & 1:
                r |= (1 << b) | (1 << (full - b))
        out.append(r)
    return out


def port_projection(r, nextra):
    out = 0
    for b in range(8 << nextra):
        if (r >> b) & 1:
            out |= 1 << (b & 7)
    return out


PORT_RELATIONS = relations(3)


def deep_relations():
    """for each port relation R: every single (ports + one point) and pair (ports + two points) relation projecting onto R, canonical"""
    singles, pairs = collections.defaultdict(set), collections.defaultdict(set)
    for r in relations(4):
        singles[port_projection(r, 1)].add(TL.canon1(r))
    for r in relations(5):
        pairs[port_projection(r, 2)].add(TL.canon2(r))
    return singles, pairs


# ------------------------------------------------------------------------------------------------ the native statement
def allows_equal(R):
    return bool(R & 1) and bool(R & 128)


def forces_equal(R, i, j):
    return all(((p >> i) & 1) == ((p >> j) & 1) for p in range(8) if (R >> p) & 1)


def symmetric(R):
    return all(TL._permute(R, 8, pi) == R for pi in TL.PERMS)


def slot_of(perm, x, b):
    """the port on cut line b of a receiving atom (minus its point x): transfer_lib's k-th line through x carries slot perm[k]"""
    through = [i for i in range(7) if x in F[i]]
    return perm[through.index(b)]


def native(kind, R, perm, x, b):
    """the law in native terms: kind 'point' = B emits (lost line x), 'line' = B receives (lost point x)"""
    if kind == "point":
        return allows_equal(R)
    if x in F[b]:
        s = slot_of(perm, x, b)
        i, j = [t for t in range(3) if t != s]
        return not forces_equal(R, i, j)
    return not symmetric(R)


def name(R):
    if R == 255:
        return "free"
    if R == 126:
        return "not all equal"
    if R == 129:
        return "all equal"
    return "/".join(sorted(format(p, "03b")[::-1] for p in range(8) if (R >> p) & 1))


# ------------------------------------------------------------------------------------------------ real spaces
def structure(S):
    """the tight-cut decomposition with owners: (braces, types, point owner, line owner, cuts {k: {brace: (kind, neighbours)}})"""
    parts = GM.decompose(GM.multigraph(S.H))
    types = [GM.brace_type(p)[0] for p in parts]
    pown, lown, xs = {}, {}, collections.defaultdict(dict)
    for b, part in enumerate(parts):
        for v in part:
            if v[0] == "P":
                pown[v[1]] = b
            elif v[0] == "L":
                lown[v[1]] = b
            else:
                xs[v[2]][b] = (v[1], sorted(part[v]))
    return parts, types, pown, lown, xs


def side_test(S, exact):
    """for every removal a and every line b of a Fano atom B not holding a: replace the removal's side of B's cut facing a by the
    relation it shows on the points it shares with B's side, and compare creation at b with the exact creation map"""
    parts, types, pown, lown, xs = structure(S)
    n = len(S.H)
    out = {a: {b for b, v in row.items() if v is not None and any(v)} for a, row in exact.items()}
    tree = nx.Graph()
    tree.add_nodes_from(range(len(parts)))
    for k, sides in xs.items():
        b1, b2 = sorted(sides)
        tree.add_edge(b1, b2)
    paths = dict(nx.all_pairs_shortest_path(tree))
    kind = "Fano trees" if set(types) == {"heawood"} else ("with a non-planar non-Heawood brace" if "other" in types else "with plane glue")
    c = collections.Counter()
    side_cache = {}
    for a in range(n):
        A = lown[a]
        for B in sorted(set(lown.values())):
            if B == A or types[B] != "heawood":
                continue
            nb = paths[B][A][1]
            if (B, nb) not in side_cache:
                h = tree.copy()
                h.remove_edge(B, nb)
                comp = nx.node_connected_component(h, nb)
                far = [x for x in range(n) if lown[x] in comp]
                near = [x for x in range(n) if lown[x] not in comp]
                ports = sorted({q for x in far for q in S.H[x]} & {q for x in near for q in S.H[x]})
                pts = sorted({q for x in near for q in S.H[x]})
                rel = {q: j for j, q in enumerate(pts)}
                ANn = TL.solutions([tuple(rel[q] for q in S.H[x]) for x in near], [S.s[x] for x in near], len(pts))
                side_cache[(B, nb)] = (far, near, ports, pts, rel, ANn)
            far, near, ports, pts, rel, ANn = side_cache[(B, nb)]
            L = [x for x in far if x != a]
            fpts = sorted({q for x in L for q in S.H[x]} | set(ports))
            frel = {q: j for j, q in enumerate(fpts)}
            ANf = TL.solutions([tuple(frel[q] for q in S.H[x]) for x in L], [S.s[x] for x in L], len(fpts))
            R = {tuple(int(v) for v in row) for row in ANf[:, [frel[q] for q in ports]]}
            pi = [rel[q] for q in ports]
            AN = ANn[np.array([tuple(int(v) for v in row[pi]) in R for row in ANn], dtype=bool)]
            through_glue = types[A] != "heawood" or any(types[x] != "heawood" for x in paths[A][B][1:-1])
            for b in [x for x in near if lown[x] == B]:
                Y = [rel[q] for q in S.H[b]]
                v = TL.verdict_of_near_side(AN, Y, S.s[b], [j for j in range(len(pts)) if j not in Y])
                tag = "%s; removal in %s; %s; %d patterns on %d shared points" % (
                    kind, "an atom" if types[A] == "heawood" else "glue", "glue between" if through_glue else "atoms only between",
                    len(R), len(ports))
                c[(tag, "pairs")] += 1
                c[(tag, "creation unchanged")] += (v is not None and any(v)) == (b in out[a])
    return c
