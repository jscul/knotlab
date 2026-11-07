"""Uniform rules on the native creation map, for REFINE-READ-20261107-001B.

All rules start from GLUE-READ C's first step: lines in yes/no twin classes of two or more are the atom lines (AL). Then:
- yes/no two-stage: yes/no twins among atom lines (GLUE-READ C);
- native row twins: lines of AL that create at each other and send the same order-free vector to every other line of AL (GENUS-READ C),
  classes = connected components;
- maximal twin cliques: the maximal cliques of that twin relation;
- refined twins: native row twins whose stable pair class (ticket A) consists of native row twins only;
- compatible twins: native row twins that are also compatible at glue lines (at no line outside AL do both create with different
  order-free vectors).
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


RF = load("rr_b_refine_lib", ROOT / "proofs/REFINE-READ-20261107-001A/REFINE-READ-20261107-001A-P001_pair_refinement_determines_the_atoms/"
          "refine_lib.py")
NG, G, AT = RF.NG, RF.G, RF.AT


def components(nodes, edges):
    g = nx.Graph()
    g.add_nodes_from(nodes)
    g.add_edges_from(edges)
    return [frozenset(c) for c in nx.connected_components(g)], g


def report(src, nm, S, ex):
    parts, types, lown, xs, atoms = AT.atoms_of(S)
    n = len(S.H)
    allatom = set().union(*atoms.values())
    out = G.creates(ex)
    col = lambda a, b: NG.free(ex[a].get(b))  # noqa: E731
    first = G.twin_classes(n, out)
    AL = set().union(*[q for q in first if len(q) >= 2])
    twin = {}
    for a, b in itertools.combinations(sorted(AL), 2):
        twin[(a, b)] = b in out[a] and a in out[b] and all(col(a, x) == col(b, x) for x in AL if x not in (a, b))

    def compat(a, b):
        for g in range(n):
            if g in AL or g in (a, b):
                continue
            u, v = col(a, g), col(b, g)
            if u != v and u is not None and v is not None and any(u) and any(v):
                return False
        return True

    P = RF.pair_refine(n, col)
    byclass = collections.defaultdict(list)
    for a, b in itertools.permutations(sorted(AL), 2):
        byclass[P[a][b]].append(twin[tuple(sorted((a, b)))])
    pure = {k for k, v in byclass.items() if all(v)}
    tw_edges = [e for e, t in twin.items() if t]
    rules = {}
    rules["yes/no two-stage (GLUE-READ C)"] = G.twin_classes(n, out, keep=AL, restrict=AL)
    rules["native row twins (GENUS-READ C)"], tg = components(AL, tw_edges)
    cliques = [frozenset(q) for q in nx.find_cliques(tg)]
    rules["maximal twin cliques"] = cliques
    rules["native row twins vetoed by pair refinement"], _ = components(AL, [(a, b) for a, b in tw_edges if P[a][b] in pure and P[b][a] in pure])
    rules["native row twins compatible at glue lines"], _ = components(AL, [(a, b) for a, b in tw_edges if compat(a, b)])
    c = collections.Counter()
    c["spaces"] += 1
    c["the native twin relation is an equivalence (its maximal cliques are disjoint)"] += sum(len(q) for q in cliques) == len(AL)
    for name, cls in rules.items():
        ok, big = AT.reads_atoms(cls, atoms, lown, types)
        c["rule reads the atoms: " + name] += ok
        if not ok:
            merged = any(len({lown[k] for k in cl if k in allatom}) > 1 for cl in big)
            c["rule fails by merging atoms: " + name] += merged
    # the regularity: compatibility at glue lines, for native row twins among Fano-atom lines
    for (a, b), t in twin.items():
        if t and a in allatom and b in allatom:
            side = "within an atom" if lown[a] == lown[b] else "across atoms"
            c["native row twins %s" % side] += 1
            c["... compatible at glue lines, %s" % side] += compat(a, b)
    # merged atoms: two atoms all of whose cross pairs are native row twins
    c["spaces where two atoms are joined by complete twinship"] += any(
        all(twin.get(tuple(sorted((a, b))), False) for a in A_ for b in B_)
        for (ka, A_), (kb, B_) in itertools.combinations(atoms.items(), 2) if set(A_) <= AL and set(B_) <= AL)
    return G.kind_of_space(types), c
