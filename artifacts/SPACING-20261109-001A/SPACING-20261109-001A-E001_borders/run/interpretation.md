# Interpretation: balance and borders at spacings 4 and 5

Run of the frozen contract `SPACING-20261109-001A-E001` (exploratory), 2026-11-09, launch `spacing-a1` (five minutes); eight runs, every
reading exact (balance through a full cycle of the state; reach to the lags read).

## The hypotheses

| Hypothesis | Verdict | Evidence |
| --- | --- | --- |
| S1: at g = 4 or 5 some schedule with hearing keeps every stage balanced to 24 × 24 | **Holds** | At g = 5 doubling every 2, 3 and 4 lags keeps every stage balanced to 24 × 24 while 720 to 1,728 own cells hear another ring. At g = 4 every hearing schedule (P = 2, 3, 4) is unbalanced at 12 × 12. |
| S2: in every balanced schedule no original ring hears ring (0, 0) and its reach stays below one original spacing | **Holds** | Largest reach 1/4 (P = 1 at both spacings) and 9/16, 5/8, 25/32 (g = 5, P = 2, 3, 4); no original ring hears ring (0, 0). |
| S3: every schedule in which an original ring hears ring (0, 0) has an unbalanced stage | **Holds vacuously** | No original ring hears ring (0, 0) in any of the eight schedules, to 96 × 96. |

## What it shows

- **Territories at every spacing read.** From g = 2 to 5, with doubling every P ≤ 4 lags, no original ring is heard by another while
  the network grows; only slower doubling (P = 6, 8 at g = 2, `GROW-HORIZON-20261109-001`) let influence cross a border, and those
  schedules were unbalanced (`DOUBLE-BALANCE-20261109-001`).
- **Odd spacings keep balance with hearing.** Balance with hearing appears at g = 3 (P = 2, 4) and g = 5 (P = 2, 3, 4), corners of an
  even number of own cells, and never at g = 2 or 4, corners of an odd number.

## Nonclaims

- One tube, P to 4, 24 × 24 for balance and 96 × 96 for reach; balance computed, not proved; plain dependence; declared rings (A45).
