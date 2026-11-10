# Growth that rounds the reading

Epic `ROUND-READ-20261110-001` (program foundations), 2026-11-10. A frozen exploratory census (ticket A, pre-registered in `fb40c5d09`).

## The question

- **Where it comes from.** Backlog B108. In `READ-GROW-20261110-001` one schedule heard a diagonal original ring before a straight one
  at the same taxicab distance, as a round distance would. The coordinator gave B108 the go-ahead on 2026-11-10, asking also what the
  law contributes beyond the drawn board, since `CONF-METRIC-20261110-001A`'s theorem is coarse and partly follows from the construction.
- **The question.** Does a growing plane read a distance rounder than its board's taxicab one?

## What was frozen

- **Four readings** from ring (0, 0), in conformal time: by routes (T ring to ring, T1 cell to cell) and plain hearing (L, L1).
- **The gap** at even taxicab distance d: the diagonal ring (±d/2, ±d/2) against the axis ring (±d, 0), (0, ±d), least lags over the four
  copies; its slope over d. Taxicab: bounded; Euclidean: about −1.17g per unit. Rounder: slope ≤ −g/2; squarer: ≥ g/2.
- **Q1** (the theorem's bound on route gaps), **Q2** (no route rounding) and **Q3** (no growth schedule rounds the plain reading).

## Conclusions

| # | Conclusion | Kind | Ticket |
| --- | --- | --- | --- |
| 1 | **No rounding.** In 113 schedules on the 13 × 13, 21 × 21 and 41 × 41 tubes (distances to 20, g = 2, 3, 5), no reading is rounder than taxicab: Q1, Q2 and Q3 hold. | exploratory, exact | A |
| 2 | **Route readings are taxicab at every distance read.** Diagonal and axis rings at the same taxicab distance are reached within 9 conformal lags of each other and the gap does not grow (at 41 × 41 it is −3 at every even distance from 2 to 20), as the theorem requires asymptotically. | exploratory, exact; bounded by the theorem | A |
| 3 | **The plain reading waits for powers of two along diagonals.** On the fixed first stage the diagonal ring at taxicab d is heard plainly 4g (2^⌈log₂ d⌉ − d) conformal lags after the axis ring: on time at d = 2, 4, 8, 16, and otherwise when the axis ring at the next power of two would be (24 of 24 baseline gaps, g = 2, 3, 5). | exploratory, exact | A |
| 4 | **Growth keeps the plain reading square.** 313 of 456 plain gaps in growth schedules follow the same law, and every growth schedule's plain slope lies between 1.5g and 2.4g, on the square side. | exploratory, exact | A |
| 5 | **The diagonal lead read before was an offset.** `READ-GROW-20261110-001`'s diagonal ring heard before a straight one at the same distance is a bounded route offset (at most 9 conformal lags here), not a trend. | exploratory, exact | A |

## Answer

No. A plane grown by the doubling law reads no distance rounder than its drawn board's. Its route readings are taxicab, by theorem and
at every distance read; its plain hearing is further from round than taxicab, because along diagonals it waits for the next power of
two, and growth perturbs that pattern without rounding it.

## What the law contributes beyond the drawn board

The coordinator asked; the answer, from the theorem and this census:
- **The coarse shape is the board's.** Route readings are, up to a constant, 4g times the board's taxicab distance (`CONF-METRIC-20261110-001A`).
  Nothing in the law rounds or distorts that shape at large scale.
- **The law sets the scale and the clock.** Its ring size and contact positions fix the speed (2g lags per ring step), and its doubling
  sets the expansion that conformal time removes.
- **The law adds bounded offsets.** Rule 60 reads leftward, so which way a ring is left shifts readings by up to 4g in the first stage
  and by the doublings' bounded jumps afterwards.
- **The law adds a 2-adic plain reading.** Plain hearing counts routes by parity, and rule 60's parity pattern (Pascal's triangle mod 2)
  makes diagonal hearing wait for powers of two. This is the one shape the law contributes on its own, and it is the opposite of round.
