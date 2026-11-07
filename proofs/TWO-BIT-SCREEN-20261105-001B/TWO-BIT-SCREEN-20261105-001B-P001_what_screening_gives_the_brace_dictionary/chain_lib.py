"""Reduced spaces of Fano atoms, for TWO-BIT-SCREEN-20261105-001B.

Contracting every part of a space built from Fano atoms that lies off the tree path between two atoms leaves a chain: the closures of the
path's atoms, glued at the path's cuts. A chain of two atoms is the Fano plane with an atom at one point (13 points); a chain of three is
a middle Fano plane with atoms at two of its elements (19 points). Here every such chain is built: every base element, every atom element
removed and every port permutation for two atoms; for three atoms, the four kinds of element pairs (point/point, line/line, point/line
incident or not) and every pair of port permutations.
"""
import collections
import itertools
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "proofs/BRACE-TREE-20261105-001B/BRACE-TREE-20261105-001B-P001_the_brace_dictionary"))
import dict_lib as DL  # noqa: E402

GL, BL = DL.GL, DL.BL
F = GL.FANO
PERMS = list(itertools.permutations(range(3)))


def two_specs():
    return [(p, li, perm) for p in range(7) for li in range(7) for perm in PERMS]


def build_two(spec):
    p, li, perm = spec
    return GL.attach_point(GL.base(*F), ("g", p), F, li, "E", perm)


def three_specs(removed=(0,)):
    lines = F[0]
    l_through0 = next(k for k, L in enumerate(lines) if 0 in L)
    l_off0 = next(k for k, L in enumerate(lines) if 0 not in L)
    l_second = next(k for k, L in enumerate(lines) if k != l_through0)
    kinds = {"two points (siblings)": (("point", 0), ("point", 1)),
             "two lines (co-receivers)": (("line", l_through0), ("line", l_second)),
             "a point and a line through it (chain)": (("point", 0), ("line", l_through0)),
             "a point and a line off it (chain)": (("point", 0), ("line", l_off0))}
    return [(kind, e1, e2, p1, p2, x1, x2) for kind, (e1, e2) in kinds.items() for p1 in PERMS for p2 in PERMS
            for x1 in removed for x2 in removed]


def build_three(spec):
    kind, e1, e2, p1, p2, x1, x2 = spec
    S = GL.base(*F)
    for name, (el, idx), perm, x in (("A", e1, p1, x1), ("B", e2, p2, x2)):
        S = (GL.attach_point if el == "point" else GL.attach_line)(S, ("g", idx), F, x, name, perm)
    return S


def matrices(spaces, pool, chunksize=4):
    """creation maps of a list of spaces, computed row by row in the pool"""
    tasks = [(S, M) for S in spaces for M in range(len(S.H))]
    rows = pool.map(GL.row_task, tasks, chunksize=chunksize)
    out, k = [], 0
    for S in spaces:
        out.append(dict(rows[k:k + len(S.H)]))
        k += len(S.H)
    return out


def place_table(spaces, maps):
    """{place: Counter(relation)} over ordered pairs of distinct lines"""
    table = collections.defaultdict(collections.Counter)
    for S, r in zip(spaces, maps):
        t = DL.Tree(S)
        for a in range(len(S.H)):
            for b in range(len(S.H)):
                if a != b:
                    table[t.place(a, b)][BL.relation(r, a, b)] += 1
    return table


def brace_tree_dictionary():
    """BRACE-TREE B's dictionary: {place: Counter(relation)}"""
    d = json.loads((ROOT / "proofs/BRACE-TREE-20261105-001B/BRACE-TREE-20261105-001B-P001_the_brace_dictionary/dictionary.json")
                   .read_text())
    out = {}
    for e in d:
        p = e["place"]
        key = tuple(tuple(x) if isinstance(x, list) else x for x in p)
        out[key] = collections.Counter(e["relations"])
    return out


def name_place(p):
    if p[0] == "same":
        return "same atom: %s to %s%s" % (p[2], p[3], (" (%s)" % p[4]) if p[4] else "")
    return "atoms %s apart, arrows %s: %s to %s" % (len(p[3]), p[3], p[5], p[6])
