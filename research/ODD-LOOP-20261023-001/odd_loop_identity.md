# The odd-loop identity

Epic `ODD-LOOP-20261023-001`, closed 2026-10-23.

## The question

The previous epic found one exact relation among the twist sectors and could not prove it:
- **The odd-loop identity.** For each class c, the two twists odd on c give the same probability that the strong components wind along c and nothing else.
- **Its stronger sibling.** "The line does not depend on the shear" had looked equally exact on small tori and then failed at 12 × 8.
- **The owner's approval.** On the recommendation (first the exact 4 × 4 count, then one bounded proof attempt with barrier-following seams), the owner wrote: "Yes please continue. I think we're getting close."

**The evidence:**
- [The exact count on the 4 × 4 torus](../../experiments/ODD-LOOP-20261023-001A/ODD-LOOP-20261023-001A-E001_four_by_four/contract.json) (A, confirmatory experiment; [result](../../artifacts/ODD-LOOP-20261023-001A/ODD-LOOP-20261023-001A-E001_four_by_four/result.json));
- [The wall involution and the odd-loop identity](../../proofs/ODD-LOOP-20261023-001B/ODD-LOOP-20261023-001B-P001_wall_involution/proof.md) (B, proof);
- **Scoping (scratch, not evidence):**
  - random walks testing the straight-band rule on 4 × 4 to 5 × 5;
  - weight enumerators of the line events on 3 × 3.

## Outcome in one paragraph

**Proved (B).** The odd-loop identity holds on every square-lattice torus, at every shear and for every primitive class.
- **The proof** is an explicit involution:
  - slide the second twist's seam onto the upper boundary of the odd loop itself;
  - flip the arrows on the boundary edges whose end off the loop is their head;
  - move the seam back to its standard place by a gauge transformation.
- **What it preserves.** No directed cycle is created or destroyed. So every configuration with a lone odd loop along c in one twist is paired with exactly one in the other twist, with the same cyclic structure.

**Exact at 4 × 4 (A).** Separate C code counted all 2³² orientations of the 4 × 4 torus at shears 0, 1 and 2, and every orientation of nine smaller tori. The identity holds in all 126 comparisons, including the diagonal classes.

**Found on the way.** The identity is a property of fair orientations. With any drift it fails, already on 3 × 3.

## The exact count (A)

| Torus | Class | Twists odd on it | Orientations in each |
| --- | --- | --- | --- |
| 4 × 4, shear 0 | (1, 0) | (1, 0) and (1, 1) | 39168000 = 39168000 |
| 4 × 4, shear 0 | (1, 1) and (1, −1) | (1, 0) and (0, 1) | 1024 = 1024 |
| 4 × 4, shear 1 | (1, −1) | (1, 0) and (0, 1) | 82944 = 82944 |
| 4 × 4, shear 2 | (1, −1) | (1, 0) and (0, 1) | 2109312 = 2109312 |
| 4 × 4, shear 2 | (1, 0) | (1, 0) and (1, 1) | 39085056 = 39085056 |

**How the run was checked.**
- **Controls.** All controls pass on every torus. In particular, contractible and cross counts are equal in every twisted sector, as the duality theorem requires.
- **The independent checker:**
  - matches the 3 × 3 rows to the earlier exact enumeration;
  - confirms the rotation and mirror symmetries exactly;
  - replays 4 × 4 at shear 1 by other code (worst deviation 2.52 standard errors).
- **Resources.** The run took 4012 s against a 6000 s budget.

**The stronger form fails exactly.** The horizontal line has 39168000 orientations at shears 0 and 1 but 39085056 at shear 2. Shear independence is false already at 4 × 4, while the identity between twists holds.

## The proof (B) in plain terms

**The setting.**
- In a twisted sector, inconsistency is a strong component of the double cover that the sheet swap maps to itself: an odd loop.
- The event in question is that such loops wind along c and nothing else winds at all.
- The two twists that make c odd differ by a seam running parallel to c.

**First attempt: straight bands.**
- **The idea.** Move the seam to the top of a horizontal band that is *inert*: one half of its lift receives nothing from outside, and the other half sends nothing out.
- **What works.** A seam there changes no directed cycle, so the move "seam to the lowest inert top" pairs the two events.
- **Where it covers everything.** Every configuration on 3 × 3 has such a band.
- **Two failures:**
  - From height 4 on, many configurations have no inert straight band (about 57% have one on 5 × 4, 33% on 6 × 5).
  - The rule stops being an involution when the lowest top falls on the default seam. A stored 4 × 4 orientation goes from top 4 to top 1.
  - So straight bands prove the identity only where coverage is complete.

