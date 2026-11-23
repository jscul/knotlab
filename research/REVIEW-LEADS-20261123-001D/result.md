# Sources that share one supply: result

Ticket `REVIEW-LEADS-20261123-001D` (B313; G15 with G5 and G17), 2026-11-23. Computed on one clock; scientific referee
pending. [Pre-registration](preregistration.md) · [full tables and commands](results_draft.md) ·
[construction addendum](../../experiments/REVIEW-LEADS-20261123-001D/REVIEW-LEADS-20261123-001D-E001_shared_supply/construction_addendum.md) ·
[deviations](../../experiments/REVIEW-LEADS-20261123-001D/REVIEW-LEADS-20261123-001D-E001_shared_supply/deviations.md)

**With two copies of the scarcity study's ring clock joined on one donor that is one loose distinction short, and
births made one at a time, the order of births decides which clock loses its tick, and a clock is exposed in
proportion to the number of donor payments its tick needs. Asking first gives no protection. A tick that needs a
one-parent birth of the donor is lost in every order.** The study could not be run on the three larger sources.

## What could be built

- **Left out.** The seven-knot, nine-knot and 21-knot sources first tick at parent steps 15, 17 and 31, long after
  their births pass the frozen bound of 400. They fail the first gate by horizon and no pair with them was grown.
- **A changed construction.** Making one donor of each of two original rings the same knot stalls the first step,
  two loose distinctions short at each of four knots, because the merged knot brings proposals across the two rings.
  The joint starts were repaired for this and are a changed definition, recorded in the addendum before any growth.
- **Staggering.** Two sources on one knot cannot first ask at different steps of the joint growth: all five joint
  starts ask the donor at joint step 1. "Staggered" therefore means that the two copies were cut from different
  stages of the clock's own history (the original ring, and the ring after five and nine parent steps).

## What happened

Counts are exact numbers of orders of the contested births, with no sampling.

| Joint start | Donor proposals m | Needed for X's tick, for Y's | Recompute after every birth, one short: X loses / Y loses / of |
| --- | ---: | --- | --- |
| Original ring twice | 4 | 2, 2 | 12 / 12 / 24 |
| Ring after five steps, twice | 6 | 2, 2 | 240 / 240 / 720 |
| Original ring with ring after five steps | 5 | 2, 2 | 48 / 48 / 120 |
| Ring after five steps with ring after nine | 7 | 2, 1 | 1,440 / 720 / 5,040 |
| Original ring with its marked knot as donor, with ring after five steps | — | a one-parent birth of the donor, — | every order ends X |

- **No shortage, no loss.** With the donor holding everything both histories take from it, neither rule loses a tick
  in any order.
- **One short.** The donor has m enabled proposals and m − 1 loose distinctions, so exactly one proposal goes unpaid:
  the last in the order. Each proposal is last in (m − 1)! of the m! orders, so a clock loses in a share of the orders
  equal to the share of the donor's proposals that its tick needs. The counts above are exactly that.
- **The one-parent birth.** The rule offers a knot's one-parent birth only while the knot holds more loose
  distinctions than it has enabled proposals with other parents. One short, it is never offered, so the clock whose
  tick needs it loses under both rules, in every order.
- **Finishing each funded step.** One short, four of the five joint starts stall as a whole: no birth, no tick.
- **Certificates.** Every loss names the donor as the required parent with no loose distinction left and the birth
  that spent its last one.

## Predictions

| # | Verdict | Evidence |
| --- | --- | --- |
| G | Passed for the ring clock only | The clock alone reproduces its recorded ticks under ordinary growth and the finish-each-step rule; the three larger sources fall outside the horizon |
| P1 | Held | No loss or stall without a shortfall |
| P2 | Failed | The copy that asks first in its own history loses while the other keeps ticking in 48 of 120 and 1,440 of 5,040 orders |
| P3 | Held under recompute-after-every-birth | Both outcomes occur in the two same-step joint starts |

The thread checked the counts against the (m − 1)! rule by hand: every row agrees.

## What this is about

About one clock joined to itself, under two supplied one-birth-at-a-time rules, with a supplied shortfall and every
order counted equally. A second reading of "contested birth", added after the first results, gave a different
labelling of which copy loses and is reported in the deviations as an artifact of slot order. No weighting of orders
follows from the model.

**Verdict.** Partially successful. The contest is real and simple: a finite donor that is one short leaves exactly one
proposal unpaid, and nothing but the order says which. That is exposure in proportion to need, on one occasion; it is
not repeated, nothing is inherited, and the larger sources were out of reach. As a route to adaptation without a
supplied learner it gives a first rule and no selection yet.