- **So, for question 9:** a rounder reading would have to come from the board, or from a board made of distinctions (sub-goal B92), not
  from this law's growth.

## Reading

**Interpretation, not a theorem.**
- **Parity reads binary, not Euclid.** The plain reading's distance along a diagonal is the next power of two: a distance in the base
  of the law's own arithmetic. That fits the program's earlier finding that a linear rule keeps one knot per lag at every power of two
  (`TIME-KNOTS-20261107-001`).

## Lag cutoffs and census-only claims

- **Census-only.** Conclusions 2 to 5 at the distances read; the power-of-two law is computed, not proved.

## Stress test

| Claim | Check | Result |
| --- | --- | --- |
| No rounding (1) | 41 × 41, distances to 20, beyond the 5 × 5 and 7 × 7 tubes of the earlier epics | pass |
| The two codes | round_lib against metric_lib on seven small schedules | pass |

## Literature and provenance

- **Sources.** Additive cellular automata and Pascal's triangle mod 2 (Martin, Odlyzko and Wolfram 1984; Lucas's theorem); the plain
  first need filtered by the parity of shortest routes (`DISTANCE-20261108-001`, A41).
- **Classification.** Known-with-delta: the parity structure is classical; the delta is its reading as the growing plane's plain shape.

## Workspace assumptions

- **Relied on.** A41, A44, A45, A51, A56. **Added.** None.

## Ratio

- **Substantive.** One frozen census (A), with a third route-and-hearing code. **Administrative.** The pre-registration, this note
  and the closure.

## Pending the owner

- Nothing new.

## Next steps

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — growth that rounds the reading | **Status:** Successful | Read exactly: no rounding; route readings taxicab, plain readings 2-adic along diagonals |
| Local direction — a grown plane that reads its own metric | Research directions | The coarse metric is proved and its shape is the board's; what remains in this line is sharpening |
| Broader exploration — G1 with G5 | Known alternatives | The board as distinctions (B92, in another line); boards of other shapes; why a run keeps balance |
| Long-term goal — G1 Space from a law (question 9) | Obstruction learned | Growth by this law adds scale, clock, offsets and a binary plain reading to the drawn board, never roundness |

**Corrections:** none. **Goals:** a G1 and G5 checkpoint (obstruction learned); B108 taken. **Assumptions:** none.

**Next step:** Research directions — selected: #1, awaiting the coordinator's go-ahead.

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | The plain reading's power-of-two law as a theorem | 2/3 — Substantial | 3/3 — Ready | Count fastest routes to a diagonal target with Lemma 1's hop lattice and read their parity with Lucas's theorem → a proof that plain hearing waits for 2^⌈log₂ d⌉ along diagonals on the fixed torus, or the distance where it fails | Selected · awaiting go-ahead |
| 2 | Sharp constants (B127) | 2/3 — Substantial | 3/3 — Ready | As recorded | Alternative · deferred |
| 3 | A metric with knots kept (B128) | 2/3 — Substantial | 2/3 — Testable | As recorded | Alternative · deferred |
| 4 | Readings on other boards | 2/3 — Substantial | 2/3 — Testable | Run the census on the program's triangular and honeycomb ring lattices (`LATTICE-REACH-20261109-001`) → whether a board, not growth, makes the route reading rounder than taxicab | Alternative · deferred |

1. **The power-of-two law.** Payoff 2: proves the one shape this law adds of its own, and answers A41's challenge for diagonals.
   Concreteness 3: Lemma 1 gives the route counts and Lucas's theorem their parity.
2. **Sharp constants.** As recorded.
3. **A metric with knots kept.** As recorded.
4. **Other boards.** Payoff 2: roundness, if any, from the board. Concreteness 2: the lattices exist in the record; the doubling law on
   them has to be written.

**Recommendation.** Research directions, #1; stop at a proof or the distance where the law fails.

**Basket:** B127, `EXPAND-READ-20261110-001#2`, B55; none taken: #1 stays in this line because it proves what this census found.
