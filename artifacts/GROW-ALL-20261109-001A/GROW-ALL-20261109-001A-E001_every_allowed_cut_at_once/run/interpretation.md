# Interpretation: growth by every allowed cut at once

Run of the frozen contract `GROW-ALL-20261109-001A-E001` (exploratory), 2026-11-09, launch `grow-all-a2` (38 minutes); a first launch
read the 3 × 3 tube at g = 2 to lag 2 with the same result and was stopped inside lag 3 (recorded in the contract).

## The hypothesis

| Hypothesis | Verdict | Evidence |
| --- | --- | --- |
| H: the order-free rule stops by lag 3 on every tube | **Refuted** | On 3 × 3, 3 × 4 and 4 × 4 at g = 2 every cut both ways is allowed at lags 0, 1 and 2 (6, 12, 24; 7, 14, 28; 8, 16, 32), exactly, and every combination read persists; the 3 × 3 tube reaches 24 × 24 after lag 2. No cut is refused anywhere. At lag 3 the 48 cuts of 24 × 24 show no failure within 50,000 steps and none repeats, so all are unknown; on 3 × 3 at g = 3 the 24 cuts of 12 × 12 at lag 2 are unknown within 400,000 steps. |

The contract's decision rule applies: some tube allows cuts both ways at lag 2 and its combination persists, so the order-free rule is a
candidate plane-growing law, read as far as the caps allow.

## What it shows

- **Every cut stays allowed, so the network doubles.** A band at every cut is a split of every ring into a 2 × 2 block; the sides go
  3, 6, 12, 24. Every stage read is balanced in the whole-history reading, while one band at a time loses persistence within a few lags
  (`GROW-RUN-20261109-001`).
- **Its contacts are renewed every lag.** Every contact is cut each lag and, with the fresh split, both halves are born; the rings keep
  their cells. "Balanced" means that whenever growth stops every contact persists from then on.
- **Where the readings stop.** The 24 × 25 networks of lag 3 and the 12 × 13 networks at g = 3 have state cycles longer than the caps;
  no refusal was seen there.

## Nonclaims

- Four tubes, lags 0 to 3; exact only to lag 2 at g = 2.
- The stages are square tori with both sides at least 6, which read distance only through freezes (`GROWN-DISTANCE-20261109-001A`,
  Theorem 3), read for the declared rings (A45).
