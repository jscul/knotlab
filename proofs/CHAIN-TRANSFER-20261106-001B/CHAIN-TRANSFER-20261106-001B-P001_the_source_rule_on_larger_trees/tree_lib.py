"""Fano trees for CHAIN-TRANSFER-20261106-001B and C: every tree up to a size, creation by ticket A's theorem, the source rule, the
counterexamples, and exact creation maps.

A design is a list of splices, each a new atom at an element of an existing atom. Without loss of generality:
- the first splice is at point 0 or line 0 of the base;
- each new atom loses its line 0 (when spliced at a point) or its point 0 (at a line);
- the port permutation is the identity.
By ticket A's theorem, creation (the block lemma and the touching rule) depends only on the tree, on each atom's lost elements and on
which lines pass through which lost points. The choices fixed above only relabel an atom or permute ports.
"""
import collections
import importlib.util
import itertools
import sys
from pathlib import Path

import networkx as nx

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CTA = ROOT / "proofs/CHAIN-TRANSFER-20261106-001A/CHAIN-TRANSFER-20261106-001A-P001_creation_along_chains_of_every_length"


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


TL = load("ct_transfer_lib", CTA / "transfer_lib.py")
GL, DL = TL.GL, TL.DL
BL = DL.BL
F = TL.F


# ------------------------------------------------------------------------------------------------ every tree of a size
def designs(natoms):
    out = []

    def rec(seq, avail):
        if len(seq) == natoms - 1:
            out.append(tuple(seq))
            return
        j = len(seq) + 1
        for h in ["g"] + ["A%d" % i for i in range(1, j)]:
            for el in sorted(avail[h]):
                if not seq and el not in (("pt", 0), ("ln", 0)):
                    continue
                nav = {k: set(v) for k, v in avail.items()}
                nav[h].discard(el)
                nav["A%d" % j] = ({("pt", q) for q in range(7)} | {("ln", l) for l in range(1, 7)} if el[0] == "pt"
                                  else {("pt", q) for q in range(1, 7)} | {("ln", l) for l in range(7)})
                rec(seq + [(h, el)], nav)

    rec([], {"g": {("pt", q) for q in range(7)} | {("ln", l) for l in range(7)}})
    return out


def build(design, perms=None, lost=None):
    """the space of a design; cuts: [(emitter, receiver, the receiver's lost point)]"""
    S = GL.base(*GL.FANO)
    cuts = []
    for j, (h, el) in enumerate(design, start=1):
        new = "A%d" % j
        perm = perms[j - 1] if perms else (0, 1, 2)
        x = lost[j - 1] if lost else 0
        if el[0] == "pt":
            S = GL.attach_point(S, (h, el[1]), GL.FANO, x, new, perm)
            cuts.append((new, h, el[1]))
        else:
            S = GL.attach_line(S, (h, el[1]), GL.FANO, x, new, perm)
            cuts.append((h, new, x))
    return S, cuts


def relation(S, cuts):
    """creation by the block lemma and the touching rule, read from the build's own bookkeeping: {a: {b: (bool,)}}"""
    g = nx.Graph()
    g.add_node("g")
    edge = {}
    for e, r, q in cuts:
        g.add_edge(e, r)
        edge[frozenset((e, r))] = (e, r, q)
    paths = dict(nx.all_pairs_shortest_path(g))
    owner, idx = [k[0] for k in S.lkey], [k[1] for k in S.lkey]
    res = {}
    for a in range(len(S.H)):
        row = {}
        for b in range(len(S.H)):
            if a == b:
                continue
            if owner[a] == owner[b]:
                row[b] = (True,)
                continue
            e, r, q = edge[frozenset((owner[b], paths[owner[b]][owner[a]][1]))]
            row[b] = (e == owner[b] or q in F[idx[b]],)
        res[a] = row
    return res


# ------------------------------------------------------------------------------------------------ the source rule (BRACE-TREE B)
def source_rule(S, res, limit=400):
    """the source rule's kept-block count for the first maximum quiet part (dict_lib.source_blocks, as fixed in BRACE-TREE B), and
    for every maximum quiet part (up to limit): (first count, Counter of counts, quiet parts, every quiet part's creative part one piece)"""
    first, total = DL.source_blocks(S, res)
    best, Ps = GL.quiet_parts(S, res, limit=limit)
    counts, one = collections.Counter(), True
    for P in Ps:
        V = [k for k in range(len(S.H)) if k not in P]
        lp, ip = GL.pieces(S, V)
        one &= len(lp) == 1
        Vs = set(V)
        blind = {a: frozenset(c for c in Vs if c != a and BL.relation(res, a, c) == "backward") for a in Vs}
        kept = 0
        for piece in lp:
            m = nx.Graph()
            m.add_nodes_from(piece)
            m.add_edges_from((a, b) for a, b in itertools.combinations(piece, 2) if BL.relation(res, a, b) == "mutual")
            kept += sum(1 for K in nx.find_cliques(m) if any(all(blind[b] <= blind[a] for b in K) for a in K))
        counts[kept] += 1
    return len(first), counts, len(Ps), one


# ------------------------------------------------------------------------------------------------ the counterexamples
L01 = next(k for k, L in enumerate(F) if 0 in L and 1 in L)
NONCOLLINEAR = next(t for t in itertools.combinations(range(7), 3) if not any(set(t) <= set(L) for L in F))


def M1(connecting_line=True, loads=(1, 1)):
    """a receiver (the base) takes cuts from two emitters E1, E2 at its points 0 and 1; each emitter feeds a further receiver (its
    load); the base emits the line through 0 and 1 to a receiver L3"""
    d = [("g", ("pt", 0)), ("g", ("pt", 1))]
    if connecting_line:
        d.append(("g", ("ln", L01)))
    if loads[0]:
        d.append(("A1", ("ln", 3)))
    if loads[1]:
        d.append(("A2", ("ln", 3)))
    return d


def M2(collinear=False):
    """a receiver (the base) takes cuts from three loaded emitters at three of its points, collinear or not"""
    tri = tuple(F[0]) if collinear else NONCOLLINEAR
    return [("g", ("pt", p)) for p in tri] + [("A%d" % (j + 1), ("ln", 3)) for j in range(3)]


# ------------------------------------------------------------------------------------------------ exact creation maps
def exact_row(args):
    """one row of the exact creation map: every solution (point by point), creation at each line by the two-round rule on the real
    near side (PENDANT-LINE A); no contraction and no automaton"""
    S, M = args
    AN = TL.solutions(S.H, S.s, S.n, skip=M)
    out = {}
    for L in range(len(S.H)):
        if L != M:
            Y = list(S.H[L])
            out[L] = TL.verdict_of_near_side(AN, Y, S.s[L], [q for q in range(S.n) if q not in Y])
    return M, out, len(AN)