**The construction that works: the loop is its own wall.**
- **The cover.** Unroll the torus across c, into a cylinder that c goes around.
- **The wall.** The odd loop's projection lifts to a strip K that goes once around the cylinder. The wall is the set of edges from K to the region above it.
- **Every wall arrow points one way.** Each edge from the loop to a vertex y has one arrow into the loop and one out of it. Both attach at the same sheet of y for all of y's edges, since otherwise y would be in the loop. So y has an *upstream* sheet that feeds the loop and a *downstream* sheet that the loop feeds.
- **The seam slides through.** Moving the seam onto the wall only reattaches each arrow to the other sheet of the loop vertex, which is still inside the loop. No directed cycle can use a wall arrow, before or after: it would have to return from the loop to an upstream sheet.
- **The bit flips.** A lift's sheet is read at the edge's tail. On wall edges whose free end is their head, the arrow must also be flipped to keep its direction at the free end. Without these flips, the check finds the cyclic arcs change in 18,668 cases.
- **Why it is an involution.** The gauge back to the standard seam changes no cycle. The loop's projection, and so the wall, is the same from the other twist's side. Applying the move twice returns the orientation.

**Consequence.** odd10 + odd01 − odd11 = twice the probability of an odd loop in a diagonal class, on every torus. With the earlier exact duality: the consistency relation measured on rectangles holds exactly when the additivity defect D equals that diagonal-loop probability.

## The identity needs fair coins (scoping)

- **What the bijection does.** It flips bits, so it preserves only the uniform measure.
- **Counts by forward edges on 3 × 3.** Count the line configurations by the number of edges oriented tail to head:
  - twist (1, 0): 27, 180, 480, 654, 480, 180, 27;
  - twist (1, 1): 3, 19, 55, 116, 226, 372, 446, 372, 226, 116, 55, 19, 3.
- **Same totals (2028), different spreads.** Any drift breaks the identity.
- **In the program's terms.** The harmony is a fairness phenomenon, like criticality at the fair spoke in the earlier epics.

## Interpretation (not theorem)

- **The loop shields the transverse twist.**
  - A lone contradiction loop along c is its own barrier: everything crossing its upper edge flows from an upstream half into the loop or out to a downstream half.
  - So how the transverse direction is glued cannot be seen from the loop's side; it can be moved through by a change of description.
  - "The loop is blind to the transverse twist" is now a theorem.
- **A relation between two unknown numbers.**
  - Neither probability has a known closed form.
  - The proof never computes them. It exhibits the symmetry that makes them equal, which is the owner's sense of a harmony: a relation, not a value.
- **Which twist is shielded.**
  - The twist that the wall can absorb is the one measured by crossing c.
  - On the torus this is the only other twist odd on c, so the identity covers every pair.
  - The same argument works on any periodic planar lattice. On a surface of higher genus it would pair a twist only with the twist dual to c. In three dimensions a loop cannot separate, so there would be no wall. These predictions are untested.

## Assumptions in the workspace this challenges

| Assumption | Where it lives | Verdict |
| --- | --- | --- |
| A proof would need a seam along a straight row ("move the seam to a row nothing crosses") | `TWIST-RELATIONS-20261022-001` note and this epic's plan | **No.** Straight rows cover only part of the event and the lowest-row rule is not an involution. The seam must follow the loop's own boundary, with bit flips at the edges entered from the free side. |
| Barrier-following seams "rewire the band" and break the bijection | `TWIST-RELATIONS-20261022-001` note ("moving a seam through a dual band rewires the band") | **Resolved.** The rewiring only swaps sheets inside the loop. The apparent obstruction came from flipping the twist without the compensating bit flips. |
| The identity is a statement about one model's probabilities | Implicit in the conjecture's wording | **Sharper.** It is a bijection that preserves every cycle statistic, so the whole conditional law of the cyclic structure agrees between the two twists. |
| Exact equality on small tori marks an exact law | Earlier epics' lesson, half right | **Here right, and now proved.** Shear independence, equally exact on small tori, fails exactly at 4 × 4. |
| The identity holds for any orientation law | Not stated; a natural reading | **No.** It needs fair orientations (3 × 3 weight enumerators differ). |

## Provenance and novelty

