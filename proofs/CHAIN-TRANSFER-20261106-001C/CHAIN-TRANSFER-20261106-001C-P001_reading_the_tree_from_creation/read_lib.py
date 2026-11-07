"""Reading a Fano tree from creation, for CHAIN-TRANSFER-20261106-001C.

The rule uses only which lines create at which:
- twins: two lines are twins when each creates at the other and they create at the same other lines; the twin classes are the atoms;
- footprints: the footprint of an atom A on an atom X is the set of X's lines at which A's lines create; for each atom X, the atoms
  whose footprint on X is a given proper subset of X's lines form the far side of one cut where X receives;
- the tree: each such far side is the split of one cut, read from its receiver; the cut joins the receiver to the atom of the far side
  that no other split separates from it, and runs from that atom (the emitter) to the receiver.
"""
import collections
import importlib.util
import itertools
import sys
from pathlib import Path

import networkx as nx

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CTB = ROOT / "proofs/CHAIN-TRANSFER-20261106-001B/CHAIN-TRANSFER-20261106-001B-P001_the_source_rule_on_larger_trees"


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


TR = load("ct_tree_lib", CTB / "tree_lib.py")
TL, GL, DL, F = TR.TL, TR.GL, TR.DL, TR.F


def read_tree(n, out):
    """n lines; out[a]: the lines a creates at. Returns (classes, directed edges as (emitter class, receiver class), splits)."""
    g = nx.Graph()
    g.add_nodes_from(range(n))
    for a, b in itertools.combinations(range(n), 2):
        if b in out[a] and a in out[b] and out[a] - {b} == out[b] - {a}:
            g.add_edge(a, b)
    classes = sorted((frozenset(c) for c in nx.connected_components(g)), key=min)
    m = len(classes)
    fp = {(i, j): frozenset(out[min(classes[i])] & classes[j]) for i in range(m) for j in range(m) if i != j}
    splits = set()
    for j in range(m):
        groups = collections.defaultdict(set)
        for i in range(m):
            if i != j:
                groups[fp[(i, j)]].add(i)
        for f, beyond in groups.items():
            if f != classes[j]:
                splits.add((j, frozenset(beyond)))
    edges = set()
    for (r, beyond) in splits:
        near = [e for e in beyond if not any((e in b2) != (r in b2) for (r2, b2) in splits if (r2, b2) != (r, beyond))]
        edges.add((near[0] if len(near) == 1 else None, r))
    return classes, edges, splits


def footprints_uniform(out, classes):
    """the footprint of an atom on another is the same from each of its lines"""
    return all(len({frozenset(out[a] & B) for a in A}) == 1 for A in classes for B in classes if A != B)


def truth(S, cuts):
    """the atoms as line sets and the directed cuts, from the build's bookkeeping"""
    owner = [k[0] for k in S.lkey]
    atoms = collections.defaultdict(set)
    for k, o in enumerate(owner):
        atoms[o].add(k)
    return atoms, {(e, r) for e, r, q in cuts}


def condition_N(S, cuts):
    """every atom keeps a line, and the footprints of its receiving cuts (its surviving lines through each lost point) are distinct
    proper subsets of its lines"""
    atoms, _ = truth(S, cuts)
    names = {"g"} | {x for e, r, q in cuts for x in (e, r)}
    idx = [k[1] for k in S.lkey]
    for X in names:
        L = atoms.get(X, set())
        if not L:
            return False
        fps = [frozenset(k for k in L if q in F[idx[k]]) for e, r, q in cuts if r == X]
        if any(f == frozenset(L) for f in fps) or len(set(fps)) < len(fps):
            return False
    return True


def compare(S, cuts, out):
    """(atoms recovered, directed tree recovered, footprints uniform)"""
    atoms, edges_true = truth(S, cuts)
    classes, edges, splits = read_tree(len(S.H), out)
    ok_atoms = sorted(map(sorted, classes)) == sorted(sorted(v) for v in atoms.values() if v)
    if not ok_atoms or len(atoms) != len(classes):
        return ok_atoms and len(atoms) == len(classes), False, footprints_uniform(out, classes)
    name = {i: next(o for o, v in atoms.items() if v == set(c)) for i, c in enumerate(classes)}
    rec = {(name[e] if e is not None else None, name[r]) for e, r in edges}
    return True, rec == edges_true, footprints_uniform(out, classes)


def random_design(r, natoms, heavy=False):
    """a random design with random lost elements and port permutations; heavy: new atoms mostly hang from the first two"""
    d, avail = [], {"g": {("pt", q) for q in range(7)} | {("ln", l) for l in range(7)}}
    perms, lost = [], []
    for j in range(1, natoms):
        hosts = [h for h in (["g", "A1"] if heavy and j > 1 else ["g"] + ["A%d" % i for i in range(1, j)]) if avail.get(h)]
        if not hosts:
            hosts = [h for h in ["g"] + ["A%d" % i for i in range(1, j)] if avail[h]]
        h = r.choice(hosts)
        el = r.choice(sorted(avail[h]))
        avail[h].discard(el)
        x = r.randrange(7)
        avail["A%d" % j] = ({("pt", q) for q in range(7)} | {("ln", l) for l in range(7) if l != x} if el[0] == "pt"
                            else {("pt", q) for q in range(7) if q != x} | {("ln", l) for l in range(7)})
        d.append((h, el))
        perms.append(r.choice(TL.PERMS))
        lost.append(x)
    return d, perms, lost


