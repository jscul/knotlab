# A ring inserted while running

Epic `RING-RUN-20261109-001` (program foundations), 2026-11-09.

## The question

- **Where it comes from.** `GROW-PLAIN-20261109-001B` found a law that grows a network reading its own distance plainly at every stage:
  insert one ring into the twist tube, rejoining the three contacts across the gap through it. Its stages were read as fixed networks
  (A42). `GROW-RUN-20261109-001` found that a band inserted while the network runs keeps only the bindings it has not reached. Backlog B37
  asked the same of a ring; the coordinator selected it on 2026-11-09.
- **The question.** If the ring is inserted while the twist tube runs, which bindings survive, and is the damage confined to the
  insertion's light cone?

## Conclusions

| # | Conclusion | Kind | Ticket |
| --- | --- | --- | --- |
| 1 | **The damage is causal, as for bands.** No ring the insertion has not reached, and not the new ring, ever loses a binding, on 19 tubes, every split and every lag read; an insertion at lag 0 gives the next stage and keeps every contact persistent. | exploratory census, exact, frozen hypotheses held | A |
| 2 | **About half of what it reaches breaks.** 53% of the bindings of reached rings fail when the rewired contacts keep their values, 51% when they are born anew, against 68% for a band. | exploratory census, exact | A |
| 3 | **Clean lags are rare.** Lag 0 only with kept values, lags 0 and 1 (and 2 on odd tubes at g = 2) with fresh ones, except the tubes of 5 and 7 rings at g = 4, where many lags are clean. | exploratory census, exact | A |

## Answer

The single-ring law also has to grow between runs. A ring inserted while the twist tube runs leaves intact everything its influence has
not reached and binds its own cells at every lag, as `GROW-RUN-20261109-001A`'s theorems predict for any insertion that rewires cells
round a gap, but about half the bindings it has reached fail: a little gentler than a band, and no rescue.

## Reading

**Interpretation, not a theorem.**
- **Growth between runs.** The twist tube grows one ring at a time and reads its distance plainly at every stage only when each stage is
  read as a fixed network (A42), as for the band law. A law that grows while it runs keeps its knots young.
- **Gentler, not safe.** A ring cuts three contacts where a band cuts a whole row, and fewer reached bindings fail; the fresh split adds
  a lag or two of grace before influence crosses the gap.

## Lag cutoffs and census-only claims

- **Lag cap.** Every insertion lag of 17 tubes; the first 64 of the 7-ring tubes at g = 3 and 4, whose run states have periods 2,044 and
  10,920 (the contract's amendment before its first run).
- **Census-only.** Every conclusion.

## Stress test

The census is the epic's evidence and covers every lag of 17 tubes; no separate stress test was run, since conclusion 1 is what
`GROW-RUN-20261109-001A`'s Theorems 1 and 2 predict for any rewiring round a gap and conclusions 2 and 3 are descriptive.

## Literature and provenance

- **Sources.** `GROW-RUN-20261109-001A` (the reached and not-reached reading, growrun_lib); linear cellular automata on changing graphs.
- **Classification.** Known-with-delta: the band result carried to single-ring insertion.

## Workspace assumptions

- **Relied on.** A30, A32, A42, A44 (cells born at an insertion are new open distinctions).
- **Added.** None.
- **Scope.** Twist tubes of 4 to 12 rings at g = 2 and 4 to 8 at g = 3 and 4, one insertion per run.

## Ratio

Since the epic opened:
- **Substantive.** One exploratory census (A), pre-registered.
- **Administrative.** The pre-registration and its amendment, this note and the closure.

## Pending the owner

- None new.
- Carried: whether to qualify `PHASE-HALO-20261103-001-D001` and `FACE-CLAIM-20261103-001-D003`; the SELECTION-NOTE erratum;
  superseding `KNOT-COMPOSE-20261101-001-D001`.

## Next steps

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — a ring inserted while running | **Status:** Successful | The answer is clear: causal damage, about half of reached bindings, no rescue |
| Local direction — growth in time | Research directions | Growth while running breaks reached knots for rings as for bands; growth chosen by the dynamics is the growth thread's |
| Broader exploration — G1 with G5 | Known alternatives | A plane read plainly beyond tori (B36, next in this thread) |
| Long-term goal — G1 Space from a law (question 9) | Obstruction learned | A law that grows while it runs keeps only its young knots, ring by ring as band by band |

**Corrections:** none. **Goals:** a G1 and G5 checkpoint (obstruction learned); B37 taken. **Assumptions:** none added or changed.

- **What the attempt leaves open.** Why the 5- and 7-ring tubes at g = 4 have many clean lags.
- **The missing bridge to the program's composed topology.** As before.

**Next step:** Research directions — selected: a plane read plainly beyond tori (B36), by the coordinator on 2026-11-09, in this thread.

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | A plane read plainly beyond tori (B36, G1 with G5) | 3/3 — Major | 1/3 — Stated | As in the backlog | Selected · this thread |
| 2 | The clean lags at g = 4 (G5) | 1/3 — Minor | 3/3 — Ready | Read the run state of the 5-ring tube at g = 4 at its clean lags → why the reached bindings survive there, or an accident of the state | Alternative · deferred |

1. **The plane.** As B36.
2. **Clean lags.** Payoff 1: a curiosity of two tubes; Concreteness 3: the state is in hand.

**Recommendation.** Research directions, selected #1 at the coordinator's instruction; #2 is not parked (a curiosity).
