<!-- modelUsage: claude-fable-5-2 -->

I reasoned from your description only, with no simulation, and I read "common neighbour" as two junctions both joined to a third; if that reading is off, items marked † need rechecking.

## 1. The rule

I could not build a certain counterexample, but there are three holes the pilot could not have exposed.

- **Growth with no birth (†, best candidate).** Take a ring of five 4-place knots, each touching its two ring neighbours once.
  - Candidates are the five pairs two steps apart, with no group of three or more, so every knot is in 2 pair-groups with 2 loose bits. There are no offshoots and no stall.
  - The five new junctions have 2 parents and demand 2, so they get 2 bits and form the same ring again.
  - That is 5 junctions per round forever: measured dimension 1, rule says 0.
  - It needs 5 knots, and the pilot stopped at 4. Longer or doubled rings and rings with 5-place knots (offshoots of demand 2, so still no birth) are the same family.
  - "0 if no birth" should be split into "closes" and "grows without a birth".
- **Linked partners.** The rule treats each partner as an inert core. If a knot sits in two groups, the two group junctions are candidates of each other in round 2, and each can carry its own class (sizes j and k).
  - The rule says max(j, k); the cores' joint lineage could give j + k or max + 1.
  - The minimal test is j = k = 1, where the rule says 1. Check whether any of the pilot's 37 dimension-1 cases has two classes with candidate partners. If none does, the pilot never tested max against combine.
  - Cases with j = 2, k ≥ 1 need 4–5 knots and are essentially unsampled.
- **Rounds.** From your known facts, surplus arises only in round 1 and from a demand-0 offshoot. So births should occur only in rounds 1 and 2, and round-2 births are closed sibling pairs. "A class of 2 meeting a later class of 2" is then moot, provided this is frozen as a prediction: no birth after round 2.

Two N² classes in one piece just add, so max is right there. The rule was found after a read-out, so report the 300 pilot arrangements separately from the confirmatory set.

## 2. The measurement

- **Dimension ≤ 3:** sound. Exact polynomials are reached well inside 30 rounds.
- **Dimension 4:** thin. The 6,000 cap cuts at about round 16–19 (c·r⁴/24), and seven constant third differences need 10 clean rounds, so the transient must end by round 6–9.
- **Dimension 5:** if it existed, it would be cut at about round 14 and need 11 clean rounds. It would most likely come out "unsettled", so P3 could pass falsely.
- **Parity effects:** period-2 counts make differences alternate, which gives "unsettled" or, with an even window, a false read. Test odd and even rounds separately as well.

Fixes I would freeze:
- Cut only at round boundaries.
- Rerun every unsettled case at a much higher cap before scoring P1 or P3.
- Record the round from which the polynomial is exact.
- Compute the rule from rounds 1–2 only, in code separate from the measurement, so it is a real forecast.

## 3. Predictions

The pilot has no 5-knot arrangements, and those are 93% of the census, so P1–P5 are all extrapolations.

- **P1:** I expect it to fail on birthless rings, and possibly on linked partners. Freeze it as three parts: (a) no birth after round 2; (b) nothing grows without a birth; (c) dimension = largest class. Then you learn which part breaks.
- **P2:** "under 5%" is too loose, since the pilot shows 1%. Dimension ≥ 3 needs every knot of a group to have exactly 2 loose bits and sit in one group. I would freeze under 2% by distinct arrangements and lower still by labelled count.
- **P3:** your argument covers only the mutually touching family. Sharper: no settled dimension ≥ 5 and no unsettled case left after rerun.
  - (†) A class of 5 needs five knots of degree ≤ 3 with every pair sharing a neighbour, which I could not construct.
  - Four mutually touching 5-place knots admit no fifth knot, since any attachment leaves one knot with 1 loose bit. So dimension 4 should be very rare at 5 knots.
  - The pilot hit dimension 4 once in 300 (chance about 15% if only one such arrangement exists). Predict the exact count and list them.
- **P4:** fine, and it follows from the known results. It is a consistency check, not a finding.
- **P5:** plausible but confounded by stalls. My guess is that the stall share rises steeply with the number of knots and exceeds 40% at 5 knots, because a knot touching three others is already in several pair-groups. Freeze the stall share per knot count as its own prediction, and state P5 among settled growing arrangements only.
- **Extra:** dimension 1 should shrink as a share of growing arrangements with more knots, unless rings contribute.

## 4. Weighting

Reporting both is right, but neither is canonical. Uniform over distinct arrangements overweights symmetric ones, which is exactly where the high dimensions sit. Labelled count is closer to "nothing chooses", but say which labels: knots only, or knots and places (random pairing of places, conditioned on connected). These differ on repeated touches.

Because 5-knot arrangements dominate either way, report every share per knot count. Call something "typical" only if it holds under both weightings and in each stratum. The cutoffs of 5 knots and 5 places are themselves a choice and belong in the assumptions register.