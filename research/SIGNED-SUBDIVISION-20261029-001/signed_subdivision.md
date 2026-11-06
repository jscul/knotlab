# Interference on genuine two-dimensional space

Epic `SIGNED-SUBDIVISION-20261029-001`, 2026-10-29.

## The question

- **The owner's request (2026-10-29).** "Yes, let's continue," on the recommendation of `INTERFERENCE-20261029-001`: interference
  on genuine two-dimensional space. Signs revived knots in finitely ramified towers there. Do signed or real weights let a knot
  reproduce itself on space that is not tree-like?
- **The setting** (`SHARED-SUBDIVISION-20261029-001`).
  - A three-bit law sits on every up triangle of the triangular-lattice torus (S2) or on every triangle, with one placement per
    orientation (S1): 122 rule shapes.
  - Each triangle is cut into k² with the new vertices shared between neighbours (scale k).
  - A rule is *exact* when the fine sums are proportional to the coarse weights on the tested coarse tori. With counts, exactly
    22 shapes are exact at scale 2 and 6 at scale 3, all with affine solution sets.
- **The reading.** Allowed states are read through the interference reading adopted on 2026-10-29: a state is allowed when its
  signed witness sum is nonzero. *Support-exact* means exact at the level of allowed states.
- **The three tests.**
  - (A) Weights ±1: which shapes and sign patterns are exact or support-exact?
  - (B) Real weights: what can be proved?
  - (C) Real weights on what (B) leaves open: what does a search find?
- **Intuitions targeted:** space from logic without a drawn space; everything relational (interference); the two/three boundary.

**The evidence:**
- [Signs add no exact law under shared subdivision](../../proofs/SIGNED-SUBDIVISION-20261029-001A/SIGNED-SUBDIVISION-20261029-001A-P001_signs_add_no_exact_law_under_shared_subdivision/proof.md) (A, proof);
- [Real weights under shared subdivision](../../proofs/SIGNED-SUBDIVISION-20261029-001B/SIGNED-SUBDIVISION-20261029-001B-P001_real_weights_under_shared_subdivision/proof.md) (B, proof);
- [Real-weight search](../../experiments/SIGNED-SUBDIVISION-20261029-001C/SIGNED-SUBDIVISION-20261029-001C-E001_real_weight_search/contract.json) (C, confirmatory experiment, closed null because its power check failed; results and a post-hoc analysis in `artifacts/SIGNED-SUBDIVISION-20261029-001C/`);
- scoping (scratch, not evidence): the first sign census, a softly bounded real-weight search, the coherence probe, the affine
  algebra, and the level-k gasket probe behind the recommendation.

## Outcome in one paragraph

**Interference does not build genuine two-dimensional space: wherever the question can be decided, the only laws that reproduce
themselves are signed or weighted copies of the affine ones.**
- **A (proved, exhaustive).** With weights ±1, no rule shape outside the 22 counted-exact ones becomes exact, or even exact on
  allowed states. Signs only sort the old exact laws. At scale 2 every sign pattern of them keeps its allowed states, but only 28
  of their 80 gauge orbits keep their weights. The planned "every sign pattern stays exact" was refuted and corrected.
- **B (proved where decidable).**
  - Positive real weights see only the counted allowed states.
  - A sign-parity obstruction rules out 54 of the 100 non-affine shapes at scale 2, and 34 at scale 3, for every real weighting.
  - On the 22 affine shapes, real magnitudes add only gauge copies of the ±1 exact laws.
  - Small tori let spurious exact weights through (2^(1/9), the golden ratio, the reciprocal tribonacci constant), and larger tori
    remove them.
- **C (confirmatory search on the 46 densest shapes and the 82 open at scale 3).** No open shape gave an exact weighting. At scale 2 none even reached a 2-torus candidate (best residual 9.2e-5 over 592
  sign classes), and at scale 3 the single candidate was not confirmed. But the search failed its power check (P2): the joint
  stage missed 2 of the 28 known exact classes at scale 2. So by the pre-registered rule the no-exact-weighting conclusion is not
  drawn from this run, and C closed null. Post hoc (exploratory), the scale-3 candidate is a degenerate point where almost
  everything cancels, and it fails on the 3-torus.
- **A lead beyond the epic (scoping, not evidence).** One signed not-all-equal law reproduces itself exactly on the level-k
  Sierpinski gaskets for k = 2 to 11. These gaskets are finitely ramified, with dimension tending to 2. What separates them from
  the plane is exactly the triangles that join neighbouring gaskets.

## What was proved

