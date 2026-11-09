# Interpretation: the reach of an original ring in the growing plane

Run of the frozen contract `GROW-HEAR-20261109-001A-E001` (exploratory), 2026-11-09, launch `grow-hear-a1` (8 seconds). Exact to the
lags read; the g = 3 schedules' balance is computed to 48 × 48 (`ISOLATION-NEED-20261109-001`), not proved.

## The expectations

| Expectation | Verdict | Evidence |
| --- | --- | --- |
| G1: at g = 3 the reach stops growing in the original units, a horizon | **Holds** | Just before each doubling the reach of ring (0, 0) is 1/4, 5/8, 9/16, 17/32 (P = 2) and 3/4, 5/8, 9/16, 17/32 (P = 4), converging to 1/2 from above: half an original spacing, the ring's own territory. |
| G2: the g = 3 radius is below the g = 2 radius at the same P, and no original ring hears ring (0, 0) | **Holds** | Largest reach 5/8 (P = 2) and 3/4 (P = 4) against 51/64 and 93/64 at g = 2; no original ring hears it in either. |
| G3: inside the horizon the contacts needing ring (0, 0) grow at least fourfold per doubling | **Refuted** | They grow by a constant per doubling: 4, 8, 12, 16 (P = 2) and 8, 16, 24, 32 (P = 4), against 4, 16, 88, 384 at g = 2, P = 4. |

Controls: the g = 2 runs reproduce `GROW-HORIZON-20261109-001A`'s readings exactly; in the static 3 × 3 torus every original ring hears
ring (0, 0), by lag 5 at g = 3 and lag 4 at g = 2.

## What it shows

- **Each original ring stays inside its own territory.** In the g = 3 growing plane, the rings that hear each other are the rings born
  inside one original ring's territory: an original ring's first row reaches only the contacts within half an original spacing, the
  boundary of its own territory, and the number of those grows like a boundary, by a constant per doubling, not like an area.
- **Knots kept, distance unread across the plane.** The plane keeps its knots across growth (computed) and its rings hear each other, but
  only within territories; no original ring ever hears another, so the grown plane reads no distance between its original rings while it
  grows.

## Nonclaims

- One tube, two g = 3 schedules, to 96 × 96 rings, lags read; plain dependence; declared rings (A45).
