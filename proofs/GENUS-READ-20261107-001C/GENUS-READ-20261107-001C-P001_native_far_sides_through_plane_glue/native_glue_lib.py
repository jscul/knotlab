"""Native far sides through plane glue, for GENUS-READ-20261107-001C.

By ticket A, K4^(3), the Fano plane and census 58 do not depend on how they are glued, so their columns of the stored creation maps are
native; census 6's are not. Everything here reads the stored maps through those three far sides only.
"""
import collections
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


FL = load("gr_c_far_lib", ROOT / "proofs/FAR-READ-20261106-001A/FAR-READ-20261106-001A-P001_the_far_side_map/far_lib.py")
AT, G = FL.AT, FL.G
FRESH = ROOT / "proofs/FAR-READ-20261106-001C/FAR-READ-20261106-001C-P001_fresh_spaces/maps.json.gz"


def spaces():
    sv, sm = FL.saved()
    fs, fm = G.load_maps(FRESH)
    return [("saved " + s[0], s[1], s[2], m) for s, m in zip(sv, sm)] + [(s[0], s[1], s[2], m) for s, m in zip(fs, fm)]


def free(v):
    """the gluing-free part of a far-side vector: (K4^(3), the Fano plane, census 58)"""
    return None if v is None else (v[0], v[2], v[3])


def vec_twins(n, out, vec, keep, restrict, cols=False):
    g = nx.Graph()
    g.add_nodes_from(keep)
    for a, b in itertools.combinations(sorted(keep), 2):
        if b in out[a] and a in out[b] and all(vec(a, x) == vec(b, x) for x in restrict if x not in (a, b)) and \
                (not cols or all(vec(x, a) == vec(x, b) for x in restrict if x not in (a, b))):
            g.add_edge(a, b)
    return [frozenset(c) for c in nx.connected_components(g)]


def report(src, nm, S, ex):
    parts, types, lown, xs, atoms = AT.atoms_of(S)
    n = len(S.H)
    out = G.creates(ex)
    inn = {b: {a for a in range(n) if b in out[a]} for b in range(n)}
    v = lambda a, b: free(ex[a].get(b))  # noqa: E731
    first = G.twin_classes(n, out)
    AL = set().union(*[q for q in first if len(q) >= 2])
    allatom = set().union(*atoms.values())
    c = collections.Counter()
    c["spaces"] += 1
    c["Fano atoms"] += len(atoms)
    # atoms act as one on the gluing-free far sides (toward atom lines)
    c["atoms acting as one on the gluing-free far sides"] += sum(all(len({v(a, x) for a in L}) == 1 for x in allatom - L)
                                                                 for L in atoms.values())
    # yes/no twins across atoms
    yn = lambda a, b: b in out[a] and a in out[b] and out[a] - {b} == out[b] - {a} and inn[a] - {b} == inn[b] - {a}  # noqa: E731
    pairs = [(a, b) for a, b in itertools.combinations(range(n), 2)
             if lown[a] != lown[b] and types[lown[a]] == types[lown[b]] == "heawood" and yn(a, b)]
    if pairs:
        c["spaces with lines of two atoms that are yes/no twins"] += 1
    for a, b in pairs:
        c["such pairs"] += 1
        where = []
        if v(a, b) != v(b, a):
            where.append("between them")
        if any(v(a, x) != v(b, x) for x in AL if x not in (a, b)):
            where.append("rows at atom lines")
        if any(v(a, x) != v(b, x) for x in range(n) if x not in AL and x not in (a, b)):
            where.append("rows at other lines")
        if any(v(x, a) != v(x, b) for x in AL if x not in (a, b)):
            where.append("columns from atom lines")
        if any(v(x, a) != v(x, b) for x in range(n) if x not in AL and x not in (a, b)):
            where.append("columns from other lines")
        c["... told apart by the gluing-free far sides"] += bool(where)
        c["... where: " + (", ".join(where) if where else "nowhere")] += 1
    kind = src.split(",")[0] + ", " + G.kind_of_space(types)
    rules = {"yes/no two-stage (GLUE-READ C)": G.twin_classes(n, out, keep=AL, restrict=AL),
             "gluing-free rows on atom lines": vec_twins(n, out, v, AL, AL),
             "gluing-free rows and columns on atom lines": vec_twins(n, out, v, AL, AL, cols=True)}
    for name, cls in rules.items():
        ok, big = AT.reads_atoms(cls, atoms, lown, types)
        c["rule: %s" % name] += ok
        if not ok and name == "gluing-free rows on atom lines":
            merged = any(len({lown[k] for k in cl if k in allatom}) > 1 for cl in big)
            c["rule: %s, failures merging atoms" % name] += merged
            c["rule: %s, failures splitting or dropping" % name] += not merged
    return kind, c
