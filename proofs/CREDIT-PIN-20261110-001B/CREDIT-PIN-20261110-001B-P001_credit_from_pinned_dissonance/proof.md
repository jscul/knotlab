# Credit from pinned dissonance

Status: Proved (computed, frozen). `check.py` (about four minutes, 21 interfaces in parallel), ticket B of
`research/CREDIT-PIN-20261110-001/preregistration.md`: targets and marks frozen in stage 1 (commit `08681795e`), the learner in stage 2
(commit `15f999a38`, erratum `8ed4bc96f`), before any run on S3, S4 or S5.

## The learner

Ticket A's fixed learner plus one rule: while an example asks for a decided output, every 10 failed probes a 20,000-step state-only
plateau walk marks the faces whose neighbourhood never clears of dissonance, and the attention lines with all three corner faces so
pinned (and no interface point) are cooled: the learner stops changing their signs (`credit_lib.py`).

## Results

S3 and S4, the same interfaces, targets and seeds as ticket A:

| | Fixed learner (ticket A) | Credit learner |
| --- | --- | --- |
| Leaves learned and held (of 32) | 31 | 29 |
| Composites learned and held (of 16) | 10 | 11 |
| Composite gate-on writes (`1uu0`, `0uu1`) learned (of 8) | 3 | 5 |
| Median steps of learned gate-on writes, leaves / composites | 103,200 / 3,309,200 | 48,600 / 1,281,800 |
| Inexact stops (of 60 writes, `0001` included) | 5 | 9 |
| `0001` stops (of 12) | 0 | 1 |

- **Cooling was always right:** 1,147 coolings cooled 4,473 lines in all, and every one lay in an atom acting at that moment (read by SAT
  afterwards); on S5 likewise.
- **S5 (one size past: six atoms, three composites, genus 6):** composites 12 of 12 learned and held, leaves 21 of 24, 5 inexact stops, two of them on `0001`.

| S5 | Learned and held | Inexact stops | Median steps of learned gate-on writes |
| --- | --- | --- | --- |
| Leaves (24 writes) | 21 | 3 | 20,300 (10 writes) |
| Composites (12 writes) | 12 | 0 | 666,400 (6 writes) |
| `0001` (9 runs) | never learned | 2 stops | |

## Against the pre-registration

- **C2 failed:** 11 of 16 composite writes on S3 and S4 (the mark was 15).
- **M held: by the frozen mark, pinned dissonance misleads.** The credit learner learned and held 40 writes against the fixed learner's
  41 and made 9 inexact stops against 5. The cooling itself was never wrong; what rose was the probe being fooled.
- **A failed:** `0001` stopped once on S3 and S4 (and twice on S5): each a probe fooled into reading an impossible map, since theorem D
  forbids it.
- **S5's C2 held:** 12 of 12.

## What it says

Pinned dissonance is an exact native signal of which inner atoms act: the learner never cooled a line outside an acting atom. Used as
credit it made composite gates faster to turn on (5 of 8 against 3 of 8, in less than half the steps) and reached every composite gate one
size past, but it did not raise the total, and the stops it made were more often wrong. The weak link is now the probe: its clamped walks
missed a reachable wrong value in 9 of 60 writes on S3 and S4 and 5 of 45 on S5, and three times it accepted the impossible `0001`.
