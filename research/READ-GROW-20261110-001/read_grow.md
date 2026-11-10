# Reading distance while growing

Epic `READ-GROW-20261110-001` (program foundations), 2026-11-10. A frozen exploratory census (ticket A, pre-registered in `4b860ceee`).

## The question

- **Where it comes from.** Sub-goal B89, recorded by `CROSS-WHY-20261110-001`: on the 3 × 3 tube, uneven doubling schedules let original
  rings hear their neighbours with every stage balanced, to 48 × 48, but nine territories read only who hears whom. The coordinator gave
  B89 the go-ahead on 2026-11-10, asking that "reads distance" be defined before running.
- **The question.** On the 5 × 5 tube at g = 3, does some schedule keep every stage balanced while original rings are heard at distance
  1 and then at distance 2, and do the hearing lags form a metric?

## What "reads distance" means here

Frozen in the contract before any run:
- **Distance** between original rings is the taxicab distance |v| of their displacement on the original 5 × 5 torus, the contact graph's
  ring distance. The **hearing lag** L(v) is the first lag at which an own cell of the original ring at displacement v depends on ring
  (0, 0)'s first row: a counted number of lags (A40).
- **Reads distance 1 then 2 (O1)**: every stage balanced through 40 × 40, all four rings at distance 1 heard, and every distance-1 lag
  below every distance-2 lag. **Across growth (O2)**: distance 2 first heard after more doublings than distance 1.
- **A metric, not just an order (O3)**: every ring heard; L symmetric; the triangle inequality L(u + w) ≤ L(u) + L(w); and, to read the
  lattice distance, L constant on taxicab classes and strictly increasing in |v|.

## Conclusions

| # | Conclusion | Kind | Ticket |
| --- | --- | --- | --- |
| 1 | **The growing plane reads distance 1, then 2.** Five two-run schedules keep every stage balanced at 10 × 10, 20 × 20 and 40 × 40 while the four rings at distance 1 hear ring (0, 0) before any ring at distance 2: [12, 28], [28, 1], [28, 2], [35, 1], [43, 1]. Two are confirmed on the full state and by an independently written code. | exploratory, exact | A |
| 2 | **Across a doubling.** In [12, 28] distance 1 is heard in the first run (lag 8) and distance 2 only in the second, after the doubling at lag 12 (lags 23 and 32). | exploratory, exact | A |
| 3 | **In one pause, taxicab distance exactly.** [35, 1] and [43, 1] hear every ring at distance 1, 2 and 3 in their first run, at lags 8, 20 and 32: L = 12|v| − 4, the same on each taxicab class. | exploratory, exact | A |
| 4 | **After a doubling, not taxicab.** [12, 28]'s second run hears the four diagonal rings at lag 23 and the four straight rings at distance 2 at lag 32. | exploratory, exact | A |
| 5 | **No metric (O3 not met).** No balanced schedule hears the rings at distance 4, and where defined the lags break the triangle inequality by their offset (L(2, 0) = 20 > 2 L(1, 0) = 16). | exploratory, exact | A |
| 6 | **One size past.** The first four O1 schedules, extended by a run of 1 or 2 lags, at 80 × 80 under both codes: stress test pending (READ-GROW-A1). | exploratory, exact | A |

## Answer

Yes for the first step, no for a metric. A uniform local law, with a declared schedule, grows the 5 × 5 tube's plane to 40 × 40 with
every stage balanced while its original rings hear each other in order of distance: nearest first, then distance 2, in one schedule
only after more growth. During a pause the fixed stage reads the board's taxicab distance exactly, as a fixed torus does; after a
doubling the reading departs from taxicab, the diagonal ring heard before the straight one. The lags are an order and an affine
reading of taxicab distance on what is heard, not a metric: the farthest rings are never heard while every stage stays balanced, and
the lags' offset breaks the triangle inequality. Every result is to 40 × 40; balance at larger sizes is pending one size past, and at
every size open.

## Reading

**Interpretation, not a theorem.**
- **The board is still drawn (A51).** What the pause reads is the declared board's own taxicab distance, recovered by the dynamics: the
  reading does not choose the board, so these results rest on A51 and do not bear against it. What growth adds is that the reading
  after a doubling is not the board's taxicab distance, a first sign that the growth law, not only the board, shapes what is read.
- **Reading and growth interleave.** In [12, 28] the plane reads distance 1, grows, and reads distance 2, keeping its knots throughout,
  to 40 × 40.

## Lag cutoffs and census-only claims

- **Exact per reading.** **Census-only.** All conclusions: one tube, one spacing, the frozen ranges; balance computed, not proved.

## Stress test

| Claim | One size past | Result |
| --- | --- | --- |
| Reading distance 1 then 2 with every stage balanced (1) | the first four O1 schedules with one more run of 1 or 2 lags, at 80 × 80, under code 1 and code 2 | **stress test pending** (READ-GROW-A1 in `docs/LONG_RUNNING.md`) |
| The two codes (1) | eleven schedules, and the first two O1 schedules at 40 × 40 | pass (`C.json`, `V.json`) |

## Literature and provenance

- **Sources.** Light cones of additive automata (Martin, Odlyzko and Wolfram 1984); the program's distance across time
  (`DISTANCE-20261108-001`).
- **Classification.** New as far as found, a frozen exploratory census.

## Workspace assumptions

- **Relied on.** A30, A32, A40 (counted lags), A42, A44, A45, A51 (the board declared). **Added.** None. A history line on A51.

## Ratio

- **Substantive.** One frozen census (A) in four parts, with a second code written for it. **Administrative.** The pre-registration,
  this note and the closure.

## Pending the owner

- Nothing new.

