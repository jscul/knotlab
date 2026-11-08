"""The spaces of TRISUM-READ-20261107-001: HANDLE-COUNT A's plain edge-atom trisum spaces from seeds 1 to 400.

Each seed gives the trisum brace of FA.trisum_brace (1 + seed % 3 trisums; cubes alone for odd seeds, cubes and prisms for even ones, as
HANDLE-COUNT B), its Pfaffian signing, a minimal signing in its switching class, and a Fano atom on every signed incidence
(FA.edge_atoms). Spaces of more than 60 lines are dropped. HANDLE-COUNT B used seeds 1 to 40; seeds 41 to 400 are new here. Its
T14-decorated spaces attach atoms by 3-edge cuts and are not used.

The generator is not a function of the seed alone. FA.pfaffian_signing walks sets, so the signing it returns, and with it the minimal
signing and the places of the atoms, depends on Python's hash seed (PYTHONHASHSEED); a run over seeds 1 to 400 gives 17 or 18 classes up
to isomorphism, depending on it. The 17 spaces used here (spaces.json) are the classes of one run, each represented by its smallest seed.
Each is reproduced, up to isomorphism, by the generator at its own seed under the hash seed recorded in HASH_SEEDS.
"""
import json
import os
import subprocess
import sys
from pathlib import Path

import networkx as nx

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import tr_lib as TR  # noqa: E402,F401  (sets the import paths of HANDLE-COUNT A and its dependencies)
import families as FA  # noqa: E402

MAX_LINES = 60
POOL = FA.planar_pool()
CUBES = {'cube': POOL['cube']}
HASH_SEEDS = {1: 0, 3: 0, 5: 0, 6: 0, 11: 0, 34: 1, 36: 1, 46: 2, 96: 0, 192: 0, 240: 6, 246: 0, 282: 0, 288: 0, 300: 0, 354: 1, 384: 0}


def edge_atom_space(seed):
    nsum = 1 + seed % 3
    G = FA.trisum_brace(seed, nsum, CUBES if seed % 2 else POOL)
    Hg, kap, nsq = FA.pfaffian_signing(G)
    mn, nu = FA.min_signing(Hg, kap)
    E = FA.edge_atoms(Hg, mn)
    return (seed, nsum, [tuple(l) for l in E]) if len(E) <= MAX_LINES else None


def incidence(H):
    g = TR.incidence(H)
    for v in g:
        g.nodes[v]["k"] = v[0]
    return g


def isomorphic(H1, H2):
    if len(H1) != len(H2):
        return False
    g1, g2 = incidence(H1), incidence(H2)
    if nx.weisfeiler_lehman_graph_hash(g1, node_attr="k", iterations=4) != nx.weisfeiler_lehman_graph_hash(g2, node_attr="k", iterations=4):
        return False
    return nx.is_isomorphic(g1, g2, node_match=lambda x, y: x["k"] == y["k"])


def generated(seeds, hash_seed):
    """{seed: (trisums, lines)} from the generator run in a fresh interpreter under the given hash seed"""
    env = dict(os.environ, PYTHONHASHSEED=str(hash_seed))
    out = subprocess.run([sys.executable, "-B", str(Path(__file__).resolve()), json.dumps(sorted(seeds))], env=env, check=True,
                         capture_output=True, text=True).stdout
    return {int(s): (v[0], [tuple(l) for l in v[1]]) for s, v in json.loads(out.strip().splitlines()[-1]).items() if v is not None}


if __name__ == "__main__":
    made = {s: edge_atom_space(s) for s in json.loads(sys.argv[1])}
    print(json.dumps({s: (r[1], r[2]) if r else None for s, r in made.items()}))
