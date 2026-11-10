# A metric while growing

Epic `METRIC-GROW-20261110-001` (program foundations), 2026-11-10. A frozen exploratory census (ticket A, pre-registered in `f8ca8d169`).

## The question

- **Where it comes from.** Sub-goal B102, recorded by `READ-GROW-20261110-001`: on the 5 × 5 tube, a growing plane with every stage
  balanced hears its original rings in order of distance, but the hearing lags form no metric (the farthest rings unheard, the offset
  breaking the triangle inequality). The coordinator gave B102 the go-ahead on 2026-11-10, asking that what counts as a metric, and how
  any offset is handled, be frozen before running.
- **The question.** Does some doubling schedule with every stage balanced reach every original ring, with time lengths that form a
  metric while the plane grows?

## What counts as a metric here

Frozen in the contract before any run:
- **Time length** is read through freezes (A41), the program's reading of distance across time: T1(v) is the first lag at which a route
  of the growing network carries ring (0, 0)'s own cell at position 1 to the same cell of the ring at v, each value confirmed by an
  explicit freeze that leaves one such route open. T (ring to ring) and the plain hearing lag L are read beside it.
- **The round trip** R1(v) = T1(v) + T1(−v), out and back, is symmetric by construction; no offset is subtracted from anything.
- **A metric (M1)** needs R1 on every original ring and the triangle inequality R1(u + w) ≤ R1(u) + R1(w); **reading the lattice
  distance (M2)** also needs R1 constant and increasing on taxicab classes. Readings are taken only while the plane grows. The failure
  outcome is the **deaf distance**: beyond it, every balanced schedule read reaches no ring both ways.

## Conclusions

| # | Conclusion | Kind | Ticket |
| --- | --- | --- | --- |
| 1 | **No metric on the 5 × 5 tube (M1 not met).** Of 42 schedules with every stage balanced to 40 × 40, one, [28, 60], reaches every original ring both ways; its round trip is symmetric and breaks the triangle inequality 60 times: R1(−2, −2) = 138 > R1(−2, −1) + R1(0, −1) = 90 + 36. Code 2 agrees on it. | exploratory, exact | A |
| 2 | **Nothing is deaf on 5 × 5.** [28, 60] reaches every ring; no other balanced schedule reaches beyond distance 2 both ways. | exploratory, exact | A |
| 3 | **The triangle fails only across a doubling.** In all 14 two-run schedules with enough readings, every violation of the directed T1 involves a target reached after the first doubling, none one reached within the first run; within one stage a route to u followed by the translate of a route to w is a route to u + w, so the time length is subadditive there. | the census exact; the within-stage bound by hand | A |
| 4 | **Far costs more than the sum of near.** In [28, 60], R1 is 36 at distance 1, 48 and 60 at 2, 90 and 102 at 3, 138 and 150 at 4: after the doubling at lag 28 doubles the ring steps between original rings, every leg is slower. | exploratory, exact | A |
| 5 | **Every reading was read through freezes**, except three T1 values, dropped from R1 as frozen. | exploratory, exact | A |
| 6 | **The 7 × 7 half: deaf beyond distance 4.** One long run of 1 to 72 lags, then 1 or 2: nine first runs keep the second stage balanced and eight two-run schedules every stage to 56 × 56. The best, [60, 1], reaches every ring within taxicab distance 4 out and back, all inside its first stage, with no triangle violation; rings at distance 5 and 6 are not all reached, so no schedule meets M1. Code 2 agrees on [60, 1]'s readings (METRIC-GROW-A1, folded in 2026-11-10). | exploratory, exact | A |

## Answer

No, on the 5 × 5 tube. A growing plane can keep every stage balanced while every original ring is reached out and back, but its time
lengths, read through freezes as the program reads distance across time, are not a metric: far rings cost more than the sum of near
trips. The excess appears only when a trip crosses a doubling; within one stage the time length is subadditive, as on a fixed network.
So what breaks the metric is not the reading but the growth: the plane expands while it is being read. Every result is to 40 × 40;
on the 7 × 7 tube every balanced schedule read is deaf beyond distance 4.

