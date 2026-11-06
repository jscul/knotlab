"""Native relations between lines, and the tight-cut decomposition at the level of lines, for BRACE-TREE-20261105-001.

The native relation of two lines a and b in a space: 'mutual' when removing either creates at the other (some far side), 'one-way'
when only one direction creates (recorded with its direction), 'silent' when neither does. The creation map is genus_lib's
(NATIVE-GENUS-20261104-001A): exact, join method, four census far sides, lines showing fewer than six patterns count as non-creating.

The decomposition: grammar_lib.decompose (THREEFOLD-GRAMMAR A) splits the incidence multigraph along tight cuts into braces; each brace
keeps its own points and lines and a contracted vertex ('X', kind, k) for each cut k it meets. A brace whose contracted vertex at k is a
line lost a line there and emits; one whose contracted vertex is a point lost a point there and receives. At a receiving brace, the cut
lines are its lines through the contracted point.
"""
import collections
import itertools
import sys
from pathlib import Path

import networkx as nx

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "proofs/NATIVE-GENUS-20261104-001A/NATIVE-GENUS-20261104-001A-P001_the_creation_map_splits_by_atom"))
sys.path.insert(0, str(ROOT / "proofs/THREEFOLD-GRAMMAR-20261030-001A/THREEFOLD-GRAMMAR-20261030-001A-P001_fano_leaves_and_planar_glue"))
sys.path.insert(0, str(ROOT / "proofs/THREEFOLD-SPACES-20261030-001A/THREEFOLD-SPACES-20261030-001A-P001_three_fold_spaces_are_built_from_the_fano_plane"))
import genus_lib as GL  # noqa: E402
import grammar_lib as GM  # noqa: E402


def relation(res, a, b):
    """the native relation of lines a and b, read from a's side: 'mutual', 'a creates at b only', 'b creates at a only' or 'silent'"""
    x, y = GL.creates(res, a, b), GL.creates(res, b, a)
    return "mutual" if x and y else ("forward" if x else ("backward" if y else "silent"))


def braces(S):
    """the tight-cut decomposition of S at the level of lines: (line -> brace index, brace types, cuts) where cuts[k] = (emitting brace,
    receiving brace, the receiving brace's cut lines)"""
    adj = GM.multigraph(S.H)
    parts = GM.decompose(adj)
    owner, types, at_cut = {}, [], collections.defaultdict(dict)
    for b, part in enumerate(parts):
        types.append(GM.brace_type(part)[0])
        for v in part:
            if v[0] == "L":
                owner[v[1]] = b
            elif v[0] == "X":
                kind, k = v[1], v[2]
                at_cut[k][b] = (kind, sorted(w[1] for w in part[v] if w[0] == "L"))
    cuts = {}
    for k, sides in at_cut.items():
        (b1, (k1, l1)), (b2, (k2, l2)) = sorted(sides.items())
        if k1 == "L":   # b1 lost a line: it emits; b2 lost a point: it receives, and its lines through that point are the cut lines
            cuts[k] = (b1, b2, l2)
        else:
            cuts[k] = (b2, b1, l1)
    assert len(owner) == len(S.H)
    return owner, types, cuts


def tree(owner, types, cuts):
    """the brace tree as a directed graph: an edge from the emitting to the receiving brace of each cut"""
    t = nx.DiGraph()
    t.add_nodes_from(range(len(types)))
    for k, (e, r, cl) in cuts.items():
        t.add_edge(e, r, cut=k)
    return t
