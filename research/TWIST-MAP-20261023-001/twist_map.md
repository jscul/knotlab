# The complete map of twist relations on genus 2

Epic `TWIST-MAP-20261023-001`, closed 2026-10-23.

## The question

The owner asked for both open options from the shielding epic, this one and the three-literal check (`TRIPLE-TWIST-20261023-001`). This
one asks for "the complete map of exact twist relations on genus 2":
- do lattice symmetry, planar duality and walls explain every exact relation between twists?
- the owner framed this as the "harmonies" thread, expected to give a clear yes or no.

**What an exact relation is here.** An event is the full cyclic structure of an orientation in a twisted sector: for each cluster of
edges on directed cycles, its parity under the twist and its period lattice. A relation is an exact equality between the numbers of
orientations with one event under two twists.

**The evidence:**
- [Where a twist can enter a count](../../proofs/TWIST-MAP-20261023-001A/TWIST-MAP-20261023-001A-P001_local_factorization/proof.md)
  (A, proof);
- [The map on genus-2 surfaces](../../experiments/TWIST-MAP-20261023-001B/TWIST-MAP-20261023-001B-E001_genus_two_map/contract.json)
  (B, confirmatory experiment;
  [result](../../artifacts/TWIST-MAP-20261023-001B/TWIST-MAP-20261023-001B-E001_genus_two_map/result.json));
- **Scoping (scratch, not evidence):** exhaustive labelled counts on L(2,2,2,2) and L(3,1,2,2), a pants-gluing analysis of a
  three-loop event, and the calibration of the mechanism on L(3,1,2,2).

## Outcome in one paragraph

**The answer to the question is no.**
- **What walls and symmetries do.** Walls (now proved for clusters of any rank) and the tiling's automorphisms predict only true
  equalities.
- **What duality does.** Planar duality relates no two counts of one genus-2 surface.
- **What they leave.** On the independent fresh surfaces they leave 31 exact equalities with counts of at least 1000 unexplained.

**Every one of them is local, but not every one is an isomorphism.**
- **Why local (A).** For a fixed skeleton (the set of cyclic edges) the count is a product of two factors:
  - the orientations of the skeleton in which every skeleton edge is cyclic;
  - the acyclic orientations of the graph with each cluster shrunk to a point.

  So a twist enters a count only through these two small pieces.
- **What the experiment found (B).** All 31 equalities hold separately on every skeleton.
- **Isomorphism explains 25.** On every skeleton, the two twists' pieces match up to switching, after merging series edges inside
  clusters and parallel edges outside.
- **The other 6 (all on one surface, L(3,1,3,1)).** On 48 of their skeletons, the clusters match, but the shrunken graphs are
  neither isomorphic nor matroid-isomorphic. Their Tutte polynomials differ. They agree only in the one number that matters there,
  the count of acyclic orientations.

That last mechanism is not explained, so the frozen verdict is "partially supported".

## The answer to the question, layer by layer

| Mechanism | What it explains | Status |
| --- | --- | --- |
| Automorphisms of the tiling | relations between twists and events moved by a symmetry | Proved (A, Proposition 4); exact on every surface (B, P1) |
| Walls | the duals of the radicals of the odd clusters' lattices (the wall group), for clusters of any rank | Proved (A, Corollary 3, via Lemma W); exact on every surface (B, P1 and the wall controls) |
| Planar duality | nothing within one genus-2 surface: the dual graph has a face of degree 12 and no vertex of degree 12 | Proved (A, Remark 5) |
| Matching pieces (isomorphism up to switching, after the merges) | 25 of the 31 remaining equalities on the independent fresh surfaces; all 41 on the scoping surfaces | Theorem (A, Theorem 2); measured (B) |
| Equal acyclic counts of different shrunken graphs | the last 6, on 48 skeletons of L(3,1,3,1) | Measured, not explained |

## The map (B, partially supported)

