"""Reading the atoms through glue, for GLUE-READ-20261106-001C.

The two-stage twin rule, from whether creation occurs (for some far side):
1. Twins: two lines that create at each other and at the same other lines. The lines in twin classes of two or more are the atom lines.
2. Atom twins: two atom lines that create at each other and at the same other atom lines (glue lines ignored). Their classes are read
   as the atoms; their number as the genus.
On Fano trees every line is an atom line and the rule is CHAIN-TRANSFER C's twin rule.

An obstruction: if two lines of different atoms create at each other and are creation twins in both directions (the same lines create
at them and they create at the same lines), exchanging them is a symmetry of the yes/no creation relation, so no rule that reads only
that relation can return the atoms.
"""
import collections
import importlib.util
import itertools
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


GRB = ROOT / "proofs/GLUE-READ-20261106-001B/GLUE-READ-20261106-001B-P001_what_plane_glue_does"
G = load("gr_plane_glue_lib", GRB / "plane_glue_lib.py")
PL, TL, GL, DL = G.PL, G.TL, G.GL, G.PL.DL


def two_stage(n, out):
    """(atom lines, classes read as atoms)"""
    first = G.twin_classes(n, out)
    atom_lines = set().union(*[c for c in first if len(c) >= 2])
    return atom_lines, G.twin_classes(n, out, keep=atom_lines, restrict=atom_lines)


def atoms_of(S):
    parts, types, pown, lown, xs = PL.structure(S)
    atoms = collections.defaultdict(set)
    for k in range(len(S.H)):
        if types[lown[k]] == "heawood":
            atoms[lown[k]].add(k)
    return parts, types, lown, xs, atoms


def reads_atoms(cls, atoms, lown, types):
    """the classes holding atom lines are exactly the atoms, one class each (extra glue lines allowed)"""
    allatom = set().union(*atoms.values())
    big = [cl for cl in cls if cl & allatom]
    return (len(big) == len(atoms) and all(len({lown[k] for k in cl if types[lown[k]] == "heawood"}) == 1 for cl in big)
            and all(any(L == (cl & allatom) for cl in big) for L in atoms.values())), big


def twins_across_atoms(n, same, lown, types):
    """some two lines of different atoms that the relation cannot tell apart: same(a, b) decides it"""
    return any(lown[a] != lown[b] and types[lown[a]] == types[lown[b]] == "heawood" and same(a, b)
               for a, b in itertools.combinations(range(n), 2))


def judge(S, exact):
    parts, types, lown, xs, atoms = atoms_of(S)
    n = len(S.H)
    out = G.creates(exact)
    inn = {b: {a for a in range(n) if b in out[a]} for b in range(n)}
    kind = G.kind_of_space(types)
    c = collections.Counter()
    c["spaces"] += 1
    c["Fano atoms"] += len(atoms)
    AL, cls = two_stage(n, out)
    ok, big = reads_atoms(cls, atoms, lown, types)
    c["two-stage rule reads the atoms"] += ok
    allatom = set().union(*atoms.values())
    c["... extra lines in its classes are doubled-square lines"] += all(types[lown[g]] == "doubled square" for cl in cls
                                                                         for g in cl - allatom)
    # the yes/no obstruction, and the full map
    yes_no = twins_across_atoms(n, lambda a, b: b in out[a] and a in out[b] and out[a] - {b} == out[b] - {a}
                                and inn[a] - {b} == inn[b] - {a}, lown, types)
    val = lambda a, b: exact[a].get(b)  # noqa: E731
    full = twins_across_atoms(n, lambda a, b: val(a, b) == val(b, a) and all(val(a, x) == val(b, x) and val(x, a) == val(x, b)
                                                                            for x in range(n) if x not in (a, b)), lown, types)
    c["two lines of different atoms indistinguishable by whether creation occurs"] += yes_no
    c["two lines of different atoms indistinguishable far side by far side"] += full
    if not ok:
        mixed = [cl for cl in big if len({lown[k] for k in cl if types[lown[k]] == "heawood"}) > 1]
        if mixed:
            def planar_neighbours(A):
                return {next(b for b in sides if b != A) for k, sides in xs.items()
                        if A in sides and types[next(b for b in sides if b != A)] == "planar"}
            how = set()
            for cl in mixed:
                ats = sorted({lown[k] for k in cl if types[lown[k]] == "heawood"})
                how.add("merges atoms meeting one planar brace" if set.intersection(*[planar_neighbours(A) for A in ats])
                        else "merges other atoms")
            c["fails: " + "; ".join(sorted(how)) + ("; indistinguishable" if yes_no else "; distinguishable")] += 1
        else:
            c["fails: drops or splits an atom" + ("; indistinguishable" if yes_no else "; distinguishable")] += 1
    import networkx as nx
    g = nx.Graph()
    g.add_nodes_from(range(n))
    g.add_edges_from((a, b) for a, b in itertools.combinations(range(n), 2)
                     if b in out[a] and a in out[b] and all(val(a, x) == val(b, x) for x in range(n) if x not in (a, b)))
    full_cls = [frozenset(cc) for cc in nx.connected_components(g) if len(cc) >= 2]
    c["twins far side by far side read the atoms"] += reads_atoms(full_cls, atoms, lown, types)[0]
    plain = [cl for cl in G.twin_classes(n, out) if len(cl) >= 2]
    c["plain twin rule reads the atoms"] += reads_atoms(plain, atoms, lown, types)[0]
    kept, total = DL.source_blocks(S, {a: {b: (v is not None and any(v),) for b, v in row.items()} for a, row in exact.items()})
    c["source rule counts the atoms"] += len(kept) == len(atoms)
    return kind, c
