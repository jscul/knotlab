"""The brace dictionary, for BRACE-TREE-20261105-001B: the place of a pair of lines in the tight-cut decomposition, against their native
relation.

The place of an ordered pair (a, b), with A and B the braces holding a and b:
- the same brace: ('same', type, role of a, role of b, whether two cut lines share a cut), where a line's role is 'cut line' when it
  lies on a cut where its brace receives (its lines through the contracted point) and 'intact' otherwise;
- different braces: ('apart', type of A, type of B, arrows, kinds in between, role of a, role of b). The arrows read the cuts along the
  tree path from A to B: '>' when the cut is crossed in its direction (from the emitting to the receiving brace), '<' against it. A
  line's role here is taken at the cut its brace has on the path: 'emitter' when its brace emits there, otherwise 'cut line' or
  'intact'. Kinds in between are 'atom' (Heawood) or 'glue' (any other brace).
"""
import collections
import sys
from pathlib import Path

import networkx as nx

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "proofs/BRACE-TREE-20261105-001A/BRACE-TREE-20261105-001A-P001_creation_inside_an_atom_and_across_a_cut"))
import brace_lib as BL  # noqa: E402

GL = BL.GL


class Tree:
    def __init__(self, S):
        self.S = S
        self.owner, self.types, self.cuts = BL.braces(S)
        self.u = nx.Graph()
        self.u.add_nodes_from(range(len(self.types)))
        self.edge = {}
        for k, (e, r, cl) in self.cuts.items():
            self.u.add_edge(e, r)
            self.edge[frozenset((e, r))] = (e, r, set(cl))
        self.recv_lines = collections.defaultdict(set)   # brace -> its lines on cuts where it receives
        self.recv_cut = collections.defaultdict(set)     # line -> the cuts where it is a cut line
        for k, (e, r, cl) in self.cuts.items():
            self.recv_lines[r] |= set(cl)
            for x in cl:
                self.recv_cut[x].add(k)

    def kind(self, b):
        return "atom" if self.types[b] == "heawood" else "glue"

    def role_at(self, x, B, other):
        """x's role at the cut between its brace B and the neighbouring brace other"""
        e, r, cl = self.edge[frozenset((B, other))]
        if e == B:
            return "emitter"
        return "cut line" if x in cl else "intact"

    def place(self, a, b):
        A, B = self.owner[a], self.owner[b]
        if A == B:
            ra = "cut line" if a in self.recv_lines[A] else "intact"
            rb = "cut line" if b in self.recv_lines[A] else "intact"
            both = "" if ra == "intact" or rb == "intact" else ("same cut" if self.recv_cut[a] & self.recv_cut[b] else "different cuts")
            return ("same", self.types[A], ra, rb, both)
        path = nx.shortest_path(self.u, A, B)
        arrows = "".join(">" if self.edge[frozenset((u, v))][0] == u else "<" for u, v in zip(path, path[1:]))
        between = tuple(self.kind(x) for x in path[1:-1])
        return ("apart", self.types[A], self.types[B], arrows, between, self.role_at(a, A, path[1]), self.role_at(b, B, path[-2]))


def dictionary(spaces):
    """spaces: list of (label, Space, creation map); returns {place: Counter(relation)} over ordered pairs of distinct lines, and the
    labels where each (place, relation) occurs"""
    table = collections.defaultdict(collections.Counter)
    where = collections.defaultdict(set)
    for label, S, r in spaces:
        t = Tree(S)
        for a in range(len(S.H)):
            for b in range(len(S.H)):
                if a == b:
                    continue
                p = t.place(a, b)
                rel = BL.relation(r, a, b)
                table[p][rel] += 1
                where[(p, rel)].add(label)
    return table, where


def path_types(t, a, b):
    """the brace types strictly between the braces of lines a and b (empty when they are equal or adjacent)"""
    if t.owner[a] == t.owner[b]:
        return ()
    path = nx.shortest_path(t.u, t.owner[a], t.owner[b])
    return tuple(t.types[x] for x in path[1:-1])


def source_blocks(S, r):
    """the reconstruction fixed in this ticket, from native creation alone: within each piece of the creative part (lines joined
    through shared points), the maximal sets of lines that create at one another in both directions (blocks); a block is kept when one of
    its lines is blind to every line any other line of the block is blind to, where a line a is blind to c when c creates at a and a
    does not create at c. Returns the kept blocks (sets of lines) and the number of blocks in all."""
    import itertools as it
    nat = GL.native(S, r)
    V = set(nat["V"])
    blind = {a: frozenset(c for c in V if c != a and BL.relation(r, a, c) == "backward") for a in V}
    kept, total = [], 0
    for piece in nat["line pieces"]:
        m = nx.Graph()
        m.add_nodes_from(piece)
        m.add_edges_from((a, b) for a, b in it.combinations(piece, 2) if BL.relation(r, a, b) == "mutual")
        for K in nx.find_cliques(m):
            total += 1
            if any(all(blind[b] <= blind[a] for b in K) for a in K):
                kept.append(frozenset(K))
    return kept, total
