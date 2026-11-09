# Interpretation: growth chosen by the dynamics

Run of the frozen contract `GROW-CHOOSE-20261109-001A-E001` (exploratory), 2026-11-09, launch `grow-choose-a3`; 48 runs (four tubes, four
splits, three rules), lags 0 to 12, every reading exact except the cuts marked unknown (state not repeated within 20,000 steps).

## The hypotheses

| Hypothesis | Verdict | Evidence |
| --- | --- | --- |
| H1: with the fresh split every rule grows a band at every lag to the horizon | **Refuted** except on one tube | Only the 3 × 3 tube at g = 2 under the first-cut rules grows at every lag, 13 bands to 3 × 16 or 16 × 3. Elsewhere growth stops with no allowed cut left: 3 × 4 at lag 6 (rows first) or 9 (columns first), 4 × 4 at lag 8, 3 × 3 at g = 3 at lag 3 (one or two cuts unknown at the stalling lag, none allowed after). Under the rule all the network passes 120 rings at lag 2 and is not read further. |
| H2: from lag 3 on every allowed cut runs across the direction already grown | **Holds** | No run has allowed cuts both ways at any lag from 3 on. |
| H3: with lower, upper and copy no rule grows after lag 2 | **Holds** | They grow at lags 0 and 1 (and 2 on 3 × 3 at g = 3) and then find no allowed cut to lag 12. |
| H4: under the rule all the combination of allowed cuts persists | **Holds** | 19 of 19 combinations persist. |

## What it shows

- **The dynamics picks a direction and keeps it.** At lags 0 and 1 a band is allowed both ways; once one band has been added, the
  allowed cuts from lag 3 on all run across the tube, so the network lengthens one way. Which way is set by the first band, and so, under
  a first-cut rule, by the listing order; the two orders give mirror-image runs (3 × 16 and 16 × 3).
- **Filling every allowed cut grows both ways at first.** The rule all, which needs no order, doubles both sides at lags 0 and 1 (3 × 3
  to 6 × 6 to 12 × 12 with fresh); its later course is not read here, since the network passes the run's 120-ring limit.
- **Growth stops.** With the cut contact keeping or copying its value, nothing can be added after the first lags. With both halves born
  (fresh), one band per lag can be added for 3 to 13 lags, and then no cut keeps every contact persistent.

## Nonclaims

- Four tubes and lags 0 to 12; the 3 × 3 tube at g = 2 may stop beyond the horizon.
- The rule all is read only to lag 1.
- Persistence is read as if growth stopped at each lag; the run is read lag by lag as it goes.
