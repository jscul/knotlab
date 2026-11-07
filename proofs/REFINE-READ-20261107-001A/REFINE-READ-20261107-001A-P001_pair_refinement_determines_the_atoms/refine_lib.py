"""Colour refinement on the native creation map, for REFINE-READ-20261107-001A.

The native creation map of a space: its lines, and for each ordered pair (a, b) of distinct lines the order-free far-side vector
(K4^(3), the Fano plane, census 58) of removing a and gluing at b, or None when b shows fewer than six patterns (GENUS-READ A: these
far sides do not depend on how a line's points are listed, so the map is native).
- Colour refinement (1-WL) colours lines; pair refinement (folklore 2-WL) colours ordered pairs, starting from atomic types (the
  vectors in both directions). Stable pair colours are the C^3 types of pairs (Cai, Furer and Immerman), and every automorphism of the
  map preserves them.
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


NG = load("rr_native_glue_lib", ROOT / "proofs/GENUS-READ-20261107-001C/GENUS-READ-20261107-001C-P001_native_far_sides_through_plane_glue/"
          "native_glue_lib.py")
G, AT = NG.G, NG.AT


def vertex_refine(n, col):
    """stable 1-WL colours of the lines"""
    c = [0] * n
    while True:
        sig = []
        for v in range(n):
            out = collections.Counter((col(v, u), c[u]) for u in range(n) if u != v)
            inn = collections.Counter((col(u, v), c[u]) for u in range(n) if u != v)
            sig.append((c[v], tuple(sorted(out.items(), key=repr)), tuple(sorted(inn.items(), key=repr))))
        ids = {s: i for i, s in enumerate(sorted(set(sig), key=repr))}
        new = [ids[s] for s in sig]
        if len(set(new)) == len(set(c)):
            return new
        c = new


def pair_refine(n, col):
    """stable folklore 2-WL colours of ordered pairs; the initial colour of (a, b) is its atomic type (col(a, b), col(b, a)), and the
    diagonal has its own"""
    ids = {}
    C = [[ids.setdefault(("d",) if a == b else ("e", col(a, b), col(b, a)), len(ids)) for b in range(n)] for a in range(n)]
    k = len(ids)
    while True:
        sig = {}
        new = [[0] * n for _ in range(n)]
        for a in range(n):
            Ca = C[a]
            for b in range(n):
                s = (Ca[b], tuple(sorted((Ca[c], C[c][b]) for c in range(n))))
                new[a][b] = sig.setdefault(s, len(sig))
        if len(sig) == k:
            return new
        C, k = new, len(sig)


def report(src, nm, S, ex):
    parts, types, lown, xs, atoms = AT.atoms_of(S)
    n = len(S.H)
    allatom = set().union(*atoms.values())
    out = G.creates(ex)
    native = lambda a, b: NG.free(ex[a].get(b))  # noqa: E731
    yesno = lambda a, b: b in out[a]  # noqa: E731
    c = collections.Counter()
    c["spaces"] += 1
    # 1-WL on the native map
    v = vertex_refine(n, native)
    classes = collections.defaultdict(set)
    for x, k in enumerate(v):
        classes[k].add(x)
    c["colour refinement: spaces where a class holds lines of two atoms"] += any(len({lown[x] for x in C_ if x in allatom}) > 1
                                                                                for C_ in classes.values())
    # 2-WL on the native map, and on the yes/no relation
    for name, col in (("native", native), ("yes/no", yesno)):
        P = pair_refine(n, col)
        kinds = collections.defaultdict(set)
        for a in allatom:
            for b in allatom:
                if a != b:
                    kinds[P[a][b]].add(lown[a] == lown[b])
        mixed = any(len(s) > 1 for s in kinds.values())
        c["pair refinement on the %s map: spaces where a pair class holds pairs within and across atoms" % name] += mixed
    # the yes/no obstruction (GLUE-READ C): two lines of different atoms that are twins of the yes/no relation
    inn = {b: {a for a in range(n) if b in out[a]} for b in range(n)}
    c["spaces with yes/no twins across atoms"] += any(
        lown[a] != lown[b] and a in allatom and b in allatom and b in out[a] and a in out[b] and out[a] - {b} == out[b] - {a}
        and inn[a] - {b} == inn[b] - {a} for a, b in itertools.combinations(range(n), 2))
    return G.kind_of_space(types), c
