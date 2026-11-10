# Readings on other boards

Epic `BOARD-READ-20261110-001` (program foundations), 2026-11-10. A proof (ticket A) and a frozen computation (ticket B), both
pre-registered in `f69403540`.

## The question

- **Where it comes from.** `ROUND-READ-20261110-001`'s direction 4. That census found the square board's route reading taxicab and no
  growth rounding it. The coordinator gave this direction the go-ahead on 2026-11-10 with the question to answer definitely: does any
  drawn board make the route reading rounder than its own graph distance, or does the reading always equal the board's graph metric up
  to a constant, and if the latter, state and, if short, prove it.
- **The question.** What shape does the route reading take on other boards, and is it the board's own?

## Conclusions

| # | Conclusion | Kind | Ticket |
| --- | --- | --- | --- |
| 1 | **On every periodic board the reading is a polygon norm up to a constant.** For every doubly periodic board of rings with shared contacts, at every g, the route reading is within a constant of the gauge of the polygon spanned by displacement over length of the simple cycles of its route digraph's finite quotient; likewise the board's graph distance. No periodic board's reading is round. | proved (a classical fact about periodic graphs, applied); checked on four boards | A |
| 2 | **On four boards it is the board's graph distance times g·d/2.** On the square, triangular, honeycomb and kagome boards (ring degree d = 4, 6, 3, 4) at g = 2 to 6, the route polygon is exactly the graph polygon scaled by 1/(g·d/2): the route reading is the board's own graph distance, scaled, up to a constant. Never rounder, never less round. | exploratory, exact, frozen; two methods (cycle polygons, breadth-first distances) | B |
| 3 | **Round trips cost the degree.** A ring path and its reverse cost together g·d per ring crossed, since leaving k slots on one way is leaving d − k slots on the other: on every d-regular board the round trip is at most g·d times graph distance plus a constant. | proved (one line) | A |

## Answer

The reading always has the board's shape, on every board read. In general, on every periodic board, the route reading is a polygon
norm up to a constant, so no drawn periodic board makes it round; on the four boards read, that polygon is exactly the board's own
graph-distance polygon, scaled by half the ring's degree times g, so the reading is the board's graph metric up to scale and a
constant, never rounder than it. That the shape is the board's on every periodic board is computed on four boards and proved for round
trips as an upper bound, not proved in general.

## The growth line's verdict

For the record of this line (`GROW-ALL-20261109-001` to here): a plane of rings grown by the doubling law, keeping its knots or not,
reads in its own clock the drawn board's graph distance, up to scale and a constant, at every size and for every schedule
(`CONF-METRIC-20261110-001A` with this epic); the law contributes the scale (g·d/2 lags per ring step), the clock, bounded offsets and a
binary plain reading, and no shape of its own. A rounder or chosen shape would have to come from the board, which every law here takes
as given (A51), so question 9's open part in this line is the board itself (sub-goal B92, in another line).

## Reading

**Interpretation, not a theorem.**
- **Half way round.** A route crosses a ring of degree d at a cost of d/2 hops on average over the turns a shortest path takes:
  right turns are cheap and left turns dear, and along any straight course they balance. That is why the scale is g·d/2 on every board
  read.
- **A51 stands, sharpened.** The board is declared, and these results show that what the dynamics reads off it is its graph distance,
  scaled; nothing in the law changes its shape.

## Lag cutoffs and census-only claims

- **The theorem has no cutoff.** Conclusion 2 is computed on four boards at g = 2 to 6, distances to 20.

## Stress test

| Claim | Check | Result |
| --- | --- | --- |
| The theorem (1) | breadth-first distances on four boards against the polygon's gauge, distances to 20 | pass: deviations bounded, no growth (ticket A's check; ticket B) |
| Homothety (2) | every g from 2 to 6 on every board | pass |

The first run of ticket B compared torus distances with the plane's gauge and read wrap-around as deviation; the analysis was amended to
take the least gauge over the torus's images, recorded in its interpretation with the first run's output kept.

## Literature and provenance

- **Sources.** Distances in periodic graphs and periodic metrics are polyhedral norms up to a bounded error (Burago, "Periodic
  metrics", 1992; the stable norm of periodic graphs); turn-cost (left/right) metrics on lattices. The scale g·d/2 for these boards is
  this epic's computation.
- **Classification.** Known: conclusion 1 is classical. Known-with-delta: conclusions 2 and 3 for the program's ring boards.

## Workspace assumptions

- **Relied on.** A41, A45, A51. **Added.** None. A history line on A51.

## Ratio

- **Substantive.** One proof (A) and one frozen computation (B) on four boards. **Administrative.** The pre-registration, this note
  and the closure.

## Pending the owner

- Nothing new.

## Next steps

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — readings on other boards | **Status:** Successful | Proved that every periodic board's reading is a polygon norm up to a constant; on four boards it is the board's graph distance times g·d/2 |
| Local direction — a grown plane that reads its own metric | Full pivot | The line has its verdict: the reading is the drawn board's graph distance, scaled, and the law adds no shape |
| Broader exploration — G1 with G5 | Known alternatives | The board as distinctions (B92, in another line); the one-way homothety as a theorem |
| Long-term goal — G1 Space from a law (question 9) | Obstruction learned | Under these laws the shape read is the board's; space chosen by a law needs the board to be part of the law |

**Corrections:** none. **Goals:** a G1 and G5 checkpoint (obstruction learned); the direction taken. **Assumptions:** a history line on
A51.

**Next step:** Full pivot — No next action selected. The growth line has its verdict and the coordinator parks it after this epic; the
work it points to is the board as distinctions (B92), in another line.

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | The one-way homothety as a theorem | 2/3 — Substantial | 2/3 — Testable | Prove with a combinatorial turning count that on every d-regular periodic board the route polygon is the graph polygon over g·d/2, or find a board where it is not → a theorem, or a board whose reading differs from its graph distance | Alternative · deferred |
| 2 | The board as distinctions (B92) | 3/3 — Major | 2/3 — Testable | As recorded, in its own line | Alternative · deferred |

1. **The one-way homothety.** Payoff 2: would make conclusion 2 a theorem for every regular board. Concreteness 2: the round-trip
   identity is proved; the one-way bound needs the turning count.
2. **B92.** Payoff 3, as recorded; taken by another line.

**Basket:** B127, `EXPAND-READ-20261110-001#2`, B55; none taken: the line is parked with its verdict.
