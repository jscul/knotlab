# The fixed learner

Status: Proved (computed, frozen; the fix is a one-rule change). `check.py` (about four and a half minutes), ticket A of
`research/CREDIT-PIN-20261110-001/preregistration.md`, frozen with the fix in commit `08681795e` before the run.

## The defect and the fix

`IN-OUT-20261110-001`'s learner probes only at its floor and widens its attention only after failed probes, so a failed write could leave
it above its floor with dissonance outside its attention, never to probe again. The fix (`fix_lib.py`): a run of 40 probe slots in a row
that pass above the floor counts as one failed probe for widening. Nothing else changes. The test is `IN-OUT-20261110-001A`'s exactly:
the census, S1 to S4, 18 interfaces, targets `1uu0`, `u10u`, `uuuu`, `0uu1`, `0001`, learner seed 3000 + k.

## Results

| | `IN-OUT-20261110-001A` (frozen learner) | Fixed learner |
| --- | --- | --- |
| Leaves learned and held (of 56) | 53 | 55 |
| Composites learned and held (of 16) | 1 | 10 |
| Inexact stops | 6 | 5 (1 at a leaf, 4 at composites) |
| `0001` stops (of 18) | 0 | 0 |
| Median steps to turn a gate on, leaves / composites | 62,600 / 2,024,900 | 95,600 / 1,473,500 |

- The census is unchanged (theorem D and lemma G on every class).
- 46 writes had at least one stall (a run of 40 probe slots above the floor), 18 of them on `0001`, which can never be met.
- At composites: `uuuu` 4 of 4; `u10u` 3 of 4; `1uu0` 2 of 4; `0uu1` 1 of 4. The rest: two never reached a gate (one composite of S3, both
  gate-on targets), and four inexact stops at S4's composites, where a reachable wrong value went unreached by the probe's walk.
- Marks as frozen: L held (98%), C failed (62.5%), A held, R failed (5 inexact stops), K held (15 times).

## What it says

Most of `IN-OUT-20261110-001`'s composite failure was the stall, not depth: with it fixed the blind learner forms composite gates in 6 of
12 gate writes. Depth still costs (15 times the steps) and fools the probe more often. The earlier reading is corrected in
`docs/CORRECTIONS.md` (Narrowing).

**Reproduction.** Re-running `check.py` reproduces every check except check 0: the pre-registration it binds gained stage 2 and its
erratum after this ticket ran, so its hash moved. The result is bound to the stage-1 text (commit `08681795e`).