# ------------------------------------------------------------------------------------------------ the fresh census (BRACE-TREE C)
BTC = ROOT / "proofs/BRACE-TREE-20261105-001C/BRACE-TREE-20261105-001C-P001_reading_the_tree_back_on_fresh_spaces"


def census_spaces():
    """BRACE-TREE C's 111 fresh spaces: its 11 new designs and the 100 three-fold classes of 23 to 26 points (fresh_census.json)"""
    import json
    Fs, Cs = GL.FANO, GL.C58
    ID = (0, 1, 2)
    g = lambda i: ("g", i)  # noqa: E731
    FB, CB = GL.base(*Fs), GL.base(*Cs)
    P4, P5 = GL.plane(GL.PL.prism(4)), GL.plane(GL.PL.prism(5))
    inner = next(q for q in range(7) if q not in Fs[0][0])
    off01 = min(k for k, L in enumerate(Fs[0]) if 0 not in L and 1 not in L)
    off0 = min(k for k, L in enumerate(Fs[0]) if 0 not in L)
    A = lambda n, kind, key: (n, kind, key, Fs, 0, ID)  # noqa: E731
    l0 = next(k for k, L in enumerate(P5.H) if 0 in L)
    designs = [
        (FB, [A("X", "point", g(0)), A("W", "point", g(1)), A("Y", "line", g(off01))]),
        (FB, [A("Y", "line", g(0)), A("V", "line", g(1)), A("Z", "point", ("Y", 1))]),
        (FB, [A("Y", "line", g(0)), A("Y2", "line", ("Y", 2))]),
        (FB, [A("Y", "line", g(0)), A("Y2", "line", ("Y", 2)), A("Y3", "line", ("Y2", 2))]),
        (FB, [A("X", "point", g(0)), A("W", "point", g(1)), A("B", "line", ("W", 1))]),
        (FB, [A("X", "point", g(0)), A("Z", "point", ("X", inner)), A("W", "point", ("X", 3))]),
        (FB, [A("Y", "line", g(off0)), A("X", "point", g(0)), A("Z", "point", ("Y", 1))]),
        (CB, [A("X", "point", g(0)), A("Y", "line", g(3))]),
        (P5, [A("X", "point", g(0)), A("Y", "line", g(l0))]),
        (P5, [A("Y", "line", g(l0)), A("Z", "point", ("Y", 1))]),
        (P4, [A("X", "point", g(0)), A("Z", "point", ("X", inner)), A("Y", "line", g(max(k for k, L in enumerate(P4.H) if 0 not in L)))]),
    ]
    out = [("design %d" % i, GL.build(d)) for i, d in enumerate(designs)]
    for row in json.loads((BTC / "fresh_census.json").read_text()):
        H = [tuple(L) for L in row["lines"]]
        n = 1 + max(p for L in H for p in L)
        signs = [[0, 0, 0] for _ in H]
        if row["twist"] is not None:
            signs[row["twist"][0]][H[row["twist"][0]].index(row["twist"][1])] = 1
        out.append((row["name"], GL.base(H, signs, n)))
    return out


def twin_report(S, exact):
    """how the twin classes of an exact creation map sit against the tight-cut decomposition: kind of space, and a Counter of class
    kinds (exact atom; atom plus glue lines; part of an atom; glue only; spanning two atoms; atom in no class of two or more lines)"""
    owner, types, cuts = DL.BL.braces(S)
    kind = "Fano tree" if set(types) == {"heawood"} else ("with a non-planar non-Heawood brace" if "other" in types else "with plane glue")
    out = {a: {b for b, v in row.items() if v is not None and any(v)} for a, row in exact.items()}
    classes, edges, splits = read_tree(len(S.H), out)
    atoms = collections.defaultdict(set)
    for k in range(len(S.H)):
        if types[owner[k]] == "heawood":
            atoms[owner[k]].add(k)
    glue = {k for k in range(len(S.H)) if types[owner[k]] != "heawood"}
    c = collections.Counter()
    for cl in classes:
        if len(cl) < 2:
            continue
        hit = {owner[k] for k in cl if k not in glue}
        if not hit:
            c["glue-only class"] += 1
        elif len(hit) > 1:
            c["class spanning two atoms"] += 1
        else:
            A = next(iter(hit))
            extra, missing = len(cl & glue), len(atoms[A] - cl)
            c["exact atom" if not extra and not missing else ("atom plus %d glue line" % extra if not missing else
                                                                "part of an atom (%d of its lines)" % len(cl & atoms[A]))] += 1
    c["atoms in no class of two or more lines"] += sum(1 for A, L in atoms.items() if not any(L & cl for cl in classes if len(cl) >= 2))
    c["atoms"] += len(atoms)
    return kind, c
