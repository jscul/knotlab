# The conformal metric as a theorem

Epic `CONF-METRIC-20261110-001` (program foundations), 2026-11-10. A proof (ticket A), its statement and stop rule frozen in `603df0d23`
before it was written.

## The question

- **Where it comes from.** Sub-goal B125, recorded by `EXPAND-READ-20261110-001`: counting a lag after k doublings as 2^−k (conformal
  time, A56), a growing plane's round-trip time lengths broke the triangle inequality in 28 of 891 schedules, by at most 2, against 240
  and up to 78 in plain lags. The coordinator gave B125 the go-ahead on 2026-11-10 at maximum effort, asking first for the residual's
  trace, a check of prior work, and whether the 4g 2^k law is a consequence of the construction.
- **The question.** Is the conformal round trip a metric up to a constant at every size and for every schedule?

## Conclusions

| # | Conclusion | Kind | Ticket |
| --- | --- | --- | --- |
| 1 | **One stage, exactly.** In a fixed stage the earliest arrival from an own cell to another is the steps to the next contact, g times the hop distance of the contact lattice, and the steps from the last contact. The contacts sit at the rings' side midpoints, each hop moves a quarter-turn round a ring, and two hops make exactly one ring step along an axis: from cell 1 to cell 1 at ring displacement (a, b), 2g + 2g min(\|a + 1\| + \|b\|, \|a\| + \|b − 1\|). | proved; checked against breadth-first search (326,400 pairs) | A |
| 2 | **Conformal time reads taxicab distance, for every schedule.** Whenever T1(v) is defined, 4g d(v) − 6g ≤ φ(T1(v)) < 4g d(v) + 9g + 2, and it is defined once the schedule's conformal length reaches the upper bound. | proved; checked on 15,373 route arrivals (891 census and 240 fresh schedules, n = 5, 7, 9, g = 2 to 5) | A |
| 3 | **A metric up to a constant.** The conformal round trip lies within [8g d − 12g, 8g d + 18g + 4], so it satisfies the triangle inequality up to 42g + 4: at every size and for every schedule it is, up to a constant, 8g times the lattice's taxicab distance. | proved | A |
| 4 | **Plain lags have no such bound.** On [28, 2 repeated K times, 40·2^(K+1)] the plain excess R1(2u) − 2 R1(u) is 42, 114, 260, 548 for K = 0 to 3, roughly doubling, while the conformal excess stays at most 1. | computed | A |
| 5 | **The 4g 2^k law is a consequence of the construction.** Lemma 1's two hops (2g lags) per ring step, and 2^(k+1) ring steps per original spacing in stage k, give it in a line; the census's 2,368 exact ring-to-ring increments are that consequence read, not an independent law. | proved (the speed); the census increments computed | A |
| 6 | **Where the residual comes from.** Of the 80 violating triples in `EXPAND-READ-20261110-001`'s 28 schedules, 50 (at g = 3 and 5) have their two shorter round trips finished in the first stage and the longer one after a doubling, and 30 (at g = 2) have all three arriving in the second stage by routes that crossed the doubling at different points: in both, the doubling's jumps that the proof bounds (a ring shrinking toward its corner, a wait), worth a few conformal lags. | traced, computed | A |

## Answer

Yes. A plane of rule-60 rings grown by the doubling law, under any schedule and at every size, reads in conformal time its original
rings' taxicab distance up to a bounded error: the conformal time length is 4g d(v) up to −6g and +9g + 2, and the conformal round trip
is a metric up to 42g + 4, 8g times taxicab distance up to a constant. The proof is elementary: a fixed stage's earliest arrivals are a
taxicab distance on the lattice of contacts (two quarter-turn hops per ring step), conformal time makes that speed the same in every
stage, and what the doublings add (a ring shrinking toward its corner, one possible wait) shrinks with the stage and sums to a constant.
In plain lags the excess grows without bound. The constants are loose: the readings stay within 6 below and 4g above, with an excess
of at most 3.

## Reading

**Interpretation, not a theorem.**
- **A grown space that reads its own distance at its own scale.** For question 9 this is the first proved statement in the line that a
  uniform local law, growing, reads a distance between its original rings, in its own clock and up to a constant, at every size and for
  every schedule. It is coarse: a metric up to a constant, not an exact one. The board is still drawn (A51), and the distance read is the
  drawn board's taxicab distance.
