# Expansion as a reading

Epic `EXPAND-READ-20261110-001` (program foundations), 2026-11-10. A frozen exploratory census (ticket A, pre-registered in
`59299d872`).

## The question

- **Where it comes from.** `METRIC-GROW-20261110-001`'s direction 1, given the go-ahead by the coordinator at the owner's word on
  2026-11-10. That epic found that a growing plane's time lengths, read through freezes, break the triangle inequality, and only for
  trips that cross a doubling: the plane grows while it is read.
- **The question.** Can the plane read its own expansion from its time lengths, and is the expansion the whole of the triangle excess?

## What was frozen

- **X1.** No triangle excess within a stage: a route to u followed by the translate of a route to w is a route to u + w while the
  network does not change (a theorem by concatenation, checked).
- **X2, the scale factor read.** Along an axis, the time length per original spacing is 4g 2^k lags in stage k: a front crosses one ring
  in 2g lags, and the k-th doubling makes the original spacing 2^(k+1) rings.
- **X3, a metric in conformal time.** Counting a lag after k doublings as 2^-k (A56, added), the round trip out and back satisfies the
  triangle inequality on every schedule read.

## Conclusions

| # | Conclusion | Kind | Ticket |
| --- | --- | --- | --- |
| 1 | **No excess within a stage (X1).** None of 8,987 directed triangle violations has both legs inside the first stage. | the bound by hand; checked on 891 schedules | A |
| 2 | **The scale factor is read exactly between rings (X2).** Every ring-to-ring time length along an axis grows by 4g 2^k lags per original spacing in stage k: 2,368 of 2,368 readings, at g = 2, 3 and 5 and in stages 0, 1 and 2. The cell-to-cell reading agrees in 1,586 of 1,614; the other 28, along +x or −y in 14 schedules, are shorter (30 for 40, 42 for 48), so X2 fails as frozen. | exploratory, exact | A |
| 3 | **Conformal time removes almost all of the excess (X3 fails as frozen, by a bounded residual).** In plain lags the round trip breaks the triangle inequality in 240 of 891 schedules, by up to 78 lags; in conformal time in 28 of them, all among those 240, by at most 2 conformal lags. So the conformal round trip plus 2 is a metric on every schedule read (post hoc). | exploratory, exact | A |
| 4 | **The balanced schedules agree.** Of the 43 schedules known to keep every stage balanced, X2 holds for all 116 increments and one, [28, 60], has a conformal violation of 1 lag. | exploratory, exact | A |
| 5 | **Two codes.** Code 2 agrees with code 1 on all 34 sampled schedules. | exploratory, exact | A |

## Answer

Yes, almost exactly. A plane grown by the doubling law reads its own scale factor from its time lengths: between rings, each doubling
doubles the time to cross one original spacing, with no exception in 2,368 readings, so the network's own crossings count a clock in
which a lag after k doublings is 2^-k of a lag. In that clock, the clock of the plane's first scale, the triangle excess that broke the
metric while the plane grows almost disappears: from up to 78 lags in 240 schedules to at most 2 in 28. The expansion is the excess,
up to a bounded residual: the plane's round trip time lengths are a metric up to an additive 2 in conformal time, while in plain lags
their error grows with every doubling crossed. Strictly, both X2 and X3 fail as frozen, on that small residual.

## Reading

**Interpretation, not a theorem.**
- **A growing plane that reads its metric, once its growth is read too.** `METRIC-GROW-20261110-001` found no metric while the plane
  grows; read at its own scale, it has one up to a bounded error. The resemblance to comoving distances and conformal time in an
  expanding space is a resemblance of counting, not a physics claim.
- **Is the clock native?** The weight 2^-k comes from the declared schedule's doublings, but X2 shows the network's own ring crossings
  keep that clock exactly between rings: a front's crossing time, which the network itself produces, doubles at every doubling. A56's
  challenge is answered in its favour, and it stays an assumption.
- **The board is still drawn (A51).** These are the declared board's distances read through growth; nothing here bears against A51.

## Lag cutoffs and census-only claims

- **Exact per reading.** **Census-only.** Conclusions 2 to 5: two tubes, three spacings, the frozen families; the bounded residual is
  read, not proved.

## Stress test

| Claim | Check | Result |
| --- | --- | --- |
| The scale factor (2) and the bounded residual (3) | three spacings and two tubes, beside `METRIC-GROW-20261110-001`'s g = 3 readings | pass: the same law at g = 2, 3, 5 and on 7 × 7 |
| The two codes (5) | 34 schedules | pass |

## Literature and provenance

- **Sources.** Comoving distance and conformal time in expanding models (the analogy only); quasi-metrics and coarse metrics (a metric
  up to an additive constant); `DISTANCE-20261108-001` (time length through freezes).
- **Classification.** New as far as found, a frozen exploratory census.

## Workspace assumptions

- **Relied on.** A38, A40, A41, A44, A45, A51. **Added.** A56 (conformal time), with its first test recorded.

## Ratio

- **Substantive.** One frozen census (A) in four families. **Administrative.** The pre-registration, this note and the closure.

## Pending the owner

- Nothing new.

