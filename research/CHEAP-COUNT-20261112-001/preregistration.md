# The cheapest counter: pre-registration

Epic `CHEAP-COUNT-20261112-001` (`TWO-BIT-ROWS-20261112-001` direction 2; G17, with G1), 2026-11-12, at the owner's go-ahead ("Yes,
start it."). Frozen before the registered run. The canonical K1–K3 test is unchanged. The law is NAE on three-place knots on
distinct distinctions; **fresh** (helper) distinctions are existential, each used only inside the knots that need it.

## The question

`ROW-NEST-20261112-001`'s referee showed that growing generations (each one position longer; the literature's rows) count depth in
binary when each new main distinction is the parity of old ones read against one reference distinction R (the additive rules 60,
90, 150; Martin, Odlyzko and Wolfram 1984), and that a parity needs fresh distinctions. What is the fewest NAE knots that make that
parity, so the cheapest counter of this kind; how fragile is it to one changed knot; how much weight does counting get under short
descriptions; and does a hopping version (the new position reading the old one at half its index, the owner's nested reach) count?

## In standard terms

The minimum number of NAE₃ constraints in a primitive positive definition of 4-ary even parity with f auxiliary variables; the
satisfiability, by depth, of the additive cellular-automaton triangles built from it; and its robustness.

## Settled or known (stated, not tested)

- Definability of the parity (Böhler et al. 2005) and the counting pattern of rules 60, 90 and 150 (Martin, Odlyzko and Wolfram)
  are known; with a gadget that projects exactly onto the parity and fresh distinctions disjoint per position, the counter is
  rule 60 by composition, so building it is a **wiring check**, not a prediction.
- No knot may lie on three named distinctions (it would forbid 0000); with 0, 1 or 2 fresh distinctions no gadget exists (the
  advisor's hand argument), so the search decides f = 3 to 6 (f = 0 to 2 are run as certificates).
- No finite depth shows non-periodicity; the counting claim for rules 60, 90 and 150 rests on the known algebra; the census reads to
  depth 64 as a check. Counting needs 1 + f distinctions per position (one main and f helpers); with one or two per position and no
  helpers nothing counted (`ROW-NEST-20261112-001`, `TWO-BIT-ROWS-20261112-001`).

## Design (frozen in `census.py`)

S1 exact synthesis (SAT with a cardinality bound) of m*(f) for f = 0..6, and every minimal gadget at the least f (cap 20,000 or ten
minutes). S2 the growth (first generation 3, missing old positions read as R, the last generation's mains closed by NAE on
consecutive triples) for rules 60, 90, 150, 102 and the hopping rule (new i, old ⌊i/2⌋, old i, R), with the parity as exact clauses,
and for rule 60 and the hopping rule also through the minimal gadget; alive(t) to depth 64. S3 every single-knot deletion or
replacement of the minimal gadget: its relation on the named four, and rule 60's growth with that relation to depth 64.
Weight: the code of the row language with h = f helpers per position (relative distinctions: old i − 1, i, i + 1 and new i − 1, i,
each with its main and h helpers, plus R) gives a rule of m knots 2^−(gamma(h) + gamma(m + 1) + log₂ C(C(5(1 + h) + 1, 3), m)) bits; the
counting share is the number of counting descriptions found (minimal gadgets × rules 60, 90, 150) times that.

## Predictions (frozen)

| # | Prediction | Fails when |
| --- | --- | --- |
| G | Gate: the gadget-built rule-60 growth's life equals the exact-clause one at every depth to 64, and rule 60's life is the referee's (1–6, 11–14, 27–30 within 40). | any difference |
| P1 | **m* has plateaued:** m*(5) = m*(6). | m*(6) < m*(5) |
| P2 | **The counter is fragile:** fewer than 10% of single-knot changes of the minimal gadget still count (same parity, or life unexplained within 64). | 10% or more |
| P3 | **Hopping counts too:** the hopping rule's life is unexplained within 64 (no period ≤ 16 from depth ≤ 32). | it is constant or periodic |
| — | Reported: m*(f), the number of minimal gadgets, distinctions per position, rules 90, 150, 102, the weight share. | — |

The advisor model reviewed a draft cold (`advisor_review_answer.md`): it made the counter a wiring check, gave the f ≤ 2
infeasibility, asked for the plateau check, the weight share as the headline and single-knot fragility in place of blind sampling.

## Plumbing (disclosed)

The exact-clause rule-60 growth was checked to depth 8 against the referee's known pattern (alive at 1 to 6, dead at 7 and 8). Nothing
else was run.

## Stop rule and runtime

S1, S2, S3 once (S1's enumeration capped at ten minutes; the rest minutes), the summary, a hand-off to the referee thread, report.