## Reading

**Interpretation, not a theorem.**
- **Expansion, read natively.** The triangle excess R1(u + w) − R1(u) − R1(w) is zero within a stage and positive across a doubling:
  a native measure of how much the plane grew during a trip. The resemblance to distances in an expanding space is a resemblance of
  counting, not a physics claim.
- **Two phases, again, for a metric.** `GROW-STOP-20261110-001` proved that a stopped plane reads the fixed torus's distances; here, a
  plane that keeps growing reads an order and a round trip, but its metric holds only between doublings.
- **The board is still drawn (A51).** As in `READ-GROW-20261110-001`, the board is declared; these results rest on A51 and do not bear
  against it.

## Lag cutoffs and census-only claims

- **Exact per reading.** **Census-only.** Conclusions 1 to 5 on one tube; the within-stage subadditivity in conclusion 3 is an
  elementary argument, the rest computed; balance computed, not proved.

## Stress test

| Claim | One size past | Result |
| --- | --- | --- |
| No metric on 5 × 5 (1) | the frozen X runs only on M1 positives; there were none | not applicable |
| The two codes (1) | seven schedules (C), and [28, 60] at 40 × 40 | pass (`C.json`, `V5_at_close.json`) |
| The 7 × 7 half (6) | the frozen S7 and V | read: deaf beyond distance 4; code 2 agrees on [60, 1]'s T, T1 and L, and on [28, 60]'s balance and readings (`S7.json`, `V.json`) |

## Literature and provenance

- **Sources.** Distance across time through freezes (`DISTANCE-20261108-001`, A41); quasi-metrics and their symmetrization by round
  trips; light cones of additive automata (Martin, Odlyzko and Wolfram 1984).
- **Classification.** New as far as found, a frozen exploratory census.

## Workspace assumptions

- **Relied on.** A30, A32, A38 (freezing), A40, A41 (time length through freezes), A42, A44, A45, A51. **Added.** None.

## Correction

**2026-11-10 · Not a block, missed prior work** (`docs/CORRECTIONS.md`). The classification "new as far as found" missed that
earliest-arrival distances in time-varying graphs need not satisfy the triangle inequality (temporal graphs: Michail 2015; arXiv
2510.01702). The census's own contribution is where the violations fall (only across doublings); their removal in conformal time is
`EXPAND-READ-20261110-001`'s and `CONF-METRIC-20261110-001`'s. Every result stands.

## Ratio

- **Substantive.** One frozen census (A), with the second code extended for it. **Administrative.** The pre-registration, this note
  and the closure.

## Pending the owner

- Nothing new.

## Next steps

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — a metric while growing | **Status:** Unsuccessful | On 5 × 5 the round trip reaches every ring with every stage balanced but breaks the triangle inequality across doublings; 7 × 7 pending |
| Local direction — a grown plane that reads its own metric | Research directions | Within a stage the reading is a metric and a stopped plane reads the fixed torus; across growth it is not |
| Broader exploration — G1 with G5 | Known alternatives | Growth that rounds the reading (B108); the expansion read as a quantity; why a run keeps balance |
| Long-term goal — G1 Space from a law (question 9) | Obstruction learned | A plane that keeps growing reads distances in order, but its time lengths are a metric only between doublings |

**Corrections:** none. **Goals:** a G1 and G5 checkpoint (obstruction learned); B102 taken. **Assumptions:** none.

