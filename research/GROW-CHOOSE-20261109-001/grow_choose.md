# Growth chosen by the dynamics

Epic `GROW-CHOOSE-20261109-001` (program foundations), 2026-11-09.

## The question

- **Where it comes from.** Backlog B23. `GROW-RUN-20261109-001` found that a band inserted while the network runs keeps what it has not
  reached and breaks most of what it has, and sharpened B23: let the network grow only where an insertion keeps every contact
  persistent. The coordinator gave it the go-ahead on 2026-11-09 as the fallback when growth while running broke.
- **The question.** On a running square tube, insert a band, along the loop or across it, only where the insertion keeps every contact
  persistent. Where and which way does the network grow, and does it keep growing? This also challenges A43, which fixed the way bands go
  by default.

## Conclusions

| # | Conclusion | Kind | Ticket |
| --- | --- | --- | --- |
| 1 | **The dynamics picks a direction and keeps it.** A band is allowed both ways at lags 0 and 1; from lag 3 on, in all 48 runs, every allowed cut runs across the direction already grown, so the network lengthens one way: a tube. Which way is set by the first band; two listing orders give mirror-image runs (3 × 16 and 16 × 3). | exploratory census, exact per decision | A |
| 2 | **Growth stops.** If the cut contact keeps or copies its value (lower, upper, copy), nothing can be added after lag 2. If both halves are born (fresh), one band per lag can be added for 3 to 13 lags, and then no cut keeps every contact persistent: on 3 × 4 at lag 6 or 9, on 4 × 4 at lag 8, on 3 × 3 at g = 3 at lag 3. Only the 3 × 3 tube at g = 2 grows at every lag to the horizon, 13 bands, and in the stress test the 3 × 5 and 5 × 3 tubes when grown along their length with three rings round. | exploratory census, exact per decision | A, stress test |
| 3 | **Filling every allowed cut at once grows both ways, at first.** The rule that needs no order, every allowed cut together, doubles both sides at lags 0 and 1 (3 × 3 to 12 × 12 with fresh), and every combination persists (19 of 19); its later course is not read, since the network passes the run's limit of 120 rings at lag 2. | exploratory census, exact | A |

## Answer

Growth chosen by the dynamics makes a tube and then stops. Once one band is in, the only places where the network allows another are
across the tube, so the dimension it grows is one, as A43 assumed; and within a few lags, in most tubes, no place is left at all. Only
filling every allowed place at once, in the first two lags, grows both ways.

## Reading

**Interpretation, not a theorem.**
- **A band across the tube would cut old influence.** A band along the growth direction can sit between the youngest bands, where little
  influence has arrived; a band the other way runs through every row, including the old ones whose influence has crossed the cut, and
  `GROW-RUN-20261109-001` showed that such insertions break most knots. That would explain conclusion 1; it is not proved here.
- **The direction is chosen by symmetry breaking.** The dynamics does not prefer a way; it keeps the way the first band went. Under the
  doctrine no scheduler may choose, so the native rule is to fill every allowed cut, and that rule grows both ways while it can.
- **For G1.** The band law, run by its own dynamics, grows a line of loops for a few lags. A plane would need both directions at every
  lag; the only rule that tries is the order-free one, and whether it can continue past lag 1 is the open question.

## Lag cutoffs and census-only claims

- **Exact per decision.** Every "allowed" or "not allowed" is read through a full period of the state; 19 cuts in 6 of the 48 runs were
  unknown (the state not repeating within 20,000 steps), each at a lag where no other cut was allowed.
- **Census-only.** All three conclusions: four tubes, lags 0 to 12.

## Stress test

| Claim | One size past | Result |
| --- | --- | --- |
| One way after lag 2 (1); no growth after lag 2 for lower, upper, copy (2) | the 3 × 5 and 5 × 3 tubes at g = 2 and the 3 × 4 tube at g = 3, four splits, both first-cut rules, lags 0 to 12 | pass: no allowed cut both ways from lag 3 on, no growth after lag 2 for the three splits |
| Where fresh growth stops (2) | the same tubes | girth-3 tubes grow at every lag to the horizon (3 × 5 to 3 × 18, 5 × 3 to 18 × 3); grown the other way they stop at lag 7 (10 × 5, 5 × 10); 3 × 4 at g = 3 stops at lag 3 or 5 |

