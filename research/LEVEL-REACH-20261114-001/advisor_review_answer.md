**Verdict: don't freeze as is.** Q1 and Q3 are close to settled by construction, Q1's conditioning hides a censoring bias, and Q5 has no pilot basis. I have not read the code, so the structural claims below are from your description only.

**(1) Soundness**

- **Ruler is the composition default.** If knots only sit within a level or join adjacent levels, chaining one cross-level knot per step and cancelling the shared intermediates gives a bond of s+2 wherever knots compose. Q1 therefore really asks how often something shortens the chain or composition fails. Compute the composition upper bound U(s) from the placement alone and freeze predictions on L versus U: the share with L < U (shortcut) and L > U or no bond (composition failure).
- **Q1's conditioning censors.** All 22 undecided are in the exponential class, where every non-ruler sits. The pilot gives 116/136 = 85% among decided, but 116/158 = 73% if the undecided are all non-ruler. At 150 s against a 90th percentile of 617 s, the undecided share will grow. Freeze Q1 as a bound pair with undecided counted both ways, failing only if the upper bound is below 70%.
- **Cut the undecided cells cheaply.** Ruler needs only "no bond of size ≤ s+1" certified plus one of size s+2 found; rigid-like needs one of size 2. Run those targeted queries first and spend k_max=10 only on "other".
- **Say what "> 10" is.** State whether (3,>10,>10,>10) counts as decided, and which bucket it falls in.
- **Q4 is near-certain.** The pilot shows 0 non-rulers in 65 finitary against 19 in 70 exponential. Keep it, labelled as confirmation, and check whether the finitary class forces the ruler outright (activity dies, so the placement is tree-like). If it does, Q4 is a lemma, not a prediction.
- **Q5 is a guess.** The pilot has 3 bounded and 0 polynomial cases. E_R is enumerated and filtered while W_R is coin-weighted, so the comparison mixes sampling schemes. Make it two-sided and descriptive, or compare within matched automaton size.
- **Define "by weight".** I assume multiplicity in W_R; E_R has none.
- **Check pilot order.** If the 247 finished first because they were fast, every pilot rate is biased toward easy cases. Say so in the freeze.

**(2) Depth N**

Q3 tests membership, not dependence. Levels below the target can still shorten a bond through implied clauses once they are quantified away, without appearing in it. That is exactly why L is non-increasing in N.

- **Honest check:** recompute L with the pattern truncated at the target level (N = 3+s) and at N = 9. Freeze "L unchanged in at least X%", and report every change as "deep levels tighten the top's bond".
- **Unequal margin:** s=1 has five levels beneath the target and s=4 has two. Either fix the margin (N = 3+s+2) or report stability per s.

**(3) For John's question**

- **Add Q0, unconditioned.** Among alive descriptions, report the share with a bond at every s. In the pilot, 81 of 247 had no join or no bond, so in about a third the top binds nothing. Q1 conditions that away.
- **Separate two meanings of "binds".** Bounded L (rigid-like or constant, about 7% in the pilot) means the top constrains deep levels with a fixed number of helpers. Ruler means it constrains them only jointly with one extra member per level, which is contact passed along a chain and weakens with depth. State the headline as three shares: none, chained, direct.
- **Add a top-specificity control.** Run the same L(s) from a random level-3 member that is not the designated top, or from level 4. If the shares match, the result is about vertical composition, not about the top.
- **Report bond multiplicity.** For rulers, record whether the least bond is unique or there are many. Many parallel chains is a different picture from a single thread.
