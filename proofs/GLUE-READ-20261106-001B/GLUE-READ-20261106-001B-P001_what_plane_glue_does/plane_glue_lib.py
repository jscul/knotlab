"""What plane glue does, for GLUE-READ-20261106-001B: random spaces with plane glue, exact creation maps, and the glue's effects.

Spaces:
- BRACE-TREE C's 111 fresh spaces (read_lib.census_spaces);
- 40 random spaces: Fano atoms hung on a random plane space (planar_lib.grow, a cube grown by ladder rungs), mostly on the plane;
- 40 random spaces: one or two Fano atoms hung on a census space with plane glue.
Every splice is the creation map's own (random element, lost element and port permutation).
"""
import collections
import gzip
import importlib.util
import itertools
import json
import random
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


GRA = ROOT / "proofs/GLUE-READ-20261106-001A/GLUE-READ-20261106-001A-P001_creation_is_decided_by_the_receiving_cut"
PL = load("gr_port_lib", GRA / "port_lib.py")
TL, TR, RD, GL = PL.TL, PL.TR, PL.RD, PL.GL


# ------------------------------------------------------------------------------------------------ spaces
def hang(S, r, k, names, host_bias=None):
    for j in range(k):
        name = "N%d" % j
        host = host_bias if (host_bias and r.random() < 0.6) else r.choice(names)
        cands = [("pt", key) for key in S.pkey if key[0] == host] + [("ln", key) for key in S.lkey if key[0] == host]
        kind, key = r.choice(cands)
        S = (GL.attach_point if kind == "pt" else GL.attach_line)(S, key, GL.FANO, r.randrange(7), name, r.choice(TL.PERMS))
        names.append(name)
    return S


def plane_space(seed):
    r = random.Random(seed)
    m = r.choice([6, 8, 10])
    k = r.choice([2, 3, 4])
    S = GL.plane(GL.PL.grow(m, r.randrange(10 ** 6)))
    return "plane of %d points + %d atoms (seed %d)" % (m, k, seed), hang(S, r, k, ["g"], host_bias="g")


def census_plus(seed, census):
    r = random.Random(seed)
    glued = [(nm, S) for nm, S in census if nm.startswith(("twisted", "untwisted"))]
    nm, S = glued[r.randrange(len(glued))]
    k = r.choice([1, 2])
    return "%s + %d atoms (seed %d)" % (nm, k, seed), hang(GL.base(S.H, S.s, S.n), r, k, ["g"])


def all_spaces():
    census = RD.census_spaces()
    rand = [plane_space(1000 + s) for s in range(40)] + [census_plus(2000 + s, census) for s in range(40)]
    return [("census", nm, S) for nm, S in census] + [("random", nm, S) for nm, S in rand]


# ------------------------------------------------------------------------------------------------ exact maps
def exact_maps(pool, spaces):
    tasks = [(i, M) for i, (src, nm, S) in enumerate(spaces) for M in range(len(S.H))]
    maps = [dict() for _ in spaces]
    for (i, M), (M_, row, ns) in zip(tasks, pool.imap(TR.exact_row, [(spaces[i][2], M) for i, M in tasks], chunksize=1)):
        maps[i][M] = row
    return maps


def encode(maps):
    return [{str(a): {str(b): (-1 if v is None else sum(int(x) << f for f, x in enumerate(v))) for b, v in row.items()}
             for a, row in m.items()} for m in maps]


def decode(data):
    return [{int(a): {int(b): (None if v < 0 else tuple(bool((v >> f) & 1) for f in range(4))) for b, v in row.items()}
             for a, row in m.items()} for m in data]


def save(path, spaces, maps):
    payload = {"spaces": [{"source": src, "name": nm, "lines": [list(L) for L in S.H], "signs": S.s, "points": S.n}
                          for src, nm, S in spaces], "maps": encode(maps)}
    with gzip.open(path, "wt") as f:
        json.dump(payload, f, sort_keys=True)


def load_maps(path):
    with gzip.open(path, "rt") as f:
        payload = json.load(f)
    spaces = [(d["source"], d["name"], GL.base([tuple(L) for L in d["lines"]], d["signs"], d["points"])) for d in payload["spaces"]]
    return spaces, decode(payload["maps"])


def creates(exact):
    return {a: {b for b, v in row.items() if v is not None and any(v)} for a, row in exact.items()}


# ------------------------------------------------------------------------------------------------ the glue's effects
def kind_of_space(types):
    return "Fano trees" if set(types) == {"heawood"} else ("with a non-planar non-Heawood brace" if "other" in types else "with plane glue")


def relation_class(npts, pats):
    """the port relation up to permuting and complementing ports: on three points by its number of patterns; two ports sharing a point
    tie them"""
    if npts == 2:
        return "two ports tied (one point), the third free" if len(pats) == 4 else "degenerate: %d patterns on two points" % len(pats)
    return {8: "free", 6: "one pattern pair excluded", 4: "two ports tied, the third free", 2: "all three tied"}[len(pats)]