The order-free rule is not stress-tested: past lag 1 it needs networks above 120 rings. The script is `stress_test.py` beside this note,
its output `stress_test.json` and its log `stress_test_log.txt` (4 seconds).

## Literature and provenance

- **Sources.** Self-organised growth with local rules and symmetry breaking in growth direction; additive cellular automata on growing
  graphs; `GROW-RUN-20261109-001` for the causal reading.
- **Classification.** New as far as found, a census.

## Workspace assumptions

- **Relied on.** A30 (two-time knots), A32 (binding), A42 (confirmed), A44 (born cells open).
- **Challenged.** A43, bands are added along the seed loop: confirmed for stated reasons; the dynamics grows one way too, the way the
  first band goes.

## Ratio

Since the epic opened:
- **Substantive.** One frozen exploratory census (A), 48 runs.
- **Administrative.** This note and the closure; two launches stopped before any result (memory, then time), recorded in the contract.

## Pending the owner

- Nothing new.

## Next steps

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — growth chosen by the dynamics | **Status:** Successful | Exact per decision: the dynamics grows one way, as a tube, and stops within a few lags in most tubes |
| Local direction — growth from a law that grows in time | Research directions | Only the order-free rule grows both ways, and only its first two lags are read |
| Broader exploration — G1 with G5 | Known alternatives | An invertible substrate (`REBASE-KNOTS-20261109-001`'s direction 3); handles from two bands (B22) |
| Long-term goal — G1 Space from a law (question 9) | Obstruction learned | Neither the band law nor its own dynamics grows a plane of persistent contacts on these tubes |

**Corrections:** none. **Goals:** a G1 and G5 checkpoint (obstruction learned), B23 marked taken. **Assumptions:** A43 confirmed for
stated reasons.

- **What the attempt leaves open.** Whether the order-free rule keeps growing both ways past lag 1; why the 3 × 3 tube at g = 2 keeps
  growing; a proof of conclusion 1.
- **The missing bridge to the program's composed topology.** A growth law, chosen by nothing outside the network, that grows a plane of
  persistent contacts.

**Next step:** Research directions.

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | The order-free rule past lag 1 | 3/3 — Major | 2/3 — Testable | Run "fill every allowed cut" from 3 × 3 and 4 × 4 past lag 1 with a faster persistence reading (the eventual period by the minimal polynomial, not by iteration) → a plane that keeps growing, or the lag it stops | Alternative · deferred |
| 2 | An invertible substrate (`REBASE-KNOTS-20261109-001`, #3) | 2/3 — Substantial | 2/3 — Testable | A rule and contact law whose one-step map is invertible, so every row is open → whether growth while running then keeps persistence | Alternative · deferred |
| 3 | Why a band across the tube breaks persistence | 1/3 — Minor | 2/3 — Testable | Read the reached rings of each refused cut (`GROW-RUN-20261109-001A`, Theorem 1) → the cause of conclusion 1, or another | Alternative · deferred |
| 4 | Handles from two bands at once (B22) | 2/3 — Substantial | 1/3 — Stated | Glue a band pair across the n × m torus as a handle → a balanced genus-2 network, or none | Alternative · deferred |

1. **Order-free past lag 1.** Payoff 3: the only native candidate for a plane grown by its own dynamics. Concreteness 2: needs a faster
   exact reading of persistence on networks of hundreds of rings. Main uncertainty: whether any cut stays allowed at lag 2.
2. **Invertible substrate.** Payoff 2: separates rule 60's forgetting from growth itself. Concreteness 2.
3. **Why across breaks.** Payoff 1: explains conclusion 1. Concreteness 2.
4. **Two bands.** As before.

**Recommendation.** Research directions, #1 first: it is the only open route to a plane grown by its own dynamics; stop it at the first
lag where no cut is allowed, or at a plane that keeps growing to a stated size.