- **Expansion and horizon together.** In lags the plane expands (`METRIC-GROW-20261110-001`); in conformal time it does not, up to a
  constant; and the schedule's total conformal length can be finite, which is the horizon `GROW-HORIZON-20261109-001` found in lags.
  The resemblance to comoving distance and conformal time in an expanding space is a resemblance of counting, not a physics claim.
- **Knots.** The theorem does not involve balance; it holds for the schedules that keep every stage balanced as for the others.

## Lag cutoffs and census-only claims

- **The theorem has no cutoff.** Conclusion 4 and the residual's trace are computed.

## Stress test

| Claim | Check | Result |
| --- | --- | --- |
| Lemma 1 (1) | breadth-first search on 16 stages | pass, 326,400 pairs |
| Theorem 2 (2) | fresh random schedules on 7 × 7 and 9 × 9 tubes, beyond the census's sizes, with short runs favoured | pass, 1,759 arrivals |

## Literature and provenance

- **Sources.** Earliest-arrival (foremost) distances in temporal graphs are known not to satisfy the triangle inequality in general
  (Michail, "An introduction to temporal graphs", 2015; the temporal path metrics of arXiv 2510.01702); shape theorems of first-passage
  percolation on fixed lattices (Richardson; Cox and Durrett; Kesten), where a rescaled ball converges to a limit shape; expansion and
  causal graphs in the Wolfram model (Gorard 2020), discussed qualitatively; comoving distance and conformal time in cosmology (the
  analogy only). No result on rescaling time to recover a metric on a refining lattice was found.
- **Classification.** Known-with-delta. The ingredients are elementary (a hop lattice and a geometric series); the delta is the exact
  one-stage formula for this network and the bounded conformal error for every doubling schedule.

## Workspace assumptions

- **Relied on.** A38, A40, A41, A44, A45, A51, A56 (conformal time). **Added.** None; A56's history records the theorem.

## Correction

**2026-11-10 · Not a block, missed prior work** (`docs/CORRECTIONS.md`). `METRIC-GROW-20261110-001` classified its finding that a growing
plane's time lengths are not a metric as new as far as found. That earliest-arrival distances in time-varying graphs need not satisfy the
triangle inequality is known; what the epic added is where the violations fall here (only across doublings) and, with
`EXPAND-READ-20261110-001` and this epic, their removal in conformal time.

## Ratio

- **Substantive.** One proof (A) with five checks, and the residual's trace. **Administrative.** The pre-registration, this note and
  the closure.

## Pending the owner

- Nothing new.

## Next steps

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — the conformal metric as a theorem | **Status:** Successful | Proved for every schedule and size, with explicit constants, and checked |
| Local direction — a grown plane that reads its own metric | Research directions | The coarse metric is proved; what is open is sharp constants, an exact metric, and doing it with knots kept and nothing drawn |
| Broader exploration — G1 with G5 | Known alternatives | Growth that rounds the reading (B108); why a run keeps balance; the board as distinctions (B92, in another line) |
| Long-term goal — G1 Space from a law (question 9) | Capability gained | A uniform local law grows a plane that, at its own scale, reads its original rings' distance up to a constant, proved at every size |

**Corrections:** one, Not a block (missed prior work): `METRIC-GROW-20261110-001`'s "not a metric" is an instance of a known fact about
temporal graphs. **Goals:** a G1 and G5 checkpoint (capability gained); B125 taken. **Assumptions:** A56's history records the theorem.

**Next step:** Research directions — selected: #1, awaiting the coordinator's go-ahead.

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Sharp constants | 2/3 — Substantial | 3/3 — Ready | Find the exact range of φ(T1) − 4g d(v) over all schedules, the observed −6 to 4g, by tightening the jump bound (the shrink of a ring toward its corner is one-sided) → the sharp constants, or a schedule beyond them | Selected · awaiting go-ahead |
| 2 | Growth that rounds the reading (B108) | 2/3 — Substantial | 3/3 — Ready | As recorded | Alternative · deferred |
| 3 | A metric with knots kept | 2/3 — Substantial | 2/3 — Testable | The schedules known to keep every stage balanced read the coarse metric by the theorem; ask which of them hear every original ring while balanced on larger tubes (the deaf distance) | Alternative · deferred |
| 4 | Why a run keeps balance (was `READ-GROW-20261110-001#3`) | 2/3 — Substantial | 2/3 — Testable | As recorded | Alternative · deferred |