| Result | Where it came from | Novelty |
| --- | --- | --- |
| The wall lemma: sliding a twist seam along the boundary of a swap-invariant strong component, with bit flips on head-free edges, changes no directed cycle | This epic's proof attempt, after the straight-band bijection failed | The technique of moving a ℤ₂ seam by a gauge transformation is standard (antiperiodic boundary conditions, interfaces, ℤ₂ gauge theory). Using the odd component as its own barrier, and the bit flips, are new to the program and not found elsewhere. Folklore risk: moderate. |
| The odd-loop identity for every torus, shear and class | The previous epic's conjecture, proved here | Not found in the literature; low folklore risk for the statement |
| Exact 4 × 4 counts, including diagonal classes, and the exact failure of shear independence | A, exhaustive C enumeration | A recorded computation |
| The identity needs fair orientations | Scratch enumeration | New to the program |

**Did the perspective do real work?** Yes.
- **What the topology view supplied.** The proof is topological in the program's sense. It uses the cover along c, the separation of a cylinder by the loop, and the Poincaré-dual twist that the wall represents.
- **The key move.** Treat the emergent loop as the barrier, rather than search the background for one.
- **What was standard.** The gauge bookkeeping.

**Ratio since the last checkpoint.**
- 2 artifacts are substantive: the experiment and the proof.
- 2 are administrative: this note and the ledger.
- So the recommendation below is substantive work, not another administrative artifact.

## Recommendation

| Option | What it would do | Interest |
| --- | --- | --- |
| **1. Where the loop shields the twist** (recommended) | Test the mechanism where it predicts something new. **On a surface of genus 2** (a square-tiled surface), a loop along c should give an exact identity only between twists that differ by the twist dual to c, and none for the other twists odd on c. **On the 3-torus** a loop cannot separate, so the identity should fail. One bounded epic: exhaustive counts on the smallest feasible lattices and a confirmatory Monte Carlo. Stop if both predictions fail, or if line events are too rare to resolve. | 2/3 |
| 2. A bounded search for the program's next barrier question | Over the lower bound P(cone = plane) ≥ c, space from a law (question 9) and dynamics (question 4), as recommended twice before | 1/3 |
| 3. Convert the twisted-torus results into a self-contained note | The exact duality, the harmonic structure and the wall involution, with replays, for readers in percolation; sharing is the owner's call | 1/3 |

| Layer | Assessment | Evidence or consequence |
| --- | --- | --- |
| Current attempt — the odd-loop identity | **Successful** | Proved on every torus, shear and class by an explicit involution that preserves the cyclic structure; exact at 4 × 4 by separate code. It needs fair orientations. |
| Local direction — exact relations of the twisted torus model | Practically complete for finite-size relations | The known exact relations are now all proved: duality, harmonic structure and the odd-loop identity. A scan of the 13 exact tori finds, within each torus, no other exact equality that the lattice symmetries and the identity do not explain, apart from two small-count coincidences on 5 × 3 (2160 and 20 orientations). Across shears, the odd horizontal line is shear-independent at height 3 (19200 on every 4 × 3; 175692 on every 5 × 3), the same kind of small-torus pattern that failed at 12 × 8. The remaining relations, additivity and the flatness of E under shear, are large-size relations. |
| Broader exploration — critical emergence of single fair contacts | Practically complete, with a proved exact relation | Reduction, class, duality, harmonic structure and the shielding identity. Open: the lower bound, and the scaling-limit degeneracy behind additivity. |
| Long-term goal — emergence from logic | Capability gained | A first theorem relating two unknown emergence quantities: a contradiction loop shields the twist dual to itself, for fair orientations. |
| Next recommendation — where the loop shields the twist | **Next step:** Continue. A fresh epic: exhaustive and Monte Carlo tests of the predicted identity on a genus-2 surface (twists dual to c only) and its predicted failure on the 3-torus. | It tests whether the mechanism, not a torus coincidence, is the reason for the harmony. A pass would give a general law tying an emergent loop to the background it screens. |
| Interest — that next step | **2/3 — Promising** | The mechanism makes sharp, opposite predictions in two settings, and either outcome is informative. The main uncertainty is practical: line events may be rare on the smallest genus-2 and 3-torus lattices, and tiny lattices can show coincidental equalities. |
| Execution — that next step | Deferred to the owner | Bound: one epic. Stop if the genus-2 identity fails for the dual twist, or if neither setting resolves at the feasible sizes. |
