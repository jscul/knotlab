# Interpretation: slower doubling at odd spacings

Run of the frozen contract `CROSS-BORDER-20261110-001A-E001` (exploratory), 2026-11-10, launch `cross-border-a1` (about three
minutes); eight runs, readings exact.

## The hypotheses

| Hypothesis | Verdict | Evidence |
| --- | --- | --- |
| C1: at P = 12 or 16, at both spacings, some original ring hears ring (0, 0) | **Holds** | At g = 3 the four nearest original rings hear it at lag 8 (P = 8, 12, 16) and the four at distance 2 at lag 23 (P = 12) or 27 (P = 16); at g = 5 the four nearest at lag 12 (P = 12, 16). |
| C2: every schedule in which an original ring hears ring (0, 0) has an unbalanced stage by 24 × 24 | **Holds** | g = 3, P = 8: unbalanced at 12 × 12; g = 3, P = 12 and 16 and g = 5, P = 12 and 16: balanced at 12 × 12, unbalanced at 24 × 24. |

The contract's decision rule: C2 holds, so crossing a border breaks balance at every spacing read.

## What it shows

- **Slow enough doubling crosses borders, and then balance goes.** Once original rings have heard each other, the next doubling or the
  one after leaves a stage unbalanced, at g = 3 and 5 as at g = 2.
- **Without crossing, balance can hold.** g = 5 with doubling every 6 lags keeps every stage balanced to 24 × 24 while rings hear each
  other inside their territories (reach 13/16); g = 3 every 6 lags and g = 5 every 8 lags hear without crossing and still lose balance.

## Nonclaims

- One tube, two odd spacings, P = 6 to 16; balance to 24 × 24, computed; plain dependence; declared rings (A45).