| Surface (edges) | Automorphisms | Events | Unexplained by walls and symmetries | Explained by matching pieces | Skeletons checked, by how the pieces match |
| --- | --- | --- | --- | --- | --- |
| L(2,2,2,2) (24), scoping | 8 | 206 | 4 | 4 | 8 outside isomorphic |
| L(3,1,2,2) (28), scoping | 4 | 318 | 37 | 37 | 158 same, 18 outside isomorphic, 44 clusters isomorphic |
| L(2,1,2,3) (24) | 4 | 224 | 8 | 8 | 42 same, 6 outside isomorphic |
| L(2,1,3,2) (26) | 4 | 256 | 7 | 7 | 160 same |
| L(2,3,2,2) (28) | 4 | 300 | 2 | 2 | 4 outside isomorphic |
| L(3,1,3,1) (30) | 8 | 281 | 14 | 8 | 544 same, 48 with no isomorphism |
| *L(2,2,3,1) (28): L(3,1,2,2) turned* | 4 | 318 | 37 | 37 | as L(3,1,2,2) |
| *L(2,2,2,3) (28): L(2,3,2,2) turned* | 4 | 300 | 2 | 2 | as L(2,3,2,2) |

**How to read it.**
- **Unexplained** counts the pairs of twists with the same event and equal counts of at least 1000 that walls and automorphisms do not
  relate. All of them, on every surface, hold skeleton by skeleton.
- **The pieces column** says how the two twists' pieces match on each skeleton of those pairs:
  - **"same"**: both pieces are identical up to switching;
  - **"outside isomorphic"**: the shrunken graphs are isomorphic by a non-trivial map;
  - **"clusters isomorphic"**: the series-reduced clusters are isomorphic but not identical.

**Two duplicated surfaces.** An explicit isomorphism of the tilings shows each is another roster surface turned by a quarter, and the
multisets of all their counts are identical (776 and 922 entries). Their rows add no independent evidence:
- L(2,2,3,1) is the scoping surface L(3,1,2,2);
- L(2,2,2,3) is L(2,3,2,2).

The decision rests on the four other fresh surfaces.

**How the run was checked.**
- **Controls:** totals, the swap-invariance flag, the halving, per-skeleton sums, 20 wall pairs per surface related by the identity on
  every skeleton, and soundness. Across 59,248 checked skeletons, no skeleton whose pieces match has unequal counts. Also the
  factorization by brute force on 240 sampled skeletons.
- **The independent checker:** with its own surface construction, classification, closure, shrinking and isomorphism search, it
  - enumerated L(2,1,2,1) itself;
  - reproduced every closure and every list of unexplained equalities;
  - recomputed 824 skeleton relations without disagreement;
  - confirmed the factorization samples and the verdict.
- **Time.** The run took 3232 s against a 10800 s budget. A first launch was killed by the session's background limit after six rows
  and was relaunched unchanged.

## Where the mechanism fell short

**The six equalities on L(3,1,3,1).** They are two orbits under the surface's symmetries:
- 434952 = 434952 for four pairs of twists, on 10 of 101 skeletons;
- 203328 = 203328 for two pairs, on 4 of 60 skeletons.

On each such skeleton the clusters are identical, so the equality is an equality of acyclic counts of two different shrunken graphs.

**One of them, as signed graphs.**
- **The shape.** Two cluster points and two vertices, seven merged edges.
- **The difference.** The twists differ on a single edge at a cluster point that carries an odd self-loop.
- **The acyclic counts** are both 54.
- **The rest of the Tutte polynomial differs.** Bases: 20 against 21. Totally cyclic orientations: 14 against 18.

**A post-hoc test, not evidence.** A natural rule (an odd self-loop at a point makes the twist of any other edge there invisible) is
false in general. It changed the count in 141 of 271 random small signed graphs. The mechanism behind these six is open.

## Three examples of matching pieces

- **Three even loops, h1, h2 and h2 − h1 (a hidden symmetry).**
  - **The counts.** On L(3,1,2,2), 69120 orientations have exactly these three clusters in each of the twists dual to h1 and dual to
    h2. No automorphism of that surface swaps h1 and h2.
  - **Why they agree.** The loops cut the surface into two pairs of pants. With each loop shrunk to a point, each pair of pants
    becomes a small graph with an automorphism swapping the h1 and h2 points. The twist enters only through how the two pants are
    glued at the three points.
  - **Found first in scoping.** The gluing data of all four twists, compared directly, are symmetric under that swap.