## Next steps

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — reading distance while growing | **Status:** Partially successful | Distance 1 then 2 read with every stage balanced to 40 × 40, once across a doubling; no metric |
| Local direction — a grown plane that reads its own metric | Continue | The order is read; the farthest rings and the triangle inequality are what is missing |
| Broader exploration — G1 with G5 | Known alternatives | Growth that rounds the reading; why a run keeps balance; a pause the network chooses |
| Long-term goal — G1 Space from a law (question 9) | Capability gained | A local law, with a declared schedule, grows a plane that keeps its knots while reading its distances in order, to 40 × 40 |

**Corrections:** none. **Goals:** a G1 and G5 checkpoint (capability gained); B89 taken; sub-goal B102 (a metric while growing)
recorded. **Assumptions:** a history line on A51.

**Next step:** Research directions — selected: #1, awaiting the coordinator's go-ahead.

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | A metric while growing (B102) | 3/3 — Major | 2/3 — Testable | On the 5 × 5 and 7 × 7 tubes, three-run schedules (two pauses) read with the territory reader, and the lags measured from each ring's own first hearing (removing the offset) or by freezes (A41) → a schedule hearing every ring with every stage balanced whose lags are symmetric and subadditive, or the distance beyond which every balanced schedule read is deaf | Selected · awaiting go-ahead |
| 2 | Growth that rounds the reading | 2/3 — Substantial | 3/3 — Ready | Read the hearing lags of every balanced schedule with a long second pause on the 5 × 5 and 7 × 7 tubes, diagonal against straight → whether growth reads a distance rounder than the board's taxicab one, or the diagonal lead is one schedule's accident | Alternative · deferred |
| 3 | Why a run keeps balance (was `CROSS-WHY-20261110-001#2`) | 2/3 — Substantial | 2/3 — Testable | As recorded | Alternative · deferred |
| 4 | A pause the network chooses (was `CROSS-WHY-20261110-001#4`) | 2/3 — Substantial | 1/3 — Exploratory | As recorded | Alternative · deferred |

1. **A metric while growing.** Payoff 3: question 9 asks for a space a uniform local law makes that reads its own distance; a metric read
   while the plane grows and keeps its knots would be that, with the board still declared. Concreteness 2: the tools are ready; the
   uncertainties are whether any balanced schedule hears the farthest rings, and which offset-free lag is native.
2. **Growth that rounds the reading.** Payoff 2: the owner's interest in roundness, read from growth rather than drawn; one schedule so
   far. Concreteness 3: the census code runs it unchanged.
3. **Why a run keeps balance.** As in `CROSS-WHY-20261110-001`.
4. **A pause the network chooses.** As in `CROSS-WHY-20261110-001`.

**Recommendation.** Research directions, #1; stop it at a balanced schedule whose lags form a metric, or at the distance beyond which
every balanced schedule read is deaf.

## Final report as sent

Sent to the owner on 2026-11-10 at 04:06 UTC and copied here verbatim.

**Reading distance while growing (B89) is closed and published. The growing plane reads its distances in order and keeps its knots, but the readings don't form a metric yet.** ([decision note](https://github.com/jscul/knotlab/blob/main/research/READ-GROW-20261110-001/read_grow.md))

- **What "reads distance" meant (frozen before running):** the lag at which each original ring first hears ring (0, 0), against taxicab distance on the 5 × 5 tube. A metric would also need every ring heard, symmetry, and the triangle inequality.
- **Distances in order** (exact census): five schedules keep every stage balanced at 10, 20 and 40 × 40 while the four nearest rings hear before any ring two away. In [12, 28] the plane hears distance 1, doubles, and only then hears distance 2. Two schedules are confirmed on the full state and by a second code I wrote from scratch.
- **What a pause reads:** lags 8, 20 and 32 at distances 1, 2 and 3. That is exactly the drawn board's taxicab distance. After a doubling, the diagonal ring is heard before the straight one two away, so it's no longer taxicab.
- **Not a metric:** the farthest rings are never heard while every stage stays balanced, and the lags' offset breaks the triangle inequality.
- **Sizes:** everything holds to 40 × 40. The 80 × 80 check with both codes is still running, and balance at every size is open.
- **On A51:** these results rest on it. The board is declared, and the reading recovers it rather than choosing it.

| Scope | Verdict | Why |
|---|---|---|
| This attempt: reading distance while growing | Partially successful | Distances read in order to 40 × 40, once across a doubling; no metric |
| Local direction: a grown plane that reads its own metric | Continue | The order is there; the farthest rings and the triangle inequality are missing |
| Broader exploration: G1 with G5 | Known alternatives | Growth that rounds the reading; why a run keeps balance; a pause the network chooses |
| Long-term goal: G1 Space from a law | Capability gained | A local law with a declared schedule grows a plane that keeps its knots while reading its distances in order |

| # | Direction | Payoff | Concreteness | First step → stop |
|---|---|---|---|---|
| 1 | A metric while growing (B102) | 3/3 | 2/3 | Two pauses on 5 × 5 and 7 × 7, lags read without their offset or through freezes → a balanced schedule whose lags form a metric, or the distance beyond which every one is deaf |
| 2 | Growth that rounds the reading | 2/3 | 3/3 | Diagonal against straight across all long second pauses → rounder than taxicab, or one schedule's accident |
| 3 | Why a run keeps balance | 2/3 | 2/3 | As recorded |
| 4 | A pause the network chooses | 2/3 | 1/3 | As recorded |

**Corrections:** none new. **Goals:** G1/G5 checkpoint (capability gained); B89 taken; sub-goal B102 recorded. **Assumptions:** a history line on A51.

I recommend #1 and will wait for the go-ahead. I'll report the 80 × 80 result when it lands.