| Result | Content |
| --- | --- |
| A, Lemma 1 | Edge sign gauges (S1) and corner sign gauges with product one (S2) leave every fine and coarse sum unchanged; the 135,440 signed rules fall into 944 orbits. |
| A, Theorem 2 | With weights ±1 no shape outside the 22 counted-exact ones is exact or support-exact (scale 2, coarse sides 2–4; scale 3, sides 2–3). At scale 2 all 80 orbits of those shapes are support-exact and 28 are exact (always the unsigned law); at scale 3, six of the eight orbits of each twisted pair are exact. The planned "every sign pattern stays exact" was refuted. |
| B, Lemma 1 | Every real weighting is gauge-equivalent to one of the 944 sign classes times 1 to 4 free positive magnitudes. |
| B, Theorem 2 | Positive weights have the counted supports, so they add no exact or support-exact shape. |
| B, Theorem 3 | Sign-parity obstruction: if all fine extensions of a forbidden coarse state use each tuple equally often mod 2, no real weighting cancels it. This excludes 54 of the 100 non-affine shapes at scale 2 and 34 shapes at scale 3, for every real weighting. The per-class refinement adds nothing. |
| B, Theorem 4 | On the 22 affine shapes, the exact real weightings are the gauge images of the exact ±1 classes (scale 2, coarse sides 2–6; scale 3, sides 2–4). Smaller tori admit spurious exact weights: −2^(±1/9) for parity on up triangles on sides 2–4; the golden ratio (scale 3) and the reciprocal tribonacci constant (scale 2) for the twisted pairs on the coarse 2-torus. Larger tori remove all of them. |
| B, Theorem 5 | The atoms excluding 000 or 111, weighted on Hamming classes, have no exact weighting on the coarse 2-torus. |

## What was searched (C)

- **Contract.** Frozen on 2026-10-29 as a confirmatory experiment.
  - The search ran in the gauge slice of ticket B, with magnitudes between 1/100 and 100, over every sign class and both scales.
  - Each class got 24 random starts on the coarse 2-torus, with a residual that normalizes each exactness equation by its own
    scale.
  - Each candidate (residual below 1e-8) was searched again on the 2- and 3-tori jointly, from its best point and 8 random starts.
- **The run.** It ran once, in 75 minutes on four workers. An earlier launch with six workers (the contract allows four) was
  stopped within seconds and wrote nothing.
- **What it saw.**

| Shapes (sign classes) | Scale 2 | Scale 3 |
| --- | --- | --- |
| Open: atoms and two-excluded laws, and more at scale 3 | 46 (592): no 2-torus candidate; best residual 9.2e-5 | 82 (792): one candidate, not confirmed |
| Excluded by the sign-parity obstruction (not affine) | 54 (272): no candidate; best residual 0.40 | 18 (72): no candidate |
| Affine | 80 candidates; 28 confirmed: 26 of the 28 exact ±1 classes, plus the 2 spurious parity classes that B finds on sides 2–4 | 48 candidates; 36 confirmed, exactly the exact ±1 classes |

- **Predictions.**
  - P1 (no open shape confirmed): held.
  - P2 (every exact ±1 class confirmed): **failed** at scale 2, with 26 of 28 confirmed; 36 of 36 at scale 3.
  - P3 (no excluded shape confirmed, none even a candidate): held.
  - P4 (no golden weighting of the Fibonacci laws exact): held, with the largest residual 1.0 everywhere.
  - The cheapest control (the earlier concentration flaw stays fixed) fired.
- **Why P2 failed (post hoc, `post_hoc.json`).**
  - The two missed classes are frozen three-excluded laws in their unsigned class. Both are exact at the ±1 point (joint and
    4-torus residual 0), as B proves.
  - Their coarse 2-torus has a single solution, so every magnitude is exact there, and the best 2-torus point was arbitrary.
  - The joint residual saturates at ±1 away from the exact point, so the joint stage's random starts never reached its basin.
  - This is a weakness of the confirmation stage. The filter stage reached residual zero for every one of the 80 affine classes.
- **The scale-3 candidate (post hoc).** It is an S1 atom (excluding 000, sign class 7) with magnitudes about 5.04, 5.04, 5.04
  and 3.86. On the 2-torus it has residual 3.8e-10, but |F|/A is only 1.9e-10 on every allowed state: F almost vanishes, so c ≈ 0.
  On the 3-torus its largest residual is 0.62.
- **Reading.** For the open shapes at scale 2 the result rests on the filter stage alone, which never produced a candidate. The
  frozen rule makes no such distinction, so this stays exploratory evidence. A confirmatory rerun would start the joint stage
  from the ±1 point and use a residual that does not saturate. It is not recommended, because the failure was one of validation
  only.