- **One odd cluster with a rank-3 lattice (series merging).**
  - **The cluster.** It is a bouquet of a 5-cycle, a 2-cycle and a loop at one vertex. Two twists make different cycles odd: the
    5-cycle and the loop in one, the 2-cycle and the loop in the other.
  - **Why they agree.** The count of orientations with every edge cyclic does not see cycle lengths: series edges must point the same
    way. After merging, both twists give one vertex with two odd loops and one even loop.
  - **Not an isomorphism.** The two clusters are not isomorphic as signed graphs, and their Tutte polynomials differ. Only after
    merging do they match.
- **Two even clusters with mixed bundles (outside identity).**
  - **The counts.** On L(2,1,3,2), 103152 = 103152 for twists differing by the dual of h1, on 55 skeletons.
  - **Why they agree.** Vertices touching the h1 loop from both sides join its point by edges of both twists. A merged bundle carrying
    both twists cannot see a change of twist on one side.

## The proofs (A) in plain terms

- **The factorization.** Every orientation splits uniquely into its cyclic part (the edges on directed cycles) and the rest. The rest
  must be acyclic once the cycles are contracted.
  - **Counting.** Counting orientations with a given cyclic part is counting the two pieces separately.
  - **The classical form.** For oriented matroids this is the decomposition of a reorientation into a totally cyclic restriction and
    an acyclic contraction. The two counts are Las Vergnas's T(0, 2) and T(2, 0) of the signed graph's frame matroid, which the check
    confirms.
- **Odd clusters are points with one node.** Their two sheets are joined, so whichever sheet an outside edge reaches is irrelevant.
  That is exactly what a wall is.
  - **The wall group.** It comes from the boundary circles of the cluster's neighbourhood. Their classes span the radical of the
    cluster's lattice (Lefschetz duality), and each circle's crossing edges all touch the odd point.
- **The merges.**
  - **Parallel edges outside** must point the same way in an acyclic orientation, or they form a 2-cycle.
  - **Series edges inside a cluster** must point the same way for both to lie on cycles.

## Interpretation (not theorem)

- **The harmonies are local.** No relation found is a coincidence of whole-surface counts. Each holds skeleton by skeleton, so it is a
  relation between the two small pieces, the cyclic part and its contraction.
- **Most are isomorphisms of those pieces.**
  - **The surface's symmetries and the walls** are special cases.
  - **Hidden symmetries.** Shrinking a cluster forgets how it was embedded, so the pieces can have symmetries the surface lacks.
- **Some are deeper.** On L(3,1,3,1), two different signed graphs have the same number of acyclic orientations, systematically across
  48 skeletons, although their Tutte polynomials differ. That is a relation between numbers of acyclic orientations, with no
  isomorphism behind it: closer to the owner's "harmonies" than anything else found here.
- **Some relations may be finite-size effects.** The mixed bundles behind many "same" relations need a vertex touching a loop from
  both sides, which narrow surfaces make common.

## Assumptions in the workspace this challenges

| Assumption | Where it lives | Verdict |
| --- | --- | --- |
| Lattice symmetry, planar duality and walls explain every exact relation between twists | The epic's question (`LOOP-SHIELD-20261023-001` recommendation) | **False** on genus 2: 31 unexplained equalities on the independent fresh surfaces. |
| The unexplained equalities are coincidences | A natural reading of equal large counts | **False.** Every one holds skeleton by skeleton, often over dozens of skeletons. |
| Matching pieces explain every relation that walls and symmetries miss | This epic's own scoping (37 of 37 on L(3,1,2,2)) | **False** on L(3,1,3,1): 6 of 14 equalities there need equal acyclic counts of non-isomorphic pieces on some skeletons. |
| Walls need the surface (a cyclic cover and its ends) | `ODD-LOOP-20261023-001B-P001`, `LOOP-SHIELD-20261023-001C-P001` | **Simpler.** Walls are what an odd point does in the shrunken graph. Their group is the dual of the radical of the cluster's lattice, for any rank. |
| Planar duality relates twists | The question's list | **Not within a genus-2 surface.** The dual is a different graph. |

