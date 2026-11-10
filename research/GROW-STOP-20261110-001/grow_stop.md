# Growth that stops

Epic `GROW-STOP-20261110-001` (program foundations), 2026-11-10.

## The question

- **Where it comes from.** Backlog B56. In every schedule read, a network that grows while it runs keeps its knots or reads distance across
  its grown plane, not both (`CROSS-BORDER-20261110-001`). The coordinator gave B56 the go-ahead on 2026-11-10 as the pivot: is the grown
  plane useful at all once growth ends?
- **The question.** Grow by doubling for k lags, stop, and read what distance the stopped network reads between its rings.

## Conclusions

| # | Conclusion | Kind | Ticket |
| --- | --- | --- | --- |
| 1 | **Stopped, the grown plane is the fixed torus.** After doubling every lag for k lags and a stop, every need of every ring, with or without freezes from the stop on, is the fixed (n·2^k × m·2^k)-torus's; so it reads that torus's cut length, time length and plain first need, its original rings 2^k ring steps apart per original step. | proved; checked at the cell level (21,456 pairs) | A |
| 2 | **Hearing before the stop spoils it.** Schedules whose rings heard each other before the stop (doubling every 2 or 4 lags at g = 2 and 3) leave a stopped network whose needs differ from the fixed torus's for most pairs; the isolating schedule every 3 lags at g = 2 reads the fixed torus exactly. | computed | A |

## Answer

Yes. The plane the doubling law grows reads no distance while it grows, but once growth stops it reads, for every ring and every
reading, exactly the distances of a fixed square torus of the grown size, with its original rings spread 2^k ring steps apart: a space
that the law has made and that reads its own distance after it is made. Its plain first need is late, as on every square torus with
both sides at least 6, so the distance is read through freezes.

## Reading

**Interpretation, not a theorem.**
- **Making and reading are two phases.** In every law read, growth and the reading of distance across the grown plane do not overlap;
  growth that isolates its rings leaves, when it stops, a network that is a fixed torus for every reading, as if it had been given.
- **The expansion is read.** Two original rings that were D apart are 2^k·D ring steps apart after k doublings: the distance the stopped
  plane reads between them grows with the growth it went through.

## Lag cutoffs and census-only claims

- **The theorem has no cutoff**; the cell-level check reads 60 lags after the stop. **Census-only.** Conclusion 2.

## Stress test

| Claim | Check | Result |
| --- | --- | --- |
| The theorem (1) | k = 3 from 3 × 3 (24 × 24 final torus), and g = 3 | pass (check 1) |

## Literature and provenance

- **Classification.** Known-with-delta: a corollary of the transfer lemma.

## Workspace assumptions

- **Relied on.** A30, A32, A38, A40, A41, A44, A45. **Added.** None.

## Ratio

- **Substantive.** One proof (A) with three checks. **Administrative.** This note and the closure.

## Pending the owner

- Nothing new.

## Next steps

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — growth that stops | **Status:** Successful | Proved: the stopped plane reads the fixed torus's distances, scaled by 2^k |
| Local direction — grown space and distance | Continue | Growth then reading works; what remains is whether growth can be shaped, not only doubled |
| Broader exploration — G1 with G5 | Known alternatives | Invertible substrate (B39, next); the proof pair for the exclusion (B55, why crossing breaks balance) |
| Long-term goal — G1 Space from a law (question 9) | Capability gained | A uniform local law grows a plane while running, keeps every stage balanced, and, once it stops, reads its own distance as a fixed torus does |

**Corrections:** none. **Goals:** a G1 and G5 checkpoint (capability gained), B56 marked taken. **Assumptions:** none.

**Next step:** Research directions — B39, as the coordinator asked.

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Invertible substrate (B39) | 2/3 — Substantial | 3/3 — Ready | A rule and contact law with an invertible one-step map and persistent contacts on a tube, then growth while running → knots across growth with rings hearing each other across territories, or no such substrate | Selected (coordinator) |
| 2 | Why odd spacings keep balance (B55) | 2/3 — Substantial | 2/3 — Testable | As recorded | Alternative · deferred |
| 3 | Why crossing breaks balance | 2/3 — Substantial | 2/3 — Testable | As recorded | Alternative · deferred |
| 4 | Shaped growth that stops | 2/3 — Substantial | 2/3 — Testable | Double only some territories before stopping, and read whether the stopped network is a fixed network of the grown shape → a law that grows a chosen shape and reads it | Alternative · deferred |

**Recommendation.** Research directions, #1 as the coordinator asked.
