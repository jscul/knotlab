"""Placements in one switching class, for SWITCH-READ-20261108-001A.

HANDLE-COUNT A's generator builds a plain edge-atom space from a trisum brace (the glue): a Pfaffian signing of the glue, a signing
with fewest signs in its switching class, and a Fano atom on every signed incidence (FA.edge_atoms). The Pfaffian signing walks
sets, so which minimal signing it returns depends on Python's hash seed (TRISUM-READ-20261107-001A). Its glue does not.
- placements(): for each of TRISUM-READ's 17 seeds and hash seeds 0 to 23, the glue, both signings and the space, generated in a fresh
  interpreter per hash seed.
- A placement class is a class of the generated spaces up to isomorphism. Two placements are compared through their native creation
  maps (each ordered pair of lines carries the order-free far-side vector of removing the first and gluing at the second, or
  degenerate): the block of glue lines, which keep their indices in every placement, and the whole map, with the glue's lines fixed or
  under any bijection.
"""
import json
import os
import subprocess
import sys
from pathlib import Path

import networkx as nx
from networkx.algorithms import isomorphism as iso

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2] if (HERE.parents[2] / "AGENTS.md").exists() else Path.cwd()
TRA = ROOT / "proofs/TRISUM-READ-20261107-001A/TRISUM-READ-20261107-001A-P001_junctions_in_the_native_creation_map"
TRB = ROOT / "proofs/TRISUM-READ-20261107-001B/TRISUM-READ-20261107-001B-P001_frozen_predictions_on_larger_trisum_spaces"
TRC = ROOT / "proofs/TRISUM-READ-20261107-001C/TRISUM-READ-20261107-001C-P001_one_size_past_four_junctions"
sys.path.insert(0, str(TRA))
import family_lib as FAM  # noqa: E402

HASH_SEEDS = range(24)
GEN = r"""
import json, sys
sys.path.insert(0, %r)
import family_lib as FAM
FA = FAM.FA
out = {}
for s in json.loads(sys.argv[1]):
    G = FA.trisum_brace(s, 1 + s %% 3, FAM.CUBES if s %% 2 else FAM.POOL)
    Hg, kap, nsq = FA.pfaffian_signing(G)
    mn, nu = FA.min_signing(Hg, kap)
    out[s] = {"glue": [list(l) for l in Hg], "pfaffian": sorted(map(list, kap)), "minimal": sorted(map(list, mn)),
              "lines": [list(l) for l in FA.edge_atoms(Hg, mn)]}
print(json.dumps(out))
""" % str(TRA)


def generate(seeds, hash_seed):
    env = dict(os.environ, PYTHONHASHSEED=str(hash_seed))
    out = subprocess.run([sys.executable, "-B", "-c", GEN, json.dumps(sorted(seeds))], env=env, check=True, capture_output=True,
                         text=True, cwd=str(ROOT)).stdout
    return {int(s): v for s, v in json.loads(out.strip().splitlines()[-1]).items()}


def incidence_of_glue(glue):
    g = nx.Graph()
    for i, l in enumerate(glue):
        for p in l:
            g.add_edge(("L", i), ("P", p))
    return g


def incidences(signing):
    return {frozenset((("L", i), ("P", p))) for i, p in signing}


def is_coboundary(g, E):
    """E (a set of edges of g) is the edge set of a cut: some 2-colouring makes exactly the edges of E bichromatic"""
    col = {}
    for s0 in g:
        if s0 in col:
            continue
        col[s0] = 0
        stack = [s0]
        while stack:
            u = stack.pop()
            for w in g[u]:
                c = col[u] ^ (frozenset((u, w)) in E)
                if w not in col:
                    col[w] = c
                    stack.append(w)
                elif col[w] != c:
                    return False
    return True


def free(v):
    return None if v is None else (bool(v[0]), bool(v[2]), bool(v[3]))


def table(m):
    """(number of lines, {(a, b): order-free vector or None})"""
    return len(m["lines"]), {(int(a), int(b)): free(v) for a, r in m["rows"].items() for b, v in r["row"].items()}


def glue_block_differences(ta, tb, g):
    return sorted((a, b) for a in range(g) for b in range(g) if a != b and ta[(a, b)] != tb[(a, b)])


def profiles(n, t):
    """per line, the multisets of vectors in its row and in its column (an invariant of the coloured digraph)"""
    import collections
    return [(tuple(sorted(collections.Counter(str(t[(a, b)]) for b in range(n) if b != a).items())),
             tuple(sorted(collections.Counter(str(t[(b, a)]) for b in range(n) if b != a).items()))) for a in range(n)]


def isomorphic_maps(n, ta, tb, g, fix_glue):
    """an isomorphism of the coloured complete digraphs, glue lines to glue lines (each to itself if fix_glue); returns it or None.
    Line profiles decide most cases: an isomorphism keeps them, so differing profiles rule it out; otherwise VF2 searches with the
    profiles as vertex colours."""
    pa, pb = profiles(n, ta), profiles(n, tb)
    if fix_glue:
        if pa[:g] != pb[:g] or sorted(pa[g:]) != sorted(pb[g:]):
            return None
    elif sorted(pa[:g]) != sorted(pb[:g]) or sorted(pa[g:]) != sorted(pb[g:]):
        return None
    def graph(t, prof):
        G = nx.DiGraph()
        for a in range(n):
            G.add_node(a, c=(("glue", a) if (fix_glue and a < g) else ("glue" if a < g else "atom"), prof[a]))
        for (a, b), v in t.items():
            G.add_edge(a, b, c=str(v))
        return G
    GM = iso.DiGraphMatcher(graph(ta, pa), graph(tb, pb), node_match=lambda x, y: x["c"] == y["c"],
                            edge_match=lambda x, y: x["c"] == y["c"])
    return GM.mapping if GM.is_isomorphic() else None


def where_they_differ(n, ta, tb, g):
    """per glue line, does the multiset of vectors at it from atom removals change, and does the multiset from it at atom lines"""
    import collections
    C = collections.Counter
    at_glue = [a for a in range(g) if C(ta[(b, a)] for b in range(g, n)) != C(tb[(b, a)] for b in range(g, n))]
    from_glue = [a for a in range(g) if C(ta[(a, b)] for b in range(g, n)) != C(tb[(a, b)] for b in range(g, n))]
    return {"glue lines whose column from atom removals changes": at_glue, "glue lines whose row to atom lines changes": from_glue}
