# Closure of the three-fold-grammar epic

Status: Proved

Ticket `THREEFOLD-GRAMMAR-20261030-001Z`, 2026-10-30. This is a ledger: one line per conclusion, with its novelty label and evidence. It
makes no new claim. The decision note is `research/THREEFOLD-GRAMMAR-20261030-001/the_grammar_of_three_fold_spaces.md`.

Words (2026-11-11). The statements use the literature's words for triple systems, gadgets and drawn substrates: a line is a
knot, a point a distinction, a triangle a copy of the knot, and a contact where copies meet a shared distinction (Intuitions
guide, Glossary). Reworded under the owner's language rule: three-fold spaces are three-regular contradictions; a Fano atom is a Fano piece; the earlier text is in git history.

## Conclusions

| # | Conclusion (standard vocabulary) | Novelty | Evidence |
| --- | --- | --- | --- |
| 1 | The approved grammar (Fano blocks, splices, odd cycles) is incomplete. Twisted 14-point pieces on three skew edges of the cube give a 43-point connected 3-regular triple system, minimally not 2-colourable, whose tight-cut decomposition contains the cube. Splices and cycles of Fano blocks only produce Heawood graphs and doubled squares. | no overlap found | A-P001, Theorem 1 |
| 2 | In the tight-cut decomposition of such a system, every piece is cubic, a brace with a repeated incidence is the doubled square, every leaf is simple with at most one twist at its contracted vertex, and every brace carries a Pfaffian signing. | specialization of Lovász and RST; folklore risk moderate | A-P001, Theorem 2 |
| 3 | In a Pfaffian brace other than the Heawood graph, every 4-cycle is edge-disjoint from another, and a non-planar one has three pairwise edge-disjoint 4-cycles. So a brace with a Pfaffian signing negating at most one edge is the Heawood graph, untwisted. | lemma stated by Gorsky–Johanni–Wiederrecht 2024 (proof independent); the one-twist consequence: no overlap found | A-P001, Lemma 3, Theorem 4 |
| 4 | Every leaf is a Fano plane minus a line or minus a point. So every non-2-colourable connected 3-regular triple system other than the Fano plane contains two vertex-disjoint such pieces. | no overlap found; follows quickly from RST | A-P001, Theorem 5 |
| 5 | Every sign-nonsingular signed cubic multi-system becomes such a system when its signed points get twisted 14-point pieces and its repeated points get Fano blocks. So every planar cubic bipartite graph is glue (cube 43, prism 45, truncated octahedron 90 points). | no overlap found | A-P001, Theorem 6 |
| 6 | SAT census of connected non-2-colourable cubic multi-systems up to 10 points: 160 untwisted and 2,492 twisted classes. All match conclusions 2–4. The only non-planar glue brace is the trisum of three cubes, which reaches a 35-point system. | no overlap found | B-P001, Theorem 1 |
| 7 | Below 23 points such systems have exactly 7, 13, 19, 21 or 22 points (1, 1, 4, 1, 1 classes; 3 at 19 up to duality), and twisted ones 14, 15, 18, 20, 21 or 22 points (1, 1, 1, 11, 7, 3). Independent SAT at 14 points agrees. | no overlap found | B-P001, Theorems 5–6 |

## Recommendation

**Continue**, as a fresh epic: the surfaces of three-regular contradictions (2/3).
- **The task.** Embed each space's incidence graph in a closed orientable surface built from its decomposition: spheres for planar glue,
  tori for Fano pieces, connected sums at splices. Test whether the genus equals the number of Fano pieces.
- **The first discriminator.** A scratch probe already answers it: the 13-point splice has genus exactly 2, the number of its Fano pieces.
  This is not evidence. Next would be the twisted cube and the 35-point space with trisum glue.
- **Status.** Deferred to the owner. The decision note has the full assessment.
