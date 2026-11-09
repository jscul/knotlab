# Interpretation: hearing and balance under the doubling law

Run of the frozen contract `ISOLATION-NEED-20261109-001A-E001` (exploratory), 2026-11-09, launch `isolation-need-a1` (under two
minutes); 24 runs, every reading exact through a full cycle of the state.

## The hypothesis

| Hypothesis | Verdict | Evidence |
| --- | --- | --- |
| H: every run with hearing has an unbalanced stage within two doublings of its first hearing, and every run without hearing stays balanced | **Refuted** | At g = 3, open births doubling every 2 and every 4 lags hear from 12 × 12 on (144 and 288 own cells, then 576 and 1,152 at 24 × 24) and every stage is balanced to the size limit, 24 × 24. Every other run with hearing fails within two doublings (delay 0 or 1 for open births, 1 or 2 for open plus copy), and every run without hearing (g = 2, P = 1, 3 and 7; g = 3, P = 1) stays balanced to its limit. |

The frozen decision rule applies: the two g = 3 runs are counterexamples to isolation being necessary, and are read further
(`research/ISOLATION-NEED-20261109-001/read_further.py`, to 48 × 48).

## What it shows

- **Isolation is sufficient, not necessary.** At g = 3 a growing network keeps every stage balanced while its rings hear each other.
- **The spacing matters.** At g = 2 every hearing schedule fails within two doublings; the schedules that isolate at g = 2 are P = 1, 3 and
  7, one less than a power of two. At g = 3, P = 3 hears and fails at once while P = 2 and 4 hear and hold.

## Nonclaims

- One tube, two births, P to 8 at g = 2 and to 4 at g = 3, sizes to 48 × 48 and 24 × 24; the g = 3 counterexamples are read to 24 × 24
  here.
