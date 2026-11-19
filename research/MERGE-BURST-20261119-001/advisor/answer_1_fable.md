# Advisor answer: MERGE-BURST before the freeze

I can't see the engine's rule, so the answers on soundness are conditional on how it reads blocks.

## 1. Is the reduction sound?

**Yes, on one condition: the growth rule must read the block family only through its down-closure.** That means it reads which point sets lie inside some block, and nothing else. A family and its maximal blocks have the same down-closure, so the reduction then changes nothing.

- **A block inside another:** it cannot matter through a point the larger block lacks, by definition. It can matter in three other ways, and each needs a check against the rule:
  - **Multiplicity:** if candidates or valid sets are indexed by (block, subset) rather than by point set, nested and equal blocks double-count. The pilot says they are not, but it is one case.
  - **Neighbour identity:** the dropped block is an old knot. If the rule ever uses that knot's other places or its own identity (for example, which distinction the new junction attaches through), dropping it matters.
  - **Relays:** a small block's knot may relay to something the larger block's knot does not. Reduce X⁺ after relaying, or prove that relaying commutes with reduction. This is the weakest point as I see it.
- **Equal blocks:** they do change the cover if it is taken on the unreduced map, because two equal blocks with two or more points make a 2-cycle in the incidence, which a cover unfolds. So do not argue through the cover of the unreduced stage, which is outside the class anyway. Argue in two steps: growth(stage) = growth(reduced stage) by the rule, then DEAD-CAP on the reduced stage.
- **Short proof sketch:**
  1. Round-1 candidates are the pairs inside a common block, which are the pairs inside a common maximal block.
  2. Valid sets are the subsets of blocks satisfying a condition on points only, so they are the same for both families.
  3. By the refereed statement, later rounds read old knots only through steps 1 and 2. By induction the two growths are equal round by round.
  4. In the class, two maximal blocks share at most one point. So every dropped block with two or more points sits in exactly one maximal block, and no dropped block bridges two maximal ones. A 3-cycle through a dropped block is already a 3-cycle through its maximal block.

  The burden is step 3 with "only through point sets" made explicit, plus the relay point.

## 2. Predictions

These are low-confidence guesses.

| Outcome | Guess | Range |
|---|---|---|
| Reach a reading within limits | 6 | 3–10 |
| Close | 5 | — |
| Keep growing | 0–1 | — |
| No reading | about 9 | — |
| Repeats (two merges before a reading) | 1–3 | — |

- **Why most readings should close:** a group that swallows nearly everything becomes a common neighbour of all remaining live junctions. That gives one block and a binomial row.
- **Why few may reach a reading:** these 15 were stopped, presumably for size, so many will hit 6 GB before or during the burst.
- **Why repeats should be uncommon:** a repeat needs a first merge that leaves live junctions outside the giant group's reach.

## 3. Changes before freezing

- **R1 needs a class-independent test.** If every reading is a single block, R1 only tests binomials. Add an engine-against-engine check: grow the unreduced and the reduced stage side by side for a few rounds at every stage, including stages outside the class. This tests the lemma directly and is the cheapest discriminator.
- **R1 must be feasible.** A block of n points gives C(n, k+1) junctions in round k. At n = 30, round 8 alone is about 14 million. Freeze a rule: compare as many rounds as fit, with a minimum of 3, and count "reading but unchecked" separately. Any mismatch in any round is a failure.
- **Split R2.** As written it is nearly implied by "single block":
  - R2a: the first reading is one maximal block.
  - R2b: every reading closes.

  Record the number of maximal blocks and the largest block size. A block of 40 "closes" after about 2⁴⁰ junctions, so say that when it happens.
- **Define "after its burst".** State what counts if a reading occurs with no merge event before it.
- **R3 at 8 of 15 is about a coin flip on my guess.** Keep it only if labelled risky; otherwise use 5 or more. For each start with no reading, record whether it ran out of memory or time, or reached round 60 still outside the class. Those are different findings.
- **The merge-event threshold needs a floor.** A tenfold jump triggers on tiny early groups, such as 1 to 10. Add a minimum, for example a largest group of at least 50, and freeze the number.
- **Add a stability check.** The reading at stage s should agree with the reading at stage s+1. This is free and catches a reduction that is right for one round only.