## Next steps

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — expansion as a reading | **Status:** Partially successful | The scale factor read exactly between rings; conformal time leaves a residual of at most 2 lags in 28 of 891 schedules; both strict predictions fail on it |
| Local direction — a grown plane that reads its own metric | Continue | In conformal time the growing plane's round trips are a metric up to 2; a proof would make it a theorem |
| Broader exploration — G1 with G5 | Known alternatives | Growth that rounds the reading (B108); the residual's first runs |
| Long-term goal — G1 Space from a law (question 9) | Capability gained | A uniform local law grows a plane whose time lengths, at its own scale, are a metric up to a bounded error, and which reads its own scale factor |

**Corrections:** none. **Goals:** a G1 and G5 checkpoint (capability gained); METRIC-GROW-20261110-001#1 taken; sub-goal B125 (the
conformal metric as a theorem) recorded. **Assumptions:** A56 added and tested.

**Next step:** Research directions — selected: #1, awaiting the coordinator's go-ahead.

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | The conformal metric as a theorem (B125) | 3/3 — Major | 2/3 — Testable | Prove that a route of conformal duration τ at one stage refines to a route of conformal duration at most τ + c after a doubling (c the residual), so the conformal round trip is subadditive up to 2c at every size → a theorem that a growing plane reads a metric up to a constant at its own scale, or the step that fails | Selected · awaiting go-ahead |
| 2 | The residual's first runs | 2/3 — Substantial | 3/3 — Ready | Trace the 28 schedules' violating triples to the lag where a route meets a doubling → the cell positions that cost the residual, as a lemma | Alternative · deferred |
| 3 | Growth that rounds the reading (B108) | 2/3 — Substantial | 3/3 — Ready | As recorded | Alternative · deferred |
| 4 | Why a run keeps balance (was `READ-GROW-20261110-001#3`) | 2/3 — Substantial | 2/3 — Testable | As recorded | Alternative · deferred |

1. **The conformal metric as a theorem.** Payoff 3: question 9 asks for a space a uniform local law makes and that reads its own
   distance; a theorem that the growing plane's time lengths are, at its own scale, a metric up to a constant would give it while the
   plane grows. Concreteness 2: X2's exact crossing times suggest the refinement argument; the residual's cell positions are the
   uncertainty.
2. **The residual's first runs.** Payoff 2: explains the bound and feeds #1. Concreteness 3: every triple is in the result file.
3. **B108.** As recorded.
4. **Why a run keeps balance.** As recorded.

**Recommendation.** Research directions: #1, with #2 as its first step; stop at a proof or at the refinement step that fails.

**Basket:** B108, B55, `GROW-HORIZON-20261109-001#2`; none taken: #1 stays in this line because it turns this result into a theorem.

## Final report as sent

Sent to the owner on 2026-11-10 at 16:58 UTC and copied here verbatim.

**Expansion as a reading is closed and published. The growing plane reads its own expansion, and once that's counted, its distances are a metric up to 2.** ([decision note](https://github.com/jscul/knotlab/blob/main/research/EXPAND-READ-20261110-001/expand_read.md))

- **The scale factor, read exactly** (frozen census, 891 schedules at g = 2, 3, 5, exact): between rings, crossing one original spacing takes 4g·2^k lags after k doublings. That held in all 2,368 readings. The network's own crossings keep the clock.
- **A metric at the plane's own scale:** count a lag after k doublings as 2^−k of a lag (conformal time, new assumption A56). The round trip then breaks the triangle inequality in only 28 of 891 schedules, by at most 2. In plain lags it broke in 240 schedules, by up to 78.
- **Strictly, two of the three frozen predictions fail on that small residual.** The scale-factor prediction misses 28 of 1,614 cell-to-cell readings, and the metric prediction misses those 28 schedules by at most 2. "No excess within a stage" holds. Code 2 agrees on all 34 sampled schedules.
- **B102's 7 × 7 half is folded in:** deaf beyond distance 4.

| Scope | Verdict | Why |
|---|---|---|
| This attempt: expansion as a reading | Partially successful | Scale factor exact between rings; in conformal time a metric up to 2; strict predictions fail on the residual |
| Local direction: a grown plane that reads its own metric | Continue | At its own scale the growing plane's round trips are a metric up to 2; a proof would make it a theorem |
| Broader exploration: G1 with G5 | Known alternatives | Growth that rounds the reading (B108); where the residual comes from |
| Long-term goal: G1 Space from a law | Capability gained | A local law grows a plane that reads its own scale factor, and at that scale a metric up to a bounded error |

| # | Direction | Payoff | Concreteness | First step → stop |
|---|---|---|---|---|
| 1 | The conformal metric as a theorem (B125) | 3/3 | 2/3 | Trace the residual to where routes meet a doubling, then prove a route refines with bounded extra conformal time → a theorem, or the step that fails |
| 2 | The residual's first runs | 2/3 | 3/3 | Trace the 28 schedules' violating triples → the cell positions behind the residual |
| 3 | Growth that rounds the reading (B108) | 2/3 | 3/3 | As recorded |
| 4 | Why a run keeps balance | 2/3 | 2/3 | As recorded |

**Corrections:** none. **Goals:** G1/G5 checkpoint (capability gained); sub-goal B125 recorded. **Assumptions:** A56 added (conformal time) and tested: the network's own crossings keep that clock exactly between rings.
**Basket:** B108, B55, GROW-HORIZON-20261109-001#2. None taken: #1 stays in this line because it turns this result into a theorem.

I recommend #1 and will wait for the go-ahead. EXPAND-READ-A1 (32 seconds) is folded in and awaiting sign-off, along with B102's 7 × 7 row.
