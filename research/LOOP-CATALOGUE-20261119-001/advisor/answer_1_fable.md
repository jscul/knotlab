['claude-fable-5-2']
# Advisor answer 1 (LOOP-CATALOGUE-20261119-001)

**The stated theta equation does not match its stated rate, and the product law needs a transit factor before you freeze.** I worked only from your statement and ran nothing, so each derivation below is for you to check.

I read the candidate map as follows: its points are the live knots, and each knot w contributes the simplex of its live neighbours. This reproduces your ring facts (odd rings give L = n, even rings two loops of n/2, rings of 3, 4 and 6 none).

## Two things to fix before the freeze

**1. The theta's equation.**
- The root of y^5 (1 + 2y) = 1 is y ≈ 0.8231, a rate of 1.2150.
- Your rate 1.2298 is the root of y^5 (2 + y) = 1 (y ≈ 0.8131).
- The cover model gives the second:
  - The blocks are the pairs {0,2}, {1,3}, {0,3} and the merged block {1,4,5} ∪ {2,4,5}.
  - The loop is 0 – 2 – [block] – 1 – 3 – 0, with four loop points.
  - Knots 2 and 1 share no simplex, so a connected cluster must take 4, 5 or both: a factor 2y + y².
  - The weight is y^4 (2y + y²) = y^5 (2 + y).

  This is not of the form y^L Π(1 + U), because its constant term is 2.

**2. The pendant chain (C2).** A chain 0 – h1 – h2 – … hanging at loop knot 0 enters the candidate map in two places:
- the odd knots h1 – h3 – … through knot 0's simplex {1, 4, h1};
- the even knots h2 – h4 – … through the pair {0, h2} at knot 0 itself.

I predict a factor (1 − y)^−2 for an endless chain, not 1/(1 − y). A chain of m knots gives (1 + … + y^⌈m/2⌉)(1 + … + y^⌊m/2⌋). Check m = 2, 3, 4 by growth.

## Q1. The eddy rule

In the cover model, a one-loop piece has a round-weight W(y), which sums y^(points) over the ways of going once round with side entries. The count per round is P(y) + Q(y)/(1 − W(y)).
- "Bare" should mean W is a single monomial (W(1) = 1): one way round, so a constant count (your 5 a round).
- An eddy is W(1) ≥ 2, or two independent cycles of blocks.

Your v2 wording agrees with this where I can check it. A hyperedge on the loop is a forced transit, the monomial y^(h−2), so it stays bare.

One gap: a hyperedge hanging off the loop at a single knot gives (1 + y²), an eddy. Check that v2 does not call it bare (ring of five plus a ring of three at one knot).

**Two hyperedges meeting at a knot.** Your guess is plausible, but I cannot prove it from the statement. My sharper version is that a loop knot needs an open distinction left for the loop after first-round demand. If both of its loop blocks are hyperedges, round 1 takes both and nothing is re-formed on later turns. This is your "live at its candidates" condition applied to blocks.

It predicts three things to test on the 46 pieces and on new ones:
- **Meeting knot off the cycle.** The exclusion should bite only when the meeting knot is on the cycle. If the knot is off the cycle and the piece has another non-bare cycle, the piece should still feed.
- **Spare at the meeting knot.** A spare there may restore the loop.
- **Hyperedge meeting a merged block.** A hyperedge and a merged block meeting at a loop knot should be fine.

If the first fails, v2's "excluded: any piece" is right as written and my mechanism is wrong.

## Q2. The general law

For one loop:

**y^(L0) · Π_B T_B(y) · Π_e (1 + U_e(y)) = 1**

Here L0 counts the loop points. T_B, for a block with ports a and b, sums y^(|S|−2) over the connected sets S ⊆ B that contain a and b. Each interior point also carries its own (1 + U).

- **One simplex of k points:** (1 + y)^(k−2).
- **Two simplices sharing c ≥ 2 points, ports on opposite sides:** ((1 + y)^c − 1) · (1 + y)^(other points). The theta is c = 2.
- **Hyperedge of h:** y^(h−2).

So y^L Π(1 + U) = 1 holds exactly when every transit has both ports in one simplex.

## Q3. The unit

Catalogue weights, not starts. The rate depends only on W, so the ring of five with a spare and with a hanging knot are one loop with two realisations. Reordering entries round the loop changes Q but not the rate. Record both: the multiset for the rate, the cyclic arrangement for the series.

Minimal one-loop eddies should have:
- W = y^L (1 + y);
- W = y^L (1 + y^m), from an all-or-nothing pendant group;
- W = y^L (2 + y).

A shared set of c ≥ 3 is never minimal. This is a prediction for the 8-knot run.

Honest bounds are starts exhaustive to 8 knots, and weights stated per L. The first minimal two-loop eddy (two bare loops, no spares) probably needs 9 knots (two rings of five sharing a knot), so say the 8-knot list may contain no algebraic entry.

## Q4. Weakest predictions and falsifiers

- **The chain factor and the theta equation**, as above.
- **C2's products.** On even rings they hold only within one loop. A spare at knot 0 enters knot 0's loop, while a knot hanging at knot 0 enters the other loop, through knot 0's simplex.
  - Ring of 8 with both at knot 0: y^4 (1 + y) = 1.
  - Hanging knot moved to knot 1: y^4 (1 + y)² = 1.
- **L = 3.** F says L ≥ 4. Test the ring of six with hanging knots, whose simplices grow past pairs.
- **Two-loop rational.** This holds exactly when the two cycles lie in one merged block, so the block graph has one cycle. Two independent cycles of blocks give a branching unrolled map and t^(−5/2), which no rational series has. Test a two-loop piece whose join is a hyperedge.
- **E4.** Its thresholds are descriptive, set from the pilot. Label them so.
- **E2.** In the cover model a non-eddy closes or grows by a constant. Say where dimension 2 comes from, or it is not a prediction of the rule.

## Q5. The sharp statement

**Theorem (cover model, by transfer).** For a piece with c independent cycles of blocks:
- **c = 0:** finitely many clusters.
- **c = 1:** the count is P + Q/(1 − W).
  - It is constant when W is a monomial.
  - Otherwise it is C ρ^t with no power factor, where 1/ρ is the one root of W = 1 in (0, 1).
- **c ≥ 2:** the count is algebraic, C ρ^t t^(−5/2).

**The set of rates.** One-loop rates are the roots of W = 1 for W in the class generated by:
- y^L;
- the transits T_B;
- the factors (1 + U), with U closed under U = y Π(1 + U′).

This inclusion is provable. The converse (every such W occurs) needs a realisability lemma under the knot-size caps and the hyperedge exclusion. State it with the caps, or as a conjecture.

**Finite, few or unbounded.** There are infinitely many rates, already from y^L (1 + y) = 1, and they fall to 1 as L grows. They are bounded above by the size cap. They are generated by finitely many pieces under two operations: multiplying weights and the joint's substitution.

Add the transit to F's generating set. It is missing {loop, spare, hanging knot, chain, joint} + {merged-block transit}.
