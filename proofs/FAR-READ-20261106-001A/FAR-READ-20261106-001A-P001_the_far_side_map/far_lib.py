"""The far-side map, for FAR-READ-20261106-001A.

The creation map records, for a removal a and a gluing line b, which of the four census far sides create (K4^(3), census 6, the Fano
plane, census 58), or that b shows fewer than six patterns. These helpers read the 191 exact maps of GLUE-READ-20261106-001B.
"""
import collections
import importlib.util
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


GRC = ROOT / "proofs/GLUE-READ-20261106-001C/GLUE-READ-20261106-001C-P001_reading_the_atoms_through_glue"
AT = load("fr_atoms_lib", GRC / "atoms_lib.py")
G, PL = AT.G, AT.PL
NAMES = ("K4^(3)", "census 6", "the Fano plane", "census 58")


def code(v):
    return "-" if v is None else "".join("KcFC"[i] if x else "." for i, x in enumerate(v))


def saved():
    return G.load_maps(AT.GRB / "maps.json.gz")


def structure(S, ex):
    """counts of far-side vectors by kind of gluing line, and whether each atom acts as one from outside"""
    parts, types, lown, xs, atoms = AT.atoms_of(S)
    n = len(S.H)
    allatom = set().union(*atoms.values())
    c = collections.Counter()
    for a in range(n):
        for b, v in ex[a].items():
            kind = "atom line" if b in allatom else "glue line"
            c[("vector at a gluing %s" % kind, code(v))] += 1
    # each atom acts as one from outside: every atom line outside it receives the same vector from each of its lines
    for A, L in atoms.items():
        out_atom = allatom - L
        one = all(len({ex[a].get(x) for a in L}) == 1 for x in out_atom)
        c[("atoms", "act as one on atom lines outside")] += one
        c[("atoms", "act as one on glue lines")] += all(len({ex[a].get(x) for a in L}) == 1 for x in set(range(n)) - allatom)
        c[("atoms", "seen alike by every atom line outside (columns)")] += all(len({ex[x].get(a) for a in L}) == 1 for x in out_atom)
        c[("atoms", "count")] += 1
    return c