## Provenance and novelty

| Result | Where it came from | Novelty |
| --- | --- | --- |
| The local factorization and the matroid evaluations | Counting skeleton by skeleton, after the scoping found the gluing picture | The signed-graph case of a classical oriented-matroid decomposition (Las Vergnas; Gioan); high folklore risk; the use for twist relations is new to the program |
| The wall group for clusters of any rank | Lemma W (boundary circles span the radical) with the factorization | New to the program; moderate folklore risk for the technique |
| Walls and symmetries are incomplete; every relation found holds skeleton by skeleton; 25 of 31 are isomorphisms of the pieces | B, exhaustive counts with per-skeleton tests | A recorded computation |
| Equal acyclic counts of non-isomorphic shrunken graphs on L(3,1,3,1) | B, with a post-hoc matroid check | A recorded computation; unexplained |
| The hidden pants symmetry of the three-loop event | Scoping | A recorded observation, subsumed by Theorem 2 |

**Did the perspective do real work?** Partly.
- **The topology framed the question.** The walls and their group came from it.
- **The answer is combinatorial.** The decisive structure, the cyclic–acyclic decomposition of an oriented matroid, is classical, and
  the surface enters only through which skeletons occur.
- **What remains.** The residual relations are questions about acyclic orientations of signed graphs.

## Recommendation

**Where the line of work stands.**
- **One theorem behind every relation.** The exact relations of the two-literal twisted model all come from the factorization.
- **Mostly isomorphisms.** Most come through surface symmetry, walls or isomorphic pieces.
- **The residue.** A few come through equal acyclic counts that no isomorphism explains.

| Option | What it would do | Interest |
| --- | --- | --- |
| **1. Continue at three places: dual pairs for three-place lines** (recommended, shared with `TRIPLE-TWIST-20261023-001`) | Test whether the shielding identity of two-literal lone loops holds for the winding contradictions of three-place tiling worlds, where no factorization of this kind is known | 2/3 |
| 2. The residual relations | Find the identity behind the equal acyclic counts on L(3,1,3,1): which changes of a signed graph keep its number of acyclic orientations without keeping its matroid; then test it on the larger genus-2 surfaces | 1/3 |
| 3. A note: "twist relations are local" | The factorization, the wall group and the genus-2 map, for readers in random two-literal formulas and oriented matroids | 1/3 |

| Layer | Assessment | Evidence or consequence |
| --- | --- | --- |
| Current attempt — the complete map of twist relations on genus 2 | **Partially successful** | The question is answered: walls, symmetries and duality are incomplete (31 unexplained equalities on independent fresh surfaces). The proposed completion is partly right: every relation holds skeleton by skeleton, and 25 of 31 are isomorphisms of the two pieces, but 6 on L(3,1,3,1) are not. |
| Local direction — exact relations of the two-literal twisted model | Practically complete; retire | Duality, harmonics, odd loops, shielding, walls of any rank and the local factorization are proved; the residue is a narrower question about acyclic orientations. |
| Broader exploration — twisted worlds | Moving to three places | The three-literal check found winding contradictions along odd classes (`TRIPLE-TWIST-20261023-001`). |
| Long-term goal — emergence from logic at the two-literal/three-literal boundary | Capability gained | The two-literal side's exact relations are now local in a proved sense. The missing bridge: whether the three-place side has exact relations of its own. |
| Next recommendation — dual pairs for three-place lines | **Next step:** Continue at three places (a fresh epic, shared with the three-literal recommendation). Retained: every result of this branch. Reopen the residue (option 2) if a three-place relation turns on acyclic counts. | It tests whether harmonies exist beyond the two-literal side. |
| Interest — that next step | **2/3 — Promising** | Lines at three places run along odd classes, as two-literal loops do (proved). No factorization is known there, so a positive result would need a new mechanism. |
| Execution — that next step | Deferred to the owner | Bound: one epic, with minimal-set enumeration on small tori. |