## Reading

- **Interference does not build genuine two-dimensional space.** On finitely ramified towers, signs rebuild and reproduce most
  knots (`INTERFERENCE-20261029-001B`). On the triangular lattice with shared midpoints they rebuild none. Neighbouring
  triangles share their midpoints, so a cancellation that rebuilds a knot inside one triangle would have to be arranged
  consistently across the whole lattice. The sign-parity obstruction is the simplest form of that failure: the extensions of a
  forbidden state all carry the same sign.
- **Exact self-reproduction on genuine space is affine under every reading tried.**
  - Existential: `SHARED-SUBDIVISION-20261029-001`.
  - Counted: the same epic.
  - Signed: A.
  - Real: B, where it can be decided. On the densest laws C's search found nothing, but it is exploratory, since its power check
    failed.
  
  In each case the survivors are parity, the frozen three-excluded laws and the line-collapsing twisted not-all-equal. Only
  parity keeps a knot on a triangle.
- **What interference does change.** It splits the old exact laws into sign classes that keep their weights and classes that keep
  only their allowed states. It also makes the finite proxies leak. Small tori admit exact real weights at 2^(1/9), the golden
  ratio and the tribonacci constant, and only larger tori remove them. The golden ratio, the epic's suggested starting point,
  appears only as such an artifact.
- **Two/three boundary.** Positivity was the whole boundary for a single relation (`INTERFERENCE-20261029-001A`), but it is not
  the boundary for self-reproduction on genuine space. There, interference cannot cross it.

## Next steps

| Layer | Assessment | Evidence or consequence |
| --- | --- | --- |
| Current attempt — interference on genuine two-dimensional space | **Status:** Successful (a negative answer, proved where decidable) | ±1 signs: no new exact or support-exact shape (A, exhaustive). Real weights: positivity, the sign-parity obstruction (54 of 100 at scale 2) and the affine classification (B). The 46 densest shapes remain unproved. C's search found no exact weighting but failed its power check, so it is not confirmatory. |
| Local direction — exact self-reproduction on the triangular lattice under shared subdivision | Practically exhausted | Affine only, under the existential, counted, signed and real readings. Closing the 46 dense shapes would complete a negative classification at low payoff. Reopen if a dense shape is found exact on the 3-torus. |
| Broader exploration — space from a law (question 9) | Known alternatives | Finitely ramified towers carry signed knots (`INTERFERENCE-20261029-001B`). Scoping (not evidence) finds one signed not-all-equal law exact on every level-k Sierpinski gasket for k = 2 to 11. |
| Long-term goal — space from logic without a drawn space | Obstruction learned; a candidate capability | Interference does not build the plane exactly. It may build exactly self-similar spaces of every dimension below 2. |
| Next recommendation — signed not-all-equal on the level-k Sierpinski gaskets | **Next step:** Continue, as a fresh epic. Prove exactness for every k, or find where it stops; explain the factors (−1, −4, 13, 85, −634, …); classify the signed laws and placements exact on each gasket. | Connection: where the spaces a non-affine knot can build end and the plane begins. Independent value: an exact renormalization identity for a frustrated triangle law on a family of fractals whose dimension tends to 2. |
| Interest — that recommendation | **3/3 — Hot** | Exact integer evidence for k = 2 to 11. The law is (−1)^((a⊕b)(a⊕c)) − [a = b = c], a quadratic phase minus the equality projector, which suggests a proof by Gauss sums. Main uncertainty: it may follow from a local identity, in which case its value is the space-building statement rather than the technique. Also, finitely ramified spaces stay unlike the plane in kind. |
| Execution — that next action | Deferred to the owner (fresh epic) | Done so far: scoping only (k up to 11, three signed laws, minutes of CPU). First step if approved: a proof attempt for every k, and a census of signed laws and placements on the gaskets of levels 3 to 6. Stop after a proof, or if exactness fails at some level without a pattern. |

**Recommendation.** **Continue**, as a fresh epic: signed not-all-equal on the level-k Sierpinski gaskets (3/3). Two alternatives were considered.
- Proving the 46 dense shapes (1/3). This completes a negative classification, and no proof route is in hand: it would need
  obstructions that combine several equations.
- Closure under subdivision, where the coarse law may differ from the fine one (1/3). It is likely negative and close to the
  folklore that decimation makes couplings proliferate.

The stop rule's item (ii) is met in its coverage: every shape was searched and the residuals recorded. Its single candidate was
refuted only post hoc, so that part is exploratory.
