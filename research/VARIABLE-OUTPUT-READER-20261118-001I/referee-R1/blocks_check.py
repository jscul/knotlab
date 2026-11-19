"""Referee R1 for VARIABLE-OUTPUT-READER-20261118-001I: the intersecting-cycle family of families.json (one, two and four
repetitions), checked for the structural facts the block proof uses: legality, two-fresh joins, the least cut around three or
more sites, an identifying pair for every five- and six-place star, the blocks of the four-place graph (sizes; simple cycle or
not), and the legal triples.

  ../../../.venv/bin/python -B blocks_check.py > referee_i_blocks.json      (from this directory)
"""
import itertools
import json
from collections import Counter

import networkx as nx

import referee_i as RI

fam = json.load(open(RI.FAM / "families.json"))["nonshrinking_intersecting_cycles"]
out = []
for d in fam:
    J, legal, T, s = RI.RG.replay(d["history"])
    n = 1 + max(max(S) for S in J)
    fresh = [sum(1 for x in S if all(x not in Q for Q in J[:k])) for k, S in enumerate(J)]
    two = sum(1 for k in range(1, len(J)) if fresh[k] == 2)
    K, _ = RI.exact_small_K_serial(J, 6)
    ok2 = all(any(K[x][y] == len(S) and not any(z not in S and K[x][z] <= len(S) and K[y][z] <= len(S) for z in range(n))
                  for x, y in itertools.combinations(sorted(S), 2)) for S in J if len(S) in (5, 6))
    four = [k for k, S in enumerate(J) if len(S) == 4]
    G4 = nx.Graph()
    G4.add_nodes_from(four)
    G4.add_edges_from((a, b) for a, b in itertools.combinations(four, 2) if set(J[a]) & set(J[b]))
    blocks = [G4.subgraph(c) for c in nx.biconnected_components(G4) if len(c) > 2]
    out.append({"width": n, "junctions": len(J), "history legal": legal, "two-fresh joins": two,
                "least cut around three or more sites": RI.min_cut_three(T),
                "identifying pairs for every 5- and 6-place star": ok2, "four-place graph a cactus": RI.is_cactus(G4),
                "nontrivial blocks (sites, meetings)": [[b.number_of_nodes(), b.number_of_edges()] for b in blocks],
                "legal triples": len(RI.F.legal_triples(T, J))})
print(json.dumps(out, indent=1))