**Next step:** Research directions — No next action selected (the owner rests the project for the night); #1 proposed for the morning.

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Expansion as a reading | 2/3 — Substantial | 3/3 — Ready | For every balanced schedule of this census and of `READ-GROW-20261110-001`, the triangle excess of R1 as a function of the doublings each trip crosses → a law for the excess (zero within a stage, growing with the doublings crossed), or none | Alternative · deferred |
| 2 | Growth that rounds the reading (B108) | 2/3 — Substantial | 3/3 — Ready | As recorded | Alternative · deferred |
| 3 | The 7 × 7 half | 1/3 — Incremental | 3/3 — Ready | Fold in METRIC-GROW-A1 when it finishes → 7 × 7's deaf distance and whether its single long pause yields a metric within one stage | Alternative · deferred |
| 4 | Why a run keeps balance (was `READ-GROW-20261110-001#3`) | 2/3 — Substantial | 2/3 — Testable | As recorded | Alternative · deferred |

1. **Expansion as a reading.** Payoff 2: turns the obstruction into a native quantity of growth. Concreteness 3: every number is in
   the census files. Uncertainty: whether the excess follows the doublings or the routes' geometry.
2. **B108.** Payoff 2, Concreteness 3, as recorded.
3. **The 7 × 7 half.** Payoff 1: a second tube for the same verdict. Concreteness 3: it is running.
4. **Why a run keeps balance.** As recorded.

**Recommendation.** Research directions: #1 when work resumes; nothing starts tonight.

**Basket:** B108, B55, `GROW-HORIZON-20261109-001#2`; none taken tonight, as the owner is resting the project; #1 stays in this line
because it reads the result just found.

## Final report as sent

Sent to the owner on 2026-11-10 at 07:32 UTC and copied here verbatim.

**A metric while growing (B102) is closed and published. The answer is no: a growing plane's time lengths are a metric only between doublings.** ([decision note](https://github.com/jscul/knotlab/blob/main/research/METRIC-GROW-20261110-001/metric_grow.md))

- **How it was read (frozen):** time length through freezes (A41), from one cell of ring (0, 0) to the same cell of another ring. The round trip out and back is the candidate metric, and no offset is subtracted.
- **No metric on 5 × 5** (exact census): one schedule, [28, 60], keeps every stage balanced to 40 × 40 and reaches every original ring out and back. But far rings cost more than the sum of near trips: 60 violations of the triangle inequality, such as 138 > 90 + 36. Code 2 agrees.
- **Growth is what breaks it:** every violation involves a trip that crosses a doubling. Within one stage the time length is subadditive, because routes concatenate. The plane expands while it's being read.
- **Pending:** the 7 × 7 half (stages there cycle through about 800,000 lags) is still running, along with its checks. It's registered as pending in the long-running index.

| Scope | Verdict | Why |
|---|---|---|
| This attempt: a metric while growing | Unsuccessful | Every ring reached with every stage balanced, but the triangle inequality fails across doublings |
| Local direction: a grown plane that reads its own metric | Research directions | A metric holds within a stage, and after growth stops; not across growth |
| Broader exploration: G1 with G5 | Known alternatives | Growth that rounds the reading (B108); the expansion as a quantity |
| Long-term goal: G1 Space from a law | Obstruction learned | A plane that keeps growing reads distances in order, but a metric only between doublings |

| # | Direction | Payoff | Concreteness | First step → stop |
|---|---|---|---|---|
| 1 | Expansion as a reading | 2/3 | 3/3 | The triangle excess against the doublings each trip crosses → a law for it, or none |
| 2 | Growth that rounds the reading (B108) | 2/3 | 3/3 | As recorded |
| 3 | The 7 × 7 half | 1/3 | 3/3 | Fold in when it finishes |
| 4 | Why a run keeps balance | 2/3 | 2/3 | As recorded |

**Corrections:** none. **Goals:** G1/G5 checkpoint (obstruction learned); B102 taken. **Assumptions:** none.
**Basket:** B108, B55, GROW-HORIZON-20261109-001#2. None taken, since you're resting the project tonight.

I propose #1 for the morning. As you asked, I'm stopping here with no new epic. The 7 × 7 run keeps going on its own, and I'll fold it in when you're back.
