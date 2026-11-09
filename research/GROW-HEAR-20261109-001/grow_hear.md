# Distance in the g = 3 growing plane

Epic `GROW-HEAR-20261109-001` (program foundations), 2026-11-09. Pre-registered (its contract committed before any reading).

## The question

- **Where it comes from.** Backlog B53. `ISOLATION-NEED-20261109-001` found growing planes that keep every stage balanced while their rings
  hear each other: open doubling every 2 or 4 lags at g = 3, balanced to 48 × 48 (computed, not proved). The coordinator gave B19's
  question on them the go-ahead on 2026-11-09.
- **The question.** How far does an original ring's first row reach, in the original units, and how does its ball grow?

## Conclusions

| # | Conclusion | Kind | Ticket |
| --- | --- | --- | --- |
| 1 | **Each original ring is heard only inside its own territory.** Its reach converges to half an original spacing from above (17/32 after four doublings, both schedules), and no original ring ever hears it. | exploratory, exact to the lags read | A |
| 2 | **Its ball grows like a boundary.** The contacts needing it grow by a constant per doubling (4 at P = 2, 8 at P = 4), not fourfold as at g = 2. | exploratory, exact | A |
| 3 | **So the hearing is within territories.** The rings that hear each other at g = 3 are those born inside one original ring's territory; the plane keeps its knots (computed to 48 × 48) and reads no distance between its original rings while it grows. | reading of 1 and 2 with `ISOLATION-NEED-20261109-001` | A |

## Answer

The g = 3 growing plane keeps its knots and lets rings hear each other, but only inside the territory of each original ring: an original
ring's influence never leaves half an original spacing, and the contacts that need it form a boundary that lengthens by a constant at each
doubling. Between original rings it reads no distance while it grows, as the every-lag doubling does (`GROW-HORIZON-20261109-001`), now
with hearing inside each territory.

## Reading

**Interpretation, not a theorem.**
- **A partition, not a space.** The grown plane is a patchwork of territories, one per original ring, each refined and internally
  connected while it grows, with no influence across their borders. The knots across growth survive because nothing crosses the borders.
- **For G1 and G5.** In every growing law read so far, keeping knots across growth and reading distance across the whole grown plane have
  not been had together: the knots survive inside territories that do not hear each other.

## Lag cutoffs and census-only claims

- **Exact to the lags read** (four doublings, to 96 × 96 rings). That the reach stays below 1/2 + 2^-k is the pattern read, not proved.

## Stress test

| Claim | Check | Result |
| --- | --- | --- |
| The reach and ball (1, 2) | the controls of the frozen contract (g = 2 runs, static tori) | pass: g = 2 reproduces `GROW-HORIZON-20261109-001A`; every original ring hears ring (0, 0) without growth |

## Literature and provenance

- **Classification.** New as far as found, an exploratory reading.

## Workspace assumptions

- **Relied on.** A30, A32, A44 (open births), A45 (declared rings).
- **Added.** None.

## Ratio

Since the epic opened:
- **Substantive.** One frozen exploratory reading (A).
- **Administrative.** The pre-registration, this note and the closure.

## Pending the owner

- Nothing new.

## Next steps

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — distance in the g = 3 growing plane | **Status:** Successful | Read: each original ring is heard only inside its territory |
| Local direction — a grown plane that keeps its knots and reads distance | Research directions | Knots and cross-border hearing have not been had together |
| Broader exploration — G1 with G5 | Known alternatives | Why g = 3 keeps balance (a lemma); larger g; growth that stops; B39 |
| Long-term goal — G1 Space from a law (question 9) | Obstruction learned | Growing planes that keep their knots partition into territories that do not hear each other |

**Corrections:** none. **Goals:** a G1 and G5 checkpoint (obstruction learned), B53 marked taken. **Assumptions:** none added.

**Next step:** Research directions — selected: #1, as the coordinator asked.

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Why g = 3 keeps balance (a lemma) | 2/3 — Substantial | 2/3 — Testable | Show that at g = 3 an original ring's first row stays inside its territory, so that the transfer lemma applies territory by territory → balance proved at every doubling, or the step that fails | Selected (coordinator) |
| 2 | Larger spacings | 2/3 — Substantial | 3/3 — Ready | The census and the reach at g = 4 and 5 → whether some spacing lets influence cross territories while keeping balance | Alternative · deferred |
| 3 | Growth that stops | 2/3 — Substantial | 2/3 — Testable | Grow by doubling for k lags, then stop: the stage is balanced and the territories hear each other from then on → the distance the stopped network reads, as a function of k | Alternative · deferred |
| 4 | Invertible substrate (B39) | 2/3 — Substantial | 3/3 — Ready | As before | Alternative · deferred |

1. **Why g = 3.** Payoff 2: a theorem in place of the census, and conclusion 1 suggests the route: territories as isolation at a coarser
   scale. Concreteness 2.
2. **Larger g.** Payoff 2. Concreteness 3.
3. **Growth that stops.** Payoff 2: once growth stops the stage is balanced and every ring hears every other on odd tori, so distance is
   read after growth. Concreteness 2.
4. **Invertible substrate.** As before.

**Recommendation.** Research directions, #1 as the coordinator asked; the territory pattern of conclusion 1 is the lemma to try.
