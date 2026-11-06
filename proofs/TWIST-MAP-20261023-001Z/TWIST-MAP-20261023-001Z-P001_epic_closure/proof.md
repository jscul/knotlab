# Closure of the twist-map epic

Status: Proved

Epic `TWIST-MAP-20261023-001` closed on 2026-10-23. This is a ledger: one line per conclusion, with its novelty label and evidence. It
makes no new claim. The decision note is `research/TWIST-MAP-20261023-001/twist_map.md`.

## Conclusions

| # | Conclusion | Novelty | Evidence |
| --- | --- | --- | --- |
| 1 | On every closed orientable surface, the number of orientations whose cyclic edges form a given skeleton factorizes in each twist as c times A. c counts orientations of the skeleton with every skeleton edge cyclic; A counts acyclic orientations of the graph with each cluster shrunk to a point, where an odd cluster is a single node. Series edges inside clusters and parallel edges outside can be merged, and twists whose reduced pieces are isomorphic up to switching give equal counts, skeleton by skeleton. c and A are T(0, 2) and T(2, 0) of the signed graph's frame matroid restricted to the skeleton and contracted by it. | The signed-graph case of a classical oriented-matroid decomposition; high folklore risk; the use for twist relations is new to the program | `TWIST-MAP-20261023-001A-P001`, Theorems 1 and 2, Corollary 1, Remark 6 |
| 2 | The boundary circles of a cluster's neighbourhood span exactly the radical of its lattice, so the duals of the radicals of a label's odd clusters (the wall group) preserve its count, for clusters of any rank. Automorphisms act on twists and labels, and on the L-shaped genus-2 tilings planar duality relates no two counts of one surface. | New to the program; moderate folklore risk for the technique | `…001A-P001`, Lemma W, Corollary 3, Proposition 4, Remark 5 |
| 3 | On genus-2 surfaces, every equality predicted by walls and automorphisms is exact, but they leave 31 exact equalities (counts of at least 1000) unexplained on the four independent fresh surfaces. Two roster surfaces were turned copies of others. | A recorded computation | `TWIST-MAP-20261023-001B-E001`, P1 and P2 |
| 4 | Every unexplained equality holds skeleton by skeleton. 25 of 31 are explained by isomorphic reduced pieces, often by symmetries of the shrunken graph that the surface lacks. The other 6, on L(3,1,3,1), are not: on 48 of their skeletons the shrunken graphs have equal acyclic counts without being isomorphic or Tutte-equivalent. The frozen verdict is partially supported. | A recorded computation; the residue is unexplained | `…001B-E001`, P3 and the decision note's post-hoc check |

## Challenged assumptions

The decision note records five workspace assumptions this epic challenges:
- that lattice symmetry, planar duality and walls explain every exact twist relation;
- that the unexplained equalities are coincidences;
- that matching pieces explain every relation walls and symmetries miss;
- that walls need the surface's cyclic cover;
- that planar duality relates twists within a surface.

## Recommendation

**Continue at three places: dual pairs for three-place lines.**
- **The question.** Shared with `TRIPLE-TWIST-20261023-001`: test whether the shielding identity of two-literal lone loops holds for
  the winding contradictions of three-place tiling worlds.
- **Interest:** 2/3.
- **Alternatives:** the residual relations, equal acyclic counts without isomorphism (1/3), and a note (1/3).
- **Execution:** deferred to the owner.
