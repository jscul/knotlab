# Larger spacings

Epic `SPACING-20261109-001` (program foundations), 2026-11-09. A pre-registered frozen census.

## The question

- **Where it comes from.** Backlog B57. `ISOLATION-NEED-20261109-001` found doubling schedules that keep every stage balanced while rings
  hear each other at g = 3, and `GROW-HEAR-20261109-001` found that the hearing stays inside each original ring's territory. The
  coordinator gave larger spacings the go-ahead on 2026-11-09: can influence cross a territory border with balance kept?
- **The question.** At g = 4 and 5, does some doubling schedule keep every stage balanced while an original ring is heard by another?

## Conclusions

| # | Conclusion | Kind | Ticket |
| --- | --- | --- | --- |
| 1 | **No border is crossed.** In all eight schedules (g = 4 and 5, doubling every 1 to 4 lags) no original ring ever hears ring (0, 0), and its reach stays below one original spacing (at most 51/64). | exploratory, exact | A |
| 2 | **g = 5 keeps balance with hearing; g = 4 does not.** At g = 5 doubling every 2, 3 and 4 lags keeps every stage balanced to 24 × 24 while 720 to 1,728 own cells hear another ring; at g = 4 every hearing schedule is unbalanced at 12 × 12. With g = 2 and 3, balance with hearing appears exactly at the odd spacings read, whose corners hold an even number of own cells. | exploratory, exact | A |

## Answer

Not at these spacings. Odd spacings let a growing plane keep its knots while rings hear each other, but in every schedule read, at
every spacing from 2 to 5, the hearing stays inside the original rings' territories while doubling is at most every 4 lags; the only
schedules read that let influence cross a border (doubling every 6 or 8 lags at g = 2) lost balance. Whether slower doubling at an odd
spacing can cross borders and keep balance is the question this leaves.

## Reading

**Interpretation, not a theorem.**
- **Territories are the rule so far.** Fast enough refinement keeps each original ring's influence inside its own region; slow enough
  refinement lets it out but, at g = 2, breaks balance. The odd spacings may be the ones where the two can meet.
- **The parity of a corner.** Balance with hearing needs corners of an even number of own cells in every case read, a pattern for the
  lemma of B55.

## Lag cutoffs and census-only claims

- **Exact.** **Census-only.** Both conclusions; balance computed, not proved.

## Stress test

| Claim | Check | Result |
| --- | --- | --- |
| The census | the frozen contract's controls (g = 3 readings of `ISOLATION-NEED-20261109-001` and `GROW-HEAR-20261109-001`) | consistent: the same pattern at g = 5 as at g = 3 |

## Literature and provenance

- **Classification.** New as far as found, a frozen exploratory census.

## Workspace assumptions

- **Relied on.** A30, A32, A44, A45. **Added.** None.

## Ratio

- **Substantive.** One frozen exploratory census (A), eight runs. **Administrative.** The pre-registration, this note and the closure.

## Pending the owner

- Nothing new.

## Next steps

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — larger spacings | **Status:** Successful | Read exactly: no border crossed at g = 4, 5; balance with hearing at g = 5 |
| Local direction — crossing a border with balance | Research directions | Not found at P ≤ 4; slower doubling at odd spacings is untried |
| Broader exploration — G1 with G5 | Known alternatives | Why g = 3 keeps balance (B55); growth that stops (B56); B39 |
| Long-term goal — G1 Space from a law (question 9) | Obstruction learned | At every spacing read, growing planes that keep their knots keep their territories apart |

**Corrections:** none. **Goals:** a G1 and G5 checkpoint (obstruction learned), B57 marked taken, sub-goal B63 added. **Assumptions:** none.

**Next step:** Research directions — #2, B55, as the coordinator asked; #1 recorded as sub-goal B63.

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Crossing a border with balance at odd spacings (B63) | 3/3 — Major | 3/3 — Ready | Doubling every 6, 8, 12 and 16 lags at g = 3 and 5: read whether an original ring is heard by another and whether every stage stays balanced → the first schedule that does both, a grown plane that keeps its knots and reads distance across territories, or none | Sub-goal (not taken: B55 first, coordinator) |
| 2 | Why odd spacings keep balance (B55) | 2/3 — Substantial | 2/3 — Testable | Territory confinement plus the transfer lemma, with the parity of a corner's own cells → a proof | Selected (coordinator) |
| 3 | Growth that stops (B56) | 2/3 — Substantial | 2/3 — Testable | As recorded | Alternative · deferred |
| 4 | Invertible substrate (B39) | 2/3 — Substantial | 3/3 — Ready | As before | Alternative · deferred |

1. **Crossing at odd spacings.** Payoff 3: it is the one test left of whether a growing plane can keep its knots and read distance across
   its territories. Concreteness 3: the census and reach code is ready. Not taken because the coordinator put B55 next; recorded as
   sub-goal B63 under G1.
2. **Why odd spacings.** Payoff 2: a theorem for conclusion 2. Concreteness 2.
3. **Growth that stops.** As recorded.
4. **Invertible substrate.** As before.

**Recommendation.** Research directions, #2 (B55) as the coordinator asked, with #1 kept as a sub-goal.
