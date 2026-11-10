# Crossing a territory border with balance

Epic `CROSS-BORDER-20261110-001` (program foundations), 2026-11-10. A pre-registered frozen census of sub-goal B63.

## The question

- **Where it comes from.** Sub-goal B63, recorded by `SPACING-20261109-001`: growing planes at odd spacings keep their knots while rings
  hear each other, but only inside territories. The coordinator gave B63 the go-ahead on 2026-11-10: does slower doubling at g = 3 and 5
  let influence cross a border with every stage balanced?
- **The question.** With doubling every 6, 8, 12 or 16 lags at g = 3 and 5, does an original ring get heard by another while every
  stage stays balanced?

## Conclusions

| # | Conclusion | Kind | Ticket |
| --- | --- | --- | --- |
| 1 | **Slow doubling crosses borders.** At g = 3 the nearest original rings hear ring (0, 0) from lag 8 when doubling every 8, 12 or 16 lags, and those at distance 2 later; at g = 5 the nearest hear it from lag 12 when doubling every 12 or 16 lags. | exploratory, exact | A |
| 2 | **Crossing breaks balance.** Every schedule that crosses a border has an unbalanced stage by 24 × 24: at the next doubling (g = 3, P = 8) or the one after (the rest). | exploratory, exact | A |
| 3 | **Without crossing, balance can hold.** g = 5 doubling every 6 lags keeps every stage balanced to 24 × 24 while rings hear each other inside their territories. | exploratory, exact | A |

## Answer

No. At both odd spacings, doubling slow enough for influence to cross a territory border loses balance within two doublings of the
crossing, as at g = 2. Across every schedule read (g = 2, 3, 4, 5), a growing plane keeps its knots across growth only while its
original rings' territories do not hear each other, so it never reads a distance between them while it grows.

## Reading

**Interpretation, not a theorem.**
- **The exclusion, in its narrowest form.** Hearing as such is compatible with balance (odd spacings, inside territories). What is not,
  in every schedule read, is hearing across territories followed by more growth: the mixtures that cross a border are what the next
  doubling cannot carry.
- **For G1 and G5.** A network that grows while it runs keeps its knots or reads its distance across its grown plane, not both, in
  every law read. Distance across the grown plane is read only once growth stops (sub-goal B56's direction).

## Lag cutoffs and census-only claims

- **Exact.** **Census-only.** All conclusions: one tube, P = 6 to 16, balance to 24 × 24, computed, not proved.

## Stress test

| Claim | Check | Result |
| --- | --- | --- |
| The census | the frozen control (g = 2: P = 6, 8 crossed and lost balance) | consistent: the same at g = 3 and 5 |

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
| This attempt — crossing a border with balance | **Status:** Successful | Read exactly: crossing breaks balance within two doublings at g = 3 and 5 |
| Local direction — a grown plane that keeps its knots and reads distance while growing | Full pivot | Not had together in any schedule read at g = 2 to 5 |
| Broader exploration — G1 with G5 | Known alternatives | Growth that stops (B56); why odd spacings keep balance (B55); B39 |
| Long-term goal — G1 Space from a law (question 9) | Obstruction learned | While a network grows, keeping its knots and reading distance across its grown plane exclude each other, in every law read |

**Corrections:** none. **Goals:** a G1 and G5 checkpoint (obstruction learned), sub-goal B63 marked taken. **Assumptions:** none.

**Next step:** Research directions — #1, B55, as the coordinator asked.

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Why odd spacings keep balance (B55) | 2/3 — Substantial | 2/3 — Testable | Territory confinement plus the transfer lemma, with the parity of a corner's own cells → a proof | Selected (coordinator) |
| 2 | Growth that stops (B56) | 2/3 — Substantial | 2/3 — Testable | Double for k lags, stop, and read the distance the stopped network reads between its territories, as a function of k → a law | Alternative · deferred |
| 3 | Why crossing breaks balance | 2/3 — Substantial | 2/3 — Testable | Read the returns of the first unbalanced contact after a crossing → the mechanism, toward a proof of the exclusion | Alternative · deferred |
| 4 | Invertible substrate (B39) | 2/3 — Substantial | 3/3 — Ready | As before | Alternative · deferred |

**Recommendation.** Research directions, #1 as ordered.

## Final report as sent

Sent to the owner on 2026-11-10 at 00:12 UTC and copied here verbatim.

**Crossing a territory border with balance (sub-goal B63) is closed and published, pre-registered. Crossing breaks balance.** ([decision note](https://github.com/jscul/knotlab/blob/main/research/CROSS-BORDER-20261110-001/cross_border.md))

- **Slow doubling does cross borders:** at g = 3, doubling every 8 to 16 lags lets the nearest original rings hear each other from lag 8. At g = 5 that happens every 12 to 16 lags.
- **And every such schedule loses balance** within two doublings of the crossing (exact, to 24 × 24), as at g = 2.
- **Without crossing, balance can hold:** g = 5 doubling every 6 lags stays balanced while rings hear each other inside their territories.

So across g = 2 to 5 and every schedule read, a network that grows while it runs keeps its knots, or reads distance across its grown plane, but not both.

| Scope | Verdict | Why |
|---|---|---|
| This attempt: crossing a border with balance | Successful | Crossing breaks balance within two doublings at g = 3 and 5 |
| Local direction: knots plus distance while growing | Full pivot | Not had together in any schedule read |
| Broader exploration: G1 with G5 | Known alternatives | Growth that stops (B56); why odd g keeps balance (B55); B39 |
| Long-term goal: G1 Space from a law | Obstruction learned | While growing, keeping knots and reading distance across the plane exclude each other, in every law read |

| # | Direction | Payoff | Concreteness | First step → stop |
|---|---|---|---|---|
| 1 | Why odd spacings keep balance (B55) | 2/3 | 2/3 | Territory confinement plus the transfer lemma → a proof |
| 2 | Growth that stops (B56) | 2/3 | 2/3 | Double for k lags, stop, read the distance → a law in k |
| 3 | Why crossing breaks balance | 2/3 | 2/3 | Read the first failing contact's returns → toward proving the exclusion |
| 4 | Invertible substrate (B39) | 2/3 | 3/3 | As before |

**Corrections:** none. **Goals:** G1/G5 checkpoint; sub-goal B63 taken. **Assumptions:** none. **Long-running:** CROSS-BORDER-A1 is folded in and awaits sign-off.

B55 is next, as agreed. This thread has now closed thirteen epics; the growth line has reached a clear exclusion, so a pause after B55 would be reasonable too.
