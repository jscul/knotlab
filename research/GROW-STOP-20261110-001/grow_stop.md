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
| Broader exploration — G1 with G5 | Known alternatives | Invertible substrate (B39, next); the proof pair for the exclusion (B55, B64) |
| Long-term goal — G1 Space from a law (question 9) | Capability gained | A uniform local law grows a plane while running, keeps every stage balanced, and, once it stops, reads its own distance as a fixed torus does |

**Corrections:** none. **Goals:** a G1 and G5 checkpoint (capability gained), B56 marked taken, backlog B64 (why crossing breaks balance) and B65 (shaped growth that stops) added. **Assumptions:** none.

**Next step:** Research directions — B39, as the coordinator asked.

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Invertible substrate (B39) | 2/3 — Substantial | 3/3 — Ready | A rule and contact law with an invertible one-step map and persistent contacts on a tube, then growth while running → knots across growth with rings hearing each other across territories, or no such substrate | Selected (coordinator) |
| 2 | Why odd spacings keep balance (B55) | 2/3 — Substantial | 2/3 — Testable | As recorded | Alternative · deferred |
| 3 | Why crossing breaks balance (B64) | 2/3 — Substantial | 2/3 — Testable | As recorded | Alternative · deferred |
| 4 | Shaped growth that stops (B65) | 2/3 — Substantial | 2/3 — Testable | Double only some territories before stopping, and read whether the stopped network is a fixed network of the grown shape → a law that grows a chosen shape and reads it | Alternative · deferred |

**Recommendation.** Research directions, #1 as the coordinator asked.

## Final report as sent

Sent to the owner on 2026-11-10 at 00:23 UTC and copied here verbatim.

**Growth that stops (B56) is closed and published, and it's a proof.** ([decision note](https://github.com/jscul/knotlab/blob/main/research/GROW-STOP-20261110-001/grow_stop.md))

- **Proved:** double every lag for k lags, then stop. From then on every reading of every ring, with or without freezes, is exactly that of a fixed torus of the grown size. Two original rings D apart are now 2^k·D ring steps apart. Checked cell by cell on 21,456 pairs.
- **Computed:** schedules where rings heard each other before the stop don't read the fixed torus.
- **So:** making and reading are two phases. The plane reads no distance while it grows and its own distance once it stops.

| Scope | Verdict | Why |
|---|---|---|
| This attempt: growth that stops | Successful | Proved: the stopped plane reads the fixed torus, scaled by 2^k |
| Local direction: grown space and distance | Continue | Growth then reading works |
| Broader exploration: G1 with G5 | Known alternatives | B39 next; the proof pair B55 and B64 |
| Long-term goal: G1 Space from a law | Capability gained | A local law grows a plane and then reads its own distance |

| # | Direction | Payoff | Concreteness | First step → stop |
|---|---|---|---|---|
| 1 | Invertible substrate (B39) | 2/3 | 3/3 | A rule with an invertible step and persistent contacts, then growth while running → knots kept across growth with hearing, or no such substrate |
| 2 | Why odd spacings keep balance (B55) | 2/3 | 2/3 | As recorded |
| 3 | Why crossing breaks balance (B64) | 2/3 | 2/3 | The first failing contact's returns → a lemma |
| 4 | Shaped growth that stops (B65) | 2/3 | 2/3 | Double one territory, stop, compare with the fixed shape |

**Corrections:** none. **Goals:** G1/G5 checkpoint; B56 taken; B64 and B65 added to the backlog. **Assumptions:** none. **Long-running:** CROSS-BORDER-A1 marked signed off.

As the coordinator asked, I'm starting B39 now.
