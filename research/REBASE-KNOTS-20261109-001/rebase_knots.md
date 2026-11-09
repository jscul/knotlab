# Knots read from the last growth event

Epic `REBASE-KNOTS-20261109-001` (program foundations), 2026-11-09.

## The question

- **Where it comes from.** `GROW-RUN-20261109-001` found that a band inserted while the network runs breaks most knots across time of
  the rings it has reached, reading the whole history from its first row. Its direction 2 asked whether that is an artefact of where the
  reading starts; the coordinator gave it the go-ahead on 2026-11-09 as a cheap test.
- **The question.** Read binding from the last growth event, the row at the insertion lag, instead of the first row. Is that reading
  native, and do contacts persist under it?

## Conclusions

| # | Conclusion | Kind | Ticket |
| --- | --- | --- | --- |
| 1 | **No row after the first is open.** Every cell is read by exactly two cells (itself and the next cell, or the next cell on each of a contact's two rings), so from lag 1 on the cells' values sum to 0: each cell is the sum of all the others. The tubes' rows lose 8 to 32 dimensions within 8 lags. | proved; checked on 48 networks | A |
| 2 | **Read as if open, every stage persists.** Treating the insertion row as a first row, every contact binds both of its rings at every later lag, whatever the split: the stage reading. | proved; 160 cases | A |
| 3 | **Read natively, it fails even without growth.** From the first row every contact binds; from any later row t0 = 1 to 7 of four tubes that never grow, every contact fails to bind each of its rings at some lag, because its value can then be computed from the row's other cells. | computed, exact | A |

## Answer

No. Reading from the last growth event restores persistence only by treating as open a row that is not: rule 60 and law (12, 12) read
every cell twice, so every later row has a parity fixed at 0. Read natively, knots across time from a later row fail at some lag in a
network that never grows. So the breakage found by `GROW-RUN-20261109-001` is not a reading artefact: the first row, and the cells a
growth event bears, are the only open distinctions knots across time can be read from.

## Reading

**Interpretation, not a theorem.**
- **Only beginnings are open.** In these networks the first row and the cells a band brings are the only open distinctions; every later
  row is a function of them with fewer degrees of freedom. A knot across time therefore always reaches back to a beginning, which is
  the program's "a beginning is a knot" (`GROWTH-LAW-20261107-001`) seen from the other side.
- **The stage reading, restated.** A42's stage reading works because each stage starts from an open first row: growth between runs is a
  new beginning. Growth while running is not, and its knots lapse inside the insertion's reach.

## Lag cutoffs and census-only claims

- **No lag cutoff.** Readings follow each contact's row under the fixed network through its whole period.
- **Census-only.** Conclusion 3, on four tubes and rows 1 to 7.

## Stress test

| Claim | One size past | Result |
| --- | --- | --- |
| The native failure from later rows (3) | the 5 × 4 tube at g = 2 and the 3 × 4 tube at g = 3, rows 1 to 9 (read on four tubes, rows 1 to 7) | pass: binding from row 0 holds; from every later row every contact fails at some lag |

The script is `stress_test.py` beside this note, its output `stress_test.json` and its log `stress_test_log.txt`.

## Literature and provenance

- **Sources.** Additive cellular automata over GF(2), whose rule 60 is x ↦ (1 + s)x and maps onto the even-weight subspace of a ring;
  Garden-of-Eden configurations (Martin, Odlyzko and Wolfram 1984).
- **Classification.** Known-with-delta. The delta is that the parity count rules out reading the program's knots across time from any
  row but the first, so growth while running cannot be rescued by moving the start of the reading.

## Workspace assumptions

- **Relied on.** A30 (two-time knots), A32 (binding), A44 (a band's cells are open).
- **Added.** None. A42's confirmation gains a reason: the stage reading starts each stage from an open row.

## Ratio

Since the epic opened:
- **Substantive.** One proof (A) with four checks.
- **Administrative.** This note and the closure.

## Pending the owner

- Nothing new.

## Next steps

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — knots from the last growth event | **Status:** Successful | Not native: no later row is open (proved), and the native reading fails without growth (computed) |
| Local direction — growth in time | Research directions | Growth while running stays broken; growth chosen by the dynamics is the live alternative |
| Broader exploration — G1 with G5 | Known alternatives | Growth chosen by the dynamics (B23, running); which reached bindings survive (backlog); handles from two bands (B22) |
| Long-term goal — G5 Dynamics (question 4) | Obstruction learned | Knots across time reach back to a beginning; a later row is never open |

**Corrections:** none. **Goals:** a G5 and G1 checkpoint (obstruction learned). **Assumptions:** none added; A42's history gains this
reason.

**Next step:** Research directions — the coordinator's order puts growth chosen by the dynamics (B23) first; its census is running.

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Growth chosen by the dynamics (B23) | 3/3 — Major | 2/3 — Testable | Its frozen census (`GROW-CHOOSE-20261109-001`) → where and which way the dynamics grows | In progress |
| 2 | Which reached bindings survive (backlog) | 1/3 — Minor | 2/3 — Testable | Split the surviving bindings by the returns they carry across the cut → a criterion | Backlog |
| 3 | Invertible substrates | 2/3 — Substantial | 2/3 — Testable | A rule and contact law under which every row is open (an invertible linear map), where reading from the last growth event would be native → whether growth while running then keeps persistence | Alternative · deferred |

1. **Dynamics-chosen growth.** As in `GROW-RUN-20261109-001`.
2. **Surviving bindings.** As there.
3. **Invertible substrates.** Payoff 2: it would tell whether the lapse is rule 60's forgetting or growth itself. Concreteness 2: rule 150
   or a self-reading contact law gives other parity counts to test. Uncertainty: whether an invertible substrate keeps contacts
   persistent at all.

**Recommendation.** Research directions; continue with B23 as ordered, and offer #3 as the sharpest test of this result.