1. **Sharp constants.** Payoff 2: turns a coarse statement into a precise one (the excess at most 3). Concreteness 3: the proof's steps
   are explicit and the data shows where they are loose.
2. **B108.** As recorded.
3. **A metric with knots kept.** Payoff 2: joins the theorem to balance. Concreteness 2: the deaf distance limits what balanced schedules
   reach.
4. **Why a run keeps balance.** As recorded.

**Recommendation.** Research directions, #1; stop at the sharp constants or a schedule beyond them.

**Basket:** B108, B55, `GROW-HORIZON-20261109-001#2`; none taken: #1 stays in this line because it sharpens the theorem just proved.

## Final report as sent

Sent to the owner on 2026-11-10 at 17:18 UTC and copied here verbatim.

**The conformal metric as a theorem (B125) is proved and published. At its own scale the growing plane reads its original rings' taxicab distance up to a constant, at every size and for every schedule.** ([decision note](https://github.com/jscul/knotlab/blob/main/research/CONF-METRIC-20261110-001/conf_metric.md))

- **One stage, exactly:** a route's earliest arrival is a taxicab distance on the lattice of contacts. Each hop goes a quarter-turn round a ring in g lags, and two hops make one ring step. Checked against breadth-first search on 326,400 pairs.
- **The theorem:** in conformal time the first arrival between original rings is 4g × taxicab distance, to within −6g and +9g + 2. So the round trip is a metric up to 42g + 4. Checked on 15,373 arrivals. In plain lags the excess roughly doubles with each doubling a trip crosses (42, 114, 260, 548).
- **Your question on the 4g·2^k law:** it's a consequence of the construction, provable in a line from two hops per ring step. The census's 2,368 exact matches confirm that consequence rather than an independent law.
- **The residual traced:** it comes from the doubling jumps the proof bounds (a ring shrinking toward its corner, one possible wait).
- **Honest limits:** it's a coarse metric (the readings stay within 6 below and 4g above, so the constants are loose), and the board is still drawn (A51).

| Scope | Verdict | Why |
|---|---|---|
| This attempt: the conformal metric as a theorem | Successful | Proved for every schedule and size, constants explicit, checked |
| Local direction: a grown plane that reads its own metric | Research directions | Coarse metric proved; sharp constants and knots-kept versions open |
| Broader exploration: G1 with G5 | Known alternatives | Growth that rounds the reading (B108); why a run keeps balance |
| Long-term goal: G1 Space from a law | Capability gained | A local law grows a plane that, in its own clock, reads its distance up to a constant, proved at every size |

| # | Direction | Payoff | Concreteness | First step → stop |
|---|---|---|---|---|
| 1 | Sharp constants | 2/3 | 3/3 | Tighten the one-sided jump bound → the exact range, or a schedule beyond it |
| 2 | Growth that rounds the reading (B108) | 2/3 | 3/3 | As recorded |
| 3 | A metric with knots kept | 2/3 | 2/3 | Which balanced schedules hear every ring on larger tubes |
| 4 | Why a run keeps balance | 2/3 | 2/3 | As recorded |

**Corrections:** one, Not a block (missed prior work). B102's "time lengths of a growing plane aren't a metric" is an instance of a known fact: earliest-arrival distances in time-varying graphs needn't satisfy the triangle inequality. What's new is where the violations fall and their removal in conformal time. Logged in CORRECTIONS.md and knotlab's HISTORY.md. **Goals:** G1/G5 checkpoint (capability gained); B125 taken. **Assumptions:** A56's history records the theorem.
**Basket:** B108, B55, GROW-HORIZON-20261109-001#2. None taken: #1 stays in this line because it sharpens the theorem just proved.

I recommend #1 and will wait for the go-ahead.