def pair_effects(S, exact):
    """for every removal and every line of a Fano atom in another brace: what lies between, the class of the relation the removal's side
    shows on the facing cut, and whether the touching rule holds"""
    parts, types, pown, lown, xs = PL.structure(S)
    n = len(S.H)
    out = creates(exact)
    tree = nx.Graph()
    tree.add_nodes_from(range(len(parts)))
    cutof = {}
    for k, sides in xs.items():
        b1, b2 = sorted(sides)
        tree.add_edge(b1, b2)
        cutof[frozenset((b1, b2))] = k
    paths = dict(nx.all_pairs_shortest_path(tree))
    c = collections.Counter()
    sides_cache = {}
    for a in range(n):
        A = lown[a]
        for B in sorted(set(lown.values())):
            if B == A or types[B] != "heawood":
                continue
            nb = paths[B][A][1]
            k = cutof[frozenset((B, nb))]
            if (B, nb) not in sides_cache:
                h = tree.copy()
                h.remove_edge(B, nb)
                comp = nx.node_connected_component(h, nb)
                far = [x for x in range(n) if lown[x] in comp]
                near = [x for x in range(n) if lown[x] not in comp]
                sides_cache[(B, nb)] = (far, sorted({q for x in far for q in S.H[x]} & {q for x in near for q in S.H[x]}))
            far, ports = sides_cache[(B, nb)]
            L = [x for x in far if x != a]
            fpts = sorted({q for x in L for q in S.H[x]} | set(ports))
            frel = {q: j for j, q in enumerate(fpts)}
            ANf = TL.solutions([tuple(frel[q] for q in S.H[x]) for x in L], [S.s[x] for x in L], len(fpts))
            pats = {tuple(int(v) for v in row) for row in ANf[:, [frel[q] for q in ports]]}
            cls = relation_class(len(ports), pats)
            role, nbrs = xs[k][B]
            between = "atoms only between" if (types[A] == "heawood" and all(types[x] == "heawood" for x in paths[A][B][1:-1])) else \
                "glue between"
            for b in [x for x in range(n) if lown[x] == B]:
                touch = role == "L" or ("L", b) in nbrs
                tag = (kind_of_space(types), "removal in an atom" if types[A] == "heawood" else "removal in glue", between, cls)
                c[tag + ("pairs",)] += 1
                c[tag + ("touching rule holds",)] += touch == (b in out[a])
    return c


def twin_classes(n, out, keep=None, restrict=None):
    keep = set(range(n)) if keep is None else set(keep)
    restrict = set(range(n)) if restrict is None else set(restrict)
    g = nx.Graph()
    g.add_nodes_from(keep)
    for a, b in itertools.combinations(sorted(keep), 2):
        if b in out[a] and a in out[b] and (out[a] & restrict) - {b} == (out[b] & restrict) - {a}:
            g.add_edge(a, b)
    return [frozenset(c) for c in nx.connected_components(g)]


def atom_ports(S, parts, types, lown, xs, A):
    """for each cut of atom A: its role ('emits'/'receives'), the points on the emitting side's lost line (the ports), and the type of
    the brace across"""
    out = {}
    for k, sides in xs.items():
        if A not in sides:
            continue
        other = next(b for b in sides if b != A)
        em = A if sides[A][0] == "L" else other
        out[k] = ("emits" if sides[A][0] == "L" else "receives", [w[1] for w in sides[em][1] if w[0] == "P"], types[other])
    return out


def emitted_line_groups(parts, xs, A, k):
    """A emits at cut k (it lost a line there): its lines grouped by the point of the lost line they meet. Each neighbour of the
    contracted line vertex in A's brace is a point of the lost line, or the contracted vertex of another cut where A lost that point;
    the lines next to it in A's brace are A's lines through that point."""
    part = parts[A]
    X = next(v for v in part if v[0] == "X" and v[2] == k)
    return {frozenset(w[1] for w in part[v] if w[0] == "L") for v in part[X]}


def twin_effects(S, exact):
    """the twin classes against the atoms: joined glue lines (and which doubled-square lines carry two or more of an atom's ports), and
    split atoms (by port, and where their out-sets differ)"""
    parts, types, pown, lown, xs = PL.structure(S)
    n = len(S.H)
    out = creates(exact)
    classes = twin_classes(n, out)
    cls_of = {a: c for c in classes for a in c}
    atoms = collections.defaultdict(set)
    for k in range(n):
        if types[lown[k]] == "heawood":
            atoms[lown[k]].add(k)
    c = collections.Counter()
    for A, L in atoms.items():
        cuts = atom_ports(S, parts, types, lown, xs, A)
        # glue lines meeting A's cuts at two or more ports (a point that is a port of two cuts counts for each), and whether they join
        for g in range(n):
            if types[lown[g]] == "heawood":
                continue
            carried = sum(len(set(S.H[g]) & set(p)) for r, p, t in cuts.values())
            joined = bool(cls_of[g] & L)
            if carried >= 2 or joined:
                c[("glue line", types[lown[g]], "meeting the atom's cuts at %s ports" % ("two or more" if carried >= 2 else "fewer than two"),
                   "joins the atom's twin class" if joined else "does not join")] += 1
        own = {cls_of[a] for a in L}
        if len(own) == 1:
            c[("atom", "one twin class")] += 1
            continue
        c[("atom", "split into %d classes" % len(own))] += 1
        # by port: lines sharing the port of a cut facing plane glue
        split = {frozenset(cl & L) for cl in own}
        by_port = [k for k, (r, p, t) in cuts.items() if r == "emits" and t == "planar" and emitted_line_groups(parts, xs, A, k) == split]
        c[("atom split", "the classes are its lines through each point of a line it emits into a planar brace" if by_port
           else "not by the emitted line's points")] += 1
        diff = set()
        for c1, c2 in itertools.combinations(own, 2):
            a1, a2 = min(c1 & L), min(c2 & L)
            diff |= (out[a1] ^ out[a2]) - L
        c[("atom split", "the classes' out-sets differ only on glue lines" if all(types[lown[x]] != "heawood" for x in diff)
           else "they differ on atom lines too")] += 1
    return c
